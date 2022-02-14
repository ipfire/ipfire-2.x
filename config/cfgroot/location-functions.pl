#!/usr/bin/perl -w
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2021  IPFire Team  <info@ipfire.org>                     #
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

package Location::Functions;

use Location;

# Hash which contains country codes and their names which are special or not
# part of ISO 3166-1.
my %not_iso_3166_location = (
	"A1" => "Anonymous Proxy",
	"A2" => "Satellite Provider",
	"A3" => "Worldwide Anycast Instance",
	"XD" => "Hostile networks safe to drop",
);

# Hash which contains possible network flags and their mapped location codes.
my %network_flags = (
	"LOC_NETWORK_FLAG_ANONYMOUS_PROXY" => "A1",
	"LOC_NETWORK_FLAG_SATELLITE_PROVIDER" => "A2",
	"LOC_NETWORK_FLAG_ANYCAST" => "A3",
	"LOC_NETWORK_FLAG_DROP" => "XD",
);

# Array which contains special country codes.
my @special_locations = ( "A1", "A2", "A3", "XD" );

# Directory where the libloc database and keyfile lives.
our $location_dir = "/var/lib/location";

# Libloc database file.
our $database = "$location_dir/database.db";

# Libloc keyfile to verify the database.
our $keyfile = "$location_dir/signing-key.pem";

# Directory which contains the exported databases.
our $ipset_db_directory = "$location_dir/ipset";

# Create libloc database handle.
my $db_handle = &init();

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
## Function to get the country code of a given address.
#
sub lookup_country_code($$) {
	my ($address) = @_;

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
		# Get the country name by using the location module.
		$name = &Location::get_country_name($db_handle, $code);
	}

	return $name;
}

# Function to get all available locations.
sub get_locations() {
	my ($mode) = @_;

	# Set default mode to add_special_locations.
	$mode = $mode ? $mode : "add_special_locations";

	# Get locations which are stored in the location database.
	my @locations = &Location::database_countries($db_handle);

	# Check if the special locations should be added.
	if ($mode ne "no_special_locations") {
		# Merge special locations array and the database locations array.
		@locations = (@special_locations, @locations);
	}

	# Sort locations array in alphabetical order.
	my @sorted_locations = sort(@locations);

	# Return the array.
	return @sorted_locations;
}

# Function to get the continent code of a given country code.
sub get_continent_code($) {
	my ($country_code) = @_;

	# Use location module to grab the continent code.
	my $continent_code = &Location::get_continent_code($db_handle, $country_code);

	return $continent_code;
}

# Function to check if a given address has one ore more special flags.
sub address_has_flags($) {
	my ($address) = @_;

	# Array to store the flags of the address.
	my @flags;

	# Loop through the hash of possible network flags.
	foreach my $flag (keys(%network_flags)) {
		# Check if the address has the current flag.
		if (&Location::lookup_network_has_flag($db_handle, $address, $flag)) {
			# The given address has the requested flag.
			#
			# Grab the mapped location code for this flag.
			$mapped_code = $network_flags{$flag};

			# Add the mapped code to the array of flags.
			push(@flags, $mapped_code);
		}
	}

	# Sort the array of flags.
	@flags = sort(@flags);

	# Return the array of flags.
	return @flags;
}

#
## Function to get the Autonomous System Number of a given address.
#
sub lookup_asn($) {
	my ($address) = @_;

	# Lookup the given address.
	my $asn = &Location::lookup_asn($db_handle, $address);

	# Return the number of the Autonomous System
	return $asn;
}

#
## Function to get the name of an Autonomous System.
#
sub get_as_name($) {
	my ($asn) = @_;

	# Fetch the name of this AS...
	my $as_name = &Location::get_as_name($db_handle, $asn);

	# Return the name of the Autonomous System
	return $as_name;
}

# Custom END declaration which will be executed when perl
# ends, to release the database handle to libloc.
END {
	# Check if a database handle exists.
	if ($db_handle) {
		# Destroy libloc database handle.
		&Location::DESTROY($db_handle);
	}
}

1;
