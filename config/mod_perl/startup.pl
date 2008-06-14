#!/usr/bin/perl -wT

use ModPerl::Registry;
use Archive::Zip qw(:ERROR_CODES :CONSTANTS);
use CGI;
use CGI::Carp 'fatalsToBrowser';
use CGI qw(param);
use CGI qw/:standard/;
use File::Copy;
use File::Temp qw/ tempfile tempdir /;
use IO::Socket;
use Locale::Country;
use LWP::UserAgent;
use Net::DNS;
use Net::IPv4Addr qw( :all );
use RRDs;
use strict;
use Time::Local;
use warnings;

print "alle Perl-Module wurden geladen.\n";

