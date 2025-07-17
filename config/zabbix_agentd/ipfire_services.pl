#!/usr/bin/perl
###############################################################################
# ipfire_services.pl - Retrieves available IPFire services information and 
#                      return this as a JSON array suitable for easy processing 
#                      by Zabbix server
#
# Author: robin.roevens (at) disroot.org
# Version: 3.0
#
# Copyright (C) 2007-2024  IPFire Team  <info@ipfire.org> 
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License 
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
###############################################################################

use strict;

# enable only the following on debugging purpose
# use warnings;

# Load General functions
require "/var/ipfire/general-functions.pl";

# Load Pakfire functions
require "/opt/pakfire/lib/functions.pl";

my $first = 1;

print "[";

# Built-in services
my %services = (
        # DHCP Server
        'DHCP Server' => {
                "process" => "dhcpd",
        },

        # Web Server
        'Web Server' => {
                "process" => "httpd",
        },

        # Cron Server
        'CRON Server' => {
                "process" => "fcron",
        },

        # DNS Proxy
        'DNS Proxy Server' => {
                "process" => "unbound",
        },

        # Syslog
        'Logging Server' => {
                "process" => "syslogd",
        },

        # Kernel Logger
        'Kernel Logging Server' => {
                "process" => "klogd",
        },

        # Time Server
        'NTP Server' => {
                "process" => "ntpd",
        },

        # SSH Server
        'Secure Shell Server' => {
                "process" => "sshd",
        },

        # IPsec
        'VPN' => {
                "process" => "charon",
        },

        # Web Proxy
        'Web Proxy' => {
                "process" => "squid",
        },

        # IPS
        'Intrusion Prevention System' => {
                "process" => "suricata",
                "pidfile" => "/var/run/suricata.pid",
        },

        # OpenVPN Roadwarrior
        'OpenVPN Roadwarrior Server' => {
                "process" => "openvpn",
                "pidfile" => "/var/run/openvpn-rw.pid",
        }
);

foreach my $service (sort keys %services){
        my %config = %{ $services{$service} };

        my $pidfile = $config{"pidfile"};
        my $process = $config{"process"};

        # Collect all pids
        my @pids = ();

        # Read the PID file or go search...
        if (defined $pidfile) {
                @pids = &General::read_pids("${pidfile}");
        } else {
                @pids = &General::find_pids("${process}");
        }

        # Not Running
        my $status = "\"state\":\"0\"";

        # Running?
        if (scalar @pids) {
                # Get memory consumption
                my $mem = &General::get_memory_consumption(@pids);

                $status = "\"state\":1,\"pids\":[" . join(',', @pids) . "],\"memory\":$mem";
        }

        print "," if not $first;
	$first = 0;

	print "{";
	print "\"service\":\"$service\",\"servicename\":\"$process\",$status";
	print "}";
}

# Generate list of installed addon pak's
my %paklist = &Pakfire::dblist("installed");

foreach my $pak (keys %paklist) {
        my %metadata = &Pakfire::getmetadata($pak, "installed");
                
        # If addon contains services
        if ("$metadata{'Services'}") {
                foreach my $service (split(/ /, "$metadata{'Services'}")) {
                        print ",";
                        print "{";

                        print "\"service\":\"Addon: $metadata{'Name'}\",";
                        print "\"servicename\":\"$service\",";

                        my $onboot = isautorun($pak, $service);
                        print "\"onboot\":$onboot,";

                        print &addonservicestats($pak, $service);

                        print "}";
                }
	}
}	

print "]";

sub isautorun() {
   my ($pak, $service) = @_;
	my @testcmd = &General::system_output("/usr/local/bin/addonctrl", "$pak", "boot-status", "$service");
	my $testcmd = @testcmd[0];
	my $status = 9;

	# Check if autorun for the given service is enabled.
	if ( $testcmd =~ /enabled\ on\ boot/ ) {
		$status = 1;
	} elsif ( $testcmd =~ /disabled\ on\ boot/ ) {
		$status = 0;
	}

	# Return the status.
	return $status;
}

sub addonservicestats() {
   my ($pak, $service) = @_;
   my $testcmd = '';
   my $exename;
   my @memory = (0);

   my @testcmd = &General::system_output("/usr/local/bin/addonctrl", "$pak", "status", "$service");
	my $testcmd = @testcmd[0];

        my $status = "\"state\":0";
        if ( $testcmd =~ /is\ running/ && $testcmd !~ /is\ not\ running/){
                $testcmd =~ s/.* //gi;
                $testcmd =~ s/[a-z_]//gi;
                $testcmd =~ s/\[[0-1]\;[0-9]+//gi;
                $testcmd =~ s/[\(\)\.]//gi;
                $testcmd =~ s/  //gi;
                $testcmd =~ s///gi;

                my @pids = split(/\s/,$testcmd);

                # Fetch the memory consumption
		my $memory = &General::get_memory_consumption(@pids);

                $status = "\"state\":1,\"pids\":[" . join(',', @pids) . "],\"memory\":$memory";
        }
        return $status;
}
