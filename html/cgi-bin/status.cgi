#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
#

use strict;

# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::colourred} );
undef (@dummy);

my %netsettings=();
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

my %cgiparams=();
# Maps a nice printable name to the changing part of the pid file, which
# is also the name of the program
my %servicenames =
(
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

my $iface = '';
if (open(FILE, "${General::swroot}/red/iface"))
{
        $iface = <FILE>;
        close FILE;
        chomp $iface;
}
$servicenames{"$Lang::tr{'intrusion detection system'} (RED)"}   = "snort_${iface}";
$servicenames{"$Lang::tr{'intrusion detection system'} (GREEN)"} = "snort_$netsettings{'GREEN_DEV'}";
if ($netsettings{'ORANGE_DEV'} ne '') {
        $servicenames{"$Lang::tr{'intrusion detection system'} (ORANGE)"} = "snort_$netsettings{'ORANGE_DEV'}";
}
if ($netsettings{'BLUE_DEV'} ne '') {
        $servicenames{"$Lang::tr{'intrusion detection system'} (BLUE)"} = "snort_$netsettings{'BLUE_DEV'}";
}

my %dhcpsettings=();
my %netsettings=();
my %dhcpinfo=();
my %pppsettings=();
my $output='';

&General::readhash("${General::swroot}/dhcp/settings", \%dhcpsettings);
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
&General::readhash("${General::swroot}/ppp/settings", \%pppsettings);

&Header::showhttpheaders();

&Header::getcgihash(\%cgiparams);

&Header::openpage($Lang::tr{'status information'}, 1, '');

&Header::openbigbox('100%', 'left');

&Header::openbox('100%', 'left', $Lang::tr{'services'});

print <<END
<div align='center'>
<table width='60%' cellspacing='0' border='0'>
END
;

my $lines = 0;
my $key = '';
foreach $key (sort keys %servicenames)
{
        if ($lines % 2) {
                print "<tr bgcolor='${Header::table1colour}'>\n"; }
        else {
                print "<tr bgcolor='${Header::table2colour}'>\n"; }
        print "<td align='left'>$key</td>\n";
        my $shortname = $servicenames{$key};
        my $status = &isrunning($shortname);
        print "$status\n";
        print "</tr>\n";
        $lines++;
}


print "</table></div>\n";

&Header::closebox();

&Header::openbox('100%', 'center', $Lang::tr{'memory'});
print "<table><tr><td><table>";
my $ram=0;
my $size=0;
my $used=0;
my $free=0;
my $percent=0;
my $shared=0;
my $buffers=0;
my $cached=0;
open(FREE,'/usr/bin/free |');
while(<FREE>)
{
        if ($_ =~ m/^\s+total\s+used\s+free\s+shared\s+buffers\s+cached$/ )
        {
    print <<END
<tr>
<td>&nbsp;</td>
<td align='center' class='boldbase'><b>$Lang::tr{'size'}</b></td>
<td align='center' class='boldbase'><b>$Lang::tr{'used'}</b></td>
<td align='center' class='boldbase'><b>$Lang::tr{'free'}</b></td>
<td align='left' class='boldbase' colspan='2'><b>$Lang::tr{'percentage'}</b></td>
</tr>
END
;
  } else {
    if ($_ =~ m/^Mem:\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)$/) {
      ($ram,$size,$used,$free,$shared,$buffers,$cached) = ($1,$1,$2,$3,$4,$5,$6);
      ($percent = ($used/$size)*100) =~ s/^(\d+)(\.\d+)?$/$1%/;
      print <<END
<tr>
<td class='boldbase'><b>$Lang::tr{'ram'}</b></td>
<td align='right'>$size</td>
END
;
    } elsif ($_ =~ m/^Swap:\s+(\d+)\s+(\d+)\s+(\d+)$/) {
      ($size,$used,$free) = ($1,$2,$3);
      if ($size != 0)
      {
        ($percent = ($used/$size)*100) =~ s/^(\d+)(\.\d+)?$/$1%/;
      } else {
        ($percent = '');
      }
      print <<END
<tr>
<td class='boldbase'><b>$Lang::tr{'swap'}</b></td>
<td align='right'>$size</td>
END
;
    } elsif ($ram and $_ =~ m/^-\/\+ buffers\/cache:\s+(\d+)\s+(\d+)$/ ) {
      ($used,$free) = ($1,$2);
      ($percent = ($used/$ram)*100) =~ s/^(\d+)(\.\d+)?$/$1%/;
      print "<tr><td colspan='2' class='boldbase'><b>$Lang::tr{'excluding buffers and cache'}</b></td>"
    }
    print <<END
<td align='right'>$used</td>
<td align='right'>$free</td>
<td>
END
;
    &percentbar($percent);
    print <<END
</td>
<td align='right'>$percent</td>
</tr>
END
;
  }
}
close FREE;
print <<END
</table></td><td>
<table>
<tr><td class='boldbase'><b>$Lang::tr{'shared'}</b></td><td align='right'>$shared</td></tr>
<tr><td class='boldbase'><b>$Lang::tr{'buffers'}</b></td><td align='right'>$buffers</td></tr>
<tr><td class='boldbase'><b>$Lang::tr{'cached'}</b></td><td align='right'>$cached</td></tr>
</table>
</td></tr></table>
END
;
&Header::closebox();

&Header::openbox('100%', 'center', $Lang::tr{'disk usage'});
print "<table width=66%>\n";
open(DF,'/bin/df -B M -x rootfs|');
while(<DF>)
{
        if ($_ =~ m/^Filesystem/ )
        {
                print <<END
<tr>
<td align='left' class='boldbase'><b>$Lang::tr{'device'}</b></td>
<td align='left' class='boldbase'><b>$Lang::tr{'mounted on'}</b></td>
<td align='center' class='boldbase'><b>$Lang::tr{'size'}</b></td>
<td align='center' class='boldbase'><b>$Lang::tr{'used'}</b></td>
<td align='center' class='boldbase'><b>$Lang::tr{'free'}</b></td>
<td align='left' class='boldbase' colspan='2'><b>$Lang::tr{'percentage'}</b></td>
</tr>
END
;
        }
        else
        {
                my ($device,$size,$used,$free,$percent,$mount) = split;
                print <<END
<tr>
<td>$device</td>
<td>$mount</td>
<td align='right'>$size</td>
<td align='right'>$used</td>
<td align='right'>$free</td>
<td>
END
;
                &percentbar($percent);
                print <<END
</td>
<td align='right'>$percent</td>
</tr>
END
;
        }
}
close DF;
print "<tr><td colspan='6'>&nbsp;\n<tr><td colspan='6'><h2>Inodes</h2>\n";

open(DF,'/bin/df -i -x rootfs|');
while(<DF>)
{
   if ($_ =~ m/^Filesystem/ )
   {
      print <<END
<tr>
<td align='left' class='boldbase'><b>$Lang::tr{'device'}</b></td>
<td align='left' class='boldbase'><b>$Lang::tr{'mounted on'}</b></td>
<td align='center' class='boldbase'><b>$Lang::tr{'size'}</b></td>
<td align='center' class='boldbase'><b>$Lang::tr{'used'}</b></td>
<td align='center' class='boldbase'><b>$Lang::tr{'free'}</b></td>
<td align='left' class='boldbase' colspan='2'><b>$Lang::tr{'percentage'}</b></td>
</tr>
END
;
   }
   else
   {
      my ($device,$size,$used,$free,$percent,$mount) = split;
      print <<END
<tr>
<td>$device</td>
<td>$mount</td>
<td align='right'>$size</td>
<td align='right'>$used</td>
<td align='right'>$free</td>
<td>
END
;
      &percentbar($percent);
      print <<END
</td>
<td align='right'>$percent</td>
</tr>
END
;
   }
}
close DF;
print "</table>\n";
&Header::closebox();

&Header::openbox('100%', 'left', $Lang::tr{'interfaces'});
$output = `/sbin/ip link show`;
$output = &Header::cleanhtml($output,"y");

my @itfs = ('ORANGE','BLUE','GREEN');
foreach my $itf (@itfs) {
    my $ColorName='';
    my $lc_itf=lc($itf);
    my $dev = $netsettings{"${itf}_DEV"};
    if ($dev){
	$ColorName = "${lc_itf}"; #dereference variable name...
	$output =~ s/$dev/<b><font color="$ColorName">$dev<\/font><\/b>/ ;
    }
}

if (open(REDIFACE, "${General::swroot}/red/iface")) {
    my $lc_itf='red';
    my $reddev = <REDIFACE>;
    close(REDIFACE);
    chomp $reddev;
    $output =~ s/$reddev/<b><font color='red'>${reddev}<\/font><\/b>/;
}
print "<pre>$output</pre>\n";
&Header::closebox();


if ( $netsettings{'CONFIG_TYPE'} =~ /^(2|3|6|7)$/  && $netsettings{'RED_TYPE'} eq "DHCP") {

	&Header::openbox('100%', 'left', "RED $Lang::tr{'dhcp configuration'}");
	if (-s "${General::swroot}/dhcpc/dhcpcd-$netsettings{'RED_DEV'}.info") {

		&General::readhash("${General::swroot}/dhcpc/dhcpcd-$netsettings{'RED_DEV'}.info", \%dhcpinfo);

		my $DNS1=`echo $dhcpinfo{'DNS'} | cut -f 1 -d ,`;
		my $DNS2=`echo $dhcpinfo{'DNS'} | cut -f 2 -d ,`;

		my $lsetme=0;
		my $leasetime="";
		if ($dhcpinfo{'LEASETIME'} ne "") {
			$lsetme=$dhcpinfo{'LEASETIME'};
			$lsetme=($lsetme/60);
			if ($lsetme > 59) {
				$lsetme=($lsetme/60); $leasetime=$lsetme." Hour";
			} else {
			$leasetime=$lsetme." Minute"; 
			}
			if ($lsetme > 1) {
				$leasetime=$leasetime."s";
			}
		}
		my $rentme=0;
		my $rnwltime="";
		if ($dhcpinfo{'RENEWALTIME'} ne "") {
			$rentme=$dhcpinfo{'RENEWALTIME'};
			$rentme=($rentme/60);
			if ($rentme > 59){
				$rentme=($rentme/60); $rnwltime=$rentme." Hour";
			} else {
				$rnwltime=$rentme." Minute";
			}
			if ($rentme > 1){
				$rnwltime=$rnwltime."s";
			}
		}
		my $maxtme=0;
		my $maxtime="";
		if ($dhcpinfo{'REBINDTIME'} ne "") {
			$maxtme=$dhcpinfo{'REBINDTIME'};
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

		print "<table width='100%'>";
		if ($dhcpinfo{'HOSTNAME'}) {
			print "<tr><td width='30%'>$Lang::tr{'hostname'}</td><td>$dhcpinfo{'HOSTNAME'}.$dhcpinfo{'DOMAIN'}</td></tr>\n";
		} else {
			print "<tr><td width='30%'>$Lang::tr{'domain'}</td><td>$dhcpinfo{'DOMAIN'}</td></tr>\n";
		}
		print <<END
	<tr><td>$Lang::tr{'gateway'}</td><td>$dhcpinfo{'GATEWAY'}</td></tr>
	<tr><td>$Lang::tr{'primary dns'}</td><td>$DNS1</td></tr>
	<tr><td>$Lang::tr{'secondary dns'}</td><td>$DNS2</td></tr>
	<tr><td>$Lang::tr{'dhcp server'}</td><td>$dhcpinfo{'DHCPSIADDR'}</td></tr>
	<tr><td>$Lang::tr{'def lease time'}</td><td>$leasetime</td></tr>
	<tr><td>$Lang::tr{'default renewal time'}</td><td>$rnwltime</td></tr>
	<tr><td>$Lang::tr{'max renewal time'}</td><td>$maxtime</td></tr>
    </table>
END
    ;
	}
	else
	{
		print "$Lang::tr{'no dhcp lease'}";
	}
	&Header::closebox();
}

if ($dhcpsettings{'ENABLE_GREEN'} eq 'on' || $dhcpsettings{'ENABLE_BLUE'} eq 'on') {
	&Header::CheckSortOrder;
	&Header::PrintActualLeases;
}

&Header::openbox('100%', 'left', $Lang::tr{'routing table entries'});
$output = `/sbin/ip route show`;
$output = &Header::cleanhtml($output,"y");
print "<pre>$output</pre>\n";
&Header::closebox();

&Header::openbox('100%', 'left', $Lang::tr{'arp table entries'});
$output = `/sbin/ip neigh show`;
$output = &Header::cleanhtml($output,"y");
print "<pre>$output</pre>\n";
&Header::closebox();

&Header::openbox('100%', 'left', $Lang::tr{'loaded modules'});
my $module = qx(/bin/lsmod | awk -F" " '{print \$1}');
my $size = qx(/bin/lsmod | awk -F" " '{print \$2}');
my $used = qx(/bin/lsmod | awk -F" " '{print \$3}');
my @usedby = qx(/bin/lsmod | awk -F" " '{print \$4}');
my @usedbyf;
my $usedbyline;

foreach $usedbyline(@usedby)
{
my $laenge = length($usedbyline);

if ( $laenge > 30)
 {
 my $usedbylinef=substr($usedbyline,0,30);
 $usedbyline="$usedbylinef ...\n";
 push(@usedbyf,$usedbyline);
 }
else
 {push(@usedbyf,$usedbyline);}
}
print <<END
<table cellspacing=25><tr>
<td><pre>$module</pre></td>
<td><pre>$size</pre></td>
<td><pre>$used</pre></td>
<td><pre>@usedbyf</pre></td>
</tr></table>
END
;

print "";
&Header::closebox();

&Header::closebigbox();

&Header::closepage();

sub isrunning
{
        my $cmd = $_[0];
        my $status = "<td bgcolor='${Header::colourred}'><font color='white'><b>$Lang::tr{'stopped'}</b></font></td>";
        my $pid = '';
        my $testcmd = '';
        my $exename;

        $cmd =~ /(^[a-z]+)/;
        $exename = $1;

        if (open(FILE, "/var/run/${cmd}.pid"))
        {
                $pid = <FILE>; chomp $pid;
                close FILE;
                if (open(FILE, "/proc/${pid}/status"))
                {
                        while (<FILE>)
                        {
                                if (/^Name:\W+(.*)/) {
                                        $testcmd = $1; }
                        }
                        close FILE;
                        if ($testcmd =~ /$exename/)
                        {
                                $status = "<td bgcolor='${Header::colourgreen}'><font color='white'><b>$Lang::tr{'running'}</b></font></td>";
                        }
                }
        }

        return $status;
}

sub percentbar
{
  my $percent = $_[0];
  my $fg = '#a0a0a0';
  my $bg = '#e2e2e2';

  if ($percent =~ m/^(\d+)%$/ )
  {
    print <<END
<table width='100' border='1' cellspacing='0' cellpadding='0' style='border-width:1px;border-style:solid;border-color:$fg;width:100px;height:10px;'>
<tr>
END
;
    if ($percent eq "100%") {
      print "<td width='100%' bgcolor='$fg' style='background-color:$fg;border-style:solid;border-width:1px;border-color:$bg'>"
    } elsif ($percent eq "0%") {
      print "<td width='100%' bgcolor='$bg' style='background-color:$bg;border-style:solid;border-width:1px;border-color:$bg'>"
    } else {
      print "<td width='$percent' bgcolor='$fg' style='background-color:$fg;border-style:solid;border-width:1px;border-color:$bg'></td><td width='" . (100-$1) . "%' bgcolor='$bg' style='background-color:$bg;border-style:solid;border-width:1px;border-color:$bg'>"
    }
    print <<END
<img src='/images/null.gif' width='1' height='1' alt='' /></td></tr></table>
END
;
  }
}
