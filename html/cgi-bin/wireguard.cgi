#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2024 Michael Tremer <michael.tremer@ipfire.org>               #
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

require "/var/ipfire/general-functions.pl";
require "${General::swroot}/header.pl";

my @errormessages = ();

# Read the global configuration
my %settings = ();
&General::readhash("/var/ipfire/wireguard/settings", \%settings);

# Set any defaults
&General::set_defaults(\%settings, {
	"ENABLED" => "off",
	"PORT"    => 51820,
});

# Generate keys
&generate_keys();

# Fetch CGI parameters
my %cgiparams = ();
&Header::getcgihash(\%cgiparams);

# Save on main page
if ($cgiparams{"ACTION"} eq $Lang::tr{'save'}) {
	# Store whether enabled or not
	if ($cgiparams{'ENABLED'} =~ m/^(on|off)$/) {
		$settings{'ENABLED'} = $cgiparams{'ENABLED'};
	}

	# Check port
	if (&General::validport($cgiparams{'PORT'})) {
		$settings{'PORT'} = $cgiparams{'PORT'};
	} else {
		push(@errormessages, $Lang::tr{'invalid port'});
	}

	# Don't continue on error
	goto MAIN if (@errormessages);

	# Store the configuration file
	&General::writehash("/var/ipfire/wireguard/settings", \%settings);

	# Start if enabled
	if ($settings{'ENABLED'} eq "on") {
		&General::system("/usr/local/bin/wireguardctl", "start");
	} else {
		&General::system("/usr/local/bin/wireguardctl", "stop");
	}
}

# The main page starts here
MAIN:
	# Send HTTP Headers
	&Header::showhttpheaders();

	# Open the page
	&Header::openpage($Lang::tr{'wireguard'}, 1, '');

	# Show any error messages
	&Header::errorbox(@errormessages);

	# Open a box for Global Settings
	&Header::openbox('100%', '', $Lang::tr{'global settings'});

	my %checked = {
		"ENABLED" => ($settings{'ENABLED'} eq "on") ? "checked" : "",
	};

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
					<td>$Lang::tr{'public key'}</td>
					<td>
						<input type="text" name="PUBLIC_KEY" value="$settings{'PUBLIC_KEY'}" readonly />
					</td>
				</tr>

				<tr>
					<td>$Lang::tr{'port'}</td>
					<td>
						<input type="number" name="PORT" value="$settings{'PORT'}"
							min="1024" max="65535" />
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
	&Header::closepage();

# This function generates a set of keys for this host if none exist
sub generate_keys($) {
	my $force = shift || 0;
	my @output = ();

	# Reset any previous keys if re-generation forced
	if ($force) {
		$settings{"PRIVATE_KEY"} = undef;
		$settings{"PUBLIC_KEY"}  = undef;
	}

	# Return if we already have keys
	return if (defined $settings{"PRIVATE_KEY"} && defined $settings{"PUBLIC_KEY"});

	# Generate a new private key
	unless (defined $settings{'PRIVATE_KEY'}) {
		# Generate a new private key
		@output = &General::system_output("wg", "genkey");

		# Store the key
		foreach (@output) {
			chomp;

			$settings{"PRIVATE_KEY"} = $_;
			last;
		}

		# Reset the public key
		$settings{"PUBLIC_KEY"} = undef;
	}

	# Derive the public key
	unless (defined $settings{"PUBLIC_KEY"}) {
		# Derive the public key
		$settings{"PUBLIC_KEY"} = &derive_public_key($settings{"PRIVATE_KEY"});
	}

	# Store the configuration file
	&General::writehash("/var/ipfire/wireguard/settings", \%settings);
}

sub derive_public_key($) {
	my $private_key = shift;
	my @output = ();

	# Derive the public key
	if (open(STDIN, "-|")) {
		@output = &General::system_output("wg", "pubkey");
	} else {
		print $private_key . "\n";
		exit (0);
	}

	# Return the first line
	foreach (@output) {
		chomp;

		return $_;
	}

	# Return on undefined on error
	return undef;
}
