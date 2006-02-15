#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# $Id: dial.cgi,v 1.4.2.3 2005/02/22 22:21:55 gespinasse Exp $
#

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require 'CONFIG_ROOT/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %cgiparams=();

$cgiparams{'ACTION'} = '';
&Header::getcgihash(\%cgiparams);

if ($cgiparams{'ACTION'} eq $Lang::tr{'dial'}) {
	system('/etc/rc.d/rc.red','start') == 0
	or &General::log("Dial failed: $?"); }
elsif ($cgiparams{'ACTION'} eq $Lang::tr{'hangup'}) {
	system('/etc/rc.d/rc.red','stop') == 0
	or &General::log("Hangup failed: $?"); }
sleep 1;

print "Status: 302 Moved\nLocation: /cgi-bin/index.cgi\n\n";
