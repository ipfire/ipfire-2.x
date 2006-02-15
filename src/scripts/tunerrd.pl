#!/usr/bin/perl

use RRDs;

# Settings
my $rrdlog = "/var/log/rrd";
$ENV{PATH}="/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin";

RRDs::tune ("$rrdlog/cpu.rrd",
"-h", "user:600",
"-h", "system:600",
"-h", "idle:600");

RRDs::tune ("$rrdlog/mem.rrd",
"-h", "memused:600",
"-h", "memfree:600",
"-h", "memshared:600",
"-h", "membuffers:600",
"-h", "memcache:600",
"-h", "swapused:600",
"-h", "swapfree:600");

RRDs::tune ("$rrdlog/disk.rrd",
"-h", "readsect:600",
"-h", "writesect:600");

RRDs::tune ("$rrdlog/RED.rrd",
"-h", "incoming:600",
"-h", "outgoing:600");

RRDs::tune ("$rrdlog/GREEN.rrd",
"-h", "incoming:600",
"-h", "outgoing:600");
# end of script
