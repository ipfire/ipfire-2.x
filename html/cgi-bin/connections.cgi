#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2023  IPFire Team  <info@ipfire.org>                     #
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
use Switch;

# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "${General::swroot}/ids-functions.pl";
require "${General::swroot}/location-functions.pl";

my $colour_multicast = "#A0A0A0";

my %settings = ();
&General::readhash("/var/ipfire/ethernet/settings", \%settings);

&Header::showhttpheaders();

# Collect all known networks
my %networks = (
	# Localhost
	"127.0.0.0/8" => ${Header::colourfw},

	# Multicast
	"224.0.0.0/3" => $colour_multicast,

	# GREEN
	"$settings{'GREEN_ADDRESS'}/32" => ${Header::colourfw},
	"$settings{'GREEN_NETADDRESS'}/$settings{'GREEN_NETMASK'}" => ${Header::colourgreen},

	# BLUE
	"$settings{'BLUE_ADDRESS'}/32" => ${Header::colourfw},
	"$settings{'BLUE_NETADDRESS'}/$settings{'BLUE_NETMASK'}" => ${Header::colourblue},

	# ORANGE
	"$settings{'ORANGE_ADDRESS'}/32" => ${Header::colourfw},
	"$settings{'ORANGE_NETADDRESS'}/$settings{'ORANGE_NETMASK'}" => ${Header::colourorange},
);

# RED Address
my $address = &IDS::get_red_address();
if ($address) {
	$networks{"${address}/32"} = ${Header::colourfw};
}

# Add all aliases
my @aliases = &IDS::get_aliases();
for my $alias (@aliases) {
	$networks{"${alias}/32"} = ${Header::colourfw};
}

my %interfaces = (
	$settings{'GREEN_DEV'}  => ${Header::colourgreen},
	$settings{'BLUE_DEV'}   => ${Header::colourblue},
	$settings{'ORANGE_DEV'} => ${Header::colourorange},

	# IPsec
	"gre[0-9]+"             => ${Header::colourvpn},
	"vti[0-9]+"             => ${Header::colourvpn},

	# OpenVPN
	"tun[0-9]+"             => ${Header::colourovpn},
);

my @routes = &General::system_output("ip", "route", "show");

# Find all routes
foreach my $intf (keys %interfaces) {
	foreach my $route (grep(/dev ${intf}/, @routes)) {
		if ($route =~ m/^(\d+\.\d+\.\d+\.\d+\/\d+)/) {
			$networks{$1} = $interfaces{$intf};
		}
	}
}

# Load the WireGuard client pool
if (-e "/var/ipfire/wireguard/settings") {
	my %wgsettings = ();

	&General::readhash("/var/ipfire/wireguard/settings", \%wgsettings);

	$networks{$wgsettings{'CLIENT_POOL'}} = ${Header::colourwg};
}

# Load routed WireGuard networks
if (-e "/var/ipfire/wireguard/peers") {
	my %wgpeers = ();

	# Load all peers
	&General::readhasharray("/var/ipfire/wireguard/peers", \%wgpeers);

	foreach my $key (keys %wgpeers) {
		my $networks = $wgpeers{$key}[6];

		# Split the string
		my @networks = split(/\|/, $networks);

		foreach my $network (@networks) {
			$networks[$network] = ${Header::colourwg};
		}
	}
}

# Add OpenVPN net and RED/BLUE/ORANGE entry (when appropriate)
if (-e "${General::swroot}/ovpn/settings") {
	my %ovpnsettings = ();
	&General::readhash("${General::swroot}/ovpn/settings", \%ovpnsettings);

	$networks{$ovpnsettings{'DOVPN_SUBNET'}} = ${Header::colourovpn};
}

# Add OpenVPN net for custom OVPNs
if (-e "${General::swroot}/ovpn/ccd.conf") {
	open(OVPNSUB, "${General::swroot}/ovpn/ccd.conf");
	foreach my $line (<OVPNSUB>) {
		my @ovpn = split(',', $line);

		$networks{$ovpn[3]} = ${Header::colourovpn};
	}
	close(OVPNSUB);
}

open(IPSEC, "${General::swroot}/vpn/config");
my @ipsec = <IPSEC>;
close(IPSEC);

foreach my $line (@ipsec) {
	my @vpn = split(',', $line);

	my @subnets = split(/\|/, $vpn[12]);
	for my $subnet (@subnets) {
		$networks{$subnet} = ${Header::colourvpn};
	}
}

if (-e "${General::swroot}/ovpn/n2nconf") {
	open(OVPNN2N, "${General::swroot}/ovpn/ovpnconfig");
	foreach my $line (<OVPNN2N>) {
		my @ovpn = split(',', $line);
		next if ($ovpn[4] ne 'net');

		$networks{$ovpn[12]} = ${Header::colourovpn};
	}
	close(OVPNN2N);
}

# Show the page.
&Header::openpage($Lang::tr{'connections'}, 1, '');
&Header::openbigbox('100%', 'left');
&Header::opensection();

# Print legend.
print <<END;
	<table style='width:100%'>
		<tr>
			<td style='text-align:center;'>
				<b>$Lang::tr{'legend'} :</b>
			</td>
			<td style='text-align:center; color:#FFFFFF; background-color:${Header::colourgreen}; font-weight:bold;'>
				<b>$Lang::tr{'lan'}</b>
			</td>
			<td style='text-align:center; color:#FFFFFF; background-color:${Header::colourred};'>
				<b>$Lang::tr{'internet'}</b>
			</td>
			<td style='text-align:center; color:#FFFFFF; background-color:${Header::colourorange};'>
				<b>$Lang::tr{'dmz'}</b>
			</td>
			<td style='text-align:center; color:#FFFFFF; background-color:${Header::colourblue};'>
				<b>$Lang::tr{'wireless'}</b>
			</td>
			<td style='text-align:center; color:#FFFFFF; background-color:${Header::colourfw};'>
				<b>IPFire</b>
			</td>
			<td style='text-align:center; color:#FFFFFF; background-color:${Header::colourvpn};'>
				<b>$Lang::tr{'vpn'}</b>
			</td>
			<td style='text-align:center; color:#FFFFFF; background-color:${Header::colourwg};'>
				<b>$Lang::tr{'wireguard'}</b>
			</td>
			<td style='text-align:center; color:#FFFFFF; background-color:${Header::colourovpn};'>
				<b>$Lang::tr{'OpenVPN'}</b>
			</td>
			<td style='text-align:center; color:#FFFFFF; background-color:$colour_multicast;'>
				<b>Multicast</b>
			</td>
		</tr>
	</table>
	<br>
END

# Print table header
print <<END;
	<table class="tbl">
		<tr>
			<th>
				$Lang::tr{'protocol'}
			</th>
			<th colspan='2'>
				$Lang::tr{'source ip and port'}
			</th>
			<th></th>
			<th colspan='2'>
				$Lang::tr{'dest ip and port'}
			</th>
			<th></th>
			<th colspan='2'>
				$Lang::tr{'data transfer'}
			</th>
			<th>
				$Lang::tr{'connection'}<br>$Lang::tr{'status'}
			</th>
			<th>
				$Lang::tr{'expires'}<br>($Lang::tr{'hours:minutes:seconds'})
			</th>
		</tr>
END

# Read and sort the connection tracking table
open(CONNTRACK, "/usr/local/bin/getconntracktable | sort -k 5,5 --numeric-sort --reverse |")
	or die "Unable to read conntrack table";

foreach my $line (<CONNTRACK>) {
	my @conn = split(' ', $line);

	# The first bit is the l3 protocol.
	my $l3proto = $conn[0];

	# Skip everything that is not IPv4.
	if ($l3proto ne 'ipv4') {
		next;
	}

	# L4 protocol (tcp, udp, ...).
	my $l4proto = $conn[2];

	# Translate unknown protocols.
	if ($l4proto eq 'unknown') {
		my $l4protonum = $conn[3];
		if ($l4protonum eq '2') {
			$l4proto = 'IGMP';
		} elsif ($l4protonum eq '4') {
			$l4proto = 'IPv4 Encap';
		} elsif ($l4protonum eq '33') {
			$l4proto = 'DCCP';
		} elsif ($l4protonum eq '41') {
			$l4proto = 'IPv6 Encap';
		} elsif ($l4protonum eq '50') {
			$l4proto = 'ESP';
		} elsif ($l4protonum eq '51') {
			$l4proto = 'AH';
		} elsif ($l4protonum eq '132') {
			$l4proto = 'SCTP';
		} else {
			$l4proto = $l4protonum;
		}
	} else {
		$l4proto = uc($l4proto);
	}

	# Source and destination.
	my $sip;
	my $sip_ret;
	my $dip;
	my $dip_ret;
	my $sport;
	my $sport_ret;
	my $dport;
	my $dport_ret;
	my @packets;
	my @bytes;

	my $ttl = $conn[4];
	my $state;
	if ($l4proto eq 'TCP') {
		$state = $conn[5];
	}

	# Kick out everything that is not IPv4.
	foreach my $item (@conn) {
		my ($key, $val) = split('=', $item);

		switch ($key) {
			case "src" {
				if ($sip == "") {
					$sip = $val;
				} else {
					$dip_ret = $val;
				}
			}
			case "dst" {
				if ($dip == "") {
					$dip = $val;
				} else {
					$sip_ret = $val;
				}
			}
			case "sport" {
				if ($sport == "") {
					$sport = $val;
				} else {
					$dport_ret = $val;
				}
			}
			case "dport" {
				if ($dport == "") {
					$dport = $val;
				} else {
					$sport_ret = $val;
				}
			}
			case "packets" {
				push(@packets, $val);
			}
			case "bytes" {
				push(@bytes, $val);
			}
		}
	}

	my $sip_colour = ipcolour($sip);
	# use colour of destination network for DNAT
	my $dip_colour = $dip ne $dip_ret ? ipcolour($dip_ret) : ipcolour($dip);

	my $sserv = '';
	if ($sport < 1024) {
		$sserv = uc(getservbyport($sport, lc($l4proto)));
	}

	my $dserv = '';
	if ($dport < 1024) {
		$dserv = uc(getservbyport($dport, lc($l4proto)));
	}

	# Format bytes
	my $bytes_in  = &General::formatBytes($bytes[0]);
	my $bytes_out = &General::formatBytes($bytes[1]);

	# enumerate location information
	my $srcccode = &Location::Functions::lookup_country_code($sip_ret);
	my $src_flag_icon = &Location::Functions::get_flag_icon($srcccode);
	my $dstccode = &Location::Functions::lookup_country_code($dip_ret);
	my $dst_flag_icon = &Location::Functions::get_flag_icon($dstccode);

	# Format TTL
	$ttl = &General::format_time($ttl);

	my $sip_extra;
	if ($sip_ret && $sip ne $sip_ret) {
		$sip_extra = "<span style='color:#FFFFFF;'>&gt;</span> ";
		$sip_extra .= "<a href='/cgi-bin/ipinfo.cgi?ip=$sip_ret'>";
		$sip_extra .= "	<span style='color:#FFFFFF;'>$sip_ret</span>";
		$sip_extra .= "</a>";
	}

	my $dip_extra;
	if ($dip_ret && $dip ne $dip_ret) {
		$dip_extra = "<span style='color:#FFFFFF;'>&gt;</span> ";
		$dip_extra .= "<a href='/cgi-bin/ipinfo.cgi?ip=$dip_ret'>";
		$dip_extra .= " <span style='color:#FFFFFF;'>$dip_ret</span>";
		$dip_extra .= "</a>";
	}

	my $sport_extra;
	if ($sport ne $sport_ret) {
		my $sserv_ret = '';
		if ($sport_ret < 1024) {
			$sserv_ret = uc(getservbyport($sport_ret, lc($l4proto)));
		}

		$sport_extra = "<span style='color:#FFFFFF;'>&gt;</span> ";
		$sport_extra .= "<a href='https://isc.sans.edu/port.html?port=$sport_ret' target='top' title='$sserv_ret'>";
		$sport_extra .= " <span style='color:#FFFFFF;'>$sport_ret</span>";
		$sport_extra .= "</a>";
	}

	my $dport_extra;
	if ($dport ne $dport_ret) {
		my $dserv_ret = '';
		if ($dport_ret < 1024) {
			$dserv_ret = uc(getservbyport($dport_ret, lc($l4proto)));
		}

		$dport_extra = "<span style='color:#FFFFFF;'>&gt;</span> ";
		$dport_extra .= "<a href='https://isc.sans.edu/port.html?port=$dport_ret' target='top' title='$dserv_ret'>";
		$dport_extra .= " <span style='color:#FFFFFF;'>$dport_ret</span>";
		$dport_extra .= "</a>";
	}

	print <<END;
	<tr>
		<td style='text-align:center'>$l4proto</td>
		<td style='text-align:center; background-color:$sip_colour;'>
			<a href='/cgi-bin/ipinfo.cgi?ip=$sip'>
				<span style='color:#FFFFFF;'>$sip</span>
			</a>
			$sip_extra
		</td>
		<td style='text-align:center; background-color:$sip_colour;'>
			<a href='https://isc.sans.edu/port.html?port=$sport' target='top' title='$sserv'>
				<span style='color:#FFFFFF;'>$sport</span>
			</a>
			$sport_extra
		</td>
		<td style='text-align:center; background-color:$sip_colour;'>
			<a href='country.cgi#$srcccode'><img src='$src_flag_icon' border='0' align='absmiddle' alt='$srcccode' title='$srcccode' /></a>
		</td>
		<td style='text-align:center; background-color:$dip_colour;'>
			<a href='/cgi-bin/ipinfo.cgi?ip=$dip'>
				<span style='color:#FFFFFF;'>$dip</span>
			</a>
			$dip_extra
		</td>
		<td style='text-align:center; background-color:$dip_colour;'>
			<a href='https://isc.sans.edu/port.html?port=$dport' target='top' title='$dserv'>
				<span style='color:#FFFFFF;'>$dport</span>
			</a>
			$dport_extra
		</td>
		<td style='text-align:center; background-color:$sip_colour;'>
			<a href='country.cgi#$dstccode'><img src='$dst_flag_icon' border='0' align='absmiddle' alt='$dstccode' title='$dstccode' /></a>
		</td>
		<td class="text-right">
			&gt; $bytes_in
		</td>
		<td class="text-right">
			&lt; $bytes_out
		</td>
		<td style='text-align:center'>$state</td>
		<td style='text-align:center'>$ttl</td>
	</tr>
END
}

close(CONNTRACK);

# Close the main table.
print "</table>";

&Header::closesection();
&Header::closebigbox();
&Header::closepage();

sub ipcolour($) {
	my $address = shift;

	# Sort all networks so we find the best match
	my @networks = reverse sort {
		&Network::get_prefix($a) <=> &Network::get_prefix($b)
	} keys %networks;

	foreach my $network (@networks) {
		if (defined $network) {
			if (&Network::ip_address_in_network($address, $network)) {
				return $networks{$network};
			}
		}
	}

	# If we don't know the network, the address must be from the RED network
	return ${Header::colourred};
}

1;
