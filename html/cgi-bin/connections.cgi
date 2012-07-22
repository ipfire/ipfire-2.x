#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2012  IPFire Team  <info@ipfire.org>                     #
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

use Net::IPv4Addr qw( :all );
use Switch;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

&Header::showhttpheaders();

my @network=();
my @masklen=();
my @colour=();

my %netsettings=();
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::table1colour} );
undef (@dummy);

# Read the connection tracking table.
open(CONNTRACK, "/usr/local/bin/getconntracktable | sort -k 5,5 --numeric-sort --reverse |") or die "Unable to read conntrack table";
my @conntrack = <CONNTRACK>;
close(CONNTRACK);

# Collect data for the @network array.

# Add Firewall Localhost 127.0.0.1
push(@network, '127.0.0.1');
push(@masklen, '255.255.255.255');
push(@colour, ${Header::colourfw});

if (open(IP, "${General::swroot}/red/local-ipaddress")) {
	my $redip = <IP>;
	close(IP);

	chomp $redip;
	push(@network, $redip);
	push(@masklen, '255.255.255.255');
	push(@colour, ${Header::colourfw});
}

# Add STATIC RED aliases
if ($netsettings{'RED_DEV'}) {
	my $aliasfile = "${General::swroot}/ethernet/aliases";
	open(ALIASES, $aliasfile) or die 'Unable to open aliases file.';
	my @aliases = <ALIASES>;
	close(ALIASES);

	# We have a RED eth iface
	if ($netsettings{'RED_TYPE'} eq 'STATIC') {
		# We have a STATIC RED eth iface
		foreach my $line (@aliases) {
			chomp($line);
			my @temp = split(/\,/,$line);
			if ($temp[0]) {
				push(@network, $temp[0]);
				push(@masklen, $netsettings{'RED_NETMASK'} );
				push(@colour, ${Header::colourfw} );
			}
		}
	}
}

# Add Green Firewall Interface
push(@network, $netsettings{'GREEN_ADDRESS'});
push(@masklen, "255.255.255.255" );
push(@colour, ${Header::colourfw} );

# Add Green Network to Array
push(@network, $netsettings{'GREEN_NETADDRESS'});
push(@masklen, $netsettings{'GREEN_NETMASK'} );
push(@colour, ${Header::colourgreen} );

# Add Green Routes to Array
my @routes = `/sbin/route -n | /bin/grep $netsettings{'GREEN_DEV'}`;
foreach my $route (@routes) {
	chomp($route);
	my @temp = split(/[\t ]+/, $route);
	push(@network, $temp[0]);
	push(@masklen, $temp[2]);
	push(@colour, ${Header::colourgreen} );
}

# Add Blue Firewall Interface
push(@network, $netsettings{'BLUE_ADDRESS'});
push(@masklen, "255.255.255.255" );
push(@colour, ${Header::colourfw} );

# Add Blue Network
if ($netsettings{'BLUE_DEV'}) {
	push(@network, $netsettings{'BLUE_NETADDRESS'});
	push(@masklen, $netsettings{'BLUE_NETMASK'} );
	push(@colour, ${Header::colourblue} );

	# Add Blue Routes to Array
	@routes = `/sbin/route -n | /bin/grep $netsettings{'BLUE_DEV'}`;
	foreach my $route (@routes) {
		chomp($route);
		my @temp = split(/[\t ]+/, $route);
		push(@network, $temp[0]);
		push(@masklen, $temp[2]);
		push(@colour, ${Header::colourblue} );
	}
}

# Add Orange Network
if ($netsettings{'ORANGE_DEV'}) {
	push(@network, $netsettings{'ORANGE_NETADDRESS'});
	push(@masklen, $netsettings{'ORANGE_NETMASK'} );
	push(@colour, ${Header::colourorange} );
	# Add Orange Routes to Array
	@routes = `/sbin/route -n | /bin/grep $netsettings{'ORANGE_DEV'}`;
	foreach my $route (@routes) {
		chomp($route);
		my @temp = split(/[\t ]+/, $route);
		push(@network, $temp[0]);
		push(@masklen, $temp[2]);
		push(@colour, ${Header::colourorange} );
	}
}

# Add OpenVPN net and RED/BLUE/ORANGE entry (when appropriate)
if (-e "${General::swroot}/ovpn/settings") {
	my %ovpnsettings = ();
	&General::readhash("${General::swroot}/ovpn/settings", \%ovpnsettings);
	my @tempovpnsubnet = split("\/",$ovpnsettings{'DOVPN_SUBNET'});

	# add OpenVPN net
	push(@network, $tempovpnsubnet[0]);
	push(@masklen, $tempovpnsubnet[1]);
	push(@colour, ${Header::colourovpn} );

	# add BLUE:port / proto
	if (($ovpnsettings{'ENABLED_BLUE'} eq 'on') && $netsettings{'BLUE_DEV'}) {
		push(@network, $netsettings{'BLUE_ADDRESS'} );
		push(@masklen, '255.255.255.255' );
		push(@colour, ${Header::colourovpn});
	}

	# add ORANGE:port / proto
	if (($ovpnsettings{'ENABLED_ORANGE'} eq 'on') && $netsettings{'ORANGE_DEV'}) {
		push(@network, $netsettings{'ORANGE_ADDRESS'} );
		push(@masklen, '255.255.255.255' );
		push(@colour, ${Header::colourovpn} );
	}
}

open(IPSEC, "${General::swroot}/vpn/config");
my @ipsec = <IPSEC>;
close(IPSEC);

foreach my $line (@ipsec) {
	my @vpn = split(',', $line);
	my ($network, $mask) = split("/", $vpn[12]);

	if (!&General::validip($mask)) {
		$mask = ipv4_cidr2msk($mask);
	}

	push(@network, $network);
	push(@masklen, $mask);
	push(@colour, ${Header::colourvpn});
}

if (-e "${General::swroot}/ovpn/n2nconf") {
	open(OVPNN2N, "${General::swroot}/ovpn/ovpnconfig");
	my @ovpnn2n = <OVPNN2N>;
	close(OVPNN2N);

	foreach my $line (@ovpnn2n) {
		my @ovpn = split(',', $line);
		next if ($ovpn[4] ne 'net');

		my ($network, $mask) = split("/", $ovpn[12]);
		if (!&General::validip($mask)) {
			$mask = ipv4_cidr2msk($mask);
		}

		push(@network, $network);
		push(@masklen, $mask);
		push(@colour, ${Header::colourovpn});
	}
}

# Show the page.
&Header::openpage($Lang::tr{'connections'}, 1, '');
&Header::openbigbox('100%', 'left');
&Header::openbox('100%', 'left', $Lang::tr{'connection tracking'});

# Print legend.
print <<END;
	<table width='100%'>
		<tr>
			<td align='center'>
				<b>$Lang::tr{'legend'} : </b>
			</td>
			<td align='center' bgcolor='${Header::colourgreen}'>
				<b><font color='#FFFFFF'>$Lang::tr{'lan'}</font></b>
			</td>
			<td align='center' bgcolor='${Header::colourred}'>
				<b><font color='#FFFFFF'>$Lang::tr{'internet'}</font></b>
			</td>
			<td align='center' bgcolor='${Header::colourorange}'>
				<b><font color='#FFFFFF'>$Lang::tr{'dmz'}</font></b>
			</td>
			<td align='center' bgcolor='${Header::colourblue}'>
				<b><font color='#FFFFFF'>$Lang::tr{'wireless'}</font></b>
			</td>
			<td align='center' bgcolor='${Header::colourfw}'>
				<b><font color='#FFFFFF'>IPFire</font></b>
			</td>
			<td align='center' bgcolor='${Header::colourvpn}'>
				<b><font color='#FFFFFF'>$Lang::tr{'vpn'}</font></b>
			</td>
			<td align='center' bgcolor='${Header::colourovpn}'>
				<b><font color='#FFFFFF'>$Lang::tr{'OpenVPN'}</font></b>
			</td>
		</tr>
	</table>
	<br>
END

# Print table header.
print <<END;
	<table width='100%'>
		<tr>
			<th align='center'>
				$Lang::tr{'protocol'}
			</th>
			<th align='center'>
				$Lang::tr{'source ip and port'}
			</th>
			<th>&nbsp;</th>
			<th align='center'>
				$Lang::tr{'dest ip and port'}
			</th>
			<th>&nbsp;</th>
			<th align='center'>
				$Lang::tr{'download'} /
				<br>$Lang::tr{'upload'}
			</th>
			<th align='center'>
				$Lang::tr{'connection'}<br>$Lang::tr{'status'}
			</th>
			<th align='center'>
				$Lang::tr{'expires'}<br>($Lang::tr{'seconds'})
			</th>
		</tr>
END

foreach my $line (@conntrack) {
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
	my $dip;
	my $sport;
	my $dport;
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
				$sip = $val;
			}
			case "dst" {
				$dip = $val;
			}
			case "sport" {
				$sport = $val;
			}
			case "dport" {
				$dport = $val;
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
	my $dip_colour = ipcolour($dip);

	my $sserv = '';
	if ($sport < 1024) {
		$sserv = uc(getservbyport($sport, lc($l4proto)));
		if ($sserv ne '') {
			$sserv = "&nbsp;($sserv)";
		}
	}

	my $dserv = '';
	if ($dport < 1024) {
		$dserv = uc(getservbyport($dport, lc($l4proto)));
		if ($dserv ne '') {
			$dserv = "&nbsp;($dserv)";
		}
	}

	my $bytes_in = format_bytes($bytes[0]);
	my $bytes_out = format_bytes($bytes[1]);

	# Format TTL
	$ttl = format_time($ttl);

	print <<END;
	<tr>
		<td align='center'>$l4proto</td>
		<td align='center' bgcolor='$sip_colour'>
			<a href='/cgi-bin/ipinfo.cgi?ip=$sip'>
				<font color='#FFFFFF'>$sip</font>
			</a>
		</td>
		<td align='center' bgcolor='$sip_colour'>
			<a href='http://isc.sans.org/port_details.php?port=$sport' target='top'>
				<font color='#FFFFFF'>$sport$sserv</font>
			</a>
		</td>
		<td align='center' bgcolor='$dip_colour'>
			<a href='/cgi-bin/ipinfo.cgi?ip=$dip'>
				<font color='#FFFFFF'>$dip</font>
			</a>
		</td>
		<td align='center' bgcolor='$dip_colour'>
			<a href='http://isc.sans.org/port_details.php?port=$dport' target='top'>
				<font color='#FFFFFF'>$dport$dserv</font>
			</a>
		</td>
		<td align='center'>
			$bytes_in / $bytes_out
		</td>
		<td align='center'>$state</td>
		<td align='center'>$ttl</td>
	</tr>
END
}

# Close the main table.
print "</table>";

&Header::closebox();
&Header::closebigbox();
&Header::closepage();

sub format_bytes($) {
	my $bytes = shift;
	my @units = ("B", "k", "M", "G", "T");

	foreach my $unit (@units) {
		if ($bytes < 1024) {
			return sprintf("%d%s", $bytes, $unit);
		}

		$bytes /= 1024;
	}

	return sprintf("%d%s", $bytes, $units[$#units]);
}

sub format_time($) {
	my $time = shift;

	my $seconds = $time % 60;
	my $minutes = $time / 60;

	my $hours = 0;
	if ($minutes >= 60) {
		$hours = $minutes / 60;
		$minutes %= 60;
	}

	return sprintf("%3d:%02d:%02d", $hours, $minutes, $seconds);
}

sub ipcolour($) {
	my $id = 0;
	my $colour = ${Header::colourred};
	my ($ip) = $_[0];
	my $found = 0;

	foreach my $line (@network) {
		if ($network[$id] eq '') {
			$id++;
		} else {
			if (!$found && ipv4_in_network($network[$id], $masklen[$id], $ip) ) {
				$found = 1;
				$colour = $colour[$id];
			}
			$id++;
		}
	}

	return $colour;
}

1;
