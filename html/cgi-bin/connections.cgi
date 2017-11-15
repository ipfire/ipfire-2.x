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
require "${General::swroot}/geoip-functions.pl";

my $colour_multicast = "#A0A0A0";

# sort arguments for connection tracking table
# the sort field. eg. 1=src IP, 2=dst IP, 3=src port, 4=dst port
my $SORT_FIELD = 0;
# the sort order. (a)scending orr (d)escending
my $SORT_ORDER = 0;
# cgi query arguments
my %cgiin;
# debug mode
my $debug = 0;

# retrieve query arguments
# note: let a-z A-Z and 0-9 pass as value only
if (length ($ENV{'QUERY_STRING'}) > 0){
	my $name;
	my $value;
	my $buffer = $ENV{'QUERY_STRING'};
	my @pairs = split(/&/, $buffer);
	foreach my $pair (@pairs){
		($name, $value) = split(/=/, $pair);
		$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg; # e.g. "%20" => " "
		$value =~ s/[^a-zA-Z0-9]*//g; # a-Z 0-9 will pass
		$cgiin{$name} = $value; 
	}
}

&Header::showhttpheaders();

my @network=();
my @masklen=();
my @colour=();

my %netsettings=();
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

# output cgi query arrguments to browser on debug
if ( $debug ){
	&Header::openbox('100%', 'center', 'DEBUG');
	my $debugCount = 0;
	foreach my $line (sort keys %cgiin) {
		print "$line = '$cgiin{$line}'<br />\n";
		$debugCount++;
	}
	print "&nbsp;Count: $debugCount\n";
	&Header::closebox();
}

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::table1colour} );
undef (@dummy);

# check sorting arguments
if ( $cgiin{'sort_field'} ~~ [ '1','2','3','4','5','6','7','8','9' ] ) {
	$SORT_FIELD = $cgiin{'sort_field'};

	if ( $cgiin{'sort_order'} ~~ [ 'a','d','A','D' ] ) {
		$SORT_ORDER = lc($cgiin{'sort_order'});
	}
}

# Read and sort the connection tracking table
# do sorting 
if ($SORT_FIELD and $SORT_ORDER) { 
	# field sorting when sorting arguments are sane
	open(CONNTRACK, "/usr/local/bin/getconntracktable | /usr/local/bin/consort.sh $SORT_FIELD $SORT_ORDER |") or die "Unable to read conntrack table";
} else {
	# default sorting with no query arguments
	open(CONNTRACK, "/usr/local/bin/getconntracktable | sort -k 5,5 --numeric-sort --reverse |") or die "Unable to read conntrack table";
}
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

# Add Orange Firewall Interface
push(@network, $netsettings{'ORANGE_ADDRESS'});
push(@masklen, "255.255.255.255" );
push(@colour, ${Header::colourfw} );

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

# Highlight multicast connections.
push(@network, "224.0.0.0");
push(@masklen, "239.0.0.0");
push(@colour, $colour_multicast);

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

# Add OpenVPN net for custom OVPNs
if (-e "${General::swroot}/ovpn/ccd.conf") {
	open(OVPNSUB, "${General::swroot}/ovpn/ccd.conf");	
	my @ovpnsub = <OVPNSUB>;
	close(OVPNSUB);

	foreach (@ovpnsub) {
		my ($network, $mask) = split '/', (split ',', $_)[2];
		
		$mask = ipv4_cidr2msk($mask) unless &General::validip($mask);

		push(@network, $network);
		push(@masklen, $mask);
		push(@colour, ${Header::colourovpn});
	}
}

open(IPSEC, "${General::swroot}/vpn/config");
my @ipsec = <IPSEC>;
close(IPSEC);

foreach my $line (@ipsec) {
	my @vpn = split(',', $line);

	my @subnets = split(/\|/, $vpn[12]);
	for my $subnet (@subnets) {
		my ($network, $mask) = split("/", $subnet);

		if (!&General::validip($mask)) {
			$mask = ipv4_cidr2msk($mask);
		}

		push(@network, $network);
		push(@masklen, $mask);
		push(@colour, ${Header::colourvpn});
	}
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

if ($SORT_FIELD and $SORT_ORDER) {
	my @sort_field_name = (
		$Lang::tr{'source ip'},
		$Lang::tr{'destination ip'},
		$Lang::tr{'source port'},
		$Lang::tr{'destination port'},
		$Lang::tr{'protocol'},
		$Lang::tr{'connection'}.' '.$Lang::tr{'status'},
		$Lang::tr{'expires'}.' ('.$Lang::tr{'seconds'}.')',
		$Lang::tr{'download'},
		$Lang::tr{'upload'}
	);
	my $sort_order_name;
	if (lc($SORT_ORDER) eq "a") {
		$sort_order_name = $Lang::tr{'sort ascending'};
	} else {
		$sort_order_name = $Lang::tr{'sort descending'};
	}

print <<END
	<div style="font-weight:bold;margin:10px;font-size: 70%">
		$sort_order_name: $sort_field_name[$SORT_FIELD-1]
	</div>
END
;
}

# Print table header.
print <<END;
	<table style='width:100%'>
		<tr>
			<th style='text-align:center'>
				<a href="?sort_field=5&amp;sort_order=d"><img style="width:10px" src="/images/up.gif" alt=""></a>
				<a href="?sort_field=5&amp;sort_order=a"><img style="width:10px" src="/images/down.gif" alt=""></a>
			</th>
			<th style='text-align:center' colspan='2'>
				<a href="?sort_field=1&amp;sort_order=d"><img style="width:10px" src="/images/up.gif" alt=""></a>
				<a href="?sort_field=1&amp;sort_order=a"><img style="width:10px" src="/images/down.gif" alt=""></a>
				&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
				<a href="?sort_field=3&amp;sort_order=d"><img style="width:10px" src="/images/up.gif" alt=""></a>
				<a href="?sort_field=3&amp;sort_order=a"><img style="width:10px" src="/images/down.gif" alt=""></a>
			</th>
			<th>&nbsp;</th>
			<th style='text-align:center' colspan='2'>
				<a href="?sort_field=2&amp;sort_order=d"><img style="width:10px" src="/images/up.gif" alt=""></a>
				<a href="?sort_field=2&amp;sort_order=a"><img style="width:10px" src="/images/down.gif" alt=""></a>
				&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
				<a href="?sort_field=4&amp;sort_order=d"><img style="width:10px" src="/images/up.gif" alt=""></a>
				<a href="?sort_field=4&amp;sort_order=a"><img style="width:10px" src="/images/down.gif" alt=""></a>
			</th>
			<th>&nbsp;</th>
			<th style='text-align:center'>
				<a href="?sort_field=8&amp;sort_order=d"><img style="width:10px" src="/images/up.gif" alt=""></a>
				<a href="?sort_field=8&amp;sort_order=a"><img style="width:10px" src="/images/down.gif" alt=""></a>
				&nbsp;&nbsp;&nbsp;&nbsp;
				<a href="?sort_field=9&amp;sort_order=d"><img style="width:10px" src="/images/up.gif" alt=""></a>
				<a href="?sort_field=9&amp;sort_order=a"><img style="width:10px" src="/images/down.gif" alt=""></a>
			</th>
			<th style='text-align:center'>
				<a href="?sort_field=6&amp;sort_order=d"><img style="width:10px" src="/images/up.gif" alt=""></a>
				<a href="?sort_field=6&amp;sort_order=a"><img style="width:10px" src="/images/down.gif" alt=""></a>
			</th>
			<th style='text-align:center'>
				<a href="?sort_field=7&amp;sort_order=d"><img style="width:10px" src="/images/up.gif" alt=""></a>
				<a href="?sort_field=7&amp;sort_order=a"><img style="width:10px" src="/images/down.gif" alt=""></a>
			</th>
		</tr>
		<tr>
			<th style='text-align:center'>
				$Lang::tr{'protocol'}
			</th>
			<th style='text-align:center' colspan='2'>
				$Lang::tr{'source ip and port'}
			</th>
			<th style='text-align:center'>
				$Lang::tr{'country'}
			</th>
			<th style='text-align:center' colspan='2'>
				$Lang::tr{'dest ip and port'}
			</th>
			<th style='text-align:center'>
				$Lang::tr{'country'}
			</th>
			<th style='text-align:center'>
				$Lang::tr{'download'} /
				<br>$Lang::tr{'upload'}
			</th>
			<th style='text-align:center'>
				$Lang::tr{'connection'}<br>$Lang::tr{'status'}
			</th>
			<th style='text-align:center'>
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

	my $bytes_in = format_bytes($bytes[0]);
	my $bytes_out = format_bytes($bytes[1]);

	# enumerate GeoIP information
	my $srcccode = &GeoIP::lookup($sip_ret);
	my $src_flag_icon = &GeoIP::get_flag_icon($srcccode);
	my $dstccode = &GeoIP::lookup($dip_ret);
	my $dst_flag_icon = &GeoIP::get_flag_icon($dstccode);

	# Format TTL
	$ttl = format_time($ttl);

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
		$sport_extra .= "<a href='http://isc.sans.org/port_details.php?port=$sport_ret' target='top' title='$sserv_ret'>";
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
		$dport_extra .= "<a href='http://isc.sans.org/port_details.php?port=$dport_ret' target='top' title='$dserv_ret'>";
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
			<a href='http://isc.sans.org/port_details.php?port=$sport' target='top' title='$sserv'>
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
			<a href='http://isc.sans.org/port_details.php?port=$dport' target='top' title='$dserv'>
				<span style='color:#FFFFFF;'>$dport</span>
			</a>
			$dport_extra
		</td>
		<td style='text-align:center; background-color:$sip_colour;'>
			<a href='country.cgi#$dstccode'><img src='$dst_flag_icon' border='0' align='absmiddle' alt='$dstccode' title='$dstccode' /></a>
		</td>
		<td style='text-align:center'>
			$bytes_in / $bytes_out
		</td>
		<td style='text-align:center'>$state</td>
		<td style='text-align:center'>$ttl</td>
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

	if ($ip) {
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
	}

	return $colour;
}

1;
