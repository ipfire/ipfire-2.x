#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# (c) 2002 Josh Grubman <jg@false.net> - Multiple registry IP lookup code
#
# $Id: ipinfo.cgi,v 1.4.2.3 2005/02/22 22:21:56 gespinasse Exp $
#

use IO::Socket;
use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require 'CONFIG_ROOT/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %cgiparams=();

&Header::showhttpheaders();

&Header::getcgihash(\%cgiparams);

$ENV{'QUERY_STRING'} =~s/&//g;
my @addrs = split(/ip=/,$ENV{'QUERY_STRING'});

my %whois_servers = ("RIPE"=>"whois.ripe.net","APNIC"=>"whois.apnic.net","LACNIC"=>"whois.lacnic.net");

&Header::openpage($Lang::tr{'ip info'}, 1, '');

&Header::openbigbox('100%', 'left');
my @lines=();
my $extraquery='';
foreach my $addr (@addrs) {
next if $addr eq "";
	$extraquery='';
	@lines=();
	my $whoisname = "whois.arin.net";
	my $iaddr = inet_aton($addr);
	my $hostname = gethostbyaddr($iaddr, AF_INET);
	if (!$hostname) { $hostname = $Lang::tr{'lookup failed'}; }

	my $sock = new IO::Socket::INET ( PeerAddr => $whoisname, PeerPort => 43, Proto => 'tcp');
	if ($sock)
	{
		print $sock "$addr\n";
		while (<$sock>) {
			$extraquery = $1 if (/NetType:    Allocated to (\S+)\s+/);
			push(@lines,$_);
		}
		close($sock);
		if ($extraquery) {
			undef (@lines);
			$whoisname = $whois_servers{$extraquery};
			my $sock = new IO::Socket::INET ( PeerAddr => $whoisname, PeerPort => 43, Proto => 'tcp');
			if ($sock)
			{
				print $sock "$addr\n";
				while (<$sock>) {
					push(@lines,$_);
				}
			}
			else
			{
				@lines = ( "$Lang::tr{'unable to contact'} $whoisname" );
			}
		}
	}
	else
	{
		@lines = ( "$Lang::tr{'unable to contact'} $whoisname" );
	}

	&Header::openbox('100%', 'left', $addr . ' (' . $hostname . ') : '.$whoisname);
	print "<pre>\n";
	foreach my $line (@lines) {
		print &Header::cleanhtml($line,"y");
	}
	print "</pre>\n";
	&Header::closebox();
}

print <<END
<div align='center'>
<table width='80%'>
<tr>
	<td align='center'><a href='$ENV{'HTTP_REFERER'}'>$Lang::tr{'back'}</a></td>
</tr>
</table>
</div>
END
;

&Header::closebigbox();

&Header::closepage();
