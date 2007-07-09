#!/usr/bin/perl

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my $debug = 1;
my @include = "";
my ($Sekunden, $Minuten, $Stunden, $Monatstag, $Monat, $Jahr, $Wochentag, $Jahrestag, $Sommerzeit) = localtime(time);
$Jahr = $Jahr + 1900;$Monat = $Monat + 1;
$Monat = sprintf("%02d", $Monat);
$Monatstag = sprintf("%02d", $Monatstag);
$Stunden = sprintf("%02d", $Stunden);
$Minuten = sprintf("%02d", $Minuten);

if ($ARGV[0] eq 'include') {
  &createinclude;
  open(DATEI, ">/tmp/include") || die "Could not save temp include file";
  print DATEI @include;
  close(DATEI);
  system("tar -cvzf /var/ipfire/backup/$Jahr$Monat$Monatstag-$Stunden:$Minuten.ipf  --files-from=/tmp/include --exclude-from=/var/ipfire/backup/exclude");
  system("rm /tmp/include");
}

if ($ARGV[0] eq 'exclude') {
  &createinclude;
  open(DATEI, ">/tmp/include") || die "Could not save temp include file";
  print DATEI @include;
  close(DATEI);
  system("tar -cvzf /var/ipfire/backup/$Jahr$Monat$Monatstag-$Stunden:$Minuten.ipf --files-from='/tmp/include' --exclude-from='/var/ipfire/backup/exclude'");
  system("rm /tmp/include");
}

sub createinclude(){

  open(DATEI, "<${General::swroot}/backup/include") || die "Can not open include file";
  my @Zeilen = <DATEI>;
  close(DATEI);
  
  foreach (@Zeilen){
  if ( $_ =~ /\*/){
    my @files = `ls $_`;
    foreach (@files){
      push(@include,$_);
      }
    }
  else {push(@include,$_);}
  }
}
