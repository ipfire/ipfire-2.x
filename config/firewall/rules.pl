#!/usr/bin/perl
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
no warnings 'uninitialized';

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

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
require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "/usr/lib/firewall/firewall-lib.pl";

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
my ($TYPE,$PROT,$SPROT,$DPROT,$SPORT,$DPORT,$TIME,$TIMEFROM,$TIMETILL,$SRC_TGT);
my $CHAIN			= "FORWARDFW";
my $conexists		= 'off';
my $command			= 'iptables --wait -A';
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
#################
#    DEBUG/TEST #
#################
my $MODE=0;     # 0 - normal operation
                # 1 - print configline and rules to console
                #
#################
my $param=shift;

if($param eq 'flush'){
	if ($MODE eq '1'){
		print " Flushing chains...\n";
	}
	&flush;
}else{
	if ($MODE eq '1'){
		print " Flushing chains...\n";
	}
	&flush;
	if ($MODE eq '1'){
		print " Preparing rules...\n";
	}
	&preparerules;
	if($MODE eq '0'){
		if ($fwdfwsettings{'POLICY'} eq 'MODE1'){
			&p2pblock;
			system ("/usr/sbin/firewall-policy");
		}elsif($fwdfwsettings{'POLICY'} eq 'MODE2'){
			&p2pblock;
			system ("/usr/sbin/firewall-policy");
			system ("/etc/sysconfig/firewall.local reload");
		}
	}
}
sub flush
{
	system ("iptables --wait -F FORWARDFW");
	system ("iptables --wait -F INPUTFW");
	system ("iptables --wait -F OUTGOINGFW");
	system ("iptables --wait -t nat -F NAT_DESTINATION");
	system ("iptables --wait -t nat -F NAT_SOURCE");
}
sub preparerules
{
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
sub buildrules
{
	my $hash=shift;
	my $STAG;
	my $natip;
	my $snatport;
	my $fireport;
	my $nat;
	my $fwaccessdport;
	my $natchain;
	my $icmptype;
	foreach my $key (sort {$a <=> $b} keys %$hash){
		next if (($$hash{$key}[6] eq 'RED' || $$hash{$key}[6] eq 'RED1') && $conexists eq 'off' );
		$command="iptables --wait -A";
		if ($$hash{$key}[28] eq 'ON'){
			$command='iptables --wait -t nat -A';
			$natip=&get_nat_ip($$hash{$key}[29],$$hash{$key}[31]);
			if($$hash{$key}[31] eq 'dnat'){
				$nat='DNAT';
				if ($$hash{$key}[30] =~ /\|/){
					$$hash{$key}[30]=~ tr/|/,/;
					$fireport='-m multiport --dport '.$$hash{$key}[30];
				}else{
					$fireport='--dport '.$$hash{$key}[30] if ($$hash{$key}[30]>0);
				}
			}else{
				$nat='SNAT';
			}
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
				my $daylight=$$hash{$key}[28];
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
			if ($MODE eq '1'){
				print "NR:$key ";
				foreach my $i (0 .. $#{$$hash{$key}}){
					print "$i: $$hash{$key}[$i]  ";
				}
				print "\n";
				print"##################################\n";
				#print rules to console
				foreach my $DPROT (@DPROT){
					$DPORT = &get_port($hash,$key,$DPROT);
					if ($DPROT ne 'TCP' && $DPROT ne 'UDP' && $DPROT ne 'ICMP' ){
						$DPORT='';
					}
					$PROT=$DPROT;
					$PROT="-p $PROT" if ($PROT ne '' && $PROT ne ' ');
					foreach my $a (sort keys %sourcehash){
						foreach my $b (sort keys %targethash){
							if(! $sourcehash{$a}[0] || ! $targethash{$b}[0] || ($natip eq '-d ' && $$hash{$key}[28] eq 'ON') || (!$natip && $$hash{$key}[28] eq 'ON')){
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
											if ($$hash{$key}[17] eq 'ON'){
												print "$command $$hash{$key}[1] $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $icmptype $_ $TIME -j LOG\n";
											}
												print "$command $$hash{$key}[1] $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $icmptype $_ $TIME -j $$hash{$key}[0]\n";
										}
									#PROCESS DNAT RULE (Portforward)
									}elsif($$hash{$key}[28] eq 'ON' && $$hash{$key}[31] eq 'dnat'){
										$natchain='NAT_DESTINATION';
										if ($$hash{$key}[17] eq 'ON'){
											print "$command $natchain $PROT $STAG $sourcehash{$a}[0] $SPORT $natip $fireport $TIME -j LOG --log-prefix 'DNAT' \n";
										}
										my ($ip,$sub) =split("/",$targethash{$b}[0]);
										#Process NAT with servicegroup used
										if ($$hash{$key}[28] eq 'ON' && $$hash{$key}[31] eq 'dnat' && $$hash{$key}[14] eq 'cust_srvgrp'){
											print "$command $natchain $PROT $STAG $sourcehash{$a}[0] $SPORT $natip $fireport $TIME -j $nat --to-destination $ip $DPORT\n";
											$fwaccessdport=$DPORT;
										}else{
											print "$command $natchain $PROT $STAG $sourcehash{$a}[0] $SPORT $natip $fireport $TIME -j $nat --to-destination $ip$DPORT\n";
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
										print "iptables --wait -A FORWARDFW $PROT $STAG $sourcehash{$a}[0] -d $ip $fwaccessdport $TIME -j $$hash{$key}[0]\n";
										next;
									#PROCESS SNAT RULE
									}elsif($$hash{$key}[28] eq 'ON' && $$hash{$key}[31] eq 'snat'){
										$natchain='NAT_SOURCE';
										if ($$hash{$key}[17] eq 'ON' ){
											print "$command $natchain $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $DPORT $TIME -j LOG --log-prefix 'SNAT' \n";
										}
										print "$command $natchain $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $DPORT $TIME -j $nat --to-source $natip\n";
									}
									#PROCESS EVERY OTHER RULE (If NOT ICMP, else the rule would be applied double)
									if ($PROT ne '-p ICMP'){
										if ($$hash{$key}[17] eq 'ON' && $$hash{$key}[28] ne 'ON'){
											print "$command $$hash{$key}[1] $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $DPORT $TIME -j LOG\n";
										}
										print "iptables --wait -A $$hash{$key}[1] $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $DPORT $TIME -j $$hash{$key}[0]\n";
									}
									#PROCESS Prot ICMP and type = All ICMP-Types
									if ($PROT eq '-p ICMP' && $$hash{$key}[9] eq 'All ICMP-Types'){
										if ($$hash{$key}[17] eq 'ON' && $$hash{$key}[28] ne 'ON'){
											print "$command $$hash{$key}[1] $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $DPORT $TIME -j LOG\n";
										}
										print "iptables --wait -A $$hash{$key}[1] $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $DPORT $TIME -j $$hash{$key}[0]\n";
									}
								}
							}
						}
					}
					print"\n";
				}
			}elsif($MODE eq '0'){
				foreach my $DPROT (@DPROT){
					$DPORT = &get_port($hash,$key,$DPROT);
					$PROT=$DPROT;
					$PROT="-p $PROT" if ($PROT ne '' && $PROT ne ' ');
					if ($DPROT ne 'TCP' && $DPROT ne'UDP' && $DPROT ne 'ICMP' ){
						$DPORT='';
					}
					foreach my $a (sort keys %sourcehash){
						foreach my $b (sort keys %targethash){
							if(! $sourcehash{$a}[0] || ! $targethash{$b}[0] || $natip eq '-d ' || !$natip){
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
											if ($$hash{$key}[17] eq 'ON'){
												system ("$command $$hash{$key}[1] $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $icmptype $_ $TIME -j LOG");
											}
												system ("$command $$hash{$key}[1] $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $icmptype $_ $TIME -j $$hash{$key}[0]");
										}
									#PROCESS DNAT RULE (Portforward)
									}elsif($$hash{$key}[28] eq 'ON' && $$hash{$key}[31] eq 'dnat'){
										$natchain='NAT_DESTINATION';
										if ($$hash{$key}[17] eq 'ON'){
											system "$command $natchain $PROT $STAG $sourcehash{$a}[0] $SPORT $natip $fireport $TIME -j LOG --log-prefix 'DNAT' \n";
										}
										my ($ip,$sub) =split("/",$targethash{$b}[0]);
										#Process NAT with servicegroup used
										if ($$hash{$key}[28] eq 'ON' && $$hash{$key}[31] eq 'dnat' && $$hash{$key}[14] eq 'cust_srvgrp'){
											system "$command $natchain $PROT $STAG $sourcehash{$a}[0] $SPORT $natip $fireport $TIME -j $nat --to-destination $ip $DPORT\n";
											$fwaccessdport=$DPORT;
										}else{
											system "$command $natchain $PROT $STAG $sourcehash{$a}[0] $SPORT $natip $fireport $TIME -j $nat --to-destination $ip$DPORT\n";
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
										system "iptables --wait -A FORWARDFW $PROT $STAG $sourcehash{$a}[0] -d $ip $fwaccessdport $TIME -j $$hash{$key}[0]\n";
										next;
									#PROCESS SNAT RULE
									}elsif($$hash{$key}[28] eq 'ON' && $$hash{$key}[31] eq 'snat'){
										$natchain='NAT_SOURCE';
										if ($$hash{$key}[17] eq 'ON' ){
											system "$command $natchain $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $DPORT $TIME -j LOG --log-prefix 'SNAT' \n";
										}
										system "$command $natchain $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $DPORT $TIME -j $nat --to-source $natip\n";
									}
									#PROCESS EVERY OTHER RULE (If NOT ICMP, else the rule would be applied double)
									if ($PROT ne '-p ICMP'){
										if ($$hash{$key}[17] eq 'ON' && $$hash{$key}[28] ne 'ON'){
											system "$command $$hash{$key}[1] $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $DPORT $TIME -j LOG\n";
										}
										system "iptables --wait -A $$hash{$key}[1] $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $DPORT $TIME -j $$hash{$key}[0]\n";
									}
									#PROCESS Prot ICMP and type = All ICMP-Types
									if ($PROT eq '-p ICMP' && $$hash{$key}[9] eq 'All ICMP-Types'){
										if ($$hash{$key}[17] eq 'ON' && $$hash{$key}[28] ne 'ON'){
											system "$command $$hash{$key}[1] $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $DPORT $TIME -j LOG\n";
										}
										system "iptables --wait -A $$hash{$key}[1] $PROT $STAG $sourcehash{$a}[0] $SPORT -d $targethash{$b}[0] $DPORT $TIME -j $$hash{$key}[0]\n";
									}
								}
							}
						}
					}
				}
			}
		}
		%sourcehash=();
		%targethash=();
		undef $TIME;
		undef $TIMEFROM;
		undef $TIMETILL;
		undef $fireport;
	}
}
sub get_nat_ip
{
	my $val=shift;
	my $type=shift;
	my $result;
	if($val eq 'RED' || $val eq 'GREEN' || $val eq 'ORANGE' || $val eq 'BLUE'){
		$result=$defaultNetworks{$val.'_ADDRESS'};
	}elsif($val eq 'ALL'){
		$result='-i '.$con;
	}elsif($val eq 'Default IP' && $type eq 'dnat'){
		$result='-d '.$redip;
	}elsif($val eq 'Default IP' && $type eq 'snat'){
		$result=$redip;
	}else{
		foreach my $al (sort keys %aliases){
			if($val eq $al && $type eq 'dnat'){
				$result='-d '.$aliases{$al}{'IPT'};
			}elsif($val eq $al && $type eq 'snat'){
				$result=$aliases{$al}{'IPT'};
			}
		}
	}
	return $result;
}
sub get_time
{
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
sub time_get_utc
{
	# Calculates the UTCtime from a given time
	my $val=shift;
	my @localtime=localtime(time);
	my @gmtime=gmtime(time);
	my $diff = ($gmtime[2]*60+$gmtime[1]%60)-($localtime[2]*60+$localtime[1]%60);
	return $diff;
}
sub utcmin
{
	my $ruletime=shift;
	my ($hrs,$min) = split(":",$ruletime);
	my $newtime = $hrs*60+$min;
	return $newtime;
}
sub p2pblock
{
	my $P2PSTRING;
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
	if ($MODE eq 1){
		if($P2PSTRING){
			print"/sbin/iptables --wait -A FORWARDFW $CMD $P2PSTRING -j $DO\n";
		}
	}else{
		if($P2PSTRING){
			system("/sbin/iptables --wait -A FORWARDFW $CMD $P2PSTRING -j $DO");
		}
	}
}
sub get_address
{
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
sub get_prot
{
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
sub get_port
{
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
