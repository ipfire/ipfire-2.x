#!/usr/bin/perl
#
# IPFire CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The IPFire Team

use strict;
# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %tripwiresettings = ();
my %checked = ();
my %netsettings = ();
my $message = "";
my $errormessage = "";
my @Logs = qx(ls /var/ipfire/tripwire/report/);
my $Log =$Lang::tr{'no log selected'};

############################################################################################################################
################################################# Tripwire Default Variablen ################################################

$tripwiresettings{'ROOT'} = '/usr/sbin';
$tripwiresettings{'POLFILE'} = '/var/ipfire/tripwire/tw.pol';
$tripwiresettings{'DBFILE'} = '/var/ipfire/tripwire/$(HOSTNAME).twd';
$tripwiresettings{'REPORTFILE'} = '/var/ipfire/tripwire/report/$(HOSTNAME)-$(DATE).twr';
$tripwiresettings{'SITEKEYFILE'} = '/var/ipfire/tripwire/site.key';
$tripwiresettings{'LOCALKEYFILE'} = '/var/ipfire/tripwire/$(HOSTNAME)-local.key';
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
$tripwiresettings{'SITEKEY'} = 'IPFire';
$tripwiresettings{'LOCALKEY'} = 'IPFire';
$tripwiresettings{'ACTION'} = '';

############################################################################################################################
######################################################### Tripwire HTML Part ###############################################

&Header::showhttpheaders();
&Header::getcgihash(\%tripwiresettings);
&Header::openpage('Tripwire', 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
############################################### Tripwire Config Datei erstellen ############################################

if ($tripwiresettings{'ACTION'} eq $Lang::tr{'save'})
{
system("/usr/local/bin/tripwirectrl readconfig");
open (FILE, ">${General::swroot}/tripwire/tw.cfg") or die "Can't save tripwire config: $!";
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
system("/usr/local/bin/tripwirectrl lockconfig");
}

############################################################################################################################
################################################## Sicherheitsabfrage für CGI ##############################################

if ($tripwiresettings{'ACTION'} eq 'globalreset')
	{
	print <<END
	<br />
	<table width='95%' cellspacing='0'>
	<tr><td bgcolor='${Header::table1colour}' colspan='2' align='center'><b>$Lang::tr{'resetglobals'}</b>
	<tr><td colspan='2' align='center'><font color=red>$Lang::tr{'defaultwarning'}<br /><br /></font></td></tr>
	<tr><td align='right' width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					 $Lang::tr{'yes'} <input type='image' alt='$Lang::tr{'yes'}' src='/images/edit-redo.png' />
					<input type='hidden' name='ACTION' value='globalresetyes' /></form></td>
			<td align='left'  width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='image' alt='$Lang::tr{'no'}' src='/images/dialog-error.png' /> $Lang::tr{'no'} 
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
	<tr><td bgcolor='${Header::table1colour}' colspan='2' align='center'><b>$Lang::tr{'generatepolicy'}</b>
	<tr><td colspan='2' align='center'><font color=red>$Lang::tr{'tripwirewarningpolicy'}<br /><br /></font></td></tr>
	<tr><td align='left' width='40%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>$Lang::tr{'sitekey'}</td><td align='left'><input type='password' name='SITEKEY' value='$tripwiresettings{'SITEKEY'}' size="30" /></td></tr>
	<tr><td align='right' width='50%'>
					 $Lang::tr{'yes'} <input type='image' alt='$Lang::tr{'yes'}' src='/images/edit-redo.png' />
					<input type='hidden' name='ACTION' value='generatepolicy' /></form></td>
			<td align='left'  width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='image' alt='$Lang::tr{'no'}' src='/images/dialog-error.png' /> $Lang::tr{'no'} 
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
	<tr><td bgcolor='${Header::table1colour}' colspan='2' align='center'><b>$Lang::tr{'resetpolicy'}</b>
	<tr><td colspan='2' align='center'><font color=red>$Lang::tr{'tripwirewarningpolicy'}<br /><br /></font></td></tr>
	<tr><td align='left' width='40%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>$Lang::tr{'sitekey'}</td><td align='left'><input type='password' name='SITEKEY' value='$tripwiresettings{'SITEKEY'}' size="30" /></td></tr>
	<tr><td align='right' width='50%'>
					 $Lang::tr{'yes'} <input type='image' alt='$Lang::tr{'yes'}' src='/images/edit-redo.png' />
					<input type='hidden' name='ACTION' value='resetpolicyyes' /></form></td>
			<td align='left'  width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='image' alt='$Lang::tr{'no'}' src='/images/dialog-error.png' /> $Lang::tr{'no'} 
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
	<tr><td bgcolor='${Header::table1colour}' colspan='2' align='center'><b>$Lang::tr{'updatedatabase'}</b>
	<tr><td colspan='2' align='center'><font color=red>$Lang::tr{'tripwirewarningdatabase'}<br /><br /></font></td></tr>
	<tr><td align='left' width='40%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>$Lang::tr{'localkey'}</td><td align='left'><input type='password' name='LOCALKEY' value='$tripwiresettings{'LOCALKEY'}' size="30" /></td></tr>
	<tr><td align='right' width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					 $Lang::tr{'yes'} <input type='image' alt='$Lang::tr{'yes'}' src='/images/edit-redo.png' />
					<input type='hidden' name='ACTION' value='updatedatabaseyes' /></form></td>
			<td align='left'  width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='image' alt='$Lang::tr{'no'}' src='/images/dialog-error.png' /> $Lang::tr{'no'} 
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
	<tr><td bgcolor='${Header::table1colour}' colspan='2' align='center'><b>$Lang::tr{'keyreset'}</b>
	<tr><td colspan='2' align='center'><font color=red>$Lang::tr{'tripwirewarningkeys'}<br /><br /></font></td></tr>
	<tr><td align='right' width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					 $Lang::tr{'yes'} <input type='image' alt='$Lang::tr{'yes'}' src='/images/edit-redo.png' />
					<input type='hidden' name='ACTION' value='keyresetyes' /></form></td>
			<td align='left'  width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='image' alt='$Lang::tr{'no'}' src='/images/dialog-error.png' /> $Lang::tr{'no'} 
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
	<tr><td bgcolor='${Header::table1colour}' colspan='2' align='center'><b>$Lang::tr{'generatekeys'}</b>
	<tr><td colspan='2' align='center'><font color=red>$Lang::tr{'tripwirewarningkeys'}<br /><br /></font></td></tr>
	<tr><td align='right' width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					 $Lang::tr{'yes'} <input type='image' alt='$Lang::tr{'yes'}' src='/images/edit-redo.png' />
					<input type='hidden' name='ACTION' value='generatekeysyes' /></form></td>
			<td align='left'  width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='image' alt='$Lang::tr{'no'}' src='/images/dialog-error.png' /> $Lang::tr{'no'} 
					<input type='hidden' name='ACTION' value='cancel' /></form></td>
	</tr>
	</table>
END
;
}

############################################################################################################################
######################################################## Tripwire Funktionen ###############################################

if ($tripwiresettings{'ACTION'} eq 'globalresetyes'){system("/usr/local/bin/tripwirectrl globalreset");}
if ($tripwiresettings{'ACTION'} eq 'generatekeysyes'){system("/usr/local/bin/tripwirectrl keys $tripwiresettings{'SITEKEY'} $tripwiresettings{'LOCALKEY'}");$tripwiresettings{'SITEKEY'} = 'IPFire';$tripwiresettings{'LOCALKEY'} = 'IPFire';}
if ($tripwiresettings{'ACTION'} eq 'keyresetyes'){system("/usr/local/bin/tripwirectrl keys IPFire IPFire");$tripwiresettings{'SITEKEY'} = 'IPFire';$tripwiresettings{'LOCALKEY'} = 'IPFire';}
if ($tripwiresettings{'ACTION'} eq 'resetpolicyyes'){system("/usr/local/bin/tripwirectrl resetpolicy tripwiresettings{'SITEKEY'}");$tripwiresettings{'SITEKEY'} = 'IPFire';}
if ($tripwiresettings{'ACTION'} eq 'generatepolicyyes'){system("/usr/local/bin/tripwirectrl generatepolicy $tripwiresettings{'SITEKEY'}");$tripwiresettings{'SITEKEY'} = 'IPFire';}
if ($tripwiresettings{'ACTION'} eq 'updatedatabaseyes'){system("/usr/local/bin/tripwirectrl updatedatabase $tripwiresettings{'LOCALKEY'}");$tripwiresettings{'LOCALKEY'} = 'IPFire';}
if ($tripwiresettings{'ACTION'} eq 'generatereport'){system("/usr/local/bin/tripwirectrl generatereport");}

############################################################################################################################
##################################################### Tripwire globale Optionen ############################################

&Header::openbox('100%', 'center', 'Tripwire');
print <<END
<hr />
<br />

<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='95%' cellspacing='0'>
<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'basic options'}</b></td></tr>
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
												<input type='image' alt='$Lang::tr{'save'}' src='/images/media-floppy.png' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
										<input type='hidden' name='ACTION' value='globalreset' />
										<input type='image' alt='$Lang::tr{'reset'}' src='/images/reload.gif' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
										<input type='hidden' name='ACTION' value='globalcaption' />
										<input type='image' alt='$Lang::tr{'caption'}' src='/images/help-browser.png' /></form></td></tr>
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
<tr><td align='right' width='33%'><img src='/images/media-floppy.png' /></td><td align='left'>$Lang::tr{'save settings'}</td></tr>
<tr><td align='right' width='33%'><img src='/images/reload.gif' /></td><td align='left'>$Lang::tr{'restore settings'}</td></tr>
</table>
END
;

}

&Header::closebox();

############################################################################################################################
################################################### Tripwire Init Policy and keygen ########################################

&Header::openbox('100%', 'center', $Lang::tr{'generate tripwire keys and init'});
print <<END
<hr />
<br />

<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='95%' cellspacing='0'>
<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'keys'}</b></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'sitekey'}</td><td align='left'><input type='password' name='SITEKEY' value='$tripwiresettings{'SITEKEY'}' size="30" /></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'localkey'}</td><td align='left'><input type='password' name='LOCALKEY' value='$tripwiresettings{'LOCALKEY'}' size="30" /></td></tr>
</table>
<br />
<table width='10%' cellspacing='0'>
<tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value='generatekeys'/>
												<input type='image' alt='$Lang::tr{'generatekeys'}' src='/images/system-lock-screen.png' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
										<input type='hidden' name='ACTION' value='keyreset' />
										<input type='image' alt='$Lang::tr{'reset'}' src='/images/reload.gif' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
										<input type='hidden' name='ACTION' value='keycaption' />
										<input type='image' alt='$Lang::tr{'caption'}' src='/images/help-browser.png' /></form></td></tr>
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
<tr><td align='right' width='33%'><img src='/images/system-lock-screen.png' /></td><td align='left'>$Lang::tr{'generatekeys'}</td></tr>
<tr><td align='right' width='33%'><img src='/images/reload.gif' /></td><td align='left'>$Lang::tr{'keyreset'}</td></tr>
</table>
END
;

}
&Header::closebox();

############################################################################################################################
################################################# Tripwire general functions ###############################################

&Header::openbox('100%', 'center', $Lang::tr{'tripwire functions'});
print <<END
<hr />
<br />

<table width='95%' cellspacing='0'>
<tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value='generatepolicypw'/>
												<input type='image' alt='$Lang::tr{'generatepolicy'}' src='/images/document-new.png' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
										<input type='hidden' name='ACTION' value='policyresetpw' />
										<input type='image' alt='$Lang::tr{'resetpolicy'}' src='/images/reload.gif' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
										<input type='hidden' name='ACTION' value='generatereport' />
										<input type='image' alt='$Lang::tr{'generatereport'}' src='/images/document-properties.png' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
										<input type='hidden' name='ACTION' value='updatedatabasepw' />
										<input type='image' alt='$Lang::tr{'updatedatabase'}' src='/images/network-server.png' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
										<input type='hidden' name='ACTION' value='policycaption' />
										<input type='image' alt='$Lang::tr{'caption'}' src='/images/help-browser.png' /></form></td></tr>
</table>
END
;
if ($tripwiresettings{'ACTION'} eq 'policycaption')
{
print <<END
<br />
<table width='95%' cellspacing='0'>
<tr><td align='center' colspan='2'><b>$Lang::tr{'caption'}</b></td></tr>
<tr><td align='right' width='33%'><img src='/images/document-new.png' /></td><td align='left'>$Lang::tr{'generatepolicy'}</td></tr>
<tr><td align='right' width='33%'><img src='/images/reload.gif' /></td><td align='left'>$Lang::tr{'resetpolicy'}</td></tr>
<tr><td align='right' width='33%'><img src='/images/document-properties.png' /></td><td align='left'>$Lang::tr{'generatereport'}</td></tr>
<tr><td align='right' width='33%'><img src='/images/network-server.png' /></td><td align='left'>$Lang::tr{'updatedatabase'}</td></tr>
</table>
END
;

}
&Header::closebox();

############################################################################################################################
####################################################### Tripwire Init Policy ###############################################

&Header::openbox('100%', 'center', $Lang::tr{'tripwire reports'});
print <<END
<hr />
<br />
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='95%' cellspacing='0'>
<tr><td bgcolor='${Header::table1colour}' colspan='3' align='left'><b>$Lang::tr{'log view'}</b></td></tr>
<tr><td colspan='3'  align='left'><br /></td></tr>
<tr><td  align='left'><select name='LOG' style="width: 500px">
END
;
foreach my $log (@Logs) {chomp $log;print"<option value='$log'>$log</option>";}
print <<END

</select></td><td  align='left'><input type='hidden' name='ACTION' value='showlog' /><input type='image' alt='view Log' src='/images/format-justify-fill.png' /></td></tr>
</table>
</form>
END
;
if ($tripwiresettings{'ACTION'} eq 'showlog')
{
$Log = qx(/usr/local/bin/tripwirectrl tripwirelog $tripwiresettings{'LOG'});
#$Log=~s/\n/<br \/>/g;
#$Log=~s/\t/....             /g;
print <<END
<table width='95%' cellspacing='0'>
<tr><td><br /></td></tr>
<tr><td><pre>LOG - $Log </pre></td></tr>
<tr><td><br /></td></tr>
<tr><td align=center>$tripwiresettings{'LOG'}</td></tr>
</table>
END
;

}

&Header::closebox();

&Header::closebigbox();
&Header::closepage();