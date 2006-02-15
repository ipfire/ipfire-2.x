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
# Copyright (C) 2003-03-09 Mark Wormgoor <mark@wormgoor.com>
#

open(LIST, "./langs/list") or die 'Unable to open language list ./langs/list';

while (<LIST>) {
	next if $_ =~ m/^#/;
	@temp = split(/:/,$_);
	$lang = $temp[0];
	$uclang = uc($lang);
	print "Downloading files for " . $temp[1] . "\n";
	system ('wget','--quiet','-N','-c','--cache=off',"http://www.ipcop.org/langs/create-c.php?Lang=${uclang}");
	rename ("create-c.php?Lang=${uclang}", "langs/${lang}/install/lang_${lang}.c") or die
		'Failed to rename downloaded file: langs/${lang}/install/lang_${lang}.c';
	system ('wget','--quiet','-N','-c','--cache=off',"http://www.ipcop.org/langs/create-pl.php?Lang=${uclang}");
	rename ("create-pl.php?Lang=${uclang}", "langs/${lang}/cgi-bin/${lang}.pl") or die
		'Failed to rename downloaded file: langs/${lang}/cgi-bin/${lang}.pl';
}
close (LIST)
