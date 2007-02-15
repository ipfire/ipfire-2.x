#!/usr/bin/perl
#
# IPCop CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) 2006 marco.s
#
# $Id: updatexlrator.cgi,v 1.0.0 2006/09/12 00:00:00 marco.s Exp $
#

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

use IO::Socket;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my $updxlratorversion = `cat ${General::swroot}/updatexlrator/version`;
my $sysupdflagfile = "${General::swroot}/updatexlrator/.up2date";

my %checked=();
my %selected=();
my %netsettings=();
my %mainsettings=();
my %proxysettings=();
my %xlratorsettings=();
my $id=0;
my $updatefile='';
my $shortname='';
my $vendor='';
my $time='';
my $filesize=0;
my $filedate='';
my $lastaccess='';
my $lastcheck='';

my $repository = "/srv/web/ipfire/html/updatecache";
my $hintcolour = '#FFFFCC';

my $sfNoSource='0';
my $sfOk='1';
my $sfOutdated='2';

my $not_accessed_last='';

my $errormessage='';

my @repositorylist=();
my @repositoryfiles=();

my @metadata=();

my $chk_cron_dly = "${General::swroot}/updatexlrator/autocheck/cron.daily";
my $chk_cron_wly = "${General::swroot}/updatexlrator/autocheck/cron.weekly";
my $chk_cron_mly = "${General::swroot}/updatexlrator/autocheck/cron.monthly";

my $latest=substr(&check4updates,0,length($updxlratorversion));

&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);

$xlratorsettings{'ACTION'} = '';
$xlratorsettings{'ENABLE_LOG'} = 'off';
$xlratorsettings{'CHILDREN'} = '5';
$xlratorsettings{'PASSIVE_MODE'} = 'off';
$xlratorsettings{'MAX_DISK_USAGE'} = '75';
$xlratorsettings{'LOW_DOWNLOAD_PRIORITY'} = 'off';
$xlratorsettings{'ENABLE_AUTOCHECK'} = 'off';
$xlratorsettings{'FULL_AUTOSYNC'} = 'off';
$xlratorsettings{'NOT_ACCESSED_LAST'} = 'month1';

&Header::getcgihash(\%xlratorsettings);

if ($xlratorsettings{'ACTION'} eq $Lang::tr{'updxlrtr purge'})
{
	if (($xlratorsettings{'REMOVE_OBSOLETE'} eq 'on') || ($xlratorsettings{'REMOVE_NOSOURCE'} eq 'on') || ($xlratorsettings{'REMOVE_OUTDATED'} eq 'on'))
	{
		@repositorylist = <$repository/*>;
		foreach (@repositorylist)
		{
			if (!-d $_)
			{
				$updatefile = substr($_,rindex($_,"/")+1);
				if (-e "$repository/metadata/$updatefile")
				{
					open (FILE,"$repository/metadata/$updatefile");
					@metadata = <FILE>;
					close FILE;
					chomp(@metadata);

					if (($xlratorsettings{'REMOVE_NOSOURCE'} eq 'on') && ($metadata[2] == $sfNoSource))
					{
						unlink("$repository/$updatefile");
						unlink("$repository/metadata/$updatefile");
					}
					if (($xlratorsettings{'REMOVE_OUTDATED'} eq 'on') && ($metadata[2] == $sfOutdated))
					{
						unlink("$repository/$updatefile");
						unlink("$repository/metadata/$updatefile");
					}
					if ($xlratorsettings{'REMOVE_OBSOLETE'} eq 'on')
					{
						if (($xlratorsettings{'NOT_ACCESSED_LAST'} eq 'week') && ($metadata[-1] < (time - 604800)))
						{
							unlink("$repository/$updatefile");
							unlink("$repository/metadata/$updatefile");
						}
						if (($xlratorsettings{'NOT_ACCESSED_LAST'} eq 'month1') && ($metadata[-1] < (time - 2505600)))
						{
							unlink("$repository/$updatefile");
							unlink("$repository/metadata/$updatefile");
						}
						if (($xlratorsettings{'NOT_ACCESSED_LAST'} eq 'month3') && ($metadata[-1] < (time - 7516800)))
						{
							unlink("$repository/$updatefile");
							unlink("$repository/metadata/$updatefile");
						}
						if (($xlratorsettings{'NOT_ACCESSED_LAST'} eq 'month6') && ($metadata[-1] < (time - 15033600)))
						{
							unlink("$repository/$updatefile");
							unlink("$repository/metadata/$updatefile");
						}
						if (($xlratorsettings{'NOT_ACCESSED_LAST'} eq 'year') && ($metadata[-1] < (time - 31536000)))
						{
							unlink("$repository/$updatefile");
							unlink("$repository/metadata/$updatefile");
						}
					}
				}
			}
		}
	}
}

if ($xlratorsettings{'ACTION'} eq $Lang::tr{'save'})
{
	if (!($xlratorsettings{'CHILDREN'} =~ /^\d+$/) || ($xlratorsettings{'CHILDREN'} < 1))
	{
		$errormessage = $Lang::tr{'updxlrtr invalid num of children'};
		goto ERROR;
	}
	if (!($xlratorsettings{'MAX_DISK_USAGE'} =~ /^\d+$/) || ($xlratorsettings{'MAX_DISK_USAGE'} < 1) || ($xlratorsettings{'MAX_DISK_USAGE'} > 100))
	{
		$errormessage = $Lang::tr{'updxlrtr invalid disk usage'};
		goto ERROR;
	}

	&savesettings;
}

if ($xlratorsettings{'ACTION'} eq $Lang::tr{'updxlrtr save and restart'})
{
	if (!($xlratorsettings{'CHILDREN'} =~ /^\d+$/) || ($xlratorsettings{'CHILDREN'} < 1))
	{
		$errormessage = $Lang::tr{'updxlrtr invalid num of children'};
		goto ERROR;
	}
	if (!($xlratorsettings{'MAX_DISK_USAGE'} =~ /^\d+$/) || ($xlratorsettings{'MAX_DISK_USAGE'} < 1) || ($xlratorsettings{'MAX_DISK_USAGE'} > 100))
	{
		$errormessage = $Lang::tr{'updxlrtr invalid disk usage'};
		goto ERROR;
	}
	if (!(-e "${General::swroot}/proxy/enable"))
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

	system('/usr/local/bin/restartsquid');
}

if ($xlratorsettings{'ACTION'} eq $Lang::tr{'updxlrtr remove file'})
{
	$updatefile = $xlratorsettings{'ID'};
	if (-e "$repository/$updatefile") { unlink("$repository/$updatefile"); }
	$updatefile =~ s/^download\///i;
	if (-e "$repository/metadata/$updatefile") { unlink("$repository/metadata/$updatefile"); }
}

ERROR:

$not_accessed_last =  $xlratorsettings{'NOT_ACCESSED_LAST'};
undef($xlratorsettings{'NOT_ACCESSED_LAST'});

if (-e "${General::swroot}/updatexlrator/settings") { &General::readhash("${General::swroot}/updatexlrator/settings", \%xlratorsettings); }

if ($xlratorsettings{'NOT_ACCESSED_LAST'} eq '') { $xlratorsettings{'NOT_ACCESSED_LAST'} = $not_accessed_last; } ;


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

$selected{'AUTOCHECK_SCHEDULE'}{$xlratorsettings{'AUTOCHECK_SCHEDULE'}} = "selected='selected'";
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

if (($updxlratorversion lt $latest) && (-e $sysupdflagfile)) { unlink($sysupdflagfile); }

if (!-e $sysupdflagfile) {
	&Header::openbox('100%', 'left', $Lang::tr{'updxlrtr update notification'});
	print "<table width='100%' cellpadding='5'>\n";
	print "<tr>\n";
	print "<td bgcolor='$hintcolour' class='base'>$Lang::tr{'updxlrtr update information'}</td>";
	print "</tr>\n";
	print "</table>\n";
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
	<td class='base' width='25%'>$Lang::tr{'updxlrtr children'}:</td>
	<td class='base' width='30%'><input type='text' name='CHILDREN' value='$xlratorsettings{'CHILDREN'}' size='5' /></td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'updxlrtr passive mode'}:</td>
	<td class='base'><input type='checkbox' name='PASSIVE_MODE' $checked{'PASSIVE_MODE'}{'on'} /></td>
	<td class='base'>$Lang::tr{'updxlrtr max disk usage'}:</td>
	<td class='base'><input type='text' name='MAX_DISK_USAGE' value='$xlratorsettings{'MAX_DISK_USAGE'}' size='1' /> %</td>
</tr>
<tr>
	<td class='base'>$Lang::tr{'updxlrtr low download priority'}:</td>
	<td class='base'><input type='checkbox' name='LOW_DOWNLOAD_PRIORITY' $checked{'LOW_DOWNLOAD_PRIORITY'}{'on'} /></td>
	<td>&nbsp;</td>
	<td>&nbsp;</td>
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
        <td colspan='6'><b>$Lang::tr{'updxlrtr maintenance'}</b></td>
</tr>
<tr>
	<td class='base' colspan='3'><input type='submit' name='ACTION' value='$Lang::tr{'updxlrtr purge'}' /> &nbsp;$Lang::tr{'updxlrtr all files'}</td>
	<td class='base' width='25%'><input type='checkbox' name='REMOVE_OBSOLETE' $checked{'REMOVE_OBSOLETE'}{'on'} />&nbsp;$Lang::tr{'updxlrtr not accessed'}</td>
	<td class='base' colspan='3'><select name='NOT_ACCESSED_LAST'>
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
	<td class='base' width='25%'><input type='checkbox' name='REMOVE_NOSOURCE' $checked{'REMOVE_NOSOURCE'}{'on'} />&nbsp;$Lang::tr{'updxlrtr marked as'}</td>
	<td class='base' width='3%'><img src='/images/updxl-led-yellow.gif' alt='$Lang::tr{'updxlrtr condition nosource'}' /></td>
	<td class='base' width='17%'>[<i>$Lang::tr{'updxlrtr condition nosource'}</i>]</td>
	<td class='base' width='25%'><input type='checkbox' name='REMOVE_OUTDATED' $checked{'REMOVE_OUTDATED'}{'on'} />&nbsp;$Lang::tr{'updxlrtr marked as'}</td>
	<td class='base' width='3%'><img src='/images/updxl-led-red.gif' alt='$Lang::tr{'updxlrtr condition outdated'}' /></td>
	<td class='base' width='27%'>[<i>$Lang::tr{'updxlrtr condition outdated'}</i>]</td>
</tr>
</table>
<hr size='1'>
<table width='100%'>
<tr>
	<td>&nbsp;</td>
	<td align='center' width='45%'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
	<td align='center' width='45%'><input type='submit' name='ACTION' value='$Lang::tr{'updxlrtr save and restart'}' /></td>
	<td>&nbsp;</td>
</tr>
</table>
<table width='100%'>
<tr>
	<td align='right'>
	<sup><small><a href='http://www.advproxy.net/update-accelerator/' target='_blank'>Update Accelerator $updxlratorversion</a></small></sup>
	</td>
</tr>
</table>
END
;

&Header::closebox();

print "</form>\n";

# ----------------------------------------------------
#    File list dialog
# ----------------------------------------------------

&Header::openbox('100%', 'left', "$Lang::tr{'updxlrtr current files'}:");

@repositorylist = <$repository/download/*>;

undef @repositoryfiles;
foreach (@repositorylist)
{
	if (!-d)
	{
		$updatefile = substr($_,rindex($_,"/")+1);
		$updatefile = "download/$updatefile";
		push(@repositoryfiles,$updatefile);
	}
}

@repositorylist = <$repository/*>;

foreach (@repositorylist)
{
	if (!-d) { push(@repositoryfiles,substr($_,rindex($_,"/")+1)); }
}

if (@repositoryfiles)
{
	print <<END
<table width='100%'>
<colgroup span='2' width='2%'></colgroup>
<colgroup span='1' width='0*'></colgroup>
<colgroup span='4' width='5%'></colgroup>
<colgroup span='1' width='2%'></colgroup>
<tr>
	<td class='base' align='center'>&nbsp;</td>
	<td class='base' align='center'>&nbsp;</td>
	<td class='base' align='center'><b>$Lang::tr{'updxlrtr filename'}</b></td>
	<td class='base' align='center'><b>$Lang::tr{'updxlrtr filesize'}</b></td>
	<td class='base' align='center'><b>$Lang::tr{'date'}</b></td>
	<td class='base' align='center'><img src='/images/reload.gif' alt='$Lang::tr{'updxlrtr last access'}' /></td>
	<td class='base' align='center'><img src='/images/floppy.gif' alt='$Lang::tr{'updxlrtr last checkup'}' /></td>
	<td class='base' align='center'>&nbsp;</td>
</tr>
END
;
	$id = 0;
	foreach $updatefile (@repositoryfiles)
	{
		$id++;
		if ($id % 2) {
			print "<tr bgcolor='$Header::table1colour'>\n"; }
		else {
			print "<tr bgcolor='$Header::table2colour'>\n"; }
		$filesize = (-s "$repository/$updatefile");
		1 while $filesize =~ s/^(-?\d+)(\d{3})/$1.$2/;

		my ($SECdt,$MINdt,$HOURdt,$DAYdt,$MONTHdt,$YEARdt) = localtime(&getmtime("$repository/$updatefile"));
		$DAYdt   = sprintf ("%.02d",$DAYdt);
		$MONTHdt = sprintf ("%.02d",$MONTHdt+1);
		$YEARdt  = sprintf ("%.04d",$YEARdt+1900);
		$filedate = $YEARdt."-".$MONTHdt."-".$DAYdt;

		$lastaccess = "n/a";
		$lastcheck  = "n/a";
		undef @metadata;

		$shortname = $updatefile;
		$shortname =~ s/^download\///i;

		if (-e "$repository/metadata/$shortname")
		{
			open (FILE,"$repository/metadata/$shortname");
			@metadata = <FILE>;
			close(FILE);
			chomp @metadata;

			($SECdt,$MINdt,$HOURdt,$DAYdt,$MONTHdt,$YEARdt) = localtime($metadata[-1]);
			$DAYdt   = sprintf ("%.02d",$DAYdt);
			$MONTHdt = sprintf ("%.02d",$MONTHdt+1);
			$YEARdt  = sprintf ("%.04d",$YEARdt+1900);
			if (($metadata[-1] =~ /^\d+/) && ($metadata[-1] >= 1)) { $lastaccess = $YEARdt."-".$MONTHdt."-".$DAYdt; }

			($SECdt,$MINdt,$HOURdt,$DAYdt,$MONTHdt,$YEARdt) = localtime($metadata[3]);
			$DAYdt   = sprintf ("%.02d",$DAYdt);
			$MONTHdt = sprintf ("%.02d",$MONTHdt+1);
			$YEARdt  = sprintf ("%.04d",$YEARdt+1900);
			if (($metadata[3] =~ /^\d+/) && ($metadata[3] >= 1)) { $lastcheck = $YEARdt."-".$MONTHdt."-".$DAYdt; }
		}
		
		print "\t\t<td align='center' nowrap='nowrap'>&nbsp;";
		if ($metadata[2] eq $sfNoSource)
		{
			print "<img src='/images/updxl-led-yellow.gif' alt='$Lang::tr{'updxlrtr condition nosource'}' />&nbsp;</td>\n";
		}
		if ($metadata[2] eq $sfOk)
		{
			print "<img src='/images/updxl-led-green.gif' alt='$Lang::tr{'updxlrtr condition ok'}' />&nbsp;</td>\n";
		}
		if (($metadata[2] eq $sfOutdated) && (!($updatefile =~ /^download\//i)))
		{
			print "<img src='/images/updxl-led-red.gif' alt='$Lang::tr{'updxlrtr condition outdated'}' />&nbsp;</td>\n";
		}
		if (($metadata[2] eq $sfOutdated) && ($updatefile =~ /^download\//i))
		{
			print "<img src='/images/updxl-led-blue.gif' alt='$Lang::tr{'updxlrtr condition download'}' />&nbsp;</td>\n";
		}
		if ($metadata[2] eq '')
		{
			print "<img src='/images/updxl-led-red.gif' alt='$Lang::tr{'updxlrtr condition outdated'}' />&nbsp;</td>\n";
		}

		print "\t\t<td align='center' nowrap='nowrap'>&nbsp;";
		if ($metadata[1] eq 'Adobe')
		{
			print "<img src='/images/updxl-src-adobe.gif' alt='Adobe'}' />&nbsp;</td>\n";
		} elsif ($metadata[1] eq 'Microsoft')
		{
			print "<img src='/images/updxl-src-windows.gif' alt='Microsoft'}' />&nbsp;</td>\n";
		} elsif ($metadata[1] eq 'Symantec')
		{
			print "<img src='/images/updxl-src-symantec.gif' alt='Symantec'}' />&nbsp;</td>\n";
		} else
		{
			print "<img src='/images/updxl-src-unknown.gif' alt='$Lang::tr{'updxlrtr unknown'}' />&nbsp;</td>\n";
		}

		$shortname = $updatefile;
		$shortname =~ s/(.*)_[\da-f]*(\.(exe|cab|psf)$)/\1_*\2/i;
		$shortname =~ s/^download\///i;

print <<END
		<td class='base' align='left' title='$updatefile'>$shortname</td>
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

print <<END
</table>
<br>
<table>
	<tr>
		<td class='boldbase'>&nbsp; <b>$Lang::tr{'legend'}:</b></td>
		<td class='base'>&nbsp;</td>
		<td><img src='/images/reload.gif' alt='$Lang::tr{'updxlrtr last access'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr last access'}</td>
		<td class='base'>&nbsp;</td>
		<td><img src='/images/floppy.gif' alt='$Lang::tr{'updxlrtr last checkup'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr last checkup'}</td>
		<td class='base'>&nbsp;</td>
		<td><img src='/images/delete.gif' alt='$Lang::tr{'updxlrtr remove file'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr remove file'}</td>
		<td class='base'>&nbsp;</td>
		<td class='base'>&nbsp;</td>
		<td class='base'>&nbsp;</td>
	</tr>
	<tr>
		<td colspan='13'></td>
	</tr>
	<tr>
		<td class='base'>&nbsp; $Lang::tr{'status'}:</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updxl-led-green.gif' alt='$Lang::tr{'updxlrtr condition ok'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr condition ok'}</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updxl-led-yellow.gif' alt='$Lang::tr{'updxlrtr condition nosource'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr condition nosource'}</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updxl-led-red.gif' alt='$Lang::tr{'updxlrtr condition outdated'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr condition outdated'}</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updxl-led-blue.gif' alt='$Lang::tr{'updxlrtr condition download'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr condition download'}</td>
	</tr>
	<tr>
		<td colspan='13'></td>
	</tr>
	<tr>
		<td class='base'>&nbsp; $Lang::tr{'updxlrtr source'}:</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updxl-src-adobe.gif' alt='Adobe' /></td>
		<td class='base'>Adobe</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updxl-src-windows.gif' alt='Microsoft' /></td>
		<td class='base'>Microsoft</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updxl-src-symantec.gif' alt='Symantec' /></td>
		<td class='base'>Symantec</td>
		<td class='base'>&nbsp;</td>
		<td align='center'><img src='/images/updxl-src-unknown.gif' alt='$Lang::tr{'updxlrtr unknown'}' /></td>
		<td class='base'>$Lang::tr{'updxlrtr unknown'}</td>
	</tr>
</table>
END
;
} else {

	print "<i>$Lang::tr{'updxlrtr empty repository'}</i>\n";
}

print <<END
<hr>

<table>
<tr><td class='boldbase'><b>$Lang::tr{'updxlrtr disk usage'}:</b></td></tr>
</table>

<table cellpadding='3'>
END
;
open(DF,"/bin/df -h $repository|");
while(<DF>)
{
	if ($_ =~ m/^Filesystem/ )
	{
		print <<END
<tr>
<td align='left' class='base'><i>$Lang::tr{'updxlrtr cache dir'}</i></td>
<td align='center' class='base'><i>$Lang::tr{'size'}</i></td>
<td align='center' class='base'><i>$Lang::tr{'used'}</i></td>
<td align='center' class='base'><i>$Lang::tr{'free'}</i></td>
<td align='left' class='base' colspan='2'><i>$Lang::tr{'percentage'}</i></td>
</tr>
END
;
	}
	else
	{
		my ($device,$size,$used,$free,$percent,$mount) = split;
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
END
;
	}
}
close DF;
print "</table>\n";

&Header::closebox();

&Header::closebigbox();

&Header::closepage();

# -------------------------------------------------------------------

sub check4updates
{
	if ((-e "${General::swroot}/red/active") && (-e $sysupdflagfile) && (int(-M $sysupdflagfile) > 7))
	{
		my @response=();;

		my $remote = IO::Socket::INET->new(
			PeerHost => 'www.advproxy.net',
			PeerPort => 'http(80)',
			Timeout  => 1
		);

		if ($remote)
		{
			print $remote "GET http://www.advproxy.net/update-accelerator/version/ipcop/latest HTTP/1.0\n";
			print $remote "User-Agent: Mozilla/4.0 (compatible; IPCop $General::version; $Lang::language; updatexlrator)\n\n";
			while (<$remote>) { push(@response,$_); }
			close $remote;
			if ($response[0] =~ /^HTTP\/\d+\.\d+\s200\sOK\s*$/)
			{
				system("touch $sysupdflagfile");
				return "$response[$#response]";
			}
		}
	}
}

# -------------------------------------------------------------------

sub savesettings
{
	if (-e $chk_cron_dly) { unlink($chk_cron_dly); }
	if (-e $chk_cron_wly) { unlink($chk_cron_wly); }
	if (-e $chk_cron_mly) { unlink($chk_cron_mly); }

	if (($xlratorsettings{'ENABLE_AUTOCHECK'} eq 'on') && ($xlratorsettings{'AUTOCHECK_SCHEDULE'} eq 'daily'))
	{
		symlink("../bin/checkup",$chk_cron_dly)
	} else {
		symlink("/bin/false",$chk_cron_dly)
	}
		if (($xlratorsettings{'ENABLE_AUTOCHECK'} eq 'on') && ($xlratorsettings{'AUTOCHECK_SCHEDULE'} eq 'weekly'))
	{
		symlink("../bin/checkup",$chk_cron_wly)
	} else {
		symlink("/bin/false",$chk_cron_wly)
	}
		if (($xlratorsettings{'ENABLE_AUTOCHECK'} eq 'on') && ($xlratorsettings{'AUTOCHECK_SCHEDULE'} eq 'monthly'))
	{
		symlink("../bin/checkup",$chk_cron_mly)
	} else {
		symlink("/bin/false",$chk_cron_mly)
	}

	delete($xlratorsettings{'REMOVE_OBSOLETE'});
	delete($xlratorsettings{'REMOVE_NOSOURCE'});
	delete($xlratorsettings{'REMOVE_OUTDATED'});

	&General::writehash("${General::swroot}/updatexlrator/settings", \%xlratorsettings);
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
