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

my %upnpsettings = ();
my %netsettings = ();
my $message = "";
my $errormessage = "";
my %selected= () ;

my %servicenames =('UPnP Daemon' => 'upnpd',);

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

&Header::showhttpheaders();
############################################################################################################################
############################################### Setzen von Standartwerten ##################################################

$upnpsettings{'DEBUGMODE'} = '3';
$upnpsettings{'FORWARDRULES'} = 'yes';
$upnpsettings{'DOWNSTREAM'} = '1048576';
$upnpsettings{'UPSTREAM'} = '131072';
$upnpsettings{'DESCRIPTION'} = 'gatedesc.xml';
$upnpsettings{'XML'} = '/etc/linuxigd';
$upnpsettings{'ENABLED'} = 'off';
$upnpsettings{'friendlyName'} = 'IPFire Gateway';
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
	$upnpsettings{'DOWNSTREAM'} = $upnpsettings{'DOWNSTREAM'} * 1024;
	$upnpsettings{'UPSTREAM'} = $upnpsettings{'UPSTREAM'} * 1024;
	&General::writehash("${General::swroot}/upnp/settings", \%upnpsettings);

	open (FILE, ">${General::swroot}/upnp/upnpd.conf") or die "Can't save the upnp config: $!";
	flock (FILE, 2);

	print FILE <<END

# UPnP Config by Ipfire Project

debug_mode = $upnpsettings{'DEBUGMODE'}
insert_forward_rules = $upnpsettings{'FORWARDRULES'}
forward_chain_name = FORWARD
prerouting_chain_name = UPNPFW
upstream_bitrate = $upnpsettings{'DOWNSTREAM'}
downstream_bitrate = $upnpsettings{'UPSTREAM'}
description_document_name = $upnpsettings{'DESCRIPTION'}
xml_document_path = $upnpsettings{'XML'}

END
;
	close FILE;
	system("/usr/local/bin/upnpctrl","upnpxml","$upnpsettings{'friendlyName'}","$upnpsettings{'XML'}","$upnpsettings{'DESCRIPTION'}");
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
$upnpsettings{'DOWNSTREAM'} = $upnpsettings{'DOWNSTREAM'} / 1024;
$upnpsettings{'UPSTREAM'} = $upnpsettings{'UPSTREAM'} / 1024;

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
if ( $message ne "" ) {print "<tr><td colspan='3' style='text-align:center; color:red;'>$message</td></tr>";}

my $lines = 0;
my $key = '';
foreach $key (sort keys %servicenames)
{
  print "<tr><td align='left'>$key\n";
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
<tr><td colspan='2' align='left' bgcolor='$color{'color20'}'><b>$Lang::tr{'options'}</b></td></tr>
<tr><td align='left' colspan='2'><br /></td></tr>
<tr><td align='left'>UPnP Device Name:</td><td><input type='text' name='friendlyName' value='$upnpsettings{'friendlyName'}' size="30" /></td></tr>
<tr><td align='left' colspan='2'><br /></td></tr>
<tr><td align='left'>Downstream in KB:</td><td><input type='text' name='DOWNSTREAM' value='$upnpsettings{'DOWNSTREAM'}' size="30" /></td></tr>
<tr><td align='left'>Upstream in KB:</td><td><input type='text' name='UPSTREAM' value='$upnpsettings{'UPSTREAM'}' size="30" /></td></tr>
<tr><td align='left' colspan='2'><br /></td></tr>
<tr><td colspan='2' align='center'>	<input type='hidden' name='ACTION' value='$Lang::tr{'save'}' />
<input type='image' alt='$Lang::tr{'save'}' title='$Lang::tr{'save'}' src='/images/floppy.gif' /></td></tr>
</table></form>
END
;
&Header::closebox();

&Header::openbox('100%', 'center', 'Aktuell geoeffnete Ports');
my @output = qx(iptables -t nat -n -L PORTFW);
my ($outputline, $extip, $extport, $int);
my @output2;
print "<table>";
foreach $outputline (@output) {
	if ( $outputline =~ /^DNAT/ ) {	
		@output2 = split(/ /, $outputline);
		$extip = $output2[23];
		$extport = $output2[29];
		$extport =~ s/dpt://;
		$int = "$output2[31]";
		$int =~ s/to://;
		print "<tr><td>$extip:$extport<td align='center'><img src='/images/forward.gif' alt='=&gt;' /><td>$int";

	}
}

print "</table>";

&Header::closebox();

&Header::closebigbox();
&Header::closepage();

############################################################################################################################
############################################################################################################################

sub isrunning
{
	my $cmd = $_[0];
	my $status = "<td bgcolor='${Header::colourred}' style='text-align:center; color:white;'><b>$Lang::tr{'stopped'}</b></td>";
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
				{$status = "<td style='color:white; background-color:${Header::colourgreen};'><b>$Lang::tr{'running'}</b></td>";}
			}
		}

		return $status;
}

