#!/usr/bin/perl
#
# This code is distributed under the terms of the GPL
#
# Copyright (c) 2005 Achim Weber
#
# $Id: trafficadm.cgi,v 1.21 2006/12/31 14:33:18 dotzball Exp $
#

use strict;

# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "${General::swroot}/net-traffic/net-traffic-admin.pl";

my %cgiparams;
my $errormessage = '';
my $infomessage = '';
my $saveerror = 0;
my @days = ( 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31 );
my @warnLevels = ( 50,60,70,80,90,100 );

my @dummy = ($NETTRAFF::settingsfile, ${Header::colourred});
undef(@dummy);

&Header::showhttpheaders();

# Init parameters
$cgiparams{'MONTHLY_VOLUME_ON'} = 'off';
$cgiparams{'MONTHLY_VOLUME'} = '';
$cgiparams{'STARTDAY'} = '1';
$cgiparams{'WARN_ON'} = 'off';
$cgiparams{'WARN'} = '80';
$cgiparams{'CALC_INTERVAL'} = '60';
$cgiparams{'SHOW_AT_HOME'} = 'off';
$cgiparams{'SEND_EMAIL_ON'} = 'off';
$cgiparams{'EMAIL_TO'} = '';
$cgiparams{'EMAIL_FROM'} = '';
$cgiparams{'EMAIL_USR'} = '';
$cgiparams{'EMAIL_PW'} = '';
$cgiparams{'EMAIL_SERVER'} = '';
$cgiparams{'VERSION_CHECK_ON'} = 'off';


&Header::getcgihash(\%cgiparams);

if ($cgiparams{'ACTION'} eq $Lang::tr{'save'})
{
	&validSave();

	if ($errormessage) {
		$saveerror = 1;
	}
	else	{ # no error, all right, save new settings
		&General::writehash($NETTRAFF::settingsfile, \%cgiparams);
		# calculate traffic
		`/usr/local/bin/monitorTraff --force < /dev/null > /dev/null 2>&1 &`;
	}
} # end if ($cgiparams{'ACTION'} eq $Lang::tr{'save'})


# if user want to save settings and get a errormessage, we don´t
# overwrite users input
unless ($saveerror) {

	&NETTRAFF::readSettings();

 	$cgiparams{'MONTHLY_VOLUME_ON'} = $NETTRAFF::settings{'MONTHLY_VOLUME_ON'};
 	$cgiparams{'MONTHLY_VOLUME'} = $NETTRAFF::settings{'MONTHLY_VOLUME'};
 	$cgiparams{'STARTDAY'} = $NETTRAFF::settings{'STARTDAY'};
 	$cgiparams{'WARN_ON'} = $NETTRAFF::settings{'WARN_ON'};
 	$cgiparams{'WARN'} = $NETTRAFF::settings{'WARN'};
 	$cgiparams{'CALC_INTERVAL'} = $NETTRAFF::settings{'CALC_INTERVAL'};
 	$cgiparams{'SHOW_AT_HOME'} = $NETTRAFF::settings{'SHOW_AT_HOME'};
 	$cgiparams{'SEND_EMAIL_ON'} = $NETTRAFF::settings{'SEND_EMAIL_ON'};
 	$cgiparams{'EMAIL_TO'} = $NETTRAFF::settings{'EMAIL_TO'};
 	$cgiparams{'EMAIL_FROM'} = $NETTRAFF::settings{'EMAIL_FROM'};
 	$cgiparams{'EMAIL_USR'} = $NETTRAFF::settings{'EMAIL_USR'};
 	$cgiparams{'EMAIL_PW'} = $NETTRAFF::settings{'EMAIL_PW'};
 	$cgiparams{'EMAIL_SERVER'} = $NETTRAFF::settings{'EMAIL_SERVER'};
 	$cgiparams{'VERSION_CHECK_ON'} = $NETTRAFF::settings{'VERSION_CHECK_ON'};

} # end unless ($saveerror)


if ($cgiparams{'ACTION'} eq $Lang::tr{'send test mail'})
{
	# send test email
	my $return = `/usr/local/bin/monitorTraff --testEmail`;
	
	if($return =~ /Email was sent successfully!/)
	{
		$infomessage = "$Lang::tr{'test email was sent'}<br/>";
	}
	else
	{
		$errormessage = "$Lang::tr{'test email could not be sent'}:<br/>";
		$errormessage .= "$return <br />";
	}


} # end if ($cgiparams{'ACTION'} eq $Lang::tr{'send test mail'})



my %selected;
$selected{'CALC_INTERVAL'}{'5'} = '';
$selected{'CALC_INTERVAL'}{'10'} = '';
$selected{'CALC_INTERVAL'}{'15'} = '';
$selected{'CALC_INTERVAL'}{'30'} = '';
$selected{'CALC_INTERVAL'}{'60'} = '';
$selected{'CALC_INTERVAL'}{$cgiparams{'CALC_INTERVAL'}} = "selected='selected'";

my %checked;
$checked{'MONTHLY_VOLUME_ON'}{'off'} = '';
$checked{'MONTHLY_VOLUME_ON'}{'on'} = '';
$checked{'MONTHLY_VOLUME_ON'}{$cgiparams{'MONTHLY_VOLUME_ON'}} = "checked='checked'";

$checked{'WARN_ON'}{'off'} = '';
$checked{'WARN_ON'}{'on'} = '';
$checked{'WARN_ON'}{$cgiparams{'WARN_ON'}} = "checked='checked'";

$checked{'SHOW_AT_HOME'}{'off'} = '';
$checked{'SHOW_AT_HOME'}{'on'} = '';
$checked{'SHOW_AT_HOME'}{$cgiparams{'SHOW_AT_HOME'}} = "checked='checked'" ;

$checked{'SEND_EMAIL_ON'}{'off'} = '';
$checked{'SEND_EMAIL_ON'}{'on'} = '';
$checked{'SEND_EMAIL_ON'}{$cgiparams{'SEND_EMAIL_ON'}} = "checked='checked'" ;

$checked{'VERSION_CHECK_ON'}{'off'} = '';
$checked{'VERSION_CHECK_ON'}{'on'} = '';
$checked{'VERSION_CHECK_ON'}{$cgiparams{'VERSION_CHECK_ON'}} = "checked='checked'" ;


my $btnTestmailDisabled = "";
$btnTestmailDisabled = "disabled='disabled'" if($cgiparams{'SEND_EMAIL_ON'} ne 'on');

&Header::openpage($Lang::tr{'traffic monitor'}, 1, '');
&Header::openbigbox('100%', 'left');

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<class name='base'><font color='${Header::colourred}'>$errormessage\n</font>";
	print "&nbsp;</class>\n";
	&Header::closebox();
}

if($infomessage) {
	&Header::openbox('100%', 'left', "$Lang::tr{'traffic info messages'}:");
	print "<class name='base'>$infomessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
}

&Header::openbox('100%', 'left', "$Lang::tr{'net-traffic configuration'}:");

print <<END;
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table width='100%'>
	<tr>
		<td align='left' class='base' width='1%'>
			<input type="checkbox" name="SHOW_AT_HOME" $checked{'SHOW_AT_HOME'}{'on'} />&nbsp;
		</td>
		<td align='left' class='base' nowrap='nowrap' colspan="3">
			$Lang::tr{'display traffic at home'}
		</td>
	</tr>
	<tr>
		<td align='left' class='base'>
			<input type="checkbox" name="MONTHLY_VOLUME_ON" $checked{'MONTHLY_VOLUME_ON'}{'on'} />&nbsp;
		</td>
		<td align='left' class='base' nowrap='nowrap' colspan="2">
			$Lang::tr{'monthly volume'} (MByte): &nbsp;
		</td>
		<td align='left' class='base' >
			<input type='text' name='MONTHLY_VOLUME' value='$cgiparams{'MONTHLY_VOLUME'}' size='20' maxlength='17' />
		</td>
	</tr>
	<tr>
		<td align='left' class='base'  colspan="2"></td>
		<td align='left' class='base' nowrap='nowrap' >
			$Lang::tr{'monthly volume start day'}: &nbsp;
		</td>
		<td align='left' class='base' >
			<select name='STARTDAY'>
END

foreach my $day (@days)
{
	print "				<option ";
	if ($day == $cgiparams{'STARTDAY'}) {
		print 'selected=\'selected\' '; }
	print "value='$day'>$day</option>\n";
}
print <<END;
			</select>
		</td>
	</tr>
	<tr>
		<td align='left' class='base' width='1%'></td>
		<td align='left' class='base' width='1%'>
			<input type="checkbox" name="WARN_ON" $checked{'WARN_ON'}{'on'} />&nbsp;
		</td>
		<td align='left' class='base' width='20%' nowrap='nowrap'>
			$Lang::tr{'warn when traffic reaches'}: &nbsp;
		</td>
		<td align='left' class='base' width='78%'>
			<select name='WARN'>
END

foreach my $level (@warnLevels)
{
	print "				<option ";
	if ($level == $cgiparams{'WARN'}) {
		print 'selected=\'selected\' '; }
	print "value='$level'>$level</option>\n";
}
print <<END;
			</select>
		</td>
	</tr>
	<tr>
		<td align='left' class='base' colspan="2"></td>
		<td align='left' class='base' nowrap='nowrap' >
			$Lang::tr{'calc traffic all x minutes'}: &nbsp;
		</td>
		<td align='left' class='base' >
			<select name='CALC_INTERVAL'>
				<option value='5'   $selected{'CALC_INTERVAL'}{'5'} > 5</option>
				<option value='10'  $selected{'CALC_INTERVAL'}{'10'}>10</option>
				<option value='15'  $selected{'CALC_INTERVAL'}{'15'}>15</option>
				<option value='30'  $selected{'CALC_INTERVAL'}{'30'}>30</option>
				<option value='60'  $selected{'CALC_INTERVAL'}{'60'}>60</option>
			</select>
		</td>
	</tr>
	<tr>
		<td align='left' class='base'> </td>
		<td align='left' class='base'>
			<input type="checkbox" name="SEND_EMAIL_ON" $checked{'SEND_EMAIL_ON'}{'on'} />&nbsp;
		</td>
		<td align='left' class='base' colspan="2" nowrap='nowrap' >
			$Lang::tr{'send email notification'}:
		</td>
	</tr>
	<tr>
		<td align='left' class='base' colspan="2"> </td>
		<td align='left' class='base' nowrap='nowrap'>
			$Lang::tr{'to email adr'}: &nbsp;
		</td>
		<td align='left' class='base' >
			<input type='text' name='EMAIL_TO' value='$cgiparams{'EMAIL_TO'}' size='25' />&nbsp;
		</td>
	</tr>
	<tr>
		<td align='left' class='base' colspan="2"> </td>
		<td align='left' class='base' nowrap='nowrap'>
			$Lang::tr{'from email adr'}: &nbsp;
		</td>
		<td align='left' class='base' >
			<input type='text' name='EMAIL_FROM' value='$cgiparams{'EMAIL_FROM'}' size='25' />&nbsp;
		</td>
	</tr>
	<tr>
		<td align='left' class='base' colspan="2"> </td>
		<td align='left' class='base' nowrap='nowrap'>
			$Lang::tr{'from email user'}: &nbsp;
		</td>
		<td align='left' class='base' >
			<input type='text' name='EMAIL_USR' value='$cgiparams{'EMAIL_USR'}' size='25' />
			&nbsp; <img src='/blob.gif' alt='*' />
		</td>
	</tr>
	<tr>
		<td align='left' class='base' colspan="2"> </td>
		<td align='left' class='base' nowrap='nowrap'>
			$Lang::tr{'from email pw'}: &nbsp;
		</td>
		<td align='left' class='base' >
			<input type='password' name='EMAIL_PW' value='$cgiparams{'EMAIL_PW'}' size='25' />
			&nbsp; <img src='/blob.gif' alt='*' />
		</td>
	</tr>
	<tr>
		<td align='left' class='base' colspan="2"> </td>
		<td align='left' class='base' nowrap='nowrap'>
			$Lang::tr{'from email server'}: &nbsp;
		</td>
		<td align='left' class='base' >
			<input type='text' name='EMAIL_SERVER' value='$cgiparams{'EMAIL_SERVER'}' size='25' />&nbsp;
		</td>
	</tr>
	<tr>
		<td align='left' class='base' colspan="2"> </td>
		<td align='left' class='base' colspan="2">
			<input type='submit' name='ACTION' value='$Lang::tr{'send test mail'}' $btnTestmailDisabled />
		</td>
	</tr>
	</table>
	<hr />
	<table width='100%'>
	<tr>
		<td align='left' class='base' nowrap='nowrap' width='2%'>
			<img src='/blob.gif' alt ='*' align='top' /> &nbsp;
			<font class='base'>$Lang::tr{'this field may be blank'}</font> &nbsp;
		</td>
		<td align='center' class='base' width='48%'>
			 &nbsp; <input type='submit' name='ACTION' value='$Lang::tr{'save'}' /> &nbsp;
END

	# if user input cause an error
	# and user want a reset, we re-read settings from settingsfile
	if ($errormessage ne '') {
		print "<input type='submit' name='ACTION' value='$Lang::tr{'reset'}' />";
	}
	else {
		print "<input type='reset' name='ACTION' value='$Lang::tr{'reset'}' />";
	}

print <<END;
		</td>
		<td align='left' class='base' nowrap='nowrap' width='50%'> </td>
	</tr>
	</table>
	</form>
	<hr />
	<table width='100%'>
	<tr>
		<td align='left' class='base' width='2%'>
			&nbsp;
		</td>
		<td align='left' class='base' width='98%'>
			<form method='post' action='/cgi-bin/traffic.cgi'>
				<input type='submit' name='ACTION' value='$Lang::tr{'traffic back'}' />
			</form>
		</td>
	</tr>
	</table>
END

&Header::closebox();
&Header::closebigbox();
&Header::closepage();


sub validSave
{
	if ($cgiparams{'SHOW_AT_HOME'} ne 'on' ) {
		$cgiparams{'SHOW_AT_HOME'} = 'off';
	}

	if ($cgiparams{'MONTHLY_VOLUME_ON'} ne 'on' ) {
		$cgiparams{'MONTHLY_VOLUME_ON'} = 'off';
	}

	if($cgiparams{'MONTHLY_VOLUME_ON'} eq 'on')
	{
		if($cgiparams{'MONTHLY_VOLUME'} !~ /^\d+$/ || $cgiparams{'MONTHLY_VOLUME'} < 1) {
			$errormessage .= "$Lang::tr{'monthly traffic bad'}<br/>";
		}

		if($cgiparams{'STARTDAY'} < 1 || 31 < $cgiparams{'STARTDAY'}) {
			$errormessage .= "$Lang::tr{'monthly start day bad'}<br/>";
		}

		if ($cgiparams{'WARN_ON'} ne 'on' ) {
			$cgiparams{'WARN_ON'} = 'off';
		}

		if($cgiparams{'WARN_ON'} eq 'on' && $cgiparams{'WARN'} !~ /^\d+$/) {
			$errormessage .= "$Lang::tr{'traffic warn level bad'}<br/>";
		}

		if($cgiparams{'CALC_INTERVAL'} < 5 || 60 < $cgiparams{'CALC_INTERVAL'}) {
			$errormessage .= "$Lang::tr{'traffic calc time bad'}<br/>";
		}

		if ($cgiparams{'SEND_EMAIL_ON'} ne 'on' ) {
			$cgiparams{'SEND_EMAIL_ON'} = 'off';
		}

		if($cgiparams{'SEND_EMAIL_ON'} eq 'on' )
		{
			if($cgiparams{'EMAIL_TO'} eq '' || (! &General::validemail($cgiparams{'EMAIL_TO'})) ) {
				$errormessage .= "$Lang::tr{'to warn email bad'}<br/>";
			}

			if($cgiparams{'EMAIL_FROM'} eq '' || (! &General::validemail($cgiparams{'EMAIL_FROM'}))) {
				$errormessage .= "$Lang::tr{'from warn email bad'}<br/>";
			}

			if($cgiparams{'EMAIL_SERVER'} eq '') {
				$errormessage .= "$Lang::tr{'email server can not be empty'}<br/>";
			}
		}
	} # monthly volumne == on

	if ($cgiparams{'VERSION_CHECK_ON'} ne 'on' ) {
		$cgiparams{'VERSION_CHECK_ON'} = 'off';
	}
}
