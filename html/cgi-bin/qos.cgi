#!/usr/bin/perl
#
# IPFire CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The IPFire Team
#

use RRDs;
use strict;
# enable only the following on debugging purpose
# use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %qossettings = ();
my %checked = ();
my %netsettings = ();
my $message = '';
my $errormessage = "";
my $c = "";
my $direntry = "";
my $classentry = "";
my $subclassentry = "";
my $l7ruleentry = "";
my $portruleentry = "";
my $tosruleentry = "";
my @tmp = ();
my @classes = ();
my @subclasses = ();
my @l7rules = ();
my @portrules = ();
my @tosrules = ();
my @tmpline = ();
my @classline = ();
my @subclassline = ();
my @l7ruleline = ();
my @portruleline = ();
my @tosruleline = ();
my @proto = ();
my %selected= ();
my @checked = ();
my $classfile = "/var/ipfire/qos/classes";
my $subclassfile = "/var/ipfire/qos/subclasses";
my $level7file = "/var/ipfire/qos/level7config";
my $portfile = "/var/ipfire/qos/portconfig";
my $tosfile = "/var/ipfire/qos/tosconfig";
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
$qossettings{'RED_DEV_SEL'} = '';
$qossettings{'IMQ_DEV_SEL'} = '';
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
$qossettings{'CLASS'} = '';
$qossettings{'CLASSPRFX'} = '';
$qossettings{'DEV'} = '';
$qossettings{'TOS'} = '';


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
$qossettings{'DEVICE'};$qossettings{'CLASS'};$qossettings{'PRIO'};$qossettings{'MINBWDTH'};$qossettings{'MAXBWDTH'};$qossettings{'BURST'};$qossettings{'CBURST'};$qossettings{'TOS'};$qossettings{'REMARK'};
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
			$qossettings{'TOS'} = $classline[7];
			$qossettings{'REMARK'} = $classline[8];
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
	&validsubclass();
	&validminbwdth();
	if ( $qossettings{'VALID'} eq 'yes' ) {
		open( FILE, ">> $subclassfile" ) or die "Unable to write $subclassfile";
		print FILE <<END
$qossettings{'DEVICE'};$qossettings{'CLASS'};$qossettings{'SCLASS'};$qossettings{'PRIO'};$qossettings{'MINBWDTH'};$qossettings{'MAXBWDTH'};$qossettings{'BURST'};$qossettings{'CBURST'};$qossettings{'TOS'};
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

if ($qossettings{'DOTOS'} eq $Lang::tr{'save'})
{
	if ($qossettings{'CLASS'} >= 100 && $qossettings{'CLASS'} < 121) {
		$qossettings{'DEVICE'} = $qossettings{'RED_DEV'};
	} elsif ($qossettings{'CLASS'} >= 1000 && $qossettings{'CLASS'} < 1021) {
		$qossettings{'DEVICE'} = $qossettings{'RED_DEV'};
	} elsif ($qossettings{'CLASS'} >= 200 && $qossettings{'CLASS'} < 221) {
		$qossettings{'DEVICE'} = $qossettings{'IMQ_DEV'};
	} elsif ($qossettings{'CLASS'} >= 2000 && $qossettings{'CLASS'} < 2021) {
		$qossettings{'DEVICE'} = $qossettings{'IMQ_DEV'};
	}
	open( FILE, ">> $tosfile" ) or die "Unable to write $tosfile";
	print FILE <<END
$qossettings{'CLASS'};$qossettings{'DEVICE'};$qossettings{'TOS'};
END
;
	close FILE;
} 
elsif ($qossettings{'DOTOS'} eq 'Loeschen')
{
	open( FILE, "< $tosfile" ) or die "Unable to read $tosfile";
	@tosrules = <FILE>;
	close FILE;
	open( FILE, "> $tosfile" ) or die "Unable to read $tosfile";
  	foreach $tosruleentry (sort @tosrules)
  	{
  		@tosruleline = split( /\;/, $tosruleentry );
  		unless ( ($tosruleline[0] eq $qossettings{'CLASS'}) && ($tosruleline[2] eq $qossettings{'TOS'}))
  		{
			print FILE $tosruleentry;
		}
	}
	close FILE;
	$message = "TOS-Regel ($qossettings{'CLASS'} - $qossettings{'TOS'}) wurde geloescht.";
} elsif ($qossettings{'DOTOS'} eq 'Bearbeiten')
{
	open( FILE, "< $tosfile" ) or die "Unable to read $tosfile";
	@tosrules = <FILE>;
	close FILE;
	open( FILE, "> $tosfile" ) or die "Unable to write $tosfile";
	foreach $tosruleentry (sort @tosrules)
	{
		@tosruleline = split( /\;/, $tosruleentry );
		if (( $tosruleline[0] eq $qossettings{'CLASS'} ) && ( $tosruleline[2] eq $qossettings{'TOS'} )) {
			$qossettings{'DEVICE'} = $tosruleline[1];
			$qossettings{'CLASS'} = $tosruleline[0];
			$qossettings{'TOS'} = $tosruleline[2];
			$qossettings{'EDIT'} = 'yes';
		} else {
			print FILE $tosruleentry;
		}
	}
	close FILE;
	&tosrule();
	&Header::closebigbox();
	&Header::closepage();
	exit
}

############################################################################################################################
############################################################################################################################

if ($qossettings{'ACTION'} eq 'Start')
{
	system("/usr/local/bin/qosctrl generate >/dev/null 2>&1");
	system("/usr/bin/touch /var/ipfire/qos/enable");
	system("/usr/local/bin/qosctrl start >/dev/null 2>&1");
	system("logger -t ipfire 'QoS started'");
	$qossettings{'ENABLED'} = 'on';
	&General::writehash("${General::swroot}/qos/settings", \%qossettings);
}
elsif ($qossettings{'ACTION'} eq 'Stop')
{
	system("/usr/local/bin/qosctrl stop >/dev/null 2>&1");
	unlink "/var/ipfire/qos/bin/qos.sh";
	unlink "/var/ipfire/qos/enable";
	system("logger -t ipfire 'QoS stopped'");
	$qossettings{'ENABLED'} = 'off';
	&General::writehash("${General::swroot}/qos/settings", \%qossettings);
}
elsif ($qossettings{'ACTION'} eq 'Neustart')
{
	if ($qossettings{'ENABLED'} eq 'on'){
		system("/usr/local/bin/qosctrl stop >/dev/null 2>&1");
		system("/usr/local/bin/qosctrl generate >/dev/null 2>&1");
		system("/usr/local/bin/qosctrl start >/dev/null 2>&1");
		system("logger -t ipfire 'QoS restarted'");
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
elsif ($qossettings{'ACTION'} eq 'Grafische Auswertung')
{
	open( FILE, "< $classfile" ) or die "Unable to read $classfile";
	@classes = <FILE>;
	close FILE;
	open( FILE, "< $subclassfile" ) or die "Unable to read $subclassfile";
	@subclasses = <FILE>;
	close FILE;
	&Header::openbox('100%', 'left', 'QoS Graphen');
	print <<END
	<table width='100%'>	<tr><td align='center'><font color='red'>Diese Seite braucht je nach Geschwindigkeit des Computers laenger zum Laden.</font>
				<tr><td align='center'><b>Klasse:</b> 
END
;
  	foreach $classentry (sort @classes)
  	{
  		@classline = split( /\;/, $classentry );
		$qossettings{'CLASS'}=$classline[1];
		print <<END
		<input type="button" onClick="swapVisibility('$qossettings{'CLASS'}')" value='$qossettings{'CLASS'}'>
END
;
	}
	print <<END
	</table>
END
;
	&Header::closebox();
  	foreach $classentry (sort @classes)
  	{
  		@classline = split( /\;/, $classentry );
		$qossettings{'DEV'}=$classline[0];
		$qossettings{'CLASS'}=$classline[1];
		&gengraph($qossettings{'DEV'},$qossettings{'CLASS'});
		print "<div id='$qossettings{'CLASS'}' style='display: none'>";
		&Header::openbox('100%', 'center', "$qossettings{'CLASS'} ($qossettings{'DEV'})");
		print <<END
		<table>
		<tr><td colspan='2' align='center'><img src='/graphs/class_$qossettings{'CLASSPRFX'}-$qossettings{'CLASS'}_$qossettings{'DEV'}-packets.png'>
		<tr><td colspan='2' align='center'><img src='/graphs/class_$qossettings{'CLASSPRFX'}-$qossettings{'CLASS'}_$qossettings{'DEV'}-borrowed.png'>
		<tr><td colspan='2' align='center'><img src='/graphs/class_$qossettings{'CLASSPRFX'}-$qossettings{'CLASS'}_$qossettings{'DEV'}-bytes.png'>
END
;
	  	foreach $subclassentry (sort @subclasses)
  		{
	  		@subclassline = split( /\;/, $subclassentry );
			if ($subclassline[1] eq $classline[1]) {
				$qossettings{'DEV'}=$subclassline[0];
				$qossettings{'SCLASS'}=$subclassline[2];
				&gengraph($qossettings{'DEV'},$qossettings{'SCLASS'});
				print <<END
				<tr><td colspan='2' align='center'><img src='/graphs/class_$qossettings{'CLASSPRFX'}-$qossettings{'SCLASS'}_$qossettings{'DEV'}-packets.png'>
				<tr><td colspan='2' align='center'><img src='/graphs/class_$qossettings{'CLASSPRFX'}-$qossettings{'SCLASS'}_$qossettings{'DEV'}-borrowed.png'>
				<tr><td colspan='2' align='center'><img src='/graphs/class_$qossettings{'CLASSPRFX'}-$qossettings{'SCLASS'}_$qossettings{'DEV'}-bytes.png'>
END
;
			}
		}
		print "\t\t</table>";
		&Header::closebox();	
		print "</div>\n";
	}
print <<END
	</table>
END
;
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
elsif ($qossettings{'ACTION'} eq 'Regel hinzufuegen')
{
	&Header::openbox('100%', 'center', 'Regel hinzufuegen');
	print <<END
		<table>
		<tr><td align='center'>Waehlen sie <u>eine</u> der untenstehenden Regeln aus.
		<tr><td align='center'>
			<input type="button" onClick="swapVisibility('l7rule')" value='Level7-Regel' />
			<input type="button" onClick="swapVisibility('portrule')" value='Port-Regel' />
			<input type="button" onClick="swapVisibility('tosrule')" value='TOS-Regel' />
		</table>
END
;
	&Header::closebox();
	print <<END
		<div id='l7rule' style='display: none'>
END
;
		&level7rule();
	print <<END
		</div>
		<div id='portrule' style='display: none'>
END
;
		&portrule();
	print <<END
		</div>
		<div id='tosrule' style='display: none'>
END
;
		&tosrule();
	print <<END
		</div>
END
;
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
		<input type='submit' name='ACTION' value="Start" /> 
		<input type='submit' name='ACTION' value="Stop" /> 
		<input type='submit' name='ACTION' value="$Lang::tr{'restart'}" />
END
;
	if (($qossettings{'OUT_SPD'} ne '') && ($qossettings{'INC_SPD'} ne '')) {
		print <<END
		<tr><td colspan='3'>&nbsp;
		<tr><td width='40%' align='right'>Downloadgeschwindigkeit: 	<td width='40%' align='left'>$qossettings{'INC_SPD'} kbps
		    <td width='20%' rowspan='2' align='center' valign='middle'><input type='submit' name='ACTIONBW' value='Andern' />
		<tr><td width='40%' align='right'>Uploadgeschwindigkeit: 	<td width='40%' align='left'>$qossettings{'OUT_SPD'} kbps
END
;
	}
	if (($qossettings{'DEFCLASS_OUT'} ne '') && ($qossettings{'DEFCLASS_INC'} ne '')&& ($qossettings{'ACK'} ne '')) {
		print <<END
		<tr><td colspan='3'><hr />
		<tr><td width='40%' align='right'>Downloadstandardklasse: 	<td width='40%' align='left'>$qossettings{'DEFCLASS_INC'}	
		    <td width='20%' rowspan='3' align='center' valign='middle'><input type='submit' name='ACTIONDEF' value='Andern'>
		<tr><td width='40%' align='right'>Uploadstandardklasse: 	<td width='40%' align='left'>$qossettings{'DEFCLASS_OUT'}
		<tr><td width='40%' align='right'>ACKs:				<td width='40%' align='left'>$qossettings{'ACK'}
	 	<tr><td colspan='3' width='100%'><hr />
		<tr><td colspan='3' width='100%' align='center'>
		<table boder='0' cellpadding='0' cellspacing='0'>
			<tr><td><input type='submit' name='ACTION' value='Parentklasse hinzufuegen'>
			    <td><input type='submit' name='ACTION' value='Erweiterte Einstellungen'>
			<tr><td><input type='submit' name='ACTION' value='Statusinformationen'>
			    <td><input type='submit' name='ACTION' value='Grafische Auswertung'>
		</table>
	</form>
END
;
	}
print "</table>";
&Header::closebox();

if ( ($qossettings{'OUT_SPD'} eq '') || ($qossettings{'INC_SPD'} eq '') ) {
	&changebandwidth();
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

&Header::openbox('100%', 'center', $Lang::tr{'info'});
&overviewgraph($qossettings{'RED_DEV'});
&overviewgraph($qossettings{'IMQ_DEV'});
print <<END
	<table>
		<tr><td colspan='9' align='right' valign='middle'><img src='/images/addblue.gif'>&nbsp;Unterklasse hinzufuegen | <img src='/images/addgreen.gif'>&nbsp;Regel hinzufuegen | <img src='/images/edit.gif'>&nbsp;Bearbeiten | <img src='/images/delete.gif'>&nbsp;Loeschen &nbsp;
		<tr><td colspan='9' align='right' valign='middle'><b>TOS-Bits:</b>&nbsp;&nbsp;<b>0</b> - Deaktiviert | <b>8</b> - Minimale Verzoegerung | <b>4</b> - Maximaler Durchsatz | <b>2</b> - Maximale Zuverlaessigkeit | <b>1</b> - Minimale Kosten &nbsp;
END
;
if (( -e "/srv/web/ipfire/html/graphs/qos-graph-$qossettings{'RED_DEV'}.png") && ( -e "/srv/web/ipfire/html/graphs/qos-graph-$qossettings{'IMQ_DEV'}.png")) {
	print <<END
		<tr><td colspan='9' align='center'><img src="/graphs/qos-graph-$qossettings{'RED_DEV'}.png">
		<tr><td colspan='9' align='center'><img src="/graphs/qos-graph-$qossettings{'IMQ_DEV'}.png">
END
;}
print "\t</table>";

&Header::closebox();

&showclasses($qossettings{'RED_DEV'});
&showclasses($qossettings{'IMQ_DEV'});

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
		<hr />
		<table width='66%'>
		<tr><td width='100%' colspan='3'>Legen sie hier die ACK-Klasse fest <br /> und klicken Sie danach auf <i>Speichern</i>.
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
		</select><td width='33%' align='center'><input type='submit' name='ACTION' value="$Lang::tr{'save'}" />
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
		<input type='hidden' name='DEF_OUT_SPD' value='' /><input type='hidden' name='DEF_INC_SPD' value='' />
		<table width='66%'>
		<tr><td width='100%' colspan='3'>Geben Sie bitte hier ihre Download- bzw. Upload-Geschwindigkeit ein <br /> und klicken Sie danach auf <i>Speichern</i>.
		<tr><td width='33%' align='right'>Download-Geschwindigkeit:
		    <td width='33%' align='left'><input type='text' name='INC_SPD' maxlength='8' value="$qossettings{'INC_SPD'}" /> &nbsp; kbps
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Upload-Geschwindigkeit:
		    <td width='33%' align='left'><input type='text' name='OUT_SPD' maxlength='8' value="$qossettings{'OUT_SPD'}" /> &nbsp; kbps
		    <td width='33%' align='center'><input type='submit' name='ACTION' value="$Lang::tr{'save'}" />&nbsp;<input type='reset' name='ACTION' value="$Lang::tr{'reset'}" />
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
		<tr><td width='100%' colspan='3'>Geben sie die Daten ein <br /> und klicken Sie danach auf <i>Speichern</i>.
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
		if ($qossettings{'MINBWDTH'} eq "") { $qossettings{'MINBWDTH'} = "1"; }
		print <<END
		</select>
		<td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Garantierte Bandbreite:
		    <td width='33%' align='left'><input type='text' size='20' name='MINBWDTH' maxlength='8' required='1' value="$qossettings{'MINBWDTH'}" />
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Maximale Bandbreite:
		    <td width='33%' align='left'><input type='text' size='20' name='MAXBWDTH' maxlength='8' required='1' value="$qossettings{'MAXBWDTH'}" />
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Burst:
		    <td width='33%' align='left'><input type='text' size='20' name='BURST' maxlength='8' value="$qossettings{'BURST'}" />
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Ceilburst:
		    <td width='33%' align='left'><input type='text' size='20' name='CBURST' maxlength='8' value="$qossettings{'CBURST'}" />
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>TOS-Bit:
		    <td width='33%' align='left'><select name='TOS'>
				<option value='0'>Ausgeschaltet (0)</option>
				<option value='8'>Minimale Verzoegerung (8)</option>
				<option value='4'>Maximaler Durchsatz (4)</option>
				<option value='2'>Maximale Zuverlaessigkeit (2)</option>
				<option value='1'>Minimale Kosten (1)</option></select>
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>$Lang::tr{'remark'}:
		    <td width='66%' colspan='2' align='left'><input type='text' name='REMARK' size='40' maxlength='40' value="$qossettings{'REMARK'}" /> <img alt='blob' src='/blob.gif' />
		<tr><td width='33%' align='right'>&nbsp;
		    <td width='33%' align='left'>&nbsp;
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
		<tr><td width='100%' colspan='3'>Geben sie die Daten ein <br /> und klicken Sie danach auf <i>Speichern</i>.
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
		    <td width='33%' align='left'><input type='text' name='MINBWDTH' maxlength='8' required='1' value="$qossettings{'MINBWDTH'}" />
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Maximale Bandbreite:
		    <td width='33%' align='left'><input type='text' name='MAXBWDTH' maxlength='8' required='1' value="$qossettings{'MAXBWDTH'}" />
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Burst:
		    <td width='33%' align='left'><input type='text' name='BURST' maxlength='8' value="$qossettings{'BURST'}" />
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>Ceilburst:
		    <td width='33%' align='left'><input type='text' name='CBURST' maxlength='8' value="$qossettings{'CBURST'}" />
		    <td width='33%' align='center'>&nbsp;
		<tr><td width='33%' align='right'>TOS-Bit:
		    <td width='33%' align='left'><select name='TOS'>
				<option value='0'>Ausgeschaltet (0)</option>
				<option value='8'>Minimale Verzoegerung (8)</option>
				<option value='4'>Maximaler Durchsatz (4)</option>
				<option value='2'>Maximale Zuverlaessigkeit (2)</option>
				<option value='1'>Minimale Kosten (1)</option></select>
		    <td width='33%' align='center'><input type='hidden' name='CLASS' value="$qossettings{'CLASS'}" />
							<input type='hidden' name='DEVICE' value="$qossettings{'DEVICE'}" />
							<input type='submit' name='DOSCLASS' value=$Lang::tr{'save'} />&nbsp;<input type='reset' value=$Lang::tr{'reset'} />
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
		<tr><td width='100%' colspan='3'>Geben sie die Daten ein <br /> und klicken Sie danach auf <i>Speichern</i>.
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
		<tr><td width='100%' colspan='3'>Geben sie die Daten ein <br /> und klicken Sie danach auf <i>Speichern</i>.
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

sub tosrule {
	&Header::openbox('100%', 'center', 'TOS-Regel');
	if ($qossettings{'TOS'}) {
		$checked[$qossettings{'TOS'}] = "checked";
	}
	print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='66%'>
END
;
	if ( $message ne "" ) {
		print "<tr><td colspan='3' align='center'><font color='red'>$message</font>";
	}
	print <<END
		<tr><td colspan='2' width='100%'>Aktuelle Klasse: $qossettings{'CLASS'}
		<tr><td width='100%' colspan='2'>Aktivieren oder deaktivieren sie die TOS-Bits <br /> und klicken Sie danach auf <i>Speichern</i>.
		<tr><td width='50%' align='left'>Minimale Verzoegerung (8)		<td width='50%'><input type="radio" name="TOS" value="8" $checked[8]>
		<tr><td width='50%' align='left'>Maximaler Durchsatz (4)		<td width='50%'><input type="radio" name="TOS" value="4" $checked[4]>
		<tr><td width='50%' align='left'>Maximale Zuverlaessigkeit (2)	<td width='50%'><input type="radio" name="TOS" value="2" $checked[2]>
		<tr><td width='50%' align='left'>Minimale Kosten (1)			<td width='50%'><input type="radio" name="TOS" value="1" $checked[1]>
		<tr><td width='100%' align='right' colspan='2'><input type='hidden' name='CLASS' value=$qossettings{'CLASS'}><input type='submit' name='DOTOS' value=$Lang::tr{'save'} />
		</table></form>
END
;
	&Header::closebox();
}

sub showclasses {
	$qossettings{'DEV'} = shift;
	open( FILE, "< $classfile" ) or die "Unable to read $classfile";
	@classes = <FILE>;
	close FILE;
	if (@classes) {
		open( FILE, "< $subclassfile" ) or die "Unable to read $subclassfile";
		@subclasses = <FILE>;
		close FILE;
		open( FILE, "< $level7file" ) or die "Unable to read $level7file";
		@l7rules = <FILE>;
		close FILE;
		open( FILE, "< $tosfile" ) or die "Unable to read $tosfile";
		@tosrules = <FILE>;
		close FILE;
		open( FILE, "< $portfile" ) or die "Unable to read $portfile";
		@portrules = <FILE>;
		close FILE;
	  	foreach $classentry (sort @classes)
	  	{
	  		@classline = split( /\;/, $classentry );
	  		if ( $classline[0] eq $qossettings{'DEV'} )
	  		{
				gengraph($qossettings{'DEV'},$classline[1]);
				&Header::openbox('100%', 'center', "Klasse: $classline[1]");
	  			print <<END
				<table border='0' width='100%' cellspacing='0'>
				<tr><td bgcolor='lightgrey' width='10%' align='center'><b>$Lang::tr{'interface'}</b>
				    <td bgcolor='lightgrey' width='10%' align='center'><b>Klasse</b>
				    <td bgcolor='lightgrey' width='10%' align='center'>Prioritaet
				    <td bgcolor='lightgrey' width='10%' align='center'>Garantierte Bandbreite
				    <td bgcolor='lightgrey' width='10%' align='center'>Maximale Bandbreite
				    <td bgcolor='lightgrey' width='10%' align='center'>Burst
				    <td bgcolor='lightgrey' width='10%' align='center'>Ceil Burst
				    <td bgcolor='lightgrey' width='10%' align='center'>TOS
				    <td bgcolor='lightgrey' width='20%' align='center'>Aktionen
				<tr><td align='center' bgcolor='#EAEAEA'>$classline[0]</td>
				    <td align='center' bgcolor='#EAEAEA'>$classline[1]</td>
				    <td align='center' bgcolor='#EAEAEA'>$classline[2]</td>
				    <td align='center' bgcolor='#EAEAEA'>$classline[3]</td>
				    <td align='center' bgcolor='#EAEAEA'>$classline[4]</td>
				    <td align='center' bgcolor='#EAEAEA'>$classline[5]</td>
				    <td align='center' bgcolor='#EAEAEA'>$classline[6]</td>
				    <td align='center' bgcolor='#EAEAEA'>$classline[7]</td>
				    <td align='right'  bgcolor='#EAEAEA'>
					<table border='0'><tr>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$classline[1]'>
						<input type='hidden' name='ACTION' value='Unterklasse hinzufuegen'>
						<input type='image' alt='Unterklasse hinzufuegen' src='/images/addblue.gif'>
					</form>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$classline[1]'>
						<input type='hidden' name='ACTION' value='Regel hinzufuegen'>
						<input type='image' alt='Regel hinzufuegen' src='/images/addgreen.gif'>
					</form>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$classline[1]'>
						<input type='hidden' name='DOCLASS' value='Bearbeiten'>
						<input type='image' alt='Bearbeiten' src='/images/edit.gif'>
					</form>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$classline[1]'>
						<input type='hidden' name='DOCLASS' value='Loeschen'>
						<input type='image' alt='Loeschen' src='/images/delete.gif'>
					</form>
					</table>
				    </td>
				<tr><td align='right' colspan='2'><b>$Lang::tr{'remark'}:</b>
				    <td align='center' colspan='6'> $classline[8]
				    <td align='right'><b>Queueing:</b> $classline[9]
END
;

				if (@l7rules) {
	  				foreach $l7ruleentry (sort @l7rules)
	  				{
	  					@l7ruleline = split( /\;/, $l7ruleentry );
	  					if ( $l7ruleline[0] eq $classline[1] )
	  					{
	  						print <<END
				<tr><td align='right' colspan='2'><b>Level7-Protokoll:</b>
				    <td align='center' colspan='6'>$l7ruleline[2]
				    <td align='right' >
					<table border='0'><tr>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$l7ruleline[0]' />
						<input type='hidden' name='L7PROT' value='$l7ruleline[2]' />
						<input type='hidden' name='DOLEVEL7' value='Bearbeiten' />
						<input type='image' alt='Bearbeiten' src='/images/edit.gif' />
					</form>
					<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='CLASS' value='$l7ruleline[0]' />
						<input type='hidden' name='L7PROT' value='$l7ruleline[2]' />
						<input type='hidden' name='DOLEVEL7' value='Loeschen' />
						<input type='image' alt='Loeschen' src='/images/delete.gif' />
					</form>
					</table>
END
;
							if (($l7ruleline[3] ne "") || ($l7ruleline[4] ne "")){
								print <<END
				<tr><td align='center'>&nbsp;
				    <td align='right' colspan='3'><b>Quell-IP:</b> $l7ruleline[3]
				    <td align='right' colspan='3'><b>Ziel-IP:</b> $l7ruleline[4]
END
;
							}


END
;
	  					}
	  				}
				}


				if (@portrules) {
				  	foreach $portruleentry (sort @portrules)
				  	{
				  		@portruleline = split( /\;/, $portruleentry );
				  		if ( $portruleline[0] eq $classline[1] )
				  		{
				  			print <<END
				<tr><td align='right' colspan='2'><b>Port-Regel:</b>
				    <td align='center'>($portruleline[2])
				    <td align='center' colspan='2'>
END
;
						if ($portruleline[4]) {
							print <<END
				    <i>Quell-Port:</i> $portruleline[4]
END
;
						}
						print "<td align='center' colspan='2'>";
						if ($portruleline[6]) {
							print <<END
				    <i>Ziel-Port:</i> $portruleline[6]
END
;
						}
						print <<END
				    <td>&nbsp;
				    <td align='right'>
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
							if (($portruleline[3] ne "") || ($portruleline[5] ne "")){
								print <<END
				<tr><td align='center'>&nbsp;
				    <td align='right' colspan='3'><b>Quell-IP:</b> $portruleline[3]
				    <td align='right' colspan='3'><b>Ziel-IP:</b> $portruleline[5]
END
;
							}
				  		}
				  	}
				}

				if (@tosrules) {
				  	foreach $tosruleentry (sort @tosrules)
				  	{
				  		@tosruleline = split( /\;/, $tosruleentry );
				  		if ( $tosruleline[0] eq $classline[1] )
				  		{
							print <<END
					<tr><td align='right' colspan='2'>
						<b>TOS Bit matches:</b>
					    <td colspan='6' align='center'>
END
;
							if ( $tosruleline[2] eq "8") {
								print "Minimale Verzoegerung\n";
							} elsif ( $tosruleline[2] eq "4") {
								print "Maximaler Durchsatz\n";
							} elsif ( $tosruleline[2] eq "2") {
								print "Maximaler Durchsatz\n";
							} elsif ( $tosruleline[2] eq "1") {
								print "Minimale Kosten\n";
							} else { print "&nbsp;\n"; }

							print <<END
						($tosruleline[2])
					    <td align='right'>
				  		  <table border='0'><tr>
							<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
								<input type='hidden' name='CLASS' value='$tosruleline[0]'>
								<input type='hidden' name='DEV' value='$tosruleline[1]'>
								<input type='hidden' name='TOS' value='$tosruleline[2]'>
								<input type='hidden' name='DOTOS' value='Bearbeiten'>
								<input type='image' alt='Bearbeiten' src='/images/edit.gif'>
							</form>
							<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
								<input type='hidden' name='CLASS' value='$tosruleline[0]'>
								<input type='hidden' name='DEV' value='$tosruleline[1]'>
								<input type='hidden' name='TOS' value='$tosruleline[2]'>
								<input type='hidden' name='DOTOS' value='Loeschen'>
								<input type='image' alt='Loeschen' src='/images/delete.gif'>
							</form>
				    		</table>
END
;
	  					}
	  				}
				}

				if ( -e "/srv/web/ipfire/html/graphs/class_$qossettings{'CLASSPRFX'}-$qossettings{'CLASS'}_$qossettings{'DEV'}-packets.png") {
					print <<END
					<tr><td colspan='9' align='center'><img src='/graphs/class_$qossettings{'CLASSPRFX'}-$qossettings{'CLASS'}_$qossettings{'DEV'}-packets.png'>
END
;
				}


			  	foreach $subclassentry (sort @subclasses)
	  			{
	  				@subclassline = split( /\;/, $subclassentry );
		  			if ( $subclassline[1] eq $classline[1] ) {
						print <<END
							<tr><td align='center' bgcolor='#FAFAFA'>Subklasse:
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[2]
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[3]
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[4]
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[5]
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[6]
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[7]
							    <td align='center' bgcolor='#FAFAFA'>$subclassline[8]
							    <td align='right'  bgcolor='#FAFAFA'>
						<table border='0'><tr>
						<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='CLASS' value='$subclassline[2]'>
							<input type='hidden' name='ACTION' value='Regel hinzufuegen'>
							<input type='image' alt='Regel hinzufuegen' src='/images/addgreen.gif'>
						</form>
						<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='CLASS' value='$subclassline[2]'>
							<input type='hidden' name='DOSCLASS' value='Bearbeiten'>
							<input type='image' alt='Bearbeiten' src='/images/edit.gif'>
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
			print <<END
			</table>
END
;
			&Header::closebox();
	  		}
	  	}
	}
}

sub expert
{
	&Header::openbox('100%', 'center', 'Expertenoptionen:');
	print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
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
		unless ( ( $qossettings{'MINBWDTH'} >= 1 ) && ( $qossettings{'MINBWDTH'} <= $qossettings{'SPD'} ) ) {
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

sub gengraph {
	$qossettings{'DEV'} = shift;
	$qossettings{'CLASS'} = shift;
	my $ERROR="";
	if ( $qossettings{'DEV'} eq $qossettings{'RED_DEV'} ) { 
		$qossettings{'CLASSPRFX'} = '1';
	} else { 
		$qossettings{'CLASSPRFX'} = '2';
	}
	my $color=random_hex_color(6);

	RRDs::graph ("/srv/web/ipfire/html/graphs/class_$qossettings{'CLASSPRFX'}-$qossettings{'CLASS'}_$qossettings{'DEV'}-packets.png",
		"--start", "-3240", "-aPNG", "-i", "-z",
		"--alt-y-grid", "-w 600", "-h 150", "-r",
		"--color", "SHADEA#EAE9EE",
		"--color", "SHADEB#EAE9EE",
		"--color", "BACK#FFFFFF",
		"-t $qossettings{'CLASS'} ($qossettings{'DEV'})",
		"DEF:pkts=/var/log/rrd/class_$qossettings{'CLASSPRFX'}-$qossettings{'CLASS'}_$qossettings{'DEV'}.rrd:pkts:AVERAGE",
		"DEF:dropped=/var/log/rrd/class_$qossettings{'CLASSPRFX'}-$qossettings{'CLASS'}_$qossettings{'DEV'}.rrd:dropped:AVERAGE",
		"DEF:overlimits=/var/log/rrd/class_$qossettings{'CLASSPRFX'}-$qossettings{'CLASS'}_$qossettings{'DEV'}.rrd:overlimits:AVERAGE",
		"AREA:pkts$color:packets",
		"GPRINT:pkts:LAST:total packets\\:%8.3lf %s packets\\j",
		"LINE3:dropped#FF0000:dropped",
		"GPRINT:dropped:LAST:dropped packets\\:%8.3lf %s packets\\j",
		"LINE3:overlimits#0000FF:overlimits",
		"GPRINT:overlimits:LAST:overlimits\\:%8.3lf %s packets\\j",
	);
	$ERROR = RRDs::error;
	#print "$ERROR";
}

sub overviewgraph {
	$qossettings{'DEV'} = shift;
	if ( $qossettings{'DEV'} eq $qossettings{'RED_DEV'} ) { 
		$qossettings{'CLASSPRFX'} = '1';
	} else { 
		$qossettings{'CLASSPRFX'} = '2';
	}
	my $ERROR="";
	my $count="1";
	my $color="#000000";
	my @command=("/srv/web/ipfire/html/graphs/qos-graph-$qossettings{'DEV'}.png",
		"--start", "-3240", "-aPNG", "-i", "-z",
		"--alt-y-grid", "-w 600", "-h 150", "-r",
		"--color", "SHADEA#EAE9EE",
		"--color", "SHADEB#EAE9EE",
		"--color", "BACK#FFFFFF",
		"-t Auslastung auf ($qossettings{'DEV'})"
	);
	open( FILE, "< $classfile" ) or die "Unable to read $classfile";
	@classes = <FILE>;
	close FILE;
  	foreach $classentry (sort @classes)
  	{
  		@classline = split( /\;/, $classentry );
  		if ( $classline[0] eq $qossettings{'DEV'} )
  		{
			$color=random_hex_color(6);
			push(@command, "DEF:$classline[1]=/var/log/rrd/class_$qossettings{'CLASSPRFX'}-$classline[1]_$qossettings{'DEV'}.rrd:bits:AVERAGE");

			if ($count eq "1") {
				push(@command, "AREA:$classline[1]$color:Klasse $classline[1] - $classline[8]\\j");
			} else {
				push(@command, "STACK:$classline[1]$color:Klasse $classline[1] - $classline[8]\\j");
			}
			$count++;
		}
	}
	RRDs::graph (@command);
	$ERROR = RRDs::error;
	#print "$ERROR";
}

sub random_hex_color {
    my $size = shift;
    $size = 6 if $size !~ /^3|6$/;
    my @hex = ( 0 .. 9, 'a' .. 'f' );
    my @color;
    push @color, @hex[rand(@hex)] for 1 .. $size;
    return join('', '#', @color);
}