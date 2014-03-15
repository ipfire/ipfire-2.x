#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2005-2010  IPFire Team                                        #
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

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "${General::swroot}/graphs.pl";

my @querry = split(/\?/,$ENV{'QUERY_STRING'});
$querry[0] = '' unless defined $querry[0];
$querry[1] = 'hour' unless defined $querry[1];

if ( $querry[0] ne~ "") {
	print "Content-type: image/png\n\n";
	binmode(STDOUT);
	&Graphs::updateentropygraph($querry[1]);

} else {
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'entropy'}, 1, '');
	&Header::openbigbox('100%', 'left');

	&Header::openbox('100%', 'center', $Lang::tr{'entropy'});
	&Graphs::makegraphbox("entropy.cgi", "day", '', 350);
	&Header::closebox();

	# Check for hardware support.
	my $message;
	my $message_colour = $Header::colourred;
	if (&has_hwrng()) {
		$message = $Lang::tr{'system has hwrng'};
		$message_colour = $Header::colourgreen;
	} elsif (&has_rdrand()) {
		$message = $Lang::tr{'system has rdrand'};
		$message_colour = $Header::colourgreen;
	} else {
		$message = $Lang::tr{'no hardware random number generator'};
	}

	&Header::openbox('100%', 'center', $Lang::tr{'hardware support'});
	print <<EOF;
		<p style="color: $message_colour; text-align: center;">$message</p>
EOF
	&Header::closebox();

	&Header::closebigbox();
	&Header::closepage();
}

sub has_hwrng() {
	return (-c "/dev/hwrng");
}

sub has_rdrand() {
	open(FILE, "/proc/cpuinfo") or return 0;
	my @cpuinfo = <FILE>;
	close(FILE);

	my @result = grep(/rdrand/, @cpuinfo);
	if (@result) {
		return 1;
	}

	return 0;
}
