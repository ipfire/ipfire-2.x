#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2005-2013  IPFire Team  <info@ipfire.org>                     #
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

my %sambasettings = ();
my %cgisettings = ();
my %checked = ();
my %netsettings = ();
my %color = ();
my %mainsettings = ();
my $message = "";
my $errormessage = "";

my $Status = qx(/usr/local/bin/sambactrl smbstatus);
$Status = &Header::cleanhtml($Status);

my $userentry = "";
my @user = ();
my @userline = ();
my $userfile = "${General::swroot}/samba/private/smbpasswd";
my %selected= () ;

my $defaultoption= "[Share]\npath = /var/ipfire/samba/share1\ncomment = Share - Public Access\nbrowseable = yes\nwriteable = yes\ncreate mask = 0777\ndirectory mask = 0777\npublic = yes\nforce user = samba";
my %shares = ();

&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

############################################################################################################################
############################################# Samba Dienste fr Statusberprfung ##########################################

&Header::showhttpheaders();

############################################################################################################################
#################################### Initialisierung von Samba Variablen fr global Settings ###############################

$sambasettings{'WORKGRP'} = 'homeip.net';
$sambasettings{'INTERFACES'} = '';
$sambasettings{'SECURITY'} = 'user';
$sambasettings{'REMOTEANNOUNCE'} = '';
$sambasettings{'REMOTESYNC'} = '';
$sambasettings{'GUESTACCOUNT'} = 'samba';
$sambasettings{'MAPTOGUEST'} = 'Bad User';
$sambasettings{'WIDELINKS'} = 'on';
$sambasettings{'UNIXEXTENSION'} = 'off';
$sambasettings{'ENCRYPTION'} = 'optional';
### Values that have to be initialized
$sambasettings{'ACTION'} = '';
my $LOGLINES = '50';

############################################################################################################################

&General::readhash("${General::swroot}/samba/settings", \%sambasettings);
&Header::getcgihash(\%sambasettings);

if (($sambasettings{'WIDELINKS'} eq 'on') & ($sambasettings{'UNIXEXTENSION'} eq 'on'))
  {$errormessage = "$errormessage<br />Don't enable 'Wide links' and 'Unix extension' at the same time"; }

&Header::openpage('Samba', 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
############################################# Samba Rootskript aufrufe fr SU-Actions #######################################

if ($sambasettings{'ACTION'} eq 'smbuserdisable'){system("/usr/local/bin/sambactrl smbuserdisable $sambasettings{'NAME'}");}
if ($sambasettings{'ACTION'} eq 'smbuserenable'){system("/usr/local/bin/sambactrl smbuserenable $sambasettings{'NAME'}");}
if ($sambasettings{'ACTION'} eq 'smbuseradd'){system("/usr/local/bin/sambactrl smbuseradd $sambasettings{'USERNAME'} $sambasettings{'PASSWORD'} $sambasettings{'GROUP'} $sambasettings{'SHELL'}");}
if ($sambasettings{'ACTION'} eq 'smbpcadd'){system("/usr/local/bin/sambactrl smbpcadd $sambasettings{'PCNAME'} $sambasettings{'GROUP'} $sambasettings{'SHELL'}");}
if ($sambasettings{'ACTION'} eq 'smbchangepw'){system("/usr/local/bin/sambactrl smbchangepw $sambasettings{'USERNAME'} $sambasettings{'PASSWORD'}");}
if ($sambasettings{'ACTION'} eq 'smbrestart'){system("/usr/local/bin/sambactrl smbrestart");}
if ($sambasettings{'ACTION'} eq 'smbstart'){system("/usr/local/bin/sambactrl smbstart");}
if ($sambasettings{'ACTION'} eq 'smbstop'){system("/usr/local/bin/sambactrl smbstop");}
if ($sambasettings{'ACTION'} eq 'smbreload'){system("/usr/local/bin/sambactrl smbreload");}
if ($sambasettings{'ACTION'} eq 'join') {
	$message .= &joindomain($sambasettings{'USERNAME'}, $sambasettings{'PASSWORD'});
}

############################################################################################################################
########################################### Samba Benutzer oder PC l�chen #################################################

if ($sambasettings{'ACTION'} eq 'userdelete'){system("/usr/local/bin/sambactrl smbuserdelete $sambasettings{'NAME'}");}

############################################################################################################################
##################################### Umsetzen der Werte von Checkboxen und Dropdowns ######################################

if ($sambasettings{'ACTION'} eq $Lang::tr{'save'})
{
############################################################################################################################
##################################### Schreiben settings und bersetzen fr smb.conf #######################################

delete $sambasettings{'__CGI__'};delete $sambasettings{'x'};delete $sambasettings{'y'};
&General::writehash("${General::swroot}/samba/settings", \%sambasettings);

if ($sambasettings{'WIDELINKS'} eq 'on'){ $sambasettings{'WIDELINKS'} = "yes";} else { $sambasettings{'WIDELINKS'} = "no";}
if ($sambasettings{'UNIXEXTENSION'} eq 'on'){ $sambasettings{'UNIXEXTENSION'} = "yes";} else { $sambasettings{'UNIXEXTENSION'} = "no";}

############################################################################################################################
############################################# Schreiben der Samba globals ##################################################

	open (FILE, ">${General::swroot}/samba/global") or die "Can't save the global settings: $!";
	flock (FILE, 2);
	
print FILE <<END
# global.settings by IPFire Project

[global]
server string = Samba on IPFire

workgroup = $sambasettings{'WORKGRP'}
realm = $mainsettings{'DOMAINNAME'}
passdb backend = smbpasswd

wide links = $sambasettings{'WIDELINKS'}
unix extensions = $sambasettings{'UNIXEXTENSION'}

map to guest = $sambasettings{'MAPTOGUEST'}

security = $sambasettings{'SECURITY'}
guest account = $sambasettings{'GUESTACCOUNT'}
unix password sync = no

bind interfaces only = true
interfaces = green0 blue0 127.0.0.0/8
remote announce = $sambasettings{'REMOTEANNOUNCE'}
remote browse sync = $sambasettings{'REMOTESYNC'}

winbind separator = +
winbind uid = 10000-20000
winbind gid = 10000-20000
winbind use default domain = yes

# Log to syslog
logging = syslog

END
;

if ($sambasettings{'ENCRYPTION'} =~ m/(desired|required)/) {
	print FILE "smb encrypt = $1\n";
}

print FILE <<END;
# Export all printers
[printers]
path = /var/spool/samba/
printable = yes

END
close FILE;

system("/usr/local/bin/sambactrl smbsafeconf");
system("/usr/local/bin/sambactrl smbreload");
}
  &General::readhash("${General::swroot}/samba/settings", \%sambasettings);
  

if ($errormessage)
	{
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<class name='base'>$errormessage\n";
	print "&nbsp;</class>\n";
	&Header::closebox();
	}

if ($message) {
	$message = &Header::cleanhtml($message);
	$message =~ s/\n/<br>/g;

	&Header::openbox('100%', 'left', $Lang::tr{'messages'});
	print "$message\n";
	&Header::closebox();
}

############################################################################################################################
########################################## Aktivieren von Checkboxen und Dropdowns #########################################

$checked{'WIDELINKS'}{'off'} = '';
$checked{'WIDELINKS'}{'on'} = '';
$checked{'WIDELINKS'}{$sambasettings{'WIDELINKS'}} = "checked='checked'";
$checked{'UNIXEXTENSION'}{'off'} = '';
$checked{'UNIXEXTENSION'}{'on'} = '';
$checked{'UNIXEXTENSION'}{$sambasettings{'UNIXEXTENSION'}} = "checked='checked'";
$selected{'ENCRYPTION'}{'optional'} = '';
$selected{'ENCRYPTION'}{'desired'} = '';
$selected{'ENCRYPTION'}{'required'} = '';
$selected{'ENCRYPTION'}{$sambasettings{'ENCRYPTION'}} = "selected='selected'";

if ( $sambasettings{'MAPTOGUEST'} eq "Never" ) {
	$sambasettings{'MAPTOGUEST'}="Bad User";
}
$selected{'MAPTOGUEST'}{$sambasettings{'MAPTOGUEST'}} = "selected='selected'";
$selected{'SECURITY'}{$sambasettings{'SECURITY'}} = "selected='selected'";

############################################################################################################################
################################### Aufbau der HTML Seite fr globale Sambaeinstellungen ###################################

&Header::openbox('100%', 'center', $Lang::tr{'samba'});

my %servicenames = (
	"nmbd"     => $Lang::tr{'netbios nameserver daemon'},
	"smbd"     => $Lang::tr{'smb daemon'},
	"winbindd" => $Lang::tr{'winbind daemon'},
);

print <<END;
	<table class="tbl" width='95%' cellspacing='0'>
		<tr bgcolor='$color{'color20'}'>
			<td colspan='2' align='left'><b>$Lang::tr{'all services'}</b></td>
		</tr>
END

foreach my $service (sort keys %servicenames) {
	my $status = &isrunning($service);

	print <<END;
		<tr>
			<td align='left' width='40%'>$servicenames{$service}</td>
			$status
		</tr>
END
}

print <<END
	</table>

	<br>

	<table width="95%">
		<td width="33%" align="center">
			<form method="POST" action="$ENV{'SCRIPT_NAME'}">
				<input type="hidden" name="ACTION" value="smbstart">
				<input type="submit" value="$Lang::tr{'enable'}">
			</form>
		</td>

		<td width="33%" align="center">
			<form method="POST" action="$ENV{'SCRIPT_NAME'}">
				<input type="hidden" name="ACTION" value="smbstop">
				<input type="submit" value="$Lang::tr{'disable'}">
			</form>
		</td>

		<td width="33%" align="center">
			<form method="POST" action="$ENV{'SCRIPT_NAME'}">
				<input type="hidden" name="ACTION" value="smbrestart">
				<input type="submit" value="$Lang::tr{'restart'}">
			</form>
		</td>
	</table>

	<br>

	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table class="tbl" width='95%' cellspacing='0'>
			<tr bgcolor='$color{'color20'}'>
				<td colspan='2' align='left'><b>$Lang::tr{'basic options'}</b></td>
			</tr>
			<tr>
				<td align='left' width='40%'>$Lang::tr{'workgroup'}</td>
				<td align='left'>
					<input type='text' name='WORKGRP' value='$sambasettings{'WORKGRP'}' size="30" />
				</td>
			</tr>
			<tr>
				<td align='left'><br /></td>
				<td></td>
			</tr>
			<tr>
				<td align='left' width='40%'>Wide links</td>
				<td align='left'>
					on <input type='radio' name='WIDELINKS' value='on' $checked{'WIDELINKS'}{'on'} /> /
					<input type='radio' name='WIDELINKS' value='off' $checked{'WIDELINKS'}{'off'} /> off
				</td>
			</tr>
			<tr>
				<td align='left' width='40%'>Unix extension</td>
				<td align='left'>
					on <input type='radio' name='UNIXEXTENSION' value='on' $checked{'UNIXEXTENSION'}{'on'} /> /
					<input type='radio' name='UNIXEXTENSION' value='off' $checked{'UNIXEXTENSION'}{'off'} /> off
				</td>
			</tr>
			<tr>
				<td align='left'><br /></td>
				<td></td>
			</tr>
			<tr bgcolor='$color{'color20'}'>
				<td colspan='2' align='left'><b>$Lang::tr{'security options'}</b></td>
			</tr>
			<tr>
				<td align='left' width='40%'>$Lang::tr{'security'}</td>
				<td align='left'>
					<select name='SECURITY' style="width: 165px">
						<option value='user' $selected{'SECURITY'}{'user'}>User</option>
						<option value='ADS' $selected{'SECURITY'}{'ADS'}>ADS</option>
						<option value='server' $selected{'SECURITY'}{'server'}>Server</option>
					</select>
				</td>
			</tr>
			<tr>
				<td align='left' width='40%'>$Lang::tr{'encryption'}</td>
				<td align='left'>
					<select name='ENCRYPTION' style="width: 165px">
						<option value='optional' $selected{'ENCRYPTION'}{'optional'}>$Lang::tr{'optional'}</option>
						<option value='desired' $selected{'ENCRYPTION'}{'desired'}>$Lang::tr{'desired'}</option>
						<option value='required' $selected{'ENCRYPTION'}{'required'}>$Lang::tr{'required'}</option>
					</select>
				</td>
			</tr>
			<tr>
				<td align='left' width='40%'>$Lang::tr{'map to guest'}</td>
				<td align='left'>
					<select name='MAPTOGUEST' style="width: 165px">
						<option value='Bad User' $selected{'MAPTOGUEST'}{'Bad User'}>Bad User</option>
						<option value='Bad Password' $selected{'MAPTOGUEST'}{'Bad Password'}>Bad Password</option>
					</select>
				</td>
			</tr>
			<tr>
				<td align='left'><br /></td>
				<td></td>
			</tr>
			<tr bgcolor='$color{'color20'}'>
				<td colspan='2' align='left'><b>$Lang::tr{'network options'}</b></td>
			</tr>
			<tr>
				<td align='left' width='40%'>$Lang::tr{'remote announce'}</td>
				<td align='left'>
					<input type='text' name='REMOTEANNOUNCE' value='$sambasettings{'REMOTEANNOUNCE'}' size="30" />
				</td>
			</tr>
			<tr>
				<td align='left' width='40%'>$Lang::tr{'remote browse sync'}</td>
				<td align='left'>
					<input type='text' name='REMOTESYNC' value='$sambasettings{'REMOTESYNC'}' size="30" />
				</td>
			</tr>
		</table>

		<br>

		<table width='100%' cellspacing='0'>
			<tr>
				<td align='center'>
					<form method='POST' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='ACTION' value="$Lang::tr{'save'}">
						<input type='submit' value="$Lang::tr{'save'}">
					</form>
				</td>
			</tr>
		</table>
END
;

&Header::closebox();

############################################################################################################################
########################################## Benutzerverwaltung fr Usersecurity #############################################

if ($sambasettings{'SECURITY'} eq 'user')
	{
	&Header::openbox('100%', 'center', $Lang::tr{'user management'});
	print <<END
	<a name="$Lang::tr{'accounting'}"></a>
	<br />
	<table class="tbl" width='95%' cellspacing='0'>
	<tr><td colspan='6' align='left'></td></tr>
	<tr><td bgcolor='$color{'color20'}' colspan='7' align='left'><b>$Lang::tr{'accounting'}</b></td></tr>
	<tr><td align='left'><u>$Lang::tr{'username'}</u></td><td align='left'><u>$Lang::tr{'password'}</u></td>
END
;

	print "<td></td>";
	print "<td align='left'><u>$Lang::tr{'status'}</u></td><td colspan='3' width='5%' align='center'><u>$Lang::tr{'options'}</u></td></tr>";
	system('/usr/local/bin/sambactrl readsmbpasswd');
	open(FILE, "<${General::swroot}/samba/private/smbpasswd") or die "Can't read user file: $!";
	@user = <FILE>;
	close(FILE);
	system('/usr/local/bin/sambactrl locksmbpasswd');
	
	my $lines = 0;
	
	foreach $userentry (sort @user)
		{
		@userline = split( /\:/, $userentry );
    if ($lines % 2) {print "<tr bgcolor='$color{'color20'}'>";} else {print "<tr bgcolor='$color{'color22'}'>";}
		print "<td align='left'>$userline[0]</td><td align='left'>";
		if ($userline[4] =~ /N/)
			{
			print "$Lang::tr{'not set'}</td><td align='left'>";
			}
		else
			{
			print "$Lang::tr{'set'}</td><td align='left'>";
			}

		print "</td><td align='left'>";

		if ($userline[4] =~ /D/)
			{
			print <<END
			$Lang::tr{'inactive'}</td>
			<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}#$Lang::tr{'accounting'}'>
					<input type='hidden' name='NAME' value='$userline[0]' />
					<input type='hidden' name='ACTION' value='smbuserenable' />
					<input type='image' alt='$Lang::tr{'activate'}' title='$Lang::tr{'activate'}' src='/images/off.gif' />
			</form></td>
END
;
			}
		else
			{
			print <<END
			$Lang::tr{'active'}</td>
			<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}#$Lang::tr{'accounting'}'>
					<input type='hidden' name='NAME' value='$userline[0]' />
					<input type='hidden' name='ACTION' value='smbuserdisable' />
					<input type='image' alt='$Lang::tr{'deactivate'}' title='$Lang::tr{'deactivate'}' src='/images/on.gif' />
			</form></td>
END
;
			}

		if ($userline[0] =~ /\$/)
			{
			print "<td></td>";
			}
		else
			{
			print <<END
			<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}#$Lang::tr{'accounting'}'>
					<input type='hidden' name='NAME' value='$userline[0]' />
					<input type='hidden' name='ACTION' value='userchangepw' />
					<input type='image' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' src='/images/edit.gif' />
			</form></td>
END
;
			}

			print <<END
			<td><form method='post' action='$ENV{'SCRIPT_NAME'}#$Lang::tr{'accounting'}'>
					<input type='hidden' name='NAME' value='$userline[0]' />
					<input type='hidden' name='ACTION' value='userdelete' />
					<input type='image' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' src='/images/user-option-remove.png' />
			</form></td></tr>
END
;
		$lines++;
		}
	print <<END
	</table>
	<br />
	<table width='10%' cellspacing='0'>
	<tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}#$Lang::tr{'accounting'}'>
													<input type='hidden' name='ACTION' value='useradd' />
													<input type='image' alt='$Lang::tr{'add user'}' title='$Lang::tr{'add user'}' src='/images/user-option-add.png' /></form></td>
END
;

	print <<END
	<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}#$Lang::tr{'accounting'}'>
											<input type='hidden' name='ACTION' value='usercaption' />
											<input type='image' alt='$Lang::tr{'caption'}' title='$Lang::tr{'caption'}' src='/images/help-browser.png' /></form>
	</td></tr>
	</table>
END
;

	if ($sambasettings{'ACTION'} eq 'usercaption')
		{
		print <<END
		<br />
		<table width='95%' cellspacing='0'>
		<tr><td align='center' colspan='2'><b>$Lang::tr{'caption'}</b></td></tr>
		<tr><td align='right' width='33%'><img src='/images/user-option-add.png' /></td><td align='left'>$Lang::tr{'add user'}</td></tr>
		<tr><td align='right' width='33%'><img src='/images/network.png' /></td><td align='left'>$Lang::tr{'pc add'}</td></tr>
		<tr><td align='right' width='33%'><img src='/images/user-option-remove.png' /></td><td align='left'>$Lang::tr{'delete user'}</td></tr>
		<tr><td align='right' width='33%'><img src='/images/network-error.png' /></td><td align='left'>$Lang::tr{'delete pc'}</td></tr>
		<tr><td align='right' width='33%'><img src='/images/off.gif' /></td><td align='left'>$Lang::tr{'activate user'}</td></tr>
		<tr><td align='right' width='33%'><img src='/images/on.gif' /></td><td align='left'>$Lang::tr{'deactivate user'}</td></tr>
		<tr><td align='right' width='33%'><img src='/images/edit.gif' /></td><td align='left'>$Lang::tr{'change passwords'}</td></tr>
		<tr><td align='right' width='33%'><img src='/images/media-floppy.png' /></td><td align='left'>$Lang::tr{'save config'}</td></tr>
		</table>
END
;
		}

	if ($sambasettings{'ACTION'} eq 'userchangepw')
		{
		my $username = "$sambasettings{'NAME'}";
		my $password = 'samba';
		print <<END
		<br />
		<form method='post' action='$ENV{'SCRIPT_NAME'}#$Lang::tr{'accounting'}'>
		<table width='95%' cellspacing='0'>
		<tr bgcolor='$color{'color20'}'><td colspan='2' align='left'><b>$Lang::tr{'change passwords'}</b></td></tr>
		<tr><td align='left'>$Lang::tr{'username'}</td><td><input type='text' name='USERNAME' value='$username' size='30' readonly='readonly' /></td></tr>
		<tr><td align='left'>$Lang::tr{'password'}</td><td><input type='password' name='PASSWORD' value='$password' size='30' /></td></tr>
		<tr><td colspan='2' align='center'><input type='hidden' name='ACTION' value='smbchangepw' />
			<input type='image' alt='$Lang::tr{'save'}' title='$Lang::tr{'save'}' src='/images/media-floppy.png' /></td></tr>
		</table>
		</form>
END
;
		}

	if ($sambasettings{'ACTION'} eq 'useradd')
		{
		my $username = "user";
		my $password = "samba";
		chomp $username;
		$username=~s/\s//g;
		chomp $password;
		$password=~s/\s//g;
		print <<END
		<br />
		<form method='post' action='$ENV{'SCRIPT_NAME'}#$Lang::tr{'accounting'}'>
		<table width='95%' cellspacing='0'>
		<tr bgcolor='$color{'color20'}'><td colspan='2' align='left'><b>$Lang::tr{'add user'}</b></td></tr>
		<tr><td align='left'>$Lang::tr{'username'}</td><td><input type='text' name='USERNAME' value='$username' size='30' /></td></tr>
		<tr><td align='left'>$Lang::tr{'password'}</td><td><input type='password' name='PASSWORD' value='$password' size='30' /></td></tr>
		<tr><td align='left'>$Lang::tr{'unix group'}</td><td><input type='text' name='GROUP' value='sambauser' size='30' /></td></tr>
		<tr><td align='left'>$Lang::tr{'unix shell'}</td><td><input type='text' name='SHELL' value='/bin/false' size='30' /></td></tr>
		<tr><td colspan='2' align='center'><input type='hidden' name='ACTION' value='smbuseradd' />
			<input type='image' alt='$Lang::tr{'save'}' title='$Lang::tr{'save'}' src='/images/media-floppy.png' /></td></tr>
		</table>
		</form>
END
;
		}

	if ($sambasettings{'ACTION'} eq 'pcadd')
		{
		my $pcname = "client\$";
		chomp $pcname;
		$pcname=~s/\s//g;
		print <<END
		<br />
		<form method='post' action='$ENV{'SCRIPT_NAME'}#$Lang::tr{'accounting'}'>
		<table width='95%' cellspacing='0'>
		<tr bgcolor='$color{'color20'}'><td colspan='2' align='left'><b>$Lang::tr{'pc add'}</b></td></tr>
		<tr><td align='left'>$Lang::tr{'client'}</td><td><input type='text' name='PCNAME' value='$pcname' size='30' /></td></tr>
		<tr><td align='left'>$Lang::tr{'unix group'}</td><td><input type='text' name='GROUP' value='sambawks' size='30' /></td></tr>
		<tr><td align='left'>$Lang::tr{'unix shell'}</td><td><input type='text' name='SHELL' value='/bin/false' size='30' /></td></tr>
		<tr><td colspan='2' align='center'><input type='hidden' name='ACTION' value='smbpcadd' />
			<input type='image' alt='$Lang::tr{'save'}' title='$Lang::tr{'save'}' src='/images/media-floppy.png' /></td></tr>
		</table>
		</form>
END
;
		}

&Header::closebox();
}

if ($sambasettings{'SECURITY'} eq "ADS") {
	&Header::openbox('100%', 'center', $Lang::tr{'samba join a domain'});

	my $AD_DOMAINNAME = uc($mainsettings{'DOMAINNAME'});

	print <<END;
	<form method="POST" action="$ENV{'SCRIPT_NAME'}">
		<input type="hidden" name="ACTION" value="join">

		<table class="tbl" width="95%">
			<tbody>
				<tr>
					<td width="40%">
						$Lang::tr{'domain'}
					</td>
					<td>
						$AD_DOMAINNAME
					</td>
				</tr>
				<tr>
					<td width="40%">
						$Lang::tr{'administrator username'}
					</td>
					<td>
						<input type="text" name="USERNAME" size="30">
					</td>
				</tr>
				<tr>
					<td width="40%">
						$Lang::tr{'administrator password'}
					</td>
					<td>
						<input type="password" name="PASSWORD" size="30">
					</td>
				</tr>
				<tr>
					<td></td>
					<td>
						<input type="submit" value="$Lang::tr{'samba join domain'}">
					</td>
				</tr>
			</tbody>
		</table>
	</form>
END

	&Header::closebox();
}

############################################################################################################################
############################################### Verwalten von Freigaben ####################################################

&Header::openbox('100%', 'center', $Lang::tr{'shares'});

my %shares =  config("${General::swroot}/samba/shares");


print <<END
<a name="$Lang::tr{'manage shares'}"></a>
<br />
<table class="tbl" width='95%' cellspacing='0' class='tbl'>
<tr><th bgcolor='$color{'color20'}' colspan='3' align='left'><b>$Lang::tr{'manage shares'}</b></th></tr>
<tr><th align='left'><u>$Lang::tr{'sharename'}</u></th><th colspan='2' width="5%" align='center'><u>$Lang::tr{'options'}</u></th></tr>
END
;

my @Shares = keys(%shares);
my $lines = 0;
my $col="";
foreach my $shareentry (sort @Shares)
	{
	chomp $shareentry;
	if ($lines % 2) {
		print "<tr>";
		$col="bgcolor='$color{'color20'}'";
	} else {
		print "<tr>";
		$col="bgcolor='$color{'color22'}'";
	}
	print <<END
	<td align='left' $col>$shareentry</td>
	<td $col><form method='post' action='$ENV{'SCRIPT_NAME'}#$Lang::tr{'manage shares'}'>
			<input type='hidden' name='NAME' value='$shareentry' />
			<input type='hidden' name='ACTION' value='sharechange' />
			<input type='image' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' src='/images/edit.gif' />
	</form></td>
	<td $col><form method='post' action='$ENV{'SCRIPT_NAME'}#$Lang::tr{'manage shares'}'>
			<input type='hidden' name='NAME' value='$shareentry' />
			<input type='hidden' name='ACTION' value='smbsharedel' />
			<input type='image' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' src='/images/user-trash.png' />
	</form></td></tr>
END
;
  $lines++;
	}

print <<END
</table>
<br />
<table width='10%' cellspacing='0'>
<tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}#$Lang::tr{'manage shares'}'>
												<input type='hidden' name='ACTION' value='shareadd' />
												<input type='image' alt='$Lang::tr{'add share'}' title='$Lang::tr{'add share'}' src='/images/list-add.png' />
												</form></td>
		<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}#$Lang::tr{'manage shares'}'>
												<input type='hidden' name='ACTION' value='sharecaption' />
												<input type='image' alt='$Lang::tr{'caption'}' title='$Lang::tr{'caption'}' src='/images/help-browser.png' />
												</form></td>
</tr>
</table>
END
;

if ($sambasettings{'ACTION'} eq 'sharecaption')
	{
	print <<END
	<br />
	<table width='95%' cellspacing='0'>
	<tr><td align='center' colspan='2'><b>$Lang::tr{'caption'}</b></td></tr>
	<tr><td align='right' width='33%'><img src='/images/list-add.png' /></td><td align='left'>$Lang::tr{'add share'}</td></tr>
	<tr><td align='right' width='33%'><img src='/images/edit.gif' /></td><td align='left'>$Lang::tr{'edit share'}</td></tr>
	<tr><td align='right' width='33%'><img src='/images/media-floppy.png' /></td><td align='left'>$Lang::tr{'save config'}</td></tr>
	<tr><td align='right' width='33%'><img src='/images/user-trash.png' /></td><td align='left'>$Lang::tr{'delete share'}</td></tr>
	</table>
END
;
	}

if ($sambasettings{'ACTION'} eq 'shareadd' || $sambasettings{'ACTION'} eq 'optioncaption' )
	{
	print <<END
	<br />
	<table width='95%' cellspacing='0'>
	<tr bgcolor='$color{'color20'}'><td colspan='2' align='left'><b>$Lang::tr{'add share'}</b></td></tr>
	<tr><td colspan='2' align='center'></td></tr>
	<form method='post' action='$ENV{'SCRIPT_NAME'}#$Lang::tr{'manage shares'}'><tr><td colspan='2' align='center'><textarea name="SHAREOPTION" cols="50" rows="15" Wrap="off">$defaultoption</textarea></td></tr>
	</table>
	<br />
	<table width='10%' cellspacing='0'>
	<tr><td align='center'><input type='hidden' name='ACTION' value='smbshareadd' />
													<input type='image' alt='$Lang::tr{'add share'}' title='$Lang::tr{'add share'}' src='/images/media-floppy.png' /></td></tr></form>
	</table>
END
;
	}

if ($sambasettings{'ACTION'} eq 'sharechange' || $sambasettings{'ACTION'} eq 'optioncaption2' )
	{
	my $shareoption = $shares{$sambasettings{'NAME'}};
	print <<END
	<br />
	<table width='95%' cellspacing='0'>
	<tr bgcolor='$color{'color20'}'><td colspan='2' align='left'><b>$Lang::tr{'edit share'}</b></td></tr>
	<tr><td colspan='2' align='center'></td></tr>
	<tr><td colspan='2' align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}#$Lang::tr{'manage shares'}'><textarea name="SHAREOPTION" cols="50" rows="15" Wrap="off">$shareoption</textarea></td></tr>
	</table>
	<br />
	<table width='10%' cellspacing='0'>
	<tr><td align='center'><input type='hidden' name='NAME' value='$sambasettings{'NAME'}' />
													<input type='image' alt='$Lang::tr{'change share'}' title='$Lang::tr{'change share'}' src='/images/media-floppy.png' />
													<input type='hidden' name='ACTION' value='smbsharechange' /></form></td></tr>
	</table>
END
;
	}

if ($sambasettings{'ACTION'} eq 'smbshareadd')
	{
	$shares{'xvx'}= "$sambasettings{'SHAREOPTION'}";
	save("shares");
	my $shares = config("${General::swroot}/samba/shares");
	}
if ($sambasettings{'ACTION'} eq 'smbsharedel')
	{
	delete $shares{$sambasettings{'NAME'}};
	save("shares");
	my %shares = config("${General::swroot}/samba/shares");
	}
if ($sambasettings{'ACTION'} eq 'smbsharechange')
	{
	$shares{$sambasettings{'NAME'}} = $sambasettings{'SHAREOPTION'};
	save("shares");
	my %shares = config("${General::swroot}/samba/shares");
	}

&Header::closebox();

############################################################################################################################
############################################### Anzeige des Sambastatus ####################################################

&Header::openbox('100%', 'center', 'Status');

print <<END
<br />
<table class="tbl" width='95%' cellspacing='0'>
<tr><td bgcolor='$color{'color20'}' colspan='3' align='left'><b>$Lang::tr{'samba status'}</b></td></tr>
<tr><td  align='left'><small><pre>$Status</pre></small></td></tr>
</table>
END
;
&Header::closebox();

&Header::closebigbox();
&Header::closepage();

############################################################################################################################
############################################ Subfunktion fr Sambadienste ###################################################

sub config
{
my $file = shift;
my @allarray = `grep -n '^\\[' $file`;
my @linesarray = ();
my @namearray = ();
my %hash = ();
my $options = ();
my $EOF = qx(cat $file | wc -l);
foreach my $allarrayentry (@allarray)
 {
 my @allarrayline = split( /\:/, $allarrayentry );
 push(@linesarray,$allarrayline[0]);$allarrayline[1]=~s/\[//g;$allarrayline[1]=~s/\]//g;push(@namearray,$allarrayline[1]);
 }
	for(my $i = 0; $i <= $#namearray; $i++)
		{
		chomp $namearray[$i];
		$namearray[$i]=~s/\[//g;$namearray[$i]=~s/\]//g;
		if ( $i eq $#namearray )
			{
			my $lineend = $EOF-$linesarray[$i]+1;
			$options=qx(tail -$lineend $file);
			}
		else
			{
			my $linestart = $EOF-$linesarray[$i]+1;
			my $lineend =  $linesarray[$i+1]-$linesarray[$i];
			$options=qx(tail -$linestart $file | head -$lineend);
			}
		$hash{$namearray[$i]} = "$options";
		#print"<pre>$namearray[$i]\n$options\n</pre>"; # enable only for debuging
		}
return(%hash);
}

sub save
{
my $smb = shift;
open (FILE, ">${General::swroot}/samba/$smb") or die "Can't $smb settings $!";
flock (FILE, 2);

if ( $smb eq 'shares')
	{while (my ($name, $option) = each %shares){chomp $option;$option =~ s/\r\n/\n/gi;$option =~ s/^\n//gi;$option =~ s/^\r//gi;$option =~ s/^.\n//gi;$option =~ s/^.\r//gi;print FILE "$option\n";}	}

close FILE;

system("/usr/local/bin/sambactrl smbsafeconf");
system("/usr/local/bin/sambactrl smbreload");
}

sub isrunning
	{
	my $cmd = $_[0];
	my $status = "<td align='center' bgcolor='${Header::colourred}'><font color='white'><b>$Lang::tr{'stopped'}</b></font></td>";
	my $pid = '';
	my $testcmd = '';
	my $exename;

	$cmd =~ /(^[a-z]+)/;
	$exename = $1;

	if (open(FILE, "/var/run/${cmd}.pid"))
		{
		$pid = <FILE>; chomp $pid;
		close FILE;
		if (open(FILE, "/proc/${pid}/status"))
			{
			while (<FILE>)
				{
				if (/^Name:\W+(.*)/)
					{
					$testcmd = $1; 
					}
				}
			close FILE;
			if ($testcmd =~ /$exename/)
				{
				$status = "<td align='center' bgcolor='${Header::colourgreen}'><font color='white'><b>$Lang::tr{'running'}</b></font></td>";
				}
			}
		}
	return $status;
	}

sub joindomain {
	my $username = shift;
	my $password = shift;

	my @options = ("/usr/local/bin/sambactrl", "join", $username, $password);
	my $output = qx(@options);

	return $output;
}
