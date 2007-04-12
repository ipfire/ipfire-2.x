#!/usr/bin/perl
#
# This code is distributed under the terms of the GPL
#
# (c) written from scratch
#

$dbdir="/var/ipfire/urlfilter/blacklists";

system("/usr/bin/squidGuard -C all");

if (-e "$dbdir/custom/allowed/domains.db") { unlink("$dbdir/custom/allowed/domains.db"); }
if (-e "$dbdir/custom/allowed/urls.db")    { unlink("$dbdir/custom/allowed/urls.db"); }
if (-e "$dbdir/custom/blocked/domains.db") { unlink("$dbdir/custom/blocked/domains.db"); }
if (-e "$dbdir/custom/blocked/urls.db")    { unlink("$dbdir/custom/blocked/urls.db"); }

system("chown -R nobody.nobody $dbdir");

&setpermissions ($dbdir);

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
