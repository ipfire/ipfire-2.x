#!/usr/bin/perl
#
# Helper program to write a new IPAC settings file
#
# (c) Lawrence Manning, 2001
#
# $id
#

use strict;
require 'CONFIG_ROOT/general-functions.pl';

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

if ($settings{'CONFIG_TYPE'} =~ /^(1|3|5|7)$/ )
{
        print FILE "incoming ORANGE ($settings{'ORANGE_DEV'})|ipac~o|$settings{'ORANGE_DEV'}|all|||\n";
        print FILE "outgoing ORANGE ($settings{'ORANGE_DEV'})|ipac~i|$settings{'ORANGE_DEV'}|all|||\n";
        print FILE "forwarded incoming ORANGE ($settings{'ORANGE_DEV'})|ipac~fi|$settings{'ORANGE_DEV'}|all|||\n";
        print FILE "forwarded outgoing ORANGE ($settings{'ORANGE_DEV'})|ipac~fo|$settings{'ORANGE_DEV'}|all|||\n";
}

if ($settings{'CONFIG_TYPE'} =~ /^(4|5|6|7)$/ )
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
