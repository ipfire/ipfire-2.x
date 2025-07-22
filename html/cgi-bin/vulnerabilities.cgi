#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2025  IPFire Team  <info@ipfire.org>                     #
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
	"gather_data_sampling" => "$Lang::tr{'downfall gather data sampling'} (CVE-2022-40982)",
	"indirect_target_selection" => "$Lang::tr{'indirect target selection'} (CVE-2024-28956)",
	"itlb_multihit" => "$Lang::tr{'itlb multihit'} (CVE-2018-12207)",
	"l1tf" => "$Lang::tr{'foreshadow'} (CVE-2018-3620)",
	"mds" => "$Lang::tr{'fallout zombieload ridl'} (CVE-2018-12126, CVE-2018-12130, CVE-2018-12127, CVE-2019-11091)",
	"meltdown" => "$Lang::tr{'meltdown'} (CVE-2017-5754)",
	"mmio_stale_data" => "$Lang::tr{'mmio stale data'} (CVE-2022-21123, CVE-2022-21125, CVE-2022-21127, CVE-2022-21166)",
	"reg_file_data_sampling" => "$Lang::tr{'reg_file_data_sampling'} (CVE-2023-28746)",
	"retbleed" => "$Lang::tr{'retbleed'} (CVE-2022-29900, CVE-2022-29901)",
	"spec_rstack_overflow" => "$Lang::tr{'spec rstack overflow'} (CVE-2023-20569)",
	"spec_store_bypass" => "$Lang::tr{'spectre variant 4'} (CVE-2018-3639)",
	"spectre_v1" => "$Lang::tr{'spectre variant 1'} (CVE-2017-5753)",
	"spectre_v2" => "$Lang::tr{'spectre variant 2'} (CVE-2017-5715)",
	"srbds" => "$Lang::tr{'srbds'} (CVE-2020-0543)",
	"tsa" => "$Lang::tr{'transient sheduler attacks'} (CVE-2024-36350,36357,36348,36349)",
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

&Header::opensection();

print <<END;
	<table class="tbl">
		<thead>
			<tr>
				<th class="text-center">
					$Lang::tr{'vulnerability'}
				</th>

				<th class="text-center">
					$Lang::tr{'status'}
				</th>
			</tr>
		</thead>

		<tbody>
END

for my $vuln (sort keys %VULNERABILITIES) {
	my ($status, $message) = &check_status($vuln);
	next if (!$status);

	my $status_message = $status;

	# Not affected
	if ($status eq "not-affected") {
		$status_message = $Lang::tr{'not affected'};

	# Vulnerable
	} elsif ($status eq "vulnerable") {
		$status_message = $Lang::tr{'vulnerable'};

	# Mitigated
	} elsif ($status eq "mitigation") {
		$status_message = $Lang::tr{'mitigated'};
	}

	print <<END;
		<tr>
			<th scope="row">
				$VULNERABILITIES{$vuln}
			</th>

			<td class="status is-$status">
END
	if ($message) {
		print "$status_message - $message";
	} else {
		print "$status_message";
	}

	print <<END;
			</td>
		</tr>
END
	}

print <<END;
		</tbody>
	</table>
END

&Header::closesection();

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

&Header::openbox('100%', 'center', $Lang::tr{'settings'});

my $smt_status = &smt_status();

print <<END;
	<table class="tbl" width="100%">
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
		return ("vulnerable", $status);

	} elsif ($status eq "Not affected") {
		return "not-affected";

	} elsif ($status =~ /^(Vulnerable|Mitigation): (.*)$/) {
		return (lc $1, $2);
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
