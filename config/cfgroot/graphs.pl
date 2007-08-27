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
&General::readhash("/var/log/mbmon-values", \%mbmon_values);

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
        "--start", "-1$period", "-aPNG", "-i", "-z", "-W www.ipfire.org",
        "--alt-y-grid", "-w 600", "-h 100", "-l 0", "-u 100", "-r",
        "--color", "SHADEA".$color{"color19"},
        "--color", "SHADEB".$color{"color19"},
        "--color", "BACK".$color{"color21"},
        "-t $Lang::tr{'cpu usage per'} $Lang::tr{$period}",
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
        "COMMENT:$Lang::tr{'caption'}\\t\\t\\t   ",
        "COMMENT:$Lang::tr{'maximal'}",
        "COMMENT:$Lang::tr{'average'}",
        "COMMENT:$Lang::tr{'minimal'}",
        "COMMENT:$Lang::tr{'current'}\\j",
        "AREA:iowaitpct".$color{"color14"}.":$Lang::tr{'iowait'}",
        "GPRINT:iowaitpct:MAX:%3.2lf%%",
        "GPRINT:iowaitpct:AVERAGE:%3.2lf%%",
        "GPRINT:iowaitpct:MIN:%3.2lf%%",
        "GPRINT:iowaitpct:LAST:%3.2lf%%\\j",
        "STACK:irqpct".$color{"color23"}.":$Lang::tr{'cpu irq usage'}",
        "GPRINT:irqpct:MAX:%3.2lf%%",
        "GPRINT:irqpct:AVERAGE:%3.2lf%%",
        "GPRINT:irqpct:MIN:%3.2lf%%",
        "GPRINT:irqpct:LAST:%3.2lf%%\\j",
        "STACK:userpct".$color{"color11"}.":$Lang::tr{'user cpu usage'}",
        "GPRINT:userpct:MAX:%3.2lf%%",
        "GPRINT:userpct:AVERAGE:%3.2lf%%",
        "GPRINT:userpct:MIN:%3.2lf%%",
        "GPRINT:userpct:LAST:%3.2lf%%\\j",
        "STACK:systempct".$color{"color13"}.":$Lang::tr{'system cpu usage'}",
        "GPRINT:systempct:MAX:%3.2lf%%",
        "GPRINT:systempct:AVERAGE:%3.2lf%%",
        "GPRINT:systempct:MIN:%3.2lf%%",
        "GPRINT:systempct:LAST:%3.2lf%%\\j",
        "STACK:idlepct".$color{"color12"}.":$Lang::tr{'idle cpu usage'}",
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
        "-w 600", "-h 100", "-i", "-z", "-W www.ipfire.org", "-l 0", "-r", "--alt-y-grid",
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
        "--start", "-1$period", "-aPNG", "-i", "-z", "-W www.ipfire.org",
        "--alt-y-grid", "-w 600", "-h 100", "-l 0", "-u 100", "-r",
        "--color", "SHADEA".$color{"color19"},
        "--color", "SHADEB".$color{"color19"},
        "--color", "BACK".$color{"color21"},
        "-t $Lang::tr{'memory usage per'} $Lang::tr{$period}",
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
        "COMMENT:$Lang::tr{'caption'}\\t\\t\\t",
        "COMMENT:$Lang::tr{'maximal'}",
        "COMMENT:$Lang::tr{'average'}",
        "COMMENT:$Lang::tr{'minimal'}",
        "COMMENT:$Lang::tr{'current'}\\j",
        "AREA:usedpct".$color{"color11"}.":$Lang::tr{'used memory'}",
        "GPRINT:usedpct:MAX:%3.2lf%%",
        "GPRINT:usedpct:AVERAGE:%3.2lf%%",
        "GPRINT:usedpct:MIN:%3.2lf%%",
        "GPRINT:usedpct:LAST:%3.2lf%%\\j",
        "STACK:sharedpct".$color{"color13"}.":$Lang::tr{'shared memory'}",
        "GPRINT:sharedpct:MAX:%3.2lf%%",
        "GPRINT:sharedpct:AVERAGE:%3.2lf%%",
        "GPRINT:sharedpct:MIN:%3.2lf%%",
        "GPRINT:sharedpct:LAST:%3.2lf%%\\j",
        "STACK:bufferpct".$color{"color23"}.":$Lang::tr{'buffered memory'}",
        "GPRINT:bufferpct:MAX:%3.2lf%%",
        "GPRINT:bufferpct:AVERAGE:%3.2lf%%",
        "GPRINT:bufferpct:MIN:%3.2lf%%",
        "GPRINT:bufferpct:LAST:%3.2lf%%\\j",
        "STACK:cachepct".$color{"color14"}.":$Lang::tr{'cached memory'}",
        "GPRINT:cachepct:MAX:%3.2lf%%",
        "GPRINT:cachepct:AVERAGE:%3.2lf%%",
        "GPRINT:cachepct:MIN:%3.2lf%%",
        "GPRINT:cachepct:LAST:%3.2lf%%\\j",
        "STACK:freepct".$color{"color12"}.":$Lang::tr{'free memory'}",
        "GPRINT:freepct:MAX:%3.2lf%%",
        "GPRINT:freepct:AVERAGE:%3.2lf%%",
        "GPRINT:freepct:MIN:%3.2lf%%",
        "GPRINT:freepct:LAST:%3.2lf%%\\j");
        $ERROR = RRDs::error;
        print "Error in RRD::graph for mem: $ERROR\n" if $ERROR;

        RRDs::graph ("$graphs/swap-$period.png",
        "--start", "-1$period", "-aPNG", "-i", "-z", "-W www.ipfire.org",
        "--alt-y-grid", "-w 600", "-h 100", "-l 0", "-u 100", "-r",
        "--color", "SHADEA".$color{"color19"},
        "--color", "SHADEB".$color{"color19"},
        "--color", "BACK".$color{"color21"},
        "-t $Lang::tr{'swap usage per'} $Lang::tr{$period}",
        "DEF:used=$rrdlog/mem.rrd:swapused:AVERAGE",
        "DEF:free=$rrdlog/mem.rrd:swapfree:AVERAGE",
        "CDEF:total=used,free,+",
        "CDEF:usedpct=100,used,total,/,*",
        "CDEF:freepct=100,free,total,/,*",
        "COMMENT:$Lang::tr{'caption'}\\t\\t",
        "COMMENT:$Lang::tr{'maximal'}",
        "COMMENT:$Lang::tr{'average'}",
        "COMMENT:$Lang::tr{'minimal'}",
        "COMMENT:$Lang::tr{'current'}\\j",
        "AREA:usedpct".$color{"color11"}.":$Lang::tr{'used swap'}",
        "GPRINT:usedpct:MAX:%3.2lf%%",
        "GPRINT:usedpct:AVERAGE:%3.2lf%%",
        "GPRINT:usedpct:MIN:%3.2lf%%",
        "GPRINT:usedpct:LAST:%3.2lf%%\\j",
        "STACK:freepct".$color{"color12"}.":$Lang::tr{'free swap'}",
        "GPRINT:freepct:MAX:%3.2lf%%",
        "GPRINT:freepct:AVERAGE:%3.2lf%%",
        "GPRINT:freepct:MIN:%3.2lf%%",
        "GPRINT:freepct:LAST:%3.2lf%%\\j");
        $ERROR = RRDs::error;
        print "Error in RRD::graph for swap: $ERROR\n" if $ERROR;
}

sub updatediskgraph {
        my $period    = $_[0];
        my $disk    = $_[1];

        RRDs::graph ("$graphs/disk-$disk-$period.png",
        "--start", "-1$period", "-aPNG", "-i", "-z", "-W www.ipfire.org",
        "--alt-y-grid", "-w 600", "-h 100", "-l 0", "-r",
        "--color", "SHADEA".$color{"color19"},
        "--color", "SHADEB".$color{"color19"},
        "--color", "BACK".$color{"color21"},
        "-t $Lang::tr{'disk access per'} $Lang::tr{$period} $disk",
        "DEF:read=$rrdlog/disk-$disk.rrd:readsect:AVERAGE",
        "DEF:write=$rrdlog/disk-$disk.rrd:writesect:AVERAGE",
        "AREA:read".$color{"color11"}.":$Lang::tr{'sectors read from disk per second'}",
        "STACK:write".$color{"color12"}.":$Lang::tr{'sectors written to disk per second'}\\j",
        "COMMENT: \\j",
        "COMMENT:$Lang::tr{'maximal'}",
        "COMMENT:$Lang::tr{'average'}",
        "COMMENT:$Lang::tr{'current'}\\j",
        "GPRINT:read:MAX:$Lang::tr{'read sectors'}\\:%8.0lf",
        "GPRINT:read:AVERAGE:$Lang::tr{'read sectors'}\\:%8.0lf",
        "GPRINT:read:LAST:$Lang::tr{'read sectors'}\\:%8.0lf\\j",
        "GPRINT:write:MAX:$Lang::tr{'written sectors'}\\:%8.0lf",
        "GPRINT:write:AVERAGE:$Lang::tr{'written sectors'}\\:%8.0lf",
        "GPRINT:write:LAST:$Lang::tr{'written sectors'}\\:%8.0lf\\j");
        $ERROR = RRDs::error;
        print "Error in RRD::graph for disk: $ERROR\n" if $ERROR;
}

sub updateifgraph {
  my $interface = $_[0];
  my $period    = $_[1];

  RRDs::graph ("$graphs/$interface-$period.png",
  "--start", "-1$period", "-aPNG", "-i", "-z", "-W www.ipfire.org",
  "--alt-y-grid", "-w 600", "-h 100",
  "--color", "SHADEA".$color{"color19"},
  "--color", "SHADEB".$color{"color19"},
  "--color", "BACK".$color{"color21"},
  "-t $Lang::tr{'traffic on'} $interface ($Lang::tr{'graph per'} $Lang::tr{$period})",
  "-v$Lang::tr{'bytes per second'}",
  "DEF:incoming=$rrdlog/$interface.rrd:incoming:AVERAGE",
  "DEF:outgoing=$rrdlog/$interface.rrd:outgoing:AVERAGE",
  "AREA:incoming".$color{"color11"}.":$Lang::tr{'incoming traffic in bytes per second'}",
  "AREA:outgoing".$color{"color12"}.":$Lang::tr{'outgoing traffic in bytes per second'}\\j",
  "COMMENT: \\j",
  "COMMENT:$Lang::tr{'maximal'}",
  "COMMENT:$Lang::tr{'average'}",
  "COMMENT:$Lang::tr{'minimal'}",
  "COMMENT:$Lang::tr{'current'}\\j",
  "GPRINT:incoming:MAX:$Lang::tr{'in'}\\:%8.3lf %sBps",
  "GPRINT:incoming:AVERAGE:$Lang::tr{'in'}\\:%8.3lf %sBps",
  "GPRINT:incoming:MIN:$Lang::tr{'in'}\\:%8.3lf %sBps",
  "GPRINT:incoming:LAST:$Lang::tr{'in'}\\:%8.3lf %sBps\\j",
  "GPRINT:outgoing:MAX:$Lang::tr{'out'}\\:%8.3lf %sBps",
  "GPRINT:outgoing:AVERAGE:$Lang::tr{'out'}\\:%8.3lf %sBps",
  "GPRINT:outgoing:MIN:$Lang::tr{'out'}\\:%8.3lf %sBps",
  "GPRINT:outgoing:LAST:$Lang::tr{'out'}\\:%8.3lf %sBps\\j");
  $ERROR = RRDs::error;
  print "Error in RRD::graph for $interface: $ERROR\n" if $ERROR;
}

sub updatefwhitsgraph {
  my $period = $_[0];

  RRDs::graph ("$graphs/firewallhits-$period-area.png",
  "--start", "-1$period", "-aPNG", "-i", "-z", "-W www.ipfire.org",
  "--alt-y-grid", "-w 600", "-h 100",
  "--color", "SHADEA".$color{"color19"},
  "--color", "SHADEB".$color{"color19"},
  "--color", "BACK".$color{"color21"},
  "-t $Lang::tr{'firewall hits per'} $Lang::tr{$period}",
  "DEF:amount=$rrdlog/firewallhits.rrd:amount:AVERAGE",
  "DEF:portamount=$rrdlog/firewallhits.rrd:portamount:AVERAGE",
  "COMMENT:$Lang::tr{'caption'}\\t\\t\\t",
  "COMMENT:$Lang::tr{'maximal'}",
  "COMMENT:$Lang::tr{'average'}",
  "COMMENT:$Lang::tr{'minimal'}",
  "COMMENT:$Lang::tr{'current'}\\j",
  "AREA:amount".$color{"color24"}.":$Lang::tr{'firewallhits'}/5 min",
  "GPRINT:amount:MAX:%2.2lf %S",
  "GPRINT:amount:AVERAGE:%2.2lf %S",
  "GPRINT:amount:MIN:%2.2lf %S",
  "GPRINT:amount:LAST:%2.2lf %S\\j",
  "STACK:portamount".$color{"color25"}.":$Lang::tr{'portscans'}/5 min",
  "GPRINT:portamount:MAX:%2.2lf %S",
  "GPRINT:portamount:MIN:%2.2lf %S",
  "GPRINT:portamount:AVERAGE:%2.2lf %S",
  "GPRINT:portamount:LAST:%2.2lf %S\\j");
  $ERROR = RRDs::error;
  print "Error in RRD::graph for Firewallhits: $ERROR\n" if $ERROR;
}

sub updatelqgraph {
  my $period    = $_[0];
  RRDs::graph ("$graphs/lq-$period.png",
  "--start", "-1$period", "-aPNG", "-i", "-z", "-W www.ipfire.org",
  "--alt-y-grid", "-w 600", "-h 100", "-l 0", "-r",
  "-t $Lang::tr{'linkq'} ($Lang::tr{'graph per'} $Lang::tr{$period})",
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
  "COMMENT:$Lang::tr{'maximal'}",
  "COMMENT:$Lang::tr{'average'}",
  "COMMENT:$Lang::tr{'minimal'}",
  "COMMENT:$Lang::tr{'current'}\\j",
  "LINE1:roundtrip#707070:",
  "GPRINT:roundtrip:MAX:Time\\:%3.2lf ms",
  "GPRINT:roundtrip:AVERAGE:Time\\:%3.2lf ms",
  "GPRINT:roundtrip:MIN:Time\\:%3.2lf ms",
  "GPRINT:roundtrip:LAST:Time\\:%3.2lf ms\\j",
  "GPRINT:loss:MAX:Loss\\:%3.2lf%%",
  "GPRINT:loss:AVERAGE:Loss\\:%3.2lf%%",
  "GPRINT:loss:MIN:Loss\\:%3.2lf%%",
  "GPRINT:loss:LAST:Loss\\:%3.2lf%%\\j"
  );
  $ERROR = RRDs::error;
  print "Error in RRD::graph for Link Quality: $ERROR\n" if $ERROR;
}

sub updatehddgraph {

  my $disk = $_[0];
  my $period = $_[1];

  RRDs::graph ("$graphs/hddtemp-$disk-$period.png",
  "--start", "-1$period", "-aPNG", "-i", "-z", "-W www.ipfire.org",
  "--alt-y-grid", "-w 600", "-h 100",
  "--color", "SHADEA".$color{"color19"},
  "--color", "SHADEB".$color{"color19"},
  "--color", "BACK".$color{"color21"},
  "-t $Lang::tr{'harddisk temperature'} ($Lang::tr{'graph per'} $Lang::tr{$period})",
  "DEF:temperature=$rrdlog/hddtemp-$disk.rrd:temperature:AVERAGE",
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
    "--alt-y-grid", "-w 600", "-h 100", "--alt-autoscale",
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
    "--alt-y-grid", "-w 600", "-h 100", "--alt-autoscale",
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
    "--alt-y-grid", "-w 600", "-h 100", "--alt-autoscale",
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
