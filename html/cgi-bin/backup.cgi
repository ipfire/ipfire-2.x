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

my %color = ();
my %mainsettings = ();
my %backupsettings = ();
my %checked = ();
my $message = "";
my $errormessage = "";
my @backups = `cd /var/ipfire/backup/ && ls *.ipf`;


&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

&Header::showhttpheaders();
&Header::getcgihash(\%backupsettings);

&Header::openpage($Lang::tr{'backup'}, 1, "");
&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
######################################## Scanne Verzeichnisse nach Mp3 Dateien #############################################

if ( $backupsettings{'ACTION'} eq "backup" )
{
 if ( $backupsettings{'BACKUPLOGS'} eq "include" ){system("/usr/local/bin/backupctrl include");}
 else {system("/usr/local/bin/backupctrl exclude");}
}

############################################################################################################################
########################################### rekursiv nach neuen Mp3s Scannen ##############################################ä

if ( $message ne "" )	{	print "<font color='red'>$message</font>"; }

&Header::openbox('100%', 'center', $Lang::tr{'backup'});

print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='95%' cellspacing='0'>
<tr><td align='left' width='40%'>$Lang::tr{'logs'}</td><td align='left'>include Logfiles <input type='radio' name='BACKUPLOGS' value='include' checked='checked'/>/
																									                                       <input type='radio' name='BACKUPLOGS' value='exclude'/> exclude Logfiles</td></tr>
<tr><td align='center' colspan='2'><input type='hidden' name='ACTION' value='backup' />
                              <input type='image' alt='$Lang::tr{'Scan for Files'}' title='$Lang::tr{'Scan for Files'}' src='/images/edit-find.png' /></td></tr>																				
</table>
</form>
END
;
&Header::closebox();

&Header::openbox('100%', 'center', $Lang::tr{'backups'});

print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='95%' cellspacing='0'>
END
;
foreach (@backups){
print "<tr><td align='left' width='40%'>$Lang::tr{'backup from'}</td><td align='left'>$_</td></tr>";
}
print <<END													
</table>
</form>
END
;
&Header::closebox();
&Header::closebigbox();
&Header::closepage();
