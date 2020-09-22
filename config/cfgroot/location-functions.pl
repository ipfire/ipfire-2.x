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
# Copyright (C) 2015 - 2020 IPFire Team <info@ipfire.org>.                 #
#                                                                          #
############################################################################

package Location::Functions;

use Location;

# Hash which contains country codes and their names which are special or not
# part of ISO 3166-1.
my %not_iso_3166_location = (
	"A1" => "Anonymous Proxy",
	"A2" => "Satellite Provider",
	"A3" => "Worldwide Anycast Instance",
);

# Hash which contains possible network flags and their mapped location codes.
my %network_flags = (
	"LOC_NETWORK_FLAG_ANONYMOUS_PROXY" => "A1",
	"LOC_NETWORK_FLAG_SATELLITE_PROVIDER" => "A2",
	"LOC_NETWORK_FLAG_ANYCAST" => "A3",
);

# Array which contains special country codes.
my @special_locations = ( "A1", "A2", "A3" );

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

	# Convert input into upper case format.
	my $code = uc($input);

	# Handle country codes which are special or not part of the list.
	if ($not_iso_3166_location{$code}) {
		# Grab location name from hash.
		$name = $not_iso_3166_location{$code};
	} else {
		# Init libloc database connection.
		my $db_handle = &init();

		# Get the country name by using the location module.
		$name = &Location::get_country_name($db_handle, $code);
	}

	return $name;
}

# Function to get all available locations.
sub get_locations() {
	# Create libloc database handle.
	my $db_handle = &init();

	# Get locations which are stored in the location database.
	my @database_locations = &Location::database_countries($db_handle);

	# Merge special locations array and the database locations array.
	my @locations = (@special_locations, @database_locations);

	# Sort locations array in alphabetical order.
	my @sorted_locations = sort(@locations);

	# Return the array..
	return @sorted_locations;
}

# Function to check if a given address has a special flag.
sub address_has_flag($) {
	my ($address) = @_;

	# Init libloc database handle.
	my $db_handle = &init();

	# Loop through the hash of possible network flags.
	foreach my $flag (keys(%network_flags)) {
		# Check if the address has the current flag.
		if (&Location::lookup_network_has_flag($db_handle, $address, $flag)) {
			# The given address has the requested flag.
			#
			# Grab the mapped location code for this flag.
			$mapped_code = $network_flags{$flag};

			# Return the code.
			return $mapped_code;
		}
	}
}

1;
