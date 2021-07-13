#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2021  IPFire Development Team                                 #
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

###--- HTML HEAD ---###
my $extraHead = <<END
<style>
	table#controls {
		width: 100%;
		border: none;
		table-layout: fixed;
	}
	#controls td {
		text-align: center;
	}
	#controls button {
		font-weight: bold;
		padding: 0.7em;
		min-width: 65%;
	}
</style>
END
;
###--- END HTML HEAD ---###

my %cgiparams=();
my $death = 0;
my $rebirth = 0;

&Header::showhttpheaders();

$cgiparams{'ACTION'} = '';
&Header::getcgihash(\%cgiparams);

if ($cgiparams{'ACTION'} eq "SHUTDOWN") {
	$death = 1;
	&General::log($Lang::tr{'shutting down ipfire'});
	&General::system('/usr/local/bin/ipfirereboot', 'down');
} elsif ($cgiparams{'ACTION'} eq "REBOOT") {
	$rebirth = 1;
	&General::log($Lang::tr{'rebooting ipfire'});
	&General::system('/usr/local/bin/ipfirereboot', 'boot');
} elsif ($cgiparams{'ACTION'} eq "REBOOT_FSCK") {
	$rebirth = 1;
	&General::log($Lang::tr{'rebooting ipfire fsck'});
	&General::system('/usr/local/bin/ipfirereboot', 'bootfs');
}

if ($death == 0 && $rebirth == 0) {

	&Header::openpage($Lang::tr{'shutdown control'}, 1, $extraHead);

	&Header::openbigbox('100%', 'left');
	&Header::openbox('100%', 'left');

	print <<END
<form method="post" action="$ENV{'SCRIPT_NAME'}">
	<table id="controls">
	<tr>
		<td><button type="submit" name="ACTION" value="SHUTDOWN">$Lang::tr{'shutdown'}</button></td>
		<td><button type="submit" name="ACTION" value="REBOOT">$Lang::tr{'reboot'}</button></td>
		<td><button type="submit" name="ACTION" value="REBOOT_FSCK">$Lang::tr{'reboot fsck'}</button></td>
	</tr>
	</table>
</form>
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

