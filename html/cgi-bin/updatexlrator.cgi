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
use warnings; # no warnings 'once';# 'redefine', 'uninitialized';
use CGI::Carp 'fatalsToBrowser';

use IO::Socket;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

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
my $dudata='';
my $dustr='';
my @updatelist=();
my @sources=();
my $sourceurl='';
my $vendorid='';
my $uuid='';
my $status=0;
my $updatefile='';
my $cachefile='';
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
my %vendimg = ();

my $repository = '/var/updatecache/';
my $webhome = '/srv/web/ipfire/html';
my $webimgdir = '/images/updbooster';

my $sfUnknown='0';
my $sfOk='1';
my $sfOutdated='2';
my $sfNoSource='3';

my $not_accessed_last='';

my @errormessages=();

my @repositorylist=();
my @repositoryfiles=();
my @downloadlist=();
my @downloadfiles=();

my @metadata=();

&General::readhash("${General::swroot}/ethernet/settings", \%netsettings);
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("${General::swroot}/proxy/settings", \%proxysettings);

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
$xlratorsettings{'REMOVE_UNKNOWN'} = 'off';
$xlratorsettings{'REMOVE_TODELETE'} = 'off';
$xlratorsettings{'TODELETE'} = 'off';
$xlratorsettings{'show'} = '';

&Header::getcgihash(\%xlratorsettings);

# ------------------------------------------------------
# Check if some ACTION is required
# ------------------------------------------------------

if ($xlratorsettings{'ACTION'} eq $Lang::tr{'save'})
  { &chksettings('save',\@errormessages);
    $xlratorsettings{'show'} = 'settings';
  }
elsif ($xlratorsettings{'ACTION'} eq $Lang::tr{'updxlrtr save and restart'})
  { &chksettings('saverestart',\@errormessages);
    $xlratorsettings{'show'} = 'settings';
  }
elsif ($xlratorsettings{'ACTION'} eq $Lang::tr{'updxlrtr cancel download'})
  { &canceldownload($xlratorsettings{'ID'});
    $xlratorsettings{'show'} = 'overview';
  }
elsif (($xlratorsettings{'ACTION'} eq $Lang::tr{'updxlrtr purge'})
    && (($xlratorsettings{'REMOVE_UNKNOWN'} eq 'on')
      || ($xlratorsettings{'REMOVE_NOSOURCE'} eq 'on')
      || ($xlratorsettings{'REMOVE_OUTDATED'} eq 'on')
      || ($xlratorsettings{'REMOVE_TODELETE'} eq 'on')))
  { &delolddata();
    $xlratorsettings{'show'} = 'maintenance';
  }

# ------------------------------------------------------
#  ACTION Check - End
# ------------------------------------------------------

$not_accessed_last = $xlratorsettings{'NOT_ACCESSED_LAST'};
undef($xlratorsettings{'NOT_ACCESSED_LAST'});

if (-e "${General::swroot}/updatexlrator/settings") {
  &General::readhash("${General::swroot}/updatexlrator/settings", \%xlratorsettings);
}

if ($xlratorsettings{'NOT_ACCESSED_LAST'} eq '') { $xlratorsettings{'NOT_ACCESSED_LAST'} = $not_accessed_last; }

if ($xlratorsettings{'show'} eq 'overview') { $xlratorsettings{'EXTENDED_GUI'} = 'overview'; }
elsif ($xlratorsettings{'show'} eq 'statistics') { $xlratorsettings{'EXTENDED_GUI'} = 'statistics'; }
elsif ($xlratorsettings{'show'} eq 'settings') { $xlratorsettings{'EXTENDED_GUI'} = 'settings'; }
elsif ($xlratorsettings{'show'} eq 'maintenance') { $xlratorsettings{'EXTENDED_GUI'} = 'maintenance'; }
else { $xlratorsettings{'EXTENDED_GUI'} = $xlratorsettings{'VIEW_SETTING'}?$xlratorsettings{'VIEW_SETTING'}:'overview'; }

&initvendimg;

# ----------------------------------------------------
#  Start Page Output
# ----------------------------------------------------

&Header::showhttpheaders();
&Header::openpage($Lang::tr{'updxlrtr configuration'}, 1, '<link rel=\'stylesheet\' type=\'text/css\' href=\'/themes/'.$mainsettings{'THEME'}.'/include/upxlr.css\' />' );
&Header::openbigbox('100%', 'left', '', scalar(@errormessages));

# =====================================================================================
#  CACHE OVERVIEW
# =====================================================================================

if ($xlratorsettings{'EXTENDED_GUI'} eq 'overview') {
  &Header::openbox('100%', 'left', $Lang::tr{'updxlrtr cache overview'});
  &printfrmview();
  &printerrormsgs(\@errormessages);
  &printtbldiskusage ($Lang::tr{'updxlrtr disk usage'},\$repository);
  &initdownloaddata(\@downloadfiles);
  &printtbldownloads(\@downloadfiles);
  &Header::closebox();
  }

# =====================================================================================
#  CACHE STATISTICS
# =====================================================================================

if ($xlratorsettings{'EXTENDED_GUI'} eq 'statistics') {
  &Header::openbox('100%', 'left', "$Lang::tr{'updxlrtr cache statistics'}");
  &printfrmview();
  &printerrormsgs(\@errormessages);
  &initcachestats();
  &printcachestatistics();
  &Header::closebox();
  } 

# =====================================================================================
#  CACHE MAINTENANCE
# =====================================================================================

if ($xlratorsettings{'EXTENDED_GUI'} eq 'maintenance') {
  &Header::openbox('100%', 'left', "$Lang::tr{'updxlrtr cache maintenance'}");
  &printfrmview();
  &printerrormsgs(\@errormessages);
  &initfrmmaintenance();
  &inittblreposdata();
  &printfrmmaintenance('withfiles', \@repositoryfiles);
  &Header::closebox();
  }

# =====================================================================================
#  CACHE SETTINGS
# =====================================================================================

if ($xlratorsettings{'EXTENDED_GUI'} eq 'settings') {
  &Header::openbox('100%', 'left', $Lang::tr{'updxlrtr cache settings'});
  &printfrmview();
  &printerrormsgs(\@errormessages);
  &initfrmsettings();
  &printfrmsettings();
  &Header::closebox();
  }

# ----------------------------------------------------
#  End Page Output
# ----------------------------------------------------
&Header::closebigbox();
&Header::closepage();

# -------------------------------------------------------------------
# Print Form to switch view
# -------------------------------------------------------------------

sub printfrmview {
  print <<END
<form class='frmshow' method='get' action='$ENV{'SCRIPT_NAME'}'>
<fieldset class='noborder'>
<legend><span>$Lang::tr{'updxlrtr current view'}:</span></legend>
END
;
  if ($xlratorsettings{'EXTENDED_GUI'} eq 'overview')
    { print "<button id='oview' class='symbols' disabled='disabled'>$Lang::tr{'updxlrtr overview'}</button>\n"; }
  else
    { print "<button id='oview' class='symbols'  type='submit' name='show' value='overview'>$Lang::tr{'updxlrtr overview'}</button>\n"; }
    
  if ($xlratorsettings{'EXTENDED_GUI'} eq 'statistics')
    { print "<button id='stat' class='symbols' disabled='disabled'>$Lang::tr{'updxlrtr statistics'}</button>\n"; }
  else
    { print "<button id='stat' class='symbols' type='submit' name='show' value='statistics'>$Lang::tr{'updxlrtr statistics'}</button>\n"; }
  
  if ($xlratorsettings{'EXTENDED_GUI'} eq 'maintenance')
    { print "<button id='wrench' class='symbols' disabled='disabled'>$Lang::tr{'updxlrtr maintenance'}</button>\n"; }
  else
    { print "<button id='wrench' class='symbols' type='submit' name='show' value='maintenance'>$Lang::tr{'updxlrtr maintenance'}</button>\n"; }
  
  if ($xlratorsettings{'EXTENDED_GUI'} eq 'settings')
    { print "<button id='set' class='symbols' disabled='disabled'>$Lang::tr{'updxlrtr settings'}</button>\n"; }
  else
    { print "<button id='set' class='symbols' type='submit' name='show' value='settings'>$Lang::tr{'updxlrtr settings'}</button>\n"; }
  print <<END
</fieldset>
</form>
END
;
  return;
}

# -------------------------------------------------------------------
# Print Error Messages - printerrormsgs(\@errormsgs)
# -------------------------------------------------------------------

sub printerrormsgs {
	my $errmsgs_ref = shift;
	unless (@$errmsgs_ref == 0) {
		&Header::openbox('100%', 'left', '');
		print <<END
			<div id='errors'><strong>$Lang::tr{'error messages'}</strong><br />
END
;
		foreach (@$errmsgs_ref) { print "$_<br />"; }
		undef(@$errmsgs_ref);  
		print "\t\t\t</div>\n";
		&Header::closebox();
	}
}

# -------------------------------------------------------------------
# Initialize Downloaddata
# -------------------------------------------------------------------

sub initdownloaddata {
  @downloadlist = <$repository/download/*>;
  my $updfile;
  my $dlfiles_ref = shift;
  undef(@$dlfiles_ref);
  foreach (@downloadlist) {
    if (-d) {
      my @filelist = <$_/*>;
      $vendorid = substr($_,rindex($_,"/")+1);
      foreach(@filelist) {
        next if(/\.info$/);
        $updfile = substr($_,rindex($_,"/")+1);
        $updfile .= ":download/$vendorid/$updfile";
        $updfile = " ".$updfile;
        push(@$dlfiles_ref, $updfile);
      }
    }
  }
}

# -------------------------------------------------------------------
# Print pending Downloadlist
# -------------------------------------------------------------------

sub printtbldownloads {
  my $dllist_ref = shift;
  print <<END
<table id='listuploads'>
<caption>$Lang::tr{'updxlrtr current downloads'}</caption>
<thead>
	<tr>
		<th>$Lang::tr{'status'}</th>
		<th>$Lang::tr{'updxlrtr source'}</th>
		<th>$Lang::tr{'updxlrtr filename'}</th>
		<th>$Lang::tr{'updxlrtr filesize'}</th>
		<th>$Lang::tr{'date'}</th>
		<th>$Lang::tr{'updxlrtr progress'}</th>
		<th>&nbsp;</th>
	</tr>
</thead>
<tfoot>
	<tr>
		<td colspan='7' id='legenddownload'>
END
;
  &printlegenddownload();
  print <<END
		</td>
	</tr>
</tfoot>
<tbody>
END
;
  &printtbldldata($dllist_ref);
  print <<END
</tbody>
</table>
END
;
}

# -------------------------------------------------------------------
# Print Download Files - printdlfiles(\@dlfiles)
# -------------------------------------------------------------------

sub printtbldldata {
  my $dlfiles_ref = shift;
  unless (@$dlfiles_ref)
    { print "<tr>\n<th colspan=\"7\">".$Lang::tr{'updxlrtr no pending downloads attime'}."</th>\n</tr>\n"; }
  else {
    $id = 0;
    foreach $updatefile (@$dlfiles_ref) {
      print "<tr>\n";
      $updatefile =~ s/.*://;
      my $size_updatefile = 0;
      my $mtime = 0;

      if(-e "$repository/$updatefile") {
        $size_updatefile = (-s "$repository/$updatefile");
        $mtime = &getmtime("$repository/$updatefile");
      }

      if (-e "$repository/$updatefile.info") { &General::readhash("$repository/$updatefile.info", \%dlinfo); }
      else { undef(%dlinfo); }

      $filesize = $size_updatefile;
      1 while $filesize =~ s/^(-?\d+)(\d{3})/$1.$2/;
      my ($SECdt,$MINdt,$HOURdt,$DAYdt,$MONTHdt,$YEARdt) = localtime($mtime);
      my $percent = '0';
      $DAYdt   = sprintf ("%.02d",$DAYdt);
      $MONTHdt = sprintf ("%.02d",$MONTHdt+1);
      $YEARdt  = sprintf ("%.04d",$YEARdt+1900);
      $filedate = $DAYdt.".".$MONTHdt.".".$YEARdt;
      ($uuid,$vendorid,$shortname) = split('/',$updatefile);
      $shortname = substr($updatefile,rindex($updatefile,"/")+1);
      $shortname =~ s/(.*)_([\da-f]{8})*(\.(exe|cab|psf|msu)$)/$1_$2*$3/i;
      unless (length($shortname) <= 50) {
        my $fext = substr($shortname,rindex("$shortname",'.'));
        $shortname = substr($shortname,0,44-length($fext));
        $shortname .= "[...] $fext";
      }
      $filesize = $dlinfo{'REMOTESIZE'};
      1 while $filesize =~ s/^(-?\d+)(\d{3})/$1.$2/;
      $dlinfo{'VENDORID'} = ucfirst $vendorid;
      if ($dlinfo{'REMOTESIZE'} && $size_updatefile) { $percent = int(100 / ($dlinfo{'REMOTESIZE'} / $size_updatefile)); }

      if (&getPID("\\s/usr/bin/wget\\s.*\\s".quotemeta($dlinfo{'SRCURL'})."\$"))
         { print '<th><span id="ledbl" class="symbols" title="'.$Lang::tr{'updxlrtr condition download'}."\"></span></th>\n"; }
      else { print '<th><span id="ledgy" class="symbols" title="'.$Lang::tr{'updxlrtr condition suspended'}."\"></span></th>\n"; }

      if ($vendimg{$vendorid})
         { print '<th><span id="vd$id" class="vendimg" style="background-image: url('.$vendimg{$vendorid}.');" title="'.ucfirst $vendorid.'">'.ucfirst $dlinfo{'VENDORID'}."</span></th>\n"; }
      else { print '<th><span id="vd$id" class="vendimg" style="background-image: url('.$vendimg{'unknown'}.');" title="'.ucfirst $vendorid.'">'.ucfirst $dlinfo{'VENDORID'}."</span></th>\n"; }
      print <<END
<td title="cache:/$updatefile">$shortname</td>
<td>$filesize</td>
<td>$filedate</td>
<td>
END
;
      &percentbar($percent);
      print <<END
		</td>
		<th>
			<form method='post' id='del$id' action='$ENV{'SCRIPT_NAME'}'>
			<div>
				<button id='del$id' class='symbols' type='submit' title='$Lang::tr{'updxlrtr cancel download'}'></button>
				<input type='hidden' name='ID' value='$updatefile' />
				<input type='hidden' name='ACTION' value='$Lang::tr{'updxlrtr cancel download'}' />
			</div>
			</form>
		</th>
	</tr>
END
;
      $id += 1;
    }
  }
}

# -------------------------------------------------------------------
# Initialize Cachestats
# -------------------------------------------------------------------

sub initcachestats {
  @sources=();
  foreach (<$repository/*>) {
    if (-d $_) {
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
    foreach $data (@updatelist) {
      if (-e "$data/source.url") {
        open (FILE,"$data/source.url");
        $sourceurl=<FILE>;
        close FILE;
        chomp($sourceurl);
        $updatefile = substr($sourceurl,rindex($sourceurl,'/')+1,length($sourceurl));
        my $size_updatefile = 0;
        if(-e "$data/$updatefile") {
          $size_updatefile = (-s "$data/$updatefile");
        }
        else {
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
}

# ----------------------------------------------------
#   Print statistics
# ----------------------------------------------------

sub printcachestatistics {
  if ($numfiles) {
    $filesize = &format_size($filesize);
    $cachedtraffic = &format_size($cachedtraffic);
    print <<END
<table id='summary'>
<caption>$Lang::tr{'updxlrtr summary'}</caption>
<tbody>
	<tr>
		<th>$Lang::tr{'updxlrtr total files'}:</th>
		<td>$numfiles</td>
		<th>$Lang::tr{'updxlrtr total cache size'}:</th>
		<td align='right'>$filesize</td>
	</tr>
	<tr>
		<th>$Lang::tr{'updxlrtr efficiency index'}:</th>
		<td>$efficiency</td>
		<th>$Lang::tr{'updxlrtr total data from cache'}:</th>
		<td>$cachedtraffic</td>
	</tr>
</tbody>
</table>
<hr />
<table id='liststatbysrc'>
<caption>$Lang::tr{'updxlrtr statistics by source'}</caption>
<colgroup>
<col></col>
<col></col>
<col></col>
<col></col>
<col span='4' style='width: 40px'></col>
</colgroup>
<thead>
	<tr>
		<th>$Lang::tr{'updxlrtr source'}</th>
		<th>$Lang::tr{'updxlrtr files'}</th>
		<th>$Lang::tr{'updxlrtr cache size'}</th>
		<th>$Lang::tr{'updxlrtr data from cache'}</th>
		<th><span id='ledgr' class='symbols' title='$Lang::tr{'updxlrtr condition ok'}'></span></th>
		<th><span id='ledye' class='symbols' title='$Lang::tr{'updxlrtr condition nosource'}'></span></th>
		<th><span id='ledrd' class='symbols' title='$Lang::tr{'updxlrtr condition outdated'}'></span></th>
		<th><span id='ledgy' class='symbols' title='$Lang::tr{'updxlrtr condition unknown'}'></span></th>
	</tr>
</thead>
<tfoot>
	<tr>
		<td colspan='8' id='legendstatus'>
END
;
    &printlegendstatus();
    print <<END
		</td>
	</tr>
</tfoot>
<tbody>
END
;
	&printtblstatdata(\@vendors);
	print <<END
</tbody>
</table>
END
;
}

sub printtblstatdata {
	my $vendlst_ref = shift;
    my $vendorid;
	$id = 0;
  unless (@$vendlst_ref) { print "<tr>\n<th colspan='8'>$Lang::tr{'updxlrtr empty repository'}.</th>\n</tr>\n"; }
	else {
		foreach (@$vendlst_ref) {
		  $vendorid = $_;
		  unless ($vendorstats{$vendorid . "_files"}) { next; }
		  print "\t<tr>\n";
		  if ($vendimg{$vendorid})
			 { print "\t\t<th><span id='vd$id' class='vendimg' style='background-image: url($vendimg{$vendorid});' title='".ucfirst $vendorid."'>". ucfirst $vendorid ."</span></th>\n"; }
		  else { print "\t\t<th><span id='vd$id' class='vendimg' style='background-image: url($vendimg{'unknown'});' title='".ucfirst $vendorid."'>". ucfirst $vendorid ."</span></th>\n"; }
		  print "\t\t<td>";
		  printf "%5d", $vendorstats{$vendorid."_files"};
		  print "</td>\n";
		  unless ($vendorstats{$vendorid."_filesize"}) { $vendorstats{$vendorid."_filesize"} = '0'; }
		  print "\t\t<td>";
		  print &format_size($vendorstats{$vendorid."_filesize"});
		  print "</td>\n";
		  unless ($vendorstats{$vendorid."_cachehits"}) { $vendorstats{$vendorid."_cachehits"} = '0'; }
		  print "\t\t<td>";
		  print &format_size($vendorstats{$vendorid."_cachehits"});
		  print "</td>\n";
		  print "\t\t<td>";
		  printf "%5d", $vendorstats{$vendorid."_1"};
		  print "</td>\n";
		  print "\t\t<td>";
		  printf "%5d", $vendorstats{$vendorid."_3"};
		  print "</td>\n";
		  print "\t\t<td>";
		  printf "%5d", $vendorstats{$vendorid."_2"};
		  print "</td>\n";
		  print "\t\t<td>";
		  printf "%5d", $vendorstats{$vendorid."_0"};
		  print "</td>\n";
		  print "\t</tr>\n";
		  $id += 1;
		}
	}
  }
}
# -------------------------------------------------------------------
# Initialize Repositorydata
# -------------------------------------------------------------------

sub inittblreposdata {
  @sources = <$repository/download/*>;
  undef @repositoryfiles;
  foreach (@sources) {
    if (-d) {
      @updatelist = <$_/*>;
      $vendorid = substr($_,rindex($_,"/")+1);
      foreach(@updatelist) {
        next if(/\.info$/);
        $updatefile = substr($_,rindex($_,"/")+1);
        $updatefile .= ":download/$vendorid/$updatefile";
        $updatefile = " ".$updatefile;
        push(@repositoryfiles,$updatefile);
      }
    }
  }

  undef (@sources);
  foreach (<$repository/*>) {
    if (-d $_) {
      unless (/^$repository\/download$/) { push(@sources,$_); }
    }
  }

  foreach (@sources) {
    @updatelist=<$_/*>;
    $vendorid = substr($_,rindex($_,"/")+1);
    foreach(@updatelist) {
      $uuid = substr($_,rindex($_,"/")+1);
      if (-e "$_/source.url") {
        open (FILE,"$_/source.url");
        $sourceurl=<FILE>;
        close FILE;
        chomp($sourceurl);
        $updatefile = substr($sourceurl,rindex($sourceurl,'/')+1,length($sourceurl));
        $_ = $updatefile; tr/[A-Z]/[a-z]/;
        $updatefile = "$_:$vendorid/$uuid/$updatefile";
        push(@repositoryfiles,$updatefile);
      }
    }
  }
  @repositoryfiles = sort { ($a =~ /.*?:(.*\/).*?/)[0] cmp ($b =~ /.*?:(.*\/).*?/)[0] } @repositoryfiles;
}

# -------------------------------------------------------------------
# Initialize Cache-Maintenance Form
# -------------------------------------------------------------------

sub initfrmmaintenance {
  $selected{'NOT_ACCESSED_LAST'}{'week'} = '';
  $selected{'NOT_ACCESSED_LAST'}{'month1'} = '';
  $selected{'NOT_ACCESSED_LAST'}{'month3'} = '';
  $selected{'NOT_ACCESSED_LAST'}{'month6'} = '';
  $selected{'NOT_ACCESSED_LAST'}{'year'} = '';
  $selected{'NOT_ACCESSED_LAST'}{$xlratorsettings{'NOT_ACCESSED_LAST'}} = "selected='selected'";
  $checked{'REMOVE_NOSOURCE'}{'off'} = '';
  $checked{'REMOVE_NOSOURCE'}{'on'} = '';
  $checked{'REMOVE_NOSOURCE'}{$xlratorsettings{'REMOVE_NOSOURCE'}} = "checked='checked'";
  $checked{'REMOVE_OUTDATED'}{'off'} = '';
  $checked{'REMOVE_OUTDATED'}{'on'} = '';
  $checked{'REMOVE_OUTDATED'}{$xlratorsettings{'REMOVE_OUTDATED'}} = "checked='checked'";
  $checked{'REMOVE_UNKNOWN'}{'off'} = '';
  $checked{'REMOVE_UNKNOWN'}{'on'} = '';
  $checked{'REMOVE_UNKNOWN'}{$xlratorsettings{'REMOVE_UNKNOWN'}} = "checked='checked'";
  $checked{'REMOVE_TODELETE'}{'off'} = '';
  $checked{'REMOVE_TODELETE'}{'on'} = '';
  $checked{'REMOVE_TODELETE'}{$xlratorsettings{'REMOVE_TODELETE'}} = "checked='checked'";
  $checked{'TODELETE'}{'off'} = '';
  $checked{'TODELETE'}{'on'} = '';
  $checked{'TODELETE'}{$xlratorsettings{'TODELETE'}} = "checked='checked'";
}

# -------------------------------------------------------------------
# Print Cache-Maintenance Form - printfrmmaintenance('withfiles', \@repositoryfiles)
# -------------------------------------------------------------------

sub printfrmmaintenance {
  my $param = shift;
  my $repos_ref = shift;
  my $disabled = '';
  unless (@$repos_ref) { $disabled = "disabled='disabled'"; }
  print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>
	<fieldset>
	<legend>$Lang::tr{'updxlrtr all files'}</legend>
		<input id='check08' type='checkbox' name='REMOVE_UNKNOWN' $checked{'REMOVE_UNKNOWN'}{'on'} $disabled/>
		<label for='check08'>$Lang::tr{'updxlrtr not accessed'}:</label>
		<select id='select02' name='NOT_ACCESSED_LAST' $disabled>
			<option value='week'   $selected{'NOT_ACCESSED_LAST'}{'week'}>$Lang::tr{'updxlrtr week'}</option>
			<option value='month1' $selected{'NOT_ACCESSED_LAST'}{'month1'}>$Lang::tr{'updxlrtr month'}</option>
			<option value='month3' $selected{'NOT_ACCESSED_LAST'}{'month3'}>$Lang::tr{'updxlrtr 3 months'}</option>
			<option value='month6' $selected{'NOT_ACCESSED_LAST'}{'month6'}>$Lang::tr{'updxlrtr 6 months'}</option>
			<option value='year'   $selected{'NOT_ACCESSED_LAST'}{'year'}>$Lang::tr{'updxlrtr year'}</option>
		</select>
	</fieldset>
	<fieldset>
	<legend>$Lang::tr{'updxlrtr marked as'} ...</legend>
		<input id='check09' type='checkbox' name='REMOVE_NOSOURCE' $disabled/>
		<label id='lbledye' class='symbols' for='check09'>$Lang::tr{'updxlrtr condition nosource'}</label>
		<input id='check10' type='checkbox' name='REMOVE_OUTDATED' $disabled/>
		<label id='lbledrd' class='symbols' for='check10'>$Lang::tr{'updxlrtr condition outdated'}</label>
		<input id='check11' type='checkbox' name='REMOVE_UNKNOWN' $disabled/>
		<label id='lbledgy' class='symbols' for='check11'>$Lang::tr{'updxlrtr condition unknown'}</label>
		<input id='check12' type='checkbox' name='REMOVE_TODELETE' $disabled/>
		<label id='lbdel' class='symbols' for='check12'>$Lang::tr{'updxlrtr remove file'}</label>
	</fieldset>
	<fieldset class='noborder'>
		<input type='submit' name='ACTION' value='$Lang::tr{'updxlrtr purge'}' $disabled/>
	</fieldset>
END
;
  if ($param =~ /withfiles/i)
    { &printtblrepository($Lang::tr{'updxlrtr current files'}, $repos_ref); }
  print "</form>\n";
}

# -------------------------------------------------------------------
# Print current files in repository - printreposfiles($title, \@files)
# -------------------------------------------------------------------

sub printtblrepository {
  my $title = shift;
  my $files = shift;

  print <<END
<hr />
<table id='listcurrfiles'>
<caption>$title</caption>
<colgroup>
<col></col>
<col></col>
<col style='width: 0*'></col>
<col span='5' style='min-width: 20px'></col>
</colgroup>
<thead>
	<tr>
		<th>$Lang::tr{'status'}</th>
		<th>$Lang::tr{'updxlrtr source'}</th>
		<th>$Lang::tr{'updxlrtr filename'}</th>
		<th>$Lang::tr{'updxlrtr filesize'}</th>
		<th>$Lang::tr{'date'}</th>
		<th><span id='rel' class='symbols' title='$Lang::tr{'updxlrtr last access'}'></span></th>
		<th><span id='glo' class='symbols' title='$Lang::tr{'updxlrtr last checkup'}'></span></th>
		<th><span id='del' class='symbols' title='$Lang::tr{'updxlrtr remove file'}'></span></th>
	</tr>
</thead>
<tfoot>
	<tr>
		<td colspan='9' id='legend'>
END
;
&printlegendicons();
&printlegendstatus();
&printlegendsource();
print <<END
		</td>
	</tr>
</tfoot>
<tbody>
END
;
  unless (@$files) { print "\t<tr>\n\t\t<th colspan='8'>$Lang::tr{'updxlrtr empty repository'}.</th>\n\t</tr>\n"; }
  else {
    $id = 0;
    foreach $updatefile (@$files) {
      $updatefile =~ s/.*://;
      my $size_updatefile = 0;
      my $mtime = 0;
      if(-e "$repository/$updatefile") {
        $size_updatefile = (-s "$repository/$updatefile");
        $mtime = &getmtime("$repository/$updatefile");
      }
      print "\t<tr>\n";
      $filesize = &format_size($size_updatefile);
      my ($SECdt,$MINdt,$HOURdt,$DAYdt,$MONTHdt,$YEARdt) = localtime($mtime);
      $DAYdt   = sprintf ("%.02d",$DAYdt);
      $MONTHdt = sprintf ("%.02d",$MONTHdt+1);
      $YEARdt  = sprintf ("%.04d",$YEARdt+1900);
      $filedate = $DAYdt.".".$MONTHdt.".".$YEARdt;
      $lastaccess = "n/a";
      $lastcheck  = "n/a";
      $status = $sfUnknown;
      unless ($updatefile =~ /^download\//) {
        ($vendorid,$uuid,$shortname) = split('/',$updatefile);
        if (-e "$repository/$vendorid/$uuid/access.log") {
          open (FILE,"$repository/$vendorid/$uuid/access.log");
          @metadata = <FILE>;
          close(FILE);
          chomp @metadata;
          ($SECdt,$MINdt,$HOURdt,$DAYdt,$MONTHdt,$YEARdt) = localtime($metadata[-1]);
          $DAYdt   = sprintf ("%.02d",$DAYdt);
          $MONTHdt = sprintf ("%.02d",$MONTHdt+1);
          $YEARdt  = sprintf ("%.04d",$YEARdt+1900);
          if (($metadata[-1] =~ /^\d+/) && ($metadata[-1] >= 1))
            { $lastaccess = $DAYdt.".".$MONTHdt.".".$YEARdt; }
        }
        if (-e "$repository/$vendorid/$uuid/checkup.log") {
          open (FILE,"$repository/$vendorid/$uuid/checkup.log");
          @metadata = <FILE>;
          close(FILE);
          chomp @metadata;
          ($SECdt,$MINdt,$HOURdt,$DAYdt,$MONTHdt,$YEARdt) = localtime($metadata[-1]);
          $DAYdt = sprintf ("%.02d",$DAYdt);
          $MONTHdt = sprintf ("%.02d",$MONTHdt+1);
          $YEARdt  = sprintf ("%.04d",$YEARdt+1900);
          if (($metadata[-1] =~ /^\d+/) && ($metadata[-1] >= 1))
            { $lastcheck = $DAYdt.".".$MONTHdt.".".$YEARdt; }
        }
        if (-e "$repository/$vendorid/$uuid/status") {
          open (FILE,"$repository/$vendorid/$uuid/status");
          @metadata = <FILE>;
          close(FILE);
          chomp @metadata;
          $status = $metadata[-1];
        }
      }
      else {
        ($uuid,$vendorid,$shortname) = split('/',$updatefile);
        $status = $sfOutdated;
      }
        
      if ($status == $sfUnknown)
        { print "\t\t<th><span id='ledgy$id' class='symbols' title='$Lang::tr{'updxlrtr condition unknown'}'>&nbsp;</span></th>\n"; }
      elsif ($status == $sfOk)
        { print "\t\t<th><span id='ledgr$id' class='symbols' title='$Lang::tr{'updxlrtr condition ok'}'></span>&nbsp;</th>\n"; }
      elsif ($status == $sfNoSource)
        { print "\t\t<th><span id='ledye$id' class='symbols' title='$Lang::tr{'updxlrtr condition nosource'}'>&nbsp;</span></th>\n"; }
      elsif (($status == $sfOutdated) && (!($updatefile =~ /^download\//i)))
        { print "\t\t<th><span id='ledrd$id' class='symbols' title='$Lang::tr{'updxlrtr condition outdated'}'>&nbsp;</span></th>\n"; }
      elsif (($status == $sfOutdated) && ($updatefile =~ /^download\//i))
        { print "\t\t<th><span id='ledbl$id' class='symbols' title='$Lang::tr{'updxlrtr condition download'}'>&nbsp;</span></th>\n"; }
      if ($vendimg{$vendorid}) {
        print "\t\t<th><span class='vendimg' style='background-image: url($vendimg{$vendorid});' title='".ucfirst $vendorid."'>&nbsp;</span></th>\n"; }
      else {
        print "\t\t<th><span class='vendimg' style='background-image: url($vendimg{unknown});' title='".ucfirst $vendorid."'>&nbsp;</span></th>\n";
      }
      $shortname = substr($updatefile,rindex($updatefile,"/")+1);
	  unless ($vendorid ne 'microsoft') { $shortname =~ s/(.*)_[\da-f]*(\.(exe|cab|psf)$)/$1\[...\] $2/i; }
	  unless (length($shortname) <= 50) {
		my $fext = substr($shortname,rindex("$shortname",'.'));
		$shortname = substr($shortname,0,44-length($fext));
		$shortname .= "[...] $fext";
	  }
      print <<END
		<td title='cache:/$updatefile'><a href="/updatecache/$updatefile">$shortname</a></td>
		<td>$filesize</td>
		<td>$filedate</td>
		<td>$lastaccess</td>
		<td>$lastcheck</td>
		<th><input id='frm$id' type='checkbox' name='TODELETE' value='$updatefile' title='$Lang::tr{'updxlrtr remove file'}' /></th>
	</tr>
END
;
    $id += 1;
    }
  }
  print <<END
</tbody>
</table>
</form>
END
;
}

# -------------------------------------------------------------------
# cancels pending download - need updatefile(-ID)
# -------------------------------------------------------------------

sub canceldownload {
  $updatefile = shift;
  if ($updatefile =~ /^download\//) {
    ($uuid,$vendorid,$updatefile) = split('/',$updatefile);
    if (-e "$repository/download/$vendorid/$updatefile.info") {
      &General::readhash("$repository/download/$vendorid/$updatefile.info", \%dlinfo);
      $id = &getPID("\\s${General::swroot}/updatexlrator/bin/download\\s.*\\s".quotemeta($dlinfo{'SRCURL'})."\\s\\d\\s\\d\$");
      if ($id) { system("/bin/kill -9 $id"); }
      $id = &getPID("\\s/usr/bin/wget\\s.*\\s".quotemeta($dlinfo{'SRCURL'})."\$");
      if ($id) { system("/bin/kill -9 $id"); }
      system("rm \"$repository/download/$vendorid/$updatefile.info\"");
    }
    
    if (-e "$repository/download/$vendorid/$updatefile") {
      system("rm \"$repository/download/$vendorid/$updatefile\"");
    }
  }
}

# -------------------------------------------------------------------
# Delete old and selected cached files
# -------------------------------------------------------------------

sub delolddata {
  undef (@sources);
  undef @repositoryfiles;
  foreach (<$repository/*>) {
    if (-d $_) {
      unless (/^$repository\/download$/) { push(@sources,$_); }
    }
  }
  
  foreach (@sources) {
    @updatelist=<$_/*>;
    $vendorid = substr($_,rindex($_,"/")+1);
    foreach(@updatelist) {
      $uuid = substr($_,rindex($_,"/")+1);
      if (-e "$_/source.url") {
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
  
  foreach (@repositoryfiles) {
    ($vendorid,$uuid,$updatefile) = split('/');
    if (-e "$repository/$vendorid/$uuid/status") {
      open (FILE,"$repository/$vendorid/$uuid/status");
      @metadata = <FILE>;
      close FILE;
      chomp(@metadata);
      $status = $metadata[-1];
    }
    
    if (-e "$repository/$vendorid/$uuid/access.log") {
      open (FILE,"$repository/$vendorid/$uuid/access.log");
      @metadata = <FILE>;
      close FILE;
      chomp(@metadata);
      $lastaccess = $metadata[-1];
    }
    
    if (($xlratorsettings{'REMOVE_NOSOURCE'} eq 'on') && ($status == $sfNoSource)) {
      if (-e "$repository/$vendorid/$uuid/$updatefile") { system("rm -r \"$repository/$vendorid/$uuid\""); }
    }
    
    if (($xlratorsettings{'REMOVE_OUTDATED'} eq 'on') && ($status == $sfOutdated)) {
      if (-e "$repository/$vendorid/$uuid/$updatefile") { system("rm -r \"$repository/$vendorid/$uuid\""); }
    }
    
    if (($xlratorsettings{'REMOVE_UNKNOWN'} eq 'on') && ($status == $sfUnknown)) {
      if (-e "$repository/$vendorid/$uuid/$updatefile") { system("rm -r \"$repository/$vendorid/$uuid\""); }
    }

	if (($xlratorsettings{'NOT_ACCESSED_LAST'} eq 'week') && ($lastaccess < (time - 604800))) {
	  if (-e "$repository/$vendorid/$uuid/$updatefile") { system("rm -r \"$repository/$vendorid/$uuid\""); }
	}
	elsif (($xlratorsettings{'NOT_ACCESSED_LAST'} eq 'month1') && ($lastaccess < (time - 2505600))) {
	  if (-e "$repository/$vendorid/$uuid/$updatefile") { system("rm -r \"$repository/$vendorid/$uuid\""); }
	}
	elsif (($xlratorsettings{'NOT_ACCESSED_LAST'} eq 'month3') && ($lastaccess < (time - 7516800))) {
	  if (-e "$repository/$vendorid/$uuid/$updatefile") { system("rm -r \"$repository/$vendorid/$uuid\""); }
	}
	elsif (($xlratorsettings{'NOT_ACCESSED_LAST'} eq 'month6') && ($lastaccess < (time - 15033600))) {
	  if (-e "$repository/$vendorid/$uuid/$updatefile") { system("rm -r \"$repository/$vendorid/$uuid\""); }
	}
	elsif (($xlratorsettings{'NOT_ACCESSED_LAST'} eq 'year') && ($lastaccess < (time - 31536000))) {
	  if (-e "$repository/$vendorid/$uuid/$updatefile") { system("rm -r \"$repository/$vendorid/$uuid\""); }
	}

    
    if (($xlratorsettings{'REMOVE_TODELETE'} eq 'on') && ($xlratorsettings{'TODELETE'} ne 'off')) {
      my @todelete = split(/\|/, $xlratorsettings{'TODELETE'});
      foreach (@todelete) {
        unless ($_ =~ /^download\//) {
          ($vendorid,$uuid,$cachefile) = split(/\//, $_);
          if (-e "$repository/$vendorid/$uuid/$cachefile") { system("rm -r \"$repository/$vendorid/$uuid\""); }
        }
      }
    }
  }
}


# -------------------------------------------------------------------

sub printlegenddownload {
  print <<END
<h5>$Lang::tr{'legend'}:</h5>
<ul>
	<li id='liledbl' class='symbols' title='$Lang::tr{'updxlrtr condition download'}'>$Lang::tr{'updxlrtr condition download'}</li>
	<li id='liledgy' class='symbols' title='$Lang::tr{'updxlrtr condition suspended'}'>$Lang::tr{'updxlrtr condition suspended'}</li>
	<li id='lidel' class='symbols' title='$Lang::tr{'updxlrtr cancel download'}'>$Lang::tr{'updxlrtr cancel download'}</li>
</ul>
END
;
}

# -------------------------------------------------------------------

sub printlegendicons {
  print <<END
<h5>$Lang::tr{'legend'}:</h5>
<ul>
	<li id='lirel' class='symbols' title='$Lang::tr{'updxlrtr last access'}'>$Lang::tr{'updxlrtr last access'}</li>
	<li id='liglo' class='symbols' title='$Lang::tr{'updxlrtr last checkup'}'>$Lang::tr{'updxlrtr last checkup'}</li>
	<li id='lidel' class='symbols' title='$Lang::tr{'updxlrtr remove file'}'>$Lang::tr{'updxlrtr remove file'}</li>
</ul>
END
;
}

# -------------------------------------------------------------------

sub printlegendstatus {
  print <<END
<h5>$Lang::tr{'status'}:</h5>
<ul>
	<li id='liledgr' class='symbols' title='$Lang::tr{'updxlrtr condition ok'}'>$Lang::tr{'updxlrtr condition ok'}</li>
	<li id='liledye' class='symbols' title='$Lang::tr{'updxlrtr condition nosource'}'>$Lang::tr{'updxlrtr condition nosource'}</li>
	<li id='liledrd' class='symbols' title='$Lang::tr{'updxlrtr condition outdated'}'>$Lang::tr{'updxlrtr condition outdated'}</li>
	<li id='liledbl' class='symbols' title='$Lang::tr{'updxlrtr condition download'}'>$Lang::tr{'updxlrtr condition download'}</li>
	<li id='liledgy' class='symbols' title='$Lang::tr{'updxlrtr condition unknown'}'>$Lang::tr{'updxlrtr condition unknown'}</li>
</ul>
END
;
}

# -------------------------------------------------------------------

sub printlegendsource {
  print <<END
<h5>$Lang::tr{'updxlrtr sources'}:</h5>
<ul>
END
;
  foreach my $name (sort keys %vendimg) {
    if ($name =~ /^unknown$/i) {
      print "\t<li class='vendimg' style='background-image: url($vendimg{$name})' title='". ucfirst $Lang::tr{$name} ."'>". ucfirst $Lang::tr{$name} ."</li>\n";
    } else {
      print "\t<li class='vendimg' style='background-image: url($vendimg{$name})' title='". ucfirst $name ."'>". ucfirst $name ."</li>\n";
    }
  }
  print "</ul>\n";
}

# -------------------------------------------------------------------
# 2012-12-18:
# Seaching updbooster-image dir for all available images of format "updxl-src-<vendor>.gif"
# Build a hash in format '<vendor(name)>' -> '/images/updbooster/updxl-src-<vendor>.gif'

sub initvendimg {
  if (opendir(DIR, "$webhome$webimgdir")) {
    my @files = grep { /updxl-src-/ } readdir(DIR);
    my @vendor = ();
    closedir(DIR);
    foreach (@files) {
      @vendor = split (/[.-]/, $_);
      $vendimg{$vendor[2]} = "$webimgdir/$_";
    }
  }
  else {
      die "updxlrtr: Can't access \"$webhome$webimgdir\". Error was: $!\n";
  }
}
# -------------------------------------------------------------------

sub printtbldiskusage {
  my $tabletitle = shift;
  my $repos_ref=shift;
  print <<END
<table id='diskusage'>
<caption>$tabletitle</caption>
<thead>
	<tr>
		<th>$Lang::tr{'updxlrtr cache dir'}</th>
		<th>$Lang::tr{'size'}</th>
		<th>$Lang::tr{'updxlrtr total used'}</th>
		<th>$Lang::tr{'updxlrtr used by'}<br />[$repository]</th>
		<th>$Lang::tr{'free'}</th>
		<th>$Lang::tr{'percentage'}</th>
	</tr>
</thead>
END
;
  open(DF,"/bin/df -h $repository|");
  @dfdata = <DF>;
  $dudata = `/usr/bin/du -hs $repository`;
  close DF;
  shift(@dfdata);
  chomp(@dfdata);
  chomp($dudata);
  $dfstr = join(' ',@dfdata);
  my ($device,$size,$used,$free,$percent,$mount) = split(' ',$dfstr);
  my ($duused,$tmp) = split(' ',$dudata);
  print <<END
<tbody>
	<tr>
		<td>[$repository]</td>
		<td>$size</td>
		<td><span id="used">$used</span></td>
		<td><span id="duused">$duused</span></td>
		<td><span id="free">$free</span></td>
		<td>
END
;
	&percentbar(&cpof($duused,$size),&cpof($used,$size));
  print <<END
		</td>
	</tr>
</tbody>
</table>
END
;
}

# -------------------------------------------------------------------
# Initialize Cache-Settings Form
# -------------------------------------------------------------------

sub initfrmsettings {
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
  $selected{'VIEW_SETTING'}{'overview'} = '';
  $selected{'VIEW_SETTING'}{'statistics'} = '';
  $selected{'VIEW_SETTING'}{'maintenance'} = '';
  $selected{'VIEW_SETTING'}{'settings'} = '';
  $selected{'VIEW_SETTING'}{$xlratorsettings{'VIEW_SETTING'}} = "checked='checked'";
  $selected{'AUTOCHECK_SCHEDULE'}{'daily'} = '';
  $selected{'AUTOCHECK_SCHEDULE'}{'weekly'} = '';
  $selected{'AUTOCHECK_SCHEDULE'}{'monthly'} = '';
  $selected{'AUTOCHECK_SCHEDULE'}{$xlratorsettings{'AUTOCHECK_SCHEDULE'}} = "selected='selected'";
}

# -------------------------------------------------------------------
# Print Cache-Settings Form
# -------------------------------------------------------------------

sub printfrmsettings {
  print <<END
<form id='frmsettings' method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>
	<fieldset>
	<legend>$Lang::tr{'updxlrtr standard view'}</legend>
	<input id='radio01' type='radio' name='VIEW_SETTING' value='overview' $selected{'VIEW_SETTING'}{'overview'} />
	<label for='radio01'>$Lang::tr{'updxlrtr overview'}</label>
	<input id='radio02' type='radio' name='VIEW_SETTING' value='statistics' $selected{'VIEW_SETTING'}{'statistics'} />
	<label for='radio02'>$Lang::tr{'updxlrtr statistics'}</label>
	<input id='radio03' type='radio' name='VIEW_SETTING' value='maintenance' $selected{'VIEW_SETTING'}{'maintenance'} />
	<label for='radio03'>$Lang::tr{'updxlrtr maintenance'}</label>
	<input id='radio04' type='radio' name='VIEW_SETTING' value='settings' $selected{'VIEW_SETTING'}{'settings'} />
	<label for='radio04'>$Lang::tr{'updxlrtr settings'}</label>
	</fieldset>
	<fieldset>
	<legend>$Lang::tr{'updxlrtr common settings'}</legend>
		<input id='check01' type='checkbox' name='ENABLE_LOG' $checked{'ENABLE_LOG'}{'on'} />
		<label for='check01'>$Lang::tr{'updxlrtr enable log'}</label>
		<input id='check02' type='checkbox' name='PASSIVE_MODE' $checked{'PASSIVE_MODE'}{'on'} />
		<label for='check02'>$Lang::tr{'updxlrtr passive mode'}</label>
		<label for='text01'>$Lang::tr{'updxlrtr max disk usage'} (<output id='duval'>$xlratorsettings{'MAX_DISK_USAGE'}</output>%):</label>
		<input id='text01' type='range' name='MAX_DISK_USAGE' min='0' max='100' step='1' onchange='duval.value=value' value='$xlratorsettings{'MAX_DISK_USAGE'}' size='3' maxlength='4'/>
	</fieldset>
	<fieldset>
	<legend>$Lang::tr{'updxlrtr performance options'}</legend>
		<input id='check04' type='checkbox' name='LOW_DOWNLOAD_PRIORITY' $checked{'LOW_DOWNLOAD_PRIORITY'}{'on'} />
		<label for='check04'>$Lang::tr{'updxlrtr low download priority'}</label>
		<label for='text02' >$Lang::tr{'updxlrtr max download rate'}:</label>
		<input id='text02' type='number' name='MAX_DOWNLOAD_RATE' title='$Lang::tr{'updxlrtr notice dlrate'}' min='0' max='1000000' step='16' value='$xlratorsettings{'MAX_DOWNLOAD_RATE'}' size='5' />
	</fieldset>
	<fieldset>
	<legend>$Lang::tr{'updxlrtr source checkup'}</legend>
		<input id='check06' type='checkbox' name='ENABLE_AUTOCHECK' $checked{'ENABLE_AUTOCHECK'}{'on'} />
		<label for='check06'>$Lang::tr{'updxlrtr enable autocheck'}</label>
		<label for='select01'>$Lang::tr{'updxlrtr source checkup schedule'}:</label>
		<select id='select01' name='AUTOCHECK_SCHEDULE'>
			<option value='daily' $selected{'AUTOCHECK_SCHEDULE'}{'daily'}>$Lang::tr{'updxlrtr daily'}</option>
			<option value='weekly' $selected{'AUTOCHECK_SCHEDULE'}{'weekly'}>$Lang::tr{'updxlrtr weekly'}</option>
			<option value='monthly' $selected{'AUTOCHECK_SCHEDULE'}{'monthly'}>$Lang::tr{'updxlrtr monthly'}</option>
		</select>
		<br />
		<input id='check07' type='checkbox' name='FULL_AUTOSYNC' $checked{'FULL_AUTOSYNC'}{'on'} />
		<label for='check07'>$Lang::tr{'updxlrtr full autosync'}</label>
	</fieldset>
	<fieldset style='border:0'>
		<input type='submit' name='ACTION' value='$Lang::tr{'save'}' />
		<input type='submit' name='ACTION' value='$Lang::tr{'updxlrtr save and restart'}' />
	</fieldset>
</form>
END
;
}

# -------------------------------------------------------------------
# chksettings([save|restart]) - Check settings and/or restart proxy
# -------------------------------------------------------------------

sub chksettings {
  my $param = shift;
  my $error_ref = shift;
  if ( $param =~ /save/i ) {
    if (!($xlratorsettings{'MAX_DISK_USAGE'} =~ /^\d+$/)
      || ($xlratorsettings{'MAX_DISK_USAGE'} < 1)
      || ($xlratorsettings{'MAX_DISK_USAGE'} > 100)) {
      push(@$error_ref, $Lang::tr{'updxlrtr invalid disk usage'});
    }
    if (($xlratorsettings{'MAX_DOWNLOAD_RATE'} ne '') && ((!($xlratorsettings{'MAX_DOWNLOAD_RATE'} =~ /^\d+$/))
      || ($xlratorsettings{'MAX_DOWNLOAD_RATE'} < 1))) {
      push(@$error_ref, $Lang::tr{'updxlrtr invalid download rate'});
    }
    unless (@$error_ref >= 1) { &savesettings; }
  }
  if ($param =~ /restart/i ) {
    if ((!(-e "${General::swroot}/proxy/enable")) && (!(-e "${General::swroot}/proxy/enable_blue"))) {
      push(@$error_ref, $Lang::tr{'updxlrtr web proxy service required'});
    }
    if ($proxysettings{'ENABLE_UPDXLRATOR'} ne 'on') {
      push(@$error_ref, $Lang::tr{'updxlrtr not enabled'});
    }
    unless (@$error_ref >= 1) { system('/usr/local/bin/squidctrl restart > /dev/null 2>&1'); }
  }
  unless (@$error_ref == 0) { &initfrmsettings; }
}

# -------------------------------------------------------------------

sub savesettings {
  if (($xlratorsettings{'ENABLE_AUTOCHECK'} eq 'on') && ($xlratorsettings{'AUTOCHECK_SCHEDULE'} eq 'daily'))
    { system('/usr/local/bin/updxlratorctrl cron daily >/dev/null 2>&1'); }
  if (($xlratorsettings{'ENABLE_AUTOCHECK'} eq 'on') && ($xlratorsettings{'AUTOCHECK_SCHEDULE'} eq 'weekly'))
    { system('/usr/local/bin/updxlratorctrl cron weekly >/dev/null 2>&1'); }
  if (($xlratorsettings{'ENABLE_AUTOCHECK'} eq 'on') && ($xlratorsettings{'AUTOCHECK_SCHEDULE'} eq 'monthly'))
  { system('/usr/local/bin/updxlratorctrl cron monthly >/dev/null 2>&1'); }

  # don't save those variable to the settings file,
  # but we wan't to have them in the hash again after saving to file
  my $obsolete = $xlratorsettings{'REMOVE_UNKNOWN'};
  my $nosource = $xlratorsettings{'REMOVE_NOSOURCE'};
  my $outdated = $xlratorsettings{'REMOVE_OUTDATED'};
  my $todelete = $xlratorsettings{'REMOVE_TODELETE'};
  my $gui = $xlratorsettings{'EXTENDED_GUI'};
  my $show = $xlratorsettings{'show'};

  delete($xlratorsettings{'REMOVE_UNKNOWN'});
  delete($xlratorsettings{'REMOVE_NOSOURCE'});
  delete($xlratorsettings{'REMOVE_OUTDATED'});
  delete($xlratorsettings{'REMOVE_TODELETE'});
  delete($xlratorsettings{'TODELETE'});
  delete($xlratorsettings{'EXTENDED_GUI'});
  delete($xlratorsettings{'show'});

  &General::writehash("${General::swroot}/updatexlrator/settings", \%xlratorsettings);

  # put temp variables back into the hash
  $xlratorsettings{'REMOVE_UNKNOWN'} = $obsolete;
  $xlratorsettings{'REMOVE_NOSOURCE'} = $nosource;
  $xlratorsettings{'REMOVE_OUTDATED'} = $outdated;
  $xlratorsettings{'REMOVE_TODELETE'} = $todelete;
  $xlratorsettings{'EXTENDED_GUI'} = $gui;
  $xlratorsettings{'show'} = $show;
}


# -------------------------------------------------------------------
# percentbar(number[, number2, number(n)) - need absolute values
# - print relative bars ([##1][##2(number2-number1)][#n-#2-#1]...)
# -------------------------------------------------------------------

sub percentbar {
  $counts = '0';
  my $width = '-0';	# width of value bar
  my $widthmax = '-0';	# overall width
  my $tmp = '';
  my @tmplst;
  my $sf = 1;		# scale-factor
  print "<div id='pbar'>";
  @_ = sort{ $a <=> $b } @_;
  for  (@_) {
	unless ($widthmax <= 100.0) { next; };
	$width = $_-($widthmax);
	$widthmax = $_;
	if (($width > 0) && ($width < 1)) { $width=1; }
	$tmp .= "<div id='bar$counts' style='width:".(sprintf("%0.2f",$width))*$sf."%'></div>\n";
	$counts = $counts + 1;
	}
	$widthmax = sprintf("%0d",$widthmax);
	if ( $widthmax < 79) { $tmp .= "<span id='percent'>$widthmax%</span>\n"; }
    else { $tmp .= "<span id='max'>$widthmax%</span>\n"; }
  
  print "\t\t$tmp</div>\n";
  return;
}

# -------------------------------------------------------------------
# Format given filesize in Bits
# into values of more human readable format like kB, MB, GB, etc
# take filesize in Bit, returns formatted string in example "xx.xx kB"
# No roundings are happened,
# so counting with the output may result in wrong values
# -------------------------------------------------------------------

sub format_size{
  my $fsize = shift;
  
  if ($fsize > 2**60)		#   EB: 1024 PB
	{ return sprintf("%.2f EB", $fsize / 2**40); }
  elsif ($fsize > 2**50)	#   PB: 1024 TB
	{ return sprintf("%.2f PB", $fsize / 2**40); }
  elsif ($fsize > 2**40)	#   TB: 1024 GB
	{ return sprintf("%.2f TB", $fsize / 2**40); }
  elsif ($fsize > 2**30)	#   GB: 1024 MB
	{ return sprintf("%.2f GB", $fsize / 2**30); }
  elsif ($fsize > 2**20)	#   MB: 1024 kB
	{ return sprintf("%.2f MB", $fsize / 2**20); }
  elsif ($fsize > 2**10)	#   kB: 1024 B
	{ return sprintf("%.2f KB", $fsize / 2**10); }
  else                       #   Bytes
	{ return "$fsize B"; }
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
    { if (/$_[0]/) { ($pid)=/^\s*(\d+)/; } }
  return $pid;
}

# -------------------------------------------------------------------
# Calculating Percentage of 2 Values (for percentbar)
# -------------------------------------------------------------------

sub cpof {
	my $Value;
	my $MValue;
	my $result;	
	my $Vsize;
	my $MVsize;
	my $corf;
	my $callme = "cpof\(value[B|K|M|G|T|P|E], maxvalue[B|K|M|G|T|P|E]\)";
	$Value = shift;
	$MValue = shift;
	my %cf = ('B'=>0,'K'=>1,'M'=>2,'G'=>3,'T'=>4,'P'=>5,'E'=>6);
	unless ('$Value' ne '') { die "updxlrtr sub cpof: value not given: $!\n$callme"; }
	unless ('$MValue' ne '') { die "updxlrtr sub cpof: maxvalue not given: $!\n$callme"; }
	
	unless ($Value =~ /\d+(B|K|M|G|T|P|E)/) { die "updxlrtr: cpof() - value has no size!\nPossible Values: 'number[B|K|M|G|T|P|E]'\n"; }
	else { $Vsize = chop $Value; }
	unless ($MValue =~ /\d+(B|K|M|G|T|P|E)/) { die "updxlrtr: cpof(): maxvalue has no size!\nPossible Values: 'number[B|K|M|G|T|P|E]'\n"; }
	else { $MVsize = chop $MValue; }
	
	if ('$Vsize' eq '$MVsize') { $result = (100/$MValue)*$Value; }
	else {
		if ($Value =~ /^0\.d+/) { $corf = 1; }
		else { $corf = '0'; }
	}
	my $tmp = (100/($MValue*(2**(10*$cf{$MVsize}))))*($Value*(2**(10*($cf{$Vsize}-$corf))));
	$tmp = sprintf ("%.2f", $tmp);
	return $tmp;
}
