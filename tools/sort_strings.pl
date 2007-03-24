#!/usr/bin/perl -w
############################################################################
#                                                                          #
# This file is part of the IPCop Firewall.                                 #
#                                                                          #
# IPCop is free software; you can redistribute it and/or modify            #
# it under the terms of the GNU General Public License as published by     #
# the Free Software Foundation; either version 2 of the License, or        #
# (at your option) any later version.                                      #
#                                                                          #
# IPCop is distributed in the hope that it will be useful,                 #
# but WITHOUT ANY WARRANTY; without even the implied warranty of           #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
# GNU General Public License for more details.                             #
#                                                                          #
# You should have received a copy of the GNU General Public License        #
# along with IPCop; if not, write to the Free Software                     #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA #
#                                                                          #
# Copyright (C) 2004-03-12 Mark Wormgoor <mark@wormgoor.com>               #
#                                                                          #
############################################################################

use Cwd;
my $basedir = cwd();

my  $lang = "$ARGV[0]";
if ( $lang eq "") {
	print "ERROR: Please give me a language!\n";
	exit;
}

require "${basedir}/langs/$lang/cgi-bin/$lang.pl";

open(FILE,">${basedir}/langs/$lang/cgi-bin/$lang.pl");

print FILE <<EOF;
\%tr = ( 
\%tr,

EOF

for my $key ( sort (keys %tr) ) {
	my $value = $tr{$key};
	$value =~ s/\'/\\\'/g;
	print FILE "\'$key\' => \'$value\',\n";
}

print FILE ");\n\n#EOF\n";
