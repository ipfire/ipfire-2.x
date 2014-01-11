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
use Net::Telnet;

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
my $warnmessage = '';
my $refresh = "";
my $ipaddr='';

my $haveipsec=0;
my $haveovpn=0;

&Header::showhttpheaders();

$cgiparams{'ACTION'} = '';
&Header::getcgihash(\%cgiparams);
$pppsettings{'VALID'} = '';
$pppsettings{'PROFILENAME'} = 'None';
&General::readhash("${General::swroot}/ppp/settings", \%pppsettings);
&General::readhash("${General::swroot}/modem/settings", \%modemsettings);
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
&General::readhash("${General::swroot}/ddns/settings", \%ddnssettings);

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

my $connstate = &Header::connectionstatus();

	if ( -e "/var/ipfire/main/gpl-accepted" ) {
if ($connstate =~ /$Lang::tr{'connecting'}/ || /$Lang::tr{'connection closed'}/ ){
	$refresh = "<meta http-equiv='refresh' content='5;'>";
} elsif ($connstate =~ /$Lang::tr{'dod waiting'}/ || -e "${General::swroot}/main/refreshindex") {
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
	system ("/usr/bin/touch", "${General::swroot}/ppp/updatesettings");

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
	or &General::log("Dial failed: $?"); sleep 1;}
elsif ($cgiparams{'ACTION'} eq $Lang::tr{'hangup'}) {
	system('/usr/local/bin/redctrl stop > /dev/null') == 0
	or &General::log("Hangup failed: $?"); sleep 1;}

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

# licence agreement
if ($cgiparams{'ACTION'} eq $Lang::tr{'yes'} && $cgiparams{'gpl_accepted'} eq '1') {
	system('touch /var/ipfire/main/gpl_accepted')
}
if ( -e "/var/ipfire/main/gpl_accepted" ) {
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
<table width=80% class='tbl'>
  <tr>  <th bgcolor='$color{'color20'}'>$Lang::tr{'network'}</th>
        <th bgcolor='$color{'color20'}'>$Lang::tr{'ip address'}</th>
        <th bgcolor='$color{'color20'}'>$Lang::tr{'status'}</th></tr>
  <tr>  <td align='center' bgcolor='$Header::colourred' width='25%'><a href="/cgi-bin/pppsetup.cgi"><font size='2' color='white'><b>$Lang::tr{'internet'}</b></font></a><br></td>
        <td width='30%' align='center'>$ipaddr </td>
        <td width='45%' align='center'>$connstate 
END
	my $HOSTNAME = (gethostbyaddr(pack("C4", split(/\./, $ipaddr)), 2))[0];
	if ( "$HOSTNAME" ne "" ) {
		print <<END;
	<tr><td><b>Hostname:</b><td align='center'>$HOSTNAME<td>&nbsp;
END
	}

	if ( -e "/var/ipfire/red/remote-ipaddress" ) {
		my $GATEWAY = `cat /var/ipfire/red/remote-ipaddress`;
		chomp($GATEWAY);
		print <<END;
	<tr><td><b>Gateway:</b><td align='center'>$GATEWAY<td>&nbsp;
END
	}

	my $DNS1 = `cat /var/ipfire/red/dns1`;
	my $DNS2 = `cat /var/ipfire/red/dns2`;
	chomp($DNS1);
	chomp($DNS1);

	if ( $DNS1 ) { print <<END;
	<tr><td><b>DNS-Server:</b><td align='center'>$DNS1
END
	}
	if ( $DNS2 ) { print <<END;
	<td align='center'>$DNS2
END
	} else { print <<END;
	<td>&nbsp;</td>
	</tr>
	</table>
END
	}

#Dial profiles
if ( $netsettings{'RED_TYPE'} ne "STATIC" && $netsettings{'RED_TYPE'} ne "DHCP" ){
print `/usr/local/bin/dialctrl.pl show`;
print <<END;
<br>
		<table width='80%'>
		<tr><td>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>$Lang::tr{'profile'}:
			<select name='PROFILE'>
END
	for ($c = 1; $c <= $maxprofiles; $c++)
	{
		if ($profilenames[$c] ne '') {
			$dialButtonDisabled = "";
			print "\t<option value='$c' $selected{'PROFILE'}{$c}>$c. $profilenames[$c]</option>\n";
		}
	}
	$dialButtonDisabled = "disabled='disabled'" if (-e '/var/run/ppp-ipfire.pid' || -e "${General::swroot}/red/active");
	if ( ( $pppsettings{'VALID'} eq 'yes' ) || ( $netsettings{'CONFIG_TYPE'} =~ /^(1|2|3|4)$/ && $netsettings{'RED_TYPE'} =~ /^(DHCP|STATIC)$/ ) ) {
		print <<END;
				</select>
				<input type='submit' name='ACTION' value='$Lang::tr{'dial profile'}' $dialButtonDisabled />
			</form>
			<td align='center'>
				<table width='100%' border='0'>
					<tr>
					<td width='50%' align='right'>	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
											<input type='submit' name='ACTION' value='$Lang::tr{'dial'}'>
										</form>
					<td width='50%' align='left'>	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
											<input type='submit' name='ACTION' value='$Lang::tr{'hangup'}'>
										</form>
				</table>
END
	} else {
	print "$Lang::tr{'profile has errors'}\n </b></font>\n";
	}
	print"</tr></table>";
}
	if ( $netsettings{'GREEN_DEV'} ) {
		my $sub=&General::iporsubtocidr($netsettings{'GREEN_NETMASK'});
		print <<END;
		<br>
		<table width='80%' class='tbl'>
		<tr>
			<th>$Lang::tr{'network'}</th>
			<th>$Lang::tr{'ip address'}</th>
			<th>$Lang::tr{'status'}</th>
		</tr>
		<tr><td align='center' bgcolor='$Header::colourgreen' width='25%'><a href="/cgi-bin/dhcp.cgi"><font size='2' color='white'><b>$Lang::tr{'lan'}</b></font></a>
		<td width='30%' align='center'>$netsettings{'GREEN_ADDRESS'}/$sub
		<td width='45%' align='center'>
END
		if ( `cat /var/ipfire/proxy/advanced/settings | grep ^ENABLE=on` ) { 
			print $Lang::tr{'advproxy on'}; 
			if ( `cat /var/ipfire/proxy/advanced/settings | grep ^TRANSPARENT=on` ) { print " (transparent)"; }
		}	else { print $Lang::tr{'advproxy off'};  }
	}
	if ( $netsettings{'BLUE_DEV'} ) {
		my $sub=&General::iporsubtocidr($netsettings{'BLUE_NETMASK'});
		print <<END;
		<tr><td align='center' bgcolor='$Header::colourblue' width='25%'><a href="/cgi-bin/wireless.cgi"><font size='2' color='white'><b>$Lang::tr{'wireless'}</b></font></a><br>
		<td width='30%' align='center'>$netsettings{'BLUE_ADDRESS'}/$sub
		<td width='45%' align='center'>
END
		if ( `cat /var/ipfire/proxy/advanced/settings | grep ^ENABLE_BLUE=on` ) { 
			print $Lang::tr{'advproxy on'};  
			if ( `cat /var/ipfire/proxy/advanced/settings | grep ^TRANSPARENT_BLUE=on` ) { print " (transparent)"; }
		}	else { print $Lang::tr{'advproxy off'};  }
	}
	if ( $netsettings{'ORANGE_DEV'} ) {
		my $sub=&General::iporsubtocidr($netsettings{'ORANGE_NETMASK'});
		print <<END;
		<tr><td align='center' bgcolor='$Header::colourorange' width='25%'><a href="/cgi-bin/firewall.cgi"><font size='2' color='white'><b>$Lang::tr{'dmz'}</b></font></a><br>
		<td width='30%' align='center'>$netsettings{'ORANGE_ADDRESS'}/$sub
		<td width='45%' align='center'><font color=$Header::colourgreen>Online</font>
END
	}
#check if IPSEC is running
if ( `cat /var/ipfire/vpn/settings | grep ^ENABLED=on` ||
	`cat /var/ipfire/vpn/settings | grep ^ENABLED_BLUE=on` ) {
	$haveipsec=1;
	my $ipsecip = `cat /var/ipfire/vpn/settings | grep ^VPN_IP= | cut -c 8-`;
print<<END;
		<tr><td align='center' bgcolor='$Header::colourvpn' width='25%'><a href="/cgi-bin/vpnmain.cgi"><font size='2' color='white'><b>$Lang::tr{'ipsec'}</b></font></a><br>
		<td width='30%' align='center'>$ipsecip
		<td width='45%' align='center'><font color=$Header::colourgreen>Online</font>
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
	$haveovpn=1;
print <<END;
	<tr>
		<td align='center' bgcolor='$Header::colourovpn' width='25%'>
			<a href="/cgi-bin/ovpnmain.cgi"><font size='2' color='white'><b>OpenVPN</b></font></a><br>
		</td>
		<td width='30%' align='center'>$ovpnip
	<td width='45%' align='center'><font color=$Header::colourgreen>Online</font>
END
	}
print"</td></tr></table>";
&Header::closebox();

# Start of Box wich contains all vpn connections
	&Header::openbox('100%', 'center', $Lang::tr{'vpn'}) if ($haveipsec || $haveovpn);

#show ipsec connectiontable
	if ( $haveipsec ) {
		my $ipsecip = `cat /var/ipfire/vpn/settings | grep ^VPN_IP= | cut -c 8-`;
		my @status = `/usr/local/bin/ipsecctrl I`;
		my %confighash = ();
		&General::readhasharray("${General::swroot}/vpn/config", \%confighash);
		print <<END;
		<br>
		<table width='80%' class='tbl'>
		<tr>
			<th>$Lang::tr{'ipsec network'}</th>
			<th>$Lang::tr{'ip address'}</th>
			<th>$Lang::tr{'status'}</th>
		</tr>
END
		my $id = 0;
		my $gif;
		my $col="";
		foreach my $key (sort { uc($confighash{$a}[1]) cmp uc($confighash{$b}[1]) } keys %confighash) {
			if ($confighash{$key}[0] eq 'on') { $gif = 'on.gif'; } else { $gif = 'off.gif'; }
			my ($vpnip,$vpnsub) = split("/",$confighash{$key}[11]);
			$vpnsub=&General::iporsubtocidr($vpnsub);
			$vpnip="$vpnip/$vpnsub";
			if ($id % 2) {
				$col="bgcolor='$color{'color20'}'";
				print "<tr><td align='left' nowrap='nowrap' bgcolor='$Header::colourvpn' width='50%'><font color=white>$confighash{$key}[1] / " . $Lang::tr{"$confighash{$key}[3]"} . " (" . $Lang::tr{"$confighash{$key}[4]"} . ")</td><td align='center' $col>$vpnip</td>";
			} else {
				$col="bgcolor='$color{'color22'}'";
				print "<tr></td><td align='left' nowrap='nowrap' bgcolor='$Header::colourvpn' width='50%'><font color=white>$confighash{$key}[1] / " . $Lang::tr{"$confighash{$key}[3]"} . " (" . $Lang::tr{"$confighash{$key}[4]"} . ")</td><td align='center' $col>$vpnip</td>";
			}
			
			my $active = "<td bgcolor='${Header::colourred}' width='15%' align='center'><b><font color='#FFFFFF'>$Lang::tr{'capsclosed'}</font></b></td>";
			if ($confighash{$key}[0] eq 'off') {
			    $active = "<td bgcolor='${Header::colourblue}' width='15%' align='center'><b><font color='#FFFFFF'>$Lang::tr{'capsclosed'}</font></b></td>";
			} else {
			    foreach my $line (@status) {
				if (($line =~ /\"$confighash{$key}[1]\".*IPsec SA established/) ||
				    ($line =~/$confighash{$key}[1]\{.*INSTALLED/ ))
				    {
				    $active = "<table cellpadding='2' cellspacing='0' bgcolor='${Header::colourgreen}' width='100%'><tr><td align='center'><b><font color='#FFFFFF'>$Lang::tr{'capsopen'}</font></b></td></tr></table>";
				}
			   }
			}
			print "$active</td>";
		}
		print "</tr></table>";
	}

###
# Check if there is any OpenVPN connection configured.
###

if ( $haveovpn )
{
	print <<END;
	<br>
	<table width='80%' class='tbl'>
	<tr>
		<th>$Lang::tr{'openvpn network'}</th>
		<th>$Lang::tr{'ip address'}</th>
		<th>$Lang::tr{'status'}</th>
END
	# Check if the OpenVPN server for Road Warrior Connections is running and display status information.
	my %confighash=();

	&General::readhash("${General::swroot}/ovpn/settings", \%confighash);
	# Print the OpenVPN N2N connection status.
	if ( -d "${General::swroot}/ovpn/n2nconf") {
		my %confighash=();

		&General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
		my $lines;
		my $col="";
		foreach my $dkey (keys %confighash) {
			$lines++;
			if (($confighash{$dkey}[3] eq 'net') && (-e "/var/run/$confighash{$dkey}[1]n2n.pid")) {
				my $tport = $confighash{$dkey}[22];
				next if ($tport eq '');

				my $tnet = new Net::Telnet ( Timeout=>5, Errmode=>'return', Port=>$tport); 
				$tnet->open('127.0.0.1');
				my @output = $tnet->cmd(String => 'state', Prompt => '/(END.*\n|ERROR:.*\n)/');
				my @tustate = split(/\,/, $output[1]);

				my $display;
				my $display_colour = $Header::colourred;
				if ( $tustate[1] eq 'CONNECTED') {
					$display_colour = $Header::colourgreen;
					$display = $Lang::tr{'capsopen'};
				} else {
					$display = $tustate[1];
				}
				if ($lines %2){
					$col="bgcolor='$color{'color20'}'";
				}else{
					$col="bgcolor='$color{'color22'}'";
				}
				#make cidr from ip
				my ($vpnip,$vpnsub) = split("/",$confighash{$dkey}[11]);
				my $vpnsub=&General::iporsubtocidr($vpnsub);
				my $vpnip="$vpnip/$vpnsub";
				print <<END;
				<tr>
					<td align='left' nowrap='nowrap' bgcolor='$Header::colourovpn' width='50%'><font color=white>
						$confighash{$dkey}[1]
					</td>
					<td align='center' $col>
						$vpnip
					</td>
					<td align='center' bgcolor='$display_colour' width='15%'>
						<b>
							<font color='#FFFFFF'>
								$display
							</font>
						</b>
					</td>
				</tr>
END
			}
		}
	}
}
&Header::closebox();
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
	$warnmessage .= "<li> $Lang::tr{'high memory usage'}: $pct% !</li>\n";
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
			$warnmessage .= "<li> $Lang::tr{'filesystem full'}: $temp[0] <b>$Lang::tr{'free'}=$1M</b> !</li>\n";
		}
		
	} else {
		# $line =~ m/^.* (\d+)m.*$/;
		$line =~ m/^.* (\d+)\%.*$/;
		if ($1>90) {
			@temp = split(/ /,$line);
			$temp2=int(100-$1);
			$warnmessage .= "<li> $Lang::tr{'filesystem full'}: $temp[0] <b>$Lang::tr{'free'}=$temp2%</b> !</li>\n";
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
		$warnmessage .= "<li> $Lang::tr{'smartwarn1'} /dev/$disk $Lang::tr{'smartwarn2'} !</li>\n\n";
	}
}

# Reiser4 warning
my @files = `mount | grep " reiser4 (" 2>/dev/null`;
foreach my $disk (@files) {
	chomp ($disk);
	$warnmessage .= "<li>$disk - $Lang::tr{'deprecated fs warn'}</li>\n\n";
}


if ($warnmessage) {
	print "<tr><td align='center' bgcolor=$Header::colourred colspan='3'><font color='white'>$warnmessage</font></table>";
}
print <<END;
</table>
END
;
&Pakfire::dblist("upgrade", "notice");
print <<END;
END
if ( -e "/var/run/need_reboot" ) {
	print "<br /><br /><font color='red'>$Lang::tr{'needreboot'}!</font>";
}
&Header::closebox();
}

else {
&Header::openbox('100%', 'left', $Lang::tr{'gpl license agreement'});
print <<END;
	$Lang::tr{'gpl please read carefully the general public license and accept it below'}.
	<br /><br />
END
;	
if ( -e "/usr/share/doc/licenses/GPLv3" ) {
	print '<textarea rows=\'25\' cols=\'75\' readonly=\'true\'>';
	print `cat /usr/share/doc/licenses/GPLv3`;
	print '</textarea>';
}
else {
	print '<br /><a href=\'http://www.gnu.org/licenses/gpl-3.0.txt\' target=\'_blank\'>GNU GENERAL PUBLIC LICENSE</a><br />';
}
print <<END;
	<p>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='checkbox' name='gpl_accepted' value='1'/> $Lang::tr{'gpl i accept these terms and conditions'}.
			<br/ >
			<input type='submit' name='ACTION' value=$Lang::tr{'yes'} />
		</form>
	</p>
	<a href='http://www.gnu.org/licenses/translations.html' target='_blank'>$Lang::tr{'gpl unofficial translation of the general public license v3'}</a>

END

&Header::closebox();
}

&Header::closebigbox();
&Header::closepage();
