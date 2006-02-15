#!/usr/bin/perl
#
# This file is part of the IPCop Firewall.
#
# IPCop is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# IPCop is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with IPCop; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# (c) The SmoothWall Team
#
# $Id: rc.red,v 1.29.2.56 2005/12/17 08:49:01 gespinasse Exp $


# Clean up our environment (we're running SUID!)
delete @ENV{qw(IFS CDPATH ENV BASH_ENV PATH)};
$< = $>;

use strict;
require 'CONFIG_ROOT/general-functions.pl';

my %pppsettings;
my %isdnsettings;
my %netsettings;
my %dhcpsettings;
my $iface;

# read vars back from file.
&General::readhash("${General::swroot}/ppp/settings", \%pppsettings);
&General::readhash("${General::swroot}/isdn/settings", \%isdnsettings);
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
&General::readhash("${General::swroot}/dhcp/settings", \%dhcpsettings);

sub dodhcpdial($;$) {
	my ($iface,$dhcp_name)=@_;

	system ('/sbin/iptables', '-A', 'REDINPUT', '-p', 'tcp', '--source-port', '67', 
		'--destination-port', '68', '-i', $iface, '-j', 'ACCEPT');
	system ('/sbin/iptables', '-A', 'REDINPUT', '-p', 'udp', '--source-port', '67', 
		'--destination-port', '68', '-i', $iface, '-j', 'ACCEPT');

	foreach ("<${General::swroot}/dhcpc/*.info>") { unlink $1 if ( $_ =~ /^([\/\w.-]+)$/ ); }
	my @dhcpcommand = ('/usr/sbin/dhcpcd');
	push(@dhcpcommand, ('-N', '-R', "$iface",'-L', "${General::swroot}/dhcpc"));

	#FIXME the only way actually to set debug use is in pppsetup.cgi and 'RED is modem/isdn' interface
	if ($pppsettings{'DEBUG'} eq 'on') {
		push(@dhcpcommand, ('-d'));
	}

	if ($dhcp_name ne '') { push(@dhcpcommand, ('-h', "$dhcp_name")); }
	if ($netsettings{'RED_TYPE'} eq 'PPTP') { push(@dhcpcommand, '-G'); }

	if (system (@dhcpcommand)) {
		&General::log('dhcpcd fail');
		exit 1;
	} else {
		&General::log('dhcpcd success');
	}
}

sub doupdatesettings {
	# complete cleanup only if settings were changed or clear is ordered
	system('/sbin/modprobe', '-r', 'pppoatm');
	system('/sbin/modprobe', '-r', 'pppoe');
	system('/bin/killall /usr/bin/br2684ctl 2>/dev/null');
	system('/sbin/modprobe', '-r', 'br2684');
	system('/sbin/modprobe', '-r', 'clip');

	if ($pppsettings{'TYPE'} ne '3cp4218usbadsl') 	{ system('/sbin/modprobe', '-r', '3cp4218');}
	if ($pppsettings{'TYPE'} ne 'alcatelusbk') 	{ system('/sbin/modprobe', '-r', 'speedtch');}
	if ($pppsettings{'TYPE'} ne 'amedynusbadsl') 	{ system('/sbin/modprobe', '-r', 'amedyn');}
	if ($pppsettings{'TYPE'} ne 'bewanadsl') {
		system('/sbin/modprobe', '-r', 'unicorn_pci_atm', 'unicorn_usb_atm');}
	if ($pppsettings{'TYPE'} ne 'conexantpciadsl') 	{ system('/sbin/modprobe', '-r', 'CnxADSL');}
	if ($pppsettings{'TYPE'} ne 'conexantusbadsl') 	{ system('/sbin/modprobe', '-r', 'cxacru');}
	if ($pppsettings{'TYPE'} ne 'eagleusbadsl') 	{ system('/sbin/modprobe', '-r', 'eagle-usb');}
	if ($pppsettings{'TYPE'} ne 'fritzdsl') 	{ 
		system('/sbin/modprobe', '-r', 'fcdsl', 'fcdsl2', 'fcdslsl', 'fcdslusb', 'fcdslslusb');}
	if ($pppsettings{'TYPE'} ne 'pulsardsl') 	{ system('/sbin/modprobe', '-r', 'pulsar');}
	sleep 1;
	if ($pppsettings{'TYPE'} !=~ /^(3cp4218usbadsl|alcatelusbk|amedynusbadsl|bewanadsl|conexantpciadsl|pulsardsl)$/) {
		system('/sbin/modprobe', '-r', 'atm');

	# remove existing default route (for static address) if it was been changed from setup or web interface SF1175052
	system ('/sbin/route del default 2>/dev/null');

	# erase in case it was created once with 'persistent' selected but rc.red stop never used : SF1171610
	unlink ("${General::swroot}/red/iface");
	}
}

# No output should be sent to the webclient
open STDIN, '</dev/zero' or die "Can't read from /dev/zero";
open STDOUT, '>/dev/null' or die "Can't write to /dev/null";

if ($ARGV[0] eq 'start') {
	if (-e "${General::swroot}/red/active" ||
	    -e '/var/run/ppp-ipcop.pid')
	{
		&General::log ("ERROR: Can't start RED when it's still active");
		exit 1;
	}

	if ( ( ( ($netsettings{'RED_TYPE'} =~ /^(PPPOE|PPTP)$/) && ($netsettings{'CONFIG_TYPE'} =~ /^(2|3|6|7)$/) ) ||
		  ( ( ($pppsettings{'METHOD'} =~ /^(PPPOE|PPPOE_PLUGIN)$/) || ($pppsettings{'PROTOCOL'} eq 'RFC2364') ) &&
		  ($netsettings{'CONFIG_TYPE'} =~ /^(0|1|4|5)$/) ) ) && ($pppsettings{'RECONNECTION'} ne 'manual') ) {
		system ('/etc/rc.d/rc.connectioncheck start &');
	}

	###
	### Red device is ethernet
	###
	if ($netsettings{'CONFIG_TYPE'} =~ /^(2|3|6|7)$/)
	{
		if ($netsettings{'RED_DEV'} ne '')
		{
			&General::log("Starting RED device $netsettings{'RED_DEV'}."); 

			if ( $netsettings{'RED_TYPE'} eq 'DHCP')
			{
				if (open(FILE, ">${General::swroot}/red/iface")) { print FILE $netsettings{'RED_DEV'}; close FILE; }
				dodhcpdial($netsettings{'RED_DEV'},$netsettings{'RED_DHCP_HOSTNAME'});
				exit 0;
			}
			elsif 	( ( $netsettings{'RED_TYPE'} eq 'PPTP') && ( $pppsettings{'METHOD'} eq 'DHCP') )
			{
				if (open(FILE, ">${General::swroot}/red/device")) { print FILE $netsettings{'RED_DEV'}; close FILE; }
				unlink ("${General::swroot}/red/iface");
				dodhcpdial($netsettings{'RED_DEV'},$netsettings{'RED_DHCP_HOSTNAME'});
			}
			elsif ( ( $netsettings{'RED_TYPE'} eq 'STATIC') ||
				( $netsettings{'RED_TYPE'} eq 'PPTP') && ( $pppsettings{'METHOD'} ne 'DHCP') )
			{
				system ("/sbin/ifconfig",
					$netsettings{'RED_DEV'}, $netsettings{'RED_ADDRESS'},
					"netmask", $netsettings{'RED_NETMASK'},
					"broadcast", $netsettings{'RED_BROADCAST'},"up");
				if ( $netsettings{'RED_TYPE'} eq 'STATIC')
				{
					system("/usr/local/bin/setaliases");
					system("echo $netsettings{'DNS1'}    > ${General::swroot}/red/dns1");
					system("echo $netsettings{'DNS2'}    > ${General::swroot}/red/dns2");
					system("echo $netsettings{'RED_ADDRESS'} > ${General::swroot}/red/local-ipaddress");
					system("echo $netsettings{'DEFAULT_GATEWAY'} > ${General::swroot}/red/remote-ipaddress");
				} elsif ( $netsettings{'RED_TYPE'} eq 'PPTP' ) {
					if (open(FILE, ">${General::swroot}/red/device")) { print FILE $netsettings{'RED_DEV'}; close FILE; }
					unlink ("${General::swroot}/red/iface");
				}
				if ( $netsettings{'DEFAULT_GATEWAY'} ne '' )
				{
					system ("/sbin/route","add","default","gw",
						$netsettings{'DEFAULT_GATEWAY'});
				}
			}
			else
			{
				# PPPoE
				system ("/sbin/ifconfig", $netsettings{'RED_DEV'}, "1.1.1.1",
					"netmask", "255.255.255.0", "broadcast", "1.1.1.255", "up");
			}

			if ( $netsettings{'RED_TYPE'} eq 'STATIC')
			{
				if (open(FILE, ">${General::swroot}/red/iface")) { print FILE $netsettings{'RED_DEV'}; close FILE; }
				system ("/bin/touch", "${General::swroot}/red/active");
				system ("/etc/rc.d/rc.updatered");
				exit 0;
			}
		}
		else
		{
			&General::log ("ERROR: Can't start RED when RED device not set!");
			exit 1;
		}
	}

	
	if ($pppsettings{'RECONNECTION'} eq 'dialondemand')
	{
		system ('/bin/touch', "${General::swroot}/red/dial-on-demand");
	}

	if ($pppsettings{'VALID'} ne 'yes') {
		&General::log("Profile has errors.");
		exit 1;
	}

	if (-e "${General::swroot}/ppp/updatesettings") {
		&doupdatesettings;
	}

	if (( $pppsettings{'METHOD'} eq 'STATIC') && ( $pppsettings{'DNS'} eq 'Manual')) {
		system("/usr/local/bin/setaliases");
		if (open(FILE, ">${General::swroot}/red/dns1")) { print FILE $pppsettings{'DNS1'}; close FILE; }
		if (open(FILE, ">${General::swroot}/red/dns2")) { print FILE $pppsettings{'DNS2'}; close FILE; }
		if (open(FILE, ">${General::swroot}/red/local-ipaddress")) { print FILE $pppsettings{'IP'}; close FILE; }
		if (open(FILE, ">${General::swroot}/red/remote-ipaddress")) { print FILE $pppsettings{'GATEWAY'}; close FILE; }
	}
	if ($pppsettings{'RECONNECTION'} eq 'dialondemand') {
		&General::log("Dial-on-Demand waiting to dial $pppsettings{'PROFILENAME'}.");
	} else {
		&General::log("Dialling $pppsettings{'PROFILENAME'}.");
	}

	if ($pppsettings{'TYPE'} eq 'modem') 			{ &domodemdial(); }
	elsif ($pppsettings{'TYPE'} eq 'serial')		{ &doserialdial(); }
	elsif ($pppsettings{'TYPE'} eq 'isdn') 			{ &doisdndial(); }
	elsif ($pppsettings{'TYPE'} eq 'pppoe') 		{ &dopppoedial(); }
	elsif ($pppsettings{'TYPE'} eq 'pptp') 			{ &dopptpdial(); }
	elsif ($pppsettings{'TYPE'} eq 'alcatelusbk') 		{ &doalcatelusbkdial(); }
	elsif ($pppsettings{'TYPE'} eq 'alcatelusb') 		{ &doalcatelusbdial(); }
	elsif ($pppsettings{'TYPE'} eq 'pulsardsl') 		{ &dopulsardsldial(); }
	elsif ($pppsettings{'TYPE'} eq 'eciadsl') 		{ &doeciadsldial(); }
	elsif ($pppsettings{'TYPE'} eq 'fritzdsl') 		{ &dofritzdsldial(); }
	elsif ($pppsettings{'TYPE'} eq 'bewanadsl') 		{ &dobewanadsldial(); }
	elsif ($pppsettings{'TYPE'} eq 'eagleusbadsl') 		{ &doeagleusbadsldial(); }
	elsif ($pppsettings{'TYPE'} eq 'conexantusbadsl') 	{ &doconexantusbadsldial(); }
	elsif ($pppsettings{'TYPE'} eq 'conexantpciadsl') 	{ &doconexantpciadsldial(); }
	elsif ($pppsettings{'TYPE'} eq 'amedynusbadsl') 	{ &doamedynusbadsldial(); }
	elsif ($pppsettings{'TYPE'} eq '3cp4218usbadsl') 	{ &do3cp4218usbadsldial(); }

	if (-e "${General::swroot}/ppp/updatesettings") {
		# erase update mark only after specific script had run, allowing specific script to treat the update
		unlink ("${General::swroot}/ppp/updatesettings");
	}
	if ( ($pppsettings{'RECONNECTION'} eq 'dialondemand') || ($pppsettings{'METHOD'} eq 'STATIC') ){
		system ("/etc/rc.d/rc.updatered");
	}
}
elsif ($ARGV[0] eq 'stop')
{
	if (open(IFACE, "${General::swroot}/red/iface")) {
		$iface = <IFACE>;
		close IFACE;
		chomp ($iface);
		$iface =~ /([a-zA-Z0-9]*)/; $iface = $1;
	}

	my $device;
	if (open(FILE, "${General::swroot}/red/device")) {
		$device = <FILE>;
		close FILE;
		chomp ($device);
		$device =~ /([a-zA-Z0-9]*)/; $device = $1;
	}

	unlink "${General::swroot}/red/dial-on-demand";
	unlink "${General::swroot}/red/active";
	unlink "${General::swroot}/red/local-ipaddress";
	unlink "${General::swroot}/red/remote-ipaddress";
	unlink "${General::swroot}/red/dns1";
	unlink "${General::swroot}/red/dns2";
	unlink "${General::swroot}/red/resolv.conf";
	unlink "${General::swroot}/red/device";

	# stay with keepconnected during transitional rc.red stop ordered by rc.connectioncheck
	if ( ! -e "${General::swroot}/red/redial") {
		unlink "${General::swroot}/red/keepconnected";
	}
	unlink "${General::swroot}/red/redial";

	# Kill PPPD
	if (open(FILE, "/var/run/ppp-ipcop.pid")) {
		my $pid = <FILE>;
		close FILE;
		chomp ($pid);
		$pid =~ /(\d*)/; $pid = $1;
		system ('/bin/kill', $pid);
	}

	# Bring down Ethernet interfaces & Kill DHCPC daemons
	if (($netsettings{'CONFIG_TYPE'} =~ /^(2|3|6|7)$/) && ( $netsettings{'RED_TYPE'} eq 'PPPOE') && $iface ) {
		system ("/sbin/ifconfig", $iface, "down");
	}
	if ($device) {
		system ("/sbin/ifconfig", $device, "down");
	}

	my $file;
	while (($file = glob("${General::swroot}/dhcpc/dhcpcd-*.pid") )) {
		if (open(FILE, $file)) {
			my $pid = <FILE>;
			close FILE;
			chomp ($pid);
			$pid =~ /(\d*)/; $pid = $1;
			system ('/bin/kill', $pid);
		}
	}

	if (!system ('/bin/ps -ef | /bin/grep -q [a]tmarpd')) {
		if ($pppsettings{'GATEWAY'} ne '') {
			system("/usr/sbin/atmarp -d $pppsettings{'GATEWAY'} 2>/dev/null"); }
		system('/bin/killall /usr/sbin/atmarpd 2>/dev/null');
		system ('/sbin/ifconfig', 'atm0', 'down');
	}

	if ($pppsettings{'TYPE'} eq 'isdn') 		{ system('/etc/rc.d/rc.isdn','stop'); }
	if ($pppsettings{'TYPE'} eq 'eciadsl') 		{ system('/etc/rc.d/rc.eciadsl', 'stop'); }
	if ($pppsettings{'TYPE'} eq 'alcatelusbk') 	{ system('/etc/rc.d/rc.alcatelusbk', 'stop'); }
	if ($pppsettings{'TYPE'} eq 'alcatelusb') 	{ system('/etc/rc.d/rc.alcatelusb', 'stop'); }
	if ($pppsettings{'TYPE'} eq 'amedynusbadsl') 	{ system('/etc/rc.d/rc.amedynusbadsl', 'stop'); }
	if ($pppsettings{'TYPE'} eq 'bewanadsl') 	{ system('/etc/rc.d/rc.bewanadsl', 'stop'); }
	if ($pppsettings{'TYPE'} eq 'conexantpciadsl') 	{ system('/etc/rc.d/rc.conexantpciadsl', 'stop'); }
	if ($pppsettings{'TYPE'} eq 'conexantusbadsl') 	{ system('/etc/rc.d/rc.conexantusbadsl', 'stop'); }
	if ($pppsettings{'TYPE'} eq 'eagleusbadsl') 	{ system('/etc/rc.d/rc.eagleusbadsl', 'stop'); }
	if ($pppsettings{'TYPE'} eq 'fritzdsl') 	{ system ('/etc/rc.d/rc.fritzdsl','stop'); }
	if ($pppsettings{'TYPE'} eq 'pulsardsl') 	{ system('/etc/rc.d/rc.pulsardsl', 'stop'); }
	if ($pppsettings{'TYPE'} eq '3cp4218usbadsl') 	{ system('/etc/rc.d/rc.3cp4218usbadsl', 'stop'); }

	if ( 	( $netsettings{'CONFIG_TYPE'} =~ /^(2|3|6|7)$/ && $netsettings{'RED_TYPE'} eq 'STATIC') ||
		( $netsettings{'CONFIG_TYPE'} =~ /^(0|1|4|5)$/ && $pppsettings{'PROTOCOL'} eq 'RFC1483' &&
		  $pppsettings{'METHOD'} eq 'STATIC' ) ) {
	    system ("/etc/rc.d/rc.updatered");
	}
}
elsif ($ARGV[0] eq 'clear')
{
	&doupdatesettings();
	&docleanup();
}

exit 0;

sub docleanup
{
	if ($pppsettings{'TYPE'} eq 'alcatelusbk') 	{ system('/etc/rc.d/rc.alcatelusbk', 'cleanup'); }
	if ($pppsettings{'TYPE'} eq 'alcatelusb') 	{ system('/etc/rc.d/rc.alcatelusb', 'cleanup'); }
	if ($pppsettings{'TYPE'} eq 'eciadsl') 		{ system('/etc/rc.d/rc.eciadsl', 'cleanup'); }
	if ($pppsettings{'TYPE'} eq 'pulsardsl') 	{ system('/etc/rc.d/rc.pulsardsl', 'cleanup'); }
	if ($pppsettings{'TYPE'} eq 'fritzdsl') 	{ system ('/etc/rc.d/rc.fritzdsl','cleanup'); }
	if ($pppsettings{'TYPE'} eq 'bewanadsl') 	{ system('/etc/rc.d/rc.bewanadsl', 'cleanup'); }
	if ($pppsettings{'TYPE'} eq 'eagleusbadsl') 	{ system('/etc/rc.d/rc.eagleusbadsl', 'cleanup'); }
	if ($pppsettings{'TYPE'} eq 'conexantusbadsl') 	{ system('/etc/rc.d/rc.conexantusbadsl', 'cleanup'); }
	if ($pppsettings{'TYPE'} eq 'conexantpciadsl') 	{ system('/etc/rc.d/rc.conexantpciadsl', 'cleanup'); }
	if ($pppsettings{'TYPE'} eq 'amedynusbadsl') 	{ system('/etc/rc.d/rc.amedynusbadsl', 'cleanup'); }
	if ($pppsettings{'TYPE'} eq '3cp4218usbadsl') 	{ system('/etc/rc.d/rc.3cp4218usbadsl', 'cleanup'); }
}

sub domodemdial
{
	my @pppcommand = ('/usr/sbin/pppd');
	my $loginscript = '';

	if ($pppsettings{'COMPORT'} =~ /ttyACM/) {
		system ('/sbin/rmmod acm');
		sleep 1;
		system ('/sbin/modprobe acm');
	}

	my $device = "/dev/${pppsettings{'COMPORT'}}";

	if ($pppsettings{'DNS'} eq 'Automatic') {
		 push(@pppcommand, ('usepeerdns')); }

	if ($pppsettings{'AUTH'} eq 'pap') {
		push(@pppcommand, ('-chap'));
	} elsif ($pppsettings{'AUTH'} eq 'chap') {
		push(@pppcommand, ('-pap'));
	} elsif ($pppsettings{'AUTH'} eq 'standard-login-script') {
		$loginscript = 'standardloginscript';
	} elsif ($pppsettings{'AUTH'} eq 'demon-login-script') {
		$loginscript = 'demonloginscript';
	} else {
		$loginscript = $pppsettings{'LOGINSCRIPT'};
	}

	if ($pppsettings{'RECONNECTION'} ne 'persistent') {
		if ($pppsettings{'TIMEOUT'} != 0)
		{
			my $seconds = $pppsettings{'TIMEOUT'} * 60;
			push (@pppcommand, ('idle', $seconds));
		}
		if ($pppsettings{'RECONNECTION'} eq 'dialondemand') {
			push (@pppcommand, ('demand', 'nopersist'));
		}
		push (@pppcommand, 
			('active-filter',
			 'outbound and not icmp[0] == 3 and not tcp[13] & 4 != 0 ' ));
	}

	push (@pppcommand, ('novj', 'novjccomp'));

	push (@pppcommand, ('lock', 'modem', 'crtscts', $device,
		$pppsettings{'DTERATE'}, 'noipdefault',
		'defaultroute', 'user', $pppsettings{'USERNAME'},
		'maxfail', $pppsettings{'MAXRETRIES'}, 'connect',
		'/etc/ppp/dialer'));
	if ($pppsettings{'DEBUG'} eq 'on') {
		push(@pppcommand, ('debug'));
	}

	system @pppcommand;
}

sub doserialdial
{
	my @pppcommand = ('/usr/sbin/pppd');
	my $loginscript = '';

	if ($pppsettings{'COMPORT'} =~ /ttyACM/) {
		system ('/sbin/rmmod acm');
		sleep 1;
		system ('/sbin/modprobe acm');
	}

	my $device = "/dev/${pppsettings{'COMPORT'}}";

	if ($pppsettings{'DNS'} eq 'Automatic') {
		 push(@pppcommand, ('usepeerdns')); }

	if ($pppsettings{'AUTH'} eq 'pap') {
		push(@pppcommand, ('-chap'));
	} elsif ($pppsettings{'AUTH'} eq 'chap') {
		push(@pppcommand, ('-pap'));
	}

	if ($pppsettings{'RECONNECTION'} ne 'persistent') {
		if ($pppsettings{'TIMEOUT'} != 0)
		{
			my $seconds = $pppsettings{'TIMEOUT'} * 60;
			push (@pppcommand, ('idle', $seconds));
		}
		if ($pppsettings{'RECONNECTION'} eq 'dialondemand') {
			push (@pppcommand, ('demand', 'nopersist'));
		}
		push (@pppcommand, 
			('active-filter',
			 'outbound and not icmp[0] == 3 and not tcp[13] & 4 != 0 ' ));
	}

	push (@pppcommand, ('novj', 'novjccomp'));

	push (@pppcommand, ('lock', 'modem', 'crtscts', $device,
		$pppsettings{'DTERATE'}, 'noipdefault',
		'defaultroute', 'user', $pppsettings{'USERNAME'},
		'maxfail', $pppsettings{'MAXRETRIES'}, 'connect',
		'/bin/true'));
	if ($pppsettings{'DEBUG'} eq 'on') {
		push(@pppcommand, ('debug'));
	}

	system @pppcommand;
}

sub doisdndial
{
	my $pppoptions;
	my $seconds;
	my $phone;

	if (system ('/etc/rc.d/rc.isdn', 'start')) {
		&General::log ("ERROR: ISDN module failed to load");
		exit 1;
	}

	$seconds = $pppsettings{'TIMEOUT'} * 60;
	if ($pppsettings{'USEDOV'} eq 'on')
	{
		$phone = 'v' . $pppsettings{'TELEPHONE'};		
	}
	else
	{
		$phone = $pppsettings{'TELEPHONE'};		
	};

	if ($pppsettings{'COMPORT'} eq 'isdn2')
	{
		system('/usr/sbin/isdnctrl','addif','ippp0');
		system('/usr/sbin/isdnctrl','addslave','ippp0','ippp1');
		system('/usr/sbin/isdnctrl','l2_prot','ippp0','hdlc');
		system('/usr/sbin/isdnctrl','l3_prot','ippp0','trans');
		system('/usr/sbin/isdnctrl','encap','ippp0','syncppp');
		system('/usr/sbin/isdnctrl','dialmax','ippp0',$pppsettings{'MAXRETRIES'});
		system('/usr/sbin/isdnctrl','eaz','ippp0',$isdnsettings{'MSN'});
		system('/usr/sbin/isdnctrl','addphone','ippp0','out',$phone);
		system('/usr/sbin/isdnctrl','huptimeout','ippp0',$seconds);
		system('/usr/sbin/isdnctrl','l2_prot','ippp1','hdlc');
		system('/usr/sbin/isdnctrl','l3_prot','ippp1','trans');
		system('/usr/sbin/isdnctrl','encap','ippp1','syncppp');
		system('/usr/sbin/isdnctrl','dialmax','ippp1',$pppsettings{'MAXRETRIES'});
		system('/usr/sbin/isdnctrl','eaz','ippp0',$isdnsettings{'MSN'});
		system('/usr/sbin/isdnctrl','addphone','ippp1','out',$phone);
		system('/usr/sbin/isdnctrl','huptimeout','ippp1',$seconds);
		system('/usr/sbin/isdnctrl','dialmode','ippp1','auto');

		my @pppcommand = ('/usr/sbin/ipppd','ms-get-dns','noipdefault','+mp',
			'defaultroute','user',$pppsettings{'USERNAME'},
			'name',$pppsettings{'USERNAME'},
			'active-filter','outbound and not icmp[0] == 3 and not tcp[13] & 4 != 0',
			'pidfile','/var/run/ppp-ipcop.pid','/dev/ippp0','/dev/ippp1');
		if ($pppsettings{'DEBUG'} eq 'on') {
			push(@pppcommand, ('debug'));
		}
		if ($pppsettings{'AUTH'} eq 'pap') {
			push(@pppcommand, ('-chap'));
		} elsif ($pppsettings{'AUTH'} eq 'chap') {
			push(@pppcommand, ('-pap'));
		}
		system (@pppcommand);
	}
	else
	{
		system('/usr/sbin/isdnctrl','addif','ippp0');
		system('/usr/sbin/isdnctrl','l2_prot','ippp0','hdlc');
		system('/usr/sbin/isdnctrl','l3_prot','ippp0','trans');
		system('/usr/sbin/isdnctrl','encap','ippp0','syncppp');
		system('/usr/sbin/isdnctrl','dialmax','ippp0',$pppsettings{'MAXRETRIES'});
		system('/usr/sbin/isdnctrl','eaz','ippp0',$isdnsettings{'MSN'});
		system('/usr/sbin/isdnctrl','addphone','ippp0','out',$phone);
		system('/usr/sbin/isdnctrl','huptimeout','ippp0',$seconds);

		my @pppcommand = ('/usr/sbin/ipppd','ms-get-dns','noipdefault',
				'defaultroute','user',$pppsettings{'USERNAME'},
				'name',$pppsettings{'USERNAME'},
				'active-filter','outbound and not icmp[0] == 3 and not tcp[13] & 4 != 0',
				'pidfile','/var/run/ppp-ipcop.pid','/dev/ippp0');
		if ($pppsettings{'DEBUG'} eq 'on') {
			push(@pppcommand, ('debug'));
		}
		if ($pppsettings{'AUTH'} eq 'pap') {
			push(@pppcommand, ('-chap'));
		} elsif ($pppsettings{'AUTH'} eq 'chap') {
			push(@pppcommand, ('-pap'));
		}
		system (@pppcommand);
	}

	sleep 1;

	if ($pppsettings{'RECONNECTION'} eq 'dialondemand') {
		system('/usr/sbin/isdnctrl','dialmode','ippp0','auto');
		system('/sbin/ifconfig','ippp0','10.112.112.112','pointopoint','10.112.112.113');
		system('/sbin/ifconfig','ippp0','-arp','-broadcast');
		system('/sbin/route','add','default','dev','ippp0');
	} else {
		system('/usr/sbin/isdnctrl', 'dial', 'ippp0');

	}

	system('/bin/killall', 'ibod');
	if ($pppsettings{'COMPORT'} eq 'isdn2') {
		if ($pppsettings{'USEIBOD'} eq 'on') {
			system("/usr/sbin/ibod &");
		} else {
			system('/usr/sbin/isdnctrl', 'addlink', 'ippp0');
		}
	}
}

sub dopppoedial
{
	if ($pppsettings{'METHOD'} ne 'PPPOE_PLUGIN') {
		my @pppcommand = ('/usr/sbin/pppd', 'pty');
		my @pppoecommand = ('/usr/sbin/pppoe', '-p','/var/run/pppoe.pid','-I',
			$netsettings{'RED_DEV'}, '-T', '80', '-U', '-m', '1412');
	
		if ($pppsettings{'SERVICENAME'}) {
			push(@pppoecommand, ('-S', $pppsettings{'SERVICENAME'})); }
		if ($pppsettings{'CONCENTRATORNAME'}) {
			push(@pppoecommand, ('-C', $pppsettings{'CONCENTRATORNAME'})); }
	
		push(@pppcommand, "@pppoecommand");
	
		if ($pppsettings{'DNS'} eq 'Automatic') {
			push(@pppcommand, ('usepeerdns'));
		}

		if ($pppsettings{'AUTH'} eq 'pap') {
			push(@pppcommand, ('-chap'));
		} elsif ($pppsettings{'AUTH'} eq 'chap') {
			push(@pppcommand, ('-pap'));
		}

		if ($pppsettings{'RECONNECTION'} ne 'persistent') {
			if ($pppsettings{'TIMEOUT'} != 0) {
				my $seconds = $pppsettings{'TIMEOUT'} * 60;  
				push(@pppcommand, ('idle', "$seconds"));
			}
			if ($pppsettings{'RECONNECTION'} eq 'dialondemand') {
				push (@pppcommand, ('demand','nopersist','connect','/bin/true'));
			}
			push (@pppcommand, 
				('active-filter',
				 'outbound and not icmp[0] == 3 and not tcp[13] & 4 != 0 ' ));
		}
	
		push(@pppcommand, ('noipdefault', 'default-asyncmap',  
			'defaultroute', 'hide-password', 'local',
			'mtu', '1492', 'mru', '1492', 'noaccomp', 'noccp',
			'nobsdcomp', 'nodeflate', 'nopcomp', 'novj', 'novjccomp',
			'user', $pppsettings{'USERNAME'}, 'lcp-echo-interval', '20',
			'lcp-echo-failure', '3', 'lcp-max-configure', '50',
			'maxfail',$pppsettings{'MAXRETRIES'}));
		if ($pppsettings{'DEBUG'} eq 'on') {
			push(@pppcommand, ('debug'));
		}

		system (@pppcommand);
	} else {
		# PPPoE plugin
		system ('/sbin/modprobe pppoe');
		my @pppcommand = ('/usr/sbin/pppd');
		push(@pppcommand,'plugin','rp-pppoe.so',"$netsettings{'RED_DEV'}");
		if ($pppsettings{'DNS'} eq 'Automatic') {
			push(@pppcommand, ('usepeerdns'));
		}
		if ($pppsettings{'AUTH'} eq 'pap') {
			push(@pppcommand, ('-chap'));
		} elsif ($pppsettings{'AUTH'} eq 'chap') {
			push(@pppcommand, ('-pap'));
		}
		if ($pppsettings{'RECONNECTION'} ne 'persistent') {
			if ($pppsettings{'TIMEOUT'} != 0) {
				my $seconds = $pppsettings{'TIMEOUT'} * 60;  
				push(@pppcommand, ('idle', "$seconds"));
			}
			if ($pppsettings{'RECONNECTION'} eq 'dialondemand') {
				push (@pppcommand, ('demand','nopersist'));
			}
			push (@pppcommand, 
				('active-filter',
				'outbound and not icmp[0] == 3 and not tcp[13] & 4 != 0 ' ));
		}
		push(@pppcommand, ('noipdefault', 'defaultroute', 'hide-password', 'ipcp-accept-local',
			'ipcp-accept-remote', 'passive', 'noccp','nopcomp', 'novjccomp',
			'user', $pppsettings{'USERNAME'}, 'lcp-echo-interval', '20',
			'lcp-echo-failure', '3', 'lcp-max-configure', '50', 
			'maxfail',$pppsettings{'MAXRETRIES'}));
		if ($pppsettings{'DEBUG'} eq 'on') {
			push(@pppcommand, ('debug'));
		}

		system (@pppcommand);
	}
}

sub dopptpdial
{
	my %pptpdhcpc;
	my $routerip = $pppsettings{'ROUTERIP'} ? $pppsettings{'ROUTERIP'} : "10.0.0.138";
	if ( $pppsettings{'METHOD'} eq 'DHCP' && open(FILE, "${General::swroot}/red/device")) {
		my $device = <FILE>;
		close FILE;
		chomp ($device);
		$device =~ /([a-zA-Z0-9]*)/; $device = $1;
		if (&General::readhash("${General::swroot}/dhcpc/dhcpcd-$device.info", \%pptpdhcpc)) {
			system("/sbin/route add -host $routerip gw $pptpdhcpc{'GATEWAY'}");
		} else {
			system("/sbin/route add -host $routerip dev $device");
		}
	}

	my @pppcommand = ('/usr/sbin/pppd', 'pty');
	my @pptpcommand = ('/usr/sbin/pptp', $routerip, '--nobuffer', '--nolaunchpppd', '--sync');
	if ($pppsettings{'PHONEBOOK'}) {
		push (@pptpcommand, ('--phone ', $pppsettings{'PHONEBOOK'}));
	}

	push(@pppcommand, "@pptpcommand");

	if ($pppsettings{'DNS'} eq 'Automatic') {
		push(@pppcommand, ('usepeerdns'));
	}
	if ($pppsettings{'AUTH'} eq 'pap') {
		push(@pppcommand, ('-chap'));
	} elsif ($pppsettings{'AUTH'} eq 'chap') {
		push(@pppcommand, ('-pap'));
	}

	if ($pppsettings{'RECONNECTION'} ne 'persistent') {
		if ($pppsettings{'TIMEOUT'} != 0) {
			my $seconds = $pppsettings{'TIMEOUT'} * 60;
			push(@pppcommand, ('idle', "$seconds"));
		}
		if ($pppsettings{'RECONNECTION'} eq 'dialondemand') {
			push (@pppcommand, ('demand','nopersist','connect','/bin/true'));
		}
		push (@pppcommand, 
			('active-filter',
			 'outbound and not icmp[0] == 3 and not tcp[13] & 4 != 0 ' ));
	}

	push(@pppcommand, ('noipdefault', 'default-asyncmap',
		'defaultroute', 'hide-password', 'local','noaccomp', 'noccp',
		'nobsdcomp', 'nodeflate', 'nopcomp', 'novj', 'novjccomp',
		'user', $pppsettings{'USERNAME'}, 'lcp-echo-interval', '20',
		'lcp-echo-failure', '3', 'lcp-max-configure', '50',
		'maxfail',$pppsettings{'MAXRETRIES'},'sync'));
	if ($pppsettings{'DEBUG'} eq 'on') {
		push(@pppcommand, ('debug'));
	}

	system (@pppcommand);
}

sub doalcatelusbdial
{
	if (system ('/etc/rc.d/rc.alcatelusb','start')) {
		&General::log( "ERROR: Failed to connect to Alcatel USB modem");
		exit 1;
	}

	if ($pppsettings{'PROTOCOL'} eq 'RFC1483') { 
		if (open(FILE, ">${General::swroot}/red/device")) { print FILE 'tap0'; close FILE; }
			$netsettings{'RED_DEV'} = 'tap0';
			&dopppoedial();
	} else {
		# PPPoA
		my @pppcommand = ('/usr/sbin/pppd', 'pty');
		my @pppoacommand = ('/usr/sbin/pppoa3','-c','-m','1','-vpi',$pppsettings{'VPI'},'-vci',$pppsettings{'VCI'});
	
		push(@pppcommand, "@pppoacommand");
	
		if ($pppsettings{'DNS'} eq 'Automatic') {
			push(@pppcommand, ('usepeerdns'));
		}
		if ($pppsettings{'AUTH'} eq 'pap') {
			push(@pppcommand, ('-chap'));
		} elsif ($pppsettings{'AUTH'} eq 'chap') {
			push(@pppcommand, ('-pap'));
		}
	
		if ($pppsettings{'RECONNECTION'} ne 'persistent') {
			if ($pppsettings{'TIMEOUT'} != 0) {
				my $seconds = $pppsettings{'TIMEOUT'} * 60;  
				push(@pppcommand, ('idle', "$seconds"));
			}
			if ($pppsettings{'RECONNECTION'} eq 'dialondemand') {
				push (@pppcommand, ('demand','nopersist','connect','/bin/true'));
			}
			push (@pppcommand, 
				('active-filter',
				 'outbound and not icmp[0] == 3 and not tcp[13] & 4 != 0 ' ));
		}
	
		push(@pppcommand, ('noipdefault', 'defaultroute', 'sync', 'user',
			$pppsettings{'USERNAME'}, 'ipcp-accept-local', 'ipcp-accept-remote', 'passive',
			'noaccomp', 'nopcomp', 'noccp', 'novj', 'nobsdcomp',
			'nodeflate', 'lcp-echo-interval', '20', 'lcp-echo-failure', '3', 
			'lcp-max-configure', '50', 'maxfail', $pppsettings{'MAXRETRIES'}));
		if ($pppsettings{'DEBUG'} eq 'on') {
			push(@pppcommand, ('debug'));
		}
	
		system (@pppcommand);
	}
}

sub doeciadsldial
{
	if (system ('/etc/rc.d/rc.eciadsl','start')) {
		&General::log ("ERROR: ECI ADSL failed to start");
		exit 1;
	}
	if ($pppsettings {'PROTOCOL'} eq 'RFC1483') {
		if ($pppsettings {'ENCAP'} =~ /^(0|1)$/) {
			 $iface = "tap0";
		} else {
			 $iface = "tun0";
		}

		if (open(FILE, ">${General::swroot}/red/iface")) { print FILE $iface; close FILE; }

		if ($pppsettings {'METHOD'} =~ /^(PPPOE|PPPOE_PLUGIN)$/) {
			if (open(FILE, ">${General::swroot}/red/device")) { print FILE $iface; close FILE; }
			$netsettings{'RED_DEV'} = $iface;
			&dopppoedial();
		} elsif ($pppsettings{'METHOD'} eq 'STATIC') {
			my @staticcommand = ('/sbin/ifconfig');
			push(@staticcommand, ($iface, $pppsettings{'IP'},'netmask', $pppsettings{'NETMASK'}));
			if ($pppsettings{'BROADCAST'} ne '') {
				push(@staticcommand, ('broadcast', $pppsettings{'BROADCAST'}));
			}
			system (@staticcommand);
			system ("/sbin/route","add","default","gw",$pppsettings{'GATEWAY'});
			system ("/bin/touch", "${General::swroot}/red/active");
			if (open(FILE, ">${General::swroot}/red/iface")) { print FILE $iface; close FILE; }
		} elsif ($pppsettings {'METHOD'} eq 'DHCP') {
			# FIXME dhcp does not support tun0 interface (routed IP)
			dodhcpdial($iface,$pppsettings{'DHCP_HOSTNAME'});
		}
	} else {
		# PPPoA
		my ($VID2, $PID2, $CHIP, $ALTP, $ECIMODE);
		open (MODEMS, "/etc/eciadsl/modems.db") or die 'Unable to open modems database.';
		while (my $line = <MODEMS>) {
			$line =~ s/\s*\t+\s*/|/g;
			$line =~ /^(.+)\|(.+)\|(.+)\|(.+)\|(.+)\|(.+)\|(.+)\|(.+)$/;
			if ( $1 eq $pppsettings{'MODEM'} ) {
				$VID2=$4 ; $PID2=$5; $CHIP=$6; $ALTP=$8;
			}
		}
		close (MODEMS);
		if ( $VID2 eq '') {
			&General::log("$pppsettings{'MODEM'} not found in modems.db");
			exit 1;
		}
		if ( $CHIP eq '' ) {
			&General::log ("error in modems.db reading for $pppsettings{'MODEM'}");
			exit 1;
		}
		if ($pppsettings {'ENCAP'} eq '1') {
			$ECIMODE = "LLC_RFC2364";
		} else {
			$ECIMODE = "VCM_RFC2364";
		}
	
		my @pppcommand = ('/usr/sbin/pppd', 'pty');
		my @pppoecicommand = ("/usr/sbin/eciadsl-pppoeci",'-alt', "$ALTP",'-vpi',$pppsettings{'VPI'},'-vci',$pppsettings{'VCI'},
					'-vendor',"0x$VID2",'-product',"0x$PID2",'-mode',$ECIMODE);
		push(@pppcommand, "@pppoecicommand");
	
		if ($pppsettings{'DNS'} eq 'Automatic') {
			push(@pppcommand, ('usepeerdns'));
		}
		if ($pppsettings{'AUTH'} eq 'pap') {
			push(@pppcommand, ('-chap'));
		} elsif ($pppsettings{'AUTH'} eq 'chap') {
			push(@pppcommand, ('-pap'));
		}
	
		if ($pppsettings{'RECONNECTION'} ne 'persistent') {
			if ($pppsettings{'TIMEOUT'} != 0) {
				my $seconds = $pppsettings{'TIMEOUT'} * 60;  
				push(@pppcommand, ('idle', "$seconds"));
			}
			if ($pppsettings{'RECONNECTION'} eq 'dialondemand') {
				push (@pppcommand, ('demand','nopersist','connect','/bin/true'));
			}
			push (@pppcommand, 
				('active-filter',
				 'outbound and not icmp[0] == 3 and not tcp[13] & 4 != 0 ' ));
		}
	
		push(@pppcommand, ('noipdefault', 'defaultroute', 'sync', 'user',
			$pppsettings{'USERNAME'}, 'ipcp-accept-local', 'ipcp-accept-remote', 'passive',
			'noaccomp', 'nopcomp', 'noccp', 'novj', 'nobsdcomp',
			'nodeflate', 'lcp-echo-interval', '20', 'lcp-echo-failure', '3', 
			'lcp-max-configure', '50', 'maxfail', $pppsettings{'MAXRETRIES'}));
		if ($pppsettings{'DEBUG'} eq 'on') {
			push(@pppcommand, ('debug'));
		}
	
		system (@pppcommand);
	}
}

sub dofritzdsldial
{
	my $controller;

	if (system ('/etc/rc.d/rc.fritzdsl','start')) {
		&General::log ("ERROR: Fritz DSL module failed to load");
		exit 1;
	}

	# controller number
	if ($pppsettings{'TYPE'} eq 'fritzdsl') {
		if ( ! system ('/bin/grep', '1244:2700', '/proc/pci')) {
			$controller=1; # fcdslsl
		} elsif (! system('/bin/grep', '1244:2900', '/proc/pci')) {
			$controller=2; # fcdsl2
		} elsif (! system('/bin/grep', '1131:5402', '/proc/pci')) {
			$controller=2; # fdsl
		} elsif (! system('/bin/grep', 'Vendor=057c ProdID=2300', '/proc/bus/usb/devices')) {
			$controller=1; # fcdslusb
		} elsif (! system('/bin/grep', 'Vendor=057c ProdID=3500', '/proc/bus/usb/devices')) {
			$controller=1; # fcdslslusb
		}
	}
	my @pppcommand = ('/usr/sbin/pppd');
	my @capiplugin;

	if ($pppsettings{'DNS'} eq 'Automatic') {
		push(@pppcommand, ('usepeerdns'));
	}

	if ($pppsettings{'RECONNECTION'} ne 'persistent') {
		if ($pppsettings{'TIMEOUT'} != 0) {
			my $seconds = $pppsettings{'TIMEOUT'} * 60;  
			push(@pppcommand, ('idle', "$seconds"));
		}
		if ($pppsettings{'RECONNECTION'} eq 'dialondemand') {
			push (@pppcommand, ('demand','nopersist','connect','/bin/true'));
		}
		push (@pppcommand, 
			('active-filter',
			 'outbound and not icmp[0] == 3 and not tcp[13] & 4 != 0 ' ));
	}

	push(@pppcommand, ('noipdefault', 'defaultroute', 'sync', 'user', 
		$pppsettings{'USERNAME'}, 'ipcp-accept-local', 'ipcp-accept-remote', 'passive',
		'noaccomp', 'nopcomp', 'noccp', 'novj', 'nobsdcomp',
		'nodeflate', 'lcp-echo-interval', '20', 'lcp-echo-failure', '3', 
		'lcp-max-configure', '50', 'maxfail', $pppsettings{'MAXRETRIES'}));

	if ($pppsettings{'DEBUG'} eq 'on') {
		push(@pppcommand, ('debug'));
	}

	if ($pppsettings {'PROTOCOL'} eq 'RFC1483') {
		@capiplugin = ('plugin', 'capiplugin.so', 'protocol', 'adslpppoe',
			'controller', $controller, 'vpi', $pppsettings{'VPI'},'vci',$pppsettings{'VCI'});
	} else {
		if ($pppsettings {'ENCAP'} eq '1') {
			@capiplugin = ('plugin', 'capiplugin.so', 'protocol', 'adslpppoallc',
				'controller', $controller, 'vpi', $pppsettings{'VPI'},'vci',$pppsettings{'VCI'});
		} else {
			@capiplugin = ('plugin', 'capiplugin.so', 'protocol', 'adslpppoa',
				'controller', $controller,'vpi', $pppsettings{'VPI'},'vci',$pppsettings{'VCI'});
		}
	}
	push(@pppcommand, @capiplugin);
	push(@pppcommand, '/dev/null');

	system (@pppcommand);
}

sub doeagleusbadsldial
{
	if (system ('/etc/rc.d/rc.eagleusbadsl','start')) {
		&General::log ("ERROR: EAGLE-USB ADSL MODEM failed to start");
		exit 1;
	}
	$iface=`/usr/sbin/eaglectrl -i 2>/dev/null | /usr/bin/tr -d '\012'`;
	$iface =~ /([a-zA-Z0-9]*)/; $iface = $1;

	if ($pppsettings {'PROTOCOL'} eq 'RFC1483') {
		if (open(FILE, ">${General::swroot}/red/iface")) { print FILE $iface; close FILE; }
		if ($pppsettings {'METHOD'} =~ /^(PPPOE|PPPOE_PLUGIN)$/) {
			if (open(FILE, ">${General::swroot}/red/device")) { print FILE $iface; close FILE; }
			$netsettings{'RED_DEV'} = $iface;
			&dopppoedial();
		} elsif ($pppsettings{'METHOD'} eq 'STATIC') {
			my @staticcommand = ('/sbin/ifconfig');
			push(@staticcommand, ($iface, $pppsettings{'IP'},'netmask', $pppsettings{'NETMASK'}));
			if ($pppsettings{'BROADCAST'} ne '') {
				push(@staticcommand, ('broadcast', $pppsettings{'BROADCAST'}));
			}
			system (@staticcommand);
			system ("/sbin/route","add","default","gw",$pppsettings{'GATEWAY'});
			system ("/bin/touch", "${General::swroot}/red/active");
		} elsif ($pppsettings {'METHOD'} eq 'DHCP') {
			dodhcpdial($iface,$pppsettings{'DHCP_HOSTNAME'});
		}
	} else {
		# PPPoA
		if (open(FILE, ">${General::swroot}/red/device")) { print FILE $iface; close FILE; }
		$netsettings{'RED_DEV'} = $iface;
		my @pppcommand = ('/usr/sbin/pppd','pty');
		push(@pppcommand,"/usr/sbin/pppoa -I $iface ");
	
		if ($pppsettings{'DNS'} eq 'Automatic') { push(@pppcommand, ('usepeerdns'));}
	
		if ($pppsettings{'AUTH'} eq 'pap') {
			push(@pppcommand, ('-chap'));
		} elsif ($pppsettings{'AUTH'} eq 'chap') {
			push(@pppcommand, ('-pap'));
		}
	
		if ($pppsettings{'RECONNECTION'} ne 'persistent') {
			if ($pppsettings{'TIMEOUT'} != 0) {
				my $seconds = $pppsettings{'TIMEOUT'} * 60;  
				push(@pppcommand, ('idle', "$seconds"));
			}
			if ($pppsettings{'RECONNECTION'} eq 'dialondemand') {
				push (@pppcommand, ('demand','nopersist','connect','/bin/true'));
			}
			push (@pppcommand, 
				('active-filter',
				 'outbound and not icmp[0] == 3 and not tcp[13] & 4 != 0 ' ));
		}
		push(@pppcommand, ('noipdefault', 'defaultroute', 'user', 
			$pppsettings{'USERNAME'}, 'ipcp-accept-local', 'ipcp-accept-remote', 'passive',
			'noaccomp', 'nopcomp', 'noccp', 'novj', 'nobsdcomp',
			'nodeflate', 'lcp-echo-interval', '20', 'lcp-echo-failure', '3', 
			'lcp-max-configure', '50', 'maxfail', $pppsettings{'MAXRETRIES'}));
	
		if ($pppsettings{'DEBUG'} eq 'on') {
			push(@pppcommand, ('debug'));
		}
	
		system (@pppcommand);
	}
}

sub dopulsardsldial
{
	if (system ('/etc/rc.d/rc.pulsardsl','start')) {
		&General::log ("ERROR: PULSAR ADSL modem failed to start");
		exit 1;
	}
	doatmdial();
}

sub dobewanadsldial
{
	if (system ('/etc/rc.d/rc.bewanadsl','start')) {
		&General::log ("ERROR: Bewan ADSL MODEM failed to start");
		exit 1;
	}
	doatmdial();
}

sub doalcatelusbkdial
{
	if (system ('/etc/rc.d/rc.alcatelusbk','start')) {
		&General::log ("ERROR: Alcatel USB kernel mode driver failed to start");
		exit 1;
	}
	doatmdial();
}

sub doconexantusbadsldial
{
	if (system ('/etc/rc.d/rc.conexantusbadsl','start')) {
		&General::log ("ERROR: Conexant USB ADSL modem failed to start");
		exit 1;
	}
	doatmdial();

}

sub doconexantpciadsldial
{
	if (system ('/etc/rc.d/rc.conexantpciadsl','start')) {
		&General::log ("ERROR: Conexant PCI ADSL modem failed to start");
		exit 1;
	}
	doatmdial();

}

sub doamedynusbadsldial
{
	if (system ('/etc/rc.d/rc.amedynusbadsl','start')) {
		&General::log ("ERROR: Zyxel 630-11/Asus AAM6000UG USB ADSL modem failed to start");
		exit 1;
	}
	doatmdial();

}

sub do3cp4218usbadsldial
{
	if (system ('/etc/rc.d/rc.3cp4218usbadsl','start')) {
		&General::log ("ERROR: 3Com USB AccessRunner modem failed to start");
		exit 1;
	}
	doatmdial();
}

sub doatmdial
{
	my $ENCAP;
	if ($pppsettings {'PROTOCOL'} eq 'RFC2364') {
		system ('/sbin/modprobe pppoatm');
		my @pppcommand = ('/usr/sbin/pppd');
		if ($pppsettings{'ENCAP'} eq '0') { $ENCAP='vc-encaps'; } else { $ENCAP='llc-encaps'; }
		push(@pppcommand,'plugin', 'pppoatm.so',$pppsettings{'VPI'}.".".$pppsettings{'VCI'},"$ENCAP");
		if ($pppsettings{'DNS'} eq 'Automatic') { push(@pppcommand, ('usepeerdns'));}
		if ($pppsettings{'AUTH'} eq 'pap') {
			push(@pppcommand, ('-chap'));
		} elsif ($pppsettings{'AUTH'} eq 'chap') {
			push(@pppcommand, ('-pap'));
		}
		if ($pppsettings{'RECONNECTION'} ne 'persistent') {
			if ($pppsettings{'TIMEOUT'} != 0) {
				my $seconds = $pppsettings{'TIMEOUT'} * 60;
				push(@pppcommand, ('idle', "$seconds"));
			}
			if ($pppsettings{'RECONNECTION'} eq 'dialondemand') {
				push (@pppcommand, ('demand','nopersist'));
			}
			push (@pppcommand, 
				('active-filter',
				'outbound and not icmp[0] == 3 and not tcp[13] & 4 != 0 ' ));
		}
		push(@pppcommand, ('noipdefault', 'defaultroute', 'user', 
			$pppsettings{'USERNAME'}, 'ipcp-accept-local', 'ipcp-accept-remote', 'passive',
			 'nopcomp', 'noccp', 'novj', 'nobsdcomp',
			'nodeflate', 'lcp-echo-interval', '20', 'lcp-echo-failure', '3', 
			'lcp-max-configure', '50', 'maxfail', $pppsettings{'MAXRETRIES'}));

		if ($pppsettings{'DEBUG'} eq 'on') {
			push(@pppcommand, ('debug'));
		}

		system (@pppcommand);
	} elsif ($pppsettings {'PROTOCOL'} eq 'RFC1483') {
		if ($pppsettings {'METHOD'} =~ /^(PPPOE|PPPOE_PLUGIN)$/) {
			my $itf='0';
			my $device = "nas$itf";
			if (open(FILE, ">${General::swroot}/red/device")) { print FILE $device; close FILE; }
			$netsettings{'RED_DEV'} = $device;
			if (system ('/bin/ps -ef | /bin/grep -q [b]r2684ctl')) {
				system ('/sbin/modprobe br2684');
				system ('/usr/bin/br2684ctl', '-b', '-c', "$itf", '-e', $pppsettings{'ENCAP'}, '-a', "$itf.$pppsettings{'VPI'}.$pppsettings{'VCI'}");
				sleep 3;
			}
			system ('/sbin/ifconfig',"$device",'up');
			&dopppoedial();
		} elsif ($pppsettings{'ENCAP'} =~ /^(0|1)$/) {
			my $itf='0';
			$iface = "nas$itf";
			if (open(FILE, ">${General::swroot}/red/iface")) { print FILE $iface; close FILE; }
			if (system ('/bin/ps -ef | /bin/grep -q [b]r2684ctl')) {
				system ('/sbin/modprobe br2684');
				system ('/usr/bin/br2684ctl', '-b', '-c', "$itf", '-e', $pppsettings{'ENCAP'}, '-a', "$itf.$pppsettings{'VPI'}.$pppsettings{'VCI'}");
				sleep 3;
			}
			system ('/sbin/ifconfig',"$iface",'up');

			if ($pppsettings{'METHOD'} eq 'STATIC') {
				my @staticcommand = ('/sbin/ifconfig');
				push(@staticcommand, ($iface, $pppsettings{'IP'},'netmask', $pppsettings{'NETMASK'}));
				if ($pppsettings{'BROADCAST'} ne '') {
					push(@staticcommand, ('broadcast', $pppsettings{'BROADCAST'}));
				}
				system (@staticcommand);
				system ("/sbin/route","add","default","gw",$pppsettings{'GATEWAY'});
				system ("/bin/touch", "${General::swroot}/red/active");
				system ("/etc/rc.d/rc.updatered");
			} elsif ($pppsettings {'METHOD'} eq 'DHCP') {
				dodhcpdial($iface,$pppsettings{'DHCP_HOSTNAME'});
			}
		} elsif ($pppsettings{'ENCAP'} =~ /^(2|3)$/) {
			my $itf='0';
			$iface = "atm$itf";
			if (open(FILE, ">${General::swroot}/red/iface")) { print FILE $iface; close FILE; }
			if (system ('/bin/ps -ef | /bin/grep -q [a]tmarpd')) {
				if (system ('/usr/sbin/atmarpd -b -l syslog')) {
					&General::log('atmarpd fail');
					exit 1;
				}
				# it will fail on all attempt after the first because interface still exist
				system ("/usr/sbin/atmarp -c $iface 2>/dev/null");
				
				if ($pppsettings{'METHOD'} eq 'STATIC') {
					my @staticcommand = ('/sbin/ifconfig');
					push(@staticcommand, ($iface, $pppsettings{'IP'},'netmask', $pppsettings{'NETMASK'}, 'up'));
					if ($pppsettings{'BROADCAST'} ne '') {
						push(@staticcommand, ('broadcast', $pppsettings{'BROADCAST'}));
					}
					system (@staticcommand);
					# we have to wait a bit before launching atmarp -s
					sleep 2;
					my @atmarp = ('/usr/sbin/atmarp', '-s', $pppsettings{'GATEWAY'}, "$itf.$pppsettings{'VPI'}.$pppsettings{'VCI'}");
					if ($pppsettings{'ENCAP'} eq '3') {
						push(@atmarp, 'null' ); # routed ip vc encap
					}
					system (@atmarp);
					system ("/sbin/route", "add", "default", "gw", $pppsettings{'GATEWAY'});
					system ("/bin/touch", "${General::swroot}/red/active");
				}
			}
		}
	}
}
