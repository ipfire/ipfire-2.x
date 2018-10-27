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
#
# WLAN AP cgi based on wlanap.cgi written by Markus Hoffmann & Olaf Westrik
#

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require '/var/ipfire/lang.pl';
require '/var/ipfire/header.pl';

my $debug = 0;
my $status = '';
my $errormessage = '';
my $status_started = "<td align='center' bgcolor='${Header::colourgreen}'><font color='white'><strong>$Lang::tr{'running'}</strong></font></td>";
my $status_stopped = "<td align='center' bgcolor='${Header::colourred}'><font color='white'><strong>$Lang::tr{'stopped'}</strong></font></td>";
my $count=0;
my $col='';
# get rid of used only once warnings
my @onlyonce = ( $Header::colourgreen, $Header::colourred );
undef @onlyonce;

my %selected=();
my %checked=();
my %color = ();
my %mainsettings = ();
my %netsettings=();
my %wlanapsettings=();
my $channel = '';
my $country = '';
my $txpower = '';

&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);
&General::readhash("/var/ipfire/ethernet/settings", \%netsettings);

$wlanapsettings{'APMODE'} = 'on';
$wlanapsettings{'ACTION'} = '';
$wlanapsettings{'MACMODE'} = '0';
$wlanapsettings{'INTERFACE'} = '';
$wlanapsettings{'SSID'} = 'IPFire';
$wlanapsettings{'HIDESSID'} = 'off';
$wlanapsettings{'ENC'} = 'wpa2';               # none / wpa1 /wpa2
$wlanapsettings{'TXPOWER'} = 'auto';
$wlanapsettings{'CHANNEL'} = '6';
$wlanapsettings{'COUNTRY'} = '00';
$wlanapsettings{'HW_MODE'} = 'g';
$wlanapsettings{'PWD'} = 'IPFire-2.x';
$wlanapsettings{'SYSLOGLEVEL'} = '0';
$wlanapsettings{'DEBUG'} = '4';
$wlanapsettings{'DRIVER'} = 'NL80211';
$wlanapsettings{'HTCAPS'} = '';
$wlanapsettings{'VHTCAPS'} = '';
$wlanapsettings{'NOSCAN'} = 'off';

&General::readhash("/var/ipfire/wlanap/settings", \%wlanapsettings);
&Header::getcgihash(\%wlanapsettings);

my @macs = $wlanapsettings{'MACS'};

delete $wlanapsettings{'__CGI__'};
delete $wlanapsettings{'x'};
delete $wlanapsettings{'y'};
delete $wlanapsettings{'MACS'};
delete $wlanapsettings{'ACCEPT_MACS'};
delete $wlanapsettings{'DENY_MACS'};

&Header::showhttpheaders();

my $string=();
my $status=();
my $errormessage = '';
my $memory = 0;
my @memory=();
my @pid=();
my @hostapd=();
sub pid
{
# for pid and memory
	open(FILE, '/usr/local/bin/addonctrl hostapd status | ');
	@hostapd = <FILE>;
	close(FILE);
	$string = join("", @hostapd);
	$string =~ s/[a-z_]//gi;
	$string =~ s/\[[0-1]\;[0-9]+//gi;
	$string =~ s/[\(\)\.]//gi;
	$string =~ s/  //gi;
	$string =~ s///gi;
	@pid = split(/\s/,$string);
	if (open(FILE, "/proc/$pid[0]/statm")){
		my $temp = <FILE>;
		@memory = split(/ /,$temp);
		close(FILE);
		}
	$memory+=$memory[0];
}
pid();



if ( $wlanapsettings{'ACTION'} eq "$Lang::tr{'wlanap del interface'}" ){
	delete $wlanapsettings{'INTERFACE'};
	&General::writehash("/var/ipfire/wlanap/settings", \%wlanapsettings);
}

if ( $wlanapsettings{'ACTION'} eq "$Lang::tr{'save'}" ){
	# verify WPA Passphrase - only with enabled enc
	if (($wlanapsettings{'ENC'} eq "wpa1") || ($wlanapsettings{'ENC'} eq "wpa2") || ($wlanapsettings{'ENC'} eq "wpa1+2")){
		# must be 8 .. 63 characters
		if ( (length($wlanapsettings{'PWD'}) < 8) || (length($wlanapsettings{'PWD'}) > 63)){
			$errormessage .= "$Lang::tr{'wlanap invalid wpa'}<br />";
		}
		# only ASCII alowed
		if ( !($wlanapsettings{'PWD'} !~ /[^\x00-\x7f]/) ){
			$errormessage .= "$Lang::tr{'wlanap invalid wpa'}<br />";
		}
	}

	if ( $errormessage eq '' ){
		&General::writehash("/var/ipfire/wlanap/settings", \%wlanapsettings);
		&WriteConfig_hostapd();

		system("/usr/local/bin/wlanapctrl restart >/dev/null 2>&1");
		pid();
	}
}elsif ( $wlanapsettings{'ACTION'} eq "$Lang::tr{'wlanap interface'}" ){
	&General::writehash("/var/ipfire/wlanap/settings", \%wlanapsettings);
}elsif ( ($wlanapsettings{'ACTION'} eq "$Lang::tr{'start'}") && ($memory == 0) ){
	system("/usr/local/bin/wlanapctrl start >/dev/null 2>&1");
	pid();
}elsif ( $wlanapsettings{'ACTION'} eq "$Lang::tr{'stop'}" ){
	system("/usr/local/bin/wlanapctrl stop >/dev/null 2>&1");
	$memory=0;
}

&Header::openpage($Lang::tr{'wlanap configuration'}, 1, '', '');
&Header::openbigbox('100%', 'left', '', $errormessage);

if ( $errormessage ){
	&Header::openbox('100%', 'center', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
}


# Found this usefull piece of code in BlockOutTraffic AddOn  8-)
#   fwrules.cgi
###############
# DEBUG DEBUG
if ( $debug ){
	&Header::openbox('100%', 'center', 'DEBUG');
	my $debugCount = 0;
	foreach my $line (sort keys %wlanapsettings) {
		print "$line = '$wlanapsettings{$line}'<br />\n";
		$debugCount++;
	}
	print "&nbsp;Count: $debugCount\n";
	&Header::closebox();
}
# DEBUG DEBUG
###############

#
# Driver and status detection
#
my $wlan_card_status = 'dummy';
my $wlan_ap_status = '';
my $message = "";

$selected{'INTERFACE'}{'green0'} = '';
$selected{'INTERFACE'}{'blue0'} = '';
$selected{'ENC'}{$wlanapsettings{'INTERFACE'}} = "selected='selected'";

if ( ($wlanapsettings{'INTERFACE'} eq '') ){
	$message = $Lang::tr{'wlanap select interface'};
	&Header::openbox('100%', 'center', "WLAN AP");
print <<END
$message<br />
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<select name='INTERFACE'>
END
;
	if ( $netsettings{'BLUE_DEV'} ne ''){
		print "<option value='blue0' $selected{'INTERFACE'}{'blue0'}>blue0</option>";
	}
print <<END
		<option value='green0' $selected{'INTERFACE'}{'green0'}>green0</option>
</select>
<br /><br />
<hr size='1'>
	<input type='submit' name='ACTION' value='$Lang::tr{'wlanap interface'}' /></form>
END
;
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit;
}else{
	my $cmd_out = `/usr/sbin/iwconfig $wlanapsettings{'INTERFACE'} 2>/dev/null`;

	if ( $cmd_out eq '' ){
		$message = "$Lang::tr{'wlanap no interface'}";
		$wlan_card_status = '';
	}else{
		$cmd_out = `/sbin/ifconfig | /bin/grep $wlanapsettings{'INTERFACE'}`;
		if ( $cmd_out eq '' ){
			$wlan_card_status = 'down';
		}else{
			$wlan_card_status = 'up';
			$cmd_out = `/usr/sbin/iwconfig $wlanapsettings{'INTERFACE'} | /bin/grep "Mode:Master"`;
			if ( $cmd_out ne '' ){
				$wlan_ap_status = 'up';
			}
		}
	}
}

# Change old "n" to "gn"
if ( $wlanapsettings{'HW_MODE'} eq 'n' ) {
	$wlanapsettings{'HW_MODE'}='gn';
}

$checked{'HIDESSID'}{'off'} = '';
$checked{'HIDESSID'}{'on'} = '';
$checked{'HIDESSID'}{$wlanapsettings{'HIDESSID'}} = "checked='checked'";

$checked{'NOSCAN'}{'off'} = '';
$checked{'NOSCAN'}{'on'} = '';
$checked{'NOSCAN'}{$wlanapsettings{'NOSCAN'}} = "checked='checked'";

$selected{'ENC'}{$wlanapsettings{'ENC'}} = "selected='selected'";
$selected{'CHANNEL'}{$wlanapsettings{'CHANNEL'}} = "selected='selected'";
$selected{'COUNTRY'}{$wlanapsettings{'COUNTRY'}} = "selected='selected'";
$selected{'TXPOWER'}{$wlanapsettings{'TXPOWER'}} = "selected='selected'";
$selected{'HW_MODE'}{$wlanapsettings{'HW_MODE'}} = "selected='selected'";
$selected{'MACMODE'}{$wlanapsettings{'MACMODE'}} = "selected='selected'";

my $monwlaninterface = $wlanapsettings{'INTERFACE'};
if ( -d '/sys/class/net/mon.'.$wlanapsettings{'INTERFACE'} ) {
	$monwlaninterface =  'mon.'.$wlanapsettings{'INTERFACE'};
}

my @channellist_cmd;
my @channellist;

if ( $wlanapsettings{'DRIVER'} eq 'NL80211' ){
my $wiphy = `iw dev $wlanapsettings{'INTERFACE'} info | grep wiphy | cut -d" " -f2`;
chomp $wiphy;

@channellist_cmd = `iw phy phy$wiphy info | grep " MHz \\\[" | grep -v "(disabled)" | grep -v "no IBSS" | grep -v "no IR" | grep -v "passive scanning" 2>/dev/null`;
# get available channels

my @temp;
foreach (@channellist_cmd){
$_ =~ /(.*) \[(\d+)(.*)\]/;
$channel = $2;chomp $channel;
if ( $channel =~ /\d+/ ){push(@temp,$channel + 0);}
}
@channellist = @temp;
} else {
@channellist_cmd = `iwlist $monwlaninterface channel|tail -n +2 2>/dev/null`;
# get available channels

my @temp;
foreach (@channellist_cmd){
$_ =~ /(.*)Channel (\d+)(.*):/;
$channel = $2;chomp $channel;
if ( $channel =~ /\d+/ ){push(@temp,$channel + 0);}
}
@channellist = @temp;
}

my @countrylist_cmd = `regdbdump /usr/lib/crda/regulatory.bin 2>/dev/null`;
# get available country codes

my @temp = "00";
foreach (@countrylist_cmd){
$_ =~ /country (.*):/;
$country = $1;chomp $country;
if ( $country =~ /[0,A-Z][0,A-Z]/ ) {push(@temp,$country);}
}
my @countrylist = @temp;

my @txpower_cmd = `iwlist $monwlaninterface txpower 2>/dev/null`;
if ( $wlanapsettings{'DRIVER'} eq 'NL80211' ){
	# There is a bug with NL80211 only all devices can displayed
	@txpower_cmd = `iwlist txpower 2>/dev/null | sed -e "s|unknown transmit-power information.||g"`;
}
# get available power

$selected{'SYSLOGLEVEL'}{$wlanapsettings{'SYSLOGLEVEL'}} = "selected='selected'";
$selected{'DEBUG'}{$wlanapsettings{'DEBUG'}} = "selected='selected'";

#
# Status box
#
&Header::openbox('100%', 'center', "WLAN AP");
print <<END
<table width='80%' cellspacing='1' class='tbl'>
END
;

if ( $wlan_card_status ne '' ){
	print "<tr><th align='left' width='50%'><strong>$Lang::tr{'service'}</strong></th><th width='22%'>Status</th><th width='10%'>PID</th><th width='15%'>$Lang::tr{'memory'}</th><th colspan='2'width='5%'>$Lang::tr{'action'}</th></tr>";
	print "<tr><td class='base'>$Lang::tr{'wlanap wlan card'} ($wlanapsettings{'DRIVER'})</td>";
	print $wlan_card_status eq 'up' ? $status_started : $status_stopped;
	print"<td colspan='4'></td></tr>";
	print "<tr><td class='base' bgcolor='$color{'color22'}'>$Lang::tr{'wlanap'}</td>";
	print $wlan_ap_status eq 'up' ? $status_started : $status_stopped;
	if ( ($memory != 0) && (@pid[0] ne "///") ){
		print "<td bgcolor='$color{'color22'}' align='center'>@pid[0]</td>";
		print "<td bgcolor='$color{'color22'}' align='center'>$memory KB</td>";
		print "<td bgcolor='$color{'color22'}'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='$Lang::tr{'start'}' /><input type='image' alt='$Lang::tr{'start'}' title='$Lang::tr{'start'}' src='/images/go-up.png' /></form></td>";
		print "<td bgcolor='$color{'color22'}'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='$Lang::tr{'stop'}' /><input type='image' alt='$Lang::tr{'stop'}' title='$Lang::tr{'stop'}' src='/images/go-down.png' /></form></td>";
	}else{
		print"<td colspan='2' bgcolor='$color{'color22'}'></td>";
		print "<td bgcolor='$color{'color22'}'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='$Lang::tr{'start'}' /><input type='image' alt='$Lang::tr{'start'}' title='$Lang::tr{'start'}' src='/images/go-up.png' /></form></td>";
		print "<td bgcolor='$color{'color22'}'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='$Lang::tr{'stop'}' /><input type='image' alt='$Lang::tr{'stop'}' title='$Lang::tr{'stop'}' src='/images/go-down.png' /></form></td>";
	}

}else{
	print "<tr><td class='base'>$message";
}
	print "</table>";

if ( $wlan_card_status eq '' ){
	print "<br />";
	print "<table width='80%' cellspacing='0' border='0'>";
	print "<tr align='center'>";
	print "<td colspan='4'></td>";
	print "</tr>";
	print "<tr align='center'>";
	print "<td width='40%'>&nbsp;</td>";
	print "<td width='20%'><form method='post' action='/cgi-bin/wlanap.cgi'><input type='submit' name='ACTION' value='$Lang::tr{'wlanap del interface'}' /></form></td>";
	print "<td width='20%'></td>";
	print "<td width='20%'></td>";
	print "</tr>";
	print "</table>";
}

if ( $wlan_card_status eq '' ){
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit 0;
}
print <<END
<br><br>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='80%' cellspacing='0' class='tbl' border='0'>
<tr><th bgcolor='$color{'color20'}' colspan='4' align='left'><strong>$Lang::tr{'wlanap wlan settings'}</strong></th></tr>
<tr><td colspan='4'><br></td></tr>
<tr><td width='25%' class='base'>SSID:&nbsp;</td><td class='base' colspan='3'><input type='text' name='SSID' size='30' value='$wlanapsettings{'SSID'}' /></td></tr>
<!--SSID Broadcast: on => HIDESSID: off -->
<tr><td width='25%' class='base'>SSID Broadcast:&nbsp;</td><td class='base' colspan='3'>on <input type='radio' name='HIDESSID' value='off' $checked{'HIDESSID'}{'off'} /> | <input type='radio' name='HIDESSID' value='on' $checked{'HIDESSID'}{'on'} /> off</td></tr>


<tr><td width='25%' class='base'>$Lang::tr{'wlanap country'}:&nbsp;</td><td class='base' colspan='3'>
	<select name='COUNTRY'>
END
;
foreach $country (@countrylist){
	print "<option $selected{'COUNTRY'}{$country}>$country</option>";
}
print<<END
</select></td></tr>
<tr><td width='25%' class='base'>HW Mode:&nbsp;</td><td class='base' colspan='3'>
	<select name='HW_MODE'>
		<option value='a' $selected{'HW_MODE'}{'a'}>802.11a</option>
		<option value='b' $selected{'HW_MODE'}{'b'}>802.11b</option>
		<option value='g' $selected{'HW_MODE'}{'g'}>802.11g</option>
		<option value='an' $selected{'HW_MODE'}{'an'}>802.11an</option>
		<option value='gn' $selected{'HW_MODE'}{'gn'}>802.11gn</option>
		<option value='ac' $selected{'HW_MODE'}{'ac'}>802.11ac</option>
	</select>
</td></tr>
END
;

if ( scalar @channellist > 0 ){
	print <<END
<tr><td width='25%' class='base'>$Lang::tr{'wlanap channel'}:&nbsp;</td><td class='base' colspan='3'>
	<select name='CHANNEL'>
END
;
	foreach $channel (@channellist){
		print "<option $selected{'CHANNEL'}{$channel}>$channel</option>";
	}
	print "</select></td></tr>"
} else {
	print <<END
<tr><td width='25%' class='base'>$Lang::tr{'wlanap channel'}:&nbsp;</td><td class='base' colspan='3'>
<input type='text' name='CHANNEL' size='10' value='$wlanapsettings{'CHANNEL'}' />
</td></tr>
END
;
}
print<<END
<tr><td width='25%' class='base'>$Lang::tr{'wlanap neighbor scan'}:&nbsp;</td><td class='base' >on <input type='radio' name='NOSCAN' value='off' $checked{'NOSCAN'}{'off'} /> | <input type='radio' name='NOSCAN' value='on' $checked{'NOSCAN'}{'on'} /> off</td><td class='base' colspan='2'>$Lang::tr{'wlanap neighbor scan warning'}</td></tr>
<tr><td colspan='4'><br></td></tr>
<tr><td width='25%' class='base'>$Lang::tr{'wlanap encryption'}:&nbsp;</td><td class='base' colspan='3'>
	<select name='ENC'>
		<option value='none' $selected{'ENC'}{'none'}>$Lang::tr{'wlanap none'}</option>
		<option value='wpa1' $selected{'ENC'}{'wpa1'}>WPA1</option>
		<option value='wpa2' $selected{'ENC'}{'wpa2'}>WPA2</option>
		<option value='wpa1+2' $selected{'ENC'}{'wpa1+2'}>WPA1+2</option>
	</select>
</td></tr>
<tr><td width='25%' class='base'>Passphrase:&nbsp;</td><td class='base' colspan='3'><input type='text' name='PWD' size='30' value='$wlanapsettings{'PWD'}' /></td></tr>
<tr><td colspan='4'><br></td></tr>
END
;
print <<END
<tr><td width='25%' class='base'>HT Caps:&nbsp;</td><td class='base' colspan='3'><input type='text' name='HTCAPS' size='30' value='$wlanapsettings{'HTCAPS'}' /></td></tr>
<tr><td width='25%' class='base'>VHT Caps:&nbsp;</td><td class='base' colspan='3'><input type='text' name='VHTCAPS' size='30' value='$wlanapsettings{'VHTCAPS'}' /></td></tr>
<tr><td width='25%' class='base'>Tx Power:&nbsp;</td><td class='base' colspan='3'><input type='text' name='TXPOWER' size='10' value='$wlanapsettings{'TXPOWER'}' /></td></tr>
<tr><td width='25%' class='base'>Loglevel (hostapd):&nbsp;</td><td class='base' width='25%'>
	<select name='SYSLOGLEVEL'>
		<option value='0' $selected{'SYSLOGLEVEL'}{'0'}>0 ($Lang::tr{'wlanap verbose'})</option>
		<option value='1' $selected{'SYSLOGLEVEL'}{'1'}>1 ($Lang::tr{'wlanap debugging'})</option>
		<option value='2' $selected{'SYSLOGLEVEL'}{'2'}>2 ($Lang::tr{'wlanap informations'})</option>
		<option value='3' $selected{'SYSLOGLEVEL'}{'3'}>3 ($Lang::tr{'wlanap notifications'})</option>
		<option value='4' $selected{'SYSLOGLEVEL'}{'4'}>4 ($Lang::tr{'wlanap warnings'})</option>
	</select>
</td>
<td width='25%' class='base'>Debuglevel (hostapd):&nbsp;</td><td class='base' width='25%'>
	<select name='DEBUG'>
		<option value='0' $selected{'DEBUG'}{'0'}>0 ($Lang::tr{'wlanap verbose'})</option>
		<option value='1' $selected{'DEBUG'}{'1'}>1 ($Lang::tr{'wlanap debugging'})</option>
		<option value='2' $selected{'DEBUG'}{'2'}>2 ($Lang::tr{'wlanap informations'})</option>
		<option value='3' $selected{'DEBUG'}{'3'}>3 ($Lang::tr{'wlanap notifications'})</option>
		<option value='4' $selected{'DEBUG'}{'4'}>4 ($Lang::tr{'wlanap warnings'})</option>
	</select>
</td></tr>
<tr><td colspan='4'><br></td></tr>
</table>
END
;
if ( $wlanapsettings{'INTERFACE'} =~ /green0/ ){
	print <<END
<br />
<table width='80%' cellspacing='0' class='tbl' border='1'>
<tr>
	<th colspan='3' align='left'>$Lang::tr{'mac filter'}</th>
</tr>
<td width='25%' class='base'>Mac Filter:&nbsp;</td><td class='base' width='25%'>
	<select name='MACMODE'>
		<option value='0' $selected{'MACMODE'}{'0'}>0 (off)</option>
		<option value='1' $selected{'MACMODE'}{'1'}>1 (Accept MACs)</option>
		<option value='2' $selected{'MACMODE'}{'2'}>2 (Deny MACs)</option>
	</select>
</td><td colspan='2'>Mac Adress List (one per line)<br /><textarea name='MACS' cols='20' rows='5' wrap='off'>
END
;
	print `cat /var/ipfire/wlanap/macfile`;
print <<END
</textarea></td>
</table>
END
;
}
print <<END
<br />
<table width='80%' cellspacing='0'>
<tr><td align='center'>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
       <input type='hidden' name='ACTION' value=$Lang::tr{'save'} />
       <input type='image' alt='$Lang::tr{'save'}' title='$Lang::tr{'save'}' src='/images/media-floppy.png' /></form></td>
</tr>
</table>
END
;
my @status;
if ( $wlanapsettings{'DRIVER'} eq 'NL80211' ){
	 @status =  `iw dev $wlanapsettings{'INTERFACE'} info && iw dev $wlanapsettings{'INTERFACE'} station dump && echo ""`;
}
print <<END
<br />
<table width='80%' cellspacing='0' class='tbl'>
<tr><th colspan='3' bgcolor='$color{'color20'}' align='left'><strong>$Lang::tr{'wlanap wlan status'}</strong></th></tr>
END
;

for (my $i=0;$i<$#status;$i++){

if (@status[$i]=~"^Station ") { $count++; }
if ($count % 2){
		$col="bgcolor='$color{'color20'}'";
	}else{
		$col="bgcolor='$color{'color22'}'";
	}
	print"<tr><td colspan='3' $col><pre>@status[$i]</pre></td></tr>";
	if (! @status[$i]=~"^/t" ) { $count++; }
}
	$count++;

foreach my $nr (@channellist_cmd){
	if ($count % 2){
		$col="bgcolor='$color{'color20'}'";
	}else{
		$col="bgcolor='$color{'color22'}'";
	}
	print"<tr><td colspan='3' $col>$nr</td></tr>";
	$count++;
}

for (my $i=0;$i<$#txpower_cmd;$i=$i+2){
	if ($count % 2){
		$col="bgcolor='$color{'color20'}'";
	}else{
		$col="bgcolor='$color{'color22'}'";
	}
	print "<tr><td $col>@txpower_cmd[$i]</td></tr>";
	$count++;
}
print "</table><br>";
print <<END
<br />
<table width='80%' cellspacing='0' class='tbl' border='0'>
<tr><td bgcolor='$color{'color20'}' align='left'><strong>$Lang::tr{'wlan clients'}</strong></td></tr>
<tr><td>&nbsp;<a href="/cgi-bin/wireless.cgi">$Lang::tr{'wlanap link wireless'}</a></td></tr>
<tr><td>&nbsp;<a href="/cgi-bin/dhcp.cgi">$Lang::tr{'wlanap link dhcp'}</a></td></tr>
<tr><td><br></td></tr>
</table>
END
;
&Header::closebox();
print "</form>";
&Header::closebigbox();
&Header::closepage();

sub WriteConfig_hostapd{
	$wlanapsettings{'DRIVER_HOSTAPD'} = lc($wlanapsettings{'DRIVER'});

	open (CONFIGFILE, ">/var/ipfire/wlanap/hostapd.conf");
	print CONFIGFILE <<END
driver=$wlanapsettings{'DRIVER_HOSTAPD'}
######################### basic hostapd configuration ##########################
#
interface=$wlanapsettings{'INTERFACE'}
country_code=$wlanapsettings{'COUNTRY'}
ieee80211d=1
ieee80211h=1
channel=$wlanapsettings{'CHANNEL'}
END
;
 if ( $wlanapsettings{'HW_MODE'} eq 'an' ){
	print CONFIGFILE <<END
hw_mode=a
ieee80211n=1
wmm_enabled=1
ht_capab=$wlanapsettings{'HTCAPS'}
END
;

 }elsif ( $wlanapsettings{'HW_MODE'} eq 'gn' ){
	print CONFIGFILE <<END
hw_mode=g
ieee80211n=1
wmm_enabled=1
ht_capab=$wlanapsettings{'HTCAPS'}
END
;

 }elsif ( $wlanapsettings{'HW_MODE'} eq 'ac' ){
	print CONFIGFILE <<END
hw_mode=a
ieee80211ac=1
ieee80211n=1
wmm_enabled=1
ht_capab=$wlanapsettings{'HTCAPS'}
vht_capab=$wlanapsettings{'VHTCAPS'}
END
;

 }else{
 	print CONFIGFILE <<END
hw_mode=$wlanapsettings{'HW_MODE'}
END
;

 }

print CONFIGFILE <<END
logger_syslog=-1
logger_syslog_level=$wlanapsettings{'SYSLOGLEVEL'}
logger_stdout=-1
logger_stdout_level=$wlanapsettings{'DEBUG'}
dump_file=/tmp/hostapd.dump
auth_algs=1
ctrl_interface=/var/run/hostapd
ctrl_interface_group=0
END
;
 if ( $wlanapsettings{'HIDESSID'} eq 'on' ){
	print CONFIGFILE <<END
ssid=$wlanapsettings{'SSID'}
ignore_broadcast_ssid=2
END
;

 }else{
 	print CONFIGFILE <<END
ssid=$wlanapsettings{'SSID'}
ignore_broadcast_ssid=0
END
;

 }

 if ( $wlanapsettings{'NOSCAN'} eq 'on' ){
	print CONFIGFILE <<END
noscan=1
END
;

 }else{
 	print CONFIGFILE <<END
noscan=0
END
;

 }

 if ( $wlanapsettings{'ENC'} eq 'wpa1'){
	print CONFIGFILE <<END
######################### wpa hostapd configuration ############################
#
wpa=1
wpa_passphrase=$wlanapsettings{'PWD'}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
END
;
 }elsif ( $wlanapsettings{'ENC'} eq 'wpa2'){
	print CONFIGFILE <<END
######################### wpa hostapd configuration ############################
#
wpa=2
wpa_passphrase=$wlanapsettings{'PWD'}
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
END
;
 } elsif ( $wlanapsettings{'ENC'} eq 'wpa1+2'){
	print CONFIGFILE <<END
######################### wpa hostapd configuration ############################
#
wpa=3
wpa_passphrase=$wlanapsettings{'PWD'}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
END
;
 }
	close CONFIGFILE;

	open (MACFILE, ">/var/ipfire/wlanap/macfile");
	foreach(@macs){
		$_ =~ s/\r//gi;
		chomp($_);
		if ( $_ ne "" ){print MACFILE $_;}
	}
	close MACFILE;
}
