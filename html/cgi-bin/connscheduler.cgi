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

require '/var/ipfire/connscheduler/lib.pl';

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

my $buttontext = $Lang::tr{'add'};
my $hiddenvalue = 'add';
my $day;
my $hour;
my $minute;
my %temppppsettings=();
my @profilenames=();


#
# defaults for settings
#
my $selected_hour = '00';
my $selected_minute = '00';
my $checked_connect = "checked='checked'";
my $checked_profile = '';
my %selected = ();
$selected{'reconnect'} = '';
$selected{'dial'} = '';
$selected{'hangup'} = '';
$selected{'reboot'} = '';
$selected{'shutdown'} = '';
$selected{'ipsecstart'} = '';
$selected{'ipsecstop'} = '';
my $selected_profile = 1;
my $checked_days = "checked='checked'";
my $selected_daystart = 1;
my $selected_dayend = 31;
my $checked_weekdays = '';
my $checked_mon = "checked='checked'";
my $checked_tue = "checked='checked'";
my $checked_wed = "checked='checked'";
my $checked_thu = "checked='checked'";
my $checked_fri = "checked='checked'";
my $checked_sat = "checked='checked'";
my $checked_sun = "checked='checked'";
my $comment = '';

my %cgiparams = ();

$cgiparams{'ACTION'} = '';              # add/edit/update/remove/wakeup
$cgiparams{'ACTION_ACTION'} = '';       # CONNECT/PROFILE
$cgiparams{'ACTION_CONNECT'} = '';      # connect/disconnect/reconnect
$cgiparams{'ACTION_PROFILENR'} = 0;
$cgiparams{'ACTION_HOUR'} = '';
$cgiparams{'ACTION_MINUTE'} = '';
$cgiparams{'ACTION_DAYSTYPE'} = '';
$cgiparams{'ACTION_DAYSTART'} = 1;
$cgiparams{'ACTION_DAYEND'} = 31;
$cgiparams{'Mon'} = '';
$cgiparams{'Tue'} = '';
$cgiparams{'Wed'} = '';
$cgiparams{'Thu'} = '';
$cgiparams{'Fri'} = '';
$cgiparams{'Sat'} = '';
$cgiparams{'Sun'} = '';
$cgiparams{'ACTION_COMMENT'} = '';

&Header::getcgihash(\%cgiparams);


# read the profile names
my $i=0;
for ($i = 1; $i <= $CONNSCHED::maxprofiles; $i++)
{
  %temppppsettings = ();
  $temppppsettings{'PROFILENAME'} = $Lang::tr{'empty'};
  &General::readhash("${General::swroot}/ppp/settings-$i", \%temppppsettings);
  $profilenames[$i] = $temppppsettings{'PROFILENAME'};
}

&Header::showhttpheaders();
&Header::openpage($Lang::tr{'connscheduler'}, 1, '');
&Header::openbigbox('100%', 'left', '', '');


# Found this usefull piece of code in BlockOutTraffic AddOn  8-)
#   fwrules.cgi
###############
# DEBUG DEBUG
#&Header::openbox('100%', 'left', 'DEBUG');
#my $debugCount = 0;
#foreach my $line (sort keys %cgiparams) {
#  print "$line = $cgiparams{$line}<br />\n";
#  $debugCount++;
#}
#print "&nbsp;Count: $debugCount\n";
#&Header::closebox();
# DEBUG DEBUG
###############


if ( $cgiparams{'ACTION'} eq 'toggle' )
{
  if ( $CONNSCHED::config[$cgiparams{'ID'}]{'ACTIVE'} eq 'on' )
  {
    $CONNSCHED::config[$cgiparams{'ID'}]{'ACTIVE'} = 'off';
  }
  else
  {
    $CONNSCHED::config[$cgiparams{'ID'}]{'ACTIVE'} = 'on';
  }
  
  &CONNSCHED::WriteConfig;
}

if ( ($cgiparams{'ACTION'} eq 'add') || ($cgiparams{'ACTION'} eq 'update') )
{
  my $l_action = $cgiparams{'ACTION_CONNECT'};
  my $l_profilenr = '';
  my $l_days = '';
  my $l_weekdays = '';

  if ( $cgiparams{'ACTION'} eq 'add' )
  {
    $i = $#CONNSCHED::config + 1;
    $CONNSCHED::config[$i]{'ACTIVE'} = 'on';
  }
  else
  {
    $i = $cgiparams{'UPDATE_ID'};
  }

  if ( $cgiparams{'ACTION_ACTION'} eq 'PROFILE')
  {
    $l_action = 'select profile';
    $l_profilenr = $cgiparams{'ACTION_PROFILENR'};
  }

  if ( $cgiparams{'ACTION_DAYSTYPE'} eq 'WEEKDAYS' )
  {
    if ( $cgiparams{'Mon'} eq 'on' ) { $l_weekdays .= 'Mon '; }
    if ( $cgiparams{'Tue'} eq 'on' ) { $l_weekdays .= 'Tue '; }
    if ( $cgiparams{'Wed'} eq 'on' ) { $l_weekdays .= 'Wed '; }
    if ( $cgiparams{'Thu'} eq 'on' ) { $l_weekdays .= 'Thu '; }
    if ( $cgiparams{'Fri'} eq 'on' ) { $l_weekdays .= 'Fri '; }
    if ( $cgiparams{'Sat'} eq 'on' ) { $l_weekdays .= 'Sat '; }
    if ( $cgiparams{'Sun'} eq 'on' ) { $l_weekdays .= 'Sun '; }
  }
  else
  {
    $l_days = "$cgiparams{'ACTION_DAYSTART'} - $cgiparams{'ACTION_DAYEND'}";
  }

  $CONNSCHED::config[$i]{'ACTION'} = $l_action;
  $CONNSCHED::config[$i]{'PROFILENR'} = $l_profilenr;
  $CONNSCHED::config[$i]{'TIME'} = "$cgiparams{'ACTION_HOUR'}:$cgiparams{'ACTION_MINUTE'}";
  $CONNSCHED::config[$i]{'DAYSTYPE'} = lc($cgiparams{'ACTION_DAYSTYPE'});
  $CONNSCHED::config[$i]{'DAYS'} = $l_days;
  $CONNSCHED::config[$i]{'WEEKDAYS'} = $l_weekdays;
  $CONNSCHED::config[$i]{'COMMENT'} = &Header::cleanhtml($cgiparams{'ACTION_COMMENT'});

  &CONNSCHED::WriteConfig;
}

if ( $cgiparams{'ACTION'} eq 'edit' )
{
  $i = $cgiparams{'ID'};
  
  $selected_hour = substr($CONNSCHED::config[$i]{'TIME'},0,2);
  $selected_minute = substr($CONNSCHED::config[$i]{'TIME'},3,2);

  if ( $CONNSCHED::config[$i]{'ACTION'} eq 'select profile' )
  {
    $checked_connect = '';
    $checked_profile = "checked='checked'";
    $selected_profile = $CONNSCHED::config[$i]{'PROFILENR'};
  }
  else
  {
    $selected{"$CONNSCHED::config[$i]{'ACTION'}"} = "selected='selected'";
  }

  if ( $CONNSCHED::config[$i]{'DAYSTYPE'} eq 'days' )
  {
    my @temp = split(/-/,$CONNSCHED::config[$i]{'DAYS'},2);

    $selected_daystart = substr($temp[0], 0, -1);
    $selected_dayend = substr($temp[1], 1);
  }
  else
  {
    my $wd = $CONNSCHED::config[$i]{'WEEKDAYS'};
    $checked_mon = '' if ( index($wd, 'Mon') == -1 ) ;
    $checked_tue = '' if ( index($wd, 'Tue') == -1 ) ;
    $checked_wed = '' if ( index($wd, 'Wed') == -1 ) ;
    $checked_thu = '' if ( index($wd, 'Thu') == -1 ) ;
    $checked_fri = '' if ( index($wd, 'Fri') == -1 ) ;
    $checked_sat = '' if ( index($wd, 'Sat') == -1 ) ;
    $checked_sun = '' if ( index($wd, 'Sun') == -1 ) ;

    $checked_days = '';
    $checked_weekdays = "checked='checked'";
  }

  $comment = $CONNSCHED::config[$cgiparams{'ID'}]{'COMMENT'};

  $buttontext = $Lang::tr{'update'};
  $hiddenvalue = 'update';
}

if ( $cgiparams{'ACTION'} eq 'remove' )
{
  # simply set ACTIVE to empty, WriteConfig will handle the gory details
  $CONNSCHED::config[$cgiparams{'ID'}]{'ACTIVE'} = '';
  &CONNSCHED::WriteConfig;
}
if ( ($cgiparams{'ACTION'} eq 'down') || ($cgiparams{'ACTION'} eq 'up') )
{
  my $action = @CONNSCHED::config[$cgiparams{'ID'}];
  my $newpos = 0;

  splice(@CONNSCHED::config, $cgiparams{'ID'}, 1);

  if ( ($cgiparams{'ACTION'} eq 'down') )
  {
    $newpos = $cgiparams{'ID'} + 1;
  }
  else
  {
    $newpos = $cgiparams{'ID'} - 1;
  }

  splice(@CONNSCHED::config, $newpos, 0, $action);

  &CONNSCHED::WriteConfig;
}


#
# Add / Edit Box
#

&Header::openbox('100%', 'left', $Lang::tr{'ConnSched add action'});

print <<END
<form method='post' name='addevent' action='$ENV{'SCRIPT_NAME'}'>
<table width='100%' border='0' cellspacing='6' cellpadding='0'>
<tr>
<td width='15%' class='base'>$Lang::tr{'ConnSched time'}&nbsp;<img src='/blob.gif' alt='*' /></td>
<td><select name='ACTION_HOUR'>
END
;
for ($hour = 0; $hour <= 23; $hour++)
{
  my $hour00 = $hour < 10 ? "0$hour" : $hour;
  if ( $hour00 eq $selected_hour )
  {
    print "<option value='$hour00' selected='selected'>$hour00</option>";
  }
  else
  {
    print "<option value='$hour00'>$hour00</option>";
  }
}
print "</select>&nbsp;:&nbsp;<select name='ACTION_MINUTE'>";
for ($minute = 0; $minute <= 55; $minute += 5)
{
  my $minute00 = $minute < 10 ? "0$minute" : $minute;
  if ( $minute00 eq $selected_minute )
  {
    print "<option value='$minute00' selected='selected'>$minute00</option>";
  }
  else
  {
    print "<option value='$minute00'>$minute00</option>";
  }
}

print <<END
</select></td></tr>
<tr><td colspan='2'><br><br></td></tr>
<tr><td width='15%' class='base'>$Lang::tr{'ConnSched action'}&nbsp;<img src='/blob.gif' alt='*' /></td><td>
<input type='radio' value='CONNECT' name='ACTION_ACTION' $checked_connect />&nbsp;<select name='ACTION_CONNECT'>
<option value='reconnect' $selected{'reconnect'}>$Lang::tr{'ConnSched reconnect'}</option>
<option value='dial' $selected{'dial'}>$Lang::tr{'ConnSched dial'}</option>
<option value='hangup' $selected{'hangup'}>$Lang::tr{'ConnSched hangup'}</option>
<option value='reboot' $selected{'reboot'}>$Lang::tr{'ConnSched reboot'}</option>
<option value='shutdown' $selected{'shutdown'}>$Lang::tr{'ConnSched shutdown'}</option>
<option value='ipsecstart' $selected{'ipsecstart'}>$Lang::tr{'ConnSched ipsecstart'}</option>
<option value='ipsecstop' $selected{'ipsecstop'}>$Lang::tr{'ConnSched ipsecstop'}</option>
</select></td></tr>
<tr><td width='15%' class='base'>&nbsp;</td>
<td><input type='radio' value='PROFILE' name='ACTION_ACTION' $checked_profile />&nbsp;$Lang::tr{'ConnSched change profile title'}&nbsp;<select name='ACTION_PROFILENR'>
END
;
for ($i = 1; $i <= $CONNSCHED::maxprofiles; $i++)
{
  if ( $i == $selected_profile )
  {
    print "<option value='$i' selected='selected'>$i. $profilenames[$i]</option>";
  }
  else
  {
    print "<option value='$i'>$i. $profilenames[$i]</option>";
  }
}
print <<END
</select></td></tr>
<tr><td colspan='2'><br><br></td></tr>
<tr><td width='15%' class='base'>$Lang::tr{'ConnSched days'}&nbsp;<img src='/blob.gif' alt='*' /></td>
<td><input type='radio' value='DAYS' name='ACTION_DAYSTYPE' $checked_days />&nbsp;<select name='ACTION_DAYSTART'>
END
;
for ($day = 1; $day <= 31; $day++)
{
  if ( $day == $selected_daystart )
  {
    print "<option value='$day' selected='selected'>$day</option>";
  }
  else
  {
    print "<option value='$day'>$day</option>";
  }
}
print "</select>&nbsp;-&nbsp;<select name='ACTION_DAYEND'>";
for ($day = 1; $day <= 31; $day++)
{
  if ( $day == $selected_dayend )
  {
    print "<option value='$day' selected='selected'>$day</option>";
  }
  else
  {
    print "<option value='$day'>$day</option>";
  }
}

print <<END
</select></td></tr>
<tr><td width='15%' class='base'>&nbsp;</td><td><input type='radio' value='WEEKDAYS' name='ACTION_DAYSTYPE' $checked_weekdays />&nbsp;$Lang::tr{'ConnSched weekdays'}<br />
&nbsp;&nbsp;<input type='checkbox' name='Mon' $checked_mon />$Lang::tr{'monday'}<br />
&nbsp;&nbsp;<input type='checkbox' name='Tue' $checked_tue />$Lang::tr{'tuesday'}<br />
&nbsp;&nbsp;<input type='checkbox' name='Wed' $checked_wed />$Lang::tr{'wednesday'}<br />
&nbsp;&nbsp;<input type='checkbox' name='Thu' $checked_thu />$Lang::tr{'thursday'}<br />
&nbsp;&nbsp;<input type='checkbox' name='Fri' $checked_fri />$Lang::tr{'friday'}<br />
&nbsp;&nbsp;<input type='checkbox' name='Sat' $checked_sat />$Lang::tr{'saturday'}<br />
&nbsp;&nbsp;<input type='checkbox' name='Sun' $checked_sun />$Lang::tr{'sunday'}
</td></tr>
<tr><td colspan='2'><br></td></tr>
<tr><td width='15%' class='base'>$Lang::tr{'remark title'}</td>
<td><input type='text' name='ACTION_COMMENT' size='40' value='$comment' /></td></tr></table>
<br>
<hr>
<table width='100%'><tr>
  <td class='base' valign='top'><img src='/blob.gif' alt='*' /></td>
  <td width='55%' class='base'>$Lang::tr{'required field'}</td>
  <td width='40%' align='right'><input type='submit' name='SUBMIT' value='$buttontext' />
  <input type='hidden' name='ACTION' value='$hiddenvalue' /></td>
  <input type='hidden' name='UPDATE_ID' value='$cgiparams{'ID'}' /></td>
</tr></table>
</form>

END
;

&Header::closebox();

#
# Box with List of events
#

&Header::openbox('100%', 'left', $Lang::tr{'ConnSched scheduled actions'});
print <<END
<table width='100%' cellspacing='1' cellpadding='0' class='tbl'>
<tr>
<th align='center' width='10%'><b>$Lang::tr{'time'}</b></th>
<th width='15%'>&nbsp;</th>
<th align='center' width='60%'><b>$Lang::tr{'remark'}</b></th>
<th align='center' colspan='5' width='5%'><b>$Lang::tr{'action'}</b></th>
</tr>
END
;
my $col="";
for my $id ( 0 .. $#CONNSCHED::config )
{
  if ( ($cgiparams{'ACTION'} eq 'edit') && ($id == $cgiparams{'ID'}) ) 
  {
    print "<tr>";
    $col="bgcolor='${Header::colouryellow}'";
  }
  elsif ( $id % 2 )
  {
    print "<tr>";
    $col="bgcolor='$color{'color20'}'";
  }
  else 
  {
    print "<tr>";
    $col="bgcolor='$color{'color22'}'";
  }

print <<END
<td align='center' $col>$CONNSCHED::config[$id]{'TIME'}</td>
<td $col>$Lang::tr{"ConnSched $CONNSCHED::config[$id]{'ACTION'}"}&nbsp;$CONNSCHED::config[$id]{'PROFILENR'}</td>
<td $col>$CONNSCHED::config[$id]{'COMMENT'}</td>
<td align='center' $col>
  <form method='post' name='frm$id' action='$ENV{'SCRIPT_NAME'}'>
  <input type='hidden' name='ACTION' value='toggle' />
  <input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$CONNSCHED::config[$id]{'ACTIVE'}.gif' alt='$Lang::tr{'toggle enable disable'}' title='$Lang::tr{'toggle enable disable'}' />
  <input type='hidden' name='ID' value='$id' />
  </form>
</td>
<td align='center' $col>
  <form method='post' name='frm$id' action='$ENV{'SCRIPT_NAME'}'>
  <input type='hidden' name='ACTION' value='edit' />
  <input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' />
  <input type='hidden' name='ID' value='$id' />
  </form>
</td>
<td align='center' $col>
  <form method='post' name='frm$id' action='$ENV{'SCRIPT_NAME'}'>
  <input type='hidden' name='ACTION' value='remove' />
  <input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' alt='$Lang::tr{'remove'}' title='$Lang::tr{'remove'}' />
  <input type='hidden' name='ID' value='$id' />
  </form>
</td>
<td align='center' $col>
  <form method='post' name='frm$id' action='$ENV{'SCRIPT_NAME'}'>
  <input type='hidden' name='ACTION' value='up' />
  <input type='image' name='$Lang::tr{'ConnSched up'}' src='/images/up.gif' alt='$Lang::tr{'ConnSched up'}' title='$Lang::tr{'ConnSched up'}' />
  <input type='hidden' name='ID' value='$id' />
  </form>
</td>
<td align='center' $col>
  <form method='post' name='frm$id' action='$ENV{'SCRIPT_NAME'}'>
  <input type='hidden' name='ACTION' value='down' />
  <input type='image' name='$Lang::tr{'ConnSched down'}' src='/images/down.gif' alt='$Lang::tr{'ConnSched down'}' title='$Lang::tr{'ConnSched down'}' />
  <input type='hidden' name='ID' value='$id' />
  </form>
</td>
</tr>
<tr>
<td $col>&nbsp;</td>
<td colspan='7' $col>$CONNSCHED::config[$id]{'DAYS'}$CONNSCHED::config[$id]{'WEEKDAYS_PR'}&nbsp;</td>
</tr>
END
;
}

print <<END
</table>
<br />
<hr />
END
;


&Header::closebox();

&Header::closebigbox();
&Header::closepage();
