#!/usr/bin/perl
#
# IPFire CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The IPFire Team
#

use strict;
# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %qossettings=();
my %checked=();
my %netsettings=();
my $errormessage = "";
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

&Header::showhttpheaders();

$qossettings{'ACTION'} = '';
$qossettings{'ACTION_BW'} = '';
$qossettings{'ENABLED'} = '';
$qossettings{'OUT_SPD'} = '';
$qossettings{'INC_SPD'} = '';
$qossettings{'RED_DEV'} = `cat /var/ipfire/red/iface`;
$qossettings{'IMQ_DEV'} = 'imq0';

&General::readhash("${General::swroot}/qos/settings", \%qossettings);
&Header::getcgihash(\%qossettings);

&Header::openpage('QoS', 1, '');

&Header::openbigbox('100%', 'left', '', $errormessage);


if ($qossettings{'ACTION'} eq 'Start')
{
	system("/bin/touch /var/ipfire/qos/enable");
	$qossettings{'ENABLED'} = 'on';
	&General::writehash("${General::swroot}/qos/settings", \%qossettings);
}
elsif ($qossettings{'ACTION'} eq 'Stop')
{
	unlink "/var/ipfire/qos/enable";
	$qossettings{'ENABLED'} = 'off';
	&General::writehash("${General::swroot}/qos/settings", \%qossettings);
}
elsif ($qossettings{'ACTION'} eq $Lang::tr{'save'})
{
	&General::writehash("${General::swroot}/qos/settings", \%qossettings);
}
if ($qossettings{'ACTION_BW'} eq 'Andern')
{
	&Header::openbox('100%', 'center', 'Bandbreiteneinstellungen');
	if ($qossettings{'ENABLED'} eq 'on') {
	print "Sie koennen die Bandbreiteneinstellungen nicht bearbeiten, wenn QoS eingeschaltet ist. Schalten sie es zuerst dazu aus.<p>";
	print "<a href='/cgi-bin/qos.cgi'>Zurueck</a>";
	} else {
	print <<END
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table width='66%'>
	<tr><td width='100%' colspan='3'>Geben Sie bitte hier ihre Download- bzw. Upload-Geschwindigkeit ein <br> und klicken Sie danach auf <i>Speichern</i>.
	<tr><td width='33%' align='right'>Download-Geschwindigkeit:<td width='33%' align='left'><input type='text' name='INC_SPD' maxlength='8' value=$qossettings{'INC_SPD'}> &nbsp; kbps<td width='33%' align='center'>&nbsp;
	<tr><td width='33%' align='right'>Upload-Geschwindigkeit:<td width='33%' align='left'><input type='text' name='OUT_SPD' maxlength='8'value=$qossettings{'OUT_SPD'}> &nbsp; kbps<td width='33%' align='center'><input type='submit' name='ACTION' value=$Lang::tr{'save'} />
	</table>
	</form>
END
;
	}
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit
}

&General::readhash("${General::swroot}/qos/settings", \%qossettings);

my $status = $Lang::tr{'stopped'};
my $statuscolor = $Header::colourred;
if ( $qossettings{'ENABLED'} eq 'on' ) {
  $status = $Lang::tr{'running'};
  $statuscolor = $Header::colourgreen;
}

if ( $netsettings{'RED_TYPE'} ne 'PPPOE' ) {
	$qossettings{'RED_DEV'} = $netsettings{'RED_DEV'};
}

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
}

&Header::openbox('100%', 'center', 'Quality of Service');
print <<END
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table width='33%'>
		<tr><td width='50%' align='left'><b>Quality of Service:</b>
		    <td width='50%' align='center' bgcolor='$statuscolor'><font color='white'>$status</font>
		<tr><td width='100%' align='center' colspan='2'>	<input type='submit' name='ACTION' value='Start' /> 
										<input type='submit' name='ACTION' value='Stop' /> 
										<input type='submit' name='ACTION' value='$Lang::tr{'restart'}' />
END
;
	if (($qossettings{'OUT_SPD'} ne '') && ($qossettings{'INC_SPD'} ne '')) {
		print <<END
		<tr><td colspan='3'>&nbsp;
		<tr><td width='40%' align='right'>Downloadgeschwindigkeit: 	<td width='40%' align='left'>$qossettings{'INC_SPD'}	<td width='20%' rowspan='2' align='center' valign='middle'><input type='submit' name='ACTION_BW' value='Andern'>
		<tr><td width='40%' align='right'>Uploadgeschwindigkeit: 	<td width='40%' align='left'>$qossettings{'OUT_SPD'}

END
;
	}
print "</table>";
&Header::closebox();

if ( ($qossettings{'OUT_SPD'} eq '') || ($qossettings{'INC_SPD'} eq '') ) {
&Header::openbox('100%', 'center', "Outgoing ($qossettings{'RED_DEV'})");
print <<END
	<table width='66%'>
	<tr><td width='100%' colspan='3'>Geben Sie bitte hier ihre Download- bzw. Upload-Geschwindigkeit ein <br> und klicken Sie danach auf <i>Speichern</i>.
	<tr><td width='33%' align='right'>Download-Geschwindigkeit:<td width='33%' align='left'><input type='text' name='INC_SPD' maxlength='8'> &nbsp; kbps<td width='33%' align='center'>&nbsp;
	<tr><td width='33%' align='right'>Upload-Geschwindigkeit:<td width='33%' align='left'><input type='text' name='OUT_SPD' maxlength='8'> &nbsp; kbps<td width='33%' align='center'><input type='submit' name='ACTION' value=$Lang::tr{'save'} />
	</table>
	</form>
END
;
&Header::closebox();
&Header::closebigbox();
&Header::closepage();
exit
}

if ( $qossettings{'RED_DEV'} ne '' ) {
	&Header::openbox('100%', 'center', 'Outgoing Interface');
	print <<END
	<table border='0' width='100%' cellspacing='0'>
	<tr><td bgcolor='lightgrey' width='20%'>Interface<td bgcolor='lightgrey' width='20%'>Klasse<td bgcolor='lightgrey' width='20%'>Maximale Geschwindigkeit<td bgcolor='lightgrey' width='40%'>Aktionen
	<tr><td bgcolor='black' height='2px' colspan='4'>
	<tr><td>ppp0<td>198<td>512<td>BLA
	<tr><td bgcolor='lightgrey'>ppp0<td bgcolor='lightgrey'>199<td bgcolor='lightgrey'>512<td bgcolor='lightgrey'>BLA
	</table>
END
;
	&Header::closebox();
} else {
	&Header::openbox('100%', 'center', 'Outgoing Interface');
	print "Es ist kein rotes Interface vorhanden.";
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit
}

&Header::closebigbox();
&Header::closepage();

