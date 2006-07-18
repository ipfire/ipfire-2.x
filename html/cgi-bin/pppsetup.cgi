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

&Header::showhttpheaders();

$pppsettings{'ACTION'} = '';
&initprofile();
&Header::getcgihash(\%pppsettings);

if ($pppsettings{'ACTION'} ne '' &&
	(-e '/var/run/ppp-ipcop.pid' || -e "${General::swroot}/red/active"))
{
	$errormessage = $Lang::tr{'unable to alter profiles while red is active'};
	# read in the current vars
	%pppsettings = ();
	$pppsettings{'VALID'} = '';
	&General::readhash("${General::swroot}/ppp/settings", \%pppsettings);
}
elsif ($pppsettings{'ACTION'} eq $Lang::tr{'refresh'})
{
	unless ($pppsettings{'TYPE'} =~ /^(modem|serial|isdn|pppoe|pptp|alcatelusb|alcatelusbk|amedynusbadsl|conexantusbadsl|conexantpciadsl|3cp4218usbadsl|pulsardsl|eciadsl|fritzdsl|bewanadsl|eagleusbadsl)$/) {
		$errormessage = $Lang::tr{'invalid input'};
		goto ERROR; }
	my $type = $pppsettings{'TYPE'};
	&General::readhash("${General::swroot}/ppp/settings", \%pppsettings);
	$pppsettings{'TYPE'} = $type;
}
elsif ($pppsettings{'ACTION'} eq $Lang::tr{'save'})
{
	if ($pppsettings{'TYPE'} =~ /^(modem|serial|isdn)$/ && $pppsettings{'COMPORT'} !~ /^(ttyS0|ttyS1|ttyS2|ttyS3|ttyS4|usb\/ttyACM0|usb\/ttyACM1|usb\/ttyACM2|usb\/ttyACM3|isdn1|isdn2)$/) {
		$errormessage = $Lang::tr{'invalid input'};
		goto ERROR; }
	if ($pppsettings{'TYPE'} =~ /^(modem|serial)$/ && $pppsettings{'DTERATE'} !~ /^(9600|19200|38400|57600|115200|230400|460800)$/) {
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
		if ($pppsettings{'PASSWORD'} eq '') {
			$errormessage = $Lang::tr{'password not set'};
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

	my $drivererror = 0;
	if ($pppsettings{'TYPE'} =~ /^(alcatelusb|alcatelusbk)$/) {
		my $modem = '';
		my $speedtouch = &Header::speedtouchversion;
		if ($speedtouch >=0 && $speedtouch <=4) {
			if ($speedtouch ==4) { $modem='v4_b'; } else { $modem='v0123'; }
			$pppsettings{'MODEM'} = $modem;
		} else {
			$modem='v0123';
			$errormessage ="$Lang::tr{'unknown'} Rev $speedtouch";
			goto ERROR;
		}
		if (! -e "${General::swroot}/alcatelusb/firmware.$modem.bin") {
			$errormessage = $Lang::tr{'no alcatelusb firmware'};
			$drivererror = 1;
			goto ERROR;
		}
	}

	if($pppsettings{'TYPE'} eq 'eciadsl' && (!(-e "${General::swroot}/eciadsl/synch.bin"))) {
		$errormessage = $Lang::tr{'no eciadsl synch.bin file'};
		$drivererror = 1;
		goto ERROR; }

	if($pppsettings{'TYPE'} eq 'fritzdsl' && (!(-e "/lib/modules/$kernel/misc/fcdslusb.o.gz"))) {
		$errormessage = $Lang::tr{'no fritzdsl driver'};
		$drivererror = 1;
		goto ERROR; }

	if( $pppsettings{'USEIBOD'} eq 'on' && $pppsettings{'COMPORT'} eq 'isdn1') {
		$errormessage = $Lang::tr{'ibod for dual isdn only'};
		goto ERROR; }

	if ($pppsettings{'TYPE'} eq 'pptp') {
		$errormessage = '';
		if ($pppsettings{'METHOD'} eq 'STATIC') {
			if (! &General::validip($pppsettings{'ROUTERIP'})) {
				$errormessage = $Lang::tr{'router ip'}.' '.$Lang::tr{'invalid ip'};
			}
		} else {
			if (($pppsettings{'DHCP_HOSTNAME'} ne '') && (! &General::validfqdn($pppsettings{'DHCP_HOSTNAME'})) ) {
				$errormessage = $errormessage.' '.$Lang::tr{'hostname'}.' '.$Lang::tr{'invalid hostname'};
			}
		}
		if ($errormessage ne '') {goto ERROR; }
	}

	if ($pppsettings{'TYPE'} =~ /^(alcatelusb|alcatelusbk|amedynusbadsl|conexantusbadsl|conexantpciadsl|3cp4218usbadsl|pulsardsl|eciadsl|fritzdsl|bewanadsl|eagleusbadsl)$/) {
		if ( ($pppsettings{'VPI'} eq '') || ($pppsettings{'VCI'} eq '') ) {
			$errormessage = $Lang::tr{'invalid vpi vpci'};
			goto ERROR; }
		if ( (!($pppsettings{'VPI'} =~ /^\d+$/)) || (!($pppsettings{'VCI'} =~ /^\d+$/)) ) {
			$errormessage = $Lang::tr{'invalid vpi vpci'};
			goto ERROR; }
		if (($pppsettings{'VPI'} eq '0') && ($pppsettings{'VCI'} eq '0')) {
			$errormessage = $Lang::tr{'invalid vpi vpci'};
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

	if ( ($pppsettings{'TYPE'} =~ /^(bewanadsl)$/) && $pppsettings{'MODEM'} eq '') {
		$errormessage = $Lang::tr{'no modem selected'};
		goto ERROR; }

	if( $pppsettings{'PROTOCOL'} eq 'RFC1483') {
		$pppsettings{'ENCAP'} = $pppsettings{'ENCAP_RFC1483'}; }
	if( $pppsettings{'PROTOCOL'} eq 'RFC2364') {
		$pppsettings{'ENCAP'} = $pppsettings{'ENCAP_RFC2364'}; }
	delete $pppsettings{'ENCAP_RFC1483'};
	delete $pppsettings{'ENCAP_RFC2364'};

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
	if ($drivererror) {
	my $refresh = "<META HTTP-EQUIV='refresh' CONTENT='1; URL=/cgi-bin/upload.cgi'>";
		my $title = $Lang::tr{'upload'};
		&Header::openpage($title, 0, $refresh);
	}
}
elsif ($pppsettings{'ACTION'} eq $Lang::tr{'select'})
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
$selected{'TYPE'}{'isdn'} = '';
$selected{'TYPE'}{'pppoe'} = '';
$selected{'TYPE'}{'pptp'} = '';
$selected{'TYPE'}{'alcatelusb'} = '';
$selected{'TYPE'}{'alcatelusbk'} = '';
$selected{'TYPE'}{'pulsardsl'} = '';
$selected{'TYPE'}{'eciadsl'} = '';
$selected{'TYPE'}{'fritzdsl'} = '';
$selected{'TYPE'}{'bewanadsl'} = '';
$selected{'TYPE'}{'eagleusbadsl'} = '';
$selected{'TYPE'}{'conexantusbadsl'} = '';
$selected{'TYPE'}{'conexantpciadsl'} = '';
$selected{'TYPE'}{'amedynusbadsl'} = '';
$selected{'TYPE'}{'3cp4218usbadsl'} = '';
$selected{'TYPE'}{$pppsettings{'TYPE'}} = "selected='selected'";

$checked{'DEBUG'}{'off'} = '';
$checked{'DEBUG'}{'on'} = '';
$checked{'DEBUG'}{$pppsettings{'DEBUG'}} = "checked='checked'";

$selected{'COMPORT'}{'ttyS0'} = '';
$selected{'COMPORT'}{'ttyS1'} = '';
$selected{'COMPORT'}{'ttyS2'} = '';
$selected{'COMPORT'}{'ttyS3'} = '';
$selected{'COMPORT'}{'ttyS4'} = '';
$selected{'COMPORT'}{'usb/ttyACM0'} = '';
$selected{'COMPORT'}{'usb/ttyACM1'} = '';
$selected{'COMPORT'}{'usb/ttyACM2'} = '';
$selected{'COMPORT'}{'usb/ttyACM3'} = '';
$selected{'COMPORT'}{'isdn1'} = '';
$selected{'COMPORT'}{'isdn2'} = '';
$selected{'COMPORT'}{$pppsettings{'COMPORT'}} = "selected='selected'";

$selected{'DTERATE'}{'9600'} = '';
$selected{'DTERATE'}{'19200'} = '';
$selected{'DTERATE'}{'38400'} = '';
$selected{'DTERATE'}{'57600'} = '';
$selected{'DTERATE'}{'115200'} = '';
$selected{'DTERATE'}{'230400'} = '';
$selected{'DTERATE'}{'460800'} = '';
$selected{'DTERATE'}{$pppsettings{'DTERATE'}} = "selected='selected'";

$checked{'SPEAKER'}{'off'} = '';
$checked{'SPEAKER'}{'on'} = '';
$checked{'SPEAKER'}{$pppsettings{'SPEAKER'}} = "checked='checked'";

$selected{'DIALMODE'}{'T'} = '';
$selected{'DIALMODE'}{'P'} = '';
$selected{'DIALMODE'}{$pppsettings{'DIALMODE'}} = "selected='selected'";

$checked{'RECONNECTION'}{'manual'} = '';
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
$checked{'USEIBOD'}{'off'} = '';
$checked{'USEIBOD'}{'on'} = '';
$checked{'USEIBOD'}{$pppsettings{'USEIBOD'}} = "checked='checked'";

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
$selected{'ENCAP'}{'2'} = '';
$selected{'ENCAP'}{'3'} = '';
$selected{'ENCAP'}{'4'} = '';
$selected{'ENCAP'}{$pppsettings{'ENCAP'}} = "selected='selected'";
$checked{'METHOD'}{'STATIC'} = '';
$checked{'METHOD'}{'PPPOE'} = '';
$checked{'METHOD'}{'PPPOE_PLUGIN'} = '';
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

&Header::openpage($Lang::tr{'ppp setup'}, 1, '');

&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<CLASS name='base'>$errormessage\n";
	print "&nbsp;</CLASS>\n";
	&Header::closebox();
}


###
### Box for selecting profile
###
print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";
&Header::openbox('100%', 'left', $Lang::tr{'profiles'});
print <<END
<table width='100%'>
<tr>
	<td align='right'>$Lang::tr{'profile'}:</td>
	<td>
	<select name='PROFILE'>
END
;
for ($c = 1; $c <= $maxprofiles; $c++)
{
	print "\t<option value='$c' $selected{'PROFILE'}{$c}>$c. $profilenames[$c]</option>\n";
}
print <<END
	</select></td>
	<td><input type='submit' name='ACTION' value='$Lang::tr{'select'}' /></td>
	<td><input type='submit' name='ACTION' value='$Lang::tr{'delete'}' /></td>
	<td width='30%'><input type='submit' name='ACTION' value='$Lang::tr{'restore'}' /></td>
</tr>
</table>
END
;
&Header::closebox();
&Header::openbox('100%', 'left', $Lang::tr{'connection'}.':');
print <<END
<table width='100%'>
<tr>
	<td align='right'>$Lang::tr{'interface'}:</td>
	<td>
	<select name='TYPE'>
	<option value='modem' $selected{'TYPE'}{'modem'}>$Lang::tr{'modem'}</option>
	<option value='serial' $selected{'TYPE'}{'serial'}>$Lang::tr{'serial'}</option>
END
;
if ($isdnsettings{'ENABLED'} eq 'on') {
	print "\t<option value='isdn' $selected{'TYPE'}{'isdn'}>$Lang::tr{'isdn'}</option>\n";
}
if ($netsettings{'RED_TYPE'} eq 'PPPOE') {
	print "\t<option value='pppoe' $selected{'TYPE'}{'pppoe'}>PPPoE</option>\n";
}
if ($netsettings{'RED_TYPE'} eq 'PPTP') {
	print "\t<option value='pptp' $selected{'TYPE'}{'pptp'}>PPTP</option>\n";
}
if (-f "/proc/bus/usb/devices") {
	print <<END
	<option value='eciadsl' $selected{'TYPE'}{'eciadsl'}>ECI USB ADSL</option>
	<option value='eagleusbadsl' $selected{'TYPE'}{'eagleusbadsl'}>Eagle USB ADSL (Acer Allied-Telesyn Comtrend D-Link Sagem USR)</option>
	<option value='conexantusbadsl' $selected{'TYPE'}{'conexantusbadsl'}>Conexant USB(Aetra Amigo Draytek Etec Mac Olitec Vitelcom Zoom)</option>
	<option value='amedynusbadsl' $selected{'TYPE'}{'amedynusbadsl'}>Zyxel 630-11 / Asus AAM6000UG USB ADSL</option>
	<option value='3cp4218usbadsl' $selected{'TYPE'}{'3cp4218usbadsl'}>3Com USB AccessRunner</option>
	<option value='alcatelusb' $selected{'TYPE'}{'alcatelusb'}>Speedtouch USB ADSL user mode driver</option>
	<option value='alcatelusbk' $selected{'TYPE'}{'alcatelusbk'}>Speedtouch USB ADSL kernel mode driver</option>
END
;
}
	print <<END
	<option value='fritzdsl' $selected{'TYPE'}{'fritzdsl'}>Fritz!DSL</option>
	<option value='pulsardsl' $selected{'TYPE'}{'pulsardsl'}>Pulsar ADSL</option>
	<option value='bewanadsl' $selected{'TYPE'}{'bewanadsl'}>Bewan ADSL PCI st/USB st</option>
	<option value='conexantpciadsl' $selected{'TYPE'}{'conexantpciadsl'}>Conexant PCI ADSL</option>
	</select></td>
	<td width='50%'><input type='submit' name='ACTION' value='$Lang::tr{'refresh'}' /></td>
	</tr>
	<tr>
	<td align='right'>USB:</td>
END
;
if (-f "/proc/bus/usb/devices") {
	my $usb=`lsmod | cut -d ' ' -f1 | grep -E "hci"`;
	if ($usb eq '') {
		print "\t<td>$Lang::tr{'not running'}</td></tr>\n";
	} else {
		print "\t<td>$usb</td></tr>\n";
	}
}

if ($pppsettings{'TYPE'}) {
	print "</table><table width='100%'>";
	if ($pppsettings{'TYPE'} =~ /^(modem|serial|isdn)$/) {
		print <<END
<tr>
	<td align='right'>$Lang::tr{'interface'}:</td>
	<td><select name='COMPORT'>
END
;
		if ($pppsettings{'TYPE'} =~ /^(modem|serial)$/ ) {
			print <<END
		<option value='ttyS0' $selected{'COMPORT'}{'ttyS0'}>$Lang::tr{'modem on com1'}</option>
		<option value='ttyS1' $selected{'COMPORT'}{'ttyS1'}>$Lang::tr{'modem on com2'}</option>
		<option value='ttyS2' $selected{'COMPORT'}{'ttyS2'}>$Lang::tr{'modem on com3'}</option>
		<option value='ttyS3' $selected{'COMPORT'}{'ttyS3'}>$Lang::tr{'modem on com4'}</option>
		<option value='ttyS4' $selected{'COMPORT'}{'ttyS4'}>$Lang::tr{'modem on com5'}</option>
		<option value='usb/ttyACM0' $selected{'COMPORT'}{'usb/ttyACM0'}>$Lang::tr{'usb modem on acm0'}</option>
		<option value='usb/ttyACM1' $selected{'COMPORT'}{'usb/ttyACM1'}>$Lang::tr{'usb modem on acm1'}</option>
		<option value='usb/ttyACM2' $selected{'COMPORT'}{'usb/ttyACM2'}>$Lang::tr{'usb modem on acm2'}</option>
		<option value='usb/ttyACM3' $selected{'COMPORT'}{'usb/ttyACM3'}>$Lang::tr{'usb modem on acm3'}</option>
	</select></td>
END
;
		} elsif ($pppsettings{'TYPE'} eq 'isdn') {
			print <<END
		<option value='isdn1' $selected{'COMPORT'}{'isdn1'}>$Lang::tr{'isdn1'}</option>
		<option value='isdn2' $selected{'COMPORT'}{'isdn2'}>$Lang::tr{'isdn2'}</option>
	</select></td>
END
;
		}
		if ($pppsettings{'TYPE'} =~ /^(modem|serial)$/ ) {
			print <<END
	<td align='right'>$Lang::tr{'computer to modem rate'}</td>
	<td><select name='DTERATE'>
		<option value='9600' $selected{'DTERATE'}{'9600'}>9600</option>
		<option value='19200' $selected{'DTERATE'}{'19200'}>19200</option>
		<option value='38400' $selected{'DTERATE'}{'38400'}>38400</option>
		<option value='57600' $selected{'DTERATE'}{'57600'}>57600</option>
		<option value='115200' $selected{'DTERATE'}{'115200'}>115200</option>
		<option value='230400' $selected{'DTERATE'}{'230400'}>230400</option>
		<option value='460800' $selected{'DTERATE'}{'460800'}>460800</option>
	</select></td>
</tr>
END
;
		} else {
			print "<td colspan='2'>&nbsp;</td></tr>\n";
		}
		if ($pppsettings{'TYPE'} =~ /^(modem|isdn)$/ ) {
			print "<tr><td align='right'>$Lang::tr{'number'}</td>\n";
			print "<td><input type='text' name='TELEPHONE' value='$pppsettings{'TELEPHONE'}' /></td>\n";
			if ($pppsettings{'TYPE'} eq 'modem' ) {
				print "<td align='right'>$Lang::tr{'modem speaker on'}</td>\n";
				print "<td><input type='checkbox' name='SPEAKER' $checked{'SPEAKER'}{'on'} /></td></tr>\n";
			} else {
				print "<td colspan='2'>&nbsp;</td></tr>\n";
			}
		}
	}
	if ($pppsettings{'TYPE'} eq 'modem') {
		print <<END
<tr>
	<td align='right'>$Lang::tr{'dialing mode'}</td>
	<td><select name='DIALMODE'>
		<option value='T' $selected{'DIALMODE'}{'T'}>$Lang::tr{'tone'}</option>
		<option value='P' $selected{'DIALMODE'}{'P'}>$Lang::tr{'pulse'}</option>
	</select></td>
	<td align='right'>$Lang::tr{'send cr'}</td>
	<td><input type='checkbox' name='SENDCR' $checked{'SENDCR'}{'on'} /></td>
</tr>
END
; 
}

print <<END
<tr>
	<td align='right'>$Lang::tr{'idle timeout'}</td>
	<td><input type='text' size='5' name='TIMEOUT' value='$pppsettings{'TIMEOUT'}' /></td>
	<td colspan='2'>&nbsp;</td>
</tr>
END
;
	if ( $netsettings{'CONFIG_TYPE'} =~ /^(2|3|6|7)$/ && ( $netsettings{'RED_TYPE'} eq "DHCP" || $netsettings{'RED_TYPE'} eq "STATIC") ) {
		$pppsettings{'AUTOCONNECT'} = 'on';
		print "<tr><td align='right'>$Lang::tr{'connect on ipfire restart'}</td>\n";
		print "<td><input type='checkbox' disabled='disabled' name='AUTOCONNECT' value='on' $checked{'AUTOCONNECT'}{'on'} /></td>\n";
	} else {
		print "<tr><td align='right'>$Lang::tr{'connect on ipfire restart'}</td>\n";
		print "<td><input type='checkbox' name='AUTOCONNECT' value='on' $checked{'AUTOCONNECT'}{'on'} /></td>\n";
	}
print <<END
	<td align='right'>$Lang::tr{'connection debugging'}:</td>
	<td><input type='checkbox' name='DEBUG' $checked{'DEBUG'}{'on'} /></td>
</tr>
<tr>
	<td colspan='5'><br /><hr /><b>$Lang::tr{'reconnection'}:</b></td>
</tr>
<tr>
	<td colspan='4'>
		<input type='radio' name='RECONNECTION' value='manual' $checked{'RECONNECTION'}{'manual'} />$Lang::tr{'manual'}</td>
</tr>
END
;
if ($pppsettings{'TYPE'} ne 'isdn') {
print <<END
<tr>
	<td>
		<input type='radio' name='RECONNECTION' value='persistent' $checked{'RECONNECTION'}{'persistent'} />$Lang::tr{'persistent'}</td>
	<td colspan='2' align='right'>$Lang::tr{'backupprofile'}:</td>
	<td>
	<select name='BACKUPPROFILE'>
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
	<td>
		<input type='radio' name='RECONNECTION' value='dialondemand' $checked{'RECONNECTION'}{'dialondemand'} />$Lang::tr{'dod'}</td>
	<td colspan='2' align='right'>$Lang::tr{'dod for dns'}</td>
	<td><input type='checkbox' name='DIALONDEMANDDNS' $checked{'DIALONDEMANDDNS'}{'on'} /></td>

</tr>
<tr>
	<td align='right'>$Lang::tr{'holdoff'}:</td>
	<td><input type='text' size='5' name='HOLDOFF' value='$pppsettings{'HOLDOFF'}' /></td>
	<td align='right'>$Lang::tr{'maximum retries'}</td>
	<td><input type='text' size='5' name='MAXRETRIES' value='$pppsettings{'MAXRETRIES'}' /></td>
</tr>
END
;

if ($pppsettings{'TYPE'} eq 'isdn') {
	print <<END
</table>
<table width='100%'>
<tr>
	<td colspan='5'><br /><hr /><b>$Lang::tr{'isdn settings'}</b></td>
</tr>
<tr>
	<td align='right'>$Lang::tr{'use ibod'}</td>
	<td><input type='checkbox' name='USEIBOD' $checked{'USEIBOD'}{'on'} /></td>
	<td align='right'>$Lang::tr{'use dov'}</td>
	<td><input type='checkbox' name='USEDOV' $checked{'USEDOV'}{'on'} /></td>
</tr>
END
;
}

if ($pppsettings{'TYPE'} eq 'pptp')
{
print <<END
</table>

<table width='100%'>
<tr>
	<td colspan='5'><br /><hr /><b>$Lang::tr{'pptp settings'}</b></td>
</tr>
<tr>
	<td colspan='2' align='right'>$Lang::tr{'phonebook entry'}</td>
	<td><input type='text' name='PHONEBOOK' value='$pppsettings{'PHONEBOOK'}' /></td>
</tr>
<tr>
	<td><input type='radio' name='METHOD' value='STATIC' $checked{'METHOD'}{'STATIC'} />$Lang::tr{'static ip'}</td>
	<td align='right'>$Lang::tr{'router ip'}</td>
	<td><input type='text' name='ROUTERIP' value='$pppsettings{'ROUTERIP'}' /></td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td colspan='3'><hr /></td>
</tr>
<tr>
	<td><input type='radio' name='METHOD' value='DHCP' $checked{'METHOD'}{'DHCP'} />$Lang::tr{'dhcp mode'}</td>
	<td align='right'>$Lang::tr{'hostname'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td><input type='text' name='DHCP_HOSTNAME' value='$pppsettings{'DHCP_HOSTNAME'}' /></td>
</tr>
END
;
}
if ($pppsettings{'TYPE'} eq 'pppoe')
{
print <<END
</table>
<table width='100%'>
<tr>
	<td colspan='5'><br /><hr /><b>$Lang::tr{'pppoe settings'}</b></td>
</tr>
END
;
}
if ($pppsettings{'TYPE'} =~ /^(alcatelusb|alcatelusbk|amedynusbadsl|conexantusbadsl|conexantpciadsl|3cp4218usbadsl|pulsardsl|eciadsl|fritzdsl|bewanadsl|eagleusbadsl)$/)
{

print <<END
</table>
<table width='100%'>
<tr>
	<td colspan='5'><br /><hr /><b>$Lang::tr{'adsl settings'}:</b></td>
</tr>
<tr>
	<td nowrap='nowrap' align='right'>$Lang::tr{'vpi number'}</td>
	<td><input type='text' size='5' name='VPI' value='$pppsettings{'VPI'}' /></td>
	<td align='right'>$Lang::tr{'vci number'}</td>
	<td colspan='2'><input type='text' size='5' name='VCI' value='$pppsettings{'VCI'}' /></td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td colspan='4'><hr /></td>
</tr>
END
;
}
if ($pppsettings{'TYPE'} eq 'bewanadsl')
{
print <<END
<tr>
	<td align='right'>$Lang::tr{'modem'}:</td>
	<td colspan='2' nowrap='nowrap'>
		<input type='radio' name='MODEM' value='PCIST' $checked{'MODEM'}{'PCIST'} />Bewan ADSL PCI st</td>
	<td colspan='2'><input type='radio' name='MODEM' value='USB' $checked{'MODEM'}{'USB'} />Bewan ADSL USB st</td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td colspan='4'><hr /></td>
</tr>
END
;
}
if ($pppsettings{'TYPE'} =~ /^(3cp4218usbadsl|bewanadsl)$/)
{
print <<END
<tr>
	<td align='right'>$Lang::tr{'modulation'}:</td>
	<td><input type='radio' name='MODULATION' value='AUTO' $checked{'MODULATION'}{'AUTO'} />$Lang::tr{'automatic'}</td>
	<td><input type='radio' name='MODULATION' value='ANSI' $checked{'MODULATION'}{'ANSI'} />ANSI T1.483</td>
	<td><input type='radio' name='MODULATION' value='GDMT' $checked{'MODULATION'}{'GDMT'} />G.DMT</td>
	<td><input type='radio' name='MODULATION' value='GLITE' $checked{'MODULATION'}{'GLITE'} />G.Lite</td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td colspan='4'><hr /></td>
</tr>
END
;
}

if ($pppsettings{'TYPE'} eq 'eagleusbadsl')
{
print <<END
<tr>
	<td align='right'>$Lang::tr{'country'}:</td>
	<td>
	<select name='LINE'>
	<option value='WO' $selected{'LINE'}{'WO'}>$Lang::tr{'other countries'}</option>
	<option value='ES' $selected{'LINE'}{'ES'}>ESPANA</option>
	<option value='ES03' $selected{'LINE'}{'ES03'}>ESPANA03</option>
	<option value='FR' $selected{'LINE'}{'FR'}>FRANCE</option>
	<option value='FR04' $selected{'LINE'}{'FR04'}>FRANCE04</option>
	<option value='FR10' $selected{'LINE'}{'FR04'}>FRANCE10</option>
	<option value='IT' $selected{'LINE'}{'IT'}>ITALIA</option>
	</select></td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td colspan='4'><hr /></td>
</tr>
END
;
}
if ($pppsettings{'TYPE'} eq 'eciadsl')
{
print <<END
<tr>
	<td align='right'>$Lang::tr{'modem'}:</td>
	<td colspan='5'>
		<select name='MODEM'>
END
;
		open (MODEMS, "/etc/eciadsl/modems.db") or die 'Unable to open modems database.';
		while (my $line = <MODEMS>) {
			$line =~ /^([\S\ ]+).*$/;
			my $modem = $1;
			$modem =~ s/^\s*(.*?)\s*$/$1/;
			print "<option value='$modem'";
			if ($pppsettings{'MODEM'} =~ /$modem/) { print " selected";}
			print ">$modem</option>\n";
		}
		close (MODEMS);

print <<END
		</select>
	</td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td colspan='4'><hr /></td>
</tr>
END
;
}
if ($pppsettings{'TYPE'} =~ /^(alcatelusb|alcatelusbk|amedynusbadsl|conexantusbadsl|conexantpciadsl|3cp4218usbadsl|pulsardsl|eciadsl|fritzdsl|bewanadsl|eagleusbadsl)$/)
{
print <<END
<tr>
	<td valign='top' align='right'>$Lang::tr{'protocol'}:</td>
	<td nowrap='nowrap'>
		<input type='radio' name='PROTOCOL' value='RFC2364' $checked{'PROTOCOL'}{'RFC2364'} />RFC2364 PPPoA</td>
END
;
}
if ($pppsettings{'TYPE'} eq 'alcatelusb')
{
	print "<td colspan=3>&nbsp;</td></tr>";
}

if ($pppsettings{'TYPE'} =~ /^(alcatelusbk|amedynusbadsl|conexantusbadsl|conexantpciadsl|3cp4218usbadsl|pulsardsl|eciadsl|bewanadsl|eagleusbadsl|fritzdsl)$/)
{
print <<END
	<td align='right'>$Lang::tr{'encapsulation'}:</td>
	<td colspan='2' width='30%'>
		<select name='ENCAP_RFC2364'>
		<option value='0' $selected{'ENCAP'}{'0'}>VCmux</option>
		<option value='1' $selected{'ENCAP'}{'1'}>LLC</option>
		</select>
	</td>
</tr>
END
;
}
if ($pppsettings{'TYPE'} =~ /^(alcatelusb|alcatelusbk|amedynusbadsl|conexantusbadsl|conexantpciadsl|3cp4218usbadsl|pulsardsl|eciadsl|fritzdsl|bewanadsl|eagleusbadsl)$/)
{
print <<END
<tr>
	<td>&nbsp;</td>
	<td colspan='4'><hr /></td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td valign='top'>
		<input type='radio' name='PROTOCOL' value='RFC1483' $checked{'PROTOCOL'}{'RFC1483'} />RFC 1483 / 2684</td>
END
;
}
if ($pppsettings{'TYPE'} eq 'alcatelusb')
{
	print "<td colspan='3'>&nbsp;</td></tr>";
}

if ($pppsettings{'TYPE'} =~ /^(alcatelusbk|amedynusbadsl|conexantusbadsl|conexantpciadsl|3cp4218usbadsl|pulsardsl|eciadsl|bewanadsl|eagleusbadsl|fritzdsl)$/)
{
	if ($pppsettings{'TYPE'} ne 'fritzdsl')
	{
print <<END
	<td align='right'>$Lang::tr{'encapsulation'}:</td>
	<td colspan='2'>
		<select name='ENCAP_RFC1483'>
		<option value='0' $selected{'ENCAP'}{'0'}>BRIDGED_ETH_LLC</option>
		<option value='1' $selected{'ENCAP'}{'1'}>BRIDGED_ETH_VC</option>
		<option value='2' $selected{'ENCAP'}{'2'}>ROUTED_IP_LLC</option>
		<option value='3' $selected{'ENCAP'}{'3'}>ROUTED_IP_VC</option>
		</select>
	</td>
</tr>
<tr>
	<td colspan='2'>&nbsp;</td>
	<td colspan='3'><hr /></td>
</tr>
END
;
	} else {
print <<END
	<td colspan='4'>PPPoE</td>
</tr>
END
;
	}
}
if ($pppsettings{'TYPE'} =~ /^(pppoe|alcatelusb|alcatelusbk|amedynusbadsl|conexantusbadsl|conexantpciadsl|3cp4218usbadsl|pulsardsl|eciadsl|bewanadsl|eagleusbadsl)$/)
{
print <<END
<tr>
	<td>&nbsp;</td>
	<td>&nbsp;</td>
	<td><input type='radio' name='METHOD' value='PPPOE_PLUGIN' $checked{'METHOD'}{'PPPOE_PLUGIN'} />PPPoE plugin</td>
	<td align='right'>$Lang::tr{'service name'}&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td><input type='text' name='SERVICENAME' value='$pppsettings{'SERVICENAME'}' /></td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td>&nbsp;</td>
	<td><input type='radio' name='METHOD' value='PPPOE' $checked{'METHOD'}{'PPPOE'} />$Lang::tr{'pppoe'}</td>
	<td align='right'>$Lang::tr{'concentrator name'}&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td><input type='text' name='CONCENTRATORNAME' value='$pppsettings{'CONCENTRATORNAME'}' /></td>
</tr>

END
;
}
if ($pppsettings{'TYPE'} =~ /^(alcatelusbk|amedynusbadsl|conexantusbadsl|conexantpciadsl|3cp4218usbadsl|pulsardsl|eciadsl|bewanadsl|eagleusbadsl)$/)
{
print <<END
<tr>
	<td colspan='2'>&nbsp;</td>
	<td colspan='3'><hr /></td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td>&nbsp;</td>
	<td rowspan='4'><input type='radio' name='METHOD' value='STATIC' $checked{'METHOD'}{'STATIC'} />$Lang::tr{'static ip'}</td>
	<td align='right'>$Lang::tr{'static ip'}:</td>
	<td><input type='text' size='16' name='IP' value='$pppsettings{'IP'}' /></td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td>&nbsp;</td>
	<td align='right'>$Lang::tr{'gateway ip'}:</td>
	<td><input type='text' size='16' name='GATEWAY' value='$pppsettings{'GATEWAY'}' /></td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td>&nbsp;</td>
	<td align='right'>$Lang::tr{'netmask'}:</td>
	<td><input type='text' size='16' name='NETMASK' value='$pppsettings{'NETMASK'}' /></td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td>&nbsp;</td>
	<td align='right' nowrap='nowrap'>$Lang::tr{'broadcast'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td><input type='text' size='16' name='BROADCAST' value='$pppsettings{'BROADCAST'}' /></td>
</tr>
END
;
	if ($pppsettings{'TYPE'} =~ /^(eciadsl|eagleusbadsl)$/)
	{
print <<END
<tr>
	<td colspan='2'>&nbsp;</td>
	<td colspan='3'><hr /></td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td>&nbsp;</td>
	<td><input type='radio' name='METHOD' value='DHCP' $checked{'METHOD'}{'DHCP'} />$Lang::tr{'dhcp mode'}</td>
	<td align='right'>$Lang::tr{'hostname'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td><input type='text' name='DHCP_HOSTNAME' value='$pppsettings{'DHCP_HOSTNAME'}' /></td>
</tr>
END
;
	}
}
if ($pppsettings{'TYPE'} =~ /^(alcatelusb|alcatelusbk|eciadsl|fritzdsl)$/) {
	print "<tr><td>&nbsp;</td><td colspan='4'><hr /></td></tr>";
}
if ($pppsettings{'TYPE'} =~ /^(alcatelusb|alcatelusbk)$/) {
	my $speedtouch = &Header::speedtouchversion;
	if (($speedtouch >= 0) && ($speedtouch <=4)) {
		my $modem;
		if ($speedtouch ==4) { $modem='v4_b'; } else { $modem='v0123'; }
		print "<tr><td align='right'>$Lang::tr{'firmware'}:</td>";
		if (-e "${General::swroot}/alcatelusb/firmware.$modem.bin") {
			print "<td>$Lang::tr{'present'}</td><td colspan='3'>&nbsp;</td></tr>\n";
		} else {
			print "<td>$Lang::tr{'not present'}</td><td colspan='3'>&nbsp;</td></tr>\n";
		}
	} else {
		print "<tr><td colspan='5'>$Lang::tr{'unknown'} Rev $speedtouch</td></tr>";
	}
} elsif ($pppsettings{'TYPE'} eq 'eciadsl') {
	print "<tr><td align='right'>$Lang::tr{'driver'}:</td>";
	if (-e "${General::swroot}/eciadsl/synch.bin") {
		print "<td>$Lang::tr{'present'}</td><td colspan='3'>&nbsp;</td></tr>\n";
	} else {
		print "<td>$Lang::tr{'not present'}</td><td colspan='3'>&nbsp;</td></tr>\n"; }
} elsif ($pppsettings{'TYPE'} eq 'fritzdsl') {
	print "<tr><td align='right'>$Lang::tr{'driver'}:</td>";
	if (-e "/lib/modules/$kernel/misc/fcdslusb.o.gz") {
		print "<td>$Lang::tr{'present'}</td><td colspan='3'>&nbsp;</td></tr>\n";
	} else {
		print "<td>$Lang::tr{'not present'}</td><td colspan='3'>&nbsp;</td></tr>\n"; }
}
print <<END
</table>
<table width='100%'>
<tr>
	<td colspan='5'><br /><hr /><b>$Lang::tr{'authentication'}</b></td>
</tr>
<tr>
	<td align='right'>$Lang::tr{'username'}</td>
	<td><input type='text' name='USERNAME' value='$pppsettings{'USERNAME'}' /></td>
	<td align='right'>$Lang::tr{'password'}</td>
	<td><input type='password' name='PASSWORD' value='$pppsettings{'PASSWORD'}' /></td>
</tr>
<tr>
	<td align='right'>$Lang::tr{'method'}</td>
	<td><select name='AUTH'>
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
	<td align='right'>$Lang::tr{'script name'}&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td nowrap='nowrap'><input type='text' name='LOGINSCRIPT' value='$pppsettings{'LOGINSCRIPT'}' /></td>
</tr>
</table>
<table width='100%'>
<tr>
	<td colspan='5'><br /><hr /><b>DNS:</b></td>
</tr>
<tr>
	<td colspan='5'><input type='radio' name='DNS' value='Automatic' $checked{'DNS'}{'Automatic'} />$Lang::tr{'automatic'}</td>
</tr>
<tr>
	<td><input type='radio' name='DNS' value='Manual' $checked{'DNS'}{'Manual'} />$Lang::tr{'manual'}</td>
	<td align='right'>$Lang::tr{'primary dns'}</td>
	<td><input type='text' size='16' name='DNS1' value='$pppsettings{'DNS1'}' /></td>
	<td align='right'>$Lang::tr{'secondary dns'}</td>
	<td><input type='text' size='16' name='DNS2' value='$pppsettings{'DNS2'}' /></td>
</tr>
<tr>
	<td colspan='5'><br /><hr /></td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td align='right'>$Lang::tr{'profile name'}</td>
	<td><input type='text' name='PROFILENAME' value='$pppsettings{'PROFILENAME'}' /></td>
	<td><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
</tr>
<tr>
	<td colspan='5'><br /><hr /></td>
</tr>
<tr>
	<td align='right'>$Lang::tr{'legend'}:</td>
	<td><img src='/blob.gif' alt='*' />&nbsp;$Lang::tr{'this field may be blank'}</td>
</tr>
</table>
END
;
&Header::closebox();
}

print "</form>\n";

&Header::closebigbox();

&Header::closepage();

sub updatesettings
{
	# make a link from the selected profile to the "default" one.
	unlink("${General::swroot}/ppp/settings");
	link("${General::swroot}/ppp/settings-$pppsettings{'PROFILE'}",
		"${General::swroot}/ppp/settings");
	system ("/bin/touch", "${General::swroot}/ppp/updatesettings");
	if ($pppsettings{'TYPE'} eq 'eagleusbadsl') {
		# eagle-usb.conf is in backup but link DSPcode.bin can't, so the link is created in rc.eagleusbadsl
		open(FILE, ">/${General::swroot}/eagle-usb/eagle-usb.conf") or die "Unable to write eagle-usb.conf file";
		flock(FILE, 2);
		# decimal to hexa
		$modemsettings{'VPI'} = uc(sprintf('%X', $pppsettings{'VPI'}));
		$modemsettings{'VCI'} = uc(sprintf('%X', $pppsettings{'VCI'}));
		if( $pppsettings{'PROTOCOL'} eq 'RFC1483') {
			$modemsettings{'Encapsulation'} =1+$pppsettings{'ENCAP'}
		} elsif ( $pppsettings{'PROTOCOL'} eq 'RFC2364') {
			$modemsettings{'Encapsulation'} =6-$pppsettings{'ENCAP'}
		}
		print FILE "<eaglectrl>\n";
		print FILE "VPI=$modemsettings{'VPI'}\n";
		print FILE "VCI=$modemsettings{'VCI'}\n";
		print FILE "Encapsulation=$modemsettings{'Encapsulation'}\n";
		print FILE "Linetype=0A\n";
		print FILE "RatePollFreq=00000009\n";
		print FILE "</eaglectrl>\n";
		close FILE;
	}
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
	$pppsettings{'DTERATE'} = 115200;
	$pppsettings{'SPEAKER'} = 'off';
	$pppsettings{'RECONNECTION'} = 'manual';
	$pppsettings{'DIALONDEMANDDNS'} = 'off';
	$pppsettings{'AUTOCONNECT'} = 'off';
	$pppsettings{'SENDCR'} = 'off';
	$pppsettings{'USEIBOD'} = 'off';
	$pppsettings{'USEDOV'} = 'off';
	$pppsettings{'MODEM'} = 'PCIST';
	$pppsettings{'LINE'} = 'WO';
	$pppsettings{'ENCAP'} = '0';
	$pppsettings{'PHONEBOOK'} = 'RELAY_PPP1';
	$pppsettings{'PROTOCOL'} = 'RFC2364';
	$pppsettings{'METHOD'} = 'PPPOE_PLUGIN';
	$pppsettings{'DIALMODE'} = 'T';
	$pppsettings{'MAXRETRIES'} = 5;
	$pppsettings{'HOLDOFF'} = 30;
	$pppsettings{'TIMEOUT'} = 15;
	$pppsettings{'MODULATION'} = 'AUTO';
	$pppsettings{'AUTH'} = 'pap-or-chap';
	$pppsettings{'DNS'} = 'Automatic';
	$pppsettings{'DEBUG'} = 'off';
	$pppsettings{'BACKUPPROFILE'} = $pppsettings{'PROFILE'};

	# Get ISDN settings so we can see if ISDN is enabled or not.
	$isdnsettings{'ENABLED'} = 'off';
	&General::readhash("${General::swroot}/isdn/settings", \%isdnsettings);
	
	# Get PPPoE settings so we can see if PPPoE is enabled or not.
	&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

	# empty profile partial pre-initialization
	if ($netsettings{'CONFIG_TYPE'} =~ /^(2|3|6|7)$/) {
		$pppsettings{'TYPE'}=lc($netsettings{'RED_TYPE'});
	} elsif ($isdnsettings{'ENABLED'} eq 'on') {
		$pppsettings{'TYPE'}='isdn';
	} else {
		$pppsettings{'TYPE'}='modem';
	}
}

