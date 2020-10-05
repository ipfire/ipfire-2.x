#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2010  IPFire Team  <info@ipfire.org>                          #
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

my %cgiparams=();

&Header::showhttpheaders();

&Header::openpage($Lang::tr{'ip info'}, 1, '');
&Header::openbigbox('100%', 'left');
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
	my $iaddr = inet_aton($addr);
	my $hostname = gethostbyaddr($iaddr, AF_INET);
	if (!$hostname) { $hostname = $Lang::tr{'lookup failed'}; }

	# enumerate location information for IP address...
	my $db_handle = &Location::Functions::init();
	my $ccode = &Location::Functions::lookup_country_code($db_handle, $addr);
	my @network_flags = &Location::Functions::address_has_flags($addr);

	# Try to get the continent of the country code.
	my $continent = &Location::get_continent_code($db_handle, $ccode);

	# Check if a whois server for the continent is known.
	if($whois_servers_by_continent{$continent}) {
		# Use it.
		$whois_server = $whois_servers_by_continent{$continent};
	}

	my $flag_icon = &Location::Functions::get_flag_icon($ccode);

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

	&Header::openbox('100%', 'left', $addr . " <a href='country.cgi#$ccode'><img src='$flag_icon' border='0' align='absmiddle' alt='$ccode' title='$ccode' /></a> (" . $hostname . ') : '.$whois_server);

	# Check if the address has a flag.
	if (@network_flags) {
		# Get amount of flags for this network.
		my $flags_amount = @network_flags;
		my $processed_flags;

		# The message string which will be displayed.
		my $message_string = "This address is marked as";

		# Loop through the array of network_flags.
		foreach my $network_flag (@network_flags) {
			# Increment value of processed flags.
			$processed_flags++;

			# Get the network flag name.
			my $network_flag_name = &Location::Functions::get_full_country_name($network_flag);

			# Add the flag name to the message string.
			$message_string = "$message_string" . " $network_flag_name";

			# Check if multiple flags are set for this network.
			if ($flags_amount gt "1") {
				# Check if the the current flag is the next-to-last one.
				if ($processed_flags eq $flags_amount - 1) {
					$message_string = "$message_string" . " and ";

				# Check if the current flag it the last one.
				} elsif ($processed_flags eq $flags_amount) {
					# The message is finished add a dot for ending the sentence.
					$message_string = "$message_string" . ".";

				# Otherwise add a simple comma to the message string.
				} else {
					$message_string = "$message_string" . ", ";
				}
			} else {
				# Nothing special to do, simple add a dot to finish the sentence.
				$message_string = "$message_string" . ".";
			}
		}

		# Display the generated notice.
		print "<h3>$message_string</h3>\n";
		print "<br>\n";
	}

	print "<pre>\n";
	foreach my $line (@lines) {
		print &Header::cleanhtml($line,"y");
	}
	print "</pre>\n";
	&Header::closebox();
} else {
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
