#!/usr/bin/perl -w
package Ovpnfunc;
use Archive::Zip qw(:ERROR_CODES :CONSTANTS);
use Net::DNS;
use File::Copy;
use File::Temp qw/ tempfile tempdir /;
use strict;
require '/var/ipfire/general-functions.pl';
my %netsettings=();
my $errormessage = '';
my $errormessage2 = '';
my @subnets;        # array of anonymous hashes {cn, from, to}
my @subnets2;        # array of anonymous hashes {cn, from, to}
my %overlaps;       # hash {cn} of anonymous arrays of subnets
my ($subnet, $from, $to, $i, $j);
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
sub haveOrangeNet
{
	if ($netsettings{'CONFIG_TYPE'} == 1) {return 1;}
	if ($netsettings{'CONFIG_TYPE'} == 3) {return 1;}
	if ($netsettings{'CONFIG_TYPE'} == 5) {return 1;}
	if ($netsettings{'CONFIG_TYPE'} == 7) {return 1;}
	return 0;
}

sub haveBlueNet
{
	if ($netsettings{'CONFIG_TYPE'} == 4) {return 1;}
	if ($netsettings{'CONFIG_TYPE'} == 5) {return 1;}
	if ($netsettings{'CONFIG_TYPE'} == 6) {return 1;}
	if ($netsettings{'CONFIG_TYPE'} == 7) {return 1;}
	return 0;
}

sub sizeformat{
    my $bytesize = $_[0];
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

    return $errormessage;
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
# TCP 67,68,81,222,444
# UDP 67,68
# Params passed in -> port, rangeyn, protocol
sub disallowreserved
{
	# port 67 and 68 same for tcp and udp, don't bother putting in an array
	my $msg = "";
	my @tcp_reserved = (81,222,444);
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
				if ($prange == $prt) { 
					$errormessage = "$msg $prange"; 
					return $errormessage; }
			}
		}
	}
	return $errormessage;
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
    print CONF "#DAN prepare ZERINA for listening on blue and orange\n";
    print CONF ";local $sovpnsettings{'VPN_IP'}\n";
    print CONF "dev $sovpnsettings{'DDEVICE'}\n";
    print CONF "$sovpnsettings{'DDEVICE'}-mtu $sovpnsettings{'DMTU'}\n";
	if ($sovpnsettings{'DPROTOCOL'} eq 'tcp') {
		print CONF "proto $sovpnsettings{'DPROTOCOL'}-server\n";
	} else {	
		print CONF "proto $sovpnsettings{'DPROTOCOL'}\n";
	}	
    print CONF "port $sovpnsettings{'DDEST_PORT'}\n";
    print CONF "tls-server\n";
    print CONF "ca /var/ipfire/ovpn/ca/cacert.pem\n";
    print CONF "cert /var/ipfire/ovpn/certs/servercert.pem\n";
    print CONF "key /var/ipfire/ovpn/certs/serverkey.pem\n";
    print CONF "dh /var/ipfire/ovpn/ca/dh1024.pem\n";
    my @tempovpnsubnet = split("\/",$sovpnsettings{'DOVPN_SUBNET'});
    print CONF "server $tempovpnsubnet[0] $tempovpnsubnet[1]\n";
    print CONF "push \"route $netsettings{'GREEN_NETADDRESS'} $netsettings{'GREEN_NETMASK'}\"\n";
	if ($sovpnsettings{AD_ROUTE1} ne '') {
		my @tempovpnsubnet = split("\/",$sovpnsettings{'AD_ROUTE1'});
		print CONF "push \"route $tempovpnsubnet[0] $tempovpnsubnet[1]\"\n";
    }
	if ($sovpnsettings{AD_ROUTE2} ne '') {
		my @tempovpnsubnet = split("\/",$sovpnsettings{'AD_ROUTE2'});
		print CONF "push \"route $tempovpnsubnet[0] $tempovpnsubnet[1]\"\n";
    }
	if ($sovpnsettings{AD_ROUTE3} ne '') {
		my @tempovpnsubnet = split("\/",$sovpnsettings{'AD_ROUTE3'});
		print CONF "push \"route $tempovpnsubnet[0] $tempovpnsubnet[1]\"\n";
    }
    if ($sovpnsettings{CLIENT2CLIENT} eq 'on') {
	print CONF "client-to-client\n";
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

    #################################################################################
    #  Added by Philipp Jenni                                                       #
    #                                                                               #
    #  Contact: philipp.jenni-at-gmx.ch                                             #
    #  Date:    2006-04-22                                                          #
    #  Description:  Add the FAST-IO Parameter from OpenVPN to der Server.Config.   #
    #                Add the NICE Parameter from OpenVPN to der Server.Config.      #
    #                Add the MTU-DISC Parameter from OpenVPN to der Server.Config.  #
    #                Add the MSSFIX Parameter from OpenVPN to der Server.Config.    #
    #                Add the FRAMGMENT Parameter from OpenVPN to der Server.Config. #
    #################################################################################
    if ($sovpnsettings{EXTENDED_FASTIO} eq 'on') {
      print CONF "fast-io\n";  
    }
    if ($sovpnsettings{EXTENDED_NICE} != 0) {
      print CONF "nice $sovpnsettings{EXTENDED_NICE}\n"; 
    }
    if ($sovpnsettings{EXTENDED_MTUDISC} eq 'on') {
      print CONF "mtu-disc yes\n";  
    }    
    if ($sovpnsettings{EXTENDED_MSSFIX} ne '') {
      print CONF "mssfix $sovpnsettings{EXTENDED_MSSFIX}\n";  
    }    
    if ($sovpnsettings{EXTENDED_FRAGMENT} ne '') {
      print CONF "fragment $sovpnsettings{EXTENDED_FRAGMENT}\n";  
    }    
    #################################################################################
    #  End of Inserted Data                                                         #
    #################################################################################

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

sub writenet2netconf {
    my $n2nkey = $_[0];
    my $zerinaclient = $_[1];
    my %n2nconfighash = ();
    my $file = '';
#    my $file = '';
	my $clientovpn = '';
	my @fileholder;
	my $tempdir = tempdir( CLEANUP => 1 );
	my $zippath = "$tempdir/";
    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%n2nconfighash);
    if (! $n2nkey) {
        $n2nkey = &General::findhasharraykey (\%n2nconfighash);
        foreach my $i (0 .. 25) { $n2nconfighash{$n2nkey}[$i] = "";}
    }
	my $zipname = "$n2nconfighash{$n2nkey}[1].zip";
	my $zippathname = "$zippath$zipname";	
    if ($n2nconfighash{$n2nkey}[3] eq 'net') {
		if ($zerinaclient eq '') {
			if ( -d "${General::swroot}/ovpn/n2nconf/$n2nconfighash{$n2nkey}[1]"){
				while ($file = glob("${General::swroot}/ovpn/n2nconf/$n2nconfighash{$n2nkey}[1]/*.conf")) {
					unlink $file		
				}
			} else {
				mkdir("${General::swroot}/ovpn/n2nconf/$n2nconfighash{$n2nkey}[1]", 0770);
			}
			open(CONF, ">${General::swroot}/ovpn/n2nconf/$n2nconfighash{$n2nkey}[1]/$n2nconfighash{$n2nkey}[1].conf") or die "Unable to open ${General::swroot}/ovpn/n2nconf/$n2nconfighash{$n2nkey}[1]/$n2nconfighash{$n2nkey}[1].conf: $!";	
		} else {			
			$clientovpn = "$n2nconfighash{$n2nkey}[1].conf";
			open(CONF, ">$tempdir/$clientovpn") or die "Unable to open $tempdir/$clientovpn: $!";						
		}		
		flock CONF, 2;		
		print CONF "dev tun\n";		
		print CONF "tun-mtu $n2nconfighash{$n2nkey}[17]\n";
		if ($n2nconfighash{$n2nkey}[14] eq 'udp') {
			print CONF "proto $n2nconfighash{$n2nkey}[14]\n";
		} elsif ((($zerinaclient eq '') && ($n2nconfighash{$n2nkey}[6] eq 'server'))) {
			print CONF "proto $n2nconfighash{$n2nkey}[14]-server\n";
		} else {
			print CONF "proto $n2nconfighash{$n2nkey}[14]-client\n";
		}
		print CONF "port $n2nconfighash{$n2nkey}[15]\n";
		my @tempovpnsubnet = split("\/",$n2nconfighash{$n2nkey}[13]);
		my @ovpnip = split /\./,$tempovpnsubnet[0];
#		if ((($zerinaclient eq '') && ($n2nconfighash{$n2nkey}[19] eq 'no'))) {
		if ((($zerinaclient eq '') && ($n2nconfighash{$n2nkey}[6] eq 'server'))) {
			print CONF "ifconfig $ovpnip[0].$ovpnip[1].$ovpnip[2].1 $ovpnip[0].$ovpnip[1].$ovpnip[2].2\n";
			print CONF "remote $n2nconfighash{$n2nkey}[10]\n";
			print CONF "tls-server\n";
			print CONF "ca /var/ipfire/ovpn/ca/cacert.pem\n";
			print CONF "cert /var/ipfire/ovpn/certs/servercert.pem\n";
			print CONF "key /var/ipfire/ovpn/certs/serverkey.pem\n";
			print CONF "dh /var/ipfire/ovpn/ca/dh1024.pem\n";
			my @tempremotesubnet = split("\/",$n2nconfighash{$n2nkey}[11]);
			print CONF "route $tempremotesubnet[0] $tempremotesubnet[1]\n";
		} else {
			print CONF "ifconfig $ovpnip[0].$ovpnip[1].$ovpnip[2].2 $ovpnip[0].$ovpnip[1].$ovpnip[2].1\n";
			#print CONF "$zerinaclient ufuk 10=$n2nconfighash{$n2nkey}[10] 18=$n2nconfighash{$n2nkey}[18] 19=$n2nconfighash{$n2nkey}[19] \n";
			if ($zerinaclient ne 'true'){			
				if ($n2nconfighash{$n2nkey}[19] eq 'no'){
					print CONF "remote $n2nconfighash{$n2nkey}[10]\n";				
				} else {
					print CONF "remote $n2nconfighash{$n2nkey}[10]\n";	
				}
			} else {
				print CONF "remote $n2nconfighash{$n2nkey}[18]\n";	
			}
			print CONF "tls-client\n";
			if ($zerinaclient ne 'true'){
				print CONF "pkcs12 ${General::swroot}/ovpn/n2nconf/$n2nconfighash{$n2nkey}[1]/$n2nconfighash{$n2nkey}[1].p12\n";
			} else {
				print CONF "pkcs12 $n2nconfighash{$n2nkey}[1].p12\n";
			}
			if ($n2nconfighash{$n2nkey}[19] eq 'no'){
				my @tempremotesubnet = split("\/",$n2nconfighash{$n2nkey}[8]);
				print CONF "route $tempremotesubnet[0] $tempremotesubnet[1]\n";
			} else {
				my @tempremotesubnet = split("\/",$n2nconfighash{$n2nkey}[11]);
				print CONF "route $tempremotesubnet[0] $tempremotesubnet[1]\n";
			}
		}
		if ($n2nconfighash{$n2nkey}[26] > 0 && $n2nconfighash{$n2nkey}[27] > 0) {	
			print CONF "keepalive $n2nconfighash{$n2nkey}[26] $n2nconfighash{$n2nkey}[27]\n";
		} else {
			print CONF "keepalive 10 60\n";
		}		
		print CONF "cipher $n2nconfighash{$n2nkey}[20]\n";
		if ($n2nconfighash{$n2nkey}[16] eq 'on') {
			print CONF "comp-lzo\n";		
		}
		if ($n2nconfighash{$n2nkey}[42] ne '') {
			print CONF "verb $n2nconfighash{$n2nkey}[42]\n";
		} else {
			print CONF "verb 3\n";
		}	
		if ($n2nconfighash{$n2nkey}[19] eq 'no'){
			print CONF "#$n2nconfighash{$n2nkey}[11]\n";
		} else {
			print CONF "#$n2nconfighash{$n2nkey}[8]\n";
		}
		if ($zerinaclient ne 'true') {
			print CONF "daemon OVPN_$n2nconfighash{$n2nkey}[1]\n";		
			print CONF "#status ${General::swroot}/ovpn/n2nconf/$n2nconfighash{$n2nkey}[1]/$n2nconfighash{$n2nkey}[1].log 2\n";
		}
		close(CONF);		
		if ($zerinaclient eq 'true') {
			my $zip = Archive::Zip->new();
			$zip->addFile( "${General::swroot}/ovpn/certs/$n2nconfighash{$n2nkey}[1].p12", "$n2nconfighash{$n2nkey}[1].p12") or die "Can't add file ${General::swroot}/ovpn/certs/$n2nconfighash{$n2nkey}[1].p12\n";			
			$zip->addFile( "$tempdir/$clientovpn", $clientovpn) or die "Can't add file $clientovpn\n";
			my $status = $zip->writeToFileNamed($zippathname);
			open(DLFILE, "<$zippathname") or die "Unable to open $zippathname: $!";
			@fileholder = <DLFILE>;
			print "Content-Type:application/x-download\n";
			print "Content-Disposition:attachment;filename=$zipname\n\n";
			print @fileholder;
			exit (0);			
		}		
	}	
}

sub removenet2netconf {
    my %n2nconfighash = ();
    my $key = $_[0];
    my $file = '';
    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%n2nconfighash);
    if ($n2nconfighash{$key}[3] eq 'net') {
		if ( -d "${General::swroot}/ovpn/n2nconf/$n2nconfighash{$key}[1]"){
			while ($file = glob("${General::swroot}/ovpn/n2nconf/$n2nconfighash{$key}[1]/*")) {
				unlink $file
			}
			rmdir("${General::swroot}/ovpn/n2nconf/$n2nconfighash{$key}[1]");
		}	    
    }
}

sub emptyserverlog{    
	if (open(FILE, ">/var/log/ovpnserver.log")) {
	flock FILE, 2;
	print FILE "";
	close FILE;
    }
}

sub displayca {
	my $key = $_[0];
	my %cahash = ();
    &General::readhasharray("${General::swroot}/ovpn/caconfig", \%cahash);
    if ( -f "${General::swroot}/ovpn/ca/$cahash{$key}[0]cert.pem") {
		&Header::showhttpheaders();
		&Header::openpage($Lang::tr{'vpn configuration main'}, 1, '');
		&Header::openbigbox('100%', 'LEFT', '', $errormessage);
		&Header::openbox('100%', 'LEFT', "$Lang::tr{'ca certificate'}:");
		my $output = `/usr/bin/openssl x509 -text -in ${General::swroot}/ovpn/ca/$cahash{$key}[0]cert.pem`;
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
}
sub displayroothost {
	my $roothost = $_[0];
    my $output;
    &Header::showhttpheaders();
    &Header::openpage($Lang::tr{'vpn configuration main'}, 1, '');
    &Header::openbigbox('100%', 'LEFT', '', '');
    if ($roothost eq $Lang::tr{'show root certificate'}) {
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
}

sub killconnection {
	my $key = $_[0];
	my %n2nconfighash = ();
	&General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%n2nconfighash);
	my $n2nactive = `/bin/ps ax|grep $n2nconfighash{$key}[1].conf|grep -v grep|awk \'{print \$1}\'`;
	if ($n2nactive ne ''){				
		system('/usr/local/bin/openvpnctrl', '-kn2n', $n2nactive);
	}						
}

sub cidrormask {
	my $cidrmask = $_[0];
	my $cidrmask2 = $cidrmask;
	if ("/$cidrmask" =~ /^\/(\d+)/){#cidr	                    
		if ($cidrmask2 = &cidr2mask("/$cidrmask")) {
			return $cidrmask2;
		} else {
			if ($cidrmask =~ /^\d+\.\d+\.\d+\.\d+/){#mask		                         
				return $cidrmask;
			}
		}		
	} else {
		if ($cidrmask =~ /^\d+\.\d+\.\d+\.\d+/){#mask		                         
			return $cidrmask;
		}
	}	
}                          
sub cidr2mask {
    my( $cidr ) = @_;
    my( $one32 ) = 0xffffffff;
    my( @d, $n, $bits );

    if ( $cidr eq "/0" ) {
        return "0.0.0.0";
    }

    if ( $cidr !~ /\/(\d+)/ ) {
        return undef;
    }
    $bits = $1;

    if ( $bits > 32 ) {
        return undef;
    }

    #-- convert to subnet-style mask
	$n = $one32 << (32 - $bits);
	$d[3] = $n % 256; $n = int( $n / 256);
	$d[2] = $n % 256; $n = int( $n / 256);
	$d[1] = $n % 256; $n = int( $n / 256);
	$d[0] = $n;
	return join '.', @d;
}


# ----------------------------------------------------------------------------
# $cidr = &mask2cidr( $mask )
# ----------------------------------------------------------------------------

sub mask2cidr {
    my( $mask ) = @_;
    my( @d, $n, $bits );
    
    if ( $mask eq "0.0.0.0" ) {
        return "/0";
    }
    
    if ( ! &validMask( $mask ) ) {
        return undef;
    }

    @d = split /\./, $mask;
    $n = ((((($d[0] * 256) + $d[1])  * 256) + $d[2]) * 256) + $d[3];
    $bits = 32;
    while ( ($n % 2) == 0 ) {
        $n >>= 1;
        $bits -= 1;
    }
    return "/$bits";
}


# ----------------------------------------------------------------------------
# $yesno = &validMask( $mask )
# ----------------------------------------------------------------------------

sub validMask {
    my( $mask ) = @_;
    my( @d, $n, $str );

    @d = split /\./, $mask;
    $n = ((((($d[0] * 256) + $d[1]) * 256) + $d[2]) * 256) + $d[3];
    $str = sprintf "%b", $n;
    return ( $str =~ /^1+0*$/ );
}

sub overlapping {
	# read all subnets from AD, convert to integer range, and sort. 
	foreach $subnet (@subnets2) {
		($from, $to) = &subnet2range ($subnet);
		push @subnets, { cn => $subnet, from => $from, to => $to };
	}
	@subnets = sort { $a->{from} <=> $b->{from} } @subnets;

	# compare all possible subnets for overlap; depend on sort order. 
	for ($i=0; $i<=$#subnets; $i++) {
		for ($j=$i+1; $j<=$#subnets; $j++) {
			last if $subnets[$i]->{to} < $subnets[$j]->{from};    # no possible overlap anymore;
			push @{$overlaps{$subnets[$i]->{cn}}}, $subnets[$j]->{cn} if $subnets[$i]->{to} >= $subnets[$j]->{from};
		}
	}

	if (scalar (keys %overlaps)) {
		foreach $subnet (sort keys %overlaps) {		
			#$errormessage = "$Lang::tr{'ovpn subnet overlap'} IPFire IPSEC  : %s\n", $subnet, join (", ", sort @{$overlaps{$subnet}});			
			$errormessage = "$subnet : $overlaps{$subnet}[0]";
			last;
		}
	}	
		return $errormessage;
}

# &subnet2range ($subnet)
# convert subnets to integers in order to compare them later.
# A subnet looks like this: 10.1.2.0/24
# returns beginning and end of subnet as integer
#
sub subnet2range {
    my $subnet = shift (@_);
    my ($from, $to);
    
    $subnet =~ /^(\d+)\.(\d+)\.(\d+)\.(\d+)\/(\d+)$/ || die "bad subnet $subnet\n";
    $from = $1*2**24 + $2*2**16 + $3*2**8 + $4;
    $to = $from + 2**(32-$5) - 1;
    return ($from, $to);
}

sub ovelapplausi {
	my $tmpovpnsubnet0 = $_[0];
	my $tmpovpnsubnet1 = $_[1];
    my %vpnconfighash = ();
	my $tmpcidr = '';
	my @tmpremotevpnsubnet;
    &General::readhasharray("${General::swroot}/vpn/config", \%vpnconfighash);

    if (&General::IpInSubnet ( $netsettings{'GREEN_ADDRESS'}, 
		$tmpovpnsubnet0, $tmpovpnsubnet1)) {
        $errormessage = "$Lang::tr{'ovpn subnet overlap'} IPFire Green Network $netsettings{'GREEN_ADDRESS'}";
        return $errormessage;
    }

	if (&haveBlueNet()) {
		if (&General::IpInSubnet ( $netsettings{'BLUE_ADDRESS'}, 
			$tmpovpnsubnet0, $tmpovpnsubnet1)) {
			$errormessage = "$Lang::tr{'ovpn subnet overlap'} IPFire Blue Network $netsettings{'BLUE_ADDRESS'}";
			return $errormessage;
		}
	}	
    if (&haveOrangeNet()) {
		if (&General::IpInSubnet ( $netsettings{'ORANGE_ADDRESS'}, 
			$tmpovpnsubnet0, $tmpovpnsubnet1)) {
			$errormessage = "$Lang::tr{'ovpn subnet overlap'} IPFire Orange Network $netsettings{'ORANGE_ADDRESS'}";
			return $errormessage;
		}
	}	
    open(ALIASES, "${General::swroot}/ethernet/aliases") or die 'Unable to open aliases file.';
    while (<ALIASES>)
    {
		chomp($_);
		my @tempalias = split(/\,/,$_);
		if ($tempalias[1] eq 'on') {
			if (&General::IpInSubnet ($tempalias[0] , 
				$tmpovpnsubnet0, $tmpovpnsubnet1)) {
				$errormessage = "$Lang::tr{'ovpn subnet overlap'} IPFire alias entry $tempalias[0]";
				exit $errormessage;
			}		
		}
    }
	close(ALIASES);
	
	#check against ipsec connections
	foreach my $key (keys %vpnconfighash) {
		#$confighash{$key}[8] = $cgiparams{'LOCAL_SUBNET'};
		#$confighash{$key}[3]#host or net
		#$confighash{$key}[11] = $cgiparams{'REMOTE_SUBNET'};
		#$confighash{$key}[10] = $cgiparams{'REMOTE'};
		&emptyarray();
		$tmpcidr = &mask2cidr($tmpovpnsubnet1);
		push @subnets2, "$tmpovpnsubnet0$tmpcidr";		
		@tmpremotevpnsubnet = split("\/",$vpnconfighash{$key}[8]);			
		$tmpcidr = &mask2cidr($tmpremotevpnsubnet[1]);
		push @subnets2, "$tmpremotevpnsubnet[0]$tmpcidr";			
		$errormessage2 = &overlapping();
		if ($errormessage2 ne '') {
			$errormessage = "$Lang::tr{'ovpn subnet overlap'}IPSCEC Connection=$vpnconfighash{$key}[1] $Lang::tr{'local subnet'} $errormessage2 ";
			last;
		}
		&emptyarray();
		if ($vpnconfighash{$key}[3] eq 'net'){
			if (&General::IpInSubnet ($vpnconfighash{$key}[10],$tmpovpnsubnet0, $tmpovpnsubnet1)) {
				$errormessage = "$Lang::tr{'ovpn subnet overlap'} IPFire IPSEC Connection/IP: $vpnconfighash{$key}[1]/$vpnconfighash{$key}[10]";
				last;				
			}
			#check agains ipsec local subent			
			push @subnets2, "$tmpovpnsubnet0$tmpcidr";
			@tmpremotevpnsubnet = split("\/",$vpnconfighash{$key}[11]);			
			$tmpcidr = &mask2cidr($tmpremotevpnsubnet[1]);
			push @subnets2, "$tmpremotevpnsubnet[0]$tmpcidr";			
			$errormessage2 = &overlapping();
			if ($errormessage2 ne '') {
				$errormessage = "$Lang::tr{'ovpn subnet overlap'}IPSCEC Connection=$vpnconfighash{$key}[1] $Lang::tr{'remote subnet'} $errormessage2 ";
				last;
			}	
			&emptyarray();
			push @subnets2, "$tmpovpnsubnet0$tmpcidr";
			@tmpremotevpnsubnet = split("\/",$vpnconfighash{$key}[8]);			
			$tmpcidr = &mask2cidr($tmpremotevpnsubnet[1]);
			push @subnets2, "$tmpremotevpnsubnet[0]$tmpcidr";			
			$errormessage2 = &overlapping();
			if ($errormessage2 ne '') {
				$errormessage = "$Lang::tr{'ovpn subnet overlap'}IPSCEC Connection=$vpnconfighash{$key}[1] $Lang::tr{'local subnet'} $errormessage2 ";
				last;
			}
			&emptyarray();			
		}		
	}
	#check against OpenVPN Connections (aware check against itself)
	return $errormessage;
}
sub emptyarray {
	@subnets2 = ();
	@subnets = ();
}
sub rwclientstatus {
	my $activeonrun = $_[0];
	my @status = `/bin/cat /var/log/ovpnserver.log`;
	my %confighash = ();
	my $dis = ''
	&General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
	if ( -f "${General::swroot}/ovpn/ca/cacert.pem" ) {
		$dis = '';
	} else {
		$dis = "disabled='disabled'";
	}	
		
		&Header::openbox('100%', 'LEFT', "Roadwarrior $Lang::tr{'Client status and controlc'}");
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
			if ($confighash{$key}[3] eq 'host') {
				if ($confighash{$key}[0] eq 'on') { $gif = 'on.gif'; } else { $gif = 'off.gif'; }
					if ($id % 2) {
						print "<tr bgcolor='${Header::table1colour}'>\n";
					} else {
						print "<tr bgcolor='${Header::table2colour}'>\n";
					}
				print "<td align='center' nowrap='nowrap'>$confighash{$key}[1]</td>";		
				print "<td align='center' nowrap='nowrap'>" . $Lang::tr{"$confighash{$key}[3]"} . " (" . $Lang::tr{"$confighash{$key}[4]"} . ")</td>";			
				if ($confighash{$key}[4] eq 'cert') {
					print "<td align='left' nowrap='nowrap'>$confighash{$key}[2]</td>";
				} else {
					print "<td align='left'>&nbsp;</td>";
				}
				if ($confighash{$key}[19] ne 'yes') {
					my $cavalid = `/usr/bin/openssl x509 -text -in ${General::swroot}/ovpn/certs/$confighash{$key}[1]cert.pem`;
					$cavalid    =~ /Not After : (.*)[\n]/;
					$cavalid    = $1;
					print "<td align='center'>$cavalid</td>";
				} else {
					print "<td>&nbsp;</td>";
				}	
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
				print "<td align='center'>$active</td>";
				my $disable_clientdl = "";
				if ($confighash{$key}[6] ne 'client') {			
					print <<END		
					<form method='post' name='frm${key}a'><td align='center'>
					<input type='image'  name='$Lang::tr{'dl client arch'}' $disable_clientdl src='/images/openvpn.gif' alt='$Lang::tr{'dl client arch'}' title='$Lang::tr{'dl client arch'}' border='0' />
					<input type='hidden' name='ACTION' value='$Lang::tr{'dl client arch'}' $disable_clientdl />
					<input type='hidden' name='KEY' value='$key' $disable_clientdl />
					</td></form>
END
		;		} else {
					print "<td>&nbsp;</td>";	
				}	
				if ($confighash{$key}[4] eq 'cert' && $confighash{$key}[19] ne 'yes') {
					print <<END
					<form method='post' name='frm${key}b'><td align='center'>
					<input type='image' name='$Lang::tr{'show certificate'}' src='/images/info.gif' alt='$Lang::tr{'show certificate'}' title='$Lang::tr{'show certificate'}' border='0' />
					<input type='hidden' name='ACTION' value='$Lang::tr{'show certificate'}' />
					<input type='hidden' name='KEY' value='$key' />
					</td></form>
END
		; 		} else {
					print "<td>&nbsp;</td>";
				}
				if ($confighash{$key}[4] eq 'cert' && -f "${General::swroot}/ovpn/certs/$confighash{$key}[1].p12") { 
					print <<END
					<form method='post' name='frm${key}c'><td align='center'>
					<input type='image' name='$Lang::tr{'download pkcs12 file'}' src='/images/floppy.gif' alt='$Lang::tr{'download pkcs12 file'}' title='$Lang::tr{'download pkcs12 file'}' border='0' />
					<input type='hidden' name='ACTION' value='$Lang::tr{'download pkcs12 file'}' />
					<input type='hidden' name='KEY' value='$key' />
					</td></form>
END
		; 		} elsif ($confighash{$key}[4] eq 'cert' && $confighash{$key}[19] ne 'yes') {
					print <<END
					<form method='post' name='frm${key}c'><td align='center'>
					<input type='image' name='$Lang::tr{'download certificate'}' src='/images/floppy.gif' alt='$Lang::tr{'download certificate'}' title='$Lang::tr{'download certificate'}' border='0' />
					<input type='hidden' name='ACTION' value='$Lang::tr{'download certificate'}' />
					<input type='hidden' name='KEY' value='$key' />
					</td></form>
END
		; 		} else {
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
			<td>&nbsp; &nbsp; <img src='/images/floppy.gif' alt='?FLOPPY' /></td>
			<td class='base'>$Lang::tr{'download certificate'}</td>
			<td>&nbsp; &nbsp; <img src='/images/openvpn.gif' alt='?RELOAD'/></td>
			<td class='base'>$Lang::tr{'dl client arch'}</td>
			</tr>
			</table>
END
	    ;
	    }
	    print <<END
	    <table width='100%'>
	    <form method='post'>
	    <tr><td width='50%' ><input type='submit' name='ACTION' value='$Lang::tr{'add'}' $dis />
				             <input type='hidden' name='TYPE' value='host' /></td>				
	    	<td width='50%' ><input type='submit' name='ACTION' value='$Lang::tr{'ovpn con stat'}' $activeonrun /></td></tr>
	    </form>
	    </table>
END
	    ;    
	    &Header::closebox();
	#}
}
sub net2netstatus {
#net2net connections
	my $activeonrun = $_[0];
	my @status = `/bin/cat /var/log/ovpnserver.log`;
	my %confighash = ();
	my $dis = ''
	&General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
	if ( -f "${General::swroot}/ovpn/ca/cacert.pem" ) {
		$dis = '';
	} else {
		$dis = "disabled='disabled'";
	}
		&Header::openbox('100%', 'LEFT', "Net to Net Connection status and control:");
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
			if ($confighash{$key}[3] eq 'net') {
				if ($confighash{$key}[0] eq 'on') { $gif = 'on.gif'; } else { $gif = 'off.gif'; }
				if ($id % 2) {
					print "<tr bgcolor='${Header::table1colour}'>\n";
				} else {
					print "<tr bgcolor='${Header::table2colour}'>\n";
				}
				print "<td align='center' nowrap='nowrap'>$confighash{$key}[1]</td>";
				print "<td align='center' nowrap='nowrap'>" . $confighash{$key}[6] . "-" . $Lang::tr{"$confighash{$key}[3]"} . " (" . $Lang::tr{"$confighash{$key}[4]"} . ")</td>";		
				if ($confighash{$key}[4] eq 'cert') {
					print "<td align='left' nowrap='nowrap'>$confighash{$key}[2]</td>";
				} else {
					print "<td align='left'>&nbsp;</td>";
				}
				if ($confighash{$key}[19] ne 'yes') {
					my $cavalid = `/usr/bin/openssl x509 -text -in ${General::swroot}/ovpn/certs/$confighash{$key}[1]cert.pem`;
					$cavalid    =~ /Not After : (.*)[\n]/;
					$cavalid    = $1;
					print "<td align='center'>$cavalid</td>";
				} else {
					print "<td>&nbsp;</td>";
				}	
				print "<td align='center'>$confighash{$key}[25]</td>";
				my $active = "<table cellpadding='2' cellspacing='0' bgcolor='${Header::colourred}' width='100%'><tr><td align='center'><b><font color='#FFFFFF'>$Lang::tr{'capsclosed'}</font></b></td></tr></table>";
				if ($confighash{$key}[0] eq 'off') {
					$active = "<table cellpadding='2' cellspacing='0' bgcolor='${Header::colourblue}' width='100%'><tr><td align='center'><b><font color='#FFFFFF'>$Lang::tr{'capsclosed'}</font></b></td></tr></table>";
				} else {
					my @tempovpnsubnet = split("\/",$confighash{$key}[13]);
					my @ovpnip = split /\./,$tempovpnsubnet[0];
					my $pingip = "";
					if ($confighash{$key}[6] eq 'server') {
						$pingip = "$ovpnip[0].$ovpnip[1].$ovpnip[2].2";
					} else {
						$pingip = "$ovpnip[0].$ovpnip[1].$ovpnip[2].1";
					}
					my $p = Net::Ping->new("udp",1);
					if ($p->ping($pingip)) {
						$active = "<table cellpadding='2' cellspacing='0' bgcolor='${Header::colourgreen}' width='100%'><tr><td align='center'><b><font color='#FFFFFF'>$Lang::tr{'capsopen'}</font></b></td></tr></table>";
					}	
					$p->close();				
				}				
				print "<td align='center'>$active</td>";
				my $disable_clientdl = "";
				if ($confighash{$key}[6] ne 'client') {			
					print <<END		
					<form method='post' name='frm${key}a'><td align='center'>
					<input type='image'  name='$Lang::tr{'dl client arch'}' $disable_clientdl src='/images/openvpn.gif' alt='$Lang::tr{'dl client arch'}' title='$Lang::tr{'dl client arch'}' border='0' />
					<input type='hidden' name='ACTION' value='$Lang::tr{'dl client arch'}' $disable_clientdl />
					<input type='hidden' name='KEY' value='$key' $disable_clientdl />
					</td></form>
END
					;		} else {
					print "<td>&nbsp;</td>";	
				}	
				if ($confighash{$key}[4] eq 'cert' && $confighash{$key}[19] ne 'yes') {
					print <<END
					<form method='post' name='frm${key}b'><td align='center'>
					<input type='image' name='$Lang::tr{'show certificate'}' src='/images/info.gif' alt='$Lang::tr{'show certificate'}' title='$Lang::tr{'show certificate'}' border='0' />
					<input type='hidden' name='ACTION' value='$Lang::tr{'show certificate'}' />
					<input type='hidden' name='KEY' value='$key' />
					</td></form>
END
					; 		} else {
					print "<td>&nbsp;</td>";
				}
				if ($confighash{$key}[4] eq 'cert' && -f "${General::swroot}/ovpn/certs/$confighash{$key}[1].p12") { 
					print <<END
					<form method='post' name='frm${key}c'><td align='center'>
					<input type='image' name='$Lang::tr{'download pkcs12 file'}' src='/images/floppy.gif' alt='$Lang::tr{'download pkcs12 file'}' title='$Lang::tr{'download pkcs12 file'}' border='0' />
					<input type='hidden' name='ACTION' value='$Lang::tr{'download pkcs12 file'}' />
					<input type='hidden' name='KEY' value='$key' />
					</td></form>
END
					; 		} elsif ($confighash{$key}[4] eq 'cert' && $confighash{$key}[19] ne 'yes') {
					print <<END
					<form method='post' name='frm${key}c'><td align='center'>
					<input type='image' name='$Lang::tr{'download certificate'}' src='/images/floppy.gif' alt='$Lang::tr{'download certificate'}' title='$Lang::tr{'download certificate'}' border='0' />
					<input type='hidden' name='ACTION' value='$Lang::tr{'download certificate'}' />
					<input type='hidden' name='KEY' value='$key' />
					</td></form>
END
					; 		} else {
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
			<td>&nbsp; &nbsp; <img src='/images/floppy.gif' alt='?FLOPPY' /></td>
			<td class='base'>$Lang::tr{'download certificate'}</td>
			<td>&nbsp; &nbsp; <img src='/images/openvpn.gif' alt='?RELOAD'/></td>
			<td class='base'>$Lang::tr{'dl client arch'}</td>
			</tr>
			</table>
END
			;
		}
		print <<END
		<table width='100%'>
		<form method='post'>
		<tr><td width='50%' ><input type='submit' name='ACTION' value='$Lang::tr{'add'}' $ dis /></td></tr>    	
		</form>
		</table>
END
		;    
		&Header::closebox();
	#}	
#net2net connections
}
