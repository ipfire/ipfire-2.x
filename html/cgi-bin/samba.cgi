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

my %sambasettings = ();
my %checked = ();
my %netsettings = ();
my $message = "";
my $errormessage = "";
my $shareentry = "";
my @shares = ();
my @shareline = ();
my @proto = ();
my %selected= () ;
my $sharefile = "/var/ipfire/samba/shares";
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

my %servicenames =
(
	'SMB Daemon' => 'smbd',
	'NetBIOS Nameserver' => 'nmbd',
	'Winbind Daemon' => 'winbindd'
);

&Header::showhttpheaders();

$sambasettings{'ENABLED'} = 'off';
$sambasettings{'EDIT'} = 'no';
$sambasettings{'VALID'} = 'yes';
$sambasettings{'WORKGRP'} = 'homeip.net';
$sambasettings{'NETBIOSNAME'} = 'IPFIRE';
$sambasettings{'SRVSTRING'} = 'Samba Server %v running on IPFire 2.0';
$sambasettings{'INTERFACES'} = '';
$sambasettings{'SECURITY'} = 'share';
$sambasettings{'OSLEVEL'} = '20';
$sambasettings{'PDC'} = 'off';
$sambasettings{'WINSSERV'} = '';
$sambasettings{'WINS'} = 'off';
### Values that have to be initialized
$sambasettings{'ACTION'} = '';

&General::readhash("${General::swroot}/samba/settings", \%sambasettings);
&Header::getcgihash(\%sambasettings);

&Header::openpage('Samba', 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
############################################################################################################################

if ($sambasettings{'ACTION'} eq $Lang::tr{'save'})
{
	&General::writehash("${General::swroot}/samba/settings", \%sambasettings);
}

&General::readhash("${General::swroot}/samba/settings", \%sambasettings);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
}

$checked{'PDC'}{'on'} = '';
$checked{'PDC'}{'off'} = '';
$checked{'PDC'}{"$sambasettings{'PDC'}"} = 'checked';
$checked{'WINS'}{'on'} = '';
$checked{'WINS'}{'off'} = '';
$checked{'WINS'}{"$sambasettings{'WINS'}"} = 'checked';

############################################################################################################################
############################################################################################################################

&Header::openbox('100%', 'center', 'Samba');
print <<END
	<table width='400px' cellspacing='0'>
END
;
	if ( $message ne "" ) {
		print "<tr><td colspan='3' align='center'><font color='red'>$message</font>";
	}

	my $lines = 0;
	my $key = '';
	foreach $key (sort keys %servicenames)
	{
		if ($lines % 2) {
			print "<tr bgcolor='${Header::table1colour}'>\n"; }
		else {
			print "<tr bgcolor='${Header::table2colour}'>\n"; }
		print "<td align='left'>$key</td>\n";
		my $shortname = $servicenames{$key};
		my $status = &isrunning($shortname);
		print "$status\n";
		print <<END
			<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
				<input type='hidden' name='ACTION' value='restart $shortname'>
				<input type='image' src='/images/reload.gif'>
			</form></td>
END
;
		print "</tr>\n";
		$lines++;
	}
	print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<tr><td><b>Alle Dienste:</b></td><td colspan='2'>
		<input type='submit' name='ACTION' value='Start' /> 
		<input type='submit' name='ACTION' value='Stop' /> 
		<input type='submit' name='ACTION' value='$Lang::tr{'restart'}' />
		</td></tr></form>
	</table>
	<hr>
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table width='500px'>
	<tr><td colspan='2' align='left'><b>Basisoptionen</b>
	<tr><td align='left'>Workgroup:<td><input type='text' name='WORKGRP' value='$sambasettings{'WORKGRP'}'>
	<tr><td align='left'>NetBIOS-Name:<td><input type='text' name='NETBIOSNAME' value='$sambasettings{'NETBIOSNAME'}'>
	<tr><td align='left'>Server-String:<td><input type='text' name='SRVSTRING' value='$sambasettings{'SRVSTRING'}'>
	<tr><td align='left'>Interfaces:<td><select name='INTERFACES'>
							<option value='$netsettings{'GREEN_DEV'}'>GREEN</option>
END
;
						if (&Header::blue_used()){
							print <<END
							<option value='$netsettings{'BLUE_DEV'}'>BLUE</option>
							<option value='$netsettings{'GREEN_DEV'},$netsettings{'BLUE_DEV'}'>GREEN & BLUE</option>
END
;
						}
	print <<END
</select>

	<tr><td colspan='2' align='left'><b>Sicherheitsoptionen</b>
	<tr><td align='left'>Security:<td><select name='SECURITY'>
							<option value='share'>SHARE</option>
							<option value='user'>USER</option>
							<option value='server'>SERVER</option>
							<option value='domain'>DOMAIN</option>
						</select>

	<tr><td colspan='2' align='left'><b>Browsingoptionen</b>
	<tr><td align='left'>OS Level:<td><input type='text' name='OSLEVEL' value='$sambasettings{'OSLEVEL'}'>
	<tr><td align='left'>Primary Domain Controller:<td>on 	<input type='radio' name='PDC' value='on' $checked{'PDC'}{'on'}>/
									<input type='radio' name='PDC' value='off' $checked{'PDC'}{'off'}> off

	<tr><td colspan='2' align='left'><b>WINS-Optionen</b>
	<tr><td align='left'>WINS-Server:<td><input type='text' name='WINSSRV' value='$sambasettings{'WINSSRV'}'>
	<tr><td align='left'>WINS-Support:<td>on 	<input type='radio' name='WINS' value='on' $checked{'WINS'}{'on'}>/
							<input type='radio' name='WINS' value='off' $checked{'WINS'}{'off'}> off

	<tr><td colspan='2' align='right'><input type='submit' name='ACTION' value=$Lang::tr{'save'}>
	</table>
	</form>
END
;
&Header::closebox();

&Header::openbox('100%', 'center', 'Shares');

print <<END
	<table width='500'>
	<tr><th width='40%'>Name der Freigabe<th width='40%'>Pfad<th width='20%'>Optionen
END
;
	open( FILE, "< $sharefile" ) or die "Unable to read $sharefile";
	@shares = <FILE>;
	close FILE;
  	foreach $shareentry (sort @shares)
  	{
  		@shareline = split( /\;/, $shareentry );
		print <<END
		<tr><td align='center' bgcolor='#EAEAEA'><b>$shareline[0]</b>
		    <td align='center' bgcolor='#EAEAEA'>$shareline[2]
		    <td align='right'  bgcolor='#EAEAEA'>
			<table border='0'><tr>
END
;
		if ($shareline[1] eq 'enabled') {
			print <<END
				<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='hidden' name='NAME' value='shareline[0]'>
					<input type='hidden' name='ACTION' value='disable'>
					<input type='image' alt='Ausschalten' src='/images/on.gif'>
				</form>
END
;
		} elsif ($shareline[1] eq 'disabled') {
			print <<END
				<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='hidden' name='NAME' value='shareline[0]'>
					<input type='hidden' name='ACTION' value='enable'>
					<input type='image' alt='Einschalten' src='/images/off.gif'>
				</form>
END
;
		}
		print <<END
			<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
				<input type='hidden' name='NAME' value='shareline[0]'>
				<input type='hidden' name='ACTION' value='Bearbeiten'>
				<input type='image' alt='Bearbeiten' src='/images/edit.gif'>
			</form>
			<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
				<input type='hidden' name='NAME' value='shareline[0]'>
				<input type='hidden' name='ACTION' value='Loeschen'>
				<input type='image' alt='Loeschen' src='/images/delete.gif'>
			</form>
			</table>
END
;
  	}
	print <<END
	<tr><td colspan='8' align='right' valign='middle'><b>Legende:</b>&nbsp;&nbsp;<img src='/images/edit.gif'>&nbsp;Freigabe bearbeiten | <img src='/images/delete.gif'>&nbsp;Freigabe loeschen &nbsp;
	</table>
END
;

&Header::closebox();

&Header::closebigbox();
&Header::closepage();

############################################################################################################################
############################################################################################################################

sub isrunning
{
	my $cmd = $_[0];
	my $status = "<td bgcolor='${Header::colourred}'><font color='white'><b>$Lang::tr{'stopped'}</b></font></td>";
	my $pid = '';
	my $testcmd = '';
	my $exename;

	$cmd =~ /(^[a-z]+)/;
	$exename = $1;

	if (open(FILE, "/var/run/${cmd}.pid"))
	{
 		$pid = <FILE>; chomp $pid;
		close FILE;
		if (open(FILE, "/proc/${pid}/status"))
		{
			while (<FILE>)
			{
				if (/^Name:\W+(.*)/) {
					$testcmd = $1; }
			}
			close FILE;
			if ($testcmd =~ /$exename/)
			{
				$status = "<td bgcolor='${Header::colourgreen}'><font color='white'><b>$Lang::tr{'running'}</b></font></td>";
			}
		}
	}

	return $status;
}

