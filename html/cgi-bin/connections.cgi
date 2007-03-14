#!/usr/bin/perl
#
# (c) 2001 Jack Beglinger <jackb_guppy@yahoo.com>
#
# (c) 2003 Dave Roberts <countzerouk@hotmail.com> - colour coded netfilter/iptables rewrite for 1.3
#
# (c) 2006 Franck - add sorting+filtering capability
#
# (c) 2006 Peter Schälchli -inetwork (bug)
#

# Setup GREEN, ORANGE, IPFIRE, VPN CIDR networks, masklengths and colours only once

my @network=();
my @masklen=();
my @colour=();

use Net::IPv4Addr qw( :all );

use strict;

# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::table1colour} );
undef (@dummy);

# Read various files

my %netsettings=();
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

open (ACTIVE, "/proc/net/ip_conntrack") or die 'Unable to open ip_conntrack';
my @active = <ACTIVE>;
close (ACTIVE);

my @vpn = ('none');
open (ACTIVE, "/proc/net/ipsec_eroute") and @vpn = <ACTIVE>;
close (ACTIVE);

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

    if ( ($ovpnsettings{'ENABLED'} eq 'on') && open(IP, "${General::swroot}/red/local-ipaddress") ) {
      # add RED:port / proto
                  my $redip = <IP>;
                  close(IP);
                  chomp $redip;
                  push(@network, $redip );
                  push(@masklen, '255.255.255.255' );
                  push(@colour, ${Header::colourovpn} );
    }
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
if (open(IP, "${General::swroot}/red/local-ipaddress")) {
        my $redip = <IP>;
        close(IP);
        chomp $redip;
        push(@network, $redip);
        push(@masklen, '255.255.255.255' );
        push(@colour, ${Header::colourfw} );
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

foreach my $line (@active) {
        my $protocol='';
        my $expires='';
        my $status='';
        my $orgsip='';
        my $orgdip='';
        my $orgsp='';
        my $orgdp='';
        my $exsip='';
        my $exdip='';
        my $exsp='';
        my $exdp='';
        my $marked='';
        my $use='';

        chomp($line);
        my @temp = split(' ',$line);

           if ($temp[0] eq 'icmp') {
                $protocol  = $temp[0];
                $status    = $Lang::tr{'all'};
                $orgsip   = substr $temp[3], 4;
                     $orgdip   = substr $temp[4], 4;
                     $marked   = $temp[8] eq '[UNREPLIED]' ? '[UNREPLIED]' : ' ';
              }
           if ($temp[0] eq 'udp') {
                $protocol  = $temp[0];
                $status  = $Lang::tr{'all'};
                $orgsip = substr $temp[3], 4;
                     $orgdip  = substr $temp[4], 4;
                     $marked   = $temp[7] eq '[UNREPLIED]' ? '[UNREPLIED]' : defined ($temp[12]) ? $temp[11] : ' ';
              }
        if ($temp[0] eq 'tcp') {
                $protocol  = $temp[0];
                $status  = $temp[3];
                $orgsip = substr $temp[4], 4;
                $orgdip   = substr $temp[5], 4;
                     $marked   = $temp[8] eq '[UNREPLIED]' ? '[UNREPLIED]' : defined ($temp[13]) ? $temp[12] : ' ';
        }

        # filter the line if we found a known proto
        next if( !(
                   (($cgiparams{'SEE_PROTO'}  eq $Lang::tr{'all'}) || ($protocol  eq $cgiparams{'SEE_PROTO'} ))
                && (($cgiparams{'SEE_STATE'}  eq $Lang::tr{'all'}) || ($status    eq $cgiparams{'SEE_STATE'} ))
                && (($cgiparams{'SEE_MARK'}   eq $Lang::tr{'all'}) || ($marked    eq $cgiparams{'SEE_MARK'}  ))
                && (($cgiparams{'SEE_SRC'}    eq "*.*.*.*")        || ($orgsip    eq $cgiparams{'SEE_SRC'}   ))
                && (($cgiparams{'SEE_DEST'}   eq "*.*.*.*")    	   || ($orgdip    eq $cgiparams{'SEE_DEST'}  ))
                ));

        if ($temp[0] eq 'icmp') {
                my $offset = 0;
                    $protocol = $temp[0] . " (" . $temp[1] . ")";
                    $expires = $temp[2];
                $status = ' ';
                    if ($temp[8] eq '[UNREPLIED]' ) {
                        $offset = +1;
                }	
                    $orgsip = substr $temp[3], 4;
                    $orgdip = substr $temp[4], 4;
                    $orgsp = &General::GetIcmpDescription(substr( $temp[5], 5)) . "/" . substr( $temp[6], 5);;
                    $orgdp = 'id=' . substr( $temp[7], 3);
                    $exsip = substr $temp[8 + $offset], 4;
                    $exdip = substr $temp[9 + $offset], 4;
                $exsp = &General::GetIcmpDescription(substr( $temp[10 + $offset], 5)). "/" . substr( $temp[11 + $offset], 5); 
                $exdp = 'id=' . substr( $temp[11 + $offset], 5);
                     $marked   = $temp[8] eq '[UNREPLIED]' ? '[UNREPLIED]' : ' ';
                $use = substr( $temp[13 + $offset], 4 );
        }
        if ($temp[0] eq 'udp') {
                my $offset = 0;
                $marked = '';
                $protocol = $temp[0] . " (" . $temp[1] . ")";
                $expires = $temp[2];
                $status = ' ';
                $orgsip = substr $temp[3], 4;
                $orgdip = substr $temp[4], 4;
                $orgsp = substr $temp[5], 6;
                $orgdp = substr $temp[6], 6;
                if ($temp[7] eq '[UNREPLIED]') {
                    $offset = 1;
                    $marked = $temp[7];
                    $use = substr $temp[12], 4;
                } else {
                    if ((substr $temp[11], 0, 3) eq 'use' ) {
                        $marked = '';
                        $use = substr $temp[11], 4;
                    } else {
                        $marked = $temp[11];
                        $use = substr $temp[12], 4;
                    }
                }
                $exsip = substr $temp[7 + $offset], 4;
                $exdip = substr $temp[8 + $offset], 4;
                $exsp = substr $temp[9 + $offset], 6;
                $exdp = substr $temp[10 + $offset], 6;
        }
        if ($temp[0] eq 'tcp') {
                my $offset = 0;
                $protocol = $temp[0] . " (" . $temp[1] . ")";
                $expires = $temp[2];
                $status = $temp[3];
                $orgsip = substr $temp[4], 4;
                $orgdip = substr $temp[5], 4;
                $orgsp = substr $temp[6], 6;
                $orgdp = substr $temp[7], 6;
                if ($temp[8] eq '[UNREPLIED]') {
                        $marked = $temp[8];
                        $offset = 1;
                } else {
                        $marked = $temp[16];
                }
                $exsip = substr $temp[10 + $offset], 4;
                $exdip = substr $temp[11 + $offset], 4;
                $exsp = substr $temp[12 + $offset], 6;
                $exdp = substr $temp[13 + $offset], 6;
                $use = substr $temp[18], 4;
        }
        if ($temp[0] eq 'unknown') {
                my $offset = 0;
                $protocol = "??? (" . $temp[1] . ")";
                $protocol = "esp (" . $temp[1] . ")" if ($temp[1] == 50);
                $protocol = "ah (" . $temp[1] . ")" if ($temp[1] == 51);
                $expires = $temp[2];
                $status = ' ';
                $orgsip = substr $temp[3], 4;
                $orgdip = substr $temp[4], 4;
                $orgsp = ' ';
                $orgdp = ' ';
                $exsip = substr $temp[5], 4;
                $exdip = substr $temp[6], 4;
                $exsp = ' ';
                $exdp = ' ';
                $marked = ' ';
                $use = ' ';
        }
        if ($temp[0] eq 'gre') {
                my $offset = 0;
                $protocol = $temp[0] . " (" . $temp[1] . ")";
                $expires = $temp[2];
                $orgsip = substr $temp[5], 4;
                $orgdip = substr $temp[6], 4;
                $orgsp = ' ';
                $orgdp = ' ';
                $exsip = substr $temp[11], 4;
                $exdip = substr $temp[12], 4;
                $exsp = ' ';
                $exdp = ' ';
                $marked = $temp[17];
                $use = $temp[18];
        }
        # Only from this point, lines have the same known format/field
        # The floating fields [UNREPLIED] [ASSURED] etc are ok.

        # Store the line in a hash array for sorting
        if ( $protocol ) { # line is decoded ?
                my @record = (  'index', $index++,
                            'protocol', $protocol,
                            'expires',  $expires,
                            'status',   $status,
                            'orgsip',   $orgsip,
                            'orgdip',   $orgdip,
                            'orgsp',    $orgsp,
                            'orgdp',    $orgdp,
                            'exsip',    $exsip,
                            'exdip', 	$exdip,
                            'exsp',	$exsp,
                            'exdp',	$exdp,
                            'marked',	$marked,
                            'use',	$use);
                my $record = {};                        	# create a reference to empty hash
                %{$record} = @record;                	# populate that hash with @record
                $entries{$record->{index}} = $record; 	# add this to a hash of hashes	    
        } else { # it was not a known line
                $unknownlines .= "<tr bgcolor='${Header::table1colour}'>";
                $unknownlines .= "<td colspan='9'> unknown:$line></td></tr>";
        }
}

# Build listbox objects
my $menu_proto = &make_select ('SEE_PROTO', $cgiparams{'SEE_PROTO'}, @list_proto);
my $menu_state = &make_select ('SEE_STATE', $cgiparams{'SEE_STATE'}, @list_state);
my $menu_src   = &make_select ('SEE_SRC',   $cgiparams{'SEE_SRC'},   &get_known_ips('orgsip'));
my $menu_dest  = &make_select ('SEE_DEST',  $cgiparams{'SEE_DEST'},  &get_known_ips('orgdip'));
my $menu_mark  = &make_select ('SEE_MARK',  $cgiparams{'SEE_MARK'},  @list_mark);
my $menu_sort  = &make_select ('SEE_SORT',  $cgiparams{'SEE_SORT'},  @list_sort);

&Header::showhttpheaders();
&Header::openpage($Lang::tr{'connections'}, 1, '');
&Header::openbigbox('100%', 'left');
&Header::openbox('100%', 'left', $Lang::tr{'connection tracking'});

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
<br></br>
<table width='100%'>
<tr><td align='center'><font size=2>$Lang::tr{'protocol'}</font></td>
    <td align='center'><font size=2>$Lang::tr{'expires'}<br></br>($Lang::tr{'seconds'})</font></td>
    <td align='center'><font size=2>$Lang::tr{'connection'}<br></br>$Lang::tr{'status'}</font></td>
    <td align='center'><font size=2>$Lang::tr{'original'}<br></br>$Lang::tr{'source ip and port'}</font></td>
    <td align='center'><font size=2>$Lang::tr{'original'}<br></br>$Lang::tr{'dest ip and port'}</font></td>
    <td align='center'><font size=2>$Lang::tr{'expected'}<br></br>$Lang::tr{'source ip and port'}</font></td>
    <td align='center'><font size=2>$Lang::tr{'expected'}<br></br>$Lang::tr{'dest ip and port'}</font></td>
    <td align='center'><font size=2>$Lang::tr{'marked'}</font></td>
</tr>
<tr>
    <td align='center'>$menu_proto</td>
    <td>&nbsp;</td>
    <td align='center'>$menu_state</td>
    <td align='center'>$menu_src</td>
    <td align='center'>$menu_dest</td>
    <td align='center' colspan='2'></td>
    <td align='center'>$menu_mark</td>
</tr>
<tr>
    <td align='center' colspan='8'></td>
</tr>
<tr>
    <td align='center' colspan='8'><input type='submit' value='Aktualisieren' /></td>
</tr>

END
;

foreach my $entry (sort sort_entries keys %entries) {
        my $orgsipcolour = &ipcolour( $entries{$entry}->{orgsip} );
        my $orgdipcolour = &ipcolour( $entries{$entry}->{orgdip} );
        my $exsipcolour  = &ipcolour( $entries{$entry}->{exsip} );
        my $exdipcolour  = &ipcolour( $entries{$entry}->{exdip} );
	print <<END
        <tr bgcolor='${Header::table1colour}'>
        <td align='center'><font size=2>$entries{$entry}->{protocol}</font></td>
        <td align='center'><font size=2>$entries{$entry}->{expires}</font></td>
        <td align='center'><font size=2>$entries{$entry}->{status}</font></td>
        <td align='center' bgcolor='$orgsipcolour'>
            <a href='/cgi-bin/ipinfo.cgi?ip=$entries{$entry}->{orgsip}'>
            <font color='#FFFFFF' size=2>$entries{$entry}->{orgsip}</font>
            </a><font color='#FFFFFF' size=2>:$entries{$entry}->{orgsp}</font></td>
        <td align='center' bgcolor='$orgdipcolour'>
            <a href='/cgi-bin/ipinfo.cgi?ip=$entries{$entry}->{orgdip}'>
            <font color='#FFFFFF' size=2>$entries{$entry}->{orgdip}</font>
            </a><font color='#FFFFFF' size=2>:$entries{$entry}->{orgdp}</font></td>
        <td align='center' bgcolor='$exsipcolour'>
            <a href='/cgi-bin/ipinfo.cgi?ip=$entries{$entry}->{exsip}'>
            <font color='#FFFFFF' size=2>$entries{$entry}->{exsip}</font>
            </a><font color='#FFFFFF' size=2>:$entries{$entry}->{exsp}</font></td>
        <td align='center' bgcolor='$exdipcolour'>
            <a href='/cgi-bin/ipinfo.cgi?ip=$entries{$entry}->{exdip}'>
            <font color='#FFFFFF' size=2>$entries{$entry}->{exdip}</font>
            </a><font color='#FFFFFF' size=2>:$entries{$entry}->{exdp}</font></td>
        <td align='center'><font size=2>$entries{$entry}->{marked}</font></td>
        </tr>
END
;
}

print "$unknownlines</table></form>";

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
