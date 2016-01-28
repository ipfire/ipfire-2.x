#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2016  IPFire Team  <alexander.marx@ipfire.org>                #
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
use HTML::Entities();
# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
unless (-e "${General::swroot}/captive/settings")	{ system("touch ${General::swroot}/captive/settings"); }
my %settings=();
my %mainsettings;
my %color;
my %cgiparams=();
my %netsettings=();
my %checked=();
my $errormessage='';
my $voucherout="${General::swroot}/captive/voucher_out";
my $clients="${General::swroot}/captive/clients";
my %voucherhash=();
my %clientshash=();
my $settingsfile="${General::swroot}/captive/settings";

unless (-e $voucherout)	{ system("touch $voucherout"); }

&Header::getcgihash(\%cgiparams);

&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);
&General::readhash("$settingsfile", \%settings) if(-f $settingsfile);
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

&Header::showhttpheaders();

#actions
if ($cgiparams{'ACTION'} eq "$Lang::tr{'save'}"){
	#saves the Captiveportal settings to disk 
	$settings{'ENABLE_GREEN'}		= $cgiparams{'ENABLE_GREEN'};
	$settings{'ENABLE_BLUE'}		= $cgiparams{'ENABLE_BLUE'};
	$settings{'AUTH'}				= $cgiparams{'AUTH'};
	$settings{'TIME'}				= $cgiparams{'TIME'};
	$settings{'EXPIRE'}				= $cgiparams{'EXPIRE'};
	$settings{'TITLE'}				= $cgiparams{'TITLE'};
	&General::writehash("$settingsfile", \%settings);
	
	#write Licensetext if defined
	if ($cgiparams{'AGB'}){
		$cgiparams{'AGB'} = &Header::escape($cgiparams{'AGB'});
		open( FH, ">:utf8", "/var/ipfire/captive/agb.txt" ) or die("$!");
		print FH $cgiparams{'AGB'};
		close( FH );
		$cgiparams{'AGB'}="";
	}
	#execute binary to reload firewall rules
	system("/usr/local/bin/captivectrl");
}

if ($cgiparams{'ACTION'} eq "$Lang::tr{'Captive voucherout'}"){
	#generates a voucher and writes it to /var/ipfire/voucher_out	

	#check if we already have a voucher with same code
	&General::readhasharray("$voucherout", \%voucherhash);
	foreach my $key (keys %voucherhash) {
		if($voucherhash{$key}[1] eq $cgiparams{'CODE'}){
			$errormessage=$Lang::tr{'Captive err doublevoucher'};
			last;
		}
	}

	#if no error detected, write to disk
	if (!$errormessage){
		my $date=time(); #seconds in utc

		#first get new key from hash
		my $key=&General::findhasharraykey (\%voucherhash);
		#initialize all fields with ''
		foreach my $i (0 .. 4) { $voucherhash{$key}[$i] = "";}
		#define fields
		$voucherhash{$key}[0] = $date;
		$voucherhash{$key}[1] = $cgiparams{'CODE'};
		$voucherhash{$key}[2] = $settings{'TIME'};
		$voucherhash{$key}[3] = $settings{'EXPIRE'};
		$voucherhash{$key}[4] = &Header::escape($cgiparams{'REMARK'});
		#write values to disk
		&General::writehasharray("$voucherout", \%voucherhash);

		#now prepare log entry, get expiring date for voucher and decode remark for logfile
		my $expdate=localtime(time()+$voucherhash{$key}[3]);
		my $rem=HTML::Entities::decode_entities($voucherhash{$key}[4]);

		#write logfile entry
		&General::log("Captive", "Generated new voucher $voucherhash{$key}[1] $voucherhash{$key}[2] hours valid expires on $expdate remark $rem");
	}
}

if ($cgiparams{'ACTION'} eq 'delvoucherout'){
	#deletes an already generated but unused voucher

	#read all generated vouchers
	&General::readhasharray("$voucherout", \%voucherhash);
	foreach my $key (keys %voucherhash) {
		if($cgiparams{'key'} eq $voucherhash{$key}[0]){
			#write logenty with decoded remark
			my $rem=HTML::Entities::decode_entities($voucherhash{$key}[4]);
			&General::log("Captive", "Delete unused voucher $voucherhash{$key}[1] $voucherhash{$key}[2] hours valid expires on $voucherhash{$key}[3] remark $rem");
			#delete line from hash
			delete $voucherhash{$key};
			last;
		}
	}
	#write back hash
	&General::writehasharray("$voucherout", \%voucherhash);
}

if ($cgiparams{'ACTION'} eq 'delvoucherinuse'){
	#delete voucher and connection in use

	#read all active clients
	&General::readhasharray("$clients", \%clientshash);
	foreach my $key (keys %clientshash) {
		if($cgiparams{'key'} eq $clientshash{$key}[0]){
			#prepare log entry with decoded remark
			my $rem=HTML::Entities::decode_entities($clientshash{$key}[7]);
			#write logentry
			&General::log("Captive", "Delete voucher in use $clientshash{$key}[1] $clientshash{$key}[2] hours valid expires on $clientshash{$key}[3] remark $rem - Connection will be terminated");
			#delete line from hash
			delete $clientshash{$key};
			last;
		}
	}
	#write back hash
	&General::writehasharray("$clients", \%clientshash);
	#reload firewallrules to kill connection of client
	system("/usr/local/bin/captivectrl");
}

#open webpage, print header and open box
&Header::openpage($Lang::tr{'Captive menu'}, 1, '');
&Header::openbigbox();

#call error() to see if we have to print an errormessage on website
&error();

#call config() to display the configuration box
&config();

sub getagb(){
	#open textfile from /var/ipfire/captive/agb.txt
	open( my $handle, "<:utf8", "/var/ipfire/captive/agb.txt" ) or die("$!");
		while(<$handle>){
			#read line by line and print on screen
			$cgiparams{'AGB'}.= HTML::Entities::decode_entities($_);
		}
	close( $handle );
}

sub config(){
	#prints the config box on the website
	&Header::openbox('100%', 'left', $Lang::tr{'Captive config'});
	print <<END
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n
		<table width='100%' border="0">
		<tr>
END
;
	#check which parameters have to be enabled (from settings file)
	$checked{'ENABLE_GREEN'}{'off'} = '';
	$checked{'ENABLE_GREEN'}{'on'} = '';
	$checked{'ENABLE_GREEN'}{$settings{'ENABLE_GREEN'}} = "checked='checked'";
	
	$checked{'ENABLE_BLUE'}{'off'} = '';
	$checked{'ENABLE_BLUE'}{'on'} = '';
	$checked{'ENABLE_BLUE'}{$settings{'ENABLE_BLUE'}} = "checked='checked'";

	if ($netsettings{'GREEN_DEV'}){
		print "<td width='30%'>$Lang::tr{'Captive active on'} <font color='$Header::colourgreen'>Green</font></td><td><input type='checkbox' name='ENABLE_GREEN' $checked{'ENABLE_GREEN'}{'on'} /></td></tr>";
	}
	if ($netsettings{'BLUE_DEV'}){
		print "<td width='30%'>$Lang::tr{'Captive active on'} <font color='$Header::colourblue'>Blue</font></td><td><input type='checkbox' name='ENABLE_BLUE' $checked{'ENABLE_BLUE'}{'on'} /></td></tr>";
	}
	
	print<<END
		</tr>
		<tr>
			<td>
				$Lang::tr{'Captive authentication'}
			</td>
			<td>
				<select name='AUTH' style='width:8em;'>
END
;
	print "<option value='LICENSE' ";
	print " selected='selected'" if ($settings{'AUTH'} eq 'LICENSE');
	print ">$Lang::tr{'Captive auth_lic'}</option>";
	
	print "<option value='VOUCHER' ";
	print " selected='selected'" if ($settings{'AUTH'} eq 'VOUCHER');
	print ">$Lang::tr{'Captive auth_vou'}</option>";
	
	print<<END
				</select>	
			</td>
		</tr>
		<tr>
			<td>
				$Lang::tr{'Captive time'}
			</td>
			<td>
				<select name='TIME' style='width:8em;'>
END
;
	print "<option value='nolimit' ";
	print " selected='selected'" if ($settings{'TIME'} eq 'nolimit');
	print ">$Lang::tr{'Captive nolimit'}</option>";

	print "<option value='1' ";
	print " selected='selected'" if ($settings{'TIME'} eq '1');
	print ">1</option>";
	
	print "<option value='3' ";
	print " selected='selected'" if ($settings{'TIME'} eq '3');
	print ">3</option>";
	
	print "<option value='8' ";
	print " selected='selected'" if ($settings{'TIME'} eq '8');
	print ">8</option>";
	
	
print<<END
			</td>
		</tr>
		<tr>
			<td>
				$Lang::tr{'Captive vouchervalid'}
			</td>
			<td>
				<select name='EXPIRE' style='width:8em;'>
END
;
	print "<option value='86400' ";
	print " selected='selected'" if ($settings{'EXPIRE'} eq '86400');
	print ">$Lang::tr{'Captive 1day'}</option>";

	print "<option value='604800' ";
	print " selected='selected'" if ($settings{'EXPIRE'} eq '604800');
	print ">$Lang::tr{'Captive 1week'}</option>";
	
	print "<option value='2592000' ";
	print " selected='selected'" if ($settings{'EXPIRE'} eq '2592000');
	print ">$Lang::tr{'Captive 1month'}</option></td></tr>";

print<<END
		<tr>
		<td><br>
			$Lang::tr{'Captive title'}
		</td>
		<td><br>
			<input type='text' name='TITLE' value="$settings{'TITLE'}" size='40'>
		</td>
END
;

	if($settings{'AUTH'} eq 'LICENSE'){ &agbbox();}
print<<END
		<tr>
			<td>
			</td>
			<td align='right'>
			<input type='submit' name='ACTION' value="$Lang::tr{'save'}"/>
			</td>
		</tr>
		</table>
		<br><br>
END
;
	print "</form>";
	&Header::closebox();

	#if settings is set to use vouchers, the voucher part has to be displayed
	if ($settings{'AUTH'} eq 'VOUCHER'){
		&voucher();
	}else{
		#otherwise we show the licensepart
		&show_license_connections();
	}
}

sub agbbox(){
	&getagb();
print<<END
	<tr>
		<td>
			License agreement
		</td>
		<td>
			<br>
			<textarea cols="50" rows="10" name="AGB">$cgiparams{'AGB'}</textarea>
		</td>
	</tr>
END
;
}

sub gencode(){
	#generate a random code only letters from A-Z except 'O'  and 0-9
	my @chars = ("A".."N", "P".."Z", "0".."9");
	my $randomstring;
	$randomstring .= $chars[rand @chars] for 1..8;
	return $randomstring;
}

sub voucher(){
	#show voucher part
	my $expire;
	&Header::openbox('100%', 'left', $Lang::tr{'Captive voucher'});
print<<END
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table class='tbl'>
	<tr>
		<th align='center' width='30%'>$Lang::tr{'Captive voucher'}</th><th align='center' width='15%'>$Lang::tr{'hours'}</th><th th align='center' width='15%'>$Lang::tr{'Captive expire'}</th></tr>
END
;
	if ($settings{'EXPIRE'} eq '86400') { $expire = $Lang::tr{'Captive 1day'};}
	if ($settings{'EXPIRE'} eq '604800') { $expire = $Lang::tr{'Captive 1week'};}
	if ($settings{'EXPIRE'} eq '2592000') { $expire = $Lang::tr{'Captive 1month'};}
	if ($settings{'TIME'} eq 'nolimit') { $settings{'TIME'} = $Lang::tr{'Captive nolimit'};}
	$cgiparams{'CODE'} = &gencode();
	print "<tr><td><center><b><font size='20'>$cgiparams{'CODE'}</font></b></center></td><td><center><b><font size='5'>$settings{'TIME'}</font></b></center></td><td><center><b><font size='5'>$expire</font></b></center></td></tr>";
	print "<tr><td colspan='3'><br>$Lang::tr{'remark'}<input type='text' name='REMARK' align='left' size='60' style='font-size: 22px;'></td></tr>";
	print "</table><br>";
	print "<center><input type='submit' name='ACTION' value='$Lang::tr{'Captive voucherout'}'><input type='hidden' name='CODE' value='$cgiparams{'CODE'}'</center></form>";
	&Header::closebox();
	if (! -z $voucherout) { &show_voucher_out();}
	if (! -z $clients) { &show_voucher_in_use();}
}

sub show_license_connections(){
	#if there are active clients, show the box with active connections
	return if ( -z $clients || ! -f $clients );
	my $count=0;
	my $col;
	&Header::openbox('100%', 'left', $Lang::tr{'Captive voactive'});
print<<END
		<center><table class='tbl'>
		<tr>
			<th align='center' width='15%'><font size='1'>$Lang::tr{'Captive mac'}</th><th align='center' width='15%'>$Lang::tr{'Captive ip'}</th><th align='center' width='15%'>$Lang::tr{'Captive voucher'}</th><th th align='center' width='15%'>$Lang::tr{'Captive activated'}</th><th th align='center' width='15%'>$Lang::tr{'Captive expire'}</th><th th align='center' width='15%'>$Lang::tr{'delete'}</th></tr>
END
;
	#read all clients from hash and show table
	&General::readhasharray("$clients", \%clientshash);
	foreach my $key (keys %clientshash){
		my ($sec, $min, $hour, $mday, $mon, $year) = localtime($clientshash{$key}[6]);
		my ($secx,$minx,$hourx) = localtime($clientshash{$key}[6]+($clientshash{$key}[5]*3600));
		$mon = '0'.++$mon if $mon<10;
		$min = '0'.$min if $min<10;
		$hour = '0'.$hour if $hour<10;
		$year=$year+1900;
		if ($count % 2){
			print" <tr>";
			$col="bgcolor='$color{'color20'}'";
		}else{
			$col="bgcolor='$color{'color22'}'";
			print" <tr>";
		}
		print "<td $col><center>$clientshash{$key}[0]</td><td $col><center>$clientshash{$key}[1]</td><td $col><center>$clientshash{$key}[4]</td><td $col><center>$mday.$mon.$year ";
		printf("%02d",$hour);
		print ":";
		printf("%02d",$min);
		print "</center></td><td $col><center>$mday.$mon.$year ";
		printf("%02d",$hourx);
		print ":";
		printf("%02d",$minx);
		print "</td><td $col><form method='post'><center><input type='image' src='/images/delete.gif' align='middle' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' /><form method='post'><input type='hidden' name='ACTION' value='delvoucherinuse' /><input type='hidden' name='key' value='$clientshash{$key}[0]' /></form></tr>";
		$count++;
	}
	
	print "</table>";
	&Header::closebox();
}

sub show_voucher_out(){
	#if there are already generated but unsused vouchers, print a table
	return if ( -z $voucherout);
	my $count=0;
	my $col;
	&Header::openbox('100%', 'left', $Lang::tr{'Captive vout'});
	print<<END
		<center><table class='tbl'>
		<tr>
			<th align='center' width='15%'><font size='1'>$Lang::tr{'date'}</th><th align='center' width='15%'>$Lang::tr{'Captive voucher'}</th><th align='center' width='5%'>$Lang::tr{'hours'}</th><th th align='center' width='15%'>$Lang::tr{'Captive expire'}</th><th align='center'>$Lang::tr{'remark'}</th><th align='center' width='15%'>$Lang::tr{'delete'}</th></tr>
END
;
	&General::readhasharray("$voucherout", \%voucherhash);
	foreach my $key (keys %voucherhash)
	{
		my ($sec, $min, $hour, $mday, $mon, $year) = localtime($voucherhash{$key}[0]);
		my ($secx, $minx, $hourx, $mdayx, $monx, $yearx) = localtime($voucherhash{$key}[0]+$voucherhash{$key}[3]);
		$mon++;
		$year=$year+1900;
		$monx++;
		$yearx=$yearx+1900;
		if ($count % 2){
			print" <tr>";
			$col="bgcolor='$color{'color20'}'";
		}else{
			$col="bgcolor='$color{'color22'}'";
			print" <tr>";
		}
		print "<td $col><center>";
		printf("%02d",$mday);
		print ".";
		printf("%02d",$mon);
		print ".";
		print"$year ";
		
		printf("%02d",$hour);
		print ":";
		printf("%02d",$min);
		print "</td><td $col><center><b>$voucherhash{$key}[1]</b></td><td $col><center>$voucherhash{$key}[2]</td><td $col><center>";
		printf("%02d",$mdayx);
		print ".";
		printf("%02d",$monx);
		print ".";
		print"$yearx ";
		
		printf("%02d",$hourx);
		print ":";
		printf("%02d",$minx);
		print "</td>";
		$voucherhash{$key}[4] = HTML::Entities::decode_entities($voucherhash{$key}[4]);
		print "<td $col align='center'>$voucherhash{$key}[4]</td>";
		print "<td $col><form method='post'><center><input type='image' src='/images/delete.gif' align='middle' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' /><form method='post'><input type='hidden' name='ACTION' value='delvoucherout' /><input type='hidden' name='key' value='$voucherhash{$key}[0]' /></form></tr>";
		$count++;
	}
	
	print "</table>";
	&Header::closebox();
}

sub show_voucher_in_use(){
	#if there are active clients which use vouchers show table
	return if ( -z $clients || ! -f $clients );
	my $count=0;
	my $col;
	&Header::openbox('100%', 'left', $Lang::tr{'Captive voactive'});
print<<END
	<center><table class='tbl'>
		<tr>
			<th align='center' width='15%'><font size='1'>$Lang::tr{'Captive mac'}</th><th align='center' width='15%'>$Lang::tr{'Captive ip'}</th><th align='center' width='15%'>$Lang::tr{'Captive voucher'}</th><th th align='center' width='15%'>$Lang::tr{'Captive activated'}</th><th th align='center' width='15%'>$Lang::tr{'Captive expire'}</th><th th align='center' width='15%'>$Lang::tr{'delete'}</th></tr>
END
;
	&General::readhasharray("$clients", \%clientshash);
	foreach my $key (keys %clientshash)
	{
			my ($sec, $min, $hour, $mday, $mon, $year) = localtime($clientshash{$key}[6]);
			my ($secx,$minx,$hourx) = localtime($clientshash{$key}[6]+($clientshash{$key}[5]*3600));
			$mon = '0'.++$mon if $mon<10;
			$min = '0'.$min if $min<10;
			$hour = '0'.$hour if $hour<10;
			$year=$year+1900;
			if ($count % 2){
				print" <tr>";
				$col="bgcolor='$color{'color20'}'";
			}else{
				$col="bgcolor='$color{'color22'}'";
				print" <tr>";
			}
			print "<td $col><center>$clientshash{$key}[0]</td><td $col><center>$clientshash{$key}[1]</td><td $col><center>$clientshash{$key}[4]</td><td $col><center>$mday.$mon.$year ";
			printf("%02d",$hour);
			print ":";
			printf("%02d",$min);
			print "</center></td><td $col><center>$mday.$mon.$year ";
			printf("%02d",$hourx);
			print ":";
			printf("%02d",$minx);
			print "</td><td $col><form method='post'><center><input type='image' src='/images/delete.gif' align='middle' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' /><form method='post'><input type='hidden' name='ACTION' value='delvoucherinuse' /><input type='hidden' name='key' value='$clientshash{$key}[0]' /></form></tr>";
			$count++;
	}
	
	print "</table>";
	&Header::closebox();
}

sub error{
	#if an errormessage exits, show a box with errormessage
	if ($errormessage) {
		&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
		print "<class name='base'>$errormessage\n";
		print "&nbsp;</class>\n";
		&Header::closebox();
	}
}

&Header::closebigbox();
&Header::closepage();
