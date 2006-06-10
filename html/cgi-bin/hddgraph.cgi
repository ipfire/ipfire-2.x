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
# 2006-02-23 modified by weizen_42 for hddgraphs
#
# 2006-02-xx weizen_42        several modifications
# 2006-03-31 weizen_42        link to homepage
# 2006-04-22 weizen_42        v0.1.1 install below proxygraphs in status menu
#

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my $version = 'v0.1.1';

my %cgiparams=();
my @cgigraphs=();
my @graphs=();

&Header::showhttpheaders();

my $graphdir = "/home/httpd/html/graphs";

$ENV{'QUERY_STRING'} =~ s/&//g;
@cgigraphs = split(/graph=/,$ENV{'QUERY_STRING'});
$cgigraphs[1] = '' unless defined $cgigraphs[1];

&Header::openpage($Lang::tr{'harddisk temperature graphs'}, 1, '');

&Header::openbigbox('100%', 'left');

  &Header::openbox('100%', 'center', $Lang::tr{'harddisk temperature'});

  if (-e "$graphdir/hddtemp-day.png") 
  {
    my $ftime = localtime((stat("$graphdir/hddtemp-day.png"))[9]);
    print "<center>";
    print "<b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br /><hr />\n";
    print "<img src='/graphs/hddtemp-day.png' border='0' /><hr />";
    print "<img src='/graphs/hddtemp-week.png' border='0' /><hr />";
    print "<img src='/graphs/hddtemp-month.png' border='0' /><hr />";
    print "<img src='/graphs/hddtemp-year.png' border='0' />";
  }
  else 
  {
    print $Lang::tr{'no information available'};
  }
  
  &Header::closebox();

&Header::closebigbox();
&Header::closepage();
