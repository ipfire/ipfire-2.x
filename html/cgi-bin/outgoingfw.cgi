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

my %outfwsettings = ();
my %checked = ();
my %selected= () ;
my %netsettings = ();
my $errormessage = "";
my $configentry = "";
my @configs = ();
my @configline = ();
my $p2pentry = "";
my @p2ps = ();
my @p2pline = ();

my $configfile = "/var/ipfire/outgoing/rules";
my $p2pfile = "/var/ipfire/outgoing/p2protocols";

&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

&Header::showhttpheaders();

### Values that have to be initialized
$outfwsettings{'ACTION'} = '';
$outfwsettings{'VALID'} = 'yes';
$outfwsettings{'EDIT'} = 'no';
$outfwsettings{'NAME'} = '';
$outfwsettings{'SNET'} = '';
$outfwsettings{'SIP'} = '';
$outfwsettings{'SPORT'} = '';
$outfwsettings{'SMAC'} = '';
$outfwsettings{'DIP'} = '';
$outfwsettings{'DPORT'} = '';
$outfwsettings{'PROT'} = '';
$outfwsettings{'STATE'} = '';
$outfwsettings{'DISPLAY_DIP'} = '';
$outfwsettings{'DISPLAY_DPORT'} = '';
$outfwsettings{'DISPLAY_SMAC'} = '';
$outfwsettings{'DISPLAY_SIP'} = '';
$outfwsettings{'POLICY'} = 'MODE0';

&General::readhash("${General::swroot}/outgoing/settings", \%outfwsettings);
&Header::getcgihash(\%outfwsettings);

if ($outfwsettings{'POLICY'} eq 'MODE0'){ $selected{'POLICY'}{'MODE0'} = 'selected'; } else { $selected{'POLICY'}{'MODE0'} = ''; }
if ($outfwsettings{'POLICY'} eq 'MODE1'){ $selected{'POLICY'}{'MODE1'} = 'selected'; } else { $selected{'POLICY'}{'MODE1'} = ''; }
if ($outfwsettings{'POLICY'} eq 'MODE2'){ $selected{'POLICY'}{'MODE2'} = 'selected'; } else { $selected{'POLICY'}{'MODE2'} = ''; }

&Header::openpage('Ausgehende Firewall', 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
############################################################################################################################

if ($outfwsettings{'ACTION'} eq $Lang::tr{'reset'})
{
	$outfwsettings{'POLICY'}='MODE0';
	unlink $configfile;
	system("/bin/touch $configfile");
	&General::writehash("${General::swroot}/outgoing/settings", \%outfwsettings);
}
if ($outfwsettings{'ACTION'} eq $Lang::tr{'save'})
{
	&General::writehash("${General::swroot}/outgoing/settings", \%outfwsettings);
}
if ($outfwsettings{'ACTION'} eq 'enable')
{
	open( FILE, "< $p2pfile" ) or die "Unable to read $p2pfile";
	@p2ps = <FILE>;
	close FILE;
	open( FILE, "> $p2pfile" ) or die "Unable to write $p2pfile";
	foreach $p2pentry (sort @p2ps)
	{
		@p2pline = split( /\;/, $p2pentry );
		if ($p2pline[1] eq $outfwsettings{'P2PROT'}) {
			print FILE "$p2pline[0];$p2pline[1];on;\n";
		} else {
			print FILE "$p2pline[0];$p2pline[1];$p2pline[2];\n";
		}
	}
	close FILE;
}
if ($outfwsettings{'ACTION'} eq 'disable')
{
	open( FILE, "< $p2pfile" ) or die "Unable to read $p2pfile";
	@p2ps = <FILE>;
	close FILE;
	open( FILE, "> $p2pfile" ) or die "Unable to write $p2pfile";
	foreach $p2pentry (sort @p2ps)
	{
		@p2pline = split( /\;/, $p2pentry );
		if ($p2pline[1] eq $outfwsettings{'P2PROT'}) {
			print FILE "$p2pline[0];$p2pline[1];off;\n";
		} else {
			print FILE "$p2pline[0];$p2pline[1];$p2pline[2];\n";
		}
	}
	close FILE;
}
if ($outfwsettings{'ACTION'} eq $Lang::tr{'edit'})
{
	open( FILE, "< $configfile" ) or die "Unable to read $configfile";
	@configs = <FILE>;
	close FILE;
	open( FILE, "> $configfile" ) or die "Unable to write $configfile";
	foreach $configentry (sort @configs)
	{
		@configline = split( /\;/, $configentry );
  		unless	(($configline[0] eq $outfwsettings{'STATE'}) && 
			($configline[1] eq $outfwsettings{'ENABLED'}) && 
			($configline[2] eq $outfwsettings{'SNET'}) && 
			($configline[3] eq $outfwsettings{'PROT'}) && 
			($configline[4] eq $outfwsettings{'NAME'}) && 
			($configline[5] eq $outfwsettings{'SIP'}) && 
			($configline[6] eq $outfwsettings{'SMAC'}) && 
			($configline[7] eq $outfwsettings{'DIP'}) && 
			($configline[8] eq $outfwsettings{'DPORT'}))
  		{
			print FILE $configentry;
		}
	}
	close FILE;
	$selected{'SNET'}{"$outfwsettings{'SNET'}"} = 'selected';
	$selected{'PROT'}{"$outfwsettings{'PROT'}"} = 'selected';
	&addrule();
	&Header::closebigbox();
	&Header::closepage();
	exit	
}
if ($outfwsettings{'ACTION'} eq $Lang::tr{'delete'})
{
	open( FILE, "< $configfile" ) or die "Unable to read $configfile";
	@configs = <FILE>;
	close FILE;
	open( FILE, "> $configfile" ) or die "Unable to write $configfile";
	foreach $configentry (sort @configs)
	{
		@configline = split( /\;/, $configentry );
  		unless	(($configline[0] eq $outfwsettings{'STATE'}) && 
			($configline[1] eq $outfwsettings{'ENABLED'}) && 
			($configline[2] eq $outfwsettings{'SNET'}) && 
			($configline[3] eq $outfwsettings{'PROT'}) && 
			($configline[4] eq $outfwsettings{'NAME'}) && 
			($configline[5] eq $outfwsettings{'SIP'}) && 
			($configline[6] eq $outfwsettings{'SMAC'}) && 
			($configline[7] eq $outfwsettings{'DIP'}) && 
			($configline[8] eq $outfwsettings{'DPORT'}))
  		{
			print FILE $configentry;
		}
	}
	close FILE;
}
if ($outfwsettings{'ACTION'} eq $Lang::tr{'add'})
{
	if ( $outfwsettings{'VALID'} eq 'yes' ) {
		open( FILE, ">> $configfile" ) or die "Unable to write $configfile";
		print FILE <<END
$outfwsettings{'STATE'};$outfwsettings{'ENABLED'};$outfwsettings{'SNET'};$outfwsettings{'PROT'};$outfwsettings{'NAME'};$outfwsettings{'SIP'};$outfwsettings{'SMAC'};$outfwsettings{'DIP'};$outfwsettings{'DPORT'};
END
;
		close FILE;
	} else {
		$outfwsettings{'ACTION'} = 'Add rule';
	}
}
if ($outfwsettings{'ACTION'} eq 'Add rule')
{
	&addrule();
	exit
}

&General::readhash("${General::swroot}/outgoing/settings", \%outfwsettings);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
}

############################################################################################################################
############################################################################################################################

if ($outfwsettings{'POLICY'} ne 'MODE0'){
	&Header::openbox('100%', 'center', 'Rules');
		print <<END
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<input type='submit' name='ACTION' value='Add rule'>
	</form>
END
;
	open( FILE, "< $configfile" ) or die "Unable to read $configfile";
	@configs = <FILE>;
	close FILE;
	if (@configs) {
		print <<END
		<hr>
		<table border='0' width='100%' cellspacing='0'>
		<tr bgcolor='white'>
		    <td width='14%'><b>Protokoll</b>
		    <td width='14%'><b>Netzwerk</b>
		    <td width='14%'><b>Ziel</b>
		    <td width='14%'><b>Anmerkung</b>
		    <td width='14%'><b>Politik</b>
		    <td width='30%'><b>Aktionen</b>
END
;
		foreach $configentry (sort @configs)
		  	{
		  		@configline = split( /\;/, $configentry );
				$outfwsettings{'STATE'} = $configline[0];
				$outfwsettings{'ENABLED'} = $configline[1];
				$outfwsettings{'SNET'} = $configline[2];
				$outfwsettings{'PROT'} = $configline[3];
				$outfwsettings{'NAME'} = $configline[4];
				$outfwsettings{'SIP'} = $configline[5];
				$outfwsettings{'SMAC'} = $configline[6];
				$outfwsettings{'DIP'} = $configline[7];
				$outfwsettings{'DPORT'} = $configline[8];
				if ($outfwsettings{'DIP'} eq ''){ $outfwsettings{'DISPLAY_DIP'} = 'ALL'; } else { $outfwsettings{'DISPLAY_DIP'} = $outfwsettings{'DIP'}; }
				if ($outfwsettings{'DPORT'} eq ''){ $outfwsettings{'DISPLAY_DPORT'} = 'ALL'; } else { $outfwsettings{'DISPLAY_DPORT'} = $outfwsettings{'DPORT'}; }
				if ($outfwsettings{'STATE'} eq 'DENY'){ $outfwsettings{'DISPLAY_STATE'} = "<img src='/images/stock_stop.png' alt='DENY'>"; }
				if ($outfwsettings{'STATE'} eq 'ALLOW'){ $outfwsettings{'DISPLAY_STATE'} = "<img src='/images/stock_ok.png' alt='ALLOW'>"; }
				if ((($outfwsettings{'POLICY'} eq 'MODE1') && ($outfwsettings{'STATE'} eq 'ALLOW')) || (($outfwsettings{'POLICY'} eq 'MODE2') && ($outfwsettings{'STATE'} eq 'DENY'))){
			  		print <<END
					<tr bgcolor='#F0F0F0'>
					    <td align='center'>$outfwsettings{'PROT'}
					    <td align='center'>$outfwsettings{'SNET'}
					    <td align='center'>$outfwsettings{'DISPLAY_DIP'}:$outfwsettings{'DISPLAY_DPORT'}
					    <td align='center'>$outfwsettings{'NAME'}
					    <td align='center'>$outfwsettings{'DISPLAY_STATE'}
					    <td align='right'>
					     <table border='0' cellpadding='0' cellspacing='0'><tr>
						<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='PROT' value=$outfwsettings{'PROT'}>
							<input type='hidden' name='STATE' value=$outfwsettings{'STATE'}>
							<input type='hidden' name='SNET' value=$outfwsettings{'SNET'}>
							<input type='hidden' name='DPORT' value=$outfwsettings{'DPORT'}>
							<input type='hidden' name='DIP' value=$outfwsettings{'DIP'}>
							<input type='hidden' name='SIP' value=$outfwsettings{'SIP'}>
							<input type='hidden' name='NAME' value=$outfwsettings{'NAME'}>
							<input type='hidden' name='SMAC' value=$outfwsettings{'SMAC'}>
							<input type='hidden' name='ENABLED' value=$outfwsettings{'ENABLED'}>
							<input type='hidden' name='ACTION' value=$Lang::tr{'edit'}>
							<input type='image' src='/images/edit.gif' width="20" height="20" alt=$Lang::tr{'edit'}>
						</form>
						<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='PROT' value=$outfwsettings{'PROT'}>
							<input type='hidden' name='STATE' value=$outfwsettings{'STATE'}>
							<input type='hidden' name='SNET' value=$outfwsettings{'SNET'}>
							<input type='hidden' name='DPORT' value=$outfwsettings{'DPORT'}>
							<input type='hidden' name='DIP' value=$outfwsettings{'DIP'}>
							<input type='hidden' name='SIP' value=$outfwsettings{'SIP'}>
							<input type='hidden' name='NAME' value=$outfwsettings{'NAME'}>
							<input type='hidden' name='SMAC' value=$outfwsettings{'SMAC'}>
							<input type='hidden' name='ENABLED' value=$outfwsettings{'ENABLED'}>
							<input type='hidden' name='ACTION' value=$Lang::tr{'delete'}>
							<input type='image' src='/images/delete.gif' width="20" height="20" alt=$Lang::tr{'delete'}>
						</form></table>
END
;
					if (($outfwsettings{'SIP'}) || ($outfwsettings{'SMAC'})) {
						unless ($outfwsettings{'SIP'}) { $outfwsettings{'DISPLAY_SIP'} = 'ALL'; } else { $outfwsettings{'DISPLAY_SIP'} = $outfwsettings{'SIP'}; }
						unless ($outfwsettings{'SMAC'}) { $outfwsettings{'DISPLAY_SMAC'} = 'ALL'; } else { $outfwsettings{'DISPLAY_SMAC'} = $outfwsettings{'SMAC'}; }
						print <<END
						<tr><td width='14%' align='right'>Quell-IP-Adresse: 
						    <td width='14%' align='left'>$outfwsettings{'DISPLAY_SIP'}
						    <td width='14%' align='right'>Quell-MAC-Adresse:
						    <td width='14%' align='left'>$outfwsettings{'DISPLAY_SMAC'}
						    <td width='44%' colspan='2' align='center'>
END
;
					}
					print <<END
					</form>
END
;
				}
			}
		print <<END
		</table>
END
;

	}
	&Header::closebox();
}

if ($outfwsettings{'POLICY'} eq 'MODE2'){
	open( FILE, "< $p2pfile" ) or die "Unable to read $p2pfile";
	@p2ps = <FILE>;
	close FILE;
	&Header::openbox('100%', 'center', 'P2P-Block');
	print <<END
	<table width='40%'>
		<tr bgcolor='#FFFFFF'><td width='66%'><b>Protokoll</b>
		    <td width='33%'><b>Status</b>
END
;
	my $id = 1;
	foreach $p2pentry (sort @p2ps)
  	{
  		@p2pline = split( /\;/, $p2pentry );
		print <<END
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
END
;
		if ($id % 2) {
			print "\t\t\t<tr bgcolor='#F0F0F0'>\n"; 
		}
		else {
			print "\t\t\t<tr bgcolor='#FAFAFA'>\n";
		}
		$id++;
		print <<END
			<td width='66%' align='center'>$p2pline[0]:	
			<td width='33%' align='center'><input type='hidden' name='P2PROT' value=$p2pline[1]>
END
;
		if ($p2pline[2] eq 'on') {
			print <<END
				<input type='hidden' name='ACTION' value='disable'>
				<input type='image' name='submit' src='/images/stock_ok.png' alt=''>
END
;
		} else {
			print <<END
				<input type='hidden' name='ACTION' value='enable'>
				<input type='image' name='submit' src='/images/stock_stop.png' alt=''>
END
;
		}
		print <<END
			</form>
END
;
	}
	print <<END
	<tr><td colspan='2' align='center'>Klicken Sie auf die Symbole um das entsprechende P2P-Netz zu (de-)aktivieren.
	</table>
END
;
	&Header::closebox();
}

&Header::openbox('100%', 'center', 'Policy');
print <<END
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table width='100%'>
		<tr><td width='10%' align='right'><b>Modus 0:</b><td width='90%' align='left' colspan='2'>In diesem Modus ist es allen Rechnern im Netzwerk uneingeschraenkt moeglich Verbindungen ins Internet aufzubauen.
		<tr><td width='10%' align='right'><b>Modus 1:</b><td width='90%' align='left' colspan='2'>In diesem Modus werden nur Verbindungen nach den oben definierten Regeln zugelassen.
		<tr><td width='10%' align='right'><b>Modus 2:</b><td width='90%' align='left' colspan='2'>In diesem Modus werden saemtliche Verbindungen erlaubt, bis auf die oben definierten Block-Regeln.<br>Hier ist eine Besonderheit der P2P-Filter.
		<tr><td colspan='3'><hr>
		<tr><td width='10%' align='right'>	<select name='POLICY'><option value='MODE0' $selected{'POLICY'}{'MODE0'}>Modus 0</option><option value='MODE1' $selected{'POLICY'}{'MODE1'}>Modus 1</option><option value='MODE2' $selected{'POLICY'}{'MODE2'}>Modus 2</option></select>
		    <td width='45%' align='left'><input type='submit' name='ACTION' value=$Lang::tr{'save'}>
		    <td width='45%' align='right'>
END
;
	if ($outfwsettings{'POLICY'} ne 'MODE0') {
		print <<END
		    Alle Regeln loeschen: <input type='submit' name='ACTION' value=$Lang::tr{'reset'}>
END
;
	}
print <<END
	</table>
	</form>
END
;
&Header::closebox();

&Header::closebigbox();
&Header::closepage();

############################################################################################################################
############################################################################################################################

sub addrule
{
	&Header::openbox('100%', 'center', 'Rules hinzufuegen');
	if ($outfwsettings{'EDIT'} eq 'no') { $selected{'ENABLED'} = 'checked'; }
	print <<END
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table width='80%'>
		<tr><td width='20%' align='right'>Anmerkung: <img src='/blob.gif'>
		    <td width='30%' align='left'><input type='text' name='NAME' maxlength='30' value='$outfwsettings{'NAME'}'>
		    <td width='20%' align='right'>Aktiviert:
		    <td width='30%' align='left'><input type='checkbox' name='ENABLED' $selected{'ENABLED'}>
		<tr><td width='20%' align='right'>Protokoll:
		    <td width='30%' align='left'><select name='PROT'><option value='tcp' $selected{'PROT'}{'tcp'}>TCP</option><option value='tcp&udp' $selected{'PROT'}{'tcp&udp'}>TCP & UDP</option><option value='udp' $selected{'PROT'}{'udp'}>UDP</option></select>
		    <td width='20%' align='right'>Sicherheitspolitik:
		    <td width='30%' align='left'>
END
;
	if ($outfwsettings{'POLICY'} eq 'MODE1'){
		print "\t\t\tALLOW<input type='hidden' name='STATE' value='ALLOW'>\n";
	} elsif ($outfwsettings{'POLICY'} eq 'MODE2'){
		print "\t\t\tDENY<input type='hidden' name='STATE' value='DENY'>\n";
	}
	print <<END
		<tr><td width='20%' align='right'>Quellnetz:
		    <td width='30%' align='left'><select name='SNET'>
			<option value='all' $selected{'SNET'}{'ALL'}>alle</option>
			<option value='ip' $selected{'SNET'}{'ip'}>Quell-IP/MAC benutzen</option>
			<option value='green' $selected{'SNET'}{'green'}>Gruen</option>
END
;
	if (&Header::blue_used()){
		print "\t\t\t<option value='blue' $selected{'SNET'}{'blue'}>Blau</option>\n";
	}
	if (&Header::orange_used()){
		print "\t\t\t<option value='orange' $selected{'SNET'}{'orange'}>Orange</option>\n";
	}
	print <<END
			</select>
		    <td width='20%' align='right'>Quell-IP-Adresse: <img src='/blob.gif'>
		    <td width='30%' align='left'><input type='text' name='SIP' maxlength='15' value='$outfwsettings{'SIP'}'>
		<tr><td width='50%' colspan='2'>&nbsp;
		    <td width='20%' align='right'>Quell-MAC-Adresse: <img src='/blob.gif'>
		    <td width='30%' align='left'><input type='text' name='SMAC' maxlength='23' value='$outfwsettings{'SMAC'}'>
		<tr><td width='20%' align='right'>Ziel-IP-Adresse: <img src='/blob.gif'>
		    <td width='30%' align='left'><input type='text' name='DIP' maxlength='15' value='$outfwsettings{'DIP'}'>
		    <td width='20%' align='right'>Ziel-Port: <img src='/blob.gif'>
		    <td width='30%' align='left'><input type='text' name='DPORT' maxlength='11' value='$outfwsettings{'DPORT'}'>
		<tr><td colspan='4'>
		<tr><td width='40%' align='right' colspan='2'><img src='/blob.gif'> $Lang::tr{'this field may be blank'}
		    <td width='60%' align='left' colspan='2'><input type='submit' name='ACTION' value=$Lang::tr{'add'}>
	</table></form>
END
;
	&Header::closebox();
}

