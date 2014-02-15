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

use Locale::Country;

my $flagdir = '/srv/web/ipfire/html/images/flags';
my $lines = '1';
my $lines2 = '';
my @flaglist=();
my @flaglistfiles=();
my $flag = '';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

&Header::showhttpheaders();

&Header::openpage('Country Codes', 1, '');
&Header::openbigbox('100%', 'LEFT');

&Header::openbox('100%', 'LEFT', 'Flags & Country Codes:');
print "<TABLE WIDTH='100%' border='0' class='tbl'>";
print "<tr><th width='5%'><b>Flag</b></th>";
print "<th width='5%'><b>Code</b></th>";
print "<th width='40%'><b>$Lang::tr{'country'}</b></th>";
print "<th><b>&nbsp;</b></th>";
print "<th width='5%'><b>Flag</b></th>";
print "<th width='5%'><b>Code</b></th>";
print "<th width='40%'><b>$Lang::tr{'country'}</b></th></tr>";

@flaglist = <$flagdir/*>;

undef @flaglistfiles;

foreach (@flaglist)
{
	if (!-d) { push(@flaglistfiles,substr($_,rindex($_,"/")+1));	}
}
my $col="";
foreach $flag (@flaglistfiles)
{
	$lines++;

	my $flagcode = uc(substr($flag, 0, 2));
	my $fcode = lc($flagcode);
	my $country = Locale::Country::code2country($fcode);
	if($fcode eq 'eu') { $country = 'Europe'; }
	if($fcode eq 'tp') { $country = 'East Timor'; }
	if($fcode eq 'yu') { $country = 'Yugoslavia'; }
	if ($lines % 2) {
		print "<td $col><a name='$fcode'/><img src='/images/flags/$fcode.png' border='0' align='absmiddle' alt='$flagcode'</td>";
		print "<td $col>$flagcode</td>";
		print "<td $col>$country</td></tr>\n";
}
else {
	$lines2++;
	if($lines2 % 2) {
		print "<tr>";
		$col="bgcolor='${Header::table2colour}'";
	} else {
		print "<tr>";
		$col="bgcolor='${Header::table1colour}'";
	}
	print "<td $col><a name='$fcode'/><img src='/images/flags/$fcode.png' border='0' align='absmiddle' alt='$flagcode'</td>";
	print "<td $col>$flagcode</td>";
	print "<td $col>$country</td>";
	print "<td $col>&nbsp;</td>";
	}
}


print "</TABLE>";
&Header::closebox();

&Header::closebigbox();

print <<END
<div align='center'>
<table width='80%'>
<tr>
<td align='center'><a href='$ENV{'HTTP_REFERER'}'>$Lang::tr{'back'}</a></td>
</tr>
</table>
</div>
END
; 

&Header::closepage();


