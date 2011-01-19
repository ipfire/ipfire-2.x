#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2011  IPFire Team  <info@ipfire.org>                     #
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

my @network=();
my @masklen=();
my @colour=();

use Net::IPv4Addr qw( :all );

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::table1colour} );
undef (@dummy);

# Read various files

my %netsettings=();
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

open (ACTIVE, '/usr/local/bin/getiptstate |') or die 'Unable to open ip_conntrack';
my @active = <ACTIVE>;
close (ACTIVE);

if (open(IP, "${General::swroot}/red/local-ipaddress")) {
        my $redip = <IP>;
        close(IP);
        chomp $redip;
        push(@network, $redip);
        push(@masklen, '255.255.255.255' );
        push(@colour, ${Header::colourfw} );
}

my @vpn = `/usr/local/bin/ipsecctrl I 2>/dev/null|grep erouted|cut -d"]" -f3|cut -d"=" -f4|cut -d";" -f1| sed "s|/| |g"`;
  foreach my $route (@vpn) {
                chomp($route);
                my @temp = split(/[\t ]+/, $route);
                if ( $temp[0] eq '$redip' ){next;}
                push(@network, $temp[0]);
                push(@masklen, $temp[1]);
                push(@colour, ${Header::colourvpn} );
        }

my $aliasfile = "${General::swroot}/ethernet/aliases";
open(ALIASES, $aliasfile) or die 'Unable to open aliases file.';
my @aliases = <ALIASES>;
close(ALIASES);

# Add Green Firewall Interface
push(@network, $netsettings{'GREEN_ADDRESS'});
push(@masklen, "255.255.255.255" );
push(@colour, ${Header::colourfw} );

# Add Green Network to Array
push(@network, $netsettings{'GREEN_NETADDRESS'});
push(@masklen, $netsettings{'GREEN_NETMASK'} );
push(@colour, ${Header::colourgreen} );

# Add Green Routes to Array
my @routes = `/sbin/route -n | /bin/grep $netsettings{'GREEN_DEV'}`;
foreach my $route (@routes) {
        chomp($route);
        my @temp = split(/[\t ]+/, $route);
        push(@network, $temp[0]);
        push(@masklen, $temp[2]);
        push(@colour, ${Header::colourgreen} );
}

# Add Firewall Localhost 127.0.0.1
push(@network, '127.0.0.1');
push(@masklen, '255.255.255.255' );
push(@colour, ${Header::colourfw} );

# Add Orange Network
if ($netsettings{'ORANGE_DEV'}) {
        push(@network, $netsettings{'ORANGE_NETADDRESS'});
        push(@masklen, $netsettings{'ORANGE_NETMASK'} );
        push(@colour, ${Header::colourorange} );
        # Add Orange Routes to Array
        @routes = `/sbin/route -n | /bin/grep $netsettings{'ORANGE_DEV'}`;
        foreach my $route (@routes) {
                  chomp($route);
                my @temp = split(/[\t ]+/, $route);
                push(@network, $temp[0]);
                push(@masklen, $temp[2]);
                push(@colour, ${Header::colourorange} );
        }
}

# Add Blue Firewall Interface
push(@network, $netsettings{'BLUE_ADDRESS'});
push(@masklen, "255.255.255.255" );
push(@colour, ${Header::colourfw} );

# Add Blue Network
if ($netsettings{'BLUE_DEV'}) {
        push(@network, $netsettings{'BLUE_NETADDRESS'});
        push(@masklen, $netsettings{'BLUE_NETMASK'} );
        push(@colour, ${Header::colourblue} );
        # Add Blue Routes to Array
        @routes = `/sbin/route -n | /bin/grep $netsettings{'BLUE_DEV'}`;
        foreach my $route (@routes) {
                  chomp($route);
                my @temp = split(/[\t ]+/, $route);
                push(@network, $temp[0]);
                push(@masklen, $temp[2]);
                push(@colour, ${Header::colourblue} );
        }
}

# Add OpenVPN net and RED/BLUE/ORANGE entry (when appropriate)
if (-e "${General::swroot}/ovpn/settings") {
    my %ovpnsettings = ();    
    &General::readhash("${General::swroot}/ovpn/settings", \%ovpnsettings);
    my @tempovpnsubnet = split("\/",$ovpnsettings{'DOVPN_SUBNET'});

    # add OpenVPN net
                push(@network, $tempovpnsubnet[0]);
                push(@masklen, $tempovpnsubnet[1]);
                push(@colour, ${Header::colourovpn} );


    if ( ($ovpnsettings{'ENABLED_BLUE'} eq 'on') && $netsettings{'BLUE_DEV'} ) {
      # add BLUE:port / proto
            push(@network, $netsettings{'BLUE_ADDRESS'} );
            push(@masklen, '255.255.255.255' );
                  push(@colour, ${Header::colourovpn} );
    }
    if ( ($ovpnsettings{'ENABLED_ORANGE'} eq 'on') && $netsettings{'ORANGE_DEV'} ) {
      # add ORANGE:port / proto
            push(@network, $netsettings{'ORANGE_ADDRESS'} );
            push(@masklen, '255.255.255.255' );
                  push(@colour, ${Header::colourovpn} );
    }
}

# Add STATIC RED aliases
if ($netsettings{'RED_DEV'}) {
        # We have a RED eth iface
        if ($netsettings{'RED_TYPE'} eq 'STATIC') {
                # We have a STATIC RED eth iface
                foreach my $line (@aliases)
                {
                        chomp($line);
                        my @temp = split(/\,/,$line);
                        if ( $temp[0] ) {
                                push(@network, $temp[0]);
                                push(@masklen, $netsettings{'RED_NETMASK'} );
                                push(@colour, ${Header::colourfw} );
                        }
                }
        }
}

# Add VPNs
if ( $vpn[0] ne 'none' ) {
        foreach my $line (@vpn) {
                my @temp = split(/[\t ]+/,$line);
                my @temp1 = split(/[\/:]+/,$temp[3]);
                push(@network, $temp1[0]);
                push(@masklen, ipv4_cidr2msk($temp1[1]));
                push(@colour, ${Header::colourvpn} );
        }
}

#Establish simple filtering&sorting boxes on top of table

our %cgiparams;
&Header::getcgihash(\%cgiparams);

my @list_proto = ($Lang::tr{'all'}, 'icmp', 'udp', 'tcp');
my @list_state = ($Lang::tr{'all'}, 'SYN_SENT', 'SYN_RECV', 'ESTABLISHED', 'FIN_WAIT',
                    'CLOSE_WAIT', 'LAST_ACK', 'TIME_WAIT', 'CLOSE', 'LISTEN');
my @list_mark = ($Lang::tr{'all'}, '[ASSURED]', '[UNREPLIED]');
my @list_sort = ('orgsip','protocol', 'expires', 'status', 'orgdip', 'orgsp',
                    'orgdp', 'exsip', 'exdip', 'exsp', 'exdp', 'marked');

# init or silently correct unknown value...
if ( ! grep ( /^$cgiparams{'SEE_PROTO'}$/ , @list_proto )) { $cgiparams{'SEE_PROTO'} = $list_proto[0] };
if ( ! grep ( /^$cgiparams{'SEE_STATE'}$/ , @list_state )) { $cgiparams{'SEE_STATE'} = $list_state[0] };
if ( ($cgiparams{'SEE_MARK'} ne $Lang::tr{'all'}) &&	# ok the grep should work but it doesn't because of
     ($cgiparams{'SEE_MARK'} ne '[ASSURED]') &&		# the '[' & ']' interpreted as list separator.
     ($cgiparams{'SEE_MARK'} ne '[UNREPLIED]')		# So, explicitly enumerate items.
   )  { $cgiparams{'SEE_MARK'}  = $list_mark[0] };
if ( ! grep ( /^$cgiparams{'SEE_SORT'}$/  , @list_sort ))  { $cgiparams{'SEE_SORT'}  = $list_sort[0] };
# *.*.*.* or a valid IP
if ( $cgiparams{'SEE_SRC'}  !~ /^(\*\.\*\.\*\.\*\.|\d+\.\d+\.\d+\.\d+)$/) {  $cgiparams{'SEE_SRC'} = '*.*.*.*' };
if ( $cgiparams{'SEE_DEST'} !~ /^(\*\.\*\.\*\.\*\.|\d+\.\d+\.\d+\.\d+)$/) {  $cgiparams{'SEE_DEST'} = '*.*.*.*' };


our %entries = ();	# will hold the lines analyzed correctly
my $unknownlines = '';	# should be empty all the time...
my $index = 0;		# just a counter to make unique entryies in entries

&Header::showhttpheaders();
&Header::openpage($Lang::tr{'connections'}, 1, '');
&Header::openbigbox('100%', 'left');
&Header::openbox('100%', 'left', $Lang::tr{'connection tracking'});

# Build listbox objects
my $menu_proto = &make_select ('SEE_PROTO', $cgiparams{'SEE_PROTO'}, @list_proto);
my $menu_state = &make_select ('SEE_STATE', $cgiparams{'SEE_STATE'}, @list_state);

print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='100%'>
<tr><td align='center'><b>$Lang::tr{'legend'} : </b></td>
    <td align='center' bgcolor='${Header::colourgreen}'><b><font color='#FFFFFF'>$Lang::tr{'lan'}</font></b></td>
    <td align='center' bgcolor='${Header::colourred}'><b><font color='#FFFFFF'>$Lang::tr{'internet'}</font></b></td>
    <td align='center' bgcolor='${Header::colourorange}'><b><font color='#FFFFFF'>$Lang::tr{'dmz'}</font></b></td>
    <td align='center' bgcolor='${Header::colourblue}'><b><font color='#FFFFFF'>$Lang::tr{'wireless'}</font></b></td>
    <td align='center' bgcolor='${Header::colourfw}'><b><font color='#FFFFFF'>IPFire</font></b></td>
    <td align='center' bgcolor='${Header::colourvpn}'><b><font color='#FFFFFF'>$Lang::tr{'vpn'}</font></b></td>
    <td align='center' bgcolor='${Header::colourovpn}'><b><font color='#FFFFFF'>$Lang::tr{'OpenVPN'}</font></b></td>
</tr>
</table>
<br />
<table width='100%'>
<tr><td align='center'><font size=2>$Lang::tr{'source ip and port'}</font></td>
		<td>&nbsp;</td>
		<td align='center'><font size=2>$Lang::tr{'dest ip and port'}</font></td>
		<td>&nbsp;</td>
		<td align='center'><font size=2>$Lang::tr{'protocol'}</font></td>
		<td align='center'><font size=2>$Lang::tr{'connection'}<br></br>$Lang::tr{'status'}</font></td>
    <td align='center'><font size=2>$Lang::tr{'expires'}<br></br>($Lang::tr{'seconds'})</font></td>
    
</tr>
<tr><td colspan='4'>&nbsp;</td>
		<td align='center'>$menu_proto</td>
    <td align='center'>$menu_state</td>
    <td>&nbsp;</td>
</tr>
<tr>
    <td align='center' colspan='7'></td>
</tr>
<tr>
    <td align='center' colspan='7'><input type='submit' value="$Lang::tr{'update'}" /></td>
</tr>

END
;

my $i=0;
foreach my $line (@active) {
    $i++;
    if ($i < 3) {
			next;
    }
    chomp($line);
    my @temp = split(' ',$line);

    my ($sip, $sport) = split(':', $temp[0]);
    my ($dip, $dport) = split(':', $temp[1]);
    my $proto = $temp[2];
    my $state; my $ttl;
    if ( $proto eq "esp" ){$state = "";$ttl = $temp[3];}
    elsif ( $proto eq "icmp" ){$state = "";$ttl = $temp[4];}
    else{$state = $temp[3];$ttl = $temp[4];}
    
    next if( !(
              		(($cgiparams{'SEE_PROTO'}  eq $Lang::tr{'all'}) || ($proto  eq $cgiparams{'SEE_PROTO'} ))
    	         && (($cgiparams{'SEE_STATE'}  eq $Lang::tr{'all'}) || ($state  eq $cgiparams{'SEE_STATE'} ))
               && (($cgiparams{'SEE_SRC'}    eq "*.*.*.*")        || ($sip    eq $cgiparams{'SEE_SRC'}   ))
               && (($cgiparams{'SEE_DEST'}   eq "*.*.*.*")    	  || ($dip    eq $cgiparams{'SEE_DEST'}  ))
              ));

    if (($proto eq 'udp') && ($ttl eq '')) {
			$ttl = $state;
			$state = '&nbsp;';	
    }

    my $sipcol = ipcolour($sip);
    my $dipcol = ipcolour($dip);

    my $sserv = '';
    if ($sport < 1024) {
	$sserv = uc(getservbyport($sport, lc($proto)));
	if ($sserv ne '') {
	    $sserv = "&nbsp;($sserv)";
	}
    }

    my $dserv = '';
    if ($dport < 1024) {
	$dserv = uc(getservbyport($dport, lc($proto)));
	if ($dserv ne '') {
	    $dserv = "&nbsp;($dserv)";
	}
    }

    print <<END
    <tr >
      <td align='center' bgcolor='$sipcol'>
        <a href='/cgi-bin/ipinfo.cgi?ip=$sip'>
          <font color='#FFFFFF'>$sip</font>
        </a>
      </td>
      <td align='center' bgcolor='$sipcol'>
        <a href='http://isc.sans.org/port_details.php?port=$sport' target='top'>
          <font color='#FFFFFF'>$sport$sserv</font>
        </a>
      </td>
      <td align='center' bgcolor='$dipcol'>
        <a href='/cgi-bin/ipinfo.cgi?ip=$dip'>
          <font color='#FFFFFF'>$dip</font>
        </a>
      </td>
      <td align='center' bgcolor='$dipcol'>
        <a href='http://isc.sans.org/port_details.php?port=$dport' target='top'>
          <font color='#FFFFFF'>$dport$dserv</font>
        </a>
      </td>
      <td align='center'>$proto</td>
      <td align='center'>$state</td>
      <td align='center'>$ttl</td>
    </tr>
END
;
}

print "</table></form>";

&Header::closebox();
&Header::closebigbox();
&Header::closepage();

sub ipcolour($) {
        my $id = 0;
        my $line;
        my $colour = ${Header::colourred};
        my ($ip) = $_[0];
        my $found = 0;
        foreach $line (@network) {
					if ($network[$id] eq '') {
			 			$id++;
					} else {
						if (!$found && ipv4_in_network( $network[$id] , $masklen[$id], $ip) ) {
							$found = 1;
							$colour = $colour[$id];
						}
						$id++;
					}
        }
        return $colour
}

# Create a string containing a complete SELECT html object 
# param1: name
# param2: current value selected
# param3: field list
sub make_select ($,$,$) {
        my $select_name = shift;
        my $selected    = shift;
        my $select = "<select name='$select_name'>";

        foreach my $value (@_) {
                    my $check = $selected eq $value ? "selected='selected'" : '';
                    $select .= "<option $check value='$value'>$value</option>";
        }
        $select .= "</select>";
        return $select;
}

# Build a list of IP obtained from the %entries hash
# param1: IP field name
sub get_known_ips ($) {
        my $field = shift;
        my $qs = $cgiparams{'SEE_SORT'};	# switch the sort order
        $cgiparams{'SEE_SORT'} = $field;

        my @liste=('*.*.*.*');
        foreach my $entry ( sort sort_entries keys %entries) {
                    push (@liste, $entries{$entry}->{$field}) if (! grep (/^$entries{$entry}->{$field}$/,@liste) );
        }

        $cgiparams{'SEE_SORT'} = $qs;	#restore sort order
        return @liste;
}

# Used to sort the table containing the lines displayed.
sub sort_entries { #Reverse is not implemented
        my $qs=$cgiparams{'SEE_SORT'};
        if ($qs =~ /orgsip|orgdip|exsip|exdip/) {
                my @a = split(/\./,$entries{$a}->{$qs});
                my @b = split(/\./,$entries{$b}->{$qs});
                ($a[0]<=>$b[0]) ||
                ($a[1]<=>$b[1]) ||
                ($a[2]<=>$b[2]) ||
                ($a[3]<=>$b[3]);
        } elsif ($qs =~ /expire|orgsp|orgdp|exsp|exdp/) {
                    $entries{$a}->{$qs} <=> $entries{$b}->{$qs};
        } else {
                    $entries{$a}->{$qs} cmp $entries{$b}->{$qs};
        }
}

1;
