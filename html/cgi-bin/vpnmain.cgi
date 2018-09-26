#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2013  IPFire Team  info@ipfire.org                       #
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

use Net::DNS;
use File::Copy;
use File::Temp qw/ tempfile tempdir /;
use strict;
use Sort::Naturally;
# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "${General::swroot}/countries.pl";

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::colourgreen}, ${Header::colourblue} );
undef (@dummy);

###
### Initialize variables
###
my $sleepDelay = 4; # after a call to ipsecctrl S or R, wait this delay (seconds) before reading status (let the ipsec do its job)
my %netsettings=();
our %cgiparams=();
our %vpnsettings=();
my %checked=();
my %confighash=();
my %cahash=();
my %selected=();
my $warnmessage = '';
my $errormessage = '';

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

my %INACTIVITY_TIMEOUTS = (
	300		=> $Lang::tr{'five minutes'},
	600		=> $Lang::tr{'ten minutes'},
	900		=> $Lang::tr{'fifteen minutes'},
	1800		=> $Lang::tr{'thirty minutes'},
	3600		=> $Lang::tr{'one hour'},
	43200		=> $Lang::tr{'twelve hours'},
	86400		=> $Lang::tr{'24 hours'},
	0		=> "- $Lang::tr{'unlimited'} -",
);

my $col="";

$cgiparams{'ENABLED'} = 'off';
$cgiparams{'EDIT_ADVANCED'} = 'off';
$cgiparams{'ACTION'} = '';
$cgiparams{'CA_NAME'} = '';
$cgiparams{'KEY'} = '';
$cgiparams{'TYPE'} = '';
$cgiparams{'ADVANCED'} = '';
$cgiparams{'NAME'} = '';
$cgiparams{'LOCAL_SUBNET'} = '';
$cgiparams{'REMOTE_SUBNET'} = '';
$cgiparams{'REMOTE'} = '';
$cgiparams{'LOCAL_ID'} = '';
$cgiparams{'REMOTE_ID'} = '';
$cgiparams{'REMARK'} = '';
$cgiparams{'PSK'} = '';
$cgiparams{'CERT_NAME'} = '';
$cgiparams{'CERT_EMAIL'} = '';
$cgiparams{'CERT_OU'} = '';
$cgiparams{'CERT_ORGANIZATION'} = '';
$cgiparams{'CERT_CITY'} = '';
$cgiparams{'CERT_STATE'} = '';
$cgiparams{'CERT_COUNTRY'} = '';
$cgiparams{'SUBJECTALTNAME'} = '';
$cgiparams{'CERT_PASS1'} = '';
$cgiparams{'CERT_PASS2'} = '';
$cgiparams{'ROOTCERT_HOSTNAME'} = '';
$cgiparams{'ROOTCERT_COUNTRY'} = '';
$cgiparams{'P12_PASS'} = '';
$cgiparams{'ROOTCERT_ORGANIZATION'} = '';
$cgiparams{'ROOTCERT_HOSTNAME'} = '';
$cgiparams{'ROOTCERT_EMAIL'} = '';
$cgiparams{'ROOTCERT_OU'} = '';
$cgiparams{'ROOTCERT_CITY'} = '';
$cgiparams{'ROOTCERT_STATE'} = '';
$cgiparams{'RW_NET'} = '';
$cgiparams{'DPD_DELAY'} = '30';
$cgiparams{'DPD_TIMEOUT'} = '120';
$cgiparams{'FORCE_MOBIKE'} = 'off';
$cgiparams{'START_ACTION'} = 'start';
$cgiparams{'INACTIVITY_TIMEOUT'} = 900;
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
###
### Just return true is one interface is vpn enabled
###
sub vpnenabled {
	return ($vpnsettings{'ENABLED'} eq 'on');
}
###
### old version: maintain serial number to one, without explication.
### this: let the counter go, so that each cert is numbered.
###
sub cleanssldatabase {
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
sub newcleanssldatabase {
	if (! -s "${General::swroot}/certs/serial" ) {
		open(FILE, ">${General::swroot}/certs/serial");
		print FILE "01";
		close FILE;
	}
	if (! -s ">${General::swroot}/certs/index.txt") {
		system ("touch ${General::swroot}/certs/index.txt");
	}
	unlink ("${General::swroot}/certs/index.txt.old");
	unlink ("${General::swroot}/certs/serial.old");
#	unlink ("${General::swroot}/certs/01.pem");		numbering evolves. Wrong place to delete
}

###
### Call openssl and return errormessage if any
###
sub callssl ($) {
	my $opt = shift;
	my $retssl = `/usr/bin/openssl $opt 2>&1`; #redirect stderr
	my $ret = '';
	foreach my $line (split (/\n/, $retssl)) {
		&General::log("ipsec", "$line") if (0); # 1 for verbose logging
		$ret .= '<br>'.$line if ( $line =~ /error|unknown/ );
	}
	if ($ret) {
		$ret= &Header::cleanhtml($ret);
	}
	return $ret ? "$Lang::tr{'openssl produced an error'}: $ret" : '' ;
}
###
### Obtain a CN from given cert
###
sub getCNfromcert ($) {
	#&General::log("ipsec", "Extracting name from $_[0]...");
	my $temp = `/usr/bin/openssl x509 -text -in $_[0]`;
	$temp =~ /Subject:.*CN = (.*)[\n]/;
	$temp = $1;
	$temp =~ s+/Email+, E+;
	$temp =~ s/ ST = / S = /;
	$temp =~ s/,//g;
	$temp =~ s/\'//g;
	return $temp;
}
###
### Obtain Subject from given cert
###
sub getsubjectfromcert ($) {
	#&General::log("ipsec", "Extracting subject from $_[0]...");
	my $temp = `/usr/bin/openssl x509 -text -in $_[0]`;
	$temp =~ /Subject: (.*)[\n]/;
	$temp = $1;
	$temp =~ s+/Email+, E+;
	$temp =~ s/ ST = / S = /;
	return $temp;
}
###
### Combine local subnet and connection name to make a unique name for each connection section
### (this sub is not used now)
###
sub makeconnname ($) {
	my $conn = shift;
	my $subnet = shift;

	$subnet =~ /^(.*?)\/(.*?)$/; # $1=IP $2=mask
	my $ip = unpack('N', &Socket::inet_aton($1));
	if (length ($2) > 2) {
		my $mm = unpack('N', &Socket::inet_aton($2));
		while ( ($mm & 1)==0 ) {
			$ip >>= 1;
			$mm >>= 1;
		};
	} else {
		$ip >>= (32 - $2);
	}
	return sprintf ("%s-%X", $conn, $ip);
}
###
### Write a config file.
###
###Type=Host : GUI can choose the interface used (RED,GREEN,BLUE) and
###		the side is always defined as 'left'.
###

sub writeipsecfiles {
	my %lconfighash = ();
	my %lvpnsettings = ();
	&General::readhasharray("${General::swroot}/vpn/config", \%lconfighash);
	&General::readhash("${General::swroot}/vpn/settings", \%lvpnsettings);

	open(CONF, ">${General::swroot}/vpn/ipsec.conf") or die "Unable to open ${General::swroot}/vpn/ipsec.conf: $!";
	open(SECRETS, ">${General::swroot}/vpn/ipsec.secrets") or die "Unable to open ${General::swroot}/vpn/ipsec.secrets: $!";
	flock CONF, 2;
	flock SECRETS, 2;
	print CONF "version 2\n\n";
	print CONF "conn %default\n";
	print CONF "\tkeyingtries=%forever\n";
	print CONF "\n";

	# Add user includes to config file
	if (-e "/etc/ipsec.user.conf") {
		print CONF "include /etc/ipsec.user.conf\n";
		print CONF "\n";
	}

	print SECRETS "include /etc/ipsec.user.secrets\n";

	if (-f "${General::swroot}/certs/hostkey.pem") {
		print SECRETS ": RSA ${General::swroot}/certs/hostkey.pem\n"
	}
	my $last_secrets = ''; # old the less specifics connections

	foreach my $key (keys %lconfighash) {
		next if ($lconfighash{$key}[0] ne 'on');

		#remote peer is not set? => use '%any'
		$lconfighash{$key}[10] = '%any' if ($lconfighash{$key}[10] eq '');

		my $localside;
		if ($lconfighash{$key}[26] eq 'BLUE') {
			$localside = $netsettings{'BLUE_ADDRESS'};
		} elsif ($lconfighash{$key}[26] eq 'GREEN') {
			$localside = $netsettings{'GREEN_ADDRESS'};
		} elsif ($lconfighash{$key}[26] eq 'ORANGE') {
			$localside = $netsettings{'ORANGE_ADDRESS'};
		} else { # it is RED
			$localside = $lvpnsettings{'VPN_IP'};
		}

		print CONF "conn $lconfighash{$key}[1]\n";
		print CONF "\tleft=$localside\n";
		print CONF "\tleftsubnet=" . &make_subnets($lconfighash{$key}[8]) . "\n";
		print CONF "\tleftfirewall=yes\n";
		print CONF "\tlefthostaccess=yes\n";
		print CONF "\tright=$lconfighash{$key}[10]\n";

		if ($lconfighash{$key}[3] eq 'net') {
			print CONF "\trightsubnet=" . &make_subnets($lconfighash{$key}[11]) . "\n";
		}

		# Local Cert and Remote Cert (unless auth is DN dn-auth)
		if ($lconfighash{$key}[4] eq 'cert') {
			print CONF "\tleftcert=${General::swroot}/certs/hostcert.pem\n";
			print CONF "\trightcert=${General::swroot}/certs/$lconfighash{$key}[1]cert.pem\n" if ($lconfighash{$key}[2] ne '%auth-dn');
		}

		# Local and Remote IDs
		print CONF "\tleftid=\"$lconfighash{$key}[7]\"\n" if ($lconfighash{$key}[7]);
		print CONF "\trightid=\"$lconfighash{$key}[9]\"\n" if ($lconfighash{$key}[9]);

		# Is PFS enabled?
		my $pfs = $lconfighash{$key}[28] eq 'on' ? 'on' : 'off';

		# Algorithms
		if ($lconfighash{$key}[18] && $lconfighash{$key}[19] && $lconfighash{$key}[20]) {
			my @encs	= split('\|', $lconfighash{$key}[18]);
			my @ints	= split('\|', $lconfighash{$key}[19]);
			my @groups	= split('\|', $lconfighash{$key}[20]);

			my @algos = &make_algos("ike", \@encs, \@ints, \@groups, 1);
			print CONF "\tike=" . join(",", @algos);

			if ($lconfighash{$key}[24] eq 'on') { #only proposed algorythms?
				print CONF "!\n";
			} else {
				print CONF "\n";
			}
		}

		if ($lconfighash{$key}[21] && $lconfighash{$key}[22]) {
			my @encs	= split('\|', $lconfighash{$key}[21]);
			my @ints	= split('\|', $lconfighash{$key}[22]);
			my @groups	= split('\|', $lconfighash{$key}[23]);

			# Use IKE grouptype if no ESP group type has been selected
			# (for backwards compatibility)
			if ($lconfighash{$key}[23] eq "") {
				@groups = split('\|', $lconfighash{$key}[20]);
			}

			my @algos = &make_algos("esp", \@encs, \@ints, \@groups, ($pfs eq "on"));
			print CONF "\tesp=" . join(",", @algos);

			if ($lconfighash{$key}[24] eq 'on') { #only proposed algorythms?
				print CONF "!\n";
			} else {
				print CONF "\n";
			}
		}

		# IKE V1 or V2
		if (! $lconfighash{$key}[29]) {
			$lconfighash{$key}[29] = "ikev1";
		}

		print CONF "\tkeyexchange=$lconfighash{$key}[29]\n";

		# Lifetimes
		print CONF "\tikelifetime=$lconfighash{$key}[16]h\n" if ($lconfighash{$key}[16]);
		print CONF "\tkeylife=$lconfighash{$key}[17]h\n" if ($lconfighash{$key}[17]);

		# Compression
		print CONF "\tcompress=yes\n" if ($lconfighash{$key}[13] eq 'on');

		# Force MOBIKE?
		if (($lconfighash{$key}[29] eq "ikev2") && ($lconfighash{$key}[32] eq 'on')) {
			print CONF "\tmobike=yes\n";
		}

		# Dead Peer Detection
		my $dpdaction = $lconfighash{$key}[27];
		print CONF "\tdpdaction=$dpdaction\n";

		# If the dead peer detection is disabled and IKEv2 is used,
		# dpddelay must be set to zero, too.
		if ($dpdaction eq "none") {
			if ($lconfighash{$key}[29] eq "ikev2") {
				print CONF "\tdpddelay=0\n";
			}
		} else {
			my $dpddelay = $lconfighash{$key}[31];
			if (!$dpddelay) {
				$dpddelay = 30;
			}
			print CONF "\tdpddelay=$dpddelay\n";
			my $dpdtimeout = $lconfighash{$key}[30];
			if (!$dpdtimeout) {
				$dpdtimeout = 120;
			}
			print CONF "\tdpdtimeout=$dpdtimeout\n";
		}

		# Build Authentication details: LEFTid RIGHTid : PSK psk
		my $psk_line;
		if ($lconfighash{$key}[4] eq 'psk') {
			$psk_line = ($lconfighash{$key}[7] ? $lconfighash{$key}[7] : $localside) . " " ;
			$psk_line .= $lconfighash{$key}[9] ? $lconfighash{$key}[9] : $lconfighash{$key}[10]; #remoteid or remote address?
			$psk_line .= " : PSK '$lconfighash{$key}[5]'\n";
			# if the line contains %any, it is less specific than two IP or ID, so move it at end of file.
			if ($psk_line =~ /%any/) {
				$last_secrets .= $psk_line;
			} else {
				print SECRETS $psk_line;
			}
			print CONF "\tauthby=secret\n";
		} else {
			print CONF "\tauthby=rsasig\n";
			print CONF "\tleftrsasigkey=%cert\n";
			print CONF "\trightrsasigkey=%cert\n";
		}

		my $start_action = $lconfighash{$key}[33];
		if (!$start_action) {
			$start_action = "start";
		}

		my $inactivity_timeout = $lconfighash{$key}[34];
		if ($inactivity_timeout eq "") {
			$inactivity_timeout = 900;
		}

		# Automatically start only if a net-to-net connection
		if ($lconfighash{$key}[3] eq 'host') {
			print CONF "\tauto=add\n";
			print CONF "\trightsourceip=$lvpnsettings{'RW_NET'}\n";
		} else {
			print CONF "\tauto=$start_action\n";

			# If in on-demand mode, we terminate the tunnel
			# after 15 min of no traffic
			if ($start_action eq 'route' && $inactivity_timeout > 0) {
				print CONF "\tinactivity=$inactivity_timeout\n";
			}
		}

		# Fragmentation
		print CONF "\tfragmentation=yes\n";

		print CONF "\n";
	} #foreach key

	# Add post user includes to config file
	# After the GUI-connections allows to patch connections.
	if (-e "/etc/ipsec.user-post.conf") {
		print CONF "include /etc/ipsec.user-post.conf\n";
		print CONF "\n";
	}

	print SECRETS $last_secrets if ($last_secrets);
	close(CONF);
	close(SECRETS);
}

# Hook to regenerate the configuration files.
if ($ENV{"REMOTE_ADDR"} eq "") {
	writeipsecfiles();
	exit(0);
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

	if ( $cgiparams{'RW_NET'} ne '' and !&General::validipandmask($cgiparams{'RW_NET'}) ) {
		$errormessage = $Lang::tr{'urlfilter invalid ip or mask error'};
		goto SAVE_ERROR;
	}

	$vpnsettings{'ENABLED'} = $cgiparams{'ENABLED'};
	$vpnsettings{'VPN_IP'} = $cgiparams{'VPN_IP'};
	$vpnsettings{'VPN_DELAYED_START'} = $cgiparams{'VPN_DELAYED_START'};
	$vpnsettings{'RW_NET'} = $cgiparams{'RW_NET'};
	&General::writehash("${General::swroot}/vpn/settings", \%vpnsettings);
	&writeipsecfiles();
	if (&vpnenabled) {
		system('/usr/local/bin/ipsecctrl', 'S');
	} else {
		system('/usr/local/bin/ipsecctrl', 'D');
	}
	sleep $sleepDelay;
	SAVE_ERROR:
###
### Reset all step 2
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'remove x509'} && $cgiparams{'AREUSURE'} eq 'yes') {
	&General::readhasharray("${General::swroot}/vpn/config", \%confighash);

	foreach my $key (keys %confighash) {
		if ($confighash{$key}[4] eq 'cert') {
			delete $confighash{$key};
		}
	}
	while (my $file = glob("${General::swroot}/{ca,certs,crls,private}/*")) {
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
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'remove x509'}) {
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'ipsec'}, 1, '');
	&Header::openbigbox('100%', 'left', '', '');
	&Header::openbox('100%', 'left', $Lang::tr{'are you sure'});
	print <<END
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='100%'>
			<tr>
				<td align='center'>
					<input type='hidden' name='AREUSURE' value='yes' />
					<b><font color='${Header::colourred}'>$Lang::tr{'capswarning'}</font></b>:&nbsp;$Lang::tr{'resetting the vpn configuration will remove the root ca, the host certificate and all certificate based connections'}
				</td>
			</tr><tr>
				<td align='center'>
					<input type='submit' name='ACTION' value='$Lang::tr{'remove x509'}' />
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

	my $key = &General::findhasharraykey (\%cahash);
	$cahash{$key}[0] = $cgiparams{'CA_NAME'};
	$cahash{$key}[1] = &Header::cleanhtml(getsubjectfromcert ("${General::swroot}/ca/$cgiparams{'CA_NAME'}cert.pem"));
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
		&Header::openpage($Lang::tr{'ipsec'}, 1, '');
		&Header::openbigbox('100%', 'left', '', '');
		&Header::openbox('100%', 'left', "$Lang::tr{'ca certificate'}:");
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
### Export ca certificate to browser
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'download ca certificate'}) {
	&General::readhasharray("${General::swroot}/vpn/caconfig", \%cahash);

	if ( -f "${General::swroot}/ca/$cahash{$cgiparams{'KEY'}}[0]cert.pem" ) {
		print "Content-Type: application/force-download\n";
		print "Content-Type: application/octet-stream\r\n";
		print "Content-Disposition: attachment; filename=$cahash{$cgiparams{'KEY'}}[0]cert.pem\r\n\r\n";
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
				system('/usr/local/bin/ipsecctrl', 'D', $key) if (&vpnenabled);
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
			&Header::openpage($Lang::tr{'ipsec'}, 1, '');
			&Header::openbigbox('100%', 'left', '', '');
			&Header::openbox('100%', 'left', $Lang::tr{'are you sure'});
			print <<END
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
				<table width='100%'>
					<tr>
						<td align='center'>
							<input type='hidden' name='KEY' value='$cgiparams{'KEY'}' />
			<input type='hidden' name='AREUSURE' value='yes' /></td>
					</tr><tr>
						<td align='center'>
							<b><font color='${Header::colourred}'>$Lang::tr{'capswarning'}</font></b>&nbsp;$Lang::tr{'connections are associated with this ca.  deleting the ca will delete these connections as well.'}</td>
					</tr><tr>
						<td align='center'>
							<input type='submit' name='ACTION' value='$Lang::tr{'remove ca certificate'}' />
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
	&Header::openpage($Lang::tr{'ipsec'}, 1, '');
	&Header::openbigbox('100%', 'left', '', '');
	if ($cgiparams{'ACTION'} eq $Lang::tr{'show root certificate'}) {
		&Header::openbox('100%', 'left', "$Lang::tr{'root certificate'}:");
		$output = `/usr/bin/openssl x509 -text -in ${General::swroot}/ca/cacert.pem`;
	} else {
		&Header::openbox('100%', 'left', "$Lang::tr{'host certificate'}:");
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
### Export root certificate to browser
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'download root certificate'}) {
	if ( -f "${General::swroot}/ca/cacert.pem" ) {
		print "Content-Type: application/force-download\n";
		print "Content-Disposition: attachment; filename=cacert.pem\r\n\r\n";
		print `/usr/bin/openssl x509 -in ${General::swroot}/ca/cacert.pem`;
		exit(0);
	}
###
### Export host certificate to browser
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'download host certificate'}) {
	if ( -f "${General::swroot}/certs/hostcert.pem" ) {
		print "Content-Type: application/force-download\n";
		print "Content-Disposition: attachment; filename=hostcert.pem\r\n\r\n";
		print `/usr/bin/openssl x509 -in ${General::swroot}/certs/hostcert.pem`;
		exit(0);
	}
###
### Form for generating/importing the caroot+host certificate
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'generate root/host certificates'} ||
	$cgiparams{'ACTION'} eq $Lang::tr{'upload p12 file'}) {

	if (-f "${General::swroot}/ca/cacert.pem") {
		$errormessage = $Lang::tr{'valid root certificate already exists'};
		goto ROOTCERT_SKIP;
	}

	&General::readhash("${General::swroot}/vpn/settings", \%vpnsettings);
	# fill in initial values
	if ($cgiparams{'ROOTCERT_HOSTNAME'} eq '') {
		if (-e "${General::swroot}/red/active" && open(IPADDR, "${General::swroot}/red/local-ipaddress")) {
			my $ipaddr = <IPADDR>;
			close IPADDR;
			chomp ($ipaddr);
			$cgiparams{'ROOTCERT_HOSTNAME'} = (gethostbyaddr(pack("C4", split(/\./, $ipaddr)), 2))[0];
			if ($cgiparams{'ROOTCERT_HOSTNAME'} eq '') {
				$cgiparams{'ROOTCERT_HOSTNAME'} = $ipaddr;
			}
		}
		$cgiparams{'ROOTCERT_COUNTRY'} = $vpnsettings{'ROOTCERT_COUNTRY'} if (!$cgiparams{'ROOTCERT_COUNTRY'});
	} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'upload p12 file'}) {
		&General::log("ipsec", "Importing from p12...");

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

		# Extract the CA certificate from the file
		&General::log("ipsec", "Extracting caroot from p12...");
		if (open(STDIN, "-|")) {
			my $opt = " pkcs12 -cacerts -nokeys";
			$opt .= " -in $filename";
			$opt .= " -out /tmp/newcacert";
			$errormessage = &callssl ($opt);
		} else { #child
			print "$cgiparams{'P12_PASS'}\n";
			exit (0);
		}

		# Extract the Host certificate from the file
		if (!$errormessage) {
			&General::log("ipsec", "Extracting host cert from p12...");
			if (open(STDIN, "-|")) {
				my $opt = " pkcs12 -clcerts -nokeys";
				$opt .= " -in $filename";
				$opt .= " -out /tmp/newhostcert";
				$errormessage = &callssl ($opt);
			} else { #child
				print "$cgiparams{'P12_PASS'}\n";
				exit (0);
			}
		}

		# Extract the Host key from the file
		if (!$errormessage) {
			&General::log("ipsec", "Extracting private key from p12...");
			if (open(STDIN, "-|")) {
				my $opt = " pkcs12 -nocerts -nodes";
				$opt .= " -in $filename";
				$opt .= " -out /tmp/newhostkey";
				$errormessage = &callssl ($opt);
			} else { #child
				print "$cgiparams{'P12_PASS'}\n";
				exit (0);
			}
		}

		if (!$errormessage) {
			&General::log("ipsec", "Moving cacert...");
			move("/tmp/newcacert", "${General::swroot}/ca/cacert.pem");
			$errormessage = "$Lang::tr{'certificate file move failed'}: $!" if ($? ne 0);
		}

		if (!$errormessage) {
			&General::log("ipsec", "Moving host cert...");
			move("/tmp/newhostcert", "${General::swroot}/certs/hostcert.pem");
			$errormessage = "$Lang::tr{'certificate file move failed'}: $!" if ($? ne 0);
		}

		if (!$errormessage) {
			&General::log("ipsec", "Moving private key...");
			move("/tmp/newhostkey", "${General::swroot}/certs/hostkey.pem");
			$errormessage = "$Lang::tr{'certificate file move failed'}: $!" if ($? ne 0);
		}

		#cleanup temp files
		unlink ($filename);
		unlink ('/tmp/newcacert');
		unlink ('/tmp/newhostcert');
		unlink ('/tmp/newhostkey');
		if ($errormessage) {
			unlink ("${General::swroot}/ca/cacert.pem");
			unlink ("${General::swroot}/certs/hostcert.pem");
			unlink ("${General::swroot}/certs/hostkey.pem");
			goto ROOTCERT_ERROR;
		}

		# Create empty CRL cannot be done because we don't have
		# the private key for this CAROOT
		# IPFire can only import certificates

		&General::log("ipsec", "p12 import completed!");
		&cleanssldatabase();
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
		#the exact syntax is a list comma separated of
		#	email:any-validemail
		#	URI: a uniform resource indicator
		#	DNS: a DNS domain name
		#	RID: a registered OBJECT IDENTIFIER
		#	IP: an IP address
		# example: email:franck@foo.com,IP:10.0.0.10,DNS:franck.foo.com

		if ($cgiparams{'SUBJECTALTNAME'} ne '' && $cgiparams{'SUBJECTALTNAME'} !~ /^(email|URI|DNS|RID|IP):[a-zA-Z0-9 :\/,\.\-_@]*$/) {
			$errormessage = $Lang::tr{'vpn altname syntax'};
			goto VPNCONF_ERROR;
		}

		# Copy the cgisettings to vpnsettings and save the configfile
		$vpnsettings{'ROOTCERT_ORGANIZATION'}	= $cgiparams{'ROOTCERT_ORGANIZATION'};
		$vpnsettings{'ROOTCERT_HOSTNAME'}		= $cgiparams{'ROOTCERT_HOSTNAME'};
		$vpnsettings{'ROOTCERT_EMAIL'}			= $cgiparams{'ROOTCERT_EMAIL'};
		$vpnsettings{'ROOTCERT_OU'}				= $cgiparams{'ROOTCERT_OU'};
		$vpnsettings{'ROOTCERT_CITY'}			= $cgiparams{'ROOTCERT_CITY'};
		$vpnsettings{'ROOTCERT_STATE'}			= $cgiparams{'ROOTCERT_STATE'};
		$vpnsettings{'ROOTCERT_COUNTRY'}		= $cgiparams{'ROOTCERT_COUNTRY'};
		&General::writehash("${General::swroot}/vpn/settings", \%vpnsettings);

		# Replace empty strings with a .
		(my $ou = $cgiparams{'ROOTCERT_OU'}) =~ s/^\s*$/\./;
		(my $city = $cgiparams{'ROOTCERT_CITY'}) =~ s/^\s*$/\./;
		(my $state = $cgiparams{'ROOTCERT_STATE'}) =~ s/^\s*$/\./;

		# Create the CA certificate
		if (!$errormessage) {
			&General::log("ipsec", "Creating cacert...");
			if (open(STDIN, "-|")) {
				my $opt = " req -x509 -sha256 -nodes";
				$opt .= " -days 999999";
				$opt .= " -newkey rsa:4096";
				$opt .= " -keyout ${General::swroot}/private/cakey.pem";
				$opt .= " -out ${General::swroot}/ca/cacert.pem";

				$errormessage = &callssl ($opt);
			} else { #child
				print "$cgiparams{'ROOTCERT_COUNTRY'}\n";
				print "$state\n";
				print "$city\n";
				print "$cgiparams{'ROOTCERT_ORGANIZATION'}\n";
				print "$ou\n";
				print "$cgiparams{'ROOTCERT_ORGANIZATION'} CA\n";
				print "$cgiparams{'ROOTCERT_EMAIL'}\n";
				exit (0);
			}
		}

		# Create the Host certificate request
		if (!$errormessage) {
			&General::log("ipsec", "Creating host cert...");
			if (open(STDIN, "-|")) {
				my $opt = " req -sha256 -nodes";
				$opt .= " -newkey rsa:2048";
				$opt .= " -keyout ${General::swroot}/certs/hostkey.pem";
				$opt .= " -out ${General::swroot}/certs/hostreq.pem";
				$errormessage = &callssl ($opt);
			} else { #child
				print "$cgiparams{'ROOTCERT_COUNTRY'}\n";
				print "$state\n";
				print "$city\n";
				print "$cgiparams{'ROOTCERT_ORGANIZATION'}\n";
				print "$ou\n";
				print "$cgiparams{'ROOTCERT_HOSTNAME'}\n";
				print "$cgiparams{'ROOTCERT_EMAIL'}\n";
				print ".\n";
				print ".\n";
				exit (0);
			}
		}

		# Sign the host certificate request
		if (!$errormessage) {
			&General::log("ipsec", "Self signing host cert...");

			#No easy way for specifying the contain of subjectAltName without writing a config file...
			my ($fh, $v3extname) = tempfile ('/tmp/XXXXXXXX');
			print $fh <<END
			basicConstraints=CA:FALSE
			nsComment="OpenSSL Generated Certificate"
			subjectKeyIdentifier=hash
			authorityKeyIdentifier=keyid,issuer:always
			extendedKeyUsage = serverAuth
END
;
			print $fh "subjectAltName=$cgiparams{'SUBJECTALTNAME'}" if ($cgiparams{'SUBJECTALTNAME'});
			close ($fh);

			my $opt = " ca -md sha256 -days 999999";
			$opt .= " -batch -notext";
			$opt .= " -in ${General::swroot}/certs/hostreq.pem";
			$opt .= " -out ${General::swroot}/certs/hostcert.pem";
			$opt .= " -extfile $v3extname";
			$errormessage = &callssl ($opt);
			unlink ("${General::swroot}/certs/hostreq.pem"); #no more needed
			unlink ($v3extname);
		}

		# Create an empty CRL
		if (!$errormessage) {
			&General::log("ipsec", "Creating emptycrl...");
			my $opt = " ca -gencrl";
			$opt .= " -out ${General::swroot}/crls/cacrl.pem";
			$errormessage = &callssl ($opt);
		}

		# Successfully build CA / CERT!
		if (!$errormessage) {
			&cleanssldatabase();
			goto ROOTCERT_SUCCESS;
		}

		#Cleanup
		unlink ("${General::swroot}/ca/cacert.pem");
		unlink ("${General::swroot}/certs/hostkey.pem");
		unlink ("${General::swroot}/certs/hostcert.pem");
		unlink ("${General::swroot}/crls/cacrl.pem");
		&cleanssldatabase();
	}

	ROOTCERT_ERROR:
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'ipsec'}, 1, '');
	&Header::openbigbox('100%', 'left', '', $errormessage);
	if ($errormessage) {
		&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
		print "<class name='base'>$errormessage";
		print "&nbsp;</class>";
		&Header::closebox();
	}
	&Header::openbox('100%', 'left', "$Lang::tr{'generate root/host certificates'}:");
	print <<END
	<form method='post' enctype='multipart/form-data' action='$ENV{'SCRIPT_NAME'}'>
		<table width='100%' border='0' cellspacing='1' cellpadding='0'>
	<tr><td width='40%' class='base'>$Lang::tr{'organization name'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
		<td width='60%' class='base' nowrap='nowrap'><input type='text' name='ROOTCERT_ORGANIZATION' value='$cgiparams{'ROOTCERT_ORGANIZATION'}' size='32' /></td></tr>
	<tr><td class='base'>$Lang::tr{'ipfires hostname'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
		<td class='base' nowrap='nowrap'><input type='text' name='ROOTCERT_HOSTNAME' value='$cgiparams{'ROOTCERT_HOSTNAME'}' size='32' /></td></tr>
	<tr><td class='base'>$Lang::tr{'your e-mail'}:</td>
		<td class='base' nowrap='nowrap'><input type='text' name='ROOTCERT_EMAIL' value='$cgiparams{'ROOTCERT_EMAIL'}' size='32' /></td></tr>
	<tr><td class='base'>$Lang::tr{'your department'}:</td>
		<td class='base' nowrap='nowrap'><input type='text' name='ROOTCERT_OU' value='$cgiparams{'ROOTCERT_OU'}' size='32' /></td></tr>
	<tr><td class='base'>$Lang::tr{'city'}:</td>
		<td class='base' nowrap='nowrap'><input type='text' name='ROOTCERT_CITY' value='$cgiparams{'ROOTCERT_CITY'}' size='32' /></td></tr>
	<tr><td class='base'>$Lang::tr{'state or province'}:</td>
		<td class='base' nowrap='nowrap'><input type='text' name='ROOTCERT_STATE' value='$cgiparams{'ROOTCERT_STATE'}' size='32' /></td></tr>
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
		</select></td></tr>
	<tr><td class='base'>$Lang::tr{'vpn subjectaltname'} (subjectAltName=email:*,URI:*,DNS:*,RID:*)</td>
	<td class='base' nowrap='nowrap'><input type='text' name='SUBJECTALTNAME' value='$cgiparams{'SUBJECTALTNAME'}' size='32' /></td></tr>
	<tr><td>&nbsp;</td>
		<td><br /><input type='submit' name='ACTION' value='$Lang::tr{'generate root/host certificates'}' /><br /><br /></td></tr>
	<tr><td class='base' colspan='2' align='left'>
		<b><font color='${Header::colourred}'>$Lang::tr{'capswarning'}</font></b>:
		$Lang::tr{'generating the root and host certificates may take a long time. it can take up to several minutes on older hardware. please be patient'}
	</td></tr>
	<tr><td colspan='2'><hr></td></tr>
	<tr><td class='base' nowrap='nowrap'>$Lang::tr{'upload p12 file'}:</td>
		<td nowrap='nowrap'><input type='file' name='FH' size='32' /></td></tr>
	<tr><td class='base'>$Lang::tr{'pkcs12 file password'}:</td>
		<td class='base' nowrap='nowrap'><input type='password' name='P12_PASS' value='$cgiparams{'P12_PASS'}' size='32' /></td></tr>
	<tr><td>&nbsp;</td>
		<td><input type='submit' name='ACTION' value='$Lang::tr{'upload p12 file'}' /></td></tr>
	<tr><td class='base' colspan='2' align='left'>
		<img src='/blob.gif' alt='*' />&nbsp;$Lang::tr{'required field'}</td></tr>
	</table></form>
END
;
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit(0);

	ROOTCERT_SUCCESS:
	if (&vpnenabled) {
		system('/usr/local/bin/ipsecctrl', 'S');
		sleep $sleepDelay;
	}
	ROOTCERT_SKIP:
###
### Export PKCS12 file to browser
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'download pkcs12 file'}) {
	&General::readhasharray("${General::swroot}/vpn/config", \%confighash);
	print "Content-Type: application/force-download\n";
	print "Content-Disposition: attachment; filename=" . $confighash{$cgiparams{'KEY'}}[1] . ".p12\r\n";
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
		&Header::openpage($Lang::tr{'ipsec'}, 1, '');
		&Header::openbigbox('100%', 'left', '', '');
		&Header::openbox('100%', 'left', "$Lang::tr{'cert'}:");
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
### Export Certificate to browser
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'download certificate'}) {
	&General::readhasharray("${General::swroot}/vpn/config", \%confighash);

	if ( -f "${General::swroot}/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem") {
		print "Content-Type: application/force-download\n";
		print "Content-Disposition: attachment; filename=" . $confighash{$cgiparams{'KEY'}}[1] . "cert.pem\n\n";
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
			system('/usr/local/bin/ipsecctrl', 'S', $cgiparams{'KEY'}) if (&vpnenabled);
		} else {
			system('/usr/local/bin/ipsecctrl', 'D', $cgiparams{'KEY'}) if (&vpnenabled);
			$confighash{$cgiparams{'KEY'}}[0] = 'off';
			&General::writehasharray("${General::swroot}/vpn/config", \%confighash);
			&writeipsecfiles();
		}
		sleep $sleepDelay;
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
		if (&vpnenabled) {
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
		system('/usr/local/bin/ipsecctrl', 'D', $cgiparams{'KEY'}) if (&vpnenabled);
		unlink ("${General::swroot}/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem");
		unlink ("${General::swroot}/certs/$confighash{$cgiparams{'KEY'}}[1].p12");
		delete $confighash{$cgiparams{'KEY'}};
		&General::writehasharray("${General::swroot}/vpn/config", \%confighash);
		&writeipsecfiles();
	} else {
		$errormessage = $Lang::tr{'invalid key'};
	}
	&General::firewall_reload();
###
### Choose between adding a host-net or net-net connection
###
} elsif ($cgiparams{'ACTION'} eq $Lang::tr{'add'} && $cgiparams{'TYPE'} eq '') {
	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'ipsec'}, 1, '');
	&Header::openbigbox('100%', 'left', '', '');
	&Header::openbox('100%', 'left', $Lang::tr{'connection type'});
	print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<b>$Lang::tr{'connection type'}:</b><br />
		<table>
		<tr><td><input type='radio' name='TYPE' value='host' checked='checked' /></td>
		<td class='base'>$Lang::tr{'host to net vpn'}</td>
		</tr><tr>
		<td><input type='radio' name='TYPE' value='net' /></td>
		<td class='base'>$Lang::tr{'net to net vpn'}</td>
		</tr><tr>
		<td align='center' colspan='2'><input type='submit' name='ACTION' value='$Lang::tr{'add'}' /></td>
		</tr>
		</table></form>
END
;
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit (0);
###
### Adding/Editing/Saving a connection
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
		$cgiparams{'ENABLED'}			= $confighash{$cgiparams{'KEY'}}[0];
		$cgiparams{'NAME'}				= $confighash{$cgiparams{'KEY'}}[1];
		$cgiparams{'TYPE'}				= $confighash{$cgiparams{'KEY'}}[3];
		$cgiparams{'AUTH'}				= $confighash{$cgiparams{'KEY'}}[4];
		$cgiparams{'PSK'}				= $confighash{$cgiparams{'KEY'}}[5];
		#$cgiparams{'free'}				= $confighash{$cgiparams{'KEY'}}[6];
		$cgiparams{'LOCAL_ID'}			= $confighash{$cgiparams{'KEY'}}[7];
		my @local_subnets = split(",", $confighash{$cgiparams{'KEY'}}[8]);
		$cgiparams{'LOCAL_SUBNET'} 		= join(/\|/, @local_subnets);
		$cgiparams{'REMOTE_ID'}			= $confighash{$cgiparams{'KEY'}}[9];
		$cgiparams{'REMOTE'}			= $confighash{$cgiparams{'KEY'}}[10];
		my @remote_subnets = split(",", $confighash{$cgiparams{'KEY'}}[11]);
		$cgiparams{'REMOTE_SUBNET'}		= join(/\|/, @remote_subnets);
		$cgiparams{'REMARK'}			= $confighash{$cgiparams{'KEY'}}[25];
		$cgiparams{'DPD_ACTION'}		= $confighash{$cgiparams{'KEY'}}[27];
		$cgiparams{'IKE_VERSION'}		= $confighash{$cgiparams{'KEY'}}[29];
		$cgiparams{'IKE_ENCRYPTION'}	= $confighash{$cgiparams{'KEY'}}[18];
		$cgiparams{'IKE_INTEGRITY'}		= $confighash{$cgiparams{'KEY'}}[19];
		$cgiparams{'IKE_GROUPTYPE'}		= $confighash{$cgiparams{'KEY'}}[20];
		$cgiparams{'IKE_LIFETIME'}		= $confighash{$cgiparams{'KEY'}}[16];
		$cgiparams{'ESP_ENCRYPTION'}	= $confighash{$cgiparams{'KEY'}}[21];
		$cgiparams{'ESP_INTEGRITY'}		= $confighash{$cgiparams{'KEY'}}[22];
		$cgiparams{'ESP_GROUPTYPE'}		= $confighash{$cgiparams{'KEY'}}[23];
		if ($cgiparams{'ESP_GROUPTYPE'} eq "") {
			$cgiparams{'ESP_GROUPTYPE'}	= $cgiparams{'IKE_GROUPTYPE'};
		}
		$cgiparams{'ESP_KEYLIFE'}		= $confighash{$cgiparams{'KEY'}}[17];
		$cgiparams{'COMPRESSION'}		= $confighash{$cgiparams{'KEY'}}[13];
		$cgiparams{'ONLY_PROPOSED'}		= $confighash{$cgiparams{'KEY'}}[24];
		$cgiparams{'PFS'}				= $confighash{$cgiparams{'KEY'}}[28];
		$cgiparams{'DPD_TIMEOUT'}		= $confighash{$cgiparams{'KEY'}}[30];
		$cgiparams{'DPD_DELAY'}			= $confighash{$cgiparams{'KEY'}}[31];
		$cgiparams{'FORCE_MOBIKE'}		= $confighash{$cgiparams{'KEY'}}[32];
		$cgiparams{'INACTIVITY_TIMEOUT'}	= $confighash{$cgiparams{'KEY'}}[34];

		if (!$cgiparams{'DPD_DELAY'}) {
			$cgiparams{'DPD_DELAY'} = 30;
		}

		if (!$cgiparams{'DPD_TIMEOUT'}) {
			$cgiparams{'DPD_TIMEOUT'} = 120;
		}

		if ($cgiparams{'INACTIVITY_TIMEOUT'} eq "") {
			$cgiparams{'INACTIVITY_TIMEOUT'} = 900;
		}

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
		if (! $cgiparams{'KEY'}) { #only for add
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
			if (($cgiparams{'REMOTE'} ne '%any') && (! &General::validip($cgiparams{'REMOTE'}))) {
				if (! &General::validfqdn ($cgiparams{'REMOTE'})) {
					$errormessage = $Lang::tr{'invalid input for remote host/ip'};
					goto VPNCONF_ERROR;
				} else {
					if (&valid_dns_host($cgiparams{'REMOTE'})) {
						$warnmessage = "$Lang::tr{'check vpn lr'} $cgiparams{'REMOTE'}. $Lang::tr{'dns check failed'}";
					}
				}
			}
		}

		my @local_subnets = split(",", $cgiparams{'LOCAL_SUBNET'});
		foreach my $subnet (@local_subnets) {
			unless (&Network::check_subnet($subnet)) {
				$errormessage = $Lang::tr{'local subnet is invalid'};
				goto VPNCONF_ERROR;
			}
		}

		# Allow only one roadwarrior/psk without remote IP-address
		if ($cgiparams{'REMOTE'} eq '' && $cgiparams{'AUTH'} eq 'psk') {
			foreach my $key (keys %confighash) {
				if ( ($cgiparams{'KEY'} ne $key) &&
					($confighash{$key}[4] eq 'psk') &&
					($confighash{$key}[10] eq '') ) {
					$errormessage = $Lang::tr{'you can only define one roadwarrior connection when using pre-shared key authentication'};
					goto VPNCONF_ERROR;
				}
			}
		}

		if ($cgiparams{'TYPE'} eq 'net') {
			my @remote_subnets = split(",", $cgiparams{'REMOTE_SUBNET'});
			foreach my $subnet (@remote_subnets) {
				unless (&Network::check_subnet($subnet)) {
					$errormessage = $Lang::tr{'remote subnet is invalid'};
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

		# Allow nothing or a string (DN,FDQN,) beginning with @
		# with no comma but slashes between RID eg @O=FR/C=Paris/OU=myhome/CN=franck
		if ( ($cgiparams{'LOCAL_ID'} !~ /^(|[\w.-]*@[\w. =*\/-]+|\d+\.\d+\.\d+\.\d+)$/) ||
			($cgiparams{'REMOTE_ID'} !~ /^(|[\w.-]*@[\w. =*\/-]+|\d+\.\d+\.\d+\.\d+)$/) ||
			(($cgiparams{'REMOTE_ID'} eq $cgiparams{'LOCAL_ID'}) && ($cgiparams{'LOCAL_ID'} ne ''))
		) {
			$errormessage = $Lang::tr{'invalid local-remote id'} . '<br />' .
			'DER_ASN1_DN: @c=FR/ou=Paris/ou=Home/cn=*<br />' .
			'FQDN: @ipfire.org<br />' .
			'USER_FQDN: info@ipfire.org<br />' .
			'IPV4_ADDR: 123.123.123.123';
			goto VPNCONF_ERROR;
		}
		# If Auth is DN, verify existance of Remote ID.
		if ( $cgiparams{'REMOTE_ID'} eq '' && (
			$cgiparams{'AUTH'} eq 'auth-dn'|| # while creation
			$confighash{$cgiparams{'KEY'}}[2] eq '%auth-dn')){ # while editing
				$errormessage = $Lang::tr{'vpn missing remote id'};
				goto VPNCONF_ERROR;
		}

		if ($cgiparams{'TYPE'} eq 'net'){
			$warnmessage=&General::checksubnets('',$cgiparams{'REMOTE_SUBNET'},'ipsec');
			if ($warnmessage ne ''){
				$warnmessage=$Lang::tr{'remote subnet'}." ($cgiparams{'REMOTE_SUBNET'}) <br>".$warnmessage;
			}
		}

		if ($cgiparams{'AUTH'} eq 'psk') {
			if (! length($cgiparams{'PSK'}) ) {
				$errormessage = $Lang::tr{'pre-shared key is too short'};
				goto VPNCONF_ERROR;
			}
			if ($cgiparams{'PSK'} =~ /'/) {
				$cgiparams{'PSK'} =~ tr/'/ /;
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

		# Sign the certificate request
		&General::log("ipsec", "Signing your cert $cgiparams{'NAME'}...");
		my $opt = " ca -md sha256 -days 999999";
		$opt .= " -batch -notext";
		$opt .= " -in $filename";
		$opt .= " -out ${General::swroot}/certs/$cgiparams{'NAME'}cert.pem";

		if ( $errormessage = &callssl ($opt) ) {
			unlink ($filename);
			unlink ("${General::swroot}/certs/$cgiparams{'NAME'}cert.pem");
			&cleanssldatabase();
			goto VPNCONF_ERROR;
		} else {
			unlink ($filename);
			&cleanssldatabase();
		}

		$cgiparams{'CERT_NAME'} = getCNfromcert ("${General::swroot}/certs/$cgiparams{'NAME'}cert.pem");
		if ($cgiparams{'CERT_NAME'} eq '') {
			$errormessage = $Lang::tr{'could not retrieve common name from certificate'};
			goto VPNCONF_ERROR;
		}
	} elsif ($cgiparams{'AUTH'} eq 'pkcs12') {
		&General::log("ipsec", "Importing from p12...");

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

		# Extract the CA certificate from the file
		&General::log("ipsec", "Extracting caroot from p12...");
		if (open(STDIN, "-|")) {
			my $opt = " pkcs12 -cacerts -nokeys";
			$opt .= " -in $filename";
			$opt .= " -out /tmp/newcacert";
			$errormessage = &callssl ($opt);
		} else { #child
			print "$cgiparams{'P12_PASS'}\n";
			exit (0);
		}

		# Extract the Host certificate from the file
		if (!$errormessage) {
			&General::log("ipsec", "Extracting host cert from p12...");
			if (open(STDIN, "-|")) {
				my $opt = " pkcs12 -clcerts -nokeys";
				$opt .= " -in $filename";
				$opt .= " -out /tmp/newhostcert";
				$errormessage = &callssl ($opt);
			} else { #child
				print "$cgiparams{'P12_PASS'}\n";
				exit (0);
			}
		}

		if (!$errormessage) {
			&General::log("ipsec", "Moving cacert...");
			#If CA have new subject, add it to our list of CA
			my $casubject = &Header::cleanhtml(getsubjectfromcert ('/tmp/newcacert'));
			my @names;
			foreach my $x (keys %cahash) {
				$casubject='' if ($cahash{$x}[1] eq $casubject);
				unshift (@names,$cahash{$x}[0]);
			}
			if ($casubject) { # a new one!
				my $temp = `/usr/bin/openssl x509 -text -in /tmp/newcacert`;
				if ($temp !~ /CA:TRUE/i) {
					$errormessage = $Lang::tr{'not a valid ca certificate'};
				} else {
					#compute a name for it
					my $idx=0;
					while (grep(/Imported-$idx/, @names) ) {$idx++};
					$cgiparams{'CA_NAME'}="Imported-$idx";
					$cgiparams{'CERT_NAME'}=&Header::cleanhtml(getCNfromcert ('/tmp/newhostcert'));
					move("/tmp/newcacert", "${General::swroot}/ca/$cgiparams{'CA_NAME'}cert.pem");
					$errormessage = "$Lang::tr{'certificate file move failed'}: $!" if ($? ne 0);
					if (!$errormessage) {
						my $key = &General::findhasharraykey (\%cahash);
						$cahash{$key}[0] = $cgiparams{'CA_NAME'};
						$cahash{$key}[1] = $casubject;
						&General::writehasharray("${General::swroot}/vpn/caconfig", \%cahash);
						system('/usr/local/bin/ipsecctrl', 'R');
					}
				}
			}
		}
		if (!$errormessage) {
			&General::log("ipsec", "Moving host cert...");
			move("/tmp/newhostcert", "${General::swroot}/certs/$cgiparams{'NAME'}cert.pem");
			$errormessage = "$Lang::tr{'certificate file move failed'}: $!" if ($? ne 0);
		}

		#cleanup temp files
		unlink ($filename);
		unlink ('/tmp/newcacert');
		unlink ('/tmp/newhostcert');
		if ($errormessage) {
			unlink ("${General::swroot}/ca/$cgiparams{'CA_NAME'}cert.pem");
			unlink ("${General::swroot}/certs/$cgiparams{'NAME'}cert.pem");
			goto VPNCONF_ERROR;
		}
		&General::log("ipsec", "p12 import completed!");
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
		&General::log("ipsec", "Validating imported cert against our known CA...");
		my $validca = 1; #assume ok
		my $test = `/usr/bin/openssl verify -CAfile ${General::swroot}/ca/cacert.pem $filename`;
		if ($test !~ /: OK/) {
			my $validca = 0;
			foreach my $key (keys %cahash) {
				$test = `/usr/bin/openssl verify -CAfile ${General::swroot}/ca/$cahash{$key}[0]cert.pem $filename`;
				if ($test =~ /: OK/) {
					$validca = 1;
					last;
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

		$cgiparams{'CERT_NAME'} = getCNfromcert ("${General::swroot}/certs/$cgiparams{'NAME'}cert.pem");
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
		#the exact syntax is a list comma separated of
		#	email:any-validemail
		#	URI: a uniform resource indicator
		#	DNS: a DNS domain name
		#	RID: a registered OBJECT IDENTIFIER
		#	IP: an IP address
		# example: email:franck@foo.com,IP:10.0.0.10,DNS:franck.foo.com

		if ($cgiparams{'SUBJECTALTNAME'} ne '' && $cgiparams{'SUBJECTALTNAME'} !~ /^(email|URI|DNS|RID|IP):[a-zA-Z0-9 :\/,\.\-_@]*$/) {
			$errormessage = $Lang::tr{'vpn altname syntax'};
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

		# Create the Client certificate request
		&General::log("ipsec", "Creating a cert...");

		if (open(STDIN, "-|")) {
			my $opt = " req -nodes -rand /proc/interrupts:/proc/net/rt_cache";
			$opt .= " -newkey rsa:2048";
			$opt .= " -keyout ${General::swroot}/certs/$cgiparams{'NAME'}key.pem";
			$opt .= " -out ${General::swroot}/certs/$cgiparams{'NAME'}req.pem";

			if ( $errormessage = &callssl ($opt) ) {
				unlink ("${General::swroot}/certs/$cgiparams{'NAME'}key.pem");
				unlink ("${General::swroot}/certs/$cgiparams{'NAME'}req.pem");
				goto VPNCONF_ERROR;
			}
		} else { #child
			print "$cgiparams{'CERT_COUNTRY'}\n";
			print "$state\n";
			print "$city\n";
			print "$cgiparams{'CERT_ORGANIZATION'}\n";
			print "$ou\n";
			print "$cgiparams{'CERT_NAME'}\n";
			print "$cgiparams{'CERT_EMAIL'}\n";
			print ".\n";
			print ".\n";
			exit (0);
		}

		# Sign the client certificate request
		&General::log("ipsec", "Signing the cert $cgiparams{'NAME'}...");

		#No easy way for specifying the contain of subjectAltName without writing a config file...
		my ($fh, $v3extname) = tempfile ('/tmp/XXXXXXXX');
		print $fh <<END
		basicConstraints=CA:FALSE
		nsComment="OpenSSL Generated Certificate"
		subjectKeyIdentifier=hash
		extendedKeyUsage=clientAuth
		authorityKeyIdentifier=keyid,issuer:always
END
;
		print $fh "subjectAltName=$cgiparams{'SUBJECTALTNAME'}" if ($cgiparams{'SUBJECTALTNAME'});
		close ($fh);

		my $opt = " ca -md sha256 -days 999999 -batch -notext";
		$opt .= " -in ${General::swroot}/certs/$cgiparams{'NAME'}req.pem";
		$opt .= " -out ${General::swroot}/certs/$cgiparams{'NAME'}cert.pem";
		$opt .= " -extfile $v3extname";

		if ( $errormessage = &callssl ($opt) ) {
			unlink ($v3extname);
			unlink ("${General::swroot}/certs/$cgiparams{'NAME'}key.pem");
			unlink ("${General::swroot}/certs/$cgiparams{'NAME'}req.pem");
			unlink ("${General::swroot}/certs/$cgiparams{'NAME'}cert.pem");
			&cleanssldatabase();
			goto VPNCONF_ERROR;
		} else {
			unlink ($v3extname);
			unlink ("${General::swroot}/certs/$cgiparams{'NAME'}req.pem");
			&cleanssldatabase();
		}

		# Create the pkcs12 file
		&General::log("ipsec", "Packing a pkcs12 file...");
		$opt = " pkcs12 -export";
		$opt .= " -inkey ${General::swroot}/certs/$cgiparams{'NAME'}key.pem";
		$opt .= " -in ${General::swroot}/certs/$cgiparams{'NAME'}cert.pem";
		$opt .= " -name \"$cgiparams{'NAME'}\"";
		$opt .= " -passout pass:$cgiparams{'CERT_PASS1'}";
		$opt .= " -certfile ${General::swroot}/ca/cacert.pem";
		$opt .= " -caname \"$vpnsettings{'ROOTCERT_ORGANIZATION'} CA\"";
		$opt .= " -out ${General::swroot}/certs/$cgiparams{'NAME'}.p12";

		if ( $errormessage = &callssl ($opt) ) {
			unlink ("${General::swroot}/certs/$cgiparams{'NAME'}key.pem");
			unlink ("${General::swroot}/certs/$cgiparams{'NAME'}cert.pem");
			unlink ("${General::swroot}/certs/$cgiparams{'NAME'}.p12");
			goto VPNCONF_ERROR;
		} else {
			unlink ("${General::swroot}/certs/$cgiparams{'NAME'}key.pem");
		}
	} elsif ($cgiparams{'AUTH'} eq 'cert') {
		;# Nothing, just editing
	} elsif ($cgiparams{'AUTH'} eq 'auth-dn') {
		$cgiparams{'CERT_NAME'} = '%auth-dn'; # a special value saying 'no cert file'
	} else {
		$errormessage = $Lang::tr{'invalid input for authentication method'};
		goto VPNCONF_ERROR;
	}

	# 1)Error message here is not accurate.
	# 2)Test is superfluous, openswan can reference same cert multiple times
	# 3)Present since initial version (1.3.2.11), it isn't a bug correction
	# Check if there is no other entry with this certificate name
	#if ((! $cgiparams{'KEY'}) && ($cgiparams{'AUTH'} ne 'psk') && ($cgiparams{'AUTH'} ne 'auth-dn')) {
	#	foreach my $key (keys %confighash) {
	#	if ($confighash{$key}[2] eq $cgiparams{'CERT_NAME'}) {
	#		$errormessage = $Lang::tr{'a connection with this common name already exists'};
	#		goto VPNCONF_ERROR;
	#	}
	#	}
	#}
		# Save the config

	my $key = $cgiparams{'KEY'};
	if (! $key) {
		$key = &General::findhasharraykey (\%confighash);
		foreach my $i (0 .. 34) { $confighash{$key}[$i] = "";}
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
		my @remote_subnets = split(",", $cgiparams{'REMOTE_SUBNET'});
		$confighash{$key}[11] = join('|', @remote_subnets);
	}
	$confighash{$key}[7] = $cgiparams{'LOCAL_ID'};
	my @local_subnets = split(",", $cgiparams{'LOCAL_SUBNET'});
	$confighash{$key}[8] = join('|', @local_subnets);
	$confighash{$key}[9] = $cgiparams{'REMOTE_ID'};
	$confighash{$key}[10] = $cgiparams{'REMOTE'};
	$confighash{$key}[25] = $cgiparams{'REMARK'};
	$confighash{$key}[26] = ""; # Formerly INTERFACE
	$confighash{$key}[27] = $cgiparams{'DPD_ACTION'};
	$confighash{$key}[29] = $cgiparams{'IKE_VERSION'};

	# don't forget advanced value
	$confighash{$key}[18] = $cgiparams{'IKE_ENCRYPTION'};
	$confighash{$key}[19] = $cgiparams{'IKE_INTEGRITY'};
	$confighash{$key}[20] = $cgiparams{'IKE_GROUPTYPE'};
	$confighash{$key}[16] = $cgiparams{'IKE_LIFETIME'};
	$confighash{$key}[21] = $cgiparams{'ESP_ENCRYPTION'};
	$confighash{$key}[22] = $cgiparams{'ESP_INTEGRITY'};
	$confighash{$key}[23] = $cgiparams{'ESP_GROUPTYPE'};
	$confighash{$key}[17] = $cgiparams{'ESP_KEYLIFE'};
	$confighash{$key}[12] = 'off'; # $cgiparams{'AGGRMODE'};
	$confighash{$key}[13] = $cgiparams{'COMPRESSION'};
	$confighash{$key}[24] = $cgiparams{'ONLY_PROPOSED'};
	$confighash{$key}[28] = $cgiparams{'PFS'};
	$confighash{$key}[30] = $cgiparams{'DPD_TIMEOUT'};
	$confighash{$key}[31] = $cgiparams{'DPD_DELAY'};
	$confighash{$key}[32] = $cgiparams{'FORCE_MOBIKE'};
	$confighash{$key}[34] = $cgiparams{'INACTIVITY_TIMEOUT'};

	# free unused fields!
	$confighash{$key}[6] = 'off';
	$confighash{$key}[15] = 'off';

	&General::writehasharray("${General::swroot}/vpn/config", \%confighash);
	&writeipsecfiles();
	if (&vpnenabled) {
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
	if ( ! -f "${General::swroot}/private/cakey.pem" ) {
		$cgiparams{'AUTH'} = 'psk';
	} elsif ( ! -f "${General::swroot}/ca/cacert.pem") {
		$cgiparams{'AUTH'} = 'certfile';
	} else {
		$cgiparams{'AUTH'} = 'certgen';
	}
	$cgiparams{'LOCAL_SUBNET'}		= "$netsettings{'GREEN_NETADDRESS'}/$netsettings{'GREEN_NETMASK'}";
	$cgiparams{'CERT_EMAIL'}		= $vpnsettings{'ROOTCERT_EMAIL'};
	$cgiparams{'CERT_OU'}			= $vpnsettings{'ROOTCERT_OU'};
	$cgiparams{'CERT_ORGANIZATION'}	= $vpnsettings{'ROOTCERT_ORGANIZATION'};
	$cgiparams{'CERT_CITY'}			= $vpnsettings{'ROOTCERT_CITY'};
	$cgiparams{'CERT_STATE'}		= $vpnsettings{'ROOTCERT_STATE'};
	$cgiparams{'CERT_COUNTRY'}		= $vpnsettings{'ROOTCERT_COUNTRY'};

	# choose appropriate dpd action
	if ($cgiparams{'TYPE'} eq 'host') {
		$cgiparams{'DPD_ACTION'} = 'clear';
	} else {
		$cgiparams{'DPD_ACTION'} = 'restart';
	}

	if (!$cgiparams{'DPD_DELAY'}) {
		$cgiparams{'DPD_DELAY'} = 30;
	}

	if (!$cgiparams{'DPD_TIMEOUT'}) {
		$cgiparams{'DPD_TIMEOUT'} = 120;
	}

	if (!$cgiparams{'FORCE_MOBIKE'}) {
		$cgiparams{'FORCE_MOBIKE'} = 'no';
	}

	# Default IKE Version to v2
	if (!$cgiparams{'IKE_VERSION'}) {
		$cgiparams{'IKE_VERSION'} = 'ikev2';
	}

	# ID are empty
	$cgiparams{'LOCAL_ID'} = '';
	$cgiparams{'REMOTE_ID'} = '';

	#use default advanced value
	$cgiparams{'IKE_ENCRYPTION'}	= 'chacha20poly1305|aes256gcm128|aes256gcm96|aes256gcm64|aes256|aes192gcm128|aes192gcm96|aes192gcm64|aes192|aes128gcm128|aes128gcm96|aes128gcm64|aes128'; #[18];
	$cgiparams{'IKE_INTEGRITY'}		= 'sha2_512|sha2_256'; #[19];
	$cgiparams{'IKE_GROUPTYPE'}		= 'curve25519|4096|3072|2048'; #[20];
	$cgiparams{'IKE_LIFETIME'}		= '3'; #[16];
	$cgiparams{'ESP_ENCRYPTION'}	= 'chacha20poly1305|aes256gcm128|aes256gcm96|aes256gcm64|aes256|aes192gcm128|aes192gcm96|aes192gcm64|aes192|aes128gcm128|aes128gcm96|aes128gcm64|aes128'; #[21];
	$cgiparams{'ESP_INTEGRITY'}		= 'sha2_512|sha2_256'; #[22];
	$cgiparams{'ESP_GROUPTYPE'}		= 'curve25519|4096|3072|2048'; #[23];
	$cgiparams{'ESP_KEYLIFE'}		= '1'; #[17];
	$cgiparams{'COMPRESSION'}		= 'off'; #[13];
	$cgiparams{'ONLY_PROPOSED'}		= 'on'; #[24];
	$cgiparams{'PFS'}				= 'on'; #[28];
	$cgiparams{'INACTIVITY_TIMEOUT'}        = 900;
}

VPNCONF_ERROR:
	$checked{'ENABLED'}{'off'} = '';
	$checked{'ENABLED'}{'on'} = '';
	$checked{'ENABLED'}{$cgiparams{'ENABLED'}} = "checked='checked'";

	$checked{'EDIT_ADVANCED'}{'off'} = '';
	$checked{'EDIT_ADVANCED'}{'on'} = '';
	$checked{'EDIT_ADVANCED'}{$cgiparams{'EDIT_ADVANCED'}} = "checked='checked'";

	$checked{'AUTH'}{'psk'} = '';
	$checked{'AUTH'}{'certreq'} = '';
	$checked{'AUTH'}{'certgen'} = '';
	$checked{'AUTH'}{'certfile'} = '';
	$checked{'AUTH'}{'pkcs12'} = '';
	$checked{'AUTH'}{'auth-dn'} = '';
	$checked{'AUTH'}{$cgiparams{'AUTH'}} = "checked='checked'";

	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'ipsec'}, 1, '');
	&Header::openbigbox('100%', 'left', '', $errormessage);
	if ($errormessage) {
		&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
		print "<class name='base'>$errormessage";
		print "&nbsp;</class>";
		&Header::closebox();
	}

	if ($warnmessage) {
		&Header::openbox('100%', 'left', "$Lang::tr{'warning messages'}:");
		print "<class name='base'>$warnmessage";
		print "&nbsp;</class>";
		&Header::closebox();
	}

	print "<form method='post' enctype='multipart/form-data' action='$ENV{'SCRIPT_NAME'}'>";
	print<<END
	<input type='hidden' name='TYPE' value='$cgiparams{'TYPE'}' />
	<input type='hidden' name='IKE_VERSION' value='$cgiparams{'IKE_VERSION'}' />
	<input type='hidden' name='IKE_ENCRYPTION' value='$cgiparams{'IKE_ENCRYPTION'}' />
	<input type='hidden' name='IKE_INTEGRITY' value='$cgiparams{'IKE_INTEGRITY'}' />
	<input type='hidden' name='IKE_GROUPTYPE' value='$cgiparams{'IKE_GROUPTYPE'}' />
	<input type='hidden' name='IKE_LIFETIME' value='$cgiparams{'IKE_LIFETIME'}' />
	<input type='hidden' name='ESP_ENCRYPTION' value='$cgiparams{'ESP_ENCRYPTION'}' />
	<input type='hidden' name='ESP_INTEGRITY' value='$cgiparams{'ESP_INTEGRITY'}' />
	<input type='hidden' name='ESP_GROUPTYPE' value='$cgiparams{'ESP_GROUPTYPE'}' />
	<input type='hidden' name='ESP_KEYLIFE' value='$cgiparams{'ESP_KEYLIFE'}' />
	<input type='hidden' name='COMPRESSION' value='$cgiparams{'COMPRESSION'}' />
	<input type='hidden' name='ONLY_PROPOSED' value='$cgiparams{'ONLY_PROPOSED'}' />
	<input type='hidden' name='PFS' value='$cgiparams{'PFS'}' />
	<input type='hidden' name='DPD_ACTION' value='$cgiparams{'DPD_ACTION'}' />
	<input type='hidden' name='DPD_DELAY' value='$cgiparams{'DPD_DELAY'}' />
	<input type='hidden' name='DPD_TIMEOUT' value='$cgiparams{'DPD_TIMEOUT'}' />
	<input type='hidden' name='FORCE_MOBIKE' value='$cgiparams{'FORCE_MOBIKE'}' />
END
;
	if ($cgiparams{'KEY'}) {
		print "<input type='hidden' name='KEY' value='$cgiparams{'KEY'}' />";
		print "<input type='hidden' name='NAME' value='$cgiparams{'NAME'}' />";
		print "<input type='hidden' name='AUTH' value='$cgiparams{'AUTH'}' />";
	}

	&Header::openbox('100%', 'left', "$Lang::tr{'connection'}: $cgiparams{'NAME'}");
	print "<table width='100%'>";
	if (!$cgiparams{'KEY'}) {
		print <<EOF;
			<tr>
				<td width='20%'>$Lang::tr{'name'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
				<td width='30%'>
					<input type='text' name='NAME' value='$cgiparams{'NAME'}' size='25' />
				</td>
				<td colspan="2"></td>
			</tr>
EOF
	}

	my $disabled;
	my $blob;
	if ($cgiparams{'TYPE'} eq 'host') {
		$disabled = "disabled='disabled'";
	} elsif ($cgiparams{'TYPE'} eq 'net') {
		$blob = "<img src='/blob.gif' alt='*' />";
	};

	my @local_subnets = split(/\|/, $cgiparams{'LOCAL_SUBNET'});
	my $local_subnets = join(",", @local_subnets);

	my @remote_subnets = split(/\|/, $cgiparams{'REMOTE_SUBNET'});
	my $remote_subnets = join(",", @remote_subnets);

	print <<END
	<tr>
		<td width='20%'>$Lang::tr{'enabled'}</td>
		<td width='30%'>
			<input type='checkbox' name='ENABLED' $checked{'ENABLED'}{'on'} />
		</td>
		<td class='boldbase' nowrap='nowrap' width='20%'>$Lang::tr{'local subnet'}&nbsp;<img src='/blob.gif' alt='*' /></td>
		<td width='30%'>
			<input type='text' name='LOCAL_SUBNET' value='$local_subnets' />
		</td>
	</tr>
	<tr>
		<td class='boldbase' width='20%'>$Lang::tr{'remote host/ip'}:&nbsp;$blob</td>
		<td width='30%'>
			<input type='text' name='REMOTE' value='$cgiparams{'REMOTE'}' size="25" />
		</td>
		<td class='boldbase' nowrap='nowrap' width='20%'>$Lang::tr{'remote subnet'}&nbsp;$blob</td>
		<td width='30%'>
			<input $disabled type='text' name='REMOTE_SUBNET' value='$remote_subnets' />
		</td>
	</tr>
	<tr>
		<td class='boldbase' width='20%'>$Lang::tr{'vpn local id'}:</td>
		<td width='30%'>
			<input type='text' name='LOCAL_ID' value='$cgiparams{'LOCAL_ID'}' size="25" />
		</td>
		<td class='boldbase' width='20%'>$Lang::tr{'vpn remote id'}:</td>
		<td width='30%'>
			<input type='text' name='REMOTE_ID' value='$cgiparams{'REMOTE_ID'}' size="25" />
		</td>
	</tr>
	<tr><td colspan="4"><br /></td></tr>
	<tr>
		<td class='boldbase' width='20%'>$Lang::tr{'remark title'}</td>
		<td colspan='3'>
			<input type='text' name='REMARK' value='$cgiparams{'REMARK'}' maxlength='50' size="73" />
		</td>
	</tr>
END
;
	if (!$cgiparams{'KEY'}) {
		print "<tr><td colspan='3'><input type='checkbox' name='EDIT_ADVANCED' $checked{'EDIT_ADVANCED'}{'on'} /> $Lang::tr{'edit advanced settings when done'}</td></tr>";
	}
	print "</table>";
	&Header::closebox();

	if ($cgiparams{'KEY'} && $cgiparams{'AUTH'} eq 'psk') {
		&Header::openbox('100%', 'left', $Lang::tr{'authentication'});
		print <<END
		<table width='100%' cellpadding='0' cellspacing='5' border='0'>
		<tr><td class='base' width='50%'>$Lang::tr{'use a pre-shared key'}</td>
			<td class='base' width='50%'><input type='password' name='PSK' size='30' value='$cgiparams{'PSK'}' /></td>
		</tr>
		</table>
END
;
		&Header::closebox();
	} elsif (! $cgiparams{'KEY'}) {
		my $cakeydisabled = ( ! -f "${General::swroot}/private/cakey.pem" ) ? "disabled='disabled'" : '';
		$cgiparams{'CERT_NAME'} = $Lang::tr{'vpn no full pki'} if ($cakeydisabled);
		my $cacrtdisabled = ( ! -f "${General::swroot}/ca/cacert.pem" ) ? "disabled='disabled'" : '';

		&Header::openbox('100%', 'left', $Lang::tr{'authentication'});
		print <<END
		<table width='100%' cellpadding='0' cellspacing='5' border='0'>
		<tr><td width='5%'><input type='radio' name='AUTH' value='psk' $checked{'AUTH'}{'psk'} /></td>
			<td class='base' width='55%'>$Lang::tr{'use a pre-shared key'}</td>
			<td class='base' width='40%'><input type='password' name='PSK' size='30' value='$cgiparams{'PSK'}' /></td></tr>
		<tr><td colspan='3' bgcolor='#000000'></td></tr>
		<tr><td><input type='radio' name='AUTH' value='certreq' $checked{'AUTH'}{'certreq'} $cakeydisabled /></td>
			<td class='base'><hr />$Lang::tr{'upload a certificate request'}</td>
			<td class='base' rowspan='3' valign='middle'><input type='file' name='FH' size='30' $cacrtdisabled /></td></tr>
		<tr><td><input type='radio' name='AUTH' value='certfile' $checked{'AUTH'}{'certfile'} $cacrtdisabled /></td>
			<td class='base'>$Lang::tr{'upload a certificate'}</td></tr>
		<tr><td><input type='radio' name='AUTH' value='pkcs12' $cacrtdisabled /></td>
			<td class='base'>$Lang::tr{'upload p12 file'} $Lang::tr{'pkcs12 file password'}:<input type='password' name='P12_PASS'/></td></tr>
		<tr><td><input type='radio' name='AUTH' value='auth-dn' $checked{'AUTH'}{'auth-dn'} $cacrtdisabled /></td>
			<td class='base'><hr />$Lang::tr{'vpn auth-dn'}</td></tr>
		<tr><td colspan='3' bgcolor='#000000'></td></tr>
		<tr><td><input type='radio' name='AUTH' value='certgen' $checked{'AUTH'}{'certgen'} $cakeydisabled /></td>
			<td class='base'><hr />$Lang::tr{'generate a certificate'}</td><td>&nbsp;</td></tr>
		<tr><td>&nbsp;</td>
			<td class='base'>$Lang::tr{'users fullname or system hostname'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
			<td class='base' nowrap='nowrap'><input type='text' name='CERT_NAME' value='$cgiparams{'CERT_NAME'}' size='32' $cakeydisabled /></td></tr>
		<tr><td>&nbsp;</td>
			<td class='base'>$Lang::tr{'users email'}:</td>
			<td class='base' nowrap='nowrap'><input type='text' name='CERT_EMAIL' value='$cgiparams{'CERT_EMAIL'}' size='32' $cakeydisabled /></td></tr>
		<tr><td>&nbsp;</td>
			<td class='base'>$Lang::tr{'users department'}:</td>
			<td class='base' nowrap='nowrap'><input type='text' name='CERT_OU' value='$cgiparams{'CERT_OU'}' size='32' $cakeydisabled /></td></tr>
		<tr><td>&nbsp;</td>
			<td class='base'>$Lang::tr{'organization name'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
			<td class='base' nowrap='nowrap'><input type='text' name='CERT_ORGANIZATION' value='$cgiparams{'CERT_ORGANIZATION'}' size='32' $cakeydisabled /></td></tr>
		<tr><td>&nbsp;</td>
			<td class='base'>$Lang::tr{'city'}:</td>
			<td class='base' nowrap='nowrap'><input type='text' name='CERT_CITY' value='$cgiparams{'CERT_CITY'}' size='32' $cakeydisabled /></td></tr>
		<tr><td>&nbsp;</td>
			<td class='base'>$Lang::tr{'state or province'}:</td>
			<td class='base' nowrap='nowrap'><input type='text' name='CERT_STATE' value='$cgiparams{'CERT_STATE'}' size='32' $cakeydisabled /></td></tr>
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

		<tr><td>&nbsp;</td><td class='base'>$Lang::tr{'vpn subjectaltname'} (subjectAltName=email:*,URI:*,DNS:*,RID:*)</td>
			<td class='base' nowrap='nowrap'><input type='text' name='SUBJECTALTNAME' value='$cgiparams{'SUBJECTALTNAME'}' size='32' $cakeydisabled /></td></tr>
		<tr><td>&nbsp;</td>
			<td class='base'>$Lang::tr{'pkcs12 file password'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
			<td class='base' nowrap='nowrap'><input type='password' name='CERT_PASS1' value='$cgiparams{'CERT_PASS1'}' size='32' $cakeydisabled /></td></tr>
		<tr><td>&nbsp;</td><td class='base'>$Lang::tr{'pkcs12 file password'}&nbsp;($Lang::tr{'confirmation'}):&nbsp;<img src='/blob.gif' alt='*' /></td>
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
		my @temp = split('\|', $cgiparams{'IKE_ENCRYPTION'});
		if ($#temp < 0) {
			$errormessage = $Lang::tr{'invalid input'};
			goto ADVANCED_ERROR;
		}
		foreach my $val (@temp) {
			if ($val !~ /^(aes(256|192|128)(gcm(128|96|64))?|3des|chacha20poly1305|camellia(256|192|128))$/) {
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
			if ($val !~ /^(sha2_(512|384|256)|sha|md5|aesxcbc)$/) {
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
			if ($val !~ /^(curve25519|e521|e384|e256|e224|e192|e512bp|e384bp|e256bp|e224bp|768|1024|1536|2048|3072|4096|6144|8192)$/) {
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
			if ($val !~ /^(aes(256|192|128)(gcm(128|96|64))?|3des|chacha20poly1305|camellia(256|192|128))$/) {
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
			if ($val !~ /^(sha2_(512|384|256)|sha1|md5|aesxcbc)$/) {
				$errormessage = $Lang::tr{'invalid input'};
				goto ADVANCED_ERROR;
			}
		}
		@temp = split('\|', $cgiparams{'ESP_GROUPTYPE'});
		if ($#temp < 0) {
			$errormessage = $Lang::tr{'invalid input'};
			goto ADVANCED_ERROR;
		}
		foreach my $val (@temp) {
			if ($val !~ /^(curve25519|e521|e384|e256|e224|e192|e512bp|e384bp|e256bp|e224bp|768|1024|1536|2048|3072|4096|6144|8192|none)$/) {
				$errormessage = $Lang::tr{'invalid input'};
				goto ADVANCED_ERROR;
			}
		}
		if ($cgiparams{'ESP_KEYLIFE'} !~ /^\d+$/) {
			$errormessage = $Lang::tr{'invalid input for esp keylife'};
			goto ADVANCED_ERROR;
		}
		if ($cgiparams{'ESP_KEYLIFE'} < 1 || $cgiparams{'ESP_KEYLIFE'} > 24) {
			$errormessage = $Lang::tr{'esp keylife should be between 1 and 24 hours'};
			goto ADVANCED_ERROR;
		}

		if (($cgiparams{'COMPRESSION'} !~ /^(|on|off)$/) ||
			($cgiparams{'FORCE_MOBIKE'} !~ /^(|on|off)$/) ||
			($cgiparams{'ONLY_PROPOSED'} !~ /^(|on|off)$/) ||
			($cgiparams{'PFS'} !~ /^(|on|off)$/)) {
			$errormessage = $Lang::tr{'invalid input'};
			goto ADVANCED_ERROR;
		}

		if ($cgiparams{'DPD_DELAY'} !~ /^\d+$/) {
			$errormessage = $Lang::tr{'invalid input for dpd delay'};
			goto ADVANCED_ERROR;
		}

		if ($cgiparams{'DPD_TIMEOUT'} !~ /^\d+$/) {
			$errormessage = $Lang::tr{'invalid input for dpd timeout'};
			goto ADVANCED_ERROR;
		}

		if ($cgiparams{'INACTIVITY_TIMEOUT'} !~ /^\d+$/) {
			$errormessage = $Lang::tr{'invalid input for inactivity timeout'};
			goto ADVANCED_ERROR;
		}

		$confighash{$cgiparams{'KEY'}}[29] = $cgiparams{'IKE_VERSION'};
		$confighash{$cgiparams{'KEY'}}[18] = $cgiparams{'IKE_ENCRYPTION'};
		$confighash{$cgiparams{'KEY'}}[19] = $cgiparams{'IKE_INTEGRITY'};
		$confighash{$cgiparams{'KEY'}}[20] = $cgiparams{'IKE_GROUPTYPE'};
		$confighash{$cgiparams{'KEY'}}[16] = $cgiparams{'IKE_LIFETIME'};
		$confighash{$cgiparams{'KEY'}}[21] = $cgiparams{'ESP_ENCRYPTION'};
		$confighash{$cgiparams{'KEY'}}[22] = $cgiparams{'ESP_INTEGRITY'};
		$confighash{$cgiparams{'KEY'}}[23] = $cgiparams{'ESP_GROUPTYPE'};
		$confighash{$cgiparams{'KEY'}}[17] = $cgiparams{'ESP_KEYLIFE'};
		$confighash{$cgiparams{'KEY'}}[12] = 'off'; #$cgiparams{'AGGRMODE'};
		$confighash{$cgiparams{'KEY'}}[13] = $cgiparams{'COMPRESSION'};
		$confighash{$cgiparams{'KEY'}}[24] = $cgiparams{'ONLY_PROPOSED'};
		$confighash{$cgiparams{'KEY'}}[28] = $cgiparams{'PFS'};
		$confighash{$cgiparams{'KEY'}}[27] = $cgiparams{'DPD_ACTION'};
		$confighash{$cgiparams{'KEY'}}[30] = $cgiparams{'DPD_TIMEOUT'};
		$confighash{$cgiparams{'KEY'}}[31] = $cgiparams{'DPD_DELAY'};
		$confighash{$cgiparams{'KEY'}}[32] = $cgiparams{'FORCE_MOBIKE'};
		$confighash{$cgiparams{'KEY'}}[33] = $cgiparams{'START_ACTION'};
		$confighash{$cgiparams{'KEY'}}[34] = $cgiparams{'INACTIVITY_TIMEOUT'};
		&General::writehasharray("${General::swroot}/vpn/config", \%confighash);
		&writeipsecfiles();
		if (&vpnenabled) {
			system('/usr/local/bin/ipsecctrl', 'S', $cgiparams{'KEY'});
			sleep $sleepDelay;
		}
		goto ADVANCED_END;
	} else {
		$cgiparams{'IKE_VERSION'}		= $confighash{$cgiparams{'KEY'}}[29];
		$cgiparams{'IKE_ENCRYPTION'}	= $confighash{$cgiparams{'KEY'}}[18];
		$cgiparams{'IKE_INTEGRITY'}		= $confighash{$cgiparams{'KEY'}}[19];
		$cgiparams{'IKE_GROUPTYPE'}		= $confighash{$cgiparams{'KEY'}}[20];
		$cgiparams{'IKE_LIFETIME'}		= $confighash{$cgiparams{'KEY'}}[16];
		$cgiparams{'ESP_ENCRYPTION'}	= $confighash{$cgiparams{'KEY'}}[21];
		$cgiparams{'ESP_INTEGRITY'}		= $confighash{$cgiparams{'KEY'}}[22];
		$cgiparams{'ESP_GROUPTYPE'}		= $confighash{$cgiparams{'KEY'}}[23];
		if ($cgiparams{'ESP_GROUPTYPE'} eq "") {
			$cgiparams{'ESP_GROUPTYPE'}	= $cgiparams{'IKE_GROUPTYPE'};
		}
		$cgiparams{'ESP_KEYLIFE'}		= $confighash{$cgiparams{'KEY'}}[17];
		$cgiparams{'COMPRESSION'}		= $confighash{$cgiparams{'KEY'}}[13];
		$cgiparams{'ONLY_PROPOSED'}		= $confighash{$cgiparams{'KEY'}}[24];
		$cgiparams{'PFS'}				= $confighash{$cgiparams{'KEY'}}[28];
		$cgiparams{'DPD_ACTION'}		= $confighash{$cgiparams{'KEY'}}[27];
		$cgiparams{'DPD_TIMEOUT'}		= $confighash{$cgiparams{'KEY'}}[30];
		$cgiparams{'DPD_DELAY'}			= $confighash{$cgiparams{'KEY'}}[31];
		$cgiparams{'FORCE_MOBIKE'}		= $confighash{$cgiparams{'KEY'}}[32];
		$cgiparams{'START_ACTION'}		= $confighash{$cgiparams{'KEY'}}[33];
		$cgiparams{'INACTIVITY_TIMEOUT'}	= $confighash{$cgiparams{'KEY'}}[34];

		if (!$cgiparams{'DPD_DELAY'}) {
			$cgiparams{'DPD_DELAY'} = 30;
		}

		if (!$cgiparams{'DPD_TIMEOUT'}) {
			$cgiparams{'DPD_TIMEOUT'} = 120;
		}

		if (!$cgiparams{'START_ACTION'}) {
			$cgiparams{'START_ACTION'} = "start";
		}

		if ($cgiparams{'INACTIVITY_TIMEOUT'} eq "") {
			$cgiparams{'INACTIVITY_TIMEOUT'} = 900; # 15 min
		}
	}

	ADVANCED_ERROR:
	$checked{'IKE_ENCRYPTION'}{'chacha20poly1305'} = '';
	$checked{'IKE_ENCRYPTION'}{'aes256'} = '';
	$checked{'IKE_ENCRYPTION'}{'aes192'} = '';
	$checked{'IKE_ENCRYPTION'}{'aes128'} = '';
	$checked{'IKE_ENCRYPTION'}{'aes256gcm128'} = '';
	$checked{'IKE_ENCRYPTION'}{'aes192gcm128'} = '';
	$checked{'IKE_ENCRYPTION'}{'aes128gcm128'} = '';
	$checked{'IKE_ENCRYPTION'}{'aes256gcm96'} = '';
	$checked{'IKE_ENCRYPTION'}{'aes192gcm96'} = '';
	$checked{'IKE_ENCRYPTION'}{'aes128gcm96'} = '';
	$checked{'IKE_ENCRYPTION'}{'aes256gcm64'} = '';
	$checked{'IKE_ENCRYPTION'}{'aes192gcm64'} = '';
	$checked{'IKE_ENCRYPTION'}{'aes128gcm64'} = '';
	$checked{'IKE_ENCRYPTION'}{'3des'} = '';
	$checked{'IKE_ENCRYPTION'}{'camellia256'} = '';
	$checked{'IKE_ENCRYPTION'}{'camellia192'} = '';
	$checked{'IKE_ENCRYPTION'}{'camellia128'} = '';
	my @temp = split('\|', $cgiparams{'IKE_ENCRYPTION'});
	foreach my $key (@temp) {$checked{'IKE_ENCRYPTION'}{$key} = "selected='selected'"; }
	$checked{'IKE_INTEGRITY'}{'sha2_512'} = '';
	$checked{'IKE_INTEGRITY'}{'sha2_384'} = '';
	$checked{'IKE_INTEGRITY'}{'sha2_256'} = '';
	$checked{'IKE_INTEGRITY'}{'sha'} = '';
	$checked{'IKE_INTEGRITY'}{'md5'} = '';
	$checked{'IKE_INTEGRITY'}{'aesxcbc'} = '';
	@temp = split('\|', $cgiparams{'IKE_INTEGRITY'});
	foreach my $key (@temp) {$checked{'IKE_INTEGRITY'}{$key} = "selected='selected'"; }
	$checked{'IKE_GROUPTYPE'}{'curve25519'} = '';
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

	$checked{'ESP_ENCRYPTION'}{'chacha20poly1305'} = '';
	$checked{'ESP_ENCRYPTION'}{'aes256'} = '';
	$checked{'ESP_ENCRYPTION'}{'aes192'} = '';
	$checked{'ESP_ENCRYPTION'}{'aes128'} = '';
	$checked{'ESP_ENCRYPTION'}{'aes256gcm128'} = '';
	$checked{'ESP_ENCRYPTION'}{'aes192gcm128'} = '';
	$checked{'ESP_ENCRYPTION'}{'aes128gcm128'} = '';
	$checked{'ESP_ENCRYPTION'}{'aes256gcm96'} = '';
	$checked{'ESP_ENCRYPTION'}{'aes192gcm96'} = '';
	$checked{'ESP_ENCRYPTION'}{'aes128gcm96'} = '';
	$checked{'ESP_ENCRYPTION'}{'aes256gcm64'} = '';
	$checked{'ESP_ENCRYPTION'}{'aes192gcm64'} = '';
	$checked{'ESP_ENCRYPTION'}{'aes128gcm64'} = '';
	$checked{'ESP_ENCRYPTION'}{'3des'} = '';
	$checked{'ESP_ENCRYPTION'}{'camellia256'} = '';
	$checked{'ESP_ENCRYPTION'}{'camellia192'} = '';
	$checked{'ESP_ENCRYPTION'}{'camellia128'} = '';
	@temp = split('\|', $cgiparams{'ESP_ENCRYPTION'});
	foreach my $key (@temp) {$checked{'ESP_ENCRYPTION'}{$key} = "selected='selected'"; }
	$checked{'ESP_INTEGRITY'}{'sha2_512'} = '';
	$checked{'ESP_INTEGRITY'}{'sha2_384'} = '';
	$checked{'ESP_INTEGRITY'}{'sha2_256'} = '';
	$checked{'ESP_INTEGRITY'}{'sha1'} = '';
	$checked{'ESP_INTEGRITY'}{'md5'} = '';
	$checked{'ESP_INTEGRITY'}{'aesxcbc'} = '';
	@temp = split('\|', $cgiparams{'ESP_INTEGRITY'});
	foreach my $key (@temp) {$checked{'ESP_INTEGRITY'}{$key} = "selected='selected'"; }
	$checked{'ESP_GROUPTYPE'}{'curve25519'} = '';
	$checked{'ESP_GROUPTYPE'}{'768'} = '';
	$checked{'ESP_GROUPTYPE'}{'1024'} = '';
	$checked{'ESP_GROUPTYPE'}{'1536'} = '';
	$checked{'ESP_GROUPTYPE'}{'2048'} = '';
	$checked{'ESP_GROUPTYPE'}{'3072'} = '';
	$checked{'ESP_GROUPTYPE'}{'4096'} = '';
	$checked{'ESP_GROUPTYPE'}{'6144'} = '';
	$checked{'ESP_GROUPTYPE'}{'8192'} = '';
	$checked{'ESP_GROUPTYPE'}{'none'} = '';
	@temp = split('\|', $cgiparams{'ESP_GROUPTYPE'});
	foreach my $key (@temp) {$checked{'ESP_GROUPTYPE'}{$key} = "selected='selected'"; }

	$checked{'COMPRESSION'} = $cgiparams{'COMPRESSION'} eq 'on' ? "checked='checked'" : '' ;
	$checked{'FORCE_MOBIKE'} = $cgiparams{'FORCE_MOBIKE'} eq 'on' ? "checked='checked'" : '' ;
	$checked{'ONLY_PROPOSED'} = $cgiparams{'ONLY_PROPOSED'} eq 'on' ? "checked='checked'" : '' ;
	$checked{'PFS'} = $cgiparams{'PFS'} eq 'on' ? "checked='checked'" : '' ;

	$selected{'IKE_VERSION'}{'ikev1'} = '';
	$selected{'IKE_VERSION'}{'ikev2'} = '';
	$selected{'IKE_VERSION'}{$cgiparams{'IKE_VERSION'}} = "selected='selected'";

	$selected{'DPD_ACTION'}{'clear'} = '';
	$selected{'DPD_ACTION'}{'hold'} = '';
	$selected{'DPD_ACTION'}{'restart'} = '';
	$selected{'DPD_ACTION'}{'none'} = '';
	$selected{'DPD_ACTION'}{$cgiparams{'DPD_ACTION'}} = "selected='selected'";

	$selected{'START_ACTION'}{'add'} = '';
	$selected{'START_ACTION'}{'route'} = '';
	$selected{'START_ACTION'}{'start'} = '';
	$selected{'START_ACTION'}{$cgiparams{'START_ACTION'}} = "selected='selected'";

	$selected{'INACTIVITY_TIMEOUT'} = ();
	foreach my $timeout (keys %INACTIVITY_TIMEOUTS) {
		$selected{'INACTIVITY_TIMEOUT'}{$timeout} = "";
	}
	$selected{'INACTIVITY_TIMEOUT'}{$cgiparams{'INACTIVITY_TIMEOUT'}} = "selected";

	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'ipsec'}, 1, '');
	&Header::openbigbox('100%', 'left', '', $errormessage);

	if ($errormessage) {
		&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
		print "<class name='base'>$errormessage";
		print "&nbsp;</class>";
		&Header::closebox();
	}

	if ($warnmessage) {
		&Header::openbox('100%', 'left', $Lang::tr{'warning messages'});
		print "<class name='base'>$warnmessage";
		print "&nbsp;</class>";
		&Header::closebox();
	}

	&Header::openbox('100%', 'left', "$Lang::tr{'advanced'}:");
	print <<EOF;
	<form method='post' enctype='multipart/form-data' action='$ENV{'SCRIPT_NAME'}'>
	<input type='hidden' name='ADVANCED' value='yes' />
	<input type='hidden' name='KEY' value='$cgiparams{'KEY'}' />

	<table width='100%'>
	<thead>
		<tr>
			<th width="15%"></th>
			<th>IKE</th>
			<th>ESP</th>
		</tr>
	</thead>
	<tbody>
		<tr>
			<td>$Lang::tr{'vpn keyexchange'}:</td>
			<td>
				<select name='IKE_VERSION'>
					<option value='ikev2' $selected{'IKE_VERSION'}{'ikev2'}>IKEv2</option>
					<option value='ikev1' $selected{'IKE_VERSION'}{'ikev1'}>IKEv1</option>
				</select>
			</td>
			<td></td>
		</tr>
		<tr>
			<td class='boldbase' width="15%">$Lang::tr{'encryption'}</td>
			<td class='boldbase'>
				<select name='IKE_ENCRYPTION' multiple='multiple' size='6' style='width: 100%'>
					<option value='chacha20poly1305' $checked{'IKE_ENCRYPTION'}{'chacha20poly1305'}>256 bit ChaCha20-Poly1305/128 bit ICV</option>
					<option value='aes256gcm128' $checked{'IKE_ENCRYPTION'}{'aes256gcm128'}>256 bit AES-GCM/128 bit ICV</option>
					<option value='aes256gcm96' $checked{'IKE_ENCRYPTION'}{'aes256gcm96'}>256 bit AES-GCM/96 bit ICV</option>
					<option value='aes256gcm64' $checked{'IKE_ENCRYPTION'}{'aes256gcm64'}>256 bit AES-GCM/64 bit ICV</option>
					<option value='aes256' $checked{'IKE_ENCRYPTION'}{'aes256'}>256 bit AES-CBC</option>
					<option value='camellia256' $checked{'IKE_ENCRYPTION'}{'camellia256'}>256 bit Camellia-CBC</option>
					<option value='aes192gcm128' $checked{'IKE_ENCRYPTION'}{'aes192gcm128'}>192 bit AES-GCM/128 bit ICV</option>
					<option value='aes192gcm96' $checked{'IKE_ENCRYPTION'}{'aes192gcm96'}>192 bit AES-GCM/96 bit ICV</option>
					<option value='aes192gcm64' $checked{'IKE_ENCRYPTION'}{'aes192gcm64'}>192 bit AES-GCM/64 bit ICV</option>
					<option value='aes192' $checked{'IKE_ENCRYPTION'}{'aes192'}>192 bit AES-CBC</option>
					<option value='camellia192' $checked{'IKE_ENCRYPTION'}{'camellia192'}>192 bit Camellia-CBC</option>
					<option value='aes128gcm128' $checked{'IKE_ENCRYPTION'}{'aes128gcm128'}>128 bit AES-GCM/128 bit ICV</option>
					<option value='aes128gcm96' $checked{'IKE_ENCRYPTION'}{'aes128gcm96'}>128 bit AES-GCM/96 bit ICV</option>
					<option value='aes128gcm64' $checked{'IKE_ENCRYPTION'}{'aes128gcm64'}>128 bit AES-GCM/64 bit ICV</option>
					<option value='aes128' $checked{'IKE_ENCRYPTION'}{'aes128'}>128 bit AES-CBC</option>
					<option value='camellia128' $checked{'IKE_ENCRYPTION'}{'camellia128'}>128 bit Camellia-CBC</option>
					<option value='3des' $checked{'IKE_ENCRYPTION'}{'3des'}>168 bit 3DES-EDE-CBC ($Lang::tr{'vpn weak'})</option>
				</select>
			</td>
			<td class='boldbase'>
				<select name='ESP_ENCRYPTION' multiple='multiple' size='6' style='width: 100%'>
					<option value='chacha20poly1305' $checked{'ESP_ENCRYPTION'}{'chacha20poly1305'}>256 bit ChaCha20-Poly1305/128 bit ICV</option>
					<option value='aes256gcm128' $checked{'ESP_ENCRYPTION'}{'aes256gcm128'}>256 bit AES-GCM/128 bit ICV</option>
					<option value='aes256gcm96' $checked{'ESP_ENCRYPTION'}{'aes256gcm96'}>256 bit AES-GCM/96 bit ICV</option>
					<option value='aes256gcm64' $checked{'ESP_ENCRYPTION'}{'aes256gcm64'}>256 bit AES-GCM/64 bit ICV</option>
					<option value='aes256' $checked{'ESP_ENCRYPTION'}{'aes256'}>256 bit AES-CBC</option>
					<option value='camellia256' $checked{'ESP_ENCRYPTION'}{'camellia256'}>256 bit Camellia-CBC</option>
					<option value='aes192gcm128' $checked{'ESP_ENCRYPTION'}{'aes192gcm128'}>192 bit AES-GCM/128 bit ICV</option>
					<option value='aes192gcm96' $checked{'ESP_ENCRYPTION'}{'aes192gcm96'}>192 bit AES-GCM/96 bit ICV</option>
					<option value='aes192gcm64' $checked{'ESP_ENCRYPTION'}{'aes192gcm64'}>192 bit AES-GCM/64 bit ICV</option>
					<option value='aes192' $checked{'ESP_ENCRYPTION'}{'aes192'}>192 bit AES-CBC</option>
					<option value='camellia192' $checked{'ESP_ENCRYPTION'}{'camellia192'}>192 bit Camellia-CBC</option>
					<option value='aes128gcm128' $checked{'ESP_ENCRYPTION'}{'aes128gcm128'}>128 bit AES-GCM/128 bit ICV</option>
					<option value='aes128gcm96' $checked{'ESP_ENCRYPTION'}{'aes128gcm96'}>128 bit AES-GCM/96 bit ICV</option>
					<option value='aes128gcm64' $checked{'ESP_ENCRYPTION'}{'aes128gcm64'}>128 bit AES-GCM/64 bit ICV</option>
					<option value='aes128' $checked{'ESP_ENCRYPTION'}{'aes128'}>128 bit AES-CBC</option>
					<option value='camellia128' $checked{'ESP_ENCRYPTION'}{'camellia128'}>128 bit Camellia-CBC</option>
					<option value='3des' $checked{'ESP_ENCRYPTION'}{'3des'}>168 bit 3DES-EDE-CBC ($Lang::tr{'vpn weak'})</option>
				</select>
			</td>
		</tr>

		<tr>
			<td class='boldbase' width="15%">$Lang::tr{'integrity'}</td>
			<td class='boldbase'>
				<select name='IKE_INTEGRITY' multiple='multiple' size='6' style='width: 100%'>
					<option value='sha2_512' $checked{'IKE_INTEGRITY'}{'sha2_512'}>SHA2 512 bit</option>
					<option value='sha2_384' $checked{'IKE_INTEGRITY'}{'sha2_384'}>SHA2 384 bit</option>
					<option value='sha2_256' $checked{'IKE_INTEGRITY'}{'sha2_256'}>SHA2 256 bit</option>
					<option value='aesxcbc' $checked{'IKE_INTEGRITY'}{'aesxcbc'}>AES XCBC</option>
					<option value='sha' $checked{'IKE_INTEGRITY'}{'sha'}>SHA1 ($Lang::tr{'vpn weak'})</option>
					<option value='md5' $checked{'IKE_INTEGRITY'}{'md5'}>MD5 ($Lang::tr{'vpn broken'})</option>
				</select>
			</td>
			<td class='boldbase'>
				<select name='ESP_INTEGRITY' multiple='multiple' size='6' style='width: 100%'>
					<option value='sha2_512' $checked{'ESP_INTEGRITY'}{'sha2_512'}>SHA2 512 bit</option>
					<option value='sha2_384' $checked{'ESP_INTEGRITY'}{'sha2_384'}>SHA2 384 bit</option>
					<option value='sha2_256' $checked{'ESP_INTEGRITY'}{'sha2_256'}>SHA2 256 bit</option>
					<option value='aesxcbc' $checked{'ESP_INTEGRITY'}{'aesxcbc'}>AES XCBC</option>
					<option value='sha1' $checked{'ESP_INTEGRITY'}{'sha1'}>SHA1 ($Lang::tr{'vpn weak'})</option>
					<option value='md5' $checked{'ESP_INTEGRITY'}{'md5'}>MD5 ($Lang::tr{'vpn broken'})</option>
				</select>
			</td>
		</tr>
		<tr>
			<td class='boldbase' width="15%">$Lang::tr{'lifetime'}&nbsp;<img src='/blob.gif' alt='*' /></td>
			<td class='boldbase'>
				<input type='text' name='IKE_LIFETIME' value='$cgiparams{'IKE_LIFETIME'}' size='5' /> $Lang::tr{'hours'}
			</td>
			<td class='boldbase'>
				<input type='text' name='ESP_KEYLIFE' value='$cgiparams{'ESP_KEYLIFE'}' size='5' /> $Lang::tr{'hours'}
			</td>
		</tr>
		<tr>
			<td class='boldbase' width="15%">$Lang::tr{'grouptype'}</td>
			<td class='boldbase'>
				<select name='IKE_GROUPTYPE' multiple='multiple' size='6' style='width: 100%'>
					<option value='curve25519' $checked{'IKE_GROUPTYPE'}{'curve25519'}>Curve 25519 (256 bit)</option>
					<option value='e521' $checked{'IKE_GROUPTYPE'}{'e521'}>ECP-521 (NIST)</option>
					<option value='e512bp' $checked{'IKE_GROUPTYPE'}{'e512bp'}>ECP-512 (Brainpool)</option>
					<option value='e384' $checked{'IKE_GROUPTYPE'}{'e384'}>ECP-384 (NIST)</option>
					<option value='e384bp' $checked{'IKE_GROUPTYPE'}{'e384bp'}>ECP-384 (Brainpool)</option>
					<option value='e256' $checked{'IKE_GROUPTYPE'}{'e256'}>ECP-256 (NIST)</option>
					<option value='e256bp' $checked{'IKE_GROUPTYPE'}{'e256bp'}>ECP-256 (Brainpool)</option>
					<option value='e224' $checked{'IKE_GROUPTYPE'}{'e224'}>ECP-224 (NIST)</option>
					<option value='e224bp' $checked{'IKE_GROUPTYPE'}{'e224bp'}>ECP-224 (Brainpool)</option>
					<option value='e192' $checked{'IKE_GROUPTYPE'}{'e192'}>ECP-192 (NIST)</option>
					<option value='8192' $checked{'IKE_GROUPTYPE'}{'8192'}>MODP-8192</option>
					<option value='6144' $checked{'IKE_GROUPTYPE'}{'6144'}>MODP-6144</option>
					<option value='4096' $checked{'IKE_GROUPTYPE'}{'4096'}>MODP-4096</option>
					<option value='3072' $checked{'IKE_GROUPTYPE'}{'3072'}>MODP-3072</option>
					<option value='2048' $checked{'IKE_GROUPTYPE'}{'2048'}>MODP-2048</option>
					<option value='1536' $checked{'IKE_GROUPTYPE'}{'1536'}>MODP-1536</option>
					<option value='1024' $checked{'IKE_GROUPTYPE'}{'1024'}>MODP-1024 ($Lang::tr{'vpn broken'})</option>
					<option value='768' $checked{'IKE_GROUPTYPE'}{'768'}>MODP-768 ($Lang::tr{'vpn broken'})</option>
				</select>
			</td>
			<td class='boldbase'>
				<select name='ESP_GROUPTYPE' multiple='multiple' size='6' style='width: 100%'>
					<option value='curve25519' $checked{'ESP_GROUPTYPE'}{'curve25519'}>Curve 25519 (256 bit)</option>
					<option value='e521' $checked{'ESP_GROUPTYPE'}{'e521'}>ECP-521 (NIST)</option>
					<option value='e512bp' $checked{'ESP_GROUPTYPE'}{'e512bp'}>ECP-512 (Brainpool)</option>
					<option value='e384' $checked{'ESP_GROUPTYPE'}{'e384'}>ECP-384 (NIST)</option>
					<option value='e384bp' $checked{'ESP_GROUPTYPE'}{'e384bp'}>ECP-384 (Brainpool)</option>
					<option value='e256' $checked{'ESP_GROUPTYPE'}{'e256'}>ECP-256 (NIST)</option>
					<option value='e256bp' $checked{'ESP_GROUPTYPE'}{'e256bp'}>ECP-256 (Brainpool)</option>
					<option value='e224' $checked{'ESP_GROUPTYPE'}{'e224'}>ECP-224 (NIST)</option>
					<option value='e224bp' $checked{'ESP_GROUPTYPE'}{'e224bp'}>ECP-224 (Brainpool)</option>
					<option value='e192' $checked{'ESP_GROUPTYPE'}{'e192'}>ECP-192 (NIST)</option>
					<option value='8192' $checked{'ESP_GROUPTYPE'}{'8192'}>MODP-8192</option>
					<option value='6144' $checked{'ESP_GROUPTYPE'}{'6144'}>MODP-6144</option>
					<option value='4096' $checked{'ESP_GROUPTYPE'}{'4096'}>MODP-4096</option>
					<option value='3072' $checked{'ESP_GROUPTYPE'}{'3072'}>MODP-3072</option>
					<option value='2048' $checked{'ESP_GROUPTYPE'}{'2048'}>MODP-2048</option>
					<option value='1536' $checked{'ESP_GROUPTYPE'}{'1536'}>MODP-1536</option>
					<option value='1024' $checked{'ESP_GROUPTYPE'}{'1024'}>MODP-1024 ($Lang::tr{'vpn broken'})</option>
					<option value='768' $checked{'ESP_GROUPTYPE'}{'768'}>MODP-768 ($Lang::tr{'vpn broken'})</option>
					<option value='none' $checked{'ESP_GROUPTYPE'}{'none'}>- $Lang::tr{'none'} -</option>
				</select>
			</td>
		</tr>
	</tbody>
	</table>

	<br><br>

	<h2>$Lang::tr{'dead peer detection'}</h2>

	<table width="100%">
	<tr>
		<td width="15%">$Lang::tr{'dpd action'}:</td>
		<td>
			<select name='DPD_ACTION'>
				<option value='none' $selected{'DPD_ACTION'}{'none'}>- $Lang::tr{'disabled'} -</option>
				<option value='clear' $selected{'DPD_ACTION'}{'clear'}>clear</option>
				<option value='hold' $selected{'DPD_ACTION'}{'hold'}>hold</option>
				<option value='restart' $selected{'DPD_ACTION'}{'restart'}>restart</option>
			</select>
		</td>
	</tr>
	<tr>
		<td width="15%">$Lang::tr{'dpd timeout'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
		<td>
			<input type='text' name='DPD_TIMEOUT' size='5' value='$cgiparams{'DPD_TIMEOUT'}' />
		</td>
	</tr>
	<tr>
		<td width="15%">$Lang::tr{'dpd delay'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
		<td>
			<input type='text' name='DPD_DELAY' size='5' value='$cgiparams{'DPD_DELAY'}' />
		</td>
	</tr>
	</table>

	<hr>

	<table width="100%">
	<tr>
		<td>
			<label>
				<input type='checkbox' name='ONLY_PROPOSED' $checked{'ONLY_PROPOSED'} />
				IKE+ESP: $Lang::tr{'use only proposed settings'}
			</label>
		</td>
		<td>
			<label>$Lang::tr{'vpn start action'}</label>
			<select name="START_ACTION">
				<option value="route" $selected{'START_ACTION'}{'route'}>$Lang::tr{'vpn start action route'}</option>
				<option value="start" $selected{'START_ACTION'}{'start'}>$Lang::tr{'vpn start action start'}</option>
				<option value="add"   $selected{'START_ACTION'}{'add'}  >$Lang::tr{'vpn start action add'}</option>
			</select>
		</td>
	</tr>
	<tr>
		<td>
			<label>
				<input type='checkbox' name='PFS' $checked{'PFS'} />
				$Lang::tr{'pfs yes no'}
			</label>
		</td>
		<td>
			<label>$Lang::tr{'vpn inactivity timeout'}</label>
			<select name="INACTIVITY_TIMEOUT">
EOF
	foreach my $t (sort { $a <=> $b } keys %INACTIVITY_TIMEOUTS) {
		print "<option value=\"$t\" $selected{'INACTIVITY_TIMEOUT'}{$t}>$INACTIVITY_TIMEOUTS{$t}</option>\n";
	}

	print <<EOF;

			</select>
		</td>
	</tr>
	<tr>
		<td colspan="2">
			<label>
				<input type='checkbox' name='COMPRESSION' $checked{'COMPRESSION'} />
				$Lang::tr{'vpn payload compression'}
			</label>
		</td>
	</tr>
	<tr>
		<td colspan="2">
			<label>
				<input type='checkbox' name='FORCE_MOBIKE' $checked{'FORCE_MOBIKE'} />
				$Lang::tr{'vpn force mobike'}
			</label>
		</td>
	</tr>
	<tr>
		<td align='left'><img src='/blob.gif' align='top' alt='*' />&nbsp;$Lang::tr{'required field'}</td>
		<td align='right'>
			<input type='submit' name='ACTION' value='$Lang::tr{'save'}' />
			<input type='submit' name='ACTION' value='$Lang::tr{'cancel'}' />
		</td>
	</tr>
	</table></form>
EOF

	&Header::closebox();
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
	$cgiparams{'CA_NAME'} = '';

	my @status = `/usr/local/bin/ipsecctrl I 2>/dev/null`;

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
	$checked{'ENABLED'} = $cgiparams{'ENABLED'} eq 'on' ? "checked='checked'" : '';

	&Header::showhttpheaders();
	&Header::openpage($Lang::tr{'ipsec'}, 1, '');
	&Header::openbigbox('100%', 'left', '', $errormessage);

	if ($errormessage) {
		&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
		print "<class name='base'>$errormessage\n";
		print "&nbsp;</class>\n";
		&Header::closebox();
	}

	if ($warnmessage) {
		&Header::openbox('100%', 'left', $Lang::tr{'warning messages'});
		print "$warnmessage<br>";
		print "$Lang::tr{'fwdfw warn1'}<br>";
		&Header::closebox();
		print"<center><form method='post'><input type='submit' name='ACTION' value='$Lang::tr{'ok'}' style='width: 5em;'></form>";
		&Header::closepage();
		exit 0;
	}

	&Header::openbox('100%', 'left', $Lang::tr{'global settings'});
	print <<END
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table width='100%'>
	<tr>
	<td width='20%' class='base' nowrap='nowrap'>$Lang::tr{'vpn red name'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td width='20%'><input type='text' name='VPN_IP' value='$cgiparams{'VPN_IP'}' /></td>
	<td width='20%' class='base'>$Lang::tr{'enabled'}<input type='checkbox' name='ENABLED' $checked{'ENABLED'} /></td>
	</tr>
END
;
print <<END
	<tr>
	<td class='base' nowrap='nowrap'>$Lang::tr{'vpn delayed start'}:&nbsp;<img src='/blob.gif' alt='*' /><img src='/blob.gif' alt='*' /></td>
	<td ><input type='text' name='VPN_DELAYED_START' value='$cgiparams{'VPN_DELAYED_START'}' /></td>
	</tr>
	<tr>
	<td class='base' nowrap='nowrap'>$Lang::tr{'host to net vpn'}:</td>
	<td ><input type='text' name='RW_NET' value='$cgiparams{'RW_NET'}' /></td>
	</tr>
</table>
<br>
<hr />
<table width='100%'>
<tr>
	<td class='base' valign='top'><img src='/blob.gif' alt='*' /></td>
	<td width='70%' class='base' valign='top'>$Lang::tr{'required field'}</td><td width='30%' align='right' class='base'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
</tr>
<tr>
	<td class='base' valign='top' nowrap='nowrap'><img src='/blob.gif' alt='*' /><img src='/blob.gif' alt='*' />&nbsp;</td>
	<td class='base'>	<font class='base'>$Lang::tr{'vpn delayed start help'}</font></td>
	<td></td>
</tr>
</table>
END
;
	print "</form>";
	&Header::closebox();

	&Header::openbox('100%', 'left', $Lang::tr{'connection status and controlc'});
	print <<END
	<table width='100%' cellspacing='1' cellpadding='0' class='tbl'>
	<tr>
	<th width='10%' class='boldbase' align='center'><b>$Lang::tr{'name'}</b></th>
	<th width='22%' class='boldbase' align='center'><b>$Lang::tr{'type'}</b></th>
	<th width='23%' class='boldbase' align='center'><b>$Lang::tr{'common name'}</b></th>
	<th width='30%' class='boldbase' align='center'><b>$Lang::tr{'remark'}</b></th>
	<th width='10%' class='boldbase' align='center'><b>$Lang::tr{'status'}</b></th>
	<th class='boldbase' align='center' colspan='6'><b>$Lang::tr{'action'}</b></th>
	</tr>
END
;
	my $id = 0;
	my $gif;
	foreach my $key (sort { ncmp ($confighash{$a}[1],$confighash{$b}[1]) } keys %confighash) {
	if ($confighash{$key}[0] eq 'on') { $gif = 'on.gif'; } else { $gif = 'off.gif'; }

	if ($id % 2) {
		print "<tr>";
		$col="bgcolor='$color{'color20'}'";
	} else {
		print "<tr>";
		$col="bgcolor='$color{'color22'}'";
	}
	print "<td align='center' nowrap='nowrap' $col>$confighash{$key}[1]</td>";
	print "<td align='center' nowrap='nowrap' $col>" . $Lang::tr{"$confighash{$key}[3]"} . " (" . $Lang::tr{"$confighash{$key}[4]"} . ") $confighash{$key}[29]</td>";
	if ($confighash{$key}[2] eq '%auth-dn') {
		print "<td align='left' nowrap='nowrap' $col>$confighash{$key}[9]</td>";
	} elsif ($confighash{$key}[4] eq 'cert') {
		print "<td align='left' nowrap='nowrap' $col>$confighash{$key}[2]</td>";
	} else {
		print "<td align='left' $col>&nbsp;</td>";
	}
	print "<td align='center' $col>$confighash{$key}[25]</td>";
	my $col1="bgcolor='${Header::colourred}'";
	my $active = "<b><font color='#FFFFFF'>$Lang::tr{'capsclosed'}</font></b>";
	if ($confighash{$key}[33] eq "add") {
		$col1="bgcolor='${Header::colourorange}'";
		$active = "<b><font color='#FFFFFF'>$Lang::tr{'vpn wait'}</font></b>";
	}
	foreach my $line (@status) {
		if (($line =~ /\"$confighash{$key}[1]\".*IPsec SA established/) ||
		($line =~ /$confighash{$key}[1]\{.*INSTALLED/)) {
			$col1="bgcolor='${Header::colourgreen}'";
			$active = "<b><font color='#FFFFFF'>$Lang::tr{'capsopen'}</font></b>";
		} elsif ($line =~ /$confighash{$key}[1]\[.*CONNECTING/) {
			$col1="bgcolor='${Header::colourorange}'";
			$active = "<b><font color='#FFFFFF'>$Lang::tr{'vpn connecting'}</font></b>";
		} elsif ($line =~ /$confighash{$key}[1]\{.*ROUTED/) {
			$col1="bgcolor='${Header::colourorange}'";
			$active = "<b><font color='#FFFFFF'>$Lang::tr{'vpn on-demand'}</font></b>";
		}
	}
	# move to blue if really down
	if ($confighash{$key}[0] eq 'off' && $col1 =~ /${Header::colourred}/ ) {
		$col1="bgcolor='${Header::colourblue}'";
		$active = "<b><font color='#FFFFFF'>$Lang::tr{'capsclosed'}</font></b>";
	}
	print <<END
	<td align='center' $col1>$active</td>
	<td align='center' $col>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<input type='image' name='$Lang::tr{'restart'}' src='/images/reload.gif' alt='$Lang::tr{'restart'}' title='$Lang::tr{'restart'}' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'restart'}' />
		<input type='hidden' name='KEY' value='$key' />
		</form>
	</td>
END
;
	if (($confighash{$key}[4] eq 'cert') && ($confighash{$key}[2] ne '%auth-dn')) {
		print <<END
		<td align='center' $col>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<input type='image' name='$Lang::tr{'show certificate'}' src='/images/info.gif' alt='$Lang::tr{'show certificate'}' title='$Lang::tr{'show certificate'}' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'show certificate'}' />
		<input type='hidden' name='KEY' value='$key' />
		</form>
		</td>
END
;
	} else {
		print "<td width='2%' $col>&nbsp;</td>";
	}
	if ($confighash{$key}[4] eq 'cert' && -f "${General::swroot}/certs/$confighash{$key}[1].p12") {
		print <<END
		<td align='center' $col>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<input type='image' name='$Lang::tr{'download pkcs12 file'}' src='/images/floppy.gif' alt='$Lang::tr{'download pkcs12 file'}' title='$Lang::tr{'download pkcs12 file'}' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'download pkcs12 file'}' />
		<input type='hidden' name='KEY' value='$key' />
		</form>
	</td>
END
;
	} elsif (($confighash{$key}[4] eq 'cert') && ($confighash{$key}[2] ne '%auth-dn')) {
		print <<END
		<td align='center' $col>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<input type='image' name='$Lang::tr{'download certificate'}' src='/images/floppy.gif' alt='$Lang::tr{'download certificate'}' title='$Lang::tr{'download certificate'}' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'download certificate'}' />
		<input type='hidden' name='KEY' value='$key' />
		</form>
	</td>
END
;
	} else {
		print "<td width='2%' $col>&nbsp;</td>";
	}
	print <<END
	<td align='center' $col>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif' alt='$Lang::tr{'toggle enable disable'}' title='$Lang::tr{'toggle enable disable'}' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'toggle enable disable'}' />
		<input type='hidden' name='KEY' value='$key' />
		</form>
	</td>

	<td align='center' $col>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<input type='hidden' name='ACTION' value='$Lang::tr{'edit'}' />
		<input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' />
		<input type='hidden' name='KEY' value='$key' />
		</form>
	</td>
	<td align='center' $col>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<input type='hidden' name='ACTION' value='$Lang::tr{'remove'}' />
		<input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' alt='$Lang::tr{'remove'}' title='$Lang::tr{'remove'}' />
		<input type='hidden' name='KEY' value='$key' />
		</form>
	</td>
	</tr>
END
;
	$id++;
	}
	print "</table>";

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
	<tr><td align='right' colspan='9'>
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<input type='submit' name='ACTION' value='$Lang::tr{'add'}' />
	</form>
	</td></tr>
	</table>
END
;
	&Header::closebox();

	&Header::openbox('100%', 'left', "$Lang::tr{'certificate authorities'}");
	print <<EOF
	<table width='100%' cellspacing='1' cellpadding='0' class='tbl'>
	<tr>
	<th width='25%' class='boldbase' align='center'><b>$Lang::tr{'name'}</b></th>
	<th width='65%' class='boldbase' align='center'><b>$Lang::tr{'subject'}</b></th>
	<th width='10%' class='boldbase' colspan='3' align='center'><b>$Lang::tr{'action'}</b></th>
	</tr>
EOF
;
	my $col1="bgcolor='$color{'color22'}'";
	my $col2="bgcolor='$color{'color20'}'";
	if (-f "${General::swroot}/ca/cacert.pem") {
		my $casubject = &Header::cleanhtml(getsubjectfromcert ("${General::swroot}/ca/cacert.pem"));
		print <<END
		<tr>
		<td class='base' $col1>$Lang::tr{'root certificate'}</td>
		<td class='base' $col1>$casubject</td>
		<td width='3%' align='center' $col1>
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='hidden' name='ACTION' value='$Lang::tr{'show root certificate'}' />
			<input type='image' name='$Lang::tr{'edit'}' src='/images/info.gif' alt='$Lang::tr{'show root certificate'}' title='$Lang::tr{'show root certificate'}' />
			</form>
		</td>
		<td width='3%' align='center' $col1>
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='image' name='$Lang::tr{'download root certificate'}' src='/images/floppy.gif' alt='$Lang::tr{'download root certificate'}' title='$Lang::tr{'download root certificate'}' />
			<input type='hidden' name='ACTION' value='$Lang::tr{'download root certificate'}' />
			</form>
		</td>
		<td width='4%' $col1>&nbsp;</td></tr>
END
;
	} else {
		# display rootcert generation buttons
		print <<END
		<tr>
		<td class='base' $col1>$Lang::tr{'root certificate'}:</td>
		<td class='base' $col1>$Lang::tr{'not present'}</td>
		<td colspan='3' $col1>&nbsp;</td></tr>
END
;
	}

	if (-f "${General::swroot}/certs/hostcert.pem") {
		my $hostsubject = &Header::cleanhtml(getsubjectfromcert ("${General::swroot}/certs/hostcert.pem"));

		print <<END
		<tr>
		<td class='base' $col2>$Lang::tr{'host certificate'}</td>
		<td class='base' $col2>$hostsubject</td>
		<td width='3%' align='center' $col2>
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='hidden' name='ACTION' value='$Lang::tr{'show host certificate'}' />
			<input type='image' name='$Lang::tr{'show host certificate'}' src='/images/info.gif' alt='$Lang::tr{'show host certificate'}' title='$Lang::tr{'show host certificate'}' />
			</form>
		</td>
		<td width='3%' align='center' $col2>
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='image' name="$Lang::tr{'download host certificate'}" src='/images/floppy.gif' alt="$Lang::tr{'download host certificate'}" title="$Lang::tr{'download host certificate'}" />
			<input type='hidden' name='ACTION' value="$Lang::tr{'download host certificate'}" />
			</form>
		</td>
		<td width='4%' $col2>&nbsp;</td></tr>
END
;
	} else {
		# Nothing
		print <<END
		<tr>
		<td width='25%' class='base' $col2>$Lang::tr{'host certificate'}:</td>
		<td class='base' $col2>$Lang::tr{'not present'}</td>
		<td colspan='3' $col2>&nbsp;</td></tr>
END
;
	}

	my $rowcolor = 0;
	if (keys %cahash > 0) {
		foreach my $key (keys %cahash) {
				if ($rowcolor++ % 2) {
					print "<tr>";
					$col="bgcolor='$color{'color20'}'";
				} else {
					print "<tr>";
					$col="bgcolor='$color{'color22'}'";
				}
			print "<td class='base' $col>$cahash{$key}[0]</td>\n";
			print "<td class='base' $col>$cahash{$key}[1]</td>\n";
			print <<END
			<td align='center' $col>
			<form method='post' name='cafrm${key}a' action='$ENV{'SCRIPT_NAME'}'>
			<input type='image' name='$Lang::tr{'show ca certificate'}' src='/images/info.gif' alt='$Lang::tr{'show ca certificate'}' title='$Lang::tr{'show ca certificate'}' />
			<input type='hidden' name='ACTION' value='$Lang::tr{'show ca certificate'}' />
			<input type='hidden' name='KEY' value='$key' />
			</form>
			</td>
			<td align='center' $col>
			<form method='post' name='cafrm${key}b' action='$ENV{'SCRIPT_NAME'}'>
			<input type='image' name='$Lang::tr{'download ca certificate'}' src='/images/floppy.gif' alt='$Lang::tr{'download ca certificate'}' title='$Lang::tr{'download ca certificate'}' />
			<input type='hidden' name='ACTION' value='$Lang::tr{'download ca certificate'}' />
			<input type='hidden' name='KEY' value='$key' />
			</form>
			</td>
			<td align='center' $col>
			<form method='post' name='cafrm${key}c' action='$ENV{'SCRIPT_NAME'}'>
			<input type='hidden' name='ACTION' value='$Lang::tr{'remove ca certificate'}' />
			<input type='image' name='$Lang::tr{'remove ca certificate'}' src='/images/delete.gif' alt='$Lang::tr{'remove ca certificate'}' title='$Lang::tr{'remove ca certificate'}' />
			<input type='hidden' name='KEY' value='$key' />
			</form>
			</td>
			</tr>
END
;
		}
	}
	print "</table>";

	# If the file contains entries, print Key to action icons
	if ( -f "${General::swroot}/ca/cacert.pem") {
		print <<END
		<table><tr>
		<td class='boldbase'>&nbsp; <b>$Lang::tr{'legend'}:</b></td>
		<td>&nbsp; &nbsp; <img src='/images/info.gif' alt='$Lang::tr{'show certificate'}' /></td>
		<td class='base'>$Lang::tr{'show certificate'}</td>
		<td>&nbsp; &nbsp; <img src='/images/floppy.gif' alt='$Lang::tr{'download certificate'}' /></td>
		<td class='base'>$Lang::tr{'download certificate'}</td>
		</tr></table>
END
;
	}
	my $createCA = -f "${General::swroot}/ca/cacert.pem" ? '' : "<tr><td colspan='3'></td><td><input type='submit' name='ACTION' value='$Lang::tr{'generate root/host certificates'}' /></td></tr>";
	print <<END
	<br>
	<hr />
	<form method='post' enctype='multipart/form-data' action='$ENV{'SCRIPT_NAME'}'>
	<table width='100%' border='0' cellspacing='1' cellpadding='0'>
	$createCA
	<tr>
	<td class='base' nowrap='nowrap'>$Lang::tr{'ca name'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td nowrap='nowrap'><input type='text' name='CA_NAME' value='$cgiparams{'CA_NAME'}' size='15' /> </td>
	<td nowrap='nowrap'><input type='file' name='FH' size='30' /></td>
	<td nowrap='nowrap'><input type='submit' name='ACTION' value='$Lang::tr{'upload ca certificate'}' /></td>
	</tr>
	<tr>
	<td colspan='3'>$Lang::tr{'resetting the vpn configuration will remove the root ca, the host certificate and all certificate based connections'}:</td>
	<td align='right'><input type='submit' name='ACTION' value='$Lang::tr{'remove x509'}' /></td>
	</tr>
	</table>
	</form>
END
;
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();

sub array_unique($) {
	my $array = shift;
	my @unique = ();

	my %seen = ();
	foreach my $e (@$array) {
		next if $seen{$e}++;
		push(@unique, $e);
	}

	return @unique;
}

sub make_algos($$$$$) {
	my ($mode, $encs, $ints, $grps, $pfs) = @_;
	my @algos = ();

	foreach my $enc (@$encs) {
		foreach my $int (@$ints) {
			foreach my $grp (@$grps) {
				my @algo = ($enc);

				if ($mode eq "ike") {
					push(@algo, $int);

					if ($grp =~ m/^e(.*)$/) {
						push(@algo, "ecp$1");
					} elsif ($grp =~ m/curve25519/) {
						push(@algo, "$grp");
					} else {
						push(@algo, "modp$grp");
					}

				} elsif ($mode eq "esp" && $pfs) {
					my $is_aead = ($enc =~ m/[cg]cm/);

					if (!$is_aead) {
						push(@algo, $int);
					}

					if ($grp eq "none") {
						# noop
					} elsif ($grp =~ m/^e(.*)$/) {
						push(@algo, "ecp$1");
					} elsif ($grp =~ m/curve25519/) {
						push(@algo, "$grp");
					} else {
						push(@algo, "modp$grp");
					}
				}

				push(@algos, join("-", @algo));
			}
		}
	}

	return &array_unique(\@algos);
}

sub make_subnets($) {
	my $subnets = shift;

	my @nets = split(/\|/, $subnets);
	my @cidr_nets = ();
	foreach my $net (@nets) {
		my $cidr_net = &General::ipcidr($net);
		push(@cidr_nets, $cidr_net);
	}

	return join(",", @cidr_nets);
}
