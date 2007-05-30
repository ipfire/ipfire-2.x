#!/usr/bin/perl
#
# This file is a library file for the Net-Traffic Addon.
#
# Copyright (C) 2006 Achim Weber <dotzball@users.sourceforge.net>
#
# $Id: net-traffic-admin.pl,v 1.13 2006/12/10 13:46:00 dotzball Exp $
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

package NETTRAFF;

use strict;
use LWP::UserAgent;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

$|=1; # line buffering

my $updateUrl = "http://blockouttraffic.de/version/Net-Traffic.latest";
my $latestVersionFile = "${General::swroot}/net-traffic/latestVersion";

%NETTRAFF::settings;


$NETTRAFF::settingsfile = "${General::swroot}/net-traffic/settings";
$NETTRAFF::versionfile = "${General::swroot}/net-traffic/version";
$NETTRAFF::logfile = "/var/log/net-traffic.log";
$NETTRAFF::colorOk 	 = '#00FF00';
$NETTRAFF::colorWarn = '#FFFF00';
$NETTRAFF::colorMax  = '#FF0000';


#~ $NETTRAFF::settingsCGI = '/cgi-bin/fwrulesadm.cgi';
#~ $NETTRAFF::configCGI = '/cgi-bin/fwrules.cgi';
#~ $NETTRAFF::advConfCGI = '/cgi-bin/fwadvconf.cgi';


@NETTRAFF::longmonths = ( $Lang::tr{'january'}, $Lang::tr{'february'}, $Lang::tr{'march'},
	$Lang::tr{'april'}, $Lang::tr{'may'}, $Lang::tr{'june'}, $Lang::tr{'july'}, $Lang::tr{'august'},
	$Lang::tr{'september'}, $Lang::tr{'october'}, $Lang::tr{'november'},
	$Lang::tr{'december'} );

@NETTRAFF::months = ( 0,1,2,3,4,5,6,7,8,9,10,11 );

@NETTRAFF::years=("2001","2002","2003","2004","2005","2006","2007","2008","2009");

#workaround to suppress a warning when a variable is used only once
my @dummy = ( $General::version );
undef (@dummy);


# Init Settings
$NETTRAFF::settings{'MONTHLY_VOLUME_ON'} = 'off';
$NETTRAFF::settings{'MONTHLY_VOLUME'} = '1';
$NETTRAFF::settings{'STARTDAY'} = '1';
$NETTRAFF::settings{'WARN_ON'} = 'off';
$NETTRAFF::settings{'WARN'} = '80';
$NETTRAFF::settings{'CALC_INTERVAL'} = '60';
$NETTRAFF::settings{'SHOW_AT_HOME'} = 'on';
$NETTRAFF::settings{'SEND_EMAIL_ON'} = 'off';
$NETTRAFF::settings{'EMAIL_TO'} = '';
$NETTRAFF::settings{'EMAIL_FROM'} = '';
$NETTRAFF::settings{'EMAIL_USR'} = '';
$NETTRAFF::settings{'EMAIL_PW'} = '';
$NETTRAFF::settings{'EMAIL_SERVER'} = '';
$NETTRAFF::settings{'VERSION_CHECK_ON'} = 'off';

&NETTRAFF::readSettings();


sub readSettings
{
	&General::readhash($NETTRAFF::settingsfile, \%NETTRAFF::settings);
}


sub showNetTrafficVersion
{
	my %versionSettings = ();

	&General::readhash($NETTRAFF::versionfile, \%versionSettings);

	print <<END;
		<a href="http://$versionSettings{'URL'}" target="_blank">
		<b>Net-Traffic $versionSettings{'VERSION_INSTALLED'}
		-
END
	print "Build $versionSettings{'BUILD_INSTALLED'}";

	if ($versionSettings{'IS_TESTVERSION'} == 1) {
		print " - Testversion $versionSettings{'TESTVERSION'}";
	}
	print "</b></a><br /><br />\n";
	
	# check for new version
	&checkForNewVersion();
}

sub traffPercentbar
{
	my $percent = $_[0];
	my $fg = '#a0a0a0';
	my $bg = '#e2e2e2';

	if ($percent =~ m/^(\d+)%$/ )
	{
		print <<END;
			<table width='100%' border='1' cellspacing='0' cellpadding='0' style='border-width:1px;border-style:solid;border-color:$fg;width:100%;height:10px;'>
			<tr>
END

		if ($percent eq "100%" || $1 > 100)
		{
			$fg = $NETTRAFF::colorMax;
			print "<td width='100%' bgcolor='$fg' style='background-color:$fg;border-style:solid;border-width:1px;border-color:$bg'>"
		}
		elsif ($percent eq "0%")
		{
			print "<td width='100%' bgcolor='$bg' style='background-color:$bg;border-style:solid;border-width:1px;border-color:$bg'>"
		}
		else
		{
			if($NETTRAFF::settings{'WARN_ON'} eq 'on'
				&& $1 >= $NETTRAFF::settings{'WARN'})
			{
				$fg = $NETTRAFF::colorWarn;
			}

			print "<td width='$percent' bgcolor='$fg' style='background-color:$fg;border-style:solid;border-width:1px;border-color:$bg'></td><td width='" . (100-$1) . "%' bgcolor='$bg' style='background-color:$bg;border-style:solid;border-width:1px;border-color:$bg'>"
		}
		print <<END;
					<img src='/images/null.gif' width='1' height='1' alt='' />
				</td>
			</tr>
			</table>
END

	}
}


sub checkForNewVersion
{
	if ($NETTRAFF::settings{'VERSION_CHECK_ON'} ne 'on')
	{
		return;
	}

	# download latest version
	&downloadLatestVersionInfo();

	if(-e $latestVersionFile)
	{
		my %versionSettings = ();
		&General::readhash($NETTRAFF::versionfile, \%versionSettings);

		my %latestVersion = ();
		&General::readhash($latestVersionFile, \%latestVersion);

		if( $versionSettings{'VERSION_INSTALLED'} lt $latestVersion{'VERSION_AVAILABLE'}
			|| ( $versionSettings{'VERSION_INSTALLED'} le $latestVersion{'VERSION_AVAILABLE'}
				&& $versionSettings{'BUILD_INSTALLED'} lt $latestVersion{'BUILD_AVAILABLE'} ) )
		{
			&Header::openbox('100%', 'left', $Lang::tr{'info'});
			print <<END;
				<table width="100%">
				<tr>
					<td>
						$Lang::tr{'net traffic newversion'}
						<a href="$latestVersion{'URL_UPDATE'}" target="_blank">
							<b>$latestVersion{'URL_UPDATE'}</b>
						</a>
					</td>
				</tr>
				<tr>
					<td>
						<b>v$latestVersion{'VERSION_AVAILABLE'} - Build $latestVersion{'BUILD_AVAILABLE'}
				</table>
END

			&Header::closebox();
		}
	}
}

sub downloadLatestVersionInfo
{
	# only check if we are online
	if (! -e '/var/ipfire/red/active')
	{
		return;
	}

	# download latest version file if it is not existing or outdated (i.e. 5 days old)
	if((! -e $latestVersionFile) || (int(-M $latestVersionFile) > 5))
	{
		my %versionSettings = ();
		&General::readhash($NETTRAFF::versionfile, \%versionSettings);

		my $ua = LWP::UserAgent->new;
		$ua->timeout(120);
		$ua->agent("Mozilla/4.0 (compatible; IPFire $General::version; $versionSettings{'VERSION_INSTALLED'})");
		my $content = $ua->get($updateUrl);

		if ( $content->is_success )
		{
#~ 			open(FILE, ">$latestVersionFile") or die "Could not write file: $latestVersionFile";
#~ 			flock (FILE, 2);
#~ 			print FILE "$content->content\n";
#~ 			close(FILE);

			my %latestVersion = ();

			# latest versions, format is: MOD_VERSION="1.3.0"
			$content->content =~ /MOD_VERSION="(.+?)"/;
			$latestVersion{'VERSION_AVAILABLE'} = $1;

			# latest build, format is: MOD_BUILD="0"
			$content->content =~ /MOD_BUILD="(.+?)"/;
			$latestVersion{'BUILD_AVAILABLE'} = $1;

			# URL format is: MOD_URL="http://blockouttraffic.de/nt_index.php"
			$content->content =~ /MOD_URL="(.+?)"/;
			$latestVersion{'URL_UPDATE'} = $1;

			&General::writehash($latestVersionFile, \%latestVersion);
		}
	}
}


sub getFormatedDate
{
	my $time = shift;
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($time);
		
	return sprintf("%04d-%02d-%02d, %02d:%02d", 1900+$year, $mon+1, $mday, $hour, $min);;
	
}
# always return 1;
1;
# EOF
