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
no warnings 'uninitialized';

package fwlib;

my %customnetwork=();
my %customhost=();
my %customgrp=();
my %customservice=();
my %customservicegrp=();
my %ccdnet=();
my %ccdhost=();
my %ipsecconf=();
my %ipsecsettings=();
my %netsettings=();
my %ovpnsettings=();

require '/var/ipfire/general-functions.pl';

my $confignet		= "${General::swroot}/fwhosts/customnetworks";
my $confighost		= "${General::swroot}/fwhosts/customhosts";
my $configgrp 		= "${General::swroot}/fwhosts/customgroups";
my $configsrv 		= "${General::swroot}/fwhosts/customservices";
my $configsrvgrp	= "${General::swroot}/fwhosts/customservicegrp";
my $configccdnet 	= "${General::swroot}/ovpn/ccd.conf";
my $configccdhost	= "${General::swroot}/ovpn/ovpnconfig";
my $configipsec		= "${General::swroot}/vpn/config";
my $configovpn		= "${General::swroot}/ovpn/settings";
my $val;
my $field;

&General::readhash("/var/ipfire/ethernet/settings", \%netsettings);
&General::readhash("${General::swroot}/ovpn/settings", \%ovpnsettings);
&General::readhash("${General::swroot}/vpn/settings", \%ipsecsettings);


&General::readhasharray("$confignet", \%customnetwork);
&General::readhasharray("$confighost", \%customhost);
&General::readhasharray("$configgrp", \%customgrp);
&General::readhasharray("$configccdnet", \%ccdnet);
&General::readhasharray("$configccdhost", \%ccdhost);
&General::readhasharray("$configipsec", \%ipsecconf);
&General::readhasharray("$configsrv", \%customservice);
&General::readhasharray("$configsrvgrp", \%customservicegrp);

sub get_srv_prot
{
	my $val=shift;
	foreach my $key (sort {$a <=> $b} keys %customservice){
		if($customservice{$key}[0] eq $val){
			if ($customservice{$key}[0] eq $val){
				return $customservice{$key}[2];
			}
		}
	}
}
sub get_srvgrp_prot
{
	my $val=shift;
	my @ips=();
	my $tcp;
	my $udp;
	my $icmp;
	foreach my $key (sort {$a <=> $b} keys %customservicegrp){
		if($customservicegrp{$key}[0] eq $val){
			if (&get_srv_prot($customservicegrp{$key}[2]) eq 'TCP'){ 
				$tcp=1;
			}elsif(&get_srv_prot($customservicegrp{$key}[2]) eq 'UDP'){ 
				$udp=1;
			}elsif(&get_srv_prot($customservicegrp{$key}[2]) eq 'ICMP'){
				$icmp=1;
			}else{
				#Protocols used in servicegroups
				push (@ips,$customservicegrp{$key}[2]);
			}
		}
	}
	if ($tcp eq '1'){push (@ips,'TCP');}
	if ($udp eq '1'){push (@ips,'UDP');}
	if ($icmp eq '1'){push (@ips,'ICMP');}
	my $back=join(",",@ips);
	return $back;
	
}


sub get_srv_port
{
	my $val=shift;
	my $field=shift;
	my $prot=shift;
	foreach my $key (sort {$a <=> $b} keys %customservice){
		if($customservice{$key}[0] eq $val && $customservice{$key}[2] eq $prot){
			return $customservice{$key}[$field];
		}
	}
}
sub get_srvgrp_port
{
	my $val=shift;
	my $prot=shift;
	my $back;
	my $value;
	my @ips=();
	foreach my $key (sort {$a <=> $b} keys %customservicegrp){
		if($customservicegrp{$key}[0] eq $val){
			if ($prot ne 'ICMP'){
				$value=&get_srv_port($customservicegrp{$key}[2],1,$prot);
			}elsif ($prot eq 'ICMP'){
				$value=&get_srv_port($customservicegrp{$key}[2],3,$prot);
			}
			push (@ips,$value) if ($value ne '') ;
		}
	}
	if($prot ne 'ICMP'){
		if ($#ips gt 0){$back="-m multiport --dports ";}else{$back="--dport ";}
	}elsif ($prot eq 'ICMP'){
		$back="--icmp-type ";
	}
	
	$back.=join(",",@ips);
	return $back;
}
sub get_ipsec_net_ip
{
	my $val=shift;
	my $field=shift;
	foreach my $key (sort {$a <=> $b} keys %ipsecconf){
		if($ipsecconf{$key}[1] eq $val){
			return $ipsecconf{$key}[$field];
		}
	}
}
sub get_ipsec_host_ip
{
	my $val=shift;
	my $field=shift;
	foreach my $key (sort {$a <=> $b} keys %ipsecconf){
		if($ipsecconf{$key}[1] eq $val){
			return $ipsecconf{$key}[$field];
		}
	}
}
sub get_ovpn_n2n_ip
{
	my $val=shift;
	my $field=shift;
	foreach my $key (sort {$a <=> $b} keys %ccdhost){
		if($ccdhost{$key}[1] eq $val){
			return $ccdhost{$key}[$field];
		}
	}
}
sub get_ovpn_host_ip
{
	my $val=shift;
	my $field=shift;
	foreach my $key (sort {$a <=> $b} keys %ccdhost){
		if($ccdhost{$key}[1] eq $val){
			return $ccdhost{$key}[$field];
		}
	}
}
sub get_ovpn_net_ip
{
	
	my $val=shift;
	my $field=shift;
	foreach my $key (sort {$a <=> $b} keys %ccdnet){
		if($ccdnet{$key}[0] eq $val){
			return $ccdnet{$key}[$field];
		}
	}
}
sub get_grp_ip
{
	my $val=shift;
	my $src=shift;
	foreach my $key (sort {$a <=> $b} keys %customgrp){
		if ($customgrp{$key}[0] eq $val){
			&get_address($customgrp{$key}[3],$src);
		}
	}		
	
}
sub get_std_net_ip
{
	my $val=shift;
	my $con=shift;
	if ($val eq 'ALL'){
		return "0.0.0.0/0.0.0.0";
	}elsif($val eq 'GREEN'){
		return "$netsettings{'GREEN_NETADDRESS'}/$netsettings{'GREEN_NETMASK'}";
	}elsif($val eq 'ORANGE'){
		return "$netsettings{'ORANGE_NETADDRESS'}/$netsettings{'ORANGE_NETMASK'}";
	}elsif($val eq 'BLUE'){
		return "$netsettings{'BLUE_NETADDRESS'}/$netsettings{'BLUE_NETMASK'}";
	}elsif($val eq 'RED'){
		return "0.0.0.0/0 -o $con";
	}elsif($val =~ /OpenVPN/i){
		return "$ovpnsettings{'DOVPN_SUBNET'}";
	}elsif($val =~ /IPsec/i){
		return "$ipsecsettings{'RW_NET'}";
	}elsif($val eq 'IPFire'){
		return ;
	}
}
sub get_net_ip
{
	my $val=shift;
	foreach my $key (sort {$a <=> $b} keys %customnetwork){
		if($customnetwork{$key}[0] eq $val){
			return "$customnetwork{$key}[1]/$customnetwork{$key}[2]";
		}  
	}
}
sub get_host_ip
{
	my $val=shift;
	my $src=shift;
	foreach my $key (sort {$a <=> $b} keys %customhost){
		if($customhost{$key}[0] eq $val){
			if ($customhost{$key}[1] eq 'mac' && $src eq 'src'){
			return "-m mac --mac-source $customhost{$key}[2]";
			}elsif($customhost{$key}[1] eq 'ip' && $src eq 'src'){
				return "$customhost{$key}[2]";
			}elsif($customhost{$key}[1] eq 'ip' && $src eq 'tgt'){
				return "$customhost{$key}[2]";
			}elsif($customhost{$key}[1] eq 'mac' && $src eq 'tgt'){
				return "none";
			}
		}  
	}
}

return 1;
