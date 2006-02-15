#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# $Id: status.cgi,v 1.6.2.7 2005/02/24 07:44:35 gespinasse Exp $
#

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require 'CONFIG_ROOT/general-functions.pl';
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
	$Lang::tr{'web proxy'} => 'squid'
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

&Header::showhttpheaders();

&Header::getcgihash(\%cgiparams);

&Header::openpage($Lang::tr{'status information'}, 1, '');

&Header::openbigbox('100%', 'left');

print <<END
<table width='100%' cellspacing='0' cellpadding='5'border='0'>
<tr><td style="background-color: #EAE9EE;" align='left'>
    <a href='#services'>$Lang::tr{'services'}</a> |
    <a href='#memory'>$Lang::tr{'memory'}</a> |
    <a href='#disk'>$Lang::tr{'disk usage'}</a> |
    <a href='#uptime'>$Lang::tr{'uptime and users'}</a> |
    <a href='#modules'>$Lang::tr{'loaded modules'}</a> |
    <a href='#kernel'>$Lang::tr{'kernel version'}</a>
</td></tr></table>
END
;

print "<a name='services'/>\n"; 
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

print "<a name='memory'/>\n";
&Header::openbox('100%', 'left', $Lang::tr{'memory'});
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

print "<a name='disk'/>\n";
&Header::openbox('100%', 'left', $Lang::tr{'disk usage'});
print "<table>\n";
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
print "</table>\n";
&Header::closebox();

print "<a name='uptime'/>\n";
&Header::openbox('100%', 'left', $Lang::tr{'uptime and users'});
my $output = `/usr/bin/w`;
$output = &Header::cleanhtml($output,"y");
print "<pre>$output</pre>\n";
&Header::closebox();

print "<a name='modules'/>\n";
&Header::openbox('100%', 'left', $Lang::tr{'loaded modules'});
$output = qx+/sbin/lsmod+;
($output = &Header::cleanhtml($output,"y")) =~ s/\[.*\]//g;
print "<pre>\n$output\n</pre>\n";
&Header::closebox();

print "<a name='kernel'/>\n";
&Header::openbox('100%', 'left', $Lang::tr{'kernel version'});
print "<pre>\n";
print `/bin/uname -a`;
print "</pre>\n";
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
