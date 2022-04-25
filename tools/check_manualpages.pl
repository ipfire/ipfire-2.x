#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2005-2021  IPFire Team                                        #
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

use strict;
#use warnings;

# Import make.sh environment
my $basedir = $ENV{'BASEDIR'};

# Load configuration file (Header::_read_manualpage_hash() isn't available yet)
my $configfile = "${basedir}/config/cfgroot/manualpages";
my %manualpages = ();

open(my $file, "<", $configfile) or die "ERROR: Can't read from file '$configfile'!\n";
while(my $line = <$file>) {
	chomp($line);
	next if(substr($line, 0, 1) eq '#'); # Skip comments
	next if(index($line, '=', 1) == -1); # Skip incomplete lines

	my($left, $value) = split(/=/, $line, 2);
	if($left =~ /^([[:alnum:]\/._-]+)$/) {
		my $key = $1;
		$manualpages{$key} = $value;
	}
}
close($file);

# Check configuration
if(! defined $manualpages{'BASE_URL'}) {
	die "ERROR: User manual base URL not configured!\n";
}
my $baseurl = $manualpages{'BASE_URL'};
delete $manualpages{'BASE_URL'};

if ($baseurl =~ /\/\s*$/) {
	die "ERROR: User manual base URL must not end with a slash!\n";
}

# Loop trough configured manual pages
foreach my $page (keys %manualpages) {
	# Build absolute path (inside cgi-bin) and URL
	my $cgifile = "${basedir}/html/cgi-bin/${page}";
	my $url = "${baseurl}/$manualpages{$page}";

	print "cgi-bin/${page} -> '$url'\n";

	# Check CGI file exists
	if(! -f $cgifile) {
		print "WARNING: Obsolete link, page '$cgifile' doesn't exist!\n";
	}

	# Check obvious invalid characters
	if($url =~ /[^[:graph:]]/) {
		die("ERROR: URL contains invalid characters!\n");
	}

	# Check HTTP 200 "OK" result, follow up to 1 redirect (e.g. HTTP -> HTTPS)
	my $status = `curl --silent --show-error --output /dev/null --location --max-redirs 1 --max-time 10 --write-out "%{http_code}" --url "${url}"`;
	if($status != 200) {
		die("ERROR: Received unexpected HTTP '$status'!\n");
	}

	print "SUCCESS: Received HTTP '$status'.\n";
}

# Clean exit
exit 0;
