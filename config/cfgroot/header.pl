# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
# Copyright (C) 2002 Alex Hudson - getcgihash() rewrite
# Copyright (C) 2002 Bob Grant <bob@cache.ucr.edu> - validmac()
# Copyright (c) 2002/04/13 Steve Bootes - add alias section, helper functions
# Copyright (c) 2002/08/23 Mark Wormgoor <mark@wormgoor.com> validfqdn()
# Copyright (c) 2003/09/11 Darren Critchley <darrenc@telus.net> srtarray()
#
# $Id: header.pl,v 1.34.2.67 2005/10/03 20:01:05 gespinasse Exp $
#

package Header;

use strict;
use CGI();
use Time::Local;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';


$Header::pagecolour = '#ffffff';	# never used, will be removed
$Header::tablecolour = '#FFFFFF';	# never used, will be removed
$Header::bigboxcolour = '#F6F4F4';	# never used, will be removed
$Header::boxcolour = '#EAE9EE';		# only header.pl, ? move in css ?
$Header::bordercolour = '#000000';	# never used, will be removed
$Header::table1colour = '#C0C0C0';
$Header::table2colour = '#F2F2F2';
$Header::colourred = '#993333';
$Header::colourorange = '#FF9933';
$Header::colouryellow = '#FFFF00';
$Header::colourgreen = '#339933';
$Header::colourblue = '#333399';
$Header::colourfw = '#000000';		# only connections.cgi
$Header::colourvpn = '#990099';		# only connections.cgi
$Header::colourerr = '#FF0000';		# only header.pl, many scripts use colourred for warnings messages
$Header::viewsize = 150;
my %menu = ();
my $hostnameintitle = 0;
our $javascript = 1;

### Initialize menu
sub genmenu
{
    ### Initialize environment
    my %ethsettings = ();
    &General::readhash("${General::swroot}/ethernet/settings", \%ethsettings);

    %{$menu{'1.system'}}=(
		'contents' =>  $Lang::tr{'alt system'},
		'uri' => '',
		'statusText' => "IPCop $Lang::tr{'alt system'}",
		'subMenu' =>   [[ $Lang::tr{'alt home'} , '/cgi-bin/index.cgi', "IPCop $Lang::tr{'alt home'}" ],
				[ $Lang::tr{'updates'} , '/cgi-bin/updates.cgi', "IPCop $Lang::tr{'updates'}" ],
				[ $Lang::tr{'sspasswords'} , '/cgi-bin/changepw.cgi', "IPCop $Lang::tr{'sspasswords'}" ],
				[ $Lang::tr{'ssh access'} , '/cgi-bin/remote.cgi', "IPCop $Lang::tr{'ssh access'}" ],
				[ $Lang::tr{'gui settings'} , '/cgi-bin/gui.cgi', "IPCop $Lang::tr{'gui settings'}" ],
				[ $Lang::tr{'backup'} , '/cgi-bin/backup.cgi', "IPCop $Lang::tr{'backup'} / $Lang::tr{'restore'}" ],
				[ $Lang::tr{'shutdown'} , '/cgi-bin/shutdown.cgi', "IPCop $Lang::tr{'shutdown'} / $Lang::tr{'reboot'}" ],
				[ $Lang::tr{'credits'} , '/cgi-bin/credits.cgi', "IPCop $Lang::tr{'credits'}" ]]
    );
    %{$menu{'2.status'}}=(
		'contents' =>  $Lang::tr{'status'},
		'uri' => '',
		'statusText' => "IPCop $Lang::tr{'status information'}",
		'subMenu' =>   [[ $Lang::tr{'sssystem status'} , '/cgi-bin/status.cgi', "IPCop $Lang::tr{'system status information'}" ],
				[ $Lang::tr{'ssnetwork status'} , '/cgi-bin/netstatus.cgi', "IPCop $Lang::tr{'network status information'}" ],
				[ $Lang::tr{'system graphs'} , '/cgi-bin/graphs.cgi', "IPCop $Lang::tr{'system graphs'}" ],
				[ $Lang::tr{'sstraffic graphs'} , '/cgi-bin/graphs.cgi?graph=network', "IPCop $Lang::tr{'network traffic graphs'}" ],
				[ $Lang::tr{'ssproxy graphs'} , '/cgi-bin/proxygraphs.cgi', "IPCop $Lang::tr{'proxy access graphs'}" ],
				[ $Lang::tr{'connections'} , '/cgi-bin/connections.cgi', "IPCop $Lang::tr{'connections'}" ]]
    );
    %{$menu{'3.network'}}=(
		'contents' =>  $Lang::tr{'network'},
		'uri' => '',
		'statusText' => "IPCop $Lang::tr{'network configuration'}",
		'subMenu' =>   [[ $Lang::tr{'alt dialup'} , '/cgi-bin/pppsetup.cgi', "IPCop $Lang::tr{'dialup settings'}" ],
				[ $Lang::tr{'upload'} , '/cgi-bin/upload.cgi', $Lang::tr{'firmware upload'} ],
				[ $Lang::tr{'modem'} , '/cgi-bin/modem.cgi', "IPCop $Lang::tr{'modem configuration'}" ],
				[ $Lang::tr{'aliases'} , '/cgi-bin/aliases.cgi', "IPCop $Lang::tr{'external aliases configuration'}" ]]
    );
    %{$menu{'4.services'}}=(
		'contents' =>  $Lang::tr{'alt services'},
		'uri' => '',
		'statusText' => "IPCop $Lang::tr{'alt services'}",
		'subMenu' =>   [[ $Lang::tr{'proxy'} , '/cgi-bin/proxy.cgi', "IPCop $Lang::tr{'web proxy configuration'}" ],
				[ $Lang::tr{'dhcp server'} , '/cgi-bin/dhcp.cgi', "IPCop $Lang::tr{'dhcp configuration'}" ],
				[ $Lang::tr{'dynamic dns'} , '/cgi-bin/ddns.cgi', "IPCop $Lang::tr{'dynamic dns client'}" ],
				[ $Lang::tr{'edit hosts'} , '/cgi-bin/hosts.cgi', "IPCop $Lang::tr{'host configuration'}" ],
				[ $Lang::tr{'time server'} , '/cgi-bin/time.cgi', "IPCop $Lang::tr{'time server'}" ],
				[ $Lang::tr{'traffic shaping'} , '/cgi-bin/shaping.cgi', "IPCop $Lang::tr{'traffic shaping settings'}" ],
				[ $Lang::tr{'intrusion detection'} , '/cgi-bin/ids.cgi', "IPCop $Lang::tr{'intrusion detection system'} (Snort)" ]]
    );
    %{$menu{'5.firewall'}}=(
		'contents' =>  $Lang::tr{'firewall'},
		'uri' => '',
		'statusText' => "IPCop $Lang::tr{'firewall'}",
		'subMenu' =>   [[ $Lang::tr{'ssport forwarding'} , '/cgi-bin/portfw.cgi', "IPCop $Lang::tr{'port forwarding configuration'}" ],
				[ $Lang::tr{'external access'} , '/cgi-bin/xtaccess.cgi', "IPCop $Lang::tr{'external access configuration'}" ],
				[ $Lang::tr{'ssdmz pinholes'} , '/cgi-bin/dmzholes.cgi', "IPCop $Lang::tr{'dmz pinhole configuration'}" ],
				[ $Lang::tr{'blue access'} , '/cgi-bin/wireless.cgi', "IPCop $Lang::tr{'blue access'}" ]
				,[ $Lang::tr{'options fw'} , '/cgi-bin/optionsfw.cgi', "IPCop $Lang::tr{'options fw'}" ]
			       ]
    );
    %{$menu{'6.vpns'}}=(
		'contents' =>  $Lang::tr{'alt vpn'},
		'uri' => '',
		'statusText' => "IPCop $Lang::tr{'virtual private networking'}",
		'subMenu' =>   [[ $Lang::tr{'alt vpn'} , '/cgi-bin/vpnmain.cgi', "IPCop $Lang::tr{'virtual private networking'}"]]
    );
    %{$menu{'7.mainlogs'}}=(
		'contents' =>  $Lang::tr{'alt logs'},
		'uri' => '',
		'statusText' => "IPCop $Lang::tr{'alt logs'}",
		'subMenu' =>   [[ $Lang::tr{'log settings'} , '/cgi-bin/logs.cgi/config.dat', "IPCop $Lang::tr{'log settings'}" ],
				[ $Lang::tr{'log summary'} , '/cgi-bin/logs.cgi/summary.dat', "IPCop $Lang::tr{'log summary'}" ],
				[ $Lang::tr{'proxy logs'} , '/cgi-bin/logs.cgi/proxylog.dat', "IPCop $Lang::tr{'proxy log viewer'}" ],
				[ $Lang::tr{'firewall logs'} , '/cgi-bin/logs.cgi/firewalllog.dat', "IPCop $Lang::tr{'firewall log viewer'}" ],
				[ $Lang::tr{'ids logs'} , '/cgi-bin/logs.cgi/ids.dat', "IPCop $Lang::tr{'intrusion detection system log viewer'}" ],
				[ $Lang::tr{'system logs'} , '/cgi-bin/logs.cgi/log.dat', "IPCop $Lang::tr{'system log viewer'}" ]]
    );
    if (! $ethsettings{'BLUE_DEV'}) {
	splice (@{$menu{'5.firewall'}{'subMenu'}}, 3, 1);
    }
    if (! $ethsettings{'BLUE_DEV'} && ! $ethsettings{'ORANGE_DEV'}) {
	splice (@{$menu{'5.firewall'}{'subMenu'}}, 2, 1);
    }
    unless ( $ethsettings{'CONFIG_TYPE'} =~ /^(2|3|6|7)$/ && $ethsettings{'RED_TYPE'} eq 'STATIC' ) {
	splice (@{$menu{'3.network'}{'subMenu'}}, 3, 1);
    }
    if ( ! -e "${General::swroot}/snort/enable" && ! -e "${General::swroot}/snort/enable_blue" &&
	! -e "${General::swroot}/snort/enable_green" && ! -e "${General::swroot}/snort/enable_orange") {
	splice (@{$menu{'7.mainlogs'}{'subMenu'}}, 4, 1);
    }
    if ( ! -e "${General::swroot}/proxy/enable" && ! -e "${General::swroot}/proxy/enable_blue" ) {
	splice (@{$menu{'2.status'}{'subMenu'}}, 4, 1);
	splice (@{$menu{'7.mainlogs'}{'subMenu'}}, 2, 1);
    }
}

sub showhttpheaders
{
    ### Make sure this is an SSL request
    if ($ENV{'SERVER_ADDR'} && $ENV{'HTTPS'} ne 'on') {
	print "Status: 302 Moved\r\n";
	print "Location: https://$ENV{'SERVER_ADDR'}:445/$ENV{'PATH_INFO'}\r\n\r\n";
	exit 0;
    } else {
	print "Pragma: no-cache\n";
	print "Cache-control: no-cache\n";
	print "Connection: close\n";
	print "Content-type: text/html\n\n";
    }
}

sub showjsmenu
{
    my $c1 = 1;

    print "    <script type='text/javascript'>\n";
    print "    domMenu_data.setItem('domMenu_main', new domMenu_Hash(\n";

    foreach my $k1 ( sort keys %menu ) {
	my $c2 = 1;
	if ($c1 > 1) {
	    print "    ),\n";
	}
	print "    $c1, new domMenu_Hash(\n";
	print "\t'contents', '" . &cleanhtml($menu{$k1}{'contents'}) . "',\n";
	print "\t'uri', '$menu{$k1}{'uri'}',\n";
	$menu{$k1}{'statusText'} =~  s/'/\\\'/g;
	print "\t'statusText', '$menu{$k1}{'statusText'}',\n";
	foreach my $k2 ( @{$menu{$k1}{'subMenu'}} ) {
	    print "\t    $c2, new domMenu_Hash(\n";
	    print "\t\t'contents', '" . &cleanhtml(@{$k2}[0])  . "',\n";
	    print "\t\t'uri', '@{$k2}[1]',\n";
	    @{$k2}[2] =~ s/'/\\\'/g;
	    print "\t\t'statusText', '@{$k2}[2]'\n";
	    if ( $c2 <= $#{$menu{$k1}{'subMenu'}} ) {
		print "\t    ),\n";
	    } else {
		print "\t    )\n";
	    }
	    $c2++;
	}
	$c1++;
    }
    print "    )\n";
    print "    ));\n\n";

    print <<EOF
    domMenu_settings.setItem('domMenu_main', new domMenu_Hash(
	'menuBarWidth', '0%',
	'menuBarClass', 'ipcop_menuBar',
	'menuElementClass', 'ipcop_menuElement',
	'menuElementHoverClass', 'ipcop_menuElementHover',
	'menuElementActiveClass', 'ipcop_menuElementHover',
	'subMenuBarClass', 'ipcop_subMenuBar',
	'subMenuElementClass', 'ipcop_subMenuElement',
	'subMenuElementHoverClass', 'ipcop_subMenuElementHover',
	'subMenuElementActiveClass', 'ipcop_subMenuElementHover',
	'subMenuMinWidth', 'auto',
	'distributeSpace', false,
	'openMouseoverMenuDelay', 0,
	'openMousedownMenuDelay', 0,
	'closeClickMenuDelay', 0,
	'closeMouseoutMenuDelay', -1
    ));
    </script>
EOF
    ;
}

sub showmenu
{
    if ($javascript) {print "<noscript>";}
    print "<table cellpadding='0' cellspacing='0' border='0'>\n";
    print "<tr>\n";

    foreach my $k1 ( sort keys %menu ) {
	print "<td class='ipcop_menuElementTD'><a href='" . @{@{$menu{$k1}{'subMenu'}}[0]}[1] . "' class='ipcop_menuElementNoJS'>";
	print $menu{$k1}{'contents'} . "</a></td>\n";
    }
    print "</tr></table>\n";
    if ($javascript) {print "</noscript>";}
}

sub showsubsection
{
    my $location = $_[0];
    my $c1 = 0;

    if ($javascript) {print "<noscript>";}
    print "<table width='100%' cellspacing='0' cellpadding='5' border='0'>\n";
    print "<tr><td style='background-color: $Header::boxcolour;' width='53'><img src='/images/null.gif' width='43' height='1' alt='' /></td>\n";
    print "<td style='background-color: $Header::boxcolour;' align='left' width='100%'>";
    my @URI=split ('\?',  $ENV{'REQUEST_URI'} );

    foreach my $k1 ( keys %menu ) {
	
	if ($menu{$k1}{'contents'} eq $location) {
	    foreach my $k2 ( @{$menu{$k1}{'subMenu'}} ) {
		if ($c1 > 0) {
		    print " | ";
		}
		if (@{$k2}[1] eq "$URI[0]\?$URI[1]" || (@{$k2}[1] eq $URI[0] && length($URI[1]) == 0)) {
		#if (@{$k2}[1] eq "$URI[0]") {
		    print "<b>@{$k2}[0]</b>";
		} else {
		    print "<a href='@{$k2}[1]'>@{$k2}[0]</a>";
		}
		$c1++;
	    }
	}
    }
    print "</td></tr></table>\n";
    if ($javascript) { print "</noscript>";}
}

sub openpage
{
    my $title = $_[0];
    my $menu = $_[1];
    my $extrahead = $_[2];

    ### Initialize environment
    my %settings = ();
    &General::readhash("${General::swroot}/main/settings", \%settings);

    if ($settings{'JAVASCRIPT'} eq 'off') {
	$javascript = 0;
    } else {
	$javascript = 1;
    }

    if ($settings{'WINDOWWITHHOSTNAME'} eq 'on') {
        $hostnameintitle = 1;
    } else {
        $hostnameintitle = 0;
    }

    print <<END
<!DOCTYPE html 
     PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html><head>
END
    ;
    print "    <title>";
    if ($hostnameintitle) {
        print "$settings{'HOSTNAME'}.$settings{'DOMAINNAME'} - $title"; 
    } else {
        print "IPCop - $title";
    }
    print "</title>\n";

    print <<END
    $extrahead
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <link rel="shortcut icon" href="/favicon.ico" />
    <style type="text/css">\@import url(/include/ipcop.css);</style>
END
    ;
    if ($javascript) {
	print "<script type='text/javascript' src='/include/domMenu.js'></script>\n";
	&genmenu();
	&showjsmenu();
    } else {
	&genmenu();
    }

    my $location = '';
    my $sublocation = '';
    my @URI=split ('\?',  $ENV{'REQUEST_URI'} );
    foreach my $k1 ( keys %menu ) {
	my $temp = $menu{$k1}{'contents'};
	foreach my $k2 ( @{$menu{$k1}{'subMenu'}} ) {
	    if ( @{$k2}[1] eq $URI[0] ) {
		$location = $temp;
		$sublocation = @{$k2}[0];
	    }
	}
    }

    my @cgigraphs = split(/graph=/,$ENV{'QUERY_STRING'});
    if (defined ($cgigraphs[1])){ 
	if ($cgigraphs[1] =~ /(GREEN|BLUE|ORANGE|RED|network)/) {
		$location = $Lang::tr{'status'};
		$sublocation = $Lang::tr{'sstraffic graphs'};
	}
	if ($cgigraphs[1] =~ /(cpu|memory|swap|disk)/) {
		$location = $Lang::tr{'status'};
		$sublocation = $Lang::tr{'system graphs'};
	}
    }
    if ($ENV{'QUERY_STRING'} =~ /(ip)/) {
        $location = $Lang::tr{'alt logs'};
	$sublocation = "WHOIS";
    }

    if ($javascript) {
	    print <<END
	    <script type="text/javascript">
	    document.onmouseup = function()
	    {
		domMenu_deactivate('domMenu_main');
	    }
	    </script>
	    </head>

	    <body onload="domMenu_activate('domMenu_main');">
END
	    ;
    } else {
	print "</head>\n\n<body>\n";
    }

    print <<END
<!-- IPCOP HEADER -->
    <table width='100%' cellpadding='0' cellspacing='0'>
    <col width='53' />
    <col />
    <tr><td><img src='/images/null.gif' width='53' height='27' alt='' /></td>
	<td valign='bottom'><table width='100%' cellspacing='0' border='0'>
	    <col width='5' />
	    <col width='175' />
	    <col />
	    <tr><td><img src='/images/null.gif' width='5' height='1' alt='' /></td>
		<td class="ipcop_menuLocationMain" valign='bottom'>$location</td>
		<td class="ipcop_menuLocationSub"  valign='bottom'>$sublocation</td>
	    </tr></table>
	</td></tr>
    <tr><td valign='bottom' class='ipcop_Version'>
	    <img src='/images/null.gif' width='1' height='29' alt='' />${General::version}</td>
	<td valign='bottom'>
END
    ;
    if ($menu == 1) {
	if ($javascript) {
	    print "<div id='domMenu_main'></div>\n";
	}
	&showmenu();
    }
    print "	</td></tr></table>\n";
    &showsubsection($location);
    print "<!-- IPCOP CONTENT -->\n";
}

sub closepage
{
	print <<END
<!-- IPCOP FOOTER -->
    <table width='100%' border='0'>
    <tr><td valign='bottom'><img src='/images/bounceback.png' width='248' height='80' alt='' /></td>
	<td align='center' valign='bottom'>
END
	;
	my $status = &connectionstatus();
	print "$status<br />\n"; 
	print `/usr/bin/uptime`;

	print <<END
	</td>
	<td valign='bottom'><a href='http://sf.net/projects/ipcop/' target='_blank'><img src='/images/sflogo.png' width='88' height='31' alt='Sourceforge logo' /></a></td>
    </tr></table>
</body></html>
END
	;
}

sub openbigbox
{
	my $width = $_[0];
	my $align = $_[1];
	my $sideimg = $_[2];
        my $errormessage = $_[3];
	my $bgcolor;

	if ($errormessage) {
		$bgcolor = "style='background-color: $Header::colourerr;'";
	} else {
		$bgcolor = '';
	}

	print "<table width='100%' border='0'>\n";
	if ($sideimg) {
	    print "<tr><td valign='top'><img src='/images/$sideimg' width='65' height='345' alt='' /></td>\n";
	} else {
	    print "<tr>\n";
	}
	print "<td valign='top' align='center'><table width='$width' $bgcolor cellspacing='0' cellpadding='10' border='0'>\n";
        print "<tr><td><img src='/images/null.gif' width='1' height='365' alt='' /></td>\n";
	print "<td align='$align' valign='top'>\n";
}

sub closebigbox
{
	print "</td></tr></table></td></tr></table>\n" 
}

sub openbox
{
	my $width = $_[0];
	my $align = $_[1];
	my $caption = $_[2];

	print <<END
	<table cellspacing="0" cellpadding="0" width="$width" border="0">
	    <col width='12' />
	    <col width='18' />
	    <col width='100%' />
	    <col width='152' />
	    <col width='11' />
	
	    <tr><td width='12'  ><img src='/images/null.gif' width='12'  height='1' alt='' /></td>
		<td width='18'  ><img src='/images/null.gif' width='18'  height='1' alt='' /></td>
		<td width='100%'><img src='/images/null.gif' width='400' height='1' alt='' /></td>
		<td width='152' ><img src='/images/null.gif' width='152' height='1' alt='' /></td>
		<td width='11'  ><img src='/images/null.gif' width='11'   height='1' alt='' /></td></tr>
	    <tr><td colspan='2' ><img src='/images/boxtop1.png' width='30' height='53' alt='' /></td>
		<td style='background: url(/images/boxtop2.png);'>
END
	;
	if ($caption) { print "<b>$caption</b>\n"; } else { print "&nbsp;"; }
	print <<END
		</td>
		<td colspan='2'><img src='/images/boxtop3.png' width='163' height='53' alt='' /></td></tr>
	    <tr><td style='background: url(/images/boxleft.png);'><img src='/images/null.gif' width='12' height='1' alt='' /></td>
		<td colspan='3' style='background-color: $Header::boxcolour;'>
		<table width='100%' cellpadding='5'><tr><td align="$align" valign='top'>
END
	;
}

sub closebox
{
	print <<END
		</td></tr></table></td>
                <td style='background: url(/images/boxright.png);'><img src='/images/null.gif' width='11' height='1' alt='' /></td></tr>
            <tr><td style='background: url(/images/boxbottom1.png);background-repeat:no-repeat;'><img src='/images/null.gif' width='12' height='14' alt='' /></td>
                <td style='background: url(/images/boxbottom2.png);background-repeat:repeat-x;' colspan='3'><img src='/images/null.gif' width='1' height='14' alt='' /></td>
                <td style='background: url(/images/boxbottom3.png);background-repeat:no-repeat;'><img src='/images/null.gif' width='11' height='14' alt='' /></td></tr>
        </table>
END
	;
}

sub getcgihash {
	my ($hash, $params) = @_;
	my $cgi = CGI->new ();
	return if ($ENV{'REQUEST_METHOD'} ne 'POST');
	if (!$params->{'wantfile'}) {
		$CGI::DISABLE_UPLOADS = 1;
		$CGI::POST_MAX        = 512 * 1024;
	} else {
		$CGI::POST_MAX = 10 * 1024 * 1024;
	}

	$cgi->referer() =~ m/^https?\:\/\/([^\/]+)/;
	my $referer = $1;
	$cgi->url() =~ m/^https?\:\/\/([^\/]+)/;
	my $servername = $1;
	return if ($referer ne $servername);

	### Modified for getting multi-vars, split by |
	my %temp = $cgi->Vars();
        foreach my $key (keys %temp) {
		$hash->{$key} = $temp{$key};
		$hash->{$key} =~ s/\0/|/g;
		$hash->{$key} =~ s/^\s*(.*?)\s*$/$1/;
        }

	if (($params->{'wantfile'})&&($params->{'filevar'})) {
		$hash->{$params->{'filevar'}} = $cgi->upload
						($params->{'filevar'});
	}
	return;
}

sub cleanhtml
{
	my $outstring =$_[0];
	$outstring =~ tr/,/ / if not defined $_[1] or $_[1] ne 'y';
	$outstring =~ s/&/&amp;/g;
	$outstring =~ s/\'/&#039;/g;
	$outstring =~ s/\"/&quot;/g;
	$outstring =~ s/</&lt;/g;
	$outstring =~ s/>/&gt;/g;
	return $outstring;
}

sub connectionstatus
{
    my %pppsettings = ();
    my %netsettings = ();
    my $iface='';

    $pppsettings{'PROFILENAME'} = 'None';
    &General::readhash("${General::swroot}/ppp/settings", \%pppsettings);
    &General::readhash("${General::swroot}/ethernet/settings", \%netsettings);

    my $profileused='';
    if ( ! ( $netsettings{'CONFIG_TYPE'} =~ /^(2|3|6|7)$/ && $netsettings{'RED_TYPE'} =~ /^(DHCP|STATIC)$/ ) ) {
    	$profileused="- $pppsettings{'PROFILENAME'}";
    }

    if ( ( $pppsettings{'METHOD'} eq 'DHCP' && $netsettings{'RED_TYPE'} ne 'PPTP') 
						|| $netsettings{'RED_TYPE'} eq 'DHCP' ) {
		if (open(IFACE, "${General::swroot}/red/iface")) {
			$iface = <IFACE>;
			close IFACE;
			chomp ($iface);
			$iface =~ /([a-zA-Z0-9]*)/; $iface = $1;
		}
    }

    my ($timestr, $connstate);
    if ($netsettings{'CONFIG_TYPE'} =~ /^(0|1|4|5)$/ &&  $pppsettings{'TYPE'} =~ /^isdn/) {
	# Count ISDN channels
	my ($idmap, $chmap, $drmap, $usage, $flags, $phone);
	my @phonenumbers;
	my $count=0;

	open (FILE, "/dev/isdninfo");

	$idmap = <FILE>; chop $idmap;
	$chmap = <FILE>; chop $chmap;
	$drmap = <FILE>; chop $drmap;
	$usage = <FILE>; chop $usage;
	$flags = <FILE>; chop $flags;
	$phone = <FILE>; chop $phone;

	$phone =~ s/^phone(\s*):(\s*)//;

	@phonenumbers = split / /, $phone;

	foreach (@phonenumbers) {
		if ($_ ne '???') {
			$count++;
		}
	}
	close (FILE);

	## Connection status
	my $number;
	if ($count == 0) {
		$number = 'none!';
	} elsif ($count == 1) {
		$number = 'single';
	} else {
		$number = 'dual';
	}

	if (-e "${General::swroot}/red/active") {
		$timestr = &General::age("${General::swroot}/red/active");
		$connstate = "<span class='ipcop_StatusBig'>$Lang::tr{'connected'} - $number channel (<span class='ipcop_StatusBigRed'>$timestr</span>) $profileused</span>";
	} else {
		if ($count == 0) {
			if (-e "${General::swroot}/red/dial-on-demand") {
				$connstate = "<span class='ipcop_StatusBig'>$Lang::tr{'dod waiting'} $profileused</span>";
			} else {
				$connstate = "<span class='ipcop_StatusBig'>$Lang::tr{'idle'} $profileused</span>";
			}
		} else {
			$connstate = "<span class='ipcop_StatusBig'>$Lang::tr{'connecting'} $profileused</span>";
		}
	}
    } elsif ($netsettings{'RED_TYPE'} eq "STATIC" || $pppsettings {'METHOD'} eq 'STATIC') {
	if (-e "${General::swroot}/red/active") {
		$timestr = &General::age("${General::swroot}/red/active");
		$connstate = "<span class='ipcop_StatusBig'>$Lang::tr{'connected'} (<span class='ipcop_StatusBigRed'>$timestr</span>) $profileused</span>";
	} else {
		$connstate = "<span class='ipcop_StatusBig'>$Lang::tr{'idle'} $profileused</span>";
	}
    } elsif ( ( (-e "${General::swroot}/dhcpc/dhcpcd-$iface.pid") && $netsettings{'RED_TYPE'} ne 'PPTP' ) || 
	!system("/bin/ps -ef | /bin/grep -q '[p]ppd'") || !system("/bin/ps -ef | /bin/grep -q '[c]onnectioncheck'")) {
	if (-e "${General::swroot}/red/active") {
		$timestr = &General::age("${General::swroot}/red/active");
		if ($pppsettings{'TYPE'} =~ /^(modem|bewanadsl|conexantpciadsl|eagleusbadsl)$/) {
			my $speed;
			if ($pppsettings{'TYPE'} eq 'modem') {
				open(CONNECTLOG, "/var/log/connect.log");
				while (<CONNECTLOG>) {
					if (/CONNECT/) {
						$speed = (split / /)[6];
					}
				}
				close (CONNECTLOG);
			} elsif ($pppsettings{'TYPE'} eq 'bewanadsl') {
				$speed = `/usr/bin/unicorn_status | /bin/grep Rate | /usr/bin/cut -f2 -d ':'`;
			} elsif ($pppsettings{'TYPE'} eq 'conexantpciadsl') {
				$speed = `/bin/cat /proc/net/atm/CnxAdsl:* | /bin/grep 'Line Rates' | /bin/sed -e 's+Line Rates:   Receive+Rx+' -e 's+Transmit+Tx+'`;
			} elsif ($pppsettings{'TYPE'} eq 'eagleusbadsl') {
				$speed = `/usr/sbin/eaglestat | /bin/grep Rate`;
			}
			$connstate = "<span class='ipcop_StatusBig'>$Lang::tr{'connected'} (<span class='ipcop_StatusBigRed'>$timestr</span>) $profileused (\@$speed)</span>";
		} else {
			$connstate = "<span class='ipcop_StatusBig'>$Lang::tr{'connected'} (<span class='ipcop_StatusBigRed'>$timestr</span>) $profileused</span>";
		}
	} else {
		if (-e "${General::swroot}/red/dial-on-demand") {
		    $connstate = "<span class='ipcop_StatusBig'>$Lang::tr{'dod waiting'} $profileused</span>";
		} else {
		    $connstate = "<span class='ipcop_StatusBig'>$Lang::tr{'connecting'} $profileused</span>";
		}
	}
    } else {
	$connstate = "<span class='ipcop_StatusBig'>$Lang::tr{'idle'} $profileused</span>";
    }
    return $connstate;
}

sub speedtouchversion
{
	my $speedtouch;
	if (-f "/proc/bus/usb/devices")
	{
		$speedtouch=`/bin/cat /proc/bus/usb/devices | /bin/grep 'Vendor=06b9 ProdID=4061' | /usr/bin/cut -d ' ' -f6`;
		if ($speedtouch eq '') {
			$speedtouch= $Lang::tr{'connect the modem'};
		}
	} else {
		$speedtouch='USB '.$Lang::tr{'not running'};
	}
	return $speedtouch
}

#Sorting of allocated leases
sub CheckSortOrder {
    my %dhcpsettings = ();
    &General::readhash("${General::swroot}/dhcp/settings", \%dhcpsettings);

    if ($ENV{'QUERY_STRING'} =~ /^IPADDR|^ETHER|^HOSTNAME|^ENDTIME/ ) {
	my $newsort=$ENV{'QUERY_STRING'};
        my $act=$dhcpsettings{'SORT_LEASELIST'};
        #Default sort if unspecified 
        $act='IPADDRRev' if !defined ($act); 
        #Reverse actual ?
        if ($act =~ $newsort) {
            my $Rev='';
            if ($act !~ 'Rev') {$Rev='Rev'};
            $newsort.=$Rev
        };

        $dhcpsettings{'SORT_LEASELIST'}=$newsort;
	&General::writehash("${General::swroot}/dhcp/settings", \%dhcpsettings);
    }
}

sub PrintActualLeases
{
    our %dhcpsettings = ();
    our %entries = ();    
    
    sub leasesort {
	my $qs ='';
	if (rindex ($dhcpsettings{'SORT_LEASELIST'},'Rev') != -1)
	{
	    $qs=substr ($dhcpsettings{'SORT_LEASELIST'},0,length($dhcpsettings{'SORT_LEASELIST'})-3);
	    if ($qs eq 'IPADDR') {
		my @a = split(/\./,$entries{$a}->{$qs});
		my @b = split(/\./,$entries{$b}->{$qs});
		($b[0]<=>$a[0]) ||
		($b[1]<=>$a[1]) ||
		($b[2]<=>$a[2]) ||
	        ($b[3]<=>$a[3]);
	    }else {
	        $entries{$b}->{$qs} cmp $entries{$a}->{$qs};
	    }
        }
        else #not reverse
        {
	    $qs=$dhcpsettings{'SORT_LEASELIST'};
	    if ($qs eq 'IPADDR') {
		my @a = split(/\./,$entries{$a}->{$qs});
	        my @b = split(/\./,$entries{$b}->{$qs});
		($a[0]<=>$b[0]) ||
	        ($a[1]<=>$b[1]) ||
	        ($a[2]<=>$b[2]) ||
	        ($a[3]<=>$b[3]);
	    }else {
		$entries{$a}->{$qs} cmp $entries{$b}->{$qs};
	    }
	}
    }

    &Header::openbox('100%', 'left', $Lang::tr{'current dynamic leases'});
    print <<END
<table width='100%'>
<tr>
<td width='25%' align='center'><a href='$ENV{'SCRIPT_NAME'}?IPADDR'><b>$Lang::tr{'ip address'}</b></a></td>
<td width='25%' align='center'><a href='$ENV{'SCRIPT_NAME'}?ETHER'><b>$Lang::tr{'mac address'}</b></a></td>
<td width='20%' align='center'><a href='$ENV{'SCRIPT_NAME'}?HOSTNAME'><b>$Lang::tr{'hostname'}</b></a></td>
<td width='30%' align='center'><a href='$ENV{'SCRIPT_NAME'}?ENDTIME'><b>$Lang::tr{'lease expires'} (local time d/m/y)</b></a></td>
</tr>
END
    ;

    my ($ip, $endtime, $ether, $hostname, @record, $record);
    open(LEASES,"/var/state/dhcp/dhcpd.leases") or die "Can't open dhcpd.leases";
    while (my $line = <LEASES>) {
	next if( $line =~ /^\s*#/ );
	chomp($line);
	my @temp = split (' ', $line);

	if ($line =~ /^\s*lease/) {
	    $ip = $temp[1];
	    #All field are not necessarily read. Clear everything
	    $endtime = 0;
	    $ether = "";
	    $hostname = "";
	} elsif ($line =~ /^\s*ends never;/) {
	    $endtime = 'never';
	} elsif ($line =~ /^\s*ends/) {
	    $line =~ /(\d+)\/(\d+)\/(\d+) (\d+):(\d+):(\d+)/;
	    $endtime = timegm($6, $5, $4, $3, $2 - 1, $1 - 1900);
	} elsif ($line =~ /^\s*hardware ethernet/) {
	    $ether = $temp[2];
	    $ether =~ s/;//g;
	} elsif ($line =~ /^\s*client-hostname/) {
	    shift (@temp);
	    $hostname = join (' ',@temp);
	    $hostname =~ s/;//g;
	    $hostname =~ s/\"//g;
	} elsif ($line eq "}") {
	    @record = ('IPADDR',$ip,'ENDTIME',$endtime,'ETHER',$ether,'HOSTNAME',$hostname);
	    $record = {};                        		# create a reference to empty hash
	    %{$record} = @record;                		# populate that hash with @record
	    $entries{$record->{'IPADDR'}} = $record;   	# add this to a hash of hashes
	} #unknown format line...
    }
    close(LEASES);

    #Get sort method
    $dhcpsettings{'SORT_LEASELIST'}='IPADDR';					#default
    &General::readhash("${General::swroot}/dhcp/settings", \%dhcpsettings);	#or maybe saved !
    my $id = 0;
    foreach my $key (sort leasesort keys %entries) {

	my $hostname = &Header::cleanhtml($entries{$key}->{HOSTNAME},"y");

	if ($id % 2) {
	    print "<tr bgcolor='$Header::table1colour'>";
	}
	else {
	    print "<tr bgcolor='$Header::table2colour'>";
	}

	print <<END
<td align='center'>$entries{$key}->{IPADDR}</td>
<td align='center'>$entries{$key}->{ETHER}</td>
<td align='center'>&nbsp;$hostname </td>
<td align='center'>
END
	;

	if ($entries{$key}->{ENDTIME} eq 'never') {
	    print "$Lang::tr{'no time limit'}";
	} else {
	    my ($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $dst);
	    ($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $dst) = localtime ($entries{$key}->{ENDTIME});
	    my $enddate = sprintf ("%02d/%02d/%d %02d:%02d:%02d",$mday,$mon+1,$year+1900,$hour,$min,$sec);

	    if ($entries{$key}->{ENDTIME} < time() ){
		print "<strike>$enddate</strike>";
	    } else {
		print "$enddate";
	    }
	}
	print "</td></tr>";
	$id++;
    }

    print "</table>";
    &Header::closebox();
}

1;
