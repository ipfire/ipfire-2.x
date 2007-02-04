/* SmoothWall install program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Contains main entry point, and misc functions.
 * 
 */

#include "install.h"
#define _GNU_SOURCE
 
#define CDROM_INSTALL 0
#define URL_INSTALL 1
#define DISK_INSTALL 2
#define INST_FILECOUNT 7000
#define UNATTENDED_CONF "/cdrom/boot/unattended.conf"

int raid_disk = 0;
FILE *flog = NULL;
char *mylog;

char **ctr;

char *pcmcia = NULL;
extern char url[STRING_SIZE];

extern char *en_tr[];
extern char *de_tr[];

int detect_smp() {
	FILE *fd = NULL;
	char line[STRING_SIZE];
	int cpu_count = 0;

	if ((fd = fopen("/proc/cpuinfo", "r")) == NULL) {
		return 0;
	}
	while (fgets(line, STRING_SIZE, fd) != NULL) {
		if (strstr(line, "processor") == line) {
			cpu_count++;
		}
	}
	(void)fclose(fd);
	return (cpu_count > 1);
}

long calc_swapsize(long memory, long disk) {
	if (memory < 128) {
		return 256;
	}
	if (memory > 1024) {
		return 512;
	}

	return memory*2;
}

int unattended_setup(struct keyvalue *unattendedkv) {
    struct keyvalue *mainsettings = initkeyvalues();
    struct keyvalue *ethernetkv = initkeyvalues();
    FILE *file, *hosts;
    char commandstring[STRING_SIZE];

    char domainname[STRING_SIZE];
    char hostname[STRING_SIZE];
    char keymap[STRING_SIZE];
    char language[STRING_SIZE];
    char timezone[STRING_SIZE];
    char theme[STRING_SIZE];
    char green_address[STRING_SIZE];
    char green_netmask[STRING_SIZE];
    char green_netaddress[STRING_SIZE];
    char green_broadcast[STRING_SIZE];
    char root_password[STRING_SIZE];
    char admin_password[STRING_SIZE];

    findkey(unattendedkv, "DOMAINNAME", domainname);
    findkey(unattendedkv, "HOSTNAME", hostname);
    findkey(unattendedkv, "KEYMAP", keymap);
    findkey(unattendedkv, "LANGUAGE", language);
    findkey(unattendedkv, "TIMEZONE", timezone);
    findkey(unattendedkv, "THEME", theme);
    findkey(unattendedkv, "GREEN_ADDRESS", green_address);
    findkey(unattendedkv, "GREEN_NETMASK", green_netmask);
    findkey(unattendedkv, "GREEN_NETADDRESS", green_netaddress);
    findkey(unattendedkv, "GREEN_BROADCAST", green_broadcast);
    findkey(unattendedkv, "ROOT_PASSWORD", root_password);
    findkey(unattendedkv, "ADMIN_PASSWORD", admin_password);

    /* write main/settings. */
    replacekeyvalue(mainsettings, "DOMAINNAME", domainname);
    replacekeyvalue(mainsettings, "HOSTNAME", hostname);
    replacekeyvalue(mainsettings, "KEYMAP", keymap);
    replacekeyvalue(mainsettings, "LANGUAGE", language);
    replacekeyvalue(mainsettings, "TIMEZONE", timezone);
    replacekeyvalue(mainsettings, "THEME", theme);
    writekeyvalues(mainsettings, "/harddisk" CONFIG_ROOT "/main/settings");
    freekeyvalues(mainsettings);

    /* do setup stuff */
    fprintf(flog, "unattended: Starting setup\n");

    /* network */
    fprintf(flog, "unattended: setting up network configuration\n");

    (void) readkeyvalues(ethernetkv, "/harddisk" CONFIG_ROOT "/ethernet/settings");
    replacekeyvalue(ethernetkv, "GREEN_ADDRESS", green_address);
    replacekeyvalue(ethernetkv, "GREEN_NETMASK", green_netmask);
    replacekeyvalue(ethernetkv, "GREEN_NETADDRESS", green_netaddress);
    replacekeyvalue(ethernetkv, "GREEN_BROADCAST", green_broadcast);
    replacekeyvalue(ethernetkv, "CONFIG_TYPE", "0");
    replacekeyvalue(ethernetkv, "GREEN_DEV", "eth0");
    write_ethernet_configs(ethernetkv);
    freekeyvalues(ethernetkv);

    /* timezone */
    unlink("/harddisk/etc/localtime");
    snprintf(commandstring, STRING_SIZE, "/harddisk/%s", timezone);
    link(commandstring, "/harddisk/etc/localtime");

    /* hostname */
    fprintf(flog, "unattended: writing hostname.conf\n");
    if (!(file = fopen("/harddisk" CONFIG_ROOT "/main/hostname.conf", "w")))
    {
	errorbox("unattended: ERROR writing hostname.conf");
	return 0;
    }
    fprintf(file, "ServerName %s\n", hostname);
    fclose(file);

    fprintf(flog, "unattended: writing hosts\n");
    if (!(hosts = fopen("/harddisk/etc/hosts", "w")))
    {
	errorbox("unattended: ERROR writing hosts");
	return 0;
    }
    fprintf(hosts, "127.0.0.1\tlocalhost\n");
    fprintf(hosts, "%s\t%s.%s\t%s\n", green_address, hostname, domainname, hostname);
    fclose(hosts);

    fprintf(flog, "unattended: writing hosts.allow\n");
    if (!(file = fopen("/harddisk/etc/hosts.allow", "w")))
    {
	errorbox("unattended: ERROR writing hosts.allow");
	return 0;
    }
    fprintf(file, "sshd : ALL\n");
    fprintf(file, "ALL  : localhost\n");
    fprintf(file, "ALL  : %s/%s\n", green_netaddress, green_netmask);
    fclose(file);

    fprintf(flog, "unattended: writing hosts.deny\n");
    if (!(file = fopen("/harddisk/etc/hosts.deny", "w")))
    {
	errorbox("unattended: ERROR writing hosts.deny");
        return 0;
    }
    fprintf(file, "ALL : ALL\n");
    fclose(file);

    /* set root password */
    fprintf(flog, "unattended: setting root password\n");
    snprintf(commandstring, STRING_SIZE,
	    "/sbin/chroot /harddisk /bin/sh -c \"echo 'root:%s' | /usr/sbin/chpasswd\"", root_password);
    if (mysystem(commandstring)) {
	errorbox("unattended: ERROR setting root password");
	return 0;
    }

    /* set admin password */
    fprintf(flog, "unattended: setting admin password\n");
    snprintf(commandstring, STRING_SIZE,
	    "/sbin/chroot /harddisk /usr/sbin/htpasswd -c -m -b " CONFIG_ROOT "/auth/users admin '%s'", admin_password);
    if (mysystem(commandstring)) {
	errorbox("unattended: ERROR setting admin password");
	return 0;
    }
    return 1;
}

int main(int argc, char *argv[])
{
	char *langnames[] = { "Deutsch", "English", NULL };
	char *shortlangnames[] = { "de", "en", NULL };
	char **langtrs[] = { de_tr, en_tr, NULL };
	char hdletter, cdletter;
	char harddrive[5], sourcedrive[5];	/* Device holder. */
	struct devparams hdparams, cdromparams; /* Params for CDROM and HD */
	int cdmounted = 0; /* Loop flag for inserting a cd. */
	int rc = 0;
	char commandstring[STRING_SIZE];
	char *installtypes[] = { "CDROM", "HTTP/FTP", NULL };
	int installtype = CDROM_INSTALL;
	char insertmessage[STRING_SIZE];
	char insertdevnode[STRING_SIZE];
	int choice;
	char shortlangname[10];
	char message[1000];
	char title[STRING_SIZE];
	int allok = 0;
	int allok_fastexit=0;
	int unmount_before=0;
	struct keyvalue *ethernetkv = initkeyvalues();
	FILE *handle, *cmdfile;
	char line[STRING_SIZE];
	char string[STRING_SIZE];
	long maximum_free = 0, current_free;
	long memory = 0;
	long system_partition, boot_partition, root_partition, swap_file;
	int scsi_disk = 0;
	int pcmcia_disk = 0;
	int pcmcia_cdrom = 0;
	int scsi_cdrom = 0;
	int ide_cdrom = 0;
	int fdisk = 0;
	int hardyn = 0;
	char *yesnoharddisk[] = { "NO", "YES", NULL };
	char *yesno[] = { "NO", "YES", NULL };
	char green[STRING_SIZE];
	int unattended = 0;
	struct keyvalue *unattendedkv = initkeyvalues();
	char packages[STRING_SIZE];
	int serial_console = 0;
	char megabridge[STRING_SIZE];

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
		if (strstr (line, "fdisk") != NULL) {
			fprintf(flog, "Manual FDISK selected.\n");
			fdisk = 1;
		}
		if (strstr (line, "nousb") == NULL) {
			fprintf(flog, "Initializing USB controllers.\n");
			initialize_usb();
		} else {
			fprintf(flog, "Skipping USB detection.\n");
		}
		// check if we have to make an unattended install
		if (strstr (line, "unattended") != NULL) {		
		    unattended = 1;
		}
	}

	// make some beeps before wiping the system :)
	if (unattended) {
	    runcommandwithstatus("/bin/sleep 10", "WARNING: Unattended installation will start in 10 seconds...");
 	}
	
	/* German is the default */
	for (choice = 0; langnames[choice]; choice++)
	{
		if (strcmp(langnames[choice], "Deutsch") == 0)
			break;
	}
	if (!langnames[choice])
		goto EXIT;

	if (!unattended) {
	    rc = newtWinMenu("Language selection",
		    "Select the language you wish to use for the " NAME ".", 50, 5, 5, 8,
		    langnames, &choice, "Ok", NULL);
	}

	ctr = langtrs[choice];
	strcpy(shortlangname, shortlangnames[choice]);

	mysystem("/bin/setfont lat0-16");

	newtDrawRootText(14, 0, NAME " " VERSION " - " SLOGAN );
	newtPushHelpLine(ctr[TR_HELPLINE]);

	if (!unattended) {
		sprintf(message, ctr[TR_WELCOME], NAME);
		sprintf (title, "%s %s - %s", NAME, VERSION, SLOGAN);
		newtWinMessage(title, ctr[TR_OK], message);

		sprintf(message, ctr[TR_SELECT_INSTALLATION_MEDIA_LONG], NAME);
		rc = newtWinMenu(ctr[TR_SELECT_INSTALLATION_MEDIA], message,
			50, 5, 5, 6, installtypes, &installtype, ctr[TR_OK],
			ctr[TR_CANCEL], NULL);
	}
	else {
	    rc = 1;
	    installtype = CDROM_INSTALL;
	}

	if (rc == 2)
		goto EXIT;

	// Starting hardware detection
	runcommandwithstatus("/bin/probehw.sh", ctr[TR_PROBING_HARDWARE]);

	/* CDROM INSTALL */
	if (installtype == CDROM_INSTALL) {

		switch (mysystem("/bin/mountsource.sh")) {
		    case 0:
			installtype = CDROM_INSTALL;
			cdmounted = 1;
			break;
		    case 1:
			installtype = DISK_INSTALL;
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

		snprintf(cdromparams.devnode, STRING_SIZE, "/dev/%s", sourcedrive);
		cdromparams.module = 0;
		fprintf(flog, "Source device: %s\n", cdromparams.devnode);
	}

 	/* Configure the network now! */
	if (installtype == URL_INSTALL) {
		/* Network driver and params. */
		if (!(networkmenu(ethernetkv))) {
			errorbox(ctr[TR_NETWORK_SETUP_FAILED]);
			goto EXIT;
		}

		/* Check for ipcop-<VERSION>.tbz2 */
		if (checktarball(SNAME "-" VERSION ".tbz2", ctr[TR_ENTER_URL])) {
			errorbox(ctr[TR_NO_IPCOP_TARBALL_FOUND]);
			goto EXIT;
		}
	}

	/* Get device for the HD.  This has to succeed. */
	if (!(hdletter = findidetype(IDE_HD)))
	{
		/* Need to clean this up at some point */
		if (!try_scsi("sda") || strstr(sourcedrive, "sda") != NULL) {
			if (!try_scsi("ida/c0d0")) {
				if (!try_scsi("cciss/c0d0")) {
					if (!try_scsi("rd/c0d0")) {
						if (!try_scsi("ataraid/d0")) {
							errorbox(ctr[TR_NO_HARDDISK]);
							goto EXIT;
						} else {
							raid_disk = 1;
							sprintf(harddrive, "ataraid/d0");
						}
					} else {
						raid_disk = 1;
						sprintf(harddrive, "rd/c0d0");
					}
				} else {
					raid_disk = 1;
					sprintf(harddrive, "cciss/c0d0");
				}
			} else {
				raid_disk = 1;
				sprintf(harddrive, "ida/c0d0");
			}
		} else {
		    if (strstr(sourcedrive, "sda") != NULL) {
			// probably installing from usb stick, try sdb
			if (try_scsi("sdb")) {
			    sprintf(harddrive, "sdb");
			}
			else {
			    errorbox(ctr[TR_NO_HARDDISK]);
			    goto EXIT;
			}
		    }
		    else {
			sprintf(harddrive, "sda");
		    }
		}
		scsi_disk = 1;
	} else
		sprintf(harddrive, "hd%c", hdletter);

	fprintf(flog, "Destination drive: %s\n", harddrive);

	/* load unattended configuration */
	if (unattended) {
	    fprintf(flog, "unattended: Reading unattended.conf\n");

	    (void) readkeyvalues(unattendedkv, UNATTENDED_CONF);
	}

	/* Make the hdparms struct and print the contents. */
	snprintf(hdparams.devnode, STRING_SIZE, "/dev/%s", harddrive);
	hdparams.module = 0;

	sprintf(message, ctr[TR_PREPARE_HARDDISK], hdparams.devnode);
	
	if (unattended) {
	    hardyn = 1;
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
        if ((handle = fopen("/tmp/disksize", "r")))
        {
           	fgets(line, STRING_SIZE-1, handle);
            	if (sscanf (line, "%s", string)) {
			maximum_free = atoi(string) / 1024;
            	}
            	fclose(handle);
        }
	
	fprintf(flog, "maximum_free = %ld, memory = %ld", 
		maximum_free, memory);
	
	swap_file = calc_swapsize(memory, maximum_free);

	if (maximum_free < 512 + swap_file ) {
		if (maximum_free < 512) {
			errorbox(ctr[TR_DISK_TOO_SMALL]);
			goto EXIT;
		}

		if (!unattended) {
		    rc = newtWinChoice(title, ctr[TR_OK], ctr[TR_CANCEL], ctr[TR_CONTINUE_NO_SWAP]);
		}
		else {
		    rc = 1;
		}
		
		if (rc != 1)
			goto EXIT;
		swap_file = 0;
	}

	boot_partition = 20; /* in MB */
	current_free = maximum_free - boot_partition - swap_file;

	root_partition = 2048 ;
	if (current_free < 512) {
		errorbox(ctr[TR_DISK_TOO_SMALL]);
		goto EXIT;
	}

	current_free = current_free - root_partition;
	if (!swap_file) {
		root_partition = root_partition + swap_file;
	}

	system_partition = current_free;

	fprintf(flog, "boot = %ld, swap = %ld, mylog = %ld, root = %ld\n",
		boot_partition, swap_file, system_partition, root_partition);

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

	snprintf(commandstring, STRING_SIZE, "/bin/sfdisk -L -uM %s < /tmp/partitiontable", hdparams.devnode);
	if (runcommandwithstatus(commandstring, ctr[TR_PARTITIONING_DISK]))
	{
		errorbox(ctr[TR_UNABLE_TO_PARTITION]);
		goto EXIT;
	}

	mysystem("/sbin/udevstart");

	if (raid_disk)
		snprintf(commandstring, STRING_SIZE, "/bin/mke2fs -T ext2 -c %sp1", hdparams.devnode);
	else
		snprintf(commandstring, STRING_SIZE, "/bin/mke2fs -T ext2 -c %s1", hdparams.devnode);
	if (runcommandwithstatus(commandstring, ctr[TR_MAKING_BOOT_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM]);
		goto EXIT;
	}

	if (swap_file) {
		if (raid_disk)
			snprintf(commandstring, STRING_SIZE, "/sbin/mkswap %sp2", hdparams.devnode);	
		else
			snprintf(commandstring, STRING_SIZE, "/sbin/mkswap %s2", hdparams.devnode);
		if (runcommandwithstatus(commandstring, ctr[TR_MAKING_SWAPSPACE]))
		{
			errorbox(ctr[TR_UNABLE_TO_MAKE_SWAPSPACE]);
			goto EXIT;
		}
	}

	if (raid_disk)
		snprintf(commandstring, STRING_SIZE, "/bin/mkreiserfs -f %sp3", hdparams.devnode);	
	else
		snprintf(commandstring, STRING_SIZE, "/bin/mkreiserfs -f %s3", hdparams.devnode);	

	if (runcommandwithstatus(commandstring, ctr[TR_MAKING_ROOT_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM]);
		goto EXIT;
	}

	if (raid_disk)
		snprintf(commandstring, STRING_SIZE, "/bin/mkreiserfs -f %sp4", hdparams.devnode);	
	else
		snprintf(commandstring, STRING_SIZE, "/bin/mkreiserfs -f %s4", hdparams.devnode);	

	if (runcommandwithstatus(commandstring, ctr[TR_MAKING_LOG_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM]);
		goto EXIT;
	}

	/* Mount harddisk. */
	if (raid_disk)
		snprintf(commandstring, STRING_SIZE, "/bin/mount %sp3 /harddisk", hdparams.devnode);
	else
		snprintf(commandstring, STRING_SIZE, "/bin/mount %s3 /harddisk", hdparams.devnode);
	if (runcommandwithstatus(commandstring, ctr[TR_MOUNTING_ROOT_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM]);
		goto EXIT;
	}

	mkdir("/harddisk/boot", S_IRWXU|S_IRWXG|S_IRWXO);
	mkdir("/harddisk/var", S_IRWXU|S_IRWXG|S_IRWXO);
	mkdir("/harddisk/var/log", S_IRWXU|S_IRWXG|S_IRWXO);
	
	if (raid_disk)
		snprintf(commandstring, STRING_SIZE, "/bin/mount %sp1 /harddisk/boot", hdparams.devnode);
	else
		snprintf(commandstring, STRING_SIZE, "/bin/mount %s1 /harddisk/boot", hdparams.devnode);

	if (runcommandwithstatus(commandstring, ctr[TR_MOUNTING_BOOT_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM]);
		goto EXIT;
	}
	if (swap_file) {
		if (raid_disk)
			snprintf(commandstring, STRING_SIZE, "/sbin/swapon %sp2", hdparams.devnode);
		else
			snprintf(commandstring, STRING_SIZE, "/sbin/swapon %s2", hdparams.devnode);
		if (runcommandwithstatus(commandstring, ctr[TR_MOUNTING_SWAP_PARTITION]))
		{
			errorbox(ctr[TR_UNABLE_TO_MOUNT_SWAP_PARTITION]);
			goto EXIT;
		}
	}
	if (raid_disk)
		snprintf(commandstring, STRING_SIZE, "/bin/mount %sp4 /harddisk/var", hdparams.devnode);
	else
		snprintf(commandstring, STRING_SIZE, "/bin/mount %s4 /harddisk/var", hdparams.devnode);
	if (runcommandwithstatus(commandstring, ctr[TR_MOUNTING_LOG_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM]);
		goto EXIT;
	}
	
	snprintf(commandstring, STRING_SIZE, "/bin/tar -C /harddisk -xvjf /cdrom/" SNAME "-" VERSION ".tbz2");
	
	if (runcommandwithprogress(60, 4, title, commandstring, INST_FILECOUNT,
		ctr[TR_INSTALLING_FILES]))
	{
		errorbox(ctr[TR_UNABLE_TO_INSTALL_FILES]);
		goto EXIT;
	}
		
	/* Save USB controller type to modules.conf */
	write_usb_modules_conf();

	/* touch the modules.dep files */
	snprintf(commandstring, STRING_SIZE, 
		"/sbin/chroot /harddisk /usr/bin/touch /lib/modules/%s/modules.dep",
		KERNEL_VERSION);
	mysystem(commandstring);
	snprintf(commandstring, STRING_SIZE, 
		"/sbin/chroot /harddisk /usr/bin/touch /lib/modules/%s-smp/modules.dep",
		KERNEL_VERSION);
	mysystem(commandstring);

	/* Rename uname */
	rename ("/harddisk/bin/uname.bak", "/harddisk/bin/uname");

	/* *always* write disk configuration */
	if (!(write_disk_configs(&hdparams))){
	  errorbox(ctr[TR_ERROR_WRITING_CONFIG]);
	  goto EXIT;
	}

	/* mount proc filesystem */
	mysystem("mkdir /harddisk/proc");
	mysystem("/bin/mount -t proc none /harddisk/proc");
	mysystem("/bin/mount --bind /dev /harddisk/dev");



	/* if we detected SCSI then fixup */
	/* doesn't really work cause it sometimes creates a ramdisk on ide systems */
/*	mysystem("/bin/probecntrl.sh");
	if ((handle = fopen("/cntrldriver", "r")))
	{
		char *driver;
			fgets(line, STRING_SIZE-1, handle);
			fclose(handle);
		line[strlen(line) - 1] = 0;
		driver = strtok(line, ".");
		fprintf(flog, "Detected SCSI driver %s\n",driver);
		if (strlen(driver) > 1) {
			fprintf(flog, "Fixing up ipfirerd.img\n");
			mysystem("/sbin/chroot /harddisk /sbin/modprobe loop");
			mkdir("/harddisk/initrd", S_IRWXU|S_IRWXG|S_IRWXO);
			snprintf(commandstring, STRING_SIZE, "/sbin/chroot /harddisk /sbin/mkinitrd --with=scsi_mod --with=%s --with=sd_mod --with=sr_mod --with=libata /boot/ipfirerd.img %s", driver, KERNEL_VERSION);
			runcommandwithstatus(commandstring, ctr[TR_BUILDING_INITRD]);
			snprintf(commandstring, STRING_SIZE, "/sbin/chroot /harddisk /sbin/mkinitrd --with=scsi_mod --with=%s --with=sd_mod --with=sr_mod --with=libata /boot/ipfirerd-smp.img %s-smp", driver, KERNEL_VERSION);
			runcommandwithstatus(commandstring, ctr[TR_BUILDING_INITRD]);
			mysystem("/sbin/chroot /harddisk /bin/mv /boot/grub/scsigrub.conf /boot/grub/grub.conf");
		}
	} */

	/* Build cache lang file */
	snprintf(commandstring, STRING_SIZE, "/sbin/chroot /harddisk /usr/bin/perl -e \"require '" CONFIG_ROOT "/lang.pl'; &Lang::BuildCacheLang\"");
	if (runcommandwithstatus(commandstring, ctr[TR_INSTALLING_LANG_CACHE]))
	{
		errorbox(ctr[TR_UNABLE_TO_INSTALL_LANG_CACHE]);
		goto EXIT;
	}

	if (raid_disk)
		sprintf(string, "root=%sp3", hdparams.devnode);
	else
		sprintf(string, "root=%s3", hdparams.devnode);
	replace( "/harddisk/boot/grub/grub.conf", "root=ROOT", string);
	replace( "/harddisk/boot/grub/grubbatch", "DEVICE", hdparams.devnode);

	/* restore permissions */
	chmod("/harddisk/boot/grub/grubbatch", S_IXUSR | S_IRUSR | S_IXGRP | S_IRGRP | S_IXOTH | S_IROTH);

	snprintf(commandstring, STRING_SIZE, 
		 "/sbin/chroot /harddisk /boot/grub/grubbatch");
	if (runcommandwithstatus(commandstring, ctr[TR_INSTALLING_GRUB])) {
		errorbox(ctr[TR_UNABLE_TO_INSTALL_GRUB]);
		goto EXIT;
	}

	/* Update /etc/fstab */
	replace( "/harddisk/etc/fstab", "DEVICE", hdparams.devnode);

	/* Install bootsplash */
	mysystem("/bin/installbootsplash.sh");

	mysystem("ln -s grub.conf /harddisk/boot/grub/menu.lst");
	mysystem("umount /harddisk/proc");
	mysystem("umount /harddisk/dev");

	if (!unattended) {
		sprintf(message, ctr[TR_CONGRATULATIONS_LONG],
				NAME, SNAME, SNAME, NAME, NAME, NAME);
		newtWinMessage(ctr[TR_CONGRATULATIONS], ctr[TR_OK], message);
	}
	         
	allok = 1;

EXIT:
	fprintf(flog, "Install program ended.\n");	
	fflush(flog);
	fclose(flog);

	if (!(allok))
		newtWinMessage(title, ctr[TR_OK], ctr[TR_PRESS_OK_TO_REBOOT]);	
	
	newtFinished();
	
	freekeyvalues(ethernetkv);

	if (allok && !allok_fastexit)
	{
		/* /proc is needed by the module checker.  We have to mount it
		 * so it can be seen by setup, which is run chrooted. */
		if (system("/bin/mount proc -t proc /harddisk/proc"))
			printf("Unable to mount proc in /harddisk.");
		else
		{

			if (!unattended) {
			    if (system("/sbin/chroot /harddisk /usr/local/sbin/setup /dev/tty2 INSTALL"))
				    printf("Unable to run setup.\n");
			}
			else {
			    fprintf(flog, "Entering unattended setup\n");
			    unattended_setup(unattendedkv);
			    snprintf(commandstring, STRING_SIZE, "/bin/sleep 10");
			    runcommandwithstatus(commandstring, "Unattended installation finished, system will reboot");
			}

			if (system("/bin/umount /harddisk/proc"))
				printf("Unable to umount /harddisk/proc.\n");
		}
	}

	fcloseall();

	if (swap_file) {
		if (raid_disk)
			snprintf(commandstring, STRING_SIZE, "/bin/swapoff %sp2", hdparams.devnode);
		else
			snprintf(commandstring, STRING_SIZE, "/bin/swapoff %s2", hdparams.devnode);
	}

	newtFinished();

	system("/bin/umount /harddisk/var");
	system("/bin/umount /harddisk/boot");
	system("/bin/umount /harddisk");
	  
	system("/etc/halt");

	return 0;
}
