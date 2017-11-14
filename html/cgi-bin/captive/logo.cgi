#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2016  Alexander Marx alexander.marx@ipfire.org                #
#                                                                             #
# This program is free software you can redistribute it and/or modify         #
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
use CGI;
use File::Copy;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';

my $logo = "${General::swroot}/captive/logo.dat";

# Send 404 if logo was not uploaded and exit
if (!-e $logo) {
	print CGI::header(status => 404);
	exit(0);
}

print "Content-Type: application/octet-stream\n\n";

# Send image data
File::Copy::copy $logo, \*STDOUT;
exit(0);
