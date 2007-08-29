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
my @dummy = ( ${Header::colouryellow} );
undef (@dummy);

my %cgiparams=();
my %checked=();
my %selected=();
my $errormessage = '';
my $filename = "${General::swroot}/xtaccess/config";
my $aliasfile = "${General::swroot}/ethernet/aliases";
my $changed = 'no';

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

&Header::showhttpheaders();

$cgiparams{'ENABLED'} = 'off';
$cgiparams{'ACTION'} = '';
$cgiparams{'SRC'} = '';
$cgiparams{'DEST_PORT'} = '';
$cgiparams{'REMARK'} ='';
&Header::getcgihash(\%cgiparams);
open(FILE, $filename) or die 'Unable to open config file.';
my @current = <FILE>;
close(FILE);

if ($cgiparams{'ACTION'} eq $Lang::tr{'add'})
{
	unless($cgiparams{'PROTOCOL'} =~ /^(tcp|udp)$/) { $errormessage = $Lang::tr{'invalid input'}; }
	unless(&General::validipormask($cgiparams{'SRC'}))
	{
		if ($cgiparams{'SRC'} ne '') {
			$errormessage = $Lang::tr{'source ip bad'}; }
		else {
			$cgiparams{'SRC'} = '0.0.0.0/0'; }
	}
	unless($errormessage){ $errormessage = &General::validportrange($cgiparams{'DEST_PORT'},'dst'); }
	if ( ! $errormessage)
	{
	    $cgiparams{'REMARK'} = &Header::cleanhtml($cgiparams{'REMARK'});

		if($cgiparams{'EDITING'} eq 'no') {
			open(FILE,">>$filename") or die 'Unable to open config file.';
			flock FILE, 2;
			print FILE "$cgiparams{'PROTOCOL'},$cgiparams{'SRC'},$cgiparams{'DEST_PORT'},$cgiparams{'ENABLED'},$cgiparams{'DEST'},$cgiparams{'REMARK'}\n";
		} else {
			open(FILE, ">$filename") or die 'Unable to open config file.';
			flock FILE, 2;
			my $id = 0;
			foreach my $line (@current)
			{
				$id++;
				if ($cgiparams{'EDITING'} eq $id) {
					print FILE "$cgiparams{'PROTOCOL'},$cgiparams{'SRC'},$cgiparams{'DEST_PORT'},$cgiparams{'ENABLED'},$cgiparams{'DEST'},$cgiparams{'REMARK'}\n";
				} else { print FILE "$line"; }
			}
		}
		close(FILE);
		undef %cgiparams;
		$changed = 'yes';
		&General::log($Lang::tr{'external access rule added'});
		system('/usr/local/bin/setxtaccess');
	} else {
		# stay on edit mode if an error occur
		if ($cgiparams{'EDITING'} ne 'no')
		{
			$cgiparams{'ACTION'} = $Lang::tr{'edit'};
			$cgiparams{'ID'} = $cgiparams{'EDITING'};
		}
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
	system('/usr/local/bin/setxtaccess');
	&General::log($Lang::tr{'external access rule removed'});
}
if ($cgiparams{'ACTION'} eq $Lang::tr{'toggle enable disable'})
{
	open(FILE, ">$filename") or die 'Unable to open config file.';
	flock FILE, 2;
	my $id = 0;
	foreach my $line (@current)
	{
		$id++;
		unless ($cgiparams{'ID'} eq $id) { print FILE "$line"; }
		else
		{
			chomp($line);
			my @temp = split(/\,/,$line);
			print FILE "$temp[0],$temp[1],$temp[2],$cgiparams{'ENABLE'},$temp[4],$temp[5]\n";
		}
	}
	close(FILE);
	system('/usr/local/bin/setxtaccess');
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
			$cgiparams{'SRC'} = $temp[1];
			$cgiparams{'DEST_PORT'} = $temp[2];
			$cgiparams{'ENABLED'} = $temp[3];
			$cgiparams{'DEST'} = $temp[4];
			$cgiparams{'REMARK'} = $temp[5];
		}
	}
}

if ($cgiparams{'ACTION'} eq '')
{
	$cgiparams{'PROTOCOL'} = 'tcp';
	$cgiparams{'DEST'} = '0.0.0.0';
	$cgiparams{'ENABLED'} = 'on';
}

$selected{'PROTOCOL'}{'udp'} = '';
$selected{'PROTOCOL'}{'tcp'} = '';
$selected{'PROTOCOL'}{$cgiparams{'PROTOCOL'}} = "selected='selected'";

$selected{'DEST'}{$cgiparams{'DEST'}} = "selected='selected'";

$checked{'ENABLED'}{'off'} = '';
$checked{'ENABLED'}{'on'} = '';
$checked{'ENABLED'}{$cgiparams{'ENABLED'}} = "checked='checked'";

&Header::openpage($Lang::tr{'external access configuration'}, 1, '');

&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
}

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

my $buttontext = $Lang::tr{'add'};
if ($cgiparams{'ACTION'} eq $Lang::tr{'edit'}) {
	&Header::openbox('100%', 'left', $Lang::tr{'edit a rule'});
	$buttontext = $Lang::tr{'update'};
} else {
	&Header::openbox('100%', 'left', $Lang::tr{'add a new rule'});
}
print <<END
<table width='100%'>
<tr>
<td width='10%'>
<select name='PROTOCOL'>
<option value='udp' $selected{'PROTOCOL'}{'udp'}>UDP</option>
<option value='tcp' $selected{'PROTOCOL'}{'tcp'}>TCP</option>
</select>
</td>
<td class='base'><font color='${Header::colourred}'>$Lang::tr{'source network'}</font></td>
<td><input type='text' name='SRC' value='$cgiparams{'SRC'}' size='32' /></td>
<td class='base'><font color='${Header::colourred}'>$Lang::tr{'destination port'}:</font></td>
<td><input type='text' name='DEST_PORT' value='$cgiparams{'DEST_PORT'}' size='5' /></td>
</tr>
</table>
<table width='100%'>
<tr>
<td width='10%' class='base'>$Lang::tr{'enabled'}<input type='checkbox' name='ENABLED' $checked{'ENABLED'}{'on'} /></td>
<td class='base'><font color='${Header::colourred}'>$Lang::tr{'destination ip'}:&nbsp;</font>
<select name='DEST'>
<option value='0.0.0.0' $selected{'DEST'}{'0.0.0.0'}>DEFAULT IP</option>
END
;

open(ALIASES, "$aliasfile") or die 'Unable to open aliases file.';
while (<ALIASES>)
{
	chomp($_);
	my @temp = split(/\,/,$_);
	if ($temp[1] eq 'on') {
		print "<option value='$temp[0]' $selected{'DEST'}{$temp[0]}>$temp[0]";
		if (defined $temp[2] and ($temp[2] ne '')) { print " ($temp[2])"; }
		print "</option>\n";
	}
}
close(ALIASES);
print <<END
</select>
</td>
</tr>
</table>
<table width='100%'>
<tr>
<td width ='10%' class='base'>
<font class='boldbase'>$Lang::tr{'remark'}:</font>&nbsp;<img src='/blob.gif' alt='*' />
</td>
<td width='65%'>
<input type='text' name='REMARK' value='$cgiparams{'REMARK'}' size='55' maxlength='50' />
</td>
<td width='25%' align='center'>
<input type='hidden' name='ACTION' value='$Lang::tr{'add'}' />
<input type='submit' name='SUBMIT' value='$buttontext' />
</td>
</tr>
</table>
<table width='100%'>
<tr>
<td class='base' width='30%'><img src='/blob.gif' alt ='*' align='top' />&nbsp;<font class='base'>$Lang::tr{'this field may be blank'}</font>
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
<td width='10%' class='boldbase' align='center'><b>$Lang::tr{'proto'}</b></td>
<td width='20%' class='boldbase' align='center'><b>$Lang::tr{'source ip'}</b></td>
<td width='20%' class='boldbase' align='center'><b>$Lang::tr{'destination ip'}</b></td>
<td width='15%' class='boldbase' align='center'><b>$Lang::tr{'destination port'}</b></td>
<td width='30%' class='boldbase' align='center'><b>$Lang::tr{'remark'}</b></td>
<td width='5%' class='boldbase' colspan='3' align='center'><b>$Lang::tr{'action'}</b></td>
</tr>
END
;

# If something has happened re-read config
if($cgiparams{'ACTION'} ne '' or $changed ne 'no')
{
	open(FILE, $filename) or die 'Unable to open config file.';
	@current = <FILE>;
	close(FILE);
}
my $id = 0;
foreach my $line (@current)
{
	$id++;
	chomp($line);
	my @temp = split(/\,/,$line);
	my $protocol = '';
	my $gif = '';
	my $gdesc = '';
	my $toggle = '';
	if ($temp[0] eq 'udp') {
		$protocol = 'UDP'; }
	else {
		$protocol = 'TCP' }
	if($cgiparams{'ACTION'} eq $Lang::tr{'edit'} && $cgiparams{'ID'} eq $id) {
		print "<tr bgcolor='${Header::colouryellow}'>\n"; }
	elsif ($id % 2) {
		print "<tr bgcolor='$color{'color22'}'>\n"; }
	else {
		print "<tr bgcolor='$color{'color20'}'>\n"; }
	if ($temp[3] eq 'on') { $gif='on.gif'; $toggle='off'; $gdesc=$Lang::tr{'click to disable'};}
	else { $gif='off.gif'; $toggle='on'; $gdesc=$Lang::tr{'click to enable'}; }
	if ($temp[1] eq '0.0.0.0/0') {
		$temp[1] = $Lang::tr{'caps all'}; }
	# catch for 'old-style' rules file - assume default ip if
	# none exists
	if (!&General::validip($temp[4]) || $temp[4] eq '0.0.0.0') {
		$temp[4] = 'DEFAULT IP'; }
	$temp[5] = '' unless defined $temp[5];
print <<END
<td align='center'>$protocol</td>
<td align='center'>$temp[1]</td>
<td align='center'>$temp[4]</td>
<td align='center'>$temp[2]</td>
<td align='left'>&nbsp;$temp[5]</td>
<td align='center'>
<form method='post' name='frma$id' action='$ENV{'SCRIPT_NAME'}'>
<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif' title='$gdesc' alt='$gdesc' />
<input type='hidden' name='ID' value='$id' />
<input type='hidden' name='ENABLE' value='$toggle' />
<input type='hidden' name='ACTION' value='$Lang::tr{'toggle enable disable'}' />
</form>
</td>
<td align='center'>
<form method='post' name='frmb$id' action='$ENV{'SCRIPT_NAME'}'>
<input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' title='$Lang::tr{'edit'}' alt='$Lang::tr{'edit'}' />
<input type='hidden' name='ID' value='$id' />
<input type='hidden' name='ACTION' value='$Lang::tr{'edit'}' />
</form>
</td>
<td align='center'>
<form method='post' name='frmc$id' action='$ENV{'SCRIPT_NAME'}'>
<input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' title='$Lang::tr{'remove'}' alt='$Lang::tr{'remove'}' />
<input type='hidden' name='ID' value='$id' />
<input type='hidden' name='ACTION' value='$Lang::tr{'remove'}' />
</form>
</td>

</tr>
END
	;
}
print "</table>\n";

# If the xt access file contains entries, print Key to action icons
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
