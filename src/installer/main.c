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
#include <libsmooth.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>

#include "hw.h"

// Translation
#include <libintl.h>
#define _(x) dgettext("installer", x)

#define INST_FILECOUNT 28000
#define LICENSE_FILE	"/cdrom/COPYING"
#define SOURCE_TEMPFILE "/tmp/downloads/image.iso"

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

	unsigned int btn_width_ok = strlen(btn_txt_ok);
	unsigned int btn_width_cancel = strlen(btn_txt_cancel);

	// Maybe make the box wider to fix both buttons inside
	unsigned int min_width = btn_width_ok + btn_width_cancel + 5;
	if (width < min_width)
		width = min_width;

	unsigned int btn_pos_ok = (width / 3) - (btn_width_ok / 2) - 1;
	unsigned int btn_pos_cancel = (width * 2 / 3) - (btn_width_cancel / 2) - 1;

	// Move buttons a bit if they overlap
	while ((btn_pos_ok + btn_width_ok + 5) > btn_pos_cancel) {
		// Move the cancel button to the right if there is enough space left
		if ((btn_pos_cancel + btn_width_cancel + 2) < width) {
			++btn_pos_cancel;
			continue;
		}

		// Move the OK button to the left if possible
		if (btn_pos_ok > 1) {
			--btn_pos_ok;
			continue;
		}

		// If they still overlap, we cannot fix the situtation
		// and break. Should actually never get here, because we
		// adjust the width of the window earlier.
		break;
	}

	newtCenteredWindow(width, height, title);

	newtComponent form = newtForm(NULL, NULL, 0);

	newtComponent textbox = newtTextbox(1, 1, width - 2, height - 6, NEWT_FLAG_WRAP);
	newtTextboxSetText(textbox, message);
	newtFormAddComponent(form, textbox);

	newtComponent btn_ok = newtButton(btn_pos_ok, height - 4, btn_txt_ok);
	newtComponent btn_cancel = newtButton(btn_pos_cancel, height - 4, btn_txt_cancel);

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

int write_lang_configs(char* lang) {
	struct keyvalue *kv = initkeyvalues();

	/* default stuff for main/settings. */
	replacekeyvalue(kv, "LANGUAGE", lang);
	replacekeyvalue(kv, "HOSTNAME", DISTRO_SNAME);
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
	if (!str)
		return NULL;

	char* string = NULL;
	unsigned int str_len = strlen(str);

	if (str_len == width) {
		string = strdup(str);

	} else if (str_len > width) {
		string = strdup(str);
		string[width - 1] = '\0';

	} else {
		unsigned int indent_length = (width - str_len) / 2;
		char indent[indent_length + 1];

		for (unsigned int i = 0; i < indent_length; i++) {
			indent[i] = ' ';
		}
		indent[indent_length] = '\0';

		if (asprintf(&string, "%s%s", indent, str) < 0)
			return NULL;
	}

	return string;
}

#define DEFAULT_LANG "en.utf8"
#define NUM_LANGS 13

static struct lang {
	const char* code;
	char* name;
} languages[NUM_LANGS + 1] = {
	{ "fa.utf8",    "فارسی (Persian)" },
	{ "da.utf8",    "Dansk (Danish)" },
	{ "es.utf8",    "Español (Spanish)" },
	{ "en.utf8",    "English" },
	{ "fr.utf8",    "Français (French)" },
	{ "hr.utf8",    "Hrvatski (Croatian)" },
	{ "it.utf8",    "Italiano (Italian)" },
	{ "de.utf8",    "Deutsch (German)" },
	{ "nl.utf8",    "Nederlands (Dutch)" },
	{ "pl.utf8",    "Polski (Polish)" },
	{ "pt.utf8",    "Portuguese (Brasil)" },
	{ "ru.utf8",    "Русский (Russian)" },
	{ "tr.utf8",    "Türkçe (Turkish)" },
	{ NULL, NULL },
};

static struct config {
	int unattended;
	int serial_console;
	int novga;
	int require_networking;
	int perform_download;
	int disable_swap;
	char download_url[STRING_SIZE];
	char postinstall[STRING_SIZE];
	char* language;
} config = {
	.unattended = 0,
	.serial_console = 0,
	.novga = 0,
	.require_networking = 0,
	.perform_download = 0,
	.disable_swap = 0,
	.download_url = DOWNLOAD_URL,
	.postinstall = "\0",
	.language = DEFAULT_LANG,
};

static void parse_command_line(FILE* flog, struct config* c) {
	char buffer[STRING_SIZE];
	char cmdline[STRING_SIZE];

	FILE* f = fopen("/proc/cmdline", "r");
	if (!f) {
		fprintf(flog, "Could not open /proc/cmdline: %m");
		return;
	}

	int r = fread(&cmdline, 1, sizeof(cmdline) - 1, f);
	if (r > 0) {
		// Remove the trailing newline
		if (cmdline[r-1] == '\n')
			cmdline[r-1] = '\0';

		char* token = strtok(cmdline, " ");
		while (token) {
			strncpy(buffer, token, sizeof(buffer));
			char* val = buffer;
			char* key = strsep(&val, "=");

			// serial console
			if ((strcmp(key, "console") == 0) && (strncmp(val, "ttyS", 4) == 0))
				c->serial_console = 1;

			// novga
			else if (strcmp(key, "novga") == 0)
				c->novga = 1;

			// enable networking?
			else if (strcmp(token, "installer.net") == 0)
				c->require_networking = 1;

			// unattended mode
			else if (strcmp(token, "installer.unattended") == 0)
				c->unattended = 1;

			// disable swap
			else if (strcmp(token, "installer.disable-swap") == 0)
				c->disable_swap = 1;

			// download url
			else if (strcmp(key, "installer.download-url") == 0) {
				strncpy(c->download_url, val, sizeof(c->download_url));
				c->perform_download = 1;

				// Require networking for the download
				c->require_networking = 1;

			// postinstall script
			} else if (strcmp(key, "installer.postinstall") == 0) {
				strncpy(c->postinstall, val, sizeof(c->postinstall));

				// Require networking for the download
				c->require_networking = 1;
			}

			token = strtok(NULL, " ");
		}
	}

	fclose(f);
}

int main(int argc, char *argv[]) {
	struct hw* hw = hw_init();
	const char* logfile = NULL;

	// Read /etc/system-release
	char* system_release = get_system_release();

	char discl_msg[40000] =	"Disclaimer\n";

	char* sourcedrive = NULL;
	int rc = 0;
	char commandstring[STRING_SIZE];
	int choice;
	char message[STRING_SIZE];
	char title[STRING_SIZE];
	int allok = 0;
	FILE *copying;

	setlocale(LC_ALL, "");
	sethostname(DISTRO_SNAME, 10);

	/* Log file/terminal stuff. */
	FILE* flog = NULL;
	if (argc >= 2) {
		logfile = argv[1];

		if (!(flog = fopen(logfile, "w+")))
			return 0;
	} else {
		return 0;
	}

	fprintf(flog, "Install program started.\n");
	if (hw->efi)
		fprintf(flog, "EFI mode enabled\n");

	newtInit();
	newtCls();

	// Determine the size of the screen
	int screen_cols = 0;
	int screen_rows = 0;

	newtGetScreenSize(&screen_cols, &screen_rows);

	// Draw title
	char* roottext = center_string(system_release, screen_cols);
	if (roottext)
		newtDrawRootText(0, 0, roottext);

	snprintf(title, sizeof(title), "%s - %s", DISTRO_NAME, DISTRO_SLOGAN);

	// Parse parameters from the kernel command line
	parse_command_line(flog, &config);

	if (config.unattended) {
		splashWindow(title, _("Warning: Unattended installation will start in 10 seconds..."), 10);
	}

	// Load common modules
	mysystem(logfile, "/sbin/modprobe vfat");  // USB key
	mysystem(logfile, "/sbin/modprobe ntfs3"); // USB key
	hw_stop_all_raid_arrays(logfile);

	if (!config.unattended) {
		// Language selection
		char* langnames[NUM_LANGS + 1];

		for (unsigned int i = 0; i < NUM_LANGS; i++) {
			if (strcmp(languages[i].code, DEFAULT_LANG) == 0)
				choice = i;

			langnames[i] = languages[i].name;
		}
		langnames[NUM_LANGS] = NULL;

		rc = newtWinMenu(_("Language selection"), _("Select the language you wish to use for the installation."),
			50, 5, 5, 8, langnames, &choice, _("OK"), NULL);

		assert(choice <= NUM_LANGS);

		fprintf(flog, "Selected language: %s (%s)\n", languages[choice].name, languages[choice].code);
		config.language = languages[choice].code;

		setlocale(LC_ALL, config.language);
		setenv("LANGUAGE", config.language, 1);
	}

	// Set helpline
	char* helpline = NULL;
	if (config.unattended)
		helpline = center_string(_("Unattended mode"), screen_cols);
	else
		helpline = center_string(_("<Tab>/<Alt-Tab> between elements | <Space> selects | <F12> next screen"), screen_cols);

	if (helpline)
		newtPushHelpLine(helpline);

	if (!config.unattended) {
		snprintf(message, sizeof(message),
			_("Welcome to the %s installation program.\n\n"
			"Selecting Cancel on any of the following screens will reboot the computer."), DISTRO_NAME);
		newtWinMessage(title, _("Start installation"), message);
	}

	/* Search for a source drive that holds the right
	 * version of the image we are going to install. */
	if (!config.perform_download) {
		sourcedrive = hw_find_source_medium(hw);
		fprintf(flog, "Source drive: %s\n", sourcedrive);
	}

	/* If we could not find a source drive, we will try
	 * downloading the install image */
	if (!sourcedrive)
		config.perform_download = 1;

	if (config.perform_download) {
		if (!config.unattended) {
			// Show the right message to the user
			char reason[STRING_SIZE];
			if (config.perform_download) {
				snprintf(reason, sizeof(reason),
					_("The installer will now try downloading the installation image."));
			} else {
				snprintf(reason, sizeof(reason),
					_("No source drive could be found.\n\n"
					"You can try downloading the required installation image."));
			}
			snprintf(message, sizeof(message), "%s %s", reason,
				_("Please make sure to connect your machine to a network and "
                                "the installer will try connect to acquire an IP address."));

			rc = newtWinOkCancel(title, message, 55, 12,
				_("Download installation image"), _("Cancel"));

			if (rc != 0)
				goto EXIT;
		}

		// Make sure that we enable networking before download
		config.require_networking = 1;
	}

	// Try starting the networking if we require it
	if (config.require_networking) {
		while (1) {
			statuswindow(60, 4, title, _("Trying to start networking (DHCP)..."));

			rc = hw_start_networking(logfile);
			newtPopWindow();

			// Networking was successfully started
			if (rc == 0) {
				break;

			// An error happened, ask the user what to do
			} else {
				rc = newtWinOkCancel(title, _("Networking could not be started "
					"but is required to go on with the installation.\n\n"
					"Please connect your machine to a network with a "
					"DHCP server and retry."), 50, 10, _("Retry"), _("Cancel"));

				if (rc)
					goto EXIT;
			}
		}

		// Download the image if required
		if (config.perform_download) {
			fprintf(flog, "Download URL: %s\n", config.download_url);
			snprintf(commandstring, sizeof(commandstring), "/usr/bin/downloadsource.sh %s %s",
				SOURCE_TEMPFILE, config.download_url);

			while (!sourcedrive) {
				rc = runcommandwithstatus(commandstring, title, _("Downloading installation image..."), logfile);

				FILE* f = fopen(SOURCE_TEMPFILE, "r");
				if (f) {
					sourcedrive = strdup(SOURCE_TEMPFILE);
					fclose(f);
				} else {
					char reason[STRING_SIZE] = "-";
					if (rc == 2)
						snprintf(reason, sizeof(STRING_SIZE), _("MD5 checksum mismatch"));

					snprintf(message, sizeof(message),
						_("The installation image could not be downloaded.\n  Reason: %s\n\n%s"),
						reason, config.download_url);

					rc = newtWinOkCancel(title, message, 75, 12, _("Retry"), _("Cancel"));
					if (rc)
						goto EXIT;
				}
			}
		}
	}

	assert(sourcedrive);

	int r = hw_mount(sourcedrive, SOURCE_MOUNT_PATH, "iso9660", MS_RDONLY);
	if (r) r = hw_mount(sourcedrive, SOURCE_MOUNT_PATH, "ntfs3", MS_RDONLY);
	if (r) r = hw_mount(sourcedrive, SOURCE_MOUNT_PATH, "vfat", MS_RDONLY);
	if (r)
		{
		snprintf(message, sizeof(message), _("Could not mount %s to %s:\n  %s\n"),
			sourcedrive, SOURCE_MOUNT_PATH, strerror(errno));
		errorbox(message);
		goto EXIT;
	}

	if (!config.unattended) {
		// Read the license file.
		if (!(copying = fopen(LICENSE_FILE, "r"))) {
			sprintf(discl_msg, "Could not open license file: %s\n", LICENSE_FILE);
			fprintf(flog, "%s", discl_msg);
		} else {
			fread(discl_msg, 1, 40000, copying);
			fclose(copying);

			if (newtLicenseBox(_("License Agreement"), discl_msg, 75, 20)) {
				errorbox(_("License not accepted!"));

				goto EXIT;
			}
		}
	}

	int part_type = HW_PART_TYPE_NORMAL;

	// Scan for disks to install on.
	struct hw_disk** disks = hw_find_disks(hw, sourcedrive);

	struct hw_disk** selected_disks = NULL;
	unsigned int num_selected_disks = 0;

	// Check how many disks have been found and what
	// we can do with them.
	unsigned int num_disks = hw_count_disks((const struct hw_disk**)disks);

	while (1) {
		// no harddisks found
		if (num_disks == 0) {
			errorbox(_("No hard disk found."));
			goto EXIT;

		// exactly one disk has been found
		// or if we are running in unattended mode, we will select
		// the first disk and go with that one
		} else if ((num_disks == 1) || (config.unattended && num_disks >= 1)) {
			selected_disks = hw_select_first_disk((const struct hw_disk**)disks);

		// more than one usable disk has been found and
		// the user needs to choose what to do with them
		} else {
			const char* disk_names[num_disks];
			int disk_selection[num_disks];

			for (unsigned int i = 0; i < num_disks; i++) {
				disk_names[i] = disks[i]->description;
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

		// Don't print the auto-selected harddisk setup in
		// unattended mode.
		if (config.unattended)
			break;

		num_selected_disks = hw_count_disks((const struct hw_disk**)selected_disks);

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
				"Do you agree to continue?"), selected_disks[0]->description, selected_disks[1]->description);
			rc = newtWinOkCancel(_("RAID Setup"), message, 50, 14,
				_("Delete all data"), _("Cancel"));

			if (rc == 0) {
				part_type = HW_PART_TYPE_RAID1;

				break;
			}

		// Currently not supported
		} else {
			errorbox(_("Your disk configuration is currently not supported."));
			fprintf(flog, "Num disks selected: %d\n", num_selected_disks);
		}

		if (selected_disks) {
			hw_free_disks(selected_disks);
			selected_disks = NULL;
		}
	}

	hw_free_disks(disks);

	struct hw_destination* destination = hw_make_destination(hw, part_type,
		selected_disks, config.disable_swap);

	if (!destination) {
		errorbox(_("Your harddisk is too small."));
		goto EXIT;
	}

	fprintf(flog, "Destination drive: %s\n", destination->path);
	fprintf(flog, "  bootldr: %s (%lluMB)\n", destination->part_bootldr, BYTES2MB(destination->size_bootldr));
	fprintf(flog, "  boot   : %s (%lluMB)\n", destination->part_boot, BYTES2MB(destination->size_boot));
	fprintf(flog, "  ESP    : %s (%lluMB)\n", destination->part_boot_efi, BYTES2MB(destination->size_boot_efi));
	fprintf(flog, "  swap   : %s (%lluMB)\n", destination->part_swap, BYTES2MB(destination->size_swap));
	fprintf(flog, "  root   : %s (%lluMB)\n", destination->part_root, BYTES2MB(destination->size_root));
	fprintf(flog, "Memory   : %lluMB\n", BYTES2MB(hw_memory()));

	// Warn the user if there is not enough space to create a swap partition
	if (!config.unattended) {
		if (!config.disable_swap && !*destination->part_swap) {
			rc = newtWinChoice(title, _("OK"), _("Cancel"),
				_("Your harddisk is very small, but you can continue without a swap partition."));

			if (rc != 1)
				goto EXIT;
		}
	}

	// Filesystem selection
	if (!config.unattended) {
		struct filesystems {
			int fstype;
			char* description;
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

		if (rc == 2)
			goto EXIT;

		destination->filesystem = filesystems[fs_choice].fstype;
	}

	// Setting up RAID if needed.
	if (destination->is_raid) {
		statuswindow(60, 4, title, _("Building RAID..."));

		rc = hw_setup_raid(destination, logfile);
		if (rc) {
			errorbox(_("Unable to build the RAID."));
			goto EXIT;
		}

		newtPopWindow();
	} else {
		// We will have to destroy all RAID setups that may have
		// been on the devices that we want to use now.
		hw_destroy_raid_superblocks(destination, logfile);
	}

	// Execute the partitioning...
	statuswindow(60, 4, title, _("Partitioning disk..."));

	rc = hw_create_partitions(destination, logfile);
	if (rc) {
		errorbox(_("Unable to partition the disk."));
		goto EXIT;
	}

	newtPopWindow();

	// Execute the formatting...
	statuswindow(60, 4, title, _("Creating filesystems..."));

	rc = hw_create_filesystems(destination, logfile);
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
		"/bin/tar --acls --xattrs --xattrs-include='*' -C /harddisk -xvf /cdrom/distro.img --zstd 2>/dev/null");

	if (runcommandwithprogress(60, 4, title, commandstring, INST_FILECOUNT,
			_("Installing the system..."), logfile)) {
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
	write_lang_configs(config.language);

	/* Build cache lang file */
	snprintf(commandstring, STRING_SIZE, "/usr/sbin/chroot /harddisk /usr/bin/perl -e \"require '" CONFIG_ROOT "/lang.pl'; &Lang::BuildCacheLang\"");
	if (runcommandwithstatus(commandstring, title, _("Installing the language cache..."), logfile)) {
		errorbox(_("Unable to install the language cache."));
		goto EXIT;
	}

	/* trigger udev to add disk-by-uuid entries */
	snprintf(commandstring, STRING_SIZE, "/usr/sbin/chroot /harddisk /sbin/udevadm trigger");
	if (runcommandwithstatus(commandstring, title, _("Trigger udev to redetect partitions..."), logfile)) {
		errorbox(_("Error triggering udev to redetect partitions."));
		goto EXIT;
	}

	// Installing bootloader...
	statuswindow(60, 4, title, _("Installing the bootloader..."));

	/* Serial console ? */
	if (config.serial_console) {
		/* grub */
		FILE* f = fopen(DESTINATION_MOUNT_PATH "/etc/default/grub", "a");
		if (!f) {
			errorbox(_("Unable to open /etc/default/grub for writing."));
			goto EXIT;
		}

		fprintf(f, "GRUB_TERMINAL=\"serial\"\n");
		fprintf(f, "GRUB_SERIAL_COMMAND=\"serial --unit=0 --speed=%d\"\n", SERIAL_BAUDRATE);
		fclose(f);

		replace(DESTINATION_MOUNT_PATH "/etc/default/grub", "panic=10", "panic=10 console=ttyS0,115200n8");
	}

	/* novga */
	if (config.novga) {
		/* grub */
		FILE* f = fopen(DESTINATION_MOUNT_PATH "/etc/default/grub", "a");
		if (!f) {
			errorbox(_("Unable to open /etc/default/grub for writing."));
			goto EXIT;
		}

		fprintf(f, "GRUB_GFXMODE=\"none\"\n");
		fclose(f);
	}

	rc = hw_install_bootloader(hw, destination, logfile);
	if (rc) {
		errorbox(_("Unable to install the bootloader."));
		goto EXIT;
	}

	newtPopWindow();

	/* Set marker that the user has already accepted the GPL if the license has been shown
	 * in the installation process. In unatteded mode, the user will be presented the
	 * license when he or she logs on to the web user interface for the first time. */
	if (!config.unattended)
		mysystem(logfile, "/usr/bin/touch /harddisk/var/ipfire/main/gpl_accepted");

	/* Copy restore file from cdrom */
	char* backup_file = hw_find_backup_file(logfile, SOURCE_MOUNT_PATH);
	if (backup_file) {
		rc = 0;
		if (!config.unattended) {
			rc = newtWinOkCancel(title, _("A backup file has been found on the installation image.\n\n"
				"Do you want to restore the backup?"), 50, 10, _("Yes"), _("No"));
		}

		if (rc == 0) {
			rc = hw_restore_backup(logfile, backup_file, DESTINATION_MOUNT_PATH);

			if (rc) {
				errorbox(_("An error occured when the backup file was restored."));
				goto EXIT;
			}
		}

		free(backup_file);
	}

	// Download and execute the postinstall script
	if (*config.postinstall) {
		snprintf(commandstring, sizeof(commandstring),
			"/usr/bin/execute-postinstall.sh %s %s", DESTINATION_MOUNT_PATH, config.postinstall);

		if (runcommandwithstatus(commandstring, title, _("Running post-install script..."), logfile)) {
			errorbox(_("Post-install script failed."));
			goto EXIT;
		}
	}

	// Umount the destination drive
	statuswindow(60, 4, title, _("Umounting filesystems..."));

	rc = hw_umount_filesystems(destination, DESTINATION_MOUNT_PATH);
	if (rc) {
		// Show an error message if filesystems could not be umounted properly
		snprintf(message, sizeof(message),
			_("Could not umount all filesystems successfully:\n\n  %s"), strerror(errno));
		errorbox(message);
		goto EXIT;
	}

	// Umount source drive and eject
	hw_umount(SOURCE_MOUNT_PATH, NULL);

	// Free downloaded ISO image
	if (strcmp(sourcedrive, SOURCE_TEMPFILE) == 0) {
		rc = unlink(sourcedrive);
		if (rc)
			fprintf(flog, "Could not free downloaded ISO image: %s\n", sourcedrive);

	// or eject real images
	} else {
		snprintf(commandstring, STRING_SIZE, "/usr/bin/eject %s", sourcedrive);
		mysystem(logfile, commandstring);
	}
	newtPopWindow();

	// Stop the RAID array if we are using RAID
	if (destination->is_raid)
		hw_stop_all_raid_arrays(logfile);

	// Show a short message that the installation went well and
	// wait a moment so that all disk caches get flushed.
	if (config.unattended) {
		splashWindow(title, _("Unattended installation has finished. The system will be shutting down in a moment..."), 5);

	} else {
		snprintf(message, sizeof(message), _(
			"%s was successfully installed!\n\n"
			"Please remove any installation mediums from this system and hit the reboot button. "
			"Once the system has restarted you will be asked to setup networking and system passwords. "
			"After that, you should point your web browser at https://%s:444 (or what ever you name "
			"your %s) for the web configuration console."), DISTRO_NAME, DISTRO_SNAME, DISTRO_NAME);
		newtWinMessage(_("Congratulations!"), _("Reboot"), message);
	}

	allok = 1;

EXIT:
	fprintf(flog, "Install program ended.\n");
	fflush(flog);
	fclose(flog);

	if (!allok)
		newtWinMessage(title, _("OK"), _("Setup has failed. Press Ok to reboot."));

	newtFinished();

	// Free resources
	if (system_release)
		free(system_release);

	if (roottext)
		free(roottext);

	if (helpline)
		free(helpline);

	if (sourcedrive)
		free(sourcedrive);

	if (destination)
		free(destination);

	hw_stop_all_raid_arrays(logfile);

	if (selected_disks)
		hw_free_disks(selected_disks);

	if (hw)
		hw_free(hw);

	fcloseall();

	if (allok == 1)
		return 0;

	return 1;
}
