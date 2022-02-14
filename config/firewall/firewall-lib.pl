#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2021 Alexander Marx <amarx@ipfire.org>                        #
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
use experimental 'smartmatch';

no warnings 'uninitialized';

package fwlib;

my %customnetwork=();
my %customhost=();
my %customgrp=();
my %customlocationgrp=();
my %customservice=();
my %customservicegrp=();
my %ccdnet=();
my %ccdhost=();
my %ipsecconf=();
my %ipsecsettings=();
my %netsettings=();
my %ovpnsettings=();
my %aliases=();

require '/var/ipfire/general-functions.pl';
require '/var/ipfire/location-functions.pl';

my $confignet		= "${General::swroot}/fwhosts/customnetworks";
my $confighost		= "${General::swroot}/fwhosts/customhosts";
my $configgrp 		= "${General::swroot}/fwhosts/customgroups";
my $configlocationgrp 	= "${General::swroot}/fwhosts/customlocationgrp";
my $configsrv 		= "${General::swroot}/fwhosts/customservices";
my $configsrvgrp	= "${General::swroot}/fwhosts/customservicegrp";
my $configccdnet 	= "${General::swroot}/ovpn/ccd.conf";
my $configccdhost	= "${General::swroot}/ovpn/ovpnconfig";
my $configipsec		= "${General::swroot}/vpn/config";
my $configovpn		= "${General::swroot}/ovpn/settings";
my $val;
my $field;
my $netsettings		= "${General::swroot}/ethernet/settings";

&General::readhash("/var/ipfire/ethernet/settings", \%netsettings);
&General::readhash("${General::swroot}/ovpn/settings", \%ovpnsettings);
&General::readhash("${General::swroot}/vpn/settings", \%ipsecsettings);

&General::readhasharray("$confignet", \%customnetwork);
&General::readhasharray("$confighost", \%customhost);
&General::readhasharray("$configgrp", \%customgrp);
&General::readhasharray("$configlocationgrp", \%customlocationgrp);
&General::readhasharray("$configccdnet", \%ccdnet);
&General::readhasharray("$configccdhost", \%ccdhost);
&General::readhasharray("$configipsec", \%ipsecconf);
&General::readhasharray("$configsrv", \%customservice);
&General::readhasharray("$configsrvgrp", \%customservicegrp);
&General::get_aliases(\%aliases);

# Get all available locations.
my @available_locations = &get_locations();

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
		#adapt $val to reflect real name without subnet (if rule with only one ipsec subnet is created)
		my @tmpval = split (/\|/, $val);
		$val = $tmpval[0];
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
sub get_ipsec_id {
	my $val = shift;

	foreach my $key (keys %ipsecconf) {
		if ($ipsecconf{$key}[1] eq $val) {
			return $key;
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
		return "0.0.0.0/0";
	}elsif($val =~ /OpenVPN/i){
		return "$ovpnsettings{'DOVPN_SUBNET'}";
	}elsif($val =~ /IPsec/i){
		return "$ipsecsettings{'RW_NET'}";
	}elsif($val eq 'IPFire'){
		return ;
	}
}
sub get_interface
{
	my $net=shift;
	if($net eq "$netsettings{'GREEN_NETADDRESS'}/$netsettings{'GREEN_NETMASK'}"){
		return "$netsettings{'GREEN_DEV'}";
	}
	if($net eq "$netsettings{'ORANGE_NETADDRESS'}/$netsettings{'ORANGE_NETMASK'}"){
		return "$netsettings{'ORANGE_DEV'}";
	}
	if($net eq "$netsettings{'BLUE_NETADDRESS'}/$netsettings{'BLUE_NETMASK'}"){
		return "$netsettings{'BLUE_DEV'}";
	}
	if($net eq "0.0.0.0/0") {
		return &get_external_interface();
	}
	return "";
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
sub get_addresses
{
	my $hash = shift;
	my $key  = shift;
	my $type = shift;

	my @addresses = ();
	my $addr_type;
	my $value;
	my $group_name;

	if ($type eq "src") {
		$addr_type = $$hash{$key}[3];
		$value = $$hash{$key}[4];

	} elsif ($type eq "tgt") {
		$addr_type = $$hash{$key}[5];
		$value = $$hash{$key}[6];
	}

	if ($addr_type ~~ ["cust_grp_src", "cust_grp_tgt"]) {
		foreach my $grp (sort {$a <=> $b} keys %customgrp) {
			if ($customgrp{$grp}[0] eq $value) {
				my @address = &get_address($customgrp{$grp}[3], $customgrp{$grp}[2], $type);
				next if ($address[0][0] eq 'none');
				if (@address) {
					push(@addresses, @address);
				}
			}
		}
	}elsif ($addr_type ~~ ["cust_location_src", "cust_location_tgt"] && $value =~ "group:") {
		$value=substr($value,6);
		foreach my $grp (sort {$a <=> $b} keys %customlocationgrp) {
			if ($customlocationgrp{$grp}[0] eq $value) {
				my @address = &get_address($addr_type, $customlocationgrp{$grp}[2], $type);

				if (@address) {
					push(@addresses, @address);
				}
			}
		}
	} else {
		my @address = &get_address($addr_type, $value, $type);

		if (@address) {
			push(@addresses, @address);
		}
	}

	return @addresses;
}
sub get_address
{
	my $key   = shift;
	my $value = shift;
	my $type  = shift;

	my @ret = ();

	# If the user manually typed an address, we just check if it is a MAC
	# address. Otherwise, we assume that it is an IP address.
	if ($key ~~ ["src_addr", "tgt_addr"]) {
		if (&General::validmac($value)) {
			push(@ret, ["-m mac --mac-source $value", ""]);
		} else {
			push(@ret, [$value, ""]);
		}

	# If a default network interface (GREEN, BLUE, etc.) is selected, we
	# try to get the corresponding address of the network.
	} elsif ($key ~~ ["std_net_src", "std_net_tgt", "Standard Network"]) {
		my $external_interface = &get_external_interface();

		my $network_address = &get_std_net_ip($value, $external_interface);

		if ($network_address) {
			my $interface = &get_interface($network_address);
			push(@ret, [$network_address, $interface]);
		}

	# Custom networks.
	} elsif ($key ~~ ["cust_net_src", "cust_net_tgt", "Custom Network"]) {
		my $network_address = &get_net_ip($value);
		if ($network_address) {
			push(@ret, [$network_address, ""]);
		}

	# Custom hosts.
	} elsif ($key ~~ ["cust_host_src", "cust_host_tgt", "Custom Host"]) {
		my $host_address = &get_host_ip($value, $type);
		if ($host_address) {
			push(@ret, [$host_address, ""]);
		}

	# OpenVPN networks.
	} elsif ($key ~~ ["ovpn_net_src", "ovpn_net_tgt", "OpenVPN static network"]) {
		my $network_address = &get_ovpn_net_ip($value, 1);
		if ($network_address) {
			push(@ret, [$network_address, ""]);
		}

	# OpenVPN hosts.
	} elsif ($key ~~ ["ovpn_host_src", "ovpn_host_tgt", "OpenVPN static host"]) {
		my $host_address = &get_ovpn_host_ip($value, 33);
		if ($host_address) {
			push(@ret, [$host_address, ""]);
		}

	# OpenVPN N2N.
	} elsif ($key ~~ ["ovpn_n2n_src", "ovpn_n2n_tgt", "OpenVPN N-2-N"]) {
		my $network_address = &get_ovpn_n2n_ip($value, 11);
		if ($network_address) {
			push(@ret, [$network_address, ""]);
		}

	# IPsec networks.
	} elsif ($key ~~ ["ipsec_net_src", "ipsec_net_tgt", "IpSec Network"]) {
		#Check if we have multiple subnets and only want one of them
		if ( $value =~ /\|/ ){
			my @parts = split(/\|/, $value);
			push(@ret, [$parts[1], ""]);
		}else{
			my $interface_mode = &get_ipsec_net_ip($value, 36);
			if ($interface_mode ~~ ["gre", "vti"]) {
				my $id = &get_ipsec_id($value);
				push(@ret, ["0.0.0.0/0", "${interface_mode}${id}"]);
			} else {
				my $network_address = &get_ipsec_net_ip($value, 11);
				my @nets = split(/\|/, $network_address);
				foreach my $net (@nets) {
					push(@ret, [$net, ""]);
				}
			}
		}

	# The firewall's own IP addresses.
	} elsif ($key ~~ ["ipfire", "ipfire_src"]) {
		# ALL
		if ($value eq "ALL") {
			push(@ret, ["0/0", ""]);

		# GREEN
		} elsif ($value eq "GREEN") {
			push(@ret, [$netsettings{"GREEN_ADDRESS"}, ""]);

		# BLUE
		} elsif ($value eq "BLUE") {
			push(@ret, [$netsettings{"BLUE_ADDRESS"}, ""]);

		# ORANGE
		} elsif ($value eq "ORANGE") {
			push(@ret, [$netsettings{"ORANGE_ADDRESS"}, ""]);

		# RED
		} elsif ($value ~~ ["RED", "RED1"]) {
			my $address = &get_external_address();
			if ($address) {
				push(@ret, [$address, ""]);
			}

		# Aliases
		} else {
			my $alias = &get_alias($value);
			if ($alias) {
				push(@ret, [$alias, ""]);
			}
		}

	# Handle rule options with a location as source.
	} elsif ($key eq "cust_location_src") {
		# Check if the given location is available.
		if(&location_is_available($value)) {
			# Get external interface.
			my $external_interface = &get_external_interface();

			push(@ret, ["-m set --match-set CC_$value src", "$external_interface"]);
		}

	# Handle rule options with a location as target.
	} elsif ($key eq "cust_location_tgt") {
		# Check if the given location is available.
		if(&location_is_available($value)) {
			# Get external interface.
			my $external_interface = &get_external_interface();

			push(@ret, ["-m set --match-set CC_$value dst", "$external_interface"]);
		}

	# If nothing was selected, we assume "any".
	} else {
		push(@ret, ["0/0", ""]);
	}

	return @ret;
}
sub get_external_interface()
{
	open(IFACE, "/var/ipfire/red/iface") or return "";
	my $iface = <IFACE>;
	close(IFACE);

	return $iface;
}
sub get_external_address()
{
	open(ADDR, "/var/ipfire/red/local-ipaddress") or return "";
	my $address = <ADDR>;
	close(ADDR);

	return $address;
}
sub get_alias
{
	my $id = shift;

	foreach my $alias (sort keys %aliases) {
		if ($id eq $alias) {
			return $aliases{$alias}{"IPT"};
		}
	}
}

sub get_nat_address {
	my $zone = shift;
	my $source = shift;

	# Any static address of any zone.
	if ($zone eq "AUTO") {
		if ($source && ($source !~ m/mac/i )) {
			my $firewall_ip = &get_internal_firewall_ip_address($source, 1);
			if ($firewall_ip) {
				return $firewall_ip;
			}

			$firewall_ip = &get_matching_firewall_address($source, 1);
			if ($firewall_ip) {
				return $firewall_ip;
			}
		}

		return &get_external_address();

	} elsif ($zone eq "RED" || $zone eq "GREEN" || $zone eq "ORANGE" || $zone eq "BLUE") {
		return $netsettings{$zone . "_ADDRESS"};

	} elsif ($zone ~~ ["Default IP", "ALL"]) {
		return &get_external_address();

	} else {
		my $alias = &get_alias($zone);
		unless ($alias) {
			$alias = &get_external_address();
		}
		return $alias;
	}

	print_error("Could not find NAT address");
}

sub get_internal_firewall_ip_addresses
{
	my $use_orange = shift;

	my @zones = ("GREEN", "BLUE");
	if ($use_orange) {
		push(@zones, "ORANGE");
	}

	my @addresses = ();
	for my $zone (@zones) {
		next unless (exists $netsettings{$zone . "_ADDRESS"});

		my $zone_address = $netsettings{$zone . "_ADDRESS"};
		push(@addresses, $zone_address);
	}

	return @addresses;
}
sub get_matching_firewall_address
{
	my $addr = shift;
	my $use_orange = shift;

	my ($address, $netmask) = split("/", $addr);

	my @zones = ("GREEN", "BLUE");
	if ($use_orange) {
		push(@zones, "ORANGE");
	}

	foreach my $zone (@zones) {
		next unless (exists $netsettings{$zone . "_ADDRESS"});

		my $zone_subnet = $netsettings{$zone . "_NETADDRESS"};
		my $zone_mask   = $netsettings{$zone . "_NETMASK"};

		if (&General::IpInSubnet($address, $zone_subnet, $zone_mask)) {
			return $netsettings{$zone . "_ADDRESS"};
		}
	}

	return 0;
}
sub get_internal_firewall_ip_address
{
	my $subnet = shift;
	my $use_orange = shift;

	my ($net_address, $net_mask) = split("/", $subnet);
	if ((!$net_mask) || ($net_mask ~~ ["32", "255.255.255.255"])) {
		return 0;
	}

	# Convert net mask into correct format for &General::IpInSubnet().
	$net_mask = &General::iporsubtodec($net_mask);

	my @addresses = &get_internal_firewall_ip_addresses($use_orange);
	foreach my $zone_address (@addresses) {
		if (&General::IpInSubnet($zone_address, $net_address, $net_mask)) {
			return $zone_address;
		}
	}

	return 0;
}

sub get_locations() {
	return &Location::Functions::get_locations();
}

# Function to check if a database of a given location is
# available.
sub location_is_available($) {
	my ($requested_location) = @_;

	# Loop through the global array of available locations.
	foreach my $location (@available_locations) {
		# Check if the current processed location is the searched one.
		if($location eq $requested_location) {
			# If it is part of the array, return "1" - True.
			return 1;
		}
	}

	# If we got here, the given location is not part of the array of available
	# zones. Return nothing.
	return;
}

return 1;
