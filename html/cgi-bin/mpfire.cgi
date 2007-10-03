#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007  Michael Tremer & Christian Schmidt                      #
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

my %color = ();
my %mainsettings = ();
my %mpfiresettings = ();
my %checked = ();
my $message = '0';
my $errormessage = "";

&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

&Header::showhttpheaders();

sub refreshpage{&Header::openbox( 'Waiting', 1, "<meta http-equiv='refresh' content='1;' />" );print "<center><img src='/images/clock.gif' alt='' /><br/><font color='red'>$Lang::tr{'pagerefresh'}</font></center>";&Header::closebox();}

$mpfiresettings{'PAGE'} = "1";

open(DATEI, "<${General::swroot}/mpfire/db/mpd.db") || die "No Database found";
my @songdb = <DATEI>;
close(DATEI);

my @artist; my @album;  my @genre;  my @year; my $linecount = 0; my %songs;
my $key;my $file;my $Time;my $Artist;my $Title;my $Album;my $Track;my $Date;my $Genre;
foreach (@songdb){
  
  if ( $_ =~ /mtime: / ){
   $songs{$key}="$file|$Time|$Artist|$Title|$Album|$Track|$Date|$Genre";
   push(@artist,$Artist);push(@album,$Album);push(@year,$Date);push(@genre,$Genre);
   $key="";$file="";$Time="";$Artist="";$Title="";$Album="";$Track="";$Date="";$Genre="";
   }
  elsif ( $_ =~ /key: / ){my @temp = split(/: /,$_);$key=$temp[1];}
  elsif ( $_ =~ /file: / ){my @temp = split(/: /,$_);$file=$temp[1];}
  elsif ( $_ =~ /Time: / ){my @temp = split(/: /,$_);$Time=$temp[1];}
  elsif ( $_ =~ /Artist: / ){my @temp = split(/: /,$_);$Artist=$temp[1];}
  elsif ( $_ =~ /Title: / ){my @temp = split(/: /,$_);$Title=$temp[1];}
  elsif ( $_ =~ /Album: / ){my @temp = split(/: /,$_);$Album=$temp[1];}
  elsif ( $_ =~ /Track: / ){my @temp = split(/: /,$_);$Track=$temp[1];}
  elsif ( $_ =~ /Date: / ){my @temp = split(/: /,$_);$Date=$temp[1];}
  elsif ( $_ =~ /Genre: / ){my @temp = split(/: /,$_);$Genre=$temp[1];}
  else {next;}
 }
 
  my %hash = map{ $_, 1 }@artist;
  @artist = sort keys %hash;
  my %hash = map{ $_, 1 }@album;
  @album = sort keys %hash;
   my %hash = map{ $_, 1 }@year;
  @year = sort keys %hash;
  my %hash = map{ $_, 1 }@genre;
  @genre = sort keys %hash;
  
  my $artistcount = $#artist+1;
  my $albumcount = $#album+1;
  my $yearcount = $#year+1;
  my $genrecount = $#genre+1;

&Header::getcgihash(\%mpfiresettings);
&Header::openpage($Lang::tr{'mpfire'}, 1, "<meta http-equiv='refresh' content='120' />");
&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
######################################## Scanne Verzeichnisse nach Mp3 Dateien #############################################

if ( $mpfiresettings{'ACTION'} eq "scan" )
{
delete $mpfiresettings{'__CGI__'};delete $mpfiresettings{'x'};delete $mpfiresettings{'y'};delete $mpfiresettings{'PAGE'};
&General::writehash("${General::swroot}/mpfire/settings", \%mpfiresettings);
open(DATEI, "<${General::swroot}/mpfire/mpd.conf") || die "Datei nicht gefunden";
my @Zeilen = <DATEI>;
close(DATEI);
open(DATEI, ">${General::swroot}/mpfire/mpd.conf") || die "Datei nicht gefunden";
foreach (@Zeilen){
if ( $_ =~ /music_directory/){print DATEI "music_directory \"".$mpfiresettings{'MUSICDIR'}."\"\n";}
else {print DATEI $_;}
}
close(DATEI);

$message=system("/usr/local/bin/mpfirectrl scan");
refreshpage();
}
elsif ( $mpfiresettings{'ACTION'} eq ">" ){$message=system("/usr/local/bin/mpfirectrl","play","\"$mpfiresettings{'FILE'}\"");}
elsif ( $mpfiresettings{'ACTION'} eq "x" ){$message=system("/usr/local/bin/mpfirectrl stop");}
elsif ( $mpfiresettings{'ACTION'} eq "|>" ){$message=system("/usr/local/bin/mpfirectrl toggle");}
elsif ( $mpfiresettings{'ACTION'} eq "<<" ){$message=system("/usr/local/bin/mpfirectrl prev");}
elsif ( $mpfiresettings{'ACTION'} eq ">>" ){$message=system("/usr/local/bin/mpfirectrl next");}
elsif ( $mpfiresettings{'ACTION'} eq "+" ){$message=system("/usr/local/bin/mpfirectrl volup 5");}
elsif ( $mpfiresettings{'ACTION'} eq "-" ){$message=system("/usr/local/bin/mpfirectrl voldown 5");}
elsif ( $mpfiresettings{'ACTION'} eq "++" ){$message=system("/usr/local/bin/mpfirectrl volup 10");}
elsif ( $mpfiresettings{'ACTION'} eq "--" ){$message=system("/usr/local/bin/mpfirectrl voldown 10");}
elsif ( $mpfiresettings{'ACTION'} eq "playweb" ){$message=system("/usr/local/bin/mpfirectrl","playweb","\"$mpfiresettings{'FILE'}\"");}
elsif ( $mpfiresettings{'ACTION'} eq "playlist" ){$message=system("/usr/local/bin/mpfirectrl playlist");}
elsif ( $mpfiresettings{'ACTION'} eq "emptyplaylist" ){$message=system("/usr/local/bin/mpfirectrl clearplaylist");}
elsif ( $mpfiresettings{'ACTION'} eq "addtoplaylist" ){$message=system("/usr/local/bin/mpfirectrl","playadd","\"$mpfiresettings{'FILE'}\"");}
elsif ( $mpfiresettings{'ACTION'} eq "playall" ){
my @temp = ""; my @song = "";

foreach (keys(%songs)){
  @song = split(/\|/,$songs{$_});push(@temp,$song[0])
  }
open(DATEI, ">${General::swroot}/mpfire/playlist.m3u") || die "Could not add playlist";
print DATEI @temp;
close(DATEI);  

$message=system("/usr/local/bin/mpfirectrl playlist");
}
elsif ( $mpfiresettings{'ACTION'} eq "playalbum" )
{
my @temp = ""; my @song = ""; my @select = split(/\|/,$mpfiresettings{'album'});

foreach (keys(%songs)){
  @song = split(/\|/,$songs{$_});$song[4] =~ s/\W/ /g;
    
  foreach (@select){
    $_ =~ s/\W/ /g;
    if ( $song[4] =~ /$_/ ){push(@temp,$song[0]);}
  }
}
 
open(DATEI, ">${General::swroot}/mpfire/playlist.m3u") || die "Could not add playlist";
print DATEI @temp;
close(DATEI);
$message=system("/usr/local/bin/mpfirectrl playlist");
}
elsif ( $mpfiresettings{'ACTION'} eq "playartist" )
{
my @temp = ""; my @song = ""; my @select = split(/\|/,$mpfiresettings{'artist'});

foreach (keys(%songs)){
  @song = split(/\|/,$songs{$_});$song[2] =~ s/\W/ /g;
    
  foreach (@select){
    $_ =~ s/\W/ /g;
    if ( $song[2] =~ /$_/ ){push(@temp,$song[0]);}
  }
}

open(DATEI, ">${General::swroot}/mpfire/playlist.m3u") || die "Could not add playlist";
print DATEI @temp;
close(DATEI);
$message=system("/usr/local/bin/mpfirectrl playlist");
}
elsif ( $mpfiresettings{'ACTION'} eq "playyear" )
{
my @temp = ""; my @song = ""; my @select = split(/\|/,$mpfiresettings{'year'});

foreach (keys(%songs)){
  @song = split(/\|/,$songs{$_});$song[6] =~ s/\W/ /g;
    
  foreach (@select){
    $_ =~ s/\W/ /g;
    if ( $song[6] =~ /$_/ ){push(@temp,$song[0]);}
  }
}

open(DATEI, ">${General::swroot}/mpfire/playlist.m3u") || die "Could not add playlist";
print DATEI @temp;
close(DATEI);
$message=system("/usr/local/bin/mpfirectrl playlist");
}
elsif ( $mpfiresettings{'ACTION'} eq "playgenre" )
{
my @temp = ""; my @song = ""; my @select = split(/\|/,$mpfiresettings{'genre'});

foreach (keys(%songs)){
  @song = split(/\|/,$songs{$_});$song[7] =~ s/\W/ /g;
    
  foreach (@select){
    $_ =~ s/\W/ /g;
    if ( $song[7] =~ /$_/ ){push(@temp,$song[0]);}
  }
}

open(DATEI, ">${General::swroot}/mpfire/playlist.m3u") || die "Could not add playlist";
print DATEI @temp;
close(DATEI);
$message=system("/usr/local/bin/mpfirectrl playlist");
}
elsif ( $mpfiresettings{'SHOWLIST'} ){delete $mpfiresettings{'__CGI__'};delete $mpfiresettings{'x'};delete $mpfiresettings{'y'};delete $mpfiresettings{'PAGE'};&General::writehash("${General::swroot}/mpfire/settings", \%mpfiresettings);refreshpage();}

############################################################################################################################
################################### Aufbau der HTML Seite fr globale Sambaeinstellungen ####################################

$mpfiresettings{'MUSICDIR'} = "/";

&General::readhash("${General::swroot}/mpfire/settings", \%mpfiresettings);

############################################################################################################################
########################################### rekursiv nach neuen Mp3s Scannen ##############################################ä

if ( $message ne '0' )	{	print "<font color='red'>An Error occured while launching the command</font>"; }
elsif ( $message ne "" && $message ne '0' )	{	print "<font color='red'>$message</font>"; }

&Header::openbox('100%', 'center', $Lang::tr{'mpfire scanning'});

print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='95%' cellspacing='0'>
<tr bgcolor='$color{'color20'}'><td colspan='2' align='left'><b>$Lang::tr{'Scan for Files'}</b></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'Scan from Directory'}</td><td align='left'><input type='text' name='MUSICDIR' value='$mpfiresettings{'MUSICDIR'}' size="50" /></td></tr>
<tr><td align='center' colspan='2'><input type='hidden' name='ACTION' value='scan' />
                              <input type='image' alt='$Lang::tr{'Scan for Files'}' title='$Lang::tr{'Scan for Files'}' src='/images/edit-find.png' /></td></tr>																				
</table>
</form>
END
;
&Header::closebox();

my $song = qx(/usr/local/bin/mpfirectrl song);
if ( $song eq "" ){$song = "None";}
if ( length($song) > 125 ) {$song = substr($song,0,125)."...";}

my $Volume = `/usr/local/bin/mpfirectrl volume`;
$Volume=~s/<break>/<br \/>/g;
my $stats = `mpc stats | tail -4`;
$stats=~s/\\/<br \/>/g

&Header::openbox('100%', 'center', $Lang::tr{'mpfire controls'});
print <<END

    <table width='95%' cellspacing='0'>
    <tr bgcolor='$color{'color20'}'>    <td colspan='5' align='center'><marquee behavior='alternate' scrollamount='1' scrolldelay='5'><font color=red>-= $song =-</font></marquee></td></tr>
END
;
my $countsongs=`/usr/local/bin/mpfirectrl stats`;
print "<tr><td colspan='5' align='center'><br/><b>".$countsongs."</b><br/><br/></td></tr>";
print <<END
    <tr>
    <td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='x' /><input type='image' alt='$Lang::tr{'stop'}' title='$Lang::tr{'stop'}' src='/images/media-playback-stop.png' /></form></td>
    <td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='<<' /><input type='image' alt='$Lang::tr{'prev'}' title='$Lang::tr{'prev'}' src='/images/media-skip-backward.png' /></form></td>
    <td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='|>' /><input type='image' alt='$Lang::tr{'toggle'}' title='$Lang::tr{'toggle'}' src='/images/media-resume.png' /></form></td>
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
<tr><td colspan='5' align='center'>$Volume</td></tr>
<tr><td colspan='5' align='center'><br />$stats</td></tr>
</table>
END
;
&Header::closebox();

&Header::openbox('100%', 'center', $Lang::tr{'quick playlist'});

print "<table width='95%' cellspacing='0'>";
if ( $#songdb eq '-1' ) {print "<tr><td align='center' bgcolor='$color{'color20'}'><b>$Lang::tr{'artist'}</b></td><td align='center' bgcolor='$color{'color20'}'><b>$Lang::tr{'album'}</b></td></tr>";}
else {print "<tr><td align='center' bgcolor='$color{'color20'}'><b>$Lang::tr{'artist'} - ".$artistcount."</b></td><td align='center' bgcolor='$color{'color20'}'><b>$Lang::tr{'album'} - ".$albumcount."</b></td></tr>";}
print <<END
  <tr><td align='center'>
      <form method='post' action='$ENV{'SCRIPT_NAME'}'>
      <select name='artist' size='8' multiple='multiple' style='width:300px;'>
END
;
foreach (@artist){if ( $_ ne '' ){print "<option>$_</option>";}}
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
  foreach (@album){if ( $_ ne '' ){print "<option>$_</option>";}}
print <<END
      </select><br/>
      <input type='hidden' name='ACTION' value='playalbum' />
      <input type='image' alt='$Lang::tr{'play'}' title='$Lang::tr{'play'}' src='/images/media-playback-start.png' />
      </form></td>
      </tr>
END
;
if ( $#songdb eq '-1' ) {print "<tr><td align='center' bgcolor='$color{'color20'}'><b>$Lang::tr{'year'}</b></td><td align='center' bgcolor='$color{'color20'}'><b>$Lang::tr{'genre'}</b></td></tr>";}
else {print "<tr><td align='center' bgcolor='$color{'color20'}'><b>$Lang::tr{'year'} - ".$yearcount."</b></td><td align='center' bgcolor='$color{'color20'}'><b>$Lang::tr{'genre'} - ".$genrecount."</b></td></tr>";}
print <<END
  <tr><td align='center'>
      <form method='post' action='$ENV{'SCRIPT_NAME'}'>
      <select name='year' size='8' multiple='multiple' style='width:300px;'>
END
;
  foreach (@year){if ( $_ ne '' ){print "<option>$_</option>";}}
print <<END
      </select><br/>
      <input type='hidden' name='ACTION' value='playyear' />
      <input type='image' alt='$Lang::tr{'play'}' title='$Lang::tr{'play'}' src='/images/media-playback-start.png' />
      </form></td>
      <td align='center'>
      <form method='post' action='$ENV{'SCRIPT_NAME'}'>
      <select name='genre' size='8' multiple='multiple' style='width:300px;'>
END
;
  foreach (@genre){if ( $_ ne '' ){print "<option>$_</option>";}}
print <<END
      </select><br/>
      <input type='hidden' name='ACTION' value='playgenre' />
      <input type='image' alt='$Lang::tr{'play'}' title='$Lang::tr{'play'}' src='/images/media-playback-start.png' />
      </form></td>
      </tr></table>
END
;
&Header::closebox();

if ( $mpfiresettings{'SHOWLIST'} eq "on" ){

&Header::openbox('100%', 'center', $Lang::tr{'mpfire songs'});
print <<END
<a name="$Lang::tr{'mpfire songs'}"</a>
<table width='95%' cellspacing='5'>
<tr bgcolor='$color{'color20'}'><td colspan='9' align='left'><b>$Lang::tr{'Existing Files'}</b></td></tr>
<tr><td align='center' colspan='9'><br/>$Lang::tr{'Pages'}<br/><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='submit' name='PAGE' value='all' /><br/>
END
;
my $pages =(int(keys(%songs)/100)+1);
for(my $i = 1; $i <= $pages; $i++) {
print "<input type='submit' name='PAGE' value='$i' />";
if (!($i % 205)){print"<br/>";}
}
print <<END
</form></td></tr>
<tr><td align='center'></td>
    <td align='center'><b>$Lang::tr{'artist'}<br/>$Lang::tr{'title'}</b></td>
    <td align='center'><b>$Lang::tr{'number'}</b></td>
    <td align='center'><b>$Lang::tr{'album'}</b></td>
    <td align='center'><b>$Lang::tr{'year'}</b></td>
    <td align='center'><b>$Lang::tr{'genre'}</b></td>
    <td align='center'><b>$Lang::tr{'length'}</b></td></tr>
END
;
my $lines=0;my $i=0;my $begin;my $end;
if ( $mpfiresettings{'PAGE'} eq 'all' ){
  $begin=0;
  $end=keys(%songs);
}
else{
  $begin=(($mpfiresettings{'PAGE'}-1) * 100);
  $end=(($mpfiresettings{'PAGE'} * 100)-1);
}
foreach (keys(%songs)){
  if (!($i >= $begin && $i <= $end)){
# print $begin."->".$i."<-".$end."\n";
  $i++;next;}
  my @song = split(/\|/,$songs{$_});
  my $minutes = sprintf ("%.0f", $song[1] / 60 );
  my $seconds = $song[1] % 60;
  
  if ($lines % 2) {print "<tr bgcolor='$color{'color20'}'>";} else {print "<tr bgcolor='$color{'color22'}'>";}
  print <<END
  <td align='center' style="white-space:nowrap;"><form method='post' action='$ENV{'SCRIPT_NAME'}#$Lang::tr{'mpfire songs'}'><input type='hidden' name='ACTION' value='addtoplaylist' /><input type='hidden' name='FILE' value="$song[0]" /><input type='image' alt='$Lang::tr{'add'}' title='$Lang::tr{'add'}' src='/images/list-add.png' /></form><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='>' /><input type='hidden' name='FILE' value="$song[0]" /><input type='image' alt='$Lang::tr{'play'}' title='$Lang::tr{'play'}' src='/images/media-playback-start.png' /></form></td>
  <td align='center'>$song[2]<br/>$song[3]</td>
  <td align='center'>$song[5]</td>
  <td align='center'>$song[4]</td>
  <td align='center'>$song[6]</td>
  <td align='center'>$song[7]</td>
  <td align='center'>$minutes:$seconds</td></tr>
END
;
  $lines++;
  $i++;
  }
print "</table>";
&Header::closebox();
}

&Header::openbox('100%', 'center', $Lang::tr{'mpfire playlist'});

my @playlist = `mpc playlist`;

print <<END
<table width='95%' cellspacing='0'>
<tr bgcolor='$color{'color20'}'><td colspan='2' align='left'><b>$Lang::tr{'current playlist'}</b></td></tr>
<tr><td align='center' colspan='2' ><textarea cols='100' rows='10' name='playlist' style='font-size:11px;width:650px;' readonly='readonly'>
END
;
foreach (@playlist){print $_;}
print <<END
</textarea></td></tr><tr>
<td align='right'>
      <form method='post' action='$ENV{'SCRIPT_NAME'}'>
      <input type='hidden' name='ACTION' value='emptyplaylist' />
      <input type='image' alt='$Lang::tr{'clear playlist'}' title='$Lang::tr{'clear playlist'}' src='/images/user-trash.png' />
      </form>
</td>
<td align='left'>
      <form method='post' action='$ENV{'SCRIPT_NAME'}'>
      <input type='hidden' name='ACTION' value='playlist' />
      <input type='image' alt='$Lang::tr{'play'}' title='$Lang::tr{'play'}' src='/images/media-playback-start.png' />
      </form>
      </td></tr>
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
 <tr><td><a href="$stream[2]" target="_blank">$stream[1]</a></td>
     <td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='FILE' value='$stream[0]' /><input type='hidden' name='ACTION' value='playweb' /><input type='image' alt='$Lang::tr{'play'}' title='$Lang::tr{'play'}' src='/images/media-playback-start.png' /></form></td>
</tr>
END
;
 }
print "</table>";
&Header::closebox();

&Header::closebigbox();
&Header::closepage();
