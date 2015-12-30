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

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::colouryellow} );
undef (@dummy);

our %dhcpsettings=();
our %netsettings=();
my %mainsettings=();
my %timesettings=();
my $setting = "${General::swroot}/dhcp/settings";
our $filename1 = "${General::swroot}/dhcp/advoptions"; 	# Field separator is TAB in this file (comma is standart)
									# because we need commas in the some data
our $filename2 = "${General::swroot}/dhcp/fixleases";
our $filename3 = "${General::swroot}/dhcp/advoptions-list";	# Describe the allowed syntax for dhcp options
my $errormessage = '';
my $warnNTPmessage = '';
my @nosaved=();
my %color = ();

#Basic syntax allowed for new Option definition. Not implemented: RECORDS & array of RECORDS 
our $OptionTypes = 'boolean|((un)?signed )?integer (8|16|32)|ip-address|text|string|encapsulate \w+|array of ip-address';

&Header::showhttpheaders();
our @ITFs=('GREEN');
if (&Header::blue_used()){push(@ITFs,'BLUE');}

#Settings1 for the first screen box
foreach my $itf (@ITFs) {
    $dhcpsettings{"ENABLE_${itf}"} = 'off';
    $dhcpsettings{"ENABLEBOOTP_${itf}"} = 'off';
    $dhcpsettings{"START_ADDR_${itf}"} = '';
    $dhcpsettings{"END_ADDR_${itf}"} = '';
    $dhcpsettings{"DOMAIN_NAME_${itf}"} = '';
    $dhcpsettings{"DEFAULT_LEASE_TIME_${itf}"} = '';
    $dhcpsettings{"MAX_LEASE_TIME_${itf}"} = '';
    $dhcpsettings{"WINS1_${itf}"} = '';
    $dhcpsettings{"WINS2_${itf}"} = '';
    $dhcpsettings{"DNS1_${itf}"} = '';
    $dhcpsettings{"DNS2_${itf}"} = '';
    $dhcpsettings{"NTP1_${itf}"} = '';
    $dhcpsettings{"NTP2_${itf}"} = '';
    $dhcpsettings{"NEXT_${itf}"} = '';
    $dhcpsettings{"FILE_${itf}"} = '';
    $dhcpsettings{"DNS_UPDATE_KEY_NAME_${itf}"} = '';
    $dhcpsettings{"DNS_UPDATE_KEY_SECRET_${itf}"} = '';
    $dhcpsettings{"DNS_UPDATE_KEY_ALGO_${itf}"} = '';
}

$dhcpsettings{'SORT_FLEASELIST'} = 'FIPADDR';
$dhcpsettings{'SORT_LEASELIST'} = 'IPADDR';

# DNS Update settings
$dhcpsettings{'DNS_UPDATE_ENABLED'} = 'off';

#Settings2 for editing the multi-line list
#Must not be saved with writehash !
$dhcpsettings{'FIX_MAC'} = '';
$dhcpsettings{'FIX_ADDR'} = '';
$dhcpsettings{'FIX_ENABLED'} = 'off';
$dhcpsettings{'FIX_NEXTADDR'} = '';
$dhcpsettings{'FIX_FILENAME'} = '';
$dhcpsettings{'FIX_ROOTPATH'} = '';
$dhcpsettings{'FIX_REMARK'} = '';
$dhcpsettings{'ACTION'} = '';
$dhcpsettings{'KEY1'} = '';
$dhcpsettings{'KEY2'} = '';
@nosaved=('FIX_MAC','FIX_ADDR','FIX_ENABLED','FIX_NEXTADDR',
	    'FIX_FILENAME','FIX_ROOTPATH','FIX_REMARK');

$dhcpsettings{'ADVOPT_ENABLED'} = '';
$dhcpsettings{'ADVOPT_NAME'} = '';
$dhcpsettings{'ADVOPT_DATA'} = '';
unshift (@nosaved,'ADVOPT_ENABLED','ADVOPT_NAME','ADVOPT_DATA');
foreach my $itf (@ITFs) {
    $dhcpsettings{"ADVOPT_SCOPE_${itf}"} = 'off';
    unshift (@nosaved, "ADVOPT_SCOPE_${itf}");
}

# Read Ipcop settings
&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("${General::swroot}/time/settings", \%timesettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

#Get GUI values
&Header::getcgihash(\%dhcpsettings);

open(FILE, "$filename1") or die 'Unable to open dhcp advanced options file.';
our @current1 = <FILE>;
close(FILE);
# Extract OptionDefinition
foreach my $line (@current1) {
    #chomp($line);   # remove newline        #don't know why, but this remove newline in @current1 .... !
    my @temp = split(/\t/,$line);
    AddNewOptionDefinition ($temp[1] . ' ' . $temp[2]);
}

open(FILE, "$filename2") or die 'Unable to open fixed leases file.';
our @current2 = <FILE>;
close(FILE);

# Check Settings1 first because they are needed by &buildconf
if ($dhcpsettings{'ACTION'} eq $Lang::tr{'save'}) {
    foreach my $itf (@ITFs) {
	if ($dhcpsettings{"ENABLE_${itf}"} eq 'on' ) {
	    # "Start" is defined, need "End" and vice versa
	    if ($dhcpsettings{"START_ADDR_${itf}"}) {
		if (!(&General::validip($dhcpsettings{"START_ADDR_${itf}"}))) {
		    $errormessage = "DHCP on ${itf}: " . $Lang::tr{'invalid start address'};
		    goto ERROR;
		}
		if (!$dhcpsettings{"END_ADDR_${itf}"}) {
		    $errormessage = "DHCP on ${itf}: " . $Lang::tr{'invalid end address'};
		    goto ERROR;
		}
		if (! &General::IpInSubnet ( $dhcpsettings{"START_ADDR_${itf}"}, 
				    $netsettings{"${itf}_NETADDRESS"},
				    $netsettings{"${itf}_NETMASK"})) {
		    $errormessage = "DHCP on ${itf}: " . $Lang::tr{'invalid start address'};
		    goto ERROR;
		}
	    }
	    
	    if ($dhcpsettings{"END_ADDR_${itf}"}) {
		if (!(&General::validip($dhcpsettings{"END_ADDR_${itf}"}))) {
		    $errormessage = "DHCP on ${itf}: " . $Lang::tr{'invalid end address'};
		    goto ERROR;
		}
		if (!$dhcpsettings{"START_ADDR_${itf}"}) {
		    $errormessage = "DHCP on ${itf}: " . $Lang::tr{'invalid start address'};
		    goto ERROR;
		}
		if (! &General::IpInSubnet ( $dhcpsettings{"END_ADDR_${itf}"}, 
				    $netsettings{"${itf}_NETADDRESS"},
				    $netsettings{"${itf}_NETMASK"})) { 
		    $errormessage = "DHCP on ${itf}: " . $Lang::tr{'invalid end address'};
		    goto ERROR;
		}
		#swap if necessary! (support 255.255.0.0 range, I doubt we need more) GE
		my @startoct = split (/\./, $dhcpsettings{"START_ADDR_${itf}"});
		my @endoct   = split (/\./, $dhcpsettings{"END_ADDR_${itf}"});
		if ( $endoct[2]*256+$endoct[3] < $startoct[2]*256+$startoct[3] ) {
		    ($dhcpsettings{"START_ADDR_${itf}"},$dhcpsettings{"END_ADDR_${itf}"}) =
			($dhcpsettings{"END_ADDR_${itf}"},$dhcpsettings{"START_ADDR_${itf}"});
		}
	    }

	    if (!($dhcpsettings{"DEFAULT_LEASE_TIME_${itf}"} =~ /^\d+$/)) {
		$errormessage = "DHCP on ${itf}: " . $Lang::tr{'invalid default lease time'} . $dhcpsettings{'DEFAULT_LEASE_TIME_${itf}'};
		goto ERROR;
	    }

	    if (!($dhcpsettings{"MAX_LEASE_TIME_${itf}"} =~ /^\d+$/)) {
		$errormessage = "DHCP on ${itf}: " . $Lang::tr{'invalid max lease time'} . $dhcpsettings{'MAX_LEASE_TIME_${itf}'};
		goto ERROR;
	    }

	    if ($dhcpsettings{"DNS1_${itf}"}) {
		if (!(&General::validip($dhcpsettings{"DNS1_${itf}"}))) {
			$errormessage = "DHCP on ${itf}: " . $Lang::tr{'invalid primary dns'};
			goto ERROR;
		}
	    }
	    if ($dhcpsettings{"DNS2_${itf}"}) {
		if (!(&General::validip($dhcpsettings{"DNS2_${itf}"}))) {
			$errormessage = "DHCP on ${itf}: " . $Lang::tr{'invalid secondary dns'};
			goto ERROR;
		}
		if (! $dhcpsettings{"DNS1_${itf}"}) {
			$errormessage = "DHCP on ${itf}: " . $Lang::tr{'cannot specify secondary dns without specifying primary'}; 
			goto ERROR;
		}
	    }

	    if ($dhcpsettings{"WINS1_${itf}"}) {
		if (!(&General::validip($dhcpsettings{"WINS1_${itf}"}))) {
			$errormessage = "DHCP on ${itf}: " . $Lang::tr{'invalid wins address'};
			goto ERROR;
		}
	    }
	    if ($dhcpsettings{"WINS2_${itf}"}) {
		if (!(&General::validip($dhcpsettings{"WINS2_${itf}"})))	{
			$errormessage = "DHCP on ${itf}: " . $Lang::tr{'invalid wins address'};
			goto ERROR;
		}
		if (! $dhcpsettings{"WINS1_${itf}"} ) {
			$errormessage = "DHCP on ${itf}: " . $Lang::tr{'cannot specify secondary wins without specifying primary'};
			goto ERROR;
		}		
	    }
	    if ($dhcpsettings{"NEXT_${itf}"}) {
		if (!(&General::validip($dhcpsettings{"NEXT_${itf}"}))) {
			$errormessage = "next-server on ${itf}: " . $Lang::tr{'invalid ip'};
			goto ERROR;
		}
	    }
	    if ($dhcpsettings{"NTP1_${itf}"}) {
		if (!(&General::validip($dhcpsettings{"NTP1_${itf}"}))) {
			$errormessage = "DHCP on ${itf}: " . $Lang::tr{'invalid primary ntp'};
			goto ERROR;
		}
		if ($dhcpsettings{"NTP1_${itf}"} eq $netsettings{"${itf}_ADDRESS"} && ($timesettings{'ENABLECLNTP'} ne 'on')) {
			$warnNTPmessage = "DHCP on ${itf}: " . $Lang::tr{'local ntp server specified but not enabled'};
			#goto ERROR;
		}
	    }
	    if ($dhcpsettings{"NTP2_${itf}"}) {
		if (!(&General::validip($dhcpsettings{"NTP2_${itf}"}))) {
			$errormessage = "DHCP on ${itf}: " . $Lang::tr{'invalid secondary ntp'};
			goto ERROR;
		}
		if ($dhcpsettings{"NTP2_${itf}"} eq $netsettings{"${itf}_ADDRESS"} && ($timesettings{'ENABLECLNTP'} ne 'on')) {
			$warnNTPmessage = "DHCP on ${itf}: " . $Lang::tr{'local ntp server specified but not enabled'};
			#goto ERROR;
		}
		if (! $dhcpsettings{"NTP1_${itf}"}) {
			$errormessage = "DHCP on ${itf}: " . $Lang::tr{'cannot specify secondary ntp without specifying primary'};
			goto ERROR;
		}
	    }
	} # enabled
    }#loop interface verify

    map (delete ($dhcpsettings{$_}) ,@nosaved,'ACTION','KEY1','KEY2','q');	# Must not be saved
    &General::writehash($setting, \%dhcpsettings);		# Save good settings
    $dhcpsettings{'ACTION'} = $Lang::tr{'save'};		# create an 'ACTION'
    map ($dhcpsettings{$_} = '',@nosaved,'KEY1','KEY2');	# and reinit vars to empty
    &buildconf;
    ERROR:   							# Leave the faulty field untouched
} else {
    &General::readhash($setting, \%dhcpsettings);   		# Get saved settings and reset to good if needed
}

## Sorting of fixed leases
if ($ENV{'QUERY_STRING'} =~ /^FETHER|^FIPADDR/ ) {
    my $newsort=$ENV{'QUERY_STRING'};
    my $act=$dhcpsettings{'SORT_FLEASELIST'};
    #Reverse actual sort ?
    if ($act =~ $newsort) {
	my $Rev='';
	if ($act !~ 'Rev') {
	    $Rev='Rev';
	}
	$newsort.=$Rev;
    }
    $dhcpsettings{'SORT_FLEASELIST'}=$newsort;
    map (delete ($dhcpsettings{$_}) ,@nosaved,'ACTION','KEY1','KEY2', 'q');	# Must never be saved
    &General::writehash($setting, \%dhcpsettings);
    &sortcurrent2;
    $dhcpsettings{'ACTION'} = 'SORT';			# create an 'ACTION'
    map ($dhcpsettings{$_} = '',@nosaved,'KEY1','KEY2');# and reinit vars to empty 
}

#Sorting of allocated leases
&Header::CheckSortOrder;


## Now manipulate the two multi-line list with Settings2. 
#  '1' suffix is for ADVANCED OPTIONS
#  '2' suffix is for FIXED LEASES

# Toggle enable/disable field on specified options.

if ($dhcpsettings{'ACTION'} eq $Lang::tr{'toggle enable disable'}.'1') {
    #move out new line
    chomp(@current1[$dhcpsettings{'KEY1'}]);
    my @temp = split(/\t/,@current1[$dhcpsettings{'KEY1'}]);		#use TAB separator !
    $temp[0] = $temp[0] eq 'on' ? '' : 'on';    # Toggle the field
    @current1[$dhcpsettings{'KEY1'}] = join ("\t",@temp)."\n";
    $dhcpsettings{'KEY1'} = ''; # End edit mode
    &General::log($Lang::tr{'dhcp advopt modified'});
    open(FILE, ">$filename1") or die 'Unable to open dhcp advanced options file.';
    print FILE @current1;
    close(FILE);
	
    #Write changes to dhcpd.conf.
    &buildconf;
}

    

if ($dhcpsettings{'ACTION'} eq $Lang::tr{'add'}.'1' &&
	$dhcpsettings{'SUBMIT'} ne $Lang::tr{'dhcp advopt help'}) {
    $dhcpsettings{'ADVOPT_NAME'} =~ s/[^ \w-]//g;  	# prevent execution of code by removing everything except letters/space
    $dhcpsettings{'ADVOPT_DATA'} =~ s/`//g;		# back tik ` ? not allowed !

    if ($dhcpsettings{'ADVOPT_DATA'} eq '') {
	$errormessage=$Lang::tr{'dhcp advopt blank value'};
    }
    
    # Test for a new option definition string (join field name & data)
    if (ExistNewOptionDefinition ($dhcpsettings{'ADVOPT_NAME'} . ' ' . $dhcpsettings{'ADVOPT_DATA'})) {
	#only edit permitted if option definition exists
	$errormessage = $Lang::tr{'dhcp advopt definition exists'} if ($dhcpsettings{'KEY1'} eq '');
	$dhcpsettings{'ADVOPT_ENABLED'} = 'on';			# force active
	map ($dhcpsettings{"ADVOPT_SCOPE_$_"} = 'off', @ITFs);	# force global
    } elsif (AddNewOptionDefinition ($dhcpsettings{'ADVOPT_NAME'} . ' ' . $dhcpsettings{'ADVOPT_DATA'})) {
	#was a new option definition
	$dhcpsettings{'ADVOPT_ENABLED'} = 'on';			# force active
	map ($dhcpsettings{"ADVOPT_SCOPE_$_"} = 'off', @ITFs);	# force global
    } elsif (ValidNewOption ($dhcpsettings{'ADVOPT_NAME'} . ' ' . $dhcpsettings{'ADVOPT_DATA'})) {
	#was a new option
    } elsif (! `grep "\$option $dhcpsettings{'ADVOPT_NAME'} " $filename3`) {
	$errormessage=$Lang::tr{'dhcp advopt unknown'}.': '.$dhcpsettings{'ADVOPT_NAME'};
    }

    unless ($errormessage) {
	
	my $scope = '';
	foreach my $itf (@ITFs) {  # buils "RED,GREEN,ORANGE,... based on selection
	    $scope .= $dhcpsettings{"ADVOPT_SCOPE_${itf}"} eq 'on' ? "\t$itf" : "\toff" ;
	}
	if ($dhcpsettings{'KEY1'} eq '') { #add or edit ?  TAB separator !
	    unshift (@current1, "$dhcpsettings{'ADVOPT_ENABLED'}\t$dhcpsettings{'ADVOPT_NAME'}\t$dhcpsettings{'ADVOPT_DATA'}$scope\n");
	    &General::log($Lang::tr{'dhcp advopt added'});
	} else {
	    @current1[$dhcpsettings{'KEY1'}] = "$dhcpsettings{'ADVOPT_ENABLED'}\t$dhcpsettings{'ADVOPT_NAME'}\t$dhcpsettings{'ADVOPT_DATA'}$scope\n";
	    $dhcpsettings{'KEY1'} = '';       # End edit mode
	    &General::log($Lang::tr{'dhcp advopt modified'});
	}

        #Write changes to dhcpd.conf.
        &sortcurrent1;    # sort newly added/modified entry
        &buildconf;       # before calling buildconf which use fixed lease file !
    }
}

if ($dhcpsettings{'ACTION'} eq $Lang::tr{'edit'}.'1') {
    #move out new line
    my $line = @current1[$dhcpsettings{'KEY1'}];
    chomp($line);
    my @temp = split(/\t/, $line);
    $dhcpsettings{'ADVOPT_ENABLED'}=$temp[0];
    $dhcpsettings{'ADVOPT_NAME'}=$temp[1];
    $dhcpsettings{'ADVOPT_DATA'}=$temp[2];

    # read next fields which are the name (color) of an interface if this interface is scoped
    for (my $key=0; $key<@ITFs; $key++) {
	my $itf = $temp[3+$key];
	if ($itf ne 'off') # Only is an interface name is read
	{
	    $dhcpsettings{"ADVOPT_SCOPE_${itf}"} = 'on';
	}    
    }
}

if ($dhcpsettings{'ACTION'} eq $Lang::tr{'remove'}.'1') {
    splice (@current1,$dhcpsettings{'KEY1'},1);
    open(FILE, ">$filename1") or die 'Unable to open dhcp advanced options file.';
    print FILE @current1;
    close(FILE);
    $dhcpsettings{'KEY1'} = '';				# End remove mode
    &General::log($Lang::tr{'dhcp advopt removed'});
    #Write changes to dhcpd.conf.
    &buildconf;
}
#end KEY1


# Toggle enable/disable field on specified lease.
if ($dhcpsettings{'ACTION'} eq $Lang::tr{'toggle enable disable'}.'2') {
    #move out new line
    chomp(@current2[$dhcpsettings{'KEY2'}]);
    my @temp = split(/\,/,@current2[$dhcpsettings{'KEY2'}]);
    $temp[2] = $temp[2] eq 'on' ? '' : 'on';    # Toggle the field
    @current2[$dhcpsettings{'KEY2'}] = join (',',@temp)."\n";
    $dhcpsettings{'KEY2'} = ''; # End edit mode
    &General::log($Lang::tr{'fixed ip lease modified'});
    open(FILE, ">$filename2") or die 'Unable to open fixed leases file.';
    print FILE @current2;
    close(FILE);
	
    #Write changes to dhcpd.conf.
    &buildconf;
}

if ($dhcpsettings{'ACTION'} eq $Lang::tr{'add'}.'2') {
    $dhcpsettings{'FIX_MAC'} =~ tr/-/:/;
    unless(&General::validip($dhcpsettings{'FIX_ADDR'})) { $errormessage = $Lang::tr{'invalid fixed ip address'}; }
    unless(&General::validmac($dhcpsettings{'FIX_MAC'})) { $errormessage = $Lang::tr{'invalid fixed mac address'}; }
    if ($dhcpsettings{'FIX_NEXTADDR'}) {
        unless(&General::validip($dhcpsettings{'FIX_NEXTADDR'})) { $errormessage = $Lang::tr{'invalid fixed ip address'}; }
    }
	
    my $key = 0;
    CHECK:foreach my $line (@current2) {
        my @temp = split(/\,/,$line);
        if($dhcpsettings{'KEY2'} ne $key) {
 	    # same MAC is OK on different subnets. This test is not complete because
	    # if ip are not inside a known subnet, I don't warn.
	    # Also it may be needed to put duplicate fixed lease in their right subnet definition..
	    foreach my $itf (@ITFs) {
		my $scoped = &General::IpInSubnet($dhcpsettings{'FIX_ADDR'},
						  $netsettings{"${itf}_NETADDRESS"}, 
						  $netsettings{"${itf}_NETMASK"}) &&
						  $dhcpsettings{"ENABLE_${itf}"} eq 'on';
		if ( $scoped &&
		    (lc($dhcpsettings{'FIX_MAC'}) eq lc($temp[0])) &&
		    &General::IpInSubnet($temp[1],
					 $netsettings{"${itf}_NETADDRESS"}, 
					 $netsettings{"${itf}_NETMASK"})) {
		    $errormessage = "$Lang::tr{'mac address in use'} $dhcpsettings{'FIX_MAC'}";
		    last CHECK;
		}
	    }
	}
	$key++;
    }

    unless ($errormessage) {
	$dhcpsettings{'FIX_REMARK'} = &Header::cleanhtml($dhcpsettings{'FIX_REMARK'});
	$dhcpsettings{'FIX_NEXTADDR'} = &Header::cleanhtml($dhcpsettings{'FIX_NEXTADDR'});
	$dhcpsettings{'FIX_FILENAME'} = &Header::cleanhtml($dhcpsettings{'FIX_FILENAME'});
	$dhcpsettings{'FIX_ROOTPATH'} = &Header::cleanhtml($dhcpsettings{'FIX_ROOTPATH'});
	if ($dhcpsettings{'KEY2'} eq '') { #add or edit ?
	    unshift (@current2, "$dhcpsettings{'FIX_MAC'},$dhcpsettings{'FIX_ADDR'},$dhcpsettings{'FIX_ENABLED'},$dhcpsettings{'FIX_NEXTADDR'},$dhcpsettings{'FIX_FILENAME'},$dhcpsettings{'FIX_ROOTPATH'},$dhcpsettings{'FIX_REMARK'}\n");
	    &General::log($Lang::tr{'fixed ip lease added'});

	    # Enter edit mode
	    $dhcpsettings{'KEY2'} = $key;
	} else {
	    @current2[$dhcpsettings{'KEY2'}] = "$dhcpsettings{'FIX_MAC'},$dhcpsettings{'FIX_ADDR'},$dhcpsettings{'FIX_ENABLED'},$dhcpsettings{'FIX_NEXTADDR'},$dhcpsettings{'FIX_FILENAME'},$dhcpsettings{'FIX_ROOTPATH'},$dhcpsettings{'FIX_REMARK'}\n";
	    $dhcpsettings{'KEY2'} = '';       # End edit mode
	    &General::log($Lang::tr{'fixed ip lease modified'});
	}

        #Write changes to dhcpd.conf.
        &sortcurrent2;    # sort newly added/modified entry
        &buildconf;       # before calling buildconf which use fixed lease file !
    }
}

if ($dhcpsettings{'ACTION_ALL'} eq '+') {
    my $news = 0;
    foreach (keys %dhcpsettings) {
        if (/^(\d+\.\d+\.\d+\.\d+)-([0-9a-fA-F:]+)$/) {     # checked names are index of the line
            my $ip=$1;
            my $mac=$2;
            if (!grep (/$2/,@current2)) {
                unshift (@current2, "$mac,$ip,on,,,,imported\n");
                $news++;
            }
        }
    }
    if ($news) {
        #Write changes to dhcpd.conf.
        $warnNTPmessage = $Lang::tr{'fixed ip lease added'}."($news)";
        &General::log($warnNTPmessage);
        &sortcurrent2;    # sort newly added/modified entry
        &buildconf;       # before calling buildconf which use fixed lease file !
    }
}

if ($dhcpsettings{'ACTION'} eq $Lang::tr{'edit'}.'2') {
    #move out new line
    my $line = @current2[$dhcpsettings{'KEY2'}];
    chomp($line);
    my @temp = split(/\,/, $line);
    $dhcpsettings{'FIX_MAC'}=$temp[0];
    $dhcpsettings{'FIX_ADDR'}=$temp[1];
    $dhcpsettings{'FIX_ENABLED'}=$temp[2];
    $dhcpsettings{'FIX_NEXTADDR'}=$temp[3];
    $dhcpsettings{'FIX_FILENAME'}=$temp[4];
    $dhcpsettings{'FIX_ROOTPATH'}=$temp[5];
    $dhcpsettings{'FIX_REMARK'}=$temp[6];
}

if ($dhcpsettings{'ACTION'} eq $Lang::tr{'remove'}.'2') {
    splice (@current2,$dhcpsettings{'KEY2'},1);
    open(FILE, ">$filename2") or die 'Unable to open fixed lease file.';
    print FILE @current2;
    close(FILE);
    $dhcpsettings{'KEY2'} = '';				# End remove mode
    &General::log($Lang::tr{'fixed ip lease removed'});
    #Write changes to dhcpd.conf.
    &buildconf;
}
#end KEY2 defined




if ($dhcpsettings{'ACTION'} eq '' ) { # First launch from GUI

    # Set default DHCP values only if blank and disabled
    foreach my $itf (@ITFs) {
	if ($dhcpsettings{"ENABLE_${itf}"} ne 'on' ) {
	    $dhcpsettings{"DNS1_${itf}"} = $netsettings{"${itf}_ADDRESS"};
	    $dhcpsettings{"DEFAULT_LEASE_TIME_${itf}"} = '60';
	    $dhcpsettings{"MAX_LEASE_TIME_${itf}"} = '120';
	    $dhcpsettings{"DOMAIN_NAME_${itf}"} = $mainsettings{'DOMAINNAME'};
	}
    }
    $dhcpsettings{'FIX_ENABLED'} = 'on';
}

&Header::openpage($Lang::tr{'dhcp configuration'}, 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
    &Header::openbox('100%', 'left', $Lang::tr{'error messages'});
    print "<font class='base'>$errormessage&nbsp;</font>\n";
    &Header::closebox();
}
if ($warnNTPmessage) {
    $warnNTPmessage = "<font color=${Header::colourred}><b>$Lang::tr{'capswarning'}</b></font>: $warnNTPmessage";
}

&Header::openbox('100%', 'left', 'DHCP');
print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>";

foreach my $itf (@ITFs) {
    my %checked=();
    $checked{'ENABLE'}{'on'} = ( $dhcpsettings{"ENABLE_${itf}"} ne 'on') ? '' : "checked='checked'";
    $checked{'ENABLEBOOTP'}{'on'} = ( $dhcpsettings{"ENABLEBOOTP_${itf}"} ne 'on') ? '' : "checked='checked'";

    if ($netsettings{"${itf}_DEV"} ne '' ) { # Show only defined interface
	my $lc_itf=lc($itf);
print <<END
<table width='100%'>
<tr>
    <td width='25%' class='boldbase'><b><font color='${lc_itf}'>$Lang::tr{"$lc_itf interface"}</font></b></td>
    <td class='base'>$Lang::tr{'enabled'}
    <input type='checkbox' name='ENABLE_${itf}' $checked{'ENABLE'}{'on'} /></td>
    <td width='25%' class='base'>$Lang::tr{'ip address'}<br />$Lang::tr{'netmask'}:</td><td><b>$netsettings{"${itf}_ADDRESS"}<br />$netsettings{"${itf}_NETMASK"}</b></td>
</tr><tr>
    <td width='25%' class='base'>$Lang::tr{'start address'}&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td width='25%'><input type='text' name='START_ADDR_${itf}' value='$dhcpsettings{"START_ADDR_${itf}"}' /></td>
    <td width='25%' class='base'>$Lang::tr{'end address'}&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td width='25%'><input type='text' name='END_ADDR_${itf}' value='$dhcpsettings{"END_ADDR_${itf}"}' /></td>
</tr><tr>
    <td class='base'>$Lang::tr{'default lease time'}&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td><input type='text' name='DEFAULT_LEASE_TIME_${itf}' value='$dhcpsettings{"DEFAULT_LEASE_TIME_${itf}"}' /></td>
    <td class='base'>$Lang::tr{'max lease time'}&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td><input type='text' name='MAX_LEASE_TIME_${itf}' value='$dhcpsettings{"MAX_LEASE_TIME_${itf}"}' /></td>
</tr><tr>
    <td class='base'>$Lang::tr{'domain name suffix'}</td>
    <td><input type='text' name='DOMAIN_NAME_${itf}' value='$dhcpsettings{"DOMAIN_NAME_${itf}"}' /></td>
    <td>$Lang::tr{'dhcp allow bootp'}:</td>
    <td><input type='checkbox' name='ENABLEBOOTP_${itf}' $checked{'ENABLEBOOTP'}{'on'} /></td>
</tr><tr>
    <td class='base'>$Lang::tr{'primary dns'}&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td><input type='text' name='DNS1_${itf}' value='$dhcpsettings{"DNS1_${itf}"}' /></td>
    <td class='base'>$Lang::tr{'secondary dns'}</td>
    <td><input type='text' name='DNS2_${itf}' value='$dhcpsettings{"DNS2_${itf}"}' /></td>
</tr><tr>
    <td class='base'>$Lang::tr{'primary ntp server'}:</td>
    <td><input type='text' name='NTP1_${itf}' value='$dhcpsettings{"NTP1_${itf}"}' /></td>
    <td class='base'>$Lang::tr{'secondary ntp server'}:</td>
    <td><input type='text' name='NTP2_${itf}' value='$dhcpsettings{"NTP2_${itf}"}' /></td>
</tr><tr>
    <td class='base'>$Lang::tr{'primary wins server address'}:</td>
    <td><input type='text' name='WINS1_${itf}' value='$dhcpsettings{"WINS1_${itf}"}' /></td>
    <td class='base'>$Lang::tr{'secondary wins server address'}:</td>
    <td><input type='text' name='WINS2_${itf}' value='$dhcpsettings{"WINS2_${itf}"}' /></td>
</tr><tr>
    <td class='base'>next-server:</td>
    <td><input type='text' name='NEXT_${itf}' value='$dhcpsettings{"NEXT_${itf}"}' /></td>
    <td class='base'>filename:</td>
    <td><input type='text' name='FILE_${itf}' value='$dhcpsettings{"FILE_${itf}"}' /></td>
</tr>
</table>
<hr />
END
;
    }# Show only defined interface
}#foreach itf
print <<END
<table width='100%'>
<tr>
    <td class='base' width='25%'><img src='/blob.gif' align='top' alt='*' />&nbsp;$Lang::tr{'required field'}</td>
    <td class='base' width='30%'>$warnNTPmessage</td>
    <td width='40%' align='right'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
</tr>
</table>
END
;
&Header::closebox();

# DHCP DNS update support (RFC2136)
&Header::openbox('100%', 'left', $Lang::tr{'dhcp dns update'});

my %checked = ();
$checked{'DNS_UPDATE_ENABLED'}{'on'} = ( $dhcpsettings{'DNS_UPDATE_ENABLED'} ne 'on') ? '' : "checked='checked'";

print <<END
<table  width='100%'>
	<tr>
		<td width='25%' class='boldbase'>$Lang::tr{'dhcp dns enable update'}</td>
		<td class='base'><input type='checkbox' name='DNS_UPDATE_ENABLED' $checked{'DNS_UPDATE_ENABLED'}{'on'}>
		</td>
	<tr>
</table>

<table width='100%'>
END
;
	my @domains = ();

	# Print options for each interface.
	foreach my $itf (@ITFs) {
		# Check if DHCP for this interface is enabled.
		if ($dhcpsettings{"ENABLE_${itf}"} eq 'on') {
			# Check for same domain name.
			next if ($dhcpsettings{"DOMAIN_NAME_${itf}"} ~~ @domains);
			my $lc_itf = lc($itf);

			# Select previously configured update algorithm.
			my %selected = ();
			$selected{'DNS_UPDATE_ALGO_${inf}'}{$dhcpsettings{'DNS_UPDATE_ALGO_${inf}'}} = 'selected';

print <<END
	<tr>
		<td colspan='6'>&nbsp;</td>
	</tr>
	<tr>
		<td colspan='6' class='boldbase'><b>$dhcpsettings{"DOMAIN_NAME_${itf}"}</b></td>
	</tr>
	<tr>
		<td width='10%' class='boldbase'>$Lang::tr{'dhcp dns key name'}:</td>
		<td width='20%'><input type='text' name='DNS_UPDATE_KEY_NAME_${itf}' value='$dhcpsettings{"DNS_UPDATE_KEY_NAME_${itf}"}'></td>
		<td width='10%' class='boldbase' align='right'>$Lang::tr{'dhcp dns update secret'}:&nbsp;&nbsp;</td>
		<td width='20%'><input type='password' name='DNS_UPDATE_KEY_SECRET_${itf}' value='$dhcpsettings{"DNS_UPDATE_KEY_SECRET_${itf}"}'></td>
		<td width='10%' class='boldbase' align='right'>$Lang::tr{'dhcp dns update algo'}:&nbsp;&nbsp;</td>
		<td width='20%'>
			<select name='DNS_UPDATE_KEY_ALGO_${itf}'>
				<!-- <option value='hmac-sha1' $selected{'DNS_UPDATE_KEY_ALGO_${itf}'}{'hmac-sha1'}>HMAC-SHA1</option> -->
				<option value='hmac-md5' $selected{'DNS_UPDATE_KEY_ALGO_${itf}'}{'hmac-md5'}>HMAC-MD5</option>
			</select>
		</td>
	</tr>
END
;
	}

	# Store configured domain based on the interface
	# in the temporary variable.
	push(@domains, $dhcpsettings{"DOMAIN_NAME_${itf}"});
}
print <<END
</table>
<hr>
<table width='100%'>
	<tr>
		<td align='right'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
	</tr>
</table>
</form>
END
;

&Header::closebox();

&Header::openbox('100%', 'left', $Lang::tr{'dhcp advopt list'});
# DHCP Advanced options settings
my %checked=();
$checked{'ADVOPT_ENABLED'}{'on'} = ($dhcpsettings{'ADVOPT_ENABLED'} ne 'on') ? '' : "checked='checked'";

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'><table width='100%'>";
my $buttontext = $Lang::tr{'add'};
if ($dhcpsettings{'KEY1'} ne '') {
    $buttontext = $Lang::tr{'update'};
    print "<tr><td class='boldbase'><b>$Lang::tr{'dhcp advopt edit'}</b></td></tr>";
} else {
    print "<tr><td class='boldbase'><b>$Lang::tr{'dhcp advopt add'}</b></td></tr>"
}

#search if the 'option' is in the list and print the syntax model
my $opt = `grep "\$option $dhcpsettings{'ADVOPT_NAME'} " $filename3`;
if ($opt ne '') {
   $opt =~ s/option $dhcpsettings{'ADVOPT_NAME'}/Syntax:/;  # "option xyz abc" => "syntax: abc"
   $opt =~ s/;//;
   $opt = "<tr><td></td><td></td><td colspan='2'>$opt</td></tr>";
}
print <<END
<tr>
    <td class='base'>$Lang::tr{'dhcp advopt name'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td><input type='text' name='ADVOPT_NAME' value='$dhcpsettings{'ADVOPT_NAME'}' size='18' /></td>
    <td class='base'>$Lang::tr{'dhcp advopt value'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td><input type='text' name='ADVOPT_DATA' value='$dhcpsettings{'ADVOPT_DATA'}' size='40' /></td>
</tr>$opt<tr>
    <td class='base'>$Lang::tr{'enabled'}</td><td><input type='checkbox' name='ADVOPT_ENABLED' $checked{'ADVOPT_ENABLED'}{'on'} /></td>
    <td class='base'>$Lang::tr{'dhcp advopt scope'}:</td>
    <td>
END
;

# Put a checkbox for each interface. Checkbox visible disabled if interface is disabled  
foreach my $itf (@ITFs) {
    my $lc_itf=lc($itf);
    $checked{'ADVOPT_SCOPE_${itf}'}{'on'} = $dhcpsettings{"ADVOPT_SCOPE_${itf}"} ne 'on' ? '' : "checked='checked'";    
    print "$Lang::tr{\"${lc_itf}\"} <input type='checkbox' name='ADVOPT_SCOPE_${itf}' $checked{'ADVOPT_SCOPE_${itf}'}{'on'} ";
    print $dhcpsettings{"ENABLE_${itf}"} eq 'on' ? "/>" : "disabled='disabled' />";
    print "&nbsp; &nbsp;";
}

print <<END
    </td>
</tr>
</table>
<hr />
<table width='100%'>
<tr>
    <td class='base' width='50%'>$Lang::tr{'dhcp advopt scope help'}</td>
    <td width='50%' align='right'>
    <input type='hidden' name='ACTION' value='$Lang::tr{'add'}1' />
    <input type='submit' name='SUBMIT' value='$buttontext' />
    <input type='submit' name='SUBMIT' value='$Lang::tr{'dhcp advopt help'}' />
    <input type='hidden' name='KEY1' value='$dhcpsettings{'KEY1'}' />
    </td>
</tr>
</table>
</form>
END
;
#Edited line number (KEY1) passed until cleared by 'save' or 'remove' or 'new sort order'

# print help taken from the file describing options
if ($dhcpsettings{'SUBMIT'} eq $Lang::tr{'dhcp advopt help'}) {
    print "<hr />";
    print "<table width='100%'>";
    print "<tr><td width='30%'><b>$Lang::tr{'dhcp advopt name'}</b></td><td width='70%'><b>$Lang::tr{'dhcp advopt value'}</b></td>";
    open(FILE, "$filename3");
    my @current3 = <FILE>;
    close(FILE);
    foreach my $line (@current3) {
	$line =~ /option ([a-z0-9-]+) (.*);/;
	print "<tr><td>$1</td><td>$2</td></tr>\n";
    }
    print "<tr><td colspan='2'><hr /></td></tr>\n";
    print '<tr><td>string type</td><td>"quoted string" or 00:01:FF...</td></tr>';
    print '<tr><td>ip-address type </td><td>10.0.0.1 | www.dot.com</td></tr>';
    print '<tr><td>int,uint types</td><td>numbers</td></tr>';
    print '<tr><td>flag type</td><td>on | off</td></tr>';
    print '</table>';
    print "<hr />";
    print "<table width='100%'>";
    print "<tr><td width='30%'><b>$Lang::tr{'dhcp advopt custom definition'}</b></td><td width='70%'><b>$Lang::tr{'dhcp advopt value'}</b></td>";
    print "<tr><td>any-name </td><td> code NNN=$OptionTypes</td></tr>";
    print '<tr><td>a-string</td><td>code 100=string</td></tr>';
    print '<tr><td>a-number</td><td>code 101=signed integer 8</td></tr>';
    print '<tr><td>wpad</td><td>code 252=text</td></tr>';
    print '<tr><td>wpad</td><td>"http://www.server.fr/path-to/proxy.pac"</td></tr>';
    print '</table>';
 
}

print <<END
<hr />
<table width='100%'>
<tr>
    <td width='30%' class='boldbase' align='center'><b>$Lang::tr{'dhcp advopt name'}</b></td>
    <td width='50%' class='boldbase' align='center'><b>$Lang::tr{'dhcp advopt value'}</b></td>
    <td width='20%' class='boldbase' align='center'><b>$Lang::tr{'dhcp advopt scope'}</b></td>
    <td colspan='3' class='boldbase' align='center'><b>$Lang::tr{'action'}</b></td>
</tr>
END
;
my $key = 0;
foreach my $line (@current1) {
    my $gif = '';
    my $gdesc = '';
    chomp($line);   # remove newline
    my @temp = split(/\t/,$line);

    if ($temp[0] eq "on") {
	$gif = 'on.gif';
	$gdesc = $Lang::tr{'click to disable'};
    } else {
	$gif = 'off.gif';
	$gdesc = $Lang::tr{'click to enable'}; 
    }

    if ($dhcpsettings{'KEY1'} eq $key) {
	print "<tr bgcolor='${Header::colouryellow}'>";
    } elsif ($key % 2) {
	print "<tr bgcolor='$color{'color22'}'>";
    } else {
	print "<tr bgcolor='$color{'color20'}'>"; 
    }

    print <<END
<td align='center'>$temp[1]</td>
<td align='center'>$temp[2]</td>
<td align='center'>
END
;
    # Prepare a global flag to make easy reading
    my $global = '';
    my $disabledTogle = '';
    my $disabledEditRemove = '';
    if ( ExistNewOptionDefinition ($temp[1] . ' ' . $temp[2]) ) {
	$global = $Lang::tr{'dhcp advopt definition'};
	$disabledTogle = "disabled='disabled'";
	# Search if it is a used NewOptionDefinition to also disable edit & delete
	$disabledEditRemove = "disabled='disabled'" if (IsUsedNewOptionDefinition ($temp[1], $temp[2]));
    } else {
	$global = $Lang::tr{'dhcp advopt scope global'};
    }
    
    
    # Print each checked interface
    for (my $key=0; $key<@ITFs; $key++) {
	my $itf = $temp[3+$key];
	if ($itf ne 'off') {	# Only if an interface name is read
	    print "$itf";
	    $global='';		# fall to local scope !
	}
    }
    print <<END
$global</td>
<td align='center'>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='ACTION' value='$Lang::tr{'toggle enable disable'}1' />
<input $disabledTogle type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif' alt='$gdesc' title='$gdesc' />
<input type='hidden' name='KEY1' value='$key' />
</form>
</td>

<td align='center'>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='ACTION' value='$Lang::tr{'edit'}1' />
<input $disabledEditRemove type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' />
<input type='hidden' name='KEY1' value='$key' />
</form>
</td>

<td align='center'>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='ACTION' value='$Lang::tr{'remove'}1' />
<input $disabledEditRemove type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' alt='$Lang::tr{'remove'}' title='$Lang::tr{'remove'}' />
<input type='hidden' name='KEY1' value='$key' />
</form>
</td>
</tr>
END
;
    $key++;
}

print "</table>";

# If there are dhcp options, print Key to action icons
if ($key) {
print <<END
<table>
<tr>
	<td class='boldbase'>&nbsp;<b>$Lang::tr{'legend'}:&nbsp;</b></td>
	<td><img src='/images/on.gif' alt='$Lang::tr{'click to disable'}' /></td>
	<td class='base'>$Lang::tr{'click to disable'}</td>
	<td>&nbsp;&nbsp;</td>
	<td><img src='/images/off.gif' alt='$Lang::tr{'click to enable'}' /></td>
	<td class='base'>$Lang::tr{'click to enable'}</td>
	<td>&nbsp;&nbsp;</td>
	<td><img src='/images/edit.gif' alt='$Lang::tr{'edit'}' /></td>
	<td class='base'>$Lang::tr{'edit'}</td>
	<td>&nbsp;&nbsp;</td>
	<td><img src='/images/delete.gif' alt='$Lang::tr{'remove'}' /></td>
	<td class='base'>$Lang::tr{'remove'}</td>
</tr>
</table>
END
;
}
&Header::closebox();

&Header::openbox('100%', 'left', $Lang::tr{'current fixed leases'});
# Fixed leases screens
$checked{'FIX_ENABLED'}{'on'} = ($dhcpsettings{'FIX_ENABLED'} ne 'on') ? '' : "checked='checked'";

$buttontext = $Lang::tr{'add'};
print "<form method='post' action='$ENV{'SCRIPT_NAME'}'><table width='100%'>";

if ($dhcpsettings{'KEY2'} ne '') {
    $buttontext = $Lang::tr{'update'};
    print "<tr><td class='boldbase' colspan='3'><b>$Lang::tr{'edit an existing lease'}</b></td></tr>";
} else {
    print "<tr><td class='boldbase' colspan='3'><b>$Lang::tr{'add new lease'}</b></td></tr>"
}
print <<END
<tr>
    <td class='base'>$Lang::tr{'mac address'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td><input type='text' name='FIX_MAC' value='$dhcpsettings{'FIX_MAC'}' size='18' /></td>
    <td class='base'>$Lang::tr{'ip address'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td><input type='text' name='FIX_ADDR' value='$dhcpsettings{'FIX_ADDR'}' size='18' /></td>
    <td class='base'>$Lang::tr{'remark'}:</td>
    <td><input type='text' name='FIX_REMARK' value='$dhcpsettings{'FIX_REMARK'}' size='18' /></td>
</tr><tr>
    <td class='base'>$Lang::tr{'enabled'}</td><td><input type='checkbox' name='FIX_ENABLED' $checked{'FIX_ENABLED'}{'on'} /></td>
</tr><tr>
    <td colspan = '3'><b>$Lang::tr{'dhcp bootp pxe data'}</b></td>
</tr><tr>
    <td class='base'>next-server:</td>
    <td><input type='text' name='FIX_NEXTADDR' value='$dhcpsettings{'FIX_NEXTADDR'}' size='18' /></td>
    <td class='base'>filename:</td>
    <td><input type='text' name='FIX_FILENAME' value='$dhcpsettings{'FIX_FILENAME'}' size='18' /></td>
    <td class='base'>root path:</td>
    <td><input type='text' name='FIX_ROOTPATH' value='$dhcpsettings{'FIX_ROOTPATH'}' size='18' /></td>
</tr>
</table>
<hr />
<table width='100%'>
<tr>
    <td class='base' width='50%'><img src='/blob.gif' align='top' alt='*' />&nbsp;$Lang::tr{'required field'}</td>
    <td width='50%' align='right'>
	<input type='hidden' name='ACTION' value='$Lang::tr{'add'}2' />
	<input type='submit' name='SUBMIT' value='$buttontext' />
	<input type='hidden' name='KEY2' value='$dhcpsettings{'KEY2'}' /></td>
</tr>
</table>
</form>
END
;
#Edited line number (KEY2) passed until cleared by 'save' or 'remove' or 'new sort order'

# Search for static leases
my $search_query = $dhcpsettings{'q'};

if (scalar @current2 >= 10) {
	print <<END;
		<form method="POST" action="#search">
			<a name="search"></a>
			<table width='100%'>
				<tr>
					<td>
						<input type="text" name="q" value="$search_query">
						<input type="submit" value="$Lang::tr{'search'}">
					</td>
				</tr>
			</table>
		</form>
END
}

print <<END
<table width='100%' class='tbl'>
<tr>
    <th width='20%' align='center'><a href='$ENV{'SCRIPT_NAME'}?FETHER'><b>$Lang::tr{'mac address'}</b></a></th>
    <th width='20%' align='center'><a href='$ENV{'SCRIPT_NAME'}?FIPADDR'><b>$Lang::tr{'ip address'}</b></a></th>
    <th width='15%' align='center'><b>$Lang::tr{'remark'}</b></th>
    <th width='15%' class='boldbase' align='center'><b>next-server</b></th>
    <th width='15%' class='boldbase' align='center'><b>filename</b></th>
    <th width='15%' class='boldbase' align='center'><b>root path</b></th>
    <th colspan='3' class='boldbase' align='center'><b>$Lang::tr{'action'}</b></th>
</tr>
END
;
my $ipdup = 0;
my %ipinuse = ();
my %macdupl = (); # Duplicate MACs have to be on different subnets
my %ipoutside = ();

# mark duplicate ip or duplicate MAC
foreach my $line (@current2) {
    my @temp = split(/\,/,$line);
    $macdupl{$temp[0]} += 1;
    if ($macdupl{$temp[0]} > 1) { 
	$ipdup = 1; 	# Flag up duplicates for use later
    }
    $ipinuse{$temp[1]} += 1;
    if ($ipinuse{$temp[1]} > 1) { 
	$ipdup = 1; 	# Flag up duplicates for use later
    }
    # Mark IP addresses outwith known subnets
    $ipoutside{$temp[1]} = 1;
    foreach my $itf (@ITFs) {
        if ( &General::IpInSubnet($temp[1],
                $netsettings{"${itf}_NETADDRESS"}, 
                $netsettings{"${itf}_NETMASK"})) {
            $ipoutside{$temp[1]} = 0;
        }
    }
}

$key = 0;
my $col="";
foreach my $line (@current2) {
    my $gif = '';
    my $gdesc = '';
    chomp($line);   # remove newline
    my @temp = split(/\,/,$line);

    if ($temp[2] eq "on") {
	$gif = 'on.gif';
	$gdesc = $Lang::tr{'click to disable'};
    } else {
	$gif = 'off.gif';
	$gdesc = $Lang::tr{'click to enable'}; 
    }

    # Skip all entries that do not match the search query
    if ($search_query ne "") {
	if (!grep(/$search_query/, @temp)) {
		$key++;
		next;
	}
    }

    if ($dhcpsettings{'KEY2'} eq $key) {
	print "<tr>";
	$col="bgcolor='${Header::colouryellow}'";
    } elsif ($key % 2) {
	print "<tr>";
	$col="bgcolor='$color{'color20'}'";
    } else {
	print "<tr>";
	$col="bgcolor='$color{'color22'}'";
    }
    my $TAG0 = '';
    my $TAG1 = '';
    my $TAG2 = '';
    my $TAG3 = '';
    my $TAG4 = '';
    if ($ipinuse{$temp[1]} > 1) { 
	$TAG0 = '<b>';
	$TAG1 = '</b>';
    }
    if ($macdupl{$temp[0]} > 1) { 
	$TAG2 = '<b>';
	$TAG3 = '</b>';
    }
    if ($ipoutside{$temp[1]} > 0) { 
	$TAG4 = "bgcolor='orange'" if ($dhcpsettings{'KEY2'} ne $key);
    }

    print <<END
<td align='center' $col>$TAG2$temp[0]$TAG3</td>
<td align='center' $col $TAG4>$TAG0$temp[1]$TAG1</td>
<td align='center' $col>$temp[6]&nbsp;</td>
<td align='center' $col>$temp[3]&nbsp;</td>
<td align='center' $col>$temp[4]&nbsp;</td>
<td align='center' $col>$temp[5]&nbsp;</td>

<td align='center' $col>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='ACTION' value='$Lang::tr{'toggle enable disable'}2' />
<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif' alt='$gdesc' title='$gdesc' />
<input type='hidden' name='KEY2' value='$key' />
</form>
</td>

<td align='center' $col>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='ACTION' value='$Lang::tr{'edit'}2' />
<input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' />
<input type='hidden' name='KEY2' value='$key' />
</form>
</td>

<td align='center' $col>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='ACTION' value='$Lang::tr{'remove'}2' />
<input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' alt='$Lang::tr{'remove'}' title='$Lang::tr{'remove'}' />
<input type='hidden' name='KEY2' value='$key' />
</form>
</td>
</tr>
END
;
    $key++;
}
print "</table>";

# If the fixed lease file contains entries, print Key to action icons
if ($key) {
my $dup = $ipdup ? "<td class='base'>$Lang::tr{'duplicate ip bold'}</td>" :'';
print <<END
<table>
<tr>
	<td class='boldbase'>&nbsp;<b>$Lang::tr{'legend'}:&nbsp;</b></td>
	<td><img src='/images/on.gif' alt='$Lang::tr{'click to disable'}' /></td>
	<td class='base'>$Lang::tr{'click to disable'}</td>
	<td>&nbsp;&nbsp;</td>
	<td><img src='/images/off.gif' alt='$Lang::tr{'click to enable'}' /></td>
	<td class='base'>$Lang::tr{'click to enable'}</td>
	<td>&nbsp;&nbsp;</td>
	<td><img src='/images/edit.gif' alt='$Lang::tr{'edit'}' /></td>
	<td class='base'>$Lang::tr{'edit'}</td>
	<td>&nbsp;&nbsp;</td>
	<td><img src='/images/delete.gif' alt='$Lang::tr{'remove'}' /></td>
	<td class='base'>$Lang::tr{'remove'}</td>
</tr>
<tr>
	<td>&nbsp;</td>
	<td bgcolor='orange'>&nbsp;</td>
	<td class='base'>$Lang::tr{'ip address outside subnets'}</td>
	<td>&nbsp;</td>
	<td>&nbsp;</td>
	$dup
</tr>
</table>
END
;
}

&Header::closebox();

foreach my $itf (@ITFs) {
    if ($dhcpsettings{"ENABLE_${itf}"} eq 'on') {
	# display leases with a list of actions to do with the global select checkbox.
	&Header::PrintActualLeases("+");	# "+" => create fixed leases from nodeaddress
	last; 			#Print one time only for all interfaces
    };
}

&Header::closebigbox();
&Header::closepage();

## Ouf it's the end !

sub sortcurrent1  # by now, do not sort, just write
{
    open(FILE, ">$filename1") or die 'Unable to open dhcp advanced options file.';
    print FILE @current1;
    close(FILE);
}


# Sort the "current2" array according to choices
sub sortcurrent2
{
    our %entries = ();

    sub fixedleasesort {
	my $qs='';
	if (rindex ($dhcpsettings{'SORT_FLEASELIST'},'Rev') != -1) {
	    $qs=substr ($dhcpsettings{'SORT_FLEASELIST'},0,length($dhcpsettings{'SORT_FLEASELIST'})-3);
	    if ($qs eq 'FIPADDR') {
		my @a = split(/\./,$entries{$a}->{$qs});
		my @b = split(/\./,$entries{$b}->{$qs});
		($b[0]<=>$a[0]) ||
		($b[1]<=>$a[1]) ||
		($b[2]<=>$a[2]) ||
		($b[3]<=>$a[3]);
	    } else {
		$entries{$b}->{$qs} cmp $entries{$a}->{$qs};
	    }
	} else { #not reverse
	    $qs=$dhcpsettings{'SORT_FLEASELIST'};
	    if ($qs eq 'FIPADDR') {
		my @a = split(/\./,$entries{$a}->{$qs});
		my @b = split(/\./,$entries{$b}->{$qs});
		($a[0]<=>$b[0]) ||
		($a[1]<=>$b[1]) ||
		($a[2]<=>$b[2]) ||
		($a[3]<=>$b[3]);
	    } else {
		$entries{$a}->{$qs} cmp $entries{$b}->{$qs};
	    }
	}
    }

    #Use an associative array (%entries)
    foreach my $line (@current2) {
	chomp( $line); #remove newline because can be on field 5 or 6 (addition of REMARK)
	my @temp = split (',',$line);
	my @record = ('FETHER',$temp[0],'FIPADDR',$temp[1],'DATA',join(',',@temp[2..6]));
	my $record = {};                        # create a reference to empty hash
	%{$record} = @record;                	# populate that hash with @record
	# use combination of ether & IP as key to allow duplicates in either but not both
	$entries{$record->{FETHER} . $record->{FIPADDR}} = $record; # add this to a hash of hashes
    }
    
    open(FILE, ">$filename2") or die 'Unable to open fixed lease file.';
    foreach my $entry ( sort fixedleasesort keys %entries) {
	print FILE "$entries{$entry}->{FETHER},$entries{$entry}->{FIPADDR},$entries{$entry}->{DATA}\n";
    }
    close(FILE);

    # Reload sorted  @current2
    open (FILE, "$filename2");
    @current2 = <FILE>;
    close (FILE);
    undef (%entries);  #This array is reused latter. Clear it.
}
						    
# Build the configuration file mixing  settings, fixed leases and advanced options
sub buildconf {
    open(FILE, ">/${General::swroot}/dhcp/dhcpd.conf") or die "Unable to write dhcpd.conf file";
    flock(FILE, 2);

    # Global settings
    print FILE "deny bootp;	#default\n";
    print FILE "authoritative;\n";

    # DNS Update settings
    if ($dhcpsettings{'DNS_UPDATE_ENABLED'} eq 'on') {
        print FILE "ddns-updates           on;\n";
        print FILE "ddns-update-style      interim;\n";
        print FILE "ddns-ttl               60; # 1 min\n";
        print FILE "ignore                 client-updates;\n";
        print FILE "update-static-leases   on;\n";
    } else {
        print FILE "ddns-update-style none;\n";
    }
    
    # Write first new option definition
    foreach my $line (@current1) {
	chomp($line);   # remove newline
	my @temp = split(/\t/,$line);
        if (ExistNewOptionDefinition ($temp[1] . ' ' . $temp[2])) {
		print FILE "option $temp[1] $temp[2];\n";
	}
    }
    # Write other global options
    foreach my $line (@current1) {
	chomp($line);   # remove newline
	my @temp = split(/\t/,$line);
	
	if ($temp[0] eq 'on' && !ExistNewOptionDefinition ($temp[1] . ' ' . $temp[2])){ # active & !definition
	    my $global=1;
	    for (my $key=0; $key<@ITFs; $key++) {
		my $itf = $temp[3+$key];
		if ($itf ne 'off') # Only if an interface name is read
		{
		    $global=0;
		}
	    }
	    if ($global) {
		print FILE "option $temp[1] $temp[2];\n";
	    }
	}# on    
    }# foreach line
    print FILE "\n";

    #Subnet range definition
    foreach my $itf (@ITFs) {
	my $lc_itf=lc($itf);
	if ($dhcpsettings{"ENABLE_${itf}"} eq 'on' ){
	    print FILE "subnet " . $netsettings{"${itf}_NETADDRESS"} . " netmask ". $netsettings{"${itf}_NETMASK"} . " #$itf\n";
	    print FILE "{\n";
	    print FILE "\trange " . $dhcpsettings{"START_ADDR_${itf}"} . ' ' . $dhcpsettings{"END_ADDR_${itf}"}.";\n" if ($dhcpsettings{"START_ADDR_${itf}"});
	    print FILE "\toption subnet-mask "   . $netsettings{"${itf}_NETMASK"} . ";\n";
	    print FILE "\toption domain-name \"" . $dhcpsettings{"DOMAIN_NAME_${itf}"} . "\";\n";
	    print FILE "\toption routers " . $netsettings{"${itf}_ADDRESS"} . ";\n";
	    print FILE "\toption domain-name-servers " . $dhcpsettings{"DNS1_${itf}"}  if ($dhcpsettings{"DNS1_${itf}"});
	    print FILE ", " . $dhcpsettings{"DNS2_${itf}"}                             if ($dhcpsettings{"DNS2_${itf}"});
	    print FILE ";\n"                                                           if ($dhcpsettings{"DNS1_${itf}"});
	    print FILE "\toption ntp-servers " . $dhcpsettings{"NTP1_${itf}"}          if ($dhcpsettings{"NTP1_${itf}"});
	    print FILE ", " . $dhcpsettings{"NTP2_${itf}"}                             if ($dhcpsettings{"NTP2_${itf}"});
	    print FILE ";\n"                                                           if ($dhcpsettings{"NTP1_${itf}"});
	    print FILE "\toption netbios-name-servers " . $dhcpsettings{"WINS1_${itf}"}     if ($dhcpsettings{"WINS1_${itf}"});
	    print FILE ", " . $dhcpsettings{"WINS2_${itf}"}                            if ($dhcpsettings{"WINS2_${itf}"});
	    print FILE ";\n"                                                           if ($dhcpsettings{"WINS1_${itf}"});
	    print FILE "\tnext-server " . $dhcpsettings{"NEXT_${itf}"} . ";\n" if ($dhcpsettings{"NEXT_${itf}"});
	    print FILE "\tfilename \"" . $dhcpsettings{"FILE_${itf}"} . "\";\n" if ($dhcpsettings{"FILE_${itf}"});
	    print FILE "\tdefault-lease-time " . ($dhcpsettings{"DEFAULT_LEASE_TIME_${itf}"} * 60). ";\n";
	    print FILE "\tmax-lease-time "     . ($dhcpsettings{"MAX_LEASE_TIME_${itf}"} * 60)    . ";\n";
	    print FILE "\tallow bootp;\n" if ($dhcpsettings{"ENABLEBOOTP_${itf}"} eq 'on');



	    # Write scoped options
	    foreach my $line (@current1) {
		chomp($line);   # remove newline
		my @temp = split(/\t/,$line);		# Use TAB separator !
	
		if ($temp[0] eq 'on'){
		    for (my $key=0; $key<@ITFs; $key++) {
			if ($itf eq $temp[3+$key]) # Only is an interface name is read
			{
			    print FILE "\toption $temp[1] $temp[2];\n";
			}
		    }
		}# on    
	    }# foreach line
	    print FILE "} #$itf\n\n";

	    if (($dhcpsettings{"DNS_UPDATE_ENABLED"} eq "on") && ($dhcpsettings{"DNS_UPDATE_KEY_NAME_${itf}"} ne "")) {
	        print FILE "key " . $dhcpsettings{"DNS_UPDATE_KEY_NAME_${itf}"} . " {\n";
	        print FILE "\talgorithm " . $dhcpsettings{"DNS_UPDATE_KEY_ALGO_${itf}"} . ";\n";
	        print FILE "\tsecret \"" . $dhcpsettings{"DNS_UPDATE_KEY_SECRET_${itf}"} . "\";\n";
	        print FILE "};\n\n";

	        print FILE "zone " . $dhcpsettings{"DOMAIN_NAME_${itf}"} . ". {\n";
	        print FILE "\tkey " . $dhcpsettings{"DNS_UPDATE_KEY_NAME_${itf}"} . ";\n";
		print FILE "}\n\n";
	    }

	    system ('/usr/bin/touch', "${General::swroot}/dhcp/enable_${lc_itf}");
	    &General::log("DHCP on ${itf}: " . $Lang::tr{'dhcp server enabled'})
	} else {
	    unlink "${General::swroot}/dhcp/enable_${lc_itf}";
	    &General::log("DHCP on ${itf}: " . $Lang::tr{'dhcp server disabled'})
	}
    }

    #write fixed leases if any. Does not handle duplicates to write them elsewhere than the global scope.
    my $key = 0;
    foreach my $line (@current2) {
	chomp($line);
	my @temp = split(/\,/,$line);
	if ($temp[2] eq "on") {
	    print FILE "\nhost fix$key # $temp[6]\n";
	    print FILE "{\n";
	    print FILE "\thardware ethernet $temp[0];\n";
	    print FILE "\tfixed-address $temp[1];\n";
	    print FILE "\tnext-server $temp[3];\n"          if ($temp[3]);
	    print FILE "\tfilename \"$temp[4]\";\n"         if ($temp[4]);
	    print FILE "\toption root-path \"$temp[5]\";\n" if ($temp[5]);
	    print FILE "}\n";
	    $key++;
	}
    }
    print FILE "include \"${General::swroot}/dhcp/dhcpd.conf.local\";\n";
    close FILE;
    if ( $dhcpsettings{"ENABLE_GREEN"} eq 'on' || $dhcpsettings{"ENABLE_BLUE"} eq 'on' ) {system '/usr/local/bin/dhcpctrl enable >/dev/null 2>&1';}
    else {system '/usr/local/bin/dhcpctrl disable >/dev/null 2>&1';}
    system '/usr/local/bin/dhcpctrl restart >/dev/null 2>&1';
}

#
# Receive a string and if it match model for a new option,
# add it to the list %newOptions
#
my %NewOptions = ();

sub AddNewOptionDefinition {
    my ($line) = @_;
    if ( $line =~ /^([-\w]+)( code \d+=($OptionTypes))/ ) {
	$NewOptions{$1} = $2;
	#&General::log ("new:<$1><$2>");
	return 1;
    }
    return 0;
}

#
# Check existence of definition for a new option
#
sub ExistNewOptionDefinition {
    my ($line) = @_;

    if ( $line =~ /^([-\w]+)( code \d+=($OptionTypes))/ ) {
	return defined $NewOptions{$1};
    }
    return 0;
}

#
# Check if it is a new option (definition must exist)
# "code=" test eliminate a false response when definition exists
# but this string is a definition with bad $OptionTypes.
sub ValidNewOption {
    my ($line) = @_;
    if ($line =~ /^([-\w]+) (.*)/ ) {
	return defined ( $NewOptions{$1} ) && $2 !~ /code=/;
    }
    return 0;
}

#
# Check if the new option $opt is used, except the definition of itself!
#
sub IsUsedNewOptionDefinition {
    my ($opt,$val) = @_;

    foreach my $line (@current1) {
	#chomp($line);   # remove newline        #don't know why, but this remove newline in @current1 .... !
	my @temp = split(/\t/,$line);
	# if we find something "opt value" & value != "code nnn=" it's ok.
	return 1 if ( ($opt eq $temp[1]) && ($temp[2] !~ /code \d+=/) );
    }
    return 0;
}
