#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2016 Alexander Marx alexander.marx@ipfire.org                 #
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

use strict;
use URI::Escape;
use CGI::Carp qw(fatalsToBrowser);

require '/var/ipfire/general-functions.pl';

my $url = "http://$ENV{'SERVER_NAME'}$ENV{'REQUEST_URI'}";
my $safe_url = uri_escape($url);
my $settings="${General::swroot}/captive/settings";
my $ethernet="${General::swroot}/ethernet/settings";
my %settingshash=();
my %ethernethash=();
my $green_ip;
my $green_mask;
my $blue_ip;
my $blue_mask;
my $target;
#Read settings
&General::readhash("$settings", \%settingshash) if(-f $settings);
&General::readhash("$ethernet", \%ethernethash) if(-f $ethernet);

#Get Clients IP-Address
my $ip_address = $ENV{X_FORWARDED_FOR} || $ENV{REMOTE_ADDR} ||"";

if($settingshash{'ENABLE_GREEN'} eq "on" && $ethernethash{'GREEN_ADDRESS'} ne ''){
		$green_ip=$ethernethash{'GREEN_ADDRESS'};
		$green_mask=$ethernethash{'GREEN_NETMASK'};
		
		if (&General::IpInSubnet($ip_address,$ethernethash{'GREEN_ADDRESS'},$ethernethash{'GREEN_NETMASK'})){
			$target = $green_ip;
		}
}elsif($settingshash{'ENABLE_BLUE'} eq "on" &&$ethernethash{'BLUE_ADDRESS'} ne '' ){
		$blue_ip=$ethernethash{'BLUE_ADDRESS'};
		$blue_mask=$ethernethash{'BLUE_NETMASK'};
		
		if (&General::IpInSubnet($ip_address,$ethernethash{'BLUE_ADDRESS'},$ethernethash{'BLUE_NETMASK'})){
			$target = $blue_ip;
		}
}else{
	exit 0;
}

print "Status: 302 Moved Temporarily\n";
print "Location: http://$target:1013/cgi-bin/index.cgi?redirect=$safe_url\n";
print "Connection: close\n\n";
