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

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %cgiparams=();
my $death = 0;
my $rebirth = 0;

&Header::showhttpheaders();

$cgiparams{'ACTION'} = '';
&Header::getcgihash(\%cgiparams);

if ($cgiparams{'ACTION'} eq $Lang::tr{'shutdown'}) {
	$death = 1;
	&General::log($Lang::tr{'shutting down ipfire'});
	system '/usr/local/bin/ipfirereboot down';
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'reboot'}) {
	$rebirth = 1;
	&General::log($Lang::tr{'rebooting ipfire'});
	system '/usr/local/bin/ipfirereboot boot';
}
if ($death == 0 && $rebirth == 0) {

	&Header::openpage($Lang::tr{'shutdown control'}, 1, '');

	&Header::openbigbox('100%', 'left');

	print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

	&Header::openbox('100%', 'left', );
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
<br /><br /><img src='/images/IPFire.png' /><br /><br /><br />
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

