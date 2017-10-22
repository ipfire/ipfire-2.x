#!/usr/bin/perl
#
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2017 Stephan Feddersen <addons@h-loit.de>                     #
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
# id: wio-graphs.pl, v1.3.1 2017/07/11 21:31:16 sfeddersen
#
# This wio-graphs.pl is based on the Code from the IPCop WIO Addon
# and is extremly adapted to work with IPFire.
#
# Autor: Stephan Feddersen
# Co-Autor: Alexander Marx
#

package WIOGraphs;

use strict;

# enable only the following on debugging purpose
#use warnings;

use RRDs;

require '/var/ipfire/general-functions.pl';
require '/var/ipfire/lang.pl';

my ( %mainsettings, %color ) = ();

&General::readhash('/var/ipfire/main/settings', \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

sub wio {
	my $hostid   = $_[0];
	my $hostname = $_[1];
	my $period   = $_[2];

	my @rrd = ();

	push @rrd, ("-");
	push @rrd, @{&header($period, "$hostname ($Lang::tr{$period})")};
	push @rrd, @{&body($hostid)};

	RRDs::graph (@rrd);

	my $error = RRDs::error;
	print "Error in RRD::graph for Who Is Online: $error\n" if $error;
}

sub body {
	my $hostid = shift;
	my $result = [];

	push @$result, "DEF:mode=/var/log/rrd/wio/$hostid.rrd:mode:AVERAGE";
	push @$result, "CDEF:online=mode,UN,0,mode,IF,50,GT,100,0,IF";
	push @$result, "CDEF:offline=mode,UN,100,mode,IF,50,LT,100,0,IF";
	push @$result, "AREA:online".$color{"color12"}.":$Lang::tr{'wio up'}\\j";
	push @$result, "AREA:offline".$color{"color13"}.":$Lang::tr{'wio down'}\\j";
	push @$result, "COMMENT:\r<span size='smaller'>$Lang::tr{'wio_last_update'}\\: ". lastupdate(scalar localtime()) ."</span>\\r";

	return $result;
}

sub lastupdate {
    my $text = shift;

    return undef if not defined $text;
    $text =~ s/\\/\\\\/g;
    $text =~ s/:/\\:/g;

    return $text;
}

sub header {
	my $period = shift;
	my $title  = shift;
	my $result = [];

	push @$result, ("--title", "$title");
	push @$result, ("--start", "-1$period", "-aPNG", "-i", "-z");
	push @$result, ("--border", "0");
	push @$result, ("--full-size-mode");
	push @$result, ("--slope-mode");
	push @$result, ("--pango-markup");
	push @$result, ("--alt-y-grid", "-w 910", "-h 300");
	if ( $period eq 'day' ) { push @$result, ("--x-grid", "MINUTE:30:HOUR:1:HOUR:2:0:%H:%M"); }
	push @$result, ("--color", "SHADEA".$color{"color19"});
	push @$result, ("--color", "SHADEB".$color{"color19"});
	push @$result, ("--color", "BACK".$color{"color21"});

	return $result;
}

sub wiographbox {
	print "<center>";
	print "<table width='100%' cellspacing='0'>";
	print "<tr>";
	print "<td align='center' bgcolor='".$color{"color20"}."'><a href='".$_[0]."?".$_[1]."?hour?".$_[3]."' target='".$_[1]."box'><b>".$Lang::tr{'hour'}."</b></a></td>";
	print "<td align='center' bgcolor='".$color{"color20"}."'><a href='".$_[0]."?".$_[1]."?day?".$_[3]."' target='".$_[1]."box'><b>".$Lang::tr{'day'}."</b></a></td>";
	print "<td align='center' bgcolor='".$color{"color20"}."'><a href='".$_[0]."?".$_[1]."?week?".$_[3]."' target='".$_[1]."box'><b>".$Lang::tr{'week'}."</b></a></td>";
	print "<td align='center' bgcolor='".$color{"color20"}."'><a href='".$_[0]."?".$_[1]."?month?".$_[3]."' target='".$_[1]."box'><b>".$Lang::tr{'month'}."</b></a></td>";
	print "<td align='center' bgcolor='".$color{"color20"}."'><a href='".$_[0]."?".$_[1]."?year?".$_[3]."' target='".$_[1]."box'><b>".$Lang::tr{'year'}."</b></a></td>";
	print "</tr>";
	print "</table>";
	print "<table width='100%' cellspacing='0'>";
	print "<tr><td align='center' colspan='8'>&nbsp;</td></tr>";
	print "<tr><td align='center' colspan='8'><iframe class='graph' src='".$_[0]."?".$_[1]."?".$_[2]."?".$_[3]."' scrolling='no' marginheight='0' frameborder='no' name='".$_[1]."box'></iframe></td></tr>";
	print "</table>";
	print "</center>";
}
