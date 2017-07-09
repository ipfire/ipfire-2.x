#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2005-2010  IPFire Team                                        #
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

my @querry = split(/\?/,$ENV{'QUERY_STRING'});
$querry[0] = '' unless defined $querry[0];
$querry[1] = 'hour' unless defined $querry[1];

if ( $querry[0] =~ "cpufreq"){
	print "Content-type: image/png\n\n";
	binmode(STDOUT);
	&Graphs::updatecpufreqgraph($querry[1]);
}elsif ( $querry[0] =~ "cpu"){
	print "Content-type: image/png\n\n";
	binmode(STDOUT);
	&Graphs::updatecpugraph($querry[1]);
}elsif ( $querry[0] =~ "load"){
	print "Content-type: image/png\n\n";
	binmode(STDOUT);
	&Graphs::updateloadgraph($querry[1]);
}else{
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'status information'}, 1, '');
	&Header::openbigbox('100%', 'left');

	&Header::openbox('100%', 'center', "CPU $Lang::tr{'graph'}");
	&Graphs::makegraphbox("system.cgi","cpu","day");
	&Header::closebox();

	if ( -e "$mainsettings{'RRDLOG'}/collectd/localhost/cpufreq/cpufreq-0.rrd"){
		&Header::openbox('100%', 'center', "CPU $Lang::tr{'graph'}");
		&Graphs::makegraphbox("system.cgi","cpufreq","day");
		&Header::closebox();
	}

	&Header::openbox('100%', 'center', "Load $Lang::tr{'graph'}");
	&Graphs::makegraphbox("system.cgi","load","day");
	&Header::closebox();

	&Header::closebigbox();
	&Header::closepage();
}
