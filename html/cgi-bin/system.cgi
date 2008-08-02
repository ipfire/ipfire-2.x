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

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

my %cgiparams=();

# Generate Graphs from rrd Data
&Graphs::updatecpugraph ("day");
&Graphs::updatecpufreqgraph ("day");
&Graphs::updateloadgraph ("day");

&Header::showhttpheaders();
&Header::getcgihash(\%cgiparams);
&Header::openpage($Lang::tr{'status information'}, 1, '');
&Header::openbigbox('100%', 'left');

&Header::openbox('100%', 'center', "CPU $Lang::tr{'graph'}");
if (-e "$Header::graphdir/cpu-day.png") {
	my $ftime = localtime((stat("$Header::graphdir/cpu-day.png"))[9]);
	print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
	print "<a href='/cgi-bin/graphs.cgi?graph=cpu'>";
	print "<img alt='' src='/graphs/cpu-day.png' border='0' />";
	print "</a>";
} else {
	print $Lang::tr{'no information available'};
}
print "<br />\n";
&Header::closebox();

if (-e "$Header::graphdir/cpufreq-day.png") {
    &Header::openbox('100%', 'center', "CPU Frequency $Lang::tr{'graph'}");
	my $ftime = localtime((stat("$Header::graphdir/cpufreq-day.png"))[9]);
	print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
	print "<a href='/cgi-bin/graphs.cgi?graph=cpufreq'>";
	print "<img alt='' src='/graphs/cpufreq-day.png' border='0' />";
	print "</a>";
	print "<br />\n";
    &Header::closebox();
}

&Header::openbox('100%', 'center', "Load $Lang::tr{'graph'}");
if (-e "$Header::graphdir/load-day.png") {
	my $ftime = localtime((stat("$Header::graphdir/load-day.png"))[9]);
	print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
	print "<a href='/cgi-bin/graphs.cgi?graph=load'>";
	print "<img alt='' src='/graphs/load-day.png' border='0' />";
	print "</a>";
} else {
	print $Lang::tr{'no information available'};
}
print "<br />\n";
&Header::closebox();
&Header::closebigbox();
&Header::closepage();
