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
my $message = "";
my $errormessage = "";
my $c = "";
my $direntry = "";
my $classentry = "";
my $subclassentry = "";
my $l7ruleentry = "";
my $portruleentry = "";
my @tmp = ();
my @classes = ();
my @subclasses = ();
my @l7rules = ();
my @portrules = ();
my @tmpline = ();
my @classline = ();
my @subclassline = ();
my @l7ruleline = ();
my @portruleline = ();
my @proto = ();
my %selected= () ;
my $classfile = "/var/ipfire/qos/classes";
my $subclassfile = "/var/ipfire/qos/subclasses";
my $level7file = "/var/ipfire/qos/level7config";
my $portfile = "/var/ipfire/qos/portconfig";
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

&Header::showhttpheaders();

$qossettings{'ENABLED'} = 'off';
$qossettings{'EDIT'} = 'no';
$qossettings{'OUT_SPD'} = '';
$qossettings{'INC_SPD'} = '';
$qossettings{'DEF_OUT_SPD'} = '';
$qossettings{'DEF_INC_SPD'} = '';
$qossettings{'DEFCLASS_INC'} = '';
$qossettings{'DEFCLASS_OUT'} = '';
$qossettings{'ACK'} = '';
$qossettings{'MTU'} = '1492';
$qossettings{'SFQ_PERTUB'} = '10';
$qossettings{'QLENGTH'} = '30';
$qossettings{'RED_DEV'} = `cat /var/ipfire/red/iface`;
$qossettings{'IMQ_DEV'} = 'imq0';
$qossettings{'VALID'} = 'yes';
### Values that have to be initialized
$qossettings{'ACTION'} = '';
$qossettings{'ACTIONDEF'} = '';
$qossettings{'ACTIONBW'} = '';
$qossettings{'PRIO'} = '';
$qossettings{'SPD'} = '';
$qossettings{'CLASS'} = '';
$qossettings{'SCLASS'} = '';
$qossettings{'QPORT'} = '';
$qossettings{'DPORT'} = '';
$qossettings{'QIP'} = '';
$qossettings{'DIP'} = '';
$qossettings{'PPROT'} = '';
$qossettings{'L7PROT'} = '';
$qossettings{'DEVICE'} = '';
$qossettings{'MINBWDTH'} = '';
$qossettings{'MAXBWDTH'} = '';
$qossettings{'BURST'} = '';
$qossettings{'CBURST'} = '';
$qossettings{'DOCLASS'} = '';
$qossettings{'DOSCLASS'} = '';
$qossettings{'DOLEVEL7'} = '';
$qossettings{'DOPORT'} = '';


&General::readhash("${General::swroot}/qos/settings", \%qossettings);
&Header::getcgihash(\%qossettings);

&Header::openpage('QoS', 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
############################################################################################################################

if ($qossettings{'DOCLASS'} eq $Lang::tr{'save'})
{
	&validclass();
	&validminbwdth();
	&validmaxbwdth();
	if ( $qossettings{'VALID'} eq 'yes' ) {
		open( FILE, ">> $classfile" ) or die "Unable to write $classfile";
		print FILE <<END
$qossettings{'DEVICE'};$qossettings{'CLASS'};$qossettings{'PRIO'};$qossettings{'MINBWDTH'};$qossettings{'MAXBWDTH'};$qossettings{'BURST'};$qossettings{'CBURST'};
END
;
		close FILE;
	} else {
		$qossettings{'ACTION'} = 'Parentklasse hinzufuegen';
	}
}
elsif ($qossettings{'DOCLASS'} eq 'Bearbeiten')
{
	open( FILE, "< $classfile" ) or die "Unable to read $classfile";
	@classes = <FILE>;
	close FILE;
	open( FILE, "> $classfile" ) or die "Unable to write $classfile";
	foreach $classentry (sort @classes)
	{
		@classline = split( /\;/, $classentry );
		if ( $classline[1] ne $qossettings{'CLASS'} ) {
			print FILE $classentry;
		} else {
			$qossettings{'DEVICE'} = $classline[0];
			$qossettings{'PRIO'} = $classline[2];
			$qossettings{'MINBWDTH'} = $classline[3];
			$qossettings{'MAXBWDTH'} = $classline[4];
			$qossettings{'BURST'} = $classline[5];
			$qossettings{'CBURST'} = $classline[6];
			$qossettings{'EDIT'} = 'yes';
		}
	}
	close FILE;
	&parentclass();
	&Header::closebigbox();
	&Header::closepage();
	exit
}
elsif ($qossettings{'DOCLASS'} eq 'Loeschen')
{
	open( FILE, "< $classfile" ) or die "Unable to read $classfile";
	@tmp = <FILE>;
	close FILE;
	open( FILE, "> $classfile" ) or die "Unable to write $classfile";
	foreach $classentry (sort @tmp)
	{
		@tmpline = split( /\;/, $classentry );
		if ( $tmpline[1] ne $qossettings{'CLASS'} )
		{
			print FILE $classentry;
		}
	}
	close FILE;
	open( FILE, "< $subclassfile" ) or die "Unable to read $classfile";
	@tmp = <FILE>;
	close FILE;
	open( FILE, "> $subclassfile" ) or die "Unable to write $classfile";
	foreach $subclassentry (sort @tmp)
	{
		@tmpline = split( /\;/, $subclassentry );
		if ( $tmpline[1] ne $qossettings{'CLASS'} )
		{
			print FILE $subclassentry;
		}
	}
	close FILE;
	$message = "Klasse $qossettings{'CLASS'} wurde mit eventuell vorhandenen Unterklassen geloescht.";
}

############################################################################################################################
############################################################################################################################

if ($qossettings{'DOSCLASS'} eq $Lang::tr{'save'})
{
	if ($qossettings{'SCLASS'} >= 1000 && $qossettings{'CLASS'} < 1021) {
		$qossettings{'DEVICE'} = $qossettings{'RED_DEV'};
	} elsif ($qossettings{'SCLASS'} >= 2000 && $qossettings{'CLASS'} < 2021) {
		$qossettings{'DEVICE'} = $qossettings{'IMQ_DEV'};
	}
	&validsubclass();
	&validminbwdth();
	if ( $qossettings{'VALID'} eq 'yes' ) {
		open( FILE, ">> $subclassfile" ) or die "Unable to write $subclassfile";
		print FILE <<END
$qossettings{'DEVICE'};$qossettings{'CLASS'};$qossettings{'SCLASS'};$qossettings{'PRIO'};$qossettings{'MINBWDTH'};$qossettings{'MAXBWDTH'};$qossettings{'BURST'};$qossettings{'CBURST'};
END
;
		close FILE;
	} else {
		$qossettings{'ACTION'} = 'Unterklasse hinzufuegen';
	}
} elsif ($qossettings{'DOSCLASS'} eq 'Loeschen')
{
	open( FILE, "< $subclassfile" ) or die "Unable to read $classfile";
	@tmp = <FILE>;
	close FILE;
	open( FILE, "> $subclassfile" ) or die "Unable to write $classfile";
	foreach $subclassentry (sort @tmp)
	{
		@tmpline = split( /\;/, $subclassentry );
		if ( $tmpline[2] ne $qossettings{'CLASS'} )
		{
			print FILE $subclassentry;
		}
	}
	close FILE;
	$message = "Unterklasse $qossettings{'CLASS'} wurde geloescht.";
}

############################################################################################################################
############################################################################################################################

if ($qossettings{'DOLEVEL7'} eq $Lang::tr{'save'})
{
	if ( $qossettings{'QIP'} ne '' ) {
		unless ( &General::validip($qossettings{'QIP'}) ) { 
			$qossettings{'VALID'} = 'no';
			$message = "Die Quell-IP-Adresse ist ungueltig."; 
		}
	}
	if ( $qossettings{'DIP'} ne '' ) {
		unless ( &General::validip($qossettings{'DIP'}) ) { 
			$qossettings{'VALID'} = 'no';
			$message = "Die Ziel-IP-Adresse ist ungueltig."; 
		}
	}
	if ($qossettings{'CLASS'} >= 100 && $qossettings{'CLASS'} < 121) {
		$qossettings{'DEVICE'} = $qossettings{'RED_DEV'};
	} elsif ($qossettings{'CLASS'} >= 1000 && $qossettings{'CLASS'} < 1021) {
		$qossettings{'DEVICE'} = $qossettings{'RED_DEV'};
	} elsif ($qossettings{'CLASS'} >= 200 && $qossettings{'CLASS'} < 221) {
		$qossettings{'DEVICE'} = $qossettings{'IMQ_DEV'};
	} elsif ($qossettings{'CLASS'} >= 2000 && $qossettings{'CLASS'} < 2021) {
		$qossettings{'DEVICE'} = $qossettings{'IMQ_DEV'};
	}
	if ( $qossettings{'VALID'} eq 'yes' ) {
		open( FILE, ">> $level7file" ) or die "Unable to write $level7file";
		print FILE <<END
$qossettings{'CLASS'};$qossettings{'DEVICE'};$qossettings{'L7PROT'};$qossettings{'QIP'};$qossettings{'DIP'};
END
;
		close FILE;
	} else {
		$qossettings{'ACTION'} = 'Level7-Regel hinzufuegen';
	}
} 
elsif ($qossettings{'DOLEVEL7'} eq 'Loeschen')
{
	open( FILE, "< $level7file" ) or die "Unable to read $level7file";
	@l7rules = <FILE>;
	close FILE;
	open( FILE, "> $level7file" ) or die "Unable to read $level7file";
  	foreach $l7ruleentry (sort @l7rules)
  	{
  		@l7ruleline = split( /\;/, $l7ruleentry );
  		if ( ($l7ruleline[0] ne $qossettings{'CLASS'}) && ($l7ruleline[2] ne $qossettings{'L7PROT'}))
  		{
			print FILE $l7ruleentry;
		}
	}
	close FILE;
	$message = "Level7-Regel ($qossettings{'CLASS'} - $qossettings{'L7PROT'}) wurde geloescht.";
}

############################################################################################################################
############################################################################################################################

if ($qossettings{'DOPORT'} eq $Lang::tr{'save'})
{
	if ( $qossettings{'QIP'} ne '' ) {
		unless ( &General::validip($qossettings{'QIP'}) ) { 
			$qossettings{'VALID'} = 'no';
			$message = "Die Quell-IP-Adresse ist ungueltig."; 
		}
	}
	if ( $qossettings{'DIP'} ne '' ) {
		unless ( &General::validip($qossettings{'DIP'}) ) { 
			$qossettings{'VALID'} = 'no';
			$message = "Die Ziel-IP-Adresse ist ungueltig."; 
		}
	}
	if ($qossettings{'CLASS'} >= 100 && $qossettings{'CLASS'} < 121) {
		$qossettings{'DEVICE'} = $qossettings{'RED_DEV'};
	} elsif ($qossettings{'CLASS'} >= 1000 && $qossettings{'CLASS'} < 1021) {
		$qossettings{'DEVICE'} = $qossettings{'RED_DEV'};
	} elsif ($qossettings{'CLASS'} >= 200 && $qossettings{'CLASS'} < 221) {
		$qossettings{'DEVICE'} = $qossettings{'IMQ_DEV'};
	} elsif ($qossettings{'CLASS'} >= 2000 && $qossettings{'CLASS'} < 2021) {
		$qossettings{'DEVICE'} = $qossettings{'IMQ_DEV'};
	}
	if ( $qossettings{'VALID'} eq 'yes' ) {
		open( FILE, ">> $portfile" ) or die "Unable to write $portfile";
		print FILE <<END
$qossettings{'CLASS'};$qossettings{'DEVICE'};$qossettings{'PPROT'};$qossettings{'QIP'};$qossettings{'QPORT'};$qossettings{'DIP'};$qossettings{'DPORT'};
END
;
		close FILE;
	} else {
		$qossettings{'ACTION'} = 'Port-Regel hinzufuegen';
	}
} elsif ($qossettings{'DOPORT'} eq 'Loeschen')
{
	open( FILE, "< $portfile" ) or die "Unable to read $portfile";
	@portrules = <FILE>;
	close FILE;
	open( FILE, "> $portfile" ) or die "Unable to read $portfile";
  	foreach $portruleentry (sort @portrules)
  	{
  		@portruleline = split( /\;/, $portruleentry );
  		unless ( ($portruleline[0] eq $qossettings{'CLASS'}) && ($portruleline[2] eq $qossettings{'PPROT'}) && ($portruleline[3] eq $qossettings{'QIP'}) && ($portruleline[4] eq $qossettings{'QPORT'}) && ($portruleline[5] eq $qossettings{'DIP'}) && ($portruleline[6] eq $qossettings{'DPORT'}))
  		{
			print FILE $portruleentry;
		}
	}
	close FILE;
	$message = "Port-Regel ($qossettings{'CLASS'} - $qossettings{'PPROT'}) wurde geloescht.";
}

############################################################################################################################
############################################################################################################################

if ($qossettings{'ACTION'} eq 'Start')
{
	system("sleep 2 && /usr/bin/perl /var/ipfire/qos/bin/makeqosscripts.pl > /var/ipfire/qos/bin/qos.sh &");
	system("/bin/touch /var/ipfire/qos/enable");
	$qossettings{'ENABLED'} = 'on';
	&General::writehash("${General::swroot}/qos/settings", \%qossettings);
}
elsif ($qossettings{'ACTION'} eq 'Stop')
{
	unlink "/var/ipfire/qos/bin/qos.sh";
	unlink "/var/ipfire/qos/enable";
	$qossettings{'ENABLED'} = 'off';
	&General::writehash("${General::swroot}/qos/settings", \%qossettings);
}
elsif ($qossettings{'ACTION'} eq 'Neustart')
{
	if ($qossettings{'ENABLED'} eq 'on'){
		system("sleep 2 && /usr/bin/perl /var/ipfire/qos/bin/makeqosscripts.pl > /var/ipfire/qos/bin/qos.sh &");
	}
}
elsif ($qossettings{'ACTION'} eq $Lang::tr{'save'})
{
	if ($qossettings{'DEF_INC_SPD'} eq '') {
		$qossettings{'DEF_INC_SPD'} = int($qossettings{'INC_SPD'} * 0.9);
	}
	if ($qossettings{'DEF_OUT_SPD'} eq '') {
		$qossettings{'DEF_OUT_SPD'} = int($qossettings{'OUT_SPD'} * 0.9);
	}
	&General::writehash("${General::swroot}/qos/settings", \%qossettings);
}
elsif ($qossettings{'ACTION'} eq 'Statusinformationen')
{
	&Header::openbox('100%', 'left', 'QoS Status');
	if ($qossettings{'ENABLED'} eq 'on'){
		my $output = "";
		$output = `/usr/local/bin/qosctrl status`;
		$output = &Header::cleanhtml($output,"y");
		print "<pre>$output</pre>\n";
	} else { print "QoS ist nicht aktiviert!"; }
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit
}
elsif ($qossettings{'ACTION'} eq 'Parentklasse hinzufuegen')
{
	&parentclass();
	&Header::closebigbox();
	&Header::closepage();
	exit
}
elsif ($qossettings{'ACTION'} eq 'Unterklasse hinzufuegen')
{
	&subclass();
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
elsif ($qossettings{'ACTION'} eq 'Port-Regel hinzufuegen')
{
	&portrule();
	&Header::closebigbox();
	&Header::closepage();
	exit
}
elsif ($qossettings{'ACTION'} eq 'Erweiterte Einstellungen')
{
	&expert();
	&Header::closebigbox();
	&Header::closepage();
	exit
}
if ($qossettings{'ACTIONBW'} eq 'Andern')
{
	&changebandwidth();
	&Header::closebigbox();
	&Header::closepage();
	exit
}
if ($qossettings{'ACTIONDEF'} eq 'Andern')
{
	&changedefclasses();
	&Header::closebigbox();
	&Header::closepage();
	exit
}

&General::readhash("${General::swroot}/qos/settings", \%qossettings);

my $status = $Lang::tr{'stopped'};
my $statuscolor = '#993333';
if ( $qossettings{'ENABLED'} eq 'on' ) {
  $status = $Lang::tr{'running'};
  $statuscolor = '#339933';
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

############################################################################################################################
############################################################################################################################

&Header::openbox('100%', 'center', 'Quality of Service');
print <<END
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table width='33%'>
END
;
	if ( $message ne "" ) {
		print "<tr><td colspan='2' align='center'><font color='red'>$message</font>";
	}
	print <<END
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
		    <td width='20%' rowspan='2' align='center' valign='middle'><input type='submit' name='ACTIONBW' value='Andern'>
		<tr><td width='40%' align='right'>Uploadgeschwindigkeit: 	<td width='40%' align='left'>$qossettings{'OUT_SPD'} kbps
END
;
	}
	if (($qossettings{'DEFCLASS_OUT'} ne '') && ($qossettings{'DEFCLASS_INC'} ne '')&& ($qossettings{'ACK'} ne '')) {
		print <<END
		<tr><td colspan='3'><hr>
		<tr><td width='40%' align='right'>Downloadstandardklasse: 	<td width='40%' align='left'>$qossettings{'DEFCLASS_INC'}	
		    <td width='20%' rowspan='3' align='center' valign='middle'><input type='submit' name='ACTIONDEF' value='Andern'>
		<tr><td width='40%' align='right'>Uploadstandardklasse: 	<td width='40%' align='left'>$qossettings{'DEFCLASS_OUT'}
		<tr><td width='40%' align='right'>ACKs:				<td width='40%' align='left'>$qossettings{'ACK'}
	 	<tr><td colspan='3' width='100%'><hr>
		<tr><td colspan='3' width='100%' align='center'><input type='submit' name='ACTION' value='Parentklasse hinzufuegen'><input type='submit' name='ACTION' value='Erweiterte Einstellungen'><input type='submit' name='ACTION' value='Statusinformationen'>
	</form>
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

&showclasses();
&showl7rules();
&showportrules();

&Header::closebigbox();
&Header::closepage();

############################################################################################################################
############################################################################################################################

sub changedefclasses {
	&Header::openbox('100%', 'center', 'Standardklassen:');
	print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='66%'>
		<tr><td width='100%' colspan='3'>Legen sie hier die Standardklassen fest durch die nicht-gefilterte Pakete gehen.
		<tr><td width='33%' align='right'>Download:<td width='33%' align='left'><select name='DEFCLASS_INC'>
END
;
		for ( $c = 200 ; $c <= 220 ; $c++ )
		{
			if ( $qossettings{'DEFCLASS_INC'} ne $c )
			{ print "<option value='$c'>$c</option>\n"; } 
			else	{ print "<option selected value='$c'>$c</option>\n"; }
		}
		print <<END
		</select><td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Upload:<td width='33%' align='left'><select name='DEFCLASS_OUT'>
END
;
		for ( $c = 100 ; $c <= 120 ; $c++ )
		{
			if ( $qossettings{'DEFCLASS_OUT'} ne $c )
			{ print "<option value='$c'>$c</option>\n"; }
			else { print "<option selected value='$c'>$c</option>\n"; }
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
		for ( $c = 100 ; $c <= 120 ; $c++ )
		{
			if ( $qossettings{'ACK'} ne $c )
			{ print "<option value='$c'>$c</option>\n"; }
			else {	print "<option selected value='$c'>$c</option>\n"; }
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
		<input type='hidden' name='DEF_OUT_SPD' value=''><input type='hidden' name='DEF_INC_SPD' value=''>
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
	&Header::openbox('100%', 'center', 'Parentklasse');
	print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='66%'>
END
;
	if ( $message ne "" ) {
		print "<tr><td colspan='3' align='center'>$message";
	}
	if ( $qossettings{'EDIT'} eq 'yes' ) { 
		print "<input type='hidden' name='CLASS' value=$qossettings{'CLASS'}>";
		print "<input type='hidden' name='DEVICE' value=$qossettings{'DEVICE'}>";
	}
	print <<END
		<tr><td width='100%' colspan='3'>Geben sie die Daten ein <br> und klicken Sie danach auf <i>Speichern</i>.
		<tr><td width='33%' align='right'>Interface:
		    <td width='33%' align='left'>
END
;
		if ( $qossettings{'EDIT'} eq 'yes' ) { 
			print "<select name='DEVICE' disabled>";
		} else {
			print "<select name='DEVICE'>";
		}
		if ( $qossettings{'DEVICE'} eq $qossettings{'RED_DEV'} ) {
			$qossettings{'RED_DEV_SEL'} = 'selected';
		} elsif ( $qossettings{'DEVICE'} eq $qossettings{'IMQ_DEV'} ) {
			$qossettings{'IMQ_DEV_SEL'} = 'selected';
		}
		print <<END
			<option value=$qossettings{'RED_DEV'} $qossettings{'RED_DEV_SEL'}>$qossettings{'RED_DEV'}</option>
			<option value=$qossettings{'IMQ_DEV'} $qossettings{'IMQ_DEV_SEL'}>$qossettings{'IMQ_DEV'}</option></select>
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Klasse:<td width='33%' align='left'>
END
;
		if ( $qossettings{'EDIT'} eq 'yes' ) { 
			print "<select name='CLASS' disabled>";
		} else {
			print "<select name='CLASS'>";
		}
		for ( $c = 100 ; $c <= 120 ; $c++ )
		{
			if ( $qossettings{'CLASS'} ne $c )
			{ print "<option value='$c'>$c</option>\n"; }
			else { print "<option selected value='$c'>$c</option>\n"; }
		}
		for ( $c = 200 ; $c <= 220 ; $c++ )
		{
			if ( $qossettings{'CLASS'} ne $c )
			{ print "<option value='$c'>$c</option>\n"; }
			else { print "<option selected value='$c'>$c</option>\n"; }
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
			{ print "<option value='$c'>$c</option>\n"; }
			else { print "<option selected value='$c'>$c</option>\n"; }
		}
		print <<END
		<td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Garantierte Bandbreite:
		    <td width='33%' align='left'><input type='text' name='MINBWDTH' maxlength='8' required='1' value=$qossettings{'MINBWDTH'} >
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Maximale Bandbreite:
		    <td width='33%' align='left'><input type='text' name='MAXBWDTH' maxlength='8' required='1' value=$qossettings{'MAXBWDTH'}>
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Burst:
		    <td width='33%' align='left'><input type='text' name='BURST' maxlength='8' value=$qossettings{'BURST'}>
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Ceilburst:
		    <td width='33%' align='left'><input type='text' name='CBURST' maxlength='8' value=$qossettings{'CBURST'}>
		    <td width='33%' align='center'><input type='submit' name='DOCLASS' value=$Lang::tr{'save'} />&nbsp;<input type='reset' value=$Lang::tr{'reset'} />
		</table></form>
END
;
	&Header::closebox();
}

sub subclass {
	&Header::openbox('100%', 'center', 'Unterklasse');
	print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='66%'>
END
;
	if ( $message ne "" ) {
		print "<tr><td colspan='3' align='center'>$message";
	}
	print <<END
		<tr><td colspan='3' width='100%'>Aktuelle Klasse: $qossettings{'CLASS'}
		<tr><td width='100%' colspan='3'>Geben sie die Daten ein <br> und klicken Sie danach auf <i>Speichern</i>.
		<tr><td width='33%' align='right'>Unterklasse:<td width='33%' align='left'><select name='SCLASS'>
END
;
	if ($qossettings{'CLASS'} >= 100 && $qossettings{'CLASS'} < 121) {
		$qossettings{'DEVICE'} = $qossettings{'RED_DEV'};
		for ( $c = 1000 ; $c <= 1020 ; $c++ )
		{
			if ( $qossettings{'SCLASS'} ne $c )
			{ print "<option value='$c'>$c</option>\n"; }
			else { print "<option selected value='$c'>$c</option>\n"; }
		}
	} elsif ($qossettings{'CLASS'} >= 200 && $qossettings{'CLASS'} < 221) {
		$qossettings{'DEVICE'} = $qossettings{'IMQ_DEV'};
		for ( $c = 2000 ; $c <= 2020 ; $c++ )
		{
			if ( $qossettings{'SCLASS'} ne $c )
			{ print "<option value='$c'>$c</option>\n"; }
			else { print "<option selected value='$c'>$c</option>\n"; }
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
			{ print "<option value='$c'>$c</option>\n"; }
			else { print "<option selected value='$c'>$c</option>\n"; }
		}
		print <<END
		<td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Garantierte Bandbreite:
		    <td width='33%' align='left'><input type='text' name='MINBWDTH' maxlength='8' required='1' value=$qossettings{'MINBWDTH'} >
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Maximale Bandbreite:
		    <td width='33%' align='left'><input type='text' name='MAXBWDTH' maxlength='8' required='1' value=$qossettings{'MAXBWDTH'}>
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Burst:
		    <td width='33%' align='left'><input type='text' name='BURST' maxlength='8' value=$qossettings{'BURST'}>
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Ceilburst:
		    <td width='33%' align='left'><input type='text' name='CBURST' maxlength='8' value=$qossettings{'CBURST'}>
		    <td width='33%' align='center'><input type='hidden' name='CLASS' value=$qossettings{'CLASS'}><input type='submit' name='DOSCLASS' value=$Lang::tr{'save'} />&nbsp;<input type='reset' value=$Lang::tr{'reset'} />
		</table></form>
END
;
	&Header::closebox();
}

sub level7rule {
	&Header::openbox('100%', 'center', 'Level7-Regel');
	print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='66%'>
END
;
	if ( $message ne "" ) {
		print "<tr><td colspan='3' align='center'><font color='red'>$message</font>";
	}
	print <<END
		<tr><td colspan='3' width='100%'>Aktuelle Klasse: $qossettings{'CLASS'}
		<tr><td width='100%' colspan='3'>Geben sie die Daten ein <br> und klicken Sie danach auf <i>Speichern</i>.
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
		    <td width='33%' align='center'><input type='hidden' name='CLASS' value=$qossettings{'CLASS'}><input type='submit' name='DOLEVEL7' value=$Lang::tr{'save'} />
		</table></form>
END
;
	&Header::closebox();
}

sub portrule {
	&Header::openbox('100%', 'center', 'Port-Regel hinzufuegen');
	print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='66%'>
		<tr><td width='100%' colspan='3'>Geben sie die Daten ein <br> und klicken Sie danach auf <i>Speichern</i>.
		<tr><td width='33%' align='right'>Protokoll:
		    <td width='33%' align='left'><select name='PPROT'>
END
;
			open( FILE, "< /etc/protocols" );
			@proto = <FILE>;
			close FILE;
			foreach $direntry (sort @proto)
			{
				@tmpline = split( /\ /, $direntry );
				next if $tmpline[0] =~ "#";
				if ( $tmpline[0] eq $qossettings{'PPROT'} ) {
					print "<option value='$tmpline[0]' selected>$tmpline[0]</option>\n";			
				} else {
					print "<option value='$tmpline[0]'>$tmpline[0]</option>\n";
				}
			}
	print <<END
		    </select><td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Quell-Port:
		    <td width='33%' align='left'><input type='text' name='QPORT' maxlength='5' value=$qossettings{'QPORT'}>
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Ziel-Port:
		    <td width='33%' align='left'><input type='text' name='DPORT' maxlength='5' value=$qossettings{'DPORT'}>
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Quell-IP-Adresse:
		    <td width='33%' align='left'><input type='text' name='QIP' maxlength='15' value=$qossettings{'QIP'}>
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Ziel-IP-Adresse:
		    <td width='33%' align='left'><input type='text' name='DIP' maxlength='15' value=$qossettings{'DIP'}>
		    <td width='33%' align='center'><input type='hidden' name='CLASS' value='$qossettings{'CLASS'}'><input type='submit' name='DOPORT' value=$Lang::tr{'save'} />
		</table></form>
END
;
	&Header::closebox();
}

sub showclasses {
	open( FILE, "< $classfile" ) or die "Unable to read $classfile";
	@classes = <FILE>;
	close FILE;
	if (@classes) {
		open( FILE, "< $subclassfile" ) or die "Unable to read $subclassfile";
		@subclasses = <FILE>;
		close FILE;
		&Header::openbox('100%', 'center', 'Klassen');
		print <<END
		<table border='0' width='100%' cellspacing='0'>
		<tr><td bgcolor='lightgrey' width='10%'>Interface
		    <td bgcolor='lightgrey' width='10%'>Klasse
		    <td bgcolor='lightgrey' width='10%'>Prioritaet
		    <td bgcolor='lightgrey' width='10%'>Garantierte Bandbreite
		    <td bgcolor='lightgrey' width='10%'>Maximale Bandbreite
		    <td bgcolor='lightgrey' width='10%'>Burst
		    <td bgcolor='lightgrey' width='10%'>Ceil Burst
		    <td bgcolor='lightgrey' width='30%'>Aktionen
END
;
	  	foreach $classentry (sort @classes)
	  	{
	  		@classline = split( /\;/, $classentry );
	  		if ( $classline[0] eq $qossettings{'RED_DEV'} )
	  		{
	  			print <<END
				<tr><td align='center' bgcolor='#EAEAEA'>$classline[0]
				    <td align='center' bgcolor='#EAEAEA'>$classline[1]
				    <td align='center' bgcolor='#EAEAEA'>$classline[2]
				    <td align='center' bgcolor='#EAEAEA'>$classline[3]
				    <td align='center' bgcolor='#EAEAEA'>$classline[4]
				    <td align='center' bgcolor='#EAEAEA'>$classline[5]
				    <td align='center' bgcolor='#EAEAEA'>$classline[6]
				    <td align='right'  bgcolor='#EAEAEA'>
					<table border='0'><tr>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$classline[1]'>
						<input type='hidden' name='DOCLASS' value='Bearbeiten'>
						<input type='image' alt='Bearbeiten' src='/images/edit.gif'>
					</form>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$classline[1]'>
						<input type='hidden' name='ACTION' value='Unterklasse hinzufuegen'>
						<input type='image' alt='Unterklasse hinzufuegen' src='/images/addblue.gif'>
					</form>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$classline[1]'>
						<input type='hidden' name='ACTION' value='Level7-Regel hinzufuegen'>
						<input type='image' alt='Level7-Regel hinzufuegen' src='/images/addgreen.gif'>
					</form>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$classline[1]'>
						<input type='hidden' name='ACTION' value='Port-Regel hinzufuegen'>
						<input type='image' alt='Port-Regel hinzufuegen' src='/images/add.gif'>
					</form>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$classline[1]'>
						<input type='hidden' name='DOCLASS' value='Loeschen'>
						<input type='image' alt='Loeschen' src='/images/delete.gif'>
					</form>
					</table>
END
;
			  	foreach $subclassentry (sort @subclasses)
	  			{
	  				@subclassline = split( /\;/, $subclassentry );
		  			if ( $subclassline[1] eq $classline[1] ) {
						print <<END
							<tr><td align='center' bgcolor='#FFFFFF'>Subklasse:
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[2]
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[3]
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[4]
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[5]
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[6]
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[7]
							    <td align='right'  bgcolor='#FAFAFA'>
						<table border='0'><tr>
						<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='CLASS' value='$subclassline[2]'>
							<input type='hidden' name='DOSCLASS' value='Bearbeiten'>
							<input type='image' alt='Bearbeiten' src='/images/edit.gif'>
						</form>
						<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='CLASS' value='$subclassline[2]'>
							<input type='hidden' name='ACTION' value='Level7-Regel hinzufuegen'>
							<input type='image' alt='Level7-Regel hinzufuegen' src='/images/addgreen.gif'>
						</form>
						<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='CLASS' value='$subclassline[2]'>
							<input type='hidden' name='ACTION' value='Port-Regel hinzufuegen'>
							<input type='image' alt='Port-Regel hinzufuegen' src='/images/add.gif'>
						</form>
						<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='CLASS' value='$subclassline[2]'>
							<input type='hidden' name='DOSCLASS' value='Loeschen'>
							<input type='image' alt='Loeschen' src='/images/delete.gif'>
						</form>
						</table>
END
;
					}
				}
	  		}
	  	}
		print "\t<tr><td colspan='8' bgcolor='lightgrey' height='2'>";
	  	foreach $classentry (sort @classes)
	  	{
	  		@classline = split( /\;/, $classentry );
	  		if ( $classline[0] eq $qossettings{'IMQ_DEV'} )
	  		{
	  			print <<END
				<tr><td align='center' bgcolor='#EAEAEA'>$classline[0]
				    <td align='center' bgcolor='#EAEAEA'>$classline[1]
				    <td align='center' bgcolor='#EAEAEA'>$classline[2]
				    <td align='center' bgcolor='#EAEAEA'>$classline[3]
				    <td align='center' bgcolor='#EAEAEA'>$classline[4]
				    <td align='center' bgcolor='#EAEAEA'>$classline[5]
				    <td align='center' bgcolor='#EAEAEA'>$classline[6]
				    <td align='right'  bgcolor='#EAEAEA'>
					<table border='0'><tr>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$classline[1]'>
						<input type='hidden' name='DOCLASS' value='Bearbeiten'>
						<input type='image' alt='Bearbeiten' src='/images/edit.gif'>
					</form>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$classline[1]'>
						<input type='hidden' name='ACTION' value='Unterklasse hinzufuegen'>
						<input type='image' alt='Unterklasse hinzufuegen' src='/images/addblue.gif'>
					</form>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$classline[1]'>
						<input type='hidden' name='ACTION' value='Level7-Regel hinzufuegen'>
						<input type='image' alt='Level7-Regel hinzufuegen' src='/images/addgreen.gif'>
					</form>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$classline[1]'>
						<input type='hidden' name='ACTION' value='Port-Regel hinzufuegen'>
						<input type='image' alt='Port-Regel hinzufuegen' src='/images/add.gif'>
					</form>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$classline[1]'>
						<input type='hidden' name='DOCLASS' value='Loeschen'>
						<input type='image' alt='Loeschen' src='/images/delete.gif'>
					</form>
					</table>
END
;
			  	foreach $subclassentry (sort @subclasses)
	  			{
	  				@subclassline = split( /\;/, $subclassentry );
		  			if ( $subclassline[1] eq $classline[1] ) {
						print <<END
							<tr><td align='center' bgcolor='#FFFFFF'>Subklasse:
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[2]
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[3]
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[4]
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[5]
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[6]
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[7]
							    <td align='right'  bgcolor='#FAFAFA'>
							<table border='0'><tr>
							<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
								<input type='hidden' name='CLASS' value='$subclassline[2]'>
								<input type='hidden' name='DOSCLASS' value='Bearbeiten'>
								<input type='image' alt='Bearbeiten' src='/images/edit.gif'>
							</form>
							<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
								<input type='hidden' name='CLASS' value='$subclassline[2]'>
								<input type='hidden' name='ACTION' value='Level7-Regel hinzufuegen'>
								<input type='image' alt='Level7-Regel hinzufuegen' src='/images/addgreen.gif'>
							</form>
							<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
								<input type='hidden' name='CLASS' value='$subclassline[2]'>
								<input type='hidden' name='ACTION' value='Port-Regel hinzufuegen'>
								<input type='image' alt='Port-Regel hinzufuegen' src='/images/add.gif'>
							</form>
							<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
								<input type='hidden' name='CLASS' value='$subclassline[2]'>
								<input type='hidden' name='DOSCLASS' value='Loeschen'>
								<input type='image' alt='Loeschen' src='/images/delete.gif'>
							</form>
							</table>
END
;
					}
				}
	  		}
	  	}
		print <<END
		<tr><td colspan='8' align='right' valign='middle'><b>Legende:</b>&nbsp;&nbsp;<img src='/images/edit.gif'>&nbsp;Klasse bearbeiten | <img src='/images/addblue.gif'>&nbsp;Unterklasse hinzufuegen | <img src='/images/addgreen.gif'>&nbsp;Level7-Regel hinzufuegen | <img src='/images/add.gif'>&nbsp;Port-Regel hinzufuegen | <img src='/images/delete.gif'>&nbsp;Klasse loeschen &nbsp;
		</table>
END
;
		&Header::closebox();
	}
}

sub showl7rules {
	open( FILE, "< $level7file" ) or die "Unable to read $level7file";
	@l7rules = <FILE>;
	close FILE;
	if (@l7rules) {
		&Header::openbox('100%', 'center', 'Level7-Regeln');
		print <<END
		<table border='0' width='100%' cellspacing='0'>
		<tr><td bgcolor='lightgrey' width='14%'>Interface
		    <td bgcolor='lightgrey' width='14%'>Klasse
		    <td bgcolor='lightgrey' width='14%'>Protokoll
		    <td bgcolor='lightgrey' width='14%'>Quell-IP-Adresse
		    <td bgcolor='lightgrey' width='14%'>Ziel-IP-Adresse
		    <td bgcolor='lightgrey' width='30%'>Aktionen
END
;
	  	foreach $l7ruleentry (sort @l7rules)
	  	{
	  		@l7ruleline = split( /\;/, $l7ruleentry );
	  		if ( $l7ruleline[1] eq $qossettings{'RED_DEV'} )
	  		{
	  			print <<END
				<tr><td align='center' bgcolor='#EAEAEA'>$l7ruleline[1]
				    <td align='center' bgcolor='#EAEAEA'>$l7ruleline[0]
				    <td align='center' bgcolor='#EAEAEA'>$l7ruleline[2]
				    <td align='center' bgcolor='#EAEAEA'>$l7ruleline[3]
				    <td align='center' bgcolor='#EAEAEA'>$l7ruleline[4]
				    <td align='right'  bgcolor='#EAEAEA'>
					<table border='0'><tr>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$l7ruleline[0]'>
						<input type='hidden' name='L7PROT' value='$l7ruleline[2]'>
						<input type='hidden' name='DOLEVEL7' value='Bearbeiten'>
						<input type='image' alt='Bearbeiten' src='/images/edit.gif'>
					</form>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$l7ruleline[0]'>
						<input type='hidden' name='L7PROT' value='$l7ruleline[2]'>
						<input type='hidden' name='DOLEVEL7' value='Loeschen'>
						<input type='image' alt='Loeschen' src='/images/delete.gif'>
					</form>
					</table>
END
;
	  		}
	  	}
		print "\t<tr><td colspan='8' bgcolor='lightgrey' height='2'>";
	  	foreach $l7ruleentry (sort @l7rules)
	  	{
	  		@l7ruleline = split( /\;/, $l7ruleentry );
	  		if ( $l7ruleline[1] eq $qossettings{'IMQ_DEV'} )
	  		{
	  			print <<END
				<tr><td align='center' bgcolor='#EAEAEA'>$l7ruleline[1]
				    <td align='center' bgcolor='#EAEAEA'>$l7ruleline[0]
				    <td align='center' bgcolor='#EAEAEA'>$l7ruleline[2]
				    <td align='center' bgcolor='#EAEAEA'>$l7ruleline[3]
				    <td align='center' bgcolor='#EAEAEA'>$l7ruleline[4]
				    <td align='right'  bgcolor='#EAEAEA'>
					<table border='0'><tr>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$l7ruleline[0]'>
						<input type='hidden' name='L7PROT' value='$l7ruleline[2]'>
						<input type='hidden' name='DOLEVEL7' value='Bearbeiten'>
						<input type='image' alt='Bearbeiten' src='/images/edit.gif'>
					</form>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$l7ruleline[0]'>
						<input type='hidden' name='L7PROT' value='$l7ruleline[2]'>
						<input type='hidden' name='DOLEVEL7' value='Loeschen'>
						<input type='image' alt='Loeschen' src='/images/delete.gif'>
					</form>
					</table>
END
;
	  		}
	  	}
		print <<END
		<tr><td colspan='8' align='right' valign='middle'><b>Legende:</b>&nbsp;&nbsp;<img src='/images/edit.gif'>&nbsp;Regel bearbeiten | <img src='/images/delete.gif'>&nbsp;Regel loeschen &nbsp;
		</table>
END
;
		&Header::closebox();
	}
}

sub showportrules {
	open( FILE, "< $portfile" ) or die "Unable to read $portfile";
	@portrules = <FILE>;
	close FILE;
	if (@portrules) {
		&Header::openbox('100%', 'center', 'Port-Regeln');
		print <<END
		<table border='0' width='100%' cellspacing='0'>
		<tr><td bgcolor='lightgrey' width='10%'>Interface
		    <td bgcolor='lightgrey' width='10%'>Klasse
		    <td bgcolor='lightgrey' width='10%'>Protokoll
		    <td bgcolor='lightgrey' width='10%'>Quell-IP-Adresse
		    <td bgcolor='lightgrey' width='10%'>Quell-Port
		    <td bgcolor='lightgrey' width='10%'>Ziel-IP-Adresse
		    <td bgcolor='lightgrey' width='10%'>Ziel-Port
		    <td bgcolor='lightgrey' width='30%'>Aktionen
END
;
	  	foreach $portruleentry (sort @portrules)
	  	{
	  		@portruleline = split( /\;/, $portruleentry );
	  		if ( $portruleline[1] eq $qossettings{'RED_DEV'} )
	  		{
	  			print <<END
				<tr><td align='center' bgcolor='#EAEAEA'>$portruleline[1]
				    <td align='center' bgcolor='#EAEAEA'>$portruleline[0]
				    <td align='center' bgcolor='#EAEAEA'>$portruleline[2]
				    <td align='center' bgcolor='#EAEAEA'>$portruleline[3]
				    <td align='center' bgcolor='#EAEAEA'>$portruleline[4]
				    <td align='center' bgcolor='#EAEAEA'>$portruleline[5]
				    <td align='center' bgcolor='#EAEAEA'>$portruleline[6]
				    <td align='right'  bgcolor='#EAEAEA'>
				    <table border='0'><tr>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$portruleline[0]'>
						<input type='hidden' name='PPROT' value='$portruleline[2]'>
						<input type='hidden' name='QIP' value='$portruleline[3]'>
						<input type='hidden' name='QPORT' value='$portruleline[4]'>
						<input type='hidden' name='DIP' value='$portruleline[5]'>
						<input type='hidden' name='DPORT' value='$portruleline[6]'>
						<input type='hidden' name='DOPORT' value='Bearbeiten'>
						<input type='image' alt='Bearbeiten' src='/images/edit.gif'>
					</form>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$portruleline[0]'>
						<input type='hidden' name='PPROT' value='$portruleline[2]'>
						<input type='hidden' name='QIP' value='$portruleline[3]'>
						<input type='hidden' name='QPORT' value='$portruleline[4]'>
						<input type='hidden' name='DIP' value='$portruleline[5]'>
						<input type='hidden' name='DPORT' value='$portruleline[6]'>
						<input type='hidden' name='DOPORT' value='Loeschen'>
						<input type='image' alt='Loeschen' src='/images/delete.gif'>
					</form>
				    </table>
END
;
	  		}
	  	}
		print "\t<tr><td colspan='8' bgcolor='lightgrey' height='2'>";
	  	foreach $portruleentry (sort @portrules)
	  	{
	  		@portruleline = split( /\;/, $portruleentry );
	  		if ( $portruleline[1] eq $qossettings{'IMQ_DEV'} )
	  		{
	  			print <<END
				<tr><td align='center' bgcolor='#EAEAEA'>$portruleline[1]
				    <td align='center' bgcolor='#EAEAEA'>$portruleline[0]
				    <td align='center' bgcolor='#EAEAEA'>$portruleline[2]
				    <td align='center' bgcolor='#EAEAEA'>$portruleline[3]
				    <td align='center' bgcolor='#EAEAEA'>$portruleline[4]
				    <td align='center' bgcolor='#EAEAEA'>$portruleline[5]
				    <td align='center' bgcolor='#EAEAEA'>$portruleline[6]
				    <td align='right'  bgcolor='#EAEAEA'>
				    <table border='0'><tr>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$portruleline[0]'>
						<input type='hidden' name='PPROT' value='$portruleline[2]'>
						<input type='hidden' name='QIP' value='$portruleline[3]'>
						<input type='hidden' name='QPORT' value='$portruleline[4]'>
						<input type='hidden' name='DIP' value='$portruleline[5]'>
						<input type='hidden' name='DPORT' value='$portruleline[6]'>
						<input type='hidden' name='DOPORT' value='Bearbeiten'>
						<input type='image' alt='Bearbeiten' src='/images/edit.gif'>
					</form>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$portruleline[0]'>
						<input type='hidden' name='PPROT' value='$portruleline[2]'>
						<input type='hidden' name='QIP' value='$portruleline[3]'>
						<input type='hidden' name='QPORT' value='$portruleline[4]'>
						<input type='hidden' name='DIP' value='$portruleline[5]'>
						<input type='hidden' name='DPORT' value='$portruleline[6]'>
						<input type='hidden' name='DOPORT' value='Loeschen'>
						<input type='image' alt='Loeschen' src='/images/delete.gif'>
					</form>
				    </table>
END
;
	  		}
	  	}
		print <<END
		<tr><td colspan='8' align='right' valign='middle'><b>Legende:</b>&nbsp;&nbsp;<img src='/images/edit.gif'>&nbsp;Regel bearbeiten | <img src='/images/delete.gif'>&nbsp;Regel loeschen &nbsp;
		</table>
END
;
		&Header::closebox();
	}
}

sub expert
{
	&Header::openbox('100%', 'center', 'Expertenoptionen:');
	print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='66%'>
		<tr><td width='100%' colspan='3'>Diese Einstellungen sollten sie nur veraendern, wenn sie wirklich wissen, was sie tun.
		<tr><td width='33%' align='right'>Download-Rate 90\%:<td width='33%' align='left'>
			<input type='text' name='DEF_INC_SPD' maxlength='8' required='4' value=$qossettings{'DEF_INC_SPD'}>
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Upload-Rate 90\%:<td width='33%' align='left'>
			<input type='text' name='DEF_OUT_SPD' maxlength='8' required='4' value=$qossettings{'DEF_OUT_SPD'}>
		    <td width='33%' align='center'>&nbsp;
		</table>
		<hr>
		<table width='66%'>
		<tr><td width='33%' align='right'>MTU:<td width='33%' align='left'>
			<input type='text' name='MTU' maxlength='8' required='4' value=$qossettings{'MTU'}>
		    <td width='33%' align='center'>Diese Einstellung aendert die MTU nicht global sondern nur fuer das QoS.
		<tr><td width='33%' align='right'>Queue Laenge:<td width='33%' align='left'>
			<input type='text' name='QLENGTH' maxlength='8' required='2' value=$qossettings{'QLENGTH'}>
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>SFQ Perturb:<td width='33%' align='left'>
			<input type='text' name='SFQ_PERTUB' maxlength='8' required='1' value=$qossettings{'SFQ_PERTUB'}>
		    <td width='33%' align='center'><input type='submit' name='ACTION' value=$Lang::tr{'save'} />
		</table>
		</form>
END
;
	&Header::closebox();
}

sub validminbwdth {
	if ( $qossettings{'VALID'} eq 'yes' ) {
		if ( $qossettings{'DEVICE'} eq $qossettings{'RED_DEV'} ) {
			$qossettings{'SPD'} = $qossettings{'OUT_SPD'};
		} elsif ( $qossettings{'DEVICE'} eq $qossettings{'IMQ_DEV'} ) {
			$qossettings{'SPD'} = $qossettings{'INC_SPD'};
		}
		unless ( ( $qossettings{'MINBDWTH'} >= 0 ) && ( $qossettings{'MINBDWTH'} <= $qossettings{'SPD'} ) ) {
			$qossettings{'VALID'} = 'no';
			$message = "Mindestbandbreite ist ungueltig.";
		}
		$qossettings{'SPD'} = '';
	}
}

sub validmaxbwdth {
	if ( $qossettings{'VALID'} eq 'yes' ) {
		if ( $qossettings{'DEVICE'} eq $qossettings{'RED_DEV'} ) {
			$qossettings{'SPD'} = $qossettings{'OUT_SPD'};
		} elsif ( $qossettings{'DEVICE'} eq $qossettings{'IMQ_DEV'} ) {
			$qossettings{'SPD'} = $qossettings{'INC_SPD'};
		}
		unless ( ( $qossettings{'MAXBDWTH'} >= 0 ) && ($qossettings{'MAXBDWTH'} >= $qossettings{'MINBDWTH'}) &&( $qossettings{'MAXBDWTH'} <= $qossettings{'SPD'} ) ) {
			$qossettings{'VALID'} = 'no';
			$message = "Mamimalbandbreite ist ungueltig.";
		}
		$qossettings{'SPD'} = '';
	}
}

sub validclass {
	if ( $qossettings{'VALID'} eq 'yes' ) {
		if ( $qossettings{'DEVICE'} eq $qossettings{'RED_DEV'} ) {
			if ($qossettings{'CLASS'} lt 100 || $qossettings{'CLASS'} ge 121) {
				$qossettings{'VALID'} = 'no';
				$message = "Die Klassennummer passt nicht zum angegebenen Interface.";
			}
		} elsif ( $qossettings{'DEVICE'} eq $qossettings{'IMQ_DEV'} ) {
			if ($qossettings{'CLASS'} lt 200 || $qossettings{'CLASS'} ge 221) {
				$qossettings{'VALID'} = 'no';
				$message = "Die Klassennummer passt nicht zum angegebenen Interface.";
			}
		}
		open( FILE, "< $classfile" ) or die "Unable to read $classfile";
		@tmp = <FILE>;
		close FILE;
		foreach $classentry (sort @tmp)
	  	{
	  		@tmpline = split( /\;/, $classentry );
	  		if ( $tmpline[1] eq $qossettings{'CLASS'} )
  			{
				$qossettings{'VALID'} = 'no';
				$message = "Die aktuelle Klasse wird bereits verwendet.";
				last
			}
		}
	}
}

sub validsubclass {
	if ( $qossettings{'VALID'} eq 'yes' ) {
		open( FILE, "< $subclassfile" ) or die "Unable to read $subclassfile";
		@tmp = <FILE>;
		close FILE;
		foreach $subclassentry (sort @tmp)
	  	{
	  		@tmpline = split( /\;/, $subclassentry );
	  		if ( $tmpline[2] eq $qossettings{'SCLASS'} )
  			{
				$qossettings{'VALID'} = 'no';
				$message = "Die aktuelle Klasse wird bereits verwendet.";
				last
			}
		}
	}
}
