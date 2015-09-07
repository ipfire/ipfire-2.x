#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2010  IPFire Team                                             #
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

my %timesettings=();
my $errormessage = '';

&Header::showhttpheaders();

$timesettings{'ACTION'} = '';
$timesettings{'VALID'} = '';

$timesettings{'ENABLENTP'} = 'off';
$timesettings{'NTP_ADDR_1'} = '';
$timesettings{'NTP_ADDR_2'} = '';
$timesettings{'UPDATE_METHOD'} = 'manually';
$timesettings{'UPDATE_VALUE'} = '0';
$timesettings{'UPDATE_PERIOD'} = '';
$timesettings{'ENABLECLNTP'} = 'off';
$timesettings{'ENABLESETONBOOT'} = 'off';

&Header::getcgihash(\%timesettings);

if ($timesettings{'ACTION'} eq $Lang::tr{'save'})
{ 
	if ($timesettings{'ENABLENTP'} eq 'on')
	{
		if ( ! ( &General::validfqdn($timesettings{'NTP_ADDR_1'}) ||
			 &General::validip  ($timesettings{'NTP_ADDR_1'})))
		{
			$errormessage = $Lang::tr{'invalid primary ntp'};
			goto ERROR;
		}
	}
	if ($timesettings{'NTP_ADDR_2'})
	{
		if ( ! ( &General::validfqdn($timesettings{'NTP_ADDR_2'}) ||
			 &General::validip  ($timesettings{'NTP_ADDR_2'})))
		{
			$errormessage = $Lang::tr{'invalid secondary ntp'};
			goto ERROR;
		}
	}
	if (!($timesettings{'NTP_ADDR_1'}) && $timesettings{'NTP_ADDR_2'})
	{
		$errormessage = $Lang::tr{'cannot specify secondary ntp without specifying primary'};
		goto ERROR;
	}

	if (!($timesettings{'UPDATE_VALUE'} =~ /^\d+$/) || $timesettings{'UPDATE_VALUE'} <= 0)
	{
		$errormessage = $Lang::tr{'invalid time period'};
		goto ERROR;
	}

	if ($timesettings{'ENABLENTP'} ne "on" && $timesettings{'ENABLECLNTP'} eq "on")
	{
		$errormessage = $Lang::tr{'ntp must be enabled to have clients'};
		goto ERROR;
	}
	if ($timesettings{'ENABLENTP'} eq "on" && !($timesettings{'NTP_ADDR_1'}) && !($timesettings{'NTP_ADDR_2'}))
	{
		$errormessage = $Lang::tr{'cannot enable ntp without specifying primary'};
		goto ERROR;
	}
ERROR:
	if ($errormessage) {
		$timesettings{'VALID'} = 'no'; }
	else {
		$timesettings{'VALID'} = 'yes'; }

		&General::writehash("${General::swroot}/time/settings", \%timesettings);
		open(FILE, ">/${General::swroot}/time/settime.conf") or die "Unable to write settime.conf file";
		flock(FILE, 2);
		print FILE "$timesettings{'NTP_ADDR_1'} $timesettings{'NTP_ADDR_2'}\n";
		close FILE;

		my $updateperiod=0;

		if  ($timesettings{'UPDATE_PERIOD'} eq 'daily') {
			$updateperiod = $timesettings{'UPDATE_VALUE'} * 1440; }
		elsif  ($timesettings{'UPDATE_PERIOD'} eq 'weekly') {
			$updateperiod = $timesettings{'UPDATE_VALUE'} * 10080; }
		elsif  ($timesettings{'UPDATE_PERIOD'} eq 'monthly') {
			$updateperiod = $timesettings{'UPDATE_VALUE'} * 40320; }
		else {
			$updateperiod = $timesettings{'UPDATE_VALUE'} * 60; }

		$updateperiod = $updateperiod - 5;

		if ($updateperiod <= 5) {
			$updateperiod = 5; }

		open(FILE, ">/${General::swroot}/time/counter.conf") or die "Unable to write counter.conf file";
		flock(FILE, 2);
		print FILE "$updateperiod\n";
		close FILE;

	if ($timesettings{'ENABLENTP'} eq 'on' && $timesettings{'VALID'} eq 'yes')
	{
		system ('/usr/bin/touch', "${General::swroot}/time/enable");
		system ('/usr/local/bin/timectrl enable >/dev/null 2>&1');
		&General::log($Lang::tr{'ntp syncro enabled'});
		unlink "/var/lock/time/counter";
		if ($timesettings{'UPDATE_METHOD'} eq 'periodically')
		{
			open(FILE, ">/var/lock/time/counter") or die "Unable to write counter file";
			flock(FILE, 2);
			print FILE "$updateperiod\n";
			close FILE;
		}
		if ($timesettings{'ENABLECLNTP'} eq 'on') # DPC added to 1.3.1
		{
			system ('/usr/bin/touch', "${General::swroot}/time/allowclients"); # DPC added to 1.3.1
			&General::log($Lang::tr{'ntpd restarted'}); # DPC added to 1.3.1
		} else {
			unlink "${General::swroot}/time/allowclients";
		}
	
	}
	else
	{
		unlink "${General::swroot}/time/enable";
		unlink "/var/lock/time/settimenow";
		unlink "${General::swroot}/time/allowclients"; # DPC added to 1.3.1
		system ('/usr/local/bin/timectrl disable >/dev/null 2>&1');
		&General::log($Lang::tr{'ntp syncro disabled'})
	}
	if (! $errormessage) {
		system ('/usr/local/bin/timectrl restart >/dev/null 2>&1'); # DPC added to 1.3.1
	}
}

# To enter an ' into a pushbutton solution is to use &#039; in it's definition
# but returned value when pressed is ' not the code. Cleanhtml recode the ' to enable comparison.
$timesettings{'ACTION'} = &Header::cleanhtml ($timesettings{'ACTION'});
if ($timesettings{'ACTION'} eq $Lang::tr{'set time now'} && $timesettings{'ENABLENTP'} eq 'on')
{
	system ('/usr/bin/touch', "/var/lock/time/settimenow");
}

&General::readhash("${General::swroot}/time/settings", \%timesettings);

if ($timesettings{'VALID'} eq '')
{
 	$timesettings{'ENABLENTP'} = 'off';
	$timesettings{'UPDATE_METHOD'} = 'manually';
	$timesettings{'UPDATE_VALUE'} = '1';
	$timesettings{'UPDATE_PERIOD'} = 'daily';
	$timesettings{'NTP_ADDR_1'} = '0.ipfire.pool.ntp.org';
	$timesettings{'NTP_ADDR_2'} = '1.ipfire.pool.ntp.org';
	$timesettings{'ENABLESETONBOOT'} = 'off';
}

unless ($errormessage) {
	$timesettings{'SETMONTH'} = `date +'%m %e %Y %H %M'|cut -c 1-2`;
	$timesettings{'SETDAY'} = `date +'%m %e %Y %H %M'|cut -c 4-5`;
	$timesettings{'SETYEAR'} = `date +'%m %e %Y %H %M'|cut -c 7-10`;
	$timesettings{'SETHOUR'} = `date +'%m %e %Y %H %M'|cut -c 12-13`;
	$timesettings{'SETMINUTES'} = `date +'%m %e %Y %H %M'|cut -c 15-16`;
	$_=$timesettings{'SETDAY'};
	$timesettings{'SETDAY'}=~ tr/ /0/;
}

my %selected=();
my %checked=();

$checked{'ENABLENTP'}{'off'} = '';
$checked{'ENABLENTP'}{'on'} = '';
$checked{'ENABLENTP'}{$timesettings{'ENABLENTP'}} = "checked='checked'";

$checked{'ENABLECLNTP'}{'off'} = '';
$checked{'ENABLECLNTP'}{'on'} = '';
$checked{'ENABLECLNTP'}{$timesettings{'ENABLECLNTP'}} = "checked='checked'";

$checked{'ENABLESETONBOOT'}{'off'} = '';
$checked{'ENABLESETONBOOT'}{'on'} = '';
$checked{'ENABLESETONBOOT'}{$timesettings{'ENABLESETONBOOT'}} = "checked='checked'";

$checked{'UPDATE_METHOD'}{'manually'} = '';
$checked{'UPDATE_METHOD'}{'periodically'} = '';
$checked{'UPDATE_METHOD'}{$timesettings{'UPDATE_METHOD'}} = "checked='checked'";

$selected{'UPDATE_PERIOD'}{'hourly'} = '';
$selected{'UPDATE_PERIOD'}{'daily'} = '';
$selected{'UPDATE_PERIOD'}{'weekly'} = '';
$selected{'UPDATE_PERIOD'}{'monthly'} = '';
$selected{'UPDATE_PERIOD'}{$timesettings{'UPDATE_PERIOD'}} = "selected='selected'";

# added to v0.0.4 to refresh screen if syncro event queued 
my $refresh = '';
if ( -e "/var/lock/time/settimenow") {
	$refresh = "<meta http-equiv='refresh' content='60;' />";
}

&Header::openpage($Lang::tr{'ntp configuration'}, 1, $refresh);

&Header::openbigbox('100%', 'left', '', $errormessage);

# DPC move error message to top so it is seen!
if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<font class='base'>$errormessage&nbsp;</font>\n";
	&Header::closebox();
	}

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

&Header::openbox('100%', 'left', $Lang::tr{'ntp common settings'});
print <<END
<table width='100%'>
<tr>
	<td><input type='checkbox' name='ENABLENTP' $checked{'ENABLENTP'}{'on'} /></td>
	<td width='100%' colspan='4' class='base'>$Lang::tr{'network time from'}</td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td width='100%' class='base' colspan='4'>
END
;

if ( -e "/var/lock/time/lastset")
{
	print "$Lang::tr{'clock last synchronized at'}\n";
	open(FILE, "</var/lock/time/lastset") or die "Unable to read lastset";
	my $output = <FILE>;
	close FILE;
	print $output;
}
else
{
	print "$Lang::tr{'clock has not been synchronized'}\n";
}

print <<END
</td></tr>
<tr>
	<td>&nbsp;</td>
	<td width='25%' class='base'>$Lang::tr{'primary ntp server'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td width='25%'><input type='text' name='NTP_ADDR_1' value='$timesettings{'NTP_ADDR_1'}' /></td>
	<td width='25%' class='base'>$Lang::tr{'secondary ntp server'}:</td>
	<td width='25%'><input type='text' name='NTP_ADDR_2' value='$timesettings{'NTP_ADDR_2'}' /></td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td class='base' colspan='4'><input type='checkbox' name='ENABLECLNTP' $checked{'ENABLECLNTP'}{'on'} /> $Lang::tr{'clenabled'}</td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td class='base' colspan='4'><input type='checkbox' name='ENABLESETONBOOT' $checked{'ENABLESETONBOOT'}{'on'} /> $Lang::tr{'Set time on boot'}</td>
</tr>
</table>
END
;
&Header::closebox();
&Header::openbox('100%',1,$Lang::tr{'ntp sync'});
print <<END
<table width='100%'>
<tr>
	<td class='base'><input type='radio' name='UPDATE_METHOD' value='periodically' $checked{'UPDATE_METHOD'}{'periodically'} /></td>
	<td width='10%'>$Lang::tr{'every'}</td>
	<td width='45%'><input type='text' name='UPDATE_VALUE' size='3' maxlength='3' value='$timesettings{'UPDATE_VALUE'}' />
	<select name='UPDATE_PERIOD'>
		<option value='hourly' $selected{'UPDATE_PERIOD'}{'hourly'}>$Lang::tr{'hours'}</option>
		<option value='daily' $selected{'UPDATE_PERIOD'}{'daily'}>$Lang::tr{'days'}</option>
		<option value='weekly' $selected{'UPDATE_PERIOD'}{'weekly'}>$Lang::tr{'weeks'}</option>
		<option value='monthly' $selected{'UPDATE_PERIOD'}{'monthly'}>$Lang::tr{'months'}</option>
	</select></td>
	<td width='50%'>&nbsp;</td>
</tr>
<tr>
	<td class='base'><input type='radio' name='UPDATE_METHOD' value='manually' $checked{'UPDATE_METHOD'}{'manually'} /></td>
	<td colspan='2'>$Lang::tr{'manually'}</td>
</tr>
<tr>
	<td colspan='4'><br><br><strong>$Lang::tr{'update time'}</strong></td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td class='base' colspan='3'>$Lang::tr{'set time now help'}</td>
</tr>
END
;

if ( -e "/var/lock/time/settimenow") {
	print "<tr>\n<td align='center'><img src='/images/clock.gif' alt='' /></td>\n";
	print "<td colspan='2'><font color='red'>$Lang::tr{'waiting to synchronize clock'}...</font></td></tr>\n";
}
print <<END
</table>
<br />
<hr />
<table width='100%'>
<tr>
	<td width='30%'><img src='/blob.gif' alt='*' /> $Lang::tr{'required field'}</td>
	<td width='65%' align='right'><input type='submit' name='ACTION' value='$Lang::tr{'set time now'}' /></td>
	<td width='5%' align='right'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
</tr>
</table>
END
;

&Header::closebox();

print "</form>\n";

&Header::closebigbox();

&Header::closepage();

