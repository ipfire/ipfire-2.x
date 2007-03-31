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

my %upnpsettings = ();
my %netsettings = ();
my $message = "";
my $errormessage = "";
my %selected= () ;

my %servicenames =('UPnP Daemon' => 'upnpd',);

&Header::showhttpheaders();
############################################################################################################################
############################################### Setzen von Standartwerten ##################################################

$upnpsettings{'DEBUGMODE'} = '3';
$upnpsettings{'FORWARDRULES'} = 'yes';
$upnpsettings{'DOWNSTREAM'} = '900000';
$upnpsettings{'UPSTREAM'} = '16000000';
$upnpsettings{'DESCRIPTION'} = 'gatedesc.xml';
$upnpsettings{'XML'} = '/etc/linuxigd';
$upnpsettings{'ENABLED'} = 'off';
$upnpsettings{'friendlyName'} = 'IpFire Upnp Device';
### Values that have to be initialized
$upnpsettings{'ACTION'} = '';

&General::readhash("${General::swroot}/upnp/settings", \%upnpsettings);
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
&Header::getcgihash(\%upnpsettings);

&Header::openpage('UPnP', 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
################################################### Speichern der Config ###################################################

if ($upnpsettings{'ACTION'} eq $Lang::tr{'save'})
	{
	$upnpsettings{'DOWNSTREAM'} = $upnpsettings{'DOWNSTREAM'} * 8;
	$upnpsettings{'UPSTREAM'} = $upnpsettings{'UPSTREAM'} * 8;
	&General::writehash("${General::swroot}/upnp/settings", \%upnpsettings);

	open (FILE, ">${General::swroot}/upnp/upnpd.conf") or die "Can't save the upnp config: $!";
	flock (FILE, 2);

	print FILE <<END

# UPnP Config by Ipfire Project

debug_mode = $upnpsettings{'DEBUGMODE'}
insert_forward_rules = $upnpsettings{'FORWARDRULES'}
forward_chain_name = FORWARD
prerouting_chain_name = PORTFW
upstream_bitrate = $upnpsettings{'DOWNSTREAM'}
downstream_bitrate = $upnpsettings{'UPSTREAM'}
description_document_name = $upnpsettings{'DESCRIPTION'}
xml_document_path = $upnpsettings{'XML'}

END
;
	close FILE;
	system("/usr/local/bin/upnpctrl upnpxml $upnpsettings{'XML'} $upnpsettings{'DESCRIPTION'} $upnpsettings{'manufacturer'}");
	}
elsif ($upnpsettings{'ACTION'} eq 'Start')
	{
	$upnpsettings{'ENABLED'} = 'on';
	&General::writehash("${General::swroot}/upnp/settings", \%upnpsettings);
	system("/usr/local/bin/upnpctrl upnpdstart $netsettings{'RED_DEV'} $netsettings{'GREEN_DEV'}");
	} 
elsif ($upnpsettings{'ACTION'} eq 'Stop')
	{
	$upnpsettings{'ENABLED'} = 'off';
	&General::writehash("${General::swroot}/upnp/settings", \%upnpsettings);
	system("/usr/local/bin/upnpctrl stop");
	} 
elsif ($upnpsettings{'ACTION'} eq $Lang::tr{'restart'})
	{
	&General::writehash("${General::swroot}/upnp/settings", \%upnpsettings);
	system("/usr/local/bin/upnpctrl stop");
	system("/usr/local/bin/upnpctrl start $netsettings{'RED_DEV'} $netsettings{'GREEN_DEV'}");
	}

&General::readhash("${General::swroot}/upnp/settings", \%upnpsettings);
$upnpsettings{'DOWNSTREAM'} = $upnpsettings{'DOWNSTREAM'} / 8;
$upnpsettings{'UPSTREAM'} = $upnpsettings{'UPSTREAM'} / 8;

if ($errormessage)
	{
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
	}

############################################################################################################################
############################################################################################################################

&Header::openbox('100%', 'center', 'UPnP');
print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='95%' cellspacing='0'>
END
;
if ( $message ne "" ) {print "<tr><td colspan='3' align='center'><font color='red'>$message</font>";}

my $lines = 0;
my $key = '';
foreach $key (sort keys %servicenames)
{
	if ($lines % 2)
		{print "<tr bgcolor='${Header::table1colour}'>\n";}
	else
		{print "<tr bgcolor='${Header::table2colour}'>\n"; }

	print "<td align='left'>$key\n";
	my $shortname = $servicenames{$key};
	my $status = &isrunning($shortname);
	print "$status\n";
	$lines++;
}

print <<END
<tr><td align='left'>Alle Dienste:</td><td align='center' colspan='2'>
<input type='submit' name='ACTION' value='Start' /> 
<input type='submit' name='ACTION' value='Stop' /> 
<input type='submit' name='ACTION' value='$Lang::tr{'restart'}' />
</table>
</form>
<br />
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='95%' cellspacing='0'>
<tr><td colspan='2' align='left' bgcolor='${Header::table1colour}'><b>$Lang::tr{'options'}</b></td></tr>
<tr><td colspan='2' align='left'><br></br></td></tr>
<tr><td align='left'>Debug Mode:</td><td><input type='text' name='DEBUGMODE' value='$upnpsettings{'DEBUGMODE'}' size="30" /></td></tr>
<tr><td align='left'>Forward Rules:</td><td><input type='text' name='FORWARDRULES' value='$upnpsettings{'FORWARDRULES'}' size="30" /></td></tr>
<tr><td align='left' colspan='2'><br /></td></tr>
<tr><td align='left'>Down Stream in KB:</td><td><input type='text' name='DOWNSTREAM' value='$upnpsettings{'DOWNSTREAM'}' size="30" /></td></tr>
<tr><td align='left'>Up Strean in KB:</td><td><input type='text' name='UPSTREAM' value='$upnpsettings{'UPSTREAM'}' size="30" /></td></tr>
<tr><td align='left' colspan='2'><br /></td></tr>
<tr><td align='left'>XML Document:</td><td><input type='text' name='XML' value='$upnpsettings{'XML'}' size="30" /></td></tr>
<tr><td align='left'>Description Document:</td><td><input type='text' name='DESCRIPTION' value='$upnpsettings{'DESCRIPTION'}' size="30" /></td></tr>
<tr><td align='left'>Upnp Device Name:</td><td><input type='text' name='friendlyName' value='$upnpsettings{'friendlyName'}' size="30" /></td></tr>
<tr><td colspan='2' align='left'><br></br></td></tr>
<tr><td colspan='2' align='center'><input type='hidden' name='ACTION' value=$Lang::tr{'save'} />
																		<input type='image' alt=$Lang::tr{'save'} src='/images/floppy.gif' /></td></tr>
</table></form>
<br />
<hr />
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
	my $status = "<td bgcolor='${Header::colourred}' align='center'><font color='white'><b>$Lang::tr{'stopped'}</b></font></td>";
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
				{if (/^Name:\W+(.*)/) {$testcmd = $1; }}
			close FILE;
			if ($testcmd =~ /$exename/)
				{$status = "<td bgcolor='${Header::colourgreen}'><font color='white'><b>$Lang::tr{'running'}</b></font></td>";}
			}
		}

		return $status;
	}