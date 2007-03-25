#!/usr/bin/perl
#
# IPFire CGIs
#
# This file is part of the IPFire Project
# 
# This code is distributed under the terms of the GPL
#
# (c) Eric Oberlander June 2002
#
# (c) Darren Critchley June 2003 - added real time clock setting, etc
#

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %pakfiresettings=();
my $errormessage = '';

&Header::showhttpheaders();

$pakfiresettings{'ACTION'} = '';
$pakfiresettings{'VALID'} = '';

$pakfiresettings{'INSTALLED'} = '';
$pakfiresettings{'AVAIL'} = '';
$pakfiresettings{'AUTOUPD'} = '';

&Header::getcgihash(\%pakfiresettings);

if ($pakfiresettings{'ACTION'} eq $Lang::tr{'save'})
{

}

&General::readhash("${General::swroot}/pakfire/settings", \%pakfiresettings);


my %selected=();
my %checked=();

$checked{'AUTOUPD'}{'off'} = '';
$checked{'AUTOUPD'}{'on'} = '';
$checked{'AUTOUPD'}{$pakfiresettings{'AUTOUPD'}} = "checked='checked'";

&Header::openpage($Lang::tr{'pakfire configuration'}, 1);

&Header::openbigbox('100%', 'left', '', $errormessage);

# DPC move error message to top so it is seen!
if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<font class='base'>$errormessage&nbsp;</font>\n";
	&Header::closebox();
	}

&Header::closebox();

&Header::closebigbox();

&Header::closepage();

