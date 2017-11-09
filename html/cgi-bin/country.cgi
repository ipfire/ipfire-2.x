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

my $col;
my $lines = '1';
my $lines2 = '';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/geoip-functions.pl";
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

&Header::showhttpheaders();

&Header::openpage($Lang::tr{'countries'}, 1, '');
&Header::openbigbox('100%', 'left');

&Header::openbox('100%', 'left', $Lang::tr{'country codes and flags'});

print<<END;
<table class='tbl'>
	<tr>
		<th style='width=5%'><b>$Lang::tr{'flag'}</b></th>
		<th style='width=5%'><b>$Lang::tr{'countrycode'}</b></th>
		<th style='width=40% text-align:left'><b>$Lang::tr{'country'}</b></th>
		<th>&nbsp;</th>
		<th style='width=5%'><b>$Lang::tr{'flag'}</b></th>
		<th style='width=5%;'><b>$Lang::tr{'countrycode'}</b></th>
		<th style='width=40% text-align:left;'><b>$Lang::tr{'country'}</b></th>
	</tr>
END

# Get a list of all supported country codes.
my @countries = Locale::Codes::Country::all_country_codes();

# Loop through whole country list.
foreach my $country (@countries) {
	$lines++;

	# Convert country code into upper case.
	$country = uc($country);

	# Get flag icon for of the country.
	my $flag_icon = &GeoIP::get_flag_icon($country);

	# Get country name.
	my $name = &GeoIP::get_full_country_name($country);

	if ($lines % 2) {
		print "<td $col><a id='$country'><img src='$flag_icon' alt='$country' title='$country'/></a></td>";
		print "<td $col>$country</td>";
		print "<td $col>$name</td></tr>\n";
	} else {
		$lines2++;
		if($lines2 % 2) {
			$col="style='background-color:${Header::table2colour};'";
		} else {
			$col="style='background-color:${Header::table1colour};'";
		}
		print "<tr>";
		print "<td $col><a id='$country'><img src='$flag_icon' alt='$country' title='$country'/></a></td>";
		print "<td $col>$country</td>";
		print "<td $col>$name</td>";
		print "<td $col>&nbsp;</td>";

		# Finish column when the last element in the array has passed and we have an uneven amount of items.
		if ( $country eq $countries[-1] ) {
			print "<td $col>&nbsp;</td>\n";
			print "<td $col>&nbsp;</td>\n";
			print "<td $col>&nbsp;</td></tr>\n";
		}
	}
}
print "</table>";
&Header::closebox();

&Header::closebigbox();

print "<div style='text-align:center'><a href='$ENV{'HTTP_REFERER'}'>$Lang::tr{'back'}</a></div>\n";

&Header::closepage();


