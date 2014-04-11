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
#
# this cgi is base on IPCop CGI - aliases.cgi
#

# to fully troubleshot your code, uncomment diagnostics, Carp and cluck lines
#use diagnostics; # need to add the file /usr/lib/perl5/5.8.x/pods/perldiag.pod before to work
# next look at /var/log/httpd/error_log , http://www.perl.com/pub/a/2002/05/07/mod_perl.html may help
#use warnings;
use strict;
#use Carp ();
#local $SIG{__WARN__} = \&Carp::cluck;

require '/var/ipfire/general-functions.pl';	# replace /var/ipcop with /var/ipcop in case of manual install
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my $configfwdfw		= "${General::swroot}/firewall/config";
my $configinput		= "${General::swroot}/firewall/input";
my $configoutgoing	= "${General::swroot}/firewall/outgoing";
my %input=();
my %forward=();
my %output=();

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::colouryellow} );
   @dummy = ( ${Header::table1colour} );
   @dummy = ( ${Header::table2colour} );
undef (@dummy);

# Files used
my $setting = "${General::swroot}/ethernet/settings";
our $datafile = "${General::swroot}/ethernet/aliases";


our %settings=();
#Settings1

#Settings2 for editing the multi-line list
#Must not be saved !
$settings{'IP'} = '';
$settings{'ENABLED'} = 'off';		# Every check box must be set to off
$settings{'NAME'} = '';
my @nosaved=('IP','ENABLED','NAME');	# List here ALL setting2 fields. Mandatory
    
$settings{'ACTION'} = '';		# add/edit/remove
$settings{'KEY1'} = '';			# point record for ACTION

#Define each field that can be used to sort columns
my $sortstring='^IP|^NAME';
my $errormessage = '';
my $warnmessage = '';

&Header::showhttpheaders();

# Read needed Ipcop netsettings
my %netsettings=();
$netsettings{'SORT_ALIASES'} = 'NAME'; 	# default sort
&General::readhash($setting, \%netsettings);

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
# Remove if no Setting1 needed
#
if ($settings{'ACTION'} eq $Lang::tr{'save'}) {
    
    #
    #Validate static Settings1 here
    #
    unless ($errormessage) {					# Everything is ok, save settings
	#map (delete ($settings{$_}) ,(@nosaved,'ACTION','KEY1'));# Must never be saved 
	#&General::writehash($setting, \%settings);		# Save good settings
	#$settings{'ACTION'} = $Lang::tr{'save'};		# Recreate  'ACTION'
	#map ($settings{$_}= '',(@nosaved,'KEY1'));		# and reinit var to empty
	
	# Rebuild configuration file if needed
	&BuildConfiguration;
    }

    ERROR:						# Leave the faulty field untouched
} else {
    #&General::readhash($setting, \%settings);  	# Get saved settings and reset to good if needed
}

## Now manipulate the multi-line list with Settings2
# Basic actions are:
#	toggle the check box
#	add/update a new line
#	begin editing a line
#	remove a line


# Toggle enable/disable field.  Field is in second position
if ($settings{'ACTION'} eq $Lang::tr{'toggle enable disable'}) {
    #move out new line
    chomp(@current[$settings{'KEY1'}]);
    my @temp = split(/\,/,@current[$settings{'KEY1'}]);
    $temp[1] = $temp[1] eq 'on' ? 'off' : 'on';		# Toggle the field
    $temp[2] = '' if ( $temp[2] eq '' );
    @current[$settings{'KEY1'}] = join (',',@temp)."\n";
    $settings{'KEY1'} = ''; 				# End edit mode
    
    &General::log($Lang::tr{'ip alias changed'});
    
    #Save current
    open(FILE, ">$datafile") or die 'Unable to open aliases file.';
    print FILE @current;
    close(FILE);
	
    # Rebuild configuration file
    &BuildConfiguration;
}

if ($settings{'ACTION'} eq $Lang::tr{'add'}) {
    # Validate inputs
    if (! &General::validip($settings{'IP'})) {$errormessage = "invalid ip"};
    $settings{'NAME'} = &Header::cleanhtml($settings{'NAME'});

    # Make sure we haven't duplicated an alias or RED
    my $spacer='';
    if ($settings{'IP'} eq $netsettings{'RED_ADDRESS'}) {
	$errormessage = $Lang::tr{'duplicate ip'} . ' (RED)';
        $spacer=" & ";
    }
    #Check if we have an emtpy name
    if (!$settings{'NAME'}){
		$errormessage=$Lang::tr{'fwhost err name1'};
	}elsif(! &General::validfqdn($settings{'NAME'}) && ! &General::validhostname($settings{'NAME'})){
		$errormessage=$Lang::tr{'invalid hostname'};
	}
    my $idx=0;
    foreach my $line (@current) {
        chomp ($line);
        my @temp = split (/\,/, $line);
        if ( ($settings{'KEY1'} eq '')||(($settings{'KEY1'} ne '') && ($settings{'KEY1'} != $idx))) { # update
	    if ($temp[0] eq $settings{'IP'}) {
	        $errormessage .= $spacer.$Lang::tr{'duplicate ip'};
	        $spacer=" & ";
	    }
	    if ($temp[2] eq $settings{'NAME'} && $temp[2] ne '') {
		$errormessage .= $spacer.$Lang::tr{'duplicate name'};
		$spacer=" & ";
		}
	}
	$idx++;
    }
	#Update firewallrules if aliasname is changed
	if ($settings{'OLDNAME'} ne $settings {'NAME'}){
		&General::readhasharray("$configfwdfw", \%forward);
		&General::readhasharray("$configinput", \%input);
		&General::readhasharray("$configoutgoing", \%output);
		#Check FORWARD
		foreach my $forwardkey (sort keys %forward){
			if ($forward{$forwardkey}[29] eq $settings{'OLDNAME'}){
				$forward{$forwardkey}[29] = $settings {'NAME'};
			}
		}
		&General::writehasharray($configfwdfw, \%forward);
		#Check INPUT
		foreach my $inputkey (sort keys %input){
			if ($input{$inputkey}[6] eq $settings{'OLDNAME'}){
				$input{$inputkey}[6] = $settings {'NAME'};
			}
		}
		&General::writehasharray($configinput, \%input);
		#Check OUTPUT
		foreach my $outputkey (sort keys %output){
			if ($output{$outputkey}[4] eq $settings{'OLDNAME'}){
				$output{$outputkey}[4] = $settings {'NAME'};
			}
		}
		&General::writehasharray($configoutgoing, \%output);
		&General::firewall_config_changed;
	}
	#If Alias IP has changed, set firewall_config_changed
	if($settings{'OLDIP'} ne $settings{'IP'} && $settings{'OLDIP'}){
		&General::firewall_config_changed;
	}
    unless ($errormessage) {
	if ($settings{'KEY1'} eq '') { #add or edit ?
	    unshift (@current, "$settings{'IP'},$settings{'ENABLED'},$settings{'NAME'}\n");
	    &General::log($Lang::tr{'ip alias added'});
	} else {
	    @current[$settings{'KEY1'}] = "$settings{'IP'},$settings{'ENABLED'},$settings{'NAME'}\n";
	    $settings{'KEY1'} = '';       # End edit mode
	    &General::log($Lang::tr{'ip alias changed'});
	}

	# Write changes to config file.
	&SortDataFile;				# sort newly added/modified entry

	&BuildConfiguration;			# then re-build conf which use new data
	
##
## if entering data line is repetitive, choose here to not erase fields between each addition
##
	map ($settings{$_}='' ,@nosaved);	# Clear fields
    }
}

if ($settings{'ACTION'} eq $Lang::tr{'edit'}) {
    #move out new line
    my $line = @current[$settings{'KEY1'}];	# KEY1 is the index in current
    chomp($line);
    my @temp = split(/\,/, $line);

##
## move data fields to Setting2 for edition
##
    $settings{'IP'}=$temp[0];			# Prepare the screen for editing
    $settings{'ENABLED'}=$temp[1];
    $settings{'NAME'}=$temp[2];
}

if ($settings{'ACTION'} eq $Lang::tr{'remove'}) {
    splice (@current,$settings{'KEY1'},1);		# Delete line 
    open(FILE, ">$datafile") or die 'Unable to open aliases file.';
    print FILE @current;
    close(FILE);
    $settings{'KEY1'} = '';				# End remove mode
    &General::log($Lang::tr{'ip alias removed'});

    &BuildConfiguration;				# then re-build conf which use new data
}



##  Check if sorting is asked
# If same column clicked, reverse the sort.
if ($ENV{'QUERY_STRING'} =~ /$sortstring/ ) {
    my $newsort=$ENV{'QUERY_STRING'};
    my $actual=$netsettings{'SORT_ALIASES'};
    #Reverse actual sort ?
    if ($actual =~ $newsort) {
	my $Rev='';
	if ($actual !~ 'Rev') {
	    $Rev='Rev';
	}
	$newsort.=$Rev;
    }
    $netsettings{'SORT_ALIASES'}=$newsort;
    &General::writehash($setting, \%netsettings);
    &SortDataFile;
    $settings{'ACTION'} = 'SORT';			# Recreate  'ACTION'
}

# Default initial value
if ($settings{'ACTION'} eq '' ) { # First launch from GUI
    $settings{'ENABLED'} ='on';
}
    
&Header::openpage($Lang::tr{'external aliases configuration'}, 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);
my %checked =();     # Checkbox manipulations

if ($errormessage) {
    &Header::openbox('100%', 'left', $Lang::tr{'error messages'});
    print "$errormessage&nbsp;";
    &Header::closebox();
}
unless (( $netsettings{'CONFIG_TYPE'} =~ /^(1|2|3|4)$/ ) && ($netsettings{'RED_TYPE'} eq 'STATIC'))
{
    &Header::openbox('100%', 'left', $Lang::tr{'capswarning'});
    print <<END
    <table style='width:100%;'>
    <tr>
    <td class='boldbase' style='color:${Header::colourred};'><b>$Lang::tr{'aliases not active'}</b></td>
    </tr>
    </table>
END
;
    &Header::closebox();
}
									
#
# Second check box is for editing the list
#
$checked{'ENABLED'}{'on'} = ($settings{'ENABLED'} eq 'on') ? "checked='checked'" : '' ;

my $buttontext = $Lang::tr{'add'};
if ($settings{'KEY1'} ne '') {
    $buttontext = $Lang::tr{'update'};
    &Header::openbox('100%', 'left', $Lang::tr{'edit an existing alias'});
} else {
    &Header::openbox('100%', 'left', $Lang::tr{'add new alias'});
}

#Edited line number (KEY1) passed until cleared by 'save' or 'remove' or 'new sort order'
print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='KEY1' value='$settings{'KEY1'}' />
<input type='hidden' name='OLDNAME' value='$settings{'NAME'}' />
<input type='hidden' name='OLDIP' value='$settings{'IP'}' />
<table style='width:100%;'>
<tr>
<td class='base' style='color:${Header::colourred};'>$Lang::tr{'name'}:</td>
<td><input type='text' name='NAME' value='$settings{'NAME'}' size='32' /></td>
<td class='base' style='text-align:right; color:${Header::colourred};'>$Lang::tr{'alias ip'}:&nbsp;</td>
<td><input type='text' name='IP' value='$settings{'IP'}' size='16' /></td>
<td class='base' style='text-align:right;'>$Lang::tr{'enabled'}&nbsp;</td>
<td><input type='checkbox' name='ENABLED' $checked{'ENABLED'}{'on'} /></td>
</tr>
</table>
<br>
<hr />
<table style='width:100%;'>
<tr>
    <td style='text-align:right;'><input type='hidden' name='ACTION' value='$Lang::tr{'add'}' /><input type='submit' name='SUBMIT' value='$buttontext' /></td>
</tr>
</table>
</form>
END
;
&Header::closebox();

# Add visual indicators to column headings to show sort order - EO
my $sortarrow1 = '';
my $sortarrow2 = '';

if ($netsettings{'SORT_ALIASES'} eq 'NAMERev') {
	$sortarrow1 = $Header::sortdn;
} elsif ($netsettings{'SORT_ALIASES'} eq 'NAME') {
	$sortarrow1 = $Header::sortup;
} elsif ($netsettings{'SORT_ALIASES'} eq 'IPRev') {
	$sortarrow2 = $Header::sortdn;
} else {
	$sortarrow2 = $Header::sortup;
}

#
# Third box shows the list, in columns
#
# Columns headers may content a link. In this case it must be named in $sortstring
#
&Header::openbox('100%', 'left', $Lang::tr{'current aliases'});
print <<END
<table class='tbl' style='width:100%;'>
<tr>
    <th style='width:55%; text-align:center;'><a href='$ENV{'SCRIPT_NAME'}?NAME'><b>$Lang::tr{'name'}</b></a> $sortarrow1</th>
    <th style='width:45%; text-align:center;'><a href='$ENV{'SCRIPT_NAME'}?IP'><b>$Lang::tr{'alias ip'}</b></a> $sortarrow2</th>
    <th colspan='3' class='boldbase' style='width:5%; text-align:center;'><b>$Lang::tr{'action'}</b></th>
</tr>
END
;

#
# Print each line of @current list
#
# each data line is splitted into @temp.
#

my $key = 0;
my $col="";
foreach my $line (@current) {
    chomp($line);
    my @temp = split(/\,/,$line);

    #Choose icon for checkbox
    my $gif = '';
    my $gdesc = '';
    if ($temp[1] eq "on") {
	$gif = 'on.gif';
	$gdesc = $Lang::tr{'click to disable'};
    } else {
	$gif = 'off.gif';
	$gdesc = $Lang::tr{'click to enable'}; 
    }

    #Colorize each line
    if ($settings{'KEY1'} eq $key) {
        $col="background-color:${Header::colouryellow};";
    } elsif ($key % 2) {
        $col="background-color:${Header::table2colour};";
    } else {
        $col="background-color:${Header::table1colour};";
    }
    print "<tr style='$col'>";

    print <<END
<td style='text-align:center; $col'>$temp[2]</td>
<td style='text-align:center; $col'>$temp[0]</td>

<td style='text-align:center; $col'>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='ACTION' value='$Lang::tr{'toggle enable disable'}' />
<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif' alt='$gdesc' title='$gdesc' />
<input type='hidden' name='KEY1' value='$key' />
</form>
</td>

<td style='text-align:center; $col'>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='ACTION' value='$Lang::tr{'edit'}' />
<input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' />
<input type='hidden' name='KEY1' value='$key' />
</form>
</td>

<td style='text-align:center; $col'>
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
&Header::closebigbox();
&Header::closepage();

## Ouf it's the end !



# Sort the "current" array according to choices
sub SortDataFile
{
    our %entries = ();
    
    # Sort pair of record received in $a $b special vars.
    # When IP is specified use numeric sort else alpha.
    # If sortname ends with 'Rev', do reverse sort.
    #
    sub fixedleasesort {
	my $qs='';             # The sort field specified minus 'Rev'
	if (rindex ($netsettings{'SORT_ALIASES'},'Rev') != -1) {
	    $qs=substr ($netsettings{'SORT_ALIASES'},0,length($netsettings{'SORT_ALIASES'})-3);
	    if ($qs eq 'IP') {
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
	    $qs=$netsettings{'SORT_ALIASES'};
	    if ($qs eq 'IP') {
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
    my $key = 0;
    foreach my $line (@current) {
	chomp( $line); #remove newline because can be on field 5 or 6 (addition of REMARK)
	my @temp = split (',',$line);
	
	# Build a pair 'Field Name',value for each of the data dataline.
	# Each SORTABLE field must have is pair.
	# Other data fields (non sortable) can be grouped in one
	
	# Exemple
	# F1,F2,F3,F4,F5       only F1 F2 for sorting
	# my @record = ('KEY',$key++,
	#		'F1',$temp[0],
	#		'F2',$temp[1],
	#		'DATA',join(',',@temp[2..4])	);  #group remainning values, with separator (,)
	
	# The KEY,key record permits doublons. If removed, then F1 becomes the key without doublon permitted.
	
	
	my @record = ('KEY',$key++,'IP',$temp[0],'ENABLED',$temp[1],'NAME',$temp[2]);
	my $record = {};                        	# create a reference to empty hash
	%{$record} = @record;                		# populate that hash with @record
	$entries{$record->{KEY}} = $record; 		# add this to a hash of hashes
    }
    
    open(FILE, ">$datafile") or die 'Unable to open aliases file.';

    # Each field value is printed , with the newline ! Don't forget separator and order of them.
    foreach my $entry (sort fixedleasesort keys %entries) {
	print FILE "$entries{$entry}->{IP},$entries{$entry}->{ENABLED},$entries{$entry}->{NAME}\n";
    }

    close(FILE);
    # Reload sorted  @current
    open (FILE, "$datafile");
    @current = <FILE>;
    close (FILE);
}

#						    
# Build the configuration file for application aliases
#
sub BuildConfiguration {
    # Restart service associated with this
    system '/usr/local/bin/setaliases';
}

