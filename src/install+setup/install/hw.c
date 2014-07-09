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
#include <libudev.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>
#include <unistd.h>

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
