# Generate Graphs exported from Makegraphs to minimize system load an only generate the Graphs when displayed
# Initialisation

package Graphs;

use strict;
use RRDs;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

$General::version = '2.0b';
$General::swroot = '/var/ipfire';

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
        "--start", "-1$period", "-aPNG", "-i", "-z",
        "--alt-y-grid", "-w 600", "-h 100", "-l 0", "-u 100", "-r",
        "--color", "SHADEA".$color{"color19"},
        "--color", "SHADEB".$color{"color19"},
        "--color", "BACK".$color{"color21"},
        "-t $tr{'cpu usage per'} $tr{$period}",
        "DEF:iowait=$rrdlog/cpu.rrd:iowait:AVERAGE",
        "DEF:user=$rrdlog/cpu.rrd:user:AVERAGE",
        "DEF:system=$rrdlog/cpu.rrd:system:AVERAGE",
        "DEF:idle=$rrdlog/cpu.rrd:idle:AVERAGE",
        "DEF:irq=$rrdlog/cpu.rrd:irq:AVERAGE",
        "CDEF:total=user,system,idle,iowait,irq,+,+,+,+",
        "CDEF:userpct=100,user,total,/,*",
        "CDEF:systempct=100,system,total,/,*",
        "CDEF:idlepct=100,idle,total,/,*",
        "CDEF:iowaitpct=100,iowait,total,/,*",
        "CDEF:irqpct=100,irq,total,/,*",
        "AREA:iowaitpct".$color{"color14"}.":$tr{'iowait'}",
        "STACK:userpct".$color{"color11"}.":$tr{'user cpu usage'}",
        "STACK:irqpct".$color{"color23"}.":IRQ CPU",
        "STACK:systempct".$color{"color13"}.":$tr{'system cpu usage'}",
        "STACK:idlepct".$color{"color12"}.":$tr{'idle cpu usage'}\\j",
        "COMMENT: \\j",
        "COMMENT:$tr{'maximal'}",
        "COMMENT:$tr{'average'}",
        "COMMENT:$tr{'current'}\\j",
        "GPRINT:userpct:MAX:$tr{'user cpu'}\\:%3.2lf%%",
        "GPRINT:userpct:AVERAGE:$tr{'user cpu'}\\:%3.2lf%%",
        "GPRINT:userpct:LAST:$tr{'user cpu'}\\:%3.2lf%%\\j",
        "GPRINT:irqpct:MAX:IRQ CPU\\:%3.2lf%%",
        "GPRINT:irqpct:AVERAGE:IRQ CPU\\:%3.2lf%%",
        "GPRINT:irqpct:LAST:IRQ CPU\\:%3.2lf%%\\j",
        "GPRINT:systempct:MAX:$tr{'system cpu'}\\:%3.2lf%%",
        "GPRINT:systempct:AVERAGE:$tr{'system cpu'}\\:%3.2lf%%",
        "GPRINT:systempct:LAST:$tr{'system cpu'}\\:%3.2lf%%\\j",
        "GPRINT:idlepct:MAX:$tr{'idle cpu'}\\:%3.2lf%%",
        "GPRINT:idlepct:AVERAGE:$tr{'idle cpu'}\\:%3.2lf%%",
        "GPRINT:idlepct:LAST:$tr{'idle cpu'}\\:%3.2lf%%\\j",
        "GPRINT:iowaitpct:MAX:$tr{'iowait'}\\:%3.2lf%%",
        "GPRINT:iowaitpct:AVERAGE:$tr{'iowait'}\\:%3.2lf%%",
        "GPRINT:iowaitpct:LAST:$tr{'iowait'}\\:%3.2lf%%\\j");
        $ERROR = RRDs::error;
        print "Error in RRD::graph for cpu: $ERROR\n" if $ERROR;
}

sub updateloadgraph {
        my $period    = $_[0];

        RRDs::graph ("$graphs/load-$period.png",
        "--start", "-1$period", "-aPNG",
        "-w 600", "-h 100", "-i", "-z", "-l 0", "-r", "--alt-y-grid",
        "-t Load Average",
        "--color", "SHADEA".$color{"color19"},
        "--color", "SHADEB".$color{"color19"},
        "--color", "BACK".$color{"color21"},
        "DEF:load1=$rrdlog/load.rrd:load1:AVERAGE",
        "DEF:load5=$rrdlog/load.rrd:load5:AVERAGE",
        "DEF:load15=$rrdlog/load.rrd:load15:AVERAGE",
        "AREA:load1".$color{"color13"}.":1 Minute, letzter:",
        "GPRINT:load1:LAST:%5.2lf",
        "AREA:load5".$color{"color18"}.":5 Minuten, letzter:",
        "GPRINT:load5:LAST:%5.2lf",
        "AREA:load15".$color{"color14"}.":15 Minuten, letzter:",
        "GPRINT:load15:LAST:%5.2lf\\j",
        "LINE1:load5".$color{"color13"},
        "LINE1:load1".$color{"color18"});
        $ERROR = RRDs::error;
        print "Error in RRD::graph for load: $ERROR\n" if $ERROR;
}

sub updatememgraph {
        my $period    = $_[0];

        RRDs::graph ("$graphs/memory-$period.png",
        "--start", "-1$period", "-aPNG", "-i", "-z",
        "--alt-y-grid", "-w 600", "-h 100", "-l 0", "-u 100", "-r",
        "--color", "SHADEA".$color{"color19"},
        "--color", "SHADEB".$color{"color19"},
        "--color", "BACK".$color{"color21"},
        "-t $tr{'memory usage per'} $tr{$period}",
        "DEF:used=$rrdlog/mem.rrd:memused:AVERAGE",
        "DEF:free=$rrdlog/mem.rrd:memfree:AVERAGE",
        "DEF:shared=$rrdlog/mem.rrd:memshared:AVERAGE",
        "DEF:buffer=$rrdlog/mem.rrd:membuffers:AVERAGE",
        "DEF:cache=$rrdlog/mem.rrd:memcache:AVERAGE",
        "CDEF:total=used,free,+",
        "CDEF:used2=used,buffer,cache,shared,+,+,-",
        "CDEF:usedpct=100,used2,total,/,*",
        "CDEF:sharedpct=100,shared,total,/,*",
        "CDEF:bufferpct=100,buffer,total,/,*",
        "CDEF:cachepct=100,cache,total,/,*",
        "CDEF:freepct=100,free,total,/,*",
        "AREA:usedpct".$color{"color11"}.":$tr{'used memory'}",
        "STACK:sharedpct".$color{"color13"}.":$tr{'shared memory'}",
        "STACK:bufferpct".$color{"color23"}.":$tr{'buffered memory'}",
        "STACK:cachepct".$color{"color14"}.":$tr{'cached memory'}",
        "STACK:freepct".$color{"color12"}.":$tr{'free memory'}\\j",
        "COMMENT: \\j",
        "COMMENT:$tr{'maximal'}",
        "COMMENT:$tr{'average'}",
        "COMMENT:$tr{'current'}\\j",
        "GPRINT:usedpct:MAX:$tr{'used memory'}\\:%3.2lf%%",
        "GPRINT:usedpct:AVERAGE:$tr{'used memory'}\\:%3.2lf%%",
        "GPRINT:usedpct:LAST:$tr{'used memory'}\\:%3.2lf%%\\j",
        "GPRINT:sharedpct:MAX:$tr{'shared memory'}\\:%3.2lf%%",
        "GPRINT:sharedpct:AVERAGE:$tr{'shared memory'}\\:%3.2lf%%",
        "GPRINT:sharedpct:LAST:$tr{'shared memory'}\\:%3.2lf%%\\j",
        "GPRINT:bufferpct:MAX:$tr{'buffered memory'}\\:%3.2lf%%",
        "GPRINT:bufferpct:AVERAGE:$tr{'buffered memory'}\\:%3.2lf%%",
        "GPRINT:bufferpct:LAST:$tr{'buffered memory'}\\:%3.2lf%%\\j",
        "GPRINT:cachepct:MAX:$tr{'cached memory'}\\:%3.2lf%%",
        "GPRINT:cachepct:AVERAGE:$tr{'cached memory'}\\:%3.2lf%%",
        "GPRINT:cachepct:LAST:$tr{'cached memory'}\\:%3.2lf%%\\j",
        "GPRINT:freepct:MAX:$tr{'free memory'}\\:%3.2lf%%",
        "GPRINT:freepct:AVERAGE:$tr{'free memory'}\\:%3.2lf%%",
        "GPRINT:freepct:LAST:$tr{'free memory'}\\:%3.2lf%%\\j");
        $ERROR = RRDs::error;
        print "Error in RRD::graph for mem: $ERROR\n" if $ERROR;

        RRDs::graph ("$graphs/swap-$period.png",
        "--start", "-1$period", "-aPNG", "-i", "-z",
        "--alt-y-grid", "-w 600", "-h 100", "-l 0", "-u 100", "-r",
        "--color", "SHADEA".$color{"color19"},
        "--color", "SHADEB".$color{"color19"},
        "--color", "BACK".$color{"color21"},
        "-t $tr{'swap usage per'} $tr{$period}",
        "DEF:used=$rrdlog/mem.rrd:swapused:AVERAGE",
        "DEF:free=$rrdlog/mem.rrd:swapfree:AVERAGE",
        "CDEF:total=used,free,+",
        "CDEF:usedpct=100,used,total,/,*",
        "CDEF:freepct=100,free,total,/,*",
        "AREA:usedpct".$color{"color11"}.":$tr{'used swap'}",
        "STACK:freepct".$color{"color12"}.":$tr{'free swap'}\\j",
        "COMMENT: \\j",
        "COMMENT:$tr{'maximal'}",
        "COMMENT:$tr{'average'}",
        "COMMENT:$tr{'current'}\\j",
        "GPRINT:usedpct:MAX:$tr{'used swap'}\\:%3.2lf%%",
        "GPRINT:usedpct:AVERAGE:$tr{'used swap'}\\:%3.2lf%%",
        "GPRINT:usedpct:LAST:$tr{'used swap'}\\:%3.2lf%%\\j",
        "GPRINT:freepct:MAX:$tr{'free swap'}\\:%3.2lf%%",
        "GPRINT:freepct:AVERAGE:$tr{'free swap'}\\:%3.2lf%%",
        "GPRINT:freepct:LAST:$tr{'free swap'}\\:%3.2lf%%\\j");
        $ERROR = RRDs::error;
        print "Error in RRD::graph for swap: $ERROR\n" if $ERROR;
}

sub updatediskgraph {
        my $period    = $_[0];
        my $disk    = $_[1];

        RRDs::graph ("$graphs/disk-$disk-$period.png",
        "--start", "-1$period", "-aPNG", "-i", "-z",
        "--alt-y-grid", "-w 600", "-h 100", "-l 0", "-r",
        "--color", "SHADEA".$color{"color19"},
        "--color", "SHADEB".$color{"color19"},
        "--color", "BACK".$color{"color21"},
        "-t $tr{'disk access per'} $tr{$period} $disk",
        "DEF:read=$rrdlog/disk-$disk.rrd:readsect:AVERAGE",
        "DEF:write=$rrdlog/disk-$disk.rrd:writesect:AVERAGE",
        "AREA:read".$color{"color11"}.":$tr{'sectors read from disk per second'}",
        "STACK:write".$color{"color12"}.":$tr{'sectors written to disk per second'}\\j",
        "COMMENT: \\j",
        "COMMENT:$tr{'maximal'}",
        "COMMENT:$tr{'average'}",
        "COMMENT:$tr{'current'}\\j",
        "GPRINT:read:MAX:$tr{'read sectors'}\\:%8.0lf",
        "GPRINT:read:AVERAGE:$tr{'read sectors'}\\:%8.0lf",
        "GPRINT:read:LAST:$tr{'read sectors'}\\:%8.0lf\\j",
        "GPRINT:write:MAX:$tr{'written sectors'}\\:%8.0lf",
        "GPRINT:write:AVERAGE:$tr{'written sectors'}\\:%8.0lf",
        "GPRINT:write:LAST:$tr{'written sectors'}\\:%8.0lf\\j");
        $ERROR = RRDs::error;
        print "Error in RRD::graph for disk: $ERROR\n" if $ERROR;
}

sub updateifgraph {
  my $interface = $_[0];
  my $period    = $_[1];

  RRDs::graph ("$graphs/$interface-$period.png",
  "--start", "-1$period", "-aPNG", "-i", "-z",
  "--alt-y-grid", "-w 600", "-h 100",
  "--color", "SHADEA".$color{"color19"},
  "--color", "SHADEB".$color{"color19"},
  "--color", "BACK".$color{"color21"},
  "-t $tr{'traffic on'} $interface ($tr{'graph per'} $tr{$period})",
  "-v$tr{'bytes per second'}",
  "DEF:incoming=$rrdlog/$interface.rrd:incoming:AVERAGE",
  "DEF:outgoing=$rrdlog/$interface.rrd:outgoing:AVERAGE",
  "AREA:incoming".$color{"color11"}.":$tr{'incoming traffic in bytes per second'}",
  "LINE1:outgoing".$color{"color12"}.":$tr{'outgoing traffic in bytes per second'}\\j",
  "COMMENT: \\j",
  "COMMENT:$tr{'maximal'}",
  "COMMENT:$tr{'average'}",
  "COMMENT:$tr{'current'}\\j",
  "GPRINT:incoming:MAX:$tr{'in'}\\:%8.3lf %sBps",
  "GPRINT:incoming:AVERAGE:$tr{'in'}\\:%8.3lf %sBps",
  "GPRINT:incoming:LAST:$tr{'in'}\\:%8.3lf %sBps\\j",
  "GPRINT:outgoing:MAX:$tr{'out'}\\:%8.3lf %sBps",
  "GPRINT:outgoing:AVERAGE:$tr{'out'}\\:%8.3lf %sBps",
  "GPRINT:outgoing:LAST:$tr{'out'}\\:%8.3lf %sBps\\j");
  $ERROR = RRDs::error;
  print "Error in RRD::graph for $interface: $ERROR\n" if $ERROR;
}

sub updatefwhitsgraph {
  my $interval = $_[0];

  RRDs::graph ("$graphs/firewallhits-$interval-area.png",
  "--start", "-1$interval", "-aPNG", "-i", "-z",
  "--alt-y-grid", "-w 600", "-h 200",
  "--color", "SHADEA".$color{"color19"},
  "--color", "SHADEB".$color{"color19"},
  "--color", "BACK".$color{"color21"},
  "-t firewall hits over the last $interval",
  "DEF:amount=$rrdlog/firewallhits.rrd:amount:AVERAGE",
  "AREA:amount".$color{"color24"}.":firewallhits",
  "GPRINT:amount:MAX:   $tr{'maximal'}\\: %2.2lf %S",
  "GPRINT:amount:AVERAGE: $tr{'average'}\\: %2.2lf %S",
  "GPRINT:amount:LAST: $tr{'current'}\\: %2.2lf %Shits/5 min\\n",
  "DEF:portamount=$rrdlog/firewallhits.rrd:portamount:AVERAGE",
  "AREA:portamount".$color{"color25"}.":portscans",
  "GPRINT:portamount:MAX:      $tr{'maximal'}\\: %2.2lf %S",
  "GPRINT:portamount:AVERAGE: $tr{'average'}\\: %2.2lf %S",
  "GPRINT:portamount:LAST: $tr{'current'}\\: %2.2lf %Shits/5 min");
  $ERROR = RRDs::error;
  print "Error in RRD::graph for Firewallhits: $ERROR\n" if $ERROR;
}

sub updatelqgraph {
  my $period    = $_[0];
  RRDs::graph ("$graphs/lq-$period.png",
  "--start", "-1$period", "-aPNG", "-i", "-z",
  "--alt-y-grid", "-w 600", "-h 100", "-l 0", "-r",
  "-t $tr{'linkq'} ($tr{'graph per'} $tr{$period})",
  "--lazy", 
  "--color", "SHADEA".$color{"color19"},
  "--color", "SHADEB".$color{"color19"},
  "--color", "BACK".$color{"color21"},
  "-v ms / pkts (% x10)",
  "DEF:roundtrip=$rrdlog/lq.rrd:roundtrip:AVERAGE",
  "DEF:loss=$rrdlog/lq.rrd:loss:AVERAGE",
  "CDEF:roundavg=roundtrip,PREV(roundtrip),+,2,/",
  "CDEF:loss10=loss,10,*",
  "CDEF:r0=roundtrip,30,MIN",
  "CDEF:r1=roundtrip,70,MIN",
  "CDEF:r2=roundtrip,150,MIN",
  "CDEF:r3=roundtrip,300,MIN",
  "AREA:roundtrip".$color{"color25"}.":>300 ms",
  "AREA:r3".$color{"color18"}.":150-300 ms",
  "AREA:r2".$color{"color14"}.":70-150 ms",
  "AREA:r1".$color{"color17"}.":30-70 ms",
  "AREA:r0".$color{"color12"}.":<30 ms",
  "AREA:loss10".$color{"color13"}.":Packet loss (x10)\\j",
  "COMMENT: \\j",
  "COMMENT:$tr{'maximal'}",
  "COMMENT:$tr{'average'}",
  "COMMENT:$tr{'current'}\\j",
  "LINE1:roundtrip#707070:",
  "GPRINT:roundtrip:MAX:Time\\:%3.2lf ms",
  "GPRINT:roundtrip:AVERAGE:Time\\:%3.2lf ms",
  "GPRINT:roundtrip:LAST:Time\\:%3.2lf ms\\j",
  "GPRINT:loss:MAX:Loss\\:%3.2lf%%",
  "GPRINT:loss:AVERAGE:Loss\\:%3.2lf%%",
  "GPRINT:loss:LAST:Loss\\:%3.2lf%%\\j"
  );
  $ERROR = RRDs::error;
  print "Error in RRD::graph for Link Quality: $ERROR\n" if $ERROR;
}

sub updatehddgraph {
  my $disk = $_[0];
  my $period = $_[1];

  RRDs::graph ("$graphs/hddtemp-$disk-$period.png",
  "--start", "-1$period", "-aPNG", "-i", "-z",
  "--alt-y-grid", "-w 600", "-h 100",
  "--color", "SHADEA".$color{"color19"},
  "--color", "SHADEB".$color{"color19"},
  "--color", "BACK".$color{"color21"},
  "-t $tr{'harddisk temperature'} ($tr{'graph per'} $tr{$period})",
  "DEF:temperature=$rrdlog/hddtemp-$disk.rrd:temperature:AVERAGE",
  "LINE2:temperature".$color{"color11"}.":$tr{'hdd temperature in'} ?C",
  "GPRINT:temperature:MAX:$tr{'maximal'}\\:%3.0lf ?C",
  "GPRINT:temperature:AVERAGE:$tr{'average'}\\:%3.0lf ?C",
  "GPRINT:temperature:LAST:$tr{'current'}\\:%3.0lf ?C",
  );
  $ERROR = RRDs::error;
  print "Error in RRD::graph for hdd-$disk: $ERROR\n" if $ERROR;
}

sub updatetempgraph
{
  my $type   = "temp";
  my $period = $_[0];

  @args = ("$graphs/mbmon-$type-$period.png", "--start", "-1$period", "-aPNG", "-i", "-z",
    "--alt-y-grid", "-w 600", "-h 100", "--alt-autoscale",
    "--color", "SHADEA".$color{"color19"},
    "--color", "SHADEB".$color{"color19"},
    "--color", "BACK".$color{"color21"},
    "-t $tr{'mbmon temp'} ($tr{'graph per'} $tr{$period})" );

  $count = 10;
  foreach $key ( sort(keys %mbmon_values) ) 
  {
    if ( (index($key, $type) != -1) && ($mbmon_settings{'LINE-'.$key} eq 'on') )
    {
      if ( !defined($mbmon_settings{'LABEL-'.$key}) || ($mbmon_settings{'LABEL-'.$key} eq '') )
      {
        $mbmon_settings{'LABEL-'.$key} = $key;
      }

      push(@args, "DEF:$key=$rrdlog/mbmon.rrd:$key:AVERAGE");
      push(@args, "LINE2:$key$color{$count}:$mbmon_settings{'LABEL-'.$key} $tr{'mbmon temp in'} ?C");
      push(@args, "GPRINT:$key:MAX:$tr{'maximal'}\\:%5.1lf ?C");
      push(@args, "GPRINT:$key:AVERAGE:$tr{'average'}\\:%5.1lf ?C");
      push(@args, "GPRINT:$key:LAST:$tr{'current'}\\:%5.1lf ?C\\j");

      $count++;
    }
  }

  if ( $count > 1 )
  {
    RRDs::graph ( @args );
    $ERROR = RRDs::error;
    print("Error in RRD::graph for temp: $ERROR\n")if $ERROR;
  }
}

sub updatefangraph
{
  my $type   = "fan";
  my $period = $_[0];

  @args = ("$graphs/mbmon-$type-$period.png", "--start", "-1$period", "-aPNG", "-i", "-z",
    "--alt-y-grid", "-w 600", "-h 100", "--alt-autoscale",
    "--color", "SHADEA".$color{"color19"},
    "--color", "SHADEB".$color{"color19"},
    "--color", "BACK".$color{"color21"},
    "-t $tr{'mbmon temp'} ($tr{'graph per'} $tr{$period})" );

  $count = 10;
  foreach $key ( sort(keys %mbmon_values) ) 
  {
    if ( (index($key, $type) != -1) && ($mbmon_settings{'LINE-'.$key} eq 'on') )
    {
      if ( !defined($mbmon_settings{'LABEL-'.$key}) || ($mbmon_settings{'LABEL-'.$key} eq '') )
      {
        $mbmon_settings{'LABEL-'.$key} = $key;
      }

      push(@args, "DEF:$key=$rrdlog/mbmon.rrd:$key:AVERAGE");
      push(@args, "LINE2:$key$color{$count}:$mbmon_settings{'LABEL-'.$key} $tr{'mbmon fan in'} rpm");
      push(@args, "GPRINT:$key:MAX:$tr{'maximal'}\\:%5.0lf rpm");
      push(@args, "GPRINT:$key:AVERAGE:$tr{'average'}\\:%5.0lf rpm");
      push(@args, "GPRINT:$key:LAST:$tr{'current'}\\:%5.0lf rpm\\j");

      $count++;
    }
  }

  if ( $count > 1 )
  {
    RRDs::graph ( @args );
    $ERROR = RRDs::error;
    print("Error in RRD::graph for temp: $ERROR\n")if $ERROR;
  }
}

sub updatevoltgraph
{
  my $type   = "volt";
  my $period = $_[0];

  @args = ("$graphs/mbmon-$type-$period.png", "--start", "-1$period", "-aPNG", "-i", "-z",
    "--alt-y-grid", "-w 600", "-h 100", "--alt-autoscale",
    "--color", "SHADEA".$color{"color19"},
    "--color", "SHADEB".$color{"color19"},
    "--color", "BACK".$color{"color21"},
    "-t $tr{'mbmon temp'} ($tr{'graph per'} $tr{$period})" );

  $count = 10;
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
      push(@args, "LINE2:$key$color{$count}:$mbmon_settings{'LABEL-'.$key} V");
      push(@args, "GPRINT:$key:MAX:$tr{'maximal'}\\:%5.2lf V");
      push(@args, "GPRINT:$key:AVERAGE:$tr{'average'}\\:%5.2lf V");
      push(@args, "GPRINT:$key:LAST:$tr{'current'}\\:%5.2lf V\\j");

      $count++;
    }
  }

  if ( $count > 1 )
  {
    RRDs::graph ( @args );
    $ERROR = RRDs::error;
    print("Error in RRD::graph for temp: $ERROR\n")if $ERROR;
  }
}
