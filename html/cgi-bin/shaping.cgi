#!/usr/bin/perl
#
#  Traffic shaping CGI
#
#  Copyright 2003-04-06 David Kilpatrick <dave@thunder.com.au>
#
# $Id: shaping.cgi,v 1.3.2.15 2005/02/27 13:42:05 eoberlander Exp $
#

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require 'CONFIG_ROOT/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::table2colour}, ${Header::colouryellow} );
undef (@dummy);

my %shapingsettings=();
my $configfile = "${General::swroot}/shaping/config";
my $settingsfile = "${General::swroot}/shaping/settings";
my $errormessage = '';

&Header::showhttpheaders();

$shapingsettings{'ACTION'} = '';
$shapingsettings{'ENABLE'} = 'off';
$shapingsettings{'VALID'} = '';
$shapingsettings{'UPLINK'} = '';
$shapingsettings{'DOWNLINK'} = '';
$shapingsettings{'SERVICE_ENABLED'} = '';
$shapingsettings{'SERVICE_PROT'} = '';
$shapingsettings{'SERVICE_PRIO'} = '';
$shapingsettings{'SERVICE_PORT'} = '';

&Header::getcgihash(\%shapingsettings);

open(FILE, "$configfile") or die 'Unable to open shaping config file.';
my @current = <FILE>;
close(FILE);

if ($shapingsettings{'ACTION'} eq $Lang::tr{'save'})
{
	if (!($shapingsettings{'UPLINK'} =~ /^\d+$/) ||
	   ($shapingsettings{'UPLINK'} < 2))
	{
		$errormessage = $Lang::tr{'invalid uplink speed'};
		goto ERROR;
	}

	if (!($shapingsettings{'DOWNLINK'} =~ /^\d+$/) ||
	     ($shapingsettings{'DOWNLINK'} < 2))
	{
		$errormessage = $Lang::tr{'invalid downlink speed'};
		goto ERROR;
	}

ERROR:
	if ($errormessage) {
		$shapingsettings{'VALID'} = 'no'; }
	else {
		$shapingsettings{'VALID'} = 'yes'; }
	
	open(FILE,">$settingsfile") or die 'Unable to open shaping settings file.';
	flock FILE, 2;
	print FILE "VALID=$shapingsettings{'VALID'}\n";
	print FILE "ENABLE=$shapingsettings{'ENABLE'}\n";
	print FILE "UPLINK=$shapingsettings{'UPLINK'}\n";
	print FILE "DOWNLINK=$shapingsettings{'DOWNLINK'}\n";
	close FILE;

	if ($shapingsettings{'VALID'} eq 'yes') {
		system('/usr/local/bin/restartshaping');
	}
}
if ($shapingsettings{'ACTION'} eq $Lang::tr{'add'})
{
	unless($shapingsettings{'SERVICE_PROT'} =~ /^(tcp|udp)$/) { $errormessage = $Lang::tr{'invalid input'}; }
	unless($shapingsettings{'SERVICE_PRIO'} =~ /^(10|20|30)$/) { $errormessage = $Lang::tr{'invalid input'}; }
	unless(&General::validport($shapingsettings{'SERVICE_PORT'})) { $errormessage = $Lang::tr{'invalid port'}; }

	if ( ! $errormessage)
	{
		if ($shapingsettings{'EDITING'} eq 'no')
		{
			open(FILE,">>$configfile") or die 'Unable to open shaping config file';
			flock FILE, 2;
			print FILE "$shapingsettings{'SERVICE_PROT'},$shapingsettings{'SERVICE_PORT'},$shapingsettings{'SERVICE_PRIO'},$shapingsettings{'SERVICE_ENABLED'}\n";
		} else {
			open(FILE,">$configfile") or die 'Unable to open shaping config file';
			flock FILE, 2;
			my $id = 0;
			foreach my $line (@current)
			{
				$id++;
				chomp($line);
				my @temp = split(/\,/,$line);
				if ($shapingsettings{'EDITING'} eq $id) {
					print FILE "$shapingsettings{'SERVICE_PROT'},$shapingsettings{'SERVICE_PORT'},$shapingsettings{'SERVICE_PRIO'},$shapingsettings{'SERVICE_ENABLED'}\n";
				} else {
					print FILE "$line\n";
				}
			}
		}
		close FILE;
		undef %shapingsettings;
		system ('/usr/local/bin/restartshaping');
	} else {
		# stay on edit mode if an error occur
		if ($shapingsettings{'EDITING'} ne 'no')
		{
			$shapingsettings{'ACTION'} = $Lang::tr{'edit'};
			$shapingsettings{'ID'} = $shapingsettings{'EDITING'};
		}
	}
}

if ($shapingsettings{'ACTION'} eq $Lang::tr{'edit'})
{
	my $id = 0;
	foreach my $line (@current)
	{
		$id++;
		if ($shapingsettings{"ID"} eq $id)
		{
			chomp($line);
			my @temp = split(/\,/,$line);
			$shapingsettings{'SERVICE_PROT'} = $temp[0];
			$shapingsettings{'SERVICE_PORT'} = $temp[1];
			$shapingsettings{'SERVICE_PRIO'} = $temp[2];
			$shapingsettings{'SERVICE_ENABLED'} = $temp[3];
		}
	}
}

if ($shapingsettings{'ACTION'} eq $Lang::tr{'remove'} || $shapingsettings{'ACTION'} eq $Lang::tr{'toggle enable disable'})
{
	open(FILE, ">$configfile") or die 'Unable to open config file.';
	flock FILE, 2;
	my $id = 0;
	foreach my $line (@current)
	{
		$id++;
		unless ($shapingsettings{"ID"} eq $id) { print FILE "$line"; }
		elsif ($shapingsettings{'ACTION'} eq $Lang::tr{'toggle enable disable'})
		{
			chomp($line);
			my @temp = split(/\,/,$line);
			if ($temp[3] eq "on") {
				print FILE "$temp[0],$temp[1],$temp[2],off\n";
			} else {
				print FILE "$temp[0],$temp[1],$temp[2],on\n";
			}
		}
	}
	close(FILE);
	system ('/usr/local/bin/restartshaping');
}

&General::readhash("${General::swroot}/shaping/settings", \%shapingsettings);

if ($shapingsettings{'ACTION'} eq '')
{
	$shapingsettings{'SERVICE_ENABLED'} = 'on';
	$shapingsettings{'SERVICE_PROT'} = 'tcp';
	$shapingsettings{'SERVICE_PRIO'} = '20';
	$shapingsettings{'SERVICE_PORT'} = '';
}

my %checked=();
$checked{'ENABLE'}{'off'} = '';
$checked{'ENABLE'}{'on'} = '';
$checked{'ENABLE'}{$shapingsettings{'ENABLE'}} = "checked='checked'";

my %service_checked=();
$service_checked{'SERVICE_ENABLED'}{'off'} = '';
$service_checked{'SERVICE_ENABLED'}{'on'} = '';
$service_checked{'SERVICE_ENABLED'}{$shapingsettings{'SERVICE_ENABLED'}} = "checked='checked'";

my %service_selected=();
$service_selected{'SERVICE_PROT'}{'udp'} = '';
$service_selected{'SERVICE_PROT'}{'tcp'} = '';
$service_selected{'SERVICE_PROT'}{$shapingsettings{'SERVICE_PROT'}} = "selected='selected'";

$service_selected{'SERVICE_PRIO'}{'10'} = '';
$service_selected{'SERVICE_PRIO'}{'20'} = '';
$service_selected{'SERVICE_PRIO'}{'30'} = '';
$service_selected{'SERVICE_PRIO'}{$shapingsettings{'SERVICE_PRIO'}} = "selected='selected'";

&Header::openpage($Lang::tr{'traffic shaping settings'}, 1, '');

&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<font class='base'>$errormessage&nbsp;</font>\n";
	&Header::closebox();
}

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

&Header::openbox('100%', 'left', "$Lang::tr{'settings'}:");
print <<END
<table width='100%'>
<tr>
	<td><input type='checkbox' name='ENABLE' $checked{'ENABLE'}{'on'} /></td>
	<td class='base' colspan='2'>$Lang::tr{'traffic shaping'}</td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td width='30%' class='base'>$Lang::tr{'downlink speed'}:&nbsp;</td>
	<td width='70%'><input type='text' name='DOWNLINK' value='$shapingsettings{'DOWNLINK'}' size='5' /></td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td class='base'>$Lang::tr{'uplink speed'}:&nbsp;</td>
	<td><input type='text' name='UPLINK' value='$shapingsettings{'UPLINK'}' size='5' /></td>
</tr>
</table>
<table width='100%'>
<hr />
<tr>
	<td width='50%'> &nbsp; </td>
	<td width='50%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
</tr>
</table>
END
;
&Header::closebox;

print "</form>\n";
print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

my $buttontext = $Lang::tr{'add'};
if($shapingsettings{'ACTION'} eq $Lang::tr{'edit'}) {
	$buttontext = $Lang::tr{'update'};
	&Header::openbox('100%', 'left', $Lang::tr{'edit service'});
} else {
	&Header::openbox('100%', 'left', $Lang::tr{'add service'});
}

print <<END

<table width='100%'>
<tr>
	<td class='base'>$Lang::tr{'priority'}:&nbsp;</td>
	<td><select name='SERVICE_PRIO'>
		<option value='10' $service_selected{'SERVICE_PRIO'}{'10'}>$Lang::tr{'high'}</option>
		<option value='20' $service_selected{'SERVICE_PRIO'}{'20'}>$Lang::tr{'medium'}</option>
		<option value='30' $service_selected{'SERVICE_PRIO'}{'30'}>$Lang::tr{'low'}</option>
	</select></td>
	<td width='20%' class='base' align='right'>$Lang::tr{'port'}:&nbsp;</td>
	<td><input type='text' name='SERVICE_PORT' value='$shapingsettings{'SERVICE_PORT'}' size='5' /></td>
	<td width='20%' class='base' align='right'>$Lang::tr{'protocol'}:&nbsp;</td>
	<td><select name='SERVICE_PROT'>
				<option value='tcp' $service_selected{'SERVICE_PROT'}{'tcp'}>TCP</option>
				<option value='udp' $service_selected{'SERVICE_PROT'}{'udp'}>UDP</option>
			</select></td>
	<td width='20%' class='base' align='right'>$Lang::tr{'enabled'}&nbsp;</td> 
	<td width='20%'><input type='checkbox' name='SERVICE_ENABLED' $service_checked{'SERVICE_ENABLED'}{'on'} /></td>
</tr>
</table>
<table width='100%'>
<hr />
<tr>
	<td width='50%'>&nbsp;</td>
	<td width='50%' align='center'><input type='submit' name='SUBMIT' value='$buttontext' /><input type='hidden' name='ACTION' value='$Lang::tr{'add'}' /></td>
</tr>
</table>
END
;
&Header::closebox;

if ($shapingsettings{'ACTION'} eq $Lang::tr{'edit'}) {
	print "<input type='hidden' name='EDITING' value='$shapingsettings{'ID'}' />\n";
} else {
	print "<input type='hidden' name='EDITING' value='no' />\n";
}

print "</form>\n";

&Header::openbox('100%', 'left', $Lang::tr{'shaping list options'});
print <<END
<table width='100%' align='center'>
<tr>
	<td width='33%' align='center' class='boldbase'><b>$Lang::tr{'priority'}</b></td>
	<td width='33%' align='center' class='boldbase'><b>$Lang::tr{'port'}</b></td>
	<td width='33%' align='center' class='boldbase'><b>$Lang::tr{'protocol'}</b></td>
	<td align='center' class='boldbase' colspan='3'><b>$Lang::tr{'action'}</b></td>
</tr>
END
;

my $id = 0;
open(SERVICES, "$configfile") or die 'Unable to open shaping config file.';
while (<SERVICES>)
{
	my $gif = '';
	my $prio = '';
	my $gdesc = '';
	$id++;
	chomp($_);
	my @temp = split(/\,/,$_);
	if ($temp[3] eq "on") {
		$gif = 'on.gif';  $gdesc=$Lang::tr{'click to disable'}; }
	else {
		$gif = 'off.gif'; $gdesc=$Lang::tr{'click to enable'};  }
	if ($shapingsettings{'ACTION'} eq $Lang::tr{'edit'} && $shapingsettings{'ID'} eq $id) {
		print "<tr bgcolor='${Header::colouryellow}'>\n"; }
	elsif ($id % 2) {
		print "<tr bgcolor='${Header::table1colour}'>\n"; }
	else {
		print "<tr bgcolor='${Header::table2colour}'>\n"; }
	if ($temp[2] eq "10") { $prio = $Lang::tr{'high'}; }
	if ($temp[2] eq "20") { $prio = $Lang::tr{'medium'}; }
	if ($temp[2] eq "30") { $prio = $Lang::tr{'low'}; }
	
print <<END
<td align='center'>$prio</td>
<td align='center'>$temp[1]</td>
<td align='center'>$temp[0]</td>

<td align='center'>
	<form method='post' action='$ENV{'SCRIPT_NAME'}' name='frma$id'>
	<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif' alt='$gdesc' title='$gdesc' />
	<input type='hidden' name='ACTION' value='$Lang::tr{'toggle enable disable'}' />
	<input type='hidden' name='ID' value='$id' />
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
close(SERVICES);

print <<END
</table>
END
;
&Header::closebox;


&Header::closebigbox();

&Header::closepage;
