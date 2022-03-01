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

require '/var/ipfire/ipblocklist/sources';

# Location where the blocklists in ipset compatible format are stored.
our $blocklist_dir = "/var/lib/ipblocklist";

# File extension of the blocklist files.
our $blocklist_file_extension = ".conf";

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

1;
