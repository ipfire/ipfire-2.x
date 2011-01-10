#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2010  IPFire Team  <info@ipfire.org>                          #
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
			<input type="hidden" name="hosted_button_id" value="10781833">
			<input type="image" src=$Lang::tr{'donation-link'} border="0" name="submit" alt="PayPal - The safer, easier way to pay online.">
			<img alt="" border="0" src="https://www.paypal.com/de_DE/i/scr/pixel.gif" width="1" height="1">
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

Project Leader - Michael Tremer
(<a href='mailto:mitch\@ipfire.org'>mitch\@ipfire.org</a>)<br />
Vice Project Leader - Christian Schmidt
(<a href='mailto:maniacikarus\@ipfire.org'>maniacikarus\@ipfire.org</a>)<br />
Maintainer IPFire 2.x - Arne Fitzenreiter
(<a href='mailto:arne\@ipfire.org'>arne\@ipfire.org</a>)<br />
Developer - Stefan Schantl
(<a href='mailto:Stevee\@ipfire.org'>stevee\@ipfire.org</a>)<br />
Developer - Jan Paul T&uuml;cking
(<a href='mailto:earl\@ipfire.org'>earl\@ipfire.org</a>)<br />
Developer & Webmaster - Heiner Schmeling
(<a href='mailto:cm\@ipfire.org'>cm\@ipfire.org</a>)<br />
Developer (Addons) - Peter Pfeiffer
(<a href='mailto:peterman\@ipfire.org'>peterman\@ipfire.org</a>)<br />
Supporter, Wiki-Admin & Sponsor - Ronald Wiesinger
(<a href='mailto:rowie\@ipfire.org'>rowie\@ipfire.org</a>)<br />
Supporter & Wiki-Admin - Silvio Rechenbach
(<a href='mailto:exciter\@ipfire.org'>exciter\@ipfire.org</a>)<br />
Sponsor - Peter Schaelchli
(<a href='mailto:scp\@ipfire.org'>scp\@ipfire.org</a>)<br />
Sponsor - Sven Nierlein
(<a href='mailto:affect\@ipfire.org'>affect\@versatel.de</a>)<br />
Sponsor  - Rene Zingel
(<a href='mailto:linuxadmin\@ipfire.org'>linuxadmin\@ipfire.org</a>)<br />
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
