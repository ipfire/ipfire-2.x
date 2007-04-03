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
my @Logs = qx(ls /var/log/samba/);
my $Log =$Lang::tr{'no log selected'};
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
$Status=~s/\n/<br \/>/g;

@shares = `grep -n '^\\[' $sharefile`;
foreach $shareentry (@shares)
 {
 @shareline = split( /\:/, $shareentry );
 push(@Zeilen,$shareline[0]);push(@Shares,$shareline[1]);
 }

############################################################################################################################
#################################### Initialisierung von Samba Variablen fr global Settings ###############################

$sambasettings{'WORKGRP'} = 'homeip.net';
$sambasettings{'NETBIOSNAME'} = 'IPFire';
$sambasettings{'SRVSTRING'} = 'Samba running on IPFire 2.0';
$sambasettings{'INTERFACES'} = '';
$sambasettings{'SECURITY'} = 'share';
$sambasettings{'OSLEVEL'} = '65';
$sambasettings{'GREEN'} = 'on';
$sambasettings{'BLUE'} = 'off';
$sambasettings{'ORANGE'} = 'off';
$sambasettings{'VPN'} = 'off';
$sambasettings{'WINSSRV'} = '';
$sambasettings{'WINSSUPPORT'} = 'on';
$sambasettings{'REMOTEANNOUNCE'} = '';
$sambasettings{'PASSWORDSYNC'} = 'off';
$sambasettings{'OTHERINTERFACES'} = '127.0.0.1';
$sambasettings{'GUESTACCOUNT'} = 'samba';
$sambasettings{'MAPTOGUEST'} = 'Never';
$sambasettings{'LOGLEVEL'} = '3 passdb:5 auth:5 winbind:2';
### Values that have to be initialized
$sambasettings{'ACTION'} = '';
my $LOGLINES = '50';

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
if ($sambasettings{'ACTION'} eq 'globalresetyes')
	{
	system("/usr/local/bin/sambactrl smbglobalreset");
	$sambasettings{'WORKGRP'} = 'homeip.net';
	$sambasettings{'NETBIOSNAME'} = 'IPFire';
	$sambasettings{'SRVSTRING'} = 'Samba running on IPFire 2.0';
	$sambasettings{'INTERFACES'} = '';
	$sambasettings{'SECURITY'} = 'share';
	$sambasettings{'OSLEVEL'} = '65';
	$sambasettings{'GREEN'} = 'on';
	$sambasettings{'BLUE'} = 'off';
	$sambasettings{'ORANGE'} = 'off';
	$sambasettings{'VPN'} = 'off';
	$sambasettings{'WINSSRV'} = '';
	$sambasettings{'WINSSUPPORT'} = 'on';
	$sambasettings{'REMOTEANNOUNCE'} = '';
	$sambasettings{'PASSWORDSYNC'} = 'off';
	$sambasettings{'OTHERINTERFACES'} = '127.0.0.1';
	$sambasettings{'GUESTACCOUNT'} = 'samba';
	$sambasettings{'MAPTOGUEST'} = 'Never';
	$sambasettings{'LOGLEVEL'} = '3 passdb:5 auth:5 winbind:2';
### Values that have to be initialized
	$sambasettings{'ACTION'} = '';
	$sambasettings{'LOCALMASTER'} = 'off';
	$sambasettings{'DOMAINMASTER'} = 'off';
	$sambasettings{'PREFERREDMASTER'} = 'off';
	$PDCOPTIONS = `cat ${General::swroot}/samba/pdc`;
	}

# smbsafeconf is directly called by the if clause

if ($sambasettings{'ACTION'} eq 'sharesresetyes')
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
################################################ Sicherheitsabfrage für den Reset ##########################################

if ($sambasettings{'ACTION'} eq 'globalreset')
	{
	print <<END
	<table width='95%' cellspacing='0'>
	<tr><td colspan='2'><br /></td></tr>
	<tr><td bgcolor='${Header::table1colour}' colspan='3' align='center'><b>Globals zurück setzen?</b>
	<tr><td align='right' width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					 Yes <input type='image' alt='Yes' src='/images/edit-redo.png' />
					<input type='hidden' name='ACTION' value='globalresetyes' /></form></td>
			<td align='left'  width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='image' alt='No' src='/images/dialog-error.png' /> No 
					<input type='hidden' name='ACTION' value='cancel' /></form></td>
	</tr>
	</table>
END
;
}

if ($sambasettings{'ACTION'} eq 'sharesreset')
	{
	print <<END
	<table width='95%' cellspacing='0'>
	<tr><td colspan='2'><br /></td></tr>
	<tr><td bgcolor='${Header::table1colour}' colspan='3' align='center'><b>Shares zurück setzen?</b>
	<tr><td align='right'  width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					 Yes <input type='image' alt='Yes' src='/images/edit-redo.png' />
					<input type='hidden' name='ACTION' value='sharesresetyes' /></form></td>
			<td align='left'  width='50%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='image' alt='No' src='/images/dialog-error.png' /> No 
					<input type='hidden' name='ACTION' value='cancel' /></form></td>
	</tr>
	</table>
END
;
	}

############################################################################################################################
########################################### Samba Benutzer oder PC l�chen #################################################

if ($sambasettings{'ACTION'} eq 'userdelete'){system("/usr/local/bin/sambactrl smbuserdelete $sambasettings{'NAME'}");}

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
if ($sambasettings{'WINSSUPPORT'} eq 'on'){ $sambasettings{'WINSSUPPORT'} = "true";$sambasettings{'WINSSRV'} = "";} else { $sambasettings{'WINSSUPPORT'} = "false";}
if ($sambasettings{'LOCALMASTER'} eq 'on'){ $sambasettings{'LOCALMASTER'} = "true";} else { $sambasettings{'LOCALMASTER'} = "false";}
if ($sambasettings{'DOMAINMASTER'} eq 'on'){ $sambasettings{'DOMAINMASTER'} = "true";} else { $sambasettings{'DOMAINMASTER'} = "false";}
if ($sambasettings{'PREFERREDMASTER'} eq 'on'){ $sambasettings{'PREFERREDMASTER'} = "true";} else { $sambasettings{'PREFERREDMASTER'} = "false";}

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
remote announce = $sambasettings{'REMOTEANNOUNCE'}

username level = 1
wins support = $sambasettings{'WINSSUPPORT'}
wins server = $sambasettings{'WINSSRV'}

log file       = /var/log/samba/samba-log.%m
lock directory = /var/lock/samba
pid directory = /var/run/
log level = $sambasettings{'LOGLEVEL'}
	
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

&Header::openbox('100%', 'center', $Lang::tr{'samba'});
print <<END
        <hr />
        <table width='95%' cellspacing='0'>
END
;
if ( $message ne "" )
	{
	print "<tr><td colspan='3' align='left'><font color='red'>$message</font>";
	}

print <<END
<tr><td colspan='3'><br /></td></tr>
<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'all services'}</b></td></tr>
</table><table width='95%' cellspacing='0'>
END
;

my $key = '';
foreach $key (sort keys %servicenames)
	{
	print "<tr><td align='left' width='40%'>$key</td>";
	my $shortname = $servicenames{$key};
	my $status = &isrunning($shortname);
	print "$status</tr>";
	}

print <<END
<tr><td colspan='3'><br /></td></tr>
<tr><td></td><td colspan='2' align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
																		<input type='submit' name='ACTION' value='smbstart' />
																		<input type='submit' name='ACTION' value='smbstop' />
																		<input type='submit' name='ACTION' value='smbrestart' />
</form></td></tr>
</table>


<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='95%' cellspacing='0'>
<tr><td colspan='2'><br /></td></tr>
<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'basic options'}</b></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'workgroup'}</td><td align='left'><input type='text' name='WORKGRP' value='$sambasettings{'WORKGRP'}' size="30" /></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'netbios name'}</td><td align='left'><input type='text' name='NETBIOSNAME' value='$sambasettings{'NETBIOSNAME'}' size="30" /></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'server string'}</td><td align='left'><input type='text' name='SRVSTRING' value='$sambasettings{'SRVSTRING'}' size="30" /></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'log level'}</td><td align='left'><input type='text' name='LOGLEVEL' value='$sambasettings{'LOGLEVEL'}' size="30" /></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'interfaces'}</td><td align='left'>on <input type='radio' name='VPN' value='on' $checked{'VPN'}{'on'} />/
																						<input type='radio' name='VPN' value='off' $checked{'VPN'}{'off'} /> off |
																						<font size='2' color='$Header::colourovpn'><b>   OpenVpn  -  $ovpnsettings{'DDEVICE'}</b></font></td></tr>
<tr><td align='left' width='40%'></td><td align='left'>on <input type='radio' name='GREEN' value='on' $checked{'GREEN'}{'on'} />/
																	<input type='radio' name='GREEN' value='off' $checked{'GREEN'}{'off'} /> off |
																	<font size='2' color='$Header::colourgreen'><b>   $Lang::tr{'green'}  -  $netsettings{'GREEN_DEV'}</b></font></td></tr>
END
;

if (&Header::blue_used())
	{
	print <<END
	<tr><td align='left' width='40%'></td><td align='left'>on <input type='radio' name='BLUE' value='on' $checked{'BLUE'}{'on'} />/
																		<input type='radio' name='BLUE' value='off' $checked{'BLUE'}{'off'} /> off |
																		<font size='2' color='$Header::colourblue'><b>   $Lang::tr{'wireless'}  -  $netsettings{'BLUE_DEV'}</b></font></td></tr>
END
;
	}

if (&Header::orange_used())
	{
	print <<END
	<tr><td align='left' width='40%'></td><td align='left'>on <input type='radio' name='ORANGE' value='on' $checked{'ORANGE'}{'on'} />/
																		<input type='radio' name='ORANGE' value='off' $checked{'ORANGE'}{'off'} /> off |
																		<font size='2' color='$Header::colourorange'><b>   $Lang::tr{'dmz'}  -  $netsettings{'ORANGE_DEV'}</b></font></td></tr>
END
;
	}

print <<END
<tr><td align='center' width='40%'>$Lang::tr{'more'}</td><td align='left'><input type='text' name='OTHERINTERFACES' value='$sambasettings{'OTHERINTERFACES'}' size="30" /></td></tr>
<tr><td align='left'><br /></td><td></td></tr>
<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'security options'}</b></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'security'}</td><td align='left'><select name='SECURITY' style="width: 165px">
																				<option value='share' $selected{'SECURITY'}{'share'}>Share</option>
																				<option value='user' $selected{'SECURITY'}{'user'}>User</option>
																				<option value='domain' $selected{'SECURITY'}{'domain'}>Domain</option>
																				<option value='ADS' $selected{'SECURITY'}{'ADS'}>ADS</option>
																				<option value='server' $selected{'SECURITY'}{'server'}>Server</option>
																				</select></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'map to guest'}</td><td align='left'><select name='MAPTOGUEST' style="width: 165px">
																						<option value='Never' $selected{'MAPTOGUEST'}{'Never'}>Never</option>
																						<option value='Bad User' $selected{'MAPTOGUEST'}{'Bad User'}>Bad User</option>
																						<option value='Bad Password' $selected{'MAPTOGUEST'}{'Bad Password'}>Bad Password</option>
																						</select></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'unix password sync'}</td><td align='left'>on <input type='radio' name='PASSWORDSYNC' value='on' $checked{'PASSWORDSYNC'}{'on'} />/
																										<input type='radio' name='PASSWORDSYNC' value='off' $checked{'PASSWORDSYNC'}{'off'} /> off</td></tr>
<tr><td align='left'><br /></td><td /></tr>
<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'network options'}</b></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'os level'}</td><td align='left'><input type='text' name='OSLEVEL' value='$sambasettings{'OSLEVEL'}' size="30" /></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'remote announce'}</td><td align='left'><input type='text' name='REMOTEANNOUNCE' value='$sambasettings{'REMOTEANNOUNCE'}' size="30" /></td></tr>
END
;
if ($sambasettings{'WINSSUPPORT'} eq 'off') {print"<tr><td align='left' width='40%'>$Lang::tr{'wins server'}</td><td align='left'><input type='text' name='WINSSRV' value='$sambasettings{'WINSSRV'}' size='30' /></td></tr>";}
	print <<END
<tr><td align='left' width='40%'>$Lang::tr{'wins support'}</td><td align='left'>on <input type='radio' name='WINSSUPPORT' value='on' $checked{'WINSSUPPORT'}{'on'} />/
																								<input type='radio' name='WINSSUPPORT' value='off' $checked{'WINSSUPPORT'}{'off'} /> off</td></tr>
END
;

if ($sambasettings{'SECURITY'} eq 'user')
	{
	print <<END
<tr><td align='left' width='40%'>$Lang::tr{'local master'}</td><td align='left'>on <input type='radio' name='LOCALMASTER' value='on' $checked{'LOCALMASTER'}{'on'} />/
																							<input type='radio' name='LOCALMASTER' value='off' $checked{'LOCALMASTER'}{'off'} /> off</td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'domain master'}</td><td align='left'>on <input type='radio' name='DOMAINMASTER' value='on' $checked{'DOMAINMASTER'}{'on'} />/
																								<input type='radio' name='DOMAINMASTER' value='off' $checked{'DOMAINMASTER'}{'off'} /> off</td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'prefered master'}</td><td align='left'>on <input type='radio' name='PREFERREDMASTER' value='on' $checked{'PREFERREDMASTER'}{'on'} />/
																									<input type='radio' name='PREFERREDMASTER' value='off' $checked{'PREFERREDMASTER'}{'off'} /> off</td></tr>
END
;
	}

if ($sambasettings{'SECURITY'} eq 'user' && $sambasettings{'DOMAINMASTER'} eq 'on')
	{
	print <<END
	<tr><td align='left'><br /></td><td></td></tr>
	<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'pdc options'}</b></td></tr>
	<tr><td align='left'><br /></td><td></td></tr>
	<tr><td colspan='2' align='center'><textarea name="PDCOPTIONS" cols="50" rows="15" Wrap="off">$PDCOPTIONS</textarea></td></tr>
END
;
	}

print <<END
</table>
<table width='10%' cellspacing='0'>
<tr><td colspan='3'><br /></td></tr>
<tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value=$Lang::tr{'save'} />
												<input type='image' alt='$Lang::tr{'save'}' src='/images/floppy.gif' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
										<input type='hidden' name='ACTION' value='globalreset' />
										<input type='image' alt='$Lang::tr{'reset'}' src='/images/reload.gif' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
										<input type='hidden' name='ACTION' value='globalcaption' />
										<input type='image' alt='$Lang::tr{'caption'}' src='/images/info.gif' /></form></td></tr>
</table>
END
;

if ($sambasettings{'ACTION'} eq 'globalcaption')
	{
	print <<END
	<table width='95%' cellspacing='0'>
	<tr><td colspan='2'><br /></td></tr>
	<tr><td align='center' colspan='2'><b>$Lang::tr{'caption'}</b></td></tr>
	<tr><td align='right' width='33%'><img src='/images/floppy.gif' /></td><td align='left'>$Lang::tr{'save settings'}</td></tr>
	<tr><td align='right' width='33%'><img src='/images/reload.gif' /></td><td align='left'>$Lang::tr{'restore settings'}</td></tr>
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
		&Header::openbox('100%', 'center', $Lang::tr{'accounting user nonpdc'});
		}
	else
		{
		&Header::openbox('100%', 'center', $Lang::tr{'accounting user pdc'});
		}
	print <<END
	<hr />
	<table width='95%' cellspacing='0'>
	<tr><td colspan='6'><br /></td></tr>
	<tr><td colspan='6' align='left'></td></tr>
	<tr><td bgcolor='${Header::table1colour}' colspan='7' align='left'><b>$Lang::tr{'accounting'}</b></td></tr>
	<tr><td align='left'><u>$Lang::tr{'username'}</u></td><td align='left'><u>$Lang::tr{'password'}</u></td>
END
;

	if ($sambasettings{'DOMAINMASTER'} eq 'off')
		{
		print "<td></td>";
		}
	else
		{
		print "<td align='left'><u>Typ</u></td>";
		}

	print "<td align='left'><u>$Lang::tr{'interfaces'}</u></td><td colspan='3' width='5%' align='center'><u>$Lang::tr{'options'}</u></td></tr>";
	system('/usr/local/bin/sambactrl readsmbpasswd');
	open(FILE, "</var/ipfire/samba/private/smbpasswd") or die "Can't read user file: $!";
	@user = <FILE>;
	close(FILE);
	system('/usr/local/bin/sambactrl locksmbpasswd');
	foreach $userentry (sort @user)
		{
		@userline = split( /\:/, $userentry );
		print "<tr><td align='left'>$userline[0]</td><td align='left'>";
		if ($userline[4] =~ /N/)
			{
			print "$Lang::tr{'not set'}</td><td align='left'>";
			}
		else
			{
			print "$Lang::tr{'set'}</td><td align='left'>";
			}

		if ($sambasettings{'DOMAINMASTER'} eq 'off')
			{
			print "</td><td align='left'>";
			}
		else
			{
			if ($userline[0] =~ /\$/)
				{
				print "$Lang::tr{'interfaces'}</td><td align='left'>";
				}
			else
				{
				print "$Lang::tr{'user'}</td><td align='left'>";
				}
			}

		if ($userline[4] =~ /D/)
			{
			print <<END
			inaktiv</td>
			<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='hidden' name='NAME' value='$userline[0]' />
					<input type='hidden' name='ACTION' value='smbuserenable' />
					<input type='image' alt='$Lang::tr{'activate'}' src='/images/on.gif' />
			</form></td>
END
;
			}
		else
			{
			print <<END
			aktiv</td>
			<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='hidden' name='NAME' value='$userline[0]' />
					<input type='hidden' name='ACTION' value='smbuserdisable' />
					<input type='image' alt='$Lang::tr{'deactivate'}' src='/images/off.gif' />
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
			<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='hidden' name='NAME' value='$userline[0]' />
					<input type='hidden' name='ACTION' value='userchangepw' />
					<input type='image' alt='$Lang::tr{'edit'}' src='/images/edit.gif' />
			</form></td>
END
;
			}

			if ($sambasettings{'DOMAINMASTER'} eq 'on' && $userline[0] =~ /\$/)
				{
				print <<END
				<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='NAME' value='$userline[0]' />
						<input type='hidden' name='ACTION' value='userdelete' />
						<input type='image' alt='$Lang::tr{'delete'}' src='/images/network-error.png' />
						</form></td></tr>
END
;
				}
			else
				{
				print <<END
				<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='NAME' value='$userline[0]' />
						<input type='hidden' name='ACTION' value='userdelete' />
						<input type='image' alt='$Lang::tr{'delete'}' src='/images/user-option-remove.png' />
				</form></td></tr>
END
;
				}
		}
	print <<END
	</table>
	<table width='10%' cellspacing='0'>
	<tr><td colspan='3'><br /></td></tr>
	<tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
													<input type='hidden' name='ACTION' value='useradd' />
													<input type='image' alt='$Lang::tr{'add user'}' src='/images/user-option-add.png' /></form></td>
END
;

	if ($sambasettings{'DOMAINMASTER'} eq 'on')
		{
		print <<END
		<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value='pcadd' />
												<input type='image' alt='$Lang::tr{'add pc'}' src='/images/network.png' /></form>
END
;
		}
	print <<END
	<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
											<input type='hidden' name='ACTION' value='usercaption' />
											<input type='image' alt='$Lang::tr{'caption'}' src='/images/info.gif' /></form>
	</td></tr>
	</table>
END
;

	if ($sambasettings{'ACTION'} eq 'usercaption')
		{
		print <<END
		<table width='95%' cellspacing='0'>
		<tr><td align='center' colspan='2'><br /></td></tr>
		<tr><td align='center' colspan='2'><b>$Lang::tr{'caption'}</b></td></tr>
		<tr><td align='right' width='33%'><img src='/images/user-option-add.png' /></td><td align='left'>$Lang::tr{'add user'}</td></tr>
		<tr><td align='right' width='33%'><img src='/images/network.png' /></td><td align='left'>$Lang::tr{'add pc'}</td></tr>
		<tr><td align='right' width='33%'><img src='/images/user-option-remove.png' /></td><td align='left'>$Lang::tr{'delete user'}</td></tr>
		<tr><td align='right' width='33%'><img src='/images/network-error.png' /></td><td align='left'>$Lang::tr{'delete pc'}</td></tr>
		<tr><td align='right' width='33%'><img src='/images/on.gif' /></td><td align='left'>$Lang::tr{'activate user'}</td></tr>
		<tr><td align='right' width='33%'><img src='/images/off.gif' /></td><td align='left'>$Lang::tr{'deactivate user'}</td></tr>
		<tr><td align='right' width='33%'><img src='/images/edit.gif' /></td><td align='left'>$Lang::tr{'change passwords'}</td></tr>
		<tr><td align='right' width='33%'><img src='/images/floppy.gif' /></td><td align='left'>$Lang::tr{'save config'}</td></tr>
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
		<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'change passwords'}</b></td></tr>
		<tr><td align='left'>$Lang::tr{'username'}</td><td><input type='text' name='USERNAME' value='$username' size='30' /></td></tr>
		<tr><td align='left'>$Lang::tr{'password'}</td><td><input type='password' name='PASSWORD' value='$password' size='30' /></td></tr>
		<tr><td colspan='2' align='center'><input type='hidden' name='ACTION' value='smbchangepw' />
																				<input type='image' alt=$Lang::tr{'save'} src='/images/floppy.gif' /></td></tr>
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
		<hr />
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='95%' cellspacing='0'>
		<tr><td colspan='2'><br /></td></tr>
		<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'add user'}</b></td></tr>
		<tr><td align='left'>$Lang::tr{'username'}</td><td><input type='text' name='USERNAME' value='$username' size='30' /></td></tr>
		<tr><td align='left'>$Lang::tr{'password'}</td><td><input type='password' name='PASSWORD' value='$password' size='30' /></td></tr>
		<tr><td align='left'>$Lang::tr{'unix group'}</td><td><input type='text' name='GROUP' value='sambauser' size='30' /></td></tr>
		<tr><td align='left'>$Lang::tr{'unix shell'}</td><td><input type='text' name='SHELL' value='/bin/false' size='30' /></td></tr>
		<tr><td colspan='2' align='center'><input type='hidden' name='ACTION' value='smbuseradd' />
																				<input type='image' alt=$Lang::tr{'save'} src='/images/floppy.gif' /></td></tr>
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
		<hr />
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table width='95%' cellspacing='0'>
		<tr><td colspan='2'><br /></td></tr>
		<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'pc add'}</b></td></tr>
		<tr><td align='left'>$Lang::tr{'client'}</td><td><input type='text' name='PCNAME' value='$pcname' size='30' /></td></tr>
		<tr><td align='left'>$Lang::tr{'unix group'}</td><td><input type='text' name='GROUP' value='sambawks' size='30' /></td></tr>
		<tr><td align='left'>$Lang::tr{'unix shell'}</td><td><input type='text' name='SHELL' value='/bin/false' size='30' /></td></tr>
		<tr><td colspan='2' align='center'><input type='hidden' name='ACTION' value='smbpcadd' />
																				<input type='image' alt=$Lang::tr{'save'} src='/images/floppy.gif' /></td></tr>
		</table>
		</form>
END
;
		}

&Header::closebox();
}

############################################################################################################################
############################################### Verwalten von Freigaben ####################################################

&Header::openbox('100%', 'center', $Lang::tr{'shares'});

print <<END
<hr />
<table width='95%' cellspacing='0'>
<tr><td colspan='3'><br /></td></tr>
<tr><td bgcolor='${Header::table1colour}' colspan='3' align='left'><b>$Lang::tr{'manage shares'}</b>
<tr><td align='left'><u>$Lang::tr{'sharename'}</u></td><td colspan='2' width="5%" align='center'><u>$Lang::tr{'options'}</u></td></tr>
END
;

foreach $shareentry (sort @Shares)
	{
	print <<END
	<tr><td align='left'>$shareentry</td>
	<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='hidden' name='NAME' value='$shareentry' />
			<input type='hidden' name='ACTION' value='sharechange' />
			<input type='image' alt='$Lang::tr{'edit'}' src='/images/edit.gif' />
	</form></td>
	<td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='hidden' name='NAME' value='$shareentry' />
			<input type='hidden' name='ACTION' value='smbsharedel' />
			<input type='image' alt='$Lang::tr{'delete'}' src='/images/delete.gif' />
	</form></td></tr>
END
;
	}

print <<END
</table>
<table width='10%' cellspacing='0'>
<tr><td colspan='3'><br /></td></tr>
<tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value='shareadd' />
												<input type='image' alt='$Lang::tr{'add share'}' src='/images/add.gif' />
												</form></td>
		<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value='sharesreset' />
												<input type='image' alt='$Lang::tr{'reset'}' src='/images/reload.gif' />
												</form></td>
		<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
												<input type='hidden' name='ACTION' value='sharecaption' />
												<input type='image' alt='$Lang::tr{'caption'}' src='/images/info.gif' />
												</form></td></tr>
</table>
END
;

if ($sambasettings{'ACTION'} eq 'sharecaption')
	{
	print <<END
	<table width='95%' cellspacing='0'>
	<tr><td align='center' colspan='2'><br /></td></tr>
	<tr><td align='center' colspan='2'><b>Legende:</b></td></tr>
	<tr><td align='right' width='33%'><img src='/images/add.gif' /></td><td align='left'>$Lang::tr{'add share'}</td></tr>
	<tr><td align='right' width='33%'><img src='/images/edit.gif' /></td><td align='left'>$Lang::tr{'edit share'}</td></tr>
	<tr><td align='right' width='33%'><img src='/images/floppy.gif' /></td><td align='left'>$Lang::tr{'save config'}</td></tr>
	<tr><td align='right' width='33%'><img src='/images/reload.gif' /></td><td align='left'>$Lang::tr{'reset shares'}</td></tr>
	<tr><td align='right' width='33%'><img src='/images/delete.gif' /></td><td align='left'>$Lang::tr{'delete share'}</td></tr>
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
	<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'add share'}</b></td></tr>
	<tr><td colspan='2' align='center'></td></tr>
	<tr><td colspan='2' align='center'>$Lang::tr{'show share options'}<form method='post' action='$ENV{'SCRIPT_NAME'}'>
																																			<input type='hidden' name='ACTION' value='optioncaption' />
																																			<input type='image' alt='$Lang::tr{'caption'}' src='/images/info.gif' />
																																			</form></td></tr>
	<form method='post' action='$ENV{'SCRIPT_NAME'}'><tr><td colspan='2' align='center'><textarea name="SHAREOPTION" cols="50" rows="15" Wrap="off">$defaultoption</textarea></td></tr>
	</table>
	<table width='10%' cellspacing='0'>
	<tr><td><br /></td></tr>
	<tr><td align='center'><input type='hidden' name='ACTION' value='smbshareadd' />
													<input type='image' alt='$Lang::tr{'add share'}' src='/images/floppy.gif' /></td></tr></form>
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
	<tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>$Lang::tr{'edit share'}</b></td></tr>
	<tr><td colspan='2' align='center'></td></tr>
	<tr><td colspan='2' align='center'>$Lang::tr{'show share options'}<form method='post' action='$ENV{'SCRIPT_NAME'}'>
																																			<input type='hidden' name='ACTION' value='optioncaption2' />
																																			<input type='image' alt='$Lang::tr{'caption'}' src='/images/info.gif' /></form></td></tr>
	<tr><td colspan='2' align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'><textarea name="SHAREOPTION" cols="50" rows="15" Wrap="off">$shareoption</textarea></td></tr>
	</table>
	<table width='10%' cellspacing='0'>
	<tr><td><br /></td></tr>
	<tr><td align='center'><input type='hidden' name='NAME' value='$sambasettings{'NAME'}' />
													<input type='image' alt='$Lang::tr{'change share'}' src='/images/floppy.gif' />
													<input type='hidden' name='ACTION' value='smbsharechange' /></form></td></tr>
	</table>
END
;
	}

if ($sambasettings{'ACTION'} eq 'optioncaption' || $sambasettings{'ACTION'} eq 'optioncaption2')
	{
	print <<END
	<table width='95%' cellspacing='0'>
	<tr><td><br /></td></tr>
	<tr><td><b>$Lang::tr{'caption'}</b></td></tr>
	<tr><td><u>$Lang::tr{'options'}</u></td><td><u>$Lang::tr{'meaning'}</u> / <u>$Lang::tr{'exampel'}</u></td></tr>
	<tr><td>comment</td><td>$Lang::tr{'comment'}</td></tr>
	<tr><td></td><td>comment = $Lang::tr{'my new share'}</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>path</td><td>$Lang::tr{'path to directory'}</td></tr>
	<tr><td></td><td>path = /tmp</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>writeable</td><td>$Lang::tr{'directory writeable'}</td></tr>
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
	<tr><td>write list</td><td>$Lang::tr{'visible in browselist'}</td></tr>
	<tr><td></td><td>write list = samba</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>hosts allow</td><td>$Lang::tr{'host allow'}</td></tr>
	<tr><td></td><td>hosts allow = localhost 192.168.1.1 192.168.2.0/24</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>hosts deny</td><td>$Lang::tr{'host deny'}</td></tr>
	<tr><td></td><td>hosts deny = 192.168.1.2 192.168.3.0/24</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>read list</td><td>$Lang::tr{'read list'}</td></tr>
	<tr><td></td><td>read list = user1</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>admin users</td><td>$Lang::tr{'admin users'}</td></tr>
	<tr><td></td><td>admin users = user1</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>invalid users</td><td>$Lang::tr{'invalid users'}</td></tr>
	<tr><td></td><td>invalid users = user2</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>force user</td><td>$Lang::tr{'force user'}</td></tr>
	<tr><td></td><td>force user = samba</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>directory mask</td><td>$Lang::tr{'directory mask'}</td></tr>
	<tr><td></td><td>directory mask = 0777</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>create mask</td><td>U$Lang::tr{'create mask'}</td></tr>
	<tr><td></td><td>create mask = 0777</td></tr>
	<tr><td><br /></td><td></td></tr>
	<tr><td>guest ok</td><td>$Lang::tr{'guest ok'}</td></tr>
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
<tr><td colspan='4'  align='left'><br /></td></tr>
<tr><td bgcolor='${Header::table1colour}' colspan='3' align='left'><b>$Lang::tr{'samba status'}</b></td></tr>
<tr><td  align='left'>$Status</td></tr>
</table>
END
;
&Header::closebox();

############################################################################################################################
############################################### Anzeige des Sambastatus ####################################################


if ($sambasettings{'ACTION'} eq 'showlog')
{
$Log = qx(tail -n $LOGLINES /var/log/samba/$sambasettings{'LOG'});
$Log=~s/\n/<br \/>/g;
}

&Header::openbox('100%', 'center', $Lang::tr{'log'});

print <<END
<hr />
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='95%' cellspacing='0'>
<tr><td colspan='3'  align='left'><br /></td></tr>
<tr><td bgcolor='${Header::table1colour}' colspan='3' align='left'><b>$Lang::tr{'log view'}</b></td></tr>
<tr><td colspan='3'  align='left'><br /></td></tr>
<tr><td  align='left'><select name='LOG' style="width: 200px">
END
;
foreach my $log (@Logs) {chomp $log;print"<option value='$log'>$log</option>";}
print <<END

</select></td><td  align='left'>$Lang::tr{'show last x lines'}<input type='text' name='LOGLINES' value='$LOGLINES' size="3" /></td>
			<td  align='left'><input type='hidden' name='ACTION' value='showlog' /><input type='image' alt='view Log' src='/images/document-open.png' /></td></tr>
<tr><td colspan='3'  align='left'><br /></td></tr>
<tr><td colspan='3'  align='left'><font size=2>$Log</font></td></tr>
<tr><td colspan='3'  align='left'><br /></td></tr>
<tr><td colspan='3'  align='center'>$sambasettings{'LOG'}</td></tr>
</table>
</form>
END
;

&Header::closebox();
&Header::closebigbox();
&Header::closepage();

############################################################################################################################
############################################ Subfunktion fr Sambadienste ###################################################

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