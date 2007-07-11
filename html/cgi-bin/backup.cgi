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
use File::Copy;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %color = ();
my %mainsettings = ();
my %cgiparams=();
my %checked = ();
my $message = "";
my $errormessage = "";
my @backups = `cd /srv/web/ipfire/html/backup && ls *.ipf`;

$a = new CGI;

&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

$cgiparams{'ACTION'} = '';
$cgiparams{'FILE'} = '';
$cgiparams{'UPLOAD'} = '';
$cgiparams{'BACKUPLOGS'} = '';
&Header::getcgihash(\%cgiparams);

############################################################################################################################
######################################## Scanne Verzeichnisse nach Mp3 Dateien #############################################

if ( $cgiparams{'ACTION'} eq "backup" )
{
 if ( $cgiparams{'BACKUPLOGS'} eq "include" ){system("/usr/local/bin/backupctrl include");}
 else {system("/usr/local/bin/backupctrl exclude");}
}
elsif ( $cgiparams{'ACTION'} eq "download" )
{
    open(DLFILE, "</srv/web/ipfire/html/backup/$cgiparams{'FILE'}") or die "Unable to open $cgiparams{'FILE'}: $!";
    my @fileholder = <DLFILE>;
    print "Content-Type:application/x-download\n";
    print "Content-Disposition:attachment;filename=$cgiparams{'FILE'}\n\n";
    print @fileholder;
    exit (0);
}
elsif ( $cgiparams{'ACTION'} eq "restore" )
{
  my $upload = $a->param("UPLOAD");
  open UPLOADFILE, ">/tmp/restore.ipf";
  binmode $upload;
  while ( <$upload> ) {
  print UPLOADFILE;
  }
  close UPLOADFILE;
  system("/usr/local/bin/backupctrl restore");
}

############################################################################################################################
########################################### rekursiv nach neuen Mp3s Scannen ##############################################ä

&Header::showhttpheaders();
&Header::openpage($Lang::tr{'backup'}, 1, "");
&Header::openbigbox('100%', 'left', '', $errormessage);

if ( $message ne "" ){
	&Header::openbox('100%','left',$Lang::tr{'error messages'});
	print "<font color='red'>$message</font>\n";
	&Header::closebox();
}

&Header::openbox('100%', 'center', $Lang::tr{'backup'});

print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='95%' cellspacing='0'>
<tr><td align='left' width='40%'>$Lang::tr{'logs'}</td><td align='left'>include Logfiles <input type='radio' name='BACKUPLOGS' value='include'/>/
																									                                       <input type='radio' name='BACKUPLOGS' value='exclude' checked='checked'/> exclude Logfiles</td></tr>
<tr><td align='center' colspan='2'><input type='hidden' name='ACTION' value='backup' />
                              <input type='image' alt='$Lang::tr{'Scan for Files'}' title='$Lang::tr{'Scan for Files'}' src='/images/document-save.png' /></td></tr>
</table>
</form>
END
;
&Header::closebox();

&Header::openbox('100%', 'center', $Lang::tr{'backups'});

print <<END
<table width='95%' cellspacing='0'>
END
;
foreach (@backups){
chomp($_);
my $Datei = "/srv/web/ipfire/html/backup/".$_;
my @Info = stat($Datei);
my $Size = $Info[7] / 1024;
$Size = sprintf("%02d", $Size);
print "<tr><td align='left'><form method='post' action='$ENV{'SCRIPT_NAME'}'>$Lang::tr{'backup from'} $_ $Lang::tr{'size'} $Size KB <input type='hidden' name='ACTION' value='download' /><input type='hidden' name='FILE' value='$_' /><input type='image' src='/images/package-x-generic.png' /></form></td></tr>";
}
print <<END													
</table>
END
;
&Header::closebox();

&Header::openbox('100%', 'center', $Lang::tr{'restore'});

print <<END
<table width='95%' cellspacing='0'>
<tr><td align='left'><form method='post' enctype='multipart/form-data' action='$ENV{'SCRIPT_NAME'}'>$Lang::tr{'backup'}</td><td align='left'><input type="file" size='50' name="UPLOAD" /><input type='submit' name='ACTION' value='restore' /></form></td></tr>
</table>
END
;
&Header::closebox();
&Header::closebigbox();
&Header::closepage();
