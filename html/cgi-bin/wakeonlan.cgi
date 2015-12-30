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


# remove comment from next line to get wakeup info in seperate page
my $refresh = 'yes';
# remove comment from next line to get wakeup info as inline box
#my $refresh = '';


#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::colouryellow} );
undef (@dummy);
my $line;
my $i;

my @wol_devices = ();
#configfile
our $datafile = "/var/ipfire/wakeonlan/clients.conf";
&ReadConfig;

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

my %netsettings = ();
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
my %cgiparams = ();

$cgiparams{'ACTION'} = '';    # add/edit/update/remove/wakeup
$cgiparams{'ID'} = '';        # points to record for ACTION (edit/update/remove)
$cgiparams{'CLIENT_MAC'} = '';
$cgiparams{'CLIENT_IFACE'} = '';
$cgiparams{'CLIENT_COMMENT'} = '';
&Header::getcgihash(\%cgiparams);

my %selected = ();
$selected{'CLIENT_IFACE'}{'green'} = '';
$selected{'CLIENT_IFACE'}{'blue'} = '';
$selected{'CLIENT_IFACE'}{'orange'} = '';
$selected{'CLIENT_IFACE'}{'red'} = '';

&Header::showhttpheaders();

my $errormessage = "";

if ( $cgiparams{'ACTION'} eq 'add' )
{
  # add a device, check for valid and non-duplicate MAC
  if ( $cgiparams{'CLIENT_MAC'} eq '' )
  {
    goto ADDEXIT;
  }

  $cgiparams{'CLIENT_MAC'} =~ tr/-/:/;

  unless( &General::validmac($cgiparams{'CLIENT_MAC'}) )
  {
    $errormessage = $Lang::tr{'invalid mac address'}; 
    goto ADDEXIT;
  }

  for $i ( 0 .. $#wol_devices )
  {
    if ( lc($cgiparams{'CLIENT_MAC'}) eq lc($wol_devices[$i]{'MAC'}) )
    {
      $errormessage = $Lang::tr{'duplicate mac'};
      goto ADDEXIT;
    }
  }

  unless ( $errormessage )
  {
    push @wol_devices, { MAC => uc($cgiparams{'CLIENT_MAC'}), IFace => $cgiparams{'CLIENT_IFACE'}, Comment => $cgiparams{'CLIENT_COMMENT'} };
    &WriteConfig;
    undef %cgiparams;
  }

ADDEXIT:
# jump here to keep cgiparams!
}

if ( $cgiparams{'ACTION'} eq 'update' )
{
  # update a device, check for valid and non-duplicate MAC
  if ( $cgiparams{'CLIENT_MAC'} eq '' )
  {
    goto UPDATEEXIT;
  }

  $cgiparams{'CLIENT_MAC'} =~ tr/-/:/;

  unless( &General::validmac($cgiparams{'CLIENT_MAC'}) )
  {
    $errormessage = $Lang::tr{'invalid mac address'}; 
    goto UPDATEEXIT;
  }

  for $i ( 0 .. $#wol_devices )
  {
    if ( $i == $cgiparams{'ID'} ) { next; }
    if ( lc($cgiparams{'CLIENT_MAC'}) eq lc($wol_devices[$i]{'MAC'}) )
    {
      $errormessage = $Lang::tr{'duplicate mac'};
      goto UPDATEEXIT;
    }
  }

  unless ( $errormessage )
  {
    $wol_devices[$cgiparams{'ID'}]{'MAC'} = $cgiparams{'CLIENT_MAC'};
    $wol_devices[$cgiparams{'ID'}]{'IFace'} = $cgiparams{'CLIENT_IFACE'};
    $wol_devices[$cgiparams{'ID'}]{'Comment'} = $cgiparams{'CLIENT_COMMENT'};
    &WriteConfig;
    undef %cgiparams;
  }

UPDATEEXIT:
# jump here to keep cgiparams!
}

if ( $cgiparams{'ACTION'} eq 'remove' )
{
  # simply set MAC to empty, WriteConfig will handle the gory details
  $wol_devices[$cgiparams{'ID'}]{'MAC'} = '';
  &WriteConfig;
}

if ( ($cgiparams{'ACTION'} ne 'wakeup') || ($refresh ne 'yes') )
{
  &Header::openpage($Lang::tr{'WakeOnLan'}, 1, '');
  &Header::openbigbox('100%', 'left', '', $errormessage);
}

if ( $cgiparams{'ACTION'} eq 'wakeup' )
{
  # wakey wakey
  my $mac = $wol_devices[$cgiparams{'ID'}]{'MAC'};
  my $iface = uc($wol_devices[$cgiparams{'ID'}]{'IFace'}).'_DEV';
  $iface = $netsettings{"$iface"};

  undef %cgiparams;

  system("/usr/local/bin/launch-ether-wake $mac $iface");

  # make a box with info, 'refresh' to normal screen after 5 seconds
  if ( $refresh eq 'yes' )
  {
    &Header::openpage($Lang::tr{'WakeOnLan'}, 1, "<meta http-equiv='refresh' content='3;url=/cgi-bin/wakeonlan.cgi'");
    &Header::openbigbox('100%', 'left');
  }
  &Header::openbox('100%', 'left', $Lang::tr{'WakeOnLan'});
  print "<p>$Lang::tr{'magic packet send to:'} $mac ($iface)</p>";
  &Header::closebox();

  if ( $refresh eq 'yes' )
  {
    &Header::closebigbox();
    &Header::closepage();
    # that's all folks
    exit;
  }
}

#print "Action: $cgiparams{'ACTION'}<br />";
#print "ID: $cgiparams{'ID'}<br />";
#print "MAC: $cgiparams{'CLIENT_MAC'}<br />";
#print "IFace: $cgiparams{'CLIENT_IFACE'}<br />";
#print "Rem: $cgiparams{'CLIENT_COMMENT'}<br />";

if ( $errormessage )
{
  # some error from add / update
  &Header::openbox('100%', 'left', $Lang::tr{'error messages'});
  print "<class name='base'>$errormessage\n";
  print "&nbsp;</class>\n";
  &Header::closebox();
}

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

$selected{'CLIENT_IFACE'}{$cgiparams{'CLIENT_IFACE'}} = "selected='selected'";
my $buttontext = $Lang::tr{'add'};
if ( $cgiparams{'ACTION'} eq 'edit' )
{
  &Header::openbox('100%', 'left', "$Lang::tr{'edit device'}");
  $buttontext = $Lang::tr{'update'};
  $cgiparams{'CLIENT_MAC'} = $wol_devices[$cgiparams{'ID'}]{'MAC'};
  $selected{'CLIENT_IFACE'}{$wol_devices[$cgiparams{'ID'}]{'IFace'}} = "selected='selected'";
  $cgiparams{'CLIENT_COMMENT'} = $wol_devices[$cgiparams{'ID'}]{'Comment'};
}
elsif ( $cgiparams{'ACTION'} eq 'update' )
{
  &Header::openbox('100%', 'left', "$Lang::tr{'edit device'}");
  $buttontext = $Lang::tr{'update'};
}
else
{
  &Header::openbox('100%', 'left', "$Lang::tr{'add device'}");
}

print <<END
<table width='100%'>
<tr>
  <td width='15%' class='base'>$Lang::tr{'mac address'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
  <td width='40%'><input type='text' name='CLIENT_MAC' value='$cgiparams{'CLIENT_MAC'}' size='25' /></td>
  <td width='10%' class='base'>$Lang::tr{'interface'}:&nbsp;</td>
  <td align='left'>
    <select name='CLIENT_IFACE'>
END
;

print "<option value='green' $selected{'CLIENT_IFACE'}{'green'}>$Lang::tr{'green'}</option>";
if (&haveBlueNet()) 
{
  print "<option value='blue' $selected{'CLIENT_IFACE'}{'blue'}>$Lang::tr{'blue'}</option>";
}
if (&haveOrangeNet()) 
{
  print "<option value='orange' $selected{'CLIENT_IFACE'}{'orange'}>$Lang::tr{'orange'}</option>";
}
# red for some testing purposes only
# print "<option value='red' $selected{'CLIENT_IFACE'}{'red'}>$Lang::tr{'red'}</option>";
print <<END
    </select>
  </td>
</tr>
<tr>
  <td width='15%' class='base'>$Lang::tr{'remark'}:</td>
  <td colspan='4' align='left'><input type='text' name='CLIENT_COMMENT' value='$cgiparams{'CLIENT_COMMENT'}' size='40' /></td>
</tr>
</table>
<br>
<hr />
<table width='100%'>
<tr>
  <td class='base' valign='top'><img src='/blob.gif' alt='*' />$Lang::tr{'required field'}</td>
  <td width='40%' align='right'>
END
;

if ( ($cgiparams{'ACTION'} eq 'edit') || ($cgiparams{'ACTION'} eq 'update') ) 
{
  print "<input type='hidden' name='ID' value='$cgiparams{'ID'}' />\n";
  print "<input type='hidden' name='ACTION' value='update' />";
}
else
{
  print "<input type='hidden' name='ACTION' value='add' />";
}
print "<input type='submit' name='SUBMIT' value='$buttontext' /></td></tr></table>";

&Header::closebox();

print "</form>\n";

#######################################
#
# now list already configured devivces
#
#######################################
&Header::openbox('100%', 'left', "$Lang::tr{'current devices'}");

print <<END
<table width='100%' class='tbl'>
<tr>
<th align='center' width='20%'><b>$Lang::tr{'mac address'}</b></th>
<th align='center' width='10%'><b>$Lang::tr{'interface'}</b></th>
<th align='center' width='60%'><b>$Lang::tr{'remark'}</b></th>
<th align='center' colspan='2'><b>$Lang::tr{'action'}</b></th>
<th></th>
</tr>
END
;
my $col="";
for $i ( 0 .. $#wol_devices )
{
  my $wol_mac = $wol_devices[$i]{'MAC'};
  my $wol_iface = $wol_devices[$i]{'IFace'};
  my $wol_txt = &Header::cleanhtml($wol_devices[$i]{'Comment'});

  if ( (($cgiparams{'ACTION'} eq 'edit') || ($cgiparams{'ACTION'} eq 'update')) && ($i == $cgiparams{'ID'}) ) 
  {
    print "<tr>";
    $col="bgcolor='${Header::colouryellow}'";
  }
  elsif ( $i % 2) 
  {
    print "<tr>";
    $col="bgcolor='$color{'color20'}'";
  }
  else
  {
    print "<tr>";
    $col="bgcolor='$color{'color22'}'";
  }

  print <<END
<td align='center' $col>$wol_mac</td>
<td align='center' $col>$Lang::tr{"$wol_iface"}</td>
<td align='left' $col>$wol_txt</td>
<td align='center' $col>
END
;
  if ( (($wol_iface eq 'blue') && ! &haveBlueNet()) 
    || (($wol_iface eq 'orange') && ! &haveOrangeNet()) )
  {
    # configured IFace (momentarily) not available -> now wakeup button/image
    print "&nbsp;";
  }
  else
  {
  print <<END
<form method='post' name='frma$i' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='ACTION' value='wakeup' />
<input type='image' name='wakeup' src='/images/wakeup.gif' alt='$Lang::tr{'wol wakeup'}' title='$Lang::tr{'wol wakeup'}' />
<input type='hidden' name='ID' value='$i' />
</form>
END
;
  }
  print <<END
</td>
<td align='center' $col>
  <form method='post' name='frmb$i' action='$ENV{'SCRIPT_NAME'}'>
  <input type='hidden' name='ACTION' value='edit' />
  <input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' />
  <input type='hidden' name='ID' value='$i' />
  </form>
</td>
<td align='center' $col>
  <form method='post' name='frmc$i' action='$ENV{'SCRIPT_NAME'}'>
  <input type='hidden' name='ACTION' value='remove' />
  <input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' alt='$Lang::tr{'remove'}' title='$Lang::tr{'remove'}' />
  <input type='hidden' name='ID' value='$i' />
  </form>
</td>
END
;
  print "</tr>\n";
}

print "</table>";

&Header::closebox();

&Header::closebigbox();
&Header::closepage();

#
# load the configuration file
#
sub ReadConfig
{
  # datafileformat:
  #   ID,MAC,IFACE,,Comment
  # 
  my @tmpfile = ();
  if ( open(FILE, "$datafile") )
  {
    @tmpfile = <FILE>;
    close (FILE);
  }

  @wol_devices = ();

  # populate devices list
  foreach $line ( @tmpfile )
  {
    chomp($line);               # remove newline
    my @temp = split(/\,/,$line,5);
    if ( $temp[1] eq '' ) { next; }
    unless(&General::validmac($temp[1])) { next; }

    push @wol_devices, { ID => $temp[0], MAC => $temp[1], IFace => $temp[2], Comment => $temp[4] };
  }
}

#
# write the configuration file
#
sub WriteConfig
{
  my $line;
  my @temp;

  my @tmp_clients;

  for $i ( 0 .. $#wol_devices )
  {
    unless(&General::validmac($wol_devices[$i]{'MAC'})) { next; }
    unshift (@tmp_clients, uc($wol_devices[$i]{'MAC'}).",$wol_devices[$i]{'IFace'},,$wol_devices[$i]{'Comment'}");
  }
  
  # sort tmp_clients on MAC
  @tmp_clients = sort ( @tmp_clients );

  open(FILE, ">$datafile") or die 'hosts datafile error';

  my $count = 0;
  foreach $line (@tmp_clients) 
  {
    print FILE "$count,$line\n";
    $count++;
  }
  close FILE;

  &ReadConfig;
}


#
# copied these from dmzholes.cgi (thnx dotzball)
#   seems to be the way to do this :-S
#
sub haveOrangeNet
{
  if ($netsettings{'CONFIG_TYPE'} == 2) {return 1;}
  if ($netsettings{'CONFIG_TYPE'} == 4) {return 1;}
  return 0;
}

sub haveBlueNet
{
  if ($netsettings{'CONFIG_TYPE'} == 3) {return 1;}
  if ($netsettings{'CONFIG_TYPE'} == 4) {return 1;}
  return 0;
}
