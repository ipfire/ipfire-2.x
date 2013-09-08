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
my %netsettings=();
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

my @graphs=();
my @wireless=();

my @querry = split(/\?/,$ENV{'QUERY_STRING'});
$querry[0] = '' unless defined $querry[0];
$querry[1] = 'hour' unless defined $querry[1];
$querry[2] = '' unless defined $querry[2];

if ( $querry[0] =~ /wireless/ ){
	print "Content-type: image/png\n\n";
	binmode(STDOUT);
	$querry[0] =~ s/wireless//g;
	&Graphs::updatewirelessgraph($querry[0],$querry[1]);
}elsif ( $querry[0] ne "" ){
	print "Content-type: image/png\n\n";
	binmode(STDOUT);
	&Graphs::updateifgraph($querry[0],$querry[1]);
}else{

	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'network traffic graphs internal'}, 1, '');
	&Header::openbigbox('100%', 'left');

	push (@graphs, ($netsettings{'GREEN_DEV'}));
	if (&Header::blue_used() && $netsettings{'BLUE_DEV'}) {push (@graphs, ($netsettings{'BLUE_DEV'})); }
	if (&Header::orange_used() && $netsettings{'ORANGE_DEV'}) {push (@graphs, ($netsettings{'ORANGE_DEV'})); }

	my @wirelessgraphs = `ls -dA /var/log/rrd/collectd/localhost/wireless* 2>/dev/null`;
	foreach (@wirelessgraphs){
		$_ =~ /(.*)\/wireless-(.*)/;
		push(@wireless,$2);
	}

	foreach (@graphs) {
		&Header::openbox('100%', 'center', "$_ $Lang::tr{'graph'}");
		&Graphs::makegraphbox("netinternal.cgi",$_,"day");
		&Header::closebox();
	}

	foreach (@wireless) {
		&Header::openbox('100%', 'center', "Wireless $_ $Lang::tr{'graph'}");
		&Graphs::makegraphbox("netinternal.cgi","wireless".$_,"day");
		&Header::closebox();
	}

	&Header::closebigbox();
	&Header::closepage();
}	
