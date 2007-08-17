#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# $Id: traffic.cgi,v 1.19 2007/01/09 18:59:23 dotzball Exp $
#
# traffic.cgi, v1.1.0 2003/10/18
#	supports now:
#		* IPCop v1.3.0
#		* choosing year
#
# 18 June 2004 Achim Weber
#	- added functionality to work with IPCop 1.4.0
#	- use some functions from ipacsum

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "${General::swroot}/net-traffic/net-traffic-admin.pl";
require "${General::swroot}/net-traffic/net-traffic-lib.pl";

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

my @dummy = (@NETTRAFF::months, @NETTRAFF::longmonths, $NETTRAFF::colorOk, $NETTRAFF::colorWarn, $NETTRAFF::colorMax);
undef(@dummy);

my %cgiparams;
my %pppsettings;
my %netsettings;

&General::readhash("${General::swroot}/ppp/settings", \%pppsettings);
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

my @now = localtime(time);

$now[5] = $now[5]+1900;

$cgiparams{'STARTYEAR'} = $now[5];
$cgiparams{'STARTMONTH'} = $now[4];

my $startDay = '1';
my $endDay = '1';

if($NETTRAFF::settings{'MONTHLY_VOLUME_ON'} eq 'on')
{
	$startDay = $NETTRAFF::settings{'STARTDAY'};
	$endDay = $NETTRAFF::settings{'STARTDAY'};
}

# this periode started last month
if ($now[3] < $startDay)
{
	# when current month is january we start in last year december
	if ($now[4] == 0) {
		$cgiparams{'STARTYEAR'} = $now[5]-1;
		$cgiparams{'STARTMONTH'} = 11;
	}
	else
	{
		$cgiparams{'STARTYEAR'} = $now[5];
		$cgiparams{'STARTMONTH'} = $now[4]-1;
	}
}

&Header::getcgihash(\%cgiparams);

my $selectYearALL = "";
$selectYearALL = 'selected=\'selected\'' if($cgiparams{'STARTYEAR'} eq '????');

my $selectMonthALL = "";
$selectMonthALL = 'selected=\'selected\'' if($cgiparams{'STARTMONTH'} eq '??');

&Header::showhttpheaders();
&Header::openpage($Lang::tr{'sstraffic'}, 1, '');
&Header::openbigbox('100%', 'left');
&Header::openbox('100%', 'left', "");

my $firstDayTxt = '';

if($NETTRAFF::settings{'MONTHLY_VOLUME_ON'} eq 'on')
{
	$firstDayTxt = " ($Lang::tr{'monthly volume start day short'}: $NETTRAFF::settings{'STARTDAY'}.)";
}

print <<END;
	<table width='100%' align='center'>
	<tr>
		<td width='90%' align='left' nowrap='nowrap'>
			<form method='post' action='/cgi-bin/traffic.cgi'>
				$Lang::tr{'selecttraffic'}$firstDayTxt:
				<select name='STARTMONTH'>
END

foreach my $month (@NETTRAFF::months)
{
	print "\t<option ";
	if ("$month" eq "$cgiparams{'STARTMONTH'}") {
		print 'selected=\'selected\' '; }
	print "value='$month'>$NETTRAFF::longmonths[$month]</option>\n";
}

print <<END;
					<option $selectMonthALL value='??'>$Lang::tr{'allmsg'}</option>
				</select>
				<select name='STARTYEAR'>
END

for (my $index=0; $index<=$#NETTRAFF::years; $index++) {
	print "\t<option ";
	if ("$NETTRAFF::years[$index]" eq "$cgiparams{'STARTYEAR'}") {
		print 'selected=\'selected\' '; }
	print "value='$NETTRAFF::years[$index]'>$NETTRAFF::years[$index]</option>\n";
}

print <<END;
					<option $selectYearALL value='????'>$Lang::tr{'allmsg'}</option>
				</select>
				<input type='submit' name='ACTION' value='$Lang::tr{'update'}' />
			</form>
		</td>
		<td width='5%' align='center'>
			<form method='post' action='/cgi-bin/traffics.cgi'>
			<input type='submit' name='ACTION' value=' > ' />
			</form>
		</td>
	</tr>
	</table>
END

&Header::closebox();

&Header::openbox('100%', 'left', "$Lang::tr{'traffics'}");

my $dateWidth = '20%';
my $netWidth = '34%';
my $inOutWidth = '17%';

# 4 networks
if ($netsettings{'CONFIG_TYPE'} =~ /^(4)$/) {
	$dateWidth = '12%';
	$netWidth = '22%';
	$inOutWidth = '11%';
}
# 3 networks
if ($netsettings{'CONFIG_TYPE'} =~ /^(2|3)$/) {
	$dateWidth = '16%';
	$netWidth = '28%';
	$inOutWidth = '14%';
}

print <<END;
	<table width='100%'>
	<tr>
		<td width='$dateWidth' align='center' class='boldbase'></td>
		<td width='$netWidth' align='center' class='boldbase' ><b>$Lang::tr{'trafficgreen'}</b></td>
END

if ($netsettings{'CONFIG_TYPE'} =~ /^(3|4)$/) {
	print "<td width='$netWidth' align='center' class='boldbase' ><b>$Lang::tr{'trafficblue'}</b></td>";
}

if ($netsettings{'CONFIG_TYPE'} =~ /^(2|4)$/) {
	print "<td width='$netWidth' align='center' class='boldbase' ><b>$Lang::tr{'trafficorange'}</b></td>";
}

if ($netsettings{'CONFIG_TYPE'} =~ /^(1|2|3|4)$/) {
  print "<td width='$netWidth' align='center' class='boldbase'><b>$Lang::tr{'trafficred'}</b></td>";
}
print <<END;
	</tr>
	</table>
	<table width='100%'>
	<tr>
		<td width='$dateWidth' align='center' class='boldbase'><b>$Lang::tr{'trafficdate'}</b></td>
		<td width='$inOutWidth' align='center' class='boldbase'><font color='$Header::colourgreen'><b>$Lang::tr{'trafficin'}</b></font></td>
		<td width='$inOutWidth' align='center' class='boldbase'><font color='$Header::colourgreen'><b>$Lang::tr{'trafficout'}</b></font></td>
END

if ($netsettings{'CONFIG_TYPE'} =~ /^(3|4)$/)
{
	print "<td width='$inOutWidth' align='center' class='boldbase'><font color='${Header::colourblue}'><b>$Lang::tr{'trafficin'}</b></font></td>";
	print "<td width='$inOutWidth' align='center' class='boldbase'><font color='${Header::colourblue}'><b>$Lang::tr{'trafficout'}</b></font></td>";
}

if ($netsettings{'CONFIG_TYPE'} =~ /^(2|4)$/)
{
	print "<td width='$inOutWidth' align='center' class='boldbase'><font color='$Header::colourorange'><b>$Lang::tr{'trafficin'}</b></font></td>";
	print "<td width='$inOutWidth' align='center' class='boldbase'><font color='$Header::colourorange'><b>$Lang::tr{'trafficout'}</b></font></td>";
}
if ($netsettings{'CONFIG_TYPE'} =~ /^(1|2|3|4)$/)
{
print "<td width='$inOutWidth' align='center' class='boldbase'><font color='$Header::colourred'><b>$Lang::tr{'trafficin'}</b></font></td>";
print "<td width='$inOutWidth' align='center' class='boldbase'><font color='$Header::colourred'><b>$Lang::tr{'trafficout'}</b></font></td>";
}
print "</tr>";

my $total_blue_in=0;
my $total_blue_out=0;
my $total_green_in=0;
my $total_green_out=0;
my $total_orange_in=0;
my $total_orange_out=0;
my $total_red_in=0;
my $total_red_out=0;
my $lines=0;



my $startYear = $cgiparams{'STARTYEAR'};
my $endYear = $cgiparams{'STARTYEAR'};
my $startMonth = $cgiparams{'STARTMONTH'};
my $endMonth = $cgiparams{'STARTMONTH'};
my $displayMode = "daily_multi";
$startDay = '1';
$endDay = '1';
my $selectedMonth = '0';

if($NETTRAFF::settings{'MONTHLY_VOLUME_ON'} eq 'on')
{
	$startDay = $NETTRAFF::settings{'STARTDAY'};
	$endDay = $NETTRAFF::settings{'STARTDAY'};
}

# "show All ?
if ($cgiparams{'STARTYEAR'} eq '????')
{
	# 'show all month' + 'show all years'
	# OR <selected Month> + 'show all years'

	# if we have a <selected Month>, we read all traffic but display only the selected month
	if($cgiparams{'STARTMONTH'} ne '??')
	{
		$selectedMonth = $cgiparams{'STARTMONTH'} + 1;
		$selectedMonth = $selectedMonth < 10 ? $selectedMonth = "0".$selectedMonth : $selectedMonth;
	}

	$displayMode = "monthly";
	# start with 1970-01-01
	$startYear = 1970;
	$startMonth = '1';
	$startDay = '1';
	# end with next year: 20xx-01-01
	$endYear = $now[5] + 1;
	$endMonth = '1';
	$endDay = '1';
}
elsif ($cgiparams{'STARTMONTH'} eq '??')
{
	# 'show all month' + 200x
	$displayMode = "monthly";
	# start with 200x-01-01
	$startMonth = '1';
	$startDay = '1';
	# end with (200x+1)-01-01
	$endYear = $startYear + 1;
	$endMonth = '1';
	$endDay = '1';
}
else
{
	# no "Show All"
	$startMonth++;
	$endMonth = $endMonth + 2;

	# this periode started last month
	if ($now[3] < $startDay)
	{
		# when current month is january we start in last year december
		if ($endMonth == 1) {
			$startYear--;
			$startMonth = 12;
		}
	}
	else
	{
		# when we are in december, this periode ends next year january
		if ($startMonth == 12) {
			$endYear++;
			$endMonth = 1;
		}
	}
}



$startMonth = $startMonth < 10 ? $startMonth = "0".$startMonth : $startMonth;
$endMonth = $endMonth < 10 ? $endMonth = "0".$endMonth : $endMonth;
$startDay = $startDay < 10 ? $startDay = "0".$startDay : $startDay;
$endDay = $endDay < 10 ? $endDay = "0".$endDay : $endDay;

my $start = "$startYear$startMonth$startDay";
my $end = "$endYear$endMonth$endDay";

my %allDaysBytes = ();
my @allDays = &Traffic::calcTraffic(\%allDaysBytes,$start,$end, $displayMode);


foreach (@allDays)
{
	# special code for: <selected Month> + 'show all years'
	if($cgiparams{'STARTMONTH'} ne '??' && $cgiparams{'STARTYEAR'} eq '????')
	{
		# show only those traffic in the selected month
		if($allDaysBytes{$_}{'Day'} !~ /^\d\d\d\d-$selectedMonth$/)
		{
			next;
		}
	}

	$total_green_in += $allDaysBytes{$_}{${Traffic::green_in}};
	$total_green_out += $allDaysBytes{$_}{${Traffic::green_out}};

	if ($netsettings{'CONFIG_TYPE'} =~ /^(3|4)$/)
	{
		$total_blue_in += $allDaysBytes{$_}{${Traffic::blue_in}};
		$total_blue_out += $allDaysBytes{$_}{${Traffic::blue_out}};
	}

	if ($netsettings{'CONFIG_TYPE'} =~ /^(2|4)$/)
	{
		$total_orange_in += $allDaysBytes{$_}{${Traffic::orange_in}};
		$total_orange_out += $allDaysBytes{$_}{${Traffic::orange_out}};
	}

  if ($netsettings{'CONFIG_TYPE'} =~ /^(1|2|3|4)$/)
  {
	$total_red_in += $allDaysBytes{$_}{${Traffic::red_in}};
	$total_red_out += $allDaysBytes{$_}{${Traffic::red_out}};
  }
  
	if ($lines % 2) {
		print "<tr bgcolor='$color{'color20'}'>"; }
	else {
		print "<tr bgcolor='$color{'color22'}}'>"; }

	printf "<td align='center' nowrap='nowrap'>%s</td>\n", $allDaysBytes{$_}{'Day'};
	printf "<td align='center' nowrap='nowrap'>%.3f</td>\n", ($allDaysBytes{$_}{${Traffic::green_in}}/1048576);
	printf "<td align='center' nowrap='nowrap'>%.3f</td>\n", ($allDaysBytes{$_}{${Traffic::green_out}}/1048576);

	if ($netsettings{'CONFIG_TYPE'} =~ /^(3|4)$/)
	{
		printf "<td align='center' nowrap='nowrap'>%.3f</td>\n", ($allDaysBytes{$_}{${Traffic::blue_in}}/1048576);
		printf "<td align='center' nowrap='nowrap'>%.3f</td>\n", ($allDaysBytes{$_}{${Traffic::blue_out}}/1048576);
	}
	if ($netsettings{'CONFIG_TYPE'} =~ /^(2|4)$/)
	{
		printf "<td align='center' nowrap='nowrap'>%.3f</td>\n", ($allDaysBytes{$_}{${Traffic::orange_in}}/1048576);
		printf "<td align='center' nowrap='nowrap'>%.3f</td>\n", ($allDaysBytes{$_}{${Traffic::orange_out}}/1048576);
	}

  if ($netsettings{'CONFIG_TYPE'} =~ /^(1|2|3|4)$/)
  {
	printf "<td align='center' nowrap='nowrap'>%.3f</td>\n", ($allDaysBytes{$_}{${Traffic::red_in}}/1048576);
	printf "<td align='center' nowrap='nowrap'>%.3f</td></tr>\n", ($allDaysBytes{$_}{${Traffic::red_out}}/1048576);
  }
  
	$lines++;
}

$total_green_in=sprintf("%.2f", ($total_green_in/1048576));
$total_green_out=sprintf("%.2f", ($total_green_out/1048576));
$total_blue_in=sprintf("%.2f", ($total_blue_in/1048576));
$total_blue_out=sprintf("%.2f", ($total_blue_out/1048576));
$total_orange_in=sprintf("%.2f", ($total_orange_in/1048576));
$total_orange_out=sprintf("%.2f", ($total_orange_out/1048576));
$total_red_in=sprintf("%.2f", ($total_red_in/1048576));
$total_red_out=sprintf("%.2f", ($total_red_out/1048576));

if ($lines % 2) {print "<tr bgcolor='$color{'color20'}'>"; }
else {print "<tr bgcolor='$color{'color22'}'>"; }

print <<END;
	<td align='center' class='boldbase' height='20' nowrap='nowrap'><b>$Lang::tr{'trafficsum'}</b></td>
	<td align='center' class='boldbase' nowrap='nowrap'><b>$total_green_in MB</b></td>
	<td align='center' class='boldbase' nowrap='nowrap'><b>$total_green_out MB</b></td>
END

if ($netsettings{'CONFIG_TYPE'} =~ /^(3|4)$/)
{
	print "<td align='center' class='boldbase' nowrap='nowrap'><b>$total_blue_in MB</b></td>";
	print "<td align='center' class='boldbase' nowrap='nowrap'><b>$total_blue_out MB</b></td>";
}

if ($netsettings{'CONFIG_TYPE'} =~ /^(2|4)$/)
{
	print "<td align='center' class='boldbase' nowrap='nowrap'><b>$total_orange_in MB</b></td>";
	print "<td align='center' class='boldbase' nowrap='nowrap'><b>$total_orange_out MB</b></td>";
}
if ($netsettings{'CONFIG_TYPE'} =~ /^(1|2|3|4)$/)
{
print "<td align='center' class='boldbase' nowrap='nowrap'><b>$total_red_in MB</b></td>";
print "<td align='center' class='boldbase' nowrap='nowrap'><b>$total_red_out MB</b></td>";
}
print "</tr></table>";

if($NETTRAFF::settings{'MONTHLY_VOLUME_ON'} eq 'on')
{
	my $total_red_all = sprintf("%.2f", ($total_red_in + $total_red_out));

	my $color = $NETTRAFF::colorOk;

	my $warnTraff = ($NETTRAFF::settings{'MONTHLY_VOLUME'} * $NETTRAFF::settings{'WARN'} / 100);
	if($NETTRAFF::settings{'WARN_ON'} eq 'on'
		&& $warnTraff < $total_red_all)
	{
		$color = $NETTRAFF::colorWarn;
	}
	if($NETTRAFF::settings{'MONTHLY_VOLUME'} < $total_red_all)
	{
		$color = $NETTRAFF::colorMax;
	}

	print <<END;
		<table width='100%'>
		<tr><td align='center' class='boldbase' nowrap='nowrap' ><b>$Lang::tr{'monthly volume'} ($NETTRAFF::settings{'MONTHLY_VOLUME'} MB)</b></td></tr>
		<tr><td align='center' class='boldbase' nowrap='nowrap' bgcolor='$color'><b>$total_red_all MB</b></td></tr>
		</table>
END
}

&Header::closebox();
&Header::closebigbox();
&Header::closepage();
