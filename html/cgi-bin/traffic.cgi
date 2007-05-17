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

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

my %cgiparams; 
my %pppsettings;
my %netsettings;

&General::readhash("${General::swroot}/ppp/settings", \%pppsettings);
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

my @wday = ($Lang::tr{'wday1'}, $Lang::tr{'wday2'}, $Lang::tr{'wday3'}, $Lang::tr{'wday4'}, $Lang::tr{'wday5'}, $Lang::tr{'wday6'}, $Lang::tr{'wday7'});

my ($s, $min, $h, $d, $m,$y) = localtime(time);
$y+=1900;
$m+=1;
$m = $m < 10 ? $m = "0".$m : $m;

$cgiparams{'MONTH'} = $m;
&Header::getcgihash(\%cgiparams);
$cgiparams{'YEAR'} = $y;
&Header::getcgihash(\%cgiparams);

&Header::showhttpheaders();

my %selectYear;
$selectYear{'YEAR'}{'2007'} = '';
$selectYear{'YEAR'}{'2008'} = '';
$selectYear{'YEAR'}{'2009'} = '';
$selectYear{'YEAR'}{'2010'} = '';
$selectYear{'YEAR'}{'2011'} = '';
$selectYear{'YEAR'}{'2012'} = '';
$selectYear{'YEAR'}{'????'} = '';
$selectYear{'YEAR'}{$cgiparams{'YEAR'}} = 'selected=\'selected\'';


my %selected;

$selected{'MONTH'}{'01'} = '';
$selected{'MONTH'}{'02'} = '';
$selected{'MONTH'}{'03'} = '';
$selected{'MONTH'}{'04'} = '';
$selected{'MONTH'}{'05'} = '';
$selected{'MONTH'}{'06'} = '';
$selected{'MONTH'}{'07'} = '';
$selected{'MONTH'}{'08'} = '';
$selected{'MONTH'}{'09'} = '';
$selected{'MONTH'}{'10'} = '';
$selected{'MONTH'}{'11'} = '';
$selected{'MONTH'}{'12'} = '';
$selected{'MONTH'}{'??'} = '';
$selected{'MONTH'}{$cgiparams{'MONTH'}} = 'selected=\'selected\'';

&Header::openpage($Lang::tr{'sstraffic'}, 1, '');

&Header::openbigbox('100%', 'left');

&Header::openbox('100%', 'left', $Lang::tr{'settingsc'});

print <<END;
	<table width='80%' align='center'>
	<tr>
		<td width='95%' align='left' nowrap='nowrap'>
			<form method='post' action='/cgi-bin/traffic.cgi'>
				$Lang::tr{'selecttraffic'}
				<select name='MONTH'>		
					<option $selected{'MONTH'}{'01'} value='01'>$Lang::tr{'january'}</option>
					<option $selected{'MONTH'}{'02'} value='02'>$Lang::tr{'february'}</option>
					<option $selected{'MONTH'}{'03'} value='03'>$Lang::tr{'march'}</option>
					<option $selected{'MONTH'}{'04'} value='04'>$Lang::tr{'april'}</option>
					<option $selected{'MONTH'}{'05'} value='05'>$Lang::tr{'may'}</option>
					<option $selected{'MONTH'}{'06'} value='06'>$Lang::tr{'june'}</option>
					<option $selected{'MONTH'}{'07'} value='07'>$Lang::tr{'july'}</option>
					<option $selected{'MONTH'}{'08'} value='08'>$Lang::tr{'august'}</option>
					<option $selected{'MONTH'}{'09'} value='09'>$Lang::tr{'september'}</option>
					<option $selected{'MONTH'}{'10'} value='10'>$Lang::tr{'october'}</option>
					<option $selected{'MONTH'}{'11'} value='11'>$Lang::tr{'november'}</option>
					<option $selected{'MONTH'}{'12'} value='12'>$Lang::tr{'december'}</option>
					<option $selected{'MONTH'}{'??'} value='??'>$Lang::tr{'allmsg'}</option>
				</select>
				<select name='YEAR'>		
					<option $selectYear{'YEAR'}{'2007'} value='2007'>2007</option>
					<option $selectYear{'YEAR'}{'2008'} value='2008'>2008</option>
					<option $selectYear{'YEAR'}{'2009'} value='2009'>2009</option>
					<option $selectYear{'YEAR'}{'2010'} value='2010'>2010</option>
					<option $selectYear{'YEAR'}{'2011'} value='2011'>2011</option>
					<option $selectYear{'YEAR'}{'2012'} value='2012'>2012</option>
					<option $selectYear{'YEAR'}{'????'} value='????'>$Lang::tr{'allmsg'}</option>
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

my $displayMode = "daily";
my $startMonth = $cgiparams{'MONTH'};
my $endMonth = $cgiparams{'MONTH'};

if ($cgiparams{'MONTH'} eq '??') {
	$displayMode = "monthly";
	$startMonth = '01';
	$endMonth = '12';
}

my $start = "$cgiparams{'YEAR'}$startMonth"."01";
my $end = "$cgiparams{'YEAR'}$endMonth"."32";
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
		print "<tr bgcolor='$color{'color20'}'>"; }
	else {
		print "<tr bgcolor='$color{'color22'}'>"; }
				
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
	
if ($lines % 2) {print "<tr bgcolor='$color{'color20'}'>"; }
else {print "<tr bgcolor='$color{'color22'}'>"; }
  
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
