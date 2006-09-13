#!/usr/bin/perl
#
# IPFire Scripts
#
# This code is distributed under the terms of the GPL
#
# (c) The IPFire Team
#

use strict;
# enable only the following on debugging purpose
#use warnings;

require '/var/ipfire/general-functions.pl';

my %outfwsettings = ();
my %checked = ();
my %selected= () ;
my %netsettings = ();
my $errormessage = "";
my $configentry = "";
my @configs = ();
my @configline = ();
my $p2pentry = "";
my @p2ps = ();
my @p2pline = ();
my @protos = ();
my $CMD = "";
my $DEBUG = 0;

my $configfile = "/var/ipfire/outgoing/rules";
my $p2pfile = "/var/ipfire/outgoing/p2protocols";

&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

### Values that have to be initialized
$outfwsettings{'ACTION'} = '';
$outfwsettings{'VALID'} = 'yes';
$outfwsettings{'EDIT'} = 'no';
$outfwsettings{'NAME'} = '';
$outfwsettings{'SNET'} = '';
$outfwsettings{'SIP'} = '';
$outfwsettings{'SPORT'} = '';
$outfwsettings{'SMAC'} = '';
$outfwsettings{'DIP'} = '';
$outfwsettings{'DPORT'} = '';
$outfwsettings{'PROT'} = '';
$outfwsettings{'STATE'} = '';
$outfwsettings{'DISPLAY_DIP'} = '';
$outfwsettings{'DISPLAY_DPORT'} = '';
$outfwsettings{'DISPLAY_SMAC'} = '';
$outfwsettings{'DISPLAY_SIP'} = '';
$outfwsettings{'POLICY'} = 'MODE0';
my $SOURCE = "";
my $DESTINATION = "";
my $PROTO = "";
my $DPORT = "";
my $DEV = "";
my $MAC = "";
my $POLICY = "";
my $DO = "";

# read files
&General::readhash("${General::swroot}/outgoing/settings", \%outfwsettings);
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

open( FILE, "< $configfile" ) or die "Unable to read $configfile";
@configs = <FILE>;
close FILE;

# Say hello!
print "Outgoing firewall for IPFire - $outfwsettings{'POLICY'}\n";
if ($DEBUG) { print "Debugging mode!\n"; }
print "\n";


if ( $outfwsettings{'POLICY'} eq 'MODE0' ) {
	system("/sbin/iptables --flush OUTGOINGFW >/dev/null 2>&1");
	system("/sbin/iptables --delete-chain OUTGOINGFW >/dev/null 2>&1");

	exit 0
} elsif ( $outfwsettings{'POLICY'} eq 'MODE1' ) {
	$outfwsettings{'STATE'} = "ALLOW";
	$POLICY = "DROP";
	$DO = "ACCEPT";
} elsif ( $outfwsettings{'POLICY'} eq 'MODE2' ) {
	$outfwsettings{'STATE'} = "DENY";
	$POLICY = "ACCEPT";
	$DO = "DROP";
}

### Initialize IPTables
system("/sbin/iptables --flush OUTGOINGFW >/dev/null 2>&1");
system("/sbin/iptables --delete-chain OUTGOINGFW >/dev/null 2>&1");
system("/sbin/iptables -N OUTGOINGFW >/dev/null 2>&1");

foreach $configentry (sort @configs)
{
	$SOURCE = "";
	$DESTINATION = "";
	$PROTO = "";
	$DPORT = "";
	$DEV = "";
	$MAC = "";
	@configline = split( /\;/, $configentry );
	if ($outfwsettings{'STATE'} eq $configline[0]) {
		if ($configline[2] eq 'green') {
			$SOURCE = "$netsettings{'GREEN_NETADDRESS'}/$netsettings{'GREEN_NETMASK'}";
			$DEV = $netsettings{'GREEN_DEV'};
		} elsif ($configline[2] eq 'blue') {
			$SOURCE = "$netsettings{'BLUE_NETADDRESS'}/$netsettings{'BLUE_NETMASK'}";
			$DEV = $netsettings{'BLUE_DEV'};
		} elsif ($configline[2] eq 'orange') {
			$SOURCE = "$netsettings{'ORANGE_NETADDRESS'}/$netsettings{'ORANGE_NETMASK'}";
			$DEV = $netsettings{'ORANGE_DEV'};
		} elsif ($configline[2] eq 'ip') {
			$SOURCE = "$configline[5]";
			$DEV = "";
		} else  {
			$SOURCE = "0/0";
			$DEV = "";
		}

		if ($configline[7]) { $DESTINATION = "$configline[7]"; } else { $DESTINATION = "0/0"; }

		$CMD = "/sbin/iptables -A OUTGOINGFW -s $SOURCE -d $DESTINATION";

		if ($configline[3] ne 'tcp&udp') {
			$PROTO = "$configline[3]";
			$CMD = "$CMD -p $PROTO";
			if ($configline[8]) {
				$DPORT = "$configline[8]";
				$CMD = "$CMD --dport $DPORT";
			}
		}

		if ($DEV) {
			$CMD = "$CMD -i $DEV";
		}

		if ($configline[6]) {
			$MAC = "$configline[6]";
		 	$CMD = "$CMD -m mac --mac-source $MAC";
		}

		$CMD = "$CMD -o $netsettings{'RED_DEV'}";
		if ($DEBUG) { print "$CMD -j $DO\n"; } else { system("$CMD -j $DO"); }

		if ($configline[9] eq "log") {
			if ($DEBUG) { print "$CMD -m state --state NEW -j LOG --log-prefix 'OUTGOINGFW '\n"; } else { system("$CMD -m state --state NEW -j LOG --log-prefix 'OUTGOINGFW '"); }
		}

	}
}
