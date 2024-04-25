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
use MIME::Base64;

require "/var/ipfire/general-functions.pl";
require "${General::swroot}/header.pl";
require "${General::swroot}/location-functions.pl";

my $DEFAULT_PORT		= 51820;
my $DEFAULT_KEEPALIVE	= 25;

my $INTF = "wg0";
my @errormessages = ();

# Read the global configuration
my %settings = ();
&General::readhash("/var/ipfire/wireguard/settings", \%settings);

# Read all peers
my %peers = ();
&General::readhasharray("/var/ipfire/wireguard/peers", \%peers);

# Set any defaults
&General::set_defaults(\%settings, {
	"ENABLED" => "off",
	"PORT"    => $DEFAULT_PORT,
});

# Generate keys
&generate_keys();

# Fetch CGI parameters
my %cgiparams = ();
&Header::getcgihash(\%cgiparams);

# Save on main page
if ($cgiparams{"ACTION"} eq $Lang::tr{'save'}) {
	# Store whether enabled or not
	if ($cgiparams{'ENABLED'} =~ m/^(on|off)?$/) {
		$settings{'ENABLED'} = $cgiparams{'ENABLED'};
	}

	# Check port
	if (&General::validport($cgiparams{'PORT'})) {
		$settings{'PORT'} = $cgiparams{'PORT'};
	} else {
		push(@errormessages, $Lang::tr{'invalid port'});
	}

	# Check client pool
	if (&Network::check_subnet($cgiparams{'CLIENT_POOL'})) {
		$settings{'CLIENT_POOL'} = $cgiparams{'CLIENT_POOL'};
	} else {
		push(@errormessages, $Lang::tr{'wg invalid client pool'});
	}

	# Don't continue on error
	goto MAIN if (scalar @errormessages);

	# Store the configuration file
	&General::writehash("/var/ipfire/wireguard/settings", \%settings);

	# Start if enabled
	if ($settings{'ENABLED'} eq "on") {
		&General::system("/usr/local/bin/wireguardctrl", "start");
	} else {
		&General::system("/usr/local/bin/wireguardctrl", "stop");
	}

# Delete an existing peer
} elsif ($cgiparams{"ACTION"} eq $Lang::tr{'remove'}) {
	my $key = $cgiparams{'KEY'};

	# Fail if the peer does not exist
	unless (exists $peers{$key}) {
		push(@errormessages, $Lang::tr{'wg peer does not exist'});
		goto MAIN;
	}

	# Delete the peer
	delete($peers{$key});

	# Store the configuration
	&General::writehasharray("/var/ipfire/wireguard/peers", \%peers);

	# Reload if enabled
	if ($settings{'ENABLED'} eq "on") {
		&General::system("/usr/local/bin/wireguardctrl", "reload");
	}

# Edit an existing peer
} elsif ($cgiparams{"ACTION"} eq $Lang::tr{'edit'}) {
	my $key = $cgiparams{'KEY'};

	# Fail if the peer does not exist
	unless (exists $peers{$key}) {
		push(@errormessages, $Lang::tr{'wg peer does not exist'});
		goto MAIN;
	}

	# Fetch type
	my $type = $peers{$key}[1];

	my @remote_subnets = &decode_subnets($peers{$key}[6]);
	my @local_subnets  = &decode_subnets($peers{$key}[8]);

	# Flush CGI parameters & load configuration
	%cgiparams = (
		"KEY"				=> $key,
		"ENABLED"			=> $peers{$key}[0],
		"TYPE"				=> $peers{$key}[1],
		"NAME"				=> $peers{$key}[2],
		"PUBLIC_KEY"		=> $peers{$key}[3],
		"ENDPOINT_ADDRESS"	=> $peers{$key}[4],
		"ENDPOINT_PORT"		=> $peers{$key}[5],
		"REMOTE_SUBNETS"	=> join(", ", @remote_subnets),
		"REMARKS"			=> &decode_base64($peers{$key}[7]),
		"LOCAL_SUBNETS"		=> join(", ", @local_subnets),
		"PSK"				=> $peers{$key}[9],
		"KEEPALIVE"			=> $peers{$key}[10],
	);

	# Jump to the editor
	if ($type eq "host") {
		goto EDITHOST;
	} elsif ($type eq "net") {
		goto EDITNET;
	} else {
		die "Unsupported type: $type";
	}

} elsif ($cgiparams{"ACTION"} eq "SAVE-PEER-NET") {
	my @local_subnets = ();
	my @remote_subnets = ();

	# Fetch or allocate a new key
	my $key = $cgiparams{'KEY'} || &General::findhasharraykey(\%peers);

	# Check if the name is valid
	unless (&name_is_valid($cgiparams{"NAME"})) {
		push(@errormessages, $Lang::tr{'wg invalid name'});
	}

	# Check if the name is free
	unless (&name_is_free($cgiparams{"NAME"}, $key)) {
		push(@errormessages, $Lang::tr{'wg name is already used'});
	}

	# Check the public key
	unless (&publickey_is_valid($cgiparams{'PUBLIC_KEY'})) {
		push(@errormessages, $Lang::tr{'wg invalid public key'});
	}

	# Check PSK
	if ($cgiparams{'PSK'} eq '') {
		# The PSK may be empty
	} elsif (!&publickey_is_valid($cgiparams{'PSK'})) {
		push(@errormessages, $Lang::tr{'wg invalid psk'});
	}

	# Check the endpoint address
	if ($cgiparams{'ENDPOINT_ADDRESS'} eq '') {
		# The endpoint address may be empty
	} elsif (!&Network::check_ip_address($cgiparams{'ENDPOINT_ADDRESS'})) {
		push(@errormessages, $Lang::tr{'wg invalid endpoint address'});
	}

	# Check the endpoint port
	unless (&General::validport($cgiparams{'ENDPOINT_PORT'})) {
		push(@errormessages, $Lang::tr{'wg invalid endpoint port'});
	}

	# Check keepalive
	unless (&keepalive_is_valid($cgiparams{'KEEPALIVE'})) {
		push(@errormessages, $Lang::tr{'wg invalid keepalive interval'});
	}

	# Check local subnets
	if (defined $cgiparams{'LOCAL_SUBNETS'}) {
		@local_subnets = split(/,/, $cgiparams{'LOCAL_SUBNETS'});

		foreach my $subnet (@local_subnets) {
			$subnet =~ s/^\s+//g;
			$subnet =~ s/\s+$//g;

			unless (&Network::check_subnet($subnet)) {
				push(@errormessages, $Lang::tr{'wg invalid local subnet'} . ": ${subnet}");
			}
		}
	} else {
		push(@errormessages, $Lang::tr{'wg no local subnets'});
	}

	# Check remote subnets
	if (defined $cgiparams{'REMOTE_SUBNETS'}) {
		@remote_subnets = split(/,/, $cgiparams{'REMOTE_SUBNETS'});

		foreach my $subnet (@remote_subnets) {
			$subnet =~ s/^\s+//g;
			$subnet =~ s/\s+$//g;

			unless (&Network::check_subnet($subnet)) {
				push(@errormessages, $Lang::tr{'wg invalid remote subnet'} . ": ${subnet}");
			}
		}
	} else {
		push(@errormessages, $Lang::tr{'wg no remote subnets'});
	}

	# If there are any errors, we go back to the editor
	goto EDITNET if (scalar @errormessages);

	# Save the connection
	$peers{$key} = [
		# 0 = Enabled
		"on",
		# 1 = Type
		"net",
		# 2 = Name
		$cgiparams{"NAME"},
		# 3 = Pubkey
		$cgiparams{"PUBLIC_KEY"},
		# 4 = Endpoint Address
		$cgiparams{"ENDPOINT_ADDRESS"},
		# 5 = Endpoint Port
		$cgiparams{"ENDPOINT_PORT"},
		# 6 = Remote Subnets
		&encode_subnets(@remote_subnets),
		# 7 = Remark
		&encode_remarks($cgiparams{"REMARKS"}),
		# 8 = Local Subnets
		&encode_subnets(@local_subnets),
		# 9 = PSK
		$cgiparams{"PSK"} || "",
		# 10 = Keepalive
		$cgiparams{"KEEPALIVE"} || 0,
	];

	# Store the configuration
	&General::writehasharray("/var/ipfire/wireguard/peers", \%peers);

	# Reload if enabled
	if ($settings{'ENABLED'} eq "on") {
		&General::system("/usr/local/bin/wireguardctrl", "reload");
	}

} elsif ($cgiparams{"ACTION"} eq "SAVE-PEER-HOST") {
	my @local_subnets = ();

	# Fetch or allocate a new key
	my $key = $cgiparams{'KEY'} || &General::findhasharraykey(\%peers);

	# Check if the name is valid
	unless (&name_is_valid($cgiparams{"NAME"})) {
		push(@errormessages, $Lang::tr{'wg invalid name'});
	}

	# Check if the name is free
	unless (&name_is_free($cgiparams{"NAME"}, $key)) {
		push(@errormessages, $Lang::tr{'wg name is already used'});
	}

	# Check local subnets
	if (defined $cgiparams{'LOCAL_SUBNETS'}) {
		@local_subnets = split(/,/, $cgiparams{'LOCAL_SUBNETS'});

		foreach my $subnet (@local_subnets) {
			$subnet =~ s/^\s+//g;
			$subnet =~ s/\s+$//g;

			unless (&Network::check_subnet($subnet)) {
				push(@errormessages, $Lang::tr{'wg invalid local subnet'} . ": ${subnet}");
			}
		}
	} else {
		push(@errormessages, $Lang::tr{'wg no local subnets'});
	}

	# If there are any errors, we go back to the editor
	goto EDITHOST if (scalar @errormessages);

	# Fetch some configuration parts
	if (exists $peers{$key}) {
		$cgiparams{"PUBLIC_KEY"} = $peers{$key}[3];
		$cgiparams{"PSK"}        = $peers{$key}[9];

	# Set some things if we are creating a new peer
	} else {
		# Generate a new private key
		my $private_key = &generate_private_key();

		# Derive the public key
		$cgiparams{"PUBLIC_KEY"} = &derive_public_key($private_key);

		# Generate a new PSK
		$cgiparams{"PSK"} = &generate_private_key();
	}

	# Save the connection
	$peers{$key} = [
		# 0 = Enabled
		"on",
		# 1 = Type
		"host",
		# 2 = Name
		$cgiparams{"NAME"},
		# 3 = Pubkey
		$cgiparams{"PUBLIC_KEY"},
		# 4 = Endpoint Address
		"",
		# 5 = Endpoint Port
		"",
		# 6 = Remote Subnets
		"", #&encode_subnets(@remote_subnets),
		# 7 = Remark
		&encode_remarks($cgiparams{"REMARKS"}),
		# 8 = Local Subnets
		&encode_subnets(@local_subnets),
		# 9 = PSK
		$cgiparams{"PSK"},
		# 10 = Keepalive
		0,
	];

	# Store the configuration
	&General::writehasharray("/var/ipfire/wireguard/peers", \%peers);

	# Reload if enabled
	if ($settings{'ENABLED'} eq "on") {
		&General::system("/usr/local/bin/wireguardctrl", "reload");
	}

} elsif ($cgiparams{"ACTION"} eq $Lang::tr{'add'}) {
	if ($cgiparams{"TYPE"} eq "net") {
		goto EDITNET;

	} elsif ($cgiparams{"TYPE"} eq "host") {
		goto EDITHOST;

	# Ask the user what type they want
	} else {
		goto ADD;
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

	my %checked = (
		"ENABLED" => ($settings{'ENABLED'} eq "on") ? "checked" : "",
	);

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

				<tr>
					<td>$Lang::tr{'wg client pool'}</td>
					<td>
						<input type="text" name="CLIENT_POOL" value="$settings{'CLIENT_POOL'}" />
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

	# Show a list with all peers
	&Header::opensection();

	# Fetch the dump
	my %dump = &dump($INTF);

	print <<END;
		<table class='tbl'>
			<tr>
				<th width='15%'>
					$Lang::tr{'name'}
				</th>

				<th width='20%' colspan='2'>
					$Lang::tr{'status'}
				</th>

				<th>
					$Lang::tr{'remark'}
				</th>

				<th width='10%' colspan='3'>
					$Lang::tr{'action'}
				</th>
			</tr>
END

	# Iterate through all peers...
	foreach my $key (sort { $peers{$a}[2] cmp $peers{$b}[2] } keys %peers) {
		my $enabled  = $peers{$key}[0];
		my $type     = $peers{$key}[1];
		my $name     = $peers{$key}[2];
		my $pubkey   = $peers{$key}[3];
		my $endpoint = $peers{$key}[4];
		my $port     = $peers{$key}[5];
		my $routes   = $peers{$key}[6];
		my $remarks  = &decode_remarks($peers{$key}[7]);

		my $connected = $Lang::tr{'capsclosed'};
		my $country   = "ZZ";
		my $location  = "";

		my $gif = ($enabled eq "on") ? "on.gif" : "off.gif";
		my @status = ("status");

		# Fetch the status of the peer (if possible)
		my $status = $dump{$pubkey} || ();

		# Fetch the actual endpoint
		my ($actual_endpoint, $actual_port) = split(/:/, $status->{"endpoint"}, 2);

		# WireGuard performs a handshake very two minutes, so we should be considered online then
		my $is_connected = (time - $status->{"latest-handshake"}) <= 120;

		# We are connected!
		if ($is_connected) {
			push(@status, "is-connected");

			$connected = $Lang::tr{'capsopen'};

			# If we have an endpoint lets lookup the country
			if ($actual_endpoint) {
				$country = &Location::Functions::lookup_country_code($actual_endpoint);

				# If we found a country, let's show it
				if ($country) {
					my $icon = &Location::Functions::get_flag_icon($country);

					$location = <<EOF;
						<a href="country.cgi#$country">
							<img src="$icon" border='0' align='absmiddle'
								alt='$country' title='$actual_endpoint:$actual_port - $country' />
						</a>
EOF
				}
			}

		# We are not connected...
		} else {
			push(@status, "is-disconnected");
		}

		# Escape remarks
		if ($remarks) {
			$remarks = &Header::escape($remarks);
		}

		print <<END;
			<tr>
				<th scope="row">
					$name
				</th>

				<td class="@status">
					$connected
				</td>

				<td class="@status">
					$location
				</td>

				<td>
					$remarks
				</td>

				<td class="text-center">
					<form method='post'>
						<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif'
							alt='$Lang::tr{'toggle enable disable'}' title='$Lang::tr{'toggle enable disable'}' />
						<input type='hidden' name='ACTION' value='$Lang::tr{'toggle enable disable'}' />
						<input type='hidden' name='KEY' value='$key' />
					</form>
				</td>

				<td class="text-center">
					<form method='post'>
						<input type='hidden' name='ACTION' value='$Lang::tr{'edit'}' />
						<input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif'
							alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' />
						<input type='hidden' name='KEY' value='$key' />
					</form>
				</td>

				<td class="text-center">
					<form method='post'>
						<input type='hidden' name='ACTION' value='$Lang::tr{'remove'}' />
						<input type='image'  name='$Lang::tr{'remove'}' src='/images/delete.gif'
							alt='$Lang::tr{'remove'}' title='$Lang::tr{'remove'}' />
						<input type='hidden' name='KEY' value='$key' />
					</form>
				</td>
			</tr>
END
	}

	print"</table>";

	# Show controls
    print <<END;
		<table class="form">
			<tr class="action">
				<td>
					<form method='post'>
						<input type='submit' name='ACTION' value='$Lang::tr{'add'}' />
					</form>
				</td>
			</tr>
		</table>
END
	&Header::closesection();
	&Header::closepage();

	exit(0);

ADD:
	# Send HTTP Headers
	&Header::showhttpheaders();

	# Open the page
	&Header::openpage($Lang::tr{'wireguard'}, 1, '');

	# Show any error messages
	&Header::errorbox(@errormessages);

	# Open a new box
	&Header::openbox('100%', '', $Lang::tr{'connection type'});

	print <<END;
		<form method="POST" ENCTYPE="multipart/form-data">
			<ul>
				<li>
					<label>
						<input type='radio' name='TYPE' value='host' checked />
						$Lang::tr{'host to net vpn'}
					</label>
				</li>

				<li>
					<label>
						<input type='radio' name='TYPE' value='net' />
						$Lang::tr{'net to net vpn'}
					</label>
				</li>
			</ul>

			<table class="form">
				<tr class="action">
					<td>
						<input type='submit' name='ACTION' value='$Lang::tr{'add'}' />
					</td>
				</tr>
			</table>
	    </form>
END

	&Header::closebox();
	&Header::closepage();

	exit(0);

EDITNET:
	# Send HTTP Headers
	&Header::showhttpheaders();

	# Open the page
	&Header::openpage($Lang::tr{'wireguard'}, 1, '');

	# Show any error messages
	&Header::errorbox(@errormessages);

	# Fetch the key
	my $key = $cgiparams{'KEY'};

	# Open a new box
	&Header::openbox('100%', '',
		(defined $key) ? $Lang::tr{'wg edit peer'} : $Lang::tr{'wg create peer'});

	# Set defaults
	unless (defined $key) {
		&General::set_defaults(\%cgiparams, {
			"ENDPOINT_PORT" => $DEFAULT_PORT,
			"LOCAL_SUBNETS" =>
				$Network::ethernet{"GREEN_NETADDRESS"}
				. "/" . $Network::ethernet{"GREEN_NETMASK"},
			"KEEPALIVE"		=> $DEFAULT_KEEPALIVE,
		});
	}

	print <<END;
		<form method="POST" ENCTYPE="multipart/form-data">
			<input type="hidden" name="ACTION" value="SAVE-PEER-NET">
			<input type="hidden" name="KEY" value="$cgiparams{'KEY'}">

			<table class="form">
				<tr>
					<td>
						$Lang::tr{'name'}
					</td>

					<td>
						<input type="text" name="NAME"
							value="$cgiparams{'NAME'}" required />
					</td>
				</tr>

				<tr>
					<td>
						$Lang::tr{'remarks'}
					</td>

					<td>
						<input type="text" name="REMARKS"
							value="$cgiparams{'REMARKS'}" />
					</td>
				</tr>
			</table>

			<h6>$Lang::tr{'endpoint'}</h6>

			<table class="form">
				<tr>
					<td>
						$Lang::tr{'endpoint address'}
					</td>

					<td>
						<input type="text" name="ENDPOINT_ADDRESS"
							value="$cgiparams{'ENDPOINT_ADDRESS'}" />
					</td>
				</tr>

				<tr>
					<td>
						$Lang::tr{'endpoint port'}
					</td>

					<td>
						<input type="number" name="ENDPOINT_PORT"
							value="$cgiparams{'ENDPOINT_PORT'}" required
							min="1" max="65535" placeholder="${DEFAULT_PORT}"/>
					</td>
				</tr>

				<tr>
					<td>$Lang::tr{'public key'}</td>
					<td>
						<input type="text" name="PUBLIC_KEY"
							value="$cgiparams{'PUBLIC_KEY'}" required />
					</td>
				</tr>

				<tr>
					<td>$Lang::tr{'wg pre-shared key (optional)'}</td>
					<td>
						<input type="text" name="PSK"
							value="$cgiparams{'PSK'}" />
					</td>
				</tr>

				<tr>
					<td>
						$Lang::tr{'wg keepalive interval'}
					</td>

					<td>
						<input type="number" name="KEEPALIVE"
							value="$cgiparams{'KEEPALIVE'}" required
							min="0" max="65535" />
					</td>
				</tr>
			</table>

			<h6>$Lang::tr{'routing'}</h6>

			<table class="form">
				<tr>
					<td>
						$Lang::tr{'local subnets'}
					</td>

					<td>
						<input type="text" name="LOCAL_SUBNETS"
							value="$cgiparams{'LOCAL_SUBNETS'}" required />
					</td>
				</tr>

				<tr>
					<td>
						$Lang::tr{'remote subnets'}
					</td>

					<td>
						<input type="text" name="REMOTE_SUBNETS"
							value="$cgiparams{'REMOTE_SUBNETS'}" required />
					</td>
				</tr>

				<tr class="action">
					<td colspan="2">
						<input type='submit' value='$Lang::tr{'save'}' />
					</td>
				</tr>
			</table>
	    </form>
END

	&Header::closebox();
	&Header::closepage();

	exit(0);

EDITHOST:
	# Send HTTP Headers
	&Header::showhttpheaders();

	# Open the page
	&Header::openpage($Lang::tr{'wireguard'}, 1, '');

	# Show any error messages
	&Header::errorbox(@errormessages);

	# Fetch the key
	my $key = $cgiparams{'KEY'};

	# Open a new box
	&Header::openbox('100%', '',
		(defined $key) ? $Lang::tr{'wg edit peer'} : $Lang::tr{'wg create peer'});

	# Set defaults
	unless (defined $key) {
		&General::set_defaults(\%cgiparams, {
			"LOCAL_SUBNETS" =>
				$Network::ethernet{"GREEN_NETADDRESS"}
				. "/" . $Network::ethernet{"GREEN_NETMASK"},
		});
	}

	print <<END;
		<form method="POST" ENCTYPE="multipart/form-data">
			<input type="hidden" name="ACTION" value="SAVE-PEER-HOST">
			<input type="hidden" name="KEY" value="$cgiparams{'KEY'}">

			<table class="form">
				<tr>
					<td>
						$Lang::tr{'name'}
					</td>

					<td>
						<input type="text" name="NAME"
							value="$cgiparams{'NAME'}" required />
					</td>
				</tr>

				<tr>
					<td>
						$Lang::tr{'remarks'}
					</td>

					<td>
						<input type="text" name="REMARKS"
							value="$cgiparams{'REMARKS'}" />
					</td>
				</tr>
			</table>

			<h6>$Lang::tr{'routing'}</h6>

			<table class="form">
				<tr>
					<td>
						$Lang::tr{'local subnets'}
					</td>

					<td>
						<input type="text" name="LOCAL_SUBNETS"
							value="$cgiparams{'LOCAL_SUBNETS'}" required />
					</td>
				</tr>

				<tr class="action">
					<td colspan="2">
						<input type='submit' value='$Lang::tr{'save'}' />
					</td>
				</tr>
			</table>
END

	&Header::closebox();
	&Header::closepage();

	exit(0);

# This function generates a set of keys for this host if none exist
sub generate_keys($) {
	my $force = shift || 0;

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
		$settings{"PRIVATE_KEY"} = &generate_private_key();

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

# Generates a new private key
sub generate_private_key() {
	# Generate a new private key
	my @output = &General::system_output("wg", "genkey");

	# Store the key
	foreach (@output) {
		chomp;

		return $_;
	}

	# Return undefined on error
	return undef;
}

# Takes a private key and derives the public key
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

	# Return undefined on error
	return undef;
}

sub dump($) {
	my $intf = shift;

	my %dump = ();
	my $lineno = 0;

	# Fetch the dump
	my @output = &General::system_output("/usr/local/bin/wireguardctrl", "dump", $intf);

	foreach my $line (@output) {
		# Increment the line numbers
		$lineno++;

		# Skip the first line
		next if ($lineno <= 1);

		# Split the line into its fields
		my @fields = split(/\t/, $line);

		# Create a new hash indexed by the public key
		$dump{$fields[0]} = {
			"psk"                  => $fields[1],
			"endpoint"             => $fields[2],
			"allowed-ips"          => $fields[3],
			"latest-handshake"     => $fields[4],
			"transfer-rx"          => $fields[5],
			"transfer-tx"          => $fields[6],
			"persistent-keepalive" => $fields[7],
		};
	}

	return %dump;
}

sub name_is_valid($) {
	my $name = shift;

	# The name must be between 1 and 63 characters
	if (length ($name) < 1 || length ($name) > 63) {
		return 0;
	}

	# Only valid characters are a-z, A-Z, 0-9, space and -
	if ($name !~ /^[a-zA-Z0-9 -]*$/) {
		return 0;
	}

	return 1;
}

sub name_is_free($) {
	my $name = shift;
	my $key  = shift || 0;

	foreach my $i (keys %peers) {
		# Skip the connection with ID
		next if ($key eq $i);

		# Return if we found a match
		return 0 if ($peers{$i}[2] eq $name);
	}

	return 1;
}

sub publickey_is_valid($) {
	my $key = shift;

	# Try to decode the key
	$key = &MIME::Base64::decode_base64($key);

	# All keys must be 32 bytes long
	return length($key) == 32;
}

sub keepalive_is_valid($) {
	my $keepalive = shift;

	# Must be a number
	return 0 unless ($keepalive =~ m/^[0-9]+$/);

	# Must be between 0 and 65535 (inclusive)
	return 0 if ($keepalive lt 0);
	return 0 if ($keepalive gt 65535);

	return 1;
}

sub encode_remarks($) {
	my $remarks = shift;

	# Encode to Base64
	$remarks = &MIME::Base64::encode_base64($remarks);

	# Remove the trailing newline
	chomp($remarks);

	return $remarks;
}

sub decode_remarks($) {
	my $remarks = shift;

	# Decode from base64
	return &MIME::Base64::decode_base64($remarks);
}

sub encode_subnets($) {
	my @subnets = @_;

	# Join subnets together separated by |
	return join("|", @subnets);
}

sub decode_subnets($) {
	my $subnets = shift;

	# Split the string
	my @subnets = split(/\|/, $subnets);

	return @subnets;
}
