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

my %qossettings = ();
my %checked = ();
my %netsettings = ();
my $errormessage = "";
my $c = "";
my $direntry = "";
my @proto = ();
my %selected= () ;
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

&Header::showhttpheaders();

$qossettings{'ENABLED'} = 'off';
$qossettings{'OUT_SPD'} = '';
$qossettings{'INC_SPD'} = '';
$qossettings{'DEFCLASS_INC'} = '';
$qossettings{'DEFCLASS_OUT'} = '';
$qossettings{'ACK'} = '';
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
elsif ($qossettings{'ACTION'} eq 'Parentklasse hinzufuegen')
{
	&parentclass();
	&Header::closebigbox();
	&Header::closepage();
	exit
}
elsif ($qossettings{'ACTION'} eq 'Level7-Regel hinzufuegen')
{
	&level7rule();
	&Header::closebigbox();
	&Header::closepage();
	exit
}
if ($qossettings{'ACTION_BW'} eq 'Andern')
{
	&changebandwidth();
	&Header::closebigbox();
	&Header::closepage();
	exit
}
if ($qossettings{'ACTION_DEF'} eq 'Andern')
{
	&changedefclasses();
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
		<tr><td width='100%' align='center' colspan='2'>
		<input type='submit' name='ACTION' value='Start' /> 
		<input type='submit' name='ACTION' value='Stop' /> 
		<input type='submit' name='ACTION' value='$Lang::tr{'restart'}' />
END
;
	if (($qossettings{'OUT_SPD'} ne '') && ($qossettings{'INC_SPD'} ne '')) {
		print <<END
		<tr><td colspan='3'>&nbsp;
		<tr><td width='40%' align='right'>Downloadgeschwindigkeit: 	<td width='40%' align='left'>$qossettings{'INC_SPD'} kbps
		    <td width='20%' rowspan='2' align='center' valign='middle'><input type='submit' name='ACTION_BW' value='Andern'>
		<tr><td width='40%' align='right'>Uploadgeschwindigkeit: 	<td width='40%' align='left'>$qossettings{'OUT_SPD'} kbps
END
;
	}
	if (($qossettings{'DEFCLASS_OUT'} ne '') && ($qossettings{'DEFCLASS_INC'} ne '')&& ($qossettings{'ACK'} ne '')) {
		print <<END
		<tr><td colspan='3'><hr>
		<tr><td width='40%' align='right'>Downloadstandardklasse: 	<td width='40%' align='left'>$qossettings{'DEFCLASS_INC'}	
		    <td width='20%' rowspan='3' align='center' valign='middle'><input type='submit' name='ACTION_DEF' value='Andern'>
		<tr><td width='40%' align='right'>Uploadstandardklasse: 	<td width='40%' align='left'>$qossettings{'DEFCLASS_OUT'}
		<tr><td width='40%' align='right'>ACKs:				<td width='40%' align='left'>$qossettings{'ACK'}
		<tr><td colspan='3' width='100%'><hr>
		<tr><td colspan='3' width='100%' align='center'><input type='submit' name='ACTION' value='Parentklasse hinzufuegen'>
		<tr><td colspan='3' width='100%' align='center'>Nur temporaer >>> <input type='submit' name='ACTION' value='Level7-Regel hinzufuegen'> <<<
END
;
	}
print "</table>";
&Header::closebox();

if ( ($qossettings{'OUT_SPD'} eq '') || ($qossettings{'INC_SPD'} eq '') ) {
	&changebandwidth();
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit
}

if ( ($qossettings{'DEFCLASS_INC'} eq '') || ($qossettings{'DEFCLASS_OUT'} eq '') || ($qossettings{'ACK'} eq '') ) {
	&changedefclasses();
	&Header::closebigbox();
	&Header::closepage();
	exit
}


#	&Header::openbox('100%', 'center', 'Outgoing Interface');
#	print <<END
#	<table border='0' width='100%' cellspacing='0'>
#	<tr><td bgcolor='lightgrey' width='20%'>Interface<td bgcolor='lightgrey' width='20%'>Klasse<td bgcolor='lightgrey' width='20%'>Maximale Geschwindigkeit<td bgcolor='lightgrey' width='40%'>Aktionen
#	</table>
#END
#;
#	&Header::closebox();

&Header::closebigbox();
&Header::closepage();

# ---------------------------------------------------------------------------------------------------------------------------------

sub changedefclasses {
	&Header::openbox('100%', 'center', 'Standardklassen:');
	print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='66%'>
		<tr><td width='100%' colspan='3'>Legen sie hier die Standardklassen fest durch die nicht-gefilterte Pakete gehen.
		<tr><td width='33%' align='right'>Download:<td width='33%' align='left'><select name='DEFCLASS_INC'>
END
;
		for ( $c = 100 ; $c <= 120 ; $c++ )
		{
			if ( $qossettings{'DEFCLASS_INC'} ne $c )
			{
 					print "<option value='$c'>$c</option>\n";
			}
			else
			{
  				print "<option selected value='$c'>$c</option>\n";			
			}
		}
		print <<END
		</select><td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Upload:<td width='33%' align='left'><select name='DEFCLASS_OUT'>
END
;
		for ( $c = 200 ; $c <= 220 ; $c++ )
		{
			if ( $qossettings{'DEFCLASS_OUT'} ne $c )
			{
  				print "<option value='$c'>$c</option>\n";
			}
			else
			{
  				print "<option selected value='$c'>$c</option>\n";			
			}
		}
		print <<END
		</select><td width='33%' align='center'>&nbsp;
		</table>
		<hr>
		<table width='66%'>
		<tr><td width='100%' colspan='3'>Legen sie hier die ACK-Klasse fest <br> und klicken Sie danach auf <i>Speichern</i>.
		<tr><td width='33%' align='right'>ACKs:<td width='33%' align='left'><select name='ACK'>
END
;
		for ( $c = 200 ; $c <= 220 ; $c++ )
		{
			if ( $qossettings{'ACK'} ne $c )
			{
  				print "<option value='$c'>$c</option>\n";
			}
			else
			{
  				print "<option selected value='$c'>$c</option>\n";			
			}
		}
		print <<END
		</select><td width='33%' align='center'><input type='submit' name='ACTION' value=$Lang::tr{'save'} />
		</table>
		</form>
END
;
	&Header::closebox();
}

sub changebandwidth {
	&Header::openbox('100%', 'center', 'Bandbreiteneinstellungen');
	if ($qossettings{'ENABLED'} eq 'on') {
		print "Sie koennen die Bandbreiteneinstellungen nicht bearbeiten, wenn QoS eingeschaltet ist. Schalten sie es zuerst dazu aus.<p>";
		print "<a href='/cgi-bin/qos.cgi'>Zurueck</a>";
	} else {
		print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='66%'>
		<tr><td width='100%' colspan='3'>Geben Sie bitte hier ihre Download- bzw. Upload-Geschwindigkeit ein <br> und klicken Sie danach auf <i>Speichern</i>.
		<tr><td width='33%' align='right'>Download-Geschwindigkeit:
		    <td width='33%' align='left'><input type='text' name='INC_SPD' maxlength='8' value=$qossettings{'INC_SPD'}> &nbsp; kbps
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Upload-Geschwindigkeit:
		    <td width='33%' align='left'><input type='text' name='OUT_SPD' maxlength='8' value=$qossettings{'OUT_SPD'}> &nbsp; kbps
		    <td width='33%' align='center'><input type='submit' name='ACTION' value=$Lang::tr{'save'} />&nbsp;<input type='reset' name='ACTION' value=$Lang::tr{'reset'} />
		</table>
		</form>
END
;
	}
	&Header::closebox();
}

sub parentclass {
	&Header::openbox('100%', 'center', 'Parentklasse hinzufuegen');
	print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='66%'>
		<tr><td width='100%' colspan='3'>Geben sie die Daten ein <br> und klicken Sie danach auf <i>Speichern</i>.
		<tr><td width='33%' align='right'>Interface:
		    <td width='33%' align='left'><select name='CLASS'>
							<option value=$qossettings{'RED_DEV'}>$qossettings{'RED_DEV'}</option>
							<option value=$qossettings{'IMQ_DEV'}>$qossettings{'IMQ_DEV'}</option></select>
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Klasse:<td width='33%' align='left'><select name='CLASS'>
END
;
		for ( $c = 100 ; $c <= 120 ; $c++ )
		{
			if ( $qossettings{'CLASS'} ne $c )
			{
  				print "<option value='$c'>$c</option>\n";
			}
			else
			{
  				print "<option selected value='$c'>$c</option>\n";			
			}
		}
		for ( $c = 200 ; $c <= 220 ; $c++ )
		{
			if ( $qossettings{'CLASS'} ne $c )
			{
  				print "<option value='$c'>$c</option>\n";
			}
			else
			{
  				print "<option selected value='$c'>$c</option>\n";			
			}
		}
		print <<END
		</select>
		<td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Prioritaet:<td width='33%' align='left'><select name='PRIO'>
END
;
		for ( $c = 1 ; $c <= 7 ; $c++ )
		{
			if ( $qossettings{'PRIO'} ne $c )
			{
  				print "<option value='$c'>$c</option>\n";
			}
			else
			{
  				print "<option selected value='$c'>$c</option>\n";			
			}
		}
		print <<END
		<td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Garantierte Bandbreite:
		    <td width='33%' align='left'><input type='text' name='MINBDWTH' maxlength='8' value=$qossettings{'MINBWDTH'}>
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Maximale Bandbreite:
		    <td width='33%' align='left'><input type='text' name='MAXBDWTH' maxlength='8' value=$qossettings{'MAXBWDTH'}>
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Burst:
		    <td width='33%' align='left'><input type='text' name='BURST' maxlength='8' value=$qossettings{'BURST'}>
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Ceilburst:
		    <td width='33%' align='left'><input type='text' name='CBURST' maxlength='8' value=$qossettings{'CBURST'}>
		    <td width='33%' align='center'><input type='submit' name='ACTION' value=$Lang::tr{'save'} />
		</table></form>
END
;
	&Header::closebox();
}

sub level7rule {
	&Header::openbox('100%', 'center', 'Level7-Regel hinzufuegen');
	print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='66%'>
		<tr><td width='100%' colspan='3'>Geben sie die Daten ein <br> und klicken Sie danach auf <i>Speichern</i>.
		<tr><td width='33%' align='right'>Name:
		    <td width='33%' align='left'><input type='text' name='NAME' maxlength='20' value=$qossettings{'NAME'}>
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Protokoll:
		    <td width='33%' align='left'><select name='L7PROT'>
END
;
		opendir( DIR, "/etc/l7-protocols/protocols" );
		foreach $direntry ( sort readdir(DIR) )
		{
			next if $direntry eq ".";
			next if $direntry eq "..";
			next if -d "/etc/l7-protocols/protocols/$direntry";
			@proto = split( /\./, $direntry );
			if ( $proto[0] eq $qossettings{'L7PROT'} ) {
				print "<option value='$proto[0]' selected>$proto[0]</option>\n";			
			} else {
				print "<option value='$proto[0]'>$proto[0]</option>\n";
			}
		}
		closedir DIR;
	print <<END
		    </select><td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Quell-IP-Adresse:
		    <td width='33%' align='left'><input type='text' name='QIP' maxlength='15' value=$qossettings{'QIP'}>
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Ziel-IP-Adresse:
		    <td width='33%' align='left'><input type='text' name='DIP' maxlength='15' value=$qossettings{'DIP'}>
		    <td width='33%' align='center'><input type='submit' name='ACTION' value=$Lang::tr{'save'} />
		</table></form>
END
;
	&Header::closebox();
}