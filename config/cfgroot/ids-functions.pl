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
# Copyright (C) 2018-2019 IPFire Team <info@ipfire.org>                    #
#                                                                          #
############################################################################

use strict;

package IDS;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/network-functions.pl";
require "${General::swroot}/suricata/ruleset-sources";

# Location where all config and settings files are stored.
our $settingsdir = "${General::swroot}/suricata";

# File where the main file for providers ruleset inclusion exists.
our $suricata_used_providers_file = "$settingsdir/suricata-used-providers.yaml";

# File for static ruleset inclusions.
our $suricata_default_rulefiles_file = "$settingsdir/suricata-default-rules.yaml";

# File where the addresses of the homenet are stored.
our $homenet_file = "$settingsdir/suricata-homenet.yaml";

# File where the addresses of the used DNS servers are stored.
our $dns_servers_file = "$settingsdir/suricata-dns-servers.yaml";

# File where the HTTP ports definition is stored.
our $http_ports_file = "$settingsdir/suricata-http-ports.yaml";

# File which contains includes for provider specific rule modifications.
our $oinkmaster_provider_includes_file = "$settingsdir/oinkmaster-provider-includes.conf";

# File which contains wheater the rules should be changed.
our $modify_sids_file = "$settingsdir/oinkmaster-modify-sids.conf";

# File which stores the configured IPS settings.
our $ids_settings_file = "$settingsdir/settings";

# File which stores the used and configured ruleset providers.
our $providers_settings_file = "$settingsdir/providers-settings";

# File which stores the configured settings for whitelisted addresses.
our $ignored_file = "$settingsdir/ignored";

# Location where the downloaded rulesets are stored.
our $dl_rules_path = "/var/tmp";

# File to store any errors, which also will be read and displayed by the wui.
our $storederrorfile = "/tmp/ids_storederror";

# File to lock the WUI, while the autoupdate script runs.
our $ids_page_lock_file = "/tmp/ids_page_locked";

# Location where the rulefiles are stored.
our $rulespath = "/var/lib/suricata";

# Location where the default rulefils are stored.
our $default_rulespath = "/usr/share/suricata/rules";

# Location where the addition config files are stored.
our $configspath = "/usr/share/suricata";

# Location of the classification file.
our $classification_file = "$configspath/classification.config";

# Location of the sid to msg mappings file.
our $sid_msg_file = "$rulespath/sid-msg.map";

# Location to store local rules. This file will not be touched.
our $local_rules_file = "$rulespath/local.rules";

# File which contains the rules to whitelist addresses on suricata.
our $whitelist_file = "$rulespath/whitelist.rules";

# File which contains a list of all supported ruleset sources.
# (Sourcefire, Emergingthreads, etc..)
our $rulesetsourcesfile = "$settingsdir/ruleset-sources";

# The pidfile of the IDS.
our $idspidfile = "/var/run/suricata.pid";

# Location of suricatactrl.
my $suricatactrl = "/usr/local/bin/suricatactrl";

# Prefix for each downloaded ruleset.
my $dl_rulesfile_prefix = "idsrules";

# Temporary directory where the rulesets will be extracted.
my $tmp_directory = "/tmp/ids_tmp";

# Temporary directory where the extracted rules files will be stored.
my $tmp_rules_directory = "$tmp_directory/rules";

# Temporary directory where the extracted additional config files will be stored.
my $tmp_conf_directory = "$tmp_directory/conf";

# Array with allowed commands of suricatactrl.
my @suricatactrl_cmds = ( 'start', 'stop', 'restart', 'reload', 'fix-rules-dir', 'cron' );

# Array with supported cron intervals.
my @cron_intervals = ('off', 'daily', 'weekly' );

# Array which contains the HTTP ports, which statically will be declared as HTTP_PORTS in the
# http_ports_file.
my @http_ports = ('80', '81');

# Array which contains a list of rulefiles which always will be included if they exist.
my @static_included_rulefiles = ('local.rules', 'whitelist.rules');

# Array which contains a list of allways enabled application layer protocols.
my @static_enabled_app_layer_protos = ('app-layer', 'decoder', 'files', 'stream');

# Hash which allows to convert the download type (dl_type) to a file suffix.
my %dl_type_to_suffix = (
	"archive" => ".tar.gz",
	"plain" => ".rules",
);

# Hash to translate an application layer protocol to the application name.
my %tr_app_layer_proto = (
	"ikev2" => "ipsec",
	"krb5" => "kerberos",
);

#
## Function to check and create all IDS related files, if the does not exist.
#
sub check_and_create_filelayout() {
	# Check if the files exist and if not, create them.
	unless (-f "$oinkmaster_provider_includes_file") { &create_empty_file($oinkmaster_provider_includes_file); }
	unless (-f "$modify_sids_file") { &create_empty_file($modify_sids_file); }
	unless (-f "$suricata_used_providers_file") { &create_empty_file($suricata_used_providers_file); }
	unless (-f "$suricata_default_rulefiles_file") { &create_empty_file($suricata_default_rulefiles_file); }
	unless (-f "$ids_settings_file") { &create_empty_file($ids_settings_file); }
	unless (-f "$providers_settings_file") { &create_empty_file($providers_settings_file); }
	unless (-f "$whitelist_file" ) { &create_empty_file($whitelist_file); }
}

#
## Function to get a list of all available ruleset providers.
##
## They will be returned as a sorted array.
#
sub get_ruleset_providers() {
	my @providers;

	# Loop through the hash of providers.
	foreach my $provider ( keys %IDS::Ruleset::Providers ) {
		# Add the provider to the array.
		push(@providers, $provider);
	}

	# Sort and return the array.
	return sort(@providers);
}

#
## Function to get a list of all enabled ruleset providers.
##
## They will be returned as an array.
#
sub get_enabled_providers () {
	my %used_providers = ();

	# Array to store the enabled providers.
	my @enabled_providers = ();

	# Read-in the providers config file.
	&General::readhasharray("$providers_settings_file", \%used_providers);

	# Loop through the hash of used_providers.
	foreach my $id (keys %used_providers) {
		# Skip disabled providers.
		next unless ($used_providers{$id}[3] eq "enabled");

		# Grab the provider handle.
		my $provider = "$used_providers{$id}[0]";

		# Add the provider to the array of enabled providers.
		push(@enabled_providers, $provider);
	}

	# Return the array.
	return @enabled_providers;
}

#
## Function for checking if at least 300MB of free disk space are available
## on the "/var" partition.
#
sub checkdiskspace () {
	# Call diskfree to gather the free disk space of /var.
	my @df = &General::system_output("/bin/df", "-B", "M", "/var");

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
## This function is responsible for downloading the configured IDS rulesets or if no one is specified
## all configured rulesets will be downloaded.
##
## * At first it gathers all configured ruleset providers, initialize the downloader and sets an
##   upstream proxy if configured.
## * After that, the given ruleset or in case all rulesets should be downloaded, it will determine wether it
##   is enabled or not.
## * The next step will be to generate the final download url, by obtaining the URL for the desired
##   ruleset, add the settings for the upstream proxy.
## * Finally the function will grab all the rules files or tarballs from the servers.
#
sub downloadruleset ($) {
	my ($provider) = @_;

	# If no provider is given default to "all".
	$provider //= 'all';

	# Hash to store the providers and access id's, for which rules should be downloaded.
	my %sheduled_providers = ();

	# Get used provider settings.
	my %used_providers = ();
	&General::readhasharray("$providers_settings_file", \%used_providers);

	# Check if a ruleset has been configured.
	unless(%used_providers) {
		# Log that no ruleset has been configured and abort.
		&_log_to_syslog("No ruleset provider has been configured.");

		# Return "1".
		return 1;
	}

	# Read proxysettings.
	my %proxysettings=();
	&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);

	# Load required perl module to handle the download.
	use LWP::UserAgent;

	# Init the download module.
	#
	# Request SSL hostname verification and specify path
	# to the CA file.
	my $downloader = LWP::UserAgent->new(
		ssl_opts => {
			SSL_ca_file     => '/etc/ssl/cert.pem',
			verify_hostname => 1,
		}
	);

	# Set timeout to 10 seconds.
	$downloader->timeout(10);

	# Check if an upstream proxy is configured.
	if ($proxysettings{'UPSTREAM_PROXY'}) {
		my $proxy_url;

		$proxy_url = "http://";

		# Check if the proxy requires authentication.
		if (($proxysettings{'UPSTREAM_USER'}) && ($proxysettings{'UPSTREAM_PASSWORD'})) {
			$proxy_url .= "$proxysettings{'UPSTREAM_USER'}\:$proxysettings{'UPSTREAM_PASSWORD'}\@";
		}

		# Add proxy server address and port.
		$proxy_url .= $proxysettings{'UPSTREAM_PROXY'};

		# Setup proxy settings.
		$downloader->proxy(['http', 'https'], $proxy_url);
	}

	# Loop through the hash of configured providers.
	foreach my $id ( keys %used_providers ) {
		# Skip providers which are not enabled.
		next if ($used_providers{$id}[3] ne "enabled");

		# Obtain the provider handle.
		my $provider_handle = $used_providers{$id}[0];

		# Handle update off all providers.
		if (($provider eq "all") || ($provider_handle eq "$provider")) {
			# Add provider handle and it's id to the hash of sheduled providers.
			$sheduled_providers{$provider_handle} = $id;
		}
	}

	# Loop through the hash of sheduled providers.
	foreach my $provider ( keys %sheduled_providers) {
		# Log download/update of the ruleset.
		&_log_to_syslog("Downloading ruleset for provider: $provider.");

		# Grab the download url for the provider.
		my $url = $IDS::Ruleset::Providers{$provider}{'dl_url'};

		# Check if the provider requires a subscription.
		if ($IDS::Ruleset::Providers{$provider}{'requires_subscription'} eq "True") {
			# Grab the previously stored access id for the provider from hash.
			my $id = $sheduled_providers{$provider};

			# Grab the subscription code.
			my $subscription_code = $used_providers{$id}[1];

			# Add the subscription code to the download url.
			$url =~ s/\<subscription_code\>/$subscription_code/g;

		}

		# Abort if no url could be determined for the provider.
		unless ($url) {
			# Log error and abort.
			&_log_to_syslog("Unable to gather a download URL for the selected ruleset provider.");
			return 1;
		}

		# Variable to store the filesize of the remote object.
		my $remote_filesize;

		# The sourcfire (snort rules) does not allow to send "HEAD" requests, so skip this check
		# for this webserver.
		#
		# Check if the ruleset source contains "snort.org".
		unless ($url =~ /\.snort\.org/) {
			# Pass the requrested url to the downloader.
			my $request = HTTP::Request->new(HEAD => $url);

			# Accept the html header.
			$request->header('Accept' => 'text/html');

			# Perform the request and fetch the html header.
			my $response = $downloader->request($request);

			# Check if there was any error.
			unless ($response->is_success) {
				# Obtain error.
				my $error = $response->status_line();

				# Log error message.
				&_log_to_syslog("Unable to download the ruleset. \($error\)");

				# Return "1" - false.
				return 1;
			}

			# Assign the fetched header object.
			my $header = $response->headers();

			# Grab the remote file size from the object and store it in the
			# variable.
			$remote_filesize = $header->content_length;
		}

		# Load perl module to deal with temporary files.
		use File::Temp;

		# Generate temporary file name, located in "/var/tmp" and with a suffix of ".tmp".
		my $tmp = File::Temp->new( SUFFIX => ".tmp", DIR => "/var/tmp/", UNLINK => 0 );
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
		if (($remote_filesize) && ($remote_filesize ne $local_filesize)) {
			# Log error message.
			&_log_to_syslog("Unable to completely download the ruleset. ");
			&_log_to_syslog("Only got $local_filesize Bytes instead of $remote_filesize Bytes. ");

			# Delete temporary file.
			unlink("$tmpfile");

			# Return "1" - false.
			return 1;
		}

		# Genarate and assign file name and path to store the downloaded rules file.
		my $dl_rulesfile = &_get_dl_rulesfile($provider);

		# Check if a file name could be obtained.
		unless ($dl_rulesfile) {
			# Log error message.
			&_log_to_syslog("Unable to store the downloaded rules file. ");

			# Delete downloaded temporary file.
			unlink("$tmpfile");

			# Return "1" - false.
			return 1;
		}

		# Load file copy module, which contains the move() function.
		use File::Copy;

		# Overwrite the may existing rulefile or tarball with the downloaded one.
		move("$tmpfile", "$dl_rulesfile");

		# Delete temporary file.
		unlink("$tmpfile");

		# Set correct ownership for the tarball.
		set_ownership("$dl_rulesfile");
	}

	# If we got here, everything worked fine. Return nothing.
	return;
}

#
## Function to extract a given ruleset.
##
## In case the ruleset provider offers a plain file, it simply will
## be copied.
#
sub extractruleset ($) {
	my ($provider) = @_;

	# Load perl module to deal with archives.
	use Archive::Tar;

	# Disable chown functionality when uncompressing files.
	$Archive::Tar::CHOWN = "0";

	# Load perl module to deal with files and path.
	use File::Basename;

	# Load perl module for file copying.
	use File::Copy;

	# Get full path and downloaded rulesfile for the given provider.
	my $tarball = &_get_dl_rulesfile($provider);

	# Check if the file exists.
	unless (-f $tarball) {
		&_log_to_syslog("Could not find ruleset file: $tarball");

		# Return nothing.
		return;
	}

	# Check if the temporary directories exist, otherwise create them.
	mkdir("$tmp_directory") unless (-d "$tmp_directory");
	mkdir("$tmp_rules_directory") unless (-d "$tmp_rules_directory");
	mkdir("$tmp_conf_directory") unless (-d "$tmp_conf_directory");

	# Omit the type (dl_type) of the stored ruleset.
	my $type = $IDS::Ruleset::Providers{$provider}{'dl_type'};

	# Handle the different ruleset types.
	if ($type eq "plain") {
		# Generate destination filename an full path.
		my $destination = "$tmp_rules_directory/$provider\-ruleset.rules";

		# Copy the file into the temporary rules directory.
		copy($tarball, $destination);

	} elsif ( $type eq "archive") {
		# Initialize the tar module.
		my $tar = Archive::Tar->new($tarball);

		# Get the filelist inside the tarball.
		my @packed_files = $tar->list_files;

		# Loop through the filelist.
		foreach my $packed_file (@packed_files) {
			my $destination;

			# Splitt the packed file into chunks.
			my $file = fileparse($packed_file);

			# Handle msg-id.map file.
			if ("$file" eq "sid-msg.map") {
				# Set extract destination to temporary config_dir.
				$destination = "$tmp_conf_directory/$provider\-sid-msg.map";

			# Handle classification.conf
			} elsif ("$file" eq "classification.config") {
				# Set extract destination to temporary config_dir.
				$destination = "$tmp_conf_directory/$provider\-classification.config";

			# Handle rules files.
			} elsif ($file =~ m/\.rules$/) {
				# Skip rule files which are not located in the rules directory or archive root.
				next unless(($packed_file =~ /^rules\//) || ($packed_file !~ /\//));

				# Skip deleted.rules.
				#
				# Mostly they have been taken out for correctness or performance reasons and therfore
				# it is not a great idea to enable any of them.
				next if($file =~ m/deleted.rules$/);

				my $rulesfilename;

				# Splitt the filename into chunks.
				my @filename = split("-", $file);

				# Reverse the array.
				@filename = reverse(@filename);

				# Get the amount of elements in the array.
				my $elements = @filename;

				# Remove last element of the hash.
				# It contains the vendor name, which will be replaced.
				if ($elements >= 3) {
				# Remove last element from hash.
					pop(@filename);
				}

				# Check if the last element of the filename does not
				# contain the providers name.
				if ($filename[-1] ne "$provider") {
					# Add provider name as last element.
					push(@filename, $provider);
				}

				# Reverse the array back.
				@filename = reverse(@filename);

				# Generate the name for the rulesfile.
				$rulesfilename = join("-", @filename);

				# Set extract destination to temporaray rules_dir.
				$destination = "$tmp_rules_directory/$rulesfilename";
			} else {
				# Skip all other files.
				next;
			}

			# Check if the destination file exists.
			unless(-e "$destination") {
				# Extract the file to the temporary directory.
				$tar->extract_file("$packed_file", "$destination");
			} else {
				# Load perl module to deal with temporary files.
				use File::Temp;

				# Generate temporary file name, located in the temporary rules directory and a suffix of ".tmp".
				my $tmp = File::Temp->new( SUFFIX => ".tmp", DIR => "$tmp_rules_directory", UNLINK => 0 );
				my $tmpfile = $tmp->filename();

				# Extract the file to the new temporary file name.
				$tar->extract_file("$packed_file", "$tmpfile");

				# Open the the existing file.
				open(DESTFILE, ">>", "$destination") or die "Could not open $destination. $!\n";
				open(TMPFILE, "<", "$tmpfile") or die "Could not open $tmpfile. $!\n";

				# Loop through the content of the temporary file.
				while (<TMPFILE>) {
					# Append the content line by line to the destination file.
					print DESTFILE "$_";
				}

				# Close the file handles.
				close(TMPFILE);
				close(DESTFILE);

				# Remove the temporary file.
				unlink("$tmpfile");
			}
		}
	}
}

#
## A wrapper function to call the oinkmaster script, setup the rules structues and
## call the functions to merge the additional config files. (classification, sid-msg, etc.).
#
sub oinkmaster () {
	# Check if the files in rulesdir have the correct permissions.
	&_check_rulesdir_permissions();

	# Cleanup the rules directory before filling it with the new rulests.
	&_cleanup_rulesdir();

	# Get all enabled providers.
	my @enabled_providers = &get_enabled_providers();

	# Loop through the array of enabled providers.
	foreach my $provider (@enabled_providers) {
		# Call the extractruleset function.
		&extractruleset($provider);
	}

	# Load perl module to talk to the kernel syslog.
	use Sys::Syslog qw(:DEFAULT setlogsock);

	# Establish the connection to the syslog service.
	openlog('oinkmaster', 'cons,pid', 'user');

	# Call oinkmaster to generate ruleset.
	open(OINKMASTER, "/usr/local/bin/oinkmaster.pl -s -u dir://$tmp_rules_directory -C $settingsdir/oinkmaster.conf -o $rulespath 2>&1 |") or die "Could not execute oinkmaster $!\n";

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

	# Call function to merge the classification files.
	&merge_classifications(@enabled_providers);

	# Call function to merge the sid to message mapping files.
	&merge_sid_msg(@enabled_providers);

	# Cleanup temporary directory.
	&cleanup_tmp_directory();
}

#
## Function to merge the classifications for a given amount of providers and write them
## to the classifications file.
#
sub merge_classifications(@) {
	my @providers = @_;

	# Hash to store all collected classifications.
	my %classifications = ();

	# Loop through the given array of providers.
	foreach my $provider (@providers) {
		# Generate full path to classification file.
		my $classification_file = "$tmp_conf_directory/$provider\-classification.config";

		# Skip provider if no classification file exists.
		next unless (-f "$classification_file");

		# Open the classification file.
		open(CLASSIFICATION, $classification_file) or die "Could not open file $classification_file. $!\n";

		# Loop through the file content.
		while(<CLASSIFICATION>) {
			# Parse the file and grab the classification details.
			if ($_ =~/.*config classification\: (.*)/) {
				# Split the grabbed details.
				my ($short_name, $short_desc, $priority) = split("\,", $1);

				# Check if the grabbed classification is allready known and the priority value is greater
				# than the stored one (which causes less priority in the IDS).
				if (($classifications{$short_name}) && ($classifications{$short_name}[1] >= $priority)) {
					#Change the priority value to the stricter one.
					$classifications{$short_name} = [ "$classifications{$short_name}[0]", "$priority" ];
				} else {
					# Add the classification to the hash.
					$classifications{$short_name} = [ "$short_desc", "$priority" ];
				}
			}
		}

		# Close the file.
		close(CLASSIFICATION);
	}

	# Open classification file for writing.
	open(FILE, ">", "$classification_file") or die "Could not write to $classification_file. $!\n";

	# Print notice about autogenerated file.
	print FILE "#Autogenerated file. Any custom changes will be overwritten!\n\n";

	# Sort and loop through the hash of classifications.
	foreach my $key (sort keys %classifications) {
		# Assign some nice variable names for the items.
		my $short_name = $key;
		my $short_desc = $classifications{$key}[0];
		my $priority = $classifications{$key}[1];

		# Write the classification to the file.
		print FILE "config classification: $short_name,$short_desc,$priority\n";
	}

	# Close file handle.
	close(FILE);
}

#
## Function to merge the "sid to message mapping" files of various given providers.
#
sub merge_sid_msg (@) {
	my @providers = @_;

	# Hash which contains all the sid to message mappings.
	my %mappings = ();

	# Loop through the array of given providers.
	foreach my $provider (@providers) {
		# Generate full path and filename.
		my $sid_msg_file = "$tmp_conf_directory/$provider\-sid-msg.map";

		# Skip provider if no sid to msg mapping file for this provider exists.
		next unless (-f $sid_msg_file);

		# Open the file.
		open(MAPPING, $sid_msg_file) or die "Could not open $sid_msg_file. $!\n";

		# Loop through the file content.
		while (<MAPPING>) {
			# Remove newlines.
			chomp($_);

			# Skip lines which do not start with a number,
			next unless ($_ =~ /^\d+/);

			# Split line content and assign it to an array.
			my @line = split(/ \|\| /, $_);

			# Grab the first element (and remove it) from the line array.
			# It contains the sid.
			my $sid = shift(@line);

			# Store the grabbed sid and the remain array as hash value.
			# It still contains the messages, references etc.
			$mappings{$sid} = [@line];
		}

		# Close file handle.
		close(MAPPING);
	}

	# Open mappings file for writing.
	open(FILE, ">", $sid_msg_file) or die "Could not write $sid_msg_file. $!\n";

	# Write notice about autogenerated file.
	print FILE "#Autogenerated file. Any custom changes will be overwritten!\n\n";

	# Loop through the hash of mappings.
	foreach my $sid ( sort keys %mappings) {
		# Grab data for the sid.
		my @data = @{$mappings{$sid}};

		# Add the sid to the data array.
		unshift(@data, $sid);

		# Generate line.
		my $line = join(" \|\| ", @data);

		print FILE "$line\n";

	}

	# Close file handle.
	close(FILE);
}

#
## A very tiny function to move an extracted ruleset from the temporary directory into
## the rules directory.
#
sub move_tmp_ruleset() {
	# Load perl module.
	use File::Copy;

	# Do a directory listing of the temporary directory.
	opendir  DH, $tmp_rules_directory;

	# Loop over all files.
	while(my $file = readdir DH) {
		# Move them to the rules directory.
		move "$tmp_rules_directory/$file" , "$rulespath/$file";
	}

	# Close directory handle.
	closedir DH;
}

#
## Function to cleanup the temporary IDS directroy.
#
sub cleanup_tmp_directory () {
	# Load rmtree() function from file path perl module.
	use File::Path 'rmtree';

	# Delete temporary directory and all containing files.
	rmtree([ "$tmp_directory" ]);
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

	# Set correct ownership for the file.
	&set_ownership("$storederrorfile");
}

#
## Private function to get the path and filename for a downloaded ruleset by a given provider.
#
sub _get_dl_rulesfile($) {
	my ($provider) = @_;

	# Gather the download type for the given provider.
	my $dl_type = $IDS::Ruleset::Providers{$provider}{'dl_type'};

	# Obtain the file suffix for the download file type.
	my $suffix = $dl_type_to_suffix{$dl_type};

	# Check if a suffix has been found.
	unless ($suffix) {
		# Abort return - nothing.
		return;
	}

	# Generate the full filename and path for the stored rules file.
	my $rulesfile = "$dl_rules_path/$dl_rulesfile_prefix-$provider$suffix";

	# Return the generated filename.
	return $rulesfile;
}

#
## Tiny function to delete the stored ruleset file or tarball for a given provider.
#
sub drop_dl_rulesfile ($) {
	my ($provider) = @_;

	# Gather the full path and name of the stored rulesfile.
	my $rulesfile = &_get_dl_rulesfile($provider);

	# Check if the given rulesfile exists.
	if (-f $rulesfile) {
		# Delete the stored rulesfile.
		unlink($rulesfile) or die "Could not delete $rulesfile. $!\n";
	}
}

#
## Tiny function to get/generate the full path and filename for the providers oinkmaster
## modified sids file.
#
sub get_oinkmaster_provider_modified_sids_file ($) {
	my ($provider) = @_;

	# Generate the filename.
	my $filename = "$settingsdir/oinkmaster-$provider-modified-sids.conf";

	# Return the filename.
	return $filename;
}

#
## Function to directly altering the oinkmaster provider includes file.
##
## Requires tha acition "remove" or "add" and a provider handle.
#
sub alter_oinkmaster_provider_includes_file ($$) {
	my ($action, $provider) = @_;

	# Call function to get the path and name for the given providers
	# oinkmaster modified sids file.
	my $provider_modified_sids_file = &get_oinkmaster_provider_modified_sids_file($provider);

	# Open the file for reading..
	open (FILE, $oinkmaster_provider_includes_file) or die "Could not read $oinkmaster_provider_includes_file. $!\n";

	# Read-in file content.
	my @lines = <FILE>;

	# Close file after reading.
	close(FILE);

	# Re-open the file for writing.
	open(FILE, ">", $oinkmaster_provider_includes_file) or die "Could not write to $oinkmaster_provider_includes_file. $!\n";

	# Loop through the file content.
	foreach my $line (@lines) {
		# Remove newlines.
		chomp($line);

		# Skip line if we found our given provider and the action should be remove.
		next if (($line =~ /$provider/) && ($action eq "remove"));

		# Write the read-in line back to the file.
		print FILE "$line\n";
	}

	# Check if the file exists and add the provider if requested.
	if ((-f $provider_modified_sids_file) && ($action eq "add")) {
		print FILE "include $provider_modified_sids_file\n";
	}

	# Close file handle.
	close(FILE);
}

#
## Function to read-in the given enabled or disables sids file.
#
sub read_enabled_disabled_sids_file($) {
	my ($file) = @_;

	# Temporary hash to store the sids and their state. It will be
	# returned at the end of this function.
	my %temphash;

	# Open the given filename.
	open(FILE, "$file") or die "Could not open $file. $!\n";

	# Loop through the file.
	while(<FILE>) {
		# Remove newlines.
		chomp $_;

		# Skip blank lines.
		next if ($_ =~ /^\s*$/);

		# Skip coments.
		next if ($_ =~ /^\#/);

		# Splitt line into sid and state part.
		my ($state, $sid) = split(" ", $_);

		# Skip line if the sid is not numeric.
		next unless ($sid =~ /\d+/ );

		# Check if the sid was enabled.
		if ($state eq "enablesid") {
			# Add the sid and its state as enabled to the temporary hash.
			$temphash{$sid} = "enabled";
		# Check if the sid was disabled.
		} elsif ($state eq "disablesid") {
			# Add the sid and its state as disabled to the temporary hash.
			$temphash{$sid} = "disabled";
		# Invalid state - skip the current sid and state.
		} else {
			next;
		}
	}

	# Close filehandle.
	close(FILE);

	# Return the hash.
	return %temphash;
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
					&General::system("$suricatactrl", "$option", "$interval");

					# Return "1" - True.
					return 1;
				}
			}

			# If we got here, the given interval is not supported or none has been given. - Return nothing.
			return;
		} else {
			# Call the suricatactrl binary and pass the requrested
			# option to it.
			&General::system("$suricatactrl", "$option");

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

		# Skip rules file for whitelisted hosts.
		next if ("$rulespath/$file" eq $whitelist_file);

		# Skip rules file with local rules.
		next if ("$rulespath/$file" eq $local_rules_file);

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
	my @network_zones = &Network::get_available_network_zones();

	# Temporary array to store network address and prefix of the configured
	# networks.
	my @networks;

	# Loop through the array of available network zones.
	foreach my $zone (@network_zones) {
		# Check if the current processed zone is red.
		if($zone eq "red") {
			# Grab the IP-address of the red interface.
			my $red_address = &get_red_address();

			# Check if an address has been obtained.
			if ($red_address) {
				# Generate full network string.
				my $red_network = join("/", $red_address, "32");

				# Add the red network to the array of networks.
				push(@networks, $red_network);
			}

			# Check if the configured RED_TYPE is static.
			if ($netsettings{'RED_TYPE'} eq "STATIC") {
				# Get configured and enabled aliases.
				my @aliases = &get_aliases();

				# Loop through the array.
				foreach my $alias (@aliases) {
					# Add "/32" prefix.
					my $network = join("/", $alias, "32");

					# Add the generated network to the array of networks.
					push(@networks, $network);
				}
			}
		# Process remaining network zones.
		} else {
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
	}

	# Format home net declaration.
	my $line = "\"[" . join(',', @networks) . "]\"";

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
# Function to generate and write the file which contains the configured and used DNS servers.
#
sub generate_dns_servers_file() {
	# Get the used DNS servers.
	my @nameservers = &General::get_nameservers();

	# Get network settings.
	my %netsettings;
	&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

	# Format dns servers declaration.
	my $line = "";

	# Check if the system has configured nameservers.
	if (@nameservers) {
		# Add the GREEN address as DNS servers.
		push(@nameservers, $netsettings{'GREEN_ADDRESS'});

		# Check if a BLUE zone exists.
		if ($netsettings{'BLUE_ADDRESS'}) {
			# Add the BLUE address to the array of nameservers.
			push(@nameservers, $netsettings{'BLUE_ADDRESS'});
		}

		# Generate the line which will be written to the DNS servers file.
		$line = join(",", @nameservers);
	} else {
		# External net simply contains (any).
		$line = "\$EXTERNAL_NET";
	}

	# Open file to store the used DNS server addresses.
	open(FILE, ">$dns_servers_file") or die "Could not open $dns_servers_file. $!\n";

	# Print yaml header.
	print FILE "%YAML 1.1\n";
	print FILE "---\n\n";

	# Print notice about autogenerated file.
	print FILE "#Autogenerated file. Any custom changes will be overwritten!\n";

	# Print the generated DNS declaration to the file.
	print FILE "DNS_SERVERS:\t\"[$line]\"\n";

	# Close file handle.
	close(FILE);
}

#
# Function to generate and write the file which contains the HTTP_PORTS definition.
#
sub generate_http_ports_file() {
	my %proxysettings;

	# Read-in proxy settings
	&General::readhash("${General::swroot}/proxy/advanced/settings", \%proxysettings);

	# Check if the proxy is enabled.
	if (( -e "${General::swroot}/proxy/enable") || (-e "${General::swroot}/proxy/enable_blue")) {
		# Add the proxy port to the array of HTTP ports.
		push(@http_ports, $proxysettings{'PROXY_PORT'});
	}

	# Check if the transparent mode of the proxy is enabled.
	if ((-e "${General::swroot}/proxy/transparent") || (-e "${General::swroot}/proxy/transparent_blue")) {
		# Add the transparent proxy port to the array of HTTP ports.
		push(@http_ports, $proxysettings{'TRANSPARENT_PORT'});
	}

	# Format HTTP_PORTS declaration.
	my $line = "";

	# Generate line which will be written to the http ports file.
	$line = join(",", @http_ports);

	# Open file to store the HTTP_PORTS.
	open(FILE, ">$http_ports_file") or die "Could not open $http_ports_file. $!\n";

	# Print yaml header.
	print FILE "%YAML 1.1\n";
	print FILE "---\n\n";

	# Print notice about autogenerated file.
	print FILE "#Autogenerated file. Any custom changes will be overwritten!\n";

	# Print the generated HTTP_PORTS declaration to the file.
	print FILE "HTTP_PORTS:\t\"[$line]\"\n";

	# Close file handle.
	close(FILE);
}

#
## Function to generate and write the file for used rulefiles file for a given provider.
##
## The function requires as first argument a provider handle, and as second an array with files.
#
sub write_used_provider_rulefiles_file($@) {
	my ($provider, @files) = @_;

	# Get the path and file for the provider specific used rulefiles file.
	my $used_provider_rulesfile_file = &get_used_provider_rulesfile_file($provider);

	# Open file for used rulefiles.
	open (FILE, ">", "$used_provider_rulesfile_file") or die "Could not write to $used_provider_rulesfile_file. $!\n";

	# Write yaml header to the file.
	print FILE "%YAML 1.1\n";
	print FILE "---\n\n";

	# Write header to file.
	print FILE "#Autogenerated file. Any custom changes will be overwritten!\n";

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
## Function to write the main file for provider rulesfiles inclusions.
##
## This function requires an array of provider handles.
#
sub write_main_used_rulefiles_file (@) {
	my (@providers) = @_;

	# Call function to write the static rulefiles file.
	&_write_default_rulefiles_file();

	# Open file for used rulefils inclusion.
	open (FILE, ">", "$suricata_used_providers_file") or die "Could not write to $suricata_used_providers_file. $!\n";

	# Write yaml header to the file.
	print FILE "%YAML 1.1\n";
	print FILE "---\n\n";

	# Write header to file.
	print FILE "#Autogenerated file. Any custom changes will be overwritten!\n";

	# Loop through the list of given providers.
	foreach my $provider (@providers) {
		# Call function to get the providers used rulefiles file.
		my $filename = &get_used_provider_rulesfile_file($provider);

		# Check if the file exists and write it into the used rulefiles file.
		if (-f $filename) {
			# Print the provider to the file.
			print FILE "include\: $filename\n";
		}
	}

	# Close the filehandle after writing.
	close(FILE);
}

sub _write_default_rulefiles_file () {
	# Get enabled application layer protocols.
	my @enabled_app_layer_protos = &get_suricata_enabled_app_layer_protos();

	# Open file.
	open (FILE, ">", $suricata_default_rulefiles_file) or die "Could not write to $suricata_default_rulefiles_file. $!\n";

	# Write yaml header to the file.
	print FILE "%YAML 1.1\n";
	print FILE "---\n\n";

	# Write notice about autogenerated file.
	print FILE "#Autogenerated file. Any custom changes will be overwritten!\n";

	# Loop through the array of static included rulesfiles.
	foreach my $file (@static_included_rulefiles) {
		# Check if the file exists.
		if (-f "$rulespath/$file") {
			# Write the rulesfile name to the file.
			print FILE " - $rulespath/$file\n";
		}
	}

	print FILE "\n#Default rules for used application layer protocols.\n";
	foreach my $enabled_app_layer_proto (@enabled_app_layer_protos) {
		# Check if the current processed app layer proto needs to be translated
		# into an application name.
		if (exists($tr_app_layer_proto{$enabled_app_layer_proto})) {
			# Obtain the translated application name for this protocol.
			$enabled_app_layer_proto = $tr_app_layer_proto{$enabled_app_layer_proto};
		}

		# Generate filename.
		my $rulesfile = "$default_rulespath/$enabled_app_layer_proto\.rules";

		# Check if such a file exists.
		if (-f "$rulesfile") {
			# Write the rulesfile name to the file.
			print FILE " - $rulesfile\n";
		}

		# Generate filename with "events" in filename.
		$rulesfile = "$default_rulespath/$enabled_app_layer_proto\-events.rules";

		# Check if this file exists.
		if (-f "$rulesfile" ) {
			# Write the rulesfile name to the file.
			print FILE " - $rulesfile\n";
		}
	}

	# Close the file handle
	close(FILE);
}

#
## Tiny function to generate the full path and name for the used_provider_rulesfile file of a given provider.
#
sub get_used_provider_rulesfile_file ($) {
	my ($provider) = @_;

	my $filename = "$settingsdir/suricata\-$provider\-used\-rulefiles.yaml";

	# Return the gernerated file.
	return $filename;
}

#
## Function to generate and write the file for modify the ruleset.
#
sub write_modify_sids_file() {
	# Get configured settings.
	my %idssettings=();
	&General::readhash("$ids_settings_file", \%idssettings);

	# Open modify sid's file for writing.
	open(FILE, ">$modify_sids_file") or die "Could not write to $modify_sids_file. $!\n";

	# Write file header.
	print FILE "#Autogenerated file. Any custom changes will be overwritten!\n";

	# Check if the traffic only should be monitored.
	unless($idssettings{'MONITOR_TRAFFIC_ONLY'} eq 'on') {
		# Suricata is in IPS mode, which means that the rule actions have to be changed
		# from 'alert' to 'drop', however not all rules should be changed.  Some rules
		# exist purely to set a flowbit which is used to convey other information, such
		# as a specific type of file being downloaded, to other rulewhich then check for
		# malware in that file.  Rules which fall into the first category should stay as
		# alert since not all flows of that type contain malware.

		# These types of rulesfiles contain meta-data which gives the action that should
		# be used when in IPS mode.  Do the following:
		#
		# 1. Disable all rules and set the action to 'drop'
		# 2. Set the action back to 'alert' if the rule contains 'flowbits:noalert;'
		#    This should give rules not in the policy a reasonable default if the user
		#    manually enables them.
		# 3. Enable rules and set actions according to the meta-data strings.

		my $policy = 'balanced';  # Placeholder to allow policy to be changed.

			print FILE <<END;
modifysid * "^#(?:alert|drop)(.+policy $policy-ips alert)" | "alert\${1}"
modifysid * "^#(?:alert|drop)(.+policy $policy-ips drop)" | "drop\${1}"
modifysid * "^(#?)(?:alert|drop)" | "\${1}drop"
modifysid * "^(#?)drop(.+flowbits:noalert;)" | "\${1}alert\${2}"
END
		}

	# Close file handle.
	close(FILE);
}

#
## Function to get the ruleset date for a given provider.
##
## The function simply return the creation date in a human read-able format
## of the stored providers rulesfile.
#
sub get_ruleset_date($) {
	my ($provider) = @_;
	my $date;
	my $mtime;

	# Load neccessary perl modules for file stat and to format the timestamp.
	use File::stat;
	use POSIX qw( strftime );

	# Get the stored rulesfile for this provider.
	my $stored_rulesfile = &_get_dl_rulesfile($provider);

	# Check if we got a file.
	if (-f $stored_rulesfile) {
		# Call stat on the rulestarball.
		my $stat = stat("$stored_rulesfile");

		# Get timestamp the file creation.
		$mtime = $stat->mtime;
	}

	# Check if the timestamp has not been grabbed.
	unless ($mtime) {
		# Return N/A for Not available.
		return "N/A";
	}

	# Convert into human read-able format.
	$date = strftime('%Y-%m-%d %H:%M:%S', localtime($mtime));

	# Return the date.
	return $date;
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

#
## Function to get the enabled application layer protocols.
#
sub get_suricata_enabled_app_layer_protos() {
	# Array to store and return the enabled app layer protos.
	my @enabled_app_layer_protos = ();

	# Execute piped suricata command and return the list of
	# enabled application layer protocols.
	open(SURICATA, "suricata --list-app-layer-protos |") or die "Could not execute program: $!";

	# Grab and store the list of enabled application layer protocols.
	my @output = <SURICATA>;

	# Close pipe.
	close(SURICATA);

	# Merge allways enabled static application layers protocols array.
	@enabled_app_layer_protos = @static_enabled_app_layer_protos;

	# Loop through the array which contains the output of suricata.
	foreach my $line (@output) {
		# Skip header line which starts with "===".
		next if ($line =~ /^\s*=/);

		# Skip info or warning lines.
		next if ($line =~ /\s*--/);

		# Remove newlines.
		chomp($line);

		# Add enabled app layer proto to the array.
		push(@enabled_app_layer_protos, $line);
	}

	# Sort the array.
	@enabled_app_layer_protos = sort(@enabled_app_layer_protos);

	# Return the array.
	return @enabled_app_layer_protos;
}

#
## Function to generate the rules file with whitelisted addresses.
#
sub generate_ignore_file() {
	my %ignored = ();

	# SID range 1000000-1999999 Reserved for Local Use
	# Put your custom rules in this range to avoid conflicts
	my $sid = 1500000;

	# Read-in ignoredfile.
	&General::readhasharray($IDS::ignored_file, \%ignored);

	# Open ignorefile for writing.
	open(FILE, ">$IDS::whitelist_file") or die "Could not write to $IDS::whitelist_file. $!\n";

	# Config file header.
	print FILE "# Autogenerated file.\n";
	print FILE "# All user modifications will be overwritten.\n\n";

	# Add all user defined addresses to the whitelist.
	#
	# Check if the hash contains any elements.
	if (keys (%ignored)) {
		# Loop through the entire hash and write the host/network
		# and remark to the ignore file.
		while ( (my $key) = each %ignored) {
			my $address = $ignored{$key}[0];
			my $remark = $ignored{$key}[1];
			my $status = $ignored{$key}[2];

			# Check if the status of the entry is "enabled".
			if ($status eq "enabled") {
				# Check if the address/network is valid.
				if ((&General::validip($address)) || (&General::validipandmask($address))) {
					# Write rule line to the file to pass any traffic from this IP
					print FILE "pass ip $address any -> any any (msg:\"pass all traffic from/to $address\"\; bypass; sid:$sid\;)\n";

					# Increment sid.
					$sid++;
				}
			}
		}
	}

	close(FILE);
}

#
## Function to set correct ownership for single files and directories.
#

sub set_ownership($) {
	my ($target) = @_;

	# User and group of the WUI.
	my $uname = "nobody";
	my $grname = "nobody";

	# The chown function implemented in perl requies the user and group as nummeric id's.
	my $uid = getpwnam($uname);
	my $gid = getgrnam($grname);

	# Check if the given target exists.
	unless ($target) {
		# Stop the script and print error message.
		die "The $target does not exist. Cannot change the ownership!\n";
	}

	# Check weather the target is a file or directory.
	if (-f $target) {
		# Change ownership ot the single file.
		chown($uid, $gid, "$target");
	} elsif (-d $target) {
		# Do a directory listing.
		opendir(DIR, $target) or die $!;
			# Loop through the direcory.
			while (my $file = readdir(DIR)) {

				# We only want files.
				next unless (-f "$target/$file");

				# Set correct ownership for the files.
				chown($uid, $gid, "$target/$file");
			}

		closedir(DIR);

		# Change ownership of the directory.
		chown($uid, $gid, "$target");
	}
}

#
## Function to read-in the aliases file and returns all configured and enabled aliases.
#
sub get_aliases() {
	# Location of the aliases file.
	my $aliases_file = "${General::swroot}/ethernet/aliases";

	# Array to store the aliases.
	my @aliases;

	# Check if the file is empty.
	if (-z $aliases_file) {
		# Abort nothing to do.
		return;
	}

	# Open the aliases file.
	open(ALIASES, $aliases_file) or die "Could not open $aliases_file. $!\n";

	# Loop through the file content.
	while (my $line = <ALIASES>) {
		# Remove newlines.
		chomp($line);

		# Splitt line content into single chunks.
		my ($address, $state, $remark) = split(/\,/, $line);

		# Check if the state of the current processed alias is "on".
		if ($state eq "on") {
			# Check if the address is valid.
			if(&Network::check_ip_address($address)) {
				# Add the alias to the array of aliases.
				push(@aliases, $address);
			}
		}
	}

	# Close file handle.
	close(ALIASES);

	# Return the array.
	return @aliases;
}

#
## Function to grab the current assigned IP-address on red.
#
sub get_red_address() {
	# File, which contains the current IP-address of the red interface.
	my $file = "${General::swroot}/red/local-ipaddress";

	# Check if the file exists.
	if (-e $file) {
		# Open the given file.
		open(FILE, "$file") or die "Could not open $file.";

		# Obtain the address from the first line of the file.
		my $address = <FILE>;

		# Close filehandle
		close(FILE);

		# Remove newlines.
		chomp $address;

		# Check if the grabbed address is valid.
		if (&General::validip($address)) {
			# Return the address.
			return $address;
		}
	}

	# Return nothing.
	return;
}

#
## Function to get the used rules files of a given provider.
#
sub read_used_provider_rulesfiles($) {
	my ($provider) = @_;

	# Array to store the used rulefiles.
	my @used_rulesfiles = ();

	# Get the used rulesefile file for the provider.
	my $rulesfile_file = &get_used_provider_rulesfile_file($provider);

	# Check if the a used rulesfile exists for this provider.
	if (-f $rulesfile_file) {
		# Open the file or used rulefiles and read-in content.
		open(FILE, $rulesfile_file) or die "Could not open $rulesfile_file. $!\n";

		while (<FILE>) {
			# Assign the current line to a nice variable.
			my $line = $_;

			# Remove newlines.
			chomp($line);

			# Skip comments.
			next if ($line =~ /\#/);

			# Skip blank  lines.
			next if ($line =~ /^\s*$/);

			# Gather the rulefile.
			if ($line =~ /.*- (.*)/) {
				my $rulefile = $1;

				# Add the rulefile to the array of used rulesfiles.
				push(@used_rulesfiles, $rulefile);
			}
		}

		# Close the file.
		close(FILE);
	}

	# Return the array of used rulesfiles.
	return @used_rulesfiles;
}

#
## Function to write the lock file for locking the WUI, while
## the autoupdate script runs.
#
sub lock_ids_page() {
	# Call subfunction to create the file.
	&create_empty_file($ids_page_lock_file);
}

#
## Function to release the lock of the WUI, again.
#
sub unlock_ids_page() {
	# Delete lock file.
	unlink($ids_page_lock_file);
}

1;
