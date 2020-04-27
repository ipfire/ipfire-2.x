#!/usr/bin/perl

###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
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
# Copyright (C) 2018 - 2020 The IPFire Team                                   #
#                                                                             #
###############################################################################

use strict;
use CGI qw/:standard/;
# enable the following only for debugging purposes
#use warnings;
#use CGI::Carp 'fatalsToBrowser';
use Sort::Naturally;
use Socket;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

###############################################################################
# Configuration variables
###############################################################################

my $settings      = "${General::swroot}/ipblacklist/settings";
my $sources       = "${General::swroot}/ipblacklist/sources";
my $getipstat     = '/usr/local/bin/getipstat';
my $getipsetstat  = '/usr/local/bin/getipsetstat';
my $control       = '/usr/local/bin/ipblacklistctrl';
my $lockfile      = '/var/run/ipblacklist.pid';
my %cgiparams     = ('ACTION' => '');

###############################################################################
# Variables
###############################################################################

my $errormessage  = '';
my $updating      = 0;
my %mainsettings;
my %color;
my %sources;
my %stats;

# Default settings - normally overwritten by settings file

my %settings = ( 'DEBUG'           => 0,
                 'LOGGING'         => 'on',
                 'ENABLE'          => 'off' );

# Read all parameters

Header::getcgihash( \%cgiparams);
General::readhash( "${General::swroot}/main/settings", \%mainsettings );
General::readhash( "/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color );
General::readhash( $settings, \%settings ) if (-r $settings);
eval qx|/bin/cat $sources|                 if (-r $sources);

# Show Headers

Header::showhttpheaders();

# Process actions

if ($cgiparams{'ACTION'} eq "$Lang::tr{'save'}")
{
  # Save Button

  my %new_settings = ( 'ENABLE'          => 'off',
                       'LOGGING'         => 'off',
                       'DEBUG'           => 0 );

  foreach my $item ('LOGGING', 'ENABLE', keys %sources)
  {
    $new_settings{$item} = (exists $cgiparams{$item}) ? 'on' : 'off';

    $updating = 1 if (not exists $settings{$item} or $new_settings{$item} ne $settings{$item});
  }

  # Check for redundant blacklists being enabled

  foreach my $list (keys %sources)
  {
    if (exists $new_settings{$list} and
        $new_settings{$list} eq 'on' and
        exists $sources{$list}{'disable'})
    {
      my @disable;

      if ('ARRAY' eq ref $sources{$list}{'disable'})
      {
        @disable = @{ $sources{$list}{'disable'} };
      }
      else
      {
        @disable = ( $sources{$list}{'disable'} );
      }

      foreach my $disable (@disable)
      {
        if ($new_settings{$disable} eq 'on')
        {
          $new_settings{$disable} = 'off';

          $updating      = 1;
          $errormessage .= "$Lang::tr{'ipblacklist disable pre'} $disable " .
                            "$Lang::tr{'ipblacklist disable mid'} $list $Lang::tr{'ipblacklist disable post'}<br>\n";
        }
      }
    }
  }

  if ($settings{'LOGGING'} ne $new_settings{'LOGGING'})
  {
    if ($new_settings{'LOGGING'} eq 'on')
    {
      system( "$control log-on" );
    }
    else
    {
      system( "$control log-off" );
    }
  }

  if ($settings{'ENABLE'} ne $new_settings{'ENABLE'})
  {
    if ($new_settings{'ENABLE'} eq 'on')
    {
      system( "$control enable" );
    }
    else
    {
      system( "$control disable" );
    }

    $updating = 1;
  }

  %settings = %new_settings;

  if ($errormessage)
  {
    $updating = 0;
  }
  else
  {
    General::writehash($settings, \%new_settings);

    if ($updating)
    {
      system( "$control update &" );
      show_running();
      exit 0;
    }
  }
}

if (is_running())
{
  show_running();
  exit 0;
}

# Show site

Header::openpage($Lang::tr{'ipblacklist'}, 1, '');
Header::openbigbox('100%', 'left');

error() if ($errormessage);

configsite();

# End of page

Header::closebigbox();
Header::closepage();

exit 0;


#------------------------------------------------------------------------------
# sub configsite()
#
# Displays configuration
#------------------------------------------------------------------------------

sub configsite
{
  # Find preselections

  my $enable = 'checked';
  Header::openbox('100%', 'left', $Lang::tr{'settings'});

  #### JAVA SCRIPT ####

  print<<END;
<script>
  \$(document).ready(function()
  {
    // Show/Hide elements when ENABLE checkbox is checked.
    if (\$("#ENABLE").attr("checked"))
    {
      \$(".sources").show();
    }
    else
    {
      \$(".sources").hide();
    }

    // Toggle Source list elements when "ENABLE" checkbox is clicked
    \$("#ENABLE").change(function()
    {
      \$(".sources").toggle();
    });
  });
</script>
END

  ##### JAVA SCRIPT END ####

  # Enable checkbox

  $enable = ($settings{'ENABLE'} eq 'on') ? ' checked' : '';

  print<<END;
  <form method='post' action='$ENV{'SCRIPT_NAME'}'>
  <table style='width:100%' border='0'>
  <tr>
    <td style='width:24em'>$Lang::tr{'ipblacklist use ipblacklists'}</td>
    <td><input type='checkbox' name='ENABLE' id='ENABLE'$enable></td>
  </tr>
  </table><br>

END

  # The following are only displayed if the blacklists are enabled

  $enable = ($settings{'LOGGING'} eq 'on') ? ' checked' : '';

  print <<END;
<div class='sources'>
  <table style='width:100%' border='0'>
  <tr>
    <td style='width:24em'>$Lang::tr{'ipblacklist log'}</td>
    <td><input type='checkbox' name="LOGGING" id="LOGGING"$enable></td>
  </tr>
  </table>
  <br><br>
  <h2>$Lang::tr{'ipblacklist blacklist settings'}</h2>
  <table width='100%' cellspacing='1' class='tbl'>
  <tr>
    <th align='left'>$Lang::tr{'ipblacklist id'}</th>
    <th align='left'>$Lang::tr{'ipblacklist name'}</th>
    <th align='left'>$Lang::tr{'ipblacklist category'}</th>
    <th align='center'>$Lang::tr{'ipblacklist enable'}</th>
  </tr>
END

  # Iterate through the list of sources

  my $lines = 0;

  foreach my $list (sort keys %sources)
  {
    my $name     = escapeHTML( $sources{$list}{'name'} );
    my $category = $Lang::tr{"ipblacklist category $sources{$list}{'category'}"};
    $enable      = '';
    my $col      = ($lines++ % 2) ? "bgcolor='$color{'color20'}'" : "bgcolor='$color{'color22'}'";

    $enable = ' checked' if (exists $settings{$list} and $settings{$list} eq 'on');

    print <<END;
    <tr $col>
    <td>
END

    if ($sources{$list}{info})
    {
      print "<a href='$sources{$list}{info}' target='_blank'>$list</a>\n";
    }
    else
    {
      print "$list\n";
    }

    print <<END;
    </td>
    <td>$name</td>
    <td>$category</td>
    <td align='center'><input type='checkbox' name="$list" id="$list"$enable></td>
    </tr>\n
END
  }

    # The save button at the bottom of the table

    print <<END;
    </table>
  </div>
    <table style='width:100%;'>
    <tr>
        <td colspan='3' display:inline align='right'><input type='submit' name='ACTION' value='$Lang::tr{'save'}'></td>
    </tr>
    </table>
END

  Header::closebox();
}


#------------------------------------------------------------------------------
# sub get_ipset_stats()
#
# Gets the number of entries in each IPSet.
#------------------------------------------------------------------------------

sub get_ipset_stats
{
  my $name;

  system( $getipsetstat );

  if (-r '/var/tmp/ipsets.txt')
  {
    open STATS, '<', '/var/tmp/ipsets.txt' or die "Can't open IP Sets stats file: $!";

    foreach my $line (<STATS>)
    {
      if ($line =~ m/Name: (\w+)/)
      {
        $name = $1;
        next;
      }

      if ($line =~ m/Number of entries: (\d+)/)
      {
        $stats{$name}{'size'} = $1;
      }
    }

    close STATS;

    unlink( '/var/tmp/ipsets.txt' );
  }
}


#------------------------------------------------------------------------------
# sub is_running()
#
# Checks to see if the main script is running
#------------------------------------------------------------------------------

sub is_running
{
  return 0 unless (-r $lockfile);

  open LOCKFILE, '<', $lockfile or die "Can't open lockfile";
  my $pid = <LOCKFILE>;
  close LOCKFILE;

  chomp $pid;

  return (-e "/proc/$pid");
}


#------------------------------------------------------------------------------
# sub show_running
#
# Displayed when update is running.
# Shows a 'working' message plus some information about the IPSets.
#------------------------------------------------------------------------------

sub show_running
{
  # Open site

  Header::openpage( $Lang::tr{'ipblacklist'}, 1, '<meta http-equiv="refresh" content="1;url=/cgi-bin/ipblacklist.cgi">' );
  Header::openbigbox( '100%', 'center' );
  error();
  Header::openbox( 'Working', 'center', "$Lang::tr{'ipblacklist working'}" );

  print <<END;
  <table width='100%'>
    <tr>
      <td align='center'>
        <img src='/images/indicator.gif' alt='$Lang::tr{'aktiv'}'>&nbsp;
      <td>
    </tr>
    </table>
    <br>
    <table cellspacing='1' align='center'>
    <tr><th>$Lang::tr{'ipblacklist id'}</th><th>$Lang::tr{'ipblacklist entries'}</th></tr>
END

  get_ipset_stats();

  foreach my $name (sort keys %stats)
  {
    print "<tr><td>$name</td><td align='right'>$stats{$name}{'size'}</td></tr>\n" if (exists $stats{$name}{'size'});
  }

  print <<END;
    </table>
END

  Header::closebox();

  Header::closebigbox();
  Header::closepage();
}


#------------------------------------------------------------------------------
# sub error()
#
# Shows error messages
#------------------------------------------------------------------------------

sub error
{
  Header::openbox('100%', 'left', $Lang::tr{'error messages'});
  print "<class name='base'>$errormessage\n";
  print "&nbsp;</class>\n";
  Header::closebox();
}


#------------------------------------------------------------------------------
# sub format_time( seconds )
#
# Converts time in seconds to HH:MM:SS
#------------------------------------------------------------------------------

sub format_time($) {
	my $time = shift;

	my $seconds = $time % 60;
	my $minutes = $time / 60;

	my $hours = 0;
	if ($minutes >= 60) {
		$hours = $minutes / 60;
		$minutes %= 60;
	}

	return sprintf("%3d:%02d:%02d", $hours, $minutes, $seconds);
}
