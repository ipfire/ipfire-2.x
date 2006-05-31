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
# $Id: services.cgi,v 1.2.2.3 2005/04/29 23:37:07 franck78 Exp $
#

use strict;

require 'CONFIG_ROOT/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my @icmptypes = &get_icmptypes();

&Header::showhttpheaders();

my %cgiparams=();
my %selected=();
my %checked=();
my $filename = "${General::swroot}/firewall/customservices";
my $key = 0; # used for finding last sequence number used 

# Darren Critchley - vars for setting up sort order
my $sort_col = '1';
my $sort_type = 'a';
my $sort_dir = 'asc';

if ($ENV{'QUERY_STRING'} ne '') {
	my ($item1, $item2, $item3) = split(/\&/,$ENV{'QUERY_STRING'});
	if ($item1 ne '') {
		($junk, $sort_col) = split(/\=/,$item1)
	}
	if ($item2 ne '') {
		($junk, $sort_type) = split(/\=/,$item2)
	}
	if ($item3 ne '') {
		($junk, $sort_dir) = split(/\=/,$item3)
	}
}

$cgiparams{'KEY'} = '';
$cgiparams{'PORTS'} = '';
$cgiparams{'PROTOCOL'} = '6';
$cgiparams{'NAME'} = '';
$cgiparams{'PORT_INVERT'} = 'off';
$cgiparams{'PROTOCOL_INVERT'} = 'off';
$cgiparams{'ICMP'} = 'BLANK';

&Header::getcgihash(\%cgiparams);

if ($cgiparams{'ACTION'} eq $Lang::tr{'add'}){

	&validateparams();
	unless($errormessage){
		$key++; # Add one to last sequence number
		open(FILE,">>$filename") or die 'Unable to open config file.';
		flock FILE, 2;
		print FILE "$key,$cgiparams{'NAME'},$cgiparams{'PORTS'},$cgiparams{'PROTOCOL'},$cgiparams{'PORT_INVERT'},$cgiparams{'PROTOCOL_INVERT'},$cgiparams{'ICMP'}\n";
		close(FILE);
		&General::log("$Lang::tr{'service added'}: $cgiparams{'NAME'}");
		undef %cgiparams;
	}
}

if ($cgiparams{'ACTION'} eq $Lang::tr{'update'})
{
	&validateparams();
	# Darren Critchley - If there is an error don't waste any more processing time
	if ($errormessage) { $cgiparams{'ACTION'} = $Lang::tr{'edit'}; goto UPD_ERROR; }

	unless($errormessage){
		open(FILE, $filename) or die 'Unable to open custom services file.';
		my @current = <FILE>;
		close(FILE);
		my $line;
		open(FILE, ">$filename") or die 'Unable to open config file.';
		flock FILE, 2;
		foreach $line (@current) {
			chomp($line);
			my @temp = split(/\,/,$line);
			if ($cgiparams{'KEY'} eq $temp[0]) {
				print FILE "$cgiparams{'KEY'},$cgiparams{'NAME'},$cgiparams{'PORTS'},$cgiparams{'PROTOCOL'},$cgiparams{'PORT_INVERT'},$cgiparams{'PROTOCOL_INVERT'},$cgiparams{'ICMP'}\n";
			} else {
				print FILE "$line\n";
			}
		}
		close(FILE);
		&General::log("$Lang::tr{'service updated'}: $cgiparams{'NAME'}");
		undef %cgiparams;
	}
UPD_ERROR:
}

if ($cgiparams{'ACTION'} eq $Lang::tr{'edit'})
{
	open(FILE, "$filename") or die 'Unable to open custom services file.';
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
				$cgiparams{'PORTS'} = $temp[2];
				$cgiparams{'PROTOCOL'} = $temp[3];
				$cgiparams{'PORT_INVERT'} = $temp[4];
				$cgiparams{'PROTOCOL_INVERT'} = $temp[5];
				$cgiparams{'ICMP'} = $temp[6];
			}
			
		}
	}
}

if ($cgiparams{'ACTION'} eq $Lang::tr{'remove'})
{
	open(FILE, $filename) or die 'Unable to open custom services file.';
	my @current = <FILE>;
	close(FILE);

	open(FILE, ">$filename") or die 'Unable to open custom services file.';
	flock FILE, 2;
	foreach my $line (@current)
	{
		chomp($line);
		if ($line ne '') {		
			my @temp = split(/\,/,$line);
			if ($cgiparams{'KEY'} eq $temp[0]) {
				&General::log("$Lang::tr{'service removed'}: $temp[1]");
			} else {
       	        		print FILE "$temp[0],$temp[1],$temp[2],$temp[3],$temp[4],$temp[5],$temp[6]\n";
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
	$cgiparams{'PORTS'} = '';
	$cgiparams{'PROTOCOL'} = '6';
    $cgiparams{'NAME'} = '';
	$cgiparams{'PORT_INVERT'} = 'off';
	$cgiparams{'PROTOCOL_INVERT'} = 'off';
	$cgiparams{'ICMP'} = 'BLANK';
}

# Darren Critchley - Bring in the protocols file built from /etc/protocols into hash %protocol
require "${General::swroot}/firewall/protocols.pl";

# Darren Critchley - figure out which protocol is selected
$selected{'PROTOCOL'}{'tcpudp'}= '';
$selected{'PROTOCOL'}{'all'}= '';
foreach $line (keys %protocols) {
#	$selected{'PROTOCOL'}{"$protocols{$line}"}= '';
	$selected{'PROTOCOL'}{$line}= '';
}
$selected{'PROTOCOL'}{$cgiparams{'PROTOCOL'}} = 'SELECTED';

# Darren Critchley - figure out which icmptype is selected
$selected{'ICMP'}{$cgiparams{'ICMP'}} = 'SELECTED';

$checked{'PORT_INVERT'}{'off'} = '';
$checked{'PORT_INVERT'}{'on'} = '';
$checked{'PORT_INVERT'}{$cgiparams{'PORT_INVERT'}} = 'CHECKED';
$checked{'PROTOCOL_INVERT'}{'off'} = '';
$checked{'PROTOCOL_INVERT'}{'on'} = '';
$checked{'PROTOCOL_INVERT'}{$cgiparams{'PROTOCOL_INVERT'}} = 'CHECKED';

&Header::openpage($Lang::tr{'services settings'}, 1, '');

&Header::openbigbox('100%', 'LEFT', '', $errormessage);

# DEBUG DEBUG
#&Header::openbox('100%', 'LEFT', 'DEBUG');
#foreach $line (keys %cgiparams) {
#	print "<CLASS NAME='base'>$line = $cgiparams{$line}<BR>";
#}
#print "$sort_col\n";
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
	&Header::openbox('100%', 'LEFT', "$Lang::tr{'edit service'}:");
} else {
	&Header::openbox('100%', 'LEFT', "$Lang::tr{'add service'}:");
}
# Darren Critchley - Show protocols with TCP, UDP, etc at the top of the list.
print <<END
<FORM METHOD='POST'>
<DIV ALIGN='CENTER'>
<TABLE WIDTH='100%' ALIGN='CENTER'>
<TR align="center">
	<TD><strong>$Lang::tr{'servicename'}</strong></TD>
	<TD ALIGN='RIGHT'><strong>$Lang::tr{'invert'}</strong></TD>
	<TD><strong>$Lang::tr{'ports'}</strong></TD>
	<TD ALIGN='RIGHT'><strong>$Lang::tr{'invert'}</strong></TD>
	<TD><strong>$Lang::tr{'protocol'}</strong></TD>
	<TD>&nbsp;</TD>
	<TD>&nbsp;</TD>
</TR>
<TR align="center">
	<TD>
		<INPUT TYPE='TEXT' NAME='NAME' VALUE='$cgiparams{'NAME'}' SIZE='20' MAXLENGTH='20'>
	</TD>
	<TD ALIGN='RIGHT'>
		<INPUT TYPE='CHECKBOX' NAME='PORT_INVERT' $checked{'PORT_INVERT'}{'on'}>
	</TD>
	<TD>
		<INPUT TYPE='TEXT' NAME='PORTS' VALUE='$cgiparams{'PORTS'}' SIZE='15' MAXLENGTH='11'>
	</TD>
	<TD ALIGN='RIGHT'>
		<INPUT TYPE='CHECKBOX' NAME='PROTOCOL_INVERT' $checked{'PROTOCOL_INVERT'}{'on'}>
	</TD>
    <TD ALIGN='LEFT'>
		<SELECT NAME='PROTOCOL'>
			<OPTION VALUE='tcp' $selected{'PROTOCOL'}{'tcp'}>TCP</OPTION>
			<OPTION VALUE='udp' $selected{'PROTOCOL'}{'udp'}>UDP</OPTION>
			<OPTION VALUE='tcpudp' $selected{'PROTOCOL'}{'tcpudp'}>TCP & UDP</OPTION>
			<OPTION VALUE='all' $selected{'PROTOCOL'}{'all'}>ALL</OPTION>
			<OPTION VALUE='icmp' $selected{'PROTOCOL'}{'icmp'}>ICMP</OPTION>
			<OPTION VALUE='gre' $selected{'PROTOCOL'}{'gre'}>GRE</OPTION>
END
;
foreach $line (sort keys %protocols) {
	# Darren Critchley - do not have duplicates in the list
	if ($protocols{$line} ne '6' && $protocols{$line} ne '17' && $protocols{$line} ne '1' && $protocols{$line} ne '47'){
#		print "<OPTION VALUE='$line' $selected{'PROTOCOL'}{$protocols{$line}}>".uc($line)."</OPTION>\n";
		print "<OPTION VALUE='$line' $selected{'PROTOCOL'}{$line}>".uc($line)."</OPTION>\n";
	}
}
print <<END
		</SELECT>
	</TD>
</TR>
<TR>
	<TD>&nbsp;</TD>
	<TD>&nbsp;</TD>
	<TD>&nbsp;</TD>
	<TD><strong>$Lang::tr{'icmp type'}:</strong></TD>
	<TD ALIGN='LEFT'>
			<SELECT NAME='ICMP'>
				<OPTION VALUE='BLANK' $selected{'ICMP'}{'BLANK'}>Valid ICMP Types</OPTION>
END
;
foreach $line (@icmptypes) {
	if ($cgiparams{'ICMP'} eq $line){
		print "<OPTION VALUE='$line' SELECTED>$line</OPTION>\n";
	} else {
		print "<OPTION VALUE='$line' >$line</OPTION>\n";
	}
}
print <<END
			</SELECT>
	</TD>
</TR>
<TR>
END
;
if ($cgiparams{'ACTION'} eq $Lang::tr{'edit'}){
	print "<TD ALIGN='CENTER'><INPUT TYPE='SUBMIT' NAME='ACTION' VALUE='$Lang::tr{'update'}'></TD>\n";
	print "<INPUT TYPE='HIDDEN' NAME='KEY' VALUE='$cgiparams{'KEY'}'>\n";
	print "<TD ALIGN='CENTER'><INPUT TYPE='SUBMIT' NAME='ACTION' VALUE='$Lang::tr{'reset'}'></TD>\n";
} else {
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

&Header::openbox('100%', 'LEFT', "$Lang::tr{'custom services'}:");
print <<END
<DIV ALIGN='CENTER'>
<TABLE WIDTH='100%' ALIGN='CENTER'>
<TR align="center">
END
;

if ($sort_dir eq 'asc' && $sort_col eq '2') {
	print "<TD WIDTH='25%'><strong><a href='services.cgi?sortcol=2&srtype=a&srtdir=dsc' title='$Lang::tr{'sort descending'}'>$Lang::tr{'servicename'}</a></strong></TD>\n";
} else {
	print "<TD WIDTH='25%'><strong><a href='services.cgi?sortcol=2&srtype=a&srtdir=asc' title='$Lang::tr{'sort ascending'}'>$Lang::tr{'servicename'}</a></strong></TD>\n";
}
if ($sort_dir eq 'asc' && $sort_col eq '3') {
	print "<TD WIDTH='25%'><strong><a href='services.cgi?sortcol=3&srtype=n&srtdir=dsc' title='$Lang::tr{'sort descending'}'>$Lang::tr{'ports'}</a></strong></TD>\n";
} else {
	print "<TD WIDTH='25%'><strong><a href='services.cgi?sortcol=3&srtype=n&srtdir=asc' title='$Lang::tr{'sort ascending'}'>$Lang::tr{'ports'}</a></strong></TD>\n";
}
if ($sort_dir eq 'asc' && $sort_col eq '4') {
	print "<TD WIDTH='25%'><strong><a href='services.cgi?sortcol=4&srtype=a&srtdir=dsc' title='$Lang::tr{'sort descending'}'>$Lang::tr{'protocol'}</a></strong></TD>\n";
} else {
	print "<TD WIDTH='25%'><strong><a href='services.cgi?sortcol=4&srtype=a&srtdir=asc' title='$Lang::tr{'sort ascending'}'>$Lang::tr{'protocol'}</a></strong></TD>\n";
}

print <<END
	<TD WIDTH='25%'><strong>$Lang::tr{'icmp type'}</strong></TD>
	<TD WIDTH='5%'>&nbsp;</TD>
	<TD WIDTH='5%'>&nbsp;</TD>
</TR>
END
;
&display_custom_services();
print <<END
</TABLE>
</DIV>
END
;
&Header::closebox();

&Header::openbox('100%', 'LEFT', "$Lang::tr{'default services'}:");
print <<END
<DIV ALIGN='CENTER'>
<TABLE WIDTH='100%' ALIGN='CENTER'>
<TR align="center">
	<TD><strong>$Lang::tr{'servicename'}</strong></TD>
	<TD><strong>$Lang::tr{'ports'}</strong></TD>
	<TD><strong>$Lang::tr{'protocol'}</strong></TD>
</TR>
END
;
&display_default_services();
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

sub display_custom_services
{
	
	open(FILE, "$filename") or die 'Unable to open services file.';
	my @current = <FILE>;
	close(FILE);

	my $id = 0;
	my $port_inv = '';
	my $prot_inv = '';
	my $port_inv_tail = '';
	my $prot_inv_tail = '';
	my @outarray = &General::srtarray($sort_col,$sort_type,$sort_dir,@current);
	foreach $line (@outarray)
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
			if ($temp[4] eq 'on'){$port_inv = " <strong><font color='RED'>! (</font></strong>";$port_inv_tail = "<strong><font color='RED'>)</font></strong>";}else{$port_inv='';$port_inv_tail='';}
			print "<TD ALIGN='CENTER'>" . $port_inv . &cleanport("$temp[2]") . $port_inv_tail . "</TD>\n";
			if ($temp[5] eq 'on'){$prot_inv = " <strong><font color='RED'>! (</font></strong>";$prot_inv_tail = "<strong><font color='RED'>)</font></strong>";}else{$prot_inv='';$prot_inv_tail='';}
			print "<TD ALIGN='CENTER'>" . $prot_inv . &cleanprotocol("$temp[3]") . $prot_inv_tail . "</TD>\n";
			if ($temp[6] eq 'BLANK') {
				print "<TD ALIGN='CENTER'>N/A</TD>\n";
			} else {
				print "<TD ALIGN='CENTER'>$temp[6]</TD>\n";
			}
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

sub display_default_services
{
	my $fname = "${General::swroot}/firewall/defaultservices";
	my $prev = "";
	my $newline="";
	
	open(FILE, "$fname") or die 'Unable to open default services file.';
	my @current = <FILE>;
	close(FILE);
	
	my $id = 0;
	
	foreach my $line (sort @current)
	{
		my @temp = split(/\,/,$line);
		if ($id % 2) {
			print "<TR BGCOLOR='${Header::table1colour}'>\n"; 
		} else {
           	print "<TR BGCOLOR='${Header::table2colour}'>\n";
		}
		print "<TD>$temp[0]</TD>\n";
		print "<TD ALIGN='CENTER'>$temp[1]</TD>\n";
		print "<TD ALIGN='CENTER'>" . &cleanprotocol("$temp[2]") . "</TD>\n";
		print "</TR>\n";
		$id++;
	}
}

sub cleanprotocol
{
	my $prtcl = $_[0];
	chomp($prtcl);
	if ($prtcl eq 'tcpudp') {
		$prtcl = 'TCP & UDP';
	} else {
		$prtcl = uc($prtcl);
	}
	return $prtcl;
}

sub cleanport
{
	my $prt = $_[0];
	chomp($prt);
	# Darren Critchley - Format the ports
	$prt =~ s/-/ - /;
	$prt =~ s/:/ - /;
	return $prt;
}

# Validate Field Entries
sub validateparams 
{
	$erromessage='';
	if ($cgiparams{'PROTOCOL'} eq 'tcp' || $cgiparams{'PROTOCOL'} eq 'udp' || $cgiparams{'PROTOCOL'} eq 'tcpudp' || $cgiparams{'PROTOCOL'} eq 'all') {
		# Darren Critchley - Get rid of dashes in port ranges
		$cgiparams{'PORTS'}=~ tr/-/:/;
		# Darren Critchley - code to substitue wildcards
		if ($cgiparams{'PORTS'} eq "*") {
			$cgiparams{'PORTS'} = "1:65535";
		}
		if ($cgiparams{'PORTS'} =~ /^(\D)\:(\d+)$/) {
			$cgiparams{'PORTS'} = "1:$2";
		}
		if ($cgiparams{'PORTS'} =~ /^(\d+)\:(\D)$/) {
			$cgiparams{'PORTS'} = "$1:65535";
		}
		# Darren Critchley - watch the order here, the validportrange sets errormessage=''
		$errormessage = &General::validportrange($cgiparams{'PORTS'}, 'src');
		if ($errormessage) {return;}
	} else {
		$cgiparams{'PORTS'} = "";
	}
	if ($cgiparams{'PROTOCOL'} eq 'tcp') {
		$cgiparams{'ICMP'} = "BLANK";
	}
	
	if($cgiparams{'PORTS'} eq '' && $cgiparams{'PORT_INVERT'} ne 'off'){
		$cgiparams{'PORT_INVERT'} = 'off';
	}
	if ($cgiparams{'NAME'} eq '') {
		$errormessage = $Lang::tr{'noservicename'};
		return;
	}
	if ($cgiparams{'PROTOCOL'} eq 'icmp' && $cgiparams{'ICMP'} eq 'BLANK'){
		$errormessage = $Lang::tr{'icmp selected but no type'};
		return;
	}
    unless($errormessage){
		$cgiparams{'NAME'}=&Header::cleanhtml($cgiparams{'NAME'});
		open(FILE, $filename) or die 'Unable to open custom services file.';
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
		unless($errormessage){
			my $fname = "${General::swroot}/firewall/defaultservices";
			my $prev = "";
			my $newline="";
			
			open(FILE, "$fname") or die 'Unable to open default services file.';
			my @current = <FILE>;
			close(FILE);
			
			foreach my $line (sort @current)
			{
				my @temp = split(/\,/,$line);
				if ($cgiparams{'NAME'} eq $temp[0]) {
					$errormessage=$Lang::tr{'duplicate name'};
					return;
				}
			}
		}
	}
}

sub get_icmptypes
{
	my $fname = "${General::swroot}/firewall/icmptypes";
	my $newline="";
	my @newarray=();
	
	open(FILE, "$fname") or die 'Unable to open icmp file.';
	my @current = <FILE>;
	close(FILE);

	foreach $newline (sort @current)
	{
		chomp ($newline);
		if (substr($newline, 0, 1) ne "#") {
			push (@newarray, $newline);
		}
	}
	return (@newarray);
}

