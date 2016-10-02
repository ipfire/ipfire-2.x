#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2014  IPFire Team  <info@ipfire.org>                     #
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

my %cgiparams;
my %pppsettings;
my %netsettings;

&General::readhash("${General::swroot}/ppp/settings", \%pppsettings);
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);


&Header::getcgihash(\%cgiparams);

&Header::showhttpheaders();
&Header::openpage($Lang::tr{'sstraffic'}, 1, '');
&Header::openbigbox('100%', 'left');

&Header::openbox('100%', 'center', "$Lang::tr{'traffics'}");

# Display internal network
display_vnstat($netsettings{'GREEN_DEV'});

# Display external network / check if it is PPP or ETH
# and dont display if RED_DEV=GREEN_DEV (green only mode)
if ($netsettings{'RED_TYPE'} ne 'PPPOE') {
    if ($netsettings{'RED_DEV'} ne $netsettings{'GREEN_DEV'}) {
	display_vnstat($netsettings{'RED_DEV'});
    }
} else {
    display_vnstat("ppp0");
}

# Check config and display aditional Networks (BLUE and ORANGE)
# if they exist
if ($netsettings{'CONFIG_TYPE'} =~ /^(3|4)$/) {
    display_vnstat($netsettings{'BLUE_DEV'});
}

if ($netsettings{'CONFIG_TYPE'} =~ /^(2|4)$/) {
    display_vnstat($netsettings{'ORANGE_DEV'});
}

&Header::closebox();
&Header::closebigbox();
&Header::closepage();

sub display_vnstat
{
	my $device = $_[0];

	my $testdata = `/usr/bin/vnstat -i $device`;

	if ( $testdata =~ 'enough') {
		print"No data for $device !<br>";
	} else {
	    system("/usr/bin/vnstati -c 5 -s -i $device -o /srv/web/ipfire/html/graphs/vnstat-s-$device.png");
	    # Hour graph
	    system("/usr/bin/vnstati -c 5 -h -i $device -o /srv/web/ipfire/html/graphs/vnstat-h-$device.png");
	    # Day graph
	    system("/usr/bin/vnstati -c 5 -d -i $device -o /srv/web/ipfire/html/graphs/vnstat-d-$device.png");
	    # Month graph
	    system("/usr/bin/vnstati -c 5 -m -i $device -o /srv/web/ipfire/html/graphs/vnstat-m-$device.png");
	    # Top10 graph
	    system("/usr/bin/vnstati -c 5 -t -i $device -o /srv/web/ipfire/html/graphs/vnstat-t-$device.png");

# Generate HTML-Table with the graphs
print <<END
<table>
<tr><td><img src="/graphs/vnstat-s-$device.png"></td></tr>
<tr><td><img src="/graphs/vnstat-h-$device.png"></td></tr>
<tr><td><img src="/graphs/vnstat-d-$device.png"></td></tr>
<tr><td><img src="/graphs/vnstat-m-$device.png"></td></tr>
<tr><td><img src="/graphs/vnstat-t-$device.png"></td></tr>
</table>
END
;
	    }
	print"<hr>";
}
