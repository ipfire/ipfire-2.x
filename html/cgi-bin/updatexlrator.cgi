#!/usr/bin/perl
#
# This code is distributed under the terms of the GPL
#
# (c) 2006-2008 marco.s - http://update-accelerator.advproxy.net
#
# Portions (c) 2008 by dotzball - http://www.blockouttraffic.de
#
# $Id: updatexlrator.cgi,v 2.1.0 2008/07/16 00:00:00 marco.s Exp $
#
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
#
# Changelog:
# 2012-10-27: nightshift - Bugfix regarding showing wrong vendor icon while Download of new Updates
# 2012-10-27: nightshift - Optimizing logic of check for vendor icons
#

use strict;

# enable only the following on debugging purpose
#use warnings; no warnings 'once';# 'redefine', 'uninitialized';
#use CGI::Carp 'fatalsToBrowser';

use IO::Socket;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %color = ();
my %checked=();
my %selected=();
my %netsettings=();
my %mainsettings=();
my %proxysettings=();
my %xlratorsettings=();
my %dlinfo=();
my $id=0;
my @dfdata=();
my $dfstr='';
my @updatelist=();
my @sources=();
my $sourceurl='';
my $vendorid='';
my $uuid='';
my $status=0;
my $updatefile='';
my $shortname='';
my $time='';
my $filesize=0;
my $filedate='';
my $lastaccess='';
my $lastcheck='';
my $cachedtraffic=0;
my @requests=();
my $data='';
my $counts=0;
my $numfiles=0;
my $cachehits=0;
my $efficiency='0.0';
my @vendors=();
my %vendorstats=();

my $repository = "/var/updatecache/";
my $webhome = "/srv/web/ipfire/html"; 
my $hintcolour = '#FFFFCC';
my $colourgray = '#808080';

my $sfUnknown='0';
my $sfOk='1';
my $sfOutdated='2';
my $sfNoSource='3';

my $not_accessed_last='';

my $errormessage='';

my @repositorylist=();
my @repositoryfiles=();
my @downloadlist=();
my @downloadfiles=();

my @metadata=();

&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

$xlratorsettings{'ACTION'} = '';
$xlratorsettings{'ENABLE_LOG'} = 'off';
$xlratorsettings{'PASSIVE_MODE'} = 'off';
$xlratorsettings{'MAX_DISK_USAGE'} = '75';
$xlratorsettings{'LOW_DOWNLOAD_PRIORITY'} = 'off';
$xlratorsettings{'MAX_DOWNLOAD_RATE'} = '';
$xlratorsettings{'ENABLE_AUTOCHECK'} = 'off';
$xlratorsettings{'FULL_AUTOSYNC'} = 'off';
$xlratorsettings{'NOT_ACCESSED_LAST'} = 'month1';
$xlratorsettings{'REMOVE_NOSOURCE'} = 'off';
$xlratorsettings{'REMOVE_OUTDATED'} = 'off';
$xlratorsettings{'REMOVE_OBSOLETE'} = 'off';

&Header::getcgihash(\%xlratorsettings);

$xlratorsettings{'EXTENDED_GUI'} = '';

if ($xlratorsettings{'ACTION'} eq "$Lang::tr{'updxlrtr statistics'} >>")
{
	$xlratorsettings{'EXTENDED_GUI'} = 'statistics';
}

if ($xlratorsettings{'ACTION'} eq "$Lang::tr{'updxlrtr maintenance'} >>")
{
	$xlratorsettings{'EXTENDED_GUI'} = 'maintenance';
}

if ($xlratorsettings{'ACTION'} eq $Lang::tr{'updxlrtr purge'})
{
	$xlratorsettings{'EXTENDED_GUI'} = 'maintenance';

	if (($xlratorsettings{'REMOVE_OBSOLETE'} eq 'on') || ($xlratorsettings{'REMOVE_NOSOURCE'} eq 'on') || ($xlratorsettings{'REMOVE_OUTDATED'} eq 'on'))
	{
		undef (@sources);
		undef @repositoryfiles;
		foreach (<$repository/*>)
		{
			if (-d $_)
			{
				unless (/^$repository\/download$/) { push(@sources,$_); }
			}
		}

		foreach (@sources)
		{
			@updatelist=<$_/*>;
			$vendorid = substr($_,rindex($_,"/")+1);
			foreach(@updatelist)
			{
				$uuid = substr($_,rindex($_,"/")+1);
				if (-e "$_/source.url")
				{
					open (FILE,"$_/source.url");
					$sourceurl=<FILE>;
					close FILE;
					chomp($sourceurl);
					$updatefile = substr($sourceurl,rindex($sourceurl,'/')+1,length($sourceurl));
					$updatefile = "$vendorid/$uuid/$updatefile";
					push(@repositoryfiles,$updatefile);
				}
			}
		}

		foreach (@repositoryfiles)
		{
			($vendorid,$uuid,$updatefile) = split('/');

			if (-e "$repository/$vendorid/$uuid/status")
			{
				open (FILE,"$repository/$vendorid/$uuid/status");
				@metadata = <FILE>;
				close FILE;
				chomp(@metadata);
				$status = $metadata[-1];
			}

			if (-e "$repository/$vendorid/$uuid/access.log")
			{
				open (FILE,"$repository/$vendorid/$uuid/access.log");
				@metadata = <FILE>;
				close FILE;
				chomp(@metadata);
				$lastaccess = $metadata[-1];
			}

			if (($xlratorsettings{'REMOVE_NOSOURCE'} eq 'on') && ($status == $sfNoSource))
			{
				if (-e "$repository/$vendorid/$uuid/$updatefile") { system("rm -r $repository/$vendorid/$uuid"); }
			}
			if (($xlratorsettings{'REMOVE_OUTDATED'} eq 'on') && ($status == $sfOutdated))
			{
				if (-e "$repository/$vendorid/$uuid/$updatefile") { system("rm -r $repository/$vendorid/$uuid"); }
			}
			if ($xlratorsettings{'REMOVE_OBSOLETE'} eq 'on')
			{
				if (($xlratorsettings{'NOT_ACCESSED_LAST'} eq 'week') && ($lastaccess < (time - 604800)))
				{
					if (-e "$repository/$vendorid/$uuid/$updatefile") { system("rm -r $repository/$vendorid/$uuid"); }
				}
				if (($xlratorsettings{'NOT_ACCESSED_LAST'} eq 'month1') && ($lastaccess < (time - 2505600)))
				{
					if (-e "$repository/$vendorid/$uuid/$updatefile") { system("rm -r $repository/$vendorid/$uuid"); }
				}
				if (($xlratorsettings{'NOT_ACCESSED_LAST'} eq 'month3') && ($lastaccess < (time - 7516800)))
				{
					if (-e "$repository/$vendorid/$uuid/$updatefile") { system("rm -r $repository/$vendorid/$uuid"); }
				}
				if (($xlratorsettings{'NOT_ACCESSED_LAST'} eq 'month6') && ($lastaccess < (time - 15033600)))
				{
					if (-e "$repository/$vendorid/$uuid/$updatefile") { system("rm -r $repository/$vendorid/$uuid"); }
				}
				if (($xlratorsettings{'NOT_ACCESSED_LAST'} eq 'year') && ($lastaccess < (time - 31536000)))
				{
					if (-e "$repository/$vendorid/$uuid/$updatefile") { system("rm -r $repository/$vendorid/$uuid"); }
				}
			}
		}
	}
}

if ($xlratorsettings{'ACTION'} eq $Lang::tr{'save'})
{
	if (!($xlratorsettings{'MAX_DISK_USAGE'} =~ /^\d+$/) || ($xlratorsettings{'MAX_DISK_USAGE'} < 1) || ($xlratorsettings{'MAX_DISK_USAGE'} > 100))
	{
		$errormessage = $Lang::tr{'updxlrtr invalid disk usage'};
		goto ERROR;
	}
	if (($xlratorsettings{'MAX_DOWNLOAD_RATE'} ne '') && ((!($xlratorsettings{'MAX_DOWNLOAD_RATE'} =~ /^\d+$/)) || ($xlratorsettings{'MAX_DOWNLOAD_RATE'} < 1)))
	{
		$errormessage = $Lang::tr{'updxlrtr invalid download rate'};
		goto ERROR;
	}

	&savesettings;
}

if ($xlratorsettings{'ACTION'} eq $Lang::tr{'updxlrtr save and restart'})
{
	if (!($xlratorsettings{'MAX_DISK_USAGE'} =~ /^\d+$/) || ($xlratorsettings{'MAX_DISK_USAGE'} < 1) || ($xlratorsettings{'MAX_DISK_USAGE'} > 100))
	{
		$errormessage = $Lang::tr{'updxlrtr invalid disk usage'};
		goto ERROR;
	}
	if (($xlratorsettings{'MAX_DOWNLOAD_RATE'} ne '') && ((!($xlratorsettings{'MAX_DOWNLOAD_RATE'} =~ /^\d+$/)) || ($xlratorsettings{'MAX_DOWNLOAD_RATE'} < 1)))
	{
		$errormessage = $Lang::tr{'updxlrtr invalid download rate'};
		goto ERROR;
	}
	if ((!(-e "${General::swroot}/proxy/enable")) && (!(-e "${General::swroot}/proxy/enable_blue")))
	{
		$errormessage = $Lang::tr{'updxlrtr web proxy service required'};
		goto ERROR;
	}
	if (!($proxysettings{'ENABLE_UPDXLRATOR'} eq 'on'))
	{
		$errormessage = $Lang::tr{'updxlrtr not enabled'};
		goto ERROR;
	}

	&savesettings;

	system('/usr/local/bin/squidctrl restart >/dev/null 2>&1');
}

if ($xlratorsettings{'ACTION'} eq $Lang::tr{'updxlrtr remove file'})
{
	$xlratorsettings{'EXTENDED_GUI'} = 'maintenance';

	$updatefile = $xlratorsettings{'ID'};

	unless ($updatefile =~ /^download\//)
	{
		($vendorid,$uuid,$updatefile) = split('/',$updatefile);
		if (-e "$repository/$vendorid/$uuid/$updatefile") { system("rm -r $repository/$vendorid/$uuid"); }
	}
}

if (($xlratorsettings{'ACTION'} eq $Lang::tr{'updxlrtr cancel download'}) || ($xlratorsettings{'ACTION'} eq $Lang::tr{'updxlrtr remove file'}))
{
	$updatefile = $xlratorsettings{'ID'};

	if ($updatefile =~ /^download\//)
	{
		($uuid,$vendorid,$updatefile) = split('/',$updatefile);

		if (-e "$repository/download/$vendorid/$updatefile.info")
		{
			&General::readhash("$repository/download/$vendorid/$updatefile.info", \%dlinfo);

			$id = &getPID("\\s${General::swroot}/updatexlrator/bin/download\\s.*\\s".quotemeta($dlinfo{'SRCURL'})."\\s\\d\\s\\d\$");
			if ($id) { system("/bin/kill -9 $id"); }
			$id = &getPID("\\s/usr/bin/wget\\s.*\\s".quotemeta($dlinfo{'SRCURL'})."\$");
			if ($id) { system("/bin/kill -9 $id"); }

			system("rm $repository/download/$vendorid/$updatefile.info");
		}

		if (-e "$repository/download/$vendorid/$updatefile")
		{
			system("rm $repository/download/$vendorid/$updatefile");
		}
	}

}

$not_accessed_last =  $xlratorsettings{'NOT_ACCESSED_LAST'};
undef($xlratorsettings{'NOT_ACCESSED_LAST'});

if (-e "${General::swroot}/updatexlrator/settings")
{
	&General::readhash("${General::swroot}/updatexlrator/settings", \%xlratorsettings);
}

if ($xlratorsettings{'NOT_ACCESSED_LAST'} eq '')
{
	$xlratorsettings{'NOT_ACCESSED_LAST'} = $not_accessed_last;
}

ERROR:

$checked{'ENABLE_LOG'}{'off'} = '';
$checked{'ENABLE_LOG'}{'on'} = '';
$checked{'ENABLE_LOG'}{$xlratorsettings{'ENABLE_LOG'}} = "checked='checked'";
$checked{'PASSIVE_MODE'}{'off'} = '';
$checked{'PASSIVE_MODE'}{'on'} = '';
$checked{'PASSIVE_MODE'}{$xlratorsettings{'PASSIVE_MODE'}} = "checked='checked'";
$checked{'LOW_DOWNLOAD_PRIORITY'}{'off'} = '';
$checked{'LOW_DOWNLOAD_PRIORITY'}{'on'} = '';
$checked{'LOW_DOWNLOAD_PRIORITY'}{$xlratorsettings{'LOW_DOWNLOAD_PRIORITY'}} = "checked='checked'";
$checked{'ENABLE_AUTOCHECK'}{'off'} = '';
$checked{'ENABLE_AUTOCHECK'}{'on'} = '';
$checked{'ENABLE_AUTOCHECK'}{$xlratorsettings{'ENABLE_AUTOCHECK'}} = "checked='checked'";
$checked{'FULL_AUTOSYNC'}{'off'} = '';
$checked{'FULL_AUTOSYNC'}{'on'} = '';
$checked{'FULL_AUTOSYNC'}{$xlratorsettings{'FULL_AUTOSYNC'}} = "checked='checked'";
$checked{'REMOVE_NOSOURCE'}{'off'} = '';
$checked{'REMOVE_NOSOURCE'}{'on'} = '';
$checked{'REMOVE_NOSOURCE'}{$xlratorsettings{'REMOVE_NOSOURCE'}} = "checked='checked'";
$checked{'REMOVE_OUTDATED'}{'off'} = '';
$checked{'REMOVE_OUTDATED'}{'on'} = '';
$checked{'REMOVE_OUTDATED'}{$xlratorsettings{'REMOVE_OUTDATED'}} = "checked='checked'";
$checked{'REMOVE_OBSOLETE'}{'off'} = '';
$checked{'REMOVE_OBSOLETE'}{'on'} = '';
$checked{'REMOVE_OBSOLETE'}{$xlratorsettings{'REMOVE_OBSOLETE'}} = "checked='checked'";


$selected{'AUTOCHECK_SCHEDULE'}{'daily'} = '';
$selected{'AUTOCHECK_SCHEDULE'}{'weekly'} = '';
$selected{'AUTOCHECK_SCHEDULE'}{'monthly'} = '';
$selected{'AUTOCHECK_SCHEDULE'}{$xlratorsettings{'AUTOCHECK_SCHEDULE'}} = "selected='selected'";

$selected{'NOT_ACCESSED_LAST'}{'week'} = '';
$selected{'NOT_ACCESSED_LAST'}{'month1'} = '';
$selected{'NOT_ACCESSED_LAST'}{'month3'} = '';
$selected{'NOT_ACCESSED_LAST'}{'month6'} = '';
$selected{'NOT_ACCESSED_LAST'}{'year'} = '';
$selected{'NOT_ACCESSED_LAST'}{$xlratorsettings{'NOT_ACCESSED_LAST'}} = "selected='selected'";

# ----------------------------------------------------
#    Settings dialog
# ----------------------------------------------------

&Header::showhttpheaders();

&Header::openpage($Lang::tr{'updxlrtr configuration'}, 1, '');

&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<font class='base'>$errormessage&nbsp;</font>\n";
	&Header::closebox();
}

print "<form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>\n";

&Header::openbox('100%', 'left', "$Lang::tr{'updxlrtr update accelerator'}");

print <<END
<table width='100%'>
<tr>
        <td colspan='4'><b>$Lang::tr{'updxlrtr common settings'}</b></td>
</tr>
<tr>
	<td class='base' width='25%'>$Lang::tr{'updxlrtr enable log'}:</td>
	<td class='base' width='20%'><input type='checkbox' name='ENABLE_LOG' $checked{'ENABLE_LOG'}{'on'} /></td>
	<td class='base' width='25%'></td>
	<td class='base' width='30%'></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'updxlrtr passive mode'}:</td>
	<td class='base'><input type='checkbox' name='PASSIVE_MODE' $checked{'PASSIVE_MODE'}{'on'} /></td>
	<td class='base'>$Lang::tr{'updxlrtr max disk usage'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
	<td class='base'><input type='text' name='MAX_DISK_USAGE' value='$xlratorsettings{'MAX_DISK_USAGE'}' size='1' /> %</td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
        <td colspan='4'><b>$Lang::tr{'updxlrtr performance options'}</b></td>
</tr>
<tr>
	<td class='base' width='25%'>$Lang::tr{'updxlrtr low download priority'}:</td>
	<td class='base' width='20%'><input type='checkbox' name='LOW_DOWNLOAD_PRIORITY' $checked{'LOW_DOWNLOAD_PRIORITY'}{'on'} /></td>
	<td class='base' width='25%'>$Lang::tr{'updxlrtr max download rate'}:</td>
	<td class='base' width='30%'><input type='text' name='MAX_DOWNLOAD_RATE' value='$xlratorsettings{'MAX_DOWNLOAD_RATE'}' size='5' /></td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
        <td colspan='4'><b>$Lang::tr{'updxlrtr source checkup'}</b></td>
</tr>
<tr>
	<td class='base' width='25%'>$Lang::tr{'updxlrtr enable autocheck'}:</td>
	<td class='base' width='20%'><input type='checkbox' name='ENABLE_AUTOCHECK' $checked{'ENABLE_AUTOCHECK'}{'on'} /></td>
	<td class='base' width='25%'>$Lang::tr{'updxlrtr source checkup schedule'}:</td>
	<td class='base' width='30%'>
	<select name='AUTOCHECK_SCHEDULE'>
	<option value='daily' $selected{'AUTOCHECK_SCHEDULE'}{'daily'}>$Lang::tr{'updxlrtr daily'}</option>
	<option value='weekly' $selected{'AUTOCHECK_SCHEDULE'}{'weekly'}>$Lang::tr{'updxlrtr weekly'}</option>
	<option value='monthly' $selected{'AUTOCHECK_SCHEDULE'}{'monthly'}>$Lang::tr{'updxlrtr monthly'}</option>
	</select>
	</td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'updxlrtr full autosync'}:</td>
	<td class='base'><input type='checkbox' name='FULL_AUTOSYNC' $checked{'FULL_AUTOSYNC'}{'on'} /></td>
	<td>&nbsp;</td>
	<td>&nbsp;</td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
	<td align='center' width='20%'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
	<td align='center' width='20%'><input type='submit' name='ACTION' value='$Lang::tr{'updxlrtr save and restart'}' /></td>
	<td>&nbsp;</td>
END
;

print"	<td align='center' width='20%'><input type='submit' name='ACTION' value='$Lang::tr{'updxlrtr statistics'}";
if ($xlratorsettings{'EXTENDED_GUI'} eq 'statistics') { print " <<' "; } else { print " >>' "; }
print "/></td>\n";

print" 	<td align='center' width='20%'><input type='submit' name='ACTION' value='$Lang::tr{'updxlrtr maintenance'}";
if ($xlratorsettings{'EXTENDED_GUI'} eq 'maintenance') { print " <<' "; } else { print " >>' "; }
print "/></td>\n";

print <<END
</tr>
</table>
END
;

&Header::closebox();

print "</form>\n";

# ----------------------------------------------------
#   List pending downloads - if any
# ----------------------------------------------------

if (($xlratorsettings{'EXTENDED_GUI'} ne 'statistics') && ($xlratorsettings{'EXTENDED_GUI'} ne 'maintenance'))
{
	@downloadlist = <$repository/download/*>;

	undef(@downloadfiles);
	foreach (@downloadlist)
	{
		if (-d)
		{
			my @filelist = <$_/*>;
			$vendorid = substr($_,rindex($_,"/")+1);
			foreach(@filelist)
			{
				next if(/\.info$/);
				$updatefile = substr($_,rindex($_,"/")+1);
				$updatefile .= ":download/$vendorid/$updatefile";
				$updatefile = " ".$updatefile;
				push(@downloadfiles, $updatefile);
			}
		}
	}

	if (@downloadfiles)
	{
		&Header::openbox('100%', 'left', "$Lang::tr{'updxlrtr pending downloads'}");

		print <<END
<table>
	<tr><td class='boldbase'><b>$Lang::tr{'updxlrtr current downloads'}</b></td></tr>
</table>
<table width='100%'>
<colgroup span='3' width='2%'></colgroup>
<colgroup span='1' width='0*'></colgroup>
<colgroup span='3' width='5%'></colgroup>
<colgroup span='1' width='2%'></colgroup>
<tr>
	<td class='base' align='center'>&nbsp;</td>
	<td class='base' align='left' colspan='2'><i>$Lang::tr{'updxlrtr source'}</i></td>
	<td class='base' align='center'><i>$Lang::tr{'updxlrtr filename'}</i></td>
	<td class='base' align='center'><i>$Lang::tr{'updxlrtr filesize'}</i></td>
	<td class='base' align='center'><i>$Lang::tr{'date'}</i></td>
	<td class='base' align='center'><i>$Lang::tr{'updxlrtr progress'}</i></td>
	<td class='base' align='center'>&nbsp;</td>
</tr>
END
;
		$id = 0;
		foreach $updatefile (@downloadfiles)
		{
			$updatefile =~ s/.*:download/download/;
			my $size_updatefile = 0;
			my $mtime = 0;
			if(-e "$repository/$updatefile") {
				$size_updatefile = (-s "$repository/$updatefile");
				$mtime = &getmtime("$repository/$updatefile");
			}
			if (-e "$repository/$updatefile.info") {
				&General::readhash("$repository/$updatefile.info", \%dlinfo);
			} else {
				undef(%dlinfo);
			}

			$id++;
			if ($id % 2) {
				print "<tr bgcolor='$Header::table1colour'>\n"; }
			else {
				print "<tr bgcolor='$Header::table2colour'>\n"; }

			$filesize = $size_updatefile;
			1 while $filesize =~ s/^(-?\d+)(\d{3})/$1.$2/;

			my ($SECdt,$MINdt,$HOURdt,$DAYdt,$MONTHdt,$YEARdt) = localtime($mtime);
			$DAYdt   = sprintf ("%.02d",$DAYdt);
			$MONTHdt = sprintf ("%.02d",$MONTHdt+1);
			$YEARdt  = sprintf ("%.04d",$YEARdt+1900);
			$filedate = $YEARdt."-".$MONTHdt."-".$DAYdt;

			($uuid,$vendorid,$shortname) = split('/',$updatefile);

		print "\t\t<td align='center' nowrap='nowrap'>&nbsp;";
		if (&getPID("\\s/usr/bin/wget\\s.*\\s".quotemeta($dlinfo{'SRCURL'})."\$"))
		{
			print "<img src='/images/updbooster/updxl-led-blue.gif' alt='$Lang::tr{'updxlrtr condition download'}' />&nbsp;</td>\n";
		} else {
			print "<img src='/images/updbooster/updxl-led-gray.gif' alt='$Lang::tr{'updxlrtr condition suspended'}' />&nbsp;</td>\n";
		}

		print "\t\t<td align='center' nowrap='nowrap'>&nbsp;";

		if (($vendorid ne '') && (-e "$webhome/images/updbooster/updxl-src-$vendorid.gif"))
		{
			print "<img src='/images/updbooster/updxl-src-" . $vendorid . ".gif' alt='" . ucfirst $vendorid . "' />&nbsp;</td>\n";
		} else {
			print "<img src='/images/updbooster/updxl-src-unknown.gif' alt='" . ucfirst $vendorid . "' />&nbsp;</td>\n";
		}

		$shortname = substr($updatefile,rindex($updatefile,"/")+1);
		$shortname =~ s/(.*)_[\da-f]*(\.(exe|cab|psf)$)/$1_*$2/i;

		$filesize = $dlinfo{'REMOTESIZE'};
		1 while $filesize =~ s/^(-?\d+)(\d{3})/$1.$2/;
		$dlinfo{'VENDORID'} = ucfirst $vendorid;

		print <<END
		<td class='base' align='center'>&nbsp;$dlinfo{'VENDORID'}&nbsp;</td>
		<td class='base' align='left' title='cache:/$updatefile'>$shortname</td>
		<td class='base' align='right'  nowrap='nowrap'>&nbsp;$filesize&nbsp;</td>
		<td class='base' align='center' nowrap='nowrap'>&nbsp;$filedate&nbsp;</td>
		<td class='base' align='center' nowrap='nowrap'>
END
;
			my $percent="0%";
			if ($dlinfo{'REMOTESIZE'} && $size_updatefile)
			{
				$percent=int(100 / ($dlinfo{'REMOTESIZE'} / $size_updatefile))."%";
			}
			print $percent; &percentbar($percent);
			print <<END
		</td>
		<td align='center'>
		<form method='post' name='frma$id' action='$ENV{'SCRIPT_NAME'}'>
		<input type='image' name='$Lang::tr{'updxlrtr cancel download'}' src='/images/delete.gif' title='$Lang::tr{'updxlrtr cancel download'}' alt='$Lang::tr{'updxlrtr cancel download'}' />
		<input type='hidden' name='ID' value='$updatefile' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'updxlrtr cancel download'}' />
		</form>
		</td>
	</tr>
END
;
		}

		print "</table>\n<br>\n<table>\n";
		&printlegenddownload();
		print "</table>\n";

		&Header::closebox();
	}
}
# =====================================================================================
#  CACHE STATISTICS
# =====================================================================================

if ($xlratorsettings{'EXTENDED_GUI'} eq 'statistics')
{

# ----------------------------------------------------
#    Get statistics
# ----------------------------------------------------

@sources=();
foreach (<$repository/*>)
{
	if (-d $_)
	{
		unless ((/^$repository\/download$/) || (/^$repository\/lost\+found$/)) { push(@sources,$_); }
	}
}

@vendors=();
foreach (@sources)
{
	$vendorid=substr($_,rindex($_,'/')+1,length($_));
	push(@vendors,$vendorid);
	$vendorstats{$vendorid."_filesize"} = 0;
	$vendorstats{$vendorid."_requests"} = 0;
	$vendorstats{$vendorid."_files"} = 0;
	$vendorstats{$vendorid."_cachehits"} = 0;
	$vendorstats{$vendorid."_0"} = 0;
	$vendorstats{$vendorid."_1"} = 0;
	$vendorstats{$vendorid."_2"} = 0;
	$vendorstats{$vendorid."_3"} = 0;
	@updatelist=<$_/*>;
	foreach $data (@updatelist)
	{
		if (-e "$data/source.url")
		{
			open (FILE,"$data/source.url");
			$sourceurl=<FILE>;
			close FILE;
			chomp($sourceurl);
			$updatefile = substr($sourceurl,rindex($sourceurl,'/')+1,length($sourceurl));

			my $size_updatefile = 0;
			if(-e "$data/$updatefile") {
				$size_updatefile = (-s "$data/$updatefile");
			}
			else
			{
				# DEBUG
				#die "file not found: $data/$updatefile\n";
			}
		#
		# Total file size
		#
			$filesize += $size_updatefile;
		#
		# File size for this source
		#
			$vendorstats{$vendorid."_filesize"} += $size_updatefile;
		#
		# Number of requests from cache for this source
		#
			open (FILE,"$data/access.log");
			@requests=<FILE>;
			close FILE;
			chomp(@requests);
			$counts = @requests;
			$counts--;
			$vendorstats{$vendorid."_requests"} += $counts;
			$cachehits += $counts;
		#
		# Total number of files in cache
		#
			$numfiles++;
		#
		# Number of files for this source
		#
			$vendorstats{$vendorid."_files"}++;
		#
		# Count cache status occurences
		#
			open (FILE,"$data/status");
			$_=<FILE>;
			close FILE;
			chomp;
			$vendorstats{$vendorid."_".$_}++;
		#
		# Calculate cached traffic for this source
		#
			$vendorstats{$vendorid."_cachehits"} += $counts * $size_updatefile;
		#
		# Calculate total cached traffic
		#
			$cachedtraffic += $counts * $size_updatefile;

		}
	}
}

if ($numfiles) { $efficiency = sprintf("%.1f", $cachehits / $numfiles); }

1 while $filesize =~ s/^(-?\d+)(\d{3})/$1.$2/;
1 while $cachedtraffic =~ s/^(-?\d+)(\d{3})/$1.$2/;

# ----------------------------------------------------
#    Show statistics
# ----------------------------------------------------

&Header::openbox('100%', 'left', "$Lang::tr{'updxlrtr cache statistics'}");

unless ($numfiles) { print "<i>$Lang::tr{'updxlrtr empty repository'}</i>\n<hr size='1'>\n"; }

print <<END
<table>
<tr><td class='boldbase'><b>$Lang::tr{'updxlrtr disk usage'}</b></td></tr>
</table>
<table cellpadding='3'>
<tr>
<td align='left' class='base'><i>$Lang::tr{'updxlrtr cache dir'}</i></td>
<td align='center' class='base'><i>$Lang::tr{'size'}</i></td>
<td align='center' class='base'><i>$Lang::tr{'used'}</i></td>
<td align='center' class='base'><i>$Lang::tr{'free'}</i></td>
<td align='left' class='base' colspan='2'><i>$Lang::tr{'percentage'}</i></td>
</tr>
END
;

open(DF,"/bin/df -h $repository|");
@dfdata = <DF>;
close DF;
shift(@dfdata);
chomp(@dfdata);
$dfstr = join(' ',@dfdata);
my ($device,$size,$used,$free,$percent,$mount) = split(' ',$dfstr);

print <<END
<tr>
<td>[$repository]</td>
<td align='right'>$size</td>
<td align='right'>$used</td>
<td align='right'>$free</td>
<td>
END
;
&percentbar($percent);
print <<END
</td>
<td align='right'>$percent</td>
</tr>
</table>
END
;

if ($numfiles)
{
	print <<END
<hr size='1'>
<table width='100%'>
<tr>
        <td colspan='5'><b>$Lang::tr{'updxlrtr summary'}</b></td>
</tr>
<tr>
	<td class='base' width='25%'>$Lang::tr{'updxlrtr total files'}:</td>
	<td class='base' width='20%'><font color='$colourgray'>$numfiles</font></td>
	<td class='base' width='25%'>$Lang::tr{'updxlrtr total cache size'}:</td>
	<td class='base' width='15%' align='right'><font color='$colourgray'>$filesize</font></td>
	<td class='base'></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'updxlrtr efficiency index'}:</td>
	<td class='base'><font color='$colourgray'>$efficiency</font></td>
	<td class='base'>$Lang::tr{'updxlrtr total data from cache'}:</td>
	<td class='base' align='right'><font color='$colourgray'>$cachedtraffic</font></td>
	<td class='base'></td>
</tr>
</table>
<hr size='1'>
<table>
<tr>
        <td colspan='17'><b>$Lang::tr{'updxlrtr statistics by source'}</b></td>
</tr>
<tr>
	<td class='base' colspan='2'><i>$Lang::tr{'updxlrtr source'}</i></td>
	<td class='base' width='7%'>&nbsp;</td>
	<td class='base' align='right'><i>$Lang::tr{'updxlrtr files'}</i></td>
	<td class='base' width='7%'>&nbsp;</td>
	<td class='base' align='right'><nobr><i>$Lang::tr{'updxlrtr cache size'}</i></nobr></td>
	<td class='base' width='7%'>&nbsp;</td>
	<td class='base' align='right'><nobr><i>$Lang::tr{'updxlrtr data from cache'}</i></nobr></td>
	<td class='base' width='15%'>&nbsp;</td>
	<td class='base'><img src="/images/updbooster/updxl-led-green.gif" /></td>
	<td class='base' width='15%'>&nbsp;</td>
	<td class='base'><img src="/images/updbooster/updxl-led-yellow.gif" /></td>
	<td class='base' width='15%'>&nbsp;</td>
	<td class='base'><img src="/images/updbooster/updxl-led-red.gif" /></td>
	<td class='base' width='15%'>&nbsp;</td>
	<td class='base'><img src="/images/updbooster/updxl-led-gray.gif" /></td>
	<td class='base' width='90%'>&nbsp;</td>
</tr>
END
;

$id = 0;

foreach (@vendors)
{
	$vendorid = $_;

	unless ($vendorstats{$vendorid . "_files"}) { next; }

	$id++;
	if ($id % 2) {
		print "<tr bgcolor=''$color{'color20'}'>\n"; }
	else {
		print "<tr bgcolor=''$color{'color22'}'>\n"; }

	print "<td class='base' align='center'><nobr>&nbsp;";

	if ($vendorid =~ /^Adobe$/i)
	{
		print "<img src='/images/updbooster/updxl-src-adobe.gif' alt='Adobe'}' />&nbsp;</nobr></td>\n";
		print "<td class='base'>&nbsp;Adobe&nbsp;</td>\n";
	} elsif ($vendorid =~ /^Microsoft$/i)
	{
		print "<img src='/images/updbooster/updxl-src-windows.gif' alt='Microsoft'}' />&nbsp;</nobr></td>\n";
		print "<td class='base'>&nbsp;Microsoft&nbsp;</td>\n";
	} elsif ($vendorid =~ /^Symantec$/i)
	{
		print "<img src='/images/updbooster/updxl-src-symantec.gif' alt='Symantec'}' />&nbsp;</nobr></td>\n";
		print "<td class='base'>&nbsp;Symantec&nbsp;</td>\n";
	} elsif ($vendorid =~ /^Linux$/i)
	{
		print "<img src='/images/updbooster/updxl-src-linux.gif' alt='Linux'}' />&nbsp;</nobr></td>\n";
		print "<td class='base'>&nbsp;Linux&nbsp;</td>\n";
	} elsif ($vendorid =~ /^TrendMicro$/i)
	{
		print "<img src='/images/updbooster/updxl-src-trendmicro.gif' alt='Trend Micro'}' />&nbsp;</nobr></td>\n";
		print "<td class='base'>&nbsp;Trend&nbsp;Micro&nbsp;</td>\n";
	} elsif ($vendorid =~ /^Apple$/i)
	{
		print "<img src='/images/updbooster/updxl-src-apple.gif' alt='Apple'}' />&nbsp;</nobr></td>\n";
		print "<td class='base'>&nbsp;Apple&nbsp;</td>\n";
	} elsif ($vendorid =~ /^Avast$/i)
	{
	 	print "<img src='/images/updbooster/updxl-src-avast.gif' alt='Avast'}' />&nbsp;</nobr></td>\n";
		print "<td class='base'>&nbsp;Avast&nbsp;</td>\n";
  } elsif ($vendorid =~ /^Avira$/i)
	{
		print "<img src='/images/updbooster/updxl-src-avira.gif' alt='Avira' />&nbsp;</td>\n";
		print "<td class='base'>&nbsp;Avira&nbsp;</td>\n";
	} elsif ($vendorid =~ /^AVG$/i)
	{
		print "<img src='/images/updbooster/updxl-src-avg.gif' alt='AVG' />&nbsp;</td>\n";
		print "<td class='base'>&nbsp;AVG&nbsp;</td>\n";
	} elsif ($vendorid =~ /^Ipfire$/i)
	{
		print "<img src='/images/IPFire.png' width='18' height='18' alt='IPFire' />&nbsp;</td>\n";
		print "<td class='base'>&nbsp;IPFire&nbsp;</td>\n";
	} else
	{
		if (-e "/srv/web/ipfire/html/images/updbooster/updxl-src-" . $vendorid . ".gif")
		{
			print "<img src='/images/updbooster/updxl-src-" . $vendorid . ".gif' alt='" . ucfirst $vendorid . "' />&nbsp;</nobr></td>\n";
		} else {
			print "<img src='/images/updbooster/updxl-src-unknown.gif' alt='" . ucfirst $vendorid . "' />&nbsp;</nobr></td>\n";
		}
		print "<td class='base'>&nbsp;" . ucfirst $vendorid . "&nbsp;</td>\n";
	}

	print "<td class='base' colspan=2 align='right'>";
	printf "%5d", $vendorstats{$vendorid."_files"};
	print "&nbsp;</td>\n";

	unless ($vendorstats{$vendorid."_filesize"}) { $vendorstats{$vendorid."_filesize"} = '0'; }
	1 while $vendorstats{$vendorid."_filesize"} =~ s/^(-?\d+)(\d{3})/$1.$2/;
	print "<td class='base' colspan=2 align='right'>";
	printf "%15s", $vendorstats{$vendorid."_filesize"};
	print "&nbsp;</td>\n";

	unless ($vendorstats{$vendorid."_cachehits"}) { $vendorstats{$vendorid."_cachehits"} = '0'; }
	1 while $vendorstats{$vendorid."_cachehits"} =~ s/^(-?\d+)(\d{3})/$1.$2/;
	print "<td class='base' colspan=2 align='right'>";
	printf "%15s", $vendorstats{$vendorid."_cachehits"};
	print "&nbsp;</td>\n";

	print "<td class='base' colspan=2 align='right'>";
	printf "%5d", $vendorstats{$vendorid."_1"};
	print "&nbsp;&nbsp;</td>\n";

	print "<td class='base' colspan=2 align='right'>";
	printf "%5d", $vendorstats{$vendorid."_3"};
	print "&nbsp;&nbsp;</td>\n";

	print "<td class='base' colspan=2 align='right'>";
	printf "%5d", $vendorstats{$vendorid."_2"};
	print "&nbsp;&nbsp;</td>\n";

	print "<td class='base' colspan=2 align='right'>";
	printf "%5d", $vendorstats{$vendorid."_0"};
	print "&nbsp;&nbsp;</td>\n";

	print "<td class='base'>&nbsp;</td>\n";
	print "</tr>\n";
}

print "</table>\n";

print <<END
<br>
<table>
	<tr>
		<td class='boldbase'>&nbsp; <b>$Lang::tr{'legend'}:</b></td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updbooster/updxl-led-green.gif' alt='$Lang::tr{'updxlrtr condition ok'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr condition ok'}</td>
		<td class='base'>&nbsp;&nbsp;&nbsp;</td>
		<td align='center'><img src='/images/updbooster/updxl-led-yellow.gif' alt='$Lang::tr{'updxlrtr condition nosource'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr condition nosource'}</td>
		<td class='base'>&nbsp;&nbsp;&nbsp;</td>
		<td align='center'><img src='/images/updbooster/updxl-led-red.gif' alt='$Lang::tr{'updxlrtr condition outdated'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr condition outdated'}</td>
		<td class='base'>&nbsp;&nbsp;&nbsp;</td>
		<td align='center'><img src='/images/updbooster/updxl-led-gray.gif' alt='$Lang::tr{'updxlrtr condition unknown'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr condition unknown'}</td>
		<td class='base'>&nbsp;&nbsp;&nbsp;</td>
	</tr>
</table>
END
;

}

&Header::closebox();

}

# =====================================================================================
#  CACHE MAINTENANCE
# =====================================================================================

if ($xlratorsettings{'EXTENDED_GUI'} eq 'maintenance')
{


# ----------------------------------------------------
#    File list dialog
# ----------------------------------------------------

&Header::openbox('100%', 'left', "$Lang::tr{'updxlrtr cache maintenance'}");

@sources= <$repository/download/*>;

undef @repositoryfiles;
foreach (@sources)
{
	if (-d)
	{
		@updatelist = <$_/*>;
		$vendorid = substr($_,rindex($_,"/")+1);
		foreach(@updatelist)
		{
			next if(/\.info$/);
			$updatefile = substr($_,rindex($_,"/")+1);
			$_ = $updatefile; tr/[A-Z]/[a-z]/;
			$updatefile = "$_:separator:download/$vendorid/$updatefile";
			$updatefile = " ".$updatefile;
			push(@repositoryfiles,$updatefile);
		}
	}
}

undef (@sources);
foreach (<$repository/*>)
{
	if (-d $_)
{
		unless (/^$repository\/download$/) { push(@sources,$_); }
	}
}

foreach (@sources)
{
	@updatelist=<$_/*>;
	$vendorid = substr($_,rindex($_,"/")+1);
	foreach(@updatelist)
	{
		$uuid = substr($_,rindex($_,"/")+1);
		if (-e "$_/source.url")
		{
			open (FILE,"$_/source.url");
			$sourceurl=<FILE>;
			close FILE;
			chomp($sourceurl);
			$updatefile = substr($sourceurl,rindex($sourceurl,'/')+1,length($sourceurl));
			$_ = $updatefile; tr/[A-Z]/[a-z]/;
			$updatefile = "$_:separator:$vendorid/$uuid/$updatefile";
			push(@repositoryfiles,$updatefile);
		}
	}
}

@repositoryfiles = sort(@repositoryfiles);

unless (@repositoryfiles) { print "<i>$Lang::tr{'updxlrtr empty repository'}</i>\n<hr size='1'>\n"; }

print <<END
<table>
<tr><td class='boldbase'><b>$Lang::tr{'updxlrtr disk usage'}</b></td></tr>
</table>
<table cellpadding='3'>
<tr>
<td align='left' class='base'><i>$Lang::tr{'updxlrtr cache dir'}</i></td>
<td align='center' class='base'><i>$Lang::tr{'size'}</i></td>
<td align='center' class='base'><i>$Lang::tr{'used'}</i></td>
<td align='center' class='base'><i>$Lang::tr{'free'}</i></td>
<td align='left' class='base' colspan='2'><i>$Lang::tr{'percentage'}</i></td>
</tr>
END
;

open(DF,"/bin/df -h $repository|");
@dfdata = <DF>;
close DF;
shift(@dfdata);
chomp(@dfdata);
$dfstr = join(' ',@dfdata);
my ($device,$size,$used,$free,$percent,$mount) = split(' ',$dfstr);

print <<END
<tr>
<td>[$repository]</td>
<td align='right'>$size</td>
<td align='right'>$used</td>
<td align='right'>$free</td>
<td>
END
;
&percentbar($percent);
print <<END
</td>
<td align='right'>$percent</td>
</tr>
</table>
END
;

if (@repositoryfiles)
{
	print <<END
<hr size='1'>
<form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>
<table width='100%'>
<tr>
	<td class='base' colspan='3'><input type='submit' name='ACTION' value='$Lang::tr{'updxlrtr purge'}' /> &nbsp;$Lang::tr{'updxlrtr all files'}</td>
	<td class='base' width='25%'>
		<input type='checkbox' name='REMOVE_OBSOLETE' $checked{'REMOVE_OBSOLETE'}{'on'} />&nbsp;$Lang::tr{'updxlrtr not accessed'}
	</td>
	<td class='base' colspan='3'>
		<select name='NOT_ACCESSED_LAST'>
			<option value='week'   $selected{'NOT_ACCESSED_LAST'}{'week'}>$Lang::tr{'updxlrtr week'}</option>
			<option value='month1' $selected{'NOT_ACCESSED_LAST'}{'month1'}>$Lang::tr{'updxlrtr month'}</option>
			<option value='month3' $selected{'NOT_ACCESSED_LAST'}{'month3'}>$Lang::tr{'updxlrtr 3 months'}</option>
			<option value='month6' $selected{'NOT_ACCESSED_LAST'}{'month6'}>$Lang::tr{'updxlrtr 6 months'}</option>
			<option value='year'   $selected{'NOT_ACCESSED_LAST'}{'year'}>$Lang::tr{'updxlrtr year'}</option>
		</select>
	</td>
</tr>
<tr>
</tr>
<tr>
	<td class='base' width='25%'>
		<input type='checkbox' name='REMOVE_NOSOURCE' $checked{'REMOVE_NOSOURCE'}{'on'} />&nbsp;$Lang::tr{'updxlrtr marked as'}
	</td>
	<td class='base' width='3%'><img src='/images/updbooster/updxl-led-yellow.gif' alt='$Lang::tr{'updxlrtr condition nosource'}' /></td>
	<td class='base' width='17%'>[<i>$Lang::tr{'updxlrtr condition nosource'}</i>]</td>
	<td class='base' width='25%'>
		<input type='checkbox' name='REMOVE_OUTDATED' $checked{'REMOVE_OUTDATED'}{'on'} />&nbsp;$Lang::tr{'updxlrtr marked as'}
	</td>
	<td class='base' width='3%'><img src='/images/updbooster/updxl-led-red.gif' alt='$Lang::tr{'updxlrtr condition outdated'}' /></td>
	<td class='base' width='27%'>[<i>$Lang::tr{'updxlrtr condition outdated'}</i>]</td>
</tr>
</table>
</form>
<hr size='1'>
END
;

	&printcurrentfiles($Lang::tr{'updxlrtr current files'}, @repositoryfiles);
	print "<br>\n<table>\n";
	&printlegendicons();
	&printlegendspacer();
	&printlegendstatus();
	&printlegendspacer();
	&printlegendsource();
	print "</table>\n";
}

&Header::closebox();

}

# =====================================================================================

&Header::closebigbox();

&Header::closepage();

# -------------------------------------------------------------------

sub printcurrentfiles
{
	my $title = shift;
	my @files = @_;

	print <<END
<table>
<tr><td class='boldbase'><b>$Lang::tr{'updxlrtr current files'}</b></td></tr>
</table>
<table width='100%'>
<colgroup span='2' width='2%'></colgroup>
<colgroup span='1' width='0*'></colgroup>
<colgroup span='4' width='5%'></colgroup>
<colgroup span='1' width='2%'></colgroup>
<tr>
	<td class='base' align='center'>&nbsp;</td>
	<td class='base' align='center'>&nbsp;</td>
	<td class='base' align='center'><i>$Lang::tr{'updxlrtr filename'}</i></td>
	<td class='base' align='center'><i>$Lang::tr{'updxlrtr filesize'}</i></td>
	<td class='base' align='center'><i>$Lang::tr{'date'}</i></td>
	<td class='base' align='center'><img src='/images/reload.gif' alt='$Lang::tr{'updxlrtr last access'}' /></td>
	<td class='base' align='center'><img src='/images/updbooster/updxl-globe.gif' alt='$Lang::tr{'updxlrtr last checkup'}' /></td>
	<td class='base' align='center'>&nbsp;</td>
</tr>
END
;
	$id = 0;
	foreach $updatefile (@files)
	{
		$updatefile =~ s/.*:separator://;
		my $size_updatefile = 0;
		my $mtime = 0;
		if(-e "$repository/$updatefile") {
			$size_updatefile = (-s "$repository/$updatefile");
			$mtime = &getmtime("$repository/$updatefile");
		}

		$id++;
		if ($id % 2) {
			print "<tr bgcolor='$Header::table1colour'>\n"; }
		else {
			print "<tr bgcolor='$Header::table2colour'>\n"; }

		$filesize = $size_updatefile;
		1 while $filesize =~ s/^(-?\d+)(\d{3})/$1.$2/;

		my ($SECdt,$MINdt,$HOURdt,$DAYdt,$MONTHdt,$YEARdt) = localtime($mtime);
		$DAYdt   = sprintf ("%.02d",$DAYdt);
		$MONTHdt = sprintf ("%.02d",$MONTHdt+1);
		$YEARdt  = sprintf ("%.04d",$YEARdt+1900);
		$filedate = $YEARdt."-".$MONTHdt."-".$DAYdt;

		$lastaccess = "n/a";
		$lastcheck  = "n/a";

		$status = $sfUnknown;

		unless ($updatefile =~ /^download\//)
		{
			($vendorid,$uuid,$shortname) = split('/',$updatefile);

			if (-e "$repository/$vendorid/$uuid/access.log")
			{
				open (FILE,"$repository/$vendorid/$uuid/access.log");
				@metadata = <FILE>;
				close(FILE);
				chomp @metadata;

				($SECdt,$MINdt,$HOURdt,$DAYdt,$MONTHdt,$YEARdt) = localtime($metadata[-1]);
				$DAYdt   = sprintf ("%.02d",$DAYdt);
				$MONTHdt = sprintf ("%.02d",$MONTHdt+1);
				$YEARdt  = sprintf ("%.04d",$YEARdt+1900);
				if (($metadata[-1] =~ /^\d+/) && ($metadata[-1] >= 1)) { $lastaccess = $YEARdt."-".$MONTHdt."-".$DAYdt; }
			}
			if (-e "$repository/$vendorid/$uuid/checkup.log")
			{
				open (FILE,"$repository/$vendorid/$uuid/checkup.log");
				@metadata = <FILE>;
				close(FILE);
				chomp @metadata;

				($SECdt,$MINdt,$HOURdt,$DAYdt,$MONTHdt,$YEARdt) = localtime($metadata[-1]);
				$DAYdt   = sprintf ("%.02d",$DAYdt);
				$MONTHdt = sprintf ("%.02d",$MONTHdt+1);
				$YEARdt  = sprintf ("%.04d",$YEARdt+1900);
				if (($metadata[-1] =~ /^\d+/) && ($metadata[-1] >= 1)) { $lastcheck = $YEARdt."-".$MONTHdt."-".$DAYdt; }
			}
			if (-e "$repository/$vendorid/$uuid/status")
			{
				open (FILE,"$repository/$vendorid/$uuid/status");
				@metadata = <FILE>;
				close(FILE);
				chomp @metadata;
				$status = $metadata[-1];
			}
		} else {
			($uuid,$vendorid,$shortname) = split('/',$updatefile);
			$status = $sfOutdated;
		}

		print "\t\t<td align='center' nowrap='nowrap'>&nbsp;";
		if ($status == $sfUnknown)
		{
			print "<img src='/images/updbooster/updxl-led-gray.gif' alt='$Lang::tr{'updxlrtr condition unknown'}' />&nbsp;</td>\n";
		}
		if ($status == $sfOk)
		{
			print "<img src='/images/updbooster/updxl-led-green.gif' alt='$Lang::tr{'updxlrtr condition ok'}' />&nbsp;</td>\n";
		}
		if ($status == $sfNoSource)
		{
			print "<img src='/images/updbooster/updxl-led-yellow.gif' alt='$Lang::tr{'updxlrtr condition nosource'}' />&nbsp;</td>\n";
		}
		if (($status == $sfOutdated) && (!($updatefile =~ /^download\//i)))
		{
			print "<img src='/images/updbooster/updxl-led-red.gif' alt='$Lang::tr{'updxlrtr condition outdated'}' />&nbsp;</td>\n";
		}
		if (($status == $sfOutdated) && ($updatefile =~ /^download\//i))
		{
			print "<img src='/images/updbooster/updxl-led-blue.gif' alt='$Lang::tr{'updxlrtr condition download'}' />&nbsp;</td>\n";
		}

		print "\t\t<td align='center' nowrap='nowrap'>&nbsp;";
		if ($vendorid =~ /^Adobe$/i)
		{
			print "<img src='/images/updbooster/updxl-src-adobe.gif' alt='Adobe'}' />&nbsp;</td>\n";
		} elsif ($vendorid =~ /^Microsoft$/i)
		{
			print "<img src='/images/updbooster/updxl-src-windows.gif' alt='Microsoft'}' />&nbsp;</td>\n";
		} elsif ($vendorid =~ /^Symantec$/i)
		{
			print "<img src='/images/updbooster/updxl-src-symantec.gif' alt='Symantec'}' />&nbsp;</td>\n";
		} elsif ($vendorid =~ /^Linux$/i)
		{
			print "<img src='/images/updbooster/updxl-src-linux.gif' alt='Linux'}' />&nbsp;</td>\n";
		} elsif ($vendorid =~ /^TrendMicro$/i)
		{
			print "<img src='/images/updbooster/updxl-src-trendmicro.gif' alt='Trend Micro'}' />&nbsp;</td>\n";
		} elsif ($vendorid =~ /^Apple$/i)
		{
			print "<img src='/images/updbooster/updxl-src-apple.gif' alt='Apple'}' />&nbsp;</td>\n";
		} elsif ($vendorid =~ /^Avast$/i)
		{
			print "<img src='/images/updbooster/updxl-src-avast.gif' alt='Avast'}' />&nbsp;</td>\n";
  	} elsif ($vendorid =~ /^Avira$/i)
		{
			print "<img src='/images/updbooster/updxl-src-avira.gif' alt='Avira' />&nbsp;</td>\n";
		} elsif ($vendorid =~ /^AVG$/i)
		{
			print "<img src='/images/updbooster/updxl-src-avg.gif' alt='AVG' />&nbsp;</td>\n";
		} elsif ($vendorid =~ /^Ipfire$/i)
		{
			print "<img src='/images/IPFire.png' width='18' height='18' alt='IPFire' />&nbsp;</td>\n";
		}
		else
		{
			if (-e "/srv/web/ipfire/html/images/updbooster/updxl-src-" . $vendorid . ".gif")
			{
				print "<img src='/images/updbooster/updxl-src-" . $vendorid . ".gif' alt='" . ucfirst $vendorid . "' />&nbsp;</td>\n";
			} else {
				print "<img src='/images/updbooster/updxl-src-unknown.gif' alt='" . ucfirst $vendorid . "' />&nbsp;</td>\n";
			}
		}

		$shortname = substr($updatefile,rindex($updatefile,"/")+1);
		$shortname =~ s/(.*)_[\da-f]*(\.(exe|cab|psf)$)/$1_*$2/i;

print <<END
		<td class='base' align='left' title='cache:/$updatefile'><a href="/updatecache/$updatefile">$shortname</a></td>
		<td class='base' align='right'  nowrap='nowrap'>&nbsp;$filesize&nbsp;</td>
		<td class='base' align='center' nowrap='nowrap'>&nbsp;$filedate&nbsp;</td>
		<td class='base' align='center' nowrap='nowrap'>&nbsp;$lastaccess&nbsp;</td>
		<td class='base' align='center' nowrap='nowrap'>&nbsp;$lastcheck&nbsp;</td>
		<td align='center'>
		<form method='post' name='frma$id' action='$ENV{'SCRIPT_NAME'}'>
		<input type='image' name='$Lang::tr{'updxlrtr remove file'}' src='/images/delete.gif' title='$Lang::tr{'updxlrtr remove file'}' alt='$Lang::tr{'updxlrtr remove file'}' />
		<input type='hidden' name='ID' value='$updatefile' />
		<input type='hidden' name='ACTION' value='$Lang::tr{'updxlrtr remove file'}' />
		</form>
		</td>
	</tr>
END
;
	}

	print "</table>\n";

}

# -------------------------------------------------------------------

sub printlegenddownload
{
	print <<END
	<tr>
		<td class='boldbase'>&nbsp; <b>$Lang::tr{'legend'}:</b></td>
		<td class='base'>&nbsp;</td>
		<td><img src='/images/updbooster/updxl-led-blue.gif' alt='$Lang::tr{'updxlrtr condition download'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr condition download'}</td>
		<td class='base'>&nbsp;</td>
		<td class='base'>&nbsp;</td>
		<td><img src='/images/updbooster/updxl-led-gray.gif' alt='$Lang::tr{'updxlrtr condition suspended'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr condition suspended'}</td>
		<td class='base'>&nbsp;</td>
		<td class='base'>&nbsp;</td>
		<td><img src='/images/delete.gif' alt='$Lang::tr{'updxlrtr cancel download'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr cancel download'}</td>
	</tr>
END
;
}

# -------------------------------------------------------------------

sub printlegendicons
{
	print <<END



	<tr>
		<td class='boldbase'>&nbsp; <b>$Lang::tr{'legend'}:</b></td>
		<td class='base'>&nbsp;</td>
		<td><img src='/images/reload.gif' alt='$Lang::tr{'updxlrtr last access'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr last access'}</td>
		<td class='base'>&nbsp;</td>
		<td><img src='/images/updbooster/updxl-globe.gif' alt='$Lang::tr{'updxlrtr last checkup'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr last checkup'}</td>
		<td class='base'>&nbsp;</td>
		<td><img src='/images/delete.gif' alt='$Lang::tr{'updxlrtr remove file'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr remove file'}</td>
		<td class='base'>&nbsp;</td>
		<td class='base'>&nbsp;</td>
		<td class='base'>&nbsp;</td>
	</tr>
END
;
}

# -------------------------------------------------------------------

sub printlegendstatus
{
	print <<END
	<tr>
		<td class='base'>&nbsp; $Lang::tr{'status'}:</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updbooster/updxl-led-green.gif' alt='$Lang::tr{'updxlrtr condition ok'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr condition ok'}</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updbooster/updxl-led-yellow.gif' alt='$Lang::tr{'updxlrtr condition nosource'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr condition nosource'}</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updbooster/updxl-led-red.gif' alt='$Lang::tr{'updxlrtr condition outdated'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr condition outdated'}</td>
		<td class='base'>&nbsp;</td>
		<td class='base'>&nbsp;</td>

		<td class='base'>&nbsp;</td>
	</tr>
	<tr>
		<td class='base'>&nbsp;</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updbooster/updxl-led-blue.gif' alt='$Lang::tr{'updxlrtr condition download'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr condition download'}</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updbooster/updxl-led-gray.gif' alt='$Lang::tr{'updxlrtr condition unknown'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr condition unknown'}</td>
		<td class='base'>&nbsp;</td>
		<td class='base'>&nbsp;</td>
		<td class='base'>&nbsp;</td>
		<td class='base'>&nbsp;</td>
		<td class='base'>&nbsp;</td>

		<td class='base'>&nbsp;</td>
	</tr>
END
;
}

# -------------------------------------------------------------------

sub printlegendsource
{
	print <<END
	<tr>



		<td class='base'>&nbsp; $Lang::tr{'updxlrtr source'}:</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updbooster/updxl-src-adobe.gif' alt='Adobe' /></td>
		<td class='base'>Adobe</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updbooster/updxl-src-apple.gif' alt='Apple' /></td>
		<td class='base'>Apple</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updbooster/updxl-src-avast.gif' alt='Avast' /></td>
		<td class='base'>Avast</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updbooster/updxl-src-linux.gif' alt='Linux' /></td>
		<td class='base'>Linux</td>
	</tr>
	<tr>
		<td colspan='13'></td>
	</tr>
	<tr>
		<td class='base'>&nbsp;</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updbooster/updxl-src-windows.gif' alt='Microsoft' /></td>
		<td class='base'>Microsoft</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updbooster/updxl-src-symantec.gif' alt='Symantec' /></td>
		<td class='base'>Symantec</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updbooster/updxl-src-trendmicro.gif' alt='Trend Micro' /></td>
		<td class='base'>Trend Micro</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/IPFire.png' width='18' height='18' alt='IPFire' /></td>
		<td class='base'>IPFire</td>
	</tr>
	<tr>
		<td class='base'>&nbsp;</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updbooster/updxl-src-avira.gif' alt='Avira' /></td>
		<td class='base'>Avira</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updbooster/updxl-src-avg.gif' alt='AVG' /></td>
		<td class='base'>AVG</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updbooster/updxl-src-unknown.gif' alt='$Lang::tr{'updxlrtr other'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr other'}</td>
		<td class='base'>&nbsp;</td>
		<td align='center'></td>
		<td class='base'>&nbsp;</td>
	</tr>

END
;

}

# -------------------------------------------------------------------

sub printlegendspacer
{
	print <<END
	<tr>
		<td colspan='13'>&nbsp;<br></td>
	</tr>
END
;
}

# -------------------------------------------------------------------

sub savesettings
{

	if (($xlratorsettings{'ENABLE_AUTOCHECK'} eq 'on') && ($xlratorsettings{'AUTOCHECK_SCHEDULE'} eq 'daily'))
	{
		system('/usr/local/bin/updxlratorctrl cron daily >/dev/null 2>&1');
	}
	if (($xlratorsettings{'ENABLE_AUTOCHECK'} eq 'on') && ($xlratorsettings{'AUTOCHECK_SCHEDULE'} eq 'weekly'))
	{
		system('/usr/local/bin/updxlratorctrl cron weekly >/dev/null 2>&1');
	}
	if (($xlratorsettings{'ENABLE_AUTOCHECK'} eq 'on') && ($xlratorsettings{'AUTOCHECK_SCHEDULE'} eq 'monthly'))
	{
		system('/usr/local/bin/updxlratorctrl cron monthly >/dev/null 2>&1');
	}

	# don't save those variable to the settings file,
	# but we wan't to have them in the hash again after saving to file
	my $obsolete = $xlratorsettings{'REMOVE_OBSOLETE'};
	my $nosource = $xlratorsettings{'REMOVE_NOSOURCE'};
	my $outdated = $xlratorsettings{'REMOVE_OUTDATED'};
	my $gui = $xlratorsettings{'EXTENDED_GUI'};

	delete($xlratorsettings{'REMOVE_OBSOLETE'});
	delete($xlratorsettings{'REMOVE_NOSOURCE'});
	delete($xlratorsettings{'REMOVE_OUTDATED'});

	delete($xlratorsettings{'EXTENDED_GUI'});

	&General::writehash("${General::swroot}/updatexlrator/settings", \%xlratorsettings);

	# put temp variables back into the hash
	$xlratorsettings{'REMOVE_OBSOLETE'} = $obsolete;
	$xlratorsettings{'REMOVE_NOSOURCE'} = $nosource;
	$xlratorsettings{'REMOVE_OUTDATED'} = $outdated;
	$xlratorsettings{'EXTENDED_GUI'} = $gui;
}

# -------------------------------------------------------------------

sub percentbar
{
  my $percent = $_[0];
  my $fg = '#a0a0a0';
  my $bg = '#e2e2e2';

  if ($percent =~ m/^(\d+)%$/ )
  {
    print <<END
<table width='100' border='1' cellspacing='0' cellpadding='0' style='border-width:1px;border-style:solid;border-color:$fg;width:100px;height:10px;'>
<tr>
END
;
    if ($percent eq "100%") {
      print "<td width='100%' bgcolor='$fg' style='background-color:$fg;border-style:solid;border-width:1px;border-color:$bg'>"
    } elsif ($percent eq "0%") {
      print "<td width='100%' bgcolor='$bg' style='background-color:$bg;border-style:solid;border-width:1px;border-color:$bg'>"
    } else {
      print "<td width='$percent' bgcolor='$fg' style='background-color:$fg;border-style:solid;border-width:1px;border-color:$bg'></td><td width='" . (100-$1) . "%' bgcolor='$bg' style='background-color:$bg;border-style:solid;border-width:1px;border-color:$bg'>"
    }
    print <<END
<img src='/images/null.gif' width='1' height='1' alt='' /></td></tr></table>
END
;
  }
}

# -------------------------------------------------------------------

sub getmtime
{
	my ($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,$atime,$mtime,$ctime,$blksize,$blocks) = stat($_[0]);

	return $mtime;
}

# -------------------------------------------------------------------

sub getPID
{
	my $pid='';
	my @psdata=`ps ax --no-heading`;

	foreach (@psdata)
	{
		if (/$_[0]/) { ($pid)=/^\s*(\d+)/; }
	}

	return $pid;
}

# -------------------------------------------------------------------
