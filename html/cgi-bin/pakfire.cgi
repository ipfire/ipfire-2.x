#!/usr/bin/perl
#
# IPFire CGIs
#
# This file is part of the IPFire Project
# 
# This code is distributed under the terms of the GPL
#
#

use strict;

# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "/opt/pakfire/lib/functions.pl";

my %pakfiresettings=();
my $errormessage = '';

&Header::showhttpheaders();

$pakfiresettings{'ACTION'} = '';
$pakfiresettings{'VALID'} = '';

$pakfiresettings{'INSPAKS'} = '';
$pakfiresettings{'DELPAKS'} = '';
$pakfiresettings{'AUTOUPDATE'} = '';

&Header::getcgihash(\%pakfiresettings);

&Header::openpage($Lang::tr{'pakfire configuration'}, 1);
&Header::openbigbox('100%', 'left', '', $errormessage);

if ($pakfiresettings{'ACTION'} eq 'install'){
	if ("$pakfiresettings{'FORCE'}" eq "on") {
		system("/usr/local/bin/pakfire", "install", "--non-interactive", "$pakfiresettings{'INSPAKS'}", "&");
		sleep(1);
	} else {
		&Header::openbox("100%", "center", "Abfrage");
		my @output = `/usr/local/bin/pakfire resolvedeps $pakfiresettings{'INSPAKS'}`;
		print <<END;
		<table><tr><td colspan='2'>Sie maechten folgende Pakete installieren: $pakfiresettings{'INSPAKS'}. Moeglicherweise haben diese Pakete Abhaengigkeiten, d.h. andere Pakete muessen zusaetzlich installiert werden. Dazu sehen sie unten eine Liste.
		<pre>		
END
		foreach (@output) {
			print "$_\n";
		}
		print <<END;
		</pre>
		<tr><td colspan='2'>Moechten Sie der Installation aller Pakete zustimmen?
		<tr><td colspan='2'>&nbsp;
		<tr><td align='right'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='INSPAKS' value='$pakfiresettings{'INSPAKS'}' />
							<input type='hidden' name='FORCE' value='on' />
							<input type='hidden' name='ACTION' value='install' />
							<input type='image' alt='$Lang::tr{'install'}' src='/images/go-next.png' />
						</form>
				<td align='left'>
						<form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='ACTION' value='' />
							<input type='image' alt='$Lang::tr{'abort'}' src='/images/dialog-error.png' />
						</form>
		</table>
END
		&Header::closebox();
		&Header::closebigbox();
		&Header::closepage();
		exit;
	}
} elsif ($pakfiresettings{'ACTION'} eq 'remove') {

} elsif ($pakfiresettings{'ACTION'} eq 'update') {
	
	system("/usr/local/bin/pakfire update --force");

} elsif ($pakfiresettings{'ACTION'} eq 'unlock') {
	
	&Pakfire::lock("off");
	
} elsif ($pakfiresettings{'ACTION'} eq "$Lang::tr{'save'}") {

	&General::writehash("${General::swroot}/pakfire/settings", \%pakfiresettings);
}

&General::readhash("${General::swroot}/pakfire/settings", \%pakfiresettings);

my %selected=();
my %checked=();

$checked{'AUTOUPDATE'}{'off'} = '';
$checked{'AUTOUPDATE'}{'on'} = '';
$checked{'AUTOUPDATE'}{$pakfiresettings{'AUTOUPDATE'}} = "checked='checked'";

# DPC move error message to top so it is seen!
if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<font class='base'>$errormessage&nbsp;</font>\n";
	&Header::closebox();
}

if ( -e "/opt/pakfire/pakfire.lock" ) {
	&Header::openbox("100%", "center", "Aktiv");
	print <<END;
	<table>
		<tr><td>
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
				<input type='hidden' name='ACTION' value='unlock' />
				<input type='image' src='/images/indicator.gif' alt='$Lang::tr{'aktiv'}' />&nbsp;
			</form>
			<td>
				Pakfire fuehrt gerade eine Aufgabe aus... Bitte warten sie, bis diese erfolgreich beendet wurde.
		<tr><td colspan='2' align='center'>
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
				<input type='image' alt='$Lang::tr{'reload'}' src='/images/view-refresh.png' />
			</form>
	</table>
END
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit;
}

&Header::openbox("100%", "center", "Pakfire");

print <<END;
	<table width='100%'>
		<tr><td width='40%' align="center">Verfuegbare Addons:<br />
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
				<select name="INSPAKS" size="10" multiple>
END
			&Pakfire::dblist("notinstalled", "forweb");
		
print <<END;
				</select>
		</td>
		<td width='20%' align="center">
				<input type='hidden' name='ACTION' value='install' />
				<input type='image' alt='$Lang::tr{'install'}' src='/images/list-add.png' />
			</form><br />
			
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
				<input type='hidden' name='ACTION' value='update' />
				<input type='submit' value='Liste aktualisieren' /><br />
			</form>
			
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
				<input type='hidden' name='ACTION' value='remove' />
				<input type='image' alt='$Lang::tr{'remove'}' src='/images/list-remove.png' />
		</td>
		<td width='40%' align="center">Installierte Addons:<br />
			<select name="DELPAKS" size="10" multiple>
END

			&Pakfire::dblist("installed", "forweb");

print <<END;
		</select>
	</table></form>
		<br /><hr /><br />
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='100%'>
			<tr><td width='40%' align="right">Automatische Updates taeglich ausfuehren:
					<td width='10%' align="left"><input type="checkbox" name="AUTOUPDATE" $checked{'AUTOUPDATE'}{'on'} />
					<td width='40%' align="right">Test:
					<td width='10%' align="left"><input type="checkbox" name="AUTOUPDATE" $checked{'AUTOUPDATE'}{'on'} />
			<tr><td width='100%' colspan="4" align="right"><input type="submit" name="ACTION" value="$Lang::tr{'save'}" />					
		</table>
	</form>
END

&Header::closebox();
&Header::closebigbox();
&Header::closepage();
