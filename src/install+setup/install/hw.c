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
#include <unistd.h>

#include <linux/fs.h>

#include "hw.h"

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

int hw_mount(const char* source, const char* target, int flags) {
	return mount(source, target, "iso9660", flags, NULL);
}

int hw_umount(const char* target) {
	return umount2(target, MNT_DETACH);
}

static int hw_test_source_medium(const char* path) {
	int ret = hw_mount(path, SOURCE_MOUNT_PATH, MS_RDONLY);

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

	// Set partition names
	char path[DEV_SIZE];
	snprintf(path, sizeof(path), "%s%s", dest->path, (dest->is_raid) ? "p" : "");
	snprintf(dest->part_boot, sizeof(dest->part_boot), "%s1", path);
	snprintf(dest->part_swap, sizeof(dest->part_swap), "%s2", path);
	snprintf(dest->part_root, sizeof(dest->part_root), "%s3", path);
	snprintf(dest->part_data, sizeof(dest->part_data), "%s4", path);

	if (dest->is_raid) {
		dest->size = (dest->disk1->size >= dest->disk2->size) ?
			dest->disk1->size : dest->disk2->size;
	} else {
		dest->size = dest->disk1->size;
	}

	return dest;
}
