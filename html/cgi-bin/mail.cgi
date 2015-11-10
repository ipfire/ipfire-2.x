#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2015  IPFire Team  <alexander.marx@ipfire.org>                #
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
 
use MIME::Lite;
 
#enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

#Initialize variables and hashes
my $dmafile="${General::swroot}/dma/dma.conf";
my $authfile="${General::swroot}/dma/auth.conf";
my $mailfile="${General::swroot}/dma/mail.conf";
my %dma=();
my %auth=();
my %mail=();
my %mainsettings=();
my %cgiparams=();
my $errormessage='';

#Read all parameters for site
&Header::getcgihash(\%cgiparams);
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

#Show Headers
&Header::showhttpheaders();

#Check configfiles
if ( -f $dmafile){
	open (FILE, "<", $dmafile) or die $!;
	foreach my $line (<FILE>) {
		$line =~ m/^([A-Z]+)\s+?(.*)?$/;
		my $key = $1;
		my $val = $2;
		$dma{$key}=$val;
	}
}else{
	open(FILE, ">$dmafile") or die $!;
}
close FILE;

if (exists $dma{'AUTHPATH'}){
	open (FILE, "<", $dma{'AUTHPATH'}) or die "$dma{'AUTHPATH'} nicht gefunden $! ";
	my $authline;
	foreach my $line (<FILE>) {
		$authline = $line;
	}
	my @part1 = split(/\|/,$authline);
	my @part2 = split(/\:/,$part1[1]);
	$auth{'AUTHNAME'} = $part1[0];
	$auth{'AUTHHOST'} = $part2[0];
	$auth{'AUTHPASS'} = $part2[1];
}

if ( -f $mailfile){
	&General::readhash($mailfile, \%mail);
}

#ACTIONS
if ($cgiparams{'ACTION'} eq "$Lang::tr{'save'}"){ #SaveButton on configsite
	#Check fields
	if ($cgiparams{'USEMAIL'} eq 'on'){
		$errormessage=&checkmailsettings;
	}else{
		$cgiparams{'txt_mailserver'}='';
		$cgiparams{'txt_mailport'}='';
		$cgiparams{'txt_mailuser'}='';
		$cgiparams{'txt_mailpass'}='';
		$cgiparams{'mail_tls'}='';
		$cgiparams{'txt_mailsender'}='';
		$cgiparams{'txt_recipient'}='';
	}
	if(!$errormessage){
		#clear hashes
		%auth=();
		%dma=();
		%mail=();

		#clear configfiles
		open (TXT, ">$dmafile") or die("Could not open /var/ipfire/dma/dma.conf: $!\n");
		open (TXT1, ">$authfile") or die("Could not open /var/ipfire/dma/auth.conf: $!\n");
		open (TXT2, ">$mailfile") or die("Could not open /var/ipfire/dma/mail.conf: $!\n");
		close TXT2;

		#Fill hashes with actual values
		$mail{'USEMAIL'}		= $cgiparams{'USEMAIL'};
		$mail{'SENDER'} 		= $cgiparams{'txt_mailsender'};
		$mail{'RECIPIENT'}		= $cgiparams{'txt_recipient'};

		if ($cgiparams{'txt_mailuser'} && $cgiparams{'txt_mailpass'}) {
			$auth{'AUTHNAME'}		= $cgiparams{'txt_mailuser'};
			$auth{'AUTHPASS'}		= $cgiparams{'txt_mailpass'};
			$auth{'AUTHHOST'}		= $cgiparams{'txt_mailserver'};
			print TXT1 "$auth{'AUTHNAME'}|$auth{'AUTHHOST'}:$auth{'AUTHPASS'}\n";
		}

		$dma{'SMARTHOST'}		= $cgiparams{'txt_mailserver'};
		$dma{'PORT'}			= $cgiparams{'txt_mailport'};
		$dma{'STARTTLS'}		= '' if ($cgiparams{'mail_tls'});
		$dma{'SECURETRANSFER'}	= '' if exists $dma{'STARTTLS'};
		$dma{'SPOOLDIR'}		= "/var/spool/dma";
		$dma{'FULLBOUNCE'}		= '';
		$dma{'MAILNAME'}		= "$mainsettings{'HOSTNAME'}.$mainsettings{DOMAINNAME}";
		$dma{'AUTHPATH'}		= "$authfile" if exists $auth{'AUTHNAME'};

		#Create new configfiles
		&General::writehash("$mailfile", \%mail);
		while ( ($k,$v) = each %dma ) {
			print TXT "$k $v\n";
		}
		close TXT;
		close TXT1;
		close TXT2;

	}else{
		$cgiparams{'update'}='on';
		&configsite;
	}
}
if ($cgiparams{'ACTION'} eq "$Lang::tr{'email testmail'}"){ #Testmail button on configsite
	&testmail;
}

#Show site
&configsite;

#FUNCTIONS
sub configsite{
	

	#If update set fieldvalues new
	if($cgiparams{'update'} eq 'on'){
		$mail{'USEMAIL'}	= 'on';
		$mail{'SENDER'} 	=  $cgiparams{'txt_mailsender'};
		$mail{'RECIPIENT'}	=  $cgiparams{'txt_recipient'};
		$dma{'SMARTHOST'} 	= $cgiparams{'txt_mailserver'};
		$dma{'PORT'} 		= $cgiparams{'txt_mailport'};
		$auth{'AUTHNAME'} 	= $cgiparams{'txt_mailuser'};
		$auth{'AUTHHOST'}	= $cgiparams{'txt_mailserver'};
		$auth{'AUTHPASS'} 	= $cgiparams{'txt_mailpass'};
		$dma{'STARTTLS'}	= $cgiparams{'mail_tls'};
	}
	#find preselections
	$checked{'usemail'}{$mail{'USEMAIL'}}	= 'CHECKED';
	$checked{'mail_tls'}{'on'}				= 'CHECKED' if exists $dma{'STARTTLS'};
	
	#Open site
	&Header::openpage($Lang::tr{'email settings'}, 1, '');
	&Header::openbigbox('100%', 'center');
	&error;
	&info;
	&Header::openbox('100%', 'left', $Lang::tr{'email config'});
	
	#### JAVA SCRIPT ####
	print<<END;
<script>
	\$(document).ready(function() {
		// Show/Hide elements when USEMAIL checkbox is checked.
		if (\$("#MAIL").attr("checked")) {
			\$(".MAILSRV").show();
		} else {
			\$(".MAILSRV").hide();
		}

		// Toggle MAIL elements when "USEMAIL" checkbox is clicked
		\$("#MAIL").change(function() {
			\$(".MAILSRV").toggle();
		});
	});
</script>
END
	##### JAVA SCRIPT END ####
	my $col="style='background-color:$color{'color22'}'";
	print<<END;
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table style='width:100%' border='0'>
	<tr>
		<th colspan='3'></th>
	</tr>
	<tr>
		<td style='width:24em'>$Lang::tr{'email usemail'}</td>
		<td><label><input type='checkbox' name='USEMAIL' id='MAIL' $checked{'usemail'}{'on'}></label></td>
		<td></td>
	</tr>
	</table><br>

	<div class="MAILSRV">
		<table style='width:100%;'>
		<tr>
			<td>$Lang::tr{'email mailsender'}<img src='/blob.gif' alt='*' /></td>
			<td><input type='text' name='txt_mailsender' value='$mail{'SENDER'}' style='width:22em;'></td>
		</tr>
		<tr>
			<td>$Lang::tr{'email mailrcpt'}<img src='/blob.gif' alt='*' /></td>
			<td><input type='text' name='txt_recipient' value='$mail{'RECIPIENT'}' style='width:22em;'></td>
		</tr>
		<tr>
			<td style='width:24em'>$Lang::tr{'email mailaddr'}<img src='/blob.gif' alt='*' /></td>
			<td><input type='text' name='txt_mailserver' value='$dma{'SMARTHOST'}' style='width:22em;'></td>
		</tr>
		<tr>
			<td>$Lang::tr{'email mailport'}<img src='/blob.gif' alt='*' /></td>
			<td><input type='text' name='txt_mailport' value='$dma{'PORT'}' size='3'></td>
		</tr>
		<tr>
			<td>$Lang::tr{'email mailuser'}</td>
			<td><input type='text' name='txt_mailuser' value='$auth{'AUTHNAME'}' style='width:22em;'></td>
		</tr>
		<tr>
			<td>$Lang::tr{'email mailpass'}</td>
			<td><input type='password' name='txt_mailpass' value='$auth{'AUTHPASS'}' style='width:22em;' ></td>
		</tr>
		<tr>
			<td>$Lang::tr{'email tls'}</td>
			<td><input type='checkbox' name='mail_tls' $checked{'mail_tls'}{'on'}></td>
		</tr>
END
		if (! -z $dmafile && $mail{'USEMAIL'} eq 'on' && !$errormessage){
			print "<tr>";
			print "<td></td>";
			print "<td><input type='submit' name='ACTION' value='$Lang::tr{'email testmail'}'></td>";
			print "</tr>";
		}
		print<<END;;
		<tr>
			<td colspan='2'>&nbsp;</td>
		</tr>
		</table>
	</div>

	<table style='width:100%;'>
	<tr>
		<td colspan='3' display:inline align='right'><input type='submit' name='ACTION' value='$Lang::tr{'save'}'></td>
	</tr>
	</table>
	<br>
	</form>
END
	&Header::closebox();
	&Header::closebigbox();	
	&Header::closepage();
	exit 0;
}

sub checkmailsettings {
	#Check if mailserver is an ip address or a domain
	if ($cgiparams{'txt_mailserver'} =~ /^(\d+)\.(\d+)\.(\d+)\.(\d+)$/){
		if (! &General::validip($cgiparams{'txt_mailserver'})){
			$errormessage.="$Lang::tr{'email invalid mailip'} $cgiparams{'txt_mailserver'}<br>";
		}
	}elsif(! &General::validfqdn($cgiparams{'txt_mailserver'})){
			$errormessage.="$Lang::tr{'email invalid mailfqdn'} $cgiparams{'txt_mailserver'}<br>";
	}
	#Check valid mailserverport
	if($cgiparams{'txt_mailport'} < 1 || $cgiparams{'txt_mailport'} > 65535){
		$errormessage.="$Lang::tr{'email invalid mailport'} $cgiparams{'txt_mailport'}<br>";
	}
	#Check valid sender
	if(! $cgiparams{'txt_mailsender'}){
		$errormessage.="$Lang::tr{'email empty field'} $Lang::tr{'email mailsender'}<br>";
	}else{
		if (! &General::validemail($cgiparams{'txt_mailsender'})){
			$errormessage.="<br>$Lang::tr{'email invalid'} $Lang::tr{'email mailsender'}<br>";
		}
	}
	return $errormessage;
}

sub testmail {
	### Create a new multipart message:
	$msg = MIME::Lite->new(
		From	=> $mail{'SENDER'},
		To		=> $mail{'RECIPIENT'},
		#Cc		=> 'some@other.com, some@more.com',
		Subject	=> 'IPFire Testmail',
		Type	=> 'multipart/mixed'
	);

	### Add parts (each "attach" has same arguments as "new"):
	$msg->attach(
		Type	=> 'TEXT',
		Data	=> "This is the IPFire test mail."
	);

	### Add attachment for testing
	#$msg->attach(
	#	Type     => 'application/txt',
	#	Encoding => 'base64',
	#	Path     => '/var/ipfire/dma/dma.conf',
	#	Filename => 'dma.conf',
	#	Disposition => 'attachment'
	#);

	$msg->send_by_sendmail;
}

sub info {
	if ($infomessage) {
		&Header::openbox('100%', 'left', $Lang::tr{'info messages'});
		print "<class name='base'>$infomessage\n";
		print "&nbsp;</class>\n";
		&Header::closebox();
	}
}

sub error {
	if ($errormessage) {
		&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
		print "<class name='base'>$errormessage\n";
		print "&nbsp;</class>\n";
		&Header::closebox();
	}
}
