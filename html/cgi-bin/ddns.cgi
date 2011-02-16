#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2011  IPFire Team  <info@ipfire.org>                     #
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
my @dummy = ( ${Header::table2colour}, ${Header::colouryellow} );
undef (@dummy);

my $ddnsprefix = $Lang::tr{'ddns noip prefix'};
$ddnsprefix =~ s/%/$General::noipprefix/;

my %color = ();
my %mainsettings = ();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

# Files used
my $setting = "${General::swroot}/ddns/settings";
our $datafile = "${General::swroot}/ddns/config";

my %settings=();
#Settings1
$settings{'BEHINDROUTER'} = 'RED_IP';
$settings{'MINIMIZEUPDATES'} = '';

#Settings2 for editing the multi-line list
#Must not be saved !
$settings{'HOSTNAME'} = '';
$settings{'DOMAIN'} = '';
$settings{'LOGIN'} = '';
$settings{'PASSWORD'} = '';
$settings{'PASSWORD2'} = '';
$settings{'ENABLED'} = '';
$settings{'PROXY'} = '';
$settings{'WILDCARDS'} = '';
$settings{'SERVICE'} = '';

my @nosaved=('HOSTNAME','DOMAIN','LOGIN','PASSWORD','PASSWORD2',
	     'ENABLED','PROXY','WILDCARDS','SERVICE');	# List here ALL setting2 fields. Mandatory
    
$settings{'ACTION'} = '';		# add/edit/remove
$settings{'KEY1'} = '';			# point record for ACTION
$settings{'KEY2'} = '';			# point record for ACTION

my $errormessage = '';
my $warnmessage = '';

&Header::showhttpheaders();

#Get GUI values
&Header::getcgihash(\%settings);

# Load multiline data
our @current = ();
if (open(FILE, "$datafile")) {
    @current = <FILE>;
    close (FILE);
}

#
# Check Settings1 first because they are needed before working on @current
#
if ($settings{'ACTION'} eq $Lang::tr{'save'}) {
    # No user input to check.  !
    #unless ($errormessage) {					# Everything is ok, save settings
	$settings{'BEHINDROUTERWAITLOOP'} = '-1';		# init  & will update on next setddns.pl call
	map (delete ($settings{$_}) ,(@nosaved,'ACTION','KEY1','KEY2'));# Must never be saved 
	&General::writehash($setting, \%settings);		# Save good settings
	$settings{'ACTION'} = $Lang::tr{'save'};		# Recreate  'ACTION'
	map ($settings{$_}= '',(@nosaved,'KEY1','KEY2'));	# and reinit var to empty
    #}
} else {
    &General::readhash($setting, \%settings);			# Get saved settings and reset to good if needed
}

#
# Now manipulate the multi-line list with Settings2
#
# Toggle enable/disable field.  Field is in second position
if ($settings{'ACTION'} eq $Lang::tr{'toggle enable disable'}) {
    #move out new line
    chomp(@current[$settings{'KEY1'}]);
    my @temp = split(/\,/,@current[$settings{'KEY1'}]);
    my $K2=$settings{'KEY2'};
    $temp[ $K2 ] = ( $temp[ $K2 ] eq 'on') ? '' : 'on';		# Toggle the field
    @current[$settings{'KEY1'}] = join (',',@temp)."\n";
    $settings{'KEY1'} = ''; 					# End edit mode
    &General::log($Lang::tr{'ddns hostname modified'});

    # Write changes to config file.
    &WriteDataFile;						# sort newly added/modified entry
}

if ($settings{'ACTION'} eq $Lang::tr{'add'}) {
    # Validate inputs

    unless ($settings{'LOGIN'} ne '') {
	$errormessage = $Lang::tr{'username not set'};
    }

    # list box returns 'service optional synonyms'
    # keep only first name
    $settings{'SERVICE'} =~ s/ .*$//;
    
    # for freedns.afraid.org, only 'connect string' is mandatory
    if ($settings{'SERVICE'} ne 'freedns.afraid.org') {
	unless ($settings{'SERVICE'} eq 'regfish.com' || $settings{'PASSWORD'} ne '') {
	    $errormessage = $Lang::tr{'password not set'};
	}
	unless ($settings{'PASSWORD'} eq $settings{'PASSWORD2'}) {
	    $errormessage = $Lang::tr{'passwords do not match'};
	}
	
	# Permit an empty HOSTNAME for the nsupdate, regfish, dyndns, enom, ovh, zoneedit, no-ip, easydns
        unless ($settings{'SERVICE'} eq 'zoneedit.com' || $settings{'SERVICE'} eq 'nsupdate' || 
		$settings{'SERVICE'} eq 'dyndns-custom'|| $settings{'SERVICE'} eq 'regfish.com' || 
		$settings{'SERVICE'} eq 'enom.com' || $settings{'SERVICE'} eq 'dnspark.com' ||
		$settings{'SERVICE'} eq 'ovh.com' || $settings{'HOSTNAME'} ne '' ||
		$settings{'SERVICE'} eq 'no-ip.com' || $settings{'SERVICE'} eq 'easydns.com' ) {
	    $errormessage = $Lang::tr{'hostname not set'};
	}
	unless ($settings{'HOSTNAME'} eq '' || $settings{'HOSTNAME'} =~ /^[a-zA-Z_0-9-]+$/) {
	    $errormessage = $Lang::tr{'invalid hostname'};
	}
	unless ($settings{'DOMAIN'} ne '') {
	    $errormessage = $Lang::tr{'domain not set'};
	}
	unless ($settings{'DOMAIN'} =~ /^[a-zA-Z_0-9.-]+$/) { 
	    $errormessage = $Lang::tr{'invalid domain name'};
	}
	unless ($settings{'DOMAIN'} =~ /[.]/) {
	    $errormessage = $Lang::tr{'invalid domain name'};
	}
    }

    # recheck service wich don't need too much fields
    if ($settings{'SERVICE'} eq 'cjb.net') {
	$errormessage = ''; # clear previous error
	unless ($settings{'LOGIN'} ne '') {
	    $errormessage = $Lang::tr{'username not set'};
	}
	unless ($settings{'PASSWORD'} ne '') {
	    $errormessage = $Lang::tr{'password not set'};
	}
	unless ($settings{'PASSWORD'} eq $settings{'PASSWORD2'}) {
	    $errormessage = $Lang::tr{'passwords do not match'};
	}
    }

    unless ($errormessage) {
	if ($settings{'KEY1'} eq '') { #add or edit ?
	    unshift (@current, "$settings{'SERVICE'},$settings{'HOSTNAME'},$settings{'DOMAIN'},$settings{'PROXY'},$settings{'WILDCARDS'},$settings{'LOGIN'},$settings{'PASSWORD'},$settings{'ENABLED'}\n");
	    &General::log($Lang::tr{'ddns hostname added'});
	} else {
	    @current[$settings{'KEY1'}] = "$settings{'SERVICE'},$settings{'HOSTNAME'},$settings{'DOMAIN'},$settings{'PROXY'},$settings{'WILDCARDS'},$settings{'LOGIN'},$settings{'PASSWORD'},$settings{'ENABLED'}\n";
	    $settings{'KEY1'} = '';       # End edit mode
	    &General::log($Lang::tr{'ddns hostname modified'});
	}
	map ($settings{$_}='' ,@nosaved);	# Clear fields
        # Write changes to config file.
	&WriteDataFile;				# sort newly added/modified entry
    }
}

if ($settings{'ACTION'} eq $Lang::tr{'edit'}) {
    #move out new line
    my $line = @current[$settings{'KEY1'}];	# KEY1 is the index in current
    chomp($line);
    my @temp = split(/\,/, $line);
    $settings{'SERVICE'}	= $temp[0];
    $settings{'HOSTNAME'}	= $temp[1];
    $settings{'DOMAIN'}		= $temp[2];
    $settings{'PROXY'}		= $temp[3];
    $settings{'WILDCARDS'}	= $temp[4];
    $settings{'LOGIN'}		= $temp[5];
    $settings{'PASSWORD'} = $settings{'PASSWORD2'} = $temp[6];
    $settings{'ENABLED'}	= $temp[7];
}

if ($settings{'ACTION'} eq $Lang::tr{'remove'}) {
    splice (@current,$settings{'KEY1'},1);		# Delete line 
    open(FILE, ">$datafile") or die 'ddns datafile error';
    print FILE @current;
    close(FILE);
    $settings{'KEY1'} = '';				# End remove mode
    &General::log($Lang::tr{'ddns hostname removed'});
    # Write changes to config file.
    &WriteDataFile;
}

if ($settings{'ACTION'} eq $Lang::tr{'instant update'}) {
    system('/usr/local/bin/setddns.pl', '-f');
}


if ($settings{'ACTION'} eq '')
{
    $settings{'SERVICE'} = 'dyndns.org';
    $settings{'ENABLED'} = 'on';
}

&Header::openpage($Lang::tr{'dynamic dns'}, 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

my %checked =();     # Checkbox manipulations
$checked{'SERVICE'}{'cjb.net'} = '';
$checked{'SERVICE'}{'dhs.org'} = '';
$checked{'SERVICE'}{'dnspark.com'} = '';
$checked{'SERVICE'}{'dtdns.com'} = '';
$checked{'SERVICE'}{'dyndns.org'} = '';
$checked{'SERVICE'}{'dyndns-custom'} = '';
$checked{'SERVICE'}{'dyndns-static'} = '';
$checked{'SERVICE'}{'dyns.cx'} = '';
$checked{'SERVICE'}{'dynu.ca'} = '';
$checked{'SERVICE'}{'easydns.com'} = '';
$checked{'SERVICE'}{'enom.com'} = '';
$checked{'SERVICE'}{'freedns.afraid.org'} = '';
$checked{'SERVICE'}{'hn.org'} = '';
$checked{'SERVICE'}{'no-ip.com'} = '';
$checked{'SERVICE'}{'nsupdate'} = '';
$checked{'SERVICE'}{'ovh.com'} = '';
$checked{'SERVICE'}{'regfish.com'} = '';
$checked{'SERVICE'}{'selfhost.de'} = '';
$checked{'SERVICE'}{'strato.com'} = '';
$checked{'SERVICE'}{'tzo.com'} = '';
$checked{'SERVICE'}{'zoneedit.com'} = '';
$checked{'SERVICE'}{$settings{'SERVICE'}} = "selected='selected'";

$checked{'BEHINDROUTER'}{'RED_IP'} = '';
$checked{'BEHINDROUTER'}{'FETCH_IP'} = '';
$checked{'BEHINDROUTER'}{$settings{'BEHINDROUTER'}} = "checked='checked'";
$checked{'MINIMIZEUPDATES'} = ($settings{'MINIMIZEUPDATES'} eq '' ) ? '' : "checked='checked'";

$checked{'PROXY'}{'on'} = ($settings{'PROXY'} eq '') ? '' : "checked='checked'";
$checked{'WILDCARDS'}{'on'} = ($settings{'WILDCARDS'} eq '') ? '' : "checked='checked'";
$checked{'ENABLED'}{'on'} = ($settings{'ENABLED'} eq '' ) ? '' : "checked='checked'";

if ($errormessage) {
    &Header::openbox('100%', 'left', $Lang::tr{'error messages'});
    print "<font class='base'>$errormessage&nbsp;</font>";
    &Header::closebox();
}

if ($warnmessage) {
    $warnmessage = "<font color=${Header::colourred}><b>$Lang::tr{'capswarning'}</b></font>: $warnmessage";
}
&Header::openbox('100%', 'left', $Lang::tr{'settings'});
print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>";
print <<END
<table width='100%'>
<tr>
        <td class='base'>$Lang::tr{'dyn dns source choice'}</td>
</tr><tr>
    <td class='base'><input type='radio' name='BEHINDROUTER' value='RED_IP' $checked{'BEHINDROUTER'}{'RED_IP'} />
    $Lang::tr{'use ipfire red ip'}</td>
</tr><tr>
    <td class='base'><input type='radio' name='BEHINDROUTER' value='FETCH_IP' $checked{'BEHINDROUTER'}{'FETCH_IP'} />
    $Lang::tr{'fetch ip from'} <img src='/blob.gif' alt='*' /></td>
</tr>
<tr>
    <td class='base'><input type='checkbox' name='MINIMIZEUPDATES' $checked{'MINIMIZEUPDATES'} />
    $Lang::tr{'ddns minimize updates'}</td>
</tr>
</table>
<br /><hr />
END
;

print <<END
<table width='100%'>
<tr>
    <td class='base' valign='top'><img src='/blob.gif' alt='*' /></td>
    <td width='70%' class='base'>$Lang::tr{'avoid dod'}</td>
    <td width='30%' align='center' class='base'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
</tr>
</table>
</form>
END
;
&Header::closebox();   # end of Settings1


my $buttontext = $Lang::tr{'add'};
if ($settings{'KEY1'} ne '') {
    $buttontext = $Lang::tr{'update'};
    &Header::openbox('100%', 'left', $Lang::tr{'edit an existing host'});
} else {
    &Header::openbox('100%', 'left', $Lang::tr{'add a host'});
}

#Edited line number (KEY1) passed until cleared by 'save' or 'remove'
print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='KEY1' value='$settings{'KEY1'}' />
<table width='100%'>
<tr>
    <td width='25%' class='base'>$Lang::tr{'service'}:</td>
    <td width='25%'><select size='1' name='SERVICE'>
    <option $checked{'SERVICE'}{'cjb.net'}>cjb.net</option>
    <option $checked{'SERVICE'}{'dhs.org'}>dhs.org</option>
    <option $checked{'SERVICE'}{'dnspark.com'}>dnspark.com</option>
    <option $checked{'SERVICE'}{'dtdns.com'}>dtdns.com</option>
    <option $checked{'SERVICE'}{'dyndns.org'}>dyndns.org</option>
    <option $checked{'SERVICE'}{'dyndns-custom'}>dyndns-custom</option>
    <option $checked{'SERVICE'}{'dyndns-static'}>dyndns-static</option>
    <option $checked{'SERVICE'}{'dyns.cx'}>dyns.cx</option>
    <option $checked{'SERVICE'}{'dynu.ca'}>dynu.ca dyn.ee dynserv.(ca|org|net|com)</option>
    <option $checked{'SERVICE'}{'easydns.com'}>easydns.com</option>
    <option $checked{'SERVICE'}{'enom.com'}>enom.com</option>
    <option $checked{'SERVICE'}{'freedns.afraid.org'}>freedns.afraid.org</option>
    <option $checked{'SERVICE'}{'hn.org'}>hn.org</option>
    <option $checked{'SERVICE'}{'no-ip.com'}>no-ip.com</option>
    <option $checked{'SERVICE'}{'nsupdate'}>nsupdate</option>
    <option $checked{'SERVICE'}{'ovh.com'}>ovh.com</option>
    <option $checked{'SERVICE'}{'regfish.com'}>regfish.com</option>
    <option $checked{'SERVICE'}{'selfhost.de'}>selfhost.de</option>
    <option $checked{'SERVICE'}{'strato.com'}>strato.com</option>
<!--    <option $checked{'SERVICE'}{'tzo.com'}>tzo.com</option>        comment this service out until a working fix is developed -->
    <option $checked{'SERVICE'}{'zoneedit.com'}>zoneedit.com</option>
    </select></td>
    <td width='20%' class='base'>$Lang::tr{'hostname'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td width='30%'><input type='text' name='HOSTNAME' value='$settings{'HOSTNAME'}' /></td>
</tr><tr>
    <td class='base'>$Lang::tr{'behind a proxy'}</td>
    <td><input type='checkbox' name='PROXY' value='on' $checked{'PROXY'}{'on'} /></td>
    <td class='base'>$Lang::tr{'domain'}:</td>
    <td><input type='text' name='DOMAIN' value='$settings{'DOMAIN'}' /></td>
</tr><tr>
    <td class='base'>$Lang::tr{'enable wildcards'}</td>
    <td><input type='checkbox' name='WILDCARDS' value='on' $checked{'WILDCARDS'}{'on'} /></td>
    <td class='base'>$Lang::tr{'username'}</td>
    <td><input type='text' name='LOGIN' value='$settings{'LOGIN'}' /></td>
</tr><tr>
    <td></td>
    <td></td>
    <td class='base'>$Lang::tr{'password'}</td>
    <td><input type='password' name='PASSWORD' value='$settings{'PASSWORD'}' /></td>
</tr><tr>
    <td class='base'>$Lang::tr{'enabled'}</td>
    <td><input type='checkbox' name='ENABLED' value='on' $checked{'ENABLED'}{'on'} /></td>
    <td class='base'>$Lang::tr{'again'}</td>
    <td><input type='password' name='PASSWORD2' value='$settings{'PASSWORD2'}' /></td>
</tr>
</table>
<hr />
<table width='100%'>
<tr>
    <td class='base' valign='top'><img src='/blob.gif' alt='*' /></td>
    <td width='70%' class='base'>$ddnsprefix</td>
    
    <td width='30%' align='center' class='base'>
	<input type='hidden' name='ACTION' value='$Lang::tr{'add'}' />
	<input type='submit' name='SUBMIT' value='$buttontext' />    </td>
</tr>
</table>
</form>
END
;
&Header::closebox();

#
# Third box shows the list, in columns
#
&Header::openbox('100%', 'left', $Lang::tr{'current hosts'});
print <<END
<table width='100%'>
<tr>
    <td width='15%' align='center' class='boldbase'><b>$Lang::tr{'service'}</b></td>
    <td width='25%' align='center' class='boldbase'><b>$Lang::tr{'hostname'}</b></td>
    <td width='30%' align='center' class='boldbase'><b>$Lang::tr{'domain'}</b></td>
    <td width='10%' align='center' class='boldbase'><b>$Lang::tr{'proxy'}</b></td>
    <td width='10%' align='center' class='boldbase'><b>$Lang::tr{'wildcards'}</b></td>
    <td width='10%' colspan='3' class='boldbase' align='center'><b>$Lang::tr{'action'}</b></td>
</tr>
END
;
my $ip = &General::GetDyndnsRedIP;
my $key = 0;
foreach my $line (@current) {
    chomp($line);   				# remove newline
    my @temp = split(/\,/,$line);

    if ($temp[0] eq 'no-ip.com') {
    	$temp[1] =~ s!$General::noipprefix(.*)!<b>group:</b>$1 !;
    } 

    #Choose icon for checkbox

    my $gifproxy='';
    my $descproxy='';
    if ($temp[3] eq "on") {
	$gifproxy = 'on.gif';
	$descproxy = $Lang::tr{'click to disable'};
    } else {
	$gifproxy = 'off.gif';
	$descproxy = $Lang::tr{'click to enable'}; 
    }

    my $gifwildcard='';
    my $descwildcard='';
    if ($temp[4] eq "on") {
	$gifwildcard = 'on.gif';
	$descwildcard = $Lang::tr{'click to disable'};
    } else {
	$gifwildcard = 'off.gif';
	$descwildcard = $Lang::tr{'click to enable'}; 
    }

    my $sync = "<font color='blue'>";
    my $gif = '';
    my $gdesc = '';
    if ($temp[7] eq "on") {
	$gif = 'on.gif';
	$gdesc = $Lang::tr{'click to disable'};
        $sync = (&General::DyndnsServiceSync ($ip,$temp[1], $temp[2]) ? "<font color='green'>": "<font color='red'>") ;
    } else {
	$gif = 'off.gif';
	$gdesc = $Lang::tr{'click to enable'};
    }
				
    #Colorize each line
    if ($settings{'KEY1'} eq $key) {
	print "<tr bgcolor='${Header::colouryellow}'>";
    } elsif ($key % 2) {
	print "<tr bgcolor='$color{'color22'}'>";
    } else {
	print "<tr bgcolor='$color{'color20'}'>"; 
    }
    
    #if a field is empty, replace it with a '---' to see colorized info!
    $temp[1] = '---' if (!$temp[1]);
    $temp[2] = '---' if (!$temp[2]);

    print <<END
<td align='center'><a href='http://$temp[0]'>$temp[0]</a></td>
<td align='center'>$sync$temp[1]</td>
<td align='center'>$sync$temp[2]</td>

<td align='center'>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='ACTION' value='$Lang::tr{'toggle enable disable'}' />
<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gifproxy' alt='$descproxy' title='$descproxy' />
<input type='hidden' name='KEY1' value='$key' />
<input type='hidden' name='KEY2' value='3' />
</form>
</td>

<td align='center'>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='ACTION' value='$Lang::tr{'toggle enable disable'}' />
<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gifwildcard' alt='$descwildcard' title='$descwildcard' />
<input type='hidden' name='KEY1' value='$key' />
<input type='hidden' name='KEY2' value='4' />
</form>
</td>

<td align='center'>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='ACTION' value='$Lang::tr{'toggle enable disable'}' />
<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif' alt='$gdesc' title='$gdesc' />
<input type='hidden' name='KEY1' value='$key' />
<input type='hidden' name='KEY2' value='7' />
</form>
</td>

<td align='center'>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='ACTION' value='$Lang::tr{'edit'}' />
<input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' />
<input type='hidden' name='KEY1' value='$key' />
</form>
</td>

<td align='center'>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='ACTION' value='$Lang::tr{'remove'}' />
<input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' alt='$Lang::tr{'remove'}' title='$Lang::tr{'remove'}' />
<input type='hidden' name='KEY1' value='$key' />
</form>
</td>
</tr>
END
;
    $key++;
}
print "</table>";

# If table contains entries, print 'Key to action icons'
if ($key) {
print <<END
<table width='100%'>
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
    <form method='post' action='$ENV{'SCRIPT_NAME'}'>
        <td align='center' width='30%'><input type='submit' name='ACTION' value='$Lang::tr{'instant update'}' /></td>
    </form>
</tr>
</table>
END
;
}

&Header::closebox();
&Header::closebigbox();
&Header::closepage();

## Ouf it's the end !


# write the "current" array
sub WriteDataFile {
    #Save current
    open(FILE, ">$datafile") or die 'ddns datafile error';
    print FILE @current;
    close (FILE);
}
