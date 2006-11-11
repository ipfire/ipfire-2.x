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

my %uptimesettings = ();
my %proxysettings = ();
my %checked = ();
my $message = "";
my $errormessage = "";
my %selected= () ;
my $uptimefile = "/var/ipfire/uptime/yasuc.conf";
&General::readhash("${General::swroot}/proxy/advanced/settings", \%proxysettings);

&Header::showhttpheaders();

$uptimesettings{'ENABLE'} = 'off';
$uptimesettings{'USER'} = '';
$uptimesettings{'PASS'} = '';
$uptimesettings{'PROXY'} = $proxysettings{'ENABLE'};
### Values that have to be initialized
$uptimesettings{'ACTION'} = '';

&General::readhash("${General::swroot}/uptime/settings", \%uptimesettings);
&Header::getcgihash(\%uptimesettings);

&Header::openpage('Uptime Client', 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
############################################################################################################################

if ($uptimesettings{'ACTION'} eq $Lang::tr{'save'})
{
	&save_configuration();
}
elsif ($uptimesettings{'ACTION'} eq $Lang::tr{'uptime enable'})
{
	&save_configuration();
	system("/bin/touch ${General::swroot}/uptime/enabled");
	system("/usr/local/bin/yasucctrl enable");
}
elsif ($uptimesettings{'ACTION'} eq $Lang::tr{'uptime disable'})
{
	unlink "${General::swroot}/uptime/enabled";
	system("/usr/local/bin/yasucctrl disable");
}
elsif ($uptimesettings{'ACTION'} eq $Lang::tr{'uptime update now'})
{
	&save_configuration();
	system("/usr/local/bin/yasucctrl");
}

&General::readhash("${General::swroot}/uptime/settings", \%uptimesettings);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
}

$checked{'PROXY'}{'on'} = '';
$checked{'PROXY'}{'off'} = '';
$checked{'PROXY'}{"$uptimesettings{'PROXY'}"} = 'checked';

############################################################################################################################
############################################################################################################################

&Header::openbox('100%', 'center', 'Uptime Client');
print <<END
	<table width='300px' cellspacing='0'>
END
;
	if ( $message ne "" ) {
		print "<tr><td colspan='3' align='center'><font color='red'>$message</font>";
	}

	my $status = "";
	my $status_color = "";
	if ( -e "${General::swroot}/uptime/enabled" ){
		$status_color = $Header::colourgreen;
		$status = $Lang::tr{'running'};
	} else {
		$status_color = $Header::colourred;
		$status = $Lang::tr{'stopped'};
	}

	print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<tr><td><b>Uptime Client:</b></td><td colspan='2'>
		<input type='submit' name='ACTION' value='$Lang::tr{'uptime enable'}' /> 
		<input type='submit' name='ACTION' value='$Lang::tr{'uptime disable'}' /> 
		<input type='submit' name='ACTION' value='$Lang::tr{'uptime update now'}' />
		</td></tr></form>
		<tr><td colspan='2' bgcolor=$status_color align='center'><font color='white'<b>$status</b></font></td></tr>
	</table>
	<hr>
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table width='500px'>
	<tr><td colspan='2' align='left'><b>Basisoptionen</b>
	<tr><td align='left'>Username:<td><input type='text' name='USER' value='$uptimesettings{'USER'}'>
	<tr><td align='left'>Password:<td><input type='password' name='PASS' value='$uptimesettings{'PASS'}'>

	<tr><td colspan='2' align='left'><b>Proxyeinstellungen</b>
	<tr><td align='left'>Use proxy:<td><input type='checkbox' name='PROXY' $checked{'PROXY'}{'on'}>
	<tr><td colspan='2' align='right'><input type='submit' name='ACTION' value=$Lang::tr{'save'}>
	</table>
	</form>
END
;
&Header::closebox();
&Header::closebigbox();
&Header::closepage();

############################################################################################################################
############################################################################################################################

sub save_configuration {
	# A small helper to create our configurationfile
	&General::writehash("${General::swroot}/uptime/settings", \%uptimesettings);
	if ($uptimesettings{'PROXY'} == "on"){ $uptimesettings{'PROXY'} = "yes";}
	if ($uptimesettings{'PROXY'} == "off"){ $uptimesettings{'PROXY'} = "no";}
	open( FILE, "> $uptimefile" ) or die "Unable to write $uptimefile";
	print FILE <<END
[global]
user    = $uptimesettings{'USER'}
password= $uptimesettings{'PASS'}
proxy   = $uptimesettings{'PROXY'}
debug   = no

[proxy]
host    = localhost
port    = $proxysettings{'PROXY_PORT'}

[debug]
path    = /var/log/yasuc.log
END
;
	close FILE;
}