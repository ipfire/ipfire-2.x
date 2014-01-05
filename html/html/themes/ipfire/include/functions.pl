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
				<strong>Traffic:</strong>
				In  <span id='rx_kbs'>--.-- Bit/s</span> &nbsp;
				Out <span id='tx_kbs'>--.-- Bit/s</span>
			</div>
EOF
	}

	print "<ul>";
	foreach my $k1 ( sort keys %$menu ) {
		$link = getlink($menu->{$k1});
		next if (!is_menu_visible($link) or $link eq '');
		print '<li class="has-sub "><a><span>'.$menu->{$k1}->{'caption'}.'</span></a>';
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
	my $suppressMenu = shift;
	my @tmp = split(/\./, basename($0));
	my $scriptName = @tmp[0];

	@URI=split ('\?',  $ENV{'REQUEST_URI'} );
	&General::readhash("${swroot}/main/settings", \%settings);
	&genmenu();

	my $headline = "IPFire";
	if ($settings{'WINDOWWITHHOSTNAME'} eq 'on') {
		$headline =  "$settings{'HOSTNAME'}.$settings{'DOMAINNAME'}";
	}

print <<END
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
	<head>
	<title>$headline - $title</title>
	$extrahead
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
	<link rel="shortcut icon" href="/favicon.ico" />
	<link href="/themes/ipfire/include/css/style.css" rel="stylesheet" type="text/css"  />
	<script type="text/javascript" src="/include/jquery.js"></script>
END
;
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
END
;
	if ($settings{'WINDOWWITHHOSTNAME'} ne 'off') {
		print "<h1>$settings{'HOSTNAME'}.$settings{'DOMAINNAME'}</h1>";
	} else {
		print "<h1>IPFire</h1>";
	}

print <<END
			</div>
		</div>
END
;

&showmenu() if ($suppressMenu != 1);

print <<END
	<div class="bigbox fixed">
		<div id="main_inner" class="fixed">
			<h1>$title</h1>
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
	open(FILE, "</etc/system-release");
	my $system_release = <FILE>;
	$system_release =~ s/core/Core Update/;
	close(FILE);

print <<END;
		</div>
	</div>

	<div id="footer" class='bigbox fixed'>
		<span class="pull-right">
			<a href="http://www.ipfire.org/" target="_blank"><strong>IPFire.org</strong></a> &bull;
			<a href="http://www.ipfire.org/donate" target="_blank">$Lang::tr{'support donation'}</a>
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

###############################################################################
#
# print box opening html layout
# @param page width
# @param page align
# @param page caption
sub openbox {
	$width = $_[0];
	$align = $_[1];
	$caption = $_[2];

	print "<div class='post' align='$align'>\n";

	if ($caption) {
		print "<h2>$caption</h2>\n";
	}
}

###############################################################################
#
# print box closing html layout
sub closebox {
	print "</div>";
}

1;
