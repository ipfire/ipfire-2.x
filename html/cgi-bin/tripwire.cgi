#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007  Michael Tremer & Christian Schmidt                      #
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

my %tripwiresettings = ();
my %checked = ();
my %netsettings = ();
my $message = "";
my $errormessage = "";
my @Logs = `ls -r /var/ipfire/tripwire/report/ 2>/dev/null`;
my $file = `ls -tr /var/ipfire/tripwire/report/ | tail -1 2>/dev/null`;
my @cronjobs = `ls /etc/fcron.daily/tripwire* 2>/dev/null`;
my $Log =$Lang::tr{'no log selected'};

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

############################################################################################################################
################################################# Tripwire Default Variablen ################################################

$tripwiresettings{'ROOT'} = '/usr/sbin';
$tripwiresettings{'POLFILE'} = '/var/ipfire/tripwire/tw.pol';
$tripwiresettings{'DBFILE'} = '/var/ipfire/tripwire/$(HOSTNAME).twd';
$tripwiresettings{'REPORTFILE'} = '/var/ipfire/tripwire/report/$(DATE).twr';
$tripwiresettings{'SITEKEYFILE'} = '/var/ipfire/tripwire/site.key';
$tripwiresettings{'LOCALKEYFILE'} = '/var/ipfire/tripwire/local.key';
$tripwiresettings{'EDITOR'} = '/usr/bin/vi';
$tripwiresettings{'LATEPROMPTING'} = 'false';
$tripwiresettings{'LOOSEDIRECTORYCHECKING'} = 'false';
$tripwiresettings{'MAILNOVIOLATIONS'} = 'false';
$tripwiresettings{'EMAILREPORTLEVEL'} = '3';
$tripwiresettings{'REPORTLEVEL'} = '3';
$tripwiresettings{'MAILMETHOD'} = 'SENDMAIL';
$tripwiresettings{'SMTPHOST'} = 'ipfire.myipfire.de';
$tripwiresettings{'SMTPPORT'} = '25';
$tripwiresettings{'SYSLOGREPORTING'} = 'false';
$tripwiresettings{'MAILPROGRAM'} = '/usr/sbin/sendmail -oi -t';
$tripwiresettings{'SITEKEY'} = 'ipfire';
$tripwiresettings{'LOCALKEY'} = 'ipfire';
$tripwiresettings{'ACTION'} = '';

&General::readhash("${General::swroot}/tripwire/settings", \%tripwiresettings);

############################################################################################################################
######################################################### Tripwire HTML Part ###############################################

&Header::showhttpheaders();

&Header::getcgihash(\%tripwiresettings);
&Header::openpage('Tripwire', 1,);
&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
############################################### Tripwire Config Datei erstellen ############################################

if ($tripwiresettings{'ACTION'} eq $Lang::tr{'save'})
{
system("/usr/local/bin/tripwirectrl readconfig  >/dev/null 2>&1");
open (FILE, ">${General::swroot}/tripwire/twcfg.txt") or die "Can't save tripwire config: $!";
flock (FILE, 2);

print FILE <<END

ROOT                   =$tripwiresettings{'ROOT'}
POLFILE                =$tripwiresettings{'POLFILE'}
DBFILE                 =$tripwiresettings{'DBFILE'}
REPORTFILE             =$tripwiresettings{'REPORTFILE'}
SITEKEYFILE            =$tripwiresettings{'SITEKEYFILE'}
LOCALKEYFILE           =$tripwiresettings{'LOCALKEYFILE'}
EDITOR                 =$tripwiresettings{'EDITOR'}
LATEPROMPTING          =$tripwiresettings{'LATEPROMPTING'}
LOOSEDIRECTORYCHECKING =$tripwiresettings{'LOOSEDIRECTORYCHECKING'}
MAILNOVIOLATIONS       =$tripwiresettings{'MAILNOVIOLATIONS'}
EMAILREPORTLEVEL       =$tripwiresettings{'EMAILREPORTLEVEL'}
REPORTLEVEL            =$tripwiresettings{'REPORTLEVEL'}
MAILMETHOD             =$tripwiresettings{'MAILMETHOD'}
SMTPHOST               =$tripwiresettings{'SMTPHOST'}
SMTPPORT               =$tripwiresettings{'SMTPPORT'}
SYSLOGREPORTING        =$tripwiresettings{'SYSLOGREPORTING'}
MAILPROGRAM            =$tripwiresettings{'MAILPROGRAM'}

END
;
close FILE;

&General::writehash("${General::swroot}/tripwire/settings", \%tripwiresettings);
system("/usr/local/bin/tripwirectrl lockconfig  >/dev/null 2>&1");
}

############################################################################################################################
################################################## Sicherheitsabfrage für CGI ##############################################

if ($tripwiresettings{'ACTION'} eq 'addcron')
	{
	print <<END
	<br />
	<table width='95%' cellspacing='0'>
	<tr><td bgcolor='$color{'color20'}' colspan='2' align='center'><b>$Lang::tr{'add cron'}</b>
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<tr><td align='center' colspan='2'>HH<input type='text' size='2' name='HOUR' value='08'/>MM<input type='text' size='2' name='MINUTE' value='00'/><br /><br /></td></tr>
	<tr><td align='right' width='50%'>
					 $Lang::tr{'ok'} <input type='image' alt='$Lang::tr{'ok'}' title='$Lang::tr{'ok'}' src='/images/edit-redo.png' />
					<input type='hidden' name='ACTION' value='addcronyes' /></form></td>
			<td align='left'  width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='image' alt='$Lang::tr{'cancel'}' title='$Lang::tr{'cancel'}' src='/images/dialog-error.png' /> $Lang::tr{'cancel'} 
					<input type='hidden' name='ACTION' value='cancel' /></form></td>
	</tr>
	</table>
END
;
}

if ($tripwiresettings{'ACTION'} eq 'globalreset')
	{
	print <<END
	<br />
	<table width='95%' cellspacing='0'>
	<tr><td bgcolor='$color{'color20'}' colspan='2' align='center'><b>$Lang::tr{'resetglobals'}</b>
	<tr><td colspan='2' align='center'><font color=red>$Lang::tr{'defaultwarning'}<br /><br /></font></td></tr>
	<tr><td align='right' width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					 $Lang::tr{'ok'} <input type='image' alt='$Lang::tr{'ok'}' title='$Lang::tr{'ok'}' src='/images/edit-redo.png' />
					<input type='hidden' name='ACTION' value='globalresetyes' /></form></td>
			<td align='left'  width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='image' alt='$Lang::tr{'cancel'}' title='$Lang::tr{'cancel'}' src='/images/dialog-error.png' /> $Lang::tr{'cancel'} 
					<input type='hidden' name='ACTION' value='cancel' /></form></td>
	</tr>
	</table>
END
;
}

if ($tripwiresettings{'ACTION'} eq 'generatepolicypw')
	{
	print <<END
	<br />
	<table width='95%' cellspacing='0'>
	<tr><td bgcolor='$color{'color20'}' colspan='2' align='center'><b>$Lang::tr{'generatepolicy'}</b>
	<tr><td colspan='2' align='center'><font color=red>$Lang::tr{'tripwirewarningpolicy'}<br /><br /></font></td></tr>
	<tr><td align='left' width='40%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>$Lang::tr{'sitekey'}</td><td align='left'><input type='password' name='SITEKEY' value='$tripwiresettings{'SITEKEY'}' size="30" /></td></tr>
	<tr><td align='left' width='40%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>$Lang::tr{'localkey'}</td><td align='left'><input type='password' name='LOCALKEY' value='$tripwiresettings{'LOCALKEY'}' size="30" /><br /><br /></td></tr>
	<tr><td align='right' width='50%'>
					 $Lang::tr{'ok'} <input type='image' alt='$Lang::tr{'ok'}' tilte='$Lang::tr{'ok'}' src='/images/edit-redo.png' />
					<input type='hidden' name='ACTION' value='generatepolicyyes' /></form></td>
			<td align='left'  width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='image' alt='$Lang::tr{'cancel'}' title='$Lang::tr{'cancel'}' src='/images/dialog-error.png' /> $Lang::tr{'cancel'} 
					<input type='hidden' name='ACTION' value='cancel' /></form></td>
	</tr>
	</table>
END
;
}

if ($tripwiresettings{'ACTION'} eq 'policyresetpw')
	{
	print <<END
	<br />
	<table width='95%' cellspacing='0'>
	<tr><td bgcolor='$color{'color20'}' colspan='2' align='center'><b>$Lang::tr{'resetpolicy'}</b>
	<tr><td colspan='2' align='center'><font color=red>$Lang::tr{'tripwirewarningpolicy'}<br /><br /></font></td></tr>
	<tr><td align='left' width='40%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>$Lang::tr{'sitekey'}</td><td align='left'><input type='password' name='SITEKEY' value='$tripwiresettings{'SITEKEY'}' size="30" /></td></tr>
	<tr><td align='left' width='40%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>$Lang::tr{'localkey'}</td><td align='left'><input type='password' name='LOCALKEY' value='$tripwiresettings{'LOCALKEY'}' size="30" /><br /><br /></td></tr>
	<tr><td align='right' width='50%'>
					 $Lang::tr{'ok'} <input type='image' alt='$Lang::tr{'ok'}' title='$Lang::tr{'ok'}' src='/images/edit-redo.png' />
					<input type='hidden' name='ACTION' value='resetpolicyyes' /></form></td>
			<td align='left'  width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='image' alt='$Lang::tr{'cancel'}' title='$Lang::tr{'cancel'}' src='/images/dialog-error.png' /> $Lang::tr{'cancel'} 
					<input type='hidden' name='ACTION' value='cancel' /></form></td>
	</tr>
	</table>
END
;
}

if ($tripwiresettings{'ACTION'} eq 'updatedatabasepw')
	{
	print <<END
	<br />
	<table width='95%' cellspacing='0'>
	<tr><td bgcolor='$color{'color20'}' colspan='2' align='center'><b>$Lang::tr{'updatedatabase'}</b>
	<tr><td colspan='2' align='center'><font color=red>$Lang::tr{'tripwirewarningdatabase'}<br /><br /></font></td></tr>
	<tr><td align='left' width='40%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>$Lang::tr{'localkey'}</td><td align='left'><input type='password' name='LOCALKEY' value='$tripwiresettings{'LOCALKEY'}' size="30" /><br /><br /></td></tr>
	<tr><td align='right' width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					 $Lang::tr{'ok'} <input type='image' alt='$Lang::tr{'ok'}' title='$Lang::tr{'ok'}' src='/images/edit-redo.png' />
					<input type='hidden' name='ACTION' value='updatedatabaseyes' /></form></td>
			<td align='left'  width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='image' alt='$Lang::tr{'cancel'}' title='$Lang::tr{'cancel'}' src='/images/dialog-error.png' /> $Lang::tr{'cancel'} 
					<input type='hidden' name='ACTION' value='cancel' /></form></td>
	</tr>
	</table>
END
;
}
if ($tripwiresettings{'ACTION'} eq 'keyreset')
	{
	print <<END
	<br />
	<table width='95%' cellspacing='0'>
	<tr><td bgcolor='$color{'color20'}' colspan='2' align='center'><b>$Lang::tr{'keyreset'}</b>
	<tr><td colspan='2' align='center'><font color=red>$Lang::tr{'tripwirewarningkeys'}<br /><br /></font></td></tr>
	<tr><td align='right' width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					 $Lang::tr{'ok'} <input type='image' alt='$Lang::tr{'ok'}' title='$Lang::tr{'ok'}' src='/images/edit-redo.png' />
					<input type='hidden' name='ACTION' value='keyresetyes' /></form></td>
			<td align='left'  width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='image' alt='$Lang::tr{'cancel'}' title='$Lang::tr{'cancel'}' src='/images/dialog-error.png' /> $Lang::tr{'cancel'} 
					<input type='hidden' name='ACTION' value='cancel' /></form></td>
	</tr>
	</table>
END
;
}

if ($tripwiresettings{'ACTION'} eq 'generatekeys')
	{
	print <<END
	<br />
	<table width='95%' cellspacing='0'>
	<tr><td bgcolor='$color{'color20'}' colspan='2' align='center'><b>$Lang::tr{'generatekeys'}</b>
	<tr><td colspan='2' align='center'><font color=red>$Lang::tr{'tripwirewarningkeys'}<br /><br /></font></td></tr>
	<tr><td align='right' width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					 $Lang::tr{'ok'} <input type='image' alt='$Lang::tr{'ok'}' title='$Lang::tr{'ok'}' src='/images/edit-redo.png' />
					<input type='hidden' name='ACTION' value='generatekeysyes' /></form></td>
			<td align='left'  width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='image' alt='$Lang::tr{'cancel'}' title='$Lang::tr{'cancel'}' src='/images/dialog-error.png' /> $Lang::tr{'cancel'} 
					<input type='hidden' name='ACTION' value='cancel' /></form></td>
	</tr>
	</table>
END
;
}

############################################################################################################################
######################################################## Tripwire Funktionen ###############################################

if ($tripwiresettings{'ACTION'} eq 'globalresetyes')
{
&Header::openbox( 'Waiting', 1, "<meta http-equiv='refresh' content='1;'>" );print "<center><img src='/images/clock.gif' alt='' /><br/><font color='red'>$Lang::tr{'tripwireoperating'}</font></center>";&Header::closebox();
$tripwiresettings{'ROOT'} = '/usr/sbin';
$tripwiresettings{'POLFILE'} = '/var/ipfire/tripwire/tw.pol';
$tripwiresettings{'DBFILE'} = '/var/ipfire/tripwire/$(HOSTNAME).twd';
$tripwiresettings{'REPORTFILE'} = '/var/ipfire/tripwire/report/$(DATE).twr';
$tripwiresettings{'SITEKEYFILE'} = '/var/ipfire/tripwire/site.key';
$tripwiresettings{'LOCALKEYFILE'} = '/var/ipfire/tripwire/local.key';
$tripwiresettings{'EDITOR'} = '/usr/bin/vi';
$tripwiresettings{'LATEPROMPTING'} = 'false';
$tripwiresettings{'LOOSEDIRECTORYCHECKING'} = 'false';
$tripwiresettings{'MAILNOVIOLATIONS'} = 'false';
$tripwiresettings{'EMAILREPORTLEVEL'} = '3';
$tripwiresettings{'REPORTLEVEL'} = '3';
$tripwiresettings{'MAILMETHOD'} = 'SENDMAIL';
$tripwiresettings{'SMTPHOST'} = 'ipfire.myipfire.de';
$tripwiresettings{'SMTPPORT'} = '25';
$tripwiresettings{'SYSLOGREPORTING'} = 'false';
$tripwiresettings{'MAILPROGRAM'} = '/usr/sbin/sendmail -oi -t';
$tripwiresettings{'SITEKEY'} = 'ipfire';
$tripwiresettings{'LOCALKEY'} = 'ipfire';
$tripwiresettings{'ACTION'} = '';
system("/usr/local/bin/tripwirectrl readconfig  >/dev/null 2>&1");
open (FILE, ">${General::swroot}/tripwire/twcfg.txt") or die "Can't save tripwire config: $!";
flock (FILE, 2);
print FILE <<END

ROOT                   =$tripwiresettings{'ROOT'}
POLFILE                =$tripwiresettings{'POLFILE'}
DBFILE                 =$tripwiresettings{'DBFILE'}
REPORTFILE             =$tripwiresettings{'REPORTFILE'}
SITEKEYFILE            =$tripwiresettings{'SITEKEYFILE'}
LOCALKEYFILE           =$tripwiresettings{'LOCALKEYFILE'}
EDITOR                 =$tripwiresettings{'EDITOR'}
LATEPROMPTING          =$tripwiresettings{'LATEPROMPTING'}
LOOSEDIRECTORYCHECKING =$tripwiresettings{'LOOSEDIRECTORYCHECKING'}
MAILNOVIOLATIONS       =$tripwiresettings{'MAILNOVIOLATIONS'}
EMAILREPORTLEVEL       =$tripwiresettings{'EMAILREPORTLEVEL'}
REPORTLEVEL            =$tripwiresettings{'REPORTLEVEL'}
MAILMETHOD             =$tripwiresettings{'MAILMETHOD'}
SMTPHOST               =$tripwiresettings{'SMTPHOST'}
SMTPPORT               =$tripwiresettings{'SMTPPORT'}
SYSLOGREPORTING        =$tripwiresettings{'SYSLOGREPORTING'}
MAILPROGRAM            =$tripwiresettings{'MAILPROGRAM'}

END
;
close FILE;
&General::writehash("${General::swroot}/tripwire/settings", \%tripwiresettings);
system("/usr/local/bin/tripwirectrl lockconfig  >/dev/null 2>&1l");
system("/usr/local/bin/tripwirectrl keys ipfire ipfire  >/dev/null 2>&1");$tripwiresettings{'SITEKEY'} = 'ipfire';$tripwiresettings{'LOCALKEY'} = 'ipfire';
}
if ($tripwiresettings{'ACTION'} eq 'generatekeysyes'){&Header::openbox( 'Waiting', 1, "<meta http-equiv='refresh' content='1;'>" );print "<center><img src='/images/clock.gif' alt='' /><br/><font color='red'>$Lang::tr{'tripwireoperating'}</font></center>";system("/usr/local/bin/tripwirectrl keys $tripwiresettings{'SITEKEY'} $tripwiresettings{'LOCALKEY'}  >/dev/null 2>&1");$tripwiresettings{'SITEKEY'} = 'ipfire';$tripwiresettings{'LOCALKEY'} = 'ipfire';}
if ($tripwiresettings{'ACTION'} eq 'keyresetyes'){&Header::openbox( 'Waiting', 1, "<meta http-equiv='refresh' content='1;'>" );print "<center><img src='/images/clock.gif' alt='' /><br/><font color='red'>$Lang::tr{'tripwireoperating'}</font></center>";system("/usr/local/bin/tripwirectrl keys ipfire ipfire  >/dev/null 2>&1");$tripwiresettings{'SITEKEY'} = 'ipfire';$tripwiresettings{'LOCALKEY'} = 'ipfire';}
if ($tripwiresettings{'ACTION'} eq 'resetpolicyyes'){&Header::openbox( 'Waiting', 1, "<meta http-equiv='refresh' content='1;'>" );print "<center><img src='/images/clock.gif' alt='' /><br/><font color='red'>$Lang::tr{'tripwireoperating'}</font></center>";system("/usr/local/bin/tripwirectrl resetpolicy tripwiresettings{'SITEKEY'} $tripwiresettings{'LOCALKEY'}  >/dev/null 2>&1");$tripwiresettings{'SITEKEY'} = 'ipfire';$tripwiresettings{'LOCALKEY'} = 'ipfire';}
if ($tripwiresettings{'ACTION'} eq 'generatepolicyyes'){&Header::openbox( 'Waiting', 1, "<meta http-equiv='refresh' content='1;'>" );print "<center><img src='/images/clock.gif' alt='' /><br/><font color='red'>$Lang::tr{'tripwireoperating'}</font></center>";system("/usr/local/bin/tripwirectrl generatepolicy $tripwiresettings{'SITEKEY'} $tripwiresettings{'LOCALKEY'}  >/dev/null 2>&1");$tripwiresettings{'SITEKEY'} = 'ipfire';$tripwiresettings{'LOCALKEY'} = 'ipfire';}
if ($tripwiresettings{'ACTION'} eq 'updatedatabaseyes'){&Header::openbox( 'Waiting', 1, "<meta http-equiv='refresh' content='1;'>" );print "<center><img src='/images/clock.gif' alt='' /><br/><font color='red'>$Lang::tr{'tripwireoperating'}</font></center>";system("/usr/local/bin/tripwirectrl updatedatabase $tripwiresettings{'LOCALKEY'} /var/ipfire/tripwire/report/$file  >/dev/null 2>&1");$tripwiresettings{'LOCALKEY'} = 'ipfire';}
if ($tripwiresettings{'ACTION'} eq 'generatereport'){&Header::openbox( 'Waiting', 1, "<meta http-equiv='refresh' content='1;'>" );print "<center><img src='/images/clock.gif' alt='' /><br/><font color='red'>$Lang::tr{'tripwireoperating'}</font></center>";system("/usr/local/bin/tripwirectrl generatereport  >/dev/null 2>&1");}
if ($tripwiresettings{'ACTION'} eq 'addcronyes'){system("/usr/local/bin/tripwirectrl addcron $tripwiresettings{'HOUR'} $tripwiresettings{'MINUTE'}  >/dev/null 2>&1");}
if ($tripwiresettings{'ACTION'} eq 'deletecron'){system("/usr/local/bin/tripwirectrl disablecron $tripwiresettings{'CRON'} >/dev/null 2>&1");@cronjobs = `ls /etc/fcron.daily/tripwire* 2>/dev/null`;}

############################################################################################################################
##################################################### Tripwire globale Optionen ############################################

&Header::openbox('100%', 'center', 'Tripwire');
print <<END
<br />

<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='95%' cellspacing='0'>
<tr bgcolor='$color{'color20'}'><td colspan='2' align='left'><b>$Lang::tr{'basic options'}</b></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'emailreportlevel'}</td><td align='left'><input type='text' name='EMAILREPORTLEVEL' value='$tripwiresettings{'EMAILREPORTLEVEL'}' size="30" /></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'reportlevel'}</td><td align='left'><input type='text' name='REPORTLEVEL' value='$tripwiresettings{'REPORTLEVEL'}' size="30" /></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'mailmethod'}</td><td align='left'><input type='text' name='MAILMETHOD' value='$tripwiresettings{'MAILMETHOD'}' size="30" /></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'smtphost'}</td><td align='left'><input type='text' name='SMTPHOST' value='$tripwiresettings{'SMTPHOST'}' size="30" /></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'smtpport'}</td><td align='left'><input type='text' name='SMTPPORT' value='$tripwiresettings{'SMTPPORT'}' size="30" /></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'mailprogramm'}</td><td align='left'><input type='text' name='MAILPROGRAM' value='$tripwiresettings{'MAILPROGRAM'}' size="30" /></td></tr>
</table>
<br />
<table width='10%' cellspacing='0'>
<tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value=$Lang::tr{'save'} />
												<input type='image' alt='$Lang::tr{'save'}' title='$Lang::tr{'save'}' src='/images/media-floppy.png' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
										<input type='hidden' name='ACTION' value='globalreset' />
										<input type='image' alt='$Lang::tr{'reset'}' title='$Lang::tr{'reset'}' src='/images/reload.gif' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
										<input type='hidden' name='ACTION' value='globalcaption' />
										<input type='image' alt='$Lang::tr{'caption'}' title='$Lang::tr{'caption'}' src='/images/help-browser.png' /></form></td></tr>
</table>
</from>
END
;
if ($tripwiresettings{'ACTION'} eq 'globalcaption')
{
print <<END
<br />
<table width='95%' cellspacing='0'>
<tr><td align='center' colspan='2'><b>$Lang::tr{'caption'}</b></td></tr>
<tr><td align='right' width='33%'><img src='/images/media-floppy.png' alt='$Lang::tr{'save settings'}' /></td><td align='left'>$Lang::tr{'save settings'}</td></tr>
<tr><td align='right' width='33%'><img src='/images/reload.gif' alt='$Lang::tr{'restore settings'}' /></td><td align='left'>$Lang::tr{'restore settings'}</td></tr>
</table>
END
;

}

&Header::closebox();

############################################################################################################################
################################################### Tripwire Init Policy and keygen ########################################

&Header::openbox('100%', 'center', $Lang::tr{'generate tripwire keys and init'});
print <<END
<br />

<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='95%' cellspacing='0'>
<tr bgcolor='$color{'color20'}'><td colspan='2' align='left'><b>$Lang::tr{'keys'}</b></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'sitekey'}</td><td align='left'><input type='password' name='SITEKEY' value='$tripwiresettings{'SITEKEY'}' size="30" /></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'localkey'}</td><td align='left'><input type='password' name='LOCALKEY' value='$tripwiresettings{'LOCALKEY'}' size="30" /></td></tr>
</table>
<br />
<table width='10%' cellspacing='0'>
<tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value='generatekeys'/>
												<input type='image' alt='$Lang::tr{'generatekeys'}' title='$Lang::tr{'generatekeys'}' src='/images/system-lock-screen.png' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
										<input type='hidden' name='ACTION' value='keyreset' />
										<input type='image' alt='$Lang::tr{'reset'}' title='$Lang::tr{'reset'}' src='/images/reload.gif' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
										<input type='hidden' name='ACTION' value='keycaption' />
										<input type='image' alt='$Lang::tr{'caption'}' title='$Lang::tr{'caption'}' src='/images/help-browser.png' /></form></td></tr>
</table>
</from>
END
;
if ($tripwiresettings{'ACTION'} eq 'keycaption')
{
print <<END
<br />
<table width='95%' cellspacing='0'>
<tr><td align='center' colspan='2'><b>$Lang::tr{'caption'}</b></td></tr>
<tr><td align='right' width='33%'><img src='/images/system-lock-screen.png' alt='$Lang::tr{'generatekeys'}' /></td><td align='left'>$Lang::tr{'generatekeys'}</td></tr>
<tr><td align='right' width='33%'><img src='/images/reload.gif' alt='$Lang::tr{'keyreset'}' /></td><td align='left'>$Lang::tr{'keyreset'}</td></tr>
</table>
END
;

}

&Header::closebox();

############################################################################################################################
################################################# Tripwire general functions ###############################################

&Header::openbox('100%', 'center', $Lang::tr{'tripwire functions'});
print <<END
<br />

<table width='95%' cellspacing='0'>
<tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value='generatepolicypw'/>
												<input type='image' alt='$Lang::tr{'generatepolicy'}' title='$Lang::tr{'generatepolicy'}' src='/images/document-new.png' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
										<input type='hidden' name='ACTION' value='policyresetpw' />
										<input type='image' alt='$Lang::tr{'resetpolicy'}' title='$Lang::tr{'resetpolicy'}' src='/images/reload.gif' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
										<input type='hidden' name='ACTION' value='generatereport' />
										<input type='image' alt='$Lang::tr{'generatereport'}' title='$Lang::tr{'generatereport'}' src='/images/document-properties.png' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
										<input type='hidden' name='ACTION' value='updatedatabasepw' />
										<input type='image' alt='$Lang::tr{'updatedatabase'}' title='$Lang::tr{'updatedatabase'}' src='/images/network-server.png' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
										<input type='hidden' name='ACTION' value='policycaption' />
										<input type='image' alt='$Lang::tr{'caption'}' title='$Lang::tr{'caption'}' src='/images/help-browser.png' /></form></td></tr>
</table>
END
;
if ($tripwiresettings{'ACTION'} eq 'policycaption')
{
print <<END
<br />
<table width='95%' cellspacing='0'>
<tr><td align='center' colspan='2'><b>$Lang::tr{'caption'}</b></td></tr>
<tr><td align='right' width='33%'><img src='/images/document-new.png' alt='$Lang::tr{'generatepolicy'}' /></td><td align='left'>$Lang::tr{'generatepolicy'}</td></tr>
<tr><td align='right' width='33%'><img src='/images/reload.gif' alt='$Lang::tr{'resetpolicy'}' /></td><td align='left'>$Lang::tr{'resetpolicy'}</td></tr>
<tr><td align='right' width='33%'><img src='/images/document-properties.png' alt='$Lang::tr{'generatereport'}' /></td><td align='left'>$Lang::tr{'generatereport'}</td></tr>
<tr><td align='right' width='33%'><img src='/images/network-server.png' alt='$Lang::tr{'updatedatabase'}' /></td><td align='left'>$Lang::tr{'updatedatabase'}</td></tr>
</table>
END
;

}
&Header::closebox();

############################################################################################################################
####################################################### Tripwire Log View ##################################################

&Header::openbox('100%', 'center', $Lang::tr{'tripwire reports'});
print <<END
<a name="$Lang::tr{'log view'}"</a>
<br />
<form method='post' action='$ENV{'SCRIPT_NAME'}#$Lang::tr{'log view'}'>
<table width='95%' cellspacing='0'>
<tr><td bgcolor='$color{'color20'}' colspan='3' align='left'><b>$Lang::tr{'log view'}</b></td></tr>
<tr><td colspan='3'  align='left'><br /></td></tr>
<tr><td  align='left'><select name='LOG' style="width: 500px">
END
;
foreach my $log (@Logs) {chomp $log;print"<option value='$log'>$log</option>";}
print <<END

</select></td><td  align='left'><input type='hidden' name='ACTION' value='showlog' /><input type='image' alt='view Log' title='view log' src='/images/format-justify-fill.png' /></td></tr>
</table>
</form>
END
;
if ($tripwiresettings{'ACTION'} eq 'showlog')
{
$Log = qx(/usr/local/bin/tripwirectrl tripwirelog $tripwiresettings{'LOG'});
$Log=~s/--cfgfile \/var\/ipfire\/tripwire\/tw.cfg --polfile \/var\/ipfire\/tripwire\/tw.pol//g;
print <<END
<table width='95%' cellspacing='0'>
<tr><td><br /></td></tr>
<tr><td><pre>$Log</pre></td></tr>
<tr><td><br /></td></tr>
<tr><td align='center'>$tripwiresettings{'LOG'}</td></tr>
</table>
END
;

}

&Header::closebox();

############################################################################################################################
####################################################### Tripwire Cronjob ##################################################
#
#&Header::openbox('100%', 'center', $Lang::tr{'tripwire cronjob'});
#print <<END
#<br />
#<table width='95%' cellspacing='0'>
#<tr><td colspan='3'  align='left'><br /></td></tr>
#END
#;
#foreach my $cronjob (@cronjobs) {chomp $cronjob;my $time=$cronjob; $time=~s/\/etc\/fcron.daily\/tripwire//g;print"<form method='post' action='$ENV{'SCRIPT_NAME'}'><tr><td  align='left' colspan='2'>$cronjob at $time daily</td><td><input type='hidden' name='ACTION' value='deletecron' /><input type='hidden' name='CRON' value='$time' /><input type='image' alt='delete cron' src='/images/user-trash.png' /></td></tr></form>";}
#print <<END
#</table>
#<br />
#<table width='10%' cellspacing='0'>
#<tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
#												<input type='hidden' name='ACTION' value='addcron'/>
#												<input type='image' alt='$Lang::tr{'add cron'}' src='/images/appointment-new.png' /></form></td>
#<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
#										<input type='hidden' name='ACTION' value='croncaption' />
#										<input type='image' alt='$Lang::tr{'caption'}' src='/images/help-browser.png' /></form></td></tr>
#</table>
#END
#;

#if ($tripwiresettings{'ACTION'} eq 'croncaption')
#{
#print <<END
#<br />
#<table width='95%' cellspacing='0'>
#<tr><td align='center' colspan='2'><b>$Lang::tr{'caption'}</b></td></tr>
#<tr><td align='right' width='33%'><img src='/images/appointment-new.png' /></td><td align='left'>$Lang::tr{'add cron'}</td></tr>
#<tr><td align='right' width='33%'><img src='/images/user-trash.png' /></td><td align='left'>$Lang::tr{'delete cron'}</td></tr>
#</table>
#END
#;
#}
#
#&Header::closebox();

&Header::closebigbox();
&Header::closepage();
