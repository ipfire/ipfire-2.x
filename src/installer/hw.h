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

#define DESTINATION_MOUNT_PATH        "/harddisk"
#define SOURCE_MOUNT_PATH             "/cdrom"
#define SOURCE_TEST_FILE              SOURCE_MOUNT_PATH "/" DISTRO_SNAME "-" DISTRO_VERSION ".media"

#define HW_MAX_DISKS                 32
#define STRING_SIZE                1024
#define DEV_SIZE                    128

#define HW_PATH_BOOT                  "/boot"
#define HW_PATH_BOOT_EFI              "/boot/efi"
#define HW_PATH_DATA                  "/var"

#define HW_PART_TYPE_NORMAL           0
#define HW_PART_TYPE_RAID1            1

#define HW_PART_TABLE_MSDOS           0
#define HW_PART_TABLE_GPT             1

#define HW_FS_SWAP                    0
#define HW_FS_REISERFS                1
#define HW_FS_EXT4                    2
#define HW_FS_EXT4_WO_JOURNAL         3
#define HW_FS_XFS                     4
#define HW_FS_FAT32                   5

#define HW_FS_DEFAULT                 HW_FS_EXT4

#define RAID_METADATA                 "1.0"

#define SERIAL_BAUDRATE               115200

#define BYTES2MB(x) ((x) / 1024 / 1024)
#define MB2BYTES(x) ((unsigned long long)(x) * 1024 * 1024)

struct hw {
	struct udev *udev;
	char arch[STRING_SIZE];

	// Enabled if we should install in EFI mode
	int efi;
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

	int is_raid;
	int raid_level;
	const struct hw_disk* disk1;
	const struct hw_disk* disk2;

	int part_table;
	char part_bootldr[DEV_SIZE];
	char part_boot[DEV_SIZE];
	char part_boot_efi[DEV_SIZE];
	char part_swap[DEV_SIZE];
	char part_root[DEV_SIZE];
	int part_boot_idx;
	int part_boot_efi_idx;

	int filesystem;

	unsigned long long size;
	unsigned long long size_bootldr;
	unsigned long long size_boot;
	unsigned long long size_boot_efi;
	unsigned long long size_swap;
	unsigned long long size_root;
};

struct hw* hw_init();
void hw_free(struct hw* hw);

int hw_mount(const char* source, const char* target, const char* fs, int flags);
int hw_umount(const char* source, const char* prefix);

char* hw_find_source_medium(struct hw* hw);

struct hw_disk** hw_find_disks(struct hw* hw, const char* sourcedrive);
void hw_free_disks(struct hw_disk** disks);
unsigned int hw_count_disks(const struct hw_disk** disks);
struct hw_disk** hw_select_disks(struct hw_disk** disks, int* selection);
struct hw_disk** hw_select_first_disk(const struct hw_disk** disks);

struct hw_destination* hw_make_destination(struct hw* hw, int part_type, struct hw_disk** disks,
	int disable_swap);

unsigned long long hw_memory();

int hw_create_partitions(struct hw_destination* dest, const char* output);
int hw_create_filesystems(struct hw_destination* dest, const char* output);

int hw_mount_filesystems(struct hw_destination* dest, const char* prefix);
int hw_umount_filesystems(struct hw_destination* dest, const char* prefix);

int hw_destroy_raid_superblocks(const struct hw_destination* dest, const char* output);
int hw_setup_raid(struct hw_destination* dest, const char* output);
int hw_stop_all_raid_arrays(const char* output);

int hw_install_bootloader(struct hw* hw, struct hw_destination* dest, const char* output);
int hw_write_fstab(struct hw_destination* dest);

char* hw_find_backup_file(const char* output, const char* search_path);
int hw_restore_backup(const char* output, const char* backup_path, const char* destination);

int hw_start_networking(const char* output);

void hw_sync();

#endif /* HEADER_HW_H */
