#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2011  IPFire Team  <info@ipfire.org>                          #
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
# New function for forwarding firewall. To make it comfortable to create	  #
# rules, we need "spelling names" for single Hosts. If you have any questions #
# <amarx@ipfire.org>														  #
###############################################################################
use strict;

# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';
no warnings 'uninitialized';
require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %fwhostsettings=();
my %customnetwork=();
my %customhost=();
my %customgrp=();
my %customservice=();
my %customservicegrp=();
my %ccdnet=();
my %ccdhost=();
my %ipsecconf=();
my %icmptypes=();
my %color=();
my %defaultNetworks=();
my %mainsettings=();
my %ownnet=();
my %ipsecsettings=();
my %fwfwd=();
my %fwinp=();

my $errormessage;
my $hint;
my $update=0;
my $confignet		= "${General::swroot}/fwhosts/customnetworks";
my $confighost		= "${General::swroot}/fwhosts/customhosts";
my $configgrp 		= "${General::swroot}/fwhosts/customgroups";
my $configccdnet 	= "${General::swroot}/ovpn/ccd.conf";
my $configccdhost	= "${General::swroot}/ovpn/ovpnconfig";
my $configipsec		= "${General::swroot}/vpn/config";
my $configsrv		= "${General::swroot}/fwhosts/customservices";
my $configsrvgrp	= "${General::swroot}/fwhosts/customservicegrp";
my $fwconfigfwd		= "${General::swroot}/forward/config";
my $fwconfiginp		= "${General::swroot}/forward/input";

unless (-e $confignet)    { system("touch $confignet"); }
unless (-e $confighost)   { system("touch $confighost"); }
unless (-e $configgrp)    { system("touch $configgrp"); }
unless (-e $configsrv)    { system("touch $configsrv"); }
unless (-e $configsrvgrp) { system("touch $configsrvgrp"); }

&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);
&General::readhash("${General::swroot}/ethernet/settings", \%ownnet);
&Header::getcgihash(\%fwhostsettings);

&Header::showhttpheaders();
&Header::openpage($Lang::tr{'fwhost hosts'}, 1, '');
&Header::openbigbox('100%', 'center');

## ACTION ####
# Update
if ($fwhostsettings{'ACTION'} eq 'updatenet' )
{
	&General::readhasharray("$confignet", \%customnetwork);
	foreach my $key (keys %customnetwork)
	{
		if($customnetwork{$key}[0] eq $fwhostsettings{'orgname'})
		{
			$fwhostsettings{'orgname'} 		= $customnetwork{$key}[0];
			$fwhostsettings{'orgip'} 		= $customnetwork{$key}[1];
			$fwhostsettings{'orgsub'} 		= $customnetwork{$key}[2];
			$fwhostsettings{'count'} 		= $customnetwork{$key}[3];
			delete $customnetwork{$key};
			
		}
	}
	&General::writehasharray("$confignet", \%customnetwork);
	$fwhostsettings{'actualize'} = 'on';
	$fwhostsettings{'ACTION'} = 'savenet';
}
if ($fwhostsettings{'ACTION'} eq 'updatehost')
{
	my ($ip,$subnet);
	&General::readhasharray("$confighost", \%customhost);
	foreach my $key (keys %customhost)
	{
		if($customhost{$key}[0] eq $fwhostsettings{'orgname'})
		{
			$fwhostsettings{'orgname'} = $customhost{$key}[0];
			if ($customhost{$key}[1] eq 'ip'){
				($ip,$subnet) = split (/\//,$customhost{$key}[2]);
			}else{
				$ip = $customhost{$key}[2];
			}
			$fwhostsettings{'orgip'} = $ip;
			$fwhostsettings{'count'} = $customhost{$key}[3];
			delete $customhost{$key};
		}
	}
	&General::writehasharray("$confighost", \%customhost);
	$fwhostsettings{'actualize'} = 'on';
	$fwhostsettings{'ACTION'} = 'savehost';
}
if ($fwhostsettings{'ACTION'} eq 'updateservice')
{
	my $count=0;
	my $needrules=0;
	$errormessage=&checkports(\%customservice);
	if (!$errormessage){
		&General::readhasharray("$configsrv", \%customservice);
		foreach my $key (keys %customservice)
		{
			if ($customservice{$key}[0] eq $fwhostsettings{'oldsrvname'})
			{
				$count=$customservice{$key}[4];
				delete $customservice{$key};
				&General::writehasharray("$configsrv", \%customservice);
				last;
			}
		}
		if ($fwhostsettings{'PROT'} ne 'ICMP'){
			$fwhostsettings{'ICMP_TYPES'}='BLANK';
		}
		my $key1 = &General::findhasharraykey(\%customservice);
		foreach my $i (0 .. 4) { $customservice{$key1}[$i] = "";}
		$customservice{$key1}[0] = $fwhostsettings{'SRV_NAME'};
		$customservice{$key1}[1] = $fwhostsettings{'SRV_PORT'};
		$customservice{$key1}[2] = $fwhostsettings{'PROT'};
		$customservice{$key1}[3] = $fwhostsettings{'ICMP_TYPES'};
		$customservice{$key1}[4] = $count;
		&General::writehasharray("$configsrv", \%customservice);
		if($fwhostsettings{'updatesrv'} eq 'on'){
			if($count gt 0 && $fwhostsettings{'oldsrvport'} ne $fwhostsettings{'SRV_PORT'} ){
				$needrules='on';
			}
			if($count gt 0 && $fwhostsettings{'oldsrvprot'} ne $fwhostsettings{'PROT'} ){
				$needrules='on';
			}
		}
		$fwhostsettings{'SRV_NAME'}	= '';
		$fwhostsettings{'SRV_PORT'}	= '';
		$fwhostsettings{'PROT'}		= '';
	}else{
		$fwhostsettings{'SRV_NAME'}	= $fwhostsettings{'oldsrvname'};
		$fwhostsettings{'SRV_PORT'}	= $fwhostsettings{'oldsrvport'};
		$fwhostsettings{'PROT'}		= $fwhostsettings{'oldsrvprot'};
		$fwhostsettings{'updatesrv'}= 'on';
	}
	if($needrules eq 'on'){
		$errormessage="reread!";
		&rules;
	}
	&addservice;
}
# save
if ($fwhostsettings{'ACTION'} eq 'savenet' )
{
	my $count=0;
	my $needrules=0;
	if ($fwhostsettings{'orgname'} eq ''){$fwhostsettings{'orgname'}=$fwhostsettings{'HOSTNAME'};}
	#check if all fields are set
	if ($fwhostsettings{'HOSTNAME'} eq '' || $fwhostsettings{'IP'} eq '' || $fwhostsettings{'SUBNET'} eq '')
	{
		$errormessage=$errormessage.$Lang::tr{'fwhost err empty'};
		&addnet;
		&viewtablenet;
	}else{
		#check valid ip 
		if (!&General::validipandmask($fwhostsettings{'IP'}."/".$fwhostsettings{'SUBNET'}))
		{
			$errormessage=$errormessage.$Lang::tr{'fwhost err addr'};
			$fwhostsettings{'BLK_HOST'}	='readonly';
			$fwhostsettings{'NOCHECK'}	='false';
			$fwhostsettings{'error'}	='on';
		}
		#check if subnet is sigle host
		if(&General::iporsubtocidr($fwhostsettings{'SUBNET'}) eq '32')
		{
			$errormessage=$errormessage.$Lang::tr{'fwhost err sub32'};
		}
		if($fwhostsettings{'error'} ne 'on'){
			#check if we use one of ipfire's networks (green,orange,blue)
			if (($ownnet{'GREEN_NETADDRESS'}  	ne '' && $ownnet{'GREEN_NETADDRESS'} 	ne '0.0.0.0') && &General::IpInSubnet($fwhostsettings{'IP'},$ownnet{'GREEN_NETADDRESS'},$ownnet{'GREEN_NETMASK'}))
			{ 
				$errormessage=$errormessage.$Lang::tr{'ccd err green'}."<br>";
				$fwhostsettings{'HOSTNAME'} = $fwhostsettings{'orgname'};
				if ($fwhostsettings{'update'} eq 'on'){$fwhostsettings{'ACTION'}='editnet';}
			}
			if (($ownnet{'ORANGE_NETADDRESS'}	ne '' && $ownnet{'ORANGE_NETADDRESS'} 	ne '0.0.0.0') && &General::IpInSubnet($fwhostsettings{'IP'},$ownnet{'ORANGE_NETADDRESS'},$ownnet{'ORANGE_NETMASK'}))
			{ 
				$errormessage=$errormessage.$Lang::tr{'ccd err orange'}."<br>";
				$fwhostsettings{'HOSTNAME'} = $fwhostsettings{'orgname'};
				if ($fwhostsettings{'update'} eq 'on'){$fwhostsettings{'ACTION'}='editnet';}
			}
			if (($ownnet{'BLUE_NETADDRESS'} 	ne '' && $ownnet{'BLUE_NETADDRESS'} 	ne '0.0.0.0') && &General::IpInSubnet($fwhostsettings{'IP'},$ownnet{'BLUE_NETADDRESS'},$ownnet{'BLUE_NETMASK'}))
			{ 
				$errormessage=$errormessage.$Lang::tr{'ccd err blue'}."<br>";
				$fwhostsettings{'HOSTNAME'} = $fwhostsettings{'orgname'};
				if ($fwhostsettings{'update'} eq 'on'){$fwhostsettings{'ACTION'}='editnet';}
			}
			if (($ownnet{'RED_NETADDRESS'} 	ne '' && $ownnet{'RED_NETADDRESS'} 		ne '0.0.0.0') && &General::IpInSubnet($fwhostsettings{'IP'},$ownnet{'RED_NETADDRESS'},$ownnet{'RED_NETMASK'}))
			{ 
				$errormessage=$errormessage.$Lang::tr{'ccd err red'}."<br>";
				$fwhostsettings{'HOSTNAME'} = $fwhostsettings{'orgname'};
				if ($fwhostsettings{'update'} eq 'on'){$fwhostsettings{'ACTION'}='editnet';}
			}
		}
		#only check plausi when no error till now
		if (!$errormessage){
			&plausicheck("editnet");
		}
		#check if network ip is part of an already used one 
		if(&checksubnet(\%customnetwork))
		{
			$errormessage=$errormessage.$Lang::tr{'fwhost err partofnet'};
			$fwhostsettings{'HOSTNAME'} = $fwhostsettings{'orgname'};
		}				
		if($fwhostsettings{'actualize'} eq 'on' && $fwhostsettings{'newnet'} ne 'on' && $errormessage)
		{
			$fwhostsettings{'actualize'} = '';
			my $key = &General::findhasharraykey (\%customnetwork);
			foreach my $i (0 .. 3) { $customnetwork{$key}[$i] = "";}
			$customnetwork{$key}[0] = $fwhostsettings{'orgname'} ;
			$customnetwork{$key}[1] = $fwhostsettings{'orgip'} ;
			$customnetwork{$key}[2] = $fwhostsettings{'orgsub'};
			$customnetwork{$key}[3] = $fwhostsettings{'count'};
			&General::writehasharray("$confignet", \%customnetwork);
			undef %customnetwork;
		} 			
		if (!$errormessage){
			&General::readhasharray("$confignet", \%customnetwork);
			if ($fwhostsettings{'ACTION'} eq 'updatenet'){
				if ($fwhostsettings{'update'} == '0'){
					foreach my $key (keys %customnetwork) {
						if($customnetwork{$key}[0] eq $fwhostsettings{'orgname'}){
							$count=$customnetwork{$key}[3];
							delete $customnetwork{$key};
							last;
						}
					}
				}
			}
			#get count if actualize is 'on'
			if($fwhostsettings{'actualize'} eq 'on'){
				$fwhostsettings{'actualize'} = '';
				$count=$fwhostsettings{'count'};
				#check if we need to reload rules
				if($fwhostsettings{'orgip'}  ne $fwhostsettings{'IP'}  && $count gt '0'){
					$needrules='on';
				}
				if ($fwhostsettings{'orgname'} ne $fwhostsettings{'HOSTNAME'}){
					#check if we need to update groups
					&General::readhasharray("$configgrp", \%customgrp);
					foreach my $key (sort keys %customgrp){
						if($customgrp{$key}[2] eq $fwhostsettings{'orgname'}){
							$customgrp{$key}[2]=$fwhostsettings{'HOSTNAME'};
							last;
						}
					}
					&General::writehasharray("$configgrp", \%customgrp);
					#check if we need to update firewallrules
					if ( ! -z $fwconfigfwd ){
						&General::readhasharray("$fwconfigfwd", \%fwfwd);
						foreach my $line (sort keys %fwfwd){
							if ($fwfwd{$line}[4] eq $fwhostsettings{'orgname'}){
								$fwfwd{$line}[4] = $fwhostsettings{'HOSTNAME'};
							}
							if ($fwfwd{$line}[6] eq $fwhostsettings{'orgname'}){
								$fwfwd{$line}[6] = $fwhostsettings{'HOSTNAME'};
							}
						}
						&General::writehasharray("$fwconfigfwd", \%fwfwd);
					}
					if ( ! -z $fwconfiginp ){
						&General::readhasharray("$fwconfiginp", \%fwinp);
						foreach my $line (sort keys %fwinp){
							if ($fwfwd{$line}[4] eq $fwhostsettings{'orgname'}){
								$fwfwd{$line}[4] = $fwhostsettings{'HOSTNAME'};
							}
						}
						&General::writehasharray("$fwconfiginp", \%fwinp);
					}
				}
			}					
			my $key = &General::findhasharraykey (\%customnetwork);
			foreach my $i (0 .. 3) { $customnetwork{$key}[$i] = "";}
			$fwhostsettings{'SUBNET'}	= &General::iporsubtocidr($fwhostsettings{'SUBNET'});
			$customnetwork{$key}[0] 	= $fwhostsettings{'HOSTNAME'};
			#convert ip when leading '0' in byte
			$fwhostsettings{'IP'}=&General::ip2dec($fwhostsettings{'IP'});
			$fwhostsettings{'IP'}=&General::dec2ip($fwhostsettings{'IP'});
			$customnetwork{$key}[1] 	= &General::getnetworkip($fwhostsettings{'IP'},$fwhostsettings{'SUBNET'}) ;
			$customnetwork{$key}[2] 	= &General::iporsubtodec($fwhostsettings{'SUBNET'}) ;
			if($fwhostsettings{'newnet'} eq 'on'){$count=0;}
			$customnetwork{$key}[3] 	= $count;
			&General::writehasharray("$confignet", \%customnetwork);
			$fwhostsettings{'IP'}=$fwhostsettings{'IP'}."/".&General::iporsubtodec($fwhostsettings{'SUBNET'});
			undef %customnetwork;
			$fwhostsettings{'HOSTNAME'}='';
			$fwhostsettings{'IP'}='';
			$fwhostsettings{'SUBNET'}='';
			#check if an edited net affected groups and need to reload rules
			if ($needrules eq 'on'){
				&rules;
			}
			&addnet;
			&viewtablenet;
		}else
		{
			&addnet;
			&viewtablenet;
		}
	}
}
if ($fwhostsettings{'ACTION'} eq 'savehost')
{
	my $count=0;
	my $needrules=0;
	if ($fwhostsettings{'orgname'} eq ''){$fwhostsettings{'orgname'}=$fwhostsettings{'HOSTNAME'};}
	$fwhostsettings{'SUBNET'}='32';
	#check if all fields are set
	if ($fwhostsettings{'HOSTNAME'} eq '' || $fwhostsettings{'IP'} eq '' || $fwhostsettings{'SUBNET'} eq '')
	{
		$errormessage=$errormessage.$Lang::tr{'fwhost err empty'};
		$fwhostsettings{'ACTION'} = 'edithost';
	}else{
		if($fwhostsettings{'type'} eq 'ip' && $fwhostsettings{'IP'}=~/^([0-9a-fA-F]{1,2}:){5}[0-9a-fA-F]{1,2}$/){
			$fwhostsettings{'type'} = 'mac';
		}elsif($fwhostsettings{'type'} eq 'mac' && $fwhostsettings{'IP'}=~/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/){
			$fwhostsettings{'type'} = 'ip';
		}elsif($fwhostsettings{'type'} eq 'mac' && $fwhostsettings{'IP'}=~/^([0-9a-fA-F]{1,2}:){5}[0-9a-fA-F]{1,2}$/){
			$fwhostsettings{'type'} = 'mac';
		}elsif($fwhostsettings{'type'} eq 'ip' && $fwhostsettings{'IP'}=~/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/){
			$fwhostsettings{'type'} = 'ip';
		}else{
			$fwhostsettings{'type'} = '';
			$errormessage=$Lang::tr{'fwhost err ipmac'};
		}
		if($fwhostsettings{'type'} eq 'mac' )
		{
			if ($fwhostsettings{'IP'}!~/^([0-9a-fA-F]{1,2}:){5}[0-9a-fA-F]{1,2}$/ )
			{
				$errormessage=$Lang::tr{'fwhost err mac'};
			}
		}
		#CHECK IP-PART
		if ($fwhostsettings{'type'} eq 'ip'){
			#check for subnet
			if (rindex($fwhostsettings{'IP'},'/') eq '-1' ){
				if($fwhostsettings{'type'} eq 'ip' && !&General::validipandmask($fwhostsettings{'IP'}."/32"))
					{
						$errormessage.=$errormessage.$Lang::tr{'fwhost err ip'};
						$fwhostsettings{'error'}='on';
					}
			}elsif(rindex($fwhostsettings{'IP'},'/') ne '-1' ){
				$errormessage=$errormessage.$Lang::tr{'fwhost err ipwithsub'};
				$fwhostsettings{'error'}='on';
			}
			#check if net or broadcast
			my @tmp= split (/\./,$fwhostsettings{'IP'});
			if (($tmp[3] eq "0") || ($tmp[3] eq "255")){
				$errormessage=$Lang::tr{'fwhost err hostip'};
			}
		}
		#only check plausi when no error till now
		if (!$errormessage){	
			&plausicheck("edithost");
		}
		if($fwhostsettings{'actualize'} eq 'on' && $fwhostsettings{'newhost'} ne 'on' && $errormessage){
			$fwhostsettings{'actualize'} = '';
			my $key = &General::findhasharraykey (\%customhost);
			foreach my $i (0 .. 3) { $customhost{$key}[$i] = "";}
			$customhost{$key}[0] = $fwhostsettings{'orgname'} ;
			$customhost{$key}[1] = $fwhostsettings{'type'} ;
			if($customhost{$key}[1] eq 'ip'){
				$customhost{$key}[2] = $fwhostsettings{'orgip'}."/".&General::iporsubtodec($fwhostsettings{'SUBNET'});
			}else{
				$customhost{$key}[2] = $fwhostsettings{'orgip'};
			}
			$customhost{$key}[3] = $fwhostsettings{'count'};
			&General::writehasharray("$confighost", \%customhost);
			undef %customhost;
		} 
		if (!$errormessage){
			#get count if host was edited
			if($fwhostsettings{'actualize'} eq 'on'){
				$count=$fwhostsettings{'count'};
				if($fwhostsettings{'orgip'} ne $fwhostsettings{'IP'} && $count gt '0' ){
					$needrules='on';
				}
				if($fwhostsettings{'orgname'} ne $fwhostsettings{'HOSTNAME'}){
					#check if we need to update groups
					&General::readhasharray("$configgrp", \%customgrp);
					foreach my $key (sort keys %customgrp){
						if($customgrp{$key}[2] eq $fwhostsettings{'orgname'}){
							$customgrp{$key}[2]=$fwhostsettings{'HOSTNAME'};
							last;
						}
					}
					&General::writehasharray("$configgrp", \%customgrp);
					#check if we need to update firewallrules
					if ( ! -z $fwconfigfwd ){
						&General::readhasharray("$fwconfigfwd", \%fwfwd);
						foreach my $line (sort keys %fwfwd){
							if ($fwfwd{$line}[4] eq $fwhostsettings{'orgname'}){
								$fwfwd{$line}[4] = $fwhostsettings{'HOSTNAME'};
							}
							if ($fwfwd{$line}[6] eq $fwhostsettings{'orgname'}){
								$fwfwd{$line}[6] = $fwhostsettings{'HOSTNAME'};
							}
						}
						&General::writehasharray("$fwconfigfwd", \%fwfwd);
					}
					if ( ! -z $fwconfiginp ){
						&General::readhasharray("$fwconfiginp", \%fwinp);
						foreach my $line (sort keys %fwinp){
							if ($fwfwd{$line}[4] eq $fwhostsettings{'orgname'}){
								$fwfwd{$line}[4] = $fwhostsettings{'HOSTNAME'};
							}
						}
						&General::writehasharray("$fwconfiginp", \%fwinp);
					}
				}
			}
			my $key = &General::findhasharraykey (\%customhost);
			foreach my $i (0 .. 3) { $customhost{$key}[$i] = "";}
			$customhost{$key}[0] = $fwhostsettings{'HOSTNAME'} ;
			$customhost{$key}[1] = $fwhostsettings{'type'} ;
			if ($fwhostsettings{'type'} eq 'ip'){
				#convert ip when leading '0' in byte
				$fwhostsettings{'IP'}=&General::ip2dec($fwhostsettings{'IP'});
				$fwhostsettings{'IP'}=&General::dec2ip($fwhostsettings{'IP'});
				$customhost{$key}[2] = $fwhostsettings{'IP'}."/".&General::iporsubtodec($fwhostsettings{'SUBNET'});
			}else{
				$customhost{$key}[2] = $fwhostsettings{'IP'};
			}
			if($fwhostsettings{'newhost'} eq 'on'){$count=0;}
			$customhost{$key}[3] = $count;
			&General::writehasharray("$confighost", \%customhost);
			#$fwhostsettings{'IP'} = $fwhostsettings{'IP'}."/".&General::iporsubtodec($fwhostsettings{'SUBNET'});
			undef %customhost;
			$fwhostsettings{'HOSTNAME'}='';
			$fwhostsettings{'IP'}='';
			$fwhostsettings{'type'}='';
			#check if we need to update rules while host was edited
			if($needrules eq 'on'){
				&rules;
			}
			&addhost;
			&viewtablehost;
		}else{
			&addhost;
			&viewtablehost;
		}
	}
}
if ($fwhostsettings{'ACTION'} eq 'savegrp')
{
	my $grp;
	my $rem=$fwhostsettings{'remark'};
	my $count;
	my $type;
	my $updcounter='off';
	my @target;
	my @newgrp;
	&General::readhasharray("$configgrp", \%customgrp);
	&General::readhasharray("$confignet", \%customnetwork);
	&General::readhasharray("$confighost", \%customhost);
	$grp=$fwhostsettings{'grp_name'};
	if (!&validhostname($grp)){$errormessage=$errormessage.$Lang::tr{'fwhost err name'};}
	###check standard networks
	if ($fwhostsettings{'grp2'} eq 'std_net'){
		@target=$fwhostsettings{'DEFAULT_SRC_ADR'};
		$type='Standard Network';	
	}
	##check custom networks
	if ($fwhostsettings{'grp2'} eq 'cust_net' && $fwhostsettings{'CUST_SRC_NET'} ne ''){
		@target=$fwhostsettings{'CUST_SRC_NET'};
		$updcounter='net';
		$type='Custom Network';
	}elsif($fwhostsettings{'grp2'} eq 'cust_net' && $fwhostsettings{'CUST_SRC_NET'} eq ''){
		$errormessage=$Lang::tr{'fwhost err groupempty'}."<br>";
		$fwhostsettings{'grp_name'}='';
		$fwhostsettings{'remark'}='';
	}
	#check custom addresses
	if ($fwhostsettings{'grp2'} eq 'cust_host' && $fwhostsettings{'CUST_SRC_HOST'} ne ''){
		@target=$fwhostsettings{'CUST_SRC_HOST'};
		$updcounter='host';
		$type='Custom Host';
	}elsif($fwhostsettings{'grp2'} eq 'cust_host' && $fwhostsettings{'CUST_SRC_HOST'} eq ''){
		$errormessage=$Lang::tr{'fwhost err groupempty'}."<br>";
		$fwhostsettings{'grp_name'}='';
		$fwhostsettings{'remark'}='';
	}
	#get address from  ovpn ccd static net
	if ($fwhostsettings{'grp2'} eq 'ovpn_net' && $fwhostsettings{'OVPN_CCD_NET'} ne ''){
		@target=$fwhostsettings{'OVPN_CCD_NET'};
		$type='OpenVPN static network';
	}elsif($fwhostsettings{'grp2'} eq 'ovpn_net' && $fwhostsettings{'OVPN_CCD_NET'} eq ''){
		$errormessage=$Lang::tr{'fwhost err groupempty'};
		$fwhostsettings{'grp_name'}='';
		$fwhostsettings{'remark'}='';
	}
	#get address from ovpn ccd static host
	if ($fwhostsettings{'grp2'} eq 'ovpn_host' && $fwhostsettings{'OVPN_CCD_HOST'} ne ''){
		@target=$fwhostsettings{'OVPN_CCD_HOST'};
		$type='OpenVPN static host';
	}elsif ($fwhostsettings{'grp2'} eq 'ovpn_host' && $fwhostsettings{'OVPN_CCD_HOST'} eq ''){
		$errormessage=$Lang::tr{'fwhost err groupempty'};
	}
	#get address from ovpn ccd Net-2-Net
	if ($fwhostsettings{'grp2'} eq 'ovpn_n2n' && $fwhostsettings{'OVPN_N2N'} ne ''){
		@target=$fwhostsettings{'OVPN_N2N'};
		$type='OpenVPN N-2-N';
	}elsif ($fwhostsettings{'grp2'} eq 'ovpn_n2n' && $fwhostsettings{'OVPN_N2N'} eq ''){
		$errormessage=$Lang::tr{'fwhost err groupempty'};
		$fwhostsettings{'grp_name'}='';
		$fwhostsettings{'remark'}='';
	}
	#get address from IPSEC HOST
	if ($fwhostsettings{'grp2'} eq 'ipsec_host' && $fwhostsettings{'IPSEC_HOST'} ne ''){
		@target=$fwhostsettings{'IPSEC_HOST'};
		$type='IpSec Host';
	}elsif ($fwhostsettings{'grp2'} eq 'ipsec_host' && $fwhostsettings{'IPSEC_HOST'} eq ''){
		$errormessage=$Lang::tr{'fwhost err groupempty'};
		$fwhostsettings{'grp_name'}='';
		$fwhostsettings{'remark'}='';
	}
	#get address from IPSEC NETWORK
	if ($fwhostsettings{'grp2'} eq 'ipsec_net' && $fwhostsettings{'IPSEC_NET'} ne ''){
		@target=$fwhostsettings{'IPSEC_NET'};
		$type='IpSec Network';
	}elsif ($fwhostsettings{'grp2'} eq 'ipsec_net' && $fwhostsettings{'IPSEC_NET'} eq ''){
		$errormessage=$Lang::tr{'fwhost err groupempty'};
		$fwhostsettings{'grp_name'}='';
		$fwhostsettings{'remark'}='';
	}
	#check if host/net exists in grp
	my $test="$grp,$fwhostsettings{'oldremark'},@target";
	foreach my $key (keys %customgrp) {
		my $test1="$customgrp{$key}[0],$customgrp{$key}[1],$customgrp{$key}[2]";
		if ($test1 eq $test){
			$errormessage=$Lang::tr{'fwhost err isingrp'};
			$fwhostsettings{'update'} = 'on';
		}
	}
	if (!$errormessage){
		#on first save, we have an empty @target, so fill it with nothing
		my $targetvalues=@target;
		if ($targetvalues == '0'){
			@target=$Lang::tr{'fwhost empty'};
		}
		#on update, we have to delete the dummy entry
		foreach my $key (keys %customgrp){
			if ($customgrp{$key}[0] eq $grp && $customgrp{$key}[2] eq $Lang::tr{'fwhost empty'}){
				delete $customgrp{$key};
				last;
			}
		}
		&General::writehasharray("$configgrp", \%customgrp);
		&General::readhasharray("$configgrp", \%customgrp);
		#get count used
		foreach my $key (keys %customgrp)
		{
			if($customgrp{$key}[0] eq $grp)
			{
				$count=$customgrp{$key}[4];
				last;
			}
		}
		if ($count eq '' ){$count='0';}
		
		#create array with new lines
		foreach my $line (@target){
			push (@newgrp,"$grp,$rem,$line");
		}
		#append new entries
		my $key = &General::findhasharraykey (\%customgrp);
		foreach my $line (@newgrp){
			foreach my $i (0 .. 4) { $customgrp{$key}[$i] = "";}
			my ($a,$b,$c,$d) = split (",",$line);
			$customgrp{$key}[0] = $a;
			$customgrp{$key}[1] = $b;
			$customgrp{$key}[2] = $c;
			$customgrp{$key}[3] = $type;
			$customgrp{$key}[4] = $count;
		}
		&General::writehasharray("$configgrp", \%customgrp);
		#update counter in Host/Net
		if($updcounter eq 'net'){
			foreach my $key (keys %customnetwork) {
				if($customnetwork{$key}[0] eq $fwhostsettings{'CUST_SRC_NET'}){
					$customnetwork{$key}[3] = $customnetwork{$key}[3]+1;
					last;
				}
			}
			&General::writehasharray("$confignet", \%customnetwork);
		}elsif($updcounter eq 'host'){
			foreach my $key (keys %customhost) {
				if ($customhost{$key}[0] eq $fwhostsettings{'CUST_SRC_HOST'}){
					$customhost{$key}[3]=$customhost{$key}[3]+1;
				}
			}
			&General::writehasharray("$confighost", \%customhost);
		}
		$fwhostsettings{'update'}='on';
	}
		if ($fwhostsettings{'remark'} ne $fwhostsettings{'oldremark'} )
		{
			foreach my $key (sort keys %customgrp)
			{
				if($customgrp{$key}[0] eq $grp && $customgrp{$key}[1] eq $fwhostsettings{'oldremark'})
				{
					$customgrp{$key}[1]='';
					$customgrp{$key}[1]=$rem;
				}	
			}
			&General::writehasharray("$configgrp", \%customgrp);
			$errormessage='';
			$fwhostsettings{'update'}='on';
		}
		#check if ruleupdate is needed
		if($count > 0 )
		{
			&rules;
		}
		&addgrp;
		&viewtablegrp;
}
if ($fwhostsettings{'ACTION'} eq 'saveservice')
{
	my $ICMP;
	&General::readhasharray("$configsrv", \%customservice );
	$errormessage=&checkports(\%customservice);
	if ($fwhostsettings{'PROT'} eq 'ICMP'){
		&General::readhasharray("${General::swroot}/fwhosts/icmp-types", \%icmptypes);
		foreach my $key (keys %icmptypes){
			if ("$icmptypes{$key}[0] ($icmptypes{$key}[1])" eq $fwhostsettings{'ICMP_TYPES'}){
					$ICMP=$icmptypes{$key}[0];
			}
		}
	}
	if($ICMP eq ''){$ICMP='BLANK';}
	if (!$errormessage){
		my $key = &General::findhasharraykey (\%customservice);
		foreach my $i (0 .. 4) { $customservice{$key}[$i] = "";}
		$customservice{$key}[0] = $fwhostsettings{'SRV_NAME'};
		$customservice{$key}[1] = $fwhostsettings{'SRV_PORT'};
		$customservice{$key}[2] = $fwhostsettings{'PROT'};
		$customservice{$key}[3] = $ICMP;
		$customservice{$key}[4] = 0;
		&General::writehasharray("$configsrv", \%customservice );
		#reset fields
		$fwhostsettings{'SRV_NAME'}='';
		$fwhostsettings{'SRV_PORT'}='';
		$fwhostsettings{'PROT'}='';
		$fwhostsettings{'ICMP_TYPES'}='';
	}
	&addservice;
}
if ($fwhostsettings{'ACTION'} eq 'saveservicegrp')
{
	my $prot;
	my $port;
	my $count=0;
	&General::readhasharray("$configsrvgrp", \%customservicegrp );
	&General::readhasharray("$configsrv", \%customservice );
	$errormessage=&checkservicegroup;
	if (!$errormessage){
		#on first save, we have to enter a dummy value
		if ($fwhostsettings{'CUST_SRV'} eq ''){$fwhostsettings{'CUST_SRV'}=$Lang::tr{'fwhost empty'};}
		#on update, we have to delete the dummy entry
		foreach my $key (keys %customservicegrp){
			if ($customservicegrp{$key}[2] eq $Lang::tr{'fwhost empty'}){
				delete $customservicegrp{$key};
				last;
			}
		}
		&General::writehasharray("$configsrvgrp", \%customservicegrp );
		#check if remark has also changed
		if ($fwhostsettings{'SRVGRP_REMARK'} ne $fwhostsettings{'oldsrvgrpremark'} && $fwhostsettings{'updatesrvgrp'} eq 'on')
		{
			foreach my $key (keys %customservicegrp)
			{
				if($customservicegrp{$key}[0] eq $fwhostsettings{'SRVGRP_NAME'} && $customservicegrp{$key}[1] eq $fwhostsettings{'oldsrvgrpremark'})
				{
					$customservicegrp{$key}[1]='';
					$customservicegrp{$key}[1]=$fwhostsettings{'SRVGRP_REMARK'};
				}	
			}
		}
		#get count used
		foreach my $key (keys %customservicegrp)
		{
			if($customservicegrp{$key}[0] eq $fwhostsettings{'SRVGRP_NAME'})
			{
				$count=$customservicegrp{$key}[5];
				last;
			}
		}
		if ($count eq '' ){$count='0';}
			
		foreach my $key (sort keys %customservice){
			if($customservice{$key}[0] eq $fwhostsettings{'CUST_SRV'}){
				$port=$customservice{$key}[1];
				$prot=$customservice{$key}[2];
				$customservice{$key}[4]++;
			}
		}
		&General::writehasharray("$configsrv", \%customservice );
		my $key = &General::findhasharraykey (\%customservicegrp);
		foreach my $i (0 .. 3) { $customservice{$key}[$i] = "";}
		$customservicegrp{$key}[0] = $fwhostsettings{'SRVGRP_NAME'};
		$customservicegrp{$key}[1] = $fwhostsettings{'SRVGRP_REMARK'};
		$customservicegrp{$key}[2] = $fwhostsettings{'CUST_SRV'};
		$customservicegrp{$key}[3] = $count;
		&General::writehasharray("$configsrvgrp", \%customservicegrp );
		$fwhostsettings{'updatesrvgrp'}='on';
	}
	if ($fwhostsettings{'SRVGRP_REMARK'} ne $fwhostsettings{'oldsrvgrpremark'} && $errormessage){
		foreach my $key (keys %customservicegrp)
		{
			if($customservicegrp{$key}[0] eq $fwhostsettings{'SRVGRP_NAME'} && $customservicegrp{$key}[1] eq $fwhostsettings{'oldsrvgrpremark'})
			{
				$customservicegrp{$key}[1]='';
				$customservicegrp{$key}[1]=$fwhostsettings{'SRVGRP_REMARK'};
			}	
		}
		&General::writehasharray("$configsrvgrp", \%customservicegrp);
		$errormessage='';
		$hint=$Lang::tr{'fwhost changeremark'};
		$fwhostsettings{'update'}='on';
	}
	if ($count gt 0){
		&rules;
	}
	&addservicegrp;
	&viewtableservicegrp;
}
# edit
if ($fwhostsettings{'ACTION'} eq 'editnet')
{
	&addnet;
	&viewtablenet;
}
if ($fwhostsettings{'ACTION'} eq 'edithost')
{
	&addhost;
	&viewtablehost;
}
if ($fwhostsettings{'ACTION'} eq 'editgrp')
{
	$fwhostsettings{'update'}='on';
	&addgrp;
	&viewtablegrp;
}
if ($fwhostsettings{'ACTION'} eq 'editservice')
{
	$fwhostsettings{'updatesrv'}='on';
	&addservice;
}
if ($fwhostsettings{'ACTION'} eq 'editservicegrp')
{
	$fwhostsettings{'updatesrvgrp'} = 'on';
	&addservicegrp;
	&viewtableservicegrp;
}
# reset
if ($fwhostsettings{'ACTION'} eq 'resetnet')
{
	$fwhostsettings{'HOSTNAME'} ="";
	$fwhostsettings{'IP'} 		="";
	$fwhostsettings{'SUBNET'}	="";
	&showmenu;
}
if ($fwhostsettings{'ACTION'} eq 'resethost')
{
	$fwhostsettings{'HOSTNAME'} ="";
	$fwhostsettings{'IP'} 		="";
	$fwhostsettings{'type'} 	="";
	&showmenu;
}
# delete
if ($fwhostsettings{'ACTION'} eq 'delnet')
{
	&General::readhasharray("$confignet", \%customnetwork);
	foreach my $key (keys %customnetwork) {
		if($fwhostsettings{'key'} eq $customnetwork{$key}[0]){
			delete $customnetwork{$key};
			&General::writehasharray("$confignet", \%customnetwork);
			last;
		}
	}
	&addnet;
	&viewtablenet;
}
if ($fwhostsettings{'ACTION'} eq 'delhost')
{
	&General::readhasharray("$confighost", \%customhost);
	foreach my $key (keys %customhost) {
		if($fwhostsettings{'key'} eq $customhost{$key}[0]){
			delete $customhost{$key};
			&General::writehasharray("$confighost", \%customhost);
			last;
		}
	}
	&addhost;
	&viewtablehost;
}
if ($fwhostsettings{'ACTION'} eq 'deletegrphost')
{
	&General::readhasharray("$configgrp", \%customgrp);
	foreach my $key (keys %customgrp){
		if($customgrp{$key}[0].",".$customgrp{$key}[1].",".$customgrp{$key}[2].",".$customgrp{$key}[3] eq $fwhostsettings{'delhost'}){
			#decrease count from source host/net
			if ($customgrp{$key}[3] eq 'Custom Network'){
				&General::readhasharray("$confignet", \%customnetwork);
				foreach my $key1 (keys %customnetwork){
						if ($customnetwork{$key1}[0] eq $customgrp{$key}[2]){
						$customnetwork{$key1}[3] = $customnetwork{$key1}[3]-1;
						last;
					}
				}
				&General::writehasharray("$confignet", \%customnetwork);
			}
			if ($customgrp{$key}[3] eq 'Custom Host'){
				&General::readhasharray("$confighost", \%customhost);
				foreach my $key1 (keys %customhost){
					if ($customhost{$key1}[0] eq $customgrp{$key}[2]){
						$customhost{$key1}[3] = $customhost{$key1}[3]-1;
						last;
					}
				}
				&General::writehasharray("$confighost", \%customhost);
			}
			delete $customgrp{$key};
		}
	}
	&General::writehasharray("$configgrp", \%customgrp);
	&rules;
	&addgrp;
	&viewtablegrp;
}
if ($fwhostsettings{'ACTION'} eq 'delgrp')
{
	&General::readhasharray("$configgrp", \%customgrp);
	&decrease($fwhostsettings{'grp_name'});
	foreach my $key (sort keys %customgrp)
	{
		if($customgrp{$key}[0] eq $fwhostsettings{'grp_name'})
		{
			delete $customgrp{$key};
		}
	}
	&General::writehasharray("$configgrp", \%customgrp);
	$fwhostsettings{'grp_name'}='';
	&addgrp;
	&viewtablegrp;
}
if ($fwhostsettings{'ACTION'} eq 'delservice')
{
	&General::readhasharray("$configsrv", \%customservice);
	foreach my $key (keys %customservice) {
		if($customservice{$key}[0] eq $fwhostsettings{'SRV_NAME'}){
			#&deletefromgrp($customhost{$key}[0],$configgrp);
			delete $customservice{$key};
			&General::writehasharray("$configsrv", \%customservice);
			last;
		}
	}
	$fwhostsettings{'SRV_NAME'}='';
	$fwhostsettings{'SRV_PORT'}='';
	$fwhostsettings{'PROT'}='';
	&addservice;
}
if ($fwhostsettings{'ACTION'} eq 'delservicegrp')
{
	&General::readhasharray("$configsrvgrp", \%customservicegrp);
	&decreaseservice($fwhostsettings{'SRVGRP_NAME'});
	foreach my $key (sort keys %customservicegrp)
	{
		if($customservicegrp{$key}[0] eq $fwhostsettings{'SRVGRP_NAME'})
		{
			delete $customservicegrp{$key};
		}
	}
	&General::writehasharray("$configsrvgrp", \%customservicegrp);
	$fwhostsettings{'SRVGRP_NAME'}='';
	&addservicegrp;
	&viewtableservicegrp;
}
if ($fwhostsettings{'ACTION'} eq 'delgrpservice')
{
	&General::readhasharray("$configsrvgrp", \%customservicegrp);
	&General::readhasharray("$configsrv", \%customservice);
	foreach my $key (keys %customservicegrp){
		if($customservicegrp{$key}[0].",".$customservicegrp{$key}[1].",".$customservicegrp{$key}[2].",".$customservicegrp{$key}[3] eq $fwhostsettings{'delsrvfromgrp'})
		{
			#decrease count from source service
			foreach my $key1 (sort keys %customservice){
				if($customservice{$key1}[0] eq $customservicegrp{$key}[2]){
					$customservice{$key1}[4]--;
					last;
				}
			}
			&General::writehasharray("$configsrv", \%customservice);
			delete $customservicegrp{$key}
		}
	}
	&General::writehasharray("$configsrvgrp", \%customservicegrp);
	&rules;
	&addservicegrp;
	&viewtableservicegrp;
	
}
if ($fwhostsettings{'ACTION'} eq $Lang::tr{'fwhost newnet'})
{
	&addnet;
	&viewtablenet;
}
if ($fwhostsettings{'ACTION'} eq $Lang::tr{'fwhost newhost'})
{
	&addhost;
	&viewtablehost;
}
if ($fwhostsettings{'ACTION'} eq $Lang::tr{'fwhost newgrp'})
{
	&addgrp;
	&viewtablegrp;
}
if ($fwhostsettings{'ACTION'} eq $Lang::tr{'fwhost newservice'})
{
	&addservice;
}
if ($fwhostsettings{'ACTION'} eq $Lang::tr{'fwhost newservicegrp'})
{
	&addservicegrp;
	&viewtableservicegrp;
}
###  VIEW  ###
if($fwhostsettings{'ACTION'} eq '')
{
	&showmenu;
}
###  FUNCTIONS  ###
sub showmenu
{
	
	&Header::openbox('100%', 'left',$Lang::tr{'fwhost menu'});
	print<<END;
	<table border='0' width='100%'><form method='post'>
	<tr><td><input type='submit' name='ACTION' value='$Lang::tr{'fwhost newnet'}' /><input type='submit' name='ACTION' value='$Lang::tr{'fwhost newhost'}' /><input type='submit' name='ACTION' value='$Lang::tr{'fwhost newgrp'}' /></td>
	<td align='right'><input type='submit' name='ACTION' value='$Lang::tr{'fwhost newservice'}' /><input type='submit' name='ACTION' value='$Lang::tr{'fwhost newservicegrp'}' /></td></tr>
	<tr><td colspan='6'><hr></hr></td></tr></table></form>
END
	
	&Header::closebox();
	
}
# Add
sub addnet
{
	&error;
	&showmenu;
	&Header::openbox('100%', 'left', $Lang::tr{'fwhost addnet'});
	$fwhostsettings{'orgname'}=$fwhostsettings{'HOSTNAME'};
	print<<END;
	<table border='0' width='100%'><form method='post' style='display:inline'  >
	<tr><td>$Lang::tr{'name'}:</td><td><input type='TEXT' name='HOSTNAME' id='textbox1' value='$fwhostsettings{'HOSTNAME'}' $fwhostsettings{'BLK_HOST'}><script>document.getElementById('textbox1').focus()</script></td><td>$Lang::tr{'fwhost netaddress'}</td><td><input type='TEXT' name='IP' value='$fwhostsettings{'IP'}' $fwhostsettings{'BLK_IP'} size='14'></td><td align='right'>$Lang::tr{'netmask'}:</td><td align='right'><input type='TEXT' name='SUBNET' value='$fwhostsettings{'SUBNET'}' $fwhostsettings{'BLK_IP'} size='14'></td></tr>
	<tr><td colspan='6'><hr></hr></td></tr><tr>
END
	if ($fwhostsettings{'ACTION'} eq 'editnet' || $fwhostsettings{'error'} eq 'on')
	{
		print "<td colspan='6' align='right' ><input type='submit' value='$Lang::tr{'update'}' style='min-width:100px;'><input type='hidden' name='ACTION' value='updatenet'><input type='hidden' name='orgname' value='$fwhostsettings{'orgname'}' ><input type='hidden' name='update' value='on'><input type='hidden' name='newnet' value='$fwhostsettings{'newnet'}'>";
	}else{
		print "<td colspan='6' align='right'><input type='submit' value='$Lang::tr{'save'}' style='min-width:100px;'/><input type='hidden' name='ACTION' value='savenet'><input type='hidden' name='newnet' value='on'>";
	}	
	print "</form><form method='post' style='display:inline'><input type='submit' value='$Lang::tr{'fwhost back'}' style='min-width:100px;' ><input type='hidden' name='ACTION' value='resetnet'></td></tr></table></form>";
	&Header::closebox();
}
sub addhost
{
	&error;
	&showmenu;
	&Header::openbox('100%', 'left', $Lang::tr{'fwhost addhost'});
	$fwhostsettings{'orgname'}=$fwhostsettings{'HOSTNAME'};
	print<<END;
	<table border='0' width='100%'><form method='post' style='display:inline'>
	<tr><td>$Lang::tr{'name'}:</td><td width='35%'><input type='TEXT' name='HOSTNAME' id='textbox1' value='$fwhostsettings{'HOSTNAME'}' $fwhostsettings{'BLK_HOST'} ><script>document.getElementById('textbox1').focus()</script></td><td><select name='type'>
END
	if ($fwhostsettings{'type'} eq 'ip'){print "<option value='ip' selected >IP</option>";}else{print "<option value='ip' >IP</option>";}
	if ($fwhostsettings{'type'} eq 'mac'){print "<option value='mac' selected >MAC</option>";}else{print "<option value='mac' >MAC</option>";}
	print<<END;
	</option></select></td><td align='right' width='15%'>IP/MAC:</td><td align='right'><input type='TEXT' name='IP' value='$fwhostsettings{'IP'}' $fwhostsettings{'BLK_IP'} ></td></tr>
	<tr><td colspan='7'><br><br><b>$Lang::tr{'fwhost attention'}</b><br>$Lang::tr{'fwhost macwarn'}</td></tr>
	<tr><td colspan='7'><hr></hr></td></tr>
END

	if ($fwhostsettings{'ACTION'} eq 'edithost' || $fwhostsettings{'error'} eq 'on')
	{
		
		print "	<td colspan='6' align='right'><input type='submit' value='$Lang::tr{'update'}' style='min-width:100px;'/><input type='hidden' name='ACTION' value='updatehost'><input type='hidden' name='orgname' value='$fwhostsettings{'orgname'}' ><input type='hidden' name='update' value='on'><input type='hidden' name='newhost' value='$fwhostsettings{'newhost'}'></form>";
	}else{
		print "	<td colspan='6' align='right'><input type='submit' name='savehost' value='$Lang::tr{'save'}'style='min-width:100px;' /><input type='hidden' name='ACTION' value='savehost' /><input type='hidden' name='newhost' value='on'>";
	}	
	print "	</form><form method='post' style='display:inline'><input type='submit' value='$Lang::tr{'fwhost back'}' style='min-width:100px;' ><input type='hidden' name='ACTION' value='resethost'></td></tr></table></form>";
	&Header::closebox();
}
sub addgrp
{
	&hint;
	&error;
	&showmenu;
	&Header::openbox('100%', 'left', $Lang::tr{'fwhost addgrp'});
	&General::setup_default_networks(\%defaultNetworks);
	my %checked=();
	$checked{'check1'}{'off'} = '';
	$checked{'check1'}{'on'} = '';
	$checked{'grp2'}{$fwhostsettings{'grp2'}} = 'CHECKED';
	$fwhostsettings{'oldremark'}=$fwhostsettings{'remark'};
		
		if ($fwhostsettings{'update'} eq ''){   
			print<<END;
			<table width='100%' border='0'><form method='post'>
			<tr><td>$Lang::tr{'fwhost addgrpname'}</td><td><input type='TEXT' name='grp_name' value='$fwhostsettings{'grp_name'}'></td><td>$Lang::tr{'remark'}:</td><td width='1%'><input type='TEXT' name='remark' size='35' value='$fwhostsettings{'remark'}'></tr>
			<tr><td colspan='5'><hr></td></tr></table>
END
		}else{
			print<<END;
			<table width='100%' border='0'><form method='post'>
			<tr><td nowrap='nowrap' width='16%'>$Lang::tr{'fwhost addgrpname'}</td><td><input type='TEXT' name='grp_name'  value='$fwhostsettings{'grp_name'}' readonly ></td><td>$Lang::tr{'remark'}:</td><td><input type='TEXT' name='remark' size='35' value='$fwhostsettings{'remark'}'></tr>
			<tr><td colspan='5'><hr></td></tr></table>
END
	
		}
		if ($fwhostsettings{'update'} eq 'on'){
			
				
			print<<END;
			<table width='100%' border='0'><tr><td width='1%'><input type='radio' name='grp2' value='std_net'  checked></td><td nowrap='nowrap' width='16%'>$Lang::tr{'fwhost stdnet'}</td><td><select name='DEFAULT_SRC_ADR' style='min-width:185px;'>
			
END
			foreach my $network (sort keys %defaultNetworks)
			{
				next if($defaultNetworks{$network}{'LOCATION'} eq "IPCOP");
				next if($defaultNetworks{$network}{'NAME'} eq "RED");
				print "<option value='$defaultNetworks{$network}{'NAME'}'";
				print " selected='selected'" if ($fwhostsettings{'DEFAULT_SRC_ADR'} eq $defaultNetworks{$network}{'NAME'});
				print ">$network</option>";
			}
	
			print<<END;
			</select></td><td width='1%'><input type='radio' name='grp2' value='ovpn_net'  $checked{'grp2'}{'ovpn_net'}></td><td nowrap='nowrap' width='16%'>$Lang::tr{'fwhost ccdnet'}</td><td nowrap='nowrap' width='1%'><select name='OVPN_CCD_NET' style='min-width:185px;'>
END
			&General::readhasharray("$configccdnet", \%ccdnet);
			foreach my $key (sort { uc($ccdnet{$a}[0]) cmp uc($ccdnet{$b}[0]) }  keys %ccdnet)
			{
				print"<option value='$ccdnet{$key}[0]'>$ccdnet{$key}[0]</option>";
			}
			
			print<<END;
			</select></td></tr>
			<tr><td><input type='radio' name='grp2' value='cust_net' $checked{'grp2'}{'cust_net'}></td><td>$Lang::tr{'fwhost cust net'}</td><td><select name='CUST_SRC_NET' style='min-width:185px;'>
END
			&General::readhasharray("$confignet", \%customnetwork);
			foreach my $key (sort { uc($customnetwork{$a}[0]) cmp uc($customnetwork{$b}[0]) } keys  %customnetwork) {
				print"<option>$customnetwork{$key}[0]</option>";
			}
			
			print<<END;
			</select></td><td width='1%'><input type='radio' name='grp2' value='ovpn_host' $checked{'grp2'}{'ovpn_host'}></td><td nowrap='nowrap' width='16%'>$Lang::tr{'fwhost ccdhost'}</td><td nowrap='nowrap' width='1%'><select name='OVPN_CCD_HOST' style='min-width:185px;'>
END
			&General::readhasharray("$configccdhost", \%ccdhost);
			foreach my $key (sort { uc($ccdhost{$a}[0]) cmp uc($ccdhost{$b}[0]) } keys %ccdhost)
			{
				if ($ccdhost{$key}[33] ne ''){
					print"<option value='$ccdhost{$key}[1]'>$ccdhost{$key}[1]</option>";
				}
			}
			
			print<<END;
			</select></td></tr>
			<tr><td valign='top'><input type='radio' name='grp2' value='cust_host' $checked{'grp2'}{'cust_host'}></td><td valign='top'>$Lang::tr{'fwhost cust addr'}</td><td><select name='CUST_SRC_HOST' style='min-width:185px;'>
END
			&General::readhasharray("$confighost", \%customhost);
			foreach my $key (sort { uc($customhost{$a}[0]) cmp uc($customhost{$b}[0]) } keys %customhost) {
				print"<option>$customhost{$key}[0]</option>";
			}
			print<<END;
			</select></td><td width='1%'><input type='radio' name='grp2' value='ovpn_n2n' $checked{'grp2'}{'ovpn_n2n'}></td><td valign='top'>$Lang::tr{'fwhost ovpn_n2n'}</td><td colspan='3'><select name='OVPN_N2N' style='min-width:185px;'>
END
			&General::readhasharray("$configccdhost", \%ccdhost);
			foreach my $key (sort { uc($ccdhost{$a}[0]) cmp uc($ccdhost{$b}[0]) } keys %ccdhost) {
				if($ccdhost{$key}[3] eq 'net'){
					print"<option>$ccdhost{$key}[1]</option>";
				}
			}
			print<<END;
			</select></td></tr>
			<tr><td colspan='3'></td><td valign='top'><input type='radio' name='grp2' value='ipsec_net' $checked{'grp2'}{'ipsec_net'}></td><td valign='top'>$Lang::tr{'fwhost ipsec net'}</td><td><select name='IPSEC_NET' style='min-width:185px;'>
END
			&General::readhasharray("$configipsec", \%ipsecconf);
			foreach my $key (sort { uc($ipsecconf{$a}[0]) cmp uc($ipsecconf{$b}[0]) } keys %ipsecconf) {
				if ($ipsecconf{$key}[3] eq 'net'){
					print"<option value='$ipsecconf{$key}[1]'>$ipsecconf{$key}[1]</option>";
				}
			}
			print<<END;
			</select></td></tr></table>
END
#			<td colspan='3'></td><td valign='top'><input type='radio' name='grp2' value='ipsec_host' $checked{'grp2'}{'ipsec_host'}></td><td valign='top'>$Lang::tr{'fwhost ipsec host'}</td><td><select name='IPSEC_HOST' style='min-width:185px;'>
#END
#			&General::readhasharray("$configipsec", \%ipsecconf);
#			foreach my $key (sort { uc($ipsecconf{$a}[0]) cmp uc($ipsecconf{$b}[0]) } keys %ipsecconf) {
#				if ($ipsecconf{$key}[3] eq 'host'){
#					print"<option>$ipsecconf{$key}[1]</option>";
#				}
#			}
#			print<<END;
#			</select></td></tr>
#			<tr>
			print<<END;
			<br><br><br>
			<b>$Lang::tr{'fwhost attention'}:</b><br>
			$Lang::tr{'fwhost macwarn'}<br><hr>
END
		}
		print<<END;
		<table border='0' width='100%'>
		<tr><td align='right'><input type='submit' value='$Lang::tr{'add'}' style='min-width:100px;' /><input type='hidden' name='oldremark' value='$fwhostsettings{'oldremark'}'><input type='hidden' name='ACTION' value='savegrp' ></form><form method='post' style='display:inline'><input type='submit' value='$Lang::tr{'fwhost back'}' style='min-width:100px;'><input type='hidden' name='ACTION' value'reset'></td></td>
		</table></form>
END
	
	&Header::closebox();
}
sub addservice
{
	&error;
	&showmenu;
	&Header::openbox('100%', 'left', $Lang::tr{'fwhost newservice'});
	if ($fwhostsettings{'updatesrv'} eq 'on')
	{
		$fwhostsettings{'oldsrvname'} = $fwhostsettings{'SRV_NAME'};
		$fwhostsettings{'oldsrvport'} = $fwhostsettings{'SRV_PORT'};
		$fwhostsettings{'oldsrvprot'} = $fwhostsettings{'PROT'};
	}
	print<<END;
	<table width='100%' border='0'><form method='post'>
	<tr><td width='1%' nowrap='nowrap'>$Lang::tr{'fwhost srv_name'}:</td><td width='1%' nowrap='nowrap'><input type='text' name='SRV_NAME' id='textbox1' value='$fwhostsettings{'SRV_NAME'}'><script>document.getElementById('textbox1').focus()</script></td><td width='1%' nowrap='nowrap'>$Lang::tr{'fwhost prot'}:</td><td><select name='PROT'>
END
	foreach ("TCP","UDP","ICMP")
	{
		if ($_ eq $fwhostsettings{'PROT'})
		{
			print"<option selected>$_</option>";
		}else{
			print"<option>$_</option>";
		}
	}
	print<<END;
	</select></td><td>$Lang::tr{'fwhost port'}:</td><td><input type='text' name='SRV_PORT' value='$fwhostsettings{'SRV_PORT'}' maxlength='11' size='9'></td></tr>
	<tr><td></td><td></td><td nowrap='nowrap'>$Lang::tr{'fwhost icmptype'}</td><td colspan='4'><select name='ICMP_TYPES'>
END
	&General::readhasharray("${General::swroot}/fwhosts/icmp-types", \%icmptypes);
	print"<option>All ICMP-Types</option>";
	foreach my $key (sort { uc($icmptypes{$a}[0]) cmp uc($icmptypes{$b}[0]) }keys %icmptypes){
		print"<option>$icmptypes{$key}[0] ($icmptypes{$key}[1])</option>";
	}
	
	print<<END;
	</select></td>
	<tr><td colspan='6'><hr></td></tr>
	<tr><td colspan='6' align='right'>
END
	if ($fwhostsettings{'updatesrv'} eq 'on')
	{
		print<<END;
		<input type='submit' value='$Lang::tr{'update'}'style='min-width:100px;' >
		<input type='hidden' name='ACTION' value='updateservice'>
		<input type='hidden' name='oldsrvname' value='$fwhostsettings{'oldsrvname'}'>
		<input type='hidden' name='oldsrvport' value='$fwhostsettings{'oldsrvport'}'>
		<input type='hidden' name='oldsrvprot' value='$fwhostsettings{'oldsrvprot'}'></form>
END
		
	}else{	
		print"<input type='submit' value='$Lang::tr{'save'}' style='min-width:100px;'><input type='hidden' name='ACTION' value='saveservice'></form>";
	}
	print<<END;
	<form style='display:inline;' method='post'><input type='submit' value='$Lang::tr{'fwhost back'}' style='min-width:100px;'></form></td></tr>
	</table></form>
	
	
END
	&Header::closebox();
	&viewtableservice;
}
sub addservicegrp
{
	&hint;
	&error;
	&showmenu;
	&Header::openbox('100%', 'left', $Lang::tr{'fwhost newservicegrp'});
	$fwhostsettings{'oldsrvgrpremark'}=$fwhostsettings{'SRVGRP_REMARK'};
	
	if ($fwhostsettings{'updatesrvgrp'} eq ''){
		print<<END;
		<table width='100%' border='0'><form method='post'>
		<tr><td>$Lang::tr{'fwhost addgrpname'}</td><td><input type='text' name='SRVGRP_NAME' value='$fwhostsettings{'SRVGRP_NAME'}'></td><td>$Lang::tr{'remark'}:</td><td width='1%'><input type='text' name='SRVGRP_REMARK' size='35' value='$fwhostsettings{'SRVGRP_REMARK'}'></td></tr>
		<tr><td colspan='4'><hr></td></td></tr>
		</table>
END
	}else{
		print<<END;
		<table width='100%' border='0'><form method='post'>
		<tr><td>$Lang::tr{'fwhost addgrpname'}</td><td><input type='text' name='SRVGRP_NAME' value='$fwhostsettings{'SRVGRP_NAME'}' readonly ></td><td>$Lang::tr{'remark'}:</td><td width='1%'><input type='text' name='SRVGRP_REMARK' size='35' value='$fwhostsettings{'SRVGRP_REMARK'}'></td></tr>
		<tr><td colspan='4'><hr></td></td></tr>
		</table>
END
	}
	if($fwhostsettings{'updatesrvgrp'} eq 'on'){
	print<<END;
	<table border='0' width='100%'>
	<tr><td width='1%' nowrap='nowrap'>$Lang::tr{'fwhost cust service'}</td><td><select name='CUST_SRV' style='min-width:185px;'>
END
	&General::readhasharray("$configsrv", \%customservice);
	foreach my $key (sort {$a <=> $b}  keys %customservice)
	{
		print "<option>$customservice{$key}[0]</option>";
	}
	print<<END;
	</select></td></tr>
	<tr><td colspan='4'><br><br><br></td></tr>
	<tr><td colspan='4'><hr></td></tr>
	</table>
END
	}
	print<<END;
	<table width='100%' border='0'>
	<tr><td align='right'><input type='submit' value='$Lang::tr{'add'}' style='min-width:100px;' /><input type='hidden' name='updatesrvgrp' value='$fwhostsettings{'updatesrvgrp'}'><input type='hidden' name='oldsrvgrpremark' value='$fwhostsettings{'oldsrvgrpremark'}'><input type='hidden' name='ACTION' value='saveservicegrp' ></form><form style='display:inline;' method='post'><input type='submit' value='$Lang::tr{'fwhost back'}' style='min-width:100px;'></td></tr>
	</table></form>
END
	
	&Header::closebox();
}
# View
sub viewtablenet
{
	if(! -z $confignet){
		&Header::openbox('100%', 'left', $Lang::tr{'fwhost cust net'});
		&General::readhasharray("$confignet", \%customnetwork);
		if (!keys %customnetwork) 
		{ 
			print "<center><b>$Lang::tr{'fwhost empty'}</b>"; 
		}else{
			print<<END;
			<table border='0' width='100%'>
			<tr><td align='center'><b>$Lang::tr{'name'}</td><td align='center'><b>$Lang::tr{'fwhost netaddress'}</td><td align='center'><b>$Lang::tr{'netmask'}</td><td align='center'><b>$Lang::tr{'used'}</td><td></td><td width='3%'></td></tr>
END
		}
		my $count=0;
		foreach my $key (sort {$a <=> $b} keys %customnetwork) {
			if ($fwhostsettings{'ACTION'} eq 'editnet' && $fwhostsettings{'HOSTNAME'} eq $customnetwork{$key}[0]) {
				print" <tr bgcolor='${Header::colouryellow}'>";
			}elsif ($count % 2)
			{ 
				print" <tr bgcolor='$color{'color22'}'>";
			}else
			{
				print" <tr bgcolor='$color{'color20'}'>";
			}
			print<<END;
			<td width='40%'><form method='post'>$customnetwork{$key}[0]</td><td width=25%'>$customnetwork{$key}[1]</td><td width='25%'>$customnetwork{$key}[2]</td><td align='center'>$customnetwork{$key}[3]x</td>
			<td width='1%'><input type='image' src='/images/edit.gif' align='middle' alt=$Lang::tr{'edit'} title=$Lang::tr{'edit'} />
			<input type='hidden' name='ACTION' value='editnet'>
			<input type='hidden' name='HOSTNAME' value='$customnetwork{$key}[0]' />
			<input type='hidden' name='IP' value='$customnetwork{$key}[1]' />
			<input type='hidden' name='SUBNET' value='$customnetwork{$key}[2]' />
			</td></form>
END
			if($customnetwork{$key}[3] == '0')
			{
				print"<td width='1%'><form method='post'><input type='image' src='/images/delete.gif' align='middle' alt=$Lang::tr{'delete'} title=$Lang::tr{'delete'} /><input type='hidden' name='ACTION' value='delnet' /><input type='hidden' name='key' value='$customnetwork{$key}[0]' /></td></form></tr>";
			}else{
				print"<td></td></form></tr>";
			}
			$count++;
		}
		print"</table>";
		&Header::closebox();
	}	

}
sub viewtablehost
{
	if (! -z $confighost){
		&Header::openbox('100%', 'left', $Lang::tr{'fwhost cust addr'});
		&General::readhasharray("$confighost", \%customhost);
		if (!keys %customhost) 
		{ 
			print "<center><b>$Lang::tr{'fwhost empty'}</b>"; 
		}else{
		print<<END;
		<table border='0' width='100%'>
		<tr><td align='center'><b>$Lang::tr{'name'}</td><td align='center'><b>$Lang::tr{'fwhost ip_mac'}</td><td align='center'><b>$Lang::tr{'used'}</td><td></td><td width='3%'></td></tr>
END
	}
		my $count=0;
		foreach my $key (sort { uc($customhost{$a}[0]) cmp uc($customhost{$b}[0])||  $a <=> $b } keys %customhost) {
			if ( ($fwhostsettings{'ACTION'} eq 'edithost' || $fwhostsettings{'error'}) && $fwhostsettings{'HOSTNAME'} eq $customhost{$key}[0]) {
				print" <tr bgcolor='${Header::colouryellow}'>";
			}elsif ($count % 2){ print" <tr bgcolor='$color{'color22'}'>";}
			else{            print" <tr bgcolor='$color{'color20'}'>";}
			my ($ip,$sub)=split(/\//,$customhost{$key}[2]);
			print<<END;
			<td width='40%'><form method='post'>$customhost{$key}[0]</td><td width='50%'>$customhost{$key}[2]</td><td align='center'>$customhost{$key}[3]x</td>
			<td width='1%'><input type='image' src='/images/edit.gif' align='middle' alt=$Lang::tr{'edit'} title=$Lang::tr{'edit'} />
			<input type='hidden' name='ACTION' value='edithost' />
			<input type='hidden' name='HOSTNAME' value='$customhost{$key}[0]' />
			<input type='hidden' name='IP' value='$ip' />
			<input type='hidden' name='type' value='$customhost{$key}[1]' />
			</td></form>
END
			if($customhost{$key}[3] == '0')
			{
				print"<td width='1%'><form method='post'><input type='image' src='/images/delete.gif' align='middle' alt=$Lang::tr{'delete'} title=$Lang::tr{'delete'} /><input type='hidden' name='ACTION' value='delhost' /><input type='hidden' name='key' value='$customhost{$key}[0]' /></td></form></tr>";
			}else{
				print"<td width='1%'></td></tr>";
			}
			$count++;
		}
		print"</table>";
		&Header::closebox();
	}
}
sub viewtablegrp
{
	if(! -z "$configgrp"){
	&Header::openbox('100%', 'left', $Lang::tr{'fwhost cust grp'});
	&General::readhasharray("$configgrp", \%customgrp);
	&General::readhasharray("$configipsec", \%ipsecconf);
	&General::readhasharray("$configccdhost", \%ccdhost);
	&General::readhasharray("$configccdnet", \%ccdnet);
	&General::readhasharray("$confighost", \%customhost);
	&General::readhasharray("$confignet", \%customnetwork);
	my @grp=();
	my $helper='';
	my $count=0;
	my $grpname;
	my $remark;
	my $number=keys %customgrp;
	if (!keys %customgrp) 
	{ 
		print "<center><b>$Lang::tr{'fwhost empty'}</b>"; 
	}else{
		foreach my $key (sort { uc($customgrp{$a}[0]) cmp uc($customgrp{$b}[0]) } sort { uc($customgrp{$a}[2]) cmp uc($customgrp{$b}[2]) } keys %customgrp){
			
			$count++;
			if ($helper ne $customgrp{$key}[0]){
				$grpname=$customgrp{$key}[0];
				$remark=$customgrp{$key}[1];
				if($count >=2){print"</table>";}
				print "<br><b><u>$grpname</u></b> &nbsp &nbsp";
				print " <b>$Lang::tr{'remark'}:</b>&nbsp $remark &nbsp " if ($remark ne '');
				print "<b>$Lang::tr{'used'}:</b> $customgrp{$key}[4]x";
				if($customgrp{$key}[4] == '0')
				{
					print"<form method='post' style='display:inline'><input type='image' src='/images/delete.gif' alt=$Lang::tr{'delete'} title=$Lang::tr{'delete'} align='right' /><input type='hidden' name='grp_name' value='$grpname' ><input type='hidden' name='ACTION' value='delgrp'></form>";
				}
				print"<form method='post' style='display:inline'><input type='image' src='/images/edit.gif' alt=$Lang::tr{'edit'} title=$Lang::tr{'edit'} align='right' /><input type='hidden' name='grp_name' value='$grpname' ><input type='hidden' name='remark' value='$remark' ><input type='hidden' name='ACTION' value='editgrp'></form>";
				print"<table width='100%' style='border: 1px solid  #000000;' rules='none' ><tr><td align='center'><b>Name</b></td><td align='center'><b>$Lang::tr{'ip address'}</b></td><td align='center' width='25%'><b>$Lang::tr{'fwhost type'}</td></tr>";
			}
			if ( ($fwhostsettings{'ACTION'} eq 'editgrp' || $fwhostsettings{'update'} ne '') && $fwhostsettings{'grp_name'} eq $customgrp{$key}[0]) {
				print" <tr bgcolor='${Header::colouryellow}'>";
				}elsif ($count %2 == 0){print"<tr bgcolor='$color{'color22'}'>";}else{print"<tr bgcolor='$color{'color20'}'>";}
			my $ip=&getipforgroup($customgrp{$key}[2],$customgrp{$key}[3]);	
			if ($ip eq ''){print"<tr bgcolor='${Header::colouryellow}'>";}
			
			
			print "<td width='39%'>";
			if($customgrp{$key}[3] eq 'Standard Network'){
				print &get_name($customgrp{$key}[2])."</td>";
			}else{
				print "$customgrp{$key}[2]</td>";
			}
			if ($ip eq '' && $customgrp{$key}[2] ne $Lang::tr{'fwhost empty'}){
				print "<td align='center'>$Lang::tr{'fwhost deleted'}</td><td>$customgrp{$key}[3]</td><td width='1%'><form method='post'>";   
			}else{
				print"<td>$ip</td><td>$customgrp{$key}[3]</td><td width='1%'><form method='post'>";
			}
			if ($number gt '1' && $ip ne ''){
				print"<input type='image' src='/images/delete.gif' align='middle' alt=$Lang::tr{'delete'} title=$Lang::tr{'delete'} />";
			}
			print"<input type='hidden' name='ACTION' value='deletegrphost'><input type='hidden' name='delhost' value='$grpname,$remark,$customgrp{$key}[2],$customgrp{$key}[3]'></form></td></tr>";
			
			$helper=$customgrp{$key}[0];
		}
		print"</table>";
		
	}
	&Header::closebox();
}

}
sub viewtableservice
{
	my $count=0;
	if(! -z "$configsrv")
	{
		&Header::openbox('100%', 'left', $Lang::tr{'fwhost services'});
		&General::readhasharray("$configsrv", \%customservice);
		print<<END;
			<table width='100%' border='0'>
			<tr><td align='center'><b>$Lang::tr{'fwhost srv_name'}</td><td align='center'><b>$Lang::tr{'fwhost prot'}</td><td align='center'><b>$Lang::tr{'fwhost port'}</td><td align='center'><b>ICMP</td><td align='center'><b>$Lang::tr{'fwhost used'}</td><td></td><td width='3%'></td></tr>
END
		foreach my $key (sort { uc($customservice{$a}[0]) cmp uc($customservice{$b}[0])||  $a <=> $b } keys %customservice)
		{
			$count++;
			if ( ($fwhostsettings{'updatesrv'} eq 'on' || $fwhostsettings{'error'}) && $fwhostsettings{'SRV_NAME'} eq $customservice{$key}[0]) {
				print" <tr bgcolor='${Header::colouryellow}'>";
			}elsif ($count % 2){ print" <tr bgcolor='$color{'color22'}'>";}else{ 	print" <tr bgcolor='$color{'color20'}'>";}
			print<<END;
			<td>$customservice{$key}[0]</td><td align='center'>$customservice{$key}[2]</td><td align='center'>$customservice{$key}[1]</td><td align='center'>
END
			if($customservice{$key}[3] ne 'BLANK'){print $customservice{$key}[3];}
		
			print<<END;
			</td><td align='center'>$customservice{$key}[4]x</td>
			<td width='1%'><form method='post'><input type='image' src='/images/edit.gif' align='middle' alt=$Lang::tr{'edit'} title=$Lang::tr{'edit'} /><input type='hidden' name='ACTION' value='editservice' />
			<input type='hidden' name='SRV_NAME' value='$customservice{$key}[0]' />
			<input type='hidden' name='SRV_PORT' value='$customservice{$key}[1]' />
			<input type='hidden' name='PROT' value='$customservice{$key}[2]' /></form></td>
END
			if ($customservice{$key}[4] eq '0')
			{
				print"<td width='1%'><form method='post'><input type='image' src='/images/delete.gif' align='middle' alt=$Lang::tr{'delete'} title=$Lang::tr{'delete'} /><input type='hidden' name='ACTION' value='delservice' /><input type='hidden' name='SRV_NAME' value='$customservice{$key}[0]'></td></tr></form>";
			}else{
				print"<td></td></tr>";
			}
		}
		print"</table>";
		&Header::closebox();
	}
}
sub viewtableservicegrp
{
	my $count=0;
	my $grpname;
	my $remark;
	my $helper;
	my $port;
	my $protocol;
	if (! -z $configsrvgrp){
		&Header::openbox('100%', 'left', $Lang::tr{'fwhost cust srvgrp'});
		&General::readhasharray("$configsrvgrp", \%customservicegrp);
		&General::readhasharray("$configsrv", \%customservice);
		my $number= keys %customservicegrp;
		foreach my $key (sort { uc($customservicegrp{$a}[0]) cmp uc($customservicegrp{$b}[0])||  $a <=> $b } keys %customservicegrp){
			$count++;
			if ($helper ne $customservicegrp{$key}[0]){
				$grpname=$customservicegrp{$key}[0];
				$remark=$customservicegrp{$key}[1];
				if($count >=2){print"</table>";}
				print "<br><b><u>$grpname</u></b> &nbsp &nbsp ";
				print "<b>$Lang::tr{'remark'}:</b>&nbsp $remark " if ($remark ne '');
				print "&nbsp <b>$Lang::tr{'used'}:</b> $customservicegrp{$key}[3]x";
				if($customservicegrp{$key}[3] == '0')
				{
					print"<form method='post' style='display:inline'><input type='image' src='/images/delete.gif' alt=$Lang::tr{'delete'} title=$Lang::tr{'delete'} align='right' /><input type='hidden' name='SRVGRP_NAME' value='$grpname' ><input type='hidden' name='ACTION' value='delservicegrp'></form>";
				}
				print"<form method='post' style='display:inline'><input type='image' src='/images/edit.gif' alt=$Lang::tr{'edit'} title=$Lang::tr{'edit'} align='right' /><input type='hidden' name='SRVGRP_NAME' value='$grpname' ><input type='hidden' name='SRVGRP_REMARK' value='$remark' ><input type='hidden' name='ACTION' value='editservicegrp'></form>";
				print"<table width='100%' style='border: 1px solid  #000000;' rules='none' ><tr><td align='center'><b>Name</b></td><td align='center'><b>$Lang::tr{'port'}</b></td><td align='center' width='25%'><b>$Lang::tr{'fwhost prot'}</td></tr>";
			}
			if( $fwhostsettings{'SRVGRP_NAME'} eq $customservicegrp{$key}[0]) {
				print" <tr bgcolor='${Header::colouryellow}'>";
			}
			if ($count %2 == 0){
				print"<tr bgcolor='$color{'color22'}'>";
			}else{
				print"<tr bgcolor='$color{'color20'}'>";
			}
			print "<td width='39%'>$customservicegrp{$key}[2]</td>";
			foreach my $srv (sort keys %customservice){
				if ($customservicegrp{$key}[2] eq $customservice{$srv}[0]){
					$protocol=$customservice{$srv}[2];
					$port=$customservice{$srv}[1];
					last;
				}
			}
			print"<td align='center'>$port</td><td align='center'>$protocol</td><td width='1%'><form method='post'>";
			if ($number gt '1'){
				print"<input type='image' src='/images/delete.gif' align='middle' alt=$Lang::tr{'delete'} title=$Lang::tr{'delete'} />";
			}
			print"<input type='hidden' name='ACTION' value='delgrpservice'><input type='hidden' name='delsrvfromgrp' value='$grpname,$remark,$customservicegrp{$key}[2],$customservicegrp{$key}[3]'></form></td></tr>";
			$helper=$customservicegrp{$key}[0];
		}
		print"</table>";
		&Header::closebox();
	}
}
# Check
sub checkname
{
	my %hash=%{(shift)};
	foreach my $key (keys %hash) {
		if($hash{$key}[0] eq $fwhostsettings{'HOSTNAME'}){
			return 0;
		}
	}
	return 1;
	
}
sub checkip
{
	
	my %hash=%{(shift)};
	my $a=shift;
	foreach my $key (keys %hash) {
		if($hash{$key}[$a] eq $fwhostsettings{'IP'}."/".&General::iporsubtodec($fwhostsettings{'SUBNET'})){
			return 0;
		}
	}
	return 1;
}
sub checksubnet
{
	
	my %hash=%{(shift)};
	&General::readhasharray("$confignet", \%hash);
	foreach my $key (keys %hash) {
		if(&General::IpInSubnet($fwhostsettings{'IP'},$hash{$key}[1],$hash{$key}[2]))
		{
			return 1;
		}
	}
	return 0;
}
sub checkservicegroup
{
	&General::readhasharray("$configsrvgrp", \%customservicegrp);
	
	
	#check name
	if ( ! &validhostname($fwhostsettings{'SRVGRP_NAME'}))
	{
		$errormessage.=$Lang::tr{'fwhost err name'}."<br>";
		return $errormessage;
	}
	#check remark
	if ( ($fwhostsettings{'SRVGRP_REMARK'} ne '') && (! &validhostname($fwhostsettings{'SRVGRP_REMARK'})))
	{
		$errormessage.=$Lang::tr{'fwhost err remark'}."<br>";
	}
	#check empty selectbox
	if (keys %customservice lt 1)
	{
		$errormessage.=$Lang::tr{'fwhost err groupempty'}."<br>";
	}
	
	#check if name already exists
	if ($fwhostsettings{'updatesrvgrp'} ne 'on'){
		foreach my $key (keys %customservicegrp) {
			if( $customservicegrp{$key}[0] eq $fwhostsettings{'SRVGRP_NAME'} ){
				$errormessage.=$Lang::tr{'fwhost err grpexist'}."<br>";
			
			}
		}
	}
	#check if service already exists in group
	foreach my $key (keys %customservicegrp) {
			if($customservicegrp{$key}[0] eq $fwhostsettings{'SRVGRP_NAME'} && $customservicegrp{$key}[2] eq $fwhostsettings{'CUST_SRV'} ){
				$errormessage.=$Lang::tr{'fwhost err srvexist'}."<br>";
			
			}
		}
	
	
	
	return $errormessage;
}
sub error
{
	if ($errormessage) {
		&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
		print "<class name='base'>$errormessage\n";
		print "&nbsp;</class>\n";
		&Header::closebox();
	}
}
sub hint
{
	if ($hint) {
		&Header::openbox('100%', 'left', $Lang::tr{'fwhost hint'});
		print "<class name='base'>$hint\n";
		print "&nbsp;</class>\n";
		&Header::closebox();
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
sub deletefromgrp
{
	my $target=shift;
	my $config=shift;
	my %hash=();
	&General::readhasharray("$config",\%hash);
	foreach my $key (keys %hash) {
		$errormessage.="lese $hash{$key}[2] und $target<br>";
		if($hash{$key}[2] eq $target){
			
			delete $hash{$key};
			$errormessage.="Habe $target aus Gruppe gelöscht!<br>";
		}
	}
	&General::writehasharray("$config",\%hash);
	
}
sub plausicheck
{
	
	my $edit=shift;
	#check hostname
	if (!&General::validhostname($fwhostsettings{'HOSTNAME'}))
	{
		$errormessage=$errormessage.$Lang::tr{'fwhost err name'};
		$fwhostsettings{'BLK_IP'}='readonly';
		$fwhostsettings{'HOSTNAME'} = $fwhostsettings{'orgname'};
		if ($fwhostsettings{'update'} eq 'on'){$fwhostsettings{'ACTION'}=$edit;}
	}
	#check if name collides with CCD Netname

	&General::readhasharray("$configccdnet", \%ccdnet);
	foreach my $key (keys %ccdnet) {
		if($ccdnet{$key}[0] eq $fwhostsettings{'HOSTNAME'}){
			$errormessage=$errormessage.$Lang::tr{'fwhost err isccdnet'};;
			$fwhostsettings{'HOSTNAME'} = $fwhostsettings{'orgname'};
			if ($fwhostsettings{'update'} eq 'on'){$fwhostsettings{'ACTION'}=$edit;}
			last;
		}
	}

	#check if IP collides with CCD NetIP
	if ($fwhostsettings{'type'} ne 'mac'){
		&General::readhasharray("$configccdnet", \%ccdnet);
		foreach my $key (keys %ccdnet) {
			my $test=(&General::getnetworkip($fwhostsettings{'IP'},&General::iporsubtocidr($fwhostsettings{'SUBNET'})))."/".$fwhostsettings{'SUBNET'};
			if($ccdnet{$key}[1] eq $test){
				$errormessage=$errormessage.$Lang::tr{'fwhost err isccdipnet'};
				$fwhostsettings{'IP'} = $fwhostsettings{'orgip'};
				$fwhostsettings{'SUBNET'} = $fwhostsettings{'orgsubnet'};
				if ($fwhostsettings{'update'} eq 'on'){$fwhostsettings{'ACTION'}=$edit;}
				last;
			}
		}
	}
	
	
	
	#check if name collides with CCD Hostname
	&General::readhasharray("$configccdhost", \%ccdhost);
	foreach my $key (keys %ccdhost) {
		my ($ip,$sub)=split(/\//,$ccdhost{$key}[33]);
		if($ip eq $fwhostsettings{'IP'}){
			$errormessage=$Lang::tr{'fwhost err isccdiphost'};
			if ($fwhostsettings{'update'} eq 'on'){$fwhostsettings{'ACTION'}=$edit;}
			last;
		}
	}
	#check if IP collides with CCD HostIP (only hosts)
	if ($edit eq 'edithost')
	{
		foreach my $key (keys %ccdhost) {
			if($ccdhost{$key}[1] eq $fwhostsettings{'HOSTNAME'}){
				$errormessage=$Lang::tr{'fwhost err isccdhost'};
				$fwhostsettings{'IP'} = $fwhostsettings{'orgname'};
				if ($fwhostsettings{'update'} eq 'on'){$fwhostsettings{'ACTION'}=$edit;}
				last;
			}
		}
	}
	#check if network with this name already exists
	&General::readhasharray("$confignet", \%customnetwork);
	if (!&checkname(\%customnetwork))
	{
		$errormessage=$errormessage."<br>".$Lang::tr{'fwhost err netexist'};
		$fwhostsettings{'HOSTNAME'} = $fwhostsettings{'orgname'};
		if ($fwhostsettings{'update'} eq 'on'){$fwhostsettings{'ACTION'}=$edit;}
	}	
	#check if network ip already exists		
	if (!&checkip(\%customnetwork,1))
	{
		$errormessage=$errormessage."<br>".$Lang::tr{'fwhost err net'};
		if ($fwhostsettings{'update'} eq 'on'){$fwhostsettings{'ACTION'}=$edit;}
	}	
	#check if host with this name already exists
	&General::readhasharray("$confighost", \%customhost);
	if (!&checkname(\%customhost))
	{
		$errormessage=$errormessage."<br>".$Lang::tr{'fwhost err hostexist'};
		$fwhostsettings{'HOSTNAME'} = $fwhostsettings{'orgname'};
		if ($fwhostsettings{'update'} eq 'on'){$fwhostsettings{'ACTION'}=$edit;}
	}
	#check if host with this ip already exists
	if (!&checkip(\%customhost,2))
	{
		$errormessage=$errormessage."<br>".$Lang::tr{'fwhost err ipcheck'};
		
	}
		
	
	return;
}
sub getipforgroup
{
	my $name=$_[0],
	my $type=$_[1];
	my $value;
	
	#get address from IPSEC NETWORK
	if ($type eq 'IpSec Network'){
		foreach my $key (keys %ipsecconf) {
			if ($ipsecconf{$key}[1] eq $name){
				return $ipsecconf{$key}[11];
			}
		}
		&deletefromgrp($name,$configgrp);
	}
	
	#get address from IPSEC HOST
	if ($type eq 'IpSec Host'){
		foreach my $key (keys %ipsecconf) {
			if ($ipsecconf{$key}[1] eq $name){
				return $ipsecconf{$key}[10];
			}
		}
		&deletefromgrp($name,$configgrp);
	}
		
	#get address from ovpn ccd Net-2-Net
	if ($type eq 'OpenVPN N-2-N'){
		foreach my $key (keys %ccdhost) {
			if($ccdhost{$key}[1] eq $name){
				my ($a,$b) = split ("/",$ccdhost{$key}[11]);
				$b=&General::iporsubtodec($b);
				return "$a/$b";
			}
		}
		&deletefromgrp($name,$configgrp);
	}
	
	#get address from ovpn ccd static host
	if ($type eq 'OpenVPN static host'){
		foreach my $key (keys %ccdhost) {
			if($ccdhost{$key}[1] eq $name){
				my ($a,$b) = split (/\//,$ccdhost{$key}[33]);
				$b=&General::iporsubtodec($b);
				return "$a/$b";
			}
		}
		&deletefromgrp($name,$configgrp);
	}
	
	#get address from  ovpn ccd static net
	if ($type eq 'OpenVPN static network'){
		foreach my $key (keys %ccdnet) {
			if ($ccdnet{$key}[0] eq $name){
				my ($a,$b) = split (/\//,$ccdnet{$key}[1]);
				$b=&General::iporsubtodec($b);
				return "$a/$b";
			}
		}
	}
	
	#check custom addresses
	if ($type eq 'Custom Host'){
		foreach my $key (keys %customhost) {
			if ($customhost{$key}[0] eq $name){
				return $customhost{$key}[2];
			}
		}
	}
	
	##check custom networks
	if ($type eq 'Custom Network'){
		foreach my $key (keys %customnetwork) {
			if($customnetwork{$key}[0] eq $name){
				return $customnetwork{$key}[1]."/".$customnetwork{$key}[2];
			}
		}
	}
	
	#check standard networks
	if ($type eq 'Standard Network'){
		if ($name =~ /OpenVPN/i){
			my %ovpn=();
			&General::readhash("${General::swroot}/ovpn/settings",\%ovpn);
			return $ovpn{'DOVPN_SUBNET'};
		}
		if ($name eq 'GREEN'){
			my %hash=();
			&General::readhash("${General::swroot}/ethernet/settings",\%hash);
			return $hash{'GREEN_NETADDRESS'}."/".$hash{'GREEN_NETMASK'};
		}
		if ($name eq 'BLUE'){
			my %hash=();
			&General::readhash("${General::swroot}/ethernet/settings",\%hash);
			return $hash{'BLUE_NETADDRESS'}."/".$hash{'BLUE_NETMASK'};
		}
		if ($name eq 'ORANGE'){
			my %hash=();
			&General::readhash("${General::swroot}/ethernet/settings",\%hash);
			return $hash{'ORANGE_NETADDRESS'}."/".$hash{'ORANGE_NETMASK'};
		}
		if ($name eq 'ALL'){
			return "0.0.0.0/0.0.0.0";
		}
		if ($name =~ /IPsec/i){
			my %hash=();
			&General::readhash("${General::swroot}/vpn/settings",\%hash);
			return $hash{'RW_NET'};
		}
	}
}
sub rules
{
	system ("/usr/local/bin/forwardfwctrl");
	system("rm ${General::swroot}/forward/reread");
}
sub decrease
{
	my $grp=$_[0];
	&General::readhasharray("$confignet", \%customnetwork);
	&General::readhasharray("$confighost", \%customhost);
	foreach my $key (sort keys %customgrp ){
		if ( ($customgrp{$key}[0] eq $grp) && ($customgrp{$key}[3] eq 'Custom Network')){
			foreach my $key1 (sort keys %customnetwork){
				if ($customnetwork{$key1}[0] eq $customgrp{$key}[2]){
					$customnetwork{$key1}[3]=$customnetwork{$key1}[3]-1;
					last;
				}
			}
		}
		
		if (($customgrp{$key}[0] eq $grp) && ($customgrp{$key}[3] eq 'Custom Host')){
			foreach my $key2 (sort keys %customhost){
				if ($customhost{$key2}[0] eq $customgrp{$key}[2]){
					$customhost{$key2}[3]=$customhost{$key2}[3]-1;
					last;
				}
			}
				
		}
	}
	&General::writehasharray("$confignet", \%customnetwork);
	&General::writehasharray("$confighost", \%customhost);
}
sub decreaseservice
{
	my $grp=$_[0];
	&General::readhasharray("$configsrv", \%customservice);
	&General::readhasharray("$configsrvgrp", \%customservicegrp);
	
	foreach my $key (sort keys %customservicegrp){
		if ($customservicegrp{$key}[0] eq $grp ){
			foreach my $key2 (sort keys %customservice){
				if ($customservice{$key2}[0] eq $customservicegrp{$key}[2]){
					$customservice{$key2}[4]--;
				}
			}
		}
	}
	&General::writehasharray("$configsrv", \%customservice);
	
}
sub checkports
{
	
	my %hash=%{(shift)};
	#check empty fields
	if ($fwhostsettings{'SRV_NAME'} eq '' ){
		$errormessage=$Lang::tr{'fwhost err name1'};
	}
	if ($fwhostsettings{'SRV_PORT'} eq '' && $fwhostsettings{'PROT'} ne 'ICMP'){
		$errormessage=$Lang::tr{'fwhost err port'};
	}
	#check valid name
	if (! &validhostname($fwhostsettings{'SRV_NAME'})){
		$errormessage="<br>".$Lang::tr{'fwhost err name'};
	}
	#change dashes with :
	$fwhostsettings{'SRV_PORT'}=~ tr/-/:/;
		
	if ($fwhostsettings{'SRV_PORT'} eq "*") {
		$fwhostsettings{'SRV_PORT'} = "1:65535";
	}
	if ($fwhostsettings{'SRV_PORT'} =~ /^(\D)\:(\d+)$/) {
		$fwhostsettings{'SRV_PORT'} = "1:$2";
	}
	if ($fwhostsettings{'SRV_PORT'} =~ /^(\d+)\:(\D)$/) {
		$fwhostsettings{'SRV_PORT'} = "$1:65535";
	}
	if($fwhostsettings{'PROT'} ne 'ICMP'){
		$errormessage = $errormessage.&General::validportrange($fwhostsettings{'SRV_PORT'}, 'src');
	}
	# a new service has to have a different name
	foreach my $key (keys %hash){
		if ($hash{$key}[0] eq $fwhostsettings{'SRV_NAME'}){
			$errormessage = "<br>".$Lang::tr{'fwhost err srv exists'};
			last;
		}
	}
	return $errormessage;
}
sub validhostname
{
	# Checks a hostname against RFC1035
        my $hostname = $_[0];

	# Each part should be at least two characters in length
	# but no more than 63 characters
	if (length ($hostname) < 1 || length ($hostname) > 63) {
		return 0;}
	# Only valid characters are a-z, A-Z, 0-9 and -
	if ($hostname !~ /^[a-zA-ZäöüÖÄÜ0-9-_()\/\s]*$/) {
		return 0;}
	# First character can only be a letter or a digit
	if (substr ($hostname, 0, 1) !~ /^[a-zA-ZöäüÖÄÜ0-9]*$/) {
		return 0;}
	# Last character can only be a letter or a digit
	if (substr ($hostname, -1, 1) !~ /^[a-zA-ZöäüÖÄÜ0-9()]*$/) {
		return 0;}
	return 1;
}

&Header::closebigbox();
&Header::closepage();
