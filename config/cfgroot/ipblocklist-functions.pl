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
##   empty_list - The downloaded blocklist is empty, or the parser was not able to parse
##                it correctly.
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
	if($response->last_modified) {
		$modified{$list} = $response->last_modified;
	} else {
		$modified{$list} = time();
	}

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

	# Check if the content could be parsed correctly and the blocklist
	# contains at least one item.
	unless(@blocklist) {
		# No entries - exit and return "empty_list".
		return "empty_list";
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

#
## sub parse_ip_or_net_list( line )
##
## Parses an input line, looking for lines starting with an IP Address or
### Network specification.
##
## Parameters:
##   line  The line to parse
##
## Returns:
##   Either an IP Address or a null string
#
sub parse_ip_or_net_list( $ ) {
	my ($line) = @_;

	# Grab the IP address or network.
	$line =~ m|^(\d+\.\d+\.\d+\.\d+(?:/\d+)?)|;

	# Return the grabbed address.
	return $1;
}

#
## sub parse_dshield( line )
##
## Parses an input line removing comments.
##
## The format is:
## Start Addrs   End Addrs   Netmask   Nb Attacks   Network Name   Country   email
## We're only interested in the start address and netmask.
##
## Parameters:
##   line  The line to parse
##
## Returns:
##   Either and IP Address or a null string
#
sub parse_dshield( $ ) {
	my ($line) = @_;

	# Skip coments.
	return "" if ($line =~ m/^\s*#/);

	$line =~ s/#.*$//;

	#          |Start addrs                |   |End Addrs                |   |Mask
	$line =~ m|(\d+\.\d+\.\d+\.\d+(?:/\d+)?)\s+\d+\.\d+\.\d+\.\d+(?:/\d+)?\s+(\d+)|;

	# Return nothing if no start address could be grabbed.
	return unless ($1);

	# Add /32 as prefix for single addresses and return it.
	return "$1/32" unless ($2);

	# Return the obtained network.
	return "$1/$2";
}

#
## Helper function to proper calculate the hashsize.
#
sub _calculate_hashsize($) {
	my ($list_entries) = @_;

	my $hashsize = 1;
	$hashsize  <<= 1 while ($hashsize < $list_entries);

	# Return the calculated hashsize.
	return $hashsize;
}

#
## sub get_holdoff_rate(list)
##
## This function is used to get the holdoff rate in seconds for a desired provider,
## based on the configured rate limit in minutes (m), hours (h) or days (d) in the
## blacklist sources settings file.
##
#
sub get_holdoff_rate($) {
	my ($list) = @_;

	# Grab the configured lookup rate for the given list.
	my $rate = $IPblocklist::List::sources{$list}{'rate'};

	# Split the grabbed rate into value and unit.
	my ($value, $unit) = (uc $rate) =~ m/(\d+)([DHM]?)/;

	# Days
	if ($unit eq 'D') {
		$value *= 60 * 60 * 24;

	# Minutes
	} elsif ($unit eq 'M') {
		$value *= 60;

	# Everything else - assume hours.
	} else {
		$value *= 60 * 60;
	}

	# Sanity check - limit to range 5 min .. 1 week

	#        d    h    m    s
	$value =           5 * 60 if ($value < 5 * 60);
	$value = 7 * 24 * 60 * 60 if ($value > 7 * 24 * 60 * 60);

	return $value;
}

1;
