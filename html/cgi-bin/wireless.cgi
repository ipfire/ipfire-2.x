#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007  Michael Tremer & Christian Schmidt                      #
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
use Time::Local;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::colouryellow} );
undef (@dummy);

my %cgiparams=();
my %checked=();
my $errormessage = '';
my $filename = "${General::swroot}/wireless/config";
my $hostsfile = "${General::swroot}/main/hosts";
our %dhcpsettings=(); 
our %netsettings=();

$cgiparams{'ENABLED'} = 'off';
$cgiparams{'ACTION'} = '';
$cgiparams{'VALID'} = '';
$cgiparams{'SOURCE_IP'} ='';
$cgiparams{'SOURCE_MAC'} ='';
$cgiparams{'REMARK'} ='';

&Header::getcgihash(\%cgiparams);

&General::readhash("${General::swroot}/dhcp/settings", \%dhcpsettings);
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

&Header::showhttpheaders();

open(FILE, $filename) or die 'Unable to open config file.';
my @current = <FILE>;
close(FILE);

if ($cgiparams{'ACTION'} eq 'add')
{

	if ($cgiparams{'SOURCE_IP'} eq '' && $cgiparams{'SOURCE_MAC'} eq '')
	{
		goto ADDEXIT;
	}

	$cgiparams{'SOURCE_MAC'} =~ tr/-/:/;

	my $key = 0;
	foreach my $line (@current)
	{
		$key++;
		my @temp = split(/\,/,$line);

		if ($temp[1] ne '' && $cgiparams{'SOURCE_IP'} eq $temp[1] && $cgiparams{'EDITING'} ne $key)
		{
			$errormessage = $Lang::tr{'duplicate ip'};
			goto ADDERROR;
		}
		if ($temp[2] ne '' && lc($cgiparams{'SOURCE_MAC'}) eq lc($temp[2]) && $cgiparams{'EDITING'} ne $key)
		{
			$errormessage = $Lang::tr{'duplicate mac'};
			goto ADDERROR;
		}
	}

	if ($cgiparams{'SOURCE_IP'} eq '')
	{
		$cgiparams{'SOURCE_IP'} = 'NONE';
	} else {
		unless(&General::validipormask($cgiparams{'SOURCE_IP'})) 
		{
			$errormessage = $Lang::tr{'invalid fixed ip address'}; 
			goto ADDERROR;
		}
	}
	if ($cgiparams{'SOURCE_MAC'} eq '')
	{
		$cgiparams{'SOURCE_MAC'} = 'NONE';
	} else {
		unless(&General::validmac($cgiparams{'SOURCE_MAC'})) 
		{ 
			$errormessage = $Lang::tr{'invalid fixed mac address'}; 
		}
	}

ADDERROR:
	if ($errormessage)
	{
		$cgiparams{'SOURCE_MAC'} = '' if $cgiparams{'SOURCE_MAC'} eq 'NONE';
		$cgiparams{'SOURCE_IP'} = '' if $cgiparams{'SOURCE_IP'} eq 'NONE';
	} else {
		if ($cgiparams{'EDITING'} eq 'no') {
			open(FILE,">>$filename") or die 'Unable to open config file.';
			flock FILE, 2;
			print FILE "$key,$cgiparams{'SOURCE_IP'},$cgiparams{'SOURCE_MAC'},$cgiparams{'ENABLED'},$cgiparams{'REMARK'}\n";
		} else {
			open(FILE,">$filename") or die 'Unable to open config file.';
			flock FILE, 2;
			my $id = 0;
			foreach my $line (@current)
			{
				$id++;
				if ($cgiparams{'EDITING'} eq $id) {
					print FILE "$id,$cgiparams{'SOURCE_IP'},$cgiparams{'SOURCE_MAC'},$cgiparams{'ENABLED'},$cgiparams{'REMARK'}\n";
				} else { print FILE "$line"; }
			}
		}
		close(FILE);
		undef %cgiparams;
		&General::log($Lang::tr{'wireless config added'});
		system('/usr/local/bin/wirelessctrl');
	}
ADDEXIT:
}

if ($cgiparams{'ACTION'} eq 'edit')
{
	my $id = 0;
	foreach my $line (@current)
	{
		$id++;
		if ($cgiparams{'ID'} eq $id)
		{
			chomp($line);
			my @temp = split(/\,/,$line);
			$cgiparams{'SOURCE_IP'}  = $temp[1];
			$cgiparams{'SOURCE_MAC'} = $temp[2];
			$cgiparams{'ENABLED'}    = $temp[3];
			$cgiparams{'REMARK'}     = $temp[4];
			$cgiparams{'SOURCE_IP'} = '' if $cgiparams{'SOURCE_IP'} eq 'NONE';
			$cgiparams{'SOURCE_MAC'} = '' if $cgiparams{'SOURCE_MAC'} eq 'NONE';
		}
	}
	&General::log($Lang::tr{'wireless config changed'});
	system('/usr/local/bin/wirelessctrl');
}

if ($cgiparams{'ACTION'} eq 'remove' || $cgiparams{'ACTION'} eq 'toggle')
{
	my $id = 0;
	open(FILE, ">$filename") or die 'Unable to open config file.';
	flock FILE, 2;
	foreach my $line (@current)
	{
		$id++;
		unless ($cgiparams{'ID'} eq $id) { print FILE "$line"; }
		elsif ($cgiparams{'ACTION'} eq 'toggle')
		{
			chomp($line);
			my @temp = split(/\,/,$line);
			print FILE "$temp[0],$temp[1],$temp[2],$cgiparams{'ENABLE'},$temp[4]\n";
		}
	}
	close(FILE);
	&General::log($Lang::tr{'wireless config changed'});
	system('/usr/local/bin/wirelessctrl');
}


$checked{'ENABLED'}{'off'} = '';
$checked{'ENABLED'}{'on'} = '';
$checked{'ENABLED'}{$cgiparams{'ENABLED'}} = "checked='checked'";


&Header::openpage($Lang::tr{'wireless configuration'}, 1, '');

&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
}

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

my $buttontext = $Lang::tr{'add'};
if ($cgiparams{'ACTION'} eq 'edit') {
	&Header::openbox('100%', 'left', "$Lang::tr{'edit device'}");
	$buttontext = $Lang::tr{'update'};
} else {
	&Header::openbox('100%', 'left', "$Lang::tr{'add device'}");
}

print <<END
<table width='100%'>
<tr>
<td width='25%' class='base'>$Lang::tr{'source ip'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
<td width='25%' ><input type='text' name='SOURCE_IP' value='$cgiparams{'SOURCE_IP'}' size='25' /></td>
<td width='25%' class='base' align='right'>$Lang::tr{'enabled'}&nbsp;</td>
<td width='25%'><input type='checkbox' name='ENABLED' $checked{'ENABLED'}{'on'} /></td>
</tr>
<tr>
<td width='25%' class='base'>$Lang::tr{'source'} $Lang::tr{'mac address'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
<td colspan='3'><input type='text' name='SOURCE_MAC' value='$cgiparams{'SOURCE_MAC'}' size='25' /></td>
</tr>
<tr>
<td width='25%' class='base'>$Lang::tr{'remark'}:</td>
<td colspan='3'><input type='text' name='REMARK' value='$cgiparams{'REMARK'}' size='40' /></td>
</tr>
</table>
<br>
<hr>
<table width='100%'>
<tr>
    <td class='base' valign='top'><img src='/blob.gif' alt='*' /> $Lang::tr{'required field'}</td>
    <td width='40%' align='right'>
      <input type='hidden' name='ACTION' value='add' />
      <input type='submit' name='SUBMIT' value='$buttontext' />
    </td>
</tr>
</table>
END
;

if ($cgiparams{'ACTION'} eq 'edit') {
	print "<input type='hidden' name='EDITING' value='$cgiparams{'ID'}' />\n";
} else {
	print "<input type='hidden' name='EDITING' value='no' />\n";
}

&Header::closebox();

print "</form>\n";

&Header::openbox('100%', 'left', "$Lang::tr{'devices on blue'}");
print <<END
<div align='center'>
END
;
open (FILE, "$filename");
my @current = <FILE>;
close (FILE);

print <<END
<table width='100%' class='tbl'>
<tr>
<th align='center' width='20%'><b>$Lang::tr{'hostname'}</b></th>
<th align='center' width='20%'><b>$Lang::tr{'source ip'}</b></th>
<th align='center' width='20%'><b>$Lang::tr{'mac address'}</b></t>
<th align='center' width='35%'><b>$Lang::tr{'remark'}</b></th>
<th align='center' colspan='3'><b>$Lang::tr{'action'}</b></th>
</tr>
END
;

my $id = 0;

open (HOSTFILE, "$hostsfile");
my @curhosts = <HOSTFILE>;
close (HOSTFILE);

my $connstate = &Header::connectionstatus();
my @arp = `/sbin/arp -n`;
shift @arp;

foreach my $line (@current)
{
	$id++;
	chomp($line);
	my $gif = "";
	my $gdesc = "";
	my $hname = "";
	my $toggle = "";
	my @temp = split(/\,/,$line);
	my $wirelessid = $temp[0];
	my $sourceip = $temp[1];
	my $sourcemac = $temp[2];
	if ( $sourceip eq 'NONE' ) {
		foreach my $aline ( @arp )
		{
			chomp($aline);
			my @atemp = split( m{\s+}, $aline );
			my $aipaddr = $atemp[0];
			my $amacaddr = lc( $atemp[2] );
			if ( $amacaddr eq $sourcemac ) {
				$sourceip = $aipaddr;
				last;
			}
		}
	}

	# SourceIP could now have been set by the ARP probe.
	if ( $sourceip ne 'NONE' ) {
		foreach my $hline (@curhosts)
		{
			chomp($hline);
			my @htemp = split(/\,/,$hline);
			my $hkey = $htemp[0];
			my $hipaddr = $htemp[1];
			my $hostname = $htemp[2];
			my $domainname = $htemp[3];
			if ($sourceip eq $hipaddr) {
				$hname = "$hostname.$domainname";
				last;
			}
		}
		if ( $hname eq "" ) {
			my ($aliases, $addrtype, $length, @addrs);
			($hname, $aliases, $addrtype, $length, @addrs) = 
				gethostbyaddr(pack("C4", split(/\./,  $sourceip)), 2);
		}
	}

	if ($temp[3] eq 'on') { $gif = 'on.gif'; $toggle='off'; $gdesc=$Lang::tr{'click to disable'};}
		else { $gif = 'off.gif'; $toggle='on'; $gdesc=$Lang::tr{'click to enable'};}

	my $remark    = &Header::cleanhtml($temp[4]);
	my $col="";

	if ($cgiparams{'ACTION'} eq 'edit' && $cgiparams{'ID'} eq $id) {
		print "<tr>";
		$col="bgcolor='${Header::colouryellow}'";
	} elsif ($id % 2) {
		print "<tr>";
		$col="bgcolor='${Header::table1colour}'";
	} else {
		print "<tr>";
		$col="bgcolor='${Header::table2colour}'";
	}
	print "<td align='center' $col>$hname</td>\n";
	print "<td align='center' $col>$sourceip</td>\n";
	print "<td align='center' $col>$sourcemac</td>\n";
	print "<td align='center' $col>$remark</td>\n";
print<<END
<td align='center' $col>
	<form method='post' name='frma$id' action='$ENV{'SCRIPT_NAME'}'>
	<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif' alt='$gdesc' title='$gdesc' />
	<input type='hidden' name='ACTION' value='toggle'}' />
	<input type='hidden' name='ID' value='$id' />
	<input type='hidden' name='ENABLE' value='$toggle' />
	</form>
</td>

<td align='center' $col>
	<form method='post' name='frmb$id' action='$ENV{'SCRIPT_NAME'}'>
	<input type='hidden' name='ACTION' value='edit' />
	<input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' />
	<input type='hidden' name='ID' value='$id' />
	</form>
</td>

<td align='center' $col>
	<form method='post' name='frmc$id' action='$ENV{'SCRIPT_NAME'}'>
	<input type='hidden' name='ACTION' value='remove' />
	<input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' alt='$Lang::tr{'remove'}' title='$Lang::tr{'remove'}' />
	<input type='hidden' name='ID' value='$id' />
	</form>
</td>
END
	;
	print "</tr>\n";
}
print "</table>\n";

print "</div>\n";

&Header::closebox();

if ( $dhcpsettings{"ENABLE_BLUE"} eq 'on') {
	&printblueleases;
}

&Header::closebigbox();

&Header::closepage();

sub printblueleases
{
	our %entries = ();

	sub blueleasesort {
		# Sort by IP address
		my $qs ='IPADDR';
		my @a = split(/\./,$entries{$a}->{$qs});
		my @b = split(/\./,$entries{$b}->{$qs});
		($a[0]<=>$b[0]) ||
		($a[1]<=>$b[1]) ||
		($a[2]<=>$b[2]) ||
		($a[3]<=>$b[3]);
	}

	&Header::openbox('100%', 'left', "$Lang::tr{'current dhcp leases on blue'}");
	print <<END
<table width='100%' class='tbl'>
<tr>
<th width='25%' align='center'><b>$Lang::tr{'ip address'}</b></th>
<th width='25%' align='center'><b>$Lang::tr{'mac address'}</b></th>
<th width='20%' align='center'><b>$Lang::tr{'hostname'}</b></th>
<th width='30%' align='center'><b>$Lang::tr{'lease expires'} (local time d/m/y)</b></th>
<th></th>
</tr>
END
	;

	my ($ip, $endtime, $ether, $hostname, @record, $record);
	open(LEASES,"/var/state/dhcp/dhcpd.leases") or die "Can't open dhcpd.leases";
	while (my $line = <LEASES>) {
		next if( $line =~ /^\s*#/ );
		chomp($line);
		my @temp = split (' ', $line);

		if ($line =~ /^\s*lease/) {
			$ip = $temp[1];
			# All fields are not necessarily read. Clear everything
			$endtime = 0;
			$ether = "";
			$hostname = "";
		} elsif ($line =~ /^\s*ends never;/) {
			$endtime = 'never';
		} elsif ($line =~ /^\s*ends/) {
			$line =~ /(\d+)\/(\d+)\/(\d+) (\d+):(\d+):(\d+)/;
			$endtime = timegm($6, $5, $4, $3, $2 - 1, $1 - 1900);
		} elsif ($line =~ /^\s*hardware ethernet/) {
			$ether = $temp[2];
			$ether =~ s/;//g;
		} elsif ($line =~ /^\s*client-hostname/) {
			shift (@temp);
			$hostname = join (' ',@temp);
			$hostname =~ s/;//g;
			$hostname =~ s/\"//g;
		} elsif ($line eq "}") {
			# Select records in Blue subnet
			if ( &General::IpInSubnet ( $ip,
				$netsettings{"BLUE_NETADDRESS"},
				$netsettings{"BLUE_NETMASK"} ) ) {
				@record = ('IPADDR',$ip,'ENDTIME',$endtime,'ETHER',$ether,'HOSTNAME',$hostname);
				$record = {};                           	# create a reference to empty hash
				%{$record} = @record;                   	# populate that hash with @record
				$entries{$record->{'IPADDR'}} = $record;	# add this to a hash of hashes
			}
		}
	}
	close(LEASES);

	my $id = 0;
	foreach my $key (sort blueleasesort keys %entries) {

		my $hostname = &Header::cleanhtml($entries{$key}->{HOSTNAME},"y");
		my $col="";

		if ($id % 2) {
			print "<tr>";
			$col="bgcolor='$Header::table2colour'";
		} else {
			print "<tr>";
			$col="bgcolor='$Header::table1colour'";
		}

		print <<END
<td align='center' $col>$entries{$key}->{IPADDR}</td>
<td align='center' $col>$entries{$key}->{ETHER}</td>
<td align='center' $col>&nbsp;$hostname </td>
<td align='center' $col>
END
		;

		if ($entries{$key}->{ENDTIME} eq 'never') {
			print "$Lang::tr{'no time limit'}";
		} else {
			my ($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $dst);
			($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $dst) = localtime ($entries{$key}->{ENDTIME});
			my $enddate = sprintf ("%02d/%02d/%d %02d:%02d:%02d",$mday,$mon+1,$year+1900,$hour,$min,$sec);

			if ($entries{$key}->{ENDTIME} < time() ){
				print "<strike>$enddate</strike>";
			} else {
				print "$enddate";
			}
		}

		if ( $hostname eq '' ) {
			$hostname = $Lang::tr{'device'};
		}

		print <<END
<td align='center' $col>
	<form method='post' name='frmd$id' action='$ENV{'SCRIPT_NAME'}'>
	<input type='hidden' name='ACTION' value='add' />
	<input type='hidden' name='SOURCE_IP' value='' />
	<input type='hidden' name='SOURCE_MAC' value='$entries{$key}->{ETHER}' />
	<input type='hidden' name='REMARK' value='$hostname $Lang::tr{'added from dhcp lease list'}' />
	<input type='hidden' name='ENABLED' value='on' />
	<input type='hidden' name='EDITING' value='no' />
	<input type='image' name='$Lang::tr{'add device'}' src='/images/addblue.gif' alt='$Lang::tr{'add device'}' title='$Lang::tr{'add device'}' />
	</form>
</td></tr>
END
		;
		$id++;
	}

	print "</table>";
	&Header::closebox();
}

