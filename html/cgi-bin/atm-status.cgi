#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2008  Michael Tremer & Christian Schmidt                      #
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

my %color = ();
my %mainsettings = ();

&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

&Header::showhttpheaders();
&Header::openpage($Lang::tr{'status information'}, 1, '');
&Header::openbigbox('100%', 'left');

my @modems = `find /sys/class/atm/*/device 2>/dev/null | cut -d'/' -f5`;
foreach (@modems){
	chomp($_);
	&Header::openbox('100%', 'left',"ATM MODEM $_ State");
	my $lines=0;
	print "<center><table>";
	my $modem=$_;
	my @pfile = `grep . /sys/class/atm/$modem/parameters/* 2>/dev/null`;
	foreach (@pfile){
		chomp($_);
		my $param= `echo $_ | cut -d'/' -f7 | cut -d':' -f1`;
		my $value= `cat /sys/class/atm/$modem/parameters/$param`;
		chomp($param);
		chomp($value);
		if (!($param =~"uevent") 
		  && !($param =~"resource")
		  && !($param eq "")
 		) {
				
			$lines++;
			if ($lines % 2){
		    		print "<tr bgcolor='$color{'color22'}'>";
			}else{
				print "<tr bgcolor='$color{'color20'}'>";
			}
			print "<td align='left'>$param</td><td align='left'>$value</td> ";		
		}
	}
	my @pfile = `grep . /sys/class/atm/$modem/device/* 2>/dev/null`;
	foreach (@pfile){
		chomp($_);
		my $param= `echo $_ | cut -d'/' -f7 | cut -d':' -f1`;
		my $value= `cat /sys/class/atm/$modem/device/$param`;
		chomp($param);
		chomp($value);
		if (!($param =~"uevent") 
		  && !($param =~"modalias") 
		  && !($param =~"bInterface")
		  && !($param =~"bAlternateSetting")
		  && !($param =~"bNumEndpoints")
		  && !($param =~"config matches")
		  && !($param =~"resource")
		  && !($param eq "")
 		) {
				
			$lines++;
			if ($lines % 2){
		    		print "<tr bgcolor='$color{'color22'}'>";
			}else{
				print "<tr bgcolor='$color{'color20'}'>";
			}
			print "<td align='left'>$param</td><td align='left'>$value</td> ";		
		}
	}
	print "</table><br>\n";
	&Header::closebox();
}
&Header::closebigbox();
&Header::closepage();
