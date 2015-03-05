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

use Socket;

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

	my $network_start = $address_bin & $netmask_bin;

	return ($network_start, $netmask_bin);
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
	my $broadcast_bin = $network_bin ^ ~$netmask_bin;

	return (($address_bin ge $network_bin) && ($address_bin le $broadcast_bin));
}

1;

# Remove the next line to enable the testsuite
__END__

sub assert($) {
	my $ret = shift;

	if ($ret) {
		return;
	}

	print "ASSERTION ERROR";
	exit(1);
}

sub testsuite() {
	my $result;

	my $address1 = &ip2bin("8.8.8.8");
	assert($address1 == 134744072);

	my $address2 = &bin2ip($address1);
	assert($address2 eq "8.8.8.8");

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
	assert($result);

	$result = &convert_netmask2prefix("255.255.254.0");
	assert($result == 23);

	$result = &convert_prefix2netmask(8);
	assert($result eq "255.0.0.0");

	$result = &find_next_ip_address("1.2.3.4", 2);
	assert($result eq "1.2.3.6");

	$result = &ip_address_in_network("10.0.1.4", "10.0.0.0/8");
	assert($result);

	return 0;
}

&testsuite();
