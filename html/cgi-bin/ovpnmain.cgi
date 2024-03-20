#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2023  IPFire Team  <info@ipfire.org>                     #
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
use Archive::Zip qw(:ERROR_CODES :CONSTANTS);
use CGI;
use CGI qw/:standard/;
use Date::Parse;
use File::Copy;
use File::Temp qw/ tempfile tempdir /;
use Imager::QRCode;
use MIME::Base32;
use MIME::Base64;
use Net::DNS;
use Net::Ping;
use Net::Telnet;
use Sort::Naturally;
use URI::Encode qw(uri_encode uri_decode);;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/header.pl";
require "${General::swroot}/countries.pl";
require "${General::swroot}/location-functions.pl";

# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);

# Supported ciphers for NCP
my @SUPPORTED_CIPHERS = (
	"AES-256-GCM",
	"AES-128-GCM",
	"AES-256-CBC",
	"AES-128-CBC",
	"CHACHA20-POLY1305",
);

my $DEFAULT_CIPHERS = "AES-256-GCM|AES-128-GCM|CHACHA20-POLY1305";

# Translations for the cipher selection
my %CIPHERS = (
	# AES
	"AES-256-GCM" => $Lang::tr{'AES-256-GCM'},
	"AES-128-GCM" => $Lang::tr{'AES-128-GCM'},
	"AES-256-CBC" => $Lang::tr{'AES-256-CBC'},
	"AES-128-CBC" => $Lang::tr{'AES-128-CBC'},

	# ChaCha20-Poly1305
	"CHACHA20-POLY1305" => $Lang::tr{'CHACHA20-POLY1305'},
);

# Use the precomputed DH paramter from RFC7919
my $DHPARAM = "/etc/ssl/ffdhe4096.pem";

###
### Initialize variables
###
my %ccdconfhash=();
my %ccdroutehash=();
my %ccdroute2hash=();
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
my $routes_push_file = "${General::swroot}/ovpn/routes_push";
my $confighost="${General::swroot}/fwhosts/customhosts";
my $configgrp="${General::swroot}/fwhosts/customgroups";
my $customnet="${General::swroot}/fwhosts/customnetworks";
my $name;
my $col="";
my $local_serverconf = "${General::swroot}/ovpn/scripts/server.conf.local";
my $local_clientconf = "${General::swroot}/ovpn/scripts/client.conf.local";

# Read Ethernet configuration
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

# Set default CGI parameters
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
$cgiparams{'ROUTES_PUSH'} = '';
$cgiparams{'MSSFIX'} = '';
$cgiparams{'number'} = '';
$cgiparams{'DCIPHER'} = '';
$cgiparams{'DAUTH'} = '';
$cgiparams{'TLSAUTH'} = '';

# Load CGI parameters
&Header::getcgihash(\%cgiparams, {'wantfile' => 1, 'filevar' => 'FH'});

# Add CCD files if not already present
unless (-e $routes_push_file) {
	open(RPF, ">$routes_push_file");
	close(RPF);
}

# Create additional files it not already existing
unless (-e "$local_serverconf") {
	open(LSC, ">$local_serverconf");
       close (LSC);
}

unless (-e "$local_clientconf") {
       open(LCC, ">$local_clientconf");
       close (LCC);
}

###
### Useful functions
###
sub iscertlegacy
{
	my $file=$_[0];
	my @certinfo = &General::system_output("/usr/bin/openssl", "pkcs12", "-info", "-nodes",
	"-in", "$file.p12", "-noout", "-passin", "pass:''");
	if (index ($certinfo[0], "MAC: sha1") != -1) {
		return 1;
	}
	return 0;
}

sub cleanssldatabase() {
	if (open(FILE, ">${General::swroot}/ovpn/certs/serial")) {
		print FILE "01";
		close FILE;
	}

	if (open(FILE, ">${General::swroot}/ovpn/certs/index.txt")) {
		print FILE "";
		close FILE;
	}

	if (open(FILE, ">${General::swroot}/ovpn/certs/index.txt.attr")) {
		print FILE "";
		close FILE;
	}

	unlink("${General::swroot}/ovpn/certs/index.txt.old");
	unlink("${General::swroot}/ovpn/certs/index.txt.attr.old");
	unlink("${General::swroot}/ovpn/certs/serial.old");
	unlink("${General::swroot}/ovpn/certs/01.pem");
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

sub writeserverconf {
    my %sovpnsettings = ();
    my @temp = ();
    &General::readhash("${General::swroot}/ovpn/settings", \%sovpnsettings);
    &read_routepushfile;

    open(CONF,    ">${General::swroot}/ovpn/server.conf") or die "Unable to open ${General::swroot}/ovpn/server.conf: $!";
    flock CONF, 2;
    print CONF "#OpenVPN Server conf\n";
    print CONF "\n";
    print CONF "daemon openvpnserver\n";
    print CONF "writepid /var/run/openvpn.pid\n";
    print CONF "#DAN prepare OpenVPN for listening on blue and orange\n";
    print CONF ";local $sovpnsettings{'VPN_IP'}\n";
    print CONF "dev tun\n";
    print CONF "proto $sovpnsettings{'DPROTOCOL'}\n";
    print CONF "port $sovpnsettings{'DDEST_PORT'}\n";
    print CONF "script-security 3\n";
    print CONF "ifconfig-pool-persist /var/ipfire/ovpn/ovpn-leases.db 3600\n";
    print CONF "client-config-dir /var/ipfire/ovpn/ccd\n";
    print CONF "tls-server\n";
    print CONF "ca ${General::swroot}/ovpn/ca/cacert.pem\n";
    print CONF "cert ${General::swroot}/ovpn/certs/servercert.pem\n";
    print CONF "key ${General::swroot}/ovpn/certs/serverkey.pem\n";
    print CONF "dh $DHPARAM\n";
    my @tempovpnsubnet = split("\/",$sovpnsettings{'DOVPN_SUBNET'});
    print CONF "server $tempovpnsubnet[0] $tempovpnsubnet[1]\n";
    #print CONF "push \"route $netsettings{'GREEN_NETADDRESS'} $netsettings{'GREEN_NETMASK'}\"\n";

    print CONF "tun-mtu $sovpnsettings{'DMTU'}\n";

    if ($vpnsettings{'ROUTES_PUSH'} ne '') {
		@temp = split(/\n/,$vpnsettings{'ROUTES_PUSH'});
		foreach (@temp)
		{
			@tempovpnsubnet = split("\/",&General::ipcidr2msk($_));
			print CONF "push \"route " . $tempovpnsubnet[0]. " " .  $tempovpnsubnet[1] . "\"\n";
		}
	}

	my %ccdconfhash=();
	&General::readhasharray("${General::swroot}/ovpn/ccd.conf", \%ccdconfhash);
	foreach my $key (keys %ccdconfhash) {
		my $a=$ccdconfhash{$key}[1];
		my ($b,$c) = split (/\//, $a);
		print CONF "route $b ".&General::cidrtosub($c)."\n";
	}
	my %ccdroutehash=();
	&General::readhasharray("${General::swroot}/ovpn/ccdroute", \%ccdroutehash);
	foreach my $key (keys %ccdroutehash) {
		foreach my $i ( 1 .. $#{$ccdroutehash{$key}}){
			my ($a,$b)=split (/\//,$ccdroutehash{$key}[$i]);
			print CONF "route $a $b\n";
		}
	}

	if ($sovpnsettings{CLIENT2CLIENT} eq 'on') {
	print CONF "client-to-client\n";
    }
    if ($sovpnsettings{MSSFIX} eq 'on') {
		print CONF "mssfix\n";
    } else {
		print CONF "mssfix 0\n";
    }
    if ($sovpnsettings{FRAGMENT} ne '' && $sovpnsettings{'DPROTOCOL'} ne 'tcp') {
		print CONF "fragment $sovpnsettings{'FRAGMENT'}\n";
    }

    if ($sovpnsettings{KEEPALIVE_1} > 0 && $sovpnsettings{KEEPALIVE_2} > 0) {
	print CONF "keepalive $sovpnsettings{'KEEPALIVE_1'} $sovpnsettings{'KEEPALIVE_2'}\n";
    }
    print CONF "status-version 1\n";
    print CONF "status /var/run/ovpnserver.log 30\n";

	# Cryptography
	if ($sovpnsettings{'DATACIPHERS'} eq '') {
		print CONF "ncp-disable\n";
	} else {
		print CONF "data-ciphers " . $sovpnsettings{'DATACIPHERS'} =~ s/\|/:/gr . "\n";
	}

	# Enable fallback cipher?
	if ($sovpnsettings{'DCIPHER'} ne '') {
	    print CONF "data-ciphers-fallback $sovpnsettings{'DCIPHER'}\n";
	}

	print CONF "auth $sovpnsettings{'DAUTH'}\n";
    # Set TLSv2 as minimum
    print CONF "tls-version-min 1.2\n";

    if ($sovpnsettings{'TLSAUTH'} eq 'on') {
	print CONF "tls-auth ${General::swroot}/ovpn/certs/ta.key\n";
    }

	# Compression
	# Use migration to support clients that have compression enabled, but disable
	# compression for everybody else.
	print CONF "compress migrate\n";

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

    if ($sovpnsettings{MAX_CLIENTS} eq '') {
	print CONF "max-clients 100\n";
    }
    if ($sovpnsettings{MAX_CLIENTS} ne '') {
	print CONF "max-clients $sovpnsettings{MAX_CLIENTS}\n";
    }
    print CONF "tls-verify /usr/lib/openvpn/verify\n";
    print CONF "crl-verify /var/ipfire/ovpn/crls/cacrl.pem\n";
    print CONF "auth-user-pass-optional\n";
    print CONF "reneg-sec 86400\n";
    print CONF "user nobody\n";
    print CONF "group nobody\n";
    print CONF "persist-key\n";
    print CONF "persist-tun\n";
	if ($sovpnsettings{LOG_VERB} ne '') {
		print CONF "verb $sovpnsettings{LOG_VERB}\n";
	} else {
		print CONF "verb 3\n";
	}

    print CONF "# Log clients connecting/disconnecting\n";
    print CONF "client-connect \"/usr/sbin/openvpn-metrics client-connect\"\n";
    print CONF "client-disconnect \"/usr/sbin/openvpn-metrics client-disconnect\"\n";
    print CONF "\n";

    print CONF "# Enable Management Socket\n";
    print CONF "management /var/run/openvpn.sock unix\n";
    print CONF "management-client-auth\n";

    # Print server.conf.local if entries exist to server.conf
    if ( !-z $local_serverconf  && $sovpnsettings{'ADDITIONAL_CONFIGS'} eq 'on') {
       open (LSC, "$local_serverconf");
               print CONF "\n#---------------------------\n";
               print CONF "# Start of custom directives\n";
               print CONF "# from server.conf.local\n";
               print CONF "#---------------------------\n\n";
       while (<LSC>) {
               print CONF $_;
       }
               print CONF "\n#-----------------------------\n";
               print CONF "# End of custom directives\n";
               print CONF "#-----------------------------\n";
       close (LSC);
    }
    print CONF "\n";

    close(CONF);
}

##
## CCD Name
##

# Checks a ccdname for letters, numbers and spaces
sub validccdname($) {
	my $name = shift;

	# name should be at least one character in length
	# but no more than 63 characters
	if (length ($name) < 1 || length ($name) > 63) {
		return 0;
	}

	# Only valid characters are a-z, A-Z, 0-9, space and -
	if ($name !~ /^[a-zA-Z0-9 -]*$/) {
		return 0;
	}

	return 1;
}

sub delccdnet($) {
	my $name = shift;

	my %conns = ();
	my %subnets = ();

	# Load all connections
	&General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%conns);

	# Check if the subnet is in use
	foreach my $key (keys %conns) {
		if ($conns{$key}[32] eq $name) {
			$errormessage = $Lang::tr{'ccd err hostinnet'};
			return 1;
		}
	}

	# Load all subnets
	&General::readhasharray("${General::swroot}/ovpn/ccd.conf", \%subnets);

	# Remove the subnet
	foreach my $key (keys %subnets) {
			if ($subnets{$key}[0] eq $name){
				delete $subnets{$key};
			}
	}

	# Write the subnets back
	&General::writehasharray("${General::swroot}/ovpn/ccd.conf", \%subnets);

	# Update the server configuration to remove routes
	&writeserverconf();

	return 0;
}

sub addccdnet
{
	my %ccdconfhash=();
	my @ccdconf=();
	my $ccdname=$_[0];
	my $ccdnet=$_[1];
	my $subcidr;
	my @ip2=();
	my $checkup;
	my $ccdip;
	my $baseaddress;


	#check name
	if ($ccdname eq '')
	{
		$errormessage=$errormessage.$Lang::tr{'ccd err name'}."<br>";
		return
	}

	if(!&validccdname($ccdname))
	{
		$errormessage=$Lang::tr{'ccd err invalidname'};
		return;
	}

	($ccdip,$subcidr) = split (/\//,$ccdnet);
	$subcidr=&General::iporsubtocidr($subcidr);
	#check subnet
	if ($subcidr > 30)
	{
		$errormessage=$Lang::tr{'ccd err invalidnet'};
		return;
	}
	#check ip
	if (!&General::validipandmask($ccdnet)){
		$errormessage=$Lang::tr{'ccd err invalidnet'};
		return;
	}

	if (!$errormessage) {
		my %ccdconfhash=();
		$baseaddress=&General::getnetworkip($ccdip,$subcidr);
		&General::readhasharray("${General::swroot}/ovpn/ccd.conf", \%ccdconfhash);
		my $key = &General::findhasharraykey (\%ccdconfhash);
		foreach my $i (0 .. 1) { $ccdconfhash{$key}[$i] = "";}
		$ccdconfhash{$key}[0] = $ccdname;
		$ccdconfhash{$key}[1] = $baseaddress."/".$subcidr;
		&General::writehasharray("${General::swroot}/ovpn/ccd.conf", \%ccdconfhash);
		&writeserverconf;
		$cgiparams{'ccdname'}='';
		$cgiparams{'ccdsubnet'}='';
		return 1;
	}
}

sub modccdnet
{

	my $newname=$_[0];
	my $oldname=$_[1];
	my %ccdconfhash=();
	my %ccdhash=();

	# Check if the new name is valid.
	if(!&validccdname($newname)) {
		$errormessage=$Lang::tr{'ccd err invalidname'};
		return;
	}

	&General::readhasharray("${General::swroot}/ovpn/ccd.conf", \%ccdconfhash);
	foreach my $key (keys %ccdconfhash) {
		if ($ccdconfhash{$key}[0] eq $oldname) {
			foreach my $key1 (keys %ccdconfhash) {
				if ($ccdconfhash{$key1}[0] eq $newname){
					$errormessage=$errormessage.$Lang::tr{'ccd err netadrexist'};
					return;
				}else{
					$ccdconfhash{$key}[0]= $newname;
					&General::writehasharray("${General::swroot}/ovpn/ccd.conf", \%ccdconfhash);
					last;
				}
			}
		}
	}

	&General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%ccdhash);
		foreach my $key (keys %ccdhash) {
			if ($ccdhash{$key}[32] eq $oldname) {
				$ccdhash{$key}[32]=$newname;
				&General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%ccdhash);
				last;
			}
		}

	return 0;
}
sub ccdmaxclients
{
	my $ccdnetwork=$_[0];
	my @octets=();
	my @subnet=();
	@octets=split("\/",$ccdnetwork);
	@subnet= split /\./, &General::cidrtosub($octets[1]);
	my ($a,$b,$c,$d,$e);
	$a=256-$subnet[0];
	$b=256-$subnet[1];
	$c=256-$subnet[2];
	$d=256-$subnet[3];
	$e=($a*$b*$c*$d)/4;
	return $e-1;
}

sub getccdadresses
{
	my $ipin=$_[0];
	my ($ip1,$ip2,$ip3,$ip4)=split  /\./, $ipin;
	my $cidr=$_[1];
	chomp($cidr);
	my $count=$_[2];
	my $hasip=$_[3];
	chomp($hasip);
	my @iprange=();
	my %ccdhash=();
	&General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%ccdhash);
	$iprange[0]=$ip1.".".$ip2.".".$ip3.".".($ip4+2);
	for (my $i=1;$i<=$count;$i++) {
		my $tmpip=$iprange[$i-1];
		my $stepper=$i*4;
		$iprange[$i]= &Network::bin2ip(&Network::ip2bin($tmpip) + 4);
	}
	my $r=0;
	foreach my $key (keys %ccdhash) {
		$r=0;
		foreach  my $tmp (@iprange){
			my ($net,$sub) = split (/\//,$ccdhash{$key}[33]);
			if ($net eq $tmp) {
				if ( $hasip ne  $ccdhash{$key}[33] ){
					splice (@iprange,$r,1);
				}
			}
			$r++;
		}
	}
	return @iprange;
}

sub fillselectbox
{
	my $boxname=$_[1];
	my ($ccdip,$subcidr) = split("/",$_[0]);
	my $tz=$_[2];
	my @allccdips=&getccdadresses($ccdip,$subcidr,&ccdmaxclients($ccdip."/".$subcidr),$tz);
	print"<select name='$boxname' STYLE='font-family : arial; font-size : 9pt; width:130px;' >";
	foreach (@allccdips) {
		my $ip=$_."/30";
		chomp($ip);
		print "<option value='$ip' ";
		if ( $ip eq $cgiparams{$boxname} ){
			print"selected";
		}
		print ">$ip</option>";
	}
	print "</select>";
}

sub hostsinnet
{
	my $name=$_[0];
	my %ccdhash=();
	my $i=0;
	&General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%ccdhash);
	foreach my $key (keys %ccdhash) {
		if ($ccdhash{$key}[32] eq $name){ $i++;}
	}
	return $i;
}

sub check_routes_push
{
			my $val=$_[0];
			my ($ip,$cidr) = split (/\//, $val);
			##check for existing routes in routes_push
			if (-e "${General::swroot}/ovpn/routes_push") {
				open(FILE,"${General::swroot}/ovpn/routes_push");
				while (<FILE>) {
					$_=~s/\s*$//g;

					my ($ip2,$cidr2) = split (/\//,"$_");
					my $val2=$ip2."/".&General::iporsubtodec($cidr2);

					if($val eq $val2){
						return 0;
					}
					#subnetcheck
					if (&General::IpInSubnet ($ip,$ip2,&General::iporsubtodec($cidr2))){
						return 0;
					}
				};
				close(FILE);
			}
	return 1;
}

sub check_ccdroute
{
	my %ccdroutehash=();
	my $val=$_[0];
	my ($ip,$cidr) = split (/\//, $val);
	#check for existing routes in ccdroute
	&General::readhasharray("${General::swroot}/ovpn/ccdroute", \%ccdroutehash);
	foreach my $key (keys %ccdroutehash) {
		foreach my $i (1 .. $#{$ccdroutehash{$key}}) {
			if (&General::iporsubtodec($val) eq $ccdroutehash{$key}[$i] && $ccdroutehash{$key}[0] ne $cgiparams{'NAME'}){
				return 0;
			}
			my ($ip2,$cidr2) = split (/\//,$ccdroutehash{$key}[$i]);
			#subnetcheck
			if (&General::IpInSubnet ($ip,$ip2,$cidr2)&& $ccdroutehash{$key}[0] ne $cgiparams{'NAME'} ){
				return 0;
			}
		}
	}
	return 1;
}
sub check_ccdconf
{
	my %ccdconfhash=();
	my $val=$_[0];
	my ($ip,$cidr) = split (/\//, $val);
	#check for existing routes in ccdroute
	&General::readhasharray("${General::swroot}/ovpn/ccd.conf", \%ccdconfhash);
	foreach my $key (keys %ccdconfhash) {
		if (&General::iporsubtocidr($val) eq $ccdconfhash{$key}[1]){
				return 0;
			}
			my ($ip2,$cidr2) = split (/\//,$ccdconfhash{$key}[1]);
			#subnetcheck
			if (&General::IpInSubnet ($ip,$ip2,&General::cidrtosub($cidr2))){
				return 0;
			}

	}
	return 1;
}

sub validdotmask
{
	my $ipdotmask = $_[0];
	if (&General::validip($ipdotmask)) { return 0; }
	if (!($ipdotmask =~ /^(.*?)\/(.*?)$/)) {  }
	my $mask = $2;
	if (($mask =~ /\./ )) { return 0; }
  return 1;
}

# -------------------------------------------------------------------

sub write_routepushfile
{
	open(FILE, ">$routes_push_file");
	flock(FILE, 2);
	if ($vpnsettings{'ROUTES_PUSH'} ne '') {
		print FILE $vpnsettings{'ROUTES_PUSH'};
	}
	close(FILE);
}

sub read_routepushfile
{
	if (-e "$routes_push_file") {
		open(FILE,"$routes_push_file");
		delete $vpnsettings{'ROUTES_PUSH'};
		while (<FILE>) { $vpnsettings{'ROUTES_PUSH'} .= $_ };
		close(FILE);
		$cgiparams{'ROUTES_PUSH'} = $vpnsettings{'ROUTES_PUSH'};

	}
}

sub writecollectdconf {
	my $vpncollectd;
	my %ccdhash=();

	open(COLLECTDVPN, ">${General::swroot}/ovpn/collectd.vpn") or die "Unable to open collectd.vpn: $!";
	print COLLECTDVPN "Loadplugin openvpn\n";
	print COLLECTDVPN "\n";
	print COLLECTDVPN "<Plugin openvpn>\n";
	print COLLECTDVPN "Statusfile \"/var/run/ovpnserver.log\"\n";

	&General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%ccdhash);
	foreach my $key (keys %ccdhash) {
		if ($ccdhash{$key}[0] eq 'on' && $ccdhash{$key}[3] eq 'net') {
			print COLLECTDVPN "Statusfile \"/var/run/openvpn/$ccdhash{$key}[1]-n2n\"\n";
		}
	}

	print COLLECTDVPN "</Plugin>\n";
	close(COLLECTDVPN);

	# Reload collectd afterwards
	&General::system("/usr/local/bin/collectdctrl", "restart");
}

###
### OpenVPN Server Control
###

if ($cgiparams{'ACTION'} eq $Lang::tr{'start ovpn server'}) {
	&General::system("/usr/local/bin/openvpnctrl", "-s");

} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'stop ovpn server'}) {
	&General::system("/usr/local/bin/openvpnctrl", "-k");
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
    $vpnsettings{'ADDITIONAL_CONFIGS'} = $cgiparams{'ADDITIONAL_CONFIGS'};
    $vpnsettings{'DHCP_DOMAIN'} = $cgiparams{'DHCP_DOMAIN'};
    $vpnsettings{'DHCP_DNS'} = $cgiparams{'DHCP_DNS'};
    $vpnsettings{'DHCP_WINS'} = $cgiparams{'DHCP_WINS'};
    $vpnsettings{'ROUTES_PUSH'} = $cgiparams{'ROUTES_PUSH'};
    $vpnsettings{'DATACIPHERS'} = $cgiparams{'DATACIPHERS'};
    $vpnsettings{'DCIPHER'} = $cgiparams{'DCIPHER'};
    $vpnsettings{'DAUTH'} = $cgiparams{'DAUTH'};
    $vpnsettings{'TLSAUTH'} = $cgiparams{'TLSAUTH'};
    my @temp=();

	# We must have at least one cipher selected
	if ($cgiparams{'DATACIPHERS'} eq '') {
		$errormessage = $Lang::tr{'ovpn no cipher selected'};
		goto ADV_ERROR;
	}

	# Split data ciphers
	my @dataciphers = split(/\|/, $cgiparams{'DATACIPHERS'});

	# Check if all ciphers are supported
	foreach my $cipher (@dataciphers) {
		if (!grep(/^$cipher$/, @SUPPORTED_CIPHERS)) {
			$errormessage = $Lang::tr{'ovpn unsupported cipher selected'};
			goto ADV_ERROR;
		}
	}

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
	unless (&General::validdomainname($cgiparams{'DHCP_DOMAIN'}) || &General::validip($cgiparams{'DHCP_DOMAIN'})) {
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
    if ($cgiparams{'ROUTES_PUSH'} ne ''){
	@temp = split(/\n/,$cgiparams{'ROUTES_PUSH'});
    	undef $vpnsettings{'ROUTES_PUSH'};

   	foreach my $tmpip (@temp)
	{
		s/^\s+//g; s/\s+$//g;

		if ($tmpip)
		{
			$tmpip=~s/\s*$//g;
			unless (&General::validipandmask($tmpip)) {
				$errormessage = "$tmpip ".$Lang::tr{'ovpn errmsg invalid ip or mask'};
				goto ADV_ERROR;
			}
			my ($ip, $cidr) = split("\/",&General::ipcidr2msk($tmpip));

			if ($ip eq $netsettings{'GREEN_NETADDRESS'} && $cidr eq $netsettings{'GREEN_NETMASK'}) {
				$errormessage = $Lang::tr{'ovpn errmsg green already pushed'};
				goto ADV_ERROR;
			}

			my %ccdroutehash=();
			&General::readhasharray("${General::swroot}/ovpn/ccdroute", \%ccdroutehash);
			foreach my $key (keys %ccdroutehash) {
				foreach my $i (1 .. $#{$ccdroutehash{$key}}) {
					if ( $ip."/".$cidr eq $ccdroutehash{$key}[$i] ){
						$errormessage="Route $ip\/$cidr ".$Lang::tr{'ccd err inuse'}." $ccdroutehash{$key}[0]" ;
						goto ADV_ERROR;
					}
					my ($ip2,$cidr2) = split(/\//,$ccdroutehash{$key}[$i]);
					if (&General::IpInSubnet ($ip,$ip2,$cidr2)){
						$errormessage="Route $ip\/$cidr ".$Lang::tr{'ccd err inuse'}." $ccdroutehash{$key}[0]" ;
						goto ADV_ERROR;
					}
				}
			}

			$vpnsettings{'ROUTES_PUSH'} .= $tmpip."\n";
		}
	}
    &write_routepushfile;
	undef $vpnsettings{'ROUTES_PUSH'};
    }
	else {
	undef $vpnsettings{'ROUTES_PUSH'};
	&write_routepushfile;
    }
    if ((length($cgiparams{'MAX_CLIENTS'}) == 0) || (($cgiparams{'MAX_CLIENTS'}) < 1 ) || (($cgiparams{'MAX_CLIENTS'}) > 1024 )) {
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

if ($cgiparams{'ACTION'} eq $Lang::tr{'save'} && $cgiparams{'TYPE'} eq 'net' && $cgiparams{'SIDE'} eq 'server')
{

my @remsubnet = split(/\//,$cgiparams{'REMOTE_SUBNET'});
my @ovsubnettemp =  split(/\./,$cgiparams{'OVPN_SUBNET'});
my $ovsubnet =  "$ovsubnettemp[0].$ovsubnettemp[1].$ovsubnettemp[2]";
my $tunmtu =  '';

unless(-d "${General::swroot}/ovpn/n2nconf/"){mkdir "${General::swroot}/ovpn/n2nconf", 0755 or die "Unable to create dir $!";}
unless(-d "${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}"){mkdir "${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}", 0770 or die "Unable to create dir $!";}

  open(SERVERCONF,    ">${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf") or die "Unable to open ${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf: $!";

  flock SERVERCONF, 2;
  print SERVERCONF "# IPFire n2n Open VPN Server Config by ummeegge und m.a.d\n";
  print SERVERCONF "\n";
  print SERVERCONF "# User Security\n";
  print SERVERCONF "user nobody\n";
  print SERVERCONF "group nobody\n";
  print SERVERCONF "persist-tun\n";
  print SERVERCONF "persist-key\n";
  print SERVERCONF "script-security 2\n";
  print SERVERCONF "# IP/DNS for remote Server Gateway\n";

  if ($cgiparams{'REMOTE'} ne '') {
  print SERVERCONF "remote $cgiparams{'REMOTE'}\n";
  }

  print SERVERCONF "float\n";
  print SERVERCONF "# IP adresses of the VPN Subnet\n";
  print SERVERCONF "ifconfig $ovsubnet.1 $ovsubnet.2\n";
  print SERVERCONF "# Client Gateway Network\n";
  print SERVERCONF "route $remsubnet[0] $remsubnet[1]\n";
  print SERVERCONF "up \"/etc/init.d/static-routes start\"\n";
  print SERVERCONF "# tun Device\n";
  print SERVERCONF "dev tun\n";
  print SERVERCONF "#Logfile for statistics\n";
  print SERVERCONF "status-version 1\n";
  print SERVERCONF "status /var/run/openvpn/$cgiparams{'NAME'}-n2n 10\n";
  print SERVERCONF "# Port and Protokol\n";
  print SERVERCONF "port $cgiparams{'DEST_PORT'}\n";

  if ($cgiparams{'PROTOCOL'} eq 'tcp') {
  print SERVERCONF "proto tcp4-server\n";
  print SERVERCONF "# Packet size\n";
  if ($cgiparams{'MTU'} eq '') {$tunmtu = '1400'} else {$tunmtu = $cgiparams{'MTU'}};
  print SERVERCONF "tun-mtu $tunmtu\n";
  }

  if ($cgiparams{'PROTOCOL'} eq 'udp') {
  print SERVERCONF "proto udp4\n";
  print SERVERCONF "# Paketsize\n";
  if ($cgiparams{'MTU'} eq '') {$tunmtu = '1500'} else {$tunmtu = $cgiparams{'MTU'}};
  print SERVERCONF "tun-mtu $tunmtu\n";
  if ($cgiparams{'FRAGMENT'} ne '') {print SERVERCONF "fragment $cgiparams{'FRAGMENT'}\n";}
  if ($cgiparams{'MSSFIX'} eq 'on') {print SERVERCONF "mssfix\n"; } else { print SERVERCONF "mssfix 0\n" };
  }

  print SERVERCONF "# Auth. Server\n";
  print SERVERCONF "tls-server\n";
  print SERVERCONF "ca ${General::swroot}/ovpn/ca/cacert.pem\n";
  print SERVERCONF "cert ${General::swroot}/ovpn/certs/servercert.pem\n";
  print SERVERCONF "key ${General::swroot}/ovpn/certs/serverkey.pem\n";
  print SERVERCONF "dh $DHPARAM\n";
  print SERVERCONF "# Cipher\n";
  print SERVERCONF "cipher $cgiparams{'DCIPHER'}\n";

  # If GCM cipher is used, do not use --auth
  if (($cgiparams{'DCIPHER'} eq 'AES-256-GCM') ||
      ($cgiparams{'DCIPHER'} eq 'AES-192-GCM') ||
      ($cgiparams{'DCIPHER'} eq 'AES-128-GCM')) {
    print SERVERCONF unless "# HMAC algorithm\n";
    print SERVERCONF unless "auth $cgiparams{'DAUTH'}\n";
  } else {
    print SERVERCONF "# HMAC algorithm\n";
    print SERVERCONF "auth $cgiparams{'DAUTH'}\n";
  }

  # Set TLSv1.2 as minimum
  print SERVERCONF "tls-version-min 1.2\n";

  if ($cgiparams{'COMPLZO'} eq 'on') {
   print SERVERCONF "# Enable Compression\n";
   print SERVERCONF "comp-lzo\n";
     }
  print SERVERCONF "# Debug Level\n";
  print SERVERCONF "verb 3\n";
  print SERVERCONF "# Tunnel check\n";
  print SERVERCONF "keepalive 10 60\n";
  print SERVERCONF "# Start as daemon\n";
  print SERVERCONF "daemon $cgiparams{'NAME'}n2n\n";
  print SERVERCONF "writepid /var/run/$cgiparams{'NAME'}n2n.pid\n";
  print SERVERCONF "# Activate Management Interface and Port\n";
  if ($cgiparams{'OVPN_MGMT'} eq '') {print SERVERCONF "management localhost $cgiparams{'DEST_PORT'}\n"}
  else {print SERVERCONF "management localhost $cgiparams{'OVPN_MGMT'}\n"};
  close(SERVERCONF);

}

if ($cgiparams{'ACTION'} eq $Lang::tr{'save'} && $cgiparams{'TYPE'} eq 'net' && $cgiparams{'SIDE'} eq 'client')
{

        my @ovsubnettemp =  split(/\./,$cgiparams{'OVPN_SUBNET'});
        my $ovsubnet =  "$ovsubnettemp[0].$ovsubnettemp[1].$ovsubnettemp[2]";
        my @remsubnet =  split(/\//,$cgiparams{'REMOTE_SUBNET'});
        my $tunmtu =  '';

unless(-d "${General::swroot}/ovpn/n2nconf/"){mkdir "${General::swroot}/ovpn/n2nconf", 0755 or die "Unable to create dir $!";}
unless(-d "${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}"){mkdir "${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}", 0770 or die "Unable to create dir $!";}

  open(CLIENTCONF,    ">${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf") or die "Unable to open ${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf: $!";

  flock CLIENTCONF, 2;
  print CLIENTCONF "# IPFire rewritten n2n Open VPN Client Config by ummeegge und m.a.d\n";
  print CLIENTCONF "#\n";
  print CLIENTCONF "# User Security\n";
  print CLIENTCONF "user nobody\n";
  print CLIENTCONF "group nobody\n";
  print CLIENTCONF "persist-tun\n";
  print CLIENTCONF "persist-key\n";
  print CLIENTCONF "script-security 2\n";
  print CLIENTCONF "# IP/DNS for remote Server Gateway\n";
  print CLIENTCONF "remote $cgiparams{'REMOTE'}\n";
  print CLIENTCONF "float\n";
  print CLIENTCONF "# IP adresses of the VPN Subnet\n";
  print CLIENTCONF "ifconfig $ovsubnet.2 $ovsubnet.1\n";
  print CLIENTCONF "# Server Gateway Network\n";
  print CLIENTCONF "route $remsubnet[0] $remsubnet[1]\n";
  print CLIENTCONF "up \"/etc/init.d/static-routes start\"\n";
  print CLIENTCONF "# tun Device\n";
  print CLIENTCONF "dev tun\n";
  print CLIENTCONF "#Logfile for statistics\n";
  print CLIENTCONF "status-version 1\n";
  print CLIENTCONF "status /var/run/openvpn/$cgiparams{'NAME'}-n2n 10\n";
  print CLIENTCONF "# Port and Protokol\n";
  print CLIENTCONF "port $cgiparams{'DEST_PORT'}\n";

  if ($cgiparams{'PROTOCOL'} eq 'tcp') {
  print CLIENTCONF "proto tcp4-client\n";
  print CLIENTCONF "# Packet size\n";
  if ($cgiparams{'MTU'} eq '') {$tunmtu = '1400'} else {$tunmtu = $cgiparams{'MTU'}};
  print CLIENTCONF "tun-mtu $tunmtu\n";
  }

  if ($cgiparams{'PROTOCOL'} eq 'udp') {
  print CLIENTCONF "proto udp4\n";
  print CLIENTCONF "# Paketsize\n";
  if ($cgiparams{'MTU'} eq '') {$tunmtu = '1500'} else {$tunmtu = $cgiparams{'MTU'}};
  print CLIENTCONF "tun-mtu $tunmtu\n";
  if ($cgiparams{'FRAGMENT'} ne '') {print CLIENTCONF "fragment $cgiparams{'FRAGMENT'}\n";}
  if ($cgiparams{'MSSFIX'} eq 'on') {print CLIENTCONF "mssfix\n"; } else { print CLIENTCONF "mssfix 0\n" };
  }

  # Check host certificate if X509 is RFC3280 compliant.
  # If not, old --ns-cert-type directive will be used.
  # If appropriate key usage extension exists, new --remote-cert-tls directive will be used.
  my @hostcert = &General::system_output("/usr/bin/openssl", "x509", "-text", "-in", "${General::swroot}/ovpn/certs/servercert.pem");
  if ( ! grep(/TLS Web Server Authentication/, @hostcert)) {
       print CLIENTCONF "ns-cert-type server\n";
  } else {
       print CLIENTCONF "remote-cert-tls server\n";
  }
  print CLIENTCONF "# Auth. Client\n";
  print CLIENTCONF "tls-client\n";
  print CLIENTCONF "# Cipher\n";
  print CLIENTCONF "cipher $cgiparams{'DCIPHER'}\n";
  print CLIENTCONF "pkcs12 ${General::swroot}/ovpn/certs/$cgiparams{'NAME'}.p12\r\n";

  # If GCM cipher is used, do not use --auth
  if (($cgiparams{'DCIPHER'} eq 'AES-256-GCM') ||
      ($cgiparams{'DCIPHER'} eq 'AES-192-GCM') ||
      ($cgiparams{'DCIPHER'} eq 'AES-128-GCM')) {
    print CLIENTCONF unless "# HMAC algorithm\n";
    print CLIENTCONF unless "auth $cgiparams{'DAUTH'}\n";
  } else {
    print CLIENTCONF "# HMAC algorithm\n";
    print CLIENTCONF "auth $cgiparams{'DAUTH'}\n";
  }

  # Set TLSv1.2 as minimum
  print CLIENTCONF "tls-version-min 1.2\n";

  if ($cgiparams{'COMPLZO'} eq 'on') {
   print CLIENTCONF "# Enable Compression\n";
   print CLIENTCONF "comp-lzo\n";
  }
  print CLIENTCONF "# Debug Level\n";
  print CLIENTCONF "verb 3\n";
  print CLIENTCONF "# Tunnel check\n";
  print CLIENTCONF "keepalive 10 60\n";
  print CLIENTCONF "# Start as daemon\n";
  print CLIENTCONF "daemon $cgiparams{'NAME'}n2n\n";
  print CLIENTCONF "writepid /var/run/$cgiparams{'NAME'}n2n.pid\n";
  print CLIENTCONF "# Activate Management Interface and Port\n";
  if ($cgiparams{'OVPN_MGMT'} eq '') {print CLIENTCONF "management localhost $cgiparams{'DEST_PORT'}\n"}
  else {print CLIENTCONF "management localhost $cgiparams{'OVPN_MGMT'}\n"};
  if (&iscertlegacy("${General::swroot}/ovpn/certs/$cgiparams{'NAME'}")) {
    	print CLIENTCONF "providers legacy default\n";
  }
  close(CLIENTCONF);

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

	# Create ta.key for tls-auth if not presant
	if ($cgiparams{'TLSAUTH'} eq 'on') {
		if ( ! -e "${General::swroot}/ovpn/certs/ta.key") {
			# This system call is safe, because all arguements are passed as an array.
			system("/usr/sbin/openvpn", "--genkey", "secret", "${General::swroot}/ovpn/certs/ta.key");
			if ($?) {
				$errormessage = "$Lang::tr{'openssl produced an error'}: $?";
				goto SETTINGS_ERROR;
			}
		}
	}

    $vpnsettings{'ENABLED_BLUE'} = $cgiparams{'ENABLED_BLUE'};
    $vpnsettings{'ENABLED_ORANGE'} =$cgiparams{'ENABLED_ORANGE'};
    $vpnsettings{'ENABLED'} = $cgiparams{'ENABLED'};
    $vpnsettings{'VPN_IP'} = $cgiparams{'VPN_IP'};
    $vpnsettings{'DOVPN_SUBNET'} = $cgiparams{'DOVPN_SUBNET'};
    $vpnsettings{'DPROTOCOL'} = $cgiparams{'DPROTOCOL'};
    $vpnsettings{'DDEST_PORT'} = $cgiparams{'DDEST_PORT'};
    $vpnsettings{'DMTU'} = $cgiparams{'DMTU'};

#new settings for daemon
    &General::writehash("${General::swroot}/ovpn/settings", \%vpnsettings);
    &writeserverconf();#hier ok
SETTINGS_ERROR:
###
### Reset all step 2
###
}elsif ($cgiparams{'ACTION'} eq $Lang::tr{'remove x509'} && $cgiparams{'AREUSURE'} eq 'yes') {
    my $file = '';
    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

    # Kill all N2N connections
    &General::system("/usr/local/bin/openvpnctrl", "-kn2n");

    foreach my $key (keys %confighash) {
	my $name = $confighash{$cgiparams{'$key'}}[1];

	if ($confighash{$key}[4] eq 'cert') {
	    delete $confighash{$cgiparams{'$key'}};
	}

	&General::system("/usr/local/bin/openvpnctrl", "-drrd", "$name");
    }
    while ($file = glob("${General::swroot}/ovpn/ca/*")) {
	unlink $file;
    }
    while ($file = glob("${General::swroot}/ovpn/certs/*")) {
	unlink $file;
    }
    while ($file = glob("${General::swroot}/ovpn/crls/*")) {
	unlink $file;
    }
	&cleanssldatabase();
    if (open(FILE, ">${General::swroot}/ovpn/caconfig")) {
        print FILE "";
        close FILE;
    }
    if (open(FILE, ">${General::swroot}/ovpn/ccdroute")) {
	print FILE "";
	close FILE;
    }
    if (open(FILE, ">${General::swroot}/ovpn/ccdroute2")) {
	print FILE "";
	close FILE;
    }
    while ($file = glob("${General::swroot}/ovpn/ccd/*")) {
	unlink $file
    }
    while ($file = glob("${General::swroot}/ovpn/ccd/*")) {
	unlink $file
    }
    if (open(FILE, ">${General::swroot}/ovpn/ovpn-leases.db")) {
	print FILE "";
	close FILE;
    }
    if (open(FILE, ">${General::swroot}/ovpn/ovpnconfig")) {
	print FILE "";
	close FILE;
    }
    while ($file = glob("${General::swroot}/ovpn/n2nconf/*")) {
	unlink($file);
    }

    # Remove everything from the collectd configuration
    &writecollectdconf();

    #&writeserverconf();
###
### Reset all step 1
###
}elsif ($cgiparams{'ACTION'} eq $Lang::tr{'remove x509'}) {
    &Header::showhttpheaders();
    &Header::openpage($Lang::tr{'ovpn'}, 1, '');
    &Header::openbigbox('100%', 'left', '', '');
    &Header::openbox('100%', 'left', $Lang::tr{'are you sure'});
    print <<END;
	<form method='post'>
		<table width='100%'>
			<tr>
				<td align='center'>
				<input type='hidden' name='AREUSURE' value='yes' />
				<b><font color='${Header::colourred}'>$Lang::tr{'capswarning'}</font></b>:
				$Lang::tr{'resetting the vpn configuration will remove the root ca, the host certificate and all certificate based connections'}</td>
			</tr>
			<tr>
				<td align='center'><input type='submit' name='ACTION' value='$Lang::tr{'remove x509'}' />
				<input type='submit' name='ACTION' value='$Lang::tr{'cancel'}' /></td>
			</tr>
		</table>
	</form>
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
	goto UPLOADCA_ERROR;
    }

    # Check if there is no other entry with this name
    foreach my $key (keys %cahash) {
	if ($cahash{$key}[0] eq $cgiparams{'CA_NAME'}) {
	    $errormessage = $Lang::tr{'a ca certificate with this name already exists'};
	    goto UPLOADCA_ERROR;
	}
    }

    unless (ref ($cgiparams{'FH'})) {
	$errormessage = $Lang::tr{'there was no file upload'};
	goto UPLOADCA_ERROR;
    }
    # Move uploaded ca to a temporary file
    (my $fh, my $filename) = tempfile( );
    if (copy ($cgiparams{'FH'}, $fh) != 1) {
	$errormessage = $!;
	goto UPLOADCA_ERROR;
    }
    my @temp = &General::system_output("/usr/bin/openssl", "x509", "-text", "-in", "$filename");
    if ( ! grep(/CA:TRUE/i, @temp )) {
	$errormessage = $Lang::tr{'not a valid ca certificate'};
	unlink ($filename);
	goto UPLOADCA_ERROR;
    } else {
	unless(move($filename, "${General::swroot}/ovpn/ca/$cgiparams{'CA_NAME'}cert.pem")) {
	    $errormessage = "$Lang::tr{'certificate file move failed'}: $!";
	    unlink ($filename);
	    goto UPLOADCA_ERROR;
	}
    }

    my @casubject = &General::system_output("/usr/bin/openssl", "x509", "-text", "-in", "${General::swroot}/ovpn/ca/$cgiparams{'CA_NAME'}cert.pem");
    my $casubject;

    foreach my $line (@casubject) {
	if ($line =~ /Subject: (.*)[\n]/) {
		$casubject    = $1;
		$casubject    =~ s+/Email+, E+;
		$casubject    =~ s/ ST=/ S=/;

		last;
	}
    }

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
	&Header::openpage($Lang::tr{'ovpn'}, 1, '');
	&Header::openbigbox('100%', 'LEFT', '', $errormessage);
	&Header::openbox('100%', 'LEFT', "$Lang::tr{'ca certificate'}:");
	my @output = &General::system_output("/usr/bin/openssl", "x509", "-text", "-in", "${General::swroot}/ovpn/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem");
	my $output = &Header::cleanhtml(join("", @output),"y");
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

	my @tmp =  &General::system_output("/usr/bin/openssl", "x509", "-in", "${General::swroot}/ovpn/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem");
	print @tmp;

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
	    my @test = &General::system_output("/usr/bin/openssl", "verify", "-CAfile", "${General::swroot}/ovpn/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem", "${General::swroot}/ovpn/certs/$confighash{$key}[1]cert.pem");
	    if (grep(/: OK/, @test)) {
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
	    my @test = &General::system_output("/usr/bin/openssl", "verify", "-CAfile", "${General::swroot}/ovpn/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem", "${General::swroot}/ovpn/certs/$confighash{$key}[1]cert.pem");
	    if (grep(/: OK/, @test)) {
		$assignedcerts++;
	    }
	}
	if ($assignedcerts) {
	    &Header::showhttpheaders();
	    &Header::openpage($Lang::tr{'ovpn'}, 1, '');
	    &Header::openbigbox('100%', 'LEFT', '', $errormessage);
	    &Header::openbox('100%', 'LEFT', $Lang::tr{'are you sure'});
	    print <<END;
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
    my @output;
    &Header::showhttpheaders();
    &Header::openpage($Lang::tr{'ovpn'}, 1, '');
    &Header::openbigbox('100%', 'LEFT', '', '');
    if ($cgiparams{'ACTION'} eq $Lang::tr{'show root certificate'}) {
	&Header::openbox('100%', 'LEFT', "$Lang::tr{'root certificate'}:");
	@output = &General::system_output("/usr/bin/openssl", "x509", "-text", "-in", "${General::swroot}/ovpn/ca/cacert.pem");
    } else {
	&Header::openbox('100%', 'LEFT', "$Lang::tr{'host certificate'}:");
	@output = &General::system_output("/usr/bin/openssl", "x509", "-text", "-in", "${General::swroot}/ovpn/certs/servercert.pem");
    }
    my $output = &Header::cleanhtml(join("", @output), "y");
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

	my @tmp = &General::system_output("/usr/bin/openssl", "x509", "-in", "${General::swroot}/ovpn/ca/cacert.pem");
	print @tmp;

	exit(0);
    }

###
### Download host certificate
###
}elsif ($cgiparams{'ACTION'} eq $Lang::tr{'download host certificate'}) {
    if ( -f "${General::swroot}/ovpn/certs/servercert.pem" ) {
	print "Content-Type: application/octet-stream\r\n";
	print "Content-Disposition: filename=servercert.pem\r\n\r\n";

	my @tmp = &General::system_output("/usr/bin/openssl", "x509", "-in", "${General::swroot}/ovpn/certs/servercert.pem");
	print @tmp;

	exit(0);
    }

###
### Download tls-auth key
###
}elsif ($cgiparams{'ACTION'} eq $Lang::tr{'download tls-auth key'}) {
    if ( -f "${General::swroot}/ovpn/certs/ta.key" ) {
	print "Content-Type: application/octet-stream\r\n";
	print "Content-Disposition: filename=ta.key\r\n\r\n";

	open(FILE, "${General::swroot}/ovpn/certs/ta.key");
	my @tmp = <FILE>;
	close(FILE);

	print @tmp;

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
	unless (ref ($cgiparams{'FH'})) {
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

	unless(move("$tempdir/cacert.pem", "${General::swroot}/ovpn/ca/cacert.pem")) {
	    $errormessage = "$Lang::tr{'certificate file move failed'}: $!";
	    unlink ($filename);
	    unlink ("${General::swroot}/ovpn/ca/cacert.pem");
	    unlink ("${General::swroot}/ovpn/certs/servercert.pem");
	    unlink ("${General::swroot}/ovpn/certs/serverkey.pem");
	    goto ROOTCERT_ERROR;
        }

	unless(move("$tempdir/hostcert.pem", "${General::swroot}/ovpn/certs/servercert.pem")) {
	    $errormessage = "$Lang::tr{'certificate file move failed'}: $!";
	    unlink ($filename);
	    unlink ("${General::swroot}/ovpn/ca/cacert.pem");
	    unlink ("${General::swroot}/ovpn/certs/servercert.pem");
	    unlink ("${General::swroot}/ovpn/certs/serverkey.pem");
	    goto ROOTCERT_ERROR;
        }

	unless(move("$tempdir/serverkey.pem", "${General::swroot}/ovpn/certs/serverkey.pem")) {
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
	    unless (exec ('/usr/bin/openssl', 'req', '-x509', '-nodes',
			'-days', '999999', '-newkey', 'rsa:4096', '-sha512',
			'-keyout', "${General::swroot}/ovpn/ca/cakey.pem",
			'-out', "${General::swroot}/ovpn/ca/cacert.pem",
			'-config', "/usr/share/openvpn/ovpn.cnf")) {
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
	    unless (exec ('/usr/bin/openssl', 'req', '-nodes',
			'-newkey', 'rsa:4096',
			'-keyout', "${General::swroot}/ovpn/certs/serverkey.pem",
			'-out', "${General::swroot}/ovpn/certs/serverreq.pem",
			'-extensions', 'server',
			'-config', "/usr/share/openvpn/ovpn.cnf" )) {
		$errormessage = "$Lang::tr{'cant start openssl'}: $!";
		unlink ("${General::swroot}/ovpn/certs/serverkey.pem");
		unlink ("${General::swroot}/ovpn/certs/serverreq.pem");
		unlink ("${General::swroot}/ovpn/ca/cakey.pem");
		unlink ("${General::swroot}/ovpn/ca/cacert.pem");
		goto ROOTCERT_ERROR;
	    }
	}

	# Sign the host certificate request
	# This system call is safe, because all argeuments are passed as an array.
	system('/usr/bin/openssl', 'ca', '-days', '999999',
		'-batch', '-notext',
		'-in',  "${General::swroot}/ovpn/certs/serverreq.pem",
		'-out', "${General::swroot}/ovpn/certs/servercert.pem",
		'-extensions', 'server',
		'-config', "/usr/share/openvpn/ovpn.cnf");
	if ($?) {
	    $errormessage = "$Lang::tr{'openssl produced an error'}: $?";
	    unlink ("${General::swroot}/ovpn/ca/cakey.pem");
	    unlink ("${General::swroot}/ovpn/ca/cacert.pem");
	    unlink ("${General::swroot}/ovpn/serverkey.pem");
	    unlink ("${General::swroot}/ovpn/certs/serverreq.pem");
	    unlink ("${General::swroot}/ovpn/certs/servercert.pem");
	    &cleanssldatabase();
	    goto ROOTCERT_ERROR;
	} else {
	    unlink ("${General::swroot}/ovpn/certs/serverreq.pem");
	    &deletebackupcert();
	}

	# Create an empty CRL
	# System call is safe, because all arguments are passed as array.
	system('/usr/bin/openssl', 'ca', '-gencrl',
		'-out', "${General::swroot}/ovpn/crls/cacrl.pem",
		'-config', "/usr/share/openvpn/ovpn.cnf" );
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
	# Create ta.key for tls-auth
	# This system call is safe, because all arguments are passed as an array.
	system('/usr/sbin/openvpn', '--genkey', 'secret', "${General::swroot}/ovpn/certs/ta.key");
	if ($?) {
	    $errormessage = "$Lang::tr{'openssl produced an error'}: $?";
	    &cleanssldatabase();
	    goto ROOTCERT_ERROR;
	}
	goto ROOTCERT_SUCCESS;
    }
    ROOTCERT_ERROR:
    if ($cgiparams{'ACTION'} ne '') {
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'ovpn'}, 1, '');
	&Header::openbigbox('100%', 'LEFT', '', '');

	# Show any errors
	&Header::errorbox($errormessage);

	&Header::openbox('100%', 'LEFT', "$Lang::tr{'generate root/host certificates'}:");
	print <<END;
	<form method='post' enctype='multipart/form-data'>
	<table width='100%' border='0' cellspacing='1' cellpadding='0'>
	<tr><td width='30%' class='base'>$Lang::tr{'organization name'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	    <td width='35%' class='base' nowrap='nowrap'><input type='text' name='ROOTCERT_ORGANIZATION' value='$cgiparams{'ROOTCERT_ORGANIZATION'}' size='32' /></td>
	    <td width='35%' colspan='2'>&nbsp;</td></tr>
	<tr><td class='base'>$Lang::tr{'ipfires hostname'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	    <td class='base' nowrap='nowrap'><input type='text' name='ROOTCERT_HOSTNAME' value='$cgiparams{'ROOTCERT_HOSTNAME'}' size='32' /></td>
	    <td colspan='2'>&nbsp;</td></tr>
	<tr><td class='base'>$Lang::tr{'your e-mail'}:</td>
	    <td class='base' nowrap='nowrap'><input type='text' name='ROOTCERT_EMAIL' value='$cgiparams{'ROOTCERT_EMAIL'}' size='32' /></td>
	    <td colspan='2'>&nbsp;</td></tr>
	<tr><td class='base'>$Lang::tr{'your department'}:</td>
	    <td class='base' nowrap='nowrap'><input type='text' name='ROOTCERT_OU' value='$cgiparams{'ROOTCERT_OU'}' size='32' /></td>
	    <td colspan='2'>&nbsp;</td></tr>
	<tr><td class='base'>$Lang::tr{'city'}:</td>
	    <td class='base' nowrap='nowrap'><input type='text' name='ROOTCERT_CITY' value='$cgiparams{'ROOTCERT_CITY'}' size='32' /></td>
	    <td colspan='2'>&nbsp;</td></tr>
	<tr><td class='base'>$Lang::tr{'state or province'}:</td>
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
	print <<END;
	    </select></td>

	<tr><td>&nbsp;</td>
	    <td><input type='submit' name='ACTION' value='$Lang::tr{'generate root/host certificates'}' /></td>
	    <td>&nbsp;</td><td>&nbsp;</td></tr>
	<tr><td class='base' colspan='4' align='left'>
	    <img src='/blob.gif' valign='top' alt='*' />&nbsp;$Lang::tr{'required field'}</td></tr>
	<tr><td colspan='2'><br></td></tr>
	</table>

	<table width='100%'>
	<tr><td colspan='4'><hr></td></tr>
	<tr><td class='base' nowrap='nowrap'>$Lang::tr{'upload p12 file'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	    <td nowrap='nowrap'><input type='file' name='FH' size='32'></td>
	    <td colspan='2'>&nbsp;</td></tr>
	<tr><td class='base'>$Lang::tr{'pkcs12 file password'}:</td>
	    <td class='base' nowrap='nowrap'><input type='password' name='P12_PASS' value='$cgiparams{'P12_PASS'}' size='32' /></td>
            <td colspan='2'>&nbsp;</td></tr>
	<tr><td>&nbsp;</td>
	    <td><input type='submit' name='ACTION' value='$Lang::tr{'upload p12 file'}' /></td>
            <td colspan='2'>&nbsp;</td></tr>
	<tr><td class='base' colspan='4' align='left'>
	    <img src='/blob.gif' valign='top' alt='*' >&nbsp;$Lang::tr{'required field'}</td>
	</tr>
	</form></table>
END
	;
	&Header::closebox();
	print "<div align='center'><a href='/cgi-bin/ovpnmain.cgi'>$Lang::tr{'back'}</a></div>";
	&Header::closebigbox();
	&Header::closepage();
        exit(0)
    }

    ROOTCERT_SUCCESS:
    &General::system("chmod", "600", "${General::swroot}/ovpn/certs/serverkey.pem");
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
    my $n2nactive = '';
    my @ps = &General::system_output("/bin/ps", "ax");

    if(grep(/$confighash{$cgiparams{'KEY'}}[1]/, @ps)) {
	$n2nactive = "1";
    }

    if ($confighash{$cgiparams{'KEY'}}) {
		if ($confighash{$cgiparams{'KEY'}}[0] eq 'off') {
			$confighash{$cgiparams{'KEY'}}[0] = 'on';
			&General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

			if ($confighash{$cgiparams{'KEY'}}[3] eq 'net'){
				&General::system("/usr/local/bin/openvpnctrl", "-sn2n", "$confighash{$cgiparams{'KEY'}}[1]");
				&writecollectdconf();
			}
		} else {

			$confighash{$cgiparams{'KEY'}}[0] = 'off';
			&General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

			if ($confighash{$cgiparams{'KEY'}}[3] eq 'net'){
				if ($n2nactive ne '') {
					&General::system("/usr/local/bin/openvpnctrl", "-kn2n", "$confighash{$cgiparams{'KEY'}}[1]");
					&writecollectdconf();
				}
			}
		}
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

if ($confighash{$cgiparams{'KEY'}}[3] eq 'net'){

        my $zipname = "$confighash{$cgiparams{'KEY'}}[1]-Client.zip";
        my $zippathname = "$zippath$zipname";
        $clientovpn = "$confighash{$cgiparams{'KEY'}}[1].conf";
        my @ovsubnettemp =  split(/\./,$confighash{$cgiparams{'KEY'}}[27]);
        my $ovsubnet =  "$ovsubnettemp[0].$ovsubnettemp[1].$ovsubnettemp[2]";
        my $tunmtu = '';
        my @remsubnet = split(/\//,$confighash{$cgiparams{'KEY'}}[8]);
        my $n2nfragment = '';

    open(CLIENTCONF, ">$tempdir/$clientovpn") or die "Unable to open tempfile: $!";
    flock CLIENTCONF, 2;

    my $zip = Archive::Zip->new();
   print CLIENTCONF "# IPFire n2n Open VPN Client Config by ummeegge und m.a.d\n";
   print CLIENTCONF "# \n";
   print CLIENTCONF "# User Security\n";
   print CLIENTCONF "user nobody\n";
   print CLIENTCONF "group nobody\n";
   print CLIENTCONF "persist-tun\n";
   print CLIENTCONF "persist-key\n";
   print CLIENTCONF "script-security 2\n";
   print CLIENTCONF "# IP/DNS for remote Server Gateway\n";
   print CLIENTCONF "remote $vpnsettings{'VPN_IP'}\n";
   print CLIENTCONF "float\n";
   print CLIENTCONF "# IP adresses of the VPN Subnet\n";
   print CLIENTCONF "ifconfig $ovsubnet.2 $ovsubnet.1\n";
   print CLIENTCONF "# Server Gateway Network\n";
   print CLIENTCONF "route $remsubnet[0] $remsubnet[1]\n";
   print CLIENTCONF "# tun Device\n";
   print CLIENTCONF "dev tun\n";
   print CLIENTCONF "#Logfile for statistics\n";
   print CLIENTCONF "status-version 1\n";
   print CLIENTCONF "status /var/run/openvpn/$cgiparams{'NAME'}-n2n 10\n";
   print CLIENTCONF "# Port and Protokoll\n";
   print CLIENTCONF "port $confighash{$cgiparams{'KEY'}}[29]\n";

   if ($confighash{$cgiparams{'KEY'}}[28] eq 'tcp') {
   print CLIENTCONF "proto tcp4-client\n";
   print CLIENTCONF "# Packet size\n";
   if ($confighash{$cgiparams{'KEY'}}[31] eq '') {$tunmtu = '1400'} else {$tunmtu = $confighash{$cgiparams{'KEY'}}[31]};
   print CLIENTCONF "tun-mtu $tunmtu\n";
   }

   if ($confighash{$cgiparams{'KEY'}}[28] eq 'udp') {
   print CLIENTCONF "proto udp4\n";
   print CLIENTCONF "# Paketsize\n";
   if ($confighash{$cgiparams{'KEY'}}[31] eq '') {$tunmtu = '1500'} else {$tunmtu = $confighash{$cgiparams{'KEY'}}[31]};
   print CLIENTCONF "tun-mtu $tunmtu\n";
   if ($confighash{$cgiparams{'KEY'}}[24] ne '') {print CLIENTCONF "fragment $confighash{$cgiparams{'KEY'}}[24]\n";}
   if ($confighash{$cgiparams{'KEY'}}[23] eq 'on') {print CLIENTCONF "mssfix\n";} else { print CLIENTCONF "mssfix 0\n"; }
   }
   # Check host certificate if X509 is RFC3280 compliant.
   # If not, old --ns-cert-type directive will be used.
   # If appropriate key usage extension exists, new --remote-cert-tls directive will be used.
   my @hostcert = &General::system_output("/usr/bin/openssl", "x509", "-text", "-in", "${General::swroot}/ovpn/certs/servercert.pem");
   if (! grep(/TLS Web Server Authentication/, @hostcert)) {
               print CLIENTCONF "ns-cert-type server\n";
   } else {
               print CLIENTCONF "remote-cert-tls server\n";
   }
   print CLIENTCONF "# Auth. Client\n";
   print CLIENTCONF "tls-client\n";
   print CLIENTCONF "# Cipher\n";
   print CLIENTCONF "cipher $confighash{$cgiparams{'KEY'}}[40]\n";
    if ($confighash{$cgiparams{'KEY'}}[4] eq 'cert' && -f "${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1].p12") {
	 print CLIENTCONF "pkcs12 ${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1].p12\r\n";
     $zip->addFile( "${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1].p12", "$confighash{$cgiparams{'KEY'}}[1].p12") or die "Can't add file $confighash{$cgiparams{'KEY'}}[1].p12\n";
   }

   # If GCM cipher is used, do not use --auth
   if (($confighash{$cgiparams{'KEY'}}[40] eq 'AES-256-GCM') ||
       ($confighash{$cgiparams{'KEY'}}[40] eq 'AES-192-GCM') ||
       ($confighash{$cgiparams{'KEY'}}[40] eq 'AES-128-GCM')) {
        print CLIENTCONF unless "# HMAC algorithm\n";
        print CLIENTCONF unless "auth $confighash{$cgiparams{'KEY'}}[39]\n";
   } else {
        print CLIENTCONF "# HMAC algorithm\n";
        print CLIENTCONF "auth $confighash{$cgiparams{'KEY'}}[39]\n";
   }

   if ($confighash{$cgiparams{'KEY'}}[30] eq 'on') {
   print CLIENTCONF "# Enable Compression\n";
   print CLIENTCONF "comp-lzo\n";
     }
   print CLIENTCONF "# Debug Level\n";
   print CLIENTCONF "verb 3\n";
   print CLIENTCONF "# Tunnel check\n";
   print CLIENTCONF "keepalive 10 60\n";
   print CLIENTCONF "# Start as daemon\n";
   print CLIENTCONF "daemon $confighash{$cgiparams{'KEY'}}[1]n2n\n";
   print CLIENTCONF "writepid /var/run/$confighash{$cgiparams{'KEY'}}[1]n2n.pid\n";
   print CLIENTCONF "# Activate Management Interface and Port\n";
   if ($confighash{$cgiparams{'KEY'}}[22] eq '') {print CLIENTCONF "management localhost $confighash{$cgiparams{'KEY'}}[29]\n"}
    else {print CLIENTCONF "management localhost $confighash{$cgiparams{'KEY'}}[22]\n"};
   print CLIENTCONF "# remsub $confighash{$cgiparams{'KEY'}}[11]\n";
  if (&iscertlegacy("${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1]")) {
    	print CLIENTCONF "providers legacy default\n";
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
}
else
{
        my $zipname = "$confighash{$cgiparams{'KEY'}}[1]-TO-IPFire.zip";
        my $zippathname = "$zippath$zipname";
        $clientovpn = "$confighash{$cgiparams{'KEY'}}[1]-TO-IPFire.ovpn";

    open(CLIENTCONF, ">$tempdir/$clientovpn") or die "Unable to open tempfile: $!";
    flock CLIENTCONF, 2;

    my $zip = Archive::Zip->new();

    print CLIENTCONF "#OpenVPN Client conf\r\n";
    print CLIENTCONF "tls-client\r\n";
    print CLIENTCONF "client\r\n";
    print CLIENTCONF "nobind\r\n";
    print CLIENTCONF "dev tun\r\n";
    print CLIENTCONF "proto $vpnsettings{'DPROTOCOL'}\r\n";
    print CLIENTCONF "tun-mtu $vpnsettings{'DMTU'}\r\n";

    if ( $vpnsettings{'ENABLED'} eq 'on'){
    	print CLIENTCONF "remote $vpnsettings{'VPN_IP'} $vpnsettings{'DDEST_PORT'}\r\n";
	if ( $vpnsettings{'ENABLED_BLUE'} eq 'on' && (&Header::blue_used())){
	    print CLIENTCONF "#comment the above line and uncomment the next line, if you want to connect on the Blue interface\r\n";
	    print CLIENTCONF ";remote $netsettings{'BLUE_ADDRESS'} $vpnsettings{'DDEST_PORT'}\r\n";
	}
	if ( $vpnsettings{'ENABLED_ORANGE'} eq 'on' && (&Header::orange_used())){
	    print CLIENTCONF "#comment the above line and uncomment the next line, if you want to connect on the Orange interface\r\n";
	    print CLIENTCONF ";remote $netsettings{'ORANGE_ADDRESS'} $vpnsettings{'DDEST_PORT'}\r\n";
	}
    } elsif ( $vpnsettings{'ENABLED_BLUE'} eq 'on' && (&Header::blue_used())){
	print CLIENTCONF "remote $netsettings{'BLUE_ADDRESS'} $vpnsettings{'DDEST_PORT'}\r\n";
	if ( $vpnsettings{'ENABLED_ORANGE'} eq 'on' && (&Header::orange_used())){
	    print CLIENTCONF "#comment the above line and uncomment the next line, if you want to connect on the Orange interface\r\n";
	    print CLIENTCONF ";remote $netsettings{'ORANGE_ADDRESS'} $vpnsettings{'DDEST_PORT'}\r\n";
	}
    } elsif ( $vpnsettings{'ENABLED_ORANGE'} eq 'on' && (&Header::orange_used())){
	print CLIENTCONF "remote $netsettings{'ORANGE_ADDRESS'} $vpnsettings{'DDEST_PORT'}\r\n";
    }

    my $file_crt = new File::Temp( UNLINK => 1 );
    my $file_key = new File::Temp( UNLINK => 1 );
    my $include_certs = 0;

    if ($confighash{$cgiparams{'KEY'}}[4] eq 'cert' && -f "${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1].p12") {
	if ($cgiparams{'MODE'} eq 'insecure') {
		$include_certs = 1;

		# Add the CA
		print CLIENTCONF ";ca cacert.pem\r\n";
		$zip->addFile("${General::swroot}/ovpn/ca/cacert.pem", "cacert.pem")  or die "Can't add file cacert.pem\n";

		# Extract the certificate
		# This system call is safe, because all arguments are passed as an array.
		if (&iscertlegacy("${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1]")) {
			system('/usr/bin/openssl', 'pkcs12', '-legacy', '-in', "${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1].p12",
				'-clcerts', '-nokeys', '-nodes', '-out', "$file_crt" , '-passin', 'pass:');
			if ($?) {
				die "openssl error: $?";
			}
		} else {
			system('/usr/bin/openssl', 'pkcs12', '-in', "${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1].p12",
				'-clcerts', '-nokeys', '-nodes', '-out', "$file_crt" , '-passin', 'pass:');
			if ($?) {
				die "openssl error: $?";
			}
		}

		$zip->addFile("$file_crt", "$confighash{$cgiparams{'KEY'}}[1].pem") or die;
		print CLIENTCONF ";cert $confighash{$cgiparams{'KEY'}}[1].pem\r\n";

		# Extract the key
		# This system call is safe, because all arguments are passed as an array.
		if (&iscertlegacy("${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1]")) {
			system('/usr/bin/openssl', 'pkcs12', '-legacy', '-in', "${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1].p12",
				'-nocerts', '-nodes', '-out', "$file_key", '-passin', 'pass:');
			if ($?) {
				die "openssl error: $?";
			}
		} else {
			system('/usr/bin/openssl', 'pkcs12', '-in', "${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1].p12",
				'-nocerts', '-nodes', '-out', "$file_key", '-passin', 'pass:');
			if ($?) {
				die "openssl error: $?";
			}
		}

		$zip->addFile("$file_key", "$confighash{$cgiparams{'KEY'}}[1].key") or die;
		print CLIENTCONF ";key $confighash{$cgiparams{'KEY'}}[1].key\r\n";
	} else {
		print CLIENTCONF "pkcs12 $confighash{$cgiparams{'KEY'}}[1].p12\r\n";
		$zip->addFile( "${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1].p12", "$confighash{$cgiparams{'KEY'}}[1].p12") or die "Can't add file $confighash{$cgiparams{'KEY'}}[1].p12\n";
	}
    } else {
	print CLIENTCONF "ca cacert.pem\r\n";
	print CLIENTCONF "cert $confighash{$cgiparams{'KEY'}}[1]cert.pem\r\n";
	print CLIENTCONF "key $confighash{$cgiparams{'KEY'}}[1].key\r\n";
	$zip->addFile( "${General::swroot}/ovpn/ca/cacert.pem", "cacert.pem")  or die "Can't add file cacert.pem\n";
	$zip->addFile( "${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem", "$confighash{$cgiparams{'KEY'}}[1]cert.pem") or die "Can't add file $confighash{$cgiparams{'KEY'}}[1]cert.pem\n";
    }

	# We no longer send any cryptographic configuration since 2.6.
	# That way, we will be able to push this from the server.
	# Therefore we always mandate NCP for new clients.

	print CLIENTCONF "auth $vpnsettings{'DAUTH'}\r\n";

    if ($vpnsettings{'TLSAUTH'} eq 'on') {
	if ($cgiparams{'MODE'} eq 'insecure') {
		print CLIENTCONF ";";
	}
	print CLIENTCONF "tls-auth ta.key\r\n";
	$zip->addFile( "${General::swroot}/ovpn/certs/ta.key", "ta.key")  or die "Can't add file ta.key\n";
    }
    print CLIENTCONF "verb 3\r\n";
	# Check host certificate if X509 is RFC3280 compliant.
	# If not, old --ns-cert-type directive will be used.
	# If appropriate key usage extension exists, new --remote-cert-tls directive will be used.
	my @hostcert = &General::system_output("/usr/bin/openssl", "x509", "-text", "-in", "${General::swroot}/ovpn/certs/servercert.pem");
	if (! grep(/TLS Web Server Authentication/, @hostcert)) {
		print CLIENTCONF "ns-cert-type server\r\n";
	} else {
		print CLIENTCONF "remote-cert-tls server\r\n";
	}
    print CLIENTCONF "verify-x509-name $vpnsettings{ROOTCERT_HOSTNAME} name\r\n";
    if ($vpnsettings{MSSFIX} eq 'on') {
	print CLIENTCONF "mssfix\r\n";
    } else {
	print CLIENTCONF "mssfix 0\r\n";
    }
    if ($vpnsettings{FRAGMENT} ne '' && $vpnsettings{DPROTOCOL} ne 'tcp' ) {
	print CLIENTCONF "fragment $vpnsettings{'FRAGMENT'}\r\n";
    }

    # Disable storing any credentials in memory
    print CLIENTCONF "auth-nocache\r\n";

    # Set a fake user name for authentication
    print CLIENTCONF "auth-user-pass\r\n";
    print CLIENTCONF "auth-token-user USER\r\n";
    print CLIENTCONF "auth-token TOTP\r\n";

    # If the server is asking for TOTP this needs to happen interactively
    print CLIENTCONF "auth-retry interact\r\n";

    # Add provider line if certificate is legacy type
    if (&iscertlegacy("${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1]")) {
	print CLIENTCONF "providers legacy default\r\n";
    }

    if ($include_certs) {
	print CLIENTCONF "\r\n";

	# CA
	open(FILE, "<${General::swroot}/ovpn/ca/cacert.pem");
	print CLIENTCONF "<ca>\r\n";
	while (<FILE>) {
		chomp($_);
		print CLIENTCONF "$_\r\n";
	}
	print CLIENTCONF "</ca>\r\n\r\n";
	close(FILE);

	# Cert
	open(FILE, "<$file_crt");
	print CLIENTCONF "<cert>\r\n";
	while (<FILE>) {
		chomp($_);
		print CLIENTCONF "$_\r\n";
	}
	print CLIENTCONF "</cert>\r\n\r\n";
	close(FILE);

	# Key
	open(FILE, "<$file_key");
	print CLIENTCONF "<key>\r\n";
	while (<FILE>) {
		chomp($_);
		print CLIENTCONF "$_\r\n";
	}
	print CLIENTCONF "</key>\r\n\r\n";
	close(FILE);

	# TLS auth
	if ($vpnsettings{'TLSAUTH'} eq 'on') {
		open(FILE, "<${General::swroot}/ovpn/certs/ta.key");
		print CLIENTCONF "<tls-auth>\r\n";
		while (<FILE>) {
			chomp($_);
			print CLIENTCONF "$_\r\n";
		}
		print CLIENTCONF "</tls-auth>\r\n\r\n";
		close(FILE);
	}
    }

    # Print client.conf.local if entries exist to client.ovpn
    if (!-z $local_clientconf && $vpnsettings{'ADDITIONAL_CONFIGS'} eq 'on') {
       open (LCC, "$local_clientconf");
               print CLIENTCONF "\n#---------------------------\n";
               print CLIENTCONF "# Start of custom directives\n";
               print CLIENTCONF "# from client.conf.local\n";
               print CLIENTCONF "#---------------------------\n\n";
       while (<LCC>) {
               print CLIENTCONF $_;
       }
               print CLIENTCONF "\n#---------------------------\n";
               print CLIENTCONF "# End of custom directives\n";
               print CLIENTCONF "#---------------------------\n\n";
       close (LCC);
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
   }



###
### Remove connection
###


} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'remove'}) {
	&General::readhash("${General::swroot}/ovpn/settings", \%vpnsettings);
	&General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

	if ($confighash{$cgiparams{'KEY'}}) {
		# Revoke certificate if certificate was deleted and rewrite the CRL
		&General::system("/usr/bin/openssl", "ca", "-revoke", "${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem", "-config", "/usr/share/openvpn/ovpn.cnf");
		&General::system("/usr/bin/openssl", "ca", "-gencrl", "-out", "${General::swroot}/ovpn/crls/cacrl.pem", "-config", "/usr/share/openvpn/ovpn.cnf");

		if ($confighash{$cgiparams{'KEY'}}[3] eq 'net') {
			# Stop the N2N connection before it is removed
			&General::system("/usr/local/bin/openvpnctrl", "-kn2n", "$confighash{$cgiparams{'KEY'}}[1]");

			my $conffile = glob("${General::swroot}/ovpn/n2nconf/$confighash{$cgiparams{'KEY'}}[1]/$confighash{$cgiparams{'KEY'}}[1].conf");
			my $certfile = glob("${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1].p12");
			unlink ($certfile);
			unlink ($conffile);

			if (-e "${General::swroot}/ovpn/n2nconf/$confighash{$cgiparams{'KEY'}}[1]") {
				rmdir ("${General::swroot}/ovpn/n2nconf/$confighash{$cgiparams{'KEY'}}[1]") || die "Kann Verzeichnis nicht loeschen: $!";
			}
		}

		unlink ("${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem");
		unlink ("${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1].p12");

		# Delete CCD files and routes

		if (-f "${General::swroot}/ovpn/ccd/$confighash{$cgiparams{'KEY'}}[2]")
		{
			unlink "${General::swroot}/ovpn/ccd/$confighash{$cgiparams{'KEY'}}[2]";
		}

		&General::readhasharray("${General::swroot}/ovpn/ccdroute", \%ccdroutehash);
		foreach my $key (keys %ccdroutehash) {
			if ($ccdroutehash{$key}[0] eq $confighash{$cgiparams{'KEY'}}[1]){
				delete $ccdroutehash{$key};
			}
		}
		&General::writehasharray("${General::swroot}/ovpn/ccdroute", \%ccdroutehash);

		&General::readhasharray("${General::swroot}/ovpn/ccdroute2", \%ccdroute2hash);
		foreach my $key (keys %ccdroute2hash) {
			if ($ccdroute2hash{$key}[0] eq $confighash{$cgiparams{'KEY'}}[1]){
				delete $ccdroute2hash{$key};
			}
		}
		&General::writehasharray("${General::swroot}/ovpn/ccdroute2", \%ccdroute2hash);
		&writeserverconf;

		# Update collectd configuration and delete all RRD files of the removed connection
		&writecollectdconf();
		&General::system("/usr/local/bin/openvpnctrl", "-drrd", "$confighash{$cgiparams{'KEY'}}[1]");

		delete $confighash{$cgiparams{'KEY'}};
		&General::system("/usr/bin/openssl", "ca", "-gencrl", "-out", "${General::swroot}/ovpn/crls/cacrl.pem", "-config", "/usr/share/openvpn/ovpn.cnf");
		&General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

	} else {
		$errormessage = $Lang::tr{'invalid key'};
	}
	&General::firewall_reload();

###
### Download PKCS12 file
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'download pkcs12 file'}) {
    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

    print "Content-Disposition: filename=" . $confighash{$cgiparams{'KEY'}}[1] . ".p12\r\n";
    print "Content-Type: application/octet-stream\r\n\r\n";

    open(FILE, "${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1].p12");
    my @tmp = <FILE>;
    close(FILE);

    print @tmp;
    exit (0);

###
### Display certificate
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'show certificate'}) {
    &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

    if ( -f "${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem") {
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'ovpn'}, 1, '');
	&Header::openbigbox('100%', 'LEFT', '', '');
	&Header::openbox('100%', 'LEFT', "$Lang::tr{'certificate'}:");
	my @output = &General::system_output("/usr/bin/openssl", "x509", "-text", "-in", "${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem");
	my $output = &Header::cleanhtml(join("", @output), "y");
	print "<pre>$output</pre>\n";
	&Header::closebox();
	print "<div align='center'><a href='/cgi-bin/ovpnmain.cgi'>$Lang::tr{'back'}</a></div>";
	&Header::closebigbox();
	&Header::closepage();
	exit(0);
    }

###
### Display OTP QRCode
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'show otp qrcode'}) {
   &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

   my $qrcode = Imager::QRCode->new(
      size          => 6,
      margin        => 0,
      version       => 0,
      level         => 'M',
      mode          => '8-bit',
      casesensitive => 1,
      lightcolor    => Imager::Color->new(255, 255, 255),
      darkcolor     => Imager::Color->new(0, 0, 0),
   );
   my $cn = uri_encode($confighash{$cgiparams{'KEY'}}[2]);
   my $secret = encode_base32(pack('H*', $confighash{$cgiparams{'KEY'}}[44]));
   my $issuer = uri_encode("$mainsettings{'HOSTNAME'}.$mainsettings{'DOMAINNAME'}");
   my $qrcodeimg = $qrcode->plot("otpauth://totp/$cn?secret=$secret&issuer=$issuer");
   my $qrcodeimgdata;
   $qrcodeimg->write(data => \$qrcodeimgdata, type=> 'png')
      or die $qrcodeimg->errstr;
   $qrcodeimgdata = encode_base64($qrcodeimgdata, '');

   &Header::showhttpheaders();
   &Header::openpage($Lang::tr{'ovpn'}, 1, '');
   &Header::openbigbox('100%', 'LEFT', '', '');
   &Header::openbox('100%', 'LEFT', "$Lang::tr{'otp qrcode'}:");
   print <<END;
$Lang::tr{'secret'}:&nbsp;$secret</br></br>
<img alt="$Lang::tr{'otp qrcode'}" src="data:image/png;base64,$qrcodeimgdata">
END
   &Header::closebox();
   print "<div align='center'><a href='/cgi-bin/ovpnmain.cgi'>$Lang::tr{'back'}</a></div>";
   &Header::closebigbox();
   &Header::closepage();
   exit(0);

###
### Display tls-auth key
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'show tls-auth key'}) {

    if (! -e "${General::swroot}/ovpn/certs/ta.key") {
	$errormessage = $Lang::tr{'not present'};
	} else {
		&Header::showhttpheaders();
		&Header::openpage($Lang::tr{'ovpn'}, 1, '');
		&Header::openbigbox('100%', 'LEFT', '', '');
		&Header::openbox('100%', 'LEFT', "$Lang::tr{'ta key'}:");

		open(FILE, "${General::swroot}/ovpn/certs/ta.key");
		my @output = <FILE>;
		close(FILE);

		my $output = &Header::cleanhtml(join("", @output),"y");
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

    if (! -e "${General::swroot}/ovpn/crls/cacrl.pem") {
	$errormessage = $Lang::tr{'not present'};
	} else {
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'ovpn'}, 1, '');
	&Header::openbigbox('100%', 'LEFT', '', '');
	&Header::openbox('100%', 'LEFT', "$Lang::tr{'crl'}:");
	my @output = &General::system_output("/usr/bin/openssl", "crl", "-text", "-noout", "-in", "${General::swroot}/ovpn/crls/cacrl.pem");
	my $output = &Header::cleanhtml(join("", @output), "y");
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
    my $disabled;
    &General::readhash("${General::swroot}/ovpn/settings", \%cgiparams);
    read_routepushfile;

ADV_ERROR:
	if ($cgiparams{'DATACIPHERS'} eq '') {
		$cgiparams{'DATACIPHERS'} = $DEFAULT_CIPHERS;
	}
	if ($cgiparams{'DAUTH'} eq '') {
		$cgiparams{'DAUTH'} = 'SHA512';
	}
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
    if ($cgiparams{'TLSAUTH'} eq '') {
		$cgiparams{'TLSAUTH'} = 'off';
    }
    $checked{'CLIENT2CLIENT'}{'off'} = '';
    $checked{'CLIENT2CLIENT'}{'on'} = '';
    $checked{'CLIENT2CLIENT'}{$cgiparams{'CLIENT2CLIENT'}} = 'CHECKED';
    $checked{'REDIRECT_GW_DEF1'}{'off'} = '';
    $checked{'REDIRECT_GW_DEF1'}{'on'} = '';
    $checked{'REDIRECT_GW_DEF1'}{$cgiparams{'REDIRECT_GW_DEF1'}} = 'CHECKED';
    $checked{'ADDITIONAL_CONFIGS'}{'off'} = '';
    $checked{'ADDITIONAL_CONFIGS'}{'on'} = '';
    $checked{'ADDITIONAL_CONFIGS'}{$cgiparams{'ADDITIONAL_CONFIGS'}} = 'CHECKED';
    $checked{'MSSFIX'}{'off'} = '';
    $checked{'MSSFIX'}{'on'} = '';
    $checked{'MSSFIX'}{$cgiparams{'MSSFIX'}} = 'CHECKED';
    $selected{'LOG_VERB'}{'0'} = '';
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
    $selected{'LOG_VERB'}{$cgiparams{'LOG_VERB'}} = 'SELECTED';

	# Split data ciphers
	my @data_ciphers = split(/\|/, $cgiparams{'DATACIPHERS'});

	# Select the correct ones
	$selected{'DATACIPHERS'} = ();
	foreach my $cipher (@SUPPORTED_CIPHERS) {
		$selected{'DATACIPHERS'}{$cipher} = grep(/^$cipher$/, @data_ciphers) ? "selected" : "";
	}

    $selected{'DCIPHER'}{'AES-256-GCM'} = '';
    $selected{'DCIPHER'}{'AES-192-GCM'} = '';
    $selected{'DCIPHER'}{'AES-128-GCM'} = '';
    $selected{'DCIPHER'}{'CAMELLIA-256-CBC'} = '';
    $selected{'DCIPHER'}{'CAMELLIA-192-CBC'} = '';
    $selected{'DCIPHER'}{'CAMELLIA-128-CBC'} = '';
    $selected{'DCIPHER'}{'AES-256-CBC'} = '';
    $selected{'DCIPHER'}{'AES-192-CBC'} = '';
    $selected{'DCIPHER'}{'AES-128-CBC'} = '';
    $selected{'DCIPHER'}{'DES-EDE3-CBC'} = '';
    $selected{'DCIPHER'}{'DESX-CBC'} = '';
    $selected{'DCIPHER'}{'SEED-CBC'} = '';
    $selected{'DCIPHER'}{'DES-EDE-CBC'} = '';
    $selected{'DCIPHER'}{'CAST5-CBC'} = '';
    $selected{'DCIPHER'}{'BF-CBC'} = '';
    $selected{'DCIPHER'}{'DES-CBC'} = '';
    $selected{'DCIPHER'}{$cgiparams{'DCIPHER'}} = 'SELECTED';

    $selected{'DAUTH'}{'whirlpool'} = '';
    $selected{'DAUTH'}{'SHA512'} = '';
    $selected{'DAUTH'}{'SHA384'} = '';
    $selected{'DAUTH'}{'SHA256'} = '';
    $selected{'DAUTH'}{'SHA1'} = '';
    $selected{'DAUTH'}{$cgiparams{'DAUTH'}} = 'SELECTED';

    $checked{'TLSAUTH'}{'off'} = '';
    $checked{'TLSAUTH'}{'on'} = '';
    $checked{'TLSAUTH'}{$cgiparams{'TLSAUTH'}} = 'CHECKED';

    &Header::showhttpheaders();
    &Header::openpage($Lang::tr{'status ovpn'}, 1, '');
    &Header::openbigbox('100%', 'LEFT', '', $errormessage);

	# Show any errors
	&Header::errorbox($errormessage);

    &Header::opensection();

    print <<END;
	    <form method='post' enctype='multipart/form-data'>
			<table width='100%' border=0>
				<tr>
					<td colspan='2'>
						<b>$Lang::tr{'ovpn crypt options'}</b>
					</td>
				</tr>

				<tr>
					<td width="25%">
						$Lang::tr{'ovpn ciphers'}
					</td>

					<td>
						<select name='DATACIPHERS' multiple required>
END

	foreach my $cipher (@SUPPORTED_CIPHERS) {
		my $name = $CIPHERS{$cipher} // $cipher;

		print <<END;
							<option value='$cipher' $selected{'DATACIPHERS'}{$cipher}>
								$name
							</option>
END
	}

	print <<END;
						</select>
					</td>
				</tr>

				<tr>
					<td>
						$Lang::tr{'ovpn ha'}
					</td>

					<td>
						<select name='DAUTH'>
							<option value='whirlpool'		$selected{'DAUTH'}{'whirlpool'}>Whirlpool (512 $Lang::tr{'bit'})</option>
							<option value='SHA512'			$selected{'DAUTH'}{'SHA512'}>SHA2 (512 $Lang::tr{'bit'})</option>
							<option value='SHA384'			$selected{'DAUTH'}{'SHA384'}>SHA2 (384 $Lang::tr{'bit'})</option>
							<option value='SHA256'			$selected{'DAUTH'}{'SHA256'}>SHA2 (256 $Lang::tr{'bit'})</option>
							<option value='SHA1'			$selected{'DAUTH'}{'SHA1'}>SHA1 (160 $Lang::tr{'bit'}, $Lang::tr{'vpn weak'})</option>
						</select>
					</td>
				</tr>

				<tr>
					<td>
						$Lang::tr{'ovpn tls auth'}
					</td>

					<td>
						<input type='checkbox' name='TLSAUTH' $checked{'TLSAUTH'}{'on'} />
					</td>
				</tr>

				<tr>
					<td>
						$Lang::tr{'ovpn fallback cipher'}
					</td>

					<td>
						<select name='DCIPHER'>
							<option value='' $selected{'DCIPHER'}{''}>- $Lang::tr{'Disabled'} -</option>
							<option value='AES-256-GCM' $selected{'DCIPHER'}{'AES-256-GCM'}>AES-GCM (256 $Lang::tr{'bit'})</option>
							<option value='AES-192-GCM' $selected{'DCIPHER'}{'AES-192-GCM'}>AES-GCM (192 $Lang::tr{'bit'})</option>
							<option value='AES-128-GCM' $selected{'DCIPHER'}{'AES-128-GCM'}>AES-GCM (128 $Lang::tr{'bit'})</option>
							<option value='CAMELLIA-256-CBC' $selected{'DCIPHER'}{'CAMELLIA-256-CBC'}>CAMELLIA-CBC (256 $Lang::tr{'bit'})</option>
							<option value='CAMELLIA-192-CBC' $selected{'DCIPHER'}{'CAMELLIA-192-CBC'}>CAMELLIA-CBC (192 $Lang::tr{'bit'})</option>
							<option value='CAMELLIA-128-CBC' $selected{'DCIPHER'}{'CAMELLIA-128-CBC'}>CAMELLIA-CBC (128 $Lang::tr{'bit'})</option>
							<option value='AES-256-CBC' $selected{'DCIPHER'}{'AES-256-CBC'}>AES-CBC (256 $Lang::tr{'bit'})</option>
							<option value='AES-192-CBC' $selected{'DCIPHER'}{'AES-192-CBC'}>AES-CBC (192 $Lang::tr{'bit'})</option>
							<option value='AES-128-CBC' $selected{'DCIPHER'}{'AES-128-CBC'}>AES-CBC (128 $Lang::tr{'bit'})</option>
							<option value='SEED-CBC' $selected{'DCIPHER'}{'SEED-CBC'}>SEED-CBC (128 $Lang::tr{'bit'})</option>
							<option value='DES-EDE3-CBC' $selected{'DCIPHER'}{'DES-EDE3-CBC'}>DES-EDE3-CBC (192 $Lang::tr{'bit'}, $Lang::tr{'vpn weak'})</option>
							<option value='DESX-CBC' $selected{'DCIPHER'}{'DESX-CBC'}>DESX-CBC (192 $Lang::tr{'bit'}, $Lang::tr{'vpn weak'})</option>
							<option value='DES-EDE-CBC' $selected{'DCIPHER'}{'DES-EDE-CBC'}>DES-EDE-CBC (128 $Lang::tr{'bit'}, $Lang::tr{'vpn weak'})</option>
							<option value='BF-CBC' $selected{'DCIPHER'}{'BF-CBC'}>BF-CBC (128 $Lang::tr{'bit'}, $Lang::tr{'vpn weak'})</option>
							<option value='CAST5-CBC' $selected{'DCIPHER'}{'CAST5-CBC'}>CAST5-CBC (128 $Lang::tr{'bit'}, $Lang::tr{'vpn weak'})</option>
						</select>
					</td>
				</tr>
				<tr>
					<td></td>
					<td>
						$Lang::tr{'ovpn fallback cipher help'}
					</td>
				</tr>

				<tr>
					<td colspan='2'><b>$Lang::tr{'dhcp-options'}</b></td>
				</tr>
				<tr>
					<td>Domain</td>
					<td>
						<input type='TEXT' name='DHCP_DOMAIN' value='$cgiparams{'DHCP_DOMAIN'}' size='30' />
					</td>
				</tr>
				<tr>
					<td>DNS</td>
					<td>
						<input type='TEXT' name='DHCP_DNS' value='$cgiparams{'DHCP_DNS'}' size='30' />
					</td>
				</tr>
				<tr>
					<td>WINS</td>
					<td>
						<input type='TEXT' name='DHCP_WINS' value='$cgiparams{'DHCP_WINS'}' size='30' />
					</td>
				</tr>
				<tr>
					<td colspan='2'><b>$Lang::tr{'ovpn routes push options'}</b></td>
				</tr>
				<tr>
					<td>$Lang::tr{'ovpn routes push'}</td>
					<td>
						<textarea name='ROUTES_PUSH' cols='26' rows='6' wrap='off'>$cgiparams{'ROUTES_PUSH'}</textarea>
					</td>
				</tr>
			</table>

<hr size='1'>

<table width='100%'>
	<tr>
		<td class='base'><b>$Lang::tr{'misc-options'}</b></td>
	</tr>

	<tr>
		<td width='20%'></td> <td width='15%'> </td><td width='35%'> </td><td width='20%'></td><td width='35%'></td>
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
		<td class='base'>$Lang::tr{'ovpn add conf'}</td>
		<td><input type='checkbox' name='ADDITIONAL_CONFIGS' $checked{'ADDITIONAL_CONFIGS'}{'on'} /></td>
		<td>$Lang::tr{'openvpn default'}: off</td>
	</tr>

	<tr>
		<td class='base'>mssfix</td>
		<td><input type='checkbox' name='MSSFIX' $checked{'MSSFIX'}{'on'} /></td>
		<td>$Lang::tr{'openvpn default'}: off</td>
	</tr>

	<tr>
		<td class='base'>fragment <br></td>
		<td><input type='TEXT' name='FRAGMENT' value='$cgiparams{'FRAGMENT'}' size='10' /></td>
	</tr>


	<tr>
		<td class='base'>Max-Clients</td>
		<td><input type='text' name='MAX_CLIENTS' value='$cgiparams{'MAX_CLIENTS'}' size='10' /></td>
	</tr>
	<tr>
		<td class='base'>Keepalive <br />
		(ping/ping-restart)</td>
		<td><input type='TEXT' name='KEEPALIVE_1' value='$cgiparams{'KEEPALIVE_1'}' size='10' /></td>
		<td><input type='TEXT' name='KEEPALIVE_2' value='$cgiparams{'KEEPALIVE_2'}' size='10' /></td>
	</tr>
</table>

<hr size='1'>
<table width='100%'>
    <tr>
	<td class='base'><b>$Lang::tr{'log-options'}</b></td>
    </tr>
    <tr>
	<td width='20%'></td> <td width='30%'> </td><td width='25%'> </td><td width='25%'></td>
    </tr>

    <tr><td class='base'>VERB</td>
        <td><select name='LOG_VERB'>
			<option value='0'  $selected{'LOG_VERB'}{'0'}>0</option>
			<option value='1'  $selected{'LOG_VERB'}{'1'}>1</option>
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
	</td></select>
    </table>

<hr size='1'>
END

if ( -e "/var/run/openvpn.pid"){
print"	<br><b><font color='#990000'>$Lang::tr{'attention'}:</b></font><br>
		$Lang::tr{'server restart'}<br><br>
		<hr>";
	print<<END;
<table width='100%'>
<tr>
    <td>&nbsp;</td>
    <td allign='center'><input type='submit' name='ACTION' value='$Lang::tr{'save-adv-options'}' disabled='disabled' /></td>
    <td allign='center'><input type='submit' name='ACTION' value='$Lang::tr{'cancel-adv-options'}' /></td>
    <td>&nbsp;</td>
</tr>
</table>
</form>
END
;


}else{

	print<<END;
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
}
    &Header::closebox();
#    print "<div align='center'><a href='/cgi-bin/ovpnmain.cgi'>$Lang::tr{'back'}</a></div>";
    &Header::closebigbox();
    &Header::closepage();
    exit(0);


# Add, delete or edit CCD net

} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'ccd net'} ||
		$cgiparams{'ACTION'} eq $Lang::tr{'ccd add'} ||
		$cgiparams{'ACTION'} eq "kill" ||
		$cgiparams{'ACTION'} eq "edit" ||
		$cgiparams{'ACTION'} eq 'editsave'){
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'ccd net'}, 1, '');
	&Header::openbigbox('100%', 'LEFT', '', '');

	if ($cgiparams{'ACTION'} eq "kill"){
		&delccdnet($cgiparams{'net'});
	}

	if ($cgiparams{'ACTION'} eq 'editsave'){
		my ($a,$b) =split (/\|/,$cgiparams{'ccdname'});
		if ( $a ne $b){ &modccdnet($a,$b);}
		$cgiparams{'ccdname'}='';
		$cgiparams{'ccdsubnet'}='';
	}

	if ($cgiparams{'ACTION'} eq $Lang::tr{'ccd add'}) {
		&addccdnet($cgiparams{'ccdname'},$cgiparams{'ccdsubnet'});
	}
	if ($errormessage) {
	    &Header::openbox('100%', 'LEFT', $Lang::tr{'error messages'});
	    print "<class name='base'>$errormessage";
	    print "&nbsp;</class>";
	    &Header::closebox();
	}
if ($cgiparams{'ACTION'} eq "edit"){

	&Header::openbox('100%', 'LEFT', $Lang::tr{'ccd modify'});

	print <<END;
    <table width='100%' border='0'>
    <tr><form method='post'>
	<td width='10%' nowrap='nowrap'>$Lang::tr{'ccd name'}:</td><td><input type='TEXT' name='ccdname' value='$cgiparams{'ccdname'}' /></td>
	<td width='8%'>$Lang::tr{'ccd subnet'}:</td><td><input type='TEXT' name='ccdsubnet' value='$cgiparams{'ccdsubnet'}' readonly='readonly' /></td></tr>
	<tr><td colspan='4' align='right'><hr><input type='submit' value='$Lang::tr{'save'}' /><input type='hidden' name='ACTION' value='editsave'/>
	<input type='hidden' name='ccdname' value='$cgiparams{'ccdname'}'/><input type='submit' value='$Lang::tr{'cancel'}' />
	</td></tr>
	</table></form>
END
;
	&Header::closebox();

	&Header::openbox('100%', 'LEFT',$Lang::tr{'ccd net'} );
	print <<END;
    <table width='100%' border='0'  cellpadding='0' cellspacing='1'>
    <tr>
	<td class='boldbase' align='center'><b>$Lang::tr{'ccd name'}</td><td class='boldbase' align='center'><b>$Lang::tr{'network'}</td><td class='boldbase' width='15%' align='center'><b>$Lang::tr{'ccd used'}</td><td width='3%'></td><td width='3%'></td></tr>
END
;
}
else{
	if (! -e "/var/run/openvpn.pid"){
	&Header::openbox('100%', 'LEFT', $Lang::tr{'ccd add'});
	print <<END;
	    <table width='100%' border='0'>
	    <tr><form method='post'>
		<td colspan='4'>$Lang::tr{'ccd hint'}<br><br></td></tr>
		<tr>
		<td width='10%' nowrap='nwrap'>$Lang::tr{'ccd name'}:</td><td><input type='TEXT' name='ccdname' value='$cgiparams{'ccdname'}' /></td>
		<td width='8%'>$Lang::tr{'ccd subnet'}:</td><td><input type='TEXT' name='ccdsubnet' value='$cgiparams{'ccdsubnet'}' /></td></tr>
		<tr><td colspan=4><hr /></td></tr><tr>
		<td colspan='4' align='right'><input type='hidden' name='ACTION' value='$Lang::tr{'ccd add'}' /><input type='submit' value='$Lang::tr{'add'}' /><input type='hidden' name='DOVPN_SUBNET' value='$cgiparams{'DOVPN_SUBNET'}'/></td></tr>
		</table></form>
END

	&Header::closebox();
}
	&Header::openbox('100%', 'LEFT',$Lang::tr{'ccd net'} );
	if ( -e "/var/run/openvpn.pid"){
		print "<b>$Lang::tr{'attention'}:</b><br>";
		print "$Lang::tr{'ccd noaddnet'}<br><hr>";
	}

    print <<END;
    <table width='100%' cellpadding='0' cellspacing='1'>
    <tr>
	<td class='boldbase' align='center' nowrap='nowrap' width='20%'><b>$Lang::tr{'ccd name'}</td><td class='boldbase' align='center' width='8%'><b>$Lang::tr{'network'}</td><td class='boldbase' width='8%' align='center' nowrap='nowrap'><b>$Lang::tr{'ccd used'}</td><td width='1%' align='center'></td><td width='1%' align='center'></td></tr>
END
;
}
	my %ccdconfhash=();
	&General::readhasharray("${General::swroot}/ovpn/ccd.conf", \%ccdconfhash);
	my @ccdconf=();
	my $count=0;
	foreach my $key (sort { uc($ccdconfhash{$a}[0]) cmp uc($ccdconfhash{$b}[0]) } keys %ccdconfhash) {
		@ccdconf=($ccdconfhash{$key}[0],$ccdconfhash{$key}[1]);
		$count++;
		my $ccdhosts = &hostsinnet($ccdconf[0]);
		if ($count % 2){ print" <tr bgcolor='$Header::color{'color22'}'>";}
		else{            print" <tr bgcolor='$Header::color{'color20'}'>";}
		print"<td>$ccdconf[0]</td><td align='center'>$ccdconf[1]</td><td align='center'>$ccdhosts/".(&ccdmaxclients($ccdconf[1])+1)."</td><td>";
        print <<END;
		<form method='post' />
		<input type='image' src='/images/edit.gif' align='middle' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' />
		<input type='hidden' name='ACTION' value='edit'/>
		<input type='hidden' name='ccdname' value='$ccdconf[0]' />
		<input type='hidden' name='ccdsubnet' value='$ccdconf[1]' />
		</form></td>
		<form method='post' />
		<td><input type='hidden' name='ACTION' value='kill'/>
		<input type='hidden' name='number' value='$count' />
		<input type='hidden' name='net' value='$ccdconf[0]' />
		<input type='image' src='/images/delete.gif' align='middle' alt='$Lang::tr{'remove'}' title='$Lang::tr{'remove'}' /></form></td></tr>
END
;
	}
	print "</table></form>";
	&Header::closebox();
	print "<div align='center'><a href='/cgi-bin/ovpnmain.cgi'>$Lang::tr{'back'}</a></div>";
	&Header::closebigbox();
	&Header::closepage();
	exit(0);

#END CCD

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
    print <<END;
    <table width='100%' cellpadding='2' cellspacing='0' class='tbl'>
    <tr>
	<th><b>$Lang::tr{'common name'}</b></th>
	<th><b>$Lang::tr{'real address'}</b></th>
	<th><b>$Lang::tr{'country'}</b></th>
	<th><b>$Lang::tr{'virtual address'}</b></th>
	<th><b>$Lang::tr{'loged in at'}</b></th>
	<th><b>$Lang::tr{'bytes sent'}</b></th>
	<th><b>$Lang::tr{'bytes received'}</b></th>
	<th><b>$Lang::tr{'last activity'}</b></th>
    </tr>
END
;
	my $filename = "/var/run/ovpnserver.log";
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
		    $users[$uid]{'BytesReceived'} = &General::formatBytes($match[3]);
		    $users[$uid]{'BytesSent'} = &General::formatBytes($match[4]);
		    $users[$uid]{'Since'} = $match[5];
		    $users[$uid]{'Proto'} = $proto;

		    # get country code for "RealAddress"...
		    my $ccode = &Location::Functions::lookup_country_code((split ':', $users[$uid]{'RealAddress'})[0]);
		    my $flag_icon = &Location::Functions::get_flag_icon($ccode);
		    $users[$uid]{'Country'} = "<a href='country.cgi#$ccode'><img src='$flag_icon' border='0' align='absmiddle' alt='$ccode' title='$ccode' /></a>";
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
							print "<tr>";
							$col="bgcolor='$Header::color{'color22'}'";
						} else {
							print "<tr>";
							$col="bgcolor='$Header::color{'color20'}'";
						}
						print "<td align='left' $col>$users[$idx-1]{'CommonName'}</td>";
						print "<td align='left' $col>$users[$idx-1]{'RealAddress'}</td>";
						print "<td align='center' $col>$users[$idx-1]{'Country'}</td>";
						print "<td align='center' $col>$users[$idx-1]{'VirtualAddress'}</td>";
						print "<td align='left' $col>$users[$idx-1]{'Since'}</td>";
						print "<td align='left' $col>$users[$idx-1]{'BytesSent'}</td>";
						print "<td align='left' $col>$users[$idx-1]{'BytesReceived'}</td>";
						print "<td align='left' $col>$users[$idx-1]{'LastRef'}</td>";
			}
	}

	print "</table>";
	print <<END;
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

	open(FILE, "${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem");
	my @tmp = <FILE>;
	close(FILE);

	print @tmp;
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

} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'add'} && $cgiparams{'TYPE'} eq '') {
	&General::readhash("${General::swroot}/ovpn/settings", \%vpnsettings);
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'ovpn'}, 1, '');
	&Header::openbigbox('100%', 'LEFT', '', '');
	&Header::openbox('100%', 'LEFT', $Lang::tr{'connection type'});

if ( -s "${General::swroot}/ovpn/settings") {

	print <<END;
	    <b>$Lang::tr{'connection type'}:</b><br />
	    <table border='0' width='100%'><form method='post' ENCTYPE="multipart/form-data">
	    <tr><td><input type='radio' name='TYPE' value='host' checked /></td>
		<td class='base'>$Lang::tr{'host to net vpn'}</td></tr>
	    <tr><td><input type='radio' name='TYPE' value='net' /></td>
		<td class='base'>$Lang::tr{'net to net vpn'}</td></tr>
  		<tr><td><input type='radio' name='TYPE' value='net2net' /></td>
		<td class='base'>$Lang::tr{'net to net vpn'} (Upload Client Package)</td></tr>
	  <tr><td>&nbsp;</td><td class='base'><input type='file' name='FH' size='30'></td></tr>
	  <tr><td>&nbsp;</td><td>Import Connection Name</td></tr>
    <tr><td>&nbsp;</td><td class='base'><input type='text' name='n2nname' size='30'>$Lang::tr{'openvpn default'}: Client Packagename</td></tr>
	  <tr><td colspan='3'><hr /></td></tr>
    <tr><td align='right' colspan='3'><input type='submit' name='ACTION' value='$Lang::tr{'add'}' /></td></tr>
	    </form></table>
END
	;


} else {
	print <<END;
		    <b>$Lang::tr{'connection type'}:</b><br />
	    <table border='0' width='100%'><form method='post' ENCTYPE="multipart/form-data">
	    <tr><td><input type='radio' name='TYPE' value='host' checked /></td> <td class='base'>$Lang::tr{'host to net vpn'}</td></tr>
	    <tr><td align='right' colspan'3'><input type='submit' name='ACTION' value='$Lang::tr{'add'}' /></td></tr>
	    </form></table>
END
	;

}

	&Header::closebox();
	print "<div align='center'><a href='/cgi-bin/ovpnmain.cgi'>$Lang::tr{'back'}</a></div>";
	&Header::closebigbox();
	&Header::closepage();
	exit (0);

}  elsif (($cgiparams{'ACTION'} eq $Lang::tr{'add'}) && ($cgiparams{'TYPE'} eq 'net2net')){

	my @firen2nconf;
	my @confdetails;
	my $uplconffilename ='';
	my $uplconffilename2 ='';
	my $uplp12name = '';
	my $uplp12name2 = '';
	my @rem_subnet;
	my @rem_subnet2;
	my @tmposupnet3;
	my $key;
	my @n2nname;

	&General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

	# Check if a file is uploaded
	unless (ref ($cgiparams{'FH'})) {
		$errormessage = $Lang::tr{'there was no file upload'};
		goto N2N_ERROR;
    }

# Move uploaded IPfire n2n package to temporary file

    (my $fh, my $filename) = tempfile( );
    if (copy ($cgiparams{'FH'}, $fh) != 1) {
		$errormessage = $!;
		goto N2N_ERROR;
    }

	my $zip = Archive::Zip->new();
	my $zipName = $filename;
	my $status = $zip->read( $zipName );
	if ($status != AZ_OK) {
		$errormessage = "Read of $zipName failed\n";
		goto N2N_ERROR;
	}

	my $tempdir = tempdir( CLEANUP => 1 );
	my @files = $zip->memberNames();
	for(@files) {
	$zip->extractMemberWithoutPaths($_,"$tempdir/$_");
	}
	my $countfiles = @files;

# Check if we have not more then 2 files

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
			goto N2N_ERROR;
		}

		open(FILE, "$tempdir/$uplconffilename") or die 'Unable to open*.conf file';
		@firen2nconf = <FILE>;
		close (FILE);
		chomp(@firen2nconf);
	} else {

		$errormessage = "Filecount does not match only 2 files are allowed\n";
		goto N2N_ERROR;
	}

 if ($cgiparams{'n2nname'} ne ''){

  $uplconffilename2 = "$cgiparams{'n2nname'}.conf";
  $uplp12name2 = "$cgiparams{'n2nname'}.p12";
  $n2nname[0] = $cgiparams{'n2nname'};
  my @n2nname2 = split(/\./,$uplconffilename);
  $n2nname2[0] =~ s/\n|\r//g;
  my $input1 = "${General::swroot}/ovpn/certs/$uplp12name";
	my $output1 = "${General::swroot}/ovpn/certs/$uplp12name2";
	my $input2 = "$n2nname2[0]n2n";
  my $output2 = "$n2nname[0]n2n";
  my $filename = "$tempdir/$uplconffilename";
  open(FILE, "< $filename") or die 'Unable to open config file.';
	my @current = <FILE>;
	close(FILE);
	foreach (@current) {s/$input1/$output1/g;}
	foreach (@current) {s/$input2/$output2/g;}
  open (OUT, "> $filename") || die 'Unable to open config file.';
  print OUT @current;
  close OUT;

    }else{
    $uplconffilename2 =  $uplconffilename;
    $uplp12name2 = $uplp12name;
    @n2nname = split(/\./,$uplconffilename);
    $n2nname[0] =~ s/\n|\r//g;
   }
    unless(-d "${General::swroot}/ovpn/n2nconf/"){mkdir "${General::swroot}/ovpn/n2nconf", 0755 or die "Unable to create dir $!";}
    unless(-d "${General::swroot}/ovpn/n2nconf/$n2nname[0]"){mkdir "${General::swroot}/ovpn/n2nconf/$n2nname[0]", 0770 or die "Unable to create dir $!";}

	#Add collectd settings to configfile
	open(FILE, ">> $tempdir/$uplconffilename") or die 'Unable to open config file.';
	print FILE "# Logfile\n";
	print FILE "status-version 1\n";
	print FILE "status /var/run/openvpn/$n2nname[0]-n2n 10\n";
	if (&iscertlegacy("${General::swroot}/ovpn/certs/$cgiparams{'n2nname'}")) {
	    	print CLIENTCONF "providers legacy default\n";
	}

	close FILE;

	unless(move("$tempdir/$uplconffilename", "${General::swroot}/ovpn/n2nconf/$n2nname[0]/$uplconffilename2")) {
	    $errormessage = "*.conf move failed: $!";
	    unlink ($filename);
	    goto N2N_ERROR;
	}

	unless(move("$tempdir/$uplp12name", "${General::swroot}/ovpn/certs/$uplp12name2")) {
	    $errormessage = "$Lang::tr{'certificate file move failed'}: $!";
	    unlink ($filename);
	    goto N2N_ERROR;
	}

	chmod 0600, "${General::swroot}/ovpn/certs/$uplp12name";

my $complzoactive;
my $mssfixactive;
my $authactive;
my $n2nfragment;
my @n2nproto2 = split(/ /, (grep { /^proto/ } @firen2nconf)[0]);
my @n2nproto = split(/-/, $n2nproto2[1]);
my @n2nport = split(/ /, (grep { /^port/ } @firen2nconf)[0]);
my @n2ntunmtu = split(/ /, (grep { /^tun-mtu/ } @firen2nconf)[0]);
my @n2ncomplzo = grep { /^comp-lzo/ } @firen2nconf;
if ($n2ncomplzo[0] =~ /comp-lzo/){$complzoactive = "on";} else {$complzoactive = "off";}
my @n2nmssfix  = grep { /^mssfix/ } @firen2nconf;
if ($n2nmssfix[0] =~ /mssfix/){$mssfixactive = "on";} else {$mssfixactive = "off";}
#my @n2nmssfix = split(/ /, (grep { /^mssfix/ } @firen2nconf)[0]);
my @n2nfragment = split(/ /, (grep { /^fragment/ } @firen2nconf)[0]);
my @n2nremote = split(/ /, (grep { /^remote/ } @firen2nconf)[0]);
my @n2novpnsuball = split(/ /, (grep { /^ifconfig/ } @firen2nconf)[0]);
my @n2novpnsub =  split(/\./,$n2novpnsuball[1]);
my @n2nremsub = split(/ /, (grep { /^route/ } @firen2nconf)[0]);
my @n2nmgmt =  split(/ /, (grep { /^management/ } @firen2nconf)[0]);
my @n2nlocalsub  = split(/ /, (grep { /^# remsub/ } @firen2nconf)[0]);
my @n2ncipher = split(/ /, (grep { /^cipher/ } @firen2nconf)[0]);
my @n2nauth = split(/ /, (grep { /^auth/ } @firen2nconf)[0]);;

###
# m.a.d delete CR and LF from arrays for this chomp doesnt work
###

$n2nremote[1] =~ s/\n|\r//g;
$n2novpnsub[0] =~ s/\n|\r//g;
$n2novpnsub[1] =~ s/\n|\r//g;
$n2novpnsub[2] =~ s/\n|\r//g;
$n2nproto[0] =~ s/\n|\r//g;
$n2nport[1] =~ s/\n|\r//g;
$n2ntunmtu[1] =~ s/\n|\r//g;
$n2nremsub[1] =~ s/\n|\r//g;
$n2nremsub[2] =~ s/\n|\r//g;
$n2nlocalsub[2] =~ s/\n|\r//g;
$n2nfragment[1] =~ s/\n|\r//g;
$n2nmgmt[2] =~ s/\n|\r//g;
$n2ncipher[1] =~ s/\n|\r//g;
$n2nauth[1] =~ s/\n|\r//g;
chomp ($complzoactive);
chomp ($mssfixactive);

###
# Check if there is no other entry with this name
###

	foreach my $dkey (keys %confighash) {
		if ($confighash{$dkey}[1] eq $n2nname[0]) {
			$errormessage = $Lang::tr{'a connection with this name already exists'};
			unlink ("${General::swroot}/ovpn/n2nconf/$n2nname[0]/$n2nname[0].conf") or die "Removing Configfile fail: $!";
	    unlink ("${General::swroot}/ovpn/certs/$n2nname[0].p12") or die "Removing Certfile fail: $!";
      rmdir ("${General::swroot}/ovpn/n2nconf/$n2nname[0]") || die "Removing Directory fail: $!";
			goto N2N_ERROR;
		}
	}

###
# Check if OpenVPN Subnet is valid
###

foreach my $dkey (keys %confighash) {
		if ($confighash{$dkey}[27] eq "$n2novpnsub[0].$n2novpnsub[1].$n2novpnsub[2].0/255.255.255.0") {
			$errormessage = 'The OpenVPN Subnet is already in use';
			unlink ("${General::swroot}/ovpn/n2nconf/$n2nname[0]/$n2nname[0].conf") or die "Removing Configfile fail: $!";
	    unlink ("${General::swroot}/ovpn/certs/$n2nname[0].p12") or die "Removing Certfile fail: $!";
      rmdir ("${General::swroot}/ovpn/n2nconf/$n2nname[0]") || die "Removing Directory fail: $!";
			goto N2N_ERROR;
		}
	}

###
# Check if Dest Port is vaild
###

foreach my $dkey (keys %confighash) {
		if ($confighash{$dkey}[29] eq $n2nport[1] ) {
			$errormessage = 'The OpenVPN Port is already in use';
			unlink ("${General::swroot}/ovpn/n2nconf/$n2nname[0]/$n2nname[0].conf") or die "Removing Configfile fail: $!";
	    unlink ("${General::swroot}/ovpn/certs/$n2nname[0].p12") or die "Removing Certfile fail: $!";
      rmdir ("${General::swroot}/ovpn/n2nconf/$n2nname[0]") || die "Removing Directory fail: $!";
			goto N2N_ERROR;
		}
	}



  $key = &General::findhasharraykey (\%confighash);

	foreach my $i (0 .. 42) { $confighash{$key}[$i] = "";}

	$confighash{$key}[0] = 'off';
	$confighash{$key}[1] = $n2nname[0];
	$confighash{$key}[2] = $n2nname[0];
	$confighash{$key}[3] = 'net';
	$confighash{$key}[4] = 'cert';
	$confighash{$key}[6] = 'client';
	$confighash{$key}[8] =  $n2nlocalsub[2];
	$confighash{$key}[10] = $n2nremote[1];
	$confighash{$key}[11] = "$n2nremsub[1]/$n2nremsub[2]";
	$confighash{$key}[22] = $n2nmgmt[2];
	$confighash{$key}[23] = $mssfixactive;
	$confighash{$key}[24] = $n2nfragment[1];
	$confighash{$key}[25] = 'IPFire n2n Client';
	$confighash{$key}[26] = 'red';
	$confighash{$key}[27] = "$n2novpnsub[0].$n2novpnsub[1].$n2novpnsub[2].0/255.255.255.0";
	$confighash{$key}[28] = $n2nproto[0];
	$confighash{$key}[29] = $n2nport[1];
	$confighash{$key}[30] = $complzoactive;
	$confighash{$key}[31] = $n2ntunmtu[1];
	$confighash{$key}[39] = $n2nauth[1];
	$confighash{$key}[40] = $n2ncipher[1];
	$confighash{$key}[41] = 'no-pass';

  &General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

  N2N_ERROR:

	&Header::showhttpheaders();
	&Header::openpage('Validate imported configuration', 1, '');
	&Header::openbigbox('100%', 'LEFT', '', $errormessage);
	if ($errormessage) {
	    &Header::openbox('100%', 'LEFT', $Lang::tr{'error messages'});
	    print "<class name='base'>$errormessage";
	    print "&nbsp;</class>";
	    &Header::closebox();

	} else
  {
		&Header::openbox('100%', 'LEFT', 'import ipfire net2net config');
	}
	if ($errormessage eq ''){
	print <<END;
		<!-- ipfire net2net config gui -->
		<table width='100%'>
		<tr><td width='25%'>&nbsp;</td><td width='25%'>&nbsp;</td></tr>
    <tr><td class='boldbase'>$Lang::tr{'name'}:</td><td><b>$n2nname[0]</b></td></tr>
    <tr><td>&nbsp;</td><td>&nbsp;</td></tr>
		<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'Act as'}</td><td><b>$confighash{$key}[6]</b></td></tr>
		<tr><td class='boldbase' nowrap='nowrap'>Remote Host </td><td><b>$confighash{$key}[10]</b></td></tr>
		<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'local subnet'}</td><td><b>$confighash{$key}[8]</b></td></tr>
		<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'remote subnet'}:</td><td><b>$confighash{$key}[11]</b></td></tr>
		<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'ovpn subnet'}</td><td><b>$confighash{$key}[27]</b></td></tr>
		<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'protocol'}</td><td><b>$confighash{$key}[28]</b></td></tr>
		<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'destination port'}:</td><td><b>$confighash{$key}[29]</b></td></tr>
		<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'comp-lzo'}</td><td><b>$confighash{$key}[30]</b></td></tr>
		<tr><td class='boldbase' nowrap='nowrap'>MSSFIX:</td><td><b>$confighash{$key}[23]</b></td></tr>
		<tr><td class='boldbase' nowrap='nowrap'>Fragment:</td><td><b>$confighash{$key}[24]</b></td></tr>
		<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'MTU'}</td><td><b>$confighash{$key}[31]</b></td></tr>
		<tr><td class='boldbase' nowrap='nowrap'>Management Port </td><td><b>$confighash{$key}[22]</b></td></tr>
		<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'ovpn tls auth'}:</td><td><b>$confighash{$key}[39]</b></td></tr>
		<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'cipher'}</td><td><b>$confighash{$key}[40]</b></td></tr>
		<tr><td>&nbsp;</td><td>&nbsp;</td></tr>
    </table>
END
;
		&Header::closebox();
	}

	if ($errormessage) {
		print "<div align='center'><a href='/cgi-bin/ovpnmain.cgi'>$Lang::tr{'back'}</a></div>";
	} else {
		print "<div align='center'><form method='post' ENCTYPE='multipart/form-data'><input type='submit' name='ACTION' value='$Lang::tr{'add'}' />";
		print "<input type='hidden' name='TYPE' value='net2netakn' />";
		print "<input type='hidden' name='KEY' value='$key' />";
		print "<input type='submit' name='ACTION' value='$Lang::tr{'cancel'}' /></div></form>";
	}
	&Header::closebigbox();
	&Header::closepage();
	exit(0);


##
### Accept IPFire n2n Package Settings
###

  }  elsif (($cgiparams{'ACTION'} eq $Lang::tr{'add'}) && ($cgiparams{'TYPE'} eq 'net2netakn')){

###
### Discard and Rollback IPFire n2n Package Settings
###

  }  elsif (($cgiparams{'ACTION'} eq $Lang::tr{'cancel'}) && ($cgiparams{'TYPE'} eq 'net2netakn')){

     &General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

if ($confighash{$cgiparams{'KEY'}}) {

     my $conffile = glob("${General::swroot}/ovpn/n2nconf/$confighash{$cgiparams{'KEY'}}[1]/$confighash{$cgiparams{'KEY'}}[1].conf");
     my $certfile = glob("${General::swroot}/ovpn/certs/$confighash{$cgiparams{'KEY'}}[1].p12");
     unlink ($certfile) or die "Removing $certfile fail: $!";
     unlink ($conffile) or die "Removing $conffile fail: $!";
     rmdir ("${General::swroot}/ovpn/n2nconf/$confighash{$cgiparams{'KEY'}}[1]") || die "Kann Verzeichnis nicht loeschen: $!";
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
		$cgiparams{'ENABLED'}		= $confighash{$cgiparams{'KEY'}}[0];
		$cgiparams{'NAME'}		= $confighash{$cgiparams{'KEY'}}[1];
		$cgiparams{'TYPE'}		= $confighash{$cgiparams{'KEY'}}[3];
		$cgiparams{'AUTH'} 		= $confighash{$cgiparams{'KEY'}}[4];
		$cgiparams{'PSK'}		= $confighash{$cgiparams{'KEY'}}[5];
		$cgiparams{'SIDE'}		= $confighash{$cgiparams{'KEY'}}[6];
		$cgiparams{'LOCAL_SUBNET'}	= $confighash{$cgiparams{'KEY'}}[8];
		$cgiparams{'REMOTE'}		= $confighash{$cgiparams{'KEY'}}[10];
		$cgiparams{'REMOTE_SUBNET'} 	= $confighash{$cgiparams{'KEY'}}[11];
		$cgiparams{'OVPN_MGMT'} 	= $confighash{$cgiparams{'KEY'}}[22];
		$cgiparams{'MSSFIX'} 		= $confighash{$cgiparams{'KEY'}}[23];
		$cgiparams{'FRAGMENT'} 		= $confighash{$cgiparams{'KEY'}}[24];
		$cgiparams{'REMARK'}		= $confighash{$cgiparams{'KEY'}}[25];
		$cgiparams{'INTERFACE'}		= $confighash{$cgiparams{'KEY'}}[26];
		$cgiparams{'OVPN_SUBNET'} 	= $confighash{$cgiparams{'KEY'}}[27];
		$cgiparams{'PROTOCOL'}	  	= $confighash{$cgiparams{'KEY'}}[28];
		$cgiparams{'DEST_PORT'}	  	= $confighash{$cgiparams{'KEY'}}[29];
		$cgiparams{'COMPLZO'}	  	= $confighash{$cgiparams{'KEY'}}[30];
		$cgiparams{'MTU'}	  	= $confighash{$cgiparams{'KEY'}}[31];
		$cgiparams{'CHECK1'}   		= $confighash{$cgiparams{'KEY'}}[32];
		$name=$cgiparams{'CHECK1'}	;
		$cgiparams{$name}		= $confighash{$cgiparams{'KEY'}}[33];
		$cgiparams{'RG'}		= $confighash{$cgiparams{'KEY'}}[34];
		$cgiparams{'CCD_DNS1'}		= $confighash{$cgiparams{'KEY'}}[35];
		$cgiparams{'CCD_DNS2'}		= $confighash{$cgiparams{'KEY'}}[36];
		$cgiparams{'CCD_WINS'}		= $confighash{$cgiparams{'KEY'}}[37];
		$cgiparams{'DAUTH'}		= $confighash{$cgiparams{'KEY'}}[39];
		$cgiparams{'DCIPHER'}		= $confighash{$cgiparams{'KEY'}}[40];
		$cgiparams{'TLSAUTH'}		= $confighash{$cgiparams{'KEY'}}[41];
		$cgiparams{'OTP_STATE'}		= $confighash{$cgiparams{'KEY'}}[43];
	} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'save'}) {
	$cgiparams{'REMARK'} = &Header::cleanhtml($cgiparams{'REMARK'});

# CCD check iroute field and convert it to decimal
if ($cgiparams{'TYPE'} eq 'host') {
	my @temp=();
	my %ccdroutehash=();
	my $keypoint=0;
	my $ip;
	my $cidr;
	if ($cgiparams{'IR'} ne ''){
		@temp = split("\n",$cgiparams{'IR'});
		&General::readhasharray("${General::swroot}/ovpn/ccdroute", \%ccdroutehash);
		#find key to use
		foreach my $key (keys %ccdroutehash) {
			if ($ccdroutehash{$key}[0] eq $cgiparams{'NAME'}) {
				$keypoint=$key;
				delete $ccdroutehash{$key};
			}else{
				$keypoint = &General::findhasharraykey (\%ccdroutehash);
			}
		}
		$ccdroutehash{$keypoint}[0]=$cgiparams{'NAME'};
		my $i=1;
		my $val=0;
		foreach $val (@temp){
			chomp($val);
			$val=~s/\s*$//g;
			#check if iroute exists in ccdroute or if new iroute is part of an existing one
			foreach my $key (keys %ccdroutehash) {
				foreach my $oldiroute ( 1 .. $#{$ccdroutehash{$key}}){
						if ($ccdroutehash{$key}[$oldiroute] eq "$val") {
							$errormessage=$errormessage.$Lang::tr{'ccd err irouteexist'};
							goto VPNCONF_ERROR;
						}
						my ($ip1,$cidr1) = split (/\//, $val);
						$ip1 = &General::getnetworkip($ip1,&General::iporsubtocidr($cidr1));
						my ($ip2,$cidr2) = split (/\//, $ccdroutehash{$key}[$oldiroute]);
						if (&General::IpInSubnet ($ip1,$ip2,$cidr2)){
							$errormessage=$errormessage.$Lang::tr{'ccd err irouteexist'};
							goto VPNCONF_ERROR;
						}

				}
			}
			if (!&General::validipandmask($val)){
				$errormessage=$errormessage."Route ".$Lang::tr{'ccd invalid'}." ($val)";
				goto VPNCONF_ERROR;
			}else{
				($ip,$cidr) = split(/\//,$val);
				$ip=&General::getnetworkip($ip,&General::iporsubtocidr($cidr));
				$cidr=&General::iporsubtodec($cidr);
				$ccdroutehash{$keypoint}[$i] = $ip."/".$cidr;

			}

			#check for existing network IP's
			if (&General::IpInSubnet ($ip,$netsettings{GREEN_NETADDRESS},$netsettings{GREEN_NETMASK}) && $netsettings{GREEN_NETADDRESS} ne '0.0.0.0')
			{
				$errormessage=$Lang::tr{'ccd err green'};
				goto VPNCONF_ERROR;
			}elsif(&General::IpInSubnet ($ip,$netsettings{RED_NETADDRESS},$netsettings{RED_NETMASK}) && $netsettings{RED_NETADDRESS} ne '0.0.0.0')
			{
				$errormessage=$Lang::tr{'ccd err red'};
				goto VPNCONF_ERROR;
			}elsif(&General::IpInSubnet ($ip,$netsettings{BLUE_NETADDRESS},$netsettings{BLUE_NETMASK}) && $netsettings{BLUE_NETADDRESS} ne '0.0.0.0' && $netsettings{BLUE_NETADDRESS} gt '')
			{
				$errormessage=$Lang::tr{'ccd err blue'};
				goto VPNCONF_ERROR;
			}elsif(&General::IpInSubnet ($ip,$netsettings{ORANGE_NETADDRESS},$netsettings{ORANGE_NETMASK}) && $netsettings{ORANGE_NETADDRESS} ne '0.0.0.0' && $netsettings{ORANGE_NETADDRESS} gt '' )
			{
				$errormessage=$Lang::tr{'ccd err orange'};
				goto VPNCONF_ERROR;
			}

			if (&General::validipandmask($val)){
				$ccdroutehash{$keypoint}[$i] = $ip."/".$cidr;
			}else{
				$errormessage=$errormessage."Route ".$Lang::tr{'ccd invalid'}." ($ip/$cidr)";
				goto VPNCONF_ERROR;
			}
			$i++;
		}
		&General::writehasharray("${General::swroot}/ovpn/ccdroute", \%ccdroutehash);
		&writeserverconf;
	}else{
		&General::readhasharray("${General::swroot}/ovpn/ccdroute", \%ccdroutehash);
		foreach my $key (keys %ccdroutehash) {
			if ($ccdroutehash{$key}[0] eq $cgiparams{'NAME'}) {
				delete $ccdroutehash{$key};
				&General::writehasharray("${General::swroot}/ovpn/ccdroute", \%ccdroutehash);
				&writeserverconf;
			}
		}
	}
	undef @temp;
	#check route field and convert it to decimal
	my $val=0;
	my $i=1;
	&General::readhasharray("${General::swroot}/ovpn/ccdroute2", \%ccdroute2hash);
	#find key to use
	foreach my $key (keys %ccdroute2hash) {
		if ($ccdroute2hash{$key}[0] eq $cgiparams{'NAME'}) {
			$keypoint=$key;
			delete $ccdroute2hash{$key};
		}else{
			$keypoint = &General::findhasharraykey (\%ccdroute2hash);
			&General::writehasharray("${General::swroot}/ovpn/ccdroute", \%ccdroutehash);
			&writeserverconf;
		}
	}
	$ccdroute2hash{$keypoint}[0]=$cgiparams{'NAME'};
	if ($cgiparams{'IFROUTE'} eq ''){$cgiparams{'IFROUTE'} = $Lang::tr{'ccd none'};}
	@temp = split(/\|/,$cgiparams{'IFROUTE'});
	my %ownnet=();
	&General::readhash("${General::swroot}/ethernet/settings", \%ownnet);
	foreach $val (@temp){
		chomp($val);
		$val=~s/\s*$//g;
		if ($val eq $Lang::tr{'green'})
		{
			$val=$ownnet{GREEN_NETADDRESS}."/".$ownnet{GREEN_NETMASK};
		}
		if ($val eq $Lang::tr{'blue'})
		{
			$val=$ownnet{BLUE_NETADDRESS}."/".$ownnet{BLUE_NETMASK};
		}
		if ($val eq $Lang::tr{'orange'})
		{
			$val=$ownnet{ORANGE_NETADDRESS}."/".$ownnet{ORANGE_NETMASK};
		}
		my ($ip,$cidr) = split (/\//, $val);

		if ($val ne $Lang::tr{'ccd none'})
		{
			if (! &check_routes_push($val)){$errormessage=$errormessage."Route $val ".$Lang::tr{'ccd err routeovpn2'}." ($val)";goto VPNCONF_ERROR;}
			if (! &check_ccdroute($val)){$errormessage=$errormessage."<br>Route $val ".$Lang::tr{'ccd err inuse'}." ($val)" ;goto VPNCONF_ERROR;}
			if (! &check_ccdconf($val)){$errormessage=$errormessage."<br>Route $val ".$Lang::tr{'ccd err routeovpn'}." ($val)";goto VPNCONF_ERROR;}
			if (&General::validipandmask($val)){
				$val=$ip."/".&General::iporsubtodec($cidr);
				$ccdroute2hash{$keypoint}[$i] = $val;
			}else{
				$errormessage=$errormessage."Route ".$Lang::tr{'ccd invalid'}." ($val)";
				goto VPNCONF_ERROR;
			}
		}else{
			$ccdroute2hash{$keypoint}[$i]='';
		}
		$i++;
	}
	&General::writehasharray("${General::swroot}/ovpn/ccdroute2", \%ccdroute2hash);

	#check dns1 ip
	if ($cgiparams{'CCD_DNS1'} ne '' &&  ! &General::validip($cgiparams{'CCD_DNS1'})) {
			$errormessage=$errormessage."<br>".$Lang::tr{'invalid input for dhcp dns'}." 1";
			goto VPNCONF_ERROR;
	}
	#check dns2 ip
	if ($cgiparams{'CCD_DNS2'} ne '' &&  ! &General::validip($cgiparams{'CCD_DNS2'})) {
			$errormessage=$errormessage."<br>".$Lang::tr{'invalid input for dhcp dns'}." 2";
			goto VPNCONF_ERROR;
	}
	#check wins ip
	if ($cgiparams{'CCD_WINS'} ne '' &&  ! &General::validip($cgiparams{'CCD_WINS'})) {
			$errormessage=$errormessage."<br>".$Lang::tr{'invalid input for dhcp wins'};
			goto VPNCONF_ERROR;
	}
}

	if ($cgiparams{'TYPE'} !~ /^(host|net)$/) {
		$errormessage = $Lang::tr{'connection type is invalid'};
		if ($cgiparams{'TYPE'} eq 'net') {
			unlink ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf") or die "Removing Configfile fail: $!";
			rmdir ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}") || die "Removing Directory fail: $!";
			goto VPNCONF_ERROR;
		}
		goto VPNCONF_ERROR;
	}

	if ($cgiparams{'NAME'} !~ /^[a-zA-Z0-9]+$/) {
		$errormessage = $Lang::tr{'name must only contain characters'};
		if ($cgiparams{'TYPE'} eq 'net') {
			goto VPNCONF_ERROR;
		}
		goto VPNCONF_ERROR;
	}

	if ($cgiparams{'NAME'} =~ /^(host|01|block|private|clear|packetdefault)$/) {
		$errormessage = $Lang::tr{'name is invalid'};
		if ($cgiparams{'TYPE'} eq 'net') {
			unlink ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf") or die "Removing Configfile fail: $!";
			rmdir ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}") || die "Removing Directory fail: $!";
			goto VPNCONF_ERROR;
		}
		goto VPNCONF_ERROR;
	}

	if (length($cgiparams{'NAME'}) >60) {
		$errormessage = $Lang::tr{'name too long'};
		if ($cgiparams{'TYPE'} eq 'net') {
			unlink ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf") or die "Removing Configfile fail: $!";
			rmdir ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}") || die "Removing Directory fail: $!";
			goto VPNCONF_ERROR;
		}
		goto VPNCONF_ERROR;
	}

if ($cgiparams{'TYPE'} eq 'net') {
	if ($cgiparams{'DEST_PORT'} eq  $vpnsettings{'DDEST_PORT'}) {
			$errormessage = $Lang::tr{'openvpn destination port used'};
			unlink ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf") or die "Removing Configfile fail: $!";
	    rmdir ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}") || die "Removing Directory fail: $!";
      goto VPNCONF_ERROR;
		}
    #Bugfix 10357
    foreach my $key (sort keys %confighash){
		if ( ($confighash{$key}[22] eq $cgiparams{'DEST_PORT'} && $cgiparams{'NAME'} ne $confighash{$key}[1]) || ($confighash{$key}[29] eq $cgiparams{'DEST_PORT'} && $cgiparams{'NAME'} ne $confighash{$key}[1])){
			$errormessage = $Lang::tr{'openvpn destination port used'};
			unlink ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf") or die "Removing Configfile fail: $!";
	    rmdir ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}") || die "Removing Directory fail: $!";
      goto VPNCONF_ERROR;
		}
	}
    if ($cgiparams{'DEST_PORT'} eq  '') {
			$errormessage = $Lang::tr{'invalid port'};
			unlink ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf") or die "Removing Configfile fail: $!";
	    rmdir ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}") || die "Removing Directory fail: $!";
      goto VPNCONF_ERROR;
		}

    # Check if the input for the transfer net is valid.
    if (!&General::validipandmask($cgiparams{'OVPN_SUBNET'})){
			$errormessage = $Lang::tr{'ccd err invalidnet'};
			unlink ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf") or die "Removing Configfile fail: $!";
	    rmdir ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}") || die "Removing Directory fail: $!";
			goto VPNCONF_ERROR;
		}

    if ($cgiparams{'OVPN_SUBNET'} eq  $vpnsettings{'DOVPN_SUBNET'}) {
			$errormessage = $Lang::tr{'openvpn subnet is used'};
			unlink ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf") or die "Removing Configfile fail: $!";
	    rmdir ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}") || die "Removing Directory fail: $!";
			goto VPNCONF_ERROR;
		}

	  if (($cgiparams{'PROTOCOL'} eq 'tcp') && ($cgiparams{'MSSFIX'} eq 'on')) {
	    $errormessage = $Lang::tr{'openvpn mssfix allowed with udp'};
	    unlink ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf") or die "Removing Configfile fail: $!";
	    rmdir ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}") || die "Removing Directory fail: $!";
	    goto VPNCONF_ERROR;
    }

    if (($cgiparams{'PROTOCOL'} eq 'tcp') && ($cgiparams{'FRAGMENT'} ne '')) {
	    $errormessage = $Lang::tr{'openvpn fragment allowed with udp'};
	    unlink ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf") or die "Removing Configfile fail: $!";
	    rmdir ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}") || die "Removing Directory fail: $!";
	    goto VPNCONF_ERROR;
    }

    if ( &validdotmask ($cgiparams{'LOCAL_SUBNET'}))  {
		  $errormessage = $Lang::tr{'openvpn prefix local subnet'};
		  unlink ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf") or die "Removing Configfile fail: $!";
	    rmdir ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}") || die "Removing Directory fail: $!";
		  goto VPNCONF_ERROR;
		}

    if ( &validdotmask ($cgiparams{'OVPN_SUBNET'}))  {
		  $errormessage = $Lang::tr{'openvpn prefix openvpn subnet'};
		  unlink ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf") or die "Removing Configfile fail: $!";
	    rmdir ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}") || die "Removing Directory fail: $!";
		  goto VPNCONF_ERROR;
		}

    if ( &validdotmask ($cgiparams{'REMOTE_SUBNET'}))  {
		  $errormessage = $Lang::tr{'openvpn prefix remote subnet'};
		  unlink ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf") or die "Removing Configfile fail: $!";
	    rmdir ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}") || die "Removing Directory fail: $!";
		  goto VPNCONF_ERROR;
		}

	if ($cgiparams{'DEST_PORT'} <= 1023) {
		$errormessage = $Lang::tr{'ovpn port in root range'};
		  unlink ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf") or die "Removing Configfile fail: $!";
	    rmdir ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}") || die "Removing Directory fail: $!";
		  goto VPNCONF_ERROR;
		}

	if ($cgiparams{'OVPN_MGMT'} eq '') {
		$cgiparams{'OVPN_MGMT'} = $cgiparams{'DEST_PORT'};
		}

	if ($cgiparams{'OVPN_MGMT'} <= 1023) {
		$errormessage = $Lang::tr{'ovpn mgmt in root range'};
		  unlink ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf") or die "Removing Configfile fail: $!";
	    rmdir ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}") || die "Removing Directory fail: $!";
		  goto VPNCONF_ERROR;
	}
	#Check if remote subnet is used elsewhere
	my ($n2nip,$n2nsub)=split("/",$cgiparams{'REMOTE_SUBNET'});
	$warnmessage=&General::checksubnets('',$n2nip,'ovpn');
	if ($warnmessage){
		$warnmessage=$Lang::tr{'remote subnet'}." ($cgiparams{'REMOTE_SUBNET'}) <br>".$warnmessage;
	}
}

	# Check if there is no other entry with this name
	if (! $cgiparams{'KEY'}) {
	    foreach my $key (keys %confighash) {
		if ($confighash{$key}[1] eq $cgiparams{'NAME'}) {
		    $errormessage = $Lang::tr{'a connection with this name already exists'};
		    if ($cgiparams{'TYPE'} eq 'net') {
        unlink ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf") or die "Removing Configfile fail: $!";
	      rmdir ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}") || die "Removing Directory fail: $!";
        }
		    goto VPNCONF_ERROR;
		}
	    }
	}

	# Check if a remote host/IP has been set for the client.
	if ($cgiparams{'TYPE'} eq 'net') {
		if ($cgiparams{'SIDE'} ne 'server' && $cgiparams{'REMOTE'} eq '') {
			$errormessage = $Lang::tr{'invalid input for remote host/ip'};

			# Check if this is a N2N connection and drop temporary config.
			unlink ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf") or die "Removing Configfile fail: $!";
			rmdir ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}") || die "Removing Directory fail: $!";

			goto VPNCONF_ERROR;
		}

		# Check if a remote host/IP has been configured - the field can be empty on the server side.
		if ($cgiparams{'REMOTE'} ne '') {
			# Check if the given IP is valid - otherwise check if it is a valid domain.
			if (! &General::validip($cgiparams{'REMOTE'})) {
				# Check for a valid domain.
				if (! &General::validfqdn ($cgiparams{'REMOTE'}))  {
					$errormessage = $Lang::tr{'invalid input for remote host/ip'};

					# Check if this is a N2N connection and drop temporary config.
					unlink ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf") or die "Removing Configfile fail: $!";
					rmdir ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}") || die "Removing Directory fail: $!";

					goto VPNCONF_ERROR;
				}
			}
		}
	}

	if ($cgiparams{'TYPE'} ne 'host') {
            unless (&General::validipandmask($cgiparams{'LOCAL_SUBNET'})) {
	            $errormessage = $Lang::tr{'local subnet is invalid'};
	            if ($cgiparams{'TYPE'} eq 'net') {
              unlink ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf") or die "Removing Configfile fail: $!";
	            rmdir ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}") || die "Removing Directory fail: $!";
              }
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
	if (($cgiparams{'TYPE'} eq 'net') && (! &General::validipandmask($cgiparams{'REMOTE_SUBNET'}))) {
                $errormessage = $Lang::tr{'remote subnet is invalid'};
                unlink ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf") or die "Removing Configfile fail: $!";
	              rmdir ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}") || die "Removing Directory fail: $!";
      		goto VPNCONF_ERROR;
	}

	# Check for N2N that OpenSSL maximum of valid days will not be exceeded
	if ($cgiparams{'TYPE'} eq 'net') {
		if ($cgiparams{'DAYS_VALID'} >= '999999') {
			$errormessage = $Lang::tr{'invalid input for valid till days'};
			unlink ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}/$cgiparams{'NAME'}.conf") or die "Removing Configfile fail: $!";
			rmdir ("${General::swroot}/ovpn/n2nconf/$cgiparams{'NAME'}") || die "Removing Directory fail: $!";
			goto VPNCONF_ERROR;
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

	if ($cgiparams{'AUTH'} eq 'certreq') {
	    if ($cgiparams{'KEY'}) {
		$errormessage = $Lang::tr{'cant change certificates'};
		goto VPNCONF_ERROR;
	    }
	    unless (ref ($cgiparams{'FH'})) {
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
	    # The system call is safe, because all arguments are passed as an array.
	    system('/usr/bin/openssl', 'ca', '-days', "$cgiparams{'DAYS_VALID'}",
		'-batch', '-notext',
		'-in', $filename,
		'-out', "${General::swroot}/ovpn/certs/$cgiparams{'NAME'}cert.pem",
		'-config', "/usr/share/openvpn/ovpn.cnf");
	    if ($?) {
		$errormessage = "$Lang::tr{'openssl produced an error'}: $?";
		unlink ($filename);
		unlink ("${General::swroot}/ovpn/certs/$cgiparams{'NAME'}cert.pem");
		&cleanssldatabase();
		goto VPNCONF_ERROR;
	    } else {
		unlink ($filename);
		&deletebackupcert();
	    }

	    my @temp = &General::system_output("/usr/bin/openssl", "x509", "-text", "-in", "${General::swroot}/ovpn/certs/$cgiparams{'NAME'}cert.pem");
	    my $temp;

	    foreach my $line (@temp) {
		if ($line =~ /Subject:.*CN\s?=\s?(.*)[\n]/) {
			$temp = $1;
			$temp =~ s+/Email+, E+;
			$temp =~ s/ ST=/ S=/;

			last;
		}
	    }

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
	    unless (ref ($cgiparams{'FH'})) {
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
	    my @test = &General::system_output("/usr/bin/openssl", "verify", "-CAfile", "${General::swroot}/ovpn/ca/cacert.pem", "$filename");
	    if (grep(/: OK/, @test)) {
		$validca = 1;
	    } else {
		foreach my $key (keys %cahash) {
		    @test = &General::system_output("/usr/bin/openssl", "verify", "-CAfile", "${General::swroot}/ovpn/ca/$cahash{$key}[0]cert.pem", "$filename");
		    if (grep(/: OK/, @test)) {
			$validca = 1;
		    }
		}
	    }
	    if (! $validca) {
		$errormessage = $Lang::tr{'certificate does not have a valid ca associated with it'};
		unlink ($filename);
		goto VPNCONF_ERROR;
	    } else {
		unless(move($filename, "${General::swroot}/ovpn/certs/$cgiparams{'NAME'}cert.pem")) {
		    $errormessage = "$Lang::tr{'certificate file move failed'}: $!";
		    unlink ($filename);
		    goto VPNCONF_ERROR;
		}
	    }

	    my @temp = &General::system_output("/usr/bin/openssl", "x509", "-text", "-in", "${General::swroot}/ovpn/certs/$cgiparams{'NAME'}cert.pem");
	    my $temp;

	    foreach my $line (@temp) {
		if ($line =~ /Subject:.*CN\s?=\s?(.*)[\n]/) {
			$temp = $1;
			$temp =~ s+/Email+, E+;
			$temp =~ s/ ST=/ S=/;

			last;
		}
	    }

	    $cgiparams{'CERT_NAME'} = $temp;
	    $cgiparams{'CERT_NAME'} =~ s/,//g;
	    $cgiparams{'CERT_NAME'} =~ s/\'//g;
	    if ($cgiparams{'CERT_NAME'} eq '') {
		unlink ("${General::swroot}/ovpn/certs/$cgiparams{'NAME'}cert.pem");
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
	    if ($cgiparams{'CERT_NAME'} eq '' || $cgiparams{'CERT_NAME'} !~ /^[a-zA-Z0-9 ,\.\-_]+$/) {
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
	    if ($cgiparams{'DAYS_VALID'} eq '' && $cgiparams{'DAYS_VALID'} !~ /^[0-9]+$/) {
		$errormessage = $Lang::tr{'invalid input for valid till days'};
		goto VPNCONF_ERROR;
	    }

	    # Check for RW that OpenSSL maximum of valid days will not be exceeded
	    if ($cgiparams{'TYPE'} eq 'host') {
		if ($cgiparams{'DAYS_VALID'} >= '999999') {
			$errormessage = $Lang::tr{'invalid input for valid till days'};
			goto VPNCONF_ERROR;
		}
	    }

	    # Check for RW if client name is already set
	    if ($cgiparams{'TYPE'} eq 'host') {
		    foreach my $key (keys %confighash) {
			    if ($confighash{$key}[1] eq $cgiparams{'NAME'}) {
				    $errormessage = $Lang::tr{'a connection with this name already exists'};
				    goto VPNCONF_ERROR;
		    }
		    }
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
		unless (exec ('/usr/bin/openssl', 'req', '-nodes',
			'-newkey', 'rsa:4096',
			'-keyout', "${General::swroot}/ovpn/certs/$cgiparams{'NAME'}key.pem",
			'-out', "${General::swroot}/ovpn/certs/$cgiparams{'NAME'}req.pem",
			'-config', "/usr/share/openvpn/ovpn.cnf")) {
		    $errormessage = "$Lang::tr{'cant start openssl'}: $!";
		    unlink ("${General::swroot}/ovpn/certs/$cgiparams{'NAME'}key.pem");
		    unlink ("${General::swroot}/ovpn/certs/$cgiparams{'NAME'}req.pem");
		    goto VPNCONF_ERROR;
		}
	    }

	    # Sign the host certificate request
	    # The system call is safe, because all arguments are passed as an array.
	    system('/usr/bin/openssl', 'ca', '-days', "$cgiparams{'DAYS_VALID'}",
		'-batch', '-notext',
		'-in',  "${General::swroot}/ovpn/certs/$cgiparams{'NAME'}req.pem",
		'-out', "${General::swroot}/ovpn/certs/$cgiparams{'NAME'}cert.pem",
		'-config', "/usr/share/openvpn/ovpn.cnf");
	    if ($?) {
		$errormessage = "$Lang::tr{'openssl produced an error'}: $?";
		unlink ("${General::swroot}/ovpn/certs/$cgiparams{'NAME'}key.pem");
		unlink ("${General::swroot}/ovpn/certs/$cgiparams{'NAME'}req.pem");
		unlink ("${General::swroot}/ovpn/certs/$cgiparams{'NAME'}cert.pem");
		&cleanssldatabase();
		goto VPNCONF_ERROR;
	    } else {
		unlink ("${General::swroot}/ovpn/certs/$cgiparams{'NAME'}req.pem");
		&deletebackupcert();
	    }

	    # Create the pkcs12 file
	    # The system call is safe, because all arguments are passed as an array.
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

    # Save the config
	my $key = $cgiparams{'KEY'};

	if (! $key) {
	    $key = &General::findhasharraykey (\%confighash);
	    foreach my $i (0 .. 43) { $confighash{$key}[$i] = "";}
	}
	$confighash{$key}[0] 		= $cgiparams{'ENABLED'};
	$confighash{$key}[1] 		= $cgiparams{'NAME'};
	if ((! $cgiparams{'KEY'}) && $cgiparams{'AUTH'} ne 'psk') {
	    $confighash{$key}[2] 	= $cgiparams{'CERT_NAME'};
	}

	$confighash{$key}[3] 		= $cgiparams{'TYPE'};
	if ($cgiparams{'AUTH'} eq 'psk') {
	    $confighash{$key}[4] 	= 'psk';
	    $confighash{$key}[5] 	= $cgiparams{'PSK'};
	} else {
	    $confighash{$key}[4] 	= 'cert';
	}
	if ($cgiparams{'TYPE'} eq 'net') {
	    $confighash{$key}[6] 	= $cgiparams{'SIDE'};
	    $confighash{$key}[11] 	= $cgiparams{'REMOTE_SUBNET'};
	}
	$confighash{$key}[8] 		= $cgiparams{'LOCAL_SUBNET'};
	$confighash{$key}[10] 		= $cgiparams{'REMOTE'};
	if ($cgiparams{'OVPN_MGMT'} eq '') {
	$confighash{$key}[22] 		= $confighash{$key}[29];
	} else {
	$confighash{$key}[22] 		= $cgiparams{'OVPN_MGMT'};
	}
	$confighash{$key}[23] 		= $cgiparams{'MSSFIX'};
	$confighash{$key}[24] 		= $cgiparams{'FRAGMENT'};
	$confighash{$key}[25] 		= $cgiparams{'REMARK'};
	$confighash{$key}[26] 		= $cgiparams{'INTERFACE'};
# new fields
	$confighash{$key}[27] 		= $cgiparams{'OVPN_SUBNET'};
	$confighash{$key}[28] 		= $cgiparams{'PROTOCOL'};
	$confighash{$key}[29] 		= $cgiparams{'DEST_PORT'};
	$confighash{$key}[30] 		= $cgiparams{'COMPLZO'};
	$confighash{$key}[31] 		= $cgiparams{'MTU'};
	$confighash{$key}[32] 		= $cgiparams{'CHECK1'};
	$name=$cgiparams{'CHECK1'};
	$confighash{$key}[33] 		= $cgiparams{$name};
	$confighash{$key}[34] 		= $cgiparams{'RG'};
	$confighash{$key}[35] 		= $cgiparams{'CCD_DNS1'};
	$confighash{$key}[36] 		= $cgiparams{'CCD_DNS2'};
	$confighash{$key}[37] 		= $cgiparams{'CCD_WINS'};
	$confighash{$key}[39]		= $cgiparams{'DAUTH'};
	$confighash{$key}[40]		= $cgiparams{'DCIPHER'};

       if ($confighash{$key}[41] eq "") {
               if (($cgiparams{'TYPE'} eq 'host') && ($cgiparams{'CERT_PASS1'} eq "")) {
                       $confighash{$key}[41] = "no-pass";
               } elsif (($cgiparams{'TYPE'} eq 'host') && ($cgiparams{'CERT_PASS1'} ne "")) {
                       $confighash{$key}[41] = "pass";
               } elsif ($cgiparams{'TYPE'} eq 'net') {
                       $confighash{$key}[41] = "no-pass";
               }
       }

   $confighash{$key}[42] = 'HOTP/T30/6';
	$confighash{$key}[43] = $cgiparams{'OTP_STATE'};
	if (($confighash{$key}[43] eq 'on') && ($confighash{$key}[44] eq '')) {
		my @otp_secret = &General::system_output("/usr/bin/openssl", "rand", "-hex", "20");
      chomp($otp_secret[0]);
		$confighash{$key}[44] = $otp_secret[0];
	} elsif ($confighash{$key}[43] eq '') {
		$confighash{$key}[44] = '';
	}

	&General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

	if ($cgiparams{'CHECK1'} ){

		my ($ccdip,$ccdsub)=split "/",$cgiparams{$name};
		my ($a,$b,$c,$d) = split (/\./,$ccdip);
			if ( -e "${General::swroot}/ovpn/ccd/$confighash{$key}[2]"){
				unlink "${General::swroot}/ovpn/ccd/$cgiparams{'CERT_NAME'}";
			}
			open ( CCDRWCONF,'>',"${General::swroot}/ovpn/ccd/$confighash{$key}[2]") or die "Unable to create clientconfigfile $!";
			print CCDRWCONF "# OpenVPN clientconfig from ccd extension by Copymaster#\n\n";
			if($cgiparams{'CHECK1'} eq 'dynamic'){
				print CCDRWCONF "#This client uses the dynamic pool\n";
			}else{
				print CCDRWCONF "#Ip address client and server\n";
				print CCDRWCONF "ifconfig-push $ccdip ". &Network::bin2ip(&Network::ip2bin($ccdip) - 1) ."\n";
			}
			if ($confighash{$key}[34] eq 'on'){
				print CCDRWCONF "\n#Redirect Gateway: \n#All IP traffic is redirected through the vpn \n";
				print CCDRWCONF "push redirect-gateway\n";
			}
			&General::readhasharray("${General::swroot}/ovpn/ccdroute", \%ccdroutehash);
			if ($cgiparams{'IR'} ne ''){
				print CCDRWCONF "\n#Client routes these networks (behind Client)\n";
				foreach my $key (keys %ccdroutehash){
					if ($ccdroutehash{$key}[0] eq $cgiparams{'NAME'}){
						foreach my $i ( 1 .. $#{$ccdroutehash{$key}}){
							my ($a,$b)=split (/\//,$ccdroutehash{$key}[$i]);
							print CCDRWCONF "iroute $a $b\n";
						}
					}
				}
			}
			if ($cgiparams{'IFROUTE'} eq $Lang::tr{'ccd none'} ){$cgiparams{'IFROUTE'}='';}
			if ($cgiparams{'IFROUTE'} ne ''){
				print CCDRWCONF "\n#Client gets routes to these networks (behind IPFire)\n";
				foreach my $key (keys %ccdroute2hash){
					if ($ccdroute2hash{$key}[0] eq $cgiparams{'NAME'}){
						foreach my $i ( 1 .. $#{$ccdroute2hash{$key}}){
							if($ccdroute2hash{$key}[$i] eq $Lang::tr{'blue'}){
								my %blue=();
								&General::readhash("${General::swroot}/ethernet/settings", \%blue);
								print CCDRWCONF "push \"route $blue{BLUE_ADDRESS} $blue{BLUE_NETMASK}\n";
							}elsif($ccdroute2hash{$key}[$i] eq $Lang::tr{'orange'}){
								my %orange=();
								&General::readhash("${General::swroot}/ethernet/settings", \%orange);
								print CCDRWCONF "push \"route $orange{ORANGE_ADDRESS}  $orange{ORANGE_NETMASK}\n";
							}else{
								my ($a,$b)=split (/\//,$ccdroute2hash{$key}[$i]);
								print CCDRWCONF "push \"route $a $b\"\n";
							}
						}
					}
				}
			}
			if(($cgiparams{'CCD_DNS1'} eq '') && ($cgiparams{'CCD_DNS1'} ne '')){ $cgiparams{'CCD_DNS1'} = $cgiparams{'CCD_DNS2'};$cgiparams{'CCD_DNS2'}='';}
			if($cgiparams{'CCD_DNS1'} ne ''){
				print CCDRWCONF "\n#Client gets these nameservers\n";
				print CCDRWCONF "push \"dhcp-option DNS $cgiparams{'CCD_DNS1'}\" \n";
			}
			if($cgiparams{'CCD_DNS2'} ne ''){
				print CCDRWCONF "push \"dhcp-option DNS $cgiparams{'CCD_DNS2'}\" \n";
			}
			if($cgiparams{'CCD_WINS'} ne ''){
				print CCDRWCONF "\n#Client gets this WINS server\n";
				print CCDRWCONF "push \"dhcp-option WINS $cgiparams{'CCD_WINS'}\" \n";
			}
			close CCDRWCONF;
	}

	if ($cgiparams{'TYPE'} eq 'net') {

		if (-e "/var/run/$confighash{$key}[1]n2n.pid") {
			&General::system("/usr/local/bin/openvpnctrl", "-kn2n", "$confighash{$cgiparams{'KEY'}}[1]");

			&General::readhasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);
			my $key = $cgiparams{'KEY'};
			if (! $key) {
			    $key = &General::findhasharraykey (\%confighash);
			    foreach my $i (0 .. 31) {
				    $confighash{$key}[$i] = "";
			    }
			}

			$confighash{$key}[0] = 'on';
			&General::writehasharray("${General::swroot}/ovpn/ovpnconfig", \%confighash);

			&General::system("/usr/local/bin/openvpnctrl", "-sn2n", "$confighash{$cgiparams{'KEY'}}[1]");
		}
	}

	if ($cgiparams{'EDIT_ADVANCED'} eq 'on') {
	    $cgiparams{'KEY'} = $key;
	    $cgiparams{'ACTION'} = $Lang::tr{'advanced'};
	}
	goto VPNCONF_END;
    } else {
        $cgiparams{'ENABLED'} = 'on';
        $cgiparams{'MSSFIX'} = 'on';
        $cgiparams{'FRAGMENT'} = '1300';
        $cgiparams{'DAUTH'} = 'SHA512';
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
	$cgiparams{'DAYS_VALID'}     	= $vpnsettings{'DAYS_VALID'} = '730';
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

    $checked{'MSSFIX'}{'off'} = '';
    $checked{'MSSFIX'}{'on'} = '';
    $checked{'MSSFIX'}{$cgiparams{'MSSFIX'}} = 'CHECKED';

    $selected{'DCIPHER'}{'AES-256-GCM'} = '';
    $selected{'DCIPHER'}{'AES-192-GCM'} = '';
    $selected{'DCIPHER'}{'AES-128-GCM'} = '';
    $selected{'DCIPHER'}{'CAMELLIA-256-CBC'} = '';
    $selected{'DCIPHER'}{'CAMELLIA-192-CBC'} = '';
    $selected{'DCIPHER'}{'CAMELLIA-128-CBC'} = '';
    $selected{'DCIPHER'}{'AES-256-CBC'} = '';
    $selected{'DCIPHER'}{'AES-192-CBC'} = '';
    $selected{'DCIPHER'}{'AES-128-CBC'} = '';
    $selected{'DCIPHER'}{'DESX-CBC'} = '';
    $selected{'DCIPHER'}{'SEED-CBC'} = '';
    $selected{'DCIPHER'}{'DES-EDE3-CBC'} = '';
    $selected{'DCIPHER'}{'DES-EDE-CBC'} = '';
    $selected{'DCIPHER'}{'CAST5-CBC'} = '';
    $selected{'DCIPHER'}{'BF-CBC'} = '';
    $selected{'DCIPHER'}{'DES-CBC'} = '';
    # If no cipher has been chossen yet, select
    # the old default (AES-256-CBC) for compatiblity reasons.
    if ($cgiparams{'DCIPHER'} eq '') {
	$cgiparams{'DCIPHER'} = 'AES-256-CBC';
    }
    $selected{'DCIPHER'}{$cgiparams{'DCIPHER'}} = 'SELECTED';
    $selected{'DAUTH'}{'whirlpool'} = '';
    $selected{'DAUTH'}{'SHA512'} = '';
    $selected{'DAUTH'}{'SHA384'} = '';
    $selected{'DAUTH'}{'SHA256'} = '';
    $selected{'DAUTH'}{'SHA1'} = '';
    $selected{'DAUTH'}{$cgiparams{'DAUTH'}} = 'SELECTED';
    $checked{'TLSAUTH'}{'off'} = '';
    $checked{'TLSAUTH'}{'on'} = '';
    $checked{'TLSAUTH'}{$cgiparams{'TLSAUTH'}} = 'CHECKED';

    if (1) {
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'ovpn'}, 1, '');
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
	print "<table width='100%'  border='0'>\n";

	print "<tr><td width='14%' class='boldbase'>$Lang::tr{'name'}:&nbsp;<img src='/blob.gif' alt='*' /></td>";

	if ($cgiparams{'TYPE'} eq 'host') {
	    if ($cgiparams{'KEY'}) {
		print "<td width='35%' class='base'><input type='hidden' name='NAME' value='$cgiparams{'NAME'}' />$cgiparams{'NAME'}</td>";
	    } else {
		print "<td width='35%'><input type='text' name='NAME' value='$cgiparams{'NAME'}' maxlength='20' size='30' /></td>";
	    }
#	    print "<tr><td>$Lang::tr{'interface'}</td>";
#	    print "<td><select name='INTERFACE'>";
#	    print "<option value='RED' $selected{'INTERFACE'}{'RED'}>RED</option>";
#		if ($netsettings{'BLUE_DEV'} ne '') {
#			print "<option value='BLUE' $selected{'INTERFACE'}{'BLUE'}>BLUE</option>";
#		}
#		print "<option value='GREEN' $selected{'INTERFACE'}{'GREEN'}>GREEN</option>";
#		print "<option value='ORANGE' $selected{'INTERFACE'}{'ORANGE'}>ORANGE</option>";
#		print "</select></td></tr>";
#		print <<END;
	} else {
	    print "<input type='hidden' name='INTERFACE' value='red' />";
	    if ($cgiparams{'KEY'}) {
		print "<td width='25%' class='base' nowrap='nowrap'><input type='hidden' name='NAME' value='$cgiparams{'NAME'}' />$cgiparams{'NAME'}</td>";
	    } else {
		print "<td width='25%'><input type='text' name='NAME' value='$cgiparams{'NAME'}' maxlength='20' /></td>";
	    }

		# If GCM ciphers are in usage, HMAC menu is disabled
		my $hmacdisabled;
		if (($confighash{$cgiparams{'KEY'}}[40] eq 'AES-256-GCM') ||
			($confighash{$cgiparams{'KEY'}}[40] eq 'AES-192-GCM') ||
			($confighash{$cgiparams{'KEY'}}[40] eq 'AES-128-GCM')) {
				$hmacdisabled = "disabled='disabled'";
		};

	    print <<END;
		    <td width='25%'>&nbsp;</td>
		    <td width='25%'>&nbsp;</td></tr>
	<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'Act as'}</td>
		<td><select name='SIDE'>
				<option value='server' $selected{'SIDE'}{'server'}>$Lang::tr{'openvpn server'}</option>
				<option value='client' $selected{'SIDE'}{'client'}>$Lang::tr{'openvpn client'}</option>
			</select>
		</td>

 		<td class='boldbase'>$Lang::tr{'remote host/ip'}:</td>
		<td><input type='TEXT' name='REMOTE' value='$cgiparams{'REMOTE'}' /></td>
	</tr>

	<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'local subnet'}&nbsp;<img src='/blob.gif' alt='*' /></td>
		<td><input type='TEXT' name='LOCAL_SUBNET' value='$cgiparams{'LOCAL_SUBNET'}' /></td>

		<td class='boldbase' nowrap='nowrap'>$Lang::tr{'remote subnet'}&nbsp;<img src='/blob.gif' alt='*' /></td>
		<td><input type='text' name='REMOTE_SUBNET' value='$cgiparams{'REMOTE_SUBNET'}' /></td>
	</tr>

	<tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'ovpn subnet'}&nbsp;<img src='/blob.gif' alt='*' /></td>
		<td><input type='TEXT' name='OVPN_SUBNET' value='$cgiparams{'OVPN_SUBNET'}' /></td>

		<td class='boldbase' nowrap='nowrap'>$Lang::tr{'protocol'}</td>
		<td><select name='PROTOCOL'>
			<option value='udp' $selected{'PROTOCOL'}{'udp'}>UDP</option>
			<option value='tcp' $selected{'PROTOCOL'}{'tcp'}>TCP</option></select></td>
	</tr>

	<tr>
		<td class='boldbase'>$Lang::tr{'destination port'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
		<td><input type='TEXT' name='DEST_PORT' value='$cgiparams{'DEST_PORT'}' size='5' /></td>

		<td class='boldbase' nowrap='nowrap'>Management Port ($Lang::tr{'openvpn default'}: <span class="base">$Lang::tr{'destination port'}):</td>
		<td> <input type='TEXT' name='OVPN_MGMT' VALUE='$cgiparams{'OVPN_MGMT'}'size='5' /></td>
	</tr>

	<tr><td colspan=4><hr /></td></tr><tr>

	<tr>
		<td class='base'><b>$Lang::tr{'MTU settings'}</b></td>
	</tr>

        <tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'MTU'}</td>
		<td><input type='TEXT' name='MTU' VALUE='$cgiparams{'MTU'}'size='5' /></td>
		<td colspan='2'>$Lang::tr{'openvpn default'}: udp/tcp <span class="base">1500/1400</span></td>
	</tr>

	<tr><td class='boldbase' nowrap='nowrap'>fragment:</td>
		<td><input type='TEXT' name='FRAGMENT' VALUE='$cgiparams{'FRAGMENT'}'size='5' /></td>
		<td>$Lang::tr{'openvpn default'}: <span class="base">1300</span></td>
	</tr>

	<tr><td class='boldbase' nowrap='nowrap'>mssfix:</td>
		<td><input type='checkbox' name='MSSFIX' $checked{'MSSFIX'}{'on'} /></td>
		<td>$Lang::tr{'openvpn default'}: <span class="base">on</span></td>
	</tr>

        <tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'comp-lzo'}</td>
		<td><input type='checkbox' name='COMPLZO' $checked{'COMPLZO'}{'on'} /></td>
	</tr>

<tr><td colspan=4><hr /></td></tr><tr>
	<tr>
		<td class='base'><b>$Lang::tr{'ovpn crypt options'}:</b></td>
	</tr>

	<tr><td class='boldbase'>$Lang::tr{'cipher'}</td>
		<td><select name='DCIPHER'  id="n2ncipher" required>
				<option value='AES-256-GCM'		$selected{'DCIPHER'}{'AES-256-GCM'}>AES-GCM (256 $Lang::tr{'bit'})</option>
				<option value='AES-192-GCM'		$selected{'DCIPHER'}{'AES-192-GCM'}>AES-GCM (192 $Lang::tr{'bit'})</option>
				<option value='AES-128-GCM'		$selected{'DCIPHER'}{'AES-128-GCM'}>AES-GCM (128 $Lang::tr{'bit'})</option>
				<option value='CAMELLIA-256-CBC'	$selected{'DCIPHER'}{'CAMELLIA-256-CBC'}>CAMELLIA-CBC (256 $Lang::tr{'bit'})</option>
				<option value='CAMELLIA-192-CBC'	$selected{'DCIPHER'}{'CAMELLIA-192-CBC'}>CAMELLIA-CBC (192 $Lang::tr{'bit'})</option>
				<option value='CAMELLIA-128-CBC'	$selected{'DCIPHER'}{'CAMELLIA-128-CBC'}>CAMELLIA-CBC (128 $Lang::tr{'bit'})</option>
				<option value='AES-256-CBC' 	 	$selected{'DCIPHER'}{'AES-256-CBC'}>AES-CBC (256 $Lang::tr{'bit'}, $Lang::tr{'default'})</option>
				<option value='AES-192-CBC' 	 	$selected{'DCIPHER'}{'AES-192-CBC'}>AES-CBC (192 $Lang::tr{'bit'})</option>
				<option value='AES-128-CBC' 	 	$selected{'DCIPHER'}{'AES-128-CBC'}>AES-CBC (128 $Lang::tr{'bit'})</option>
				<option value='SEED-CBC' 			$selected{'DCIPHER'}{'SEED-CBC'}>SEED-CBC (128 $Lang::tr{'bit'})</option>
				<option value='DES-EDE3-CBC'	 	$selected{'DCIPHER'}{'DES-EDE3-CBC'}>DES-EDE3-CBC (192 $Lang::tr{'bit'}, $Lang::tr{'vpn weak'})</option>
				<option value='DESX-CBC' 			$selected{'DCIPHER'}{'DESX-CBC'}>DESX-CBC (192 $Lang::tr{'bit'}, $Lang::tr{'vpn weak'})</option>
				<option value='DES-EDE-CBC' 		$selected{'DCIPHER'}{'DES-EDE-CBC'}>DES-EDE-CBC (128 $Lang::tr{'bit'}, $Lang::tr{'vpn weak'})</option>
				<option value='BF-CBC' 				$selected{'DCIPHER'}{'BF-CBC'}>BF-CBC (128 $Lang::tr{'bit'}, $Lang::tr{'vpn weak'})</option>
				<option value='CAST5-CBC' 			$selected{'DCIPHER'}{'CAST5-CBC'}>CAST5-CBC (128 $Lang::tr{'bit'}, $Lang::tr{'vpn weak'})</option>
			</select>
		</td>

		<td class='boldbase'>$Lang::tr{'ovpn ha'}:</td>
		<td><select name='DAUTH' id="n2nhmac" $hmacdisabled>
				<option value='whirlpool'		$selected{'DAUTH'}{'whirlpool'}>Whirlpool (512 $Lang::tr{'bit'})</option>
				<option value='SHA512'			$selected{'DAUTH'}{'SHA512'}>SHA2 (512 $Lang::tr{'bit'})</option>
				<option value='SHA384'			$selected{'DAUTH'}{'SHA384'}>SHA2 (384 $Lang::tr{'bit'})</option>
				<option value='SHA256'			$selected{'DAUTH'}{'SHA256'}>SHA2 (256 $Lang::tr{'bit'})</option>
				<option value='SHA1'			$selected{'DAUTH'}{'SHA1'}>SHA1 (160 $Lang::tr{'bit'}, $Lang::tr{'vpn weak'})</option>
			</select>
		</td>
	</tr>
	<tr><td colspan=4><hr /></td></tr><tr>

END
;
	}

#### JAVA SCRIPT ####
# Validate N2N cipher. If GCM will be used, HMAC menu will be disabled onchange
print<<END;
	<script>
		var disable_options = false;
		document.getElementById('n2ncipher').onchange = function () {
			if((this.value == "AES-256-GCM"||this.value == "AES-192-GCM"||this.value == "AES-128-GCM")) {
				document.getElementById('n2nhmac').setAttribute('disabled', true);
			} else {
				document.getElementById('n2nhmac').removeAttribute('disabled');
			}
		}
	</script>
END

	print "<tr><td class='boldbase'>$Lang::tr{'remark title'}</td>";
	print "<td colspan='3'><input type='text' name='REMARK' value='$cgiparams{'REMARK'}' size='55' maxlength='50' /></td></tr></table>";

	if ($cgiparams{'TYPE'} eq 'host') {
      print "<tr><td>$Lang::tr{'enabled'} <input type='checkbox' name='ENABLED' $checked{'ENABLED'}{'on'} /></td>";
    }

		print"</tr></table><br><br>";

if ($cgiparams{'TYPE'} eq 'host') {
	    print "<table border='0' width='100%' cellspacing='1' cellpadding='0'><tr><td colspan='3'><hr><br><b>$Lang::tr{'ccd choose net'}</td></tr><tr><td height='20' colspan='3'></td></tr>";
	    my %vpnnet=();
	    my $vpnip;
	    &General::readhash("${General::swroot}/ovpn/settings", \%vpnnet);
	    $vpnip=$vpnnet{'DOVPN_SUBNET'};
	    &General::readhasharray("${General::swroot}/ovpn/ccd.conf", \%ccdconfhash);
	    my @ccdconf=();
		my $count=0;
		my $checked;
		$checked{'check1'}{'off'} = '';
	    $checked{'check1'}{'on'} = '';
	    $checked{'check1'}{$cgiparams{'CHECK1'}} = 'CHECKED';
	    print"<tr><td align='center' width='1%' valign='top'><input type='radio' name='CHECK1' value='dynamic' checked /></td><td align='left' valign='top' width='35%'>$Lang::tr{'ccd dynrange'} ($vpnip)</td><td width='30%'>";
	    print"</td></tr></table><br><br>";
		my $name=$cgiparams{'CHECK1'};
		$checked{'RG'}{$cgiparams{'RG'}} = 'CHECKED';
		$checked{'OTP_STATE'}{$cgiparams{'OTP_STATE'}} = 'CHECKED';

	if (! -z "${General::swroot}/ovpn/ccd.conf"){
		print"<table border='0' width='100%' cellspacing='1' cellpadding='0'><tr><td width='1%'></td><td width='30%' class='boldbase' align='center'><b>$Lang::tr{'ccd name'}</td><td width='15%' class='boldbase' align='center'><b>$Lang::tr{'network'}</td><td class='boldbase' align='center' width='18%'><b>$Lang::tr{'ccd clientip'}</td></tr>";
		foreach my $key (sort { uc($ccdconfhash{$a}[0]) cmp uc($ccdconfhash{$b}[0]) } keys %ccdconfhash) {
			$count++;
			@ccdconf=($ccdconfhash{$key}[0],$ccdconfhash{$key}[1]);
			if ($count % 2){print"<tr bgcolor='$Header::color{'color22'}'>";}else{print"<tr bgcolor='$Header::color{'color20'}'>";}
			print"<td align='center' width='1%'><input type='radio' name='CHECK1' value='$ccdconf[0]' $checked{'check1'}{$ccdconf[0]}/></td><td>$ccdconf[0]</td><td width='40%' align='center'>$ccdconf[1]</td><td align='left' width='10%'>";
			&fillselectbox($ccdconf[1],$ccdconf[0],$cgiparams{$name});
			print"</td></tr>";
		}
		print "</table><br><br><hr><br><br>";
	}
}

	&Header::closebox();
	if ($cgiparams{'KEY'} && $cgiparams{'AUTH'} eq 'psk') {

		} elsif (! $cgiparams{'KEY'}) {


	    my $disabled='';
	    my $cakeydisabled='';
	    my $cacrtdisabled='';
	    if ( ! -f "${General::swroot}/ovpn/ca/cakey.pem" ) { $cakeydisabled = "disabled='disabled'" } else { $cakeydisabled = "" };
	    if ( ! -f "${General::swroot}/ovpn/ca/cacert.pem" ) { $cacrtdisabled = "disabled='disabled'" } else { $cacrtdisabled = "" };

	    &Header::openbox('100%', 'LEFT', $Lang::tr{'authentication'});


 if ($cgiparams{'TYPE'} eq 'host') {

	print <<END;
	    <table width='100%' cellpadding='0' cellspacing='5' border='0'>

	    <tr><td><input type='radio' name='AUTH' value='certreq' $checked{'AUTH'}{'certreq'} $cakeydisabled /></td><td class='base'>$Lang::tr{'upload a certificate request'}</td><td class='base' rowspan='2'><input type='file' name='FH' size='30' $cacrtdisabled></td></tr>
	    <tr><td><input type='radio' name='AUTH' value='certfile' $checked{'AUTH'}{'certfile'} $cacrtdisabled /></td><td class='base'>$Lang::tr{'upload a certificate'}</td></tr>
	    <tr><td colspan='3'>&nbsp;</td></tr>
      <tr><td colspan='3'><hr /></td></tr>
      <tr><td colspan='3'>&nbsp;</td></tr>
	    <tr><td><input type='radio' name='AUTH' value='certgen' $checked{'AUTH'}{'certgen'} $cakeydisabled /></td><td class='base'>$Lang::tr{'generate a certificate'}</td><td>&nbsp;</td></tr>
	    <tr><td>&nbsp;</td><td class='base'>$Lang::tr{'users fullname or system hostname'}:&nbsp;<img src='/blob.gif' alt='*' /></td><td class='base' nowrap='nowrap'><input type='text' name='CERT_NAME' value='$cgiparams{'CERT_NAME'}' SIZE='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td><td class='base'>$Lang::tr{'users email'}:</td><td class='base' nowrap='nowrap'><input type='text' name='CERT_EMAIL' value='$cgiparams{'CERT_EMAIL'}' SIZE='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td><td class='base'>$Lang::tr{'users department'}:</td><td class='base' nowrap='nowrap'><input type='text' name='CERT_OU' value='$cgiparams{'CERT_OU'}' SIZE='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td><td class='base'>$Lang::tr{'organization name'}:</td><td class='base' nowrap='nowrap'><input type='text' name='CERT_ORGANIZATION' value='$cgiparams{'CERT_ORGANIZATION'}' SIZE='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td><td class='base'>$Lang::tr{'city'}:</td><td class='base' nowrap='nowrap'><input type='text' name='CERT_CITY' value='$cgiparams{'CERT_CITY'}' SIZE='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td><td class='base'>$Lang::tr{'state or province'}:</td><td class='base' nowrap='nowrap'><input type='text' name='CERT_STATE' value='$cgiparams{'CERT_STATE'}' SIZE='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td><td class='base'>$Lang::tr{'country'}:</td><td class='base'><select name='CERT_COUNTRY' $cakeydisabled>
END
;

} else {

	print <<END;
	    <table width='100%' cellpadding='0' cellspacing='5' border='0'>

	    <tr><td><input type='radio' name='AUTH' value='certgen' $checked{'AUTH'}{'certgen'} $cakeydisabled /></td><td class='base'>$Lang::tr{'generate a certificate'}</td><td>&nbsp;</td></tr>
	    <tr><td>&nbsp;</td><td class='base'>$Lang::tr{'users fullname or system hostname'}:&nbsp;<img src='/blob.gif' alt='*' /></td><td class='base' nowrap='nowrap'><input type='text' name='CERT_NAME' value='$cgiparams{'CERT_NAME'}' SIZE='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td><td class='base'>$Lang::tr{'users email'}:</td><td class='base' nowrap='nowrap'><input type='text' name='CERT_EMAIL' value='$cgiparams{'CERT_EMAIL'}' SIZE='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td><td class='base'>$Lang::tr{'users department'}:</td><td class='base' nowrap='nowrap'><input type='text' name='CERT_OU' value='$cgiparams{'CERT_OU'}' SIZE='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td><td class='base'>$Lang::tr{'organization name'}:</td><td class='base' nowrap='nowrap'><input type='text' name='CERT_ORGANIZATION' value='$cgiparams{'CERT_ORGANIZATION'}' SIZE='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td><td class='base'>$Lang::tr{'city'}:</td><td class='base' nowrap='nowrap'><input type='text' name='CERT_CITY' value='$cgiparams{'CERT_CITY'}' SIZE='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td><td class='base'>$Lang::tr{'state or province'}:</td><td class='base' nowrap='nowrap'><input type='text' name='CERT_STATE' value='$cgiparams{'CERT_STATE'}' SIZE='32' $cakeydisabled /></td></tr>
	    <tr><td>&nbsp;</td><td class='base'>$Lang::tr{'country'}:</td><td class='base'><select name='CERT_COUNTRY' $cakeydisabled>


END
;

}

	    foreach my $country (sort keys %{Countries::countries}) {
		print "<option value='$Countries::countries{$country}'";
		if ( $Countries::countries{$country} eq $cgiparams{'CERT_COUNTRY'} ) {
		    print " selected='selected'";
		}
		print ">$country</option>";
	    }

if ($cgiparams{'TYPE'} eq 'host') {
	print <<END;
	</select></td></tr>
		<td>&nbsp;</td><td class='base'>$Lang::tr{'valid till'} (days):&nbsp;<img src='/blob.gif' alt='*' /</td>
		<td class='base' nowrap='nowrap'><input type='text' name='DAYS_VALID' value='$cgiparams{'DAYS_VALID'}' size='32' $cakeydisabled /></td></tr>
		<tr><td>&nbsp;</td>
		<td class='base'>$Lang::tr{'pkcs12 file password'}:</td>
		<td class='base' nowrap='nowrap'><input type='password' name='CERT_PASS1' value='$cgiparams{'CERT_PASS1'}' size='32' $cakeydisabled /></td></tr>
		<tr><td>&nbsp;</td><td class='base'>$Lang::tr{'pkcs12 file password'}:<br>($Lang::tr{'confirmation'})</td>
		<td class='base' nowrap='nowrap'><input type='password' name='CERT_PASS2' value='$cgiparams{'CERT_PASS2'}' size='32' $cakeydisabled /></td></tr>
		<tr><td colspan='3'>&nbsp;</td></tr>
		<tr><td colspan='3'><hr /></td></tr>
		<tr><td class='base' colspan='3' align='left'><img src='/blob.gif' alt='*' />&nbsp;$Lang::tr{'required field'}</td></tr>
	</table>
END
}else{
	print <<END;
	</select></td></tr>
		<td>&nbsp;</td><td class='base'>$Lang::tr{'valid till'} (days):&nbsp;<img src='/blob.gif' alt='*' /</td>
		<td class='base' nowrap='nowrap'><input type='text' name='DAYS_VALID' value='$cgiparams{'DAYS_VALID'}' size='32' $cakeydisabled /></td></tr>
		<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
		<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
		<tr><td colspan='3'><hr /></td></tr>
		<tr><td class='base' colspan='3' align='left'><img src='/blob.gif' alt='*' />&nbsp;$Lang::tr{'required field'}</td></tr>
       </table>

END
}

	    &Header::closebox();

	}

if ($cgiparams{'TYPE'} eq 'host') {
	    print"<br><br>";
	    &Header::openbox('100%', 'LEFT', "$Lang::tr{'ccd client options'}:");


	print <<END;
	<table border='0' width='100%'>
	<tr><td width='20%'>$Lang::tr{'enable otp'}:</td><td colspan='3'><input type='checkbox' name='OTP_STATE' $checked{'OTP_STATE'}{'on'} /></td></tr>
	<tr><td width='20%'>Redirect Gateway:</td><td colspan='3'><input type='checkbox' name='RG' $checked{'RG'}{'on'} /></td></tr>
	<tr><td colspan='4'><b><br>$Lang::tr{'ccd routes'}</b></td></tr>
	<tr><td colspan='4'>&nbsp</td></tr>
	<tr><td valign='top'>$Lang::tr{'ccd iroute'}</td><td align='left' width='30%'><textarea name='IR' cols='26' rows='6' wrap='off'>
END

	if ($cgiparams{'IR'} ne ''){
		print $cgiparams{'IR'};
	}else{
		&General::readhasharray ("${General::swroot}/ovpn/ccdroute", \%ccdroutehash);
		foreach my $key (keys %ccdroutehash) {
			if( $cgiparams{'NAME'} eq $ccdroutehash{$key}[0]){
				foreach my $i (1 .. $#{$ccdroutehash{$key}}) {
						if ($ccdroutehash{$key}[$i] ne ''){
							print $ccdroutehash{$key}[$i]."\n";
						}
						$cgiparams{'IR'} .= $ccdroutehash{$key}[$i];
				}
			}
		}
	}

	print <<END;
</textarea></td><td valign='top' colspan='2'>$Lang::tr{'ccd iroutehint'}</td></tr>
	<tr><td colspan='4'><br></td></tr>
	<tr><td valign='top' rowspan='3'>$Lang::tr{'ccd iroute2'}</td><td align='left' valign='top' rowspan='3'><select name='IFROUTE' style="width: 205px"; size='6' multiple>
END

	my $set=0;
	my $selorange=0;
	my $selblue=0;
	my $selgreen=0;
	my $helpblue=0;
	my $helporange=0;
	my $other=0;
	my $none=0;
	my @temp=();

	our @current = ();
	open(FILE, "${General::swroot}/main/routing") ;
	@current = <FILE>;
	close (FILE);
	&General::readhasharray ("${General::swroot}/ovpn/ccdroute2", \%ccdroute2hash);
	#check for "none"
	foreach my $key (keys %ccdroute2hash) {
		if($ccdroute2hash{$key}[0] eq $cgiparams{'NAME'}){
			if ($ccdroute2hash{$key}[1] eq ''){
				$none=1;
				last;
			}
		}
	}
	if ($none ne '1'){
		print"<option>$Lang::tr{'ccd none'}</option>";
	}else{
		print"<option selected>$Lang::tr{'ccd none'}</option>";
	}
	#check if static routes are defined for client
	foreach my $line (@current) {
		chomp($line);
		$line=~s/\s*$//g; 			# remove newline
		@temp=split(/\,/,$line);
		$temp[1] = '' unless defined $temp[1]; # not always populated
		my ($a,$b) = split(/\//,$temp[1]);
		$temp[1] = $a."/".&General::iporsubtocidr($b);
		foreach my $key (keys %ccdroute2hash) {
			if($ccdroute2hash{$key}[0] eq $cgiparams{'NAME'}){
				foreach my $i (1 .. $#{$ccdroute2hash{$key}}) {
					if($ccdroute2hash{$key}[$i] eq $a."/".&General::iporsubtodec($b)){
						$set=1;
					}
				}
			}
		}
		if ($set == '1' && $#temp != -1){ print"<option selected>$temp[1]</option>";$set=0;}elsif($set == '0' && $#temp != -1){print"<option>$temp[1]</option>";}
	}

	my %vpnconfig = ();
	&General::readhasharray("${General::swroot}/vpn/config", \%vpnconfig);
	foreach my $vpn (keys %vpnconfig) {
		# Skip all disabled VPN connections
		my $enabled = $vpnconfig{$vpn}[0];
		next unless ($enabled eq "on");

		my $name = $vpnconfig{$vpn}[1];

		# Remote subnets
		my @networks = split(/\|/, $vpnconfig{$vpn}[11]);
		foreach my $network (@networks) {
			my $selected = "";

			foreach my $key (keys %ccdroute2hash) {
				if ($ccdroute2hash{$key}[0] eq $cgiparams{'NAME'}) {
					foreach my $i (1 .. $#{$ccdroute2hash{$key}}) {
						if ($ccdroute2hash{$key}[$i] eq $network) {
							$selected = "selected";
						}
					}
				}
			}

			print "<option value=\"$network\" $selected>$name ($network)</option>\n";
		}
	}

	#check if green,blue,orange are defined for client
	foreach my $key (keys %ccdroute2hash) {
		if($ccdroute2hash{$key}[0] eq $cgiparams{'NAME'}){
			$other=1;
			foreach my $i (1 .. $#{$ccdroute2hash{$key}}) {
				if ($ccdroute2hash{$key}[$i] eq $netsettings{'GREEN_NETADDRESS'}."/".&General::iporsubtodec($netsettings{'GREEN_NETMASK'})){
					$selgreen=1;
				}
				if (&Header::blue_used()){
					if( $ccdroute2hash{$key}[$i] eq $netsettings{'BLUE_NETADDRESS'}."/".&General::iporsubtodec($netsettings{'BLUE_NETMASK'})) {
						$selblue=1;
					}
				}
				if (&Header::orange_used()){
					if( $ccdroute2hash{$key}[$i] eq $netsettings{'ORANGE_NETADDRESS'}."/".&General::iporsubtodec($netsettings{'ORANGE_NETMASK'}) ) {
						$selorange=1;
					}
				}
			}
		}
	}
	if (&Header::blue_used() && $selblue == '1'){ print"<option selected>$Lang::tr{'blue'}</option>";$selblue=0;}elsif(&Header::blue_used() && $selblue == '0'){print"<option>$Lang::tr{'blue'}</option>";}
	if (&Header::orange_used() && $selorange == '1'){ print"<option selected>$Lang::tr{'orange'}</option>";$selorange=0;}elsif(&Header::orange_used() && $selorange == '0'){print"<option>$Lang::tr{'orange'}</option>";}
	if ($selgreen == '1' || $other == '0'){ print"<option selected>$Lang::tr{'green'}</option>";$set=0;}else{print"<option>$Lang::tr{'green'}</option>";};

	print<<END;
	</select></td><td valign='top'>DNS1:</td><td valign='top'><input type='TEXT' name='CCD_DNS1' value='$cgiparams{'CCD_DNS1'}' size='30' /></td></tr>
	<tr valign='top'><td>DNS2:</td><td><input type='TEXT' name='CCD_DNS2' value='$cgiparams{'CCD_DNS2'}' size='30' /></td></tr>
	<tr valign='top'><td valign='top'>WINS:</td><td><input type='TEXT' name='CCD_WINS' value='$cgiparams{'CCD_WINS'}' size='30' /></td></tr></table><br><hr>

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

    open(FILE, "/var/run/ovpnserver.log");
    my @status = <FILE>;
    close(FILE);

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
    if ($cgiparams{'DDEST_PORT'} eq '') {
		$cgiparams{'DDEST_PORT'} =  '1194';
    }
    if ($cgiparams{'DMTU'} eq '') {
		$cgiparams{'DMTU'} =  '1400';
    }
    if ($cgiparams{'MSSFIX'} eq '') {
		$cgiparams{'MSSFIX'} = 'off';
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

    $selected{'DPROTOCOL'}{'udp'} = '';
    $selected{'DPROTOCOL'}{'tcp'} = '';
    $selected{'DPROTOCOL'}{$cgiparams{'DPROTOCOL'}} = 'SELECTED';

    &Header::showhttpheaders();
    &Header::openpage($Lang::tr{'status ovpn'}, 1, '');
    &Header::openbigbox('100%', 'LEFT', '', $errormessage);

	# Show any errors and warnings
	&Header::errorbox($errormessage);

	if ($warnmessage) {
		&Header::openbox('100%', 'LEFT', $Lang::tr{'warning messages'});
		print "$warnmessage<br>";
		print "$Lang::tr{'fwdfw warn1'}<br>";
		&Header::closebox();
		print"<center><form method='post'><input type='submit' name='ACTION' value='$Lang::tr{'ok'}' style='width: 5em;'></form>";
		&Header::closepage();
		exit 0;
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

	# Show the service status
	&Header::ServiceStatus({
		$Lang::tr{'ovpn roadwarrior server'} => {
			"process" => "openvpn",
			"pidfile" => "/var/run/openvpn.pid",
		}
	});

	print <<END;
    <table width='100%' border='0'>
    <form method='post'>
    <tr><td class='boldbase'>$Lang::tr{'ovpn server status'}</td>
    <td align='left'>$sactive</td>
    <tr><td class='boldbase'>$Lang::tr{'ovpn on red'}</td>
    <td><input type='checkbox' name='ENABLED' $checked{'ENABLED'}{'on'} /></td>
END
;
    if (&Header::blue_used()) {
	print "<tr><td class='boldbase'>$Lang::tr{'ovpn on blue'}</td>";
	print "<td><input type='checkbox' name='ENABLED_BLUE' $checked{'ENABLED_BLUE'}{'on'} /></td>";
    }
    if (&Header::orange_used()) {
	print "<tr><td class='boldbase'>$Lang::tr{'ovpn on orange'}</td>";
	print "<td><input type='checkbox' name='ENABLED_ORANGE' $checked{'ENABLED_ORANGE'}{'on'} /></td>";
    }

	print <<END;

	<tr><td colspan='4'><br></td></tr>
	<tr>
		<td class='base'><b>$Lang::tr{'net config'}:</b></td>
	</tr>
    <tr><td colspan='1'><br></td></tr>

    <tr><td class='base' nowrap='nowrap' colspan='2'>$Lang::tr{'local vpn hostname/ip'}:<br /><input type='text' name='VPN_IP' value='$cgiparams{'VPN_IP'}' size='30' /></td>
	<td class='boldbase' nowrap='nowrap' colspan='2'>$Lang::tr{'ovpn subnet'}<br /><input type='TEXT' name='DOVPN_SUBNET' value='$cgiparams{'DOVPN_SUBNET'}' size='30' /></td></tr>
    <tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'protocol'}</td>
        <td><select name='DPROTOCOL'><option value='udp' $selected{'DPROTOCOL'}{'udp'}>UDP</option>
               			    <option value='tcp' $selected{'DPROTOCOL'}{'tcp'}>TCP</option></select></td>
        <td class='boldbase'>$Lang::tr{'destination port'}:</td>
        <td><input type='TEXT' name='DDEST_PORT' value='$cgiparams{'DDEST_PORT'}' size='5' /></td></tr>
    <tr><td class='boldbase' nowrap='nowrap'>$Lang::tr{'MTU'}&nbsp;</td>
        <td> <input type='TEXT' name='DMTU' VALUE='$cgiparams{'DMTU'}' size='5' /></td>
    </tr>

	<tr><td colspan='4'><br></td></tr>
END
;

    if ( $srunning eq "yes" ) {
	print "<tr><td align='right' colspan='4'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' disabled='disabled' />";
	print "<input type='submit' name='ACTION' value='$Lang::tr{'ccd net'}' />";
	print "<input type='submit' name='ACTION' value='$Lang::tr{'advanced server'}' />";
	print "<input type='submit' name='ACTION' value='$Lang::tr{'stop ovpn server'}' /></td></tr>";
    } else{
	print "<tr><td align='right' colspan='4'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' />";
	print "<input type='submit' name='ACTION' value='$Lang::tr{'ccd net'}' />";
	print "<input type='submit' name='ACTION' value='$Lang::tr{'advanced server'}' />";
	if (( -e "${General::swroot}/ovpn/ca/cacert.pem" &&
	     -e "${General::swroot}/ovpn/certs/servercert.pem" &&
	     -e "${General::swroot}/ovpn/certs/serverkey.pem") &&
	    (( $cgiparams{'ENABLED'} eq 'on') ||
	    ( $cgiparams{'ENABLED_BLUE'} eq 'on') ||
	    ( $cgiparams{'ENABLED_ORANGE'} eq 'on'))){
	    print "<input type='submit' name='ACTION' value='$Lang::tr{'start ovpn server'}' /></td></tr>";
	} else {
	    print "<input type='submit' name='ACTION' value='$Lang::tr{'start ovpn server'}' disabled='disabled' /></td></tr>";
	}
    }
    print "</form></table>";
    &Header::closebox();

    if ( -f "${General::swroot}/ovpn/ca/cacert.pem" ) {
###
#<td width='25%' class='boldbase' align='center'><b>$Lang::tr{'remark'}</b><br /><img src='/images/null.gif' width='125' height='1' border='0' alt='L2089' /></td>
###

    &Header::openbox('100%', 'LEFT', $Lang::tr{'connection status and controlc' });
	;
	my $id = 0;
	my $gif;
	my $col1="";
	my $lastnet;
	foreach my $key (sort { ncmp ($confighash{$a}[32],$confighash{$b}[32]) } sort { ncmp ($confighash{$a}[1],$confighash{$b}[1]) } keys %confighash) {
		if ($confighash{$key}[32] eq "" && $confighash{$key}[3] eq 'net' ){$confighash{$key}[32]=$Lang::tr{'fwhost OpenVPN N-2-N'};}
		if ($confighash{$key}[32] eq "dynamic"){$confighash{$key}[32]=$Lang::tr{'ccd dynrange'};}
		if($id == 0){
			print"<b>$confighash{$key}[32]</b>";
			print <<END;
	<table width='100%' cellspacing='1' cellpadding='0' class='tbl'>
<tr>
	<th width='10%' class='boldbase' align='center'><b>$Lang::tr{'name'}</b></th>
	<th width='15%' class='boldbase' align='center'><b>$Lang::tr{'type'}</b></th>
	<th width='20%' class='boldbase' align='center'><b>$Lang::tr{'remark'}</b></th>
	<th width='10%' class='boldbase' align='center'><b>$Lang::tr{'status'}</b></th>
	<th width='5%' class='boldbase' colspan='8' align='center'><b>$Lang::tr{'action'}</b></th>
</tr>
END
		}
		if ($id > 0 && $lastnet ne $confighash{$key}[32]){
			print "</table><br>";
			print"<b>$confighash{$key}[32]</b>";
			print <<END;
	<table width='100%' cellspacing='1' cellpadding='0' class='tbl'>
<tr>
	<th width='10%' class='boldbase' align='center'><b>$Lang::tr{'name'}</b></th>
	<th width='15%' class='boldbase' align='center'><b>$Lang::tr{'type'}</b></th>
	<th width='20%' class='boldbase' align='center'><b>$Lang::tr{'remark'}</b></th>
	<th width='10%' class='boldbase' align='center'><b>$Lang::tr{'status'}</b></th>
	<th width='5%' class='boldbase' colspan='8' align='center'><b>$Lang::tr{'action'}</b></th>
</tr>
END
		}
	if ($confighash{$key}[0] eq 'on') { $gif = 'on.gif'; } else { $gif = 'off.gif'; }

	# Create some simple booleans to check the status
	my $hasExpired;
	my $expiresSoon;

	# Fetch information about the certificate for non-N2N connections only
	if ($confighash{$key}[3] ne 'net') {
		my @cavalid = &General::system_output("/usr/bin/openssl", "x509", "-text",
			"-in", "${General::swroot}/ovpn/certs/$confighash{$key}[1]cert.pem");

		my $expiryDate = 0;

		# Parse the certificate information
		foreach my $line (@cavalid) {
			if ($line =~ /Not After : (.*)[\n]/) {
				$expiryDate = &Date::Parse::str2time($1);
				last;
			}
		}

		# Calculate the remaining time
		my $remainingTime = $expiryDate - time();

		# Determine whether the certificate has already expired, or will so soon
		$hasExpired = ($remainingTime <= 0);
		$expiresSoon = ($remainingTime <= 30 * 24 * 3600);

	} else {
		# Populate booleans with dummy values for N2N connections (#13066)
		$hasExpired = 0;
		$expiresSoon = 0;
	}

	print "<tr>";

	if ($hasExpired || $expiresSoon) {
		$col="bgcolor='$Header::color{'color14'}'";
	} elsif ($id % 2) {
		$col="bgcolor='$Header::color{'color20'}'";
	} else {
		$col="bgcolor='$Header::color{'color22'}'";
	}
	print "<td align='center' nowrap='nowrap' $col>$confighash{$key}[1]";
	if ($hasExpired) {
		print " ($Lang::tr{'openvpn cert has expired'})";
	} elsif ($expiresSoon) {
		print " ($Lang::tr{'openvpn cert expires soon'})";
	}
	print "</td>";
	print "<td align='center' nowrap='nowrap' $col>" . $Lang::tr{"$confighash{$key}[3]"} . " (" . $Lang::tr{"$confighash{$key}[4]"} . ")</td>";
	print "<td align='center' $col>$confighash{$key}[25]</td>";
	$col1="class='status is-disconnected'";
	my $active = "$Lang::tr{'capsclosed'}";

	if ($confighash{$key}[0] eq 'off') {
		$col1="class='status is-disabled'";
		$active = "$Lang::tr{'capsclosed'}";
	} else {
       if ($confighash{$key}[3] eq 'net') {

        if (-e "/var/run/$confighash{$key}[1]n2n.pid") {
          my @output = "";
          my @tustate = "";
          my $tport = $confighash{$key}[22];
          my $tnet = new Net::Telnet ( Timeout=>5, Errmode=>'return', Port=>$tport);
          if ($tport ne '') {
          $tnet->open('127.0.0.1');
          @output = $tnet->cmd(String => 'state', Prompt => '/(END.*\n|ERROR:.*\n)/');
          @tustate = split(/\,/, $output[1]);
###
#CONNECTING    -- OpenVPN's initial state.
#WAIT          -- (Client only) Waiting for initial response from server.
#AUTH          -- (Client only) Authenticating with server.
#GET_CONFIG    -- (Client only) Downloading configuration options from server.
#ASSIGN_IP     -- Assigning IP address to virtual network interface.
#ADD_ROUTES    -- Adding routes to system.
#CONNECTED     -- Initialization Sequence Completed.
#RECONNECTING  -- A restart has occurred.
#EXITING       -- A graceful exit is in progress.
####

		if (($tustate[1] eq 'CONNECTED') || ($tustate[1] eq 'WAIT')) {
			$col1="class='status is-connected'";
			$active = "$Lang::tr{'capsopen'}";
		}else {
			$col1="class='status is-disconnected'";
			$active = "$tustate[1]";
		}
           }
           }
        }else {

				my $cn;
				my @match = ();
		foreach my $line (@status) {
			chomp($line);
			if ( $line =~ /^(.+),(\d+\.\d+\.\d+\.\d+\:\d+),(\d+),(\d+),(.+)/) {
				@match = split(m/^(.+),(\d+\.\d+\.\d+\.\d+\:\d+),(\d+),(\d+),(.+)/, $line);
				if ($match[1] ne "Common Name") {
					$cn = $match[1];
				}
				if ($cn eq "$confighash{$key}[2]") {
					$col1="class='status is-connected'";
					$active = "$Lang::tr{'capsopen'}";
				}
			}
		}
	}
}


       if ($confighash{$key}[41] eq "pass") {
               print <<END;
                       <td align='center' $col1>$active</td>

                       <form method='post' name='frm${key}a'><td align='center' $col>
                           <input type='image'  name='$Lang::tr{'dl client arch'}' src='/images/openvpn_encrypted.png'
                                       alt='$Lang::tr{'dl client arch'}' title='$Lang::tr{'dl client arch'}' border='0' />
                           <input type='hidden' name='ACTION' value='$Lang::tr{'dl client arch'}' />
                           <input type='hidden' name='MODE' value='secure' />
                           <input type='hidden' name='KEY' value='$key' />
                       </td></form>
END

       ; } elsif ($confighash{$key}[41] eq "no-pass") {
		print <<END;
                       <td align='center' $col1>$active</td>

                       <form method='post' name='frm${key}a'><td align='center' $col>
				<input type='image'  name='$Lang::tr{'dl client arch insecure'}' src='/images/openvpn.png'
					alt='$Lang::tr{'dl client arch insecure'}' title='$Lang::tr{'dl client arch insecure'}' border='0' />
				<input type='hidden' name='ACTION' value='$Lang::tr{'dl client arch'}' />
				<input type='hidden' name='MODE' value='insecure' />
				<input type='hidden' name='KEY' value='$key' />
			</td></form>
END
	; } else {
		print "<td $col>&nbsp;</td>";
	}

	if ($confighash{$key}[4] eq 'cert') {
	    print <<END;
	    <form method='post' name='frm${key}b'><td align='center' $col>
		<input type='image' name='$Lang::tr{'show certificate'}' src='/images/info.gif' alt='$Lang::tr{'show certificate'}' title='$Lang::tr{'show certificate'}' border='0' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'show certificate'}' />
		<input type='hidden' name='KEY' value='$key' />
	    </td></form>
END
	; } else {
	    print "<td>&nbsp;</td>";
	}

   if ($confighash{$key}[43] eq 'on') {
      print <<END;
<form method='post' name='frm${key}o'><td align='center' $col>
<input type='image' name='$Lang::tr{'show otp qrcode'}' src='/images/qr-code.png' alt='$Lang::tr{'show otp qrcode'}' title='$Lang::tr{'show otp qrcode'}' border='0' />
<input type='hidden' name='ACTION' value='$Lang::tr{'show otp qrcode'}' />
<input type='hidden' name='KEY' value='$key' />
</td></form>
END
; } else {
      print "<td $col>&nbsp;</td>";
   }

	if ($confighash{$key}[4] eq 'cert' && -f "${General::swroot}/ovpn/certs/$confighash{$key}[1].p12") {
	    print <<END;
	    <form method='post' name='frm${key}c'><td align='center' $col>
		<input type='image' name='$Lang::tr{'download pkcs12 file'}' src='/images/media-floppy.png' alt='$Lang::tr{'download pkcs12 file'}' title='$Lang::tr{'download pkcs12 file'}' border='0' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'download pkcs12 file'}' />
		<input type='hidden' name='KEY' value='$key' />
	    </td></form>
END
	; } elsif ($confighash{$key}[4] eq 'cert') {
	    print <<END;
	    <form method='post' name='frm${key}c'><td align='center' $col>
		<input type='image' name='$Lang::tr{'download certificate'}' src='/images/media-floppy.png' alt='$Lang::tr{'download certificate'}' title='$Lang::tr{'download certificate'}' border='0' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'download certificate'}' />
		<input type='hidden' name='KEY' value='$key' />
	    </td></form>
END
	; } else {
	    print "<td>&nbsp;</td>";
	}
	print <<END
	<form method='post' name='frm${key}d'><td align='center' $col>
	    <input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif' alt='$Lang::tr{'toggle enable disable'}' title='$Lang::tr{'toggle enable disable'}' border='0' />
	    <input type='hidden' name='ACTION' value='$Lang::tr{'toggle enable disable'}' />
	    <input type='hidden' name='KEY' value='$key' />
	</td></form>

	<form method='post' name='frm${key}e'><td align='center' $col>
	    <input type='hidden' name='ACTION' value='$Lang::tr{'edit'}' />
	    <input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' width='20' height='20' border='0'/>
	    <input type='hidden' name='KEY' value='$key' />
	</td></form>
	<form method='post' name='frm${key}f'><td align='center' $col>
	    <input type='hidden' name='ACTION' value='$Lang::tr{'remove'}' />
	    <input type='image'  name='$Lang::tr{'remove'}' src='/images/delete.gif' alt='$Lang::tr{'remove'}' title='$Lang::tr{'remove'}' width='20' height='20' border='0' />
	    <input type='hidden' name='KEY' value='$key' />
	</td></form>
	</tr>
END
	;
	$id++;
	$lastnet = $confighash{$key}[32];
    }
    print"</table>";
    ;

    # If the config file contains entries, print Key to action icons
    if ( $id ) {
    print <<END;
       <table width='85%' border='0'>
       <tr>
		<td class='boldbase'>&nbsp; <b>$Lang::tr{'legend'}:</b></td>
              <td>&nbsp; &nbsp; <img src='/images/openvpn.png' alt='?RELOAD'/></td>
              <td class='base'>$Lang::tr{'dl client arch insecure'}</td>
              <td>&nbsp; &nbsp; <img src='/images/openvpn_encrypted.png' alt='?RELOAD'/></td>
              <td class='base'>$Lang::tr{'dl client arch'}</td>
		<td>&nbsp; &nbsp; <img src='/images/info.gif' alt='$Lang::tr{'show certificate'}' /></td>
		<td class='base'>$Lang::tr{'show certificate'}</td>
              <td>&nbsp; &nbsp; <img src='/images/qr-code.png' alt='$Lang::tr{'show otp qrcode'}'/></td>
              <td class='base'>$Lang::tr{'show otp qrcode'}</td>
       </tr>
       <tr>
              <td>&nbsp; </td>
              <td>&nbsp; &nbsp; <img src='/images/media-floppy.png' alt='?FLOPPY' /></td>
              <td class='base'>$Lang::tr{'download certificate'}</td>
              <td>&nbsp; <img src='/images/off.gif' alt='?OFF' /></td>
              <td class='base'>$Lang::tr{'click to enable'}</td>
              <td>&nbsp; <img src='/images/on.gif' alt='$Lang::tr{'click to disable'}' /></td>
              <td class='base'>$Lang::tr{'click to disable'}</td>

		<td>&nbsp; &nbsp; <img src='/images/edit.gif' alt='$Lang::tr{'edit'}' /></td>
		<td class='base'>$Lang::tr{'edit'}</td>
		<td>&nbsp; &nbsp; <img src='/images/delete.gif' alt='$Lang::tr{'remove'}' /></td>
		<td class='base'>$Lang::tr{'remove'}</td>
       </tr>
       </table><br>
END
    ;
    }

    print <<END;
    <table width='100%'>
    <form method='post'>
    <tr><td align='right'>
		<input type='submit' name='ACTION' value='$Lang::tr{'add'}' />
		<input type='submit' name='ACTION' value='$Lang::tr{'ovpn con stat'}' $activeonrun /></td>
	</tr>
    </form>
    </table>
END
    ;
	&Header::closebox();
	}

    # CA/key listing
    &Header::openbox('100%', 'LEFT', "$Lang::tr{'certificate authorities'}");
    print <<END;
    <table width='100%' cellspacing='1' cellpadding='0' class='tbl'>
    <tr>
		<th width='25%' class='boldbase' align='center'><b>$Lang::tr{'name'}</b></th>
		<th width='65%' class='boldbase' align='center'><b>$Lang::tr{'subject'}</b></th>
		<th width='10%' class='boldbase' colspan='3' align='center'><b>$Lang::tr{'action'}</b></th>
    </tr>
END
    ;
    my $col1="bgcolor='$Header::color{'color22'}'";
    my $col2="bgcolor='$Header::color{'color20'}'";
    # DH parameter line
    my $col3="bgcolor='$Header::color{'color22'}'";
    # ta.key line
    my $col4="bgcolor='$Header::color{'color20'}'";

    if (-f "${General::swroot}/ovpn/ca/cacert.pem") {
		my @casubject = &General::system_output("/usr/bin/openssl", "x509", "-text", "-in", "${General::swroot}/ovpn/ca/cacert.pem");
		my $casubject;

		foreach my $line (@casubject) {
			if ($line =~ /Subject: (.*)[\n]/) {
				$casubject    = $1;
				$casubject    =~ s+/Email+, E+;
				$casubject    =~ s/ ST=/ S=/;

				last;
			}
		}

		print <<END;
		<tr>
			<td class='base' $col1>$Lang::tr{'root certificate'}</td>
			<td class='base' $col1>$casubject</td>
			<form method='post' name='frmrootcrta'><td width='3%' align='center' $col1>
			<input type='hidden' name='ACTION' value='$Lang::tr{'show root certificate'}' />
			<input type='image' name='$Lang::tr{'edit'}' src='/images/info.gif' alt='$Lang::tr{'show root certificate'}' title='$Lang::tr{'show root certificate'}' width='20' height='20' border='0' />
			</form>
			<form method='post' name='frmrootcrtb'><td width='3%' align='center' $col1>
			<input type='image' name='$Lang::tr{'download root certificate'}' src='/images/media-floppy.png' alt='$Lang::tr{'download root certificate'}' title='$Lang::tr{'download root certificate'}' border='0' />
			<input type='hidden' name='ACTION' value='$Lang::tr{'download root certificate'}' />
			</form>
			<td width='4%' $col1>&nbsp;</td>
		</tr>
END
		;
    } else {
		# display rootcert generation buttons
		print <<END;
		<tr>
			<td class='base' $col1>$Lang::tr{'root certificate'}:</td>
			<td class='base' $col1>$Lang::tr{'not present'}</td>
			<td colspan='3' $col1>&nbsp;</td>
		</tr>
END
		;
    }

    if (-f "${General::swroot}/ovpn/certs/servercert.pem") {
		my @hostsubject = &General::system_output("/usr/bin/openssl", "x509", "-text", "-in", "${General::swroot}/ovpn/certs/servercert.pem");
		my $hostsubject;

		foreach my $line (@hostsubject) {
			if ($line =~ /Subject: (.*)[\n]/) {
				$hostsubject    = $1;
				$hostsubject    =~ s+/Email+, E+;
				$hostsubject    =~ s/ ST=/ S=/;

				last;
			}
		}

		print <<END;
		<tr>
			<td class='base' $col2>$Lang::tr{'host certificate'}</td>
			<td class='base' $col2>$hostsubject</td>
			<form method='post' name='frmhostcrta'><td width='3%' align='center' $col2>
			<input type='hidden' name='ACTION' value='$Lang::tr{'show host certificate'}' />
			<input type='image' name='$Lang::tr{'show host certificate'}' src='/images/info.gif' alt='$Lang::tr{'show host certificate'}' title='$Lang::tr{'show host certificate'}' width='20' height='20' border='0' />
			</form>
			<form method='post' name='frmhostcrtb'><td width='3%' align='center' $col2>
			<input type='image' name="$Lang::tr{'download host certificate'}" src='/images/media-floppy.png' alt="$Lang::tr{'download host certificate'}" title="$Lang::tr{'download host certificate'}" border='0' />
			<input type='hidden' name='ACTION' value="$Lang::tr{'download host certificate'}" />
			</td></form>
			<td width='4%' $col2>&nbsp;</td>
		</tr>
END
		;
    } else {
		# Nothing
		print <<END;
		<tr>
			<td width='25%' class='base' $col2>$Lang::tr{'host certificate'}:</td>
			<td class='base' $col2>$Lang::tr{'not present'}</td>
			</td><td colspan='3' $col2>&nbsp;</td>
		</tr>
END
		;
    }

    # Adding ta.key to chart
    if (-f "${General::swroot}/ovpn/certs/ta.key") {
		open(FILE, "${General::swroot}/ovpn/certs/ta.key");
		my @tasubject = <FILE>;
		close(FILE);

		my $tasubject;
		foreach my $line (@tasubject) {
			if($line =~ /# (.*)[\n]/) {
				$tasubject    = $1;

				last;
			}
		}

		print <<END;

		<tr>
			<td class='base' $col4>$Lang::tr{'ta key'}</td>
			<td class='base' $col4>$tasubject</td>
			<form method='post' name='frmtakey'><td width='3%' align='center' $col4>
			<input type='hidden' name='ACTION' value='$Lang::tr{'show tls-auth key'}' />
			<input type='image' name='$Lang::tr{'edit'}' src='/images/info.gif' alt='$Lang::tr{'show tls-auth key'}' title='$Lang::tr{'show tls-auth key'}' width='20' height='20' border='0' />
			</form>
			<form method='post' name='frmtakey'><td width='3%' align='center' $col4>
			<input type='image' name='$Lang::tr{'download tls-auth key'}' src='/images/media-floppy.png' alt='$Lang::tr{'download tls-auth key'}' title='$Lang::tr{'download tls-auth key'}' border='0' />
			<input type='hidden' name='ACTION' value='$Lang::tr{'download tls-auth key'}' />
			</form>
			<td width='4%' $col4>&nbsp;</td>
		</tr>
END
		;
    } else {
		# Nothing
		print <<END;
		<tr>
			<td width='25%' class='base' $col4>$Lang::tr{'ta key'}:</td>
			<td class='base' $col4>$Lang::tr{'not present'}</td>
			<td colspan='3' $col4>&nbsp;</td>
		</tr>
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
				print "<tr bgcolor='$Header::color{'color20'}'>\n";
			} else {
				print "<tr bgcolor='$Header::color{'color22'}'>\n";
			}
			print "<td class='base'>$cahash{$key}[0]</td>\n";
			print "<td class='base'>$cahash{$key}[1]</td>\n";
			print <<END;
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
		print <<END;
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

	<br><hr><br>

	<form method='post' enctype='multipart/form-data'>
		<table border='0' width='100%'>
			<tr>
				<td colspan='4'><b>$Lang::tr{'upload ca certificate'}</b></td>
			</tr>

			<tr>
				<td width='10%'>$Lang::tr{'ca name'}:</td>
				<td width='30%'><input type='text' name='CA_NAME' value='$cgiparams{'CA_NAME'}' size='15' align='left'></td>
				<td width='30%'><input type='file' name='FH' size='25'>
				<td width='30%'align='right'><input type='submit' name='ACTION' value='$Lang::tr{'upload ca certificate'}'></td>
			</tr>

			<tr>
				<td colspan='3'>&nbsp;</td>
				<td align='right'><input type='submit' name='ACTION' value='$Lang::tr{'show crl'}' /></td>
			</tr>
		</table>
	</form>

	<br><hr>
END
	;

    if ( $srunning eq "yes" ) {
		print "<div align='center'><form method='post'><input type='submit' name='ACTION' value='$Lang::tr{'remove x509'}' disabled='disabled' /></div></form>\n";
    } else {
		print "<div align='center'><form method='post'><input type='submit' name='ACTION' value='$Lang::tr{'remove x509'}' /></div></form>\n";
    }
	&Header::closebox();
END
	;

&Header::closepage();

