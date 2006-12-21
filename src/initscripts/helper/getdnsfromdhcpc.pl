#!/usr/bin/perl
#
# Helper program to get DNS info from dhcpc .info file.
#
# (c) Lawrence Manning, 2001

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


$dns = $dhcpc{'DNS'};

@alldns = split(',', $dns);

print "$alldns[$count - 1]\n";
