#!/usr/bin/perl
#
# This file is part of the IPCop Firewall.
#
# IPCop is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# IPCop is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with IPCop; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# Copyright (C) 2003-02-04 Mark Wormgoor <mark@wormgoor.com>
#

# Usage:
#
# ./tools/cvs2sql.pl | grep -e INSERT -e UPDATE > lang_data.sql
#

# Get time
($sec, $min, $hour, $day, $month, $year, $weekday, $dayofyear, $isdst) = localtime(time);
$year += 1900;
if ($month < 10) { $month = "0" . $month; }
if ($day   < 10) { $day   = "0" . $day;   }
if ($hour  < 10) { $hour  = "0" . $hour;  }
if ($min   < 10) { $min   = "0" . $min;   }
if ($sec   < 10) { $sec   = "0" . $sec;   }
$lastchange = "$year$month$day$hour$sec";

# Read English install file
  undef $/;
  open (FILE, "langs/en/install/lang_en.c") or die "Couldn't open English language file";
  $file = <FILE>;
  close (FILE);
  $file =~ s/"\s*\\\s*\n"//g;
  $file =~ s/",/"/g;
  $file =~ s/\\n/\\\\n/g;
  $file =~ s/^.*(TR_[\w]+).*$/$1/gm;
  $file =~ s/(TR_\w+)\n(.*$)/INSERT INTO Lang_Data (VarName, EN_Word, Section, LastChange) Values ("$1", $2, "SETUP", "$lastchange");/gm;
  print "$file";

# Read English Perl file
  do "langs/en/cgi-bin/en.pl" or die "Failed to open English web language file";
  while( my ($key, $value) = each(%tr) ) {
	$key = lc($key);
	$value =~ s/\n//mg;
	$value =~ s/\\*\"/\\"/g;
	print "INSERT INTO Lang_Data (VarName, EN_Word, Section, LastChange) Values (\"$key\", \"$value\", \"WEB\", \"$lastchange\");\n";
  }

# Other language install files
  while (($trans = glob("langs/*/install/lang_*.c") ))  {
	if ( $trans =~ /lang_en.c/ ) { next; }
	if ( $trans =~ /lang_el.c/ ) { next; }
	open (FILE, "$trans") or die "Couldn't open language file: $trans";
	$file = <FILE>;
	close (FILE);
	$trans =~ s/.*lang_(.*).c/$1/;
	$trans = uc($trans);
	$file =~ s/"\s*\\\s*\n"//g;
	$file =~ s/",/"/g;
	$file =~ s/\\n/\\\\n/g;
	$file =~ s/^.*(TR_[\w]+).*$/$1/gm;
	$file =~ s/(TR_\w+)\n(.*$)/UPDATE Lang_Data set ${trans}_Word = $2 where VarName = "$1";/gm;
	print "$file";
  }

# Other language perl files
  while (($trans = glob("langs/*/cgi-bin/*.pl") ))  {
	if ( $trans =~ /en.pl/ ) { next; }
	if ( $trans =~ /el.pl/ ) { next; }
	%tr=();
	do "$trans" or die "Failed to load translation file: $trans";
	$trans =~ s/.*\/(\w+).pl/$1/;
	$trans = uc($trans);
	while( my ($key, $value) = each(%tr) ) {
		$key = lc($key);
		$value =~ s/\n//mg;
		$value =~ s/\\*\"/\\"/g;
		print "UPDATE Lang_Data set ${trans}_Word = \"$value\" where VarName = \"$key\";\n";
	}
  }
