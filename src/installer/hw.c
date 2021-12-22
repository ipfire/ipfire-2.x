/*#############################################################################
#                                                                             #
# IPFire - An Open Source Firewall Distribution                               #
# Copyright (C) 2014 IPFire development team                                  #
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
#############################################################################*/

#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <assert.h>
#include <blkid/blkid.h>
#include <errno.h>
#include <fcntl.h>
#include <libudev.h>
#include <linux/loop.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/swap.h>
#include <sys/sysinfo.h>
#include <sys/utsname.h>
#include <unistd.h>

#include <linux/fs.h>

#include <libsmooth.h>

#include "hw.h"

static int system_chroot(const char* output, const char* path, const char* cmd) {
	char chroot_cmd[STRING_SIZE];

	snprintf(chroot_cmd, sizeof(chroot_cmd), "/usr/sbin/chroot %s %s", path, cmd);

	return mysystem(output, chroot_cmd);
}

struct hw* hw_init() {
	struct hw* hw = calloc(1, sizeof(*hw));
	assert(hw);

	// Initialize libudev
	hw->udev = udev_new();
	if (!hw->udev) {
		fprintf(stderr, "Could not create udev instance\n");
		exit(1);
	}

	// What architecture are we running on?
	struct utsname uname_data;
	int ret = uname(&uname_data);
	if (ret == 0)
		snprintf(hw->arch, sizeof(hw->arch), "%s", uname_data.machine);

	// Should we install in EFI mode?
	if ((strcmp(hw->arch, "x86_64") == 0) || (strcmp(hw->arch, "aarch64") == 0))
		hw->efi = 1;

	return hw;
}

void hw_free(struct hw* hw) {
	if (hw->udev)
		udev_unref(hw->udev);

	free(hw);
}

static int strstartswith(const char* a, const char* b) {
	return (strncmp(a, b, strlen(b)) == 0);
}

static char loop_device[STRING_SIZE];

static int setup_loop_device(const char* source, const char* device) {
	int file_fd = open(source, O_RDWR);
	if (file_fd < 0)
		goto ERROR;

	int device_fd = -1;
	if ((device_fd = open(device, O_RDWR)) < 0)
		goto ERROR;

	if (ioctl(device_fd, LOOP_SET_FD, file_fd) < 0)
		goto ERROR;

	close(file_fd);
	close(device_fd);

	return 0;

ERROR:
	if (file_fd >= 0)
		close(file_fd);

	if (device_fd >= 0) {
		ioctl(device_fd, LOOP_CLR_FD, 0);
		close(device_fd);
	}

	return -1;
}

int hw_mount(const char* source, const char* target, const char* fs, int flags) {
	const char* loop_device = "/dev/loop0";

	// Create target if it does not exist
	if (access(target, X_OK) != 0)
		mkdir(target, S_IRWXU|S_IRWXG|S_IRWXO);

	struct stat st;
	stat(source, &st);

	if (S_ISREG(st.st_mode)) {
		int r = setup_loop_device(source, loop_device);
		if (r == 0) {
			source = loop_device;
		} else {
			return -1;
		}
	}

	return mount(source, target, fs, flags, NULL);
}

static int hw_bind_mount(const char* source, const char* prefix) {
	if (!source || !prefix) {
		errno = EINVAL;
		return 1;
	}

	char target[PATH_MAX];
	int r;

	// Format target
	r = snprintf(target, sizeof(target) - 1, "%s/%s", prefix, source);
	if (r < 0)
		return 1;

	// Ensure target exists
	mkdir(target, S_IRWXU|S_IRWXG|S_IRWXO);

	return hw_mount(source, target, NULL, MS_BIND);
}

int hw_umount(const char* source, const char* prefix) {
	char target[PATH_MAX];
	int r;

	if (prefix)
		r = snprintf(target, sizeof(target) - 1, "%s/%s", prefix, source);
	else
		r = snprintf(target, sizeof(target) - 1, "%s", source);
	if (r < 0)
		return r;

	// Perform umount
	r = umount2(target, 0);
	if (r) {
		switch (errno) {
			// Try again with force if umount wasn't successful
			case EBUSY:
				sleep(1);

				r = umount2(target, MNT_FORCE);
				break;

			// target wasn't a mountpoint. Ignore.
			case EINVAL:
				r = 0;
				break;

			// target doesn't exist
			case ENOENT:
				r = 0;
				break;
		}
	}

	return r;
}

static int hw_test_source_medium(const char* path) {
	int ret = hw_mount(path, SOURCE_MOUNT_PATH, "iso9660", MS_RDONLY);

	// If the source could not be mounted we
	// cannot proceed.
	if (ret != 0)
		return ret;

	// Check if the test file exists.
	ret = access(SOURCE_TEST_FILE, R_OK);

	// Umount the test device.
	hw_umount(SOURCE_MOUNT_PATH, NULL);

	return ret;
}

char* hw_find_source_medium(struct hw* hw) {
	char* ret = NULL;

	struct udev_enumerate* enumerate = udev_enumerate_new(hw->udev);

	udev_enumerate_add_match_subsystem(enumerate, "block");
	udev_enumerate_scan_devices(enumerate);

	struct udev_list_entry* devices = udev_enumerate_get_list_entry(enumerate);

	struct udev_list_entry* dev_list_entry;
	udev_list_entry_foreach(dev_list_entry, devices) {
		const char* path = udev_list_entry_get_name(dev_list_entry);
		struct udev_device* dev = udev_device_new_from_syspath(hw->udev, path);

		const char* dev_path = udev_device_get_devnode(dev);

		// Skip everything what we cannot work with
		if (strstartswith(dev_path, "/dev/loop") || strstartswith(dev_path, "/dev/fd") ||
				strstartswith(dev_path, "/dev/ram") || strstartswith(dev_path, "/dev/md"))
			continue;

		if (hw_test_source_medium(dev_path) == 0) {
			ret = strdup(dev_path);
		}

		udev_device_unref(dev);

		// If a suitable device was found the search will end.
		if (ret)
			break;
	}

	udev_enumerate_unref(enumerate);

	return ret;
}

static struct hw_disk** hw_create_disks() {
	struct hw_disk** ret = malloc(sizeof(*ret) * (HW_MAX_DISKS + 1));

	return ret;
}

static unsigned long long hw_block_device_get_size(const char* dev) {
	int fd = open(dev, O_RDONLY);
	if (fd < 0)
		return 0;

	unsigned long long size = blkid_get_dev_size(fd);
	close(fd);

	return size;
}

struct hw_disk** hw_find_disks(struct hw* hw, const char* sourcedrive) {
	struct hw_disk** ret = hw_create_disks();
	struct hw_disk** disks = ret;

	struct udev_enumerate* enumerate = udev_enumerate_new(hw->udev);

	udev_enumerate_add_match_subsystem(enumerate, "block");
	udev_enumerate_scan_devices(enumerate);

	struct udev_list_entry* devices = udev_enumerate_get_list_entry(enumerate);

	struct udev_list_entry* dev_list_entry;
	unsigned int i = HW_MAX_DISKS;
	udev_list_entry_foreach(dev_list_entry, devices) {
		const char* path = udev_list_entry_get_name(dev_list_entry);
		struct udev_device* dev = udev_device_new_from_syspath(hw->udev, path);

		const char* dev_path = udev_device_get_devnode(dev);

		// Skip everything what we cannot work with
		if (strstartswith(dev_path, "/dev/loop") || strstartswith(dev_path, "/dev/fd") ||
				strstartswith(dev_path, "/dev/ram") || strstartswith(dev_path, "/dev/sr") ||
				strstartswith(dev_path, "/dev/md")) {
			udev_device_unref(dev);
			continue;
		}

		// Skip sourcedrive if we need to
		if (sourcedrive && (strcmp(dev_path, sourcedrive) == 0)) {
			udev_device_unref(dev);
			continue;
		}

		// DEVTYPE must be disk (otherwise we will see all sorts of partitions here)
		const char* devtype = udev_device_get_property_value(dev, "DEVTYPE");
		if (devtype && (strcmp(devtype, "disk") != 0)) {
			udev_device_unref(dev);
			continue;
		}

		// Skip devices with a size of zero
		unsigned long long size = hw_block_device_get_size(dev_path);
		if (size == 0) {
			udev_device_unref(dev);
			continue;
		}

		struct hw_disk* disk = malloc(sizeof(*disk));
		if (disk == NULL)
			return NULL;

		disk->ref = 1;

		strncpy(disk->path, dev_path, sizeof(disk->path));
		const char* p = disk->path + 5;

		disk->size = size;

		// Vendor
		const char* vendor = udev_device_get_property_value(dev, "ID_VENDOR");
		if (!vendor)
			vendor = udev_device_get_sysattr_value(dev, "vendor");
		if (!vendor)
			vendor = udev_device_get_sysattr_value(dev, "manufacturer");

		if (vendor)
			strncpy(disk->vendor, vendor, sizeof(disk->vendor));
		else
			*disk->vendor = '\0';

		// Model
		const char* model = udev_device_get_property_value(dev, "ID_MODEL");
		if (!model)
			model = udev_device_get_sysattr_value(dev, "model");
		if (!model)
			model = udev_device_get_sysattr_value(dev, "product");

		if (model)
			strncpy(disk->model, model, sizeof(disk->model));
		else
			*disk->model = '\0';

		// Format description
		char size_str[STRING_SIZE];
		snprintf(size_str, sizeof(size_str), "%4.1fGB", (double)disk->size / pow(1024, 3));

		if (*disk->vendor && *disk->model) {
			snprintf(disk->description, sizeof(disk->description),
				"%s - %s - %s - %s", size_str, p, disk->vendor, disk->model);

		} else if (*disk->vendor || *disk->model) {
			snprintf(disk->description, sizeof(disk->description),
				"%s - %s - %s", size_str, p, (*disk->vendor) ? disk->vendor : disk->model);

		} else {
			snprintf(disk->description, sizeof(disk->description),
				"%s - %s", size_str, p);
		}

		// Cut off the description string after 40 characters
		disk->description[41] = '\0';

		*disks++ = disk;

		if (--i == 0)
			break;

		udev_device_unref(dev);
	}

	udev_enumerate_unref(enumerate);

	*disks = NULL;

	return ret;
}

void hw_free_disks(struct hw_disk** disks) {
	struct hw_disk** disk = disks;

	while (*disk != NULL) {
		if (--(*disk)->ref == 0)
			free(*disk);

		disk++;
	}

	free(disks);
}

unsigned int hw_count_disks(const struct hw_disk** disks) {
	unsigned int ret = 0;

	while (*disks++)
		ret++;

	return ret;
}

struct hw_disk** hw_select_disks(struct hw_disk** disks, int* selection) {
	struct hw_disk** ret = hw_create_disks();
	struct hw_disk** selected_disks = ret;

	unsigned int num_disks = hw_count_disks((const struct hw_disk**)disks);

	for (unsigned int i = 0; i < num_disks; i++) {
		if (!selection || selection[i]) {
			struct hw_disk *selected_disk = disks[i];
			selected_disk->ref++;

			*selected_disks++ = selected_disk;
		}
	}

	// Set sentinel
	*selected_disks = NULL;

	return ret;
}

struct hw_disk** hw_select_first_disk(const struct hw_disk** disks) {
	struct hw_disk** ret = hw_create_disks();
	struct hw_disk** selected_disks = ret;

	unsigned int num_disks = hw_count_disks(disks);
	assert(num_disks > 0);

	for (unsigned int i = 0; i < num_disks; i++) {
		struct hw_disk *disk = disks[i];
		disk->ref++;

		*selected_disks++ = disk;
		break;
	}

	// Set sentinel
	*selected_disks = NULL;

	return ret;
}

static unsigned long long hw_swap_size(struct hw_destination* dest) {
	unsigned long long memory = hw_memory();

	unsigned long long swap_size = memory / 4;

	// Min. swap size is 128MB
	if (swap_size < MB2BYTES(128))
		swap_size = MB2BYTES(128);

	// Cap swap size to 1GB
	else if (swap_size > MB2BYTES(1024))
		swap_size = MB2BYTES(1024);

	return swap_size;
}

static unsigned long long hw_boot_size(struct hw_destination* dest) {
	return MB2BYTES(128);
}

static int hw_device_has_p_suffix(const struct hw_destination* dest) {
	// All RAID devices have the p suffix.
	if (dest->is_raid)
		return 1;

	// Devices with a number at the end have the p suffix, too.
	// e.g. mmcblk0, cciss0
	unsigned int last_char = strlen(dest->path) - 1;
	if ((dest->path[last_char] >= '0') && (dest->path[last_char] <= '9'))
		return 1;

	return 0;
}

static int hw_calculate_partition_table(struct hw* hw, struct hw_destination* dest, int disable_swap) {
	char path[DEV_SIZE];
	int part_idx = 1;

	snprintf(path, sizeof(path), "%s%s", dest->path,
		hw_device_has_p_suffix(dest) ? "p" : "");
	dest->part_boot_idx = 0;

	// Determine the size of the target block device
	if (dest->is_raid) {
		dest->size = (dest->disk1->size >= dest->disk2->size) ?
			dest->disk2->size : dest->disk1->size;

		// The RAID will install some metadata at the end of the disk
		// and we will save up some space for that.
		dest->size -= MB2BYTES(2);
	} else {
		dest->size = dest->disk1->size;
	}

	// As we add some extra space before the beginning of the first
	// partition, we need to substract that here.
	dest->size -= MB2BYTES(1);

	// Add some more space for partition tables, etc.
	dest->size -= MB2BYTES(1);

	// The disk has to have at least 2GB
	if (dest->size <= MB2BYTES(2048))
		return -1;

	// Determine partition table
	dest->part_table = HW_PART_TABLE_MSDOS;

	// Disks over 2TB need to use GPT
	if (dest->size >= MB2BYTES(2047 * 1024))
		dest->part_table = HW_PART_TABLE_GPT;

	// We also use GPT on raid disks by default
	else if (dest->is_raid)
		dest->part_table = HW_PART_TABLE_GPT;

	// When using GPT, GRUB2 needs a little bit of space to put
	// itself in.
	if (dest->part_table == HW_PART_TABLE_GPT) {
		snprintf(dest->part_bootldr, sizeof(dest->part_bootldr),
			"%s%d", path, part_idx);

		dest->size_bootldr = MB2BYTES(4);

		dest->part_boot_idx = part_idx++;
	} else {
		*dest->part_bootldr = '\0';
		dest->size_bootldr = 0;
	}

	dest->size_boot = hw_boot_size(dest);

	// Create an EFI partition when running in EFI mode
	if (hw->efi)
		dest->size_boot_efi = MB2BYTES(32);
	else
		dest->size_boot_efi = 0;

	// Determine the size of the data partition.
	unsigned long long space_left = dest->size - \
		(dest->size_bootldr + dest->size_boot + dest->size_boot_efi);

	// If we have less than 2GB left, we disable swap
	if (space_left <= MB2BYTES(2048))
		disable_swap = 1;

	// Should we use swap?
	if (disable_swap)
		dest->size_swap = 0;
	else
		dest->size_swap = hw_swap_size(dest);

	// Subtract swap
	space_left -= dest->size_swap;

	// Root is getting what ever is left
	dest->size_root = space_left;

	// Set partition names
	if (dest->size_boot > 0) {
		if (dest->part_boot_idx == 0)
			dest->part_boot_idx = part_idx;

		snprintf(dest->part_boot, sizeof(dest->part_boot), "%s%d", path, part_idx++);
	} else
		*dest->part_boot = '\0';

	if (dest->size_boot_efi > 0) {
		dest->part_boot_efi_idx = part_idx;

		snprintf(dest->part_boot_efi, sizeof(dest->part_boot_efi),
			"%s%d", path, part_idx++);
	} else {
		*dest->part_boot_efi = '\0';
		dest->part_boot_efi_idx = 0;
	}

	if (dest->size_swap > 0)
		snprintf(dest->part_swap, sizeof(dest->part_swap), "%s%d", path, part_idx++);
	else
		*dest->part_swap = '\0';

	// There is always a root partition
	if (dest->part_boot_idx == 0)
		dest->part_boot_idx = part_idx;

	snprintf(dest->part_root, sizeof(dest->part_root), "%s%d", path, part_idx++);

	return 0;
}

struct hw_destination* hw_make_destination(struct hw* hw, int part_type, struct hw_disk** disks, int disable_swap) {
	struct hw_destination* dest = malloc(sizeof(*dest));

	if (part_type == HW_PART_TYPE_NORMAL) {
		dest->disk1 = *disks;
		dest->disk2 = NULL;

		strncpy(dest->path, dest->disk1->path, sizeof(dest->path));

	} else if (part_type == HW_PART_TYPE_RAID1) {
		dest->disk1 = *disks++;
		dest->disk2 = *disks;
		dest->raid_level = 1;

		snprintf(dest->path, sizeof(dest->path), "/dev/md0");
	}

	// Is this a RAID device?
	dest->is_raid = (part_type > HW_PART_TYPE_NORMAL);

	int r = hw_calculate_partition_table(hw, dest, disable_swap);
	if (r)
		return NULL;

	// Set default filesystem
	dest->filesystem = HW_FS_DEFAULT;

	return dest;
}

unsigned long long hw_memory() {
	struct sysinfo si;

	int r = sysinfo(&si);
	if (r < 0)
		return 0;

	return si.totalram;
}

static int hw_zero_out_device(const char* path, int bytes) {
	char block[512];
	memset(block, 0, sizeof(block));

	int blocks = bytes / sizeof(block);

	int fd = open(path, O_WRONLY);
	if (fd < 0)
		return -1;

	unsigned int bytes_written = 0;
	while (blocks-- > 0) {
		bytes_written += write(fd, block, sizeof(block));
	}

	fsync(fd);
	close(fd);

	return bytes_written;
}

static int try_open(const char* path) {
	FILE* f = fopen(path, "r");
	if (f) {
		fclose(f);
		return 0;
	}

	return -1;
}

int hw_create_partitions(struct hw_destination* dest, const char* output) {
	// Before we write a new partition table to the disk, we will erase
	// the first couple of megabytes at the beginning of the device to
	// get rid of all left other things like bootloaders and partition tables.
	// This solves some problems when changing from MBR to GPT partitions or
	// the other way around.
	int r = hw_zero_out_device(dest->path, MB2BYTES(10));
	if (r <= 0)
		return r;

	char* cmd = NULL;
	asprintf(&cmd, "/usr/sbin/parted -s %s -a optimal", dest->path);

	// Set partition type
	if (dest->part_table == HW_PART_TABLE_MSDOS)
		asprintf(&cmd, "%s mklabel msdos", cmd);
	else if (dest->part_table == HW_PART_TABLE_GPT)
		asprintf(&cmd, "%s mklabel gpt", cmd);

	unsigned long long part_start = MB2BYTES(1);

	if (*dest->part_bootldr) {
		asprintf(&cmd, "%s mkpart %s ext2 %lluB %lluB", cmd,
			(dest->part_table == HW_PART_TABLE_GPT) ? "BOOTLDR" : "primary",
		part_start, part_start + dest->size_bootldr - 1);

		part_start += dest->size_bootldr;
	}

	if (*dest->part_boot) {
		asprintf(&cmd, "%s mkpart %s ext2 %lluB %lluB", cmd,
			(dest->part_table == HW_PART_TABLE_GPT) ? "BOOT" : "primary",
			part_start, part_start + dest->size_boot - 1);

		part_start += dest->size_boot;
	}

	if (*dest->part_boot_efi) {
		asprintf(&cmd, "%s mkpart %s fat32 %lluB %lluB", cmd,
			(dest->part_table == HW_PART_TABLE_GPT) ? "ESP" : "primary",
			part_start, part_start + dest->size_boot_efi - 1);

		part_start += dest->size_boot_efi;
	}

	if (*dest->part_swap) {
		asprintf(&cmd, "%s mkpart %s linux-swap %lluB %lluB", cmd,
			(dest->part_table == HW_PART_TABLE_GPT) ? "SWAP" : "primary",
			part_start, part_start + dest->size_swap - 1);

		part_start += dest->size_swap;
	}

	if (*dest->part_root) {
		asprintf(&cmd, "%s mkpart %s ext2 %lluB %lluB", cmd,
			(dest->part_table == HW_PART_TABLE_GPT) ? "ROOT" : "primary",
			part_start, part_start + dest->size_root - 1);

		part_start += dest->size_root;
	}

	if (dest->part_boot_idx > 0)
		asprintf(&cmd, "%s set %d boot on", cmd, dest->part_boot_idx);

	if (dest->part_boot_efi_idx > 0)
		asprintf(&cmd, "%s set %d esp on", cmd, dest->part_boot_efi_idx);

	if (dest->part_table == HW_PART_TABLE_GPT) {
		if (*dest->part_bootldr) {
			asprintf(&cmd, "%s set %d bios_grub on", cmd, dest->part_boot_idx);
		}
	}

	r = mysystem(output, cmd);

	// Wait until the system re-read the partition table
	if (r == 0) {
		unsigned int counter = 10;

		while (counter-- > 0) {
			sleep(1);

			if (*dest->part_bootldr && (try_open(dest->part_bootldr) != 0))
				continue;

			if (*dest->part_boot && (try_open(dest->part_boot) != 0))
				continue;

			if (*dest->part_boot_efi && (try_open(dest->part_boot_efi) != 0))
				continue;

			if (*dest->part_swap && (try_open(dest->part_swap) != 0))
				continue;

			if (*dest->part_root && (try_open(dest->part_root) != 0))
				continue;

			// All partitions do exist, exiting the loop.
			break;
		}
	}

	if (cmd)
		free(cmd);

	return r;
}

static int hw_format_filesystem(const char* path, int fs, const char* output) {
	char cmd[STRING_SIZE] = "\0";

	// Swap
	if (fs == HW_FS_SWAP) {
		snprintf(cmd, sizeof(cmd), "/sbin/mkswap -v1 %s &>/dev/null", path);
	// ReiserFS
	} else if (fs == HW_FS_REISERFS) {
		snprintf(cmd, sizeof(cmd), "/sbin/mkreiserfs -f %s ", path);

	// EXT4
	} else if (fs == HW_FS_EXT4) {
		snprintf(cmd, sizeof(cmd), "/sbin/mke2fs -FF -T ext4 %s", path);

	// EXT4 w/o journal
	} else if (fs == HW_FS_EXT4_WO_JOURNAL) {
		snprintf(cmd, sizeof(cmd), "/sbin/mke2fs -FF -T ext4 -O ^has_journal %s", path);

	// XFS
	} else if (fs == HW_FS_XFS) {
		snprintf(cmd, sizeof(cmd), "/sbin/mkfs.xfs -f %s", path);

	// FAT32
	} else if (fs == HW_FS_FAT32) {
		snprintf(cmd, sizeof(cmd), "/sbin/mkfs.vfat %s", path);
	}

	assert(*cmd);

	int r = mysystem(output, cmd);

	return r;
}

int hw_create_filesystems(struct hw_destination* dest, const char* output) {
	int r;

	// boot
	if (*dest->part_boot) {
		r = hw_format_filesystem(dest->part_boot, dest->filesystem, output);
		if (r)
			return r;
	}

	// ESP
	if (*dest->part_boot_efi) {
		r = hw_format_filesystem(dest->part_boot_efi, HW_FS_FAT32, output);
		if (r)
			return r;
	}

	// swap
	if (*dest->part_swap) {
		r = hw_format_filesystem(dest->part_swap, HW_FS_SWAP, output);
		if (r)
			return r;
	}

	// root
	r = hw_format_filesystem(dest->part_root, dest->filesystem, output);
	if (r)
		return r;

	return 0;
}

int hw_mount_filesystems(struct hw_destination* dest, const char* prefix) {
	char target[STRING_SIZE];

	assert(*prefix == '/');

	const char* filesystem;
	switch (dest->filesystem) {
		case HW_FS_REISERFS:
			filesystem = "reiserfs";
			break;

		case HW_FS_EXT4:
		case HW_FS_EXT4_WO_JOURNAL:
			filesystem = "ext4";
			break;

		case HW_FS_XFS:
			filesystem = "xfs";
			break;

		case HW_FS_FAT32:
			filesystem = "vfat";
			break;

		default:
			assert(0);
	}

	// root
	int r = hw_mount(dest->part_root, prefix, filesystem, 0);
	if (r)
		return r;

	// boot
	if (*dest->part_boot) {
		snprintf(target, sizeof(target), "%s%s", prefix, HW_PATH_BOOT);
		mkdir(target, S_IRWXU|S_IRWXG|S_IRWXO);

		r = hw_mount(dest->part_boot, target, filesystem, 0);
		if (r) {
			hw_umount_filesystems(dest, prefix);

			return r;
		}
	}

	// ESP
	if (*dest->part_boot_efi) {
		snprintf(target, sizeof(target), "%s%s", prefix, HW_PATH_BOOT_EFI);
		mkdir(target, S_IRWXU|S_IRWXG|S_IRWXO);

		r = hw_mount(dest->part_boot_efi, target, "vfat", 0);
		if (r) {
			hw_umount_filesystems(dest, prefix);

			return r;
		}
	}

	// swap
	if (*dest->part_swap) {
		r = swapon(dest->part_swap, 0);
		if (r) {
			hw_umount_filesystems(dest, prefix);

			return r;
		}
	}

	// bind-mount misc filesystems
	r = hw_bind_mount("/dev", prefix);
	if (r)
		return r;

	r = hw_bind_mount("/proc", prefix);
	if (r)
		return r;

	r = hw_bind_mount("/sys", prefix);
	if (r)
		return r;

	r = hw_bind_mount("/sys/firmware/efi/efivars", prefix);
	if (r && errno != ENOENT)
		return r;

	return 0;
}

int hw_umount_filesystems(struct hw_destination* dest, const char* prefix) {
	int r;
	char target[STRING_SIZE];

	// Write all buffers to disk before umounting
	hw_sync();

	// ESP
	if (*dest->part_boot_efi) {
		r = hw_umount(HW_PATH_BOOT_EFI, prefix);
		if (r)
			return -1;
	}

	// boot
	if (*dest->part_boot) {
		r = hw_umount(HW_PATH_BOOT, prefix);
		if (r)
			return -1;
	}

	// swap
	if (*dest->part_swap) {
		swapoff(dest->part_swap);
	}

	// misc filesystems
	r = hw_umount("/sys/firmware/efi/efivars", prefix);
	if (r)
		return -1;

	r = hw_umount("/sys", prefix);
	if (r)
		return -1;

	r = hw_umount("/proc", prefix);
	if (r)
		return -1;

	r = hw_umount("/dev", prefix);
	if (r)
		return -1;

	// root
	r = hw_umount(prefix, NULL);
	if (r)
		return -1;

	return 0;
}

int hw_destroy_raid_superblocks(const struct hw_destination* dest, const char* output) {
	char cmd[STRING_SIZE];

	hw_stop_all_raid_arrays(output);
	hw_stop_all_raid_arrays(output);

	if (dest->disk1) {
		snprintf(cmd, sizeof(cmd), "/sbin/mdadm --zero-superblock %s", dest->disk1->path);
		mysystem(output, cmd);
	}

	if (dest->disk2) {
		snprintf(cmd, sizeof(cmd), "/sbin/mdadm --zero-superblock %s", dest->disk2->path);
		mysystem(output, cmd);
	}

	return 0;
}

int hw_setup_raid(struct hw_destination* dest, const char* output) {
	char* cmd = NULL;
	int r;

	assert(dest->is_raid);

	// Stop all RAID arrays that might be around (again).
	// It seems that there is some sort of race-condition with udev re-enabling
	// the raid arrays and therefore locking the disks.
	r = hw_destroy_raid_superblocks(dest, output);

	asprintf(&cmd, "echo \"y\" | /sbin/mdadm --create --verbose --metadata=%s --auto=mdp %s",
		RAID_METADATA, dest->path);

	switch (dest->raid_level) {
		case 1:
			asprintf(&cmd, "%s --level=1 --raid-devices=2", cmd);
			break;

		default:
			assert(0);
	}

	if (dest->disk1) {
		asprintf(&cmd, "%s %s", cmd, dest->disk1->path);

		// Clear all data at the beginning
		r = hw_zero_out_device(dest->disk1->path, MB2BYTES(10));
		if (r <= 0)
			return r;
	}

	if (dest->disk2) {
		asprintf(&cmd, "%s %s", cmd, dest->disk2->path);

		// Clear all data at the beginning
		r = hw_zero_out_device(dest->disk2->path, MB2BYTES(10));
		if (r <= 0)
			return r;
	}

	r = mysystem(output, cmd);
	free(cmd);

	// Wait a moment until the device has been properly brought up
	if (r == 0) {
		unsigned int counter = 10;
		while (counter-- > 0) {
			sleep(1);

			// If the raid device has not yet been properly brought up,
			// opening it will fail with the message: Device or resource busy
			// Hence we will wait a bit until it becomes usable.
			if (try_open(dest->path) == 0)
				break;
		}
	}

	return r;
}

int hw_stop_all_raid_arrays(const char* output) {
	return mysystem(output, "/sbin/mdadm --stop --scan --verbose");
}

int hw_install_bootloader(struct hw* hw, struct hw_destination* dest, const char* output) {
	char cmd[STRING_SIZE];

	snprintf(cmd, sizeof(cmd), "/usr/bin/install-bootloader %s", dest->path);
	int r = system_chroot(output, DESTINATION_MOUNT_PATH, cmd);
	if (r)
		return r;

	hw_sync();

	return 0;
}

static char* hw_get_uuid(const char* dev) {
	blkid_probe p = blkid_new_probe_from_filename(dev);
	const char* buffer = NULL;
	char* uuid = NULL;

	if (!p)
		return NULL;

	blkid_do_probe(p);
	blkid_probe_lookup_value(p, "UUID", &buffer, NULL);

	if (buffer)
		uuid = strdup(buffer);

	blkid_free_probe(p);

	return uuid;
}

#define FSTAB_FMT "UUID=%s %-8s %-4s %-10s %d %d\n"

int hw_write_fstab(struct hw_destination* dest) {
	FILE* f = fopen(DESTINATION_MOUNT_PATH "/etc/fstab", "w");
	if (!f)
		return -1;

	char* uuid = NULL;

	// boot
	if (*dest->part_boot) {
		uuid = hw_get_uuid(dest->part_boot);

		if (uuid) {
			fprintf(f, FSTAB_FMT, uuid, "/boot", "auto", "defaults", 1, 2);
			free(uuid);
		}
	}

	// ESP
	if (*dest->part_boot_efi) {
		uuid = hw_get_uuid(dest->part_boot_efi);

		if (uuid) {
			fprintf(f, FSTAB_FMT, uuid, "/boot/efi", "auto", "defaults", 1, 2);
			free(uuid);
		}
	}


	// swap
	if (*dest->part_swap) {
		uuid = hw_get_uuid(dest->part_swap);

		if (uuid) {
			fprintf(f, FSTAB_FMT, uuid, "swap", "swap", "defaults,pri=1", 0, 0);
			free(uuid);
		}
	}

	// root
	uuid = hw_get_uuid(dest->part_root);
	if (uuid) {
		fprintf(f, FSTAB_FMT, uuid, "/", "auto", "defaults", 1, 1);
		free(uuid);
	}

	fclose(f);

	return 0;
}

void hw_sync() {
	sync();
	sync();
	sync();
}

int hw_start_networking(const char* output) {
	return mysystem(output, "/usr/bin/start-networking.sh");
}

char* hw_find_backup_file(const char* output, const char* search_path) {
	char path[STRING_SIZE];

	snprintf(path, sizeof(path), "%s/backup.ipf", search_path);
	int r = access(path, R_OK);

	if (r == 0)
		return strdup(path);

	return NULL;
}

int hw_restore_backup(const char* output, const char* backup_path, const char* destination) {
	char command[STRING_SIZE];

	snprintf(command, sizeof(command), "/bin/tar xzpf %s -C %s", backup_path, destination);
	int rc = mysystem(output, command);

	if (rc)
		return -1;

	return 0;
}
