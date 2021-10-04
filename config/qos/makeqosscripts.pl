#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2013  IPFire Team  <info@ipfire.org>                     #
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
my $l7ruleentry = "";
my $portruleentry = "";
my $tosruleentry = "";
my @tmp = ();
my @classes = ();
my @l7rules = ();
my @portrules = ();
my @tosrules = ();
my @tmpline = ();
my @classline = ();
my @tosruleline = ();
my @l7ruleline = ();
my @portruleline = ();
my @proto = ();
my %selected= () ;
my $classfile = "/var/ipfire/qos/classes";
my $level7file = "/var/ipfire/qos/level7config";
my $portfile = "/var/ipfire/qos/portconfig";
my $tosfile = "/var/ipfire/qos/tosconfig";
my $fqcodel_options = "limit 10240 quantum 1514";

# Define iptables MARKs
my $QOS_INC_MASK = 0x0000ff00;
my $QOS_INC_SHIFT = 8;
my $QOS_OUT_MASK = 0x000000ff;
my $QOS_OUT_SHIFT = 0;

&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

$qossettings{'ENABLED'} = 'off';
$qossettings{'EDIT'} = 'no';
$qossettings{'OUT_SPD'} = '';
$qossettings{'INC_SPD'} = '';
$qossettings{'DEF_OUT_SPD'} = '';
$qossettings{'DEF_INC_SPD'} = '';
$qossettings{'DEFCLASS_INC'} = '';
$qossettings{'DEFCLASS_OUT'} = '';
$qossettings{'RED_DEV'} = `cat /var/ipfire/red/iface`;
$qossettings{'IMQ_DEV'} = 'imq0';
$qossettings{'TOS'} = '';
$qossettings{'VALID'} = 'yes';

&General::readhash("${General::swroot}/qos/settings", \%qossettings);

my $DEF_OUT_MARK = ($qossettings{'DEFCLASS_OUT'} << $QOS_OUT_SHIFT) . "/$QOS_OUT_MASK";
my $DEF_INC_MARK = ($qossettings{'DEFCLASS_INC'} << $QOS_INC_SHIFT) . "/$QOS_INC_MASK";

open( FILE, "< $classfile" ) or die "Unable to read $classfile";
@classes = <FILE>;
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

	### ADD HTB QDISC FOR $qossettings{'RED_DEV'}
	tc qdisc del dev $qossettings{'RED_DEV'} root >/dev/null 2>&1
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

print "\n\t### ATTACH QDISC TO LEAF CLASSES\n";
foreach $classentry (sort @classes)
{
	@classline = split( /\;/, $classentry );
	if ($qossettings{'RED_DEV'} eq $classline[0]) {
		$qossettings{'DEVICE'} = $classline[0];
		$qossettings{'CLASS'} = $classline[1];
		print "\ttc qdisc add dev $qossettings{'DEVICE'} parent 1:$qossettings{'CLASS'} handle $qossettings{'CLASS'}: fq_codel $fqcodel_options\n";
	}
}
print "\n\t### FILTER TRAFFIC INTO CLASSES\n";
foreach $classentry (sort @classes)
{
	@classline = split( /\;/, $classentry );
	if ($qossettings{'RED_DEV'} eq $classline[0]) {
		$qossettings{'DEVICE'} = $classline[0];
		$qossettings{'CLASS'} = $classline[1];
		print "\ttc filter add dev $qossettings{'DEVICE'} parent 1:0 prio 0 protocol ip";
		printf(" u32 match mark 0x%x 0x%x flowid 1:%d\n", ($qossettings{'CLASS'} << $QOS_OUT_SHIFT), $QOS_OUT_MASK, $qossettings{'CLASS'});
	}
}

print <<END

	### ADD QOS-OUT CHAIN TO THE MANGLE TABLE IN IPTABLES
	iptables -t mangle -N QOS-OUT
	iptables -t mangle -A POSTROUTING -o $qossettings{'RED_DEV'} -j QOS-OUT

	# If the packet is already marked, then skip the processing
	iptables -t mangle -A QOS-OUT -m mark ! --mark 0/$QOS_OUT_MASK -j RETURN

	### Don't change mark on traffic for the ipsec tunnel
	iptables -t mangle -A QOS-OUT -m mark --mark 50 -j RETURN

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
			print "\tiptables -t mangle -A QOS-OUT -m tos --tos $qossettings{'TOS'} -j MARK --set-xmark " . ($qossettings{'CLASS'} << $QOS_OUT_SHIFT) . "/$QOS_OUT_MASK\n";
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
			print "\tiptables -t mangle -A QOS-OUT -m mark --mark 0/$QOS_OUT_MASK ";
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
			print "-j MARK --set-xmark " . ($qossettings{'CLASS'} << $QOS_OUT_SHIFT) . "/$QOS_OUT_MASK\n";
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
			print "-m layer7 --l7dir /etc/l7-protocols/protocols --l7proto $qossettings{'L7PROT'} -j MARK --set-xmark " . $qossettings{'CLASS'} << $QOS_OUT_SHIFT . "/$QOS_OUT_MASK\n";
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
	iptables -t mangle -A QOS-OUT -m mark --mark 0/$QOS_OUT_MASK -j MARK --set-xmark $DEF_OUT_MARK

	# Save mark in connection tracking
	iptables -t mangle -A QOS-OUT -m mark ! --mark 0/$QOS_OUT_MASK -j CONNMARK --save-mark

	###
	### $qossettings{'IMQ_DEV'}
	###

	tc qdisc del dev $qossettings{'RED_DEV'} ingress >/dev/null 2>&1
	tc qdisc add dev $qossettings{'RED_DEV'} handle ffff: ingress

	### BRING UP $qossettings{'IMQ_DEV'}
	if [ ! -d "/sys/class/net/$qossettings{'IMQ_DEV'}" ]; then
		ip link add name $qossettings{'IMQ_DEV'} type ifb
	fi

	ip link set $qossettings{'IMQ_DEV'} up

	tc filter add dev $qossettings{'RED_DEV'} parent ffff: protocol all u32 match u32 0 0 \\
		action mirred egress redirect dev $qossettings{'IMQ_DEV'}

	### ADD HTB QDISC FOR $qossettings{'IMQ_DEV'}
	tc qdisc del dev $qossettings{'IMQ_DEV'} root >/dev/null 2>&1
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

print "\n\t### ATTACH QDISC TO LEAF CLASSES\n";
foreach $classentry (sort @classes)
{
	@classline = split( /\;/, $classentry );
	if ($qossettings{'IMQ_DEV'} eq $classline[0]) {
		$qossettings{'DEVICE'} = $classline[0];
		$qossettings{'CLASS'} = $classline[1];
		print "\ttc qdisc add dev $qossettings{'DEVICE'} parent 2:$qossettings{'CLASS'} handle $qossettings{'CLASS'}: fq_codel $fqcodel_options\n";
	}
}
print "\n\t### FILTER TRAFFIC INTO CLASSES\n";
foreach $classentry (sort @classes)
{
	@classline = split( /\;/, $classentry );
	if ($qossettings{'IMQ_DEV'} eq $classline[0]) {
		$qossettings{'DEVICE'} = $classline[0];
		$qossettings{'CLASS'} = $classline[1];
		print "\ttc filter add dev $qossettings{'DEVICE'} parent 2:0 prio 0 protocol ip";
		printf(" u32 match mark 0x%x 0x%x flowid 2:%d\n", ($qossettings{'CLASS'} << $QOS_INC_SHIFT), $QOS_INC_MASK, $qossettings{'CLASS'});
	}
}
print <<END

	### ADD QOS-INC CHAIN TO THE MANGLE TABLE IN IPTABLES
	iptables -t mangle -N QOS-INC
	iptables -t mangle -A PREROUTING -i $qossettings{'RED_DEV'} -j QOS-INC

	# If the packet is already marked, then skip the processing
	iptables -t mangle -A QOS-INC -m mark ! --mark 0/$QOS_INC_MASK -j RETURN

	### SET TOS
END
;
  	foreach $tosruleentry (sort @tosrules)
  	{
  		@tosruleline = split( /\;/, $tosruleentry );
		$qossettings{'CLASS'} = $tosruleline[0];
		$qossettings{'TOS'} = abs $tosruleline[2] * 2;
  		if ( $tosruleline[1] eq $qossettings{'IMQ_DEV'} )
  		{
			print "\tiptables -t mangle -A QOS-INC -m tos --tos $qossettings{'TOS'} -j MARK --set-xmark " . ($qossettings{'CLASS'} << $QOS_INC_SHIFT) . "/$QOS_INC_MASK\n";
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
			print "\tiptables -t mangle -A QOS-INC -m mark --mark 0/$QOS_INC_MASK ";
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
			print "-j MARK --set-xmark " . ($qossettings{'CLASS'} << $QOS_INC_SHIFT) . "/$QOS_INC_MASK\n";
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
			print "\tiptables -t mangle -A QOS-INC -m mark --mark 0/$QOS_INC_MASK ";
			if ($qossettings{'QIP'} ne ''){
				print "-s $qossettings{'QIP'} ";
			}
			if ($qossettings{'DIP'} ne ''){
				print "-d $qossettings{'DIP'} ";
			}
			print "-m layer7 --l7dir /etc/l7-protocols/protocols --l7proto $qossettings{'L7PROT'} -j MARK --set-xmark " . ($qossettings{'CLASS'} << $QOS_INC_SHIFT) . "/$QOS_INC_MASK\n";
  		}
  	}

print <<END
	### REDUNDANT: SET ALL NONMARKED PACKETS TO DEFAULT CLASS
	iptables -t mangle -A QOS-INC -m mark --mark 0/$QOS_INC_MASK -m layer7 ! --l7proto unset -j MARK --set-xmark $DEF_INC_MARK

	# Save mark in connection tracking
	iptables -t mangle -A QOS-INC -m mark ! --mark 0/$QOS_INC_MASK -j CONNMARK --save-mark

	## STARTING COLLECTOR
	/usr/local/bin/qosd $qossettings{'RED_DEV'} >/dev/null 2>&1
	/usr/local/bin/qosd $qossettings{'IMQ_DEV'} >/dev/null 2>&1

	for i in \$(ls \$RRDLOG/class_*.rrd); do
		rrdtool update \$i \$(date +%s): 2>/dev/null
	done

	echo "Quality of Service was successfully started!"
	exit 0
  ;;
  clear|stop)
	### RESET EVERYTHING TO A KNOWN STATE
	killall qosd >/dev/null 2>&1

	# DELETE QDISCS
	tc qdisc del dev $qossettings{'RED_DEV'} root >/dev/null 2>&1
	tc qdisc del dev $qossettings{'RED_DEV'} ingress >/dev/null 2>&1
	tc qdisc add root dev $qossettings{'RED_DEV'} fq_codel >/dev/null 2>&1
	tc qdisc del dev $qossettings{'IMQ_DEV'} root >/dev/null 2>&1
	tc qdisc del dev $qossettings{'IMQ_DEV'} ingress >/dev/null 2>&1
	tc qdisc add root dev $qossettings{'IMQ_DEV'} fq_codel >/dev/null 2>&1
	# STOP IMQ-DEVICE
	ip link set $qossettings{'IMQ_DEV'} down >/dev/null 2>&1
	ip link del $qossettings{'IMQ_DEV'} >/dev/null 2>&1

	# REMOVE & FLUSH CHAINS
	iptables -t mangle --delete POSTROUTING -o $qossettings{'RED_DEV'} -j QOS-OUT >/dev/null 2>&1
	iptables -t mangle --delete PREROUTING -i $qossettings{'RED_DEV'} -j QOS-INC >/dev/null 2>&1
	iptables -t mangle --flush  QOS-OUT >/dev/null 2>&1
	iptables -t mangle --delete-chain QOS-OUT >/dev/null 2>&1
	iptables -t mangle --flush  QOS-INC >/dev/null 2>&1
	iptables -t mangle --delete-chain QOS-INC >/dev/null 2>&1

	rmmod sch_htb >/dev/null 2>&1

	for i in \$(ls \$RRDLOG/class_*.rrd); do
		rrdtool update \$i \$(date +%s):
	done

	echo "Quality of Service was successfully cleared!"
  ;;
  gen|generate)
	echo -n "Generating the QoS-Scripts..."
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
