#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %dhcpsettings=();
my %netsettings=();
my %dhcpinfo=();
my %pppsettings=();
my $output='';

&General::readhash("${General::swroot}/dhcp/settings", \%dhcpsettings);
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
&General::readhash("${General::swroot}/ppp/settings", \%pppsettings);
&Header::showhttpheaders();
&Header::openpage($Lang::tr{'network status information'}, 1, '');

&Header::openbigbox('100%', 'left');

&Header::openbox('100%', 'left', $Lang::tr{'interfaces'});
$output = `/sbin/ip addr show`;
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

	print "<a name='reddhcp'/>\n";
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

	print "<a name='leases'/>";
	&Header::CheckSortOrder;
	&Header::PrintActualLeases;
}

&Header::openbox('100%', 'left', $Lang::tr{'routing table entries'});
$output = `/sbin/ip show show`;
$output = &Header::cleanhtml($output,"y");
print "<pre>$output</pre>\n";
&Header::closebox();

&Header::openbox('100%', 'left', $Lang::tr{'arp table entries'});
$output = `/sbin/ip neigh show`;
$output = &Header::cleanhtml($output,"y");
print "<pre>$output</pre>\n";
&Header::closebox();

&Header::closebigbox();

&Header::closepage();
