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
				In  <span id='rx_kbs'>--.-- bit/s</span> &nbsp;
				Out <span id='tx_kbs'>--.-- bit/s</span>
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


print "<link href=\"/themes/ipfire/include/css/style.css\" rel=\"stylesheet\" type=\"text/css\" />\n";


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
				<a href="https://www.ipfire.org" style="text-decoration: none;">
					<img src="/themes/ipfire/images/tux2.png" style="float:left; margin-left: -3px; margin-top: -3px;"/>
END
;
	if ($settings{'WINDOWWITHHOSTNAME'} ne 'off') {
		print "</a><h1>$settings{'HOSTNAME'}.$settings{'DOMAINNAME'}</h1>";
	} else {
		print "<h1>IPFire</h1></a>";
	}

print <<END
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
my $manual_url = &Header::get_manualpage_url();
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
	$system_release =~ s/core/Core Update /;
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

	if($align eq 'center') {
		print "<div class='post' align='center'>\n"
	}
	else {
		print "<div class='post'>\n";
	}

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
