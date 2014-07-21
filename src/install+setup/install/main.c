
/* SmoothWall install program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Contains main entry point, and misc functions.6
 * 
 */

#define _GNU_SOURCE

#include <assert.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>

#include "hw.h"
#include "install.h"
 
#define INST_FILECOUNT 21000
#define UNATTENDED_CONF "/cdrom/boot/unattended.conf"
#define LICENSE_FILE	"/cdrom/COPYING"

FILE *flog = NULL;
char *mylog;

char **ctr;

extern char url[STRING_SIZE];

struct  nic  nics[20] = { { "" , "" , "" } }; // only defined for compile
struct knic knics[20] = { { "" , "" , "" , "" } }; // only defined for compile

extern char *en_tr[];
extern char *es_tr[];
extern char *de_tr[];
extern char *fr_tr[];
extern char *nl_tr[];
extern char *pl_tr[];
extern char *ru_tr[];
extern char *tr_tr[];

static int newtChecklist(const char* title, const char* message,
		unsigned int width, unsigned int height, unsigned int num_entries,
		const char** entries, int* states) {
	int ret;
	const int list_height = 4;

	char cbstates[num_entries];

	for (unsigned int i = 0; i < num_entries; i++) {
		cbstates[i] = states[i] ? '*' : ' ';
	}

	newtCenteredWindow(width, height, title);

	newtComponent textbox = newtTextbox(1, 1, width - 2, height - 6 - list_height,
		NEWT_FLAG_WRAP);
	newtTextboxSetText(textbox, message);

	int top = newtTextboxGetNumLines(textbox) + 2;

	newtComponent form = newtForm(NULL, NULL, 0);

	newtComponent sb = NULL;
	if (list_height < num_entries) {
		sb = newtVerticalScrollbar(
			width - 4, top + 1, list_height,
			NEWT_COLORSET_CHECKBOX, NEWT_COLORSET_ACTCHECKBOX);

		newtFormAddComponent(form, sb);
	}

	newtComponent subform = newtForm(sb, NULL, 0);
	newtFormSetBackground(subform, NEWT_COLORSET_CHECKBOX);

	newtFormSetHeight(subform, list_height);
	newtFormSetWidth(subform, width - 10);

	for (unsigned int i = 0; i < num_entries; i++) {
		newtComponent cb = newtCheckbox(4, top + i, entries[i], cbstates[i],
			NULL, &cbstates[i]);

		newtFormAddComponent(subform, cb);
	}

	newtFormAddComponents(form, textbox, subform, NULL);

	newtComponent btn_okay   = newtButton((width - 18) / 3, height - 4, ctr[TR_OK]);
	newtComponent btn_cancel = newtButton((width - 18) / 3 * 2 + 9, height - 4, ctr[TR_CANCEL]);
	newtFormAddComponents(form, btn_okay, btn_cancel, NULL);

	newtComponent answer = newtRunForm(form);

	if ((answer == NULL) || (answer == btn_cancel)) {
		ret = -1;
	} else {
		ret = 0;

		for (unsigned int i = 0; i < num_entries; i++) {
			states[i] = (cbstates[i] != ' ');

			if (states[i])
				ret++;
		}
	}

	newtFormDestroy(form);
	newtPopWindow();

	return ret;
}

static int newtWinOkCancel(const char* title, const char* message, int width, int height,
		const char* btn_txt_ok, const char* btn_txt_cancel) {
	int ret = 1;

	newtCenteredWindow(width, height, title);

	newtComponent form = newtForm(NULL, NULL, 0);

	newtComponent textbox = newtTextbox(1, 1, width - 2, height - 6, NEWT_FLAG_WRAP);
	newtTextboxSetText(textbox, message);
	newtFormAddComponent(form, textbox);

	newtComponent btn_ok = newtButton((width - 16) / 3, height - 4, btn_txt_ok);
	newtComponent btn_cancel = newtButton((width - 16) / 3 * 2 + 9, height - 4,
		btn_txt_cancel);

	newtFormAddComponents(form, btn_ok, btn_cancel, NULL);

	newtComponent answer = newtRunForm(form);

	if (answer == btn_ok) {
		ret = 0;
	}

	newtFormDestroy(form);
	newtPopWindow();

	return ret;
}

int main(int argc, char *argv[]) {
	struct hw* hw = hw_init();

	char discl_msg[40000] =	"Disclaimer\n";

	char *langnames[] = { "Deutsch", "English", "Français", "Español", "Nederlands", "Polski", "Русский", "Türkçe", NULL };
	char *shortlangnames[] = { "de", "en", "fr", "es", "nl", "pl", "ru", "tr", NULL };
	char **langtrs[] = { de_tr, en_tr, fr_tr, es_tr, nl_tr, pl_tr, ru_tr, tr_tr, NULL };
	char* sourcedrive = NULL;
	int rc = 0;
	char commandstring[STRING_SIZE];
	int choice;
	char shortlangname[10];
	char message[STRING_SIZE];
	char title[STRING_SIZE];
	int allok = 0;
	struct keyvalue *ethernetkv = initkeyvalues();
	FILE *handle, *cmdfile, *copying;
	char line[STRING_SIZE];
		
	int unattended = 0;
	int serialconsole = 0;
	struct keyvalue *unattendedkv = initkeyvalues();
	char restore_file[STRING_SIZE] = "";

	setlocale (LC_ALL, "");
	sethostname( SNAME , 10);

	/* Log file/terminal stuff. */
	if (argc >= 2)
	{		
		if (!(flog = fopen(argv[1], "w+")))
			return 0;
	}
	else
		return 0;
	
	mylog = argv[1];
	
	fprintf(flog, "Install program started.\n");
		
	newtInit();
	newtCls();

	newtDrawRootText(14, 0, NAME " " VERSION " - " SLOGAN );
	sprintf (title, "%s %s - %s", NAME, VERSION, SLOGAN);

	if (! (cmdfile = fopen("/proc/cmdline", "r")))
	{
		fprintf(flog, "Couldn't open commandline: /proc/cmdline\n");
	} else {
		fgets(line, STRING_SIZE, cmdfile);
		
		// check if we have to make an unattended install
		if (strstr (line, "unattended") != NULL) {
		    unattended = 1;
		    runcommandwithstatus("/bin/sleep 10", "WARNING: Unattended installation will start in 10 seconds...");
		}		
		// check if we have to patch for serial console
		if (strstr (line, "console=ttyS0") != NULL) {
		    serialconsole = 1;
		}
	}

	// Load common modules
	mysystem("/sbin/modprobe vfat"); // USB key
	
	/* German is the default */
	for (choice = 0; langnames[choice]; choice++)
	{
		if (strcmp(langnames[choice], "English") == 0)
			break;
	}
	if (!langnames[choice])
		goto EXIT;

	if (!unattended) {
	    rc = newtWinMenu("Language selection", "Select the language you wish to use for the " NAME ".", 50, 5, 5, 8,
		    langnames, &choice, "Ok", NULL);
	}

	ctr = langtrs[choice];
	strcpy(shortlangname, shortlangnames[choice]);

	newtPushHelpLine(ctr[TR_HELPLINE]);

	if (!unattended) {
		sprintf(message, ctr[TR_WELCOME], NAME);
		newtWinMessage(title, ctr[TR_OK], message);
	}

	/* Search for a source drive that holds the right
	 * version of the image we are going to install. */
	sourcedrive = hw_find_source_medium(hw);

	fprintf(flog, "Source drive: %s\n", sourcedrive);
	if (!sourcedrive) {
		newtWinMessage(title, ctr[TR_OK], ctr[TR_NO_LOCAL_SOURCE]);
		runcommandwithstatus("/bin/downloadsource.sh", ctr[TR_DOWNLOADING_ISO]);
		if ((handle = fopen("/tmp/source_device", "r")) == NULL) {
			errorbox(ctr[TR_DOWNLOAD_ERROR]);
			goto EXIT;
		}

		fgets(sourcedrive, 5, handle);
		fclose(handle);
	}

	assert(sourcedrive);

	int r = hw_mount(sourcedrive, SOURCE_MOUNT_PATH, "iso9660", MS_RDONLY);
	if (r) {
		fprintf(flog, "Could not mount %s to %s\n", sourcedrive, SOURCE_MOUNT_PATH);
		fprintf(flog, strerror(errno));
		exit(1);
	}

	/* load unattended configuration */
	if (unattended) {
	    fprintf(flog, "unattended: Reading unattended.conf\n");

	    (void) readkeyvalues(unattendedkv, UNATTENDED_CONF);
	    findkey(unattendedkv, "RESTORE_FILE", restore_file);
	}

	if (!unattended) {
		// Read the license file.
		if (!(copying = fopen(LICENSE_FILE, "r"))) {
			sprintf(discl_msg, "Could not open license file: %s\n", LICENSE_FILE);
			fprintf(flog, discl_msg);
		} else {
			fread(discl_msg, 1, 40000, copying);
			fclose(copying);

			if (disclaimerbox(discl_msg)==0) {
				errorbox(ctr[TR_LICENSE_NOT_ACCEPTED]);
				goto EXIT;
			}
		}
	}

	int part_type = HW_PART_TYPE_NORMAL;

	// Scan for disks to install on.
	struct hw_disk** disks = hw_find_disks(hw);

	struct hw_disk** selected_disks = NULL;
	unsigned int num_selected_disks = 0;

	// Check how many disks have been found and what
	// we can do with them.
	unsigned int num_disks = hw_count_disks(disks);

	while (1) {
		// no harddisks found
		if (num_disks == 0) {
			errorbox(ctr[TR_NO_HARDDISK]);
			goto EXIT;

		// exactly one disk has been found
		} else if (num_disks == 1) {
			selected_disks = hw_select_disks(disks, NULL);

		// more than one usable disk has been found and
		// the user needs to choose what to do with them
		} else {
			const char* disk_names[num_disks];
			int disk_selection[num_disks];

			for (unsigned int i = 0; i < num_disks; i++) {
				disk_names[i] = &disks[i]->description;
				disk_selection[i] = 0;
			}

			while (!selected_disks) {
				rc = newtChecklist(ctr[TR_DISK_SELECTION], ctr[TR_DISK_SELECTION_MSG],
					50, 20, num_disks, disk_names, disk_selection);

				// Error
				if (rc < 0) {
					goto EXIT;

				// Nothing has been selected
				} else if (rc == 0) {
					errorbox(ctr[TR_NO_DISK_SELECTED]);

				} else {
					selected_disks = hw_select_disks(disks, disk_selection);
				}
			}
		}

		num_selected_disks = hw_count_disks(selected_disks);

		if (num_selected_disks == 1) {
			snprintf(message, sizeof(message), ctr[TR_DISK_SETUP_DESC], (*selected_disks)->description);
			rc = newtWinOkCancel(ctr[TR_DISK_SETUP], message, 50, 10,
				ctr[TR_DELETE_ALL_DATA], ctr[TR_CANCEL]);

			if (rc == 0)
				break;

		} else if (num_selected_disks == 2) {
			snprintf(message, sizeof(message), ctr[TR_RAID_SETUP_DESC],
				(*selected_disks)->description, (*selected_disks + 1)->description);
			rc = newtWinOkCancel(ctr[TR_RAID_SETUP], message, 50, 10,
				ctr[TR_DELETE_ALL_DATA], ctr[TR_CANCEL]);

			if (rc == 0) {
				part_type = HW_PART_TYPE_RAID1;

				break;
			}

		// Currently not supported
		} else {
			errorbox(ctr[TR_DISK_CONFIGURATION_NOT_SUPPORTED]);
		}

		if (selected_disks) {
			hw_free_disks(selected_disks);
			selected_disks = NULL;
		}
	}

	hw_free_disks(disks);

	struct hw_destination* destination = hw_make_destination(part_type, selected_disks);

	if (!destination) {
		errorbox(ctr[TR_DISK_TOO_SMALL]);
		goto EXIT;
	}

	fprintf(flog, "Destination drive: %s\n", destination->path);
	fprintf(flog, "  boot: %s (%lluMB)\n", destination->part_boot, BYTES2MB(destination->size_boot));
	fprintf(flog, "  swap: %s (%lluMB)\n", destination->part_swap, BYTES2MB(destination->size_swap));
	fprintf(flog, "  root: %s (%lluMB)\n", destination->part_root, BYTES2MB(destination->size_root));
	fprintf(flog, "  data: %s (%lluMB)\n", destination->part_data, BYTES2MB(destination->size_data));

	// Warn the user if there is not enough space to create a swap partition
	if (!unattended && !*destination->part_swap) {
		rc = newtWinChoice(title, ctr[TR_OK], ctr[TR_CANCEL], ctr[TR_CONTINUE_NO_SWAP]);

		if (rc != 1)
			goto EXIT;
	}

	// Filesystem selection
	if (!unattended) {
		struct filesystems {
			int fstype;
			const char* description;
		} filesystems[] = {
			{ HW_FS_EXT4,            ctr[TR_EXT4FS] },
			{ HW_FS_EXT4_WO_JOURNAL, ctr[TR_EXT4FS_WO_JOURNAL] },
			{ HW_FS_REISERFS,        ctr[TR_REISERFS] },
			{ 0, NULL },
		};
		unsigned int num_filesystems = sizeof(filesystems) / sizeof(*filesystems);

		char* fs_names[num_filesystems];
		int fs_choice = 0;
		for (unsigned int i = 0; i < num_filesystems; i++) {
			if (HW_FS_DEFAULT == filesystems[i].fstype)
				fs_choice = i;

			fs_names[i] = filesystems[i].description;
		}

		rc = newtWinMenu(ctr[TR_CHOOSE_FILESYSTEM], ctr[TR_CHOOSE_FILESYSTEM],
			50, 5, 5, 6, fs_names, &fs_choice, ctr[TR_OK], ctr[TR_CANCEL], NULL);

		if (rc == 0)
			destination->filesystem = filesystems[fs_choice].fstype;

		else
			goto EXIT;
	}

	// Execute the partitioning...
	statuswindow(60, 4, title, ctr[TR_PARTITIONING_DISK]);

	rc = hw_create_partitions(destination);
	if (rc) {
		errorbox(ctr[TR_UNABLE_TO_PARTITION]);
		goto EXIT;
	}

	newtPopWindow();

	// Execute the formatting...
	statuswindow(60, 4, title, ctr[TR_CREATING_FILESYSTEMS]);

	rc = hw_create_filesystems(destination);
	if (rc) {
		errorbox(ctr[TR_UNABLE_TO_CREATE_FILESYSTEMS]);
		goto EXIT;
	}

	rc = hw_mount_filesystems(destination, DESTINATION_MOUNT_PATH);
	if (rc) {
		errorbox(ctr[TR_UNABLE_TO_MOUNT_FILESYSTEMS]);
		goto EXIT;
	}

	newtPopWindow();

	// Extract files...
	snprintf(commandstring, STRING_SIZE,
		"/bin/tar -C /harddisk  -xvf /cdrom/" SNAME "-" VERSION ".tlz --lzma 2>/dev/null");
	
	if (runcommandwithprogress(60, 4, title, commandstring, INST_FILECOUNT,
		ctr[TR_INSTALLING_FILES]))
	{
		errorbox(ctr[TR_UNABLE_TO_INSTALL_FILES]);
		goto EXIT;
	}
	
	/* Save language und local settings */
	write_lang_configs(shortlangname);

	/* Build cache lang file */
	snprintf(commandstring, STRING_SIZE, "/usr/sbin/chroot /harddisk /usr/bin/perl -e \"require '" CONFIG_ROOT "/lang.pl'; &Lang::BuildCacheLang\"");
	if (runcommandwithstatus(commandstring, ctr[TR_INSTALLING_LANG_CACHE]))
	{
		errorbox(ctr[TR_UNABLE_TO_INSTALL_LANG_CACHE]);
		goto EXIT;
	}

	/* Update /etc/fstab */
	snprintf(commandstring, STRING_SIZE, "/bin/sed -i -e \"s#DEVICE1#UUID=$(/sbin/blkid %s -sUUID | /usr/bin/cut -d'\"' -f2)#g\" /harddisk/etc/fstab", destination->part_boot);
	system(commandstring);
	snprintf(commandstring, STRING_SIZE, "/bin/sed -i -e \"s#DEVICE2#UUID=$(/sbin/blkid %s -sUUID | /usr/bin/cut -d'\"' -f2)#g\" /harddisk/etc/fstab", destination->part_swap);
	system(commandstring);
	snprintf(commandstring, STRING_SIZE, "/bin/sed -i -e \"s#DEVICE3#UUID=$(/sbin/blkid %s -sUUID | /usr/bin/cut -d'\"' -f2)#g\" /harddisk/etc/fstab", destination->part_root);
	system(commandstring);
	snprintf(commandstring, STRING_SIZE, "/bin/sed -i -e \"s#DEVICE4#UUID=$(/sbin/blkid %s -sUUID | /usr/bin/cut -d'\"' -f2)#g\" /harddisk/etc/fstab", destination->part_data);
	system(commandstring);

	switch (destination->filesystem) {
		case HW_FS_REISERFS:
			replace("/harddisk/etc/fstab", "FSTYPE", "reiserfs");
			replace("/harddisk/boot/grub/grub.conf", "MOUNT", "ro");
			break;

		case HW_FS_EXT4:
		case HW_FS_EXT4_WO_JOURNAL:
			replace("/harddisk/etc/fstab", "FSTYPE", "ext4");
			replace("/harddisk/boot/grub/grub.conf", "MOUNT", "ro");
			break;

		default:
			assert(0);
	}

	replace("/harddisk/boot/grub/grub.conf", "KVER", KERNEL_VERSION);

	snprintf(commandstring, STRING_SIZE, "/bin/sed -i -e \"s#root=ROOT#root=UUID=$(/sbin/blkid %s -sUUID | /usr/bin/cut -d'\"' -f2)#g\" /harddisk/boot/grub/grub.conf", destination->part_root);
	system(commandstring);

	mysystem("ln -s grub.conf /harddisk/boot/grub/menu.lst");

	system("/bin/sed -e 's#/harddisk#/#g' -e 's#//#/#g'  < /proc/mounts > /harddisk/etc/mtab");

	/*
	 * Generate device.map to help grub finding the device to install itself on.
	 */
	FILE *f = NULL;
	if (f = fopen("/harddisk/boot/grub/device.map", "w")) {
		fprintf(f, "(hd0) %s\n", destination->path);
		fclose(f);
	}

	snprintf(commandstring, STRING_SIZE, 
		 "/usr/sbin/chroot /harddisk /usr/sbin/grub-install --no-floppy %s", destination->path);
	if (runcommandwithstatus(commandstring, ctr[TR_INSTALLING_GRUB])) {
		errorbox(ctr[TR_UNABLE_TO_INSTALL_GRUB]);
		goto EXIT;
	}

	/* Serial console ? */
	if (serialconsole) {
		/* grub */
		replace("/harddisk/boot/grub/grub.conf", "splashimage", "#splashimage");
		replace("/harddisk/boot/grub/grub.conf", "#serial", "serial");
		replace("/harddisk/boot/grub/grub.conf", "#terminal", "terminal");
		replace("/harddisk/boot/grub/grub.conf", " panic=10 ", " console=ttyS0,115200n8 panic=10 ");

		/*inittab*/
		replace("/harddisk/etc/inittab", "1:2345:respawn:", "#1:2345:respawn:");
		replace("/harddisk/etc/inittab", "2:2345:respawn:", "#2:2345:respawn:");
		replace("/harddisk/etc/inittab", "3:2345:respawn:", "#3:2345:respawn:");
		replace("/harddisk/etc/inittab", "4:2345:respawn:", "#4:2345:respawn:");
		replace("/harddisk/etc/inittab", "5:2345:respawn:", "#5:2345:respawn:");
		replace("/harddisk/etc/inittab", "6:2345:respawn:", "#6:2345:respawn:");
		replace("/harddisk/etc/inittab", "#7:2345:respawn:", "7:2345:respawn:");
	}

	/* Set marker that the user has already accepted the gpl */
	mysystem("/usr/bin/touch /harddisk/var/ipfire/main/gpl_accepted");

	/* Copy restore file from cdrom */
	if (unattended && (strlen(restore_file) > 0)) {
		fprintf(flog, "unattended: Copy restore file\n");
		snprintf(commandstring, STRING_SIZE, 
			"cp /cdrom/%s /harddisk/var/ipfire/backup", restore_file);
		mysystem(commandstring);
	}
	
	mysystem("umount /cdrom");
	snprintf(commandstring, STRING_SIZE, "/usr/bin/eject /dev/%s", sourcedrive);
	mysystem(commandstring);

	if (!unattended) {
		sprintf(message, ctr[TR_CONGRATULATIONS_LONG],
				NAME, SNAME, NAME);
		newtWinMessage(ctr[TR_CONGRATULATIONS], ctr[TR_PRESS_OK_TO_REBOOT], message);
	}

	allok = 1;

EXIT:
	fprintf(flog, "Install program ended.\n");	

	if (!(allok))
		newtWinMessage(title, ctr[TR_OK], ctr[TR_PRESS_OK_TO_REBOOT]);	
	
	freekeyvalues(ethernetkv);

	if (allok) {
		fflush(flog);
		fclose(flog);
	}

	newtFinished();

	// Free resources
	free(sourcedrive);

	if (destination) {
		hw_umount_filesystems(destination, DESTINATION_MOUNT_PATH);
		free(destination);
	}

	if (selected_disks)
		hw_free_disks(selected_disks);

	hw_free(hw);

	fcloseall();

	if (!(allok))
		system("/etc/halt");

	return 0;
}
