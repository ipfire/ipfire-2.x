#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2005-2013  IPFire Team  <info@ipfire.org>                     #
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
use File::Basename;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %color = ();
my %mainsettings = ();
my %cgiparams=();
my %checked = ();
my $message = "";
my $errormessage = "";
my @backups = "";
my @backupisos = "";

$a = new CGI;

&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

$cgiparams{'ACTION'} = '';
$cgiparams{'FILE'} = '';
$cgiparams{'UPLOAD'} = '';
$cgiparams{'BACKUPLOGS'} = '';

&Header::getcgihash(\%cgiparams);

############################################################################################################################
################################################ Workaround for Directories ################################################

system("/usr/local/bin/backupctrl makedirs >/dev/null 2>&1 ") unless ( -e '/var/ipfire/backup/addons/backup') ;

############################################################################################################################
############################################## System calls ohne Http Header ###############################################

if ($cgiparams{'ACTION'} eq "download") {
		my $file = &sanitise_file($cgiparams{'FILE'});
		exit(1) unless defined($file);

		&deliver_file($file);
		exit(0);
} elsif ($cgiparams{'ACTION'} eq "downloadiso") {
		my $file = &sanitise_file($cgiparams{'FILE'});
		exit(1) unless defined($file);

		&deliver_file($file);
		exit(0);
} elsif ($cgiparams{'ACTION'} eq "downloadaddon") {
		my $file = &sanitise_file($cgiparams{'FILE'});
		exit(1) unless defined($file);

		&deliver_file($file);
		exit(0);
} elsif ( $cgiparams{'ACTION'} eq "restore") {
		my $upload = $a->param("UPLOAD");
		open UPLOADFILE, ">/tmp/restore.ipf";
		binmode $upload;
		while ( <$upload> ) {
		print UPLOADFILE;
		}
		close UPLOADFILE;
		system("/usr/local/bin/backupctrl restore >/dev/null 2>&1");
}
elsif ( $cgiparams{'ACTION'} eq "restoreaddon" )
{
    chomp($cgiparams{'UPLOAD'});
    # we need to fix cause IE7 gives the full path and FF only the filename
    my @temp = split(/\\/,$cgiparams{'UPLOAD'});
		my $upload = $a->param("UPLOAD");
		open UPLOADFILE, ">/tmp/".$temp[$#temp];
		binmode $upload;
		while ( <$upload> ) {
		print UPLOADFILE;
		}
		close UPLOADFILE;
		system("/usr/local/bin/backupctrl restoreaddon ".$temp[$#temp]." >/dev/null 2>&1");
}

&Header::showhttpheaders();

sub refreshpage{&Header::openbox( 'Waiting', 1, "<meta http-equiv='refresh' content='1;'>" );print "<center><img src='/images/clock.gif' alt='' /><br/><font color='red'>$Lang::tr{'pagerefresh'}</font></center>";&Header::closebox();}

&Header::openpage($Lang::tr{'backup'}, 1, "");
&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
################################################### Default System calls ###################################################

if ( $cgiparams{'ACTION'} eq "backup" )
{
	if ( $cgiparams{'BACKUPLOGS'} eq "include" ) {
		system("/usr/local/bin/backupctrl include >/dev/null 2>&1");
	} elsif ( $cgiparams{'BACKUPLOGS'} eq "exclude" ) {
		system("/usr/local/bin/backupctrl exclude >/dev/null 2>&1");
	} elsif ( $cgiparams{'BACKUPLOGS'} eq "iso" ) {
		system("/usr/local/bin/backupctrl iso >/dev/null 2>&1");
	}
}
if ( $cgiparams{'ACTION'} eq "addonbackup" )
{
	# Exit if there is any dots or slashes in the addon name
	exit(1) if ($cgiparams{'ADDON'} =~ /(\.|\/)/);

	# Check if the addon exists
	exit(1) unless (-e "/var/ipfire/backup/addons/includes/$cgiparams{'ADDON'}");

	system("/usr/local/bin/backupctrl addonbackup $cgiparams{'ADDON'} >/dev/null 2>&1");
}
elsif ( $cgiparams{'ACTION'} eq "delete" )
{
	my $file = &sanitise_file($cgiparams{'FILE'});
	exit(1) unless defined($file);

	system("/usr/local/bin/backupctrl $file >/dev/null 2>&1");
}

############################################################################################################################
############################################ Backups des Systems erstellen #################################################

if ( $message ne "" ){
	&Header::openbox('100%','left',$Lang::tr{'error messages'});
	print "<font color='red'>$message</font>\n";
	&Header::closebox();
}

if ( -e "/var/ipfire/backup/" ){
	@backups = `cd /var/ipfire/backup/ && ls *.ipf 2>/dev/null`;
}

if ( -e "/var/tmp/backupiso/" ){
	@backupisos = `cd /var/tmp/backupiso/ && ls *.iso 2>/dev/null`;
}

&Header::openbox('100%', 'center', );

print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='95%' cellspacing='0'>
<tr>
	<td align='left' width='40%'>$Lang::tr{'logs'}</td>
	<td align='left'>
		<input type='radio' name='BACKUPLOGS' value='include'/> $Lang::tr{'include logfiles'}<br/>
		<input type='radio' name='BACKUPLOGS' value='exclude' checked='checked'/> $Lang::tr{'exclude logfiles'}<br/>
END
;
my $MACHINE=`uname -m`;
if ( ! ( $MACHINE =~ "arm" )) {
	print"		<input type='radio' name='BACKUPLOGS' value='iso' /> $Lang::tr{'generate iso'}<br/>"
}
print <<END
	</td>
</tr>
<tr><td align='center' colspan='2'>
	<input type='hidden' name='ACTION' value='backup' />
	<input type='image' alt='$Lang::tr{'backup'}' title='$Lang::tr{'backup'}' src='/images/document-save.png' />
</td></tr>
</table>
</form>
END
;
&Header::closebox();

############################################################################################################################
############################################ Backups des Systems downloaden ################################################

&Header::openbox('100%', 'center', $Lang::tr{'backups'});

print <<END
<table width='95%' cellspacing='0'>
END
;
foreach (@backups){
if ( $_ !~ /ipf$/){next;}
chomp($_);
my $Datei = "/var/ipfire/backup/".$_;
my @Info = stat($Datei);
my $Size = $Info[7] / 1024 / 1024;
$Size = sprintf("%0.2f", $Size);
print "<tr><td align='center'>$Lang::tr{'backup from'} $_ $Lang::tr{'size'} $Size MB</td><td width='5'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='download' /><input type='hidden' name='FILE' value='$_' /><input type='image' alt='$Lang::tr{'download'}' title='$Lang::tr{'download'}' src='/images/package-x-generic.png' /></form></td>";
print "<td width='5'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='delete' /><input type='hidden' name='FILE' value='$_' /><input type='image' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' src='/images/user-trash.png' /></form></td></tr>";
}
foreach (@backupisos){
if ( $_ !~ /iso$/){next;}
chomp($_);
my $Datei = "/var/tmp/backupiso/".$_;
my @Info = stat($Datei);
my $Size = $Info[7] / 1024 / 1024;
$Size = sprintf("%0.2f", $Size);
print "<tr><td align='center'>$Lang::tr{'backup from'} $_ $Lang::tr{'size'} $Size MB</td><td width='5'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='downloadiso' /><input type='hidden' name='FILE' value='$_' /><input type='image' alt='$Lang::tr{'download'}' title='$Lang::tr{'download'}' src='/images/package-x-generic.png' /></form></td>";
print "<td width='5'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='delete' /><input type='hidden' name='FILE' value='$_' /><input type='image' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' src='/images/user-trash.png' /></form></td></tr>";
}
print <<END
</table>
END
;
&Header::closebox();

############################################################################################################################
############################################# Backups von Addons erstellen #################################################

&Header::openbox('100%', 'center', $Lang::tr{'addons'});

my @addonincluds = `ls /var/ipfire/backup/addons/includes/ 2>/dev/null`;
my @addons = `ls /var/ipfire/backup/addons/backup/ 2>/dev/null`;
my %addons;

foreach (@addons){
	my $addon=substr($_,0,length($_)-5);
	$addons{$addon}='';
}

print "<table width='95%' cellspacing='0'>";
foreach (@addonincluds){
chomp($_);
delete $addons{$_};
my $Datei = "/var/ipfire/backup/addons/backup/".$_.".ipf";
my @Info = stat($Datei);
my $Size = $Info[7] / 1024;

if ( -e $Datei ){
	if ($Size < 1) {
			$Size = sprintf("%.2f", $Size);
			print "<tr><td align='center'>$Lang::tr{'backup from'} $_ $Lang::tr{'size'} $Size KB $Lang::tr{'date'} ".localtime($Info[9])."</td>";
	} else {
			$Size = sprintf("%2d", $Size);
			print "<tr><td align='center'>$Lang::tr{'backup from'} $_ $Lang::tr{'size'} $Size KB $Lang::tr{'date'} ".localtime($Info[9])."</td>";

	}

print <<END
	<td align='right' width='5'>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<input type='hidden' name='ACTION' value='downloadaddon' />
		<input type='hidden' name='FILE' value='$_.ipf' />
		<input type='image' alt='$Lang::tr{'download'}' title='$Lang::tr{'download'}' src='/images/package-x-generic.png' />
		</form>
	</td>
	<td align='right' width='5'>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<input type='hidden' name='ACTION' value='delete' />
		<input type='hidden' name='FILE' value='$_.ipf' />
		<input type='image' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' src='/images/user-trash.png' />
		</form>
	</td>
END
;
}
else{
  print "<tr><td align='center'>$Lang::tr{'backup from'} $_ </td><td width='5' align='right'></td><td width='5' align='right'></td>";
}
print <<END
	<td align='right' width='5'>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<input type='hidden' name='ACTION' value='addonbackup' />
		<input type='hidden' name='ADDON' value='$_' />
		<input type='image' alt='$Lang::tr{'backup'}' title='$Lang::tr{'backup'}' src='/images/document-save.png' />
		</form>
	</td></tr>
END
;
}
foreach (keys(%addons)){
chomp($_);
my $Datei = "/var/ipfire/backup/addons/backup/".$_.".ipf";
my @Info = stat($Datei);
my $Size = $Info[7] / 1024;
$Size = sprintf("%2d", $Size);
print "<tr><td align='center'>$Lang::tr{'backup from'} $_ $Lang::tr{'size'} $Size KB $Lang::tr{'date'} ".localtime($Info[9])."</td>";
print <<END
	<td align='right' width='5'>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<input type='hidden' name='ACTION' value='downloadaddon' />
		<input type='hidden' name='FILE' value='$_.ipf' />
		<input type='image' alt='$Lang::tr{'download'}' title='$Lang::tr{'download'}' src='/images/package-x-generic.png' />
		</form>
	</td>
	<td align='right' width='5'>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<input type='hidden' name='ACTION' value='delete' />
		<input type='hidden' name='FILE' value='$_.ipf' />
		<input type='image' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' src='/images/user-trash.png' />
		</form>
	</td>
	<td align='right' width='5'></td></tr>
END
;
}

print "</table>";
&Header::closebox();

############################################################################################################################
####################################### Backups des Systems wiederherstellen ###############################################

&Header::openbox('100%', 'center', $Lang::tr{'restore'});

print <<END
<table width='95%' cellspacing='0'>
<tr><td align='center' colspan='2'><font color='red'><br />$Lang::tr{'backupwarning'}</font><br /><br /></td></tr>
<tr><td align='left'>$Lang::tr{'backup'}</td><td align='left'><form method='post' enctype='multipart/form-data' action='$ENV{'SCRIPT_NAME'}'><input type="file" size='50' name="UPLOAD" /><input type='hidden' name='ACTION' value='restore' /><input type='hidden' name='FILE' /><input type='image' alt='$Lang::tr{'restore'}' title='$Lang::tr{'restore'}' src='/images/media-floppy.png' /></form></td></tr>
<tr><td align='left'>$Lang::tr{'backupaddon'}</td><td align='left'><form method='post' enctype='multipart/form-data' action='$ENV{'SCRIPT_NAME'}'><input type="file" size='50' name="UPLOAD" /><input type='hidden' name='ACTION' value='restoreaddon' /><input type='hidden' name='FILE' /><input type='image' alt='$Lang::tr{'restore'}' title='$Lang::tr{'restore'}' src='/images/media-floppy.png' /></form></td></tr>
</table>
END
;
&Header::closebox();
&Header::closebigbox();
&Header::closepage();

sub sanitise_file() {
	my $file = shift;

	# Filenames cannot contain any slashes
	return undef if ($file =~ /\//);

	# File must end with .ipf or .iso
	return undef unless ($file =~ /\.(ipf|iso)$/);

	# Convert to absolute path
	if (-e "/var/ipfire/backup/$file") {
		return "/var/ipfire/backup/$file";
	} elsif (-e "/var/ipfire/backup/addons/backup/$file") {
		return "/var/ipfire/backup/addons/backup/$file";
	} elsif (-e "/var/tmp/backupiso/$file") {
		return "/var/tmp/backupiso/$file";
	}

	# File does not seem to exist
	return undef;
}

sub deliver_file() {
	my $file = shift;
	my @stat = stat($file);

	# Print headers
	print "Content-Disposition: attachment; filename=" . &File::Basename::basename($file) . "\n";
	print "Content-Type: application/octet-stream\n";
	print "Content-Length: $stat[7]\n";
	print "\n";

	# Deliver content
	open(FILE, "<$file") or die "Unable to open $file: $!";
	print <FILE>;
	close(FILE);
}
