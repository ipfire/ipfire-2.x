#!/usr/bin/perl
#
# IPFire CGI's - base.cgi
#
# This code is distributed under the terms of the GPL
#
# (c) place a name here
#
# $Id: base.cgi,v 1.1.2.10 2005/11/03 19:20:50 franck78 Exp $
#
#


# This file is a starting base for writting a new GUI screen using the three box model
#	Box 1 : global settings for the application
#	Box 2 : line editor for multiple data line
#	Box 3 : the list of data line, with edit/remove buttons
#
#	This example do the following
#	Read global settings:
#		a NAME and an interface (IT)
#	Lines of data composed of:
#		an ipaddress (IP), an enabled/disabled options (CB), a comment (CO)
#
#
# All you need to do is
#	replace 'XY' with your app name
# 	define your global $settings{'var name'}
#	define your strings
#	write validation code for Settings1 and Settings2
#	write HTML box Settings1 and Settings2
#	adapt the sort function
#	write the correct configuration file
#
#
# to fully troubleshot your code, uncomment diagnostics, Carp and cluck lines
# use diagnostics; # need to add the file /usr/lib/perl5/5.8.x/pods/perldiag.pod before to work
# next look at /var/log/httpd/error_log , http://www.perl.com/pub/a/2002/05/07/mod_perl.html may help
#use warnings;
use strict;
#use Carp ();
#local $SIG{__WARN__} = \&Carp::cluck;

require '/var/ipfire/general-functions.pl';	# Replace all occurences of </var/ipfire> with CONFIG_ROOT
						# before updating cvs IPFire file.
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

# Files used
our $setting  = "${General::swroot}/XY/settings";		# particular settings
my  $datafile = "${General::swroot}/XY/data";			# repeted settings (multilines)
our $conffile = "${General::swroot}/XY/XY.conf";		# Config file for application XY

# strings to add to languages databases or in addon language file
$Lang::tr{'XY title'}     = 'XY service';
$Lang::tr{'XY settings'}  = 'XY setup';
$Lang::tr{'XY add data'}  = 'add data';
$Lang::tr{'XY edit data'} = 'edit data';
$Lang::tr{'XY data'}      = 'XY data';

# informationnal & log strings, no translation required
my  $msg_added           = 'XY added';
my  $msg_modified        = 'XY modified';
my  $msg_deleted         = 'XY removed';
my  $msg_datafileerror   = 'XY data file error';
our $msg_configfileerror = 'XY configuration file error';

my %settings=();

# Settings1
$settings{'NAME'} = '';		# a string field than must be 'GOOD' or 'good'
$settings{'IT'} = '';		# a 'choose' field for color interface
$settings{'TURBO'} = 'off';	# a checkbox field to enable something

# Settings2 for editing the multi-line list
# Must not be saved by writehash !
$settings{'IP'} = '';			# datalines are: IPaddress,enable,comment 
$settings{'CB'} = 'off';		# Every check box must be set to off
$settings{'COMMENT'} = '';
my @nosaved=('IP','CB','COMMENT');        # List here ALL setting2 fields. Mandatory

$settings{'ACTION'} = '';		# add/edit/remove....
$settings{'KEY1'} = '';			# point record for ACTION

# Define each field that can be used to sort columns
my $sortstring='^IP|^COMMENT';
my $errormessage = '';
my $warnmessage = '';

&Header::showhttpheaders();

# Read needed Ipcop settings (exemple)
my %mainsettings=();
&General::readhash("${General::swroot}/main/settings", \%mainsettings);

# Get GUI values
&Header::getcgihash(\%settings);

# Load multiline data. Do it before use in save action
our $f = new Multilines (filename => $datafile,
			 fields   => ['IP','CB','COMMENT'],
			 comment  => 1
			);

##
## SAVE Settings1 
##
# Remove if no Settings1 needed
if ($settings{'ACTION'} eq $Lang::tr{'save'}) {

    #
    #Validate static Settings1 here
    #
    if (($settings{"NAME"} ne "GOOD") &&
	($settings{"NAME"} ne "good"))    {
	$errormessage = 'Enter good or GOOD in Name field';
    }

    unless ($errormessage) {					# Everything is ok, save settings
	map (delete ($settings{$_}) ,(@nosaved,'ACTION','KEY1'));# Must never be saved
	&General::writehash($setting, \%settings);		# Save good settings
	$settings{'ACTION'} = $Lang::tr{'save'};		# Recreate  'ACTION'
	map ($settings{$_}= '',(@nosaved,'KEY1'));		# and reinit var to empty

	# Rebuild configuration file if needed
	&BuildConfiguration;
    }

    ERROR:						# Leave the faulty field untouched
} else {
    &General::readhash($setting, \%settings);  		# Get saved settings and reset to good if needed
}

##
## Now manipulate the multiline list with Settings2
##

# Basic actions are:
#	toggle the check box
#	add/update a new line
#	begin editing a line
#	remove a line
# $KEY1 contains the index of the line manipulated

##
## Toggle CB field.
##
if ($settings{'ACTION'} eq $Lang::tr{'toggle enable disable'}) {

    $f->togglebyfields($settings{'KEY1'},'CB');		# toggle checkbox
    $settings{'KEY1'} = ''; 				# End edit mode

    &General::log($msg_modified);

    # save changes
    $f->savedata || die "$msg_datafileerror";

    # Rebuild configuration file
    &BuildConfiguration;
}

##
## ADD/UPDATE a line of configuration from Settings2
##
if ($settings{'ACTION'} eq $Lang::tr{'add'}) {
    # Validate inputs
    if (! &General::validip($settings{'IP'})) {$errormessage = "Specify an IP value !"};
    if (! $settings{'COMMENT'} ) {$warnmessage = "no comment specified"};

    unless ($errormessage) {
	if ($settings{'KEY1'} eq '') { #add or edit ?
	    # insert new data line
	    $f->writedata(-1, $settings{'IP'},$settings{'CB'},$settings{'COMMENT'});
	    &General::log($msg_added);
	} else {
	    # modify data line
	    $f->writedata($settings{'KEY1'}, $settings{'IP'},$settings{'CB'},$settings{'COMMENT'});
	    $settings{'KEY1'} = '';       # End edit mode
	    &General::log($msg_modified);
	}
	# save changes
	$f->savedata || die "$msg_datafileerror";

	# Rebuild configuration file
	&BuildConfiguration;

	# if entering data line is a repetitive task, choose here to not erase fields between each addition
	map ($settings{$_}='' ,@nosaved);
    }
}

##
## begin EDIT: move data fields to Settings2 controls
##
if ($settings{'ACTION'} eq $Lang::tr{'edit'}) {
    $f->readdata ($settings{'KEY1'},
		  $settings{'IP'},
		  $settings{'CB'},
		  $settings{'COMMENT'});
}
##
## REMOVE: remove selected line
##
if ($settings{'ACTION'} eq $Lang::tr{'remove'}) {
    $f->deleteline ($settings{'KEY1'});
    $settings{'KEY1'} = '';				# End remove mode
    &General::log($msg_deleted);

    # save changes
    $f->savedata || die "$msg_datafileerror";

    # Rebuild configuration file
    &BuildConfiguration;
}


##
## Check if sorting is asked
##
if ($ENV{'QUERY_STRING'} =~ /$sortstring/ ) {
    my $newsort=$ENV{'QUERY_STRING'};
    my $actual=$settings{'SORT_XY'};

    # Reverse actual sort or choose new column ?
    if ($actual =~ $newsort) {
	$f->setsortorder ($newsort ,rindex($actual,'Rev'));
	$newsort .= rindex($actual,'Rev')==-1 ? 'Rev' : '';
    } else {
	$f->setsortorder ($newsort ,1);
    }
    $f->savedata;						# Synchronise file & display
    $settings{'SORT_XY'} = $newsort;
    map (delete ($settings{$_}) ,(@nosaved,'ACTION','KEY1'));	# Must never be saved
    &General::writehash($setting, \%settings);
    $settings{'ACTION'} = 'SORT';				# Recreate an 'ACTION'
    map ($settings{$_}= '',(@nosaved,,'KEY1'));			# and reinit var to empty
}

##
## Remove if no Setting1 needed
##
if ($settings{'ACTION'} eq '' ) { # First launch from GUI
    # Place here default value when nothing is initialized

}

&Header::openpage($Lang::tr{'XY title'}, 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);
my %checked =();     # Checkbox manipulations

if ($errormessage) {
    &Header::openbox('100%', 'left', $Lang::tr{'error messages'});
    print "<font class='base'>$errormessage&nbsp;</font>";
    &Header::closebox();
}

##
## First box Settings1. Remove if not needed
##
$warnmessage = "<font color=${Header::colourred}><b>$Lang::tr{'capswarning'}</b></font>: $warnmessage" if ($warnmessage);

&Header::openbox('100%', 'left', $Lang::tr{'XY settings'});
print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>";
$checked{'IT'}{'RED'} = '';
$checked{'IT'}{'GREEN'} = '';
$checked{'IT'}{'ORANGE'} = '';
$checked{'IT'}{'BLUE'} = '';
$checked{'IT'}{$settings{'IT'}} = "checked='checked'";
$checked{'TURBO'} = ($settings{'TURBO'} eq 'on') ? "checked='checked'" : '';

print<<END
<table width='100%'>
<tr>
    <td class='base'>Name:</td>
    <td><input type='text' name='NAME' value='$settings{'NAME'}' /></td>
    <td align='right'>INTERFACE</td>
    <td align='right'>red<input type='radio' name='IT' value='RED' $checked{'IT'}{'RED'} /></td>
</tr><tr>
    <td>Turbo:</td>
    <td><input type='checkbox' name='TURBO' $checked{'TURBO'}' /></td>
    <td></td>
    <td align='right'>green<input type='radio' name='IT' value='GREEN' $checked{'IT'}{'GREEN'} /></td>
</tr><tr>
    <td></td>
    <td></td>
    <td></td>
    <td align='right'>blue<input type='radio' name='IT' value='BLUE' $checked{'IT'}{'BLUE'} /></td>
</tr><tr>
    <td></td>
    <td></td>
    <td></td>
    <td align='right'>orange<input type='radio' name='IT' value='ORANGE' $checked{'IT'}{'ORANGE'} /></td>
</tr>
</table>
<br />
END
;

print<<END
<table width='100%'>
<hr />
<tr>
    <td class='base' width='25%'><img src='/blob.gif' align='top' alt='*' />&nbsp;$Lang::tr{'this field may be blank'}</td>
    <td class='base' width='25%'>$warnmessage</td>
    <td width='50%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
</tr>
</table>
</form>
END
;
&Header::closebox();   # end of Settings1

##
## Second box is for editing the an item of the list
##
$checked{'CB'} = ($settings{'CB'} eq 'on') ? "checked='checked'" : '';

my $buttontext = $Lang::tr{'add'};
if ($settings{'KEY1'} ne '') {
    $buttontext = $Lang::tr{'update'};
    &Header::openbox('100%', 'left', $Lang::tr{'XY edit data'});
} else {
    &Header::openbox('100%', 'left', $Lang::tr{'XY add data'});
}

# Edited line number (KEY1) passed until cleared by 'save' or 'remove' or 'new sort order'
print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='KEY1' value='$settings{'KEY1'}' />
<table width='100%'>
<tr>
    <td class='base'>$Lang::tr{'ip address'}:</td>
    <td><input type='text' name='IP' value='$settings{'IP'}' /></td>
    <td class='base'>$Lang::tr{'enabled'}</td>
    <td><input type='checkbox' name='CB' $checked{'CB'} /></td>
    <td class='base'>$Lang::tr{'remark'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td><input type 'text' name='COMMENT' value='$settings{'COMMENT'}' /></td>
</tr>
</table>
<hr />
<table width='100%'>
<tr>
    <td class='base' width='50%'><img src='/blob.gif' align='top' alt='*' />&nbsp;$Lang::tr{'this field may be blank'}</td>
    <td width='50%' align='center'><input type='hidden' name='ACTION' value='$Lang::tr{'add'}' /><input type='submit' name='SUBMIT' value='$buttontext' /></td>
</tr>
</table>
</form>
END
;
&Header::closebox();

##
## Third box shows the list
##

# Columns headers may be a sort link. In this case it must be named in $sortstring
&Header::openbox('100%', 'left', $Lang::tr{'XY data'});
print <<END
<table width='100%'>
<tr>
    <td width='20%' align='center'><a href='$ENV{'SCRIPT_NAME'}?IP'><b>$Lang::tr{'ip address'}</b></a></td>
    <td width='70%' align='center'><a href='$ENV{'SCRIPT_NAME'}?COMMENT'><b>$Lang::tr{'remark'}</b></a></td>
    <td width='10%' colspan='3' class='boldbase' align='center'><b>$Lang::tr{'action'}</b></td>
</tr>
END
;

##
## Print each line of @current list
##
my $key = 0;
$f->readreset; # beginning of data
for ($key=0; $key<$f->getnumberofline; $key++) {

    my($cb,$comment,$ip) = $f->readbyfieldsseq($key,'CB','COMMENT','IP');

    #Choose icon for checkbox
    my $gif = '';
    my $gdesc = '';
    if ($cb eq "on") {
	$gif = 'on.gif';
	$gdesc = $Lang::tr{'click to disable'};
    } else {
	$gif = 'off.gif';
	$gdesc = $Lang::tr{'click to enable'};
    }

    #Colorize each line
    if ($settings{'KEY1'} eq $key) {
	print "<tr bgcolor='${Header::colouryellow}'>";
    } elsif ($key % 2) {
	print "<tr bgcolor='${Header::table2colour}'>";
    } else {
	print "<tr bgcolor='${Header::table1colour}'>"; 
    }

    print <<END
<td align='center'>$ip</td>
<td align='center'>$comment</td>

<td align='center'>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='ACTION' value='$Lang::tr{'toggle enable disable'}' />
<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif' alt='$gdesc' title='$gdesc' />
<input type='hidden' name='KEY1' value='$key' />
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
} print "</table>";

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

##
## Build the configuration file for application XY
##
sub BuildConfiguration {
    open(FILE, ">/$conffile") or die "$msg_configfileerror";
    flock(FILE, 2);

    #Global settings
    print FILE "#\n#  Configuration file for application XY\n#\n\n";
    print FILE "#     do not edit manually\n";
    print FILE "#     build for Ipcop:$mainsettings{'HOSTNAME'}\n\n\n";
    print FILE "service=$settings{'NAME'}\n";
    print FILE "activate-turbo\n" if $settings{'TURBO'} eq 'on';
    print FILE "interface=$settings{'IT'}\n\n\n";
    #write data line
    {
	my ($IP,$CB,$COMMENT);
	$f->readreset;
	while (defined ($f->readdataseq($IP,$CB,$COMMENT))) {
	    if ($CB eq "on") {
		print FILE "$IP\t\t\t\t\t#$COMMENT\n";
	    } else {
		print FILE "#DISABLED $IP\t\t\t\t#$COMMENT\n";
	    }
	}
    }
    close FILE;

    # Restart service
    #system '/usr/local/bin/restartyourhelper';
}
