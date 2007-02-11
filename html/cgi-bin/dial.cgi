#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# $Id: dial.cgi,v 1.4.2.3 2005/02/22 22:21:55 gespinasse Exp $
#

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %cgiparams=();

$cgiparams{'ACTION'} = '';
&Header::getcgihash(\%cgiparams);

if ($cgiparams{'ACTION'} eq $Lang::tr{'dial profile'})
{
	my $profile = $cgiparams{'PROFILE'};
	my %tempcgiparams = ();
	$tempcgiparams{'PROFILE'} = '';
	&General::readhash("${General::swroot}/ppp/settings-$cgiparams{'PROFILE'}",
		\%tempcgiparams);

	# make a link from the selected profile to the "default" one.
	unlink("${General::swroot}/ppp/settings");
	link("${General::swroot}/ppp/settings-$cgiparams{'PROFILE'}",
		"${General::swroot}/ppp/settings");
	system ("/usr/bin/touch", "${General::swroot}/ppp/updatesettings");

	# read in the new params "early" so we can write secrets.
	%cgiparams = ();
	&General::readhash("${General::swroot}/ppp/settings", \%cgiparams);
	$cgiparams{'PROFILE'} = $profile;
	$cgiparams{'BACKUPPROFILE'} = $profile;
	&General::writehash("${General::swroot}/ppp/settings-$cgiparams{'PROFILE'}",
		\%cgiparams);

	# write secrets file.
	open(FILE, ">/${General::swroot}/ppp/secrets") or die "Unable to write secrets file.";
	flock(FILE, 2);
	my $username = $cgiparams{'USERNAME'};
	my $password = $cgiparams{'PASSWORD'};
	print FILE "'$username' * '$password'\n";
	chmod 0600, "${General::swroot}/ppp/secrets";
	close FILE;

	&General::log("$Lang::tr{'profile made current'} $tempcgiparams{'PROFILENAME'}"); 
	$cgiparams{'ACTION'} = "$Lang::tr{'dial'}";
}

if ($cgiparams{'ACTION'} eq $Lang::tr{'dial'}) {
	system('/etc/rc.d/init.d/red','start') == 0
	or &General::log("Dial failed: $?"); }
elsif ($cgiparams{'ACTION'} eq $Lang::tr{'hangup'}) {
	system('/etc/rc.d/init.d/red','stop') == 0
	or &General::log("Hangup failed: $?"); }
sleep 1;

print "Status: 302 Moved\nLocation: /cgi-bin/index.cgi\n\n";
