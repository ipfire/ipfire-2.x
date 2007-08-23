#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# $Id: remote.cgi,v 1.6.2.8 2005/02/22 22:21:56 gespinasse Exp $
#

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %remotesettings=();
my %checked=();
my $errormessage='';

&Header::showhttpheaders();

$remotesettings{'ENABLE_SSH'} = 'off';
$remotesettings{'ENABLE_SSH_PROTOCOL1'} = 'off';
$remotesettings{'ENABLE_SSH_PORTFW'} = 'off';
$remotesettings{'ACTION'} = '';
&Header::getcgihash(\%remotesettings);

if ( (($remotesettings{'ACTION'} eq $Lang::tr{'save'}) || ($remotesettings{'ACTION'} eq $Lang::tr{'ssh tempstart15'}) || ($remotesettings{'ACTION'} eq $Lang::tr{'ssh tempstart30'})) && $remotesettings{'ACTION'} ne "" )
{
	# not existing here indicates the box is unticked
	$remotesettings{'ENABLE_SSH_PASSWORDS'} = 'off' unless exists $remotesettings{'ENABLE_SSH_PASSWORDS'};
	$remotesettings{'ENABLE_SSH_KEYS'} = 'off' unless exists $remotesettings{'ENABLE_SSH_KEYS'};


	&General::writehash("${General::swroot}/remote/settings", \%remotesettings);
	if ($remotesettings{'ENABLE_SSH'} eq 'on')
	{
		&General::log($Lang::tr{'ssh is enabled'});
		if  ($remotesettings{'ENABLE_SSH_PASSWORDS'} eq 'off'
		 and $remotesettings{'ENABLE_SSH_KEYS'}      eq 'off')
		{
			$errormessage = $Lang::tr{'ssh no auth'};
		}
		system ('/usr/bin/touch', "${General::swroot}/remote/enablessh");
	}
	else
	{
		&General::log($Lang::tr{'ssh is disabled'});
		unlink "${General::swroot}/remote/enablessh";
	}

	if ($remotesettings{'ENABLE_SSH_PROTOCOL1'} eq 'on')
	{
		&General::log($Lang::tr{'ssh1 enabled'});
	}
	else
	{
		&General::log($Lang::tr{'ssh1 disabled'});
	}
if ( $remotesettings{'ACTION'} eq $Lang::tr{'ssh tempstart15'} ){
	system('/usr/local/bin/sshctrl','tempstart15') == 0
		or $errormessage = "$Lang::tr{'bad return code'} " . $?/256;
 }
elsif ( $remotesettings{'ACTION'} eq $Lang::tr{'ssh tempstart30'} ){
	system('/usr/local/bin/sshctrl','tempstart30') == 0
		or $errormessage = "$Lang::tr{'bad return code'} " . $?/256;
 }
else {
	system('/usr/local/bin/sshctrl') == 0
		or $errormessage = "$Lang::tr{'bad return code'} " . $?/256;
 }
}

&General::readhash("${General::swroot}/remote/settings", \%remotesettings);

# not existing here means they're undefined and the default value should be
# used
	$remotesettings{'ENABLE_SSH_PASSWORDS'} = 'on' unless exists $remotesettings{'ENABLE_SSH_PASSWORDS'};
	$remotesettings{'ENABLE_SSH_KEYS'} = 'on' unless exists $remotesettings{'ENABLE_SSH_KEYS'};

$checked{'ENABLE_SSH'}{'off'} = '';
$checked{'ENABLE_SSH'}{'on'} = '';
$checked{'ENABLE_SSH'}{$remotesettings{'ENABLE_SSH'}} = "checked='checked'";
$checked{'ENABLE_SSH_PROTOCOL1'}{'off'} = '';
$checked{'ENABLE_SSH_PROTOCOL1'}{'on'} = '';
$checked{'ENABLE_SSH_PROTOCOL1'}{$remotesettings{'ENABLE_SSH_PROTOCOL1'}} = "checked='checked'";
$checked{'ENABLE_SSH_PORTFW'}{'off'} = '';
$checked{'ENABLE_SSH_PORTFW'}{'on'} = '';
$checked{'ENABLE_SSH_PORTFW'}{$remotesettings{'ENABLE_SSH_PORTFW'}} = "checked='checked'";
$checked{'ENABLE_SSH_PASSWORDS'}{'off'} = '';
$checked{'ENABLE_SSH_PASSWORDS'}{'on'} = '';
$checked{'ENABLE_SSH_PASSWORDS'}{$remotesettings{'ENABLE_SSH_PASSWORDS'}} = "checked='checked'";
$checked{'ENABLE_SSH_KEYS'}{'off'} = '';
$checked{'ENABLE_SSH_KEYS'}{'on'} = '';
$checked{'ENABLE_SSH_KEYS'}{$remotesettings{'ENABLE_SSH_KEYS'}} = "checked='checked'";


&Header::openpage($Lang::tr{'remote access'}, 1, '');

&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<FONT CLASS='base'>$errormessage&nbsp;</FONT>\n";
	&Header::closebox();
}

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

&Header::openbox('100%', 'left', 'SSH:');
print <<END
<table width='100%'>
<tr>
	<td><input type='checkbox' name='ENABLE_SSH' $checked{'ENABLE_SSH'}{'on'} /></td>
	<td class='base' colspan='2'>$Lang::tr{'ssh access'}</td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td><input type='checkbox' name='ENABLE_SSH_PROTOCOL1' $checked{'ENABLE_SSH_PROTOCOL1'}{'on'} /></td>
	<td width='100%' class='base'>$Lang::tr{'ssh1 support'}</td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td><input type='checkbox' name='ENABLE_SSH_PORTFW' $checked{'ENABLE_SSH_PORTFW'}{'on'} /></td>
	<td width='100%' class='base'>$Lang::tr{'ssh portfw'}</td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td><input type='checkbox' name='ENABLE_SSH_PASSWORDS' $checked{'ENABLE_SSH_PASSWORDS'}{'on'} /></td>
	<td width='100%' class='base'>$Lang::tr{'ssh passwords'}</td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td><input type='checkbox' name='ENABLE_SSH_KEYS' $checked{'ENABLE_SSH_KEYS'}{'on'} /></td>
	<td width='100%' class='base'>$Lang::tr{'ssh keys'}</td>
</tr>
<tr>
	<td align='center' colspan='3'><hr />
	<input type='submit' name='ACTION' value='$Lang::tr{'ssh tempstart15'}' />
	<input type='submit' name='ACTION' value='$Lang::tr{'ssh tempstart30'}' />
	<input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
</tr>
</table>
END
;
&Header::closebox();

print "</form>\n";

&Header::openbox('100%', 'left', $Lang::tr{'ssh host keys'});

print "<table>\n";

print <<END
<tr><td class='boldbase'><b>$Lang::tr{'ssh key'}</b></td>
    <td class='boldbase'><b>$Lang::tr{'ssh fingerprint'}</b></td>
    <td class='boldbase'><b>$Lang::tr{'ssh key size'}</b></td></tr>
END
;

&viewkey("/etc/ssh/ssh_host_key.pub","RSA1");
&viewkey("/etc/ssh/ssh_host_rsa_key.pub","RSA2");
&viewkey("/etc/ssh/ssh_host_dsa_key.pub","DSA");

print "</table>\n";

&Header::closebox();

&Header::closebigbox();

&Header::closepage();


sub viewkey
{
  my $key = $_[0];
  my $name = $_[1];

  if ( -e $key )
  {
    my @temp = split(/ /,`/usr/bin/ssh-keygen -l -f $key`);
    my $keysize = &Header::cleanhtml($temp[0],"y");
    my $fingerprint = &Header::cleanhtml($temp[1],"y");
    print "<tr><td>$key ($name)</td><td><code>$fingerprint</code></td><td align='center'>$keysize</td></tr>\n";
  }
}
