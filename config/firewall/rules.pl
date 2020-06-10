#!/usr/bin/perl -w
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2019  IPFire Team  <info@ipfire.org>                     #
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
use experimental 'smartmatch';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/geoip-functions.pl";
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
my @ANY_ADDRESSES         = ("0.0.0.0/0.0.0.0", "0.0.0.0/0", "0/0");

my @PROTOCOLS = ("tcp", "udp", "icmp", "igmp", "ah", "esp", "gre", "ipv6", "ipip");
my @PROTOCOLS_WITH_PORTS = ("tcp", "udp");

my @VALID_TARGETS = ("ACCEPT", "DROP", "REJECT");

my %fwdfwsettings=();
my %fwoptions = ();
my %defaultNetworks=();
my %configfwdfw=();;
my %customgrp=();
my %configinputfw=();
my %configoutgoingfw=();
my %confignatfw=();
my %geoipsettings = (
	"GEOIPBLOCK_ENABLED" => "off"
);

my @p2ps=();

my $configfwdfw		= "${General::swroot}/firewall/config";
my $configinput	    = "${General::swroot}/firewall/input";
my $configoutgoing  = "${General::swroot}/firewall/outgoing";
my $p2pfile			= "${General::swroot}/firewall/p2protocols";
my $geoipfile		= "${General::swroot}/firewall/geoipblock";
my $configgrp		= "${General::swroot}/fwhosts/customgroups";
my $netsettings		= "${General::swroot}/ethernet/settings";

&General::readhash("${General::swroot}/firewall/settings", \%fwdfwsettings);
&General::readhash("${General::swroot}/optionsfw/settings", \%fwoptions);
&General::readhash("$netsettings", \%defaultNetworks);
&General::readhasharray($configfwdfw, \%configfwdfw);
&General::readhasharray($configinput, \%configinputfw);
&General::readhasharray($configoutgoing, \%configoutgoingfw);
&General::readhasharray($configgrp, \%customgrp);

# Check if the geoip settings file exists
if (-e "$geoipfile") {
	# Read settings file
	&General::readhash("$geoipfile", \%geoipsettings);
}

# Get all GeoIP locations.
my @locations = &fwlib::get_geoip_locations();

my @log_limit_options = &make_log_limit_options();

my $POLICY_INPUT_ALLOWED   = 0;
my $POLICY_FORWARD_ALLOWED = ($fwdfwsettings{"POLICY"} eq "MODE2");
my $POLICY_OUTPUT_ALLOWED  = ($fwdfwsettings{"POLICY1"} eq "MODE2");

my $POLICY_INPUT_ACTION    = $fwoptions{"FWPOLICY2"};
my $POLICY_FORWARD_ACTION  = $fwoptions{"FWPOLICY"};
my $POLICY_OUTPUT_ACTION   = $fwoptions{"FWPOLICY1"};

# MAIN
&main();

sub main {
	# Gather locations which should be exported.
	my @locations_to_export = &gather_locations_to_export();

	# Flush all chains.
	&flush();

	# Flush exported locations.
	&GeoIP::flush_exported_locations();

	# Export required locations.
	&GeoIP::export_locations(\@locations_to_export);

	# Prepare firewall rules.
	if (! -z  "${General::swroot}/firewall/input"){
		&buildrules(\%configinputfw);
	}
	if (! -z  "${General::swroot}/firewall/outgoing"){
		&buildrules(\%configoutgoingfw);
	}
	if (! -z  "${General::swroot}/firewall/config"){
		&buildrules(\%configfwdfw);
	}

	# Load P2P block rules.
	&p2pblock();

	# Load GeoIP block rules.
	&geoipblock();

	# Reload firewall policy.
	run("/usr/sbin/firewall-policy");

	#Reload firewall.local if present
	if ( -f '/etc/sysconfig/firewall.local'){
		run("/etc/sysconfig/firewall.local reload");
	}
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

sub count_elements {
	my $hash = shift;

	return scalar @$hash;
}

sub flush {
	run("$IPTABLES -F $CHAIN_INPUT");
	run("$IPTABLES -F $CHAIN_FORWARD");
	run("$IPTABLES -F $CHAIN_OUTPUT");
	run("$IPTABLES -t nat -F $CHAIN_NAT_SOURCE");
	run("$IPTABLES -t nat -F $CHAIN_NAT_DESTINATION");
	run("$IPTABLES -t mangle -F $CHAIN_MANGLE_NAT_DESTINATION_FIX");
}

sub buildrules {
	my $hash = shift;

	# Search for targets that need to be specially handled when adding
	# forwarding rules. Additional rules will automatically get inserted
	# into the INPUT/OUTPUT chains for these targets.
	my @special_input_targets = ();
	if (!$POLICY_FORWARD_ALLOWED) {
		push(@special_input_targets, "ACCEPT");
	}

	if ($POLICY_INPUT_ACTION eq "DROP") {
		push(@special_input_targets, ("ACCEPT", "REJECT"));
	} elsif ($POLICY_INPUT_ACTION eq "REJECT") {
		push(@special_input_targets, ("ACCEPT", "DROP"));
	}

	my @special_output_targets = ();
	if ($POLICY_OUTPUT_ALLOWED) {
		push(@special_output_targets, ("DROP", "REJECT"));
	} else {
		push(@special_output_targets, "ACCEPT");

		if ($POLICY_OUTPUT_ACTION eq "DROP") {
			push(@special_output_targets, ("ACCEPT", "REJECT"));
		} elsif ($POLICY_OUTPUT_ACTION eq "REJECT") {
			push(@special_output_targets, ("ACCEPT", "DROP"));
		}
	}

	foreach my $key (sort {$a <=> $b} keys %$hash) {
		# Skip disabled rules.
		next unless ($$hash{$key}[2] eq 'ON');

		# Count number of elements in this line
		my $elements = &count_elements($$hash{$key});

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
		my @sources = &fwlib::get_addresses($hash, $key, "src");

		# Collect all destinations.
		my @destinations = &fwlib::get_addresses($hash, $key, "tgt");

		# True if the destination is the firewall itself.
		my $destination_is_firewall = ($$hash{$key}[5] eq "ipfire");

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

		# Concurrent connection limit
		my @ratelimit_options = ();

		if (($elements ge 34) && ($$hash{$key}[32] eq 'ON')) {
			my $conn_limit = $$hash{$key}[33];

			if ($conn_limit ge 1) {
				push(@ratelimit_options, ("-m", "connlimit"));

				# Use the the entire source IP address
				push(@ratelimit_options, "--connlimit-saddr");
				push(@ratelimit_options, ("--connlimit-mask", "32"));

				# Apply the limit
				push(@ratelimit_options, ("--connlimit-upto", $conn_limit));
			}
		}

		# Ratelimit
		if (($elements ge 37) && ($$hash{$key}[34] eq 'ON')) {
			my $rate_limit = "$$hash{$key}[35]/$$hash{$key}[36]";

			if ($rate_limit) {
				push(@ratelimit_options, ("-m", "limit"));
				push(@ratelimit_options, ("--limit", $rate_limit));
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
			my @protocol_options = &get_protocol_options($hash, $key, $protocol, 0);

			# Check if this protocol knows ports.
			my $protocol_has_ports = ($protocol ~~ @PROTOCOLS_WITH_PORTS);

			foreach my $src (@sources) {
				# Skip invalid source.
				next unless (defined $src);
				next unless ($src);

				# Sanitize source.
				my $source = @$src[0];
				if ($source ~~ @ANY_ADDRESSES) {
					$source = "";
				}

				my $source_intf = @$src[1];

				foreach my $dst (@destinations) {
					# Skip invalid rules.
					next unless (defined $dst);
					next if (!$dst || ($dst eq "none"));

					# Sanitize destination.
					my $destination = @$dst[0];
					if ($destination ~~ @ANY_ADDRESSES) {
						$destination = "";
					}

					my $destination_intf = @$dst[1];

					# Array with iptables arguments.
					my @options = ();

					# Append protocol.
					if ($protocol ne "all") {
						push(@options, @protocol_options);
					}

					# Prepare source options.
					my @source_options = ();
					if ($source =~ /mac/) {
						push(@source_options, $source);
					} elsif ($source =~ /-m geoip/) {
						push(@source_options, $source);
					} elsif($source) {
						push(@source_options, ("-s", $source));
					}

					# Prepare destination options.
					my @destination_options = ();
					if ($destination =~ /-m geoip/) {
						push(@destination_options,  $destination);
					} elsif ($destination) {
						push(@destination_options, ("-d", $destination));
					}

					# Add source and destination interface to the filter rules.
					# These are supposed to help filtering forged packets that originate
					# from BLUE with an IP address from GREEN for instance.
					my @source_intf_options = ();
					if ($source_intf) {
						push(@source_intf_options, ("-i", $source_intf));
					}

					my @destination_intf_options = ();
					if ($destination_intf) {
						push(@destination_intf_options, ("-o", $destination_intf));
					}

					# Add time constraint options.
					push(@options, @time_options);

					# Add ratelimiting option
					push(@options, @ratelimit_options);

					my $firewall_is_in_source_subnet = 1;
					if ($source) {
						$firewall_is_in_source_subnet = &firewall_is_in_subnet($source);
					}

					my $firewall_is_in_destination_subnet = 1;
					if ($destination) {
						$firewall_is_in_destination_subnet = &firewall_is_in_subnet($destination);
					}

					# Process NAT rules.
					if ($NAT) {
						my $nat_address = &fwlib::get_nat_address($$hash{$key}[29], $source);

						# Skip NAT rules if the NAT address is unknown
						# (i.e. no internet connection has been established, yet).
						next unless ($nat_address);

						# Destination NAT
						if ($NAT_MODE eq "DNAT") {
							my @nat_options = ();
							if ($protocol ne "all") {
								my @nat_protocol_options = &get_protocol_options($hash, $key, $protocol, 1);
								push(@nat_options, @nat_protocol_options);
							}
							push(@nat_options, @time_options);

							# Make port-forwardings useable from the internal networks.
							my @internal_addresses = &fwlib::get_internal_firewall_ip_addresses(1);
							unless ($nat_address ~~ @internal_addresses) {
								&add_dnat_mangle_rules($nat_address, $source_intf, @nat_options);
							}

							push(@nat_options, @source_options);
							push(@nat_options, ("-d", $nat_address));

							my $dnat_port;
							if ($protocol_has_ports) {
								$dnat_port = &get_dnat_target_port($hash, $key);
							}

							my @nat_action_options = ();

							# Use iptables REDIRECT
							my $use_redirect = ($destination_is_firewall && !$destination && $protocol_has_ports && $dnat_port);
							if ($use_redirect) {
								push(@nat_action_options, ("-j", "REDIRECT", "--to-ports", $dnat_port));

							# Use iptables DNAT
							} else {
								if ($destination_is_firewall && !$destination) {
									$destination = &fwlib::get_external_address();
								}
								next unless ($destination);

								my ($dnat_address, $dnat_mask) = split("/", $destination);
								@destination_options = ("-d", $dnat_address);

								if ($protocol_has_ports) {
									my $dnat_port = &get_dnat_target_port($hash, $key);

									if ($dnat_port) {
										$dnat_address .= ":$dnat_port";
									}
								}

								push(@nat_action_options, ("-j", "DNAT", "--to-destination", $dnat_address));
							}

							if ($LOG) {
								run("$IPTABLES -t nat -A $CHAIN_NAT_DESTINATION @nat_options @log_limit_options -j LOG --log-prefix 'DNAT '");
							}
							run("$IPTABLES -t nat -A $CHAIN_NAT_DESTINATION @nat_options @nat_action_options");

						# Source NAT
						} elsif ($NAT_MODE eq "SNAT") {
							my @snat_options = ( "-m", "policy", "--dir", "out", "--pol", "none" );
							my @nat_options = @options;

							# Get addresses for the configured firewall interfaces.
							my @local_addresses = &fwlib::get_internal_firewall_ip_addresses(1);

							# Check if the nat_address is one of the local addresses.
							foreach my $local_address (@local_addresses) {
								if ($nat_address eq $local_address) {
									# Clear SNAT options.
									@snat_options = ();

									# Finish loop.
									last;
								}
							}

							push(@nat_options, @destination_intf_options);
							push(@nat_options, @source_options);
							push(@nat_options, @destination_options);

							if ($LOG) {
								run("$IPTABLES -t nat -A $CHAIN_NAT_SOURCE @nat_options @snat_options @log_limit_options -j LOG --log-prefix 'SNAT '");
							}
							run("$IPTABLES -t nat -A $CHAIN_NAT_SOURCE @nat_options @snat_options -j SNAT --to-source $nat_address");
						}
					}

					push(@options, @source_options);
					push(@options, @destination_options);

					# Insert firewall rule.
					if ($LOG) {
						run("$IPTABLES -A $chain @options @source_intf_options @destination_intf_options @log_limit_options -j LOG --log-prefix '$chain '");
					}
					run("$IPTABLES -A $chain @options @source_intf_options @destination_intf_options -j $target");

					# Handle forwarding rules and add corresponding rules for firewall access.
					if ($chain eq $CHAIN_FORWARD) {
						# If the firewall is part of the destination subnet and access to the destination network
						# is granted/forbidden for any network that the firewall itself is part of, we grant/forbid access
						# for the firewall, too.
						if ($firewall_is_in_destination_subnet && ($target ~~ @special_input_targets)) {
							if ($LOG) {
								run("$IPTABLES -A $CHAIN_INPUT @options @source_intf_options @log_limit_options -j LOG --log-prefix '$CHAIN_INPUT '");
							}
							run("$IPTABLES -A $CHAIN_INPUT @options @source_intf_options -j $target");
						}

						# Likewise.
						if ($firewall_is_in_source_subnet && ($target ~~ @special_output_targets)) {
							if ($LOG) {
								run("$IPTABLES -A $CHAIN_OUTPUT @options @destination_intf_options @log_limit_options -j LOG --log-prefix '$CHAIN_OUTPUT '");
							}
							run("$IPTABLES -A $CHAIN_OUTPUT @options @destination_intf_options -j $target");
						}
					}
				}
			}
		}
	}
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
	open(FILE, "<$p2pfile") or die "Unable to read $p2pfile";
	my @protocols = ();
	foreach my $p2pentry (<FILE>) {
		my @p2pline = split(/\;/, $p2pentry);
		next unless ($p2pline[2] eq "off");

		push(@protocols, "--$p2pline[1]");
	}
	close(FILE);

	run("$IPTABLES -F P2PBLOCK");
	if (@protocols) {
		run("$IPTABLES -A P2PBLOCK -m ipp2p @protocols -j DROP");
	}
}

sub geoipblock {
	# Flush iptables chain.
	run("$IPTABLES -F GEOIPBLOCK");

	# If geoip blocking is not enabled, we are finished here.
	if ($geoipsettings{'GEOIPBLOCK_ENABLED'} ne "on") {
		# Exit submodule. Process remaining script.
		return;
	}

	# Loop through all supported geoip locations and
	# create iptables rules, if blocking this country
	# is enabled.
	foreach my $location (@locations) {
		if(exists $geoipsettings{$location} && $geoipsettings{$location} eq "on") {
			run("$IPTABLES -A GEOIPBLOCK -m geoip --src-cc $location -j DROP");
		}
	}
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
	my $nat_options_wanted = shift;
	my @options = ();

	# Nothing to do if no protocol is specified.
	if ($protocol eq "all") {
		return @options;
	} else {
		push(@options, ("-p", $protocol));
	}

	if ($protocol ~~ @PROTOCOLS_WITH_PORTS) {
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
				if ($nat_options_wanted && $use_dnat && $$hash{$key}[30]) {
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
	}

	# Check if a single ICMP type is selected.
	if ($protocol eq "icmp") {
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
	my $interface = shift;
	my @options = @_;

	my $mark = 0;
	foreach my $zone ("GREEN", "BLUE", "ORANGE") {
		$mark++;

		# Skip rule if not all required information exists.
		next unless (exists $defaultNetworks{$zone . "_NETADDRESS"});
		next unless (exists $defaultNetworks{$zone . "_NETMASK"});

		next if ($interface && $interface ne $defaultNetworks{$zone . "_DEV"});

		my @mangle_options = @options;

		my $netaddress = $defaultNetworks{$zone . "_NETADDRESS"};
		$netaddress .= "/" . $defaultNetworks{$zone . "_NETMASK"};

		push(@mangle_options, ("-s", $netaddress, "-d", $nat_address));
		push(@mangle_options, ("-j", "MARK", "--set-mark", $mark));

		run("$IPTABLES -t mangle -A $CHAIN_MANGLE_NAT_DESTINATION_FIX @mangle_options");
	}
}

sub make_log_limit_options {
	my @options = ("-m", "limit");

	# Maybe we should get this from the configuration.
	my $limit = 10;

	# We limit log messages to $limit messages per second.
	push(@options, ("--limit", "$limit/second"));

	# And we allow bursts of 2x $limit.
	push(@options, ("--limit-burst", $limit * 2));

	return @options;
}

sub firewall_is_in_subnet {
	my $subnet = shift;

	# ORANGE is missing here, because nothing may ever access
	# the firewall from this network.
	my $address = &fwlib::get_internal_firewall_ip_address($subnet, 0);

	if ($address) {
		return 1;
	}

	return 0;
}

#
# Function to gather which locations needs to be exported.
#
sub gather_locations_to_export () {
	my %geoipblock_exports = ();

	# Array to store the final list of locations.
	my @export_locations;

	# Array to temporary store all used GeoIP groups.
	my @used_GeoIP_groups;

	# Check if GeoIP-block is enabled.
	if($geoipsettings{"GEOIPBLOCK_ENABLED"} eq "on") {
		# Loop through the array of supported locations.
		foreach my $location (@locations) {
			if ($geoipsettings{$location} eq "on") {
				$geoipblock_exports{$location} = "1";
			}
		}
	}

	# Get the firewall locations of the input, forward and output
	# firewall settings hashhes.
	my %input_exports = &_grab_geoip_locations_from_fw_settings_hash(\%configinputfw);
	my %forward_exports = &_grab_geoip_locations_from_fw_settings_hash(\%configfwdfw);
	my %output_exports = &_grab_geoip_locations_from_fw_settings_hash(\%configoutgoingfw);

	# Merge the hashes.
	#
	# If a location is part of multiple hashes, it results in only one entry in the final hash.
	my %export_locations = ( %geoipblock_exports, %input_exports, %forward_exports, %output_exports );

	# Loop through the hash of exported locations.
	foreach my $location (keys %export_locations) {
		# Convert location into upper-case format.
		my $location_uc = uc($location);

		# Add the location to the array.
		push(@export_locations, $location_uc);
	}

	# Return the array.
	return @export_locations;
}

#
# Function to gather the GeoIP locations from a given hash
# containing the firewall settings.
#
sub _grab_geoip_locations_from_fw_settings_hash (\%) {
	my $hash = shift;
	my %exports;

	# Loop through the given firewall config hash.
	foreach my $rule ( keys %$hash ) {
		# Skip if the rule is disabled.
		next unless($$hash{$rule}[2] eq "ON");

		# Process rules with GeoIP as source.
		if($$hash{$rule}[3] eq "cust_geoip_src") {
			my $source = $$hash{$rule}[4];

			# Check if the source is a group.
			if($source =~ m/group/) {
			       my($group, $groupname) = split(":", $source);

				# Get locations which are part of the group.
				my @group_locations = &_grab_geoip_locations_from_group($groupname);

				# Loop through the array.
				foreach my $location (@group_locations) {
					# Add location to the exports hash.
					$exports{$location} = "1";
				}
			} else {
				# Add location to the exports hash.
				$exports{$source} = "1";
			}

			# Jump the next rule.
			next;
		}

		# Process rules with GeoIP as target.
		if($$hash{$rule}[5] eq "cust_geoip_tgt") {
			my $destination = $$hash{$rule}[6];

			# Check if the destination is a group.
			if($destination =~ m/group/) {
				my($group, $groupname) = split(":", $destination);

				# Get locations which are part of the group.
				my @group_locations = &_grab_geoip_locations_from_group($groupname);

				# Loop through the array.
				foreach my $location (@group_locations) {
					# Add location to the exports hash.
					$exports{$location} = "1";
				}
			} else {
				# Add location to the exports hash.
				$exports{$destination} = "1";
			}

			# Jump to next rule.
			next;
		}
	}

	# Return the array.
	return %exports;
}

#
# Function to gather the GeoIP locations from a given group name.
#
sub _grab_geoip_locations_from_group($) {
	my ($groupname) = @_;

	my %geoipgroups = ();
	my @group_locations;

	# Get all configured GeoIP related groups.
	&General::readhasharray("${General::swroot}/fwhosts/customgeoipgrp", \%geoipgroups);

	# Loop through the hash of GeoIP groups.
	foreach my $key (keys %geoipgroups) {
		# Seach for members of the given group.
		if($geoipgroups{$key}[0] eq "$groupname") {
			# Add the location to the group_locations array.
			push(@group_locations, $geoipgroups{$key}[2]);
		}
	}

	# Return the array.
	return @group_locations;
}
