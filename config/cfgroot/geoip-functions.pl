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

use Location;
use Locale::Codes::Country;

# Hash which contains country codes and their names which are special or not
# part of ISO 3166-1.
my %not_iso_3166_location = (
	"a1" => "Anonymous Proxy",
	"a2" => "Satellite Provider",
	"a3" => "Worldwide Anycast Instance",
	"an" => "Netherlands Antilles",
	"ap" => "Asia/Pacific Region",
	"eu" => "Europe",
	"fx" => "France, Metropolitan"
);

# Directory where the libloc database and keyfile lives.
our $location_dir = "/var/lib/location/";

# Libloc database file.
our $database = "$location_dir/database.db";

# Libloc keyfile to verify the database.
our $keyfile = "$location_dir/signing-key.pem";

# Directory which contains the exported databases.
our $xt_geoip_db_directory = "/usr/share/xt_geoip/";

#
## Tiny function to init the location database.
#
sub init () {
	# Init and open the database.
	my $db = &Location::init($database);

	# Return the database handle.
	return $db;
}

#
## Function to verify the integrity of the location database.
#
sub verify ($) {
	my ($db_handle) = @_;

	# Verify the integrity of the database.
	if(&Location::verify($db_handle, $keyfile)) {
		# Success, return "1".
		return 1;
	}

	# If we got here, return nothing.
	return;
}

#
## Function to the the country code of a given address.
#
sub lookup_country_code($$) {
	my ($db_handle, $address) = @_;

	# Lookup the given address.
	my $country_code = &Location::lookup_country_code($db_handle, $address);

	# Return the name of the country
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
	if ($not_iso_3166_location{$code}) {
		# Grab location name from hash.
		$name = $not_iso_3166_location{$code};
	} else {
		# Use perl built-in module to get the country code.
		$name = &Locale::Codes::Country::code2country($code);
	}

	return $name;
}

# Function to get all available GeoIP locations.
sub get_geoip_locations() {
	my @locations = ();

	# Get listed country codes from ISO 3166-1.
	my @locations_lc = &Locale::Codes::Country::all_country_codes();

	# The Codes::Country module provides the country codes only in lower case.
	# So we have to loop over the array and convert them into upper case format.
	foreach my $ccode (@locations_lc) {
		# Convert the country code to uppercase.
		my $ccode_uc = uc($ccode);

		# Add the converted ccode to the locations array.
		push(@locations, $ccode_uc);
	}

	# Add locations from not_iso_3166_locations.
	foreach my $location (keys %not_iso_3166_location) {
		# Convert the location into uppercase.
		my $location_uc = uc($location);

		# Add the location to the locations array.
		push(@locations, $location_uc);
	}

	# Sort locations array in alphabetical order.
	my @sorted_locations = sort(@locations);

	# Return the array..
	return @sorted_locations;
}

1;
