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

my %mbmonsettings = ();
my %cgiparams=();
my @cgigraphs=();

&Header::showhttpheaders();

my $graphdir = "/srv/web/ipfire/html/graphs";

$ENV{'QUERY_STRING'} =~ s/&//g;
@cgigraphs = split(/graph=/,$ENV{'QUERY_STRING'});
$cgigraphs[1] = '' unless defined $cgigraphs[1];

my @mbmongraphs = ();
if ( -e "/var/log/rrd/collectd/localhost/mbmon" ){@mbmongraphs = `ls /var/log/rrd/collectd/localhost/mbmon/`;}

&Header::getcgihash(\%mbmonsettings);

if ( $mbmonsettings{'ACTION'} eq $Lang::tr{'save'} ) {
	 foreach (@mbmongraphs){
	 				 chomp($_);
 					 my @name=split(/\./,$_);
					 if ( $mbmonsettings{'LINE-'.$name[0]} ne "on" ){$mbmonsettings{'LINE-'.$name[0]} = 'off';}
					 elsif ( $mbmonsettings{'LINE-'.$name[0]} eq "on" ){$mbmonsettings{'LINE-'.$name[0]} = 'checked';}
	 }
	 &General::writehash("${General::swroot}/mbmon/settings", \%mbmonsettings);
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
									if (-e "$graphdir/mbmon-$_-day.png"){
											my $ftime = localtime((stat("$graphdir/mbmon-$_-day.png"))[9]);
											print "<center>";
											print "<b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
	  									print "<a href='/cgi-bin/hardwaregraphs.cgi?graph=$_'>";
											print "<img src='/graphs/mbmon-$_-day.png' border='0' />";
											print "</a><hr />";
									}
									else{print $Lang::tr{'no information available'};}
									&Header::closebox();
	}
	if ( -e "/var/log/rrd/collectd/localhost/mbmon" ){mbmonbox();}
}

&Header::closebigbox();
&Header::closepage();

sub hddtempbox {
 my $disk = $_[0];
    if (-e "$graphdir/hddtemp-$disk-week.png") {

 	  &Header::openbox('100%', 'center', "Disk $disk $Lang::tr{'graph'}");
	  my $ftime = localtime((stat("$graphdir/hddtemp-$disk-week.png"))[9]);
	  print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
	  print "<img src='/graphs/hddtemp-$disk-day.png' border='0' />";
	  print "<br />\n";
        &Header::closebox();
  }
      if (-e "$graphdir/hddtemp-$disk-month.png") {

 	  &Header::openbox('100%', 'center', "Disk $disk $Lang::tr{'graph'}");
	  my $ftime = localtime((stat("$graphdir/hddtemp-$disk-month.png"))[9]);
	  print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
	  print "<img src='/graphs/hddtemp-$disk-day.png' border='0' />";
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
	if (-e "$graphdir/mbmon-$graph-week.png"){
			 my $ftime = localtime((stat("$graphdir/mbmon-$graph-day.png"))[9]);
			 print "<center>";
			 print "<b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
			 print "<img src='/graphs/mbmon-$graph-day.png' border='0' /><hr />";
	 }
	 else{print $Lang::tr{'no information available'};}
	 &Header::closebox();
	&Header::openbox('100%', 'center', "$graph $Lang::tr{'graph'}");
	if (-e "$graphdir/mbmon-$graph-month.png"){
			 my $ftime = localtime((stat("$graphdir/mbmon-$graph-month.png"))[9]);
			 print "<center>";
			 print "<b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
			 print "<img src='/graphs/mbmon-$graph-month.png' border='0' /><hr />";
	 }
	 else{print $Lang::tr{'no information available'};}
	 &Header::closebox();
	&Header::openbox('100%', 'center', "$graph $Lang::tr{'graph'}");
	if (-e "$graphdir/mbmon-$graph-year.png"){
			 my $ftime = localtime((stat("$graphdir/mbmon-$graph-year.png"))[9]);
			 print "<center>";
			 print "<b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
			 print "<img src='/graphs/mbmon-$graph-year.png' border='0' /><hr />";
	 }
	 else{print $Lang::tr{'no information available'};}
	 &Header::closebox();
}

sub mbmonbox{

 foreach (@mbmongraphs){
 				 chomp($_);
				 my @name=split(/\./,$_);my $label = $name[0]; $label=~ s/-//;
				 $mbmonsettings{'LABEL-'.$name[0]}="$label";
				 $mbmonsettings{'LINE-'.$name[0]}="checked";
				 }
 &General::readhash("${General::swroot}/mbmon/settings", \%mbmonsettings);
 
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
 foreach (@mbmongraphs){
 				 chomp($_);my @name=split(/\./,$_);
				 print("<tr><td align='right'><input type='checkbox' name='LINE-$name[0]' $mbmonsettings{'LINE-'.$name[0]} /></td>");
 				 print("<td><input type='text' name='LABEL-$name[0]' value='$mbmonsettings{'LABEL-'.$name[0]}' size='25' /></td></tr>\n");
  }
 print <<END
 <tr><td align='center' colspan='2' ><input type='submit' name='ACTION' value=$Lang::tr{'save'} /></td></tr>
 </table>
 </form>
END
;
 &Header::closebox();
}
