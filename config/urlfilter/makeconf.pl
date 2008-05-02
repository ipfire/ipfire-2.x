#!/usr/bin/perl

$swroot="/var/ipfire";
$logdir="/var/log/squidGuard";
$dbdir="/var/ipfire/urlfilter/blacklists";

print "Creating configuration file ";
foreach $blacklist (<$dbdir/*>)
{
	if (-d $blacklist)
	{
		$lastslashpos = rindex($blacklist,"/");
		$section = substr($blacklist,$lastslashpos+1);
		push(@categories,$section);
	}
}
open(FILE, ">$swroot/urlfilter/squidGuard.conf");
print FILE "logdir $logdir\n";
print FILE "dbhome $dbdir\n\n";
foreach $category (@categories)
{
	print FILE "dest $category {\n";
	if (-e "$dbdir/$category/domains") {
		print FILE "    domainlist     $category\/domains\n";
	}
	if (-e "$dbdir/$category/urls") {
		print FILE "    urllist        $category\/urls\n";
	}
	print FILE "}\n\n";
}
print FILE "acl {\n";
print FILE "    default {\n";
print FILE "        pass all\n";
print FILE "    }\n";
print FILE "}\n";
close FILE;
print "\n";

print "Creating custom directories ";
mkdir("$dbdir/custom");
mkdir("$dbdir/custom/allowed");
mkdir("$dbdir/custom/blocked");
system("touch $dbdir/custom/allowed/domains");
system("touch $dbdir/custom/allowed/urls");
system("touch $dbdir/custom/blocked/domains");
system("touch $dbdir/custom/blocked/urls");
print "\n";

print "Building blacklist databases ";
system("$swroot/urlfilter/bin/prebuild.pl");
print "\n";

exit
