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
# Version: 2020/08/04 21:12:23
#
# This wio.cgi is based on the code from the IPCop WIO Addon
# and is extremly adapted to work with IPFire.
#
# Autor: Stephan Feddersen
# Co-Autor: Alexander Marx
# Co-Autor: Frank Mainz (for some code for the IPCop WIO Addon)
#

use strict;

# enable only the following on debugging purpose
#use warnings;
#no warnings 'once';
#use CGI::Carp 'fatalsToBrowser';

my $debug = 0;

use Socket;
use POSIX qw(strftime);
use File::Copy;
use Fatal qw/ open /;
use Net::Telnet;

require '/var/ipfire/general-functions.pl';
require '/var/ipfire/network-functions.pl';
require '/var/ipfire/lang.pl';
require '/var/ipfire/header.pl';
require '/usr/lib/wio/wio-lib.pl';
require '/usr/lib/wio/wio-graphs.pl';

my $logdir = "/var/log/wio";

my ( %mainsettings, %mailsettings, %wiosettings, %cgiparams, %netsettings, %ipshash, %vpnsettings,
	 %vpnconfighash, %ovpnconfighash, %ovpnccdconfhash, %ovpnsettings, %checked, %selected, %color ) = ();

&General::readhash('/var/ipfire/main/settings', \%mainsettings);
&General::readhash('/var/ipfire/ethernet/settings', \%netsettings);
&General::readhash('/var/ipfire/dma/mail.conf', \%mailsettings);
&General::readhash('/var/ipfire/wio/wio.conf', \%wiosettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);
&General::readhasharray('/var/ipfire/ovpn/ovpnconfig', \%ovpnconfighash);
&General::readhash('/var/ipfire/ovpn/settings', \%ovpnsettings);
&General::readhasharray('/var/ipfire/ovpn/ccd.conf', \%ovpnccdconfhash);
&General::readhasharray('/var/ipfire/vpn/config', \%vpnconfighash);
&General::readhash('/var/ipfire/vpn/settings', \%vpnsettings);

my $ipadrfile    = "$logdir/wioips";
my $onoffip      = "$logdir/wioscip";
my $wiosettings  = "/var/ipfire/wio/wio.conf";
my $dyndnsconfig = "/var/ipfire/ddns/config";
my $importfile   = "$logdir/importfile";
my $wiofile      = "$logdir/wiofile";
my $editfile     = "$logdir/editfile";
my $hostfile     = "/var/ipfire/main/hosts";
my $dhcpfile     = "/var/ipfire/dhcp/fixleases";
my $imgstatic    = "/images/wio";
my $rrddir       = "/var/log/rrd/wio";
my $refreshbox   = '<meta http-equiv="refresh" content="0;url=/cgi-bin/wio.cgi">';
my $sortstring   = '^IPADR|^HOST';
my $ovpnaddon    = "/var/ipfire/ovpn";
my $ovpnpid      = "/var/run/openvpn.pid";
my $vpnpid       = "/var/run/charon.pid";
my $redactive    = "/var/ipfire/red/active";
my $redip        = '-';
my $now          = strftime "%Y-%m-%d", localtime;

if ( -e $redactive ) {
	open(IPADDR, "/var/ipfire/red/local-ipaddress");
	$redip = <IPADDR>;
	close IPADDR;
	chomp($redip);
}

my $i = 0;
my $idarp = 0;
my $iddyndns = 0;
my $idvpn = 0;
my $idovpn = 0;
my $idsort = 0;
my $nr = 0;
my $count = 0;
my $showcount = 0;

my $arpbuttontext = "$Lang::tr{'wio_show_table_on'}";
my $clientimportbuttontext = "$Lang::tr{'wio_show_table_on'}";
my $networksearchbuttontext = "$Lang::tr{'wio_show_table_on'}";

my ( $message, $infomessage, $errormessage, $importmessage ) = '';

my ( $buttontext, $host, $timestamp, $ipadr, $on, $remark, $dyndns, $dyndnsip, $sendemailon, $net, $dev, $iprange, $output, $write, $webinterface,
	 $sendemailoff, $pingmethode, $online, $color, $bgcolor, $exitcode, $id, $line, $interface, $counter, $vpnn2nip, $vpnn2nmask, $edc,
	 $edd, $wmon, $wmoff, $ipfqdn, $http, $wioscan, $statustxt, $status, $key, $ic, $text, $image ) = (); 

my ( @temp, @dates, @ipaddresses, @names, @remark, @sendemailon, @sendemailoff, @current, @ddns, @match, @webinterface, @arpcache, @arpadd, @line,
	 @hosts, @vpnstatus, @ovpnstatus, @activ, @dyndns, @pingmethode, @status, @id, @write, @log );

my @nosaved = ('ACTION','ID','CLIENTID','TIMESTAMP','IPADR','HOST','REMARK','DYNDNS','SENDEMAILON','SENDEMAILOFF','PINGMETHODE','ONLINE','WEBINTERFACE');

my @devs_color = ('GREEN','BLUE','ORANGE','RED');
my @devs_net   = ('green0','blue0','orange0','red0');
my @devs_img   = ('green.png','blue.png','orange.png','red.png');
my @devs_alt   = ('green','blue','orange','red');

my %ifacecolor = ( GREEN => 'wio_run_green', BLUE => 'wio_run_blue', ORANGE => 'wio_run_orange');

#if ( $netsettings{'RED_TYPE'} eq 'STATIC' || $netsettings{'RED_TYPE'} eq 'DHCP' ) {
#	%ifacecolor = ( %ifacecolor, RED => 'wio_run_red' );
#}

&loadips();

## some wio settings

$wiosettings{'ACTION'} = '';
$wiosettings{'COUNT'} = '';
$wiosettings{'ID'} = '';
$wiosettings{'CLIENTID'} = '';
$wiosettings{'SORT'} = 'IPADR';
$wiosettings{'HOST'} = '';
$wiosettings{'IPADR'} = '';
$wiosettings{'EN'} = 'on';
$wiosettings{'REMARK'} = '';
$wiosettings{'DYNDNS'} = '';
$wiosettings{'CLIENTREMARK'} = '';
$wiosettings{'SENDEMAILON'} = '';
$wiosettings{'SENDEMAILOFF'} = '';
$wiosettings{'PINGMETHODE'} = 'ip';
$wiosettings{'WEBINTERFACE'} = '----';
$wiosettings{'TIMEOUT'} = '1';
$wiosettings{'TIMESTAMP'} = '';
$wiosettings{'ONLINE'} = 'off';
$wiosettings{'CRON'} = '15';
$wiosettings{'OVPNCRON'} = '5';
$wiosettings{'ENABLE'} = 'off';
$wiosettings{'LOGGING'} = 'off';
$wiosettings{'MAILREMARK'} = 'off';
$wiosettings{'MAILSTYLE'} = 'email';
$wiosettings{'OVPNRWMAIL'} = 'off';
$wiosettings{'WIOGUISHOWARPTABLE'} = '';
$wiosettings{'WIOGUISHOWCLIENTIMPORTTABLE'} = '';
$wiosettings{'WIOGUISHOWNETWORKSEARCHTABLE'} = '';

&Header::getcgihash(\%wiosettings);
&Header::getcgihash(\%mainsettings);
&Header::getcgihash(\%mailsettings);
&Header::getcgihash(\%netsettings);

if ( $mailsettings{'USEMAIL'} eq 'on' ) { $wiosettings{'SENDEMAIL'} = 'on'; }
else { $wiosettings{'SENDEMAIL'} = 'off'; }

if ( -e $wiofile ) { goto WIOSCAN; }

## get network ips
foreach (@devs_color) {
	if ( $netsettings{"${_}_DEV"} ne '' ) {
		$wiosettings{"${_}_IPLOW"} = &Network::find_next_ip_address($netsettings{"${_}_NETADDRESS"}, 1);

		my $broadcast = &Network::get_broadcast($netsettings{"${_}_NETADDRESS"} . "/" . $netsettings{"${_}_NETMASK"});
		$wiosettings{"${_}_IPHIGH"} = &Network::find_next_ip_address($broadcast, -1);
	}
}

## save wio settings

if ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_save'}.'1' ) {
	unless ( `ps -A | grep wio.pl` ) {
		$cgiparams{'SORT'} = $wiosettings{'SORT'};
		$cgiparams{'CRON'} = $wiosettings{'CRON'};
		$cgiparams{'OVPNCRON'} = $wiosettings{'OVPNCRON'};
		$cgiparams{'ENABLE'} = $wiosettings{'ENABLE'};
		$cgiparams{'LOGGING'} = $wiosettings{'LOGGING'};
		$cgiparams{'TIMEOUT'} = $wiosettings{'TIMEOUT'};
		$cgiparams{'ACTION'} = $wiosettings{'ACTION'};
		$cgiparams{'CLIENTREMARK'} = $wiosettings{'CLIENTREMARK'};
		$cgiparams{'MAILREMARK'} = $wiosettings{'MAILREMARK'};
		$cgiparams{'MAILSTYLE'} = $wiosettings{'MAILSTYLE'};
		$cgiparams{'OVPNRWMAIL'} = $wiosettings{'OVPNRWMAIL'};

		&General::writehash($wiosettings, \%cgiparams);
		&General::readhash($wiosettings, \%wiosettings);

		if ( $wiosettings{'ENABLE'} eq 'off' ) {
			&WIO::clearfile($ipadrfile);
			unlink glob "$rrddir/*";
		}
	}
	else {
		$infomessage = "$Lang::tr{'wio_error_function'}";
	}
}

## save imported clients

if ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_save'}.'2' ) {
	unless ( `ps -A | grep wio.pl` ) {
		while ( $count < $wiosettings{'COUNT'} ) {
			if ( defined($wiosettings{"USE$count"}) && $wiosettings{"USE$count"} eq 'on' ) {
				$wiosettings{'CLIENTID'} = $wiosettings{"CLIENTID$count"};
				$wiosettings{'TIMESTAMP'} = $wiosettings{"TIMESTAMP$count"};
				$wiosettings{'IPADR'} = $wiosettings{"IPADR$count"};
				$wiosettings{'HOST'} = $wiosettings{"HOST$count"};
				$wiosettings{'EN'} = $wiosettings{"EN$count"};
				$wiosettings{'REMARK'} = $wiosettings{"REMARK$count"};
				$wiosettings{'DYNDNS'} = $wiosettings{"DYNDNS$count"};
				$wiosettings{'SENDEMAILON'} = $wiosettings{"SENDEMAILON$count"};
				$wiosettings{'SENDEMAILOFF'} = $wiosettings{"SENDEMAILOFF$count"};
				$wiosettings{'PINGMETHODE'} = $wiosettings{"PINGMETHODE$count"};
				$wiosettings{'ONLINE'} = $wiosettings{"ONLINE$count"};
				$wiosettings{'WEBINTERFACE'} = $wiosettings{"WEBINTERFACE$count"};

				&validSave();

				if ($errormessage) {
					open(FILE, ">> $editfile");
					print FILE "$wiosettings{'CLIENTID'},$wiosettings{'TIMESTAMP'},$wiosettings{'IPADR'},$wiosettings{'HOST'},$wiosettings{'EN'},$wiosettings{'REMARK'},$wiosettings{'DYNDNS'},$wiosettings{'SENDEMAILON'},$wiosettings{'SENDEMAILOFF'},$wiosettings{'PINGMETHODE'},$wiosettings{'ONLINE'},$wiosettings{'WEBINTERFACE'}\n";
					close(FILE);
					$importmessage = $errormessage;
				}
				else {
					$wiosettings{'CLIENTID'} = &General::findhasharraykey (\%ipshash);
					unshift (@current, "$wiosettings{'CLIENTID'},$wiosettings{'TIMESTAMP'},$wiosettings{'IPADR'},$wiosettings{'HOST'},$wiosettings{'EN'},$wiosettings{'REMARK'},$wiosettings{'DYNDNS'},$wiosettings{'SENDEMAILON'},$wiosettings{'SENDEMAILOFF'},$wiosettings{'PINGMETHODE'},$wiosettings{'ONLINE'},$wiosettings{'WEBINTERFACE'}\n");
					&SortDataFile('',@current);
				}
			}
			$count++;
		}

		map ($wiosettings{$_} = '' ,@nosaved);
		unlink ($importfile);
		if ( -e "$editfile" ) { goto EDIT; }
	}
	else {
		$infomessage = "$Lang::tr{'wio_error_function'}";
	}
}

## add or update client

if ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_client_add'} ) {
	unless ( `ps -A | grep wio.pl` ) {
		&validSave();

		unless ($errormessage) {
			if ( $wiosettings{'ID'} eq '' && $wiosettings{'ACTION'} ne $Lang::tr{'edit'} ) {
				$wiosettings{'CLIENTID'} = &General::findhasharraykey (\%ipshash);
				unshift (@current, "$wiosettings{'CLIENTID'},$wiosettings{'TIMESTAMP'},$wiosettings{'IPADR'},$wiosettings{'HOST'},$wiosettings{'EN'},$wiosettings{'REMARK'},$wiosettings{'DYNDNS'},$wiosettings{'SENDEMAILON'},$wiosettings{'SENDEMAILOFF'},$wiosettings{'PINGMETHODE'},$wiosettings{'ONLINE'},$wiosettings{'WEBINTERFACE'}\n");
			}
			else {
				@current[$wiosettings{'ID'}] = "$wiosettings{'CLIENTID'},$wiosettings{'TIMESTAMP'},$wiosettings{'IPADR'},$wiosettings{'HOST'},$wiosettings{'EN'},$wiosettings{'REMARK'},$wiosettings{'DYNDNS'},$wiosettings{'SENDEMAILON'},$wiosettings{'SENDEMAILOFF'},$wiosettings{'PINGMETHODE'},$wiosettings{'ONLINE'},$wiosettings{'WEBINTERFACE'}\n";
			}
		}
		else { goto ERROR; }

		map ($wiosettings{$_} = '' ,@nosaved);
		&SortDataFile('',@current);
	}
	else {
		$infomessage = "$Lang::tr{'wio_error_function'}";
	}
}

## show / hide arptable

if ( $wiosettings{'WIOGUISHOWARPTABLE'} eq 'arptable' ) {
	unless ( `ps -A | grep wio.pl` ) {
		if ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_show_table_off'} ) {
			$wiosettings{'WIOGUISHOWARPTABLE'} = 'off';
			$arpbuttontext = "$Lang::tr{'wio_show_table_on'}";
		}
		else {
			$wiosettings{'WIOGUISHOWARPTABLE'} = 'on';
			$arpbuttontext = "$Lang::tr{'wio_show_table_off'}";
		}
	}
	else {
		$infomessage = "$Lang::tr{'wio_error_function'}";
	}
}

## show / hide clientimporttable

if ( $wiosettings{'WIOGUISHOWCLIENTIMPORTTABLE'} eq 'clientimport' ) {
	unless ( `ps -A | grep wio.pl` ) {
		if ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_show_table_off'} ) {
			$wiosettings{'WIOGUISHOWCLIENTIMPORTTABLE'} = 'off';
			$clientimportbuttontext = "$Lang::tr{'wio_show_table_on'}";
		}
		else {
			$wiosettings{'WIOGUISHOWCLIENTIMPORTTABLE'} = 'on';
			$clientimportbuttontext = "$Lang::tr{'wio_show_table_off'}";
		}
	}
	else {
		$infomessage = "$Lang::tr{'wio_error_function'}";
	}
}

## show / hide networksearchtable

if ( $wiosettings{'WIOGUISHOWNETWORKSEARCHTABLE'} eq 'networksearch' ) {
	unless ( `ps -A | grep wio.pl` ) {
		if ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_show_table_off'} ) {
			$wiosettings{'WIOGUISHOWNETWORKSEARCHTABLE'} = 'off';
			$networksearchbuttontext = "$Lang::tr{'wio_show_table_on'}";
		}
		else {
			$wiosettings{'WIOGUISHOWNETWORKSEARCHTABLE'} = 'on';
			$networksearchbuttontext = "$Lang::tr{'wio_show_table_off'}";
		}
	}
	else {
		$infomessage = "$Lang::tr{'wio_error_function'}";
	}
}

## add arp client

if ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_add'} ) {
	unless ( `ps -A | grep wio.pl` ) {
		open(FILE, "$logdir/.arpcache");
		@arpadd = <FILE>;
		close (FILE);

		chomp(@arpadd[$wiosettings{'ID'}]);
		@temp = split (/\,/, @arpadd[$wiosettings{'ID'}]);

		$wiosettings{'CLIENTID'} = &General::findhasharraykey (\%ipshash);
		$wiosettings{'IPADR'} = $temp[1];
		$wiosettings{'HOST'} = $temp[2];
		$wiosettings{'EN'} = 'on';

		$wiosettings{'PINGMETHODE'} = 'ip';
		$wiosettings{'ONLINE'} = 'off';

		open(FILE, ">> $editfile");
		print FILE "$wiosettings{'CLIENTID'},$wiosettings{'TIMESTAMP'},$wiosettings{'IPADR'},$wiosettings{'HOST'},$wiosettings{'EN'},$wiosettings{'REMARK'},$wiosettings{'DYNDNS'},$wiosettings{'SENDEMAILON'},$wiosettings{'SENDEMAILOFF'},$wiosettings{'PINGMETHODE'},$wiosettings{'ONLINE'},$wiosettings{'WEBINTERFACE'}\n";
		close(FILE);

		goto EDIT;
	}
	else {
		undef($wiosettings{'ID'});
		$infomessage = "$Lang::tr{'wio_error_function'}";
	}
}

## enable / disable client || enable / disable dyndns || enable / disable sendemailon || enable / disable sendemailoff || change ip / fqdn

if ( $wiosettings{'ACTION'} eq $Lang::tr{'enable disable client'} ) { $edc = 'on'; }
if ( $wiosettings{'ACTION'} eq $Lang::tr{'enable disable dyndns'} ) { $edd = 'on'; }
if ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_mail_online'} ) { $wmon = 'on'; }
if ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_mail_offline'} ) { $wmoff = 'on'; }
if (( $wiosettings{'ACTION'} eq $Lang::tr{'wio_ip_on'} ) || ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_fqdn_on'} )) { $ipfqdn = 'on'; }

if ( defined($edc) || defined($edd) || defined($wmon) || defined($wmoff) || defined($ipfqdn) ) {
	unless ( `ps -A | grep wio.pl` ) {
		chomp(@current[$wiosettings{'ID'}]);
		@temp = split (/\,/, @current[$wiosettings{'ID'}]);

		if ( $edc eq 'on' ) {
			$temp[4] = $temp[4] ne '' ? '' : 'on';
			$temp[10] = '';
			$temp[11] = '';
			$temp[1] = '';
			unlink "$rrddir/$temp[0].rrd";
		}
		elsif ( $edd eq 'on' ) { $temp[6] = $temp[6] ne '' ? '' : 'on'; }
		elsif ( $wmon eq 'on' ) { $temp[7] = $temp[7] ne '' ? '' : 'on'; }
		elsif ( $wmoff eq 'on' ) { $temp[8] = $temp[8] ne '' ? '' : 'on'; }
		elsif ( $ipfqdn eq 'on' ) { $temp[9] = $temp[9] eq 'fqdn' ? 'ip' : 'fqdn'; }

		@current[$wiosettings{'ID'}] = join (',', @temp)."\n";
		undef($wiosettings{'ID'});

		&writeips();
	}
	else {
		undef($wiosettings{'ID'});
		$infomessage = "$Lang::tr{'wio_error_function'}";
	}
}

## refresh wio status || refresh single client status

if ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_refresh'} || $wiosettings{'ACTION'} eq $Lang::tr{'wio_sc_refresh'} ) {

unless ( `ps -A | grep wio.pl` ) {

	if ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_sc_refresh'} ) {
		open(FILE, "> $onoffip");
		print FILE @current[$wiosettings{'ID'}];
		close(FILE);

		undef($wiosettings{'ID'});
	}

&Header::showhttpheaders();
&Header::openpage($Lang::tr{'wio'}, 1, $refreshbox);
&Header::openbigbox('100%', 'left', '');
&Header::openbox('100%', 'left', $Lang::tr{'wio_info'});

print"
<table align='center' width='100%'>
	<tr><td align='center'>$Lang::tr{'wio_msg'}</td></tr>
	<tr><td>&nbsp;</td></tr>
	<tr><td align='center'><img align='middle' src='/images/indicator.gif' /></td></tr>
</table>
";

&Header::closebox();
&Header::closebigbox();
&Header::closepage();

while ( system("/usr/local/bin/wiohelper", "&") ) {}

exit 0;
}
else {
	$infomessage = "$Lang::tr{'wio_already_running'}";
	unlink($onoffip);
}

}

## refresh dyndns ip

if ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_dyndns_refresh'} ) {
	unless ( `ps -A | grep wio.pl` ) {
		chomp(@current[$wiosettings{'ID'}]);
		@temp = split (/\,/, @current[$wiosettings{'ID'}]);

		($temp[2], $infomessage) = &WIO::getdyndnsip($temp[2], $temp[3]);

		@current[$wiosettings{'ID'}] = join (',', @temp)."\n";

		&writeips();

		undef($wiosettings{'ID'});
	}
	else {
		$infomessage = "$Lang::tr{'wio_error_function'}";
	}
}

## edit client

if ( $wiosettings{'ACTION'} eq $Lang::tr{'edit'} ) {
	unless ( `ps -A | grep wio.pl` ) {
		chomp(@current[$wiosettings{'ID'}]);
		@temp = split (/\,/, @current[$wiosettings{'ID'}]);

		$wiosettings{'CLIENTID'} = $temp[0];
		$wiosettings{'TIMESTAMP'} = $temp[1];
		$wiosettings{'IPADR'} = $temp[2];
		$wiosettings{'HOST'} = $temp[3];
		$wiosettings{'EN'} = $temp[4];
		$wiosettings{'REMARK'} = $temp[5];
		$wiosettings{'DYNDNS'} = $temp[6];
		$wiosettings{'SENDEMAILON'} = $temp[7];
		$wiosettings{'SENDEMAILOFF'} = $temp[8];
		$wiosettings{'PINGMETHODE'} = $temp[9];
		$wiosettings{'ONLINE'} = $temp[10];
		$wiosettings{'WEBINTERFACE'} = $temp[11];
	}
	else {
		undef($wiosettings{'ACTION'});
		$infomessage = "$Lang::tr{'wio_error_function'}";
	}
}

## remove client

if ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_remove_client'} ) {
	unless ( `ps -A | grep wio.pl` ) {
		chomp(@current[$wiosettings{'ID'}]);

		@temp = split (/\,/, @current[$wiosettings{'ID'}]);

		unlink "$rrddir/$temp[0].rrd";

		splice (@current,$wiosettings{'ID'},1);

		&writeips();

		undef($wiosettings{'ID'});
	}
	else {
		undef($wiosettings{'ID'});
		$infomessage = "$Lang::tr{'wio_error_function'}";
	}
}

## remove all clients

if ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_remove_all'} ) {
	unless ( `ps -A | grep wio.pl` ) {
		&WIO::clearfile($ipadrfile);
		unlink glob "$rrddir/*";
		undef(@current);
	}
	else {
		$infomessage = "$Lang::tr{'wio_error_function'}";
	}
}

## back function

if ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_back'} ) {
	if ( -e "$importfile" ) { unlink ($importfile); }
	map ($wiosettings{$_} = '' ,@nosaved);
	undef($errormessage);
}

## import hosts, fixleases or csv file || scan networks (green/blue/orange)

if ( $wiosettings{'ACTION'} eq 'wio_run_green'  ||
	 $wiosettings{'ACTION'} eq 'wio_run_blue'   ||
	 $wiosettings{'ACTION'} eq 'wio_run_red'   ||
	 $wiosettings{'ACTION'} eq 'wio_run_orange') { $wioscan = 'on'; }

if ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_import'}.'1' ||
	 $wiosettings{'ACTION'} eq $Lang::tr{'wio_import'}.'2' ||
	 $wiosettings{'ACTION'} eq $Lang::tr{'wio_import'}.'3' ||
	 defined($wioscan) || defined($importmessage) ) {

unless ( `ps -A | grep wio.pl` ) {
	if ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_import'}.'1' && $importmessage eq '' ) {

		&Header::getcgihash(\%wiosettings, {'wantfile' => 1, 'filevar' => 'CSVFILE'});

		if ( $wiosettings{'CSVFILE'} eq '' ) {
			$errormessage = $Lang::tr{'wio_no_file_selected'};
			$message = 2; goto ERROR;
		}

		if ( $wiosettings{'CSVFILE'} =~ /[^a-z0-9A-Z\ \.\-\_\:\\]+/ ) {
			$errormessage = $Lang::tr{'wio_no_csv_error'};
			$message = 2; goto ERROR;
		}

		if ( !($wiosettings{'CSVFILE'} =~ /.csv$/) ) {
			$errormessage = $Lang::tr{'wio_no_csv'};
			$message = 2; goto ERROR;
		}

		if (copy($wiosettings{'CSVFILE'}, "$logdir/importfile") != 1) {
			$errormessage = $!;
			$message = 2; goto ERROR;
		}
	}

EDIT:

&General::readhash($wiosettings, \%wiosettings);

&Header::showhttpheaders();
&Header::openpage($Lang::tr{'wio'}, 1, '');
&Header::openbigbox('100%', 'left');

if ($importmessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'wio_error'}, 'error');
		print" <table width='100%'><tr><td><font class='base'>$importmessage</font></td></tr></table>";
	&Header::closebox();
}

if ( -e "$editfile" ) {
	open(FILE, "< $editfile" ); }
elsif ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_import'}.'1' ) {
	open(FILE, "< $importfile" ); }
elsif ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_import'}.'2' ) {
	open(FILE, "< $hostfile" ); }
elsif ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_import'}.'3' ) {
	open(FILE, "< $dhcpfile" ); }
elsif ( $wioscan eq 'on' ) {

	foreach (keys(%ifacecolor)) {
		if ( $netsettings{"${_}_DEV"} eq $wiosettings{'ID'} ) {
			$dev = $netsettings{"${_}_DEV"};
			$iprange = $wiosettings{"${_}_IPLOW"} . "-" . $wiosettings{"${_}_IPHIGH"};

			if ( $_ eq 'GREEN' ) { $color = "$Header::colourgreen"; $net = $Lang::tr{'wio_msg_green'}; }
			elsif ( $_ eq 'BLUE' ) { $color = "$Header::colourblue"; $net = $Lang::tr{'wio_msg_blue'}; }
			elsif ( $_ eq 'RED' ) { $color = "$Header::colourred"; $net = $Lang::tr{'wio_msg_red'}; }
			else { $color = "$Header::colourorange"; $net = $Lang::tr{'wio_msg_orange'}; }
		}
	}

&Header::openbox('100%', 'left', $Lang::tr{'wio_info'});
	print"<table width='100%'>
		  <tr><td align='center'><font class='base'>$Lang::tr{'wio_msg_left'} </font><font class='base' color='$color'><b>$net</b></font> $Lang::tr{'wio_msg_center'} <font class='base'> $Lang::tr{'wio_msg_right'} $Lang::tr{'wio_msg_hint'}</font></td></tr>
		  <tr><td>&nbsp;</td></tr>
		  <tr><td align='center'><img align='middle' src='/images/indicator.gif' /></td></tr>
		  </table>";
&Header::closebox();
&Header::closebigbox();

	open(FILE, "/usr/local/bin/wioscan -wsa $dev $iprange |" );

}

@hosts = <FILE>;
close(FILE);

if ( $wioscan ne 'on' && ! -e $wiofile ) { @hosts = sort @hosts; }
else {
	open(FILE, "> $wiofile");
	print FILE @hosts;
	close(FILE);

	print"<meta http-equiv=\"refresh\" content=\"0; URL=$ENV{'SCRIPT_NAME'}\">";
	exit 0;
}

WIOSCAN:

if ( -e $wiofile ) {
	open(FILE, "< $wiofile");
	@hosts = <FILE>;
	close (FILE);

	&General::readhash($wiosettings, \%wiosettings);

	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'wio'}, 1, '');
	&Header::openbigbox('100%', 'left');
}

foreach (@hosts) {
	chomp;

	@line = split (/\,/, $_);

	if ( -e $editfile || -e $importfile ) {
		$wiosettings{'CLIENTID$count'} = $line[0];
		$wiosettings{'TIMESTAMP$count'} = $line[1];
		$wiosettings{'IPADR$count'} = $line[2];
		$wiosettings{'HOST$count'} = $line[3];
		$wiosettings{'EN$count'} = $line[4];
		$wiosettings{'REMARK$count'} = $line[5];
		$wiosettings{'DYNDNS$count'} = $line[6];
		$wiosettings{'SENDEMAILON$count'} = $line[7];
		$wiosettings{'SENDEMAILOFF$count'} = $line[8];
		$wiosettings{'PINGMETHODE$count'} = $line[9];
		$wiosettings{'ONLINE$count'} = $line[10];
		$wiosettings{'WEBINTERFACE$count'} = $line[11];
		$wiosettings{'USE$count'} = 'on';
	}
	else {
		$wiosettings{'IPADR$count'} = $line[1];
		$wiosettings{'EN$count'} = 'on';
		$wiosettings{'PINGMETHODE$count'} = 'ip';
		$wiosettings{'USE$count'} = 'on';

		if ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_import'}.'2' ) {
			$wiosettings{'HOST$count'} = $line[2];
			$wiosettings{'DOM$count'} = $line[3];
			$wiosettings{'REMARK$count'} = '';
		}
		elsif ( $wioscan eq 'on' || -e $wiofile ) {
			$wiosettings{'HOST$count'} = gethostbyaddr(inet_aton($line[1]), AF_INET);
			if ($wiosettings{'HOST$count'} eq '') { $wiosettings{'HOST$count'} = $line[1]; }
			$wiosettings{'REMARK$count'} = '';
		}
		else {
			$wiosettings{'HOST$count'} = $line[7];
			$wiosettings{'REMARK$count'} = $line[6];
		}
	}

	$checked{'EN$count'}{'on'} = ($wiosettings{'EN$count'} eq '' ) ? '' : "checked='checked'";

	$checked{'DYNDNS$count'}{'on'} = ($wiosettings{'DYNDNS$count'} eq '' ) ? '' : "checked='checked'";
	$checked{'SENDEMAILON$count'}{'on'} = ($wiosettings{'SENDEMAILON$count'} eq '' ) ? '' : "checked='checked'";
	$checked{'SENDEMAILOFF$count'}{'on'} = ($wiosettings{'SENDEMAILOFF$count'} eq '' ) ? '' : "checked='checked'";

	$checked{'PINGMETHODE$count'}{'ip'} = $checked{'PINGMETHODE$count'}{'fqdn'} = '';
	$checked{'PINGMETHODE$count'}{$wiosettings{'PINGMETHODE$count'}} = "checked='checked'";

	$checked{'USE$count'}{'on'} = ($wiosettings{'USE$count'} eq '' ) ? '' : "checked='checked'";
	
	$selected{'WEBINTERFACE$count'}{'----'} = '';
	$selected{'WEBINTERFACE$count'}{'HTTP'} = '';
	$selected{'WEBINTERFACE$count'}{'HTTPS'} = '';
	$selected{'WEBINTERFACE$count'}{$wiosettings{'WEBINTERFACE$count'}} = "selected='selected'";

if (! &WIO::checkinto($wiosettings{'IPADR$count'}, $wiosettings{'HOST$count'}, @current) ) {

if ( $importmessage ) {
	&Header::openbox('100%', 'left', "$Lang::tr{'wio_import_data'}'$wiosettings{'HOST$count'}'$Lang::tr{'wio_import_data1'}");
} 
elsif ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_import'}.'1' || $wioscan eq 'on' || -e $wiofile || -e $editfile ) {
	&Header::openbox('100%', 'left', "$Lang::tr{'wio_import_data'}'$wiosettings{'HOST$count'}'$Lang::tr{'wio_import_data2'}");
}
elsif ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_import'}.'2' ) {
	&Header::openbox('100%', 'left', "$Lang::tr{'wio_import_data'}'$wiosettings{'HOST$count'}.$wiosettings{'DOM$count'}'$Lang::tr{'wio_import_data2'}");
}
else {
	&Header::openbox('100%', 'left', $Lang::tr{'wio_import_leases'});
}

print"
<form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>
<input type='hidden' name='ONLINE$count' value='$wiosettings{'ONLINE$count'}' />

<table width='100%'>
<tr>
	<td>$Lang::tr{'wio_use'}</td>
	<td><input type='checkbox' name='USE$count' $checked{'USE$count'}{'on'} /></td>
</tr>
<tr>
	<td>$Lang::tr{'wio_client_enable'}</td>
	<td><input type='checkbox' name='EN$count' $checked{'EN$count'}{'on'} /></td>
</tr>
<tr>
	<td>$Lang::tr{'host ip'}:</td>
	<td><input type='text' name='IPADR$count' value='$wiosettings{'IPADR$count'}' size='18' /></td>
	<td>$Lang::tr{'hostname'}:</td>
";

if ( $wiosettings{'ACTION'} eq $Lang::tr{'wio_import'}.'2' ) {
	print"<td><input type='text' name='HOST$count' size='18' value='$wiosettings{'HOST$count'}.$wiosettings{'DOM$count'}' /></td>";
}
else {
	print"<td><input type='text' name='HOST$count' size='18' value='$wiosettings{'HOST$count'}' /></td>";
}

print"
	<td>$Lang::tr{'remark'}:</td>
	<td><input type='text' name='REMARK$count' value='$wiosettings{'REMARK$count'}' size='18' /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'wio_ping_send'}:</td>
	<td align='left'><input type='radio' name='PINGMETHODE$count' value='ip' $checked{'PINGMETHODE$count'}{'ip'} />&nbsp;IP&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type='radio' name='PINGMETHODE$count' value='fqdn' $checked{'PINGMETHODE$count'}{'fqdn'} />&nbsp;FQDN</td>
	<td>$Lang::tr{'wio_dyndns'}:</td>
	<td><input type='checkbox' name='DYNDNS$count' $checked{'DYNDNS$count'}{'on'} /></td>
";

if ( $wiosettings{'SENDEMAIL'} eq 'on' ) {
	print"<td>$Lang::tr{'wio_sendemail'}:</td>
		  <td><input type='checkbox' name='SENDEMAILON$count' $checked{'SENDEMAILON$count'}{'on'} />&nbsp;$Lang::tr{'wio_online'}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type='checkbox' name='SENDEMAILOFF$count' $checked{'SENDEMAILOFF$count'}{'on'} />&nbsp;$Lang::tr{'wio_offline'}</td>";
}
else {
	print"<td colspan='2'>&nbsp;</td>";
}

print"
</tr>
<tr>
	<td height='30'>$Lang::tr{'wio_link_open'}:</td>
	<td align='left' colspan='5'>
		<select size='1' name='WEBINTERFACE$count' width='80' style='width: 80px'>
		<option value='----' $selected{'WEBINTERFACE$count'}{'----'}>----</option>
		<option value='HTTP' $selected{'WEBINTERFACE$count'}{'HTTP'}>HTTP</option>
		<option value='HTTPS' $selected{'WEBINTERFACE$count'}{'HTTPS'}>HTTPS</option>
		</select>
	</td>
</tr>
</table>
";

&Header::closebox();
$showcount++;
}
$count++;
}

if ( $showcount gt 0 ) {
&Header::openbox('100%', 'left', $Lang::tr{'wio_import_infos'});

print"
<table width='100%'>
<tr>
";

if ($importmessage) { print"<td>&nbsp;</td>"; }
else { print"<td><font color='$color{'color11'}'>$Lang::tr{'wio_import_infos_csv'}</font></td>"; }

print"
</tr>
<tr><td colspan='4'>&nbsp;</td></tr>
</table>
<table width='100%'>
<tr>
	<td width='25%'>&nbsp;</td>
	<td width='25%'><input type='hidden' name='COUNT' value='$count' /><input type='hidden' name='ACTION' value='$Lang::tr{'wio_save'}2' /><input type='submit' name='SUBMIT' value='$Lang::tr{'wio_save'}' /></form></td>
	<td width='25%'><form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'><input type='submit' name='ACTION' value='$Lang::tr{'wio_back'}' /></form></td>
	<td width='25%'>&nbsp;</td>
</tr>
</table>
";

&Header::closebox();
&Header::closebigbox();
&Header::closepage();
}
else {
	print"<meta http-equiv=\"refresh\" content=\"0; URL=$ENV{'SCRIPT_NAME'}?INFO\">";
}

if ( -e "$editfile" ) { unlink ($editfile); }
if ( -e "$wiofile" ) { unlink($wiofile); }
exit 0;
}
else {
	$infomessage = "$Lang::tr{'wio_error_function'}";
}
}

## skript function

if ($ENV{'QUERY_STRING'} =~ /$sortstring/ ) {
	my $string = $ENV{'QUERY_STRING'};

	if ( $string eq 'INFO' ) {
		$infomessage = $Lang::tr{'wio_import_info_csv'};
	}
	else {
		&General::readhash($wiosettings, \%wiosettings);

		my $actual = $wiosettings{'SORT'};

		if ($actual =~ $string) {
			my $Rev = '';
			if ($actual !~ 'Rev') { $Rev = 'Rev'; }
			$string.=$Rev;
		}

		system("/bin/sed -i 's#$wiosettings{'SORT'}#$string#g' $wiosettings");

		$wiosettings{'SORT'} = $string;
		map ($wiosettings{$_} = '' ,@nosaved);
		&SortDataFile('',@current);
	}
}

## main part

ERROR:

unless($message == 1) { &General::readhash($wiosettings, \%wiosettings); }

for ($i=5; $i<=60; $i+=5) { $selected{'CRON'}{$i} = ''; }

$selected{'CRON'}{$wiosettings{'CRON'}} = "selected='selected'";
	
for ($i=1; $i<=15; $i++) {
	$selected{'TIMEOUT'}{$i} = '';
	$selected{'OVPNCRON'}{$i} = '';
}

$selected{'TIMEOUT'}{$wiosettings{'TIMEOUT'}} = "selected='selected'";
$selected{'OVPNCRON'}{$wiosettings{'OVPNCRON'}} = "selected='selected'";

$checked{'ENABLE'}{'off'} = $checked{'ENABLE'}{'on'} = '';
$checked{'ENABLE'}{$wiosettings{'ENABLE'}} = "checked='checked'";

$checked{'LOGGING'}{'off'} = $checked{'LOGGING'}{'on'} = '';
$checked{'LOGGING'}{$wiosettings{'LOGGING'}} = "checked='checked'";

$checked{'CLIENTREMARK'}{'off'} = $checked{'CLIENTREMARK'}{'on'} = '';
$checked{'CLIENTREMARK'}{$wiosettings{'CLIENTREMARK'}} = "checked='checked'";

$checked{'MAILREMARK'}{'off'} = $checked{'MAILREMARK'}{'on'} = '';
$checked{'MAILREMARK'}{$wiosettings{'MAILREMARK'}} = "checked='checked'";

$checked{'OVPNRWMAIL'}{'off'} = $checked{'OVPNRWMAIL'}{'on'} = '';
$checked{'OVPNRWMAIL'}{$wiosettings{'OVPNRWMAIL'}} = "checked='checked'";

$checked{'MAILSTYLE'}{'smail'} = $checked{'MAILSTYLE'}{'email'} = '';
$checked{'MAILSTYLE'}{$wiosettings{'MAILSTYLE'}} = "checked='checked'";

&Header::showhttpheaders();
&Header::openpage($Lang::tr{'wio'}, 1, "<meta http-equiv='expires' content='-1'><meta http-equiv='cache-control' content='no-store, no-cache, must-revalidate'><meta http-equiv='pragma' content='no-cache'>");
&Header::openbigbox('100%', 'left', '');

## DEBUG / ERROR / INFO / UPDATE

if ( $debug ) {
	&Header::openbox('100%', 'left', 'DEBUG', 'warning');

		print"errormessage: $errormessage<br />\n";
		print"infomessage: $infomessage<br />\n";

		&hrline();

		my $wiodebug = 0;
		foreach (sort keys %wiosettings) {
			print"$_ = $wiosettings{$_}<br />\n";
			$wiodebug++;
		}

		&hrline();

		my $netdebug = 0;
		foreach (sort keys %netsettings) {
			print"$_ = $netsettings{$_}<br />\n";
			$netdebug++;
		}
	&Header::closebox();
}

if ( $errormessage ) {
	&Header::openbox('100%', 'left', $Lang::tr{'wio_error'}, 'error');
		print"<table width='100%'><tr><td><font class='base'><b>$errormessage</b></font></td></tr></table>";
	&Header::closebox();
}

if ( $infomessage ) {
	&Header::openbox('100%', 'left', $Lang::tr{'wio_info'}, 'warning');
		print"<table width='100%'><tr><td><font class='base'><b>$infomessage</b></font></td></tr></table>";
	&Header::closebox();
}

## wio configuration

if ( $wiosettings{'ACTION'} eq $Lang::tr{'edit'}.'1' || $message == 1 || $wiosettings{'ENABLE'} eq 'off' ) {

&Header::openbox('100%', 'left', $Lang::tr{'wio settings'});

print"
<form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>
<table width='100%'>
<tr>
	<td bgcolor='$color{'color20'}' align='left'><b>$Lang::tr{'wio_settings_msg_hint'}</b></td>
	<td colspan='2'>&nbsp;</td>
</tr>
<tr>
	<td width='48%'>&nbsp;</td>
	<td width='2%'>&nbsp;</td>
	<td width='50%'>&nbsp;</td>
</tr>
<tr>
	<td align='right'>$Lang::tr{'wio enabled'}</td>
";

print"<td>&nbsp;</td>";

if ( $wiosettings{'ENABLE'} eq 'on' ) {
	print"<td align='left'><input type='checkbox' onClick=\"return confirm('$Lang::tr{'wio_disable_hint'}')\" name='ENABLE' $checked{'ENABLE'}{'on'} /></td>";
}
else {
	print"<td align='left'><input type='checkbox' name='ENABLE' $checked{'ENABLE'}{'on'} /></td>";
}
print"
</tr>
<tr><td colspan='3'>&nbsp;</td></tr>
<tr>
	<td align='right'>$Lang::tr{'wio cron'}</td>
	<td>&nbsp;</td>
	<td align='left'><select size='1' name='CRON' size='5'>
";

for ($i=5; $i<=60; $i+=5) {
	$_ = sprintf("%02s",$i);
	print "<option $selected{'CRON'}{$_}>$_</option>\n";
}

print"
	</select>&nbsp;$Lang::tr{'wio min'}</td>
</tr>
<tr><td colspan='3'>&nbsp;</td></tr>
<tr>
	<td align='right'>$Lang::tr{'wio timeout'}</td>
	<td>&nbsp;</td>
	<td align='left'><select size='1' name='TIMEOUT' size='5'>
";

for ($i=1; $i<=15; $i++) {
	$_ = sprintf("%02s",$i);
	print "<option $selected{'TIMEOUT'}{$_}>$_</option>\n";
}

print"
	</select>&nbsp;$Lang::tr{'wio sec'}</td>
</tr>
<tr><td colspan='3'>&nbsp;</td></tr>
<tr>
	<td align='right'>$Lang::tr{'wio_logging'}</td>
	<td>&nbsp;</td>
	<td align='left'><input type='checkbox' name='LOGGING' $checked{'LOGGING'}{'on'} /></td>
</tr>
<tr><td colspan='3'>&nbsp;</td></tr>
<tr>
	<td align='right'>$Lang::tr{'wio_clientremark'}</td>
	<td>&nbsp;</td>
	<td align='left'><input type='checkbox' name='CLIENTREMARK' $checked{'CLIENTREMARK'}{'on'} /></td>
</tr>
<tr><td colspan='3'>&nbsp;</td></tr>
";

if ( $wiosettings{'SENDEMAIL'} eq 'on' ) {
print"
<tr>
	<td align='right'>$Lang::tr{'wio_mail_style'}:</td>
	<td>&nbsp;</td>
	<td align='left'><input type='radio' name='MAILSTYLE' value='smail' $checked{'MAILSTYLE'}{'smail'} />&nbsp;$Lang::tr{'wio_mail_smail'}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type='radio' name='MAILSTYLE' value='email' $checked{'MAILSTYLE'}{'email'} />&nbsp;$Lang::tr{'wio_mail_email'}</td>
</tr>
<tr><td colspan='3'>&nbsp;</td></tr>
<tr>
	<td align='right'>$Lang::tr{'wio_mailremark_enabled'}</td>
	<td>&nbsp;</td>
	<td align='left'><input type='checkbox' name='MAILREMARK' $checked{'MAILREMARK'}{'on'}></td>
</tr>
<tr><td colspan='3'>&nbsp;</td></tr>
";
}
if ( -e "$ovpnaddon" || ! -z "/var/ipfire/vpn/config" ) {
print"
<tr>
	<td align='right'>$Lang::tr{'wio_mail_ovpnrw'}</td>
	<td>&nbsp;</td>
	<td align='left'><input type='checkbox' name='OVPNRWMAIL' $checked{'OVPNRWMAIL'}{'on'}></td>
</tr>
<tr><td colspan='3'>&nbsp;</td></tr>
<tr>
	<td align='right'>$Lang::tr{'wio_ovpn_cron'}</td>
	<td>&nbsp;</td>
	<td align='left'><select size='1' name='OVPNCRON' size='5'>
";

for ($i=1; $i<=15; $i++) {
	$_ = sprintf("%02s",$i);
	print "<option $selected{'OVPNCRON'}{$_}>$_</option>\n";
}

print"
	</select>&nbsp;$Lang::tr{'wio min'}</td>
</tr>
<tr><td colspan='3'>&nbsp;</td></tr>
";
}
print"
<tr><td colspan='3'>&nbsp;</td></tr>
<tr>
	<td colspan='2'>&nbsp;</td>
	<td align='left'><input type='hidden' name='ACTION' value='$Lang::tr{'wio_save'}1' /><input type='submit' name='submit' value='$Lang::tr{'wio_save'}' />"
	.($wiosettings{'ENABLE'} ne 'off' ? "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type='button' onClick='location.href=\"/cgi-bin/wio.cgi\"' value='$Lang::tr{'wio_back'}'>" : "")
	."</td>
</tr>
</table>
</form>
";

&Header::closebox();
&Header::closebigbox();
&Header::closepage();
exit 0;
}

## wio client status

if ( $wiosettings{'ENABLE'} eq 'on') {
	if ( !$errormessage && $wiosettings{'ACTION'} ne $Lang::tr{'edit'} || $message == 2 ) {
		&Header::openbox('100%', 'left', $Lang::tr{'wio stat'});

		foreach (@current) {
			chomp;

			($id,$timestamp,$ipadr,$host,$on,$remark,$dyndns,$sendemailon,$sendemailoff,$pingmethode,$online,$webinterface) = split (/\,/, $_);

			if ( defined($dyndns) && ( $dyndns =~ 'on' ) ) {
				($dyndnsip, $infomessage) = &WIO::getdyndnsip($ipadr, $host);

				if ( $dyndnsip ne $ipadr  ) {
					$ipadr = $dyndnsip;
					$write = 'on';
				}
			}

			push (@id,($id));

			if ( $on eq 'on' ) { push (@dates,($timestamp)); }
			else { push (@dates,('-')); }

			push (@ipaddresses,($ipadr));
			push (@names,($host));
			push (@activ,($on));
			push (@remark,($remark));
			push (@dyndns,($dyndns));
			push (@sendemailon,($sendemailon));
			push (@sendemailoff,($sendemailoff));
			push (@pingmethode,($pingmethode));
			push (@status,($online));
			push (@webinterface,($webinterface));

			push (@write, "$id,$timestamp,$ipadr,$host,$on,$remark,$dyndns,$sendemailon,$sendemailoff,$pingmethode,$online,$webinterface\n");

			$nr++;
		}

		if ( defined($write) ) { &writeips(); }

## wan connection

print"
<table border='0' width='100%' bordercolor='$Header::bordercolour' cellspacing='0' cellpadding='0' style='border-collapse: collapse'>
<tr height='25'>
	<td width='33%' bgcolor='$color{'color20'}' align='left'><b>&nbsp;$Lang::tr{'wio_wan_con'}</b></td>
	<td width='67%' align='right'>&nbsp;</td>
</tr>
<tr><td colspan='2'>&nbsp;</td></tr>
</table>

<table border='0' width='100%' bordercolor='$Header::bordercolour' cellspacing='0' cellpadding='0' style='border-collapse: collapse'>
<tr bgcolor='$color{'color20'}' height='20'>
	<td width='3%' align='center'><b>$Lang::tr{'wio_id'}</b></td>
	<td width='15%' align='center'><b>$Lang::tr{'wio ipadress'}</b></td>
	<td width='7%' align='center'><b>$Lang::tr{'wio network'}</b></td>
	<td width='15%' align='center'><b>$Lang::tr{'wio_lanname'}</b></td>
	<td width='15%' align='center'><b>$Lang::tr{'wio_wanname'}</b></td>
	<td width='20%' align='center'><b>$Lang::tr{'wio_dyndns_hosts'}</b></td>
	<td width='11%' align='center'><b>$Lang::tr{'wio image'}</b></td>
	<td width='14%' align='center'><b>$Lang::tr{'wio_connected'}</b></td>
</tr>
<tr bgcolor='$color{'color22'}' height='20'>
	<td align='center'>01</td>
	<td align='center'><font color='$Header::colourred'>$redip</font></td>
	<td align='center'><img align='middle' src='$imgstatic/red.png' alt='$Lang::tr{'internet'}' title='$Lang::tr{'internet'}' /></td>
	<td align='center'><font color='$Header::colourgreen'>".$mainsettings{'HOSTNAME'}.".".$mainsettings{'DOMAINNAME'}."</font></td>
	<td align='center'><font color='$Header::colourred'>".( $redip ne '-' ? (gethostbyaddr(pack("C4", split (/\./, $redip)), 2))[0] : '-' )."</font></td>
	<td align='center'>
";

if ( -s "$dyndnsconfig" ) {

open(FILE, "< $dyndnsconfig");
@ddns = <FILE>;
close (FILE);

	foreach (@ddns) {
		chomp;

		@temp = split (/\,/, $_);

		if ( $temp[7] eq "on" ) {
			$bgcolor = ( &General::DyndnsServiceSync (&General::GetDyndnsRedIP,$temp[1],$temp[2]) ? "$Header::colourgreen" : "$Header::colourred" );
		}
		else {
			$bgcolor = "blue";
		}

		print"<font color='$bgcolor'>$temp[1].$temp[2]</font>";
		if ( $iddyndns++ ne (@ddns-1) ) { print"<br />\n"; }
	}
}
else {
	print"-";
}

print"
	</td>
	<td align='center'>
		<table bgcolor='".( -e $redactive ? "${Header::colourgreen}" : "${Header::colourred}" )."' cellpadding='2' cellspacing='0' width='100%'>
			<tr height='20'>
				<td align='center'><font color='white'><b>".( -e $redactive ? $Lang::tr{'wio_wan_up'} : $Lang::tr{'wio_wan_down'} )."</b></font></td>
			</tr>
		</table>
	</td>
	<td align='center'><font color='$Header::colourred'>".( -e "$redactive" ? &General::age("$redactive") : '-' )."</font></td>
</tr>
<tr height='1'><td colspan='9' bgcolor='#696565'></td></tr>
</table>
";

&hrline();

## vpn connection(s)

if ( -e "$vpnpid" ) {

@vpnstatus = `/usr/local/bin/ipsecctrl I`;

print"
<table border='0' width='100%' bordercolor='$Header::bordercolour' cellspacing='0' cellpadding='0' style='border-collapse: collapse'>
<tr height='25'>
	<td width='33%' bgcolor='$color{'color20'}' align='left'><b>&nbsp;$Lang::tr{'wio_vpn_con'}</b></td>
	<td width='67%'>&nbsp;</td>
</tr>
<tr><td colspan='2'>&nbsp;</td></tr>
</table>
<table border='0' width='100%' bordercolor='$Header::bordercolour' cellspacing='0' cellpadding='0' style='border-collapse: collapse'>
<tr bgcolor='$color{'color20'}' height='20'>
	<td width='3%' align='center'><b>$Lang::tr{'wio_id'}</b></td>
	<td width='19%' align='center'><b>$Lang::tr{'wio checked'}</b></td>
	<td width='20%' align='center'><b>$Lang::tr{'name'}</b></td>
	<td width='8%' align='center'><b>$Lang::tr{'type'}</b></td>
	<td width='25%' align='center'><b>$Lang::tr{'wio_common_name'}</b></td>
	<td width='11%' align='center'><b>$Lang::tr{'wio image'}</b></td>
	<td width='14%' align='center'><b>$Lang::tr{'wio_connected'}</b></td>
</tr>
";

foreach $key (sort SortByTunnelName (keys(%vpnconfighash))) {

my ( $vpnclient, $vpnclientip, $vpnrwnet, $vpnn2nnet, $vpntime, $vpncheck ) = '';

$status = "bgcolor='${Header::colourred}'";
$statustxt = "$Lang::tr{'capsclosed'}";
$vpnclient = $vpnconfighash{$key}[1];

my ($ip,$sub) = split(/\//,$vpnsettings{'RW_NET'});
my @ip = split( /\./, $ip);
$vpnrwnet = join( '.', ( $ip[0], $ip[1], $ip[2], ) );

	if ($vpnconfighash{$key}[0] eq 'off') {
		$status = "bgcolor='${Header::colourblue}'";
		$statustxt = "$Lang::tr{'capsclosed'}";
		$vpnn2nnet = '-';
	}
	else {
		$vpnn2nnet = $vpnconfighash{$key}[11];
	}

	foreach (@vpnstatus) {
		if ($_ =~ /$vpnclient.*ESTABLISHED/) {
			$status = "bgcolor='${Header::colourgreen}'";
			$statustxt = "$Lang::tr{'capsopen'}";
			$vpntime = `/usr/local/bin/ipsecctrl I | grep $vpnclient.*ESTABLISHED | sed 's/^[ \t]*//' | cut -d " " -f 3-4`;
			$vpntime = &WIO::contime($vpntime, "ipsec");
			$vpnclientip = `/usr/local/bin/ipsecctrl I | grep $vpnclient.*$vpnrwnet | sed 's/^[ \t]*//' | cut -d " " -f 6 | cut -d "/" -f 1`;
			$vpncheck = strftime("%d.%m.%Y - %H:%M:%S",localtime);
			last;
		}
	}

	print"<tr".($idvpn % 2?" bgcolor='$color{'color20'}'":" bgcolor='$color{'color22'}'")." height='20'>";

	my $vpnnr = $idvpn+1;

	printf ("<td align='center'>%02d</td>", $vpnnr);

	print"<td align='center'>".($vpncheck ne '' ? "$vpncheck" : "-")."</td>
		  <td align='center'>$vpnclient</td>
		  <td align='center'><img align='middle' src='$imgstatic/".($vpnconfighash{$key}[3] eq 'host' ? "vpnrw.png' alt='$Lang::tr{'wio_rw'}' title='$Lang::tr{'wio_rw'}'" : "vpnn2n.png' alt='$Lang::tr{'wio_n2n'}' title='$Lang::tr{'wio_n2n'}'")." /></td>
		  <td align='center'>".($vpnconfighash{$key}[3] eq 'host' ? (defined($vpnclientip) ? "$vpnclientip" : "-") : $vpnconfighash{$key}[3] eq 'net' ? "$vpnn2nnet" : "-")."</td>
		  <td align='center'>
		  	<table $status cellpadding='2' cellspacing='0' width='100%'>
		  		<tr height='20'>
		  			<td align='center'><font color='white'><b>$statustxt</b></font></td>
		  		</tr>
		  	</table>
		  </td>
		  <td align='center' height='20'>".($vpntime ne '' ? "$vpntime" : "-")."</td>
		  </tr>
";

if ($wiosettings{'CLIENTREMARK'} eq 'on') {
	print"<tr".($idvpn % 2?" bgcolor='$color{'color20'}'":" bgcolor='$color{'color22'}'")." height='20'><td>&nbsp;</td><td colspan='16' align='left'>".($vpnconfighash{$key}[25] ne '' ? "$vpnconfighash{$key}[25]" : "-")."</td></tr>";
}

print"<tr height='1'><td colspan='7' bgcolor='#696565'></td></tr>";
$idvpn++
}

print"</table>";
&hrline();
}

## openvpn connection(s)

if ( -e "$ovpnpid" ) {

@ovpnstatus = `cat /var/run/ovpnserver.log`;

print"
<table border='0' width='100%' bordercolor='$Header::bordercolour' cellspacing='0' cellpadding='0' style='border-collapse: collapse'>
<tr height='25'>
	<td width='33%' bgcolor='$color{'color20'}' align='left'><b>&nbsp;$Lang::tr{'wio_ovpn_con'}</b></td>
	<td width='67%'>&nbsp;</td>
</tr>
<tr><td colspan='2'>&nbsp;</td></tr>
</table>
<table border='0' width='100%' bordercolor='$Header::bordercolour' cellspacing='0' cellpadding='0' style='border-collapse: collapse'>
<tr bgcolor='$color{'color20'}' height='20'>
	<td width='3%' align='center'><b>$Lang::tr{'wio_id'}</b></td>
	<td width='19%' align='center'><b>$Lang::tr{'wio checked'}</b></td>
	<td width='20%' align='center'><b>$Lang::tr{'name'}</b></td>
	<td width='8%' align='center'><b>$Lang::tr{'type'}</b></td>
	<td width='25%' align='center'><b>$Lang::tr{'wio_common_name'}</b></td>
	<td width='11%' align='center'><b>$Lang::tr{'wio image'}</b></td>
	<td width='14%' align='center'><b>$Lang::tr{'wio_connected'}</b></td>
</tr>
";

foreach $key (keys %ovpnconfighash) {

	my ( $ovpncheck, $ovpntime, $ovpnclt, $ovpnrwip ) = '';

	print"<tr".($idovpn % 2?" bgcolor='$color{'color20'}'":" bgcolor='$color{'color22'}'")." height='20'>";

	my $ovpnnr = $idovpn+1;

	printf ("<td align='center' height='20'> %02d</td>", $ovpnnr);

	if ($ovpnconfighash{$key}[3] eq 'net') {
		$image = "$imgstatic/ovpnn2n.png";
		$text = "$Lang::tr{'wio_n2n'}";
	}
	else {
		$image = "$imgstatic/ovpnrw.png";
		$text = "$Lang::tr{'wio_rw'}";
	}

	if ( $ovpnconfighash{$key}[0] eq 'off' ) {
		$status = "${Header::colourblue}";
		$statustxt = "$Lang::tr{'capsclosed'}";
		$ovpncheck = "-";
	}
	else {
		if ($ovpnconfighash{$key}[3] eq 'net') {
			if (-e "/var/run/$ovpnconfighash{$key}[1]n2n.pid") {
				my ( @output, @tustate ) = '';
				my $tport = $ovpnconfighash{$key}[22];
				my $tnet = new Net::Telnet ( Timeout=>5, Errmode=>'return', Port=>$tport);
				if ($tport ne '') {
					$tnet->open('127.0.0.1');
					@output = $tnet->cmd(String => 'state', Prompt => '/(END.*\n|ERROR:.*\n)/');
					@tustate = split(/\,/, $output[1]);
					$ovpntime = &WIO::contime(scalar localtime($tustate[0]), "ovpn");
					$ovpncheck = strftime("%d.%m.%Y - %H:%M:%S", localtime);

					if (($tustate[1] eq 'CONNECTED')) {
						$status = "${Header::colourgreen}";
						$statustxt = "$Lang::tr{'capsopen'}";
						$ovpnrwip = $ovpnconfighash{$key}[11];
					}
					else {
						$status = "${Header::colourred}";
						$statustxt = "$tustate[1]";
					}
				}
			}
		}
		else {
			foreach (@ovpnstatus) {
				if ( $_ =~ /^(.+),(\d+\.\d+\.\d+\.\d+\:\d+),(\d+),(\d+),(.+)/ ) {
					@match = split (m/^(.+),(\d+\.\d+\.\d+\.\d+\:\d+),(\d+),(\d+),(.+)/, $_);
					$match[1] =~ s/[_]/ /g;
				}

				if ( $match[1] ne "Common Name" && ($match[1] eq $ovpnconfighash{$key}[2]) ) {
					$ovpnclt = $match[1];
					$ovpntime = &WIO::contime($match[5], "ovpn");
				}

				if ( $_ =~ /^(\d+\.\d+\.\d+\.\d+),(.+),(\d+\.\d+\.\d+\.\d+\:\d+),(.+)/ ) {
					@match = split(m/^(\d+\.\d+\.\d+\.\d+),(.+),(\d+\.\d+\.\d+\.\d+\:\d+),(.+)/, $_);
				}

				if ( $match[1] ne "Virtual Address" && $match[2] eq $ovpnclt ) {
					$ovpnrwip = $match[1];
					$ovpncheck = &WIO::statustime($match[4]);
				}

				if ( $ovpnclt eq $ovpnconfighash{$key}[2] ) {
					$status = "${Header::colourgreen}";
					$statustxt = "$Lang::tr{'capsopen'}";
				}
				else {
					$status = "${Header::colourred}";
					$statustxt = "$Lang::tr{'capsclosed'}";
				}
			}
		}
	}

print"
	<td align='center'>".(defined($ovpncheck) ? "$ovpncheck" : "-")."</td>
	<td align='center'>".($ovpnconfighash{$key}[2] eq '%auth-dn' ? "$ovpnconfighash{$key}[9]" : ($ovpnconfighash{$key}[4] eq 'cert' ? "$ovpnconfighash{$key}[1]": "-"))."</td>
	<td align='center'><img align='middle' src='$image' alt='$text' title='$text' /></td>
	<td align='center'>".($ovpnrwip ne '' ? "$ovpnrwip" : "-")."</td>
	<td align='center'><table bgcolor='$status' cellpadding='2' cellspacing='0' width='100%'><tr height='20'><td align='center'><font color='white'><b>$statustxt</b></font></td></tr></table></td>
	<td align='center'>".(defined($ovpntime) ? "$ovpntime" : "-")."</td>
</tr>
";

if ($wiosettings{'CLIENTREMARK'} eq 'on') {
	print"<tr".($idovpn % 2?" bgcolor='$color{'color20'}'":" bgcolor='$color{'color22'}'")." height='20'><td>&nbsp;</td><td colspan='16' align='left'>".($ovpnconfighash{$key}[25] ne '' ? "$ovpnconfighash{$key}[25]" : "-")."</td></tr>";
}

print"<tr height='1'><td colspan='17' bgcolor='#696565'></td></tr>";
$idovpn++
}

print"</table>";
&hrline();
}

## client status

print"
<table border='0' width='100%' bordercolor='$Header::bordercolour' cellspacing='0' cellpadding='0' style='border-collapse: collapse'>
<tr height='25'>
	<td width='33%' bgcolor='$color{'color20'}' align='left'><b>&nbsp;$Lang::tr{'wio_clients'}</b></td>
	<td width='67%'>&nbsp;</td>
</tr>
<tr><td colspan='2'>&nbsp;</td></tr>
</table>

<table border='0' width='100%' bordercolor='$Header::bordercolour' cellspacing='0' cellpadding='0' style='border-collapse: collapse'>
<tr bgcolor='$color{'color20'}' height='20'>
	<td width='3%' align='center'><b>$Lang::tr{'wio_id'}</b></td>
	<td width='4%' align='center'><b>$Lang::tr{'wio_activ'}</b></td>
	<td width='5%' align='center'><b>$Lang::tr{'wio_check'}</b></td>
	<td width='15%' align='center'><b>$Lang::tr{'wio checked'}</b></td>
	<td width='4%' align='center'><b>$Lang::tr{'wio_webinterface'}</b></td>
	<td width='11%' align='center'><a href='$ENV{'SCRIPT_NAME'}?IPADR'><b>$Lang::tr{'wio ipadress'}</b></a></td>
	<td width='5%' align='center'><b>$Lang::tr{'wio network'}</b></td>
	<td width='23%' align='center'><a href='$ENV{'SCRIPT_NAME'}?HOST'><b>$Lang::tr{'wio name'}</b></a></td>
	<td width='9%' align='center'><b>$Lang::tr{'wio image'}</b></td>
	<td width='3%' align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'><input type='hidden' name='ACTION' value='$Lang::tr{'wio_refresh'}' /><input type='image' name='$Lang::tr{'wio_refresh'}' src='$imgstatic/refresh.png' align='middle' alt='$Lang::tr{'wio_refresh'}' title='$Lang::tr{'wio_refresh'}' /></form></td>
	<td width='4%' colspan='2' align='center'><b>$Lang::tr{'wio_dyndns'}</b></td>
	<td width='12%' colspan='4' align='center'><b>$Lang::tr{'action'}</b></td>
	<td width='3%' align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'><input type='hidden' name='ACTION' value='$Lang::tr{'wio_remove_all'}' /><input type='image' name='$Lang::tr{'wio_remove_all'}' src='/images/delete.gif' align='middle' alt='$Lang::tr{'wio_remove_all'}' title='$Lang::tr{'wio_remove_all'}' onClick=\"return confirm('$Lang::tr{'wio_remove_all_hint'}')\"/></form></td>
</tr>
";

for (my $a=0; $a<$nr; $a++) {

my $gif = 'off.gif';
my $gdesc = $Lang::tr{'wio_client_off'};
my $dyndnsimg = 'on.gif';
my $dyndnsimgtxt = $Lang::tr{'wio_dyndns_on'};
my $mailonimg = 'wio/mailgreenon.png';
my $mailonimgtxt = $Lang::tr{'wio_mail_online_on'};
my $mailoffimg = 'wio/mailredon.png';
my $mailoffimgtxt = $Lang::tr{'wio_mail_offline_on'};
my $pingimg = '';
my $pingtxt = '';
my $webimg = '';

if ( $activ[$a] eq 'on' ) {
	$gif = 'on.gif';
	$gdesc = $Lang::tr{'wio_client_on'};
}

if ( $dyndns[$a] ne 'on' ) {
	$dyndnsimg = 'off.gif';
	$dyndnsimgtxt = $Lang::tr{'wio_dyndns_off'};
}

if ( $sendemailon[$a] ne 'on' ) {
	$mailonimg = 'wio/mailgreenoff.png';
	$mailonimgtxt = $Lang::tr{'wio_mail_online_off'};
}

if ( $sendemailoff[$a] ne 'on' ) {
	$mailoffimg = 'wio/mailredoff.png';
	$mailoffimgtxt = $Lang::tr{'wio_mail_offline_off'};
}

if ( $webinterface[$a] eq 'HTTP' ) {
	$webimg = 'wio/http.png';
}
elsif ( $webinterface[$a] eq 'HTTPS' ) {
	$webimg = 'wio/https.png';
}
else {
	$webimg = 'wio/none.png';
}

$bgcolor = $status[$a] eq "on" ? "${Header::colourgreen}" : ($status[$a] eq "off" && $dates[$a] eq "") ? "${Header::colourblue}" : "${Header::colourred}";
$statustxt = $status[$a] eq "on" ? "$Lang::tr{'wio up'}" : ($status[$a] eq "off" && $dates[$a] eq "") ? "$Lang::tr{'wio_no_image'}" : "$Lang::tr{'wio down'}";

print"<tr".($a % 2?" bgcolor='$color{'color20'}'":" bgcolor='$color{'color22'}'")." height='20'>";
printf ("<td align='center'> %02d</td>", $a+1);

print"<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>
	  <input type='hidden' name='ACTION' value='$Lang::tr{'enable disable client'}' />
	  <input type='image' name='$Lang::tr{'enable disable client'}' src='/images/$gif' align='middle' alt='$gdesc' title='$gdesc' />
	  <input type='hidden' name='ID' value='$a' /></form></td>";

if ( $pingmethode[$a] eq 'ip') {
	print"<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>
		<input type='hidden' name='ACTION' value='$Lang::tr{'wio_ip_on'}' />
		<input type='image' name='$Lang::tr{'wio_ip_on'}' src='/images/wio/ip.png' align='middle' alt='$Lang::tr{'wio_ip_on'}' title='$Lang::tr{'wio_ip_on'}' />
		<input type='hidden' name='ID' value='$a' /></form></td>";
}
else {
	print"<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>
		<input type='hidden' name='ACTION' value='$Lang::tr{'wio_fqdn_on'}' />
		<input type='image' name='$Lang::tr{'wio_fqdn_on'}' src='/images/wio/fqdn.png' align='middle' alt='$Lang::tr{'wio_fqdn_on'}' title='$Lang::tr{'wio_fqdn_on'}' />
		<input type='hidden' name='ID' value='$a' /></form></td>";
}

print"<td align='center'>$dates[$a]</td>";

print"<td align='center'><img align='middle' src='/images/$webimg' /></td>";

if ( $webinterface[$a] eq 'HTTP' ) {
	print"<td align='center'><a title=\"$Lang::tr{'wio_webinterface_link'}\" href=\"http://$ipaddresses[$a]\" target=\"_blank\">$ipaddresses[$a]</a></td>";
}
elsif ( $webinterface[$a] eq 'HTTPS' ) {
	print"<td align='center'><a title=\"$Lang::tr{'wio_webinterface_link'}\" href=\"https://$ipaddresses[$a]\" target=\"_blank\">$ipaddresses[$a]</a></td>";
}
else {
	print"<td align='center'>$ipaddresses[$a]</td>";
}

my $dotip = length($ipaddresses[$a]) - rindex($ipaddresses[$a],'.');
	SWITCH: {
		foreach (@devs_color) {
			my $in = 0;
			$ic = "${_}";

			foreach $interface (@devs_net) {
			next if ( $netsettings{"$ic"."_DEV"} eq 'red0' && $netsettings{"RED_TYPE"} eq 'PPPOE');
				if ( $netsettings{"$ic"."_DEV"} eq $interface ) {
					if ( &General::IpInSubnet($ipaddresses[$a], $netsettings{"$ic"."_NETADDRESS"}, $netsettings{"$ic"."_NETMASK"}) ) {
						if ( $netsettings{"$ic"."_DEV"} eq 'red0' ) {
							print"<td align='center' height='20'><img src='$imgstatic/$devs_img[$in]' alt='$Lang::tr{'wio_red_lan'}' title='$Lang::tr{'wio_red_lan'}' /></td>";
						}
						else {
							print"<td align='center' height='20'><img src='$imgstatic/$devs_img[$in]' alt='$Lang::tr{$devs_alt[$in]}' title='$Lang::tr{$devs_alt[$in]}' /></td>";
						}
					last SWITCH;
					}
				}
			$in++;
			}
		}

		if ( -e "$vpnpid" ) {
			foreach $key (keys(%vpnconfighash)) {
				next unless ($vpnconfighash{$key}[3] eq 'net');

				my $convertip = &General::ipcidr2msk($vpnconfighash{$key}[11]);

				my @net = split ("/", $convertip);

					$vpnn2nip = $net[0];
					$vpnn2nmask = length($net[1]) - rindex($net[1],'.');

					if (substr($ipaddresses[$a],0,length($ipaddresses[$a])-$dotip) eq substr($vpnn2nip,0,length($vpnn2nip)-$vpnn2nmask)) {
						print"<td align='center'><img align='middle' src='$imgstatic/vpn.png' alt='IPsec' title='IPsec' /></td>";
						last SWITCH;
					}
			}
		}

		if ( $ovpnsettings{'DOVPN_SUBNET'} ne '' ) {
			@match = split ("/", $ovpnsettings{'DOVPN_SUBNET'});

			if ( &General::IpInSubnet($ipaddresses[$a], $match[0], $match[1]) ) {
				print"<td align='center'><img src='$imgstatic/ovpn.png' alt='OpenVPN' title='OpenVPN' /></td>";
				last SWITCH;
			}
		}

		if ( %ovpnccdconfhash ne '' ) {
			foreach $key (keys(%ovpnccdconfhash)) {

				my $convertip = &General::ipcidr2msk($ovpnccdconfhash{$key}[1]);
				my @net = split ("/", $convertip);

				$vpnn2nip = $net[0];
				$vpnn2nmask = length($net[1]) - rindex($net[1],'.');

				if (substr($ipaddresses[$a],0,length($ipaddresses[$a])-$dotip) eq substr($vpnn2nip,0,length($vpnn2nip)-$vpnn2nmask)) {
					print"<td align='center'><img align='middle' src='$imgstatic/ovpn.png' alt='OpenVPN' title='OpenVPN' /></td>";
					last SWITCH;
				}
			}
		}

		if ( $netsettings{"RED_TYPE"} eq 'PPPOE' ) {
			my $redipadr = qx'ip addr | grep red0 | grep inet | awk "{print \$2}"';
			my @rednet = split ("/", $redipadr);
			chomp ($rednet[1]);
			my $red_netmask = General::iporsubtodec($rednet[1]);
			my $red_netaddress = Network::get_netaddress("$rednet[0]/$red_netmask");

			if ( &General::IpInSubnet($ipaddresses[$a], $red_netaddress, $red_netmask) ) {
				print"<td align='center' height='20'><img src='$imgstatic/red.png' alt='$Lang::tr{'internet'}' title='$Lang::tr{'internet'}' /></td>";
				last SWITCH;
			}
		}
		else {
				print"<td align='center'><img align='middle' src='$imgstatic/white.png' alt='$Lang::tr{'wio_unknown_lan'}' title='$Lang::tr{'wio_unknown_lan'}' /></td>";
				last SWITCH;
		}
	}

if ( $webinterface[$a] eq 'HTTP' ) {
	print"<td align='center'><a title=\"$Lang::tr{'wio_webinterface_link'}\" href=\"http://$names[$a]\" target=\"_blank\">$names[$a]</a></td>";
}
elsif ( $webinterface[$a] eq 'HTTPS' ) {
	print"<td align='center'><a title=\"$Lang::tr{'wio_webinterface_link'}\" href=\"https://$names[$a]\" target=\"_blank\">$names[$a]</a></td>";
}
else {
	print"<td align='center'>$names[$a]</td>";
}

print"
	<td>
		<table bgcolor='$bgcolor' cellpadding='2' cellspacing='0' width='100%'>
			<tr height='20'>
				<td align='center'><font color='$color{'color21'}'><b>$statustxt</b></font></td>
			</tr>
		</table>
	</td>

	<td width='3%' align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>
	<input type='hidden' name='ACTION' value='$Lang::tr{'wio_sc_refresh'}' />
	<input type='image' name='$Lang::tr{'wio_sc_refresh'}' src='$imgstatic/refresh.png' align='middle' alt='$Lang::tr{'wio_sc_refresh'}' title='$Lang::tr{'wio_sc_refresh'}' />
	<input type='hidden' name='ID' value='$a' /></form></td>

	<td width='3%' align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>
	<input type='hidden' name='ACTION' value='$Lang::tr{'enable disable dyndns'}' />
	<input type='image' name='$Lang::tr{'enable disable dyndns'}' src='/images/$dyndnsimg' align='middle' alt='$dyndnsimgtxt' title='$dyndnsimgtxt' />
	<input type='hidden' name='ID' value='$a' /></form></td>";

if ( defined($dyndns[$a]) && ($dyndns[$a] eq 'on') ) {
	print"<td width='3%' align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>
		  <input type='hidden' name='ACTION' value='$Lang::tr{'wio_dyndns_refresh'}' />
		  <input type='image' name='$Lang::tr{'wio_dyndns_refresh'}' src='/images/reload.gif' align='middle' alt='$Lang::tr{'wio_dyndns_refresh'}' title='$Lang::tr{'wio_dyndns_refresh'}' />
		  <input type='hidden' name='ID' value='$a' /></form></td>";
}
else {
	print"<td width='3%' align='center'>-</td>";
}

if ( -e "/var/log/rrd/wio/$id[$a].rrd" ) {
	print"
		<td width='3%' align='center'><form method='post' action='/cgi-bin/wiographs.cgi' enctype='multipart/form-data'>
		<input type='image' name='$Lang::tr{'wio_graphs'}' src='$imgstatic/graph.png' align='middle' alt='$Lang::tr{'wio_graphs'}' title='$Lang::tr{'wio_graphs'}' />
		<input type='hidden' name='HOSTID' value='$id[$a]' /><input type='hidden' name='HOSTNAME' value='$names[$a]' /></form></td>
	";
}
else {
	print "<td width='3%' align='center'><img src='$imgstatic/no_graph.png' align='middle' alt='$Lang::tr{'wio_no_graphs'}' title='$Lang::tr{'wio_no_graphs'}' /></td>";
}

if ( $wiosettings{'SENDEMAIL'} eq 'on') {
	print"<td width='3%' align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>
		  <input type='hidden' name='ACTION' value='$Lang::tr{'wio_mail_online'}' />
		  <input type='image' name='$Lang::tr{'wio_mail_online'}' src='/images/$mailonimg' align='middle' alt='$mailonimgtxt' title='$mailonimgtxt' />
		  <input type='hidden' name='ID' value='$a' /></form></td>
		  <td width='3%' align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>
		  <input type='hidden' name='ACTION' value='$Lang::tr{'wio_mail_offline'}' />
		  <input type='image' name='$Lang::tr{'wio_mail_offline'}' src='/images/$mailoffimg' align='middle' alt='$mailoffimgtxt' title='$mailoffimgtxt' />
		  <input type='hidden' name='ID' value='$a' /></form></td>";
}
else {
	print"<td width='3%' align='center'>-</td>
		  <td width='3%' align='center'>-</td>";
}

print"
	  <td width='3%' align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>
	  <input type='hidden' name='ACTION' value='$Lang::tr{'edit'}' />
	  <input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' align='middle' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' />
	  <input type='hidden' name='ID' value='$a' /></form></td>

	  <td width='3%' align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>
	  <input type='hidden' name='ACTION' value='$Lang::tr{'wio_remove_client'}' />
	  <input type='image' name='$Lang::tr{'wio_remove_client'}' src='/images/delete.gif' align='middle' alt='$Lang::tr{'wio_remove_client'}' title='$Lang::tr{'wio_remove_client'}' onClick=\"return confirm('$Lang::tr{'wio_remove_client_hint'}')\" />
	  <input type='hidden' name='ID' value='$a' /></form></td></tr>
";

if ($wiosettings{'CLIENTREMARK'} eq 'on') {
	print"<tr".($a % 2?" bgcolor='$color{'color20'}'":" bgcolor='$color{'color22'}'")." height='20'><td>&nbsp;</td><td colspan='16' align='left'>".($remark[$a] ne '' ? "$remark[$a]" : "-")."</td></tr>";
}
	print"<tr height='1'><td colspan='17' bgcolor='#696565'></td></tr>";
}

print"</table>";

&Header::closebox();

}

## add / modify client

$checked{'EN'}{'on'} = ($wiosettings{'EN'} eq '' ) ? '' : "checked='checked'";

$checked{'DYNDNS'}{'off'} = $checked{'DYNDNS'}{'on'} = '';
$checked{'DYNDNS'}{$wiosettings{'DYNDNS'}} = "checked='checked'";

$checked{'SENDEMAILON'}{'off'} = $checked{'SENDEMAILON'}{'on'} = '';
$checked{'SENDEMAILON'}{$wiosettings{'SENDEMAILON'}} = "checked='checked'";

$checked{'SENDEMAILOFF'}{'off'} = $checked{'SENDEMAILOFF'}{'on'} = '';
$checked{'SENDEMAILOFF'}{$wiosettings{'SENDEMAILOFF'}} = "checked='checked'";

if (! defined($errormessage) && $wiosettings{'ACTION'} ne $Lang::tr{'edit'} ) {
	$wiosettings{'PINGMETHODE'} = 'ip';
}

$checked{'PINGMETHODE'}{'ip'} = $checked{'PINGMETHODE'}{'fqdn'} = '';
$checked{'PINGMETHODE'}{$wiosettings{'PINGMETHODE'}} = "checked='checked'";

$selected{'WEBINTERFACE'}{'----'} = '';
$selected{'WEBINTERFACE'}{'HTTP'} = '';
$selected{'WEBINTERFACE'}{'HTTPS'} = '';
$selected{'WEBINTERFACE'}{$wiosettings{'WEBINTERFACE'}} = "selected='selected'";

$buttontext = $Lang::tr{'wio_client_add'};

if ( $wiosettings{'ACTION'} eq $Lang::tr{'edit'} || defined($errormessage)  && ! defined($message) ) {
	&Header::openbox('100%', 'left', $Lang::tr{'wio_edit_client'});
	$buttontext = $Lang::tr{'update'};
}
else {
	&Header::openbox('100%', 'left', $Lang::tr{'wio_edit_settings'});
}

if (! defined($errormessage) && $wiosettings{'ACTION'} ne $Lang::tr{'edit'} ) {
print"
<table width='100%' border='0' bordercolor='$Header::bordercolour' cellspacing='0' cellpadding='0' style='border-collapse: collapse'>
<tr>
	<td width='33%' bgcolor='$color{'color20'}' align='left' height='25'><b>&nbsp;$Lang::tr{'wio_add'}</b></td>
	<td width='67%' align='right'>&nbsp;</td>
</tr>
<tr>
	<td>&nbsp;</td>
</tr>
</table>
";
}

print"
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='ID' value='$wiosettings{'ID'}' />
<input type='hidden' name='CLIENTID' value='$wiosettings{'CLIENTID'}' />
<input type='hidden' name='ONLINE' value='$wiosettings{'ONLINE'}' />
<input type='hidden' name='TIMESTAMP' value='$wiosettings{'TIMESTAMP'}' />
";

print"
<table width='100%' border='0' bordercolor='$Header::bordercolour' cellspacing='0' cellpadding='0' style='border-collapse: collapse'>
<tr>
	<td height='30'>$Lang::tr{'wio_client_enable'}</td>
	<td align='left'><input type='checkbox' name='EN' $checked{'EN'}{'on'} /></td>
	<td colspan='4'>&nbsp;</td>
</tr>
<tr>
	<td height='30'>$Lang::tr{'wio ipadress'}:</td>
	<td align='left'><input type='text' name='IPADR' value='$wiosettings{'IPADR'}' size='25' /></td>
	<td>$Lang::tr{'wio name'}:</td>
	<td align='left'><input type='text' name='HOST' value='$wiosettings{'HOST'}' size='25' /></td>
	<td>$Lang::tr{'remark'}:</td>
	<td align='left'><input type='text' name='REMARK' value='$wiosettings{'REMARK'}' size='30'></td>
</tr>
<tr>
	<td height='30'>$Lang::tr{'wio_ping_send'}:</td>
	<td align='left'><input type='radio' name='PINGMETHODE' value='ip' $checked{'PINGMETHODE'}{'ip'} />&nbsp;IP&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type='radio' name='PINGMETHODE' value='fqdn' $checked{'PINGMETHODE'}{'fqdn'} />&nbsp;FQDN</td>
	<td>$Lang::tr{'wio_dyndns'}:</td>
	<td align='left'><input type='checkbox' name='DYNDNS' $checked{'DYNDNS'}{'on'} /></td>
";

if ( $wiosettings{'SENDEMAIL'} eq 'on' ) {
	print"<td>$Lang::tr{'wio_sendemail'}:</td>
		  <td><input type='checkbox' name='SENDEMAILON' $checked{'SENDEMAILON'}{'on'} />&nbsp;$Lang::tr{'wio_online'}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type='checkbox' name='SENDEMAILOFF' $checked{'SENDEMAILOFF'}{'on'} />&nbsp;$Lang::tr{'wio_offline'}</td>";
}
else {
	print"<td colspan='2'>&nbsp;</td>";
}

print"
</tr>
<tr>
	<td height='30'>$Lang::tr{'wio_link_open'}:</td>
	<td align='left' colspan='5'>
		<select size='1' name='WEBINTERFACE' width='80' style='width: 80px'>
		<option value='----' $selected{'WEBINTERFACE'}{'----'}>----</option>
		<option value='HTTP' $selected{'WEBINTERFACE'}{'HTTP'}>HTTP</option>
		<option value='HTTPS' $selected{'WEBINTERFACE'}{'HTTPS'}>HTTPS</option>
		</select>
	</td>
</tr>
</table>
<table width='100%' cellspacing='0' cellpadding='0' style='border-collapse: collapse'>
<tr>
	<td width='20%' align='center'>&nbsp;</td>
";

if ( $buttontext eq $Lang::tr{'update'} && ( defined($errormessage) || $wiosettings{'ACTION'} eq $Lang::tr{'edit'}) && ! defined($message) ) {
	print"<td width='20%' align='center'>&nbsp;</td>
		  <td width='20%' align='center'>&nbsp;</td>
		  <td width='20%' align='center'><input type='hidden' name='ACTION' value='$Lang::tr{'wio_client_add'}' /><input type='submit' name='SUBMIT' value='$buttontext' /></td>
		  <td width='20%' align='center'><input type='button' onClick='location.href=\"/cgi-bin/wio.cgi\"' value='$Lang::tr{'wio_back'}'></form></td>";
}
else {
	print"<td width='20%' align='center'>&nbsp;</td>
		  <td width='20%' align='center'>&nbsp;</td>
		  <td width='20%' align='center'>&nbsp;</td>
		  <td width='20%' align='right'><input type='hidden' name='ACTION' value='$Lang::tr{'wio_client_add'}' /><input type='submit' name='SUBMIT' value='$buttontext' /></form></td>";
}

print"
</tr>
</table>
";

if ( $wiosettings{'ENABLE'} eq 'on' && !$errormessage && $wiosettings{'ACTION'} ne $Lang::tr{'edit'} || $message == 2 ) {

&hrline();

## arp table entries

print"
<table border='0' width='100%' bordercolor='$Header::bordercolour' cellspacing='0' cellpadding='0' style='border-collapse: collapse'>
<tr>
	<td width='33%' bgcolor='$color{'color20'}' align='left' height='25'><b>&nbsp;$Lang::tr{'wio_arp_table_entries'}</b></td>
	<td width='67%' align='right'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='WIOGUISHOWARPTABLE' value='arptable' /><input type='submit' name='ACTION' value='$arpbuttontext' /></form></td>
</tr>
</table>
";

if ( $wiosettings{'WIOGUISHOWARPTABLE'} eq 'on' ) {

print"
<table border='0' width='100%' bordercolor='$Header::bordercolour' cellspacing='0' cellpadding='0' style='border-collapse: collapse'>
<tr><td colspan='2'>&nbsp;</td></tr>
<tr bgcolor='$color{'color20'}'>
	<td width='5%' align='center' height='20'><b>$Lang::tr{'wio_id'}</b></td>
	<td width='20%' align='center' height='20'><b>$Lang::tr{'wio_hwaddress'}</b></td>
	<td width='20%' align='center' height='20'><b>$Lang::tr{'wio ipadress'}</b></td>
	<td width='15%'  align='center' height='20'><b>$Lang::tr{'wio network'}</b></td>
	<td width='20%' align='center' height='20'><b>$Lang::tr{'wio name'}</b></td>
	<td width='15%' align='center' height='20'><b>$Lang::tr{'wio_iface'}</b></td>
	<td width='5%' align='center' height='20'><b>$Lang::tr{'action'}</b></td>
</tr>
";

$output = `/sbin/ip neigh list`;
$output = &Header::cleanhtml($output,"y");

my $arpcnt = 0;

foreach $line (split(/\n/, $output))
{
	if ($line =~ m/^(.*) dev ([^ ]+) lladdr ([0-9a-f:]*) (.*)$/) {
		my $arphost = gethostbyaddr(inet_aton($1), AF_INET);
		if ( $arphost eq 'localhost' ) { $arphost = ''; }
		push (@arpcache, "$3,$1,$arphost,$2\n");
	}
	elsif ($line =~ m/^(.*) dev ([^ ]+)  (.*)$/) {
		my $arphost = gethostbyaddr(inet_aton($1), AF_INET);
		if ( $arphost eq 'localhost' ) { $arphost = ''; }
		push (@arpcache, ",$1,$arphost,$2\n");
	}

	$arpcnt++;
}

&SortDataFile('arpcache',@arpcache);

foreach (@arpcache) {
	chomp;

	@line = split (/\,/, $_);

	print"<tr".($idarp % 2?" bgcolor='$color{'color20'}'":" bgcolor='$color{'color22'}'")." height='20'>";
	printf ("<td align='center'> %02d</td>", $idarp+1);
	print"<td align='center'>$line[0]</td>
		  <td align='center'>$line[1]</td>";

SWITCH: {

	foreach (@devs_color) {
		my $in = 0;
		$ic = "${_}";

		foreach $interface (@devs_net) {
			next if ( $netsettings{"$ic"."_DEV"} eq 'red0' && ($netsettings{"RED_TYPE"} eq 'DHCP' || $netsettings{"RED_TYPE"} eq 'PPPOE'));

			if ($netsettings{"$ic"."_DEV"} eq $interface) {
				if ( &General::IpInSubnet($line[1], $netsettings{"$ic"."_NETADDRESS"}, $netsettings{"$ic"."_NETMASK"}) ) {
					print"<td align='center'><img src='$imgstatic/$devs_img[$in]' alt='$Lang::tr{$devs_alt[$in]}' title='$Lang::tr{$devs_alt[$in]}' /></td>";
					last SWITCH;
				}
			}

			$in++;
		}
	}

			if ($netsettings{"RED_TYPE"} eq 'DHCP' || $netsettings{"RED_TYPE"} eq 'PPPOE' || $netsettings{"RED_TYPE"} eq 'STATIC') {
			my $redipadr = qx'ip addr | grep red0 | grep inet | awk "{print \$2}"';
			my @rednet = split ("/", $redipadr);
			chomp ($rednet[1]);
			my $red_netmask = General::iporsubtodec($rednet[1]);
			my $red_netaddress = Network::get_netaddress("$rednet[0]/$red_netmask");

			if ( &General::IpInSubnet($line[1], $red_netaddress, $red_netmask) ) {
				print"<td align='center' height='20'><img src='$imgstatic/red.png' alt='$Lang::tr{'internet'}' title='$Lang::tr{'internet'}' /></td>";
				last SWITCH;
			}
			else {
				print"<td align='center'><img align='middle' src='$imgstatic/white.png' alt='$Lang::tr{'wio_unknown_lan'}' title='$Lang::tr{'wio_unknown_lan'}' /></td>";
				last SWITCH;
			}
		}
}

	print"<td align='center'>$line[2]</td>
		  <td align='center'>".&WIO::color_devices($line[3])."</td>";

	unless (&WIO::checkinto($line[1], '', @current)) {
		print"<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>
			  <input type='hidden' name='ACTION' value='$Lang::tr{'wio_add'}' />
			  <input type='image' name='$Lang::tr{'wio_add'}' src='/images/add.gif' align='middle' alt='$Lang::tr{'wio_add'}' title='$Lang::tr{'wio_add'}' />
			  <input type='hidden' name='ID' value='$idarp' /></form></td>";
	}
	else {
		print"<td align='center'><img src='$imgstatic/add.png' align='middle' alt='$Lang::tr{'wio_no_add'}' title='$Lang::tr{'wio_no_add'}' /></td>";
	}

print"</tr>";
print"<tr height='1'><td colspan='17' bgcolor='#696565'></td></tr>";
$idarp++
}

print"
</table>
";
}

&hrline();

print"
<table border='0' width='100%' bordercolor='$Header::bordercolour' cellspacing='0' cellpadding='0' style='border-collapse: collapse'>
<tr>
	<td width='33%' bgcolor='$color{'color20'}' align='left' height='25'><b>&nbsp;$Lang::tr{'wio_import_file'}</b></td>
	<td width='67%' align='right'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='WIOGUISHOWCLIENTIMPORTTABLE' value='clientimport' /><input type='submit' name='ACTION' value='$clientimportbuttontext' /></form></td>
</tr>
</table>
";

if ( $wiosettings{'WIOGUISHOWCLIENTIMPORTTABLE'} eq 'on' ) {

print"
<table width='100%' cellspacing='0' cellpadding='0' style='border-collapse: collapse'>
<tr><td colspan='3'>&nbsp;</td></tr>
<tr bgcolor='$color{'color22'}'>
	<form method='post' action='/cgi-bin/wio.cgi' enctype='multipart/form-data'>
	<td width='33%' align='right'>$Lang::tr{'wio_import_csv'}&nbsp;</td>
	<td width='40%' align='center'><input type='file' name='CSVFILE' size='30' /></td>
	<td width='27%' align='right'><input type='hidden' name='ACTION' value='$Lang::tr{'wio_import'}1' /><input type='submit' name='SUBMIT' value='$Lang::tr{'wio_import'}' /></td>
	</form>
</tr>
<tr><td colspan='3'>&nbsp;</td></tr>
<tr bgcolor='$color{'color22'}'>
	<form method='post' action='/cgi-bin/wio.cgi' enctype='multipart/form-data'>
	<td width='33%' align='right'>$Lang::tr{'wio_import_hosts'}&nbsp;</td>
	<td width='40%' align='center'>&nbsp;</td>
	<td width='27%' align='right'><input type='hidden' name='ACTION' value='$Lang::tr{'wio_import'}2' /><input type='submit' name='SUBMIT' value='$Lang::tr{'wio_import'}' /></td>
	</form>
</tr>
<tr><td colspan='3'>&nbsp;</td></tr>
<tr bgcolor='$color{'color22'}'>
	<form method='post' action='/cgi-bin/wio.cgi' enctype='multipart/form-data'>
	<td width='33%' align='right'>$Lang::tr{'wio_import_fixleases'}&nbsp;</td>
	<td width='40%' align='center'>&nbsp;</td>
	<td width='27%' align='right'><input type='hidden' name='ACTION' value='$Lang::tr{'wio_import'}3' /><input type='submit' name='SUBMIT' value='$Lang::tr{'wio_import'}' /></td>
	</form>
</tr>
</table>
";
}

&hrline();

print"
<table border='0' width='100%' bordercolor='$Header::bordercolour' cellspacing='0' cellpadding='0' style='border-collapse: collapse'>
<tr>
	<td width='33%' bgcolor='$color{'color20'}' align='left' height='25'><b>&nbsp;$Lang::tr{'wio_net_scan'}</b></td>
	<td width='67%' align='right'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='WIOGUISHOWNETWORKSEARCHTABLE' value='networksearch' /><input type='submit' name='ACTION' value='$networksearchbuttontext' /></form></td>
</tr>
</table>
";

if ( $wiosettings{'WIOGUISHOWNETWORKSEARCHTABLE'} eq 'on' ) {

print"
<table width='100%' cellspacing='0' cellpadding='0' style='border-collapse: collapse'>
<tr>
	<td colspan='3'>&nbsp;</td>
</tr>
";

foreach (keys(%ifacecolor)) {
	if ( $_ eq 'GREEN' ) { $color = "$Header::colourgreen"; $net = $Lang::tr{'wio_net_scan_green'}; }
	elsif ( $_ eq 'BLUE' ) { $color = "$Header::colourblue"; $net = $Lang::tr{'wio_net_scan_blue'}; }
	elsif ( $_ eq 'RED' ) { $color = "$Header::colourred"; $net = $Lang::tr{'wio_net_scan_red'}; }
	else { $color = "$Header::colourorange"; $net = $Lang::tr{'wio_net_scan_orange'}; }

	if ( $netsettings{"${_}_DEV"} eq 'disabled' || $netsettings{"${_}_DEV"} eq '' || $netsettings{"${_}_ADDRESS"} eq '' ) { next; }
	else {
		print <<END;

			<tr bgcolor='$color{'color22'}'>
				<td width='33%' align='right'><form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>$Lang::tr{'wio_net_scan_l'} <font color='$color'><b>$net&nbsp;</b></font>$Lang::tr{'wio_net_scan_r'}</td>
				<td width='40%' align='center'><input type='text' name='${_}_IPLOW' value='$wiosettings{"${_}_IPLOW"}' size='14' STYLE='background-color:$color; text-align: center; color:white' /> - <input type='text' name='${_}_IPHIGH' value='$wiosettings{"${_}_IPHIGH"}' size='14' STYLE='background-color:$color; text-align: center; color:white' /></td>
				<td width='27%' align='right'><input type='hidden' name='ACTION' value='$ifacecolor{$_}' /><input type='hidden' name='ID' value='$netsettings{"${_}_DEV"}' /><input type='submit' name='SUBMIT' value='$Lang::tr{'wio_net_scan_run'}'></form></td>
			</tr>
			<tr>
				<td colspan='3'>&nbsp;</td>
			</tr>
END
	}
}

print"
</tr>
</table>
</form>
";
}
&Header::closebox();
}

if ( $wiosettings{'ENABLE'} eq 'on' && !$errormessage && $wiosettings{'ACTION'} ne $Lang::tr{'edit'} || $message == 2 ) {

&Header::openbox('100%', 'left', $Lang::tr{'wio_service'});

print"
<table border='0' width='100%' bordercolor='$Header::bordercolour' cellspacing='0' cellpadding='0' style='border-collapse: collapse'>
<tr bgcolor='$color{'color22'}'>
	<td colspan='2' align='right'></td>
";

if ( $wiosettings{'LOGGING'} eq 'on' ) {
	print"<td width='10%' align='right'><form method='post' action='/cgi-bin/logs.cgi/log.dat' enctype='multipart/form-data'><input type='hidden' name='SECTION' value='wio' /><input type='submit' name='SUBMIT' value='$Lang::tr{'system logs'}' /></form></td>";
}

print"
	<td width='10%' align='right'><form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'><input type='hidden' name='ACTION' value='$Lang::tr{'edit'}1' /><input type='submit' name='SUBMIT' value='$Lang::tr{'wio_edit_set'}' /></form></td>
</tr>
</table>
";
}

&Header::closebox();
}

&Header::closebigbox();
&Header::closepage();

############################################################################################################################

sub SortDataFile {
my ($data,@checkfile) = @_;
	my $idsort = 0;
	our %entries = ();

	sub sortips {
		my $qs = '';

		if (rindex ($wiosettings{'SORT'},'Rev') != -1) {
			$qs = substr ($wiosettings{'SORT'},0,length($wiosettings{'SORT'})-3);

			if ($qs eq 'IPADR') {
				my @a = split (/\./,$entries{$a}->{$qs});
				my @b = split (/\./,$entries{$b}->{$qs});
				($b[0]<=>$a[0]) ||
				($b[1]<=>$a[1]) ||
				($b[2]<=>$a[2]) ||
				($b[3]<=>$a[3]);
			}
			else {
				$entries{$b}->{$qs} cmp $entries{$a}->{$qs};
			}
		}
		else {
			$qs = $wiosettings{'SORT'};

			if ($qs eq 'IPADR') {
				my @a = split (/\./,$entries{$a}->{$qs});
				my @b = split (/\./,$entries{$b}->{$qs});
				($a[0]<=>$b[0]) ||
				($a[1]<=>$b[1]) ||
				($a[2]<=>$b[2]) ||
				($a[3]<=>$b[3]);
			}
			else {
				$entries{$a}->{$qs} cmp $entries{$b}->{$qs};
			}
		}
	}

	if ($data eq 'arpcache') {
		foreach (@checkfile) {
			chomp;
			@temp = split (',', $_);

			my @record = ('KEY',$idsort++,'MAC',$temp[0],'IPADR',$temp[1],'HOST',$temp[2],'REMARK',$temp[3],'IFACE',$temp[4]);
			my $record = ();
			%{$record} = @record; 
			$entries{$record->{KEY}} = $record;
		}

		open(FILE, "> $logdir/.arpcache");

		foreach (sort sortips keys %entries) {
			print FILE "$entries{$_}->{MAC},$entries{$_}->{IPADR},$entries{$_}->{HOST},$entries{$_}->{REMARK},$entries{$_}->{IFACE},$entries{$_}->{HW}\n";
		}

		close(FILE);

		open (FILE, "$logdir/.arpcache");
		@arpcache = <FILE>;
		close (FILE);
	}
	else {
		foreach (@checkfile) {
			chomp;
			@temp = split (',', $_);

			my @record = ('KEY',$idsort++,'CLIENTID',$temp[0],'TIMESTAMP',$temp[1],'IPADR',$temp[2],'HOST',$temp[3],'EN',$temp[4],'REMARK',$temp[5],'DYNDNS',$temp[6],'SENDEMAILON',$temp[7],'SENDEMAILOFF',$temp[8],'PINGMETHODE',$temp[9],'ONLINE',$temp[10],'WEBINTERFACE',$temp[11]);
			my $record = ();
			%{$record} = @record; 
			$entries{$record->{KEY}} = $record;
		}

		open(FILE, "> $ipadrfile");

		foreach (sort sortips keys %entries) {
			print FILE "$entries{$_}->{CLIENTID},$entries{$_}->{TIMESTAMP},$entries{$_}->{IPADR},$entries{$_}->{HOST},$entries{$_}->{EN},$entries{$_}->{REMARK},$entries{$_}->{DYNDNS},$entries{$_}->{SENDEMAILON},$entries{$_}->{SENDEMAILOFF},$entries{$_}->{PINGMETHODE},$entries{$_}->{ONLINE},$entries{$_}->{WEBINTERFACE}\n";
		}

		close(FILE);

		&loadips();
	}
}

############################################################################################################################

sub hrline { 

print"<table width='100%'><tr><td colspan='2' height='35'><hr></td></tr></table>";

}

############################################################################################################################

sub loadips {

&General::readhasharray($ipadrfile, \%ipshash);

open(FILE, "< $ipadrfile");
@current = <FILE>;
close (FILE);

}

############################################################################################################################

sub writeips {

open(FILE, "> $ipadrfile");
if ( defined($write) ) { print FILE @write; }
else { print FILE @current; }
close(FILE);

}

############################################################################################################################

sub SortByTunnelName {

	if ($vpnconfighash{$a}[1] lt $vpnconfighash{$b}[1]) {
		return -1;
	}
	elsif ($vpnconfighash{$a}[1] gt $vpnconfighash{$b}[1]) {
		return 1;
	}
	else {
		return 0;
	}

}

############################################################################################################################

sub validSave {

	if ( $wiosettings{'IPADR'} eq '' && $wiosettings{'PINGMETHODE'} eq 'ip' && $wiosettings{'DYNDNS'} eq '' ) {
		$errormessage = $Lang::tr{'wio_ip_empty'};
	}

	if ( $wiosettings{'IPADR'} ne '' && (! &General::validip($wiosettings{'IPADR'})) ) {
		$errormessage = $Lang::tr{'wio_ip_error'};
	}

	if ( $wiosettings{'HOST'} eq '' && $wiosettings{'PINGMETHODE'} eq 'fqdn' ) {
		$errormessage = $Lang::tr{'wio_host_empty'};
	}

	if ( $wiosettings{'HOST'} ne '' && (! &General::validdomainname($wiosettings{'HOST'})) ) {
		$errormessage = $Lang::tr{'wio_host_error'};
	}

	if ( $wiosettings{'DYNDNS'} eq 'on' && (! defined($errormessage)) ) {
		unless(&General::validfqdn($wiosettings{'HOST'})) { $errormessage = $Lang::tr{'wio_fqdn_error'}; }
		( $wiosettings{'IPADR'}, $infomessage ) = &WIO::getdyndnsip($wiosettings{'IPADR'}, $wiosettings{'HOST'});
		$wiosettings{'PINGMETHODE'} = 'fqdn';
	}

	if ( $wiosettings{'ID'} eq '' && ! defined($errormessage) ) { $errormessage = &WIO::checkinto($wiosettings{'IPADR'}, $wiosettings{'HOST'}, @current); }

	if ( $wiosettings{'REMARK'} ne '' ) { $wiosettings{'REMARK'} =~ s/,/&#44;/g; }

}
