#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2005-2010  IPFire Team                                        #
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
use experimental 'smartmatch';

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

use IO::Socket;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "${General::swroot}/graphs.pl";

my %color = ();
my %mainsettings = ();
my %netsettings=();
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/ipfire/include/colors.txt", \%color);

my @graphs=();
my %dhcpinfo=();

	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'network traffic graphs external'}, 1, '');
	&Header::openbigbox('100%', 'left');

	if ($netsettings{'RED_TYPE'} ne 'PPPOE'){
		if ($netsettings{'RED_DEV'} ne $netsettings{'GREEN_DEV'}){
			push (@graphs, ($netsettings{'RED_DEV'}));
		}
	}else{
		push (@graphs, "ppp0");
	}
	
	if (-e "/var/log/rrd/collectd/localhost/interface/if_octets-ipsec0.rrd"){
		push (@graphs, ("ipsec0"));
	}

	if (-e "/var/log/rrd/collectd/localhost/interface/if_octets-tun0.rrd"){
		push (@graphs, ("tun0"));
	}

	foreach (@graphs) {
		&Header::openbox('100%', 'center', "$_ $Lang::tr{'graph'}");
		&Graphs::makegraphbox("netexternal.cgi",$_,"day");
		&Header::closebox();
	}

	if ( $netsettings{'CONFIG_TYPE'} =~ /^(1|2|3|4)$/  && $netsettings{'RED_TYPE'} eq "DHCP"){

		&Header::openbox('100%', 'left', "RED $Lang::tr{'dhcp configuration'}");
		if (-s "${General::swroot}/dhcpc/dhcpcd-$netsettings{'RED_DEV'}.info") {

			&General::readhash("${General::swroot}/dhcpc/dhcpcd-$netsettings{'RED_DEV'}.info", \%dhcpinfo);

			my ($DNS1, $DNS2) = split(/ /, $dhcpinfo{'domain_name_servers'});

			my $lsetme=0;
			my $leasetime="";
			if ($dhcpinfo{'dhcp_lease_time'} ne "") {
				$lsetme=$dhcpinfo{'dhcp_lease_time'};
				$lsetme=($lsetme/60);
				
				if ($lsetme > 59) {
					$lsetme=($lsetme/60); $leasetime=$lsetme." Hour";
				}else{
					$leasetime=$lsetme." Minute";
				}
				
				if ($lsetme > 1) {
					$leasetime=$leasetime."s";
				}
			}

			my $rentme=0;
			my $rnwltime="";

			if ($dhcpinfo{'dhcp_renewal_time'} ne "") {
				$rentme=$dhcpinfo{'dhcp_renewal_time'};
				$rentme=($rentme/60);
				
				if ($rentme > 59){
					$rentme=($rentme/60); $rnwltime=$rentme." Hour";
				}else{
					$rnwltime=$rentme." Minute";
				}
				
				if ($rentme > 1){
					$rnwltime=$rnwltime."s";
				}
			}

			my $maxtme=0;
			my $maxtime="";

			if ($dhcpinfo{'dhcp_rebinding_time'} ne "") {
				$maxtme=$dhcpinfo{'dhcp_rebinding_time'};
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


			print <<END
<table width='100%'>
<tr><td width='30%'>$Lang::tr{'domain'}</td><td>$dhcpinfo{'domain_name'}</td></tr>
<tr><td>$Lang::tr{'gateway'}</td><td>$dhcpinfo{'routers'}</td></tr>
<tr><td>$Lang::tr{'primary dns'}</td><td>$DNS1</td></tr>
<tr><td>$Lang::tr{'secondary dns'}</td><td>$DNS2</td></tr>
<tr><td>$Lang::tr{'dhcp server'}</td><td>$dhcpinfo{'dhcp_server_identifier'}</td></tr>
<tr><td>$Lang::tr{'def lease time'}</td><td>$leasetime</td></tr>
<tr><td>$Lang::tr{'default renewal time'}</td><td>$rnwltime</td></tr>
<tr><td>$Lang::tr{'max renewal time'}</td><td>$maxtime</td></tr>
</table>
END
;
		}else{
			print "$Lang::tr{'no dhcp lease'}";
		}
		&Header::closebox();
	}

	&Header::closebigbox();
	&Header::closepage();
