#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2013 Alexander Marx <amarx@ipfire.org>                        #
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
use Sort::Naturally;
use utf8;
use feature 'unicode_strings';

no warnings 'uninitialized';

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require '/var/ipfire/network-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "${General::swroot}/geoip-functions.pl";
require "/usr/lib/firewall/firewall-lib.pl";

unless (-d "${General::swroot}/firewall")			{ system("mkdir ${General::swroot}/firewall"); }
unless (-e "${General::swroot}/firewall/settings")	{ system("touch ${General::swroot}/firewall/settings"); }
unless (-e "${General::swroot}/firewall/config")	{ system("touch ${General::swroot}/firewall/config"); }
unless (-e "${General::swroot}/firewall/input")		{ system("touch ${General::swroot}/firewall/input"); }
unless (-e "${General::swroot}/firewall/outgoing")	{ system("touch ${General::swroot}/firewall/outgoing"); }

my %fwdfwsettings=();
my %selected=() ;
my %defaultNetworks=();
my %netsettings=();
my %customhost=();
my %customgrp=();
my %customgeoipgrp=();
my %customnetworks=();
my %customservice=();
my %customservicegrp=();
my %ccdnet=();
my %customnetwork=();
my %ccdhost=();
my %configfwdfw=();
my %configinputfw=();
my %configoutgoingfw=();
my %ipsecconf=();
my %color=();
my %mainsettings=();
my %checked=();
my %icmptypes=();
my %ovpnsettings=();
my %ipsecsettings=();
my %aliases=();
my %optionsfw=();
my %ifaces=();
my %rulehash=();

my @PROTOCOLS = ("TCP", "UDP", "ICMP", "IGMP", "AH", "ESP", "GRE","IPv6","IPIP");

my $color;
my $confignet		= "${General::swroot}/fwhosts/customnetworks";
my $confighost		= "${General::swroot}/fwhosts/customhosts";
my $configgrp 		= "${General::swroot}/fwhosts/customgroups";
my $configgeoipgrp	= "${General::swroot}/fwhosts/customgeoipgrp";
my $configsrv 		= "${General::swroot}/fwhosts/customservices";
my $configsrvgrp	= "${General::swroot}/fwhosts/customservicegrp";
my $configccdnet 	= "${General::swroot}/ovpn/ccd.conf";
my $configccdhost	= "${General::swroot}/ovpn/ovpnconfig";
my $configipsec		= "${General::swroot}/vpn/config";
my $configipsecrw	= "${General::swroot}/vpn/settings";
my $configfwdfw		= "${General::swroot}/firewall/config";
my $configinput		= "${General::swroot}/firewall/input";
my $configoutgoing	= "${General::swroot}/firewall/outgoing";
my $configovpn		= "${General::swroot}/ovpn/settings";
my $fwoptions 		= "${General::swroot}/optionsfw/settings";
my $ifacesettings	= "${General::swroot}/ethernet/settings";
my $errormessage='';
my $hint='';
my $ipgrp="${General::swroot}/outgoing/groups";
my $tdcolor='';
my $checkorange='';
my @protocols;
&General::readhash("${General::swroot}/firewall/settings", \%fwdfwsettings);
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);
&General::readhash($fwoptions, \%optionsfw); 
&General::readhash($ifacesettings, \%ifaces);
&General::readhash("$configovpn", \%ovpnsettings);
&General::readhash("$configipsecrw", \%ipsecsettings);
&General::readhasharray("$configipsec", \%ipsecconf);
&Header::showhttpheaders();
&Header::getcgihash(\%fwdfwsettings);
&Header::openpage($Lang::tr{'firewall rules'}, 1, '');
&Header::openbigbox('100%', 'center',$errormessage);
#### JAVA SCRIPT ####
print<<END;
<script>
	var PROTOCOLS_WITH_PORTS = ["TCP", "UDP"];

	var update_protocol = function() {
		var protocol = \$("#protocol").val();

		if (protocol === undefined)
			return;

		// Check if a template is/should be used.
		if (protocol === "template") {
			\$("#PROTOCOL_TEMPLATE").show();
		} else {
			\$("#PROTOCOL_TEMPLATE").hide();
		}

		// Check if we are dealing with a protocol, that knows ports.
		if (\$.inArray(protocol, PROTOCOLS_WITH_PORTS) >= 0) {
			\$("#PROTOCOL_PORTS").show();
		} else {
			\$("#PROTOCOL_PORTS").hide();
		}

		// Handle ICMP.
		if (protocol === "ICMP") {
			\$("#PROTOCOL_ICMP_TYPES").show();
		} else {
			\$("#PROTOCOL_ICMP_TYPES").hide();
		}
	};

	\$(document).ready(function() {
		\$("#protocol").change(update_protocol);
		update_protocol();

		// Show/Hide elements when NAT checkbox is checked.
		if (\$("#USE_NAT").attr("checked")) {
			\$("#actions").hide();
		} else {
			\$(".NAT").hide();
		}

		// Show NAT area when "use nat" checkbox is clicked
		\$("#USE_NAT").change(function() {
			\$(".NAT").toggle();
			\$("#actions").toggle();
		});

		// Hide SNAT items when DNAT is selected and vice versa.
		if (\$('input[name=nat]:checked').val() == 'dnat') {
			\$('.snat').hide();
		} else {
			\$('.dnat').hide();
		}

		// Show/Hide elements when SNAT/DNAT get changed.
		\$('input[name=nat]').change(function() {
			\$('.snat').toggle();
			\$('.dnat').toggle();
		});

		// Time constraints
		if(!\$("#USE_TIME_CONSTRAINTS").attr("checked")) {
			\$("#TIME_CONSTRAINTS").hide();
		}
		\$("#USE_TIME_CONSTRAINTS").change(function() {
			\$("#TIME_CONSTRAINTS").toggle();
		});

		// Limit concurrent connections per ip
		if(!\$("#USE_LIMIT_CONCURRENT_CONNECTIONS_PER_IP").attr("checked")) {
			\$("#LIMIT_CON").hide();
		}
		\$("#USE_LIMIT_CONCURRENT_CONNECTIONS_PER_IP").change(function() {
			\$("#LIMIT_CON").toggle();
		});

		// Rate-limit new connections
		if(!\$("#USE_RATELIMIT").attr("checked")) {
			\$("#RATELIMIT").hide();
		}
		\$("#USE_RATELIMIT").change(function() {
			\$("#RATELIMIT").toggle();
		});

		// Automatically select radio buttons when corresponding
		// dropdown menu changes.
		\$("select").change(function() {
			var id = \$(this).attr("name");
			\$('#' + id).prop("checked", true);
		});
	});
</script>
END

####  ACTION  #####

if ($fwdfwsettings{'ACTION'} eq 'saverule')
{
	&General::readhasharray("$configfwdfw", \%configfwdfw);
	&General::readhasharray("$configinput", \%configinputfw);
	&General::readhasharray("$configoutgoing", \%configoutgoingfw);
	my $maxkey;
	#Set Variables according to the JQuery code in protocol section
	if ($fwdfwsettings{'PROT'} eq 'TCP' || $fwdfwsettings{'PROT'} eq 'UDP')
	{
		if ($fwdfwsettings{'SRC_PORT'} ne '')
		{
			$fwdfwsettings{'USE_SRC_PORT'} = 'ON';
		}
		if ($fwdfwsettings{'TGT_PORT'} ne '')
		{
			$fwdfwsettings{'USESRV'} = 'ON';
			$fwdfwsettings{'grp3'} = 'TGT_PORT';
		}
	}
	if ($fwdfwsettings{'PROT'} eq 'template')
	{
		$fwdfwsettings{'USESRV'} = 'ON';
	}
	$errormessage=&checksource;
	if(!$errormessage){&checktarget;}
	if(!$errormessage){&checkrule;}

	#check if manual ip (source) is orange network
	if ($fwdfwsettings{'grp1'} eq 'src_addr'){
		my ($sip,$scidr) = split("/",$fwdfwsettings{$fwdfwsettings{'grp1'}});
		if ( &General::IpInSubnet($sip,$netsettings{'ORANGE_ADDRESS'},$netsettings{'ORANGE_NETMASK'})){
			$checkorange='on';
		}
	}
	#check if we try to break rules
	if(	$fwdfwsettings{'grp1'} eq 'ipfire_src' && $fwdfwsettings{'grp2'} eq 'ipfire'){
		$errormessage=$Lang::tr{'fwdfw err same'};
	}
	# INPUT part
	if ($fwdfwsettings{'grp2'} eq 'ipfire' && $fwdfwsettings{$fwdfwsettings{'grp1'}} ne 'ORANGE'){
		$fwdfwsettings{'config'}=$configinput;
		$fwdfwsettings{'chain'} = 'INPUTFW';
		$maxkey=&General::findhasharraykey(\%configinputfw);
		%rulehash=%configinputfw;
	}elsif ($fwdfwsettings{'grp1'} eq 'ipfire_src' ){
	# OUTGOING PART
		$fwdfwsettings{'config'}=$configoutgoing;
		$fwdfwsettings{'chain'} = 'OUTGOINGFW';
		$maxkey=&General::findhasharraykey(\%configoutgoingfw);
		%rulehash=%configoutgoingfw;
	}else {
	# FORWARD PART
		$fwdfwsettings{'config'}=$configfwdfw;
		$fwdfwsettings{'chain'} = 'FORWARDFW';
		$maxkey=&General::findhasharraykey(\%configfwdfw);
		%rulehash=%configfwdfw;
	}
	#check if we have an identical rule already
	if($fwdfwsettings{'oldrulenumber'} eq $fwdfwsettings{'rulepos'}){
		foreach my $key (sort keys %rulehash){
			if (   "$fwdfwsettings{'RULE_ACTION'},$fwdfwsettings{'ACTIVE'},$fwdfwsettings{'grp1'},$fwdfwsettings{$fwdfwsettings{'grp1'}},$fwdfwsettings{'grp2'},$fwdfwsettings{$fwdfwsettings{'grp2'}},$fwdfwsettings{'USE_SRC_PORT'},$fwdfwsettings{'PROT'},$fwdfwsettings{'ICMP_TYPES'},$fwdfwsettings{'SRC_PORT'},$fwdfwsettings{'USESRV'},$fwdfwsettings{'TGT_PROT'},$fwdfwsettings{'ICMP_TGT'},$fwdfwsettings{'grp3'},$fwdfwsettings{$fwdfwsettings{'grp3'}},$fwdfwsettings{'ruleremark'},$fwdfwsettings{'LOG'},$fwdfwsettings{'TIME'},$fwdfwsettings{'TIME_MON'},$fwdfwsettings{'TIME_TUE'},$fwdfwsettings{'TIME_WED'},$fwdfwsettings{'TIME_THU'},$fwdfwsettings{'TIME_FRI'},$fwdfwsettings{'TIME_SAT'},$fwdfwsettings{'TIME_SUN'},$fwdfwsettings{'TIME_FROM'},$fwdfwsettings{'TIME_TO'},$fwdfwsettings{'USE_NAT'},$fwdfwsettings{$fwdfwsettings{'nat'}},$fwdfwsettings{'dnatport'},$fwdfwsettings{'nat'},$fwdfwsettings{'LIMIT_CON_CON'},$fwdfwsettings{'concon'},$fwdfwsettings{'RATE_LIMIT'},$fwdfwsettings{'ratecon'},$fwdfwsettings{'RATETIME'}"
				eq "$rulehash{$key}[0],$rulehash{$key}[2],$rulehash{$key}[3],$rulehash{$key}[4],$rulehash{$key}[5],$rulehash{$key}[6],$rulehash{$key}[7],$rulehash{$key}[8],$rulehash{$key}[9],$rulehash{$key}[10],$rulehash{$key}[11],$rulehash{$key}[12],$rulehash{$key}[13],$rulehash{$key}[14],$rulehash{$key}[15],$rulehash{$key}[16],$rulehash{$key}[17],$rulehash{$key}[18],$rulehash{$key}[19],$rulehash{$key}[20],$rulehash{$key}[21],$rulehash{$key}[22],$rulehash{$key}[23],$rulehash{$key}[24],$rulehash{$key}[25],$rulehash{$key}[26],$rulehash{$key}[27],$rulehash{$key}[28],$rulehash{$key}[29],$rulehash{$key}[30],$rulehash{$key}[31],$rulehash{$key}[32],$rulehash{$key}[33],$rulehash{$key}[34],$rulehash{$key}[35],$rulehash{$key}[36]"){
					$errormessage.=$Lang::tr{'fwdfw err ruleexists'};
					if($fwdfwsettings{'oldruleremark'} ne $fwdfwsettings{'ruleremark'} && $fwdfwsettings{'updatefwrule'} eq 'on' && $fwdfwsettings{'ruleremark'} ne '' && !&validremark($fwdfwsettings{'ruleremark'})){
						$errormessage=$Lang::tr{'fwdfw err remark'}."<br>";
					}
					if($fwdfwsettings{'oldruleremark'} ne $fwdfwsettings{'ruleremark'} && $fwdfwsettings{'updatefwrule'} eq 'on' && $fwdfwsettings{'ruleremark'} ne '' && &validremark($fwdfwsettings{'ruleremark'})){
						$errormessage='';
					}
					if ($fwdfwsettings{'oldruleremark'} eq $fwdfwsettings{'ruleremark'}){
						$fwdfwsettings{'nosave'} = 'on';
					}
			}
		}
	}
	#check Rulepos on new Rule
	if($fwdfwsettings{'rulepos'} > 0 && !$fwdfwsettings{'oldrulenumber'}){
		$fwdfwsettings{'oldrulenumber'}=$maxkey;
		foreach my $key (sort keys %rulehash){
			if (   "$fwdfwsettings{'RULE_ACTION'},$fwdfwsettings{'ACTIVE'},$fwdfwsettings{'grp1'},$fwdfwsettings{$fwdfwsettings{'grp1'}},$fwdfwsettings{'grp2'},$fwdfwsettings{$fwdfwsettings{'grp2'}},$fwdfwsettings{'USE_SRC_PORT'},$fwdfwsettings{'PROT'},$fwdfwsettings{'ICMP_TYPES'},$fwdfwsettings{'SRC_PORT'},$fwdfwsettings{'USESRV'},$fwdfwsettings{'TGT_PROT'},$fwdfwsettings{'ICMP_TGT'},$fwdfwsettings{'grp3'},$fwdfwsettings{$fwdfwsettings{'grp3'}},$fwdfwsettings{'TIME'},$fwdfwsettings{'TIME_MON'},$fwdfwsettings{'TIME_TUE'},$fwdfwsettings{'TIME_WED'},$fwdfwsettings{'TIME_THU'},$fwdfwsettings{'TIME_FRI'},$fwdfwsettings{'TIME_SAT'},$fwdfwsettings{'TIME_SUN'},$fwdfwsettings{'TIME_FROM'},$fwdfwsettings{'TIME_TO'},$fwdfwsettings{'USE_NAT'},$fwdfwsettings{$fwdfwsettings{'nat'}},$fwdfwsettings{'dnatport'},$fwdfwsettings{'nat'},$fwdfwsettings{'LIMIT_CON_CON'},$fwdfwsettings{'concon'},$fwdfwsettings{'RATE_LIMIT'},$fwdfwsettings{'ratecon'},$fwdfwsettings{'RATETIME'}"
				eq "$rulehash{$key}[0],$rulehash{$key}[2],$rulehash{$key}[3],$rulehash{$key}[4],$rulehash{$key}[5],$rulehash{$key}[6],$rulehash{$key}[7],$rulehash{$key}[8],$rulehash{$key}[9],$rulehash{$key}[10],$rulehash{$key}[11],$rulehash{$key}[12],$rulehash{$key}[13],$rulehash{$key}[14],$rulehash{$key}[15],$rulehash{$key}[18],$rulehash{$key}[19],$rulehash{$key}[20],$rulehash{$key}[21],$rulehash{$key}[22],$rulehash{$key}[23],$rulehash{$key}[24],$rulehash{$key}[25],$rulehash{$key}[26],$rulehash{$key}[27],$rulehash{$key}[28],$rulehash{$key}[29],$rulehash{$key}[30],$rulehash{$key}[31],$rulehash{$key}[32],$rulehash{$key}[33],$rulehash{$key}[34],$rulehash{$key}[35],$rulehash{$key}[36]"){
					$errormessage.=$Lang::tr{'fwdfw err ruleexists'};
			}
		}
	}
	#check if we just close a rule
	if( $fwdfwsettings{'oldgrp1a'} eq  $fwdfwsettings{'grp1'} && $fwdfwsettings{'oldgrp1b'} eq $fwdfwsettings{$fwdfwsettings{'grp1'}} && $fwdfwsettings{'oldgrp2a'} eq  $fwdfwsettings{'grp2'} && $fwdfwsettings{'oldgrp2b'} eq $fwdfwsettings{$fwdfwsettings{'grp2'}} &&  $fwdfwsettings{'oldgrp3a'} eq $fwdfwsettings{'grp3'} && $fwdfwsettings{'oldgrp3b'} eq  $fwdfwsettings{$fwdfwsettings{'grp3'}} && $fwdfwsettings{'oldusesrv'} eq $fwdfwsettings{'USESRV'} && $fwdfwsettings{'oldruleremark'} eq $fwdfwsettings{'ruleremark'} && $fwdfwsettings{'oldruletype'} eq $fwdfwsettings{'chain'}){
		if($fwdfwsettings{'nosave'} eq 'on' && $fwdfwsettings{'updatefwrule'} eq 'on'){
			$fwdfwsettings{'nosave2'} = 'on';
			$errormessage='';
		}
	}
	#check max concurrent connections per ip address
	if ($fwdfwsettings{'LIMIT_CON_CON'} eq 'ON'){
		if (!($fwdfwsettings{'concon'} =~ /^(\d+)$/)) {
			$errormessage.=$Lang::tr{'fwdfw err concon'};
		}
	}else{
		$fwdfwsettings{'concon'}='';
	}
	#check ratelimit value
	if ($fwdfwsettings{'RATE_LIMIT'} eq 'ON'){
		if (!($fwdfwsettings{'ratecon'} =~ /^(\d+)$/)) {
			$errormessage.=$Lang::tr{'fwdfw err ratecon'};
		}
	}else{
		$fwdfwsettings{'ratecon'}='';
	}
	#increase counters
	if (!$errormessage){
		if ($fwdfwsettings{'nosave2'} ne 'on'){
			&saverule(\%rulehash,$fwdfwsettings{'config'});
		}
	}
	if ($errormessage){
		&newrule;
	}else{
		if($fwdfwsettings{'nosave2'} ne 'on'){
			&General::firewall_config_changed();
		}
		&base;
	}
}
if ($fwdfwsettings{'ACTION'} eq $Lang::tr{'fwdfw newrule'})
{
	&newrule;
}
if ($fwdfwsettings{'ACTION'} eq $Lang::tr{'fwdfw toggle'})
{
	my %togglehash=();
	&General::readhasharray($fwdfwsettings{'config'}, \%togglehash);
	foreach my $key (sort keys %togglehash){
		if ($key eq $fwdfwsettings{'key'}){
			if ($togglehash{$key}[2] eq 'ON'){$togglehash{$key}[2]='';}else{$togglehash{$key}[2]='ON';}
		}
	}
	&General::writehasharray($fwdfwsettings{'config'}, \%togglehash);
	&General::firewall_config_changed();
	&base;
}
if ($fwdfwsettings{'ACTION'} eq $Lang::tr{'fwdfw togglelog'})
{
	my %togglehash=();
	&General::readhasharray($fwdfwsettings{'config'}, \%togglehash);
	foreach my $key (sort keys %togglehash){
		if ($key eq $fwdfwsettings{'key'}){
			if ($togglehash{$key}[17] eq 'ON'){$togglehash{$key}[17]='';}else{$togglehash{$key}[17]='ON';}
		}
	}
	&General::writehasharray($fwdfwsettings{'config'}, \%togglehash);
	&General::firewall_config_changed();
	&base;
}
if ($fwdfwsettings{'ACTION'} eq $Lang::tr{'fwdfw reread'})
{
	&General::firewall_reload();
	&base;
}
if ($fwdfwsettings{'ACTION'} eq 'editrule')
{
	$fwdfwsettings{'updatefwrule'}='on';
	&newrule;
}
if ($fwdfwsettings{'ACTION'} eq 'deleterule')
{
	&deleterule;
}
if ($fwdfwsettings{'ACTION'} eq 'moveup')
{
	&pos_up;
	&base;
}
if ($fwdfwsettings{'ACTION'} eq 'movedown')
{
	&pos_down;
	&base;
}
if ($fwdfwsettings{'ACTION'} eq 'copyrule')
{
	$fwdfwsettings{'copyfwrule'}='on';
	&newrule;
}
if ($fwdfwsettings{'ACTION'} eq '' or $fwdfwsettings{'ACTION'} eq 'reset')
{
	&base;
}
###  Functions  ####
sub addrule
{
	&error;

	&Header::openbox('100%', 'left', "");
	print <<END;
		<form method="POST" action="">
			<table border='0' width="100%">
				<tr>
					<td align='center'>
						<input type='submit' name='ACTION' value='$Lang::tr{'fwdfw newrule'}'>
END

	if (&General::firewall_needs_reload()) {
		print <<END;
			<input type='submit' name='ACTION' value='$Lang::tr{'fwdfw reread'}' style='font-weight: bold; color: green;'>
END
	}

	print <<END;
					</td>
				</tr>
			</table>
		</form>

		<br>
END

	&Header::closebox();
	&viewtablerule;
}
sub base
{
	&hint;
	&addrule;
}
sub changerule
{
	my $oldchain=shift;
	$fwdfwsettings{'updatefwrule'}='';
	$fwdfwsettings{'config'}=$oldchain;
	$fwdfwsettings{'nobase'}='on';
	&deleterule;
}
sub checksource
{
	my ($ip,$subnet);
	#check ip-address if manual
	if ($fwdfwsettings{'src_addr'} eq $fwdfwsettings{$fwdfwsettings{'grp1'}} && $fwdfwsettings{'src_addr'} ne ''){
		#check if ip with subnet
		if ($fwdfwsettings{'src_addr'} =~ /^(.*?)\/(.*?)$/) {
			($ip,$subnet)=split (/\//,$fwdfwsettings{'src_addr'});
			$subnet = &General::iporsubtocidr($subnet);
			$fwdfwsettings{'isip'}='on';
		}
		#check if only ip
		if($fwdfwsettings{'src_addr'}=~/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/){
			$ip=$fwdfwsettings{'src_addr'};
			$subnet = '32';
			$fwdfwsettings{'isip'}='on';
		}

		if ($fwdfwsettings{'isip'} ne 'on'){
			if (&General::validmac($fwdfwsettings{'src_addr'})){
				$fwdfwsettings{'ismac'}='on';
			}
		}
		if ($fwdfwsettings{'isip'} eq 'on'){
			#remove leading zero
			$ip = &Network::ip_remove_zero($ip);

			##check if ip is valid
			if (! &General::validip($ip)){
				$errormessage.=$Lang::tr{'fwdfw err src_addr'}."<br>";
				return $errormessage;
			}
			#check and form valid IP
			$ip=&General::ip2dec($ip);
			$ip=&General::dec2ip($ip);
			#check if net or broadcast
			$fwdfwsettings{'src_addr'}="$ip/$subnet";
			if(!&General::validipandmask($fwdfwsettings{'src_addr'})){
				$errormessage.=$Lang::tr{'fwdfw err src_addr'}."<br>";
				return $errormessage;
			}
		}
		if ($fwdfwsettings{'isip'} ne 'on' && $fwdfwsettings{'ismac'} ne 'on'){
			$errormessage.=$Lang::tr{'fwdfw err src_addr'}."<br>";
			return $errormessage;
		}
	}elsif($fwdfwsettings{'src_addr'} eq $fwdfwsettings{$fwdfwsettings{'grp1'}} && $fwdfwsettings{'src_addr'} eq ''){
		$fwdfwsettings{'grp1'}='std_net_src';
		$fwdfwsettings{$fwdfwsettings{'grp1'}} = 'ALL';
	}

	#check empty fields
	if ($fwdfwsettings{$fwdfwsettings{'grp1'}} eq ''){ $errormessage.=$Lang::tr{'fwdfw err nosrc'}."<br>";}
	if($fwdfwsettings{'USE_SRC_PORT'} eq 'ON' && ($fwdfwsettings{'PROT'} eq 'TCP' || $fwdfwsettings{'PROT'} eq 'UDP') && $fwdfwsettings{'SRC_PORT'} ne ''){
		my @parts=split(",",$fwdfwsettings{'SRC_PORT'});
		my @values=();
		foreach (@parts){
			chomp($_);
			if ($_ =~ /^(\d+)\-(\d+)$/ || $_ =~ /^(\d+)\:(\d+)$/) {
				my $check;
				#change dashes with :
				$_=~ tr/-/:/;
				if ($_ eq "*") {
					push(@values,"1:65535");
					$check='on';
				}
				if ($_ =~ /^(\D)\:(\d+)$/ || $_ =~ /^(\D)\-(\d+)$/) {
					push(@values,"1:$2");
					$check='on';
				}
				if ($_ =~ /^(\d+)\:(\D)$/ || $_ =~ /^(\d+)\-(\D)$/ ) {
					push(@values,"$1:65535");
					$check='on'
				}
				$errormessage .= &General::validportrange($_, 'destination');
				if(!$check){
					push (@values,$_);
				}
			}else{
				if (&General::validport($_)){
					push (@values,$_);
				}else{
					
				}
			}
		}
		$fwdfwsettings{'SRC_PORT'}=join("|",@values);
	}
	return $errormessage;
}
sub checktarget
{
	my ($ip,$subnet);
	&General::readhasharray("$configsrv", \%customservice);
	#check DNAT settings (has to be single Host and single Port or portrange)
	if ($fwdfwsettings{'USE_NAT'} eq 'ON' && $fwdfwsettings{'nat'} eq 'dnat'){
		if($fwdfwsettings{'grp2'} eq 'tgt_addr' || $fwdfwsettings{'grp2'} eq 'cust_host_tgt' || $fwdfwsettings{'grp2'} eq 'ovpn_host_tgt'){
			#check if Port is a single Port or portrange
			if ($fwdfwsettings{'nat'} eq 'dnat' &&  $fwdfwsettings{'grp3'} eq 'TGT_PORT'){
				if(($fwdfwsettings{'PROT'} ne 'TCP'|| $fwdfwsettings{'PROT'} ne 'UDP') && $fwdfwsettings{'TGT_PORT'} eq ''){
					$errormessage=$Lang::tr{'fwdfw target'}.": ".$Lang::tr{'fwdfw dnat porterr'}."<br>";
					return $errormessage;
				}
				if (($fwdfwsettings{'PROT'} eq 'TCP'|| $fwdfwsettings{'PROT'} eq 'UDP') && $fwdfwsettings{'TGT_PORT'} ne '' && !&check_natport($fwdfwsettings{'TGT_PORT'})){
					$errormessage=$Lang::tr{'fwdfw target'}.": ".$Lang::tr{'fwdfw dnat porterr'}."<br>";
					return $errormessage;
				}
			}
		}else{
			if ($fwdfwsettings{'grp2'} ne 'ipfire'){
				$errormessage=$Lang::tr{'fwdfw dnat error'}."<br>";
				return $errormessage;
			}
		}
	}
	if ($fwdfwsettings{'tgt_addr'} eq $fwdfwsettings{$fwdfwsettings{'grp2'}} && $fwdfwsettings{'tgt_addr'} ne ''){
		#check if ip with subnet
		if ($fwdfwsettings{'tgt_addr'} =~ /^(.*?)\/(.*?)$/) {
			($ip,$subnet)=split (/\//,$fwdfwsettings{'tgt_addr'});
			$subnet = &General::iporsubtocidr($subnet);
		}

		#check if only ip
		if($fwdfwsettings{'tgt_addr'}=~/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/){
			$ip=$fwdfwsettings{'tgt_addr'};
			$subnet='32';
		}
		#remove leading zero
		$ip = &Network::ip_remove_zero($ip);

		#check if ip is valid
		if (! &General::validip($ip)){
			$errormessage.=$Lang::tr{'fwdfw err tgt_addr'}."<br>";
			return $errormessage;
		}
		#check and form valid IP
		$ip=&General::ip2dec($ip);
		$ip=&General::dec2ip($ip);
		$fwdfwsettings{'tgt_addr'}="$ip/$subnet";
		if(!&General::validipandmask($fwdfwsettings{'tgt_addr'})){
			$errormessage.=$Lang::tr{'fwdfw err tgt_addr'}."<br>";
			return $errormessage;
		}
	}elsif($fwdfwsettings{'tgt_addr'} eq $fwdfwsettings{$fwdfwsettings{'grp2'}} && $fwdfwsettings{'tgt_addr'} eq ''){
		$fwdfwsettings{'grp2'}='std_net_tgt';
		$fwdfwsettings{$fwdfwsettings{'grp2'}} = 'ALL';
	}
	#check for mac in targetgroup
	if ($fwdfwsettings{'grp2'} eq 'cust_grp_tgt'){
		&General::readhasharray("$configgrp", \%customgrp);
		&General::readhasharray("$confighost", \%customhost);
		foreach my $grpkey (sort keys %customgrp){
			foreach my $hostkey (sort keys %customhost){
				if ($customgrp{$grpkey}[2] eq $customhost{$hostkey}[0] && $customgrp{$grpkey}[2] eq $fwdfwsettings{$fwdfwsettings{'grp2'}} && $customhost{$hostkey}[1] eq 'mac'){
					$hint=$Lang::tr{'fwdfw hint mac'};
					return $hint;
				}
			}
		}
	}
	#check empty fields
	if ($fwdfwsettings{$fwdfwsettings{'grp2'}} eq ''){ $errormessage.=$Lang::tr{'fwdfw err notgt'}."<br>";}
	#check tgt services
	if ($fwdfwsettings{'USESRV'} eq 'ON'){
		if ($fwdfwsettings{'grp3'} eq 'cust_srv'){
			$fwdfwsettings{'TGT_PROT'}='';
			$fwdfwsettings{'ICMP_TGT'}='';
			$fwdfwsettings{'TGT_PORT'}='';
		}
		if ($fwdfwsettings{'grp3'} eq 'cust_srvgrp'){
			$fwdfwsettings{'TGT_PROT'}='';
			$fwdfwsettings{'ICMP_TGT'}='';
			$fwdfwsettings{'TGT_PORT'}='';
			#check target service
			if($fwdfwsettings{$fwdfwsettings{'grp3'}} eq ''){
				$errormessage.=$Lang::tr{'fwdfw err tgt_grp'};
			}
		}
		if ($fwdfwsettings{'grp3'} eq 'TGT_PORT'){
			if ($fwdfwsettings{'PROT'} eq 'TCP' || $fwdfwsettings{'PROT'} eq 'UDP'){
				if ($fwdfwsettings{'TGT_PORT'} ne ''){
					if ($fwdfwsettings{'TGT_PORT'} =~ "," && $fwdfwsettings{'USE_NAT'} && $fwdfwsettings{'nat'} eq 'dnat') {
						$errormessage=$Lang::tr{'fwdfw dnat porterr'}."<br>";
						return $errormessage;
					}
					my @parts=split(",",$fwdfwsettings{'TGT_PORT'});
					my @values=();
					foreach (@parts){
						chomp($_);
						if ($_ =~ /^(\d+)\-(\d+)$/ || $_ =~ /^(\d+)\:(\d+)$/) {
							my $check;
							#change dashes with :
							$_=~ tr/-/:/;
							if ($_ eq "*") {
								push(@values,"1:65535");
								$check='on';
							}
							if ($_ =~ /^(\D)\:(\d+)$/ || $_ =~ /^(\D)\-(\d+)$/) {
								push(@values,"1:$2");
								$check='on';
							}
							if ($_ =~ /^(\d+)\:(\D)$/ || $_ =~ /^(\d+)\-(\D)$/) {
								push(@values,"$1:65535");
								$check='on'
							}
							$errormessage .= &General::validportrange($_, 'destination');
							if(!$check){
								push (@values,$_);
							}
						}else{
							if (&General::validport($_)){
								push (@values,$_);
							}else{
								$errormessage=$Lang::tr{'fwdfw err tgt_port'};
								return $errormessage;
							}
						}
					}
					$fwdfwsettings{'TGT_PORT'}=join("|",@values);
				}
			}elsif ($fwdfwsettings{'PROT'} eq 'GRE'){
					$fwdfwsettings{$fwdfwsettings{'grp3'}} = '';
					$fwdfwsettings{'TGT_PORT'} = '';
					$fwdfwsettings{'ICMP_TGT'} = '';
			}elsif ($fwdfwsettings{'PROT'} eq 'ESP'){
					$fwdfwsettings{$fwdfwsettings{'grp3'}} = '';
					$fwdfwsettings{'TGT_PORT'} = '';
					$fwdfwsettings{'ICMP_TGT'}='';
			}elsif ($fwdfwsettings{'PROT'} eq 'AH'){
					$fwdfwsettings{$fwdfwsettings{'grp3'}} = '';
					$fwdfwsettings{'TGT_PORT'} = '';
					$fwdfwsettings{'ICMP_TGT'}='';
			}elsif ($fwdfwsettings{'PROT'} eq 'ICMP'){
				$fwdfwsettings{$fwdfwsettings{'grp3'}} = '';
				$fwdfwsettings{'TGT_PORT'} = '';
			}
		}
	}
	#check targetport
	if ($fwdfwsettings{'USESRV'} ne 'ON'){
		$fwdfwsettings{'grp3'}='';
		$fwdfwsettings{$fwdfwsettings{'grp3'}}='';
		$fwdfwsettings{'ICMP_TGT'}='';
	}
	#check timeframe
	if($fwdfwsettings{'TIME'} eq 'ON'){
		if($fwdfwsettings{'TIME_MON'} eq '' && $fwdfwsettings{'TIME_TUE'} eq '' && $fwdfwsettings{'TIME_WED'} eq '' && $fwdfwsettings{'TIME_THU'} eq '' && $fwdfwsettings{'TIME_FRI'} eq '' && $fwdfwsettings{'TIME_SAT'} eq '' && $fwdfwsettings{'TIME_SUN'} eq ''){
			$errormessage=$Lang::tr{'fwdfw err time'};
			return $errormessage;
		}
	}
	return $errormessage;
}
sub check_natport
{
	my $val=shift;
	if($fwdfwsettings{'USE_NAT'} eq 'ON' && $fwdfwsettings{'nat'} eq 'dnat' && $fwdfwsettings{'dnatport'} ne ''){
		if ($fwdfwsettings{'dnatport'} =~ /^(\d+)\-(\d+)$/) {
			$fwdfwsettings{'dnatport'} =~ tr/-/:/;
			if ($fwdfwsettings{'dnatport'} eq "*") {
				$fwdfwsettings{'dnatport'}="1:65535";
			}
			if ($fwdfwsettings{'dnatport'} =~ /^(\D)\:(\d+)$/) {
				$fwdfwsettings{'dnatport'} = "1:$2";
			}
			if ($fwdfwsettings{'dnatport'} =~ /^(\d+)\:(\D)$/) {
				$fwdfwsettings{'dnatport'} ="$1:65535";
			}
		}
		return 1;
	}
	if ($val =~ "," || $val>65536 || $val<0){
		return 0;
	}
	return 1;
}
sub checkrule
{
	#check valid port for NAT
	if($fwdfwsettings{'USE_NAT'} eq 'ON'){
		#RULE_ACTION must be ACCEPT if we use NAT
		$fwdfwsettings{'RULE_ACTION'} = 'ACCEPT';

		#if no dnat or snat selected errormessage
		if ($fwdfwsettings{'nat'} eq ''){
			$errormessage=$Lang::tr{'fwdfw dnat nochoice'};
			return;
		}

		#if using snat, the external port has to be empty
		if ($fwdfwsettings{'nat'} eq 'snat' && $fwdfwsettings{'dnatport'} ne ''){
			$errormessage=$Lang::tr{'fwdfw dnat extport'};
			return;
		}
		#if no dest port is given in nat area, take target host port
		if($fwdfwsettings{'nat'} eq 'dnat' && $fwdfwsettings{'grp3'} eq 'TGT_PORT' && $fwdfwsettings{'dnatport'} eq ''){$fwdfwsettings{'dnatport'}=$fwdfwsettings{'TGT_PORT'};}
		if($fwdfwsettings{'TGT_PORT'} eq '' && $fwdfwsettings{'dnatport'} ne '' && ($fwdfwsettings{'PROT'} eq 'TCP' || $fwdfwsettings{'PROT'} eq 'UDP')){
			$errormessage=$Lang::tr{'fwdfw dnat porterr2'};
			return;
		}
		#check if port given in nat area is a single valid port or portrange
		if($fwdfwsettings{'nat'} eq 'dnat' && $fwdfwsettings{'TGT_PORT'} ne '' && !&check_natport($fwdfwsettings{'dnatport'})){
			$errormessage=$Lang::tr{'fwdfw target'}.": ".$Lang::tr{'fwdfw dnat porterr'}."<br>";
		}elsif($fwdfwsettings{'USESRV'} eq 'ON' && $fwdfwsettings{'grp3'} eq 'cust_srv'){
			my $custsrvport;
			#get service Protocol and Port
			foreach my $key (sort keys %customservice){
				if($fwdfwsettings{$fwdfwsettings{'grp3'}} eq $customservice{$key}[0]){
					if ($customservice{$key}[2] ne 'TCP' && $customservice{$key}[2] ne 'UDP'){
						$errormessage=$Lang::tr{'fwdfw target'}.": ".$Lang::tr{'fwdfw dnat porterr'}."<br>";
					}
					$custsrvport= $customservice{$key}[1];
				}
			}
			if($fwdfwsettings{'nat'} eq 'dnat' && $fwdfwsettings{'dnatport'} eq ''){$fwdfwsettings{'dnatport'}=$custsrvport;}
		}
		#check if DNAT port is multiple
		if($fwdfwsettings{'nat'} eq 'dnat' && $fwdfwsettings{'dnatport'} ne ''){
			my @parts=split(",",$fwdfwsettings{'dnatport'});
					my @values=();
					foreach (@parts){
						chomp($_);
						if ($_ =~ /^(\d+)\-(\d+)$/ || $_ =~ /^(\d+)\:(\d+)$/) {
							my $check;
							#change dashes with :
							$_=~ tr/-/:/;
							if ($_ eq "*") {
								push(@values,"1:65535");
								$check='on';
							}
							if ($_ =~ /^(\D)\:(\d+)$/ || $_ =~ /^(\D)\-(\d+)$/) {
								push(@values,"1:$2");
								$check='on';
							}
							if ($_ =~ /^(\d+)\:(\D)$/ || $_ =~ /^(\d+)\-(\D)$/) {
								push(@values,"$1:65535");
								$check='on'
							}
							$errormessage .= &General::validportrange($_, 'destination');
							if(!$check){
								push (@values,$_);
							}
						}else{
							if (&General::validport($_)){
								push (@values,$_);
							}else{
								
							}
						}
					}
					$fwdfwsettings{'dnatport'}=join("|",@values);
		}
		#check if a rule with prot tcp or udp and ports is edited and now prot is "all", then delete all ports
		if($fwdfwsettings{'PROT'} eq ''){
			$fwdfwsettings{'dnatport'}='';
		}
	}
	#check valid remark
	if ($fwdfwsettings{'ruleremark'} ne '' && !&validremark($fwdfwsettings{'ruleremark'})){
		$errormessage.=$Lang::tr{'fwdfw err remark'}."<br>";
	}
	#check if source and target identical
	if ($fwdfwsettings{$fwdfwsettings{'grp1'}} eq $fwdfwsettings{$fwdfwsettings{'grp2'}} && $fwdfwsettings{$fwdfwsettings{'grp1'}} ne 'ALL' && $fwdfwsettings{'grp2'} ne 'ipfire'){
		$errormessage=$Lang::tr{'fwdfw err same'};
		return $errormessage;
	}
	#get source and targetip address if possible
	my ($sip,$scidr,$tip,$tcidr);
	($sip,$scidr)=&get_ip("src","grp1");
	($tip,$tcidr)=&get_ip("tgt","grp2");
	#check same iprange in source and target
	if ($sip ne '' && $scidr ne '' && $tip ne '' && $tcidr ne ''){
		my $networkip1=&General::getnetworkip($sip,$scidr);
		my $networkip2=&General::getnetworkip($tip,$tcidr);
		if ($scidr gt $tcidr){
			if ( &General::IpInSubnet($networkip1,$tip,&General::iporsubtodec($tcidr))){
				$errormessage.=$Lang::tr{'fwdfw err samesub'};
			}
		}elsif($scidr eq $tcidr && $scidr eq '32'){
			my ($sbyte1,$sbyte2,$sbyte3,$sbyte4)=split(/\./,$networkip1);
			my ($tbyte1,$tbyte2,$tbyte3,$tbyte4)=split(/\./,$networkip2);
				if ($sbyte1 eq $tbyte1 && $sbyte2 eq $tbyte2 && $sbyte3 eq $tbyte3){
					$hint=$Lang::tr{'fwdfw hint ip1'}."<br>";
					$hint.=$Lang::tr{'fwdfw hint ip2'}." Source: $networkip1/$scidr Target: $networkip2/$tcidr<br>";
				}
		}else{
			if ( &General::IpInSubnet($networkip2,$sip,&General::iporsubtodec($scidr)) ){
			$errormessage.=$Lang::tr{'fwdfw err samesub'};
			}
		}
	}
	#when icmp selected, no source and targetport allowed
	if (($fwdfwsettings{'PROT'} ne '' && $fwdfwsettings{'PROT'} ne 'TCP' && $fwdfwsettings{'PROT'} ne 'UDP' && $fwdfwsettings{'PROT'} ne 'template') && ($fwdfwsettings{'USESRV'} eq 'ON' || $fwdfwsettings{'USE_SRC_PORT'} eq 'ON')){
		$errormessage.=$Lang::tr{'fwdfw err prot_port'};
		return;
	}
	#change protocol if prot not equal dest single service
	if ($fwdfwsettings{'grp3'} eq 'cust_srv'){
		foreach my $key (sort keys %customservice){
			if($customservice{$key}[0] eq $fwdfwsettings{$fwdfwsettings{'grp3'}}){
				if ($customservice{$key}[2] ne $fwdfwsettings{'PROT'}){
					$fwdfwsettings{'PROT'} = $customservice{$key}[2];
					last;
				}
			}
		}
	}
	#check source and destination protocol if source manual and dest servicegroup
	if ($fwdfwsettings{'grp3'} eq 'cust_srvgrp'){
		$fwdfwsettings{'PROT'} = '';
	}
	#ATTENTION: $fwdfwsetting{'TGT_PROT'} deprecated since 30.09.2013
	$fwdfwsettings{'TGT_PROT'}=''; #Set field empty (deprecated)
	#Check ICMP Types
	if ($fwdfwsettings{'PROT'} eq 'ICMP'){
		$fwdfwsettings{'USE_SRC_PORT'}='';
		$fwdfwsettings{'SRC_PORT'}='';
		#$fwdfwsettings{'USESRV'}='';
		$fwdfwsettings{'TGT_PORT'}='';
		&General::readhasharray("${General::swroot}/fwhosts/icmp-types", \%icmptypes);
		foreach my $key (keys %icmptypes){
			if($fwdfwsettings{'ICMP_TYPES'} eq "$icmptypes{$key}[0] ($icmptypes{$key}[1])"){
				$fwdfwsettings{'ICMP_TYPES'}="$icmptypes{$key}[0]";
			}
		}
	}elsif($fwdfwsettings{'PROT'} eq 'GRE'){
		$fwdfwsettings{'USE_SRC_PORT'}='';
		$fwdfwsettings{'SRC_PORT'}='';
		$fwdfwsettings{'ICMP_TYPES'}='';
		$fwdfwsettings{'USESRV'}='';
		$fwdfwsettings{'TGT_PORT'}='';
	}elsif($fwdfwsettings{'PROT'} eq 'ESP'){
		$fwdfwsettings{'USE_SRC_PORT'}='';
		$fwdfwsettings{'SRC_PORT'}='';
		$fwdfwsettings{'ICMP_TYPES'}='';
		$fwdfwsettings{'USESRV'}='';
		$fwdfwsettings{'TGT_PORT'}='';
	}elsif($fwdfwsettings{'PROT'} eq 'AH'){
		$fwdfwsettings{'USE_SRC_PORT'}='';
		$fwdfwsettings{'SRC_PORT'}='';
		$fwdfwsettings{'ICMP_TYPES'}='';
		$fwdfwsettings{'USESRV'}='';
		$fwdfwsettings{'TGT_PORT'}='';
	}elsif($fwdfwsettings{'PROT'} eq 'IGMP'){
		$fwdfwsettings{'USE_SRC_PORT'}='';
		$fwdfwsettings{'SRC_PORT'}='';
		$fwdfwsettings{'ICMP_TYPES'}='';
		$fwdfwsettings{'USESRV'}='';
		$fwdfwsettings{'TGT_PORT'}='';
	}elsif($fwdfwsettings{'PROT'} eq 'IPv6'){
		$fwdfwsettings{'USE_SRC_PORT'}='';
		$fwdfwsettings{'SRC_PORT'}='';
		$fwdfwsettings{'ICMP_TYPES'}='';
		$fwdfwsettings{'USESRV'}='';
		$fwdfwsettings{'TGT_PORT'}='';
	}elsif($fwdfwsettings{'PROT'} eq 'IPIP'){
		$fwdfwsettings{'USE_SRC_PORT'}='';
		$fwdfwsettings{'SRC_PORT'}='';
		$fwdfwsettings{'ICMP_TYPES'}='';
		$fwdfwsettings{'USESRV'}='';
		$fwdfwsettings{'TGT_PORT'}='';
	}elsif($fwdfwsettings{'PROT'} ne 'TCP' && $fwdfwsettings{'PROT'} ne 'UDP'){
		$fwdfwsettings{'ICMP_TYPES'}='';
		$fwdfwsettings{'SRC_PORT'}='';
		$fwdfwsettings{'TGT_PORT'}='';
	}elsif($fwdfwsettings{'PROT'} ne 'ICMP'){
		$fwdfwsettings{'ICMP_TYPES'}='';
	}
}
sub checkvpn
{
	my $ip=shift;
	#Test if manual IP is part of static OpenVPN networks
	&General::readhasharray("$configccdnet", \%ccdnet);
	foreach my $key (sort keys %ccdnet){
		my ($vpnip,$vpnsubnet) = split ("/",$ccdnet{$key}[1]);
		my $sub=&General::iporsubtodec($vpnsubnet);
		if (&General::IpInSubnet($ip,$vpnip,$sub)){
			return 0;
		}
	}
	# A Test if manual ip is part of dynamic openvpn subnet is made in getcolor
	# because if one creates a custom host with the ip, we need to check the color there!
	# It does not make sense to check this here
	
	# Test if manual IP is part of an OpenVPN N2N subnet does also not make sense here
	# Is also checked in getcolor
	
	# Test if manual ip is part of an IPsec Network is also checked in getcolor
	return 1;
}
sub checkvpncolor
{
	
}
sub deleterule
{
	my %delhash=();
	&General::readhasharray($fwdfwsettings{'config'}, \%delhash);
	foreach my $key (sort {$a <=> $b} keys %delhash){
		if ($key >= $fwdfwsettings{'key'}) {
			my $next = $key + 1;
			if (exists $delhash{$next}) {
				foreach my $i (0 .. $#{$delhash{$next}}) {
					$delhash{$key}[$i] = $delhash{$next}[$i];
				}
			}
		}
	}
	# Remove the very last entry.
	my $last_key = (sort {$a <=> $b} keys %delhash)[-1];
	delete $delhash{$last_key};

	&General::writehasharray($fwdfwsettings{'config'}, \%delhash);
	&General::firewall_config_changed();

	if($fwdfwsettings{'nobase'} ne 'on'){
		&base;
	}
}
sub del_double
{
	my %all=();
	@all{@_}=1;
	return (keys %all);
}
sub disable_rule
{
	my $key1=shift;
	&General::readhasharray("$configfwdfw", \%configfwdfw);
	foreach my $key (sort keys %configfwdfw){
			if ($key eq $key1 ){
			if ($configfwdfw{$key}[2] eq 'ON'){$configfwdfw{$key}[2]='';}
		}
	}
	&General::writehasharray("$configfwdfw", \%configfwdfw);
	&General::firewall_config_changed();
}
sub error
{
	if ($errormessage) {
		&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
		print "<class name='base'>$errormessage\n";
		print "&nbsp;</class>\n";
		&Header::closebox();
	}
}
sub fillselect
{
	my %hash=%{(shift)};
	my $val=shift;
	my $key;
	foreach my $key (sort { ncmp($hash{$a}[0],$hash{$b}[0]) }  keys %hash){
		if($hash{$key}[0] eq $val){
			print"<option value='$hash{$key}[0]' selected>$hash{$key}[0]</option>";
		}else{
			print"<option value='$hash{$key}[0]'>$hash{$key}[0]</option>";
		}
	}
}
sub gen_dd_block
{
	my $srctgt = shift;
	my $grp=shift;
	my $helper='';
	my $show='';
	$checked{'grp1'}{$fwdfwsettings{'grp1'}} 				= 'CHECKED';
	$checked{'grp2'}{$fwdfwsettings{'grp2'}} 				= 'CHECKED';
	$checked{'grp3'}{$fwdfwsettings{'grp3'}} 				= 'CHECKED';
	$checked{'USE_SRC_PORT'}{$fwdfwsettings{'USE_SRC_PORT'}} = 'CHECKED';
	$checked{'USESRV'}{$fwdfwsettings{'USESRV'}} 			= 'CHECKED';
	$checked{'ACTIVE'}{$fwdfwsettings{'ACTIVE'}} 			= 'CHECKED';
	$checked{'LOG'}{$fwdfwsettings{'LOG'}} 					= 'CHECKED';
	$checked{'TIME'}{$fwdfwsettings{'TIME'}} 				= 'CHECKED';
	$checked{'TIME_MON'}{$fwdfwsettings{'TIME_MON'}} 		= 'CHECKED';
	$checked{'TIME_TUE'}{$fwdfwsettings{'TIME_TUE'}} 		= 'CHECKED';
	$checked{'TIME_WED'}{$fwdfwsettings{'TIME_WED'}} 		= 'CHECKED';
	$checked{'TIME_THU'}{$fwdfwsettings{'TIME_THU'}} 		= 'CHECKED';
	$checked{'TIME_FRI'}{$fwdfwsettings{'TIME_FRI'}} 		= 'CHECKED';
	$checked{'TIME_SAT'}{$fwdfwsettings{'TIME_SAT'}} 		= 'CHECKED';
	$checked{'TIME_SUN'}{$fwdfwsettings{'TIME_SUN'}} 		= 'CHECKED';
	$selected{'TIME_FROM'}{$fwdfwsettings{'TIME_FROM'}}		= 'selected';
	$selected{'TIME_TO'}{$fwdfwsettings{'TIME_TO'}}			= 'selected';
	$selected{'ipfire'}{$fwdfwsettings{$fwdfwsettings{'grp1'}}} ='selected';
	$selected{'ipfire'}{$fwdfwsettings{$fwdfwsettings{'grp2'}}} ='selected';
print<<END;
		<table width='100%' border='0'>
		<tr><td width='50%' valign='top'>
		<table width='95%' border='0'>
		<tr><td width='1%'><input type='radio' name='$grp' id='std_net_$srctgt' value='std_net_$srctgt' $checked{$grp}{'std_net_'.$srctgt}></td><td>$Lang::tr{'fwhost stdnet'}</td><td align='right'><select name='std_net_$srctgt' style='width:200px;'>
END
	foreach my $network (sort keys %defaultNetworks)
		{
			next if($defaultNetworks{$network}{'NAME'} eq "IPFire");
			print "<option value='$defaultNetworks{$network}{'NAME'}'";
			print " selected='selected'" if ($fwdfwsettings{$fwdfwsettings{$grp}} eq $defaultNetworks{$network}{'NAME'});
			my $defnet="$defaultNetworks{$network}{'NAME'}_NETADDRESS";
			my $defsub="$defaultNetworks{$network}{'NAME'}_NETMASK";
			my $defsub1=&General::subtocidr($ifaces{$defsub});
			$ifaces{$defnet}='' if ($defaultNetworks{$network}{'NAME'} eq 'RED');
			if ($ifaces{$defnet}){
				print ">$network ($ifaces{$defnet}/$defsub1)</option>";
			}else{
				print ">$network</option>";
			}
		}
	print"</select></td></tr>";
	#custom networks
	if (! -z $confignet || $optionsfw{'SHOWDROPDOWN'} eq 'on'){
		print"<tr><td><input type='radio' name='$grp' id='cust_net_$srctgt' value='cust_net_$srctgt' $checked{$grp}{'cust_net_'.$srctgt}></td><td>$Lang::tr{'fwhost cust net'}</td><td align='right'><select name='cust_net_$srctgt' style='width:200px;'>";
		&fillselect(\%customnetwork,$fwdfwsettings{$fwdfwsettings{$grp}});
		print"</select></td>";
	}
	#custom hosts
	if (! -z $confighost || $optionsfw{'SHOWDROPDOWN'} eq 'on'){
		print"<tr><td><input type='radio' name='$grp' id='cust_host_$srctgt' value='cust_host_$srctgt' $checked{$grp}{'cust_host_'.$srctgt}></td><td>$Lang::tr{'fwhost cust addr'}</td><td align='right'><select name='cust_host_$srctgt' style='width:200px;'>";
		&fillselect(\%customhost,$fwdfwsettings{$fwdfwsettings{$grp}});
		print"</select></td>";
	}
	#custom groups
	if (! -z $configgrp || $optionsfw{'SHOWDROPDOWN'} eq 'on'){
		print"<tr><td valign='top'><input type='radio' name='$grp' id='cust_grp_$srctgt' value='cust_grp_$srctgt' $checked{$grp}{'cust_grp_'.$srctgt}></td><td >$Lang::tr{'fwhost cust grp'}</td><td align='right'><select name='cust_grp_$srctgt' style='width:200px;'>";
		foreach my $key (sort { ncmp($customgrp{$a}[0],$customgrp{$b}[0]) } keys %customgrp) {
			if($helper ne $customgrp{$key}[0] && $customgrp{$key}[2] ne 'none'){
				print"<option ";
				print "selected='selected' " if ($fwdfwsettings{$fwdfwsettings{$grp}} eq $customgrp{$key}[0]);
				print ">$customgrp{$key}[0]</option>";
			}
			$helper=$customgrp{$key}[0];
		}
		print"</select></td>";
	}
	# geoip locations / groups.
	my @geoip_locations = &fwlib::get_geoip_locations();

	print "<tr>\n";
	print "<td valign='top'><input type='radio' name='$grp' id='cust_geoip_$srctgt' value='cust_geoip_$srctgt' $checked{$grp}{'cust_geoip_'.$srctgt}></td>\n";
	print "<td>$Lang::tr{'geoip'}</td>\n";
	print "<td align='right'><select name='cust_geoip_$srctgt' style='width:200px;'>\n";

	# Add GeoIP groups to dropdown.
	if (!-z $configgeoipgrp) {
		print "<optgroup label='$Lang::tr{'fwhost cust geoipgroup'}'>\n";
		foreach my $key (sort { ncmp($customgeoipgrp{$a}[0],$customgeoipgrp{$b}[0]) } keys %customgeoipgrp) {
			my $selected;

			# Generate stored value for select detection.
			my $stored = join(':', "group",$customgeoipgrp{$key}[0]);

			# Only show a group once and group with elements.
			if($helper ne $customgeoipgrp{$key}[0] && $customgeoipgrp{$key}[2] ne 'none') {
				# Mark current entry as selected.
				if ($fwdfwsettings{$fwdfwsettings{$grp}} eq $stored) {
					$selected = "selected='selected'";
				}
                                print"<option $selected value='group:$customgeoipgrp{$key}[0]'>$customgeoipgrp{$key}[0]</option>\n";
                        }
                        $helper=$customgeoipgrp{$key}[0];
                }
		print "</optgroup>\n";
	}

	# Add locations.
	print "<optgroup label='$Lang::tr{'fwhost cust geoiplocation'}'>\n";
	foreach my $location (@geoip_locations) {
		# Get country name.
		my $country_name = &GeoIP::get_full_country_name($location);

		# Mark current entry as selected.
		my $selected;
		if ($fwdfwsettings{$fwdfwsettings{$grp}} eq $location) {
			$selected = "selected='selected'";
		}
		print "<option $selected value='$location'>$location - $country_name</option>\n";
	}
	print "</optgroup>\n";

	# Close GeoIP dropdown.
	print "</select></td>\n";

	#End left table. start right table (vpn)
	print"</tr></table></td><td valign='top'><table width='95%' border='0' align='right'><tr>";
	# CCD networks
	if( ! -z $configccdnet || $optionsfw{'SHOWDROPDOWN'} eq 'on'){
		print"<td width='1%'><input type='radio' name='$grp' id='ovpn_net_$srctgt' value='ovpn_net_$srctgt'  $checked{$grp}{'ovpn_net_'.$srctgt}></td><td nowrap='nowrap' width='16%'>$Lang::tr{'fwhost ccdnet'}</td><td nowrap='nowrap' width='1%' align='right'><select name='ovpn_net_$srctgt' style='width:200px;'>";
		&fillselect(\%ccdnet,$fwdfwsettings{$fwdfwsettings{$grp}});
		print"</select></td></tr>";
	}
	#OVPN CCD Hosts
	foreach my $key (sort { ncmp($ccdhost{$a}[0],$ccdhost{$b}[0]) } keys %ccdhost){
		if ($ccdhost{$key}[33] ne '' ){
			print"<tr><td width='1%'><input type='radio' name='$grp' id='ovpn_host_$srctgt' value='ovpn_host_$srctgt' $checked{$grp}{'ovpn_host_'.$srctgt}></td><td nowrap='nowrap' width='16%'>$Lang::tr{'fwhost ccdhost'}</td><td nowrap='nowrap' width='1%' align='right'><select name='ovpn_host_$srctgt' style='width:200px;'>" if ($show eq '');
			$show='1';
			print "<option value='$ccdhost{$key}[1]'";
			print "selected='selected'" if ($fwdfwsettings{$fwdfwsettings{$grp}} eq $ccdhost{$key}[1]);
			print ">$ccdhost{$key}[1]</option>";
		}
	}
	if($optionsfw{'SHOWDROPDOWN'} eq 'on' && $show eq ''){
		print"<tr><td width='1%'><input type='radio' name='$grp' id='ovpn_host_$srctgt' value='ovpn_host_$srctgt' $checked{$grp}{'ovpn_host_'.$srctgt}></td><td nowrap='nowrap' width='16%'>$Lang::tr{'fwhost ccdhost'}</td><td nowrap='nowrap' width='1%' align='right'><select name='ovpn_host_$srctgt' style='width:200px;'></select></td></tr>" ;
	}
	if ($show eq '1'){$show='';print"</select></td></tr>";}
	#OVPN N2N
	foreach my $key (sort { ncmp($ccdhost{$a}[1],$ccdhost{$b}[1]) } keys %ccdhost){
		if ($ccdhost{$key}[3] eq 'net'){
			print"<tr><td width='1%'><input type='radio' name='$grp' id='ovpn_n2n_$srctgt' value='ovpn_n2n_$srctgt' $checked{$grp}{'ovpn_n2n_'.$srctgt}></td><td nowrap='nowrap' width='16%'>$Lang::tr{'fwhost ovpn_n2n'}:</td><td nowrap='nowrap' width='1%' align='right'><select name='ovpn_n2n_$srctgt' style='width:200px;'>" if ($show eq '');
			$show='1';
			print "<option value='$ccdhost{$key}[1]'";
			print "selected='selected'" if ($fwdfwsettings{$fwdfwsettings{$grp}} eq $ccdhost{$key}[1]);
			print ">$ccdhost{$key}[1]</option>";
		}
	}
	if($optionsfw{'SHOWDROPDOWN'} eq 'on' && $show eq ''){
		print"<tr><td width='1%'><input type='radio' name='$grp' id='ovpn_n2n_$srctgt' value='ovpn_n2n_$srctgt' $checked{$grp}{'ovpn_n2n_'.$srctgt}></td><td nowrap='nowrap' width='16%'>$Lang::tr{'fwhost ovpn_n2n'}</td><td nowrap='nowrap' width='1%' align='right'><select name='ovpn_n2n_$srctgt' style='width:200px;'></select></td></tr>" ;
	}
	if ($show eq '1'){$show='';print"</select></td></tr>";}
	#IPsec netze
	foreach my $key (sort { ncmp($ipsecconf{$a}[1],$ipsecconf{$b}[1]) } keys %ipsecconf) {
		if ($ipsecconf{$key}[3] eq 'net' || ($optionsfw{'SHOWDROPDOWN'} eq 'on' && $ipsecconf{$key}[3] ne 'host')){
			print"<tr><td valign='top'><input type='radio' name='$grp' id='ipsec_net_$srctgt' value='ipsec_net_$srctgt' $checked{$grp}{'ipsec_net_'.$srctgt}></td><td >$Lang::tr{'fwhost ipsec net'}</td><td align='right'><select name='ipsec_net_$srctgt' style='width:200px;'>" if ($show eq '');
			$show='1';

			#Check if we have more than one REMOTE subnet in config
			my @arr1 = split /\|/, $ipsecconf{$key}[11];
			my $cnt1 += @arr1;

			print "<option ";
			print "value=$ipsecconf{$key}[1]";
			print " selected " if ($fwdfwsettings{$fwdfwsettings{$grp}} eq "$ipsecconf{$key}[1]");
			print ">$ipsecconf{$key}[1] ";
			print "($Lang::tr{'fwdfw all subnets'})" if $cnt1 > 1; #If this Conenction has more than one subnet, print one option for all subnets
			print "</option>";

			if ($cnt1 > 1){
				foreach my $val (@arr1){
					#normalize subnet to cidr notation
					my ($val1,$val2) = split /\//, $val;
					my $val3 = &General::iporsubtocidr($val2);
					print "<option ";
					print "value='$ipsecconf{$key}[1]|$val1/$val3'";
					print "selected " if ($fwdfwsettings{$fwdfwsettings{$grp}} eq "$ipsecconf{$key}[1]|$val1/$val3");
					print ">$ipsecconf{$key}[1] ($val1/$val3)</option>";
				}
			}
		}
	}
	if($optionsfw{'SHOWDROPDOWN'} eq 'on' && $show eq ''){
		print"<tr><td valign='top'><input type='radio' name='$grp' id='ipsec_net_$srctgt' value='ipsec_net_$srctgt' $checked{$grp}{'ipsec_net_'.$srctgt}></td><td >$Lang::tr{'fwhost ipsec net'}</td><td align='right'><select name='ipsec_net_$srctgt' style='width:200px;'><select></td></tr>";
	}
	if ($show eq '1'){$show='';print"</select></td></tr>";}
	
	print"</table>";
	print"</td></tr></table><br>";
}
sub get_ip
{
	my $val=shift;
	my $grp =shift;
	my $a;
	my $b;
	&General::readhash("/var/ipfire/ethernet/settings", \%netsettings);
	if ($fwdfwsettings{$grp} ne $Lang::tr{'fwhost any'}){
		if ($fwdfwsettings{$grp} eq $val.'_addr'){
			($a,$b)   = split (/\//, $fwdfwsettings{$fwdfwsettings{$grp}});
		}elsif($fwdfwsettings{$grp} eq 'std_net_'.$val){
			if ($fwdfwsettings{$fwdfwsettings{$grp}} =~ /Gr/i){
				$a=$netsettings{'GREEN_NETADDRESS'};
				$b=&General::iporsubtocidr($netsettings{'GREEN_NETMASK'});
			}elsif($fwdfwsettings{$fwdfwsettings{$grp}} =~ /Ora/i){
				$a=$netsettings{'ORANGE_NETADDRESS'};
				$b=&General::iporsubtocidr($netsettings{'ORANGE_NETMASK'});
			}elsif($fwdfwsettings{$fwdfwsettings{$grp}} =~ /Bl/i){
				$a=$netsettings{'BLUE_NETADDRESS'};
				$b=&General::iporsubtocidr($netsettings{'BLUE_NETMASK'});
			}elsif($fwdfwsettings{$fwdfwsettings{$grp}} =~ /OpenVPN/i){
				&General::readhash("$configovpn",\%ovpnsettings);
				($a,$b)   = split (/\//, $ovpnsettings{'DOVPN_SUBNET'});
				$b=&General::iporsubtocidr($b);
			}
		}elsif($fwdfwsettings{$grp} eq 'cust_net_'.$val){
			&General::readhasharray("$confignet", \%customnetwork);
			foreach my $key (keys %customnetwork){
				if($customnetwork{$key}[0] eq $fwdfwsettings{$fwdfwsettings{$grp}}){
					$a=$customnetwork{$key}[1];
					$b=&General::iporsubtocidr($customnetwork{$key}[2]);
				}
			}
		}elsif($fwdfwsettings{$grp} eq 'cust_host_'.$val){
			&General::readhasharray("$confighost", \%customhost);
			foreach my $key (keys %customhost){
				if($customhost{$key}[0] eq $fwdfwsettings{$fwdfwsettings{$grp}}){
					if ($customhost{$key}[1] eq 'ip'){
						($a,$b)=split (/\//,$customhost{$key}[2]);
						$b=&General::iporsubtocidr($b);
					}else{
						if ($grp eq 'grp2'){
							$errormessage=$Lang::tr{'fwdfw err tgt_mac'};
						}
					}
				}
			}
		}
	}
	return $a,$b;
}
sub get_name
{
	my $val=shift;
	&General::setup_default_networks(\%defaultNetworks);
	foreach my $network (sort keys %defaultNetworks)
	{
		return "$network" if ($val eq $defaultNetworks{$network}{'NAME'});
	}
}
sub getsrcport
{
	my %hash=%{(shift)};
	my $key=shift;
	if($hash{$key}[7] eq 'ON' && $hash{$key}[10]){
		$hash{$key}[10]=~ s/\|/,/g;
		print": $hash{$key}[10]";
	}elsif($hash{$key}[7] eq 'ON' && $hash{$key}[8] eq 'ICMP'){
		print": <br>$hash{$key}[9] ";
	}
}
sub gettgtport
{
	my %hash=%{(shift)};
	my $key=shift;
	my $service;
	my $prot;
	if($hash{$key}[11] eq 'ON' && $hash{$key}[12] ne 'ICMP'){
		if($hash{$key}[14] eq 'cust_srv'){
			&General::readhasharray("$configsrv", \%customservice);
			foreach my $i (sort keys %customservice){
				if($customservice{$i}[0] eq $hash{$key}[15]){
					$service = $customservice{$i}[0];
				}
			}
		}elsif($hash{$key}[14] eq 'cust_srvgrp'){
			$service=$hash{$key}[15];
		}elsif($hash{$key}[14] eq 'TGT_PORT'){
			$hash{$key}[15]=~ s/\|/,/g;
			$service=$hash{$key}[15];
		}
		if($service){
			print": $service";
		}
	}
}
sub get_serviceports
{
	my $type=shift;
	my $name=shift;
	&General::readhasharray("$configsrv", \%customservice);
	&General::readhasharray("$configsrvgrp", \%customservicegrp);
	@protocols=();
	my @specprot=("IPIP","IPV6","IGMP","GRE","AH","ESP");
	if($type eq 'service'){
		foreach my $key (sort { ncmp($customservice{$a}[0],$customservice{$b}[0]) } keys %customservice){
			if ($customservice{$key}[0] eq $name){
				push (@protocols,$customservice{$key}[2]);
			}
		}
	}elsif($type eq 'group'){
		foreach my $key (sort { ncmp($customservicegrp{$a}[0],$customservicegrp{$b}[0]) } keys %customservicegrp){
			if ($customservicegrp{$key}[0] eq $name){
				if ($customservicegrp{$key}[2] ~~ @specprot){
					push (@protocols," ".$customservicegrp{$key}[2]);
				}else{
					foreach my $key1 (sort { ncmp($customservice{$a}[0],$customservice{$b}[0]) } keys %customservice){
						if ($customservice{$key1}[0] eq $customservicegrp{$key}[2]){
							if (!grep(/$customservice{$key1}[2]/, @protocols)){
								push (@protocols,$customservice{$key1}[2]);}
						}
					}
				}
			}
		}
	}

	# Sort protocols alphabetically.
	@protocols = sort(@protocols);

	return @protocols;
}
sub getcolor
{
	my $nettype=shift;
	my $val=shift;
	my $hash=shift;
	if($optionsfw{'SHOWCOLORS'} eq 'on'){
		# Don't colourise MAC addresses
		if (&General::validmac($val)) {
			$tdcolor = "";
			return;
		}

		#custom Hosts
		if ($nettype eq 'cust_host_src' || $nettype eq 'cust_host_tgt'){
			foreach my $key (sort keys %$hash){
				if ($$hash{$key}[0] eq $val){
					$val=$$hash{$key}[2];
				}
			}
		}
		#standard networks
		if ($val eq 'GREEN'){
			$tdcolor="style='background-color: $Header::colourgreen;color:white;'";
			return;
		}elsif ($val eq 'ORANGE'){
			$tdcolor="style='background-color:  $Header::colourorange;color:white;'";
			return;
		}elsif ($val eq 'BLUE'){
			$tdcolor="style='background-color: $Header::colourblue;color:white;'";
			return;
		}elsif ($val eq 'RED' ||$val eq 'RED1' ){
			$tdcolor="style='background-color: $Header::colourred;color:white;'";
			return;
		}elsif ($val eq 'IPFire' ){
			$tdcolor="style='background-color: $Header::colourred;color:white;'";
			return;
		}elsif ($val eq 'OpenVPN-Dyn' ){
			$tdcolor="style='background-color: $Header::colourovpn;color:white;'";
			return;
		}elsif ($val eq 'IPsec RW' ){
			$tdcolor="style='background-color: $Header::colourvpn;color:white;'";
			return;
		}elsif($val =~ /^(.*?)\/(.*?)$/){
			my ($sip,$scidr) = split ("/",$val);
			if ( &Header::orange_used() && &General::IpInSubnet($sip,$netsettings{'ORANGE_ADDRESS'},$netsettings{'ORANGE_NETMASK'})){
				$tdcolor="style='background-color: $Header::colourorange;color:white;'";
				return;
			}
			if ( &General::IpInSubnet($sip,$netsettings{'GREEN_ADDRESS'},$netsettings{'GREEN_NETMASK'})){
				$tdcolor="style='background-color: $Header::colourgreen;color:white;'";
				return;
			}
			if ( &Header::blue_used() && &General::IpInSubnet($sip,$netsettings{'BLUE_ADDRESS'},$netsettings{'BLUE_NETMASK'})){
				$tdcolor="style='background-color: $Header::colourblue;color:white;'";
				return;
			}
		}elsif ($val eq 'Default IP'){
			$tdcolor="style='background-color: $Header::colourred;color:white;'";
			return;
		}
		#Check if a manual IP or custom host is part of a VPN
		if ($nettype eq 'src_addr' || $nettype eq 'tgt_addr' || $nettype eq 'cust_host_src' || $nettype eq 'cust_host_tgt'){
			#Check if IP is part of OpenVPN dynamic subnet
			my ($a,$b) = split("/",$ovpnsettings{'DOVPN_SUBNET'});
			my ($c,$d) = split("/",$val);
			if (&General::IpInSubnet($c,$a,$b)){
				$tdcolor="style='background-color: $Header::colourovpn;color:white;'";
				return;
			}
			#Check if IP is part of OpenVPN static subnet
			foreach my $key (sort keys %ccdnet){
				my ($a,$b) = split("/",$ccdnet{$key}[1]);
				$b =&General::iporsubtodec($b);
				if (&General::IpInSubnet($c,$a,$b)){
					$tdcolor="style='background-color: $Header::colourovpn;color:white;'";
					return;
				}
			}
			#Check if IP is part of OpenVPN N2N subnet
			foreach my $key (sort keys %ccdhost){
				if ($ccdhost{$key}[3] eq 'net'){
					my ($a,$b) = split("/",$ccdhost{$key}[11]);
					if (&General::IpInSubnet($c,$a,$b)){
						$tdcolor="style='background-color: $Header::colourovpn;color:white;'";
						return;
					}
				}
			}
			#Check if IP is part of IPsec RW network
			if ($ipsecsettings{'RW_NET'} ne ''){
				my ($a,$b) = split("/",$ipsecsettings{'RW_NET'});
				$b=&General::iporsubtodec($b);
				if (&General::IpInSubnet($c,$a,$b)){
					$tdcolor="style='background-color: $Header::colourvpn;color:white;'";
					return;
				}
			}
			#Check if IP is part of a IPsec N2N network
			foreach my $key (sort keys %ipsecconf){
				if ($ipsecconf{$key}[11]){
					my ($a,$b) = split("/",$ipsecconf{$key}[11]);
					$b=&General::iporsubtodec($b);
					if (&General::IpInSubnet($c,$a,$b)){
						$tdcolor="style='background-color: $Header::colourvpn;color:white;'";
						return;
					}
				}
			}
		}
		#VPN networks
		if ($nettype eq 'ovpn_n2n_src' || $nettype eq 'ovpn_n2n_tgt' || $nettype eq 'ovpn_net_src' || $nettype eq 'ovpn_net_tgt'|| $nettype eq 'ovpn_host_src' || $nettype eq 'ovpn_host_tgt'){
			$tdcolor="style='background-color: $Header::colourovpn;color:white;'";
			return;
		}
		if ($nettype eq 'ipsec_net_src' || $nettype eq 'ipsec_net_tgt'){
			$tdcolor="style='background-color: $Header::colourvpn;color:white;'";
			return;
		}
		#ALIASE
		foreach my $alias (sort keys %aliases)
		{
			if ($val eq $alias){
				$tdcolor="style='background-color:$Header::colourred;color:white;'";
				return;
			}
		}
	}
	$tdcolor='';
	return;
}
sub hint
{
	if ($hint) {
		&Header::openbox('100%', 'left', $Lang::tr{'fwhost hint'});
		print "<class name='base'>$hint\n";
		print "&nbsp;</class>\n";
		&Header::closebox();
	}
}
sub newrule
{
	&error;
	&General::setup_default_networks(\%defaultNetworks);
	&General::readhash("/var/ipfire/ethernet/settings", \%netsettings);
	#read all configfiles
	&General::readhasharray("$configccdnet", \%ccdnet);
	&General::readhasharray("$confignet", \%customnetwork);
	&General::readhasharray("$configccdhost", \%ccdhost);
	&General::readhasharray("$confighost", \%customhost);
	&General::readhasharray("$configccdhost", \%ccdhost);
	&General::readhasharray("$configgrp", \%customgrp);
	&General::readhasharray("$configgeoipgrp", \%customgeoipgrp);
	&General::readhasharray("$configipsec", \%ipsecconf);
	&General::get_aliases(\%aliases);
	my %checked=();
	my $helper;
	my $sum=0;
	if($fwdfwsettings{'config'} eq ''){$fwdfwsettings{'config'}=$configfwdfw;}
	my $config=$fwdfwsettings{'config'};
	my %hash=();
	#Get Red IP-ADDRESS
	open (CONN1,"/var/ipfire/red/local-ipaddress");
	my $redip = <CONN1>;
	close(CONN1);
	if (! $fwdfwsettings{'RULE_ACTION'} && $fwdfwsettings{'POLICY'} eq 'MODE2'){
		$fwdfwsettings{'RULE_ACTION'}='DROP';
	}elsif(! $fwdfwsettings{'RULE_ACTION'} && $fwdfwsettings{'POLICY'} eq 'MODE1'){
		$fwdfwsettings{'RULE_ACTION'}='ACCEPT';
	}
	$checked{'grp1'}{$fwdfwsettings{'grp1'}} 				= 'CHECKED';
	$checked{'grp2'}{$fwdfwsettings{'grp2'}} 				= 'CHECKED';
	$checked{'grp3'}{$fwdfwsettings{'grp3'}} 				= 'CHECKED';
	$checked{'USE_SRC_PORT'}{$fwdfwsettings{'USE_SRC_PORT'}} = 'CHECKED';
	$checked{'USESRV'}{$fwdfwsettings{'USESRV'}} 			= 'CHECKED';
	$checked{'ACTIVE'}{$fwdfwsettings{'ACTIVE'}} 			= 'CHECKED';
	$checked{'LOG'}{$fwdfwsettings{'LOG'}} 					= 'CHECKED';
	$checked{'TIME'}{$fwdfwsettings{'TIME'}} 				= 'CHECKED';
	$checked{'TIME_MON'}{$fwdfwsettings{'TIME_MON'}} 		= 'CHECKED';
	$checked{'TIME_TUE'}{$fwdfwsettings{'TIME_TUE'}} 		= 'CHECKED';
	$checked{'TIME_WED'}{$fwdfwsettings{'TIME_WED'}} 		= 'CHECKED';
	$checked{'TIME_THU'}{$fwdfwsettings{'TIME_THU'}} 		= 'CHECKED';
	$checked{'TIME_FRI'}{$fwdfwsettings{'TIME_FRI'}} 		= 'CHECKED';
	$checked{'TIME_SAT'}{$fwdfwsettings{'TIME_SAT'}} 		= 'CHECKED';
	$checked{'TIME_SUN'}{$fwdfwsettings{'TIME_SUN'}} 		= 'CHECKED';
	$checked{'USE_NAT'}{$fwdfwsettings{'USE_NAT'}} 			= 'CHECKED';
	$selected{'TIME_FROM'}{$fwdfwsettings{'TIME_FROM'}}		= 'selected';
	$selected{'TIME_TO'}{$fwdfwsettings{'TIME_TO'}}			= 'selected';
	$selected{'ipfire'}{$fwdfwsettings{$fwdfwsettings{'grp2'}}} ='selected';
	$selected{'ipfire_src'}{$fwdfwsettings{$fwdfwsettings{'grp1'}}} ='selected';
	#check if update and get values
	if($fwdfwsettings{'updatefwrule'} eq 'on' || $fwdfwsettings{'copyfwrule'} eq 'on' && !$errormessage){
		&General::readhasharray("$config", \%hash);
		foreach my $key (sort keys %hash){
			$sum++;
			if ($key eq $fwdfwsettings{'key'}){
				$fwdfwsettings{'oldrulenumber'}			= $fwdfwsettings{'key'};
				$fwdfwsettings{'RULE_ACTION'}			= $hash{$key}[0];
				$fwdfwsettings{'chain'}					= $hash{$key}[1];
				$fwdfwsettings{'ACTIVE'}				= $hash{$key}[2];
				$fwdfwsettings{'grp1'}					= $hash{$key}[3];   
				$fwdfwsettings{$fwdfwsettings{'grp1'}}	= $hash{$key}[4];   
				$fwdfwsettings{'grp2'}					= $hash{$key}[5];   
				$fwdfwsettings{$fwdfwsettings{'grp2'}}	= $hash{$key}[6];   
				$fwdfwsettings{'USE_SRC_PORT'}			= $hash{$key}[7];
				$fwdfwsettings{'PROT'}					= $hash{$key}[8];
			    $fwdfwsettings{'ICMP_TYPES'}			= $hash{$key}[9];
			    $fwdfwsettings{'SRC_PORT'}				= $hash{$key}[10];
			    $fwdfwsettings{'USESRV'}				= $hash{$key}[11];
			    $fwdfwsettings{'TGT_PROT'}				= $hash{$key}[12];
			    $fwdfwsettings{'ICMP_TGT'}				= $hash{$key}[13];
			    $fwdfwsettings{'grp3'}					= $hash{$key}[14];
			    $fwdfwsettings{$fwdfwsettings{'grp3'}}	= $hash{$key}[15];
			    $fwdfwsettings{'ruleremark'}			= $hash{$key}[16];
			    $fwdfwsettings{'LOG'}					= $hash{$key}[17];
			    $fwdfwsettings{'TIME'}					= $hash{$key}[18];
				$fwdfwsettings{'TIME_MON'}				= $hash{$key}[19];
				$fwdfwsettings{'TIME_TUE'}				= $hash{$key}[20];
				$fwdfwsettings{'TIME_WED'}				= $hash{$key}[21];
				$fwdfwsettings{'TIME_THU'}				= $hash{$key}[22];
				$fwdfwsettings{'TIME_FRI'}				= $hash{$key}[23];
				$fwdfwsettings{'TIME_SAT'}				= $hash{$key}[24];
				$fwdfwsettings{'TIME_SUN'}				= $hash{$key}[25];
				$fwdfwsettings{'TIME_FROM'}				= $hash{$key}[26];
				$fwdfwsettings{'TIME_TO'}				= $hash{$key}[27];
				$fwdfwsettings{'USE_NAT'}				= $hash{$key}[28];
				$fwdfwsettings{'nat'}					= $hash{$key}[31]; #changed order
				$fwdfwsettings{$fwdfwsettings{'nat'}}	= $hash{$key}[29];
				$fwdfwsettings{'dnatport'}				= $hash{$key}[30];
				$fwdfwsettings{'LIMIT_CON_CON'}			= $hash{$key}[32];
				$fwdfwsettings{'concon'}				= $hash{$key}[33];
				$fwdfwsettings{'RATE_LIMIT'}			= $hash{$key}[34];
				$fwdfwsettings{'ratecon'}				= $hash{$key}[35];
				$fwdfwsettings{'RATETIME'}				= $hash{$key}[36];
				$checked{'grp1'}{$fwdfwsettings{'grp1'}} 				= 'CHECKED';
				$checked{'grp2'}{$fwdfwsettings{'grp2'}} 				= 'CHECKED';
				$checked{'grp3'}{$fwdfwsettings{'grp3'}} 				= 'CHECKED';
				$checked{'USE_SRC_PORT'}{$fwdfwsettings{'USE_SRC_PORT'}} = 'CHECKED';
				$checked{'USESRV'}{$fwdfwsettings{'USESRV'}} 			= 'CHECKED';
				$checked{'ACTIVE'}{$fwdfwsettings{'ACTIVE'}} 			= 'CHECKED';
				$checked{'LOG'}{$fwdfwsettings{'LOG'}} 					= 'CHECKED';
				$checked{'TIME'}{$fwdfwsettings{'TIME'}} 				= 'CHECKED';
				$checked{'TIME_MON'}{$fwdfwsettings{'TIME_MON'}} 		= 'CHECKED';
				$checked{'TIME_TUE'}{$fwdfwsettings{'TIME_TUE'}} 		= 'CHECKED';
				$checked{'TIME_WED'}{$fwdfwsettings{'TIME_WED'}} 		= 'CHECKED';
				$checked{'TIME_THU'}{$fwdfwsettings{'TIME_THU'}} 		= 'CHECKED';
				$checked{'TIME_FRI'}{$fwdfwsettings{'TIME_FRI'}} 		= 'CHECKED';
				$checked{'TIME_SAT'}{$fwdfwsettings{'TIME_SAT'}} 		= 'CHECKED';
				$checked{'TIME_SUN'}{$fwdfwsettings{'TIME_SUN'}} 		= 'CHECKED';
				$checked{'USE_NAT'}{$fwdfwsettings{'USE_NAT'}}	 		= 'CHECKED';
				$checked{'nat'}{$fwdfwsettings{'nat'}}					= 'CHECKED';
				$checked{'LIMIT_CON_CON'}{$fwdfwsettings{'LIMIT_CON_CON'}}	= 'CHECKED';
				$checked{'RATE_LIMIT'}{$fwdfwsettings{'RATE_LIMIT'}}	= 'CHECKED';
				$selected{'TIME_FROM'}{$fwdfwsettings{'TIME_FROM'}}		= 'selected';
				$selected{'TIME_TO'}{$fwdfwsettings{'TIME_TO'}}			= 'selected';
				$selected{'ipfire'}{$fwdfwsettings{$fwdfwsettings{'grp2'}}} ='selected';
				$selected{'ipfire_src'}{$fwdfwsettings{$fwdfwsettings{'grp1'}}} ='selected';
				$selected{'dnat'}{$fwdfwsettings{'dnat'}}				='selected';
				$selected{'snat'}{$fwdfwsettings{'snat'}}				='selected';
				$selected{'RATETIME'}{$fwdfwsettings{'RATETIME'}}		='selected';
			}
		}
		$fwdfwsettings{'oldgrp1a'}=$fwdfwsettings{'grp1'};
		$fwdfwsettings{'oldgrp1b'}=$fwdfwsettings{$fwdfwsettings{'grp1'}};
		$fwdfwsettings{'oldgrp2a'}=$fwdfwsettings{'grp2'};
		$fwdfwsettings{'oldgrp2b'}=$fwdfwsettings{$fwdfwsettings{'grp2'}};
		$fwdfwsettings{'oldgrp3a'}=$fwdfwsettings{'grp3'};
		$fwdfwsettings{'oldgrp3b'}=$fwdfwsettings{$fwdfwsettings{'grp3'}};
		$fwdfwsettings{'oldusesrv'}=$fwdfwsettings{'USESRV'};
		$fwdfwsettings{'oldruleremark'}=$fwdfwsettings{'ruleremark'};
		$fwdfwsettings{'oldnat'}=$fwdfwsettings{'USE_NAT'};
		$fwdfwsettings{'oldruletype'}=$fwdfwsettings{'chain'};
		$fwdfwsettings{'oldconcon'}=$fwdfwsettings{'LIMIT_CON_CON'};
		$fwdfwsettings{'olduseratelimit'}=$fwdfwsettings{'RATE_LIMIT'};
		$fwdfwsettings{'olduseratelimitamount'}=$fwdfwsettings{'ratecon'};
		$fwdfwsettings{'oldratelimittime'}=$fwdfwsettings{'RATETIME'};

		#check if manual ip (source) is orange network
		if ($fwdfwsettings{'grp1'} eq 'src_addr'){
			my ($sip,$scidr) = split("/",$fwdfwsettings{$fwdfwsettings{'grp1'}});
			if ( &General::IpInSubnet($sip,$netsettings{'ORANGE_ADDRESS'},$netsettings{'ORANGE_NETMASK'})){
				$fwdfwsettings{'oldorange'} ='on';
			}
		}
	}else{
		$fwdfwsettings{'ACTIVE'}='ON';
		$fwdfwsettings{'nat'} = 'dnat';
		$checked{'ACTIVE'}{$fwdfwsettings{'ACTIVE'}} = 'CHECKED';
		$checked{'nat'}{$fwdfwsettings{'nat'}} = 'CHECKED';
		$fwdfwsettings{'oldgrp1a'}=$fwdfwsettings{'grp1'};
		$fwdfwsettings{'oldgrp1b'}=$fwdfwsettings{$fwdfwsettings{'grp1'}};
		$fwdfwsettings{'oldgrp2a'}=$fwdfwsettings{'grp2'};
		$fwdfwsettings{'oldgrp2b'}=$fwdfwsettings{$fwdfwsettings{'grp2'}};
		$fwdfwsettings{'oldgrp3a'}=$fwdfwsettings{'grp3'};
		$fwdfwsettings{'oldgrp3b'}=$fwdfwsettings{$fwdfwsettings{'grp3'}};
		$fwdfwsettings{'oldusesrv'}=$fwdfwsettings{'USESRV'};
		$fwdfwsettings{'oldruleremark'}=$fwdfwsettings{'ruleremark'};
		$fwdfwsettings{'oldnat'}=$fwdfwsettings{'USE_NAT'};
		$fwdfwsettings{'oldconcon'}=$fwdfwsettings{'LIMIT_CON_CON'};
		#check if manual ip (source) is orange network
		if ($fwdfwsettings{'grp1'} eq 'src_addr'){
			my ($sip,$scidr) = split("/",$fwdfwsettings{$fwdfwsettings{'grp1'}});
			if ( &General::IpInSubnet($sip,$netsettings{'ORANGE_ADDRESS'},$netsettings{'ORANGE_NETMASK'})){
				$fwdfwsettings{'oldorange'} ='on';
			}
		}	
	}
	# Split manual source and target address and delete the subnet
	my ($sip,$scidr) = split("/",$fwdfwsettings{$fwdfwsettings{'grp1'}});
	if ($scidr eq '32'){$fwdfwsettings{$fwdfwsettings{'grp1'}}=$sip;}
	my ($dip,$dcidr) = split("/",$fwdfwsettings{$fwdfwsettings{'grp2'}});
	if ($dcidr eq '32'){$fwdfwsettings{$fwdfwsettings{'grp2'}}=$dip;}
	&Header::openbox('100%', 'left', $Lang::tr{'fwdfw source'});
	#------SOURCE-------------------------------------------------------
	print "<form method='post'>";
	print<<END;
		<table width='100%' border='0'>
		<tr><td width='1%'><input type='radio' name='grp1' value='src_addr'  checked></td><td width='60%'>$Lang::tr{'fwdfw sourceip'}<input type='TEXT' name='src_addr' value='$fwdfwsettings{'src_addr'}' size='16' maxlength='18' ></td><td width='1%'><input type='radio' name='grp1' id='ipfire_src' value='ipfire_src'  $checked{'grp1'}{'ipfire_src'}></td><td><b>Firewall</b></td>
END
		print"<td align='right'><select name='ipfire_src' style='width:200px;'>";
		print "<option value='ALL' $selected{'ipfire_src'}{'ALL'}>$Lang::tr{'all'}</option>";
		print "<option value='GREEN' $selected{'ipfire_src'}{'GREEN'}>$Lang::tr{'green'} ($ifaces{'GREEN_ADDRESS'})</option>" if $ifaces{'GREEN_ADDRESS'};
		print "<option value='ORANGE' $selected{'ipfire_src'}{'ORANGE'}>$Lang::tr{'orange'} ($ifaces{'ORANGE_ADDRESS'})</option>" if (&Header::orange_used());
		print "<option value='BLUE' $selected{'ipfire_src'}{'BLUE'}>$Lang::tr{'blue'} ($ifaces{'BLUE_ADDRESS'})</option>" if (&Header::blue_used());
		print "<option value='RED1' $selected{'ipfire_src'}{'RED1'}>$Lang::tr{'red1'} ($redip)" if ($redip);
		if (! -z "${General::swroot}/ethernet/aliases"){
			foreach my $alias (sort keys %aliases)
			{
				print "<option value='$alias' $selected{'ipfire_src'}{$alias}>$alias ($aliases{$alias}{'IPT'})</option>";
			}
		}
		print<<END;
		</select></td></tr>
		<tr><td><br></td></tr>
		</table>
END
		&gen_dd_block('src','grp1');
		&Header::closebox();

		#---SNAT / DNAT ------------------------------------------------
		&Header::openbox('100%', 'left', 'NAT');
		print<<END;
			<label>
				<input type='checkbox' name='USE_NAT' id='USE_NAT' value="ON" $checked{'USE_NAT'}{'ON'}>
				$Lang::tr{'fwdfw use nat'}
			</label>
			<div class="NAT">
				<table class='fw-nat' width='100%' border='0'>
					<tr>
						<td width='5%'></td>
						<td width='40%'>
							<label>
								<input type='radio' name='nat'  value='dnat' $checked{'nat'}{'dnat'}>
								$Lang::tr{'fwdfw dnat'}
							</label>
						</td>
END

	print <<END;
						<td width='25%' align='right'><span class='dnat'>$Lang::tr{'dnat address'}:</span></td>
						<td width='30%'>
							<select name='dnat' class='dnat' style='width: 100%;'>
								<option value='AUTO' $selected{'dnat'}{'AUTO'}>- $Lang::tr{'automatic'} -</option>
								<option value='Default IP' $selected{'dnat'}{'Default IP'}>$Lang::tr{'red1'} ($redip)</option>
END
		if (%aliases) {
			foreach my $alias (sort keys %aliases) {
				print "<option value='$alias' $selected{'dnat'}{$alias}>$alias ($aliases{$alias}{'IPT'})</option>";
			}
		}
		#DNAT Dropdown
		foreach my $network (sort keys %defaultNetworks)
		{
			if ($defaultNetworks{$network}{'NAME'} eq 'BLUE'||$defaultNetworks{$network}{'NAME'} eq 'GREEN' ||$defaultNetworks{$network}{'NAME'} eq 'ORANGE'){
				print "<option value='$defaultNetworks{$network}{'NAME'}'";
				print " selected='selected'" if ($fwdfwsettings{'dnat'} eq $defaultNetworks{$network}{'NAME'});
				print ">$network ($defaultNetworks{$network}{'NET'})</option>";
			}
		}
		print "</select>";
		print "</tr>";

		#SNAT
		print <<END;
					<tr>
						<td width='5%'></td>
						<td width='40%'>
							<label>
								<input type='radio' name='nat'  value='snat' $checked{'nat'}{'snat'}>
								$Lang::tr{'fwdfw snat'}
							</label>
						</td>
						<td width='25%' align='right'><span class='snat'>$Lang::tr{'snat new source ip address'}:</span></td>
						<td width='30%'>
							<select name='snat' class='snat' style='width: 100%;'>
END

		foreach my $alias (sort keys %aliases) {
			print "<option value='$alias' $selected{'snat'}{$alias}>$alias ($aliases{$alias}{'IPT'})</option>";
		}
		# SNAT Dropdown
		foreach my $network (sort keys %defaultNetworks) {
			if ($defaultNetworks{$network}{'NAME'} eq 'BLUE'||$defaultNetworks{$network}{'NAME'} eq 'GREEN' ||$defaultNetworks{$network}{'NAME'} eq 'ORANGE'){
				print "<option value='$defaultNetworks{$network}{'NAME'}'";
				print " selected='selected'" if ($fwdfwsettings{'snat'} eq $defaultNetworks{$network}{'NAME'});
				print ">$network ($defaultNetworks{$network}{'NET'})</option>";
			}
		}
		print <<END;
							</select>
						</td>
					</tr>
				</table>
			</div>
END
		&Header::closebox();

		#---TARGET------------------------------------------------------
		&Header::openbox('100%', 'left', $Lang::tr{'fwdfw target'});
		print<<END;
		<table width='100%' border='0'>	
		<tr><td width='1%'><input type='radio' name='grp2' value='tgt_addr'  checked></td><td width='60%' nowrap='nowrap'>$Lang::tr{'fwdfw targetip'}<input type='TEXT' name='tgt_addr' value='$fwdfwsettings{'tgt_addr'}' size='16' maxlength='18'><td width='1%'><input type='radio' name='grp2' id='ipfire' value='ipfire'  $checked{'grp2'}{'ipfire'}></td><td><b>Firewall</b></td>
END
		print"<td align='right'><select name='ipfire' style='width:200px;'>";
		print "<option value='ALL' $selected{'ipfire'}{'ALL'}>$Lang::tr{'all'}</option>";
		print "<option value='GREEN' $selected{'ipfire'}{'GREEN'}>$Lang::tr{'green'} ($ifaces{'GREEN_ADDRESS'})</option>" if $ifaces{'GREEN_ADDRESS'};
		print "<option value='ORANGE' $selected{'ipfire'}{'ORANGE'}>$Lang::tr{'orange'} ($ifaces{'ORANGE_ADDRESS'})</option>" if (&Header::orange_used());
		print "<option value='BLUE' $selected{'ipfire'}{'BLUE'}>$Lang::tr{'blue'} ($ifaces{'BLUE_ADDRESS'})</option>"if (&Header::blue_used());
		print "<option value='RED1' $selected{'ipfire'}{'RED1'}>$Lang::tr{'red1'} ($redip)" if ($redip);
		if (! -z "${General::swroot}/ethernet/aliases"){
			foreach my $alias (sort keys %aliases)
			{
				print "<option value='$alias' $selected{'ipfire'}{$alias}>$alias ($aliases{$alias}{'IPT'})</option>";
			}
		}
		print<<END;
		</select></td></tr>
		<tr><td><br></td></tr></table>
END
		&gen_dd_block('tgt','grp2');
		&Header::closebox;
		#---PROTOCOL------------------------------------------------------
		$fwdfwsettings{'SRC_PORT'} =~ s/\|/,/g;
		$fwdfwsettings{'TGT_PORT'} =~ s/\|/,/g;
		$fwdfwsettings{'dnatport'} =~ tr/|/,/;

		# The dnatport may be empty, if it matches TGT_PORT
		if ($fwdfwsettings{'dnatport'} eq $fwdfwsettings{'TGT_PORT'}) {
			$fwdfwsettings{'dnatport'} = "";
		}

		&Header::openbox('100%', 'left', $Lang::tr{'fwhost prot'});
		#Fix Protocol for JQuery
		if ($fwdfwsettings{'grp3'} eq 'cust_srv' || $fwdfwsettings{'grp3'} eq 'cust_srvgrp'){
			$fwdfwsettings{'PROT'} = 'template';
		}
		print<<END;
			<table width='100%' border='0'>
				<tr>
					<td width="25%">
						<select name='PROT' id='protocol' style="width: 95px;">
END
		print "<option value=\"\"";
		if ($fwdfwsettings{'PROT'} eq '') {
			print " selected=\"selected\"";
		}
		print ">$Lang::tr{'all'}</option>";

		print "<option value=\"template\"";
		print " selected=\"selected\"" if ($fwdfwsettings{'grp3'} eq 'cust_srv' || $fwdfwsettings{'grp3'} eq 'cust_srvgrp');
		print ">- $Lang::tr{'template'} -</option>";

		foreach (@PROTOCOLS) {
			print"<option value=\"$_\"";
			if ($_ eq $fwdfwsettings{'PROT'}) {
				print " selected=\"selected\"";
			}
			if($_ eq "IPv6"){
				print ">$Lang::tr{'fwdfw prot41'}</option>";
			}else{
				print ">$_</option>";
			}
		}

		print<<END;
						</select>
					</td>
					<td width="75%">
						<table width='100%' border='0' id="PROTOCOL_ICMP_TYPES">
							<tr>
								<td width='20%'>$Lang::tr{'fwhost icmptype'}</td>
								<td colspan='2'>
									<select name='ICMP_TYPES' style='min-width:230px;'>
END
		&General::readhasharray("${General::swroot}/fwhosts/icmp-types", \%icmptypes);
		print"<option value='All ICMP-Types'>$Lang::tr{'fwdfw all icmp'}</option>";
		foreach my $key (sort { ncmp($icmptypes{$a}[0],$icmptypes{$b}[0]) }keys %icmptypes){
			if($fwdfwsettings{'ICMP_TYPES'} eq "$icmptypes{$key}[0]"){
				print"<option selected>$icmptypes{$key}[0] ($icmptypes{$key}[1])</option>";
			}else{
				print"<option>$icmptypes{$key}[0] ($icmptypes{$key}[1])</option>";
			}
		}

		print <<END;
									</select>
								</td>
							</tr>
						</table>

						<table width="100%" border="0" id="PROTOCOL_PORTS">
							<tr>
								<!-- #SOURCEPORT -->
								<td>
									$Lang::tr{'fwdfw use srcport'}
								</td>
								<td>
									<input type='text' name='SRC_PORT' value='$fwdfwsettings{'SRC_PORT'}' maxlength='20' size='18'>
								</td>
								<td width='10%'>
								</td>

								<!-- #TARGETPORT -->
								<td>
									$Lang::tr{'fwdfw use srv'}
								</td>

								<td>
									<input type='text' name='TGT_PORT' value='$fwdfwsettings{'TGT_PORT'}' maxlength='20' size='18'>
								</td>
							</tr>
							<tr class="NAT">
								<td colspan='3'></td>
								<td>$Lang::tr{'fwdfw external port nat'}:</td>
								<td>
									<input type='text' name='dnatport' value=\"$fwdfwsettings{'dnatport'}\" maxlength='20' size='18'>
								</td>
							</tr>
						</table>

						<table width="100%" border="0" id="PROTOCOL_TEMPLATE">
							<tr>
								<td>
									<input type='radio' name='grp3' id='cust_srv' value='cust_srv' checked>
									$Lang::tr{'fwhost cust service'}
								</td>
								<td>
									<select name='cust_srv' style='min-width: 230px;'>
END

		&General::readhasharray("$configsrv", \%customservice);
		foreach my $key (sort { ncmp($customservice{$a}[0],$customservice{$b}[0]) } keys %customservice){
			print"<option ";
			print"selected='selected'" if ($fwdfwsettings{$fwdfwsettings{'grp3'}} eq $customservice{$key}[0]);
			print"value='$customservice{$key}[0]'>$customservice{$key}[0]</option>";
		}

		print <<END;
									</select>
								</td>
							</tr>
							<tr>
								<td>
									<input type='radio' name='grp3' id='cust_srvgrp' value='cust_srvgrp' $checked{'grp3'}{'cust_srvgrp'}>
									$Lang::tr{'fwhost cust srvgrp'}
								</td>
								<td>
									<select name='cust_srvgrp' style='min-width:230px;'>
END

		&General::readhasharray("$configsrvgrp", \%customservicegrp);
		my $helper;
		foreach my $key (sort { ncmp($customservicegrp{$a}[0],$customservicegrp{$b}[0]) } keys %customservicegrp){
			if ($helper ne $customservicegrp{$key}[0] && $customservicegrp{$key}[2] ne 'none'){
				print"<option ";
				print"selected='selected'" if ($fwdfwsettings{$fwdfwsettings{'grp3'}} eq $customservicegrp{$key}[0]);
				print">$customservicegrp{$key}[0]</option>";
			}
			$helper=$customservicegrp{$key}[0];
		}

		print<<END;
									</select>
								</td>
							</tr>
						</table>
					</td>
				</tr>
			</table>
END

		&Header::closebox;
		$checked{"RULE_ACTION"}{$fwdfwsettings{'RULE_ACTION'}}	= 'CHECKED';
		print <<END;
			<center>
				<table width="80%" class='tbl' id='actions'>
					<tr>
						<td width="33%" align="center" bgcolor="$color{'color17'}">
							&nbsp;<br>&nbsp;
						</td>
						<td width="33%" align="center" bgcolor="$color{'color25'}">
							&nbsp;<br>&nbsp;
						</td>
						<td width="33%" align="center" bgcolor="$color{'color16'}">
							&nbsp;<br>&nbsp;
						</td>
					</tr>
					<tr>
						<td width="33%" align="center">
							<label>
								<input type="radio" name="RULE_ACTION" value="ACCEPT" $checked{"RULE_ACTION"}{"ACCEPT"}>
								<strong>$Lang::tr{'fwdfw ACCEPT'}</strong>
							</label>
						</td>
						<td width="33%" align="center">
							<label>
								<input type="radio" name="RULE_ACTION" value="DROP" $checked{"RULE_ACTION"}{"DROP"}>
								<strong>$Lang::tr{'fwdfw DROP'}</strong>
							</label>
						</td>
						<td width="33%" align="center">
							<label>
								<input type="radio" name="RULE_ACTION" value="REJECT" $checked{"RULE_ACTION"}{"REJECT"}>
								<strong>$Lang::tr{'fwdfw REJECT'}</strong>
							</label>
						</td>
					</tr>
				</table>
			</center>

			<br>
END
		#---Activate/logging/remark-------------------------------------
		&Header::openbox('100%', 'left', $Lang::tr{'fwdfw additional'});
		print<<END;
		<table width='100%' border='0'>
END
		print"<tr><td width='12%'>$Lang::tr{'remark'}:</td><td width='88%' align='left'><input type='text' name='ruleremark' maxlength='255' value='$fwdfwsettings{'ruleremark'}' style='width:99%;'></td></tr>";
		if($fwdfwsettings{'updatefwrule'} eq 'on' || $fwdfwsettings{'copyfwrule'} eq 'on'){
			print "<tr><td width='12%'>$Lang::tr{'fwdfw rulepos'}:</td><td><select name='rulepos' >";
			for (my $count =1; $count <= $sum; $count++){ 
				print"<option value='$count' ";
				print"selected='selected'" if($fwdfwsettings{'oldrulenumber'} eq $count);
				print">$count</option>";
			}
			print"</select></td></tr>";
		}else{
			print "<tr><td width='12%'>$Lang::tr{'fwdfw rulepos'}:</td><td><input type='text' name='rulepos' size='2'></td></tr>";
		}

		print<<END;
		</table>
		<table width='100%'>
			<tr>
END

		if ($fwdfwsettings{'updatefwrule'} eq 'on') {
			print <<END;
				<td>
					<input type='checkbox' name='ACTIVE' value="ON" $checked{'ACTIVE'}{'ON'}>
				</td>
				<td>$Lang::tr{'fwdfw rule activate'}</td>
END
		} else {
			print <<END;
				<td colspan="2">
					<input type="hidden" name="ACTIVE" value="ON">
				</td>
END
		}

		print <<END;
			</tr>
			<tr>
				<td>
					<input type='checkbox' name='LOG' value='ON' $checked{'LOG'}{'ON'}>
				</td>
				<td>$Lang::tr{'fwdfw log rule'}</td>
			</tr>
			<tr>
				<td width='1%'>
					<input type='checkbox' name='TIME' id="USE_TIME_CONSTRAINTS" value='ON' $checked{'TIME'}{'ON'}>
				</td>
				<td>$Lang::tr{'fwdfw timeframe'}</td>
			</tr>
			<tr id="TIME_CONSTRAINTS">
				<td colspan="2">
					<table width="66%" border="0">
						<tr>
							<td width="8em">&nbsp;</td>
							<td align="center">$Lang::tr{'advproxy monday'}</td>
							<td align="center">$Lang::tr{'advproxy tuesday'}</td>
							<td align="center">$Lang::tr{'advproxy wednesday'}</td>
							<td align="center">$Lang::tr{'advproxy thursday'}</td>
							<td align="center">$Lang::tr{'advproxy friday'}</td>
							<td align="center">$Lang::tr{'advproxy saturday'}</td>
							<td align="center">$Lang::tr{'advproxy sunday'}</td>
							<td>&nbsp;</td>
						</tr>
						<tr>
							<td width="8em">&nbsp;</td>
							<td align="center"><input type='checkbox' name='TIME_MON' value='on' $checked{'TIME_MON'}{'on'} ></td>
							<td align="center"><input type='checkbox' name='TIME_TUE' value='on' $checked{'TIME_TUE'}{'on'} ></td>
							<td align="center"><input type='checkbox' name='TIME_WED' value='on' $checked{'TIME_WED'}{'on'} ></td>
							<td align="center"><input type='checkbox' name='TIME_THU' value='on' $checked{'TIME_THU'}{'on'} ></td>
							<td align="center"><input type='checkbox' name='TIME_FRI' value='on' $checked{'TIME_FRI'}{'on'} ></td>
							<td align="center"><input type='checkbox' name='TIME_SAT' value='on' $checked{'TIME_SAT'}{'on'} ></td>
							<td align="center"><input type='checkbox' name='TIME_SUN' value='on' $checked{'TIME_SUN'}{'on'} ></td>
							<td>
								<select name='TIME_FROM'>
END
		for (my $i=0;$i<=23;$i++) {
			$i = sprintf("%02s",$i);
			for (my $j=0;$j<=45;$j+=15) {
				$j = sprintf("%02s",$j);
				my $time = $i.":".$j;
				print "<option $selected{'TIME_FROM'}{$time}>$i:$j</option>\n";
			}
		}
		print<<END;	
								</select> &dash;
								<select name='TIME_TO'>
END
		for (my $i=0;$i<=23;$i++) {
			$i = sprintf("%02s",$i);
			for (my $j=0;$j<=45;$j+=15) {
				$j = sprintf("%02s",$j);
				my $time = $i.":".$j;
				print "<option $selected{'TIME_TO'}{$time}>$i:$j</option>\n";
			}
		}
		print<<END;
								</select>
							</td>
						</tr>
					</table>
				</td>
			</tr>
			<tr>
				<td width='1%'>
					<input type='checkbox' name='LIMIT_CON_CON' id="USE_LIMIT_CONCURRENT_CONNECTIONS_PER_IP" value='ON' $checked{'LIMIT_CON_CON'}{'ON'}>
				</td>
				<td>$Lang::tr{'fwdfw limitconcon'}</td>
			</tr>
			<tr id="LIMIT_CON">
				<td colspan='2'>
					<table width='66%' border='0'>
						<tr>
							<td width="20em">&nbsp;</td>
							<td>$Lang::tr{'fwdfw maxconcon'}: <input type='text' name='concon' size='2' value="$fwdfwsettings{'concon'}"></td>
						</tr>
					</table>
				</td>
			</tr>
			<tr>
				<td width='1%'>
					<input type='checkbox' name='RATE_LIMIT' id="USE_RATELIMIT" value='ON' $checked{'RATE_LIMIT'}{'ON'}>
				</td>
				<td>$Lang::tr{'fwdfw ratelimit'}</td>
			</tr>
			<tr id="RATELIMIT">
				<td colspan='2'>
					<table width='66%' border='0'>
						<tr>
							<td width="20em">&nbsp;</td>
							<td>$Lang::tr{'fwdfw numcon'}: <input type='text' name='ratecon' size='2' value="$fwdfwsettings{'ratecon'}"> /
								<select name='RATETIME' style='width:100px;'>
									<option value='second' $selected{'RATETIME'}{'second'}>$Lang::tr{'age second'}</option>
									<option value='minute' $selected{'RATETIME'}{'minute'}>$Lang::tr{'minute'}</option>
									<option value='hour' $selected{'RATETIME'}{'hour'}>$Lang::tr{'hour'}</option>
								</select>
							</td>
						</tr>
					</table>
				</td>
			</tr>
		</table>
		<br>
END

		#---ACTION------------------------------------------------------
		if($fwdfwsettings{'updatefwrule'} ne 'on'){
			print<<END;
			<table border='0' width='100%'>
			<tr><td align='right'><input type='submit' value='$Lang::tr{'add'}' style='min-width:100px;' />
			<input type='hidden' name='config' value='$config' >
			<input type='hidden' name='ACTION' value='saverule' ></form>
			<form method='post' style='display:inline;'><input type='submit' value='$Lang::tr{'fwhost back'}' style='min-width:100px;'><input type='hidden' name='ACTION' value='reset'></form></td></tr>
			</table>
			<br>
END
		}else{
			print<<END;
			<table border='0' width='100%'>
			<tr><td align='right'><input type='submit' value='$Lang::tr{'fwdfw change'}' style='min-width:100px;' /><input type='hidden' name='updatefwrule' value='$fwdfwsettings{'updatefwrule'}'><input type='hidden' name='key' value='$fwdfwsettings{'key'}'>
			<input type='hidden' name='oldgrp1a' value='$fwdfwsettings{'oldgrp1a'}' />
			<input type='hidden' name='oldgrp1b' value='$fwdfwsettings{'oldgrp1b'}' />
			<input type='hidden' name='oldgrp2a' value='$fwdfwsettings{'oldgrp2a'}' />
			<input type='hidden' name='oldgrp2b' value='$fwdfwsettings{'oldgrp2b'}' />
			<input type='hidden' name='oldgrp3a' value='$fwdfwsettings{'oldgrp3a'}' />
			<input type='hidden' name='oldgrp3b' value='$fwdfwsettings{'oldgrp3b'}' />
			<input type='hidden' name='oldusesrv' value='$fwdfwsettings{'oldusesrv'}' />
			<input type='hidden' name='oldrulenumber' value='$fwdfwsettings{'oldrulenumber'}' />
			<input type='hidden' name='rulenumber' value='$fwdfwsettings{'rulepos'}' />
			<input type='hidden' name='oldruleremark' value='$fwdfwsettings{'oldruleremark'}' />
			<input type='hidden' name='oldorange' value='$fwdfwsettings{'oldorange'}' />
			<input type='hidden' name='oldnat' value='$fwdfwsettings{'oldnat'}' />
			<input type='hidden' name='oldruletype' value='$fwdfwsettings{'oldruletype'}' />
			<input type='hidden' name='oldconcon' value='$fwdfwsettings{'oldconcon'}' />
			<input type='hidden' name='ACTION' value='saverule' ></form><form method='post' style='display:inline'><input type='submit' value='$Lang::tr{'fwhost back'}' style='min-width:100px;'><input type='hidden' name='ACTION' value'reset'></td></td>
			</table></form>
END
		}
		&Header::closebox();
}
sub pos_up
{
	my %uphash=();
	my %tmp=();
	&General::readhasharray($fwdfwsettings{'config'}, \%uphash);
	foreach my $key (sort keys %uphash){
		if ($key eq $fwdfwsettings{'key'}) {
			my $last = $key -1;
			if (exists $uphash{$last}){
				#save rule last
				foreach my $y (0 .. $#{$uphash{$last}}) {
						$tmp{0}[$y] = $uphash{$last}[$y];
				}
				#copy active rule to last
				foreach my $i (0 .. $#{$uphash{$last}}) {
					$uphash{$last}[$i] = $uphash{$key}[$i];
				}
				#copy saved rule to actual position
				foreach my $x (0 .. $#{$tmp{0}}) {
						$uphash{$key}[$x] = $tmp{0}[$x];
				}
			}
		}
	}
	&General::writehasharray($fwdfwsettings{'config'}, \%uphash);
	&General::firewall_config_changed();
}
sub pos_down
{
	my %downhash=();
	my %tmp=();
	&General::readhasharray($fwdfwsettings{'config'}, \%downhash);
	foreach my $key (sort keys %downhash){
		if ($key eq $fwdfwsettings{'key'}) {
			my $next = $key + 1;
			if (exists $downhash{$next}){
				#save rule next
				foreach my $y (0 .. $#{$downhash{$next}}) {
						$tmp{0}[$y] = $downhash{$next}[$y];
				}
				#copy active rule to next
				foreach my $i (0 .. $#{$downhash{$next}}) {
					$downhash{$next}[$i] = $downhash{$key}[$i];
				}
				#copy saved rule to actual position
				foreach my $x (0 .. $#{$tmp{0}}) {
						$downhash{$key}[$x] = $tmp{0}[$x];
				}
			}
		}
	}
	&General::writehasharray($fwdfwsettings{'config'}, \%downhash);
	&General::firewall_config_changed();
}
sub saverule
{
	my $hash=shift;
	my $config=shift;
	&General::readhasharray("$config", $hash);
	if (!$errormessage){
		################################################################
		#check if we change an INPUT rule to a OUTGOING
		if($fwdfwsettings{'oldruletype'} eq 'INPUTFW'  && $fwdfwsettings{'chain'} eq 'OUTGOINGFW'  ){
			&changerule($configinput);
			#print"1";
		}
		#check if we change an INPUT rule to a FORWARD
		elsif($fwdfwsettings{'oldruletype'} eq 'INPUTFW'  && $fwdfwsettings{'chain'} eq 'FORWARDFW'  ){
			&changerule($configinput);
			#print"2";
		}
		################################################################
		#check if we change an OUTGOING rule to an INPUT
		elsif($fwdfwsettings{'oldruletype'} eq 'OUTGOINGFW'  && $fwdfwsettings{'chain'} eq 'INPUTFW'  ){
			&changerule($configoutgoing);
			#print"3";
		}
		#check if we change an OUTGOING rule to a FORWARD
		elsif($fwdfwsettings{'oldruletype'} eq 'OUTGOINGFW'  && $fwdfwsettings{'chain'} eq 'FORWARDFW'  ){
			&changerule($configoutgoing);
			#print"4";
		}
		################################################################
		#check if we change a FORWARD rule to an INPUT
		elsif($fwdfwsettings{'oldruletype'} eq 'FORWARDFW'  && $fwdfwsettings{'chain'} eq 'INPUTFW'){
			&changerule($configfwdfw);
			#print"5";
		}
		#check if we change a FORWARD rule to an OUTGOING
		elsif($fwdfwsettings{'oldruletype'} eq 'FORWARDFW'  && $fwdfwsettings{'chain'} eq 'OUTGOINGFW'){
			&changerule($configfwdfw);
			#print"6";
		}
		$fwdfwsettings{'ruleremark'}=~ s/,/;/g;
		utf8::decode($fwdfwsettings{'ruleremark'});
		$fwdfwsettings{'ruleremark'}=&Header::escape($fwdfwsettings{'ruleremark'});
		if ($fwdfwsettings{'updatefwrule'} ne 'on'){
			my $key = &General::findhasharraykey ($hash);
			$$hash{$key}[0]  = $fwdfwsettings{'RULE_ACTION'};
			$$hash{$key}[1]  = $fwdfwsettings{'chain'};
			$$hash{$key}[2]  = $fwdfwsettings{'ACTIVE'};
			$$hash{$key}[3]  = $fwdfwsettings{'grp1'};
			$$hash{$key}[4]  = $fwdfwsettings{$fwdfwsettings{'grp1'}};
			$$hash{$key}[5]  = $fwdfwsettings{'grp2'};
			$$hash{$key}[6]  = $fwdfwsettings{$fwdfwsettings{'grp2'}};
			$$hash{$key}[7]  = $fwdfwsettings{'USE_SRC_PORT'};
			$$hash{$key}[8]  = $fwdfwsettings{'PROT'};
			$$hash{$key}[9]  = $fwdfwsettings{'ICMP_TYPES'};
			$$hash{$key}[10] = $fwdfwsettings{'SRC_PORT'};
			$$hash{$key}[11] = $fwdfwsettings{'USESRV'};
			$$hash{$key}[12] = $fwdfwsettings{'TGT_PROT'};
			$$hash{$key}[13] = $fwdfwsettings{'ICMP_TGT'};
			$$hash{$key}[14] = $fwdfwsettings{'grp3'};
			$$hash{$key}[15] = $fwdfwsettings{$fwdfwsettings{'grp3'}};
			$$hash{$key}[16] = $fwdfwsettings{'ruleremark'};
			$$hash{$key}[17] = $fwdfwsettings{'LOG'};
			$$hash{$key}[18] = $fwdfwsettings{'TIME'};
			$$hash{$key}[19] = $fwdfwsettings{'TIME_MON'};
			$$hash{$key}[20] = $fwdfwsettings{'TIME_TUE'};
			$$hash{$key}[21] = $fwdfwsettings{'TIME_WED'};
			$$hash{$key}[22] = $fwdfwsettings{'TIME_THU'};
			$$hash{$key}[23] = $fwdfwsettings{'TIME_FRI'};
			$$hash{$key}[24] = $fwdfwsettings{'TIME_SAT'};
			$$hash{$key}[25] = $fwdfwsettings{'TIME_SUN'};
			$$hash{$key}[26] = $fwdfwsettings{'TIME_FROM'};
			$$hash{$key}[27] = $fwdfwsettings{'TIME_TO'};
			$$hash{$key}[28] = $fwdfwsettings{'USE_NAT'};
			$$hash{$key}[29] = $fwdfwsettings{$fwdfwsettings{'nat'}};
			$$hash{$key}[30] = $fwdfwsettings{'dnatport'};
			$$hash{$key}[31] = $fwdfwsettings{'nat'};
			$$hash{$key}[32] = $fwdfwsettings{'LIMIT_CON_CON'};
			$$hash{$key}[33] = $fwdfwsettings{'concon'};
			$$hash{$key}[34] = $fwdfwsettings{'RATE_LIMIT'};
			$$hash{$key}[35] = $fwdfwsettings{'ratecon'};
			$$hash{$key}[36] = $fwdfwsettings{'RATETIME'};
			&General::writehasharray("$config", $hash);
		}else{
			foreach my $key (sort {$a <=> $b} keys %$hash){
				if($key eq $fwdfwsettings{'key'}){
					$$hash{$key}[0]  = $fwdfwsettings{'RULE_ACTION'};
					$$hash{$key}[1]  = $fwdfwsettings{'chain'};
					$$hash{$key}[2]  = $fwdfwsettings{'ACTIVE'};
					$$hash{$key}[3]  = $fwdfwsettings{'grp1'};
					$$hash{$key}[4]  = $fwdfwsettings{$fwdfwsettings{'grp1'}};
					$$hash{$key}[5]  = $fwdfwsettings{'grp2'};
					$$hash{$key}[6]  = $fwdfwsettings{$fwdfwsettings{'grp2'}};
					$$hash{$key}[7]  = $fwdfwsettings{'USE_SRC_PORT'};
					$$hash{$key}[8]  = $fwdfwsettings{'PROT'};
					$$hash{$key}[9]  = $fwdfwsettings{'ICMP_TYPES'};
					$$hash{$key}[10] = $fwdfwsettings{'SRC_PORT'};
					$$hash{$key}[11] = $fwdfwsettings{'USESRV'};
					$$hash{$key}[12] = $fwdfwsettings{'TGT_PROT'};
					$$hash{$key}[13] = $fwdfwsettings{'ICMP_TGT'};
					$$hash{$key}[14] = $fwdfwsettings{'grp3'};
					$$hash{$key}[15] = $fwdfwsettings{$fwdfwsettings{'grp3'}};
					$$hash{$key}[16] = $fwdfwsettings{'ruleremark'};
					$$hash{$key}[17] = $fwdfwsettings{'LOG'};
					$$hash{$key}[18] = $fwdfwsettings{'TIME'};
					$$hash{$key}[19] = $fwdfwsettings{'TIME_MON'};
					$$hash{$key}[20] = $fwdfwsettings{'TIME_TUE'};
					$$hash{$key}[21] = $fwdfwsettings{'TIME_WED'};
					$$hash{$key}[22] = $fwdfwsettings{'TIME_THU'};
					$$hash{$key}[23] = $fwdfwsettings{'TIME_FRI'};
					$$hash{$key}[24] = $fwdfwsettings{'TIME_SAT'};
					$$hash{$key}[25] = $fwdfwsettings{'TIME_SUN'};
					$$hash{$key}[26] = $fwdfwsettings{'TIME_FROM'};
					$$hash{$key}[27] = $fwdfwsettings{'TIME_TO'};
					$$hash{$key}[28] = $fwdfwsettings{'USE_NAT'};
					$$hash{$key}[29] = $fwdfwsettings{$fwdfwsettings{'nat'}};
					$$hash{$key}[30] = $fwdfwsettings{'dnatport'};
					$$hash{$key}[31] = $fwdfwsettings{'nat'};
					$$hash{$key}[32] = $fwdfwsettings{'LIMIT_CON_CON'};
					$$hash{$key}[33] = $fwdfwsettings{'concon'};
					$$hash{$key}[34] = $fwdfwsettings{'RATE_LIMIT'};
					$$hash{$key}[35] = $fwdfwsettings{'ratecon'};
					$$hash{$key}[36] = $fwdfwsettings{'RATETIME'};
					last;
				}
			}
		}
		&General::writehasharray("$config", $hash);
		if($fwdfwsettings{'oldrulenumber'} > $fwdfwsettings{'rulepos'}){
			my %tmp=();
			my $val=$fwdfwsettings{'oldrulenumber'}-$fwdfwsettings{'rulepos'};
			for (my $z=0;$z<$val;$z++){
				foreach my $key (sort {$a <=> $b} keys %$hash){
					if ($key eq $fwdfwsettings{'oldrulenumber'}) {
						my $last = $key -1;
						if (exists $$hash{$last}){
							#save rule last
							foreach my $y (0 .. $#{$$hash{$last}}) {
								$tmp{0}[$y] = $$hash{$last}[$y];
							}
							#copy active rule to last
							foreach my $i (0 .. $#{$$hash{$last}}) {
								$$hash{$last}[$i] = $$hash{$key}[$i];
							}
							#copy saved rule to actual position
							foreach my $x (0 .. $#{$tmp{0}}) {
								$$hash{$key}[$x] = $tmp{0}[$x];
							}
						}
					}
				}
				$fwdfwsettings{'oldrulenumber'}--;
			}
			&General::writehasharray("$config", $hash);
			&General::firewall_config_changed();
		}elsif($fwdfwsettings{'rulepos'} > $fwdfwsettings{'oldrulenumber'}){
			my %tmp=();
			my $val=$fwdfwsettings{'rulepos'}-$fwdfwsettings{'oldrulenumber'};
				for (my $z=0;$z<$val;$z++){
					foreach my $key (sort {$a <=> $b} keys %$hash){
					if ($key eq $fwdfwsettings{'oldrulenumber'}) {
						my $next = $key + 1;
						if (exists $$hash{$next}){
							#save rule next
							foreach my $y (0 .. $#{$$hash{$next}}) {
								$tmp{0}[$y] = $$hash{$next}[$y];
							}
							#copy active rule to next
							foreach my $i (0 .. $#{$$hash{$next}}) {
								$$hash{$next}[$i] = $$hash{$key}[$i];
							}
							#copy saved rule to actual position
							foreach my $x (0 .. $#{$tmp{0}}) {
								$$hash{$key}[$x] = $tmp{0}[$x];
							}
						}
					}
				}
				$fwdfwsettings{'oldrulenumber'}++;
			}
			&General::writehasharray("$config", $hash);
			&General::firewall_config_changed();
		}
	}
}
sub validremark
{
	# Checks a hostname against RFC1035
	my $remark = $_[0];

	# Try to decode $remark into UTF-8. If this doesn't work,
	# we assume that the string it not sane.
	if (!utf8::decode($remark)) {
		return 0;
	}

	# Check if the string only contains of printable characters.
	if ($remark =~ /^[[:print:]]*$/) {
		return 1;
	}
	return 0;
}
sub viewtablerule
{
	&General::readhash("/var/ipfire/ethernet/settings", \%netsettings);

	&viewtablenew(\%configfwdfw, $configfwdfw, $Lang::tr{'firewall rules'});
	&viewtablenew(\%configinputfw, $configinput, $Lang::tr{'incoming firewall access'});
	&viewtablenew(\%configoutgoingfw, $configoutgoing, $Lang::tr{'outgoing firewall access'});
}
sub viewtablenew
{
	my $hash=shift;
	my $config=shift;
	my $title=shift;
	my $go='';

	my $show_box = (! -z $config) || ($optionsfw{'SHOWTABLES'} eq 'on');
	return if (!$show_box);

	&General::get_aliases(\%aliases);
	&General::readhasharray("$confighost", \%customhost);
	&General::readhasharray("$config", $hash);
	&General::readhasharray("$configccdnet", \%ccdnet);
	&General::readhasharray("$configccdhost", \%ccdhost);
	&General::readhasharray("$configgrp", \%customgrp);
	&General::readhasharray("$configsrvgrp", \%customservicegrp);

	&Header::openbox('100%', 'left', $title);
	print "<table width='100%' cellspacing='0' class='tbl'>";

	if (! -z $config) {
		my $count=0;
		my ($gif,$log);
		my $ruletype;
		my $rulecolor;
		my $tooltip;
		my @tmpsrc=();
		my @tmptgt=();
		my $coloryellow='';

		print <<END;
				<tr>
					<th align='right' width='3%'>
						#
					</th>
					<th width='2%'></th>
					<th align='center'>
						<b>$Lang::tr{'protocol'}</b>
					</th>
					<th align='center' width='30%'>
						<b>$Lang::tr{'fwdfw source'}</b>
					</th>
					<th align='center'>
						<b>$Lang::tr{'fwdfw log'}</b>
					</th>
					<th align='center' width='30%'>
						<b>$Lang::tr{'fwdfw target'}</b>
					</th>
					<th align='center' colspan='6' width='18%'>
						<b>$Lang::tr{'fwdfw action'}</b>
					</th>
				</tr>
END

		foreach my $key (sort  {$a <=> $b} keys %$hash){
			$tdcolor='';
			@tmpsrc=();
			@tmptgt=();
			#check if vpn hosts/nets have been deleted
			if($$hash{$key}[3] =~ /ipsec/i || $$hash{$key}[3] =~ /ovpn/i){
				push (@tmpsrc,$$hash{$key}[4]);
			}
			if($$hash{$key}[5] =~ /ipsec/i || $$hash{$key}[5] =~ /ovpn/i){
				push (@tmptgt,$$hash{$key}[6]);
			}
			foreach my $host (@tmpsrc){
				if($$hash{$key}[3] eq  'ipsec_net_src'){
					if(&fwlib::get_ipsec_net_ip($host,11) eq ''){
						$coloryellow='on';
					}
				}elsif($$hash{$key}[3] eq  'ovpn_net_src'){
					if(&fwlib::get_ovpn_net_ip($host,1) eq ''){
						$coloryellow='on';
					}
				}elsif($$hash{$key}[3] eq  'ovpn_n2n_src'){
					if(&fwlib::get_ovpn_n2n_ip($host,27) eq ''){
						$coloryellow='on';
					}
				}elsif($$hash{$key}[3] eq  'ovpn_host_src'){
					if(&fwlib::get_ovpn_host_ip($host,33) eq ''){
						$coloryellow='on';
					}
				}
			}
			foreach my $host (@tmptgt){
				if($$hash{$key}[5] eq 'ipsec_net_tgt'){
					if(&fwlib::get_ipsec_net_ip($host,11) eq ''){
						$coloryellow='on';
					}
				}elsif($$hash{$key}[5] eq 'ovpn_net_tgt'){
					if(&fwlib::get_ovpn_net_ip($host,1) eq ''){
						$coloryellow='on';
					}
				}elsif($$hash{$key}[5] eq 'ovpn_n2n_tgt'){
					if(&fwlib::get_ovpn_n2n_ip($host,27) eq ''){
						$coloryellow='on';
					}
				}elsif($$hash{$key}[5] eq 'ovpn_host_tgt'){
					if(&fwlib::get_ovpn_host_ip($host,33) eq ''){
						$coloryellow='on';
					}
				}
			}
			#check if networkgroups or servicegroups are empty
			foreach my $netgroup (sort keys %customgrp){
				if(($$hash{$key}[4] eq $customgrp{$netgroup}[0] || $$hash{$key}[6] eq $customgrp{$netgroup}[0]) && $customgrp{$netgroup}[2] eq 'none'){
					$coloryellow='on';
				}
			}
			foreach my $srvgroup (sort keys %customservicegrp){
				if($$hash{$key}[15] eq $customservicegrp{$srvgroup}[0] && $customservicegrp{$srvgroup}[2] eq 'none'){
					$coloryellow='on';
				}
			}
			$$hash{'ACTIVE'}=$$hash{$key}[2];
			$count++;
			if($coloryellow eq 'on'){
				$color="$color{'color14'}";
				$coloryellow='';
			}elsif($coloryellow eq ''){
				if ($count % 2){ 
					$color="$color{'color22'}";
				}
				else{
					$color="$color{'color20'}";
				}
			}
			print<<END;
				<tr bgcolor='$color'>
					<td align='right' width='3%'>
						<b>$key&nbsp;</b>
					</td>
END

			#RULETYPE (A,R,D)
			if ($$hash{$key}[0] eq 'ACCEPT'){
				$ruletype='A';
				$tooltip='ACCEPT';
				$rulecolor=$color{'color17'};
			}elsif($$hash{$key}[0] eq 'DROP'){
				$ruletype='D';
				$tooltip='DROP';
				$rulecolor=$color{'color25'};
			}elsif($$hash{$key}[0] eq 'REJECT'){
				$ruletype='R';
				$tooltip='REJECT';
				$rulecolor=$color{'color16'};
			}

			print <<END;
					<td bgcolor='$rulecolor' align='center' width='2%'>
						<span title='$tooltip'>&nbsp;&nbsp;</span>
					</td>
END

			#Get Protocol
			my $prot;
			if ($$hash{$key}[8]){
				if ($$hash{$key}[8] eq "IPv6"){
					push (@protocols,$Lang::tr{'fwdfw prot41 short'})
				}else{
					push (@protocols,$$hash{$key}[8]);
				}
			}elsif($$hash{$key}[14] eq 'cust_srv'){
				&get_serviceports("service",$$hash{$key}[15]);
			}elsif($$hash{$key}[14] eq 'cust_srvgrp'){
				&get_serviceports("group",$$hash{$key}[15]);
			}else{
				push (@protocols,$Lang::tr{'all'});
			}

			my $protz=join(", ",@protocols);
			if($protz eq 'ICMP' && $$hash{$key}[9] ne 'All ICMP-Types' && $$hash{$key}[14] ne 'cust_srvgrp'){
				&General::readhasharray("${General::swroot}/fwhosts/icmp-types", \%icmptypes);
				foreach my $keyicmp (sort { ncmp($icmptypes{$a}[0],$icmptypes{$b}[0]) }keys %icmptypes){
					if($$hash{$key}[9] eq "$icmptypes{$keyicmp}[0]"){
						print "<td align='center'><span title='$icmptypes{$keyicmp}[0]'><b>$protz ($icmptypes{$keyicmp}[1])</b></span></td>";
						last;
					}
				}
			}elsif($#protocols gt '3'){
				print"<td align='center'><span title='$protz'>$Lang::tr{'fwdfw many'}</span></td>";
			}else{
				print"<td align='center'>$protz</td>";
			}
			@protocols=();
			#SOURCE
			my $ipfireiface;
			&getcolor($$hash{$key}[3],$$hash{$key}[4],\%customhost);
			# Check SRC Host and replace "|" with space
			if ($$hash{$key}[4] =~ /\|/){
				$$hash{$key}[4] =~ s/\|/ (/g;
				$$hash{$key}[4] = $$hash{$key}[4].")";
			}
			print"<td align='center' width='30%' $tdcolor>";
			if ($$hash{$key}[3] eq 'ipfire_src'){
				$ipfireiface=$Lang::tr{'fwdfw iface'};
			}
			if ($$hash{$key}[3] eq 'std_net_src'){
				print &get_name($$hash{$key}[4]);
			}elsif ($$hash{$key}[3] eq 'src_addr'){
				my ($split1,$split2) = split("/",$$hash{$key}[4]);
				if ($split2 eq '32'){
					print $split1;
				}else{
					print $$hash{$key}[4];
				}
			}elsif ($$hash{$key}[3] eq 'cust_geoip_src') {
				my ($split1,$split2) = split(":", $$hash{$key}[4]);
				if ($split2) {
					print "$split2\n";
				}else{
					print "$Lang::tr{'geoip'}: $$hash{$key}[4]\n";
				}
			}elsif ($$hash{$key}[4] eq 'RED1'){
				print "$ipfireiface $Lang::tr{'fwdfw red'}";
			}elsif ($$hash{$key}[4] eq 'ALL'){
				print "$ipfireiface $Lang::tr{'all'}";
			}else{
				if ($$hash{$key}[4] eq 'GREEN' || $$hash{$key}[4] eq 'ORANGE' || $$hash{$key}[4] eq 'BLUE' || $$hash{$key}[4] eq 'RED'){
					print "$ipfireiface $Lang::tr{lc($$hash{$key}[4])}";
				}else{
					print "$ipfireiface $$hash{$key}[4]";
				}
			}
			$tdcolor='';
			#SOURCEPORT
			&getsrcport(\%$hash,$key);
			#Is this a SNAT rule?
			if ($$hash{$key}[31] eq 'snat' && $$hash{$key}[28] eq 'ON'){
				my $net=&get_name($$hash{$key}[29]);
				if ( ! $net){ $net=$$hash{$key}[29];}
					print"<br>->$net";
				if ($$hash{$key}[30] ne ''){
					print": $$hash{$key}[30]";
				}
			}
			if ($$hash{$key}[17] eq 'ON'){
				$log="/images/on.gif";
			}else{
				$log="/images/off.gif";
			}
			#LOGGING
			print<<END;
					</td>
					<td align='center'>
						<form method='POST' action=''>
							<input type='image' img src='$log' alt='$Lang::tr{'click to disable'}' title='$Lang::tr{'fwdfw togglelog'}' style='padding-top: 0px; padding-left: 0px; padding-bottom: 0px ;padding-right: 0px ;'/>
							<input type='hidden' name='key' value='$key' />
							<input type='hidden' name='config' value='$config' />
							<input type='hidden' name='ACTION' value='$Lang::tr{'fwdfw togglelog'}' />
						</form>
					</td>
END
			#TARGET
			&getcolor($$hash{$key}[5],$$hash{$key}[6],\%customhost);
			print<<END;
					<td align='center' $tdcolor>
END
			# Check TGT Host and replace "|" with space
			if ($$hash{$key}[6] =~ /\|/){
				$$hash{$key}[6] =~ s/\|/ (/g;
				$$hash{$key}[6] = $$hash{$key}[6].")";
			}
			#Is this a DNAT rule?
			my $natstring;
			if ($$hash{$key}[31] eq 'dnat' && $$hash{$key}[28] eq 'ON'){
				if ($$hash{$key}[29] eq 'Default IP'){$$hash{$key}[29]=$Lang::tr{'red1'};}
				if ($$hash{$key}[29] eq 'AUTO'){
					my @src_addresses=&fwlib::get_addresses(\%$hash,$key,'src');
					my @nat_ifaces;
					foreach my $val (@src_addresses){
						push (@nat_ifaces,&fwlib::get_nat_address($$hash{$key}[29],$val));
					}
					@nat_ifaces=&del_double(@nat_ifaces);
					$natstring = "";
				}else{
					$natstring = "($$hash{$key}[29])";
				}
				print "$Lang::tr{'firewall'} $natstring";
				if($$hash{$key}[30] ne ''){
					$$hash{$key}[30]=~ tr/|/,/;
					print": $$hash{$key}[30]";
				}
				print"<br>-&gt;";
			}
			if ($$hash{$key}[5] eq 'std_net_tgt' || $$hash{$key}[5] eq 'ipfire'){
				if ($$hash{$key}[6] eq 'RED1'){
					print "$Lang::tr{'red1'}";
				}elsif ($$hash{$key}[6] eq 'GREEN' || $$hash{$key}[6] eq 'ORANGE' || $$hash{$key}[6] eq 'BLUE'|| $$hash{$key}[6] eq 'ALL' || $$hash{$key}[6] eq 'RED')
				{
					print &get_name($$hash{$key}[6]);
				}else{
					print $$hash{$key}[6];
				}
			}elsif ($$hash{$key}[5] eq 'cust_geoip_tgt') {
				my ($split1,$split2) = split(":", $$hash{$key}[6]);
				if ($split2) {
					print "$split2\n";
				}else{
					print "$Lang::tr{'geoip'}: $$hash{$key}[6]\n";
				}
			}elsif ($$hash{$key}[5] eq 'tgt_addr'){
				my ($split1,$split2) = split("/",$$hash{$key}[6]);
				if ($split2 eq '32'){
					print $split1;
				}else{
					print $$hash{$key}[6];
				}
			}else{
				print "$$hash{$key}[6]";
			}
			$tdcolor='';
			#TARGETPORT
			&gettgtport(\%$hash,$key);
			print"</td>";
			#RULE ACTIVE
			if($$hash{$key}[2] eq 'ON'){
				$gif="/images/on.gif"
			}else{
				$gif="/images/off.gif"
			}
			print<<END;
				<td width='3%' align='center'>
					<form method='POST' action=''>
						<input type='image' img src='$gif' alt='$Lang::tr{'click to disable'}' title='$Lang::tr{'fwdfw toggle'}' style='padding-top: 0px; padding-left: 0px; padding-bottom: 0px ;padding-right: 0px ;display: block;' />
						<input type='hidden' name='key' value='$key' />
						<input type='hidden' name='config' value='$config' />
						<input type='hidden' name='ACTION' value='$Lang::tr{'fwdfw toggle'}' />
					</form>
				</td>
				<td width='3%' align='center'>
					<form method='POST' action=''>
						<input type='image' img src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'fwdfw edit'}' style='padding-top: 0px; padding-left: 0px; padding-bottom: 0px ;padding-right: 0px ;display: block;'  />
						<input type='hidden' name='key' value='$key' />
						<input type='hidden' name='config' value='$config' />
						<input type='hidden' name='ACTION' value='editrule' />
					</form>
				</td>
				<td width='3%' align='center'>
					<form method='POST' action=''>
						<input type='image' img src='/images/addblue.gif' alt='$Lang::tr{'fwdfw copy'}' title='$Lang::tr{'fwdfw copy'}' style='padding-top: 0px; padding-left: 0px; padding-bottom: 0px ;padding-right: 0px ;display: block;' />
						<input type='hidden' name='key' value='$key' />
						<input type='hidden' name='config' value='$config' />
						<input type='hidden' name='ACTION' value='copyrule' />
					</form>
				</td>
				<td width='3%' align='center'>
					<form method='POST' action=''>
						<input type='image' img src='/images/delete.gif' alt='$Lang::tr{'delete'}' title='$Lang::tr{'fwdfw delete'}' style='padding-top: 0px; padding-left: 0px; padding-bottom: 0px ;padding-right: 0px ;display: block;'   />
						<input type='hidden' name='key' value='$key' />
						<input type='hidden' name='config' value='$config' />
						<input type='hidden' name='ACTION' value='deleterule' />
					</form>
				</td>
END
			if (exists $$hash{$key-1}){
				print<<END;
					<td width='3%' align='center'>
						<form method='POST' action=''>
							<input type='image' img src='/images/up.gif' alt='$Lang::tr{'fwdfw moveup'}' title='$Lang::tr{'fwdfw moveup'}'  style='padding-top: 0px; padding-left: 0px; padding-bottom: 0px ;padding-right: 0px ;display: block;'  />
							<input type='hidden' name='key' value='$key' />
							<input type='hidden' name='config' value='$config' />
							<input type='hidden' name='ACTION' value='moveup' />
						</form>
					</td>
END
			}else{
				print"<td width='3%'></td>";
			}

			if (exists $$hash{$key+1}){
				print<<END;
					<td width='3%' align='center'>
						<form method='POST' action=''>
							<input type='image' img src='/images/down.gif' alt='$Lang::tr{'fwdfw movedown'}' title='$Lang::tr{'fwdfw movedown'}' style='padding-top: 0px; padding-left: 0px; padding-bottom: 0px ;padding-right: 0px ;display: block;'  />
							<input type='hidden' name='key' value='$key' />
							<input type='hidden' name='config' value='$config' />
							<input type='hidden' name='ACTION' value='movedown' />
						</form>
					</td>
				</tr>
END
			}else{
				print"<td width='3%'></td></tr>";
			}
			#REMARK
			if ($optionsfw{'SHOWREMARK'} eq 'on' && $$hash{$key}[16] ne ''){
				print <<END;
					<tr bgcolor='$color'>
						<td>&nbsp;</td>
						<td bgcolor='$rulecolor'></td>
						<td colspan='10'>
							&nbsp; <em>$$hash{$key}[16]</em>
						</td>
					</tr>
END
			}

			if ($$hash{$key}[18] eq 'ON'){
				#TIMEFRAME
				if ($$hash{$key}[18] eq 'ON'){
					my @days=();
					if($$hash{$key}[19] ne ''){push (@days,$Lang::tr{'fwdfw wd_mon'});}
					if($$hash{$key}[20] ne ''){push (@days,$Lang::tr{'fwdfw wd_tue'});}
					if($$hash{$key}[21] ne ''){push (@days,$Lang::tr{'fwdfw wd_wed'});}
					if($$hash{$key}[22] ne ''){push (@days,$Lang::tr{'fwdfw wd_thu'});}
					if($$hash{$key}[23] ne ''){push (@days,$Lang::tr{'fwdfw wd_fri'});}
					if($$hash{$key}[24] ne ''){push (@days,$Lang::tr{'fwdfw wd_sat'});}
					if($$hash{$key}[25] ne ''){push (@days,$Lang::tr{'fwdfw wd_sun'});}
					my $weekdays=join(",",@days);
					if (@days){
						print"<tr bgcolor='$color'>";
						print"<td>&nbsp;</td><td bgcolor='$rulecolor'></td><td align='left' colspan='10'>&nbsp; $weekdays &nbsp; $$hash{$key}[26] - $$hash{$key}[27]</td></tr>";
					}
				}
			}
			print"<tr bgcolor='FFFFFF'><td colspan='13' height='1'></td></tr>";
		}
	} elsif ($optionsfw{'SHOWTABLES'} eq 'on') {
		print <<END;
			<tr>
				<td colspan='7' height='30' bgcolor=$color{'color22'} align='center'>$Lang::tr{'fwhost empty'}</td>
			</tr>
END
	}

	#SHOW FINAL RULE
	my $policy = 'fwdfw ' . $fwdfwsettings{'POLICY'};
	my $colour = "bgcolor='green'";
	if ($fwdfwsettings{'POLICY'} eq 'MODE1') {
		$colour = "bgcolor='darkred'";
	}

	my $message;
	if (($config eq '/var/ipfire/firewall/config') && ($fwdfwsettings{'POLICY'} ne 'MODE1')) {
		print <<END;
			<tr>
				<td colspan='13'>&nbsp;</td>
			</tr>
			<tr>
				<td colspan='13' style="padding-left:0px;padding-right:0px">
					<table width="100%" border='1' rules="cols" cellspacing='0'>
END

		# GREEN
		print <<END;
			<tr>
				<td align='center'>
					<font color="$Header::colourgreen">$Lang::tr{'green'}</font>
				</td>
				<td align='center'>
					<font color="$Header::colourred">$Lang::tr{'red'}</font>
					($Lang::tr{'fwdfw pol allow'})
				</td>
END

		if (&Header::orange_used()) {
			print <<END;
				<td align='center'>
					<font color="$Header::colourorange">$Lang::tr{'orange'}</font>
					($Lang::tr{'fwdfw pol allow'})
				</td>
END
		}

		if (&Header::blue_used()) {
			print <<END;
				<td align='center'>
					<font color="$Header::colourblue">$Lang::tr{'blue'}</font>
					($Lang::tr{'fwdfw pol allow'})
				</td>
END
		}

		print"</tr>";

		# ORANGE
		if (&Header::orange_used()) {
			print <<END;
				<tr>
					<td align='center' width='20%'>
						<font color="$Header::colourorange">$Lang::tr{'orange'}</font>
					</td>
					<td align='center'>
						<font color="$Header::colourred">$Lang::tr{'red'}</font>
						($Lang::tr{'fwdfw pol allow'})
					</td>
					<td align='center'>
						<font color="$Header::colourgreen">$Lang::tr{'green'}</font>
						($Lang::tr{'fwdfw pol block'})
					</td>
END

			if (&Header::blue_used()) {
				print <<END;
					<td align='center'>
						<font color="$Header::colourblue">$Lang::tr{'blue'}</font>
						($Lang::tr{'fwdfw pol block'})
					</td>
END
			}

			print"</tr>";
		}

		if (&Header::blue_used()) {
			print <<END;
				<tr>
					<td align='center'>
						<font color="$Header::colourblue">$Lang::tr{'blue'}</font>
					</td>
					<td align='center'>
						<font color="$Header::colourred">$Lang::tr{'red'}</font>
						($Lang::tr{'fwdfw pol allow'})
					</td>
END

			if (&Header::orange_used()) {
				print <<END;
					<td align='center'>
						<font color="$Header::colourorange">$Lang::tr{'orange'}</font>
						($Lang::tr{'fwdfw pol block'})
					</td>
END
			}

			print <<END;
					<td align='center'>
						<font color="$Header::colourgreen">$Lang::tr{'green'}</font>
						($Lang::tr{'fwdfw pol block'})
					</td>
				</tr>
END
		}

		print <<END;
					</table>
				</td>
			</tr>
END

		$message = $Lang::tr{'fwdfw pol allow'};

	} elsif ($config eq '/var/ipfire/firewall/outgoing' && ($fwdfwsettings{'POLICY1'} ne 'MODE1')) {
		$message = $Lang::tr{'fwdfw pol allow'};
		$colour = "bgcolor='green'";
	} else {
		$message = $Lang::tr{'fwdfw pol block'};
		$colour = "bgcolor='darkred'";
	}

	if ($message) {
		print <<END;
			<tr>
				<td $colour align='center' colspan='13'>
					<font color='#FFFFFF'>$Lang::tr{'policy'}: $message</font>
				</td>
			</tr>
END
	}

	print "</table>";
	print "<br>";

	&Header::closebox();
}

&Header::closebigbox();
&Header::closepage();
