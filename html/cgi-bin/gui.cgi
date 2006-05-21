#!/usr/bin/perl
#
# IPCop CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) Bill Ward
#
# $Id: gui.cgi,v 1.2.2.17 2005/07/06 09:21:22 franck78 Exp $
#

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require 'CONFIG_ROOT/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %cgiparams=();
my %mainsettings=();
my %checked=();
my $errormessage='';


$cgiparams{'JAVASCRIPT'} = 'off';
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
		$errormessage="$errormessage<P>$Lang::tr{'invalid input'}";
		goto SAVE_ERROR;
	}

        # Set flag if index page is to refresh whilst ppp is up.
        # Default is NO refresh.
        if ($cgiparams{'REFRESHINDEX'} ne 'off') {
            system ('/bin/touch', "${General::swroot}/main/refreshindex");
        } else {
            unlink "${General::swroot}/main/refreshindex";
        }

        # Beep on ip-up or ip-down. Default is ON.
        if ($cgiparams{'PPPUPDOWNBEEP'} ne 'on') {
            $cgiparams{'PPPUPDOWNBEEP'} = 'off';
            system ('/bin/touch', "${General::swroot}/ppp/nobeeps");
        } else {
            unlink "${General::swroot}/ppp/nobeeps";
        }

        # write cgi vars to the file.
	$mainsettings{'LANGUAGE'} = $cgiparams{'lang'};
	$mainsettings{'WINDOWWITHHOSTNAME'} = $cgiparams{'WINDOWWITHHOSTNAME'};
	$mainsettings{'PPPUPDOWNBEEP'} = $cgiparams{'PPPUPDOWNBEEP'};
	$mainsettings{'REFRESHINDEX'} = $cgiparams{'REFRESHINDEX'};
	&General::writehash("${General::swroot}/main/settings", \%mainsettings);
	&Lang::reload($cgiparams{'lang'});
	SAVE_ERROR:
} else {
	if ($mainsettings{'WINDOWWITHHOSTNAME'}) {
		$cgiparams{'WINDOWWITHHOSTNAME'} = $mainsettings{'WINDOWWITHHOSTNAME'};
	} else {
		$cgiparams{'WINDOWWITHHOSTNAME'} = 'off';
	}

	if ($mainsettings{'PPPUPDOWNBEEP'}) {
		$cgiparams{'PPPUPDOWNBEEP'} = $mainsettings{'PPPUPDOWNBEEP'};
	} else {
		$cgiparams{'PPPUPDOWNBEEP'} = 'on';
	}

	if($mainsettings{'REFRESHINDEX'}) {
		$cgiparams{'REFRESHINDEX'} = $mainsettings{'REFRESHINDEX'};
	} else {
		$cgiparams{'REFRESHINDEX'} = 'off';
	}
}

# Default settings
if ($cgiparams{'ACTION'} eq "$Lang::tr{'restore defaults'}")
{
	$cgiparams{'WINDOWWITHHOSTNAME'} = 'off';
	$cgiparams{'PPPUPDOWNBEEP'} = 'on';
	$cgiparams{'REFRESHINDEX'} = 'off';
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

&Header::openpage($Lang::tr{'gui settings'}, 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
	&Header::openbox('100%','left',$Lang::tr{'error messages'});
	print "<font class='base'>${errormessage}&nbsp;</font>\n";
	&Header::closebox();
}

&Header::openbox('100%','left',$Lang::tr{'gui settings'});

print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='100%'>
<tr>
    <td colspan='2'><p><b>$Lang::tr{'display'}</b></td>
</tr>
<tr>
    <td><input type='checkbox' name='WINDOWWITHHOSTNAME' $checked{'WINDOWWITHHOSTNAME'}{'on'} /></td>
    <td>$Lang::tr{'display hostname in window title'}</td>
</tr>
<tr>
    <td><input type='checkbox' name='REFRESHINDEX' $checked{'REFRESHINDEX'}{'on'} /></td>
    <td>$Lang::tr{'refresh index page while connected'}</td>
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
<tr>
    <td colspan='2'><hr /><p><b>$Lang::tr{'sound'}</b></td>
</tr>
<tr>
    <td><input type ='checkbox' name='PPPUPDOWNBEEP' $checked{'PPPUPDOWNBEEP'}{'on'} /></td>
    <td>$Lang::tr{'beep when ppp connects or disconnects'}</td>
</tr>
<tr>
    <td colspan='2'><hr /></td>
</tr>
</table>
<div align='center'>
<table width='80%'>
<tr>
    <td width='50%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'restore defaults'}' /></td>
    <td width='50%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
</tr>
</table>
</div>
</form>
END
;
&Header::closebox();
&Header::closebigbox();
&Header::closepage();



