#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#

use strict;

# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %cgiparams=();
my %pppsettings=();
my %modemsettings=();
my %netsettings=();
my %ddnssettings=();
my $warnmessage = '';
my $refresh = "";
my $ipaddr='';

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
if ($connstate =~ /$Lang::tr{'dod waiting'}/ || -e "${General::swroot}/main/refreshindex") {
	$refresh = "<meta http-equiv='refresh' content='30;'>";
} elsif ($connstate =~ /$Lang::tr{'connecting'}/) {
	$refresh = "<meta http-equiv='refresh' content='5;'>";
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
&Header::openbox('100%', 'center', &Header::cleanhtml(`/bin/uname -n`,"y"));

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

if ( $netsettings{'RED_TYPE'} =~ /^(DHCP|STATIC)$/ ) {
	$ipaddr = $netsettings{'RED_ADDRESS'};
}

my $death = 0;
my $rebirth = 0;

if ($cgiparams{'ACTION'} eq $Lang::tr{'shutdown'}) {
	$death = 1;
	&General::log($Lang::tr{'shutting down ipfire'});
	system '/usr/local/bin/ipfirereboot down';
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'reboot'}) {
	$rebirth = 1;
	&General::log($Lang::tr{'rebooting ipfire'});
	system '/usr/local/bin/ipfirereboot boot';
}

if ($death == 0 && $rebirth == 0) {

print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='100%'>
<tr>
	<td width='33%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'reboot'}' /></td>
	<td width='33%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'refresh'}' /></td>
	<td width='33%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'shutdown'}' /></td>
</tr>
</table>
END
;
print <<END;

<!-- Table of networks -->
<table border='0' width=80%>
  <tr>	<th bgcolor='$color{'color20'}'>$Lang::tr{'network'}
	<th bgcolor='$color{'color20'}'>IP
	<th bgcolor='$color{'color20'}'>$Lang::tr{'status'}
  <tr>	<td bgcolor='$Header::colourred' width='25%'><a href="/cgi-bin/pppsetup.cgi"><font size='2' color='white'><b>$Lang::tr{'internet'}:</b></font></a><br>
	<td width='30%'>$ipaddr 
	<td width='45%'>$connstate
END
print `/usr/local/bin/dialctrl.pl show`;
print <<END;
	<tr><td colspan='2'>
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

	my $HOSTNAME = (gethostbyaddr(pack("C4", split(/\./, $ipaddr)), 2))[0];
	if ( "$HOSTNAME" ne "" ) {
		print <<END;
	<tr><td><b>Hostname:</b><td>$HOSTNAME<td>&nbsp;
END
	}

	if ( -e "/var/ipfire/red/remote-ipaddress" ) {
		my $GATEWAY = `cat /var/ipfire/red/remote-ipaddress`;
		chomp($GATEWAY);
		print <<END;
	<tr><td><b>Gateway:</b><td>$GATEWAY<td>&nbsp;
END
	}

	my $DNS1 = `cat /var/ipfire/red/dns1`;
	my $DNS2 = `cat /var/ipfire/red/dns2`;
	chomp($DNS1);
	chomp($DNS1);

	if ( $DNS1 ) { print <<END;
	<tr><td><b>DNS-Server:</b><td>$DNS1
END
	}
	if ( $DNS2 ) { print <<END;
	<td>$DNS2
END
	} else { print <<END;
	<td>&nbsp;
END
	}

	if ( $netsettings{'GREEN_DEV'} ) { print <<END;
		<tr><td bgcolor='$Header::colourgreen' width='25%'><a href="/cgi-bin/dhcp.cgi"><font size='2' color='white'><b>$Lang::tr{'lan'}:</b></font></a>
	  	<td width='30%'>$netsettings{'GREEN_ADDRESS'}
  		<td width='45%'>
END
		if ( `cat /var/ipfire/proxy/advanced/settings | grep ^ENABLE=on` ) { 
			print "Proxy an"; 
			if ( `cat /var/ipfire/proxy/advanced/settings | grep ^TRANSPARENT=on` ) { print " (transparent)"; }
		}	else { print "Proxy aus"; }
	}
	if ( $netsettings{'BLUE_DEV'} ) { print <<END;
		<tr><td bgcolor='$Header::colourblue' width='25%'><a href="/cgi-bin/wireless.cgi"><font size='2' color='white'><b>$Lang::tr{'wireless'}:</b></font></a><br>
	  	<td width='30%'>$netsettings{'BLUE_ADDRESS'}
  		<td width='45%'>
END
		if ( `cat /var/ipfire/proxy/advanced/settings | grep ^ENABLE_BLUE=on` ) { 
			print "Proxy an"; 
			if ( `cat /var/ipfire/proxy/advanced/settings | grep ^TRANSPARENT_BLUE=on` ) { print " (transparent)"; }
		}	else { print "Proxy aus"; }
	}
	if ( $netsettings{'ORANGE_DEV'} ) { print <<END;
		<tr><td bgcolor='$Header::colourorange' width='25%'><a href="/cgi-bin/dmzholes.cgi"><font size='2' color='white'><b>$Lang::tr{'dmz'}:</b></font></a><br>
	  	<td width='30%'>$netsettings{'ORANGE_ADDRESS'}
  		<td width='45%'><font color=$Header::colourgreen>Online</font>
END
	}
	if ( `cat /var/ipfire/vpn/settings | grep ^ENABLED=on` ||
	     `cat /var/ipfire/vpn/settings | grep ^ENABLED_BLUE=on` ) { 
		my $ipsecip = `cat /var/ipfire/vpn/settings | grep ^VPN_IP= | cut -c 8-`;
		my @status = `/usr/sbin/ipsec auto --status`;
		my %confighash = ();
		&General::readhasharray("${General::swroot}/vpn/config", \%confighash);
		print <<END;
		<tr><td bgcolor='$Header::colourvpn' width='25%'><a href="/cgi-bin/vpnmain.cgi"><font size='2' color='white'><b>$Lang::tr{'vpn'}:</b></font></a><br>
	  	<td width='30%'>$ipsecip
  		<td width='45%'><font color=$Header::colourgreen>Online</font>
END
		my $id = 0;
		my $gif;
		foreach my $key (keys %confighash) {
			if ($confighash{$key}[0] eq 'on') { $gif = 'on.gif'; } else { $gif = 'off.gif'; }

			if ($id % 2) {
			    print "<tr bgcolor='${Header::table1colour}'>\n";
			} else {
			    print "<tr bgcolor='${Header::table2colour}'>\n";
			}
			print "<td bgcolor='#ffffff'>&nbsp;</td><td align='center' nowrap='nowrap'>$confighash{$key}[1] / " . $Lang::tr{"$confighash{$key}[3]"} . " (" . $Lang::tr{"$confighash{$key}[4]"} . ")</td>";
			my $active = "<table cellpadding='2' cellspacing='0' bgcolor='${Header::colourred}' width='100%'><tr><td align='center'><b><font color='#FFFFFF'>$Lang::tr{'capsclosed'}</font></b></td></tr></table>";
			if ($confighash{$key}[0] eq 'off') {
			    $active = "<table cellpadding='2' cellspacing='0' bgcolor='${Header::colourblue}' width='100%'><tr><td align='center'><b><font color='#FFFFFF'>$Lang::tr{'capsclosed'}</font></b></td></tr></table>";
			} else {
			    foreach my $line (@status) {
				if ($line =~ /\"$confighash{$key}[1]\".*IPsec SA established/) {
				    $active = "<table cellpadding='2' cellspacing='0' bgcolor='${Header::colourgreen}' width='100%'><tr><td align='center'><b><font color='#FFFFFF'>$Lang::tr{'capsopen'}</font></b></td></tr></table>";
				}
			   }
			}
			print "<td align='center'>$active</td>";
		}
	}
	if ( `cat /var/ipfire/ovpn/settings | grep ^ENABLED=on` || 
	     `cat /var/ipfire/ovpn/settings | grep ^ENABLED_BLUE=on` || 
	     `cat /var/ipfire/ovpn/settings | grep ^ENABLED_ORANGE=on`) { 
		my $ovpnip = `cat /var/ipfire/ovpn/settings | grep ^DOVPN_SUBNET= | cut -c 14- | sed -e 's\/\\/255.255.255.0\/\/'`;
		print <<END;
		<tr><td bgcolor='$Header::colourovpn' width='25%'><a href="/cgi-bin/ovpnmain.cgi"><font size='2' color='white'><b>OpenVPN:</b></font></a><br>
	  	<td width='30%'>$ovpnip
  		<td width='45%'><font color=$Header::colourgreen>Online</font>
END
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
my @df = `/bin/df -B M -x rootfs`;
foreach my $line (@df) {
	next if $line =~ m/^Filesystem/;
	if ($line =~ m/root/ ) {
		$line =~ m/^.* (\d+)M.*$/;
		@temp = split(/ +/,$line);
		if ($1<5) {
			# available:plain value in MB, and not %used as 10% is too much to waste on small disk
			# and root size should not vary during time
			$warnmessage .= "$Lang::tr{'filesystem full'}: $temp[0] <b>$Lang::tr{'free'}=$1M</b> !\n";
		}
		
	} else {
		# $line =~ m/^.* (\d+)m.*$/;
		$line =~ m/^.* (\d+)\%.*$/;
		if ($1>90) {
			@temp = split(/ /,$line);
			$temp2=int(100-$1);
			$warnmessage .= "$Lang::tr{'filesystem full'}: $temp[0] <b>$Lang::tr{'free'}=$temp2%</b> !\n";
		}
	}
}

if ($warnmessage) {
	print "<tr><td align='center' bgcolor=$Header::colourred colspan='3'><font color='white'>$warnmessage</font></table>";
}
print <<END;
</table>

END
} else {
	my $message='';
	if ($death) {
		$message = $Lang::tr{'ipfire has now shutdown'};
	} else {
		$message = $Lang::tr{'ipfire has now rebooted'};
	}
	print <<END
<div align='center'>
<table width='100%' bgcolor='#ffffff'>
<tr><td align='center'>
<br /><br /><img src='/ipfire_big.gif' /><br /><br /><br />
</td></tr>
</table>
<br />
<font size='6'>$message</font>
</div>
END
;
}
&Header::closebox();
&Header::closebigbox();
&Header::closepage();
