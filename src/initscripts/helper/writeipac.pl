#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007  Michael Tremer & Christian Schmidt                      #
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

my %settings;
my $iface;

General::readhash("${General::swroot}/ethernet/settings", \%settings);

if (!open(FILE, '>/etc/ipac-ng/rules.conf')) {
	die "Unable to create /etc/ipac-ng/rules.conf"; }

if (open(IFACE, "${General::swroot}/red/iface"))
{
	$iface = <IFACE>;
	close IFACE;
	chomp ($iface);
}

print FILE "incoming GREEN ($settings{'GREEN_DEV'})|ipac~o|$settings{'GREEN_DEV'}|all|||\n";
print FILE "outgoing GREEN ($settings{'GREEN_DEV'})|ipac~i|$settings{'GREEN_DEV'}|all|||\n";
print FILE "forwarded incoming GREEN ($settings{'GREEN_DEV'})|ipac~fi|$settings{'GREEN_DEV'}|all|||\n";
print FILE "forwarded outgoing GREEN ($settings{'GREEN_DEV'})|ipac~fo|$settings{'GREEN_DEV'}|all|||\n";

if ($settings{'CONFIG_TYPE'} =~ /^(2|4)$/ )
{
        print FILE "incoming ORANGE ($settings{'ORANGE_DEV'})|ipac~o|$settings{'ORANGE_DEV'}|all|||\n";
        print FILE "outgoing ORANGE ($settings{'ORANGE_DEV'})|ipac~i|$settings{'ORANGE_DEV'}|all|||\n";
        print FILE "forwarded incoming ORANGE ($settings{'ORANGE_DEV'})|ipac~fi|$settings{'ORANGE_DEV'}|all|||\n";
        print FILE "forwarded outgoing ORANGE ($settings{'ORANGE_DEV'})|ipac~fo|$settings{'ORANGE_DEV'}|all|||\n";
}

if ($settings{'CONFIG_TYPE'} =~ /^(3|4)$/ )
{
        print FILE "incoming BLUE ($settings{'BLUE_DEV'})|ipac~o|$settings{'BLUE_DEV'}|all|||\n";
        print FILE "outgoing BLUE ($settings{'BLUE_DEV'})|ipac~i|$settings{'BLUE_DEV'}|all|||\n";
        print FILE "forwarded incoming BLUE ($settings{'BLUE_DEV'})|ipac~fi|$settings{'BLUE_DEV'}|all|||\n";
        print FILE "forwarded outgoing BLUE ($settings{'BLUE_DEV'})|ipac~fo|$settings{'BLUE_DEV'}|all|||\n";
}
if ($iface) {
	print FILE "incoming RED ($iface)|ipac~o|$iface|all|||\n";
	print FILE "outgoing RED ($iface)|ipac~i|$iface|all|||\n";
	print FILE "forwarded incoming RED ($iface)|ipac~fi|$iface|all|||\n";
	print FILE "forwarded outgoing RED ($iface)|ipac~fo|$iface|all|||\n";
}

close FILE;
