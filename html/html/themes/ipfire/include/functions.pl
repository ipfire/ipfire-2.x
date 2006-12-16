#!/usr/bin/perl

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
    &readhash("${swroot}/main/settings", \%settings);
    &genmenu();

    my $h2 = gettitle($menu);

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
    <link rel="stylesheet" type="text/css" href="/themes/ipfire/include/style.css" />
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
			<h1><span>IPFire</span></h1>
			<h2>$h2</h2>
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
    &readhash("${swroot}/main/settings", \%settings);
    &genmenu();

    my $h2 = gettitle($menu);

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
			<h1><span>IPFire</span></h1>
			<h2>$h2</h2>
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
    $uptime = `/usr/bin/uptime`;
	
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
			<b>Status:</b> $status <b>Uptime:</b>$uptime <b>Version:</b> $FIREBUILD
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
