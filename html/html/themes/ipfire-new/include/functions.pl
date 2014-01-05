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
#                                                                             #
# Theme file for IPfire (based on ipfire theme)                               #
# Author kay-michael köhler kmk <michael@koehler.tk>                          #
#                                                                             #
# Version 1.0	March, 6th 2013                                               #
###############################################################################
#                                                                             #
# Modyfied theme by a.marx@ipfire.org January 2014                            #
#                                                                             #
# Cleanup code, deleted unused code and rewrote the rest to get a new working #
# IPFire default theme.                                                       #
###############################################################################

use File::Basename;
require "${General::swroot}/lang.pl";
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
		print '<a href="'.$link.'"><span>'.$submenus->{$item}->{'caption'}.'</span></a>';

		&showsubmenu($subsubmenus) if ($subsubmenus);
		print '</li>';
	}
	print "</ul>"
}

###############################################################################
#
# print menu html elements
sub showmenu() {
	print '<div id="cssmenu"><ul>';
	foreach my $k1 ( sort keys %$menu ) {
		$link = getlink($menu->{$k1});
		next if (!is_menu_visible($link) or $link eq '');
		print '<li class="has-sub "><a><span>'.$menu->{$k1}->{'caption'}.'</span></a>';
		my $submenus = $menu->{$k1}->{'subMenu'};
		&showsubmenu($submenus) if ($submenus);
		print "</li>";
	}
	if ($settings{'SPEED'} ne 'off') {
		print"<div id='traffic'>";
		print"<table><tr><td style='font-weight: bold;'>Traffic: &nbsp;</td>";
		print"<td id='bandwidthCalculationContainer'>In <span id='rx_kbs'></span> &nbsp; Out <span id='tx_kbs'></span></td>";
		print"</tr></table>";
		print '</ul></div></div>';
	}
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
	my $suppressMenu = shift;
	my @tmp = split(/\./, basename($0));
	my $scriptName = @tmp[0];
	my $h2 = $title;

	@URI=split ('\?',  $ENV{'REQUEST_URI'} );
	&General::readhash("${swroot}/main/settings", \%settings);
	&genmenu();

	$title = "IPFire - $title";
	if ($settings{'WINDOWWITHHOSTNAME'} eq 'on') {
		$title =  "$settings{'HOSTNAME'}.$settings{'DOMAINNAME'} - $title"; 
	}

print <<END
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
	<head>
	<title>$title</title>
	$extrahead
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
	<link rel="shortcut icon" href="/favicon.ico" />
	<link href="/themes/ipfire-new/include/css/style.css" rel="stylesheet" type="text/css"  />
	<script type="text/javascript" src="/include/jquery-1.9.1.min.js"></script>
END
;
if ($settings{'SPEED'} ne 'off') {
print <<END
	<script type="text/javascript" src="/themes/ipfire-new/include/js/refreshInetInfo.js"></script>
END
;
}

if ($settings{'FX'} ne 'off') {
print <<END
	<meta http-equiv="Page-Enter" content="blendTrans(Duration=0.5,Transition=12)" />
	<meta http-equiv="Page-Exit" content="blendTrans(Duration=0.5,Transition=12)" />
END
;
}

print <<END
		</head>
		<body>
END
;

print <<END
<!-- IPFIRE HEADER -->
		<div id="header_inner" class="fixed">
			<div id="logo">
END
;
	if ($settings{'WINDOWWITHHOSTNAME'} eq 'on') {
		print "<h1><span>$settings{'HOSTNAME'}.$settings{'DOMAINNAME'}</span></h1><br />"; 
	} else {
		print "<h1><span>IPFire</span></h1><br />";
	}

print <<END
				<h2>$h2</h2>
			</div>
		</div>
END
;

&showmenu() if ($suppressMenu != 1);

print <<END
<div id="main">
	<div id="main_inner" class="fixed">
		<div id="columnA_2columns">
END
;
}

###############################################################################
#
# print page opening html layout without menu
# @param page title
# @param boh
# @param extra html code for html head section
sub openpagewithoutmenu {
	openpage(shift,shift,shift,1);
	return;
}


###############################################################################
#
# print page closing html layout

sub closepage () {
	my $status = &connectionstatus();
	my $uptime = `/usr/bin/uptime|cut -d \" \" -f 4-`;
	$uptime =~ s/year(s|)/$Lang::tr{'year'}/;
	$uptime =~ s/month(s|)/$Lang::tr{'month'}/;
	$uptime =~ s/days/$Lang::tr{'days'}/;
	$uptime =~ s/day /$Lang::tr{'day'}/;
	$uptime =~ s/user(s|)/$Lang::tr{'user'}/;
	$uptime =~ s/load average/$Lang::tr{'uptime load average'}/;  
print <<END
		<!-- closepage begin -->
			</div>
	</div>
END
;

print "<div id='columnC_2columns'>";
print <<END
			<table cellspacing="5"  class="statusdisplay" border="0">
			<tr><td align='center'>$status   Uptime: $uptime</td></tr>
END
;

print <<END
		</table>
		</div>
	</div>
</body>
</html>
<!-- closepage end -->
END
;
}

###############################################################################
#
# print big box opening html layout
sub openbigbox
{
}

###############################################################################
#
# print big box closing html layout
sub closebigbox
{
}

###############################################################################
#
# print box opening html layout
# @param page width
# @param page align
# @param page caption
sub openbox
{
	$width = $_[0];
	$align = $_[1];
	$caption = $_[2];

print <<END
<!-- openbox -->
		<div class="post" align="$align">
END
;
if ($caption) { print "<h3>$caption</h3>\n"; } else { print "&nbsp;"; }
}

###############################################################################
#
# print box closing html layout
sub closebox
{
	print <<END
	</div>
	<br class="clear" />
	<!-- closebox -->
END
;
}

1;
