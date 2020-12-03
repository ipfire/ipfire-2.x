#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2020  IPFire Team  <info@ipfire.org>                     #
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

use CGI;
use IO::Socket;
use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "${General::swroot}/location-functions.pl";

# Load colours for current theme...
my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

my %cgiparams=();

&Header::showhttpheaders();

my @lines=();
my $extraquery='';

# Hash which contains the whois servers from
# the responisible RIR of the continent.
my %whois_servers_by_continent = (
	"AF" => "whois.afrinic.net",
	"AS" => "whois.apnic.net",
	"EU" => "whois.ripe.net",
	"NA" => "whois.arin.net",
	"SA" => "whois.lacnic.net"
);

# Default whois server if no continent could be determined.
my $whois_server = "whois.arin.net";

my $addr = CGI::param("ip") || "";

if (&General::validip($addr)) {
	# Write HTML page header...
	&Header::openpage($Lang::tr{'ip info for'} . ' ' . $addr, 1, '');
	&Header::openbigbox('100%', 'left');

	my $iaddr = inet_aton($addr);
	my $hostname = gethostbyaddr($iaddr, AF_INET);
	if (!$hostname) { $hostname = $Lang::tr{'ptr lookup failed'}; }

	# Enumerate location information for IP address...
	my $ccode = &Location::Functions::lookup_country_code($addr);
	my $cname = &Location::Functions::get_full_country_name($ccode);
	my @network_flags = &Location::Functions::address_has_flags($addr);

	# Try to get the continent of the country code.
	my $continent = &Location::Functions::get_continent_code($ccode);

	# Enumerate Autonomous System details for IP address...
	my $asn = &Location::Functions::lookup_asn($addr);
	my $as_name;
	if ($asn) {
		$as_name = &Location::Functions::get_as_name($asn);

		# In case we have found an AS name, make output more readable...
		if ($as_name) {
			$as_name = "- " . $as_name;
		}
		$asn = "AS" . $asn;
	} else {
		$asn = $Lang::tr{'asn lookup failed'};
	}

	# Check if a whois server for the continent is known.
	if($whois_servers_by_continent{$continent}) {
		# Use it.
		$whois_server = $whois_servers_by_continent{$continent};
	}

	my $flag_icon = &Location::Functions::get_flag_icon($ccode);

	&Header::openbox('100%', 'left', $Lang::tr{'ip basic info'});

	print <<END;
		<center>
			<table class="tbl" width='100%'>
				<tr>
					<td bgcolor='$color{'color22'}'><strong>$Lang::tr{'country'}</strong></td>
					<td bgcolor='$color{'color22'}'>$cname <a href='country.cgi#$ccode'><img src="$flag_icon" border="0" align="absmiddle" alt="$cname" title="$cname" /></td>
				</tr>
				<tr>
					<td bgcolor='$color{'color20'}'><strong>$Lang::tr{'ptr'}</strong></td>
					<td bgcolor='$color{'color20'}'>$hostname</td>
				</tr>
				<tr>
					<td bgcolor='$color{'color22'}'><strong>$Lang::tr{'autonomous system'}</strong></td>
					<td bgcolor='$color{'color22'}'>$asn $as_name</td>
				</tr>
END

	# Check if the address has a flag.
	if (@network_flags) {
		# Get amount of flags for this network.
		my $flags_amount = @network_flags;
		my $processed_flags;

		# Loop through the array of network_flags.
		foreach my $network_flag (@network_flags) {
			# Increment value of processed flags.
			$processed_flags++;

			# Get the network flag name.
			my $network_flag_name = &Location::Functions::get_full_country_name($network_flag);

			# Colorize columns.
			my $col;
			if ($processed_flags % 2) {
				$col = "bgcolor='$color{'color20'}'"; }
			else {
				$col = "bgcolor='$color{'color22'}'";
			}

			# Write table row...
			print <<END;
				<tr>
					<td $col><strong>$network_flag_name</strong></td>
					<td $col>$Lang::tr{'yes'}</td>
				</tr>
END
		}
	}

	print "			</table>\n";
	print "		</center>\n";

	&Header::closebox();

	my $sock = new IO::Socket::INET ( PeerAddr => $whois_server, PeerPort => 43, Proto => 'tcp');
	if ($sock)
	{
		print $sock "$addr\n";
		while (<$sock>) {
			$extraquery = $1 if (/ReferralServer:  whois:\/\/(\S+)\s+/);
			push(@lines,$_);
		}
		close($sock);
		if ($extraquery) {
			undef (@lines);
			$whois_server = $extraquery;
			my $sock = new IO::Socket::INET ( PeerAddr => $whois_server, PeerPort => 43, Proto => 'tcp');
			if ($sock)
			{
				print $sock "$addr\n";
				while (<$sock>) {
					push(@lines,$_);
				}
			}
			else
			{
				@lines = ( "$Lang::tr{'unable to contact'} $whois_server" );
			}
		}
	}
	else
	{
		@lines = ( "$Lang::tr{'unable to contact'} $whois_server" );
	}

	&Header::openbox('100%', 'left', $Lang::tr{'whois results from'} . " " . $whois_server);

	print "<pre>\n";
	foreach my $line (@lines) {
		print &Header::cleanhtml($line,"y");
	}
	print "</pre>\n";
	&Header::closebox();
} else {
	# Open HTML page header in case of invalid IP addresses
	&Header::openpage($Lang::tr{'ip info'}, 1, '');
	&Header::openbigbox('100%', 'left');

	&Header::openbox('100%', 'left', $Lang::tr{'invalid ip'});
	print <<EOF;
		<p style="text-align: center;">
			$Lang::tr{'invalid ip'}
		</p>
EOF
	&Header::closebox();
}

print <<END
<div align='center'>
<table width='80%'>
<tr>
	<td align='center'><a href='$ENV{'HTTP_REFERER'}'><img src='/images/back.png' alt='$Lang::tr{'back'}' title='$Lang::tr{'back'}' /></a></td>
</tr>
</table>
</div>
END
;

&Header::closebigbox();

&Header::closepage();
