#!/usr/bin/perl -w
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2022  IPFire Team  <info@ipfire.org>                     #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

package IPblocklist;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/ipblocklist/sources";

# The directory where all ipblocklist related files and settings are stored.
our $settings_dir = "/var/ipfire/ipblocklist";

# Main settings file.
our $settings_file = "$settings_dir/settings";

# The file which keeps the time, when a blocklist last has been modified.
my $modified_file = "$settings_dir/modified";

# Location where the blocklists in ipset compatible format are stored.
my $blocklist_dir = "/var/lib/ipblocklist";

# File extension of the blocklist files.
my $blocklist_file_extension = ".conf";

# Hash which calls the correct parser functions.
my %parsers = (
	'ip-or-net-list' => \&parse_ip_or_net_list,
	'dshield'        => \&parse_dshield
);

#
## Function to get all available blocklists.
#
sub get_blocklists () {
	my @blocklists;

	# Loop through the hash of blocklists.
	foreach my $blocklist ( keys %IPblocklist::List::sources ) {
		# Add the list to the array.
		push(@blocklists, $blocklist);
	}

	# Sort and return the array.
	return sort(@blocklists);
}

#
## Tiny function to get the full path and name of a given blocklist.
#
sub get_ipset_db_file($) {
	my ($set) = @_;

	# Generate the
	my $file = "$blocklist_dir/$set$blocklist_file_extension";

	# Return the file name.
	return $file;
}

#
## The main download_and_create blocklist function.
##
## Uses LWP to download a given blocklist. The If-Modified-Since header is
## specified in the request so that only updated lists are downloaded (providing
## that the server supports this functionality).
##
## Once downloaded the list gets parsed, converted and stored in an ipset compatible
## format.
##
## Parameters:
##   list      The name of the blocklist
##
## Returns:
##   nothing - On success
##   not_modified - In case the servers responds with "Not modified" (304)
##   dl_error - If the requested blocklist could not be downloaded.
#
sub download_and_create_blocklist($) {
	my ($list) = @_;

	# Check if the given blockist is known and data available.
	unless($IPblocklist::List::sources{$list}) {
		# No valid data for this blocklist - exit and return "1".
		return 1;
	}

	# The allowed maximum download size in bytes.
	my $max_dl_bytes = 10_485_760;

	# The amount of download attempts before giving up and
	# logging an error.
	my $max_dl_attempts = 5;

	# Read proxysettings.
	my %proxysettings=();
	&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);

	# Load required perl module to handle the download.
	use LWP::UserAgent;

	# Create a user agent for downloading the blacklist
	# Limit the download size for safety
	my $ua = LWP::UserAgent->new (
		ssl_opts => {
			SSL_ca_file     => '/etc/ssl/cert.pem',
			verify_hostname => 1,
		},

		max_size => $max_dl_bytes,
	);

	# Set timeout to 10 seconds.
	$ua->timeout(10);

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
		$ua->proxy(['http', 'https'], $proxy_url);
	}

	# Gather the details, when a list got modified last time.
	my %modified = ();

	# Read-in data if the file exists.
	&General::readhash($modified_file, \%modified ) if (-e $modified_file);

	# Get the last modified time for this list.
	my $last_modified = gmtime($modified{$list} || 0);

	my $dl_attempt = 1;
	my $response;

	# Download and rety on failure loop.
	while ($dl_attempt <= $max_dl_attempts) {
		# Try to determine if there is a newer blocklist since last time and grab it.
		$response = $ua->get($IPblocklist::List::sources{$list}{'url'}, 'If-Modified-Since' => $last_modified );

		# Check if the download attempt was successfull.
		if ($response->is_success) {
			# We successfully grabbed the list - no more retries needed, break the loop.
			# Further process the script code.
			last;

		# Exit, if the server responds with "Not modified (304).
		} elsif ($response->code == 304) {
			# Exit and return "not modified".
			return "not_modified";

		# Exit and log an erro
		} elsif ($dl_attempt eq $max_dl_attempts) {
			# Exit and return "dl_error".
			return "dl_error";
		}

		# Increase download attempt counter.
		$dl_attempt++;
	}

	# Update the timestamp for the new or modified list.
	$modified{$list} = $response->last_modified;

	# Write-back the modified timestamps.
	&General::writehash($modified_file, \%modified);

	# Parse and loop through the downloaded list.
	my @blocklist = ();

	# Get the responsible parser for the current list.
	my $parser = $parsers{$IPblocklist::List::sources{$list}{'parser'}};

	# Loop through the grabbed raw list.
	foreach my $line (split /[\r\n]+/, $response->content) {
		# Remove newlines.
		chomp $line;

		# Call the parser and obtain the addess or network.
		my $address = &$parser($line);

		# Skip the line if it does not contain an address.
		next unless ($address and $address =~ m/\d+\.\d+\.\d+\.\d+/);

		# Check if we got a single address.
		if ($address =~ m|/32|) {
			# Add /32 as prefix.
			$address =~ s|/32||;
		}

		# Push the address/network to the blocklist array.
		push(@blocklist, $address);
	}

	# Get amount of entries in the blocklist array.
	my $list_entries = scalar(@blocklist);

	# Optain the filename for this blocklist to save.
	my $file = &get_ipset_db_file($list);

	# Open the file for writing.
	open(FILE, ">", "$file") or die "Could not write to $file. $!\n";

	# Write file header.
	print FILE "#Autogenerated file. Any custom changes will be overwritten!\n\n";

	# Calculate the hashsize for better list performance.
	my $hashsize = &_calculate_hashsize($list_entries);

	# Simply set the limit of list elements to the double of current list elements.
	my $maxelem = $list_entries *2;

	# Write line to create the set.
	#
	# We safely can use hash:net as type because it supports single addresses and networks.
	print FILE "create $list hash:net family inet hashsize $hashsize maxelem $maxelem -exist\n";

	# Write line to flush the set itself during loading.
	print FILE "flush $list\n";

	# Loop through the array which contains the blocklist.
	foreach my $entry (@blocklist) {
		# Add the entry to the list.
		print FILE "add $list $entry\n";
	}

	# Close the file handle.
	close(FILE);

	# Finished.
	return;
}

1;
