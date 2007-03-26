#!/usr/bin/perl
#
# IPFire CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The IPFire Team

use strict;
# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %sambasettings = ();
my %cgisettings = ();
my %checked = ();
my %netsettings = ();
my %ovpnsettings = ();
my $message = "";
my $errormessage = "";
my $defaultoption= "[Share]\npath = /var/samba/share1\ncomment = Share - Public Access\nbrowseable = yes\nwriteable = yes\ncreate mask = 0777\ndirectory mask = 0777\nguest ok = yes\npublic = yes\nforce user = samba";
my $userentry = "";
my @user = ();
my @userline = ();
my @proto = ();
my %selected= () ;
my $userfile = "/var/ipfire/samba/private/smbpasswd";
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
&General::readhash("${General::swroot}/ovpn/settings", \%ovpnsettings);

############################################################################################################################
############################################# Samba Dienste fr Statusberprfung ##########################################

my %servicenames = ('SMB Daemon' => 'smbd','NetBIOS Nameserver' => 'nmbd','Winbind Daemon' => 'winbindd');

&Header::showhttpheaders();

############################################################################################################################
#################################### Initialisierung von Samba Sharess fr die Verarbeitung ################################

my @Zeilen= ();
my @Shares= ();
my $shareentry = "";
my $shareconfigentry = "";
my @shareconfigline = ();
my $shareoption = '';
my @shares = ();
my @shareline = ();
my $sharefile = "/var/ipfire/samba/shares";
my $EOF = qx(cat $sharefile | wc -l);
my $Status = qx(/usr/local/bin/sambactrl smbstatus);

@shares = `grep -n '^\\[' $sharefile`;
foreach $shareentry (@shares)
 {
 @shareline = split( /\:/, $shareentry );
 push(@Zeilen,$shareline[0]);push(@Shares,$shareline[1]);
 }

############################################################################################################################
#################################### Initialisierung von Samba Variablen fr global Settings ###############################

$sambasettings{'WORKGRP'} = 'homeip.net';
$sambasettings{'NETBIOSNAME'} = 'IPFIRE';
$sambasettings{'SRVSTRING'} = 'Samba Server running on IPFire 2.0';
$sambasettings{'INTERFACES'} = '';
$sambasettings{'SECURITY'} = 'share';
$sambasettings{'OSLEVEL'} = '65';
$sambasettings{'GREEN'} = 'on';
$sambasettings{'BLUE'} = 'off';
$sambasettings{'ORANGE'} = 'off';
$sambasettings{'VPN'} = 'off';
$sambasettings{'WINSSRV'} = "$netsettings{'GREEN_NETADDRESS'}";
$sambasettings{'WINSSUPPORT'} = 'off';
$sambasettings{'PASSWORDSYNC'} = 'off';
$sambasettings{'OTHERINTERFACES'} = '';
$sambasettings{'GUESTACCOUNT'} = 'samba';
$sambasettings{'MAPTOGUEST'} = 'Never';
### Values that have to be initialized
$cgisettings{'ACTION'} = '';

################################################## Samba PDC Variablen #####################################################

$sambasettings{'LOCALMASTER'} = 'off';
$sambasettings{'DOMAINMASTER'} = 'off';
$sambasettings{'PREFERREDMASTER'} = 'off';
my $PDCOPTIONS = `cat ${General::swroot}/samba/pdc`;


############################################################################################################################

&General::readhash("${General::swroot}/samba/settings", \%sambasettings);
&Header::getcgihash(\%sambasettings);

&Header::openpage('Samba', 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
############################################# Samba Rootskript aufrufe fr SU-Actions ######################################

if ($sambasettings{'ACTION'} eq 'smbuserdisable'){system("/usr/local/bin/sambactrl smbuserdisable $sambasettings{'NAME'}");}
if ($sambasettings{'ACTION'} eq 'smbuserenable'){system("/usr/local/bin/sambactrl smbuserenable $sambasettings{'NAME'}");}
if ($sambasettings{'ACTION'} eq 'smbuseradd'){system("/usr/local/bin/sambactrl smbuseradd $sambasettings{'USERNAME'} $sambasettings{'PASSWORD'} $sambasettings{'GROUP'} $sambasettings{'SHELL'}");}
if ($sambasettings{'ACTION'} eq 'smbpcadd'){system("/usr/local/bin/sambactrl smbpcadd $sambasettings{'PCNAME'} $sambasettings{'GROUP'} $sambasettings{'SHELL'}");}
if ($sambasettings{'ACTION'} eq 'smbchangepw'){system("/usr/local/bin/sambactrl smbchangepw $sambasettings{'USERNAME'} $sambasettings{'PASSWORD'}");}
if ($sambasettings{'ACTION'} eq 'smbrestart'){system("/usr/local/bin/sambactrl smbrestart");}
if ($sambasettings{'ACTION'} eq 'smbstart'){system("/usr/local/bin/sambactrl smbstart");}
if ($sambasettings{'ACTION'} eq 'smbstop'){system("/usr/local/bin/sambactrl smbstop");}
if ($sambasettings{'ACTION'} eq 'smbstop'){system("/usr/local/bin/sambactrl smbstop");}
if ($sambasettings{'ACTION'} eq 'globalreset'){system("/usr/local/bin/sambactrl smbglobalreset");}

# smbsafeconf is directly called by the if clause

if ($sambasettings{'ACTION'} eq 'sharesreset')
{
system('/usr/local/bin/sambactrl smbsharesreset');
 @Zeilen = ();
 @Shares = ();
 $shareentry = "";
 @shares = ();
 @shareline = ();
 $EOF = qx(cat $sharefile | wc -l);
 
 @shares = `grep -n '^\\[' $sharefile`;
 foreach $shareentry (@shares)
 {
 @shareline = split( /\:/, $shareentry );
 push(@Zeilen,$shareline[0]);push(@Shares,$shareline[1]);
 }
}

############################################################################################################################
########################################### Samba Benutzer oder PC l�chen #################################################

if ($sambasettings{'ACTION'} eq 'userdelete' && $sambasettings{'NAME'} =~ /\$/)
{
system("/usr/local/bin/sambactrl smbpcdelete $sambasettings{'NAME'}");
}
elsif ($sambasettings{'ACTION'} eq 'userdelete')
{
system("/usr/local/bin/sambactrl smbuserdelete $sambasettings{'NAME'}");
}

############################################################################################################################
############################################## Samba Share neu anlegen #####################################################

if ($sambasettings{'ACTION'} eq 'smbshareadd')
{
  my $emptyline= ""; 
	open (FILE, ">>${General::swroot}/samba/shares") or die "Can't save the shares settings: $!";
	flock (FILE, 2);
	
print FILE <<END
$sambasettings{'SHAREOPTION'}
$emptyline
END
;
close FILE;
system("/usr/local/bin/sambactrl smbsafeconf");

 @Zeilen = ();
 @Shares = ();
 $shareentry = "";
 @shares = ();
 @shareline = ();
 $EOF = qx(cat $sharefile | wc -l);
 
 @shares = `grep -n '^\\[' $sharefile`;
 foreach $shareentry (@shares)
 {
 @shareline = split( /\:/, $shareentry );
 push(@Zeilen,$shareline[0]);push(@Shares,$shareline[1]);
 }
}

############################################################################################################################
################################################## Samba Share l�chen #####################################################

if ($sambasettings{'ACTION'} eq 'smbsharedel')
{
my $sharebody = '';
my $sharehead = '';
my $sharetext = '';
my $sharename = "$sambasettings{'NAME'}";
chomp $sharename;
$sharename=~s/\s//g;

for(my $i = 0; $i <= $#Shares; $i++)
 {
 chomp $Shares[$i];
 $Shares[$i]=~s/\s//g;
 if ( "$Shares[$i]" eq "$sharename" )
  {
  my $Zeilenbegin = $Zeilen[$i]-2;
  my $Zeilenende =  $EOF-$Zeilen[$i+1]+1;
  my $Zeilenende2 =  $Zeilenende-1;

  if ( $Zeilen[$i] eq $Zeilen[$#Shares] )
   {
   $sharehead = qx(head -$Zeilenbegin $sharefile);
   $sharetext = $sharehead;
   }
  elsif ($Zeilen[$i] eq 1 )
   {
   $sharehead = qx(tail -$Zeilenende $sharefile | head -$Zeilenende2);
   $sharetext = $sharehead;
   }
  else
   {
   $sharehead = qx(head -$Zeilenbegin $sharefile);$sharebody = qx(tail -$Zeilenende $sharefile | head -$Zeilenende2);
   $sharetext = "$sharehead\n$sharebody";
   }
  }
 }
 
open (FILE, ">${General::swroot}/samba/shares") or die "Can't delete the share settings: $!";
flock (FILE, 2);
print FILE <<END
$sharetext
END
;
close FILE;
system("/usr/local/bin/sambactrl smbsafeconf");

 @Zeilen = ();
 @Shares = ();
 $shareentry = "";
 @shares = ();
 @shareline = ();
 $EOF = qx(cat $sharefile | wc -l);
 
 @shares = `grep -n '^\\[' $sharefile`;
 foreach $shareentry (@shares)
 {
 @shareline = split( /\:/, $shareentry );
 push(@Zeilen,$shareline[0]);push(@Shares,$shareline[1]);
 }
}
############################################################################################################################
################################################## Sambashare �dern #######################################################

if ($sambasettings{'ACTION'} eq 'smbsharechange')
{
my $sharebody = '';
my $sharehead = '';
my $sharename = "$sambasettings{'NAME'}";
my $sharetext = '';
$sharename=~s/\s//g;

for(my $i = 0; $i <= $#Shares; $i++)
 {
 chomp $Shares[$i];
 $Shares[$i]=~s/\s//g;
 if ( "$Shares[$i]" eq "$sharename" )
  {
  my $Zeilenbegin = $Zeilen[$i]-2;
  my $Zeilenende =  $EOF-$Zeilen[$i+1]+1;
  my $Zeilenende2 =  $Zeilenende-1;

  if ( $Zeilen[$i] eq $Zeilen[$#Shares] )
   {
   $sharehead = qx(head -$Zeilenbegin $sharefile);
   $sharetext = $sharehead;
   }
  elsif ($Zeilen[$i] eq 1 )
   {
   $sharehead = qx(tail -$Zeilenende $sharefile | head -$Zeilenende2);
   $sharetext = $sharehead;
   }
  else
   {
   $sharehead = qx(head -$Zeilenbegin $sharefile);$sharebody = qx(tail -$Zeilenende $sharefile | head -$Zeilenende2);
   $sharetext = "$sharehead\n$sharebody";
   }
  }
 }
 
open (FILE, ">${General::swroot}/samba/shares") or die "Can't delete the share settings: $!";
flock (FILE, 2);
print FILE <<END
$sharetext
$sambasettings{'SHAREOPTION'}
END
;
close FILE;
system("/usr/local/bin/sambactrl smbsafeconf");

 @Zeilen = ();
 @Shares = ();
 @shares = `grep -n '^\\[' $sharefile`;
 foreach $shareentry (@shares)
 {
 @shareline = split( /\:/, $shareentry );
 push(@Zeilen,$shareline[0]);push(@Shares,$shareline[1]);
 }
}

############################################################################################################################
##################################### Umsetzen der Werte von Checkboxen und Dropdowns ######################################

if ($sambasettings{'ACTION'} eq $Lang::tr{'save'})
{
$sambasettings{'INTERFACES'} = '';
if ($sambasettings{'GREEN'} eq 'on'){ $sambasettings{'INTERFACES'} .= " $netsettings{'GREEN_DEV'}";}
if ($sambasettings{'BLUE'} eq 'on'){ $sambasettings{'INTERFACES'} .= " $netsettings{'BLUE_DEV'}";}
if ($sambasettings{'ORANGE'} eq 'on'){ $sambasettings{'INTERFACES'} .= " $netsettings{'ORANGE_DEV'}";}
if ($sambasettings{'VPN'} eq 'on'){ $sambasettings{'INTERFACES'} .= " $ovpnsettings{'DDEVICE'}";}
if ($sambasettings{'OTHERINTERFACES'} ne ''){ $sambasettings{'INTERFACES'} .= " $sambasettings{'OTHERINTERFACES'}";}

############################################################################################################################
##################################### Schreiben settings und bersetzen fr smb.conf #######################################

  &General::writehash("${General::swroot}/samba/settings", \%sambasettings);
  
if ($sambasettings{'PASSWORDSYNC'} eq 'on'){ $sambasettings{'PASSWORDSYNC'} = "true";} else { $sambasettings{'PASSWORDSYNC'} = "false";}
if ($sambasettings{'WINSSUPPORT'} eq 'on'){ $sambasettings{'WINSSUPPORT'} = "true";} else { $sambasettings{'WINSSUPPORT'} = "false";}
if ($sambasettings{'LOCALMASTER'} eq 'on'){ $sambasettings{'LOCALMASTER'} = "true";} else { $sambasettings{'LOCALMASTER'} = "false";}
if ($sambasettings{'DOMAINMASTER'} eq 'on'){ $sambasettings{'DOMAINMASTER'} = "true";} else { $sambasettings{'DOMAINMASTER'} = "false";}
if ($sambasettings{'PREFERREDMASTER'} eq 'on'){ $sambasettings{'PREFERREDMASTER'} = "true";} else { $sambasettings{'PREFERREDMASTER'} = "false";}
if ($sambasettings{'MAPTOGUEST'} eq 'on'){ $sambasettings{'MAPTOGUEST'} = "true";} else { $sambasettings{'MAPTOGUEST'} = "false";}

############################################################################################################################
############################################# Schreiben der Samba globals ##################################################

	open (FILE, ">${General::swroot}/samba/global") or die "Can't save the global settings: $!";
	flock (FILE, 2);
	
print FILE <<END
# global.settings by IPFire Project

[global]
netbios name = $sambasettings{'NETBIOSNAME'}
server string = $sambasettings{'SRVSTRING'}
workgroup = $sambasettings{'WORKGRP'}

keep alive = 30
os level = $sambasettings{'OSLEVEL'}
fstype = NTFS

kernel oplocks = false
map to guest = $sambasettings{'MAPTOGUEST'}
smb ports = 445 139
unix charset = CP850

security = $sambasettings{'SECURITY'}
encrypt passwords = yes
guest account = $sambasettings{'GUESTACCOUNT'}
unix password sync = $sambasettings{'PASSWORDSYNC'}
null passwords = yes

bind interfaces only = true
interfaces = $sambasettings{'INTERFACES'}
socket options = TCP_NODELAY SO_RCVBUF=8192 SO_SNDBUF=8192 SO_KEEPALIVE

username level = 1
wins support = $sambasettings{'WINSSUPPORT'}

log file       = /var/log/samba/samba-log.%m
lock directory = /var/lock/samba
pid directory = /var/run/
	
preferred master = $sambasettings{'PREFERREDMASTER'}
domain master = $sambasettings{'DOMAINMASTER'}
local master = $sambasettings{'LOCALMASTER'}

END
;
close FILE;

 if ($sambasettings{'SECURITY'} eq 'User' && $sambasettings{'DOMAINMASTER'} eq 'true' )
 {	
 open (FILE, ">${General::swroot}/samba/pdc") or die "Can't save the pdc settings: $!";
 flock (FILE, 2);
 print FILE <<END
$sambasettings{'PDCOPTIONS'}
END
;
 close FILE;
 system('/usr/local/bin/sambactrl smbsafeconfpdc');
 }
 else
 {
 system('/usr/local/bin/sambactrl smbsafeconf');
 }
}
  &General::readhash("${General::swroot}/samba/settings", \%sambasettings);

if ($errormessage) {
        &Header::openbox('100%', 'left', $Lang::tr{'error messages'});
        print "<class name='base'>$errormessage\n";
        print "&nbsp;</class>\n";
        &Header::closebox();
                  }

############################################################################################################################
########################################## Aktivieren von Checkboxen und Dropdowns #########################################

$checked{'WINSSUPPORT'}{'off'} = '';
$checked{'WINSSUPPORT'}{'on'} = '';
$checked{'WINSSUPPORT'}{$sambasettings{'WINSSUPPORT'}} = "checked='checked'";
$checked{'PASSWORDSYNC'}{'off'} = '';
$checked{'PASSWORDSYNC'}{'on'} = '';
$checked{'PASSWORDSYNC'}{$sambasettings{'PASSWORDSYNC'}} = "checked='checked'";
$checked{'LOCALMASTER'}{'off'} = '';
$checked{'LOCALMASTER'}{'on'} = '';
$checked{'LOCALMASTER'}{$sambasettings{'LOCALMASTER'}} = "checked='checked'";
$checked{'DOMAINMASTER'}{'off'} = '';
$checked{'DOMAINMASTER'}{'on'} = '';
$checked{'DOMAINMASTER'}{$sambasettings{'DOMAINMASTER'}} = "checked='checked'";
$checked{'PREFERREDMASTER'}{'off'} = '';
$checked{'PREFERREDMASTER'}{'on'} = '';
$checked{'PREFERREDMASTER'}{$sambasettings{'PREFERREDMASTER'}} = "checked='checked'";
$checked{'GREEN'}{'off'} = '';
$checked{'GREEN'}{'on'} = '';
$checked{'GREEN'}{$sambasettings{'GREEN'}} = "checked='checked'";
$checked{'BLUE'}{'off'} = '';
$checked{'BLUE'}{'on'} = '';
$checked{'BLUE'}{$sambasettings{'BLUE'}} = "checked='checked'";
$checked{'ORANGE'}{'off'} = '';
$checked{'ORANGE'}{'on'} = '';
$checked{'ORANGE'}{$sambasettings{'ORANGE'}} = "checked='checked'";
$checked{'VPN'}{'off'} = '';
$checked{'VPN'}{'on'} = '';
$checked{'VPN'}{$sambasettings{'VPN'}} = "checked='checked'";

$selected{'MAPTOGUEST'}{$sambasettings{'MAPTOGUEST'}} = "selected='selected'";
$selected{'SECURITY'}{$sambasettings{'SECURITY'}} = "selected='selected'";

############################################################################################################################
################################### Aufbau der HTML Seite fr globale Sambaeinstellungen ###################################

&Header::openbox('100%', 'center', 'Samba');
print <<END
        <hr />
        <table width='95%' cellspacing='0'>
END
;
if ( $message ne "" )
	{
	print "<tr><td colspan='2' align='left'><font color='red'>$message</font>";
	}

print <<END
<tr><td colspan='2'><br /></td></tr>
<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>Alle Dienste</b></td></tr>
</table><table width='95%' cellspacing='0'>
END
;

my $key = '';
foreach $key (sort keys %servicenames)
	{
	print "<tr><td align='left'>$key";
	my $shortname = $servicenames{$key};
	my $status = &isrunning($shortname);
	print "$status";
	print <<END
	<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
				<input type='hidden' name='ACTION' value='restart $shortname' />
				<input type='image' src='/images/reload.gif' />
	</form></td>
END
;
	}

print <<END
<tr><td colspan='2'><br /></td></tr>
<tr><td colspan='2' align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
																		<input type='submit' name='ACTION' value='Start' />
																		<input type='submit' name='ACTION' value='Stop' />
																		<input type='submit' name='ACTION' value='$Lang::tr{'restart'}' />
</form></td></tr>
</table>


<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='95%' cellspacing='0'>
<tr><td colspan='2'><br /></td></tr>
<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>Basisoptionen</b></td></tr>
<tr><td align='left'>Workgroup:</td><td><input type='text' name='WORKGRP' value='$sambasettings{'WORKGRP'}' size="30" /></td></tr>
<tr><td align='left'>NetBIOS-Name:</td><td><input type='text' name='NETBIOSNAME' value='$sambasettings{'NETBIOSNAME'}' size="30" /></td></tr>
<tr><td align='left'>Server-String:</td><td><input type='text' name='SRVSTRING' value='$sambasettings{'SRVSTRING'}' size="30" /></td></tr>
<tr><td align='left'>Interfaces:</td><td>on <input type='radio' name='VPN' value='on' $checked{'VPN'}{'on'} />/
																						<input type='radio' name='VPN' value='off' $checked{'VPN'}{'off'} /> off |
																						<font size='2' color='$Header::colourovpn'><b>   OpenVpn  -  $ovpnsettings{'DDEVICE'}</b></font></td></tr>
<tr><td align='left'></td><td>on <input type='radio' name='GREEN' value='on' $checked{'GREEN'}{'on'} />/
																	<input type='radio' name='GREEN' value='off' $checked{'GREEN'}{'off'} /> off |
																	<font size='2' color='$Header::colourgreen'><b>   $Lang::tr{'green'}  -  $netsettings{'GREEN_DEV'}</b></font></td></tr>
END
;

if (&Header::blue_used())
	{
	print <<END
	<tr><td align='left'></td><td>on <input type='radio' name='BLUE' value='on' $checked{'BLUE'}{'on'} />/
																		<input type='radio' name='BLUE' value='off' $checked{'BLUE'}{'off'} /> off |
																		<font size='2' color='$Header::colourblue'><b>   $Lang::tr{'wireless'}  -  $netsettings{'BLUE_DEV'}</b></font></td></tr>
END
;
	}

if (&Header::orange_used())
	{
	print <<END
	<tr><td align='left'></td><td>on <input type='radio' name='ORANGE' value='on' $checked{'ORANGE'}{'on'} />/
																		<input type='radio' name='ORANGE' value='off' $checked{'ORANGE'}{'off'} /> off |
																		<font size='2' color='$Header::colourorange'><b>   $Lang::tr{'dmz'}  -  $netsettings{'ORANGE_DEV'}</b></font></td></tr>
END
;
	}

print <<END
<tr><td align='center'>weitere</td><td><input type='text' name='OTHERINTERFACES' value='$sambasettings{'OTHERINTERFACES'}' size="30" /></td></tr>
<tr><td align='left'><br /></td><td></td></tr>
<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>Sicherheitsoptionen</b></td></tr>
<tr><td align='left'>Security:</td><td><select name='SECURITY'>
																				<option value='share' $selected{'SECURITY'}{'share'}>Share</option>
																				<option value='user' $selected{'SECURITY'}{'user'}>User</option>
																				<option value='domain' $selected{'SECURITY'}{'domain'}>Domain</option>
																				<option value='ADS' $selected{'SECURITY'}{'ADS'}>ADS</option>
																				<option value='server' $selected{'SECURITY'}{'server'}>Server</option>
																				</select></td></tr>
<tr><td align='left'>Map to guest:</td><td><select name='MAPTOGUEST'>
																						<option value='Never' $selected{'MAPTOGUEST'}{'Never'}>Never</option>
																						<option value='Bad User' $selected{'MAPTOGUEST'}{'Bad User'}>Bad User</option>
																						<option value='Bad Password' $selected{'MAPTOGUEST'}{'Bad Password'}>Bad Password</option>
																						</select></td></tr>
<tr><td align='left'>Unix Passwort Sync:</td><td>on <input type='radio' name='PASSWORDSYNC' value='on' $checked{'PASSWORDSYNC'}{'on'} />/
																										<input type='radio' name='PASSWORDSYNC' value='off' $checked{'PASSWORDSYNC'}{'off'} /> off</td></tr>
<tr><td align='left'><br /></td><td></td></tr>
<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>Netzwerkoptionen</b></td></tr>
<tr><td align='left'>OS Level:</td><td><input type='text' name='OSLEVEL' value='$sambasettings{'OSLEVEL'}' size="30" /></td></tr>
<tr><td align='left'>WINS-Server:</td><td><input type='text' name='WINSSRV' value='$sambasettings{'WINSSRV'}' size="30" /></td></tr>
END
;

if ($sambasettings{'SECURITY'} eq 'user')
	{
	print <<END
	<tr><td align='left'>WINS-Support:</td><td>on <input type='radio' name='WINSSUPPORT' value='on' $checked{'WINSSUPPORT'}{'on'} />/
																								<input type='radio' name='WINSSUPPORT' value='off' $checked{'WINSSUPPORT'}{'off'} /> off</td></tr>
<tr><td align='left'>Local Master:</td><td>on <input type='radio' name='LOCALMASTER' value='on' $checked{'LOCALMASTER'}{'on'} />/
																							<input type='radio' name='LOCALMASTER' value='off' $checked{'LOCALMASTER'}{'off'} /> off</td></tr>
<tr><td align='left'>Domain Master:</td><td>on <input type='radio' name='DOMAINMASTER' value='on' $checked{'DOMAINMASTER'}{'on'} />/
																								<input type='radio' name='DOMAINMASTER' value='off' $checked{'DOMAINMASTER'}{'off'} /> off</td></tr>
<tr><td align='left'>Preferred Master:</td><td>on <input type='radio' name='PREFERREDMASTER' value='on' $checked{'PREFERREDMASTER'}{'on'} />/
																									<input type='radio' name='PREFERREDMASTER' value='off' $checked{'PREFERREDMASTER'}{'off'} /> off</td></tr>
END
;
	}

if ($sambasettings{'SECURITY'} eq 'user' && $sambasettings{'DOMAINMASTER'} eq 'on')
	{
	print <<END
	<tr><td align='left'><br /></td><td></td></tr>
	<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>PDC Optionen</b></td></tr>
	<tr><td align='left'><br /></td><td></td></tr>
	<tr><td colspan='2' align='center'><textarea name="PDCOPTIONS" cols="50" rows="15" Wrap="off">$PDCOPTIONS</textarea></td></tr>
END
;
	}

print <<END
</table>
<table width='10%' cellspacing='0'>
<tr><td colspan='2'><br /></td></tr>
<tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value=$Lang::tr{'save'} />
												<input type='image' alt=$Lang::tr{'save'} src='/images/floppy.gif' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
										<input type='hidden' name='ACTION' value='globalreset' />
										<input type='image' alt='Reset' src='/images/reload.gif' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
										<input type='hidden' name='ACTION' value='globalcaption' />
										<input type='image' alt='Legende' src='/images/info.gif'></form></td></tr>
</table>
END
;

if ($sambasettings{'ACTION'} eq 'globalcaption')
	{
	print <<END
	<table width='95%' cellspacing='0'>
	<tr><td colspan='2'><br /></td></tr>
	<tr><td><b>Legende:</b></td></tr>
	<tr><td><img src='/images/floppy.gif'>Einstellungen speichern</td></tr>
	<tr><td><img src='/images/reload.gif'>Auf default zurueck setzen</td></tr>
	</table>
END
;
	}

&Header::closebox();

############################################################################################################################
########################################## Benutzerverwaltung fr Usersecurity #############################################

if ($sambasettings{'SECURITY'} eq 'user')
	{
	if ($sambasettings{'DOMAINMASTER'} eq 'off')
		{
		&Header::openbox('100%', 'center', 'accounting - user Security none PDC mode');
		}
	else
		{
		&Header::openbox('100%', 'center', 'accounting - user Security PDC mode');
		}
	print <<END
	<hr />
	<table width='95%' cellspacing='0'>
	<tr><td colspan='6'><br /></td></tr>
	<tr><td colspan='6' align='left'></td></tr>
	<tr><td bgcolor='${Header::table1colour}' colspan='7' align='left'><b>Benutzerverwaltung</b></td></tr>
	<tr><td><u>Name</u></td><td><u>Passwort</u></td>
END
;

	if ($sambasettings{'DOMAINMASTER'} eq 'off')
		{
		print "<td></td>";
		}
	else
		{
		print "<td><u>Typ</u></td>";
		}

	print "<td><u>Status</u></td><td colspan='3' width="5"><u>Optionen</u></td></tr>";
	system('/usr/local/bin/sambactrl readsmbpasswd');
	open(FILE, "</var/ipfire/samba/private/smbpasswd") or die "Can't read user file: $!";
	@user = <FILE>;
	close(FILE);
	system('/usr/local/bin/sambactrl locksmbpasswd');
	foreach $userentry (sort @user)
		{
		@userline = split( /\:/, $userentry );
		print "<tr><td align='left'>$userline[0]</td><td>";
		if ($userline[4] =~ /N/)
			{
			print "nicht gesetzt</td><td>";
			}
		else
			{
			print "gesetzt</td><td>";
			}

		if ($sambasettings{'DOMAINMASTER'} eq 'off')
			{
			print "</td><td>";
			}
		else
			{
			if ($userline[0] =~ /\$/)
				{
				print "PC</td><td>";
				}
			else
				{
				print "User</td><td>";
				}
			}

		if ($userline[4] =~ /D/)
			{
			print <<END
			inaktiv</td>
			<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='hidden' name='NAME' value='$userline[0]' />
					<input type='hidden' name='ACTION' value='smbuserenable' />
					<input type='image' alt='Aktivieren' src='/images/on.gif' />
			</form></td>
END
;
			}
		else
			{
			print <<END
			aktiv</td>
			<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='hidden' name='NAME' value='$userline[0]' />
					<input type='hidden' name='ACTION' value='smbuserdisable' />
					<input type='image' alt='Deaktivieren' src='/images/off.gif' />
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
			<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='hidden' name='NAME' value='$userline[0]' />
					<input type='hidden' name='ACTION' value='userchangepw' />
					<input type='image' alt='Bearbeiten' src='/images/edit.gif' />
			</form></td>
END
;
			}

		print <<END
		<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
				<input type='hidden' name='NAME' value='$userline[0]' />
				<input type='hidden' name='ACTION' value='userdelete' />
				<input type='image' alt='Loeschen' src='/images/delete.gif' />
		</form></td></tr>
END
;
		}
	print <<END
	</table>
	<table width='10%' cellspacing='0'>
	<tr><td colspan='3'><br /></td></tr>
	<tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
													<input type='hidden' name='ACTION' value='useradd' />
													<input type='image' alt='Benutzer anlegen' src='/images/add.gif' /></form></td>
END
;

	if ($sambasettings{'DOMAINMASTER'} eq 'on')
		{
		print <<END
		<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value='pcadd' />
												<input type='image' alt='Legende' src='/images/comp.blue.gif' /></form>
END
;
		}
	print <<END
	<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
											<input type='hidden' name='ACTION' value='usercaption' />
											<input type='image' alt='Legende' src='/images/info.gif' /></form>
	</td><tr>
	</table>
END
;

	if ($sambasettings{'ACTION'} eq 'usercaption')
		{
		print <<END
		<table width='95%' cellspacing='0'>
		<tr><td><br /></td></tr>
		<tr><td><b>Legende:</b></td></tr>
		<tr><td><img src='/images/add.gif'>Benutzer neu anlegen</td></tr>
		<tr><td><img src='/images/comp.blue.gif'>Client Account neu anlegen</td></tr>
		<tr><td><img src='/images/on.gif'>Benutzer aktivieren</td></tr>
		<tr><td><img src='/images/off.gif'>Benutzer deaktivieren</td></tr>
		<tr><td><img src='/images/floppy.gif'>Einstellungen speichern</td></tr>
		<tr><td><img src='/images/edit.gif'>Passwort wechseln</td></tr>
		<tr><td><img src='/images/delete.gif'>Benutzer loeschen</td></tr>
		</table>
END
;
		}

	if ($sambasettings{'ACTION'} eq 'userchangepw')
		{
		my $username = "$sambasettings{'NAME'}";
		my $password = 'samba';
		print <<END
		<hr />
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='95%' cellspacing='0'>
		<tr><td colspan='2'><br /></td></tr>
		<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>Passwort wechseln</b></td></tr>
		<tr><td align='left'>Benutzername</td><td><input type='text' name='USERNAME' value='$username' size="30" /></td></tr>
		<tr><td align='left'>Passwort</td><td><input type='password' name='PASSWORD' value='$password' size="30" /></td></tr>
		<tr><td colspan='2' align='center'><input type='hidden' name='ACTION' value='smbchangepw' />
																				<input type='image' alt=$Lang::tr{'save'} src='/images/floppy.gif' /></form></td></tr>
		</table>
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
		<hr />
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='95%' cellspacing='0'>
		<tr><td colspan='2'><br /></td></tr>
		<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>Benutzer neu anlegen</b></td></tr>
		<tr><td align='left'>Benutzername</td><td><input type='text' name='USERNAME' value='$username' size="30" /></td></tr>
		<tr><td align='left'>Passwort</td><td><input type='password' name='PASSWORD' value='$password' size="30" /></td></tr>
		<tr><td align='left'>Unix Gruppe</td><td><input type='text' name='GROUP' value='sambauser' size="30" /></td></tr>
		<tr><td align='left'>Unix Shell</td><td><input type='text' name='SHELL' value='/bin/false' size="30" /></td></tr>
		<tr><td colspan='2' align='center'><input type='hidden' name='ACTION' value='smbuseradd' />
																				<input type='image' alt=$Lang::tr{'save'} src='/images/floppy.gif' /></form></td></tr>
		</table>
END
;
		}

	if ($sambasettings{'ACTION'} eq 'pcadd')
		{
		my $pcname = "client\$";
		chomp $pcname;
		$pcname=~s/\s//g;
		print <<END
		<hr />
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='95%' cellspacing='0'>
		<tr><td colspan='2'><br /></td></tr>
		<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>Client Account neu anlegen</b></td></tr>
		<tr><td align='left'>Clientname</td><td><input type='text' name='PCNAME' value='$pcname' size="30" /></td></tr>
		<tr><td align='left'>Unix Gruppe</td><td><input type='text' name='GROUP' value='sambawks' size="30" /></td></tr>
		<tr><td align='left'>Unix Shell</td><td><input type='text' name='SHELL' value='/bin/false' size="30" /></td></tr>
		<tr><td colspan='2' align='center'><input type='hidden' name='ACTION' value='smbpcadd' />
																				<input type='image' alt=$Lang::tr{'save'} src='/images/floppy.gif' /></form></td></tr>
		</table>
END
;
		}

&Header::closebox();
}

############################################################################################################################
############################################### Verwalten von Freigaben ####################################################
        
&Header::openbox('100%', 'center', 'Shares');

print <<END
<hr />
<table width='95%' cellspacing='0'>
<tr><td colspan='3'><br /></td></tr>
<tr><td bgcolor='${Header::table1colour}' colspan='3' align='left'><b>Shareverwaltung</b>
<tr><td><u>Names des Shares</u></td><td colspan='2' width="5"><u>Optionen</u></td></tr>
END
;

foreach $shareentry (sort @Shares)
	{
	print <<END
	<tr><td align='left'>$shareentry</td>
	<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='hidden' name='NAME' value='$shareentry' />
			<input type='hidden' name='ACTION' value='sharechange' />
			<input type='image' alt='Bearbeiten' src='/images/edit.gif' />
	</form></td>
	<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='hidden' name='NAME' value='$shareentry' />
			<input type='hidden' name='ACTION' value='smbsharedel' />
			<input type='image' alt='Loeschen' src='/images/delete.gif' />
	</form></td><tr>
END
;
	}

print <<END
</table>
<table width='10%' cellspacing='0'>
<tr><td colspan='3'><br /></td></tr>
<tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value='shareadd'>
												<input type='image' alt='neuen Share anlegen' src='/images/add.gif'>
												</form></td>
		<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value='sharesreset'>
												<input type='image' alt='Reset' src='/images/reload.gif'>
												</form></td>
		<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value='sharecaption'>
												<input type='image' alt='Legende' src='/images/info.gif'>
												</form></td><tr>
</table>
END
;

if ($sambasettings{'ACTION'} eq 'sharecaption')
	{
	print <<END
	<table width='95%' cellspacing='0'>
	<tr><td><br /></td></tr>
	<tr><td><b>Legende:</b></td></tr>
	<tr><td><img src='/images/add.gif'>Share neu anlegen</td></tr>
	<tr><td><img src='/images/edit.gif'>Share bearbeiten</td></tr>
	<tr><td><img src='/images/floppy.gif'>Einstellungen speichern</td></tr>
	<tr><td><img src='/images/reload.gif'>Shares zurueck setzen</td></tr>
	<tr><td><img src='/images/delete.gif'>Share loeschen</td></tr>
	</table>
END
;
	}

if ($sambasettings{'ACTION'} eq 'shareadd' || $sambasettings{'ACTION'} eq 'optioncaption' )
	{
	print <<END
	<hr />
	<table width='95%' cellspacing='0'>
	<tr><td colspan='2'><br /></td></tr>
	<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>neuen Share anlegen</b></td></tr>
	<tr><td colspan='2' align='center'></td></tr>
	<tr><td colspan='2' align='center'>Anzeige der Optionen fuer Shares<form method='post' action='$ENV{'SCRIPT_NAME'}'>
																																			<input type='hidden' name='ACTION' value='optioncaption'>
																																			<input type='image' alt='Legende' src='/images/info.gif'>
																																			</form></td></tr>
	<tr><td colspan='2' align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'><textarea name="SHAREOPTION" cols="50" rows="15" Wrap="off">$defaultoption</textarea></td></tr>
	</table>
	<table width='10%' cellspacing='0'>
	<tr><td><br /></td></tr>
	<tr><td align='center'><input type='hidden' name='ACTION' value='smbshareadd'>
													<input type='image' alt='Share hinzufuegen' src='/images/floppy.gif'>
													</form></td></tr>
	</table>
END
;
	}

if ($sambasettings{'ACTION'} eq 'sharechange' || $sambasettings{'ACTION'} eq 'optioncaption2' )
	{
	my $sharename = "$sambasettings{'NAME'}";
	chomp $sharename;
	$sharename=~s/\s//g;
	
	for(my $i = 0; $i <= $#Shares; $i++)
		{
		chomp $Shares[$i];
		$Shares[$i]=~s/\s//g;
		if ( "$Shares[$i]" eq "$sharename" )
			{
			my $Zeilenbegin = $Zeilen[$i+1]-2;
			my $Zeilenende =  $Zeilen[$i+1]-$Zeilen[$i];
			if ( $Zeilen[$i] eq $Zeilen[$#Shares] )
				{$Zeilenende =  $EOF-$Zeilen[$#Shares]+1;$Zeilenbegin = $EOF-$Zeilen[$#Shares]; $shareoption = qx(tail -$Zeilenende $sharefile | head -$Zeilenbegin);}
			else
				{$shareoption = qx(head -$Zeilenbegin $sharefile | tail -$Zeilenende);}
			}
		}
	print <<END
	<hr />
	<table width='95%' cellspacing='0'>
	<tr><td colspan='2'><br /></td></tr>
	<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>Share bearbeiten</b></td></tr>
	<tr><td colspan='2' align='center'></td></tr>
	<tr><td colspan='2' align='center'>Anzeige der Optionen fuer Shares<form method='post' action='$ENV{'SCRIPT_NAME'}'>
																																			<input type='hidden' name='ACTION' value='optioncaption2'>
																																			<input type='image' alt='Legende' src='/images/info.gif'>
																																			</form></td></tr>
	<tr><td colspan='2' align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'><textarea name="SHAREOPTION" cols="50" rows="15" Wrap="off">$shareoption</textarea></td></tr>
	</table>
	<table width='10%' cellspacing='0'>
	<tr><td><br /></td></tr>
	<tr><td align='center'><input type='hidden' name='NAME' value='$sambasettings{'NAME'}'>
													<input type='submit' name='ACTION' value='smbsharechange'></td></tr></form>
	</table>
END
;
	}

if ($sambasettings{'ACTION'} eq 'optioncaption' || $sambasettings{'ACTION'} eq 'optioncaption2')
	{
	print <<END
	<table width='95%' cellspacing='0'>
	<tr><td><br /></td></tr>
	<tr><td><b>Legende:</b></td></tr>
	<tr><td><u>Option</u></td><td><u>Bedeutung</u> / <u>Beispiel</u></td></tr>
	<tr><td>comment</td><td>Kommentar</td></tr>
	<tr><td></td><td>comment = Mein neues Share</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>path</td><td>Pfad zum Verzeichnis</td></tr>
	<tr><td></td><td>path = /share/neu</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>writeable</td><td>Verzeichnis schreibbar</td></tr>
	<tr><td></td><td>writeable = yes</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>browseable</td><td>sichtbar in Verzeichnisliste</td></tr>
	<tr><td></td><td>browsable = yes</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>user</td><td>Besitzer der Freigabe</td></tr>
	<tr><td></td><td>user = samba</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>valid users</td><td>Liste der Zugriffsberechtigten</td></tr>
	<tr><td></td><td>valid users = samba, user1</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>write list</td><td>Liste der Schreibberechtigten</td></tr>
	<tr><td></td><td>write list = samba</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>hosts allow</td><td>nur die angegebenen Hosts drfen das Share benutzen</td></tr>
	<tr><td></td><td>hosts allow = localhost 192.168.1.1 192.168.2.0/24</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>hosts deny</td><td>jede Maschine ausser diesen darf das Share benutzen</td></tr>
	<tr><td></td><td>hosts deny = 192.168.1.2 192.168.3.0/24</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>read list</td><td>Liste der nur Leseberechtigten</td></tr>
	<tr><td></td><td>read list = user1</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>admin users</td><td>Liste der Benutzer mit SuperUser Rechten</td></tr>
	<tr><td></td><td>admin users = user1</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>invalid users</td><td>Liste der Benutzer denen der Zugriff verweigert wird</td></tr>
	<tr><td></td><td>invalid users = user2</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>force user</td><td>Standartbenutzer fuer alle Dateien</td></tr>
	<tr><td></td><td>force user = samba</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>directory mask</td><td>UNIX Verzeichnisberchtigung beim Erzeugen</td></tr>
	<tr><td></td><td>directory mask = 0777</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>create mask</td><td>UNIX Dateiberchtigung beim Erzeugen</td></tr>
	<tr><td></td><td>create mask = 0777</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>guest ok</td><td>Annonymer Zugriff</td></tr>
	<tr><td></td><td>guest ok = yes</td></tr>
	</table>
END
;
}

&Header::closebox();

############################################################################################################################
############################################### Anzeige des Sambastatus ####################################################

&Header::openbox('100%', 'center', 'Status');

print <<END
<hr />
<table width='95%' cellspacing='0'>
<tr><td colspan='4'><br /></td></tr>
<tr><td bgcolor='${Header::table1colour}' colspan='3' align='left'><b>Samba Status</b></td></tr>
<tr><td>$Status</td></tr>
</table>
END
;

&Header::closebox();
&Header::closebigbox();
&Header::closepage();

############################################################################################################################
############################################ Subfunktion fr Sambadienste ##################################################

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