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

my %cgiparams=();
my %pppsettings=();
my %netsettings=();
my @cgigraphs=();
my @graphs=();
my $iface='';

&Header::showhttpheaders();

my $graphdir = "/srv/web/ipfire/html/graphs";
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

$ENV{'QUERY_STRING'} =~ s/&//g;
@cgigraphs = split(/graph=/,$ENV{'QUERY_STRING'});
$cgigraphs[1] = '' unless defined $cgigraphs[1];
$cgigraphs[2] = '' unless defined $cgigraphs[2];

if ($cgigraphs[1] =~ /(load)/) {&Graphs::updateloadgraph ("hour");&Graphs::updateloadgraph ("week");&Graphs::updateloadgraph ("month");&Graphs::updateloadgraph ("year");}
if ($cgigraphs[1] =~ /(cpu)/) {&Graphs::updatecpugraph ("hour");&Graphs::updatecpugraph ("week");&Graphs::updatecpugraph ("month");&Graphs::updatecpugraph ("year");}
if ($cgigraphs[1] =~ /(processes)/) {&Graphs::updateprocessesgraph ("hour");&Graphs::updateprocessesgraph ("week");&Graphs::updateprocessesgraph ("month");&Graphs::updateprocessesgraph ("year");}
if ($cgigraphs[1] =~ /(memory|swap)/) {&Graphs::updatememgraph ("hour");&Graphs::updatememgraph ("week");&Graphs::updatememgraph ("month");&Graphs::updatememgraph ("year");}
if ($cgigraphs[1] =~ /disk/){
          my @devices = `kudzu -qps -c HD | grep device: | cut -d" " -f2 | sort | uniq`;
          foreach (@devices) {
	         my $device = $_;
	         chomp($device);
					  &Graphs::updatediskgraph ("hour",$device);
	          &Graphs::updatediskgraph ("week",$device);
	          &Graphs::updatediskgraph ("month",$device);
	          &Graphs::updatediskgraph ("year",$device);}}
if ($cgigraphs[2] ne "" ) {&Graphs::updatepinggraph("hour",$cgigraphs[1]);&Graphs::updatepinggraph("week",$cgigraphs[1]);&Graphs::updatepinggraph("month",$cgigraphs[1]);&Graphs::updatepinggraph("year",$cgigraphs[1]);}
if ($cgigraphs[1] =~ /fwhits/) {&Graphs::updatefwhitsgraph("hour");&Graphs::updatefwhitsgraph("week");&Graphs::updatefwhitsgraph("month");&Graphs::updatefwhitsgraph("year");}
if ($cgigraphs[1] =~ /green/ || $cgigraphs[1] =~ /blue/ || $cgigraphs[1] =~ /ipsec/ || $cgigraphs[1] =~ /orange/ || $cgigraphs[1] =~ /ppp/ || $cgigraphs[1] =~ /red/ ) {&Graphs::updateifgraph($cgigraphs[1], "hour");&Graphs::updateifgraph($cgigraphs[1], "week");&Graphs::updateifgraph($cgigraphs[1], "month");&Graphs::updateifgraph($cgigraphs[1], "year");}

if ($cgigraphs[1] =~ /(network|green|blue|orange|red|ppp|ipsec)/ || $cgigraphs[2] ne "") {
	&Header::openpage($Lang::tr{'network traffic graphs'}, 1, '');
} else {
	&Header::openpage($Lang::tr{'system graphs'}, 1, '');
}

&Header::openbigbox('100%', 'left');

if ($cgigraphs[1] =~ /(green|blue|orange|red|ppp|ipsec|cpu|memory|swap|disk|load|fwhits|processes)/ || $cgigraphs[2] ne "") {
	my $graph = $cgigraphs[1];
	my $graphname = ucfirst(lc($cgigraphs[1]));
	&Header::openbox('100%', 'center', "$graphname $Lang::tr{'graph'}");

	if (-e "$graphdir/${graph}-day.png") {
		my $ftime = localtime((stat("$graphdir/${graph}-day.png"))[9]);
		print "<center>";
		print "<b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br /><hr />\n";
		print "<img alt='' src='/graphs/${graph}-hour.png' border='0' /><hr />";
		print "<img alt='' src='/graphs/${graph}-day.png' border='0' /><hr />";
		print "<img alt='' src='/graphs/${graph}-week.png' border='0' /><hr />";
		print "<img alt='' src='/graphs/${graph}-month.png' border='0' /><hr />";
		print "<img alt='' src='/graphs/${graph}-year.png' border='0' />";
	} else {
		print $Lang::tr{'no information available'};
	}
	&Header::closebox();
} elsif ($cgigraphs[1] =~ /network/) {
	push (@graphs, ('GREEN'));
	if ($netsettings{'BLUE_DEV'}) {
		push (@graphs, ('BLUE')); }
	if ($netsettings{'ORANGE_DEV'}) {
		push (@graphs, ('ORANGE')); }
	push (@graphs, ("RED"));
	push (@graphs, ('gateway'));

	foreach my $graphname (@graphs) {
		&Header::openbox('100%', 'center', "$graphname $Lang::tr{'graph'}");

		if (-e "$graphdir/${graphname}-day.png") {
			my $ftime = localtime((stat("$graphdir/${graphname}-day.png"))[9]);
			print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
			print "<a href='/cgi-bin/graphs.cgi?graph=$graphname'>";
			print "<img alt='' src='/graphs/${graphname}-day.png' border='0' />";
			print "</a>";
		} else {
			print $Lang::tr{'no information available'};
		}
		print "<br />\n";
		&Header::closebox();
	}
}

print "<div align='center'><table width='80%'><tr><td align='center'>";
if ( $cgigraphs[1] eq "cpu" || $cgigraphs[1] eq "load" ) { print "<a href='/cgi-bin/system.cgi'>"; }
elsif ( $cgigraphs[1] eq "memory" || $cgigraphs[1] eq "swap" ) { print "<a href='/cgi-bin/memory.cgi'>"; }
elsif ( $cgigraphs[1] eq "processes" ) { print "<a href='/cgi-bin/services.cgi'>"; }
elsif ( $cgigraphs[1] =~ /disk/ ) { print "<a href='/cgi-bin/media.cgi'>"; }
elsif ( $cgigraphs[1] =~ /red/ || $cgigraphs[1] =~ /ppp/ || $cgigraphs[1] =~ /ipsec/ ) { print "<a href='/cgi-bin/network.cgi?network=red'>"; }
elsif ( $cgigraphs[1] =~ /green/ || $cgigraphs[1] =~ /blue/ || $cgigraphs[1] =~ /orange/ ) { print "<a href='/cgi-bin/network.cgi?network=internal'>"; }
elsif ( $cgigraphs[1] eq "fwhits" || $cgigraphs[2] ne "" ) { print "<a href='/cgi-bin/network.cgi?network=other'>"; }
print "$Lang::tr{'back'}</a></td></tr></table></div>\n";

&Header::closebigbox();
&Header::closepage();
