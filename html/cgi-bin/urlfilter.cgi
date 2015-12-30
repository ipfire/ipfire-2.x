#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2005-2010  IPFire Team                                        #
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

use File::Copy;
use IO::Socket;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my $http_port='81';
my %netsettings=();
my %mainsettings=();
my %proxysettings=();
my %filtersettings=();
my %tcsettings=();
my %uqsettings=();
my %besettings=();
my %updatesettings=();
my %checked=();
my %selected=();
my $id=0;
my $line='';
my $i=0;
my $n=0;
my $time='';
my $filesize;
my $category='';
my $section='';
my $blacklist='';
my $blistbackup='';

my $changed = 'no';
my $tcfile = "${General::swroot}/urlfilter/timeconst";
my $uqfile = "${General::swroot}/urlfilter/userquota";
my $dbdir = "${General::swroot}/urlfilter/blacklists";
my $editdir = "${General::swroot}/urlfilter/editor";
my $templatedir = "/srv/web/ipfire/html/redirect-templates";
my $repository = "/var/urlrepo";
my $hintcolour = '#FFFFCC';

my $sourceurlfile = "${General::swroot}/urlfilter/autoupdate/autoupdate.urls";
my $updconffile = "${General::swroot}/urlfilter/autoupdate/autoupdate.conf";
my $updflagfile = "${General::swroot}/urlfilter/blacklists/.autoupdate.last";

my $errormessage='';
my $updatemessage='';
my $restoremessage='';
my $buttontext='';
my $source_name='';
my $source_url='';
my $blacklistage=0;

my @repositorylist=();
my @repositoryfiles=();
my @categories=();
my @selectedcategories=();
my @filtergroups=();
my @tclist=();
my @uqlist=();
my @source_urllist=();
my @clients=();
my @temp=();

my $lastslashpos=0;

my $toggle='';
my $gif='';
my $led='';
my $ldesc='';
my $gdesc='';

if (! -d $dbdir) { mkdir("$dbdir"); }
if (! -e $tcfile) { system("touch $tcfile"); }
if (! -e $uqfile) { system("touch $uqfile"); }
if (! -e $sourceurlfile) { system("touch $sourceurlfile"); }

&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);

&readblockcategories;

open(FILE, $tcfile);
@tclist = <FILE>;
close(FILE);
open(FILE, $uqfile);
@uqlist = <FILE>;
close(FILE);
open(FILE, $sourceurlfile);
@source_urllist = <FILE>;
close(FILE);

$filtersettings{'ENABLE_CUSTOM_BLACKLIST'} = 'off';
$filtersettings{'ENABLE_CUSTOM_WHITELIST'} = 'off';
$filtersettings{'ENABLE_CUSTOM_EXPRESSIONS'} = 'off';
$filtersettings{'BLOCK_EXECUTABLES'} = 'off';
$filtersettings{'BLOCK_AUDIO-VIDEO'} = 'off';
$filtersettings{'BLOCK_ARCHIVES'} = 'off';
$filtersettings{'ENABLE_REWRITE'} = 'off';
$filtersettings{'UNFILTERED_CLIENTS'} = '';
$filtersettings{'BANNED_CLIENTS'} = '';
$filtersettings{'SHOW_CATEGORY'} = 'off';
$filtersettings{'SHOW_URL'} = 'off';
$filtersettings{'SHOW_IP'} = 'off';
$filtersettings{'ENABLE_DNSERROR'} = 'off';
$filtersettings{'ENABLE_JPEG'} = 'off';
$filtersettings{'REDIRECT_PAGE'} = '';
$filtersettings{'MSG_TEXT_1'} = '';
$filtersettings{'MSG_TEXT_2'} = '';
$filtersettings{'MSG_TEXT_3'} = '';
$filtersettings{'ENABLE_EXPR_LISTS'} = 'off';
$filtersettings{'BLOCK_IP_ADDR'} = 'off';
$filtersettings{'BLOCK_ALL'} = 'off';
$filtersettings{'ENABLE_EMPTY_ADS'} = 'off';
$filtersettings{'ENABLE_GLOBAL_WHITELIST'} = 'off';
$filtersettings{'ENABLE_SAFESEARCH'} = 'off';
$filtersettings{'ENABLE_LOG'} = 'off';
$filtersettings{'ENABLE_USERNAME_LOG'} = 'off';
$filtersettings{'ENABLE_CATEGORY_LOG'} = 'off';
$filtersettings{'ENABLE_AUTOUPDATE'} = 'off';
$filtersettings{'REDIRECT_TEMPLATE'} = 'legacy';

$filtersettings{'ACTION'} = '';
$filtersettings{'VALID'} = '';

&Header::getcgihash(\%filtersettings);
&Header::getcgihash(\%tcsettings);
&Header::getcgihash(\%uqsettings);
&Header::getcgihash(\%besettings);

if (($filtersettings{'ACTION'} eq $Lang::tr{'save'}) ||
    ($filtersettings{'ACTION'} eq $Lang::tr{'urlfilter save and restart'}) ||
    ($filtersettings{'ACTION'} eq $Lang::tr{'urlfilter upload file'}) ||
    ($filtersettings{'ACTION'} eq $Lang::tr{'urlfilter remove file'}) ||
    ($filtersettings{'ACTION'} eq $Lang::tr{'urlfilter upload blacklist'}) ||
    ($filtersettings{'ACTION'} eq $Lang::tr{'urlfilter backup'}) ||
    ($filtersettings{'ACTION'} eq $Lang::tr{'urlfilter restore'}))
{

	@clients = split(/\n/,$filtersettings{'UNFILTERED_CLIENTS'});
	foreach (@clients)
	{
		s/^\s+//g; s/\s+$//g; s/\s+-\s+/-/g; s/\s+/ /g; s/\n//g;
		if (/.*-.*-.*/) { $errormessage = $Lang::tr{'urlfilter invalid ip or mask error'}; }
		@temp = split(/-/);
		foreach (@temp) { unless ((&General::validipormask($_)) || (&General::validipandmask($_))) { $errormessage = $Lang::tr{'urlfilter invalid ip or mask error'}; } }
	}
	@clients = split(/\n/,$filtersettings{'BANNED_CLIENTS'});
	foreach (@clients)
	{
		s/^\s+//g; s/\s+$//g; s/\s+-\s+/-/g; s/\s+/ /g; s/\n//g;
		if (/.*-.*-.*/) { $errormessage = $Lang::tr{'urlfilter invalid ip or mask error'}; }
		@temp = split(/-/);
		foreach (@temp) { unless ((&General::validipormask($_)) || (&General::validipandmask($_))) { $errormessage = $Lang::tr{'urlfilter invalid ip or mask error'}; } }
	}
	if ($errormessage) { goto ERROR; }

	if ((!($filtersettings{'REDIRECT_PAGE'} eq '')) && (!($filtersettings{'REDIRECT_PAGE'} =~ /^https?:\/\//)))
	{
		$filtersettings{'REDIRECT_PAGE'} = "http://".$filtersettings{'REDIRECT_PAGE'};
	}

	if ($filtersettings{'ACTION'} eq $Lang::tr{'urlfilter remove file'})
	{
		if (-e "$repository/$filtersettings{'ID'}") { unlink("$repository/$filtersettings{'ID'}"); }
		$filtersettings{'ACTION'} = $Lang::tr{'urlfilter manage repository'};
	}

	if ($filtersettings{'ACTION'} eq $Lang::tr{'urlfilter upload file'})
	{
		&Header::getcgihash(\%filtersettings, {'wantfile' => 1, 'filevar' => 'UPLOADFILE'});

		$filtersettings{'ACTION'} = $Lang::tr{'urlfilter manage repository'};
		$_ = $filtersettings{'UPLOADFILE'};
		tr/\\/\//;
		$_ = substr($_,rindex($_,"/")+1);
		if ($_) {
			if (copy($filtersettings{'UPLOADFILE'}, "$repository/$_") != 1)
			{
				$errormessage = $!;
				goto ERROR;
			}
		}

	}

	if ($filtersettings{'ACTION'} eq $Lang::tr{'urlfilter upload blacklist'})
	{
		&Header::getcgihash(\%filtersettings, {'wantfile' => 1, 'filevar' => 'UPDATEFILE'});

		if (!($filtersettings{'UPDATEFILE'} =~ /.tar.gz$/))
		{
			$errormessage = $Lang::tr{'urlfilter wrong filetype'};
			goto ERROR;
		}

		if (copy($filtersettings{'UPDATEFILE'}, "${General::swroot}/urlfilter/blacklists.tar.gz") != 1)
		{
			$errormessage = $!;
			goto ERROR;
		}

		if (!(-d "${General::swroot}/urlfilter/update")) { mkdir("${General::swroot}/urlfilter/update"); }

		my $exitcode = system("/bin/tar --no-same-owner -xzf ${General::swroot}/urlfilter/blacklists.tar.gz -C ${General::swroot}/urlfilter/update");

		if ($exitcode > 0)
		{
			$errormessage = $Lang::tr{'urlfilter tar error'};
		} else {

			if (-d "${General::swroot}/urlfilter/update/BL")
			{
				system("mv ${General::swroot}/urlfilter/update/BL ${General::swroot}/urlfilter/update/blacklists");
			}

			if (-d "${General::swroot}/urlfilter/update/category")
			{
				system("mv ${General::swroot}/urlfilter/update/category ${General::swroot}/urlfilter/update/blacklists");
			}

			if (!(-d "${General::swroot}/urlfilter/update/blacklists"))
			{
				$errormessage = $Lang::tr{'urlfilter invalid content'};
			} else {
				system("cp -r ${General::swroot}/urlfilter/update/blacklists/* $dbdir");

				&readblockcategories;
				&readcustomlists;

				&writeconfigfile;

				$updatemessage = $Lang::tr{'urlfilter upload success'};
				system("${General::swroot}/urlfilter/bin/prebuild.pl &");
				system("logger -t installpackage[urlfilter] \"URL filter blacklist - Blacklist update from local source completed\"");
			}
		}
		if (-d "${General::swroot}/urlfilter/update") { system("rm -rf ${General::swroot}/urlfilter/update"); }
		if (-e "${General::swroot}/urlfilter/blacklists.tar.gz") { unlink("${General::swroot}/urlfilter/blacklists.tar.gz"); }
		if ($errormessage) { goto ERROR; }
	}

	if ($filtersettings{'ACTION'} eq $Lang::tr{'urlfilter backup'})
	{
		$blistbackup = ($filtersettings{'ENABLE_FULLBACKUP'} eq 'on') ? "blacklists" : "blacklists/custom";
		if (system("/bin/tar -C ${General::swroot}/urlfilter -czf ${General::swroot}/urlfilter/backup.tar.gz settings timeconst userquota autoupdate $blistbackup"))
		{
			$errormessage = $Lang::tr{'urlfilter backup error'};
			goto ERROR;
		}
		else
		{
			print "Content-type: application/gzip\n";
			print "Content-length: ";
			print (-s "${General::swroot}/urlfilter/backup.tar.gz");
			print "\n";
			print "Content-disposition: attachment; filename=urlfilter-backup.tar.gz\n\n";

			open (FILE, "${General::swroot}/urlfilter/backup.tar.gz");
			while (<FILE>) { print; }
			close (FILE);

			if (-e "${General::swroot}/urlfilter/backup.tar.gz") { unlink("${General::swroot}/urlfilter/backup.tar.gz"); }
			exit;
		}
	}

	if ($filtersettings{'ACTION'} eq $Lang::tr{'urlfilter restore'})
	{
		&Header::getcgihash(\%filtersettings, {'wantfile' => 1, 'filevar' => 'UPDATEFILE'});

		if (!($filtersettings{'UPDATEFILE'} =~ /.tar.gz$/))
		{
			$errormessage = $Lang::tr{'urlfilter wrong filetype'};
			goto ERROR;
		}

		if (!(-d "${General::swroot}/urlfilter/restore")) { mkdir("${General::swroot}/urlfilter/restore"); }

		if (copy($filtersettings{'UPDATEFILE'}, "${General::swroot}/urlfilter/backup.tar.gz") != 1)
		{
			$errormessage = $!;
		}

		my $exitcode = system("/bin/tar --no-same-owner --preserve-permissions -xzf ${General::swroot}/urlfilter/backup.tar.gz -C ${General::swroot}/urlfilter/restore");
		if ($exitcode > 0)
		{
			$errormessage = $Lang::tr{'urlfilter tar error'};
		} else {
			if (!(-e "${General::swroot}/urlfilter/restore/settings"))
			{
				$errormessage = $Lang::tr{'urlfilter invalid restore file'};
			} else {
				system("cp -rp ${General::swroot}/urlfilter/restore/* ${General::swroot}/urlfilter/");
				&readblockcategories;
				&readcustomlists;
				&writeconfigfile;

				$restoremessage = $Lang::tr{'urlfilter restore success'};
			}
		}

		if (-e "${General::swroot}/urlfilter/backup.tar.gz") { unlink("${General::swroot}/urlfilter/backup.tar.gz"); }
		if (-d "${General::swroot}/urlfilter/restore") { system("rm -rf ${General::swroot}/urlfilter/restore"); }
		if ($errormessage) { goto ERROR; }
	}

	if ($filtersettings{'ACTION'} eq $Lang::tr{'save'})
	{
              	$filtersettings{'VALID'} = 'yes';
		&savesettings;
	}

	if ($filtersettings{'ACTION'} eq $Lang::tr{'urlfilter save and restart'})
	{
		if ((!(-e "${General::swroot}/proxy/enable")) && (!(-e "${General::swroot}/proxy/enable_blue")))
		{
			$errormessage = $Lang::tr{'urlfilter web proxy service required'};
			goto ERROR;
		}
		if (!($proxysettings{'ENABLE_FILTER'} eq 'on'))
		{
			$errormessage = $Lang::tr{'urlfilter not enabled'};
			goto ERROR;
		}

              	$filtersettings{'VALID'} = 'yes';
		&savesettings;

		system('/usr/local/bin/squidctrl restart >/dev/null 2>&1');
	}
}

if ($tcsettings{'ACTION'} eq $Lang::tr{'urlfilter set time constraints'}) { $tcsettings{'TCMODE'} = 'on'}

if (($tcsettings{'MODE'} eq 'TIMECONSTRAINT') && ($tcsettings{'ACTION'} eq $Lang::tr{'add'}))
{
	$tcsettings{'TCMODE'}='on';

	if (!$tcsettings{'DST'})
	{
		$errormessage=$Lang::tr{'urlfilter dst error'};
	}

	if (!$tcsettings{'SRC'})
	{
		$errormessage=$Lang::tr{'urlfilter src error'};
	}

	if (!($tcsettings{'TO_HOUR'}.$tcsettings{'TO_MINUTE'} gt $tcsettings{'FROM_HOUR'}.$tcsettings{'FROM_MINUTE'}))
	{
		$errormessage=$Lang::tr{'urlfilter timespace error'};
	}

	if (!(($tcsettings{'MON'} eq 'on') || ($tcsettings{'TUE'} eq 'on') || ($tcsettings{'WED'} eq 'on') || ($tcsettings{'THU'} eq 'on') || ($tcsettings{'FRI'} eq 'on') || ($tcsettings{'SAT'} eq 'on') || ($tcsettings{'SUN'} eq 'on')))
	{
		$errormessage=$Lang::tr{'urlfilter weekday error'};
	}

	if (!$errormessage)
	{
		# transform to pre1.8 client definitions
		@clients = split(/\n/,$tcsettings{'SRC'});
		undef $tcsettings{'SRC'};
		foreach(@clients)
		{
			s/^\s+//g; s/\s+$//g; s/\s+-\s+/-/g; s/\s+/ /g; s/\n//g;
			$tcsettings{'SRC'} .= "$_ ";
		}
		$tcsettings{'SRC'} =~ s/\s+$//;

		if ($tcsettings{'DST'} =~ /^any/) { $tcsettings{'DST'} = 'any'; }
		if ($tcsettings{'ENABLERULE'} eq 'on') { $tcsettings{'ACTIVE'} = $tcsettings{'ENABLERULE'}; } else { $tcsettings{'ACTIVE'} = 'off'}

		$tcsettings{'ENABLERULE'} = 'on';
		if($tcsettings{'EDITING'} eq 'no') {
			open(FILE,">>$tcfile");
			flock FILE, 2;
			print FILE "$tcsettings{'DEFINITION'},$tcsettings{'MON'},$tcsettings{'TUE'},$tcsettings{'WED'},$tcsettings{'THU'},$tcsettings{'FRI'},$tcsettings{'SAT'},$tcsettings{'SUN'},$tcsettings{'FROM_HOUR'},$tcsettings{'FROM_MINUTE'},$tcsettings{'TO_HOUR'},$tcsettings{'TO_MINUTE'},$tcsettings{'SRC'},$tcsettings{'DST'},$tcsettings{'ACCESS'},$tcsettings{'ACTIVE'},$tcsettings{'COMMENT'}\n";
		} else {
			open(FILE, ">$tcfile");
			flock FILE, 2;
			$id = 0;
			foreach $line (@tclist)
			{
				$id++;
				if ($tcsettings{'EDITING'} eq $id) {
					print FILE "$tcsettings{'DEFINITION'},$tcsettings{'MON'},$tcsettings{'TUE'},$tcsettings{'WED'},$tcsettings{'THU'},$tcsettings{'FRI'},$tcsettings{'SAT'},$tcsettings{'SUN'},$tcsettings{'FROM_HOUR'},$tcsettings{'FROM_MINUTE'},$tcsettings{'TO_HOUR'},$tcsettings{'TO_MINUTE'},$tcsettings{'SRC'},$tcsettings{'DST'},$tcsettings{'ACCESS'},$tcsettings{'ACTIVE'},$tcsettings{'COMMENT'}\n";
				} else { print FILE "$line"; }
			}
		}
		close(FILE);
		undef %tcsettings;
		$tcsettings{'CHANGED'}='yes';
		$tcsettings{'TCMODE'}='on';
		$changed = 'yes';
	} else {
		if ($tcsettings{'EDITING'} ne 'no')
		{
			$tcsettings{'ACTION'} = $Lang::tr{'edit'};
			$tcsettings{'ID'} = $tcsettings{'EDITING'};
		}
	}
}

if (($tcsettings{'MODE'} eq 'TIMECONSTRAINT') && ($tcsettings{'ACTION'} eq $Lang::tr{'urlfilter copy rule'}) && (!$errormessage))
{
	$id = 0;
	foreach $line (@tclist)
	{
		$id++;
		if ($tcsettings{'ID'} eq $id)
		{
			chomp($line);
			@temp = split(/\,/,$line);
			$tcsettings{'DEFINITION'} = $temp[0];
			$tcsettings{'MON'} = $temp[1];
			$tcsettings{'TUE'} = $temp[2];
			$tcsettings{'WED'} = $temp[3];
			$tcsettings{'THU'} = $temp[4];
			$tcsettings{'FRI'} = $temp[5];
			$tcsettings{'SAT'} = $temp[6];
			$tcsettings{'SUN'} = $temp[7];
			$tcsettings{'FROM_HOUR'} = $temp[8];
			$tcsettings{'FROM_MINUTE'} = $temp[9];
			$tcsettings{'TO_HOUR'} = $temp[10];
			$tcsettings{'TO_MINUTE'} = $temp[11];
			$tcsettings{'SRC'} = $temp[12];
			$tcsettings{'DST'} = $temp[13];
			$tcsettings{'ACCESS'} = $temp[14];
			$tcsettings{'ENABLERULE'} = $temp[15];
			$tcsettings{'COMMENT'} = $temp[16];
		}
	}
	$tcsettings{'TCMODE'}='on';
}

if (($tcsettings{'MODE'} eq 'TIMECONSTRAINT') && ($tcsettings{'ACTION'} eq $Lang::tr{'remove'}))
{
	$id = 0;
	open(FILE, ">$tcfile");
	flock FILE, 2;
	foreach $line (@tclist)
	{
		$id++;
		unless ($tcsettings{'ID'} eq $id) { print FILE "$line"; }
	}
	close(FILE);
	$tcsettings{'CHANGED'}='yes';
	$tcsettings{'TCMODE'}='on';
}

if (($tcsettings{'MODE'} eq 'TIMECONSTRAINT') && ($tcsettings{'ACTION'} eq $Lang::tr{'urlfilter restart'}))
{
	if (!($proxysettings{'ENABLE_FILTER'} eq 'on'))
	{
		$errormessage = $Lang::tr{'urlfilter not enabled'};
	}
	if ((!(-e "${General::swroot}/proxy/enable")) && (!(-e "${General::swroot}/proxy/enable_blue")))
	{
		$errormessage = $Lang::tr{'urlfilter web proxy service required'};
	}

	if (!$errormessage) { system('/usr/local/bin/squidctrl restart >/dev/null 2>&1'); }
	$tcsettings{'TCMODE'}='on';
}

if (($tcsettings{'MODE'} eq 'TIMECONSTRAINT') && ($tcsettings{'ACTION'} eq $Lang::tr{'toggle enable disable'}))
{
	open(FILE, ">$tcfile");
	flock FILE, 2;
	$id = 0;
	foreach $line (@tclist)
	{
		$id++;
		unless ($tcsettings{'ID'} eq $id) { print FILE "$line"; }
		else
		{
			chomp($line);
			@temp = split(/\,/,$line);
			if ($temp[15] eq 'on') { $temp[15] = 'off'; } else { $temp[15] = 'on' }
			print FILE "$temp[0],$temp[1],$temp[2],$temp[3],$temp[4],$temp[5],$temp[6],$temp[7],$temp[8],$temp[9],$temp[10],$temp[11],$temp[12],$temp[13],$temp[14],$temp[15],$temp[16]\n";
		}
	}
	close(FILE);
	$tcsettings{'CHANGED'}='yes';
	$tcsettings{'TCMODE'}='on';
}

if (($tcsettings{'MODE'} eq 'TIMECONSTRAINT') && ($tcsettings{'ACTION'} eq $Lang::tr{'edit'}) && (!$errormessage))
{
	$id = 0;
	foreach $line (@tclist)
	{
		$id++;
		if ($tcsettings{'ID'} eq $id)
		{
			chomp($line);
			@temp = split(/\,/,$line);
			$tcsettings{'DEFINITION'} = $temp[0];
			$tcsettings{'MON'} = $temp[1];
			$tcsettings{'TUE'} = $temp[2];
			$tcsettings{'WED'} = $temp[3];
			$tcsettings{'THU'} = $temp[4];
			$tcsettings{'FRI'} = $temp[5];
			$tcsettings{'SAT'} = $temp[6];
			$tcsettings{'SUN'} = $temp[7];
			$tcsettings{'FROM_HOUR'} = $temp[8];
			$tcsettings{'FROM_MINUTE'} = $temp[9];
			$tcsettings{'TO_HOUR'} = $temp[10];
			$tcsettings{'TO_MINUTE'} = $temp[11];
			$tcsettings{'SRC'} = $temp[12];
			$tcsettings{'DST'} = $temp[13];
			$tcsettings{'ACCESS'} = $temp[14];
			$tcsettings{'ENABLERULE'} = $temp[15];
			$tcsettings{'COMMENT'} = $temp[16];
		}
	}
	$tcsettings{'TCMODE'}='on';
}

if ((!$errormessage) && (!($tcsettings{'ACTION'} eq $Lang::tr{'urlfilter copy rule'})) && (!($tcsettings{'ACTION'} eq $Lang::tr{'edit'}))) {
	$tcsettings{'ENABLERULE'}='on';
	$tcsettings{'TO_HOUR'}='24';
}

if ($uqsettings{'ACTION'} eq $Lang::tr{'urlfilter set user quota'}) { $uqsettings{'UQMODE'} = 'on'}

if (($uqsettings{'MODE'} eq 'USERQUOTA') && ($uqsettings{'ACTION'} eq $Lang::tr{'add'}))
{
	$uqsettings{'UQMODE'}='on';

	if ((!($uqsettings{'TIME_QUOTA'} =~ /^\d+/)) || ($uqsettings{'TIME_QUOTA'} < '1'))
	{
		$errormessage=$Lang::tr{'urlfilter quota time error'};
	}

	@temp = split(/\n/,$uqsettings{'QUOTA_USERS'});
	undef $uqsettings{'QUOTA_USERS'};
	foreach (@temp)
	{
		s/^\s+//g; s/\s+$//g;
		if ($_) { $uqsettings{'QUOTA_USERS'} .= $_."\n"; }
	}

	if ($uqsettings{'QUOTA_USERS'} eq '')
	{
		$errormessage=$Lang::tr{'urlfilter quota user error'};
	}

	$_  = $uqsettings{'QUOTA_USERS'};
	chomp; s/\n/|/g;
	my $quota_users = $_;

	if ($uqsettings{'QUOTA_USERS'} =~ /\\/)
	{
		$errormessage=$Lang::tr{'urlfilter invalid user error'};
	}

	if (!$errormessage) {
		if ($uqsettings{'ENABLEQUOTA'} eq 'on') { $uqsettings{'ACTIVE'} = $uqsettings{'ENABLEQUOTA'}; } else { $uqsettings{'ACTIVE'} = 'off'}

		$uqsettings{'ENABLERULE'} = 'on';
		if($uqsettings{'EDITING'} eq 'no') {
			open(FILE,">>$uqfile");
			flock FILE, 2;
			print FILE "$uqsettings{'TIME_QUOTA'},$uqsettings{'SPORADIC'},$uqsettings{'RENEWAL'},$quota_users,$uqsettings{'ACTIVE'}\n";
		} else {
			open(FILE, ">$uqfile");
			flock FILE, 2;
			$id = 0;
			foreach $line (@uqlist)
			{
				$id++;
				if ($uqsettings{'EDITING'} eq $id) {
					print FILE "$uqsettings{'TIME_QUOTA'},$uqsettings{'SPORADIC'},$uqsettings{'RENEWAL'},$quota_users,$uqsettings{'ACTIVE'}\n";
				} else { print FILE "$line"; }
			}
		}
		close(FILE);
		undef %uqsettings;
		$uqsettings{'CHANGED'}='yes';
		$uqsettings{'MODE'}='USERQUOTA';
		$uqsettings{'UQMODE'}='on';
		$changed = 'yes';
	} else {
		if ($uqsettings{'EDITING'} ne 'no')
		{
			$uqsettings{'ACTION'} = $Lang::tr{'edit'};
			$uqsettings{'ID'} = $uqsettings{'EDITING'};
		}
	}
}

if (($uqsettings{'MODE'} eq 'USERQUOTA') && ($uqsettings{'ACTION'} eq $Lang::tr{'remove'}))
{
	$id = 0;
	open(FILE, ">$uqfile");
	flock FILE, 2;
	foreach $line (@uqlist)
	{
		$id++;
		unless ($uqsettings{'ID'} eq $id) { print FILE "$line"; }
	}
	close(FILE);
	$uqsettings{'CHANGED'}='yes';
	$uqsettings{'UQMODE'}='on';
}

if (!$errormessage) {
	$uqsettings{'ENABLEQUOTA'}='on';
}

if (($uqsettings{'MODE'} eq 'USERQUOTA') && ($uqsettings{'ACTION'} eq $Lang::tr{'edit'}) && (!$errormessage))
{
	$id = 0;
	foreach $line (@uqlist)
	{
		$id++;
		if ($uqsettings{'ID'} eq $id)
		{
			chomp($line);
			@temp = split(/\,/,$line);
			$uqsettings{'TIME_QUOTA'} = $temp[0];
			$uqsettings{'SPORADIC'} = $temp[1];
			$uqsettings{'RENEWAL'} = $temp[2];
			$uqsettings{'QUOTA_USERS'} = $temp[3];
			$uqsettings{'ENABLEQUOTA'} = $temp[4];
		}
	}
	$uqsettings{'UQMODE'}='on';
}

if (($uqsettings{'MODE'} eq 'USERQUOTA') && ($uqsettings{'ACTION'} eq $Lang::tr{'toggle enable disable'}))
{
	open(FILE, ">$uqfile");
	flock FILE, 2;
	$id = 0;
	foreach $line (@uqlist)
	{
		$id++;
		unless ($uqsettings{'ID'} eq $id) { print FILE "$line"; }
		else
		{
			chomp($line);
			@temp = split(/\,/,$line);
			if ($temp[4] eq 'on') { $temp[4] = 'off'; } else { $temp[4] = 'on' }
			print FILE "$temp[0],$temp[1],$temp[2],$temp[3],$temp[4]\n";
		}
	}
	close(FILE);
	$uqsettings{'CHANGED'}='yes';
	$uqsettings{'UQMODE'}='on';
}

if (($uqsettings{'MODE'} eq 'USERQUOTA') && ($uqsettings{'ACTION'} eq $Lang::tr{'urlfilter restart'}))
{
	if (!($proxysettings{'ENABLE_FILTER'} eq 'on'))
	{
		$errormessage = $Lang::tr{'urlfilter not enabled'};
	}
	if ((!(-e "${General::swroot}/proxy/enable")) && (!(-e "${General::swroot}/proxy/enable_blue")))
	{
		$errormessage = $Lang::tr{'urlfilter web proxy service required'};
	}

	if (!$errormessage) { system('/usr/local/bin/squidctrl restart >/dev/null 2>&1'); }
	$uqsettings{'UQMODE'}='on';
}

if ($besettings{'ACTION'} eq $Lang::tr{'urlfilter blacklist editor'}) { $besettings{'BEMODE'} = 'on'; }

if ($besettings{'MODE'} eq 'BLACKLIST_EDITOR')
{
	@temp = split(/\n/,$besettings{'BE_DOMAINS'});
        undef $besettings{'BE_DOMAINS'};
        foreach (@temp)
        {
                s/^\s+//g; s/\s+$//g;
                if ($_) { $besettings{'BE_DOMAINS'} .= $_."\n"; }
        }
	chomp($besettings{'BE_DOMAINS'});
	@temp = split(/\n/,$besettings{'BE_URLS'});
        undef $besettings{'BE_URLS'};
        foreach (@temp)
        {
                s/^\s+//g; s/\s+$//g;
                if ($_) { $besettings{'BE_URLS'} .= $_."\n"; }
        }
	chomp($besettings{'BE_URLS'});
	@temp = split(/\n/,$besettings{'BE_EXPRESSIONS'});
        undef $besettings{'BE_EXPRESSIONS'};
        foreach (@temp)
        {
                s/^\s+//g; s/\s+$//g;
                if ($_) { $besettings{'BE_EXPRESSIONS'} .= $_."\n"; }
        }
	chomp($besettings{'BE_EXPRESSIONS'});
}

if (($besettings{'ACTION'} eq $Lang::tr{'urlfilter load blacklist'}) && ($besettings{'MODE'} = 'BLACKLIST_EDITOR'))
{
	$besettings{'BEMODE'} = 'on';

	$besettings{'BE_NAME'} = $besettings{'BE_BLACKLIST'};

	delete $besettings{'BE_DOMAINS'};
	delete $besettings{'BE_URLS'};
	delete $besettings{'BE_EXPRESSIONS'};

	if (-e "$dbdir/$besettings{'BE_NAME'}/domains")
	{
		open(FILE, "$dbdir/$besettings{'BE_NAME'}/domains");
		while (<FILE>) { unless ($_ eq '\n') { $besettings{'BE_DOMAINS'} .= $_ } };
		close FILE;
		chomp($besettings{'BE_DOMAINS'});
	}
	if (-e "$dbdir/$besettings{'BE_NAME'}/urls")
	{
		open(FILE, "$dbdir/$besettings{'BE_NAME'}/urls");
		while (<FILE>) { unless ($_ eq '\n') { $besettings{'BE_URLS'} .= $_ } };
		close FILE;
		chomp($besettings{'BE_URLS'});
	}
	if (-e "$dbdir/$besettings{'BE_NAME'}/expressions")
	{
		open(FILE, "$dbdir/$besettings{'BE_NAME'}/expressions");
		while (<FILE>) { unless ($_ eq '\n') { $besettings{'BE_EXPRESSIONS'} .= $_ } };
		close FILE;
		chomp($besettings{'BE_EXPRESSIONS'});
	}
}

if (($besettings{'ACTION'} eq $Lang::tr{'urlfilter import blacklist'}) && ($besettings{'MODE'} = 'BLACKLIST_EDITOR'))
{
	$besettings{'BEMODE'} = 'on';

	&Header::getcgihash(\%besettings, {'wantfile' => 1, 'filevar' => 'IMPORTFILE'});

	if (!($besettings{'IMPORTFILE'} =~ /.tar.gz$/))
	{
		$errormessage = $Lang::tr{'urlfilter wrong filetype'};
	} else {
		if (!-d "$editdir") { mkdir("$editdir"); }

		if (copy($besettings{'IMPORTFILE'}, "$editdir/blacklist.tar.gz") != 1)
		{
			$errormessage = $!;
		} else {

			my $exitcode = system("/bin/tar --no-same-owner --preserve-permissions -xzf $editdir/blacklist.tar.gz -C $editdir");
			if ($exitcode > 0)
			{
				$errormessage = $Lang::tr{'urlfilter tar error'};
			} else {
				$i = 0;
				foreach (<$editdir/blacklists/*>)
				{
					if (-d)
					{
						$i++;
						$besettings{'BE_NAME'} = substr($_, rindex($_,"/")+1);
					}
				}

				if (!($i == 1))
				{
					$errormessage = $Lang::tr{'urlfilter invalid import file'};
				} else {
					delete $besettings{'BE_DOMAINS'};
					delete $besettings{'BE_URLS'};
					delete $besettings{'BE_EXPRESSIONS'};

					if (-e "$editdir/blacklists/$besettings{'BE_NAME'}/domains")
					{
						open(FILE, "$editdir/blacklists/$besettings{'BE_NAME'}/domains");
						while (<FILE>) { unless ($_ eq '\n') { $besettings{'BE_DOMAINS'} .= $_ } };
						close FILE;
						chomp($besettings{'BE_DOMAINS'});
					}
					if (-e "$editdir/blacklists/$besettings{'BE_NAME'}/urls")
					{
						open(FILE, "$editdir/blacklists/$besettings{'BE_NAME'}/urls");
						while (<FILE>) { unless ($_ eq '\n') { $besettings{'BE_URLS'} .= $_ } };
						close FILE;
						chomp($besettings{'BE_URLS'});
					}
					if (-e "$editdir/blacklists/$besettings{'BE_NAME'}/expressions")
					{
						open(FILE, "$editdir/blacklists/$besettings{'BE_NAME'}/expressions");
						while (<FILE>) { unless ($_ eq '\n') { $besettings{'BE_EXPRESSIONS'} .= $_ } };
						close FILE;
						chomp($besettings{'BE_EXPRESSIONS'});
					}
				}
			}

		if (-d $editdir) { system("rm -rf $editdir"); }

		}
	}
}

if (($besettings{'ACTION'} eq $Lang::tr{'urlfilter export blacklist'}) && ($besettings{'MODE'} = 'BLACKLIST_EDITOR'))
{
	$besettings{'BEMODE'} = 'on';

	if ($besettings{'BE_NAME'} eq '')
	{
		$errormessage = $Lang::tr{'urlfilter category name error'};
	} elsif ($besettings{'BE_DOMAINS'} || $besettings{'BE_URLS'} || $besettings{'BE_EXPRESSIONS'}) {

		$_ = $besettings{'BE_NAME'}; tr/A-Z/a-z/; $besettings{'BE_NAME'} = $_;

		if (!(-d "$editdir")) { mkdir("$editdir"); }
		if (!(-d "$editdir/blacklists")) { mkdir("$editdir/blacklists"); }
		if (!(-d "$editdir/blacklists/$besettings{'BE_NAME'}")) { mkdir("$editdir/blacklists/$besettings{'BE_NAME'}"); }

		open(FILE, ">$editdir/blacklists/$besettings{'BE_NAME'}/domains");
		flock FILE, 2;
		print FILE "$besettings{'BE_DOMAINS'}\n";
		close FILE;
		open(FILE, ">$editdir/blacklists/$besettings{'BE_NAME'}/urls");
		flock FILE, 2;
		print FILE "$besettings{'BE_URLS'}\n";
		close FILE;
		open(FILE, ">$editdir/blacklists/$besettings{'BE_NAME'}/expressions");
		flock FILE, 2;
		print FILE "$besettings{'BE_EXPRESSIONS'}\n";
		close FILE;

		if (system("/bin/tar -C $editdir -czf $editdir/$besettings{'BE_NAME'}.tar.gz blacklists"))
		{
			$errormessage = $Lang::tr{'urlfilter export error'};
		}
		else
		{
			print "Content-type: application/gzip\n";
			print "Content-length: ";
			print (-s "$editdir/$besettings{'BE_NAME'}.tar.gz");
			print "\n";
			print "Content-disposition: attachment; filename=$besettings{'BE_NAME'}.tar.gz\n\n";

			open (FILE, "$editdir/$besettings{'BE_NAME'}.tar.gz");
			while (<FILE>) { print; }
			close (FILE);

			if (-d $editdir) { system("rm -rf $editdir"); }
			exit;
		}
	} else {
		$errormessage = $Lang::tr{'urlfilter category data error'};
	}
}

if (($besettings{'ACTION'} eq $Lang::tr{'urlfilter install blacklist'}) && ($besettings{'MODE'} = 'BLACKLIST_EDITOR'))
{
	$besettings{'BEMODE'} = 'on';

	if ($besettings{'BE_NAME'} eq '')
	{
		$errormessage = $Lang::tr{'urlfilter category name error'};
	} elsif ($besettings{'BE_DOMAINS'} || $besettings{'BE_URLS'} || $besettings{'BE_EXPRESSIONS'}) {

		$_ = $besettings{'BE_NAME'}; tr/A-Z/a-z/; $besettings{'BE_NAME'} = $_;

		if (!-d "$editdir") { mkdir("$editdir"); }

		if (!-d "$dbdir/$besettings{'BE_NAME'}") { mkdir("$dbdir/$besettings{'BE_NAME'}"); }

		if (-e "$dbdir/$besettings{'BE_NAME'}/domains") { unlink("$dbdir/$besettings{'BE_NAME'}/domains"); }
		if ($besettings{'BE_DOMAINS'})
		{
			open(FILE, ">$dbdir/$besettings{'BE_NAME'}/domains");
			flock FILE, 2;
			print FILE "$besettings{'BE_DOMAINS'}\n";
			close FILE;
		}
		if (-e "$dbdir/$besettings{'BE_NAME'}/urls") { unlink("$dbdir/$besettings{'BE_NAME'}/urls"); }
		if ($besettings{'BE_URLS'})
		{
			open(FILE, ">$dbdir/$besettings{'BE_NAME'}/urls");
			flock FILE, 2;
			print FILE "$besettings{'BE_URLS'}\n";
			close FILE;
		}
		if (-e "$dbdir/$besettings{'BE_NAME'}/expressions") { unlink("$dbdir/$besettings{'BE_NAME'}/expressions"); }
		if ($besettings{'BE_EXPRESSIONS'})
		{
			open(FILE, ">$dbdir/$besettings{'BE_NAME'}/expressions");
			flock FILE, 2;
			print FILE "$besettings{'BE_EXPRESSIONS'}\n";
			close FILE;
		}

		open(FILE, ">$editdir/install.conf");
		flock FILE, 2;
		print FILE "logdir /var/log/squidGuard\n";
		print FILE "dbhome $dbdir/$besettings{'BE_NAME'}\n\n";
		print FILE "dest $besettings{'BE_NAME'} {\n";
		if ($besettings{'BE_DOMAINS'})     { print FILE "    domainlist  domains\n"; }
		if ($besettings{'BE_URLS'})        { print FILE "    urllist     urls\n"; }
		if ($besettings{'BE_EXPRESSIONS'}) { print FILE "    expressions expressions\n"; }
		print FILE "}\n\n";
		print FILE "acl {\n";
		print FILE "    default {\n";
		print FILE "        pass none\n";
		print FILE "    }\n";
		print FILE "}\n";
		close FILE;

		system("rm -f $dbdir/$besettings{'BE_NAME'}/*.db");
		system("/usr/bin/squidGuard -c $editdir/install.conf -C all");
		system("chmod a+w $dbdir/$besettings{'BE_NAME'}/*.db");

		&readblockcategories;
		&readcustomlists;

		&writeconfigfile;

		system('/usr/local/bin/squidctrl restart >/dev/null 2>&1') unless ($besettings{'NORESTART'} eq 'on');

		if (-d $editdir) { system("rm -rf $editdir"); }
	} else {
		$errormessage = $Lang::tr{'urlfilter category data error'};
	}
}

if ($filtersettings{'ACTION'} eq $Lang::tr{'urlfilter save schedule'})
{
	if (($filtersettings{'UPDATE_SOURCE'} eq 'custom') && ($filtersettings{'CUSTOM_UPDATE_URL'} eq ''))
	{
		$errormessage = $Lang::tr{'urlfilter custom url required'};
	} else {
		open (FILE, ">$updconffile");
		print FILE "ENABLE_AUTOUPDATE=$filtersettings{'ENABLE_AUTOUPDATE'}\n";
		print FILE "UPDATE_SCHEDULE=$filtersettings{'UPDATE_SCHEDULE'}\n";
		print FILE "UPDATE_SOURCE=$filtersettings{'UPDATE_SOURCE'}\n";
		print FILE "CUSTOM_UPDATE_URL=$filtersettings{'CUSTOM_UPDATE_URL'}\n";
		close FILE;


		if (($filtersettings{'ENABLE_AUTOUPDATE'} eq 'on') && ($filtersettings{'UPDATE_SCHEDULE'} eq 'daily'))
		{
			system('/usr/local/bin/urlfilterctrl cron daily >/dev/null 2>&1');
		}

		if (($filtersettings{'ENABLE_AUTOUPDATE'} eq 'on') && ($filtersettings{'UPDATE_SCHEDULE'} eq 'weekly'))
		{
			system('/usr/local/bin/urlfilterctrl cron weekly >/dev/null 2>&1');
		}

		if (($filtersettings{'ENABLE_AUTOUPDATE'} eq 'on') && ($filtersettings{'UPDATE_SCHEDULE'} eq 'monthly'))
		{
			system('/usr/local/bin/urlfilterctrl cron monthly >/dev/null 2>&1');
		}
	}
}

if ($filtersettings{'ACTION'} eq $Lang::tr{'urlfilter update now'})
{
	if ($filtersettings{'UPDATE_SOURCE'} eq 'custom')
	{
		if ($filtersettings{'CUSTOM_UPDATE_URL'} eq '')
		{
			$errormessage = $Lang::tr{'urlfilter custom url required'};
		} else {
			system("${General::swroot}/urlfilter/bin/autoupdate.pl $filtersettings{'CUSTOM_UPDATE_URL'} &");
		}
	} else {
		system("${General::swroot}/urlfilter/bin/autoupdate.pl $filtersettings{'UPDATE_SOURCE'} &");
	}
}


if (-e "${General::swroot}/urlfilter/settings") { &General::readhash("${General::swroot}/urlfilter/settings", \%filtersettings); }

&readcustomlists;

ERROR:

if ($errormessage) { $filtersettings{'VALID'} = 'no'; }

$checked{'ENABLE_CUSTOM_BLACKLIST'}{'off'} = '';
$checked{'ENABLE_CUSTOM_BLACKLIST'}{'on'} = '';
$checked{'ENABLE_CUSTOM_BLACKLIST'}{$filtersettings{'ENABLE_CUSTOM_BLACKLIST'}} = "checked='checked'";
$checked{'ENABLE_CUSTOM_WHITELIST'}{'off'} = '';
$checked{'ENABLE_CUSTOM_WHITELIST'}{'on'} = '';
$checked{'ENABLE_CUSTOM_WHITELIST'}{$filtersettings{'ENABLE_CUSTOM_WHITELIST'}} = "checked='checked'";
$checked{'ENABLE_CUSTOM_EXPRESSIONS'}{'off'} = '';
$checked{'ENABLE_CUSTOM_EXPRESSIONS'}{'on'} = '';
$checked{'ENABLE_CUSTOM_EXPRESSIONS'}{$filtersettings{'ENABLE_CUSTOM_EXPRESSIONS'}} = "checked='checked'";
$checked{'BLOCK_EXECUTABLES'}{'off'} = '';
$checked{'BLOCK_EXECUTABLES'}{'on'} = '';
$checked{'BLOCK_EXECUTABLES'}{$filtersettings{'BLOCK_EXECUTABLES'}} = "checked='checked'";
$checked{'BLOCK_AUDIO-VIDEO'}{'off'} = '';
$checked{'BLOCK_AUDIO-VIDEO'}{'on'} = '';
$checked{'BLOCK_AUDIO-VIDEO'}{$filtersettings{'BLOCK_AUDIO-VIDEO'}} = "checked='checked'";
$checked{'BLOCK_ARCHIVES'}{'off'} = '';
$checked{'BLOCK_ARCHIVES'}{'on'} = '';
$checked{'BLOCK_ARCHIVES'}{$filtersettings{'BLOCK_ARCHIVES'}} = "checked='checked'";
$checked{'ENABLE_REWRITE'}{'off'} = '';
$checked{'ENABLE_REWRITE'}{'on'} = '';
$checked{'ENABLE_REWRITE'}{$filtersettings{'ENABLE_REWRITE'}} = "checked='checked'";
$checked{'SHOW_CATEGORY'}{'off'} = '';
$checked{'SHOW_CATEGORY'}{'on'} = '';
$checked{'SHOW_CATEGORY'}{$filtersettings{'SHOW_CATEGORY'}} = "checked='checked'";
$checked{'SHOW_URL'}{'off'} = '';
$checked{'SHOW_URL'}{'on'} = '';
$checked{'SHOW_URL'}{$filtersettings{'SHOW_URL'}} = "checked='checked'";
$checked{'SHOW_IP'}{'off'} = '';
$checked{'SHOW_IP'}{'on'} = '';
$checked{'SHOW_IP'}{$filtersettings{'SHOW_IP'}} = "checked='checked'";
$checked{'ENABLE_DNSERROR'}{'off'} = '';
$checked{'ENABLE_DNSERROR'}{'on'} = '';
$checked{'ENABLE_DNSERROR'}{$filtersettings{'ENABLE_DNSERROR'}} = "checked='checked'";
$checked{'ENABLE_JPEG'}{'off'} = '';
$checked{'ENABLE_JPEG'}{'on'} = '';
$checked{'ENABLE_JPEG'}{$filtersettings{'ENABLE_JPEG'}} = "checked='checked'";
$checked{'ENABLE_EXPR_LISTS'}{'off'} = '';
$checked{'ENABLE_EXPR_LISTS'}{'on'} = '';
$checked{'ENABLE_EXPR_LISTS'}{$filtersettings{'ENABLE_EXPR_LISTS'}} = "checked='checked'";
$checked{'BLOCK_IP_ADDR'}{'off'} = '';
$checked{'BLOCK_IP_ADDR'}{'on'} = '';
$checked{'BLOCK_IP_ADDR'}{$filtersettings{'BLOCK_IP_ADDR'}} = "checked='checked'";
$checked{'BLOCK_ALL'}{'off'} = '';
$checked{'BLOCK_ALL'}{'on'} = '';
$checked{'BLOCK_ALL'}{$filtersettings{'BLOCK_ALL'}} = "checked='checked'";
$checked{'ENABLE_EMPTY_ADS'}{'off'} = '';
$checked{'ENABLE_EMPTY_ADS'}{'on'} = '';
$checked{'ENABLE_EMPTY_ADS'}{$filtersettings{'ENABLE_EMPTY_ADS'}} = "checked='checked'";
$checked{'ENABLE_GLOBAL_WHITELIST'}{'off'} = '';
$checked{'ENABLE_GLOBAL_WHITELIST'}{'on'} = '';
$checked{'ENABLE_GLOBAL_WHITELIST'}{$filtersettings{'ENABLE_GLOBAL_WHITELIST'}} = "checked='checked'";
$checked{'ENABLE_SAFESEARCH'}{'off'} = '';
$checked{'ENABLE_SAFESEARCH'}{'on'} = '';
$checked{'ENABLE_SAFESEARCH'}{$filtersettings{'ENABLE_SAFESEARCH'}} = "checked='checked'";
$checked{'ENABLE_LOG'}{'off'} = '';
$checked{'ENABLE_LOG'}{'on'} = '';
$checked{'ENABLE_LOG'}{$filtersettings{'ENABLE_LOG'}} = "checked='checked'";
$checked{'ENABLE_USERNAME_LOG'}{'off'} = '';
$checked{'ENABLE_USERNAME_LOG'}{'on'} = '';
$checked{'ENABLE_USERNAME_LOG'}{$filtersettings{'ENABLE_USERNAME_LOG'}} = "checked='checked'";
$checked{'ENABLE_CATEGORY_LOG'}{'off'} = '';
$checked{'ENABLE_CATEGORY_LOG'}{'on'} = '';
$checked{'ENABLE_CATEGORY_LOG'}{$filtersettings{'ENABLE_CATEGORY_LOG'}} = "checked='checked'";

foreach $category (@filtergroups) {
	$checked{$category}{'off'} = '';
	$checked{$category}{'on'} = '';
	$checked{$category}{$filtersettings{$category}} = "checked='checked'";
}

$selected{'REDIRECT_TEMPLATE'}{$filtersettings{'REDIRECT_TEMPLATE'}} = "selected='selected'";

$selected{'DEFINITION'}{$tcsettings{'DEFINITION'}} = "selected='selected'";
$selected{'FROM_HOUR'}{$tcsettings{'FROM_HOUR'}} = "selected='selected'";
$selected{'FROM_MINUTE'}{$tcsettings{'FROM_MINUTE'}} = "selected='selected'";
$selected{'TO_HOUR'}{$tcsettings{'TO_HOUR'}} = "selected='selected'";
$selected{'TO_MINUTE'}{$tcsettings{'TO_MINUTE'}} = "selected='selected'";

@selectedcategories = split(/\|/,$tcsettings{'DST'});
foreach (@selectedcategories)
{
        $selected{'DST'}{$_} = "selected='selected'";
}

$selected{'ACCESS'}{$tcsettings{'ACCESS'}} = "selected='selected'";

$checked{'ENABLERULE'}{'off'} = '';
$checked{'ENABLERULE'}{'on'} = '';
$checked{'ENABLERULE'}{$tcsettings{'ENABLERULE'}} = "checked='checked'";
$checked{'MON'}{'off'} = '';
$checked{'MON'}{'on'} = '';
$checked{'MON'}{$tcsettings{'MON'}} = "checked='checked'";
$checked{'TUE'}{'off'} = '';
$checked{'TUE'}{'on'} = '';
$checked{'TUE'}{$tcsettings{'TUE'}} = "checked='checked'";
$checked{'WED'}{'off'} = '';
$checked{'WED'}{'on'} = '';
$checked{'WED'}{$tcsettings{'WED'}} = "checked='checked'";
$checked{'THU'}{'off'} = '';
$checked{'THU'}{'on'} = '';
$checked{'THU'}{$tcsettings{'THU'}} = "checked='checked'";
$checked{'FRI'}{'off'} = '';
$checked{'FRI'}{'on'} = '';
$checked{'FRI'}{$tcsettings{'FRI'}} = "checked='checked'";
$checked{'SAT'}{'off'} = '';
$checked{'SAT'}{'on'} = '';
$checked{'SAT'}{$tcsettings{'SAT'}} = "checked='checked'";
$checked{'SUN'}{'off'} = '';
$checked{'SUN'}{'on'} = '';
$checked{'SUN'}{$tcsettings{'SUN'}} = "checked='checked'";

$selected{'SPORADIC'}{$uqsettings{'SPORADIC'}} = "selected='selected'";
$selected{'RENEWAL'} {$uqsettings{'RENEWAL'}}  = "selected='selected'";

$checked{'ENABLEQUOTA'}{'off'} = '';
$checked{'ENABLEQUOTA'}{'on'} = '';
$checked{'ENABLEQUOTA'}{$uqsettings{'ENABLEQUOTA'}} = "checked='checked'";

$selected{'BE_BLACKLIST'}{$besettings{'BE_BLACKLIST'}} = "selected='selected'";


&Header::showhttpheaders();

&Header::openpage($Lang::tr{'urlfilter configuration'}, 1, '');

&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<font class='base'>$errormessage&nbsp;</font>\n";
	&Header::closebox();
} elsif (($tcsettings{'CHANGED'} eq 'yes') || ($uqsettings{'CHANGED'} eq 'yes') ) {
	&writeconfigfile;
	print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";
	&Header::openbox('100%', 'left', "$Lang::tr{'urlfilter restart notification'}:");
	print "<class name='base'>$Lang::tr{'urlfilter restart message'}\n";
	if ($uqsettings{'MODE'} eq 'USERQUOTA') { print "<p><class name='base'>$Lang::tr{'urlfilter quota restart message'}\n"; }
	print "</class>\n";
	print "<p><input type='submit' name='ACTION' value='$Lang::tr{'urlfilter restart'}' />";
	if ($tcsettings{'MODE'} eq 'TIMECONSTRAINT') { print "<input type='hidden' name='MODE' value='TIMECONSTRAINT' />"; }
	if ($uqsettings{'MODE'} eq 'USERQUOTA') { print "<input type='hidden' name='MODE' value='USERQUOTA' />"; }
	&Header::closebox();
	print "</form>\n";
}

if ($restoremessage) {
	&Header::openbox('100%', 'left', "$Lang::tr{'urlfilter restore results'}:");
	print "<class name='base'>$restoremessage\n";
        print "&nbsp;</class>\n";
	&Header::closebox();
}

if ((!$tcsettings{'TCMODE'}) && (!$uqsettings{'UQMODE'}) && (!$besettings{'BEMODE'})) {

if (!($filtersettings{'ACTION'} eq $Lang::tr{'urlfilter manage repository'})) {

#==========================================================
#
# Section: Main Configuration
#
#==========================================================

print "<form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>\n";

&Header::openbox('100%', 'left', "$Lang::tr{'urlfilter filter settings'}");
print <<END
<table width='100%'>
<tr>
        <td colspan='4'><b>$Lang::tr{'urlfilter block categories'}</b></td>
</tr>
END
;

if (@categories == 0) {
print <<END
<tr>
        <td><i>$Lang::tr{'urlfilter no categories'}</i></td>
        <td>&nbsp;</td>
        <td>&nbsp;</td>
        <td>&nbsp;</td>
</tr>

END
;
}

for ($n=0; $n<=@categories; $n = $n + $i) {
	for ($i=0; $i<=3; $i++) {
		if ($i eq 0) { print "<tr>\n"; }
		if (($n+$i) < @categories) {
			print "<td width='15%'>@categories[$n+$i]:<\/td>\n";
			print "<td width='10%'><input type='checkbox' name=@filtergroups[$n+$i] $checked{@filtergroups[$n+$i]}{'on'} /></td>\n";
		}
		if ($i eq 3) { print "<\/tr>\n"; }
	}
}

print <<END
</table>
<hr size='1'>
<table width='100%'>
<tr>
        <td><b>$Lang::tr{'urlfilter custom blacklist'}</b></td>
        <td>&nbsp;</td>
        <td>&nbsp;</td>
        <td>&nbsp;</td>
</tr>
<tr>
	<td colspan='2'>$Lang::tr{'urlfilter blocked domains'}</td>
	<td colspan='2'>$Lang::tr{'urlfilter blocked urls'}</td>
</tr>
<tr>
	<td colspan='2'>$Lang::tr{'urlfilter example'}</td>
	<td colspan='2'>$Lang::tr{'urlfilter example ads'}</td>
</tr>
<tr>
	<td colspan='2' width='50%'><textarea name='CUSTOM_BLACK_DOMAINS' cols='32' rows='6' wrap='off'>
END
;

print $filtersettings{'CUSTOM_BLACK_DOMAINS'};

print <<END
</textarea></td>
	<td colspan='2' width='50%'><textarea name='CUSTOM_BLACK_URLS' cols='32' rows='6' wrap='off'>
END
;

print $filtersettings{'CUSTOM_BLACK_URLS'};

print <<END
</textarea></td>
</tr>
</table>
<table width='100%'>
<tr>
        <td class='base' width='25%'>$Lang::tr{'urlfilter enable custom blacklist'}:</td>
        <td><input type='checkbox' name='ENABLE_CUSTOM_BLACKLIST' $checked{'ENABLE_CUSTOM_BLACKLIST'}{'on'} /></td>
        <td>&nbsp;</td>
        <td>&nbsp;</td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
        <td><b>$Lang::tr{'urlfilter custom whitelist'}</b></td>
        <td>&nbsp;</td>
        <td>&nbsp;</td>
        <td>&nbsp;</td>
</tr>
<tr>
	<td colspan='2'>$Lang::tr{'urlfilter allowed domains'}</td>
	<td colspan='2'>$Lang::tr{'urlfilter allowed urls'}</td>
</tr>
<tr>
	<td colspan='2'>$Lang::tr{'urlfilter example'}</td>
	<td colspan='2'>$Lang::tr{'urlfilter example ads'}</td>
</tr>
<tr>
	<td colspan='2' width='50%'><textarea name='CUSTOM_WHITE_DOMAINS' cols='32' rows='6' wrap='off'>
END
;

print $filtersettings{'CUSTOM_WHITE_DOMAINS'};

print <<END
</textarea></td>
	<td colspan='2' width='50%'><textarea name='CUSTOM_WHITE_URLS' cols='32' rows='6' wrap='off'>
END
;

print $filtersettings{'CUSTOM_WHITE_URLS'};

print <<END
</textarea></td>
</tr>
</table>
<table width='100%'>
<tr>
        <td class='base' width='25%'>$Lang::tr{'urlfilter enable custom whitelist'}:</td>
        <td><input type='checkbox' name='ENABLE_CUSTOM_WHITELIST' $checked{'ENABLE_CUSTOM_WHITELIST'}{'on'} /></td>
        <td>&nbsp;</td>
        <td>&nbsp;</td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
        <td colspan='4'><b>$Lang::tr{'urlfilter custom expression list'}</b></td>
</tr>
<tr>
	<td colspan='4'>$Lang::tr{'urlfilter blocked expressions'}</td>
</tr>
<tr>
	<td colspan='4'><textarea name='CUSTOM_EXPRESSIONS' cols='70' rows='3' wrap='off'>
END
;

print $filtersettings{'CUSTOM_EXPRESSIONS'};

print <<END
</textarea></td>
</tr>
<tr>
        <td class='base' width='25%'>$Lang::tr{'urlfilter enable custom expression list'}:</td>
        <td><input type='checkbox' name='ENABLE_CUSTOM_EXPRESSIONS' $checked{'ENABLE_CUSTOM_EXPRESSIONS'}{'on'} /></td>
        <td>&nbsp;</td>
        <td>&nbsp;</td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
        <td colspan='4'><b>$Lang::tr{'urlfilter file ext block'}</b></td>
</tr>
<tr>
        <td width='25%' class='base'>$Lang::tr{'urlfilter block executables'}:</td>
        <td width='12%'><input type='checkbox' name='BLOCK_EXECUTABLES' $checked{'BLOCK_EXECUTABLES'}{'on'} /></td>
        <td width='25%'  class='base'>$Lang::tr{'urlfilter block audio-video'}:</td>
        <td><input type='checkbox' name='BLOCK_AUDIO-VIDEO' $checked{'BLOCK_AUDIO-VIDEO'}{'on'} /></td>
</tr>
<tr>
        <td class='base'>$Lang::tr{'urlfilter block archives'}:</td>
        <td><input type='checkbox' name='BLOCK_ARCHIVES' $checked{'BLOCK_ARCHIVES'}{'on'} /></td>
        <td>&nbsp;</td>
        <td>&nbsp;</td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
        <td colspan='4'><b>$Lang::tr{'urlfilter local file redirection'}</b></td>
</tr>
<tr>
	<td width='25%' class='base'>$Lang::tr{'urlfilter enable rewrite rules'}:</td>
	<td width='12%'><input type='checkbox' name='ENABLE_REWRITE' $checked{'ENABLE_REWRITE'}{'on'} /></td>
        <td>&nbsp;</td>
        <td>&nbsp;</td>
</tr>
<tr>
	<td><input type='submit' name='ACTION' value='$Lang::tr{'urlfilter manage repository'}'></td>
        <td>&nbsp;</td>
        <td>&nbsp;</td>
        <td>&nbsp;</td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
        <td colspan='2'><b>$Lang::tr{'urlfilter network access control'}</b></td>
        <td>&nbsp;</td>
        <td>&nbsp;</td>
</tr>
<tr>
	<td colspan='2'>$Lang::tr{'urlfilter unfiltered clients'}</td>
	<td colspan='2'>$Lang::tr{'urlfilter banned clients'}</td>
</tr>
<tr>
	<td colspan='2' width='50%'><textarea name='UNFILTERED_CLIENTS' cols='32' rows='6' wrap='off'>
END
;

# transform from pre1.8 client definitions
$filtersettings{'UNFILTERED_CLIENTS'} =~ s/^\s+//g;
$filtersettings{'UNFILTERED_CLIENTS'} =~ s/\s+$//g;
$filtersettings{'UNFILTERED_CLIENTS'} =~ s/\s+-\s+/-/g;
$filtersettings{'UNFILTERED_CLIENTS'} =~ s/\s+/ /g;

@clients = split(/ /,$filtersettings{'UNFILTERED_CLIENTS'});
undef $filtersettings{'UNFILTERED_CLIENTS'};
foreach (@clients) { $filtersettings{'UNFILTERED_CLIENTS'} .= "$_\n"; }

print $filtersettings{'UNFILTERED_CLIENTS'};

print <<END
</textarea></td>
	<td colspan='2' width='50%'><textarea name='BANNED_CLIENTS' cols='32' rows='6' wrap='off'>
END
;

# transform from pre1.8 client definitions
$filtersettings{'BANNED_CLIENTS'} =~ s/^\s+//g;
$filtersettings{'BANNED_CLIENTS'} =~ s/\s+$//g;
$filtersettings{'BANNED_CLIENTS'} =~ s/\s+-\s+/-/g;
$filtersettings{'BANNED_CLIENTS'} =~ s/\s+/ /g;

@clients = split(/ /,$filtersettings{'BANNED_CLIENTS'});
undef $filtersettings{'BANNED_CLIENTS'};
foreach (@clients) { $filtersettings{'BANNED_CLIENTS'} .= "$_\n"; }

print $filtersettings{'BANNED_CLIENTS'};

print <<END
</textarea></td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
        <td colspan='4'><b>$Lang::tr{'urlfilter timebased access control'}</b></td>
</tr>
<tr>
	<td width='25%'><input type='submit' name='ACTION' value='$Lang::tr{'urlfilter set time constraints'}'></td>
	<td width='25%'><input type='submit' name='ACTION' value='$Lang::tr{'urlfilter set user quota'}'></td>
        <td>&nbsp;</td>
        <td>&nbsp;</td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
        <td colspan='4'><b>$Lang::tr{'urlfilter block settings'}</b></td>
</tr>
<tr>
	<td width='25%' class='base'>$Lang::tr{'urlfilter redirect template'}</td>
	<td width='75%' colspan='2'>
		<select name='REDIRECT_TEMPLATE'>
END
;

	foreach (<$templatedir/*>) {
		if ((-d "$_") && (-e "$_/template.html")) {
			my $template = substr($_,rindex($_,"/")+1);
			print "<option value='$template' $selected{'REDIRECT_TEMPLATE'}{$template}>$template</option>\n";
		}
	}

print <<END
		</select>
	</td>
</tr>
<tr>
	<td width='25%' class='base'>$Lang::tr{'urlfilter show category'}:</td>
	<td width='12%'><input type='checkbox' name='SHOW_CATEGORY' $checked{'SHOW_CATEGORY'}{'on'} /></td>
	<td width='25%' class='base'>$Lang::tr{'urlfilter redirectpage'}:</td>
	<td><input type='text' name='REDIRECT_PAGE' value='$filtersettings{'REDIRECT_PAGE'}' size='40' /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'urlfilter show url'}:</td>
	<td><input type='checkbox' name='SHOW_URL' $checked{'SHOW_URL'}{'on'} /></td>
	<td class='base'>$Lang::tr{'urlfilter msg text 1'}:</td>
	<td><input type='text' name='MSG_TEXT_1' value='$filtersettings{'MSG_TEXT_1'}' size='40' /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'urlfilter show ip'}:</td>
	<td><input type='checkbox' name='SHOW_IP' $checked{'SHOW_IP'}{'on'} /></td>
	<td class='base'>$Lang::tr{'urlfilter msg text 2'}:</td>
	<td><input type='text' name='MSG_TEXT_2' value='$filtersettings{'MSG_TEXT_2'}' size='40' /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'urlfilter show dnserror'}:</td>
	<td><input type='checkbox' name='ENABLE_DNSERROR' $checked{'ENABLE_DNSERROR'}{'on'} /></td>
	<td class='base'>$Lang::tr{'urlfilter msg text 3'}:</td>
	<td><input type='text' name='MSG_TEXT_3' value='$filtersettings{'MSG_TEXT_3'}' size='40' /></td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
	<td colspan='4'><b>$Lang::tr{'urlfilter advanced settings'}</b></td>
</tr>
<tr>
	<td width='25%' class='base'>$Lang::tr{'urlfilter enable expression lists'}:</td>
	<td width='12%'><input type='checkbox' name='ENABLE_EXPR_LISTS' $checked{'ENABLE_EXPR_LISTS'}{'on'} /></td>
	<td width='25%' class='base'>$Lang::tr{'urlfilter enable log'}:</td>
	<td><input type='checkbox' name='ENABLE_LOG' $checked{'ENABLE_LOG'}{'on'} /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'urlfilter safesearch'}:</td>
	<td><input type='checkbox' name='ENABLE_SAFESEARCH' $checked{'ENABLE_SAFESEARCH'}{'on'} /></td>
	<td class='base'>$Lang::tr{'urlfilter username log'}:</td>
	<td><input type='checkbox' name='ENABLE_USERNAME_LOG' $checked{'ENABLE_USERNAME_LOG'}{'on'} /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'urlfilter empty ads'}:</td>
	<td><input type='checkbox' name='ENABLE_EMPTY_ADS' $checked{'ENABLE_EMPTY_ADS'}{'on'} /></td>
	<td class='base'>$Lang::tr{'urlfilter category log'}:</td>
	<td><input type='checkbox' name='ENABLE_CATEGORY_LOG' $checked{'ENABLE_CATEGORY_LOG'}{'on'} /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'urlfilter block ip'}:</td>
	<td><input type='checkbox' name='BLOCK_IP_ADDR' $checked{'BLOCK_IP_ADDR'}{'on'} /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'urlfilter block all'}:</td>
	<td><input type='checkbox' name='BLOCK_ALL' $checked{'BLOCK_ALL'}{'on'} /></td>
	<td class='base'>$Lang::tr{'urlfilter whitelist always allowed'}:</td>
	<td><input type='checkbox' name='ENABLE_GLOBAL_WHITELIST' $checked{'ENABLE_GLOBAL_WHITELIST'}{'on'} /></td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
	<td><img src='/blob.gif' align='top' alt='*' />&nbsp;<font class='base'>$Lang::tr{'required field'}</font></td>
	<td align='right'>&nbsp;</td>
</tr>
</table>
<table width='100%'>
<tr>
<td>&nbsp;</td>
<td align='center'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
<td align='center'><input type='submit' name='ACTION' value='$Lang::tr{'urlfilter save and restart'}' /></td>
<td>&nbsp;</td>
</tr>
</table>
END
;

&Header::closebox();

print "</form>\n";

print "<form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>\n";

&Header::openbox('100%', 'left', "$Lang::tr{'urlfilter maintenance'}");

print <<END
<table width='100%'>
<tr>
<td class='base'><b>$Lang::tr{'urlfilter blacklist update'}</b></td>
</tr>
<tr>
<td>$Lang::tr{'urlfilter upload information'}<p>$Lang::tr{'urlfilter upload text'}:</td>
</tr>
<tr>
<td><input type='file' name='UPDATEFILE' size='40' /> &nbsp; <input type='submit' name='ACTION' value='$Lang::tr{'urlfilter upload blacklist'}' /></td>
</tr>
</table>

<hr size='1'>

<table width='100%'>
<tr>
	<td colspan='2' class='base'><b>$Lang::tr{'urlfilter automatic blacklist update'}</b>
END
;
if (-e "$updflagfile")
{
$blacklistage = int(-M "$updflagfile");
print "&nbsp; <b>[</b> <small><i>$Lang::tr{'urlfilter blacklist age 1'} <b>$blacklistage</b> $Lang::tr{'urlfilter blacklist age 2'}</i></small> <b>]</b>";
}

$updatesettings{'UPDATE_SCHEDULE'} = 'monthly';
$updatesettings{'CUSTOM_UPDATE_URL'} = '';

if (-e "$updconffile") { &General::readhash("$updconffile", \%updatesettings); }

$checked{'ENABLE_AUTOUPDATE'}{'off'} = '';
$checked{'ENABLE_AUTOUPDATE'}{'on'} = '';
$checked{'ENABLE_AUTOUPDATE'}{$updatesettings{'ENABLE_AUTOUPDATE'}} = "checked='checked'";

$selected{'UPDATE_SCHEDULE'}{$updatesettings{'UPDATE_SCHEDULE'}} = "selected='selected'";

$selected{'UPDATE_SOURCE'}{$updatesettings{'UPDATE_SOURCE'}} = "selected='selected'";

print <<END
	</td>
</tr>
<tr>
	<td width='25%' class='base'>$Lang::tr{'urlfilter enable automatic blacklist update'}:</td>
        <td width='75%' class='base'><input type='checkbox' name='ENABLE_AUTOUPDATE' $checked{'ENABLE_AUTOUPDATE'}{'on'} /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'urlfilter automatic update schedule'}:</td>
	<td class='base'>
	<select name='UPDATE_SCHEDULE'>
	<option value='daily' $selected{'UPDATE_SCHEDULE'}{'daily'}>$Lang::tr{'urlfilter daily'}</option>
	<option value='weekly' $selected{'UPDATE_SCHEDULE'}{'weekly'}>$Lang::tr{'urlfilter weekly'}</option>
	<option value='monthly' $selected{'UPDATE_SCHEDULE'}{'monthly'}>$Lang::tr{'urlfilter monthly'}</option>
	</select>
	</td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'urlfilter select source'}:</td>
	<td class='base' colspan='2'>
	<select name='UPDATE_SOURCE'>
END
;

foreach (@source_urllist) {
	chomp;
	$source_name = substr($_,0,rindex($_,","));
	$source_url = substr($_,index($_,",")+1);
	print "\t<option value='$source_url' $selected{'UPDATE_SOURCE'}{$source_url}>$source_name</option>\n";
}

print <<END
	<option value='custom' $selected{'UPDATE_SOURCE'}{'custom'}>$Lang::tr{'urlfilter custom url'}</option>
	</select>
	</td>
</tr>
<tr>
	<td>$Lang::tr{'urlfilter custom url'}:</td>
	<td><input type='text' name='CUSTOM_UPDATE_URL' value='$updatesettings{'CUSTOM_UPDATE_URL'}' size='72' /></td>
</tr>
</table>
<table width='100%'>
<tr>
	<td width='25%'><input type='submit' name='ACTION' value='$Lang::tr{'urlfilter save schedule'}'>&nbsp;&nbsp;&nbsp;<input type='submit' name='ACTION' value='$Lang::tr{'urlfilter update now'}'></td>
</tr>
</table>

<hr size='1'>

<table width='100%'>
<tr>
	<td class='base'><b>$Lang::tr{'urlfilter blacklist editor'}</b></td>
</tr>
<tr>
	<td>$Lang::tr{'urlfilter blacklist editor info'}</td>
</tr>
<tr>
	<td><input type='submit' name='ACTION' value='$Lang::tr{'urlfilter blacklist editor'}' /></td>
</tr>
</table>

<hr size='1'>

<table width='100%'>
<tr>
	<td colspan='4' class='base'><b>$Lang::tr{'urlfilter backup settings'}</b></td>
</tr>
<tr>
	<td width='25%' class='base'>$Lang::tr{'urlfilter enable full backup'}:</td>
        <td width='12%' class='base'><input type='checkbox' name='ENABLE_FULLBACKUP' $checked{'ENABLE_FULLBACKUP'}{'on'} /></td>
        <td>&nbsp;</td>
        <td>&nbsp;</td>
</tr>
<tr>
	<td colspan='4' class='base'><input type='submit' name='ACTION' value='$Lang::tr{'urlfilter backup'}' /></td>
</tr>
</table>

<hr size='1'>

<table width='100%'>
<tr>
	<td class='base'><b>$Lang::tr{'urlfilter restore settings'}</b></td>
</tr>
<tr>
	<td>$Lang::tr{'urlfilter restore text'}:</td>
</tr>
<tr>
	<td><input type='file' name='UPDATEFILE' size='40' /> &nbsp; <input type='submit' name='ACTION' value='$Lang::tr{'urlfilter restore'}' /></td>
</tr>
</table>
</form>
END
;

&Header::closebox();

} else {

#==========================================================
#
# Section: Manage Repository
#
#==========================================================

print "<form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>\n";

&Header::openbox('100%', 'left', "$Lang::tr{'urlfilter manage local file repository'}:");
print <<END
<table width='100%'>
<tr>
	<td>$Lang::tr{'urlfilter repository information'}<br><br></td>
</tr>
<tr>
	<td>$Lang::tr{'urlfilter upload file text'}:</td>
</tr>
<tr>
	<td><input type='file' name='UPLOADFILE' size='50' /> &nbsp; <input type='submit' name='ACTION' value='$Lang::tr{'urlfilter upload file'}' /></td>
</tr>
<tr>
	<td><br><b>$Lang::tr{'urlfilter upload file information 1'}:</b> $Lang::tr{'urlfilter upload file information 2'}</td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
	<td><input type='button' name='return2main' value='$Lang::tr{'urlfilter back to main page'}' onClick='self.location.href="$ENV{'SCRIPT_NAME'}"'></td>
</tr>
</table>
</form>
END
;

&Header::closebox();

&Header::openbox('100%', 'left', "$Lang::tr{'urlfilter current files'}: </b>[$repository]");

@repositorylist = <$repository/*>;

undef @repositoryfiles;
foreach (@repositorylist)
{
	if (!-d) { push(@repositoryfiles,substr($_,rindex($_,"/")+1));	}
}

if (@repositoryfiles)
{
	print <<END
<table width='100%'>
<tr>
	<td align='center'><b>$Lang::tr{'urlfilter filename'}</b></td>
	<td width='15%' align='center'><b>$Lang::tr{'urlfilter filesize'}</b></td>
	<td width='10%'></td>
</tr>
END
;
	$id = 0;
	foreach $line (@repositoryfiles)
	{
		$id++;
		if ($id % 2) {
			print "<tr bgcolor='$Header::table1colour'>\n"; }
		else {
			print "<tr bgcolor='$Header::table2colour'>\n"; }
		$filesize = (-s "$repository/$line");
		1 while $filesize =~ s/^(-?\d+)(\d{3})/$1.$2/;

print <<END
		<td>&nbsp; &nbsp;$line</td>
		<td align='right'>$filesize&nbsp; &nbsp;</td>

		<td align='center'>
		<form method='post' name='frma$id' action='$ENV{'SCRIPT_NAME'}'>
		<input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' title='$Lang::tr{'remove'}' alt='$Lang::tr{'remove'}' />
		<input type='hidden' name='ID' value='$line' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'urlfilter remove file'}' />
		</form>
		</td>

	</tr>
END
;
	}

print <<END
</table>
<table>
	<tr>
	</tr>
</table>
<table>
	<tr>
		<td class='boldbase'>&nbsp; <b>$Lang::tr{'legend'}:</b></td>
		<td>&nbsp; &nbsp; <img src='/images/delete.gif' alt='$Lang::tr{'remove'}' /></td>
		<td class='base'>$Lang::tr{'remove'}</td>
	</tr>
</table>
END
;
} else {

	print "<i>$Lang::tr{'urlfilter empty repository'}</i>\n";
}

&Header::closebox();

}

} elsif ($tcsettings{'TCMODE'}) {

#==========================================================
#
# Section: Set Time Constraints
#
#==========================================================

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

$buttontext = $Lang::tr{'urlfilter add rule'};
if ($tcsettings{'ACTION'} eq $Lang::tr{'edit'}) {
&Header::openbox('100%', 'left', $Lang::tr{'urlfilter edit time constraint rule'}.':');
$buttontext = $Lang::tr{'urlfilter update rule'};
} else {
&Header::openbox('100%', 'left', $Lang::tr{'urlfilter add new time constraint rule'}.':');
}
print <<END

<table width='100%'>
<tr>
	<td width='2%'>$Lang::tr{'urlfilter constraint definition'}</td>
	<td width='1%'>&nbsp;&nbsp;</td>
	<td width='2%' align='center'>$Lang::tr{'urlfilter monday'}</td>
	<td width='2%' align='center'>$Lang::tr{'urlfilter tuesday'}</td>
	<td width='2%' align='center'>$Lang::tr{'urlfilter wednesday'}</td>
	<td width='2%' align='center'>$Lang::tr{'urlfilter thursday'}</td>
	<td width='2%' align='center'>$Lang::tr{'urlfilter friday'}</td>
	<td width='2%' align='center'>$Lang::tr{'urlfilter saturday'}</td>
	<td width='2%' align='center'>$Lang::tr{'urlfilter sunday'}</td>
	<td width='1%'>&nbsp;&nbsp;</td>
	<td width='7%' colspan=3>$Lang::tr{'urlfilter from'}</td>
	<td width='1%'>&nbsp;</td>
	<td width='7%' colspan=3>$Lang::tr{'urlfilter to'}</td>
	<td>&nbsp;</td>
</tr>
<tr>
	<td class='base'>
	<select name='DEFINITION'>
	<option value='within' $selected{'DEFINITION'}{'within'}>$Lang::tr{'urlfilter constraint within'}</option>
	<option value='outside' $selected{'DEFINITION'}{'outside'}>$Lang::tr{'urlfilter constraint outside'}</option>
	</select>
	</td>
	<td>&nbsp;</td>
	<td class='base'><input type='checkbox' name='MON' $checked{'MON'}{'on'} /></td>
	<td class='base'><input type='checkbox' name='TUE' $checked{'TUE'}{'on'} /></td>
	<td class='base'><input type='checkbox' name='WED' $checked{'WED'}{'on'} /></td>
	<td class='base'><input type='checkbox' name='THU' $checked{'THU'}{'on'} /></td>
	<td class='base'><input type='checkbox' name='FRI' $checked{'FRI'}{'on'} /></td>
	<td class='base'><input type='checkbox' name='SAT' $checked{'SAT'}{'on'} /></td>
	<td class='base'><input type='checkbox' name='SUN' $checked{'SUN'}{'on'} /></td>
	<td>&nbsp;</td>
	<td class='base'>
	<select name='FROM_HOUR'>
END
;
for ($i=0;$i<=24;$i++) {
$_ = sprintf("%02s",$i);
print "<option $selected{'FROM_HOUR'}{$_}>$_</option>\n";
}
print <<END
	</select>
	</td>
	<td>:</td>
	<td class='base'>
	<select name='FROM_MINUTE'>
END
;
for ($i=0;$i<=45;$i+=15) {
$_ = sprintf("%02s",$i);
print "<option $selected{'FROM_MINUTE'}{$_}>$_</option>\n";
}
print <<END
	</select>
	<td> - </td>
	</td>
	<td class='base'>
	<select name='TO_HOUR'>
END
;
for ($i=0;$i<=24;$i++) {
$_ = sprintf("%02s",$i);
print "<option $selected{'TO_HOUR'}{$_}>$_</option>\n";
}
print <<END
	</select>
	</td>
	<td>:</td>
	<td class='base'>
	<select name='TO_MINUTE'>
END
;
for ($i=0;$i<=45;$i+=15) {
$_ = sprintf("%02s",$i);
print "<option $selected{'TO_MINUTE'}{$_}>$_</option>\n";
}
print <<END
	</select>
	</td>
	<td>&nbsp;</td>
</tr>
</table>

<br>

<table width='100%'>
	<tr>
		<td width='5%'>$Lang::tr{'urlfilter source'}&nbsp;<img src='/blob.gif' alt='*' /></td>
		<td width='1%'>&nbsp;&nbsp;</td>
		<td width='5%'>$Lang::tr{'urlfilter dst'}&nbsp;<img src='/blob.gif' alt='*' /></td>
		<td width='1%'>&nbsp;&nbsp;</td>
		<td width='5%'>$Lang::tr{'urlfilter access'}</td>
		<td>&nbsp;</td>
	</tr>
	<tr>
        <td rowspan='2'><textarea name='SRC' cols='28' rows='5' wrap='off'>
END
;

# transform from pre1.8 client definitions
$tcsettings{'SRC'} =~ s/^\s+//g;
$tcsettings{'SRC'} =~ s/\s+$//g;
$tcsettings{'SRC'} =~ s/\s+-\s+/-/g;
$tcsettings{'SRC'} =~ s/\s+/ /g;

@clients = split(/ /,$tcsettings{'SRC'});
undef $tcsettings{'SRC'};
foreach (@clients) { $tcsettings{'SRC'} .= "$_\n"; }

print $tcsettings{'SRC'};

print <<END
</textarea></td>

		<td>&nbsp;</td>
		<td class='base' rowspan='2' valign='top'>
		<select name='DST' size='6' multiple>
		<option value='any' $selected{'DST'}{'any'} = "selected='selected'">$Lang::tr{'urlfilter category all'}</option>
		<option value='in-addr' $selected{'DST'}{'in-addr'} = "selected='selected'">in-addr</option>
END
;

&readblockcategories;
foreach (@categories)
{
	print "<option value='$_' $selected{'DST'}{$_}>$_</option>\n";
}

print <<END
		<option value='files' $selected{'DST'}{'files'} = "selected='selected'">files</option>
		<option value='custom-blocked' $selected{'DST'}{'custom-blocked'} = "selected='selected'">custom-blocked</option>
		<option value='custom-expressions' $selected{'DST'}{'custom-expressions'} = "selected='selected'">custom-expressions</option>
		</select>
		</td>
		<td>&nbsp;</td>
		<td class='base' valign='top'>
		<select name='ACCESS'>
		<option value='block' $selected{'ACCESS'}{'block'}>$Lang::tr{'urlfilter mode block'}</option>
		<option value='allow' $selected{'ACCESS'}{'allow'}>$Lang::tr{'urlfilter mode allow'}</option>
		</select>
		</td>
		<td>&nbsp;</td>
	</tr>
	<tr>
		<td>&nbsp;</td>
		<td>&nbsp;</td>
		<td>&nbsp;</td>
		<td>&nbsp;</td>
	</tr>
	<tr>
		<td>$Lang::tr{'remark'}</td>
		<td>&nbsp;</td>
		<td>&nbsp;</td>
		<td>&nbsp;</td>
		<td>&nbsp;</td>
		<td>&nbsp;</td>
	</tr>
	<tr>
		<td><input type='text' name='COMMENT' value='$tcsettings{'COMMENT'}' size='32' /></td>
		<td>&nbsp;</td>
		<td>&nbsp;</td>
		<td>&nbsp;</td>
		<td>&nbsp;</td>
		<td>&nbsp;</td>
	</tr>
</table>

<table width='100%'>
	<tr>
		<td class='base'>$Lang::tr{'urlfilter enabled'}<input type='checkbox' name='ENABLERULE' $checked{'ENABLERULE'}{'on'} /></td>
	</tr>
</table>

<p>

<table width='50%'>
	<tr>
		<td><input type='hidden' name='ACTION' value='$Lang::tr{'add'}' /></td>
		<td><input type='hidden' name='MODE' value='TIMECONSTRAINT' /></td>
		<td><input type='submit' name='SUBMIT' value='$buttontext' /></td>
		<td><input type='reset' name='ACTION' value='$Lang::tr{'urlfilter reset'}' /></td>
		<td>&nbsp;</td>
		<td><input type='button' name='return2main' value='$Lang::tr{'urlfilter back to main page'}' onClick='self.location.href="$ENV{'SCRIPT_NAME'}"'></td>
	</tr>
</table>
<p>
<table width='100%'>
	<tr>
		<td width='1%' align='right'> <img src='/blob.gif' align='top' alt='*' />&nbsp;</td>
		<td><font class='base'>$Lang::tr{'required field'}</font></td>
	</tr>
	<tr>
		<td width='1%' align='right'>&nbsp;</td>
		<td><font class='base'>$Lang::tr{'urlfilter select multi'}</font></td>
	</tr>
</table>
END
;

if ($tcsettings{'ACTION'} eq $Lang::tr{'edit'}) {
	print "<input type='hidden' name='EDITING' value='$tcsettings{'ID'}' />\n";
} else {
	print "<input type='hidden' name='EDITING' value='no' />\n";
}

&Header::closebox();
print "</form>\n";

&Header::openbox('100%', 'left', $Lang::tr{'current rules'});
print <<END
<table width='100%'>
	<tr>
		<td width='5%' class='boldbase' align='center'><b>$Lang::tr{'urlfilter constraint definition'}</b></td>
		<td width='10%' class='boldbase' align='center'><b>$Lang::tr{'urlfilter time space'}</b></td>
		<td width='15%' class='boldbase' align='center'><b>$Lang::tr{'urlfilter src'}</b></td>
		<td width='5%' class='boldbase' align='center'><b>$Lang::tr{'urlfilter dst'}</b></td>
		<td width='10%' class='boldbase' colspan='5' align='center'>&nbsp;</td>
	</tr>
END
;

if ($tcsettings{'ACTION'} ne '' or $changed ne 'no')
{
	open(FILE, $tcfile);
	@tclist = <FILE>;
	close(FILE);
}

$id = 0;
foreach $line (@tclist)
{
	$id++;
	chomp($line);
	@temp = split(/\,/,$line);
	if($tcsettings{'ACTION'} eq $Lang::tr{'edit'} && $tcsettings{'ID'} eq $id) {
		print "<tr bgcolor='$Header::colouryellow'>\n"; }
	elsif ($id % 2) {
		print "<tr bgcolor='$Header::table1colour'>\n"; }
	else {
		print "<tr bgcolor='$Header::table2colour'>\n"; }
	if ($temp[0] eq 'within') { $temp[0]=$Lang::tr{'urlfilter constraint within'}; } else { $temp[0]=$Lang::tr{'urlfilter constraint outside'}; }
	if ($temp[13] eq 'any') { $temp[13]=$Lang::tr{'urlfilter category all'}; }
	if ($temp[15] eq 'on') { $gif='on.gif'; $toggle='off'; $gdesc=$Lang::tr{'click to disable'};}
	else { $gif='off.gif'; $toggle='on'; $gdesc=$Lang::tr{'click to enable'}; }
	if ($temp[14] eq 'block') { $led='led-red.gif'; $ldesc=$Lang::tr{'urlfilter block access'};}
	else { $led='led-green.gif'; $ldesc=$Lang::tr{'urlfilter allow access'}; }

	undef $time;
	if ($temp[1] eq 'on') { $time.=$Lang::tr{'urlfilter mon'}; } else { $time.='='; }
	if ($temp[2] eq 'on') { $time.=$Lang::tr{'urlfilter tue'}; } else { $time.='='; }
	if ($temp[3] eq 'on') { $time.=$Lang::tr{'urlfilter wed'}; } else { $time.='='; }
	if ($temp[4] eq 'on') { $time.=$Lang::tr{'urlfilter thu'}; } else { $time.='='; }
	if ($temp[5] eq 'on') { $time.=$Lang::tr{'urlfilter fri'}; } else { $time.='='; }
	if ($temp[6] eq 'on') { $time.=$Lang::tr{'urlfilter sat'}; } else { $time.='='; }
	if ($temp[7] eq 'on') { $time.=$Lang::tr{'urlfilter sun'}; } else { $time.='='; }
	$time=$time.' &nbsp; '.$temp[8].':'.$temp[9].' to '.$temp[10].':'.$temp[11];

print <<END
		<td align='center'>$temp[0]</td>
		<td align='center' nowrap>$time</td>
		<td align='center'>$temp[12]</td>
		<td align='center'>$temp[13]</td>
		<td align='center'><image src='/images/urlfilter/$led' alt='$ldesc'></td>

		<td align='center'>
		<form method='post' name='frma$id' action='$ENV{'SCRIPT_NAME'}'>
		<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif' title='$gdesc' alt='$gdesc' />
		<input type='hidden' name='MODE' value='TIMECONSTRAINT' />
		<input type='hidden' name='ID' value='$id' />
		<input type='hidden' name='ACTIVE' value='$toggle' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'toggle enable disable'}' />
		</form>
		</td>

		<td align='center'>
		<form method='post' name='frmb$id' action='$ENV{'SCRIPT_NAME'}'>
		<input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' title='$Lang::tr{'edit'}' alt='$Lang::tr{'edit'}' />
		<input type='hidden' name='MODE' value='TIMECONSTRAINT' />
		<input type='hidden' name='ID' value='$id' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'edit'}' />
		</form>
		</td>

		<td align='center'>
		<form method='post' name='frmc$id' action='$ENV{'SCRIPT_NAME'}'>
		<input type='image' name='$Lang::tr{'urlfilter copy rule'}' src='/images/urlfilter/copy.gif' title='$Lang::tr{'urlfilter copy rule'}' alt='$Lang::tr{'urlfilter copy rule'}' />
		<input type='hidden' name='MODE' value='TIMECONSTRAINT' />
		<input type='hidden' name='ID' value='$id' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'urlfilter copy rule'}' />
		</form>
		</td>

		<td align='center'>
		<form method='post' name='frmd$id' action='$ENV{'SCRIPT_NAME'}'>
		<input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' title='$Lang::tr{'remove'}' alt='$Lang::tr{'remove'}' />
		<input type='hidden' name='MODE' value='TIMECONSTRAINT' />
		<input type='hidden' name='ID' value='$id' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'remove'}' />
		</form>
		</td>

	</tr>
END
;
	if($tcsettings{'ACTION'} eq $Lang::tr{'edit'} && $tcsettings{'ID'} eq $id) {
		print "<tr bgcolor='$Header::colouryellow'>\n"; }
	elsif ($id % 2) {
		print "<tr bgcolor='$Header::table1colour'>\n"; }
	else {
		print "<tr bgcolor='$Header::table2colour'>\n"; }
print <<END
		<td align='center' colspan='4'>$temp[16]
		</td>
		<td align='center' colspan='5'>
		</td>
	</tr>
END
;
}

print "</table>\n";

# If the time constraint file contains entries, print entries and action icons
if (! -z "$tcfile") {
print <<END

<table>
	<tr>
		<td class='boldbase'>&nbsp; <b>$Lang::tr{'legend'}:</b></td>
		<td>&nbsp; &nbsp; <img src='/images/urlfilter/led-green.gif' alt='$Lang::tr{'urlfilter allow access'}' /></td>
		<td class='base'>$Lang::tr{'urlfilter allow'}</td>
		<td>&nbsp; &nbsp; <img src='/images/urlfilter/led-red.gif' alt='$Lang::tr{'urlfilter block access'}' /></td>
		<td class='base'>$Lang::tr{'urlfilter block'}</td>
		<td>&nbsp; <img src='/images/on.gif' alt='$Lang::tr{'click to disable'}' /></td>
		<td class='base'>$Lang::tr{'click to disable'}</td>
		<td>&nbsp; &nbsp; <img src='/images/off.gif' alt='$Lang::tr{'click to enable'}' /></td>
		<td class='base'>$Lang::tr{'click to enable'}</td>
		<td>&nbsp; &nbsp; <img src='/images/edit.gif' alt='$Lang::tr{'edit'}' /></td>
		<td class='base'>$Lang::tr{'edit'}</td>
		<td>&nbsp; &nbsp; <img src='/images/urlfilter/copy.gif' alt='$Lang::tr{'urlfilter copy rule'}' /></td>
		<td class='base'>$Lang::tr{'urlfilter copy rule'}</td>
		<td>&nbsp; &nbsp; <img src='/images/delete.gif' alt='$Lang::tr{'remove'}' /></td>
		<td class='base'>$Lang::tr{'remove'}</td>
	</tr>
</table>
END
;
}

&Header::closebox();

} elsif ($uqsettings{'UQMODE'}) {

#==========================================================
#
# Section: Set User Quota
#
#==========================================================

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

$buttontext = $Lang::tr{'urlfilter add rule'};
if ($uqsettings{'ACTION'} eq $Lang::tr{'edit'}) {
&Header::openbox('100%', 'left', $Lang::tr{'urlfilter edit user quota rule'}.':');
$buttontext = $Lang::tr{'urlfilter update rule'};
} else {
&Header::openbox('100%', 'left', $Lang::tr{'urlfilter add new user quota rule'}.':');
}
print <<END

<table width='100%'>
<tr>
	<td width='25%'></td> <td width='20%'> </td><td width='25%'> </td><td width='30%'></td>
</tr>
<tr>
        <td class='base'>$Lang::tr{'urlfilter user time quota'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
        <td><input type='text' name='TIME_QUOTA' value='$uqsettings{'TIME_QUOTA'}' size='5' /></td>
	<td colspan='2' rowspan= '5' valign='top' class='base'>
		<table cellpadding='0' cellspacing='0'>
			<tr>
				<!-- intentionally left empty -->
			</tr>
			<tr>
			<td>$Lang::tr{'urlfilter assigned quota users'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
			</tr>
			<tr>
				<!-- intentionally left empty -->
			</tr>
			<tr>
				<!-- intentionally left empty -->
			</tr>
			<tr>
			<td><textarea name='QUOTA_USERS' cols='32' rows='6' wrap='off'>
END
;

$uqsettings{'QUOTA_USERS'} =~ s/\|/\n/g;
print $uqsettings{'QUOTA_USERS'};

print <<END
</textarea></td>
		</tr>
		</table>
	</td>
</tr>
<tr>
        <td class='base'>$Lang::tr{'urlfilter activity detection'}:</td>
        <td class='base'><select name='SPORADIC'>
                <option value='0'   $selected{'SPORADIC'}{'0'}>$Lang::tr{'urlfilter disabled'}</option>
                <option value='300' $selected{'SPORADIC'}{'300'}>5 $Lang::tr{'urlfilter minutes'}</option>
                <option value='900' $selected{'SPORADIC'}{'900'}>15 $Lang::tr{'urlfilter minutes'}</option>
        </select></td>
</tr>
<tr>
        <td class='base'>$Lang::tr{'urlfilter renewal period'}:</td>
        <td class='base'><select name='RENEWAL'>
                <option value='hourly' $selected{'RENEWAL'}{'hourly'}>$Lang::tr{'urlfilter hourly'}</option>
                <option value='daily'  $selected{'RENEWAL'}{'daily'}>$Lang::tr{'urlfilter daily'}</option>
                <option value='weekly' $selected{'RENEWAL'}{'weekly'}>$Lang::tr{'urlfilter weekly'}</option>
        </select></td>
</tr>
<tr>
	<td colspan='2'>&nbsp;</td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'urlfilter enabled'}</td>
	<td class='base'><input type='checkbox' name='ENABLEQUOTA' $checked{'ENABLEQUOTA'}{'on'} /></td>
</tr>

</table>
<p>

<table width='50%'>
	<tr>
		<td><input type='hidden' name='ACTION' value='$Lang::tr{'add'}' /></td>
		<td><input type='hidden' name='MODE' value='USERQUOTA' /></td>
		<td><input type='submit' name='SUBMIT' value='$buttontext' /></td>
		<td><input type='reset'  name='ACTION' value='$Lang::tr{'urlfilter reset'}' /></td>
		<td>&nbsp;</td>
		<td><input type='button' name='return2main' value='$Lang::tr{'urlfilter back to main page'}' onClick='self.location.href="$ENV{'SCRIPT_NAME'}"'></td>
	</tr>
</table>

<p>
END
;

if ($uqsettings{'ACTION'} eq $Lang::tr{'edit'}) {
	print "<input type='hidden' name='EDITING' value='$uqsettings{'ID'}' />\n";
} else {
	print "<input type='hidden' name='EDITING' value='no' />\n";
}

&Header::closebox();
print "</form>\n";

&Header::openbox('100%', 'left', $Lang::tr{'current rules'});
print <<END
<table width='100%'>
	<tr>
		<td width='15%' class='boldbase' align='center'><b><nobr>$Lang::tr{'urlfilter time quota'}</nobr></b></td>
		<td width='15%' class='boldbase' align='center'><b><nobr>$Lang::tr{'urlfilter activity detection'}</nobr></b></td>
		<td width='10%' class='boldbase' align='center'><b>$Lang::tr{'urlfilter renewal'}</b></td>
		<td class='boldbase' align='center'><b>$Lang::tr{'urlfilter assigned users'}</b></td>
		<td width='20%' class='boldbase' colspan='4' align='center'>&nbsp;</td>
	</tr>
END
;

if ($uqsettings{'ACTION'} ne '' or $changed ne 'no')
{
	open(FILE, $uqfile);
	@uqlist = <FILE>;
	close(FILE);
}

$id = 0;
foreach $line (@uqlist)
{
	$id++;
	chomp($line);
	@temp = split(/\,/,$line);
	if($uqsettings{'ACTION'} eq $Lang::tr{'edit'} && $uqsettings{'ID'} eq $id) {
		print "<tr bgcolor='$Header::colouryellow'>\n"; }
	elsif ($id % 2) {
		print "<tr bgcolor='$Header::table1colour'>\n"; }
	else {
		print "<tr bgcolor='$Header::table2colour'>\n"; }
	if ($temp[4] eq 'on') { $gif='on.gif'; $toggle='off'; $gdesc=$Lang::tr{'click to disable'};}
	else { $gif='off.gif'; $toggle='on'; $gdesc=$Lang::tr{'click to enable'}; }

	$temp[5] = $temp[1];
	if ($temp[1] eq '0') { $temp[5] = $Lang::tr{'urlfilter disabled'} } else { $temp[5] = ($temp[5]/60).' '.$Lang::tr{'urlfilter minutes'} }
	$_ = $temp[3]; s/\|/, /g; $temp[6] = $_;

print <<END
		<td align='center'>$temp[0] $Lang::tr{'urlfilter minutes'}</td>
		<td align='center'>$temp[5]</td>
		<td align='center'>$Lang::tr{'urlfilter '.$temp[2]}</td>
		<td align='center'>$temp[6]</td>

		<td align='center'>
		<form method='post' name='frma$id' action='$ENV{'SCRIPT_NAME'}'>
		<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif' title='$gdesc' alt='$gdesc' />
		<input type='hidden' name='MODE' value='USERQUOTA' />
		<input type='hidden' name='ID' value='$id' />
		<input type='hidden' name='ACTIVE' value='$toggle' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'toggle enable disable'}' />
		</form>
		</td>

		<td align='center'>
		<form method='post' name='frmb$id' action='$ENV{'SCRIPT_NAME'}'>
		<input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' title='$Lang::tr{'edit'}' alt='$Lang::tr{'edit'}' />
		<input type='hidden' name='MODE' value='USERQUOTA' />
		<input type='hidden' name='ID' value='$id' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'edit'}' />
		</form>
		</td>

		<td align='center'>
		<form method='post' name='frmc$id' action='$ENV{'SCRIPT_NAME'}'>
		<input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' title='$Lang::tr{'remove'}' alt='$Lang::tr{'remove'}' />
		<input type='hidden' name='MODE' value='USERQUOTA' />
		<input type='hidden' name='ID' value='$id' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'remove'}' />
		</form>
		</td>

	</tr>
END
;
}

print "</table>\n";

# If the user quota file contains entries, print entries and action icons
if (! -z "$uqfile") {
print <<END

<table>
	<tr>
		<td class='boldbase'>&nbsp; <b>$Lang::tr{'legend'}:</b></td>
		<td>&nbsp; <img src='/images/on.gif' alt='$Lang::tr{'click to disable'}' /></td>
		<td class='base'>$Lang::tr{'click to disable'}</td>
		<td>&nbsp; &nbsp; <img src='/images/off.gif' alt='$Lang::tr{'click to enable'}' /></td>
		<td class='base'>$Lang::tr{'click to enable'}</td>
		<td>&nbsp; &nbsp; <img src='/images/edit.gif' alt='$Lang::tr{'edit'}' /></td>
		<td class='base'>$Lang::tr{'edit'}</td>
		<td>&nbsp; &nbsp; <img src='/images/delete.gif' alt='$Lang::tr{'remove'}' /></td>
		<td class='base'>$Lang::tr{'remove'}</td>
	</tr>
</table>
END
;
}

&Header::closebox();

} else {

#==========================================================
#
# Section: Blacklist editor
#
#==========================================================

print "<form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>\n";

&Header::openbox('100%', 'left', $Lang::tr{'urlfilter urlfilter blacklist editor'}.':');

print <<END

<table width='100%'>
<tr>
	<td width='25%'></td> <td width='20%'> </td><td width='25%'> </td><td width='30%'></td>
</tr>
<tr>
       	<td class='base'><b>$Lang::tr{'urlfilter blacklist name'}</b></td>
</tr>
<tr>
       	<td class='base'>$Lang::tr{'urlfilter blacklist category name'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td><input type='text' name='BE_NAME' value='$besettings{'BE_NAME'}' size='12' /></td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
	<td width='25%'></td> <td width='20%'> </td><td width='25%'> </td><td width='20%'></td>
</tr>
<tr>
       	<td class='base' colspan='4'><b>$Lang::tr{'urlfilter edit domains urls expressions'}</b>&nbsp;<img src='/blob.gif' alt='*' /></td>
</tr>
<tr>
	<td colspan='2'>$Lang::tr{'urlfilter domains'}</td>
	<td colspan='2'>$Lang::tr{'urlfilter urls'}</td>
</tr>
<tr>
	<td colspan='2'><textarea name='BE_DOMAINS' cols='38' rows='10' wrap='off'>
END
;

print $besettings{'BE_DOMAINS'};

print <<END
</textarea></td>
	<td colspan='2'><textarea name='BE_URLS' cols='38' rows='10' wrap='off'>
END
;

print $besettings{'BE_URLS'};

print <<END
</textarea></td>
</tr>
<tr>
	<td colspan='4'>$Lang::tr{'urlfilter expressions'}</td>
</tr>
<tr>
	<td colspan='4'><textarea name='BE_EXPRESSIONS' cols='80' rows='3' wrap='off'>
END
;

print $besettings{'BE_EXPRESSIONS'};

print <<END
</textarea></td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
       	<td class='base' colspan='4'><b>$Lang::tr{'urlfilter load blacklist'}</b></td>
</tr>
<tr>
       	<td width='25%' class='base'>$Lang::tr{'urlfilter select blacklist'}:</td>
	<td width='20%' class='base'>
	<select name='BE_BLACKLIST'>
END
;

&readblockcategories;
foreach (@categories)
{
	print "<option value='$_' $selected{'BE_BLACKLIST'}{$_}>$_</option>\n";
}

print <<END
	</select>
	</td>
	<td>&nbsp;</td>
	<td>&nbsp;</td>
<tr>
	<td colpsan='4'><input type='submit' name='ACTION' value='$Lang::tr{'urlfilter load blacklist'}' /></td>
</tr>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
       	<td class='base' colspan='4'><b>$Lang::tr{'urlfilter import blacklist'}</b></td>
</tr>
<tr>
	<td colspan='4'>$Lang::tr{'urlfilter import text'}:</td>
</tr>
<tr>
	<td nowrap><input type='file' name='IMPORTFILE' size='40' /> &nbsp; <input type='submit' name='ACTION' value='$Lang::tr{'urlfilter import blacklist'}' /></td>
	<td><input type='hidden' name='MODE' value='BLACKLIST_EDITOR' /></td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
       	<td class='base' colspan='4'><b>$Lang::tr{'urlfilter export blacklist'}</b></td>
</tr>
<tr>
	<td><input type='submit' name='ACTION' value='$Lang::tr{'urlfilter export blacklist'}' /></td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
       	<td class='base' colspan='4'><b>$Lang::tr{'urlfilter install blacklist'}</b></td>
</tr>
<tr>
	<td width='25%' class='base'>$Lang::tr{'urlfilter dont restart urlfilter'}:</td>
	<td width='20%' class='base'><input type='checkbox' name='NORESTART' $checked{'NORESTART'}{'on'} /></td>
	<td>&nbsp;</td>
	<td>&nbsp;</td>
</tr>
<tr>
	<td><input type='submit' name='ACTION' value='$Lang::tr{'urlfilter install blacklist'}' /></td>
</tr>
<tr>
       	<td class='base' colspan='4'><br>$Lang::tr{'urlfilter install information'}</td>
</tr>
</table>
<hr size='1'>
<table width='20%'>
<tr>
	<td><input type='reset' name='ACTION' value='$Lang::tr{'urlfilter reset'}' /></td>
	<td>&nbsp;</td>
	<td><input type='button' name='return2main' value='$Lang::tr{'urlfilter back to main page'}' onClick='self.location.href="$ENV{'SCRIPT_NAME'}"'></td>
</tr>
</table>

END
;

&Header::closebox();
print "</form>\n";

}

&Header::closebigbox();

&Header::closepage();

# -------------------------------------------------------------------

sub savesettings
{
	# transform to pre1.8 client definitions
	@clients = split(/\n/,$filtersettings{'UNFILTERED_CLIENTS'});
	undef $filtersettings{'UNFILTERED_CLIENTS'};
	foreach(@clients)
	{
		s/^\s+//g; s/\s+$//g; s/\s+-\s+/-/g; s/\s+/ /g; s/\n//g;
		$filtersettings{'UNFILTERED_CLIENTS'} .= "$_ ";
	}
	$filtersettings{'UNFILTERED_CLIENTS'} =~ s/\s+$//;

	# transform to pre1.8 client definitions
	@clients = split(/\n/,$filtersettings{'BANNED_CLIENTS'});
	undef $filtersettings{'BANNED_CLIENTS'};
	foreach(@clients)
	{
		s/^\s+//g; s/\s+$//g; s/\s+-\s+/-/g; s/\s+/ /g; s/\n//g;
		$filtersettings{'BANNED_CLIENTS'} .= "$_ ";
	}
	$filtersettings{'BANNED_CLIENTS'} =~ s/\s+$//;

	&writeconfigfile;

	delete $filtersettings{'CUSTOM_BLACK_DOMAINS'};
	delete $filtersettings{'CUSTOM_BLACK_URLS'};
	delete $filtersettings{'CUSTOM_WHITE_DOMAINS'};
	delete $filtersettings{'CUSTOM_WHITE_URLS'};
	delete $filtersettings{'CUSTOM_EXPRESSIONS'};
	delete $filtersettings{'BACKGROUND'};
	delete $filtersettings{'UPDATEFILE'};

	system("chown -R nobody.nobody $dbdir");
	system('/usr/bin/squidGuard -C custom/allowed/domains >/dev/null 2>&1');
	system('/usr/bin/squidGuard -C custom/allowed/urls >/dev/null 2>&1');
	system('/usr/bin/squidGuard -C custom/blocked/domains >/dev/null 2>&1');
	system('/usr/bin/squidGuard -C custom/blocked/urls >/dev/null 2>&1 ');
	&setpermissions ($dbdir);

	&General::writehash("${General::swroot}/urlfilter/settings", \%filtersettings);
}

# -------------------------------------------------------------------

sub readblockcategories
{
	undef(@categories);

	&getblockcategory ($dbdir);

	foreach (@categories) { $_ = substr($_,length($dbdir)+1); }

	@filtergroups = @categories;

	foreach (@filtergroups) {
		s/\//_/g;
        	tr/a-z/A-Z/;
	        $_ = "FILTER_".$_;
	}
}

# -------------------------------------------------------------------

sub getblockcategory
{
	foreach $category (<$_[0]/*>)
	{
		if (-d $category)
		{
			if ((-e "$category/domains") || (-e "$category/urls"))
			{
				unless ($category =~ /\bcustom\b/) { push(@categories,$category); }
			}
			&getblockcategory ($category);
		}
	}
}

# -------------------------------------------------------------------

sub readcustomlists
{
	if (-e "$dbdir/custom/blocked/domains") {
		open(FILE,"$dbdir/custom/blocked/domains");
		delete $filtersettings{'CUSTOM_BLACK_DOMAINS'};
		while (<FILE>) { $filtersettings{'CUSTOM_BLACK_DOMAINS'} .= $_ };
		close(FILE);
	}

	if (-e "$dbdir/custom/blocked/urls") {
		open(FILE,"$dbdir/custom/blocked/urls");
		delete $filtersettings{'CUSTOM_BLACK_URLS'};
		while (<FILE>) { $filtersettings{'CUSTOM_BLACK_URLS'} .= $_ };
		close(FILE);
	}

	if (-e "$dbdir/custom/blocked/expressions") {
		open(FILE,"$dbdir/custom/blocked/expressions");
		delete $filtersettings{'CUSTOM_EXPRESSIONS'};
		while (<FILE>) { $filtersettings{'CUSTOM_EXPRESSIONS'} .= $_ };
		close(FILE);
	}

	if (-e "$dbdir/custom/allowed/domains") {
		open(FILE,"$dbdir/custom/allowed/domains");
		delete $filtersettings{'CUSTOM_WHITE_DOMAINS'};
		while (<FILE>) { $filtersettings{'CUSTOM_WHITE_DOMAINS'} .= $_ };
		close(FILE);
	}
	if (-e "$dbdir/custom/allowed/urls") {
		open(FILE,"$dbdir/custom/allowed/urls");
		delete $filtersettings{'CUSTOM_WHITE_URLS'};
		while (<FILE>) { $filtersettings{'CUSTOM_WHITE_URLS'} .= $_ };
		close(FILE);
	}
}

# -------------------------------------------------------------------

sub aggregatedconstraints
{
	my $aggregated;
	my @old;
	my @new;
	my @tmp1;
	my @tmp2;
	my $x;

	if (-e $tcfile)
	{
		open(TC, $tcfile);
		@old = <TC>;
		close(TC);

		while (@old > 0)
		{
			$aggregated = 0;
			$x = shift(@old);
			chomp($x);
			@tmp1 = split(/\,/,$x);
			$tmp1[16] = '';
			foreach (@new)
			{
				@tmp2 = split(/\,/);
				if (($tmp1[15] eq 'on') && ($tmp2[15] eq 'on'))
				{
					if (($tmp1[0] eq $tmp2[0]) && ($tmp1[12] eq $tmp2[12]) && ($tmp1[13] eq $tmp2[13]) && ($tmp1[14] eq $tmp2[14]))
					{
						$aggregated = 1;
						$tmp2[16] .= "    weekly ";
						if ($tmp1[1] eq 'on') { $tmp2[16] .= "m"; }
						if ($tmp1[2] eq 'on') { $tmp2[16] .= "t"; }
						if ($tmp1[3] eq 'on') { $tmp2[16] .= "w"; }
						if ($tmp1[4] eq 'on') { $tmp2[16] .= "h"; }
						if ($tmp1[5] eq 'on') { $tmp2[16] .= "f"; }
						if ($tmp1[6] eq 'on') { $tmp2[16] .= "a"; }
						if ($tmp1[7] eq 'on') { $tmp2[16] .= "s"; }
						$tmp2[16] .= " $tmp1[8]:$tmp1[9]-$tmp1[10]:$tmp1[11]\n";
						$_ = join(",",@tmp2);
					}

				}
			}
			if (!$aggregated)
			{
				$tmp1[16] .= "    weekly ";
				if ($tmp1[1] eq 'on') { $tmp1[16] .= "m"; }
				if ($tmp1[2] eq 'on') { $tmp1[16] .= "t"; }
				if ($tmp1[3] eq 'on') { $tmp1[16] .= "w"; }
				if ($tmp1[4] eq 'on') { $tmp1[16] .= "h"; }
				if ($tmp1[5] eq 'on') { $tmp1[16] .= "f"; }
				if ($tmp1[6] eq 'on') { $tmp1[16] .= "a"; }
				if ($tmp1[7] eq 'on') { $tmp1[16] .= "s"; }
				$tmp1[16] .= " $tmp1[8]:$tmp1[9]-$tmp1[10]:$tmp1[11]\n";
				$x = join(",",@tmp1);
				push(@new,$x);
			}
		}
	}

	return @new;

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

sub writeconfigfile
{
	my $executables = "/[^/]*\\.\(ade|adp|asx|bas|bat|chm|com|cmd|cpl|crt|dll|eml|exe|hiv|hlp|hta|inc|inf|ins|isp|jse|jtd|lnk|msc|msh|msi|msp|mst|nws|ocx|oft|ops|pcd|pif|plx|reg|scr|sct|sha|shb|shm|shs|sys|tlb|tsp|url|vbe|vbs|vxd|wsc|wsf|wsh\)\$";
	my $audiovideo = "/[^/]*\\.\(aiff|asf|avi|dif|divx|flv|mkv|mov|movie|mp3|mp4|mpe?g?|mpv2|ogg|ra?m|snd|qt|wav|wma|wmf|wmv\)\$";
	my $archives = "/[^/]*\\.\(7z|bin|bz2|cab|cdr|dmg|gz|hqx|rar|smi|sit|sea|tar|tgz|zip\)\$";

	my $ident = " anonymous";

	my $defaultrule='';
	my $tcrule='';
	my $redirect='';
	my $qredirect='';

	my $idx;

	my @ec=();
	my @tc=();
	my @uq=();

	if (!(-d "$dbdir/custom"))         { mkdir("$dbdir/custom") }
	if (!(-d "$dbdir/custom/blocked")) { mkdir("$dbdir/custom/blocked") }
	if (!(-d "$dbdir/custom/allowed")) { mkdir("$dbdir/custom/allowed") }

	open(FILE, ">/$dbdir/custom/blocked/domains");
	print FILE $filtersettings{'CUSTOM_BLACK_DOMAINS'};
	close(FILE);
	open(FILE, ">/$dbdir/custom/blocked/urls");
	print FILE $filtersettings{'CUSTOM_BLACK_URLS'};
	close(FILE);
	open(FILE, ">/$dbdir/custom/blocked/expressions");
	print FILE $filtersettings{'CUSTOM_EXPRESSIONS'};
	close(FILE);
	open(FILE, ">/$dbdir/custom/blocked/files");
	if ($filtersettings{'BLOCK_EXECUTABLES'} eq 'on') { print FILE "$executables\n"; }
	if ($filtersettings{'BLOCK_AUDIO-VIDEO'} eq 'on') { print FILE "$audiovideo\n"; }
	if ($filtersettings{'BLOCK_ARCHIVES'} eq 'on') { print FILE "$archives\n"; }
	close(FILE);
	open(FILE, ">/$dbdir/custom/allowed/domains");
	print FILE $filtersettings{'CUSTOM_WHITE_DOMAINS'};
	close(FILE);
	open(FILE, ">/$dbdir/custom/allowed/urls");
	print FILE $filtersettings{'CUSTOM_WHITE_URLS'};
	close(FILE);

	if ($filtersettings{'ENABLE_USERNAME_LOG'} eq 'on') { $ident = ""; }

	if ($filtersettings{'REDIRECT_PAGE'} eq '')
	{
		if (($filtersettings{'SHOW_CATEGORY'} eq 'on') || ($filtersettings{'SHOW_URL'} eq 'on') || ($filtersettings{'SHOW_IP'} eq 'on')) {
			if ($filtersettings{'SHOW_CATEGORY'} eq 'on') { $redirect .= "&category=%t"; }
			if ($filtersettings{'SHOW_URL'} eq 'on') { $redirect .= "&url=%u"; }
			if ($filtersettings{'SHOW_IP'} eq 'on') { $redirect .= "&ip=%a"; }
			$redirect  =~ s/^&/?/;
			$redirect = "http:\/\/$netsettings{'GREEN_ADDRESS'}:$http_port\/redirect.cgi".$redirect;
		} else {
			$redirect="http:\/\/$netsettings{'GREEN_ADDRESS'}:$http_port\/redirect.cgi";
		}
	} else { $redirect=$filtersettings{'REDIRECT_PAGE'}; }

	if ($filtersettings{'ENABLE_DNSERROR'} eq 'on') { $redirect  = "302:http://0.0.0.0"; }

	undef $defaultrule;

	if ($filtersettings{'ENABLE_CUSTOM_WHITELIST'} eq 'on')
	{
		$defaultrule .= "custom-allowed ";
	}
	if ($filtersettings{'BLOCK_ALL'} eq 'on')
	{
		$defaultrule .= "none";
	}
	else
	{
		if ($filtersettings{'BLOCK_IP_ADDR'} eq 'on')
		{
			$defaultrule .= "!in-addr ";
		}
		for ($i=0; $i<=@filtergroups; $i++) {
			if ($filtersettings{@filtergroups[$i]} eq 'on')
			{
				$defaultrule .= "!@categories[$i] ";
			}
		}
		if ($filtersettings{'ENABLE_CUSTOM_BLACKLIST'} eq 'on')
		{
			$defaultrule .= "!custom-blocked ";
		}
		if ($filtersettings{'ENABLE_CUSTOM_EXPRESSIONS'} eq 'on')
		{
			$defaultrule .= "!custom-expressions ";
		}
		if (($filtersettings{'BLOCK_EXECUTABLES'} eq 'on') ||
		    ($filtersettings{'BLOCK_AUDIO-VIDEO'} eq 'on') ||
		    ($filtersettings{'BLOCK_ARCHIVES'} eq 'on'))
		{
			$defaultrule .= "!files ";
		}
		$defaultrule .= "any";
	}

	$defaultrule =~ s/\//_/g;

	open(FILE, ">${General::swroot}/urlfilter/squidGuard.conf") or die "Unable to write squidGuard.conf file";
	flock(FILE, 2);

	print FILE "logdir /var/log/squidGuard\n";
	print FILE "dbhome $dbdir\n\n";

	undef @repositoryfiles;
	if ($filtersettings{'ENABLE_REWRITE'} eq 'on')
	{
		@repositorylist = <$repository/*>;
		foreach (@repositorylist)
		{
			if (!-d) { push(@repositoryfiles,substr($_,rindex($_,"/")+1));  }
		}
	}

	if ((($filtersettings{'ENABLE_REWRITE'} eq 'on') && (@repositoryfiles)) || ($filtersettings{'ENABLE_SAFESEARCH'} eq 'on'))
	{
		print FILE "rewrite rew-rule-1 {\n";

		if (($filtersettings{'ENABLE_REWRITE'} eq 'on') && (@repositoryfiles))
		{
			print FILE "    # rewrite localfiles\n";
			foreach (@repositoryfiles)
			{
				print FILE "    s@.*/$_\$\@http://$netsettings{'GREEN_ADDRESS'}:$http_port/repository/$_\@i\n";
			}
		}

		if ($filtersettings{'ENABLE_SAFESEARCH'} eq 'on')
		{
			print FILE "    # rewrite safesearch\n";
			print FILE "    s@(.*\\Wgoogle\\.\\w+/(webhp|search|imghp|images|grphp|groups|nwshp|frghp|froogle)\\?)(.*)(\\bsafe=\\w+)(.*)\@\\1\\3safe=strict\\5\@i\n";
			print FILE "    s@(.*\\Wgoogle\\.\\w+/(webhp|search|imghp|images|grphp|groups|nwshp|frghp|froogle)\\?)(.*)\@\\1safe=strict\\\&\\3\@i\n";
			print FILE "    s@(.*\\Wsearch\\.yahoo\\.\\w+/search\\W)(.*)(\\bvm=\\w+)(.*)\@\\1\\2vm=r\\4\@i\n";
			print FILE "    s@(.*\\Wsearch\\.yahoo\\.\\w+/search\\W.*)\@\\1\\\&vm=r\@i\n";
			print FILE "    s@(.*\\Walltheweb\\.com/customize\\?)(.*)(\\bcopt_offensive=\\w+)(.*)\@\\1\\2copt_offensive=on\\4\@i\n";
			print FILE "    s@(.*\\Wbing\\.\\w+/)(.*)(\\badlt=\\w+)(.*)\@\\1\\2adlt=strict\\4\@i\n";
			print FILE "    s@(.*\\Wbing\\.\\w+/.*)\@\\1\\\&adlt=strict\@i\n";
		}

		print FILE "}\n\n";

		if ((!($filtersettings{'UNFILTERED_CLIENTS'} eq '')) && ($filtersettings{'ENABLE_SAFESEARCH'} eq 'on')) {
			print FILE "rewrite rew-rule-2 {\n";
			if (($filtersettings{'ENABLE_REWRITE'} eq 'on') && (@repositoryfiles))
			{
				print FILE "    # rewrite localfiles\n";
				foreach (@repositoryfiles)
				{
					print FILE "    s@.*/$_\$\@http://$netsettings{'GREEN_ADDRESS'}:$http_port/repository/$_\@i\n";
				}
			} else {
				print FILE "    # rewrite nothing\n";
			}
			print FILE "}\n\n";
		}
	}

	if (!($filtersettings{'UNFILTERED_CLIENTS'} eq '')) {
		print FILE "src unfiltered {\n";
		print FILE "    ip $filtersettings{'UNFILTERED_CLIENTS'}\n";
		print FILE "}\n\n";
	}
	if (!($filtersettings{'BANNED_CLIENTS'} eq '')) {
		print FILE "src banned {\n";
		print FILE "    ip $filtersettings{'BANNED_CLIENTS'}\n";
		if ($filtersettings{'ENABLE_LOG'} eq 'on')
		{
			if ($filtersettings{'ENABLE_CATEGORY_LOG'} eq 'on')
			{
				print FILE "    logfile       ".$ident." banned.log\n";
			} else {
				print FILE "    logfile       ".$ident." urlfilter.log\n";
			}
		}
		print FILE "}\n\n";
	}

	if (-e $uqfile)
	{
		open(UQ, $uqfile);
		@uqlist = <UQ>;
		close(UQ);

		if (@uqlist > 0)
		{
			$idx=0;
			foreach (@uqlist)
			{
				chomp;
				@uq = split(/\,/);
				if ($uq[4] eq 'on')
				{
					$idx++;
					$uq[0] = $uq[0] * 60;
					if ($uq[1] eq '0') {
						if ($uq[2] eq 'hourly') { $uq[1] = 3600 }
						if ($uq[2] eq 'daily')  { $uq[1] = 86400 }
						if ($uq[2] eq 'weekly') { $uq[1] = 604800 }
					}
					$uq[3] =~ s/\|/ /g;
					print FILE "src quota-$idx {\n";
					print FILE "    user $uq[3]\n";
					print FILE "    userquota $uq[0] $uq[1] $uq[2]\n";
					print FILE "}\n\n";
				}
			}

		}
	}

	@tclist = &aggregatedconstraints;

	if (@tclist > 0)
	{
		$idx=0;
		foreach (@tclist)
		{
			chomp;
			@tc = split(/\,/);
			if ($tc[15] eq 'on')
			{
				$idx++;
				print FILE "src network-$idx {\n";
				@clients = split(/ /,$tc[12]);
				@temp = split(/-/,$clients[0]);
				if ( (&General::validipormask($temp[0])) || (&General::validipandmask($temp[0])))
				{
					print FILE "    ip $tc[12]\n";
				} else {
					print FILE "    user";
					@clients = split(/ /,$tc[12]);
					foreach $line (@clients)
					{
						$line =~ s/(^\w+)\\(\w+$)/$1%5c$2/;
						print FILE " $line";
					}
					print FILE "\n";
				}
				if (($filtersettings{'ENABLE_LOG'} eq 'on') && ($tc[14] eq 'block') && ($tc[13] eq 'any'))
				{
					if ($filtersettings{'ENABLE_CATEGORY_LOG'} eq 'on')
					{
						print FILE "    logfile       ".$ident." timeconst.log\n";
					} else {
						print FILE "    logfile       ".$ident." urlfilter.log\n";
					}
				}
				print FILE "}\n\n";
			}
		}

		$idx=0;
		foreach (@tclist)
		{
			chomp;
			@tc = split(/\,/);
			if ($tc[15] eq 'on')
			{
				$idx++;
				print FILE "time constraint-$idx {\n";
				print FILE "$tc[16]\n";
				print FILE "}\n\n";
			}
		}
	}

	foreach $category (@categories) {
		$blacklist = $category;
		$category =~ s/\//_/g;
		
		if ( $filtersettings{"FILTER_".uc($category)} ne "on" ){
			my $constraintrule = "false";
			
			foreach (@tclist){
				chomp;
				@tc = split(/\,/);
				$tc[13] =~ s/\//_/g;
				if ($tc[15] eq 'on' && $tc[13] =~ $category){
					$constraintrule = "true";
				}
			}
			
			if ( $constraintrule eq "false"){
				next;
			}
		}
		
		print FILE "dest $category {\n";
		if (-e "$dbdir/$blacklist/domains") {
			print FILE "    domainlist     $blacklist\/domains\n";
		}
		if (-e "$dbdir/$blacklist/urls") {
			print FILE "    urllist        $blacklist\/urls\n";
		}
		if ((-e "$dbdir/$blacklist/expressions") && ($filtersettings{'ENABLE_EXPR_LISTS'} eq 'on')) {
			print FILE "    expressionlist $blacklist\/expressions\n";
		}
		if ((($category eq 'ads') || ($category eq 'adv')) && ($filtersettings{'ENABLE_EMPTY_ADS'} eq 'on'))
		{
			print FILE "    redirect       http:\/\/$netsettings{'GREEN_ADDRESS'}:$http_port\/images/urlfilter/1x1.gif\n";
		}
		if ($filtersettings{'ENABLE_LOG'} eq 'on')
		{
			if ($filtersettings{'ENABLE_CATEGORY_LOG'} eq 'on')
			{
				print FILE "    logfile       $ident $category.log\n";
			} else {
				print FILE "    logfile       $ident urlfilter.log\n";
			}
		}
		print FILE "}\n\n";
		$category = $blacklist;
	}

	print FILE "dest files {\n";
	print FILE "    expressionlist custom\/blocked\/files\n";
	if ($filtersettings{'ENABLE_LOG'} eq 'on')
	{
		if ($filtersettings{'ENABLE_CATEGORY_LOG'} eq 'on')
		{
			print FILE "    logfile       $ident files.log\n";
		} else {
			print FILE "    logfile       $ident urlfilter.log\n";
		}
	}
	print FILE "}\n\n";

	print FILE "dest custom-allowed {\n";
	print FILE "    domainlist     custom\/allowed\/domains\n";
	print FILE "    urllist        custom\/allowed\/urls\n";
	print FILE "}\n\n";

	print FILE "dest custom-blocked {\n";
	print FILE "    domainlist     custom\/blocked\/domains\n";
	print FILE "    urllist        custom\/blocked\/urls\n";
	if ($filtersettings{'ENABLE_LOG'} eq 'on')
	{
		if ($filtersettings{'ENABLE_CATEGORY_LOG'} eq 'on')
		{
			print FILE "    logfile       $ident custom.log\n";
		} else {
			print FILE "    logfile       $ident urlfilter.log\n";
		}
	}
	print FILE "}\n\n";

	print FILE "dest custom-expressions {\n";
	print FILE "    expressionlist custom\/blocked\/expressions\n";
	if ($filtersettings{'ENABLE_LOG'} eq 'on')
	{
		if ($filtersettings{'ENABLE_CATEGORY_LOG'} eq 'on')
		{
			print FILE "    logfile       $ident custom.log\n";
		} else {
			print FILE "    logfile       $ident urlfilter.log\n";
		}
	}
	print FILE "}\n\n";

	print FILE "acl {\n";
	if (!($filtersettings{'UNFILTERED_CLIENTS'} eq '')) {
		print FILE "    unfiltered {\n";
		print FILE "        pass all\n";
		if ($filtersettings{'ENABLE_SAFESEARCH'} eq 'on')
		{
			print FILE "        rewrite rew-rule-2\n";
		}
		print FILE "    }\n\n";
	}
	if (!($filtersettings{'BANNED_CLIENTS'} eq '')) {
		print FILE "    banned {\n";
		print FILE "        pass ";
		if (($filtersettings{'ENABLE_CUSTOM_WHITELIST'} eq 'on') && ($filtersettings{'ENABLE_GLOBAL_WHITELIST'} eq 'on'))
		{
			print FILE "custom-allowed ";
		}
		print FILE "none\n";
		print FILE "    }\n\n";
	}

	if (-s $uqfile)
	{
		open(UQ, $uqfile);
		@uqlist = <UQ>;
		close(UQ);

		$idx=0;
		foreach (@uqlist)
		{
			chomp;
			@uq = split(/\,/);
			if ($uq[4] eq 'on')
			{
				$idx++;
				$qredirect = $redirect;
				$qredirect =~ s/\%t/\%q\%20-\%20\%i/;
				print FILE "    quota-$idx {\n";
				print FILE "        pass ";
				if (($filtersettings{'ENABLE_CUSTOM_WHITELIST'} eq 'on') && ($filtersettings{'ENABLE_GLOBAL_WHITELIST'} eq 'on'))
				{
					print FILE "custom-allowed ";
				}
				print FILE "none\n";
				unless ($redirect eq $qredirect) { print FILE "        redirect $qredirect\n"; }
				print FILE "    }\n\n";
			}
		}
	}

	if (@tclist > 0)
	{
		$idx=0;
		foreach (@tclist)
		{
			chomp;
			@tc = split(/\,/);
			@ec = split(/\|/,$tc[13]);
			foreach (@ec) { s/\//_/g; }
			if ($tc[15] eq 'on')
			{
				$idx++;
				print FILE "    network-$idx $tc[0] constraint-$idx {\n";
				print FILE "        pass ";

				if ($filtersettings{'BLOCK_ALL'} eq 'on')
				{
					if ($tc[14] eq 'block')
					{
						if ((@ec == 1) && ($ec[0] eq 'any')) {
							if (($filtersettings{'ENABLE_CUSTOM_WHITELIST'} eq 'on') && ($filtersettings{'ENABLE_GLOBAL_WHITELIST'} eq 'on'))
							{
								print FILE "custom-allowed ";
							}
							print FILE "none";
						} else {
							print FILE $defaultrule;
						}
					} else {
						foreach (@ec)
						{
							print FILE "$_ ";
						}
						print FILE $defaultrule unless ((@ec == 1) && ($ec[0] eq 'any'));
					}
				} else {
					if ($tc[14] eq 'block')
					{
						$tcrule = $defaultrule;
						if ($filtersettings{'ENABLE_CUSTOM_WHITELIST'} eq 'on') {
							$tcrule =~ s/custom-allowed //;
							print FILE "custom-allowed " unless ((@ec == 1) && ($ec[0] eq 'any') && ($filtersettings{'ENABLE_GLOBAL_WHITELIST'} eq 'off'));
						}
						if ((@ec == 1) && ($ec[0] eq 'any')) {
							print FILE "none";
						} else {
							foreach (@ec)
							{
								print FILE "!$_ " unless (index($defaultrule,"!".$_." ") ge 0);
							}
						}
						print FILE $tcrule unless ((@ec == 1) && ($ec[0] eq 'any'));
					} else {
						$tcrule = $defaultrule;
						if ((@ec == 1) && ($ec[0] eq 'any'))
						{
							print FILE "any";
						} else {
							foreach (@ec)
							{
								$tcrule = "$_ ".$tcrule unless (index($defaultrule,"!".$_." ") ge 0);
								$tcrule =~ s/!$_ //;
							}
							print FILE $tcrule;
						}
					}
				}

				print FILE "\n";

				print FILE "    }\n\n";
			}
		}
	}

	print FILE "    default {\n";
	print FILE "        pass $defaultrule\n";
	if (($filtersettings{'ENABLE_LOG'} eq 'on') && ($filtersettings{'BLOCK_ALL'} eq 'on'))
	{
		if ($filtersettings{'ENABLE_CATEGORY_LOG'} eq 'on')
		{
			print FILE "        logfile".$ident." default.log\n";
		} else {
			print FILE "        logfile".$ident." urlfilter.log\n";
		}
	}
	if ((($filtersettings{'ENABLE_REWRITE'} eq 'on') && (@repositoryfiles)) || ($filtersettings{'ENABLE_SAFESEARCH'} eq 'on'))
	{
		print FILE "        rewrite rew-rule-1\n";
	}
	print FILE "        redirect $redirect\n";
	print FILE "    }\n";
	print FILE "}\n";

	close FILE;
}

# -------------------------------------------------------------------
