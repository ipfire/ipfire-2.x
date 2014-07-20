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

#ifndef HEADER_HW_H
#define HEADER_HW_H

#include <libudev.h>

#define SOURCE_MOUNT_PATH "/cdrom"
#define SOURCE_TEST_FILE  SOURCE_MOUNT_PATH "/" VERSION ".media"

#define HW_MAX_DISKS                 32
#define STRING_SIZE                1024
#define DEV_SIZE                    128

#define HW_PART_TYPE_NORMAL           0
#define HW_PART_TYPE_RAID1            1

struct hw {
	struct udev *udev;
};

struct hw_disk {
	char path[DEV_SIZE];
	unsigned long long size;

	char description[STRING_SIZE];
	char vendor[STRING_SIZE];
	char model[STRING_SIZE];

	// Reference counter
	int ref;
};

struct hw_destination {
	char path[DEV_SIZE];
	unsigned long long size;

	int is_raid;

	const struct hw_disk* disk1;
	const struct hw_disk* disk2;

	char part_boot[DEV_SIZE];
	char part_swap[DEV_SIZE];
	char part_root[DEV_SIZE];
	char part_data[DEV_SIZE];
};

struct hw* hw_init();
void hw_free(struct hw* hw);

int hw_mount(const char* source, const char* target, int flags);
int hw_umount(const char* target);

char* hw_find_source_medium(struct hw* hw);

struct hw_disk** hw_find_disks(struct hw* hw);
void hw_free_disks(struct hw_disk** disks);
unsigned int hw_count_disks(struct hw_disk** disks);
struct hw_disk** hw_select_disks(struct hw_disk** disks, int* selection);

#endif /* HEADER_HW_H */
