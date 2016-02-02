#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2016  Alexander Marx alexander.marx@ipfire.org                #
#                                                                             #
# This program is free software you can redistribute it and/or modify         #
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
use CGI ':standard';
use URI::Escape;
use HTML::Entities();

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";

#Set Variables
my %voucherhash=();
my %clientshash=();
my %cgiparams=();
my %settings=();
my $voucherout="${General::swroot}/captive/voucher_out";
my $clients="${General::swroot}/captive/clients";
my $settingsfile="${General::swroot}/captive/settings";
my $redir=0;
my $errormessage;
my $url=param('redirect');

#Create /var/ipfire/captive/clients if not exist
unless (-f $clients){ system("touch $clients"); }

#Get GUI variables
&getcgihash(\%cgiparams);

#Read settings
&General::readhash("$settingsfile", \%settings) if(-f $settingsfile);

#Actions
if ($cgiparams{'ACTION'} eq "$Lang::tr{'gpl i accept these terms and conditions'}"){
	my $key = &General::findhasharraykey(\%clientshash);

	#Get Clients IP-Address
	my $ip_address = $ENV{X_FORWARDED_FOR} || $ENV{REMOTE_ADDR} ||"";

	#Ask arp to give the corresponding MAC-Address
	my $mac_address = qx(arp -a|grep $ip_address|cut -d ' ' -f 4);
	$mac_address =~ s/\n+\z//;

	&General::readhasharray("$clients", \%clientshash);

	if (!$errormessage){
		foreach my $i (0 .. 5) { $clientshash{$key}[$i] = "";}

		$clientshash{$key}[0] = $mac_address;			#mac address of actual client
		$clientshash{$key}[1] = $ip_address;			#ip address of actual client
		$clientshash{$key}[2] = time();					#actual time in unix seconds (timestamp of first conenction)
		$clientshash{$key}[3] = $settings{'EXPIRE'};	#Expire time in seconds (1day, 1 week ....)
		$clientshash{$key}[4] = $Lang::tr{'Captive auth_lic'};	#Type of license (license or voucher)
		$clientshash{$key}[5] = '';

		&General::writehasharray("$clients", \%clientshash);
		system("/usr/local/bin/captivectrl");
		&General::log("Captive", "Internet Access granted via license-agreement for $ip_address until $clientshash{$key}[3]");
		$redir=1;
	}	
}

if ($cgiparams{'ACTION'} eq "$Lang::tr{'Captive activate'}"){
	my $ip_address;
	my $mac_address;

	#Convert voucherinput to uppercase
	$cgiparams{'VOUCHER'} = uc $cgiparams{'VOUCHER'};
	#Get Clients IP-Address
	$ip_address = $ENV{X_FORWARDED_FOR} || $ENV{REMOTE_ADDR} ||"";
	#Ask arp to give the corresponding MAC-Address
	$mac_address = qx(arp -a|grep $ip_address|cut -d ' ' -f 4);
	$mac_address =~ s/\n+\z//;
	#Check if voucher is valid and write client to clients file, delete voucher from voucherout
	&General::readhasharray("$voucherout", \%voucherhash);
	&General::readhasharray("$clients", \%clientshash);
	foreach my $key (keys %voucherhash) {
		if($voucherhash{$key}[1] eq $cgiparams{'VOUCHER'}){
			#Voucher valid, write to clients, then delete from voucherout
			my $key1 = &General::findhasharraykey(\%clientshash);
			foreach my $i (0 .. 5) { $clientshash{$key1}[$i] = "";}

			$clientshash{$key1}[0] = $mac_address;
			$clientshash{$key1}[1] = $ip_address;
			$clientshash{$key1}[2] = time();
			$clientshash{$key1}[3] = $voucherhash{$key}[2];
			$clientshash{$key1}[4] = $cgiparams{'VOUCHER'};
			$clientshash{$key1}[5] = HTML::Entities::decode_entities($voucherhash{$key}[3]);

			&General::writehasharray("$clients", \%clientshash);
			&General::log("Captive", "Internet Access granted via voucher no. $clientshash{$key1}[4] for $ip_address until $clientshash{$key}[3] Remark: $clientshash{$key1}[7]");

			delete $voucherhash{$key};
			&General::writehasharray("$voucherout", \%voucherhash);
			last;
		}
	}
	system("/usr/local/bin/captivectrl");
	$redir=1;
}

if($redir == 1){
	sleep(4);
	print "Status: 302 Moved Temporarily\n";
	print "Location: $url\n";
	print "Connection: close\n";
	print "\n";
	exit 0;
}

#Open HTML Page, load header and css
&head();
&error();
&start();

#Functions
sub start(){
	if ($settings{'AUTH'} eq 'VOUCHER'){
		&voucher();
	}else{
		&agb();
	}
}

sub error(){
	if ($errormessage){
		print "<div id='title'><br>$errormessage<br></diV>";
	}
}

sub head(){
print<<END
Content-type: text/html\n\n
<html> 
	<head>
		<meta charset="utf-8">
		<title>$settings{'TITLE'}</title>
		<link href="../assets/captive.css" type="text/css" rel="stylesheet">
	</head>
END
;
}

sub agb(){
print<<END
	<body>
	<center>
		<div class="title">
			<h1>$settings{'TITLE'}
		</div>
		<br>
		<div class="agb">
		<textarea style="width:100%;" rows='40'>
END
;
&getagb();
print<<END
		</textarea>
			<center>
				<form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<br><input type='hidden' name='redirect' value ='$url'><input type='submit' name='ACTION' value="$Lang::tr{'gpl i accept these terms and conditions'}"/>
				</form>
			</center>
		</div>
	</center>
	</body>
	</html>
END
;
}

sub voucher(){
	print<<END
	<body>
	<center>
		<div class="title">
			<h1>LOGIN</h1>
		</div>
		<br>
		<div class="login">
END
;

print<<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<center>
				<table>
					<tr>
						<td>
							<b>$Lang::tr{'Captive voucher'}</b>&nbsp<input type='text' maxlength="8" size='10' style="font-size: 24px;font-weight: bold;" name='VOUCHER'>
						</td>
						<td>
							<input type='submit' name='ACTION' value="$Lang::tr{'Captive activate'}"/>
						</td>
					</tr>
				</table>
		</form>
		</div>
		<br>
		<div class="agb">
			<textarea style="width:100%;" rows='40'>
END
;
&getagb();
print<<END
			</textarea>
			<br><br>
		</div>
	</body>
	</html>
END
;
}

sub getcgihash {
	my ($hash, $params) = @_;
	my $cgi = CGI->new ();
	$hash->{'__CGI__'} = $cgi;
	return if ($ENV{'REQUEST_METHOD'} ne 'POST');
	if (!$params->{'wantfile'}) {
		$CGI::DISABLE_UPLOADS = 1;
		$CGI::POST_MAX        = 1024 * 1024;
	} else {
		$CGI::POST_MAX = 10 * 1024 * 1024;
	}
	$cgi->referer() =~ m/^http?\:\/\/([^\/]+)/;
	my $referer = $1;
	$cgi->url() =~ m/^http?\:\/\/([^\/]+)/;
	my $servername = $1;
	return if ($referer ne $servername);

	### Modified for getting multi-vars, split by |
	my %temp = $cgi->Vars();
        foreach my $key (keys %temp) {
		$hash->{$key} = $temp{$key};
		$hash->{$key} =~ s/\0/|/g;
		$hash->{$key} =~ s/^\s*(.*?)\s*$/$1/;
        }

	if (($params->{'wantfile'})&&($params->{'filevar'})) {
		$hash->{$params->{'filevar'}} = $cgi->upload
						($params->{'filevar'});
	}
	return;
}

sub getagb(){
	open( my $handle, "<:utf8", "/var/ipfire/captive/agb.txt" ) or die("$!");
		while(<$handle>){
			$_ = HTML::Entities::decode_entities($_);
			print $_;
		}
	close( $handle );
}
