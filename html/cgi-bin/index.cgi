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
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %cgiparams=();
my %pppsettings=();
my %modemsettings=();
my %netsettings=();
my %ddnssettings=();
my $warnmessage = '';
my $refresh = '';
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

my $connstate = &Header::connectionstatus();
if ($connstate =~ /$Lang::tr{'dod waiting'}/ || -e "${General::swroot}/main/refreshindex") {
	$refresh = "<meta http-equiv='refresh' content='30;'>";
} elsif ($connstate =~ /$Lang::tr{'connecting'}/) {
	$refresh = "<meta http-equiv='refresh' content='5;'>";
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
&Header::openbox('100%', 'center', &Header::cleanhtml(`/bin/uname -n`,"y"));

if ( ( $pppsettings{'VALID'} eq 'yes'&& $modemsettings{'VALID'} eq 'yes' ) || ( $netsettings{'CONFIG_TYPE'} =~ /^(2|3|6|7)$/ && $netsettings{'RED_TYPE'} =~ /^(DHCP|STATIC)$/ )) {
	if ($connstate =~ /$Lang::tr{'connected'}/) {
	    if ($ddnssettings{'BEHINDROUTER'} eq 'FETCH_IP') {
	        if (open(IPADDR,"${General::swroot}/ddns/ipcache")) {
	   	    $ipaddr = <IPADDR>;
	    	    close IPADDR;
	    	    chomp ($ipaddr);
		}
	    }
	    if (open(IPADDR,"${General::swroot}/red/local-ipaddress")) {
	   	my $ipaddr = <IPADDR>;
	    	close IPADDR;
	    	chomp ($ipaddr);
	    }
        }
} elsif ($modemsettings{'VALID'} eq 'no') {
	print "$Lang::tr{'modem settings have errors'}\n </b></font>\n";
} else {
	print "$Lang::tr{'profile has errors'}\n </b></font>\n";
}

if ( $netsettings{'RED_TYPE'} =~ /^(DHCP|STATIC)$/ ) {
	$ipaddr = $netsettings{'RED_ADDRESS'};
}

print <<END;
<table border='0'>
<tr>
	<td align='center'><form method='post' action="$ENV{'SCRIPT_NAME'}">
		<input type='submit' name='ACTION' value='$Lang::tr{'refresh'}' />
	</form></td>
</tr></table>

<!-- Table of networks -->
<table border='0' width=80%>
  <!--  Headline -->
  <tr>	<th bgcolor='lightgrey'>$Lang::tr{'network'}
	<th bgcolor='lightgrey'>IP
	<th bgcolor='lightgrey'>$Lang::tr{'status'}
  <!-- RED -->
  <tr>	<td bgcolor='$Header::colourred' width='25%'><font size='2' color='white'><b>$Lang::tr{'internet'}:</b></font><br>
	<td width='30%'>$ipaddr <td width='45%'>$connstate
	<tr><td colspan='2'>
		<form method='post' action='/cgi-bin/dial.cgi'>$Lang::tr{'profile'}:
			<select name='PROFILE'>
END
	for ($c = 1; $c <= $maxprofiles; $c++)
	{
		if ($profilenames[$c] ne '') {
			$dialButtonDisabled = "";
			print "\t<option value='$c' $selected{'PROFILE'}{$c}>$c. $profilenames[$c]</option>\n";
		}
	}
	$dialButtonDisabled = "disabled='disabled'" if (-e '/var/run/ppp-ipcop.pid' || -e "${General::swroot}/red/active");
	if ( ( $pppsettings{'VALID'} eq 'yes' ) || ( $netsettings{'CONFIG_TYPE'} =~ /^(2|3|6|7)$/ && $netsettings{'RED_TYPE'} =~ /^(DHCP|STATIC)$/ ) ) {
		print <<END;
				</select>
				<input type='submit' name='ACTION' value='$Lang::tr{'dial profile'}' $dialButtonDisabled />
			</form>
			<td align='center'>
				<table width='100%' border='0'>
					<tr>
					<td width='50%' align='right'>	<form method='post' action='/cgi-bin/dial.cgi'>
											<input type='submit' name='ACTION' value='$Lang::tr{'dial'}'>
										</form>
					<td width='50%' align='left'>	<form method='post' action='/cgi-bin/dial.cgi'>
											<input type='submit' name='ACTION' value='$Lang::tr{'hangup'}'>
										</form>
				</table>
END
	} else {
	print "$Lang::tr{'profile has errors'}\n </b></font>\n";
	}

print <<END;
  <!-- Green -->
  <tr><td bgcolor='$Header::colourgreen' width='25%'>
		<font size='2' color='white'><b>$Lang::tr{'lan'}:</b></font>
  	<td width='30%'>$netsettings{'GREEN_ADDRESS'}
  	<td width='45%'>
END
	if (`ifconfig | grep $netsettings{'GREEN_DEV'}`) { print "<font color=$Header::colourgreen>Online</font>"; } else { print "<font color=$Header::colourred>Offline</font>"; }
print <<END;
  <!-- BLUE -->
  <tr><td bgcolor='$Header::colourblue' width='25%'><font size='2' color='white'><b>$Lang::tr{'wireless'}:</b></font><br>
  	<td width='30%'>$netsettings{'BLUE_ADDRESS'}
  	<td width='45%'>
END
	if (`ifconfig | grep $netsettings{'BLUE_DEV'}`) { print "<font color=$Header::colourgreen>Online</font>"; } else { print "<font color=$Header::colourred>Offline</font>"; }
print <<END;
  <tr><td bgcolor='$Header::colourorange' width='25%'><font size='2' color='white'><b>$Lang::tr{'dmz'}:</b></font><br>
  	<td width='30%'>$netsettings{'ORANGE_ADDRESS'}
  	<td width='45%'>
END
	if (`ifconfig | grep $netsettings{'ORANGE_DEV'}`) { print "<font color=$Header::colourgreen>Online</font>"; } else { print "<font color=$Header::colourred>Offline</font>"; }
print <<END;
  <tr><td bgcolor='$Header::colourvpn' width='25%'><font size='2' color='white'><b>$Lang::tr{'vpn'}:</b></font><br>
  	<td width='30%'>N/A
  	<td width='45%'>
END
	if (`ifconfig | grep ipsec0`) { print "<font color=$Header::colourgreen>Online</font>"; } else { print "<font color=$Header::colourred>Offline</font>"; }
print <<END;
  <tr><td bgcolor='$Header::colourovpn' width='25%'><font size='2' color='white'><b>OpenVPN:</b></font><br>
  	<td width='30%'>N/A
  	<td width='45%'>
END
	if (`ifconfig | grep tun0`) { print "<font color=$Header::colourgreen>Online</font>"; } else { print "<font color=$Header::colourred>Offline</font>"; }
print <<END;
</table>
END

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

# Patches warning
open(AV, "<${General::swroot}/patches/available") or die "Could not open available patches database ($!)";
my @av = <AV>;
close(AV);
open(PF, "<${General::swroot}/patches/installed") or die "Could not open installed patches file. ($!)<br />";
while(<PF>)
{
        next if $_ =~ m/^#/;
        @temp = split(/\|/,$_);
        @av = grep(!/^$temp[0]/, @av);
}
close(PF);

if ($#av != -1) 
{
	$warnmessage .= "<li> $Lang::tr{'there are updates'}</li>";
}
my $age = &General::age("/${General::swroot}/patches/available");
if ($age =~ m/(\d{1,3})d/) {
	if ($1 >= 7) {
		$warnmessage .= "<li>$Lang::tr{'updates is old1'} $age $Lang::tr{'updates is old2'}</li>\n";
	}
}

if ($warnmessage) {
	print "<ol>$warnmessage</ol>";
}

print "<p>";
system('/usr/bin/uptime');
print "</p>\n";

&Header::closebox();

&Header::closebigbox();

&Header::closepage();
