#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2012  											              #
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
#																			  #
# Hi folks! I hope this code is useful for all. I needed something to handle  #
# my VPN Connections in a comfortable way. As a prerequisite i needed 		  #
# something that makes sure the vpn roadwarrior are able to have a fixed 	  #
# ip-address. So i developed the ccd extension for the vpn server.			  #
# 																			  #
# Now that the ccd extension is ready i am able to develop the main request.  #
# Any feedback is appreciated.												  #
#																			  #
#																			  #
###############################################################################

use strict;
no warnings 'uninitialized';
# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "${General::swroot}/forward/bin/firewall-lib.pl";

unless (-d "${General::swroot}/forward") 			{ system("mkdir ${General::swroot}/forward"); }
unless (-e "${General::swroot}/forward/settings")   { system("touch ${General::swroot}/forward/settings"); }
unless (-e "${General::swroot}/forward/config")  	{ system("touch ${General::swroot}/forward/config"); }
unless (-e "${General::swroot}/forward/input")  	{ system("touch ${General::swroot}/forward/input"); }

my %fwdfwsettings=();
my %selected=() ;
my %defaultNetworks=();
my %netsettings=();
my %customhost=();
my %customgrp=();
my %customnetworks=();
my %customservice=();
my %customservicegrp=();
my %ccdnet=();
my %customnetwork=();
my %ccdhost=();
my %configfwdfw=();
my %configinputfw=();
my %ipsecconf=();
my %color=();
my %mainsettings=();
my %checked=();
my %icmptypes=();
my %ovpnsettings=();
my %ipsecsettings=();
my %aliases=();
my @p2ps = ();
my $color;
my $confignet		= "${General::swroot}/fwhosts/customnetworks";
my $confighost		= "${General::swroot}/fwhosts/customhosts";
my $configgrp 		= "${General::swroot}/fwhosts/customgroups";
my $configsrv 		= "${General::swroot}/fwhosts/customservices";
my $configsrvgrp	= "${General::swroot}/fwhosts/customservicegrp";
my $configccdnet 	= "${General::swroot}/ovpn/ccd.conf";
my $configccdhost	= "${General::swroot}/ovpn/ovpnconfig";
my $configipsec		= "${General::swroot}/vpn/config";
my $configipsecrw	= "${General::swroot}/vpn/settings";
my $configfwdfw		= "${General::swroot}/forward/config";
my $configinput		= "${General::swroot}/forward/input";
my $configovpn		= "${General::swroot}/ovpn/settings";
my $p2pfile			= "${General::swroot}/forward/p2protocols";
my $errormessage='';
my $hint='';
my $ipgrp="${General::swroot}/outgoing/groups";


&General::readhash("${General::swroot}/forward/settings", \%fwdfwsettings);
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

&Header::showhttpheaders();
&Header::getcgihash(\%fwdfwsettings);
&Header::openpage($Lang::tr{'fwdfw menu'}, 1, '');
&Header::openbigbox('100%', 'center',$errormessage);
####  ACTION  #####

if ($fwdfwsettings{'ACTION'} eq $Lang::tr{'save'})
{
	my $MODE = $fwdfwsettings{'POLICY'};
	%fwdfwsettings = ();
	$fwdfwsettings{'POLICY'} = "$MODE";
	&General::writehash("${General::swroot}/forward/settings", \%fwdfwsettings);
	&reread_rules;
}
if ($fwdfwsettings{'ACTION'} eq 'saverule')
{
	&General::readhasharray("$configfwdfw", \%configfwdfw);
	&General::readhasharray("$configinput", \%configinputfw);
	$errormessage=&checksource;
	if(!$errormessage){&checktarget;}
	if(!$errormessage){&checkrule;}
	#check if we change an forward rule to an external access
	if(	$fwdfwsettings{'grp2'} eq 'ipfire' && $fwdfwsettings{'oldgrp2a'} ne 'ipfire' && $fwdfwsettings{'updatefwrule'} eq 'on'){
		$fwdfwsettings{'updatefwrule'}='';
		$fwdfwsettings{'config'}=$configfwdfw;
		$fwdfwsettings{'nobase'}='on';
		&deleterule;
		&checkcounter(0,0,$fwdfwsettings{'grp1'},$fwdfwsettings{$fwdfwsettings{'grp1'}});
		&checkcounter(0,0,$fwdfwsettings{'grp3'},$fwdfwsettings{$fwdfwsettings{'grp3'}});
	}
	#check if we change an external access rule to an forward
	if(	$fwdfwsettings{'grp2'} ne 'ipfire' && $fwdfwsettings{'oldgrp2a'} eq 'ipfire' && $fwdfwsettings{'updatefwrule'} eq 'on'){
		$fwdfwsettings{'updatefwrule'}='';
		$fwdfwsettings{'config'}=$configinput;
		$fwdfwsettings{'nobase'}='on';
		&deleterule;
		&checkcounter(0,0,$fwdfwsettings{'grp1'},$fwdfwsettings{$fwdfwsettings{'grp1'}});
		&checkcounter(0,0,$fwdfwsettings{'grp3'},$fwdfwsettings{$fwdfwsettings{'grp3'}});
	}	
	#INPUT part
	if($fwdfwsettings{'grp2'} eq 'ipfire'){
		$fwdfwsettings{'chain'} = 'INPUTFW';
		my $maxkey=&General::findhasharraykey(\%configinputfw);
		#check if we have an identical rule already
		if($fwdfwsettings{'oldrulenumber'} eq $fwdfwsettings{'rulepos'}){
			foreach my $key (sort keys %configinputfw){
				if ("$fwdfwsettings{'RULE_ACTION'},$fwdfwsettings{'ACTIVE'},$fwdfwsettings{'grp1'},$fwdfwsettings{$fwdfwsettings{'grp1'}},$fwdfwsettings{'grp2'},$fwdfwsettings{$fwdfwsettings{'grp2'}},$fwdfwsettings{'USE_SRC_PORT'},$fwdfwsettings{'PROT'},$fwdfwsettings{'ICMP_TYPES'},$fwdfwsettings{'SRC_PORT'},$fwdfwsettings{'USESRV'},$fwdfwsettings{'TGT_PROT'},$fwdfwsettings{'ICMP_TGT'},$fwdfwsettings{'grp3'},$fwdfwsettings{$fwdfwsettings{'grp3'}},$fwdfwsettings{'LOG'},$fwdfwsettings{'TIME'},$fwdfwsettings{'TIME_MON'},$fwdfwsettings{'TIME_TUE'},$fwdfwsettings{'TIME_WED'},$fwdfwsettings{'TIME_THU'},$fwdfwsettings{'TIME_FRI'},$fwdfwsettings{'TIME_SAT'},$fwdfwsettings{'TIME_SUN'},$fwdfwsettings{'TIME_FROM'},$fwdfwsettings{'TIME_TO'}" 
					eq "$configinputfw{$key}[0],$configinputfw{$key}[2],$configinputfw{$key}[3],$configinputfw{$key}[4],$configinputfw{$key}[5],$configinputfw{$key}[6],$configinputfw{$key}[7],$configinputfw{$key}[8],$configinputfw{$key}[9],$configinputfw{$key}[10],$configinputfw{$key}[11],$configinputfw{$key}[12],$configinputfw{$key}[13],$configinputfw{$key}[14],$configinputfw{$key}[15],$configinputfw{$key}[17],$configinputfw{$key}[18],$configinputfw{$key}[19],$configinputfw{$key}[20],$configinputfw{$key}[21],$configinputfw{$key}[22],$configinputfw{$key}[23],$configinputfw{$key}[24],$configinputfw{$key}[25],$configinputfw{$key}[26],$configinputfw{$key}[27]"){
						$errormessage.=$Lang::tr{'fwdfw err ruleexists'};
						if ($fwdfwsettings{'oldruleremark'} ne $fwdfwsettings{'ruleremark'} && $fwdfwsettings{'updatefwrule'} eq 'on' && &validremark($fwdfwsettings{'ruleremark'})){
							$errormessage='';
						}elsif($fwdfwsettings{'oldruleremark'} ne $fwdfwsettings{'ruleremark'} && $fwdfwsettings{'updatefwrule'} eq 'on' && !&validremark($fwdfwsettings{'ruleremark'})){
							$errormessage=$Lang::tr{'fwdfw err remark'}."<br>";
						}
						if ($fwdfwsettings{'oldruleremark'} eq $fwdfwsettings{'ruleremark'}){
							$fwdfwsettings{'nosave'} = 'on';
						}
				}	
			}	
		}
		#check Rulepos on new Rule
		if($fwdfwsettings{'rulepos'} > 0 && !$fwdfwsettings{'oldrulenumber'}){
			$fwdfwsettings{'oldrulenumber'}=$maxkey;
			foreach my $key (sort keys %configinputfw){
				if ("$fwdfwsettings{'RULE_ACTION'},$fwdfwsettings{'ACTIVE'},$fwdfwsettings{'grp1'},$fwdfwsettings{$fwdfwsettings{'grp1'}},$fwdfwsettings{'grp2'},$fwdfwsettings{$fwdfwsettings{'grp2'}},$fwdfwsettings{'USE_SRC_PORT'},$fwdfwsettings{'PROT'},$fwdfwsettings{'ICMP_TYPES'},$fwdfwsettings{'SRC_PORT'},$fwdfwsettings{'USESRV'},$fwdfwsettings{'TGT_PROT'},$fwdfwsettings{'ICMP_TGT'},$fwdfwsettings{'grp3'},$fwdfwsettings{$fwdfwsettings{'grp3'}},$fwdfwsettings{'LOG'},$fwdfwsettings{'TIME'},$fwdfwsettings{'TIME_MON'},$fwdfwsettings{'TIME_TUE'},$fwdfwsettings{'TIME_WED'},$fwdfwsettings{'TIME_THU'},$fwdfwsettings{'TIME_FRI'},$fwdfwsettings{'TIME_SAT'},$fwdfwsettings{'TIME_SUN'},$fwdfwsettings{'TIME_FROM'},$fwdfwsettings{'TIME_TO'}" 
					eq "$configinputfw{$key}[0],$configinputfw{$key}[2],$configinputfw{$key}[3],$configinputfw{$key}[4],$configinputfw{$key}[5],$configinputfw{$key}[6],$configinputfw{$key}[7],$configinputfw{$key}[8],$configinputfw{$key}[9],$configinputfw{$key}[10],$configinputfw{$key}[11],$configinputfw{$key}[12],$configinputfw{$key}[13],$configinputfw{$key}[14],$configinputfw{$key}[15],$configinputfw{$key}[17],$configinputfw{$key}[18],$configinputfw{$key}[19],$configinputfw{$key}[20],$configinputfw{$key}[21],$configinputfw{$key}[22],$configinputfw{$key}[23],$configinputfw{$key}[24],$configinputfw{$key}[25],$configinputfw{$key}[26],$configinputfw{$key}[27]"){
						$errormessage.=$Lang::tr{'fwdfw err ruleexists'};
				}
			}
		}
		#check if we just close a rule
		if( $fwdfwsettings{'oldgrp1a'} eq  $fwdfwsettings{'grp1'} && $fwdfwsettings{'oldgrp1b'} eq $fwdfwsettings{$fwdfwsettings{'grp1'}} && $fwdfwsettings{'oldgrp2a'} eq  $fwdfwsettings{'grp2'} && $fwdfwsettings{'oldgrp2b'} eq $fwdfwsettings{$fwdfwsettings{'grp2'}} &&  $fwdfwsettings{'oldgrp3a'} eq $fwdfwsettings{'grp3'} && $fwdfwsettings{'oldgrp3b'} eq  $fwdfwsettings{$fwdfwsettings{'grp3'}} && $fwdfwsettings{'oldusesrv'} eq $fwdfwsettings{'USESRV'} ) {
			if($fwdfwsettings{'nosave'} eq 'on' && $fwdfwsettings{'updatefwrule'} eq 'on'){
				$errormessage='';
				$fwdfwsettings{'nosave2'} = 'on';
			}
		}
		&checkcounter($fwdfwsettings{'oldgrp1a'},$fwdfwsettings{'oldgrp1b'},$fwdfwsettings{'grp1'},$fwdfwsettings{$fwdfwsettings{'grp1'}});
		if ($fwdfwsettings{'nobase'} ne 'on'){
			&checkcounter($fwdfwsettings{'oldgrp2a'},$fwdfwsettings{'oldgrp2b'},$fwdfwsettings{'grp2'},$fwdfwsettings{$fwdfwsettings{'grp2'}});
		}
		if($fwdfwsettings{'oldusesrv'} eq '' &&  $fwdfwsettings{'USESRV'} eq 'ON'){
			&checkcounter(0,0,$fwdfwsettings{'grp3'},$fwdfwsettings{$fwdfwsettings{'grp3'}});
		}elsif ($fwdfwsettings{'USESRV'} eq '' && $fwdfwsettings{'oldusesrv'} eq 'ON') {
			&checkcounter($fwdfwsettings{'oldgrp3a'},$fwdfwsettings{'oldgrp3b'},0,0);
		}elsif ($fwdfwsettings{'oldusesrv'} eq $fwdfwsettings{'USESRV'} && $fwdfwsettings{'oldgrp3b'} ne $fwdfwsettings{$fwdfwsettings{'grp3'}} && $fwdfwsettings{'updatefwrule'} eq 'on'){
			&checkcounter($fwdfwsettings{'oldgrp3a'},$fwdfwsettings{'oldgrp3b'},$fwdfwsettings{'grp3'},$fwdfwsettings{$fwdfwsettings{'grp3'}});
		}
		if($fwdfwsettings{'nosave2'} ne 'on'){
			&saverule(\%configinputfw,$configinput);
		}
		#print "Source: $fwdfwsettings{'grp1'} -> $fwdfwsettings{$fwdfwsettings{'grp1'}}<br>";
		#print "Sourceport: $fwdfwsettings{'USE_SRC_PORT'}, $fwdfwsettings{'PROT'}, $fwdfwsettings{'ICMP_TYPES'}, $fwdfwsettings{'SRC_PORT'}<br>";
		#print "Target: $fwdfwsettings{'grp2'} -> $fwdfwsettings{$fwdfwsettings{'grp2'}}<br>";
		#print "Dienst:  $fwdfwsettings{'USESRV'}, $fwdfwsettings{'grp3'} -> $fwdfwsettings{$fwdfwsettings{'grp3'}}<br>";
		#print "BEMERKUNG: $fwdfwsettings{'ruleremark'}<br>";
		#print " Regel AKTIV: $fwdfwsettings{'ACTIVE'}<br>";
		#print " Regel LOG: $fwdfwsettings{'LOG'}<br>";
		#print " ZEITRAHMEN: $fwdfwsettings{'TIME'}<br>";
		#print " MO: $fwdfwsettings{'TIME_MON'}<br>";
		#print " DI: $fwdfwsettings{'TIME_TUE'}<br>";
		#print " MI: $fwdfwsettings{'TIME_WED'}<br>";
		#print " DO: $fwdfwsettings{'TIME_THU'}<br>";
		#print " FR: $fwdfwsettings{'TIME_FRI'}<br>";
		#print " SA: $fwdfwsettings{'TIME_SAT'}<br>";
		#print " SO: $fwdfwsettings{'TIME_SUN'}<br>";
		#print " VON: $fwdfwsettings{'TIME_FROM'} bis $fwdfwsettings{'TIME_TO'}<br>";
		#print "<br>";
		#print"ALT: $fwdfwsettings{'oldgrp1a'} $fwdfwsettings{'oldgrp1b'}	NEU:	$fwdfwsettings{'grp1'} $fwdfwsettings{$fwdfwsettings{'grp1'}}<br>";
		#print"ALT: $fwdfwsettings{'oldgrp2a'} $fwdfwsettings{'oldgrp2b'}	NEU:	$fwdfwsettings{'grp2'} $fwdfwsettings{$fwdfwsettings{'grp2'}}<br>";
		#print"ALT: $fwdfwsettings{'oldgrp3a'} $fwdfwsettings{'oldgrp3b'}	NEU:	$fwdfwsettings{'grp3'} $fwdfwsettings{$fwdfwsettings{'grp3'}}<br>";
		#print"DIENSTE Checkalt:$fwdfwsettings{'oldusesrv'}  DIENSTE Checkneu:$fwdfwsettings{'USESRV'}    DIENST ALT:$fwdfwsettings{'oldgrp3a'},$fwdfwsettings{'oldgrp3b'}   DIENST NEU:$fwdfwsettings{'grp3'},$fwdfwsettings{$fwdfwsettings{'grp3'}}<br>";
	}else{
		#FORWARD PART
		$fwdfwsettings{'chain'} = 'FORWARDFW';
		my $maxkey=&General::findhasharraykey(\%configfwdfw);
		if($fwdfwsettings{'oldrulenumber'} eq $fwdfwsettings{'rulepos'}){
			#check if we have an identical rule already
			foreach my $key (sort keys %configfwdfw){
				if ("$fwdfwsettings{'RULE_ACTION'},$fwdfwsettings{'ACTIVE'},$fwdfwsettings{'grp1'},$fwdfwsettings{$fwdfwsettings{'grp1'}},$fwdfwsettings{'grp2'},$fwdfwsettings{$fwdfwsettings{'grp2'}},$fwdfwsettings{'USE_SRC_PORT'},$fwdfwsettings{'PROT'},$fwdfwsettings{'ICMP_TYPES'},$fwdfwsettings{'SRC_PORT'},$fwdfwsettings{'USESRV'},$fwdfwsettings{'TGT_PROT'},$fwdfwsettings{'ICMP_TGT'},$fwdfwsettings{'grp3'},$fwdfwsettings{$fwdfwsettings{'grp3'}},$fwdfwsettings{'LOG'},$fwdfwsettings{'TIME'},$fwdfwsettings{'TIME_MON'},$fwdfwsettings{'TIME_TUE'},$fwdfwsettings{'TIME_WED'},$fwdfwsettings{'TIME_THU'},$fwdfwsettings{'TIME_FRI'},$fwdfwsettings{'TIME_SAT'},$fwdfwsettings{'TIME_SUN'},$fwdfwsettings{'TIME_FROM'},$fwdfwsettings{'TIME_TO'}" 
					eq "$configfwdfw{$key}[0],$configfwdfw{$key}[2],$configfwdfw{$key}[3],$configfwdfw{$key}[4],$configfwdfw{$key}[5],$configfwdfw{$key}[6],$configfwdfw{$key}[7],$configfwdfw{$key}[8],$configfwdfw{$key}[9],$configfwdfw{$key}[10],$configfwdfw{$key}[11],$configfwdfw{$key}[12],$configfwdfw{$key}[13],$configfwdfw{$key}[14],$configfwdfw{$key}[15],$configfwdfw{$key}[17],$configfwdfw{$key}[18],$configfwdfw{$key}[19],$configfwdfw{$key}[20],$configfwdfw{$key}[21],$configfwdfw{$key}[22],$configfwdfw{$key}[23],$configfwdfw{$key}[24],$configfwdfw{$key}[25],$configfwdfw{$key}[26],$configfwdfw{$key}[27]"){
						$errormessage.=$Lang::tr{'fwdfw err ruleexists'};
						if ($fwdfwsettings{'oldruleremark'} ne $fwdfwsettings{'ruleremark'} && $fwdfwsettings{'updatefwrule'} eq 'on' && &validremark($fwdfwsettings{'ruleremark'})){
							$errormessage='';
						}elsif($fwdfwsettings{'oldruleremark'} ne $fwdfwsettings{'ruleremark'} && $fwdfwsettings{'updatefwrule'} eq 'on' && !&validremark($fwdfwsettings{'ruleremark'})){
							$errormessage=$Lang::tr{'fwdfw err remark'}."<br>";
						}
						if ($fwdfwsettings{'oldruleremark'} eq $fwdfwsettings{'ruleremark'}){
							$fwdfwsettings{'nosave'} = 'on';
						}
				}		
			}
		}	
		#check Rulepos on new Rule
		if($fwdfwsettings{'rulepos'} > 0 && !$fwdfwsettings{'oldrulenumber'}){
			$fwdfwsettings{'oldrulenumber'}=$maxkey;
			foreach my $key (sort keys %configfwdfw){
				if ("$fwdfwsettings{'RULE_ACTION'},$fwdfwsettings{'ACTIVE'},$fwdfwsettings{'grp1'},$fwdfwsettings{$fwdfwsettings{'grp1'}},$fwdfwsettings{'grp2'},$fwdfwsettings{$fwdfwsettings{'grp2'}},$fwdfwsettings{'USE_SRC_PORT'},$fwdfwsettings{'PROT'},$fwdfwsettings{'ICMP_TYPES'},$fwdfwsettings{'SRC_PORT'},$fwdfwsettings{'USESRV'},$fwdfwsettings{'TGT_PROT'},$fwdfwsettings{'ICMP_TGT'},$fwdfwsettings{'grp3'},$fwdfwsettings{$fwdfwsettings{'grp3'}},$fwdfwsettings{'LOG'},$fwdfwsettings{'TIME'},$fwdfwsettings{'TIME_MON'},$fwdfwsettings{'TIME_TUE'},$fwdfwsettings{'TIME_WED'},$fwdfwsettings{'TIME_THU'},$fwdfwsettings{'TIME_FRI'},$fwdfwsettings{'TIME_SAT'},$fwdfwsettings{'TIME_SUN'},$fwdfwsettings{'TIME_FROM'},$fwdfwsettings{'TIME_TO'}" 
					eq "$configfwdfw{$key}[0],$configfwdfw{$key}[2],$configfwdfw{$key}[3],$configfwdfw{$key}[4],$configfwdfw{$key}[5],$configfwdfw{$key}[6],$configfwdfw{$key}[7],$configfwdfw{$key}[8],$configfwdfw{$key}[9],$configfwdfw{$key}[10],$configfwdfw{$key}[11],$configfwdfw{$key}[12],$configfwdfw{$key}[13],$configfwdfw{$key}[14],$configfwdfw{$key}[15],$configfwdfw{$key}[17],$configfwdfw{$key}[18],$configfwdfw{$key}[19],$configfwdfw{$key}[20],$configfwdfw{$key}[21],$configfwdfw{$key}[22],$configfwdfw{$key}[23],$configfwdfw{$key}[24],$configfwdfw{$key}[25],$configfwdfw{$key}[26],$configfwdfw{$key}[27]"){
						$errormessage.=$Lang::tr{'fwdfw err ruleexists'};
				}		
			}
		}
		#check if we just close a rule
		if( $fwdfwsettings{'oldgrp1a'} eq  $fwdfwsettings{'grp1'} && $fwdfwsettings{'oldgrp1b'} eq $fwdfwsettings{$fwdfwsettings{'grp1'}} && $fwdfwsettings{'oldgrp2a'} eq  $fwdfwsettings{'grp2'} && $fwdfwsettings{'oldgrp2b'} eq $fwdfwsettings{$fwdfwsettings{'grp2'}} &&  $fwdfwsettings{'oldgrp3a'} eq $fwdfwsettings{'grp3'} && $fwdfwsettings{'oldgrp3b'} eq  $fwdfwsettings{$fwdfwsettings{'grp3'}} && $fwdfwsettings{'oldusesrv'} eq $fwdfwsettings{'USESRV'} && $fwdfwsettings{'oldruleremark'} eq $fwdfwsettings{'ruleremark'} ) {
			if($fwdfwsettings{'nosave'} eq 'on' && $fwdfwsettings{'updatefwrule'} eq 'on'){
				$fwdfwsettings{'nosave2'} = 'on';
				$errormessage='';
			}
		}
		#increase counters
		&checkcounter($fwdfwsettings{'oldgrp1a'},$fwdfwsettings{'oldgrp1b'},$fwdfwsettings{'grp1'},$fwdfwsettings{$fwdfwsettings{'grp1'}});
		&checkcounter($fwdfwsettings{'oldgrp2a'},$fwdfwsettings{'oldgrp2b'},$fwdfwsettings{'grp2'},$fwdfwsettings{$fwdfwsettings{'grp2'}});
		if($fwdfwsettings{'oldusesrv'} eq '' &&  $fwdfwsettings{'USESRV'} eq 'ON'){
			&checkcounter(0,0,$fwdfwsettings{'grp3'},$fwdfwsettings{$fwdfwsettings{'grp3'}});
		}elsif ($fwdfwsettings{'USESRV'} eq '' && $fwdfwsettings{'oldusesrv'} eq 'ON') {
			&checkcounter($fwdfwsettings{'oldgrp3a'},$fwdfwsettings{'oldgrp3b'},0,0);
		}elsif ($fwdfwsettings{'oldusesrv'} eq $fwdfwsettings{'USESRV'} && $fwdfwsettings{'oldgrp3b'} ne $fwdfwsettings{$fwdfwsettings{'grp3'}} && $fwdfwsettings{'updatefwrule'} eq 'on'){
			&checkcounter($fwdfwsettings{'oldgrp3a'},$fwdfwsettings{'oldgrp3b'},$fwdfwsettings{'grp3'},$fwdfwsettings{$fwdfwsettings{'grp3'}});
		}
		if ($fwdfwsettings{'nobase'} eq 'on'){
			&checkcounter(0,0,$fwdfwsettings{'grp3'},$fwdfwsettings{$fwdfwsettings{'grp3'}});
		}
		if ($fwdfwsettings{'nosave2'} ne 'on'){
			&saverule(\%configfwdfw,$configfwdfw);
		}	
		#print "Source: $fwdfwsettings{'grp1'} -> $fwdfwsettings{$fwdfwsettings{'grp1'}}<br>";
		#print "Sourceport: $fwdfwsettings{'USE_SRC_PORT'}, $fwdfwsettings{'PROT'}, $fwdfwsettings{'ICMP_TYPES'}, $fwdfwsettings{'SRC_PORT'}<br>";
		#print "Target: $fwdfwsettings{'grp2'} -> $fwdfwsettings{$fwdfwsettings{'grp2'}}<br>";
		#print "Dienst:  $fwdfwsettings{'USESRV'}, $fwdfwsettings{'grp3'} -> $fwdfwsettings{$fwdfwsettings{'grp3'}}<br>";
		#print "BEMERKUNG: $fwdfwsettings{'ruleremark'}<br>";
		#print " Regel AKTIV: $fwdfwsettings{'ACTIVE'}<br>";
		#print " Regel LOG: $fwdfwsettings{'LOG'}<br>";
		#print " ZEITRAHMEN: $fwdfwsettings{'TIME'}<br>";
		#print " MO: $fwdfwsettings{'TIME_MON'}<br>";
		#print " DI: $fwdfwsettings{'TIME_TUE'}<br>";
		#print " MI: $fwdfwsettings{'TIME_WED'}<br>";
		#print " DO: $fwdfwsettings{'TIME_THU'}<br>";
		#print " FR: $fwdfwsettings{'TIME_FRI'}<br>";
		#print " SA: $fwdfwsettings{'TIME_SAT'}<br>";
		#print " SO: $fwdfwsettings{'TIME_SUN'}<br>";
		#print " VON: $fwdfwsettings{'TIME_FROM'} bis $fwdfwsettings{'TIME_TO'}<br>";
		#print "<br>";
		#print"ALT: $fwdfwsettings{'oldgrp1a'} $fwdfwsettings{'oldgrp1b'}	NEU:	$fwdfwsettings{'grp1'} $fwdfwsettings{$fwdfwsettings{'grp1'}}<br>";
		#print"ALT: $fwdfwsettings{'oldgrp2a'} $fwdfwsettings{'oldgrp2b'}	NEU:	$fwdfwsettings{'grp2'} $fwdfwsettings{$fwdfwsettings{'grp2'}}<br>";
		#print"ALT: $fwdfwsettings{'oldgrp3a'} $fwdfwsettings{'oldgrp3b'}	NEU:	$fwdfwsettings{'grp3'} $fwdfwsettings{$fwdfwsettings{'grp3'}}<br>";
		#print"DIENSTE Checkalt:$fwdfwsettings{'oldusesrv'}  DIENSTE Checkneu:$fwdfwsettings{'USESRV'}    DIENST ALT:$fwdfwsettings{'oldgrp3a'},$fwdfwsettings{'oldgrp3b'}   DIENST NEU:$fwdfwsettings{'grp3'},$fwdfwsettings{$fwdfwsettings{'grp3'}}<br>";
	}
	if ($errormessage){
		&newrule;
	}else{
		if($fwdfwsettings{'nosave2'} ne 'on'){
			&rules;
		}
		&base;
	}
}
if ($fwdfwsettings{'ACTION'} eq $Lang::tr{'reset'})
{
	&General::readhasharray("$configfwdfw", \%configfwdfw);
	foreach my $key (sort keys %configfwdfw){
		&checkcounter($configfwdfw{$key}[3],$configfwdfw{$key}[4],,);
		&checkcounter($configfwdfw{$key}[5],$configfwdfw{$key}[6],,);
		&checkcounter($configfwdfw{$key}[14],$configfwdfw{$key}[15],,);
	}
		&General::readhasharray("$configinput", \%configinputfw);
	foreach my $key (sort keys %configinputfw){
		&checkcounter($configinputfw{$key}[3],$configinputfw{$key}[4],,);
		&checkcounter($configinputfw{$key}[5],$configinputfw{$key}[6],,);
		&checkcounter($configinputfw{$key}[14],$configinputfw{$key}[15],,);
	}
	
	system("rm ${General::swroot}/forward/config");
	system("rm ${General::swroot}/forward/input");
	&General::writehash("${General::swroot}/forward/settings", \%fwdfwsettings);
	unless (-e "${General::swroot}/forward/config")  	{ system("touch ${General::swroot}/forward/config"); }
	unless (-e "${General::swroot}/forward/input")  	{ system("touch ${General::swroot}/forward/input"); }
	%fwdfwsettings = ();
	$fwdfwsettings{'POLICY'}='MODE2';
	&General::writehash("${General::swroot}/forward/settings", \%fwdfwsettings);
	&reread_rules;

}
if ($fwdfwsettings{'ACTION'} eq $Lang::tr{'fwdfw newrule'})
{
	&newrule;
}
if ($fwdfwsettings{'ACTION'} eq $Lang::tr{'fwdfw toggle'})
{
	my %togglehash=();
	&General::readhasharray($fwdfwsettings{'config'}, \%togglehash);
	foreach my $key (sort keys %togglehash){
		if ($key eq $fwdfwsettings{'key'}){
			if ($togglehash{$key}[2] eq 'ON'){$togglehash{$key}[2]='';}else{$togglehash{$key}[2]='ON';}
		}
	}
	&General::writehasharray($fwdfwsettings{'config'}, \%togglehash);
	&rules;
	&base;
}
if ($fwdfwsettings{'ACTION'} eq $Lang::tr{'fwdfw togglelog'})
{
	my %togglehash=();
	&General::readhasharray($fwdfwsettings{'config'}, \%togglehash);
	foreach my $key (sort keys %togglehash){
		if ($key eq $fwdfwsettings{'key'}){
			if ($togglehash{$key}[17] eq 'ON'){$togglehash{$key}[17]='';}else{$togglehash{$key}[17]='ON';}
		}
	}
	&General::writehasharray($fwdfwsettings{'config'}, \%togglehash);
	&rules;
	&base;
}
if ($fwdfwsettings{'ACTION'} eq $Lang::tr{'fwdfw reread'})
{
	&reread_rules;
	&base;
}
if ($fwdfwsettings{'ACTION'} eq 'editrule')
{
	$fwdfwsettings{'updatefwrule'}='on';
	&newrule;
}
if ($fwdfwsettings{'ACTION'} eq 'deleterule')
{
	&deleterule;
}
if ($fwdfwsettings{'ACTION'} eq 'moveup')
{
	&pos_up;
	&base;
}
if ($fwdfwsettings{'ACTION'} eq 'movedown')
{
	&pos_down;
	&base;
}
if ($fwdfwsettings{'ACTION'} eq 'copyrule')
{
	$fwdfwsettings{'copyfwrule'}='on';
	#$fwdfwsettings{'updatefwrule'}='on';
	&newrule;
}
if ($fwdfwsettings{'ACTION'} eq 'togglep2p')
{
	#$errormessage="Toggle $fwdfwsettings{'P2PROT'}<br>";
	open( FILE, "< $p2pfile" ) or die "Unable to read $p2pfile";
	@p2ps = <FILE>;
	close FILE;
	open( FILE, "> $p2pfile" ) or die "Unable to write $p2pfile";
	foreach my $p2pentry (sort @p2ps)
	{
		my @p2pline = split( /\;/, $p2pentry );
		if ($p2pline[1] eq $fwdfwsettings{'P2PROT'}) {
			if($p2pline[2] eq 'on'){
				$p2pline[2]='off';
			}else{
				$p2pline[2]='on';
			}
		}
		print FILE "$p2pline[0];$p2pline[1];$p2pline[2];\n";
	}
	close FILE;
	&rules;
	&base;
}
if ($fwdfwsettings{'ACTION'} eq '')
{
	&base;
}
###  Functions  ####
sub pos_up
{
	my %uphash=();
	my %tmp=();
	&General::readhasharray($fwdfwsettings{'config'}, \%uphash);
	foreach my $key (sort keys %uphash){
		if ($key eq $fwdfwsettings{'key'}) {
			my $last = $key -1;
			if (exists $uphash{$last}){
				#save rule last
				foreach my $y (0 .. $#{$uphash{$last}}) {
						$tmp{0}[$y] = $uphash{$last}[$y];
				}
				#copy active rule to last
				foreach my $i (0 .. $#{$uphash{$last}}) {
					$uphash{$last}[$i] = $uphash{$key}[$i];
				}
				#copy saved rule to actual position
				foreach my $x (0 .. $#{$tmp{0}}) {
						$uphash{$key}[$x] = $tmp{0}[$x];
				}
			}
		}
	}
	&General::writehasharray($fwdfwsettings{'config'}, \%uphash);
	&rules;
}
sub pos_down
{
	my %downhash=();
	my %tmp=();
	&General::readhasharray($fwdfwsettings{'config'}, \%downhash);
	foreach my $key (sort keys %downhash){
		if ($key eq $fwdfwsettings{'key'}) {
			my $next = $key + 1;
			if (exists $downhash{$next}){
				#save rule next
				foreach my $y (0 .. $#{$downhash{$next}}) {
						$tmp{0}[$y] = $downhash{$next}[$y];
				}
				#copy active rule to next
				foreach my $i (0 .. $#{$downhash{$next}}) {
					$downhash{$next}[$i] = $downhash{$key}[$i];
				}
				#copy saved rule to actual position
				foreach my $x (0 .. $#{$tmp{0}}) {
						$downhash{$key}[$x] = $tmp{0}[$x];
				}
			}
		}
	}
	&General::writehasharray($fwdfwsettings{'config'}, \%downhash);
	&rules;
}
sub checkcounter
{
	my ($base1,$val1,$base2,$val2) = @_;
		
	if($base1 eq 'cust_net_src' || $base1 eq 'cust_net_tgt'){
		&dec_counter($confignet,\%customnetwork,$val1);
	}elsif($base1 eq 'cust_host_src' || $base1 eq 'cust_host_tgt'){
		&dec_counter($confighost,\%customhost,$val1);
	}elsif($base1 eq 'cust_grp_src' || $base1 eq 'cust_grp_tgt'){
		&dec_counter($configgrp,\%customgrp,$val1);
	}elsif($base1 eq 'cust_srv'){
		&dec_counter($configsrv,\%customservice,$val1);
	}elsif($base1 eq 'cust_srvgrp'){
		&dec_counter($configsrvgrp,\%customservicegrp,$val1);	
	}

	if($base2 eq 'cust_net_src' || $base2 eq 'cust_net_tgt'){
		&inc_counter($confignet,\%customnetwork,$val2);
	}elsif($base2 eq 'cust_host_src' || $base2 eq 'cust_host_tgt'){
		&inc_counter($confighost,\%customhost,$val2);
	}elsif($base2 eq 'cust_grp_src' || $base2 eq 'cust_grp_tgt'){
		&inc_counter($configgrp,\%customgrp,$val2);
	}elsif($base2 eq 'cust_srv'){
		&inc_counter($configsrv,\%customservice,$val2);
	}elsif($base2 eq 'cust_srvgrp'){
		&inc_counter($configsrvgrp,\%customservicegrp,$val2);	
	}
}
sub inc_counter
{
	my $config=shift;
	my %hash=%{(shift)};
	my $val=shift;
	my $pos;

	&General::readhasharray($config, \%hash);
	foreach my $key (sort { uc($hash{$a}[0]) cmp uc($hash{$b}[0]) }  keys %hash){
		if($hash{$key}[0] eq $val){
			$pos=$#{$hash{$key}};
			$hash{$key}[$pos] = $hash{$key}[$pos]+1;
		}
	}
	&General::writehasharray($config, \%hash);
}
sub dec_counter
{
	my $config=shift;
	my %hash=%{(shift)};
	my $val=shift;
	my $pos;
	#$errormessage.="ALT:config: $config , verringert wird $val <br>";
	&General::readhasharray($config, \%hash);
	foreach my $key (sort { uc($hash{$a}[0]) cmp uc($hash{$b}[0]) }  keys %hash){
		if($hash{$key}[0] eq $val){
			$pos=$#{$hash{$key}};
			$hash{$key}[$pos] = $hash{$key}[$pos]-1;
		}
	}
	&General::writehasharray($config, \%hash);
}
sub base
{
	if ($fwdfwsettings{'POLICY'} eq 'MODE1'){ $selected{'POLICY'}{'MODE1'} = 'selected'; } else { $selected{'POLICY'}{'MODE1'} = ''; }
	if ($fwdfwsettings{'POLICY'} eq 'MODE2'){ $selected{'POLICY'}{'MODE2'} = 'selected'; } else { $selected{'POLICY'}{'MODE2'} = ''; }
	&hint;
	&addrule;
	&p2pblock;
	&Header::openbox('100%', 'center', 'Policy');
print <<END;
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table width='100%'>
		<tr><td width='10%' align='left'><b>$Lang::tr{'mode'} 1:</b><td width='90%' align='left' colspan='2'>$Lang::tr{'outgoing firewall mode1'}</td></tr>
		<tr><td width='10%' align='left'><b>$Lang::tr{'mode'} 2:</b><td width='90%' align='left' colspan='2'>$Lang::tr{'outgoing firewall mode2'}</td></tr>
		<tr><td colspan='3'><hr /></td></tr>
		<tr><td width='10%' align='left'>	<select name='POLICY' style="width: 85px">$Lang::tr{'mode'} 0</option><option value='MODE1' $selected{'POLICY'}{'MODE1'}>$Lang::tr{'mode'} 1</option><option value='MODE2' $selected{'POLICY'}{'MODE2'}>$Lang::tr{'mode'} 2</option></select>
	    <td width='45%' align='left'><input type='submit' name='ACTION' value=$Lang::tr{'save'} />
	    <td width='45%' align='left'>
END
	print "$Lang::tr{'outgoing firewall reset'}: <input type='submit' name='ACTION' value='$Lang::tr{'reset'}' />";
	print "</table></form>";
	&Header::closebox();
}
sub addrule
{
	&error;
	&Header::openbox('100%', 'left', $Lang::tr{'fwdfw addrule'});

	print "<form method='post'>";
	print "<table border='0'>";
	print "<tr><td><input type='submit' name='ACTION' value='$Lang::tr{'fwdfw newrule'}'></td>";
	if (-f "${General::swroot}/forward/reread"){
		print "<td><input type='submit' name='ACTION' value='$Lang::tr{'fwdfw reread'}'></td>";
	}
		print"</tr></table></form><hr>";	

	&Header::closebox();
	&viewtablerule;
}
sub deleterule
{
	my %delhash=();
	&General::readhasharray($fwdfwsettings{'config'}, \%delhash);
	foreach my $key (sort {$a <=> $b} keys %delhash){
		if ($key == $fwdfwsettings{'key'}){
			#check hosts/net and groups
			&checkcounter($delhash{$key}[3],$delhash{$key}[4],,);
			&checkcounter($delhash{$key}[5],$delhash{$key}[6],,);
			#check services and groups
			if ($delhash{$key}[11] eq 'ON'){
				&checkcounter($delhash{$key}[14],$delhash{$key}[15],,);
			}
		}
		if ($key >= $fwdfwsettings{'key'}) {
			my $next = $key + 1;
			if (exists $delhash{$next}) {
				foreach my $i (0 .. $#{$delhash{$next}}) {
					$delhash{$key}[$i] = $delhash{$next}[$i];
				}
			}
		}
	}
	# Remove the very last entry.
	my $last_key = (sort {$a <=> $b} keys %delhash)[-1];
	delete $delhash{$last_key};

	&General::writehasharray($fwdfwsettings{'config'}, \%delhash);
	&rules;

	if($fwdfwsettings{'nobase'} ne 'on'){
		&base;
	}
}
sub disable_rule
{
	my $key1=shift;
	&General::readhasharray("$configfwdfw", \%configfwdfw);
	foreach my $key (sort keys %configfwdfw){
			if ($key eq $key1 ){
			if ($configfwdfw{$key}[2] eq 'ON'){$configfwdfw{$key}[2]='';}
		}
	}
	&General::writehasharray("$configfwdfw", \%configfwdfw);
	&rules;
}
sub checksource
{
	my ($ip,$subnet);

	#check ip-address if manual
	if ($fwdfwsettings{'src_addr'} eq $fwdfwsettings{$fwdfwsettings{'grp1'}} && $fwdfwsettings{'src_addr'} ne ''){
		#check if ip with subnet
		if ($fwdfwsettings{'src_addr'} =~ /^(.*?)\/(.*?)$/) {
			($ip,$subnet)=split (/\//,$fwdfwsettings{'src_addr'});
			$subnet = &General::iporsubtocidr($subnet);
			$fwdfwsettings{'isip'}='on';
		}
		#check if only ip
		if($fwdfwsettings{'src_addr'}=~/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/){
			$ip=$fwdfwsettings{'src_addr'};
			$subnet = '32';
			$fwdfwsettings{'isip'}='on';
		}

		if ($fwdfwsettings{'isip'} ne 'on'){
			if (&General::validmac($fwdfwsettings{'src_addr'})){$fwdfwsettings{'ismac'}='on';}
		}
		if ($fwdfwsettings{'isip'} eq 'on'){
			#check and form valid IP
			$ip=&General::ip2dec($ip);
			$ip=&General::dec2ip($ip);
			#check if net or broadcast
			my @tmp= split (/\./,$ip);
			if (($tmp[3] eq "0") || ($tmp[3] eq "255"))
			{
				$errormessage=$Lang::tr{'fwhost err hostip'}."<br>";
			}
			$fwdfwsettings{'src_addr'}="$ip/$subnet";

			if(!&General::validipandmask($fwdfwsettings{'src_addr'})){
				$errormessage.=$Lang::tr{'fwdfw err src_addr'}."<br>";
			}
		}
		if ($fwdfwsettings{'isip'} ne 'on' && $fwdfwsettings{'ismac'} ne 'on'){
			$errormessage.=$Lang::tr{'fwdfw err src_addr'}."<br>";
		}
	}elsif($fwdfwsettings{'src_addr'} eq $fwdfwsettings{$fwdfwsettings{'grp1'}} && $fwdfwsettings{'src_addr'} eq ''){
		$errormessage.=$Lang::tr{'fwdfw err nosrcip'};
		return $errormessage;
	}

	#check empty fields
	if ($fwdfwsettings{$fwdfwsettings{'grp1'}} eq ''){ $errormessage.=$Lang::tr{'fwdfw err nosrc'}."<br>";}
	#check icmp source
		if ($fwdfwsettings{'USE_SRC_PORT'} eq 'ON' && $fwdfwsettings{'PROT'} eq 'ICMP'){
			$fwdfwsettings{'SRC_PORT'}='';
			&General::readhasharray("${General::swroot}/fwhosts/icmp-types", \%icmptypes);
			foreach my $key (keys %icmptypes){
				if($fwdfwsettings{'ICMP_TYPES'} eq "$icmptypes{$key}[0] ($icmptypes{$key}[1])"){
					$fwdfwsettings{'ICMP_TYPES'}="$icmptypes{$key}[0]";
				}
			}
		}elsif($fwdfwsettings{'USE_SRC_PORT'} eq 'ON' && $fwdfwsettings{'PROT'} eq 'GRE'){
			$fwdfwsettings{'SRC_PORT'}='';
			$fwdfwsettings{'ICMP_TYPES'}='';
		}elsif($fwdfwsettings{'USE_SRC_PORT'} eq 'ON' && $fwdfwsettings{'PROT'} eq 'ESP'){
			$fwdfwsettings{'SRC_PORT'}='';
			$fwdfwsettings{'ICMP_TYPES'}='';
		}elsif($fwdfwsettings{'USE_SRC_PORT'} eq 'ON' && $fwdfwsettings{'PROT'} eq 'AH'){
			$fwdfwsettings{'SRC_PORT'}='';
			$fwdfwsettings{'ICMP_TYPES'}='';	
		}elsif($fwdfwsettings{'USE_SRC_PORT'} eq 'ON' && $fwdfwsettings{'PROT'} ne 'ICMP'){
			$fwdfwsettings{'ICMP_TYPES'}='';
		}else{
			$fwdfwsettings{'ICMP_TYPES'}='';
			$fwdfwsettings{'SRC_PORT'}='';
			$fwdfwsettings{'PROT'}='';
		}

	if($fwdfwsettings{'USE_SRC_PORT'} eq 'ON' && ($fwdfwsettings{'PROT'} eq 'TCP' || $fwdfwsettings{'PROT'} eq 'UDP') && $fwdfwsettings{'SRC_PORT'} ne ''){
		my @parts=split(",",$fwdfwsettings{'SRC_PORT'});
		my @values=();
		foreach (@parts){
			chomp($_);
			if ($_ =~ /^(\d+)\:(\d+)$/) {
				my $check;
				#change dashes with :
				$_=~ tr/-/:/;
				if ($_ eq "*") {
					push(@values,"1:65535");
					$check='on';
				}
				if ($_ =~ /^(\D)\:(\d+)$/) {
					push(@values,"1:$2");
					$check='on';
				}
				if ($_ =~ /^(\d+)\:(\D)$/) {
					push(@values,"$1:65535");
					$check='on'
				}
				$errormessage .= &General::validportrange($_, 'destination');
				if(!$check){
					push (@values,$_);
				}
			}else{
				if (&General::validport($_)){
					push (@values,$_);
				}else{
					
				}
			}
		}
		$fwdfwsettings{'SRC_PORT'}=join("|",@values);
		return $errormessage;
	}
}
sub checktarget
{
	my ($ip,$subnet);

	if ($fwdfwsettings{'tgt_addr'} eq $fwdfwsettings{$fwdfwsettings{'grp2'}} && $fwdfwsettings{'tgt_addr'} ne ''){
		#check if ip with subnet
		if ($fwdfwsettings{'tgt_addr'} =~ /^(.*?)\/(.*?)$/) {
			($ip,$subnet)=split (/\//,$fwdfwsettings{'tgt_addr'});
			$subnet = &General::iporsubtocidr($subnet);
		}
		#check if only ip
		if($fwdfwsettings{'tgt_addr'}=~/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/){
			$ip=$fwdfwsettings{'tgt_addr'};
			$subnet='32';
		}
		#check and form valid IP
		$ip=&General::ip2dec($ip);
		$ip=&General::dec2ip($ip);

		#check if net or broadcast
		my @tmp= split (/\./,$ip);
		if ($tmp[3] eq "0" || ($tmp[3] eq "255"))
		{
			$errormessage=$Lang::tr{'fwhost err hostip'}."<br>";
		}
		$fwdfwsettings{'tgt_addr'}="$ip/$subnet";
				
		if(!&General::validipandmask($fwdfwsettings{'tgt_addr'})){
			$errormessage.=$Lang::tr{'fwdfw err tgt_addr'}."<br>";
		}

	}elsif($fwdfwsettings{'tgt_addr'} eq $fwdfwsettings{$fwdfwsettings{'grp2'}} && $fwdfwsettings{'tgt_addr'} eq ''){
		$errormessage.=$Lang::tr{'fwdfw err notgtip'};
		return $errormessage;
	}

	#check empty fields
	if ($fwdfwsettings{$fwdfwsettings{'grp2'}} eq ''){ $errormessage.=$Lang::tr{'fwdfw err notgt'}."<br>";}

	#check tgt services
	if ($fwdfwsettings{'USESRV'} eq 'ON'){
		if ($fwdfwsettings{'grp3'} eq 'cust_srv'){
			$fwdfwsettings{'TGT_PROT'}='';
			$fwdfwsettings{'ICMP_TGT'}='';
		}
		if ($fwdfwsettings{'grp3'} eq 'cust_srvgrp'){
			$fwdfwsettings{'TGT_PROT'}='';
			$fwdfwsettings{'ICMP_TGT'}='';
			#check target service
			if($fwdfwsettings{$fwdfwsettings{'grp3'}} eq ''){
				$errormessage.=$Lang::tr{'fwdfw err tgt_grp'};
			}
		}
		if ($fwdfwsettings{'grp3'} eq 'TGT_PORT'){
			if ($fwdfwsettings{'TGT_PROT'} eq 'TCP' || $fwdfwsettings{'TGT_PROT'} eq 'UDP'){
				if ($fwdfwsettings{'TGT_PORT'} ne ''){
					my @parts=split(",",$fwdfwsettings{'TGT_PORT'});
					my @values=();
					foreach (@parts){
						chomp($_);
						if ($_ =~ /^(\d+)\:(\d+)$/) {
							my $check;
							#change dashes with :
							$_=~ tr/-/:/;
							if ($_ eq "*") {
								push(@values,"1:65535");
								$check='on';
							}
							if ($_ =~ /^(\D)\:(\d+)$/) {
								push(@values,"1:$2");
								$check='on';
							}
							if ($_ =~ /^(\d+)\:(\D)$/) {
								push(@values,"$1:65535");
								$check='on'
							}
							$errormessage .= &General::validportrange($_, 'destination');
							if(!$check){
								push (@values,$_);
							}
						}else{
							if (&General::validport($_)){
								push (@values,$_);
							}else{
								
							}
						}
					}
					$fwdfwsettings{'TGT_PORT'}=join("|",@values);
				}
			}elsif ($fwdfwsettings{'TGT_PROT'} eq 'GRE'){
					$fwdfwsettings{$fwdfwsettings{'grp3'}} = '';
					$fwdfwsettings{'TGT_PORT'} = '';
					$fwdfwsettings{'ICMP_TGT'} = '';
			}elsif($fwdfwsettings{'TGT_PROT'} eq 'ESP'){
					$fwdfwsettings{$fwdfwsettings{'grp3'}} = '';
					$fwdfwsettings{'TGT_PORT'} = '';
					$fwdfwsettings{'ICMP_TGT'}='';
			}elsif($fwdfwsettings{'TGT_PROT'} eq 'AH'){
					$fwdfwsettings{$fwdfwsettings{'grp3'}} = '';
					$fwdfwsettings{'TGT_PORT'} = '';
					$fwdfwsettings{'ICMP_TGT'}='';
			}elsif ($fwdfwsettings{'TGT_PROT'} eq 'ICMP'){
				$fwdfwsettings{$fwdfwsettings{'grp3'}} = '';
				$fwdfwsettings{'TGT_PORT'} = '';
				&General::readhasharray("${General::swroot}/fwhosts/icmp-types", \%icmptypes);
				foreach my $key (keys %icmptypes){
					
					if ("$icmptypes{$key}[0] ($icmptypes{$key}[1])" eq $fwdfwsettings{'ICMP_TGT'}){
						$fwdfwsettings{'ICMP_TGT'}=$icmptypes{$key}[0];
					}
				}
			}
		}
	}

	#check targetport
	if ($fwdfwsettings{'USESRV'} ne 'ON'){
		$fwdfwsettings{'grp3'}='';
		$fwdfwsettings{$fwdfwsettings{'grp3'}}='';
		$fwdfwsettings{'TGT_PROT'}='';
		$fwdfwsettings{'ICMP_TGT'}='';
	}
	#check timeframe
	if($fwdfwsettings{'TIME'} eq 'ON'){
		if($fwdfwsettings{'TIME_MON'} eq '' && $fwdfwsettings{'TIME_TUE'} eq '' && $fwdfwsettings{'TIME_WED'} eq '' && $fwdfwsettings{'TIME_THU'} eq '' && $fwdfwsettings{'TIME_FRI'} eq '' && $fwdfwsettings{'TIME_SAT'} eq '' && $fwdfwsettings{'TIME_SUN'} eq ''){
			$errormessage=$Lang::tr{'fwdfw err time'};
		}
	}
	return $errormessage;
}
sub checkrule
{
	#check valid remark
	if ($fwdfwsettings{'ruleremark'} ne '' && !&validremark($fwdfwsettings{'ruleremark'})){
		$errormessage.=$Lang::tr{'fwdfw err remark'}."<br>";
	}
	#check if source and target identical
	if ($fwdfwsettings{$fwdfwsettings{'grp1'}} eq $fwdfwsettings{$fwdfwsettings{'grp2'}} && $fwdfwsettings{$fwdfwsettings{'grp1'}} ne 'ALL'){
		$errormessage.=$Lang::tr{'fwdfw err same'};
		return $errormessage;
	}

	#get source and targetip address if possible
	my ($sip,$scidr,$tip,$tcidr);
	($sip,$scidr)=&get_ip("src","grp1");
	($tip,$tcidr)=&get_ip("tgt","grp2");

	#check same iprange in source and target
	if ($sip ne '' && $scidr ne '' && $tip ne '' && $tcidr ne ''){
		my $networkip1=&General::getnetworkip($sip,$scidr);
		my $networkip2=&General::getnetworkip($tip,$tcidr);
		if ($scidr gt $tcidr){
			if ( &General::IpInSubnet($networkip1,$tip,&General::iporsubtodec($tcidr))){
				$errormessage.=$Lang::tr{'fwdfw err samesub'};
			}
		}elsif($scidr eq $tcidr && $scidr eq '32'){
			my ($sbyte1,$sbyte2,$sbyte3,$sbyte4)=split(/\./,$networkip1);
			my ($tbyte1,$tbyte2,$tbyte3,$tbyte4)=split(/\./,$networkip2);
				if ($sbyte1 eq $tbyte1 && $sbyte2 eq $tbyte2 && $sbyte3 eq $tbyte3){
					$hint=$Lang::tr{'fwdfw hint ip1'}."<br>";
					$hint.=$Lang::tr{'fwdfw hint ip2'}." Source: $networkip1/$scidr Target: $networkip2/$tcidr<br>";
				}
		}else{
			if ( &General::IpInSubnet($networkip2,$sip,&General::iporsubtodec($scidr)) ){
			$errormessage.=$Lang::tr{'fwdfw err samesub'};
			}
		}
	}

	#check source and destination protocol if manual
	if( $fwdfwsettings{'USE_SRC_PORT'} eq 'ON' && $fwdfwsettings{'USESRV'} eq 'ON'){
			if($fwdfwsettings{'PROT'} ne $fwdfwsettings{'TGT_PROT'} && $fwdfwsettings{'grp3'} eq 'TGT_PORT'){
			$errormessage.=$Lang::tr{'fwdfw err prot'};
		}
		#check source and destination protocol if source manual and dest servicegrp
		if ($fwdfwsettings{'grp3'} eq 'cust_srv'){
			&General::readhasharray("$configsrv", \%customservice);
			foreach my $key (sort keys %customservice){
				if($customservice{$key}[0] eq $fwdfwsettings{$fwdfwsettings{'grp3'}}){
					if ($customservice{$key}[2] ne $fwdfwsettings{'PROT'}){
						$errormessage.=$Lang::tr{'fwdfw err prot'};
						last;
					}
				}
			}
		}
	}
}
sub get_ip
{
	my $val=shift;
	my $grp =shift;
	my $a;
	my $b;
	&General::readhash("/var/ipfire/ethernet/settings", \%netsettings);
	if ($fwdfwsettings{$grp} ne $Lang::tr{'fwhost any'}){
		if ($fwdfwsettings{$grp} eq $val.'_addr'){
			($a,$b)   = split (/\//, $fwdfwsettings{$fwdfwsettings{$grp}});
		}elsif($fwdfwsettings{$grp} eq 'std_net_'.$val){
			if ($fwdfwsettings{$fwdfwsettings{$grp}} =~ /Gr/i){
				$a=$netsettings{'GREEN_NETADDRESS'};
				$b=&General::iporsubtocidr($netsettings{'GREEN_NETMASK'});
			}elsif($fwdfwsettings{$fwdfwsettings{$grp}} =~ /Ora/i){
				$a=$netsettings{'ORANGE_NETADDRESS'};
				$b=&General::iporsubtocidr($netsettings{'ORANGE_NETMASK'});
			}elsif($fwdfwsettings{$fwdfwsettings{$grp}} =~ /Bl/i){
				$a=$netsettings{'BLUE_NETADDRESS'};
				$b=&General::iporsubtocidr($netsettings{'BLUE_NETMASK'});
			}elsif($fwdfwsettings{$fwdfwsettings{$grp}} =~ /OpenVPN/i){
				&General::readhash("$configovpn",\%ovpnsettings);
				($a,$b)   = split (/\//, $ovpnsettings{'DOVPN_SUBNET'});
				$b=&General::iporsubtocidr($b);
			}
		}elsif($fwdfwsettings{$grp} eq 'cust_net_'.$val){
			&General::readhasharray("$confignet", \%customnetwork);
			foreach my $key (keys %customnetwork){
				if($customnetwork{$key}[0] eq $fwdfwsettings{$fwdfwsettings{$grp}}){
					$a=$customnetwork{$key}[1];
					$b=&General::iporsubtocidr($customnetwork{$key}[2]);
				}
			}
		}elsif($fwdfwsettings{$grp} eq 'cust_host_'.$val){
			&General::readhasharray("$confighost", \%customhost);
			foreach my $key (keys %customhost){
				if($customhost{$key}[0] eq $fwdfwsettings{$fwdfwsettings{$grp}}){
					if ($customhost{$key}[1] eq 'ip'){
						($a,$b)=split (/\//,$customhost{$key}[2]);
						$b=&General::iporsubtocidr($b);
					}else{
						if ($grp eq 'grp2'){
							$errormessage=$Lang::tr{'fwdfw err tgt_mac'};
						}
					}
				}
			}
		}
	}
	return $a,$b;
}
sub newrule
{
	&error;
	&General::setup_default_networks(\%defaultNetworks);
	#read all configfiles
	&General::readhasharray("$configccdnet", \%ccdnet);
	&General::readhasharray("$confignet", \%customnetwork);
	&General::readhasharray("$configccdhost", \%ccdhost);
	&General::readhasharray("$confighost", \%customhost);
	&General::readhasharray("$configccdhost", \%ccdhost);
	&General::readhasharray("$configgrp", \%customgrp);
	&General::readhasharray("$configipsec", \%ipsecconf);
	&General::get_aliases(\%aliases);
	my %checked=();
	my $helper;
	my $sum=0;
	if($fwdfwsettings{'config'} eq ''){$fwdfwsettings{'config'}=$configfwdfw;}
	my $config=$fwdfwsettings{'config'};
	my %hash=();
	$checked{'grp1'}{$fwdfwsettings{'grp1'}} 				= 'CHECKED';
	$checked{'grp2'}{$fwdfwsettings{'grp2'}} 				= 'CHECKED';
	$checked{'grp3'}{$fwdfwsettings{'grp3'}} 				= 'CHECKED';
	$checked{'USE_SRC_PORT'}{$fwdfwsettings{'USE_SRC_PORT'}} = 'CHECKED';
	$checked{'USESRV'}{$fwdfwsettings{'USESRV'}} 			= 'CHECKED';
	$checked{'ACTIVE'}{$fwdfwsettings{'ACTIVE'}} 			= 'CHECKED';
	$checked{'LOG'}{$fwdfwsettings{'LOG'}} 					= 'CHECKED';
	$checked{'TIME'}{$fwdfwsettings{'TIME'}} 				= 'CHECKED';
	$checked{'TIME_MON'}{$fwdfwsettings{'TIME_MON'}} 		= 'CHECKED';
	$checked{'TIME_TUE'}{$fwdfwsettings{'TIME_TUE'}} 		= 'CHECKED';
	$checked{'TIME_WED'}{$fwdfwsettings{'TIME_WED'}} 		= 'CHECKED';
	$checked{'TIME_THU'}{$fwdfwsettings{'TIME_THU'}} 		= 'CHECKED';
	$checked{'TIME_FRI'}{$fwdfwsettings{'TIME_FRI'}} 		= 'CHECKED';
	$checked{'TIME_SAT'}{$fwdfwsettings{'TIME_SAT'}} 		= 'CHECKED';
	$checked{'TIME_SUN'}{$fwdfwsettings{'TIME_SUN'}} 		= 'CHECKED';
	$selected{'TIME_FROM'}{$fwdfwsettings{'TIME_FROM'}}		= 'selected';
	$selected{'TIME_TO'}{$fwdfwsettings{'TIME_TO'}}			= 'selected';
	$selected{'ipfire'}{$fwdfwsettings{$fwdfwsettings{'grp2'}}} ='selected';
	#check if update and get values
	if($fwdfwsettings{'updatefwrule'} eq 'on' || $fwdfwsettings{'copyfwrule'} eq 'on' && !$errormessage){
		&General::readhasharray("$config", \%hash);
		foreach my $key (sort keys %hash){
			$sum++;
			if ($key eq $fwdfwsettings{'key'}){
				$fwdfwsettings{'oldrulenumber'}			= $fwdfwsettings{'key'};
				$fwdfwsettings{'RULE_ACTION'}			= $hash{$key}[0];
				$fwdfwsettings{'ACTIVE'}				= $hash{$key}[2];
				$fwdfwsettings{'grp1'}					= $hash{$key}[3];   
				$fwdfwsettings{$fwdfwsettings{'grp1'}}	= $hash{$key}[4];   
				$fwdfwsettings{'grp2'}					= $hash{$key}[5];   
				$fwdfwsettings{$fwdfwsettings{'grp2'}}	= $hash{$key}[6];   
				$fwdfwsettings{'USE_SRC_PORT'}			= $hash{$key}[7];
				$fwdfwsettings{'PROT'}					= $hash{$key}[8];
			    $fwdfwsettings{'ICMP_TYPES'}			= $hash{$key}[9];
			    $fwdfwsettings{'SRC_PORT'}				= $hash{$key}[10];
			    $fwdfwsettings{'USESRV'}				= $hash{$key}[11];
			    $fwdfwsettings{'TGT_PROT'}				= $hash{$key}[12];
			    $fwdfwsettings{'ICMP_TGT'}				= $hash{$key}[13];
			    $fwdfwsettings{'grp3'}					= $hash{$key}[14];
			    $fwdfwsettings{$fwdfwsettings{'grp3'}}	= $hash{$key}[15];
			    $fwdfwsettings{'ruleremark'}			= $hash{$key}[16];
			    $fwdfwsettings{'LOG'}					= $hash{$key}[17];
			    $fwdfwsettings{'TIME'}					= $hash{$key}[18];
				$fwdfwsettings{'TIME_MON'}				= $hash{$key}[19];
				$fwdfwsettings{'TIME_TUE'}				= $hash{$key}[20];
				$fwdfwsettings{'TIME_WED'}				= $hash{$key}[21];
				$fwdfwsettings{'TIME_THU'}				= $hash{$key}[22];
				$fwdfwsettings{'TIME_FRI'}				= $hash{$key}[23];
				$fwdfwsettings{'TIME_SAT'}				= $hash{$key}[24];
				$fwdfwsettings{'TIME_SUN'}				= $hash{$key}[25];
				$fwdfwsettings{'TIME_FROM'}				= $hash{$key}[26];
				$fwdfwsettings{'TIME_TO'}				= $hash{$key}[27];
				$checked{'grp1'}{$fwdfwsettings{'grp1'}} 				= 'CHECKED';
				$checked{'grp2'}{$fwdfwsettings{'grp2'}} 				= 'CHECKED';
				$checked{'grp3'}{$fwdfwsettings{'grp3'}} 				= 'CHECKED';
				$checked{'USE_SRC_PORT'}{$fwdfwsettings{'USE_SRC_PORT'}} = 'CHECKED';
				$checked{'USESRV'}{$fwdfwsettings{'USESRV'}} 			= 'CHECKED';
				$checked{'ACTIVE'}{$fwdfwsettings{'ACTIVE'}} 			= 'CHECKED';
				$checked{'LOG'}{$fwdfwsettings{'LOG'}} 					= 'CHECKED';
				$checked{'TIME'}{$fwdfwsettings{'TIME'}} 				= 'CHECKED';
				$checked{'TIME_MON'}{$fwdfwsettings{'TIME_MON'}} 		= 'CHECKED';
				$checked{'TIME_TUE'}{$fwdfwsettings{'TIME_TUE'}} 		= 'CHECKED';
				$checked{'TIME_WED'}{$fwdfwsettings{'TIME_WED'}} 		= 'CHECKED';
				$checked{'TIME_THU'}{$fwdfwsettings{'TIME_THU'}} 		= 'CHECKED';
				$checked{'TIME_FRI'}{$fwdfwsettings{'TIME_FRI'}} 		= 'CHECKED';
				$checked{'TIME_SAT'}{$fwdfwsettings{'TIME_SAT'}} 		= 'CHECKED';
				$checked{'TIME_SUN'}{$fwdfwsettings{'TIME_SUN'}} 		= 'CHECKED';
				$selected{'TIME_FROM'}{$fwdfwsettings{'TIME_FROM'}}		= 'selected';
				$selected{'TIME_TO'}{$fwdfwsettings{'TIME_TO'}}			= 'selected';
				$selected{'ipfire'}{$fwdfwsettings{$fwdfwsettings{'grp2'}}} ='selected';
			}
		}
		$fwdfwsettings{'oldgrp1a'}=$fwdfwsettings{'grp1'};
		$fwdfwsettings{'oldgrp1b'}=$fwdfwsettings{$fwdfwsettings{'grp1'}};
		$fwdfwsettings{'oldgrp2a'}=$fwdfwsettings{'grp2'};
		$fwdfwsettings{'oldgrp2b'}=$fwdfwsettings{$fwdfwsettings{'grp2'}};
		$fwdfwsettings{'oldgrp3a'}=$fwdfwsettings{'grp3'};
		$fwdfwsettings{'oldgrp3b'}=$fwdfwsettings{$fwdfwsettings{'grp3'}};
		$fwdfwsettings{'oldusesrv'}=$fwdfwsettings{'USESRV'};
		$fwdfwsettings{'oldruleremark'}=$fwdfwsettings{'ruleremark'};
	}else{
		$fwdfwsettings{'ACTIVE'}='ON';
		$checked{'ACTIVE'}{$fwdfwsettings{'ACTIVE'}} = 'CHECKED';
	}

	&Header::openbox('100%', 'left', $Lang::tr{'fwdfw addrule'});

print <<END;
	<form method="post">
	<table border='0'>
	<tr><td nowrap>$Lang::tr{'fwdfw rule action'}</td><td><select name='RULE_ACTION'>
END
	foreach ("ACCEPT","DROP","REJECT")
	{
		if($fwdfwsettings{'updatefwrule'} eq 'on'){
			print"<option ";
			print "selected='selected'" if ($fwdfwsettings{'RULE_ACTION'} eq $_);
			print">$_</option>";
		}else{
			if($fwdfwsettings{'POLICY'} eq 'MODE2'){
				$fwdfwsettings{'RULE_ACTION'} = 'DROP';
			}
	
			if ($_ eq $fwdfwsettings{'RULE_ACTION'})
			{
				print"<option selected>$_</option>";
			}else{
				print"<option>$_</option>";
			}
		}
	}
	print"</select></td></tr></table><hr>";	

	&Header::closebox();
	&Header::openbox('100%', 'left', $Lang::tr{'fwdfw source'});
	#------SOURCE-------------------------------------------------------
	print<<END;
		<table width='100%' border='0'>
		<tr><td width='1%'><input type='radio' name='grp1' value='src_addr'  checked></td><td colspan='5'>$Lang::tr{'fwdfw sourceip'}<input type='TEXT' name='src_addr' value='$fwdfwsettings{'src_addr'}' ></td></tr>
		<tr><td colspan='7'><hr style='border:dotted #BFBFBF; border-width:1px 0 0 0 ; ' /></td></tr>
		<tr><td width='1%'><input type='radio' name='grp1' value='std_net_src' $checked{'grp1'}{'std_net_src'}></td><td nowrap='nowrap' width='12%'>$Lang::tr{'fwhost stdnet'}</td><td width='13%'><select name='std_net_src' style='min-width:185px;'>
END
		foreach my $network (sort keys %defaultNetworks)
		{
			next if($defaultNetworks{$network}{'LOCATION'} eq "IPCOP");
			next if($defaultNetworks{$network}{'NAME'} eq "RED");
			print "<option value='$defaultNetworks{$network}{'NAME'}'";
			print " selected='selected'" if ($fwdfwsettings{$fwdfwsettings{'grp1'}} eq $defaultNetworks{$network}{'NAME'});
			print ">$network</option>";
		}
		print<<END;
		</select></td><td width='1%'><input type='radio' name='grp1' value='ovpn_net_src'  $checked{'grp1'}{'ovpn_net_src'}></td><td nowrap='nowrap' width='16%'>$Lang::tr{'fwhost ccdnet'}</td><td nowrap='nowrap' width='1%'><select name='ovpn_net_src' style='min-width:185px;'>
END
		&fillselect(\%ccdnet,$fwdfwsettings{$fwdfwsettings{'grp1'}});
		print<<END;
		</select></td></tr>
		<tr><td><input type='radio' name='grp1' value='cust_net_src' $checked{'grp1'}{'cust_net_src'}></td><td>$Lang::tr{'fwhost cust net'}</td><td><select name='cust_net_src' style='min-width:185px;'>
END
		&fillselect(\%customnetwork,$fwdfwsettings{$fwdfwsettings{'grp1'}});
		print<<END;
		</select></td><td width='1%'><input type='radio' name='grp1' value='ovpn_host_src' $checked{'grp1'}{'ovpn_host_src'}></td><td nowrap='nowrap' width='16%'>$Lang::tr{'fwhost ccdhost'}</td><td nowrap='nowrap' width='1%'><select name='ovpn_host_src' style='min-width:185px;'>
END
		foreach my $key (sort { uc($ccdhost{$a}[0]) cmp uc($ccdhost{$b}[0]) } keys %ccdhost)
		{
			if ($ccdhost{$key}[33] ne ''){
				
				print "<option value='$ccdhost{$key}[1]'";
				print "selected='selected'" if ($fwdfwsettings{$fwdfwsettings{'grp1'}} eq $ccdhost{$key}[1]);
				print ">$ccdhost{$key}[1]</option>";
			}
		}
		print<<END;
		</select></td></tr>
		<tr><td valign='top'><input type='radio' name='grp1' value='cust_host_src' $checked{'grp1'}{'cust_host_src'}></td><td>$Lang::tr{'fwhost cust addr'}</td><td><select name='cust_host_src' style='min-width:185px;'>
END
		&fillselect(\%customhost,$fwdfwsettings{$fwdfwsettings{'grp1'}});
		print<<END;
		</select></td><td width='1%'><input type='radio' name='grp1' value='ovpn_n2n_src' $checked{'grp1'}{'ovpn_n2n_src'}></td><td >$Lang::tr{'fwhost ovpn_n2n'}</td><td colspan='3'><select name='ovpn_n2n_src' style='min-width:185px;'>
END
		foreach my $key (sort { uc($ccdhost{$a}[0]) cmp uc($ccdhost{$b}[0]) } keys %ccdhost) {
			if($ccdhost{$key}[3] eq 'net'){
				print"<option ";
				print " selected='selected'" if ($fwdfwsettings{$fwdfwsettings{'grp1'}} eq $ccdhost{$key}[1]);
				print ">$ccdhost{$key}[1]</option>";
			}
		}
		print<<END;
		</select></td></tr>

		<tr><td valign='top'><input type='radio' name='grp1' value='cust_grp_src' $checked{'grp1'}{'cust_grp_src'}></td><td >$Lang::tr{'fwhost cust grp'}</td><td><select name='cust_grp_src' style='min-width:185px;'>
END
		foreach my $key (sort { uc($customgrp{$a}[0]) cmp uc($customgrp{$b}[0]) } keys %customgrp) {
			if($helper ne $customgrp{$key}[0]){
				print"<option ";
				print "selected='selected' " if ($fwdfwsettings{$fwdfwsettings{'grp1'}} eq $customgrp{$key}[0]);
				print ">$customgrp{$key}[0]</option>";
			}
			$helper=$customgrp{$key}[0];
		}
		print<<END;
		</select></td>
		<td valign='top'><input type='radio' name='grp1' value='ipsec_net_src' $checked{'grp1'}{'ipsec_net_src'}></td><td >$Lang::tr{'fwhost ipsec net'}</td><td><select name='ipsec_net_src' style='min-width:185px;'>
END
		foreach my $key (sort { uc($ipsecconf{$a}[1]) cmp uc($ipsecconf{$b}[1]) } keys %ipsecconf) {
			if ($ipsecconf{$key}[3] eq 'net'){
				print "<option ";
				print "selected='selected'" if ($fwdfwsettings{$fwdfwsettings{'grp1'}} eq $ipsecconf{$key}[1]);
				print ">$ipsecconf{$key}[1]</option>";
			}
		}
		#sourceport
		print<<END;
		</select></td></tr>
END

#		<td valign='top'><input type='radio' name='grp1' value='ipsec_host_src' $checked{'grp1'}{'ipsec_host_src'}></td><td >$Lang::tr{'fwhost ipsec host'}</td><td><select name='ipsec_host_src' style='min-width:185px;'>
#END
#		foreach my $key (sort { uc($ipsecconf{$a}[1]) cmp uc($ipsecconf{$b}[1]) } keys %ipsecconf) {
#			if ($ipsecconf{$key}[3] eq 'host'){
#				print "<option ";
#				print "selected='selected'" if($fwdfwsettings{$fwdfwsettings{'grp1'}} eq $ipsecconf{$key}[1]);
#				print ">$ipsecconf{$key}[1]</option>";
#			}
#		}
		print<<END;
		<tr><td colspan='8'><hr style='border:dotted #BFBFBF; border-width:1px 0 0 0 ; ' /></td></tr></table>
		<table width='100%' border='0'>
		<tr><td width='1%'><input type='checkbox' name='USE_SRC_PORT' value='ON' $checked{'USE_SRC_PORT'}{'ON'}></td><td width='51%' colspan='3'>$Lang::tr{'fwdfw use srcport'}</td>
		<td width='15%' nowrap='nowrap'>$Lang::tr{'fwdfw man port'}</td><td><select name='PROT'>
END
		foreach ("TCP","UDP","GRE","ESP","AH","ICMP")
		{
			if ($_ eq $fwdfwsettings{'PROT'})
			{
				print"<option selected>$_</option>";
			}else{
				print"<option>$_</option>";
			}
		}
		$fwdfwsettings{'SRC_PORT'}=~ s/\|/,/g;
		print<<END;
		</select></td><td align='right'><input type='text' name='SRC_PORT' value='$fwdfwsettings{'SRC_PORT'}' maxlength='20' size='18' ></td></tr>
		<tr><td></td><td></td><td></td><td></td><td nowrap='nowrap'>$Lang::tr{'fwhost icmptype'}</td><td colspan='2'><select name='ICMP_TYPES'>
END
		&General::readhasharray("${General::swroot}/fwhosts/icmp-types", \%icmptypes);
		print"<option>All ICMP-Types</option>";
		foreach my $key (sort { uc($icmptypes{$a}[0]) cmp uc($icmptypes{$b}[0]) } keys %icmptypes){
			if($fwdfwsettings{'ICMP_TYPES'} eq "$icmptypes{$key}[0]"){
				print"<option selected>$icmptypes{$key}[0] ($icmptypes{$key}[1])</option>";
			}else{
				print"<option>$icmptypes{$key}[0] ($icmptypes{$key}[1])</option>";
			}
		}
		print<<END;
		</select></td></tr></table><hr>
END
		&Header::closebox();

		#---TARGET------------------------------------------------------
		&Header::openbox('100%', 'left', $Lang::tr{'fwdfw target'});
		print<<END;
		<table width='100%' border='0'>	
		<tr><td width='1%'><input type='radio' name='grp2' value='tgt_addr'  checked></td><td colspan='2'>$Lang::tr{'fwdfw targetip'}<input type='TEXT' name='tgt_addr' value='$fwdfwsettings{'tgt_addr'}' size='16'><td><input type='radio' name='grp2' value='ipfire'  $checked{'grp2'}{'ipfire'}></td><td><b>IPFire ($Lang::tr{'external access'})</b></td><td><select name='ipfire' style='min-width:185px;'>
END
		print "<option value='Default IP' $selected{'ipfire'}{'Default IP'}>Default IP</option>";

		foreach my $alias (sort keys %aliases)
		{
			print "<option value='$alias' $selected{'ipfire'}{$alias}>$alias</option>";
		}

		print<<END;
		</td></tr>
		<tr><td colspan='7'><hr style='border:dotted #BFBFBF; border-width:1px 0 0 0 ; ' /></td></tr>
		<tr><td width='1%'><input type='radio' name='grp2' value='std_net_tgt' $checked{'grp2'}{'std_net_tgt'}></td><td nowrap='nowrap' width='12%'>$Lang::tr{'fwhost stdnet'}</td><td width='13%'><select name='std_net_tgt' style='min-width:185px;'>
END
		foreach my $network (sort keys %defaultNetworks)
		{
			print "<option value='$defaultNetworks{$network}{'NAME'}'";
			print " selected='selected'" if ($fwdfwsettings{$fwdfwsettings{'grp2'}} eq $defaultNetworks{$network}{'NAME'});
			print ">$network</option>";
		}
		print<<END;
		</select></td><td width='1%'><input type='radio' name='grp2' value='ovpn_net_tgt'  $checked{'grp2'}{'ovpn_net_tgt'}></td><td nowrap='nowrap' width='16%'>$Lang::tr{'fwhost ccdnet'}</td><td nowrap='nowrap' width='1%'><select name='ovpn_net_tgt' style='min-width:185px;'>
END
		&fillselect(\%ccdnet,$fwdfwsettings{$fwdfwsettings{'grp2'}});
		print<<END;
		</select></td></tr>
		<tr><td><input type='radio' name='grp2' value='cust_net_tgt' $checked{'grp2'}{'cust_net_tgt'}></td><td>$Lang::tr{'fwhost cust net'}</td><td><select name='cust_net_tgt' style='min-width:185px;'>
END
		&fillselect(\%customnetwork,$fwdfwsettings{$fwdfwsettings{'grp2'}});
		print<<END;
		</select></td><td width='1%'><input type='radio' name='grp2' value='ovpn_host_tgt' $checked{'grp2'}{'ovpn_host_tgt'}></td><td nowrap='nowrap' width='16%'>$Lang::tr{'fwhost ccdhost'}</td><td nowrap='nowrap' width='1%'><select name='ovpn_host_tgt' style='min-width:185px;'>
END
		foreach my $key (sort { uc($ccdhost{$a}[0]) cmp uc($ccdhost{$b}[0]) } keys %ccdhost)
		{
			if ($ccdhost{$key}[33] ne ''){
				print "<option value='$ccdhost{$key}[1]' ";
				print "selected='selected'" if ($fwdfwsettings{$fwdfwsettings{'grp2'}} eq $ccdhost{$key}[33]);
				print ">$ccdhost{$key}[1]</option>";
			}
		}
		print<<END;
		</select></td></tr>
		<tr><td valign='top'><input type='radio' name='grp2' value='cust_host_tgt' $checked{'grp2'}{'cust_host_tgt'}></td><td>$Lang::tr{'fwhost cust addr'}</td><td><select name='cust_host_tgt' style='min-width:185px;'>
END
		&fillselect(\%customhost,$fwdfwsettings{$fwdfwsettings{'grp2'}});
		print<<END;
		</select></td><td width='1%'><input type='radio' name='grp2' value='ovpn_n2n_tgt' $checked{'grp2'}{'ovpn_n2n_tgt'}></td><td >$Lang::tr{'fwhost ovpn_n2n'}</td><td colspan='3'><select name='ovpn_n2n_tgt' style='min-width:185px;'>
END
		foreach my $key (sort { uc($ccdhost{$a}[0]) cmp uc($ccdhost{$b}[0]) } keys %ccdhost) {
			if($ccdhost{$key}[3] eq 'net'){
				print "<option ";
				print "selected='selected'" if($fwdfwsettings{$fwdfwsettings{'grp2'}} eq $ccdhost{$key}[1]);
				print ">$ccdhost{$key}[1]</option>";
			}
		}
		print<<END;
		</select></td></tr>
		<tr><td valign='top'><input type='radio' name='grp2' value='cust_grp_tgt' $checked{'grp2'}{'cust_grp_tgt'}></td><td >$Lang::tr{'fwhost cust grp'}</td><td><select name='cust_grp_tgt' style='min-width:185px;'>
END
		$helper='';
		foreach my $key (sort { uc($customgrp{$a}[0]) cmp uc($customgrp{$b}[0]) } keys %customgrp) {
			if($helper ne $customgrp{$key}[0]){
				print"<option ";
				print"selected='selected'" if ($fwdfwsettings{$fwdfwsettings{'grp2'}} eq  $customgrp{$key}[0]);
				print">$customgrp{$key}[0]</option>";
			}
			$helper=$customgrp{$key}[0];
		}
		print<<END;
		</select></td>
		<td valign='top'><input type='radio' name='grp2' value='ipsec_net_tgt' $checked{'grp2'}{'ipsec_net_tgt'}></td><td >$Lang::tr{'fwhost ipsec net'}</td><td><select name='ipsec_net_tgt' style='min-width:185px;'>
END
		foreach my $key (sort  { uc($ipsecconf{$a}[1]) cmp uc($ipsecconf{$b}[1]) } keys %ipsecconf) {
			if ($ipsecconf{$key}[3] eq 'net'){
				print"<option ";
				print"selected='selected'" if ($fwdfwsettings{$fwdfwsettings{'grp2'}} eq $ipsecconf{$key}[1]);
				print">$ipsecconf{$key}[1]</option>";
			}
		}
		print<<END;
		</select></td></tr>
END
#		<td valign='top'><input type='radio' name='grp2' value='ipsec_host_tgt' $checked{'grp2'}{'ipsec_host_tgt'}></td><td >$Lang::tr{'fwhost ipsec host'}</td><td><select name='ipsec_host_tgt' style='min-width:185px;'>
#END
#		foreach my $key (sort { uc($ipsecconf{$a}[1]) cmp uc($ipsecconf{$b}[1]) } keys %ipsecconf) {
#			if ($ipsecconf{$key}[3] eq 'host'){
#				print"<option ";
#				print"selected='Selected'" if ($fwdfwsettings{$fwdfwsettings{'grp2'}} eq $ipsecconf{$key}[1]);
#				print">$ipsecconf{$key}[1]</option>";
#			}
#		}
		print<<END;
		</table>
		<b>$Lang::tr{'fwhost attention'}:</b><br>
		$Lang::tr{'fwhost macwarn'}<br><hr style='border:dotted #BFBFBF; border-width:1px 0 0 0 ; '></hr><br>

		<table width='100%' border='0'>
		<tr><td width='1%'><input type='checkbox' name='USESRV' value='ON' $checked{'USESRV'}{'ON'} ></td><td width='48%'>$Lang::tr{'fwdfw use srv'}</td><td width='1%'><input type='radio' name='grp3' value='cust_srv' checked></td><td nowrap='nowrap'>$Lang::tr{'fwhost cust service'}</td><td width='1%' colspan='2'><select name='cust_srv'style='min-width:230px;' >
END
		&General::readhasharray("$configsrv", \%customservice);
		foreach my $key (sort { uc($customservice{$a}[0]) cmp uc($customservice{$b}[0]) } keys %customservice){
			print"<option ";
			print"selected='selected'" if ($fwdfwsettings{$fwdfwsettings{'grp3'}} eq $customservice{$key}[0]);
			print"value='$customservice{$key}[0]'>$customservice{$key}[0]</option>";
		}	
		print<<END;
		</select></td></tr>
		<tr><td colspan='2'></td><td><input type='radio' name='grp3' value='cust_srvgrp' $checked{'grp3'}{'cust_srvgrp'}></td><td nowrap='nowrap'>$Lang::tr{'fwhost cust srvgrp'}:</td><td colspan='2'><select name='cust_srvgrp'style='min-width:230px;' >
END
		&General::readhasharray("$configsrvgrp", \%customservicegrp);
		my $helper;
		foreach my $key (sort { uc($customservicegrp{$a}[0]) cmp uc($customservicegrp{$b}[0]) } keys %customservicegrp){
			if ($helper ne $customservicegrp{$key}[0]){
				print"<option ";
				print"selected='selected'" if ($fwdfwsettings{$fwdfwsettings{'grp3'}} eq $customservicegrp{$key}[0]);
				print">$customservicegrp{$key}[0]</option>";
			}
			$helper=$customservicegrp{$key}[0];
		}	
		print<<END;
		</select></td></tr>
		<tr><td colspan='2'></td><td><input type='radio' name='grp3' value='TGT_PORT' $checked{'grp3'}{'TGT_PORT'}></td><td>$Lang::tr{'fwdfw man port'}</td><td><select name='TGT_PROT'>
END
		foreach ("TCP","UDP","GRE","ESP","AH","ICMP")
		{
			if ($_ eq $fwdfwsettings{'TGT_PROT'})
			{
				print"<option selected>$_</option>";
			}else{
				print"<option>$_</option>";
			}
		}
		$fwdfwsettings{'TGT_PORT'} =~ s/\|/,/g;
		print<<END;
		</select></td><td align='right'><input type='text' name='TGT_PORT' value='$fwdfwsettings{'TGT_PORT'}' maxlength='20' size='18' ></td></tr>
		<tr><td colspan='2'></td><td></td><td>$Lang::tr{'fwhost icmptype'}</td><td colspan='2'><select name='ICMP_TGT'>
END
		&General::readhasharray("${General::swroot}/fwhosts/icmp-types", \%icmptypes);
		print"<option>All ICMP-Types</option>";
		foreach my $key (sort { uc($icmptypes{$a}[0]) cmp uc($icmptypes{$b}[0]) }keys %icmptypes){
			if($fwdfwsettings{'ICMP_TGT'} eq "$icmptypes{$key}[0]"){
				print"<option selected>$icmptypes{$key}[0] ($icmptypes{$key}[1])</option>";
			}else{
				print"<option>$icmptypes{$key}[0] ($icmptypes{$key}[1])</option>";
			}
		}
		print<<END;
		</select></td></tr>
		</table><hr><br><br>

END
		#---Activate/logging/remark-------------------------------------
		&Header::openbox('100%', 'left', $Lang::tr{'fwdfw additional'});
		print<<END;
		<table width='100%' border='0'>
		<tr><td width='12%'>$Lang::tr{'remark'}:</td><td align='left'><input type='text' name='ruleremark' size='40' maxlength='255' value='$fwdfwsettings{'ruleremark'}'></td></tr>
END
		if($fwdfwsettings{'updatefwrule'} eq 'on' || $fwdfwsettings{'copyfwrule'} eq 'on'){
			print "<tr><td width='12%'>$Lang::tr{'fwdfw rulepos'}:</td><td><select name='rulepos' >";
			for (my $count =1; $count <= $sum; $count++){ 
				print"<option value='$count' ";
				print"selected='selected'" if($fwdfwsettings{'oldrulenumber'} eq $count);
				print">$count</option>";
			}
			print"</select></td></tr>";
		}else{
			print "<tr><td width='12%'>$Lang::tr{'fwdfw rulepos'}:</td><td><input type='text' name='rulepos' size='2'></td></tr>";
		}

		print<<END;
		</table><table width='100%'>
		<tr><td width='1%'><input type='checkbox' name='ACTIVE' value='ON' $checked{'ACTIVE'}{'ON'}></td><td>$Lang::tr{'fwdfw rule activate'}</td></tr>
		<tr><td width='1%'><input type='checkbox' name='LOG' value='ON'  $checked{'LOG'}{'ON'}  ></td><td>$Lang::tr{'fwdfw log rule'}</td></tr>
		</table><hr><br>
END
		&Header::closebox();
		#---ADD TIMEFRAME-----------------------------------------------
		&Header::openbox('100%', 'left', $Lang::tr{'fwdfw timeframe'});
		print<<END;
		<table width='70%' border='0'>
		<tr><td width='1%'><input type='checkbox' name='TIME' value='ON' $checked{'TIME'}{'ON'}></td><td colspan='4'>$Lang::tr{'fwdfw timeframe'}</td></tr>
		<tr><td colspan='7'>&nbsp</td></tr>
		<tr>
			<td  align='left'>$Lang::tr{'time'}:</td>
			<td width='30%' align='left'>$Lang::tr{'advproxy monday'} $Lang::tr{'advproxy tuesday'} $Lang::tr{'advproxy wednesday'} $Lang::tr{'advproxy thursday'} $Lang::tr{'advproxy friday'} $Lang::tr{'advproxy saturday'} $Lang::tr{'advproxy sunday'}</td>
			<td width='15%' align='left'>$Lang::tr{'advproxy from'}</td>
			<td width='15%' align='left'>$Lang::tr{'advproxy to'}</td>
		</tr>
		<tr>
			<td  align='right'></td>
			<td width='30%' align='left'>
				<input type='checkbox' name='TIME_MON' value='on' $checked{'TIME_MON'}{'on'} />
				<input type='checkbox' name='TIME_TUE' value='on' $checked{'TIME_TUE'}{'on'} />
				<input type='checkbox' name='TIME_WED' value='on' $checked{'TIME_WED'}{'on'} />
				<input type='checkbox' name='TIME_THU' value='on' $checked{'TIME_THU'}{'on'} />
				<input type='checkbox' name='TIME_FRI' value='on' $checked{'TIME_FRI'}{'on'} />
				<input type='checkbox' name='TIME_SAT' value='on' $checked{'TIME_SAT'}{'on'} />
				<input type='checkbox' name='TIME_SUN' value='on' $checked{'TIME_SUN'}{'on'} />
			</td>
			<td><select name='TIME_FROM'>
END
		for (my $i=0;$i<=23;$i++) {
			$i = sprintf("%02s",$i);
			for (my $j=0;$j<=45;$j+=15) {
				$j = sprintf("%02s",$j);
				my $time = $i.":".$j;
				print "\t\t\t\t\t<option $selected{'TIME_FROM'}{$time}>$i:$j</option>\n";
			}
		}
		print<<END;	
			</select></td>
			<td><select name='TIME_TO'>
END
		for (my $i=0;$i<=23;$i++) {
			$i = sprintf("%02s",$i);
			for (my $j=0;$j<=45;$j+=15) {
				$j = sprintf("%02s",$j);
				my $time = $i.":".$j;
				print "\t\t\t\t\t<option $selected{'TIME_TO'}{$time}>$i:$j</option>\n";
			}
		}
		print<<END;
		</select></td></tr>
		</table><hr>
END
		&Header::closebox();
		#---ACTION------------------------------------------------------
		if($fwdfwsettings{'updatefwrule'} ne 'on'){
			print<<END;
			<table border='0' width='100%'>
			<tr><td align='right'><input type='submit' value='$Lang::tr{'add'}' style='min-width:100px;' />
			<input type='hidden' name='config' value='$config' >
			<input type='hidden' name='ACTION' value='saverule' >
			</form><form method='post' style='display:inline'><input type='submit' value='$Lang::tr{'fwhost back'}' style='min-width:100px;'><input type='hidden' name='ACTION' value'reset'></td></td>
			</table></form>
END
		}else{
			print<<END;
			<table border='0' width='100%'>
			<tr><td align='right'><input type='submit' value='$Lang::tr{'fwdfw change'}' style='min-width:100px;' /><input type='hidden' name='updatefwrule' value='$fwdfwsettings{'updatefwrule'}'><input type='hidden' name='key' value='$fwdfwsettings{'key'}'>
			<input type='hidden' name='oldgrp1a' value='$fwdfwsettings{'oldgrp1a'}' />
			<input type='hidden' name='oldgrp1b' value='$fwdfwsettings{'oldgrp1b'}' />
			<input type='hidden' name='oldgrp2a' value='$fwdfwsettings{'oldgrp2a'}' />
			<input type='hidden' name='oldgrp2b' value='$fwdfwsettings{'oldgrp2b'}' />
			<input type='hidden' name='oldgrp3a' value='$fwdfwsettings{'oldgrp3a'}' />
			<input type='hidden' name='oldgrp3b' value='$fwdfwsettings{'oldgrp3b'}' />
			<input type='hidden' name='oldusesrv' value='$fwdfwsettings{'oldusesrv'}' />
			<input type='hidden' name='oldrulenumber' value='$fwdfwsettings{'oldrulenumber'}' />
			<input type='hidden' name='rulenumber' value='$fwdfwsettings{'rulepos'}' />
			<input type='hidden' name='oldruleremark' value='$fwdfwsettings{'oldruleremark'}' />
			<input type='hidden' name='ACTION' value='saverule' ></form><form method='post' style='display:inline'><input type='submit' value='$Lang::tr{'fwhost back'}' style='min-width:100px;'><input type='hidden' name='ACTION' value'reset'></td></td>
			</table></form>
END
		}
		&Header::closebox();
}
sub saverule
{
	my $hash=shift;
	my $config=shift;
	&General::readhasharray("$config", $hash);
	if (!$errormessage){
		if ($fwdfwsettings{'updatefwrule'} ne 'on'){
			my $key = &General::findhasharraykey ($hash);
			$$hash{$key}[0]  = $fwdfwsettings{'RULE_ACTION'};
			$$hash{$key}[1]  = $fwdfwsettings{'chain'};
			$$hash{$key}[2]  = $fwdfwsettings{'ACTIVE'};
			$$hash{$key}[3]  = $fwdfwsettings{'grp1'};
			$$hash{$key}[4]  = $fwdfwsettings{$fwdfwsettings{'grp1'}};
			$$hash{$key}[5]  = $fwdfwsettings{'grp2'};
			$$hash{$key}[6]  = $fwdfwsettings{$fwdfwsettings{'grp2'}};
			$$hash{$key}[7]  = $fwdfwsettings{'USE_SRC_PORT'};
			$$hash{$key}[8]  = $fwdfwsettings{'PROT'};
			$$hash{$key}[9]  = $fwdfwsettings{'ICMP_TYPES'};
			$$hash{$key}[10] = $fwdfwsettings{'SRC_PORT'};
			$$hash{$key}[11] = $fwdfwsettings{'USESRV'};
			$$hash{$key}[12] = $fwdfwsettings{'TGT_PROT'};
			$$hash{$key}[13] = $fwdfwsettings{'ICMP_TGT'};
			$$hash{$key}[14] = $fwdfwsettings{'grp3'};
			$$hash{$key}[15] = $fwdfwsettings{$fwdfwsettings{'grp3'}};
			$$hash{$key}[16] = $fwdfwsettings{'ruleremark'};
			$$hash{$key}[17] = $fwdfwsettings{'LOG'};
			$$hash{$key}[18] = $fwdfwsettings{'TIME'};
			$$hash{$key}[19] = $fwdfwsettings{'TIME_MON'};
			$$hash{$key}[20] = $fwdfwsettings{'TIME_TUE'};
			$$hash{$key}[21] = $fwdfwsettings{'TIME_WED'};
			$$hash{$key}[22] = $fwdfwsettings{'TIME_THU'};
			$$hash{$key}[23] = $fwdfwsettings{'TIME_FRI'};
			$$hash{$key}[24] = $fwdfwsettings{'TIME_SAT'};
			$$hash{$key}[25] = $fwdfwsettings{'TIME_SUN'};
			$$hash{$key}[26] = $fwdfwsettings{'TIME_FROM'};
			$$hash{$key}[27] = $fwdfwsettings{'TIME_TO'};
			&General::writehasharray("$config", $hash);
		}else{
			foreach my $key (sort {$a <=> $b} keys %$hash){
				if($key eq $fwdfwsettings{'key'}){
					$$hash{$key}[0]  = $fwdfwsettings{'RULE_ACTION'};
					$$hash{$key}[1]  = $fwdfwsettings{'chain'};
					$$hash{$key}[2]  = $fwdfwsettings{'ACTIVE'};
					$$hash{$key}[3]  = $fwdfwsettings{'grp1'};
					$$hash{$key}[4]  = $fwdfwsettings{$fwdfwsettings{'grp1'}};
					$$hash{$key}[5]  = $fwdfwsettings{'grp2'};
					$$hash{$key}[6]  = $fwdfwsettings{$fwdfwsettings{'grp2'}};
					$$hash{$key}[7]  = $fwdfwsettings{'USE_SRC_PORT'};
					$$hash{$key}[8]  = $fwdfwsettings{'PROT'};
					$$hash{$key}[9]  = $fwdfwsettings{'ICMP_TYPES'};
					$$hash{$key}[10] = $fwdfwsettings{'SRC_PORT'};
					$$hash{$key}[11] = $fwdfwsettings{'USESRV'};
					$$hash{$key}[12] = $fwdfwsettings{'TGT_PROT'};
					$$hash{$key}[13] = $fwdfwsettings{'ICMP_TGT'};
					$$hash{$key}[14] = $fwdfwsettings{'grp3'};
					$$hash{$key}[15] = $fwdfwsettings{$fwdfwsettings{'grp3'}};
					$$hash{$key}[16] = $fwdfwsettings{'ruleremark'};
					$$hash{$key}[17] = $fwdfwsettings{'LOG'};
					$$hash{$key}[18] = $fwdfwsettings{'TIME'};
					$$hash{$key}[19] = $fwdfwsettings{'TIME_MON'};
					$$hash{$key}[20] = $fwdfwsettings{'TIME_TUE'};
					$$hash{$key}[21] = $fwdfwsettings{'TIME_WED'};
					$$hash{$key}[22] = $fwdfwsettings{'TIME_THU'};
					$$hash{$key}[23] = $fwdfwsettings{'TIME_FRI'};
					$$hash{$key}[24] = $fwdfwsettings{'TIME_SAT'};
					$$hash{$key}[25] = $fwdfwsettings{'TIME_SUN'};
					$$hash{$key}[26] = $fwdfwsettings{'TIME_FROM'};
					$$hash{$key}[27] = $fwdfwsettings{'TIME_TO'};
					last;
				}
			}
		}
		&General::writehasharray("$config", $hash);
		if($fwdfwsettings{'oldrulenumber'} gt $fwdfwsettings{'rulepos'}){
			my %tmp=();
			my $val=$fwdfwsettings{'oldrulenumber'}-$fwdfwsettings{'rulepos'};
			for (my $z=0;$z<$val;$z++){
				foreach my $key (sort {$a <=> $b} keys %$hash){
					if ($key eq $fwdfwsettings{'oldrulenumber'}) {
						my $last = $key -1;
						if (exists $$hash{$last}){
							#save rule last
							foreach my $y (0 .. $#{$$hash{$last}}) {
								$tmp{0}[$y] = $$hash{$last}[$y];
							}
							#copy active rule to last
							foreach my $i (0 .. $#{$$hash{$last}}) {
								$$hash{$last}[$i] = $$hash{$key}[$i];
							}
							#copy saved rule to actual position
							foreach my $x (0 .. $#{$tmp{0}}) {
								$$hash{$key}[$x] = $tmp{0}[$x];
							}
						}
					}
				}
				$fwdfwsettings{'oldrulenumber'}--;
			}
			&General::writehasharray("$config", $hash);
			&rules;
		}elsif($fwdfwsettings{'rulepos'} gt $fwdfwsettings{'oldrulenumber'}){
			my %tmp=();
			my $val=$fwdfwsettings{'rulepos'}-$fwdfwsettings{'oldrulenumber'};
				for (my $z=0;$z<$val;$z++){
					foreach my $key (sort {$a <=> $b} keys %$hash){
					if ($key eq $fwdfwsettings{'oldrulenumber'}) {
						my $next = $key + 1;
						if (exists $$hash{$next}){
							#save rule next
							foreach my $y (0 .. $#{$$hash{$next}}) {
								$tmp{0}[$y] = $$hash{$next}[$y];
							}
							#copy active rule to next
							foreach my $i (0 .. $#{$$hash{$next}}) {
								$$hash{$next}[$i] = $$hash{$key}[$i];
							}
							#copy saved rule to actual position
							foreach my $x (0 .. $#{$tmp{0}}) {
								$$hash{$key}[$x] = $tmp{0}[$x];
							}
						}
					}
				}
				$fwdfwsettings{'oldrulenumber'}++;
			}
			&General::writehasharray("$config", $hash);
			&rules;
		}
	}
}
sub error
{
	if ($errormessage) {
		&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
		print "<class name='base'>$errormessage\n";
		print "&nbsp;</class>\n";
		&Header::closebox();
		print"<hr>";
	}
}
sub hint
{
	if ($hint) {
		&Header::openbox('100%', 'left', $Lang::tr{'fwhost hint'});
		print "<class name='base'>$hint\n";
		print "&nbsp;</class>\n";
		&Header::closebox();
		print"<hr>";
	}
}
sub get_name
{
	my $val=shift;
	&General::setup_default_networks(\%defaultNetworks);
	foreach my $network (sort keys %defaultNetworks)
	{
		return "$network" if ($val eq $defaultNetworks{$network}{'NAME'});
	}
}
sub validremark
{
	# Checks a hostname against RFC1035
        my $remark = $_[0];

	# Each part should be at least two characters in length
	# but no more than 63 characters
	if (length ($remark) < 1 || length ($remark) > 255) {
		return 0;}
	# Only valid characters are a-z, A-Z, 0-9 and -
	if ($remark !~ /^[a-zäöüA-ZÖÄÜ0-9-.:_\/\s]*$/) {
		return 0;}
	# First character can only be a letter or a digit
	if (substr ($remark, 0, 1) !~ /^[a-zäöüA-ZÖÄÜ0-9]*$/) {
		return 0;}
	# Last character can only be a letter or a digit
	if (substr ($remark, -1, 1) !~ /^[a-zöäüA-ZÖÄÜ0-9.]*$/) {
		return 0;}
	return 1;
}
sub getsrcport
{
	my %hash=%{(shift)};
	my $key=shift;
	if($hash{$key}[7] eq 'ON' && $hash{$key}[8] ne '' && $hash{$key}[10]){
		$hash{$key}[10]=~ s/\|/,/g;
		print": $hash{$key}[10]";
	}elsif($hash{$key}[7] eq 'ON' && $hash{$key}[8] eq 'ICMP'){
		print": <br>$hash{$key}[9] ";
	}
}
sub gettgtport
{
	my %hash=%{(shift)};
	my $key=shift;
	my $service;
	my $prot;
	if($hash{$key}[11] eq 'ON' && $hash{$key}[12] ne 'ICMP'){
		if($hash{$key}[14] eq 'cust_srv'){
			&General::readhasharray("$configsrv", \%customservice);
			foreach my $i (sort keys %customservice){
				if($customservice{$i}[0] eq $hash{$key}[15]){
					$service = $customservice{$i}[0];
				}
			}
		}elsif($hash{$key}[14] eq 'cust_srvgrp'){
			$service=$hash{$key}[15];
		}elsif($hash{$key}[14] eq 'TGT_PORT'){
			$hash{$key}[15]=~ s/\|/,/g;
			$service=$hash{$key}[15];
		}
		if($service){
			print": $service";
		}
	}elsif($hash{$key}[11] eq 'ON' && $hash{$key}[12] eq 'ICMP'){
		print":<br>$hash{$key}[13]";
	}
}
sub get_serviceports
{
	my $type=shift;
	my $name=shift;
	&General::readhasharray("$configsrv", \%customservice);
	&General::readhasharray("$configsrvgrp", \%customservicegrp);
	my $protocols;
	my $tcp;
	my $udp;
	if($type eq 'service'){
		foreach my $key (sort { uc($customservice{$a}[0]) cmp uc($customservice{$b}[0]) } keys %customservice){
			if ($customservice{$key}[0] eq $name){
				$protocols=$customservice{$key}[2];
			}
		}
		
	}elsif($type eq 'group'){
		foreach my $key (sort { uc($customservicegrp{$a}[0]) cmp uc($customservicegrp{$b}[0]) } keys %customservicegrp){
			if ($customservicegrp{$key}[0] eq $name){
				if($customservicegrp{$key}[4] eq 'TCP'){$tcp='TCP';}else{$udp='UDP';}
			}
		}
	}
	if($tcp){$protocols.="TCP";}
	if($udp){$protocols.=",UDP";}
	return $protocols;
}
sub viewtablerule
{
	
	&viewtablenew(\%configfwdfw,$configfwdfw,$Lang::tr{'fwdfw rules'},"Forward" );
	&viewtablenew(\%configfwdfw,$configfwdfw,'',"DMZ" );
	&viewtablenew(\%configfwdfw,$configfwdfw,'',"WLAN" );
	&viewtablenew(\%configinputfw,$configinput,"",$Lang::tr{'external access'} );
}
sub viewtablenew
{
	my $hash=shift;
	my $config=shift;
	my $title=shift;
	my $title1=shift;
	my $go='';
	&General::readhasharray("$config", $hash);
	#check if there are DMZ entries
	if ($title1 eq 'DMZ'){
		foreach my $key (keys %$hash){
			if ($$hash{$key}[4] eq 'ORANGE'){$go='on';last} 
		}
	}elsif($title1 eq 'WLAN'){
		foreach my $key (keys %$hash){
			if ($$hash{$key}[4] eq 'BLUE'){$go='on';last} 
		}
	}elsif($title1 eq 'Forward'){
		foreach my $key (keys %$hash){
			if (($$hash{$key}[4] ne 'ORANGE' && $$hash{$key}[4] ne 'BLUE')){$go='on';last} 
		}
	}elsif( ! -z $config){
		$go='on';
	}
	if($go ne ''){
		&Header::openbox('100%', 'left',$title);
		my $count=0;
		my ($gif,$log);
		my $ruletype;
		my $rulecolor;
		my $tooltip;
		my @tmpsrc=();
		my $coloryellow='';
		print"<b>$title1</b><br>";
		print"<table width='100%' border='0' cellspacing='1' style='padding-top: 0px; padding-left: 0px; padding-bottom: 0px ;padding-right: 0px ;'>";
		print"<tr><td align='center' width='1%'><b>#</td><td width='1%'></td><td align='center' ><b>$Lang::tr{'fwdfw source'}</td><td width='1%'><b>Log</td><td align='center' width='20%'><b>$Lang::tr{'fwdfw target'}</td><td align='center'><b>$Lang::tr{'protocol'}</b></td><td align='center' width='70%'><b>$Lang::tr{'remark'}</td><td align='center' colspan='3' width='1%'><b>$Lang::tr{'fwdfw action'}</td></tr>";
		foreach my $key (sort  {$a <=> $b} keys %$hash){
			#check if we have a FORWARDFW OR DMZ RULE
			if ($title1 eq 'DMZ' && ($$hash{$key}[4] ne 'ORANGE')){next;}
			if ($title1 eq 'WLAN' && ($$hash{$key}[4] ne 'BLUE')){next;}
			if ($title1 eq 'Forward' && ($$hash{$key}[4] eq 'ORANGE' || $$hash{$key}[4] eq 'BLUE')){next;}
			@tmpsrc=();
			#check if vpn hosts/nets have been deleted
			if($$hash{$key}[3] =~ /ipsec/i || $$hash{$key}[3] =~ /ovpn/i){
				push (@tmpsrc,$$hash{$key}[4]);
			}
			if($$hash{$key}[5] =~ /ipsec/i || $$hash{$key}[5] =~ /ovpn/i){
				push (@tmpsrc,$$hash{$key}[6]);
			}
			foreach my $host (@tmpsrc){
				if($$hash{$key}[3] eq  'ipsec_net_src' || $$hash{$key}[5] eq 'ipsec_net_tgt'){
					if(&fwlib::get_ipsec_net_ip($host,11) eq ''){
						$coloryellow='on';
						&disable_rule($key);
						$$hash{$key}[2]='';
					}
				}elsif($$hash{$key}[3] eq  'ovpn_net_src' || $$hash{$key}[5] eq 'ovpn_net_tgt'){
					if(&fwlib::get_ovpn_net_ip($host,1) eq ''){
						$coloryellow='on';
						&disable_rule($key);
						$$hash{$key}[2]='';
					}
				}elsif($$hash{$key}[3] eq  'ovpn_n2n_src' || $$hash{$key}[5] eq 'ovpn_n2n_tgt'){
					if(&fwlib::get_ovpn_n2n_ip($host,27) eq ''){
						$coloryellow='on';
						&disable_rule($key);
						$$hash{$key}[2]='';
					}
				}elsif($$hash{$key}[3] eq  'ovpn_host_src' || $$hash{$key}[5] eq 'ovpn_host_tgt'){
					if(&fwlib::get_ovpn_host_ip($host,33) eq ''){
						$coloryellow='on';
						&disable_rule($key);
						$$hash{$key}[2]='';
					}
				}
				$$hash{$key}[3]='';
				$$hash{$key}[5]='';
			}
			$$hash{'ACTIVE'}=$$hash{$key}[2];
			$count++;
			if($coloryellow eq 'on'){
				print"<tr bgcolor='$color{'color14'}' >";
				$coloryellow='';
			}elsif($coloryellow eq ''){
				if ($count % 2){ 
					print"<tr bgcolor='$color{'color22'}' >";
				}
				else{
					print"<tr bgcolor='$color{'color20'}' >";
				}
			}
			print<<END;
			<td align='right'>$key</td>
END
			if ($$hash{$key}[0] eq 'ACCEPT'){
				$ruletype='A';
				$tooltip='ACCEPT';
				$rulecolor=$color{'color17'};
			}elsif($$hash{$key}[0] eq 'DROP'){
				$ruletype='D';
				$tooltip='DROP';
				$rulecolor=$color{'color25'};
			}elsif($$hash{$key}[0] eq 'REJECT'){
				$ruletype='R';
				$tooltip='REJECT';
				$rulecolor=$color{'color16'};
			}
			print"<td bgcolor='$rulecolor' width='2%' align='center'><span title='$tooltip'><b>$ruletype</b></span></td>";
			print"<td align='center' nowrap='nowrap'>";
			if ($$hash{$key}[3] eq 'std_net_src'){
				print &get_name($$hash{$key}[4]);
			}else{
				print $$hash{$key}[4];
			}
			&getsrcport(\%$hash,$key);
			if ($$hash{$key}[17] eq 'ON'){
				$log="/images/on.gif";
			}else{
				$log="/images/off.gif";
			}
			print<<END;
			</td>
			<form method='post'>
			<td width='1%' align='left'><input type='image' img src='$log' alt='$Lang::tr{'click to disable'}' title='$Lang::tr{'fwdfw togglelog'}' style='padding-top: 0px; padding-left: 0px; padding-bottom: 0px ;padding-right: 0px ;'/>
			<input type='hidden' name='key' value='$key' />
			<input type='hidden' name='config' value='$config' />
			<input type='hidden' name='ACTION' value='$Lang::tr{'fwdfw togglelog'}' />
			</td></form>
END
			print<<END;
			<td align='center' nowrap='nowrap'>
END
			if ($$hash{$key}[5] eq 'std_net_tgt'){
				print &get_name($$hash{$key}[6]);
			}else{
				print $$hash{$key}[6];
			}
			&gettgtport(\%$hash,$key);
	################################################################################
			print"</td>";
			#Get Protocol
			my $prot;
			if ($$hash{$key}[12]){			#target prot if manual
				$prot=$$hash{$key}[12];
			}elsif($$hash{$key}[8]){		#source prot if manual
				$prot=$$hash{$key}[8];
			}elsif($$hash{$key}[14] eq 'cust_srv'){ 
				$prot=&get_serviceports("service",$$hash{$key}[15]);
			}elsif($$hash{$key}[14] eq 'cust_srvgrp'){
				$prot=&get_serviceports("group",$$hash{$key}[15]);
			}else{
				$prot=$Lang::tr{'all'};
			}
			print"<td align='center'>$prot</td>";
			
			print"<td width='20%'>$$hash{$key}[16]</td>";
			
			if($$hash{$key}[2] eq 'ON'){
				$gif="/images/on.gif"
				
			}else{
				$gif="/images/off.gif"
			}
			print<<END;
			<form method='post'>
			<td width='1%'><input type='image' img src='$gif' alt='$Lang::tr{'click to disable'}' title='$Lang::tr{'fwdfw toggle'}' style='padding-top: 0px; padding-left: 0px; padding-bottom: 0px ;padding-right: 0px ;display: block;' />
			<input type='hidden' name='key' value='$key' />
			<input type='hidden' name='config' value='$config' />
			<input type='hidden' name='ACTION' value='$Lang::tr{'fwdfw toggle'}' />
			</td></form>
			<form method='post'>
			<td  width='1%' ><input type='image' img src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'fwdfw edit'}' style='padding-top: 0px; padding-left: 0px; padding-bottom: 0px ;padding-right: 0px ;display: block;'  />
			<input type='hidden' name='key' value='$key' />
			<input type='hidden' name='config' value='$config' />
			<input type='hidden' name='ACTION' value='editrule' />
			</td></form></td>
			<form method='post'>
			<td  width='1%'><input type='image' img src='/images/addblue.gif' alt='$Lang::tr{'fwdfw copy'}' title='$Lang::tr{'fwdfw copy'}' style='padding-top: 0px; padding-left: 0px; padding-bottom: 0px ;padding-right: 0px ;display: block;' />
			<input type='hidden' name='key' value='$key' />
			<input type='hidden' name='config' value='$config' />
			<input type='hidden' name='ACTION' value='copyrule' />
			</td></form></td>
			<form method='post'>
			<td width='1%' ><input type='image' img src='/images/delete.gif' alt='$Lang::tr{'delete'}' title='$Lang::tr{'fwdfw delete'}' style='padding-top: 0px; padding-left: 0px; padding-bottom: 0px ;padding-right: 0px ;display: block;'   />
			<input type='hidden' name='key' value='$key' />
			<input type='hidden' name='config' value='$config' />
			<input type='hidden' name='ACTION' value='deleterule' />
			</td></form></td>
END
			if (exists $$hash{$key-1}){
				print<<END;
				<form method='post'>
				<td width='1%'><input type='image' img src='/images/up.gif' alt='$Lang::tr{'fwdfw moveup'}' title='$Lang::tr{'fwdfw moveup'}'  style='padding-top: 0px; padding-left: 0px; padding-bottom: 0px ;padding-right: 0px ;display: block;'  />
				<input type='hidden' name='key' value='$key' />
				<input type='hidden' name='config' value='$config' />
				<input type='hidden' name='ACTION' value='moveup' />
				</td></form></td>
END
			}else{
				print"<td></td>";
			}
			if (exists $$hash{$key+1}){
				print<<END;
				<form method='post'>
				<td  width='1%' ><input type='image' img src='/images/down.gif' alt='$Lang::tr{'fwdfw movedown'}' title='$Lang::tr{'fwdfw movedown'}' style='padding-top: 0px; padding-left: 0px; padding-bottom: 0px ;padding-right: 0px ;display: block;'  />
				<input type='hidden' name='key' value='$key' />
				<input type='hidden' name='config' value='$config' />
				<input type='hidden' name='ACTION' value='movedown' />
				</td></form></td></tr>
END
			}else{
				print"<td></td></tr>";
			}
			#if timeframe set, print new line in table
			if ($$hash{$key}[18] eq 'ON'){
				my @days=();
				if($$hash{$key}[19] ne ''){push (@days,$Lang::tr{'fwdfw wd_mon'});}
				if($$hash{$key}[20] ne ''){push (@days,$Lang::tr{'fwdfw wd_tue'});}
				if($$hash{$key}[21] ne ''){push (@days,$Lang::tr{'fwdfw wd_wed'});}
				if($$hash{$key}[22] ne ''){push (@days,$Lang::tr{'fwdfw wd_thu'});}
				if($$hash{$key}[23] ne ''){push (@days,$Lang::tr{'fwdfw wd_fri'});}
				if($$hash{$key}[24] ne ''){push (@days,$Lang::tr{'fwdfw wd_sat'});}
				if($$hash{$key}[25] ne ''){push (@days,$Lang::tr{'fwdfw wd_sun'});}
				my $weekdays=join(",",@days);
				if (@days){
					print"<tr bgcolor='#FFE4B5'><td colspan='6'>$Lang::tr{'fwdfw time'} ";
					print"$weekdays";
					print "&nbsp $Lang::tr{'fwdfw from'} $$hash{$key}[26] &nbsp $Lang::tr{'fwdfw till'} $$hash{$key}[27]</td><td colspan='8'></d></tr>";
				}
			}
		}
		print"</table>";
		&Header::closebox();
	}
}
sub p2pblock
{
	my $gif;
	open( FILE, "< $p2pfile" ) or die "Unable to read $p2pfile";
	@p2ps = <FILE>;
	close FILE;
	&Header::openbox('100%', 'center', 'P2P-Block');
	print <<END;
	<table width='35%' border='0'>
	<tr bgcolor='$color{'color22'}'><td align=center colspan='2' ><b>$Lang::tr{'protocol'}</b></td><td align='center'><b>$Lang::tr{'status'}</b></td></tr>
END
	foreach my $p2pentry (sort @p2ps)
	{
		my @p2pline = split( /\;/, $p2pentry );
		if($p2pline[2] eq 'on'){
			$gif="/images/on.gif"
		}else{
			$gif="/images/off.gif"
		}
		print <<END;
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<tr bgcolor='$color{'color20'}'>
		<td align='center' colspan='2' >$p2pline[0]:</td><td align='center'><input type='hidden' name='P2PROT' value='$p2pline[1]' /><input type='image' img src='$gif' alt='$Lang::tr{'click to disable'}' title='$Lang::tr{'fwdfw toggle'}' style='padding-top: 0px; padding-left: 0px; padding-bottom: 0px ;padding-right: 0px ;display: block;' ><input type='hidden' name='ACTION' value='togglep2p'></td></tr></form>
END
	}
	print"<tr><td><img src='/images/on.gif'></td><td  align='left'>$Lang::tr{'outgoing firewall p2p allow'}</td></tr>";
	print"<tr><td><img src='/images/off.gif'></td><td align='left'>$Lang::tr{'outgoing firewall p2p deny'}</td></tr></table>";
	&Header::closebox();
}
sub fillselect
{
	my %hash=%{(shift)};
	my $val=shift;
	my $key;
	foreach my $key (sort { uc($hash{$a}[0]) cmp uc($hash{$b}[0]) }  keys %hash){
		if($hash{$key}[0] eq $val){
			print"<option value='$hash{$key}[0]' selected>$hash{$key}[0]</option>";
		}else{
			print"<option value='$hash{$key}[0]'>$hash{$key}[0]</option>";
		}
	}
}
sub rules
{
	if (!-f "${General::swroot}/forward/reread"){
		system("touch ${General::swroot}/forward/reread");
	}
}
sub reread_rules
{
	system("/usr/local/bin/forwardfwctrl");
	if ( -f "${General::swroot}/forward/reread"){
		system("rm ${General::swroot}/forward/reread");
	}
}
&Header::closebigbox();
&Header::closepage();
