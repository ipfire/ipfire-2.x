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
# Copyright (C) 2015 IPFire Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################

package GeoIP;

require '/var/ipfire/network-functions.pl';

use Locale::Codes::Country;

# Path where all the GeoIP related databases are stored.
my $geoip_database_dir = "/var/lib/GeoIP";

# Database which contains all IPv4 networks.
my $address_ipv4_database = "GeoLite2-Country-Blocks-IPv4.csv";

# Database wich contains the locations data.
my $location_database = "GeoLite2-Country-Locations-en.csv";

sub lookup($) {
	my $address = shift;
	my $location_id;
	my $country_code;

	# Check if the given address is valid.
	unless(&Network::check_ip_address($address)) {
		return;
	}

	# Open the address database.
	open(ADDRESS, "$geoip_database_dir/$address_ipv4_database") or die "Could not open $geoip_database_dir/$address_ipv4_database. $!\n";

	# Loop through the file.
	while(my $line = <ADDRESS>) {
		# Remove newlines.
		chomp($line);

		# Split the line content.
		my ($network, $geoname_id, $registered_country_geoname_id, $represented_country_geoname_id, $is_anonymous_proxy, $is_satellite_provider) = split(/\,/, $line);

		# Check if the given address is part of the current processed network.
		if (&Network::ip_address_in_network($address, $network)) {
			# Store the geoname_id for this address.
			$location_id = $geoname_id;

			# Break loop.
			last;
		}
	}

	# Return nothing if no location_id could be found.
	return unless($location_id);

	# Close filehandle.
	close(ADDRESS);

	# Open the location database.
	open(LOCATION, "$geoip_database_dir/$location_database") or die "Could not open $geoip_database_dir/$location_database. $!\n";

	# Loop through the file.
	while(my $line = <LOCATION>) {
		# Remove newlines.
		chomp($line);

		# Split the line content.
		my ($geoname_id, $locale_code, $continent_code, $continent_name, $country_iso_code, $country_name, $is_in_european_union) = split(/\,/, $line);

		# Check if the correct location_id has been found.
		if ($geoname_id eq $location_id) {
			# Store the county code.
			$country_code = $country_iso_code;

			# Break loop.
			last;
		}
	}

	# Close filehandle.
	close(LOCATION);

	# Return the obtained country code.
	return $country_code;
}

# Function to get the flag icon for a specified country code.
sub get_flag_icon($) {
	my ($input) = @_;

	# Webserver's root dir. (Required for generating full path)
	my $webroot = "/srv/web/ipfire/html";

	# Directory which contains the flag icons.
	my $flagdir = "/images/flags";

	# File extension of the country flags.
	my $ext = "png";

	# Remove whitespaces.
	chomp($input);

	# Convert given country code to upper case.
	my $ccode = uc($input);

	# Generate filename, based on the contry code in lower case
	# and the defined file extension.
	my $file = join('.', $ccode,$ext);

	# Generate path inside webroot to the previously generated file.
	my $flag_icon = join('/', $flagdir,$file);

	# Generate absolute path to the icon file.
	my $absolute_path = join('', $webroot,$flag_icon);
 
	# Check if the a icon file exists.
	if (-e "$absolute_path") {
		# Return content of flag_icon.
		return $flag_icon;
	} else {
		# If no icon for the specified country exists, try to use
		# the icon for "unknown".
		my $ccode = "unknown";

		# Redoing all the stuff from above for the "unknown" icon.
		my $file = join('.', $ccode, $ext);
		my $flag_icon = join('/', $flagdir, $file);
		my $absolute_path = join('', $webroot, $flag_icon);

		# Check if the icon is present.
		if (-e "$absolute_path") {
			# Return "unknown" icon.
			return $flag_icon;
		}
	}
}

# Function to get the county name by a given country code.
sub get_full_country_name($) {
	my ($input) = @_;
	my $name;

	# Remove whitespaces.
	chomp($input);

	# Convert input into lower case format.
	my $code = lc($input);

	# Handle country codes which are not in the list.
	if ($code eq "a1") { $name = "Anonymous Proxy" }
	elsif ($code eq "a2") { $name = "Satellite Provider" }
	elsif ($code eq "o1") { $name = "Other Country" }
	elsif ($code eq "ap") { $name = "Asia/Pacific Region" }
	elsif ($code eq "eu") { $name = "Europe" }
	elsif ($code eq "yu") { $name = "Yugoslavia" }
	else {
		# Use perl built-in module to get the country code.
		$name = &Locale::Codes::Country::code2country($code);
	}

	return $name;
}

# Function to get all available GeoIP locations.
sub get_geoip_locations() {
	my @locations;

	# Open the location database.
	open(LOCATION, "$geoip_database_dir/$location_database") or die "Could not open $geoip_database_dir/$location_database. $!\n";

	# Loop through the file.
	while(my $line = <LOCATION>) {
		# Remove newlines.
		chomp($line);

		# Split the line content.
		my ($geoname_id, $locale_code, $continent_code, $continent_name, $country_iso_code, $country_name, $is_in_european_union) = split(/\,/, $line);

		# Check if the country_iso_code is upper case.
		if($country_iso_code =~ /[A-Z]/) {
			# Add the current ISO code.
			push(@locations, $country_iso_code);
		}
	}

	# Close filehandle.
	close(LOCATION);

	# Sort locations array in alphabetical order.
	my @sorted_locations = sort(@locations);

	# Return the array..
	return @sorted_locations;
}


1;
