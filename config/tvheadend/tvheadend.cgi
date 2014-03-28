#!/usr/bin/perl -w

use strict;
use CGI;

my $cgi = new CGI;

print $cgi->redirect('http://'.$ENV{'SERVER_NAME'}.':9981/extjs.html');