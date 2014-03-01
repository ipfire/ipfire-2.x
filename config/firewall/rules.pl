#!/usr/bin/perl -w
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2013 Alexander Marx <amarx@ipfire.org>                        #
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
use Time::Local;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "/usr/lib/firewall/firewall-lib.pl";

# Set to one to enable debugging mode.
my $DEBUG = 0;

my $IPTABLES = "iptables --wait";

# iptables chains
my $CHAIN                 = "FORWARDFW";
my $CHAIN_NAT_SOURCE      = "NAT_SOURCE";
my $CHAIN_NAT_DESTINATION = "NAT_DESTINATION";

my %fwdfwsettings=();
my %defaultNetworks=();
my %configfwdfw=();
my %color=();
my %icmptypes=();
my %ovpnSettings=();
my %customgrp=();
our %sourcehash=();
our %targethash=();
my @timeframe=();
my %configinputfw=();
my %configoutgoingfw=();
my %confignatfw=();
my %aliases=();
my @DPROT=();
my @p2ps=();

my $configfwdfw		= "${General::swroot}/firewall/config";
my $configinput	    = "${General::swroot}/firewall/input";
my $configoutgoing  = "${General::swroot}/firewall/outgoing";
my $p2pfile			= "${General::swroot}/firewall/p2protocols";
my $configgrp		= "${General::swroot}/fwhosts/customgroups";
my $netsettings		= "${General::swroot}/ethernet/settings";
my $errormessage	= '';
my $orange			= '';
my $green			= '';
my $blue			= '';
my ($TYPE,$PROT,$SPROT,$DPROT,$SPORT,$DPORT,$SRC_TGT);
my $conexists		= 'off';
my $dnat			='';
my $snat			='';

&General::readhash("${General::swroot}/firewall/settings", \%fwdfwsettings);
&General::readhash("$netsettings", \%defaultNetworks);
&General::readhasharray($configfwdfw, \%configfwdfw);
&General::readhasharray($configinput, \%configinputfw);
&General::readhasharray($configoutgoing, \%configoutgoingfw);
&General::readhasharray($configgrp, \%customgrp);
&General::get_aliases(\%aliases);

#check if we have an internetconnection
open (CONN,"/var/ipfire/red/iface");
my $con = <CONN>;
close(CONN);

if (-f "/var/ipfire/red/active"){
	$conexists='on';
}

open (CONN1,"/var/ipfire/red/local-ipaddress");
my $redip = <CONN1>;
close(CONN1);

# MAIN
&main();

sub main {
	# Flush all chains.
	&flush();

	# Reload firewall rules.
	&preparerules();

	# Load P2P block rules.
	&p2pblock();

	# Reload firewall policy.
	run("/usr/sbin/firewall-policy");
}

sub run {
	# Executes or prints the given shell command.
	my $command = shift;

	if ($DEBUG) {
		print "$command\n";
	} else {
		system "$command";
	}
}

sub print_error {
	my $message = shift;

	print STDERR "$message\n";
}

sub flush {
	run("$IPTABLES -F FORWARDFW");
	run("$IPTABLES -F INPUTFW");
	run("$IPTABLES -F OUTGOINGFW");
	run("$IPTABLES -t nat -F NAT_DESTINATION");
	run("$IPTABLES -t nat -F NAT_SOURCE");
}

sub preparerules {
	if (! -z  "${General::swroot}/firewall/config"){
		&buildrules(\%configfwdfw);
	}
	if (! -z  "${General::swroot}/firewall/input"){
		&buildrules(\%configinputfw);
	}
	if (! -z  "${General::swroot}/firewall/outgoing"){
		&buildrules(\%configoutgoingfw);
	}
}

sub buildrules {
	my $hash=shift;
	my $STAG;
	my $snatport;
	my $fireport;
	my $fwaccessdport;
	my $natchain;
	my $icmptype;
	foreach my $key (sort {$a <=> $b} keys %$hash){
		next if (($$hash{$key}[6] eq 'RED' || $$hash{$key}[6] eq 'RED1') && $conexists eq 'off' );

		my $TIME = "";
		my $TIMEFROM;
		my $TIMETILL;
		my $natip = "";

		# Check if logging should be enabled.
		my $LOG = 0;
		if ($$hash{$key}[17] eq 'ON') {
			$LOG = 1;
		}

		my $NAT = 0;
		my $NAT_MODE;

		# Check if NAT is enabled and initialize variables, that we use for that.
		if ($$hash{$key}[28] eq 'ON') {
			$NAT = 1;

			# Destination NAT
			if ($$hash{$key}[31] eq 'dnat') {
				$NAT_MODE = "DNAT";

				if ($$hash{$key}[30] =~ /\|/) {
					$$hash{$key}[30]=~ tr/|/,/;
					$fireport='-m multiport --dport '.$$hash{$key}[30];
				} else {
					$fireport='--dport '.$$hash{$key}[30] if ($$hash{$key}[30]>0);
				}

			# Source NAT
			} elsif ($$hash{$key}[31] eq 'snat') {
				$NAT_MODE = "SNAT";

			} else {
				print_error("Invalid NAT mode: $$hash{$key}[31]");
				next;
			}

			$natip = &get_nat_ip($$hash{$key}[29], $NAT_MODE);
		}

		$STAG='';
		if($$hash{$key}[2] eq 'ON'){
			#get source ip's
			if ($$hash{$key}[3] eq 'cust_grp_src'){
				foreach my $grp (sort {$a <=> $b} keys %customgrp){
						if($customgrp{$grp}[0] eq $$hash{$key}[4]){
						&get_address($customgrp{$grp}[3],$customgrp{$grp}[2],"src");
					}
				}
			}else{
				&get_address($$hash{$key}[3],$$hash{$key}[4],"src");
			}
			#get target ip's
			if ($$hash{$key}[5] eq 'cust_grp_tgt'){
				foreach my $grp (sort {$a <=> $b} keys %customgrp){
					if($customgrp{$grp}[0] eq $$hash{$key}[6]){
						&get_address($customgrp{$grp}[3],$customgrp{$grp}[2],"tgt");
					}
				}
			}elsif($$hash{$key}[5] eq 'ipfire' ){
				if($$hash{$key}[6] eq 'GREEN'){
					$targethash{$key}[0]=$defaultNetworks{'GREEN_ADDRESS'};
				}
				if($$hash{$key}[6] eq 'BLUE'){
					$targethash{$key}[0]=$defaultNetworks{'BLUE_ADDRESS'};
				}
				if($$hash{$key}[6] eq 'ORANGE'){
					$targethash{$key}[0]=$defaultNetworks{'ORANGE_ADDRESS'};
				}
				if($$hash{$key}[6] eq 'ALL'){
					$targethash{$key}[0]='0.0.0.0/0';
				}
				if($$hash{$key}[6] eq 'RED' || $$hash{$key}[6] eq 'RED1'){
					open(FILE, "/var/ipfire/red/local-ipaddress")or die "Couldn't open local-ipaddress";
					$targethash{$key}[0]= <FILE>;
					close(FILE);
				}else{
					foreach my $alias (sort keys %aliases){
						if ($$hash{$key}[6] eq $alias){
							$targethash{$key}[0]=$aliases{$alias}{'IPT'};
						}
					}
				}
			}else{
				&get_address($$hash{$key}[5],$$hash{$key}[6],"tgt");
			}
			##get source prot and port
			$SRC_TGT='SRC';
			$SPORT = &get_port($hash,$key);
			$SRC_TGT='';

			##get target prot and port
			$DPROT=&get_prot($hash,$key);

			if ($DPROT eq ''){$DPROT=' ';}
			@DPROT=split(",",$DPROT);

			#get time if defined
			if($$hash{$key}[18] eq 'ON'){
				my ($time1,$time2,$daylight);
				$daylight=$$hash{$key}[28];
				$time1=&get_time($$hash{$key}[26],$daylight);
				$time2=&get_time($$hash{$key}[27],$daylight);
				if($$hash{$key}[19] ne ''){push (@timeframe,"Mon");}
				if($$hash{$key}[20] ne ''){push (@timeframe,"Tue");}
				if($$hash{$key}[21] ne ''){push (@timeframe,"Wed");}
				if($$hash{$key}[22] ne ''){push (@timeframe,"Thu");}
				if($$hash{$key}[23] ne ''){push (@timeframe,"Fri");}
				if($$hash{$key}[24] ne ''){push (@timeframe,"Sat");}
				if($$hash{$key}[25] ne ''){push (@timeframe,"Sun");}
				$TIME=join(",",@timeframe);

				$TIMEFROM="--timestart $time1 ";
				$TIMETILL="--timestop $time2 ";
				$TIME="-m time --weekdays $TIME $TIMEFROM $TIMETILL";
			}
			foreach my $DPROT (@DPROT){
				$DPORT = &get_port($hash,$key,$DPROT);
				$PROT=$DPROT;
				$PROT="-p $PROT" if ($PROT ne '' && $PROT ne ' ');
				if ($DPROT ne 'TCP' && $DPROT ne'UDP' && $DPROT ne 'ICMP' ){
					$DPORT='';
				}
				foreach my $a (sort keys %sourcehash){
					foreach my $b (sort keys %targethash){
						if(! $sourcehash{$a}[0] || ! $targethash{$b}[0] || ($natip eq '-d ' && $NAT) || (!$natip && $NAT)){
							#Skip rules when no RED IP is set (DHCP,DSL)
							next;
						}
						next if ($targethash{$b}[0] eq 'none');
						$STAG='';
						if ($sourcehash{$a}[0] ne $targethash{$b}[0] && $targethash{$b}[0] ne 'none' || $sourcehash{$a}[0] eq '0.0.0.0/0.0.0.0'){
							if($DPROT ne ''){
								if(substr($sourcehash{$a}[0], 3, 3) ne 'mac' && $sourcehash{$a}[0] ne ''){ $STAG="-s";}
								#Process ICMP RULE
								if(substr($DPORT, 2, 4) eq 'icmp'){
									my @icmprule= split(",",substr($DPORT, 12,));
									foreach (@icmprule){
										$icmptype="--icmp-type ";
										if ($_ eq "BLANK") {
												$icmptype="";
												$_="";
										}
										if ($LOG) {
											run("$IPTABLES -A $$hash{$key}[1] $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $icmptype $_ $TIME -j LOG");
										}
										run("$IPTABLES -A $$hash{$key}[1] $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $icmptype $_ $TIME -j $$hash{$key}[0]");
									}
								#PROCESS DNAT RULE (Portforward)
								} elsif ($NAT && $NAT_MODE eq "DNAT") {
									if ($LOG) {
										run("$IPTABLES -t nat -A $CHAIN_NAT_DESTINATION $PROT $STAG $sourcehash{$a}[0] $SPORT $natip $fireport $TIME -j LOG --log-prefix 'DNAT'");
									}
									my ($ip,$sub) =split("/",$targethash{$b}[0]);
									#Process NAT with servicegroup used
									if ($$hash{$key}[14] eq 'cust_srvgrp') {
										run("$IPTABLES -t nat -A $CHAIN_NAT_DESTINATION $PROT $STAG $sourcehash{$a}[0] $SPORT $natip $fireport $TIME -j DNAT --to-destination $ip $DPORT");
										$fwaccessdport=$DPORT;
									} else {
										run("$IPTABLES -t nat -A $CHAIN_NAT_DESTINATION $PROT $STAG $sourcehash{$a}[0] $SPORT $natip $fireport $TIME -j DNAT --to-destination $ip$DPORT");
										$DPORT =~ s/\-/:/g;
										if ($DPORT){
											$fwaccessdport="--dport ".substr($DPORT,1,);
										}elsif(! $DPORT && $$hash{$key}[30] ne ''){
											if ($$hash{$key}[30]=~m/|/i){
												$$hash{$key}[30] =~ s/\|/,/g;
												$fwaccessdport="-m multiport --dport $$hash{$key}[30]";
											}else{
												$fwaccessdport="--dport $$hash{$key}[30]";
											}
										}
									}
									run("$IPTABLES -A FORWARDFW $PROT $STAG $sourcehash{$a}[0] -d $ip $fwaccessdport $TIME -j $$hash{$key}[0]");
									next;
								#PROCESS SNAT RULE
								} elsif ($NAT && $NAT_MODE eq "SNAT") {
									if ($LOG) {
										run("$IPTABLES -t nat -A $CHAIN_NAT_SOURCE $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $DPORT $TIME -j LOG --log-prefix 'SNAT'");
									}
									run("$IPTABLES -t nat -A $CHAIN_NAT_SOURCE $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $DPORT $TIME -j SNAT --to-source $natip");
								}
								#PROCESS EVERY OTHER RULE (If NOT ICMP, else the rule would be applied double)
								if ($PROT ne '-p ICMP'){
									if ($LOG && !$NAT) {
										run("$IPTABLES -A $$hash{$key}[1] $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $DPORT $TIME -j LOG");
									}
									run("$IPTABLES -A $$hash{$key}[1] $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $DPORT $TIME -j $$hash{$key}[0]");
								}
								#PROCESS Prot ICMP and type = All ICMP-Types
								if ($PROT eq '-p ICMP' && $$hash{$key}[9] eq 'All ICMP-Types'){
									if ($LOG && !$NAT) {
										run("$IPTABLES -A $$hash{$key}[1] $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $DPORT $TIME -j LOG");
									}
									run("$IPTABLES -A $$hash{$key}[1] $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $DPORT $TIME -j $$hash{$key}[0]");
								}
							}
						}
					}
				}
			}
		}
		%sourcehash=();
		%targethash=();
		undef $fireport;
	}
}

sub get_nat_ip {
	my $val=shift;
	my $type=shift;
	my $result;
	if($val eq 'RED' || $val eq 'GREEN' || $val eq 'ORANGE' || $val eq 'BLUE'){
		$result=$defaultNetworks{$val.'_ADDRESS'};
	}elsif($val eq 'ALL'){
		$result='-i '.$con;
	}elsif($val eq 'Default IP' && $type eq "DNAT"){
		$result='-d '.$redip;
	}elsif($val eq 'Default IP' && $type eq "SNAT"){
		$result=$redip;
	}else{
		foreach my $al (sort keys %aliases){
			if($val eq $al && $type eq "DNAT"){
				$result='-d '.$aliases{$al}{'IPT'};
			}elsif($val eq $al && $type eq "SNAT"){
				$result=$aliases{$al}{'IPT'};
			}
		}
	}
	return $result;
}

sub get_time {
	my $val=shift;
	my $val1=shift;
	my $time;
	my $minutes;
	my $ruletime;
	$minutes = &utcmin($val);
	$ruletime = $minutes + &time_get_utc($val);
	if ($ruletime < 0){$ruletime +=1440;}
	if ($ruletime > 1440){$ruletime -=1440;}
	$time=sprintf "%02d:%02d", $ruletime / 60, $ruletime % 60;
	return $time;
}

sub time_get_utc {
	# Calculates the UTCtime from a given time
	my $val=shift;
	my @localtime=localtime(time);
	my @gmtime=gmtime(time);
	my $diff = ($gmtime[2]*60+$gmtime[1]%60)-($localtime[2]*60+$localtime[1]%60);
	return $diff;
}

sub utcmin {
	my $ruletime=shift;
	my ($hrs,$min) = split(":",$ruletime);
	my $newtime = $hrs*60+$min;
	return $newtime;
}

sub p2pblock {
	my $P2PSTRING = "";
	my $DO;
	open( FILE, "< $p2pfile" ) or die "Unable to read $p2pfile";
	@p2ps = <FILE>;
	close FILE;
	my $CMD = "-m ipp2p";
	foreach my $p2pentry (sort @p2ps) {
		my @p2pline = split( /\;/, $p2pentry );
		if ( $fwdfwsettings{'POLICY'} eq 'MODE1' ) {
			$DO = "ACCEPT";
			if ("$p2pline[2]" eq "on") {
				$P2PSTRING = "$P2PSTRING --$p2pline[1]";
			}
		}else {
			$DO = "RETURN";
			if ("$p2pline[2]" eq "off") {
				$P2PSTRING = "$P2PSTRING --$p2pline[1]";
			}
		}
	}

	if($P2PSTRING) {
		run("$IPTABLES -A FORWARDFW $CMD $P2PSTRING -j $DO");
	}
}

sub get_address {
	my $base=shift; #source of checking ($configfwdfw{$key}[x] or groupkey
	my $base2=shift;
	my $type=shift; #src or tgt
	my $hash;
	if ($type eq 'src'){
		$hash=\%sourcehash;
	}else{
		$hash=\%targethash;
	}
	my $key = &General::findhasharraykey($hash);
	if($base eq 'src_addr' || $base eq 'tgt_addr' ){
		if (&General::validmac($base2)){
			$$hash{$key}[0] = "-m mac --mac-source $base2";
		}else{
			$$hash{$key}[0] = $base2;
		}
	}elsif($base eq 'std_net_src' || $base eq 'std_net_tgt' || $base eq 'Standard Network'){
		$$hash{$key}[0]=&fwlib::get_std_net_ip($base2,$con);
	}elsif($base eq 'cust_net_src' || $base eq 'cust_net_tgt' || $base eq 'Custom Network'){
		$$hash{$key}[0]=&fwlib::get_net_ip($base2);
	}elsif($base eq 'cust_host_src' || $base eq 'cust_host_tgt' || $base eq 'Custom Host'){
		$$hash{$key}[0]=&fwlib::get_host_ip($base2,$type);
	}elsif($base eq 'ovpn_net_src' || $base eq 'ovpn_net_tgt' || $base eq 'OpenVPN static network'){
		$$hash{$key}[0]=&fwlib::get_ovpn_net_ip($base2,1);
	}elsif($base eq 'ovpn_host_src' ||$base eq 'ovpn_host_tgt' || $base eq 'OpenVPN static host'){
		$$hash{$key}[0]=&fwlib::get_ovpn_host_ip($base2,33);
	}elsif($base eq 'ovpn_n2n_src' ||$base eq 'ovpn_n2n_tgt' || $base eq 'OpenVPN N-2-N'){
		$$hash{$key}[0]=&fwlib::get_ovpn_n2n_ip($base2,11);
	}elsif($base eq 'ipsec_net_src' || $base eq 'ipsec_net_tgt' || $base eq 'IpSec Network'){
		$$hash{$key}[0]=&fwlib::get_ipsec_net_ip($base2,11);
	}elsif($base eq 'ipfire_src' ){
		if($base2 eq 'GREEN'){
			$$hash{$key}[0]=$defaultNetworks{'GREEN_ADDRESS'};
		}
		if($base2 eq 'BLUE'){
			$$hash{$key}[0]=$defaultNetworks{'BLUE_ADDRESS'};
		}
		if($base2 eq 'ORANGE'){
			$$hash{$key}[0]=$defaultNetworks{'ORANGE_ADDRESS'};
		}
		if($base2 eq 'ALL'){
			$$hash{$key}[0]='0.0.0.0/0';
		}
		if($base2 eq 'RED' || $base2 eq 'RED1'){
			open(FILE, "/var/ipfire/red/local-ipaddress");
			$$hash{$key}[0]= <FILE>;
			close(FILE);
		}else{
			foreach my $alias (sort keys %aliases){
				if ($base2 eq $alias){
					$$hash{$key}[0]=$aliases{$alias}{'IPT'};
				}
			}
		}
	}
}

sub get_prot {
	my $hash=shift;
	my $key=shift;
	#check AH,GRE,ESP or ICMP
	if ($$hash{$key}[7] ne 'ON' && $$hash{$key}[11] ne 'ON'){
		return "$$hash{$key}[8]";
	}
	if ($$hash{$key}[7] eq 'ON' || $$hash{$key}[11] eq 'ON'){
		#check if servicegroup or service
		if($$hash{$key}[14] eq 'cust_srv'){
			return &fwlib::get_srv_prot($$hash{$key}[15]);
		}elsif($$hash{$key}[14] eq 'cust_srvgrp'){
			return &fwlib::get_srvgrp_prot($$hash{$key}[15]);
		}elsif (($$hash{$key}[10] ne '' || $$hash{$key}[15] ne '') && $$hash{$key}[8] eq ''){ #when ports are used and prot set to "all"
			return "TCP,UDP";
		}elsif (($$hash{$key}[10] ne '' || $$hash{$key}[15] ne '') && ($$hash{$key}[8] eq 'TCP' || $$hash{$key}[8] eq 'UDP')){ #when ports are used and prot set to "tcp" or "udp"
			return "$$hash{$key}[8]";
		}elsif (($$hash{$key}[10] eq '' && $$hash{$key}[15] eq '') && $$hash{$key}[8] ne 'ICMP'){ #when ports are NOT used and prot NOT set to "ICMP"
			return "$$hash{$key}[8]";
		}else{
			return "$$hash{$key}[8]";
		}
	}
	#DNAT
	if ($SRC_TGT eq '' && $$hash{$key}[31] eq 'dnat' && $$hash{$key}[11] eq '' && $$hash{$key}[12] ne ''){
		return "$$hash{$key}[8]";
	}
}

sub get_port {
	my $hash=shift;
	my $key=shift;
	my $prot=shift;
	#Get manual defined Ports from SOURCE
	if ($$hash{$key}[7] eq 'ON' && $SRC_TGT eq 'SRC'){
		if ($$hash{$key}[10] ne ''){
			$$hash{$key}[10] =~ s/\|/,/g;
			if(index($$hash{$key}[10],",") > 0){
				return "-m multiport --sport $$hash{$key}[10] ";
			}else{
				if($$hash{$key}[28] ne 'ON' || ($$hash{$key}[28] eq 'ON' && $$hash{$key}[31] eq 'snat') ||($$hash{$key}[28] eq 'ON' && $$hash{$key}[31] eq 'dnat')  ){
					return "--sport $$hash{$key}[10] ";
				}else{
					return ":$$hash{$key}[10]";
				}
			}
		}
		#Get manual ports from TARGET
	}elsif($$hash{$key}[11] eq 'ON' && $SRC_TGT eq ''){
		if($$hash{$key}[14] eq 'TGT_PORT'){
			if ($$hash{$key}[15] ne ''){
				$$hash{$key}[15] =~ s/\|/,/g;
				if(index($$hash{$key}[15],",") > 0){
					return "-m multiport --dport $$hash{$key}[15] ";
				}else{
					if($$hash{$key}[28] ne 'ON' || ($$hash{$key}[28] eq 'ON' && $$hash{$key}[31] eq 'snat') ){
						return "--dport $$hash{$key}[15] ";
					 }else{
						 $$hash{$key}[15] =~ s/\:/-/g;
						 return ":$$hash{$key}[15]";
					 }
				}
			}
		#Get ports defined in custom Service (firewall-groups)
		}elsif($$hash{$key}[14] eq 'cust_srv'){
			if ($prot ne 'ICMP'){
				if($$hash{$key}[31] eq 'dnat' && $$hash{$key}[28] eq 'ON'){
					my $ports =&fwlib::get_srv_port($$hash{$key}[15],1,$prot);
					$ports =~ s/\:/-/g;
					return ":".$ports
				}else{
					return "--dport ".&fwlib::get_srv_port($$hash{$key}[15],1,$prot);
				}
			}elsif($prot eq 'ICMP' && $$hash{$key}[11] eq 'ON'){        #When PROT is ICMP and "use targetport is checked, this is an icmp-service
				return "--icmp-type ".&fwlib::get_srv_port($$hash{$key}[15],3,$prot);
			}
		#Get ports from services which are used in custom servicegroups (firewall-groups)
		}elsif($$hash{$key}[14] eq 'cust_srvgrp'){
			if 	($prot ne 'ICMP'){
				return &fwlib::get_srvgrp_port($$hash{$key}[15],$prot);
			}
			elsif($prot eq 'ICMP'){
				return &fwlib::get_srvgrp_port($$hash{$key}[15],$prot);
			}
		}
	}
	#CHECK ICMP
	if ($$hash{$key}[7] ne 'ON' && $$hash{$key}[11] ne 'ON' && $SRC_TGT eq ''){
		if($$hash{$key}[9] ne '' && $$hash{$key}[9] ne 'All ICMP-Types'){
			return "--icmp-type $$hash{$key}[9] ";
		}elsif($$hash{$key}[9] eq 'All ICMP-Types'){
			return;
		}
	}
}
