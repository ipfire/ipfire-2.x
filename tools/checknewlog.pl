#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2017  IPFire Team  <info@ipfire.org>                     #
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


opendir(DIR, "./log") || die;
my @FILES = readdir(DIR);
closedir(DIR);

foreach(@FILES) {
#	print $_."\n";
	my $Found = 0;

	if ( $_ =~ /$\.log/ || $_ =~ /^\.+/  || $_=~ /-install/ || $_=~ /-tools/ || $_=~ /-config/ || $_=~ /-kmod-/|| $_=~ /u-boot-.*-1/|| $_=~ /coreutils/ || $_=~ /cmake/ || $_=~ /gdb/ || $_=~ /libsigc/ || $_ eq 'FILES' ){
		next;
	} elsif ( $_=~ /missing_rootfile/ ){
		print "Rootfile for $_ missing!\n";
	} else {
		open(DATEI, "<./log/$_") || die "File not found";
		my @Lines = <DATEI>;
		close(DATEI);

		foreach (@Lines){
			if ( $_ =~ /^\+/ ){$Found=1;}
		}

		if ($Found){
			print "Changes in $_ check rootfile!\n";
		}
	}
}
