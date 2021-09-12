#!/usr/bin/perl -w
############################################################################
#                                                                          #
# This file is part of the IPFire Firewall.                                #
#                                                                          #
# IPFire is free software; you can redistribute it and/or modify           #
# it under the terms of the GNU General Public License as published by     #
# the Free Software Foundation; either version 2 of the License, or        #
# (at your option) any later version.                                      #
#                                                                          #
# IPFire is distributed in the hope that it will be useful,                #
# but WITHOUT ANY WARRANTY; without even the implied warranty of           #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
# GNU General Public License for more details.                             #
#                                                                          #
# You should have received a copy of the GNU General Public License        #
# along with IPFire; if not, write to the Free Software                    #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA #
#                                                                          #
# Copyright (C) 2014 IPFire Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################

package Network;

require "/var/ipfire/general-functions.pl";

use experimental 'smartmatch';
use Socket;

# System ethernet configuration
our %ethernet_settings = ();
&General::readhash("${General::swroot}/ethernet/settings", \%ethernet_settings);

# List of all possible network zones that can be configured
our @known_network_zones = ("red", "green", "orange", "blue");

# IPv4 netmask CIDR to dotted decimal notation conversion table
my %PREFIX2NETMASK = (
	32 => "255.255.255.255",
	31 => "255.255.255.254",
	30 => "255.255.255.252",
	29 => "255.255.255.248",
	28 => "255.255.255.240",
	27 => "255.255.255.224",
	26 => "255.255.255.192",
	25 => "255.255.255.128",
	24 => "255.255.255.0",
	23 => "255.255.254.0",
	22 => "255.255.252.0",
	21 => "255.255.248.0",
	20 => "255.255.240.0",
	19 => "255.255.224.0",
	18 => "255.255.192.0",
	17 => "255.255.128.0",
	16 => "255.255.0.0",
	15 => "255.254.0.0",
	14 => "255.252.0.0",
	13 => "255.248.0.0",
	12 => "255.240.0.0",
	11 => "255.224.0.0",
	10 => "255.192.0.0",
	 9 => "255.128.0.0",
	 8 => "255.0.0.0",
	 7 => "254.0.0.0",
	 6 => "252.0.0.0",
	 5 => "248.0.0.0",
	 4 => "240.0.0.0",
	 3 => "224.0.0.0",
	 2 => "192.0.0.0",
	 1 => "128.0.0.0",
	 0 => "0.0.0.0"
);

my %NETMASK2PREFIX = reverse(%PREFIX2NETMASK);

# Takes an IP address in dotted decimal notation and
# returns a 32 bit integer representing that IP addresss.
# Will return undef for invalid inputs.
sub ip2bin($) {
	my $address = shift;

	# This function returns undef for undefined input.
	if (!defined $address) {
		return undef;
	}

	my $address_bin = &Socket::inet_pton(AF_INET, $address);
	if ($address_bin) {
		$address_bin = unpack('N', $address_bin);
	}

	return $address_bin;
}

# Does the reverse of ip2bin().
# Will return undef for invalid inputs.
sub bin2ip($) {
	my $address_bin = shift;

	# This function returns undef for undefined input.
	if (!defined $address_bin) {
		return undef;
	}

	my $address = pack('N', $address_bin);
	if ($address) {
		$address = &Socket::inet_ntop(AF_INET, $address);
	}

	return $address;
}

# Takes two network addresses, compares them against each other
# and returns true if equal or false if not
sub network_equal {
	my $network1 = shift;
	my $network2 = shift;

	my @bin1 = &network2bin($network1);
	my @bin2 = &network2bin($network2);

	if (!defined $bin1 || !defined $bin2) {
		return undef;
	}

	if ($bin1[0] == $bin2[0] && $bin1[1] == $bin2[1]) {
		return 1;
	}

	return 0;
}

# Takes a network in either a.b.c.d/a.b.c.d or a.b.c.d/e notation
# and will return an 32 bit integer representing the start
# address and an other one representing the network mask.
sub network2bin($) {
	my $network = shift;

	my ($address, $netmask) = split(/\//, $network, 2);

	if (&check_prefix($netmask)) {
		$netmask = &convert_prefix2netmask($netmask);
	}

	my $address_bin = &ip2bin($address);
	my $netmask_bin = &ip2bin($netmask);

	if (!defined $address_bin || !defined $netmask_bin) {
		return undef;
	}

	my $network_start = $address_bin & $netmask_bin;

	return ($network_start, $netmask_bin);
}

# Deletes leading zeros in ip address
sub ip_remove_zero{
	my $address = shift;
	my @ip = split (/\./, $address);

	foreach my $octet (@ip) {
		$octet = int($octet);
	}

	$address = join (".", @ip);

	return $address;
}
# Returns True for all valid IP addresses
sub check_ip_address($) {
	my $address = shift;

	# Normalise the IP address and compare the result with
	# the input - which should obviously the same.
	my $normalised_address = &_normalise_ip_address($address);

	return ((defined $normalised_address) && ($address eq $normalised_address));
}

# Returns True for all valid prefixes.
sub check_prefix($) {
	my $prefix = shift;

	return (exists $PREFIX2NETMASK{$prefix});
}

# Returns True for all valid subnet masks.
sub check_netmask($) {
	my $netmask = shift;

	return (exists $NETMASK2PREFIX{$netmask});
}

# Returns True for all valid inputs like a.b.c.d/a.b.c.d.
sub check_ip_address_and_netmask($$) {
	my $network = shift;

	my ($address, $netmask) = split(/\//, $network, 2);

	# Check if the IP address is fine.
	#
	my $result = &check_ip_address($address);
	unless ($result) {
		return $result;
	}

	return &check_netmask($netmask);
}

# Returns True for all valid subnets like a.b.c.d/e or a.b.c.d/a.b.c.d
sub check_subnet($) {
	my $subnet = shift;

	my ($address, $network) = split(/\//, $subnet, 2);

	# Check if the IP address is fine.
	my $result = &check_ip_address($address);
	unless ($result) {
		return $result;
	}

	return &check_prefix($network) || &check_netmask($network);
}

# For internal use only. Will take an IP address and
# return it in a normalised style. Like 8.8.8.010 -> 8.8.8.8.
sub _normalise_ip_address($) {
	my $address = shift;

	my $address_bin = &ip2bin($address);
	if (!defined $address_bin) {
		return undef;
	}

	return &bin2ip($address_bin);
}

# Returns the prefix for the given subnet mask.
sub convert_netmask2prefix($) {
	my $netmask = shift;

	if (exists $NETMASK2PREFIX{$netmask}) {
		return $NETMASK2PREFIX{$netmask};
	}

	return undef;
}

# Returns the subnet mask for the given prefix.
sub convert_prefix2netmask($) {
	my $prefix = shift;

	if (exists $PREFIX2NETMASK{$prefix}) {
		return $PREFIX2NETMASK{$prefix};
	}

	return undef;
}

# Takes an IP address and an offset and
# will return the offset'th IP address.
sub find_next_ip_address($$) {
	my $address = shift;
	my $offset = shift;

	my $address_bin = &ip2bin($address);
	$address_bin += $offset;

	return &bin2ip($address_bin);
}

# Returns the network address of the given network.
sub get_netaddress($) {
	my $network = shift;
	my ($network_bin, $netmask_bin) = &network2bin($network);

	if (defined $network_bin) {
		return &bin2ip($network_bin);
	}

	return undef;
}

# Returns the broadcast of the given network.
sub get_broadcast($) {
	my $network = shift;
	my ($network_bin, $netmask_bin) = &network2bin($network);

	return &bin2ip($network_bin ^ ~$netmask_bin);
}

# Returns True if $address is in $network.
sub ip_address_in_network($$) {
	my $address = shift;
	my $network = shift;

	my $address_bin = &ip2bin($address);
	return undef unless (defined $address_bin);

	my ($network_bin, $netmask_bin) = &network2bin($network);

	# Find end address
	my $broadcast_bin = $network_bin ^ (~$netmask_bin % 2 ** 32);

	return (($address_bin >= $network_bin) && ($address_bin <= $broadcast_bin));
}

sub setup_upstream_proxy() {
	my %proxysettings = ();
	&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);

	if ($proxysettings{'UPSTREAM_PROXY'}) {
		my $credentials = "";

		if ($proxysettings{'UPSTREAM_USER'}) {
			$credentials = $proxysettings{'UPSTREAM_USER'};

			if ($proxysettings{'UPSTREAM_PASSWORD'}) {
				$credentials .= ":" . $proxysettings{'UPSTREAM_PASSWORD'};
			}

			$credentials .= "@";
		}

		my $proxy = "http://" . $credentials . $proxysettings{'UPSTREAM_PROXY'};

		$ENV{'http_proxy'} = $proxy;
		$ENV{'https_proxy'} = $proxy;
		$ENV{'ftp_proxy'} = $proxy;
	}
}

sub list_wireless_interfaces() {
	my %interfaces = ();

	opendir(INTERFACES, "/sys/class/net");

	my $intf;
	while ($intf = readdir(INTERFACES)) {
		# Is this a wireless interface?
		opendir(PHY80211, "/sys/class/net/$intf/phy80211") or next;
		closedir(PHY80211);

		# Read the MAC address
		my $address = &get_nic_property($intf, "address");

		$interfaces{$address} = "$address ($intf)";
	}

	closedir(INTERFACES);

	return %interfaces;
}

my %wireless_status = ();

sub _get_wireless_status($) {
	my $intf = shift;

	if (!$wireless_status{$intf}) {
		$wireless_status{$intf} = join('\n', &General::system_output("iwconfig", "$intf"));
	}

	return $wireless_status{$intf};
}

sub wifi_get_essid($) {
	my $status = &_get_wireless_status(shift);

	my ($essid) = $status =~ /ESSID:\"(.*)\"/;

	return $essid;
}

sub wifi_get_frequency($) {
	my $status = &_get_wireless_status(shift);

	my ($frequency) = $status =~ /Frequency:(\d+\.\d+ GHz)/;

	return $frequency;
}

sub wifi_get_access_point($) {
	my $status = &_get_wireless_status(shift);

	my ($access_point) = $status =~ /Access Point: ([0-9A-F:]+)/;

	return $access_point;
}

sub wifi_get_bit_rate($) {
	my $status = &_get_wireless_status(shift);

	my ($bit_rate) = $status =~ /Bit Rate=(\d+ [GM]b\/s)/;

	return $bit_rate;
}

sub wifi_get_link_quality($) {
	my $status = &_get_wireless_status(shift);

	my ($cur, $max) = $status =~ /Link Quality=(\d+)\/(\d+)/;

	if($max > 0) {
		return sprintf('%.0f', ($cur * 100) / $max);
	}

	return 0;
}

sub wifi_get_signal_level($) {
	my $status = &_get_wireless_status(shift);

	my ($signal_level) = $status =~ /Signal level=(\-\d+ dBm)/;

	return $signal_level;
}

sub get_hardware_address($) {
	my $ip_address = shift;
	my $ret;

	open(FILE, "/proc/net/arp") or die("Could not read ARP table");

	while (<FILE>) {
		my ($ip_addr, $hwtype, $flags, $hwaddr, $mask, $device) = split(/\s+/, $_);
		if ($ip_addr eq $ip_address) {
			$ret = $hwaddr;
			last;
		}
	}

	close(FILE);

	return $ret;
}

sub get_nic_property {
	my $nicname = shift;
	my $property = shift;
	my $result;

	open(FILE, "/sys/class/net/$nicname/$property") or die("Could not read property $property for $nicname");
	$result = <FILE>;
	close(FILE);

	chomp($result);

	return $result;
}

sub valid_mac($) {
	my $mac = shift;

	return $mac =~ /^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$/;
}

# Compares two MAC addresses and returns true if they are equal
sub is_mac_equal {
	my $mac_1 = uc shift; # convert to upper case
	my $mac_2 = uc shift;

	if(valid_mac($mac_1) && valid_mac($mac_2) && ($mac_1 eq $mac_2)) {
		return 1;
	}

	return 0;
}

sub random_mac {
	my $address = "02";

	for my $i (0 .. 4) {
		$address = sprintf("$address:%02x", int(rand(255)));
	}

	return $address;
}

sub get_mac_by_name($) {
	my $mac = shift;

	if ((!&valid_mac($mac)) && ($mac ne "")) {
		if (-e "/sys/class/net/$mac/") {
			$mac = get_nic_property($mac, "address");
		}
	}

	return $mac;
}

sub get_intf_by_address($) {
	my $address = shift;

	opendir(INTERFACES, "/sys/class/net");

	while (my $intf = readdir(INTERFACES)) {
		next if ($intf eq "." or $intf eq "..");

		my $intf_address = &get_nic_property($intf, "address");

		# Skip interfaces without addresses
		next if ($intf_address eq "");

		# Return a match
		return $intf if ($intf_address eq $address);
	}

	closedir(INTERFACES);

	return undef;
}

#
## Function to get a list of all available network zones.
#
sub get_available_network_zones () {
	# Obtain the configuration type from the netsettings hash.
	my $config_type = $ethernet_settings{'CONFIG_TYPE'};

	# Hash which contains the conversation from the config mode
	# to the existing network interface names. They are stored like
	# an array.
	#
	# Mode "0" red is a modem and green
	# Mode "1" red is a netdev and green
	# Mode "2" red, green and orange
	# Mode "3" red, green and blue
	# Mode "4" red, green, blue, orange
	my %config_type_to_interfaces = (
		"0" => [ "red", "green" ],
		"1" => [ "red", "green" ],
		"2" => [ "red", "green", "orange" ],
		"3" => [ "red", "green", "blue" ],
		"4" => [ "red", "green", "blue", "orange" ]
	);

	# Obtain and dereference the corresponding network interaces based on the read
	# network config type.
	my @network_zones = @{ $config_type_to_interfaces{$config_type} };

	# Return them.
	return @network_zones;
}

#
## Function to check if a network zone is available in the current configuration
#
sub is_zone_available() {
	my $zone = lc shift;
	
	# Make sure the zone is valid
	die("Unknown network zone '$zone'") unless ($zone ~~ @known_network_zones);
	
	# Get available zones and return result
	my @available_zones = get_available_network_zones();
	return ($zone ~~ @available_zones);
}

#
## Function to determine if the RED zone is in standard IP (or modem, PPP, VDSL, ...) mode
#
sub is_red_mode_ip() {
	# Obtain the settings from the netsettings hash
	my $config_type = $ethernet_settings{'CONFIG_TYPE'};
	my $red_type = $ethernet_settings{'RED_TYPE'};

	# RED must be a network device (configuration 1-4) with dynamic or static IP
	return (($config_type ~~ [1..4]) && ($red_type ~~ ["DHCP", "STATIC"]));
}

1;

# Remove the next line to enable the testsuite
__END__

sub assert($$) {
	my $tst = shift;
	my $ret = shift;

	if ($ret) {
		return;
	}

	print "ASSERTION ERROR - $tst\n";
	exit(1);
}

sub testsuite() {
	my $result;

	my $address1 = &ip2bin("8.8.8.8");
	assert('ip2bin("8.8.8.8")', $address1 == 134744072);

	my $address2 = &bin2ip($address1);
	assert("bin2ip($address1)", $address2 eq "8.8.8.8");

	# Check if valid IP addresses are correctly recognised.
	foreach my $address ("1.2.3.4", "192.168.180.1", "127.0.0.1") {
		if (!&check_ip_address($address)) {
			print "$address is not correctly recognised as a valid IP address!\n";
			exit 1;
		};
	}

	# Check if invalid IP addresses are correctly found.
	foreach my $address ("456.2.3.4", "192.768.180.1", "127.1", "1", "a.b.c.d", "1.2.3.4.5", "1.2.3.4/12") {
		if (&check_ip_address($address)) {
			print "$address is recognised as a valid IP address!\n";
			exit 1;
		};
	}

	$result = &check_ip_address_and_netmask("192.168.180.0/255.255.255.0");
	assert('check_ip_address_and_netmask("192.168.180.0/255.255.255.0")', $result);

	$result = &convert_netmask2prefix("255.255.254.0");
	assert('convert_netmask2prefix("255.255.254.0")', $result == 23);

	$result = &convert_prefix2netmask(8);
	assert('convert_prefix2netmask(8)', $result eq "255.0.0.0");

	$result = &find_next_ip_address("1.2.3.4", 2);
	assert('find_next_ip_address("1.2.3.4", 2)', $result eq "1.2.3.6");

	$result = &network_equal("192.168.0.0/24", "192.168.0.0/255.255.255.0");
	assert('network_equal("192.168.0.0/24", "192.168.0.0/255.255.255.0")', $result);

	$result = &network_equal("192.168.0.0/24", "192.168.0.0/25");
	assert('network_equal("192.168.0.0/24", "192.168.0.0/25")', !$result);

	$result = &network_equal("192.168.0.0/24", "192.168.0.128/25");
	assert('network_equal("192.168.0.0/24", "192.168.0.128/25")', !$result);

	$result = &network_equal("192.168.0.1/24", "192.168.0.XXX/24");
	assert('network_equal("192.168.0.1/24", "192.168.0.XXX/24")', !$result);

	$result = &ip_address_in_network("10.0.1.4", "10.0.0.0/8");
	assert('ip_address_in_network("10.0.1.4", "10.0.0.0/8"', $result);

	$result = &ip_address_in_network("192.168.30.11", "192.168.30.0/255.255.255.0");
	assert('ip_address_in_network("192.168.30.11", "192.168.30.0/255.255.255.0")', $result);

	$result = &ip_address_in_network("192.168.30.11", "0.0.0.0/8");
	assert('ip_address_in_network("192.168.30.11", "0.0.0.0/8")', !$result);

	print "Testsuite completed successfully!\n";

	return 0;
}

&testsuite();
