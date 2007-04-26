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
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

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

if ($cgigraphs[1] =~ /(network|GREEN|BLUE|ORANGE|RED|lq)/) {
	&Header::openpage($Lang::tr{'network traffic graphs'}, 1, '');
} else {
	&Header::openpage($Lang::tr{'system graphs'}, 1, '');
}

&Header::openbigbox('100%', 'left');

if ($cgigraphs[1] =~ /(GREEN|BLUE|ORANGE|RED|lq|cpu|memory|swap|disk|load)/) {
	my $graph = $cgigraphs[1];
	my $graphname = ucfirst(lc($cgigraphs[1]));
	&Header::openbox('100%', 'center', "$graphname $Lang::tr{'graph'}");

	if (-e "$graphdir/${graph}-day.png") {
		my $ftime = localtime((stat("$graphdir/${graph}-day.png"))[9]);
		print "<center>";
		print "<b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br /><hr />\n";
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
	push (@graphs, ('lq'));

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

&Header::closebigbox();
&Header::closepage();
