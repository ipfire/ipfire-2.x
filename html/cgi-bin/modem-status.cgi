#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2014  IPFire Team  <info@ipfire.org>                     #
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
require "${General::swroot}/modem-lib.pl";

my $modem;
my %ethsettings = {};
my %pppsettings = {};

&General::readhash("${General::swroot}/ethernet/settings", \%ethsettings);

if ($ethsettings{"RED_TYPE"} eq "PPPOE") {
	&General::readhash("${General::swroot}/ppp/settings", \%pppsettings);

	# Establish the connection to the modem.
	my $port = $pppsettings{'MONPORT'};
	if ($port) {
		$port = "/dev/$port";
		$modem = Modem->new($port, $pppsettings{"DTERATE"});
	}
}

&Header::showhttpheaders();
&Header::openpage($Lang::tr{'modem information'}, 1, '');
&Header::openbigbox('100%', 'left');

if ($modem) {
	&Header::openbox("100%", "center", $Lang::tr{'modem hardware details'});

	print <<END;
		<table width="100%">
			<tbody>
END

	my $vendor = $modem->get_vendor();
	if ($vendor) {
		print <<END;
			<tr>
				<td width="33%">$Lang::tr{'vendor'}</td>
				<td>$vendor</td>
			</tr>
END
	}

	my $model = $modem->get_model();
	if ($model) {
		print <<END;
			<tr>
				<td width="33%">$Lang::tr{'model'}</td>
				<td>$model</td>
			</tr>
END
	}

	my $software_version = $modem->get_software_version();
	if ($software_version) {
		print <<END;
			<tr>
				<td width="33%">$Lang::tr{'software version'}</td>
				<td>$software_version</td>
			</tr>
END
	}

	my $imei = $modem->get_imei();
	if ($imei) {
		print <<END;
			<tr>
				<td width="33%">$Lang::tr{'imei'}</td>
				<td>$imei</td>
			</tr>
END
	}

	my @caps = $modem->get_capabilities();
	if (@caps) {
		my $caps_string = join(", ", @caps);

		print <<END;
			<tr>
				<td width="33%">$Lang::tr{'capabilities'}</td>
				<td>$caps_string</td>
			</tr>
END
	}

	print <<END;
			</tbody>
		</table>
END
	&Header::closebox();


	&Header::openbox("100%", "center", $Lang::tr{'modem sim information'});
	print <<END;
		<table width="100%">
			<tbody>
END

	my $imsi = $modem->get_sim_imsi();
	if ($imsi) {
		print <<END;
			<tr>
				<td width="33%">$Lang::tr{'imsi'}</td>
				<td>$imsi</td>
			</tr>
END
	}

	print <<END;
			</tbody>
		</table>
END
	&Header::closebox();

	&Header::openbox("100%", "center", $Lang::tr{'modem network information'});
	print <<END;
		<table width="100%">
			<tbody>
END

	my $network_registration = $modem->get_network_registration();
	if ($network_registration) {
		print <<END;
			<tr>
				<td width="33%">$Lang::tr{'modem network registration'}</td>
				<td>$network_registration</td>
			</tr>
END
	}

	my $network_operator = $modem->get_network_operator();
	if ($network_operator) {
		print <<END;
			<tr>
				<td width="33%">$Lang::tr{'modem network operator'}</td>
				<td>$network_operator</td>
			</tr>
END
	}

	my $network_mode = $modem->get_network_mode();
	if ($network_mode) {
		print <<END;
			<tr>
				<td width="33%">$Lang::tr{'modem network mode'}</td>
				<td>$network_mode</td>
			</tr>
END
	}

	my $signal_quality = $modem->get_signal_quality();
	if ($signal_quality) {
		print <<END;
			<tr>
				<td width="33%">$Lang::tr{'modem network signal quality'}</td>
				<td>$signal_quality dBm</td>
			</tr>
END
	}

	my $bit_error_rate = $modem->get_bit_error_rate();
	if ($bit_error_rate) {
		print <<END;
			<tr>
				<td width="33%">$Lang::tr{'modem network bit error rate'}</td>
				<td>$bit_error_rate</td>
			</tr>
END
	}
	print <<END;
			</tbody>
		</table>
END

	&Header::closebox();
} else {
	&Header::openbox("100%", "center", $Lang::tr{'modem no connection'});
	print "<p>$Lang::tr{'modem no connection message'}</p>";
	&Header::closebox();
}

&Header::closebigbox();
&Header::closepage();
