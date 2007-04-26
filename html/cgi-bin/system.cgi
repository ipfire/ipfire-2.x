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

&Header::showhttpheaders();

&Header::getcgihash(\%cgiparams);

&Header::openpage($Lang::tr{'status information'}, 1, '');

&Header::openbigbox('100%', 'left');

&Header::openbox('100%', 'center', "CPU $Lang::tr{'graph'}");
if (-e "$Header::graphdir/cpu-day.png") {
	my $ftime = localtime((stat("$Header::graphdir/cpu-day.png"))[9]);
	print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
	print "<a href='/cgi-bin/graphs.cgi?graph=cpu'>";
	print "<img alt='' src='/graphs/cpu-day.png' border='0' />";
	print "</a>";
} else {
	print $Lang::tr{'no information available'};
}
print "<br />\n";
&Header::closebox();

&Header::openbox('100%', 'center', "Load $Lang::tr{'graph'}");
if (-e "$Header::graphdir/load-day.png") {
	my $ftime = localtime((stat("$Header::graphdir/load-day.png"))[9]);
	print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
	print "<a href='/cgi-bin/graphs.cgi?graph=load'>";
	print "<img alt='' src='/graphs/load-day.png' border='0' />";
	print "</a>";
} else {
	print $Lang::tr{'no information available'};
}
print "<br />\n";
&Header::closebox();

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
