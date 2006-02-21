#!/usr/bin/perl
#
# (c) 2001 Jack Beglinger <jackb_guppy@yahoo.com>
#
# (c) 2003 Dave Roberts <countzerouk@hotmail.com> - colour coded netfilter/iptables rewrite for 1.3
#
# $Id: connections.cgi,v 1.6.2.11 2005/02/24 07:44:35 gespinasse Exp $
#

# Setup GREEN, ORANGE, IPCOP, VPN CIDR networks, masklengths and colours only once

my @network=();
my @masklen=();
my @colour=();

use Net::IPv4Addr qw( :all );

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require 'CONFIG_ROOT/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::table1colour} );
undef (@dummy);

# Read various files

my %netsettings=();
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

open (ACTIVE, "/proc/net/ip_conntrack") or die 'Unable to open ip_conntrack';
my @active = <ACTIVE>;
close (ACTIVE);

my @vpn = ('none');
open (ACTIVE, "/proc/net/ipsec_eroute") and @vpn = <ACTIVE>; close (ACTIVE);

my $aliasfile = "${General::swroot}/ethernet/aliases";
open(ALIASES, $aliasfile) or die 'Unable to open aliases file.';
my @aliases = <ALIASES>;
close(ALIASES);

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

# Add Firewall Localhost 127.0.0.1
push(@network, '127.0.0.1');
push(@masklen, '255.255.255.255' );
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

# Add STATIC RED aliases
if ($netsettings{'RED_DEV'}) {
	# We have a RED eth iface
	if ($netsettings{'RED_TYPE'} eq 'STATIC') {
		# We have a STATIC RED eth iface
		foreach my $line (@aliases)
		{
			chomp($line);
			my @temp = split(/\,/,$line);
			if ( $temp[0] ) {
				push(@network, $temp[0]);
				push(@masklen, $netsettings{'RED_NETMASK'} );
				push(@colour, ${Header::colourfw} );
			}
		}
	}
}

# Add VPNs
if ( $vpn[0] ne 'none' ) {
	foreach my $line (@vpn) {
		my @temp = split(/[\t ]+/,$line);
		my @temp1 = split(/[\/:]+/,$temp[3]);
		push(@network, $temp1[0]);
		push(@masklen, ipv4_cidr2msk($temp1[1]));
		push(@colour, ${Header::colourvpn} );
	}
}
if (open(IP, "${General::swroot}/red/local-ipaddress")) {
	my $redip = <IP>;
	close(IP);
	chomp $redip;
	push(@network, $redip);
	push(@masklen, '255.255.255.255' );
	push(@colour, ${Header::colourfw} );
}

&Header::showhttpheaders();
&Header::openpage($Lang::tr{'connections'}, 1, '');
&Header::openbigbox('100%', 'left');
&Header::openbox('100%', 'left', $Lang::tr{'connection tracking'});

print <<END
<table width='60%'>
<tr><td align='center'><b>$Lang::tr{'legend'} : </b></td>
     <td align='center' bgcolor='${Header::colourgreen}'><b><font color='#FFFFFF'>$Lang::tr{'lan'}</font></b></td>
     <td align='center' bgcolor='${Header::colourred}'><b><font color='#FFFFFF'>$Lang::tr{'internet'}</font></b></td>
     <td align='center' bgcolor='${Header::colourorange}'><b><font color='#FFFFFF'>$Lang::tr{'dmz'}</font></b></td>
     <td align='center' bgcolor='${Header::colourblue}'><b><font color='#FFFFFF'>$Lang::tr{'wireless'}</font></b></td>
     <td align='center' bgcolor='${Header::colourfw}'><b><font color='#FFFFFF'>IPCop</font></b></td>
     <td align='center' bgcolor='${Header::colourvpn}'><b><font color='#FFFFFF'>$Lang::tr{'vpn'}</font></b></td>
</tr>
</table>
<br />
<table cellpadding='2'>
<tr><td align='center'><b>$Lang::tr{'protocol'}</b></td>
    <td align='center'><b>$Lang::tr{'expires'}<br />($Lang::tr{'seconds'})</b></td>
    <td align='center'><b>$Lang::tr{'connection'}<br />$Lang::tr{'status'}</b></td>
    <td align='center'><b>$Lang::tr{'original'}<br />$Lang::tr{'source ip and port'}</b></td>
    <td align='center'><b>$Lang::tr{'original'}<br />$Lang::tr{'dest ip and port'}</b></td>
    <td align='center'><b>$Lang::tr{'expected'}<br />$Lang::tr{'source ip and port'}</b></td>
    <td align='center'><b>$Lang::tr{'expected'}<br />$Lang::tr{'dest ip and port'}</b></td>
    <td align='center'><b>$Lang::tr{'marked'}</b></td>
    <td align='center'><b>$Lang::tr{'use'}</b></td>
</tr>
END
;

foreach my $line (@active)
{
	my $protocol='';
	my $expires='';
	my $connstatus='';
	my $orgsip='';
	my $orgdip='';
	my $orgsp='';
	my $orgdp='';
	my $exsip='';
	my $exdip='';
	my $exsp='';
	my $exdp='';
	my $marked='';
	my $use='';
	my $orgsipcolour='';
	my $orgdipcolour='';
	my $exsipcolour='';
	my $exdipcolour='';

	chomp($line);
	my @temp = split(' ',$line);
	print "<tr bgcolor='${Header::table1colour}'>\n";
	if ($temp[0] eq 'udp') {
		my $offset = 0;
		$marked = '';
		$protocol = $temp[0] . " (" . $temp[1] . ")";
		$expires = $temp[2];
		$connstatus = ' ';
		$orgsip = substr $temp[3], 4;
		$orgdip = substr $temp[4], 4;
		$orgsp = substr $temp[5], 6;
		$orgdp = substr $temp[6], 6;
		if ($temp[7] eq '[UNREPLIED]') {
                        $marked = $temp[7];
                        $offset = 1;
                }
                else {
                        $connstatus = ' ';
                }

		$exsip = substr $temp[7 + $offset], 4;
		$exdip = substr $temp[8 + $offset], 4;
		$exsp = substr $temp[9 + $offset], 6;
		$exdp = substr $temp[10 + $offset], 6;
		if ($marked eq '[UNREPLIED]') {
			$use = substr $temp[11 + $offset], 4;
                }
                else {
                        $marked = $temp[11 + $offset];
			$use = substr $marked, 0, 3;
			if ($use eq 'use' ) {
				$marked = '';
				$use = substr $temp[11 + $offset], 4;
			}
			else {
				$use = substr $temp[12 + $offset], 4;
			}
		}
	}
	if ($temp[0] eq 'tcp') {
		my $offset = 0;
                $protocol = $temp[0] . " (" . $temp[1] . ")";
                $expires = $temp[2];
                $connstatus = $temp[3];
                $orgsip = substr $temp[4], 4;
                $orgdip = substr $temp[5], 4;
                $orgsp = substr $temp[6], 6;
		$orgdp = substr $temp[7], 6;
		if ($temp[8] eq '[UNREPLIED]') {
                        $marked = $temp[8];
                        $offset = 1;
			$use = substr $temp[13], 4;
                }
                else {
                        $marked = $temp[12];
			$use = substr $temp[13], 4;
                }
		
		$exsip = substr $temp[8 + $offset], 4;
                $exdip = substr $temp[9 + $offset], 4;
                $exsp = substr $temp[10 + $offset], 6;
                $exdp = substr $temp[11 + $offset], 6;
        }
	if ($temp[0] eq 'unknown') {
                my $offset = 0;
                $protocol = "??? (" . $temp[1] . ")";
                $protocol = "esp (" . $temp[1] . ")" if ($temp[1] == 50);
                $protocol = " ah (" . $temp[1] . ")" if ($temp[1] == 51);
                $expires = $temp[2];
                $connstatus = ' ';
                $orgsip = substr $temp[3], 4;
                $orgdip = substr $temp[4], 4;
                $orgsp = ' ';
                $orgdp = ' ';
                $exsip = substr $temp[5], 4;
                $exdip = substr $temp[6], 4;
                $exsp = ' ';
                $exdp = ' ';
                $marked = ' ';
                $use = ' ';
        }
	if ($temp[0] eq 'gre') {
                my $offset = 0;
		$protocol = $temp[0] . " (" . $temp[1] . ")";
                $expires = $temp[2];
                $orgsip = substr $temp[5], 4;
                $orgdip = substr $temp[6], 4;
                $orgsp = ' ';
		$orgdp = ' ';
		$exsip = substr $temp[11], 4;
                $exdip = substr $temp[12], 4;
                $exsp = ' ';
                $exdp = ' ';
		$marked = $temp[17];
		$use = $temp[18];
	}
	$orgsipcolour = &ipcolour($orgsip);
	$orgdipcolour = &ipcolour($orgdip);
	$exsipcolour = &ipcolour($exsip);
	$exdipcolour = &ipcolour($exdip);
	print <<END
	<td align='center'>$protocol</td>
	<td align='center'>$expires</td>
	<td align='center'>$connstatus</td>
	<td align='center' bgcolor='$orgsipcolour'><a href='/cgi-bin/ipinfo.cgi?ip=$orgsip'><font color='#FFFFFF'>$orgsip</font></a><font color='#FFFFFF'>:$orgsp</font></td>
	<td align='center' bgcolor='$orgdipcolour'><a href='/cgi-bin/ipinfo.cgi?ip=$orgdip'><font color='#FFFFFF'>$orgdip</font></a><font color='#FFFFFF'>:$orgdp</font></td>
	<td align='center' bgcolor='$exsipcolour'><a href='/cgi-bin/ipinfo.cgi?ip=$exsip'><font color='#FFFFFF'>$exsip</font></a><font color='#FFFFFF'>:$exsp</font></td>
	<td align='center' bgcolor='$exdipcolour'><a href='/cgi-bin/ipinfo.cgi?ip=$exdip'><font color='#FFFFFF'>$exdip</font></a><font color='#FFFFFF'>:$exdp</font></td>
	<td align='center'>$marked</td><td align='center'>$use</td>
	</tr>
END
	;
}
print "</table>\n";

&Header::closebox();
&Header::closebigbox();
&Header::closepage();

sub ipcolour($) {
	my $id = 0;
	my $line;
	my $colour = ${Header::colourred};
	my ($ip) = $_[0];
	my $found = 0;
	foreach $line (@network)
	{
		if (!$found && ipv4_in_network( $network[$id] , $masklen[$id], $ip) ) {
			$found = 1;
			$colour = $colour[$id];
		}
		$id++;
	}
	return $colour
}
