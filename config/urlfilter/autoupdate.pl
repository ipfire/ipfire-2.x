#!/usr/bin/perl
#
# This code is distributed under the terms of the GPL
#
# (c) 2004-2007 marco.s - http://www.urlfilter.net
#
# $Id: autoupdate.pl,v 1.1 2007/03/14 00:00:00 marco.s Exp $
#
use strict;

my $make_clean = 1;

my $swroot = "/var/ipfire";
my $target = "$swroot/urlfilter/download";
my $tempdb = "$target/blacklists";
my $dbdir  = "$swroot/urlfilter/blacklists";

my $sourceurlfile = "$swroot/urlfilter/autoupdate/autoupdate.urls";
my $updconffile = "$swroot/urlfilter/autoupdate/autoupdate.conf";
my $updflagfile = "$swroot/urlfilter/blacklists/.autoupdate.last";

my %cgiparams;
my %updatesettings;
my $blacklist_url;
my $blacklist_src;
my $source_url;
my $source_name;
my @source_urllist;

my @categories;
my $blacklist;
my $category;

my $exitcode = 1;

if (-e "$sourceurlfile")
{
	open(FILE, $sourceurlfile);
	@source_urllist = <FILE>;
	close(FILE);
}

if (-e "$updconffile") { &readhash("$updconffile", \%updatesettings); }

if (@ARGV[0] =~ m@^(f|h)tt?ps?://@) { $updatesettings{'UPDATE_SOURCE'} = @ARGV[0]; }

if ($updatesettings{'UPDATE_SOURCE'} eq 'custom')
{
	$blacklist_url=$updatesettings{'CUSTOM_UPDATE_URL'};
} else {
	$blacklist_url=$updatesettings{'UPDATE_SOURCE'};
	foreach (@source_urllist)
	{
		chomp;
		$source_name = substr($_,0,rindex($_,","));
		$source_url = substr($_,index($_,",")+1);
		if ($blacklist_url eq $source_url) { $blacklist_src=$source_name; }
	}
}

if ($blacklist_src eq '') { $blacklist_src="custom source URL"; }

$blacklist_url =~ s/\&/\\\&/;

$blacklist=substr($blacklist_url,rindex($blacklist_url,"/")+1);
if (($blacklist =~ /\?/) || (!($blacklist =~ /\.t(ar\.)?gz$/))) { $blacklist = 'blacklist.tar.gz'; }
$blacklist=$target.'/'.$blacklist;

unless ($blacklist_url eq '')
{

	if (-d $target) { system("rm -rf $target"); }
	system("mkdir $target");

	system("/usr/bin/wget -o $target/wget.log -O $blacklist $blacklist_url");

	if (-e $blacklist)
	{
		system("/bin/tar --no-same-owner -xzf $blacklist -C $target");
		if (-d "$target/BL") { system ("mv $target/BL $target/blacklists"); }
		if (-d "$tempdb")
		{
			undef(@categories);
			&getblockcategory ($tempdb);
			foreach (@categories) { $_ = substr($_,length($tempdb)+1); }

			open(FILE, ">$target/update.conf");
			flock FILE, 2;
			print FILE "logdir $target\n";
			print FILE "dbhome $tempdb\n\n";

			foreach $category (@categories) {
				$blacklist = $category;
				$category =~ s/\//_/g;
				print FILE "dest $category {\n";
				if (-s "$tempdb/$blacklist/domains") {
					print FILE "    domainlist     $blacklist\/domains\n";
				}
				if (-s "$tempdb/$blacklist/urls") {
					print FILE "    urllist        $blacklist\/urls\n";
				}
				print FILE "}\n\n";
				$category = $blacklist;
			}

			print FILE "acl {\n";
			print FILE "    default {\n";
			print FILE "        pass none\n";
			print FILE "    }\n";
			print FILE "}\n";
			close FILE;

			system("/usr/bin/squidGuard -d -c $target/update.conf -C all");

			system("cp -r $target/blacklists/* $dbdir");

			system("chown -R nobody.nobody $dbdir");

			&setpermissions ($dbdir);

			system("touch $updflagfile");
			system("chown nobody.nobody $updflagfile");

			system("/etc/init.d/squid restart");

			system("logger -t installpackage[urlfilter] \"URL filter blacklist - Update from $blacklist_src completed\"");

			$exitcode = 0;

         	} else {
			system("logger -t installpackage[urlfilter] \"URL filter blacklist - ERROR: Not a valid URL filter blacklist\"");
		}
	} else {
		system("logger -t installpackage[urlfilter] \"URL filter blacklist - ERROR: Unable to retrieve blacklist from $blacklist_src\"");
	}

} else {
	system("logger -t installpackage[urlfilter] \"URL filter blacklist - ERROR: No update source defined\"");
}

if ((-d $target) && ($make_clean)) { system("rm -rf $target"); }

exit $exitcode;

# -------------------------------------------------------------------

sub readhash
{
	my $filename = $_[0];
	my $hash = $_[1];
	my ($var, $val);

	if (-e $filename)
	{
		open(FILE, $filename) or die "Unable to read file $filename";
		while (<FILE>)
		{
			chop;
			($var, $val) = split /=/, $_, 2;
			if ($var)
			{
				$val =~ s/^\'//g;
				$val =~ s/\'$//g;
	
				# Untaint variables read from hash
				$var =~ /([A-Za-z0-9_-]*)/;        $var = $1;
				$val =~ /([\w\W]*)/; $val = $1;
				$hash->{$var} = $val;
			}
		}
		close FILE;
	}
}

# -------------------------------------------------------------------

sub getblockcategory
{
	foreach $category (<$_[0]/*>)
	{
		if (-d $category)
		{
			if ((-s "$category/domains") || (-s "$category/urls"))
			{
				unless ($category =~ /\bcustom\b/) { push(@categories,$category); }
			}
			&getblockcategory ($category);
		}
	}
}

# -------------------------------------------------------------------

sub setpermissions
{
	my $bldir = $_[0];

	foreach $category (<$bldir/*>)
	{
        	 if (-d $category){
			system("chmod 755 $category &> /dev/null");
			foreach $blacklist (<$category/*>)
			{
         			if (-f $blacklist) { system("chmod 644 $blacklist &> /dev/null"); }
         			if (-d $blacklist) { system("chmod 755 $blacklist &> /dev/null"); }
			}
        	 	system("chmod 666 $category/*.db &> /dev/null");
			&setpermissions ($category);
		}
	 }
}

# -------------------------------------------------------------------
