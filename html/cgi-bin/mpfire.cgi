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

# use the special mpd POD and the encode POD to handle the utf8 scalars
use Audio::MPD;
use Encode;

# initiate the connector for the mpd POD, mpd must be running on locahost
# port 6600 without authentication
my $mpd = Audio::MPD->new('localhost',6600,'','$REUSE');
my $work = $mpd->status()->updating_db();

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %color = ();
my %mainsettings = ();
my %mpfiresettings = ();
my %checked = ();
my $message = '0';
my $errormessage = "";
my @songs;

&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/ipfire/include/colors.txt", \%color);

&Header::showhttpheaders();

if ( $ENV{'QUERY_STRING'} =~ /title/){

################################################################################
# $ENV{'QUERY_STRING'} =~ /title/ is used to handle the inline iframe used to
# display the current song playing ( artist - title - album aso )
# the cgi call´s itself with a parameter and the iframe refreshes itself without
# reloading the whole page
################################################################################

	my $number = $mpd->status()->song()+1;
	my $volume = $mpd->status()->volume();
	my $random = $mpd->status()->random();

	if ($random eq "0" ){
		$random="off";
	}else{
		$random="on";
	}

	my $repeat = $mpd->status()->repeat();
	if ($repeat eq "0" ){
		$repeat="off";
	}else{
		$repeat="on";
	}

	my $song = "";
	if ( $mpd->current() )
	{
		$song = substr("-= ".$mpd->current()->Artist()." | ".$mpd->current()->Title(),0,85)." =-<br /> ";
		if ( $song eq "-=  |  =-<br /> " ){
			$song = "None<br />"
		};
		$song .= $mpd->current()->Track()."# ".substr($mpd->current()->Album(),0,90)."<br />";
	}else{
		$song = "None<br /><br />";
	}

	if ( $song eq "None<br /># <br />" ){
		$song = "None<br />".substr($mpd->current()->file(),0,90)."<br />"
	};
	$song .= "Playlist: ".$number."-".$mpd->status()->playlistlength()." Time: ".$mpd->status()->time()->sofar."/";
	$song .= $mpd->status()->time()->total." (".$mpd->status()->time()->percent()."%) Status: ";
	$song .= $mpd->status()->state()." Volume: ".$volume." % Repeat: ".$repeat." Random: ".$random;

	print <<END
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<meta http-equiv='refresh' content='5'>
<title></title>
<body>
<table width='100%' cellspacing='0' align='center' style="background-image:url(/images/mpfire/box.png);background-repeat:no-repeat">
END
;
	print"<tr ><td align='center'><font color='red' face='Verdana' size='2'><br />".encode('utf-8', $song)."<br /><br /></font></td></tr></table></body>";
	exit;
}elsif ( $ENV{'QUERY_STRING'} =~ /control/){

################################################################################
# $ENV{'QUERY_STRING'} =~ /control/ is used to handle the inline iframe used to
# display the control button ( prev play skip stop toggle aso )
# the cgi call´s itself with a parameter and only the iframe is reloaded on click
################################################################################

	&Header::getcgihash(\%mpfiresettings);
	if ( $mpfiresettings{'ACTION'} eq "playall" ){
		$mpd->playlist->clear();
		foreach ($mpd->collection->all_pathes){
			$mpd->playlist->add($_);
		}
		$mpd->play();
	}elsif ($mpfiresettings{'ACTION'} eq "x" ){
		$mpd->stop();
	}elsif ( $mpfiresettings{'ACTION'} eq "|>" ){
		$mpd->pause();
	}elsif ( $mpfiresettings{'ACTION'} eq "<<" ){
		$mpd->prev();
	}elsif ( $mpfiresettings{'ACTION'} eq ">>" ){
		$mpd->next();
	}elsif ( $mpfiresettings{'ACTION'} eq "+" ){
		$mpd->volume('+5');
	}elsif ( $mpfiresettings{'ACTION'} eq "-" ){
		$mpd->volume('-5');
	}elsif ( $mpfiresettings{'ACTION'} eq "++" ){
		$mpd->volume('+10');
	}elsif ( $mpfiresettings{'ACTION'} eq "--" ){
		$mpd->volume('-10');
	}elsif ( $mpfiresettings{'ACTION'} eq ">" ){
		$mpd->play();
	}elsif ( $mpfiresettings{'ACTION'} eq "repeat" ){
		$mpd->repeat();
	}elsif ( $mpfiresettings{'ACTION'} eq "shuffle" ){
		$mpd->random();
	}
	print <<END
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<title></title>
<body>
<table width='95%' cellspacing='0'>
<tr>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}?control'><input type='hidden' name='ACTION' value='<<' /><input type='image' alt='$Lang::tr{'prev'}' title='$Lang::tr{'prev'}' src='/images/media-skip-backward.png' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}?control'><input type='hidden' name='ACTION' value='x' /><input type='image' alt='$Lang::tr{'stop'}' title='$Lang::tr{'stop'}' src='/images/media-playback-stop.png' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}?control'><input type='hidden' name='ACTION' value='|>' /><input type='image' alt='$Lang::tr{'toggle'}' title='$Lang::tr{'toggle'}' src='/images/media-resume.png' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}?control'><input type='hidden' name='ACTION' value='>' /><input type='image' alt='$Lang::tr{'play'}' title='$Lang::tr{'play'}' src='/images/media-playback-start.png' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}?control'><input type='hidden' name='ACTION' value='playall' /><input type='image' alt='$Lang::tr{'play'} all' title='$Lang::tr{'play'} all' src='/images/media-playback-start-all.png' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}?control'><input type='hidden' name='ACTION' value='>>' /><input type='image' alt='$Lang::tr{'next'}' title='$Lang::tr{'next'}' src='/images/media-skip-forward.png' /></form></td>
</tr>
END
;
	print <<END
<tr>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}?control'><input type='hidden' name='ACTION' value='repeat' /><input type='image' alt='$Lang::tr{'repeat'}' title='$Lang::tr{'repeat'}' src='/images/media-repeat.png' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}?control'><input type='hidden' name='ACTION' value='--' /><input type='image' alt='$Lang::tr{'voldown10'}' title='$Lang::tr{'voldown10'}' src='/images/audio-volume-low-red.png' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}?control'><input type='hidden' name='ACTION' value='-' /><input type='image' alt='$Lang::tr{'voldown5'}' title='$Lang::tr{'voldown5'}' src='/images/audio-volume-low.png' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}?control'><input type='hidden' name='ACTION' value='+' /><input type='image' alt='$Lang::tr{'volup5'}' title='$Lang::tr{'volup5'}' src='/images/audio-volume-high.png' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}?control'><input type='hidden' name='ACTION' value='++' /><input type='image' alt='$Lang::tr{'volup10'}' title='$Lang::tr{'volup10'}' src='/images/audio-volume-high-red.png' /></form></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}?control'><input type='hidden' name='ACTION' value='shuffle' /><input type='image' alt='$Lang::tr{'shuffle'}' title='$Lang::tr{'shuffle'}' src='/images/media-shuffle.png' /></form></td>
</tr>
</table>
</body>
END
;
	exit;
}

# just a little subpage to handle automatic page refresh on demand ( 1 sec )
sub refreshpage{
	&Header::openbox( 'Waiting', 1, "<meta http-equiv='refresh' content='1;' />" );
	print "<center><img src='/images/clock.gif' alt='' /><br/><font color='red'>$Lang::tr{'pagerefresh'}</font></center>";
	&Header::closebox();
}

# if the mpd is updating his database because of user interaction then the cgi
# should display that the mpd is unavailable, and refresh the status every 5 seconds
if ($work ne ""){
	&Header::openpage($Lang::tr{'mpfire'}, 1,);
	&Header::openbigbox('100%', 'left', '', $errormessage);
	&Header::openbox( 'Waiting', 5, "<meta http-equiv='refresh' content='5;' />" );
	print "<center><img src='/images/clock.gif' alt='' /><br/><font color='red'>Database is updating, please be patient.</font></center>";
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit;
}

if ( $mpfiresettings{'PAGE'} eq "" ){ $mpfiresettings{'PAGE'} = "1";};
if ( $mpfiresettings{'FRAME'} eq "" ){$mpfiresettings{'FRAME'} = "webradio";};

&Header::getcgihash(\%mpfiresettings);
&Header::openpage($Lang::tr{'mpfire'}, 1,);
&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
######################################## Scanne Verzeichnisse nach Mp3 Dateien #############################################

if ( $mpfiresettings{'ACTION'} eq "scan" ){

# on keypress scan the given directory and store the path to the mpd config
	&General::readhash("${General::swroot}/mpfire/settings", \%mpfiresettings);
	&Header::getcgihash(\%mpfiresettings);
	delete $mpfiresettings{'__CGI__'};delete $mpfiresettings{'x'};delete $mpfiresettings{'y'};
	delete $mpfiresettings{'PAGE'}; delete $mpfiresettings{'FRAME'};
	&General::writehash("${General::swroot}/mpfire/settings", \%mpfiresettings);

	open(DATEI, "<${General::swroot}/mpfire/mpd.conf") || die "Datei nicht gefunden";
	my @Zeilen = <DATEI>;
	close(DATEI);

	open(DATEI, ">${General::swroot}/mpfire/mpd.conf") || die "Datei nicht gefunden";
	foreach (@Zeilen){
		if ( $_ =~ /music_directory/){
			print DATEI "music_directory \"".$mpfiresettings{'MUSICDIR'}."\"\n";
		}else {
			print DATEI $_;
		}
	}
	close(DATEI);

	$mpd->updatedb();
	refreshpage();
}elsif ( $mpfiresettings{'ACTION'} eq "playweb" ){
	$message=system("/usr/local/bin/mpfirectrl","playweb","\"$mpfiresettings{'FILE'}\"","2>/dev/null");
}elsif ( $mpfiresettings{'ACTION'} eq "playlist" ){
	$mpd->play();
}elsif ( $mpfiresettings{'ACTION'} eq "emptyplaylist" ){
# on keypress clear the playlist
	$mpd->playlist->clear();
}elsif ( $mpfiresettings{'ACTION'} eq "addtoplaylist" ){
	$mpd->playlist->add($mpfiresettings{'FILE'});
}elsif ( $mpfiresettings{'ACTION'} eq "playalbum" ){
# on keypress play the selected albums
	my @select = split(/\|/,$mpfiresettings{'album'});
	$mpd->playlist->clear();
	foreach (@select){
		foreach ($mpd->collection->filenames_by_album($_)){
			if ( $_ ne "" ){
				$mpd->playlist->add($_);
			}
		}
	}
	$mpd->play();
}elsif ( $mpfiresettings{'ACTION'} eq "playartist" ){
# on keypress play the selected artist
	my @select = split(/\|/,$mpfiresettings{'artist'});
	$mpd->playlist->clear();
	foreach (@select){
		foreach ($mpd->collection->filenames_by_artist($_)){
			if ( $_ ne "" ){
				$mpd->playlist->add($_);
			}
		}
	}
	$mpd->play();
}elsif ( $mpfiresettings{'ACTION'} eq "playyear" ){
# on keypress play the selected year
	my @select = split(/\|/,$mpfiresettings{'year'});
	$mpd->playlist->clear();
	foreach (@select){
		foreach ($mpd->collection->filenames_by_year($_)){
			if ( $_ ne "" ){
				$mpd->playlist->add($_);
			}
		}
	}
	$mpd->play();
}elsif ( $mpfiresettings{'ACTION'} eq "playgenre" ){
# on keypress play the selected genre
	my @select = split(/\|/,$mpfiresettings{'genre'});
	$mpd->playlist->clear();
	foreach (@select){
		foreach ($mpd->collection->filenames_by_genre($_)){
			if ( $_ ne "" ){
				$mpd->playlist->add($_);
			}
		}
	}
	$mpd->play();
}elsif ( $mpfiresettings{'ACTION'} eq ">" ){
		$mpd->playlist->clear();
		$mpd->playlist->add($mpfiresettings{'FILE'});
		$mpd->play();
}

	if ( $mpfiresettings{'SEARCH'} eq "artist" && $mpfiresettings{'SEARCHITEM'} ne "" ){
		foreach ($mpd->collection->songs_with_artist_partial_filename($mpfiresettings{'SEARCHITEM'})){
			if ( $_ ne "" ){
				push(@songs,$_);
			}
		}
	}elsif ( $mpfiresettings{'SEARCH'} eq "title" && $mpfiresettings{'SEARCHITEM'} ne "" ){
		foreach ($mpd->collection->songs_with_title_partial_filename($mpfiresettings{'SEARCHITEM'})){
			if ( $_ ne "" ){
				push(@songs,$_);
			}
		}
	}elsif ( $mpfiresettings{'SEARCH'} eq "album" && $mpfiresettings{'SEARCHITEM'} ne "" ){
		foreach ($mpd->collection->songs_with_album_partial_filename($mpfiresettings{'SEARCHITEM'})){
			if ( $_ ne "" ){
				push(@songs,$_);
			}
		}
	}else{
	@songs = $mpd->collection->all_items_simple();
	shift(@songs);
	}

############################################################################################################################
################################### Aufbau der HTML Seite fr globale Sambaeinstellungen ####################################

$mpfiresettings{'MUSICDIR'} = "/var/mp3";
&General::readhash("${General::swroot}/mpfire/settings", \%mpfiresettings);

############################################################################################################################
########################################### rekursiv nach neuen Mp3s Scannen ##############################################ä

if ( $message ne '0' ){
	print "<font color='red'>An Error occured while launching the command</font>";
}elsif ( $message ne "" && $message ne '0' ){
	print "<font color='red'>$message</font>";
}

&Header::openbox('100%', 'center', $Lang::tr{'mpfire scanning'});
# box to enter the music directory and initiate the scan process
print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='95%' cellspacing='0'>
<tr bgcolor='$color{'color20'}'><td colspan='2' align='left'><b>$Lang::tr{'Scan for Files'}</b></td></tr>
<tr><td align='left' width='40%'>$Lang::tr{'Scan from Directory'}</td><td align='left'><input type='text' name='MUSICDIR' value='$mpfiresettings{'MUSICDIR'}' size="50" /></td></tr>
<tr><td align='center' colspan='2'><input type='hidden' name='ACTION' value='scan' /><input type='image' alt='$Lang::tr{'Scan for Files'}' title='$Lang::tr{'Scan for Files'}' src='/images/edit-find.png' /></td></tr>
</table>
</form>
END
;
&Header::closebox();

&Header::openbox('100%', 'center', $Lang::tr{'mpfire controls'});
# box for the two iframes showing the current playbar and the control buttons
print <<END
<iframe height='85' width='685' src='/cgi-bin/mpfire.cgi?title' scrolling='no' frameborder='no' marginheight='0'></iframe>
<iframe height='50' width='685' src='/cgi-bin/mpfire.cgi?control' scrolling='no' frameborder='no' marginheight='0'></iframe>
END
;
print "<b>Songs:".$mpd->stats()->songs()."</b><br />";

&Header::closebox();

&Header::openbox('100%', 'center', '');
print <<END
<tr><td align='center' colspan='4'>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
END
;
my @buttons=("webradio", "quick playlist","songs");
foreach (@buttons){
	if ( $mpfiresettings{'FRAME'} eq $_ ) {
		print "<input type='submit' name='FRAME' value='$_' disabled />";
	} else {
		print "<input type='submit' name='FRAME' value='$_' />";
	}
}

print <<END
</form></td></tr>
END
;
&Header::closebox();

if ( $mpfiresettings{'FRAME'} eq "quick playlist" )
{
&Header::openbox('100%', 'center', $Lang::tr{'quick playlist'});
# box to quickly select artist, album, year or genre and play the selection
print "<table width='95%' cellspacing='0'>";
print "<tr><td align='center' bgcolor='$color{'color20'}'><b>$Lang::tr{'artist'} - ".$mpd->stats()->artists()."</b></td><td align='center' bgcolor='$color{'color20'}'><b>$Lang::tr{'album'} - ".$mpd->stats()->albums()."</b></td></tr>";

print <<END
<tr><td align='center'>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<select name='artist' size='8' multiple='multiple' style='width:300px;'>
END
;

foreach (sort($mpd->collection->all_artists())){
	if ( $_ ne '' ){
		print "<option>".encode('utf-8', $_)."</option>\n";
	}
}

print <<END
</select><br/>
<input type='hidden' name='ACTION' value='playartist' />
<input type='image' alt='$Lang::tr{'play'}' title='$Lang::tr{'play'}' src='/images/media-playback-start.png' />
<input type='hidden' name='FRAME' value='$mpfiresettings{'FRAME'}' />
</form></td>
<td align='center'>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<select name='album' size='8' multiple='multiple' style='width:300px;'>
END
;

foreach (sort($mpd->collection->all_albums())){
	if ( $_ ne '' ){
		print "<option>".encode('utf-8', $_)."</option>\n";
	}
}

print <<END
</select><br/>
<input type='hidden' name='ACTION' value='playalbum' />
<input type='image' alt='$Lang::tr{'play'}' title='$Lang::tr{'play'}' src='/images/media-playback-start.png' />
<input type='hidden' name='FRAME' value='$mpfiresettings{'FRAME'}' />
</form></td>
</tr>
<tr><td align='center' bgcolor='$color{'color20'}'><b>$Lang::tr{'year'}</b></td><td align='center' bgcolor='$color{'color20'}'><b>$Lang::tr{'genre'}</b></td></tr>
<tr><td align='center'>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<select name='year' size='8' multiple='multiple' style='width:300px;'>
END
;

foreach (sort($mpd->collection->all_years())){
	if ( $_ ne '' ){
		print "<option>$_</option>\n";
	}
}

print <<END
</select><br/>
<input type='hidden' name='ACTION' value='playyear' />
<input type='image' alt='$Lang::tr{'play'}' title='$Lang::tr{'play'}' src='/images/media-playback-start.png' />
<input type='hidden' name='FRAME' value='$mpfiresettings{'FRAME'}' />
</form></td>
<td align='center'>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<select name='genre' size='8' multiple='multiple' style='width:300px;'>
END
;

foreach (sort($mpd->collection->all_genre())){
	if ( $_ ne '' ){
		print "<option>$_</option>\n";
	}
}

print <<END
</select><br/>
<input type='hidden' name='ACTION' value='playgenre' />
<input type='image' alt='$Lang::tr{'play'}' title='$Lang::tr{'play'}' src='/images/media-playback-start.png' />
<input type='hidden' name='FRAME' value='$mpfiresettings{'FRAME'}' />
</form></td>
</tr></table>
END
;

&Header::closebox();
}

if ( $mpfiresettings{'FRAME'} eq "songs" )
{
&Header::openbox('100%', 'center', $Lang::tr{'mpfire search'});
# box to quickly search artist, album or title
print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}#$Lang::tr{'mpfire songs'}'>
<table width='95%' cellspacing='0'>
<tr>
<td align='right' width='33%'>$Lang::tr{'artist'}</td>
<td align='center' width='33%'>$Lang::tr{'title'}</td>
<td align='left' width='33%'>$Lang::tr{'album'}</td>
</tr>
<tr>
<td align='right' width='33%'><input type='radio' name='SEARCH' value='artist' /></td>
<td align='center' width='33%'><input type='radio' name='SEARCH' value='title' checked='checked' /></td>
<td align='left' width='33%'><input type='radio' name='SEARCH' value='album' /></td>
</tr>
<tr>
<td align='center' colspan='3'><input type='text' name='SEARCHITEM' value='$mpfiresettings{'SEARCHITEM'}' size="50" /></td>
</tr>
<tr>
<td align='center' colspan='3'><input type='hidden' name='ACTION' value='search' /><input type='image' alt='$Lang::tr{'Scan for Songs'}' title='$Lang::tr{'Scan for Songs'}' src='/images/edit-find.png' /></td>
</tr>
</table>
<input type='hidden' name='FRAME' value='$mpfiresettings{'FRAME'}' />
</form>
END
;
&Header::closebox();

&Header::openbox('100%', 'center', $Lang::tr{'mpfire songs'});
print <<END
<a id='$Lang::tr{'mpfire songs'}' name='$Lang::tr{'mpfire songs'}'></a>
<table width='95%' cellspacing='3'>
<tr bgcolor='$color{'color20'}'><td colspan='4' align='left'><b>$Lang::tr{'Existing Files'}</b></td></tr>
END
;
if ( $#songs > 100 ){
	print "<tr><td align='center' colspan='4'><br/>$Lang::tr{'Pages'}<br/><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='submit' name='PAGE' value='all' /><br/>";
	my $pages =(int($#songs/100)+1);
	for(my $i = 1; $i <= $pages; $i++){
		print "<input type='submit' name='PAGE' value='$i' />";
		if (!($i % 205)){
			print"<br/>";
		}
	}
	print "<input type='hidden' name='FRAME' value='$mpfiresettings{'FRAME'}' />";
	print "</form></td></tr>";
}
print <<END
<tr><td align='center'></td>
<td align='center'><b>$Lang::tr{'artist'}<br/>$Lang::tr{'title'}</b></td>
<td align='center'><b>$Lang::tr{'number'}</b></td>
<td align='center'><b>$Lang::tr{'album'}</b></td>
END
;

my $lines=0;my $i=0;my $begin;my $end;
if ( $mpfiresettings{'PAGE'} eq 'all' ){
	$begin=0;
	$end=$#songs;
}else{
	$begin=(($mpfiresettings{'PAGE'}-1) * 100);
	$end=(($mpfiresettings{'PAGE'} * 100)-1);
}
	foreach (@songs){
	if (!($i >= $begin && $i <= $end)){
		#print $begin."->".$i."<-".$end."\n";
		$i++;next;
	}
	my @song = split(/\=/,$mpd->collection->song($_));
	@song = reverse @song;

	if ($lines % 2) {
		print "<tr bgcolor='$color{'color20'}'>";
	}else{
		print "<tr bgcolor='$color{'color22'}'>";
	}
	print <<END
<td align='center' style="white-space:nowrap;">
<form method='post' action='$ENV{'SCRIPT_NAME'}#$Lang::tr{'mpfire songs'}'>
<input type='hidden' name='ACTION' value='addtoplaylist' />
<input type='hidden' name='FILE' value="$_" />
<input type='hidden' name='PAGE' value='$mpfiresettings{'PAGE'}' />
<input type='hidden' name='FRAME' value='$mpfiresettings{'FRAME'}' />
<input type='hidden' name='SEARCH' value='$mpfiresettings{'SEARCH'}' />
<input type='hidden' name='SEARCHITEM' value='$mpfiresettings{'SEARCHITEM'}' />
<input type='image' alt='$Lang::tr{'add'}' title='$Lang::tr{'add'}' src='/images/list-add.png' />
</form>
<form method='post' action='$ENV{'SCRIPT_NAME'}#$Lang::tr{'mpfire songs'}'>
<input type='hidden' name='ACTION' value='>' />
<input type='hidden' name='FILE' value="$_" />
<input type='hidden' name='PAGE' value='$mpfiresettings{'PAGE'}' />
<input type='hidden' name='FRAME' value='$mpfiresettings{'FRAME'}' />
<input type='hidden' name='SEARCH' value='$mpfiresettings{'SEARCH'}' />
<input type='hidden' name='SEARCHITEM' value='$mpfiresettings{'SEARCHITEM'}' />
<input type='image' alt='$Lang::tr{'play'}' title='$Lang::tr{'play'}' src='/images/media-playback-start.png' />
</form>
</td>
END
;
	print "<td align='center'>".encode('utf-8', $song[0])."<br/>".encode('utf-8', $song[1])."</td>";
	print "<td align='center'>".encode('utf-8', $song[2])."</td>";
	print "<td align='center'>".encode('utf-8', $song[3])."</td>";
	$lines++;
	$i++;
}

print "</table>";
&Header::closebox();
}

if ( $mpfiresettings{'FRAME'} eq "webradio" )
{
&Header::openbox('100%', 'center', $Lang::tr{'mpfire webradio'});
# box to select some webradio´s to be played by one click
open(DATEI, "<${General::swroot}/mpfire/webradio") || die "Could not open playlist";
my @webradio = <DATEI>;
close(DATEI);

print <<END
<table width='95%' cellspacing='0'>
<tr bgcolor='$color{'color20'}'><td colspan='9' align='left'><b>$Lang::tr{'webradio playlist'}</b></td></tr>
<tr><td align='left'>Stream</td><td colspan='2'></td></tr>
END
;

my $lines=0;
foreach (@webradio){
	my @stream = split(/\|/,$_);
	$lines++;
	chomp($stream[2]);
	if ($lines % 2) {
		print "<tr bgcolor='$color{'color22'}'>";
	}else{
		print "<tr>";
	}
	chomp $stream[1];chomp $stream[2];
	print <<END
<td align='left'><a href='$stream[2]' target='_blank'>$stream[1]</a></td>
<td align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='FILE' value='$stream[0]' /><input type='hidden' name='ACTION' value='playweb' /><input type='image' alt='$Lang::tr{'play'}' title='$Lang::tr{'play'}' src='/images/media-playback-start.png' align='middle' />
<input type='hidden' name='FRAME' value='$mpfiresettings{'FRAME'}' />
</form></td>
</tr>
END
;
}

$lines++;
if ($lines % 2){
	print "<tr bgcolor='$color{'color22'}'>";
}else{
	print "<tr>";
}

print <<END
<td align='center' colspan='2'><form method='post' action='$ENV{'SCRIPT_NAME'}'><br />http://<input type=text name='FILE' value='www.meineradiourl:1234' size='75' />
<input type='hidden' name='ACTION' value='playweb' /><input type='image' alt='$Lang::tr{'play'}' title='$Lang::tr{'play'}' src='/images/media-playback-start.png' align='top' />
<input type='hidden' name='FRAME' value='$mpfiresettings{'FRAME'}' />
</form></td>
</tr>
END
;
print "</table>";
&Header::closebox();
}

&Header::openbox('100%', 'center', $Lang::tr{'mpfire playlist'});
# box to show the current playlist given from mpc system command
my @playlist = `mpc playlist 2>/dev/null`;

print <<END
<table width='95%' cellspacing='0'>
<tr bgcolor='$color{'color20'}'><td colspan='2' align='left'><b>$Lang::tr{'current playlist'}</b></td></tr>
<tr><td align='center' colspan='2' ><textarea cols='100' rows='10' name='playlist' style='font-size:11px;width:650px;' readonly='readonly'>
END
;

foreach (@playlist){
	$_=~s/&/&amp\;/g;;print $_;
}

print <<END
</textarea></td></tr><tr>
<td align='right'>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='ACTION' value='emptyplaylist' />
<input type='image' alt='$Lang::tr{'clear playlist'}' title='$Lang::tr{'clear playlist'}' src='/images/user-trash.png' />
<input type='hidden' name='FRAME' value='$mpfiresettings{'FRAME'}' />
</form>
</td>
<td align='left'>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='ACTION' value='playlist' />
<input type='image' alt='$Lang::tr{'play'}' title='$Lang::tr{'play'}' src='/images/media-playback-start.png' />
<input type='hidden' name='FRAME' value='$mpfiresettings{'FRAME'}' />
</form>
</td></tr>
</table>
END
;

&Header::closebox();
&Header::closebigbox();
&Header::closepage();
