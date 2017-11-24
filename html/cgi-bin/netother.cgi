#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2008  Michael Tremer & Christian Schmidt                      #
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

my @pings=();

my @querry = split(/\?/,$ENV{'QUERY_STRING'});
$querry[0] = '' unless defined $querry[0];
$querry[1] = 'hour' unless defined $querry[1];

if ( $querry[0] =~ "fwhits"){
	print "Content-type: image/png\n\n";
	binmode(STDOUT);
	&Graphs::updatefwhitsgraph($querry[1]);
}elsif ( $querry[0] ne ""){
	print "Content-type: image/png\n\n";
	binmode(STDOUT);
	&Graphs::updatepinggraph($querry[0],$querry[1]);
}else{

	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'network traffic graphs others'}, 1, '');
	&Header::openbigbox('100%', 'left');
	
	my @pinggraphs = `ls -dA /var/log/rrd/collectd/localhost/ping/ping-*`;
	foreach (@pinggraphs){
		$_ =~ /(.*)\/ping\/ping-(.*)\.rrd/;
		push(@pings,$2);
	}

	foreach (@pings) {
		&Header::openbox('100%', 'center', "$_ $Lang::tr{'graph'}");
		&Graphs::makegraphbox("netother.cgi",$_,"day");
		&Header::closebox();
	}

	&Header::openbox('100%', 'center', "$Lang::tr{'firewallhits'} $Lang::tr{'graph'}");
	&Graphs::makegraphbox("netother.cgi","fwhits","day");
	&Header::closebox();

	my $output = '';
	
	&Header::openbox('100%', 'left', $Lang::tr{'routing table entries'});
	$output = `/sbin/ip route show`;
	$output = &Header::cleanhtml($output,"y");
	print "<pre>$output</pre>\n";
	&Header::closebox();

	&Header::openbox('100%', 'left', $Lang::tr{'arp table entries'});
	$output = `/sbin/ip neigh show`;
	$output = &Header::cleanhtml($output,"y");
	print "<pre>$output</pre>\n";
	&Header::closebox();

	&Header::closebigbox();
	&Header::closepage();
}	
