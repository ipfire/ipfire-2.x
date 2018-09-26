#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2014  IPFire Team  <info@ipfire.org>                     #
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
use Net::Telnet;
use Sort::Naturally;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "/opt/pakfire/lib/functions.pl";

my %cgiparams=();
my %pppsettings=();
my %modemsettings=();
my %netsettings=();
my %ddnssettings=();
my %proxysettings=();
my %vpnsettings=();
my %vpnconfig=();
my %ovpnconfig=();
my $warnmessage = '';
my $refresh = "";
my $ipaddr='';
my $showbox=0;
my $showipsec=0;
my $showovpn=0;

if ( ! -e "/var/ipfire/main/gpl_accepted" ) {
	print "Status: 302 Moved Temporarily\n";
	print "Location: gpl.cgi\n\n";
	exit (0);
}

&Header::showhttpheaders();

$cgiparams{'ACTION'} = '';
&Header::getcgihash(\%cgiparams);
$pppsettings{'VALID'} = '';
$pppsettings{'PROFILENAME'} = 'None';
&General::readhash("${General::swroot}/ppp/settings", \%pppsettings);
&General::readhash("${General::swroot}/modem/settings", \%modemsettings);
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
&General::readhash("${General::swroot}/ddns/settings", \%ddnssettings);
&General::readhash("${General::swroot}/proxy/advanced/settings", \%proxysettings);
&General::readhash("${General::swroot}/vpn/settings", \%vpnsettings);

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

my $connstate = &Header::connectionstatus();

if ( -e "/var/ipfire/main/gpl-accepted" ) {
	if ($connstate =~ /$Lang::tr{'connecting'}/ || /$Lang::tr{'connection closed'}/ ){
		$refresh = "<meta http-equiv='refresh' content='5;'>";
	}elsif ($connstate =~ /$Lang::tr{'dod waiting'}/ || -e "${General::swroot}/main/refreshindex") {
		$refresh = "<meta http-equiv='refresh' content='30;'>";
	}
}

if ($cgiparams{'ACTION'} eq $Lang::tr{'dial profile'})
{
	my $profile = $cgiparams{'PROFILE'};
	my %tempcgiparams = ();
	$tempcgiparams{'PROFILE'} = '';
	&General::readhash("${General::swroot}/ppp/settings-$cgiparams{'PROFILE'}",
		\%tempcgiparams);

	# make a link from the selected profile to the "default" one.
	unlink("${General::swroot}/ppp/settings");
	link("${General::swroot}/ppp/settings-$cgiparams{'PROFILE'}",
		"${General::swroot}/ppp/settings");
	open (TMP, ">${General::swroot}/ppp/updatesettings");
	close TMP;
	# read in the new params "early" so we can write secrets.
	%cgiparams = ();
	&General::readhash("${General::swroot}/ppp/settings", \%cgiparams);
	$cgiparams{'PROFILE'} = $profile;
	$cgiparams{'BACKUPPROFILE'} = $profile;
	&General::writehash("${General::swroot}/ppp/settings-$cgiparams{'PROFILE'}",
		\%cgiparams);

	# write secrets file.
	open(FILE, ">/${General::swroot}/ppp/secrets") or die "Unable to write secrets file.";
	flock(FILE, 2);
	my $username = $cgiparams{'USERNAME'};
	my $password = $cgiparams{'PASSWORD'};
	print FILE "'$username' * '$password'\n";
	chmod 0600, "${General::swroot}/ppp/secrets";
	close FILE;

	&General::log("$Lang::tr{'profile made current'} $tempcgiparams{'PROFILENAME'}"); 
	$cgiparams{'ACTION'} = "$Lang::tr{'dial'}";
}

if ($cgiparams{'ACTION'} eq $Lang::tr{'dial'}) {
	system('/usr/local/bin/redctrl start > /dev/null') == 0
	or &General::log("Dial failed: $?"); sleep 1;
}elsif ($cgiparams{'ACTION'} eq $Lang::tr{'hangup'}) {
	system('/usr/local/bin/redctrl stop > /dev/null') == 0
	or &General::log("Hangup failed: $?"); sleep 1;
}

my $c;
my $maxprofiles = 5;
my @profilenames = ();

for ($c = 1; $c <= $maxprofiles; $c++)
{
	my %temppppsettings = ();
	$temppppsettings{'PROFILENAME'} = '';
	&General::readhash("${General::swroot}/ppp/settings-$c", \%temppppsettings);
	$profilenames[$c] = $temppppsettings{'PROFILENAME'};
}
my %selected;
for ($c = 1; $c <= $maxprofiles; $c++) {
	$selected{'PROFILE'}{$c} = ''; 
}
$selected{'PROFILE'}{$pppsettings{'PROFILE'}} = "selected='selected'";
my $dialButtonDisabled = "disabled='disabled'";

&Header::openpage($Lang::tr{'main page'}, 1, $refresh);
&Header::openbigbox('', 'center');
if (open(IPADDR,"${General::swroot}/red/local-ipaddress")) {
	    $ipaddr = <IPADDR>;
	    close IPADDR;
	    chomp ($ipaddr);
	}

&Header::openbox('100%', 'center', '');
if ( ( $pppsettings{'VALID'} eq 'yes' && $modemsettings{'VALID'} eq 'yes' ) || ( $netsettings{'CONFIG_TYPE'} =~ /^(1|2|3|4)$/ && $netsettings{'RED_TYPE'} =~ /^(DHCP|STATIC)$/ )) {
	if (open(IPADDR,"${General::swroot}/ddns/ipcache")) {
   	    $ipaddr = <IPADDR>;
    	    close IPADDR;
    	    chomp ($ipaddr);
	}
	if (open(IPADDR,"${General::swroot}/red/local-ipaddress")) {
	    $ipaddr = <IPADDR>;
	    close IPADDR;
	    chomp ($ipaddr);
	}
} elsif ($modemsettings{'VALID'} eq 'no') {
	print "$Lang::tr{'modem settings have errors'}\n </b></font>\n";
} else {
	print "$Lang::tr{'profile has errors'}\n </b></font>\n";
}

print <<END;
<!-- Table of networks -->
<table class='tbl' style='width:80%;'>
  <tr>
        <th style='background-color:$color{'color20'};'>$Lang::tr{'network'}</th>
        <th style='background-color:$color{'color20'};'>$Lang::tr{'ip address'}</th>
        <th style='background-color:$color{'color20'};'>$Lang::tr{'status'}</th>
  </tr>
  <tr>
        <td style='width:25%; text-align:center; background-color:$Header::colourred;'><a href='/cgi-bin/pppsetup.cgi' style='color:white;'><b>$Lang::tr{'internet'}</b></a><br/></td>
        <td style='width:30%; text-align:center;'>$ipaddr </td>
        <td style='width:45%; text-align:center;'>$connstate </td>
  </tr>
END
	my $HOSTNAME = (gethostbyaddr(pack("C4", split(/\./, $ipaddr)), 2))[0];
	if ( "$HOSTNAME" ne "" ) {
		print <<END;
	<tr><td><b>$Lang::tr{'hostname'}:</b><td style='text-align:center;'>$HOSTNAME</td><td></td>
END
	}

	if ( -e "${General::swroot}/red/remote-ipaddress" ) {
		open (TMP, "<${General::swroot}/red/remote-ipaddress");
		my $GATEWAY = <TMP>;
		chomp($GATEWAY);
		close TMP;
		print <<END;
	<tr><td><b>$Lang::tr{'gateway'}:</b><td style='text-align:center;'>$GATEWAY</td><td></td></tr>
END
	}

	my $dns_servers;
	if ( -e "${General::swroot}/red/dns" ) {
		open (TMP, "<${General::swroot}/red/dns");
		$dns_servers = <TMP>;
		chomp($dns_servers);
		close TMP;
	}
	print <<END;
		<tr>
			<td>
				<b><a href="netexternal.cgi">$Lang::tr{'dns servers'}</a>:</b>
			</td>
			<td style='text-align:center;'>
				$dns_servers
			</td>
			<td></td>
		</tr>
END

	if (&General::RedIsWireless()) {
		my $iface = $netsettings{"RED_DEV"} || "red0";

		my $essid        = &Network::wifi_get_essid($iface);
		my $frequency    = &Network::wifi_get_frequency($iface);
		my $access_point = &Network::wifi_get_access_point($iface);
		my $bit_rate     = &Network::wifi_get_bit_rate($iface);
		my $link_quality = &Network::wifi_get_link_quality($iface);
		my $signal_level = &Network::wifi_get_signal_level($iface);

		print <<END;
			<tr>
				<td>
					<strong>$Lang::tr{'wireless network'}:</strong>
				</td>
				<td style="text-align: center">
					$essid
				</td>
				<td style="text-align: center">
					$access_point @ $frequency
				</td>
			</tr>
			<tr>
				<td>
					<strong>
						$Lang::tr{'uplink bit rate'}:
					</strong>
				</td>
				<td style="text-align: center">
					$bit_rate
				</td>
				<td style="text-align: center">
					$link_quality% @ $signal_level
				</td>
			</tr>
END
	}

	print <<END;
		</table>
END

#Dial profiles
if ( $netsettings{'RED_TYPE'} ne "STATIC" && $netsettings{'RED_TYPE'} ne "DHCP" ){
	if ( ( $pppsettings{'VALID'} eq 'yes' ) || ( $netsettings{'CONFIG_TYPE'} =~ /^(1|2|3|4)$/ && $netsettings{'RED_TYPE'} =~ /^(DHCP|STATIC)$/ ) ) {
		print <<END;
		<br/>
		<table style='width:80%;'>
		<tr><td>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>$Lang::tr{'profile'}:
			<select name='PROFILE'>
END
		for ($c = 1; $c <= $maxprofiles; $c++)
		{
			if ($profilenames[$c] ne '') {
				$dialButtonDisabled = "";
				print "<option value='$c' $selected{'PROFILE'}{$c}>$c. $profilenames[$c]</option>";
			}
		}
		$dialButtonDisabled = "disabled='disabled'" if (-e '/var/run/ppp-ipfire.pid' || -e "${General::swroot}/red/active");
		print <<END;
			</select>
			<input type='submit' name='ACTION' value='$Lang::tr{'dial profile'}' $dialButtonDisabled />
		</form>
		</td>
		<td style='text-align:center;'>
			<table style='width:100%;'>
				<tr>
				<td style='width=50%; text-align:right;'>
					<form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='submit' name='ACTION' value='$Lang::tr{'dial'}'>
					</form>
				</td>
				<td style='width=50%; text-align:left;'>
					<form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='submit' name='ACTION' value='$Lang::tr{'hangup'}'>
					</form>
				</td>
				</tr>
			</table>
		</td>
		</tr>
		</table>
END
	} else {
		print "<br/><span style='color:red;'>$Lang::tr{'profile has errors'}</span><br/>";
	}
}


print <<END;
<br/>
<table class='tbl' style='width:80%;'>
<tr>
	<th>$Lang::tr{'network'}</th>
	<th>$Lang::tr{'ip address'}</th>
	<th>$Lang::tr{'status'}</th>
</tr>
END

if ( $netsettings{'GREEN_DEV'} ) {
		my $sub=&General::iporsubtocidr($netsettings{'GREEN_NETMASK'});
		print <<END;
		<tr>
			<td style='width:25%; text-align:center; background-color:$Header::colourgreen;'>
				<a href='/cgi-bin/dhcp.cgi' style='color:white'><b>$Lang::tr{'lan'}</b></a>
			</td>
			<td style='width:30%; text-align:center;'>$netsettings{'GREEN_ADDRESS'}/$sub</td>
			<td style='width:45%; text-align:center;'>
END
		if ( $proxysettings{'ENABLE'} eq 'on' ) {
			print $Lang::tr{'advproxy on'};
			if ( $proxysettings{'TRANSPARENT'} eq 'on' ) { print " (transparent)"; }
		}	else { print $Lang::tr{'advproxy off'};  }
		print '</td>';
		print '</tr>';
	}
if (&Header::blue_used()) {
		my $sub=&General::iporsubtocidr($netsettings{'BLUE_NETMASK'});
		print <<END;
		<tr>
			<td style='width:25%; text-align:center; background-color:$Header::colourblue;'>
				<a href='/cgi-bin/wireless.cgi' style='color:white'><b>$Lang::tr{'wireless'}</b></a>
			</td>
			<td style='width:30%; text-align:center;'>$netsettings{'BLUE_ADDRESS'}/$sub
			<td style='width:45%; text-align:center;'>
END
		if ( $proxysettings{'ENABLE_BLUE'} eq 'on' ) {
			print $Lang::tr{'advproxy on'};
			if ( $proxysettings{'TRANSPARENT_BLUE'} eq 'on' ) { print " (transparent)"; }
		}	else { print $Lang::tr{'advproxy off'};  }
		print '</td>';
		print '</tr>';
	}
if (&Header::orange_used()) {
		my $sub=&General::iporsubtocidr($netsettings{'ORANGE_NETMASK'});
		print <<END;
		<tr>
			<td style='width:25%; text-align:center; background-color:$Header::colourorange;'>
				<a href='/cgi-bin/firewall.cgi' style='color:white'><b>$Lang::tr{'dmz'}</b></a>
			</td>
			<td style='width:30%; text-align:center;'>$netsettings{'ORANGE_ADDRESS'}/$sub</td>
			<td style='width:45%; text-align:center; color:$Header::colourgreen;'>Online</td>
		</tr>
END
	}
#check if IPSEC is running
if ( $vpnsettings{'ENABLED'} eq 'on' || $vpnsettings{'ENABLED_BLUE'} eq 'on' ) {
	my $ipsecip = $vpnsettings{'VPN_IP'};
print<<END;
		<tr>
			<td style='width:25%; text-align:center; background-color:$Header::colourvpn;'>
				<a href='/cgi-bin/vpnmain.cgi' style='color:white'><b>$Lang::tr{'ipsec'}</b></a>
			</td>
			<td style='width:30%; text-align:center;'>$ipsecip</td>
			<td style='width:45%; text-align:center; color:$Header::colourgreen;'>Online</td>
		</tr>
END
}

#check if OpenVPN is running
my %confighash=();
&General::readhash("${General::swroot}/ovpn/settings", \%confighash);

if (($confighash{'ENABLED'} eq "on") ||
    ($confighash{'ENABLED_BLUE'} eq "on") ||
    ($confighash{'ENABLED_ORANGE'} eq "on")) {
	my ($ovpnip,$sub) = split("/",$confighash{'DOVPN_SUBNET'});
	$sub=&General::iporsubtocidr($sub);
	$ovpnip="$ovpnip/$sub";
print <<END;
	<tr>
		<td style='width:25%; text-align:center; background-color:$Header::colourovpn;'>
			<a href='/cgi-bin/ovpnmain.cgi' style='color:white'><b>OpenVPN</b></a>
		</td>
		<td style='width:30%; text-align:center;'>$ovpnip</td>
		<td style='width:45%; text-align:center; color:$Header::colourgreen;'>Online</td>
	</tr>
END
	}
print"</table>";
&Header::closebox();

#Check if there are any vpns configured (ipsec and openvpn)
&General::readhasharray("${General::swroot}/vpn/config", \%vpnconfig);
foreach my $key (sort { ncmp($vpnconfig{$a}[1],$vpnconfig{$b}[1]) } keys %vpnconfig) {
	if ($vpnconfig{$key}[0] eq 'on' && $vpnconfig{$key}[3] ne 'host'){
		$showipsec=1;
		$showbox=1;
		last;
	}
}
&General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%ovpnconfig);
foreach my $dkey (sort { ncmp($ovpnconfig{$a}[1],$ovpnconfig{$b}[1])} keys %ovpnconfig) {
	if (($ovpnconfig{$dkey}[3] eq 'net') && (-e "/var/run/$ovpnconfig{$dkey}[1]n2n.pid")){
		$showbox=1;
		$showovpn=1;
		last;
	}
}

if ($showbox){
# Start of Box wich contains all vpn connections
	&Header::openbox('100%', 'center', $Lang::tr{'vpn'});

	#show ipsec connectiontable
	if ( $showipsec ) {
		my $ipsecip = $vpnsettings{'VPN_IP'};
		my @status = `/usr/local/bin/ipsecctrl I`;
		my %confighash = ();
		my $id = 0;
		my $gif;
		my $col="";
		my $count=0;
		print <<END;
		<table class='tbl' style='width:80%;'>
		<tr>
			<th style='width:40%;'>$Lang::tr{'ipsec network'}</th>
			<th style='width:30%;'>$Lang::tr{'ip address'}</th>
			<th style='width:30%;'>$Lang::tr{'status'}</th>
		</tr>
END
		foreach my $key (sort { uc($vpnconfig{$a}[1]) cmp uc($vpnconfig{$b}[1]) } keys %vpnconfig) {
			if ($vpnconfig{$key}[0] eq 'on' && $vpnconfig{$key}[3] ne 'host') {
				$count++;

				my @n = ();

				my @networks = split(/\|/, $vpnconfig{$key}[11]);
				foreach my $network (@networks) {
					my ($vpnip, $vpnsub) = split("/", $network);
					$vpnsub = &Network::convert_netmask2prefix($vpnsub) || $vpnsub;
					push(@n, "$vpnip/$vpnsub");
				}

				if ($count % 2){
					$col = $color{'color22'};
				}else{
					$col = $color{'color20'};
				}
				print "<tr>";
				print "<td style='text-align:left; color:white; background-color:$Header::colourvpn;'>$vpnconfig{$key}[1]</td>";
				print "<td style='text-align:center; background-color:$col'>" . join("<br>", @n) . "</td>";

				my $activecolor = $Header::colourred;
				my $activestatus = $Lang::tr{'capsclosed'};
				if ($vpnconfig{$key}[33] eq "add") {
					$activecolor = ${Header::colourorange};
					$activestatus = $Lang::tr{'vpn wait'};
				}
				if ($vpnconfig{$key}[0] eq 'off') {
					$activecolor = $Header::colourblue;
					$activestatus = $Lang::tr{'capsclosed'};
				} else {
					foreach my $line (@status) {
						if (($line =~ /\"$vpnconfig{$key}[1]\".*IPsec SA established/) || ($line =~/$vpnconfig{$key}[1]\{.*INSTALLED/ )){
							$activecolor = $Header::colourgreen;
							$activestatus = $Lang::tr{'capsopen'};
						} elsif ($line =~ /$vpnconfig{$key}[1]\[.*CONNECTING/) {
							$activecolor = $Header::colourorange;
							$activestatus = $Lang::tr{'vpn connecting'};
						} elsif ($line =~ /$vpnconfig{$key}[1]\{.*ROUTED/) {
							$activecolor = $Header::colourorange;
							$activestatus = $Lang::tr{'vpn on-demand'};
						}
					}
				}
				print "<td style='text-align:center; color:white; background-color:$activecolor;'><b>$activestatus</b></td>";
				print "</tr>";
			}
		}
		print "</table>";
	}

	# Check if there is any OpenVPN connection configured.
	if ( $showovpn ){
		print <<END;
		<br/>
		<table class='tbl' style='width:80%;'>
		<tr>
			<th style='width:40%;'>$Lang::tr{'openvpn network'}</th>
			<th style='width:30%;'>$Lang::tr{'ip address'}</th>
			<th style='width:30%;'>$Lang::tr{'status'}</th>
END

		# Check if the OpenVPN server for Road Warrior Connections is running and display status information.
		my $active;
		my $count=0;
		# Print the OpenVPN N2N connection status.
		if ( -d "${General::swroot}/ovpn/n2nconf") {
			my $col="";
			foreach my $dkey (sort { ncmp ($ovpnconfig{$a}[1],$ovpnconfig{$b}[1])} keys %ovpnconfig) {
				if (($ovpnconfig{$dkey}[3] eq 'net') && (-e "/var/run/$ovpnconfig{$dkey}[1]n2n.pid")){
					$count++;
					my $tport = $ovpnconfig{$dkey}[22];
					next if ($tport eq '');
					my $tnet = new Net::Telnet ( Timeout=>5, Errmode=>'return', Port=>$tport);
					$tnet->open('127.0.0.1');
					my @output = $tnet->cmd(String => 'state', Prompt => '/(END.*\n|ERROR:.*\n)/');
					my @tustate = split(/\,/, $output[1]);
					my $display;
					my $display_colour = $Header::colourred;
					if ( $tustate[1] eq 'CONNECTED' || ($tustate[1] eq 'WAIT')) {
						$display_colour = $Header::colourgreen;
						$display = $Lang::tr{'capsopen'};
					} else {
						$display = $tustate[1];
					}
					if ($count %2){
						$col = $color{'color22'};
					}else{
						$col = $color{'color20'};
					}
					$active='off';
					#make cidr from ip
					my ($vpnip,$vpnsub) = split("/",$ovpnconfig{$dkey}[11]);
					my $vpnsub=&General::iporsubtocidr($vpnsub);
					my $vpnip="$vpnip/$vpnsub";
					print <<END;
					<tr>
						<td style='text-align:left; color:white; background-color:$Header::colourovpn;'>$ovpnconfig{$dkey}[1]</td>
						<td style='text-align:center; background-color:$col'>$vpnip</td>
						<td style='text-align:center; color:white; background-color:$display_colour' ><b>$display</b></td>
					</tr>
END
				}
			}
		}
		if ($active ne 'off'){
			print "<tr><td colspan='3' style='text-align:center;'>$Lang::tr{'ovpn no connections'}</td></tr>";
		}
		print"</table>";
	}
&Header::closebox();
}

my $dnssec_status = &General::dnssec_status();
if ($dnssec_status eq "off") {
	$warnmessage .= "<li>$Lang::tr{'dnssec disabled warning'}</li>";
}

# Fireinfo
if ( ! -e "/var/ipfire/main/send_profile") {
	$warnmessage .= "<li><a style='color: white;' href='fireinfo.cgi'>$Lang::tr{'fireinfo please enable'}</a></li>";
}

# Memory usage warning
my @free = `/usr/bin/free`;
$free[1] =~ m/(\d+)/;
my $mem = $1;
$free[2] =~ m/(\d+)/;
my $used = $1;
my $pct = int 100 * ($mem - $used) / $mem;
if ($used / $mem > 90) {
	$warnmessage .= "<li>$Lang::tr{'high memory usage'}: $pct% !</li>";
}

# Diskspace usage warning
my @temp=();
my $temp2=();
my @df = `/bin/df -B M -P -x rootfs`;
foreach my $line (@df) {
	next if $line =~ m/^Filesystem/;
	if ($line =~ m/root/ ) {
		$line =~ m/^.* (\d+)M.*$/;
		@temp = split(/ +/,$line);
		if ($1<5) {
			# available:plain value in MB, and not %used as 10% is too much to waste on small disk
			# and root size should not vary during time
			$warnmessage .= "<li>$Lang::tr{'filesystem full'}: $temp[0] <b>$Lang::tr{'free'}=$1M</b> !</li>";
		}
		
	} else {
		# $line =~ m/^.* (\d+)m.*$/;
		$line =~ m/^.* (\d+)\%.*$/;
		if ($1>90) {
			@temp = split(/ /,$line);
			$temp2=int(100-$1);
			$warnmessage .= "<li>$Lang::tr{'filesystem full'}: $temp[0] <b>$Lang::tr{'free'}=$temp2%</b> !</li>";
		}
	}
}

# S.M.A.R.T. health warning
my @files = `/bin/ls /var/run/smartctl_out_hddtemp-* 2>/dev/null`;
foreach my $file (@files) {
	chomp ($file);
	my $disk=`echo $file | cut -d"-" -f2`;
	chomp ($disk);
	if (`/bin/grep "SAVE ALL DATA" $file`) {
		$warnmessage .= "<li>$Lang::tr{'smartwarn1'} /dev/$disk $Lang::tr{'smartwarn2'} !</li>";
	}
}

# Reiser4 warning
my @files = `mount | grep " reiser4 (" 2>/dev/null`;
foreach my $disk (@files) {
	chomp ($disk);
	$warnmessage .= "<li>$disk - $Lang::tr{'deprecated fs warn'}</li>";
}

if ($warnmessage) {
	&Header::openbox('100%','center', );
	print "<table class='tbl' style='width:80%;'>";
	print "<tr><th>$Lang::tr{'fwhost hint'}</th></tr>";
	print "<tr><td style='color:white; background-color:$Header::colourred;'>$warnmessage</td></tr>";
    print "</table>";
	&Header::closebox();
}

&Pakfire::dblist("upgrade", "notice");
if ( -e "/var/run/need_reboot" ) {
	print "<div style='text-align:center; color:red;'>";
	print "<br/><br/>$Lang::tr{'needreboot'}!";
	print "</div>";
}

&Header::closebigbox();
&Header::closepage();

