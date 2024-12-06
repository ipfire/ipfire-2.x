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
use Imager::QRCode;
use MIME::Base64;

require "/var/ipfire/general-functions.pl";
require "${General::swroot}/header.pl";
require "${General::swroot}/location-functions.pl";
require "${General::swroot}/wireguard-functions.pl";

my %cgiparams = ();
my @errormessages = ();

# Generate keys
&Wireguard::generate_keys();

# Fetch CGI parameters
&Header::getcgihash(\%cgiparams, {'wantfile' => 1, 'filevar' => 'FH'});

# Save on main page
if ($cgiparams{"ACTION"} eq $Lang::tr{'save'}) {
	my @client_dns = ();

	# Store whether enabled or not
	if ($cgiparams{'ENABLED'} =~ m/^(on|off)?$/) {
		$Wireguard::settings{'ENABLED'} = $cgiparams{'ENABLED'};
	}

	# Check endpoint
	if (&General::validfqdn($cgiparams{'ENDPOINT'}) || &Network::check_ip_address($cgiparams{'ENDPOINT'}) || ($cgiparams{'ENDPOINT'} eq '')) {
		$Wireguard::settings{'ENDPOINT'} = $cgiparams{'ENDPOINT'};
	} else {
		push(@errormessages, $Lang::tr{'invalid endpoint'});
	}

	# Check port
	if (&General::validport($cgiparams{'PORT'})) {
		$Wireguard::settings{'PORT'} = $cgiparams{'PORT'};
	} else {
		push(@errormessages, $Lang::tr{'invalid port'});
	}

	# Check client pool
	if (&Wireguard::pool_is_in_use($Wireguard::settings{'CLIENT_POOL'})) {
		# Ignore any changes if the pool is in use
	} elsif (&Network::check_subnet($cgiparams{'CLIENT_POOL'})) {
		$Wireguard::settings{'CLIENT_POOL'} = $cgiparams{'CLIENT_POOL'};
	} elsif ($cgiparams{'CLIENT_POOL'} ne '') {
		push(@errormessages, $Lang::tr{'wg invalid client pool'});
	}

	# Check client DNS
	if (defined $cgiparams{'CLIENT_DNS'}) {
		@client_dns = split(/,/, $cgiparams{'CLIENT_DNS'});

		foreach my $dns (@client_dns) {
			unless (&Network::check_ip_address($dns)) {
				push(@errormessages, "$Lang::tr{'wg invalid client dns'}: ${dns}");
			}
		}

		# Store CLIENT_DNS
		$Wireguard::settings{'CLIENT_DNS'} = join("|", @client_dns);
	}

	# Don't continue on error
	goto MAIN if (scalar @errormessages);

	# Store the configuration file
	&General::writehash("/var/ipfire/wireguard/settings", \%Wireguard::settings);

	# Start if enabled
	if ($Wireguard::settings{'ENABLED'} eq "on") {
		&General::system("/usr/local/bin/wireguardctrl", "start");
	} else {
		&General::system("/usr/local/bin/wireguardctrl", "stop");
	}

# Delete an existing peer
} elsif ($cgiparams{"ACTION"} eq $Lang::tr{'remove'}) {
	my $key = $cgiparams{'KEY'};

	# Fail if the peer does not exist
	unless (exists $Wireguard::peers{$key}) {
		push(@errormessages, $Lang::tr{'wg peer does not exist'});
		goto MAIN;
	}

	# Delete the peer
	delete($Wireguard::peers{$key});

	# Store the configuration
	&General::writehasharray("/var/ipfire/wireguard/peers", \%Wireguard::peers);

	# Reload if enabled
	if ($Wireguard::settings{'ENABLED'} eq "on") {
		&General::system("/usr/local/bin/wireguardctrl", "start");
	}

# Edit an existing peer
} elsif ($cgiparams{"ACTION"} eq $Lang::tr{'edit'}) {
	my $key = $cgiparams{'KEY'};

	# Fail if the peer does not exist
	unless (exists $Wireguard::peers{$key}) {
		push(@errormessages, $Lang::tr{'wg peer does not exist'});
		goto MAIN;
	}

	# Fetch type
	my $type = $Wireguard::peers{$key}[1];

	my @remote_subnets = &Wireguard::decode_subnets($Wireguard::peers{$key}[8]);
	my @local_subnets  = &Wireguard::decode_subnets($Wireguard::peers{$key}[10]);

	# Flush CGI parameters & load configuration
	%cgiparams = (
		"KEY"				=> $key,
		"ENABLED"			=> $Wireguard::peers{$key}[0],
		"TYPE"				=> $Wireguard::peers{$key}[1],
		"NAME"				=> $Wireguard::peers{$key}[2],
		"PUBLIC_KEY"		=> $Wireguard::peers{$key}[3],
		"PRIVATE_KEY"		=> $Wireguard::peers{$key}[4],
		"PORT"				=> $Wireguard::peers{$key}[5],
		"ENDPOINT_ADDRESS"	=> $Wireguard::peers{$key}[6],
		"ENDPOINT_PORT"		=> $Wireguard::peers{$key}[7],
		"REMOTE_SUBNETS"	=> join(", ", @remote_subnets),
		"REMARKS"			=> &MIME::Base64::decode_base64($Wireguard::peers{$key}[9]),
		"LOCAL_SUBNETS"		=> join(", ", @local_subnets),
		"PSK"				=> $Wireguard::peers{$key}[11],
		"KEEPALIVE"			=> $Wireguard::peers{$key}[12],
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
	my $key = $cgiparams{'KEY'} || &General::findhasharraykey(\%Wireguard::peers);

	# Check if the name is valid
	unless (&Wireguard::name_is_valid($cgiparams{"NAME"})) {
		push(@errormessages, $Lang::tr{'wg invalid name'});
	}

	# Check if the name is free
	unless (&Wireguard::name_is_free($cgiparams{"NAME"}, $key)) {
		push(@errormessages, $Lang::tr{'wg name is already used'});
	}

	# Check the public key
	unless (&Wireguard::key_is_valid($cgiparams{'PUBLIC_KEY'})) {
		push(@errormessages, $Lang::tr{'wg invalid public key'});
	}

	# Check private key
	#if ($cgiparams{'PRIVATE_KEY'} eq '') {
	#		# The private key may be empty
	#} elsif (!&Wireguard::key_is_valid($cgiparams{'PRIVATE_KEY'})) {
	#		push(@errormessages, $Lang::tr{'wg invalid private key'});
	#}

	# Check PSK
	if ($cgiparams{'PSK'} eq '') {
		# The PSK may be empty
	} elsif (!&Wireguard::key_is_valid($cgiparams{'PSK'})) {
		push(@errormessages, $Lang::tr{'wg invalid psk'});
	}

	# Select a new random port if none given
	if ($cgiparams{'PORT'} eq "") {
		$cgiparams{'PORT'} = &Wireguard::get_free_port();

	# If a port was given we check that it is valid
	} elsif (!&General::validport($cgiparams{'PORT'})) {
		push(@errormessages, $LANG::tr{'invalid port'});
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
	unless (&Wireguard::keepalive_is_valid($cgiparams{'KEEPALIVE'})) {
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
	$Wireguard::peers{$key} = [
		# 0 = Enabled
		"on",
		# 1 = Type
		"net",
		# 2 = Name
		$cgiparams{"NAME"},
		# 3 = Public Key
		$cgiparams{"PUBLIC_KEY"},
		# 4 = Private Key
		$cgiparams{"PRIVATE_KEY"},
		# 5 = Port
		$cgiparams{"PORT"},
		# 6 = Endpoint Address
		$cgiparams{"ENDPOINT_ADDRESS"},
		# 7 = Endpoint Port
		$cgiparams{"ENDPOINT_PORT"},
		# 8 = Remote Subnets
		&Wireguard::encode_subnets(@remote_subnets),
		# 9 = Remark
		&Wireguard::encode_remarks($cgiparams{"REMARKS"}),
		# 10 = Local Subnets
		&Wireguard::encode_subnets(@local_subnets),
		# 11 = PSK
		$cgiparams{"PSK"} || "",
		# 12 = Keepalive
		$cgiparams{"KEEPALIVE"} || 0,
	];

	# Store the configuration
	&General::writehasharray("/var/ipfire/wireguard/peers", \%Wireguard::peers);

	# Reload if enabled
	if ($Wireguard::settings{'ENABLED'} eq "on") {
		&General::system("/usr/local/bin/wireguardctrl", "start");
	}

} elsif ($cgiparams{"ACTION"} eq "SAVE-PEER-HOST") {
	my @free_addresses = ();
	my @local_subnets = ();

	# Fetch or allocate a new key
	my $key = $cgiparams{'KEY'} || &General::findhasharraykey(\%Wireguard::peers);

	# Is this a new connection?
	my $is_new = !exists $Wireguard::peers{$key};

	# Check if the name is valid
	unless (&Wireguard::name_is_valid($cgiparams{"NAME"})) {
		push(@errormessages, $Lang::tr{'wg invalid name'});
	}

	# Check if the name is free
	unless (&Wireguard::name_is_free($cgiparams{"NAME"}, $key)) {
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

	# Check if we have address space left in the pool
	if ($is_new) {
		# Fetch the next free address
		@free_addresses = &Wireguard::free_pool_addresses($Wireguard::settings{'CLIENT_POOL'}, 1);

		# Fail if we ran out of addresses
		if (scalar @free_addresses == 0) {
			push(@errormessages, $Lang::tr{'wg no more free addresses in pool'});
		}
	}

	# If there are any errors, we go back to the editor
	goto EDITHOST if (scalar @errormessages);

	# Generate things for a new peer
	if ($is_new) {
		# Generate a new private key
		$cgiparams{"PRIVATE_KEY"} = &Wireguard::generate_private_key();

		# Derive the public key
		$cgiparams{"PUBLIC_KEY"} = &Wireguard::derive_public_key($cgiparams{"PRIVATE_KEY"});

		# Generate a new PSK
		$cgiparams{"PSK"} = &Wireguard::generate_private_key();

		# Fetch a free address from the pool
		foreach (@free_addresses) {
			$cgiparams{'CLIENT_ADDRESS'} = $_;
			last;
		}

	# Fetch some configuration parts
	} else {
		$cgiparams{"PUBLIC_KEY"}     = $Wireguard::peers{$key}[3];
		$cgiparams{"PRIVATE_KEY"}    = $Wireguard::peers{$key}[4];
		$cgiparams{'CLIENT_ADDRESS'} = $Wireguard::peers{$key}[8];
		$cgiparams{"PSK"}            = $Wireguard::peers{$key}[11];
	}

	# Save the connection
	$Wireguard::peers{$key} = [
		# 0 = Enabled
		"on",
		# 1 = Type
		"host",
		# 2 = Name
		$cgiparams{"NAME"},
		# 3 = Public Key
		$cgiparams{"PUBLIC_KEY"},
		# 4 = Private Key
		$cgiparams{"PRIVATE_KEY"},
		# 5 = Port
		"",
		# 6 = Endpoint Address
		"",
		# 7 = Endpoint Port
		"",
		# 8 = Remote Subnets
		$cgiparams{'CLIENT_ADDRESS'},
		# 9 = Remark
		&Wireguard::encode_remarks($cgiparams{"REMARKS"}),
		# 10 = Local Subnets
		&Wireguard::encode_subnets(@local_subnets),
		# 11 = PSK
		$cgiparams{"PSK"},
		# 12 = Keepalive
		0,
	];

	# Store the configuration
	&General::writehasharray("/var/ipfire/wireguard/peers", \%Wireguard::peers);

	# Reload if enabled
	if ($Wireguard::settings{'ENABLED'} eq "on") {
		&General::system("/usr/local/bin/wireguardctrl", "start");
	}

	# Show the client configuration when creating a new peer
	&show_peer_configuration($key) if ($is_new);

} elsif ($cgiparams{"ACTION"} eq $Lang::tr{'add'}) {
	if ($cgiparams{"TYPE"} eq "net") {
		# Generate a new private key
		$cgiparams{'PRIVATE_KEY'} = &Wireguard::generate_private_key();

		# Generate a new PSK
		$cgiparams{"PSK"} = &Wireguard::generate_private_key();

		goto EDITNET;

	} elsif ($cgiparams{"TYPE"} eq "host") {
		goto EDITHOST;

	} elsif ($cgiparams{"TYPE"} eq "import") {
		# Parse the configuration file
		(%cgiparams, @errormessages) = &Wireguard::parse_configuration($cgiparams{'FH'});

		# We basically don't support importing RW connections, so we always
		# need to go and show the N2N editor.
		goto EDITNET;

	# Ask the user what type they want
	} else {
		goto ADD;
	}

# Toggle Enable/Disable
} elsif ($cgiparams{'ACTION'} eq 'TOGGLE-ENABLE-DISABLE') {
	my $key = $cgiparams{'KEY'} || 0;

	if (exists $Wireguard::peers{$key}) {
		if ($Wireguard::peers{$key}[0] eq "on") {
			$Wireguard::peers{$key}[0] = "off";
		} else {
			$Wireguard::peers{$key}[0] = "on";
		}
	}

	# Store the configuration
	&General::writehasharray("/var/ipfire/wireguard/peers", \%Wireguard::peers);

	# Reload if enabled
	if ($Wireguard::settings{'ENABLED'} eq "on") {
		&General::system("/usr/local/bin/wireguardctrl", "start");
	}

# Download configuration
} elsif ($cgiparams{'ACTION'} eq 'CONFIG') {
	my $key = $cgiparams{'KEY'} || 0;

	# Load the peer
	my %peer = &Wireguard::load_peer($key);

	# Make the filename for files
	my $filename = &Header::normalize($peer{'NAME'}) . ".conf";

	# Generate the client configuration
	my $config = &Wireguard::generate_peer_configuration($key);

	# Send the configuration
	if (defined $config) {
		print "Content-Type: application/octet-stream\n";
		print "Content-Disposition: filename=\"${filename}\"\n";
		print "\n";
		print $config;

	# If there is no configuration, we return 404
	} else {
		&CGI::header(status => 404);
	}

	exit(0);

# Show the configuration as QR code
} elsif ($cgiparams{'ACTION'} eq 'CONFIG-QRCODE') {
	my $key = $cgiparams{'KEY'} || 0;

	# Show the configuration
	&show_peer_configuration($key);

	exit(0);
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
		"ENABLED" => ($Wireguard::settings{'ENABLED'} eq "on") ? "checked" : "",
	);

	my %readonly = (
		"CLIENT_POOL" => (&Wireguard::pool_is_in_use($Wireguard::settings{'CLIENT_POOL'}) ? "readonly" : ""),
	);

	my $client_dns = $Wireguard::settings{'CLIENT_DNS'} =~ s/\|/, /gr;

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
					<td>$Lang::tr{'endpoint'}</td>
					<td>
						<input type="text" name="ENDPOINT" value="$Wireguard::settings{'ENDPOINT'}" placeholder="$General::mainsettings{'HOSTNAME'}.$General::mainsettings{'DOMAINNAME'}" />
					</td>
				</tr>

				<tr>
					<td>$Lang::tr{'port'}</td>
					<td>
						<input type="number" name="PORT" value="$Wireguard::settings{'PORT'}"
							min="1024" max="65535" />
					</td>
				</tr>
			</table>

			<h6>$Lang::tr{'wg host to net client settings'}</h6>

			<table class="form">
				<tr>
					<td>$Lang::tr{'wg client pool'}</td>
					<td>
						<input type="text" name="CLIENT_POOL"
							value="$Wireguard::settings{'CLIENT_POOL'}" $readonly{'CLIENT_POOL'} />
					</td>
				</tr>

				<tr>
					<td>$Lang::tr{'wg dns'}</td>
					<td>
						<input type="text" name="CLIENT_DNS"
							value="$client_dns" />
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

	if (%Wireguard::peers) {
		print <<END;
			<table class='tbl'>
				<tr>
					<th width='15%'>
						$Lang::tr{'name'}
					</th>

					<th>
						$Lang::tr{'remark'}
					</th>

					<th width='20%' colspan='2'>
						$Lang::tr{'status'}
					</th>

					<th width='10%' colspan='5'>
						$Lang::tr{'action'}
					</th>
				</tr>
END

		# Dump all RW peers
		my %DUMP = &Wireguard::dump("wg0");

		# Iterate through all peers...
		foreach my $key (sort { $Wireguard::peers{$a}[2] cmp $Wireguard::peers{$b}[2] } keys %Wireguard::peers) {
			my $enabled  = $Wireguard::peers{$key}[0];
			my $type     = $Wireguard::peers{$key}[1];
			my $name     = $Wireguard::peers{$key}[2];
			my $pubkey   = $Wireguard::peers{$key}[3];
			#my $privkey  = $Wireguard::peers{$key}[4]
			#my $port     = $Wireguard::peers{$key}[5];
			my $endpoint = $Wireguard::peers{$key}[6];
			#my $endpport = $Wireguard::peers{$key}[7];
			my $routes   = $Wireguard::peers{$key}[8];
			my $remarks  = &Wireguard::decode_remarks($Wireguard::peers{$key}[9]);

			my $connected = $Lang::tr{'capsclosed'};
			my $country   = "ZZ";
			my $location  = "";

			my $gif = ($enabled eq "on") ? "on.gif" : "off.gif";
			my @status = ("status");

			# Fetch the dump
			my %dump = ($type eq "net") ? &Wireguard::dump("wg$key") : %DUMP;

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

					<td>
						$remarks
					</td>
END

			if ($location) {
				print <<END;
					<td class="@status">
						$connected
					</td>

					<td class="@status">
						$location
					</td>
END
			} else {
				print <<END;
					<td class="@status" colspan="2">
						$connected
					</td>
END
			}

			print <<END;
					<td class="text-center">
						<form method='post'>
							<input type='image' name='$Lang::tr{'wg show configuration qrcode'}' src='/images/qr-code.png'
								alt='$Lang::tr{'wg show configuration qrcode'}' title='$Lang::tr{'wg show configuration qrcode'}' />
							<input type='hidden' name='ACTION' value='CONFIG-QRCODE' />
							<input type='hidden' name='KEY' value='$key' />
						</form>
					</td>

					<td class="text-center">
						<form method='post'>
							<input type='image' name='$Lang::tr{'wg download configuration'}' src='/images/media-floppy.png'
								alt='$Lang::tr{'wg download configuration'}' title='$Lang::tr{'wg download configuration'}' />
							<input type='hidden' name='ACTION' value='CONFIG' />
							<input type='hidden' name='KEY' value='$key' />
						</form>
					</td>

					<td class="text-center">
						<form method='post'>
							<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif'
								alt='$Lang::tr{'toggle enable disable'}' title='$Lang::tr{'toggle enable disable'}' />
							<input type='hidden' name='ACTION' value='TOGGLE-ENABLE-DISABLE' />
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
	}

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

	my %disabled = (
		"host" => "",
	);

	# If there is no CLIENT_POOL configured, we disable the option
	if ($Wireguard::settings{'CLIENT_POOL'} eq "") {
		$disabled{"host"} = "disabled";

	# If the client pool is out of addresses, we do the same
	} else {
		my @free_addresses = &Wireguard::free_pool_addresses($Wireguard::settings{'CLIENT_POOL'}, 1);

		if (scalar @free_addresses == 0) {
			$disabled{"host"} = "disabled";
		}
	}

	print <<END;
		<form method="POST" ENCTYPE="multipart/form-data">
			<ul>
				<li>
					<label>
						<input type='radio' name='TYPE' value='host' $disabled{'host'} />
						$Lang::tr{'host to net vpn'}
					</label>
				</li>

				<li>
					<label>
						<input type='radio' name='TYPE' value='net' checked />
						$Lang::tr{'net to net vpn'}
					</label>
				</li>

				<li>
					<label>
						<input type='radio' name='TYPE' value='import' />
						$Lang::tr{'import connection'}
					</label>

					<input type='file' name='FH' />
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

	# Derive our own public key
	my $public_key = &Wireguard::derive_public_key($cgiparams{'PRIVATE_KEY'});

	# Open a new box
	&Header::openbox('100%', '',
		(defined $key) ? $Lang::tr{'wg edit net-to-net peer'} : $Lang::tr{'wg create net-to-net peer'});

	# Set defaults
	unless (defined $key) {
		&General::set_defaults(\%cgiparams, {
			"ENDPOINT_PORT" => $Wireguard::DEFAULT_PORT,
			"LOCAL_SUBNETS" =>
				$Network::ethernet{"GREEN_NETADDRESS"}
				. "/" . $Network::ethernet{"GREEN_NETMASK"},
			"KEEPALIVE"     => $Wireguard::DEFAULT_KEEPALIVE,
		});
	}

	print <<END;
		<form method="POST" ENCTYPE="multipart/form-data">
			<input type="hidden" name="ACTION" value="SAVE-PEER-NET">
			<input type="hidden" name="KEY" value="$cgiparams{'KEY'}">

			<input type="hidden" name="PRIVATE_KEY" value="$cgiparams{'PRIVATE_KEY'}">

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

				<tr>
					<td>
						$Lang::tr{'public key'}
					</td>

					<td>
						<input type="text" value="$public_key" readonly />
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
							min="1" max="65535" placeholder="${Wireguard::DEFAULT_PORT}"/>
					</td>
				</tr>

				<tr>
					<td>
						$Lang::tr{'local port'}
					</td>

					<td>
						<input type="number" name="PORT"
							value="$cgiparams{'PORT'}" min="1" max="65535"
							placeholder="$Lang::tr{'wg leave empty to automatically select'}" />
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
		(defined $key) ? $Lang::tr{'wg edit host-to-net peer'} : $Lang::tr{'wg create host-to-net peer'});

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
						$Lang::tr{'allowed subnets'}
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

sub show_peer_configuration($) {
	my $key = shift;

	# The generated QR code
	my $qrcode;

	# Send HTTP Headers
	&Header::showhttpheaders();

	# Open the page
	&Header::openpage($Lang::tr{'wireguard'}, 1, '');

	# Load the peer
	my %peer = &Wireguard::load_peer($key);

	# Generate the client configuration
	my $config = &Wireguard::generate_peer_configuration($key);

	# Create a QR code generator
	my $qrgen = Imager::QRCode->new(
		size          => 6,
		margin        => 0,
		version       => 0,
		level         => 'M',
		mode          => '8-bit',
		casesensitive => 1,
		lightcolor    => Imager::Color->new(255, 255, 255),
		darkcolor     => Imager::Color->new(0, 0, 0),
	);

	# Encode the configuration
	my $img = $qrgen->plot("$config");

	# Encode the image as PNG
	$img->write(data => \$qrcode, type => "png") or die $img->errstr;

	# Encode the image as bas64
	$qrcode = &MIME::Base64::encode_base64($qrcode);

	# Encode the configuration as Base64
	$config = &MIME::Base64::encode_base64($config);

	# Open a new box
	&Header::openbox('100%', '', "$Lang::tr{'wg peer configuration'}: $peer{'NAME'}");

	# Make the filename for files
	my $filename = &Header::normalize($peer{'NAME'}) . ".conf";

	print <<END;
		<div class="text-center">
			<p>
				<img src="data:image/png;base64,${qrcode}" alt="$Lang::tr{'qr code'}">
			</p>

			<p>
				$Lang::tr{'wg scan the qr code'}
			</p>

			<p>
				<a href="data:text/plain;base64,${config}" download="${filename}">
					$Lang::tr{'wg download configuration file'}
				</a>
			</p>

			<p>
				<form method="GET" action="">
					<button type="submit">$Lang::tr{'done'}</button>
				</form>
			</p>
		</div>
END

	&Header::closebox();
	&Header::closepage();

	exit(0);
}
