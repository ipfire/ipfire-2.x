#!/usr/bin/perl -w
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007  Michael Tremer & Christian Schmidt                      #
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
