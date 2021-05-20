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
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require '/opt/pakfire/lib/functions.pl';

my $configfile = "/var/ipfire/main/send_profile";

my %fireinfosettings=();
my $errormessage='';

&Header::showhttpheaders();

$fireinfosettings{'ENABLE_FIREINFO'} = 'off';
$fireinfosettings{'ACTION'} = '';

&Header::getcgihash(\%fireinfosettings);

if ( -e "$configfile" ) {
	$fireinfosettings{'ENABLE_FIREINFO'} = 'on';
}

if ("$fireinfosettings{'ACTION'}" eq "trigger") {
	if ($fireinfosettings{'ENABLE_FIREINFO'} eq 'off') 	{
		&General::log($Lang::tr{'fireinfo is enabled'});

		# Write empty configfile.
		open(FILE, ">$configfile");
		close(FILE);

		$fireinfosettings{'ENABLE_FIREINFO'} = 'on';
	} else {
		&General::log($Lang::tr{'fireinfo is disabled'});
		unlink "$configfile";
		$fireinfosettings{'ENABLE_FIREINFO'} = 'off';
	}
	&General::system_background("/usr/local/bin/fireinfoctrl");
}

&Header::openpage('Fireinfo', 1, '');

if ($fireinfosettings{'ENABLE_FIREINFO'} ne "on") {
	&Header::openbox("100%", "left", "$Lang::tr{'fireinfo why enable'}");

	print <<END;
<font color="$Header::colourred">
	<p>
		$Lang::tr{'fireinfo why descr1'}
		$Lang::tr{'fireinfo why descr2'}<a href="https://fireinfo.ipfire.org" target="_blank">$Lang::tr{'fireinfo why read more'}</a>
	</p>
</font>
END

	&Header::closebox();
}

&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
	&Header::openbox('100%', 'left', "$Lang::tr{'error messages'}");
	print "<font class='base'>$errormessage&nbsp;</font>\n";
	&Header::closebox();
}

# Get IPFire version string.
open(FILE, "/etc/system-release");
my $ipfire_version = <FILE>;
close(FILE);

my $pakfire_version = &Pakfire::make_version();
my $kernel_version = &General::system_output("uname", "-a");

&Header::openbox('100%', 'left', $Lang::tr{'fireinfo system version'});
print <<END;
	<table cellspacing='1' cellpadding='0' class='tbl'>
		<tr>
			<td align='center' bgcolor='#F0F0F0' width='15%'>$Lang::tr{'fireinfo ipfire version'}</td>
			<td bgcolor='#F0F0F0'><code>$ipfire_version</code></td>
		</tr>
		<tr>
			<td align='center' bgcolor='#D6D6D6' width='15%'>$Lang::tr{'fireinfo pakfire version'}</td>
			<td bgcolor='#D6D6D6'><code>$pakfire_version</code></td>
		</tr>
		<tr>
			<td align='center' bgcolor='#F0F0F0' width='15%'>$Lang::tr{'fireinfo kernel version'}</td>
			<td bgcolor='#F0F0F0'><code>$kernel_version</code></td>
		</tr>
	</table>
END
&Header::closebox();

# Read pregenerated profile data
open(FILE, "/var/ipfire/fireinfo/profile");
my $profile = <FILE>;
close(FILE);
chomp($profile);

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

# Read profile ID from file
open(FILE, "/var/ipfire/fireinfo/public_id");
my $profile_id = <FILE>;
close(FILE);
chomp($profile_id);

&Header::openbox('100%', 'left', $Lang::tr{'fireinfo settings'});
print <<END;
<input type='hidden' name='ACTION' value='trigger' />
<table width='100%'>
	<tr>
		<td>$Lang::tr{'fireinfo your profile id'}:</td>
		<td>
			<a href="https://fireinfo.ipfire.org/profile/$profile_id" target="_blank">$profile_id</a>
		</td>
	</tr>
	<tr>
		<!-- spacer -->
		<td colspan="2">&nbsp;</td>
	</tr>
	<tr>
		<td class='base'>
END

if ($fireinfosettings{'ENABLE_FIREINFO'} eq "on") {
	print "<font color='$Header::colourgreen'>$Lang::tr{'fireinfo is submitted'}</font>";
} else {
	print "<font color='$Header::colourred'>$Lang::tr{'fireinfo not submitted'}</font>";
}

print "</td><td>";

if ($fireinfosettings{'ENABLE_FIREINFO'} eq "on") {
	print "<input type='submit' name='submit' value=\"$Lang::tr{'fireinfo is submitted button'}\" />";
} else {
	print "<input type='submit' name='submit' value=\"$Lang::tr{'fireinfo not submitted button'}\" />";
}

print <<END;
		</td>
	</tr>
	<tr>
		<!-- spacer -->
		<td colspan="2"><font color='$Header::colourgreen'>&nbsp;</font></td>
	</tr>
	<tr>
		<td colspan='2'>
			<textarea rows="25" cols="75" readonly="readonly">$profile</textarea>
		</td>
	</tr>
</table>
END
;
&Header::closebox();
print "</form>\n";

&Header::closebigbox();
&Header::closepage();
