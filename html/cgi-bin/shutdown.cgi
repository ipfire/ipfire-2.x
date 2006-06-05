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
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require 'CONFIG_ROOT/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %cgiparams=();
my $death = 0;
my $rebirth = 0;
my $default_time = '03:15';

&Header::showhttpheaders();

$cgiparams{'ACTION'} = '';
&Header::getcgihash(\%cgiparams);

if ($cgiparams{'ACTION'} eq $Lang::tr{'shutdown'}) {
	$death = 1;
	&General::log($Lang::tr{'shutting down ipfire'});
	#system '/usr/local/bin/ipfiredeath';
	system '/usr/local/bin/ipfirereboot down';
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'reboot'}) {
	$rebirth = 1;
	&General::log($Lang::tr{'rebooting ipfire'});
	#system '/usr/local/bin/ipfirerebirth';
	system '/usr/local/bin/ipfirereboot boot';
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'save'}) {
	my $days='';
	my $n = 1;
	# build list of days
	map ($cgiparams{$_} eq 'on' ?  $days .= ",".$n++ : $n++ ,
	    ('MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY','SUNDAY') );

	# if days is empty, it is a remove else it is a change
	if (length ($days)){
	    substr($days,0,1) = ''; 	#kill front comma
	    &General::log("Scheduling reboot on $days at $cgiparams{'TIME'}");
	    my $min;
	    my $hour;
	    ($hour,$min) = split (':', $cgiparams{'TIME'});
	    $days = "'*'" if ($days eq '1,2,3,4,5,6,7');
	    my $mode = ($cgiparams{'MODE'} eq 'halt') ? '-h' : '-r';
	    system "/usr/local/bin/ipfirereboot cron+ $min $hour $days $mode"; #reboot checks values of $hour & $min
	} else {
	    &General::log("Remove scheduled reboot");
	    system '/usr/local/bin/ipfirereboot cron-';
	}
}
if ($death == 0 && $rebirth == 0) {

	&Header::openpage($Lang::tr{'shutdown control'}, 1, '');

	&Header::openbigbox('100%', 'left');

	print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

	&Header::openbox('100%', 'left', $Lang::tr{'shutdown2'});
	print <<END
<table width='100%'>
<tr>
	<td width='50%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'reboot'}' /></td>
	<td width='50%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'shutdown'}' /></td>
</tr>
</table>
END
	;
	&Header::closebox();

	&Header::openbox('100%', 'left', $Lang::tr{'reboot schedule'});
	my %checked=();
	my $reboot_at = $default_time;
	my $days = '';

	#decode the shutdown line stored in crontab
	#get the line
	open(FILE, "/usr/local/bin/ipfirereboot cron?|");
	my $schedule = <FILE>;
	close (FILE);

	if ($schedule) { # something exist
	    $schedule =~ /(\d+) (\d+) \* \* ([1234567*,]+) .* (-[h|r])/;
	    $reboot_at = sprintf("%.02d",$2) . ':' . sprintf("%.02d",$1);  # hour (03:45)
	    $days = $3;		# 1,2,3... or *
	    if ($4 eq '-h') {
                $checked{'MODE'}{'halt'} = "checked='checked'";
            } else {
                $checked{'MODE'}{'reboot'} = "checked='checked'";
            }
	}
	#decode $days
	if ($days eq '*') {
	    $checked{'MONDAY'} = "checked='checked'";
	    $checked{'TUESDAY'} = "checked='checked'";
	    $checked{'WEDNESDAY'} = "checked='checked'";
	    $checked{'THURSDAY'} = "checked='checked'";
	    $checked{'FRIDAY'} = "checked='checked'";
	    $checked{'SATURDAY'} = "checked='checked'";
	    $checked{'SUNDAY'} = "checked='checked'";
	} else {
	    $checked{'MONDAY'} = "checked='checked'" 	if ($days =~ /1/);
	    $checked{'TUESDAY'} = "checked='checked'"	if ($days =~ /2/);
	    $checked{'WEDNESDAY'} = "checked='checked'"	if ($days =~ /3/);
	    $checked{'THURSDAY'} = "checked='checked'"	if ($days =~ /4/);
	    $checked{'FRIDAY'} = "checked='checked'"	if ($days =~ /5/);
	    $checked{'SATURDAY'} = "checked='checked'"	if ($days =~ /6/);
	    $checked{'SUNDAY'} = "checked='checked'"	if ($days =~ /7/);	    
	}

	print <<END
<table width='100%'>
<tr>
    <td class='boldbase' colspan='2'><b>$Lang::tr{'time'}</b></td>
    <td class='boldbase' colspan='2'><b>$Lang::tr{'day'}</b></td>
    <td class='boldbase'><b>$Lang::tr{'action'}</b></td>
</tr>
<tr>
END
        ;
        print "<td align='left' width='15%' class='base' valign='top' rowspan='2'>", &select_hour_var("TIME", $reboot_at);
        print <<END
</td>
    <td>
        <input type='checkbox' name='MONDAY'    $checked{'MONDAY'}></td>
    <td width='15%' class='base'>
        $Lang::tr{'monday'}</td>
    <td>
        <input type='radio' name='MODE' value='reboot' $checked{'MODE'}{'reboot'} /></td>
    <td width='70%' class='base'>$Lang::tr{'reboot'}</td></tr>
<tr>
    <td>
        <input type='checkbox' name='TUESDAY'   $checked{'TUESDAY'}></td>
    <td width='15%' class='base'>
        $Lang::tr{'tuesday'}</td>
    <td>
        <input type='radio' name='MODE' value='halt' $checked{'MODE'}{'halt'} /></td>
    <td class='base'>$Lang::tr{'shutdown'}</td></tr>
<tr>
    <td>&nbsp;</td>
    <td>
        <input type='checkbox' name='WEDNESDAY' $checked{'WEDNESDAY'}></td>
    <td width='15%' class='base'>
        $Lang::tr{'wednesday'}</td></tr>
<tr>
    <td>&nbsp;</td>
    <td>
        <input type='checkbox' name='THURSDAY'  $checked{'THURSDAY'}></td>
    <td width='15%' class='base'>
        $Lang::tr{'thursday'}</td></tr>
<tr>
    <td>&nbsp;</td>
    <td>
        <input type='checkbox' name='FRIDAY'    $checked{'FRIDAY'}></td>
    <td width='15%' class='base'>
        $Lang::tr{'friday'}</td></tr>
<tr>
    <td>&nbsp;</td>
    <td>
        <input type='checkbox' name='SATURDAY'  $checked{'SATURDAY'}></td>
    <td width='15%' class='base'>
        $Lang::tr{'saturday'}</td></tr>
<tr>
    <td>&nbsp;</td>
    <td>
        <input type='checkbox' name='SUNDAY'    $checked{'SUNDAY'}></td>
    <td width='15%' class='base'>
        $Lang::tr{'sunday'}</td></tr>
</table>

<table width='100%'>
<hr />
<tr>
    <td width='60%'>&nbsp;</td>
    <td width='30%' align='center'>
        <input type='submit' name='ACTION' value='$Lang::tr{'save'}' />
    </td>
    <td width='10%' align='right'>&nbsp;
</tr>
</table>

END
;
	&Header::closebox();
	print "</form>\n";
} else {
	my $message='';
	my $title='';
	my $refresh = "<meta http-equiv='refresh' content='5; URL=/cgi-bin/index.cgi' />";
	if ($death) {
		$title = $Lang::tr{'shutting down'};
		$message = $Lang::tr{'ipfire has now shutdown'};
	} else {
		$title = $Lang::tr{'rebooting'};
		$message = $Lang::tr{'ipfire has now rebooted'};
	}
	&Header::openpage($title, 0, $refresh);

	&Header::openbigbox('100%', 'center');
	print <<END
<div align='center'>
<table width='100%' bgcolor='#ffffff'>
<tr><td align='center'>
<br /><br /><img src='/ipfire_big.gif' /><br /><br /><br />
</td></tr>
</table>
<br />
<font size='6'>$message</font>
</div>
END
	;
}

&Header::closebigbox();
&Header::closepage();



# Create a named select box containing valid times from quarter to quarter.
sub select_hour_var {
	# Create a variable containing the SELECT with selected value variable name and current value selected
        my $select_hour_var = shift;
	my $selected_hour = shift;

	my $select_hour = "<select name='$select_hour_var'>";
	my $hh = 0;
	my $mm = 15;
	my $str = '00:00';
	for (my $x=0; $x<(24*4); $x++) {
	    my $check = $selected_hour eq $str ?  "selected='selected'" : '';
	    $select_hour .= "<Option $check value='$str'>$str";
	    $str = sprintf("%.02d", $hh) . ":" . sprintf("%.02d", $mm);
	    $mm += 15;
	    if ($mm==60) {$mm=0; $hh++; }
	}
	$select_hour .= "</select>\n";
	return ($select_hour);
}
