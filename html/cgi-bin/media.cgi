#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
#

use strict;

# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::colourred} );
undef (@dummy);

my %cgiparams=();

&Header::showhttpheaders();

&Header::getcgihash(\%cgiparams);

&Header::openpage($Lang::tr{'media information'}, 1, '');

&Header::openbigbox('100%', 'left');

&Header::openbox('100%', 'center', "Disk $Lang::tr{'graph'}");
if (-e "$Header::graphdir/disk-day.png") {
	my $ftime = localtime((stat("$Header::graphdir/disk-day.png"))[9]);
	print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
	print "<a href='/cgi-bin/graphs.cgi?graph=disk'>";
	print "<img alt='' src='/graphs/disk-day.png' border='0' />";
	print "</a>";
} else {
	print $Lang::tr{'no information available'};
}
print "<br />\n";
&Header::closebox();

my @devices = `kudzu -qps -c HD | grep device: | cut -d" " -f2 | sort | uniq`;

foreach (@devices) {
	my $device = $_;
	chomp($device);
	diskbox("$device");
}

&Header::openbox('100%', 'center', $Lang::tr{'disk usage'});
print "<table width='95%' cellspacing='5'>\n";
open(DF,'/bin/df -B M -x rootfs|');
while(<DF>)
{
        if ($_ =~ m/^Filesystem/ )
        {
                print <<END
<tr>
<td align='center' class='boldbase'><b>$Lang::tr{'device'}</b></td>
<td align='center' class='boldbase'><b>$Lang::tr{'mounted on'}</b></td>
<td align='center' class='boldbase'><b>$Lang::tr{'size'}</b></td>
<td align='center' class='boldbase'><b>$Lang::tr{'used'}</b></td>
<td align='center' class='boldbase'><b>$Lang::tr{'free'}</b></td>
<td align='left' class='boldbase' colspan='2'><b>$Lang::tr{'percentage'}</b></td>
</tr>
END
;
        }
        else
        {
                my ($device,$size,$used,$free,$percent,$mount) = split;
                print <<END
<tr>
<td align='center'>$device</td>
<td align='center'>$mount</td>
<td align='center'>$size</td>
<td align='center'>$used</td>
<td align='center'>$free</td>
<td align='left'>
END
;
                &percentbar($percent);
                print <<END
</td>
<td align='left'>$percent</td>
</tr>
END
;
        }
}
close DF;
print "<tr><td colspan='7'>&nbsp;\n<tr><td colspan='7'><h3>Inodes</h3>\n";

open(DF,'/bin/df -i -x rootfs|');
while(<DF>)
{
   if ($_ =~ m/^Filesystem/ )
   {
      print <<END
<tr>
<td align='center' class='boldbase'><b>$Lang::tr{'device'}</b></td>
<td align='center' class='boldbase'><b>$Lang::tr{'mounted on'}</b></td>
<td align='center' class='boldbase'><b>$Lang::tr{'size'}</b></td>
<td align='center' class='boldbase'><b>$Lang::tr{'used'}</b></td>
<td align='center' class='boldbase'><b>$Lang::tr{'free'}</b></td>
<td align='left' class='boldbase' colspan='2'><b>$Lang::tr{'percentage'}</b></td>
</tr>
END
;
   }
   else
   {
      my ($device,$size,$used,$free,$percent,$mount) = split;
      print <<END
<tr>
<td align='center'>$device</td>
<td align='center'>$mount</td>
<td align='center'>$size</td>
<td align='center'>$used</td>
<td align='center'>$free</td>
<td>
END
;
      &percentbar($percent);
      print <<END
</td>
<td align='left'>$percent</td>
</tr>
END
;
   }
}
close DF;
my @iostat1 = qx(/usr/bin/iostat -dm -p | grep -v "Linux" | awk '{print \$1}');
my @iostat2 = qx(/usr/bin/iostat -dm -p | grep -v "Linux" | awk '{print \$5}');
my @iostat3 = qx(/usr/bin/iostat -dm -p | grep -v "Linux" | awk '{print \$6}');
print "<tr><td colspan='3'>&nbsp;\n<tr><td colspan='3'><h3>transfers</h3></td></tr>";
my $i=0;

for(my $i = 1; $i <= $#iostat1; $i++)
{
if ( $i eq '1' ){print "<tr><td align='center' class='boldbase'><b>Device</b></td><td align='center' class='boldbase'><b>MB read</b></td><td align='center' class='boldbase'><b>MB writen</b></td></tr>";}
else {print "<tr><td align='center'>@iostat1[$i]</td><td align='center'>@iostat2[$i]</td><td align='center'>@iostat3[$i]</td></tr>";}
}
print "</table>\n";
&Header::closebox();

&Header::closebigbox();

&Header::closepage();

sub percentbar
{
  my $percent = $_[0];
  my $fg = '#a0a0a0';
  my $bg = '#e2e2e2';

  if ($percent =~ m/^(\d+)%$/ )
  {
    print <<END
<table width='100' border='1' cellspacing='0' cellpadding='0' style='border-width:1px;border-style:solid;border-color:$fg;width:100px;height:10px;'>
<tr>
END
;
    if ($percent eq "100%") {
      print "<td width='100%' bgcolor='$fg' style='background-color:$fg;border-style:solid;border-width:1px;border-color:$bg'>"
    } elsif ($percent eq "0%") {
      print "<td width='100%' bgcolor='$bg' style='background-color:$bg;border-style:solid;border-width:1px;border-color:$bg'>"
    } else {
      print "<td width='$percent' bgcolor='$fg' style='background-color:$fg;border-style:solid;border-width:1px;border-color:$bg'></td><td width='" . (100-$1) . "%' bgcolor='$bg' style='background-color:$bg;border-style:solid;border-width:1px;border-color:$bg'>"
    }
    print <<END
<img src='/images/null.gif' width='1' height='1' alt='' /></td></tr></table>
END
;
  }
}

sub diskbox {
 my $disk = $_[0];
    if (-e "$Header::graphdir/disk-$disk-day.png") {
	 	  &Header::openbox('100%', 'center', "Disk /dev/$disk $Lang::tr{'graph'}");
		  my $ftime = localtime((stat("$Header::graphdir/disk-$disk-day.png"))[9]);
		  print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
		  print "<a href='/cgi-bin/graphs.cgi?graph=disk-$disk'>";
		  print "<img alt='' src='/graphs/disk-$disk-day.png' border='0' />";
		  print "</a>";
		  print "<br />\n";
		  if (-e "/usr/local/bin/hddshutdown-state") {
		    system("/usr/local/bin/hddshutdown-state $disk");
		  }
		  my $smart = `smartctrl $disk`;
			$smart = &Header::cleanhtml($smart);
			print <<END
				<br /><input type="button" onClick="swapVisibility('smart_$disk')" value="$Lang::tr{'smart information'}" />
				<div id='smart_$disk' style='display: none'>
					<hr /><table border=0><tr><td align=left><pre>$smart</pre></table>
				</div>
END
;
      &Header::closebox();
		}

  
}
