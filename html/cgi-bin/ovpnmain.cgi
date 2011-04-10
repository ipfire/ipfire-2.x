#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007  Michael Tremer & Christian Schmidt                      #
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

use CGI;
use CGI qw/:standard/;
use Net::DNS;
use File::Copy;
use File::Temp qw/ tempfile tempdir /;
use strict;
use Archive::Zip qw(:ERROR_CODES :CONSTANTS);
require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "${General::swroot}/countries.pl";

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';
#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::colourgreen} );
undef (@dummy);

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

###
### Initialize variables
###
my %netsettings=();
my %cgiparams=();
my %vpnsettings=();
my %checked=();
my %confighash=();
my %cahash=();
my %selected=();
my $warnmessage = '';
my $errormessage = '';
my %settings=();
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
$cgiparams{'ENABLED'} = 'off';
$cgiparams{'ENABLED_BLUE'} = 'off';
$cgiparams{'ENABLED_ORANGE'} = 'off';
$cgiparams{'EDIT_ADVANCED'} = 'off';
$cgiparams{'NAT'} = 'off';
$cgiparams{'COMPRESSION'} = 'off';
$cgiparams{'ONLY_PROPOSED'} = 'off';
$cgiparams{'ACTION'} = '';
$cgiparams{'CA_NAME'} = '';
$cgiparams{'DHCP_DOMAIN'} = '';
$cgiparams{'DHCP_DNS'} = '';
$cgiparams{'DHCP_WINS'} = '';
$cgiparams{'DCOMPLZO'} = 'off';
$cgiparams{'MSSFIX'} = '';

&Header::getcgihash(\%cgiparams, {'wantfile' => 1, 'filevar' => 'FH'});

# prepare openvpn config file
###
### Useful functions
###
sub haveOrangeNet
{
	if ($netsettings{'CONFIG_TYPE'} == 2) {return 1;}
	if ($netsettings{'CONFIG_TYPE'} == 4) {return 1;}
	return 0;
}

sub haveBlueNet
{
	if ($netsettings{'CONFIG_TYPE'} == 3) {return 1;}
	if ($netsettings{'CONFIG_TYPE'} == 4) {return 1;}
	return 0;
}

sub sizeformat{
    my $bytesize = shift;
    my $i = 0;

    while(abs($bytesize) >= 1024){
	$bytesize=$bytesize/1024;
	$i++;
	last if($i==6);
    }

    my @units = ("Bytes","KB","MB","GB","TB","PB","EB");
    my $newsize=(int($bytesize*100 +0.5))/100;
    return("$newsize $units[$i]");
}

sub valid_dns_host {
	my $hostname = $_[0];
	unless ($hostname) { return "No hostname"};
	my $res = new Net::DNS::Resolver;
	my $query = $res->search("$hostname");
	if ($query) {
		foreach my $rr ($query->answer) {
			## Potential bug - we are only looking at A records:
			return 0 if $rr->type eq "A";
		}
	} else {
		return $res->errorstring;
	}
}

sub cleanssldatabase
{
    if (open(FILE, ">${General::swroot}/ovpn/certs/serial")) {
	print FILE "01";
	close FILE;
    }
    if (open(FILE, ">${General::swroot}/ovpn/certs/index.txt")) {
	print FILE "";
	close FILE;
    }
    unlink ("${General::swroot}/ovpn/certs/index.txt.old");
    unlink ("${General::swroot}/ovpn/certs/serial.old");
    unlink ("${General::swroot}/ovpn/certs/01.pem");
}

sub newcleanssldatabase
{
    if (! -s "${General::swroot}/ovpn/certs/serial" )  {
        open(FILE, ">${General::swroot}(ovpn/certs/serial");
	print FILE "01";
	close FILE;
    }
    if (! -s ">${General::swroot}/ovpn/certs/index.txt") {
	system ("touch ${General::swroot}/ovpn/certs/index.txt");
    }
    unlink ("${General::swroot}/ovpn/certs/index.txt.old");
    unlink ("${General::swroot}/ovpn/certs/serial.old");
}

sub deletebackupcert
{
	if (open(FILE, "${General::swroot}/ovpn/certs/serial.old")) {
		my $hexvalue = <FILE>;
		chomp $hexvalue;
		close FILE;
		unlink ("${General::swroot}/ovpn/certs/$hexvalue.pem");
	}
}

sub checkportfw {
    my $KEY2 = $_[0]; # key2
    my $SRC_PORT = $_[1]; # src_port
    my $PROTOCOL = $_[2]; # protocol
    my $SRC_IP = $_[3]; # sourceip

    my $pfwfilename = "${General::swroot}/portfw/config";
    open(FILE, $pfwfilename) or die 'Unable to open config file.';
    my @pfwcurrent = <FILE>;
    close(FILE);
    my $pfwkey1 = 0; # used for finding last sequence number used 
    foreach my $pfwline (@pfwcurrent)
    {
	my @pfwtemp = split(/\,/,$pfwline);

	chomp ($pfwtemp[8]);
	if ($KEY2 eq "0"){ # if key2 is 0 then it is a portfw addition
		if ( $SRC_PORT eq $pfwtemp[3] &&
			$PROTOCOL eq $pfwtemp[2] &&
			$SRC_IP eq $pfwtemp[7])
		{
			 $errormessage = "$Lang::tr{'source port in use'} $SRC_PORT";
		}
		# Check if key2 = 0, if it is then it is a port forward entry and we want the sequence number
		if ( $pfwtemp[1] eq "0") {
			$pfwkey1=$pfwtemp[0];
		}
		# Darren Critchley - Duplicate or overlapping Port range check
		if ($pfwtemp[1] eq "0" && 
			$PROTOCOL eq $pfwtemp[2] &&
			$SRC_IP eq $pfwtemp[7] &&
			$errormessage eq '') 
		{
			&portchecks($SRC_PORT, $pfwtemp[5]);		
#			&portchecks($pfwtemp[3], $pfwtemp[5]);
#			&portchecks($pfwtemp[3], $SRC_IP);
		}
	}
    }
#    $errormessage="$KEY2 $SRC_PORT $PROTOCOL $SRC_IP";

    return;
}

sub checkportoverlap
{
	my $portrange1 = $_[0]; # New port range
	my $portrange2 = $_[1]; # existing port range
	my @tempr1 = split(/\:/,$portrange1);
	my @tempr2 = split(/\:/,$portrange2);

	unless (&checkportinc($tempr1[0], $portrange2)){ return 0;}
	unless (&checkportinc($tempr1[1], $portrange2)){ return 0;}
	
	unless (&checkportinc($tempr2[0], $portrange1)){ return 0;}
	unless (&checkportinc($tempr2[1], $portrange1)){ return 0;}

	return 1; # Everything checks out!
}

# Darren Critchley - we want to make sure that a port entry is not within an already existing range
sub checkportinc
{
	my $port1 = $_[0]; # Port
	my $portrange2 = $_[1]; # Port range
	my @tempr1 = split(/\:/,$portrange2);

	if ($port1 < $tempr1[0] || $port1 > $tempr1[1]) {
		return 1; 
	} else {
		return 0; 
	}
}
# Darren Critchley - Duplicate or overlapping Port range check
sub portchecks
{
	my $p1 = $_[0]; # New port range
	my $p2 = $_[1]; # existing port range
#	$_ = $_[0];
	our ($prtrange1, $prtrange2);
	$prtrange1 = 0;
#	if (m/:/ && $prtrange1 == 1) { # comparing two port ranges
#		unless (&checkportoverlap($p1,$p2)) {
#			$errormessage = "$Lang::tr{'source port overlaps'} $p1";
#		}
#	}
	if (m/:/ && $prtrange1 == 0 && $errormessage eq '') { # compare one port to a range
		unless (&checkportinc($p2,$p1)) {
			$errormessage = "$Lang::tr{'srcprt within existing'} $p1";
		}
	}
	$prtrange1 = 1;
	if (! m/:/ && $prtrange1 == 1 && $errormessage eq '') { # compare one port to a range
		unless (&checkportinc($p1,$p2)) {
			$errormessage = "$Lang::tr{'srcprt range overlaps'} $p2";
		}
	}
	return;
}

# Darren Critchley - certain ports are reserved for IPFire 
# TCP 67,68,81,222,445
# UDP 67,68
# Params passed in -> port, rangeyn, protocol
sub disallowreserved
{
	# port 67 and 68 same for tcp and udp, don't bother putting in an array
	my $msg = "";
	my @tcp_reserved = (81,222,445);
	my $prt = $_[0]; # the port or range
	my $ryn = $_[1]; # tells us whether or not it is a port range
	my $prot = $_[2]; # protocol
	my $srcdst = $_[3]; # source or destination
	if ($ryn) { # disect port range
		if ($srcdst eq "src") {
			$msg = "$Lang::tr{'rsvd src port overlap'}";
		} else {
			$msg = "$Lang::tr{'rsvd dst port overlap'}";
		}
		my @tmprng = split(/\:/,$prt);
		unless (67 < $tmprng[0] || 67 > $tmprng[1]) { $errormessage="$msg 67"; return; }
		unless (68 < $tmprng[0] || 68 > $tmprng[1]) { $errormessage="$msg 68"; return; }
		if ($prot eq "tcp") {
			foreach my $prange (@tcp_reserved) {
				unless ($prange < $tmprng[0] || $prange > $tmprng[1]) { $errormessage="$msg $prange"; return; }
			}
		}
	} else {
		if ($srcdst eq "src") {
			$msg = "$Lang::tr{'reserved src port'}";
		} else {
			$msg = "$Lang::tr{'reserved dst port'}";
		}
		if ($prt == 67) { $errormessage="$msg 67"; return; }
		if ($prt == 68) { $errormessage="$msg 68"; return; }
		if ($prot eq "tcp") {
			foreach my $prange (@tcp_reserved) {
				if ($prange == $prt) { $errormessage="$msg $prange"; return; }
			}
		}
	}
	return;
}

sub writeserverconf {
    my %sovpnsettings = ();    
    &General::readhash("${General::swroot}/ovpn/settings", \%sovpnsettings);

    open(CONF,    ">${General::swroot}/ovpn/server.conf") or die "Unable to open ${General::swroot}/ovpn/server.conf: $!";
    flock CONF, 2;
    print CONF "#OpenVPN Server conf\n";
    print CONF "\n";
    print CONF "daemon openvpnserver\n";
    print CONF "writepid /var/run/openvpn.pid\n";
    print CONF "#DAN prepare OpenVPN for listening on blue and orange\n";
    print CONF ";local $sovpnsettings{'VPN_IP'}\n";
    print CONF "dev $sovpnsettings{'DDEVICE'}\n";
    print CONF "$sovpnsettings{'DDEVICE'}-mtu $sovpnsettings{'DMTU'}\n";
    print CONF "proto $sovpnsettings{'DPROTOCOL'}\n";
    print CONF "port $sovpnsettings{'DDEST_PORT'}\n";
    print CONF "script-security 3 system\n";
    print CONF "ifconfig-pool-persist /var/ipfire/ovpn/ovpn-leases.db 3600\n";
    print CONF "tls-server\n";
    print CONF "ca /var/ipfire/ovpn/ca/cacert.pem\n";
    print CONF "cert /var/ipfire/ovpn/certs/servercert.pem\n";
    print CONF "key /var/ipfire/ovpn/certs/serverkey.pem\n";
    print CONF "dh /var/ipfire/ovpn/ca/dh1024.pem\n";
    my @tempovpnsubnet = split("\/",$sovpnsettings{'DOVPN_SUBNET'});
    print CONF "server $tempovpnsubnet[0] $tempovpnsubnet[1]\n";
    print CONF "push \"route $netsettings{'GREEN_NETADDRESS'} $netsettings{'GREEN_NETMASK'}\"\n";
    if ($sovpnsettings{CLIENT2CLIENT} eq 'on') {
	print CONF "client-to-client\n";
    }
    if ($sovpnsettings{MSSFIX} eq 'on') {
	print CONF "mssfix\n";
    }
    if ($sovpnsettings{FRAGMENT} ne '' && $sovpnsettings{'DPROTOCOL'} ne 'tcp') {
	print CONF "fragment $sovpnsettings{'FRAGMENT'}\n";
    }
    if ($sovpnsettings{KEEPALIVE_1} > 0 && $sovpnsettings{KEEPALIVE_2} > 0) {	
	print CONF "keepalive $sovpnsettings{'KEEPALIVE_1'} $sovpnsettings{'KEEPALIVE_2'}\n";
    }	
    print CONF "status-version 1\n";
    print CONF "status /var/log/ovpnserver.log 30\n";
    print CONF "cipher $sovpnsettings{DCIPHER}\n";
    if ($sovpnsettings{DCOMPLZO} eq 'on') {
        print CONF "comp-lzo\n";
    }
    if ($sovpnsettings{REDIRECT_GW_DEF1} eq 'on') {
        print CONF "push \"redirect-gateway def1\"\n";
    }
    if ($sovpnsettings{DHCP_DOMAIN} ne '') {
        print CONF "push \"dhcp-option DOMAIN $sovpnsettings{DHCP_DOMAIN}\"\n";
    }

    if ($sovpnsettings{DHCP_DNS} ne '') {
        print CONF "push \"dhcp-option DNS $sovpnsettings{DHCP_DNS}\"\n";
    }

    if ($sovpnsettings{DHCP_WINS} ne '') {
        print CONF "push \"dhcp-option WINS $sovpnsettings{DHCP_WINS}\"\n";
    }
    
    if ($sovpnsettings{DHCP_WINS} eq '') {
	print CONF "max-clients 100\n";
    }
    if ($sovpnsettings{DHCP_WINS} ne '') {
	print CONF "max-clients $sovpnsettings{MAX_CLIENTS}\n";
    }	
    print CONF "tls-verify /var/ipfire/ovpn/verify\n";
    print CONF "crl-verify /var/ipfire/ovpn/crls/cacrl.pem\n";
    print CONF "user nobody\n";
    print CONF "group nobody\n";
    print CONF "persist-key\n";
    print CONF "persist-tun\n";
	if ($sovpnsettings{LOG_VERB} ne '') {
		print CONF "verb $sovpnsettings{LOG_VERB}\n";
	} else {
		print CONF "verb 3\n";
	}	
    print CONF "\n";
    
    close(CONF);
}    
#
sub emptyserverlog{
    if (open(FILE, ">/var/log/ovpnserver.log")) {
	flock FILE, 2;
	print FILE "";
	close FILE;
    }

}

#hier die refresh page
if ( -e "${General::swroot}/ovpn/gencanow") {
    my $refresh = '';
    $refresh = "<meta http-equiv='refresh' content='15;' />";
    &Header::showhttpheaders();
    &Header::openpage($Lang::tr{'OVPN'}, 1, $refresh);
    &Header::openbigbox('100%', 'center');
    &Header::openbox('100%', 'left', "$Lang::tr{'generate root/host certificates'}:");
    print "<tr>\n<td align='center'><img src='/images/clock.gif' alt='' /></td>\n";
    print "<td colspan='2'><font color='red'>Please be patient this realy can take some time on older hardware...</font></td></tr>\n";
    &Header::closebox();
    &Header::closebigbox();
    &Header::closepage();
    exit (0);
}
##hier die refresh page


###
### OpenVPN Server Control
###
if ($cgiparams{'ACTION'} eq $Lang::tr{'start ovpn server'} ||
    $cgiparams{'ACTION'} eq $Lang::tr{'stop ovpn server'} ||
    $cgiparams{'ACTION'} eq $Lang::tr{'restart ovpn server'}) {
    #start openvpn server
    if ($cgiparams{'ACTION'} eq $Lang::tr{'start ovpn server'}){
    	&emptyserverlog();
	system('/usr/local/bin/openvpnctrl', '-s');
    }   
    #stop openvpn server
    if ($cgiparams{'ACTION'} eq $Lang::tr{'stop ovpn server'}){
    	system('/usr/local/bin/openvpnctrl', '-k');
	&emptyserverlog();	
    }   
#    #restart openvpn server
    if ($cgiparams{'ACTION'} eq $Lang::tr{'restart ovpn server'}){
#workarund, till SIGHUP also works when running as nobody    
    	system('/usr/local/bin/openvpnctrl', '-r');	
	&emptyserverlog();	
    }       
}

###
### Save Advanced options
###

if ($cgiparams{'ACTION'} eq $Lang::tr{'save-adv-options'}) {
    &General::readhash("${General::swroot}/ovpn/settings", \%vpnsettings);
    #DAN do we really need (to to check) this value? Besides if we listen on blue and orange too,
    #DAN this value has to leave.
#new settings for daemon
    $vpnsettings{'LOG_VERB'} = $cgiparams{'LOG_VERB'};
    $vpnsettings{'KEEPALIVE_1'} = $cgiparams{'KEEPALIVE_1'};
    $vpnsettings{'KEEPALIVE_2'} = $cgiparams{'KEEPALIVE_2'};
    $vpnsettings{'MAX_CLIENTS'} = $cgiparams{'MAX_CLIENTS'};
    $vpnsettings{'REDIRECT_GW_DEF1'} = $cgiparams{'REDIRECT_GW_DEF1'};
    $vpnsettings{'CLIENT2CLIENT'} = $cgiparams{'CLIENT2CLIENT'};
    $vpnsettings{'DHCP_DOMAIN'} = $cgiparams{'DHCP_DOMAIN'};
    $vpnsettings{'DHCP_DNS'} = $cgiparams{'DHCP_DNS'};
    $vpnsettings{'DHCP_WINS'} = $cgiparams{'DHCP_WINS'};
    
    if ($cgiparams{'FRAGMENT'} eq '') {
    	delete $vpnsettings{'FRAGMENT'};
    } else {
    	if ($cgiparams{'FRAGMENT'} !~ /^[0-9]+$/) { 
    	    $errormessage = "Incorrect value, please insert only numbers.";
        goto ADV_ERROR;
		} else {
			$vpnsettings{'FRAGMENT'} = $cgiparams{'FRAGMENT'};
    	}
    }
    if ($cgiparams{'MSSFIX'} ne 'on') {
    	delete $vpnsettings{'MSSFIX'};
    } else {
    	$vpnsettings{'MSSFIX'} = $cgiparams{'MSSFIX'};
    }
    if ($cgiparams{'DHCP_DOMAIN'} ne ''){
	unless (&General::validfqdn($cgiparams{'DHCP_DOMAIN'}) || &General::validip($cgiparams{'DHCP_DOMAIN'})) {
		$errormessage = $Lang::tr{'invalid input for dhcp domain'};
	goto ADV_ERROR;
    	}
    }
    if ($cgiparams{'DHCP_DNS'} ne ''){
	unless (&General::validfqdn($cgiparams{'DHCP_DNS'}) || &General::validip($cgiparams{'DHCP_DNS'})) {
		$errormessage = $Lang::tr{'invalid input for dhcp dns'};
	goto ADV_ERROR;
    	}
    }
    if ($cgiparams{'DHCP_WINS'} ne ''){
	unless (&General::validfqdn($cgiparams{'DHCP_WINS'}) || &General::validip($cgiparams{'DHCP_WINS'})) {
		$errormessage = $Lang::tr{'invalid input for dhcp wins'};
	goto ADV_ERROR;
    	}
    }
    if ((length($cgiparams{'MAX_CLIENTS'}) == 0) || (($cgiparams{'MAX_CLIENTS'}) < 1 ) || (($cgiparams{'MAX_CLIENTS'}) > 255 )) {
        $errormessage = $Lang::tr{'invalid input for max clients'};
        goto ADV_ERROR;
    }
    if ($cgiparams{'KEEPALIVE_1'} ne '') {
	if ($cgiparams{'KEEPALIVE_1'} !~ /^[0-9]+$/) { 
    	    $errormessage = $Lang::tr{'invalid input for keepalive 1'};
        goto ADV_ERROR;
	}
    }
    if ($cgiparams{'KEEPALIVE_2'} ne ''){
	if ($cgiparams{'KEEPALIVE_2'} !~ /^[0-9]+$/) { 
    	    $errormessage = $Lang::tr{'invalid input for keepalive 2'};
        goto ADV_ERROR;
	}
    }
    if ($cgiparams{'KEEPALIVE_2'} < ($cgiparams{'KEEPALIVE_1'} * 2)){
        $errormessage = $Lang::tr{'invalid input for keepalive 1:2'};
        goto ADV_ERROR;	
    }
    
    &General::writehash("${General::swroot}/ovpn/settings", \%vpnsettings);
    &writeserverconf();#hier ok
}




###
### Save main settings
###
if ($cgiparams{'ACTION'} eq $Lang::tr{'save'} && $cgiparams{'TYPE'} eq '' && $cgiparams{'KEY'} eq '') {
    &General::readhash("${General::swroot}/ovpn/settings", \%vpnsettings);
    #DAN do we really need (to to check) this value? Besides if we listen on blue and orange too,
    #DAN this value has to leave.
    if ($cgiparams{'ENABLED'} eq 'on'){
    	unless (&General::validfqdn($cgiparams{'VPN_IP'}) || &General::validip($cgiparams{'VPN_IP'})) {
		$errormessage = $Lang::tr{'invalid input for hostname'};
	goto SETTINGS_ERROR;
    	}
    }
    if ($cgiparams{'ENABLED'} eq 'on'){
	&disallowreserved($cgiparams{'DDEST_PORT'},0,$cgiparams{'DPROTOCOL'},"dest");
    }	
    if ($errormessage) { goto SETTINGS_ERROR; }
    
    
    if ($cgiparams{'ENABLED'} eq 'on'){
	&checkportfw(0,$cgiparams{'DDEST_PORT'},$cgiparams{'DPROTOCOL'},'0.0.0.0');
    }
    	
    if ($errormessage) { goto SETTINGS_ERROR; }
    
    if (! &General::validipandmask($cgiparams{'DOVPN_SUBNET'})) {
            $errormessage = $Lang::tr{'ovpn subnet is invalid'};
	goto SETTINGS_ERROR;
    }
    my @tmpovpnsubnet = split("\/",$cgiparams{'DOVPN_SUBNET'});
    
    if (&General::IpInSubnet ( $netsettings{'RED_ADDRESS'}, 
	$tmpovpnsubnet[0], $tmpovpnsubnet[1])) {
	$errormessage = "$Lang::tr{'ovpn subnet overlap'} IPFire RED Network $netsettings{'RED_ADDRESS'}";
	goto SETTINGS_ERROR;
    }
    
    if (&General::IpInSubnet ( $netsettings{'GREEN_ADDRESS'}, 
	$tmpovpnsubnet[0], $tmpovpnsubnet[1])) {
        $errormessage = "$Lang::tr{'ovpn subnet overlap'} IPFire Green Network $netsettings{'GREEN_ADDRESS'}";
        goto SETTINGS_ERROR;
    }

    if (&General::IpInSubnet ( $netsettings{'BLUE_ADDRESS'}, 
	$tmpovpnsubnet[0], $tmpovpnsubnet[1])) {
	$errormessage = "$Lang::tr{'ovpn subnet overlap'} IPFire Blue Network $netsettings{'BLUE_ADDRESS'}";
	goto SETTINGS_ERROR;
    }
    
    if (&General::IpInSubnet ( $netsettings{'ORANGE_ADDRESS'}, 
	$tmpovpnsubnet[0], $tmpovpnsubnet[1])) {
	$errormessage = "$Lang::tr{'ovpn subnet overlap'} IPFire Orange Network $netsettings{'ORANGE_ADDRESS'}";
	goto SETTINGS_ERROR;
    }
    open(ALIASES, "${General::swroot}/ethernet/aliases") or die 'Unable to open aliases file.';
    while (<ALIASES>)
    {
	chomp($_);
	my @tempalias = split(/\,/,$_);
	if ($tempalias[1] eq 'on') {
	    if (&General::IpInSubnet ($tempalias[0] , 
		$tmpovpnsubnet[0], $tmpovpnsubnet[1])) {
		$errormessage = "$Lang::tr{'ovpn subnet overlap'} IPFire alias entry $tempalias[0]";
	    }		
	}
    }
    close(ALIASES);
    if ($errormessage ne ''){
	goto SETTINGS_ERROR;
    }
    if ($cgiparams{'ENABLED'} !~ /^(on|off)$/) {
        $errormessage = $Lang::tr{'invalid input'};
        goto SETTINGS_ERROR;
    }
    if ((length($cgiparams{'DMTU'})==0) || (($cgiparams{'DMTU'}) < 1000 )) {
        $errormessage = $Lang::tr{'invalid mtu input'};
        goto SETTINGS_ERROR;
    }
    
    unless (&General::validport($cgiparams{'DDEST_PORT'})) {
	$errormessage = $Lang::tr{'invalid port'};
	goto SETTINGS_ERROR;
    }
    $vpnsettings{'ENABLED_BLUE'} = $cgiparams{'ENABLED_BLUE'};
    $vpnsettings{'ENABLED_ORANGE'} =$cgiparams{'ENABLED_ORANGE'};
    $vpnsettings{'ENABLED'} = $cgiparams{'ENABLED'};
    $vpnsettings{'VPN_IP'} = $cgiparams{'VPN_IP'};
#new settings for daemon
    $vpnsettings{'DOVPN_SUBNET'} = $cgiparams{'DOVPN_SUBNET'};
    $vpnsettings{'DDEVICE'} = $cgiparams{'DDEVICE'};
    $vpnsettings{'DPROTOCOL'} = $cgiparams{'DPROTOCOL'};
    $vpnsettings{'DDEST_PORT'} = $cgiparams{'DDEST_PORT'};
    $vpnsettings{'DMTU'} = $cgiparams{'DMTU'};
    $vpnsettings{'DCOMPLZO'} = $cgiparams{'DCOMPLZO'};
    $vpnsettings{'DCIPHER'} = $cgiparams{'DCIPHER'};
#wrtie enable

  if ( $vpnsettings{'ENABLED_BLUE'} eq 'on' ) {system("touch ${General::swroot}/ovpn/enable_blue 2>/dev/null");}else{system("unlink ${General::swroot}/ovpn/enable_blue 2>/dev/null");}
  if ( $vpnsettings{'ENABLED_ORANGE'} eq 'on' ) {system("touch ${General::swroot}/ovpn/enable_orange 2>/dev/null");}else{system("unlink ${General::swroot}/ovpn/enable_orange 2>/dev/null");}
  if ( $vpnsettings{'ENABLED'} eq 'on' ) {system("touch ${General::swroot}/ovpn/enable 2>/dev/null");}else{system("unlink ${General::swroot}/ovpn/enable 2>/dev/null");}
#new settings for daemon    
    &General::writehash("${General::swroot}/ovpn/settings", \%vpnsettings);
    &writeserverconf();#hier ok
SETTINGS_ERROR:
###
### Reset all step 2
###
}elsif ($cgiparams{'ACTION'} eq $Lang::tr{'reset'} && $cgiparams{'AREUSURE'} eq 'yes') {
    my $file = '';
    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

    foreach my $key (keys %confighash) {
	if ($confighash{$key}[4] eq 'cert') {
	    delete $confighash{$cgiparams{'$key'}};
	}
    }
    while ($file = glob("${General::swroot}/ovpn/ca/*")) {
	unlink $file
    }
    while ($file = glob("${General::swroot}/ovpn/certs/*")) {
	unlink $file
    }
    while ($file = glob("${General::swroot}/ovpn/crls/*")) {
	unlink $file
    }
    &cleanssldatabase();
    if (open(FILE, ">${General::swroot}/ovpn/caconfig")) {
        print FILE "";
        close FILE;
    }
    &General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
    #&writeserverconf();
###
### Reset all step 1
###
}elsif ($cgiparams{'ACTION'} eq $Lang::tr{'reset'}) {
    &Header::showhttpheaders();
    &Header::openpage($Lang::tr{'vpn configuration main'}, 1, '');
    &Header::openbigbox('100%', 'LEFT', '', '');
    &Header::openbox('100%', 'LEFT', $Lang::tr{'are you sure'});
    print <<END
	<table><form method='post'><input type='hidden' name='AREUSURE' value='yes' />
	    <tr><td align='center'>		
		<b><font color='${Header::colourred}'>$Lang::tr{'capswarning'}</font></b>: 
		$Lang::tr{'resetting the vpn configuration will remove the root ca, the host certificate and all certificate based connections'}
	    <tr><td align='center'><input type='submit' name='ACTION' value='$Lang::tr{'reset'}' />
		<input type='submit' name='ACTION' value='$Lang::tr{'cancel'}' /></td></tr>
	</form></table>
END
    ;
    &Header::closebox();
    &Header::closebigbox();
    &Header::closepage();
    exit (0);

###
### Upload CA Certificate
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'upload ca certificate'}) {
    &General::readhasharray("${General::swroot}/ovpn/caconfig", \%cahash);

    if ($cgiparams{'CA_NAME'} !~ /^[a-zA-Z0-9]+$/) {
	$errormessage = $Lang::tr{'name must only contain characters'};
	goto UPLOADCA_ERROR;
    }

    if (length($cgiparams{'CA_NAME'}) >60) {
	$errormessage = $Lang::tr{'name too long'};
	goto VPNCONF_ERROR;
    }

    if ($cgiparams{'CA_NAME'} eq 'ca') {
	$errormessage = $Lang::tr{'name is invalid'};
	goto UPLOAD_CA_ERROR;
    }

    # Check if there is no other entry with this name
    foreach my $key (keys %cahash) {
	if ($cahash{$key}[0] eq $cgiparams{'CA_NAME'}) {
	    $errormessage = $Lang::tr{'a ca certificate with this name already exists'};
	    goto UPLOADCA_ERROR;
	}
    }

    if (ref ($cgiparams{'FH'}) ne 'Fh') {
	$errormessage = $Lang::tr{'there was no file upload'};
	goto UPLOADCA_ERROR;
    }
    # Move uploaded ca to a temporary file
    (my $fh, my $filename) = tempfile( );
    if (copy ($cgiparams{'FH'}, $fh) != 1) {
	$errormessage = $!;
	goto UPLOADCA_ERROR;
    }
    my $temp = `/usr/bin/openssl x509 -text -in $filename`;
    if ($temp !~ /CA:TRUE/i) {
	$errormessage = $Lang::tr{'not a valid ca certificate'};
	unlink ($filename);
	goto UPLOADCA_ERROR;
    } else {
	move($filename, "${General::swroot}/ovpn/ca/$cgiparams{'CA_NAME'}cert.pem");
	if ($? ne 0) {
	    $errormessage = "$Lang::tr{'certificate file move failed'}: $!";
	    unlink ($filename);
	    goto UPLOADCA_ERROR;
	}
    }

    my $casubject = `/usr/bin/openssl x509 -text -in ${General::swroot}/ovpn/ca/$cgiparams{'CA_NAME'}cert.pem`;
    $casubject    =~ /Subject: (.*)[\n]/;
    $casubject    = $1;
    $casubject    =~ s+/Email+, E+;
    $casubject    =~ s/ ST=/ S=/;
    $casubject    = &Header::cleanhtml($casubject);

    my $key = &General::findhasharraykey (\%cahash);
    $cahash{$key}[0] = $cgiparams{'CA_NAME'};
    $cahash{$key}[1] = $casubject;
    &General::writehasharray("${General::swroot}/ovpn/caconfig", \%cahash);
#    system('/usr/local/bin/ipsecctrl', 'R');

    UPLOADCA_ERROR:

###
### Display ca certificate
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'show ca certificate'}) {
    &General::readhasharray("${General::swroot}/ovpn/caconfig", \%cahash);

    if ( -f "${General::swroot}/ovpn/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem") {
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'vpn configuration main'}, 1, '');
	&Header::openbigbox('100%', 'LEFT', '', $errormessage);
	&Header::openbox('100%', 'LEFT', "$Lang::tr{'ca certificate'}:");
	my $output = `/usr/bin/openssl x509 -text -in ${General::swroot}/ovpn/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem`;
	$output = &Header::cleanhtml($output,"y");
	print "<pre>$output</pre>\n";
	&Header::closebox();
	print "<div align='center'><a href='/cgi-bin/ovpnmain.cgi'>$Lang::tr{'back'}</a></div>";
	&Header::closebigbox();
	&Header::closepage();
	exit(0);
    } else {
	$errormessage = $Lang::tr{'invalid key'};
    }

###
### Download ca certificate
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'download ca certificate'}) {
    &General::readhasharray("${General::swroot}/ovpn/caconfig", \%cahash);

    if ( -f "${General::swroot}/ovpn/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem" ) {
	print "Content-Type: application/octet-stream\r\n";
	print "Content-Disposition: filename=$cahash{$cgiparams{'KEY'}}[0]cert.pem\r\n\r\n";
	print `/usr/bin/openssl x509 -in ${General::swroot}/ovpn/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem`;
	exit(0);
    } else {
	$errormessage = $Lang::tr{'invalid key'};
    }

###
### Remove ca certificate (step 2)
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'remove ca certificate'} && $cgiparams{'AREUSURE'} eq 'yes') {
    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
    &General::readhasharray("${General::swroot}/ovpn/caconfig", \%cahash);

    if ( -f "${General::swroot}/ovpn/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem" ) {
	foreach my $key (keys %confighash) {
	    my $test = `/usr/bin/openssl verify -CAfile ${General::swroot}/ovpn/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem ${General::swroot}/ovpn/certs/$confighash{$key}[1]cert.pem`;
	    if ($test =~ /: OK/) {
		# Delete connection
#		if ($vpnsettings{'ENABLED'} eq 'on' ||
#		    $vpnsettings{'ENABLED_BLUE'} eq 'on') {
#		    system('/usr/local/bin/ipsecctrl', 'D', $key);
#		}
		unlink ("${General::swroot}/ovpn//certs/$confighash{$key}[1]cert.pem");
		unlink ("${General::swroot}/ovpn/certs/$confighash{$key}[1].p12");
		delete $confighash{$key};
		&General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
#		&writeipsecfiles();
	    }
	}
	unlink ("${General::swroot}/ovpn/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem");
	delete $cahash{$cgiparams{'KEY'}};
	&General::writehasharray("${General::swroot}/ovpn/caconfig", \%cahash);
#	system('/usr/local/bin/ipsecctrl', 'R');
    } else {
	$errormessage = $Lang::tr{'invalid key'};
    }
###
### Remove ca certificate (step 1)
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'remove ca certificate'}) {
    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
    &General::readhasharray("${General::swroot}/ovpn/caconfig", \%cahash);

    my $assignedcerts = 0;
    if ( -f "${General::swroot}/ovpn/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem" ) {
	foreach my $key (keys %confighash) {
	    my $test = `/usr/bin/openssl verify -CAfile ${General::swroot}/ovpn/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem ${General::swroot}/ovpn/certs/$confighash{$key}[1]cert.pem`;
	    if ($test =~ /: OK/) {
		$assignedcerts++;
	    }
	}
	if ($assignedcerts) {
	    &Header::showhttpheaders();
	    &Header::openpage($Lang::tr{'vpn configuration main'}, 1, '');
	    &Header::openbigbox('100%', 'LEFT', '', $errormessage);
	    &Header::openbox('100%', 'LEFT', $Lang::tr{'are you sure'});
	    print <<END
		<table><form method='post'><input type='hidden' name='AREUSURE' value='yes' />
		       <input type='hidden' name='KEY' value='$cgiparams{'KEY'}' />
		    <tr><td align='center'>
			<b><font color='${Header::colourred}'>$Lang::tr{'capswarning'}</font></b>: $assignedcerts
			$Lang::tr{'connections are associated with this ca.  deleting the ca will delete these connections as well.'}
		    <tr><td align='center'><input type='submit' name='ACTION' value='$Lang::tr{'remove ca certificate'}' />
			<input type='submit' name='ACTION' value='$Lang::tr{'cancel'}' /></td></tr>
		</form></table>
END
	    ;
	    &Header::closebox();
	    &Header::closebigbox();
	    &Header::closepage();
	    exit (0);
	} else {
	    unlink ("${General::swroot}/ovpn/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem");
	    delete $cahash{$cgiparams{'KEY'}};
	    &General::writehasharray("${General::swroot}/ovpn/caconfig", \%cahash);
#	    system('/usr/local/bin/ipsecctrl', 'R');
	}
    } else {
	$errormessage = $Lang::tr{'invalid key'};
    }

###
### Display root certificate
###
}elsif ($cgiparams{'ACTION'} eq $Lang::tr{'show root certificate'} ||
    $cgiparams{'ACTION'} eq $Lang::tr{'show host certificate'}) {
    my $output;
    &Header::showhttpheaders();
    &Header::openpage($Lang::tr{'vpn configuration main'}, 1, '');
    &Header::openbigbox('100%', 'LEFT', '', '');
    if ($cgiparams{'ACTION'} eq $Lang::tr{'show root certificate'}) {
	&Header::openbox('100%', 'LEFT', "$Lang::tr{'root certificate'}:");
	$output = `/usr/bin/openssl x509 -text -in ${General::swroot}/ovpn/ca/cacert.pem`;
    } else {
	&Header::openbox('100%', 'LEFT', "$Lang::tr{'host certificate'}:");
	$output = `/usr/bin/openssl x509 -text -in ${General::swroot}/ovpn/certs/servercert.pem`;
    }
    $output = &Header::cleanhtml($output,"y");
    print "<pre>$output</pre>\n";
    &Header::closebox();
    print "<div align='center'><a href='/cgi-bin/ovpnmain.cgi'>$Lang::tr{'back'}</a></div>";
    &Header::closebigbox();
    &Header::closepage();
    exit(0);

###
### Download root certificate
###
}elsif ($cgiparams{'ACTION'} eq $Lang::tr{'download root certificate'}) {
    if ( -f "${General::swroot}/ovpn/ca/cacert.pem" ) {
	print "Content-Type: application/octet-stream\r\n";
	print "Content-Disposition: filename=cacert.pem\r\n\r\n";
	print `/usr/bin/openssl x509 -in ${General::swroot}/ovpn/ca/cacert.pem`;
	exit(0);
    }
    
###
### Download host certificate
###
}elsif ($cgiparams{'ACTION'} eq $Lang::tr{'download host certificate'}) {
    if ( -f "${General::swroot}/ovpn/certs/servercert.pem" ) {
	print "Content-Type: application/octet-stream\r\n";
	print "Content-Disposition: filename=servercert.pem\r\n\r\n";
	print `/usr/bin/openssl x509 -in ${General::swroot}/ovpn/certs/servercert.pem`;
	exit(0);
    }
###
### Form for generating a root certificate
###
}elsif ($cgiparams{'ACTION'} eq $Lang::tr{'generate root/host certificates'} ||
	 $cgiparams{'ACTION'} eq $Lang::tr{'upload p12 file'}) {

    &General::readhash("${General::swroot}/ovpn/settings", \%vpnsettings);
    if (-f "${General::swroot}/ovpn/ca/cacert.pem") {
	$errormessage = $Lang::tr{'valid root certificate already exists'};
	$cgiparams{'ACTION'} = '';
	goto ROOTCERT_ERROR;
    }

    if (($cgiparams{'ROOTCERT_HOSTNAME'} eq '') && -e "${General::swroot}/red/active") {
	if (open(IPADDR, "${General::swroot}/red/local-ipaddress")) {
	    my $ipaddr = <IPADDR>;
	    close IPADDR;
	    chomp ($ipaddr);
	    $cgiparams{'ROOTCERT_HOSTNAME'} = (gethostbyaddr(pack("C4", split(/\./, $ipaddr)), 2))[0];
	    if ($cgiparams{'ROOTCERT_HOSTNAME'} eq '') {
		$cgiparams{'ROOTCERT_HOSTNAME'} = $ipaddr;
	    }
	}
    } elsif ($cgiparams{'ACTION'} eq $Lang::tr{'upload p12 file'}) {

	if (ref ($cgiparams{'FH'}) ne 'Fh') {
	    $errormessage = $Lang::tr{'there was no file upload'};
	    goto ROOTCERT_ERROR;
	}

	# Move uploaded certificate request to a temporary file
	(my $fh, my $filename) = tempfile( );
	if (copy ($cgiparams{'FH'}, $fh) != 1) {
	    $errormessage = $!;
	    goto ROOTCERT_ERROR;
	}

	# Create a temporary dirctory
	my $tempdir = tempdir( CLEANUP => 1 );

	# Extract the CA certificate from the file
	my $pid = open(OPENSSL, "|-");
	$SIG{ALRM} = sub { $errormessage = $Lang::tr{'broken pipe'}; goto ROOTCERT_ERROR;};
	if ($pid) {	# parent
	    if ($cgiparams{'P12_PASS'} ne '') {
		print OPENSSL "$cgiparams{'P12_PASS'}\n";
	    }
	    close (OPENSSL);
	    if ($?) {
		$errormessage = "$Lang::tr{'openssl produced an error'}: $?";
		unlink ($filename);
		goto ROOTCERT_ERROR;
	    }
	} else {	# child
	    unless (exec ('/usr/bin/openssl', 'pkcs12', '-cacerts', '-nokeys',
		    '-in', $filename,
		    '-out', "$tempdir/cacert.pem")) {
		$errormessage = "$Lang::tr{'cant start openssl'}: $!";
		unlink ($filename);
		goto ROOTCERT_ERROR;
	    }
	}

	# Extract the Host certificate from the file
	$pid = open(OPENSSL, "|-");
	$SIG{ALRM} = sub { $errormessage = $Lang::tr{'broken pipe'}; goto ROOTCERT_ERROR;};
	if ($pid) {	# parent
	    if ($cgiparams{'P12_PASS'} ne '') {
		print OPENSSL "$cgiparams{'P12_PASS'}\n";
	    }
	    close (OPENSSL);
	    if ($?) {
		$errormessage = "$Lang::tr{'openssl produced an error'}: $?";
		unlink ($filename);
		goto ROOTCERT_ERROR;
	    }
	} else {	# child
	    unless (exec ('/usr/bin/openssl', 'pkcs12', '-clcerts', '-nokeys',
		    '-in', $filename,
		    '-out', "$tempdir/hostcert.pem")) {
		$errormessage = "$Lang::tr{'cant start openssl'}: $!";
		unlink ($filename);
		goto ROOTCERT_ERROR;
	    }
	}

	# Extract the Host key from the file
	$pid = open(OPENSSL, "|-");
	$SIG{ALRM} = sub { $errormessage = $Lang::tr{'broken pipe'}; goto ROOTCERT_ERROR;};
	if ($pid) {	# parent
	    if ($cgiparams{'P12_PASS'} ne '') {
		print OPENSSL "$cgiparams{'P12_PASS'}\n";
	    }
	    close (OPENSSL);
	    if ($?) {
		$errormessage = "$Lang::tr{'openssl produced an error'}: $?";
		unlink ($filename);
		goto ROOTCERT_ERROR;
	    }
	} else {	# child
	    unless (exec ('/usr/bin/openssl', 'pkcs12', '-nocerts',
		    '-nodes',
		    '-in', $filename,
		    '-out', "$tempdir/serverkey.pem")) {
		$errormessage = "$Lang::tr{'cant start openssl'}: $!";
		unlink ($filename);
		goto ROOTCERT_ERROR;
	    }
	}

	move("$tempdir/cacert.pem", "${General::swroot}/ovpn/ca/cacert.pem");
	if ($? ne 0) {
	    $errormessage = "$Lang::tr{'certificate file move failed'}: $!";
	    unlink ($filename);
	    unlink ("${General::swroot}/ovpn/ca/cacert.pem");
	    unlink ("${General::swroot}/ovpn/certs/servercert.pem");
	    unlink ("${General::swroot}/ovpn/certs/serverkey.pem");
	    goto ROOTCERT_ERROR;
        }

	move("$tempdir/hostcert.pem", "${General::swroot}/ovpn/certs/servercert.pem");
	if ($? ne 0) {
	    $errormessage = "$Lang::tr{'certificate file move failed'}: $!";
	    unlink ($filename);
	    unlink ("${General::swroot}/ovpn/ca/cacert.pem");
	    unlink ("${General::swroot}/ovpn/certs/servercert.pem");
	    unlink ("${General::swroot}/ovpn/certs/serverkey.pem");
	    goto ROOTCERT_ERROR;
        }

	move("$tempdir/serverkey.pem", "${General::swroot}/ovpn/certs/serverkey.pem");
	if ($? ne 0) {
	    $errormessage = "$Lang::tr{'certificate file move failed'}: $!";
	    unlink ($filename);
	    unlink ("${General::swroot}/ovpn/ca/cacert.pem");
	    unlink ("${General::swroot}/ovpn/certs/servercert.pem");
	    unlink ("${General::swroot}/ovpn/certs/serverkey.pem");
	    goto ROOTCERT_ERROR;
        }

	goto ROOTCERT_SUCCESS;

    } elsif ($cgiparams{'ROOTCERT_COUNTRY'} ne '') {

	# Validate input since the form was submitted
	if ($cgiparams{'ROOTCERT_ORGANIZATION'} eq ''){
	    $errormessage = $Lang::tr{'organization cant be empty'};
	    goto ROOTCERT_ERROR;
	}
	if (length($cgiparams{'ROOTCERT_ORGANIZATION'}) >60) {
	    $errormessage = $Lang::tr{'organization too long'};
	    goto ROOTCERT_ERROR;
	}
	if ($cgiparams{'ROOTCERT_ORGANIZATION'} !~ /^[a-zA-Z0-9 ,\.\-_]*$/) {
	    $errormessage = $Lang::tr{'invalid input for organization'};
	    goto ROOTCERT_ERROR;
	}
	if ($cgiparams{'ROOTCERT_HOSTNAME'} eq ''){
	    $errormessage = $Lang::tr{'hostname cant be empty'};
	    goto ROOTCERT_ERROR;
	}
	unless (&General::validfqdn($cgiparams{'ROOTCERT_HOSTNAME'}) || &General::validip($cgiparams{'ROOTCERT_HOSTNAME'})) {
	    $errormessage = $Lang::tr{'invalid input for hostname'};
	    goto ROOTCERT_ERROR;
	}
	if ($cgiparams{'ROOTCERT_EMAIL'} ne '' && (! &General::validemail($cgiparams{'ROOTCERT_EMAIL'}))) {
	    $errormessage = $Lang::tr{'invalid input for e-mail address'};
	    goto ROOTCERT_ERROR;
	}
	if (length($cgiparams{'ROOTCERT_EMAIL'}) > 40) {
	    $errormessage = $Lang::tr{'e-mail address too long'};
	    goto ROOTCERT_ERROR;
	}
	if ($cgiparams{'ROOTCERT_OU'} ne '' && $cgiparams{'ROOTCERT_OU'} !~ /^[a-zA-Z0-9 ,\.\-_]*$/) {
	    $errormessage = $Lang::tr{'invalid input for department'};
	    goto ROOTCERT_ERROR;
	}
	if ($cgiparams{'ROOTCERT_CITY'} ne '' && $cgiparams{'ROOTCERT_CITY'} !~ /^[a-zA-Z0-9 ,\.\-_]*$/) {
	    $errormessage = $Lang::tr{'invalid input for city'};
	    goto ROOTCERT_ERROR;
	}
	if ($cgiparams{'ROOTCERT_STATE'} ne '' && $cgiparams{'ROOTCERT_STATE'} !~ /^[a-zA-Z0-9 ,\.\-_]*$/) {
	    $errormessage = $Lang::tr{'invalid input for state or province'};
	    goto ROOTCERT_ERROR;
	}
	if ($cgiparams{'ROOTCERT_COUNTRY'} !~ /^[A-Z]*$/) {
	    $errormessage = $Lang::tr{'invalid input for country'};
	    goto ROOTCERT_ERROR;
	}

	# Copy the cgisettings to vpnsettings and save the configfile
	$vpnsettings{'ROOTCERT_ORGANIZATION'}	= $cgiparams{'ROOTCERT_ORGANIZATION'};
	$vpnsettings{'ROOTCERT_HOSTNAME'}	= $cgiparams{'ROOTCERT_HOSTNAME'};
	$vpnsettings{'ROOTCERT_EMAIL'}	 	= $cgiparams{'ROOTCERT_EMAIL'};
	$vpnsettings{'ROOTCERT_OU'}		= $cgiparams{'ROOTCERT_OU'};
	$vpnsettings{'ROOTCERT_CITY'}		= $cgiparams{'ROOTCERT_CITY'};
	$vpnsettings{'ROOTCERT_STATE'}		= $cgiparams{'ROOTCERT_STATE'};
	$vpnsettings{'ROOTCERT_COUNTRY'}	= $cgiparams{'ROOTCERT_COUNTRY'};
	&General::writehash("${General::swroot}/ovpn/settings", \%vpnsettings);

	# Replace empty strings with a .
	(my $ou = $cgiparams{'ROOTCERT_OU'}) =~ s/^\s*$/\./;
	(my $city = $cgiparams{'ROOTCERT_CITY'}) =~ s/^\s*$/\./;
	(my $state = $cgiparams{'ROOTCERT_STATE'}) =~ s/^\s*$/\./;

	# refresh
	#system ('/bin/touch', "${General::swroot}/ovpn/gencanow");
	
	# Create the CA certificate
	my $pid = open(OPENSSL, "|-");
	$SIG{ALRM} = sub { $errormessage = $Lang::tr{'broken pipe'}; goto ROOTCERT_ERROR;};
	if ($pid) {	# parent
	    print OPENSSL "$cgiparams{'ROOTCERT_COUNTRY'}\n";
	    print OPENSSL "$state\n";
	    print OPENSSL "$city\n";
	    print OPENSSL "$cgiparams{'ROOTCERT_ORGANIZATION'}\n";
	    print OPENSSL "$ou\n";
	    print OPENSSL "$cgiparams{'ROOTCERT_ORGANIZATION'} CA\n";
	    print OPENSSL "$cgiparams{'ROOTCERT_EMAIL'}\n";
	    close (OPENSSL);
	    if ($?) {
		$errormessage = "$Lang::tr{'openssl produced an error'}: $?";
		unlink ("${General::swroot}/ovpn/ca/cakey.pem");
		unlink ("${General::swroot}/ovpn/ca/cacert.pem");
		goto ROOTCERT_ERROR;
	    }
	} else {	# child
	    unless (exec ('/usr/bin/openssl', 'req', '-x509', '-nodes', '-rand', '/proc/interrupts:/proc/net/rt_cache',
			'-days', '999999', '-newkey', 'rsa:2048',
			'-keyout', "${General::swroot}/ovpn/ca/cakey.pem",
			'-out', "${General::swroot}/ovpn/ca/cacert.pem",
			'-config',"${General::swroot}/ovpn/openssl/ovpn.cnf")) {
		$errormessage = "$Lang::tr{'cant start openssl'}: $!";
		goto ROOTCERT_ERROR;
	    }
	}

	# Create the Host certificate request
	$pid = open(OPENSSL, "|-");
	$SIG{ALRM} = sub { $errormessage = $Lang::tr{'broken pipe'}; goto ROOTCERT_ERROR;};
	if ($pid) {	# parent
	    print OPENSSL "$cgiparams{'ROOTCERT_COUNTRY'}\n";
	    print OPENSSL "$state\n";
	    print OPENSSL "$city\n";
	    print OPENSSL "$cgiparams{'ROOTCERT_ORGANIZATION'}\n";
	    print OPENSSL "$ou\n";
	    print OPENSSL "$cgiparams{'ROOTCERT_HOSTNAME'}\n";
	    print OPENSSL "$cgiparams{'ROOTCERT_EMAIL'}\n";
	    print OPENSSL ".\n";
	    print OPENSSL ".\n";
	    close (OPENSSL);
	    if ($?) {
		$errormessage = "$Lang::tr{'openssl produced an error'}: $?";
		unlink ("${General::swroot}/ovpn/certs/serverkey.pem");
		unlink ("${General::swroot}/ovpn/certs/serverreq.pem");
		goto ROOTCERT_ERROR;
	    }
	} else {	# child
	    unless (exec ('/usr/bin/openssl', 'req', '-nodes', '-rand', '/proc/interrupts:/proc/net/rt_cache',
			'-newkey', 'rsa:1024',
			'-keyout', "${General::swroot}/ovpn/certs/serverkey.pem",
			'-out', "${General::swroot}/ovpn/certs/serverreq.pem",
			'-extensions', 'server',
			'-config', "${General::swroot}/ovpn/openssl/ovpn.cnf" )) {
		$errormessage = "$Lang::tr{'cant start openssl'}: $!";
		unlink ("${General::swroot}/ovpn/certs/serverkey.pem");
		unlink ("${General::swroot}/ovpn/certs/serverreq.pem");
		unlink ("${General::swroot}/ovpn/ca/cakey.pem");
		unlink ("${General::swroot}/ovpn/ca/cacert.pem");
		goto ROOTCERT_ERROR;
	    }
	}
	
	# Sign the host certificate request
	system('/usr/bin/openssl', 'ca', '-days', '999999',
		'-batch', '-notext',
		'-in',  "${General::swroot}/ovpn/certs/serverreq.pem",
		'-out', "${General::swroot}/ovpn/certs/servercert.pem",
		'-extensions', 'server',
		'-config', "${General::swroot}/ovpn/openssl/ovpn.cnf");
	if ($?) {
	    $errormessage = "$Lang::tr{'openssl produced an error'}: $?";
	    unlink ("${General::swroot}/ovpn/ca/cakey.pem");
	    unlink ("${General::swroot}/ovpn/ca/cacert.pem");
	    unlink ("${General::swroot}/ovpn/serverkey.pem");
	    unlink ("${General::swroot}/ovpn/certs/serverreq.pem");
	    unlink ("${General::swroot}/ovpn/certs/servercert.pem");
	    &newcleanssldatabase();
	    goto ROOTCERT_ERROR;
	} else {
	    unlink ("${General::swroot}/ovpn/certs/serverreq.pem");
	    &deletebackupcert();
	}

	# Create an empty CRL
	system('/usr/bin/openssl', 'ca', '-gencrl',
		'-out', "${General::swroot}/ovpn/crls/cacrl.pem",
		'-config', "${General::swroot}/ovpn/openssl/ovpn.cnf" );
	if ($?) {
	    $errormessage = "$Lang::tr{'openssl produced an error'}: $?";
	    unlink ("${General::swroot}/ovpn/certs/serverkey.pem");
	    unlink ("${General::swroot}/ovpn/certs/servercert.pem");
	    unlink ("${General::swroot}/ovpn/ca/cacert.pem");
	    unlink ("${General::swroot}/ovpn/crls/cacrl.pem");	    
	    &cleanssldatabase();
	    goto ROOTCERT_ERROR;
#	} else {
#	    &cleanssldatabase();
	}
	# Create Diffie Hellmann Parameter
	system('/usr/bin/openssl', 'dhparam', '-rand', '/proc/interrupts:/proc/net/rt_cache',
	       '-out', "${General::swroot}/ovpn/ca/dh1024.pem",
	       '1024' );
	if ($?) {
	    $errormessage = "$Lang::tr{'openssl produced an error'}: $?";
	    unlink ("${General::swroot}/ovpn/certs/serverkey.pem");
	    unlink ("${General::swroot}/ovpn/certs/servercert.pem");
	    unlink ("${General::swroot}/ovpn/ca/cacert.pem");
	    unlink ("${General::swroot}/ovpn/crls/cacrl.pem");
	    unlink ("${General::swroot}/ovpn/ca/dh1024.pem");
	    &cleanssldatabase();
	    goto ROOTCERT_ERROR;
#	} else {
#	    &cleanssldatabase();
	}       
	goto ROOTCERT_SUCCESS;
    }
    ROOTCERT_ERROR:
    if ($cgiparams{'ACTION'} ne '') {
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'vpn configuration main'}, 1, '');
	&Header::openbigbox('100%', 'LEFT', '', '');
	if ($errormessage) {
	    &Header::openbox('100%', 'LEFT', $Lang::tr{'error messages'});
	    print "<class name='base'>$errormessage";
	    print "&nbsp;</class>";
	    &Header::closebox();
	}
	&Header::openbox('100%', 'LEFT', "$Lang::tr{'generate root/host certificates'}:");
	print <<END
	<form method='post' enctype='multipart/form-data'>
	<table width='100%' border='0' cellspacing='1' cellpadding='0'>
	<tr><td width='30%' class='base'>$Lang::tr{'organization name'}:</td>
	    <td width='35%' class='base' nowrap='nowrap'><input type='text' name='ROOTCERT_ORGANIZATION' value='$cgiparams{'ROOTCERT_ORGANIZATION'}' size='32' /></td>
	    <td width='35%' colspan='2'>&nbsp;</td></tr>
	<tr><td class='base'>$Lang::tr{'ipfires hostname'}:</td>
	    <td class='base' nowrap='nowrap'><input type='text' name='ROOTCERT_HOSTNAME' value='$cgiparams{'ROOTCERT_HOSTNAME'}' size='32' /></td>
	    <td colspan='2'>&nbsp;</td></tr>
	<tr><td class='base'>$Lang::tr{'your e-mail'}:&nbsp;<img src='/blob.gif' alt'*' /></td>
	    <td class='base' nowrap='nowrap'><input type='text' name='ROOTCERT_EMAIL' value='$cgiparams{'ROOTCERT_EMAIL'}' size='32' /></td>
	    <td colspan='2'>&nbsp;</td></tr>
	<tr><td class='base'>$Lang::tr{'your department'}:&nbsp;<img src='/blob.gif' alt'*' /></td>
	    <td class='base' nowrap='nowrap'><input type='text' name='ROOTCERT_OU' value='$cgiparams{'ROOTCERT_OU'}' size='32' /></td>
	    <td colspan='2'>&nbsp;</td></tr>
	<tr><td class='base'>$Lang::tr{'city'}:&nbsp;<img src='/blob.gif' alt'*' /></td>
	    <td class='base' nowrap='nowrap'><input type='text' name='ROOTCERT_CITY' value='$cgiparams{'ROOTCERT_CITY'}' size='32' /></td>
	    <td colspan='2'>&nbsp;</td></tr>
	<tr><td class='base'>$Lang::tr{'state or province'}:&nbsp;<img src='/blob.gif' alt'*' /></td>
	    <td class='base' nowrap='nowrap'><input type='text' name='ROOTCERT_STATE' value='$cgiparams{'ROOTCERT_STATE'}' size='32' /></td>
	    <td colspan='2'>&nbsp;</td></tr>
	<tr><td class='base'>$Lang::tr{'country'}:</td>
	    <td class='base'><select name='ROOTCERT_COUNTRY'> 

END
	;
	foreach my $country (sort keys %{Countries::countries}) {
	    print "<option value='$Countries::countries{$country}'";
	    if ( $Countries::countries{$country} eq $cgiparams{'ROOTCERT_COUNTRY'} ) {
		print " selected='selected'";
	    }
	    print ">$country</option>";
	}
	print <<END
	    </select></td>
	    <td colspan='2'>&nbsp;</td></tr>
	<tr><td>&nbsp;</td>
	    <td><input type='submit' name='ACTION' value='$Lang::tr{'generate root/host certificates'}' /></td>
	    <td>&nbsp;</td><td>&nbsp;</td></tr> 
	<tr><td class='base' colspan='4' align='left'>
	    <img src='/blob.gif' valign='top' alt='*' />&nbsp;$Lang::tr{'this field may be blank'}</td></tr>
	<tr><td class='base' colspan='4' align='left'>
	    <b><font color='${Header::colourred}'>$Lang::tr{'capswarning'}</font></b>: 
	    $Lang::tr{'generating the root and host certificates may take a long time. it can take up to several minutes on older hardware. please be patient'}
	</td></tr>
	<tr><td colspan='4' bgcolor='#000000'><img src='/images/null.gif' width='1' height='1' border='0' /></td></tr>
	<tr><td class='base' nowrap='nowrap'>$Lang::tr{'upload p12 file'}:</td>
	    <td nowrap='nowrap'><input type='file' name='FH' size='32'></td>
	    <td colspan='2'>&nbsp;</td></tr>
	<tr><td class='base'>$Lang::tr{'pkcs12 file password'}:&nbsp;<img src='/blob.gif' alt='*' ></td>
	    <td class='base' nowrap='nowrap'><input type='password' name='P12_PASS' value='$cgiparams{'P12_PASS'}' size='32' /></td>
            <td colspan='2'>&nbsp;</td></tr>
	<tr><td>&nbsp;</td>
	    <td><input type='submit' name='ACTION' value='$Lang::tr{'upload p12 file'}' /></td>
            <td colspan='2'>&nbsp;</td></tr>
	<tr><td class='base' colspan='4' align='left'>
	    <img src='/blob.gif' valign='top' al='*' >&nbsp;$Lang::tr{'this field may be blank'}</td></tr>
	</form></table>
END
	;
	&Header::closebox();

	&Header::closebigbox();
	&Header::closepage();
        exit(0)
    }

    ROOTCERT_SUCCESS:
    system ("chmod 600 ${General::swroot}/ovpn/certs/serverkey.pem");
#    if ($vpnsettings{'ENABLED'} eq 'on' ||
#	$vpnsettings{'ENABLE_BLUE'} eq 'on') {
#	system('/usr/local/bin/ipsecctrl', 'S');
#    }

###
### Enable/Disable connection
###
}elsif ($cgiparams{'ACTION'} eq $Lang::tr{'toggle enable disable'}) {
    
    &General::readhash("${General::swroot}/ovpn/settings", \%vpnsettings);
    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

    if ($confighash{$cgiparams{'KEY'}}) {
	if ($confighash{$cgiparams{'KEY'}}[0] eq 'off') {
	    $confighash{$cgiparams{'KEY'}}[0] = 'on';
	    &General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
	    #&writeserverconf();
#	    if ($vpnsettings{'ENABLED'} eq 'on' ||
#		$vpnsettings{'ENABLED_BLUE'} eq 'on') {
#	 	system('/usr/local/bin/ipsecctrl', 'S', $cgiparams{'KEY'});
#	    }
	} else {
	    $confighash{$cgiparams{'KEY'}}[0] = 'off';
#	    if ($vpnsettings{'ENABLED'} eq 'on' ||
#		$vpnsettings{'ENABLED_BLUE'} eq 'on') {
#		system('/usr/local/bin/ipsecctrl', 'D', $cgiparams{'KEY'});
#	    }
	    &General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
	    #&writeserverconf();
	}
    } else {
	$errormessage = $Lang::tr{'invalid key'};
    }

###
### Download OpenVPN client package
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'dl client arch'}) {
    &General::readhash("${General::swroot}/ovpn/settings", \%vpnsettings);
    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
    my $file = '';
    my $clientovpn = '';
    my @fileholder;
    my $tempdir = tempdir( CLEANUP => 1 );
    my $zippath = "$tempdir/";
    my $zipname = "$confighash{$cgiparams{'KEY'}}[1]-TO-IPFire.zip";
    my $zippathname = "$zippath$zipname";
    $clientovpn = "$confighash{$cgiparams{'KEY'}}[1]-TO-IPFire.ovpn";
    open(CLIENTCONF, ">$tempdir/$clientovpn") or die "Unable to open tempfile: $!";
    flock CLIENTCONF, 2;
    
    my $zip = Archive::Zip->new();
    
    print CLIENTCONF "#OpenVPN Server conf\r\n";
    print CLIENTCONF "tls-client\r\n";
    print CLIENTCONF "client\r\n";
    print CLIENTCONF "dev $vpnsettings{'DDEVICE'}\r\n";
    print CLIENTCONF "proto $vpnsettings{'DPROTOCOL'}\r\n";
    print CLIENTCONF "$vpnsettings{'DDEVICE'}-mtu $vpnsettings{'DMTU'}\r\n";
    if ( $vpnsettings{'ENABLED'} eq 'on'){
    	print CLIENTCONF "remote $vpnsettings{'VPN_IP'} $vpnsettings{'DDEST_PORT'}\r\n";
	if ( $vpnsettings{'ENABLED_BLUE'} eq 'on' && (&haveBlueNet())){	
	    print CLIENTCONF "#Coment the above line and uncoment the next line, if you want to connect on the Blue interface\r\n";	
	    print CLIENTCONF ";remote $netsettings{'BLUE_ADDRESS'} $vpnsettings{'DDEST_PORT'}\r\n";
	}
	if ( $vpnsettings{'ENABLED_ORANGE'} eq 'on' && (&haveOrangeNet())){
	    print CLIENTCONF "#Coment the above line and uncoment the next line, if you want to connect on the Orange interface\r\n";		
	    print CLIENTCONF ";remote $netsettings{'ORANGE_ADDRESS'} $vpnsettings{'DDEST_PORT'}\r\n";
	}
    } elsif ( $vpnsettings{'ENABLED_BLUE'} eq 'on' && (&haveBlueNet())){
	print CLIENTCONF "remote $netsettings{'BLUE_ADDRESS'} $vpnsettings{'DDEST_PORT'}\r\n";
	if ( $vpnsettings{'ENABLED_ORANGE'} eq 'on' && (&haveOrangeNet())){
	    print CLIENTCONF "#Coment the above line and uncoment the next line, if you want to connect on the Orange interface\r\n";		
	    print CLIENTCONF ";remote $netsettings{'ORANGE_ADDRESS'} $vpnsettings{'DDEST_PORT'}\r\n";
	}
    } elsif ( $vpnsettings{'ENABLED_ORANGE'} eq 'on' && (&haveOrangeNet())){
	print CLIENTCONF "remote $netsettings{'ORANGE_ADDRESS'} $vpnsettings{'DDEST_PORT'}\r\n";
    }
    	    		
    if ($confighash{$cgiparams{'KEY'}}[4] eq 'cert' && -f "${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1].p12") { 
	print CLIENTCONF "pkcs12 $confighash{$cgiparams{'KEY'}}[1].p12\r\n";
	$zip->addFile( "${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1].p12", "$confighash{$cgiparams{'KEY'}}[1].p12") or die "Can't add file $confighash{$cgiparams{'KEY'}}[1].p12\n";
    } else {
	print CLIENTCONF "ca cacert.pem\r\n";
	print CLIENTCONF "cert $confighash{$cgiparams{'KEY'}}[1]cert.pem\r\n";
	print CLIENTCONF "key $confighash{$cgiparams{'KEY'}}[1].key\r\n";
	$zip->addFile( "${General::swroot}/ovpn/ca/cacert.pem", "cacert.pem")  or die "Can't add file cacert.pem\n";
	$zip->addFile( "${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem", "$confighash{$cgiparams{'KEY'}}[1]cert.pem") or die "Can't add file $confighash{$cgiparams{'KEY'}}[1]cert.pem\n";    
    }
    print CLIENTCONF "cipher $vpnsettings{DCIPHER}\r\n";
    if ($vpnsettings{DCOMPLZO} eq 'on') {
        print CLIENTCONF "comp-lzo\r\n";
    }
    print CLIENTCONF "verb 3\r\n";
    print CLIENTCONF "ns-cert-type server\r\n";
    print CLIENTCONF "tls-remote $vpnsettings{ROOTCERT_HOSTNAME}\r\n"; 
    if ($vpnsettings{MSSFIX} eq 'on') {
	print CLIENTCONF "mssfix\r\n";
    }
    if ($vpnsettings{FRAGMENT} ne '' && $vpnsettings{DPROTOCOL} ne 'tcp' ) {
	print CLIENTCONF "fragment $vpnsettings{'FRAGMENT'}\r\n";
    }
    close(CLIENTCONF);
    $zip->addFile( "$tempdir/$clientovpn", $clientovpn) or die "Can't add file $clientovpn\n";
    my $status = $zip->writeToFileNamed($zippathname);

    open(DLFILE, "<$zippathname") or die "Unable to open $zippathname: $!";
    @fileholder = <DLFILE>;
    print "Content-Type:application/x-download\n";
    print "Content-Disposition:attachment;filename=$zipname\n\n";
    print @fileholder;
    exit (0);

###
### Remove connection
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'remove'}) {
    &General::readhash("${General::swroot}/ovpn/settings", \%vpnsettings);
    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

    if ($confighash{$cgiparams{'KEY'}}) {
#	if ($vpnsettings{'ENABLED'} eq 'on' ||
#	    $vpnsettings{'ENABLED_BLUE'} eq 'on') {
#	    system('/usr/local/bin/ipsecctrl', 'D', $cgiparams{'KEY'});
#	}
#
	my $temp = `/usr/bin/openssl ca -revoke ${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem -config ${General::swroot}/ovpn/openssl/ovpn.cnf`;
	unlink ("${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem");
	unlink ("${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1].p12");
	delete $confighash{$cgiparams{'KEY'}};
	my $temp2 = `/usr/bin/openssl ca -gencrl -out ${General::swroot}/ovpn/crls/cacrl.pem -config ${General::swroot}/ovpn/openssl/ovpn.cnf`;
	&General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
	#&writeserverconf();
    } else {
	$errormessage = $Lang::tr{'invalid key'};
    }
###
### Download PKCS12 file
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'download pkcs12 file'}) {
    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

    print "Content-Disposition: filename=" . $confighash{$cgiparams{'KEY'}}[1] . ".p12\r\n";
    print "Content-Type: application/octet-stream\r\n\r\n";
    print `/bin/cat ${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1].p12`;
    exit (0);

###
### Display certificate
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'show certificate'}) {
    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

    if ( -f "${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem") {
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'vpn configuration main'}, 1, '');
	&Header::openbigbox('100%', 'LEFT', '', '');
	&Header::openbox('100%', 'LEFT', "$Lang::tr{'certificate'}:");
	my $output = `/usr/bin/openssl x509 -text -in ${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem`;
	$output = &Header::cleanhtml($output,"y");
	print "<pre>$output</pre>\n";
	&Header::closebox();
	print "<div align='center'><a href='/cgi-bin/ovpnmain.cgi'>$Lang::tr{'back'}</a></div>";
	&Header::closebigbox();
	&Header::closepage();
	exit(0);
    }
###
### Display Certificate Revoke List
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'show crl'}) {
#    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

    if ( -f "${General::swroot}/ovpn/crls/cacrl.pem") {
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'vpn configuration main'}, 1, '');
	&Header::openbigbox('100%', 'LEFT', '', '');
	&Header::openbox('100%', 'LEFT', "$Lang::tr{'crl'}:");
	my $output = `/usr/bin/openssl crl -text -noout -in ${General::swroot}/ovpn/crls/cacrl.pem`;
	$output = &Header::cleanhtml($output,"y");
	print "<pre>$output</pre>\n";
	&Header::closebox();
	print "<div align='center'><a href='/cgi-bin/ovpnmain.cgi'>$Lang::tr{'back'}</a></div>";
	&Header::closebigbox();
	&Header::closepage();
	exit(0);
    }

###
### Advanced Server Settings
###

} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'advanced server'}) {
    %cgiparams = ();
    %cahash = ();
    %confighash = ();
    &General::readhash("${General::swroot}/ovpn/settings", \%cgiparams);

#    if ($cgiparams{'CLIENT2CLIENT'} eq '') {
#	$cgiparams{'CLIENT2CLIENT'} =  'on';     
#    }
ADV_ERROR:
    if ($cgiparams{'MAX_CLIENTS'} eq '') {
	$cgiparams{'MAX_CLIENTS'} =  '100';     
    }
    
    if ($cgiparams{'KEEPALIVE_1'} eq '') {
	$cgiparams{'KEEPALIVE_1'} =  '10';     
    }
    if ($cgiparams{'KEEPALIVE_2'} eq '') {
	$cgiparams{'KEEPALIVE_2'} =  '60';     
    }
    if ($cgiparams{'LOG_VERB'} eq '') {
	$cgiparams{'LOG_VERB'} =  '3';     
    }
    $checked{'CLIENT2CLIENT'}{'off'} = '';
    $checked{'CLIENT2CLIENT'}{'on'} = '';
    $checked{'CLIENT2CLIENT'}{$cgiparams{'CLIENT2CLIENT'}} = 'CHECKED';
    $checked{'REDIRECT_GW_DEF1'}{'off'} = '';
    $checked{'REDIRECT_GW_DEF1'}{'on'} = '';
    $checked{'REDIRECT_GW_DEF1'}{$cgiparams{'REDIRECT_GW_DEF1'}} = 'CHECKED';
    $selected{'ENGINES'}{$cgiparams{'ENGINES'}} = 'SELECTED';
    $checked{'MSSFIX'}{'off'} = '';
    $checked{'MSSFIX'}{'on'} = '';
    $checked{'MSSFIX'}{$cgiparams{'MSSFIX'}} = 'CHECKED';
    $selected{'LOG_VERB'}{'1'} = '';
    $selected{'LOG_VERB'}{'2'} = '';
    $selected{'LOG_VERB'}{'3'} = '';
    $selected{'LOG_VERB'}{'4'} = '';
    $selected{'LOG_VERB'}{'5'} = '';
    $selected{'LOG_VERB'}{'6'} = '';
    $selected{'LOG_VERB'}{'7'} = '';
    $selected{'LOG_VERB'}{'8'} = '';
    $selected{'LOG_VERB'}{'9'} = '';
    $selected{'LOG_VERB'}{'10'} = '';
    $selected{'LOG_VERB'}{'11'} = '';
    $selected{'LOG_VERB'}{'0'} = '';
    $selected{'LOG_VERB'}{$cgiparams{'LOG_VERB'}} = 'SELECTED';


    
    &Header::showhttpheaders();
    &Header::openpage($Lang::tr{'status ovpn'}, 1, '');
    &Header::openbigbox('100%', 'LEFT', '', $errormessage);    
    if ($errormessage) {
	&Header::openbox('100%', 'LEFT', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
    }
    &Header::openbox('100%', 'LEFT', $Lang::tr{'advanced server'});
    print <<END
    <form method='post' enctype='multipart/form-data'>
    <table width='100%'>
    <tr>
	<td colspan='4'><b>$Lang::tr{'dhcp-options'}</b></td>
    </tr>
    <tr>
	<td width='25%'></td> <td width='20%'> </td><td width='25%'> </td><td width='30%'></td>
    </tr>	
    <tr>		
	<td class='base'>Domain</td>
        <td><input type='TEXT' name='DHCP_DOMAIN' value='$cgiparams{'DHCP_DOMAIN'}' size='30' /></td>
    </tr>
    <tr>	
	<td class='base'>DNS</td>
	<td><input type='TEXT' name='DHCP_DNS' value='$cgiparams{'DHCP_DNS'}' size='30' /></td>
    </tr>	
    <tr>	
	<td class='base'>WINS</td>
	<td><input type='TEXT' name='DHCP_WINS' value='$cgiparams{'DHCP_WINS'}' size='30' /></td>
    </tr>
</table>
<hr size='1'>
    <table width='100%'>
    <tr>
	<td class'base'><b>$Lang::tr{'misc-options'}</b></td>
    </tr>
    <tr>
	<td width='20%'></td> <td width='15%'> </td><td width='15%'> </td><td width='50%'></td>
    </tr>
    <tr>
	<td class='base'>Client-To-Client</td>
	<td><input type='checkbox' name='CLIENT2CLIENT' $checked{'CLIENT2CLIENT'}{'on'} /></td>
    </tr>
    <tr>	
	<td class='base'>Redirect-Gateway def1</td>
	<td><input type='checkbox' name='REDIRECT_GW_DEF1' $checked{'REDIRECT_GW_DEF1'}{'on'} /></td>
    </tr>
    <tr>	
        <td class='base'>Max-Clients</td>
        <td><input type='text' name='MAX_CLIENTS' value='$cgiparams{'MAX_CLIENTS'}' size='10' /></td>
    </tr>	
     	<tr>
     	  <td class='base'>Keppalive <br />
     	    (ping/ping-restart)</td>
     	  <td><input type='TEXT' name='KEEPALIVE_1' value='$cgiparams{'KEEPALIVE_1'}' size='10' /></td>
     	  <td><input type='TEXT' name='KEEPALIVE_2' value='$cgiparams{'KEEPALIVE_2'}' size='10' /></td>
    </tr>
     	<tr>
     	  <td class='base'>fragment <br></td>
     	  <td><input type='TEXT' name='FRAGMENT' value='$cgiparams{'FRAGMENT'}' size='10' /></td>
     	  <td>Default: <span class="base">1300</span></td>
   	  </tr>
     	<tr>
     	  <td class='base'>mssfix</td>
     	  <td><input type='checkbox' name='MSSFIX' $checked{'MSSFIX'}{'on'} /></td>
     	  <td>Default: on</td>
   	  </tr>	
</table>

<!--
<hr size='1'>
    <table width='100%'>
    <tr>
 <td class'base'><b>Crypto-Engines</b></td>
    </tr>
    <tr>
	<td width='15%'></td> <td width='30%'> </td><td width='25%'> </td><td width='30%'></td>
    </tr>	
    <tr><td class='base'>Engines:</td>        
        <td><select name='ENGINES'><option value="none" $selected{'ENGINES'}{'none'}>none</option>
				    <option value="cryptodev" $selected{'ENGINES'}{'cryptodev'}>cryptodev</option>
				    <option value="padlock" $selected{'ENGINES'}{'padlock'}>padlock</option>
			</select>
		</td>	
</table>
-->
<hr size='1'>
    <table width='100%'>
    <tr>
	<td class'base'><b>$Lang::tr{'log-options'}</b></td>
    </tr>
    <tr>
	<td width='15%'></td> <td width='30%'> </td><td width='25%'> </td><td width='30%'></td>
    </tr>	
	
    <tr><td class='base'>VERB</td>        
        <td><select name='LOG_VERB'><option value='1'  $selected{'LOG_VERB'}{'1'}>1</option>
				    <option value='2'  $selected{'LOG_VERB'}{'2'}>2</option>
				    <option value='3'  $selected{'LOG_VERB'}{'3'}>3</option>
				    <option value='4'  $selected{'LOG_VERB'}{'4'}>4</option>
				    <option value='5'  $selected{'LOG_VERB'}{'5'}>5</option>
				    <option value='6'  $selected{'LOG_VERB'}{'6'}>6</option>				  				    
				    <option value='7'  $selected{'LOG_VERB'}{'7'}>7</option>
				    <option value='8'  $selected{'LOG_VERB'}{'8'}>8</option>
				    <option value='9'  $selected{'LOG_VERB'}{'9'}>9</option>
				    <option value='10' $selected{'LOG_VERB'}{'10'}>10</option>
				    <option value='11' $selected{'LOG_VERB'}{'11'}>11</option>
				    <option value='0'  $selected{'LOG_VERB'}{'0'}>0</option></select></td>	
</table>
<hr size='1'>
<table width='100%'>
<tr>
    <td>&nbsp;</td>
    <td allign='center'><input type='submit' name='ACTION' value='$Lang::tr{'save-adv-options'}' /></td>
    <td allign='center'><input type='submit' name='ACTION' value='$Lang::tr{'cancel-adv-options'}' /></td>
    <td>&nbsp;</td>    
</tr>
</table>    
</form>
END
;				   

    &Header::closebox();
#    print "<div align='center'><a href='/cgi-bin/ovpnmain.cgi'>$Lang::tr{'back'}</a></div>";
    &Header::closebigbox();
    &Header::closepage();
    exit(0);
	
###
### Openvpn Connections Statistics
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'ovpn con stat'}) {
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'ovpn con stat'}, 1, '');
	&Header::openbigbox('100%', 'LEFT', '', '');
    &Header::openbox('100%', 'LEFT', $Lang::tr{'ovpn con stat'});

#
#	<td><b>$Lang::tr{'protocol'}</b></td>
# protocol temp removed 
    print <<END
    <table width='100%' border='0' cellpadding='2' cellspacing='0'>
    <tr>
	<td><b>$Lang::tr{'common name'}</b></td>
	<td><b>$Lang::tr{'real address'}</b></td>
	<td><b>$Lang::tr{'virtual address'}</b></td>
	<td><b>$Lang::tr{'loged in at'}</b></td>
	<td><b>$Lang::tr{'bytes sent'}</b></td>
	<td><b>$Lang::tr{'bytes received'}</b></td>
	<td><b>$Lang::tr{'last activity'}</b></td>
    </tr>
END
;
	my $filename = "/var/log/ovpnserver.log";
	open(FILE, $filename) or die 'Unable to open config file.';
	my @current = <FILE>;
	close(FILE);
	my @users =();
	my $status;
	my $uid = 0;
	my $cn;
	my @match = ();
	my $proto = "udp";
	my $address;
	my %userlookup = ();
	foreach my $line (@current)
	{
	    chomp($line);
	    if ( $line =~ /^Updated,(.+)/){
		@match = split( /^Updated,(.+)/, $line); 
		$status = $match[1];
	    }
#gian	    
	    if ( $line =~ /^(.+),(\d+\.\d+\.\d+\.\d+\:\d+),(\d+),(\d+),(.+)/) {
		@match = split(m/^(.+),(\d+\.\d+\.\d+\.\d+\:\d+),(\d+),(\d+),(.+)/, $line);
		if ($match[1] ne "Common Name") {
	    	    $cn = $match[1];
		    $userlookup{$match[2]} = $uid;
		    $users[$uid]{'CommonName'} = $match[1];
		    $users[$uid]{'RealAddress'} = $match[2];
		    $users[$uid]{'BytesReceived'} = &sizeformat($match[3]);
		    $users[$uid]{'BytesSent'} = &sizeformat($match[4]);
		    $users[$uid]{'Since'} = $match[5];
		    $users[$uid]{'Proto'} = $proto;
		    $uid++;
		}    
	    }
	    if ( $line =~ /^(\d+\.\d+\.\d+\.\d+),(.+),(\d+\.\d+\.\d+\.\d+\:\d+),(.+)/) {
		@match = split(m/^(\d+\.\d+\.\d+\.\d+),(.+),(\d+\.\d+\.\d+\.\d+\:\d+),(.+)/, $line);
		if ($match[1] ne "Virtual Address") {
		    $address = $match[3];
		    #find the uid in the lookup table
		    $uid = $userlookup{$address};
		    $users[$uid]{'VirtualAddress'} = $match[1];
		    $users[$uid]{'LastRef'} = $match[4];
		}
	    }
	}
	my $user2 = @users;
	if ($user2 >= 1){
    	    for (my $idx = 1; $idx <= $user2; $idx++){
						if ($idx % 2) {
		    			print "<tr bgcolor='$color{'color20'}'>\n";
	    			} else {
		    			print "<tr bgcolor='$color{'color22'}'>\n";
						}
						print "<td align='left'>$users[$idx-1]{'CommonName'}</td>";
						print "<td align='left'>$users[$idx-1]{'RealAddress'}</td>";
						print "<td align='left'>$users[$idx-1]{'VirtualAddress'}</td>";
						print "<td align='left'>$users[$idx-1]{'Since'}</td>";
						print "<td align='left'>$users[$idx-1]{'BytesSent'}</td>";
						print "<td align='left'>$users[$idx-1]{'BytesReceived'}</td>";
						print "<td align='left'>$users[$idx-1]{'LastRef'}</td>";
#		        print "<td align='left'>$users[$idx-1]{'Proto'}</td>";
	    }
	}        
	
	print "</table>";
	print <<END
	<table width='100%' border='0' cellpadding='2' cellspacing='0'>
	<tr><td></td></tr>
	<tr><td></td></tr>
	<tr><td></td></tr>
	<tr><td></td></tr>
	<tr><td align='center' >$Lang::tr{'the statistics were last updated at'} <b>$status</b></td></tr>
	</table>
END
;	
	&Header::closebox();
	print "<div align='center'><a href='/cgi-bin/ovpnmain.cgi'>$Lang::tr{'back'}</a></div>";
	&Header::closebigbox();
	&Header::closepage();
	exit(0);

###
### Download Certificate
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'download certificate'}) {
    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

    if ( -f "${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem") {
	print "Content-Disposition: filename=" . $confighash{$cgiparams{'KEY'}}[1] . "cert.pem\r\n";
	print "Content-Type: application/octet-stream\r\n\r\n";
	print `/bin/cat ${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem`;
	exit (0);
    }

###
### Enable/Disable connection
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'toggle enable disable'}) {
    
    &General::readhash("${General::swroot}/ovpn/settings", \%vpnsettings);
    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

    if ($confighash{$cgiparams{'KEY'}}) {
	if ($confighash{$cgiparams{'KEY'}}[0] eq 'off') {
	    $confighash{$cgiparams{'KEY'}}[0] = 'on';
	    &General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
	    #&writeserverconf();
#	    if ($vpnsettings{'ENABLED'} eq 'on' ||
#		$vpnsettings{'ENABLED_BLUE'} eq 'on') {
#	 	system('/usr/local/bin/ipsecctrl', 'S', $cgiparams{'KEY'});
#	    }
	} else {
	    $confighash{$cgiparams{'KEY'}}[0] = 'off';
#	    if ($vpnsettings{'ENABLED'} eq 'on' ||
#		$vpnsettings{'ENABLED_BLUE'} eq 'on') {
#		system('/usr/local/bin/ipsecctrl', 'D', $cgiparams{'KEY'});
#	    }
	    &General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
	    #&writeserverconf();
	}
    } else {
	$errormessage = $Lang::tr{'invalid key'};
    }

###
### Restart connection
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'restart'}) {
    &General::readhash("${General::swroot}/ovpn/settings", \%vpnsettings);
    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

    if ($confighash{$cgiparams{'KEY'}}) {
#	if ($vpnsettings{'ENABLED'} eq 'on' ||
#	    $vpnsettings{'ENABLED_BLUE'} eq 'on') {
#	    system('/usr/local/bin/ipsecctrl', 'S', $cgiparams{'KEY'});
#	}
    } else {
	$errormessage = $Lang::tr{'invalid key'};
    }

###
### Remove connection
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'remove'}) {
    &General::readhash("${General::swroot}/ovpn/settings", \%vpnsettings);
    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

    if ($confighash{$cgiparams{'KEY'}}) {
#	if ($vpnsettings{'ENABLED'} eq 'on' ||
#	    $vpnsettings{'ENABLED_BLUE'} eq 'on') {
#	    system('/usr/local/bin/ipsecctrl', 'D', $cgiparams{'KEY'});
#	}
	unlink ("${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem");
	unlink ("${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1].p12");
	delete $confighash{$cgiparams{'KEY'}};
	&General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
	#&writeserverconf();
    } else {
	$errormessage = $Lang::tr{'invalid key'};
    }
} elsif (($cgiparams{'ACTION'} eq $Lang::tr{'add'}) ||
	 ($cgiparams{'ACTION'} eq $Lang::tr{'edit'}) ||
	 ($cgiparams{'ACTION'} eq $Lang::tr{'save'} && $cgiparams{'ADVANCED'} eq '')) {

    &General::readhash("${General::swroot}/ovpn/settings", \%vpnsettings);
    &General::readhasharray("${General::swroot}/ovpn/caconfig", \%cahash);
    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

    if ($cgiparams{'ACTION'} eq $Lang::tr{'edit'}) {
	if (! $confighash{$cgiparams{'KEY'}}[0]) {
	    $errormessage = $Lang::tr{'invalid key'};
	    goto VPNCONF_END;
	}

	$cgiparams{'ENABLED'}	= $confighash{$cgiparams{'KEY'}}[0];
	$cgiparams{'NAME'}	= $confighash{$cgiparams{'KEY'}}[1];
	$cgiparams{'TYPE'}	= 'host';
	$cgiparams{'AUTH'} 	= $confighash{$cgiparams{'KEY'}}[4];
	$cgiparams{'PSK'}	= $confighash{$cgiparams{'KEY'}}[5];
	$cgiparams{'SIDE'}	= $confighash{$cgiparams{'KEY'}}[6];
	$cgiparams{'LOCAL_SUBNET'} = $confighash{$cgiparams{'KEY'}}[8];
	$cgiparams{'REMOTE'}	= $confighash{$cgiparams{'KEY'}}[10];
	$cgiparams{'REMOTE_SUBNET'} = $confighash{$cgiparams{'KEY'}}[11];
	$cgiparams{'REMARK'}	= $confighash{$cgiparams{'KEY'}}[25];
	$cgiparams{'INTERFACE'}	= $confighash{$cgiparams{'KEY'}}[26];
#new fields	
	$cgiparams{'OVPN_SUBNET'} = $confighash{$cgiparams{'KEY'}}[27];
	$cgiparams{'PROTOCOL'}	  = $confighash{$cgiparams{'KEY'}}[28];
	$cgiparams{'DEST_PORT'}	  = $confighash{$cgiparams{'KEY'}}[29];
	$cgiparams{'COMPLZO'}	  = $confighash{$cgiparams{'KEY'}}[30];
	$cgiparams{'MTU'}	  = $confighash{$cgiparams{'KEY'}}[31];
#new fields
#ab hiere error uebernehmen
    } elsif ($cgiparams{'ACTION'} eq $Lang::tr{'save'}) {
	$cgiparams{'REMARK'} = &Header::cleanhtml($cgiparams{'REMARK'});
	if ($cgiparams{'TYPE'} !~ /^(host|net)$/) {
	    $errormessage = $Lang::tr{'connection type is invalid'};
	    goto VPNCONF_ERROR;
	}


	if ($cgiparams{'NAME'} !~ /^[a-zA-Z0-9]+$/) {
	    $errormessage = $Lang::tr{'name must only contain characters'};
	    goto VPNCONF_ERROR;
	}

	if ($cgiparams{'NAME'} =~ /^(host|01|block|private|clear|packetdefault)$/) {
	    $errormessage = $Lang::tr{'name is invalid'};
	    goto VPNCONF_ERROR;
	}

	if (length($cgiparams{'NAME'}) >60) {
	    $errormessage = $Lang::tr{'name too long'};
	    goto VPNCONF_ERROR;
	}

	# Check if there is no other entry with this name
	if (! $cgiparams{'KEY'}) {
	    foreach my $key (keys %confighash) {
		if ($confighash{$key}[1] eq $cgiparams{'NAME'}) {
		    $errormessage = $Lang::tr{'a connection with this name already exists'};
		    goto VPNCONF_ERROR;
		}
	    }
	}

	if ($cgiparams{'REMOTE'}) {
	    if (! &General::validip($cgiparams{'REMOTE'})) {
		if (! &General::validfqdn ($cgiparams{'REMOTE'}))  {
		    $errormessage = $Lang::tr{'invalid input for remote host/ip'};
		    goto VPNCONF_ERROR;
		} else {
		    if (&valid_dns_host($cgiparams{'REMOTE'})) {
			$warnmessage = "$Lang::tr{'check vpn lr'} $cgiparams{'REMOTE'}. $Lang::tr{'dns check failed'}";
		    }
		}
	    }
	}
	if ($cgiparams{'TYPE'} ne 'host') {
            unless (&General::validipandmask($cgiparams{'LOCAL_SUBNET'})) {
	            $errormessage = $Lang::tr{'local subnet is invalid'}; 
			goto VPNCONF_ERROR;}
	}
	# Check if there is no other entry without IP-address and PSK
	if ($cgiparams{'REMOTE'} eq '') {
	    foreach my $key (keys %confighash) {
		if(($cgiparams{'KEY'} ne $key) && 
		   ($confighash{$key}[4] eq 'psk' || $cgiparams{'AUTH'} eq 'psk') && 
		    $confighash{$key}[10] eq '') {
			$errormessage = $Lang::tr{'you can only define one roadwarrior connection when using pre-shared key authentication'};
			goto VPNCONF_ERROR;
		}
	    }
	}

	if ($cgiparams{'ENABLED'} !~ /^(on|off)$/) {
	    $errormessage = $Lang::tr{'invalid input'};
	    goto VPNCONF_ERROR;
	}
	if ($cgiparams{'EDIT_ADVANCED'} !~ /^(on|off)$/) {
	    $errormessage = $Lang::tr{'invalid input'};
	    goto VPNCONF_ERROR;
	}

#fixplausi
	if ($cgiparams{'AUTH'} eq 'psk')  {
#	    if (! length($cgiparams{'PSK'}) ) {
#		$errormessage = $Lang::tr{'pre-shared key is too short'};
#		goto VPNCONF_ERROR;
#	    }
#	    if ($cgiparams{'PSK'} =~ /['",&]/) {
#		$errormessage = $Lang::tr{'invalid characters found in pre-shared key'};
#		goto VPNCONF_ERROR;
#	    }
	} elsif ($cgiparams{'AUTH'} eq 'certreq') {
	    if ($cgiparams{'KEY'}) {
		$errormessage = $Lang::tr{'cant change certificates'};
		goto VPNCONF_ERROR;
	    }
	    if (ref ($cgiparams{'FH'}) ne 'Fh') {
		$errormessage = $Lang::tr{'there was no file upload'};
		goto VPNCONF_ERROR;
	    }

	    # Move uploaded certificate request to a temporary file
	    (my $fh, my $filename) = tempfile( );
	    if (copy ($cgiparams{'FH'}, $fh) != 1) {
		$errormessage = $!;
		goto VPNCONF_ERROR;
	    }

	    # Sign the certificate request and move it
	    # Sign the host certificate request
	    system('/usr/bin/openssl', 'ca', '-days', '999999',
		'-batch', '-notext',
		'-in', $filename,
		'-out', "${General::swroot}/ovpn/certs/$cgiparams{'NAME'}cert.pem",
		'-config',"${General::swroot}/ovpn/openssl/ovpn.cnf");
	    if ($?) {
		$errormessage = "$Lang::tr{'openssl produced an error'}: $?";
		unlink ($filename);
		unlink ("${General::swroot}/ovpn/certs/$cgiparams{'NAME'}cert.pem");
		&newcleanssldatabase();
		goto VPNCONF_ERROR;
	    } else {
		unlink ($filename);
		&deletebackupcert();
	    }

	    my $temp = `/usr/bin/openssl x509 -text -in ${General::swroot}/ovpn/certs/$cgiparams{'NAME'}cert.pem`;
	    $temp =~ /Subject:.*CN=(.*)[\n]/;
	    $temp = $1;
	    $temp =~ s+/Email+, E+;
	    $temp =~ s/ ST=/ S=/;
	    $cgiparams{'CERT_NAME'} = $temp;
	    $cgiparams{'CERT_NAME'} =~ s/,//g;
	    $cgiparams{'CERT_NAME'} =~ s/\'//g;
	    if ($cgiparams{'CERT_NAME'} eq '') {
		$errormessage = $Lang::tr{'could not retrieve common name from certificate'};
		goto VPNCONF_ERROR;
	    }
	} elsif ($cgiparams{'AUTH'} eq 'certfile') {
	    if ($cgiparams{'KEY'}) {
		$errormessage = $Lang::tr{'cant change certificates'};
		goto VPNCONF_ERROR;
	    }
	    if (ref ($cgiparams{'FH'}) ne 'Fh') {
		$errormessage = $Lang::tr{'there was no file upload'};
		goto VPNCONF_ERROR;
	    }
	    # Move uploaded certificate to a temporary file
	    (my $fh, my $filename) = tempfile( );
	    if (copy ($cgiparams{'FH'}, $fh) != 1) {
		$errormessage = $!;
		goto VPNCONF_ERROR;
	    }

	    # Verify the certificate has a valid CA and move it
	    my $validca = 0;
	    my $test = `/usr/bin/openssl verify -CAfile ${General::swroot}/ovpn/ca/cacert.pem $filename`;
	    if ($test =~ /: OK/) {
		$validca = 1;
	    } else {
		foreach my $key (keys %cahash) {
		    $test = `/usr/bin/openssl verify -CAfile ${General::swroot}/ovpn/ca/$cahash{$key}[0]cert.pem $filename`;
		    if ($test =~ /: OK/) {
			$validca = 1;
		    }
		}
	    }
	    if (! $validca) {
		$errormessage = $Lang::tr{'certificate does not have a valid ca associated with it'};
		unlink ($filename);
		goto VPNCONF_ERROR;
	    } else {
		move($filename, "${General::swroot}/ovpn/certs/$cgiparams{'NAME'}cert.pem");
		if ($? ne 0) {
		    $errormessage = "$Lang::tr{'certificate file move failed'}: $!";
		    unlink ($filename);
		    goto VPNCONF_ERROR;
		}
	    }

	    my $temp = `/usr/bin/openssl x509 -text -in ${General::swroot}/ovpn/certs/$cgiparams{'NAME'}cert.pem`;
	    $temp =~ /Subject:.*CN=(.*)[\n]/;
	    $temp = $1;
	    $temp =~ s+/Email+, E+;
	    $temp =~ s/ ST=/ S=/;
	    $cgiparams{'CERT_NAME'} = $temp;
	    $cgiparams{'CERT_NAME'} =~ s/,//g;
	    $cgiparams{'CERT_NAME'} =~ s/\'//g;
	    if ($cgiparams{'CERT_NAME'} eq '') {
		unlink ("${General::swroot}/ovpn/certs/$cgiparams{'NAME'}cert.pem");
		$errormessage = $Lang::tr{'could not retrieve common name from certificate'};
		goto VPNCONF_ERROR;
	    }
	} elsif ($cgiparams{'AUTH'} eq 'certgen') {
	
	    $cgiparams{'CERT_NAME'} =~ s/ //g;
	
	    if ($cgiparams{'KEY'}) {
		$errormessage = $Lang::tr{'cant change certificates'};
		goto VPNCONF_ERROR;
	    }
	    # Validate input since the form was submitted
	    if (length($cgiparams{'CERT_NAME'}) >60) {
		$errormessage = $Lang::tr{'name too long'};
		goto VPNCONF_ERROR;
	    }
	    if ($cgiparams{'CERT_NAME'} !~ /^[a-zA-Z0-9 ,\.\-_]+$/) {
		$errormessage = $Lang::tr{'invalid input for name'};
		goto VPNCONF_ERROR;
	    }
	    if ($cgiparams{'CERT_EMAIL'} ne '' && (! &General::validemail($cgiparams{'CERT_EMAIL'}))) {
		$errormessage = $Lang::tr{'invalid input for e-mail address'};
		goto VPNCONF_ERROR;
	    }
	    if (length($cgiparams{'CERT_EMAIL'}) > 40) {
		$errormessage = $Lang::tr{'e-mail address too long'};
		goto VPNCONF_ERROR;
	    }
	    if ($cgiparams{'CERT_OU'} ne '' && $cgiparams{'CERT_OU'} !~ /^[a-zA-Z0-9 ,\.\-_]*$/) {
		$errormessage = $Lang::tr{'invalid input for department'};
		goto VPNCONF_ERROR;
	    }
	    if (length($cgiparams{'CERT_ORGANIZATION'}) >60) {
		$errormessage = $Lang::tr{'organization too long'};
		goto VPNCONF_ERROR;
	    }
	    if ($cgiparams{'CERT_ORGANIZATION'} !~ /^[a-zA-Z0-9 ,\.\-_]+$/) {
		$errormessage = $Lang::tr{'invalid input for organization'};
		goto VPNCONF_ERROR;
	    }
	    if ($cgiparams{'CERT_CITY'} ne '' && $cgiparams{'CERT_CITY'} !~ /^[a-zA-Z0-9 ,\.\-_]*$/) {
		$errormessage = $Lang::tr{'invalid input for city'};
		goto VPNCONF_ERROR;
	    }
	    if ($cgiparams{'CERT_STATE'} ne '' && $cgiparams{'CERT_STATE'} !~ /^[a-zA-Z0-9 ,\.\-_]*$/) {
		$errormessage = $Lang::tr{'invalid input for state or province'};
		goto VPNCONF_ERROR;
	    }
	    if ($cgiparams{'CERT_COUNTRY'} !~ /^[A-Z]*$/) {
		$errormessage = $Lang::tr{'invalid input for country'};
		goto VPNCONF_ERROR;
	    }
	    if ($cgiparams{'CERT_PASS1'} ne '' && $cgiparams{'CERT_PASS2'} ne ''){
		if (length($cgiparams{'CERT_PASS1'}) < 5) {
		    $errormessage = $Lang::tr{'password too short'};
		    goto VPNCONF_ERROR;
		}
	    }	
	    if ($cgiparams{'CERT_PASS1'} ne $cgiparams{'CERT_PASS2'}) {
		$errormessage = $Lang::tr{'passwords do not match'};
		goto VPNCONF_ERROR;
	    }

	    # Replace empty strings with a .
	    (my $ou = $cgiparams{'CERT_OU'}) =~ s/^\s*$/\./;
	    (my $city = $cgiparams{'CERT_CITY'}) =~ s/^\s*$/\./;
	    (my $state = $cgiparams{'CERT_STATE'}) =~ s/^\s*$/\./;

	    # Create the Host certificate request client
	    my $pid = open(OPENSSL, "|-");
	    $SIG{ALRM} = sub { $errormessage = $Lang::tr{'broken pipe'}; goto VPNCONF_ERROR;};
	    if ($pid) {	# parent
		print OPENSSL "$cgiparams{'CERT_COUNTRY'}\n";
		print OPENSSL "$state\n";
		print OPENSSL "$city\n";
		print OPENSSL "$cgiparams{'CERT_ORGANIZATION'}\n";
		print OPENSSL "$ou\n";
		print OPENSSL "$cgiparams{'CERT_NAME'}\n";
		print OPENSSL "$cgiparams{'CERT_EMAIL'}\n";
		print OPENSSL ".\n";
		print OPENSSL ".\n";
		close (OPENSSL);
		if ($?) {
		    $errormessage = "$Lang::tr{'openssl produced an error'}: $?";
		    unlink ("${General::swroot}ovpn/certs/$cgiparams{'NAME'}key.pem");
		    unlink ("${General::swroot}ovpn/certs/$cgiparams{'NAME'}req.pem");
		    goto VPNCONF_ERROR;
		}
	    } else {	# child
		unless (exec ('/usr/bin/openssl', 'req', '-nodes', '-rand', '/proc/interrupts:/proc/net/rt_cache',
			'-newkey', 'rsa:1024',
			'-keyout', "${General::swroot}/ovpn/certs/$cgiparams{'NAME'}key.pem",
			'-out', "${General::swroot}/ovpn/certs/$cgiparams{'NAME'}req.pem",
			'-config',"${General::swroot}/ovpn/openssl/ovpn.cnf")) {
		    $errormessage = "$Lang::tr{'cant start openssl'}: $!";
		    unlink ("${General::swroot}/ovpn/certs/$cgiparams{'NAME'}key.pem");
		    unlink ("${General::swroot}/ovpn/certs/$cgiparams{'NAME'}req.pem");
		    goto VPNCONF_ERROR;
		}
	    }
	
	    # Sign the host certificate request
	    system('/usr/bin/openssl', 'ca', '-days', '999999',
		'-batch', '-notext',
		'-in',  "${General::swroot}/ovpn/certs/$cgiparams{'NAME'}req.pem",
		'-out', "${General::swroot}/ovpn/certs/$cgiparams{'NAME'}cert.pem",
		'-config',"${General::swroot}/ovpn/openssl/ovpn.cnf");
	    if ($?) {
		$errormessage = "$Lang::tr{'openssl produced an error'}: $?";
		unlink ("${General::swroot}/ovpn/certs/$cgiparams{'NAME'}key.pem");
		unlink ("${General::swroot}/ovpn/certs/$cgiparams{'NAME'}req.pem");
		unlink ("${General::swroot}/ovpn/certs/$cgiparams{'NAME'}cert.pem");
		&newcleanssldatabase();
		goto VPNCONF_ERROR;
	    } else {
		unlink ("${General::swroot}/ovpn/certs/$cgiparams{'NAME'}req.pem");
		&deletebackupcert();
	    }

	    # Create the pkcs12 file
	    system('/usr/bin/openssl', 'pkcs12', '-export', 
		'-inkey', "${General::swroot}/ovpn/certs/$cgiparams{'NAME'}key.pem",
		'-in', "${General::swroot}/ovpn/certs/$cgiparams{'NAME'}cert.pem",
		'-name', $cgiparams{'NAME'},
		'-passout', "pass:$cgiparams{'CERT_PASS1'}",
		'-certfile', "${General::swroot}/ovpn/ca/cacert.pem", 
		'-caname', "$vpnsettings{'ROOTCERT_ORGANIZATION'} CA",
		'-out', "${General::swroot}/ovpn/certs/$cgiparams{'NAME'}.p12");
	    if ($?) {
		$errormessage = "$Lang::tr{'openssl produced an error'}: $?";
		unlink ("${General::swroot}/ovpn/certs/$cgiparams{'NAME'}key.pem");
		unlink ("${General::swroot}/ovpn/certs/$cgiparams{'NAME'}cert.pem");
		unlink ("${General::swroot}/ovpn/certs/$cgiparams{'NAME'}.p12");
		goto VPNCONF_ERROR;
	    } else {
		unlink ("${General::swroot}/ovpn/certs/$cgiparams{'NAME'}key.pem");
	    }
	} elsif ($cgiparams{'AUTH'} eq 'cert') {
	    ;# Nothing, just editing
	} else {
	    $errormessage = $Lang::tr{'invalid input for authentication method'};
	    goto VPNCONF_ERROR;
	}

	# Check if there is no other entry with this common name
	if ((! $cgiparams{'KEY'}) && ($cgiparams{'AUTH'} ne 'psk')) {
	    foreach my $key (keys %confighash) {
		if ($confighash{$key}[2] eq $cgiparams{'CERT_NAME'}) {
		    $errormessage = $Lang::tr{'a connection with this common name already exists'};
		    goto VPNCONF_ERROR;
		}
	    }
	}

        # Save the config
	my $key = $cgiparams{'KEY'};
	if (! $key) {
	    $key = &General::findhasharraykey (\%confighash);
	    foreach my $i (0 .. 31) { $confighash{$key}[$i] = "";}
	}
	$confighash{$key}[0] = $cgiparams{'ENABLED'};
	$confighash{$key}[1] = $cgiparams{'NAME'};
	if ((! $cgiparams{'KEY'}) && $cgiparams{'AUTH'} ne 'psk') {
	    $confighash{$key}[2] = $cgiparams{'CERT_NAME'};
	}
	$confighash{$key}[3] = 'host';
	if ($cgiparams{'AUTH'} eq 'psk') {
	    $confighash{$key}[4] = 'psk';
	    $confighash{$key}[5] = $cgiparams{'PSK'};
	} else {
	    $confighash{$key}[4] = 'cert';
	}
	$confighash{$key}[8] = $cgiparams{'LOCAL_SUBNET'};
	$confighash{$key}[10] = $cgiparams{'REMOTE'};
	$confighash{$key}[25] = $cgiparams{'REMARK'};
	$confighash{$key}[26] = $cgiparams{'INTERFACE'};
# new fields	
	$confighash{$key}[27] = $cgiparams{'OVPN_SUBNET'};
	$confighash{$key}[28] = $cgiparams{'PROTOCOL'};
	$confighash{$key}[29] = $cgiparams{'DEST_PORT'};
	$confighash{$key}[30] = $cgiparams{'COMPLZO'};
	$confighash{$key}[31] = $cgiparams{'MTU'};
# new fileds	
	&General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
	if ($cgiparams{'EDIT_ADVANCED'} eq 'on') {
	    $cgiparams{'KEY'} = $key;
	    $cgiparams{'ACTION'} = $Lang::tr{'advanced'};
	}
	goto VPNCONF_END;
    } else {
        $cgiparams{'ENABLED'} = 'on';
	$cgiparams{'SIDE'} = 'left';
	if ( ! -f "${General::swroot}/ovpn/ca/cakey.pem" ) {
	    $cgiparams{'AUTH'} = 'psk';
	} elsif ( ! -f "${General::swroot}/ovpn/ca/cacert.pem") {
	    $cgiparams{'AUTH'} = 'certfile';
	} else {
            $cgiparams{'AUTH'} = 'certgen';
	}
	$cgiparams{'LOCAL_SUBNET'}      ="$netsettings{'GREEN_NETADDRESS'}/$netsettings{'GREEN_NETMASK'}";
	$cgiparams{'CERT_ORGANIZATION'} = $vpnsettings{'ROOTCERT_ORGANIZATION'};
	$cgiparams{'CERT_CITY'}         = $vpnsettings{'ROOTCERT_CITY'};
	$cgiparams{'CERT_STATE'}        = $vpnsettings{'ROOTCERT_STATE'};
	$cgiparams{'CERT_COUNTRY'}      = $vpnsettings{'ROOTCERT_COUNTRY'};
    }

    VPNCONF_ERROR:
    $checked{'ENABLED'}{'off'} = '';
    $checked{'ENABLED'}{'on'} = '';
    $checked{'ENABLED'}{$cgiparams{'ENABLED'}} = 'CHECKED';
    $checked{'ENABLED_BLUE'}{'off'} = '';
    $checked{'ENABLED_BLUE'}{'on'} = '';
    $checked{'ENABLED_BLUE'}{$cgiparams{'ENABLED_BLUE'}} = 'CHECKED';
    $checked{'ENABLED_ORANGE'}{'off'} = '';
    $checked{'ENABLED_ORANGE'}{'on'} = '';
    $checked{'ENABLED_ORANGE'}{$cgiparams{'ENABLED_ORANGE'}} = 'CHECKED';


    $checked{'EDIT_ADVANCED'}{'off'} = '';
    $checked{'EDIT_ADVANCED'}{'on'} = '';
    $checked{'EDIT_ADVANCED'}{$cgiparams{'EDIT_ADVANCED'}} = 'CHECKED';

    $selected{'SIDE'}{'server'} = '';
    $selected{'SIDE'}{'client'} = '';
    $selected{'SIDE'}{$cgiparams{'SIDE'}} = 'SELECTED';

    $checked{'AUTH'}{'psk'} = '';
    $checked{'AUTH'}{'certreq'} = '';
    $checked{'AUTH'}{'certgen'} = '';
    $checked{'AUTH'}{'certfile'} = '';
    $checked{'AUTH'}{$cgiparams{'AUTH'}} = 'CHECKED';

    $selected{'INTERFACE'}{$cgiparams{'INTERFACE'}} = 'SELECTED';
    
    $checked{'COMPLZO'}{'off'} = '';
    $checked{'COMPLZO'}{'on'} = '';
    $checked{'COMPLZO'}{$cgiparams{'COMPLZO'}} = 'CHECKED';


    if (1) {
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'vpn configuration main'}, 1, '');
	&Header::openbigbox('100%', 'LEFT', '', $errormessage);
	if ($errormessage) {
	    &Header::openbox('100%', 'LEFT', $Lang::tr{'error messages'});
	    print "<class name='base'>$errormessage";
	    print "&nbsp;</class>";
	    &Header::closebox();
	}

	if ($warnmessage) {
	    &Header::openbox('100%', 'LEFT', "$Lang::tr{'warning messages'}:");
	    print "<class name='base'>$warnmessage";
	    print "&nbsp;</class>";
	    &Header::closebox();
	}

	print "<form method='post' enctype='multipart/form-data'>";
	print "<input type='hidden' name='TYPE' value='host' />";

	if ($cgiparams{'KEY'}) {
	    print "<input type='hidden' name='KEY' value='$cgiparams{'KEY'}' />";
	    print "<input type='hidden' name='AUTH' value='$cgiparams{'AUTH'}' />";
	}

	&Header::openbox('100%', 'LEFT', "$Lang::tr{'connection'}:");
	print "<table width='100%'>\n";
	print "<tr><td width='25%' class='boldbase'>$Lang::tr{'name'}:</td>";
	    if ($cgiparams{'KEY'}) {
		print "<td width='35%' class='base'><input type='hidden' name='NAME' value='$cgiparams{'NAME'}' />$cgiparams{'NAME'}</td>\n";
	    } else {
		print "<td width='35%'><input type='text' name='NAME' value='$cgiparams{'NAME'}' maxlength='20' size='30' /></td>";
	    }
#	    print "<tr><td>$Lang::tr{'interface'}</td>";
#	    print "<td><select name='INTERFACE'>";
#	    print "<option value='RED' $selected{'INTERFACE'}{'RED'}>RED</option>";
#	    if ($netsettings{'BLUE_DEV'} ne '') {
#	    	print "<option value='BLUE' $selected{'INTERFACE'}{'BLUE'}>BLUE</option>";
#	    }
# 	    print "<option value='GREEN' $selected{'INTERFACE'}{'GREEN'}>GREEN</option>";
#	    print "<option value='ORANGE' $selected{'INTERFACE'}{'ORANGE'}>ORANGE</option>";
#	    print "</select></td></tr>";
#	    print <<END
	print "<tr><td class='boldbase'>$Lang::tr{'remark title'}&nbsp;<img src='/blob.gif' /></td>";
	print "<td colspan='3'><input type='text' name='REMARK' value='$cgiparams{'REMARK'}' size='55' maxlength='50' /></td></tr>";
	
#	if ($cgiparams{'TYPE'} eq 'net') {
	    print "<tr><td>$Lang::tr{'enabled'} <input type='checkbox' name='ENABLED' $checked{'ENABLED'}{'on'} /></td>\n";
	
#	    if ($cgiparams{'KEY'}) {
#		print "<td colspan='3'>&nbsp;</td></tr></table>";
#    	    } else {
#		print "<td colspan='3'><input type='checkbox' name='EDIT_ADVANCED' $checked{'EDIT_ADVANCED'}{'on'} /> $Lang::tr{'edit advanced settings when done'}</tr></table>";
#	    }
#	}else{
	    print "<td colspan='3'>&nbsp;</td></tr></table>";
#	}    
	    
	

	&Header::closebox();
	
	if ($cgiparams{'KEY'} && $cgiparams{'AUTH'} eq 'psk') {
	#    &Header::openbox('100%', 'LEFT', $Lang::tr{'authentication'});
	#    print <<END
	#    <table width='100%' cellpadding='0' cellspacing='5' border='0'>
	#    <tr><td class='base' width='50%'>$Lang::tr{'use a pre-shared key'}</td>
	#	<td class='base' width='50%'><input type='text' name='PSK' size='30' value='$cgiparams{'PSK'}' /></td></tr>
	#    </table>
END
	#    ;
	#    &Header::closebox();
	} elsif (! $cgiparams{'KEY'}) {
	    my $disabled='';
	    my $cakeydisabled='';
	    my $cacrtdisabled='';
	    if ( ! -f "${General::swroot}/ovpn/ca/cakey.pem" ) { $cakeydisabled = "disabled='disabled'" } else { $cakeydisabled = "" };
	    if ( ! -f "${General::swroot}/ovpn/ca/cacert.pem" ) { $cacrtdisabled = "disabled='disabled'" } else { $cacrtdisabled = "" };
	    &Header::openbox('100%', 'LEFT', $Lang::tr{'authentication'});
	    print <<END
	    <table width='100%' cellpadding='0' cellspacing='5' border='0'>
	    <tr><td colspan='3' bgcolor='#000000'><img src='/images/null.gif' width='1' height='1' border='0' /></td></tr>
	    <tr><td><input type='radio' name='AUTH' value='certreq' $checked{'AUTH'}{'certreq'} $cakeydisabled /></td>
		<td class='base'>$Lang::tr{'upload a certificate request'}</td>
		<td class='base' rowspan='2'><input type='file' name='FH' size='30' $cacrtdisabled></td></tr>
	    <tr><td><input type='radio' name='AUTH' value='certfile' $checked{'AUTH'}{'certfile'} $cacrtdisabled /></td>
		<td class='base'>$Lang::tr{'upload a certificate'}</td></tr>
	    <tr><td colspan='3' bgcolor='#000000'><img src='/images/null.gif' width='1' height='1' BORDER='0' /></td></tr>
	    <tr><td><input type='radio' name='AUTH' value='certgen' $checked{'AUTH'}{'certgen'} $cakeydisabled /></td>
		<td class='base'>$Lang::tr{'generate a certificate'}</td><td>&nbsp;</td></tr>
	    <tr><td>&nbsp;</td>
		<td class='base'>$Lang::tr{'users fullname or system hostname'}:</td>
		<td class='base' nowrap='nowrap'><input type='text' name='CERT_NAME' value='$cgiparams{'CERT_NAME'}' SIZE='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td>
		<td class='base'>$Lang::tr{'users email'}:&nbsp;<img src='/blob.gif' /></td>
		<td class='base' nowrap='nowrap'><input type='text' name='CERT_EMAIL' value='$cgiparams{'CERT_EMAIL'}' SIZE='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td>
		<td class='base'>$Lang::tr{'users department'}:&nbsp;<img src='/blob.gif' /></td>
		<td class='base' nowrap='nowrap'><input type='text' name='CERT_OU' value='$cgiparams{'CERT_OU'}' SIZE='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td>
		<td class='base'>$Lang::tr{'organization name'}:&nbsp;<img src='/blob.gif' /></td>
	        <td class='base' nowrap='nowrap'><input type='text' name='CERT_ORGANIZATION' value='$cgiparams{'CERT_ORGANIZATION'}' SIZE='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td>
		<td class='base'>$Lang::tr{'city'}:&nbsp;<img src='/blob.gif'></td>
		<td class='base' nowrap='nowrap'><input type='text' name='CERT_CITY' value='$cgiparams{'CERT_CITY'}' SIZE='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td>
		<td class='base'>$Lang::tr{'state or province'}:&nbsp;<img src='/blob.gif' /></td>
		<td class='base' nowrap='nowrap'><input type='text' name='CERT_STATE' value='$cgiparams{'CERT_STATE'}' SIZE='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td>
		<td class='base'>$Lang::tr{'country'}:</td>
		<td class='base'><select name='CERT_COUNTRY' $cakeydisabled>
END

	    ;
	    foreach my $country (sort keys %{Countries::countries}) {
		print "<option value='$Countries::countries{$country}'";
		if ( $Countries::countries{$country} eq $cgiparams{'CERT_COUNTRY'} ) {
		    print " selected='selected'";
		}
		print ">$country</option>";
	    }
	    print <<END
	    </select></td></tr>
	    <tr><td>&nbsp;</td>
		
		<td class='base'>$Lang::tr{'valid till'} (days):</td>
		<td class='base' nowrap='nowrap'><input type='text' name='DAYS_VALID' value='$cgiparams{'DAYS_VALID'}' size='32' $cakeydisabled /></td></tr>		
		
		<tr><td>&nbsp;</td>
		<td class='base'>$Lang::tr{'pkcs12 file password'}:</td>
		<td class='base' nowrap='nowrap'><input type='password' name='CERT_PASS1' value='$cgiparams{'CERT_PASS1'}' size='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td><td class='base'>$Lang::tr{'pkcs12 file password'}:<BR>($Lang::tr{'confirmation'})</td>
		<td class='base' nowrap='nowrap'><input type='password' name='CERT_PASS2' value='$cgiparams{'CERT_PASS2'}' size='32' $cakeydisabled /></td></tr>
	    </table>
END
	    ;
	    &Header::closebox();
	}

	print "<div align='center'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' />";
	if ($cgiparams{'KEY'}) {
#	    print "<input type='submit' name='ACTION' value='$Lang::tr{'advanced'}' />";
	}
	print "<input type='submit' name='ACTION' value='$Lang::tr{'cancel'}' /></div></form>";
	&Header::closebigbox();
	&Header::closepage();
	exit (0);
    }
    VPNCONF_END:
}

#    SETTINGS_ERROR:
###
### Default status page
###
    %cgiparams = ();
    %cahash = ();
    %confighash = ();
    &General::readhash("${General::swroot}/ovpn/settings", \%cgiparams);
    &General::readhasharray("${General::swroot}/ovpn/caconfig", \%cahash);
    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

    my @status = `/bin/cat /var/log/ovpnserver.log`;

    if ($cgiparams{'VPN_IP'} eq '' && -e "${General::swroot}/red/active") {
	if (open(IPADDR, "${General::swroot}/red/local-ipaddress")) {
	    my $ipaddr = <IPADDR>;
	    close IPADDR;
	    chomp ($ipaddr);
	    $cgiparams{'VPN_IP'} = (gethostbyaddr(pack("C4", split(/\./, $ipaddr)), 2))[0];
	    if ($cgiparams{'VPN_IP'} eq '') {
		$cgiparams{'VPN_IP'} = $ipaddr;
	    }
	}
    }
    
#default setzen
    if ($cgiparams{'DCIPHER'} eq '') {
	$cgiparams{'DCIPHER'} =  'BF-CBC';     
    }
#    if ($cgiparams{'DCOMPLZO'} eq '') {
#	$cgiparams{'DCOMPLZO'} =  'on';     
#    }
    if ($cgiparams{'DDEST_PORT'} eq '') {
	$cgiparams{'DDEST_PORT'} =  '1194';     
    }
    if ($cgiparams{'DMTU'} eq '') {
	$cgiparams{'DMTU'} =  '1400';     
    }
    if ($cgiparams{'DOVPN_SUBNET'} eq '') {
	$cgiparams{'DOVPN_SUBNET'} = '10.' . int(rand(256)) . '.' . int(rand(256)) . '.0/255.255.255.0';
    }

    $checked{'ENABLED'}{'off'} = '';
    $checked{'ENABLED'}{'on'} = '';
    $checked{'ENABLED'}{$cgiparams{'ENABLED'}} = 'CHECKED';
    $checked{'ENABLED_BLUE'}{'off'} = '';
    $checked{'ENABLED_BLUE'}{'on'} = '';
    $checked{'ENABLED_BLUE'}{$cgiparams{'ENABLED_BLUE'}} = 'CHECKED';
    $checked{'ENABLED_ORANGE'}{'off'} = '';
    $checked{'ENABLED_ORANGE'}{'on'} = '';
    $checked{'ENABLED_ORANGE'}{$cgiparams{'ENABLED_ORANGE'}} = 'CHECKED';
    

#new settings
    $selected{'DDEVICE'}{'tun'} = '';
    $selected{'DDEVICE'}{'tap'} = '';
    $selected{'DDEVICE'}{$cgiparams{'DDEVICE'}} = 'SELECTED';

    $selected{'DPROTOCOL'}{'udp'} = '';
    $selected{'DPROTOCOL'}{'tcp'} = '';
    $selected{'DPROTOCOL'}{$cgiparams{'DPROTOCOL'}} = 'SELECTED';
    
    $selected{'DCIPHER'}{'DES-CBC'} = '';
    $selected{'DCIPHER'}{'DES-EDE-CBC'} = '';
    $selected{'DCIPHER'}{'DES-EDE3-CBC'} = '';
    $selected{'DCIPHER'}{'DESX-CBC'} = '';
    $selected{'DCIPHER'}{'RC2-CBC'} = '';
    $selected{'DCIPHER'}{'RC2-40-CBC'} = '';
    $selected{'DCIPHER'}{'RC2-64-CBC'} = '';
    $selected{'DCIPHER'}{'BF-CBC'} = '';
    $selected{'DCIPHER'}{'CAST5-CBC'} = '';    
    $selected{'DCIPHER'}{'AES-128-CBC'} = '';
    $selected{'DCIPHER'}{'AES-192-CBC'} = '';
    $selected{'DCIPHER'}{'AES-256-CBC'} = '';
    $selected{'DCIPHER'}{$cgiparams{'DCIPHER'}} = 'SELECTED';
    $checked{'DCOMPLZO'}{'off'} = '';
    $checked{'DCOMPLZO'}{'on'} = '';
    $checked{'DCOMPLZO'}{$cgiparams{'DCOMPLZO'}} = 'CHECKED';

#new settings
    &Header::showhttpheaders();
    &Header::openpage($Lang::tr{'status ovpn'}, 1, '');
    &Header::openbigbox('100%', 'LEFT', '', $errormessage);

    if ($errormessage) {
	&Header::openbox('100%', 'LEFT', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
    }

    my $sactive = "<table cellpadding='2' cellspacing='0' bgcolor='${Header::colourred}' width='50%'><tr><td align='center'><b><font color='#FFFFFF'>$Lang::tr{'stopped'}</font></b></td></tr></table>";
    my $srunning = "no";
    my $activeonrun = "";
    if ( -e "/var/run/openvpn.pid"){
	$sactive = "<table cellpadding='2' cellspacing='0' bgcolor='${Header::colourgreen}' width='50%'><tr><td align='center'><b><font color='#FFFFFF'>$Lang::tr{'running'}</font></b></td></tr></table>";
	$srunning ="yes";
	$activeonrun = "";
    } else {
	$activeonrun = "disabled='disabled'";
    }	
    &Header::openbox('100%', 'LEFT', $Lang::tr{'global settings'});	
    print <<END	
    <table width='100%'>
    <form method='post'>
    <td width='25%'>&nbsp;</td>
    <td width='25%'>&nbsp;</td>
    <td width='25%'>&nbsp;</td></tr>
    <tr><td class='boldbase'>$Lang::tr{'ovpn server status'}</td>
    <td align='left'>$sactive</td>
    <tr><td class='boldbase'>$Lang::tr{'ovpn on red'}</td>
        <td><input type='checkbox' name='ENABLED' $checked{'ENABLED'}{'on'} /></td>
END
;
    if (&haveBlueNet()) {
	print "<tr><td class='boldbase'>$Lang::tr{'ovpn on blue'}</td>";
	print "<td><input type='checkbox' name='ENABLED_BLUE' $checked{'ENABLED_BLUE'}{'on'} /></td>";
    }
    if (&haveOrangeNet()) {    
	print "<tr><td class='boldbase'>$Lang::tr{'ovpn on orange'}</td>";
	print "<td><input type='checkbox' name='ENABLED_ORANGE' $checked{'ENABLED_ORANGE'}{'on'} /></td>";
    }	
    print <<END    	
    <tr><td class='base' nowrap='nowrap' colspan='2'>$Lang::tr{'local vpn hostname/ip'}:<br /><input type='text' name='VPN_IP' value='$cgiparams{'VPN_IP'}' size='30' /></td>
	<td class='boldbase' nowrap='nowrap' colspan='2'>$Lang::tr{'ovpn subnet'}<br /><input type='TEXT' name='DOVPN_SUBNET' value='$cgiparams{'DOVPN_SUBNET'}' size='30' /></td></tr>
    <tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'ovpn device'}</td>
        <td><select name='DDEVICE' ><option value='tun' $selected{'DDEVICE'}{'tun'}>TUN</option>
               			<!-- this is still not working
               			    <option value='tap' $selected{'DDEVICE'}{'tap'}>TAP</option></select>--> </td>				    
    <tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'protocol'}</td>
        <td><select name='DPROTOCOL'><option value='udp' $selected{'DPROTOCOL'}{'udp'}>UDP</option>
               			    <option value='tcp' $selected{'DPROTOCOL'}{'tcp'}>TCP</option></select></td>				    
        <td class='boldbase'>$Lang::tr{'destination port'}:</td>
        <td><input type='TEXT' name='DDEST_PORT' value='$cgiparams{'DDEST_PORT'}' size='5' /></td></tr>
    <tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'MTU'}&nbsp;</td>
        <td> <input type='TEXT' name='DMTU' VALUE='$cgiparams{'DMTU'}'size='5' /></TD>
    <tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'comp-lzo'}</td>
        <td><input type='checkbox' name='DCOMPLZO' $checked{'DCOMPLZO'}{'on'} /></td>
        <td class='boldbase' nowrap='nowrap'>$Lang::tr{'cipher'}</td>
        <td><select name='DCIPHER'><option value='DES-CBC' $selected{'DCIPHER'}{'DES-CBC'}>DES-CBC</option>
				   <option value='DES-EDE-CBC' $selected{'DCIPHER'}{'DES-EDE-CBC'}>DES-EDE-CBC</option>
				   <option value='DES-EDE3-CBC' $selected{'DCIPHER'}{'DES-EDE3-CBC'}>DES-EDE3-CBC</option>
				   <option value='DESX-CBC' $selected{'DCIPHER'}{'DESX-CBC'}>DESX-CBC</option>
				   <option value='RC2-CBC' $selected{'DCIPHER'}{'RC2-CBC'}>RC2-CBC</option>				  				    
				   <option value='RC2-40-CBC' $selected{'DCIPHER'}{'RC2-40-CBC'}>RC2-40-CBC</option>
				   <option value='RC2-64-CBC' $selected{'DCIPHER'}{'RC2-64-CBC'}>RC2-64-CBC</option>
				   <option value='BF-CBC' $selected{'DCIPHER'}{'BF-CBC'}>BF-CBC</option>
				   <option value='CAST5-CBC' $selected{'DCIPHER'}{'CAST5-CBC'}>CAST5-CBC</option>
				   <option value='AES-128-CBC' $selected{'DCIPHER'}{'AES-128-CBC'}>AES-128-CBC</option>
				   <option value='AES-192-CBC' $selected{'DCIPHER'}{'AES-192-CBC'}>AES-192-CBC</option>
				   <option value='AES-256-CBC' $selected{'DCIPHER'}{'AES-256-CBC'}>AES-256-CBC</option></select></td>
END
;				   
    
    if ( $srunning eq "yes" ) {
	print "<tr><td align='left'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' disabled='disabled' /></td>";
	print "<td><input type='submit' name='ACTION' value='$Lang::tr{'advanced server'}' disabled='disabled'/></td>";	
	print "<td><input type='submit' name='ACTION' value='$Lang::tr{'stop ovpn server'}' /></td>";
	print "<td><input type='submit' name='ACTION' value='$Lang::tr{'restart ovpn server'}' /></td></tr>";	
    } else{
	print "<tr><td align='left'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>";
	print "<td><input type='submit' name='ACTION' value='$Lang::tr{'advanced server'}' /></td>";
	if (( -e "${General::swroot}/ovpn/ca/cacert.pem" &&
	     -e "${General::swroot}/ovpn/ca/dh1024.pem" &&
	     -e "${General::swroot}/ovpn/certs/servercert.pem" &&
	     -e "${General::swroot}/ovpn/certs/serverkey.pem") &&
	    (( $cgiparams{'ENABLED'} eq 'on') || 
	    ( $cgiparams{'ENABLED_BLUE'} eq 'on') ||
	    ( $cgiparams{'ENABLED_ORANGE'} eq 'on'))){
	    print "<td><input type='submit' name='ACTION' value='$Lang::tr{'start ovpn server'}' /></td>";
	    print "<td><input type='submit' name='ACTION' value='$Lang::tr{'restart ovpn server'}' /></td></tr>";	
	} else {
	    print "<td><input type='submit' name='ACTION' value='$Lang::tr{'start ovpn server'}' disabled='disabled' /></td>";    
	    print "<td><input type='submit' name='ACTION' value='$Lang::tr{'restart ovpn server'}' disabled='disabled' /></td></tr>";		    
	}    
    }
    print "</form></table>";
    &Header::closebox();
    &Header::openbox('100%', 'LEFT', "$Lang::tr{'certificate authorities'}:");
    print <<EOF#'
    <table width='100%' border='0' cellspacing='1' cellpadding='0'>
    <tr>
	<td width='25%' class='boldbase' align='center'><b>$Lang::tr{'name'}</b></td>
	<td width='65%' class='boldbase' align='center'><b>$Lang::tr{'subject'}</b></td>
	<td width='10%' class='boldbase' colspan='3' align='center'><b>$Lang::tr{'action'}</b></td>
    </tr>
EOF
    ;
    if (-f "${General::swroot}/ovpn/ca/cacert.pem") {
	my $casubject = `/usr/bin/openssl x509 -text -in ${General::swroot}/ovpn/ca/cacert.pem`;
	$casubject    =~ /Subject: (.*)[\n]/;
	$casubject    = $1;
	$casubject    =~ s+/Email+, E+;
	$casubject    =~ s/ ST=/ S=/;

	print <<END
	<tr bgcolor='$color{'color22'}'>
	<td class='base'>$Lang::tr{'root certificate'}</td>
	<td class='base'>$casubject</td>
	<form method='post' name='frmrootcrta'><td width='3%' align='center'>
	    <input type='hidden' name='ACTION' value='$Lang::tr{'show root certificate'}' />
	    <input type='image' name='$Lang::tr{'edit'}' src='/images/info.gif' alt='$Lang::tr{'show root certificate'}' title='$Lang::tr{'show root certificate'}' width='20' height='20' border='0' />
	</td></form>
	<form method='post' name='frmrootcrtb'><td width='3%' align='center'>
	    <input type='image' name='$Lang::tr{'download root certificate'}' src='/images/media-floppy.png' alt='$Lang::tr{'download root certificate'}' title='$Lang::tr{'download root certificate'}' border='0' />
	    <input type='hidden' name='ACTION' value='$Lang::tr{'download root certificate'}' />
	</td></form>
	<td width='4%'>&nbsp;</td></tr>
END
	;
    } else {
	# display rootcert generation buttons
	print <<END
	<tr bgcolor='$color{'color22'}'>
	<td class='base'>$Lang::tr{'root certificate'}:</td>
	<td class='base'>$Lang::tr{'not present'}</td>
	<td colspan='3'>&nbsp;</td></tr>
END
	;
    }

    if (-f "${General::swroot}/ovpn/certs/servercert.pem") {
	my $hostsubject = `/usr/bin/openssl x509 -text -in ${General::swroot}/ovpn/certs/servercert.pem`;
	$hostsubject    =~ /Subject: (.*)[\n]/;
	$hostsubject    = $1;
	$hostsubject    =~ s+/Email+, E+;
	$hostsubject    =~ s/ ST=/ S=/;

	print <<END
	<tr bgcolor='$color{'color20'}'>
	<td class='base'>$Lang::tr{'host certificate'}</td>
	<td class='base'>$hostsubject</td>
	<form method='post' name='frmhostcrta'><td width='3%' align='center'>
	    <input type='hidden' name='ACTION' value='$Lang::tr{'show host certificate'}' />
	    <input type='image' name='$Lang::tr{'show host certificate'}' src='/images/info.gif' alt='$Lang::tr{'show host certificate'}' title='$Lang::tr{'show host certificate'}' width='20' height='20' border='0' />
	</td></form>
	<form method='post' name='frmhostcrtb'><td width='3%' align='center'>
	    <input type='image' name='$Lang::tr{'download host certificate'}' src='/images/media-floppy.png' alt='$Lang::tr{'download host certificate'}' title='$Lang::tr{'download host certificate'}' border='0' />
	    <input type='hidden' name='ACTION' value='$Lang::tr{'download host certificate'}' />
	</td></form>
	<td width='4%'>&nbsp;</td></tr>
END
	;
    } else {
	# Nothing
	print <<END
	<tr bgcolor='$color{'color20'}'>
	<td width='25%' class='base'>$Lang::tr{'host certificate'}:</td>
	<td class='base'>$Lang::tr{'not present'}</td>
	</td><td colspan='3'>&nbsp;</td></tr>
END
	;
    }

    if (! -f "${General::swroot}/ovpn/ca/cacert.pem") {
        print "<tr><td colspan='5' align='center'><form method='post'>";
	print "<input type='submit' name='ACTION' value='$Lang::tr{'generate root/host certificates'}' />";
        print "</form></td></tr>\n";
    }

    if (keys %cahash > 0) {
	foreach my $key (keys %cahash) {
	    if (($key + 1) % 2) {
		print "<tr bgcolor='$color{'color20'}'>\n";
	    } else {
		print "<tr bgcolor='$color{'color22'}'>\n";
	    }
	    print "<td class='base'>$cahash{$key}[0]</td>\n";
	    print "<td class='base'>$cahash{$key}[1]</td>\n";
	    print <<END
	    <form method='post' name='cafrm${key}a'><td align='center'>
		<input type='image' name='$Lang::tr{'show ca certificate'}' src='/images/info.gif' alt='$Lang::tr{'show ca certificate'}' title='$Lang::tr{'show ca certificate'}' border='0' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'show ca certificate'}' />
		<input type='hidden' name='KEY' value='$key' />
	    </td></form>
	    <form method='post' name='cafrm${key}b'><td align='center'>
		<input type='image' name='$Lang::tr{'download ca certificate'}' src='/images/media-floppy.png' alt='$Lang::tr{'download ca certificate'}' title='$Lang::tr{'download ca certificate'}' border='0' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'download ca certificate'}' />
		<input type='hidden' name='KEY' value='$key' />
	    </td></form>
	    <form method='post' name='cafrm${key}c'><td align='center'>
		<input type='hidden' name='ACTION' value='$Lang::tr{'remove ca certificate'}' />
		<input type='image'  name='$Lang::tr{'remove ca certificate'}' src='/images/delete.gif' alt='$Lang::tr{'remove ca certificate'}' title='$Lang::tr{'remove ca certificate'}' width='20' height='20' border='0' />
		<input type='hidden' name='KEY' value='$key' />
	    </td></form></tr>
END
	    ;
	}
    }

    print "</table>";

    # If the file contains entries, print Key to action icons
    if ( -f "${General::swroot}/ovpn/ca/cacert.pem") {
    print <<END
    <table>
    <tr>
	<td class='boldbase'>&nbsp; <b>$Lang::tr{'legend'}:</b></td>
	<td>&nbsp; &nbsp; <img src='/images/info.gif' alt='$Lang::tr{'show certificate'}' /></td>
	<td class='base'>$Lang::tr{'show certificate'}</td>
	<td>&nbsp; &nbsp; <img src='/images/media-floppy.png' alt='$Lang::tr{'download certificate'}' /></td>
	<td class='base'>$Lang::tr{'download certificate'}</td>
    </tr>
    </table>
END
    ;
    }
    print <<END
    <form method='post' enctype='multipart/form-data'>
    <table width='100%' border='0' cellspacing='1' cellpadding='0'>
    <tr><td class='base' nowrap='nowrap'>$Lang::tr{'ca name'}:</td>
    <td nowrap='nowrap'><input type='text' name='CA_NAME' value='$cgiparams{'CA_NAME'}' size='15' />
    <td nowrap='nowrap'><input type='file' name='FH' size='30' /></td>
    <td nowrap='nowrap'><input type='submit' name='ACTION' value='$Lang::tr{'upload ca certificate'}' /><br /><input type='submit' name='ACTION' value='$Lang::tr{'show crl'}' /></td>    
    </tr></table></form>
END
    ;

    &Header::closebox();
    if ( $srunning eq "yes" ) {    
	print "<div align='center'><form method='post'><input type='submit' name='ACTION' value='$Lang::tr{'reset'}' disabled='disabled' /></div></form>\n";    
    }else{
    	print "<div align='center'><form method='post'><input type='submit' name='ACTION' value='$Lang::tr{'reset'}' /></div></form>\n";
    }	    
    if ( -f "${General::swroot}/ovpn/ca/cacert.pem" ) {
    &Header::openbox('100%', 'LEFT', $Lang::tr{'Client status and controlc' });
    print <<END
    <table width='100%' border='0' cellspacing='1' cellpadding='0'>
<tr>
    <td width='10%' class='boldbase' align='center'><b>$Lang::tr{'name'}</b></td>
    <td width='15%' class='boldbase' align='center'><b>$Lang::tr{'type'}</b></td>
    <td width='18%' class='boldbase' align='center'><b>$Lang::tr{'common name'}</b></td>
    <td width='17%' class='boldbase' align='center'><b>$Lang::tr{'valid till'}</b></td>
    <td width='25%' class='boldbase' align='center'><b>$Lang::tr{'remark'}</b><br /><img src='/images/null.gif' width='125' height='1' border='0' alt='L2089' /></td>
    <td width='10%' class='boldbase' align='center'><b>$Lang::tr{'status'}</b></td>
    <td width='5%' class='boldbase' colspan='6' align='center'><b>$Lang::tr{'action'}</b></td>
</tr>
END
	;
        my $id = 0;
        my $gif;
        foreach my $key (keys %confighash) {
    	if ($confighash{$key}[0] eq 'on') { $gif = 'on.gif'; } else { $gif = 'off.gif'; }

	if ($id % 2) {
	    print "<tr bgcolor='$color{'color20'}'>\n";
	} else {
	    print "<tr bgcolor='$color{'color22'}'>\n";
	}
	print "<td align='center' nowrap='nowrap'>$confighash{$key}[1]</td>";
	print "<td align='center' nowrap='nowrap'>" . $Lang::tr{"$confighash{$key}[3]"} . " (" . $Lang::tr{"$confighash{$key}[4]"} . ")</td>";
	if ($confighash{$key}[4] eq 'cert') {
	    print "<td align='left' nowrap='nowrap'>$confighash{$key}[2]</td>";
	} else {
	    print "<td align='left'>&nbsp;</td>";
	}
	my $cavalid = `/usr/bin/openssl x509 -text -in ${General::swroot}/ovpn/certs/$confighash{$key}[1]cert.pem`;
	$cavalid    =~ /Not After : (.*)[\n]/;
	$cavalid    = $1;
	print "<td align='center'>$cavalid</td>";
	print "<td align='center'>$confighash{$key}[25]</td>";
	my $active = "<table cellpadding='2' cellspacing='0' bgcolor='${Header::colourred}' width='100%'><tr><td align='center'><b><font color='#FFFFFF'>$Lang::tr{'capsclosed'}</font></b></td></tr></table>";
	if ($confighash{$key}[0] eq 'off') {
	    $active = "<table cellpadding='2' cellspacing='0' bgcolor='${Header::colourblue}' width='100%'><tr><td align='center'><b><font color='#FFFFFF'>$Lang::tr{'capsclosed'}</font></b></td></tr></table>";
	} else {
	    my $cn;
    	    my @match = ();	
	    foreach my $line (@status) {
		chomp($line);
		if ( $line =~ /^(.+),(\d+\.\d+\.\d+\.\d+\:\d+),(\d+),(\d+),(.+)/) {
		    @match = split(m/^(.+),(\d+\.\d+\.\d+\.\d+\:\d+),(\d+),(\d+),(.+)/, $line);
		    if ($match[1] ne "Common Name") {
	    		$cn = $match[1];
		    }	    
	    	$cn =~ s/[_]/ /g;
		    if ($cn eq "$confighash{$key}[2]") {
			$active = "<table cellpadding='2' cellspacing='0' bgcolor='${Header::colourgreen}' width='100%'><tr><td align='center'><b><font color='#FFFFFF'>$Lang::tr{'capsopen'}</font></b></td></tr></table>";
		    }
		}    
	    }
	}
	my $disable_clientdl = "disabled='disabled'";
	if (( $cgiparams{'ENABLED'} eq 'on') || 
	    ( $cgiparams{'ENABLED_BLUE'} eq 'on') ||
	    ( $cgiparams{'ENABLED_ORANGE'} eq 'on')){
	    $disable_clientdl = "";
	}
	print <<END
	<td align='center'>$active</td>
		
	<form method='post' name='frm${key}a'><td align='center'>
	    <input type='image'  name='$Lang::tr{'dl client arch'}' $disable_clientdl src='/images/openvpn.png' alt='$Lang::tr{'dl client arch'}' title='$Lang::tr{'dl client arch'}' border='0' />
	    <input type='hidden' name='ACTION' value='$Lang::tr{'dl client arch'}' $disable_clientdl />
	    <input type='hidden' name='KEY' value='$key' $disable_clientdl />
	</td></form>
END
	;
	if ($confighash{$key}[4] eq 'cert') {
	    print <<END
	    <form method='post' name='frm${key}b'><td align='center'>
		<input type='image' name='$Lang::tr{'show certificate'}' src='/images/info.gif' alt='$Lang::tr{'show certificate'}' title='$Lang::tr{'show certificate'}' border='0' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'show certificate'}' />
		<input type='hidden' name='KEY' value='$key' />
	    </td></form>
END
	; } else {
	    print "<td>&nbsp;</td>";
	}
	if ($confighash{$key}[4] eq 'cert' && -f "${General::swroot}/ovpn/certs/$confighash{$key}[1].p12") { 
	    print <<END
	    <form method='post' name='frm${key}c'><td align='center'>
		<input type='image' name='$Lang::tr{'download pkcs12 file'}' src='/images/media-floppy.png' alt='$Lang::tr{'download pkcs12 file'}' title='$Lang::tr{'download pkcs12 file'}' border='0' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'download pkcs12 file'}' />
		<input type='hidden' name='KEY' value='$key' />
	    </td></form>
END
	; } elsif ($confighash{$key}[4] eq 'cert') {
	    print <<END
	    <form method='post' name='frm${key}c'><td align='center'>
		<input type='image' name='$Lang::tr{'download certificate'}' src='/images/media-floppy.png' alt='$Lang::tr{'download certificate'}' title='$Lang::tr{'download certificate'}' border='0' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'download certificate'}' />
		<input type='hidden' name='KEY' value='$key' />
	    </td></form>
END
	; } else {
	    print "<td>&nbsp;</td>";
	}
	print <<END
	<form method='post' name='frm${key}d'><td align='center'>
	    <input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif' alt='$Lang::tr{'toggle enable disable'}' title='$Lang::tr{'toggle enable disable'}' border='0' />
	    <input type='hidden' name='ACTION' value='$Lang::tr{'toggle enable disable'}' />
	    <input type='hidden' name='KEY' value='$key' />
	</td></form>

	<form method='post' name='frm${key}e'><td align='center'>
	    <input type='hidden' name='ACTION' value='$Lang::tr{'edit'}' />
	    <input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' width='20' height='20' border='0'/>
	    <input type='hidden' name='KEY' value='$key' />
	</td></form>
	<form method='post' name='frm${key}f'><td align='center'>
	    <input type='hidden' name='ACTION' value='$Lang::tr{'remove'}' />
	    <input type='image'  name='$Lang::tr{'remove'}' src='/images/delete.gif' alt='$Lang::tr{'remove'}' title='$Lang::tr{'remove'}' width='20' height='20' border='0' />
	    <input type='hidden' name='KEY' value='$key' />
	</td></form>
	</tr>
END
	;
	$id++;
    }
    ;

    # If the config file contains entries, print Key to action icons
    if ( $id ) {
    print <<END
    <table>
    <tr>
	<td class='boldbase'>&nbsp; <b>$Lang::tr{'legend'}:</b></td>
	<td>&nbsp; <img src='/images/on.gif' alt='$Lang::tr{'click to disable'}' /></td>
	<td class='base'>$Lang::tr{'click to disable'}</td>
	<td>&nbsp; &nbsp; <img src='/images/info.gif' alt='$Lang::tr{'show certificate'}' /></td>
	<td class='base'>$Lang::tr{'show certificate'}</td>
	<td>&nbsp; &nbsp; <img src='/images/edit.gif' alt='$Lang::tr{'edit'}' /></td>
	<td class='base'>$Lang::tr{'edit'}</td>
	<td>&nbsp; &nbsp; <img src='/images/delete.gif' alt='$Lang::tr{'remove'}' /></td>
	<td class='base'>$Lang::tr{'remove'}</td>
    </tr>
    <tr>
	<td>&nbsp; </td>
	<td>&nbsp; <img src='/images/off.gif' alt='?OFF' /></td>
	<td class='base'>$Lang::tr{'click to enable'}</td>
	<td> <img src='/images/media-floppy.png' alt='?FLOPPY' /></td>
	<td class='base'>$Lang::tr{'download certificate'}</td>
	<td> <img src='/images/openvpn.png' alt='?RELOAD'/></td>
	<td class='base'>$Lang::tr{'dl client arch'}</td>
    </tr>
    </table>
END
    ;
    }

    print <<END
    <table width='100%'>
    <form method='post'>
    <tr><td width='50%' ><input type='submit' name='ACTION' value='$Lang::tr{'add'}' /></td>
    	<td width='50%' ><input type='submit' name='ACTION' value='$Lang::tr{'ovpn con stat'}' $activeonrun /></td></tr>
    </form>
    </table>
END
    ;    
    &Header::closebox();
}
&Header::closepage();
