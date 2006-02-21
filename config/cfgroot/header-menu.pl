sub genmenu
{
    ... snip ...
    if ( ! -e "${General::swroot}/proxy/enable" && ! -e "${General::swroot}/proxy/enable_blue" ) {
	splice (@{$menu{'2.status'}{'subMenu'}}, 4, 1);
	splice (@{$menu{'7.mainlogs'}{'subMenu'}}, 2, 1);
    }

    # Read additionnal menus entry
    # this have to be hardened and accepted. To be extended.
    opendir (DIR, "${General::swroot}/addon-menu");
    while (my $menuitem = readdir (DIR)) {

	if ( $menuitem =~ /^menu\.([1-6]\..*)\..*/) {  #model is "menu.(N.submenu).filename"
	    my $submenu = $1;
	    open (FILE,"${General::swroot}/addon-menu/$menuitem") or die;
	    while (my $text = <FILE>) {	    # file may content many entry
		splice (@{$menu{$submenu}{'subMenu'}} ,-1,0, [ eval($text) ] );
	    }
	    close (FILE);
	}
    }
    closedir (DIR);
}
