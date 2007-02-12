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
my %checked = ();
my %netsettings = ();
my $message = "";
my $errormessage = "";
my %selected= () ;
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

my %servicenames =
(
	'UPnP Daemon' => 'upnpd',
);

&Header::showhttpheaders();

$upnpsettings{'ENABLED'} = 'off';
$upnpsettings{'GREEN'} = 'on';
$upnpsettings{'BLUE'} = 'off';
### Values that have to be initialized
$upnpsettings{'ACTION'} = '';

&General::readhash("${General::swroot}/upnp/settings", \%upnpsettings);
&Header::getcgihash(\%upnpsettings);

&Header::openpage('UPnP', 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
############################################################################################################################

if ($upnpsettings{'ACTION'} eq $Lang::tr{'save'})
{
	&General::writehash("${General::swroot}/upnp/settings", \%upnpsettings);
} 
elsif ($upnpsettings{'ACTION'} eq 'Start')
{
	$upnpsettings{'ENABLED'} = 'on';
	&General::writehash("${General::swroot}/upnp/settings", \%upnpsettings);
	system('/usr/local/bin/upnpctrl start');
} 
elsif ($upnpsettings{'ACTION'} eq 'Stop')
{
	$upnpsettings{'ENABLED'} = 'off';
	&General::writehash("${General::swroot}/upnp/settings", \%upnpsettings);
	system('/usr/local/bin/upnpctrl stop');
} 
elsif ($upnpsettings{'ACTION'} eq $Lang::tr{'restart'})
{
	&General::writehash("${General::swroot}/upnp/settings", \%upnpsettings);
	system('/usr/local/bin/upnpctrl restart');
}

&General::readhash("${General::swroot}/upnp/settings", \%upnpsettings);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
}

$checked{'GREEN'}{'on'} = '';
$checked{'GREEN'}{'off'} = '';
$checked{'GREEN'}{"$upnpsettings{'GREEN'}"} = 'checked';
$checked{'BLUE'}{'on'} = '';
$checked{'BLUE'}{'off'} = '';
$checked{'BLUE'}{"$upnpsettings{'BLUE'}"} = 'checked';

############################################################################################################################
############################################################################################################################

&Header::openbox('100%', 'center', 'UPnP');
print <<END
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table width='400' cellspacing='0'>
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
		print "<td align='left'>$key\n";
		my $shortname = $servicenames{$key};
		my $status = &isrunning($shortname);
		print "$status\n";
		$lines++;
	}
	print <<END
		<tr><td><b>Alle Dienste:</b></td><td colspan='2'>
		<input type='submit' name='ACTION' value='Start' /> 
		<input type='submit' name='ACTION' value='Stop' /> 
		<input type='submit' name='ACTION' value='$Lang::tr{'restart'}' />
	</table>
	</form>
	<hr />
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table width='500'>
	<tr><td colspan='2' align='left'><b>$Lang::tr{'options'}</b>
        <tr><td align='left'>$Lang::tr{'interfaces'}
	     <td align='left'>&nbsp;<td><input type='checkbox' name='GREEN' $checked{'GREEN'}{'on'} /> <font size='2' color='$Header::colourgreen'><b>$Lang::tr{'green'} - $netsettings{'GREEN_DEV'}</b></font>
END
;
         if (&Header::blue_used()){
         print <<END
         <tr><td align='left'>&nbsp;<td><input type='checkbox' name='BLUE' $checked{'BLUE'}{'on'} /> <font size='2' color='$Header::colourblue'><b>$Lang::tr{'wireless'} - $netsettings{'BLUE_DEV'}</b></font>
END
;
                                    }
        print <<END
	<tr><td colspan='2' align='right'><input type='submit' name='ACTION' value=$Lang::tr{'save'} />
	</table>
	</form>
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

