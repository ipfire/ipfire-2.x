#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2016-2024  IPFire Team  <info@ipfire.org>                     #
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
use CGI;
use File::Copy;
use File::LibMagic;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';

my $q = new CGI;
my $magic = File::LibMagic->new;

my $logo = "${General::swroot}/captive/logo.dat";
my $file_info = $magic->info_from_filename($logo);

# Send 404 if logo was not uploaded and exit
if (!-e $logo) {
	print CGI::header(status => 404);
	exit(0);
}

# Send image data
print $q->header(-type=>$file_info->{mime_type});
binmode STDOUT;
File::Copy::copy $logo, \*STDOUT;
exit(0);
