#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2025 Michael Tremer <michael.tremer@ipfire.org>               #
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
use JSON::PP;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require "/var/ipfire/general-functions.pl";
require "${General::swroot}/header.pl";

my %cgiparams = ();
my @errormessages = ();

# Fetch CGI parameters
&Header::getcgihash(\%cgiparams, {'wantfile' => 1, 'filevar' => 'FH'});

# Read the settings
my %settings = ();
&General::readhash("${General::swroot}/lldp/settings", \%settings);

# Save on main page
if ($cgiparams{"ACTION"} eq $Lang::tr{'save'}) {
	# Store whether enabled or not
	if ($cgiparams{'ENABLED'} =~ m/^(on|off)?$/) {
		$settings{'ENABLED'} = $cgiparams{'ENABLED'};
	}

	# Validate the description
	if (($cgiparams{"DESCRIPTION"} eq "") || ($cgiparams{"DESCRIPTION"} =~ /^[A-Za-z0-9_\-]+$/)) {
		$settings{"DESCRIPTION"} = $cgiparams{"DESCRIPTION"};
	} else {
		# Add error message about invalid characters in description.
		push(@errormessages, "$Lang::tr{'lldp invalid description'}");
	}

	# Don't continue on error
	goto MAIN if (scalar @errormessages);

	# Store the configuration file
	&General::writehash("${General::swroot}/lldp/settings", \%settings);

	# Start if enabled
	if ($settings{"ENABLED"} eq "on") {
		&General::system("/usr/local/bin/lldpdctrl", "restart");
	} else {
		&General::system("/usr/local/bin/lldpdctrl", "stop");
	}
}

# The main page starts here
MAIN:
	# Send HTTP Headers
	&Header::showhttpheaders();

	# Open the page
	&Header::openpage($Lang::tr{'lldp'}, 1, '');

	# Show any error messages
	&Header::errorbox(@errormessages);

	# Open a box for Global Settings
	&Header::openbox('100%', '', $Lang::tr{'global settings'});

	my %checked = (
		"ENABLED" => ($settings{"ENABLED"} eq "on") ? "checked" : "",
	);

	# Description field, defaults to CGI input otherwise use configured description.
	my $description = $cgiparams{'DESCRIPTION'} // $settings{'DESCRIPTION'};

	print <<END;
		<form method="POST" action="">
			<table class="form">
				<tr>
					<td>$Lang::tr{'enabled'}</td>
					<td>
						<input type="checkbox" name="ENABLED" $checked{'ENABLED'} />
					</td>
				</tr>

				<tr>
					<td>$Lang::tr{'description'}</td>
					<td>
						<input type="text" name="DESCRIPTION" value="$description" />
					</td>
				</tr>

				<tr class="action">
					<td colspan="2">
						<input type='submit' name='ACTION' value='$Lang::tr{'save'}' />
					</td>
				</tr>
			</table>
		</form>
END
	&Header::closebox();

	# Load data about all peers
	my @output = &General::system_output("lldpctl", "-f", "json0");

	my $json;

	# Parse the JSON output
	eval {
		$json = decode_json join("\n", @output);
		1;
	} or do {
		$json = undef;
	};

	# Show a list with all peers if the service is enabled
	if ($settings{"ENABLED"} eq "on") {
		&Header::opensection($Lang::tr{'lldp neighbors'});

		# Fetch the interface object
		my $interface = $json->{"lldp"}[0]->{"interface"};

		print <<END;
			<table class='tbl'>
				<tr>
					<th>
						$Lang::tr{'name'}
					</th>

					<th>
						$Lang::tr{'interface'}
					</th>

					<th>
						$Lang::tr{'port'}
					</th>

					<th style="text-align: right;">
						$Lang::tr{'vlan'}
					</th>

					<th>
						$Lang::tr{'protocol'}
					</th>

					<th>
						$Lang::tr{'description'}
					</th>
				</tr>
END

				foreach my $peer (@{ $interface }) {
					my $intf = $peer->{"name"};
					my $proto = $peer->{"via"};
					my $name = "";
					my $descr = "";
					my $port_name = "";
					my $vlan_id = "";

					# Fetch the chassis
					foreach my $chassis (@{ $peer->{"chassis"} }) {
						$name = &Header::escape(
							$chassis->{"name"}[0]->{"value"}
						);;
						$descr = &Header::escape(
							$chassis->{"descr"}[0]->{"value"}
						);

						# Replace any line breaks in the description
						$descr =~ s/\n/<br>/g;
					}

					# Fetch the port
					foreach my $port (@{ $peer->{"port"} }) {
						$port_name = $port->{"descr"}[0]->{"value"};
					}

					# Fetch the VLAN
					foreach my $vlan (@{ $peer->{"vlan"} }) {
						$vlan_id = $vlan->{"vlan-id"};
					}

					print <<END;
						<tr>
							<th scope="row">
								$name
							</th>

							<td>
								$intf
							</td>

							<td>
								$port_name
							</td>

							<td style="text-align: right;">
								$vlan_id
							</td>

							<td>
								$proto
							</td>

							<td>
								$descr
							</td>
						</tr>
END
				}

				# Show a message if there are no neighbors
				unless (scalar @{ $interface }) {
					print <<END;
						<tr>
							<td colspan="6" style="text-align: center;">
								$Lang::tr{'lldp there are no neighbors'}
							</td>
						</tr>
END
				}

		print <<END;
			</table>
END

		&Header::closesection();
	}

	&Header::closepage();

	exit(0);
