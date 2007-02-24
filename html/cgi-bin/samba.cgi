#!/usr/bin/perl
#
# IPFire CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The IPFire Team
#

use strict;
# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %sambasettings = ();
my %checked = ();
my %netsettings = ();
my %ovpnsettings = ();
my $message = "";
my $errormessage = "";
my $shareconfigentry = "";
my @sharesconfig = ();
my @shareconfigline = ();
my $shareoption = '';
my $defaultoption= "[Share]\npath = /shares/share1\ncomment = Share - Public Access\nbrowseable = yes\nwriteable = yes\ncreate mask = 0777\ndirectory mask = 0777\nguest ok = yes\npublic = yes\nforce user = samba";
my $userentry = "";
my @user = ();
my @userline = ();
my @proto = ();
my %selected= () ;
my $userfile = "/var/ipfire/samba/private/smbpasswd";
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
&General::readhash("${General::swroot}/ovpn/settings", \%ovpnsettings);

############################################################################################################################
############################################# Samba Dienste für Statusüberprüfung ##########################################

my %servicenames =
(
        'SMB Daemon' => 'smbd',
        'NetBIOS Nameserver' => 'nmbd',
        'Winbind Daemon' => 'winbindd'
);

&Header::showhttpheaders();

############################################################################################################################
#################################### Initialisierung von Samba Sharess für die Verarbeitung ################################

my @Zeilen= ();
my @Shares= ();
my $shareentry = "";
my @shares = ();
my @shareline = ();
my $sharefile = "/var/ipfire/samba/shares";
my $EOF = qx(cat $sharefile | wc -l);

@shares = `grep -n '^\\[' $sharefile`;
foreach $shareentry (@shares)
 {
 @shareline = split( /\:/, $shareentry );
 push(@Zeilen,$shareline[0]);push(@Shares,$shareline[1]);
 }

############################################################################################################################
#################################### Initialisierung von Samba Variablen für global Settings ###############################

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
$sambasettings{'OTHERINTERFACES'} = '';
$sambasettings{'GUESTACCOUNT'} = 'samba';
$sambasettings{'MAPTOGUEST'} = 'Never';
$sambasettings{'BINDINTERFACESONLY'} = 'True';
### Values that have to be initialized
$sambasettings{'ACTION'} = '';

&General::readhash("${General::swroot}/samba/settings", \%sambasettings);
&Header::getcgihash(\%sambasettings);

&Header::openpage('Samba', 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
############################################# Samba Rootskript aufrufe für SU-Actions ######################################

if ($sambasettings{'ACTION'} eq 'smbuserdisable'){system('/usr/local/bin/sambactrl smbuserdisable $sambasettings{"NAME"}');}
if ($sambasettings{'ACTION'} eq 'smbuserenable'){system('/usr/local/bin/sambactrl smbuserenable $sambasettings{"NAME"}');}
if ($sambasettings{'ACTION'} eq 'smbuserdelete'){system('/usr/local/bin/sambactrl smbuserdelete $sambasettings{"NAME"}');}
if ($sambasettings{'ACTION'} eq 'smbuseradd'){system('/usr/local/bin/sambactrl smbuseradd $username $password');}
if ($sambasettings{'ACTION'} eq 'smbchangepw'){system('/usr/local/bin/sambactrl smbchangepw $username $password');}
if ($sambasettings{'ACTION'} eq 'smbrestart'){system('/usr/local/bin/sambactrl smbrestart');}
if ($sambasettings{'ACTION'} eq 'smbstart'){system('/usr/local/bin/sambactrl smbstart');}
if ($sambasettings{'ACTION'} eq 'smbstop'){system('/usr/local/bin/sambactrl smbstop');}
# smbsharechange is directly called by the if clause

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
system('/usr/local/bin/sambactrl smbsharechange');

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
################################################## Samba Share löschen #####################################################

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
system('/usr/local/bin/sambactrl smbsharechange');

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
################################################## Sambashare ändern #######################################################

if ($sambasettings{'ACTION'} eq 'smbsharechange')
{
my $sharebody = '';
my $sharehead = '';
my $sharename = "$sambasettings{'NAME'}";
my $sharetext = '';
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
$sambasettings{'SHAREOPTION'}
END
;
close FILE;
system('/usr/local/bin/sambactrl smbsharechange');

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
if ($checked{'GREEN'}){ $sambasettings{'INTERFACES'} = "$sambasettings{'INTERFACES'} $netsettings{'GREEN_DEV'}";}
if ($checked{'BLUE'}){ $sambasettings{'INTERFACES'} = "$sambasettings{'INTERFACES'} $netsettings{'BLUE_DEV'}";}
if ($checked{'ORANGE'}){ $sambasettings{'INTERFACES'} = "$sambasettings{'INTERFACES'} $netsettings{'ORANGE_DEV'}";}
if ($checked{'VPN'}){ $sambasettings{'INTERFACES'} = "$sambasettings{'INTERFACES'} $ovpnsettings{'DDEVICE'}";}
if ($sambasettings{'OTHERINTERFACES'} ne ''){ $sambasettings{'INTERFACES'} = "$sambasettings{'INTERFACES'} $sambasettings{'OTHERINTERFACES'}";}

############################################################################################################################
############################################# Schreiben der Samba globals ##################################################

  &General::writehash("${General::swroot}/samba/settings", \%sambasettings);

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
	
	preferred master = yes
	domain master = yes
	local master = yes

	kernel oplocks = false
	map to guest = $sambasettings{'MAPTOGUEST'}
	smb ports = 445 139
	unix charset = CP850

	security = $sambasettings{'SECURITY'}
	encrypt passwords = yes
	guest account = $sambasettings{'GUESTACCOUNT'}
	unix password sync = no
	null passwords = yes

	bind interfaces only = $sambasettings{'BINDINTERFACESONLY'}
	interfaces = $sambasettings{'INTERFACES'}
	socket options = TCP_NODELAY IPTOS_NODELAY SO_RCVBUF=8192 SO_SNDBUF=8192 SO_KEEPALIVE

	username level = 1
	wins support = $sambasettings{'WINSSUPPORT'}
	local master = yes

	log file       = /var/log/samba/samba-log.%m
	lock directory = /var/lock/samba
	pid directory = /var/run/

END
;
	close FILE;
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

$checked{'WINSSUPPORT'}{$sambasettings{'WINSSUPPORT'}} = "checked='checked' ";
$checked{'GREEN'}{$sambasettings{'GREEN'}} = "checked='checked' ";
$checked{'BLUE'}{$sambasettings{'BLUE'}} = "checked='checked' ";
$checked{'ORANGE'}{$sambasettings{'ORANGE'}} = "checked='checked' ";
$checked{'VPN'}{$sambasettings{'VPN'}} = "checked='checked' ";

$selected{'MAPTOGUEST'}{$sambasettings{'MAPTOGUEST'}} = "selected='selected'";
$selected{'SECURITY'}{$sambasettings{'SECURITY'}} = "selected='selected'";

############################################################################################################################
################################### Aufbau der HTML Seite für globale Sambaeinstellungen ###################################

&Header::openbox('100%', 'center', 'Samba');
print <<END
        <hr>
        <table width='500px' cellspacing='0'><br>
END
;
        if ( $message ne "" ) {
                print "<tr><td colspan='2' align='left'><font color='red'>$message</font>";
        }
print <<END        
        <tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>Alle Dienste</b></td></tr>
        </table><table width='500px' cellspacing='0'>
END
;
        my $key = '';
        foreach $key (sort keys %servicenames)
        {
                print "<tr><td align='left'>$key";
                my $shortname = $servicenames{$key};
                my $status = &isrunning($shortname);
                print "$status</td>";
                print <<END
                        <td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
                                <input type='hidden' name='ACTION' value='restart $shortname'>
                                <input type='image' src='/images/reload.gif'>
                        </form></td>
END
;
        }
        print <<END
                <form method='post' action='$ENV{'SCRIPT_NAME'}'>
                <table width='500px' cellspacing='0'><br>
                <tr><td colspan='2' align='center'>
                <input type='submit' name='ACTION' value='Start' /> 
                <input type='submit' name='ACTION' value='Stop' /> 
                <input type='submit' name='ACTION' value='$Lang::tr{'restart'}' />
                </td></tr></form></table>
        
        <form method='post' action='$ENV{'SCRIPT_NAME'}'>
        <table width='500px' cellspacing='0'><br>
        <tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>Basisoptionen</b></td></tr>
        <tr><td align='left'>Workgroup:</td><td><input type='text' name='WORKGRP' value='$sambasettings{'WORKGRP'}' size="30"></td></tr>
        <tr><td align='left'>NetBIOS-Name:</td><td><input type='text' name='NETBIOSNAME' value='$sambasettings{'NETBIOSNAME'}' size="30"></td></tr>
        <tr><td align='left'>Server-String:</td><td><input type='text' name='SRVSTRING' value='$sambasettings{'SRVSTRING'}' size="30"></td></tr>
        <tr><td align='left'>Interfaces:</td><td><input type='checkbox' name='VPN' $checked{'VPN'}{'on'}><font size='2' color='$Header::colourovpn'><b>   OpenVpn  -  $ovpnsettings{'DDEVICE'}</td></tr>
        <tr><td align='left'></td><td><input type='checkbox' name='GREEN' $checked{'GREEN'}{'on'}><font size='2' color='$Header::colourgreen'><b>   $Lang::tr{'green'}  -  $netsettings{'GREEN_DEV'}</td></tr>
END
;
         if (&Header::blue_used()){
         print <<END
         <tr><td align='left'></td><td><input type='checkbox' name='BLUE' $checked{'BLUE'}{'on'}><font size='2' color='$Header::colourblue'><b>   $Lang::tr{'wireless'}  -  $netsettings{'BLUE_DEV'}</td></tr>
END
;
                                    }
         if (&Header::orange_used()){
         print <<END
         <tr><td align='left'></td><td><input type='checkbox' name='ORANGE' $checked{'ORANGE'}{'on'}><font size='2' color='$Header::colourorange'><b>   $Lang::tr{'dmz'}  -  $netsettings{'ORANGE_DEV'}</td></tr>
END
;
                                    }
        print <<END
        <tr><td align='center'>weitere</td><td><input type='text' name='OTHERINTERFACES' value='$sambasettings{'OTHERINTERFACES'}' size="30"></td></tr>
        <tr><td align='left'><br></td><td></td></tr>
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
        <tr><td align='left'><br></td><td></td></tr>
        <tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>Browsingoptionen</b></td></tr>
        <tr><td align='left'>OS Level:</td><td><input type='text' name='OSLEVEL' value='$sambasettings{'OSLEVEL'}' size="30"></td></tr>
        <tr><td align='left'><br></td><td></td></tr>        
        <tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>WINS-Optionen</b></td></tr>
        <tr><td align='left'>WINS-Server:</td><td><input type='text' name='WINSSRV' value='$sambasettings{'WINSSRV'}' size="30"></td></tr>
        <tr><td align='left'>WINS-Support:</td><td>on <input type='radio' name='WINSSUPPORT' value='on' $checked{'WINSSUPPORT'}{'on'}>/
                                                        <input type='radio' name='WINSSUPPORT' value='off' $checked{'WINSSUPPORT'}{'off'}> off</td></tr>
        <tr><td colspan='2' align='center'><input type='submit' name='ACTION' value=$Lang::tr{'save'}></td></tr>
        </table>
        </form>
END
;
&Header::closebox();

############################################################################################################################
########################################## Benutzerverwaltung für Usersecurity #############################################

if ($sambasettings{'SECURITY'} eq 'user')
{
&Header::openbox('100%', 'center', 'accounting - user Security');

print <<END
        <hr>        
        <table width='500px' cellspacing='0'><br>
        <tr><td colspan='6' align='left'>
        <tr><td bgcolor='${Header::table1colour}' colspan='6' align='left'><b>Benutzerverwaltung</b>
        <tr><td><u>Benutzername</u></td><td><u>Passwort</u></td><td><u>Status</u></td><td colspan='3' width="5"><u>Optionen</u></td></tr>
END
;

        system('/usr/local/bin/sambactrl readsmbpasswd');
        open(FILE, "</var/ipfire/samba/private/smbpasswd") or die "Can't read user file: $!";
        flock (FILE, 2);
        @user = <FILE>;
        close(FILE);
        system('/usr/local/bin/sambactrl locksmbpasswd');
        foreach $userentry (sort @user)
        {
        @userline = split( /\:/, $userentry );
        print <<END
        <tr><td align='left'>$userline[0]</td><td>
END
;
        if ($userline[2] =~ m/N/){
        print <<END
        nicht gesetzt</td><td>
END
;
        }else{
        print <<END
        gesetzt</td><td>
END
;
        }
        if ($userline[2] =~ m/D/){
        print <<END
        aktiv</td>
        <td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
                                        <input type='hidden' name='NAME' value='$userline[0]'>
                                        <input type='hidden' name='ACTION' value='userdisable'>
                                        <input type='image' alt='Deaktivieren' src='/images/off.gif'>
                                </form></td>
END
;
        }else{
        print <<END
        inaktiv</td>
        <td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
                                        <input type='hidden' name='NAME' value='$userline[0]'>
                                        <input type='hidden' name='ACTION' value='userenable'>
                                        <input type='image' alt='Aktivieren' src='/images/on.gif'>
                                </form></td>
END
;
        }
        print <<END
        <td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
                                <input type='hidden' name='NAME' value='$userline[0]'>
                                <input type='hidden' name='ACTION' value='userchangepw'>
                                <input type='image' alt='Bearbeiten' src='/images/edit.gif'>
                        </form></td>
        <td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
                                <input type='hidden' name='NAME' value='$userline[0]'>
                                <input type='hidden' name='ACTION' value='userdelete'>
                                <input type='image' alt='Loeschen' src='/images/delete.gif'>
                        </form></td>
        </td></tr>
END
;
        }
        print <<END
        </table>
        <table width='50px' cellspacing='0'><br>
        <tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
                               <input type='hidden' name='ACTION' value='useradd'>
                               <input type='image' alt='Benutzer anlegen' src='/images/add.gif'></form></td>
            <td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
                               <input type='hidden' name='ACTION' value='usercaption'>
                               <input type='image' alt='Legende' src='/images/info.gif'></form>
        </td><tr>
        </table>
END
;
if ($sambasettings{'ACTION'} eq 'usercaption')
{
        print <<END
        <table width='500px' cellspacing='0'><br>
        <tr><td><b>Legende:</b></td></tr>
        <tr><td><img src='/images/add.gif'>Benutzer neu anlegen</td></tr>
        <tr><td><img src='/images/on.gif'>Benutzer aktivieren</td></tr>
        <tr><td><img src='/images/off.gif'>Benutzer deaktivieren</td></tr>
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
        <hr>
        <form method='post' action='$ENV{'SCRIPT_NAME'}'>
        <table width='500px' cellspacing='0'><br>
        <tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>Passwort wechseln</b></td></tr>
        <tr><td align='left'>Benutzername</td><td><input type='text' name='USERNAME' value='$username' size="30"></td></tr>
        <tr><td align='left'>Passwort</td><td><input type='password' name='PASSWORD' value='$password' size="30"></td></tr>
        <tr><td colspan='2' align='center'><input type='submit' name='ACTION' value='smbchangepw'></td></tr></form>
        </table>
END
;
}
if ($sambasettings{'ACTION'} eq 'useradd')
{
        my $username = "User";
        my $password = 'samba';
        print <<END
        <hr>
        <form method='post' action='$ENV{'SCRIPT_NAME'}'>
        <table width='500px' cellspacing='0'><br>
        <tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>Benutzer neu anlegen</b></td></tr>
        <tr><td align='left'>Benutzername</td><td><input type='text' name='USERNAME' value='$username' size="30"></td></tr>
        <tr><td align='left'>Passwort</td><td><input type='password' name='PASSWORD' value='$password' size="30"></td></tr>
        <tr><td colspan='2' align='center'><input type='submit' name='ACTION' value='smbuseradd'></td></tr></form>
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
        <hr>
        <table width='500px' cellspacing='0'><br>
        <tr><td bgcolor='${Header::table1colour}' colspan='3' align='left'><b>Shareverwaltung</b>
        <tr><td><u>Names des Shares</u></td><td colspan='2' width="5"><u>Optionen</u></td></tr>
END
;

        
        foreach $shareentry (sort @Shares)
        {
        print <<END
        <tr><td align='left'>$shareentry</td>
            <td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
                 <input type='hidden' name='NAME' value='$shareentry'>
                 <input type='hidden' name='ACTION' value='sharechange'>
                 <input type='image' alt='Bearbeiten' src='/images/edit.gif'>
            </td></form>
            <td><form method='post' action='$ENV{'SCRIPT_NAME'}'>
                 <input type='hidden' name='NAME' value='$shareentry'>
                 <input type='hidden' name='ACTION' value='smbsharedel'>
                 <input type='image' alt='Loeschen' src='/images/delete.gif'>
            </td></form><tr>
END
;
        }
        print <<END
        </table>

        <table width='50px' cellspacing='0'><br>
        <tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
                               <input type='hidden' name='ACTION' value='shareadd'>
                               <input type='image' alt='neuen Share anlegen' src='/images/add.gif'></form></td>
            <td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
                               <input type='hidden' name='ACTION' value='sharecaption'>
                               <input type='image' alt='Legende' src='/images/info.gif'></form>
        </td><tr>
        </table>
END
;
if ($sambasettings{'ACTION'} eq 'sharecaption')
{
        print <<END
        <table width='500px' cellspacing='0'><br>
        <tr><td><b>Legende:</b></td></tr>
        <tr><td><img src='/images/add.gif'>Share neu anlegen</td></tr>
        <tr><td><img src='/images/edit.gif'>Share bearbeiten</td></tr>
        <tr><td><img src='/images/delete.gif'>Share loeschen</td></tr>
        </table>
END
;
}

if ($sambasettings{'ACTION'} eq 'shareadd' || $sambasettings{'ACTION'} eq 'optioncaption' )
{
        print <<END
        <hr>
        <table width='500px' cellspacing='0'><br>
        <tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>neuen Share anlegen</b></td></tr>
        <tr><td colspan='2' align='center'></td></tr>
        <form method='post' action='$ENV{'SCRIPT_NAME'}'>
        <tr><td colspan='2' align='center'>Anzeige der Optionen fuer Shares<input type='hidden' name='ACTION' value='optioncaption'>
                <input type='image' alt='Legende' src='/images/info.gif'></td></tr></form>
        <form method='post' action='$ENV{'SCRIPT_NAME'}'>
        <tr><td colspan='2' align='center'><textarea name="SHAREOPTION" cols="50" rows="15" Wrap="off">$defaultoption</textarea></td></tr>
        </table>
        <table width='50px' cellspacing='0'><br>
        <tr><td align='center'><input type='submit' name='ACTION' value='smbshareadd'></td></tr></form>
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
            else{$shareoption = qx(head -$Zeilenbegin $sharefile | tail -$Zeilenende);}
           }
         }
                 
        print <<END
        <hr>
        <table width='500px' cellspacing='0'><br>
        <tr bgcolor='${Header::table1colour}'><td colspan='2' align='left'><b>Share bearbeiten</b></td></tr>
        <tr><td colspan='2' align='center'></td></tr>
        <form method='post' action='$ENV{'SCRIPT_NAME'}'>
        <tr><td colspan='2' align='center'>Anzeige der Optionen fuer Shares<input type='hidden' name='ACTION' value='optioncaption2'>
                <input type='image' alt='Legende' src='/images/info.gif'></td></tr></form>
        <form method='post' action='$ENV{'SCRIPT_NAME'}'>
        <tr><td colspan='2' align='center'><textarea name="SHAREOPTION" cols="50" rows="15" Wrap="off">$shareoption</textarea></td></tr>
        </table>
        <table width='50px' cellspacing='0'><br>
        <tr><td align='center'>
                                <input type='hidden' name='NAME' value='$sharename'>
                                <input type='submit' name='ACTION' value='smbsharechange'></td></tr></form>
        </table>
END
;
}

if ($sambasettings{'ACTION'} eq 'optioncaption' || $sambasettings{'ACTION'} eq 'optioncaption2')
{
        print <<END
        <table width='500px' cellspacing='0'><br>
        <tr><td><b>Legende:</b></td></tr>
        <tr><td><u>Option</u></td><td><u>Bedeutung</u> / <u>Beispiel</u></td></tr>
        <tr><td>comment</td><td>Kommentar</td></tr>
        <tr><td></td><td>comment = Mein neues Share</td></tr>
        <tr><td><br></td><td></td></tr>
        <tr><td>path</td><td>Pfad zum Verzeichnis</td></tr>
        <tr><td></td><td>path = /share/neu</td></tr>
        <tr><td><br></td><td></td></tr>
        <tr><td>writeable</td><td>Verzeichnis schreibbar</td></tr>
        <tr><td></td><td>writeable = yes</td></tr>
        <tr><td><br></td><td></td></tr>
        <tr><td>browseable</td><td>sichtbar in Verzeichnisliste</td></tr>
        <tr><td></td><td>browsable = yes</td></tr>
        <tr><td><br></td><td></td></tr>
        <tr><td>user</td><td>Besitzer der Freigabe</td></tr>
        <tr><td></td><td>user = samba</td></tr>
        <tr><td><br></td><td></td></tr>
        <tr><td>valid users</td><td>Liste der Zugriffsberechtigten</td></tr>
        <tr><td></td><td>valid users = samba, user1</td></tr>
        <tr><td><br></td><td></td></tr>
        <tr><td>write list</td><td>Liste der Schreibberechtigten</td></tr>
        <tr><td></td><td>write list = samba</td></tr>
        <tr><td><br></td><td></td></tr>
        <tr><td>read list</td><td>Liste der nur Leseberechtigten</td></tr>
        <tr><td></td><td>read list = user1</td></tr>
        <tr><td><br></td><td></td></tr>
        <tr><td>admin users</td><td>Liste der Benutzer mit SuperUser Rechten</td></tr>
        <tr><td></td><td>admin users = user1</td></tr>
        <tr><td><br></td><td></td></tr>
        <tr><td>invalid users</td><td>Liste der Benutzer denen der Zugriff verweigert wird</td></tr>
        <tr><td></td><td>invalid users = user2</td></tr>
        <tr><td><br></td><td></td></tr>
        <tr><td>force user</td><td>Standartbenutzer fuer alle Dateien</td></tr>
        <tr><td></td><td>force user = samba</td></tr>
        <tr><td><br></td><td></td></tr>
        <tr><td>directory mask</td><td>UNIX Verzeichnisberchtigung beim Erzeugen</td></tr>
        <tr><td></td><td>directory mask = 0777</td></tr>
        <tr><td><br></td><td></td></tr>
        <tr><td>create mask</td><td>UNIX Dateiberchtigung beim Erzeugen</td></tr>
        <tr><td></td><td>create mask = 0777</td></tr>
        <tr><td><br></td><td></td></tr>
        <tr><td>guest ok</td><td>Annonymer Zugriff</td></tr>
        <tr><td></td><td>guest ok = yes</td></tr>
        </table>
END
;
}

&Header::closebox();
&Header::closebigbox();
&Header::closepage();

############################################################################################################################
############################################ Subfunktion für Sambadienste ##################################################

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
                                if (/^Name:\W+(.*)/) {
                                        $testcmd = $1; }
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