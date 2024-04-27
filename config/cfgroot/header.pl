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
use File::Basename;
use HTML::Entities();
use Socket;
use Time::Local;
use Encode;

require "${General::swroot}/graphs.pl";

our %color = ();
&General::readhash("/srv/web/ipfire/html/themes/ipfire/include/colors.txt", \%color);

$|=1; # line buffering

$Header::revision = 'final';
$Header::swroot = '/var/ipfire';
$Header::graphdir='/srv/web/ipfire/html/graphs';
$Header::pagecolour = '#ffffff';
$Header::bordercolour = '#363636';
$Header::table1colour = '#f5f5f5';
$Header::table2colour = '#fafafa';
$Header::colourred = '#993333';
$Header::colourorange = '#FF9933';
$Header::colouryellow = '#FFFF00';
$Header::colourgreen = '#339933';
$Header::colourblue = '#333399';
$Header::colourovpn = '#339999';
$Header::colourfw = '#000000';
$Header::colourvpn = '#990099';
$Header::colourwg = '#ff007f';
$Header::colourerr = '#FF0000';
$Header::viewsize = 150;
$Header::errormessage = '';
$Header::extraHead = <<END
<style>
	.color20 {
		background-color: $color{'color20'};
	}
	.color22 {
		background-color: $color{'color22'};
	}
	.colouryellow {
		background-color: $Header::colouryellow;
	}
	.orange {
		background-color: orange;
	}
	.red {
		background-color: red;
	}
	.table1colour {
		background-color: $Header::table1colour;
	}
	.table2colour {
		background-color: $Header::table2colour;
	}
	.percent-box {
		border-style: solid;
		border-width: 1px;
		border-color: #a0a0a0;
		width: 100px;
		height: 10px;
	}
	.percent-bar {
		background-color: #a0a0a0;
		border-style: solid;
		border-width: 1px;
		border-color: #e2e2e2;
	}
	.percent-space {
		background-color: #e2e2e2;
		border-style: solid;
		border-width: 1px;
		border-color: #e2e2e2;
	}
</style>
END
;
my %menuhash = ();
my $menu = \%menuhash;
%settings = ();
my @URI = split('\?', $ENV{'REQUEST_URI'});

### Make sure this is an SSL request
if ($ENV{'SERVER_ADDR'} && $ENV{'HTTPS'} ne 'on') {
    print "Status: 302 Moved\r\n";
    print "Location: https://$ENV{'SERVER_ADDR'}:444/$ENV{'PATH_INFO'}\r\n\r\n";
    exit 0;
}

### Initialize environment
&General::readhash("${swroot}/main/settings", \%settings);
$hostname = $settings{'HOSTNAME'};
$hostnameintitle = 0;

### Initialize language
require "${swroot}/lang.pl";
$language = &Lang::FindWebLanguage($settings{"LANGUAGE"});

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

### Initialize user manual
my %manualpages = ();
&_read_manualpage_hash("${General::swroot}/main/manualpages");

### Load selected language and theme functions
require "${swroot}/langs/en.pl";
require "${swroot}/langs/${language}.pl";

###############################################################################
#
# print menu html elements for submenu entries
# @param submenu entries
sub showsubmenu() {
	my $submenus = shift;

	print "<ul>";
	foreach my $item (sort keys %$submenus) {
		$link = getlink($submenus->{$item});
		next if (!is_menu_visible($link) or $link eq '');

		my $subsubmenus = $submenus->{$item}->{'subMenu'};

		if ($subsubmenus) {
			print '<li class="has-sub ">';
		} else {
			print '<li>';
		}
		print '<a href="'.$link.'">'.$submenus->{$item}->{'caption'}.'</a>';

		&showsubmenu($subsubmenus) if ($subsubmenus);
		print '</li>';
	}
	print "</ul>"
}

###############################################################################
#
# print menu html elements
sub showmenu() {
	print '<div id="cssmenu" class="bigbox fixed">';

	if ($settings{'SPEED'} ne 'off') {
		print <<EOF;
			<div id='traffic'>
				<strong>$Lang::tr{'traffic stat title'}:</strong>
				$Lang::tr{'traffic stat in'} <span id='rx_kbs'>--.-- bit/s</span> &nbsp;
				$Lang::tr{'traffic stat out'} <span id='tx_kbs'>--.-- bit/s</span>
			</div>
EOF
	}

	print "<ul>";
	foreach my $k1 ( sort keys %$menu ) {
		$link = getlink($menu->{$k1});
		next if (!is_menu_visible($link) or $link eq '');
		print '<li class="has-sub "><a href="#"><span>'.$menu->{$k1}->{'caption'}.'</span></a>';
		my $submenus = $menu->{$k1}->{'subMenu'};
		&showsubmenu($submenus) if ($submenus);
		print "</li>";
	}

	print "</ul></div>";
}

###############################################################################
#
# print page opening html layout
# @param page title
# @param boh
# @param extra html code for html head section
# @param suppress menu option, can be numeric 1 or nothing.
#		 menu will be suppressed if param is 1
sub openpage {
	my $title = shift;
	my $boh = shift;
	my $extrahead = shift;
	my $suppressMenu = shift // 0;

	my $headline = "IPFire";
	if (($settings{'WINDOWWITHHOSTNAME'} eq 'on') || ($settings{'WINDOWWITHHOSTNAME'} eq '')) {
		$headline =  "$settings{'HOSTNAME'}.$settings{'DOMAINNAME'}";
	}

print <<END;
<!DOCTYPE html>
<html lang="$language">
	<head>
	<title>$headline - $title</title>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
	<link rel="shortcut icon" href="/favicon.ico" />
	<script type="text/javascript" src="/include/jquery.js"></script>
	<script src="/include/rrdimage.js"></script>

	$extrahead
	<script type="text/javascript">
		function swapVisibility(id) {
			\$('#' + id).toggle();
		}
	</script>
END


print "<link href=\"/themes/ipfire/include/css/style.css?v=20240806\" rel=\"stylesheet\" type=\"text/css\" />\n";


if ($settings{'SPEED'} ne 'off') {
print <<END
	<script type="text/javascript" src="/themes/ipfire/include/js/refreshInetInfo.js"></script>
END
;
}

print <<END
	</head>
	<body>
		<div id="header" class="fixed">
			<div id="logo">
				<h1>
					<a href="https://www.ipfire.org">
						IPFire_
					</a>
END
;
	if ($settings{'WINDOWWITHHOSTNAME'} ne 'off') {
		print "&dash; $settings{'HOSTNAME'}.$settings{'DOMAINNAME'}";
	}

print <<END
				</h1>
			</div>
		</div>
END
;

unless($suppressMenu) {
	&genmenu();
	&showmenu();
}

print <<END
	<div class="bigbox fixed">
		<div id="main_inner" class="fixed">
			<div id="main_header">
				<h1>$title</h1>
END
;

# Print user manual link
my $manual_url = &get_manualpage_url();
if($manual_url) {
	print <<END
				<span><a href="$manual_url" title="$Lang::tr{'online help en'}" target="_blank"><img src="/images/help-browser.png" alt="$Lang::tr{'online help en'}"></a></span>
END
;
}

print <<END
			</div>
END
;
}

###############################################################################
#
# print page closing html layout

sub closepage () {
	open(FILE, "</etc/system-release");
	my $system_release = <FILE>;
	$system_release =~ s/core/$Lang::tr{'core update'} /;
	close(FILE);

print <<END;
		</div>
	</div>

	<div id="footer" class='bigbox fixed'>
		<span class="pull-right">
			<a href="https://www.ipfire.org/" target="_blank"><strong>IPFire.org</strong></a> &bull;
			<a href="https://www.ipfire.org/donate" target="_blank">$Lang::tr{'support donation'}</a>
		</span>

		<strong>$system_release</strong>
	</div>
</body>
</html>
END
;
}

###############################################################################
#
# print big box opening html layout
sub openbigbox {
}

###############################################################################
#
# print big box closing html layout
sub closebigbox {
}

# Sections

sub opensection($) {
	my $title = shift;

	# Open the section
	print "<section class=\"section\">";

	# Show the title if set
	if ($title) {
		print "	<h2 class=\"title\">${title}</h2>\n";
	}
}

sub closesection() {
	print "</section>";
}

###############################################################################
#
# print box opening html layout
# @param page width
# @param page align
# @param page caption
sub openbox {
	# The width parameter is ignored and should always be '100%'
	my $width = shift;
	my $align = shift;

	my $title = shift;

	print "<section class=\"section is-box\">\n";

	# Show the title
	if ($title) {
		print "	<h2 class=\"title\">${title}</h2>\n";
	}
}

###############################################################################
#
# print box closing html layout
sub closebox {
	print "</section>";
}

sub graph($) {
	my $title = shift;

	# Open a new section with a title
	&opensection($title);

	&Graphs::makegraphbox(@_);

	# Close the section
	&closesection();
}

sub green_used() {
    if ($Network::ethernet{'GREEN_DEV'} && $Network::ethernet{'GREEN_DEV'} ne "") {
        return 1;
    }

    return 0;
}

sub orange_used () {
    if ($Network::ethernet{'CONFIG_TYPE'} =~ /^[24]$/) {
	return 1;
    }
    return 0;
}

sub blue_used () {
    if ($Network::ethernet{'CONFIG_TYPE'} =~ /^[34]$/) {
	return 1;
    }
    return 0;
}

### Initialize menu
sub genmenu {

    my %subsystemhash = ();
    my $subsystem = \%subsystemhash;

    my %substatushash = ();
    my $substatus = \%substatushash;

    my %subnetworkhash = ();
    my $subnetwork = \%subnetworkhash;

    my %subserviceshash = ();
    my $subservices = \%subserviceshash;

    my %subfirewallhash = ();
    my $subfirewall = \%subfirewallhash;

    my %subipfirehash = ();
    my $subipfire = \%subipfirehash;

    my %sublogshash = ();
    my $sublogs = \%sublogshash;

    eval `/bin/cat /var/ipfire/menu.d/*.menu`;
    eval `/bin/cat /var/ipfire/menu.d/*.main`;

    if (! blue_used()) {
	$menu->{'05.firewall'}{'subMenu'}->{'60.wireless'}{'enabled'} = 0;
    }
    if ( $Network::ethernet{'CONFIG_TYPE'} =~ /^(1|2|3|4)$/ && $Network::ethernet{'RED_TYPE'} eq 'STATIC' ) {
	$menu->{'03.network'}{'subMenu'}->{'70.aliases'}{'enabled'} = 1;
    }

    if (&General::RedIsWireless()) {
        $menu->{'01.system'}{'subMenu'}->{'21.wlan'}{'enabled'} = 1;
    }

    if ( $Network::ethernet{'RED_TYPE'} eq "PPPOE" && $Network::ppp{'MONPORT'} ne "" ) {
        $menu->{'02.status'}{'subMenu'}->{'74.modem-status'}{'enabled'} = 1;
    }

	# Disable the Dialup/PPPoE menu item when the RED interface is in IP mode
	# (the "Network" module is loaded by general-functions.pl)
	if(&Network::is_red_mode_ip()) {
		$menu->{'01.system'}{'subMenu'}->{'20.dialup'}{'enabled'} = 0;
	}

    # Disbale unusable things in cloud environments
    if (&General::running_in_cloud()) {
        $menu->{'03.network'}{'subMenu'}->{'30.dhcp'}{'enabled'} = 0;
        $menu->{'03.network'}{'subMenu'}->{'80.macadressmenu'}{'enabled'} = 0;
        $menu->{'03.network'}{'subMenu'}->{'90.wakeonlan'}{'enabled'} = 0;
    }
}

sub showhttpheaders($) {
	my $overwrites = shift;

	my %headers = (
		"Content-Type"  => "text/html; charset=UTF-8",
		"Cache-Control" => "private",

		# Overwrite anything passed
		%$overwrites,
	);

	# Print all headers
	foreach my $header (keys %headers) {
		print "$header: $headers{$header}\n";
	}

	# End headers
	print "\n";
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

sub getcgihash {
	my ($hash, $params) = @_;
	my $cgi = CGI->new ();
	$hash->{'__CGI__'} = $cgi;
	return if ($ENV{'REQUEST_METHOD'} ne 'POST');
	if (!$params->{'wantfile'}) {
		$CGI::DISABLE_UPLOADS = 1;
		$CGI::POST_MAX        = 1024 * 1024;
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

sub escape($) {
	my $s = shift;
	return HTML::Entities::encode_entities($s);
}

sub cleanhtml {
	my $outstring =$_[0];
	$outstring =~ tr/,/ / if not defined $_[1] or $_[1] ne 'y';
	# decode the UTF-8 text so that characters with diacritical marks such as
	# umlauts are treated correctly by the escape command
	$outstring = &Encode::decode("UTF-8",$outstring);
	escape($outstring);
	# encode the text back to UTF-8 after running the escape command
	$outstring = &Encode::encode("UTF-8",$outstring);
	return $outstring;
}

sub connectionstatus
{
    my $iface='';

    my $profileused='';
    unless ($Network::ethernet{'RED_TYPE'} =~ /^(DHCP|STATIC)$/) {
		$profileused="- $Network::ppp{'PROFILENAME'}";
    }

    my ($timestr, $connstate);

		my $connstate = "<span>$Lang::tr{'idle'} $profileused</span>";

		if (-e "${General::swroot}/red/active") {
			$timestr = &General::age("${General::swroot}/red/active");
			$connstate = "<span>$Lang::tr{'connected'} - (<span>$timestr</span>) $profileused</span>";
		} else {
		  if (open(KEEPCONNECTED, "</var/ipfire/red/keepconnected") == false) {
				$connstate = "<span>$Lang::tr{'connection closed'} $profileused</span>";
			} else {
				$connstate = "<span>$Lang::tr{'connecting'} $profileused</span>" if (system("ps -ef | grep -q '[p]ppd'"));
			}
		}

    return $connstate;
}

sub CheckSortOrder {
#Sorting of allocated leases
    if ($ENV{'QUERY_STRING'} =~ /^IPADDR|^ETHER|^HOSTNAME|^ENDTIME/ ) {
        my $newsort=$ENV{'QUERY_STRING'};
        &General::readhash("${swroot}/dhcp/settings", \%dhcpsettings);
        $act=$dhcpsettings{'SORT_LEASELIST'};
        #Reverse actual ?
        if ($act =~ $newsort) {
            if ($act !~ 'Rev') {$Rev='Rev'};
            $newsort.=$Rev
        };

        $dhcpsettings{'SORT_LEASELIST'}=$newsort;
        &General::writehash("${swroot}/dhcp/settings", \%dhcpsettings);
        $dhcpsettings{'ACTION'} = 'SORT';  # avoid the next test "First lauch"
    }

}

sub PrintActualLeases
{
    &openbox('100%', 'left', $Lang::tr{'current dynamic leases'});
    print <<END
<table width='100%' class='tbl'>
<tr>
<th width='25%' align='center'><a href='$ENV{'SCRIPT_NAME'}?IPADDR'><b>$Lang::tr{'ip address'}</b></a></th>
<th width='25%' align='center'><a href='$ENV{'SCRIPT_NAME'}?ETHER'><b>$Lang::tr{'mac address'}</b></a></th>
<th width='20%' align='center'><a href='$ENV{'SCRIPT_NAME'}?HOSTNAME'><b>$Lang::tr{'hostname'}</b></a></th>
<th width='25%' align='center'><a href='$ENV{'SCRIPT_NAME'}?ENDTIME'><b>$Lang::tr{'lease expires'} (local time d/m/y)</b></a></th>
<th width='5%' align='center'><b>$Lang::tr{'dhcp make fixed lease'}</b></th>
</tr>
END
;

    open(LEASES,"/var/state/dhcp/dhcpd.leases") or die "Can't open dhcpd.leases";
	while (my $line = <LEASES>) {
		next if( $line =~ /^\s*#/ );
		chomp($line);
		@temp = split (' ', $line);

		if ($line =~ /^\s*lease/) {
			$ip = $temp[1];
			#All field are not necessarily read. Clear everything
			$endtime = 0;
			$endtime_print = "";
			$expired = 0;
			$ether = "";
			$hostname = "";
		}

		if ($line =~ /^\s*ends \d (\d+)\/(\d+)\/(\d+) (\d+):(\d+):(\d+)/) {
			$endtime = timegm($6, $5, $4, $3, $2 - 1, $1 - 1900);
			($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $dst) = localtime($endtime);
			$endtime_print = sprintf ("%02d/%02d/%d %02d:%02d:%02d",$mday,$mon+1,$year+1900,$hour,$min,$sec);
			$expired = $endtime < time();

		} elsif ($line =~ /^\s*ends never/) {
			$endtime = 0;
			$endtime_print = $Lang::tr{'never'};
			$expired = 0;
		}

		if ($line =~ /^\s*hardware ethernet/) {
			$ether = $temp[2];
			$ether =~ s/;//g;
		}

		if ($line =~ /^\s*client-hostname/) {
			$hostname = "$temp[1] $temp[2] $temp[3]";
			$hostname =~ s/\"|[;\s]+?$//g; # remove quotes, trim semicolon and white space
		}

		if ($line eq "}") {
			@record = ('IPADDR',$ip,'ENDTIME',$endtime,'ETHER',$ether,'HOSTNAME',$hostname,'endtime_print',$endtime_print,'expired',$expired);
			$record = {};								# create a reference to empty hash
			%{$record} = @record;						# populate that hash with @record
			$entries{$record->{'IPADDR'}} = $record;	# add this to a hash of hashes
		}
    }
    close(LEASES);

    my $id = 0;
    my $col = "";
	my $divider_printed = 0;
    foreach my $key (sort leasesort keys %entries) {
		my $hostname = &cleanhtml($entries{$key}->{HOSTNAME},"y");
		my $hostname_print = $hostname;
		if($hostname_print eq "") { #print blank space if no hostname is found
			$hostname_print = "&nbsp;&nbsp;&nbsp;";
		}

		# separate active and expired leases with a horizontal line
		if(($entries{$key}->{expired}) && ($divider_printed == 0)) {
			$divider_printed = 1;
			if ($id % 2) {
				print "<tr><td colspan='5' bgcolor='$table1colour'><hr size='1'></td></tr>\n";
			} else {
				print "<tr><td colspan='5' bgcolor='$table2colour'><hr size='1'></td></tr>\n";
			}
			$id++;
		}

		print "<form method='post' action='/cgi-bin/dhcp.cgi'><tr>\n";
		if ($id % 2) {
			$col="bgcolor='$table1colour'";
		} else {
			$col="bgcolor='$table2colour'";
		}

		if($entries{$key}->{expired}) {
			print <<END
<td align='center' $col><input type='hidden' name='FIX_ADDR' value='$entries{$key}->{IPADDR}' /><strike><i>$entries{$key}->{IPADDR}</i></strike></td>
<td align='center' $col><input type='hidden' name='FIX_MAC' value='$entries{$key}->{ETHER}' /><strike><i>$entries{$key}->{ETHER}</i></strike></td>
<td align='center' $col><input type='hidden' name='FIX_REMARK' value='$hostname' /><strike><i>$hostname_print<i><strike></td>
<td align='center' $col><input type='hidden' name='FIX_ENABLED' value='on' /><strike><i>$entries{$key}->{endtime_print}</i></strike></td>
END
;
		} else {
			print <<END
<td align='center' $col><input type='hidden' name='FIX_ADDR' value='$entries{$key}->{IPADDR}' />$entries{$key}->{IPADDR}</td>
<td align='center' $col><input type='hidden' name='FIX_MAC' value='$entries{$key}->{ETHER}' />$entries{$key}->{ETHER}</td>
<td align='center' $col><input type='hidden' name='FIX_REMARK' value='$hostname' />$hostname_print</td>
<td align='center' $col><input type='hidden' name='FIX_ENABLED' value='on' />$entries{$key}->{endtime_print}</td>
END
;
		}

		print <<END
<td $col><input type='hidden' name='ACTION' value='$Lang::tr{'add'}2' /><input type='submit' name='SUBMIT' value='$Lang::tr{'add'}' /></td>
</tr></form>
END
;
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
			$entries{$a}->{'expired'} <=> $entries{$b}->{'expired'} || # always sort by expiration first
			($b[0]<=>$a[0]) ||
			($b[1]<=>$a[1]) ||
			($b[2]<=>$a[2]) ||
			($b[3]<=>$a[3]);
		} else {
			$entries{$a}->{'expired'} <=> $entries{$b}->{'expired'} ||
			$entries{$b}->{$qs} cmp $entries{$a}->{$qs};
		}
	}
	else #not reverse
	{
		$qs=$dhcpsettings{'SORT_LEASELIST'};
		if ($qs eq 'IPADDR') {
			@a = split(/\./,$entries{$a}->{$qs});
			@b = split(/\./,$entries{$b}->{$qs});
			$entries{$a}->{'expired'} <=> $entries{$b}->{'expired'} ||
			($a[0]<=>$b[0]) ||
			($a[1]<=>$b[1]) ||
			($a[2]<=>$b[2]) ||
			($a[3]<=>$b[3]);
		} else {
			$entries{$a}->{'expired'} <=> $entries{$b}->{'expired'} ||
			$entries{$a}->{$qs} cmp $entries{$b}->{$qs};
		}
	}
}

sub colorize {
	my $string =  $_[0];
	my @array = split(/\//,$string);
	my $string2 = $array[0];

	if ( $string eq "*" or $string eq "" ){
		return $string;
	} elsif ( $string =~ "ipsec" ){
		return "<font color='".${Header::colourvpn}."'>".$string."</font>";
	} elsif ( $string =~ "tun" ){
		return "<font color='".${Header::colourovpn}."'>".$string."</font>";
	} elsif ( $string =~ "lo" or $string =~ "127.0.0.0" ){
		return "<font color='".${Header::colourfw}."'>".$string."</font>";
	} elsif ( $string =~ $Network::ethernet{'GREEN_DEV'} or &General::IpInSubnet($string2,$Network::ethernet{'GREEN_NETADDRESS'},$Network::ethernet{'GREEN_NETMASK'}) ){
		return "<font color='".${Header::colourgreen}."'>".$string."</font>";
	} elsif (  $string =~ "ppp0" or $string =~ $Network::ethernet{'RED_DEV'} or $string =~ "0.0.0.0" or $string =~ $Network::ethernet{'RED_ADDRESS'} ){
		return "<font color='".${Header::colourred}."'>".$string."</font>";
	} elsif ( $Network::ethernet{'CONFIG_TYPE'}>1 and ( $string =~ $Network::ethernet{'BLUE_DEV'} or &General::IpInSubnet($string2,$Network::ethernet{'BLUE_NETADDRESS'},$Network::ethernet{'BLUE_NETMASK'}) )){
		return "<font color='".${Header::colourblue}."'>".$string."</font>";
	} elsif ( $Network::ethernet{'CONFIG_TYPE'}>2 and ( $string =~ $Network::ethernet{'ORANGE_DEV'} or &General::IpInSubnet($string2,$Network::ethernet{'ORANGE_NETADDRESS'},$Network::ethernet{'ORANGE_NETMASK'}) )){
		return "<font color='".${Header::colourorange}."'>".$string."</font>";
	} else {
		return $string;
	}
}

# Get user manual URL for a configuration page inside the "/cgi-bin/"
# (reads current page from the environment variables unless defined)
# Returns empty if no URL is available
sub get_manualpage_url() {
	my ($cgifile) = @_;
	$cgifile //= substr($ENV{'SCRIPT_NAME'}, 9); # remove fixed "/cgi-bin/" path

	# Ensure base url is configured
	return unless($manualpages{'BASE_URL'});

	# Return URL
	if($cgifile && defined($manualpages{$cgifile})) {
		return "$manualpages{'BASE_URL'}/$manualpages{$cgifile}";
	}

	# No manual page configured, return nothing
	return;
}

# Private function to load a hash of configured user manual pages from file
# (run check_manualpages.pl to make sure the file is correct)
sub _read_manualpage_hash() {
	my ($filename) = @_;

	open(my $file, "<", $filename) or return; # Fail silent
	while(my $line = <$file>) {
		chomp($line);
		next if(substr($line, 0, 1) eq '#'); # Skip comments
		next if(index($line, '=', 1) == -1); # Skip incomplete lines

		my($left, $value) = split(/=/, $line, 2);
		if($left =~ /^([[:alnum:]\/._-]+)$/) {
			my $key = $1;
			$manualpages{$key} = $value;
		}
	}
	close($file);
}

sub ServiceStatus() {
	my $services = shift;
	my %services = %{ $services };

	# Write the table header
	print <<EOF;
		<table class="tbl">
			<!-- <thead>
				<tr>
					<th>
						$Lang::tr{'service'}
					</th>

					<th>
						$Lang::tr{'status'}
					</th>

					<th>
						$Lang::tr{'memory'}
					</th>
				</tr>
			</thead> -->

			<tbody>
EOF

	foreach my $service (sort keys %services) {
		my %config = %{ $services{$service} };

		my $pidfile = $config{"pidfile"};
		my $process = $config{"process"};

		# Collect all pids
		my @pids = ();

		# Read the PID file or go search...
		if (defined $pidfile) {
			@pids = &General::read_pids("${pidfile}");
		} else {
			@pids = &General::find_pids("${process}");
		}

		# Get memory consumption
		my $mem = &General::get_memory_consumption(@pids);

		print <<EOF;
				<tr>
					<th scope="row">
						$service
					</th>
EOF

		# Running?
		if (scalar @pids) {
			# Format memory
			$mem = &General::formatBytes($mem);

			print <<EOF;
					<td class="status is-running">
						$Lang::tr{'running'}
					</td>

					<td class="text-right">
						${mem}
					</td>
EOF

		# Not Running
		} else {
			print <<EOF;
					<td class="status is-stopped" colspan="2">
						$Lang::tr{'stopped'}
					</td>
EOF
		}

		print <<EOF;
				</tr>
EOF

	}

	print <<EOF;
		</tbody>
		</table>
EOF
}

1; # End of package "Header"
