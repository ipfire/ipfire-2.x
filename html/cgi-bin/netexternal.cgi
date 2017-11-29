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

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

use IO::Socket;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "${General::swroot}/geoip-functions.pl";
require "${General::swroot}/graphs.pl";

my %color = ();
my %mainsettings = ();
my %netsettings=();
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

my @graphs=();
my %dhcpinfo=();

my @querry = split(/\?/,$ENV{'QUERY_STRING'});
$querry[0] = '' unless defined $querry[0];
$querry[1] = 'hour' unless defined $querry[1];

if ( $querry[0] ne~ ""){
	print "Content-type: image/png\n\n";
	binmode(STDOUT);
	&Graphs::updateifgraph($querry[0],$querry[1]);
}else{

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

	## DNSSEC
	my @nameservers = ();
	foreach my $f ("${General::swroot}/red/dns1", "${General::swroot}/red/dns2") {
		open(DNS, "<$f");
		my $nameserver = <DNS>;
		close(DNS);

		chomp($nameserver);
		if ($nameserver) {
			push(@nameservers, $nameserver);
		}
	}

	&Header::openbox('100%', 'center', $Lang::tr{'dnssec information'});

	print <<END;
		<table class="tbl" width='66%'>
			<thead>
				<tr>
					<th align="center">
						<strong>$Lang::tr{'nameserver'}</strong>
					</th>
					<th align="center">
						<strong>$Lang::tr{'country'}</strong>
					</th>
					<th align="center">
						<strong>$Lang::tr{'rdns'}</strong>
					</th>
					<th align="center">
						<strong>$Lang::tr{'status'}</strong>
					</th>
				</tr>
			</thead>
			<tbody>
END

	my $id = 0;
	for my $nameserver (@nameservers) {
		my $status = &check_dnssec($nameserver, "ping.ipfire.org");

		my $colour = "";
		my $bgcolour = "";
		my $message = "";

		# DNSSEC Not supported
		if ($status == 0) {
			$message = $Lang::tr{'dnssec not supported'};
			$colour = "white";
			$bgcolour = ${Header::colourred};

		# DNSSEC Aware
		} elsif ($status == 1) {
			$message = $Lang::tr{'dnssec aware'};
			$colour = "black";
			$bgcolour = ${Header::colouryellow};

		# DNSSEC Validating
		} elsif ($status == 2) {
			$message = $Lang::tr{'dnssec validating'};
			$colour = "white";
			$bgcolour = ${Header::colourgreen};

		# Error
		} else {
			$colour = ${Header::colourred};
		}

		my $table_colour = ($id++ % 2) ? $color{'color22'} : $color{'color20'};

		# collect more information about name server (rDNS, GeoIP country code)
		my $ccode = &GeoIP::lookup($nameserver);
		my $flag_icon = &GeoIP::get_flag_icon($ccode);

		my $iaddr = inet_aton($nameserver);
		my $rdns = gethostbyaddr($iaddr, AF_INET);
		if (!$rdns) { $rdns = $Lang::tr{'lookup failed'}; }

		print <<END;
			<tr bgcolor="$table_colour">
				<td>
					$nameserver
				</td>
				<td align="center">
					<a href='country.cgi#$ccode'><img src="$flag_icon" border="0" alt="$ccode" title="$ccode" /></a>
				</td>
				<td align="center">
					$rdns
				</td>
				<td bgcolor="$bgcolour" align="center">
					<font color="$colour"><strong>$message</strong></font>
				</td>
			</tr>
END
	}

	print <<END;
			</tbody>
		</table>
END

	&Header::closebox();

	if ( $netsettings{'CONFIG_TYPE'} =~ /^(1|2|3|4)$/  && $netsettings{'RED_TYPE'} eq "DHCP"){

		&Header::openbox('100%', 'left', "RED $Lang::tr{'dhcp configuration'}");
		if (-s "${General::swroot}/dhcpc/dhcpcd-$netsettings{'RED_DEV'}.info") {

			&General::readhash("${General::swroot}/dhcpc/dhcpcd-$netsettings{'RED_DEV'}.info", \%dhcpinfo);

			my $DNS1=`echo $dhcpinfo{'domain_name_servers'} | cut -f 1 -d " "`;
			my $DNS2=`echo $dhcpinfo{'domain_name_servers'} | cut -f 2 -d " "`;

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
}

sub check_dnssec($$) {
	my $nameserver = shift;
	my $record = shift;

	my @command = ("dig", "+dnssec", $record, "\@$nameserver");

	my @output = qx(@command);
	my $output = join("", @output);

	my $status = 0;
	if ($output =~ m/status: (\w+)/) {
		$status = ($1 eq "NOERROR");

		if (!$status) {
			return -1;
		}
	}

	my @flags = ();
	if ($output =~ m/flags: (.*);/) {
		@flags = split(/ /, $1);
	}

	my $aware = ($output =~ m/RRSIG/);
	my $validating = ("ad" ~~ @flags);

	return $aware + $validating;
}
