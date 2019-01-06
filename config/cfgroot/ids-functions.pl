#!/usr/bin/perl -w
############################################################################
#                                                                          #
# This file is part of the IPFire Firewall.                                #
#                                                                          #
# IPFire is free software; you can redistribute it and/or modify           #
# it under the terms of the GNU General Public License as published by     #
# the Free Software Foundation; either version 2 of the License, or        #
# (at your option) any later version.                                      #
#                                                                          #
# IPFire is distributed in the hope that it will be useful,                #
# but WITHOUT ANY WARRANTY; without even the implied warranty of           #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
# GNU General Public License for more details.                             #
#                                                                          #
# You should have received a copy of the GNU General Public License        #
# along with IPFire; if not, write to the Free Software                    #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA #
#                                                                          #
# Copyright (C) 2018 IPFire Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################

package IDS;

require '/var/ipfire/general-functions.pl';

# Location where all config and settings files are stored.
our $settingsdir = "${General::swroot}/suricata";

# File where the used rulefiles are stored.
our $used_rulefiles_file = "$settingsdir/suricata-used-rulefiles.yaml";

# File where the addresses of the homenet are stored.
our $homenet_file = "$settingsdir/suricata-homenet.yaml";

# File which contains the enabled sids.
our $enabled_sids_file = "$settingsdir/oinkmaster-enabled-sids.conf";

# File which contains the disabled sids.
our $disabled_sids_file = "$settingsdir/oinkmaster-disabled-sids.conf";

# File which contains wheater the rules should be changed.
our $modify_sids_file = "$settingsdir/oinkmaster-modify-sids.conf";

# File which stores the configured IPS settings.
our $ids_settings_file = "$settingsdir/settings";

# File which stores the configured rules-settings.
our $rules_settings_file = "$settingsdir/rules-settings";

# File which stores the configured settings for whitelisted addresses.
our $ignored_file = "$settingsdir/ignored";

# Location and name of the tarball which contains the ruleset.
our $rulestarball = "/var/tmp/idsrules.tar.gz";

# File to store any errors, which also will be read and displayed by the wui.
our $storederrorfile = "/tmp/ids_storederror";

# Location where the rulefiles are stored.
our $rulespath = "/var/lib/suricata";

# File which contains the rules to whitelist addresses on suricata.
our $whitelist_file = "$rulespath/whitelist.rules";

# File which contains a list of all supported ruleset sources.
# (Sourcefire, Emergingthreads, etc..)
our $rulesetsourcesfile = "$settingsdir/ruleset-sources";

# The pidfile of the IDS.
our $idspidfile = "/var/run/suricata.pid";

# Location of suricatactrl.
my $suricatactrl = "/usr/local/bin/suricatactrl";

# Array with allowed commands of suricatactrl.
my @suricatactrl_cmds = ( 'start', 'stop', 'restart', 'reload', 'fix-rules-dir', 'cron' );

# Array with supported cron intervals.
my @cron_intervals = ('off', 'daily', 'weekly' );

#
## Function to check and create all IDS related files, if the does not exist.
#
sub check_and_create_filelayout() {
	# Check if the files exist and if not, create them.
	unless (-f "$enabled_sids_file") { &create_empty_file($enabled_sids_file); }
	unless (-f "$disabled_sids_file") { &create_empty_file($disabled_sids_file); }
	unless (-f "$modify_sids_file") { &create_empty_file($modify_sids_file); }
	unless (-f "$used_rulefiles_file") { &create_empty_file($used_rulefiles_file); }
	unless (-f "$ids_settings_file") { &create_empty_file($ids_settings_file); }
	unless (-f "$rules_settings_file") { &create_empty_file($rules_settings_file); }
	unless (-f "$ignored_file") { &create_empty_file($ignored_file); }
	unless (-f "$whitelist_file" ) { &create_empty_file($whitelist_file); }
}

#
## Function for checking if at least 300MB of free disk space are available
## on the "/var" partition.
#
sub checkdiskspace () {
	# Call diskfree to gather the free disk space of /var.
	my @df = `/bin/df -B M /var`;

	# Loop through the output.
	foreach my $line (@df) {
		# Ignore header line.
		next if $line =~ m/^Filesystem/;

		# Search for a line with the device information.
		if ($line =~ m/dev/ ) {
			# Split the line into single pieces.
			my @values = split(' ', $line);
			my ($filesystem, $blocks, $used, $available, $used_perenctage, $mounted_on) = @values;

			# Check if the available disk space is more than 300MB.
			if ($available < 300) {
				# Log error to syslog.
				&_log_to_syslog("Not enough free disk space on /var. Only $available MB from 300 MB available.");

				# Exit function and return "1" - False.
				return 1;
			}
		}
	}

	# Everything okay, return nothing.
	return;
}

#
## This function is responsible for downloading the configured IDS ruleset.
##
## * At first it obtains from the stored rules settings which ruleset should be downloaded.
## * The next step is to get the download locations for all available rulesets.
## * After that, the function will check if an upstream proxy should be used and grab the settings.
## * The last step will be to generate the final download url, by obtaining the URL for the desired
##   ruleset, add the settings for the upstream proxy and final grab the rules tarball from the server.
#
sub downloadruleset {
	# Get rules settings.
	my %rulessettings=();
	&General::readhash("$rules_settings_file", \%rulessettings);

	# Check if a ruleset has been configured.
	unless($rulessettings{'RULES'}) {
		# Log that no ruleset has been configured and abort.
		&_log_to_syslog("No ruleset source has been configured.");

		# Return "1".
		return 1;
	}

	# Get all available ruleset locations.
	my %rulesetsources=();
	&General::readhash($rulesetsourcesfile, \%rulesetsources);

	# Read proxysettings.
	my %proxysettings=();
	&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);

	# Load required perl module to handle the download.
	use LWP::UserAgent;

	# Init the download module.
	my $downloader = LWP::UserAgent->new;

	# Set timeout to 10 seconds.
	$downloader->timeout(10);

	# Check if an upstream proxy is configured.
	if ($proxysettings{'UPSTREAM_PROXY'}) {
		my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
		my $proxy_url;

		# Check if we got a peer.
		if ($peer) {
			$proxy_url = "http://";

			# Check if the proxy requires authentication.
			if (($proxysettings{'UPSTREAM_USER'}) && ($proxysettings{'UPSTREAM_PASSWORD'})) {
				$proxy_url .= "$proxysettings{'UPSTREAM_USER'}\:$proxysettings{'UPSTREAM_PASSWORD'}\@";
			}

			# Add proxy server address and port.
			$proxy_url .= "$peer\:$peerport";
		} else {
			# Log error message and break.
			&_log_to_syslog("Could not proper configure the proxy server access.");

			# Return "1" - false.
			return 1;
		}

		# Setup proxy settings.
		$downloader->proxy(['http', 'https'], $proxy_url);
	}

	# Grab the right url based on the configured vendor.
	my $url = $rulesetsources{$rulessettings{'RULES'}};

	# Check if the vendor requires an oinkcode and add it if needed.
	$url =~ s/\<oinkcode\>/$rulessettings{'OINKCODE'}/g;

	# Abort if no url could be determined for the vendor.
	unless ($url) {
		# Log error and abort.
		&_log_to_syslog("Unable to gather a download URL for the selected ruleset.");
		return 1;
	}

	# Pass the requrested url to the downloader.
	my $request = HTTP::Request->new(HEAD => $url);

	# Accept the html header.
	$request->header('Accept' => 'text/html');

	# Perform the request and fetch the html header.
	my $response = $downloader->request($request);

	# Check if there was any error.
	unless ($response->is_success) {
		# Obtain error.
		my $error = $response->content;

		# Log error message.
		&_log_to_syslog("Unable to download the ruleset. \($error\)");

		# Return "1" - false.
		return 1;
	}

	# Assign the fetched header object.
	my $header = $response->headers;

	# Grab the remote file size from the object and store it in the
	# variable.
	my $remote_filesize = $header->content_length;

	# Load perl module to deal with temporary files.
	use File::Temp;

	# Generate temporay file name, located in "/var/tmp" and with a suffix of ".tar.gz".
	my $tmp = File::Temp->new( SUFFIX => ".tar.gz", DIR => "/var/tmp/", UNLINK => 0 );
	my $tmpfile = $tmp->filename();

	# Pass the requested url to the downloader.
	my $request = HTTP::Request->new(GET => $url);

	# Perform the request and save the output into the tmpfile.
	my $response = $downloader->request($request, $tmpfile);

	# Check if there was any error.
	unless ($response->is_success) {
		# Obtain error.
		my $error = $response->content;

		# Log error message.
		&_log_to_syslog("Unable to download the ruleset. \($error\)");

		# Return "1" - false.
		return 1;
	}

	# Load perl stat module.
	use File::stat;

	# Perform stat on the tmpfile.
	my $stat = stat($tmpfile);

	# Grab the local filesize of the downloaded tarball.
	my $local_filesize = $stat->size;

	# Check if both file sizes match.
	unless ($remote_filesize eq $local_filesize) {
		# Log error message.
		&_log_to_syslog("Unable to completely download the ruleset. ");
		&_log_to_syslog("Only got $local_filesize Bytes instead of $remote_filesize Bytes. ");

		# Delete temporary file.
		unlink("$tmpfile");

		# Return "1" - false.
		return 1;
	}

	# Load file copy module, which contains the move() function.
	use File::Copy;

	# Overwrite existing rules tarball with the new downloaded one.
	move("$tmpfile", "$rulestarball");

	# If we got here, everything worked fine. Return nothing.
	return;
}

#
## A tiny wrapper function to call the oinkmaster script.
#
sub oinkmaster () {
	# Check if the files in rulesdir have the correct permissions.
	&_check_rulesdir_permissions();

	# Cleanup the rules directory before filling it with the new rulest.
	&_cleanup_rulesdir();

	# Load perl module to talk to the kernel syslog.
	use Sys::Syslog qw(:DEFAULT setlogsock);

	# Establish the connection to the syslog service.
	openlog('oinkmaster', 'cons,pid', 'user');

	# Call oinkmaster to generate ruleset.
	open(OINKMASTER, "/usr/local/bin/oinkmaster.pl -v -s -u file://$rulestarball -C $settingsdir/oinkmaster.conf -o $rulespath|") or die "Could not execute oinkmaster $!\n";

	# Log output of oinkmaster to syslog.
	while(<OINKMASTER>) {
		# The syslog function works best with an array based input,
		# so generate one before passing the message details to syslog.
		my @syslog = ("INFO", "$_");

		# Send the log message.
		syslog(@syslog);
	}

	# Close the pipe to oinkmaster process.
	close(OINKMASTER);

	# Close the log handle.
	closelog();
}

#
## Function to do all the logging stuff if the downloading or updating of the ruleset fails.
#
sub log_error ($) {
	my ($error) = @_;

	# Remove any newline.
	chomp($error);

	# Call private function to log the error message to syslog.
	&_log_to_syslog($error);

	# Call private function to write/store the error message in the storederrorfile.
	&_store_error_message($error);
}

#
## Function to log a given error message to the kernel syslog.
#
sub _log_to_syslog ($) {
	my ($message) = @_;

	# Load perl module to talk to the kernel syslog.
	use Sys::Syslog qw(:DEFAULT setlogsock);

	# The syslog function works best with an array based input,
	# so generate one before passing the message details to syslog.
	my @syslog = ("ERR", "<ERROR> $message");

	# Establish the connection to the syslog service.
	openlog('oinkmaster', 'cons,pid', 'user');

	# Send the log message.
	syslog(@syslog);

	# Close the log handle.
	closelog();
}

#
## Private function to write a given error message to the storederror file.
#
sub _store_error_message ($) {
        my ($message) = @_;

	# Remove any newline.
	chomp($message);

        # Open file for writing.
        open (ERRORFILE, ">$storederrorfile") or die "Could not write to $storederrorfile. $!\n";

        # Write error to file.
        print ERRORFILE "$message\n";

        # Close file.
        close (ERRORFILE);
}

#
## Function to get a list of all available network zones.
#
sub get_available_network_zones () {
	# Get netsettings.
	my %netsettings = ();
	&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

	# Obtain the configuration type from the netsettings hash.
	my $config_type = $netsettings{'CONFIG_TYPE'};

	# Hash which contains the conversation from the config mode
	# to the existing network interface names. They are stored like
	# an array.
	#
	# Mode "0" red is a modem and green
	# Mode "1" red is a netdev and green
	# Mode "2" red, green and orange
	# Mode "3" red, green and blue
	# Mode "4" red, green, blue, orange
	my %config_type_to_interfaces = (
		"0" => [ "red", "green" ],
		"1" => [ "red", "green" ],
		"2" => [ "red", "green", "orange" ],
		"3" => [ "red", "green", "blue" ],
		"4" => [ "red", "green", "blue", "orange" ]
	);

	# Obtain and dereference the corresponding network interaces based on the read
	# network config type.
	my @network_zones = @{ $config_type_to_interfaces{$config_type} };

	# Return them.
	return @network_zones;
}

#
## Function to check if the IDS is running.
#
sub ids_is_running () {
	if(-f $idspidfile) {
		# Open PID file for reading.
		open(PIDFILE, "$idspidfile") or die "Could not open $idspidfile. $!\n";

		# Grab the process-id.
		my $pid = <PIDFILE>;

		# Close filehandle.
		close(PIDFILE);

		# Remove any newline.
		chomp($pid);

		# Check if a directory for the process-id exists in proc.
		if(-d "/proc/$pid") {
			# The IDS daemon is running return the process id.
			return $pid;
		}
	}

	# Return nothing - IDS is not running.
	return;
}

#
## Function to call suricatactrl binary with a given command.
#
sub call_suricatactrl ($) {
	# Get called option.
	my ($option, $interval) = @_;

	# Loop through the array of supported commands and check if
	# the given one is part of it.
	foreach my $cmd (@suricatactrl_cmds) {
		# Skip current command unless the given one has been found.
		next unless($cmd eq $option);

		# Check if the given command is "cron".
		if ($option eq "cron") {
			# Check if an interval has been given.
			if ($interval) {
				# Check if the given interval is valid.
				foreach my $element (@cron_intervals) {
					# Skip current element until the given one has been found.
					next unless($element eq $interval);

					# Call the suricatactrl binary and pass the "cron" command
					# with the requrested interval.
					system("$suricatactrl $option $interval &>/dev/null");

					# Return "1" - True.
					return 1;
				}
			}

			# If we got here, the given interval is not supported or none has been given. - Return nothing.
			return;
		} else {
			# Call the suricatactrl binary and pass the requrested
			# option to it.
			system("$suricatactrl $option &>/dev/null");

			# Return "1" - True.
			return 1;
		}
	}

	# Command not found - return nothing.
	return;
}

#
## Function to create a new empty file.
#
sub create_empty_file($) {
	my ($file) = @_;

	# Check if the given file exists.
	if(-e $file) {
		# Do nothing to prevent from overwriting existing files.
		return;
	}

	# Open the file for writing.
	open(FILE, ">$file") or die "Could not write to $file. $!\n";

	# Close file handle.
	close(FILE);

	# Return true.
	return 1;
}

#
## Private function to check if the file permission of the rulespath are correct.
## If not, call suricatactrl to fix them.
#
sub _check_rulesdir_permissions() {
	# Check if the rulepath main directory is writable.
	unless (-W $rulespath) {
		# If not call suricatctrl to fix it.
		&call_suricatactrl("fix-rules-dir");
	}

	# Open snort rules directory and do a directory listing.
	opendir(DIR, $rulespath) or die $!;
	# Loop through the direcory.
	while (my $file = readdir(DIR)) {
		# We only want files.
		next unless (-f "$rulespath/$file");

		# Check if the file is writable by the user.
		if (-W "$rulespath/$file") {
			# Everything is okay - go on to the next file.
			next;
		} else {
			# There are wrong permissions, call suricatactrl to fix it.
			&call_suricatactrl("fix-rules-dir");
		}
	}
}

#
## Private function to cleanup the directory which contains
## the IDS rules, before extracting and modifing the new ruleset.
#
sub _cleanup_rulesdir() {
	# Open rules directory and do a directory listing.
	opendir(DIR, $rulespath) or die $!;

	# Loop through the direcory.
	while (my $file = readdir(DIR)) {
		# We only want files.
		next unless (-f "$rulespath/$file");

		# Skip element if it has config as file extension.
		next if ($file =~ m/\.config$/);

		# Delete the current processed file, if not, exit this function
		# and return an error message.
		unlink("$rulespath/$file") or return "Could not delete $rulespath/$file. $!\n";
	}

	# Return nothing;
	return;
}

#
## Function to generate the file which contains the home net information.
#
sub generate_home_net_file() {
	my %netsettings;

	# Read-in network settings.
	&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

	# Get available network zones.
	my @network_zones = &get_available_network_zones();

	# Temporary array to store network address and prefix of the configured
	# networks.
	my @networks;

	# Loop through the array of available network zones.
	foreach my $zone (@network_zones) {
		# Skip the red network - It never can be part to the home_net!
		next if($zone eq "red");

		# Convert current zone name into upper case.
		$zone = uc($zone);

		# Generate key to access the required data from the netsettings hash.
		my $zone_netaddress = $zone . "_NETADDRESS";
		my $zone_netmask = $zone . "_NETMASK";

		# Obtain the settings from the netsettings hash.
		my $netaddress = $netsettings{$zone_netaddress};
		my $netmask = $netsettings{$zone_netmask};

		# Convert the subnetmask into prefix notation.
		my $prefix = &Network::convert_netmask2prefix($netmask);

		# Generate full network string.
		my $network = join("/", $netaddress,$prefix);

		# Check if the network is valid.
		if(&Network::check_subnet($network)) {
			# Add the generated network to the array of networks.
			push(@networks, $network);
		}
	}

	# Format home net declaration.
	my $line = "\"\[";

	# Loop through the array of networks.
	foreach my $network (@networks) {
		# Add the network to the line.
		$line = "$line" . "$network";

		# Check if the current network was the last in the array.
		if ($network eq $networks[-1]) {
			# Close the line.
			$line = "$line" . "\]\"";
		} else {
			# Add "," for the next network.
			$line = "$line" . "\,";
		}
	}

	# Open file to store the addresses of the home net.
	open(FILE, ">$homenet_file") or die "Could not open $homenet_file. $!\n";

	# Print yaml header.
	print FILE "%YAML 1.1\n";
	print FILE "---\n\n";

	# Print notice about autogenerated file.
	print FILE "#Autogenerated file. Any custom changes will be overwritten!\n";

	# Print the generated and required HOME_NET declaration to the file.
	print FILE "HOME_NET:\t$line\n";

	# Close file handle.
	close(FILE);
}

#
## Function to generate and write the file for used rulefiles.
#
sub write_used_rulefiles_file(@) {
	my @files = @_;

	# Open file for used rulefiles.
	open (FILE, ">$used_rulefiles_file") or die "Could not write to $used_rulefiles_file. $!\n";

	# Write yaml header to the file.
	print FILE "%YAML 1.1\n";
	print FILE "---\n\n";

	# Write header to file.
	print FILE "#Autogenerated file. Any custom changes will be overwritten!\n";

	# Allways use the whitelist.
	print FILE " - whitelist.rules\n";

	# Loop through the array of given files.
	foreach my $file (@files) {
		# Check if the given filename exists and write it to the file of used rulefiles.
		if(-f "$rulespath/$file") {
			print FILE " - $file\n";
		}
	}

	# Close file after writing.
	close(FILE);
}

#
## Function to generate and write the file for modify the ruleset.
#
sub write_modify_sids_file($) {
	my ($ruleaction) = @_;

	# Open modify sid's file for writing.
	open(FILE, ">$modify_sids_file") or die "Could not write to $modify_sids_file. $!\n";

	# Write file header.
	print FILE "#Autogenerated file. Any custom changes will be overwritten!\n";

	# Check if the traffic only should be monitored.
	unless($ruleaction eq "alert") {
		# Tell oinkmaster to switch all rules from alert to drop.
		print FILE "modifysid \* \"alert\" \| \"drop\"\n";
	}

	# Close file handle.
	close(FILE);
}

#
## Function to gather the version of suricata.
#
sub get_suricata_version($) {
	my ($format) = @_;

	# Execute piped suricata command and return the version information.
	open(SURICATA, "suricata -V |") or die "Couldn't execute program: $!";

	# Grab and store the output of the piped program.
	my $version_string = <SURICATA>;

	# Close pipe.
        close(SURICATA);

	# Remove newlines.
        chomp($version_string);

	# Grab the version from the version string. 
	$version_string =~ /([0-9]+([.][0-9]+)+)/;

	# Splitt the version into single chunks.
	my ($major_ver, $minor_ver, $patchlevel) = split(/\./, $1);

	# Check and return the requested version sheme.
	if ($format eq "major") {
		# Return the full version.
		return "$major_ver";
	} elsif ($format eq "minor") {
		# Return the major and minor part.
		return "$major_ver.$minor_ver";
	} else {
		# Return the full version string.
		return "$major_ver.$minor_ver.$patchlevel";
	} 
}

1;
