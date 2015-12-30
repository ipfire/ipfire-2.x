#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2014 IPFire Developemnt Team <info@ipfire.org>                #
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
require "${General::swroot}/geoip-functions.pl";
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "/usr/lib/firewall/firewall-lib.pl";

my $notice;
my $settingsfile = "${General::swroot}/firewall/geoipblock";

my %color = ();
my %mainsettings = ();
my %settings = ();
my %cgiparams = ();

# Read configuration file.
&General::readhash("$settingsfile", \%settings);

&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

&Header::showhttpheaders();

#Get GUI values
&Header::getcgihash(\%cgiparams);

# Call subfunction to get all available locations.
my @locations = &fwlib::get_geoip_locations();

if ($cgiparams{'ACTION'} eq $Lang::tr{'save'}) {
	# Check if we want to disable geoipblock.
	if (exists $cgiparams{'GEOIPBLOCK_ENABLED'}) {
		$settings{'GEOIPBLOCK_ENABLED'} = "on";
	} else {
		$settings{'GEOIPBLOCK_ENABLED'} = "off";
	}

	# Loop through our locations array to prevent from
	# non existing countries or code.
	foreach my $cn (@locations) {
		# Check if blocking for this country should be enabled/disabled.
		if (exists $cgiparams{$cn}) {
			$settings{$cn} = "on";
		} else {
			$settings{$cn} = "off";
		}
	}

	&General::writehash("$settingsfile", \%settings);

	# Mark the firewall config as changed.
	&General::firewall_config_changed();

	# Assign reload notice. We directly can use
	# the notice from p2p block.
	$notice = $Lang::tr{'p2p block save notice'};
}

&Header::openpage($Lang::tr{'geoipblock configuration'}, 1, '');

# Print notice that a firewall reload is required.
if ($notice) {
	&Header::openbox('100%', 'left', $Lang::tr{'notice'});
	print "<font class='base'>$notice</font>";
	&Header::closebox();
}

# Checkbox pre-selection.
my $checked;
if ($settings{'GEOIPBLOCK_ENABLED'} eq "on") {
	$checked = "checked='checked'";
}

# Print box to enable/disable geoipblock.
print"<form method='POST' action='$ENV{'SCRIPT_NAME'}'>\n";

&Header::openbox('100%', 'center', $Lang::tr{'geoipblock'});
print <<END;
	<table width='95%'>
		<tr>
			<td width='25%' class='base'>$Lang::tr{'geoipblock enable feature'}
			<td><input type='checkbox' name='GEOIPBLOCK_ENABLED' $checked></td>
		</tr>
		<tr>
			<td colspan='2'><br></td>
		</tr>
	</table>

	<hr>

	<table width='95%'>
		<tr>
			<td align='center'><input type='submit' name='ACTION' value='$Lang::tr{'save'}'></td>
		</tr>
	</table>
END

&Header::closebox();

&Header::openbox('100%', 'center', $Lang::tr{'geoipblock block countries'});
### JAVA SCRIPT ###
print <<END;
<script>
	// Function to allow checking all checkboxes at once.
	function check_all() {
		\$("#countries").find(":checkbox").prop("checked", true);
	}

	function uncheck_all() {
		\$("#countries").find(":checkbox").prop("checked", false);
	}
</script>

<table width='95%' class='tbl' id="countries">
	<tr>
		<td width='5%' align='center' bgcolor='$color{'color20'}'></td>
		<td width='5%' align='center' bgcolor='$color{'color20'}'>
			<b>$Lang::tr{'flag'}</b>
		</td>
		<td width='5%' align='center' bgcolor='$color{'color20'}'>
			<b>$Lang::tr{'countrycode'}</b>
		</td>
		<td with='35%' align='left' bgcolor='$color{'color20'}'>
			<b>$Lang::tr{'country'}</b>
		</td>

		<td width='5%' bgcolor='$color{'color20'}'>&nbsp;</td>

		<td width='5%' align='center' bgcolor='$color{'color20'}'></td>
		<td width='5%' align='center' bgcolor='$color{'color20'}'>
			<b>$Lang::tr{'flag'}</b>
		</td>
		<td width='5%' align='center' bgcolor='$color{'color20'}'>
			<b>$Lang::tr{'countrycode'}</b>
		</td>
		<td with='35%' align='left' bgcolor='$color{'color20'}'>
			<b>$Lang::tr{'country'}</b>
		</td>
	</tr>
END

my $lines;
my $lines2;
my $col;
foreach my $location (@locations) {
	# Country code in upper case. (DE)
	my $ccode_uc = $location;

	# County code in lower case. (de)
	my $ccode_lc = lc($location);

	# Full name of the country based on the country code.
	my $cname = &GeoIP::get_full_country_name($ccode_lc);

	# Get flag icon for of the country.
	my $flag_icon = &GeoIP::get_flag_icon($ccode_uc);

	my $flag;
	# Check if a flag for the country is available.
	if ($flag_icon) {
		$flag="<img src='$flag_icon' alt='$ccode_uc' title='$ccode_uc'>";
	} else {
		$flag="<b>N/A</b>";
	}

	# Checkbox pre-selection.
	my $checked;
	if ($settings{$ccode_uc} eq "on") {
		$checked = "checked='checked'";
	}

	# Colour lines.
	if ($lines % 2) {
		$col="bgcolor='$color{'color20'}'";
	} else {
		$col="bgcolor='$color{'color22'}'";
	}

	# Grouping elements.
	my $line_start;
	my $line_end;
	if ($lines2 % 2) {
		# Increase lines (background color by once.
		$lines++;

		# Add empty column in front.
		$line_start="<td $col>&nbsp;</td>";

		# When the line number can be diveded by "2",
		# we are going to close the line.
		$line_end="</tr>";
	} else {
		# When the line number is  not divideable by "2",
		# we are starting a new line.
		$line_start="<tr>";
		$line_end;
	}

	print "$line_start<td align='center' $col><input type='checkbox' name='$ccode_uc' $checked></td>\n";
	print "<td align='center' $col>$flag</td>\n";
	print "<td align='center' $col>$ccode_uc</td>\n";
	print "<td align='left' $col>$cname</td>$line_end\n";

	# Finish column when the last element in the array has passed and we have an uneven amount of items.
	if(! ($lines2 % 2) && ($location eq $locations[-1] )) {
		print "<td $col>&nbsp;</td>\n";
		print "<td $col>&nbsp;</td>\n";
		print "<td $col>&nbsp;</td>\n";
		print "<td $col>&nbsp;</td>\n";
		print "<td $col>&nbsp;</td></tr>\n";
	}

$lines2++;
}

print <<END;
</table>

<table width='95%'>
	<tr>
		<td align='right'>
			<a href="javascript:check_all()">$Lang::tr{'check all'}</a> /
			<a href="javascript:uncheck_all()">$Lang::tr{'uncheck all'}</a>
		</td>
	</tr>
	<tr>
		<td align='center'><input type='submit' name='ACTION' value='$Lang::tr{'save'}'></td>
	</tr>
</table>

<hr>

<table width='70%'>
	<tr>
		<td width='5%'><img src='/images/on.gif'></td>
		<td>$Lang::tr{'geoipblock country is blocked'}</td>
		<td width='5%'><img src='/images/off.gif'></td>
		<td>$Lang::tr{'geoipblock country is allowed'}</td>
	</tr>
</table>
END

&Header::closebox();
print"</form>\n";

&Header::closebigbox();
&Header::closepage();
