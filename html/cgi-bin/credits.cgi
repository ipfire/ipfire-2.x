#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2011  IPFire Team  <info@ipfire.org>                          #
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

&Header::showhttpheaders();

&Header::openpage($Lang::tr{'credits'}, 1, '');

&Header::openbigbox('100%', 'center');

&Header::openbox('100%', 'left', $Lang::tr{'donation'});

print <<END
<p>$Lang::tr{'donation-text'}</p>
	<div align="center">
		<form action="https://www.paypal.com/cgi-bin/webscr" method="post">
			<input type="hidden" name="cmd" value="_s-xclick">
			<input type="hidden" name="hosted_button_id" value="HHBTSN9QRWPAY">
			<input type="image" src="$Lang::tr{'donation-link'}" border="0" name="submit" alt="PayPal - The safer, easier way to pay online!">
			<img alt="" border="0" src="https://www.paypalobjects.com/de_DE/i/scr/pixel.gif" width="1" height="1">
		</form>
	</div>
<br />

END
;
&Header::closebox();

&Header::openbox('100%', 'left', $Lang::tr{'credits'});

print <<END
<br /><center><b><a href='http://www.ipfire.org/' target="_blank">http://www.ipfire.org/</a></b></center>
<br />
<p>
	<b>IPFire is based on IPCop and Smoothwall. Many thanks to its developers.</b><br />
	<b>We want to say thank you to all of the developers who ever contributed anything to IPFire.</b>
</p>

<p><b>Development:</b><br />

Arne Fitzenreiter
(<a href='mailto:arne.fitzenreiter\@ipfire.org'>arne.fitzenreiter\@ipfire.org</a>)  - Maintainer IPFire 2.x <br />
Michael Tremer
(<a href='mailto:michael.tremer\@ipfire.org'>michael.tremer\@ipfire.org</a>) - Project Leader <br />
Christian Schmidt
(<a href='mailto:christian.schmidt\@ipfire.org'>christian.schmidt\@ipfire.org</a>) - Vice Project Leader <br />
Stefan Schantl
(<a href='mailto:stefan.schantl\@ipfire.org'>stefan.schantl\@ipfire.org</a>)<br />
Jan Paul T&uuml;cking
(<a href='mailto:jan.tuecking\@ipfire.org'>jan.tuecking\@ipfire.org</a>)<br />
Heiner Schmeling
(<a href='mailto:heiner.schmeling\@ipfire.org'>heiner.schmeling\@ipfire.org</a>)<br />
Ronald Wiesinger
(<a href='mailto:ronald.wiesinger\@ipfire.org'>ronald.wiesinger\@ipfire.org</a>)<br />
Silvio Rechenbach
(<a href='mailto:silvio.rechenbach\@ipfire.org'>silvio.rechenbach\@ipfire.org</a>)<br />
Dirk Wagner
(<a href='mailto:dirk.wagner\@ipfire.org'>dirk.wagner\@ipfire.org</a>)<br />
Erik Kapfer
(<a href='mailto:erik.kapfer\@ipfire.org'>erik.kapfer\@ipfire.org</a>)<br />
Alfred Haas
(<a href='mailto:alfred.haas\@ipfire.org'>alfred.haas\@ipfire.org</a>)<br />

<p><b>Inactive:</b><br />

Peter Pfeiffer
(<a href='mailto:peter.pfeifer\@ipfire.org'>peter.pfeifer\@ipfire.org</a>)<br />
Peter Sch&auml;lchli
(<a href='mailto:peter.schaelchli\@ipfire.org'>peter.schaelchli\@ipfire.org</a>)<br />
</p>
<p>Some parts of the distribution are left ajar on third-party software, that is licensed under the GPL, too.<br />
There are: Advanced Proxy with URL-Filter and Update-Accelerator, ZERINA, Connection Scheduler, Hddtemp and Wake-on-LAN.<br />
Distributed by Marco Sondermann, Ufuk Altinkaynak, Thomas Eichstaedt and Olaf Westrik.</p>
<p>

This product includes GeoLite data created by MaxMind, available from <a href='http://www.maxmind.com/' target="_blank">http://www.maxmind.com/</a>.
</p>
END
;
&Header::closebox();

&Header::openbox('100%', 'left', 'General Public License v3');
if ( -e "/usr/share/doc/licenses/GPLv3" )  {
	print '<textarea rows="25" cols="75" readonly="true">';
	print `cat "/usr/share/doc/licenses/GPLv3"`;
	print '</textarea>';
}
else {
	print '<br /><a href="http://www.gnu.org/licenses/gpl-3.0.txt" target="_blank">GENERAL PUBLIC LICENSE</a><br />';
}

&Header::closebox();

&Header::closebigbox();

&Header::closepage();
