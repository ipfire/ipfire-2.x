#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2022  IPFire Team  <info@ipfire.org>                     #
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

package CONNSCHED;

$CONNSCHED::maxprofiles = 5;

@CONNSCHED::weekdays = ( 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun' );
@CONNSCHED::weekdays_pr = ( 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday' );

%CONNSCHED::config;
$CONNSCHED::configfile = "/var/ipfire/connscheduler/connscheduler.conf";
&ReadConfig;


1;

#
# load the configuration file
#
sub ReadConfig
{
  # datafileformat:
  # active,action,profilenr,time,daystype,days,weekdays,,comment

  @CONNSCHED::config = ();

  my @tmpfile = ();
  if ( open(FILE, "$configfile") )
  {
    @tmpfile = <FILE>;
    close (FILE);
  }

  foreach $line ( @tmpfile )
  {
    chomp($line);               # remove newline
    my @temp = split(/\,/,$line,9);
    if ( ($temp[0] ne 'on') &&  ($temp[0] ne 'off') ) { next; }

    my $weekdays_pr = '';
    for (my $i = 0; $i < 7; $i++)
    {
      if ( index($temp[6], $CONNSCHED::weekdays[$i]) != -1 )
      {
        $weekdays_pr .= "$Lang::tr{$CONNSCHED::weekdays_pr[$i]} ";
      }
    }

    push @CONNSCHED::config, { ACTIVE => $temp[0], ACTION => $temp[1], PROFILENR => $temp[2], TIME => $temp[3], 
      DAYSTYPE => $temp[4], DAYS => $temp[5], WEEKDAYS => $temp[6], WEEKDAYS_PR => $weekdays_pr, COMMENT => $temp[8] };
  }
}

#
# write the configuration file
#
sub WriteConfig
{
  open(FILE, ">$configfile") or die 'hosts datafile error';

  for my $i ( 0 .. $#CONNSCHED::config )
  {
    if ( ($CONNSCHED::config[$i]{'ACTIVE'} ne 'on') && ($CONNSCHED::config[$i]{'ACTIVE'} ne 'off') ) { next; }

    print FILE "$CONNSCHED::config[$i]{'ACTIVE'},$CONNSCHED::config[$i]{'ACTION'},$CONNSCHED::config[$i]{'PROFILENR'},";
    print FILE "$CONNSCHED::config[$i]{'TIME'},$CONNSCHED::config[$i]{'DAYSTYPE'},";
    print FILE "$CONNSCHED::config[$i]{'DAYS'},$CONNSCHED::config[$i]{'WEEKDAYS'},,$CONNSCHED::config[$i]{'COMMENT'}\n";
  }
  close FILE;

  &ReadConfig();
}
