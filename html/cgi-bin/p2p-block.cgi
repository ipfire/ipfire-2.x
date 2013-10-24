#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2013                                                          #
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
# Author: Alexander Marx (Amarx@ipfire.org)                                   #
###############################################################################

use strict;
no warnings 'uninitialized';
# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my $errormessage = '';
my $p2pfile = "${General::swroot}/firewall/p2protocols";

my @p2ps = ();
my %fwdfwsettings = ();
my %color = ();
my %mainsettings = ();

&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

&Header::showhttpheaders();
&Header::getcgihash(\%fwdfwsettings);
&Header::openpage($Lang::tr{'p2p block'}, 1, '');
&Header::openbigbox('100%', 'center', $errormessage);

if ($fwdfwsettings{'ACTION'} eq 'togglep2p') {
	open( FILE, "<$p2pfile") or die "Unable to read $p2pfile";
	@p2ps = <FILE>;
	close FILE;
	open( FILE, ">$p2pfile") or die "Unable to write $p2pfile";
	foreach my $p2pentry (sort @p2ps) {
		my @p2pline = split( /\;/, $p2pentry);
		if ($p2pline[1] eq $fwdfwsettings{'P2PROT'}) {
			if ($p2pline[2] eq 'on') {
				$p2pline[2] = 'off';
			} else {
				$p2pline[2] = 'on';
			}
		}
		print FILE "$p2pline[0];$p2pline[1];$p2pline[2];\n";
	}
	close FILE;

	&General::firewall_config_changed();
	&p2pblock();
} else {
	&p2pblock();
}

sub p2pblock {
	my $gif;

	open(FILE, "<$p2pfile") or die "Unable to read $p2pfile";
	@p2ps = <FILE>;
	close FILE;

	&Header::openbox('100%', 'center', $Lang::tr{'p2p block'});
	print <<END;
		<table width='35%' border='0'>
			<tr bgcolor='$color{'color22'}'>
				<td align=center colspan='2' >
					<b>$Lang::tr{'protocol'}</b>
				</td>
				<td align='center'>
					<b>$Lang::tr{'status'}</b>
				</td>
			</tr>
END

	foreach my $p2pentry (sort @p2ps) {
		my @p2pline = split( /\;/, $p2pentry);
		if ($p2pline[2] eq 'on') {
			$gif = "/images/on.gif"
		} else {
			$gif = "/images/off.gif"
		}

		print <<END;
			<tr bgcolor='$color{'color20'}'>
				<td align='center' colspan='2'>
					$p2pline[0]:
				</td>
				<td align='center'>
					<form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='P2PROT' value='$p2pline[1]'>
						<input type='image' img src='$gif' alt='$Lang::tr{'click to disable'}' title='$Lang::tr{'fwdfw toggle'}' style='padding-top: 0px; padding-left: 0px; padding-bottom: 0px ;padding-right: 0px ;display: block;'>
						<input type='hidden' name='ACTION' value='togglep2p'>
					</form>
				</td>
			</tr>
END
	}

	print <<END;
			<tr>
				<td>
					<img src='/images/on.gif'>
				</td>
				<td>
					$Lang::tr{'outgoing firewall p2p allow'}
				</td>
			</tr>
			<tr>
				<td>
					<img src='/images/off.gif'>
				</td>
				<td>
					$Lang::tr{'outgoing firewall p2p deny'}
				</td>
			</tr>
		</table>
END

	&Header::closebox();
}

&Header::closebigbox();
&Header::closepage();
