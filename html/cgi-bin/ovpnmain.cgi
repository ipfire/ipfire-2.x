#!/usr/bin/perl
# based on SmoothWall and IPCop CGIs
# 
# This code is distributed under the terms of the GPL
# Main idea from zeroconcept
# ZERNINA-VERSION:0.9.7a9
# (c) 2005 Ufuk Altinkaynak
#
# Ipcop and OpenVPN eas as one two three..
#

use CGI;
use CGI qw/:standard/;
use Net::DNS;
use File::Copy;
use File::Temp qw/ tempfile tempdir /;
use strict;
use Archive::Zip qw(:ERROR_CODES :CONSTANTS);
use Net::Ping;
require '/var/ipfire/general-functions.pl';
require '/home/httpd/cgi-bin/ovpnfunc.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "${General::swroot}/countries.pl";

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';
#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::colourgreen} );
undef (@dummy);



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
my $zerinaclient = '';
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
&Header::getcgihash(\%cgiparams, {'wantfile' => 1, 'filevar' => 'FH'});

# prepare openvpn config file
###
### Useful functions
###

###
### OpenVPN Server Control
###
if ($cgiparams{'ACTION'} eq $Lang::tr{'start ovpn server'} ||
    $cgiparams{'ACTION'} eq $Lang::tr{'stop ovpn server'} ||
    $cgiparams{'ACTION'} eq $Lang::tr{'restart ovpn server'}) {
	my $serveractive = `/bin/ps ax|grep server.conf|grep -v grep|awk \'{print \$1}\'`;
    #start openvpn server
    if ($cgiparams{'ACTION'} eq $Lang::tr{'start ovpn server'}){
    	&Ovpnfunc::emptyserverlog();
	system('/usr/local/bin/openvpnctrl', '-s');
    }   
    #stop openvpn server
    if ($cgiparams{'ACTION'} eq $Lang::tr{'stop ovpn server'}){
		if ($serveractive ne ''){
			system('/usr/local/bin/openvpnctrl', '-kn2n', $serveractive);
		}
    	system('/usr/local/bin/openvpnctrl', '-k');
		&Ovpnfunc::emptyserverlog();	
    }   
#    #restart openvpn server
    if ($cgiparams{'ACTION'} eq $Lang::tr{'restart ovpn server'}){
#workarund, till SIGHUP also works when running as nobody    
		if ($serveractive ne ''){
			system('/usr/local/bin/openvpnctrl', '-kn2n', $serveractive);
		}
		system('/usr/local/bin/openvpnctrl', '-k');    	
		&Ovpnfunc::emptyserverlog();
		system('/usr/local/bin/openvpnctrl', '-s');
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
	#additional push route
	$vpnsettings{'AD_ROUTE1'} = $cgiparams{'AD_ROUTE1'};
	$vpnsettings{'AD_ROUTE2'} = $cgiparams{'AD_ROUTE2'};
	$vpnsettings{'AD_ROUTE3'} = $cgiparams{'AD_ROUTE3'};
	#additional push route
	
    #################################################################################
    #  Added by Philipp Jenni                                                       #
    #                                                                               #
    #  Contact: philipp.jenni-at-gmx.ch                                             #
    #  Date:    2006-04-22                                                          #
    #  Description:  Add the FAST-IO Parameter from OpenVPN to the Zerina Config    #
    #                Add the NICE Parameter from OpenVPN to the Zerina Config       #
    #                Add the MTU-DISC Parameter from OpenVPN to the Zerina Config   #
    #                Add the MSSFIX Parameter from OpenVPN to the Zerina Config     #
    #                Add the FRAMGMENT Parameter from OpenVPN to the Zerina Config  #
    #################################################################################
    $vpnsettings{'EXTENDED_FASTIO'} = $cgiparams{'EXTENDED_FASTIO'};
    $vpnsettings{'EXTENDED_NICE'} = $cgiparams{'EXTENDED_NICE'};
    $vpnsettings{'EXTENDED_MTUDISC'} = $cgiparams{'EXTENDED_MTUDISC'};
    $vpnsettings{'EXTENDED_MSSFIX'} = $cgiparams{'EXTENDED_MSSFIX'};
    $vpnsettings{'EXTENDED_FRAGMENT'} = $cgiparams{'EXTENDED_FRAGMENT'};
    #################################################################################
    #  End of Inserted Data                                                         #
    #################################################################################

    
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
	if ($cgiparams{'AD_ROUTE1'} ne ''){
		if (! &General::validipandmask($cgiparams{'AD_ROUTE1'})) {
			$errormessage = $Lang::tr{'route subnet is invalid'};
			goto ADV_ERROR;
		}
	}
	if ($cgiparams{'AD_ROUTE2'} ne ''){
		if (! &General::validipandmask($cgiparams{'AD_ROUTE2'})) {
			$errormessage = $Lang::tr{'route subnet is invalid'};
			goto ADV_ERROR;
		}
	}	
	if ($cgiparams{'AD_ROUTE3'} ne ''){
		if (! &General::validipandmask($cgiparams{'AD_ROUTE3'})) {
			$errormessage = $Lang::tr{'route subnet is invalid'};
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
    &Ovpnfunc::writeserverconf();#hier ok
}

###
### Save main settings
###
if ($cgiparams{'ACTION'} eq $Lang::tr{'save'} && $cgiparams{'TYPE'} eq '' && $cgiparams{'KEY'} eq '') {
    &General::readhash("${General::swroot}/ovpn/settings", \%vpnsettings);
	&General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
    #DAN do we really need (to to check) this value? Besides if we listen on blue and orange too,
    #DAN this value has to leave.
    if ($cgiparams{'ENABLED'} eq 'on'){
    	unless (&General::validfqdn($cgiparams{'VPN_IP'}) || &General::validip($cgiparams{'VPN_IP'})) {
		$errormessage = $Lang::tr{'invalid input for hostname'};
		goto SETTINGS_ERROR;
    	}
    }
    if ($cgiparams{'ENABLED'} eq 'on'){
		$errormessage = &Ovpnfunc::disallowreserved($cgiparams{'DDEST_PORT'},0,$cgiparams{'DPROTOCOL'},"dest");
    }	
    if ($errormessage) { goto SETTINGS_ERROR; }
    
    
    if ($cgiparams{'ENABLED'} eq 'on'){
		$errormessage = &Ovpnfunc::checkportfw(0,$cgiparams{'DDEST_PORT'},$cgiparams{'DPROTOCOL'},'0.0.0.0');
    }
    	
    if ($errormessage) { goto SETTINGS_ERROR; }
    
    if (! &General::validipandmask($cgiparams{'DOVPN_SUBNET'})) {
		$errormessage = $Lang::tr{'ovpn subnet is invalid'};
		goto SETTINGS_ERROR;
    }
    my @tmpovpnsubnet = split("\/",$cgiparams{'DOVPN_SUBNET'});	
    $tmpovpnsubnet[1]  = &Ovpnfunc::cidrormask($tmpovpnsubnet[1]);
	$cgiparams{'DOVPN_SUBNET'} = "$tmpovpnsubnet[0]/$tmpovpnsubnet[1]";#convert from cidr
	#plausi1
	$errormessage = &Ovpnfunc::ovelapplausi($tmpovpnsubnet[0],$tmpovpnsubnet[1]);
	#plausi1
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
	#hhh
	foreach my $dkey (keys %confighash) {#Check if there is no other entry with this name	
		if ($confighash{$dkey}[14] eq $cgiparams{'DPROTOCOL'} &&  $confighash{$dkey}[15] eq $cgiparams{'DDEST_PORT'}){			
			$errormessage = "Choosed Protocol/Port combination is already used by connection: $confighash{$dkey}[1]";
			goto SETTINGS_ERROR;			
		}		
	}
	#hhh
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
#new settings for daemon    
    &General::writehash("${General::swroot}/ovpn/settings", \%vpnsettings);
    &Ovpnfunc::writeserverconf();#hier ok
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
    &Ovpnfunc::cleanssldatabase();
    if (open(FILE, ">${General::swroot}/ovpn/caconfig")) {
        print FILE "";
        close FILE;
    }
    &General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
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
    UPLOADCA_ERROR:

###
### Display ca certificate
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'show ca certificate'}) {
	&Ovpnfunc::displayca($cgiparams{'KEY'});
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
		unlink ("${General::swroot}/ovpn//certs/$confighash{$key}[1]cert.pem");
		unlink ("${General::swroot}/ovpn/certs/$confighash{$key}[1].p12");
		delete $confighash{$key};
		&General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
	    }
	}
	unlink ("${General::swroot}/ovpn/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem");
	delete $cahash{$cgiparams{'KEY'}};
	&General::writehasharray("${General::swroot}/ovpn/caconfig", \%cahash);
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
}elsif ($cgiparams{'ACTION'} eq $Lang::tr{'show root certificate'} || $cgiparams{'ACTION'} eq $Lang::tr{'show host certificate'}) {
	&Ovpnfunc::displayroothost($cgiparams{'ACTION'});
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
	    &Ovpnfunc::newcleanssldatabase();
	    goto ROOTCERT_ERROR;
	} else {
	    unlink ("${General::swroot}/ovpn/certs/serverreq.pem");
	    &Ovpnfunc::deletebackupcert();
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
	    &Ovpnfunc::cleanssldatabase();
	    goto ROOTCERT_ERROR;
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
	    &Ovpnfunc::cleanssldatabase();
	    goto ROOTCERT_ERROR;
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

###
### Enable/Disable connection
###
}elsif ($cgiparams{'ACTION'} eq $Lang::tr{'toggle enable disable'}) {
    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
    if ($confighash{$cgiparams{'KEY'}}) {
		my $n2nactive = `/bin/ps ax|grep $confighash{$cgiparams{'KEY'}}[1].conf|grep -v grep|awk \'{print \$1}\'`;
		if ($confighash{$cgiparams{'KEY'}}[0] eq 'off') {
			$confighash{$cgiparams{'KEY'}}[0] = 'on';
			&General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
			if ($n2nactive eq ''){
				system('/usr/local/bin/openvpnctrl', '-sn2n', $confighash{$cgiparams{'KEY'}}[1]);
			} else {
				system('/usr/local/bin/openvpnctrl', '-kn2n', $n2nactive);
				system('/usr/local/bin/openvpnctrl', '-sn2n', $confighash{$cgiparams{'KEY'}}[1]);
			}			
		} else {
			$confighash{$cgiparams{'KEY'}}[0] = 'off';
			&General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
			if ($n2nactive ne ''){				
				system('/usr/local/bin/openvpnctrl', '-kn2n', $n2nactive);
			}						
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
	my $uhost3 = '';
	my $uhost = `/bin/uname -n`;
	if ($uhost ne '') {
		my @uhost2 = split /\./, $uhost;
		$uhost3 = $uhost2[0];
	} else {
		$uhost3 = "IPFire";
	}	
    my $tempdir = tempdir( CLEANUP => 1 );
    my $zippath = "$tempdir/";
    my $zipname = "$confighash{$cgiparams{'KEY'}}[1]-TO-$uhost3.zip";
    my $zippathname = "$zippath$zipname";
    #anna
    if ($confighash{$cgiparams{'KEY'}}[3] eq 'net'){
		$zerinaclient = 'true';
		&Ovpnfunc::writenet2netconf($cgiparams{'KEY'},$zerinaclient);
		exit(0);
	}
    $clientovpn = "$confighash{$cgiparams{'KEY'}}[1]-TO-$uhost3.ovpn";
    open(CLIENTCONF, ">$tempdir/$clientovpn") or die "Unable to open tempfile: $clientovpn $!";
    flock CLIENTCONF, 2;
    
    my $zip = Archive::Zip->new();
    
    print CLIENTCONF "#OpenVPN Client conf\r\n";
    print CLIENTCONF "tls-client\r\n";
    print CLIENTCONF "client\r\n";
    print CLIENTCONF "dev $vpnsettings{'DDEVICE'}\r\n";
	if ($vpnsettings{'DPROTOCOL'} eq 'tcp') {
		print CLIENTCONF "proto $vpnsettings{'DPROTOCOL'}-client\r\n";
	} else {	
		print CLIENTCONF "proto $vpnsettings{'DPROTOCOL'}\r\n";
	}	
    print CLIENTCONF "$vpnsettings{'DDEVICE'}-mtu $vpnsettings{'DMTU'}\r\n";
    if ( $vpnsettings{'ENABLED'} eq 'on'){
    	print CLIENTCONF "remote $vpnsettings{'VPN_IP'} $vpnsettings{'DDEST_PORT'}\r\n";
		if ( $vpnsettings{'ENABLED_BLUE'} eq 'on' && (&Ovpnfunc::haveBlueNet())){	
			print CLIENTCONF "#Coment the above line and uncoment the next line, if you want to connect on the Blue interface\r\n";	
			print CLIENTCONF ";remote $netsettings{'BLUE_ADDRESS'} $vpnsettings{'DDEST_PORT'}\r\n";
		}
		if ( $vpnsettings{'ENABLED_ORANGE'} eq 'on' && (&Ovpnfunc::haveOrangeNet())){
			print CLIENTCONF "#Coment the above line and uncoment the next line, if you want to connect on the Orange interface\r\n";		
			print CLIENTCONF ";remote $netsettings{'ORANGE_ADDRESS'} $vpnsettings{'DDEST_PORT'}\r\n";
		}
    } elsif ( $vpnsettings{'ENABLED_BLUE'} eq 'on' && (&Ovpnfunc::haveBlueNet())){
		print CLIENTCONF "remote $netsettings{'BLUE_ADDRESS'} $vpnsettings{'DDEST_PORT'}\r\n";
		if ( $vpnsettings{'ENABLED_ORANGE'} eq 'on' && (&Ovpnfunc::haveOrangeNet())){
			print CLIENTCONF "#Coment the above line and uncoment the next line, if you want to connect on the Orange interface\r\n";		
			print CLIENTCONF ";remote $netsettings{'ORANGE_ADDRESS'} $vpnsettings{'DDEST_PORT'}\r\n";
		}
    } elsif ( $vpnsettings{'ENABLED_ORANGE'} eq 'on' && (&Ovpnfunc::haveOrangeNet())){
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
		if ($confighash{$cgiparams{'KEY'}}[19] eq 'yes') {			
			&Ovpnfunc::killconnection($cgiparams{'KEY'});
			&Ovpnfunc::removenet2netconf($cgiparams{'KEY'});
			delete $confighash{$cgiparams{'KEY'}};
			&General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);		
		} else {
			my $temp = `/usr/bin/openssl ca -revoke ${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem -config ${General::swroot}/ovpn/openssl/ovpn.cnf`;
			unlink ("${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem");
			unlink ("${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1].p12");
			&Ovpnfunc::killconnection($cgiparams{'KEY'});
			&Ovpnfunc::removenet2netconf($cgiparams{'KEY'});
			delete $confighash{$cgiparams{'KEY'}};
			my $temp2 = `/usr/bin/openssl ca -gencrl -out ${General::swroot}/ovpn/crls/cacrl.pem -config ${General::swroot}/ovpn/openssl/ovpn.cnf`;
			&General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
		}	
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
	if ($cgiparams{'EXTENDED_NICE'} eq '') {
		$cgiparams{'EXTENDED_NICE'} =  '0';     
    }	
    $checked{'CLIENT2CLIENT'}{'off'} = '';
    $checked{'CLIENT2CLIENT'}{'on'} = '';
    $checked{'CLIENT2CLIENT'}{$cgiparams{'CLIENT2CLIENT'}} = 'CHECKED';
    $checked{'REDIRECT_GW_DEF1'}{'off'} = '';
    $checked{'REDIRECT_GW_DEF1'}{'on'} = '';
    $checked{'REDIRECT_GW_DEF1'}{$cgiparams{'REDIRECT_GW_DEF1'}} = 'CHECKED';
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

    #################################################################################
    #  Added by Philipp Jenni                                                       #
    #                                                                               #
    #  Contact: philipp.jenni-at-gmx.ch                                             #
    #  Date:    2006-04-22                                                          #
    #  Description:  Definitions to set the FASTIO Checkbox                         #
    #                Definitions to set the MTUDISC Checkbox                        #
    #                Definitions to set the NICE Selectionbox                       #
    #################################################################################
    $checked{'EXTENDED_FASTIO'}{'off'} = '';
    $checked{'EXTENDED_FASTIO'}{'on'} = '';
    $checked{'EXTENDED_FASTIO'}{$cgiparams{'EXTENDED_FASTIO'}} = 'CHECKED';
    $checked{'EXTENDED_MTUDISC'}{'off'} = '';
    $checked{'EXTENDED_MTUDISC'}{'on'} = '';
    $checked{'EXTENDED_MTUDISC'}{$cgiparams{'EXTENDED_MTUDISC'}} = 'CHECKED';
    $selected{'EXTENDED_NICE'}{'-13'} = '';
    $selected{'EXTENDED_NICE'}{'-10'} = '';
    $selected{'EXTENDED_NICE'}{'-7'} = '';
    $selected{'EXTENDED_NICE'}{'-3'} = '';
    $selected{'EXTENDED_NICE'}{'0'} = '';
    $selected{'EXTENDED_NICE'}{'3'} = '';
    $selected{'EXTENDED_NICE'}{'7'} = '';
    $selected{'EXTENDED_NICE'}{'10'} = '';
    $selected{'EXTENDED_NICE'}{'13'} = '';
    $selected{'EXTENDED_NICE'}{$cgiparams{'EXTENDED_NICE'}} = 'SELECTED';
    #################################################################################
    #  End of inserted Data                                                         #
    #################################################################################
    
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
<!-- Additional push route START-->
    <table width='100%'>
    <tr>
	<td colspan='4'><b>$Lang::tr{'add-route'}</b></td>
    </tr>
    <tr>
	<td width='25%'></td> <td width='20%'> </td><td width='25%'> </td><td width='30%'></td>
    </tr>	
    <tr>		
	<td class='base'>$Lang::tr{'subnet'} 1</td>
        <td><input type='TEXT' name='AD_ROUTE1' value='$cgiparams{'AD_ROUTE1'}' size='30' /></td>
    </tr>
    <tr>	
	<td class='base'>$Lang::tr{'subnet'} 2</td>
	<td><input type='TEXT' name='AD_ROUTE2' value='$cgiparams{'AD_ROUTE2'}' size='30' /></td>
    </tr>	
    <tr>	
	<td class='base'>$Lang::tr{'subnet'} 3</td>
	<td><input type='TEXT' name='AD_ROUTE3' value='$cgiparams{'AD_ROUTE3'}' size='30' /></td>
    </tr>
</table>
<hr size='1'>
<!-- Additional push route END-->
    <table width='100%'>
    <tr>
	<td class'base'><b>$Lang::tr{'misc-options'}</b></td>
    </tr>
    <tr>
	<td width='25%'></td> <td width='20%'> </td><td width='25%'> </td><td width='30%'></td>
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
        <td><input type='text' name='MAX_CLIENTS' value='$cgiparams{'MAX_CLIENTS'}' size='30' /></td>
    </tr>	
     	<td class='base'>Keppalive (ping/ping-restart)</td>	
	<td><input type='TEXT' name='KEEPALIVE_1' value='$cgiparams{'KEEPALIVE_1'}' size='30' /></td>
	<td><input type='TEXT' name='KEEPALIVE_2' value='$cgiparams{'KEEPALIVE_2'}' size='30' /></td>
    </tr>	

<!--			    
    #################################################################################
    #  Added by Philipp Jenni                                                       #
    #                                                                               #
    #  Contact: philipp.jenni-at-gmx.ch                                             #
    #  Date:    2006-04-22                                                          #
    #  Description:  Add the FAST-IO Checkbox to the HTML Form                      #
    #                Add the NICE Selectionbox to the HTML Form                     #
    #                Add the MTU-DISC Checkbox to the HTML Form                     #
    #                Add the MSSFIX Textbox to the HTML Form                        #
    #                Add the FRAMGMENT Textbox to the HTML Form                     #
    #  Updates:                                                                     #
    #  2006-04-27    Include Multilanguage-Support                                  #
    #################################################################################
-->
    </tr>
    <tr>
      <td class='base'>$Lang::tr{'ovpn_processprio'}</td>        
      <td>
        <select name='EXTENDED_NICE'>
				  <option value='-13' $selected{'EXTENDED_NICE'}{'-13'}>$Lang::tr{'ovpn_processprioEH'}</option>
				  <option value='-10' $selected{'EXTENDED_NICE'}{'-10'}>$Lang::tr{'ovpn_processprioVH'}</option>
				  <option value='-7'  $selected{'EXTENDED_NICE'}{'-7'}>$Lang::tr{'ovpn_processprioH'}</option>
				  <option value='-3'  $selected{'EXTENDED_NICE'}{'-3'}>$Lang::tr{'ovpn_processprioEN'}</option>
				  <option value='0'  $selected{'EXTENDED_NICE'}{'0'}>$Lang::tr{'ovpn_processprioN'}</option>
				  <option value='3'  $selected{'EXTENDED_NICE'}{'3'}>$Lang::tr{'ovpn_processprioLN'}</option>
				  <option value='7'  $selected{'EXTENDED_NICE'}{'7'}>$Lang::tr{'ovpn_processprioD'}</option>
				  <option value='10' $selected{'EXTENDED_NICE'}{'10'}>$Lang::tr{'ovpn_processprioVD'}</option>
				  <option value='13' $selected{'EXTENDED_NICE'}{'13'}>$Lang::tr{'ovpn_processprioED'}</option>
				</select>
		  </td>
		</tr>
    <tr>
      <td class='base'>$Lang::tr{'ovpn_fastio'}</td>        
      <td>
        <input type='checkbox' name='EXTENDED_FASTIO' $checked{'EXTENDED_FASTIO'}{'on'} />
		  </td>
		</tr>
    <tr>
      <td class='base'>$Lang::tr{'ovpn_mtudisc'}</td>        
      <td>
        <input type='checkbox' name='EXTENDED_MTUDISC' $checked{'EXTENDED_MTUDISC'}{'on'} />
		  </td>
		</tr>  
    <tr>
      <td class='base'>$Lang::tr{'ovpn_mssfix'}</td>        
      <td>
        <input type='TEXT' name='EXTENDED_MSSFIX' value='$cgiparams{'EXTENDED_MSSFIX'}' size='30'/>
		  </td>
		</tr>  
    <tr>
      <td class='base'>$Lang::tr{'ovpn_fragment'}</td>        
      <td>
        <input type='TEXT' name='EXTENDED_FRAGMENT' value='$cgiparams{'EXTENDED_FRAGMENT'}' size='30'/>
		  </td>
		</tr>  

<!--
    #################################################################################
    #  End of Inserted Data                                                         #
    #################################################################################
-->
			
    
</table>
<hr size='1'>
    <table width='100%'>
    <tr>
	<td class'base'><b>$Lang::tr{'log-options'}</b></td>
    </tr>
    <tr>
	<td width='25%'></td> <td width='20%'> </td><td width='25%'> </td><td width='30%'></td>
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
<!--			    
    #################################################################################
    #  Added by Philipp Jenni                                                       #
    #                                                                               #
    #  Contact: philipp.jenni-at-gmx.ch                                             #
    #  Date:    2006-04-22                                                          #
    #  Description:  Required </TR> Command from this Table                         #
    #################################################################################
-->
    </tr>				    
<!--
    #################################################################################
    #  End of Inserted Data                                                         #
    #################################################################################
-->
	    
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
	    if ( $line =~ /^(.+),(\d+\.\d+\.\d+\.\d+\:\d+),(\d+),(\d+),(.+)/) {
		@match = split(m/^(.+),(\d+\.\d+\.\d+\.\d+\:\d+),(\d+),(\d+),(.+)/, $line);
		if ($match[1] ne "Common Name") {
	    	    $cn = $match[1];
		    $userlookup{$match[2]} = $uid;
		    $users[$uid]{'CommonName'} = $match[1];
		    $users[$uid]{'RealAddress'} = $match[2];
		    $users[$uid]{'BytesReceived'} = &Ovpnfunc::sizeformat($match[3]);
		    $users[$uid]{'BytesSent'} = &Ovpnfunc::sizeformat($match[4]);
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
		    			print "<tr bgcolor='${Header::table1colour}'>\n";
	    			} else {
		    			print "<tr bgcolor='${Header::table2colour}'>\n";
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
### Restart connection
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'restart'}) {
    &General::readhash("${General::swroot}/ovpn/settings", \%vpnsettings);
    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

    if ($confighash{$cgiparams{'KEY'}}) {
    } else {
		$errormessage = $Lang::tr{'invalid key'};
    }

###
### Choose between adding a host-net or net-net connection
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'add'} && $cgiparams{'TYPE'} eq '') {
	&General::readhash("${General::swroot}/ovpn/settings", \%vpnsettings);
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'vpn configuration main'}, 1, '');
	&Header::openbigbox('100%', 'LEFT', '', '');
	&Header::openbox('100%', 'LEFT', "Net to Net $Lang::tr{'connection type'}");
	print <<END
	    <b>$Lang::tr{'connection type'}:</b><br />
	    <table><form method='post' enctype='multipart/form-data'>		
	    <tr><td><input type='radio' name='TYPE' value='net' checked /></td>
		<td class='base'>$Lang::tr{'net to net vpn'}</td></tr>
		<tr><td><input type='radio' name='TYPE' value='zerinan2n' /></td>		
			<td class='base'>upload a ZERINA Net-to-Net package</td>
		<td class='base'><input type='file' name='FH' size='30'></td></tr>		
	    <tr><td align='center'><input type='submit' name='ACTION' value='$Lang::tr{'add'}' /></td></tr>
	    </form></table>
END
	;
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit (0);
	
###
### uploading a ZERINA n2n connection package
###
}  elsif (($cgiparams{'ACTION'} eq $Lang::tr{'add'}) && ($cgiparams{'TYPE'} eq 'zerinan2n')){
	my @zerinaconf;
	my @confdetails;
	my $uplconffilename ='';
	my $uplp12name = '';
	my $complzoactive ='';
	my @rem_subnet;
	my @rem_subnet2;
	my @tmposupnet3;	
	my $key;
	&General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);	
# Move uploaded ZERINA n2n package to a temporary file
	if (ref ($cgiparams{'FH'}) ne 'Fh') {
		$errormessage = $Lang::tr{'there was no file upload'};
		goto ZERINA_ERROR;
    }
    # Move uploaded ca to a temporary file
    (my $fh, my $filename) = tempfile( );
    if (copy ($cgiparams{'FH'}, $fh) != 1) {
		$errormessage = $!;
		goto ZERINA_ERROR;
    }

	my $zip = Archive::Zip->new();
	my $zipName = $filename;
	my $status = $zip->read( $zipName );
	if ($status != AZ_OK) {   
		$errormessage = "Read of $zipName failed\n";
		goto ZERINA_ERROR;
	}
	#my $tempdir = tempdir( CLEANUP => 1 );
	my $tempdir = tempdir();
	my @files = $zip->memberNames();
	for(@files) {
	$zip->extractMemberWithoutPaths($_,"$tempdir/$_");
	}
	my $countfiles = @files;
	# see if we have 2 files
	if ( $countfiles == 2){
		foreach (@files){
			if ( $_ =~ /.conf$/){
				$uplconffilename = $_;
			}
			if ( $_ =~ /.p12$/){
				$uplp12name = $_;
			}			
		}
		if (($uplconffilename eq '') || ($uplp12name eq '')){
			$errormessage = "Either no *.conf or no *.p12 file found\n";
			goto ZERINA_ERROR;
		}
		open(FILE, "$tempdir/$uplconffilename") or die 'Unable to open*.conf file';
		@zerinaconf = <FILE>;
		close (FILE);
		chomp(@zerinaconf);
	} else {
	# only 2 files are allowed
		$errormessage = "Filecount does not match only 2 files are allowed\n";
		goto ZERINA_ERROR;
	}
	#prepare imported data not elegant, will be changed later
	my $ufuk = (@zerinaconf);
	push(@confdetails, substr($zerinaconf[0],4));#dev tun 0
	push(@confdetails, substr($zerinaconf[1],8));#mtu value 1
	push(@confdetails, substr($zerinaconf[2],6));#protocol 2
	if ($confdetails[2] eq 'tcp-client' || $confdetails[2] eq 'tcp-server') {
		$confdetails[2] = 'tcp';
	}	
	push(@confdetails, substr($zerinaconf[3],5));#port 3
	push(@confdetails, substr($zerinaconf[4],9));#ovpn subnet 4
	push(@confdetails, substr($zerinaconf[5],7));#remote ip 5
	push(@confdetails, $zerinaconf[6]);	#tls-server/tls-client 6
	push(@confdetails, substr($zerinaconf[7],7));#pkcs12	name 7	
	push(@confdetails, substr($zerinaconf[$ufuk-1],1));#remote subnet	 8
	push(@confdetails, substr($zerinaconf[9],10));#keepalive 9
	push(@confdetails, substr($zerinaconf[10],7));#cipher 10	
	if ($ufuk == 14) {
		push(@confdetails, $zerinaconf[$ufuk-3]);#complzo	 11	
		$complzoactive = "on";
	} else {
		$complzoactive = "off";
	}	
	push(@confdetails, substr($zerinaconf[$ufuk-2],5));#verb 12
	push(@confdetails, substr($zerinaconf[8],6));#localsubnet 13
	#push(@confdetails, substr($uplconffilename,0,-5));#connection Name 14
	push(@confdetails, substr($uplp12name,0,-4));#connection Name 14
	#chomp(@confdetails);	
	foreach my $dkey (keys %confighash) {#Check if there is no other entry with this name
		if ($confighash{$dkey}[1] eq $confdetails[$ufuk]) {
			$errormessage = $Lang::tr{'a connection with this name already exists'};
			goto ZERINA_ERROR;			
		}
	}
	if ($confdetails[$ufuk] eq 'server') {
			$errormessage = $Lang::tr{'server reserved'};
			goto ZERINA_ERROR;			
	}
	@rem_subnet2 = split(/ /,$confdetails[4]);
	@tmposupnet3 = split /\./,$rem_subnet2[0];
	$errormessage = &Ovpnfunc::ovelapplausi("$tmposupnet3[0].$tmposupnet3[1].$tmposupnet3[2].0","255.255.255.0");
	if ($errormessage ne ''){
		goto ZERINA_ERROR;
	}
	
	$key = &General::findhasharraykey (\%confighash);
	foreach my $i (0 .. 42) { $confighash{$key}[$i] = "";}
	$confighash{$key}[0] = 'off';
	$confighash{$key}[1] = $confdetails[$ufuk];
	#$confighash{$key}[2] = $confdetails[7];	
	$confighash{$key}[2] = $confdetails[$ufuk];
	$confighash{$key}[3] = 'net';
	$confighash{$key}[4] = 'cert';	
	$confighash{$key}[6] = 'client';		
	$confighash{$key}[8] = $confdetails[8];		
	@rem_subnet = split(/ /,$confdetails[$ufuk-1]);
	$confighash{$key}[11] = "$rem_subnet[0]/$rem_subnet[1]";
	$confighash{$key}[10] = $confdetails[5];
	$confighash{$key}[25] = 'imported';
	$confighash{$key}[12] = 'red';
	my @tmposupnet = split(/ /,$confdetails[4]);
	my @tmposupnet2 = split /\./,$tmposupnet[0];
	$confighash{$key}[13] = "$tmposupnet2[0].$tmposupnet2[1].$tmposupnet2[2].0/255.255.255.0";
	$confighash{$key}[14] = $confdetails[2];
	$confighash{$key}[15] = $confdetails[3];
	$confighash{$key}[16] = $complzoactive;
	$confighash{$key}[17] = $confdetails[1];
	$confighash{$key}[18] = '';# nn2nvpn_ip
	$confighash{$key}[19] = 'yes';# nn2nvpn_ip
	$confighash{$key}[20] = $confdetails[10];
	$cgiparams{'KEY'} = $key;
	&General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
	mkdir("${General::swroot}/ovpn/n2nconf/$confdetails[$ufuk]", 0770);
	move("$tempdir/$uplconffilename", "${General::swroot}/ovpn/n2nconf/$confdetails[$ufuk]/$uplconffilename");
	if ($? ne 0) {
	    $errormessage = "*.conf move failed: $!";
	    unlink ($filename);
	    goto ZERINA_ERROR;
	}
	move("$tempdir/$uplp12name", "${General::swroot}/ovpn/n2nconf/$confdetails[$ufuk]/$uplp12name");
	if ($? ne 0) {
	    $errormessage = "$Lang::tr{'certificate file move failed'}: $!";
	    unlink ($filename);
	    goto ZERINA_ERROR;
	}	
	ZERINA_ERROR:
		
	&Header::showhttpheaders();
	&Header::openpage('Validate imported configuration', 1, '');
	&Header::openbigbox('100%', 'LEFT', '', $errormessage);
	if ($errormessage) {
	    &Header::openbox('100%', 'LEFT', $Lang::tr{'error messages'});
	    print "<class name='base'>$errormessage";
	    print "&nbsp;</class>";
	    &Header::closebox();		
	} else {		
		&Header::openbox('100%', 'LEFT', 'Validate imported configuration');
	}
	if ($errormessage eq ''){
		print <<END		
		<!-- net2net config gui -->
		<tr><td width='25%'>&nbsp;</td>
			<td width='25%'>&nbsp;</td></tr>
		<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'name'}:</td>
			<td><b>$confdetails[$ufuk]</b></td></tr>	
		<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'Act as'}</td>
			<td><b>$confdetails[6]</b></td>								
			<td class='boldbase'>$Lang::tr{'remote host/ip'}:</td>
			<td><b>$confdetails[5]</b></td></tr>
		<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'local subnet'}</td>
			<td><b>$confighash{$key}[8]</b></td>
			<td class='boldbase' nowrap='nowrap'>$Lang::tr{'remote subnet'}</td>
			<td><b>$confighash{$key}[11]</b></td></tr>
		<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'ovpn subnet'}</td>
			<td><b>$confighash{$key}[$ufuk-1]</b></td></tr>
		<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'protocol'}</td>
			<td><b>$confdetails[2]</b></td>
			<td class='boldbase'>$Lang::tr{'destination port'}:</td>
			<td><b>$confdetails[3]</b></td></tr>
		<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'comp-lzo'}</td>
			<td><b>$complzoactive</b></td>
			<td class='boldbase'>$Lang::tr{'cipher'}</td>
			<td><b>$confdetails[10]</b></td></tr>
		<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'MTU'}&nbsp;<img src='/blob.gif' /></td>
		    <td><b>$confdetails[1]</b></td></tr>	
END
;	
	
		&Header::closebox();
	}
	if ($errormessage) {
		print "<div align='center'><a href='/cgi-bin/ovpnmain.cgi'>$Lang::tr{'back'}</a></div>";
	} else {	
		print "<div align='center'><form method='post' enctype='multipart/form-data'><input type='submit' name='ACTION' value='Approved' />";		
		print "<input type='hidden' name='TYPE' value='zerinan2n' />";
		print "<input type='hidden' name='KEY' value='$cgiparams{'KEY'}' />";			
		print "<input type='submit' name='ACTION' value='Discard' /></div></form>";
	}	
	&Header::closebigbox();
	&Header::closepage();
	exit(0);	

###
### Approve Zerina n2n
###
}  elsif (($cgiparams{'ACTION'} eq 'Approved') && ($cgiparams{'TYPE'} eq 'zerinan2n')){
	&Ovpnfunc::writenet2netconf($cgiparams{'KEY'},$zerinaclient);
###
### Discard Zerina n2n
###
}  elsif (($cgiparams{'ACTION'} eq 'Discard') && ($cgiparams{'TYPE'} eq 'zerinan2n')){
    &General::readhash("${General::swroot}/ovpn/settings", \%vpnsettings);
    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

    if ($confighash{$cgiparams{'KEY'}}) {	
		&Ovpnfunc::removenet2netconf();
		delete $confighash{$cgiparams{'KEY'}};	
		&General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);	
    } else {
		$errormessage = $Lang::tr{'invalid key'};
    }	
###
### Adding a new connection
###
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
		$cgiparams{'TYPE'}	= $confighash{$cgiparams{'KEY'}}[3];
		$cgiparams{'AUTH'} 	= $confighash{$cgiparams{'KEY'}}[4];
		$cgiparams{'PSK'}	= $confighash{$cgiparams{'KEY'}}[5];
		$cgiparams{'SIDE'}	= $confighash{$cgiparams{'KEY'}}[6];
		$cgiparams{'LOCAL_SUBNET'} = $confighash{$cgiparams{'KEY'}}[8];
		$cgiparams{'REMOTE'}	= $confighash{$cgiparams{'KEY'}}[10];
		$cgiparams{'REMOTE_SUBNET'} = $confighash{$cgiparams{'KEY'}}[11];
		$cgiparams{'REMARK'}	= $confighash{$cgiparams{'KEY'}}[25];
		$cgiparams{'INTERFACE'}	= $confighash{$cgiparams{'KEY'}}[12];
		$cgiparams{'OVPN_SUBNET'} = $confighash{$cgiparams{'KEY'}}[13];#new fields	
		$cgiparams{'PROTOCOL'}	  = $confighash{$cgiparams{'KEY'}}[14];
		$cgiparams{'DEST_PORT'}	  = $confighash{$cgiparams{'KEY'}}[15];
		$cgiparams{'COMPLZO'}	  = $confighash{$cgiparams{'KEY'}}[16];
		$cgiparams{'MTU'}	  = $confighash{$cgiparams{'KEY'}}[17];
		$cgiparams{'N2NVPN_IP'}	  = $confighash{$cgiparams{'KEY'}}[18];#new fields
		$cgiparams{'ZERINA_CLIENT'}	  = $confighash{$cgiparams{'KEY'}}[19];#new fields
		$cgiparams{'CIPHER'}	  = $confighash{$cgiparams{'KEY'}}[20];#new fields
		if ($cgiparams{'ZERINA_CLIENT'} eq ''){
			$cgiparams{'ZERINA_CLIENT'} = 'no';
		}
    } elsif ($cgiparams{'ACTION'} eq $Lang::tr{'save'}) {#ab hiere error uebernehmen
		$cgiparams{'REMARK'} = &Header::cleanhtml($cgiparams{'REMARK'});
		# n2n error
		if ($cgiparams{'TYPE'} !~ /^(host|net)$/) {
			$errormessage = $Lang::tr{'connection type is invalid'};
			goto VPNCONF_ERROR;
		}
		if ($cgiparams{'NAME'} !~ /^[a-zA-Z0-9]+$/) {
			$errormessage = $Lang::tr{'name must only contain characters'};
			goto VPNCONF_ERROR;
		}
		if ($cgiparams{'NAME'} =~ /^(host|01|block|private|clear|packetdefault|server)$/) {
			$errormessage = $Lang::tr{'name is invalid'};
			goto VPNCONF_ERROR;
		}
		if (length($cgiparams{'NAME'}) >60) {
			$errormessage = $Lang::tr{'name too long'};
			goto VPNCONF_ERROR;
		}
		if (! $cgiparams{'KEY'}) {# Check if there is no other entry with this name
			foreach my $key (keys %confighash) {
				if ($confighash{$key}[1] eq $cgiparams{'NAME'}) {
					$errormessage = $Lang::tr{'a connection with this name already exists'};
					goto VPNCONF_ERROR;
				}
			}
		}		
		if (($cgiparams{'TYPE'} eq 'net') && (! $cgiparams{'REMOTE'})) {
			$errormessage = $Lang::tr{'invalid input for remote host/ip'};
			goto VPNCONF_ERROR;
		}
		if ($cgiparams{'REMOTE'}) {
			if (! &General::validip($cgiparams{'REMOTE'})) {
				if (! &General::validfqdn ($cgiparams{'REMOTE'}))  {
					$errormessage = $Lang::tr{'invalid input for remote host/ip'};
					goto VPNCONF_ERROR;
				} else {
					if (&Ovpnfunc::valid_dns_host($cgiparams{'REMOTE'})) {
						$warnmessage = "$Lang::tr{'check vpn lr'} $cgiparams{'REMOTE'}. $Lang::tr{'dns check failed'}";
					}
				}
			}
		}
		if ($cgiparams{'TYPE'} ne 'host') {
			unless (&General::validipandmask($cgiparams{'LOCAL_SUBNET'})) {
				$errormessage = $Lang::tr{'local subnet is invalid'}; 
				goto VPNCONF_ERROR;
			}
		}
		#hier1
		my @tmpovpnsubnet = split("\/",$cgiparams{'LOCAL_SUBNET'});	
		$tmpovpnsubnet[1]  = &Ovpnfunc::cidrormask($tmpovpnsubnet[1]);
		$cgiparams{'LOCAL_SUBNET'} = "$tmpovpnsubnet[0]/$tmpovpnsubnet[1]";#convert from cidr
		#hier1
		if ($cgiparams{'REMOTE'} eq '') {# Check if there is no other entry without IP-address and PSK
			foreach my $key (keys %confighash) {
				if(($cgiparams{'KEY'} ne $key) && ($confighash{$key}[4] eq 'psk' || $cgiparams{'AUTH'} eq 'psk') && $confighash{$key}[10] eq '') {
					$errormessage = $Lang::tr{'you can only define one roadwarrior connection when using pre-shared key authentication'};
					goto VPNCONF_ERROR;
				}
			}
		}
		if (($cgiparams{'TYPE'} eq 'net') && (! &General::validipandmask($cgiparams{'REMOTE_SUBNET'}))) {
			$errormessage = $Lang::tr{'remote subnet is invalid'};
			goto VPNCONF_ERROR;
		}
		#hier2
		my @tmpovpnsubnet = split("\/",$cgiparams{'REMOTE_SUBNET'});	
		$tmpovpnsubnet[1]  = &Ovpnfunc::cidrormask($tmpovpnsubnet[1]);
		$cgiparams{'REMOTE_SUBNET'} = "$tmpovpnsubnet[0]/$tmpovpnsubnet[1]";#convert from cidr
		#hier2
		if ($cgiparams{'ENABLED'} !~ /^(on|off)$/) {
			$errormessage = $Lang::tr{'invalid input'};
			goto VPNCONF_ERROR;
		}
		if ($cgiparams{'EDIT_ADVANCED'} !~ /^(on|off)$/) {
			$errormessage = $Lang::tr{'invalid input'};
			goto VPNCONF_ERROR;
		}
		if ($cgiparams{'ENABLED'} eq 'on'){
			$errormessage = &Ovpnfunc::disallowreserved($cgiparams{'DEST_PORT'},0,$cgiparams{'PROTOCOL'},"dest");
		}	
		if ($errormessage) { goto VPNCONF_ERROR; }
    
		if ($cgiparams{'ENABLED'} eq 'on'){
			$errormessage = &Ovpnfunc::checkportfw(0,$cgiparams{'DEST_PORT'},$cgiparams{'PROTOCOL'},'0.0.0.0');
		}  	
		if ($errormessage) { goto VPNCONF_ERROR; }
#raul
		if ($cgiparams{'TYPE'} eq 'net') {
			if (! &General::validipandmask($cgiparams{'OVPN_SUBNET'})) {
				$errormessage = $Lang::tr{'ovpn subnet is invalid'};
				goto VPNCONF_ERROR;
			}
			#hier3
			my @tmpovpnsubnet = split("\/",$cgiparams{'OVPN_SUBNET'});
			$tmpovpnsubnet[1]  = &Ovpnfunc::cidrormask($tmpovpnsubnet[1]);
			$cgiparams{'OVPN_SUBNET'} = "$tmpovpnsubnet[0]/$tmpovpnsubnet[1]";#convert from cidr
			#hier3  
			#plausi2	
			$errormessage = &Ovpnfunc::ovelapplausi($tmpovpnsubnet[0],$tmpovpnsubnet[1]);
			#plausi2
			if ($errormessage ne ''){
				goto VPNCONF_ERROR;
			}
			if ((length($cgiparams{'MTU'})==0) || (($cgiparams{'MTU'}) < 1000 )) {
				$errormessage = $Lang::tr{'invalid mtu input'};
				goto VPNCONF_ERROR;
			}  
			unless (&General::validport($cgiparams{'DEST_PORT'})) {
				$errormessage = $Lang::tr{'invalid port'};
				goto VPNCONF_ERROR;
			}
			# check protcol/port overlap against existing connections gian
			foreach my $dkey (keys %confighash) {#Check if there is no other entry with this name
				if ($dkey ne $cgiparams{'KEY'}) {
					if ($confighash{$dkey}[14] eq $cgiparams{'PROTOCOL'} &&  $confighash{$dkey}[15] eq $cgiparams{'DEST_PORT'}){
						#if ($confighash{$dkey}[14] eq 'on') {
							$errormessage = "Choosed Protocol/Port combination is already used by connection: $confighash{$dkey}[1]";
							goto VPNCONF_ERROR;			
						#} else {
						#	$warnmessage = "Choosed Protcol/Port combination is used by inactive connection: $confighash{$dkey}[1]";
						#}	
					}
				}
			}			
			#check  protcol/port overlap against RWserver gian
			if ($vpnsettings{'ENABLED'} eq 'on') {		
				if ($vpnsettings{'DPROTOCOL'} eq $cgiparams{'PROTOCOL'} &&  $vpnsettings{'DDEST_PORT'} eq $cgiparams{'DEST_PORT'}){
					$errormessage = "Choosed Protocol/Port combination is already used OpenVPN Roadwarrior Server";
					goto VPNCONF_ERROR;			
				}
			}			
		}
		if ($cgiparams{'AUTH'} eq 'psk')  {
			#removed
		} elsif ($cgiparams{'AUTH'} eq 'certreq') {
		#	{
			if ($cgiparams{'KEY'}) {
				$errormessage = $Lang::tr{'cant change certificates'};
				goto VPNCONF_ERROR;
			}
			if (ref ($cgiparams{'FH'}) ne 'Fh') {
				$errormessage = $Lang::tr{'there was no file upload'};
				goto VPNCONF_ERROR;
			}
			(my $fh, my $filename) = tempfile( );# Move uploaded certificate request to a temporary file
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
				&Ovpnfunc::newcleanssldatabase();
				goto VPNCONF_ERROR;
			} else {
				unlink ($filename);
				&Ovpnfunc::deletebackupcert();
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
			(my $fh, my $filename) = tempfile( );# Move uploaded certificate to a temporary file
			if (copy ($cgiparams{'FH'}, $fh) != 1) {
				$errormessage = $!;
				goto VPNCONF_ERROR;
			}
			my $validca = 0;# Verify the certificate has a valid CA and move it
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
		} elsif ($cgiparams{'AUTH'} eq 'certgen'){		
			if ($cgiparams{'KEY'}) {
				$errormessage = $Lang::tr{'cant change certificates'};
				goto VPNCONF_ERROR;
			}
			if (length($cgiparams{'CERT_NAME'}) >60) {# Validate input since the form was submitted
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
			(my $ou = $cgiparams{'CERT_OU'}) =~ s/^\s*$/\./;# Replace empty strings with a .
			(my $city = $cgiparams{'CERT_CITY'}) =~ s/^\s*$/\./;
			(my $state = $cgiparams{'CERT_STATE'}) =~ s/^\s*$/\./;
			my $pid = open(OPENSSL, "|-");# Create the Host certificate request client
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
				&Ovpnfunc::newcleanssldatabase();
				goto VPNCONF_ERROR;
			} else {
				unlink ("${General::swroot}/ovpn/certs/$cgiparams{'NAME'}req.pem");
				&Ovpnfunc::deletebackupcert();
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
		if ((! $cgiparams{'KEY'}) && ($cgiparams{'AUTH'} ne 'psk')) {# Check if there is no other entry with this common name
			foreach my $key (keys %confighash) {
				if ($confighash{$key}[2] eq $cgiparams{'CERT_NAME'}) {
					$errormessage = $Lang::tr{'a connection with this common name already exists'};
					goto VPNCONF_ERROR;
				}
			}
		}

		my $key = $cgiparams{'KEY'};# Save the config
		if (! $key) {
			$key = &General::findhasharraykey (\%confighash);
			foreach my $i (0 .. 42) { $confighash{$key}[$i] = "";}
		}
		$confighash{$key}[0] = $cgiparams{'ENABLED'};
		$confighash{$key}[1] = $cgiparams{'NAME'};
		if ((! $cgiparams{'KEY'}) && $cgiparams{'AUTH'} ne 'psk') {
			$confighash{$key}[2] = $cgiparams{'CERT_NAME'};
		}
		$confighash{$key}[3] = $cgiparams{'TYPE'};
		if ($cgiparams{'AUTH'} eq 'psk') {
			$confighash{$key}[4] = 'psk';
			$confighash{$key}[5] = $cgiparams{'PSK'};
		} else {
			$confighash{$key}[4] = 'cert';
		}
		if ($cgiparams{'TYPE'} eq 'net') {
			$confighash{$key}[6] = $cgiparams{'SIDE'};
			$confighash{$key}[11] = $cgiparams{'REMOTE_SUBNET'};
			if ( $cgiparams{'SIDE'} eq  'client') {
					$confighash{$key}[19] = 'yes';
			} else{
				$confighash{$key}[19] = 'no';
			}
		}
		$confighash{$key}[8] = $cgiparams{'LOCAL_SUBNET'};
		$confighash{$key}[10] = $cgiparams{'REMOTE'};
		$confighash{$key}[25] = $cgiparams{'REMARK'};
		$confighash{$key}[12] = $cgiparams{'INTERFACE'};
		$confighash{$key}[13] = $cgiparams{'OVPN_SUBNET'};# new fields	
		$confighash{$key}[14] = $cgiparams{'PROTOCOL'};
		$confighash{$key}[15] = $cgiparams{'DEST_PORT'};
		$confighash{$key}[16] = $cgiparams{'COMPLZO'};
		$confighash{$key}[17] = $cgiparams{'MTU'};
		$confighash{$key}[18] = $cgiparams{'N2NVPN_IP'};# new fileds
		$confighash{$key}[19] = $cgiparams{'ZERINA_CLIENT'};# new fileds
		$confighash{$key}[20] = $cgiparams{'CIPHER'};
		
		#default n2n advanced
		$confighash{$key}[26] = '10';#keepalive ping
		$confighash{$key}[27] = '60';#keepalive restart
		$confighash{$key}[28] = '0';#nice
		$confighash{$key}[42] = '3';#verb
		#default n2n advanced
		&General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
		&Ovpnfunc::writenet2netconf($key,$zerinaclient);
		#ppp
		my $n2nactive = `/bin/ps ax|grep $cgiparams{'NAME'}.conf|grep -v grep|awk \'{print \$1}\'`;
		if ($cgiparams{'ENABLED'}) {			
			if ($n2nactive eq ''){
				system('/usr/local/bin/openvpnctrl', '-sn2n', $cgiparams{'NAME'});
			} else {
				system('/usr/local/bin/openvpnctrl', '-kn2n', $n2nactive);
				system('/usr/local/bin/openvpnctrl', '-sn2n', $cgiparams{'NAME'});
			}			
		} else {					
			if ($n2nactive ne ''){				
				system('/usr/local/bin/openvpnctrl', '-kn2n', $cgiparams{'NAME'});
			}						
		}
		if ($cgiparams{'EDIT_ADVANCED'} eq 'on') {
			$cgiparams{'KEY'} = $key;
			$cgiparams{'ACTION'} = $Lang::tr{'advanced'};
		}
		goto VPNCONF_END;
    } else {
		$cgiparams{'ENABLED'} = 'on';
		if ($cgiparams{'ZERINA_CLIENT'} eq ''){
			$cgiparams{'ZERINA_CLIENT'} = 'no';
		}			
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
	# n2n default settings
	if ($cgiparams{'CIPHER'} eq '') {
		$cgiparams{'CIPHER'} =  'BF-CBC';     
    }
    if ($cgiparams{'MTU'} eq '') {
		$cgiparams{'MTU'} =  '1400';     
    }
    if ($cgiparams{'OVPN_SUBNET'} eq '') {
		$cgiparams{'OVPN_SUBNET'} = '10.' . int(rand(256)) . '.' . int(rand(256)) . '.0/255.255.255.0';
    }
	#n2n default settings
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
	
#	$selected{'DDEVICE'}{'tun'} = '';
#    $selected{'DDEVICE'}{'tap'} = '';
#    $selected{'DDEVICE'}{$cgiparams{'DDEVICE'}} = 'SELECTED';

    $selected{'PROTOCOL'}{'udp'} = '';
    $selected{'PROTOCOL'}{'tcp'} = '';
    $selected{'PROTOCOL'}{$cgiparams{'PROTOCOL'}} = 'SELECTED';
 
    $checked{'AUTH'}{'psk'} = '';
    $checked{'AUTH'}{'certreq'} = '';
    $checked{'AUTH'}{'certgen'} = '';
    $checked{'AUTH'}{'certfile'} = '';
    $checked{'AUTH'}{$cgiparams{'AUTH'}} = 'CHECKED';
    $selected{'INTERFACE'}{$cgiparams{'INTERFACE'}} = 'SELECTED';
    $checked{'COMPLZO'}{'off'} = '';
    $checked{'COMPLZO'}{'on'} = '';
    $checked{'COMPLZO'}{$cgiparams{'COMPLZO'}} = 'CHECKED';
	$selected{'CIPHER'}{'DES-CBC'} = '';
    $selected{'CIPHER'}{'DES-EDE-CBC'} = '';
    $selected{'CIPHER'}{'DES-EDE3-CBC'} = '';
    $selected{'CIPHER'}{'DESX-CBC'} = '';
    $selected{'CIPHER'}{'RC2-CBC'} = '';
    $selected{'CIPHER'}{'RC2-40-CBC'} = '';
    $selected{'CIPHER'}{'RC2-64-CBC'} = '';
    $selected{'CIPHER'}{'BF-CBC'} = '';
    $selected{'CIPHER'}{'CAST5-CBC'} = '';    
    $selected{'CIPHER'}{'AES-128-CBC'} = '';
    $selected{'CIPHER'}{'AES-192-CBC'} = '';
    $selected{'CIPHER'}{'AES-256-CBC'} = '';
    $selected{'CIPHER'}{$cgiparams{'CIPHER'}} = 'SELECTED';

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
	print "<input type='hidden' name='TYPE' value='$cgiparams{'TYPE'}' />";
	print "<input type='hidden' name='ZERINA_CLIENT' value='$cgiparams{'ZERINA_CLIENT'}' />";
	if ($cgiparams{'KEY'}) {
	    print "<input type='hidden' name='KEY' value='$cgiparams{'KEY'}' />";
	    print "<input type='hidden' name='AUTH' value='$cgiparams{'AUTH'}' />";
	}
	&Header::openbox('100%', 'LEFT', "$Lang::tr{'connection'}:");
	print "<table width='100%'>\n";
	print "<tr><td width='25%' class='boldbase'>$Lang::tr{'name'}:</td>";
	if ($cgiparams{'TYPE'} eq 'host') {
	    if ($cgiparams{'KEY'}) {
		print "<td width='35%' class='base'><input type='hidden' name='NAME' value='$cgiparams{'NAME'}' />$cgiparams{'NAME'}</td>\n";
	    } else {
		print "<td width='35%'><input type='text' name='NAME' value='$cgiparams{'NAME'}' maxlength='20' size='30' /></td>";
	    }
	} else {
	    print "<input type='hidden' name='INTERFACE' value='red' />";
	    if ($cgiparams{'KEY'}) {
			print "<td width='25%' class='base' nowrap='nowrap'><input type='hidden' name='NAME' value='$cgiparams{'NAME'}' />$cgiparams{'NAME'}</td>";
	    } else {
			print "<td width='25%'><input type='text' name='NAME' value='$cgiparams{'NAME'}' maxlength='20' /></td>";
	    }
			print "<!-- net2net config gui -->";
			print "<td width='25%'>&nbsp;</td>";
		    print "<td width='25%'>&nbsp;</td></tr>";
			if ((($cgiparams{'ACTION'} eq $Lang::tr{'edit'}) && ($cgiparams{'ZERINA_CLIENT'} eq 'no')) ||
			   (($cgiparams{'ACTION'} eq $Lang::tr{'save'}) && ($cgiparams{'ZERINA_CLIENT'} eq 'no')) ||
			   (($cgiparams{'ACTION'} eq $Lang::tr{'add'}) && ($cgiparams{'ZERINA_CLIENT'} eq 'no'))) {
				print "<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'Act as'}</td>";
					print "<td><select name='SIDE'><option value='server' $selected{'SIDE'}{'server'}>OpenVPN Server</option>";
											print "<option value='client' $selected{'SIDE'}{'client'}>OpenVPN Client</option></select></td>";
				print "<tr><td class='base' nowrap='nowrap'>$Lang::tr{'local vpn hostname/ip'}:</td>";
					print "<td><input type='text' name='N2NVPN_IP' value='$cgiparams{'N2NVPN_IP'}' size='30' /></td>";						
				print "<td class='boldbase'>$Lang::tr{'remote host/ip'}:</td>";
			} else {
				print "<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'Act as'}</td>";
					print "<td>$cgiparams{'SIDE'}</td><input type='hidden' name='SIDE' value='$cgiparams{'SIDE'}' />";								
				print "<td class='boldbase'>$Lang::tr{'remote host/ip'}:</td>";				
			}	
				print "<td><input type='TEXT' name='REMOTE' value='$cgiparams{'REMOTE'}' /></td></tr>";
				print "<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'local subnet'}</td>";
				print "<td><input type='TEXT' name='LOCAL_SUBNET' value='$cgiparams{'LOCAL_SUBNET'}' /></td>";
				print "<td class='boldbase' nowrap='nowrap'>$Lang::tr{'remote subnet'}</td>";
				print "<td><input type='text' name='REMOTE_SUBNET' value='$cgiparams{'REMOTE_SUBNET'}' /></td></tr>";
				print "<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'ovpn subnet'}</td>";
				print "<td><input type='TEXT' name='OVPN_SUBNET' value='$cgiparams{'OVPN_SUBNET'}' /></td></tr>";
				print "<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'protocol'}</td>";
				print "<td><select name='PROTOCOL'><option value='udp' $selected{'PROTOCOL'}{'udp'}>UDP</option>";
											print "<option value='tcp' $selected{'PROTOCOL'}{'tcp'}>TCP</option></select></td>";
				print "<td class='boldbase'>$Lang::tr{'destination port'}:</td>";
				print "<td><input type='TEXT' name='DEST_PORT' value='$cgiparams{'DEST_PORT'}' size='5' /></td></tr>";
				print "<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'comp-lzo'}</td>";
				print "<td><input type='checkbox' name='COMPLZO' $checked{'COMPLZO'}{'on'} /></td>";
				print "<td class='boldbase' nowrap='nowrap'>$Lang::tr{'cipher'}</td>";
				print "<td><select name='CIPHER'><option value='DES-CBC' $selected{'CIPHER'}{'DES-CBC'}>DES-CBC</option>";
				print "<option value='DES-EDE-CBC' $selected{'CIPHER'}{'DES-EDE-CBC'}>DES-EDE-CBC</option>";
				print "<option value='DES-EDE3-CBC' $selected{'CIPHER'}{'DES-EDE3-CBC'}>DES-EDE3-CBC</option>";
				print "<option value='DESX-CBC' $selected{'CIPHER'}{'DESX-CBC'}>DESX-CBC</option>";
				print "<option value='RC2-CBC' $selected{'CIPHER'}{'RC2-CBC'}>RC2-CBC</option>";
				print "<option value='RC2-40-CBC' $selected{'CIPHER'}{'RC2-40-CBC'}>RC2-40-CBC</option>";
				print "<option value='RC2-64-CBC' $selected{'CIPHER'}{'RC2-64-CBC'}>RC2-64-CBC</option>";
				print "<option value='BF-CBC' $selected{'CIPHER'}{'BF-CBC'}>BF-CBC</option>";
				print "<option value='CAST5-CBC' $selected{'CIPHER'}{'CAST5-CBC'}>CAST5-CBC</option>";
				print "<option value='AES-128-CBC' $selected{'CIPHER'}{'AES-128-CBC'}>AES-128-CBC</option>";
				print "<option value='AES-192-CBC' $selected{'CIPHER'}{'AES-192-CBC'}>AES-192-CBC</option>";
				print "<option value='AES-256-CBC' $selected{'CIPHER'}{'AES-256-CBC'}>AES-256-CBC</option></select></td>";
				print "<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'MTU'}&nbsp;</td>";
				print "<td> <input type='TEXT' name='MTU' VALUE='$cgiparams{'MTU'}'size='5' /></TD>";
	}
	print "<tr><td class='boldbase'>$Lang::tr{'remark title'}&nbsp;<img src='/blob.gif' /></td>";
	print "<td colspan='3'><input type='text' name='REMARK' value='$cgiparams{'REMARK'}' size='55' maxlength='50' /></td></tr>";
#	if ($cgiparams{'TYPE'} eq 'net') {
	    print "<tr><td>$Lang::tr{'enabled'} <input type='checkbox' name='ENABLED' $checked{'ENABLED'}{'on'} /></td>\n";
	
	if ($cgiparams{'TYPE'} eq 'host') {
	    print "<td colspan='3'>&nbsp;</td></tr></table>";
	} elsif  ($cgiparams{'ACTION'} ne $Lang::tr{'edit'}){
		print "<td colspan='3'><input type='checkbox' name='EDIT_ADVANCED' $checked{'EDIT_ADVANCED'}{'on'}/> $Lang::tr{'edit advanced settings when done'}</tr></table>";
    } else {
		print "<td colspan='3'></tr></table>";
	}	
	

	&Header::closebox();
	if ($cgiparams{'KEY'} && $cgiparams{'AUTH'} eq 'psk') {
	;#we dont have psk
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
		if ($cgiparams{'TYPE'} ne 'host') { 
			print "<input type='submit' name='ACTION' value='$Lang::tr{'advanced'}' />";
		}	
	}
	print "<input type='submit' name='ACTION' value='$Lang::tr{'cancel'}' /></div></form>";
	&Header::closebigbox();
	&Header::closepage();
	exit (0);
    }
    VPNCONF_END:
}
###
### Advanced settings
###
if(($cgiparams{'ACTION'} eq $Lang::tr{'advanced'}) ||
	($cgiparams{'ACTION'} eq $Lang::tr{'save'} && $cgiparams{'ADVANCED'} eq 'yes')) {
    &General::readhash("${General::swroot}/ovpn/settings", \%vpnsettings);
    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
	
    if (! $confighash{$cgiparams{'KEY'}}) {
		$errormessage = $Lang::tr{'invalid key'};
		goto ADVANCED_END;
    }
	#n2n advanced error
	if ($cgiparams{'KEEPALIVE_1'} ne '') {
		if ($cgiparams{'KEEPALIVE_1'} !~ /^[0-9]+$/) { 
    	    $errormessage = $Lang::tr{'invalid input for keepalive 1'};
			goto ADVANCED_ERROR;
		}
    }
    if ($cgiparams{'KEEPALIVE_2'} ne ''){
		if ($cgiparams{'KEEPALIVE_2'} !~ /^[0-9]+$/) { 
    	    $errormessage = $Lang::tr{'invalid input for keepalive 2'};
			goto ADVANCED_ERROR;
		}
    }
    if ($cgiparams{'KEEPALIVE_2'} < ($cgiparams{'KEEPALIVE_1'} * 2)){
        $errormessage = $Lang::tr{'invalid input for keepalive 1:2'};
        goto ADVANCED_ERROR;	
    }
	if ($cgiparams{'ACTION'} eq $Lang::tr{'save'}) {
#		if ($cgiparams{'NAT'} !~ /^(on|off)$/) {
#			$errormessage = $Lang::tr{'invalid input'};
#			goto ADVANCED_ERROR;
#		}
	#n2n advanced error
	#cgi an config
		$confighash{$cgiparams{'KEY'}}[26] = $cgiparams{'KEEPALIVE_1'};
		$confighash{$cgiparams{'KEY'}}[27] = $cgiparams{'KEEPALIVE_2'};
		$confighash{$cgiparams{'KEY'}}[28] = $cgiparams{'EXTENDED_NICE'};
		$confighash{$cgiparams{'KEY'}}[29] = $cgiparams{'EXTENDED_FASTIO'};
		$confighash{$cgiparams{'KEY'}}[30] = $cgiparams{'EXTENDED_MTUDISC'};
		$confighash{$cgiparams{'KEY'}}[31] = $cgiparams{'EXTENDED_MSSFIX'};
		$confighash{$cgiparams{'KEY'}}[32] = $cgiparams{'EXTENDED_FRAGMENT'};
		$confighash{$cgiparams{'KEY'}}[33] = $cgiparams{'PROXY_HOST'};
		$confighash{$cgiparams{'KEY'}}[34] = $cgiparams{'PROXY_PORT'};
		$confighash{$cgiparams{'KEY'}}[35] = $cgiparams{'PROXY_USERNAME'};
		$confighash{$cgiparams{'KEY'}}[36] = $cgiparams{'PROXY_PASS'};
		$confighash{$cgiparams{'KEY'}}[37] = $cgiparams{'PROXY_AUTH_METHOD'};
		$confighash{$cgiparams{'KEY'}}[38] = $cgiparams{'http-proxy-retry'};
		$confighash{$cgiparams{'KEY'}}[39] = $cgiparams{'PROXY_TIMEOUT'};
		$confighash{$cgiparams{'KEY'}}[40] = $cgiparams{'PROXY_OPT_VERSION'};
		$confighash{$cgiparams{'KEY'}}[41] = $cgiparams{'PROXY_OPT_AGENT'};
		$confighash{$cgiparams{'KEY'}}[42] = $cgiparams{'LOG_VERB'};
		&General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
		&Ovpnfunc::writenet2netconf($cgiparams{'KEY'},$zerinaclient);
	#	restart n2n after advanced save ?
		goto ADVANCED_END;
	} else {	
		$cgiparams{'KEEPALIVE_1'}         =  $confighash{$cgiparams{'KEY'}}[26];
		$cgiparams{'KEEPALIVE_2'}         =  $confighash{$cgiparams{'KEY'}}[27];
		$cgiparams{'EXTENDED_NICE'}       =  $confighash{$cgiparams{'KEY'}}[28];
		$cgiparams{'EXTENDED_FASTIO'}     =  $confighash{$cgiparams{'KEY'}}[29];
		$cgiparams{'EXTENDED_MTUDISC'}    =  $confighash{$cgiparams{'KEY'}}[30];
		$cgiparams{'EXTENDED_MSSFIX'}     =  $confighash{$cgiparams{'KEY'}}[31];
		$cgiparams{'EXTENDED_FRAGMENT'}   =  $confighash{$cgiparams{'KEY'}}[32];
		$cgiparams{'PROXY_HOST'}          =  $confighash{$cgiparams{'KEY'}}[33];
		$cgiparams{'PROXY_PORT'}          =  $confighash{$cgiparams{'KEY'}}[34];
		$cgiparams{'PROXY_USERNAME'}      =  $confighash{$cgiparams{'KEY'}}[35];
		$cgiparams{'PROXY_PASS'}          =  $confighash{$cgiparams{'KEY'}}[36];
		$cgiparams{'PROXY_AUTH_METHOD'}   =  $confighash{$cgiparams{'KEY'}}[37];
		$cgiparams{'http-proxy-retry'}    =  $confighash{$cgiparams{'KEY'}}[38];
		$cgiparams{'PROXY_TIMEOUT'}       =  $confighash{$cgiparams{'KEY'}}[39];
		$cgiparams{'PROXY_OPT_VERSION'}   =  $confighash{$cgiparams{'KEY'}}[40];
		$cgiparams{'PROXY_OPT_AGENT'}     =  $confighash{$cgiparams{'KEY'}}[41];
		$cgiparams{'LOG_VERB'}            =  $confighash{$cgiparams{'KEY'}}[42];
		#cgi an config
	}	
	ADVANCED_ERROR:
	#Schalter setzen
    $selected{'EXTENDED_NICE'}{'-13'} = '';
    $selected{'EXTENDED_NICE'}{'-10'} = '';
    $selected{'EXTENDED_NICE'}{'-7'} = '';
    $selected{'EXTENDED_NICE'}{'-3'} = '';
    $selected{'EXTENDED_NICE'}{'0'} = '';
    $selected{'EXTENDED_NICE'}{'3'} = '';
    $selected{'EXTENDED_NICE'}{'7'} = '';
    $selected{'EXTENDED_NICE'}{'10'} = '';
    $selected{'EXTENDED_NICE'}{'13'} = '';
    $selected{'EXTENDED_NICE'}{$cgiparams{'EXTENDED_NICE'}} = 'SELECTED';
	$checked{'EXTENDED_FASTIO'}{'off'} = '';
    $checked{'EXTENDED_FASTIO'}{'on'} = '';
    $checked{'EXTENDED_FASTIO'}{$cgiparams{'EXTENDED_FASTIO'}} = 'CHECKED';
    $checked{'EXTENDED_MTUDISC'}{'off'} = '';
    $checked{'EXTENDED_MTUDISC'}{'on'} = '';
    $checked{'EXTENDED_MTUDISC'}{$cgiparams{'EXTENDED_MTUDISC'}} = 'CHECKED';
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
	$selected{'PROXY_AUTH_METHOD'}{'none'} = '';
	$selected{'PROXY_AUTH_METHOD'}{'basic'} = '';
	$selected{'PROXY_AUTH_METHOD'}{'ntlm'} = '';
	$selected{'PROXY_AUTH_METHOD'}{$cgiparams{'PROXY_AUTH_METHOD'}} = 'SELECTED';
	$checked{'PROXY_RETRY'}{'off'} = '';
	$checked{'PROXY_RETRY'}{'on'} = '';
	$checked{'PROXY_RETRY'}{$cgiparams{'PROXY_RETRY'}} = 'CHECKED';
	#Schalter setzen
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
	&Header::openbox('100%', 'LEFT', $Lang::tr{'warning messages'});
	print "<class name='base'>$warnmessage";
	print "&nbsp;</class>";
	&Header::closebox();
    }

    print "<form method='post' enctype='multipart/form-data'>\n";
    print "<input type='hidden' name='ADVANCED' value='yes' />\n";
    print "<input type='hidden' name='KEY' value='$cgiparams{'KEY'}' />\n";

    &Header::openbox('100%', 'LEFT', "$Lang::tr{'advanced'}:");    
    print <<EOF
    <form method='post' enctype='multipart/form-data'>
    <table width='100%'>
    <tr>
	<td class'base'><b>$Lang::tr{'misc-options'}</b></td>
    </tr>
    <tr>
	<td width='25%'></td> <td width='20%'> </td><td width='25%'> </td><td width='30%'></td>
    </tr>
    <td class='base'>Keppalive (ping/ping-restart)</td>	
	<td><input type='TEXT' name='KEEPALIVE_1' value='$cgiparams{'KEEPALIVE_1'}' size='30' /></td>
	<td><input type='TEXT' name='KEEPALIVE_2' value='$cgiparams{'KEEPALIVE_2'}' size='30' /></td>
    </tr>	
    </tr>
    <tr>
      <td class='base'>$Lang::tr{'ovpn_processprio'}</td>        
      <td>
        <select name='EXTENDED_NICE' disabled='disabled'>
				  <option value='-13' $selected{'EXTENDED_NICE'}{'-13'}>$Lang::tr{'ovpn_processprioEH'}</option>
				  <option value='-10' $selected{'EXTENDED_NICE'}{'-10'}>$Lang::tr{'ovpn_processprioVH'}</option>
				  <option value='-7'  $selected{'EXTENDED_NICE'}{'-7'}>$Lang::tr{'ovpn_processprioH'}</option>
				  <option value='-3'  $selected{'EXTENDED_NICE'}{'-3'}>$Lang::tr{'ovpn_processprioEN'}</option>
				  <option value='0'  $selected{'EXTENDED_NICE'}{'0'}>$Lang::tr{'ovpn_processprioN'}</option>
				  <option value='3'  $selected{'EXTENDED_NICE'}{'3'}>$Lang::tr{'ovpn_processprioLN'}</option>
				  <option value='7'  $selected{'EXTENDED_NICE'}{'7'}>$Lang::tr{'ovpn_processprioD'}</option>
				  <option value='10' $selected{'EXTENDED_NICE'}{'10'}>$Lang::tr{'ovpn_processprioVD'}</option>
				  <option value='13' $selected{'EXTENDED_NICE'}{'13'}>$Lang::tr{'ovpn_processprioED'}</option>
				</select>
		  </td>
		</tr>
    <tr>
      <td class='base'>$Lang::tr{'ovpn_fastio'}</td>        
      <td>
        <input type='checkbox' name='EXTENDED_FASTIO' $checked{'EXTENDED_FASTIO'}{'on'} disabled='disabled'/>
		  </td>
		</tr>
    <tr>
      <td class='base'>$Lang::tr{'ovpn_mtudisc'}</td>        
      <td>
        <input type='checkbox' name='EXTENDED_MTUDISC' $checked{'EXTENDED_MTUDISC'}{'on'} disabled='disabled'/>
		  </td>
		</tr>  
    <tr>
      <td class='base'>$Lang::tr{'ovpn_mssfix'}</td>        
      <td>
        <input type='TEXT' name='EXTENDED_MSSFIX' value='$cgiparams{'EXTENDED_MSSFIX'}' size='30' disabled='disabled'/>
		  </td>
		</tr>  
    <tr>
      <td class='base'>$Lang::tr{'ovpn_fragment'}</td>        
      <td>
        <input type='TEXT' name='EXTENDED_FRAGMENT' value='$cgiparams{'EXTENDED_FRAGMENT'}' size='30' disabled='disabled'/>
		  </td>
		</tr>    
</table>
<hr size='1'>
    <table width='100%'>
    <tr>
	<td class'base'><b>$Lang::tr{'proxy'} $Lang::tr{'settings'}</b></td>
    </tr>
    <tr>
	<td width='25%'></td> <td width='25%'> </td><td width='25%'> </td><td width='25%'></td>
    </tr>
    <td class='base'>$Lang::tr{'proxy'} $Lang::tr{'host'}:</td>	
	<td><input type='TEXT' name='PROXY_HOST' value='$cgiparams{'PROXY_HOST'}' size='30' disabled='disabled'/></td>
	<td class='base'>$Lang::tr{'proxy port'}:</td>
	<td><input type='TEXT' name='PROXY_PORT' value='$cgiparams{'PROXY_PORT'}' size='10' disabled='disabled'/></td>
	</tr>
	<tr>
	<td class='base'>$Lang::tr{'username'}</td>	
    <td><input type='TEXT' name='PROXY_USERNAME' value='$cgiparams{'PROXY_USERNAME'}' size='30' disabled='disabled' /></td>
	<td class='base'>$Lang::tr{'password'}</td>
	<td><input type='TEXT' name='PROXY_PASS' value='$cgiparams{'PROXY_PASS'}' size='10' disabled='disabled'/></td>
	</tr>
	<tr>
	<td class='base'>$Lang::tr{'authentication'} $Lang::tr{'method'}</td>
		<td>	
           <select name='PROXY_AUTH_METHOD' disabled='disabled'>
				  <option value='none' $selected{'PROXY_AUTH_METHOD'}{'none'}>none</option>
				  <option value='basic' $selected{'PROXY_AUTH_METHOD'}{'basic'}>basic</option>
				  <option value='ntlm' $selected{'PROXY_AUTH_METHOD'}{'ntlm'}>ntlm</option>				  
				</select>	
		</td>					
	</tr>
	<tr>
		<td class='base'>http-proxy-retry</td>	
		<td><input type='checkbox' name='PROXY_RETRY' $checked{'PROXY_RETRY'}{'on'} disabled='disabled' /></td>
		<td class='base'>http-proxy-timeout</td>
		<td><input type='TEXT' name='PROXY_TIMEOUT' value='$cgiparams{'PROXY_TIMEOUT'}' size='10' disabled='disabled'/></td>
	</tr>
	<td class='base'>http-proxy-option VERSION</td>
    <td><input type='TEXT' name='PROXY_OPT_VERSION' value='$cgiparams{'PROXY_OPT_VERSION'}' size='30' disabled='disabled'/></td>
	<td class='base'>http-proxy-option AGENT</td>
	<td><input type='TEXT' name='PROXY_OPT_AGENT' value='$cgiparams{'PROXY_OPT_AGENT'}' size='10' disabled='disabled'/></td>
	</tr>
</table>
<hr size='1'>
    <table width='100%'>
    <tr>
	<td class'base'><b>$Lang::tr{'log-options'}</b></td>
    </tr>
    <tr>
	<td width='25%'></td> <td width='20%'> </td><td width='25%'> </td><td width='30%'></td>
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
    </tr>	
</table>
</form>
EOF
    ;
    &Header::closebox();
    print "<div align='center'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' />";
    print "<input type='submit' name='ACTION' value='$Lang::tr{'cancel'}' /></div></form>";
    &Header::closebigbox();
    &Header::closepage();
    exit(0);

    ADVANCED_END:
}
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
#ufuk
#CERT
&Header::openbox('100%', 'LEFT', "$Lang::tr{'certificate authorities'}:");
print "<div align='center'><strong>ZERINA-0.9.7a9</strong></div>";	
print "&nbsp";
print <<EOF
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
	<tr bgcolor='${Header::table2colour}'>
	    <td class='base'>$Lang::tr{'root certificate'}</td>
		<td class='base'>$casubject</td>
		<form method='post' name='frmrootcrta'><td width='3%' align='center'>
			<input type='hidden' name='ACTION' value='$Lang::tr{'show root certificate'}' />
			<input type='image' name='$Lang::tr{'edit'}' src='/images/info.gif' alt='$Lang::tr{'show root certificate'}' title='$Lang::tr{'show root certificate'}' width='20' height='20' border='0' />
		</td></form>
		<form method='post' name='frmrootcrtb'><td width='3%' align='center'>
	    <input type='image' name='$Lang::tr{'download root certificate'}' src='/images/floppy.gif' alt='$Lang::tr{'download root certificate'}' title='$Lang::tr{'download root certificate'}' border='0' />
	    <input type='hidden' name='ACTION' value='$Lang::tr{'download root certificate'}' />
		</td></form>
		<td width='4%'>&nbsp;</td></tr>
END
	;
} else {
	# display rootcert generation buttons
	print <<END
	<tr bgcolor='${Header::table2colour}'>
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
	<tr bgcolor='${Header::table1colour}'>
	<td class='base'>$Lang::tr{'host certificate'}</td>
	<td class='base'>$hostsubject</td>
	<form method='post' name='frmhostcrta'><td width='3%' align='center'>
		<input type='hidden' name='ACTION' value='$Lang::tr{'show host certificate'}' />
		<input type='image' name='$Lang::tr{'show host certificate'}' src='/images/info.gif' alt='$Lang::tr{'show host certificate'}' title='$Lang::tr{'show host certificate'}' width='20' height='20' border='0' />
	</td></form>
	<form method='post' name='frmhostcrtb'><td width='3%' align='center'>
		<input type='image' name='$Lang::tr{'download host certificate'}' src='/images/floppy.gif' alt='$Lang::tr{'download host certificate'}' title='$Lang::tr{'download host certificate'}' border='0' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'download host certificate'}' />
	</td></form>
	<td width='4%'>&nbsp;</td></tr>
END
	;
} else {
	# Nothing
	print <<END
	<tr bgcolor='${Header::table1colour}'>
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
			print "<tr bgcolor='${Header::table1colour}'>\n";
		} else {
			print "<tr bgcolor='${Header::table2colour}'>\n";
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
		<input type='image' name='$Lang::tr{'download ca certificate'}' src='/images/floppy.gif' alt='$Lang::tr{'download ca certificate'}' title='$Lang::tr{'download ca certificate'}' border='0' />
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
if ( -f "${General::swroot}/ovpn/ca/cacert.pem") {# If the file contains entries, print Key to action icons
	print <<END
	<table>
	<tr>
	<td class='boldbase'>&nbsp; <b>$Lang::tr{'legend'}:</b></td>
	<td>&nbsp; &nbsp; <img src='/images/info.gif' alt='$Lang::tr{'show certificate'}' /></td>
	<td class='base'>$Lang::tr{'show certificate'}</td>
	<td>&nbsp; &nbsp; <img src='/images/floppy.gif' alt='$Lang::tr{'download certificate'}' /></td>
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
<td nowrap='nowrap'><input type='submit' name='ACTION' value='$Lang::tr{'upload ca certificate'}' /></td>
<td nowrap='nowrap'><input type='submit' name='ACTION' value='$Lang::tr{'show crl'}' /></td>    
</tr></table></form>
END
    ;
&Header::closebox();
if ( $srunning eq "yes" ) {    
	print "<div align='center'><form method='post'><input type='submit' name='ACTION' value='$Lang::tr{'reset'}' disabled='disabled' /></div></form>\n";    
}else{
   	print "<div align='center'><form method='post'><input type='submit' name='ACTION' value='$Lang::tr{'reset'}' /></div></form>\n";
}	    
#CERT
#RWSERVER
#&Header::openbox('100%', 'LEFT', $Lang::tr{'global settings'});
&Header::openbox('100%', 'LEFT', 'Roadwarrior Server');
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
if (&Ovpnfunc::haveBlueNet()) {
	print "<tr><td class='boldbase'>$Lang::tr{'ovpn on blue'}</td>";
	print "<td><input type='checkbox' name='ENABLED_BLUE' $checked{'ENABLED_BLUE'}{'on'} /></td>";
}
if (&Ovpnfunc::haveOrangeNet()) {    
	print "<tr><td class='boldbase'>$Lang::tr{'ovpn on orange'}</td>";
	print "<td><input type='checkbox' name='ENABLED_ORANGE' $checked{'ENABLED_ORANGE'}{'on'} /></td>";
}	
print <<END    	
<tr><td class='base' nowrap='nowrap'>$Lang::tr{'local vpn hostname/ip'}:</td>
    <td><input type='text' name='VPN_IP' value='$cgiparams{'VPN_IP'}' size='30' /></td>
	<td class='boldbase' nowrap='nowrap'>$Lang::tr{'ovpn subnet'}</td>
	<td><input type='TEXT' name='DOVPN_SUBNET' value='$cgiparams{'DOVPN_SUBNET'}' size='30' /></td></tr>
<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'ovpn device'}</td>
    <td><select name='DDEVICE' ><option value='tun' $selected{'DDEVICE'}{'tun'}>TUN</option>
                                <option value='tap' $selected{'DDEVICE'}{'tap'}>TAP</option></select></td>				    
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
#RWSERVER
&Ovpnfunc::rwclientstatus($activeonrun);
&Ovpnfunc::net2netstatus($activeonrun);
&Header::closepage();