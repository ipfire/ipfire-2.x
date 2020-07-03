#!/usr/bin/perl
#
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2017-2020 Stephan Feddersen <sfeddersen@ipfire.org>           #
# All Rights Reserved.                                                        #
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
#
# Version: 2020/05/04 12:02:23
#
# This wioovpn.pl is based on the code from the IPCop WIO Addon
# and is extremly adapted to work with IPFire.
#
# Autor: Stephan Feddersen
# Co-Autor: Alexander Marx
# Co-Autor: Frank Mainz (for some code for the IPCop WIO Addon)
#

# enable only the following on debugging purpose
#use warnings;

use strict;
use POSIX qw(strftime);

require '/var/ipfire/general-functions.pl';
require '/var/ipfire/lang.pl';
require '/usr/lib/wio/wio-lib.pl';

my %wiosettings = ();

&General::readhash( "/var/ipfire/wio/wio.conf", \%wiosettings );

my $mailremark = $wiosettings{'MAILREMARK'};
my $logging    = $wiosettings{'LOGGING'};

my ( @ovpnstatus, @ovpncfg, @ovpncache, @ovpnarray, @ovpnmatch, @ovpnwrite );

my $now         = strftime "%a, %d.%m.%Y %H:%M:%S", localtime;
my $ovpnpid     = "/var/run/openvpn.pid";
my $ovpnmailmsg = '';
my $ovpncache   = "/var/log/wio/.ovpncache";
my $ovpnconfig  = "/var/ipfire/ovpn/ovpnconfig";

my ( $name, $nameul, $ovpnclt, $ovpncltip, $realipadr, $connected )  = '';
my ( $ovpnmailsub, $ovpnrwlogin, $ovpnrwstatus, $status, $remark, $logmsg ) = '';

my ( @vpnstatus, @vpncfg, @vpncache, @vpnarray, @vpnwrite );

my $vpnpid       = "/var/run/charon.pid";
my $vpnmailmsg   = '';
my $vpncache     = "/var/log/wio/.vpncache";
my $vpnconfig    = "/var/ipfire/vpn/config";

my ( $vpnmailsub, $vpnrwstatus )  = '';

my $togglestat = 0;

if ( ! -e "$ovpnpid" ) {
	unlink "$ovpncache";
}
else {

@ovpnstatus = `cat /var/run/ovpnserver.log`;

open(FILE, "$ovpnconfig");
@ovpncfg = <FILE>;
close (FILE);

unless ( -e "$ovpncache" ) {
	open(FILE, ">$ovpncache");
	close (FILE);
}
else {
	open(FILE, "$ovpncache");
	@ovpncache = <FILE>;
	close (FILE);
}

foreach (@ovpncfg) {
	chomp;

	if ( $_ =~ "server" ) { next; }

	( $name, $remark ) = (split (/\,/, $_))[3, 26];

	unless ( grep (/$name/, @ovpncache) ) { push (@ovpncache, "$name,$remark,off\n"); }
}

foreach (@ovpncache) {
	chomp;

	( $name, $remark, $status ) = split (/\,/, $_);

	if ( grep (/$name/, @ovpncfg) ) { push (@ovpnarray, "$name,$remark,$status\n"); }
}

foreach (@ovpnarray) {
	chomp;

	( $name, $remark, $status ) = split (/\,/, $_);

	$remark = `/bin/cat $ovpnconfig | grep '$name' | cut -d "," -f 27`;
	chomp ($remark);

	if ( $name =~ m/_/ ) { $nameul = $name; }
	else { ($nameul = $name) =~ s/ /_/g; }

	if ( grep (/$name/, @ovpnstatus) || grep (/$nameul/, @ovpnstatus) ) {
		foreach (@ovpnstatus) {
			chomp;

			if ( $_ =~ "ROUTING TABLE" ) { last; }

			@ovpnmatch = split (/\,/, $_);

			if ( @ovpnmatch != 5 || $_ =~ "Common Name" ) { next; }

			( $ovpnclt, $realipadr, undef, undef, $connected ) = @ovpnmatch;

			( $ovpncltip, undef ) = split (/:/, $realipadr);

			$ovpnrwlogin  = &WIO::statustime($connected);

			if ( $nameul eq $ovpnclt || $name eq $ovpnclt ) {
				$ovpnrwstatus = "$Lang::tr{'wio up'}";
				$togglestat   = ( $status ne 'on' ) ? 1 : 0;
				$status       = 'on';
			}

			if ( ! $name =~ m/_/ ) { $ovpnclt =~ s/_/ /g; }

			if ( $nameul eq $ovpnclt || $name eq $ovpnclt ) { push (@ovpnwrite, "$name,$remark,$status\n"); }

			if ( $togglestat == 1 && ($name eq $ovpnclt || $nameul eq $ovpnclt) ) {
				$ovpnmailsub = "WIO OVPN - $name - $ovpnrwstatus - $now";
				$logmsg = "Client: WIO OVPN $name - IP: $ovpncltip - Status: $ovpnrwstatus";
				$ovpnmailmsg = "Client : $name\nLogin  : $ovpnrwlogin\nIP     : $ovpncltip\nStatus : $ovpnrwstatus\n";

				if ( $mailremark eq 'on' ) {
					$ovpnmailmsg .= "Remark : $remark\n\n";
				}

				&WIO::mailsender($ovpnmailsub, $ovpnmailmsg);
				if ( $logging eq 'on' ) { &General::log("wio","$logmsg"); }
				undef ($ovpnmailsub);
				undef ($ovpnmailmsg);
				$togglestat = 0;
			}
		}
	}
	else {
		if ( $status eq 'on' ) {
			$ovpnrwstatus = "$Lang::tr{'wio down'}";
			$status = 'off';
			$ovpnmailsub  = "WIO OVPN - $name - $ovpnrwstatus - $now";
			$logmsg = "Client: WIO OVPN $name - Status: $ovpnrwstatus";
			$ovpnmailmsg = "Client : $name\nLogout : $now\nStatus : $ovpnrwstatus\n";

			if ( $mailremark eq 'on' ) { $ovpnmailmsg .= "Remark : $remark\n\n"; }

			&WIO::mailsender($ovpnmailsub, $ovpnmailmsg);

			if ( $logging eq 'on' ) { &General::log("wio","$logmsg"); }
			undef ($ovpnmailsub);
			undef ($ovpnmailmsg);
		}

		push (@ovpnwrite, "$name,$remark,$status\n");
	}
}

open( FILE, "> $ovpncache" );
print FILE @ovpnwrite;
close(FILE);

}

if ( ! -e "$vpnpid" ) {
	unlink "$vpncache";
}
else {

@vpnstatus = `/usr/local/bin/ipsecctrl I`;

open(FILE, "$vpnconfig");
@vpncfg = <FILE>;
close (FILE);

unless ( -e "$vpncache" ) {
	open(FILE, ">$vpncache");
	close (FILE);
}
else {
	open(FILE, "$vpncache");
	@vpncache = <FILE>;
	close (FILE);
}

foreach (@vpncfg) {
	chomp;

	( $name, $remark ) = (split (/\,/, $_))[2, 26];

	unless ( grep (/$name/, @vpncache) ) { push (@vpncache, "$name,$remark,off\n"); }
}

foreach (@vpncache) {
	chomp;

	( $name, $remark, $status ) = split (/\,/, $_);
	
	if ( grep (/$name/, @vpncfg) ) { push (@vpnarray, "$name,$remark,$status\n"); }
}

foreach (@vpnarray) {
	chomp;
	
	( $name, $remark, $status ) = split (/\,/, $_);

	$remark = `/bin/cat $vpnconfig | grep '$name' | cut -d "," -f 27`;
	chomp ($remark);

	if ( grep (/$name\{.*INSTALLED/ , @vpnstatus) ) {
		$vpnrwstatus = "$Lang::tr{'wio up'}";
		$togglestat   = ( $status ne 'on' ) ? 1 : 0;
		$status       = 'on';
	}
	else {
		$vpnrwstatus = "$Lang::tr{'wio down'}";
		$togglestat   = ( $status ne 'off' ) ? 1 : 0;
		$status       = 'off';
	}

	push (@vpnwrite, "$name,$remark,$status\n");

	if ( $togglestat == 1 ) {
		$vpnmailsub  = "WIO IPsec - $name - $vpnrwstatus - $now";
		$logmsg = "Client: WIO IPSec $name - Status: $vpnrwstatus $now";
		$vpnmailmsg = "Client : $name\n";

		if ( $status eq 'on' ) {
			$vpnmailmsg .= "Login  : $now\n";
		}
		else {
			$vpnmailmsg .= "Logout : $now\n";
		}

		$vpnmailmsg .= "Status : $vpnrwstatus\n";

		if ( $mailremark eq 'on' ) { $vpnmailmsg .= "Remark : $remark\n\n"; }

		&WIO::mailsender($vpnmailsub, $vpnmailmsg);

		if ( $logging eq 'on' ) { &General::log("wio","$logmsg"); }
		undef ($vpnmailsub);
		undef ($vpnmailmsg);
		$togglestat = 0;
	}
}

open( FILE, "> $vpncache" );
print FILE @vpnwrite;
close(FILE);

}
