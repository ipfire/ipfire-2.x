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

# Location and name of the tarball which contains the ruleset.
our $rulestarball = "/var/tmp/idsrules.tar.gz";

# File to store any errors, which also will be read and displayed by the wui.
our $storederrorfile = "/tmp/ids_storederror";

# Location where the rulefiles are stored.
our $rulespath = "/etc/suricata/rules";

# File which contains a list of all supported ruleset sources.
# (Sourcefire, Emergingthreads, etc..)
our $rulesetsourcesfile = "$settingsdir/ruleset-sources";

# The pidfile of the IDS.
our $idspidfile = "/var/run/suricata.pid";

# Location of suricatactrl.
my $suricatactrl = "/usr/local/bin/suricatactrl";

# Array with allowed commands of suricatactrl.
my @suricatactrl_cmds = ( 'start', 'stop', 'restart', 'reload' );

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
## This function is responsible for downloading the configured snort ruleset.
##
## * At first it obtains from the stored snortsettings which ruleset should be downloaded.
## * The next step is to get the download locations for all available rulesets.
## * After that, the function will check if an upstream proxy should be used and grab the settings.
## * The last step will be to generate the final download url, by obtaining the URL for the desired
##   ruleset, add the settings for the upstream proxy and final grab the rules tarball from the server.
#
sub downloadruleset {
	# Get snort settings.
	my %snortsettings=();
	&General::readhash("$settingsdir/settings", \%snortsettings);

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
		$downloader->proxy('http', $proxy_url);
	}

	# Grab the right url based on the configured vendor.
	my $url = $rulesetsources{$snortsettings{'RULES'}};

	# Check if the vendor requires an oinkcode and add it if needed.
	$url =~ s/\<oinkcode\>/$snortsettings{'OINKCODE'}/g;

	# Abort if no url could be determined for the vendor.
	unless ($url) {
		# Log error and abort.
		&_log_to_syslog("Unable to gather a download URL for the selected ruleset.");
		return 1;
	}

	# Pass the requested url to the downloader.
	my $request = HTTP::Request->new(GET => $url);

	# Perform the request and save the output into the "$rulestarball" file.
	my $response = $downloader->request($request, $rulestarball);

	# Check if there was any error.
	unless ($response->is_success) {
		# Log error message.
		&_log_to_syslog("Unable to download the ruleset. $response->status_line");

		# Return "1" - false.
		return 1;
	}

	# If we got here, everything worked fine. Return nothing.
	return;
}

#
## A tiny wrapper function to call the oinkmaster script.
#
sub oinkmaster () {
	# Load perl module to talk to the kernel syslog.
	use Sys::Syslog qw(:DEFAULT setlogsock);

	# Establish the connection to the syslog service.
	openlog('oinkmaster', 'cons,pid', 'user');

	# Call oinkmaster to generate ruleset.
	open(OINKMASTER, "/usr/local/bin/oinkmaster.pl -v -s -u file://$rulestarball -C $settingsdir/oinkmaster.conf -o $rulespath|");

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
	my ($option) = @_;

	# Loop through the array of supported commands and check if
	# the given one is part of it.
	foreach my $cmd (@suricatactrl_cmds) {
		# Skip current command unless the given one has been found.
		next unless($cmd eq $option);

		# Call the suricatactrl binary and pass the requrested
		# option to it.
		system("$suricatactrl $option &>/dev/null");

		# Return "1" - True.
		return 1;
	}

	# Command not found - return nothing.
	return;
}

1;
