#!/usr/bin/perl

use MP3::Tag;
use MP3::Info;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my $filename = "";
my %songs = "";
my $debug = 0;

if ($ARGV[0] eq 'scan') {
my $command = "find ";
chomp $ARGV[1];
$command .= "\"$ARGV[1]\"";
if ($ARGV[2] eq 'off'){$command .= " -maxdepth 1";}
$command .= " -name *.mp3";
my @files = `$command`;

&getExistingSongs();

foreach (@files){
 $filename = $_;
 chomp($filename)
  &getSongInfo();
  }
open(DATEI, ">${General::swroot}/mpfire/db/songs.db") || die "Kann Datenbank nicht speichern";
print DATEI %songs;
close(DATEI);
}

if ($ARGV[0] eq 'getdb') {
  &getExistingSongs();
  print %songs;
  }

if ($ARGV[0] eq 'play') {
  if ($debug){print "Yes we are called and we will play $ARGV[1]\n";}
  system("/usr/bin/mpg123 -b 1024 --aggressive -q \"$ARGV[1]\" 2>/dev/null >/dev/null &");
  }
  
if ($ARGV[0] eq 'stop') {
  my $PID =  `ps -ef | grep mpg123 | grep playlist | head -1 | awk '{  print \$2 }'`;
  if ($debug){print "Stopping $PID\n";}
  system("kill -KILL $PID");
  }

if ($ARGV[0] eq 'volup') {
  if ($debug){print "Increasing Volume\n";}
  system("/usr/bin/amixer set Master $ARGV[1]%+ 2>/dev/null >/dev/null");
  }

if ($ARGV[0] eq 'voldown') {
  if ($debug){print "Decreasing Volume\n";}
  system("/usr/bin/amixer set Master $ARGV[1]%- 2>/dev/null >/dev/null");
  }

if ($ARGV[0] eq 'playall') {
  if ($debug){print "Playing everything\n";}
  system("/usr/bin/mpg123 -b 1024 --aggressive -Zq@ /var/ipfire/mpfire/playlist 2>/dev/null >/dev/null &"); 
  }
  
if ($ARGV[0] eq 'pause') {
  my $PID =  `ps -ef | grep mpg123 | grep playlist | head -1 | awk '{  print \$2 }'`;
  if ($debug){print "Pausing Process $PID\n";}
  system("kill -STOP $PID");
  }

if ($ARGV[0] eq 'resume') {
  my $PID =  `ps -ef | grep mpg123 | grep playlist | head -1 | awk '{  print \$2 }'`;
  if ($debug){print "Resuming Process $PID\n";}
  system("kill -CONT $PID");
  }
  
if ($ARGV[0] eq 'next') {
  if ($debug){print "Next Song\n";}
  my $PID =  `ps -ef | grep mpg123 | grep playlist | head -1 | awk '{  print \$2 }'`;
  system("kill -SIGINT $PID");
  }

sub getSongInfo(){
  my $mp3 = MP3::Tag->new($filename);
  my ($title, $track, $artist, $album, $comment, $year, $genre) = $mp3->autoinfo();
  my $info = get_mp3info($filename);
  $mp3->close();
  $songs{$filename} = "|".$artist."|".$title."|".$track."|".$album."|".$year."|".$genre."|".$info->{MM}."|".$info->{SS}."|".$info->{BITRATE}."|".$info->{FREQUENCY}."|".$info->{MODE}."\n";
  }

sub getExistingSongs(){
  open(DATEI, "<${General::swroot}/mpfire/db/songs.db") || die "Keine Datenbank vorhanden";
  my @Zeilen = <DATEI>;
  close(DATEI);
  foreach (@Zeilen){
    my @Zeile = split(/\|/,$_);
    $songs{$Zeile[0]} = "|".$Zeile[1]."|".$Zeile[2]."|".$Zeile[3]."|".$Zeile[4]."|".$Zeile[5]."|".$Zeile[6]."|".$Zeile[7]."|".$Zeile[8]."|".$Zeile[9]."|".$Zeile[10]."|".$Zeile[11]."\n";
    }
 }
