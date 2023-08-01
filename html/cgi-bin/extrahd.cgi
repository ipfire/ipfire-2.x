#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2011  IPFire Team  <info@ipfire.org>                          #
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

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %extrahdsettings = ();
my $message = "";
my $errormessage = "";
my $size = "";
my $ok = "true";
my @tmp = ();
my @tmpline = ();
my $tmpentry = "";
my @devices = ();
my @deviceline = ();
my $deviceentry = "";
my @scans = ();
my @scanline = ();
my $scanentry = "";
my @partitions = ();
my @partitionline = ();
my $partitionentry = "";
my $devicefile = "/var/ipfire/extrahd/devices";
my $scanfile = "/var/ipfire/extrahd/scan";
my $partitionsfile = "/var/ipfire/extrahd/partitions";

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::colourgreen}, ${Header::colourred} );
undef (@dummy);

&General::system("/usr/local/bin/extrahdctrl", "scanhd", "ide");
&General::system("/usr/local/bin/extrahdctrl", "scanhd", "partitions");

&Header::showhttpheaders();

### Values that have to be initialized
$extrahdsettings{'PATH'} = '';
$extrahdsettings{'FS'} = '';
$extrahdsettings{'DEVICE'} = '';
$extrahdsettings{'ACTION'} = '';
$extrahdsettings{'UUID'} = '';

&General::readhash("${General::swroot}/extrahd/settings", \%extrahdsettings);
&Header::getcgihash(\%extrahdsettings);

&Header::openpage('ExtraHD', 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
############################################################################################################################

if ($extrahdsettings{'ACTION'} eq $Lang::tr{'add'})
{
	open( FILE, "< $devicefile" ) or die "Unable to read $devicefile";
	@devices = <FILE>;
	close FILE;
	foreach $deviceentry (sort @devices)
	{
		@deviceline = split( /\;/, $deviceentry );
		if ( "$extrahdsettings{'PATH'}" eq "$deviceline[2]" ) {
			$ok = "false";
			$errormessage = "$Lang::tr{'extrahd you cant mount'} $extrahdsettings{'DEVICE'} $Lang::tr{'extrahd to'} $extrahdsettings{'PATH'}$Lang::tr{'extrahd because there is already a device mounted'}.";
		}
		if ( "$extrahdsettings{'PATH'}" eq "/" ) {
			$ok = "false";
			$errormessage = "$Lang::tr{'extrahd you cant mount'} $extrahdsettings{'DEVICE'} $Lang::tr{'extrahd to root'}.";
		}
	}

	if ( "$ok" eq "true" ) {
		open(FILE, ">> $devicefile" ) or die "Unable to write $devicefile";
		print FILE <<END
UUID=$extrahdsettings{'UUID'};$extrahdsettings{'FS'};$extrahdsettings{'PATH'};
END
;
	&General::system("/usr/local/bin/extrahdctrl", "mount", "$extrahdsettings{'PATH'}");
	}
}
elsif ($extrahdsettings{'ACTION'} eq $Lang::tr{'delete'})
{
	if ( ! &General::system("/usr/local/bin/extrahdctrl", "umount", "$extrahdsettings{'PATH'}")) {
		open( FILE, "< $devicefile" ) or die "Unable to read $devicefile";
		@tmp = <FILE>;
		close FILE;
		open( FILE, "> $devicefile" ) or die "Unable to write $devicefile";
		foreach $deviceentry (sort @tmp)
		{
			@tmpline = split( /\;/, $deviceentry );
			if ( $tmpline[2] ne $extrahdsettings{'PATH'} )
			{
				print FILE $deviceentry;
			}
		}
		close FILE;
	} else {
		$errormessage = "$Lang::tr{'extrahd cant umount'} $extrahdsettings{'PATH'}$Lang::tr{'extrahd maybe the device is in use'}?";
	}
}

if ($errormessage) {
        &Header::openbox('100%', 'left', $Lang::tr{'error messages'});
        print "<class name='base'>$errormessage\n";
        print "&nbsp;</class>\n";
        &Header::closebox();
}

############################################################################################################################
############################################################################################################################

	open( FILE, "< $devicefile" ) or die "Unable to read $devicefile";
	@devices = <FILE>;
	close FILE;
	print <<END
		<table border='0' width='600' cellspacing="0">
END
;
	foreach $deviceentry (sort @devices)
	{
		@deviceline = split( /\;/, $deviceentry );
		my $color="$Header::colourred";

		# Use safe system_output to get mountpoint details.
		my @mountpoint = &General::system_output("/bin/mountpoint", "$deviceline[2]");

		if ( ! grep(/not/, @mountpoint)) {
			$color=$Header::colourgreen;
		}
		print <<END
			<tr><td colspan="4">&nbsp;</td></tr>
			<tr><td align='left'><font color=$color><b>$deviceline[0]</b></font></td>
				<td align='left'>$deviceline[1]</td>
				<td align='left'>$deviceline[2]</td>
				<td align='center'>
					<form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='hidden' name='DEVICE' value='$deviceline[0]' />
						<input type='hidden' name='FS' value='$deviceline[1]' />
						<input type='hidden' name='PATH' value='$deviceline[2]' />
						<input type='hidden' name='ACTION' value='$Lang::tr{'delete'}' />
						<input type='image' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' src='/images/delete.gif' />
					</form></td></tr>
END
;
	}
	print <<END
		</table>
END
;
&Header::openbox('100%', 'center', $Lang::tr{'extrahd detected drives'});
	print <<END
		<table border='0' width='600' cellspacing="0">
END
;
	open( FILE, "< $scanfile" ) or die "Unable to read $scanfile";
	@scans = <FILE>;
	close FILE;
	open( FILE, "< $partitionsfile" ) or die "Unable to read $partitionsfile";
	@partitions = <FILE>;
	close FILE;
	foreach $scanentry (sort @scans)
	{
		@scanline = split( /\;/, $scanentry );
		# remove wrong entries like usb controller name
		if ($scanline[1] ne "\n")
		{
			print <<END
				<tr><td colspan="5">&nbsp;</td></tr>
				<tr><td align='left' colspan="2"><b>/dev/$scanline[0]</b></td>
				<td align='center' colspan="2">$scanline[1]</td>
END
;

		}
		foreach $partitionentry (sort @partitions)
		{
			@partitionline = split( /\;/, $partitionentry );
			if ( "$partitionline[0]" eq "$scanline[0]" ) {
				$size = int($partitionline[1] / 1024);
				print <<END
				<td align='center'>$Lang::tr{'size'} $size MB</td>
				<td>&nbsp;</td></tr>
				<tr><td colspan="5">&nbsp;</td></tr>
END
;
			}
		}

		foreach $partitionentry (sort @partitions)
		{
			@partitionline = split( /\;/, $partitionentry );
			if (( "$partitionline[0]" =~ /^$scanline[0]/ ) && !( "$partitionline[2]" eq "" )) {
				$size = int($partitionline[1] / 1024);
				print <<END
				<form method='post' action='$ENV{'SCRIPT_NAME'}'>
				<tr><td align="left" colspan=5><strong>UUID=$partitionline[2]</strong></td></tr>
				<tr>
				<td align="list">/dev/$partitionline[0]</td>
				<td align="center">$Lang::tr{'size'} $size MB</td>
				<td align="center"><select name="FS">
										<option value="auto">auto</option>
										<option value="ext3">ext3</option>
										<option value="ext4">ext4</option>
										<option value="reiserfs">reiserfs</option>
										<option value="vfat">fat</option>
										<option value="ntfs-3g">ntfs (experimental)</option>
									   </select></td>
				<td align="center"><input type='text' name='PATH' value=/mnt/harddisk /></td>
				<td align="center">
					<input type='hidden' name='DEVICE' value='$partitionline[0]' />
					<input type='hidden' name='UUID' value='$partitionline[2]' />
					<input type='hidden' name='ACTION' value='$Lang::tr{'add'}' />
					<input type='image' alt='$Lang::tr{'add'}' title='$Lang::tr{'add'}' src='/images/add.gif' />
				</form></td></tr>
END
;

END
;
			}
		}
	}

	print <<END
	<tr><td align="center" colspan="5">&nbsp;</td></tr>
	<tr><td align="center" colspan="5">&nbsp;</td></tr>
	<tr><td align="center" colspan="5">$Lang::tr{'extrahd install or load driver'}</td></tr>
	</table>
END
;
&Header::closebox();

&Header::closebigbox();
&Header::closepage();

#
## Function which return an array with all available block devices.
#
sub get_block_devices () {
	my @devices;

	# Open directory from kernel sysfs.
	opendir(DEVICES, "/sys/block");

	# Loop through the directory.
	while(readdir(DEVICES)) {
		# Skip . and ..
		next if($_ =~ /^\.$/);
		next if($_ =~ /^\..$/);

		# Skip any loopback and ram devices.
		next if($_ =~ "^loop");
		next if($_ =~ "^ram");

		# Add the device to the array of found devices.
		push(@devices, $_);
	}

	# Close directory handle.
	closedir(DEVICES);

	# Return the devices array.
	return @devices;
}

#
## Function which return all partitions of a given block device.
#
sub get_device_partitions ($) {
	my ($device) = @_;

	# Array to store the known partitions for the given
	# device.
	my @partitions;

	# Assign device directory.
	my $device_dir = "$sysfs_block_dir/$device";

	# Abort and return nothing if the device dir does not exist.
	return unless(-d "$device_dir");

	opendir(DEVICE, "$sysfs_block_dir/$device");
	while(readdir(DEVICE)) {
		next unless($_ =~ "^$device");

		push(@partitions, $_);
	}

	closedir(DEVICE);

	@partitions = sort(@partitions);

	return @partitions;
}

#
## Returns the vendor of a given block device.
#
sub get_device_vendor ($) {
	my ($device) = @_;

	# Assign device directory.
	my $device_dir = "$sysfs_block_dir/$device";

	# Abort and return nothing if the device dir does not exist
	# or no vendor file exists.
	return unless(-d "$device_dir");
	return unless(-f "$device_dir/device/vendor");

	# Open and read-in the device vendor.
	open(VENDOR, "$device_dir/device/vendor");
	my $vendor = <VENDOR>;
	close(VENDOR);

	# Abort and return nothing if no vendor could be read.
	return unless($vendor);

	# Remove any newlines from the vendor string.
	chomp($vendor);

	# Return the omited vendor.
	return $vendor;
}

#
## Returns the model name (string) of a given block device.
#
sub get_device_model ($) {
	my ($device) = @_;

	# Assign device directory.
	my $device_dir = "$sysfs_block_dir/$device";

	# Abort and return nothing if the device dir does not exist
	# or no model file exists.
	return unless(-d "$device_dir");
	return unless(-f "$device_dir/device/model");

	# Open and read-in the device model.
	open(MODEL, "$device_dir/device/model");
	my $model = <MODEL>;
	close(MODEL);

	# Abort and return nothing if no model could be read.
	return unless($model);

	# Remove any newlines from the model string.
	chomp($model);

	# Return the model string.
	return $model;
}

#
## Returns the size of a given device in bytes.
#
sub get_device_size ($) {
	my ($device) = @_;

	# Assign device directory.
	my $device_dir = "$sysfs_block_dir/$device";

	# Abort and return nothing if the device dir does not exist
	# or no size file exists.
	return unless(-d "$device_dir");
	return unless(-f "$device_dir/size");

	# Open and read-in the device size.
	open(SIZE, "$device_dir/size");
	my $size = <SIZE>;
	close(SIZE);

	# Abort and return nothing if the size could not be read.
	return unless($size);

	# Remove any newlines for the size string.
	chomp($size);

	# The omited size only contains the amount of blocks from the
	# given device. To convert this into bytes we have to multiply this
	# value with 512 bytes for each block. This is a static value used by
	# the linux kernel.
	$size = $size * 512;

	# Return the size in bytes.
	return $size;
}

#
## Function which returns all currently mounted devices as a hash.
## example: "sda1" -> "/boot"
#
sub get_mountpoints () {
	my %mounts;

	# Open and read-in the current mounts from the
	# kernel file system.
	open(MOUNT, "/proc/mounts");

	# Loop through the known mounts.
	while(<MOUNT>) {
		# Skip mounts which does not belong to a device.
		next unless ($_ =~ "^/dev");

		# Cut the line into pieces and assign nice variables.
		my ($dev, $mpoint, $fs, $options, $a, $b) = split(/ /, $_);

		# Split the device name.
		my @tmp = split("/", $dev);

		# Assign the plain device name to a new variable.
		# It is the last element of the array.
		my $device = $tmp[-1];

		# Add the mountpoint to the hash of mountpoints.
		$mounts{"$device"} = $mpoint;
	}

	# Close file handle.
	close(MOUNT);

	# Return the hash of known mountpoints.
	return %mounts;
}

sub get_swaps () {
	my @swaps;

	# Open and read the swaps file.
	open(SWAP, "/proc/swaps");

	# Loop though the file content.
	while(<SWAP>) {
		# Skip lines which does not belong to a device.
		next unless ($_ =~ "^/dev");

		# Split the line and assign nice variables.
		my ($dev, $type, $size, $used, $prio) = split(/ /, $_);

		# Cut the device line into pieces.
		my @tmp = split("/", $dev);

		my $device = @tmp[-1];

		# Add the found swap to the array of swaps.
		push(@swaps, $device);
	}

	# Close file handle.
	close(SWAP);

	# Sort the array.
	@swaps = sort(@swaps);

	# Return the array.
	return @swaps;
}

#
## Function with returns the mounted devices and the used filesystems as a hash.
## Example: "sda1" -> "ext4"
#
sub get_mountedfs () {
	my %mountedfs;

	# Open and read the current mounts from the kernel
	# file system.
	open(MOUNT, "/proc/mounts");

	# Loop through the known mounts.
	while(<MOUNT>) {
		# Skip mounts which does not belong to a device.
		next unless ($_ =~ "^/dev");

		# Split line and assign nice variables.
		my ($dev, $mpoint, $fs, $options, $a, $b) = split(/ /, $_);

		# Cut the device line into pieces.
		my @tmp = split("/", $dev);

		# Assign the plain device name to a variable
		# It is the last element of the temporary array.
		my $device = $tmp[-1];

		# Convert the filesystem into lower case format.
		$fs = lc($fs);

		# Add the mounted file system.
		$mountedfs{$device} = $fs;
	}

	# Close file handle.
	close(MOUNT);

	# Return the hash with the mounted filesystems.
	return %mountedfs;
}

#
## Function which returns all known UUID's as a hash.
## Example: "sda1" -> "1234-5678-abcd"
#
sub get_uuids () {
	my %uuids;

	# Directory where the uuid mappings can be found.
	my $uuid_dir = "/dev/disk/by-uuid";

	# Open uuid directory and read-in the current known uuids.
	opendir(UUIDS, "$uuid_dir");

	# Loop through the uuids.
	foreach my $uuid (readdir(UUIDS)) {
		# Skip . and ..
		next if($uuid eq "." or $uuid eq "..");

		# Skip everything which is not a symbolic link.
		next unless(-l "$uuid_dir/$uuid");

		# Resolve the target of the symbolic link.
		my $target = readlink("$uuid_dir/$uuid");

		# Split the link target into pieces.
		my @tmp = split("/", $target);

		# Assign the last element of the array to the dev variable.
		my $dev = "$tmp[-1]";

		# Add the device and uuid to the hash of uuids.
		$uuids{$dev} = $uuid;
	}

	# Close directory handle.
	closedir(UUIDS);

	# Return the hash of uuids.
	return %uuids;
}

#
## Returns the device name of a given uuid.
#
sub device_by_uuid ($) {
	my ($uuid) = @_;

	# Reverse the main uuids hash.
	my %uuids = reverse %uuids;

	# Lookup and return the device name.
	return $uuids{$uuid};
}

#
## Returns "True" in case a given path is a known mountpoint.
#
sub is_mounted ($) {
	my ($mpoint) = @_;

	my %mountpoints = reverse %mountpoints;

	# Return "True" if the requested mountpoint is known and
	# therefore mounted.
	return 1 if($mountpoints{$mpoint});
}

#
## Returns "True" if a given mountpoint is a subdirectory of one
## of the directories specified by the valid_mount_dirs array abouve.
#
sub is_valid_dir ($) {
	my ($mpoint) = @_;

	# Split the given mountpoint into pieces and store them
	# in a temporay array.
	my @tmp = split("/", $mpoint);

	# Exit and return nothing if the temporary array is empty.
	return unless(@tmp);

	# Build the root path based on the given mount point.
	my $root_path = "/" . @tmp[1];

	# Check if the root path is valid.
	return 1 if(grep /$root_path/, @valid_mount_dirs);
}

#
# Returns "True" if a device is used as swap.
#
sub is_swap ($) {
	my ($device) = @_;

	return 1 if(grep /$device/, @swaps);
}
