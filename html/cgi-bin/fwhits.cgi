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
my @cgigraphs=();
my @graphs=();

&Graphs::updatefwhitsgraph ("day");
&Graphs::updatefwhitsgraph ("week");
&Graphs::updatefwhitsgraph ("month");
&Graphs::updatefwhitsgraph ("year");

$ENV{'QUERY_STRING'} =~ s/&//g;
@cgigraphs = split(/graph=/,$ENV{'QUERY_STRING'});
$cgigraphs[1] = '' unless defined $cgigraphs[1];

&Header::showhttpheaders();

my $graphdir = "/home/httpd/html/graphs";
my @LOCALCHECK=();
my $errormessage="";

&Header::openpage($Lang::tr{'firewall graphs'}, 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

	        &Header::openbox('100%', 'center', $Lang::tr{"daily firewallhits"});
if (-e "$Header::graphdir/firewallhits-day-area.png") {
		my $ftime = localtime((stat("$Header::graphdir/firewallhits-day-area.png"))[9]);
		print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
		print "<img alt='' src='/graphs/firewallhits-day-area.png' border='0' />";
		print "<br />\n";
} else {
	print $Lang::tr{'no information available'};
}
print "<br />\n";
	        &Header::closebox();
	        
	        &Header::openbox('100%', 'center', $Lang::tr{"weekly firewallhits"});
if (-e "$Header::graphdir/firewallhits-week-area.png") {
		my $ftime = localtime((stat("$Header::graphdir/firewallhits-week-area.png"))[9]);
		print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
		print "<img alt='' src='/graphs/firewallhits-week-area.png' border='0' />";
		print "<br />\n";
} else {
	print $Lang::tr{'no information available'};
}
print "<br />\n";
	        &Header::closebox();

	        &Header::openbox('100%', 'center', $Lang::tr{"monthly firewallhits"});
if (-e "$Header::graphdir/firewallhits-month-area.png") {
		my $ftime = localtime((stat("$Header::graphdir/firewallhits-month-area.png"))[9]);
		print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
		print "<img alt='' src='/graphs/firewallhits-month-area.png' border='0' />";
		print "<br />\n";
} else {
	print $Lang::tr{'no information available'};
}
print "<br />\n";
	        &Header::closebox();

	        &Header::openbox('100%', 'center', $Lang::tr{"yearly firewallhits"});
if (-e "$Header::graphdir/firewallhits-year-area.png") {
		my $ftime = localtime((stat("$Header::graphdir/firewallhits-year-area.png"))[9]);
		print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
		print "<img alt='' src='/graphs/firewallhits-year-area.png' border='0' />";
		print "<br />\n";
} else {
	print $Lang::tr{'no information available'};
}
print "<br />\n";
	        &Header::closebox();

&Header::closebigbox();
&Header::closepage();
