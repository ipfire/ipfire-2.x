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
# Version: 2020/06/01 13:29:23
#
# This wio.pl is based on the code from the IPCop WIO Addon
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
use Time::HiRes qw(gettimeofday tv_interval);
use Net::Ping;
use RRDs;
use Fatal qw/ open /;

require '/var/ipfire/general-functions.pl';
require '/var/ipfire/lang.pl';
require '/usr/lib/wio/wio-lib.pl';

my ( $debug, $i, $t, $ib, $tb, $ivpn, $tvpn ) = '';
my $owner     = getpwnam "nobody";
my $group     = getgrnam "nobody";
my $ipadrfile = "/var/log/wio/wioips";

unless ( -e $ipadrfile ) { print ( "The file $ipadrfile doesn't exist!\n" ); exit; }

foreach (@ARGV) {
  if ( $_ eq '-d' || $_ eq '--debug') { $debug = 1; }
  if ( $_ eq '-h' || $_ eq '--help' ) { die help(); }
}

my ( %wiosettings, %mainsettings, %mailsettings, %netsettings ) = ();

&General::readhash('/var/ipfire/main/settings', \%mainsettings);
&General::readhash('/var/ipfire/ethernet/settings', \%netsettings);
&General::readhash('/var/ipfire/dma/mail.conf', \%mailsettings);
&General::readhash("/var/ipfire/wio/wio.conf", \%wiosettings);

my $now        = strftime "%a, %d.%m.%Y %H:%M:%S", localtime;
my $logging    = $wiosettings{'LOGGING'};
my $mailstyle  = $wiosettings{'MAILSTYLE'};
my $mailremark = $wiosettings{'MAILREMARK'};
my $timeout    = $wiosettings{'TIMEOUT'};
my $rrddir     = "/var/log/rrd/wio";
my $onoffip    = "/var/log/wio/wioscip";
my $hostname   = "$mainsettings{'HOSTNAME'}.$mainsettings{'DOMAINNAME'}";
my $redactive  = "/var/ipfire/red/active";
my $rediface   = "/var/ipfire/red/iface";
my $reddev     = '';

if ( -e $rediface ) {
	$reddev = &General::get_red_interface;
}

my $redip      = $hostname;
my $vpnpid     = ( -e "/var/run/charon.pid" ? `awk '{print $1}' /var/run/charon.pid`: '');
my $ovpnpid    = ( -e  "/var/run/openvpn.pid" ? `awk '{print $1}' /var/run/openvpn.pid`: '');

my $steptime   = $wiosettings{'CRON'} *= 60;
my $i_ping     = 'icmp';
my $t_ping     = 'tcp';

my $nr = 1;

my ( $togglestat, $arp, $time, $start, $timestamp ) = 0;
my ( $id, $ipadr, $ipadrnew, $host, $hostnew, $enable, $remark, $dyndns, $dyndnsip ) = '';
my ( $mail, $mailon, $mailoff, $ping, $on, $httphost, $mailen ) = '';
my ( $msg, $logmsg, $mailmsg, $smailtxt, $infomsg, $client, $mode, $onbak, $arpclient ) = '';
my ( $ping_i, $ping_t, $ping_ib, $ping_tb, $ping_iv, $ping_tv, $pingmode ) = '';
my ( @tmp, @arptmp, @myarray, @status, @arpclients ) = '';
my @ifaces = ('GREEN','BLUE','ORANGE');

if ( $netsettings{'RED_TYPE'} eq 'STATIC' || $netsettings{'RED_TYPE'} eq 'DHCP' ) {
	push (@ifaces, "RED");
}

if ( $mailsettings{'USEMAIL'} eq 'on' ) { $mailen = 'on'; }
else { $mailen = 'off'; }

if ( -e $redactive ) {
	open(IPADDR, "/var/ipfire/red/local-ipaddress");
	$redip = <IPADDR>;
	close IPADDR;
	chomp($redip);
}

if ($debug) {
	$start = [gettimeofday];
	startdebug();
}

foreach (@ifaces) {
	if ( $netsettings{"${_}_DEV"} ne '' && $netsettings{"${_}_DEV"} ne 'disabled' ) {
		my $output = `ifconfig $netsettings{"${_}_DEV"}`;

		if ( grep (/RX bytes:0/, $output) ) { next; }
		else {
			@arptmp = `/usr/local/bin/wioscan -s $netsettings{"${_}_DEV"}`;

			foreach $arpclient (@arptmp) {
				push (@arpclients, (split (/\,/,$arpclient))[1]);
			}
		}
		$output = '';
		undef(@arptmp);
	}
}

if ( -e "$onoffip" ) { open( FILE, "< $onoffip" ); }
else { open( FILE, "< $ipadrfile" ); }
@myarray = <FILE>;
close(FILE);

# ping all clients

foreach (@myarray) {
	chomp;
	@tmp = split( /\,/, $_ );

	($id,$timestamp,$ipadr,$host,$enable,$remark,$dyndns,$mailon,$mailoff,$ping,$on,$httphost) = @tmp;

	$timestamp = strftime "%d.%m.%Y - %H:%M:%S", localtime;

	if ( $enable ne 'on' ) {
		push (@status, "$id,$timestamp,$ipadr,$host,$enable,$remark,$dyndns,$mailon,$mailoff,$ping,$on,$httphost\n");
		next;
	}

	if ( defined($dyndns) && ( $dyndns =~ 'on' ) ) {
		($dyndnsip, $infomsg) = &WIO::getdyndnsip($host, @myarray);
		if ($dyndnsip ne $ipadr) { $ipadr = $dyndnsip; }
	}

	$ping_i = $ping_t = $ping_ib = $ping_tb = $ping_iv =  $ping_tv = $pingmode = $arp = 0;

	foreach (@arpclients) {
		chomp;
		unless ( $ipadr eq $_ )
		{
			$i = Net::Ping->new( $i_ping, $timeout );
			unless ( defined $i ) { die "Can't create Net::Ping object $!"; }

			$t = Net::Ping->new( $t_ping, $timeout );
			unless ( defined $t ) { die "Can't create Net::Ping object $!"; }

			$ib = Net::Ping->new( $i_ping, $timeout );
			unless ( defined $ib ) { die "Can't create Net::Ping object $!"; }
			$ib->bind($redip);

			$tb = Net::Ping->new( $t_ping, $timeout );
			unless ( defined $tb ) { die "Can't create Net::Ping object $!"; }
			$tb->bind($redip);

			if ($ovpnpid || $vpnpid)
			{
				$ivpn = Net::Ping->new( $i_ping, $timeout );
				unless ( defined $ivpn ) { die "Can't create Net::Ping object $!"; }
				$ivpn->bind($hostname);

				$tvpn = Net::Ping->new( $t_ping, $timeout );
				unless ( defined $tvpn ) { die "Can't create Net::Ping object $!"; }
				$tvpn->bind($hostname);
			}
		}
		else { $arp = 1 }
	}

	$client = ( ( $dyndns eq 'on' || $ping eq 'fqdn' ) ? $host : $ipadr );

	if ($debug) {
		printf "%2s   %15s", $nr++,  ($client ne $ipadr ? $ipadr : $client );
		$time = [gettimeofday];
	}

	if ( $arp == 1 
		|| ($ping_i = $i->ping($client))
		|| ($ping_t = $t->ping($client))
		|| ($ping_ib = $ib->ping($client))
		|| ($ping_tb = $tb->ping($client))
		|| ($ovpnpid?($ping_iv = $ivpn->ping($client)) : 0)
		|| ($vpnpid?($ping_tv = $tvpn->ping($client)) : 0) )
	{
		$mode       = 100;
		$msg        = "$Lang::tr{'wio up'}";
		$onbak      = $on;
		$togglestat = ( $on ne 'on' ) ? 1 : 0;
		$on         = 'on';
	}
	else {
		$mode       = 0;
		$msg        = "$Lang::tr{'wio down'}";
		$onbak      = $on;
		$togglestat = ( $on ne 'off' ) ? 1 : 0;
		$on         = 'off';
	}

	push (@status, "$id,$timestamp,$ipadr,$host,$enable,$remark,$dyndns,$mailon,$mailoff,$ping,$on,$httphost\n");

	if ($debug) {
		$mail = '----';
		if ( $mailon eq 'on' && $togglestat == 1 && $mode == 100 ) { $mail = 'Online'; }
		if ( $mailoff eq 'on' && $togglestat == 1 && $mode == 0 ) { $mail = 'Offline'; }
		if ( $dyndns ne 'on' ) { $dyndns = 'off'; }

		$pingmode = $arp ? 'ARPSCAN' : $ping_i ? 'ICMP' : $ping_t ? 'TCP' : $ping_ib ? 'ICMP+BIND' : $ping_tb ? 'TCP+BIND' : $ping_iv ? 'VPN ICMP' : $ping_tv ? 'VPN TCP' : 'NO ECHO';  
		printf "%7s%8s%9s%10s     %.4f sek%12s\n", $ping, $dyndns, $msg, $mail, tv_interval($time), $pingmode;
	}

	if ( $host eq '' ) { $hostnew = 'n/a'; } else { $hostnew = $host; }
	if ( $ipadr eq '' ) { $ipadrnew = 'n/a'; } else { $ipadrnew = $ipadr; }

	if ( $logging eq 'on' ) {
		$logmsg = "Client: $hostnew - IP: $ipadrnew - Status: $msg";
		&General::log("wio","$logmsg");
	}

	if ( $mailen eq 'on' && $togglestat == 1 && ($mailon eq 'on' || $mailoff eq 'on')) {
	
		if ( $mailstyle eq 'email' || ($mailstyle eq 'smail' && $smailtxt eq '') ) { $mailmsg .= "Date\t : $now\n\n"; }

		$mailmsg .= "Client\t : $hostnew\nIP\t : $ipadrnew\nStatus\t : $msg\n";

		if ( $mailremark eq 'on' && $remark ne '' ) {
			$mailmsg .= "Remark : $remark\n\n";
		}

		if ( $mailstyle eq 'email' ) {
			&WIO::mailsender("WIO - $host - $msg", $mailmsg);
			undef ($mailmsg);
		}
		elsif ( $mailstyle eq 'smail'  ) {
			$smailtxt .= $mailmsg."\n";
			undef ($mailmsg);
		}
	}

	if ( $ping ne 'fqdn' ) { $client = $host; }
	if ( $host eq '' ) { $client = $ipadr; }

	updatewiodata("$id");

	if ( $arp == 0 ) {
		$i->close();
		$t->close();
		$ib->close();
		$tb->close();
	}

	if ( ( -e $ovpnpid || -e $vpnpid ) && $arp == 0 ) {
		$ivpn->close();
		$tvpn->close();
	}
}

# write ipadressfile new

if ( !-e $onoffip ) {
	open( FILE, "> $ipadrfile" );
	print FILE @status;
	close(FILE);
}
else {
	system("/bin/sed -i 's#$tmp[0],$tmp[1],$tmp[2],$tmp[3],$tmp[4],$tmp[5],$tmp[6],$tmp[7],$tmp[8],$tmp[9],$tmp[10],$tmp[11]#$id,$timestamp,$ipadr,$host,$enable,$remark,$dyndns,$mailon,$mailoff,$ping,$on,$httphost#g' $ipadrfile");
	chmod ( 0644, $ipadrfile ); 
	chown ( $owner, $group, $ipadrfile );
}

if ($debug) {
	printf ("\n$Lang::tr{'wio_scriptruntime'}:  %.4f $Lang::tr{'age ssecond'}\n\n", tv_interval($start));
}

if ( $smailtxt ne '' ) { &WIO::mailsender($Lang::tr{'wio_sub'}, $smailtxt); }

undef (@tmp);
undef (@myarray);
undef (@status);
undef (@arptmp);
undef (@arpclients);

if ( -e $onoffip ) { unlink($onoffip); }

sub updatewiodata {
	my $id = $_[0];

	if ( !-e "$rrddir/$id.rrd" ) {
		RRDs::create(
			"$rrddir/$id.rrd",      "--step=$steptime",
			"DS:mode:GAUGE:3600:0:100", "RRA:AVERAGE:0.5:1:576",
			"RRA:AVERAGE:0.5:6:672",    "RRA:AVERAGE:0.5:24:732",
			"RRA:AVERAGE:0.5:144:1460"
		);
		my $ERROR = RRDs::error;
		print "Error in RRD::create for Who Is Online: $ERROR\n" if $ERROR;
	}

	RRDs::update( "$rrddir/$id.rrd", "-t", "mode", "N:$mode" );

	my $error = RRDs::error;

	if ($error) { &General::log("wio","$error"); }
}

sub startdebug {
printf "
HOSTNAME    : $hostname
TIMEOUT     : $timeout $Lang::tr{'age ssecond'}
MAILSTYLE   : $mailstyle
RED TYPE    : $netsettings{'RED_TYPE'}
RED DEVICE  : $reddev
RED ADDRESS : $redip
";

if ($ovpnpid) {printf "OpenVPN PID : $ovpnpid"}
if ($vpnpid) {printf "IPsec PID   : $vpnpid"}

printf  "
$Lang::tr{'wio_search'}

%3s%17s%7s%8s%9s%10s%15s%12s
---------------------------------------------------------------------------------
","ID ", "$Lang::tr{'wio ipadress'}", "Ping", "DynDNS", "Status", "Mail", "$Lang::tr{'wio_answer_time'}", "$Lang::tr{'wio_answer'}";
}

sub help {
	return "
Who Is Online? for IPFire

use option -d for debugging
use option -h for help\n\n";
}
