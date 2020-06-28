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
# Version: 2020/05/25 19:39:23
#
# This wio-lib.pl is based on the code from the IPCop WIO Addon
# and is extremly adapted to work with IPFire.
#
# Autor: Stephan Feddersen
# Co-Autor: Alexander Marx
# Co-Autor: Frank Mainz (for some code for the IPCop WIO Addon)
#

package WIO;

# enable only the following on debugging purpose
#use warnings;

use strict;
use Socket;
use Time::Local;
use MIME::Lite;

require '/var/ipfire/general-functions.pl';
require '/var/ipfire/header.pl';
require '/var/ipfire/lang.pl';

my %mailsettings = ();

&General::readhash('/var/ipfire/dma/mail.conf', \%mailsettings);

############################################################################################################################

sub getdyndnsip {
	my $ipadr = $_[0];
	my $host = $_[1];
	my @fetchip = ();

	if ( -e "/var/ipfire/red/active" ) {
		@fetchip = gethostbyname($host);

		if ( defined($fetchip[0]) ) {
			@fetchip = map ( &Socket::inet_ntoa($_), @fetchip[4..$#fetchip]);
			return ($fetchip[0], $Lang::tr{'wio_dyndns_success'});
		}
	}
	else {
		return ($ipadr, $Lang::tr{'wio_dyndns_info'});
	}
}

############################################################################################################################

sub contime {
	chomp(my $str = $_[0]);
	chomp(my $vpn = $_[1]);

	my %m = ();
	@m{qw/Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec/} = (0 .. 11);

	my $totalsecs = '';

	if ( $vpn eq 'ipsec' ) {
		my @temp = split (/ /, $str);

		if ( $temp[1] eq 'seconds' ) {
			$totalsecs = $temp[0];
		}

		if ( $temp[1] eq 'minutes' ) {
			$totalsecs = $temp[0] * 60;
		}

		if ( $temp[1] eq 'hours' ) {
			$totalsecs = $temp[0] * 3600;
		}

		if ( $temp[1] eq 'days' ) {
			$totalsecs = $temp[0] * 86400;
		}
	}

	if ( $vpn eq 'ovpn' ) {
		if ( $str =~ /^\w{3}\ ([a-zA-Z]+)\ (\d{1,2})\ (\d{2})\:(\d{2})\:(\d{2}) (\d{4})$/ ||
			 $str =~ /^\w{3}\ ([a-zA-Z]+)\  (\d{1})\ (\d{2})\:(\d{2})\:(\d{2}) (\d{4})$/ )
		{
			my $past = timelocal($5, $4, $3, $2, $m{$1}, $6);
			my $now  = time;
			$totalsecs = $now - $past;
		}
	}

	if ( $totalsecs ne '' )  {
		my $days = int($totalsecs / 86400);
		my $totalhours = int($totalsecs / 3600);
		my $hours = $totalhours % 24;
		my $totalmins = int($totalsecs / 60);
		my $mins = $totalmins % 60;
		my $secs = $totalsecs % 60;

		return "${days}d ${hours}h ${mins}m ${secs}s";
	}
	else {
		return;
	}
}

############################################################################################################################

sub statustime {
	my $str = $_[0];
	my ( $day, $mon ) = '';

	my %m = qw ( Jan 01 Feb 02 Mar 03 Apr 04 May 05 Jun 06 Jul 07 Aug 08 Sep 09 Oct 10 Nov 11 Dec 12 );

	if ( $str =~ /^\w{3}\ ([a-zA-Z]+)\ (\d{1,2})\ (\d{2})\:(\d{2})\:(\d{2}) (\d{4})$/ ||
		 $str =~ /^\w{3}\ ([a-zA-Z]+)\  (\d{1})\ (\d{2})\:(\d{2})\:(\d{2}) (\d{4})$/ )
	{
		$mon = $m{$1};

		if (length $2 < 2) { $day = "0$2"; }
		else { $day = $2; }

		return "$day.$mon.$6 - $3:$4:$5";
	}
	else {
		return;
	}
}

############################################################################################################################

sub mailsender {
	my $msg = '';

	$msg = MIME::Lite->new(
		From	=> $mailsettings{'SENDER'},
		To		=> $mailsettings{'RECIPIENT'},
		Subject	=> $_[0],
		Type	=> 'multipart/mixed'
	);

	$msg->attach(
		Type	=> 'TEXT',
		Data	=> $_[1]
	);

	$msg->send_by_sendmail;
}

############################################################################################################################

sub checkinto {
	my ($checkip, $checkhost, @checkfile) = @_;

	if ( $checkip ne '' ) {
		foreach (@checkfile) {
			chomp;
			if ( (split (/\,/, $_))[2] eq $checkip ) { return $Lang::tr{'wio_ip_exists'}; last; }
		}
	}

	if ( $checkhost ne '' ) {
		foreach (@checkfile) {
			chomp;
			if ( (split (/\,/, $_))[3] eq $checkhost ) {
				if ( $checkip ne '' ) {
					my $fileip = (split (/\,/, $_))[2];

					$fileip =~ /^(\d+)\.(\d+)\.(\d+)\.(\d+)$/;

					my $fileip1 = $1;
					my $fileip2 = $2;
					my $fileip3 = $3;
					my $fileip4 = $4;
					
					$checkip =~ /^(\d+)\.(\d+)\.(\d+)\.(\d+)$/;

					if ( $fileip1 == $1 && $fileip2 == $2 && $fileip3 == $3 ) {
						return $Lang::tr{'wio_host_exists'}; last; }
				}
				else { return $Lang::tr{'wio_host_exists'}; last; }
			}
		}
	}

	return;
}

############################################################################################################################

sub clearfile {
	my $file = $_[0];

	open(FILE, "> $file");
	close(FILE);
}

############################################################################################################################

sub color_devices() {
	my $output = shift;

	if ( uc($output) eq "GREEN0" ) { $output = "<b><font color ='$Header::colourgreen'>$output</b>";}
	elsif ( uc($output) eq "BLUE0" ) { $output = "<b><font color ='$Header::colourblue'>$output</b>"; }
	elsif ( uc($output) eq "ORANGE0" ) { $output = "<b><font color ='$Header::colourorange'>$output</b>"; }
	elsif ( uc($output) eq "RED0" ) { $output = "<b><font color ='$Header::colourred'>$output</b>"; }
	else { return $output = "<b><font color ='#696565'>$output</b>"; }

	return $output;
}

return 1;
