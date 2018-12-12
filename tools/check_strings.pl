#!/usr/bin/perl
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

my (%tr2, $basedir);

use Cwd;
use File::Find;

my  $lang = "$ARGV[0]";
if ( $lang eq "") {
	print "ERROR: Please give me a language!\n";
	exit;
}

$basedir = cwd();

# Load English strings
require "${basedir}/langs/en/cgi-bin/en.pl";

# Copy hash and empty %tr
my %tr_en = %tr;
%tr = ();

# Load requested language
require "${basedir}/langs/$lang/cgi-bin/$lang.pl";

sub wanted {
	if ( -f $File::Find::name && open(FILE, $File::Find::name)) {
		while (<FILE>) {
			while ($_ =~ /\$Lang::tr\{'([A-Za-z0-9,:_\s\/\.-]+)'\}/g) {
				$tr2{$1} = $tr_en{$1} || "unknown string";
			}
		}
		close(FILE);
	}
}

## Main
find (\&wanted, "$basedir/html"  );
find (\&wanted, "$basedir/src/scripts"  );
find (\&wanted, "$basedir/config/cfgroot"  );
find (\&wanted, "$basedir/config/menu"  );

for my $key ( sort (keys %tr) ) {
	my $value = $tr{$key};
	if (! $tr2{$key}) {
		print "WARNING: translation string unused: $key\n";
	}
}

for my $key ( sort(keys %tr2) ) {
	my $value = $tr2{$key};
	if (! $tr{$key}) {
		print "WARNING: untranslated string: $key = $value\n";
	}
}
