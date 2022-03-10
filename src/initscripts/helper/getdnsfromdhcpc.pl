#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2022  IPFire Team  <info@ipfire.org>                     #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
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

use strict;
require '/var/ipfire/general-functions.pl';

my $count = $ARGV[0];
my ($dhcp, $dns, @alldns, %dhcpc);

if ($count eq "" || $count < 1) {
	die "Bad DNS number given"; }

if (open(FILE, "${General::swroot}/red/iface")) {
	my $iface = <FILE>;
	close FILE;
	chomp ($iface);
	if (!&General::readhash("${General::swroot}/dhcpc/dhcpcd-$iface.info", \%dhcpc)) {
		die "Could not open dhcpc info file";
	}
} else {
	die "Could not open interface file";
}


$dns = $dhcpc{'domain_name_servers'};

@alldns = split(' ', $dns);

print "$alldns[$count - 1]\n";
