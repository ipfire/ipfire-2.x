#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# $Id: index.cgi,v 1.15.2.18 2005/09/17 13:51:47 gespinasse Exp $
#

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require 'CONFIG_ROOT/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %cgiparams=();
my %pppsettings=();
my %modemsettings=();
my %netsettings=();
my %ddnssettings=();
my $warnmessage = '';
my $refresh = '';

&Header::showhttpheaders();

$cgiparams{'ACTION'} = '';
&Header::getcgihash(\%cgiparams);
$pppsettings{'VALID'} = '';
$pppsettings{'PROFILENAME'} = 'None';
&General::readhash("${General::swroot}/ppp/settings", \%pppsettings);
&General::readhash("${General::swroot}/modem/settings", \%modemsettings);
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
&General::readhash("${General::swroot}/ddns/settings", \%ddnssettings);

my $connstate = &Header::connectionstatus();
if ($connstate =~ /$Lang::tr{'dod waiting'}/ || -e "${General::swroot}/main/refreshindex") {
	$refresh = "<meta http-equiv='refresh' content='30;'>";
} elsif ($connstate =~ /$Lang::tr{'connecting'}/) {
	$refresh = "<meta http-equiv='refresh' content='5;'>";
}

&Header::openpage($Lang::tr{'main page'}, 1, $refresh);
&Header::openbigbox('', 'center');
&Header::openbox('100%', 'center', &Header::cleanhtml(`/bin/uname -n`,"y"));

# hide buttons only when pppsettings mandatory used and not valid
if ( ( $pppsettings{'VALID'} eq 'yes' ) ||
		( $netsettings{'CONFIG_TYPE'} =~ /^(2|3|6|7)$/ && $netsettings{'RED_TYPE'} =~ /^(DHCP|STATIC)$/ ) ) {
	print <<END
	<table border='0'>
	<tr>
		<td align='center'><form method='post' action='/cgi-bin/dial.cgi'>
			<input type='submit' name='ACTION' value='$Lang::tr{'dial'}' />
		</form></td>
		<td>&nbsp;&nbsp;</td>
		<td align='center'><form method='post' action='/cgi-bin/dial.cgi'>
			<input type='submit' name='ACTION' value='$Lang::tr{'hangup'}' />
		</form></td>
		<td>&nbsp;&nbsp;</td>
		<td align='center'><form method='post' action="$ENV{'SCRIPT_NAME'}">
			<input type='submit' name='ACTION' value='$Lang::tr{'refresh'}' />
		</form></td>
	</tr></table>
END
	;
}

print "<font face='Helvetica' size='4'><b>";
if ( !( $netsettings{'CONFIG_TYPE'} =~ /^(2|3|6|7)$/ && $netsettings{'RED_TYPE'} =~ /^(DHCP|STATIC)$/ ) ) {
	print "<u>$Lang::tr{'current profile'} $pppsettings{'PROFILENAME'}</u><br />\n";
}
	
if ( ( $pppsettings{'VALID'} eq 'yes'&& $modemsettings{'VALID'} eq 'yes' ) ||
		( $netsettings{'CONFIG_TYPE'} =~ /^(2|3|6|7)$/ && $netsettings{'RED_TYPE'} =~ /^(DHCP|STATIC)$/ )) {
	print $connstate;
	print "</b></font>\n";
	if ($connstate =~ /$Lang::tr{'connected'}/) {
	    my $fetch_ip='nothing';
	    if ($ddnssettings{'BEHINDROUTER'} eq 'FETCH_IP') {
	        if (open(IPADDR,"${General::swroot}/ddns/ipcache")) {
	   	    $fetch_ip = <IPADDR>;
	    	    close IPADDR;
	    	    chomp ($fetch_ip);
	    	    my $host_name = (gethostbyaddr(pack("C4", split(/\./, $fetch_ip)), 2))[0];
	    	    print "<br />$Lang::tr{'ip address'} (internet): $fetch_ip <br /> $Lang::tr{'ipcops hostname'} (internet): $host_name <br />";
		}
	    }
	    if (open(IPADDR,"${General::swroot}/red/local-ipaddress")) {
	   	my $ipaddr = <IPADDR>;
	    	close IPADDR;
	    	chomp ($ipaddr);
		if ($ipaddr ne $fetch_ip){	#do not show info twice
	    	    my $host_name = (gethostbyaddr(pack("C4", split(/\./, $ipaddr)), 2))[0];
	    	    print "<br />$Lang::tr{'ip address'}: $ipaddr <br /> $Lang::tr{'ipcops hostname'}: $host_name <br />";
		}
	    }
        }

} elsif ($modemsettings{'VALID'} eq 'no') {
	print "$Lang::tr{'modem settings have errors'}\n </b></font>\n";
} else {
	print "$Lang::tr{'profile has errors'}\n </b></font>\n";
}


# Memory usage warning
my @free = `/usr/bin/free`;
$free[1] =~ m/(\d+)/;
my $mem = $1;
$free[2] =~ m/(\d+)/;
my $used = $1;
my $pct = int 100 * ($mem - $used) / $mem;
if ($used / $mem > 90) {
	$warnmessage .= "<li> $Lang::tr{'high memory usage'}: $pct% !</li>\n";
}

# Diskspace usage warning
my @temp=();
my $temp2=();
my @df = `/bin/df -B M -x rootfs`;
foreach my $line (@df) {
	next if $line =~ m/^Filesystem/;
	if ($line =~ m/root/ ) {
		$line =~ m/^.* (\d+)M.*$/;
		@temp = split(/ +/,$line);
		if ($1<5) {
			# available:plain value in MB, and not %used as 10% is too much to waste on small disk
			# and root size should not vary during time
			$warnmessage .= "<li> $Lang::tr{'filesystem full'}: $temp[0] <b>$Lang::tr{'free'}=$1M</b> !</li>\n";
		}
		
	} else {
		# $line =~ m/^.* (\d+)m.*$/;
		$line =~ m/^.* (\d+)\%.*$/;
		if ($1>90) {
			@temp = split(/ /,$line);
			$temp2=int(100-$1);
			$warnmessage .= "<li> $Lang::tr{'filesystem full'}: $temp[0] <b>$Lang::tr{'free'}=$temp2%</b> !</li>\n";
		}
	}
}

# Patches warning
open(AV, "<${General::swroot}/patches/available") or die "Could not open available patches database ($!)";
my @av = <AV>;
close(AV);
open(PF, "<${General::swroot}/patches/installed") or die "Could not open installed patches file. ($!)<br />";
while(<PF>)
{
        next if $_ =~ m/^#/;
        @temp = split(/\|/,$_);
        @av = grep(!/^$temp[0]/, @av);
}
close(PF);

if ($#av != -1) 
{
	$warnmessage .= "<li> $Lang::tr{'there are updates'}</li>";
}
my $age = &General::age("/${General::swroot}/patches/available");
if ($age =~ m/(\d{1,3})d/) {
	if ($1 >= 7) {
		$warnmessage .= "<li>$Lang::tr{'updates is old1'} $age $Lang::tr{'updates is old2'}</li>\n";
	}
}

if ($warnmessage) {
	print "<ol>$warnmessage</ol>";
}

print "<p>";
system('/usr/bin/uptime');
print "</p>\n";

&Header::closebox();

# Test browser, and direct User where to turn off Javascript if necessary
# only display message if Javascript is currently enabled
if (${Header::javascript}) {
print <<END
<script type='text/javascript'>\n
if(navigator.platform.indexOf("MacPPC")>(-1)){
  document.write(
    "<center><p>"
    + "$Lang::tr{'javascript menu error1'}"
    + " <a href='/cgi-bin/gui.cgi'>$Lang::tr{'gui settings'}</a> "
    + "$Lang::tr{'javascript menu error2'}"
    + "</p></center>"
  )
}
</script>
END
;
}

&Header::closebigbox();

&Header::closepage();
