#!/usr/bin/perl

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my $filename = "";
my $debug = 0; 

if (  `/etc/init.d/mpd status` =~/not running/ ){
system("/etc/init.d/mpd start >/dev/null");
}

if ($ARGV[0] eq 'scan') {
  if ($debug){print "Creating Database\n";}
  system("mpd --create-db >/dev/null");
  system("/etc/init.d/mpd restart >/dev/null");
}
elsif ($ARGV[0] eq 'play') {
  &checkmute();
  &clearplaylist();
  if ($debug){print "Yes we are called and we will play $ARGV[1]\n";}
  system("mpc add \"$ARGV[1]\" >/dev/null && mpc play >/dev/null");
  }
elsif ($ARGV[0] eq 'playadd') {
  if ($debug){print "Yes we are called and we will add $ARGV[1]\n";}
  system("mpc add \"$ARGV[1]\" >/dev/null && mpc play >/dev/null");
  }
elsif ($ARGV[0] eq 'clearplaylist') {
  if ($debug){print "Deleting playlist\n";}
  &clearplaylist();
  }
elsif ($ARGV[0] eq 'stop') {
    my $PID = 'cat /var/run/mpd.pid';
    if ($debug){print "Killing Process $PID\n";}
    system("mpc stop >/dev/null");
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
elsif ($ARGV[0] eq 'toggle') {
  system("mpc toggle >/dev/null");
  }
elsif ($ARGV[0] eq 'next') {
  if ($debug){print "Next Song\n";}
  system("mpc next >/dev/null[");
  }
elsif ( $ARGV[0] eq 'prev' ) {
  if ($debug){print "Previous Song\n";}
  system("mpc prev >/dev/null");  
  }
elsif ($ARGV[0] eq 'song') {
  my $song = `mpc \| head -2 | grep -v volume`;
  print $song;
  }
elsif ($ARGV[0] eq 'stats') {
  my $song = `mpc stats | grep Songs`;
  print $song;
  }
elsif ($ARGV[0] eq 'playweb') {
  &checkmute();
  &clearplaylist();
  if ($debug){print "Playing webstream $ARGV[1] \n";}
     system("mpc add http://$ARGV[1] >/dev/null && mpc play >/dev/null && sleep 1");
  }
elsif ($ARGV[0] eq 'volume') {
 $temp = "Master - ";
 $temp .= `amixer get Master \| tail -2 \| awk '{ print \$2" "\$5 }'`;
 $temp .= "<break>PCM -";
 $temp .= `amixer get PCM \| tail -2 \| awk '{ print \$2" "\$5 }'`;
 print $temp;
}

sub clearplaylist(){
  system("mpc clear >/dev/null");  
  }

sub shuffle(){
  system("mpc random >/dev/null");  
  }

sub checkplaylist(){
 my $Datei = "/var/ipfire/mpd/playlist.m3u";
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
  system("amixer set PCM toggle >/dev/null");
  }
 if ( $Master[7] =~ /off/ ){
  if ($debug){print "Master was muted - umuting.\n";}
  system("amixer set Master toggle >/dev/null");
  } 
}
