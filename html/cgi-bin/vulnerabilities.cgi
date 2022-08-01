#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2022  IPFire Team  <info@ipfire.org>                     #
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

my %VULNERABILITIES = (
	"itlb_multihit" => "$Lang::tr{'itlb multihit'} (CVE-2018-12207)",
	"l1tf" => "$Lang::tr{'foreshadow'} (CVE-2018-3620)",
	"mds" => "$Lang::tr{'fallout zombieload ridl'} (CVE-2018-12126, CVE-2018-12130, CVE-2018-12127, CVE-2019-11091)",
	"meltdown" => "$Lang::tr{'meltdown'} (CVE-2017-5754)",
	"mmio_stale_data" => "$Lang::tr{'mmio stale data'} (CVE-2022-21123, CVE-2022-21125, CVE-2022-21127, CVE-2022-21166)",
	"retbleed" => "$Lang::tr{'retbleed'} (CVE-2022-29900, CVE-2022-29901)",
	"spec_store_bypass" => "$Lang::tr{'spectre variant 4'} (CVE-2018-3639)",
	"spectre_v1" => "$Lang::tr{'spectre variant 1'} (CVE-2017-5753)",
	"spectre_v2" => "$Lang::tr{'spectre variant 2'} (CVE-2017-5715)",
	"srbds" => "$Lang::tr{'srbds'} (CVE-2020-0543)",
	"tsx_async_abort" => "$Lang::tr{'taa zombieload2'} (CVE-2019-11135)",
);

my $errormessage = "";
my $notice = "";

my %mainsettings = ();
my %color = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/ipfire/include/colors.txt", \%color);

my %settings = (
	"ENABLE_SMT" => "auto",
);
&General::readhash("${General::swroot}/main/security", \%settings);

&Header::showhttpheaders();

&Header::getcgihash(\%settings);

if ($settings{'ACTION'} eq $Lang::tr{'save'}) {
	if ($settings{'ENABLE_SMT'} !~ /^(auto|on)$/) {
		$errormessage = $Lang::tr{'invalid input'};
	}

	unless ($errormessage) {
		&General::writehash("${General::swroot}/main/security", \%settings);
		$notice = $Lang::tr{'please reboot to apply your changes'};
	}
}

my %checked = ();
$checked{'ENABLE_SMT'}{'auto'} = '';
$checked{'ENABLE_SMT'}{'on'} = '';
$checked{'ENABLE_SMT'}{$settings{'ENABLE_SMT'}} = "checked";

&Header::openpage($Lang::tr{'processor vulnerability mitigations'}, 1, '');

&Header::openbigbox("100%", "left", "", $errormessage);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<font color='red'>$errormessage</font>";
	&Header::closebox();
}

if ($notice) {
	&Header::openbox('100%', 'left', $Lang::tr{'notice'});
	print "<font color='red'>$notice</font>";
	&Header::closebox();
}

&Header::openbox('100%', 'center', $Lang::tr{'processor vulnerability mitigations'});

print <<END;
	<table class="tbl" width='100%'>
		<thead>
			<tr>
				<th align="center">
					<strong>$Lang::tr{'vulnerability'}</strong>
				</th>
				<th align="center">
					<strong>$Lang::tr{'status'}</strong>
				</th>
			</tr>
		</thead>
		<tbody>
END

my $id = 0;
for my $vuln (sort keys %VULNERABILITIES) {
	my ($status, $message) = &check_status($vuln);
	next if (!$status);

	my $colour = "";
	my $bgcolour = "";
	my $status_message = "";

	# Not affected
	if ($status eq "Not affected") {
		$status_message = $Lang::tr{'not affected'};
		$colour = "white";
		$bgcolour = ${Header::colourgreen};

	# Vulnerable
	} elsif ($status eq "Vulnerable") {
		$status_message = $Lang::tr{'vulnerable'};
		$colour = "white";
		$bgcolour = ${Header::colourred};

	# Mitigated
	} elsif ($status eq "Mitigation") {
		$status_message = $Lang::tr{'mitigated'};
		$colour = "white";
		$bgcolour = ${Header::colourblue};

	# Unknown report from kernel
	} else {
		$status_message = $status;
		$colour = "black";
		$bgcolour = ${Header::colouryellow};
	}

	my $table_colour = ($id++ % 2) ? $color{'color22'} : $color{'color20'};

	print <<END;
		<tr bgcolor="$table_colour">
			<td align="left">
				<strong>$VULNERABILITIES{$vuln}</strong>
			</td>

			<td bgcolor="$bgcolour" align="center">
				<font color="$colour">
END
	if ($message) {
		print "<strong>$status_message</strong> - $message";
	} else {
		print "<strong>$status_message</strong>";
	}

	print <<END;
				</font>
			</td>
		</tr>
END
	}

print <<END;
		</tbody>
	</table>
END

&Header::closebox();

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

&Header::openbox('100%', 'center', $Lang::tr{'settings'});

my $smt_status = &smt_status();

print <<END;
	<table class="tbl" width="66%">
		<tbody>
			<tr>
				<th colspan="2" align="center">
					<strong>$smt_status</strong>
				</th>
			</tr>

			<tr>
				<td width="50%" align="left">
					$Lang::tr{'enable smt'}
				</td>

				<td width="50%" align="center">
					<label>
						<input type="radio" name="ENABLE_SMT"
							value="auto" $checked{'ENABLE_SMT'}{'auto'}>
						$Lang::tr{'automatic'}
					</label> /
					<label>
						<input type="radio" name="ENABLE_SMT"
							value="on" $checked{'ENABLE_SMT'}{'on'}>
						$Lang::tr{'force enable'} ($Lang::tr{'dangerous'})
					</label>
				</td>
			</tr>

			<tr>
				<td colspan="2" align="right">
					<input type="submit" name="ACTION" value="$Lang::tr{'save'}">
				</td>
			</tr>
		</tbody>
	</table>
END

&Header::closebox();

print "</form>\n";

&Header::closebigbox();

&Header::closepage();

sub check_status($) {
	my $vuln = shift;

	open(FILE, "/sys/devices/system/cpu/vulnerabilities/$vuln") or return undef;
	my $status = <FILE>;
	close(FILE);

	chomp($status);

	# Fix status when something has been mitigated, but not fully, yet
	if ($status =~ /^(Mitigation): (.*vulnerable.*)$/) {
		return ("Vulnerable", $status);
	}

	if ($status =~ /^(Vulnerable|Mitigation): (.*)$/) {
		return ($1, $2);
	}

	return $status;
}

sub smt_status() {
	open(FILE, "/sys/devices/system/cpu/smt/control");
	my $status = <FILE>;
	close(FILE);

	chomp($status);

	if ($status eq "on") {
		return $Lang::tr{'smt enabled'};
	} elsif (($status eq "off") || ($status eq "forceoff")) {
		return $Lang::tr{'smt disabled'};
	} elsif ($status eq "notsupported") {
		return $Lang::tr{'smt not supported'};
	}

	return $status;
}
