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
require "${General::swroot}/graphs.pl";

my %cgiparams=();
my %pppsettings=();
my %netsettings=();
my @cgiparams=();
my @graphs=();
my $iface='';
my %dhcpsettings=();
my %dhcpinfo=();
my $output='';

&Header::showhttpheaders();

&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

$ENV{'QUERY_STRING'} =~ s/&//g;
@cgiparams = split(/network=/,$ENV{'QUERY_STRING'});
$cgiparams[1] = '' unless defined $cgiparams[1];

if ($cgiparams[1] =~ /red/) {
	&Header::openpage($Lang::tr{'network traffic graphs external'}, 1, '');
	push (@graphs, ($netsettings{'RED_DEV'}));
	if (-e "/var/log/rrd/collectd/localhost/interface/if_octets-ipsec0.rrd") {push (@graphs, ("ipsec0"));
}elsif ($cgiparams[1] =~ /other/) {
	&Header::openpage($Lang::tr{'network traffic graphs others'}, 1, '');
	push (@graphs, ("lq"));
	push (@graphs, ("fwhits"));
}else {
	&Header::openpage($Lang::tr{'network traffic graphs internal'}, 1, '');
	push (@graphs, ($netsettings{'GREEN_DEV'}));
	if ($netsettings{'BLUE_DEV'}) {
		push (@graphs, ($netsettings{'BLUE_DEV'})); }
	if ($netsettings{'ORANGE_DEV'}) {
		push (@graphs, ($netsettings{'ORANGE_DEV'})); }
}

&Header::openbigbox('100%', 'left');

foreach my $graphname (@graphs) {

  if ($graphname eq "lq" )
  {  &Graphs::updatelqgraph("day");  }
  elsif ($graphname eq "fwhits" )
  {  &Graphs::updatefwhitsgraph("day");  }
  else
  {  &Graphs::updateifgraph($graphname, "day");  }
  
	&Header::openbox('100%', 'center', "$graphname $Lang::tr{'graph'}");
	if (-e "$Header::graphdir/${graphname}-day.png") {
		my $ftime = localtime((stat("$Header::graphdir/${graphname}-day.png"))[9]);
		print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
		print "<a href='/cgi-bin/graphs.cgi?graph=$graphname'>";
		print "<img alt='' src='/graphs/${graphname}-day.png' border='0' />";
		print "</a>";
	} else {
		print $Lang::tr{'no information available'};
	}
	print "<br />\n";
	&Header::closebox();
}

if ($cgiparams[1] =~ /red/) {
	
	if ( $netsettings{'CONFIG_TYPE'} =~ /^(1|2|3|4)$/  && $netsettings{'RED_TYPE'} eq "DHCP") {

		&Header::openbox('100%', 'left', "RED $Lang::tr{'dhcp configuration'}");
		if (-s "${General::swroot}/dhcpc/dhcpcd-$netsettings{'RED_DEV'}.info") {

			&General::readhash("${General::swroot}/dhcpc/dhcpcd-$netsettings{'RED_DEV'}.info", \%dhcpinfo);

			my $DNS1=`echo $dhcpinfo{'DNS'} | cut -f 1 -d ,`;
			my $DNS2=`echo $dhcpinfo{'DNS'} | cut -f 2 -d ,`;

			my $lsetme=0;
			my $leasetime="";
			if ($dhcpinfo{'LEASETIME'} ne "") {
				$lsetme=$dhcpinfo{'LEASETIME'};
				$lsetme=($lsetme/60);
				if ($lsetme > 59) {
					$lsetme=($lsetme/60); $leasetime=$lsetme." Hour";
				} else {
				$leasetime=$lsetme." Minute";
				}
				if ($lsetme > 1) {
					$leasetime=$leasetime."s";
				}
			}
			my $rentme=0;
			my $rnwltime="";
			if ($dhcpinfo{'RENEWALTIME'} ne "") {
				$rentme=$dhcpinfo{'RENEWALTIME'};
				$rentme=($rentme/60);
				if ($rentme > 59){
					$rentme=($rentme/60); $rnwltime=$rentme." Hour";
				} else {
					$rnwltime=$rentme." Minute";
				}
				if ($rentme > 1){
					$rnwltime=$rnwltime."s";
				}
			}
			my $maxtme=0;
			my $maxtime="";
			if ($dhcpinfo{'REBINDTIME'} ne "") {
				$maxtme=$dhcpinfo{'REBINDTIME'};
				$maxtme=($maxtme/60);
				if ($maxtme > 59){
					$maxtme=($maxtme/60); $maxtime=$maxtme." Hour";
				} else {
					$maxtime=$maxtme." Minute";
				}
				if ($maxtme > 1) {
					$maxtime=$maxtime."s";
				}
			}

			print "<table width='100%'>";
			if ($dhcpinfo{'HOSTNAME'}) {
				print "<tr><td width='30%'>$Lang::tr{'hostname'}</td><td>$dhcpinfo{'HOSTNAME'}.$dhcpinfo{'DOMAIN'}</td></tr>\n";
			} else {
				print "<tr><td width='30%'>$Lang::tr{'domain'}</td><td>$dhcpinfo{'DOMAIN'}</td></tr>\n";
			}
			print <<END
		<tr><td>$Lang::tr{'gateway'}</td><td>$dhcpinfo{'GATEWAY'}</td></tr>
		<tr><td>$Lang::tr{'primary dns'}</td><td>$DNS1</td></tr>
		<tr><td>$Lang::tr{'secondary dns'}</td><td>$DNS2</td></tr>
		<tr><td>$Lang::tr{'dhcp server'}</td><td>$dhcpinfo{'DHCPSIADDR'}</td></tr>
		<tr><td>$Lang::tr{'def lease time'}</td><td>$leasetime</td></tr>
		<tr><td>$Lang::tr{'default renewal time'}</td><td>$rnwltime</td></tr>
		<tr><td>$Lang::tr{'max renewal time'}</td><td>$maxtime</td></tr>
	    </table>
END
	    ;
		}
		else
		{
			print "$Lang::tr{'no dhcp lease'}";
		}
		&Header::closebox();
	}

	if ($dhcpsettings{'ENABLE_GREEN'} eq 'on' || $dhcpsettings{'ENABLE_BLUE'} eq 'on') {
		&Header::CheckSortOrder;
		&Header::PrintActualLeases;
	}
	
} else {

	&Header::openbox('100%', 'left', $Lang::tr{'routing table entries'});
	$output = `/sbin/ip route show`;
	$output = &Header::cleanhtml($output,"y");
	print "<pre>$output</pre>\n";
	&Header::closebox();
	
	&Header::openbox('100%', 'left', $Lang::tr{'arp table entries'});
	$output = `/sbin/ip neigh show`;
	$output = &Header::cleanhtml($output,"y");
	print "<pre>$output</pre>\n";
	&Header::closebox();
	
}

&Header::closebigbox();
&Header::closepage();
