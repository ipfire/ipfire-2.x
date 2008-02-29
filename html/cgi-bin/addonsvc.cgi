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

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::colourred} );
undef (@dummy);

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

my %cgiparams=();

&Header::showhttpheaders();
&Header::getcgihash(\%cgiparams);
&Header::openpage($Lang::tr{'status information'}, 1, '');
&Header::openbigbox('100%', 'left');

&Header::openbox('100%', 'left', 'Addon - Services');

my $paramstr=$ENV{QUERY_STRING};
my @param=split(/!/, $paramstr);
if ($param[1] ne '') {
    my $temp = `/usr/local/bin/addonctrl @param[0] @param[1]`;
}

print <<END
<div align='center'>
<table width='90%' cellspacing='2' border='0'>
<tr bgcolor='$color{'color20'}'>
<td align='left'><b>Addon</b></td>
<td align='center' colspan=3><b>Bootconfiguration</b></td>
<td align='center' colspan=2><b>Manual</b></td>
<td align='left' width='50%'><b>Status</b></td>
</tr>
END
;

my $lines=0; # Used to count the outputlines to make different bgcolor

# Generate list of installed addon pak's
my @pak = `find /opt/pakfire/db/installed/meta-* | cut -d"-" -f2`;
foreach (@pak)
{
	chomp($_);
	
	# Check which of the paks are services
	my @svc = `find /etc/init.d/$_ | cut -d"/" -f4`;
	foreach (@svc)
	{
	    # blacklist some packages
	    #
	    # alsa has trouble with the volume saving and was not really stopped
	    #
	    chomp($_);
	    if ($_ ne "alsa")
	    {
		$lines++;
		if ($lines % 2) 
		{
		    print "<tr bgcolor='$color{'color22'}'>";
		}
		else
		{
		    print "<tr bgcolor='$color{'color20'}'>";
		}
		print "<td align='left'>$_</td> ";
		my $status = isautorun($_);
		print "$status ";
		print "<td align='center'><A HREF=addonsvc.cgi?$_!enable>enable</A></td> ";
		print "<td align='center'><A HREF=addonsvc.cgi?$_!disable>disable</A></td> ";
		print "<td align='center'><A HREF=addonsvc.cgi?$_!start>start</A></td> ";
		print "<td align='center'><A HREF=addonsvc.cgi?$_!stop>stop</A></td> ";
		my $status = `/usr/local/bin/addonctrl $_ status`;
 		$status =~ s/\\[[0-1]\;[0-9]+m//g;
		chomp($status);
		print "<td align='left'>$status</td> ";
		print "</tr>";
	    }
	}
}

print "</table></div>\n";

&Header::closebox();
&Header::closebigbox();
&Header::closepage();

sub isautorun
{
	my $cmd = $_[0];
	my $status = "<td align='center' bgcolor='${Header::colourblue}'><font color='white'><b>---</b></font></td>";
	my $init = `find /etc/rc.d/rc3.d/S??${cmd}`;
	chomp ($init);
	if ($init ne '') {
		$status = "<td align='center' bgcolor='${Header::colourgreen}'><font color='white'><b>Ein</b></font></td>";
	}
	$init = `find /etc/rc.d/rc3.d/off/S??${cmd}`;
	chomp ($init);
	if ($init ne '') {
		$status = "<td align='center' bgcolor='${Header::colourred}'><font color='white'><b>Aus</b></font></td>";
	}
	
return $status;
}

