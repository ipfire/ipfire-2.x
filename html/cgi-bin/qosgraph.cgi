#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
#

use strict;

# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "${General::swroot}/graphs.pl";

my @cgigraph=();
my $errormessage = "";

&Header::showhttpheaders();

$ENV{'QUERY_STRING'} =~ s/&//g;
@cgigraph = split(/graph=/,$ENV{'QUERY_STRING'});
$cgigraph[1] = '' unless defined $cgigraph[1];

&Graphs::overviewgraph("day",$cgigraph[1]);
&Graphs::overviewgraph("week",$cgigraph[1]);
&Graphs::overviewgraph("month",$cgigraph[1]);
&Graphs::overviewgraph("year",$cgigraph[1]);

&Header::openpage('QoS', 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);
&Header::openbox('100%', 'left', $cgigraph[1]);

	if (-e "/srv/web/ipfire/html/graphs/qos-graph-$cgigraph[1]-day.png") {
		my $ftime = localtime((stat("/srv/web/ipfire/html/graphs/qos-graph-$cgigraph[1]-day.png"))[9]);
		print "<center>";
		print "<b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
		print "<img alt='' src='/graphs/qos-graph-$cgigraph[1]-day.png' border='0' /><hr />";
	} else {
		print $Lang::tr{'no information available'};
	}

	if (-e "/srv/web/ipfire/html/graphs/qos-graph-$cgigraph[1]-week.png") {
		my $ftime = localtime((stat("/srv/web/ipfire/html/graphs/qos-graph-$cgigraph[1]-week.png"))[9]);
		print "<center>";
		print "<b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
		print "<img alt='' src='/graphs/qos-graph-$cgigraph[1]-week.png' border='0' /><hr />";
	} else {
		print $Lang::tr{'no information available'};
	}

	if (-e "/srv/web/ipfire/html/graphs/qos-graph-$cgigraph[1]-month.png") {
		my $ftime = localtime((stat("/srv/web/ipfire/html/graphs/qos-graph-$cgigraph[1]-month.png.png"))[9]);
		print "<center>";
		print "<b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
		print "<img alt='' src='/graphs/qos-graph-$cgigraph[1]-month.png' border='0' /><hr />";
	} else {
		print $Lang::tr{'no information available'};
	}
	
	if (-e "/srv/web/ipfire/html/graphs/qos-graph-$cgigraph[1]-year.png") {
		my $ftime = localtime((stat("/srv/web/ipfire/html/graphs/qos-graph-$cgigraph[1]-year.png"))[9]);
		print "<center>";
		print "<b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
		print "<img alt='' src='/graphs/qos-graph-$cgigraph[1]-year.png' border='0' /><hr />";
	} else {
		print $Lang::tr{'no information available'};
	}
	
	print"<div align='center'><br/><a href='/cgi-bin/qos.cgi'>$Lang::tr{'back'}</a></div>";

&Header::closebox();
&Header::closebigbox();
&Header::closepage();
