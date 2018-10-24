#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2011  Michael Tremer & Christian Schmidt                 #
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
require "/opt/pakfire/lib/functions.pl";

my %pakfiresettings=();
my $errormessage = '';
my %color = ();
my %mainsettings = ();

&Header::showhttpheaders();

$pakfiresettings{'ACTION'} = '';
$pakfiresettings{'VALID'} = '';

$pakfiresettings{'INSPAKS'} = '';
$pakfiresettings{'DELPAKS'} = '';
$pakfiresettings{'AUTOUPDATE'} = 'off';
$pakfiresettings{'UUID'} = 'on';

sub refreshpage{&Header::openbox( 'Waiting', 1, "<meta http-equiv='refresh' content='1;'>" );print "<center><img src='/images/clock.gif' alt='' /><br/><font color='red'>$Lang::tr{'pagerefresh'}</font></center>";&Header::closebox();}

&Header::getcgihash(\%pakfiresettings);

&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

&Header::openpage($Lang::tr{'pakfire configuration'}, 1);
&Header::openbigbox('100%', 'left', '', $errormessage);

if ($pakfiresettings{'ACTION'} eq 'install'){
	$pakfiresettings{'INSPAKS'} =~ s/\|/\ /g;
	if ("$pakfiresettings{'FORCE'}" eq "on") {
		my $command = "/usr/local/bin/pakfire install --non-interactive --no-colors $pakfiresettings{'INSPAKS'} &>/dev/null &";
		system("$command");
		system("/bin/sleep 1");
	} else {
		&Header::openbox("100%", "center", $Lang::tr{'request'});
  	my @output = `/usr/local/bin/pakfire resolvedeps --no-colors $pakfiresettings{'INSPAKS'}`;
		print <<END;
		<table><tr><td colspan='2'>$Lang::tr{'pakfire install package'}.$pakfiresettings{'INSPAKS'}.$Lang::tr{'pakfire possible dependency'}
		<pre>
END
		foreach (@output) {
		  $_ =~ s/\\[[0-1]\;[0-9]+m//g;
			print "$_\n";
		}
		print <<END;
		</pre>
		<tr><td colspan='2'>$Lang::tr{'pakfire accept all'}
		<tr><td colspan='2'>&nbsp;
		<tr><td align='right'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='INSPAKS' value='$pakfiresettings{'INSPAKS'}' />
							<input type='hidden' name='FORCE' value='on' />
							<input type='hidden' name='ACTION' value='install' />
							<input type='image' alt='$Lang::tr{'install'}' title='$Lang::tr{'install'}' src='/images/go-next.png' />
						</form>
				<td align='left'>
						<form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='ACTION' value='' />
							<input type='image' alt='$Lang::tr{'abort'}' title='$Lang::tr{'abort'}' src='/images/dialog-error.png' />
						</form>
		</table>
END
		&Header::closebox();
		&Header::closebigbox();
		&Header::closepage();
		exit;
	}
} elsif ($pakfiresettings{'ACTION'} eq 'remove') {

	$pakfiresettings{'DELPAKS'} =~ s/\|/\ /g;
	if ("$pakfiresettings{'FORCE'}" eq "on") {
		my $command = "/usr/local/bin/pakfire remove --non-interactive --no-colors $pakfiresettings{'DELPAKS'} &>/dev/null &";
		system("$command");
		system("/bin/sleep 1");
	} else {
		&Header::openbox("100%", "center", $Lang::tr{'request'});
  	my @output = `/usr/local/bin/pakfire resolvedeps --no-colors $pakfiresettings{'DELPAKS'}`;
		print <<END;
		<table><tr><td colspan='2'>$Lang::tr{'pakfire uninstall package'}.$pakfiresettings{'DELPAKS'}.$Lang::tr{'pakfire possible dependency'}
		<pre>
END
		foreach (@output) {
		  $_ =~ s/\\[[0-1]\;[0-9]+m//g;
			print "$_\n";
		}
		print <<END;
		</pre>
		<tr><td colspan='2'>$Lang::tr{'pakfire accept all'}
		<tr><td colspan='2'>&nbsp;
		<tr><td align='right'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='DELPAKS' value='$pakfiresettings{'DELPAKS'}' />
							<input type='hidden' name='FORCE' value='on' />
							<input type='hidden' name='ACTION' value='remove' />
							<input type='image' alt='$Lang::tr{'uninstall'}' title='$Lang::tr{'uninstall'}' src='/images/go-next.png' />
						</form>
				<td align='left'>
						<form method='post' action='$ENV{'SCRIPT_NAME'}'>
							<input type='hidden' name='ACTION' value='' />
							<input type='image' alt='$Lang::tr{'abort'}' title='$Lang::tr{'abort'}' src='/images/dialog-error.png' />
						</form>
		</table>
END
		&Header::closebox();
		&Header::closebigbox();
		&Header::closepage();
		exit;
	}

} elsif ($pakfiresettings{'ACTION'} eq 'update') {

	system("/usr/local/bin/pakfire update --force --no-colors &>/dev/null &");
	system("/bin/sleep 1");
} elsif ($pakfiresettings{'ACTION'} eq 'upgrade') {
	my $command = "/usr/local/bin/pakfire upgrade -y --no-colors &>/dev/null &";
	system("$command");
	system("/bin/sleep 1");
} elsif ($pakfiresettings{'ACTION'} eq "$Lang::tr{'save'}") {

	if ($pakfiresettings{'AUTOUPDATE'} eq 'on') {
		system("/usr/local/bin/pakfire enable updates >/dev/null 2>&1");
	} else {
		system("/usr/local/bin/pakfire disable updates  >/dev/null 2>&1");
	}

	&General::writehash("${General::swroot}/pakfire/settings", \%pakfiresettings);
}

&General::readhash("${General::swroot}/pakfire/settings", \%pakfiresettings);

my %selected=();
my %checked=();

$checked{'AUTOUPDATE'}{'off'} = '';
$checked{'AUTOUPDATE'}{'on'} = '';
$checked{'AUTOUPDATE'}{$pakfiresettings{'AUTOUPDATE'}} = "checked='checked'";
$checked{'UUID'}{'off'} = '';
$checked{'UUID'}{'on'} = '';
$checked{'UUID'}{$pakfiresettings{'UUID'}} = "checked='checked'";

# DPC move error message to top so it is seen!
if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<font class='base'>$errormessage&nbsp;</font>\n";
	&Header::closebox();
}

my $return = `pidof pakfire`;
chomp($return);
if ($return) {
	&Header::openbox( 'Waiting', 1, "<meta http-equiv='refresh' content='10;'>" );
	print <<END;
	<table>
		<tr><td>
				<img src='/images/indicator.gif' alt='$Lang::tr{'aktiv'}' title='$Lang::tr{'aktiv'}' />&nbsp;
			<td>
				$Lang::tr{'pakfire working'}
		<tr><td colspan='2' align='center'>
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
				<input type='image' alt='$Lang::tr{'reload'}' title='$Lang::tr{'reload'}' src='/images/view-refresh.png' />
			</form>
		<tr><td colspan='2' align='left'><code>
END
	my @output = `grep pakfire /var/log/messages | tail -20`;
	foreach (@output) {
		print "$_<br>";
	}
	print <<END;
			</code>
		</table>
END
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit;
	refreshpage();
}

my $core_release = `cat /opt/pakfire/db/core/mine 2>/dev/null`;
chomp($core_release);
my $core_update_age = &General::age("/opt/pakfire/db/core/mine");
my $corelist_update_age = &General::age("/opt/pakfire/db/lists/core-list.db");
my $server_update_age = &General::age("/opt/pakfire/db/lists/server-list.db");
my $packages_update_age = &General::age("/opt/pakfire/db/lists/packages_list.db");

&Header::openbox("100%", "center", "Pakfire");

print <<END;
	<table width='95%' cellpadding='5' >
END
if ( -e "/var/run/need_reboot") {
	print "<tr><td align='center' colspan='2'><font color='red'>$Lang::tr{'needreboot'}!</font></td></tr>";
	print "<tr><td colspan='2'>&nbsp;</font></td></tr>"
}
print <<END;
		<tr><td width="50%" bgcolor='$color{'color20'}' align="center"><b>$Lang::tr{'pakfire system state'}:</b>
				<td width="50%">
		<tr><td align="center">$Lang::tr{'pakfire core update level'}: $core_release<hr />
					$Lang::tr{'pakfire last update'} $core_update_age $Lang::tr{'pakfire ago'}<br />
					$Lang::tr{'pakfire last serverlist update'} $server_update_age $Lang::tr{'pakfire ago'}<br />
					$Lang::tr{'pakfire last core list update'} $corelist_update_age $Lang::tr{'pakfire ago'}<br />
					$Lang::tr{'pakfire last package update'} $packages_update_age $Lang::tr{'pakfire ago'}
					<form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='ACTION' value='update' />
						<input type='submit' value='$Lang::tr{'calamaris refresh list'}' /><br />
					</form>
				<td align="center">
				 <form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<select name="UPDPAKS" size="5" disabled>
END
						&Pakfire::dblist("upgrade", "forweb");
	print <<END;
					</select>
					<br />
					<input type='hidden' name='ACTION' value='upgrade' />
					<input type='image' alt='$Lang::tr{'upgrade'}' title='$Lang::tr{'upgrade'}' src='/images/document-save.png' />
				 </form>

		<tr><td colspan="2"><!-- Just an empty line -->&nbsp;
		<tr><td bgcolor='$color{'color20'}' align="center"><b>$Lang::tr{'pakfire available addons'}</b>
				<td bgcolor='$color{'color20'}' align="center"><b>$Lang::tr{'pakfire installed addons'}</b>
		<tr><td align="center">
			<p>$Lang::tr{'pakfire install description'}</p>
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
				<select name="INSPAKS" size="10" multiple>
END
			&Pakfire::dblist("notinstalled", "forweb");

print <<END;
				</select>
				<br />
				<input type='hidden' name='ACTION' value='install' />
				<input type='image' alt='$Lang::tr{'install'}' title='$Lang::tr{'install'}' src='/images/list-add.png' />
			</form>

		<td align="center">
			<p>$Lang::tr{'pakfire uninstall description'}</p>
		 <form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<select name="DELPAKS" size="10" multiple>
END

			&Pakfire::dblist("installed", "forweb");

print <<END;
			</select>
			<br />
			<input type='hidden' name='ACTION' value='remove' />
			<input type='image' alt='$Lang::tr{'remove'}' title='$Lang::tr{'remove'}' src='/images/list-remove.png' />
		</form>
	</table>
END

&Header::closebox();
&Header::closebigbox();
&Header::closepage();
