/* SmoothWall install program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Contains main entry point, and misc functions.6
 * 
 */

#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>

#include "hw.h"
#include "install.h"

// Translation
#include <libintl.h>
#define _(x) dgettext("installer", x)

#define INST_FILECOUNT 21000
#define UNATTENDED_CONF "/cdrom/boot/unattended.conf"
#define LICENSE_FILE	"/cdrom/COPYING"

FILE *flog = NULL;
char *mylog;

extern char url[STRING_SIZE];

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

	newtComponent btn_okay   = newtButton((width - 18) / 3, height - 4, _("OK"));
	newtComponent btn_cancel = newtButton((width - 18) / 3 * 2 + 9, height - 4, _("Cancel"));
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

static int newtLicenseBox(const char* title, const char* text, int width, int height) {
	int ret = 1;

	newtCenteredWindow(width, height, title);

	newtComponent form = newtForm(NULL, NULL, 0);

	newtComponent textbox = newtTextbox(1, 1, width - 2, height - 7,
		NEWT_FLAG_WRAP|NEWT_FLAG_SCROLL);
	newtTextboxSetText(textbox, text);
	newtFormAddComponent(form, textbox);

	char choice;
	newtComponent checkbox = newtCheckbox(3, height - 3, _("I accept this license"),
		' ', " *", &choice);

	newtComponent btn = newtButton(width - 15, height - 4, _("OK"));

	newtFormAddComponents(form, checkbox, btn, NULL);

	newtComponent answer = newtRunForm(form);
	if (answer == btn && choice == '*')
		ret = 0;

	newtFormDestroy(form);
	newtPopWindow();

	return ret;
}

int write_lang_configs(const char *lang) {
	struct keyvalue *kv = initkeyvalues();

	/* default stuff for main/settings. */
	replacekeyvalue(kv, "LANGUAGE", lang);
	replacekeyvalue(kv, "HOSTNAME", SNAME);
	replacekeyvalue(kv, "THEME", "ipfire");
	writekeyvalues(kv, "/harddisk" CONFIG_ROOT "/main/settings");
	freekeyvalues(kv);

	return 1;
}

static char* get_system_release() {
	char system_release[STRING_SIZE] = "\0";

	FILE* f = fopen("/etc/system-release", "r");
	if (f) {
		fgets(system_release, sizeof(system_release), f);
		fclose(f);
	}

	return strdup(system_release);
}

static char* center_string(const char* str, int width) {
	unsigned int str_len = strlen(str);

	unsigned int indent_length = (width - str_len) / 2;
	char indent[indent_length + 1];

	for (unsigned int i = 0; i < indent_length; i++) {
		indent[i] = ' ';
	}
	indent[indent_length] = '\0';

	char* string = NULL;
	if (asprintf(&string, "%s%s", indent, str) < 0)
		return NULL;

	return string;
}

#define DEFAULT_LANG "English"
#define NUM_LANGS 8

static struct lang {
	const char* code;
	char* name;
} languages[NUM_LANGS + 1] = {
	{ "nl", "Dutch (Nederlands)" },
	{ "en", "English" },
	{ "fr", "French (Français)" },
	{ "de", "German (Deutsch)" },
	{ "pl", "Polish (Polski)" },
	{ "ru", "Russian (Русский)" },
	{ "es", "Spanish (Español)" },
	{ "tr", "Turkish (Türkçe)" },
	{ NULL, NULL },
};

int main(int argc, char *argv[]) {
	struct hw* hw = hw_init();

	// Read /etc/system-release
	char* system_release = get_system_release();

	char discl_msg[40000] =	"Disclaimer\n";

	char* sourcedrive = NULL;
	int rc = 0;
	char commandstring[STRING_SIZE];
	int choice;
	char shortlangname[10];
	char message[STRING_SIZE];
	char title[STRING_SIZE];
	int allok = 0;
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

	// Determine the size of the screen
	int screen_cols = 0;
	int screen_rows = 0;

	newtGetScreenSize(&screen_cols, &screen_rows);

	// Draw title
	char* roottext = center_string(system_release, screen_cols);
	newtDrawRootText(0, 0, roottext);

	sprintf (title, "%s %s - %s", NAME, VERSION, SLOGAN);

	if (! (cmdfile = fopen("/proc/cmdline", "r")))
	{
		fprintf(flog, "Couldn't open commandline: /proc/cmdline\n");
	} else {
		fgets(line, STRING_SIZE, cmdfile);
		
		// check if we have to make an unattended install
		if (strstr (line, "unattended") != NULL) {
		    unattended = 1;
		    runcommandwithstatus("/bin/sleep 10", title, "WARNING: Unattended installation will start in 10 seconds...");
		}		
		// check if we have to patch for serial console
		if (strstr (line, "console=ttyS0") != NULL) {
		    serialconsole = 1;
		}
	}

	// Load common modules
	mysystem("/sbin/modprobe vfat"); // USB key
	hw_stop_all_raid_arrays();

	if (!unattended) {
		// Language selection
		char* langnames[NUM_LANGS + 1];

		for (unsigned int i = 0; i < NUM_LANGS; i++) {
			if (strcmp(languages[i].name, DEFAULT_LANG) == 0)
				choice = i;

			langnames[i] = languages[i].name;
		}
		langnames[NUM_LANGS] = NULL;

	    rc = newtWinMenu(_("Language selection"), _("Select the language you wish to use for the installation."),
			50, 5, 5, 8, langnames, &choice, _("OK"), NULL);

		assert(choice <= NUM_LANGS);

		fprintf(flog, "Selected language: %s (%s)\n", languages[choice].name, languages[choice].code);
		setlocale(LC_ALL, languages[choice].code);
	}

	char* helpline = center_string(_("<Tab>/<Alt-Tab> between elements | <Space> selects | <F12> next screen"), screen_cols);
	newtPushHelpLine(helpline);

	if (!unattended) {
		snprintf(message, sizeof(message),
			_("Welcome to the %s installation program. "
			"Selecting Cancel on any of the following screens will reboot the computer."), NAME);
		newtWinMessage(title, _("Start installation"), message);
	}

	/* Search for a source drive that holds the right
	 * version of the image we are going to install. */
	sourcedrive = hw_find_source_medium(hw);

	fprintf(flog, "Source drive: %s\n", sourcedrive);
	if (!sourcedrive) {
		newtWinMessage(title, _("OK"), _("No local source media found. Starting download."));
		runcommandwithstatus("/bin/downloadsource.sh", title, _("Downloading installation image ..."));
		if ((handle = fopen("/tmp/source_device", "r")) == NULL) {
			errorbox(_("Download error"));
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

			if (newtLicenseBox(title, discl_msg, 75, 20)) {
				errorbox(_("License not accepted!"));

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
			errorbox(_("No hard disk found."));
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
				rc = newtChecklist(_("Disk Selection"),
					_("Select the disk(s) you want to install IPFire on. "
					"First those will be partitioned, and then the partitions will have a filesystem put on them.\n\n"
					"ALL DATA ON THE DISK WILL BE DESTROYED."),
					50, 20, num_disks, disk_names, disk_selection);

				// Error
				if (rc < 0) {
					goto EXIT;

				// Nothing has been selected
				} else if (rc == 0) {
					errorbox(_("No disk has been selected.\n\n"
						"Please select one or more disks you want to install IPFire on."));

				} else {
					selected_disks = hw_select_disks(disks, disk_selection);
				}
			}
		}

		num_selected_disks = hw_count_disks(selected_disks);

		if (num_selected_disks == 1) {
			snprintf(message, sizeof(message),
				_("The installation program will now prepare the chosen harddisk:\n\n  %s\n\n"
				"Do you agree to continue?"), (*selected_disks)->description);
			rc = newtWinOkCancel(_("Disk Setup"), message, 50, 10,
				_("Delete all data"), _("Cancel"));

			if (rc == 0)
				break;

		} else if (num_selected_disks == 2) {
			snprintf(message, sizeof(message),
				_("The installation program will now set up a RAID configuration on the selected harddisks:\n\n  %s\n  %s\n\n"
				"Do you agree to continue?"), (*selected_disks)->description, (*selected_disks + 1)->description);
			rc = newtWinOkCancel(_("RAID Setup"), message, 50, 14,
				_("Delete all data"), _("Cancel"));

			if (rc == 0) {
				part_type = HW_PART_TYPE_RAID1;

				break;
			}

		// Currently not supported
		} else {
			errorbox(_("You disk configuration is currently not supported."));
		}

		if (selected_disks) {
			hw_free_disks(selected_disks);
			selected_disks = NULL;
		}
	}

	hw_free_disks(disks);

	struct hw_destination* destination = hw_make_destination(part_type, selected_disks);

	if (!destination) {
		errorbox(_("Your harddisk is too small."));
		goto EXIT;
	}

	fprintf(flog, "Destination drive: %s\n", destination->path);
	fprintf(flog, "  bootldr: %s (%lluMB)\n", destination->part_bootldr, BYTES2MB(destination->size_bootldr));
	fprintf(flog, "  boot   : %s (%lluMB)\n", destination->part_boot, BYTES2MB(destination->size_boot));
	fprintf(flog, "  swap   : %s (%lluMB)\n", destination->part_swap, BYTES2MB(destination->size_swap));
	fprintf(flog, "  root   : %s (%lluMB)\n", destination->part_root, BYTES2MB(destination->size_root));
	fprintf(flog, "  data   : %s (%lluMB)\n", destination->part_data, BYTES2MB(destination->size_data));

	// Warn the user if there is not enough space to create a swap partition
	if (!unattended && !*destination->part_swap) {
		rc = newtWinChoice(title, _("OK"), _("Cancel"),
			_("Your harddisk is very small, but you can continue with an very small swap. (Use with caution)."));

		if (rc != 1)
			goto EXIT;
	}

	// Filesystem selection
	if (!unattended) {
		struct filesystems {
			int fstype;
			const char* description;
		} filesystems[] = {
			{ HW_FS_EXT4,            _("ext4 Filesystem") },
			{ HW_FS_EXT4_WO_JOURNAL, _("ext4 Filesystem without journal") },
			{ HW_FS_XFS,             _("XFS Filesystem") },
			{ HW_FS_REISERFS,        _("ReiserFS Filesystem") },
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

		rc = newtWinMenu(_("Filesystem Selection"), _("Please choose your filesystem:"),
			50, 5, 5, 6, fs_names, &fs_choice, _("OK"), _("Cancel"), NULL);

		if (rc != 1)
			goto EXIT;

		destination->filesystem = filesystems[fs_choice].fstype;
	}

	// Setting up RAID if needed.
	if (destination->is_raid) {
		statuswindow(60, 4, title, _("Building RAID..."));

		rc = hw_setup_raid(destination);
		if (rc) {
			errorbox(_("Unable to build the RAID."));
			goto EXIT;
		}

		newtPopWindow();
	}

	// Execute the partitioning...
	statuswindow(60, 4, title, _("Partitioning disk..."));

	rc = hw_create_partitions(destination);
	if (rc) {
		errorbox(_("Unable to partition the disk."));
		goto EXIT;
	}

	newtPopWindow();

	// Execute the formatting...
	statuswindow(60, 4, title, _("Creating filesystems..."));

	rc = hw_create_filesystems(destination);
	if (rc) {
		errorbox(_("Unable to create filesystems."));
		goto EXIT;
	}

	rc = hw_mount_filesystems(destination, DESTINATION_MOUNT_PATH);
	if (rc) {
		errorbox(_("Unable to mount filesystems."));
		goto EXIT;
	}

	newtPopWindow();

	// Extract files...
	snprintf(commandstring, STRING_SIZE,
		"/bin/tar -C /harddisk  -xvf /cdrom/distro.img --lzma 2>/dev/null");

	if (runcommandwithprogress(60, 4, title, commandstring, INST_FILECOUNT,
			_("Installing the system..."))) {
		errorbox(_("Unable to install the system."));
		goto EXIT;
	}

	// Write fstab
	rc = hw_write_fstab(destination);
	if (rc) {
		fprintf(flog, "Could not write /etc/fstab\n");
		goto EXIT;
	}

	/* Save language und local settings */
	write_lang_configs(shortlangname);

	/* Build cache lang file */
	snprintf(commandstring, STRING_SIZE, "/usr/sbin/chroot /harddisk /usr/bin/perl -e \"require '" CONFIG_ROOT "/lang.pl'; &Lang::BuildCacheLang\"");
	if (runcommandwithstatus(commandstring, title, _("Installing the language cache..."))) {
		errorbox(_("Unable to install the language cache."));
		goto EXIT;
	}

	// Installing bootloader...
	statuswindow(60, 4, title, _("Installing the bootloader..."));

	rc = hw_install_bootloader(destination);
	if (rc) {
		errorbox(_("Unable to install the bootloader."));
		goto EXIT;
	}

	newtPopWindow();

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

	// Umount source drive and eject
	hw_umount(SOURCE_MOUNT_PATH);

	snprintf(commandstring, STRING_SIZE, "/usr/bin/eject %s", sourcedrive);
	mysystem(commandstring);

	if (!unattended) {
		snprintf(message, sizeof(message), _("%s was successfully installed. "
			"Please remove any installation mediums from this system. "
			"Setup will now run where you may configure networking and the system passwords. "
			"After Setup has been completed, you should point your web browser at https://%s:444 "
			"(or whatever you name your %s), and configure dialup networking (if required) and "
			"remote access."), NAME, SNAME, NAME);
		newtWinMessage(_("Congratulations!"), _("Reboot"), message);
	}

	allok = 1;

EXIT:
	fprintf(flog, "Install program ended.\n");	

	if (!(allok))
		newtWinMessage(title, _("OK"), _("Press Ok to reboot."));

	if (allok) {
		fflush(flog);
		fclose(flog);
	}

	newtFinished();

	// Free resources
	free(system_release);
	free(roottext);
	free(helpline);

	free(sourcedrive);

	if (destination) {
		hw_sync();

		hw_umount_filesystems(destination, DESTINATION_MOUNT_PATH);
		free(destination);
	}

	hw_stop_all_raid_arrays();

	if (selected_disks)
		hw_free_disks(selected_disks);

	hw_free(hw);

	fcloseall();

	if (allok == 1)
		return 0;

	return 1;
}
