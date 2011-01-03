#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2010  IPFire Team  <info@ipfire.org>                          #
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
# use warnings;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %qossettings = ();
my %checked = ();
my %netsettings = ();
my $message = "";
my $errormessage = "";
my $c = "";
my $direntry = "";
my $classentry = "";
my $subclassentry = "";
my $l7ruleentry = "";
my $portruleentry = "";
my $tosruleentry = "";
my @tmp = ();
my @classes = ();
my @subclasses = ();
my @l7rules = ();
my @portrules = ();
my @tosrules = ();
my @tmpline = ();
my @classline = ();
my @subclassline = ();
my @tosruleline = ();
my @l7ruleline = ();
my @portruleline = ();
my @proto = ();
my %selected= () ;
my $classfile = "/var/ipfire/qos/classes";
my $subclassfile = "/var/ipfire/qos/subclasses";
my $level7file = "/var/ipfire/qos/level7config";
my $portfile = "/var/ipfire/qos/portconfig";
my $tosfile = "/var/ipfire/qos/tosconfig";

&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

$qossettings{'ENABLED'} = 'off';
$qossettings{'EDIT'} = 'no';
$qossettings{'OUT_SPD'} = '';
$qossettings{'INC_SPD'} = '';
$qossettings{'DEF_OUT_SPD'} = '';
$qossettings{'DEF_INC_SPD'} = '';
$qossettings{'DEFCLASS_INC'} = '';
$qossettings{'DEFCLASS_OUT'} = '';
$qossettings{'ACK'} = '';
$qossettings{'MTU'} = '1492';
$qossettings{'RED_DEV'} = `cat /var/ipfire/red/iface`;
$qossettings{'IMQ_DEV'} = 'imq0';
$qossettings{'TOS'} = '';
$qossettings{'VALID'} = 'yes';
$qossettings{'IMQ_MODE'} = 'PREROUTING';

&General::readhash("${General::swroot}/qos/settings", \%qossettings);

open( FILE, "< $classfile" ) or die "Unable to read $classfile";
@classes = <FILE>;
close FILE;
open( FILE, "< $subclassfile" ) or die "Unable to read $subclassfile";
@subclasses = <FILE>;
close FILE;
open( FILE, "< $level7file" ) or die "Unable to read $level7file";
@l7rules = <FILE>;
close FILE;
open( FILE, "< $portfile" ) or die "Unable to read $portfile";
@portrules = <FILE>;
close FILE;
open( FILE, "< $tosfile" ) or die "Unable to read $tosfile";
@tosrules = <FILE>;
close FILE;

############################################################################################################################
############################################################################################################################

print <<END
#/bin/bash
#################################################
# This is an autocreated QoS-Script for         #
# IPFIRE                                        #
# Copyright by the IPFire Team (GPLv2)          #
# www.ipfire.org                                #
#################################################

### SYSTEMVARIABLES:
# RED INTERFACE: 	$qossettings{'RED_DEV'}
# IMQ DEVICE:		$qossettings{'IMQ_DEV'}

eval \$(/usr/local/bin/readhash /var/ipfire/main/settings)
if [ "\$RRDLOG" == "" ]; then
	RRDLOG=/var/log/rrd
fi

case "\$1" in

  status)
	case "\$2" in
	  qdisc)
		echo "[qdisc]"
		tc -s qdisc show dev $qossettings{'RED_DEV'}
		tc -s qdisc show dev $qossettings{'IMQ_DEV'}
		exit 0
	  ;;
	  class)
		echo "[class]"
		tc -s class show dev $qossettings{'RED_DEV'}
		tc -s class show dev $qossettings{'IMQ_DEV'}
		exit 0
	  ;;
	  filter)
		echo "[filter]"
		tc -s filter show dev $qossettings{'RED_DEV'}
		tc -s filter show dev $qossettings{'IMQ_DEV'}
		exit 0
	  ;;
	  iptables)
		echo "[iptables]"
		iptables -t mangle -n -L QOS-OUT -v -x 2> /dev/null
		iptables -t mangle -n -L QOS-INC -v -x 2> /dev/null
		iptables -t mangle -n -L QOS-TOS -v -x 2> /dev/null
		exit 0
	  ;;
	esac
	\$0 \$1 qdisc
	\$0 \$1 class
	\$0 \$1 filter
	\$0 \$1 iptables
	exit 0
  ;;
  start)
	###
	### $qossettings{'RED_DEV'}
	###

	### INIT KERNEL
	modprobe sch_htb

	### SET QUEUE LENGTH & MTU - has just to be tested!!! IMPORTANT
	ip link set dev $qossettings{'RED_DEV'} qlen $qossettings{'QLENGTH'}
	#ip link set dev $qossettings{'RED_DEV'} mtu $qossettings{'MTU'}

	### ADD HTB QDISC FOR $qossettings{'RED_DEV'}
	tc qdisc add dev $qossettings{'RED_DEV'} root handle 1: htb default $qossettings{'DEFCLASS_OUT'}

	### MAIN RATE LIMIT
	tc class add dev $qossettings{'RED_DEV'} parent 1: classid 1:1 htb rate $qossettings{'OUT_SPD'}kbit

	### CLASSES FOR $qossettings{'RED_DEV'}
END
;
foreach $classentry (sort @classes)
{
	@classline = split( /\;/, $classentry );
	if ($qossettings{'RED_DEV'} eq $classline[0]) {
		$qossettings{'DEVICE'} = $classline[0];
		$qossettings{'CLASS'} = $classline[1];
		$qossettings{'PRIO'} = $classline[2];
		$qossettings{'RATE'} = $classline[3];
		$qossettings{'CEIL'} = $classline[4];
		$qossettings{'BURST'} = $classline[5];
		$qossettings{'CBURST'} = $classline[6];
		print "\ttc class add dev $qossettings{'DEVICE'} parent 1:1 classid 1:$qossettings{'CLASS'} htb rate $qossettings{'RATE'}kbit ceil $qossettings{'CEIL'}kbit prio $qossettings{'PRIO'} ";
		if (($qossettings{'BURST'} ne '') && ($qossettings{'BURST'} ne 0)) {
			print "burst $qossettings{'BURST'}k ";
		}
		if (($qossettings{'CBURST'} ne '') && ($qossettings{'CBURST'} ne 0)) {
			print "cburst $qossettings{'CBURST'}k";
		}
		print "\n";
	}
}
foreach $subclassentry (sort @subclasses) {
	@subclassline = split( /\;/, $subclassentry );
	if ($qossettings{'RED_DEV'} eq $subclassline[0]) {
		$qossettings{'DEVICE'} = $subclassline[0];
		$qossettings{'CLASS'} = $subclassline[1];
		$qossettings{'SCLASS'} = $subclassline[2];
		$qossettings{'SPRIO'} = $subclassline[3];
		$qossettings{'SRATE'} = $subclassline[4];
		$qossettings{'SCEIL'} = $subclassline[5];
		$qossettings{'SBURST'} = $subclassline[6];
		$qossettings{'SCBURST'} = $subclassline[7];
		print "\ttc class add dev $qossettings{'DEVICE'} parent 1:$qossettings{'CLASS'} classid 1:$qossettings{'SCLASS'} htb rate $qossettings{'SRATE'}kbit ceil $qossettings{'SCEIL'}kbit prio $qossettings{'SPRIO'} ";
		if ($qossettings{'SBURST'} > 0) {
			print "burst $qossettings{'SBURST'}k ";
		}
		if (($qossettings{'SCBURST'} ne '') && ($qossettings{'SCBURST'} ne 0)) {
			print "cburst $qossettings{'CBURST'}k";
		}
		print "\n";
	}
}

print "\n\t### ATTACH QDISC TO LEAF CLASSES\n";
foreach $classentry (sort @classes)
{
	@classline = split( /\;/, $classentry );
	if ($qossettings{'RED_DEV'} eq $classline[0]) {
		$qossettings{'DEVICE'} = $classline[0];
		$qossettings{'CLASS'} = $classline[1];
		print "\ttc qdisc add dev $qossettings{'DEVICE'} parent 1:$qossettings{'CLASS'} handle $qossettings{'CLASS'}: sfq perturb $qossettings{'SFQ_PERTUB'}\n";
	}
}
foreach $subclassentry (sort @subclasses) {
	@subclassline = split( /\;/, $subclassentry );
	if ($qossettings{'RED_DEV'} eq $subclassline[0]) {
		$qossettings{'DEVICE'} = $subclassline[0];
		$qossettings{'SCLASS'} = $subclassline[2];
		print "\ttc qdisc add dev $qossettings{'DEVICE'} parent 1:$qossettings{'SCLASS'} handle $qossettings{'SCLASS'}: sfq perturb $qossettings{'SFQ_PERTUB'}\n";
	}
}
print "\n\t### FILTER TRAFFIC INTO CLASSES\n";
foreach $classentry (sort @classes)
{
	@classline = split( /\;/, $classentry );
	if ($qossettings{'RED_DEV'} eq $classline[0]) {
		$qossettings{'DEVICE'} = $classline[0];
		$qossettings{'CLASS'} = $classline[1];
		print "\ttc filter add dev $qossettings{'DEVICE'} parent 1:0 prio 0 protocol ip handle $qossettings{'CLASS'} fw flowid 1:$qossettings{'CLASS'}\n";
	}
}
foreach $subclassentry (sort @subclasses) {
	@subclassline = split( /\;/, $subclassentry );
	if ($qossettings{'RED_DEV'} eq $subclassline[0]) {
		$qossettings{'DEVICE'} = $subclassline[0];
		$qossettings{'CLASS'} = $subclassline[1];
		$qossettings{'SCLASS'} = $subclassline[2];
		print "\ttc filter add dev $qossettings{'DEVICE'} parent 1:0 prio 0 protocol ip handle $qossettings{'SCLASS'} fw flowid 1:$qossettings{'SCLASS'}\n";
	}
}
print <<END

	### add l7-filter to POSTROUTING chain to see all traffic
	iptables -t mangle -A POSTROUTING -m layer7 --l7proto unset

	### ADD QOS-OUT CHAIN TO THE MANGLE TABLE IN IPTABLES
	iptables -t mangle -N QOS-OUT
	iptables -t mangle -N QOS-TOS
	iptables -t mangle -I POSTROUTING -o $qossettings{'RED_DEV'} -j QOS-OUT
	iptables -t mangle -A POSTROUTING -o $qossettings{'RED_DEV'} -j QOS-TOS

	### Don't change mark on traffic for the ipsec tunnel
	iptables -t mangle -A QOS-OUT -m mark --mark 50 -j RETURN

	### MARK ACKs
	iptables -t mangle -A QOS-OUT -p tcp --tcp-flags SYN,RST SYN -j TOS --set-tos 4
	iptables -t mangle -A QOS-OUT -p tcp --tcp-flags SYN,RST SYN -j MARK --set-mark $qossettings{'ACK'}
	iptables -t mangle -A QOS-OUT -p tcp --tcp-flags SYN,RST SYN -j RETURN

	iptables -t mangle -A QOS-OUT -p icmp -m length --length 40:100 -j MARK --set-mark $qossettings{'ACK'}
	iptables -t mangle -A QOS-OUT -p icmp -m length --length 40:100 -j RETURN

	iptables -t mangle -A QOS-OUT -p tcp --syn -m length --length 40:68 -j TOS --set-tos 4
	iptables -t mangle -A QOS-OUT -p tcp --syn -m length --length 40:68 -j MARK --set-mark $qossettings{'ACK'}
	iptables -t mangle -A QOS-OUT -p tcp --syn -m length --length 40:68 -j RETURN

	iptables -t mangle -A QOS-OUT -p tcp --tcp-flags ALL SYN,ACK -m length --length 40:68 -j TOS --set-tos 4
	iptables -t mangle -A QOS-OUT -p tcp --tcp-flags ALL SYN,ACK -m length --length 40:68 -j MARK --set-mark $qossettings{'ACK'}
	iptables -t mangle -A QOS-OUT -p tcp --tcp-flags ALL SYN,ACK -m length --length 40:68 -j RETURN

	iptables -t mangle -A QOS-OUT -p tcp --tcp-flags ALL ACK -m length --length 40:100 -j TOS --set-tos 4
	iptables -t mangle -A QOS-OUT -p tcp --tcp-flags ALL ACK -m length --length 40:100 -j MARK --set-mark $qossettings{'ACK'}
	iptables -t mangle -A QOS-OUT -p tcp --tcp-flags ALL ACK -m length --length 40:100 -j RETURN

	iptables -t mangle -A QOS-OUT -p tcp --tcp-flags ALL RST -j TOS --set-tos 4
	iptables -t mangle -A QOS-OUT -p tcp --tcp-flags ALL RST -j MARK --set-mark $qossettings{'ACK'}
	iptables -t mangle -A QOS-OUT -p tcp --tcp-flags ALL RST -j RETURN

	iptables -t mangle -A QOS-OUT -p tcp --tcp-flags ALL ACK,RST -j TOS --set-tos 4
	iptables -t mangle -A QOS-OUT -p tcp --tcp-flags ALL ACK,RST -j MARK --set-mark $qossettings{'ACK'}
	iptables -t mangle -A QOS-OUT -p tcp --tcp-flags ALL ACK,RST -j RETURN

	iptables -t mangle -A QOS-OUT -p tcp --tcp-flags ALL ACK,FIN -j TOS --set-tos 4
	iptables -t mangle -A QOS-OUT -p tcp --tcp-flags ALL ACK,FIN -j MARK --set-mark $qossettings{'ACK'}
	iptables -t mangle -A QOS-OUT -p tcp --tcp-flags ALL ACK,FIN -j RETURN

	### SET TOS
END
;
  	foreach $tosruleentry (sort @tosrules)
  	{
  		@tosruleline = split( /\;/, $tosruleentry );
		$qossettings{'CLASS'} = $tosruleline[0];
		$qossettings{'TOS'} = abs $tosruleline[2] * 2;
  		if ( $tosruleline[1] eq $qossettings{'RED_DEV'} )
  		{
			print "\tiptables -t mangle -A QOS-OUT -m tos --tos $qossettings{'TOS'} -j MARK --set-mark $qossettings{'CLASS'}\n";
			print "\tiptables -t mangle -A QOS-OUT -m tos --tos $qossettings{'TOS'} -j RETURN\n";
		}
	}

print "\n\t### SET PORT-RULES\n";
  	foreach $portruleentry (sort @portrules)
  	{
  		@portruleline = split( /\;/, $portruleentry );
  		if ( $portruleline[1] eq $qossettings{'RED_DEV'} )
  		{
			$qossettings{'CLASS'} = $portruleline[0];
			$qossettings{'DEVICE'} = $portruleline[1];
			$qossettings{'PPROT'} = $portruleline[2];
			$qossettings{'QIP'} = $portruleline[3];
			$qossettings{'QPORT'} = $portruleline[4];
			$qossettings{'DIP'} = $portruleline[5];
			$qossettings{'DPORT'} = $portruleline[6];
			print "\tiptables -t mangle -A QOS-OUT ";
			if ($qossettings{'QIP'} ne ''){
				print "-s $qossettings{'QIP'} ";
			}
			if ($qossettings{'DIP'} ne ''){
				print "-d $qossettings{'DIP'} ";
			}
			print "-p $qossettings{'PPROT'} ";
#			if (($qossettings{'QPORT'} ne '') || ($qossettings{'DPORT'} ne '')){
#				print "-m multiport ";
#			}
			if ($qossettings{'QPORT'} ne ''){
				print "--sport $qossettings{'QPORT'} ";
			}
			if ($qossettings{'DPORT'} ne ''){
				print "--dport $qossettings{'DPORT'} ";
			}
			print "-j MARK --set-mark $qossettings{'CLASS'}\n";
			print "\tiptables -t mangle -A QOS-OUT ";
			if ($qossettings{'QIP'} ne ''){
				print "-s $qossettings{'QIP'} ";
			}
			if ($qossettings{'DIP'} ne ''){
				print "-d $qossettings{'DIP'} ";
			}
			print "-p $qossettings{'PPROT'} ";
#			if (($qossettings{'QPORT'} ne '') || ($qossettings{'DPORT'} ne '')){
#				print "-m multiport ";
#			}
			if ($qossettings{'QPORT'} ne ''){
				print "--sport $qossettings{'QPORT'} ";
			}
			if ($qossettings{'DPORT'} ne ''){
				print "--dport $qossettings{'DPORT'} ";
			}
			print "-j RETURN\n\n";
		}
	}

print <<END

	### SET LEVEL7-RULES
END
;
  	foreach $l7ruleentry (sort @l7rules)
  	{
  		@l7ruleline = split( /\;/, $l7ruleentry );
  		if ( $l7ruleline[1] eq $qossettings{'RED_DEV'} )
  		{
			$qossettings{'CLASS'} = $l7ruleline[0];
			$qossettings{'DEVICE'} = $l7ruleline[1];
			$qossettings{'L7PROT'} = $l7ruleline[2];
			$qossettings{'QIP'} = $l7ruleline[3];
			$qossettings{'DIP'} = $l7ruleline[4];
  			print "\tiptables -t mangle -A QOS-OUT ";
			if ($qossettings{'QIP'} ne ''){
				print "-s $qossettings{'QIP'} ";
			}
			if ($qossettings{'DIP'} ne ''){
				print "-d $qossettings{'DIP'} ";
			}
			print "-m layer7 --l7dir /etc/l7-protocols/protocols --l7proto $qossettings{'L7PROT'} -j MARK --set-mark $qossettings{'CLASS'}\n";
  			print "\tiptables -t mangle -A QOS-OUT ";
			if ($qossettings{'QIP'} ne ''){
				print "-s $qossettings{'QIP'} ";
			}
			if ($qossettings{'DIP'} ne ''){
				print "-d $qossettings{'DIP'} ";
			}
			print "-m layer7 --l7dir /etc/l7-protocols/protocols --l7proto $qossettings{'L7PROT'} -j RETURN\n";
  		}
  	}

print <<END

	### REDUNDANT: SET ALL NONMARKED PACKETS TO DEFAULT CLASS
	iptables -t mangle -A QOS-OUT -m mark --mark 0 -j MARK --set-mark $qossettings{'DEFCLASS_OUT'}

	###
	### $qossettings{'IMQ_DEV'}
	###

	### BRING UP $qossettings{'IMQ_DEV'}
	if [ `lsmod | grep -q ipt_IMQ` ]; then
		insmod ipt_IMQ
		sleep 2
	fi
	modprobe imq numdevs=1
	ip link set $qossettings{'IMQ_DEV'} up

	### SET QUEUE LENGTH & MTU - has just to be tested!!! IMPORTANT
	ip link set dev $qossettings{'IMQ_DEV'} qlen $qossettings{'QLENGTH'}
	# ip link set dev $qossettings{'IMQ_DEV'} mtu $qossettings{'MTU'}

	### ADD HTB QDISC FOR $qossettings{'IMQ_DEV'}
	tc qdisc add dev $qossettings{'IMQ_DEV'} root handle 2: htb default $qossettings{'DEFCLASS_INC'}

	### MAIN RATE LIMIT
	tc class add dev $qossettings{'IMQ_DEV'} parent 2: classid 2:1 htb rate $qossettings{'INC_SPD'}kbit

	### CLASSES FOR $qossettings{'IMQ_DEV'}
END
;
foreach $classentry (sort @classes)
{
	@classline = split( /\;/, $classentry );
	if ($qossettings{'IMQ_DEV'} eq $classline[0]) {
		$qossettings{'DEVICE'} = $classline[0];
		$qossettings{'CLASS'} = $classline[1];
		$qossettings{'PRIO'} = $classline[2];
		$qossettings{'RATE'} = $classline[3];
		$qossettings{'CEIL'} = $classline[4];
		$qossettings{'BURST'} = $classline[5];
		$qossettings{'CBURST'} = $classline[6];
		print "\ttc class add dev $qossettings{'DEVICE'} parent 2:1 classid 2:$qossettings{'CLASS'} htb rate $qossettings{'RATE'}kbit ceil $qossettings{'CEIL'}kbit prio $qossettings{'PRIO'} ";
		if (($qossettings{'BURST'} ne '') && ($qossettings{'BURST'} ne 0)) {
			print "burst $qossettings{'BURST'}k ";
		}
		if (($qossettings{'CBURST'} ne '') && ($qossettings{'CBURST'} ne 0)) {
			print "cburst $qossettings{'CBURST'}k";
		}
		print "\n";
	}
}
foreach $subclassentry (sort @subclasses) {
	@subclassline = split( /\;/, $subclassentry );
	if ($qossettings{'IMQ_DEV'} eq $subclassline[0]) {
		$qossettings{'DEVICE'} = $subclassline[0];
		$qossettings{'CLASS'} = $subclassline[1];
		$qossettings{'SCLASS'} = $subclassline[2];
		$qossettings{'SPRIO'} = $subclassline[3];
		$qossettings{'SRATE'} = $subclassline[4];
		$qossettings{'SCEIL'} = $subclassline[5];
		$qossettings{'SBURST'} = $subclassline[6];
		$qossettings{'SCBURST'} = $subclassline[7];
		print "\ttc class add dev $qossettings{'DEVICE'} parent 2:$qossettings{'CLASS'} classid 2:$qossettings{'SCLASS'} htb rate $qossettings{'SRATE'}kbit ceil $qossettings{'SCEIL'}kbit prio $qossettings{'SPRIO'} ";
		if ($qossettings{'SBURST'} > 0) {
			print "burst $qossettings{'SBURST'}k ";
		}
		if (($qossettings{'SCBURST'} ne '') && ($qossettings{'SCBURST'} ne 0)) {
			print "cburst $qossettings{'CBURST'}k";
		}
		print "\n";
	}
}

print "\n\t### ATTACH QDISC TO LEAF CLASSES\n";
foreach $classentry (sort @classes)
{
	@classline = split( /\;/, $classentry );
	if ($qossettings{'IMQ_DEV'} eq $classline[0]) {
		$qossettings{'DEVICE'} = $classline[0];
		$qossettings{'CLASS'} = $classline[1];
		print "\ttc qdisc add dev $qossettings{'DEVICE'} parent 2:$qossettings{'CLASS'} handle $qossettings{'CLASS'}: sfq perturb $qossettings{'SFQ_PERTUB'}\n";
	}
}
foreach $subclassentry (sort @subclasses) {
	@subclassline = split( /\;/, $subclassentry );
	if ($qossettings{'IMQ_DEV'} eq $subclassline[0]) {
		$qossettings{'DEVICE'} = $subclassline[0];
		$qossettings{'SCLASS'} = $subclassline[2];
		print "\ttc qdisc add dev $qossettings{'DEVICE'} parent 2:$qossettings{'SCLASS'} handle $qossettings{'SCLASS'}: sfq perturb $qossettings{'SFQ_PERTUB'}\n";
	}
}
print "\n\t### FILTER TRAFFIC INTO CLASSES\n";
foreach $classentry (sort @classes)
{
	@classline = split( /\;/, $classentry );
	if ($qossettings{'IMQ_DEV'} eq $classline[0]) {
		$qossettings{'DEVICE'} = $classline[0];
		$qossettings{'CLASS'} = $classline[1];
		print "\ttc filter add dev $qossettings{'DEVICE'} parent 2:0 prio 0 protocol ip handle $qossettings{'CLASS'} fw flowid 2:$qossettings{'CLASS'}\n";
	}
}
foreach $subclassentry (sort @subclasses) {
	@subclassline = split( /\;/, $subclassentry );
	if ($qossettings{'IMQ_DEV'} eq $subclassline[0]) {
		$qossettings{'DEVICE'} = $subclassline[0];
		$qossettings{'CLASS'} = $subclassline[1];
		$qossettings{'SCLASS'} = $subclassline[2];
		print "\ttc filter add dev $qossettings{'DEVICE'} parent 2:0 prio 0 protocol ip handle $qossettings{'SCLASS'} fw flowid 2:$qossettings{'SCLASS'}\n";
	}
}

if ( $qossettings{'IMQ_MODE'} eq 'POSTROUTING' )
{
print <<END

	### ADD QOS-INC CHAIN TO THE MANGLE TABLE IN IPTABLES
	iptables -t mangle -N QOS-INC
	iptables -t mangle -A POSTROUTING -i $qossettings{'RED_DEV'} -p ah -j RETURN
	iptables -t mangle -A POSTROUTING -i $qossettings{'RED_DEV'} -p esp -j RETURN
	iptables -t mangle -A POSTROUTING -i $qossettings{'RED_DEV'} -p ip -j RETURN
	iptables -t mangle -A POSTROUTING -m mark ! --mark 0 ! -o $qossettings{'RED_DEV'} -j IMQ --todev 0
	iptables -t mangle -I FORWARD -i $qossettings{'RED_DEV'} -j QOS-INC
	iptables -t mangle -A FORWARD -i $qossettings{'RED_DEV'} -j QOS-TOS

	### SET TOS
END
;
}
else
{
print <<END

	### ADD QOS-INC CHAIN TO THE MANGLE TABLE IN IPTABLES
	iptables -t mangle -N QOS-INC
	iptables -t mangle -A PREROUTING -i $qossettings{'RED_DEV'} -p ah -j RETURN
	iptables -t mangle -A PREROUTING -i $qossettings{'RED_DEV'} -p esp -j RETURN
	iptables -t mangle -A PREROUTING -i $qossettings{'RED_DEV'} -p ip -j RETURN
	iptables -t mangle -A PREROUTING -i $qossettings{'RED_DEV'} -j IMQ --todev 0
	iptables -t mangle -I PREROUTING -i $qossettings{'RED_DEV'} -j QOS-INC
	iptables -t mangle -A PREROUTING -i $qossettings{'RED_DEV'} -j QOS-TOS

	### SET TOS
END
;
}

  	foreach $tosruleentry (sort @tosrules)
  	{
  		@tosruleline = split( /\;/, $tosruleentry );
		$qossettings{'CLASS'} = $tosruleline[0];
		$qossettings{'TOS'} = abs $tosruleline[2] * 2;
  		if ( $tosruleline[1] eq $qossettings{'IMQ_DEV'} )
  		{
			print "\tiptables -t mangle -A QOS-INC -m tos --tos $qossettings{'TOS'} -j MARK --set-mark $qossettings{'CLASS'}\n";
			print "\tiptables -t mangle -A QOS-INC -m tos --tos $qossettings{'TOS'} -j RETURN\n";
		}

	}

print "\n\t### SET PORT-RULES\n";
  	foreach $portruleentry (sort @portrules)
  	{
  		@portruleline = split( /\;/, $portruleentry );
  		if ( $portruleline[1] eq $qossettings{'IMQ_DEV'} )
  		{
			$qossettings{'CLASS'} = $portruleline[0];
			$qossettings{'DEVICE'} = $portruleline[1];
			$qossettings{'PPROT'} = $portruleline[2];
			$qossettings{'QIP'} = $portruleline[3];
			$qossettings{'QPORT'} = $portruleline[4];
			$qossettings{'DIP'} = $portruleline[5];
			$qossettings{'DPORT'} = $portruleline[6];
			print "\tiptables -t mangle -A QOS-INC ";
			if ($qossettings{'QIP'} ne ''){
				print "-s $qossettings{'QIP'} ";
			}
			if ($qossettings{'DIP'} ne ''){
				print "-d $qossettings{'DIP'} ";
			}
			print "-p $qossettings{'PPROT'} ";
#			if (($qossettings{'QPORT'} ne '') || ($qossettings{'DPORT'} ne '')){
#				print "-m multiport ";
#			}
			if ($qossettings{'QPORT'} ne ''){
				print "--sport $qossettings{'QPORT'} ";
			}
			if ($qossettings{'DPORT'} ne ''){
				print "--dport $qossettings{'DPORT'} ";
			}
			print "-j MARK --set-mark $qossettings{'CLASS'}\n";
			print "\tiptables -t mangle -A QOS-INC ";
			if ($qossettings{'QIP'} ne ''){
				print "-s $qossettings{'QIP'} ";
			}
			if ($qossettings{'DIP'} ne ''){
				print "-d $qossettings{'DIP'} ";
			}
			print "-p $qossettings{'PPROT'} ";
#			if (($qossettings{'QPORT'} ne '') || ($qossettings{'DPORT'} ne '')){
#				print "-m multiport ";
#			}
			if ($qossettings{'QPORT'} ne ''){
				print "--sport $qossettings{'QPORT'} ";
			}
			if ($qossettings{'DPORT'} ne ''){
				print "--dport $qossettings{'DPORT'} ";
			}
			print "-j RETURN\n\n";
		}
	}

print <<END

	### SET LEVEL7-RULES
END
;
  	foreach $l7ruleentry (sort @l7rules)
  	{
  		@l7ruleline = split( /\;/, $l7ruleentry );
  		if ( $l7ruleline[1] eq $qossettings{'IMQ_DEV'} )
  		{
			$qossettings{'CLASS'} = $l7ruleline[0];
			$qossettings{'DEVICE'} = $l7ruleline[1];
			$qossettings{'L7PROT'} = $l7ruleline[2];
			$qossettings{'QIP'} = $l7ruleline[3];
			$qossettings{'DIP'} = $l7ruleline[4];
  			print "\tiptables -t mangle -A QOS-INC ";
			if ($qossettings{'QIP'} ne ''){
				print "-s $qossettings{'QIP'} ";
			}
			if ($qossettings{'DIP'} ne ''){
				print "-d $qossettings{'DIP'} ";
			}
			print "-m layer7 --l7dir /etc/l7-protocols/protocols --l7proto $qossettings{'L7PROT'} -j MARK --set-mark $qossettings{'CLASS'}\n";
  			print "\tiptables -t mangle -A QOS-INC ";
			if ($qossettings{'QIP'} ne ''){
				print "-s $qossettings{'QIP'} ";
			}
			if ($qossettings{'DIP'} ne ''){
				print "-d $qossettings{'DIP'} ";
			}
			print "-m layer7 --l7dir /etc/l7-protocols/protocols --l7proto $qossettings{'L7PROT'} -j RETURN\n";
  		}
  	}

print <<END
	### REDUNDANT: SET ALL NONMARKED PACKETS TO DEFAULT CLASS
	iptables -t mangle -A QOS-INC -m mark --mark 0 -j MARK --set-mark $qossettings{'DEFCLASS_INC'}

	### SETTING TOS BITS
END
;
	foreach $classentry (sort @classes)
	{
		@classline = split( /\;/, $classentry );
		$qossettings{'CLASS'} = $classline[1];
		$qossettings{'TOS'} = abs $classline[7] * 2;
		if ($qossettings{'TOS'} ne "0") {
			print "\tiptables -t mangle -A QOS-TOS -m mark --mark $qossettings{'CLASS'} -j TOS --set-tos $qossettings{'TOS'}\n";
			print "\tiptables -t mangle -A QOS-TOS -m mark --mark $qossettings{'CLASS'} -j RETURN\n";
		}
	}
	foreach $subclassentry (sort @subclasses)
	{
		@subclassline = split( /\;/, $subclassentry );
		$qossettings{'SUBCLASS'} = $subclassline[1];
		$qossettings{'TOS'} = $subclassline[8];
		$qossettings{'TOS'} = abs $qossettings{'TOS'} * 2;
		if ($qossettings{'TOS'} ne "0") {
			print "\tiptables -t mangle -A QOS-TOS -m mark --mark $qossettings{'SUBCLASS'} -j TOS --set-tos $qossettings{'TOS'}\n";
			print "\tiptables -t mangle -A QOS-TOS -m mark --mark $qossettings{'SUBCLASS'} -j RETURN\n";
		}
	}

print <<END

	## STARTING COLLECTOR
	( sleep 10 && /usr/local/bin/qosd $qossettings{'RED_DEV'} >/dev/null 2>&1) &
	( sleep 10 && /usr/local/bin/qosd $qossettings{'IMQ_DEV'} >/dev/null 2>&1) &

	for i in \$(ls \$RRDLOG/class_*.rrd); do
		rrdtool update \$i \$(date +%s):
	done

	echo "Quality of Service was successfully started!"
	exit 0
  ;;
  clear|stop)
	### RESET EVERYTHING TO A KNOWN STATE
	killall qosd >/dev/null 2>&1
	(sleep 3 && killall -9 qosd &>/dev/null) &
	# DELETE QDISCS
	tc qdisc del dev $qossettings{'RED_DEV'} root >/dev/null 2>&1
	tc qdisc del dev $qossettings{'IMQ_DEV'} root >/dev/null 2>&1
	# STOP IMQ-DEVICE
	ip link set $qossettings{'IMQ_DEV'} down >/dev/null 2>&1
	iptables -t mangle --delete POSTROUTING -i $qossettings{'RED_DEV'} -p ah -j RETURN >/dev/null 2>&1
	iptables -t mangle --delete POSTROUTING -i $qossettings{'RED_DEV'} -p esp -j RETURN >/dev/null 2>&1
	iptables -t mangle --delete POSTROUTING -i $qossettings{'RED_DEV'} -p ip -j RETURN >/dev/null 2>&1
	iptables -t mangle --delete PREROUTING -i $qossettings{'RED_DEV'} -p ah -j RETURN >/dev/null 2>&1
	iptables -t mangle --delete PREROUTING -i $qossettings{'RED_DEV'} -p esp -j RETURN >/dev/null 2>&1
	iptables -t mangle --delete PREROUTING -i $qossettings{'RED_DEV'} -p ip -j RETURN >/dev/null 2>&1
	iptables -t mangle --delete POSTROUTING -m mark ! --mark 0 ! -o $qossettings{'RED_DEV'} -j IMQ --todev 0 >/dev/null 2>&1
	iptables -t mangle --delete PREROUTING -i $qossettings{'RED_DEV'} -j IMQ --todev 0  >/dev/null 2>&1
	# rmmod imq # this crash on 2.6.25.xx
	# REMOVE & FLUSH CHAINS
	iptables -t mangle --delete POSTROUTING -o $qossettings{'RED_DEV'} -j QOS-OUT >/dev/null 2>&1
	iptables -t mangle --delete POSTROUTING -o $qossettings{'RED_DEV'} -j QOS-TOS >/dev/null 2>&1
	iptables -t mangle --flush  QOS-OUT >/dev/null 2>&1
	iptables -t mangle --delete-chain QOS-OUT >/dev/null 2>&1
	iptables -t mangle --delete FORWARD -i $qossettings{'RED_DEV'} -j QOS-INC >/dev/null 2>&1
	iptables -t mangle --delete FORWARD -i $qossettings{'RED_DEV'} -j QOS-TOS >/dev/null 2>&1
	iptables -t mangle --delete PREROUTING -i $qossettings{'RED_DEV'} -j QOS-INC >/dev/null 2>&1
	iptables -t mangle --delete PREROUTING -i $qossettings{'RED_DEV'} -j QOS-TOS >/dev/null 2>&1
	iptables -t mangle --flush  QOS-INC >/dev/null 2>&1
	iptables -t mangle --delete-chain QOS-INC >/dev/null 2>&1
	iptables -t mangle --flush  QOS-TOS >/dev/null 2>&1
	iptables -t mangle --delete-chain QOS-TOS >/dev/null 2>&1
	# remove l7-filter
	iptables -t mangle --delete POSTROUTING -m layer7 --l7proto unset

	rmmod sch_htb >/dev/null 2>&1

	for i in \$(ls \$RRDLOG/class_*.rrd); do
		rrdtool update \$i \$(date +%s):
	done

	echo "Quality of Service was successfully cleared!"
  ;;
  gen|generate)
	echo -n "Generateing the QoS-Scripts..."
	/usr/bin/perl /var/ipfire/qos/bin/makeqosscripts.pl > /var/ipfire/qos/bin/qos.sh
	echo ".Done!"
	exit 0
	;;
  restart)
	### FIRST CLEAR EVERYTHING
	\$0 clear

	### THEN START
	\$0 start
	;;
esac
### EOF
END
;

############################################################################################################################
############################################################################################################################
