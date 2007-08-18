#!/usr/bin/perl

use MP3::Tag;
use MP3::Info;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my $filename = "";
my %songs = "";
my $debug = 0;
my $temp;

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
elsif ($ARGV[0] eq 'play') {
  &checkplaylist();
  &checkmute();
  if ($debug){print "Yes we are called and we will play $ARGV[1]\n";}
  system("/usr/bin/mpg123 -b 1024 --aggressive -q \"$ARGV[1]\" 2>/dev/null >/dev/null &");
  }
elsif ($ARGV[0] eq 'stop') {
  my $PID = `ps -ef \| grep "wget -qO" \| head -1 \| grep -v "sh -c" \| awk '{  print \$2 }'`;
  if ( $PID ne '' ){
   if ($debug){print "Stopping $PID\n";}
   system("kill -KILL $PID");
   my $PID =  `ps -ef \| grep "mpg123 -b 1024 --aggressive -Zq -" \| head -1 \| grep -v "sh -c" \| awk '{  print \$2 }'`;
   if ($debug){print "Killing Process $PID\n";}
   system("kill -KILL $PID");
  }
  else{
   my $PID =  `ps -ef \| grep mpg123 \| grep playlist \| head -1 \| grep -v "sh -c" \| awk '{  print \$2 }'`;
   if ($debug){print "Stopping $PID\n";}
   system("kill -KILL $PID");
  }
  }
elsif ($ARGV[0] eq 'volup') {
  if ($debug){print "Increasing Volume\n";}
  system("/usr/bin/amixer set Master $ARGV[1]%+ 2>/dev/null >/dev/null");
  system("/usr/bin/amixer set PCM $ARGV[1]%+ 2>/dev/null >/dev/null");
  }
elsif ($ARGV[0] eq 'voldown') {
  if ($debug){print "Decreasing Volume\n";}
  system("/usr/bin/amixer set Master $ARGV[1]%- 2>/dev/null >/dev/null");
  system("/usr/bin/amixer set PCM $ARGV[1]%- 2>/dev/null >/dev/null");
  }
elsif ($ARGV[0] eq 'playall') {
  &checkplaylist();
  &checkmute();
  if ($debug){print "Playing everything\n";}
  system("/usr/bin/mpg123 -b 1024 --aggressive -Zq@ /var/ipfire/mpfire/playlist 2>/dev/null >/dev/null &"); 
  }
elsif ($ARGV[0] eq 'pause') {
  my $PID =  `ps -ef \| grep mpg123 \| grep playlist \| head -1 \| grep -v "sh -c" \| grep -v "grep" \| awk '{  print \$2 }'`;
  if ($debug){print "Pausing Process $PID\n";}
  system("kill -STOP $PID");
  }
elsif ($ARGV[0] eq 'resume') {
  my $PID =  `ps -ef \| grep mpg123 \| grep playlist \| head -1 \| grep -v "sh -c" \| grep -v "grep" \| awk '{  print \$2 }'`;
  if ($debug){print "Resuming Process $PID\n";}
  system("kill -CONT $PID");
  }
elsif ($ARGV[0] eq 'next') {
  if ($debug){print "Next Song\n";}
  my $PID =  `ps -ef | grep mpg123 | grep playlist | head -1 | awk '{  print \$2 }'`;
  system("kill -SIGINT $PID");
  }
elsif ($ARGV[0] eq 'song') {
  &checkmute();
  my $song = `lsof -nX \| grep mpg123 \| grep REG \| grep mem | grep mp3 \| grep -v "sh -c" \| grep -v "grep"`;
  my @song = split(/\//,$song);
  my $i = @song;
  if ( $i == 0 ){
  my $song = `ps -ef \| grep "wget -qO" \| grep -v "sh -c" \| grep -v "grep"`;
  my @song = split(/http\:\/\//,$song);
  my $temp = $song[1];
  my @song = split(/ /,$temp);
  print $song[0];
  }
  else { print $song[$i-1];}
  }
elsif ($ARGV[0] eq 'playweb') {
  &General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
  &checkmute();

			if ($proxysettings{'UPSTREAM_PROXY'}) {
			  if ($proxysettings{'UPSTREAM_USER'}) {
			    &checkm3uproxy();
			    if ($debug){print "Playing webstream\n";}
          system("wget -qO - `wget -qO - http://$proxysettings{'UPSTREAM_USER'}:$proxysettings{'UPSTREAM_PASSWORD'}@$proxysettings{'UPSTREAM_PROXY'}$ARGV[1]` | mpg123 -b 1024 --aggressive -Zq - 2>/dev/null >/dev/null &");
          }
          else {
          &checkm3uproxyuser();
          if ($debug){print "Playing webstream\n";}
          system("wget -qO - `wget -qO - http://$proxysettings{'UPSTREAM_PROXY'}$ARGV[1]` | mpg123 -b 1024 --aggressive -Zq - 2>/dev/null >/dev/null &");} 
			} else {
        &checkm3u();
        if ($debug){print "Playing webstream\n";}
        system("wget -qO - `wget -qO - http://$ARGV[1]` | mpg123 -b 1024 --aggressive -Zq - 2>/dev/null >/dev/null &");
			}
  }
elsif ($ARGV[0] eq 'volume') {
 $temp = "Master - ";
 $temp .= `amixer get Master \| tail -2 \| awk '{ print \$2" "\$5 }'`;
 $temp .= "<break>PCM -";
 $temp .= `amixer get PCM \| tail -2 \| awk '{ print \$2" "\$5 }'`;
 print $temp;
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
 
sub checkplaylist(){
 my $Datei = "/var/ipfire/mpfire/playlist";
 my @Info = stat($Datei);
 if ( $Info[7] eq '' || $Info[7] eq '0' ){print "There is no playlist";exit(1);}
}

sub checkmute(){
 $temp = `amixer get Master \| tail -2`;
  my @Master = split(/ /,$temp);
 $temp = `amixer get PCM \| tail -2`;
  my @PCM = split(/ /,$temp);
 if ( $PCM[7] =~  /off/ ){
  if ($debug){print "PCM was muted - umuting.\n";}
  system("amixer set PCM toggle");
  }
 if ( $Master[7] =~ /off/ ){
  if ($debug){print "Master was muted - umuting.\n";}
  system("amixer set Master toggle");
  } 
}

sub checkm3u(){
 my $Datei = system("wget -q --spider http://$ARGV[1]");
 if ( $Datei ne '0' ){print "We are unable to get the stream";exit(1);}
}

sub checkm3uproxy(){
 my $Datei = system("wget -q --spider http://$ARGV[1]");
 if ( $Datei ne '0' ){print "We are unable to get the stream";exit(1);}
}

sub checkm3uproxyuser(){
 my $Datei = system("wget -q --spider http://$ARGV[1]");
 if ( $Datei ne '0' ){print "We are unable to get the stream";exit(1);}
}
