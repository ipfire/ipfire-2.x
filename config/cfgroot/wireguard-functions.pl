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

package Wireguard;

use strict;
use MIME::Base64;

require "/var/ipfire/general-functions.pl";
require "/var/ipfire/network-functions.pl";

our $DEFAULT_PORT		= 51820;
our $DEFAULT_KEEPALIVE	= 25;
our $INTF               = "wg0";

# Read the global configuration
our %settings = ();
&General::readhash("/var/ipfire/wireguard/settings", \%settings);

# Read all peers
our %peers = ();
&General::readhasharray("/var/ipfire/wireguard/peers", \%peers);

# Set any defaults
&General::set_defaults(\%settings, {
	"ENABLED"    => "off",
	"PORT"       => $DEFAULT_PORT,
	"CLIENT_DNS" => $Network::ethernet{'GREEN_ADDRESS'},
});

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

sub load_peer($) {
	my $key = shift;

	my $type = $peers{$key}[1];

	my %peer = (
		"ENABLED"               => $peers{$key}[0],
		"TYPE"                  => $type,
		"NAME"                  => $peers{$key}[2],
		"PUBLIC_KEY"            => $peers{$key}[3],
		"PRIVATE_KEY"           => $peers{$key}[4],
		"PORT"                  => $peers{$key}[5],
		"ENDPOINT_ADDR"         => $peers{$key}[6],
		"ENDPOINT_PORT"         => $peers{$key}[7],
		($type eq "host") ? "CLIENT_ADDRESS" : "REMOTE_SUBNETS"
		                        => &decode_subnets($peers{$key}[8]),
		"REMARKS"               => &decode_remarks($peers{$key}[9]),
		"LOCAL_SUBNETS"         => &decode_subnets($peers{$key}[10]),
		"PSK"                   => $peers{$key}[11],
		"KEEPALIVE"             => $peers{$key}[12],
	);

	return %peer;
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

sub key_is_valid($) {
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

	my @formatted = ();

	# wg only handles the CIDR notation
	foreach my $subnet (@subnets) {
		my $netaddr = &Network::get_netaddress($subnet);
		my $prefix  = &Network::get_prefix($subnet);

		next unless (defined $netaddr && defined $prefix);

		push(@formatted, "${netaddr}/${prefix}");
	}

	# Join subnets together separated by |
	return join("|", @formatted);
}

sub decode_subnets($) {
	my $subnets = shift;

	# Split the string
	my @subnets = split(/\|/, $subnets);

	return @subnets;
}

sub pool_is_in_use($) {
	my $pool = shift;

	foreach my $key (keys %peers) {
		my $type    = $peers{$key}[1];
		my $address = $peers{$key}[6];

		# Check if a host is using an IP address from the pool
		if ($type eq "host" && &Network::ip_address_in_network($address, $pool)) {
			return 1;
		}
	}

	# No match found
	return 0;
}

# Takes the pool and an optional limit of up to how many addresses to return
sub free_pool_addresses($$) {
	my $pool = shift;
	my $limit = shift || 0;

	my @used_addresses = ();
	my @free_addresses = ();

	# Collect all used addresses
	foreach my $key (keys %peers) {
		my $type    = $peers{$key}[1];
		my $address = $peers{$key}[6];

		# Only check hosts
		next if ($type ne "host");

		push(@used_addresses, &Network::ip2bin($address));
	}

	# Fetch the first address
	my $address = &Network::get_netaddress($pool);

	# Fetch the last address
	my $broadcast = &Network::get_broadcast($pool);
	$broadcast = &Network::ip2bin($broadcast);

	# Walk through all addresses excluding the first and last address.
	# No technical reason, we just don't want to confuse people.
	OUTER: for (my $i = &Network::ip2bin($address) + 1; $i < $broadcast; $i++) {
		# Skip any addresses that already in use
		foreach my $used_address (@used_addresses) {
			next OUTER if ($i == $used_address);
		}

		push(@free_addresses, &Network::bin2ip($i));

		# Check limit
		last if ($limit > 0 && scalar @free_addresses >= $limit);
	}

	return @free_addresses;
}

sub generate_peer_configuration($) {
	my $key = shift;

	# Load the peer
	my %peer = &load_peer($key);

	# Return if we could not find the peer
	return undef unless (%peer);

	my @allowed_ips = ();
	my @dns = ();

	# Convert all subnets into CIDR notation
	foreach my $subnet ($peer{'LOCAL_SUBNETS'}) {
		my $netaddress = &Network::get_netaddress($subnet);
		my $prefix     = &Network::get_prefix($subnet);

		# Skip invalid subnets
		next if (!defined $netaddress || !defined $prefix);

		push(@allowed_ips, "${netaddress}/${prefix}");
	}

	my $endpoint = $settings{'ENDPOINT'};

	# If no endpoint is set, we fall back to the FQDN of the firewall
	if ($endpoint eq "") {
		$endpoint = $General::mainsettings{'HOSTNAME'} . "." . $General::mainsettings{'DOMAINNAME'};
	}

	my $port = $settings{'PORT'};

	# Fetch any DNS servers for hosts
	if ($peer{'TYPE'} eq 'host') {
		@dns = split(/\|/, $settings{'CLIENT_DNS'});
	}

	my @conf = (
		"[Interface]",
		"PrivateKey = $peer{'PRIVATE_KEY'}",
		"Address = $peer{'CLIENT_ADDRESS'}",
	);

	# Optionally add DNS servers
	if (scalar @dns) {
		push(@conf, "DNS = " . join(", ", @dns));
	}

	# Finish the [Interface] section
	push(@conf, "");

	# Add peer configuration
	push(@conf, (
		"[Peer]",
		"Endpoint = ${endpoint}:${port}",
		"PublicKey = $settings{'PUBLIC_KEY'}",
		"PresharedKey = $peer{'PSK'}",
		"AllowedIPs = " . join(", ", @allowed_ips),
		"PersistentKeepalive = $DEFAULT_KEEPALIVE",
	));

	return join("\n", @conf);
}

sub parse_configuration($) {
	my $fh = shift;

	my %peer = ();

	# Collect any errors
	my @errormessages = ();

	my $section = undef;
	my $key = undef;
	my $val = undef;

	while (<$fh>) {
		# Remove line breaks
		chomp;

		# Search for section headers
		if ($_ =~ m/^\[(\w+)\]$/) {
			$section = $1;
			next;

		# Search for key = value lines
		} elsif ($_ =~ m/^(\w+)\s+=\s+(.*)$/) {
			# Skip anything before the first section header
			next unless (defined $section);

			# Store keys and values
			$key = $1;
			$val = $2;

		# Skip any unhandled lines
		} else {
			next;
		}

		# Interface section
		if ($section eq "Interface") {
			# Address
			if ($key eq "Address") {
				if (&Network::check_ip_address($val)) {
					$peer{'CLIENT_ADDRESS'} = $val;
				} else {
					push(@errormessages, $Lang::tr{'invalid ip address'});
				}

			# PrivateKey
			} elsif ($key eq "PrivateKey") {
				if (&key_is_valid($val)) {
					$peer{'PRIVATE_KEY'} = $val;
				} else {
					push(@errormessages, $Lang::tr{'malformed private key'});
				}
			}

		# Peer section
		} elsif ($section eq "Peer") {
			# PublicKey
			if ($key eq "PublicKey") {
				if (&key_is_valid($val)) {
					$peer{'PUBLIC_KEY'} = $val;
				} else {
					push(@errormessages, $Lang::tr{'malformed public key'});
				}

			# PresharedKey
			} elsif ($key eq "PresharedKey") {
				if (&key_is_valid($val)) {
					$peer{'PSK'} = $val;
				} else {
					push(@errormessages, $Lang::tr{'malformed preshared key'});
				}

			# AllowedIPs
			} elsif ($key eq "AllowedIPs") {
				my @networks = split(/,/, $val);

				# Check if all networks are valid
				foreach my $network (@networks) {
					unless (&Network::check_subnet($network)) {
						push(@errormessages, $Lang::tr{'invalid network'} . " $network");
					}
				}

				$peer{'REMOTE_SUBNETS'} = join(/, /, @networks);
			# Endpoint
			} elsif ($key eq "Endpoint") {
				my $address = $val;
				my $port = $DEFAULT_PORT;

				# Try to separate the port (if any)
				if ($val =~ m/^(.*):(\d+)$/) {
					$address = $1;
					$port    = $2;
				}

				# Check if we have a valid IP address
				if (&Network::check_ip_address($address)) {
					# nothing

				# Otherwise this fails
				} else {
					push(@errormessages, $Lang::tr{'invalid endpoint address'});
					next;
				}

				# Store the values
				$peer{'ENDPOINT_ADDRESS'} = $address;
				$peer{'ENDPOINT_PORT'}    = $port;

			# PersistentKeepalive
			} elsif ($key eq "PersistentKeepalive") {
				# Must be an integer
				if ($val =~ m/^(\d+)$/) {
					$peer{'KEEPALIVE'} = $1;
				} else {
					push(@errormessages, $Lang::tr{'invalid keepalive interval'});
				}
			}
		}
	}

	return %peer, @errormessages;
}

1;
