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
require "${General::swroot}/lang.pl";

# Location and name of the tarball which contains the ruleset.
my $rulestarball = "/var/tmp/snortrules.tar.gz";

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
				# If there is not enough space, print out an error message.
				my $errormessage = "$Lang::tr{'not enough disk space'} < 300MB, /var $available MB";

				# Exit function and return the error message.
				return $errormessage;
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
	&General::readhash("${General::swroot}/snort/settings", \%snortsettings);

	# Get all available ruleset locations.
	my %rulesetsources=();
	&General::readhash("${General::swroot}/snort/ruleset-sources.list", \%rulesetsources);

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
			# Break and return error message.
			return "$Lang::tr{'could not download latest updates'}";
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
		# Abort and return errormessage.
		return "$Lang::tr{'could not download latest updates'}";
	}

	# Pass the requested url to the downloader.
	my $request = HTTP::Request->new(GET => $url);

	# Perform the request and save the output into the "$rulestarball" file.
	my $response = $downloader->request($request, $rulestarball);

	# Check if there was any error.
	unless ($response->is_success) {
		# Return error message.
		return "$response->status_line";
	}

	# If we got here, everything worked fine. Return nothing.
	return;
}

#
## A tiny wrapper function to call the oinkmaster script.
#
sub oinkmaster () {
	# Call oinkmaster to generate ruleset.
	system("/usr/local/bin/oinkmaster.pl -v -s -u file://$rulestarball -C /var/ipfire/snort/oinkmaster.conf -o /etc/snort/rules 2>&1 |logger -t oinkmaster");
}

1;
