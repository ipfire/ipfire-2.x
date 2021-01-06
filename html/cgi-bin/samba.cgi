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

my $userentry = "";
my @user = ();
my @userline = ();
my $userfile = "${General::swroot}/samba/private/smbpasswd";
my %selected= () ;

my $defaultoption= "[My Share]\npath = \ncomment = Share - Public Access\nbrowseable = yes\nwriteable = yes\ncreate mask = 0644\ndirectory mask = 0755\npublic = yes\nforce user = samba";
my %shares = &config("${General::swroot}/samba/shares");

&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

############################################################################################################################
#################################### Initialisierung von Samba Variablen fr global Settings ###############################

$sambasettings{'WORKGRP'} = uc($mainsettings{'DOMAINNAME'});
$sambasettings{'ROLE'} = 'standalone';
$sambasettings{'REMOTEANNOUNCE'} = '';
$sambasettings{'REMOTESYNC'} = '';
$sambasettings{'GUESTACCOUNT'} = 'samba';
$sambasettings{'MAPTOGUEST'} = 'Bad User';
$sambasettings{'ENCRYPTION'} = 'optional';
### Values that have to be initialized
$sambasettings{'ACTION'} = '';
my $LOGLINES = '50';

############################################################################################################################

&General::readhash("${General::swroot}/samba/settings", \%sambasettings);

# Hook to regenerate the configuration files.
if ($ENV{"REMOTE_ADDR"} eq "") {
	&writeconfiguration();
	exit(0);
}

&Header::showhttpheaders();

&Header::getcgihash(\%sambasettings);
delete $sambasettings{'__CGI__'};delete $sambasettings{'x'};delete $sambasettings{'y'};

&Header::openpage('Samba', 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
############################################# Samba Rootskript aufrufe fr SU-Actions #######################################

if ($sambasettings{'ACTION'} eq 'smbuserdisable'){system("/usr/local/bin/sambactrl smbuserdisable $sambasettings{'NAME'}");}
if ($sambasettings{'ACTION'} eq 'smbuserenable'){system("/usr/local/bin/sambactrl smbuserenable $sambasettings{'NAME'}");}
if ($sambasettings{'ACTION'} eq 'smbuseradd'){system("/usr/local/bin/sambactrl smbuseradd $sambasettings{'USERNAME'} $sambasettings{'PASSWORD'}");}
if ($sambasettings{'ACTION'} eq 'smbchangepw'){system("/usr/local/bin/sambactrl smbchangepw $sambasettings{'USERNAME'} $sambasettings{'PASSWORD'}");}
if ($sambasettings{'ACTION'} eq 'smbrestart'){system("/usr/local/bin/sambactrl smbrestart");}
if ($sambasettings{'ACTION'} eq 'smbstart'){system("/usr/local/bin/sambactrl smbstart");}
if ($sambasettings{'ACTION'} eq 'smbstop'){system("/usr/local/bin/sambactrl smbstop");}
if ($sambasettings{'ACTION'} eq 'smbreload'){system("/usr/local/bin/sambactrl smbreload");}
if ($sambasettings{'ACTION'} eq 'join') {
	$message .= &joindomain($sambasettings{'USERNAME'}, $sambasettings{'PASSWORD'});
}

if ($sambasettings{'ACTION'} eq 'smbshareadd') {
	$shares{'xvx'} = $sambasettings{'SHAREOPTION'};
	&save("shares");

	# Reload configuration
	%shares = config("${General::swroot}/samba/shares");
}

if ($sambasettings{'ACTION'} eq 'smbsharedel') {
	delete $shares{$sambasettings{'NAME'}};
	&save("shares");

	# Reload configuration
	%shares = config("${General::swroot}/samba/shares");
}

if ($sambasettings{'ACTION'} eq 'smbsharechange') {
	$shares{$sambasettings{'NAME'}} = $sambasettings{'SHAREOPTION'};
	&save("shares");

	# Reload configuration
	%shares = config("${General::swroot}/samba/shares");
}

############################################################################################################################
########################################### Samba Benutzer oder PC l�chen #################################################

if ($sambasettings{'ACTION'} eq 'userdelete'){system("/usr/local/bin/sambactrl smbuserdelete $sambasettings{'NAME'}");}

############################################################################################################################
##################################### Umsetzen der Werte von Checkboxen und Dropdowns ######################################

############################################################################################################################
##################################### Schreiben settings und bersetzen fr smb.conf #######################################

if ($sambasettings{'ACTION'} eq $Lang::tr{'save'}) {
	&General::writehash("${General::swroot}/samba/settings", \%sambasettings);

	# Write configuration to file
	&writeconfiguration();

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

$selected{'ENCRYPTION'}{'optional'} = '';
$selected{'ENCRYPTION'}{'desired'} = '';
$selected{'ENCRYPTION'}{'required'} = '';
$selected{'ENCRYPTION'}{$sambasettings{'ENCRYPTION'}} = "selected='selected'";
$selected{'ROLE'}{'standalone'} = '';
$selected{'ROLE'}{'member'} = '';
$selected{'ROLE'}{$sambasettings{'ROLE'}} = "selected='selected'";

if ( $sambasettings{'MAPTOGUEST'} eq "Never" ) {
	$sambasettings{'MAPTOGUEST'}="Bad User";
}
$selected{'MAPTOGUEST'}{$sambasettings{'MAPTOGUEST'}} = "selected='selected'";

############################################################################################################################
################################### Aufbau der HTML Seite fr globale Sambaeinstellungen ###################################

&Header::openbox('100%', 'center', $Lang::tr{'samba'});

my %servicenames = (
	"nmbd"     => $Lang::tr{'netbios nameserver daemon'},
	"smbd"     => $Lang::tr{'smb daemon'},
	"winbindd" => $Lang::tr{'winbind daemon'},
);

print <<END;
	<table class="tbl" width='100%' cellspacing='0'>
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

	<table width="100%">
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
		<table class="tbl" width='100%' cellspacing='0'>
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
			<tr bgcolor='$color{'color20'}'>
				<td colspan='2' align='left'><b>$Lang::tr{'security options'}</b></td>
			</tr>
			<tr>
				<td align='left' width='40%'>$Lang::tr{'security'}</td>
				<td align='left'>
					<select name='ROLE' style="width: 165px">
						<option value='standalone' $selected{'ROLE'}{'standalone'}>$Lang::tr{'samba server role standalone'}</option>
						<option value='member' $selected{'ROLE'}{'member'}>$Lang::tr{'samba server role member'}</option>
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

if ($sambasettings{'ROLE'} eq 'standalone') {
	&Header::openbox('100%', 'center', $Lang::tr{'user management'});

	print <<END;
		<table class="tbl" width='100%' cellspacing='0'>
			<tr>
				<th align='left'>$Lang::tr{'user'}</th>
				<th colspan='3' width='5%'></th>
			</tr>
END

	system('/usr/local/bin/sambactrl readsmbpasswd');
	open(FILE, "<${General::swroot}/samba/private/smbpasswd") or die "Can't read user file: $!";
	my @users = <FILE>;
	close(FILE);
	system('/usr/local/bin/sambactrl locksmbpasswd');

	my $lines = 0;
	foreach $userentry (sort @users) {
		@userline = split( /\:/, $userentry);

		if ($lines % 2) {
			print "<tr bgcolor='$color{'color20'}'>";
		} else {
			print "<tr bgcolor='$color{'color22'}'>";
		}

		# Print username
		print "<td align='left'>$userline[0]</td>";

		if ($userline[4] =~ /D/) {
			print <<END;
				<td align='center'>
					<form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='NAME' value='$userline[0]' />
						<input type='hidden' name='ACTION' value='smbuserenable' />
						<input type='image' alt='$Lang::tr{'activate'}' title='$Lang::tr{'activate'}' src='/images/off.gif' />
					</form>
				</td>
END
		} else {
			print <<END;
				<td align='center'>
					<form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='NAME' value='$userline[0]' />
						<input type='hidden' name='ACTION' value='smbuserdisable' />
						<input type='image' alt='$Lang::tr{'deactivate'}' title='$Lang::tr{'deactivate'}' src='/images/on.gif' />
					</form>
				</td>
END
		}

		# Machine accounts can't be edited
		if ($userline[0] =~ /\$/) {
			print "<td></td>";
		} else {
			print <<END;
				<td align='center'>
					<form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='NAME' value='$userline[0]' />
						<input type='hidden' name='ACTION' value='userchangepw' />
						<input type='image' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' src='/images/edit.gif' />
					</form>
				</td>
END
		}

		print <<END;
			<td align='center'>
				<form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='hidden' name='NAME' value='$userline[0]' />
					<input type='hidden' name='ACTION' value='userdelete' />
					<input type='image' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' src='/images/delete.gif' />
				</form>
			</td>
		</tr>
END
		$lines++;
	}

	print <<END;
		</table>

		<br>

		<table width='10%' cellspacing='0'>
			<tr>
				<td align='center'>
					<form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='ACTION' value='useradd'>
						<input type='submit' value='$Lang::tr{'add user'}'>
					</form>
				</td>
			</tr>
		</table>
END

	if ($sambasettings{'ACTION'} eq 'userchangepw') {
		my $username = $sambasettings{'NAME'};
		my $password = 'samba';

		print <<END
			<br>
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
				<table width='100%' cellspacing='0'>
					<tr bgcolor='$color{'color20'}'>
						<td colspan='2' align='left'><b>$Lang::tr{'change passwords'}</b></td>
					</tr>
					<tr>
						<td align='left'>$Lang::tr{'username'}</td>
						<td>
							<input type='text' name='USERNAME' value='$username' size='30' readonly='readonly' />
						</td>
					</tr>
					<tr>
						<td align='left'>$Lang::tr{'password'}</td>
						<td>
							<input type='password' name='PASSWORD' value='$password' size='30' />
						</td>
					</tr>
					<tr>
						<td colspan='2' align='center'>
							<input type='hidden' name='ACTION' value='smbchangepw'>
							<input type='submit' value='$Lang::tr{'save'}'>
						</td>
					</tr>
				</table>
			</form>
END
	}

	if ($sambasettings{'ACTION'} eq 'useradd') {
		my $username = "user";
		my $password = "samba";
		chomp $username;
		$username=~s/\s//g;
		chomp $password;
		$password=~s/\s//g;

		print <<END;
			<br>

			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
				<table width='100%' cellspacing='0'>
					<tr bgcolor='$color{'color20'}'>
						<td colspan='2' align='left'><b>$Lang::tr{'add user'}</b></td>
					</tr>
					<tr>
						<td align='left'>$Lang::tr{'username'}</td>
						<td>
							<input type='text' name='USERNAME' value='$username' size='30' />
						</td>
					</tr>
					<tr>
						<td align='left'>$Lang::tr{'password'}</td>
						<td>
							<input type='password' name='PASSWORD' value='$password' size='30' />
						</td>
					</tr>
					<tr>
						<td colspan='2' align='center'>
							<input type='hidden' name='ACTION' value='smbuseradd'>
							<input type='submit' value='$Lang::tr{'save'}'>
						</td>
					</tr>
				</table>
			</form>
END
	}

	&Header::closebox();
}

if ($sambasettings{'ROLE'} eq "member") {
	&Header::openbox('100%', 'center', $Lang::tr{'samba join a domain'});

	my $AD_DOMAINNAME = uc($mainsettings{'DOMAINNAME'});

	print <<END;
	<form method="POST" action="$ENV{'SCRIPT_NAME'}">
		<input type="hidden" name="ACTION" value="join">

		<table width="100%">
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

print <<END;
	<table class="tbl" width='100%' cellspacing='0'>
		<tr>
			<th align='left'>$Lang::tr{'sharename'}</th>
			<th colspan='2' width="5%" align='center'></th>
		</tr>
END

my @shares = keys(%shares);
my $lines = 0;
my $col="";
foreach my $shareentry (sort @shares) {
	chomp $shareentry;

	if ($lines % 2) {
		$col = "bgcolor='$color{'color20'}'";
	} else {
		$col = "bgcolor='$color{'color22'}'";
	}

	print <<END;
		<tr>
			<td align='left' $col>$shareentry</td>
			<td $col>
				<form method='post' action='$ENV{'SCRIPT_NAME'}#$Lang::tr{'manage shares'}'>
					<input type='hidden' name='NAME' value='$shareentry' />
					<input type='hidden' name='ACTION' value='sharechange' />
					<input type='image' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' src='/images/edit.gif' />
				</form>
			</td>
			<td $col>
				<form method='post' action='$ENV{'SCRIPT_NAME'}#$Lang::tr{'manage shares'}'>
					<input type='hidden' name='NAME' value='$shareentry' />
					<input type='hidden' name='ACTION' value='smbsharedel' />
					<input type='image' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' src='/images/delete.gif' />
				</form>
			</td>
		</tr>
END
;
	$lines++;
}

print <<END;
	</table>

	<br>

	<table width='100%' cellspacing='0'>
		<tr>
			<td align='center'>
				<form method='POST' action='$ENV{'SCRIPT_NAME'}'>
					<input type='hidden' name='ACTION' value='shareadd'>
					<input type='submit' value='$Lang::tr{'add share'}'>
				</form>
			</td>
		</tr>
	</table>
END

if ($sambasettings{'ACTION'} eq 'shareadd') {
	print <<END;
		<br />

		<form method='POST' action='$ENV{'SCRIPT_NAME'}'>
			<table width='100%' cellspacing='0'>
				<tr bgcolor='$color{'color20'}'>
					<td align='left'><b>$Lang::tr{'add share'}</b></td>
				</tr>
				<tr>
					<td align='center'>
						<textarea name="SHAREOPTION" cols="121" rows="15">$defaultoption</textarea>
					</td>
				</tr>
				<tr>
					<td align='center'>
						<input type='hidden' name='ACTION' value='smbshareadd'>
						<input type='submit' value='$Lang::tr{'save'}'>
					</td>
				</tr>
			</table>
		</form>
END
}

if ($sambasettings{'ACTION'} eq 'sharechange') {
	my $shareoption = $shares{$sambasettings{'NAME'}};

	print <<END;
		<br />

		<form method='POST' action='$ENV{'SCRIPT_NAME'}'>
			<input type='hidden' name='NAME' value='$sambasettings{'NAME'}'>

			<table width='100%' cellspacing='0'>
				<tr bgcolor='$color{'color20'}'>
					<td align='left'><b>$Lang::tr{'edit share'}</b></td>
				</tr>
				<tr>
					<td align='center'>
						<textarea name="SHAREOPTION" cols="121" rows="15">$shareoption</textarea>
					</td>
				</tr>
				<tr>
					<td align='center'>
						<input type='hidden' name='ACTION' value='smbsharechange'>
						<input type='submit' value='$Lang::tr{'save'}'>
					</td>
				</tr>
			</table>
		</form>
END
}

&Header::closebox();

############################################################################################################################
############################################### Anzeige des Sambastatus ####################################################

&Header::openbox('100%', 'left', $Lang::tr{'status'});

my $status = qx(/usr/local/bin/sambactrl smbstatus);
$status = &Header::cleanhtml($status);

print <<END;
	<small>
		<pre>$status</pre>
	</small>
END

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

sub writeconfiguration() {
	open (FILE, ">${General::swroot}/samba/global") or die "Can't save the global settings: $!";
	flock (FILE, 2);
	
	print FILE <<END;
# global.settings by IPFire Project

[global]
server string = Samba on IPFire

workgroup = $sambasettings{'WORKGRP'}
realm = $mainsettings{'DOMAINNAME'}
passdb backend = smbpasswd

map to guest = $sambasettings{'MAPTOGUEST'}

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

# Enable support for Apple
vfs objects = catia fruit streams_xattr recycle

# Enable following symlinks
wide links = yes

END

# Server Role
if ($sambasettings{'ROLE'} eq "standalone") {
	print FILE "server role = standalone\n";
} elsif ($sambasettings{'ROLE'} eq "member") {
	print FILE "server role = member server\n";
}

if ($sambasettings{'ENCRYPTION'} =~ m/(desired|required)/) {
	print FILE "smb encrypt = $1\n";
}

# Include smb.conf.local
if (-e "${General::swroot}/samba/smb.conf.local") {
	open(LOCAL, "<${General::swroot}/samba/smb.conf.local");

	# Copy content line by line
	while (<LOCAL>) {
		print FILE $_;
	}

	close(LOCAL);
}

print FILE <<END;
# Export all printers
[printers]
path = /var/spool/samba/
printable = yes

END
close FILE;

	system("/usr/local/bin/sambactrl smbsafeconf");
}

sub joindomain {
	my $username = shift;
	my $password = shift;

	my @options = ("/usr/local/bin/sambactrl", "join", $username, $password);
	my $output = qx(@options);

	return $output;
}
