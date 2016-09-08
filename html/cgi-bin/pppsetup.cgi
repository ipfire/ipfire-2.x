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

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

our %pppsettings=();
my %temppppsettings=();
our %modemsettings=();
our %isdnsettings=();
our %netsettings=();
my %selected=();
my %checked=();
my @profilenames=();
my $errormessage = '';
my $maxprofiles = 5;
my $kernel=`/bin/uname -r | /usr/bin/tr -d '\012'`;

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

&Header::showhttpheaders();

$pppsettings{'ACTION'} = '';
&initprofile();
&Header::getcgihash(\%pppsettings);

if ($pppsettings{'ACTION'} ne '' &&
        ( -e "${General::swroot}/red/active")){
        $errormessage = $Lang::tr{'unable to alter profiles while red is active'};
        # read in the current vars
        %pppsettings = ();
        $pppsettings{'VALID'} = '';
        &General::readhash("${General::swroot}/ppp/settings", \%pppsettings);}
elsif ($pppsettings{'ACTION'} eq $Lang::tr{'refresh'})
{
        unless ($pppsettings{'TYPE'} =~ /^(modem|serial|isdn|pppoe|pptp|vdsl|pppoeatm|pptpatm)$/) {
                $errormessage = $Lang::tr{'invalid input'};
                goto ERROR; }
        my $type = $pppsettings{'TYPE'};
        &General::readhash("${General::swroot}/ppp/settings", \%pppsettings);
        $pppsettings{'TYPE'} = $type;
}
elsif ($pppsettings{'ACTION'} eq $Lang::tr{'save'})
{
        if ($pppsettings{'TYPE'} =~ /^(modem|serial|isdn)$/ && $pppsettings{'COMPORT'} !~ /^(ttyS0|ttyS1|ttyS2|ttyS3|ttyS4|ttyACM[0-9]|ttyUSB[0-9]|rfcomm0|rfcomm1|isdn1|isdn2)$/) {
                $errormessage = $Lang::tr{'invalid input'};
                goto ERROR; }
        if ($pppsettings{'TYPE'} =~ /^(modem|serial|isdn)$/ && $pppsettings{'MONPORT'} !~ /^(|ttyACM[0-9]|ttyUSB[0-9]|rfcomm0|rfcomm1)$/) {
                $errormessage = $Lang::tr{'invalid input'};
                goto ERROR; }
        if ($pppsettings{'TYPE'} =~ /^(modem|serial)$/ && $pppsettings{'DTERATE'} !~ /^(9600|19200|38400|57600|115200|230400|460800|921600)$/) {
                $errormessage = $Lang::tr{'invalid input'};
                goto ERROR; }
        if ($pppsettings{'TYPE'} eq 'modem' && $pppsettings{'DIALMODE'} !~ /^(T|P)$/) {
                $errormessage = $Lang::tr{'invalid input'};
                goto ERROR; }
        if ($pppsettings{'AUTH'} !~ /^(pap-or-chap|pap|chap|standard-login-script|demon-login-script|other-login-script)$/) {
                $errormessage = $Lang::tr{'invalid input'};
                goto ERROR;
        }

        if ($pppsettings{'PROFILENAME'} eq '') {
                $errormessage = $Lang::tr{'profile name not given'};
                $pppsettings{'PROFILENAME'} = '';
                goto ERROR; }
        if ($pppsettings{'TYPE'} =~ /^(modem|isdn)$/) {
                if ($pppsettings{'TELEPHONE'} eq '') {
                        $errormessage = $Lang::tr{'telephone not set'};
                        goto ERROR; }
                if (!($pppsettings{'TELEPHONE'} =~ /^[\d\*\#\,]+$/)) {
                        $errormessage = $Lang::tr{'bad characters in the telephone number field'};
                        goto ERROR; }
        }
        unless (($pppsettings{'PROTOCOL'} eq 'RFC1483' && $pppsettings{'METHOD'} =~ /^(STATIC|DHCP)$/)) {
                if ($pppsettings{'USERNAME'} eq '') {
                        $errormessage = $Lang::tr{'username not set'};
                        goto ERROR; }
		}

        if ($pppsettings{'TIMEOUT'} eq '') {
                $errormessage = $Lang::tr{'idle timeout not set'};
                goto ERROR; }
        if (!($pppsettings{'TIMEOUT'} =~ /^\d+$/)) {
                $errormessage = $Lang::tr{'only digits allowed in the idle timeout'};
                goto ERROR; }

        if ($pppsettings{'LOGINSCRIPT'} =~ /[.\/ ]/ ) {
                $errormessage = $Lang::tr{'bad characters in script field'};
                goto ERROR; }

        if ($pppsettings{'DNS1'})
        {
                if (!(&General::validip($pppsettings{'DNS1'}))) {
                        $errormessage = $Lang::tr{'invalid primary dns'};
                        goto ERROR;  }
        }
        if ($pppsettings{'DNS2'})
        {
                if (!(&General::validip($pppsettings{'DNS2'}))) {
                        $errormessage = $Lang::tr{'invalid secondary dns'};
                        goto ERROR; }
        }

        if ($pppsettings{'MAXRETRIES'} eq '') {
                $errormessage = $Lang::tr{'max retries not set'};
                goto ERROR; }
        if (!($pppsettings{'MAXRETRIES'} =~ /^\d+$/)) {
                $errormessage = $Lang::tr{'only digits allowed in max retries field'};
                goto ERROR; }

        if (!($pppsettings{'HOLDOFF'} =~ /^\d+$/)) {
                $errormessage = $Lang::tr{'only digits allowed in holdoff field'};
                goto ERROR; }

        if ($pppsettings{'TYPE'} =~ /^(pppoeatm|pptpatm)$/) {
                if ( ($pppsettings{'VPI'} eq '') || ($pppsettings{'VCI'} eq '') ) {
                        $errormessage = $Lang::tr{'invalid vpi vpci'};
                        goto ERROR; }
                if ( (!($pppsettings{'VPI'} =~ /^\d+$/)) || (!($pppsettings{'VCI'} =~ /^\d+$/)) ) {
                        $errormessage = $Lang::tr{'invalid vpi vpci'};
                        goto ERROR; }
                if (($pppsettings{'VPI'} eq '0') && ($pppsettings{'VCI'} eq '0')) {
                        $errormessage = $Lang::tr{'invalid vpi vpci'};
                        goto ERROR; }
                if ($pppsettings{'ATM_DEV'} eq '') {
                        $errormessage = $Lang::tr{'invalid input'};
                        goto ERROR; }
                if ( $pppsettings{'PROTOCOL'} eq '' ) {
                        $errormessage = $Lang::tr{'invalid input'};
                        goto ERROR; }
        }

        if ( ($pppsettings{'PROTOCOL'} eq 'RFC1483') && ($pppsettings{'METHOD'} eq '') && \
                ($pppsettings{'TYPE'} !~ /^(alcatelusb|fritzdsl)$/)) {
                        $errormessage = $Lang::tr{'invalid input'};
                        goto ERROR; }

        if (($pppsettings{'PROTOCOL'} eq 'RFC1483' && $pppsettings{'METHOD'} eq 'DHCP')) {
                if ($pppsettings{'DHCP_HOSTNAME'} ne '') {
                        if (! &General::validfqdn($pppsettings{'DHCP_HOSTNAME'})) {
                                $errormessage = $errormessage.' '.$Lang::tr{'hostname'}.': '.$Lang::tr{'invalid hostname'}; }
                }
        }

        if (($pppsettings{'PROTOCOL'} eq 'RFC1483' && $pppsettings{'METHOD'} eq 'STATIC')) {
                $errormessage = '';
                if (! &General::validip($pppsettings{'IP'})) {
                        $errormessage = $Lang::tr{'static ip'}.' '.$Lang::tr{'invalid ip'}; }
                if (! &General::validip($pppsettings{'GATEWAY'})) {
                        $errormessage = $errormessage.' '.$Lang::tr{'gateway ip'}.' '.$Lang::tr{'invalid ip'}; }
                if (! &General::validmask($pppsettings{'NETMASK'})) {
                        $errormessage = $errormessage.' '.$Lang::tr{'netmask'}.' '.$Lang::tr{'invalid netmask'}; }
                if ($pppsettings{'BROADCAST'} ne '') {
                        if (! &General::validip($pppsettings{'BROADCAST'})) {
                                 $errormessage = $errormessage.' '.$Lang::tr{'broadcast'}.' '.$Lang::tr{'invalid broadcast ip'}; }
                }
                if( $pppsettings{'DNS'} eq 'Automatic') {
                        $errormessage = $Lang::tr{'invalid input'}; }
                if ($errormessage ne '') {goto ERROR; }
        }

        if( $pppsettings{'PROTOCOL'} eq 'RFC1483' && $pppsettings{'METHOD'} ne 'PPPOE'  && \
                $pppsettings{'RECONNECTION'} eq 'dialondemand' ) {
                $errormessage = $Lang::tr{'invalid input'};
                goto ERROR; }

        if( $pppsettings{'RECONNECTION'} eq 'dialondemand' && `/bin/cat ${General::swroot}/ddns/config` =~ /,on$/m ) {
                $errormessage = $Lang::tr{'dod not compatible with ddns'};
                goto ERROR; }

#       if( $pppsettings{'PROTOCOL'} eq 'RFC1483') {
#               $pppsettings{'ENCAP'} = $pppsettings{'ENCAP_RFC1483'}; }
#       if( $pppsettings{'PROTOCOL'} eq 'RFC2364') {
#               $pppsettings{'ENCAP'} = $pppsettings{'ENCAP_RFC2364'}; }
        delete $pppsettings{'ENCAP_RFC1483'};
        delete $pppsettings{'ENCAP_RFC2364'};

        if ((!($pppsettings{'INET_VLAN'} =~ /^\d+$/)) ||
		($pppsettings{'INET_VLAN'} eq '') ||
		($pppsettings{'INET_VLAN'} > 4095) ) {
			$errormessage = 'INET_VLAN - '.$Lang::tr{'invalid input'}; }

        if ((!($pppsettings{'IPTV_VLAN'} =~ /^\d+$/)) ||
		($pppsettings{'IPTV_VLAN'} eq '') ||
		($pppsettings{'IPTV_VLAN'} > 4095) ) {
			$errormessage = 'IPTV_VLAN - '.$Lang::tr{'invalid input'}; }

ERROR:
        if ($errormessage) {
                $pppsettings{'VALID'} = 'no'; }
        else {
                $pppsettings{'VALID'} = 'yes'; }

        # write cgi vars to the file.
        &General::writehash("${General::swroot}/ppp/settings-$pppsettings{'PROFILE'}",
                \%pppsettings);

        # make link and write secret file.
        &updatesettings();
        &writesecrets();

        &General::log("$Lang::tr{'profile saved'} $pppsettings{'PROFILENAME'}");
}
if ($pppsettings{'ACTION'} eq $Lang::tr{'select'})
{
        my $profile = $pppsettings{'PROFILE'};
        %temppppsettings = ();
        $temppppsettings{'PROFILE'} = '';
        &General::readhash("${General::swroot}/ppp/settings-$pppsettings{'PROFILE'}",
                \%temppppsettings);

        # make link.
        &updatesettings();

        # read in the new params "early" so we can write secrets.
        %pppsettings = ();
        &General::readhash("${General::swroot}/ppp/settings", \%pppsettings);
        $pppsettings{'PROFILE'} = $profile;
        &General::writehash("${General::swroot}/ppp/settings-$pppsettings{'PROFILE'}",
                \%pppsettings);

        &writesecrets();

        &General::log("$Lang::tr{'profile made current'} $pppsettings{'PROFILENAME'}");
}
elsif ($pppsettings{'ACTION'} eq $Lang::tr{'delete'})
{
        &General::log("$Lang::tr{'profile deleted'} $pppsettings{'PROFILENAME'}");

        my $profile = $pppsettings{'PROFILE'};
        truncate ("${General::swroot}/ppp/settings-$pppsettings{'PROFILE'}", 0);

        %temppppsettings = ();
        $temppppsettings{'PROFILE'} = '';
        &General::readhash("${General::swroot}/ppp/settings-$pppsettings{'PROFILE'}",
                \%temppppsettings);

        # make link.
        &updatesettings();

        # read in the new params "early" so we can write secrets.
        %pppsettings = ();
        &General::readhash("${General::swroot}/ppp/settings", \%pppsettings);
        $pppsettings{'PROFILE'} = $profile;
        &initprofile;
        &General::writehash("${General::swroot}/ppp/settings-$pppsettings{'PROFILE'}",
                \%pppsettings);
}
elsif ($pppsettings{'ACTION'} eq $Lang::tr{'refresh'})
{
}
else
{
        # read in the current vars
        %pppsettings = ();
        $pppsettings{'VALID'} = '';
        &General::readhash("${General::swroot}/ppp/settings", \%pppsettings);
}

# read in the profile names into @profilenames.
my $c=0;
for ($c = 1; $c <= $maxprofiles; $c++)
{
        %temppppsettings = ();
        $temppppsettings{'PROFILENAME'} = $Lang::tr{'empty profile'};
        &General::readhash("${General::swroot}/ppp/settings-$c", \%temppppsettings);
        $profilenames[$c] = $temppppsettings{'PROFILENAME'};
}

if ($pppsettings{'VALID'} eq '')
{
        if ($pppsettings{'PROFILE'} eq '') {
                $pppsettings{'PROFILE'} = '1';
                &initprofile();
        }
}
for ($c = 1; $c <= $maxprofiles; $c++) {
        $selected{'PROFILE'}{$c} = ''; }
$selected{'PROFILE'}{$pppsettings{'PROFILE'}} = "selected='selected'";
for ($c = 1; $c <= $maxprofiles; $c++) {
        $selected{'BACKUPPROFILE'}{$c} = ''; }
$selected{'BACKUPPROFILE'}{$pppsettings{'BACKUPPROFILE'}} = "selected='selected'";

$selected{'TYPE'}{'modem'} = '';
$selected{'TYPE'}{'serial'} = '';
$selected{'TYPE'}{'pppoe'} = '';
$selected{'TYPE'}{'pptp'} = '';
$selected{'TYPE'}{'vdsl'} = '';
$selected{'TYPE'}{'pppoeatm'} = '';
$selected{'TYPE'}{'pptpatm'} = '';
$selected{'TYPE'}{$pppsettings{'TYPE'}} = "selected='selected'";
$checked{'DEBUG'}{'off'} = '';
$checked{'DEBUG'}{'on'} = '';
$checked{'DEBUG'}{$pppsettings{'DEBUG'}} = "checked='checked'";

$selected{'COMPORT'}{'ttyS0'} = '';
$selected{'COMPORT'}{'ttyS1'} = '';
$selected{'COMPORT'}{'ttyS2'} = '';
$selected{'COMPORT'}{'ttyS3'} = '';
$selected{'COMPORT'}{'ttyS4'} = '';
$selected{'COMPORT'}{'ttyACM0'} = '';
$selected{'COMPORT'}{'ttyACM1'} = '';
$selected{'COMPORT'}{'ttyACM2'} = '';
$selected{'COMPORT'}{'ttyACM3'} = '';
$selected{'COMPORT'}{'ttyACM4'} = '';
$selected{'COMPORT'}{'ttyACM5'} = '';
$selected{'COMPORT'}{'ttyACM6'} = '';
$selected{'COMPORT'}{'ttyACM7'} = '';
$selected{'COMPORT'}{'ttyACM8'} = '';
$selected{'COMPORT'}{'ttyACM9'} = '';
$selected{'COMPORT'}{'ttyUSB0'} = '';
$selected{'COMPORT'}{'ttyUSB1'} = '';
$selected{'COMPORT'}{'ttyUSB2'} = '';
$selected{'COMPORT'}{'ttyUSB3'} = '';
$selected{'COMPORT'}{'ttyUSB4'} = '';
$selected{'COMPORT'}{'ttyUSB5'} = '';
$selected{'COMPORT'}{'ttyUSB6'} = '';
$selected{'COMPORT'}{'ttyUSB7'} = '';
$selected{'COMPORT'}{'ttyUSB8'} = '';
$selected{'COMPORT'}{'ttyUSB9'} = '';
$selected{'COMPORT'}{'rfcomm0'} = '';
$selected{'COMPORT'}{'rfcomm1'} = '';
$selected{'COMPORT'}{$pppsettings{'COMPORT'}} = "selected='selected'";

$selected{'MONPORT'}{''} = '';
$selected{'MONPORT'}{'ttyACM0'} = '';
$selected{'MONPORT'}{'ttyACM1'} = '';
$selected{'MONPORT'}{'ttyACM2'} = '';
$selected{'MONPORT'}{'ttyACM3'} = '';
$selected{'MONPORT'}{'ttyACM4'} = '';
$selected{'MONPORT'}{'ttyACM5'} = '';
$selected{'MONPORT'}{'ttyACM6'} = '';
$selected{'MONPORT'}{'ttyACM7'} = '';
$selected{'MONPORT'}{'ttyACM8'} = '';
$selected{'MONPORT'}{'ttyACM9'} = '';
$selected{'MONPORT'}{'ttyUSB0'} = '';
$selected{'MONPORT'}{'ttyUSB1'} = '';
$selected{'MONPORT'}{'ttyUSB2'} = '';
$selected{'MONPORT'}{'ttyUSB3'} = '';
$selected{'MONPORT'}{'ttyUSB4'} = '';
$selected{'MONPORT'}{'ttyUSB5'} = '';
$selected{'MONPORT'}{'ttyUSB6'} = '';
$selected{'MONPORT'}{'ttyUSB7'} = '';
$selected{'MONPORT'}{'ttyUSB8'} = '';
$selected{'MONPORT'}{'ttyUSB9'} = '';
$selected{'MONPORT'}{'rfcomm0'} = '';
$selected{'MONPORT'}{'rfcomm1'} = '';
$selected{'MONPORT'}{$pppsettings{'MONPORT'}} = "selected='selected'";

$selected{'DTERATE'}{'9600'} = '';
$selected{'DTERATE'}{'19200'} = '';
$selected{'DTERATE'}{'38400'} = '';
$selected{'DTERATE'}{'57600'} = '';
$selected{'DTERATE'}{'115200'} = '';
$selected{'DTERATE'}{'230400'} = '';
$selected{'DTERATE'}{'460800'} = '';
$selected{'DTERATE'}{'921600'} = '';
$selected{'DTERATE'}{$pppsettings{'DTERATE'}} = "selected='selected'";

$checked{'SPEAKER'}{'off'} = '';
$checked{'SPEAKER'}{'on'} = '';
$checked{'SPEAKER'}{$pppsettings{'SPEAKER'}} = "checked='checked'";

$selected{'DIALMODE'}{'T'} = '';
$selected{'DIALMODE'}{'P'} = '';
$selected{'DIALMODE'}{$pppsettings{'DIALMODE'}} = "selected='selected'";

$checked{'RECONNECTION'}{'persistent'} = '';
$checked{'RECONNECTION'}{'dialondemand'} = '';
$checked{'RECONNECTION'}{$pppsettings{'RECONNECTION'}} = "checked='checked'";

$checked{'DIALONDEMANDDNS'}{'off'} = '';
$checked{'DIALONDEMANDDNS'}{'on'} = '';
$checked{'DIALONDEMANDDNS'}{$pppsettings{'DIALONDEMANDDNS'}} = "checked='checked'";

$checked{'AUTOCONNECT'}{'off'} = '';
$checked{'AUTOCONNECT'}{'on'} = '';
$checked{'AUTOCONNECT'}{$pppsettings{'AUTOCONNECT'}} = "checked='checked'";

$checked{'SENDCR'}{'off'} = '';
$checked{'SENDCR'}{'on'} = '';
$checked{'SENDCR'}{$pppsettings{'SENDCR'}} = "checked='checked'";
$checked{'USEDOV'}{'off'} = '';
$checked{'USEDOV'}{'on'} = '';
$checked{'USEDOV'}{$pppsettings{'USEDOV'}} = "checked='checked'";

$checked{'MODEM'}{'PCIST'} = '';
$checked{'MODEM'}{'USB'} = '';
$checked{'MODEM'}{$pppsettings{'MODEM'}} = "checked='checked'";

$selected{'LINE'}{'WO'} = '';
$selected{'LINE'}{'ES'} = '';
$selected{'LINE'}{'ES03'} = '';
$selected{'LINE'}{'FR'} = '';
$selected{'LINE'}{'FR04'} = '';
$selected{'LINE'}{'FR10'} = '';
$selected{'LINE'}{'IT'} = '';
$selected{'LINE'}{$pppsettings{'LINE'}} = "selected='selected'";

$checked{'MODULATION'}{'GDMT'} = '';
$checked{'MODULATION'}{'ANSI'} = '';
$checked{'MODULATION'}{'GLITE'} = '';
$checked{'MODULATION'}{'AUTO'} = '';
$checked{'MODULATION'}{$pppsettings{'MODULATION'}} = "checked='checked'";

$checked{'PROTOCOL'}{'RFC1483'} = '';
$checked{'PROTOCOL'}{'RFC2364'} = '';
$checked{'PROTOCOL'}{$pppsettings{'PROTOCOL'}} = "checked='checked'";

$selected{'ENCAP'}{'0'} = '';
$selected{'ENCAP'}{'1'} = '';
#$selected{'ENCAP'}{'2'} = '';
#$selected{'ENCAP'}{'3'} = '';
#$selected{'ENCAP'}{'4'} = '';
$selected{'ENCAP'}{$pppsettings{'ENCAP'}} = "selected='selected'";

$checked{'METHOD'}{'STATIC'} = '';
$checked{'METHOD'}{'PPPOE'} = '';
$checked{'METHOD'}{'DHCP'} = '';
$checked{'METHOD'}{$pppsettings{'METHOD'}} = "checked='checked'";

$selected{'AUTH'}{'pap-or-chap'} = '';
$selected{'AUTH'}{'pap'} = '';
$selected{'AUTH'}{'chap'} = '';
$selected{'AUTH'}{'standard-login-script'} = '';
$selected{'AUTH'}{'demon-login-script'} = '';
$selected{'AUTH'}{'other-login-script'} = '';
$selected{'AUTH'}{$pppsettings{'AUTH'}} = "selected='selected'";

$checked{'DNS'}{'Automatic'} = '';
$checked{'DNS'}{'Manual'} = '';
$checked{'DNS'}{$pppsettings{'DNS'}} = "checked='checked'";

$checked{'IPTV'}{'enable'} = '';
$checked{'IPTV'}{'disable'} = '';
$checked{'IPTV'}{$pppsettings{'IPTV'}} = "checked='checked'";

if ($pppsettings{'INET_VLAN'} eq '') { $pppsettings{'INET_VLAN'}='7'; }
if ($pppsettings{'IPTV_VLAN'} eq '') { $pppsettings{'IPTV_VLAN'}='8'; }

&Header::openpage($Lang::tr{'ppp setup'}, 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

if ($netsettings{'RED_TYPE'} ne 'PPPOE') {
	$errormessage = $Lang::tr{'dialup red not ppp'};
	&Header::openbox('100%', 'center', $Lang::tr{'error messages'});
        print "<class name='base'>$errormessage\n";
        print "&nbsp;</class>\n";
        &Header::closebox();
	&Header::closebigbox();

	&Header::closepage();
	exit(1);
}

if ($errormessage) {
        &Header::openbox('100%', 'center', $Lang::tr{'error messages'});
        print "<class name='base'>$errormessage\n";
        print "&nbsp;</class>\n";
        &Header::closebox();
}


###
### Box for selecting profile
###
print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";
&Header::openbox('100%', 'center', $Lang::tr{'profile'});
print <<END
<table width='95%' cellspacing='0'>
<tr>
                <td align='left'>$Lang::tr{'profile'}</td>
        <td align='left'>
        <select name='PROFILE' style="width: 165px">
END
;
for ($c = 1; $c <= $maxprofiles; $c++)
{
        print "\t<option value='$c' $selected{'PROFILE'}{$c}>$c. $profilenames[$c]</option>\n";
}
print <<END
        </select></td>
        <td align='left'><input type='submit' name='ACTION' value='$Lang::tr{'select'}' /></td>
        <td align='left'><input type='submit' name='ACTION' value='$Lang::tr{'delete'}' /></td>
        <td align='left'><input type='submit' name='ACTION' value='$Lang::tr{'restore'}' /></td>
</tr>
</table>
<br></br>
<hr></hr>
END
;

&Header::closebox();
&Header::openbox('100%', 'center', $Lang::tr{'connection'});

print <<END
<table width='95%' cellspacing='0'>
<tr>
        <td width='25%'>$Lang::tr{'interface'}:</td>
        <td width='25%'>
        <select name='TYPE' style="width: 165px">
END
;
if ($netsettings{'RED_TYPE'} eq 'PPPOE' ) {
print <<END
	<option value='modem' $selected{'TYPE'}{'modem'}>$Lang::tr{'modem'}</option>
	<option value='serial' $selected{'TYPE'}{'serial'}>$Lang::tr{'serial'}</option>
	<option value='pppoe' $selected{'TYPE'}{'pppoe'}>PPPoE</option>
	<option value='pptp' $selected{'TYPE'}{'pptp'}>PPTP</option>
	<option value='vdsl' $selected{'TYPE'}{'vdsl'}>VDSL</option>
END
;

my $atmdev=`cat /proc/net/atm/devices 2>/dev/null | grep 0`;
chomp ($atmdev);
if ($atmdev ne '') {
        print <<END
        <option value='pppoeatm' $selected{'TYPE'}{'pppoeatm'}>PPPoE over ATM-BRIDGE</option>
        <option value='pptpatm' $selected{'TYPE'}{'pptpatm'}>PPTP over ATM-BRIDGE</option>
END
;
}
}
#if (0) {
#       print <<END
#       <option value='eciadsl' $selected{'TYPE'}{'eciadsl'}>ECI USB ADSL</option>
#       <option value='eagleusbadsl' $selected{'TYPE'}{'eagleusbadsl'}>Eagle USB ADSL (Acer Allied-Telesyn Comtrend D-Link Sagem USR)</option>
#       <option value='conexantusbadsl' $selected{'TYPE'}{'conexantusbadsl'}>Conexant USB(Aetra Amigo Draytek Etec Mac Olitec Vitelcom Zoom)</option>
#       <option value='amedynusbadsl' $selected{'TYPE'}{'amedynusbadsl'}>Zyxel 630-11 / Asus AAM6000UG USB ADSL</option>
#       <option value='3cp4218usbadsl' $selected{'TYPE'}{'3cp4218usbadsl'}>3Com USB AccessRunner</option>
#       <option value='alcatelusb' $selected{'TYPE'}{'alcatelusb'}>Speedtouch USB ADSL user mode driver</option>
#       <option value='alcatelusbk' $selected{'TYPE'}{'alcatelusbk'}>Speedtouch USB ADSL kernel mode driver</option>
#END
#;
#}
#       print "<option value='fritzdsl' $selected{'TYPE'}{'fritzdsl'}>Fritz!DSL</option>";

        print <<END
        </select></td>
        <td colspan='1' width='25%'><input type='submit' name='ACTION' value='$Lang::tr{'refresh'}'></td>
END
;
        if ($pppsettings{'TYPE'} =~ /^(modem)$/) {
        print <<END
            <td colspan='1' width='25%'><a href='modem.cgi'>$Lang::tr{'modem configuration'}</a></td>
END
;
}

        print "</tr>";

#if (-f "/proc/bus/usb/devices") {
#       <td colspan='2' width='50%'>USB:</td>
#       my $usb=`lsmod | cut -d ' ' -f1 | grep -E "hci"`;
#       if ($usb eq '') {
#               print "\t<td colspan='2' width='50%'>$Lang::tr{'not running'}</td></tr>\n";
#       } else {
#               print "\t<td colspan='2' width='50%'>$usb</td></tr>\n";
#       }
#}

if ($pppsettings{'TYPE'}) {
        print "<tr><td colspan='4' width='100%'><br></br></td></tr>";

        if ($pppsettings{'TYPE'} =~ /^(modem|serial)$/) {
                print <<END

<tr>
        <td colspan='3' width='75%'>$Lang::tr{'interface'}:</td>
        <td width='25%'><select name='COMPORT' style="width: 165px">
END
;
                if ($pppsettings{'TYPE'} =~ /^(modem|serial)$/ ) {
                        print <<END
                <option value='ttyS0' $selected{'COMPORT'}{'ttyS0'}>COM1</option>
                <option value='ttyS1' $selected{'COMPORT'}{'ttyS1'}>COM2</option>
                <option value='ttyS2' $selected{'COMPORT'}{'ttyS2'}>COM3</option>
                <option value='ttyS3' $selected{'COMPORT'}{'ttyS3'}>COM4</option>
                <option value='ttyS4' $selected{'COMPORT'}{'ttyS4'}>COM5</option>
                <option value='ttyUSB0' $selected{'COMPORT'}{'ttyUSB0'}>ttyUSB0</option>
                <option value='ttyUSB1' $selected{'COMPORT'}{'ttyUSB1'}>ttyUSB1</option>
                <option value='ttyUSB2' $selected{'COMPORT'}{'ttyUSB2'}>ttyUSB2</option>
                <option value='ttyUSB3' $selected{'COMPORT'}{'ttyUSB3'}>ttyUSB3</option>
                <option value='ttyUSB4' $selected{'COMPORT'}{'ttyUSB4'}>ttyUSB4</option>
                <option value='ttyUSB5' $selected{'COMPORT'}{'ttyUSB5'}>ttyUSB5</option>
                <option value='ttyUSB6' $selected{'COMPORT'}{'ttyUSB6'}>ttyUSB6</option>
                <option value='ttyUSB7' $selected{'COMPORT'}{'ttyUSB7'}>ttyUSB7</option>
                <option value='ttyUSB8' $selected{'COMPORT'}{'ttyUSB8'}>ttyUSB8</option>
                <option value='ttyUSB9' $selected{'COMPORT'}{'ttyUSB9'}>ttyUSB9</option>
                <option value='rfcomm0' $selected{'COMPORT'}{'rfcomm0'}>rfcomm0 (bluetooth)</option>
                <option value='rfcomm1' $selected{'COMPORT'}{'rfcomm1'}>rfcomm1 (bluetooth)</option>
END
;
                if ($pppsettings{'TYPE'} ne 'serial' ) {
                        print <<END
                <option value='ttyACM0' $selected{'COMPORT'}{'ttyACM0'}>ttyACM0</option>
                <option value='ttyACM1' $selected{'COMPORT'}{'ttyACM1'}>ttyACM1</option>
                <option value='ttyACM2' $selected{'COMPORT'}{'ttyACM2'}>ttyACM2</option>
                <option value='ttyACM3' $selected{'COMPORT'}{'ttyACM3'}>ttyACM3</option>
                <option value='ttyACM4' $selected{'COMPORT'}{'ttyACM4'}>ttyACM4</option>
                <option value='ttyACM5' $selected{'COMPORT'}{'ttyACM5'}>ttyACM5</option>
                <option value='ttyACM6' $selected{'COMPORT'}{'ttyACM6'}>ttyACM6</option>
                <option value='ttyACM7' $selected{'COMPORT'}{'ttyACM7'}>ttyACM7</option>
                <option value='ttyACM8' $selected{'COMPORT'}{'ttyACM8'}>ttyACM8</option>
                <option value='ttyACM9' $selected{'COMPORT'}{'ttyACM9'}>ttyACM9</option>
END
;
                }
    print "</select></td>       "}

	if ($pppsettings{'TYPE'} =~ /^(modem|serial)$/) {
		print <<END;
			<tr>
				<td colspan='3' width='75%'>$Lang::tr{'monitor interface'}:</td>
				<td width='25%'>
					<select name="MONPORT" style="width: 165px;">
						<option value="" $selected{'MONPORT'}{''}>---</option>
						<option value="ttyUSB0" $selected{'MONPORT'}{'ttyUSB0'}>ttyUSB0</option>
						<option value="ttyUSB1" $selected{'MONPORT'}{'ttyUSB1'}>ttyUSB1</option>
						<option value="ttyUSB2" $selected{'MONPORT'}{'ttyUSB2'}>ttyUSB2</option>
						<option value="ttyUSB3" $selected{'MONPORT'}{'ttyUSB3'}>ttyUSB3</option>
						<option value="ttyUSB4" $selected{'MONPORT'}{'ttyUSB4'}>ttyUSB4</option>
						<option value="ttyUSB5" $selected{'MONPORT'}{'ttyUSB5'}>ttyUSB5</option>
						<option value="ttyUSB6" $selected{'MONPORT'}{'ttyUSB6'}>ttyUSB6</option>
						<option value="ttyUSB7" $selected{'MONPORT'}{'ttyUSB7'}>ttyUSB7</option>
						<option value="ttyUSB8" $selected{'MONPORT'}{'ttyUSB8'}>ttyUSB8</option>
						<option value="ttyUSB9" $selected{'MONPORT'}{'ttyUSB9'}>ttyUSB9</option>
						<option value="rfcomm0" $selected{'COMPORT'}{'rfcomm0'}>rfcomm0 (bluetooth)</option>
						<option value="rfcomm1" $selected{'COMPORT'}{'rfcomm1'}>rfcomm1 (bluetooth)</option>
						<option value="ttyACM0" $selected{'COMPORT'}{'ttyACM0'}>ttyACM0</option>
						<option value="ttyACM1" $selected{'COMPORT'}{'ttyACM1'}>ttyACM1</option>
						<option value="ttyACM2" $selected{'COMPORT'}{'ttyACM2'}>ttyACM2</option>
						<option value="ttyACM3" $selected{'COMPORT'}{'ttyACM3'}>ttyACM3</option>
						<option value="ttyACM4" $selected{'COMPORT'}{'ttyACM4'}>ttyACM4</option>
						<option value="ttyACM5" $selected{'COMPORT'}{'ttyACM5'}>ttyACM5</option>
						<option value="ttyACM6" $selected{'COMPORT'}{'ttyACM6'}>ttyACM6</option>
						<option value="ttyACM7" $selected{'COMPORT'}{'ttyACM7'}>ttyACM7</option>
						<option value="ttyACM8" $selected{'COMPORT'}{'ttyACM8'}>ttyACM8</option>
						<option value="ttyACM9" $selected{'COMPORT'}{'ttyACM9'}>ttyACM9</option>
					</select>
				</td>
			</tr>
END
	}

                if ($pppsettings{'TYPE'} =~ /^(modem|serial)$/ ) {
                        print <<END
  <tr>
   <td colspan='3' width='75%'>$Lang::tr{'computer to modem rate'}</td>
         <td width='25%'><select name='DTERATE' style="width: 165px">
                <option value='9600' $selected{'DTERATE'}{'9600'}>9600</option>
                <option value='19200' $selected{'DTERATE'}{'19200'}>19200</option>
                <option value='38400' $selected{'DTERATE'}{'38400'}>38400</option>
                <option value='57600' $selected{'DTERATE'}{'57600'}>57600</option>
                <option value='115200' $selected{'DTERATE'}{'115200'}>115200</option>
                <option value='230400' $selected{'DTERATE'}{'230400'}>230400</option>
                <option value='460800' $selected{'DTERATE'}{'460800'}>460800</option>
                <option value='921600' $selected{'DTERATE'}{'921600'}>921600</option>
        </select></td>
</tr>
END
;
                }
                if ($pppsettings{'TYPE'} =~ /^(modem)$/ ) {
                        print "<tr><td colspan='3' width='75%'>$Lang::tr{'number'}&nbsp;<img src='/blob.gif' alt='*' /></td>\n";
                        print "<td width='25%'><input type='text' name='TELEPHONE' value='$pppsettings{'TELEPHONE'}'></td><tr>\n";
                        if ($pppsettings{'TYPE'} eq 'modem' ) {
                                print "<tr><td colspan='3' width='75%'>$Lang::tr{'modem speaker on'}</td>\n";
                                print "<td width='25%'><input type='checkbox' name='SPEAKER' $checked{'SPEAKER'}{'on'} /></td></tr>\n";
                        }
                }
        }
        if ($pppsettings{'TYPE'} eq 'modem') {
                print <<END
<tr>
        <td colspan='3' width='75%'>$Lang::tr{'dialing mode'}</td>
        <td width='25%'><select name='DIALMODE' style="width: 165px">
                <option value='T' $selected{'DIALMODE'}{'T'}>$Lang::tr{'tone'}</option>
                <option value='P' $selected{'DIALMODE'}{'P'}>$Lang::tr{'pulse'}</option>
        </select></td>
</tr>
<tr>
        <td colspan='3' width='75%'>$Lang::tr{'optional at cmd'}&nbsp;1</td>
        <td width='25%'><input type='text' name='ADD_AT1' value='$pppsettings{'ADD_AT1'}'></td>
</tr>
<tr>
        <td colspan='3' width='75%'>$Lang::tr{'optional at cmd'}&nbsp;2</td>
        <td width='25%'><input type='text' name='ADD_AT2' value='$pppsettings{'ADD_AT2'}'></td>
</tr>
<tr>
        <td colspan='3' width='75%'>$Lang::tr{'optional at cmd'}&nbsp;3</td>
        <td width='25%'><input type='text' name='ADD_AT3' value='$pppsettings{'ADD_AT3'}'></td>
</tr>
<tr>
  <td colspan='3' width='75%'>$Lang::tr{'send cr'}</td>
        <td width='50%'><input type='checkbox' name='SENDCR' $checked{'SENDCR'}{'on'} /></td>
</tr>
END
;
}

print <<END
<tr>
        <td colspan='3' width='75%'>$Lang::tr{'idle timeout'}&nbsp;<img src='/blob.gif' alt='*' /></td>
        <td width='25%'><input type='text' name='TIMEOUT' value='$pppsettings{'TIMEOUT'}' /></td>
</tr>
 <tr>
  <td colspan='3' width='75%'>$Lang::tr{'connection debugging'}:</td>
        <td width='25%'><input type='checkbox' name='DEBUG' $checked{'DEBUG'}{'on'} /></td>
 </tr>
 <tr>
  <td colspan='4' width='100%'><br></br></td></tr>
<tr>
        <td colspan='4' width='100%' bgcolor='$color{'color20'}'><b>$Lang::tr{'reconnection'}:</b></td>
</tr>
<tr>
        <td colspan='4' width='100%'><input type='radio' name='RECONNECTION' value='dialondemand' $checked{'RECONNECTION'}{'dialondemand'}>$Lang::tr{'dod'}</td>
 </tr>
END
;
if ($pppsettings{'TYPE'} ne 'isdn') {
print <<END
 <tr>
        <td colspan='4' width='100%'><input type='radio' name='RECONNECTION' value='persistent' $checked{'RECONNECTION'}{'persistent'}>$Lang::tr{'persistent'}</td>
 </tr>
 <tr>
  <td colspan='3' width='75%'>$Lang::tr{'backupprofile'}:</td>
        <td width='25%'><select name='BACKUPPROFILE' style="width: 165px">
END
;
        for ($c = 1; $c <= $maxprofiles; $c++) {
                print "\t<option value='$c' $selected{'BACKUPPROFILE'}{$c}>$c. $profilenames[$c]</option>\n";
        }
        print <<END
        </select></td>
</tr>
END
;
}
print <<END
 <tr>
        <td colspan='3' width='75%'>$Lang::tr{'dod for dns'}</td>
  <td width='25%'><input type='checkbox' name='DIALONDEMANDDNS' $checked{'DIALONDEMANDDNS'}{'on'} /></td>
</tr>
<tr>
        <td colspan='3' width='75%'>$Lang::tr{'holdoff'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
        <td width='25%'><input type='text' name='HOLDOFF' value='$pppsettings{'HOLDOFF'}' /></td>
</tr>
<tr>
        <td colspan='3' width='75%'>$Lang::tr{'maximum retries'}&nbsp;<img src='/blob.gif' alt='*' /></td>
        <td width='25%'><input type='text' name='MAXRETRIES' value='$pppsettings{'MAXRETRIES'}' /></td>
</tr>
END
;

if ($pppsettings{'TYPE'} eq 'pptp')
{

print <<END
<tr><td colspan='4' width='100%'><br></br></td></tr>
<tr>
        <td colspan='4' width='100%' bgcolor='$color{'color20'}'><b>$Lang::tr{'pptp settings'}</b></td>
</tr>
<tr>
        <td width='25%'>$Lang::tr{'pptp peer'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
        <td colspan='3'><input size=50 type='text' name='PPTP_PEER' value='$pppsettings{'PPTP_PEER'}' /></td>
</tr>
<tr>
        <td width='25%'>$Lang::tr{'pptp netconfig'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
        <td colspan='3'><input size=50 type='text' name='PPTP_NICCFG' value='$pppsettings{'PPTP_NICCFG'}' /></td>
</tr>
<tr>
        <td width='25%'>$Lang::tr{'pptp route'}:</td>
        <td colspan='3'><input size=50 type='text' name='PPTP_ROUTE' value='$pppsettings{'PPTP_ROUTE'}' /></td>
</tr>

END
;
}

if ($pppsettings{'TYPE'} =~ /^(pppoeatm|pptpatm)$/)
{

print <<END
<tr>
        <td colspan='4' width='100%' bgcolor='$color{'color20'}'><b>$Lang::tr{'atm settings'}:</b></td>
<tr>
        <td nowrap='nowrap'>$Lang::tr{'atm device'}</td>
        <td><input type='text' size='5' name='ATM_DEV' value='$pppsettings{'ATM_DEV'}' /></td>
        <td> $Lang::tr{'encapsulation'}:</td>
        <td>
                <select name='ENCAP'>
                   <option value='0' $selected{'ENCAP'}{'0'}>LLC</option>
                   <option value='1' $selected{'ENCAP'}{'1'}>VCmux</option>
                </select>
        </td>
</tr>
<tr>
        <td nowrap='nowrap'>$Lang::tr{'vpi number'}</td>
        <td><input type='text' size='5' name='VPI' value='$pppsettings{'VPI'}' /></td>
        <td> $Lang::tr{'vci number'}</td>
        <td><input type='text' size='5' name='VCI' value='$pppsettings{'VCI'}' /></td>
</tr>
END
;
}

        if ($pppsettings{'TYPE'} =~ /^(pppoe|vdsl|pppoeatm)$/) {
print <<END
<tr>
        <td colspan='4' width='100%' bgcolor='$color{'color20'}'><b>IPTV/VLAN:</b></td>
</tr>
END
;
	if ( -e '/opt/pakfire/db/installed/meta-igmpproxy'){
print <<END
		<tr>
		        <td colspan='3' width='100%'><input type='radio' name='IPTV' value='enable' $checked{'IPTV'}{'enable'}>$Lang::tr{'on'}</td>
		        <td colspan='1' rowspan='2' width='100%'><textarea name='IPTVSERVERS' cols='16' wrap='off'>
END
;
		print $pppsettings{'IPTVSERVERS'};
print <<END
</textarea></td>
		</tr>
		<tr>
		        <td colspan='3' width='100%'><input type='radio' name='IPTV' value='disable' $checked{'IPTV'}{'disable'}>$Lang::tr{'off'}</td>
		</tr>
		<tr>
			<td>INET_VLAN</td>
			<td><input size=5 type='number' name='INET_VLAN' value='$pppsettings{'INET_VLAN'}' /></td>
			<td>IPTV_VLAN</td>
			<td><input size=5 type='number' name='IPTV_VLAN' value='$pppsettings{'IPTV_VLAN'}' /></td>
		</tr>

END
;
	}
	else {
	print "<tr><td colspan='4' width='100%'>No IPTV possible install addon igmpproxy</td></tr>";
		if ($pppsettings{'TYPE'} eq 'vdsl') {
print <<END
			<tr>
				<td>INET_VLAN</td>
				<td><input size=5 type='number' name='INET_VLAN' value='$pppsettings{'INET_VLAN'}' /></td>
			</tr>
END
;
		}
	}
}

if ($pppsettings{'TYPE'} eq 'pppoe' || $pppsettings{'TYPE'} eq 'pppoeatm' || $pppsettings{'TYPE'} eq 'vdsl')
{
print <<END
<tr><td colspan='4' width='100%'><br></br></td></tr>
<tr>
        <td colspan='4' width='100%' bgcolor='$color{'color20'}'><b>$Lang::tr{'pppoe settings'}</b></td>
</tr>
<tr>
        <td width='25%'>$Lang::tr{'service name'}</td>
        <td colspan='2' width='50%'></td>
        <td width='25%'><input type='text' name='SERVICENAME' value='$pppsettings{'SERVICENAME'}' /></td>
</tr>
<tr>
        <td width='25%'>$Lang::tr{'concentrator name'}</td>
        <td colspan='2' width='50%'></td>
        <td width='25%'><input type='text' name='CONCENTRATORNAME' value='$pppsettings{'CONCENTRATORNAME'}' /></td>
</tr>
END
;
}

print <<END
<tr><td colspan='4' width='100%'><br></br></td></tr>
<tr>
        <td bgcolor='$color{'color20'}' colspan='4' width='100%'><b>MTU/MRU</b></td>
</tr>
<tr>
<tr>
        <td width='25%'>MTU:</td>
        <td width='25%'><input type='text' name='MTU' value='$pppsettings{'MTU'}' /></td>
</tr>
<tr>
        <td width='25%'>MRU:</td>
        <td width='25%'><input type='text' name='MRU' value='$pppsettings{'MRU'}' /></td>
</tr>
END
;

print <<END
<tr><td colspan='4' width='100%'><br></br></td></tr>
<tr>
        <td bgcolor='$color{'color20'}' colspan='4' width='100%'><b>$Lang::tr{'authentication'}</b></td>
</tr>
<tr>
        <td width='25%'>$Lang::tr{'username'}&nbsp;<img src='/blob.gif' alt='*' /></td>
        <td width='25%'><input type='text' name='USERNAME' value='$pppsettings{'USERNAME'}' /></td>
        <td width='25%'>$Lang::tr{'password'}&nbsp;</td>
        <td width='25%'><input type='password' name='PASSWORD' value='$pppsettings{'PASSWORD'}' /></td>
</tr>
<tr>
        <td width='25%'>$Lang::tr{'method'}</td>
        <td width='25%'><select name='AUTH' style="width: 165px">
                <option value='pap-or-chap' $selected{'AUTH'}{'pap-or-chap'}>$Lang::tr{'pap or chap'}</option>
                <option value='pap' $selected{'AUTH'}{'pap'}>PAP</option>
                <option value='chap' $selected{'AUTH'}{'chap'}>CHAP</option>
END
;
if ($pppsettings{'TYPE'} eq 'modem') {
print <<END
                <option value='standard-login-script' $selected{'AUTH'}{'standard-login-script'}>$Lang::tr{'standard login script'}</option>
                <option value='demon-login-script' $selected{'AUTH'}{'demon-login-script'}>$Lang::tr{'demon login script'}</option>
                <option value='other-login-script' $selected{'AUTH'}{'other-login-script'}>$Lang::tr{'other login script'}</option>
END
;
}
print <<END
        </select></td>
        <td width='25%'>$Lang::tr{'script name'}</td>
        <td width='25%'><input type='text' name='LOGINSCRIPT' value='$pppsettings{'LOGINSCRIPT'}' /></td>
</tr>
<tr><td colspan='4' width='100%'><br></br></td></tr>
<tr>
        <td bgcolor='$color{'color20'}' colspan='4' width='100%'><b>DNS:</b></td>
</tr>
<tr>
        <td colspan='4' width='100%'><input type='radio' name='DNS' value='Automatic' $checked{'DNS'}{'Automatic'} />$Lang::tr{'automatic'}</td>
</tr>
<tr>
        <td colspan='4' width='100%'><input type='radio' name='DNS' value='Manual' $checked{'DNS'}{'Manual'} />$Lang::tr{'manual'}</td>
</tr>
<tr>
        <td width='25%'>$Lang::tr{'primary dns'}</td>
        <td width='25%'><input type='text' name='DNS1' value='$pppsettings{'DNS1'}'></td>
        <td width='25%'>$Lang::tr{'secondary dns'}</td>
        <td width='25%'><input type='text' name='DNS2' value='$pppsettings{'DNS2'}'></td>
</tr>
<tr><td colspan='4' width='100%'><br></br><hr></hr><br></br></td></tr>
<tr>
        <td width='25%'>$Lang::tr{'profile name'}&nbsp;<img src='/blob.gif' alt='*' /></td>
        <td width='25%'><input type='text' name='PROFILENAME' value='$pppsettings{'PROFILENAME'}'>
        <td colspan='2' width='50%'></td>
</tr>
<tr>
  <td align='center' colspan='4' width='100%'><input type='submit' name='ACTION' value='$Lang::tr{'save'}'></td>
</tr>
<tr>
        <td colspan='2' width='50%'>$Lang::tr{'legend'}:</td>
        <td colspan='2' width='50%'><img src='/blob.gif' alt='*' />&nbsp;$Lang::tr{'required field'}</td>
</tr>
END
;
}

print "</table>";

&Header::closebox();

print "</form>\n";

&Header::closebigbox();

&Header::closepage();

sub updatesettings
{
        # make a link from the selected profile to the "default" one.
        unlink("${General::swroot}/ppp/settings");
        link("${General::swroot}/ppp/settings-$pppsettings{'PROFILE'}",
                "${General::swroot}/ppp/settings");
        system ("/usr/bin/touch", "${General::swroot}/ppp/updatesettings");
}

sub writesecrets
{
        # write secrets file.
        open(FILE, ">/${General::swroot}/ppp/secrets") or die "Unable to write secrets file.";
        flock(FILE, 2);
        my $username = $pppsettings{'USERNAME'};
        my $password = $pppsettings{'PASSWORD'};
        print FILE "'$username' * '$password'\n";
        chmod 0600, "${General::swroot}/ppp/secrets";
        close FILE;
}

sub initprofile
{
        $pppsettings{'PROFILENAME'} = $Lang::tr{'unnamed'};
        $pppsettings{'COMPORT'} = 'ttyS0';
        $pppsettings{'MONPORT'} = '';
        $pppsettings{'DTERATE'} = 115200;
        $pppsettings{'SPEAKER'} = 'off';
        $pppsettings{'RECONNECTION'} = 'persistent';
        $pppsettings{'DIALONDEMANDDNS'} = 'off';
        $pppsettings{'AUTOCONNECT'} = 'on';
        $pppsettings{'SENDCR'} = 'off';
        $pppsettings{'USEIBOD'} = 'off';
        $pppsettings{'USEDOV'} = 'off';
        $pppsettings{'MODEM'} = 'PCIST';
        $pppsettings{'LINE'} = 'WO';
        $pppsettings{'ENCAP'} = '0';
        $pppsettings{'VPI'} = '1';
        $pppsettings{'VCI'} = '32';
        $pppsettings{'ATM_DEV'} = '0';
        $pppsettings{'PPTP_PEER'} = '10.0.0.138';
	$pppsettings{'PPTP_NICCFG'} = '10.0.0.140/24 broadcast 10.0.0.255';
	$pppsettings{'PPTP_ROUTE'} = '';
        $pppsettings{'PROTOCOL'} = 'RFC2364';
        $pppsettings{'MTU'} = '';
        $pppsettings{'MRU'} = '';
        $pppsettings{'DIALMODE'} = 'T';
        $pppsettings{'MAXRETRIES'} = 5;
        $pppsettings{'HOLDOFF'} = 30;
        $pppsettings{'TIMEOUT'} = 15;
        $pppsettings{'MODULATION'} = 'AUTO';
        $pppsettings{'AUTH'} = 'pap-or-chap';
        $pppsettings{'DNS'} = 'Automatic';
        $pppsettings{'DEBUG'} = 'off';
        $pppsettings{'BACKUPPROFILE'} = $pppsettings{'PROFILE'};
        $pppsettings{'IPTVSERVERS'} = '192.168.2.51/32';
        $pppsettings{'IPTV'} = 'disable';
        $pppsettings{'INET_VLAN'} = '7';
        $pppsettings{'IPTV_VLAN'} = '8';

	if ( -e '/usr/local/bin/igmpproxy'){
	        $pppsettings{'IPTV'} = 'enable';
	}

        # Get PPPoE settings so we can see if PPPoE is enabled or not.
        &General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

        # empty profile partial pre-initialization
        if ($netsettings{'CONFIG_TYPE'} =~ /^(1|2|3|4)$/) {
                $pppsettings{'TYPE'}=lc($netsettings{'RED_TYPE'});
        } else {
                $pppsettings{'TYPE'}='modem';
        }
}

