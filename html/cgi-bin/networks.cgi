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
# Copyright (C) 2003-09-22 Darren Critchley <darrenc@telus.net>
#
# $Id: networks.cgi,v 1.2.2.3 2005/04/29 23:37:06 franck78 Exp $
#

use strict;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %netsettings=();
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

my @networks=();
my $filename = "${General::swroot}/firewall/customnetworks";
&setup_default_networks();

&Header::getcgihash(\%cgiparams);

if ($cgiparams{'ACTION'} eq $Lang::tr{'add'}){

	&validateparams();
	unless($errormessage){
		$key++; # Add one to last sequence number
		open(FILE,">>$filename") or die 'Unable to open custom networks file.';
		flock FILE, 2;
		print FILE "$key,$cgiparams{'NAME'},$cgiparams{'IPADDRESS'},$cgiparams{'NETMASK'}\n";
		close(FILE);
		&General::log("$Lang::tr{'network added'}: $cgiparams{'NAME'}");
		undef %cgiparams;
	}
}

if ($cgiparams{'ACTION'} eq $Lang::tr{'update'})
{
	&validateparams();
	# Darren Critchley - If there is an error don't waste any more processing time
	if ($errormessage) { $cgiparams{'ACTION'} = $Lang::tr{'edit'}; goto UPD_ERROR; }

	unless($errormessage){
		open(FILE, $filename) or die 'Unable to open custom networks file.';
		my @current = <FILE>;
		close(FILE);
		open(FILE, ">$filename") or die 'Unable to open config file.';
		flock FILE, 2;
		foreach my $line (@current) {
			chomp($line);
			my @temp = split(/\,/,$line);
			if ($cgiparams{'KEY'} eq $temp[0]) {
				print FILE "$cgiparams{'KEY'},$cgiparams{'NAME'},$cgiparams{'IPADDRESS'},$cgiparams{'NETMASK'}\n";
			} else {
				print FILE "$line\n";
			}
		}
		close(FILE);
		&General::log("$Lang::tr{'network updated'}: $cgiparams{'NAME'}");
		undef %cgiparams;
	}
UPD_ERROR:
}

if ($cgiparams{'ACTION'} eq $Lang::tr{'edit'})
{
	open(FILE, "$filename") or die 'Unable to open custom networks file.';
	my @current = <FILE>;
	close(FILE);

	unless ($errormessage)
	{
		foreach my $line (@current)
		{
			chomp($line);
			my @temp = split(/\,/,$line);
			if ($cgiparams{'KEY'} eq $temp[0]) {
				$cgiparams{'NAME'} = $temp[1];
				$cgiparams{'IPADDRESS'} = $temp[2];
				$cgiparams{'NETMASK'} = $temp[3];
			}
			
		}
	}
}

if ($cgiparams{'ACTION'} eq $Lang::tr{'remove'})
{
	open(FILE, $filename) or die 'Unable to open custom networks file.';
	my @current = <FILE>;
	close(FILE);

	open(FILE, ">$filename") or die 'Unable to open custom networks file.';
	flock FILE, 2;
	foreach my $line (@current)
	{
		chomp($line);
		if ($line ne '') {		
			my @temp = split(/\,/,$line);
			if ($cgiparams{'KEY'} eq $temp[0]) {
				&General::log("$Lang::tr{'network removed'}: $temp[1]");
			} else {
       	        		print FILE "$temp[0],$temp[1],$temp[2],$temp[3]\n";
			}
		}
	}
	close(FILE);
	undef %cgiparams;
}

if ($cgiparams{'ACTION'} eq $Lang::tr{'reset'})
{
	undef %cgiparams;
}

if ($cgiparams{'ACTION'} eq '')
{
	$cgiparams{'KEY'} = '';
	$cgiparams{'IPADDRESS'} = '';
	$cgiparams{'NETMASK'} = '';
    $cgiparams{'NAME'} = '';
}

&Header::showhttpheaders();

&Header::openpage($Lang::tr{'networks settings'}, 1, '');

&Header::openbigbox('100%', 'LEFT', '', $errormessage);

# DEBUG DEBUG
#&Header::openbox('100%', 'LEFT', 'DEBUG');
#foreach $line (keys %cgiparams) {
#	print "<CLASS NAME='base'>$line = $cgiparams{$line}<BR>";
#}
#print "$ENV{'QUERY_STRING'}\n";
#print "&nbsp;</CLASS>\n";
#&Header::closebox();

if ($errormessage) {
	&Header::openbox('100%', 'LEFT', $Lang::tr{'error messages'});
	print "<CLASS NAME='base'><FONT COLOR='${Header::colourred}'>$errormessage\n</FONT>";
	print "&nbsp;</CLASS>\n";
	&Header::closebox();
}

if ($cgiparams{'ACTION'} eq $Lang::tr{'edit'}){
	&Header::openbox('100%', 'LEFT', "$Lang::tr{'edit network'}:");
} else {
	&Header::openbox('100%', 'LEFT', "$Lang::tr{'add network'}:");
}
print <<END
<FORM METHOD='POST'>
<DIV ALIGN='CENTER'>
<TABLE WIDTH='100%'>
<TR align="center">
	<TD><strong>$Lang::tr{'name'}</strong></TD>
	<TD><strong>$Lang::tr{'ip address'}</strong></TD>
	<TD><strong>$Lang::tr{'netmask'}</strong></TD>
	<TD>&nbsp;</TD>
	<TD>&nbsp;</TD>
	<TD>&nbsp;</TD>
</TR>
<TR align="center">
	<TD>
		<INPUT TYPE='TEXT' NAME='NAME' VALUE='$cgiparams{'NAME'}' SIZE='20' MAXLENGTH='20'>
	</TD>
	<TD>
		<INPUT TYPE='TEXT' NAME='IPADDRESS' VALUE='$cgiparams{'IPADDRESS'}' SIZE='15' MAXLENGTH='15'>
	</TD>
	<TD>
		<INPUT TYPE='TEXT' NAME='NETMASK' VALUE='$cgiparams{'NETMASK'}' SIZE='15' MAXLENGTH='15'>
	</TD>
END
;
if ($cgiparams{'ACTION'} eq $Lang::tr{'edit'}){
#   Darren Critchley - put in next release - author has authorized GPL inclusion
#	print "<TD ALIGN='CENTER'><a href='ipcalc.cgi' target='_blank'>IP Calculator</a></TD>\n";
	print "<TD ALIGN='CENTER'><INPUT TYPE='SUBMIT' NAME='ACTION' VALUE='$Lang::tr{'update'}'></TD>\n";
	print "<INPUT TYPE='HIDDEN' NAME='KEY' VALUE='$cgiparams{'KEY'}'>\n";
	print "<TD ALIGN='CENTER'><INPUT TYPE='SUBMIT' NAME='ACTION' VALUE='$Lang::tr{'reset'}'></TD>\n";
} else {
#   Darren Critchley - put in next release - author has authorized GPL inclusion
#	print "<TD ALIGN='CENTER'><a href='ipcalc.cgi' target='_blank'>IP Calculator</a></TD>\n";
	print "<TD ALIGN='CENTER'><INPUT TYPE='SUBMIT' NAME='ACTION' VALUE='$Lang::tr{'add'}'></TD>\n";
	print "<TD ALIGN='CENTER'><INPUT TYPE='SUBMIT' NAME='ACTION' VALUE='$Lang::tr{'reset'}'></TD>\n";
}
print <<END   
</TR>
</TABLE>
</DIV>
</FORM>
END
;
&Header::closebox();

&Header::openbox('100%', 'LEFT', "$Lang::tr{'custom networks'}:");
print <<END
<DIV ALIGN='CENTER'>
<TABLE WIDTH='100%' ALIGN='CENTER'>
<TR align="center">
	<TD><strong>$Lang::tr{'name'}</strong></TD>
	<TD><strong>$Lang::tr{'ip address'}</strong></TD>
	<TD><strong>$Lang::tr{'netmask'}</strong></TD>
</TR>
END
;
&display_custom_networks();
print <<END
</TABLE>
</DIV>
END
;
&Header::closebox();

&Header::openbox('100%', 'LEFT', "$Lang::tr{'default networks'}:");
print <<END
<DIV ALIGN='CENTER'>
<TABLE WIDTH='100%' ALIGN='CENTER'>
<TR align="center">
	<TD><strong>$Lang::tr{'name'}</strong></TD>
	<TD><strong>$Lang::tr{'ip address'}</strong></TD>
	<TD><strong>$Lang::tr{'netmask'}</strong></TD>
</TR>
END
;
&display_default_networks();
print <<END
</TABLE>
</DIV>
END
;
&Header::closebox();
 
    print "$Lang::tr{'this feature has been sponsored by'} : ";
    print "<A HREF='http://www.kdi.ca/' TARGET='_blank'>Kobelt Development Inc.</A>.\n";

&Header::closebigbox();

&Header::closepage();

sub display_custom_networks
{
	open(FILE, "$filename") or die 'Unable to open networks file.';
	my @current = <FILE>;
	close(FILE);

	my $id = 0;
	foreach $line (@current)
	{
		chomp($line);
		if ($line ne ''){
			my @temp = split(/\,/,$line);
			# Darren Critchley highlight the row we are editing
			if ( $cgiparams{'ACTION'} eq $Lang::tr{'edit'} && $cgiparams{'KEY'} eq $temp[0] ) { 
				print "<TR BGCOLOR='${Header::colouryellow}'>\n";
			} else {
				if ($id % 2) {
					print "<TR BGCOLOR='${Header::table1colour}'>\n"; 
				} else {
	    	       	print "<TR BGCOLOR='${Header::table2colour}'>\n";
				}
			}
			print "<TD>$temp[1]</TD>\n";
			print "<TD ALIGN='CENTER'>$temp[2]</TD>\n";
			print "<TD ALIGN='CENTER'>$temp[3]</TD>\n";
			print <<END
<FORM METHOD='POST' NAME='frm$temp[0]'>
<TD ALIGN='CENTER'>
	<INPUT TYPE='hidden' NAME='ACTION' VALUE='$Lang::tr{'edit'}'>
	<INPUT TYPE='image' NAME='$Lang::tr{'edit'}' src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' width='20' height='20' border='0'>
	<INPUT TYPE='hidden' NAME='KEY' VALUE='$temp[0]'>
</TD>
</FORM>
<FORM METHOD='POST' NAME='frm$temp[0]b'>
<TD ALIGN='CENTER'>
	<INPUT TYPE='hidden' NAME='ACTION' VALUE='$Lang::tr{'remove'}'>
	<INPUT TYPE='image' NAME='$Lang::tr{'remove'}' src='/images/delete.gif' alt='$Lang::tr{'remove'}' title='$Lang::tr{'remove'}' width='20' height='20' border='0'>
	<INPUT TYPE='hidden' NAME='KEY' VALUE='$temp[0]'>
</TD>
</FORM>
END
;
			print "</TR>\n";
			$id++;
		}
	}
}

sub display_default_networks
{
	foreach $line (sort @networks)
	{
		my @temp = split(/\,/,$line);
		if ($id % 2) {
			print "<TR BGCOLOR='${Header::table1colour}'>\n"; 
		} else {
           	print "<TR BGCOLOR='${Header::table2colour}'>\n";
		}
		print "<TD>$temp[0]</TD>\n";
		print "<TD ALIGN='CENTER'>$temp[1]</TD>\n";
		print "<TD ALIGN='CENTER'>$temp[2]</TD>\n";
		print "</TR>\n";
		$id++;
	}
}

sub setup_default_networks
{
	# Get current defined networks (Red, Green, Blue, Orange)
	my $line = "Any,0.0.0.0,0.0.0.0";
	push (@networks, $line);
	$line = "localhost,127.0.0.1,255.255.255.255";
	push (@networks, $line);
	$line = "localnet,127.0.0.0,255.0.0.0";
	push (@networks, $line);
	$line = "Private Network 10.0.0.0,10.0.0.0,255.0.0.0";
	push (@networks, $line);
	$line = "Private Network 172.16.0.0,172.16.0.0,255.240.0.0";
	push (@networks, $line);
	$line = "Private Network 192.168.0.0,192.168.0.0,255.255.0.0";
	push (@networks, $line);
	
	my $red_address=`cat ${General::swroot}/red/local-ipaddress`;
	$line = "Red Address,$red_address,";
	push (@networks, $line);
	
	$line = "Green Address,$netsettings{'GREEN_ADDRESS'},255.255.255.255";
	push (@networks, $line);
	$line = "Green Network,$netsettings{'GREEN_NETADDRESS'},$netsettings{'GREEN_NETMASK'}";
	push (@networks, $line);
	
	if ($netsettings{'ORANGE_DEV'}ne ''){
		$line = "Orange Address,$netsettings{'ORANGE_ADDRESS'},255.255.255.255";
		push (@networks, $line);
		$line = "Orange Network,$netsettings{'ORANGE_NETADDRESS'},$netsettings{'ORANGE_NETMASK'}";
		push (@networks, $line);
	}	
	
	if ($netsettings{'BLUE_DEV'}ne ''){
		$line = "Blue Address,$netsettings{'BLUE_ADDRESS'},255.255.255.255";
		push (@networks, $line);
		$line = "Blue Network,$netsettings{'BLUE_NETADDRESS'},$netsettings{'BLUE_NETMASK'}";
		push (@networks, $line);
	}	
	open(FILE, "${General::swroot}/ethernet/aliases") or die 'Unable to open aliases file.';
	my @current = <FILE>;
	close(FILE);
	my $ctr = 0;
	foreach my $lne (@current)
	{
		if ($lne ne ''){
			chomp($lne);	
			my @temp = split(/\,/,$lne);
			if ($temp[2] eq '') {
				$temp[2] = "Alias $ctr : $temp[0]";
			}
			$line = "$temp[2],$temp[0],";
			push (@networks, $line);
			$ctr++;
		}
	}
}

# Validate Field Entries
sub validateparams 
{
	if ($cgiparams{'NAME'} eq '') {
		$errormessage = $Lang::tr{'nonetworkname'};
		return;
	}
	$cgiparams{'NAME'}=&Header::cleanhtml($cgiparams{'NAME'});
	unless(&General::validip($cgiparams{'IPADDRESS'})){$errormessage = $Lang::tr{'invalid ip'}; }
	unless($errormessage){
		my @tmp = split(/\./,$cgiparams{'IPADDRESS'});
		if ($cgiparams{'NETMASK'} eq '' && $tmp[3] ne '255' && $tmp[3] ne '0'){
			$cgiparams{'NETMASK'} = "255.255.255.255";
		}
	}
	unless(&General::validmask($cgiparams{'NETMASK'})){$errormessage = $Lang::tr{'subnet is invalid'}; }
	
	open(FILE, $filename) or die 'Unable to open custom network file.';
	my @current = <FILE>;
	close(FILE);
	foreach my $line (@current)
	{
		chomp($line);
		if ($line ne '') {
			my @temp = split(/\,/,$line);
			if ($cgiparams{'NAME'} eq $temp[1] && $cgiparams{'KEY'} ne $temp[0]) {
				$errormessage=$Lang::tr{'duplicate name'};
				return;
			}
			$key=$temp[0];
		}
	}
	foreach $line (@networks)
	{
		my @temp = split(/\,/,$line);
			if ($cgiparams{'NAME'} eq $temp[0]) {
				$errormessage=$Lang::tr{'duplicate name'};
				return;
			}
	}
}
