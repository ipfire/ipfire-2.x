#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# $Id: graphs.cgi,v 1.9.2.6 2005/02/22 22:21:55 gespinasse Exp $
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

my $graphdir = "/home/httpd/html/graphs";
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

$ENV{'QUERY_STRING'} =~ s/&//g;
@cgigraphs = split(/graph=/,$ENV{'QUERY_STRING'});
$cgigraphs[1] = '' unless defined $cgigraphs[1];

if ($cgigraphs[1] =~ /(network|GREEN|BLUE|ORANGE|RED|lq)/) {
	&Header::openpage($Lang::tr{'network traffic graphs'}, 1, '');
} else {
	&Header::openpage($Lang::tr{'system graphs'}, 1, '');
}

sub diskbox {
 my $disk = $_[0];
    if (-e "$graphdir/disk-$disk-day.png") {
  
 	  &Header::openbox('100%', 'center', "Disk /dev/$disk $Lang::tr{'graph'}");
	  my $ftime = localtime((stat("$graphdir/disk-$disk-day.png"))[9]);
	  print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
	  print "<a href='/cgi-bin/graphs.cgi?graph=disk-$disk'>";
	  print "<img src='/graphs/disk-$disk-day.png' border='0' />";
	  print "</a>";
	  print "<br />\n";
	  if (-e "/usr/local/bin/hddshutdown-state") {
	    system("/usr/local/bin/hddshutdown-state $disk");
	  }	
        &Header::closebox();
  }
}

&Header::openbigbox('100%', 'left');

if ($cgigraphs[1] =~ /(GREEN|BLUE|ORANGE|RED|lq|cpu|memory|swap|disk)/) {
	my $graph = $cgigraphs[1];
	my $graphname = ucfirst(lc($cgigraphs[1]));
	&Header::openbox('100%', 'center', "$graphname $Lang::tr{'graph'}");

	if (-e "$graphdir/${graph}-day.png") {
		my $ftime = localtime((stat("$graphdir/${graph}-day.png"))[9]);
		print "<center>";
		print "<b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br /><hr />\n";
		print "<img src='/graphs/${graph}-day.png' border='0' /><hr />";
		print "<img src='/graphs/${graph}-week.png' border='0' /><hr />";
		print "<img src='/graphs/${graph}-month.png' border='0' /><hr />";
		print "<img src='/graphs/${graph}-year.png' border='0' />";
	} else {
		print $Lang::tr{'no information available'};
	}
	&Header::closebox();
	print "<div align='center'><table width='80%'><tr><td align='center'>";
	if ($cgigraphs[1] =~ /(GREEN|BLUE|ORANGE|RED|lq)/) {
		print "<a href='/cgi-bin/graphs.cgi?graph=network'>";
	} else {
		print "<a href='/cgi-bin/graphs.cgi'>";
	}
	print "$Lang::tr{'back'}</a></td></tr></table></div>\n";
	;
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
			print "<img src='/graphs/${graphname}-day.png' border='0' />";
			print "</a>";
		} else {
			print $Lang::tr{'no information available'};
		}
		print "<br />\n";
		&Header::closebox();
	}
} else {
	&Header::openbox('100%', 'center', "CPU $Lang::tr{'graph'}");
	if (-e "$graphdir/cpu-day.png") {
		my $ftime = localtime((stat("$graphdir/cpu-day.png"))[9]);
		print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
		print "<a href='/cgi-bin/graphs.cgi?graph=cpu'>";
		print "<img src='/graphs/cpu-day.png' border='0' />";
		print "</a>";
	} else {
		print $Lang::tr{'no information available'};
	}
	print "<br />\n";
	&Header::closebox();

	&Header::openbox('100%', 'center', "Memory $Lang::tr{'graph'}");
	if (-e "$graphdir/memory-day.png") {
		my $ftime = localtime((stat("$graphdir/memory-day.png"))[9]);
		print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
		print "<a href='/cgi-bin/graphs.cgi?graph=memory'>";
		print "<img src='/graphs/memory-day.png' border='0' />";
		print "</a>";
	} else {
		print $Lang::tr{'no information available'};
	}
	print "<br />\n";
	&Header::closebox();

	&Header::openbox('100%', 'center', "Swap $Lang::tr{'graph'}");
	if (-e "$graphdir/swap-day.png") {
		my $ftime = localtime((stat("$graphdir/swap-day.png"))[9]);
		print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
		print "<a href='/cgi-bin/graphs.cgi?graph=swap'>";
		print "<img src='/graphs/swap-day.png' border='0' />";
		print "</a>";
	} else {
		print $Lang::tr{'no information available'};
	}
	print "<br />\n";
	&Header::closebox();

	&Header::openbox('100%', 'center', "Disk $Lang::tr{'graph'}");
	if (-e "$graphdir/disk-day.png") {
		my $ftime = localtime((stat("$graphdir/disk-day.png"))[9]);
		print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
		print "<a href='/cgi-bin/graphs.cgi?graph=disk'>";
		print "<img src='/graphs/disk-day.png' border='0' />";
		print "</a>";
	} else {
		print $Lang::tr{'no information available'};
	}
	print "<br />\n";
	&Header::closebox();

    diskbox("hda");
    diskbox("hdb");
    diskbox("hdc");
    diskbox("hdd");
    diskbox("hde");
    diskbox("hdf");
    diskbox("hdg");
    diskbox("hdh");
}

&Header::closebigbox();
&Header::closepage();
