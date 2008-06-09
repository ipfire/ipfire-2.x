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
 
#define INST_FILECOUNT 6200
#define UNATTENDED_CONF "/cdrom/boot/unattended.conf"

#define REISER4 0
#define REISERFS 1
#define EXT3 2

FILE *flog = NULL;
char *mylog;

char **ctr;

extern char url[STRING_SIZE];

struct  nic  nics[20] = { { "" , "" , "" } }; // only defined for compile
struct knic knics[20] = { { "" , "" , "" , "" } }; // only defined for compile

extern char *en_tr[];
extern char *de_tr[];

int main(int argc, char *argv[])
{
	char *langnames[] = { "Deutsch", "English", NULL };
	char *shortlangnames[] = { "de", "en", NULL };
	char **langtrs[] = { de_tr, en_tr, NULL };
	char hdletter;
	char harddrive[30], sourcedrive[5];	/* Device holder. */
	struct devparams hdparams, cdromparams; /* Params for CDROM and HD */
	int rc = 0;
	char commandstring[STRING_SIZE];
	char mkfscommand[STRING_SIZE];
	char *fstypes[] = { "Reiser4", "ReiserFS", "ext3", NULL };
	int fstype = REISER4;
	int choice;
	int i;
	int found = 0;
	int firstrun = 0;
	char shortlangname[10];
	char message[1000];
	char title[STRING_SIZE];
	int allok = 0;
	int allok_fastexit=0;
	int raid_disk = 0;
	struct keyvalue *ethernetkv = initkeyvalues();
	FILE *handle, *cmdfile;
	char line[STRING_SIZE];
	char string[STRING_SIZE];
	long memory = 0, disk = 0, free;
	long system_partition, boot_partition, root_partition, swap_file;
	int scsi_disk = 0;
	char *yesnoharddisk[3];	//	char *yesnoharddisk = { "NO", "YES", NULL };
		
	int unattended = 0;
	struct keyvalue *unattendedkv = initkeyvalues();
	int hardyn = 0;

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

	/* Do usb detection first for usb keyboard */
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
	}

	mysystem("/sbin/modprobe ide-generic");
	mysystem("/sbin/modprobe generic");
	mysystem("/sbin/modprobe ide-cd");
	mysystem("/sbin/modprobe ide-disk");
	mysystem("/sbin/modprobe uhci-hcd");
	mysystem("/sbin/modprobe ohci-hcd");
	mysystem("/sbin/modprobe ehci-hcd");
	mysystem("/sbin/modprobe ohci1394");
	mysystem("/sbin/modprobe sd_mod");
	mysystem("/sbin/modprobe sr_mod");
	mysystem("/sbin/modprobe usb-storage");
	mysystem("/sbin/modprobe usbhid");

	mysystem("/sbin/modprobe iso9660"); // CDROM
	mysystem("/sbin/modprobe ext2"); // Boot patition
	mysystem("/sbin/modprobe vfat"); // USB key
	
	/* German is the default */
	for (choice = 0; langnames[choice]; choice++)
	{
		if (strcmp(langnames[choice], "Deutsch") == 0)
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

	newtDrawRootText(14, 0, NAME " " VERSION " - " SLOGAN );
	newtPushHelpLine(ctr[TR_HELPLINE]);
	sprintf (title, "%s %s - %s", NAME, VERSION, SLOGAN);

	// Starting hardware detection
	runcommandwithstatus("/bin/probehw.sh", ctr[TR_PROBING_HARDWARE]);

	sprintf(message, ctr[TR_WELCOME], NAME);
	newtWinMessage(title, ctr[TR_OK], message);

	switch (mysystem("/bin/mountsource.sh")) {
	    case 0:
				break;
	    case 10:
      	errorbox(ctr[TR_NO_CDROM]);
		goto EXIT;
	}

	/* read source drive letter */
	if ((handle = fopen("/tmp/source_device", "r")) == NULL) {
		errorbox(ctr[TR_ERROR_PROBING_CDROM]);
		goto EXIT;
	}
	fgets(sourcedrive, 5, handle);
	fprintf(flog, "Source drive: %s\n", sourcedrive);
	fclose(handle);
	
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
				if (firstrun == 1) {
					errorbox(ctr[TR_NO_HARDDISK]);
					goto EXIT;
				}
				// Do this if the kudzu-scan fails...
				runcommandwithstatus("/bin/probehw.sh deep-scan", ctr[TR_PROBING_HARDWARE]);
				firstrun = 1;
		}
	}

	if ((handle = fopen("/tmp/dest_device", "r")) == NULL) {
		errorbox(ctr[TR_NO_HARDDISK]);
		goto EXIT;
	}
	fgets(harddrive, 30, handle);
	fclose(handle);
			
	/* load unattended configuration */
	if (unattended) {
	    fprintf(flog, "unattended: Reading unattended.conf\n");

	    (void) readkeyvalues(unattendedkv, UNATTENDED_CONF);
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
	{	char tmp[30];
		strcpy(tmp, scsi_disk ? "sda" : harddrive);
		sprintf(hdparams.devnode_disk_run, "/dev/%s", tmp);
		sprintf(hdparams.devnode_part_run, "/dev/%s%s", tmp, raid_disk ? "p" : "");
	}

	fprintf(flog, "Destination drive: %s\n", hdparams.devnode_disk);
	
	sprintf(message, ctr[TR_PREPARE_HARDDISK], hdparams.devnode_disk);
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

	if (!unattended) {		
		sprintf(message, ctr[TR_CHOOSE_FILESYSTEM]);
		rc = newtWinMenu( ctr[TR_CHOOSE_FILESYSTEM], message,
			50, 5, 5, 6, fstypes, &fstype, ctr[TR_OK],
			ctr[TR_CANCEL], NULL);
	} else {
	    rc = 1;
	    fstype = REISER4; // Reiser4 is our standard filesystem. Love it or shut up!
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
	sprintf(commandstring, "/bin/sfdisk -s /dev/%s > /tmp/disksize 2> /dev/null", harddrive);
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
	if (memory < 128)
		swap_file = 32;
	else if (memory >= 1024)
		swap_file = 512;
	else 
		swap_file = memory;
	
  /* Calculating Root-Size dependend of Max Disk Space */
  if ( disk < 756 )
		root_partition = 200;
	else if ( disk >= 756 && disk <= 3072 )
		root_partition = 512;
	else 
		root_partition = 2048;
		
	
  /* Calculating the amount of free space */
	boot_partition = 20; /* in MB */
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

	snprintf(commandstring, STRING_SIZE, "/bin/sfdisk -L -uM %s < /tmp/partitiontable", hdparams.devnode_disk);
	if (runcommandwithstatus(commandstring, ctr[TR_PARTITIONING_DISK]))
	{
		errorbox(ctr[TR_UNABLE_TO_PARTITION]);
		goto EXIT;
	}
	
	if (fstype == REISER4) {
		mysystem("/sbin/modprobe reiser4");
		sprintf(mkfscommand, "/sbin/mkfs.reiser4 -y");
	} else if (fstype == REISERFS) {
		mysystem("/sbin/modprobe reiserfs");
		sprintf(mkfscommand, "/sbin/mkreiserfs -f");
	} else if (fstype == EXT3) {
		mysystem("/sbin/modprobe ext3");
		sprintf(mkfscommand, "/sbin/mke2fs -T ext3 -c");
	}

	snprintf(commandstring, STRING_SIZE, "/sbin/mke2fs -T ext2 -c %s1", hdparams.devnode_part);
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
		"/bin/tar -C /harddisk -xvjf /cdrom/" SNAME "-" VERSION ".tbz2");
	
	if (runcommandwithprogress(60, 4, title, commandstring, INST_FILECOUNT,
		ctr[TR_INSTALLING_FILES]))
	{
		errorbox(ctr[TR_UNABLE_TO_INSTALL_FILES]);
		goto EXIT;
	}
	
	/* Save language und local settings */
	write_lang_configs(shortlangname);

	/* touch the modules.dep files */
	snprintf(commandstring, STRING_SIZE, 
		"/bin/touch /harddisk/lib/modules/%s-ipfire/modules.dep",
		KERNEL_VERSION);
	mysystem(commandstring);
	snprintf(commandstring, STRING_SIZE, 
		"/bin/touch /harddisk/lib/modules/%s-ipfire-smp/modules.dep",
		KERNEL_VERSION);
	mysystem(commandstring);

	/* Rename uname */
	rename ("/harddisk/bin/uname.bak", "/harddisk/bin/uname");

	/* mount proc filesystem */
	mysystem("mkdir /harddisk/proc");
	mysystem("/bin/mount --bind /proc /harddisk/proc");
	mysystem("/bin/mount --bind /dev  /harddisk/dev");
	mysystem("/bin/mount --bind /sys  /harddisk/sys");

	/* Build cache lang file */
	snprintf(commandstring, STRING_SIZE, "/sbin/chroot /harddisk /usr/bin/perl -e \"require '" CONFIG_ROOT "/lang.pl'; &Lang::BuildCacheLang\"");
	if (runcommandwithstatus(commandstring, ctr[TR_INSTALLING_LANG_CACHE]))
	{
		errorbox(ctr[TR_UNABLE_TO_INSTALL_LANG_CACHE]);
		goto EXIT;
	}

	/* Update /etc/fstab */
	replace("/harddisk/etc/fstab", "DEVICE", hdparams.devnode_part_run);
	
	if (fstype == REISER4) {
		replace("/harddisk/etc/fstab", "FSTYPE", "reiser4");
		replace("/harddisk/etc/mkinitcpio.conf", "MODULES=\"", "MODULES=\"reiser4 ");
		replace("/harddisk/boot/grub/grub.conf", "MOUNT", "rw");
	} else if (fstype == REISERFS) {
		replace("/harddisk/etc/fstab", "FSTYPE", "reiserfs");
		replace("/harddisk/boot/grub/grub.conf", "MOUNT", "ro");
	} else if (fstype == EXT3) {
		snprintf(commandstring, STRING_SIZE, "tune2fs -j %s3", hdparams.devnode_part);
		if (runcommandwithstatus(commandstring, ctr[TR_JOURNAL_EXT3]))
		{
			errorbox(ctr[TR_JOURNAL_ERROR]);
			replace("/harddisk/etc/fstab", "FSTYPE", "ext2");
			goto NOJOURNAL;
		}
		snprintf(commandstring, STRING_SIZE, "tune2fs -j %s4", hdparams.devnode_part);
		if (runcommandwithstatus(commandstring, ctr[TR_JOURNAL_EXT3]))
		{
			errorbox(ctr[TR_JOURNAL_ERROR]);
			replace("/harddisk/etc/fstab", "FSTYPE", "ext2");
			goto NOJOURNAL;
		}
		replace("/harddisk/etc/fstab", "FSTYPE", "ext3");
		NOJOURNAL:
		replace("/harddisk/etc/mkinitcpio.conf", "MODULES=\"", "MODULES=\"ext3 ");
		replace("/harddisk/boot/grub/grub.conf", "MOUNT", "ro");
	}

	replace("/harddisk/boot/grub/grub.conf", "KVER", KERNEL_VERSION);

	/* mkinitcpio has a problem if ide and pata are included */
	if ( scsi_disk==1 ) {
	    /* Remove the ide hook if we install sda */
	    replace("/harddisk/etc/mkinitcpio.conf", " ide ", " ");
	} else {
	    /* Remove the pata hook if we install hda */
	    replace("/harddisk/etc/mkinitcpio.conf", " pata ", " ");
	}
	/* Going to make our initrd... */
	snprintf(commandstring, STRING_SIZE, "/sbin/chroot /harddisk /sbin/mkinitcpio -g /boot/ipfirerd-%s.img -k %s-ipfire", KERNEL_VERSION, KERNEL_VERSION);
	runcommandwithstatus(commandstring, ctr[TR_BUILDING_INITRD]);
	snprintf(commandstring, STRING_SIZE, "/sbin/chroot /harddisk /sbin/mkinitcpio -g /boot/ipfirerd-%s-smp.img -k %s-ipfire-smp", KERNEL_VERSION, KERNEL_VERSION );
	runcommandwithstatus(commandstring, ctr[TR_BUILDING_INITRD]);

	sprintf(string, "root=%s3", hdparams.devnode_part_run);
	replace( "/harddisk/boot/grub/grub.conf", "root=ROOT", string);
	mysystem("ln -s grub.conf /harddisk/boot/grub/menu.lst");

	system("sed -e 's#harddisk\\/##g' < /proc/mounts > /harddisk/etc/mtab");

	snprintf(commandstring, STRING_SIZE, 
		 "/sbin/chroot /harddisk /usr/sbin/grub-install --no-floppy %s", hdparams.devnode_disk);
	if (runcommandwithstatus(commandstring, ctr[TR_INSTALLING_GRUB])) {
		errorbox(ctr[TR_UNABLE_TO_INSTALL_GRUB]);
		goto EXIT;
	}
	
	mysystem("umount /cdrom");
	snprintf(commandstring, STRING_SIZE, "eject /dev/%s", sourcedrive);
	mysystem(commandstring);

	if (!unattended) {
		sprintf(message, ctr[TR_CONGRATULATIONS_LONG],
				NAME, SNAME, NAME);
		newtWinMessage(ctr[TR_CONGRATULATIONS], ctr[TR_OK], message);
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

		if (!unattended) {
			if (system("/sbin/chroot /harddisk /usr/local/sbin/setup /dev/tty2 INSTALL"))
				printf("Unable to run setup.\n");
		}

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

	system("/bin/umount /harddisk/proc");
	system("/bin/umount /harddisk/dev");
	system("/bin/umount /harddisk/sys");

	system("/bin/umount /harddisk/var");
	system("/bin/umount /harddisk/boot");
	system("/bin/umount /harddisk");
	  
	system("/etc/halt");

	return 0;
}
