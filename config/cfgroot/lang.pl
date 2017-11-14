# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
# Copyright (c) 2002/08/23 Mark Wormgoor <mark@wormgoor.com> Split from header.pl
#
# $Id: lang.pl,v 1.1.2.11 2005/09/10 16:22:50 eoberlander Exp $
#

package Lang;
require 'CONFIG_ROOT/general-functions.pl';
use strict;

### A cache file to avoid long recalculation
$Lang::CacheLang = '/var/ipfire/langs/cache-lang.pl';

# When you want to add your own language strings/entries to the ipcop language file,
# you should create a file with <PREFIX>.<LANG>.pl into CONFIG_ROOT/addon-lang dir
#	<PREFIX> is free choosable but should be significant. An Example might be "myAddnName"
# 	<LANG> is a mnemonic of the used language like en, de, it, nl etc.
#		You can find a detailed list of possible mnemonic's in the file CONFIG_ROOT/langs/list
# A file could be named "VirtualHttpd.en.pl" for example.
#
# The file content has to start with (of course without the leading #):
# --------- CODE ---------
#%tr = (%tr,
# 'key1' => 'value',				# add all your entries key/values here 
# 'key2' => 'value'				# and end with (of course without the leading #):
#);
# --------- CODE END---------
#
# After you have copied all your files to CONFIG_ROOT/add-lang you have to run the
# script compilation:
# perl -e "require '/CONFIG_ROOT/lang.pl'; &Lang::BuildCacheLang"


### Initialize language
%Lang::tr = ();
my %settings = ();
&General::readhash("${General::swroot}/main/settings", \%settings);
reload($settings{'LANGUAGE'});

# language variable used by makegraphs script
our $language;
$language = $settings{'LANGUAGE'};

#
# Load requested language file from cachefile. If cachefile doesn't exist, build on the fly.
# (it is a developper options)
#
sub reload {
    my $LG = &FindWebLanguage(shift);

    %Lang::tr = ();	# start with a clean array

    # Use CacheLang if present & not empty.
    if (-s "$Lang::CacheLang.$LG" ) {
	##fix: need to put a lock_shared on it in case rebuild is active ?
	do "$Lang::CacheLang.$LG";
        #&General::log ("cachelang file used [$LG]");	
	return;
    }
    
    #&General::log("Building on the fly cachelang file for [$LG]");
    do "${General::swroot}/langs/en.pl";
    do "${General::swroot}/langs/$LG.pl" if ($LG ne 'en');

    my $AddonDir = ${General::swroot}.'/addon-lang';

    opendir (DIR, $AddonDir);
    my @files = readdir (DIR);
    closedir (DIR);

    # default is to load english first
    foreach my $file ( grep (/.*\.en.pl$/,@files)) {
    	do "$AddonDir/$file";
    }

    # read again, overwriting 'en' with choosed lang
    if ($LG ne 'en') {
	foreach my $file (grep (/.*\.$LG\.pl$/,@files) ) {
    	    do "$AddonDir/$file";
	}
    }
}

#
# Assume this procedure is called with enough privileges.
# Merge ipcop langage file + all other extension found in addon-lang
# to build a 'cachefile' for selected language
#
sub BuildUniqueCacheLang {

    my ($LG) = @_;
    
    # Make CacheLang empty so that it won't be used by Lang::reload
    open (FILE, ">$Lang::CacheLang.$LG") or return 1;
    flock (FILE, 2) or return 1;
    close (FILE);

    # Load languages files
    &Lang::reload ($LG);
    
    # Write the unique %tr=('key'=>'value') array
    open (FILE, ">$Lang::CacheLang.$LG") or return 1;
    flock (FILE, 2) or return 1;
    print FILE '%tr=(';
    foreach my $k ( keys %Lang::tr ){
	$Lang::tr{$k} =~ s/\'/\\\'/g;                   # quote ' => \'
	print FILE "'$k' => '$Lang::tr{$k}',";  	# key => value,
    }
    print FILE ');';
    close (FILE);
    
    # Make nobody:nobody file's owner
    # Will work when called by root/rc.sysinit
    chown (0,0,"$Lang::CacheLang.$LG");
    chmod (0004,"$Lang::CacheLang.$LG");
    return 0;
}

#
# Switch Ipcop Language for each lang then call build cachelang
#
sub BuildCacheLang {

    my $AddonDir = ${General::swroot}.'/addon-lang';
    
    # Correct permission in case addon-installer did not do it
    opendir (DIR, $AddonDir);
    my @files = readdir (DIR);
    foreach my $file (@files) {
	next if (($file eq '..') || ($file eq '.'));
	chown (0,0,"$AddonDir/$file");
	chmod (0004,"$AddonDir/$file");
    }
    closedir (DIR);

    my $selected = '';;
    my $missed = '';
    my $error = 0;
    
    open (LANGS, "${General::swroot}/langs/list");
    while (<LANGS>) {
	($selected) = split (':');
	if (BuildUniqueCacheLang ($selected) == 1) {
	    $missed = $selected; # will try latter. Can only be the current cachelang file locked
	};
    }
    close (LANGS);

    if ($missed) { # collision with current cache lang being used ?
	$error = &BuildUniqueCacheLang ($missed);
    }
    
    &General::log ("WARNING: cannot build cachelang file for [$missed].") if ($error);
    return $error;
}

sub FindWebLanguage() {
	my $lang = shift;

	my @options = ($lang);

	my ($shortlang, $encoding) = split(/\./, $lang);
	push(@options, $shortlang);

	my ($language, $country) = split(/_/, $shortlang);
	push(@options, $language);

	# Add English as fallback
	push(@options, "en");

	foreach my $option (@options) {
		return $option if (-e "${General::swroot}/langs/$option.pl");
	}

	return undef;
}

sub DetectBrowserLanguages() {
	my $langs = $ENV{"HTTP_ACCEPT_LANGUAGE"};
	my @results = ();

	foreach my $lang (split /[,;]/, $langs) {
		# Drop all q= arguments
		next if ($lang =~ m/^q=/);

		push(@results, $lang);
	}

	return @results;
}

1;
