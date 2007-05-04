#!/usr/bin/perl
#
# IPFire CGIs
#
# This file is part of the IPFire Project
# 
# This code is distributed under the terms of the GPL
#
# (c) Eric Oberlander June 2002
#
# (c) Darren Critchley June 2003 - added real time clock setting, etc
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

if ($pakfiresettings{'ACTION'} eq 'install')
{
	my @inspaks = split(/\|/, "$pakfiresettings{'INSPAKS'}");
	&General::writehash("${General::swroot}/pakfire/settings", \%pakfiresettings);
	my @deps = "";
	foreach (@inspaks) {
		push(@deps, $_);
		my @add = split(/ /, `/usr/local/bin/pakfire resolvedeps $_`);
		foreach (@add) { push(@deps, $_); }
	}
	&Header::openbox("100%", "center", "Pakfire");
	print "Wenn sie die Pakete @inspaks installieren wollen müssen sie auch folgende Pakete installieren: @deps";
	&Header::closebox();
	exit 0;
}
elsif ($pakfiresettings{'ACTION'} eq 'remove')
{
	$errormessage = "$pakfiresettings{'DELPAKS'}";
	&General::writehash("${General::swroot}/pakfire/settings", \%pakfiresettings);
} elsif ($pakfiresettings{'ACTION'} eq "$Lang::tr{'save'}")
{
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
				<input type='submit' value='Liste aktualisieren' /><br />
			</form>
			
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
				<input type='hidden' name='ACTION' value='remove' />
				<input type='image' alt='$Lang::tr{'remove'}' src='/images/list-remove.png' />
		</td>
		<td width='40%' align="center">Installierte Addons:<br />
			<select name="DELPAKS" size="10" multiple>
			<option value="postfix">Postfix v2.4.0-1</option>
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

