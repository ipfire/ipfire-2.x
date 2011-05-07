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

if (($ARGV[0] eq 'include') || ($ARGV[0] eq 'iso')) {
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
  system("tar -cvzf /var/ipfire/backup/$Jahr$Monat$Monatstag-$Stunden$Minuten.ipf --files-from='/tmp/include' --exclude-from='/var/ipfire/backup/exclude' --files-from='/var/ipfire/backup/include.user' --exclude-from='/var/ipfire/backup/exclude.user'");
  system("rm /tmp/include");
  if ($ARGV[0] eq 'iso') {
  	system("/usr/local/bin/backupiso $Jahr$Monat$Monatstag-$Stunden$Minuten &");
  }
}
elsif ($ARGV[0] eq 'exclude') {
  &createinclude;
  open(DATEI, ">/tmp/include") || die "Could not save temp include file";
  print DATEI @include;
  close(DATEI);
  system("tar -cvzf /var/ipfire/backup/$Jahr$Monat$Monatstag-$Stunden$Minuten.ipf --files-from='/tmp/include' --exclude-from='/var/ipfire/backup/exclude' --files-from='/var/ipfire/backup/include.user' --exclude-from='/var/ipfire/backup/exclude.user'");
  system("rm /tmp/include");
}
elsif ($ARGV[0] eq 'restore') {
  system("cd / && tar -xvz -p -f /tmp/restore.ipf");
}
elsif ($ARGV[0] eq 'restoreaddon') {
  if ( -e "/tmp/$ARGV[1]" ){system("mv /tmp/$ARGV[1] /var/ipfire/backup/addons/backup/$ARGV[1]");}
  system("cd / && tar -xvz -p -f /var/ipfire/backup/addons/backup/$ARGV[1]");
}
elsif ($ARGV[0] eq 'cli') {
  system("tar -cvzf /var/ipfire/backup/$Jahr$Monat$Monatstag-$Stunden$Minuten-$ARGV[1].ipf --files-from='$ARGV[2]' --exclude-from='$ARGV[3]'");
}
elsif ($ARGV[0] eq 'addonbackup') {
  system("tar -cvzf /var/ipfire/backup/addons/backup/$ARGV[1].ipf --files-from='/var/ipfire/backup/addons/includes/$ARGV[1]'");
}
elsif ($ARGV[0] =~ /ipf$/ ) {
  system("rm /var/ipfire/backup/$ARGV[0]");
}
elsif ($ARGV[0] =~ /iso$/ ) {
  system("rm /var/tmp/backupiso/$ARGV[0]");
}
elsif ($ARGV[0] eq '') {
 printf "No argument given, please use <include><exclude><cli>\n"
}
elsif ($ARGV[0] eq 'makedirs') {
 system("mkdir -p /var/ipfire/backup/addons");
 system("mkdir -p /var/ipfire/backup/addons/backup");
 system("mkdir -p /var/ipfire/backup/addons/includes");
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
