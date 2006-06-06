#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# $Id: changepw.cgi,v 1.4.2.6 2005/03/07 21:28:03 eoberlander Exp $
#

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %cgiparams=();
my $errormessage='';

&Header::showhttpheaders();

$cgiparams{'ACTION_ADMIN'} = '';
$cgiparams{'ACTION_DIAL'} = '';

&Header::getcgihash(\%cgiparams);

if ($cgiparams{'ACTION_ADMIN'} eq $Lang::tr{'save'})
{
	my $password1 = $cgiparams{'ADMIN_PASSWORD1'};
	my $password2 = $cgiparams{'ADMIN_PASSWORD2'};	
	if ($password1 eq $password2)
	{
		if ($password1 =~ m/\s|\"/) {
			$errormessage = $Lang::tr{'password contains illegal characters'};
		}
		elsif (length($password1) >= 6)
		{
			system('/usr/bin/htpasswd', '-m', '-b', "${General::swroot}/auth/users", 'admin', "${password1}");
			&General::log($Lang::tr{'admin user password has been changed'});
		}
		else {
			$errormessage = $Lang::tr{'passwords must be at least 6 characters in length'}; }
	}
	else {
		$errormessage = $Lang::tr{'passwords do not match'}; }
}

if ($cgiparams{'ACTION_DIAL'} eq $Lang::tr{'save'})
{
	my $password1 = $cgiparams{'DIAL_PASSWORD1'};
	my $password2 = $cgiparams{'DIAL_PASSWORD2'};	
	if ($password1 eq $password2)
	{
		if($password1 =~ m/\s|\"/) {
			$errormessage = $Lang::tr{'password contains illegal characters'};
                }
		elsif (length($password1) >= 6)
		{
			system('/usr/bin/htpasswd', '-b', "${General::swroot}/auth/users", 'dial', "${password1}"); 
			&General::log($Lang::tr{'dial user password has been changed'});
		}
		else {
			$errormessage = $Lang::tr{'passwords must be at least 6 characters in length'}; }
	}
	else {
		$errormessage = $Lang::tr{'passwords do not match'}; }
}

&Header::openpage($Lang::tr{'change passwords'}, 1, '');

&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
}

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

&Header::openbox('100%', 'left', $Lang::tr{'administrator user password'});
print <<END
<table width='100%'>
<tr>
	<td width='20%' class='base'>$Lang::tr{'username'}&nbsp;'admin'</td>
	<td width='15%' class='base' align='right'>$Lang::tr{'password'}&nbsp;</td>
	<td width='15%'><input type='password' name='ADMIN_PASSWORD1' size='10' /></td>
	<td width='15%' class='base' align='right'>$Lang::tr{'again'} </td>
	<td width='15%'><input type='password' name='ADMIN_PASSWORD2' size='10' /></td>
	<td width='20%' align='center'><input type='submit' name='ACTION_ADMIN' value='$Lang::tr{'save'}' /></td>
</tr>
</table>
END
;
&Header::closebox();

&Header::openbox('100%', 'left', $Lang::tr{'dial user password'});
print <<END
<table width='100%'>
<tr>
	<td width='20%' class='base'>$Lang::tr{'username'}&nbsp;'dial'</td>
	<td width='15%' class='base' align='right'>$Lang::tr{'password'}&nbsp;</td>
	<td width='15%'><input type='password' name='DIAL_PASSWORD1' size='10'/></td>
	<td width='15%' class='base' align='right'>$Lang::tr{'again'}&nbsp;</td>
	<td width='15%'><input type='password' name='DIAL_PASSWORD2' size='10' /></td>
	<td width='20%' align='center'><input type='submit' name='ACTION_DIAL' value='$Lang::tr{'save'}' /></td>
</tr>
</table>
END
;
&Header::closebox();

print "</form>\n";

&Header::closebigbox();

&Header::closepage();
