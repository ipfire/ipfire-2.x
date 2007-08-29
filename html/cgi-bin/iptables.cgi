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

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my @iplines;
my $lines = 0;
my @ipmanlines;
my $manlines = 0;
my @ipnatlines;
my $natlines = 0;

system('/usr/local/bin/getipstat');

&Header::showhttpheaders();
&Header::openpage($Lang::tr{'ipts'}, 1, '');
&Header::openbigbox('100%', 'LEFT');
&Header::openbox('100%', 'LEFT', $Lang::tr{'ipts'}.':');
print <<END

    <DIV align='left'>
    <PRE>
END
;
	open (FILE, '/srv/web/ipfire/html/iptables.txt');
	while (<FILE>)
       {
         	$iplines[$lines] = $_;
		$lines++;
       }
	close (FILE);
	foreach $_ (@iplines) {
		print "$_"; }

print <<END
    </PRE>
    </DIV>
    <BR> 

END
;
&Header::closebox();

## MANGLE
&Header::openbox('100%', 'LEFT', $Lang::tr{'iptmangles'}.':');
print <<END

    <DIV align='left'>
    <PRE>
END
;
	open (FILEMAN, '/srv/web/ipfire/html/iptablesmangle.txt');
	while (<FILEMAN>)
       {
         	$ipmanlines[$manlines] = $_;
		$manlines++;
       }
	close (FILEMAN);
	foreach $_ (@ipmanlines) {
		print "$_"; }

print <<END
    </PRE>
    </DIV>
    <BR> 

END
;
&Header::closebox();

## NAT
&Header::openbox('100%', 'LEFT', $Lang::tr{'iptnats'}.':');
print <<END

    <DIV align='left'>
    <PRE>
END
;
	open (FILENAT, '/srv/web/ipfire/html/iptablesnat.txt');
	while (<FILENAT>)
       {
         	$ipnatlines[$natlines] = $_;
		$natlines++;
       }
	close (FILENAT);
	foreach $_ (@ipnatlines) {
		print "$_"; }

print <<END
    </PRE>
    </DIV>
    <BR> 

END
;
&Header::closebox();
&Header::closebigbox();
&Header::closepage();

system(rm -f "/srv/web/ipfire/html/iptables.txt");
system(rm -f "/srv/web/ipfire/html/iptablesmangle.txt");
system(rm -f "/srv/web/ipfire/html/iptablesnat.txt");
