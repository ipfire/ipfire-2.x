#!/usr/bin/perl
#
# IPFire CGIs
#
# This file is part of the IPFire Project
# 
# This code is distributed under the terms of the GPL
#
# (c) Eric Oberlander June 2002
#
# (c) Darren Critchley June 2003 - added real time clock setting, etc
#

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require 'CONFIG_ROOT/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %pakfiresettings=();
my $errormessage = '';

&Header::showhttpheaders();

$pakfiresettings{'ACTION'} = '';
$pakfiresettings{'VALID'} = '';

$pakfiresettings{'INSTALLED'} = '';
$pakfiresettings{'AVAIL'} = '';
$pakfiresettings{'AUTOUPD'} = '';

&Header::getcgihash(\%pakfiresettings);

if ($pakfiresettings{'ACTION'} eq $Lang::tr{'save'})
{

}

&General::readhash("${General::swroot}/pakfire/settings", \%pakfiresettings);


my %selected=();
my %checked=();

$checked{'AUTOUPD'}{'off'} = '';
$checked{'AUTOUPD'}{'on'} = '';
$checked{'AUTOUPD'}{$pakfiresettings{'AUTOUPD'}} = "checked='checked'";

&Header::openpage($Lang::tr{'pakfire configuration'}, 1, $refresh);

&Header::openbigbox('100%', 'left', '', $errormessage);

# DPC move error message to top so it is seen!
if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<font class='base'>$errormessage&nbsp;</font>\n";
	&Header::closebox();
	}

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

&Header::openbox('100%', 'left', $Lang::tr{'network pakfire'});
print <<END
<table width='100%'>
<tr>
	<td><input type='checkbox' name='ENABLENTP' $checked{'ENABLENTP'}{'on'} /></td>
	<td width='100%' colspan='4' class='base'>$Lang::tr{'network pakfire from'}</td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td width='100%' class='base' colspan='4'>
END
;


print <<END
</table>
<br />
<hr />
<table width='100%'>
<tr>
	<td width='30%'><img src='/blob.gif' alt='*' /> $Lang::tr{'this field may be blank'}</td>
	<td width='33%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
	<td width='33%' align='right'>
		<a href='${General::adminmanualurl}/services.html#services_pakfire' target='_blank'><img src='/images/web-support.png' title='$Lang::tr{'online help en'}' /></a>
	</td>
</tr>
</table>
END
;

&Header::closebox();

print "</form>\n";

&Header::closebigbox();

&Header::closepage();

