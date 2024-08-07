#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2023  IPFire Team  <info@ipfire.org>                          #
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
my $errormessage = "";

# Hash to store the configured drives.
my %configured_drives;

# SYSFS directory which contains all block device data.
my $sysfs_block_dir = "/sys/class/block";

# Array which contains the valid mount directories.
# Only mounting to subdirectories inside them is allowed.
my @valid_mount_dirs = (
	"/data",
	"/media",
	"/mnt",
);

# Grab all available block devices.
my @devices = &get_block_devices();

# Grab all known UUID's.
my %uuids = &get_uuids();

# Detect device mapper devices.
my %device_mapper = &get_device_mapper();

# Grab members of group devices (RAID, LVM)
my %grouped_devices = &collect_grouped_devices();

# Grab all mountpoints.
my %mountpoints = &get_mountpoints();

# Omit the file system types of the mounted devices.
my %filesystems = &get_mountedfs();

# Gather all used swap devices.
my @swaps = &get_swaps();

# The config file which contains the configured devices.
my $devicefile = "/var/ipfire/extrahd/devices";

#workaround to suppress a warning when a variable is used only once
my @dummy = ( ${Header::colourgreen}, ${Header::colourred} );
undef (@dummy);

&Header::showhttpheaders();

### Values that have to be initialized
$extrahdsettings{'PATH'} = '';
$extrahdsettings{'FS'} = '';
$extrahdsettings{'DEVICE'} = '';
$extrahdsettings{'ACTION'} = '';
$extrahdsettings{'UUID'} = '';

&Header::getcgihash(\%extrahdsettings);

&Header::openpage('ExtraHD', 1, '');
&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
############################################################################################################################

#
## Add a new device.
#
if ($extrahdsettings{'ACTION'} eq $Lang::tr{'add'}) {
	# Check if a mount path has been given.
	if (not $extrahdsettings{'PATH'}) {
		$errormessage = "$Lang::tr{'extrahd no mount point given'}.";
	
	# Check if a valid mount path has been choosen.
	} elsif(not &is_valid_dir("$extrahdsettings{'PATH'}")) {
		$errormessage = "$Lang::tr{'extrahd you cant mount'} $extrahdsettings{'DEVICE'} $Lang::tr{'extrahd to'} $extrahdsettings{'PATH'} $Lang::tr{'extrahd because it is outside the allowed mount path'}.";

	# Check if the given path allready is mounted somewhere.
	} elsif(&is_mounted("$extrahdsettings{'PATH'}")) {
		$errormessage = "$Lang::tr{'extrahd you cant mount'} $extrahdsettings{'DEVICE'} $Lang::tr{'extrahd to'} $extrahdsettings{'PATH'} $Lang::tr{'extrahd because there is already a device mounted'}.";
	}

	# Check against may previously configured drives.
	unless ($errormessage) {
		# Open device file for reading.
		open( FILE, "< $devicefile" ) or die "Unable to read $devicefile";
		my @devices = <FILE>;
		close FILE;

		# Loop through the entries line-by-line.
		foreach my $entry (sort @devices) {
			# Split the line into pieces and assign nice variables.
			my ($uuid, $fs, $path) = split( /\;/, $entry );

			# Remove tailing UUID= from uuid string.
			$uuid =~ s{^UUID=}{};

			# Check if the path is allready used.
			if ( "$extrahdsettings{'PATH'}" eq "$path" ) {
				$errormessage = "$Lang::tr{'extrahd you cant mount'} $extrahdsettings{'DEVICE'} $Lang::tr{'extrahd to'} $extrahdsettings{'PATH'} $Lang::tr{'extrahd because there is already a device mounted'}.";
			}

			# Check if the uuid is allready used.
			if ("$extrahdsettings{'UUID'}" eq "$uuid") {
				$errormessage = "$extrahdsettings{'DEVICE'} is allready mounted.";
			}
		}
	}

	# Go further if there was no error message.
	unless($errormessage) {
		# Re-open the device file for writing.
		open(FILE, ">> $devicefile" ) or die "Unable to write $devicefile";

		# Write the config line.
		print FILE "UUID=$extrahdsettings{'UUID'};$extrahdsettings{'FS'};$extrahdsettings{'PATH'};\n";

		# Close file handle.
		close(FILE);

		# Call helper binary to mount the device.
		&General::system("/usr/local/bin/extrahdctrl", "mount", "$extrahdsettings{'PATH'}");
	}
	
#
# Remove an existing one.
#
} elsif ($extrahdsettings{'ACTION'} eq $Lang::tr{'delete'})  {
	# Call helper binary to unmount the device.
	unless(&General::system("/usr/local/bin/extrahdctrl", "umount", "$extrahdsettings{'PATH'}")) {
		# Open the device file for reading.
		open(FILE, "< $devicefile" ) or die "Unable to read $devicefile";

		# Read the file content into a temporary array.
		my @tmp = <FILE>;

		# Close file handle.
		close(FILE);

		# Re-open device file for writing.
		open(FILE, "> $devicefile" ) or die "Unable to write $devicefile";

		# Loop through the previous read file content.
		foreach my $line (sort @tmp) {
			# Split line content and assign nice variables.
			my ($uuid, $fs, $path) = split( /\;/, $line );

			# Write the line in case it does not contain our element to delete.
			if ($path ne $extrahdsettings{'PATH'}) {
				print FILE "$line";
			}
		}

		# Close file handle.
		close(FILE);
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

&Header::openbox('100%', 'center', $Lang::tr{'extrahd detected drives'});

	# Re-read mountpoints.
	%mountpoints = &get_mountpoints();

	# Read-in the device config file.
	open( FILE, "< $devicefile" ) or die "Unable to read $devicefile";

	# Loop through the file content.
	while (<FILE>) {
		# Cut the line into pieces.
		my ($uuid, $fs, $path) = split( /\;/, $_ );

		# Add the found entry to the hash of configured drives.
		$configured_drives{$uuid} = $path;
	}

	# Close the file handle.
	close(FILE);

	print <<END
		<table border='0' width='100%' cellspacing="0">
END
;
	foreach my $device (sort @devices) {
		# Grab the device details.
		my $vendor = &get_device_vendor($device);
		my $model = &get_device_model($device);
		my $bsize = &get_device_size($device);

		# Convert size into human-readable format.
		my $size = &General::formatBytes($bsize);

		print <<END
			<tr><td colspan="5">&nbsp;</td></tr>
			<tr><td align='left' colspan="2"><b>/dev/$device</b></td>
			<td align='center' colspan="2">$vendor $model</td>

			<td align='center'>$Lang::tr{'size'} $size</td>
			<td>&nbsp;</td></tr>
			<tr><td colspan="5">&nbsp;</td></tr>
END
;

		# Grab the known partitions of the current block device.
		my @partitions = &get_device_partitions($device);

		# Check if the block device has any partitions for display.
		if (@partitions) {
			# Loop through the partitions.
			foreach my $partition (@partitions) {
				# Call function to display the row in the WUI.
				&print_row($partition);
			}
		}

		# Also print rows for devices with an UUID.
		&print_row($device) if($uuids{$device});
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
# Function to print a table row with device data on the WUI.
#
sub print_row ($) {
	my ($partition) = @_;

	my $disabled;

	# Omit the partition size.
	my $bsize = &get_device_size($partition);

	# Convert into human-readable format.
	my $size = &General::formatBytes($bsize);

	# Try to omit the used filesystem.
	my $fs = $filesystems{$partition};

	# Get the mountpoint.
	my $mountpoint = $mountpoints{$partition};

	# Generate partition string.
	my $partition_string = "/dev/$partition";

	# Check if the given partition is managed by device mapper.
	if (exists($device_mapper{$partition})) {
		# Alter the partition string to used one by the device mapper.
		$partition_string = "$device_mapper{$partition}";
	}

	# Check if the device is part of a group.
	my $grouped_device = &is_grouped_member($partition);

	# If no mountpoint could be determined try to grab from
	# configured drives.
	unless($mountpoint) {
		my $uuid = $uuids{$partition};

		# Build uuid string.
		$uuid = "UUID=" . $uuid;

		# Try to obtain a possible moutpoint from configured drives.
		$mountpoint = $configured_drives{$uuid} if ($configured_drives{$uuid});
	}

	# Check if the mountpoint is used as root or boot device.
	if ($mountpoint eq "/" or $mountpoint =~ "^/boot") {
		$disabled = "disabled";

	# Check if it is mounted.
	} elsif(&is_mounted($mountpoint)) {
		$disabled = "disabled";

	# Check if the device is used as swap.
	} elsif (&is_swap($partition)) {
		$disabled = "disabled";
		$mountpoint = "swap";
		$fs = "swap";

	# Check if the device is part of a group.
	} elsif ($grouped_device) {
		$disabled = "disabled";
		$mountpoint = "/dev/$grouped_device";
		$mountpoint = $device_mapper{$grouped_device} if (exists($device_mapper{$grouped_device}));
	}

	print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

	# Only display UUID details if an UUID could be obtained.
	if ( $uuids{$partition} ) {
		print "<tr><td align='left' colspan=5><strong>UUID=$uuids{$partition}</strong></td></tr>\n";
	}

	print <<END

	<tr>
	<td align="list">$partition_string</td>
		<td align="center">$Lang::tr{'size'} $size</td>
		<td align="center">$fs</td>
		<td align="center"><input type='text' name='PATH' value='$mountpoint' $disabled></td>
		<td align="center">
			<input type='hidden' name='DEVICE' value='$partition_string' />
			<input type='hidden' name='UUID' value='$uuids{$partition}' />
END
;
		# Check if the mountpoint refers to a known configured drive.
		if(&is_configured($mountpoint)) {
			print "<input type='hidden' name='ACTION' value='$Lang::tr{'delete'}'>\n";
			print "<input type='hidden' name='PATH' value='$mountpoint'>\n";

			# Check if the device is mounted properly.
			if(&is_mounted($mountpoint)) {
				print "<img src='/images/updbooster/updxl-led-green.gif' alt='$Lang::tr{'extrahd mounted'}' title='$Lang::tr{'extrahd mounted'}'>&nbsp;\n";
			} else {
				print "<img src='/images/updbooster/updxl-led-red.gif' alt='$Lang::tr{'extrahd not mounted'}' title='$Lang::tr{'extrahd not mounted'}'>&nbsp;\n";
			}

				print "<input type='image' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' src='/images/delete.gif'>\n";
		} else {
			unless($disabled) {
				print "<input type='hidden' name='ACTION' value='$Lang::tr{'add'}'>\n";
				print "<input type='hidden' name='FS' value='auto'>\n";
				print "<img src='/images/updbooster/updxl-led-gray.gif' alt='$Lang::tr{'extrahd not configured'}' title='$Lang::tr{'extrahd not configured'}'>&nbsp;\n";
				print "<input type='image' alt='$Lang::tr{'add'}' title='$Lang::tr{'add'}' src='/images/add.gif'>\n";
			}
		}

	print <<END
	</form></td></tr>
END
;
}

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
## Function which tries to detect if a block device is a device mapper device and returns the alias a
## a hash. Example: "dm-0" -> "/dev/mapper/GROUP-DEVICE"
#
sub get_device_mapper () {
	my %mapper_devices = ();

	# Loop through all known block devices.
	foreach my $block_device (@devices) {
		# Generate  device directory.
		my $device_dir = "$sysfs_block_dir/$block_device";

		# Skip the device if it is not managed by device mapper
		# In this case the "bd" is not present.
		next unless (-e "$device_dir/dm");

		# Grab the group and volume name.
		open(NAME, "$device_dir/dm/name") if (-e "$device_dir/dm/name");
		my $name = <NAME>;
		close(NAME);

		# Skip device if no name could be determined.
		next unless($name);

		# Remove any newlines from the name string.
		chomp($name);

		# Generate path to the dev node in devfs.
		my $dev_path = "/dev/mapper/$name";

		# Store the device and the omited mapper name in the hash.
		$mapper_devices{$block_device} = $dev_path;
	}

	# Return the hash of omited device mapper devices.
	return %mapper_devices;
}

#
## Function which will collect grouped devices and their members as array in a hash and returns them.
## For example: "sda1" -> "dm-0" in case /dev/sda1 is assigned to a device mapper group.
#
sub collect_grouped_devices () {
	my %grouped_devices = ();

	# Loop through the array of known block devices.
	foreach my $device (@devices) {
		# Generate device directory.
		my $device_dir = "$sysfs_block_dir/$device";

		# Skip device if it has no members.
		# In this case the "slaves" directory does not exist.
		next unless (-e "$device_dir/slaves");

		# Tempoarary array to store the members of a group.
		my @members = ();

		# Grab all members.
		opendir(MEMBERS, "$device_dir/slaves");
		while(readdir(MEMBERS)) {
			next if($_ eq ".");
			next if($_ eq "..");

			# Add the found member to the array of members.
			push(@members, $_);
		}

		closedir(MEMBERS);

		# Skip the device if no members could be grabbed.
		next unless (@members);

		# Add the array of found members as value to the hash of grouped devices.
		$grouped_devices{$device} = [ @members ];
	}

	# Return the hash of found grouped devices and their members.
	return %grouped_devices;
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

	# Do not allow "/mnt" or "/media" as mount points.
	return if($mpoint eq "/mnt");
	return if($mpoint eq "/media");

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

#
## Returns "True" if a drive is a configured one.
#
sub is_configured ($) {
	my ($path) = @_;

	# Loop through the hash of configured drives.
	foreach my $uuid (keys %configured_drives) {
	       return 1 if($configured_drives{$uuid} eq "$path");
	}
}

#
## Retruns the device name of the grouped device,if a given device is a group member.
#
sub is_grouped_member ($) {
	my ($device) = @_;

	# Loop through the hash of found grouped devices.
	foreach my $grouped_device(keys %grouped_devices) {
		# The found members are stored as arrays.
		my @members = @{ $grouped_devices{$grouped_device} };

		# Loop through array of members and check if the given
		# device is part of it.
		foreach my $member (@members) {
			return $grouped_device if ($member eq $device);
		}
	}
}
