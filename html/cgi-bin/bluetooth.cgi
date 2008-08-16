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

&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

my %bluetoothsettings=();
$bluetoothsettings{'PASSKEY_AGENT'} = 'on';
$bluetoothsettings{'PWD'} = '12345';
$bluetoothsettings{'RFCOMM0_BIND'} = 'off';
$bluetoothsettings{'RFCOMM0_DEVICE'} = '';
$bluetoothsettings{'RFCOMM0_CHANNEL'} = '1';
$bluetoothsettings{'RFCOMM1_BIND'} = 'off';
$bluetoothsettings{'RFCOMM1_DEVICE'} = '';
$bluetoothsettings{'RFCOMM1_CHANNEL'} = '1';

&General::readhash("/var/ipfire/bluetooth/settings", \%bluetoothsettings);

my %cgiparams=();
$cgiparams{'ACTION'} = '';
$cgiparams{'RUNNING'} = 'off';
$cgiparams{'PASSKEY_AGENT'} = 'off';
$cgiparams{'PWD'} = '';
$cgiparams{'RFCOMM0_BIND'} = 'off';
$cgiparams{'RFCOMM0_DEVICE'} = '';
$cgiparams{'RFCOMM0_CHANNEL'} = '';
$cgiparams{'RFCOMM1_BIND'} = 'off';
$cgiparams{'RFCOMM1_DEVICE'} = '';
$cgiparams{'RFCOMM1_CHANNEL'} = '';


&Header::getcgihash(\%cgiparams);

&Header::showhttpheaders();

if ( $cgiparams{'ACTION'} eq "$Lang::tr{'save'}" ){
	$bluetoothsettings{'PASSKEY_AGENT'}  = $cgiparams{'PASSKEY_AGENT'};
	$bluetoothsettings{'PWD'}  = $cgiparams{'PWD'};
	if ( (length($bluetoothsettings{'PWD'}) < 4) || (length($bluetoothsettings{'PWD'}) > 8) ){
		$errormessage .= "Invalid length in Passphrase. Must be between 4 and 8 characters.<br />";
	}
	$bluetoothsettings{'RFCOMM0_BIND'}  = $cgiparams{'RFCOMM0_BIND'};
	$bluetoothsettings{'RFCOMM1_BIND'}  = $cgiparams{'RFCOMM1_BIND'};
	$bluetoothsettings{'RFCOMM0_DEVICE'}  = $cgiparams{'RFCOMM0_DEVICE'};
	$bluetoothsettings{'RFCOMM1_DEVICE'}  = $cgiparams{'RFCOMM1_DEVICE'};
	$bluetoothsettings{'RFCOMM0_CHANNEL'}  = $cgiparams{'RFCOMM0_CHANNEL'};
	$bluetoothsettings{'RFCOMM1_CHANNEL'}  = $cgiparams{'RFCOMM1_CHANNEL'};
	
# TODO: CHECK RFCOMM DEVICES

	if ( $errormessage eq '' ){
		&WriteConfig();
		system("/usr/local/bin/addonctrl bluetooth restart >/dev/null 2>&1")
	}
}

&Header::openpage('Bluetooth', 1, '', '');
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


my $checked_passkey_agent = '';
my $checked_rfcomm0_bind = '';
my $checked_rfcomm1_bind = '';

$checked_passkey_agent = "checked='checked'" if ( $bluetoothsettings{'PASSKEY_AGENT'} eq 'on' );
$checked_rfcomm0_bind = "checked='checked'" if ( $bluetoothsettings{'RFCOMM0_BIND'} eq 'on' );
$checked_rfcomm1_bind = "checked='checked'" if ( $bluetoothsettings{'RFCOMM1_BIND'} eq 'on' );

#
# Devices box
#
&Header::openbox('100%', 'left', "Bluetooth devices in range");
print <<END
<table width='100%'>
END
;
my $bluetooth_scan = `hcitool scan | grep -v "Scanning ..." | sed 's|:|-|g'`;

print "<table width='80%'><td bgcolor='${Header::colourblue}'><font color='white'><pre>$bluetooth_scan</pre></font></td></table>";

&Header::closebox();

#
# Bluetooth settings
#
&Header::openbox('100%', 'left', "Bluetooth Settings");
print <<END
<table width='100%'>
<tr><td width='25%' class='base'>Passkey-Agent:&nbsp;</td><td class='base'><input type='checkbox' name='PASSKEY_AGENT' $checked_passkey_agent /></td>
    <td width='25%' class='base'>Password:&nbsp;</td><td class='base'><input type='text' name='PWD' size='8' value='$bluetoothsettings{'PWD'}' /></td></tr>
<tr><td width='25%' class='base'>Bind rfcomm0:&nbsp;</td><td class='base' colspan='3'><input type='checkbox' name='RFCOMM0_BIND' $checked_rfcomm0_bind />
    Device:&nbsp; <input type='text' name='RFCOMM0_DEVICE' size='17' value='$bluetoothsettings{'RFCOMM0_DEVICE'}' />
    Channel:&nbsp; <input type='text' name='RFCOMM0_CHANNEL' size='1' value='$bluetoothsettings{'RFCOMM0_CHANNEL'}' /></td></tr>
<tr><td width='25%' class='base'>Bind rfcomm1:&nbsp;</td><td class='base' colspan='3'><input type='checkbox' name='RFCOMM1_BIND' $checked_rfcomm1_bind />
    Device:&nbsp; <input type='text' name='RFCOMM1_DEVICE' size='17' value='$bluetoothsettings{'RFCOMM1_DEVICE'}' />
    Channel:&nbsp; <input type='text' name='RFCOMM1_CHANNEL' size='1' value='$bluetoothsettings{'RFCOMM1_CHANNEL'}' /></td></tr>

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


sub WriteConfig{
	&General::writehash("/var/ipfire/bluetooth/settings", \%bluetoothsettings);
}

