#!/usr/bin/perl
#
# This file is part of the IPFire Firewall.
#
# IPFire is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# IPFire is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with IPFire; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# Copyright (C) 2003-05-25 Mark Wormgoor <mark@wormgoor.com>
#
# $Id: vpnmain.cgi,v 1.10.2.69 2006/01/31 02:07:19 franck78 Exp $
#

use Net::DNS;
use File::Copy;
use File::Temp qw/ tempfile tempdir /;
use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

require "${General::swroot}/countries.pl";

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::colourgreen} );
undef (@dummy);

###
### Initialize variables
###
my $sleepDelay = '4s';	# after a call to ipsecctrl S or R, wait this delay (seconds) before reading status
			# (let the ipsec do its job)
my %netsettings=();
my %cgiparams=();
my %vpnsettings=();
my %checked=();
my %confighash=();
my %cahash=();
my %selected=();
my $warnmessage = '';
my $errormessage = '';
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
$cgiparams{'ENABLED'} = 'off';
$cgiparams{'ENABLED_BLUE'} = 'off';
$cgiparams{'EDIT_ADVANCED'} = 'off';
$cgiparams{'NAT'} = 'off';
$cgiparams{'COMPRESSION'} = 'off';
$cgiparams{'ONLY_PROPOSED'} = 'off';
$cgiparams{'ACTION'} = '';
$cgiparams{'CA_NAME'} = '';
$cgiparams{'DBG_CRYPT'} = '';
$cgiparams{'DBG_PARSING'} = '';
$cgiparams{'DBG_EMITTING'} = '';
$cgiparams{'DBG_CONTROL'} = '';
$cgiparams{'DBG_KLIPS'} = '';
$cgiparams{'DBG_DNS'} = '';
$cgiparams{'DBG_NAT_T'} = '';

&Header::getcgihash(\%cgiparams, {'wantfile' => 1, 'filevar' => 'FH'});

###
### Useful functions
###
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

#
# old version: maintain serial number to one, without explication. 
# this	     : let the counter go, so that each cert is numbered.
#
sub cleanssldatabase
{
    if (open(FILE, ">${General::swroot}/certs/serial")) {
	print FILE "01";
	close FILE;
    }
    if (open(FILE, ">${General::swroot}/certs/index.txt")) {
	print FILE "";
	close FILE;
    }
    unlink ("${General::swroot}/certs/index.txt.old");
    unlink ("${General::swroot}/certs/serial.old");
    unlink ("${General::swroot}/certs/01.pem");
}
sub newcleanssldatabase
{
    if (! -s "${General::swroot}/certs/serial" )  {
        open(FILE, ">${General::swroot}/certs/serial");
	print FILE "01";
	close FILE;
    }
    if (! -s ">${General::swroot}/certs/index.txt") {
	system ("touch ${General::swroot}/certs/index.txt");
    }
    unlink ("${General::swroot}/certs/index.txt.old");
    unlink ("${General::swroot}/certs/serial.old");
#   unlink ("${General::swroot}/certs/01.pem");		numbering evolves. Wrong place to delete
}
							    
sub writeipsecfiles {
    my %lconfighash = ();
    my %lvpnsettings = ();
    &General::readhasharray("${General::swroot}/vpn/config", \%lconfighash);
    &General::readhash("${General::swroot}/vpn/settings", \%lvpnsettings);

    open(CONF,    ">${General::swroot}/vpn/ipsec.conf") or die "Unable to open ${General::swroot}/vpn/ipsec.conf: $!";
    open(SECRETS, ">${General::swroot}/vpn/ipsec.secrets") or die "Unable to open ${General::swroot}/vpn/ipsec.secrets: $!";
    flock CONF, 2;
    flock SECRETS, 2;
    print CONF "config setup\n";
    if ($lvpnsettings{'ENABLED_BLUE'} eq 'on')
    {
	if ($lvpnsettings{'ENABLED'} eq 'on')
	{
		print CONF "\tinterfaces=\"%defaultroute ipsec1=$netsettings{'BLUE_DEV'}\"\n";
	} else {
		print CONF "\tinterfaces=ipsec0=$netsettings{'BLUE_DEV'}\n";
	}
    } else {
	print CONF "\tinterfaces=%defaultroute\n";
    }
    
    my $plutodebug = '';			# build debug list
    map ($plutodebug .= $lvpnsettings{$_} eq 'on' ? lc (substr($_,4)).' ' : '',
	('DBG_CRYPT','DBG_PARSING','DBG_EMITTING','DBG_CONTROL',
	 'DBG_KLIPS','DBG_DNS','DBG_NAT_T'));
    $plutodebug = 'none' if $plutodebug eq '';  # if nothing selected, use 'none'.
    print CONF "\tklipsdebug=none\n";
    print CONF "\tplutodebug=\"$plutodebug\"\n";
    print CONF "\tplutoload=%search\n";
    print CONF "\tplutostart=%search\n";
    print CONF "\tuniqueids=yes\n";
    print CONF "\tnat_traversal=yes\n";
    print CONF "\toverridemtu=$lvpnsettings{'VPN_OVERRIDE_MTU'}\n" if ($lvpnsettings{'VPN_OVERRIDE_MTU'} ne '');
    print CONF "\tvirtual_private=%v4:10.0.0.0/8,%v4:172.16.0.0/12,%v4:192.168.0.0/16";
    print CONF ",%v4:!$netsettings{'GREEN_NETADDRESS'}/$netsettings{'GREEN_NETMASK'}";
    if (length($netsettings{'ORANGE_DEV'}) > 2) {
	print CONF ",%v4:!$netsettings{'ORANGE_NETADDRESS'}/$netsettings{'ORANGE_NETMASK'}";
    }
    if (length($netsettings{'BLUE_DEV'}) > 2) {
	print CONF ",%v4:!$netsettings{'BLUE_NETADDRESS'}/$netsettings{'BLUE_NETMASK'}";
    }
    foreach my $key (keys %lconfighash) {
	if ($lconfighash{$key}[3] eq 'net') {
	    print CONF ",%v4:!$lconfighash{$key}[11]";
	}
    }
    print CONF "\n\n";
    print CONF "conn %default\n";
    print CONF "\tkeyingtries=0\n";
    print CONF "\tdisablearrivalcheck=no\n";
    print CONF "\n";

    if (-f "${General::swroot}/certs/hostkey.pem") {
        print SECRETS ": RSA ${General::swroot}/certs/hostkey.pem\n"
    }

    foreach my $key (keys %lconfighash) {
	if ($lconfighash{$key}[0] eq 'on') {
	    if ($lconfighash{$key}[10] eq '') { $lconfighash{$key}[10] = '%any'; }

	    print CONF "conn $lconfighash{$key}[1]\n";
	    #always choose LEFT localside for roadwarrior
	    if ($lconfighash{$key}[3] eq 'host' || $lconfighash{$key}[6] eq 'left') {
		if ($lconfighash{$key}[26] eq 'BLUE')
		{
		    print CONF "\tleft=$netsettings{'BLUE_ADDRESS'}\n";
#		    print CONF "\tleftnexthop=$netsettings{'BLUE_NETADDRESS'}\n";
		} 
		elsif ($lconfighash{$key}[26] eq 'ORANGE')
		{
		    print CONF "\tleft=$netsettings{'ORANGE_ADDRESS'}\n";
		} 
		elsif ($lconfighash{$key}[26] eq 'GREEN')
		{
		    print CONF "\tleft=$netsettings{'GREEN_ADDRESS'}\n";
		} 
		elsif ($lconfighash{$key}[26] eq 'RED')
		{
		    print CONF "\tleft=$lvpnsettings{'VPN_IP'}\n";
		    print CONF "\tleftnexthop=%defaultroute\n" if ($lvpnsettings{'VPN_IP'} ne '%defaultroute');
		}
		print CONF "\tleftsubnet=$lconfighash{$key}[8]\n";
		print CONF "\tright=$lconfighash{$key}[10]\n";
		if ($lconfighash{$key}[3] eq 'net') {
		    print CONF "\trightsubnet=$lconfighash{$key}[11]\n";
		    print CONF "\trightnexthop=%defaultroute\n";
		} elsif ($lconfighash{$key}[10] eq '%any' && $lconfighash{$key}[14] eq 'on') {
		    print CONF "\trightsubnet=vhost:%no,%priv\n";
		}
		if ($lconfighash{$key}[4] eq 'cert') {
		    print CONF "\tleftcert=${General::swroot}/certs/hostcert.pem\n";
		    print CONF "\trightcert=${General::swroot}/certs/$lconfighash{$key}[1]cert.pem\n";
		}
	    } else {
		print CONF "\tright=$lvpnsettings{'VPN_IP'}\n";
		print CONF "\trightsubnet=$lconfighash{$key}[8]\n";
		print CONF "\trightnexthop=%defaultroute\n"  if ($lvpnsettings{'VPN_IP'} ne '%defaultroute');
		print CONF "\tleft=$lconfighash{$key}[10]\n";
		if ($lconfighash{$key}[3] eq 'net') {
		    print CONF "\tleftsubnet=$lconfighash{$key}[11]\n";
		    print CONF "\tleftnexthop=%defaultroute\n";
		}
		if ($lconfighash{$key}[4] eq 'cert') {
		    print CONF "\trightcert=${General::swroot}/certs/hostcert.pem\n";
		    print CONF "\tleftcert=${General::swroot}/certs/$lconfighash{$key}[1]cert.pem\n";
		}
	    }
	    print CONF "\tleftid=$lconfighash{$key}[7]\n" if ($lconfighash{$key}[7]);
	    print CONF "\trightid=$lconfighash{$key}[9]\n" if ($lconfighash{$key}[9]);

	    # Algorithms
	    if ($lconfighash{$key}[18] && $lconfighash{$key}[19] && $lconfighash{$key}[20]) {
		print CONF "\tike=";
		my @encs   = split('\|', $lconfighash{$key}[18]);
		my @ints   = split('\|', $lconfighash{$key}[19]);
		my @groups = split('\|', $lconfighash{$key}[20]);
		my $comma = 0;
		foreach my $i (@encs) {
		    foreach my $j (@ints) {
			foreach my $k (@groups) {
			    if ($comma != 0) { print CONF ","; } else { $comma = 1; }
			    print CONF "$i-$j-modp$k";
			}
		    }
		}
		if ($lconfighash{$key}[24] eq 'on') {
		    print CONF "!\n";
		} else {
		    print CONF "\n";
		}
	    }
	    if ($lconfighash{$key}[21] && $lconfighash{$key}[22]) {
		print CONF "\tesp=";
		my @encs   = split('\|', $lconfighash{$key}[21]);
		my @ints   = split('\|', $lconfighash{$key}[22]);
		my $comma = 0;
		foreach my $i (@encs) {
		    foreach my $j (@ints) {
			if ($comma != 0) { print CONF ","; } else { $comma = 1; }
			print CONF "$i-$j";
		    }
		}
		if ($lconfighash{$key}[24] eq 'on') {
		    print CONF "!\n";
		} else {
		    print CONF "\n";
		}
	    }
	    if ($lconfighash{$key}[23]) {
		print CONF "\tpfsgroup=$lconfighash{$key}[23]\n";
	    }

	    # Lifetimes
	    if ($lconfighash{$key}[16]) {
		print CONF "\tikelifetime=$lconfighash{$key}[16]h\n";
	    }
	    if ($lconfighash{$key}[17]) {
		print CONF "\tkeylife=$lconfighash{$key}[17]h\n";
	    }

	    # Compression
	    if ($lconfighash{$key}[13] eq 'on') {
		print CONF "\tcompress=yes\n";
	    }

	    # Dead Peer Detection
	    print CONF "\tdpddelay=30\n";
	    print CONF "\tdpdtimeout=120\n";
	    print CONF "\tdpdaction=$lconfighash{$key}[27]\n";
	    
	    # Disable pfs ?
	    print CONF "\tpfs=$lconfighash{$key}[28]\n";

	    # Print Authentication details
	    if ($lconfighash{$key}[4] eq 'psk') {
		if ($lconfighash{$key}[6] eq 'left'){
		    if ($lconfighash{$key}[26] eq 'BLUE') {
		        print SECRETS ($lconfighash{$key}[7] ? $lconfighash{$key}[7] : $netsettings{'BLUE_ADDRESS'}) . " ";
		        print SECRETS $lconfighash{$key}[9] ? $lconfighash{$key}[9] : $lconfighash{$key}[10];
			print SECRETS " : PSK \"$lconfighash{$key}[5]\"\n";
		    } else {
			print SECRETS ($lconfighash{$key}[7] ? $lconfighash{$key}[7] : $lvpnsettings{'VPN_IP'}) . " ";
		        print SECRETS $lconfighash{$key}[9] ? $lconfighash{$key}[9] : $lconfighash{$key}[10];
			print SECRETS " : PSK \"$lconfighash{$key}[5]\"\n";
		    }
		} else {
		    if ($lconfighash{$key}[26] eq 'BLUE') {
		        print SECRETS ($lconfighash{$key}[9] ? $lconfighash{$key}[9] : $netsettings{'BLUE_ADDRESS'}) . " ";
		        print SECRETS $lconfighash{$key}[7] ? $lconfighash{$key}[7] : $lconfighash{$key}[10];
			print SECRETS " : PSK \"$lconfighash{$key}[5]\"\n";
		    } else {
			print SECRETS ($lconfighash{$key}[9] ? $lconfighash{$key}[9] : $lvpnsettings{'VPN_IP'}) . " ";
		        print SECRETS $lconfighash{$key}[7] ? $lconfighash{$key}[7] : $lconfighash{$key}[10];
			print SECRETS " : PSK \"$lconfighash{$key}[5]\"\n";
		    }
		}

		print CONF "\tauthby=secret\n";
	    } else {
		print CONF "\tauthby=rsasig\n";
	    }

	    # Automatically start only if a net-to-net connection
	    if ($lconfighash{$key}[3] eq 'host') {
		print CONF "\tauto=add\n";
	    } else {
		print CONF "\tauto=start\n";
	    }
	    print CONF "\n";
	}#on
    }#foreach key

    close(CONF);
    close(SECRETS);
}

###
### Save main settings
###
if ($cgiparams{'ACTION'} eq $Lang::tr{'save'} && $cgiparams{'TYPE'} eq '' && $cgiparams{'KEY'} eq '') {
    &General::readhash("${General::swroot}/vpn/settings", \%vpnsettings);
    unless (&General::validfqdn($cgiparams{'VPN_IP'}) || &General::validip($cgiparams{'VPN_IP'})
	    || $cgiparams{'VPN_IP'} eq '%defaultroute' ) {
	$errormessage = $Lang::tr{'invalid input for hostname'};
	goto SAVE_ERROR;
    }

    unless ($cgiparams{'VPN_DELAYED_START'} =~ /^[0-9]{1,3}$/ ) { #allow 0-999 seconds !
	$errormessage = $Lang::tr{'invalid time period'};
	goto SAVE_ERROR;
    }

    unless ($cgiparams{'VPN_OVERRIDE_MTU'} =~ /^(|[0-9]{1,5})$/ ) { #allow 0-99999
	$errormessage = $Lang::tr{'vpn mtu invalid'};
	goto SAVE_ERROR;
    }

    map ($vpnsettings{$_} = $cgiparams{$_},
	('ENABLED','ENABLED_BLUE','DBG_CRYPT','DBG_PARSING','DBG_EMITTING','DBG_CONTROL',
	 'DBG_KLIPS','DBG_DNS','DBG_NAT_T'));

    $vpnsettings{'VPN_IP'} = $cgiparams{'VPN_IP'};
    $vpnsettings{'VPN_DELAYED_START'} = $cgiparams{'VPN_DELAYED_START'};
    $vpnsettings{'VPN_OVERRIDE_MTU'} = $cgiparams{'VPN_OVERRIDE_MTU'};
    &General::writehash("${General::swroot}/vpn/settings", \%vpnsettings);
    &writeipsecfiles();
    if ($vpnsettings{'ENABLED'} eq 'on' ||
	$vpnsettings{'ENABLED_BLUE'} eq 'on') {
	system('/usr/local/bin/ipsecctrl', 'S');
    } else {
	system('/usr/local/bin/ipsecctrl', 'D');
    }
    sleep $sleepDelay;
    SAVE_ERROR:
###
### Reset all step 2
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'reset'} && $cgiparams{'AREUSURE'} eq 'yes') {
    my $file = '';
    &General::readhasharray("${General::swroot}/vpn/config", \%confighash);

    foreach my $key (keys %confighash) {
	if ($confighash{$key}[4] eq 'cert') {
	    delete $confighash{$key};
	}
    }
    while ($file = glob("${General::swroot}/{ca,certs,crls,private}/*")) {
	unlink $file
    }
    &cleanssldatabase();
    if (open(FILE, ">${General::swroot}/vpn/caconfig")) {
        print FILE "";
        close FILE;
    }
    &General::writehasharray("${General::swroot}/vpn/config", \%confighash);
    &writeipsecfiles();
    system('/usr/local/bin/ipsecctrl', 'R');
    sleep $sleepDelay;

###
### Reset all step 1
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'reset'}) {
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
    &General::readhasharray("${General::swroot}/vpn/caconfig", \%cahash);

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
	move($filename, "${General::swroot}/ca/$cgiparams{'CA_NAME'}cert.pem");
	if ($? ne 0) {
	    $errormessage = "$Lang::tr{'certificate file move failed'}: $!";
	    unlink ($filename);
	    goto UPLOADCA_ERROR;
	}
    }

    my $casubject = `/usr/bin/openssl x509 -text -in ${General::swroot}/ca/$cgiparams{'CA_NAME'}cert.pem`;
    $casubject    =~ /Subject: (.*)[\n]/;
    $casubject    = $1;
    $casubject    =~ s+/Email+, E+;
    $casubject    =~ s/ ST=/ S=/;
    $casubject    = &Header::cleanhtml($casubject);

    my $key = &General::findhasharraykey (\%cahash);
    $cahash{$key}[0] = $cgiparams{'CA_NAME'};
    $cahash{$key}[1] = $casubject;
    &General::writehasharray("${General::swroot}/vpn/caconfig", \%cahash);
    system('/usr/local/bin/ipsecctrl', 'R');
    sleep $sleepDelay;

    UPLOADCA_ERROR:

###
### Display ca certificate
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'show ca certificate'}) {
    &General::readhasharray("${General::swroot}/vpn/caconfig", \%cahash);

    if ( -f "${General::swroot}/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem") {
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'vpn configuration main'}, 1, '');
	&Header::openbigbox('100%', 'LEFT', '', '');
	&Header::openbox('100%', 'LEFT', "$Lang::tr{'ca certificate'}:");
	my $output = `/usr/bin/openssl x509 -text -in ${General::swroot}/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem`;
	$output = &Header::cleanhtml($output,"y");
	print "<pre>$output</pre>\n";
	&Header::closebox();
	print "<div align='center'><a href='/cgi-bin/vpnmain.cgi'>$Lang::tr{'back'}</a></div>";
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
    &General::readhasharray("${General::swroot}/vpn/caconfig", \%cahash);

    if ( -f "${General::swroot}/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem" ) {
	print "Content-Type: application/octet-stream\r\n";
	print "Content-Disposition: filename=$cahash{$cgiparams{'KEY'}}[0]cert.pem\r\n\r\n";
	print `/usr/bin/openssl x509 -in ${General::swroot}/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem`;
	exit(0);
    } else {
	$errormessage = $Lang::tr{'invalid key'};
    }

###
### Remove ca certificate (step 2)
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'remove ca certificate'} && $cgiparams{'AREUSURE'} eq 'yes') {
    &General::readhasharray("${General::swroot}/vpn/config", \%confighash);
    &General::readhasharray("${General::swroot}/vpn/caconfig", \%cahash);

    if ( -f "${General::swroot}/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem" ) {
	foreach my $key (keys %confighash) {
	    my $test = `/usr/bin/openssl verify -CAfile ${General::swroot}/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem ${General::swroot}/certs/$confighash{$key}[1]cert.pem`;
	    if ($test =~ /: OK/) {
		# Delete connection
		if ($vpnsettings{'ENABLED'} eq 'on' ||
		    $vpnsettings{'ENABLED_BLUE'} eq 'on') {
		    system('/usr/local/bin/ipsecctrl', 'D', $key);
		}
		unlink ("${General::swroot}/certs/$confighash{$key}[1]cert.pem");
		unlink ("${General::swroot}/certs/$confighash{$key}[1].p12");
		delete $confighash{$key};
		&General::writehasharray("${General::swroot}/vpn/config", \%confighash);
		&writeipsecfiles();
	    }
	}
	unlink ("${General::swroot}/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem");
	delete $cahash{$cgiparams{'KEY'}};
	&General::writehasharray("${General::swroot}/vpn/caconfig", \%cahash);
	system('/usr/local/bin/ipsecctrl', 'R');
	sleep $sleepDelay;
    } else {
	$errormessage = $Lang::tr{'invalid key'};
    }
###
### Remove ca certificate (step 1)
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'remove ca certificate'}) {
    &General::readhasharray("${General::swroot}/vpn/config", \%confighash);
    &General::readhasharray("${General::swroot}/vpn/caconfig", \%cahash);

    my $assignedcerts = 0;
    if ( -f "${General::swroot}/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem" ) {
	foreach my $key (keys %confighash) {
	    my $test = `/usr/bin/openssl verify -CAfile ${General::swroot}/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem ${General::swroot}/certs/$confighash{$key}[1]cert.pem`;
	    if ($test =~ /: OK/) {
		$assignedcerts++;
	    }
	}
	if ($assignedcerts) {
	    &Header::showhttpheaders();
	    &Header::openpage($Lang::tr{'vpn configuration main'}, 1, '');
	    &Header::openbigbox('100%', 'LEFT', '', '');
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
	    unlink ("${General::swroot}/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem");
	    delete $cahash{$cgiparams{'KEY'}};
	    &General::writehasharray("${General::swroot}/vpn/caconfig", \%cahash);
	    system('/usr/local/bin/ipsecctrl', 'R');
	    sleep $sleepDelay;
	}
    } else {
	$errormessage = $Lang::tr{'invalid key'};
    }

###
### Display root certificate
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'show root certificate'} ||
	$cgiparams{'ACTION'} eq $Lang::tr{'show host certificate'}) {
    my $output;
    &Header::showhttpheaders();
    &Header::openpage($Lang::tr{'vpn configuration main'}, 1, '');
    &Header::openbigbox('100%', 'LEFT', '', '');
    if ($cgiparams{'ACTION'} eq $Lang::tr{'show root certificate'}) {
	&Header::openbox('100%', 'LEFT', "$Lang::tr{'root certificate'}:");
	$output = `/usr/bin/openssl x509 -text -in ${General::swroot}/ca/cacert.pem`;
    } else {
	&Header::openbox('100%', 'LEFT', "$Lang::tr{'host certificate'}:");
	$output = `/usr/bin/openssl x509 -text -in ${General::swroot}/certs/hostcert.pem`;
    }
    $output = &Header::cleanhtml($output,"y");
    print "<pre>$output</pre>\n";
    &Header::closebox();
    print "<div align='center'><a href='/cgi-bin/vpnmain.cgi'>$Lang::tr{'back'}</a></div>";
    &Header::closebigbox();
    &Header::closepage();
    exit(0);

###
### Download root certificate
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'download root certificate'}) {
    if ( -f "${General::swroot}/ca/cacert.pem" ) {
	print "Content-Type: application/octet-stream\r\n";
	print "Content-Disposition: filename=cacert.pem\r\n\r\n";
	print `/usr/bin/openssl x509 -in ${General::swroot}/ca/cacert.pem`;
	exit(0);
    }
###
### Download host certificate
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'download host certificate'}) {
    if ( -f "${General::swroot}/certs/hostcert.pem" ) {
	print "Content-Type: application/octet-stream\r\n";
	print "Content-Disposition: filename=hostcert.pem\r\n\r\n";
	print `/usr/bin/openssl x509 -in ${General::swroot}/certs/hostcert.pem`;
	exit(0);
    }
###
### Form for generating a root certificate
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'generate root/host certificates'} ||
	 $cgiparams{'ACTION'} eq $Lang::tr{'upload p12 file'}) {

    &General::readhash("${General::swroot}/vpn/settings", \%vpnsettings);
    if (-f "${General::swroot}/ca/cacert.pem") {
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
		    '-out', "$tempdir/hostkey.pem")) {
		$errormessage = "$Lang::tr{'cant start openssl'}: $!";
		unlink ($filename);
		goto ROOTCERT_ERROR;
	    }
	}

	move("$tempdir/cacert.pem", "${General::swroot}/ca/cacert.pem");
	if ($? ne 0) {
	    $errormessage = "$Lang::tr{'certificate file move failed'}: $!";
	    unlink ($filename);
	    unlink ("${General::swroot}/ca/cacert.pem");
	    unlink ("${General::swroot}/certs/hostcert.pem");
	    unlink ("${General::swroot}/certs/hostkey.pem");
	    goto ROOTCERT_ERROR;
        }

	move("$tempdir/hostcert.pem", "${General::swroot}/certs/hostcert.pem");
	if ($? ne 0) {
	    $errormessage = "$Lang::tr{'certificate file move failed'}: $!";
	    unlink ($filename);
	    unlink ("${General::swroot}/ca/cacert.pem");
	    unlink ("${General::swroot}/certs/hostcert.pem");
	    unlink ("${General::swroot}/certs/hostkey.pem");
	    goto ROOTCERT_ERROR;
        }

	move("$tempdir/hostkey.pem", "${General::swroot}/certs/hostkey.pem");
	if ($? ne 0) {
	    $errormessage = "$Lang::tr{'certificate file move failed'}: $!";
	    unlink ($filename);
	    unlink ("${General::swroot}/ca/cacert.pem");
	    unlink ("${General::swroot}/certs/hostcert.pem");
	    unlink ("${General::swroot}/certs/hostkey.pem");
	    goto ROOTCERT_ERROR;
        }

	# Create an empty CRL
	system('/usr/bin/openssl', 'ca', '-gencrl',
		'-out', "${General::swroot}/crls/cacrl.pem");
	if ($?) {
	    $errormessage = "$Lang::tr{'openssl produced an error'}: $?";
	    unlink ("${General::swroot}/certs/hostkey.pem");
	    unlink ("${General::swroot}/certs/hostcert.pem");
	    unlink ("${General::swroot}/ca/cacert.pem");
	    unlink ("${General::swroot}/crls/cacrl.pem");
	    &cleanssldatabase();
	    goto ROOTCERT_ERROR;
	} else {
	    &cleanssldatabase();
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
	&General::writehash("${General::swroot}/vpn/settings", \%vpnsettings);

	# Replace empty strings with a .
	(my $ou = $cgiparams{'ROOTCERT_OU'}) =~ s/^\s*$/\./;
	(my $city = $cgiparams{'ROOTCERT_CITY'}) =~ s/^\s*$/\./;
	(my $state = $cgiparams{'ROOTCERT_STATE'}) =~ s/^\s*$/\./;

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
		unlink ("${General::swroot}/private/cakey.pem");
		unlink ("${General::swroot}/ca/cacert.pem");
		goto ROOTCERT_ERROR;
	    }
	} else {	# child
	    unless (exec ('/usr/bin/openssl', 'req', '-x509', '-nodes', '-rand', '/proc/interrupts:/proc/net/rt_cache',
			'-days', '999999', '-newkey', 'rsa:2048',
			'-keyout', "${General::swroot}/private/cakey.pem",
			'-out', "${General::swroot}/ca/cacert.pem")) {
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
		unlink ("${General::swroot}/certs/hostkey.pem");
		unlink ("${General::swroot}/certs/hostreq.pem");
		goto ROOTCERT_ERROR;
	    }
	} else {	# child
	    unless (exec ('/usr/bin/openssl', 'req', '-nodes', '-rand', '/proc/interrupts:/proc/net/rt_cache',
			'-newkey', 'rsa:1024',
			'-keyout', "${General::swroot}/certs/hostkey.pem",
			'-out', "${General::swroot}/certs/hostreq.pem")) {
		$errormessage = "$Lang::tr{'cant start openssl'}: $!";
		unlink ("${General::swroot}/certs/hostkey.pem");
		unlink ("${General::swroot}/certs/hostreq.pem");
		unlink ("${General::swroot}/private/cakey.pem");
		unlink ("${General::swroot}/ca/cacert.pem");
		goto ROOTCERT_ERROR;
	    }
	}
	
	# Sign the host certificate request
	system('/usr/bin/openssl', 'ca', '-days', '999999',
		'-batch', '-notext',
		'-in',  "${General::swroot}/certs/hostreq.pem",
		'-out', "${General::swroot}/certs/hostcert.pem");
	if ($?) {
	    $errormessage = "$Lang::tr{'openssl produced an error'}: $?";
	    unlink ("${General::swroot}/private/cakey.pem");
	    unlink ("${General::swroot}/ca/cacert.pem");
	    unlink ("${General::swroot}/certs/hostkey.pem");
	    unlink ("${General::swroot}/certs/hostreq.pem");
	    unlink ("${General::swroot}/certs/hostcert.pem");
	    &cleanssldatabase();
	    goto ROOTCERT_ERROR;
	} else {
	    unlink ("${General::swroot}/certs/hostreq.pem");
	    &cleanssldatabase();
	}

	# Create an empty CRL
	system('/usr/bin/openssl', 'ca', '-gencrl',
		'-out', "${General::swroot}/crls/cacrl.pem");
	if ($?) {
	    $errormessage = "$Lang::tr{'openssl produced an error'}: $?";
	    unlink ("${General::swroot}/certs/hostkey.pem");
	    unlink ("${General::swroot}/certs/hostcert.pem");
	    unlink ("${General::swroot}/ca/cacert.pem");
	    unlink ("${General::swroot}/crls/cacrl.pem");
	    &cleanssldatabase();
	    goto ROOTCERT_ERROR;
	} else {
	    &cleanssldatabase();
	}
	goto ROOTCERT_SUCCESS;
    }
    ROOTCERT_ERROR:
    if ($cgiparams{'ACTION'} ne '') {
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'vpn configuration main'}, 1, '');
	&Header::openbigbox('100%', 'LEFT', '', $errormessage);
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
	<tr><td class='base'>$Lang::tr{'your e-mail'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	    <td class='base' nowrap='nowrap'><input type='text' name='ROOTCERT_EMAIL' value='$cgiparams{'ROOTCERT_EMAIL'}' size='32' /></td>
	    <td colspan='2'>&nbsp;</td></tr>
	<tr><td class='base'>$Lang::tr{'your department'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	    <td class='base' nowrap='nowrap'><input type='text' name='ROOTCERT_OU' value='$cgiparams{'ROOTCERT_OU'}' size='32' /></td>
	    <td colspan='2'>&nbsp;</td></tr>
	<tr><td class='base'>$Lang::tr{'city'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	    <td class='base' nowrap='nowrap'><input type='text' name='ROOTCERT_CITY' value='$cgiparams{'ROOTCERT_CITY'}' size='32' /></td>
	    <td colspan='2'>&nbsp;</td></tr>
	<tr><td class='base'>$Lang::tr{'state or province'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
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
	    <td><br /><input type='submit' name='ACTION' value='$Lang::tr{'generate root/host certificates'}' /><br /><br /></td>
	    <td>&nbsp;</td><td>&nbsp;</td></tr>
	<tr><td class='base' align='left' valign='top'>
	    <img src='/blob.gif' valign='top' alt='*' />&nbsp;$Lang::tr{'this field may be blank'}</td>
	    <td class='base' align='left'>
	    <b><font color='${Header::colourred}'>$Lang::tr{'capswarning'}</font></b>: 
	    $Lang::tr{'generating the root and host certificates may take a long time. it can take up to several minutes on older hardware. please be patient'}
	</td></tr>
	<tr><td colspan='4'><hr /></td></tr>
	<tr><td class='base' nowrap='nowrap'>$Lang::tr{'upload p12 file'}:</td>
	    <td nowrap='nowrap'><input type='file' name='FH' size='32'></td>
	    <td colspan='2'>&nbsp;</td></tr>
	<tr><td class='base'>$Lang::tr{'pkcs12 file password'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	    <td class='base' nowrap='nowrap'><input type='password' name='P12_PASS' value='$cgiparams{'P12_PASS'}' size='32' /></td>
            <td colspan='2'>&nbsp;</td></tr>
	<tr><td>&nbsp;</td>
	    <td><input type='submit' name='ACTION' value='$Lang::tr{'upload p12 file'}' /></td>
            <td colspan='2'>&nbsp;</td></tr>
	<tr><td class='base' colspan='4' align='left'>
	    <img src='/blob.gif' valign='top' alt='*' />&nbsp;$Lang::tr{'this field may be blank'}</td></tr>
	</form></table>
END
	;
	&Header::closebox();

	&Header::closebigbox();
	&Header::closepage();
        exit(0)
    }

    ROOTCERT_SUCCESS:
    if ($vpnsettings{'ENABLED'} eq 'on' ||
	$vpnsettings{'ENABLE_BLUE'} eq 'on') {
	system('/usr/local/bin/ipsecctrl', 'S');
	sleep $sleepDelay;
    }
###
### Download PKCS12 file
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'download pkcs12 file'}) {
    &General::readhasharray("${General::swroot}/vpn/config", \%confighash);

    print "Content-Disposition: filename=" . $confighash{$cgiparams{'KEY'}}[1] . ".p12\r\n";
    print "Content-Type: application/octet-stream\r\n\r\n";
    print `/bin/cat ${General::swroot}/certs/$confighash{$cgiparams{'KEY'}}[1].p12`;
    exit (0);

###
### Display certificate
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'show certificate'}) {
    &General::readhasharray("${General::swroot}/vpn/config", \%confighash);

    if ( -f "${General::swroot}/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem") {
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'vpn configuration main'}, 1, '');
	&Header::openbigbox('100%', 'LEFT', '', '');
	&Header::openbox('100%', 'LEFT', "$Lang::tr{'certificate'}:");
	my $output = `/usr/bin/openssl x509 -text -in ${General::swroot}/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem`;
	$output = &Header::cleanhtml($output,"y");
	print "<pre>$output</pre>\n";
	&Header::closebox();
	print "<div align='center'><a href='/cgi-bin/vpnmain.cgi'>$Lang::tr{'back'}</a></div>";
	&Header::closebigbox();
	&Header::closepage();
	exit(0);
    }

###
### Download Certificate
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'download certificate'}) {
    &General::readhasharray("${General::swroot}/vpn/config", \%confighash);

    if ( -f "${General::swroot}/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem") {
	print "Content-Disposition: filename=" . $confighash{$cgiparams{'KEY'}}[1] . "cert.pem\r\n";
	print "Content-Type: application/octet-stream\r\n\r\n";
	print `/bin/cat ${General::swroot}/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem`;
	exit (0);
    }

###
### Enable/Disable connection
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'toggle enable disable'}) {
    
    &General::readhash("${General::swroot}/vpn/settings", \%vpnsettings);
    &General::readhasharray("${General::swroot}/vpn/config", \%confighash);

    if ($confighash{$cgiparams{'KEY'}}) {
	if ($confighash{$cgiparams{'KEY'}}[0] eq 'off') {
	    $confighash{$cgiparams{'KEY'}}[0] = 'on';
	    &General::writehasharray("${General::swroot}/vpn/config", \%confighash);
	    &writeipsecfiles();
	    if ($vpnsettings{'ENABLED'} eq 'on' ||
		$vpnsettings{'ENABLED_BLUE'} eq 'on') {
	 	system('/usr/local/bin/ipsecctrl', 'S', $cgiparams{'KEY'});
		sleep $sleepDelay;
	    }
	} else {
	    $confighash{$cgiparams{'KEY'}}[0] = 'off';
	    if ($vpnsettings{'ENABLED'} eq 'on' ||
		$vpnsettings{'ENABLED_BLUE'} eq 'on') {
		system('/usr/local/bin/ipsecctrl', 'D', $cgiparams{'KEY'});
	    }
	    &General::writehasharray("${General::swroot}/vpn/config", \%confighash);
	    &writeipsecfiles();
	}
    } else {
	$errormessage = $Lang::tr{'invalid key'};
    }

###
### Restart connection
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'restart'}) {
    &General::readhash("${General::swroot}/vpn/settings", \%vpnsettings);
    &General::readhasharray("${General::swroot}/vpn/config", \%confighash);

    if ($confighash{$cgiparams{'KEY'}}) {
	if ($vpnsettings{'ENABLED'} eq 'on' ||
	    $vpnsettings{'ENABLED_BLUE'} eq 'on') {
	    system('/usr/local/bin/ipsecctrl', 'S', $cgiparams{'KEY'});
	    sleep $sleepDelay;
	}
    } else {
	$errormessage = $Lang::tr{'invalid key'};
    }

###
### Remove connection
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'remove'}) {
    &General::readhash("${General::swroot}/vpn/settings", \%vpnsettings);
    &General::readhasharray("${General::swroot}/vpn/config", \%confighash);

    if ($confighash{$cgiparams{'KEY'}}) {
	if ($vpnsettings{'ENABLED'} eq 'on' ||
	    $vpnsettings{'ENABLED_BLUE'} eq 'on') {
	    system('/usr/local/bin/ipsecctrl', 'D', $cgiparams{'KEY'});
	}
	unlink ("${General::swroot}/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem");
	unlink ("${General::swroot}/certs/$confighash{$cgiparams{'KEY'}}[1].p12");
	delete $confighash{$cgiparams{'KEY'}};
	&General::writehasharray("${General::swroot}/vpn/config", \%confighash);
	&writeipsecfiles();
    } else {
	$errormessage = $Lang::tr{'invalid key'};
    }

###
### Choose between adding a host-net or net-net connection
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'add'} && $cgiparams{'TYPE'} eq '') {
	&General::readhash("${General::swroot}/vpn/settings", \%vpnsettings);
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'vpn configuration main'}, 1, '');
	&Header::openbigbox('100%', 'LEFT', '', '');
	&Header::openbox('100%', 'LEFT', $Lang::tr{'connection type'});
	print <<END
	    <b>$Lang::tr{'connection type'}:</b><br />
	    <table><form method='post'>
	    <tr><td><input type='radio' name='TYPE' value='host' checked /></td>
		<td class='base'>$Lang::tr{'host to net vpn'}</td></tr>
	    <tr><td><input type='radio' name='TYPE' value='net' /></td>
		<td class='base'>$Lang::tr{'net to net vpn'}</td></tr>
	    <tr><td align='center' colspan='2'><input type='submit' name='ACTION' value='$Lang::tr{'add'}' /></td></tr>
	    </form></table>
END
	;
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit (0);
###
### Adding a new connection
###
} elsif (($cgiparams{'ACTION'} eq $Lang::tr{'add'}) ||
	 ($cgiparams{'ACTION'} eq $Lang::tr{'edit'}) ||
	 ($cgiparams{'ACTION'} eq $Lang::tr{'save'} && $cgiparams{'ADVANCED'} eq '')) {

    &General::readhash("${General::swroot}/vpn/settings", \%vpnsettings);
    &General::readhasharray("${General::swroot}/vpn/caconfig", \%cahash);
    &General::readhasharray("${General::swroot}/vpn/config", \%confighash);

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
	$cgiparams{'LOCAL_ID'}	= $confighash{$cgiparams{'KEY'}}[7];
	$cgiparams{'LOCAL_SUBNET'} = $confighash{$cgiparams{'KEY'}}[8];
	$cgiparams{'REMOTE_ID'}	= $confighash{$cgiparams{'KEY'}}[9];
	$cgiparams{'REMOTE'}	= $confighash{$cgiparams{'KEY'}}[10];
	$cgiparams{'REMOTE_SUBNET'} = $confighash{$cgiparams{'KEY'}}[11];
	$cgiparams{'REMARK'}	= $confighash{$cgiparams{'KEY'}}[25];
	$cgiparams{'INTERFACE'}	= $confighash{$cgiparams{'KEY'}}[26];
	$cgiparams{'DPD_ACTION'}= $confighash{$cgiparams{'KEY'}}[27];
	$cgiparams{'PFS_YES_NO'}= $confighash{$cgiparams{'KEY'}}[28];

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

	if (($cgiparams{'TYPE'} eq 'net') && ($cgiparams{'SIDE'} !~ /^(left|right)$/)) {
	    $errormessage = $Lang::tr{'ipfire side is invalid'};
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
		    if (&valid_dns_host($cgiparams{'REMOTE'})) {
			$warnmessage = "$Lang::tr{'check vpn lr'} $cgiparams{'REMOTE'}. $Lang::tr{'dns check failed'}";
		    }
		}
	    }
	}

        unless (&General::validipandmask($cgiparams{'LOCAL_SUBNET'})) {
            $errormessage = $Lang::tr{'local subnet is invalid'};
	    goto VPNCONF_ERROR;
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
	if (($cgiparams{'TYPE'} eq 'net') && (! &General::validipandmask($cgiparams{'REMOTE_SUBNET'}))) {
            $errormessage = $Lang::tr{'remote subnet is invalid'};
	    goto VPNCONF_ERROR;
	}

	if ($cgiparams{'ENABLED'} !~ /^(on|off)$/) {
	    $errormessage = $Lang::tr{'invalid input'};
	    goto VPNCONF_ERROR;
	}
	if ($cgiparams{'EDIT_ADVANCED'} !~ /^(on|off)$/) {
	    $errormessage = $Lang::tr{'invalid input'};
	    goto VPNCONF_ERROR;
	}

	if (($cgiparams{'LOCAL_ID'} !~ /^(|@[a-zA-Z0-9_.-]*)$/) ||
	    ($cgiparams{'REMOTE_ID'} !~ /^(|@[a-zA-Z0-9_.-]*)$/) ||
	    (($cgiparams{'REMOTE_ID'} eq $cgiparams{'LOCAL_ID'}) && ($cgiparams{'LOCAL_ID'} ne ''))
	   ) {
	    $errormessage = $Lang::tr{'invalid local-remote id'};
	    goto VPNCONF_ERROR;
	}
	
	if ($cgiparams{'AUTH'} eq 'psk')  {
	    if (! length($cgiparams{'PSK'}) ) {
		$errormessage = $Lang::tr{'pre-shared key is too short'};
		goto VPNCONF_ERROR;
	    }
	    if ($cgiparams{'PSK'} =~ /['",&]/) {        # " ' correct coloring syntax editor !
		$errormessage = $Lang::tr{'invalid characters found in pre-shared key'};
		goto VPNCONF_ERROR;
	    }
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
		'-out', "${General::swroot}/certs/$cgiparams{'NAME'}cert.pem");
	    if ($?) {
		$errormessage = "$Lang::tr{'openssl produced an error'}: $?";
		unlink ($filename);
		unlink ("${General::swroot}/certs/$cgiparams{'NAME'}cert.pem");
		&cleanssldatabase();
		goto VPNCONF_ERROR;
	    } else {
		unlink ($filename);
		&cleanssldatabase();
	    }

	    my $temp = `/usr/bin/openssl x509 -text -in ${General::swroot}/certs/$cgiparams{'NAME'}cert.pem`;
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
	    my $test = `/usr/bin/openssl verify -CAfile ${General::swroot}/ca/cacert.pem $filename`;
	    if ($test =~ /: OK/) {
		$validca = 1;
	    } else {
		foreach my $key (keys %cahash) {
		    $test = `/usr/bin/openssl verify -CAfile ${General::swroot}/ca/$cahash{$key}[0]cert.pem $filename`;
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
		move($filename, "${General::swroot}/certs/$cgiparams{'NAME'}cert.pem");
		if ($? ne 0) {
		    $errormessage = "$Lang::tr{'certificate file move failed'}: $!";
		    unlink ($filename);
		    goto VPNCONF_ERROR;
		}
	    }

	    my $temp = `/usr/bin/openssl x509 -text -in ${General::swroot}/certs/$cgiparams{'NAME'}cert.pem`;
	    $temp =~ /Subject:.*CN=(.*)[\n]/;
	    $temp = $1;
	    $temp =~ s+/Email+, E+;
	    $temp =~ s/ ST=/ S=/;
	    $cgiparams{'CERT_NAME'} = $temp;
	    $cgiparams{'CERT_NAME'} =~ s/,//g;
	    $cgiparams{'CERT_NAME'} =~ s/\'//g;
	    if ($cgiparams{'CERT_NAME'} eq '') {
		unlink ("${General::swroot}/certs/$cgiparams{'NAME'}cert.pem");
		$errormessage = $Lang::tr{'could not retrieve common name from certificate'};
		goto VPNCONF_ERROR;
	    }
	} elsif ($cgiparams{'AUTH'} eq 'certgen') {
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
	    if (length($cgiparams{'CERT_PASS1'}) < 5) {
		$errormessage = $Lang::tr{'password too short'};
		goto VPNCONF_ERROR;
	    }
	    if ($cgiparams{'CERT_PASS1'} ne $cgiparams{'CERT_PASS2'}) {
		$errormessage = $Lang::tr{'passwords do not match'};
		goto VPNCONF_ERROR;
	    }

	    # Replace empty strings with a .
	    (my $ou = $cgiparams{'CERT_OU'}) =~ s/^\s*$/\./;
	    (my $city = $cgiparams{'CERT_CITY'}) =~ s/^\s*$/\./;
	    (my $state = $cgiparams{'CERT_STATE'}) =~ s/^\s*$/\./;

	    # Create the Host certificate request
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
		    unlink ("${General::swroot}/certs/$cgiparams{'NAME'}key.pem");
		    unlink ("${General::swroot}/certs/$cgiparams{'NAME'}req.pem");
		    goto VPNCONF_ERROR;
		}
	    } else {	# child
		unless (exec ('/usr/bin/openssl', 'req', '-nodes', '-rand', '/proc/interrupts:/proc/net/rt_cache',
			'-newkey', 'rsa:1024',
			'-keyout', "${General::swroot}/certs/$cgiparams{'NAME'}key.pem",
			'-out', "${General::swroot}/certs/$cgiparams{'NAME'}req.pem")) {
		    $errormessage = "$Lang::tr{'cant start openssl'}: $!";
		    unlink ("${General::swroot}/certs/$cgiparams{'NAME'}key.pem");
		    unlink ("${General::swroot}/certs/$cgiparams{'NAME'}req.pem");
		    goto VPNCONF_ERROR;
		}
	    }
	
	    # Sign the host certificate request
	    system('/usr/bin/openssl', 'ca', '-days', '999999',
		'-batch', '-notext',
		'-in',  "${General::swroot}/certs/$cgiparams{'NAME'}req.pem",
		'-out', "${General::swroot}/certs/$cgiparams{'NAME'}cert.pem");
	    if ($?) {
		$errormessage = "$Lang::tr{'openssl produced an error'}: $?";
		unlink ("${General::swroot}/certs/$cgiparams{'NAME'}key.pem");
		unlink ("${General::swroot}/certs/$cgiparams{'NAME'}req.pem");
		unlink ("${General::swroot}/certs/$cgiparams{'NAME'}cert.pem");
		&cleanssldatabase();
		goto VPNCONF_ERROR;
	    } else {
		unlink ("${General::swroot}/certs/$cgiparams{'NAME'}req.pem");
		&cleanssldatabase();
	    }

	    # Create the pkcs12 file
	    system('/usr/bin/openssl', 'pkcs12', '-export', 
		'-inkey', "${General::swroot}/certs/$cgiparams{'NAME'}key.pem",
		'-in', "${General::swroot}/certs/$cgiparams{'NAME'}cert.pem",
		'-name', $cgiparams{'NAME'},
		'-passout', "pass:$cgiparams{'CERT_PASS1'}",
		'-certfile', "${General::swroot}/ca/cacert.pem", 
		'-caname', "$vpnsettings{'ROOTCERT_ORGANIZATION'} CA",
		'-out', "${General::swroot}/certs/$cgiparams{'NAME'}.p12");
	    if ($?) {
		$errormessage = "$Lang::tr{'openssl produced an error'}: $?";
		unlink ("${General::swroot}/certs/$cgiparams{'NAME'}key.pem");
		unlink ("${General::swroot}/certs/$cgiparams{'NAME'}cert.pem");
		unlink ("${General::swroot}/certs/$cgiparams{'NAME'}.p12");
		goto VPNCONF_ERROR;
	    } else {
		unlink ("${General::swroot}/certs/$cgiparams{'NAME'}key.pem");
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
	    foreach my $i (0 .. 28) { $confighash{$key}[$i] = "";}
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
	}
	$confighash{$key}[7] = $cgiparams{'LOCAL_ID'};
	$confighash{$key}[8] = $cgiparams{'LOCAL_SUBNET'};
	$confighash{$key}[9] = $cgiparams{'REMOTE_ID'};
	$confighash{$key}[10] = $cgiparams{'REMOTE'};
	$confighash{$key}[25] = $cgiparams{'REMARK'};
	$confighash{$key}[26] = $cgiparams{'INTERFACE'};
	$confighash{$key}[27] = $cgiparams{'DPD_ACTION'};
	$confighash{$key}[28] = $cgiparams{'PFS_YES_NO'};

	#use default advanced value
	$confighash{$key}[14] = 'on';
	$confighash{$key}[13] = 'off';
	$confighash{$key}[18] = 'aes128|3des';
	$confighash{$key}[19] = 'sha|md5';
	$confighash{$key}[20] = '1536|1024';
	$confighash{$key}[16] = '1';
	$confighash{$key}[21] = 'aes128|3des';
	$confighash{$key}[22] = 'sha1|md5';
	$confighash{$key}[23] = '';
	$confighash{$key}[17] = '8';
	$confighash{$key}[24] = 'off';

	#free unused fields!
	#$confighash{$key}[12] = '';
	#$confighash{$key}[15] = '';

	&General::writehasharray("${General::swroot}/vpn/config", \%confighash);
	&writeipsecfiles();
	if ($vpnsettings{'ENABLED'} eq 'on' ||
	    $vpnsettings{'ENABLED_BLUE'} eq 'on') {
	    system('/usr/local/bin/ipsecctrl', 'S', $key);
	    sleep $sleepDelay;
	}
	if ($cgiparams{'EDIT_ADVANCED'} eq 'on') {
	    $cgiparams{'KEY'} = $key;
	    $cgiparams{'ACTION'} = $Lang::tr{'advanced'};
	}
	goto VPNCONF_END;
    } else { # add new connection
        $cgiparams{'ENABLED'} = 'on';
	$cgiparams{'SIDE'} = 'left';
	if ( ! -f "${General::swroot}/private/cakey.pem" ) {
	    $cgiparams{'AUTH'} = 'psk';
	} elsif ( ! -f "${General::swroot}/ca/cacert.pem") {
	    $cgiparams{'AUTH'} = 'certfile';
	} else {
            $cgiparams{'AUTH'} = 'certgen';
	}
	$cgiparams{'LOCAL_SUBNET'}      ="$netsettings{'GREEN_NETADDRESS'}/$netsettings{'GREEN_NETMASK'}";
	$cgiparams{'CERT_ORGANIZATION'} = $vpnsettings{'ROOTCERT_ORGANIZATION'};
	$cgiparams{'CERT_CITY'}         = $vpnsettings{'ROOTCERT_CITY'};
	$cgiparams{'CERT_STATE'}        = $vpnsettings{'ROOTCERT_STATE'};
	$cgiparams{'CERT_COUNTRY'}      = $vpnsettings{'ROOTCERT_COUNTRY'};

	# choose appropriate dpd action	
	if ($cgiparams{'TYPE'} eq 'host') {
	    $cgiparams{'DPD_ACTION'} = 'clear';
	} else {
	    $cgiparams{'DPD_ACTION'} = 'hold';  #restart when available!
	}

	# Default is yes for 'pfs'
	$cgiparams{'PFS_YES_NO'}     = 'yes';
	
	# ID are empty
	$cgiparams{'LOCAL_ID'}  = '';
	$cgiparams{'REMOTE_ID'} = '';
	
    }

    VPNCONF_ERROR:
    $checked{'ENABLED'}{'off'} = '';
    $checked{'ENABLED'}{'on'} = '';
    $checked{'ENABLED'}{$cgiparams{'ENABLED'}} = "checked='checked'";
    $checked{'ENABLED_BLUE'}{'off'} = '';
    $checked{'ENABLED_BLUE'}{'on'} = '';
    $checked{'ENABLED_BLUE'}{$cgiparams{'ENABLED_BLUE'}} = "checked='checked'";

    $checked{'EDIT_ADVANCED'}{'off'} = '';
    $checked{'EDIT_ADVANCED'}{'on'} = '';
    $checked{'EDIT_ADVANCED'}{$cgiparams{'EDIT_ADVANCED'}} = "checked='checked'";

    $selected{'SIDE'}{'left'} = '';
    $selected{'SIDE'}{'right'} = '';
    $selected{'SIDE'}{$cgiparams{'SIDE'}} = "selected='selected'";

    $checked{'AUTH'}{'psk'} = '';
    $checked{'AUTH'}{'certreq'} = '';
    $checked{'AUTH'}{'certgen'} = '';
    $checked{'AUTH'}{'certfile'} = '';
    $checked{'AUTH'}{$cgiparams{'AUTH'}} = "checked='checked'";

    $selected{'INTERFACE'}{$cgiparams{'INTERFACE'}} = "selected='selected'";
    $selected{'DPD_ACTION'}{$cgiparams{'DPD_ACTION'}} = "selected='selected'";
    $selected{'PFS_YES_NO'}{$cgiparams{'PFS_YES_NO'}} = "selected='selected'";

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

	if ($cgiparams{'KEY'}) {
	    print "<input type='hidden' name='KEY' value='$cgiparams{'KEY'}' />";
	    print "<input type='hidden' name='AUTH' value='$cgiparams{'AUTH'}' />";
	}

	&Header::openbox('100%', 'LEFT', "$Lang::tr{'connection'}:");
	print "<table width='100%'>";
	print "<tr><td width='25%' class='boldbase'>$Lang::tr{'name'}:</td>";
	if ($cgiparams{'KEY'}) {
	    print "<td width='25%' class='base'><input type='hidden' name='NAME' value='$cgiparams{'NAME'}' /><b>$cgiparams{'NAME'}</b></td>";
	} else {
	    print "<td width='25%'><input type='text' name='NAME' value='$cgiparams{'NAME'}' maxlength='20' size='30' /></td>";
	}
	print "<td>$Lang::tr{'enabled'}</td><td><input type='checkbox' name='ENABLED' $checked{'ENABLED'}{'on'} /></td></tr>";
	
	if ($cgiparams{'TYPE'} eq 'host') {

	    print "<tr><td>$Lang::tr{'interface'}</td>";
	    print "<td><select name='INTERFACE'>";
	    print "<option value='RED' $selected{'INTERFACE'}{'RED'}>RED</option>";
	    print "<option value='BLUE' $selected{'INTERFACE'}{'BLUE'}>BLUE</option>" if ($netsettings{'BLUE_DEV'} ne '');
# 	    print "<option value='GREEN' $selected{'INTERFACE'}{'GREEN'}>GREEN</option>";
#	    print "<option value='ORANGE' $selected{'INTERFACE'}{'ORANGE'}>ORANGE</option>";
	    print "</select></td></tr>";
	    print <<END
		<tr><td class='boldbase'>$Lang::tr{'local subnet'}</td>
		    <td><input type='text' name='LOCAL_SUBNET' value='$cgiparams{'LOCAL_SUBNET'}' size='30' /></td>
		    <td colspan='2'>&nbsp;</td></tr>
		<tr><td class='boldbase'>$Lang::tr{'remote host/ip'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
		    <td><input type='text' name='REMOTE' value='$cgiparams{'REMOTE'}' size='30' /></td>
		    <td colspan='2'>&nbsp;</td></tr>
END
	    ;
	} else {
	    print <<END
		<tr><input type='hidden' name='INTERFACE' value='RED' />
		    <td class='boldbase' nowrap='nowrap'>$Lang::tr{'ipfire side'}</td>
		    <td><select name='SIDE'><option value='left' $selected{'SIDE'}{'left'}>left</option>
					    <option value='right' $selected{'SIDE'}{'right'}>right</option></select></td>
 		    <td class='boldbase'>$Lang::tr{'remote host/ip'}:</td>
		    <td><input type='TEXT' name='REMOTE' value='$cgiparams{'REMOTE'}' size ='30' /></td></tr>
		<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'local subnet'}</td>
		    <td><input type='TEXT' name='LOCAL_SUBNET' value='$cgiparams{'LOCAL_SUBNET'}' size='30' /></td>
		    <td class='boldbase' nowrap='nowrap'>$Lang::tr{'remote subnet'}</td>
		    <td><input type='text' name='REMOTE_SUBNET' value='$cgiparams{'REMOTE_SUBNET'}' size='30' /></td></tr>
END
	    ;
	}
	print <<END
	<tr><td>$Lang::tr{'dpd action'}:</td>
	<td><select name='DPD_ACTION'>
	    <option value='clear' $selected{'DPD_ACTION'}{'clear'}>clear</option>
	    <option value='hold' $selected{'DPD_ACTION'}{'hold'}>hold</option>
	    <option value='restart' $selected{'DPD_ACTION'}{'restart'}>restart</option>
	</select>&nbsp; <a href='http://www.openswan.com/docs/local/README.DPD'>?</a></td>
<!--	http://www.openswan.com/docs/local/README.DPD
	http://bugs.xelerance.com/view.php?id=156
	restart = clear + reinitiate connection
-->	<td width='25%'>$Lang::tr{'pfs yes no'}:</td>
	<td width='25%'><select name='PFS_YES_NO'>
	    <option value='yes' $selected{'PFS_YES_NO'}{'yes'}>$Lang::tr{'yes'}</option>
	    <option value='no' $selected{'PFS_YES_NO'}{'no'}>$Lang::tr{'no'}</option>
	</select></td></tr>
	<td><b>$Lang::tr{'options'}</b></td>
	<tr><td class='boldbase'>leftid:&nbsp;<img src='/blob.gif' alt='*' />
	<br />($Lang::tr{'eg'} <tt>&#64;xy.example.com</tt>)</td>
	<td><input type='text' name='LOCAL_ID' value='$cgiparams{'LOCAL_ID'}' maxlength='50' /></td>
	<td class='boldbase'>rightid:&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td><input type='text' name='REMOTE_ID' value='$cgiparams{'REMOTE_ID'}' maxlength='50' /></td></tr>
	<tr><td class='boldbase'>$Lang::tr{'remark title'}&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td colspan='3'><input type='text' name='REMARK' value='$cgiparams{'REMARK'}' size='55' maxlength='50' /></td></tr>
END
	;
	if (!$cgiparams{'KEY'}) {
	    print "<tr><td colspan='3'><input type='checkbox' name='EDIT_ADVANCED' $checked{'EDIT_ADVANCED'}{'on'} /> $Lang::tr{'edit advanced settings when done'}</td></tr>";
	}
	print "</table>";
	&Header::closebox();
	
	if ($cgiparams{'KEY'} && $cgiparams{'AUTH'} eq 'psk') {
	    &Header::openbox('100%', 'LEFT', $Lang::tr{'authentication'});
	    print <<END
	    <table width='100%' cellpadding='0' cellspacing='5' border='0'>
	    <tr><td class='base' width='50%'>$Lang::tr{'use a pre-shared key'}</td>
		<td class='base' width='50%'><input type='text' name='PSK' size='30' value='$cgiparams{'PSK'}' /></td></tr>
	    </table>
END
	    ;
	    &Header::closebox();
	} elsif (! $cgiparams{'KEY'}) {
	    my $disabled='';
	    my $cakeydisabled='';
	    my $cacrtdisabled='';
	    if ( ! -f "${General::swroot}/private/cakey.pem" ) { $cakeydisabled = "disabled='disabled'" } else { $cakeydisabled = "" };
	    if ( ! -f "${General::swroot}/ca/cacert.pem" ) { $cacrtdisabled = "disabled='disabled'" } else { $cacrtdisabled = "" };
	    &Header::openbox('100%', 'LEFT', $Lang::tr{'authentication'});
	    print <<END
	    <table width='100%' cellpadding='0' cellspacing='5' border='0'>
	    <tr><td width='5%'><input type='radio' name='AUTH' value='psk' $checked{'AUTH'}{'psk'} /></td>
		<td class='base' width='45%'>$Lang::tr{'use a pre-shared key'}</td>
		<td class='base' width='50%'><input type='text' name='PSK' size='30' value='$cgiparams{'PSK'}' /></td></tr>
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
		<td class='base'>$Lang::tr{'users email'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
		<td class='base' nowrap='nowrap'><input type='text' name='CERT_EMAIL' value='$cgiparams{'CERT_EMAIL'}' SIZE='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td>
		<td class='base'>$Lang::tr{'users department'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
		<td class='base' nowrap='nowrap'><input type='text' name='CERT_OU' value='$cgiparams{'CERT_OU'}' SIZE='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td>
		<td class='base'>$Lang::tr{'organization name'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	        <td class='base' nowrap='nowrap'><input type='text' name='CERT_ORGANIZATION' value='$cgiparams{'CERT_ORGANIZATION'}' SIZE='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td>
		<td class='base'>$Lang::tr{'city'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
		<td class='base' nowrap='nowrap'><input type='text' name='CERT_CITY' value='$cgiparams{'CERT_CITY'}' SIZE='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td>
		<td class='base'>$Lang::tr{'state or province'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
		<td class='base' nowrap='nowrap'><input type='text' name='CERT_STATE' value='$cgiparams{'CERT_STATE'}' SIZE='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td>
		<td class='base'>$Lang::tr{'country'}:</td>
		<td class='base'><select name='CERT_COUNTRY' $cakeydisabled>
END
	    ;
	    foreach my $country (sort keys %{Countries::countries}) {
		print "\t\t\t<option value='$Countries::countries{$country}'";
		if ( $Countries::countries{$country} eq $cgiparams{'CERT_COUNTRY'} ) {
		    print " selected='selected'";
		}
		print ">$country</option>\n";
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
	    print "<input type='submit' name='ACTION' value='$Lang::tr{'advanced'}' />";
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
    &General::readhash("${General::swroot}/vpn/settings", \%vpnsettings);
    &General::readhasharray("${General::swroot}/vpn/config", \%confighash);
    if (! $confighash{$cgiparams{'KEY'}}) {
	$errormessage = $Lang::tr{'invalid key'};
	goto ADVANCED_END;
    }

    if ($cgiparams{'ACTION'} eq $Lang::tr{'save'}) {
	if ($cgiparams{'NAT'} !~ /^(on|off)$/) {
	    $errormessage = $Lang::tr{'invalid input'};
	    goto ADVANCED_ERROR;
	}
	if ($cgiparams{'COMPRESSION'} !~ /^(on|off)$/) {
	    $errormessage = $Lang::tr{'invalid input'};
	    goto ADVANCED_ERROR;
	}
	if ($cgiparams{'NAT'} eq 'on' && $cgiparams{'COMPRESSION'} eq 'on') {
	    $errormessage = $Lang::tr{'cannot enable both nat traversal and compression'};
	    goto ADVANCED_ERROR;
	}
	my @temp = split('\|', $cgiparams{'IKE_ENCRYPTION'});
	if ($#temp < 0) {
	    $errormessage = $Lang::tr{'invalid input'};
	    goto ADVANCED_ERROR;
	}
	foreach my $val (@temp) {
	    if ($val !~ /^(aes256|aes128|3des|twofish256|twofish128|serpent256|serpent128|blowfish256|blowfish128|cast128)$/) {
		$errormessage = $Lang::tr{'invalid input'};
		goto ADVANCED_ERROR;
	    }
	}
	@temp = split('\|', $cgiparams{'IKE_INTEGRITY'});
	if ($#temp < 0) {
	    $errormessage = $Lang::tr{'invalid input'};
	    goto ADVANCED_ERROR;
	}
	foreach my $val (@temp) {
	    if ($val !~ /^(sha2_512|sha2_256|sha|md5)$/) {
		$errormessage = $Lang::tr{'invalid input'};
		goto ADVANCED_ERROR;
	    }
	}
	@temp = split('\|', $cgiparams{'IKE_GROUPTYPE'});
	if ($#temp < 0) {
	    $errormessage = $Lang::tr{'invalid input'};
	    goto ADVANCED_ERROR;
	}
	foreach my $val (@temp) {
	    if ($val !~ /^(768|1024|1536|2048|3072|4096|6144|8192)$/) {
		$errormessage = $Lang::tr{'invalid input'};
		goto ADVANCED_ERROR;
	    }
	}
	if ($cgiparams{'IKE_LIFETIME'} !~ /^\d+$/) {
	    $errormessage = $Lang::tr{'invalid input for ike lifetime'};
	    goto ADVANCED_ERROR;
	}
	if ($cgiparams{'IKE_LIFETIME'} < 1 || $cgiparams{'IKE_LIFETIME'} > 8) {
	    $errormessage = $Lang::tr{'ike lifetime should be between 1 and 8 hours'};
	    goto ADVANCED_ERROR;
	}
	@temp = split('\|', $cgiparams{'ESP_ENCRYPTION'});
	if ($#temp < 0) {
	    $errormessage = $Lang::tr{'invalid input'};
	    goto ADVANCED_ERROR;
	}
	foreach my $val (@temp) {
	    if ($val !~ /^(aes256|aes128|3des|twofish256|twofish128|serpent256|serpent128|blowfish256|blowfish128)$/) {
		$errormessage = $Lang::tr{'invalid input'};
		goto ADVANCED_ERROR;
	    }
	}
	@temp = split('\|', $cgiparams{'ESP_INTEGRITY'});
	if ($#temp < 0) {
	    $errormessage = $Lang::tr{'invalid input'};
	    goto ADVANCED_ERROR;
	}
	foreach my $val (@temp) {
	    if ($val !~ /^(sha2_512|sha2_256|sha1|md5)$/) {
		$errormessage = $Lang::tr{'invalid input'};
		goto ADVANCED_ERROR;
	    }
	}
	if ($cgiparams{'ESP_GROUPTYPE'} ne '' &&
	    $cgiparams{'ESP_GROUPTYPE'} !~  /^modp(768|1024|1536|2048|3072|4096)$/) {
	    $errormessage = $Lang::tr{'invalid input'};
	    goto ADVANCED_ERROR;
	}

	if ($cgiparams{'ESP_KEYLIFE'} !~ /^\d+$/) {
	    $errormessage = $Lang::tr{'invalid input for esp keylife'};
	    goto ADVANCED_ERROR;
	}
	if ($cgiparams{'ESP_KEYLIFE'} < 1 || $cgiparams{'ESP_KEYLIFE'} > 24) {
	    $errormessage = $Lang::tr{'esp keylife should be between 1 and 24 hours'};
	    goto ADVANCED_ERROR;
	}
	if ($cgiparams{'ONLY_PROPOSED'} !~ /^(on|off)$/) {
	    $errormessage = $Lang::tr{'invalid input'};
	    goto ADVANCED_ERROR;
	}
	$confighash{$cgiparams{'KEY'}}[14] = $cgiparams{'NAT'};
	$confighash{$cgiparams{'KEY'}}[13] = $cgiparams{'COMPRESSION'};
	$confighash{$cgiparams{'KEY'}}[18] = $cgiparams{'IKE_ENCRYPTION'};
	$confighash{$cgiparams{'KEY'}}[19] = $cgiparams{'IKE_INTEGRITY'};
	$confighash{$cgiparams{'KEY'}}[20] = $cgiparams{'IKE_GROUPTYPE'};
	$confighash{$cgiparams{'KEY'}}[16] = $cgiparams{'IKE_LIFETIME'};
	$confighash{$cgiparams{'KEY'}}[21] = $cgiparams{'ESP_ENCRYPTION'};
	$confighash{$cgiparams{'KEY'}}[22] = $cgiparams{'ESP_INTEGRITY'};
	$confighash{$cgiparams{'KEY'}}[23] = $cgiparams{'ESP_GROUPTYPE'};
	$confighash{$cgiparams{'KEY'}}[17] = $cgiparams{'ESP_KEYLIFE'};
	$confighash{$cgiparams{'KEY'}}[24] = $cgiparams{'ONLY_PROPOSED'};
	&General::writehasharray("${General::swroot}/vpn/config", \%confighash);
	&writeipsecfiles();
	if ($vpnsettings{'ENABLED'} eq 'on' ||
	    $vpnsettings{'ENABLED_BLUE'} eq 'on') {
	    system('/usr/local/bin/ipsecctrl', 'S', $cgiparams{'KEY'});
	    sleep $sleepDelay;
	}
	goto ADVANCED_END;
    } else {

	$cgiparams{'NAT'}            = $confighash{$cgiparams{'KEY'}}[14];
	$cgiparams{'COMPRESSION'}    = $confighash{$cgiparams{'KEY'}}[13];
	$cgiparams{'IKE_ENCRYPTION'} = $confighash{$cgiparams{'KEY'}}[18];
	$cgiparams{'IKE_INTEGRITY'}  = $confighash{$cgiparams{'KEY'}}[19];
	$cgiparams{'IKE_GROUPTYPE'}  = $confighash{$cgiparams{'KEY'}}[20];
	$cgiparams{'IKE_LIFETIME'}   = $confighash{$cgiparams{'KEY'}}[16];
	$cgiparams{'ESP_ENCRYPTION'} = $confighash{$cgiparams{'KEY'}}[21];
	$cgiparams{'ESP_INTEGRITY'}  = $confighash{$cgiparams{'KEY'}}[22];
	$cgiparams{'ESP_GROUPTYPE'}  = $confighash{$cgiparams{'KEY'}}[23];
	$cgiparams{'ESP_KEYLIFE'}    = $confighash{$cgiparams{'KEY'}}[17];
	$cgiparams{'ONLY_PROPOSED'}  = $confighash{$cgiparams{'KEY'}}[24];
 
	if ($confighash{$cgiparams{'KEY'}}[3] eq 'net' || $confighash{$cgiparams{'KEY'}}[10]) {
	    $cgiparams{'NAT'}            = 'off';
	}
    }

    ADVANCED_ERROR:
    $checked{'NAT'}{'off'} = '';
    $checked{'NAT'}{'on'} = '';
    $checked{'NAT'}{$cgiparams{'NAT'}} = "checked='checked'";
    $checked{'COMPRESSION'}{'off'} = '';
    $checked{'COMPRESSION'}{'on'} = '';
    $checked{'COMPRESSION'}{$cgiparams{'COMPRESSION'}} = "checked='checked'";
    $checked{'IKE_ENCRYPTION'}{'aes256'} = '';
    $checked{'IKE_ENCRYPTION'}{'aes128'} = '';
    $checked{'IKE_ENCRYPTION'}{'3des'} = '';
    $checked{'IKE_ENCRYPTION'}{'twofish256'} = '';
    $checked{'IKE_ENCRYPTION'}{'twofish128'} = '';
    $checked{'IKE_ENCRYPTION'}{'serpent256'} = '';
    $checked{'IKE_ENCRYPTION'}{'serpent128'} = '';
    $checked{'IKE_ENCRYPTION'}{'blowfish256'} = '';
    $checked{'IKE_ENCRYPTION'}{'blowfish128'} = '';
    $checked{'IKE_ENCRYPTION'}{'cast128'} = '';
    my @temp = split('\|', $cgiparams{'IKE_ENCRYPTION'});
    foreach my $key (@temp) {$checked{'IKE_ENCRYPTION'}{$key} = "selected='selected'"; }
    $checked{'IKE_INTEGRITY'}{'sha2_512'} = '';
    $checked{'IKE_INTEGRITY'}{'sha2_256'} = '';
    $checked{'IKE_INTEGRITY'}{'sha'} = '';
    $checked{'IKE_INTEGRITY'}{'md5'} = '';
    @temp = split('\|', $cgiparams{'IKE_INTEGRITY'});
    foreach my $key (@temp) {$checked{'IKE_INTEGRITY'}{$key} = "selected='selected'"; }
    $checked{'IKE_GROUPTYPE'}{'768'} = '';
    $checked{'IKE_GROUPTYPE'}{'1024'} = '';
    $checked{'IKE_GROUPTYPE'}{'1536'} = '';
    $checked{'IKE_GROUPTYPE'}{'2048'} = '';
    $checked{'IKE_GROUPTYPE'}{'3072'} = '';
    $checked{'IKE_GROUPTYPE'}{'4096'} = '';
    $checked{'IKE_GROUPTYPE'}{'6144'} = '';
    $checked{'IKE_GROUPTYPE'}{'8192'} = '';
    @temp = split('\|', $cgiparams{'IKE_GROUPTYPE'});
    foreach my $key (@temp) {$checked{'IKE_GROUPTYPE'}{$key} = "selected='selected'"; }
    $checked{'ESP_ENCRYPTION'}{'aes256'} = '';
    $checked{'ESP_ENCRYPTION'}{'aes128'} = '';
    $checked{'ESP_ENCRYPTION'}{'3des'} = '';
    $checked{'ESP_ENCRYPTION'}{'twofish256'} = '';
    $checked{'ESP_ENCRYPTION'}{'twofish128'} = '';
    $checked{'ESP_ENCRYPTION'}{'serpent256'} = '';
    $checked{'ESP_ENCRYPTION'}{'serpent128'} = '';
    $checked{'ESP_ENCRYPTION'}{'blowfish256'} = '';
    $checked{'ESP_ENCRYPTION'}{'blowfish128'} = '';
    @temp = split('\|', $cgiparams{'ESP_ENCRYPTION'});
    foreach my $key (@temp) {$checked{'ESP_ENCRYPTION'}{$key} = "selected='selected'"; }
    $checked{'ESP_INTEGRITY'}{'sha2_512'} = '';
    $checked{'ESP_INTEGRITY'}{'sha2_256'} = '';
    $checked{'ESP_INTEGRITY'}{'sha1'} = '';
    $checked{'ESP_INTEGRITY'}{'md5'} = '';
    @temp = split('\|', $cgiparams{'ESP_INTEGRITY'});
    foreach my $key (@temp) {$checked{'ESP_INTEGRITY'}{$key} = "selected='selected'"; }
    $checked{'ESP_GROUPTYPE'}{'modp768'} = '';
    $checked{'ESP_GROUPTYPE'}{'modp1024'} = '';
    $checked{'ESP_GROUPTYPE'}{'modp1536'} = '';
    $checked{'ESP_GROUPTYPE'}{'modp2048'} = '';
    $checked{'ESP_GROUPTYPE'}{'modp3072'} = '';
    $checked{'ESP_GROUPTYPE'}{'modp4096'} = '';
    $checked{'ESP_GROUPTYPE'}{$cgiparams{'ESP_GROUPTYPE'}} = "selected='selected'";
    $checked{'ONLY_PROPOSED'}{'off'} = '';
    $checked{'ONLY_PROPOSED'}{'on'} = '';
    $checked{'ONLY_PROPOSED'}{$cgiparams{'ONLY_PROPOSED'}} = "checked='checked'";

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
    print "<table width='100%'>\n";
    print "<tr><td width='25%' class='boldbase'>$Lang::tr{'compression'}</td>\n";
    print "<td width='25%'><input type='checkbox' name='COMPRESSION' $checked{'COMPRESSION'}{'on'} /></td>\n";
    if ($confighash{$cgiparams{'KEY'}}[3] eq 'net') {
	print "<td width='25%'><input type='hidden' name='NAT' value='off' /></td><td width='25%'>&nbsp;</td></tr>\n";
    } elsif ($confighash{$cgiparams{'KEY'}}[10]) {
	print "<td width='25%' class='boldbase'>$Lang::tr{'nat-traversal'}</td>\n";
	print "<td width='25%'><input type='checkbox' name='NAT' $checked{'NAT'}{'on'} disabled='disabled' /></td></tr>\n";
    } else {
	print "<td width='25%' class='boldbase'>$Lang::tr{'nat-traversal'}</td>\n";
	print "<td width='25%'><input type='checkbox' name='NAT' $checked{'NAT'}{'on'} /></td></tr>\n";
    }
    print <<EOF
	<tr><td width='25%' class='boldbase' valign='top'>$Lang::tr{'ike encryption'}</td>
	    <td width='25%' valign='top'><select name='IKE_ENCRYPTION' multiple='multiple' size='4'>
			<option value='aes256' $checked{'IKE_ENCRYPTION'}{'aes256'}>AES (256 bit)</option>
			<option value='aes128' $checked{'IKE_ENCRYPTION'}{'aes128'}>AES (128 bit)</option>
			<option value='3des' $checked{'IKE_ENCRYPTION'}{'3des'}>3DES</option>
			<option value='twofish256' $checked{'IKE_ENCRYPTION'}{'twofish256'}>Twofish (256 bit)</option>
			<option value='twofish128' $checked{'IKE_ENCRYPTION'}{'twofish128'}>Twofish (128 bit)</option>
			<option value='serpent256' $checked{'IKE_ENCRYPTION'}{'serpent256'}>Serpent (256 bit)</option>
			<option value='serpent128' $checked{'IKE_ENCRYPTION'}{'serpent128'}>Serpent (128 bit)</option>
			<option value='blowfish256' $checked{'IKE_ENCRYPTION'}{'blowfish256'}>Blowfish (256 bit)</option>
			<option value='blowfish128' $checked{'IKE_ENCRYPTION'}{'blowfish128'}>Blowfish (128 bit)</option>
			<option value='cast128' $checked{'IKE_ENCRYPTION'}{'cast128'}>Cast (128 bit)</option></SELECT></td>
	    <td width='25%' class='boldbase' valign='top'>$Lang::tr{'ike integrity'}</td>
	    <td width='25%' valign='top'><select name='IKE_INTEGRITY' multiple='multiple' size='4'>
			<option value='sha2_512' $checked{'IKE_INTEGRITY'}{'sha2_512'}>SHA2 (512)</option>
			<option value='sha2_256' $checked{'IKE_INTEGRITY'}{'sha2_256'}>SHA2 (256)</option>
			<option value='sha' $checked{'IKE_INTEGRITY'}{'sha'}>SHA</option>
			<option value='md5' $checked{'IKE_INTEGRITY'}{'md5'}>MD5</option></SELECT></td></tr>
	<tr><td width='25%' class='boldbase' valign='top'>$Lang::tr{'ike lifetime'}</td>
	    <td width='25%' valign='top'><input type='text' name='IKE_LIFETIME' value='$cgiparams{'IKE_LIFETIME'}' SIZE='5'> $Lang::tr{'hours'}</td>
	    <td width='25%' class='boldbase' valign='top'>$Lang::tr{'ike grouptype'}</td>
	    <td width='25%' valign='top'><select name='IKE_GROUPTYPE' multiple='multiple' size='4'>
			<option value='8192' $checked{'IKE_GROUPTYPE'}{'8192'}>MODP-8192</option>
			<option value='6144' $checked{'IKE_GROUPTYPE'}{'6144'}>MODP-6144</option>
			<option value='4096' $checked{'IKE_GROUPTYPE'}{'4096'}>MODP-4096</option>
			<option value='3072' $checked{'IKE_GROUPTYPE'}{'3072'}>MODP-3072</option>
			<option value='2048' $checked{'IKE_GROUPTYPE'}{'2048'}>MODP-2048</option>
			<option value='1536' $checked{'IKE_GROUPTYPE'}{'1536'}>MODP-1536</option>
			<option value='1024' $checked{'IKE_GROUPTYPE'}{'1024'}>MODP-1024</option>
			<option value='768'  $checked{'IKE_GROUPTYPE'}{'768'}>MODP-768</option></select></td></tr>
	<tr><td width='25%' class='boldbase' valign='top'>$Lang::tr{'esp encryption'}</td>
	    <td width='25%' valign='top'><select name='ESP_ENCRYPTION' multiple='multiple' size='4'>
			<option value='aes256' $checked{'ESP_ENCRYPTION'}{'aes256'}>AES (256 bit)</option>
			<option value='aes128' $checked{'ESP_ENCRYPTION'}{'aes128'}>AES (128 bit)</option>
			<option value='3des' $checked{'ESP_ENCRYPTION'}{'3des'}>3DES</option>
			<option value='twofish256' $checked{'ESP_ENCRYPTION'}{'twofish256'}>Twofish (256 bit)</option>
			<option value='twofish128' $checked{'ESP_ENCRYPTION'}{'twofish128'}>Twofish (128 bit)</option>
			<option value='serpent256' $checked{'ESP_ENCRYPTION'}{'serpent256'}>Serpent (256 bit)</option>
			<option value='serpent128' $checked{'ESP_ENCRYPTION'}{'serpent128'}>Serpent (128 bit)</option>
			<option value='blowfish256' $checked{'ESP_ENCRYPTION'}{'blowfish256'}>Blowfish (256 bit)</option>
			<option value='blowfish128' $checked{'ESP_ENCRYPTION'}{'blowfish128'}>Blowfish (128 bit)</option></select></td>
	    <td width='25%' class='boldbase' valign='top'>$Lang::tr{'esp integrity'}</td>
	    <td width='25%' valign='top'><select name='ESP_INTEGRITY' multiple='multiple' size='4'>
			<option value='sha2_512' $checked{'ESP_INTEGRITY'}{'sha2_512'}>SHA2 (512)</option>
			<option value='sha2_256' $checked{'ESP_INTEGRITY'}{'sha2_256'}>SHA2 (256)</option>
			<option value='sha1' $checked{'ESP_INTEGRITY'}{'sha1'}>SHA1</option>
			<option value='md5' $checked{'ESP_INTEGRITY'}{'md5'}>MD5</option></select></td></tr>
	<tr><td width='25%' class='boldbase' valign='top'>$Lang::tr{'esp keylife'}</td>
	    <td width='25%' valign='top'><input type='text' name='ESP_KEYLIFE' value='$cgiparams{'ESP_KEYLIFE'}' size='5' /> $Lang::tr{'hours'}</td>
	    <td width='25%' class='boldbase' valign='top'>$Lang::tr{'esp grouptype'}</td>
	    <td width='25%' valign='top'><select name='ESP_GROUPTYPE'>
			<option value=''>$Lang::tr{'phase1 group'}</option>
			<option value='modp4096' $checked{'ESP_GROUPTYPE'}{'modp4096'}>MODP-4096</option>
			<option value='modp3072' $checked{'ESP_GROUPTYPE'}{'modp3072'}>MODP-3072</option>
			<option value='modp2048' $checked{'ESP_GROUPTYPE'}{'modp2048'}>MODP-2048</option>
			<option value='modp1536' $checked{'ESP_GROUPTYPE'}{'modp1536'}>MODP-1536</option>
			<option value='modp1024' $checked{'ESP_GROUPTYPE'}{'modp1024'}>MODP-1024</option>
			<option value='modp768'  $checked{'ESP_GROUPTYPE'}{'modp768'}>MODP-768</option></select></td></tr>
	<tr><td colspan='4'><input type='CHECKBOX' name='ONLY_PROPOSED' $checked{'ONLY_PROPOSED'}{'on'} />
		$Lang::tr{'use only proposed settings'}</td></tr>
	</table>
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
    &General::readhash("${General::swroot}/vpn/settings", \%cgiparams);
    &General::readhasharray("${General::swroot}/vpn/caconfig", \%cahash);
    &General::readhasharray("${General::swroot}/vpn/config", \%confighash);

    my @status = `/usr/sbin/ipsec auto --status`;

    # suggest a default name for this side
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
    # no IP found, use %defaultroute
    $cgiparams{'VPN_IP'} ='%defaultroute' if ($cgiparams{'VPN_IP'} eq '');
    
    $cgiparams{'VPN_DELAYED_START'} = 0 if (! defined ($cgiparams{'VPN_DELAYED_START'}));
    map ($checked{$_} = $cgiparams{$_} eq 'on' ? "checked='checked'" : '',
	('ENABLED','ENABLED_BLUE','DBG_CRYPT','DBG_PARSING','DBG_EMITTING','DBG_CONTROL',
	 'DBG_KLIPS','DBG_DNS','DBG_NAT_T'));


    &Header::showhttpheaders();
    &Header::openpage($Lang::tr{'vpn configuration main'}, 1, '');
    &Header::openbigbox('100%', 'LEFT', '', $errormessage);

    if ($errormessage) {
	&Header::openbox('100%', 'LEFT', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
    }

    &Header::openbox('100%', 'LEFT', $Lang::tr{'global settings'});
    print <<END
    <form method='post'>
    <table width='100%'>
    <tr>
	<td width='25%' class='base' nowrap='nowrap'>$Lang::tr{'local vpn hostname/ip'}:</td>
	<td width='25%'><input type='text' name='VPN_IP' value='$cgiparams{'VPN_IP'}' /></td>
	<td width='25%' class='base'>$Lang::tr{'enabled'}<input type='checkbox' name='ENABLED' $checked{'ENABLED'} /></td>
    </tr>
END
    ;
    if ($netsettings{'BLUE_DEV'} ne '') {
    print <<END
    <tr>
	<td width='25%' class='base' nowrap='nowrap'>$Lang::tr{'vpn on blue'}:</td>
	<td></td>
	<td width='25%' class='base'>$Lang::tr{'enabled'}<input type='checkbox' name='ENABLED_BLUE' $checked{'ENABLED_BLUE'} /></td>
    </tr>
END
    ;
    }
print <<END
	<td width='25%' class='base' nowrap='nowrap'>$Lang::tr{'vpn delayed start'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td width='25%'><input type='text' name='VPN_DELAYED_START' value='$cgiparams{'VPN_DELAYED_START'}' /></td>
	<td width='25%' class='base' nowrap='nowrap'>$Lang::tr{'override mtu'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td width='25%'><input type='text' name='VPN_OVERRIDE_MTU' value='$cgiparams{'VPN_OVERRIDE_MTU'}' /></td>
</table>
<table width='100%'>
<tr><td>PLUTO DEBUG</td>
    <td>crypt:<input type='checkbox' name='DBG_CRYPT' $checked{'DBG_CRYPT'} /></td>
    <td>parsing:<input type='checkbox' name='DBG_PARSING' $checked{'DBG_PARSING'} /></td>
    <td>emitting:<input type='checkbox' name='DBG_EMITTING' $checked{'DBG_EMITTING'} /></td>
    <td>control:<input type='checkbox' name='DBG_CONTROL' $checked{'DBG_CONTROL'} /></td>
    <td>klips:<input type='checkbox' name='DBG_KLIPS' $checked{'DBG_KLIPS'} /></td>
    <td>dns:<input type='checkbox' name='DBG_DNS' $checked{'DBG_DNS'} /></td>
    <td>nat_t:<input type='checkbox' name='DBG_NAT_T' $checked{'DBG_NAT_T'} /></td>
</tr></table>
<hr />
<table width='100%'>
<tr>
    <td class='base' valign='top'><img src='/blob.gif' alt='*' /></td>
    <td width='70%' class='base'>$Lang::tr{'vpn delayed start help'}</td>
    <td width='30%' align='center' class='base'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
</tr>
</table>
END
;	        
    print "</form>";
    &Header::closebox();

    &Header::openbox('100%', 'LEFT', $Lang::tr{'connection status and controlc'});
    print <<END
    <table width='100%' border='0' cellspacing='1' cellpadding='0'>
    <tr>
	<td width='10%' class='boldbase' align='center'><b>$Lang::tr{'name'}</b></td>
	<td width='22%' class='boldbase' align='center'><b>$Lang::tr{'type'}</b></td>
	<td width='23%' class='boldbase' align='center'><b>$Lang::tr{'common name'}</b></td>
	<td width='30%' class='boldbase' align='center'><b>$Lang::tr{'remark'}</b><br /><img src='/images/null.gif' width='125' height='1' border='0' alt='L2089' /></td>
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
	print "<td align='center'>$confighash{$key}[25]</td>";
	my $active = "<table cellpadding='2' cellspacing='0' bgcolor='${Header::colourred}' width='100%'><tr><td align='center'><b><font color='#FFFFFF'>$Lang::tr{'capsclosed'}</font></b></td></tr></table>";
	if ($confighash{$key}[0] eq 'off') {
	    $active = "<table cellpadding='2' cellspacing='0' bgcolor='${Header::colourblue}' width='100%'><tr><td align='center'><b><font color='#FFFFFF'>$Lang::tr{'capsclosed'}</font></b></td></tr></table>";
	} else {
	    foreach my $line (@status) {
		if ($line =~ /\"$confighash{$key}[1]\".*IPsec SA established/) {
		    $active = "<table cellpadding='2' cellspacing='0' bgcolor='${Header::colourgreen}' width='100%'><tr><td align='center'><b><font color='#FFFFFF'>$Lang::tr{'capsopen'}</font></b></td></tr></table>";
		}
	    }
	}
	print <<END
	<td align='center'>$active</td>
	<form method='post' name='frm${key}a'><td align='center'>
	    <input type='image'  name='$Lang::tr{'restart'}' src='/images/reload.gif' alt='$Lang::tr{'restart'}' title='$Lang::tr{'restart'}' border='0' />
	    <input type='hidden' name='ACTION' value='$Lang::tr{'restart'}' />
	    <input type='hidden' name='KEY' value='$key' />
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
	if ($confighash{$key}[4] eq 'cert' && -f "${General::swroot}/certs/$confighash{$key}[1].p12") { 
	    print <<END
	    <form method='post' name='frm${key}c'><td align='center'>
		<input type='image' name='$Lang::tr{'download pkcs12 file'}' src='/images/floppy.gif' alt='$Lang::tr{'download pkcs12 file'}' title='$Lang::tr{'download pkcs12 file'}' border='0' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'download pkcs12 file'}' />
		<input type='hidden' name='KEY' value='$key' />
	    </td></form>
END
	; } elsif ($confighash{$key}[4] eq 'cert') {
	    print <<END
	    <form method='post' name='frm${key}c'><td align='center'>
		<input type='image' name='$Lang::tr{'download certificate'}' src='/images/floppy.gif' alt='$Lang::tr{'download certificate'}' title='$Lang::tr{'download certificate'}' border='0' />
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
	<td>&nbsp; &nbsp; <img src='/images/floppy.gif' alt='?FLOPPY' /></td>
	<td class='base'>$Lang::tr{'download certificate'}</td>
	<td>&nbsp; &nbsp; <img src='/images/reload.gif' alt='?RELOAD'/></td>
	<td class='base'>$Lang::tr{'restart'}</td>
    </tr>
    </table>
END
    ;
    }

    print <<END
    <table width='100%'>
    <form method='post'>
    <tr><td align='center' colspan='9'><input type='submit' name='ACTION' value='$Lang::tr{'add'}' /></td></tr>
    </form>
    </table>
END
    ;
    &Header::closebox();

    &Header::openbox('100%', 'LEFT', "$Lang::tr{'certificate authorities'}:");
    print <<EOF
    <table width='100%' border='0' cellspacing='1' cellpadding='0'>
    <tr>
	<td width='25%' class='boldbase' align='center'><b>$Lang::tr{'name'}</b></td>
	<td width='65%' class='boldbase' align='center'><b>$Lang::tr{'subject'}</b></td>
	<td width='10%' class='boldbase' colspan='3' align='center'><b>$Lang::tr{'action'}</b></td>
    </tr>
EOF
    ;
    if (-f "${General::swroot}/ca/cacert.pem") {
	my $casubject = `/usr/bin/openssl x509 -text -in ${General::swroot}/ca/cacert.pem`;
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

    if (-f "${General::swroot}/certs/hostcert.pem") {
	my $hostsubject = `/usr/bin/openssl x509 -text -in ${General::swroot}/certs/hostcert.pem`;
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

    if (! -f "${General::swroot}/ca/cacert.pem") {
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

    # If the file contains entries, print Key to action icons
    if ( -f "${General::swroot}/ca/cacert.pem") {
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
    </tr></table></form>
END
    ;
    &Header::closebox();

    print "<div align='center'><form method='post'><input type='submit' name='ACTION' value='$Lang::tr{'reset'}' /></div></form>\n";
    print "$Lang::tr{'this feature has been sponsored by'} : ";
    print "<a href='http://www.seminolegas.com/' target='_blank'>Seminole Canada Gas Company</a>.\n";

    &Header::closebigbox();
    &Header::closepage();
