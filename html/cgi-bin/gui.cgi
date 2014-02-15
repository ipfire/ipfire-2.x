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

my %cgiparams=();
my %mainsettings=();
my %checked=();
my $errormessage='';


$cgiparams{'SPEED'} = 'off';
$cgiparams{'WINDOWWITHHOSTNAME'} = 'off';
$cgiparams{'REFRESHINDEX'} = 'off';
$cgiparams{'ACTION'} = '';
&Header::getcgihash(\%cgiparams);

&Header::showhttpheaders();
&General::readhash("${General::swroot}/main/settings",\%mainsettings);
if ($cgiparams{'ACTION'} eq "$Lang::tr{'save'}")
{
	open(FILE,"${General::swroot}/langs/list");
	my $found=0;
	while (<FILE>)
	{
		my $lang='';
		my $engname='';
		my $natname='';
		chomp;
		($lang,$engname,$natname) = split (/:/, $_,3);
		if ($cgiparams{'lang'} eq $lang)
		{
			$found=1;
		}
	}
	close (FILE);
	if ( $found == 0 )
	{
		$errormessage="$errormessage<p>$Lang::tr{'invalid input'}</p>";
		goto SAVE_ERROR;
	}

        # Set flag if index page is to refresh whilst ppp is up.
        # Default is NO refresh.
        if ($cgiparams{'REFRESHINDEX'} ne 'off') {
            system ('/usr/bin/touch', "${General::swroot}/main/refreshindex");
        } else {
            unlink "${General::swroot}/main/refreshindex";
        }

        # Beep on ip-up or ip-down. Default is ON.
        if ($cgiparams{'PPPUPDOWNBEEP'} ne 'on') {
            $cgiparams{'PPPUPDOWNBEEP'} = 'off';
            system ('/usr/bin/touch', "${General::swroot}/ppp/nobeeps");
        } else {
            unlink "${General::swroot}/ppp/nobeeps";
        }

        # write cgi vars to the file.
	$mainsettings{'LANGUAGE'} = $cgiparams{'lang'};
	$mainsettings{'WINDOWWITHHOSTNAME'} = $cgiparams{'WINDOWWITHHOSTNAME'};
	$mainsettings{'PPPUPDOWNBEEP'} = $cgiparams{'PPPUPDOWNBEEP'};
	$mainsettings{'SPEED'} = $cgiparams{'SPEED'};
	$mainsettings{'THEME'} = $cgiparams{'theme'};
	$mainsettings{'REFRESHINDEX'} = $cgiparams{'REFRESHINDEX'};
	&General::writehash("${General::swroot}/main/settings", \%mainsettings);
	&Lang::reload($cgiparams{'lang'});
	SAVE_ERROR:
} else {
	if ($mainsettings{'WINDOWWITHHOSTNAME'}) {
		$cgiparams{'WINDOWWITHHOSTNAME'} = $mainsettings{'WINDOWWITHHOSTNAME'};
	} else {
		$cgiparams{'WINDOWWITHHOSTNAME'} = 'on';
	}

	if ($mainsettings{'PPPUPDOWNBEEP'}) {
		$cgiparams{'PPPUPDOWNBEEP'} = $mainsettings{'PPPUPDOWNBEEP'};
	} else {
		$cgiparams{'PPPUPDOWNBEEP'} = 'on';
	}

	if ($mainsettings{'THEME'}) {
		$cgiparams{'THEME'} = $mainsettings{'THEME'};
	} else {
		$cgiparams{'THEME'} = 'ipfire';
	}

	if($mainsettings{'REFRESHINDEX'}) {
		$cgiparams{'REFRESHINDEX'} = $mainsettings{'REFRESHINDEX'};
	} else {
		$cgiparams{'REFRESHINDEX'} = 'off';
	}
	if($mainsettings{'SPEED'}) {
		$cgiparams{'SPEED'} = $mainsettings{'SPEED'};
	} else {
	# if var is not defined it will be set to on because after installation var
	# is not set and the speedmeter should be displayed, it can only be deactivated
	# by manually setting the var to off
		$cgiparams{'SPEED'} = 'on';
	}
}

# Default settings
if ($cgiparams{'ACTION'} eq "$Lang::tr{'restore defaults'}")
{
	$cgiparams{'WINDOWWITHHOSTNAME'} = 'on';
	$cgiparams{'PPPUPDOWNBEEP'} = 'on';
	$cgiparams{'REFRESHINDEX'} = 'off';
	$cgiparams{'SPEED'} = 'on';
	$cgiparams{'THEME'} = 'ipfire';
}

$checked{'WINDOWWITHHOSTNAME'}{'off'} = '';
$checked{'WINDOWWITHHOSTNAME'}{'on'} = '';
$checked{'WINDOWWITHHOSTNAME'}{$cgiparams{'WINDOWWITHHOSTNAME'}} = "checked='checked'";

$checked{'PPPUPDOWNBEEP'}{'off'} = '';
$checked{'PPPUPDOWNBEEP'}{'on'} = '';
$checked{'PPPUPDOWNBEEP'}{$cgiparams{'PPPUPDOWNBEEP'}} = "checked='checked'";

$checked{'REFRESHINDEX'}{'off'} = '';
$checked{'REFRESHINDEX'}{'on'} = '';
$checked{'REFRESHINDEX'}{$cgiparams{'REFRESHINDEX'}} = "checked='checked'";

$checked{'SPEED'}{'off'} = '';
$checked{'SPEED'}{'on'} = '';
$checked{'SPEED'}{$cgiparams{'SPEED'}} = "checked='checked'";

&Header::openpage($Lang::tr{'gui settings'}, 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
	&Header::openbox('100%','left',$Lang::tr{'error messages'});
	print "<font class='base'>${errormessage}&nbsp;</font>\n";
	&Header::closebox();
}

&Header::openbox('100%','left',$Lang::tr{'display'});

print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='100%'>
<tr>
    <td><input type='checkbox' name='WINDOWWITHHOSTNAME' $checked{'WINDOWWITHHOSTNAME'}{'on'} /></td>
    <td>$Lang::tr{'display hostname in window title'}</td>
</tr>
<tr>
    <td><input type='checkbox' name='REFRESHINDEX' $checked{'REFRESHINDEX'}{'on'} /></td>
    <td>$Lang::tr{'refresh index page while connected'}</td>
</tr>
<tr>
    <td><input type='checkbox' name='SPEED' $checked{'SPEED'}{'on'} /></td>
    <td>$Lang::tr{'show ajax speedmeter in footer'}</td>
</tr>
<tr>
    <td>&nbsp;</td>
    <td>$Lang::tr{'languagepurpose'}</td>
</tr>
<tr>
    <td>&nbsp;</td>
    <td><select name='lang'>
END
;

my $id=0;
open(FILE,"${General::swroot}/langs/list");
while (<FILE>)
{
	my $lang='';
	my $engname='';
	my $natname='';
        $id++;
        chomp;
        ($lang,$engname,$natname) = split (/:/, $_, 3);
	print "<option value='$lang' ";
	if ($lang =~ /$mainsettings{'LANGUAGE'}/)
	{
		print " selected='selected'";
	}
	print <<END
>$engname ($natname)</option>
END
	;
}

print <<END
</select></td></tr>
</table>
END
;
&Header::closebox();
&Header::openbox('100%','left',$Lang::tr{'theme'});
print<<END;
<table>
<tr>
    <td>&nbsp;</td>
    <td><select name='theme'>
END
;

my $dir = "/srv/web/ipfire/html/themes";
local *DH;
my ($item, $file);
my @files;

# Foreach directory create am theme entry to be selected by user

opendir (DH, $dir);
while ($file = readdir (DH)) {
	next if ( $file =~ /^\./ );
	push (@files, $file);
}
closedir (DH);

foreach $item (sort (@files)) {
	if ( "$mainsettings{'THEME'}" eq "$item" ) {
		print "<option value='$item' selected='selected'>$item</option>\n";
	} else {
		print "<option value='$item'>$item</option>\n";
	}
}

print <<END
</select></td></tr>
</table>
END
;
&Header::closebox();
&Header::openbox('100%','left',$Lang::tr{'sound'});
print <<END
<tr>
    <td><input type ='checkbox' name='PPPUPDOWNBEEP' $checked{'PPPUPDOWNBEEP'}{'on'} /></td>
    <td>$Lang::tr{'beep when ppp connects or disconnects'}</td>
</tr>
<tr>
    <td colspan='2'></td>
</tr>
</table>
<div align='right'>
<br>
<table width='100%'>
<tr>
    <td width='90%' align='right'><input type='submit' name='ACTION' value='$Lang::tr{'restore defaults'}' /></td>
    <td width='10%' align='right'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
</tr>
</table>
</div>
</form>
END
;
&Header::closebox();
&Header::closebigbox();
&Header::closepage();



