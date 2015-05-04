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

use Locale::Codes::Country;

my $flagdir = '/srv/web/ipfire/html/images/flags';
my $lines = '1';
my $lines2 = '';
my @flaglist=();
my @flaglistfiles=();
my $flag = '';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/geoip-functions.pl";
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

&Header::showhttpheaders();

&Header::openpage($Lang::tr{'countries'}, 1, '');
&Header::openbigbox('100%', 'left');

&Header::openbox('100%', 'left', $Lang::tr{'country codes and flags'});
print "<table class='tbl'>";
print "<tr><th style='width=5%;'><b>$Lang::tr{'flag'}</b></th>";
print "<th style='width=5%;'><b>$Lang::tr{'countrycode'}</b></th>";
print "<th style='width=40%; text-align:left;'><b>$Lang::tr{'country'}</b></th>";
print "<th>&nbsp;</th>";
print "<th style='width=5%;'><b>$Lang::tr{'flag'}</b></th>";
print "<th style='width=5%;'><b>$Lang::tr{'countrycode'}</b></th>";
print "<th style='width=40%; text-align:left;'><b>$Lang::tr{'country'}</b></th></tr>";

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

	# Get flag icon for of the country.
	my $flag_icon = &GeoIP::get_flag_icon($fcode);

	my $country = Locale::Country::code2country($fcode);
	if($fcode eq 'eu') { $country = 'Europe'; }
	if($fcode eq 'tp') { $country = 'East Timor'; }
	if($fcode eq 'yu') { $country = 'Yugoslavia'; }
	if ($lines % 2) {
		print "<td $col><a id='$fcode'><img src='$flag_icon' alt='$flagcode' title='$flagcode'/></a></td>";
		print "<td $col>$flagcode</td>";
		print "<td $col>$country</td></tr>\n";
	}
	else {
		$lines2++;
		if($lines2 % 2) {
			$col="style='background-color:${Header::table2colour};'";
		} else {
			$col="style='background-color:${Header::table1colour};'";
		}
		print "<tr>";
		print "<td $col><a id='$fcode'><img src='$flag_icon' alt='$flagcode' title='$flagcode'/></a></td>";
		print "<td $col>$flagcode</td>";
		print "<td $col>$country</td>";
		print "<td $col>&nbsp;</td>";
	}
}


print "</table>";
&Header::closebox();

&Header::closebigbox();

print <<END
<div style='text-align:center'>
<a href='$ENV{'HTTP_REFERER'}'>$Lang::tr{'back'}</a>
</div>
END
; 

&Header::closepage();


