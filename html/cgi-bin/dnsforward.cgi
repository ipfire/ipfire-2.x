#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2013  IPFire Development Team                                 #
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
my $filename = "${General::swroot}/dnsforward/config";
my $changed = 'no';

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

&Header::showhttpheaders();

$cgiparams{'ENABLED'} = 'off';
$cgiparams{'ACTION'} = '';
$cgiparams{'ZONE'} = '';
$cgiparams{'FORWARD_SERVER'} = '';
$cgiparams{'REMARK'} ='';
&Header::getcgihash(\%cgiparams);
open(FILE, $filename) or die 'Unable to open config file.';
my @current = <FILE>;
close(FILE);

###
# Add / Edit entries.
#
if ($cgiparams{'ACTION'} eq $Lang::tr{'add'})
{
	# Check if the entered domainname is valid.
	unless (&General::validdomainname($cgiparams{'ZONE'})) {
		$errormessage = $Lang::tr{'invalid domain name'};
	}

	# Check if the settings for the forward server are valid.
	unless(&General::validip($cgiparams{'FORWARD_SERVER'})) {
		$errormessage = $Lang::tr{'invalid ip'};
	}

	# Go further if there was no error.
	if ( ! $errormessage)
	{
	    # Check if a remark has been entered.
	    $cgiparams{'REMARK'} = &Header::cleanhtml($cgiparams{'REMARK'});

		# Check if we want to edit an existing or add a new entry.
		if($cgiparams{'EDITING'} eq 'no') {
			open(FILE,">>$filename") or die 'Unable to open config file.';
			flock FILE, 2;
			print FILE "$cgiparams{'ENABLED'},$cgiparams{'ZONE'},$cgiparams{'FORWARD_SERVER'},$cgiparams{'REMARK'}\n";
		} else {
			open(FILE, ">$filename") or die 'Unable to open config file.';
			flock FILE, 2;
			my $id = 0;
			foreach my $line (@current)
			{
				$id++;
				if ($cgiparams{'EDITING'} eq $id) {
					print FILE "$cgiparams{'ENABLED'},$cgiparams{'ZONE'},$cgiparams{'FORWARD_SERVER'},$cgiparams{'REMARK'}\n";
				} else { print FILE "$line"; }
			}
		}
		close(FILE);
		undef %cgiparams;
		$changed = 'yes';
	} else {
		# stay on edit mode if an error occur
		if ($cgiparams{'EDITING'} ne 'no')
		{
			$cgiparams{'ACTION'} = $Lang::tr{'edit'};
			$cgiparams{'ID'} = $cgiparams{'EDITING'};
		}
	}
	# Restart unbound
	system('/usr/local/bin/unboundctrl restart >/dev/null');
}

###
# Remove existing entries.
#
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
	# Restart unbound.
	system('/usr/local/bin/unboundctrl restart >/dev/null');
}

###
# Toggle Enable/Disable for entries.
#
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
			print FILE "$cgiparams{'ENABLE'},$temp[1],$temp[2],$temp[3]\n";
		}
	}
	close(FILE);
	# Restart unbound.
	system('/usr/local/bin/unboundctrl restart >/dev/null');
}

###
# Read items for edit mode.
#
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
			$cgiparams{'ENABLED'} = $temp[0];
			$cgiparams{'ZONE'} = $temp[1];
			$cgiparams{'FORWARD_SERVER'} = $temp[2];
			$cgiparams{'REMARK'} = $temp[3];
		}
	}
}

$checked{'ENABLED'}{'off'} = '';
$checked{'ENABLED'}{'on'} = '';
$checked{'ENABLED'}{$cgiparams{'ENABLED'}} = "checked='checked'";

&Header::openpage($Lang::tr{'dnsforward configuration'}, 1, '');

&Header::openbigbox('100%', 'left', '', $errormessage);

###
# Error messages layout.
#
if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
}

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

my $buttontext = $Lang::tr{'add'};
if ($cgiparams{'ACTION'} eq $Lang::tr{'edit'}) {
	&Header::openbox('100%', 'left', $Lang::tr{'dnsforward edit an entry'});
	$buttontext = $Lang::tr{'update'};
} else {
	&Header::openbox('100%', 'left', $Lang::tr{'dnsforward add a new entry'});
}

###
# Content of the main page.
#
print <<END
<table width='100%'>
	<tr>
		<td width='20%' class='base'>$Lang::tr{'dnsforward zone'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
		<td><input type='text' name='ZONE' value='$cgiparams{'ZONE'}' size='24' /></td>
		<td width='30%' class='base'>$Lang::tr{'enabled'}<input type='checkbox' name='ENABLED' $checked{'ENABLED'}{'on'} /></td>
	</tr>

	<tr>
		<td width='20%' class='base'>$Lang::tr{'dnsforward forward_server'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
		<td><input type='text' name='FORWARD_SERVER' value='$cgiparams{'FORWARD_SERVER'}' size='24' /></td>
	</tr>
</table>

<table width='100%'>
	<tr>
		<td width ='20%' class='base'>$Lang::tr{'remark'}:</td>
		<td><input type='text' name='REMARK' value='$cgiparams{'REMARK'}' size='40' maxlength='50' /></td>
	</tr>
</table>
<br>
<hr>

<table width='100%'>
	<tr>
		<td class='base' width='55%'><img src='/blob.gif' alt ='*' align='top' />&nbsp;$Lang::tr{'required field'}</td>
		<td width='40%' align='right'>
			<input type='hidden' name='ACTION' value='$Lang::tr{'add'}' />
			<input type='submit' name='SUBMIT' value='$buttontext' />
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

###
# Existing rules.
#
&Header::openbox('100%', 'left', $Lang::tr{'dnsforward entries'});
print <<END
<table width='100%' class='tbl'>
	<tr>
		<th width='35%' class='boldbase' align='center'><b>$Lang::tr{'dnsforward zone'}</b></th>
		<th width='30%' class='boldbase' align='center'><b>$Lang::tr{'dnsforward forward_server'}</b></th>
		<th width='30%' class='boldbase' align='center'><b>$Lang::tr{'remark'}</b></th>
		<th width='5%' class='boldbase' colspan='3' align='center'><b>$Lang::tr{'action'}</b></th>
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

###
# Re-read entries and highlight selected item for editing.
#
my $id = 0;
my $col="";
foreach my $line (@current)
{
	$id++;
	chomp($line);
	my @temp = split(/\,/,$line);
	my $toggle = '';
	my $gif = '';
	my $gdesc = '';
	my $toggle = '';
	
	if($cgiparams{'ACTION'} eq $Lang::tr{'edit'} && $cgiparams{'ID'} eq $id) {
		print "<tr>";
		$col="bgcolor='${Header::colouryellow}'"; }
	elsif ($id % 2) {
		print "<tr>";
		$col="bgcolor='$color{'color22'}'"; }
	else {
		print "<tr>";
		$col="bgcolor='$color{'color20'}'"; }

	if ($temp[0] eq 'on') { $gif='on.gif'; $toggle='off'; $gdesc=$Lang::tr{'click to disable'};}
	else { $gif='off.gif'; $toggle='on'; $gdesc=$Lang::tr{'click to enable'}; }

###
# Display edit page.
#
print <<END
	<td align='center' $col>$temp[1]</td>
	<td align='center' $col>$temp[2]</td>
	<td align='center' $col>$temp[3]</td>
	<td align='center' $col>
		<form method='post' name='frma$id' action='$ENV{'SCRIPT_NAME'}'>
			<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif' title='$gdesc' alt='$gdesc' />
			<input type='hidden' name='ID' value='$id' />
			<input type='hidden' name='ENABLE' value='$toggle' />
			<input type='hidden' name='ACTION' value='$Lang::tr{'toggle enable disable'}' />
		</form>
	</td>
	<td align='center' $col>
		<form method='post' name='frmb$id' action='$ENV{'SCRIPT_NAME'}'>
			<input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' title='$Lang::tr{'edit'}' alt='$Lang::tr{'edit'}' />
			<input type='hidden' name='ID' value='$id' />
			<input type='hidden' name='ACTION' value='$Lang::tr{'edit'}' />
		</form>
	</td>
	<td align='center' $col>
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

###
# Print the legend at the bottom if there are any configured entries.
#
# Check if the file size is zero - no existing entries.
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
