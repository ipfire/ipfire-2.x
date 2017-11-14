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

sub showmenu() {
    print <<EOF
		<div id="menu">
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
	    print "<li><a href=\"$link\" class=\"active\">$menu->{$k1}{'caption'}</a></li>";
	} else {
	    print "<li><a href=\"$link\">$menu->{$k1}{'caption'}</a></li>";
	}
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
	<h4><span>Side</span>menu</h4>
	<ul class="links">
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

	print "<a href=\"$link\">$hash->{'caption'}</a></li>";
    }

    print <<EOF
	</ul>
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

sub openpage {
    my $title = shift;
    my $boh = shift;
    my $extrahead = shift;

    @URI=split ('\?',  $ENV{'REQUEST_URI'} );
    &General::readhash("${swroot}/main/settings", \%settings);
    &genmenu();

    my $h2 = gettitle($menu);

    $title = "-= IPFire - $title =-";
    if ($settings{'WINDOWWITHHOSTNAME'} eq 'on') {
        $title =  "$settings{'HOSTNAME'}.$settings{'DOMAINNAME'} - $title"; 
    }

    print <<END
<?xml version='1.0' encoding='UTF-8'?>
<!DOCTYPE html PUBLIC '-//W3C//DTD XHTML 1.0 Strict//EN' 'http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd'>
<html xmlns='http://www.w3.org/1999/xhtml'>
<head>
		<title>$title</title>
    $extrahead
    <link rel="shortcut icon" href="/favicon.ico" />
    <link rel="stylesheet" type="text/css" href="/themes/darkdos/include/style.css" />
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
END
;
if ($settings{'SPEED'} ne 'off') {
print <<END
    <script type="text/javascript" src="/include/jquery.js"></script>
    <script type="text/javascript">
        var t_current;
        var t_last;
        var rxb_current;
        var rxb_last;
        var txb_current;
        var txb_last;
				function refreshInetInfo() {
						\$.ajax({
								url: '/cgi-bin/speed.cgi',
											success: function(xml){
											t_current = new Date();
											var t_diff = t_current - t_last;
											t_last = t_current;
				
											rxb_current = \$("rxb",xml).text();
											var rxb_diff = rxb_current - rxb_last;
											rxb_last = rxb_current;
				
											var rx_kbs = rxb_diff/t_diff;
											rx_kbs = Math.round(rx_kbs*10)/10;
				
											txb_current = \$("txb",xml).text();
											var txb_diff = txb_current - txb_last;
											txb_last = txb_current;
				
											var tx_kbs = txb_diff/t_diff;
											tx_kbs = Math.round(tx_kbs*10)/10;
				
											\$("#rx_kbs").text(rx_kbs + ' kb/s');
											\$("#tx_kbs").text(tx_kbs + ' kb/s');
											}
								});
								window.setTimeout("refreshInetInfo()", 3000);
						}
						\$(document).ready(function(){
						refreshInetInfo();
				});
    </script>
  </head>
  <body>
END
;
}
else {
print "</head>\n<body>";}
print <<END
<!-- IPFIRE HEADER -->

<div id="header">

	<div id="header_inner" class="fixed">

		<div id="logo">
END
;
    if ($settings{'WINDOWWITHHOSTNAME'} eq 'on') {
        print "<h1><span>$settings{'HOSTNAME'}.$settings{'DOMAINNAME'}</span></h1><br />"; 
    } else {
				print "<h1><span><a href='https://www.ipfire.org' style='text-decoration: none;'>-= IPFire =-</a></span></h1><br />";
		}
		print <<END
			<h2>+ $h2 +</h2>
		</div>

END
;
	&showmenu();

print <<END	
	</div>
</div>

<div id="main">
	<div id="main_inner" class="fixed">
		<div id="primaryContent_2columns">
			<div id="columnA_2columns">
END
;
}

sub openpagewithoutmenu {
    my $title = shift;
    my $boh = shift;
    my $extrahead = shift;

    @URI=split ('\?',  $ENV{'REQUEST_URI'} );
    &General::readhash("${swroot}/main/settings", \%settings);
    &genmenu();

    my $h2 = gettitle($menu);

    $title = "-= IPFire - $title =-";
    if ($settings{'WINDOWWITHHOSTNAME'} eq 'on') {
        $title =  "$settings{'HOSTNAME'}.$settings{'DOMAINNAME'} - $title"; 
    }

    print <<END
<?xml version='1.0' encoding='UTF-8'?>
<!DOCTYPE html PUBLIC '-//W3C//DTD XHTML 1.0 Strict//EN' 'http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd'>
<html xmlns='http://www.w3.org/1999/xhtml'>
<head>
		<title>$title</title>
		$extrahead
END
;
    if ($settings{'FX'} ne 'off') {
    print <<END
    <meta http-equiv="Page-Enter" content="blendTrans(Duration=0.5,Transition=12)" />
    <meta http-equiv="Page-Exit" content="blendTrans(Duration=0.5,Transition=12)" />
END
;
    }
    print <<END
    <link rel="shortcut icon" href="/favicon.ico" />
    <link rel="stylesheet" type="text/css" href="/include/style.css" />
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

<div id="header">

	<div id="header_inner" class="fixed">

		<div id="logo">
			<h1><span>-= IPFire =-</span></h1>
			<h2>+ $h2 +</h2>
		</div>	
	</div>
</div>

<div id="main">
	<div id="main_inner" class="fixed">
		<div id="primaryContent_2columns">
			<div id="columnA_2columns">
END
;
}

sub closepage () {
	my $status = &connectionstatus();
	my $uptime = `/usr/bin/uptime|cut -d \" \" -f 4-`;
	$uptime =~ s/year(s|)/$Lang::tr{'year'}/;
	$uptime =~ s/month(s|)/$Lang::tr{'month'}/;
	$uptime =~ s/day(s|)/$Lang::tr{'day'}/;
	$uptime =~ s/user(s|)/$Lang::tr{'user'}/;
	$uptime =~ s/load average/$Lang::tr{'uptime load average'}/;     
				
    print <<END
			</div>
		</div>

		<div id="secondaryContent_2columns">
		
			<div id="columnC_2columns">
END
;
    &showsubsection($menu);
    &showsubsubsection($menu);

	print <<END
				</div>
			</div>
			<br class="clear" />	
			<div id="footer" class="fixed">
				<b>Status:</b> $status <b>Uptime:</b> $uptime
END
;
if ($settings{'SPEED'} ne 'off') {
print <<END                        
                        <br />
                                <b>$Lang::tr{'bandwidth usage'}:</b>
				$Lang::tr{'incoming'}: <span id="rx_kbs"></span>&nbsp;$Lang::tr{'outgoing'}: <span id="tx_kbs"></span>

END
;
}
print <<END
                </div>
        </div>
</div>
</body>
</html>
END
;
}

sub openbigbox
{
}

sub closebigbox
{
}

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
