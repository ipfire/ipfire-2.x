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
    my @files = `find / -name *.log* 2>/dev/null`;
    foreach (@files){
      push(@include,$_);
     }
    my @files = `find /var/log/ -name *messages* 2>/dev/null`;
    foreach (@files){
      push(@include,$_);
     }
  open(DATEI, ">/tmp/include") || die "Could not save temp include file";
  print DATEI @include;
  print "/var/log/messages";
  close(DATEI);
  system("tar -cvzf /var/ipfire/backup/$Jahr$Monat$Monatstag-$Stunden:$Minuten.ipf --files-from='/tmp/include' --exclude-from='/var/ipfire/backup/exclude'");
  system("rm /tmp/include");
}
elsif ($ARGV[0] eq 'exclude') {
  &createinclude;
  open(DATEI, ">/tmp/include") || die "Could not save temp include file";
  print DATEI @include;
  close(DATEI);
  system("tar -cvzf /var/ipfire/backup/$Jahr$Monat$Monatstag-$Stunden:$Minuten.ipf --files-from='/tmp/include' --exclude-from='/var/ipfire/backup/exclude'");
  system("rm /tmp/include");
}
elsif ($ARGV[0] eq 'restore') {
  system("tar -xvz --preserve -f /tmp/restore.ipf");
}
elsif ($ARGV[0] eq 'cli') {
  system("tar -cvzf /var/ipfire/backup/$Jahr$Monat$Monatstag-$Stunden:$Minuten-$ARGV[1].ipf --files-from='$ARGV[2]' --exclude-from='$ARGV[3]'");
}
elsif ($ARGV[0] =~ /ipf$/ ) {
  system("rm /var/ipfire/backup/$ARGV[0]");
}
elsif ($ARGV[0] eq '') {
 printf "No argument given, please use <include><exclude><cli>\n"
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
