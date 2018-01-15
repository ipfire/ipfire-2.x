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
		system ('/usr/bin/touch', $configfile);
		$fireinfosettings{'ENABLE_FIREINFO'} = 'on';
	} else {
		&General::log($Lang::tr{'fireinfo is disabled'});
		unlink "$configfile";
		$fireinfosettings{'ENABLE_FIREINFO'} = 'off';
	}
	system("/usr/local/bin/fireinfoctrl &");
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

my $ipfire_version = `cat /etc/system-release`;
my $pakfire_version = `cat /opt/pakfire/etc/pakfire.conf | grep "version =" | cut -d\\" -f2`;
my $kernel_version = `uname -a`;

&Header::openbox('100%', 'left', $Lang::tr{'fireinfo system version'});
print <<END;
	<table width="100%">
		<tr>
			<td>$Lang::tr{'fireinfo ipfire version'}:</td>
			<td>$ipfire_version</td>
		</tr>
		<tr>
			<td>$Lang::tr{'fireinfo pakfire version'}:</td>
			<td>$pakfire_version</td>
		</tr>
		<tr>
			<td>$Lang::tr{'fireinfo kernel version'}:</td>
			<td>$kernel_version</td>
		</tr>
	</table>
END
&Header::closebox();

# Read pregenerated profile data
my $profile = `cat /var/ipfire/fireinfo/profile`;

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

# Read profile ID from file
my $profile_id = `cat /var/ipfire/fireinfo/public_id`;
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
