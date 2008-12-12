#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2008  Michael Tremer & Christian Schmidt                      #
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
my $status_started = "<td align='center' width='75%' bgcolor='${Header::colourgreen}'><font color='white'><b>$Lang::tr{'running'}</b></font></td></tr>";
my $status_stopped = "<td align='center' width='75%' bgcolor='${Header::colourred}'><font color='white'><b>$Lang::tr{'stopped'}</b></font></td></tr>";

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
my $txpower = '';

&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);
&General::readhash("/var/ipfire/ethernet/settings", \%netsettings);

$wlanapsettings{'APMODE'} = 'on';
$wlanapsettings{'MACMODE'} = '0';
$wlanapsettings{'INTERFACE'} = '';
$wlanapsettings{'SSID'} = 'IPFire';
$wlanapsettings{'HIDESSID'} = 'off';
$wlanapsettings{'ENC'} = 'wpa2';               # none / wpa1 /wpa2
$wlanapsettings{'TXPOWER'} = 'auto';
$wlanapsettings{'CHANNEL'} = '05';
$wlanapsettings{'PWD'} = 'IPFire-2.x';
$wlanapsettings{'SYSLOGLEVEL'} = '0';
$wlanapsettings{'DEBUG'} = '4';
$wlanapsettings{'DRIVER'} = 'MADWIFI';

&General::readhash("/var/ipfire/wlanap/settings", \%wlanapsettings);

my %cgiparams=();
$cgiparams{'ACTION'} = '';
$cgiparams{'APMODE'} = 'on';
$cgiparams{'MACMODE'} = '0';
$cgiparams{'SSID'} = 'IPFire';
$cgiparams{'HIDESSID'} = 'off';
$cgiparams{'ENC'} = 'wpa2';               # none / wep / wpa / wep+wpa
$cgiparams{'TXPOWER'} = 'auto';
$cgiparams{'CHANNEL'} = '05';
$cgiparams{'PWD'} = 'IPFire-2.x';
$cgiparams{'SYSLOGLEVEL'} = '0';
$cgiparams{'DEBUG'} = '4';
&Header::getcgihash(\%cgiparams);


&Header::showhttpheaders();

if ( $cgiparams{'ACTION'} eq "$Lang::tr{'save'}" ){
	$wlanapsettings{'SSID'}		= $cgiparams{'SSID'};
	$wlanapsettings{'MACMODE'}	= $cgiparams{'MACMODE'};
	$wlanapsettings{'MACS'}		= $cgiparams{'MACS'};
	$wlanapsettings{'HIDESSID'}	= $cgiparams{'HIDESSID'};
	$wlanapsettings{'ENC'}		= $cgiparams{'ENC'};
	$wlanapsettings{'CHANNEL'}	= $cgiparams{'CHANNEL'};
	$wlanapsettings{'TXPOWER'}	= $cgiparams{'TXPOWER'};

	$wlanapsettings{'PWD'}		= $cgiparams{'PWD'};
	$wlanapsettings{'SYSLOGLEVEL'}	= $cgiparams{'SYSLOGLEVEL'};
	$wlanapsettings{'DEBUG'}	= $cgiparams{'DEBUG'};

	# verify WPA Passphrase, must be 8 .. 63 characters
	if ( (length($wlanapsettings{'PWD'}) < 8) || (length($wlanapsettings{'PWD'}) > 63) ){
		$errormessage .= "Invalid length in WPA Passphrase. Must be between 8 and 63 characters.<br />";
	}

	if ( $errormessage eq '' ){
		&General::writehash("/var/ipfire/wlanap/settings", \%wlanapsettings);
		&WriteConfig_hostapd();

		system("/usr/local/bin/wlanapctrl restart >/dev/null 2>&1");
	}
}elsif ( $cgiparams{'ACTION'} eq "$Lang::tr{'interface'}" ){
	$wlanapsettings{'INTERFACE'}      = $cgiparams{'INTERFACE'};
	&General::writehash("/var/ipfire/wlanap/settings", \%wlanapsettings);
}elsif ( $cgiparams{'ACTION'} eq 'Start' ){
	system("/usr/local/bin/wlanapctrl start >/dev/null 2>&1");
}elsif ( $cgiparams{'ACTION'} eq 'Stop' ){
	system("/usr/local/bin/wlanapctrl stop >/dev/null 2>&1");
}

&Header::openpage('WLAN', 1, '', '');
&Header::openbigbox('100%', 'left', '', $errormessage);
print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>";

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
my $message = "";

$selected{'INTERFACE'}{'green0'} = '';
$selected{'INTERFACE'}{'blue0'} = '';
$selected{'ENC'}{$wlanapsettings{'INTERFACE'}} = "selected='selected'";

if ( ($wlanapsettings{'INTERFACE'} eq '') ){
	$message = "No WLan Interface selected.";
	&Header::openbox('100%', 'center', "WLAN AP");
print <<END
$message<br />
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<select name='INTERFACE'>
	<option value='green0' $selected{'INTERFACE'}{'green0'}>green0</option>
END
;
	if ( $netsettings{'BLUE_DEV'} ne ''){
		print "<option value='blue0' $selected{'INTERFACE'}{'blue0'}>blue0</option>";
	}
print <<END
</select>
<br />
	<input type='hidden' name='ACTION' value='$Lang::tr{'interface'}' />
	<input type='image' alt='$Lang::tr{'save'}' title='$Lang::tr{'save'}' src='/images/media-floppy.png' /></form>
END
;
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit;
}else{
	my $cmd_out = `/usr/sbin/iwconfig $wlanapsettings{'INTERFACE'} 2>/dev/null`;

	if ( $cmd_out eq '' ){
		$message = "Interface is not a WLAN card.";
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

my $checked_hidessid = '';
$checked_hidessid = "checked='checked'" if ( $wlanapsettings{'HIDESSID'} eq 'on' );

$selected{'ENC'}{$wlanapsettings{'ENC'}} = "selected='selected'";
$selected{'CHANNEL'}{$wlanapsettings{'CHANNEL'}} = "selected='selected'";
$selected{'TXPOWER'}{$wlanapsettings{'TXPOWER'}} = "selected='selected'";
$selected{'MACMODE'}{$wlanapsettings{'MACMODE'}} = "selected='selected'";

my @channellist_cmd = `iwlist $wlanapsettings{'INTERFACE'} channel`;
# get available channels

my @temp;
foreach (@channellist_cmd){
$_ =~ /(.*)Channel (\d+)(.*):/;
$channel = $2;chomp $channel;
if ( $channel =~ /\d+/ ){push(@temp,$channel);}
}
my @channellist = @temp;

my @txpower_cmd = `iwlist $wlanapsettings{'INTERFACE'} txpower`;
# get available channels

my @temp;
foreach (@txpower_cmd){
$_ =~ /(\s)(\d+)(\s)dBm(\s)(.*)(\W)(\d+)(.*)/;
$txpower = $7;chomp $txpower;
if ( $txpower =~ /\d+/ ){push(@temp,$txpower."mW");}
}
my @txpower = @temp;
push(@txpower,"auto");

$selected{'SYSLOGLEVEL'}{$wlanapsettings{'SYSLOGLEVEL'}} = "selected='selected'";
$selected{'DEBUG'}{$wlanapsettings{'DEBUG'}} = "selected='selected'";

#
# Status box
#
&Header::openbox('100%', 'center', "WLAN AP");
print <<END
<table width='95%' cellspacing='0'>
<tr><td bgcolor='$color{'color20'}' colspan='2' align='left'><b>WLAN Services</b></td></tr>
END
;
if ( $wlan_card_status ne '' ){
	print "<tr><td class='base'>WLAN card ($wlanapsettings{'DRIVER'})</td>";
	print $wlan_card_status eq 'up' ? $status_started : $status_stopped;
	print "<tr><td class='base'>Access Point</td>";
	print $wlan_ap_status eq 'up' ? $status_started : $status_stopped;
	if ( $wlan_card_status eq 'up' ){
		print "<tr><td colspan='2' align='center'><input type='submit' name='ACTION' value='Stop' />";
		print "<input type='submit' name='ACTION' value='Restart' /></td></tr>";
	}else{
		print "<tr><td colspan='2' align='center'><input type='submit' name='ACTION' value='Start' /></td></tr>";
	}
}else{
	print "<tr><td colspan='2' class='base'><b>$message</b></td></tr>";
}
print "</table>";

if ( $wlan_card_status eq '' ){
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit 0;
}
print <<END
<br />
<table width='95%' cellspacing='0'>
<tr><td bgcolor='$color{'color20'}' colspan='4' align='left'><b>WLAN Settings</b>
<tr><td width='25%' class='base'>SSID:&nbsp;</td><td class='base' colspan='3'><input type='text' name='SSID' size='40' value='$wlanapsettings{'SSID'}' /></td></tr>
<tr><td width='25%' class='base'>Disable SSID broadcast:&nbsp;</td><td class='base' colspan='3'><input type='checkbox' name='HIDESSID' $checked_hidessid /></td></tr>
<tr><td width='25%' class='base'>Encryption:&nbsp;</td><td class='base' colspan='3'>
	<select name='ENC'>
		<option value='none' $selected{'ENC'}{'none'}>none</option>
		<option value='wpa1' $selected{'ENC'}{'wpa1'}>wpa1</option>
		<option value='wpa2' $selected{'ENC'}{'wpa2'}>wpa2</option>
	</select>
</td></tr>
<tr><td width='25%' class='base'>Channel:&nbsp;</td><td class='base' colspan='3'>
	<select name='CHANNEL'>
END
;
foreach $channel (@channellist){
	print "<option $selected{'CHANNEL'}{$channel}>$channel</option>";
}

print <<END
</select></td></tr>
<tr><td width='25%' class='base'>Tx Power:&nbsp;</td><td class='base' colspan='3'><select name='TXPOWER'>
END
;
foreach $txpower (@txpower){
	print "<option $selected{'TXPOWER'}{$txpower}>$txpower</option>&nbsp;dBm";
}
print <<END
	</select></td></tr>
<tr><td width='25%' class='base'>Passphrase:&nbsp;</td><td class='base' colspan='3'><input type='text' name='PWD' size='63' value='$wlanapsettings{'PWD'}' /></td></tr>
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
		<option value='0' $selected{'DEBUG'}{'0'}>0 (verbose)</option>
		<option value='1' $selected{'DEBUG'}{'1'}>1 (debugging)</option>
		<option value='2' $selected{'DEBUG'}{'2'}>2 (informations)</option>
		<option value='3' $selected{'DEBUG'}{'3'}>3 (notifications)</option>
		<option value='4' $selected{'DEBUG'}{'4'}>4 (warnings)</option>
	</select>
</td></tr>
</table>
END
;
if ( $wlanapsettings{'INTERFACE'} =~ /green0/ ){
	print <<END
<br />
<table width='95%' cellspacing='0'>
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
<table width='10%' cellspacing='0'>
<tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<input type='hidden' name='ACTION' value=$Lang::tr{'save'} />
	<input type='image' alt='$Lang::tr{'save'}' title='$Lang::tr{'save'}' src='/images/media-floppy.png' /></form></td>
</tr>
</table>
END
;

if ( $wlanapsettings{'DRIVER'} eq 'MADWIFI' ){
	 $status =  `wlanconfig $wlanapsettings{'INTERFACE'} list`;
}
print <<END
<br />
<table width='95%' cellspacing='0'>
<tr><td bgcolor='$color{'color20'}' colspan='2' align='left'><b>WLAN Status</b></td></tr>
<tr><td><pre>@channellist_cmd</pre></td><td><pre>@txpower_cmd</pre></td></tr>
<tr><td colspan='2'><pre>$status</pre></td></tr>
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
######################### basic hostapd configuration ##########################
#
interface=$wlanapsettings{'INTERFACE'}
driver=$wlanapsettings{'DRIVER_HOSTAPD'}
logger_syslog=-1
logger_syslog_level=$wlanapsettings{'SYSLOGLEVEL'}
logger_stdout=-1
logger_stdout_level=$wlanapsettings{'DEBUG'}
dump_file=/tmp/hostapd.dump
auth_algs=3
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

 if ( $wlanapsettings{'ENC'} eq 'wpa1'){
	print CONFIGFILE <<END
######################### wpa hostapd configuration ############################
#
wpa=1
wpa_passphrase=$wlanapsettings{'PWD'}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP TKIP
END
;
 }elsif ( $wlanapsettings{'ENC'} eq 'wpa2'){
	print CONFIGFILE <<END
######################### wpa hostapd configuration ############################
#
wpa=2
wpa_passphrase=$wlanapsettings{'PWD'}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP TKIP
END
;
 }
	close CONFIGFILE;

$wlanapsettings{'MACS'} =~ s/\r//gi;
chomp($wlanapsettings{'MACS'});
	open (MACFILE, ">/var/ipfire/wlanap/macfile");
	print MACFILE <<END
$wlanapsettings{'MACS'}
END
;
	close MACFILE;
}
