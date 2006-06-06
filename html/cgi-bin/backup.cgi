#!/usr/bin/perl
#
# IPFire CGI's - backup.cgi: manage import/export of configuration files
#
# This code is distributed under the terms of the GPL
#
# (c) The IPFire Team
# 2005	Franck Bourdonnec, major rewrite
#
# $Id: backup.cgi,v 1.2.2.15 2006/01/29 15:31:49 eoberlander Exp $
#
#


# to fully troubleshot your code, uncomment diagnostics, Carp and cluck lines
# use diagnostics; # need to add the file /usr/lib/perl5/5.8.x/pods/perldiag.pod before to work
# next look at /var/log/httpd/error_log , http://www.perl.com/pub/a/2002/05/07/mod_perl.html may help
#use warnings;
use strict;
#use Carp ();
#local $SIG{__WARN__} = \&Carp::cluck;
use File::Copy;
use Sys::Hostname;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my $errormessage = '';
my $warnmessage = '';
my $setdir = '/home/httpd/html/backup'; # location where sets are stored and imported
my $datafile = hostname() . '.dat';	# file containing data backup
my $datefile = $datafile . '.time';	# and creation date

# ask if backup crypting key exists
my $tmpkeyfile = "$setdir/key";		# import the backup key

# Get GUI values
my %settings = ();
&Header::getcgihash(\%settings, {'wantfile' => 1, 'filevar' => 'FH'});

##
## Backup key management
##

#
# Export the key. root pw is required to avoid user 'noboby' uses the helper to read it and creates
# fake backup.
#
if ($settings{'ACTION'} eq $Lang::tr{'backup export key'})  {

    my $size = 0;
    if ($settings{'PASSWORD1'} ne '' && $settings{'PASSWORD1'} ne $settings{'PASSWORD2'} ){
	$errormessage = $Lang::tr{'passwords do not match'}
    } else {
	my @lines = `/usr/local/bin/ipfirebackup -keycat $settings{'PASSWORD'}`;
	# If previous operation succeded and the key need to be crypted, redo operation with pipe to openssl
	if (@lines && $settings{'PASSWORD1'}) {
	    @lines = `/usr/local/bin/ipfirebackup -keycat $settings{'PASSWORD'}|openssl enc -a -e -aes256 -salt -pass pass:$settings{'PASSWORD1'} `;
	}
        if (@lines) {
    	    use bytes;
	    foreach (@lines) {$size += length($_)};
	    print "Pragma: no-cache\n";
	    print "Cache-control: no-cache\n";
	    print "Connection: close\n";
	    print "Content-type: application/octet-stream\n";
    	    print "Content-Disposition: filename=backup.key\n";
    	    print "Content-Length: $size\n\n";
    	    print @lines;
    	    exit (0);
	} else {
	    $errormessage = $Lang::tr{'incorrect password'};
	}
    }	
}
#
#  Import the key. Fail if key exists. This avoid creating fake backup.
#
if ($settings{'ACTION'} eq $Lang::tr{'backup import key'})  {
    if (ref ($settings{'FH'}) ne 'Fh') {
	$errormessage = $Lang::tr{'no cfg upload'};
    } else {
	if (copy ($settings{'FH'}, $tmpkeyfile) != 1) {
	    $errormessage = $Lang::tr{'save error'};
	} else {
	    # if a password is given, decrypt the key received in $tmpkeyfile file with it.
	    # no error is produce if the password is wrong.
	    if ($settings{'PASSWORD1'}) {
		my @lines = `openssl enc -a -d -aes256 -salt -pass pass:$settings{'PASSWORD1'} -in $tmpkeyfile`;
		open(FILE,">$tmpkeyfile");
		print FILE @lines;
		close (FILE);
	    }
	    $errormessage = &get_bk_error(system ('/usr/local/bin/ipfirebackup -key import')>>8);
	}
    }
}
#
#  Import the key. Fail if key exists. Key is extracted from a non-encrypted backup (pre 1.4.10)
#
if ($settings{'ACTION'} eq $Lang::tr{'backup extract key'})  {
    if (ref ($settings{'FH'}) ne 'Fh') {
	$errormessage = $Lang::tr{'no cfg upload'};
    } else {
	if (copy ($settings{'FH'}, '/tmp/tmptarfile.tgz') != 1) {
	    $errormessage = $Lang::tr{'save error'};
	} else {
	    system( "tar -C /tmp -xzf /tmp/tmptarfile.tgz */backup/backup.key;\
	    	    mv -f /tmp${General::swroot}/backup/backup.key $tmpkeyfile;\
	    	    rm -rf /tmp${General::swroot};\
		    rm /tmp/tmptarfile.tgz");
	    $errormessage = &get_bk_error(system ('/usr/local/bin/ipfirebackup -key import')>>8);
	}
    }
}
#
#  Create the key. Cannot overwrite existing key to avoid difference with exported (saved) key
#
if ($settings{'ACTION'} eq $Lang::tr{'backup generate key'})  {
    $errormessage = &get_bk_error(system('/usr/local/bin/ipfirebackup -key new')>>8);
}

my $cryptkeymissing = system ('/usr/local/bin/ipfirebackup -key exist')>>8;

&Header::showhttpheaders();
if ($cryptkeymissing) {  #If no key is present, force creation or import
    &Header::openpage($Lang::tr{'backup configuration'}, 1, '');
    &Header::openbigbox('100%', 'left', '', $errormessage);
    if ($errormessage) {
	&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
	print "<font class='base'>$errormessage&nbsp;</font>";
	&Header::closebox();
    }
    &Header::openbox('100%', 'left', $Lang::tr{'backup key'});
    print <<END
    <form method = 'post' enctype = 'multipart/form-data'>
      <table>
        <tr>
	  <td colspan='2'>
	  $Lang::tr{'backup explain key'}:
	  <ul>
	  <li>$Lang::tr{'backup explain key li1'}
	  <li>$Lang::tr{'backup explain key li2'}
	  <li>$Lang::tr{'backup explain key li3'}
	  </ul>
          </td>
	</tr><tr>
	  <td width='15%'></td><td width='20%'></td><td>
	  <input type = 'submit' name = 'ACTION' value = '$Lang::tr{'backup generate key'}' />
          </td>
	</tr><tr>
	  <td align='right'>$Lang::tr{'backup key file'}:</td><td><input type = 'file' name = 'FH' size = '30' value='backup.key' />
	  </td><td>
	  <input type = 'submit' name = 'ACTION' value = '$Lang::tr{'backup import key'}' />
	</tr><tr>
	  <td align='right'>$Lang::tr{'backup protect key password'}:<td><input type = 'password' name='PASSWORD1' size='10' />
          </td>
	</tr><tr>
	  <td align='right'>$Lang::tr{'backup clear archive'}:</td><td><input type = 'file' name = 'FH' size = '30' value='your-ipfire.tar.gz' />
	  </td><td>
	  <input type = 'submit' name = 'ACTION' value = '$Lang::tr{'backup extract key'}' />
          </td>
	</tr>
      </table>
      $Lang::tr{'notes'}:
      <ul>
	  <li>$Lang::tr{'backup explain key no1'}
	  <li>$Lang::tr{'backup explain key no2'}
      </ul>
    </form>
END
;
    &floppybox();
    &Header::closebox();
    &Header::closebigbox();
    &Header::closepage();
    exit (0);
}

##
## Sets management (create/delete/import/restore)
##

erase_files ($setdir);			#clean up

#
# create new archive set
#
if ($settings{'ACTION'} eq $Lang::tr{'create'}) {
    $errormessage = &get_bk_error(system('/usr/local/bin/ipfirebkcfg > /dev/null')>>8);
    &import_set (" ".&Header::cleanhtml ($settings{'COMMENT'})) if (!$errormessage);
}
#
# delete a backup set
#
if ($settings{'ACTION'} eq $Lang::tr{'remove'}) {
    erase_files (&Header::cleanhtml ($settings{'KEY'}));	# remove files
    rmdir($settings{'KEY'});		# remove directory
}
#
# import an archive set
#
if ($settings{'ACTION'} eq $Lang::tr{'import'}) {
    if (ref ($settings{'FH'}) ne 'Fh') {
	$errormessage = $Lang::tr{'no cfg upload'};
    } else {
	if (!copy ($settings{'FH'}, "$setdir/$datafile")) {
	    $errormessage = $Lang::tr{'save error'};
	} else {
	    &import_set ('&nbsp;(imported)');
	}
    }
}
#
# restore an archive
#
if ($settings{'ACTION'} eq $Lang::tr{'restore'}) {
    if ($settings{'AreYouSure'} eq 'yes') {
	if (!$cryptkeymissing) {   			# if keyfile exists
	    if (-e "$settings{'KEY'}/$datafile"){   	# encrypted dat is required
    		copy_files($settings{'KEY'}, $setdir);	# to working dir
        	$errormessage = get_rs_error(system("/usr/local/bin/ipfirerscfg" 
					. ($settings{'RESTOREHW'} eq 'on' ? ' --hardware' : '') 
					. ' >/dev/null')>>8);
		if (!$errormessage) {
		    # restored ok, recommend restarting system
		    $warnmessage = $Lang::tr{'cfg restart'};
		}
		erase_files ($setdir);			#clean up
	    } else {
		$errormessage = $Lang::tr{'missing dat'}."$settings{'KEY'}/$datafile";
	    }
	} else {  # if keyfile does not exist
	    $errormessage = $Lang::tr{'backup missing key'};
	}
    
    } else {  # not AreYouSure=yes
	&Header::openpage($Lang::tr{'backup configuration'}, 1, '');
	&Header::openbigbox('100%', 'left');
	&Header::openbox('100%', 'left', $Lang::tr{'are you sure'});
	print <<END
<form method = 'post'>
  <input type = 'hidden' name = 'KEY' value ='$settings{'KEY'}' /> 
  <input type = 'hidden' name = 'AreYouSure' value ='yes' />
  <table align = 'center'>
    <tr>
      <td align = 'center'>
	<input type = 'submit' name = 'ACTION' value = '$Lang::tr{'restore'}' />
      </td><td>
	<input type = 'submit' name = 'ACTION' value = '$Lang::tr{'cancel'}' />
      </td>
    </tr><tr>
      <td>
	$Lang::tr{'restore hardware settings'}: <input type = 'checkbox' name = 'RESTOREHW'>
      </td>
    </tr>
</table>
</form>
END
;
	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit (0);
    }
}
##
##  Media management
##
#
# now build the list of removable device
#

# Read partitions sizes registered with the system
my %partitions;
foreach my $li (`/usr/local/bin/ipfirebackup -proc partitions`) {		# use suid helper...
    # partitions{'sda1'} = 128M        if         /major minor  blocks name/
    $partitions{$4} = &kmgt($3*1024,4) if ($li =~ /(\d+) +(\d+) +(\d+) +(.*)/);
}

# Search usb-storage scsi device
my %medias;
    
foreach (`/usr/local/bin/ipfirebackup -glob '/proc/scsi/usb-storage*/*'`) {# use suid helper...
    my $m;
    foreach ( `cat $_` ) {	# list each line of information for the device:
#	Host scsi0: usb-storage
#	Vendor: SWISSBIT
#	Product: Black Silver
#	Serial Number: D0ED423A4F84A31E
#	Protocol: Transparent SCSI
#	Transport: Bulk
#	GUID: 13706828d0ed423a4f84a31e
#	Attached: Yes
				       
	chomp;
	my ($key,$val) = split(': ',$_,2);
	$key =~ s/^ *//;	# remove front space

	# convert 'scsi?' key to sda, sdb,... and use it as a %medias keyhash
	if ($key =~ /Host scsi(.)/) {
	    $val = $m = 'sd' . chr(97+$1);
	    $key = 'Host';
	}
	$medias{$m}{$key} = $val;		# save data
    }
}

#
# Switch mounted media
#
if ($settings{'ACTION'} eq $Lang::tr{'mount'})
{
    # Find what is really mounted under backup. Can be local hard disk or any removable media
    my $mounted = &findmounted();
    #umount previous, even if same device already mouted.
    system ("/usr/local/bin/ipfirebackup -U $mounted") if ($mounted ne $Lang::tr{'local hard disk'});
    $errormessage = `/usr/local/bin/ipfirebackup -M $settings{'SELECT'}` if (grep (/$settings{'SELECT'}/,%partitions));
}
#
# Compute a full description of device
#
my $mounted = &findmounted();
my $media_des = $mounted;	# Description
if ($mounted ne $Lang::tr{'local hard disk'}) {
    $_ = $mounted;	# sda1 => sda
    tr/0-9//d;
    $media_des = "$medias{$_}{'Product'} ($media_des, $partitions{$mounted})";
}
&Header::openpage($Lang::tr{'backup configuration'}, 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
    &Header::openbox('100%', 'left', $Lang::tr{'error messages'});
    print "<font class='base'>$errormessage&nbsp;</font>";
    &Header::closebox();
}

$warnmessage = "<font color=${Header::colourred}><b>$Lang::tr{'capswarning'}</b></font>: $warnmessage <p>" if ($warnmessage);

&Header::openbox('100%', 'left', $Lang::tr{'backup configuration'});

#Divide the window in two : left and right
print <<END
    <table width = '100%' >
    <tr>
	<th width = '50%'>$Lang::tr{'current media'}:<font color=${Header::colourred}><b>$media_des</b></font></th>
	<th width = '3%'></th>
	<th>$Lang::tr{'choose media'}</th>
    </tr>
END
;

# Left part of window
print <<END
    <tr><td>
    <ul>
    <li>$Lang::tr{'backup sets'}:
    <table width = '80%' border='0'>
    <tr>
	<th  class = 'boldbase' align = 'center'>$Lang::tr{'name'}</th>
 	<th  class = 'boldbase' align = 'center' colspan = '3'>$Lang::tr{'action'}</th>
    </tr>
END
;

# get list of available sets by globbing directories under $setdir
# External device (usk key) are mounted in $setdir. -R permits finding sets in hierarchy.
my $i = 0;
foreach my $set (`ls -Rt1 $setdir`) {
    chop ($set);	#remove ':' & newline from line
    chop ($set);
    if (-d $set && ($set =~ m!/.+/\d{8}_\d{6}! ) ) { # filter out things not sets !
	if ($i++ % 2) {
	    print "<tr bgcolor = '$Header::table2colour'>";
	} else {
	    print "<tr bgcolor = '$Header::table1colour'>";
	}
	my $settime = read_timefile( "$set/$datefile", "$set/$datafile" );
	my $name = substr ($set,length($setdir)+1);
	print<<EOF
<td>
    $settime
</td>

<td align = 'center'>
<form method = 'post'>
<input type = 'hidden' name = 'ACTION' value ='$Lang::tr{'restore'}' />
<input type = 'image'  name = '$Lang::tr{'restore'}' src = '/images/reload.gif' alt = '$Lang::tr{'restore'}' title = '$Lang::tr{'restore'}' />
<input type = 'hidden' name = 'KEY' value = '$set' />
</form>
</td>

<td align = 'center'>
<a href = '/backup/$name/$datafile'><img src = '/images/floppy.gif' title = '$Lang::tr{'export'}'></a>
</td>

<td align = 'center'>
<form method = 'post'>
<input type = 'hidden' name = 'ACTION' value = '$Lang::tr{'remove'}' />
<input type = 'image'  name = '$Lang::tr{'remove'}' src = '/images/delete.gif' alt = '$Lang::tr{'remove'}' title = '$Lang::tr{'remove'}' border = '0' />
<input type = 'hidden' name = 'KEY' value = '$set' />
</form>
</td>
</tr>
EOF
;
    }
}
print "</table>" . ($i ? "<br>" : "$Lang::tr{'empty'}!<hr /><br>");
print <<EOF
$warnmessage
<form method = 'post'>
	<li>$Lang::tr{'backup configuration'}<br>
	$Lang::tr{'description'}:<input type = 'text' name = 'COMMENT' size='30' />
	<input type = 'submit' name = 'ACTION' value = '$Lang::tr{'create'}' />
</form><p>
<form method = 'post' enctype = 'multipart/form-data'>
	<li>$Lang::tr{'backup import dat file'}:<br>
	<input type = 'file' name = 'FH' size = '20' />
	<input type = 'submit' name = 'ACTION' value = '$Lang::tr{'import'}' />
</form>
</ul>
EOF
;

print "</td><td></td><td valign='top'>";  # Start right part (devices selection)
print $Lang::tr{'backup media info'};

print "<form method = 'post'>";
print "<table width = '100%'><tr><td>";
my $nodev = 1;             # nothing present
foreach my $media (keys %medias) {
    if ( $medias{$media}{'Attached'} eq 'Yes') {	# device is attached to USB bus ?
	$nodev = 0;             # at least one device present
	my $checked = $medias{$media}{'Host'} eq $mounted ? "checked='checked'" : '';
	print "<input type='radio' name = 'SELECT' value = '$medias{$media}{'Host'}' $checked />";
  	print "<b>$medias{$media}{'Product'}</b><br>";
	# list attached partitions to this media
	foreach my $part (sort (keys (%partitions))) {
	    if ($part =~ /$medias{$media}{'Host'}./) {
	        my $checked = $part eq $mounted ? "checked='checked'" : '';
	        print "&nbsp;&nbsp;&nbsp;<input type='radio' name = 'SELECT' value = '$part' $checked />$part ($partitions{$part})<br>";
	    }
	}
    }
}
if ($nodev) {
    print "<br>$Lang::tr{'insert removable device'}";
    print "</td><td>";
    print "<br><input type = 'submit' name = 'ACTION' value = '$Lang::tr{'done'}' />";
} else {
    #Add an entry for the local disk
    my $checked =  $Lang::tr{'local hard disk'} eq $mounted ? "checked='checked'" : '';
    print "<input type = 'radio' name = 'SELECT' value = '$Lang::tr{'local hard disk'}' $checked />";
    print "<b>$Lang::tr{'local hard disk'}</b>";
    print "</td><td>";
    print "<br><input type = 'submit' name = 'ACTION' value = '$Lang::tr{'mount'}' />";
}
print "</tr></table>";
print "</form>";
#
#Backup key
#
print<<EOF
    <hr />
<form method='post'>
    <b>$Lang::tr{'backup key'}</b><br>
    $Lang::tr{'backup key info'}<br>
    <table><tr>
    <td align= 'right'>$Lang::tr{'root user password'}:
    <td align='left'><input type = 'password' name='PASSWORD' />
    <input type = 'submit' name = 'ACTION' value = '$Lang::tr{'backup export key'}' />
    </tr><tr>
    <td align='right'>$Lang::tr{'backup protect key password'}:
    <td align='left'><input type = 'password' name='PASSWORD1' size='10' />
    </tr><tr>
    <td align='right'>$Lang::tr{'again'}
    <td align='left'><input type = 'password' name='PASSWORD2'  size='10'/>
    </tr></table>
</form>

EOF
;
# End of right table
print "</td></tr></table>";

&floppybox();

&Header::closebox();
&Header::closebigbox();
&Header::closepage();

sub floppybox {
    print <<END
<hr />
<form method = 'post'>
<table width='100%'>
<tr>
    <td>
         <b>$Lang::tr{'backup to floppy'}</b>
    </td>
</tr>
<tr>
    <td width='50%'>
	$Lang::tr{'insert floppy'}
    </td>
    <td align='center'> 
	<input type='submit' name='ACTION' value='$Lang::tr{'backup to floppy'}' />
    </td> 
</tr>
</table>
</form>
END
;
    print   "<b>$Lang::tr{'alt information'}</b><pre>" .
    	    `/usr/local/bin/ipfirebackup -savecfg floppy` .
	    '&nbsp;</pre>' if ($settings{'ACTION'} eq $Lang::tr{'backup to floppy'} );
}

# Return device name of what is mounted under 'backup'
sub findmounted() {
    my $mounted = `mount|grep ' /home/httpd/html/backup '`;
    if ($mounted) {				# extract device name
        $mounted =~ m!^/dev/(.*) on!;		# device on mountmoint options
        return $1; 
    } else {					# it's the normal subdir
        return $Lang::tr{'local hard disk'};
    }
}
# read and return a date/time string from a time file
sub read_timefile() {
    my $fname = shift;   # name of file to read from
    my $fname2 = shift;  # if first file doesn't exist, get date of this file

    my $dt;
    if (defined(open(FH, "<$fname"))) {
	$dt = <FH>;
	chomp $dt;
	close(FH);
    } else {
	$dt = &get_fdate($fname2);    # get file date/time
	write_timefile($fname, $dt); # write to expected time file
    }
    return $dt;
}
# write a date/time string to a time file
sub write_timefile() {
    my $fname = shift; # name of file to write to
    my $dt = shift;    # date/time string to write

    if (open(FH, ">$fname")) {
      print FH "$dt\n";
      close(FH);
    }  
}
# move a dat file without time stamp to subdir
sub import_set() {
    my $dt = get_fdate("$setdir/$datafile") . shift;
    &write_timefile("$setdir/$datefile", $dt);

    # create set directory
    my $setname = "$setdir/" . get_ddate("$setdir/$datafile");
    mkdir($setname);

    # move files to the new set directory
    copy_files($setdir, $setname);
    erase_files ($setdir);
}

# get date/time string from file
sub get_fdate() {
    my $fname = shift;
    open(DT, "/bin/date -r $fname|");
    my $dt = <DT>;
    close(DT);
    chomp $dt;
    $dt =~ s/\s+/ /g;  # remove duplicate spaces
    return $dt;
}
# get date/time string from file for use as directory name
sub get_ddate() {
    my $fname = shift;
    open(DT, "/bin/date -r $fname +%Y%m%d_%H%M%S|");
    my $dt = <DT>;
    close(DT);
    chomp $dt;
    return $dt;
}
# copy archive files from source directory to destination directory
sub copy_files() {
    my $src_dir = shift;
    my $dest_dir = shift;
    map (copy ("$src_dir/$_", "$dest_dir/$_"),  ($datafile, $datefile) );
}
# erase set files
sub erase_files() {
    my $src_dir = shift;
    map (unlink ("$src_dir/$_"),  ($datafile, $datefile));
}
# get backup error text
sub get_bk_error() {
    my $exit_code = shift || return '';
    if ($exit_code == 0) {
	return '';
    } elsif ($exit_code == 2) {
	return $Lang::tr{'err bk 2 key'};
    } elsif ($exit_code == 3) {
	return $Lang::tr{'err bk 3 tar'};
    } elsif ($exit_code == 4) {
	return $Lang::tr{'err bk 4 gz'};
    } elsif ($exit_code == 5) {
	return $Lang::tr{'err bk 5 encrypt'};
    } else {
	return $Lang::tr{'err bk 1'};
    }
}
# show any restore errors
sub get_rs_error() {
    
    my $exit_code = shift || return '';
    if ($exit_code == 0) {
	return '';
    } elsif ($exit_code == 6) {
	return $Lang::tr{'err rs 6 decrypt'};
    } elsif ($exit_code == 7) {
	return $Lang::tr{'err rs 7 untartst'};
    } elsif ($exit_code == 8) {
	return $Lang::tr{'err rs 8 untar'};
    } elsif ($exit_code == 9) {
	return $Lang::tr{'missing dat'};
    } else {
	return $Lang::tr{'err rs 1'}."($exit_code)";
    }
}
sub kmgt {
    my ($value,$length,$opt_U) = @_;
    if      ( $value > 10**( $length + 8 ) or $opt_U eq 'T' ) {
	return sprintf( "%d%s", int( ( $value / 1024**4 ) + .5 ), 'T' );
    } elsif ( $value > 10**( $length + 5 ) or $opt_U eq 'G' ) {
	return sprintf( "%d%s", int( ( $value / 1024**3 ) + .5 ), 'G' );
    } elsif ( $value > 10**( $length + 2 ) or $opt_U eq 'M' ) {
	return sprintf( "%d%s", int( ( $value / 1024**2 ) + .5 ), 'M' );
    } elsif ( $value > 10**($length) or $opt_U eq 'K' ) {
	return sprintf( "%d%s", int( ( $value / 1024 ) + .5 ), 'K' );
    } else {
	return $value;
    }
}

1;
