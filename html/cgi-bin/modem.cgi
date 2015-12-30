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

my %modemsettings=();
my $errormessage = '';

&Header::showhttpheaders();

$modemsettings{'ACTION'} = '';
$modemsettings{'VALID'} = '';

&Header::getcgihash(\%modemsettings);

if ($modemsettings{'ACTION'} eq $Lang::tr{'save'})
{ 
        if (!($modemsettings{'TIMEOUT'} =~ /^\d+$/))
        {
      	 	$errormessage = $Lang::tr{'timeout must be a number'};
	 	goto ERROR;
        }
ERROR:   
        if ($errormessage) {
                $modemsettings{'VALID'} = 'no'; }
        else {
                $modemsettings{'VALID'} = 'yes'; }

	&General::writehash("${General::swroot}/modem/settings", \%modemsettings);
}

if ($modemsettings{'ACTION'} eq $Lang::tr{'restore defaults'})
{
	system('/bin/cp', "${General::swroot}/modem/defaults", "${General::swroot}/modem/settings", '-f');
}

&General::readhash("${General::swroot}/modem/settings", \%modemsettings);

&Header::openpage($Lang::tr{'modem configuration'}, 1, '');

&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<font class='base'>$errormessage&nbsp;</font>\n";
	&Header::closebox();
}

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

&Header::openbox('100%', 'left', "$Lang::tr{'modem configuration'}:");
print <<END
<table width='100%'>
<tr>
	<td width='25%' class='base'>$Lang::tr{'init string'}</td>
	<td width='25%'><input type='text' name='INIT' value='$modemsettings{'INIT'}' /></td>
	<td width='25%' class='base'>$Lang::tr{'hangup string'}</td>
	<td width='25%'><input type='text' name='HANGUP' value='$modemsettings{'HANGUP'}' /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'speaker on'}</td>
	<td><input type='text' name='SPEAKER_ON' value='$modemsettings{'SPEAKER_ON'}' /></td>
	<td class='base'>$Lang::tr{'speaker off'}</td>
	<td><input type='text' name='SPEAKER_OFF' value='$modemsettings{'SPEAKER_OFF'}' /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'tone dial'}</td>
	<td><input type='text' name='TONE_DIAL' value='$modemsettings{'TONE_DIAL'}' /></td>
	<td class='base'>$Lang::tr{'pulse dial'}</td>
	<td><input type='text' name='PULSE_DIAL' value='$modemsettings{'PULSE_DIAL'}' /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'connect timeout'}&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td><input type='text' name='TIMEOUT' value='$modemsettings{'TIMEOUT'}' /></td>
	<td class='base'>&nbsp;</td>
	<td>&nbsp;</td>
</tr>

</table>
<table width='100%'>
<hr />
<tr>
	<td width='33%'>
		<img src='/blob.gif' align='top' alt='*' />&nbsp;<font class='base'>$Lang::tr{'required field'}</font>
	</td>
	<td width='33%' align='center'>
		<input type='submit' name='ACTION' value='$Lang::tr{'restore defaults'}' />
	</td>
	<td width='33%' align='center'>
		<input type='submit' name='ACTION' value='$Lang::tr{'save'}' />
	</td>
</tr>
</table>
</div>
END
;
&Header::closebox();

print "</form>\n";

&Header::closebigbox();

&Header::closepage();
