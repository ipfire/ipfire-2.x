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

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::table2colour}, ${Header::colouryellow} );
undef (@dummy);

my %cgiparams=();
my %checked=();
my %selected=();
my %netsettings=();
my $errormessage = '';
my $filename = "${General::swroot}/dmzholes/config";

&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

&Header::showhttpheaders();

$cgiparams{'ENABLED'} = 'off';
$cgiparams{'REMARK'} = '';
$cgiparams{'ACTION'} = '';
$cgiparams{'SRC_IP'} = '';
$cgiparams{'DEST_IP'} ='';
$cgiparams{'DEST_PORT'} = '';
&Header::getcgihash(\%cgiparams);

open(FILE, $filename) or die 'Unable to open config file.';
my @current = <FILE>;
close(FILE);

if ($cgiparams{'ACTION'} eq $Lang::tr{'add'})
{
	unless($cgiparams{'PROTOCOL'} =~ /^(tcp|udp)$/) { $errormessage = $Lang::tr{'invalid input'}; }
	unless(&General::validipormask($cgiparams{'SRC_IP'})) { $errormessage = $Lang::tr{'source ip bad'}; }
	unless($errormessage){$errormessage = &General::validportrange($cgiparams{'DEST_PORT'},'dst');}
	unless(&General::validipormask($cgiparams{'DEST_IP'})) { $errormessage = $Lang::tr{'destination ip bad'}; }
	unless ($errormessage) {
		$errormessage = &validNet($cgiparams{'SRC_NET'},$cgiparams{'DEST_NET'}); }
	# Darren Critchley - Remove commas from remarks
	$cgiparams{'REMARK'} = &Header::cleanhtml($cgiparams{'REMARK'});

	unless ($errormessage)
	{
		if($cgiparams{'EDITING'} eq 'no') {
			open(FILE,">>$filename") or die 'Unable to open config file.';
			flock FILE, 2;
			print FILE "$cgiparams{'PROTOCOL'},";		# [0]
			print FILE "$cgiparams{'SRC_IP'},";		# [1]
			print FILE "$cgiparams{'DEST_IP'},";		# [2]
			print FILE "$cgiparams{'DEST_PORT'},";		# [3]
			print FILE "$cgiparams{'ENABLED'},";		# [4]
			print FILE "$cgiparams{'SRC_NET'},";		# [5]
			print FILE "$cgiparams{'DEST_NET'},";		# [6]
			print FILE "$cgiparams{'REMARK'}\n";		# [7]
		} else {
			open(FILE,">$filename") or die 'Unable to open config file.';
			flock FILE, 2;
			my $id = 0;
			foreach my $line (@current)
			{
				$id++;
				if ($cgiparams{'EDITING'} eq $id) {
					print FILE "$cgiparams{'PROTOCOL'},";		# [0]
					print FILE "$cgiparams{'SRC_IP'},";		# [1]
					print FILE "$cgiparams{'DEST_IP'},";		# [2]
					print FILE "$cgiparams{'DEST_PORT'},";		# [3]
					print FILE "$cgiparams{'ENABLED'},";		# [4]
					print FILE "$cgiparams{'SRC_NET'},";		# [5]
					print FILE "$cgiparams{'DEST_NET'},";		# [6]
					print FILE "$cgiparams{'REMARK'}\n";		# [7]
				} else { print FILE "$line"; }
			}
		}
		close(FILE);
		undef %cgiparams;
		&General::log($Lang::tr{'dmz pinhole rule added'});
		system('/usr/local/bin/setdmzholes');
	}
}
if ($cgiparams{'ACTION'} eq $Lang::tr{'remove'})
{
	my $id = 0;
	open(FILE, ">$filename") or die 'Unable to open config file.';
	flock FILE, 2;
	foreach my $line (@current)
	{
		$id++;
		unless ($cgiparams{'ID'} eq $id) { print FILE "$line"; }
	}
	close(FILE);
	system('/usr/local/bin/setdmzholes');
	&General::log($Lang::tr{'dmz pinhole rule removed'});
}
if ($cgiparams{'ACTION'} eq $Lang::tr{'toggle enable disable'})
{
	my $id = 0;
	open(FILE, ">$filename") or die 'Unable to open config file.';
	flock FILE, 2;
	foreach my $line (@current)
	{
		$id++;
		unless ($cgiparams{'ID'} eq $id) { print FILE "$line"; }
		else
		{
			chomp($line);
			my @temp = split(/\,/,$line);
			print FILE "$temp[0],$temp[1],$temp[2],$temp[3],$cgiparams{'ENABLE'},$temp[5],$temp[6],$temp[7]\n";
		}
	}
	close(FILE);
	system('/usr/local/bin/setdmzholes');
}
if ($cgiparams{'ACTION'} eq $Lang::tr{'edit'})
{
	my $id = 0;
	foreach my $line (@current)
	{
		$id++;
		if ($cgiparams{'ID'} eq $id)
		{
			chomp($line);
			my @temp = split(/\,/,$line);
			$cgiparams{'PROTOCOL'} = $temp[0];
			$cgiparams{'SRC_IP'} = $temp[1];
			$cgiparams{'DEST_IP'} = $temp[2];
			$cgiparams{'DEST_PORT'} = $temp[3];
			$cgiparams{'ENABLED'} = $temp[4];
			$cgiparams{'SRC_NET'} = $temp[5];
			$cgiparams{'DEST_NET'} = $temp[6];
			$cgiparams{'REMARK'} = $temp[7];
		}
	}
}

if ($cgiparams{'ACTION'} eq '')
{
	$cgiparams{'PROTOCOL'} = 'tcp';
	$cgiparams{'ENABLED'} = 'on';
	$cgiparams{'SRC_NET'} = 'orange';
	$cgiparams{'DEST_NET'} = 'blue';
}

$selected{'PROTOCOL'}{'udp'} = '';
$selected{'PROTOCOL'}{'tcp'} = '';
$selected{'PROTOCOL'}{$cgiparams{'PROTOCOL'}} = "selected='selected'";

$selected{'SRC_NET'}{'orange'} = '';
$selected{'SRC_NET'}{'blue'} = '';
$selected{'SRC_NET'}{$cgiparams{'SRC_NET'}} = "selected='selected'";

$selected{'DEST_NET'}{'blue'} = '';
$selected{'DEST_NET'}{'green'} = '';
$selected{'DEST_NET'}{$cgiparams{'DEST_NET'}} = "selected='selected'";

$checked{'ENABLED'}{'off'} = '';
$checked{'ENABLED'}{'on'} = '';
$checked{'ENABLED'}{$cgiparams{'ENABLED'}} = "checked='checked'";

&Header::openpage($Lang::tr{'dmz pinhole configuration'}, 1, '');

&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
}

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

my $buttonText = $Lang::tr{'add'};
if ($cgiparams{'ACTION'} eq $Lang::tr{'edit'}) {
	&Header::openbox('100%', 'left', $Lang::tr{'edit a rule'});
	$buttonText = $Lang::tr{'update'};
} else {
	&Header::openbox('100%', 'left', $Lang::tr{'add a new rule'});
}
print <<END
<table width='100%'>
<tr>
<td>
	<select name='PROTOCOL'>
		<option value='udp' $selected{'PROTOCOL'}{'udp'}>UDP</option>
		<option value='tcp' $selected{'PROTOCOL'}{'tcp'}>TCP</option>
	</select>
</td>
<td>
	$Lang::tr{'source net'}:</td>
<td>
	<select name='SRC_NET'>
END
;
	if (&haveOrangeNet()) {
		print "<option value='orange' $selected{'SRC_NET'}{'orange'}>$Lang::tr{'orange'}</option>";
	}
	if (&haveBlueNet()) {
		print "<option value='blue' $selected{'SRC_NET'}{'blue'}>$Lang::tr{'blue'}</option>";
	}
print <<END
	</select>
</td>
<td class='base'>$Lang::tr{'source ip or net'}:</td>
<td><input type='text' name='SRC_IP' value='$cgiparams{'SRC_IP'}' size='15' /></td>
</tr>
<tr>
<td>
	&nbsp;</td>
<td>
	$Lang::tr{'destination net'}:</td>
<td>
	<select name='DEST_NET'>
END
;
	if (&haveOrangeNet() && &haveBlueNet()) {
		print "<option value='blue' $selected{'DEST_NET'}{'blue'}>$Lang::tr{'blue'}</option>";
	}

print <<END
		<option value='green' $selected{'DEST_NET'}{'green'}>$Lang::tr{'green'}</option>
	</select>
</td>
<td class='base'>
	$Lang::tr{'destination ip or net'}:</td>
<td>
	<input type='text' name='DEST_IP' value='$cgiparams{'DEST_IP'}' size='15' />
</td>
<td class='base'>
	$Lang::tr{'destination port'}:&nbsp;
	<input type='text' name='DEST_PORT' value='$cgiparams{'DEST_PORT'}' size='5' />
</td>
</tr>
</table>
<table width='100%'>
	<tr>
		<td colspan='3' width='50%' class='base'>
			<font class='boldbase'>$Lang::tr{'remark title'}&nbsp;<img src='/blob.gif' alt='*' /></font>
			<input type='text' name='REMARK' value='$cgiparams{'REMARK'}' size='55' maxlength='50' />
		</td>
	</tr>
	<tr>
		<td class='base' width='50%'>
			<img src='/blob.gif' alt ='*' align='top' />&nbsp;
			<font class='base'>$Lang::tr{'this field may be blank'}</font>
		</td>
		<td class='base' width='25%' align='center'>$Lang::tr{'enabled'}<input type='checkbox' name='ENABLED' $checked{'ENABLED'}{'on'} /></td>
		<td width='25%' align='center'>
			<input type='hidden' name='ACTION' value='$Lang::tr{'add'}' />
			<input type='submit' name='SUBMIT' value='$buttonText' />
		</td>
	</tr>
</table>
END
;
if ($cgiparams{'ACTION'} eq $Lang::tr{'edit'}) {
	print "<input type='hidden' name='EDITING' value='$cgiparams{'ID'}' />\n";
} else {
	print "<input type='hidden' name='EDITING' value='no' />\n";
}
&Header::closebox();
print "</form>\n";

&Header::openbox('100%', 'left', $Lang::tr{'current rules'});
print <<END
<table width='100%'>
<tr>
<td width='7%' class='boldbase' align='center'><b>$Lang::tr{'proto'}</b></td>
<td width='3%' class='boldbase' align='center'><b>$Lang::tr{'net'}</b></td>
<td width='25%' class='boldbase' align='center'><b>$Lang::tr{'source'}</b></td>
<td width='2%' class='boldbase' align='center'>&nbsp;</td>
<td width='3%' class='boldbase' align='center'><b>$Lang::tr{'net'}</b></td>
<td width='25%' class='boldbase' align='center'><b>$Lang::tr{'destination'}</b></td>
<td width='30%' class='boldbase' align='center'><b>$Lang::tr{'remark'}</b></td>
<td width='1%' class='boldbase' align='center'>&nbsp;</td>
<td width='4%' class='boldbase' colspan='3' align='center'><b>$Lang::tr{'action'}</b></td>
END
;

# Achim Weber: if i add a new rule, this rule is not displayed?!?
#							we re-read always config.
# If something has happeened re-read config
#if($cgiparams{'ACTION'} ne '')
#{
	open(FILE, $filename) or die 'Unable to open config file.';
	@current = <FILE>;
	close(FILE);
#}
my $id = 0;
foreach my $line (@current)
{
	my $protocol='';
	my $gif='';
	my $toggle='';
	my $gdesc='';
	$id++;
	chomp($line);
	my @temp = split(/\,/,$line);
	if ($temp[0] eq 'udp') { $protocol = 'UDP'; } else { $protocol = 'TCP' }

	my $srcnetcolor = ($temp[5] eq 'blue')? ${Header::colourblue} : ${Header::colourorange};
	my $destnetcolor = ($temp[6] eq 'blue')? ${Header::colourblue} : ${Header::colourgreen};

	if ($cgiparams{'ACTION'} eq $Lang::tr{'edit'} && $cgiparams{'ID'} eq $id) {
		print "<tr bgcolor='${Header::colouryellow}'>\n"; }
	elsif ($id % 2) {
		print "<tr bgcolor='${Header::table1colour}'>\n"; }
	else {
		print "<tr bgcolor='${Header::table2colour}'>\n"; }
	if ($temp[4] eq 'on') { $gif='on.gif'; $toggle='off'; $gdesc=$Lang::tr{'click to disable'};}
	else { $gif = 'off.gif'; $toggle='on'; $gdesc=$Lang::tr{'click to enable'}; }

	# Darren Critchley - Get Port Service Name if we can - code borrowed from firewalllog.dat
	my $dstprt =$temp[3];
	$_=$temp[3];
	if (/^\d+$/) {
		my $servi = uc(getservbyport($temp[3], lc($temp[0])));
		if ($servi ne '' && $temp[3] < 1024) {
			$dstprt = "$dstprt($servi)"; }
	}
	# Darren Critchley - If the line is too long, wrap the port numbers
	my $dstaddr = "$temp[2] : $dstprt";
	if (length($dstaddr) > 26) {
		$dstaddr = "$temp[2] :<br /> $dstprt";
	}
print <<END
<td align='center'>$protocol</td>
<td bgcolor='$srcnetcolor'></td>
<td align='center'>$temp[1]</td>
<td align='center'><img src='/images/forward.gif' /></td>
<td bgcolor='$destnetcolor'></td>
<td align='center'>$dstaddr</td>
<td align='center'>$temp[7]</td>

<td align='center'>
<form method='post' name='frma$id' action='$ENV{'SCRIPT_NAME'}'>
<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif' alt='$gdesc' />
<input type='hidden' name='ID' value='$id' />
<input type='hidden' name='ENABLE' value='$toggle' />
<input type='hidden' name='ACTION' value='$Lang::tr{'toggle enable disable'}' />
</form>
</td>

<td align='center'>
<form method='post' name='frmb$id' action='$ENV{'SCRIPT_NAME'}'>
<input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' alt='$Lang::tr{'edit'}' />
<input type='hidden' name='ID' value='$id' />
<input type='hidden' name='ACTION' value='$Lang::tr{'edit'}' />
</form>
</td>

<td align='center'>
<form method='post' name='frmc$id' action='$ENV{'SCRIPT_NAME'}'>
<input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' alt='$Lang::tr{'remove'}' />
<input type='hidden' name='ID' value='$id' />
<input type='hidden' name='ACTION' value='$Lang::tr{'remove'}' />
</form>
</td>

</tr>
END
	;
}
print "</table>\n";

# If the fixed lease file contains entries, print Key to action icons
if ( ! -z "$filename") {
print <<END
<table>
<tr>
	<td class='boldbase'>&nbsp; <b>$Lang::tr{'legend'}:</b></td>
	<td>&nbsp; <img src='/images/on.gif' alt='$Lang::tr{'click to disable'}' /></td>
	<td class='base'>$Lang::tr{'click to disable'}</td>
	<td>&nbsp; &nbsp; <img src='/images/off.gif' alt='$Lang::tr{'click to enable'}' /></td>
	<td class='base'>$Lang::tr{'click to enable'}</td>
	<td>&nbsp; &nbsp; <img src='/images/edit.gif' alt='$Lang::tr{'edit'}' /></td>
	<td class='base'>$Lang::tr{'edit'}</td>
	<td>&nbsp; &nbsp; <img src='/images/delete.gif' alt='$Lang::tr{'remove'}' /></td>
	<td class='base'>$Lang::tr{'remove'}</td>
</tr>
</table>
END
;
}

&Header::closebox();

&Header::closebigbox();

&Header::closepage();

sub validNet
{
	my $srcNet	= $_[0];
	my $destNet	= $_[1];

	if ($srcNet eq $destNet) {
		return $Lang::tr{'dmzpinholes for same net not necessary'}; }
	unless ($srcNet =~ /^(blue|orange)$/) {
		return $Lang::tr{'select source net'}; }
	unless ($destNet =~ /^(blue|green)$/) {
		return $Lang::tr{'select dest net'}; }
		
	return '';
}

sub haveOrangeNet
{
	if ($netsettings{'CONFIG_TYPE'} == 2) {return 1;}
	if ($netsettings{'CONFIG_TYPE'} == 4) {return 1;}
	return 0;
}

sub haveBlueNet
{
	if ($netsettings{'CONFIG_TYPE'} == 3) {return 1;}
	if ($netsettings{'CONFIG_TYPE'} == 4) {return 1;}
	return 0;
}
