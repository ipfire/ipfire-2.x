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

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "${General::swroot}/graphs.pl";

my %color = ();
my %mainsettings = ();
my %netsettings=();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::colourred} );
undef (@dummy);


my %cgiparams=();
# Maps a nice printable name to the changing part of the pid file, which
# is also the name of the program
my %servicenames =(
	$Lang::tr{'dhcp server'} => 'dhcpd',
	$Lang::tr{'web server'} => 'httpd',
	$Lang::tr{'cron server'} => 'fcron',
	$Lang::tr{'dns proxy server'} => 'dnsmasq',
	$Lang::tr{'logging server'} => 'syslogd',
	$Lang::tr{'kernel logging server'} => 'klogd',
	$Lang::tr{'ntp server'} => 'ntpd',
	$Lang::tr{'secure shell server'} => 'sshd',
	$Lang::tr{'vpn'} => 'pluto',
	$Lang::tr{'web proxy'} => 'squid',
	'OpenVPN' => 'openvpn'
);

my %link =(
	$Lang::tr{'dhcp server'} => "<a href=\'dhcp.cgi\'>$Lang::tr{'dhcp server'}</a>",
	$Lang::tr{'web server'} => $Lang::tr{'web server'},
	$Lang::tr{'cron server'} => $Lang::tr{'cron server'},
	$Lang::tr{'dns proxy server'} => $Lang::tr{'dns proxy server'},
	$Lang::tr{'logging server'} => $Lang::tr{'logging server'},
	$Lang::tr{'kernel logging server'} => $Lang::tr{'kernel logging server'},
	$Lang::tr{'ntp server'} => "<a href=\'time.cgi\'>$Lang::tr{'ntp server'}</a>",
	$Lang::tr{'secure shell server'} => "<a href=\'remote.cgi\'>$Lang::tr{'secure shell server'}</a>",
	$Lang::tr{'vpn'} => "<a href=\'vpnmain.cgi\'>$Lang::tr{'vpn'}</a>",
	$Lang::tr{'web proxy'} => "<a href=\'proxy.cgi\'>$Lang::tr{'web proxy'}</a>",
	'OpenVPN' => "<a href=\'ovpnmain.cgi\'>OpenVPN</a>",
	"$Lang::tr{'intrusion detection system'} (GREEN)" => "<a href=\'ids.cgi\'>$Lang::tr{'intrusion detection system'} (GREEN)</a>",
	"$Lang::tr{'intrusion detection system'} (RED)" => "<a href=\'ids.cgi\'>$Lang::tr{'intrusion detection system'} (RED)</a>",
	"$Lang::tr{'intrusion detection system'} (ORANGE)" => "<a href=\'ids.cgi\'>$Lang::tr{'intrusion detection system'} (ORANGE)</a>",
	"$Lang::tr{'intrusion detection system'} (BLUE)" => "<a href=\'ids.cgi\'>$Lang::tr{'intrusion detection system'} (BLUE)</a>"
);

my $lines=0; # Used to count the outputlines to make different bgcolor

my $iface = '';
if (open(FILE, "${General::swroot}/red/iface")){
	$iface = <FILE>;
	close FILE;
	chomp $iface;
}

$servicenames{"$Lang::tr{'intrusion detection system'} (RED)"}   = "snort_${iface}";
$servicenames{"$Lang::tr{'intrusion detection system'} (GREEN)"} = "snort_$netsettings{'GREEN_DEV'}";

if ($netsettings{'ORANGE_DEV'} ne ''){
	$servicenames{"$Lang::tr{'intrusion detection system'} (ORANGE)"} = "snort_$netsettings{'ORANGE_DEV'}";
}
if ($netsettings{'BLUE_DEV'} ne ''){
	$servicenames{"$Lang::tr{'intrusion detection system'} (BLUE)"} = "snort_$netsettings{'BLUE_DEV'}";
}

my @querry = split(/\?/,$ENV{'QUERY_STRING'});
$querry[0] = '' unless defined $querry[0];
$querry[1] = 'hour' unless defined $querry[1];

if ( $querry[0] =~ "processescpu"){
	print "Content-type: image/png\n\n";
	binmode(STDOUT);
	&Graphs::updateprocessescpugraph($querry[1]);
}elsif ( $querry[0] =~ "processesmemory"){
	print "Content-type: image/png\n\n";
	binmode(STDOUT);
	&Graphs::updateprocessesmemorygraph($querry[1]);
}else{
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'status information'}, 1, '');
	&Header::openbigbox('100%', 'left');

	&Header::openbox('100%', 'left', $Lang::tr{'services'});
	print <<END
<div align='center'>
<table width='80%' cellspacing='1' border='0'>
<tr bgcolor='$color{'color20'}'><td align='left'><b>$Lang::tr{'services'}</b></td><td align='center' ><b>$Lang::tr{'status'}</b></td><td align='center'><b>PID</b></td><td align='center'><b>$Lang::tr{'memory'}</b></td></tr>
END
;
	my $key = '';
	foreach $key (sort keys %servicenames){
		$lines++;
		if ($lines % 2){
			print "<tr bgcolor='$color{'color22'}'>\n<td align='left'>";
			print %link->{$key};
			print "</td>\n";
		}else{
			print "<tr bgcolor='$color{'color20'}'>\n<td align='left'>";
			print %link->{$key};
			print "</td>\n";
		}

		my $shortname = $servicenames{$key};
		my $status = &isrunning($shortname);

	 	print "$status\n";
		print "</tr>\n";
	}

	print "</table></div>\n";
	&Header::closebox();

	&Header::openbox('100%', 'left', "Addon - $Lang::tr{services}");
	my $paramstr=$ENV{QUERY_STRING};
	my @param=split(/!/, $paramstr);
	if ($param[1] ne ''){
		system("/usr/local/bin/addonctrl @param[0] @param[1] > /dev/null 2>&1");
	}

	print <<END
<div align='center'>
<table width='80%' cellspacing='1' border='0'>
<tr bgcolor='$color{'color20'}'>
<td align='center'><b>Addon</b></td>
<td align='center'><b>Boot</b></td>
<td align='center' colspan=2><b>$Lang::tr{'action'}</b></td>
<td align='center'><b>$Lang::tr{'status'}</b></td>
<td align='center'><b>PID</b></td>
<td align='center'><b>$Lang::tr{'memory'}</b></td>
</tr>
END
;

	my $lines=0; # Used to count the outputlines to make different bgcolor

	# Generate list of installed addon pak's
	my @pak = `find /opt/pakfire/db/installed/meta-* 2>/dev/null | cut -d"-" -f2`;
	foreach (@pak){
		chomp($_);

		# Check which of the paks are services
		my @svc = `find /etc/init.d/$_ 2>/dev/null | cut -d"/" -f4`;
		foreach (@svc){
			# blacklist some packages
			#
			# alsa has trouble with the volume saving and was not really stopped
			# mdadm should not stopped with webif because this could crash the system
			#
			chomp($_);
			if ( ($_ ne "alsa") && ($_ ne "mdadm") ) {
				$lines++;
				if ($lines % 2){
					print "<tr bgcolor='$color{'color22'}'>";
				}else{
					print "<tr bgcolor='$color{'color20'}'>";
				}
				print "<td align='left'>$_</td> ";
				my $status = isautorun($_);
				print "$status ";
				print "<td align='center'><A HREF=services.cgi?$_!start><img alt='$Lang::tr{'start'}' title='$Lang::tr{'start'}' src='/images/go-up.png' border='0' /></A></td>";
				print "<td align='center'><A HREF=services.cgi?$_!stop><img alt='$Lang::tr{'stop'}' title='$Lang::tr{'stop'}' src='/images/go-down.png' border='0' /></A></td> ";
				my $status = &isrunningaddon($_);
		 		$status =~ s/\\[[0-1]\;[0-9]+m//g;

				chomp($status);
				print "$status";
				print "</tr>";
			}
		}
	}

	print "</table></div>\n";
	&Header::closebox();

	&Header::openbox('100%', 'center', "$Lang::tr{'processes'} $Lang::tr{'graph'}");
	&Graphs::makegraphbox("services.cgi","processescpu","day");
	&Header::closebox();

	&Header::openbox('100%', 'center', "$Lang::tr{'processes'} $Lang::tr{'memory'} $Lang::tr{'graph'}");
	&Graphs::makegraphbox("services.cgi","processesmemory","day");
	&Header::closebox();

	&Header::closebigbox();
	&Header::closepage();
}

sub isautorun{
	my $cmd = $_[0];
	my $status = "<td align='center'></td>";
	my $init = `find /etc/rc.d/rc3.d/S??${cmd} 2>/dev/null`;
	chomp ($init);
	if ($init ne ''){
		$status = "<td align='center'><A HREF=services.cgi?$_!disable><img alt='$Lang::tr{'deactivate'}' title='$Lang::tr{'deactivate'}' src='/images/on.gif' border='0' width='16' height='16' /></A></td>";
	}
	$init = `find /etc/rc.d/rc3.d/off/S??${cmd} 2>/dev/null`;
	chomp ($init);
	if ($init ne ''){
		$status = "<td align='center'><A HREF=services.cgi?$_!enable><img alt='$Lang::tr{'activate'}' title='$Lang::tr{'activate'}' src='/images/off.gif' border='0' width='16' height='16' /></A></td>";
	}

	return $status;
}

sub isrunning{
	my $cmd = $_[0];
	my $status = "<td align='center' bgcolor='${Header::colourred}'><font color='white'><b>$Lang::tr{'stopped'}</b></font></td><td colspan='2'></td>";
	my $pid = '';
	my $testcmd = '';
	my $exename;
	my @memory;

	$cmd =~ /(^[a-z]+)/;
	$exename = $1;

	if (open(FILE, "/var/run/${cmd}.pid")){
		$pid = <FILE>; chomp $pid;
		close FILE;
		if (open(FILE, "/proc/${pid}/status")){
			while (<FILE>){
				if (/^Name:\W+(.*)/) {
					$testcmd = $1;
				}
			}
			close FILE;
		}
		if (open(FILE, "/proc/${pid}/statm")){
				my $temp = <FILE>;
				@memory = split(/ /,$temp);
		}
		close FILE;
		if ($testcmd =~ /$exename/){
			$status = "<td align='center' bgcolor='${Header::colourgreen}'><font color='white'><b>$Lang::tr{'running'}</b></font></td><td align='center'>$pid</td><td align='center'>$memory[0] KB</td>";
		}
	}
	return $status;
}

sub isrunningaddon{
	my $cmd = $_[0];
	my $status = "<td align='center' bgcolor='${Header::colourred}'><font color='white'><b>$Lang::tr{'stopped'}</b></font></td><td colspan='2'></td>";
	my $pid = '';
	my $testcmd = '';
	my $exename;
	my @memory;

	my $testcmd = `/usr/local/bin/addonctrl $_ status 2>/dev/null`;

	if ( $testcmd =~ /is\ running/ && $testcmd !~ /is\ not\ running/){
		$status = "<td align='center' bgcolor='${Header::colourgreen}'><font color='white'><b>$Lang::tr{'running'}</b></font></td>";
		$testcmd =~ s/.* //gi;
		$testcmd =~ s/[a-z_]//gi;
		$testcmd =~ s/\[[0-1]\;[0-9]+//gi;
		$testcmd =~ s/[\(\)\.]//gi;
		$testcmd =~ s/  //gi;
		$testcmd =~ s///gi;

		my @pid = split(/\s/,$testcmd);
		$status .="<td align='center'>$pid[0]</td>";

		my $memory = 0;

		foreach (@pid){
			chomp($_);
			if (open(FILE, "/proc/$_/statm")){
				my $temp = <FILE>;
				@memory = split(/ /,$temp);
			}
			$memory+=$memory[0];
		}
		$status .="<td align='center'>$memory KB</td>";
	}else{
		$status = "<td align='center' bgcolor='${Header::colourred}'><font color='white'><b>$Lang::tr{'stopped'}</b></font></td><td colspan='2'></td>";
	}
	return $status;
}
