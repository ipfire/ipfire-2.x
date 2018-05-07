#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2014  IPFire Team  <info@ipfire.org>                     #
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

use IO::Socket;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/geoip-functions.pl";
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %color = ();
my %mainsettings = ();
my %remotesettings=();
my %checked=();
my $errormessage='';
my $counter = 0;

&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

&Header::showhttpheaders();

$remotesettings{'ENABLE_SSH'} = 'off';
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
	
	if ($remotesettings{'SSH_PORT'} eq 'on')
	{
		&General::log("SSH Port 22");
	}
	else
	{
		&General::log("SSH Port 222");
	}
	
if ( $remotesettings{'ACTION'} eq $Lang::tr{'ssh tempstart15'} || $remotesettings{'ACTION'} eq $Lang::tr{'ssh tempstart30'} ){
	if ($remotesettings{'ENABLE_SSH'} eq 'off')
	{
			system ('/usr/bin/touch', "${General::swroot}/remote/enablessh");
			system('/usr/local/bin/sshctrl');
	}
  if ( $remotesettings{'ACTION'} eq $Lang::tr{'ssh tempstart15'} ) { $counter = 900;}
  elsif ( $remotesettings{'ACTION'} eq $Lang::tr{'ssh tempstart30'} ) { $counter = 1800;}
 
  system("/usr/local/bin/sshctrl tempstart $counter >/dev/null");
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
$checked{'ENABLE_SSH_PORTFW'}{'off'} = '';
$checked{'ENABLE_SSH_PORTFW'}{'on'} = '';
$checked{'ENABLE_SSH_PORTFW'}{$remotesettings{'ENABLE_SSH_PORTFW'}} = "checked='checked'";
$checked{'ENABLE_SSH_PASSWORDS'}{'off'} = '';
$checked{'ENABLE_SSH_PASSWORDS'}{'on'} = '';
$checked{'ENABLE_SSH_PASSWORDS'}{$remotesettings{'ENABLE_SSH_PASSWORDS'}} = "checked='checked'";
$checked{'ENABLE_SSH_KEYS'}{'off'} = '';
$checked{'ENABLE_SSH_KEYS'}{'on'} = '';
$checked{'ENABLE_SSH_KEYS'}{$remotesettings{'ENABLE_SSH_KEYS'}} = "checked='checked'";
$checked{'SSH_PORT'}{'off'} = '';
$checked{'SSH_PORT'}{'on'} = '';
$checked{'SSH_PORT'}{$remotesettings{'SSH_PORT'}} = "checked='checked'";

&Header::openpage($Lang::tr{'remote access'}, 1, '');

&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<font class='base'>$errormessage&nbsp;</font>\n";
	&Header::closebox();
}

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

&Header::openbox('100%', 'left', $Lang::tr{'ssh'});
print <<END
<table width='100%'>
<tr>
	<td><input type='checkbox' name='ENABLE_SSH' $checked{'ENABLE_SSH'}{'on'} /></td>
	<td class='base' colspan='2'>$Lang::tr{'ssh access'}</td>
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
	<td>&nbsp;</td>
	<td><input type='checkbox' name='SSH_PORT' $checked{'SSH_PORT'}{'on'} /></td>
	<td width='100%' class='base'>$Lang::tr{'ssh port'}</td>
</tr>
<tr>
	<td align='right' colspan='3'>
	<input type='submit' name='ACTION' value='$Lang::tr{'ssh tempstart15'}' />
	<input type='submit' name='ACTION' value='$Lang::tr{'ssh tempstart30'}' />
	<input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
</tr>
</table>
END
;
&Header::closebox();

print "</form>\n";

&Header::openbox('100%', 'center', $Lang::tr{'ssh host keys'});

print "<table class='tbl'>\n";

print <<END
<thead>
	<tr>
		<th align="center"><strong>$Lang::tr{'ssh key'}</strong></th>
		<th align="center"><strong>$Lang::tr{'type'}</strong></th>
		<th align="center"><strong>$Lang::tr{'ssh fingerprint'}</strong></th>
		<th align="center"><strong>$Lang::tr{'ssh key size'}</strong></th>
	</tr>
</thead>
<tbody>
END
;

&viewkey("/etc/ssh/ssh_host_key.pub","RSA1");
&viewkey("/etc/ssh/ssh_host_rsa_key.pub","RSA2");
&viewkey("/etc/ssh/ssh_host_dsa_key.pub","DSA");
&viewkey("/etc/ssh/ssh_host_ecdsa_key.pub","ECDSA");
&viewkey("/etc/ssh/ssh_host_ed25519_key.pub","ED25519");

print "</tbody>\n</table>\n";

&Header::closebox();

&Header::openbox('100%', 'center', $Lang::tr{'ssh active sessions'});

print <<END;
		<table class="tbl" width='66%'>
			<thead>
				<tr>
					<th align="center">
						<strong>$Lang::tr{'ssh username'}</strong>
					</th>
					<th align="center">
						<strong>$Lang::tr{'ssh login time'}</strong>
					</th>
					<th align="center">
						<strong>$Lang::tr{'ip address'}</strong>
					</th>
					<th align="center">
						<strong>$Lang::tr{'country'}</strong>
					</th>
					<th align="center">
						<strong>$Lang::tr{'rdns'}</strong>
					</th>
				</tr>
			</thead>
			<tbody>
END

&printactivelogins();

print "</tbody>\n</table>\n";

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
    print "<tr><td><code>$key</code></td><td align='center'>$name</td><td><code>$fingerprint</code></td><td align='center'>$keysize</td></tr>\n";
  }
}

sub printactivelogins()
{
	# print active SSH logins (grep outpout of "who -s")
	my $command = "who -s";
	my @output = `$command`;
	chomp(@output);

	my $id = 0;

	if ( scalar(@output) == 0 )
	{
		# no logins appeared
		my $table_colour = ($id++ % 2) ? $color{'color22'} : $color{'color20'};
		print "<tr bgcolor='$table_colour'><td colspan='5'>$Lang::tr{'ssh no active logins'}</td></tr>\n";
	} else {
		# list active logins...

		foreach my $line (@output)
		{
			my @arry = split(/\ +/, $line);

			my $username = @arry[0];
			my $logintime = join(' ', @arry[2..4]);
			my $remoteip = @arry[5];
			$remoteip =~ s/[()]//g;

			# display more information about that IP adress...
			my $ccode = &GeoIP::lookup($remoteip);
			my $flag_icon = &GeoIP::get_flag_icon($ccode);

			# get rDNS...
			my $iaddr = inet_aton($remoteip);
			my $rdns = gethostbyaddr($iaddr, AF_INET);
			if (!$rdns) { $rdns = $Lang::tr{'lookup failed'}; };

			my $table_colour = ($id++ % 2) ? $color{'color22'} : $color{'color20'};

			print <<END;
			<tr bgcolor='$table_colour'>
				<td>$username</td>
				<td>$logintime</td>
				<td align='center'><a href='ipinfo.cgi?ip=$remoteip'>$remoteip</a></td>
				<td align='center'><a href='country.cgi#$ccode'><img src='$flag_icon' border='0' alt='$ccode' title='$ccode' /></a></td>
				<td>$rdns</td>
			</tr>
END
;
		}
	}
}
