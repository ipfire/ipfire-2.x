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
# Version: 2020/05/26 10:34:23
#
# This wio-graphs.pl is based on the code from the IPCop WIO Addon
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
&General::readhash('/srv/web/ipfire/html/themes/ipfire/include/colors.txt', \%color);

sub wiograph {
	my $hostid = $_[0];
	my $host   = $_[1];
	my $period = $_[2];

	my $title  = "$host ($Lang::tr{$period})\n";

	my @rrd = ();

	push @rrd, ("-");
	push @rrd, ("--title", "$title");
	push @rrd, ("--start", "-1$period", "-aPNG", "-i", "-z");
	push @rrd, ("--border", "0");
	push @rrd, ("--full-size-mode");
	push @rrd, ("--slope-mode");
	push @rrd, ("--pango-markup");
	push @rrd, ("--alt-y-grid", "-w 910", "-h 300");
	if ( $period eq 'day' ) { push @rrd, ("--x-grid", "MINUTE:30:HOUR:1:HOUR:2:0:%H:%M"); }
	push @rrd, ("--color", "SHADEA".$color{"color19"});
	push @rrd, ("--color", "SHADEB".$color{"color19"});
	push @rrd, ("--color", "BACK".$color{"color21"});
	push @rrd, "DEF:mode=/var/log/rrd/wio/$hostid.rrd:mode:AVERAGE";
	push @rrd, "CDEF:online=mode,UN,0,mode,IF,50,GT,100,0,IF";
	push @rrd, "CDEF:offline=mode,UN,100,mode,IF,50,LT,100,0,IF";
	push @rrd, "AREA:online".$color{"color12"}.":$Lang::tr{'wio up'}\\j";
	push @rrd, "AREA:offline".$color{"color13"}.":$Lang::tr{'wio down'}\\j";
	push @rrd, "-W www.ipfire.org";

	RRDs::graph (@rrd);

	my $error = RRDs::error;
	print "Error in RRD::graph for Who Is Online: $error\n" if $error;
}

sub wiographbox {
	print "<table width='100%' align='center' cellspacing='0' border='0'>";
	print "<tr><td align='center' bgcolor='".$color{"color20"}."'><a href='".$_[0]."?".$_[1]."?hour?".$_[3]."' target='".$_[1]."box'><b>".$Lang::tr{'hour'}."</b></a></td>";
	print "<td align='center' bgcolor='".$color{"color20"}."'><a href='".$_[0]."?".$_[1]."?day?".$_[3]."' target='".$_[1]."box'><b>".$Lang::tr{'day'}."</b></a></td>";
	print "<td align='center' bgcolor='".$color{"color20"}."'><a href='".$_[0]."?".$_[1]."?week?".$_[3]."' target='".$_[1]."box'><b>".$Lang::tr{'week'}."</b></a></td>";
	print "<td align='center' bgcolor='".$color{"color20"}."'><a href='".$_[0]."?".$_[1]."?month?".$_[3]."' target='".$_[1]."box'><b>".$Lang::tr{'month'}."</b></a></td>";
	print "<td align='center' bgcolor='".$color{"color20"}."'><a href='".$_[0]."?".$_[1]."?year?".$_[3]."' target='".$_[1]."box'><b>".$Lang::tr{'year'}."</b></a></td></tr>";
	print "<tr><td colspan='5' align='center'>&nbsp;</td></tr>";
	print "<tr><td colspan='5' align='center'><iframe height='300px' width='940px' src='".$_[0]."?".$_[1]."?".$_[2]."?".$_[3]."' scrolling='no' marginheight='0' frameborder='no' name='".$_[1]."box'></iframe></td></tr>";
	print "</table>";
}
