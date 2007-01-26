#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#

use strict;

# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require '/var/ipfire/net-traffic/net-traffic-lib.pl';

my %cgiparams; 
my %netsettings;

&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

my @years=("2007","2008","2009","2010","2011","2012","2013","2014","2015");

my @longmonths = ( $Lang::tr{'january'}, $Lang::tr{'february'}, $Lang::tr{'march'},
	$Lang::tr{'april'}, $Lang::tr{'may'}, $Lang::tr{'june'}, $Lang::tr{'july'}, $Lang::tr{'august'},
	$Lang::tr{'september'}, $Lang::tr{'october'}, $Lang::tr{'november'},
	$Lang::tr{'december'} );

my @months = ( 0,1,2,3,4,5,6,7,8,9,10,11 );
my @days = ( 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31 );

my @wday = ($Lang::tr{'wday1'}, $Lang::tr{'wday2'}, $Lang::tr{'wday3'}, $Lang::tr{'wday4'}, $Lang::tr{'wday5'}, $Lang::tr{'wday6'}, $Lang::tr{'wday7'});

my @now = localtime(time);	

$now[5] = $now[5]+1900;

$cgiparams{'STARTDAY'} = 10;  
$cgiparams{'STOPDAY'} = 11;  
$cgiparams{'STARTYEAR'} = $now[5];  
$cgiparams{'STOPYEAR'} = $now[5];  

# this periode started last month
if ($now[3] < 10) {
	$cgiparams{'STARTMONTH'} = $now[4]-1;
	$cgiparams{'STOPMONTH'} = $now[4];
	# when current month is january we start in last year december
	if ($now[4] == 0) {
		$cgiparams{'STARTYEAR'} = $now[5]-1;
		$cgiparams{'STARTMONTH'} = 11; 
	}
}
else {
	$cgiparams{'STARTMONTH'} = $now[4];
	$cgiparams{'STOPMONTH'} = $now[4]+1;
	# when we are december, this periode ends next year january
	if ($now[4] == 11) {
		$cgiparams{'STOPYEAR'} = $now[5]+1; 
		$cgiparams{'STOPMONTH'} = 0;
	}
}
	
&Header::getcgihash(\%cgiparams);

&Header::showhttpheaders();

&Header::openpage($Lang::tr{'sstraffic'}, 1, '');

&Header::openbigbox('100%', 'left');

&Header::openbox('100%', 'left', $Lang::tr{'settingsc'});

print <<END;
<table width='100%' align='center'>
<tr>
	<td width='95%' class='base' align='center'>
		<form method='post' action='/cgi-bin/traffics.cgi'>
		$Lang::tr{'trafficfrom'}
		<select name='STARTDAY'>
END

foreach (@days) 
{
	print "\t<option ";
	if ($_ == $cgiparams{'STARTDAY'}) {
		print 'selected=\'selected\' '; }
	print "value='$_'>$_</option>\n";
}
print <<END;
	</select>
	<select name='STARTMONTH'>
END

foreach (@months)
{
	print "\t<option ";
	if ($_ == $cgiparams{'STARTMONTH'}) {
		print 'selected=\'selected\' '; }
	print "value='$_'>$longmonths[$_]</option>\n";
}

print <<END;
	</select>
	<select name='STARTYEAR'>
END

for (my $index=0; $index<=$#years; $index++) {
	print "\t<option ";
	if ($years[$index] == $cgiparams{'STARTYEAR'}) {
		print 'selected=\'selected\' '; }
	print "value='$years[$index]'>$years[$index]</option>\n";
}

print <<END;
	</select>
	$Lang::tr{'trafficto'}
	<select name='STOPDAY'>
END

foreach (@days) 
{
	print "\t<option ";
	if ($_ == $cgiparams{'STOPDAY'}) 
		{
		print 'selected=\'selected\' '; }
	print "value='$_'>$_</option>\n";
}

print <<END;
	</select>
	<select name='STOPMONTH'>
END

foreach (@months)
{
	print "\t<option ";
	if ($_ == $cgiparams{'STOPMONTH'}) {
		print 'selected=\'selected\' '; }
	print "value='$_'>$longmonths[$_]</option>\n";
}

print <<END;
	</select>
	<select name='STOPYEAR'>
END

for (my $index = 0; $index <=$#years; $index++) {
	print "\t<option ";
	if ($years[$index] == $cgiparams{'STOPYEAR'}) {
		print 'selected=\'selected\' '; }
	print "value='$years[$index]'>$years[$index]</option>\n";
}


print <<END;
			</select>
			<input type='submit' name='ACTION' value='$Lang::tr{'update'}' />
		</form>	
	</td>        
	<td width='5%' align='center'>
		<form method='post' action='/cgi-bin/traffic.cgi'>
		<input type='submit' name='ACTION' value=' > ' />
		</form>
	</td>	
	</tr>
	</table>
END

&Header::closebox();

&Header::openbox('100%', 'left', $Lang::tr{'traffics'});

my $dateWidth = '20%';
my $netWidth = '34%';
my $inOutWidth = '17%';

# 4 networks
if ($netsettings{'CONFIG_TYPE'} =~ /^(5|7)$/) {
	$dateWidth = '12%';
	$netWidth = '22%';
	$inOutWidth = '11%';
}
# 3 networks
if ($netsettings{'CONFIG_TYPE'} =~ /^(1|3|4|6)$/) {
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

if ($netsettings{'CONFIG_TYPE'} =~ /^(4|5|6|7)$/) {
	print "<td width='$netWidth' align='center' class='boldbase' ><b>$Lang::tr{'trafficblue'}</b></td>";
}

if ($netsettings{'CONFIG_TYPE'} =~ /^(1|3|5|7)$/) {
	print "<td width='$netWidth' align='center' class='boldbase' ><b>$Lang::tr{'trafficorange'}</b></td>";
}

print <<END;
		<td width='$netWidth' align='center' class='boldbase'><b>$Lang::tr{'trafficred'}</b></td>
	</tr>
	</table>
	<table width='100%'>
	<tr>
		<td width='$dateWidth' align='center' class='boldbase'><b>$Lang::tr{'trafficdate'}</b></td>
		<td width='$inOutWidth' align='center' class='boldbase'><font color='#16A61D'><b>$Lang::tr{'trafficin'}</b></font></td>
		<td width='$inOutWidth' align='center' class='boldbase'><font color='#16A61D'><b>$Lang::tr{'trafficout'}</b></font></td>
END

if ($netsettings{'CONFIG_TYPE'} =~ /^(4|5|6|7)$/)
{  
	print "<td width='$inOutWidth' align='center' class='boldbase'><font color='${Header::colourblue}'><b>$Lang::tr{'trafficin'}</b></font></td>";
	print "<td width='$inOutWidth' align='center' class='boldbase'><font color='${Header::colourblue}'><b>$Lang::tr{'trafficout'}</b></font></td>";
} 

if ($netsettings{'CONFIG_TYPE'} =~ /^(1|3|5|7)$/)
{  
	print "<td width='$inOutWidth' align='center' class='boldbase'><font color='#FF9933'><b>$Lang::tr{'trafficin'}</b></font></td>";
	print "<td width='$inOutWidth' align='center' class='boldbase'><font color='#FF9933'><b>$Lang::tr{'trafficout'}</b></font></td>";
} 
print <<END;
		<td width='$inOutWidth' align='center' class='boldbase'><font color='#CE1B31'><b>$Lang::tr{'trafficin'}</b></font></td>
		<td width='$inOutWidth' align='center' class='boldbase'><font color='#CE1B31'><b>$Lang::tr{'trafficout'}</b></font></td>
	</tr>
END

my $total_blue_in=0;
my $total_blue_out=0;
my $total_green_in=0;
my $total_green_out=0;
my $total_orange_in=0;
my $total_orange_out=0;
my $total_red_in=0;
my $total_red_out=0;
my $lines=0;


my $startyear = $cgiparams{'STARTYEAR'};
my $stopyear = $cgiparams{'STOPYEAR'};

my $startMonth = $cgiparams{'STARTMONTH'}+1;
$startMonth = $startMonth < 10 ? $startMonth = "0".$startMonth : $startMonth;

my $endMonth = $cgiparams{'STOPMONTH'}+1;
$endMonth = $endMonth < 10 ? $endMonth = "0".$endMonth : $endMonth;

my $startDay = $cgiparams{'STARTDAY'};
$startDay = $startDay < 10 ? $startDay = "0".$startDay : $startDay;

my $endDay = $cgiparams{'STOPDAY'}+1;
$endDay = $endDay < 10 ? $endDay = "0".$endDay : $endDay;

my $displayMode = "daily_multi";
my $start = $startyear.$startMonth.$startDay;
my $end = $stopyear.$endMonth.$endDay;

my %allDaysBytes = ();
my @allDays = &Traffic::calcTraffic(\%allDaysBytes,$start,$end, $displayMode);


foreach (@allDays) {
	$total_green_in += $allDaysBytes{$_}{${Traffic::green_in}};
	$total_green_out += $allDaysBytes{$_}{${Traffic::green_out}};
		
	if ($netsettings{'CONFIG_TYPE'} =~ /^(4|5|6|7)$/)
	{
		$total_blue_in += $allDaysBytes{$_}{${Traffic::blue_in}};
		$total_blue_out += $allDaysBytes{$_}{${Traffic::blue_out}};
	}
		
	if ($netsettings{'CONFIG_TYPE'} =~ /^(1|3|5|7)$/)
	{
		$total_orange_in += $allDaysBytes{$_}{${Traffic::orange_in}};
		$total_orange_out += $allDaysBytes{$_}{${Traffic::orange_out}};
	}
		
	$total_red_in += $allDaysBytes{$_}{${Traffic::red_in}};
	$total_red_out += $allDaysBytes{$_}{${Traffic::red_out}};
				
	if ($lines % 2) {
		print "<tr bgcolor='${Header::table1colour}'>"; }
	else {
		print "<tr bgcolor='${Header::table2colour}'>"; }
				
	printf "<td align='center' nowrap='nowrap'>%s</td>\n", $allDaysBytes{$_}{'Day'};
	printf "<td align='center' nowrap='nowrap'>%.3f</td>\n", ($allDaysBytes{$_}{${Traffic::green_in}}/1048576);
	printf "<td align='center' nowrap='nowrap'>%.3f</td>\n", ($allDaysBytes{$_}{${Traffic::green_out}}/1048576);
		
	if ($netsettings{'CONFIG_TYPE'} =~ /^(4|5|6|7)$/)
	{   
		printf "<td align='center' nowrap='nowrap'>%.3f</td>\n", ($allDaysBytes{$_}{${Traffic::blue_in}}/1048576);
		printf "<td align='center' nowrap='nowrap'>%.3f</td>\n", ($allDaysBytes{$_}{${Traffic::blue_out}}/1048576);
	} 
	if ($netsettings{'CONFIG_TYPE'} =~ /^(1|3|5|7)$/)
	{   
		printf "<td align='center' nowrap='nowrap'>%.3f</td>\n", ($allDaysBytes{$_}{${Traffic::orange_in}}/1048576);
		printf "<td align='center' nowrap='nowrap'>%.3f</td>\n", ($allDaysBytes{$_}{${Traffic::orange_out}}/1048576);
	} 
		
	printf "<td align='center' nowrap='nowrap'>%.3f</td>\n", ($allDaysBytes{$_}{${Traffic::red_in}}/1048576);
	printf "<td align='center' nowrap='nowrap'>%.3f</td></tr>\n", ($allDaysBytes{$_}{${Traffic::red_out}}/1048576);
    	        
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
	
if ($lines % 2) {print "<tr bgcolor='${Header::table1colour}'>"; }
else {print "<tr bgcolor='${Header::table2colour}'>"; }
  
print <<END;
	<td align='center' class='boldbase' height='20' nowrap='nowrap'><b>$Lang::tr{'trafficsum'}</b></td>
	<td align='center' class='boldbase' nowrap='nowrap'><b>$total_green_in MB</b></td>
	<td align='center' class='boldbase' nowrap='nowrap'><b>$total_green_out MB</b></td>
END
  
if ($netsettings{'CONFIG_TYPE'} =~ /^(4|5|6|7)$/)
{    
	print "<td align='center' class='boldbase' nowrap='nowrap'><b>$total_blue_in MB</b></td>";
	print "<td align='center' class='boldbase' nowrap='nowrap'><b>$total_blue_out MB</b></td>";
}

if ($netsettings{'CONFIG_TYPE'} =~ /^(1|3|5|7)$/)
{    
	print "<td align='center' class='boldbase' nowrap='nowrap'><b>$total_orange_in MB</b></td>";
	print "<td align='center' class='boldbase' nowrap='nowrap'><b>$total_orange_out MB</b></td>";
}
     
print <<END;
		<td align='center' class='boldbase' nowrap='nowrap'><b>$total_red_in MB</b></td>
		<td align='center' class='boldbase' nowrap='nowrap'><b>$total_red_out MB</b></td>
	</tr>
	</table>
END

&Header::closebox();

&Header::closebigbox();

&Header::closepage();
