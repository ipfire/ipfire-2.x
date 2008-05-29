#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007  Michael Tremer & Christian Schmidt                      #
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

my %sensorsettings = ();
my %cgiparams=();
my @cgigraphs=();
my $rrdlog = "/var/log/rrd";

&Header::showhttpheaders();

my $graphdir = "/srv/web/ipfire/html/graphs";

$ENV{'QUERY_STRING'} =~ s/&//g;
@cgigraphs = split(/graph=/,$ENV{'QUERY_STRING'});
$cgigraphs[1] = '' unless defined $cgigraphs[1];

my @sensorsgraphs = ();
my @sensorsdir = `ls -dA $rrdlog/collectd/localhost/sensors-*/`;
foreach (@sensorsdir)
{
	chomp($_);chop($_);
	foreach (`ls $_/*`){
		chomp($_);
		push(@sensorsgraphs,$_);
	}
}

&Header::getcgihash(\%sensorsettings);

if ( $sensorsettings{'ACTION'} eq $Lang::tr{'save'} ) {
	foreach(@sensorsgraphs){
		chomp($_);
			$_ =~ /\/(.*)sensors-(.*)\/(.*)\.rrd/;
			my $label = $2.$3;$label=~ s/-//g;
			if ( $sensorsettings{'LINE-'.$label} ne "on" ){$sensorsettings{'LINE-'.$label} = 'off';}
			elsif ( $sensorsettings{'LINE-'.$label} eq "on" ){$sensorsettings{'LINE-'.$label} = 'checked';}
	}
	 &General::writehash("${General::swroot}/sensors/settings", \%sensorsettings);
}

my @disks = `kudzu -qps -c HD | grep device: | cut -d" " -f2 | sort | uniq`;

&Header::openpage($Lang::tr{'harddisk temperature graphs'}, 1, '');
&Header::openbigbox('100%', 'left');

if ($cgigraphs[1] =~ /hwtemp/) {&Graphs::updatehwtempgraph ("hour");&Graphs::updatehwtempgraph ("week");&Graphs::updatehwtempgraph ("month");&Graphs::updatehwtempgraph ("year");graphbox("hwtemp");}
elsif ($cgigraphs[1] =~ /hwfan/) {&Graphs::updatehwfangraph ("hour");&Graphs::updatehwfangraph ("week");&Graphs::updatehwfangraph ("month");&Graphs::updatehwfangraph ("year");graphbox("hwfan");}
elsif ($cgigraphs[1] =~ /hwvolt/) {&Graphs::updatehwvoltgraph ("hour");&Graphs::updatehwvoltgraph ("week");&Graphs::updatehwvoltgraph ("month");&Graphs::updatehwvoltgraph ("year");graphbox("hwvolt");}
elsif ($cgigraphs[1] =~ /hddtemp/) {
 foreach (@disks){
  my $disk = $_;
  chomp $disk;
  my @array = split(/\//,$disk);
  &Graphs::updatehddgraph ($array[$#array],"week");&Graphs::updatehddgraph ($array[$#array],"month");&Graphs::updatehddgraph ($array[$#array],"year");
  hddtempbox($array[$#array]);
	}
}
else
{
 &Graphs::updatehwtempgraph ("day");&Graphs::updatehwfangraph ("day");&Graphs::updatehwvoltgraph ("day");
 foreach (@disks){
  my $disk = $_;
  chomp $disk;
  my @array = split(/\//,$disk);
  &Graphs::updatehddgraph ($array[$#array],"day");
   	if (-e "$graphdir/hddtemp-$disk-day.png") {

 	  &Header::openbox('100%', 'center', "Disk $disk $Lang::tr{'graph'}");
	  my $ftime = localtime((stat("$graphdir/hddtemp-$disk-day.png"))[9]);
	  print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
	  print "<a href='/cgi-bin/hardwaregraphs.cgi?graph=hddtemp'>";
	  print "<img src='/graphs/hddtemp-$disk-day.png' border='0' />";
		print "</a>";
	  print "<br />\n";
        &Header::closebox();
		}
  }

 my @graphs = ("hwtemp","hwfan","hwvolt");
 foreach (@graphs){
 	&Header::openbox('100%', 'center', "$_ $Lang::tr{'graph'}");
	if (-e "$graphdir/sensors-$_-day.png"){
	    my $ftime = localtime((stat("$graphdir/sensors-$_-day.png"))[9]);
	    print "<center>";
	    print "<b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
	    print "<a href='/cgi-bin/hardwaregraphs.cgi?graph=$_'>";
	    print "<img src='/graphs/sensors-$_-day.png' border='0' />";
	    print "</a><hr />";
	    }
	    else{print $Lang::tr{'no information available'};}
	&Header::closebox();
 }
	sensorsbox();
}

&Header::closebigbox();
&Header::closepage();

sub hddtempbox {
 my $disk = $_[0];
    if (-e "$graphdir/hddtemp-$disk-week.png") {

 	  &Header::openbox('100%', 'center', "Disk $disk $Lang::tr{'graph'}");
	  my $ftime = localtime((stat("$graphdir/hddtemp-$disk-week.png"))[9]);
	  print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
	  print "<img src='/graphs/hddtemp-$disk-week.png' border='0' />";
	  print "<br />\n";
        &Header::closebox();
  }
      if (-e "$graphdir/hddtemp-$disk-month.png") {

 	  &Header::openbox('100%', 'center', "Disk $disk $Lang::tr{'graph'}");
	  my $ftime = localtime((stat("$graphdir/hddtemp-$disk-month.png"))[9]);
	  print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
	  print "<img src='/graphs/hddtemp-$disk-month.png' border='0' />";
	  print "<br />\n";
        &Header::closebox();
  }
      if (-e "$graphdir/hddtemp-$disk-year.png") {

 	  &Header::openbox('100%', 'center', "Disk $disk $Lang::tr{'graph'}");
	  my $ftime = localtime((stat("$graphdir/hddtemp-$disk-year.png"))[9]);
	  print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
	  print "<img src='/graphs/hddtemp-$disk-year.png' border='0' />";
	  print "<br />\n";
        &Header::closebox();
  }
}

sub graphbox {
 my $graph = $_[0];
 
	&Header::openbox('100%', 'center', "$graph $Lang::tr{'graph'}");
	if (-e "$graphdir/sensors-$graph-week.png"){
			 my $ftime = localtime((stat("$graphdir/sensors-$graph-week.png"))[9]);
			 print "<center>";
			 print "<b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
			 print "<img src='/graphs/sensors-$graph-week.png' border='0' /><hr />";
	 }
	 else{print $Lang::tr{'no information available'};}
	 &Header::closebox();
	&Header::openbox('100%', 'center', "$graph $Lang::tr{'graph'}");
	if (-e "$graphdir/sensors-$graph-month.png"){
			 my $ftime = localtime((stat("$graphdir/sensors-$graph-month.png"))[9]);
			 print "<center>";
			 print "<b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
			 print "<img src='/graphs/sensors-$graph-month.png' border='0' /><hr />";
	 }
	 else{print $Lang::tr{'no information available'};}
	 &Header::closebox();
	&Header::openbox('100%', 'center', "$graph $Lang::tr{'graph'}");
	if (-e "$graphdir/sensors-$graph-year.png"){
			 my $ftime = localtime((stat("$graphdir/sensors-$graph-year.png"))[9]);
			 print "<center>";
			 print "<b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
			 print "<img src='/graphs/sensors-$graph-year.png' border='0' /><hr />";
	 }
	 else{print $Lang::tr{'no information available'};}
	 &Header::closebox();
}

sub sensorsbox{

 &Header::openbox('100%', 'center', "$Lang::tr{'mbmon settings'}");
 if ( $cgiparams{'ACTION'} eq $Lang::tr{'save'} ){print "Test";}

 print <<END
 <form method='post' action='$ENV{'SCRIPT_NAME'}'>
 <table width='100%' border='0' cellspacing='5' cellpadding='0' align='center'>
 <tr><td align='right' width='40%'><b>$Lang::tr{'mbmon display'}</b></td>
		 <td align='left'><b>$Lang::tr{'mbmon label'}</b></td>
 </tr>
END
;
foreach (@sensorsgraphs){
		$_ =~ /\/(.*)sensors-(.*)\/(.*)\.rrd/;
		my $label = $2.$3;$label=~ s/-//g;
		$sensorsettings{'LABEL-'.$label}="$label";
		$sensorsettings{'LINE-'.$label}="checked";
		&General::readhash("${General::swroot}/sensors/settings", \%sensorsettings);
		print("<tr><td align='right'><input type='checkbox' name='LINE-$label' $sensorsettings{'LINE-'.$label} /></td>");
 		print("<td><input type='text' name='LABEL-$label' value='$sensorsettings{'LABEL-'.$label}' size='25' /></td></tr>\n");
}
 print <<END
 <tr><td align='center' colspan='2' ><input type='submit' name='ACTION' value=$Lang::tr{'save'} /></td></tr>
 </table>
 </form>
END
;
 &Header::closebox();
}
