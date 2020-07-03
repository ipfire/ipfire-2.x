#!/usr/bin/perl
#
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2017-2020 Stephan Feddersen <sfeddersen@ipfire.org>           #
# All Rights Reserved.                                                        #
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
#
# Version: 2020/05/26 11:01:23
#
# This wiographs.cgi is based on the code from the IPCop WIO Addon
# and is extremly adapted to work with IPFire.
#
# Autor: Stephan Feddersen
# Co-Autor: Alexander Marx
#

use strict;

# enable only the following on debugging purpose
#use warnings;
#no warnings 'once';
#use CGI::Carp 'fatalsToBrowser';

use CGI;
my $cgi = new CGI;
my $hostid  = $cgi->param("HOSTID");
my $hostname = $cgi->param("HOSTNAME");

require '/var/ipfire/general-functions.pl';
require '/var/ipfire/header.pl';
require '/var/ipfire/lang.pl';
require '/usr/lib/wio/wio-graphs.pl';

my @querry =  split(/\?/,$ENV{'QUERY_STRING'});

$querry[0] = '' unless defined $querry[0]; # hostid
$querry[1] = '' unless defined $querry[1]; # period
$querry[2] = '' unless defined $querry[2]; # hostname

if ($querry[0] =~ "$hostid") {
	print "Content-type: image/png\n\n";
	binmode(STDOUT);
	&WIOGraphs::wiograph($querry[0], $querry[2], $querry[1]);
}
else {
	&Header::showhttpheaders();
	&Header::openpage("$Lang::tr{'wio'}", 1, '');
	&Header::openbigbox('100%', 'left');
	&Header::openbox('100%', 'left', "$Lang::tr{'wio_graphs_stat'} $hostname");
	&WIOGraphs::wiographbox("wiographs.cgi","$hostid","day","$hostname");
	print"<table width='100%'><tr><td align='left'><a href='/cgi-bin/wio.cgi'><img src='/images/wio/back.png' alt='$Lang::tr{'wio_back'}' title='$Lang::tr{'wio_back'}' /></a></td></tr></table>";
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
}

1;
