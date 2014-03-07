#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2012  IPFire Team  <info@ipfire.org>                     #
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
require "/opt/pakfire/lib/functions.pl";

# If the license has already been accepted.
if ( -e "/var/ipfire/main/gpl_accepted" ) {
	&redirect();
}

my %cgiparams;
$cgiparams{'ACTION'} = '';

&Header::getcgihash(\%cgiparams);

# Check if the license agreement has been accepted.
if ($cgiparams{'ACTION'} eq "$Lang::tr{'yes'}" && $cgiparams{'gpl_accepted'} eq '1') {
	open(FILE, ">/var/ipfire/main/gpl_accepted");
	close(FILE);

	&redirect();
}

&Header::showhttpheaders();

&Header::openpage($Lang::tr{'main page'}, 1);
&Header::openbigbox('', 'center');

&Header::openbox('100%', 'left', $Lang::tr{'gpl license agreement'});
print <<END;
	$Lang::tr{'gpl please read carefully the general public license and accept it below'}.
	<br /><br />
END
;	
if ( -e "/usr/share/doc/licenses/GPLv3" ) {
	print '<textarea rows=\'25\' cols=\'75\' readonly=\'readonly\'>';
	print `cat /usr/share/doc/licenses/GPLv3`;
	print '</textarea>';
}
else {
	print '<br /><a href=\'http://www.gnu.org/licenses/gpl-3.0.txt\' target=\'_blank\'>GNU GENERAL PUBLIC LICENSE</a><br />';
}
print <<END;
	<p>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='checkbox' name='gpl_accepted' value='1'/> $Lang::tr{'gpl i accept these terms and conditions'}.
			<br/ >
			<input type='submit' name='ACTION' value=$Lang::tr{'yes'} />
		</form>
	</p>
	<a href='http://www.gnu.org/licenses/translations.html' target='_blank'>$Lang::tr{'gpl unofficial translation of the general public license v3'}</a>

END

&Header::closebox();
&Header::closebigbox();
&Header::closepage();

sub redirect {
	print "Status: 302 Moved Temporarily\n";
	print "Location: index.cgi\n\n";
	exit (0);
}
