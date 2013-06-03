
/* SmoothWall install program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Contains main entry point, and misc functions.6
 * 
 */

#include "install.h"
#define _GNU_SOURCE
 
#define INST_FILECOUNT 14400
#define UNATTENDED_CONF "/cdrom/boot/unattended.conf"
#define LICENSE_FILE	"/cdrom/COPYING"

#define EXT2 0
#define EXT3 1
#define EXT4 2
#define REISERFS 3

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

int main(int argc, char *argv[])
{

	char discl_msg[40000] =	"Disclaimer\n";

	char *langnames[] = { "Deutsch", "English", "Français", "Español", "Nederlands", "Polski", "Русский", "Türkçe", NULL };
	char *shortlangnames[] = { "de", "en", "fr", "es", "nl", "pl", "ru", "tr", NULL };
	char **langtrs[] = { de_tr, en_tr, fr_tr, es_tr, nl_tr, pl_tr, ru_tr, tr_tr, NULL };
	char hdletter;
	char harddrive[30], sourcedrive[5];	/* Device holder. */
	char harddrive_info[STRING_SIZE];	/* Additional infos about target */
	struct devparams hdparams, cdromparams; /* Params for CDROM and HD */
	int rc = 0;
	char commandstring[STRING_SIZE];
	char mkfscommand[STRING_SIZE];
	char *fstypes[] = { "ext2", "ext3", "ext4", "ReiserFS", NULL };
	int fstype = EXT4;
	int choice;
	int i;
	int found = 0;
	char shortlangname[10];
	char message[1000];
	char title[STRING_SIZE];
	int allok = 0;
	int allok_fastexit=0;
	int raid_disk = 0;
	struct keyvalue *ethernetkv = initkeyvalues();
	FILE *handle, *cmdfile, *copying;
	char line[STRING_SIZE];
	char string[STRING_SIZE];
	long memory = 0, disk = 0, free;
	long system_partition, boot_partition, root_partition, swap_file;
	int scsi_disk = 0;
	char *yesnoharddisk[3];	//	char *yesnoharddisk = { "NO", "YES", NULL };
		
	int unattended = 0;
	int serialconsole = 0;
	struct keyvalue *unattendedkv = initkeyvalues();
	int hardyn = 0;
	char restore_file[STRING_SIZE] = "";

	setlocale (LC_ALL, "");
	sethostname( SNAME , 10);

	memset(&hdparams, 0, sizeof(struct devparams));
	memset(&cdromparams, 0, sizeof(struct devparams));

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
	mysystem("/sbin/modprobe iso9660"); // CDROM
//	mysystem("/sbin/modprobe ext2"); // Boot patition
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

	mysystem("/bin/mountsource.sh");

	if ((handle = fopen("/tmp/source_device", "r")) == NULL) {
		newtWinMessage(title, ctr[TR_OK], ctr[TR_NO_LOCAL_SOURCE]);
		runcommandwithstatus("/bin/downloadsource.sh",ctr[TR_DOWNLOADING_ISO]);
		if ((handle = fopen("/tmp/source_device", "r")) == NULL) {
			errorbox(ctr[TR_DOWNLOAD_ERROR]);
			goto EXIT;
		}
	}

	fgets(sourcedrive, 5, handle);
	fprintf(flog, "Source drive: %s\n", sourcedrive);
	fclose(handle);

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

	i = 0;
	while (found == 0) {
		i++;
		fprintf(flog, "Harddisk scan pass %i\n", i);

		switch (mysystem("/bin/mountdest.sh") % 255) {
			case 0: // Found IDE disk
				scsi_disk = 0;
				raid_disk = 0;
				found = 1;
				break;
			case 1: // Found SCSI disk
				scsi_disk = 1;
				raid_disk = 0;
				found = 1;
				break;
			case 2: // Found RAID disk
				scsi_disk = 0;
				raid_disk= 1;
				found = 1;
				break;
			case 10: // No harddisk found
				errorbox(ctr[TR_NO_HARDDISK]);
				goto EXIT;
		}
	}

	if ((handle = fopen("/tmp/dest_device", "r")) == NULL) {
		errorbox(ctr[TR_NO_HARDDISK]);
		goto EXIT;
	}
	fgets(harddrive, 30, handle);
	fclose(handle);
	if ((handle = fopen("/tmp/dest_device_info", "r")) == NULL) {
		sprintf(harddrive_info, "%s", harddrive);
	}
	fgets(harddrive_info, 70, handle);
	fclose(handle);

			
	/* load unattended configuration */
	if (unattended) {
	    fprintf(flog, "unattended: Reading unattended.conf\n");

	    (void) readkeyvalues(unattendedkv, UNATTENDED_CONF);
	    findkey(unattendedkv, "RESTORE_FILE", restore_file);	    
	}
	
	/* Make the hdparms struct and print the contents.
	   With USB-KEY install and SCSI disk, while installing, the disk
	   is named 'sdb,sdc,...' (following keys)
	   On reboot, it will become 'sda'
	   To avoid many test, all names are built in the struct.
	*/
	sprintf(hdparams.devnode_disk, "/dev/%s", harddrive);
	/* Address the partition or raid partition (eg dev/sda or /dev/sdap1 */
	sprintf(hdparams.devnode_part, "/dev/%s%s", harddrive,raid_disk ? "p" : "");
	/* Now the names after the machine is booted. Only scsi is affected
	   and we only install on the first scsi disk. */

	fprintf(flog, "Destination drive: %s\n", hdparams.devnode_disk);
	
	sprintf(message, ctr[TR_PREPARE_HARDDISK], harddrive_info);
	if (unattended) {
	    hardyn = 1;
	} else {
		yesnoharddisk[0] = ctr[TR_NO];
		yesnoharddisk[1] = ctr[TR_YES];
		yesnoharddisk[2] = NULL;
	}

	while (! hardyn) {
		rc = newtWinMenu(title, message,
				 50, 5, 5, 6, yesnoharddisk,
				 &hardyn, ctr[TR_OK],
				 ctr[TR_CANCEL], NULL);
		if (rc == 2)
			goto EXIT;
	}
	if (rc == 2)
		goto EXIT;

	fstypes[0]=ctr[TR_EXT2FS_DESCR];
	fstypes[1]=ctr[TR_EXT3FS_DESCR];
	fstypes[2]=ctr[TR_EXT4FS_DESCR];
	fstypes[3]=ctr[TR_REISERFS_DESCR];
	fstypes[4]=NULL;

	if (!unattended) {		
		sprintf(message, ctr[TR_CHOOSE_FILESYSTEM]);
		rc = newtWinMenu( ctr[TR_CHOOSE_FILESYSTEM], message,
			50, 5, 5, 6, fstypes, &fstype, ctr[TR_OK],
			ctr[TR_CANCEL], NULL);
	} else {
	    rc = 1;
	    fstype = EXT4;
	}
	if (rc == 2)
		goto EXIT;

	/* Calculate amount of memory in machine */
        if ((handle = fopen("/proc/meminfo", "r")))
        {
            while (fgets(line, STRING_SIZE-1, handle)) {
                if (sscanf (line, "MemTotal: %s kB", string)) {
                    memory = atoi(string) / 1024 ;
                }
            }
            fclose(handle);
        }

	/* Partition, mkswp, mkfs.
	 * before partitioning, first determine the sizes of each
	 * partition.  In order to do that we need to know the size of
	 * the disk. 
	 */
	/* Don't use mysystem here so we can redirect output */
	sprintf(commandstring, "/sbin/sfdisk -s /dev/%s > /tmp/disksize 2> /dev/null", harddrive);
	system(commandstring);

	/* Calculate amount of disk space */
	if ((handle = fopen("/tmp/disksize", "r"))) {
		fgets(line, STRING_SIZE-1, handle);
		if (sscanf (line, "%s", string)) {
			disk = atoi(string) / 1024;
		}
		fclose(handle);
	}
	
	fprintf(flog, "Disksize = %ld, memory = %ld", disk, memory);
	
	 /* Calculating Swap-Size dependend of Ram Size */
	if (memory <= 256)
		swap_file = 128;
	else if (memory <= 1024 && memory > 256)
		swap_file = 256;
	else 
		swap_file = memory / 4;
	
  /* Calculating Root-Size dependend of Max Disk Space */
  if ( disk < 756 )
		root_partition = 200;
	else if ( disk >= 756 && disk <= 3072 )
		root_partition = 512;
	else 
		root_partition = 2048;
		
	
  /* Calculating the amount of free space */
	boot_partition = 64; /* in MB */
	system_partition = disk - ( root_partition + swap_file + boot_partition );
	
	fprintf(flog, ", boot = %ld, swap = %ld, mylog = %ld, root = %ld\n",
	boot_partition, swap_file, system_partition, root_partition);
	rc = 0;

	if ( (!unattended) && (((disk - (root_partition + swap_file + boot_partition)) < 256 ) && ((disk - (root_partition + boot_partition )) > 256)) ) {
   rc = newtWinChoice(title, ctr[TR_OK], ctr[TR_CANCEL], ctr[TR_CONTINUE_NO_SWAP]);
    if (rc == 1){
      swap_file = 0;
      system_partition = disk - ( root_partition + swap_file + boot_partition );
      fprintf(flog, "Changing Swap Size to 0 MB.\n");
    }
    else if (rc == 2){
    fprintf(flog, "Disk is too small.\n");
    errorbox(ctr[TR_DISK_TOO_SMALL]);goto EXIT;
    }
  } 
  else if (disk - (root_partition + swap_file + boot_partition) >= 256) {
  
  }
  else {
   fprintf(flog, "Disk is too small.\n");
   errorbox(ctr[TR_DISK_TOO_SMALL]);goto EXIT;
  }
  	 
	handle = fopen("/tmp/partitiontable", "w");

	/* Make swapfile */
  if (swap_file) {
     fprintf(handle, ",%ld,L,*\n,%ld,S,\n,%ld,L,\n,,L,\n",
     boot_partition, swap_file, root_partition);
  } else {
     fprintf(handle, ",%ld,L,*\n,0,0,\n,%ld,L,\n,,L,\n",
     boot_partition, root_partition);
  }

	fclose(handle);

	snprintf(commandstring, STRING_SIZE, "/sbin/sfdisk -L -uM %s < /tmp/partitiontable", hdparams.devnode_disk);
	if (runcommandwithstatus(commandstring, ctr[TR_PARTITIONING_DISK]))
	{
		errorbox(ctr[TR_UNABLE_TO_PARTITION]);
		goto EXIT;
	}

	if (fstype == EXT2) {
//		mysystem("/sbin/modprobe ext2");
		sprintf(mkfscommand, "/sbin/mke2fs -T ext2");
	} else if (fstype == REISERFS) {
		mysystem("/sbin/modprobe reiserfs");
		sprintf(mkfscommand, "/sbin/mkreiserfs -f");
	} else if (fstype == EXT3) {
//		mysystem("/sbin/modprobe ext3");
		sprintf(mkfscommand, "/sbin/mke2fs -T ext3");
	} else if (fstype == EXT4) {
//		mysystem("/sbin/modprobe ext4");
		sprintf(mkfscommand, "/sbin/mke2fs -T ext4");
	}

	snprintf(commandstring, STRING_SIZE, "/sbin/mke2fs -T ext2 -I 128 %s1", hdparams.devnode_part);
	if (runcommandwithstatus(commandstring, ctr[TR_MAKING_BOOT_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM]);
		goto EXIT;
	}

	if (swap_file) {
		snprintf(commandstring, STRING_SIZE, "/sbin/mkswap %s2", hdparams.devnode_part);
		if (runcommandwithstatus(commandstring, ctr[TR_MAKING_SWAPSPACE]))
		{
			errorbox(ctr[TR_UNABLE_TO_MAKE_SWAPSPACE]);
			goto EXIT;
		}
	}

	snprintf(commandstring, STRING_SIZE, "%s %s3", mkfscommand, hdparams.devnode_part);
	if (runcommandwithstatus(commandstring, ctr[TR_MAKING_ROOT_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM]);
		goto EXIT;
	}

	snprintf(commandstring, STRING_SIZE, "%s %s4", mkfscommand, hdparams.devnode_part);	
	if (runcommandwithstatus(commandstring, ctr[TR_MAKING_LOG_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MAKE_LOG_FILESYSTEM]);
		goto EXIT;
	}

	snprintf(commandstring, STRING_SIZE, "/bin/mount %s3 /harddisk", hdparams.devnode_part);
	if (runcommandwithstatus(commandstring, ctr[TR_MOUNTING_ROOT_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM]);
		goto EXIT;
	}

	mkdir("/harddisk/boot", S_IRWXU|S_IRWXG|S_IRWXO);
	mkdir("/harddisk/var", S_IRWXU|S_IRWXG|S_IRWXO);
	mkdir("/harddisk/var/log", S_IRWXU|S_IRWXG|S_IRWXO);
	
	snprintf(commandstring, STRING_SIZE, "/bin/mount %s1 /harddisk/boot", hdparams.devnode_part);
	if (runcommandwithstatus(commandstring, ctr[TR_MOUNTING_BOOT_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM]);
		goto EXIT;
	}
	if (swap_file) {
		snprintf(commandstring, STRING_SIZE, "/sbin/swapon %s2", hdparams.devnode_part);
		if (runcommandwithstatus(commandstring, ctr[TR_MOUNTING_SWAP_PARTITION]))
		{
			errorbox(ctr[TR_UNABLE_TO_MOUNT_SWAP_PARTITION]);
			goto EXIT;
		}
	}
	snprintf(commandstring, STRING_SIZE, "/bin/mount %s4 /harddisk/var", hdparams.devnode_part);
	if (runcommandwithstatus(commandstring, ctr[TR_MOUNTING_LOG_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM]);
		goto EXIT;
	}

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

	/* mount proc filesystem */
	mysystem("mkdir /harddisk/proc");
	mysystem("/bin/mount --bind /proc /harddisk/proc");
	mysystem("/bin/mount --bind /dev  /harddisk/dev");
	mysystem("/bin/mount --bind /sys  /harddisk/sys");

	/* Build cache lang file */
	snprintf(commandstring, STRING_SIZE, "/usr/sbin/chroot /harddisk /usr/bin/perl -e \"require '" CONFIG_ROOT "/lang.pl'; &Lang::BuildCacheLang\"");
	if (runcommandwithstatus(commandstring, ctr[TR_INSTALLING_LANG_CACHE]))
	{
		errorbox(ctr[TR_UNABLE_TO_INSTALL_LANG_CACHE]);
		goto EXIT;
	}

	/* Update /etc/fstab */
	snprintf(commandstring, STRING_SIZE, "/bin/sed -i -e \"s#DEVICE1#UUID=$(/sbin/blkid %s1 -sUUID | /usr/bin/cut -d'\"' -f2)#g\" /harddisk/etc/fstab", hdparams.devnode_part);
	system(commandstring);
	snprintf(commandstring, STRING_SIZE, "/bin/sed -i -e \"s#DEVICE2#UUID=$(/sbin/blkid %s2 -sUUID | /usr/bin/cut -d'\"' -f2)#g\" /harddisk/etc/fstab", hdparams.devnode_part);
	system(commandstring);
	snprintf(commandstring, STRING_SIZE, "/bin/sed -i -e \"s#DEVICE3#UUID=$(/sbin/blkid %s3 -sUUID | /usr/bin/cut -d'\"' -f2)#g\" /harddisk/etc/fstab", hdparams.devnode_part);
	system(commandstring);
	snprintf(commandstring, STRING_SIZE, "/bin/sed -i -e \"s#DEVICE4#UUID=$(/sbin/blkid %s4 -sUUID | /usr/bin/cut -d'\"' -f2)#g\" /harddisk/etc/fstab", hdparams.devnode_part);
	system(commandstring);

	if (fstype == EXT2) {
		replace("/harddisk/etc/fstab", "FSTYPE", "ext2");
		replace("/harddisk/boot/grub/grub.conf", "MOUNT", "ro");
	} else if (fstype == REISERFS) {
		replace("/harddisk/etc/fstab", "FSTYPE", "reiserfs");
		replace("/harddisk/boot/grub/grub.conf", "MOUNT", "ro");
	} else if (fstype == EXT3) {
		replace("/harddisk/etc/fstab", "FSTYPE", "ext3");
		replace("/harddisk/boot/grub/grub.conf", "MOUNT", "ro");
	} else if (fstype == EXT4) {
		replace("/harddisk/etc/fstab", "FSTYPE", "ext4");
		replace("/harddisk/boot/grub/grub.conf", "MOUNT", "ro");
	}

	replace("/harddisk/boot/grub/grub.conf", "KVER", KERNEL_VERSION);

	snprintf(commandstring, STRING_SIZE, "/bin/sed -i -e \"s#root=ROOT#root=UUID=$(/sbin/blkid %s3 -sUUID | /usr/bin/cut -d'\"' -f2)#g\" /harddisk/boot/grub/grub.conf", hdparams.devnode_part);
	system(commandstring);

	mysystem("ln -s grub.conf /harddisk/boot/grub/menu.lst");

	system("/bin/sed -e 's#/harddisk#/#g' -e 's#//#/#g'  < /proc/mounts > /harddisk/etc/mtab");

	/*
	 * Generate device.map to help grub finding the device to install itself on.
	 */
	FILE *f = NULL;
	if (f = fopen("/harddisk/boot/grub/device.map", "w")) {
		fprintf(f, "(hd0) %s\n", hdparams.devnode_disk);
		fclose(f);
	}

	snprintf(commandstring, STRING_SIZE, 
		 "/usr/sbin/chroot /harddisk /usr/sbin/grub-install --no-floppy %s", hdparams.devnode_disk);
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
		replace("/harddisk/boot/grub/grub.conf", " panic=10 ", " console=ttyS0,38400n8 panic=10 ");

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

	if (allok && !allok_fastexit)
	{
		if (unattended) {
			fprintf(flog, "Entering unattended setup\n");
			if (unattended_setup(unattendedkv)) {
				snprintf(commandstring, STRING_SIZE, "/bin/sleep 10");
				runcommandwithstatus(commandstring, "Unattended installation finished, system will reboot");
			} else {
				errorbox("Unattended setup failed.");
				goto EXIT;
			}
		}

		fflush(flog);
		fclose(flog);
		newtFinished();

		if (system("/bin/umount /harddisk/proc"))
			printf("Unable to umount /harddisk/proc.\n"); 
	} else {
		fflush(flog);
		fclose(flog);
		newtFinished();
	}

	fcloseall();

	if (swap_file) {
		snprintf(commandstring, STRING_SIZE, "/bin/swapoff %s2", hdparams.devnode_part);
	}

	newtFinished();

	system("/bin/umount /harddisk/proc >/dev/null 2>&1");
	system("/bin/umount /harddisk/dev >/dev/null 2>&1");
	system("/bin/umount /harddisk/sys >/dev/null 2>&1");

	system("/bin/umount /harddisk/var >/dev/null 2>&1");
	system("/bin/umount /harddisk/boot >/dev/null 2>&1");
	system("/bin/umount /harddisk >/dev/null 2>&1");

	if (!(allok))
		system("/etc/halt");

	return 0;
}
