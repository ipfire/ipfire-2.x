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
my %mpfiresettings = ();
my %checked = ();
my $message = "";
my $errormessage = "";

open(DATEI, "<${General::swroot}/mpfire/db/songs.db") || die "No Database found";
my @songdb = <DATEI>;
close(DATEI);
@songdb = sort(@songdb);

&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

&Header::showhttpheaders();

sub refreshpage{&Header::openbox( 'Waiting', 1, "<meta http-equiv='refresh' content='1;'>" );print "<center><img src='/images/clock.gif' alt='' /><br/><font color='red'>$Lang::tr{'pagerefresh'}</font></center>";&Header::closebox();}

&Header::getcgihash(\%mpfiresettings);
&Header::openpage($Lang::tr{'mpfire'}, 1, "<meta http-equiv='refresh' content='120'>");
&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
######################################## Scanne Verzeichnisse nach Mp3 Dateien #############################################

if ( $mpfiresettings{'ACTION'} eq "scan" )
{
delete $mpfiresettings{'__CGI__'};delete $mpfiresettings{'x'};delete $mpfiresettings{'y'};
&General::writehash("${General::swroot}/mpfire/settings", \%mpfiresettings);
system("/usr/local/bin/mpfirectrl scan $mpfiresettings{'SCANDIR'} $mpfiresettings{'SCANDIRDEPS'}");
refreshpage();
}

if ( $mpfiresettings{'ACTION'} eq ">" ){system("/usr/local/bin/mpfirectrl","play","\"$mpfiresettings{'FILE'}\"");}
if ( $mpfiresettings{'ACTION'} eq "x" ){system("/usr/local/bin/mpfirectrl stop");}
if ( $mpfiresettings{'ACTION'} eq "||" ){system("/usr/local/bin/mpfirectrl pause");}
if ( $mpfiresettings{'ACTION'} eq "|>" ){system("/usr/local/bin/mpfirectrl resume");}
if ( $mpfiresettings{'ACTION'} eq ">>" ){system("/usr/local/bin/mpfirectrl next");}
if ( $mpfiresettings{'ACTION'} eq "stopweb" ){system("/usr/local/bin/mpfirectrl stopweb");}
if ( $mpfiresettings{'ACTION'} eq "playweb" ){system("/usr/local/bin/mpfirectrl","playweb","\"$mpfiresettings{'FILE'}\"");}
if ( $mpfiresettings{'ACTION'} eq "+" ){system("/usr/local/bin/mpfirectrl volup 5");}
if ( $mpfiresettings{'ACTION'} eq "-" ){system("/usr/local/bin/mpfirectrl voldown 5");}
if ( $mpfiresettings{'ACTION'} eq "++" ){system("/usr/local/bin/mpfirectrl volup 10");}
if ( $mpfiresettings{'ACTION'} eq "--" ){system("/usr/local/bin/mpfirectrl voldown 10");}
if ( $mpfiresettings{'ACTION'} eq "playlist" ){system("/usr/local/bin/mpfirectrl playall");}
if ( $mpfiresettings{'ACTION'} eq "playalbum" )
{
my @temp = "";
my @album = split(/\|/,$mpfiresettings{'album'});
my %hash = map{ $_, 1 }@album;

foreach (@songdb){
  my @song = split(/\|/,$_);
  chomp($song[0]);
  push(@temp,$song[0]."\n") if exists $hash{$song[4]};
  }
open(DATEI, ">${General::swroot}/mpfire/playlist") || die "Could not add playlist";
print DATEI @temp;
close(DATEI);
system("/usr/local/bin/mpfirectrl playall");
}
if ( $mpfiresettings{'ACTION'} eq "playartist" )
{
my @temp = "";
my @artist = split(/\|/,$mpfiresettings{'artist'});
my %hash = map{ $_, 1 }@artist;

foreach (@songdb){
  my @song = split(/\|/,$_);
  chomp($song[0]);
    push(@temp,$song[0]."\n") if exists $hash{$song[1]};
  }
open(DATEI, ">${General::swroot}/mpfire/playlist") || die "Could not add playlist";
print DATEI @temp;
close(DATEI);
system("/usr/local/bin/mpfirectrl playall");
}
if ( $mpfiresettings{'ACTION'} eq "playall" )
{
my @temp = "";
foreach (@songdb){
  my @song = split(/\|/,$_);
  chomp($song[0]);
  push(@temp,$song[0]."\n");
  }
open(DATEI, ">${General::swroot}/mpfire/playlist") || die "Could not add playlist";
print DATEI @temp;
close(DATEI);
system("/usr/local/bin/mpfirectrl playall");
}
if ( $mpfiresettings{'SHOWLIST'} ){delete $mpfiresettings{'__CGI__'};delete $mpfiresettings{'x'};delete $mpfiresettings{'y'};&General::writehash("${General::swroot}/mpfire/settings", \%mpfiresettings);}

############################################################################################################################
################################### Aufbau der HTML Seite fr globale Sambaeinstellungen ####################################

$mpfiresettings{'SCANDIR'} = "/";
$mpfiresettings{'SHOWLIST'} = "off";

&General::readhash("${General::swroot}/mpfire/settings", \%mpfiresettings);

############################################################################################################################
########################################### rekursiv nach neuen Mp3s Scannen ##############################################ä

if ( $message ne "" )	{	print "<font color='red'>$message</font>"; }

&Header::openbox('100%', 'center', $Lang::tr{'mpfire scanning'});

print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='95%' cellspacing='0'>
<tr bgcolor='$color{'color20'}'><td colspan='2' align='left'><b>$Lang::tr{'Scan for Files'}</b></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'Scan from Directory'}</td><td align='left'><input type='text' name='SCANDIR' value='$mpfiresettings{'SCANDIR'}' size="30" /></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'deep scan directories'}</td><td align='left'>on <input type='radio' name='SCANDIRDEPS' value='on' checked='checked'/>/
																									                                          <input type='radio' name='SCANDIRDEPS' value='off'/> off</td></tr>
<tr><td align='center' colspan='2'><input type='hidden' name='ACTION' value='scan' />
                              <input type='image' alt='$Lang::tr{'Scan for Files'}' title='$Lang::tr{'Scan for Files'}' src='/images/edit-find.png' /></td></tr>																				
</table>
</form>
END
;
&Header::closebox();

my $song = qx(/usr/local/bin/mpfirectrl song);
if ( $song eq "" ){$song = "None";}

&Header::openbox('100%', 'center', $Lang::tr{'mpfire controls'});
print <<END

    <table width='95%' cellspacing='0'>
    <tr bgcolor='$color{'color20'}'>    <td colspan='5' align='center'><marquee behavior='alternate' scrollamount='1' scrolldelay='5'><font color=red>-= $song =-</font></marquee></td></tr>
    <tr><td colspan='5' align='center'><br/><b>total $#songdb songs</b><br/><br/></td></tr>
    <tr>
    <td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='x' /><input type='image' alt='$Lang::tr{'stop'}' title='$Lang::tr{'stop'}' src='/images/media-playback-stop.png' /></form></td>
    <td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='||' /><input type='image' alt='$Lang::tr{'pause'}' title='$Lang::tr{'pause'}' src='/images/media-playback-pause.png' /></form></td>
    <td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='|>' /><input type='image' alt='$Lang::tr{'resume'}' title='$Lang::tr{'resume'}' src='/images/media-resume.png' /></form></td>
    <td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='playall' /><input type='image' alt='$Lang::tr{'play'}' title='$Lang::tr{'play'}' src='/images/media-playback-start.png' /></form></td>
    <td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='>>' /><input type='image' alt='$Lang::tr{'next'}' title='$Lang::tr{'next'}' src='/images/media-skip-forward.png' /></form></td>
    </tr>
END
;
if ( $mpfiresettings{'SHOWLIST'} eq "on" ){print"<tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='SHOWLIST' value='off' /><input type='image' alt='$Lang::tr{'off'}' title='$Lang::tr{'off'}' src='/images/audio-x-generic.png' /></form></td>";}
else { print"<tr><td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='SHOWLIST' value='on' /><input type='image' alt='$Lang::tr{'on'}' title='$Lang::tr{'on'}' src='/images/audio-x-generic-red.png' /></form></td>";}    
print <<END  
    <td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='--' /><input type='image' alt='$Lang::tr{'voldown10'}' title='$Lang::tr{'voldown10'}' src='/images/audio-volume-low-red.png' /></form></td>
    <td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='-' /><input type='image' alt='$Lang::tr{'voldown5'}' title='$Lang::tr{'voldown5'}' src='/images/audio-volume-low.png' /></form></td>
    <td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='+' /><input type='image' alt='$Lang::tr{'volup5'}' title='$Lang::tr{'volup5'}' src='/images/audio-volume-high.png' /></form></td>
    <td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='++' /><input type='image' alt='$Lang::tr{'volup10'}' title='$Lang::tr{'volup10'}' src='/images/audio-volume-high-red.png' /></form></td>
    </tr>
</table>
END
;
&Header::closebox();

&Header::openbox('100%', 'center', $Lang::tr{'quick playlist'});

my @artist;
my @album;
foreach (@songdb){
  my @song = split(/\|/,$_);
  push(@artist,$song[1]);push(@album,$song[4]);}
  my %hash = map{ $_, 1 }@artist;
  @artist = sort keys %hash;
  my %hash = map{ $_, 1 }@album;
  @album = sort keys %hash;
print <<END
  <table width='95%' cellspacing='0'>
  <tr><td align='center' bgcolor='$color{'color20'}'><b>$Lang::tr{'artist'} - $#artist</b></td><td align='center' bgcolor='$color{'color20'}'><b>$Lang::tr{'album'} - $#album</b></td></tr>
  <tr><td align='center'>
      <form method='post' action='$ENV{'SCRIPT_NAME'}'>
      <select name='artist' size='8' multiple='multiple' style='width:300px;'>
END
;
  foreach (@artist){print "<option>$_</option>";}
print <<END
      </select><br/>
      <input type='hidden' name='ACTION' value='playartist' />
      <input type='image' alt='$Lang::tr{'play'}' title='$Lang::tr{'play'}' src='/images/media-playback-start.png' />
      </form></td>
      <td align='center'>
      <form method='post' action='$ENV{'SCRIPT_NAME'}'>
      <select name='album' size='8' multiple='multiple' style='width:300px;'>
END
;
  foreach (@album){print "<option>$_</option>";}
print <<END
      </select><br/>
      <input type='hidden' name='ACTION' value='playalbum' />
      <input type='image' alt='$Lang::tr{'play'}' title='$Lang::tr{'play'}' src='/images/media-playback-start.png' />
      </form></td>
      </tr></table>
END
;
&Header::closebox();

if ( $mpfiresettings{'SHOWLIST'} eq "on" ){

&Header::openbox('100%', 'center', $Lang::tr{'mpfire songs'});
print <<END

<table width='95%' cellspacing='5'>
<tr bgcolor='$color{'color20'}'><td colspan='9' align='left'><b>$Lang::tr{'Existing Files'}</b></td></tr>
<tr><td align='center'></td>
    <td align='center'><b>$Lang::tr{'artist'}<br/>$Lang::tr{'title'}</b></td>
    <td align='center'><b>$Lang::tr{'number'}</b></td>
    <td align='center'><b>$Lang::tr{'album'}</b></td>
    <td align='center'><b>$Lang::tr{'year'}</b></td>
    <td align='center'><b>$Lang::tr{'genre'}</b></td>
    <td align='center'><b>$Lang::tr{'length'}<br/>$Lang::tr{'bitrate'} - $Lang::tr{'frequency'}</b></td>
    <td align='center'><b>$Lang::tr{'mode'}</b></td></tr>
END
;
my $lines = 0;
foreach (@songdb){
  my @song = split(/\|/,$_);
  
  if ($lines % 2) {print "<tr bgcolor='$color{'color20'}'>";} else {print "<tr bgcolor='$color{'color22'}'>";}
  $song[0]=~s/\/\//\//g;   
  print <<END
  <td align='center' style="white-space:nowrap;"><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='>' /><input type='hidden' name='FILE' value="$song[0]" /><input type='image' alt='$Lang::tr{'play'}' title='$Lang::tr{'play'}' src='/images/media-playback-start.png' /></form></td>
  <td align='center'>$song[1]<br/>$song[2]</td>
  <td align='center'>$song[3]</td>
  <td align='center'>$song[4]</td>
  <td align='center'>$song[5]</td>
  <td align='center'>$song[6]</td>
  <td align='center'>$song[7]:$song[8]<br/>$song[9] - $song[10]</td>
END
;
    if ( $song[11] eq "0\n" ) {print "<td align='center'>Stereo</td></tr>"; }
    elsif ( $song[11] eq "1\n" ) {print "<td align='center'>Joint<br/>Stereo</td></tr>"; }
    elsif ( $song[11] eq "2\n" ) {print "<td align='center'>Dual<br/>Channel</td></tr>"; }
    elsif ( $song[11] eq "3\n" ) {print "<td align='center'>Single<br/>Channel</td></tr>"; }
    else {print "<td align='center'></td></tr>"; }
  $lines++
  }
print "</table></form>";
&Header::closebox();
}

&Header::openbox('100%', 'center', $Lang::tr{'mpfire playlist'});

open(DATEI, "<${General::swroot}/mpfire/playlist") || die "Could not open playlist";
my @playlist = <DATEI>;
close(DATEI);

print <<END
<table width='95%' cellspacing='0'>
<tr bgcolor='$color{'color20'}'><td colspan='9' align='left'><b>$Lang::tr{'current playlist'}</b></td></tr>
<tr><td align='center'><textarea cols='120' rows='10' name='playlist' style='font-size:10px' readonly='readonly' >@playlist</textarea><br/>
                       <form method='post' action='$ENV{'SCRIPT_NAME'}'>
                       <input type='hidden' name='ACTION' value='playlist' />
                       <input type='image' alt='$Lang::tr{'play'}' title='$Lang::tr{'play'}' src='/images/media-playback-start.png' />
      </form></td></tr>
</table>
END
;
&Header::closebox();

&Header::openbox('100%', 'center', $Lang::tr{'mpfire webradio'});

open(DATEI, "<${General::swroot}/mpfire/webradio") || die "Could not open playlist";
my @webradio = <DATEI>;
close(DATEI);

print <<END
<table width='95%' cellspacing='0'>
<tr bgcolor='$color{'color20'}'><td colspan='9' align='left'><b>$Lang::tr{'webradio playlist'}</b></td></tr>
<tr><td>Stream</td><td colspan='2'></td></tr>
END
;
foreach (@webradio){
 my @stream = split(/\|/,$_);
 print <<END
 <tr><td>$stream[1]</td>
     <td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='stopweb' /><input type='image' alt='$Lang::tr{'stop'}' title='$Lang::tr{'stop'}' src='/images/media-playback-stop.png' /></form></td>
     <td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='FILE' value='$stream[0]' /><input type='hidden' name='ACTION' value='playweb' /><input type='image' alt='$Lang::tr{'play'}' title='$Lang::tr{'play'}' src='/images/media-playback-start.png' /></form></td>
</tr>
END
;
 }
print "</table>";
&Header::closebox();

&Header::closebigbox();
&Header::closepage();
