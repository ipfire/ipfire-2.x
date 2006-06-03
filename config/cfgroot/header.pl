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
package Header;

use CGI();
use Socket;
use Time::Local;

$|=1; # line buffering

$Header::revision = 'final';
$Header::swroot = '/var/ipfire';
$Header::pagecolour = '#ffffff';
#$Header::tablecolour = '#a0a0a0';
$Header::tablecolour = '#FFFFFF';
$Header::bigboxcolour = '#F6F4F4';
$Header::boxcolour = '#EAE9EE';
$Header::bordercolour = '#000000';
$Header::table1colour = '#E0E0E0';
$Header::table2colour = '#F0F0F0';
$Header::colourred = '#993333';
$Header::colourorange = '#FF9933';
$Header::colouryellow = '#FFFF00';
$Header::colourgreen = '#339933';
$Header::colourblue = '#333399';
$Header::colourovpn = '#339999';
$Header::colourfw = '#000000';
$Header::colourvpn = '#990099';
$Header::colourerr = '#FF0000';
$Header::viewsize = 150;
$Header::errormessage = '';
my %menuhash = ();
my $menu = \%menuhash;
%settings = ();
%ethsettings = ();
@URI = ();
$Header::supported=0;

### Make sure this is an SSL request
if ($ENV{'SERVER_ADDR'} && $ENV{'HTTPS'} ne 'on') {
    print "Status: 302 Moved\r\n";
    print "Location: https://$ENV{'SERVER_ADDR'}:10443/$ENV{'PATH_INFO'}\r\n\r\n";
    exit 0;
}

### Initialize environment
&readhash("${swroot}/main/settings", \%settings);
&readhash("${swroot}/ethernet/settings", \%ethsettings);
$language = $settings{'LANGUAGE'};
$hostname = $settings{'HOSTNAME'};
$hostnameintitle = 0;

### Initialize language
if ($language =~ /^(\w+)$/) {$language = $1;}

### Read English Files
if ( -d "/var/ipfire/langs/en/" ) {
    opendir(DIR, "/var/ipfire/langs/en/");
    @names = readdir(DIR) or die "Cannot Read Directory: $!\n";
    foreach $name(@names) {
        next if ($name eq ".");
        next if ($name eq "..");
        next if (!($name =~ /\.pl$/));
        require "${swroot}/langs/en/${name}";
    };
};


### Enable Language Files
if ( -d "/var/ipfire/langs/${language}/" ) {
    opendir(DIR, "/var/ipfire/langs/${language}/");
    @names = readdir(DIR) or die "Cannot Read Directory: $!\n";
    foreach $name(@names) {
        next if ($name eq ".");
        next if ($name eq "..");
        next if (!($name =~ /\.pl$/));
        require "${swroot}/langs/${language}/${name}";
    };
};


require "${swroot}/langs/en.pl";
require "${swroot}/langs/${language}.pl";

sub orange_used () {
    if ($ethsettings{'CONFIG_TYPE'} =~ /^[1357]$/) {
	return 1;
    }
    return 0;
}

sub blue_used () {
    if ($ethsettings{'CONFIG_TYPE'} =~ /^[4567]$/) {
	return 1;
    }
    return 0;
}

sub is_modem {
    if ($ethsettings{'CONFIG_TYPE'} =~ /^[0145]$/) {
	return 1;
    }
    return 0;
}

### Initialize menu
sub genmenu {
    my %subsystemhash = ();
    my $subsystem = \%subsystemhash;

    $subsystem->{'01.home'} = {
				'caption' => $tr{'alt home'},
				'uri' => '/cgi-bin/index.cgi',
				'title' => "$tr{'alt home'}",
				'enabled' => 1,
				};
    $subsystem->{'02.passwords'} = {
				'caption' => $tr{'sspasswords'},
				'uri' => '/cgi-bin/changepw.cgi',
				'title' => "$tr{'sspasswords'}",
				'enabled' => 1,
				};
    $subsystem->{'03.ssh'} = {
				'caption' => $tr{'ssh access'},
				'uri' => '/cgi-bin/remote.cgi',
				'title' => "$tr{'ssh access'}",
				'enabled' => 1,
				};
    $subsystem->{'04.gui'} = {
				'caption' => $tr{'gui settings'},
				'uri' => '/cgi-bin/gui.cgi',
				'title' => "$tr{'gui settings'}",
				'enabled' => 1,
				};
    $subsystem->{'05.shutdown'} = {
				'caption' => $tr{'shutdown'},
				'uri' => '/cgi-bin/shutdown.cgi',
				'title' => "$tr{'shutdown'} / $tr{'reboot'}",
				'enabled' => 1,
				};
    $subsystem->{'99.credits'} = {
				'caption' => $tr{'credits'},
				'uri' => '/cgi-bin/credits.cgi',
				'title' => "$tr{'credits'}",
				'enabled' => 1,
				};

    my %substatushash = ();
    my $substatus = \%substatushash;
    $substatus->{'01.systemstatus'} = {
				 'caption' => $tr{'sssystem status'},
				 'uri' => '/cgi-bin/status.cgi',
				 'title' => "$tr{'system status information'}",
				 'enabled' => 1,
				 };
    $substatus->{'02.networkstatus'} = {
				'caption' => $tr{'ssnetwork status'},
				'uri' => '/cgi-bin/netstatus.cgi',
				'title' => "$tr{'network status information'}",
				'enabled' => 1,
				};
    $substatus->{'03.systemgraphs'} = {
				'caption' => $tr{'system graphs'},
				'uri' => '/cgi-bin/graphs.cgi',
				'novars' => 1,
				'title' => "$tr{'system graphs'}",
				'enabled' => 1,
				};
    $substatus->{'04.trafficgraphs'} = {
				'caption' => $tr{'sstraffic graphs'},
				'uri' => '/cgi-bin/graphs.cgi',
				'vars' => 'graph=network',
				'title' => "$tr{'network traffic graphs'}",
				'enabled' => 1,
				};
    $substatus->{'05.proxygraphs'} = {
				'caption' => $tr{'ssproxy graphs'},
				'uri' => '/cgi-bin/proxygraphs.cgi',
				'title' => "$tr{'proxy access graphs'}",
				'enabled' => 1,
				};
    $substatus->{'06.connections'} = {
				'caption' => $tr{'connections'},
				'uri' => '/cgi-bin/connections.cgi',
				'title' => "$tr{'connections'}",
				'enabled' => 1,
				};
    $substatus->{'99.iptfilters'} = {
				'caption' => $tr{'iptfilters iptable rules'},
				'uri' => '/cgi-bin/iptfilters.cgi',
				'title' => "$tr{'iptfilters iptable rules'}",
				'enabled' => 1,
				};

    my %subnetworkhash = ();
    my $subnetwork = \%subnetworkhash;

    $subnetwork->{'01.dialup'} = {
				  'caption' => $tr{'alt dialup'},
				  'uri' => '/cgi-bin/pppsetup.cgi',
				  'title' => "$tr{'dialup settings'}",
				  'enabled' => 1,
				  };
    $subnetwork->{'02.hosts'} = {
				 'caption' => $tr{'edit hosts'},
				 'uri' => '/cgi-bin/hosts.cgi',
				 'title' => "$tr{'host configuration'}",
				 'enabled' => 1,
				 };
    $subnetwork->{'03.upload'} = {
				  'caption' => $tr{'upload'},
				  'uri' => '/cgi-bin/upload.cgi',
				  'title' => "$tr{'firmware upload'}",
				  'enabled' => 0,
				  };
    $subnetwork->{'04.aliases'} = {
				  'caption' => $tr{'aliases'},
				  'uri' => '/cgi-bin/aliases.cgi',
				  'title' => "$tr{'external aliases configuration'}",
				  'enabled' => 1,
				  };
    $subnetwork->{'05.nettraf'} = {
				  'caption' => $tr{'sstraffic'},
			     	  'uri' => '/cgi-bin/traffic.cgi',
			     	  'title' => "$tr{'sstraffic'}",
			         'enabled' => 1,
			   	  };
    $subnetwork->{'06.fwhits'} = {
				  'caption' => 'Firewallhits',
			     	  'uri' => '/cgi-bin/fwhits.cgi',
			     	  'title' => "IPFire Firewallhits",
			         'enabled' => 1,
			   	  };
    $subnetwork->{'07.openvpn'} = {
				  'caption' => 'OpenVPN',
			     	  'uri' => '/cgi-bin/ovpnmain.cgi',
			     	  'title' => "$tr{'virtual private networking'}",
			         'enabled' => 1,
			   	  };
    $subnetwork->{'08.ipsec'} = {
				  'caption' => 'IPSec',
			     	  'uri' => '/cgi-bin/vpnmain.cgi',
			     	  'title' => "$tr{'virtual private networking'}",
			     	  'enabled' => 1,
			 	  };


    my %subserviceshash = ();
    my $subservices = \%subserviceshash;

    $subservices->{'01.proxy'} = {'caption' => $tr{'proxy'},
			        'uri' => '/cgi-bin/proxy.cgi',
			        'title' => "HTTP: $tr{'web proxy configuration'}",
			        'enabled' => 1,
			        };
    $subservices->{'02.dhcp'} = {'caption' => $tr{'dhcp server'},
				 'uri' => '/cgi-bin/dhcp.cgi',
				 'title' => "$tr{'dhcp configuration'}",
				 'enabled' => 1,
				 };
    $subservices->{'03.dyndns'} = {'caption' => $tr{'dynamic dns'},
				'uri' => '/cgi-bin/ddns.cgi',
				'title' => "$tr{'dynamic dns client'}",
				'enabled' => 1,
				};
    $subservices->{'04.time'} = {'caption' => $tr{'time server'},
				'uri' => '/cgi-bin/time.cgi',
				'title' => "$tr{'time server'}",
				'enabled' => 1,
				};
    $subservices->{'05.qos'} = {'caption' => 'Quality of Service',
				'uri' => '/cgi-bin/qos.cgi',
				'title' => "$tr{'traffic shaping settings'}",
				'enabled' => 1,
				};
    $subservices->{'06.ids'} = {'caption' => $tr{'intrusion detection'},
				'enabled' => 1,
				'uri' => '/cgi-bin/ids.cgi',
				'title' => "$tr{'intrusion detection system'} (Snort)",
				};


    my %subfirewallhash = ();
    my $subfirewall = \%subfirewallhash;

    
    $subfirewall->{'01.dnat'} = {
				 'caption' => $tr{'ssport forwarding'},
				 'uri' => '/cgi-bin/portfw.cgi',
				 'title' => "$tr{'port forwarding configuration'}",
				 'enabled' => 1,
				 };
    $subfirewall->{'02.xtaccess'} = {
				 'caption' => $tr{'external access'},
				 'uri' => '/cgi-bin/xtaccess.cgi',
				 'title' => "$tr{'external access configuration'}",
				 'enabled' => 1,
				 };
    $subfirewall->{'03.dmz'} = {
				'caption' => $tr{'ssdmz pinholes'},
				'uri' => '/cgi-bin/dmzholes.cgi',
				'title' => "$tr{'dmz pinhole configuration'}",
				'enabled' => 1,
				 };
    $subfirewall->{'04.outgoing'} = {
				'caption' => $tr{'outgoing firewall'},
				'uri' => '/cgi-bin/outgoingfw.cgi',
				'title' => "$tr{'outgoing firewall'}",
				'enabled' => 1,
				};
    
    my %sublogshash = ();
    my $sublogs = \%sublogshash;

    $sublogs->{'01.summary'} = {'caption' => $tr{'log summary'},
				 'uri' => '/cgi-bin/logs.cgi/summary.dat',
				 'title' => "$tr{'log summary'}",
				 'enabled' => 1
				 };
    $sublogs->{'02.settings'} = {'caption' => $tr{'log settings'},
				 'uri' => '/cgi-bin/logs.cgi/config.dat',
				 'title' => "$tr{'log settings'}",
				 'enabled' => 1
				 };
    $sublogs->{'03.proxy'} = {'caption' => $tr{'proxy logs'},
				 'uri' => '/cgi-bin/logs.cgi/proxylog.dat',
				 'title' => "$tr{'proxy log viewer'}",
				 'enabled' => 1
				 };
    $sublogs->{'04.firewall'} = {'caption' => $tr{'firewall logs'},
				 'uri' => '/cgi-bin/logs.cgi/firewalllog.dat',
				 'title' => "$tr{'firewall log viewer'}",
				 'enabled' => 1
				 };
    $sublogs->{'05.ids'} = {'caption' => $tr{'ids logs'},
				'uri' => '/cgi-bin/logs.cgi/ids.dat',
				'title' => "$tr{'intrusion detection system log viewer'}",
				'enabled' => 1
				};
    $sublogs->{'07.urlfilter'} = {
				'caption' => $tr{'urlfilter log'},
				'uri' => '/cgi-bin/logs.cgi/urlfilter.dat',
				'title' => "$tr{'urlfilter log'}",
				'enabled' => 1,
				};
    $sublogs->{'08.openvpn'} = {'caption' => $tr{'openvpn log'},
				'uri' => '/cgi-bin/logs.cgi/openvpn.dat',
				'title' => "$tr{'openvpn log'}",
				'enabled' => 1
				};
    $sublogs->{'09.system'} = {'caption' => $tr{'system logs'},
				'uri' => '/cgi-bin/logs.cgi/log.dat',
				'title' => "$tr{'system log viewer'}",
				'enabled' => 1
				};
    $sublogs->{'10.userlog'} = {'caption' => $tr{'user proxy logs'},
				'uri' => '/cgi-bin/logs.cgi/userlog.dat',
				'title' => "$tr{'user log viewer'}",
				'enabled' => 1
				};

    my %subipfirehash = ();
    my $subipfire = \%subipfirehash;
    $subipfire->{'01.pakfire'} = {'caption' => $tr{'pakfire'},
				  'uri' => '/cgi-bin/pakfire.cgi',
				  'title' => "$tr{'paketmanager'}",
				  'enabled' => 1,
				  };
    $subipfire->{'02.asterisk'} = {'caption' => $tr{'asterisk'},
				  'uri' => '/cgi-bin/asterisk.cgi',
				  'title' => "$tr{'asterisk'}",
				  'enabled' => 1,
				  };
    $subipfire->{'02.samba'} = {'caption' => $tr{'samba'},
				  'uri' => '/cgi-bin/samba.cgi',
				  'title' => "$tr{'samba'}",
				  'enabled' => 1,
				  };
    $subipfire->{'99.help'} = {'caption' => $tr{'help'},
				  'uri' => '/cgi-bin/help.cgi',
				  'title' => "$tr{'help'}",
				  'enabled' => 1,
				  };



    $menu->{'01.system'} = {'caption' => $tr{'alt system'},
			    	'enabled' => 1,
			    	'subMenu' => $subsystem
			    	};
    $menu->{'02.status'} = {'caption' => $tr{'status'},
			    	'enabled' => 1,
			   	'subMenu' => $substatus
			    	};
    $menu->{'03.network'} = {'caption' => $tr{'network'},
			     	'enabled' => 1,
			     	'subMenu' => $subnetwork
			     	};
    $menu->{'04.services'} = {'caption' => $tr{'alt services'},
			    	'enabled' => 1,
			    	'subMenu' => $subservices
			    	};
    $menu->{'05.firewall'} = {'caption' => $tr{'firewall'},
			    	'enabled' => 1,
			    	'subMenu' => $subfirewall
			    	};
    $menu->{'06.proxy'} = {'caption' => $tr{'alt proxy'},
			   	'enabled' => 1,
			   	'subMenu' => $subproxy
			   	};
    $menu->{'07.ipfire'} = {'caption' => 'IPFire',
				'enabled' => 1,
				'subMenu' => $subipfire
			 	};
    $menu->{'08.logs'} = {'caption' => $tr{'alt logs'},
			  	'enabled' => 1,
			  	'subMenu' => $sublogs
			  	};

    if (! blue_used() && ! orange_used()) {
	$menu->{'05.firewall'}{'subMenu'}->{'03.dmz'}{'enabled'} = 0;
    }
}

sub showhttpheaders
{
	print "Pragma: no-cache\n";
	print "Cache-control: no-cache\n";
	print "Connection: close\n";
	print "Content-type: text/html\n\n";
}

sub is_menu_visible($) {
    my $link = shift;
    $link =~ s#\?.*$##;
    return (-e $ENV{'DOCUMENT_ROOT'}."/../$link");
}


sub getlink($) {
    my $root = shift;
    if (! $root->{'enabled'}) {
	return '';
    }
    if ($root->{'uri'} !~ /^$/) {
	my $vars = '';
	if ($root->{'vars'} !~ /^$/) {
	    $vars = '?'. $root->{'vars'};
	}
	if (! is_menu_visible($root->{'uri'})) {
	    return '';
	}
	return $root->{'uri'}.$vars;
    }
    my $submenus = $root->{'subMenu'};
    if (! $submenus) {
	return '';
    }
    foreach my $item (sort keys %$submenus) {
	my $link = getlink($submenus->{$item});
	if ($link ne '') {
	    return $link;
	}
    }
    return '';
}


sub compare_url($) {
    my $conf = shift;

    my $uri = $conf->{'uri'};
    my $vars = $conf->{'vars'};
    my $novars = $conf->{'novars'};

    if ($uri eq '') {
	return 0;
    }
    if ($uri ne $URI[0]) {
	return 0;
    }
    if ($novars) {
	if ($URI[1] !~ /^$/) {
	    return 0;
	}
    }
    if (! $vars) {
	return 1;
    }
    return ($URI[1] eq $vars);
}


sub gettitle($) {
    my $root = shift;

    if (! $root) {
	return '';
    }
    foreach my $item (sort keys %$root) {
	my $val = $root->{$item};
	if (compare_url($val)) {
	    $val->{'selected'} = 1;
	    if ($val->{'title'} !~ /^$/) {
		return $val->{'title'};
	    }
	    return 'EMPTY TITLE';
	}

	my $title = gettitle($val->{'subMenu'});
	if ($title ne '') {
	    $val->{'selected'} = 1;
	    return $title;
	}
    }
    return '';
}


sub showmenu() {
    print <<EOF
  <div id="menu-top">
    <ul>
EOF
;
    foreach my $k1 ( sort keys %$menu ) {
	if (! $menu->{$k1}{'enabled'}) {
	    next;
	}

	my $link = getlink($menu->{$k1});
	if ($link eq '') {
	    next;
	}
	if (! is_menu_visible($link)) {
	    next;
	}
	if ($menu->{$k1}->{'selected'}) {
	    print '<li class="selected">';
	} else {
	    print '<li>';
	}

	print <<EOF
    <div class="rcorner">
      <a href="$link">$menu->{$k1}{'caption'}</a>
    </div>
  </li>
EOF
;
    }

    print <<EOF
    </ul>
  </div>
EOF
;    
}

sub getselected($) {
    my $root = shift;
    if (!$root) {
	return 0;
    }

    foreach my $item (%$root) {
	if ($root->{$item}{'selected'}) {
	    return $root->{$item};
	}
    }
}

sub showsubsection($$) {
    my $root = shift;
    my $id = shift;
    if ($id eq '') {
	$id = 'menu-left';
    }

    if (! $root) {
	return;
    }
    my $selected = getselected($root);
    if (! $selected) {
	return;
    }
    my $submenus = $selected->{'subMenu'};
    if (! $submenus) {
	return;
    }

    print <<EOF
  <div id="$id">
    <ul>
EOF
;
    foreach my $item (sort keys %$submenus) {
	my $hash = $submenus->{$item};
	if (! $hash->{'enabled'}) {
	    next;
	}

	my $link = getlink($hash);
	if ($link eq '') {
	    next;
	}
	if (! is_menu_visible($link)) {
	    next;
	}
	if ($hash->{'selected'}) {
	    print '<li class="selected">';
	} else {
	    print '<li>';
	}

	print <<EOF
      <a href="$link">$hash->{'caption'}</a>
  </li>
EOF
;
    }

    print <<EOF
    </ul>
  </div>
EOF
;    

}


sub showsubsubsection($) {
    my $root = shift;
    if (!$root) {
	return;
    }
    my $selected = getselected($root);
    if (! $selected) {
	return
    }
    if (! $selected->{'subMenu'}) {
	return
    }

    showsubsection($selected->{'subMenu'}, 'menu-subtop');
}


sub get_helpuri() {
    my $helpfile = '';
    if ($URI[0] =~ /.*\/([^\/]+)\.cgi/) {
	$helpfile = $1;
    } else {
	return '';
    }
    $helpfile .= '.help.html';

    my $helpuri = '/doc/'.$language.'/'.$helpfile;
    if (! -e $ENV{'DOCUMENT_ROOT'}.$helpuri) {
	return '';
    }
    return $helpuri;
}


sub openpage {
    my $title = shift;
    my $boh = shift;
    my $extrahead = shift;

    @URI=split ('\?',  $ENV{'REQUEST_URI'} );
    &readhash("${swroot}/main/settings", \%settings);
    &genmenu();

    my $h2 = gettitle($menu);
    my $helpuri = get_helpuri();

    $title = "IPFire - $title";
    if ($settings{'WINDOWWITHHOSTNAME'} eq 'on') {
        $title =  "$settings{'HOSTNAME'}.$settings{'DOMAINNAME'} - $title"; 
    }

    print <<END
<!DOCTYPE html 
     PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html>
  <head>
  <title>$title</title>

    $extrahead
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <meta http-equiv="Page-Enter" content="blendTrans(Duration=0.5,Transition=12)">
    <meta http-equiv="Page-Exit" content="blendTrans(Duration=0.5,Transition=12)">
    <link rel="shortcut icon" href="/favicon.ico" />
    <style type="text/css">\@import url(/include/style.css);</style>
    <style type="text/css">\@import url(/include/menu.css);</style>
    <style type="text/css">\@import url(/include/content.css);</style>
    <script language="javascript" type="text/javascript">
      
        function swapVisibility(id) {
            el = document.getElementById(id);
  	    if(el.style.display != 'block') {
  	        el.style.display = 'block'
  	    }
  	    else {
  	        el.style.display = 'none'
  	    }
        }
    </script>

  </head>
  <body>
<!-- IPFIRE HEADER -->

<div id="main">

<div id="header">
	<img id="logo-product" src="/images/logo_ipfire.gif">
   <div id="header-icons">
END
;

    if ($helpuri ne '') {
	print <<END
	    <a href="$helpuri" target="_blank"><img border="0" src="/images/help.gif"></a>
END
;
    } else {
	print '<img src="/images/help.gif">';
    }

print <<END
   </div>
</div>

END
;

    &showmenu();

print <<END
<div id="content">
  <table width="90%">
    <tr>
      <td valign="top">
END
;
	
    &showsubsection($menu);

    print <<END

      </td>
        <td width="100%" valign="top">
        <div id="page-content">
            <h2>$h2</h2>
END
    ;
    
    &showsubsubsection($menu);

    eval {
	require 'ipfire-network.pl';
	$supported = check_support();
	warn_unsupported($supported);
    };
}

sub closepage () {
    my $status = &connectionstatus();
    $uptime = `/usr/bin/uptime`;
	
    print <<END
	  <div align="center">
            <p>
	      <div style="font-size: 9px"><b>Status:</b> $status <b>Uptime:</b>$uptime</div>
            </p>
          </div>
	</body>
</html>
END
;
}

sub openbigbox
{
    my $width = $_[0];
    my $align = $_[1];
    my $sideimg = $_[2];

    if ($errormessage) {
	$bgcolor = "style='background-color: $colourerr;'";
    } else {
	$bgcolor = '';
    }
}

sub closebigbox
{
#	print "</td></tr></table></td></tr></table>\n" 
}

sub openbox
{
	$width = $_[0];
	$align = $_[1];
	$caption = $_[2];

	if ($caption) { print "<h3>$caption</h3>\n"; } else { print "&nbsp;"; }
	
	print "<table class=\"list\"><tr><td align=\"$align\">\n";
}

sub closebox
{
	print "</td></tr></table><br><br>";
}

sub writehash
{
	my $filename = $_[0];
	my $hash = $_[1];
	
	# write cgi vars to the file.
	open(FILE, ">${filename}") or die "Unable to write file $filename";
	flock FILE, 2;
	foreach $var (keys %$hash) 
	{
		$val = $hash->{$var};
		# Darren Critchley Jan 17, 2003 added the following because when submitting with a graphic, the x and y
		# location of the mouse are submitted as well, this was being written to the settings file causing
		# some serious grief! This skips the variable.x and variable.y
		if (!($var =~ /(.x|.y)$/)) {
			if ($val =~ / /) {
				$val = "\'$val\'"; }
			if (!($var =~ /^ACTION/)) {
				print FILE "${var}=${val}\n"; }
		}
	}
	close FILE;
}

sub readhash
{
	my $filename = $_[0];
	my $hash = $_[1];
	my ($var, $val);

	open(FILE, $filename) or die "Unable to read file $filename";
	
	while (<FILE>)
	{
		chop;
		($var, $val) = split /=/, $_, 2;
		if ($var)
		{
			$val =~ s/^\'//g;
			$val =~ s/\'$//g;

			# Untaint variables read from hash
			$var =~ /([A-Za-z0-9_-]*)/;        $var = $1;
			$val =~ /([\w\W]*)/; $val = $1;
			$hash->{$var} = $val;
		}
	}
	close FILE;
}

sub getcgihash {
	my ($hash, $params) = @_;
	my $cgi = CGI->new ();
	$hash->{'__CGI__'} = $cgi;
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
	%temp = $cgi->Vars();
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

sub log
{
	my $logmessage = $_[0];
	$logmessage =~ /([\w\W]*)/;
	$logmessage = $1;
	system('/usr/bin/logger', '-t', 'ipfire', $logmessage);
}

sub age
{
	my ($dev, $ino, $mode, $nlink, $uid, $gid, $rdev, $size,
	        $atime, $mtime, $ctime, $blksize, $blocks) = stat $_[0];
	my $now = time;

	my $totalsecs = $now - $mtime;
	my $days = int($totalsecs / 86400);
	my $totalhours = int($totalsecs / 3600);
	my $hours = $totalhours % 24;
	my $totalmins = int($totalsecs / 60);
	my $mins = $totalmins % 60;
	my $secs = $totalsecs % 60;

 	return "${days}d ${hours}h ${mins}m ${secs}s";
}

sub validip
{
	my $ip = $_[0];

	if (!($ip =~ /^(\d+)\.(\d+)\.(\d+)\.(\d+)$/)) {
		return 0; }
	else 
	{
		@octets = ($1, $2, $3, $4);
		foreach $_ (@octets)
		{
			if (/^0./) {
				return 0; }
			if ($_ < 0 || $_ > 255) {
				return 0; }
		}
		return 1;
	}
}

sub validmask
{
	my $mask = $_[0];

	# secord part an ip?
	if (&validip($mask)) {
		return 1; }
	# second part a number?
	if (/^0/) {
		return 0; }
	if (!($mask =~ /^\d+$/)) {
		return 0; }
	if ($mask >= 0 && $mask <= 32) {
		return 1; }
	return 0;
}

sub validipormask
{
	my $ipormask = $_[0];

	# see if it is a IP only.
	if (&validip($ipormask)) {
		return 1; }
	# split it into number and mask.
	if (!($ipormask =~ /^(.*?)\/(.*?)$/)) {
		return 0; }
	$ip = $1;
	$mask = $2;
	# first part not a ip?
	if (!(&validip($ip))) {
		return 0; }
	return &validmask($mask);
}

sub validipandmask
{
	my $ipandmask = $_[0];

	# split it into number and mask.
	if (!($ipandmask =~ /^(.*?)\/(.*?)$/)) {
		return 0; }
	$ip = $1;
	$mask = $2;
	# first part not a ip?
	if (!(&validip($ip))) {
		return 0; }
	return &validmask($mask);
}

sub validport
{
	$_ = $_[0];

	if (!/^\d+$/) {
		return 0; }
	if (/^0./) {
		return 0; }
	if ($_ >= 1 && $_ <= 65535) {
		return 1; }
	return 0;
}

sub validmac
{
	my $checkmac = $_[0];
	my $ot = '[0-9a-f]{2}'; # 2 Hex digits (one octet)
	if ($checkmac !~ /^$ot:$ot:$ot:$ot:$ot:$ot$/i)
	{
		return 0;
	}
	return 1;
}

sub validhostname
{
	# Checks a hostname against RFC1035
        my $hostname = $_[0];

	# Each part should be at least two characters in length
	# but no more than 63 characters
	if (length ($hostname) < 2 || length ($hostname) > 63) {
		return 0;}
	# Only valid characters are a-z, A-Z, 0-9 and -
	if ($hostname !~ /^[a-zA-Z0-9-]*$/) {
		return 0;}
	# First character can only be a letter or a digit
	if (substr ($hostname, 0, 1) !~ /^[a-zA-Z0-9]*$/) {
		return 0;}
	# Last character can only be a letter or a digit
	if (substr ($hostname, -1, 1) !~ /^[a-zA-Z0-9]*$/) {
		return 0;}
	return 1;
}

sub validdomainname
{
	# Checks a domain name against RFC1035
        my $domainname = $_[0];
	my @parts = split (/\./, $domainname);	# Split hostname at the '.'

	foreach $part (@parts) {
		# Each part should be at least two characters in length
		# but no more than 63 characters
		if (length ($part) < 2 || length ($part) > 63) {
			return 0;}
		# Only valid characters are a-z, A-Z, 0-9 and -
		if ($part !~ /^[a-zA-Z0-9-]*$/) {
			return 0;}
		# First character can only be a letter or a digit
		if (substr ($part, 0, 1) !~ /^[a-zA-Z0-9]*$/) {
			return 0;}
		# Last character can only be a letter or a digit
		if (substr ($part, -1, 1) !~ /^[a-zA-Z0-9]*$/) {
			return 0;}
	}
	return 1;
}

sub validfqdn
{
	# Checks a fully qualified domain name against RFC1035
        my $fqdn = $_[0];
	my @parts = split (/\./, $fqdn);	# Split hostname at the '.'
	if (scalar(@parts) < 2) {		# At least two parts should
		return 0;}			# exist in a FQDN
						# (i.e. hostname.domain)
	foreach $part (@parts) {
		# Each part should be at least two characters in length
		# but no more than 63 characters
		if (length ($part) < 2 || length ($part) > 63) {
			return 0;}
		# Only valid characters are a-z, A-Z, 0-9 and -
		if ($part !~ /^[a-zA-Z0-9-]*$/) {
			return 0;}
		# First character can only be a letter or a digit
		if (substr ($part, 0, 1) !~ /^[a-zA-Z0-9]*$/) {
			return 0;}
		# Last character can only be a letter or a digit
		if (substr ($part, -1, 1) !~ /^[a-zA-Z0-9]*$/) {
			return 0;}
	}
	return 1;
}

sub validportrange # used to check a port range 
{
	my $port = $_[0]; # port values
	$port =~ tr/-/:/; # replace all - with colons just in case someone used -
	my $srcdst = $_[1]; # is it a source or destination port

	if (!($port =~ /^(\d+)\:(\d+)$/)) {
	
		if (!(&validport($port))) {	 
			if ($srcdst eq 'src'){
				return $tr{'source port numbers'};
			} else 	{
				return $tr{'destination port numbers'};
			} 
		}
	}
	else 
	{
		@ports = ($1, $2);
		if ($1 >= $2){
			if ($srcdst eq 'src'){
				return $tr{'bad source range'};
			} else 	{
				return $tr{'bad destination range'};
			} 
		}
		foreach $_ (@ports)
		{
			if (!(&validport($_))) {
				if ($srcdst eq 'src'){
					return $tr{'source port numbers'}; 
				} else 	{
					return $tr{'destination port numbers'};
				} 
			}
		}
		return;
	}
}

# Test if IP is within a subnet
# Call: IpInSubnet (Addr, Subnet, Subnet Mask)
#       Subnet can be an IP of the subnet: 10.0.0.0 or 10.0.0.1
#       Everything in dottted notation
# Return: TRUE/FALSE
sub IpInSubnet
{
    $ip = unpack('N', inet_aton(shift));
    $start = unpack('N', inet_aton(shift));
    $mask  = unpack('N', inet_aton(shift));
    $start &= $mask;  # base of subnet...
    $end   = $start + ~$mask;
    return (($ip >= $start) && ($ip <= $end));
}

sub validemail {
    my $mail = shift;
    return 0 if ( $mail !~ /^[0-9a-zA-Z\.\-\_]+\@[0-9a-zA-Z\.\-]+$/ );
    return 0 if ( $mail =~ /^[^0-9a-zA-Z]|[^0-9a-zA-Z]$/);
    return 0 if ( $mail !~ /([0-9a-zA-Z]{1})\@./ );
    return 0 if ( $mail !~ /.\@([0-9a-zA-Z]{1})/ );
    return 0 if ( $mail =~ /.\.\-.|.\-\..|.\.\..|.\-\-./g );
    return 0 if ( $mail =~ /.\.\_.|.\-\_.|.\_\..|.\_\-.|.\_\_./g );
    return 0 if ( $mail !~ /\.([a-zA-Z]{2,3})$/ );
    return 1;
}

sub readhasharray {
    my ($filename, $hash) = @_;

    open(FILE, $filename) or die "Unable to read file $filename";

    while (<FILE>) {
	my ($key, $rest, @temp);
	chomp;
	($key, $rest) = split (/,/, $_, 2);
	if ($key =~ /^[0-9]+$/ && $rest) {
	    @temp = split (/,/, $rest);
	    $hash->{$key} = \@temp;
        }
    }
    close FILE;
    return;
}

sub writehasharray {
    my ($filename, $hash) = @_;
    my ($key, @temp);

    open(FILE, ">$filename") or die "Unable to write to file $filename";

    foreach $key (keys %$hash) {
	if ( $hash->{$key} ) {
	    print FILE "$key";
	    foreach $i (0 .. $#{$hash->{$key}}) {
		print FILE ",$hash->{$key}[$i]";
	    }
	}
	print FILE "\n";
    }
    close FILE;
    return;
}

sub findhasharraykey {
    foreach my $i (1 .. 1000000) {
	if ( ! exists $_[0]{$i}) {
	     return $i;
	}
    }
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
        my $status;
        opendir UPLINKS, "/var/ipfire/uplinks" or die "Cannot read uplinks: $!";
                foreach my $uplink (sort grep !/^\./, readdir UPLINKS) {
                    if ( -f "${swroot}/uplinks/${uplink}/active") {
                        if ( ! $status ) {
                                $timestr = &age("${swroot}/uplinks/${uplink}/active");
                                $status = "$tr{'connected'}: $uplink (<span class='ipcop_StatusBigRed'>$timestr</span>) ";
                        } else {
                                $timestr = &age("${swroot}/uplinks/${uplink}/active");
                                $status = "$status , $uplink (<span class='ipcop_StatusBigRed'>$timestr</span>) ";
                        }
                    } elsif ( -f "${swroot}/uplinks/${uplink}/connecting") {
                        if ( ! $status ) {
                                $status = "$tr{'connecting'} $uplink";
                        } else {
                                $status = "$status , $tr{'connecting'} $uplink (<span class='ipcop_StatusBigRed'>$timestr</span>) ";
                        }
                    }
                    $lines++;
                }
                closedir(UPLINKS);
                if ( ! $status ) {
                        $status = "$tr{'idle'}";
                }
                $connstate = "<span class='ipcop_StatusBig'>$status</span>";
    return $connstate;
}

sub srtarray 
# Darren Critchley - darrenc@telus.net - (c) 2003
# &srtarray(SortOrder, AlphaNumeric, SortDirection, ArrayToBeSorted)
# This subroutine will take the following parameters:
#   ColumnNumber = the column which you want to sort on, starts at 1
#   AlphaNumberic = a or n (lowercase) defines whether the sort should be alpha or numberic
#   SortDirection = asc or dsc (lowercase) Ascending or Descending sort
#   ArrayToBeSorted = the array that wants sorting
#
#   Returns an array that is sorted to your specs
#
#   If SortOrder is greater than the elements in array, then it defaults to the first element
# 
{
	my ($colno, $alpnum, $srtdir, @tobesorted) = @_;
	my @tmparray;
	my @srtedarray;
	my $line;
	my $newline;
	my $ttlitems = scalar @tobesorted; # want to know the number of rows in the passed array
	if ($ttlitems < 1){ # if no items, don't waste our time lets leave
		return (@tobesorted);
	}
	my @tmp = split(/\,/,$tobesorted[0]);
	$ttlitems = scalar @tmp; # this should be the number of elements in each row of the passed in array

	# Darren Critchley - validate parameters
	if ($colno > $ttlitems){$colno = '1';}
	$colno--; # remove one from colno to deal with arrays starting at 0
	if($colno < 0){$colno = '0';}
	if ($alpnum ne '') { $alpnum = lc($alpnum); } else { $alpnum = 'a'; }
	if ($srtdir ne '') { $srtdir = lc($srtdir); } else { $srtdir = 'src'; }

	foreach $line (@tobesorted)
	{
		chomp($line);
		if ($line ne '') {
			my @temp = split(/\,/,$line);
			# Darren Critchley - juggle the fields so that the one we want to sort on is first
			my $tmpholder = $temp[0];
			$temp[0] = $temp[$colno];
			$temp[$colno] = $tmpholder;
			$newline = "";
			for ($ctr=0; $ctr < $ttlitems ; $ctr++) {
				$newline=$newline . $temp[$ctr] . ",";
			}
			chop($newline);
			push(@tmparray,$newline);
		}
	}
	if ($alpnum eq 'n') {
		@tmparray = sort {$a <=> $b} @tmparray;
	} else {
		@tmparray = (sort @tmparray);
	}
	foreach $line (@tmparray)
	{
		chomp($line);
		if ($line ne '') {
			my @temp = split(/\,/,$line);
			my $tmpholder = $temp[0];
			$temp[0] = $temp[$colno];
			$temp[$colno] = $tmpholder;
			$newline = "";
			for ($ctr=0; $ctr < $ttlitems ; $ctr++){
				$newline=$newline . $temp[$ctr] . ",";
			}
			chop($newline);
			push(@srtedarray,$newline);
		}
	}

	if ($srtdir eq 'dsc') {
		@tmparray = reverse(@srtedarray);
		return (@tmparray);
	} else {
		return (@srtedarray);
	}
}

sub speedtouchversion
{
	if (-f "/proc/bus/usb/devices")
	{
		$speedtouch=`/bin/cat /proc/bus/usb/devices | /bin/grep 'Vendor=06b9 ProdID=4061' | /usr/bin/cut -d ' ' -f6`;
		if ($speedtouch eq '') {
			$speedtouch= $tr{'connect the modem'};
		}
	} else {
		$speedtouch='USB '.$tr{'not running'};
	}
	return $speedtouch
}

sub CheckSortOrder {
#Sorting of allocated leases
    if ($ENV{'QUERY_STRING'} =~ /^IPADDR|^ETHER|^HOSTNAME|^ENDTIME/ ) {
	my $newsort=$ENV{'QUERY_STRING'};
        &readhash("${swroot}/dhcp/settings", \%dhcpsettings);
        $act=$dhcpsettings{'SORT_LEASELIST'};
        #Reverse actual ?
        if ($act =~ $newsort) {
            if ($act !~ 'Rev') {$Rev='Rev'};
            $newsort.=$Rev
        };

        $dhcpsettings{'SORT_LEASELIST'}=$newsort;
	&writehash("${swroot}/dhcp/settings", \%dhcpsettings);
        $dhcpsettings{'ACTION'} = 'SORT';  # avoid the next test "First lauch"
    }

}

sub PrintActualLeases
{
    &openbox('100%', 'left', $tr{'current dynamic leases'});
    print <<END
<table width='100%'>
<tr>
<td width='25%' align='center'><a href='$ENV{'SCRIPT_NAME'}?IPADDR'><b>$tr{'ip address'}</b></a></td>
<td width='25%' align='center'><a href='$ENV{'SCRIPT_NAME'}?ETHER'><b>$tr{'mac address'}</b></a></td>
<td width='20%' align='center'><a href='$ENV{'SCRIPT_NAME'}?HOSTNAME'><b>$tr{'hostname'}</b></a></td>
<td width='30%' align='center'><a href='$ENV{'SCRIPT_NAME'}?ENDTIME'><b>$tr{'lease expires'} (local time d/m/y)</b></a></td>
</tr>
END
    ;

    open(LEASES,"/var/lib/dhcp/dhcpd.leases") or die "Can't open dhcpd.leases";
    while ($line = <LEASES>) {
	next if( $line =~ /^\s*#/ );
	chomp($line);
	@temp = split (' ', $line);

	if ($line =~ /^\s*lease/) {
	    $ip = $temp[1];
	    #All field are not necessarily read. Clear everything
	    $endtime = 0;
	    $ether = "";
	    $hostname = "";
	}

	if ($line =~ /^\s*ends/) {
	    $line =~ /(\d+)\/(\d+)\/(\d+) (\d+):(\d+):(\d+)/;
	    $endtime = timegm($6, $5, $4, $3, $2 - 1, $1 - 1900);
	}

	if ($line =~ /^\s*hardware ethernet/) {
	    $ether = $temp[2];
	    $ether =~ s/;//g;
	}

	if ($line =~ /^\s*client-hostname/) {
	    $hostname = "$temp[1] $temp[2] $temp[3]";
	    $hostname =~ s/;//g;
	    $hostname =~ s/\"//g;
	}

	if ($line eq "}") {
	    @record = ('IPADDR',$ip,'ENDTIME',$endtime,'ETHER',$ether,'HOSTNAME',$hostname);
    	    $record = {};                        		# create a reference to empty hash
	    %{$record} = @record;                		# populate that hash with @record
	    $entries{$record->{'IPADDR'}} = $record;   	# add this to a hash of hashes
	}
    }
    close(LEASES);

    my $id = 0;
    foreach my $key (sort leasesort keys %entries) {

	my $hostname = &cleanhtml($entries{$key}->{HOSTNAME},"y");

	if ($id % 2) {
	    print "<tr bgcolor='$table1colour'>"; 
	}
	else {
	    print "<tr bgcolor='$table2colour'>"; 
	}

	print <<END
<td align='center'>$entries{$key}->{IPADDR}</td>
<td align='center'>$entries{$key}->{ETHER}</td>
<td align='center'>&nbsp;$hostname </td>
<td align='center'>
END
	;

	($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $dst) = localtime ($entries{$key}->{ENDTIME});
	$enddate = sprintf ("%02d/%02d/%d %02d:%02d:%02d",$mday,$mon+1,$year+1900,$hour,$min,$sec);

	if ($entries{$key}->{ENDTIME} < time() ){
	    print "<strike>$enddate</strike>";
	} else {
	    print "$enddate";
	}
	print "</td></tr>";
	$id++;
    }

    print "</table>";
    &closebox();
}


# This sub is used during display of actives leases
sub leasesort {
    if (rindex ($dhcpsettings{'SORT_LEASELIST'},'Rev') != -1)
    {
        $qs=substr ($dhcpsettings{'SORT_LEASELIST'},0,length($dhcpsettings{'SORT_LEASELIST'})-3);
        if ($qs eq 'IPADDR') {
            @a = split(/\./,$entries{$a}->{$qs});
            @b = split(/\./,$entries{$b}->{$qs});
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
	    @a = split(/\./,$entries{$a}->{$qs});
    	    @b = split(/\./,$entries{$b}->{$qs});
    	    ($a[0]<=>$b[0]) ||
	    ($a[1]<=>$b[1]) ||
	    ($a[2]<=>$b[2]) ||
    	    ($a[3]<=>$b[3]);
	}else {
    	    $entries{$a}->{$qs} cmp $entries{$b}->{$qs};
	}
    }
}

sub get_uplinks() {
    my @uplinks = ();
    opendir(DIR, "${swroot}/uplinks/") || return \@uplinks;
    foreach my $dir (readdir(DIR)) {
	next if ($dir =~ /^\./);
	next if (-f "${swroot}/uplinks/$dir");
	push(@uplinks, $dir);
    }
    closedir(DIR);
    return \@uplinks;
}

sub get_iface($) {
    my $filename = shift;
    chomp($filename);
    open (F, $filename) || return "";
    my $iface = <F>;
    close(F);
    chomp($iface);
    return $iface;
}

sub get_red_ifaces_by_type($) {
    my $type=shift;
    my @gottypeiface = ();
    my @gottypeuplink = ();
    my @gottype = ();

    my $ref=get_uplinks();
    my @uplinks=@$ref;
    my %set = ();
    foreach my $link (@uplinks) {
	eval {
	    &readhash("${swroot}/uplinks/$link/settings", \%set);
	};
	push(@gottype, $link);

	my $iface = $set{'RED_DEV'};
	if (!$iface) {
	    $iface = get_iface("${swroot}/uplinks/$link/interface");
	}
	next if (!$iface);

	if ($set{'RED_TYPE'} eq $type) {
	    push(@gottypeiface, $iface);
	    push(@gottypeuplink, $link);
	}
    }
    return (\@gottypeiface, \@gottypeuplink, \@gottype);
}

sub get_red_ifaces() {
    return `cat ${swroot}/uplinks/*/interface 2>/dev/null`;
}

sub get_zone_devices($) {
    my $bridge = shift;
    my @ifaces = ();
    open (FILE, "${swroot}/ethernet/$bridge") || return "";
    foreach my $line (<FILE>) {
	chomp($line);
	next if (!$line);
	push(@ifaces, $line);
    }
    close(FILE);
    return \@ifaces;
}
