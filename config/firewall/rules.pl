#!/usr/bin/perl -w
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2013 Alexander Marx <amarx@ipfire.org>                        #
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

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "/usr/lib/firewall/firewall-lib.pl";

# Set to one to enable debugging mode.
my $DEBUG = 0;

my $IPTABLES = "iptables --wait";

# iptables chains
my $CHAIN_INPUT           = "INPUTFW";
my $CHAIN_FORWARD         = "FORWARDFW";
my $CHAIN_OUTPUT          = "OUTGOINGFW";
my $CHAIN                 = $CHAIN_FORWARD;
my $CHAIN_NAT_SOURCE      = "NAT_SOURCE";
my $CHAIN_NAT_DESTINATION = "NAT_DESTINATION";
my $CHAIN_MANGLE_NAT_DESTINATION_FIX = "NAT_DESTINATION";
my @VALID_CHAINS          = ($CHAIN_INPUT, $CHAIN_FORWARD, $CHAIN_OUTPUT);

my @PROTOCOLS = ("tcp", "udp", "icmp", "igmp", "ah", "esp", "gre", "ipv6", "ipip");
my @PROTOCOLS_WITH_PORTS = ("tcp", "udp");

my @VALID_TARGETS = ("ACCEPT", "DROP", "REJECT");

my %fwdfwsettings=();
my %defaultNetworks=();
my %configfwdfw=();;
my %customgrp=();
my %configinputfw=();
my %configoutgoingfw=();
my %confignatfw=();
my %aliases=();
my @p2ps=();

my $configfwdfw		= "${General::swroot}/firewall/config";
my $configinput	    = "${General::swroot}/firewall/input";
my $configoutgoing  = "${General::swroot}/firewall/outgoing";
my $p2pfile			= "${General::swroot}/firewall/p2protocols";
my $configgrp		= "${General::swroot}/fwhosts/customgroups";
my $netsettings		= "${General::swroot}/ethernet/settings";

&General::readhash("${General::swroot}/firewall/settings", \%fwdfwsettings);
&General::readhash("$netsettings", \%defaultNetworks);
&General::readhasharray($configfwdfw, \%configfwdfw);
&General::readhasharray($configinput, \%configinputfw);
&General::readhasharray($configoutgoing, \%configoutgoingfw);
&General::readhasharray($configgrp, \%customgrp);
&General::get_aliases(\%aliases);

# MAIN
&main();

sub main {
	# Flush all chains.
	&flush();

	# Reload firewall rules.
	&preparerules();

	# Load P2P block rules.
	&p2pblock();

	# Reload firewall policy.
	run("/usr/sbin/firewall-policy");
}

sub run {
	# Executes or prints the given shell command.
	my $command = shift;

	if ($DEBUG) {
		print "$command\n";
	} else {
		system "$command";

		if ($?) {
			print_error("ERROR: $command");
		}
	}
}

sub print_error {
	my $message = shift;

	print STDERR "$message\n";
}

sub print_rule {
	my $hash = shift;

	print "\nRULE:";

	my $i = 0;
	foreach (@$hash) {
		printf("  %2d: %s", $i++, $_);
	}
	print "\n";
}

sub flush {
	run("$IPTABLES -F $CHAIN_INPUT");
	run("$IPTABLES -F $CHAIN_FORWARD");
	run("$IPTABLES -F $CHAIN_OUTPUT");
	run("$IPTABLES -t nat -F $CHAIN_NAT_SOURCE");
	run("$IPTABLES -t nat -F $CHAIN_NAT_DESTINATION");
	run("$IPTABLES -t mangle -F $CHAIN_MANGLE_NAT_DESTINATION_FIX");
}

sub preparerules {
	if (! -z  "${General::swroot}/firewall/config"){
		&buildrules(\%configfwdfw);
	}
	if (! -z  "${General::swroot}/firewall/input"){
		&buildrules(\%configinputfw);
	}
	if (! -z  "${General::swroot}/firewall/outgoing"){
		&buildrules(\%configoutgoingfw);
	}
}

sub buildrules {
	my $hash = shift;

	foreach my $key (sort {$a <=> $b} keys %$hash) {
		# Skip disabled rules.
		next unless ($$hash{$key}[2] eq 'ON');

		if ($DEBUG) {
			print_rule($$hash{$key});
		}

		# Check if the target is valid.
		my $target = $$hash{$key}[0];
		if (!$target ~~ @VALID_TARGETS) {
			print_error("Invalid target '$target' for rule $key");
			next;
		}

		# Check if the chain is valid.
		my $chain = $$hash{$key}[1];
		if (!$chain ~~ @VALID_CHAINS) {
			print_error("Invalid chain '$chain' in rule $key");
			next;
		}

		# Collect all sources.
		my @sources = &get_addresses($hash, $key, "src");

		# Collect all destinations.
		my @destinations = &get_addresses($hash, $key, "tgt");

		# Check if logging should be enabled.
		my $LOG = ($$hash{$key}[17] eq 'ON');

		# Check if NAT is enabled and initialize variables, that we use for that.
		my $NAT = ($$hash{$key}[28] eq 'ON');
		my $NAT_MODE;
		if ($NAT) {
			$NAT_MODE = uc($$hash{$key}[31]);
		}

		# Set up time constraints.
		my @time_options = ();
		if ($$hash{$key}[18] eq 'ON') {
			push(@time_options, ("-m", "time"));

			# Select all days of the week this match is active.
			my @weekdays = ();
			if ($$hash{$key}[19] ne '') {
				push (@weekdays, "Mon");
			}
			if ($$hash{$key}[20] ne '') {
				push (@weekdays, "Tue");
			}
			if ($$hash{$key}[21] ne '') {
				push (@weekdays, "Wed");
			}
			if ($$hash{$key}[22] ne '') {
				push (@weekdays, "Thu");
			}
			if ($$hash{$key}[23] ne '') {
				push (@weekdays, "Fri");
			}
			if ($$hash{$key}[24] ne '') {
				push (@weekdays, "Sat");
			}
			if ($$hash{$key}[25] ne '') {
				push (@weekdays, "Sun");
			}
			if (@weekdays) {
				push(@time_options, ("--weekdays", join(",", @weekdays)));
			}

			# Convert start time.
			my $time_start = &format_time($$hash{$key}[26]);
			if ($time_start) {
				push(@time_options, ("--timestart", $time_start));
			}

			# Convert end time.
			my $time_stop = &format_time($$hash{$key}[27]);
			if ($time_stop) {
				push(@time_options, ("--timestop", $time_stop));
			}
		}

		# Check which protocols are used in this rule and so that we can
		# later group rules by protocols.
		my @protocols = &get_protocols($hash, $key);
		if (!@protocols) {
			print_error("Invalid protocol configuration for rule $key");
			next;
		}

		foreach my $protocol (@protocols) {
			# Check if the given protocol is supported.
			if (($protocol ne "all") && (!$protocol ~~ @PROTOCOLS)) {
				print_error("Protocol $protocol is not supported (rule $key)");
				next;
			}

			# Prepare protocol options (like ICMP types, ports, etc...).
			my @protocol_options = &get_protocol_options($hash, $key, $protocol);

			# Check if this protocol knows ports.
			my $protocol_has_ports = ($protocol ~~ @PROTOCOLS_WITH_PORTS);

			foreach my $source (@sources) {
				foreach my $destination (@destinations) {
					# Skip invalid rules.
					next if (!$source || !$destination || ($destination eq "none"));

					# Array with iptables arguments.
					my @options = ();

					# Append protocol.
					if ($protocol ne "all") {
						push(@options, ("-p", $protocol));
						push(@options, @protocol_options);
					}

					# Prepare source options.
					my @source_options = ();
					if ($source =~ /mac/) {
						push(@source_options, $source);
					} else {
						push(@source_options, ("-s", $source));
					}

					# Prepare destination options.
					my @destination_options = ("-d", $destination);

					# Add time constraint options.
					push(@options, @time_options);

					# Process NAT rules.
					if ($NAT) {
						my $nat_address = &get_nat_address($$hash{$key}[29]);

						# Skip NAT rules if the NAT address is unknown
						# (i.e. no internet connection has been established, yet).
						next unless ($nat_address);

						# Destination NAT
						if ($NAT_MODE eq "DNAT") {
							# Make port-forwardings useable from the internal networks.
							&add_dnat_mangle_rules($nat_address, @options);

							my @nat_options = @options;
							push(@nat_options, @source_options);
							push(@nat_options, ("-d", $nat_address));

							my ($dnat_address, $dnat_mask) = split("/", $destination);
							@destination_options = ("-d", $dnat_address);

							if ($protocol_has_ports) {
								my $dnat_port = &get_dnat_target_port($hash, $key);

								if ($dnat_port) {
									$dnat_address .= ":$dnat_port";
								}
							}

							if ($LOG) {
								run("$IPTABLES -t nat -A $CHAIN_NAT_DESTINATION @nat_options -j LOG --log-prefix 'DNAT'");
							}
							run("$IPTABLES -t nat -A $CHAIN_NAT_DESTINATION @nat_options -j DNAT --to-destination $dnat_address");

						# Source NAT
						} elsif ($NAT_MODE eq "SNAT") {
							my @nat_options = @options;

							push(@nat_options, @source_options);
							push(@nat_options, @destination_options);

							if ($LOG) {
								run("$IPTABLES -t nat -A $CHAIN_NAT_SOURCE @nat_options -j LOG --log-prefix 'SNAT'");
							}
							run("$IPTABLES -t nat -A $CHAIN_NAT_SOURCE @nat_options -j SNAT --to-source $nat_address");
						}
					}

					push(@options, @source_options);
					push(@options, @destination_options);

					# Insert firewall rule.
					if ($LOG && !$NAT) {
						run("$IPTABLES -A $chain @options -j LOG");
					}
					run("$IPTABLES -A $chain @options -j $target");
				}
			}
		}
	}
}

sub get_external_interface() {
	open(IFACE, "/var/ipfire/red/iface") or return "";
	my $iface = <IFACE>;
	close(IFACE);

	return $iface;
}

sub get_external_address() {
	open(ADDR, "/var/ipfire/red/local-ipaddress") or return "";
	my $address = <ADDR>;
	close(ADDR);

	return $address;
}

sub get_alias {
	my $id = shift;

	foreach my $alias (sort keys %aliases) {
		if ($id eq $alias) {
			return $aliases{$alias};
		}
	}
}

sub get_nat_address {
	my $zone = shift;

	# Any static address of any zone.
	if ($zone eq "RED" || $zone eq "GREEN" || $zone eq "ORANGE" || $zone eq "BLUE") {
		return $defaultNetworks{$zone . "_ADDRESS"};

	} elsif ($zone eq "Default IP") {
		return &get_external_address();

	} else {
		return &get_alias($zone);
	}

	print_error("Could not find NAT address");
}

# Formats the given timestamp into the iptables format which is "hh:mm" UTC.
sub format_time {
	my $val = shift;

	# Convert the given time into minutes.
	my $minutes = &time_convert_to_minutes($val);

	# Move the timestamp into UTC.
	$minutes += &time_utc_offset();

	# Make sure $minutes is between 00:00 and 23:59.
	if ($minutes < 0) {
		$minutes += 1440;
	}

	if ($minutes > 1440) {
		$minutes -= 1440;
	}

	# Format as hh:mm.
	return sprintf("%02d:%02d", $minutes / 60, $minutes % 60);
}

# Calculates the offsets in minutes from the local timezone to UTC.
sub time_utc_offset {
	my @localtime = localtime(time);
	my @gmtime = gmtime(time);

	return ($gmtime[2] * 60 + $gmtime[1] % 60) - ($localtime[2] * 60 + $localtime[1] % 60);
}

# Takes a timestamp like "14:00" and converts it into minutes since midnight.
sub time_convert_to_minutes {
	my ($hrs, $min) = split(":", shift);

	return ($hrs * 60) + $min;
}

sub p2pblock {
	my $P2PSTRING = "";
	my $DO;
	open( FILE, "< $p2pfile" ) or die "Unable to read $p2pfile";
	@p2ps = <FILE>;
	close FILE;
	my $CMD = "-m ipp2p";
	foreach my $p2pentry (sort @p2ps) {
		my @p2pline = split( /\;/, $p2pentry );
		if ( $fwdfwsettings{'POLICY'} eq 'MODE1' ) {
			$DO = "ACCEPT";
			if ("$p2pline[2]" eq "on") {
				$P2PSTRING = "$P2PSTRING --$p2pline[1]";
			}
		}else {
			$DO = "RETURN";
			if ("$p2pline[2]" eq "off") {
				$P2PSTRING = "$P2PSTRING --$p2pline[1]";
			}
		}
	}

	if($P2PSTRING) {
		run("$IPTABLES -A FORWARDFW $CMD $P2PSTRING -j $DO");
	}
}

sub get_addresses {
	my $hash = shift;
	my $key  = shift;
	my $type = shift;

	my @addresses = ();
	my $addr_type;
	my $value;
	my $group_name;

	if ($type eq "src") {
		$addr_type = $$hash{$key}[3];
		$value = $$hash{$key}[4];

	} elsif ($type eq "tgt") {
		$addr_type = $$hash{$key}[5];
		$value = $$hash{$key}[6];
	}

	if ($addr_type ~~ ["cust_grp_src", "cust_grp_tgt"]) {
		foreach my $grp (sort {$a <=> $b} keys %customgrp) {
			if ($customgrp{$grp}[0] eq $value) {
				my @address = &get_address($customgrp{$grp}[3], $customgrp{$grp}[2], $type);

				if (@address) {
					push(@addresses, @address);
				}
			}
		}
	} else {
		my @address = &get_address($addr_type, $value, $type);

		if (@address) {
			push(@addresses, @address);
		}
	}

	return @addresses;
}

sub get_address {
	my $key   = shift;
	my $value = shift;
	my $type  = shift;

	my @ret = ();

	# If the user manually typed an address, we just check if it is a MAC
	# address. Otherwise, we assume that it is an IP address.
	if ($key ~~ ["src_addr", "tgt_addr"]) {
		if (&General::validmac($value)) {
			push(@ret, "-m mac --mac-source $value");
		} else {
			push(@ret, $value);
		}

	# If a default network interface (GREEN, BLUE, etc.) is selected, we
	# try to get the corresponding address of the network.
	} elsif ($key ~~ ["std_net_src", "std_net_tgt", "Standard Network"]) {
		my $external_interface = &get_external_interface();

		my $network_address = &fwlib::get_std_net_ip($value, $external_interface);
		if ($network_address) {
			push(@ret, $network_address);
		}

	# Custom networks.
	} elsif ($key ~~ ["cust_net_src", "cust_net_tgt", "Custom Network"]) {
		my $network_address = &fwlib::get_net_ip($value);
		if ($network_address) {
			push(@ret, $network_address);
		}

	# Custom hosts.
	} elsif ($key ~~ ["cust_host_src", "cust_host_tgt", "Custom Host"]) {
		my $host_address = &fwlib::get_host_ip($value, $type);
		if ($host_address) {
			push(@ret, $host_address);
		}

	# OpenVPN networks.
	} elsif ($key ~~ ["ovpn_net_src", "ovpn_net_tgt", "OpenVPN static network"]) {
		my $network_address = &fwlib::get_ovpn_net_ip($value, 1);
		if ($network_address) {
			push(@ret, $network_address);
		}

	# OpenVPN hosts.
	} elsif ($key ~~ ["ovpn_host_src", "ovpn_host_tgt", "OpenVPN static host"]) {
		my $host_address = &fwlib::get_ovpn_host_ip($value, 33);
		if ($host_address) {
			push(@ret, $host_address);
		}

	# OpenVPN N2N.
	} elsif ($key ~~ ["ovpn_n2n_src", "ovpn_n2n_tgt", "OpenVPN N-2-N"]) {
		my $network_address = &fwlib::get_ovpn_n2n_ip($value, 11);
		if ($network_address) {
			push(@ret, $network_address);
		}

	# IPsec networks.
	} elsif ($key ~~ ["ipsec_net_src", "ipsec_net_tgt", "IpSec Network"]) {
		my $network_address = &fwlib::get_ipsec_net_ip($value, 11);
		if ($network_address) {
			push(@ret, $network_address);
		}

	# The firewall's own IP addresses.
	} elsif ($key ~~ ["ipfire", "ipfire_src"]) {
		# ALL
		if ($value eq "ALL") {
			push(@ret, "0/0");

		# GREEN
		} elsif ($value eq "GREEN") {
			push(@ret, $defaultNetworks{"GREEN_ADDRESS"});

		# BLUE
		} elsif ($value eq "BLUE") {
			push(@ret, $defaultNetworks{"BLUE_ADDRESS"});

		# ORANGE
		} elsif ($value eq "ORANGE") {
			push(@ret, $defaultNetworks{"ORANGE_ADDRESS"});

		# RED
		} elsif ($value ~~ ["RED", "RED1"]) {
			my $address = &get_external_address();
			if ($address) {
				push(@ret, $address);
			}

		# Aliases
		} else {
			my %alias = &get_alias($value);
			if (%alias) {
				push(@ret, $alias{"IPT"});
			}
		}

	# If nothing was selected, we assume "any".
	} else {
		push(@ret, "0/0");
	}

	return @ret;
}

sub get_protocols {
	my $hash = shift;
	my $key = shift;

	my $uses_source_ports = ($$hash{$key}[7] eq "ON");
	my $uses_services = ($$hash{$key}[11] eq "ON");

	my @protocols = ();

	# Rules which don't have source ports or services (like ICMP, ESP, ...).
	if (!$uses_source_ports && !$uses_services) {
		push(@protocols, $$hash{$key}[8]);

	# Rules which either use ports or services.
	} elsif ($uses_source_ports || $uses_services) {
		# Check if service group or service
		if ($$hash{$key}[14] eq 'cust_srv') {
			push(@protocols, &fwlib::get_srv_prot($$hash{$key}[15]));

		} elsif($$hash{$key}[14] eq 'cust_srvgrp'){
			my $protos = &fwlib::get_srvgrp_prot($$hash{$key}[15]);
			push(@protocols, split(",", $protos));

		} else {
			# Fetch the protocol for this rule.
			my $protocol = lc($$hash{$key}[8]);

			# Fetch source and destination ports for this rule.
			my $source_ports = $$hash{$key}[10];
			my $destination_ports = $$hash{$key}[15];

			# Check if ports are set for protocols which do not support ports.
			if (!($protocol ~~ @PROTOCOLS_WITH_PORTS) && ($source_ports || $destination_ports)) {
				print_error("$protocol does not support ports");
				return ();
			}

			push(@protocols, $protocol);
		}
	}

	# Remove all empty elements
	@protocols = map { $_ ? $_ : () } @protocols;

	# If no protocol has been defined, we assume "all".
	if (!@protocols) {
		push(@protocols, "all");
	}

	# Make all protocol names lowercase.
	@protocols = map { lc } @protocols;

	return @protocols;
}

sub get_protocol_options {
	my $hash = shift;
	my $key  = shift;
	my $protocol = shift;
	my @options = ();

	# Process source ports.
	my $use_src_ports = ($$hash{$key}[7] eq "ON");
	my $src_ports     = $$hash{$key}[10];

	if ($use_src_ports && $src_ports) {
		push(@options, &format_ports($src_ports, "src"));
	}

	# Process destination ports.
	my $use_dst_ports  = ($$hash{$key}[11] eq "ON");
	my $use_dnat       = (($$hash{$key}[28] eq "ON") && ($$hash{$key}[31] eq "dnat"));

	if ($use_dst_ports) {
		my $dst_ports_mode = $$hash{$key}[14];
		my $dst_ports      = $$hash{$key}[15];

		if (($dst_ports_mode eq "TGT_PORT") && $dst_ports) {
			if ($use_dnat && $$hash{$key}[30]) {
				$dst_ports = $$hash{$key}[30];
			}
			push(@options, &format_ports($dst_ports, "dst"));

		} elsif ($dst_ports_mode eq "cust_srv") {
			if ($protocol eq "ICMP") {
				push(@options, ("--icmp-type", &fwlib::get_srv_port($dst_ports, 3, "ICMP")));
			} else {
				$dst_ports = &fwlib::get_srv_port($dst_ports, 1, uc($protocol));
				push(@options, &format_ports($dst_ports, "dst"));
			}

		} elsif ($dst_ports_mode eq "cust_srvgrp") {
			push(@options, &fwlib::get_srvgrp_port($dst_ports, uc($protocol)));
		}
	}

	# Check if a single ICMP type is selected.
	if (!$use_src_ports && !$use_dst_ports && $protocol eq "icmp") {
		my $icmp_type = $$hash{$key}[9];

		if (($icmp_type ne "All ICMP-Types") && $icmp_type) {
			push(@options, ("--icmp-type", $icmp_type));
		}
	}

	return @options;
}

sub format_ports {
	my $ports = shift;
	my $type = shift;

	my $arg;
	if ($type eq "src") {
		$arg = "--sport";
	} elsif ($type eq "dst") {
		$arg = "--dport";
	}

	my @options = ();

	if ($ports =~ /\|/) {
		$ports =~ s/\|/,/g;
		push(@options, ("-m", "multiport"));
	}

	if ($ports) {
		push(@options, ($arg, $ports));
	}

	return @options;
}

sub get_dnat_target_port {
	my $hash = shift;
	my $key  = shift;

	if ($$hash{$key}[14] eq "TGT_PORT") {
		my $port = $$hash{$key}[15];
		my $external_port = $$hash{$key}[30];

		if ($external_port && ($port ne $external_port)) {
			return $$hash{$key}[15];
		}
	}
}

sub add_dnat_mangle_rules {
	my $nat_address = shift;
	my @options = @_;

	my $mark = 0;
	foreach my $zone ("GREEN", "BLUE", "ORANGE") {
		$mark++;

		# Skip rule if not all required information exists.
		next unless (exists $defaultNetworks{$zone . "_NETADDRESS"});
		next unless (exists $defaultNetworks{$zone . "_NETMASK"});

		my @mangle_options = @options;

		my $netaddress = $defaultNetworks{$zone . "_NETADDRESS"};
		$netaddress .= "/" . $defaultNetworks{$zone . "_NETMASK"};

		push(@mangle_options, ("-s", $netaddress, "-d", $nat_address));
		push(@mangle_options, ("-j", "MARK", "--set-mark", $mark));

		run("$IPTABLES -t mangle -A $CHAIN_MANGLE_NAT_DESTINATION_FIX @mangle_options");
	}
}
