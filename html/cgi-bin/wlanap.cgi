#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007  Michael Tremer & Christian Schmidt                      #
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
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require '/var/ipfire/lang.pl';
require '/var/ipfire/header.pl';

my $debug = 0;
my $i = 0;
my $errormessage = '';
my $status_started = "<td align='center' bgcolor='${Header::colourgreen}'><font color='white'><b>$Lang::tr{'running'}</b></font></td>";
my $status_stopped = "<td align='center' bgcolor='${Header::colourred}'><font color='white'><b>$Lang::tr{'stopped'}</b></font></td>";

# get rid of used only once warnings
my @onlyonce = ( $Header::colourgreen, $Header::colourred );
undef @onlyonce;

my %selected=();
my %checked=();
my %color = ();
my %mainsettings = ();
my $channel = '';
my $txpower = '';

&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

my %wlanapsettings=();
$wlanapsettings{'APMODE'} = 'on';
$wlanapsettings{'BOOTSTART'} = 'on';
$wlanapsettings{'SSID'} = 'IPFire';
$wlanapsettings{'HIDESSID'} = 'off';
$wlanapsettings{'ENC'} = 'wpa';               # none / wep / wpa / wep+wpa
$wlanapsettings{'ANTENNA'} = 'both';
$wlanapsettings{'TXPOWER'} = 'auto';
# $wlanapsettings{'CC'} = '276';                    # CountryCode, 276 = Germany
$wlanapsettings{'CHAN'} = '5';

$wlanapsettings{'WEPKEY1'} = 'BF715772DADA8A3E7AFFA5C26B';
$wlanapsettings{'WEPKEY2'} = '';
$wlanapsettings{'WEPKEY3'} = '';
$wlanapsettings{'WEPKEY4'} = '';
$wlanapsettings{'USEDKEY'} = '1';

$wlanapsettings{'PWD'} = 'IPFire-2.x';
$wlanapsettings{'PSK'} = '69eb868ed7b3cc36d767b729048c9c585234723d1eafbe66e5a16957b7c85e9c';
$wlanapsettings{'WPA'} = '3';

$wlanapsettings{'SYSLOGLEVEL'} = '0';
$wlanapsettings{'DEBUG'} = '4';
$wlanapsettings{'DRIVER'} = 'MADWIFI';            # UNKNOWN / MADWIFI / RT2500 / PRISM54 / ...

# WLANMODE= (a/b/g)
&General::readhash("/var/ipfire/wlanap/settings", \%wlanapsettings);

my %netsettings=();
&General::readhash("/var/ipfire/ethernet/settings", \%netsettings);

my %cgiparams=();
$cgiparams{'ACTION'} = '';
$cgiparams{'RUNNING'} = 'off';
$cgiparams{'APMODE'} = 'on';
$cgiparams{'BOOTSTART'} = 'on';
$cgiparams{'SSID'} = 'IPFire';
$cgiparams{'HIDESSID'} = 'off';
$cgiparams{'ENC'} = 'wpa';               # none / wep / wpa / wep+wpa
$cgiparams{'ANTENNA'} = 'both';
$cgiparams{'TXPOWER'} = 'auto';
$cgiparams{'CHAN'} = '5';

$cgiparams{'WEPKEY1'} = 'BF715772DADA8A3E7AFFA5C26B';
$cgiparams{'WEPKEY2'} = '';
$cgiparams{'WEPKEY3'} = '';
$cgiparams{'WEPKEY4'} = '';
$cgiparams{'USEDKEY'} = '1';
$cgiparams{'WEPPWD'} = '';
$cgiparams{'WEPKEYCALC'} = '';

$cgiparams{'PWD'} = 'IPFire-2.x';
$cgiparams{'PSK'} = '69eb868ed7b3cc36d767b729048c9c585234723d1eafbe66e5a16957b7c85e9c';
$cgiparams{'WPA'} = '3';

$cgiparams{'SYSLOGLEVEL'} = '0';
$cgiparams{'DEBUG'} = '4';
&Header::getcgihash(\%cgiparams);


&Header::showhttpheaders();

if ( $cgiparams{'ACTION'} eq "$Lang::tr{'save'}" ){
	$wlanapsettings{'APMODE'}     = $cgiparams{'APMODE'};
	$wlanapsettings{'BOOTSTART'}  = $cgiparams{'BOOTSTART'};
	$wlanapsettings{'SSID'}       = $cgiparams{'SSID'};
	$wlanapsettings{'HIDESSID'}   = $cgiparams{'HIDESSID'};
	$wlanapsettings{'ENC'}        = $cgiparams{'ENC'};
	$wlanapsettings{'ANTENNA'}    = $cgiparams{'ANTENNA'};
	$wlanapsettings{'CHAN'}       = $cgiparams{'CHAN'};
	$wlanapsettings{'TXPOWER'}    = $cgiparams{'TXPOWER'};

	$wlanapsettings{'WEPKEY1'}    = $cgiparams{'WEPKEY1'};
	$wlanapsettings{'WEPKEY2'}    = $cgiparams{'WEPKEY2'};
	$wlanapsettings{'WEPKEY3'}    = $cgiparams{'WEPKEY3'};
	$wlanapsettings{'WEPKEY4'}    = $cgiparams{'WEPKEY4'};
	$wlanapsettings{'USEDKEY'}    = $cgiparams{'USEDKEY'};

	$wlanapsettings{'PWD'}        = $cgiparams{'PWD'};
	$wlanapsettings{'PSK'}        = $cgiparams{'PSK'};
	$wlanapsettings{'WPA'}        = $cgiparams{'WPA'};
	$wlanapsettings{'SYSLOGLEVEL'}= $cgiparams{'SYSLOGLEVEL'};
	$wlanapsettings{'DEBUG'}      = $cgiparams{'DEBUG'};

	# verify WEP keys, allowed characters are 0..9A..F, length must be 10 or 26 characters
	for $i ( 1 .. 4 ){
		my $wepkey = $wlanapsettings{"WEPKEY${i}"};
		next if ( $wepkey eq '' );
		if ( (length($wepkey) != 10) && (length($wepkey) != 26) ){
			$errormessage .= "Invalid length in WEP Key $i. Key must be 10 or 26 characters.<br />";
			next;
		}

		if ( $wepkey !~ /[0-9A-Fa-f]$/ ){
			$errormessage .= "Invalid character in WEP Key $i. Only A..F and 0..9 allowed.<br />";
			next;
		}

		$wlanapsettings{"WEPKEY${i}"} = uc($wepkey);
	}

	# verify WPA Passphrase, must be 8 .. 63 characters
	if ( (length($wlanapsettings{'PWD'}) < 8) || (length($wlanapsettings{'PWD'}) > 63) ){
		$errormessage .= "Invalid length in WPA Passphrase. Must be between 8 and 63 characters.<br />";
	}

	if ( $errormessage eq '' ){
		&WriteConfig();
		&WriteConfig_hostapd();

		system("/usr/local/bin/wlanapctrl start >/dev/null 2>&1") if ( $cgiparams{'RUNNING'} eq 'on' );
	}
}elsif ( $cgiparams{'ACTION'} eq 'Start' ){
	system("/usr/local/bin/wlanapctrl start >/dev/null 2>&1");
}elsif ( $cgiparams{'ACTION'} eq 'Stop' ){
	system("/usr/local/bin/wlanapctrl stop >/dev/null 2>&1");
}elsif ( $cgiparams{'ACTION'} eq 'Calc WEP Key' ){
	$cgiparams{'WEPKEYCALC'} = '';
	$errormessage = "Invalid length in WEP Passphrase. Must be exactly 13 characters.<br />" if ( length($cgiparams{'WEPPWD'}) != 13 );

	if ( $errormessage eq '' ){
		$cgiparams{'WEPKEYCALC'} = uc(&WEPKeyCalc($cgiparams{'WEPPWD'}));
	}
}elsif ( $cgiparams{'ACTION'} eq 'Random WEP Key' ){
	$cgiparams{'WEPKEYCALC'} = &WEPKeyRandom();
}

&Header::openpage('WLAN', 1, '', '');
&Header::openbigbox('100%', 'left', '', $errormessage);
print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>";

if ( $errormessage ){
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
}


# Found this usefull piece of code in BlockOutTraffic AddOn  8-)
#   fwrules.cgi
###############
# DEBUG DEBUG
if ( $debug ){
	&Header::openbox('100%', 'left', 'DEBUG');
	my $debugCount = 0;
	foreach my $line (sort keys %cgiparams) {
		print "$line = '$cgiparams{$line}'<br />\n";
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
my $wlan_hostapd_status = '';
my $blue_message = "";

if ( ($netsettings{'BLUE_DEV'} eq '') || ($netsettings{'BLUE_DRIVER'} eq '') ){
	$blue_message = "No BLUE Interface.";
}else{
	my $cmd_out = `/usr/sbin/iwconfig $netsettings{'BLUE_DEV'} 2>/dev/null`;

	if ( $cmd_out eq '' ){
		$blue_message = "BLUE Interface is not a WLAN card.";
	}else{
		$cmd_out = `/sbin/ifconfig | /bin/grep $netsettings{'BLUE_DEV'}`;
		if ( $cmd_out eq '' ){
			$wlan_card_status = 'down';
		}else{
			$wlan_card_status = 'up';
			$cmd_out = `/usr/sbin/iwconfig $netsettings{'BLUE_DEV'} | /bin/grep "Mode:Master"`;
			if ( $cmd_out ne '' ){
				$wlan_ap_status = 'up';
				if ( -e "/var/run/hostapd.pid" ){
					$wlan_hostapd_status = 'up';
				}
			}
		}
	}
}

my $disabled_apmode = "disabled='disabled'";
$disabled_apmode = '' if ( ($wlanapsettings{'DRIVER'} eq 'MADWIFI') || ($wlanapsettings{'DRIVER'} eq 'HOSTAP') || ($wlanapsettings{'DRIVER'} eq 'ACX100') );

my $checked_apmode = '';
my $checked_bootstart = '';
my $checked_hidessid = '';
$checked_apmode = "checked='checked'" if ( $wlanapsettings{'APMODE'} eq 'on' );
$checked_bootstart = "checked='checked'" if ( $wlanapsettings{'BOOTSTART'} eq 'on' );
$checked_hidessid = "checked='checked'" if ( $wlanapsettings{'HIDESSID'} eq 'on' );

$selected{'ENC'}{'none'} = '';
$selected{'ENC'}{'wep'} = '';
$selected{'ENC'}{'wpa'} = '';
$selected{'ENC'}{'wep+wpa'} = '';
$selected{'ENC'}{$wlanapsettings{'ENC'}} = "selected='selected'";

$selected{'ANTENNA'}{'both'} = '';
$selected{'ANTENNA'}{'1'} = '';
$selected{'ANTENNA'}{'2'} = '';
$selected{'ANTENNA'}{$wlanapsettings{'ANTENNA'}} = "selected='selected'";

my @channellist;
# get available channels
if ( -e "/var/ipfire/wlanap/channels" ){
	open(CHANNELFILE, "/var/ipfire/wlanap/channels");
	@channellist=<CHANNELFILE>;
	close CHANNELFILE;
	foreach $channel (@channellist){
		chomp($channel);
		$selected{'CHAN'}{$channel} = '';
	}
	$selected{'CHAN'}{$wlanapsettings{'CHAN'}} = 'selected="selected"';
}else{
	$channellist[0] = '1';
	$selected{'CHAN'}{'1'} = 'selected="selected"';
}

my @txpowerlist;
# get available txpowers
if ( -e "/var/ipfire/wlanap/txpower" ){
	open(CHANNELFILE, "/var/ipfire/wlanap/txpower");
	@txpowerlist=<CHANNELFILE>;
	close CHANNELFILE;
	foreach $txpower (@txpowerlist){
		chomp($txpower);
		$selected{'TXPOWER'}{$txpower} = '';
	}
	$selected{'TXPOWER'}{$wlanapsettings{'TXPOWER'}} = 'selected="selected"';
}else{
	$txpowerlist[0] = 'auto';
	$selected{'TXPOWER'}{'auto'} = 'selected="selected"';
}

$selected{'USEDKEY'}{'1'} = '';
$selected{'USEDKEY'}{'2'} = '';
$selected{'USEDKEY'}{'3'} = '';
$selected{'USEDKEY'}{'4'} = '';
$selected{'USEDKEY'}{$wlanapsettings{'USEDKEY'}} = "selected='selected'";

$selected{'WPA'}{'1'} = '';
$selected{'WPA'}{'2'} = '';
$selected{'WPA'}{'3'} = '';
$selected{'WPA'}{$wlanapsettings{'WPA'}} = "selected='selected'";

$selected{'SYSLOGLEVEL'}{'0'} = '';
$selected{'SYSLOGLEVEL'}{'1'} = '';
$selected{'SYSLOGLEVEL'}{'2'} = '';
$selected{'SYSLOGLEVEL'}{'3'} = '';
$selected{'SYSLOGLEVEL'}{'4'} = '';
$selected{'SYSLOGLEVEL'}{$wlanapsettings{'SYSLOGLEVEL'}} = "selected='selected'";

$selected{'DEBUG'}{'0'} = '';
$selected{'DEBUG'}{'1'} = '';
$selected{'DEBUG'}{'2'} = '';
$selected{'DEBUG'}{'3'} = '';
$selected{'DEBUG'}{'4'} = '';
$selected{'DEBUG'}{$wlanapsettings{'DEBUG'}} = "selected='selected'";

#
# Status box
#
&Header::openbox('100%', 'left', "WLAN Status");
print <<END
<table width='100%'>
END
;
if ( $wlan_card_status ne '' ){
	print "<tr><td class='base'><b>WLAN card ($wlanapsettings{'DRIVER'})</b></td>";
	print $wlan_card_status eq 'up' ? $status_started : $status_stopped;
	print "<td colspan='2'>&nbsp;</td></tr>";
	print "<tr><td class='base'><b>Access Point</b></td>";
	print $wlan_ap_status eq 'up' ? $status_started : $status_stopped;
	print "<td colspan='2'>&nbsp;</td></tr>";
	print "<tr><td class='base'><b>Hostapd</b></td>";
	print $wlan_hostapd_status eq 'up' ? $status_started : $status_stopped;
	print "<td colspan='2'>&nbsp;</td></tr>";
	print "<tr><td width='30%' align='right'>&nbsp;</td>";
	print "<td width='25' align='right'>&nbsp;</td>";
	if ( $wlan_card_status eq 'up' ){
		print "<td width='40%' align='center'><input type='submit' name='ACTION' value='Stop' /><input type='hidden' name='RUNNING' value='on' /></td>";
	}else{
		print "<td width='40%' align='center'><input type='submit' name='ACTION' value='Start' /></td>";
	}
	print "<td width='5%' align='right'>&nbsp;</td>";
	print "</tr>";
}else{
	print "<tr><td width='55%' class='base'><b>$blue_message</b></td><td width='40%' align='center'>&nbsp;";
	if ( $netsettings{'CONFIG_TYPE'} & 0x04 ){
		print "<input type='submit' name='ACTION' value='Detect' />"
	}else{
		print "</td><td>&nbsp;</td></tr><tr><td class='base' colspan='2'><b>Use setup on IPCop Console first to configure a (dummy) BLUE interface.</b>"
	}
	print "&nbsp;</td><td width='5%' align='right'>&nbsp;</td></tr>";
}
print <<END
</table><hr />
END
;
&Header::closebox();

if ( $wlan_card_status eq '' ){
	print "</form>";
	&Header::closebigbox();
	&Header::closepage();
	exit 0;
}

#
# WLAN settings
#
&Header::openbox('100%', 'left', "WLAN Settings");
print <<END
<table width='100%'>
<tr><td width='25%' class='base'>Access Point:&nbsp;</td><td class='base' colspan='3'><input type='checkbox' name='APMODE' $checked_apmode $disabled_apmode /></td></tr>
<tr><td width='25%' class='base'>SSID:&nbsp;</td><td class='base' colspan='3'><input type='text' name='SSID' size='40' value='$wlanapsettings{'SSID'}' /></td></tr>
<tr><td width='25%' class='base'>Autostart after Boot:&nbsp;</td><td class='base' colspan='3'><input type='checkbox' name='BOOTSTART' $checked_bootstart /></td></tr>
<tr><td width='25%' class='base'>Disable SSID broadcast:&nbsp;</td><td class='base' colspan='3'><input type='checkbox' name='HIDESSID' $checked_hidessid $disabled_apmode /></td></tr>
<tr><td width='25%' class='base'>Encryption:&nbsp;</td><td class='base' colspan='3'>
	<select name='ENC'>
		<option value='none' $selected{'ENC'}{'none'}>none</option>
		<option value='wep' $selected{'ENC'}{'wep'}>wep</option>
		<option value='wpa' $selected{'ENC'}{'wpa'}>wpa</option>
		<option value='wep+wpa' $selected{'ENC'}{'wep+wpa'}>wep+wpa</option>
	</select>
</td></tr>
<tr><td width='25%' class='base'>Use Antenna:&nbsp;</td><td class='base' colspan='3'>
	<select name='ANTENNA'>
		<option value='both' $selected{'ANTENNA'}{'both'}>both</option>
		<option value='1' $selected{'ANTENNA'}{'1'}>1 only</option>
		<option value='2' $selected{'ANTENNA'}{'2'}>2 only</option>
	</select>
</td></tr>
<!-- <tr><td width='25%' class='base'>Select Country:&nbsp;</td><td class='base' colspan='3'><input type='checkbox' name='CC' $checked_hidessid /></td></tr> -->
<tr><td width='25%' class='base'>Channel:&nbsp;</td><td class='base' colspan='3'>
	<select name='CHAN'>
END
;
foreach $channel (@channellist){
	print "<option $selected{'CHAN'}{$channel}>$channel</option>";
}
print <<END
</select></td></tr>
<tr><td width='25%' class='base'>Tx Power:&nbsp;</td><td class='base' colspan='3'><select name='TXPOWER'>
END
;
foreach $txpower (@txpowerlist){
	print "<option $selected{'TXPOWER'}{$txpower}>$txpower</option>&nbsp;dBm";
}
print <<END
	</select></td></tr>
</table>
<hr /><table width='100%'>
<tr>
<td width='55%' class='base' valign='top'>&nbsp;</td>
<td width='40%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
</tr>
</table>
END
;
&Header::closebox();


#
# WEP
#
&Header::openbox('100%', 'left', "WEP Configuration");
print <<END
<table width='100%'>
<tr><td width='25%' class='base'>Key 1:&nbsp;</td><td class='base' colspan='3'><input type='text' name='WEPKEY1' size='32' value='$wlanapsettings{'WEPKEY1'}' /></td></tr>
<tr><td width='25%' class='base'>Key 2:&nbsp;<img src='/blob.gif' alt='*' />&nbsp;</td><td class='base' colspan='3'><input type='text' name='WEPKEY2' size='32' value='$wlanapsettings{'WEPKEY2'}' /></td></tr>
<tr><td width='25%' class='base'>Key 3:&nbsp;<img src='/blob.gif' alt='*' />&nbsp;</td><td class='base' colspan='3'><input type='text' name='WEPKEY3' size='32' value='$wlanapsettings{'WEPKEY3'}' /></td></tr>
<tr><td width='25%' class='base'>Key 4:&nbsp;<img src='/blob.gif' alt='*' />&nbsp;</td><td class='base' colspan='3'><input type='text' name='WEPKEY4' size='32' value='$wlanapsettings{'WEPKEY4'}' /></td></tr>
<tr><td width='25%' class='base'>WEP Key to Use:&nbsp;</td><td class='base' colspan='3'>
	<select name='USEDKEY'>
		<option value='1' $selected{'USEDKEY'}{'1'}>1</option>
		<option value='2' $selected{'USEDKEY'}{'2'}>2</option>
		<option value='3' $selected{'USEDKEY'}{'3'}>3</option>
		<option value='4' $selected{'USEDKEY'}{'4'}>4</option>
	</select>
</td></tr>
</table>
<hr /><table width='100%'>
<tr><td width='25%' class='base'>Passphrase:&nbsp;</td><td class='base' width='50%'><input type='text' name='WEPPWD' size='13' value='$cgiparams{'WEPPWD'}' /></td><td width='25%'><input type='submit' name='ACTION' value='Calc WEP Key' /></td></tr>
<tr><td width='25%' class='base'>WEP Key:&nbsp;</td><td class='base'><input type='text' name='WEPKEYCALC' size='32' value='$cgiparams{'WEPKEYCALC'}' /></td><td width='25%'><input type='submit' name='ACTION' value='Random WEP Key' /></td></tr>
</table>
<hr /><table width='100%'>
<tr>
<td width='55%' class='base' valign='top'><img src='/blob.gif' alt='*' />&nbsp;$Lang::tr{'this field may be blank'}</td>
<td width='40%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
</tr>
</table>
END
;
&Header::closebox();


#
# WPA
#
&Header::openbox('100%', 'left', "WPA Configuration");
print <<END
<table width='100%'>
<tr><td width='25%' class='base'>Passphrase:&nbsp;</td><td class='base' colspan='3'><input type='text' name='PWD' size='63' value='$wlanapsettings{'PWD'}' /></td></tr>
<tr><td width='25%' class='base'>WPA Version:&nbsp;</td><td class='base' colspan='3'>
	<select name='WPA'>
		<option value='1' $selected{'WPA'}{'1'}>1</option>
		<option value='2' $selected{'WPA'}{'2'}>2</option>
		<option value='3' $selected{'WPA'}{'3'}>1+2</option>
	</select>
</td></tr>
<tr><td width='25%' class='base'>Loglevel (hostapd):&nbsp;</td><td class='base' width='25%'>
	<select name='SYSLOGLEVEL'>
		<option value='0' $selected{'SYSLOGLEVEL'}{'0'}>0 (verbose)</option>
		<option value='1' $selected{'SYSLOGLEVEL'}{'1'}>1 (debugging)</option>
		<option value='2' $selected{'SYSLOGLEVEL'}{'2'}>2 (informations)</option>
		<option value='3' $selected{'SYSLOGLEVEL'}{'3'}>3 (notifications)</option>
		<option value='4' $selected{'SYSLOGLEVEL'}{'4'}>4 (warnings)</option>
	</select>
</td>
<td width='25%' class='base'>Debuglevel (hostapd):&nbsp;</td><td class='base' width='25%'>
	<select name='DEBUG'>
		<option value='0' $selected{'DEBUG'}{'0'}>0 (no debugging)</option>
		<option value='1' $selected{'DEBUG'}{'1'}>1 (minimal)</option>
		<option value='2' $selected{'DEBUG'}{'2'}>2 (verbose)</option>
		<option value='3' $selected{'DEBUG'}{'3'}>3 (msg dumps)</option>
		<option value='4' $selected{'DEBUG'}{'4'}>4 (excessive)</option>
	</select>
</td></tr>
</table>
<hr /><table width='100%'>
<tr>
<td width='55%' class='base' valign='top'>&nbsp;</td>
<td width='40%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
</tr>
</table>
END
;
&Header::closebox();

print "</form>";
&Header::closebigbox();
&Header::closepage();

sub WEPKeyRandom{
	my $length = 26;      # 10 is also allowed
	my $string = "0123456789ABCDEF";
	my @chars = split(//,$string);
	my $n = @chars;
	my $index;
	my $key = '';
	for ( $i = 0; $i < $length; $i++){
		$index = int(rand $n);
		$key = $key . $chars[$index];
	}
	return $key;
}

sub WEPKeyCalc{
	require Digest::MD5;
	return substr Digest::MD5::md5_hex( substr( shift() x 64, 0, 64 ) ), 0, 26;
}

sub WriteConfig{
	&General::writehash("/var/ipfire/wlanap/settings", \%wlanapsettings);
}

sub WriteConfig_hostapd{
	$wlanapsettings{'DRIVER_HOSTAPD'} = lc($wlanapsettings{'DRIVER'});

	open (CONFIGFILE, ">/var/ipfire/wlanap/hostapd.conf");
	print CONFIGFILE <<END
##### hostapd configuration file ##############################################

interface=$netsettings{'BLUE_DEV'}
# Driver interface type (hostap/wired/madwifi; default: hostap)
driver=$wlanapsettings{'DRIVER_HOSTAPD'}
logger_syslog=-1
logger_syslog_level=$wlanapsettings{'SYSLOGLEVEL'}
logger_stdout=-1
logger_stdout_level=$wlanapsettings{'SYSLOGLEVEL'}
debug=$wlanapsettings{'DEBUG'}
dump_file=/tmp/hostapd.dump
ssid=$wlanapsettings{'SSID'}
eapol_key_index_workaround=0
eap_server=0
own_ip_addr=127.0.0.1
wpa=$wlanapsettings{'WPA'}
wpa_passphrase=$wlanapsettings{'PWD'}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP TKIP
auth_algs=3
ctrl_interface=/var/run/hostapd
ctrl_interface_group=0
macaddr_acl=0
END
;
	close CONFIGFILE;
}
