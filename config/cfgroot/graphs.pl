#!/usr/bin/perl
# Generate Graphs exported from Makegraphs to minimize system load an only generate the Graphs when displayed
# This is part of the IPFire Firewall


package Graphs;

use strict;
use RRDs;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my $ERROR;
my $rrdlog = "/var/log/rrd";
my $graphs = "/srv/web/ipfire/html/graphs";
$ENV{PATH}="/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin";

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

my %mbmon_settings = ();
&General::readhash("${General::swroot}/mbmon/settings", \%mbmon_settings);

my %mbmon_values = ();
if ( -e "/var/log/mbmon-values" ){
&General::readhash("/var/log/mbmon-values", \%mbmon_values);
}

my $key;
my $value;
my @args = ();
my $count = 0;

use Encode 'from_to';

my %tr=();
if ((${Lang::language} eq 'el') ||
    (${Lang::language} eq 'fa') ||
    (${Lang::language} eq 'ru') ||
    (${Lang::language} eq 'th') ||
    (${Lang::language} eq 'vi') ||
    (${Lang::language} eq 'zh') ||
    (${Lang::language} eq 'zt')) {
        eval `/bin/cat "${General::swroot}/langs/en.pl"`;
} else {
        %tr=%Lang::tr;          # use translated version for other languages
}


sub updatecpugraph {
 my $period    = $_[0];

        RRDs::graph ("$graphs/cpu-$period.png",
        "--start", "-1$period", "-aPNG", "-i", "-z", "-W www.ipfire.org",, "-v $Lang::tr{'percentage'}",
        "--alt-y-grid", "-w 600", "-h 150", "-l 0", "-u 100", "-r",
        "--color", "SHADEA".$color{"color19"},
        "--color", "SHADEB".$color{"color19"},
        "--color", "BACK".$color{"color21"},
        "-t $Lang::tr{'cpu usage per'} $Lang::tr{$period}",
        "DEF:iowait=$rrdlog/collectd/localhost/cpu-0/cpu-wait.rrd:value:AVERAGE",
        "DEF:nice=$rrdlog/collectd/localhost/cpu-0/cpu-nice.rrd:value:AVERAGE",
        "DEF:interrupt=$rrdlog/collectd/localhost/cpu-0/cpu-interrupt.rrd:value:AVERAGE",
        "DEF:steal=$rrdlog/collectd/localhost/cpu-0/cpu-steal.rrd:value:AVERAGE",
        "DEF:user=$rrdlog/collectd/localhost/cpu-0/cpu-user.rrd:value:AVERAGE",
        "DEF:system=$rrdlog/collectd/localhost/cpu-0/cpu-system.rrd:value:AVERAGE",
        "DEF:idle=$rrdlog/collectd/localhost/cpu-0/cpu-idle.rrd:value:AVERAGE",
        "DEF:irq=$rrdlog/collectd/localhost/cpu-0/cpu-softirq.rrd:value:AVERAGE",
        "CDEF:total=user,system,idle,iowait,irq,nice,interrupt,steal,+,+,+,+,+,+,+",
        "CDEF:userpct=100,user,total,/,*",
        "CDEF:nicepct=100,nice,total,/,*",
        "CDEF:interruptpct=100,interrupt,total,/,*",
        "CDEF:stealpct=100,steal,total,/,*",
        "CDEF:systempct=100,system,total,/,*",
        "CDEF:idlepct=100,idle,total,/,*",
        "CDEF:iowaitpct=100,iowait,total,/,*",
        "CDEF:irqpct=100,irq,total,/,*",
        "COMMENT:".sprintf("%-29s",$Lang::tr{'caption'}),
        "COMMENT:$Lang::tr{'maximal'}",
        "COMMENT:$Lang::tr{'average'}",
        "COMMENT:$Lang::tr{'minimal'}",
        "COMMENT:$Lang::tr{'current'}\\j",
        "AREA:iowaitpct".$color{"color14"}.":".sprintf("%-25s",$Lang::tr{'cpu iowait usage'}),
        "GPRINT:iowaitpct:MAX:%3.2lf%%",
        "GPRINT:iowaitpct:AVERAGE:%3.2lf%%",
        "GPRINT:iowaitpct:MIN:%3.2lf%%",
        "GPRINT:iowaitpct:LAST:%3.2lf%%\\j",
        "STACK:irqpct".$color{"color23"}."A0:".sprintf("%-25s",$Lang::tr{'cpu irq usage'}),
        "GPRINT:irqpct:MAX:%3.2lf%%",
        "GPRINT:irqpct:AVERAGE:%3.2lf%%",
        "GPRINT:irqpct:MIN:%3.2lf%%",
        "GPRINT:irqpct:LAST:%3.2lf%%\\j",
        "STACK:nicepct".$color{"color16"}."A0:".sprintf("%-25s",$Lang::tr{'cpu nice usage'}),
        "GPRINT:nicepct:MAX:%3.2lf%%",
        "GPRINT:nicepct:AVERAGE:%3.2lf%%",
        "GPRINT:nicepct:MIN:%3.2lf%%",
        "GPRINT:nicepct:LAST:%3.2lf%%\\j",
        "STACK:interruptpct".$color{"color15"}."A0:".sprintf("%-25s",$Lang::tr{'cpu interrupt usage'}),
        "GPRINT:interruptpct:MAX:%3.2lf%%",
        "GPRINT:interruptpct:AVERAGE:%3.2lf%%",
        "GPRINT:interruptpct:MIN:%3.2lf%%",
        "GPRINT:interruptpct:LAST:%3.2lf%%\\j",
        "STACK:stealpct".$color{"color18"}."A0:".sprintf("%-25s",$Lang::tr{'cpu steal usage'}),
        "GPRINT:stealpct:MAX:%3.2lf%%",
        "GPRINT:stealpct:AVERAGE:%3.2lf%%",
        "GPRINT:stealpct:MIN:%3.2lf%%",
        "GPRINT:stealpct:LAST:%3.2lf%%\\j",
        "STACK:userpct".$color{"color11"}."A0:".sprintf("%-25s",$Lang::tr{'cpu user usage'}),
        "GPRINT:userpct:MAX:%3.2lf%%",
        "GPRINT:userpct:AVERAGE:%3.2lf%%",
        "GPRINT:userpct:MIN:%3.2lf%%",
        "GPRINT:userpct:LAST:%3.2lf%%\\j",
        "STACK:systempct".$color{"color13"}."A0:".sprintf("%-25s",$Lang::tr{'cpu system usage'}),
        "GPRINT:systempct:MAX:%3.2lf%%",
        "GPRINT:systempct:AVERAGE:%3.2lf%%",
        "GPRINT:systempct:MIN:%3.2lf%%",
        "GPRINT:systempct:LAST:%3.2lf%%\\j",
        "STACK:idlepct".$color{"color12"}."A0:".sprintf("%-25s",$Lang::tr{'cpu idle usage'}),
        "GPRINT:idlepct:MAX:%3.2lf%%",
        "GPRINT:idlepct:AVERAGE:%3.2lf%%",
        "GPRINT:idlepct:MIN:%3.2lf%%",
        "GPRINT:idlepct:LAST:%3.2lf%%\\j");
        $ERROR = RRDs::error;
        print "Error in RRD::graph for cpu: $ERROR\n" if $ERROR;
}

sub updateloadgraph {
        my $period    = $_[0];

        RRDs::graph ("$graphs/load-$period.png",
        "--start", "-1$period", "-aPNG",
        "-w 600", "-h 150", "-i", "-z", "-W www.ipfire.org", "-l 0", "-r", "--alt-y-grid",
        "-t Load Average $Lang::tr{'graph per'} $Lang::tr{$period}",
        "--color", "SHADEA".$color{"color19"},
        "--color", "SHADEB".$color{"color19"},
        "--color", "BACK".$color{"color21"},
        "DEF:load1=$rrdlog/collectd/localhost/load/load.rrd:shortterm:AVERAGE",
        "DEF:load5=$rrdlog/collectd/localhost/load/load.rrd:midterm:AVERAGE",
        "DEF:load15=$rrdlog/collectd/localhost/load/load.rrd:longterm:AVERAGE",
        "AREA:load1".$color{"color13"}."A0:1 Minute, letzter:",
        "GPRINT:load1:LAST:%5.2lf",
        "AREA:load5".$color{"color18"}."A0:5 Minuten, letzter:",
        "GPRINT:load5:LAST:%5.2lf",
        "AREA:load15".$color{"color14"}."A0:15 Minuten, letzter:",
        "GPRINT:load15:LAST:%5.2lf\\j",
        "LINE1:load5".$color{"color13"},
        "LINE1:load1".$color{"color18"});
        $ERROR = RRDs::error;
        print "Error in RRD::graph for load: $ERROR\n" if $ERROR;
}

sub updatememgraph {
        my $period    = $_[0];

        RRDs::graph ("$graphs/memory-$period.png",
        "--start", "-1$period", "-aPNG", "-i", "-z", "-W www.ipfire.org", "-v $Lang::tr{'percentage'}",
        "--alt-y-grid", "-w 600", "-h 150", "-l 0", "-u 100", "-r",
        "--color", "SHADEA".$color{"color19"},
        "--color", "SHADEB".$color{"color19"},
        "--color", "BACK".$color{"color21"},
        "-t $Lang::tr{'memory usage per'} $Lang::tr{$period}",
        "DEF:used=$rrdlog/collectd/localhost/memory/memory-used.rrd:value:AVERAGE",
        "DEF:free=$rrdlog/collectd/localhost/memory/memory-free.rrd:value:AVERAGE",
        "DEF:buffer=$rrdlog/collectd/localhost/memory/memory-buffered.rrd:value:AVERAGE",
        "DEF:cache=$rrdlog/collectd/localhost/memory/memory-cached.rrd:value:AVERAGE",
        "CDEF:total=used,free,cache,buffer,+,+,+",
        "CDEF:usedpct=used,total,/,100,*",
        "CDEF:bufferpct=buffer,total,/,100,*",
        "CDEF:cachepct=cache,total,/,100,*",
        "CDEF:freepct=free,total,/,100,*",
        "COMMENT:$Lang::".sprintf("%-29s",$Lang::tr{'caption'}),
        "COMMENT:$Lang::tr{'maximal'}",
        "COMMENT:$Lang::tr{'average'}",
        "COMMENT:$Lang::tr{'minimal'}",
        "COMMENT:$Lang::tr{'current'}\\j",
        "AREA:usedpct".$color{"color11"}."A0:".sprintf("%-25s",$Lang::tr{'used memory'}),
        "GPRINT:usedpct:MAX:%3.2lf%%",
        "GPRINT:usedpct:AVERAGE:%3.2lf%%",
        "GPRINT:usedpct:MIN:%3.2lf%%",
        "GPRINT:usedpct:LAST:%3.2lf%%\\j",
        "STACK:bufferpct".$color{"color23"}."A0:".sprintf("%-25s",$Lang::tr{'buffered memory'}),
        "GPRINT:bufferpct:MAX:%3.2lf%%",
        "GPRINT:bufferpct:AVERAGE:%3.2lf%%",
        "GPRINT:bufferpct:MIN:%3.2lf%%",
        "GPRINT:bufferpct:LAST:%3.2lf%%\\j",
        "STACK:cachepct".$color{"color14"}."A0:".sprintf("%-25s",$Lang::tr{'cached memory'}),
        "GPRINT:cachepct:MAX:%3.2lf%%",
        "GPRINT:cachepct:AVERAGE:%3.2lf%%",
        "GPRINT:cachepct:MIN:%3.2lf%%",
        "GPRINT:cachepct:LAST:%3.2lf%%\\j",
        "STACK:freepct".$color{"color12"}."A0:".sprintf("%-25s",$Lang::tr{'free memory'}),
        "GPRINT:freepct:MAX:%3.2lf%%",
        "GPRINT:freepct:AVERAGE:%3.2lf%%",
        "GPRINT:freepct:MIN:%3.2lf%%",
        "GPRINT:freepct:LAST:%3.2lf%%\\j");
        $ERROR = RRDs::error;
        print "Error in RRD::graph for mem: $ERROR\n" if $ERROR;

        RRDs::graph ("$graphs/swap-$period.png",
        "--start", "-1$period", "-aPNG", "-i", "-z", "-W www.ipfire.org", "-v $Lang::tr{'percentage'}",
        "--alt-y-grid", "-w 600", "-h 150", "-l 0", "-u 100", "-r",
        "--color", "SHADEA".$color{"color19"},
        "--color", "SHADEB".$color{"color19"},
        "--color", "BACK".$color{"color21"},
        "-t $Lang::tr{'swap usage per'} $Lang::tr{$period}",
        "DEF:used=$rrdlog/collectd/localhost/swap/swap-used.rrd:value:AVERAGE",
        "DEF:free=$rrdlog/collectd/localhost/swap/swap-free.rrd:value:AVERAGE",
				"DEF:cached=$rrdlog/collectd/localhost/swap/swap-cached.rrd:value:AVERAGE",
        "CDEF:total=used,free,cached,+,+",
        "CDEF:usedpct=100,used,total,/,*",
        "CDEF:freepct=100,free,total,/,*",
        "CDEF:cachedpct=100,cached,total,/,*",
        "COMMENT:$Lang::".sprintf("%-29s",$Lang::tr{'caption'}),
        "COMMENT:$Lang::tr{'maximal'}",
        "COMMENT:$Lang::tr{'average'}",
        "COMMENT:$Lang::tr{'minimal'}",
        "COMMENT:$Lang::tr{'current'}\\j",
        "AREA:usedpct".$color{"color11"}."A0:".sprintf("%-25s",$Lang::tr{'used swap'}),
        "GPRINT:usedpct:MAX:%3.2lf%%",
        "GPRINT:usedpct:AVERAGE:%3.2lf%%",
        "GPRINT:usedpct:MIN:%3.2lf%%",
        "GPRINT:usedpct:LAST:%3.2lf%%\\j",
        "STACK:freepct".$color{"color12"}."A0:".sprintf("%-25s",$Lang::tr{'free swap'}),
        "GPRINT:freepct:MAX:%3.2lf%%",
        "GPRINT:freepct:AVERAGE:%3.2lf%%",
        "GPRINT:freepct:MIN:%3.2lf%%",
        "GPRINT:freepct:LAST:%3.2lf%%\\j",
        "STACK:cachedpct".$color{"color13"}."A0:".sprintf("%-25s",$Lang::tr{'cached swap'}),
        "GPRINT:cachedpct:MAX:%3.2lf%%",
        "GPRINT:cachedpct:AVERAGE:%3.2lf%%",
        "GPRINT:cachedpct:MIN:%3.2lf%%",
        "GPRINT:cachedpct:LAST:%3.2lf%%\\j");
        $ERROR = RRDs::error;
        print "Error in RRD::graph for swap: $ERROR\n" if $ERROR;
}

sub updatediskgraph {
        my $period    = $_[0];
        my $disk    = $_[1];

        RRDs::graph ("$graphs/disk-$disk-$period.png",
        "--start", "-1$period", "-aPNG", "-i", "-W www.ipfire.org", "-v $Lang::tr{'bytes per second'}",
        "--alt-y-grid", "-w 600", "-h 150", "-r", "-z",
				"--color", "SHADEA".$color{"color19"},
        "--color", "SHADEB".$color{"color19"},
        "--color", "BACK".$color{"color21"},
        "-t $disk $Lang::tr{'disk access per'} $Lang::tr{$period}",
        "DEF:read=$rrdlog/collectd/localhost/disk-$disk/disk_octets.rrd:read:AVERAGE",
        "DEF:write=$rrdlog/collectd/localhost/disk-$disk/disk_octets.rrd:write:AVERAGE",
        "CDEF:writen=write,-1,*",
        "DEF:standby=$rrdlog/hddshutdown-$disk.rrd:standby:AVERAGE",
        "CDEF:st=standby,INF,*",
        "COMMENT:$Lang::".sprintf("%-25s",$Lang::tr{'caption'}),
        "COMMENT:$Lang::tr{'maximal'}",
        "COMMENT:$Lang::tr{'average'}",
        "COMMENT:$Lang::tr{'minimal'}",
        "COMMENT:$Lang::tr{'current'}\\j",
        "AREA:st".$color{"color20"}.":standby\\j",
        "AREA:read".$color{"color14"}."A0:".sprintf("%-25s",$Lang::tr{'read bytes'}),
        "GPRINT:read:MAX:%8.1lf %sBps",
        "GPRINT:read:AVERAGE:%8.1lf %sBps",
        "GPRINT:read:MIN:%8.1lf %sBps",
        "GPRINT:read:LAST:%8.1lf %sBps\\j",
        "AREA:writen".$color{"color13"}."A0:".sprintf("%-25s",$Lang::tr{'written bytes'}),
				"GPRINT:write:MAX:%8.1lf %sBps",
        "GPRINT:write:AVERAGE:%8.1lf %sBps",
        "GPRINT:write:MIN:%8.1lf %sBps",
        "GPRINT:write:LAST:%8.1lf %sBps\\j");
        $ERROR = RRDs::error;
        print "Error in RRD::graph for disk: $ERROR\n" if $ERROR;
}

sub updateifgraph {
        my $interface = $_[0];
        my $period    = $_[1];

				RRDs::graph ("$graphs/$interface-$period.png",
				"--start", "-1$period", "-aPNG", "-i", "-W www.ipfire.org", "-v $Lang::tr{'bytes per second'}",
				"--alt-y-grid", "-w 600", "-h 150", "-z", "-r",
				"--color", "SHADEA".$color{"color19"},
				"--color", "SHADEB".$color{"color19"},
				"--color", "BACK".$color{"color21"},
				"-t $Lang::tr{'traffic on'} $interface $Lang::tr{'graph per'} $Lang::tr{$period}",
				"-v$Lang::tr{'bytes per second'}",
				"DEF:incoming=$rrdlog/collectd/localhost/interface/if_octets-$interface.rrd:rx:AVERAGE",
				"DEF:outgoing=$rrdlog/collectd/localhost/interface/if_octets-$interface.rrd:tx:AVERAGE",
				"CDEF:outgoingn=outgoing,-1,*",
				"COMMENT:$Lang::".sprintf("%-20s",$Lang::tr{'caption'}),
				"COMMENT:$Lang::tr{'maximal'}",
				"COMMENT:$Lang::tr{'average'}",
				"COMMENT:$Lang::tr{'minimal'}",
				"COMMENT:$Lang::tr{'current'}\\j",
				"AREA:incoming".$color{"color12"}."A0:$Lang::tr{'incoming traffic in bytes per second'}",
				"GPRINT:incoming:MAX:%8.1lf %sBps",
				"GPRINT:incoming:AVERAGE:%8.1lf %sBps",
				"GPRINT:incoming:MIN:%8.1lf %sBps",
				"GPRINT:incoming:LAST:%8.1lf %sBps\\j",
				"AREA:outgoingn".$color{"color13"}."A0:$Lang::tr{'outgoing traffic in bytes per second'}",
				"GPRINT:outgoing:MAX:%8.1lf %sBps",
				"GPRINT:outgoing:AVERAGE:%8.1lf %sBps",
				"GPRINT:outgoing:MIN:%8.1lf %sBps",
				"GPRINT:outgoing:LAST:%8.1lf %sBps\\j");
				$ERROR = RRDs::error;
				print "Error in RRD::graph for $interface: $ERROR\n" if $ERROR;
}

sub updatefwhitsgraph {
				my $period = $_[0];
				RRDs::graph ("$graphs/fwhits-$period.png",
				"--start", "-1$period", "-aPNG", "-i", "-z", "-W www.ipfire.org",
				"--alt-y-grid", "-w 600", "-h 150", "-r", "-v $Lang::tr{'bytes per second'}",
				"--color", "SHADEA".$color{"color19"},
				"--color", "SHADEB".$color{"color19"},
				"--color", "BACK".$color{"color21"},
				"-t $Lang::tr{'firewall hits per'} $Lang::tr{$period}",
				"DEF:output=$rrdlog/collectd/localhost/iptables-filter-FORWARD/ipt_bytes-DROP_OUTPUT.rrd:value:AVERAGE",
				"DEF:input=$rrdlog/collectd/localhost/iptables-filter-INPUT/ipt_bytes-DROP_INPUT.rrd:value:AVERAGE",
				"DEF:newnotsyn=$rrdlog/collectd/localhost/iptables-filter-NEWNOTSYN/ipt_bytes-DROP_NEWNOTSYN.rrd:value:AVERAGE",
				"DEF:portscan=$rrdlog/collectd/localhost/iptables-filter-PSCAN/ipt_bytes-DROP_PScan.rrd:value:AVERAGE",
				"CDEF:amount=output,input,newnotsyn,+,+",
				"COMMENT:$Lang::".sprintf("%-20s",$Lang::tr{'caption'}),
				"COMMENT:$Lang::tr{'maximal'}",
				"COMMENT:$Lang::tr{'average'}",
				"COMMENT:$Lang::tr{'minimal'}",
				"COMMENT:$Lang::tr{'current'}\\j",
				"AREA:amount".$color{"color24"}."A0:".sprintf("%-20s",$Lang::tr{'firewallhits'}),
				"GPRINT:amount:MAX:%8.1lf %sBps",
				"GPRINT:amount:AVERAGE:%8.1lf %sBps",
				"GPRINT:amount:MIN:%8.1lf %sBps",
				"GPRINT:amount:LAST:%8.1lf %sBps\\j",
				"STACK:portscan".$color{"color25"}."A0:".sprintf("%-20s",$Lang::tr{'portscans'}),
				"GPRINT:portscan:MAX:%8.1lf %sBps",
				"GPRINT:portscan:MIN:%8.1lf %sBps",
				"GPRINT:portscan:AVERAGE:%8.1lf %sBps",
				"GPRINT:portscan:LAST:%8.1lf %sBps\\j");
				$ERROR = RRDs::error;
				print "Error in RRD::graph for Firewallhits: $ERROR\n" if $ERROR;
}

sub updatelqgraph {
				my $period    = $_[0];
				RRDs::graph ("$graphs/lq-$period.png",
				"--start", "-1$period", "-aPNG", "-i", "-W www.ipfire.org",
				"--alt-y-grid", "-w 600", "-h 150", "-l 0", "-r", "-v ms",
				"-t $Lang::tr{'linkq'} $Lang::tr{'graph per'} $Lang::tr{$period}",
				"--color", "SHADEA".$color{"color19"},
				"--color", "SHADEB".$color{"color19"},
				"--color", "BACK".$color{"color21"},
				"DEF:roundtrip=$rrdlog/collectd/localhost/ping/ping-gateway.rrd:ping:AVERAGE",
				"COMMENT:$Lang::".sprintf("%-20s",$Lang::tr{'caption'})."\\j",
				"CDEF:r0=roundtrip,30,-",
				"CDEF:r1=r0,70,-",
				"CDEF:r2=r1,150,-",
				"CDEF:r3=r2,300,-",
				"AREA:r0".$color{"color12"}."A0:<30 ms",
				"STACK:r1".$color{"color17"}."A0:30-70 ms",
				"STACK:r2".$color{"color14"}."A0:70-150 ms",
				"STACK:r3".$color{"color18"}."A0:150-300 ms",
				"STACK:roundtrip".$color{"color25"}.":>300 ms\\j",
				"COMMENT:$Lang::tr{'maximal'}",
				"COMMENT:$Lang::tr{'average'}",
				"COMMENT:$Lang::tr{'minimal'}",
				"COMMENT:$Lang::tr{'current'}\\j",
				"LINE1:roundtrip#707070:",
				"GPRINT:roundtrip:MAX:%3.2lf ms",
				"GPRINT:roundtrip:AVERAGE:%3.2lf ms",
				"GPRINT:roundtrip:MIN:%3.2lf ms",
				"GPRINT:roundtrip:LAST:%3.2lf ms\\j");
				$ERROR = RRDs::error;
				print "Error in RRD::graph for Link Quality: $ERROR\n" if $ERROR;
}

sub updatehddgraph {

  my $disk = $_[0];
  my $period = $_[1];

  RRDs::graph ("$graphs/hddtemp-$disk-$period.png",
  "--start", "-1$period", "-aPNG", "-i", "-z", "-W www.ipfire.org",
  "--alt-y-grid", "-w 600", "-h 150",
  "--color", "SHADEA".$color{"color19"},
  "--color", "SHADEB".$color{"color19"},
  "--color", "BACK".$color{"color21"},
  "-t $disk $Lang::tr{'harddisk temperature'} $Lang::tr{'graph per'} $Lang::tr{$period}",
  "DEF:temperature=$rrdlog/hddtemp-$disk.rrd:temperature:AVERAGE",
  "DEF:standby=$rrdlog/hddshutdown-$disk.rrd:standby:AVERAGE",
  "CDEF:st=standby,INF,*",
  "AREA:st".$color{"color20"}.":standby",
  "LINE2:temperature".$color{"color11"}.":$Lang::tr{'hdd temperature in'} C\\j",
  "COMMENT:$Lang::tr{'maximal'}",
  "COMMENT:$Lang::tr{'average'}",
  "COMMENT:$Lang::tr{'minimal'}",
  "COMMENT:$Lang::tr{'current'}\\j",
  "GPRINT:temperature:MAX:%3.0lf Grad C",
  "GPRINT:temperature:AVERAGE:%3.0lf Grad C",
  "GPRINT:temperature:MIN:%3.0lf Grad C",
  "GPRINT:temperature:LAST:%3.0lf Grad C\\j",
  );
  $ERROR = RRDs::error;
  print "Error in RRD::graph for hdd-$disk: $ERROR\n" if $ERROR;
}

sub updatetempgraph
{
  my $type   = "temp";
  my $period = $_[0];
  my $count = "11";

  @args = ("$graphs/mbmon-$type-$period.png",
    "--start", "-1$period", "-aPNG", "-i", "-z", "-W www.ipfire.org",
    "--alt-y-grid", "-w 600", "-h 150", "--alt-autoscale",
    "--color", "SHADEA".$color{"color19"},
    "--color", "SHADEB".$color{"color19"},
    "--color", "BACK".$color{"color21"},
    "-t $Lang::tr{'mbmon temp'} ($Lang::tr{'graph per'} $Lang::tr{$period})",
    "COMMENT:$Lang::tr{'caption'}\\t\\t",
    "COMMENT:$Lang::tr{'maximal'}",
    "COMMENT:$Lang::tr{'average'}",
    "COMMENT:$Lang::tr{'minimal'}",
    "COMMENT:$Lang::tr{'current'}\\j",);

  foreach $key ( sort(keys %mbmon_values) )
  {
    if ( (index($key, $type) != -1) && ($mbmon_settings{'LINE-'.$key} eq 'on') )
    {
      if ( !defined($mbmon_settings{'LABEL-'.$key}) || ($mbmon_settings{'LABEL-'.$key} eq '') )
      {
        $mbmon_settings{'LABEL-'.$key} = $key;
      }
    push (@args, "DEF:$key=$rrdlog/mbmon.rrd:$key:AVERAGE");
    push (@args, "LINE2:".$key.$color{"color$count"}.":$mbmon_settings{'LABEL-'.$key} Grad C");
    push (@args, "GPRINT:$key:MAX:%3.1lf");
    push (@args, "GPRINT:$key:AVERAGE:%3.1lf");
    push (@args, "GPRINT:$key:MIN:%3.1lf");
    push (@args, "GPRINT:$key:LAST:%3.1lf\\j");
    $count++;
   }
  }

  RRDs::graph ( @args );
    $ERROR = RRDs::error;
    print("Error in RRD::graph for temp: $ERROR\n")if $ERROR;
}

sub updatefangraph
{
  my $type   = "fan";
  my $period = $_[0];
  my $count = "11";

  @args = ("$graphs/mbmon-$type-$period.png", "--start", "-1$period", "-aPNG", "-i", "-z", "-W www.ipfire.org",
    "--alt-y-grid", "-w 600", "-h 150", "--alt-autoscale",
    "--color", "SHADEA".$color{"color19"},
    "--color", "SHADEB".$color{"color19"},
    "--color", "BACK".$color{"color21"},
    "-t $Lang::tr{'mbmon fan'} ($Lang::tr{'graph per'} $Lang::tr{$period})",
    "COMMENT:$Lang::tr{'caption'}\\t\\t",
    "COMMENT:$Lang::tr{'maximal'}",
    "COMMENT:$Lang::tr{'average'}",
    "COMMENT:$Lang::tr{'minimal'}",
    "COMMENT:$Lang::tr{'current'}\\j",);

  foreach $key ( sort(keys %mbmon_values) )
  {
    if ( (index($key, $type) != -1) && ($mbmon_settings{'LINE-'.$key} eq 'on') )
    {
      if ( !defined($mbmon_settings{'LABEL-'.$key}) || ($mbmon_settings{'LABEL-'.$key} eq '') )
      {
        $mbmon_settings{'LABEL-'.$key} = $key;
      }

      push(@args, "DEF:$key=$rrdlog/mbmon.rrd:$key:AVERAGE");
      push(@args, "LINE2:".$key.$color{"color$count"}.":$mbmon_settings{'LABEL-'.$key} rpm");
      push(@args, "GPRINT:$key:MAX:%5.0lf");
      push(@args, "GPRINT:$key:AVERAGE:%5.0lf");
      push(@args, "GPRINT:$key:MIN:%5.0lf");
      push(@args, "GPRINT:$key:LAST:%5.0lf\\j");
      $count++;
    }
  }
    RRDs::graph ( @args );
    $ERROR = RRDs::error;
    print("Error in RRD::graph for temp: $ERROR\n")if $ERROR;
}

sub updatevoltgraph
{
  my $type   = "volt";
  my $period = $_[0];
  my $count = "11";

  @args = ("$graphs/mbmon-$type-$period.png", "--start", "-1$period", "-aPNG", "-i", "-z", "-W www.ipfire.org",
    "--alt-y-grid", "-w 600", "-h 150", "--alt-autoscale",
    "--color", "SHADEA".$color{"color19"},
    "--color", "SHADEB".$color{"color19"},
    "--color", "BACK".$color{"color21"},
    "-t $Lang::tr{'mbmon volt'} ($Lang::tr{'graph per'} $Lang::tr{$period})",
    "COMMENT:$Lang::tr{'caption'}\\t",
    "COMMENT:$Lang::tr{'maximal'}",
    "COMMENT:$Lang::tr{'average'}",
    "COMMENT:$Lang::tr{'minimal'}",
    "COMMENT:$Lang::tr{'current'}\\j",);

  foreach $key ( sort(keys %mbmon_values) )
  {
    my $v = substr($key,0,1);
    if ( ($v eq 'v') && ($mbmon_settings{'LINE-'.$key} eq 'on') )
    {
      if ( !defined($mbmon_settings{'LABEL-'.$key}) || ($mbmon_settings{'LABEL-'.$key} eq '') )
      {
        $mbmon_settings{'LABEL-'.$key} = $key;
      }

      push(@args, "DEF:$key=$rrdlog/mbmon.rrd:$key:AVERAGE");
      push(@args, "LINE2:".$key.$color{"color$count"}.":$mbmon_settings{'LABEL-'.$key} Volt");
      push(@args, "GPRINT:$key:MAX:%3.2lf");
      push(@args, "GPRINT:$key:AVERAGE:%3.2lf");
      push(@args, "GPRINT:$key:MIN:%3.2lf");
      push(@args, "GPRINT:$key:LAST:%3.2lf\\j");
      $count++;
    }
  }

    RRDs::graph ( @args );
    $ERROR = RRDs::error;
    print("Error in RRD::graph for temp: $ERROR\n")if $ERROR;
}

sub overviewgraph {

  my $period = $_[0];
  my $periodstring;
  my $description;
  my %qossettings = ();
  &General::readhash("${General::swroot}/qos/settings", \%qossettings);
  my $classentry = "";
  my @classes = ();
  my @classline = ();
  my $classfile = "/var/ipfire/qos/classes";

	$qossettings{'DEV'} = $_[1];
	if ( $qossettings{'DEV'} eq $qossettings{'RED_DEV'} ) {
		$qossettings{'CLASSPRFX'} = '1';
	} else {
		$qossettings{'CLASSPRFX'} = '2';
	}

  if ( $period ne '3240' ){ $periodstring = "-1$period";}else{ $periodstring = "-".$period;}
  if ( $period ne '3240' ){ $description = "-t $Lang::tr{'Utilization on'} ($qossettings{'DEV'}) ($Lang::tr{'graph per'} $Lang::tr{$period})";}else{ $description = "-t $Lang::tr{'Utilization on'} ($qossettings{'DEV'})";}

	my $ERROR="";
	my $count="1";
	my $color="#000000";
	my @command=("/srv/web/ipfire/html/graphs/qos-graph-$qossettings{'DEV'}-$period.png",
		"--start", $periodstring, "-aPNG", "-i", "-z", "-W www.ipfire.org",
		"--alt-y-grid", "-w 600", "-h 150", "-r",
    "--color", "SHADEA".$color{"color19"},
    "--color", "SHADEB".$color{"color19"},
    "--color", "BACK".$color{"color21"},
    "COMMENT:$Lang::tr{'caption'}\\t\\t\\t\\t   ",
    "COMMENT:$Lang::tr{'maximal'}",
    "COMMENT:$Lang::tr{'average'}",
    "COMMENT:$Lang::tr{'minimal'}",
    "COMMENT:$Lang::tr{'current'}\\j",
		$description
	);
	open( FILE, "< $classfile" ) or die "Unable to read $classfile";
	@classes = <FILE>;
	close FILE;
  	foreach $classentry (sort @classes)
  	{
  		@classline = split( /\;/, $classentry );
  		if ( $classline[0] eq $qossettings{'DEV'} )
  		{
			$color=random_hex_color(6);
			push(@command, "DEF:$classline[1]=/var/log/rrd/class_$qossettings{'CLASSPRFX'}-$classline[1]_$qossettings{'DEV'}.rrd:bytes:AVERAGE");

			if ($count eq "1") {
				push(@command, "AREA:$classline[1]$color:Klasse $classline[1] -".sprintf("%15s",$classline[8]));
			} else {
				push(@command, "STACK:$classline[1]$color:Klasse $classline[1] -".sprintf("%15s",$classline[8]));

			}
			push(@command, "GPRINT:$classline[1]:MAX:%5.2lf");
			push(@command, "GPRINT:$classline[1]:AVERAGE:%5.2lf");
			push(@command, "GPRINT:$classline[1]:MIN:%5.2lf");
			push(@command, "GPRINT:$classline[1]:LAST:%5.2lf\\j");
			$count++;
		}
	}
	RRDs::graph (@command);
	$ERROR = RRDs::error;
	print "$ERROR";
}

sub random_hex_color {
    my $size = shift;
    $size = 6 if $size !~ /^3|6$/;
    my @hex = ( 0 .. 9, 'a' .. 'f' );
    my @color;
    push @color, @hex[rand(@hex)] for 1 .. $size;
    return join('', '#', @color);
}
