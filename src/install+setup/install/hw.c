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
#include <fcntl.h>
#include <libudev.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mount.h>
#include <sys/swap.h>
#include <unistd.h>

#include <linux/fs.h>

#include "hw.h"
#include "../libsmooth/libsmooth.h"

const char* other_filesystems[] = {
	"/dev",
	"/proc",
	"/sys",
	NULL
};

struct hw* hw_init() {
	struct hw* hw = malloc(sizeof(*hw));
	assert(hw);

	// Initialize libudev
	hw->udev = udev_new();
	if (!hw->udev) {
		fprintf(stderr, "Could not create udev instance\n");
		exit(1);
	}

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

int hw_mount(const char* source, const char* target, const char* fs, int flags) {
	return mount(source, target, fs, flags, NULL);
}

int hw_umount(const char* target) {
	return umount2(target, MNT_DETACH);
}

static int hw_test_source_medium(const char* path) {
	int ret = hw_mount(path, SOURCE_MOUNT_PATH, "iso9660", MS_RDONLY);

	// If the source could not be mounted we
	// cannot proceed.
	if (ret)
		return ret;

	// Check if the test file exists.
	ret = access(SOURCE_TEST_FILE, F_OK);

	// Umount the test device.
	hw_umount(SOURCE_MOUNT_PATH);

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
				strstartswith(dev_path, "/dev/ram"))
			continue;

		if (hw_test_source_medium(dev_path)) {
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

struct hw_disk** hw_find_disks(struct hw* hw) {
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
				strstartswith(dev_path, "/dev/ram") || strstartswith(dev_path, "/dev/sr")) {
			udev_device_unref(dev);
			continue;
		}

		// DEVTYPE must be disk (otherwise we will see all sorts of partitions here)
		const char* devtype = udev_device_get_property_value(dev, "DEVTYPE");
		if (devtype && (strcmp(devtype, "disk") != 0)) {
			udev_device_unref(dev);
			continue;
		}

		// Skip all source mediums
		if (hw_test_source_medium(dev_path) == 0) {
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

		disk->size = size;

		// Vendor
		const char* vendor = udev_device_get_property_value(dev, "ID_VENDOR");
		if (!vendor)
			vendor = udev_device_get_sysattr_value(dev, "vendor");
		if (!vendor)
			vendor = udev_device_get_sysattr_value(dev, "manufacturer");
		if (!vendor)
			vendor = "N/A";

		strncpy(disk->vendor, vendor, sizeof(disk->vendor));

		// Model
		const char* model = udev_device_get_property_value(dev, "ID_MODEL");
		if (!model)
			model = udev_device_get_sysattr_value(dev, "model");
		if (!model)
			model = udev_device_get_sysattr_value(dev, "product");
		if (!model)
			model = "N/A";

		strncpy(disk->model, model, sizeof(disk->model));

		snprintf(disk->description, sizeof(disk->description),
			"%4.1fGB %s - %s", (double)disk->size / pow(1024, 3),
			disk->vendor, disk->model);

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

unsigned int hw_count_disks(struct hw_disk** disks) {
	unsigned int ret = 0;

	while (*disks++)
		ret++;

	return ret;
}

struct hw_disk** hw_select_disks(struct hw_disk** disks, int* selection) {
	struct hw_disk** ret = hw_create_disks();
	struct hw_disk** selected_disks = ret;

	unsigned int num_disks = hw_count_disks(disks);

	for (unsigned int i = 0; i < num_disks; i++) {
		if (selection && selection[i]) {
			struct hw_disk *selected_disk = disks[i];
			selected_disk->ref++;

			*selected_disks++ = selected_disk;
		}
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

static unsigned long long hw_root_size(struct hw_destination* dest) {
	unsigned long long root_size;

	if (dest->size < MB2BYTES(2048))
		root_size = MB2BYTES(1024);

	else if (dest->size >= MB2BYTES(2048) && dest->size <= MB2BYTES(3072))
		root_size = MB2BYTES(1536);

	else
		root_size = MB2BYTES(2048);

	return root_size;
}

static unsigned long long hw_boot_size(struct hw_destination* dest) {
	return MB2BYTES(64);
}

static int hw_calculate_partition_table(struct hw_destination* dest) {
	// Determine the size of the target block device
	if (dest->is_raid) {
		dest->size = (dest->disk1->size >= dest->disk2->size) ?
			dest->disk1->size : dest->disk2->size;
	} else {
		dest->size = dest->disk1->size;
	}

	dest->size_boot = hw_boot_size(dest);
	dest->size_swap = hw_swap_size(dest);
	dest->size_root = hw_root_size(dest);

	// Determine the size of the data partition.
	unsigned long long used_space = dest->size_boot + dest->size_swap + dest->size_root;

	// Disk is way too small
	if (used_space >= dest->size)
		return -1;

	dest->size_data = dest->size - used_space;

	// If it gets too small, we remove the swap space.
	if (dest->size_data <= MB2BYTES(256)) {
		dest->size_data += dest->size_swap;
		dest->size_swap = 0;
	}

	// Set partition names
	char path[DEV_SIZE];
	int part_idx = 1;

	snprintf(path, sizeof(path), "%s%s", dest->path, (dest->is_raid) ? "p" : "");

	if (dest->size_boot > 0) {
		dest->part_boot_idx = part_idx;

		snprintf(dest->part_boot, sizeof(dest->part_boot), "%s%d", path, part_idx++);
	} else
		*dest->part_boot = '\0';

	if (dest->size_swap > 0)
		snprintf(dest->part_swap, sizeof(dest->part_swap), "%s%d", path, part_idx++);
	else
		*dest->part_swap = '\0';

	// There is always a root partition
	if (!*dest->part_boot)
		dest->part_boot_idx = part_idx;

	snprintf(dest->part_root, sizeof(dest->part_root), "%s%d", path, part_idx++);

	if (dest->size_data > 0)
		snprintf(dest->part_data, sizeof(dest->part_data), "%s%d", path, part_idx++);
	else
		*dest->part_data = '\0';

	// Determine partition table
	dest->part_table = HW_PART_TABLE_MSDOS;

	// Disks over 2TB need to use GPT
	if (dest->size >= MB2BYTES(2047 * 1024))
		dest->part_table = HW_PART_TABLE_GPT;

	// We also use GPT on raid disks by default
	else if (dest->is_raid)
		dest->part_table = HW_PART_TABLE_GPT;

	return 0;
}

struct hw_destination* hw_make_destination(int part_type, struct hw_disk** disks) {
	struct hw_destination* dest = malloc(sizeof(*dest));

	if (part_type == HW_PART_TYPE_NORMAL) {
		dest->disk1 = *disks;
		dest->disk2 = NULL;

		strncpy(dest->path, dest->disk1->path, sizeof(dest->path));

	} else if (part_type == HW_PART_TYPE_RAID1) {
		dest->disk1 = *disks++;
		dest->disk2 = *disks;

		snprintf(dest->path, sizeof(dest->path), "/dev/md0");
	}

	// Is this a RAID device?
	dest->is_raid = (part_type > HW_PART_TYPE_NORMAL);

	int r = hw_calculate_partition_table(dest);
	if (r)
		return NULL;

	// Set default filesystem
	dest->filesystem = HW_FS_DEFAULT;

	return dest;
}

unsigned long long hw_memory() {
	FILE* handle = NULL;
	char line[STRING_SIZE];

	unsigned long long memory = 0;

	/* Calculate amount of memory in machine */
	if ((handle = fopen("/proc/meminfo", "r"))) {
		while (fgets(line, sizeof(line), handle)) {
			if (!sscanf (line, "MemTotal: %llu kB", &memory)) {
				memory = 0;
			}
		}

		fclose(handle);
	}

	return memory * 1024;
}

int hw_create_partitions(struct hw_destination* dest) {
	char* cmd = NULL;

	asprintf(&cmd, "/usr/sbin/parted -s %s -a optimal", dest->path);

	// Set partition type
	if (dest->part_table == HW_PART_TABLE_MSDOS)
		asprintf(&cmd, "%s mklabel msdos", cmd);
	else if (dest->part_table == HW_PART_TABLE_GPT)
		asprintf(&cmd, "%s mklabel gpt", cmd);

	unsigned long long part_start = 0 * 1024 * 1024; // 1MB

	if (*dest->part_boot) {
		asprintf(&cmd, "%s mkpart %s ext2 %lluMB %lluMB", cmd,
			(dest->part_table == HW_PART_TABLE_GPT) ? "BOOT" : "primary",
			BYTES2MB(part_start), BYTES2MB(part_start + dest->size_boot));

		part_start += dest->size_boot;
	}

	if (*dest->part_swap) {
		asprintf(&cmd, "%s mkpart %s linux-swap %lluMB %lluMB", cmd,
			(dest->part_table == HW_PART_TABLE_GPT) ? "SWAP" : "primary",
			BYTES2MB(part_start), BYTES2MB(part_start + dest->size_swap));

		part_start += dest->size_swap;
	}

	if (*dest->part_root) {
		asprintf(&cmd, "%s mkpart %s ext2 %lluMB %lluMB", cmd,
			(dest->part_table == HW_PART_TABLE_GPT) ? "ROOT" : "primary",
			BYTES2MB(part_start), BYTES2MB(part_start + dest->size_root));

		part_start += dest->size_root;
	}

	if (*dest->part_data) {
		asprintf(&cmd, "%s mkpart %s ext2 %lluMB %lluMB", cmd,
			(dest->part_table == HW_PART_TABLE_GPT) ? "DATA" : "primary",
			BYTES2MB(part_start), BYTES2MB(part_start + dest->size_data));

		part_start += dest->size_data;
	}

	if (dest->part_table == HW_PART_TABLE_MSDOS && dest->part_boot_idx > 0) {
		asprintf(&cmd, "%s set %d boot on", cmd, dest->part_boot_idx);

	} else if (dest->part_table == HW_PART_TABLE_GPT) {
		asprintf(&cmd, "%s disk_set pmbr_boot on", cmd);
	}

	int r = mysystem(cmd);

	if (cmd)
		free(cmd);

	return r;
}

static int hw_format_filesystem(const char* path, int fs) {
	char cmd[STRING_SIZE] = "\0";

	// Swap
	if (fs == HW_FS_SWAP) {
		snprintf(cmd, sizeof(cmd), "/sbin/mkswap -v1 %s &>/dev/null", path);
	// ReiserFS
	} else if (fs == HW_FS_REISERFS) {
		snprintf(cmd, sizeof(cmd), "/sbin/mkreiserfs -f %s ", path);

	// EXT4
	} else if (fs == HW_FS_EXT4) {
		snprintf(cmd, sizeof(cmd), "/sbin/mke2fs -T ext4 %s", path);

	// EXT4 w/o journal
	} else if (fs == HW_FS_EXT4_WO_JOURNAL) {
		snprintf(cmd, sizeof(cmd), "/sbin/mke2fs -T ext4 -O ^has_journal %s", path);
	}

	assert(*cmd);

	int r = mysystem(cmd);

	return r;
}

int hw_create_filesystems(struct hw_destination* dest) {
	int r;

	// boot
	if (*dest->part_boot) {
		r = hw_format_filesystem(dest->part_boot, dest->filesystem);
		if (r)
			return r;
	}

	// swap
	if (*dest->part_swap) {
		r = hw_format_filesystem(dest->part_swap, HW_FS_SWAP);
		if (r)
			return r;
	}

	// root
	r = hw_format_filesystem(dest->part_root, dest->filesystem);
	if (r)
		return r;

	// data
	if (*dest->part_data) {
		r = hw_format_filesystem(dest->part_data, dest->filesystem);
		if (r)
			return r;
	}

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

	// data
	if (*dest->part_data) {
		snprintf(target, sizeof(target), "%s%s", prefix, HW_PATH_DATA);
		mkdir(target, S_IRWXU|S_IRWXG|S_IRWXO);

		r = hw_mount(dest->part_data, target, filesystem, 0);
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
	char** otherfs = other_filesystems;
	while (*otherfs) {
		snprintf(target, sizeof(target), "%s%s", prefix, *otherfs);

		mkdir(target, S_IRWXU|S_IRWXG|S_IRWXO);
		r = hw_mount(*otherfs, target, NULL, MS_BIND);
		if (r) {
			hw_umount_filesystems(dest, prefix);

			return r;
		}

		otherfs++;
	}

	return 0;
}

int hw_umount_filesystems(struct hw_destination* dest, const char* prefix) {
	// boot
	if (*dest->part_boot) {
		hw_umount(dest->part_boot);
	}

	// data
	if (*dest->part_data) {
		hw_umount(dest->part_data);
	}

	// root
	hw_umount(dest->part_root);

	// swap
	if (*dest->part_swap) {
		swapoff(dest->part_swap);
	}

	// misc filesystems
	char target[STRING_SIZE];
	char** otherfs = other_filesystems;

	while (*otherfs) {
		snprintf(target, sizeof(target), "%s%s", prefix, *otherfs++);
		hw_umount(target);
	}

	return 0;
}
