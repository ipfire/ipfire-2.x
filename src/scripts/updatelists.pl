#!/usr/bin/perl

use strict;
use LWP::UserAgent;
require "CONFIG_ROOT/general-functions.pl";

my @this;
my $return = &downloadlist();
if($return && $return->is_success) {
	unless(open(LIST, ">CONFIG_ROOT/patches/available")) {
		die "Could not open available lists database.";
	}
	flock LIST, 2;
	@this = split(/----START LIST----\n/,$return->content);
	print LIST $this[1];
	close(LIST);
} else {
	die "Could not download patches list.";
}

sub downloadlist {
	unless(-e "CONFIG_ROOT/red/active") {
		die "Not connected.";
	}

	my $downloader = LWP::UserAgent->new;
	$downloader->timeout(5);

	my %proxysettings;
	&General::readhash("CONFIG_ROOT/proxy/settings", \%proxysettings);

	if ($_=$proxysettings{'UPSTREAM_PROXY'}) {
		my ($peer, $peerport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);
		if ($proxysettings{'UPSTREAM_USER'}) {
			$downloader->proxy("http","http://$proxysettings{'UPSTREAM_USER'}:$proxysettings{'UPSTREAM_PASSWORD'}@"."$peer:$peerport/");
		} else {
			$downloader->proxy("http","http://$peer:$peerport/");
		}
	}

	return $downloader->get("http://www.ipcop.org/patches/${General::version}", 'Cache-Control', 'no-cache');
}
