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
my @proto = ();
my $CMD = "";
my $P2PSTRING = "";

my $DEBUG = 0;

my $configfile = "/var/ipfire/outgoing/rules";
my $p2pfile = "/var/ipfire/outgoing/p2protocols";

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

$netsettings{'RED_DEV'}=`cat /var/ipfire/red/iface`;

open( FILE, "< $configfile" ) or die "Unable to read $configfile";
@configs = <FILE>;
close FILE;

if ( $outfwsettings{'POLICY'} eq 'MODE1' ) {
	$outfwsettings{'STATE'} = "ALLOW";
	$POLICY = "DROP";
	$DO = "ACCEPT";
} elsif ( $outfwsettings{'POLICY'} eq 'MODE2' ) {
	$outfwsettings{'STATE'} = "DENY";
	$POLICY = "ACCEPT";
	$DO = "DROP -m comment --comment 'DROP_OUTGOINGFW'";
}

### Initialize IPTables
system("/sbin/iptables --flush OUTGOINGFW >/dev/null 2>&1");
system("/sbin/iptables --delete-chain OUTGOINGFW >/dev/null 2>&1");
system("/sbin/iptables -N OUTGOINGFW >/dev/null 2>&1");

if ( $outfwsettings{'POLICY'} eq 'MODE0' ) {
	exit 0
}

if ( $outfwsettings{'POLICY'} eq 'MODE1' ) {
	$CMD = "/sbin/iptables -A OUTGOINGFW -m state --state ESTABLISHED,RELATED -j ACCEPT";
	if ($DEBUG) { print "$CMD\n"; } else { system("$CMD"); }
		$CMD = "/sbin/iptables -A OUTGOINGFW -p icmp -j ACCEPT";
	if ($DEBUG) { print "$CMD\n"; } else { system("$CMD"); }
}

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
		
		if ($configline[3] eq 'tcp') {
			@proto = ("tcp");
		} elsif ($configline[3] eq 'udp') {
			@proto = ("udp");
		} else {
			@proto = ("tcp", "udp");
		}
		
		foreach $PROTO (@proto) {
			$CMD = "/sbin/iptables -A OUTGOINGFW -s $SOURCE -d $DESTINATION -p $PROTO";
	
			if ($configline[8]) {
				$DPORT = "$configline[8]";
				$CMD = "$CMD --dport $DPORT";
			}
			
			if ($DEV) {
				$CMD = "$CMD -i $DEV";
			}
	
			if ($configline[6]) {
				$MAC = "$configline[6]";
			 	$CMD = "$CMD -m mac --mac-source $MAC";
			}
			
			$CMD = "$CMD -o $netsettings{'RED_DEV'}";

			if ($configline[9] eq "aktiv") {
				if ($DEBUG) {
					print "$CMD -m limit --limit 10/minute -j LOG --log-prefix 'OUTGOINGFW '\n";
				} else {
					system("$CMD -m limit --limit 10/minute -j LOG --log-prefix 'OUTGOINGFW '");
				}
			}
			
			if ($DEBUG) {
				print "$CMD -j $DO\n";
			} else {
				system("$CMD -j $DO");
			}
    }
	}
}

### Do the P2P-Stuff here
open( FILE, "< $p2pfile" ) or die "Unable to read $p2pfile";
@p2ps = <FILE>;
close FILE;

$CMD = "/sbin/iptables -A OUTGOINGFW -m ipp2p";

foreach $p2pentry (sort @p2ps)
{
	@p2pline = split( /\;/, $p2pentry );
	if ( $outfwsettings{'POLICY'} eq 'MODE2' ) {
		$DO = "DROP";
		if ("$p2pline[2]" eq "off") {
			$P2PSTRING = "$P2PSTRING --$p2pline[1]";
		}
	} else {
		$DO = "ACCEPT";
		if ("$p2pline[2]" eq "on") {
			$P2PSTRING = "$P2PSTRING --$p2pline[1]";
		}
	}
}
if ($P2PSTRING) {
	if ($DEBUG) {
		print "$CMD $P2PSTRING -j $DO\n";
	} else {
		system("$CMD $P2PSTRING -j $DO");
	}
}

if ( $outfwsettings{'POLICY'} eq 'MODE1' ) {
	$CMD = "/sbin/iptables -A OUTGOINGFW -o $netsettings{'RED_DEV'} -j DROP -m comment --comment 'DROP_OUTGOINGFW'";
	if ($DEBUG) {
		print "$CMD\n";
	} else {
		system("$CMD");
	}
}
