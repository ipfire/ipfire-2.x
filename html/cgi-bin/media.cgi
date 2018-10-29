#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2013  IPFire Team  <info@ipfire.org>                     #
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
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "${General::swroot}/graphs.pl";

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::colourred} );
undef (@dummy);

my %cgiparams=();

my @querry = split(/\?/,$ENV{'QUERY_STRING'});
$querry[0] = '' unless defined $querry[0];
$querry[1] = 'hour' unless defined $querry[1];

my @devices = `ls -1 /sys/block | grep -E '^sd|^mmcblk|^nvme|^xvd|^vd|^md' | sort | uniq`;

if ( $querry[0] =~ "sd?" || $querry[0] =~ "mmcblk?" || $querry[0] =~ "nvme?n?" || $querry[0] =~ "xvd??" || $querry[0] =~ "vd?" || $querry[0] =~ "md*" ){
	print "Content-type: image/png\n\n";
	binmode(STDOUT);
	
	&Graphs::updatediskgraph($querry[0],$querry[1]);
}else{
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'media information'}, 1, '');
	&Header::openbigbox('100%', 'left');

	foreach (@devices) {
		my $device = $_;
		chomp($device);
		my @array = split(/\//,$device);
		&Header::openbox('100%', 'center', "$array[$#array] $Lang::tr{'graph'}");
		diskbox($array[$#array]);
		&Graphs::makegraphbox("media.cgi",$array[$#array],"day");
		&Header::closebox();
	}

	
	&Header::openbox('100%', 'center', $Lang::tr{'disk usage'});
	print "<table width='95%' cellspacing='5'>\n";
	open(DF,'/bin/df -P -B M -x rootfs|');
	while(<DF>){
		if ($_ =~ m/^Filesystem/ ){
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
		}else{
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

	open(DF,'/bin/df -P -i -x rootfs|');
	while(<DF>){
		if ($_ =~ m/^Filesystem/ ){
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
		}else{
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

	for(my $i = 1; $i <= $#iostat1; $i++){
		if ( $i eq '1' ){
			print "<tr><td align='center' class='boldbase'><b>$Lang::tr{'device'}</b></td><td align='center' class='boldbase'><b>$Lang::tr{'MB read'}</b></td><td align='center' class='boldbase'><b>$Lang::tr{'MB written'}</b></td></tr>";
		}else{
			print "<tr><td align='center'>$iostat1[$i]</td><td align='center'>$iostat2[$i]</td><td align='center'>$iostat3[$i]</td></tr>";
		}
	}
	print "</table>\n";
	&Header::closebox();

	&Header::closebigbox();
	&Header::closepage();
}

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
	chomp $disk;
	my @status;
	if (-e "/var/run/hddstatus"){
		open(DATEI, "</var/run/hddstatus") || die "Datei nicht gefunden";
		my  @diskstate = <DATEI>;
		close(DATEI);

		foreach (@diskstate){
			if ( $_ =~/$disk/ ){@status = split(/-/,$_);}
		}

		if ( $status[1]=~/standby/){
			my $ftime = localtime((stat("/var/run/hddshutdown-$disk"))[9]);
			print"<b>Disk $disk status:<span style='color:#FF0000'>".$status[1]."</b> ($Lang::tr{'since'} $ftime)";
		}else{
			print"<b>Disk $disk status:<span style='color:#00FF00'>".$status[1]."</b>";
		}
	}

	my $smart = `/usr/local/bin/smartctrl $disk`;
	$smart = &Header::cleanhtml($smart);
	print <<END
<br /><input type="button" onClick="swapVisibility('smart_$disk')" value="$Lang::tr{'smart information'}" />
<div id='smart_$disk' style='display: none'>
	<hr /><table border='0'><tr><td align='left'><pre>$smart</pre></table>
</div>
END
;
}
