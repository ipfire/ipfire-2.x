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
#define INST_FILECOUNT 6600
#define UNATTENDED_CONF "/cdrom/data/unattended.conf"

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

int generate_packages_list(char *packages, const char *rpmdir, const char *source) {

	FILE *fd=NULL;
	char buffer[STRING_SIZE];
	bzero(buffer, sizeof(buffer));

	if ((fd = fopen(source, "r")) == NULL) {
		(void) fprintf(flog, "Packages file %s not found\n", source);
		return -1;
	}
	while (fgets(buffer, sizeof(buffer), fd) != NULL) {
		int length = -1;
		length = strlen(buffer)-1;
		if (length<=0) {
			continue;
		}
		if (buffer[length] == '\n') {
			buffer[length]='\0';
		}
		length = snprintf(packages, STRING_SIZE, "%s %s/%s", strdup(packages), rpmdir, buffer);
		if ((length <0) || (length >STRING_SIZE)) {
			(void) fprintf(flog, "rpm command line too long: %d\n%s", length, packages);
			return -1;
		}
	}
	if (ferror(fd)) {
		(void) fprintf(flog, "Error reading file\n");
		(void) fclose(fd);
		return -1;
	}
	(void) fclose(fd);
	return 0;
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
    char green_address[STRING_SIZE];
    char green_netmask[STRING_SIZE];
    char green_netaddress[STRING_SIZE];
    char green_broadcast[STRING_SIZE];
    char root_password[STRING_SIZE];
    char admin_password[STRING_SIZE];
    char serial_console[STRING_SIZE];
    char reversesort[STRING_SIZE];

    findkey(unattendedkv, "DOMAINNAME", domainname);
    findkey(unattendedkv, "HOSTNAME", hostname);
    findkey(unattendedkv, "KEYMAP", keymap);
    findkey(unattendedkv, "LANGUAGE", language);
    findkey(unattendedkv, "TIMEZONE", timezone);
    findkey(unattendedkv, "GREEN_ADDRESS", green_address);
    findkey(unattendedkv, "GREEN_NETMASK", green_netmask);
    findkey(unattendedkv, "GREEN_NETADDRESS", green_netaddress);
    findkey(unattendedkv, "GREEN_BROADCAST", green_broadcast);
    findkey(unattendedkv, "ROOT_PASSWORD", root_password);
    findkey(unattendedkv, "ADMIN_PASSWORD", admin_password);
    findkey(unattendedkv, "SERIAL_CONSOLE", serial_console);
    findkey(unattendedkv, "REVERSE_NICS", reversesort);

    /* write main/settings. */
    replacekeyvalue(mainsettings, "DOMAINNAME", domainname);
    replacekeyvalue(mainsettings, "HOSTNAME", hostname);
    replacekeyvalue(mainsettings, "KEYMAP", keymap);
    replacekeyvalue(mainsettings, "LANGUAGE", language);
    replacekeyvalue(mainsettings, "TIMEZONE", timezone);
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
    replacekeyvalue(ethernetkv, "GREEN_DEV", "br0");
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

    if (strcmp(serial_console, "yes") != 0) {
	    snprintf(commandstring, STRING_SIZE,
		     "/bin/chroot /harddisk /bin/sed -i -e \"s/^s0/#s0/\" /etc/inittab");
	    if (mysystem(commandstring)) {
		    errorbox("unattended: ERROR modifying inittab");
		    return 0;    
	    }

	    snprintf(commandstring, STRING_SIZE,
		     "/bin/chroot /harddisk /bin/sed -i -e \"s/^serial/#serial/; s/^terminal/#terminal/\" /boot/grub/grub.conf");
	    if (mysystem(commandstring)) {
		    errorbox("unattended: ERROR modifying inittab");
		    return 0;
	    }
    }

    /* set reverse sorting of interfaces */
    if (strcmp(reversesort, "yes") == 0) {
	    mysystem("/bin/touch /harddisk/var/ipfire/ethernet/reverse_nics");
    }

    /* set root password */
    fprintf(flog, "unattended: setting root password\n");
    
    snprintf(commandstring, STRING_SIZE,
	    "/bin/chroot /harddisk /bin/sh -c \"echo 'root:%s' | /usr/sbin/chpasswd\"", root_password);
    if (mysystem(commandstring)) {
	errorbox("unattended: ERROR setting root password");
	return 0;
    }
    
    /* set admin password */
    fprintf(flog, "unattended: setting admin password\n");
    snprintf(commandstring, STRING_SIZE,
	    "/bin/chroot /harddisk /usr/bin/htpasswd -c -m -b " CONFIG_ROOT "/auth/users admin '%s'", admin_password);
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
	long log_partition, boot_partition, root_partition, swap_file;
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
		if (strstr (line, "nopcmcia") == NULL) {
			fprintf(flog, "Initializing PCMCIA controllers.\n");
			pcmcia = initialize_pcmcia();
			if (pcmcia) {
				fprintf (flog, "Detected PCMCIA Controller: %s.\n", pcmcia);
				sprintf(commandstring, "/sbin/modprobe %s", pcmcia);
				mysystem("/sbin/modprobe pcmcia_core");
				mysystem(commandstring);
				mysystem("/sbin/modprobe ds");
				/* pcmcia netcard drivers are not available from Boot floppy,
				 * they will be loaded from Drivers floppy later */
			} else {
				fprintf (flog, "Detected No PCMCIA Controller.\n");
			}
		} else {
			fprintf(flog, "Skipping PCMCIA detection.\n");
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
	    runcommandwithstatus("/bin/beep -f 450 -r 10 -D 800 -n -f 900 -l 1000", "WARNING: Unattended installation will start in 10 seconds...");
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

	newtDrawRootText(14, 0, NAME " v" VERSION " - " SLOGAN );
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
	if ((handle = fopen("/source_device", "r")) == NULL) {
	    errorbox("ERROR reading source_device");
	}
	fgets(sourcedrive, 5, handle);
	fprintf(flog, "Source drive: %s\n", sourcedrive);
	fclose(handle);
	
	if (installtype == CDROM_INSTALL) {
	    snprintf(cdromparams.devnode, STRING_SIZE, "/dev/%s", sourcedrive);
	    cdromparams.module = 0;
	    fprintf(flog, "Source device: %s\n", cdromparams.devnode);
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
	sprintf(commandstring, "/bin/sfdisk -s /dev/%s > /disksize 2> /dev/null", harddrive);
	system(commandstring);

	/* Calculate amount of disk space */
        if ((handle = fopen("/disksize", "r")))
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

	boot_partition = 10; /* in MB */
	current_free = maximum_free - boot_partition - swap_file;

	root_partition = current_free / 3 ;
	if (current_free < 400) {
		errorbox(ctr[TR_DISK_TOO_SMALL]);
		goto EXIT;
	}

	current_free = current_free - root_partition;
	if (!swap_file) {
		root_partition = root_partition + swap_file;
	}

	log_partition = current_free;

	fprintf(flog, "boot = %ld, swap = %ld, mylog = %ld, root = %ld\n",
		boot_partition, swap_file, log_partition, root_partition);

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

	mysystem("/bin/udevstart");

	if (raid_disk)
		snprintf(commandstring, STRING_SIZE, "/bin/mke2fs -T ext3 -c %sp1", hdparams.devnode);	
	else
		snprintf(commandstring, STRING_SIZE, "/bin/mke2fs -T ext3 -c %s1", hdparams.devnode);
	if (runcommandwithstatus(commandstring, ctr[TR_MAKING_BOOT_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM]);
		goto EXIT;
	}

	if (swap_file) {
		if (raid_disk)
			snprintf(commandstring, STRING_SIZE, "/bin/mkswap %sp2", hdparams.devnode);	
		else
			snprintf(commandstring, STRING_SIZE, "/bin/mkswap %s2", hdparams.devnode);
		if (runcommandwithstatus(commandstring, ctr[TR_MAKING_SWAPSPACE]))
		{
			errorbox(ctr[TR_UNABLE_TO_MAKE_SWAPSPACE]);
			goto EXIT;
		}
	}

	if (raid_disk)
		snprintf(commandstring, STRING_SIZE, "/bin/mke2fs -T ext3 %sp3", hdparams.devnode);	
	else
		snprintf(commandstring, STRING_SIZE, "/bin/mke2fs -T ext3 %s3", hdparams.devnode);	

	if (runcommandwithstatus(commandstring, ctr[TR_MAKING_ROOT_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM]);
		goto EXIT;
	}

	if (raid_disk)
		snprintf(commandstring, STRING_SIZE, "/bin/mke2fs -T ext3 %sp4", hdparams.devnode);	
	else
		snprintf(commandstring, STRING_SIZE, "/bin/mke2fs -T ext3 %s4", hdparams.devnode);	

	if (runcommandwithstatus(commandstring, ctr[TR_MAKING_LOG_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM]);
		goto EXIT;
	}

	/* Mount harddisk. */
	if (raid_disk)
		snprintf(commandstring, STRING_SIZE, "/sbin/mount %sp3 /harddisk", hdparams.devnode);
	else
		snprintf(commandstring, STRING_SIZE, "/sbin/mount %s3 /harddisk", hdparams.devnode);
	if (runcommandwithstatus(commandstring, ctr[TR_MOUNTING_ROOT_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM]);
		goto EXIT;
	}

	mkdir("/harddisk/boot", S_IRWXU|S_IRWXG|S_IRWXO);
	mkdir("/harddisk/var", S_IRWXU|S_IRWXG|S_IRWXO);
	mkdir("/harddisk/var/log", S_IRWXU|S_IRWXG|S_IRWXO);
	
	if (raid_disk)
		snprintf(commandstring, STRING_SIZE, "/sbin/mount %sp1 /harddisk/boot", hdparams.devnode);
	else
		snprintf(commandstring, STRING_SIZE, "/sbin/mount %s1 /harddisk/boot", hdparams.devnode);

	if (runcommandwithstatus(commandstring, ctr[TR_MOUNTING_BOOT_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM]);
		goto EXIT;
	}
	if (swap_file) {
		if (raid_disk)
			snprintf(commandstring, STRING_SIZE, "/bin/swapon %sp2", hdparams.devnode);
		else
			snprintf(commandstring, STRING_SIZE, "/bin/swapon %s2", hdparams.devnode);
		if (runcommandwithstatus(commandstring, ctr[TR_MOUNTING_SWAP_PARTITION]))
		{
			errorbox(ctr[TR_UNABLE_TO_MOUNT_SWAP_PARTITION]);
			goto EXIT;
		}
	}
	if (raid_disk)
		snprintf(commandstring, STRING_SIZE, "/sbin/mount %sp4 /harddisk/var", hdparams.devnode);
	else
		snprintf(commandstring, STRING_SIZE, "/sbin/mount %s4 /harddisk/var", hdparams.devnode);
	if (runcommandwithstatus(commandstring, ctr[TR_MOUNTING_LOG_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM]);
		goto EXIT;
	}



	if (installtype == CDROM_INSTALL)
	{	
		/* First look for an IDE CDROM. */
		if (!(cdletter = findidetype(IDE_CDROM)))
		{
			/* If we have a USB attached CDROM then it will
			 * have already appeared at /dev/scd0, so we
			 * try to access it first, before asking for the
			 * SCSI drivers disk.
			 */
			if (!(try_scsi("scd0"))) {
				sprintf(insertmessage, ctr[TR_INSERT_FLOPPY], NAME" SCSI");
				rc = newtWinChoice(title, ctr[TR_OK], ctr[TR_CANCEL], insertmessage);
				if (rc != 1)
				{
					errorbox(ctr[TR_INSTALLATION_CANCELED]);
					goto EXIT;
				}
				
				if (runcommandwithstatus("/bin/tar -C / -xvzf /dev/floppy", ctr[TR_EXTRACTING_MODULES]))
				{
					errorbox(ctr[TR_UNABLE_TO_EXTRACT_MODULES]);
					goto EXIT;
				}
		
				if (pcmcia)
				{
					/* trying to support SCSI pcmcia :-) */
					runcommandwithstatus("cardmgr -o -c /etc/pcmcia/scsi", 
						ctr[TR_LOADING_PCMCIA]);
					if (try_scsi("scd0"))
						pcmcia_cdrom = 1;
				}
	
				/* try loading all SCSI modules with default options */
				/* Should expand this to allow options later though */
				if (!pcmcia_cdrom)
				    runcommandwithstatus("/bin/probehw.sh",
					ctr[TR_PROBING_HARDWARE]);
	
				/* If it fails, give up. */
				if (!(try_scsi("scd0"))) {
					errorbox(ctr[TR_NO_CDROM]);
					goto EXIT;
				}
			}

			sprintf(sourcedrive, "scd0");
			scsi_cdrom = 1;
		} else {
			sprintf(sourcedrive, "hd%c", cdletter);
			ide_cdrom = 1;
		}

		snprintf(cdromparams.devnode, STRING_SIZE, "/dev/%s", sourcedrive);
		cdromparams.module = 0;
		
		sprintf(insertmessage, ctr[TR_INSERT_CDROM], NAME);
		strcpy (insertdevnode, cdromparams.devnode);
	}
	else
	{
		/* If we've done a PXE boot, we can skip the Drivers floppy,
		 * as we've already got the modules in our instroot.gz */
        	if (!(handle = fopen("/CDROMBOOT", "r"))) {
			sprintf(insertmessage, ctr[TR_INSERT_FLOPPY], NAME);
			strcpy (insertdevnode , "/dev/floppy");
		} else {
			fclose(handle);
			cdmounted = 1;
	      		unmount_before = 1;
		}
	}

	if (scsi_cdrom || ide_cdrom) {
		/* Try to mount /cdrom in a loop. */
		snprintf(commandstring, STRING_SIZE, "/bin/mount -o ro %s /cdrom", insertdevnode);
		while (!cdmounted)
		{
			rc = newtWinChoice(title, ctr[TR_OK], ctr[TR_CANCEL], insertmessage);
			if (rc != 1)
			{
				errorbox(ctr[TR_INSTALLATION_CANCELED]);
				goto EXIT;
			}
			if (!(mysystem(commandstring))) {
				handle = fopen ("/cdrom/" SNAME "-" VERSION ".tgz", "r");
				if (handle != NULL) {
					fclose (handle);
       		 			cdmounted = 1;
					/* If we've booted from CDROM, then
					 * we've already got the drivers,
					 * so we can skip this unpack. */
        				if (!(handle = fopen("/CDROMBOOT", "r"))) {
						sprintf(string, "/bin/tar -C / -xvzf /cdrom/images/drivers-%s.img", VERSION); 
						if (runcommandwithprogress(60, 4, title, 
							string,
							175, ctr[TR_EXTRACTING_MODULES]))
						{
							errorbox(ctr[TR_UNABLE_TO_EXTRACT_MODULES]);
			
			 				goto EXIT;
						}
					} else 
						fclose(handle);
       		 		} else {
       		 			mysystem ("/bin/umount /cdrom");
        			}
			}
		}
	} else {
		snprintf(commandstring, STRING_SIZE, "/bin/tar -C / -xvzf /dev/floppy");
		while (!cdmounted)
		{
			rc = newtWinChoice(title, ctr[TR_OK], ctr[TR_CANCEL], insertmessage);
			if (rc != 1)
			{
				errorbox(ctr[TR_INSTALLATION_CANCELED]);
				goto EXIT;
			}
			if (runcommandwithprogress(60, 4, title, 
				commandstring,
				175, ctr[TR_EXTRACTING_MODULES]))
			{
#if 0 /* disable this, so we allow for people putting in the wrong disk */
				errorbox(ctr[TR_UNABLE_TO_EXTRACT_MODULES]);
				goto EXIT;
#endif
			}
			else
			{
				handle = fopen ("/bin/mke2fs", "r");
				if (handle != NULL) {
					fclose (handle);
       		 			cdmounted = 1;
        			}
			}
		}
	}

	/* PCMCIA controller is already detected
	 * On Boot floppy, we didn't have the PCMCIA drivers
	 * so load them now because they are installed from Drivers. */
	if (!(handle = fopen("/CDROMBOOT", "r"))) {
		if (strstr (line, "nopcmcia") == NULL) {
			fprintf(flog,"Floppy boot detected, loading PCMCIA drivers.\n");
			if (pcmcia) {
				fprintf (flog, "Detected PCMCIA Controller: %s.\n", pcmcia);
				sprintf(commandstring, "/sbin/modprobe %s", pcmcia);
				mysystem("/sbin/modprobe pcmcia_core");
				mysystem(commandstring);
				mysystem("/sbin/modprobe ds");
			} else {
				fprintf (flog, "Detected No PCMCIA Controller.\n");
			}
		} else {
			fprintf(flog, "Skipping PCMCIA detection.\n");
		}
		if (strstr (line, "nousb") == NULL) {
			fprintf(flog, "Initializing USB controllers.\n");
			initialize_usb();
		} else {
			fprintf(flog, "Skipping USB detection.\n");
		}
	} else
		fclose(handle);

 	/* Configure the network now! */
	if (installtype == URL_INSTALL)
	{
	        /* Network driver and params. */
	        if (!(networkmenu(ethernetkv)))
	        {
		        errorbox(ctr[TR_NETWORK_SETUP_FAILED]);
		        goto EXIT;
	        }

		/* Check for ipfire-<VERSION>.tgz */
		if (!(checktarball(SNAME "-" VERSION ".tgz")))
		{
			errorbox(ctr[TR_NO_IPCOP_TARBALL_FOUND]);
			goto EXIT;
		}
	}

	/* Get device for the HD.  This has to succeed. */
	if (!(hdletter = findidetype(IDE_HD)))
	{
		if (installtype == URL_INSTALL)
		{
			/* If we've done a PXE boot, we can skip the SCSI
		 	 * floppy as we've already got the modules in our 
			 * instroot.gz */
        		if (!(handle = fopen("/CDROMBOOT", "r"))) 
			{
				/* search img where it is on a mounted loop iso */
				sprintf(string, "images/scsidrv-%s.img", VERSION);
				if (!(checktarball(string)))
				{
					/* Couldn't find the SCSI drivers on the URL page,
					 * so after 3 failed attempts, ask the user for the
					 * SCSI drivers floppy disk. */
					errorbox(ctr[TR_NO_SCSI_IMAGE_FOUND]);
					sprintf(insertmessage, ctr[TR_INSERT_FLOPPY], NAME" SCSI");
					rc = newtWinChoice(title, ctr[TR_OK], ctr[TR_CANCEL], insertmessage);
					if (rc != 1)
					{
						errorbox(ctr[TR_INSTALLATION_CANCELED]);
						goto EXIT;
					}

					if (runcommandwithstatus("/bin/tar -C / -xvzf /dev/floppy", ctr[TR_EXTRACTING_MODULES]))
					{
						errorbox(ctr[TR_UNABLE_TO_EXTRACT_MODULES]);
						goto EXIT;
					}
				} else {
					/* unpack... */
					snprintf(commandstring, STRING_SIZE,
						"/bin/wget -O - %s/%s | /bin/tar -C / -xvzf -",
						url, string);
					if (runcommandwithprogress(60, 4, title, commandstring,
						4500, ctr[TR_INSTALLING_FILES]))
					{
						errorbox(ctr[TR_UNABLE_TO_INSTALL_FILES]);
						goto EXIT;
					}
				}
			} else
				fclose(handle);
		} else {
			if (ide_cdrom) {
				sprintf(string, "/bin/tar -C / -xvzf /cdrom/images/scsidrv-%s.img", VERSION);
				if (runcommandwithstatus(string, ctr[TR_EXTRACTING_MODULES]))
				{
					errorbox(ctr[TR_UNABLE_TO_EXTRACT_MODULES]);
					goto EXIT;
				}
			}
		}

		if (!scsi_cdrom) {

#if 0 /* not yet */
			if (pcmcia)
			{
				/* trying to support SCSI pcmcia :-) */
				runcommandwithstatus("cardmgr -o -c /etc/pcmcia/scsi", 
					ctr[TR_LOADING_PCMCIA]);
				if (try_scsi("sda"))
					pcmcia_disk = 1;
			}
#endif

			/* try loading all SCSI modules with default options */
			/* Should expand this to allow options later though */
			if (!pcmcia_disk)
				runcommandwithstatus("/bin/probehw.sh",
					ctr[TR_PROBING_HARDWARE]);
		}
	
		/* Need to clean this up at some point */
		if (!try_scsi("sda")) {
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
			sprintf(harddrive, "sda");
		}
		scsi_disk = 1;
	} else
		sprintf(harddrive, "hd%c", hdletter);

	/* Make the hdparms struct and print the contents. */
	snprintf(hdparams.devnode, STRING_SIZE, "/dev/%s", harddrive);
	hdparams.module = 0;

	rc = newtWinChoice(title, ctr[TR_OK], ctr[TR_CANCEL],
		ctr[TR_PREPARE_HARDDISK], hdparams.devnode);
	if (rc != 1)
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
	sprintf(commandstring, "/bin/sfdisk -s /dev/%s > /disksize 2> /dev/null", harddrive);
	system(commandstring);

	/* Calculate amount of disk space */
        if ((handle = fopen("/disksize", "r")))
        {
           	fgets(line, STRING_SIZE-1, handle);
            	if (sscanf (line, "%s", string)) {
			maximum_free = atoi(string) / 1024;
            	}
            	fclose(handle);
        }
	
	fprintf(flog, "maximum_free = %d, memory = %d", 
		maximum_free, memory);
	
	/* If you need more than this, you should really add physical memory */
	/* Minimum: 192 = 64 real + 128 swap */
	swap_file = memory < 64 ? 2 * memory : 192 - memory ;
	swap_file = swap_file < 32 ? 32 : swap_file ;

	if (maximum_free < 135 + swap_file )
	{
		if (maximum_free < 135) {
			errorbox(ctr[TR_DISK_TOO_SMALL]);
			goto EXIT;
		}

		rc = newtWinChoice(title, ctr[TR_OK], ctr[TR_CANCEL], ctr[TR_CONTINUE_NO_SWAP]);
		if (rc != 1)
			goto EXIT;
		swap_file = 0;
	}

	boot_partition = 20; /* in MB */
	current_free = maximum_free - boot_partition - swap_file;

	/* Give more place for add-on, extend root to 25% of current_free, upper limit to 8 gigas */
	root_partition = current_free / 4 ;
	root_partition = root_partition > 8192 ? 8192 : root_partition ;
	root_partition = current_free < 860 ? 235 : root_partition;
	root_partition = current_free < 380 ? 110 : root_partition;

	current_free = current_free - root_partition;
	root_partition = root_partition + swap_file;

	log_partition = current_free;

	fprintf(flog, "boot = %d, swap = %d, mylog = %d, root = %d\n",
		boot_partition, swap_file, log_partition, root_partition);


#ifdef __alpha__
	fdisk = 1;
#endif

	if (fdisk) {
		rc = newtWinChoice(title, ctr[TR_OK], ctr[TR_CANCEL], "NOW FDISK");
		if (rc != 1)
			goto EXIT;
	} else {
#ifdef __i386__
		handle = fopen("/tmp/partitiontable", "w");

		fprintf(handle, ",%d,83,*\n,%d,83,\n,0,0,\n,,83,\n",
			boot_partition, log_partition);

		fclose(handle);		

		snprintf(commandstring, STRING_SIZE, "/bin/sfdisk -uM %s < /tmp/partitiontable", hdparams.devnode);
		if (runcommandwithstatus(commandstring, ctr[TR_PARTITIONING_DISK]))
		{
			errorbox(ctr[TR_UNABLE_TO_PARTITION]);
			goto EXIT;
		}
#endif
	}

	if (raid_disk)
		snprintf(commandstring, STRING_SIZE, "/bin/mke2fs -m 0 -j %sp1", hdparams.devnode);
	else
		snprintf(commandstring, STRING_SIZE, "/bin/mke2fs -m 0 -j %s1", hdparams.devnode);
	if (runcommandwithstatus(commandstring, ctr[TR_MAKING_BOOT_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM]);
		goto EXIT;
	}
	if (raid_disk)
		snprintf(commandstring, STRING_SIZE, "/bin/mke2fs -j %sp2", hdparams.devnode);
	else
		snprintf(commandstring, STRING_SIZE, "/bin/mke2fs -j %s2", hdparams.devnode);
	if (runcommandwithstatus(commandstring, ctr[TR_MAKING_LOG_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MAKE_LOG_FILESYSTEM]);
		goto EXIT;
	}
	if (raid_disk)
		snprintf(commandstring, STRING_SIZE, "/bin/mke2fs -m 1 -j %sp4", hdparams.devnode);
	else
		snprintf(commandstring, STRING_SIZE, "/bin/mke2fs -m 1 -j %s4", hdparams.devnode);

	if (runcommandwithstatus(commandstring, ctr[TR_MAKING_ROOT_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM]);
		goto EXIT;
	}
	/* Mount harddisk. */
	if (raid_disk)
		snprintf(commandstring, STRING_SIZE, "/sbin/mount -t ext2 %sp4 /harddisk", hdparams.devnode);
	else
		snprintf(commandstring, STRING_SIZE, "/sbin/mount -t ext2 %s4 /harddisk", hdparams.devnode);
	if (runcommandwithstatus(commandstring, ctr[TR_MOUNTING_ROOT_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM]);
		goto EXIT;
	}
	/* Make swapfile */
	if (swap_file) {
		snprintf(commandstring, STRING_SIZE, "/bin/dd if=/dev/zero of=/harddisk/swapfile bs=1024k count=%d", swap_file);
		if (runcommandwithstatus(commandstring, ctr[TR_MAKING_SWAPSPACE]))
		{
			errorbox(ctr[TR_UNABLE_TO_MAKE_SWAPSPACE]);
			goto EXIT;
		}
		snprintf(commandstring, STRING_SIZE, "/bin/mkswap /harddisk/swapfile");
		if (runcommandwithstatus(commandstring, ctr[TR_MAKING_SWAPSPACE]))
		{
			errorbox(ctr[TR_UNABLE_TO_MAKE_SWAPSPACE]);
			goto EXIT;
		}
	}
	mkdir("/harddisk/boot", S_IRWXU|S_IRWXG|S_IRWXO);
	mkdir("/harddisk/var", S_IRWXU|S_IRWXG|S_IRWXO);	
	mkdir("/harddisk/var/log", S_IRWXU|S_IRWXG|S_IRWXO);
	
	if (raid_disk)
		snprintf(commandstring, STRING_SIZE, "/sbin/mount -t ext2 %sp1 /harddisk/boot", hdparams.devnode);
	else
		snprintf(commandstring, STRING_SIZE, "/sbin/mount -t ext2 %s1 /harddisk/boot", hdparams.devnode);

	if (runcommandwithstatus(commandstring, ctr[TR_MOUNTING_BOOT_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM]);
		goto EXIT;
	}
	if (swap_file) {
		snprintf(commandstring, STRING_SIZE, "/bin/swapon /harddisk/swapfile");
		if (runcommandwithstatus(commandstring, ctr[TR_MOUNTING_SWAP_PARTITION]))
		{
			errorbox(ctr[TR_UNABLE_TO_MOUNT_SWAP_PARTITION]);
			goto EXIT;
		}
	}
	if (raid_disk)
		snprintf(commandstring, STRING_SIZE, "/sbin/mount -t ext2 %sp2 /harddisk/var/log", hdparams.devnode);
	else
		snprintf(commandstring, STRING_SIZE, "/sbin/mount -t ext2 %s2 /harddisk/var/log", hdparams.devnode);
	if (runcommandwithstatus(commandstring, ctr[TR_MOUNTING_LOG_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM]);
		goto EXIT;
	}
	
 	/* Either use tarball from cdrom or download. */
	if (installtype == CDROM_INSTALL)
		snprintf(commandstring, STRING_SIZE, 
			"/bin/tar -C /harddisk -xvzf /cdrom/" SNAME "-" VERSION ".tgz");
	else
		snprintf(commandstring, STRING_SIZE, 
			"/bin/wget -O - %s/" SNAME "-" VERSION ".tgz | /bin/tar -C /harddisk -xvzf -", url);
	
	/* if (runcommandwithprogress(60, 4, title, commandstring, 4600,
	 *	ctr[TR_INSTALLING_FILES]))
	 * {
	 *	errorbox(ctr[TR_UNABLE_TO_INSTALL_FILES]);
	 *	goto EXIT;
	 * }
	 */

	if (runcommandwithstatus(commandstring, ctr[TR_INSTALLING_FILES]))
	{
		errorbox(ctr[TR_UNABLE_TO_INSTALL_FILES]);
		goto EXIT;
	}
		
	/* Save USB controller type to modules.conf */
	write_usb_modules_conf();

	/* touch the modules.dep files */
	snprintf(commandstring, STRING_SIZE, 
		"/bin/chroot /harddisk /bin/touch /lib/modules/%s/modules.dep",
		KERNEL_VERSION);
	mysystem(commandstring);
#ifdef __i386__
	snprintf(commandstring, STRING_SIZE, 
		"/bin/chroot /harddisk /bin/touch /lib/modules/%s-smp/modules.dep",
		KERNEL_VERSION);
	mysystem(commandstring);
#endif

	/* Rename uname */
	rename ("/harddisk/bin/uname.bak", "/harddisk/bin/uname");

	/* Write PCMCIA Config */
	if (pcmcia) {
		handle = fopen("/harddisk/etc/modules.conf", "a");
		if (handle != NULL) {
			fprintf (handle, "# PCMCIA Settings\n");
			fprintf (handle, "alias pcmcia-controller %s\n", pcmcia);
			fclose(handle);
		}
	}

	handle = fopen("/harddisk/etc/pcmcia.conf", "w");
	if (handle != NULL) {
		if (pcmcia) {
			fprintf (handle, "PCMCIA=yes\n");
			fprintf (handle, "PCIC=%s\n", pcmcia);
		} else {
			fprintf (handle, "PCMCIA=no\n");
			fprintf (handle, "PCIC=\n");
		}
		fprintf (handle, "CARDMGR_OPTS=\n");
		fprintf (handle, "SCHEME=\n");
        	fclose(handle);
	}

	/* *always* write disk configuration */
	if (!(write_disk_configs(&hdparams))){
	  errorbox(ctr[TR_ERROR_WRITING_CONFIG]);
	  goto EXIT;
	}

	/*  
	  Allow the user to restore their configuration from a floppy.
	  It uses tar.  If the tar fails for any reason, show user an
	  error and go back to the restore/skip question. This gives
	  the user the chance to have another go. */

#ifdef OLD_RESTORECFG	
RESTORE:
	/* set status variables to nonsense values */
	allok_fastexit = 0;
	/* loop until floppy succeeds or user skips out */
	while (1)
	{
	  sprintf(message, ctr[TR_RESTORE_CONFIGURATION], NAME);
	  if (newtWinChoice(title, ctr[TR_RESTORE], ctr[TR_SKIP], message) == 1)
	  {
	    /* Temporarily mount /proc under /harddisk/proc,
	     * run updfstab to locate the floppy, and unmount /harddisk/proc
	     * again.  This should be run each time the user tries to restore
	     * so it can properly detect removable devices */
	    if (mysystem("/bin/mount -n -t proc /proc /harddisk/proc")) {
	      errorbox(ctr[TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM]);
	      goto EXIT;
	    }
	    if (mysystem("/bin/chroot /harddisk /usr/sbin/updfstab")) {
	      errorbox(ctr[TR_UNABLE_TO_WRITE_ETC_FSTAB]);
	      goto EXIT;
	    }
	    mysystem("/bin/umount /harddisk/proc");

	    mkdir("/harddisk/tmp/ipcop", S_IRWXU|S_IRWXG|S_IRWXO);

	    /* Always extract to /tmp/ipcop for temporary extraction
	     * just in case floppy fails */

	    /* try a compressed backup first because it's quicker to fail.
	     * In exclude.system, files name must be without leading / or 
	     * on extraction, name will never match */
	    snprintf(commandstring, STRING_SIZE, 
		     "/bin/chroot /harddisk /bin/tar -X " CONFIG_ROOT "/backup/exclude.system -C /tmp/ipcop -xvzf /dev/floppy > %s 2> /dev/null", mylog);
	
	    statuswindow(45, 4, title, ctr[TR_INSTALLING_FILES]);
	    rc = system(commandstring);
	    
	    if (rc) {
	      /* if it's not compressed, try uncompressed first before failing*/
	      snprintf(commandstring, STRING_SIZE, 
		     "/bin/chroot /harddisk /bin/tar -X " CONFIG_ROOT "/backup/exclude.system -C /tmp/ipcop -xvf /dev/floppy > %s 2> /dev/null", mylog);
	      rc = system(commandstring);
	      if (rc) {
	    	newtPopWindow();
	        /* command failed trying to read from floppy */
	        errorbox(ctr[TR_UNABLE_TO_INSTALL_FILES]);
		
		/* remove badly restored files */
	        mysystem("/bin/chroot /harddisk /bin/rm -rf /tmp/ipcop");
		goto RESTORE;
	      } else {
	      	/* Now copy to correct location */
	    	mysystem("/bin/chroot /harddisk /bin/cp -af /tmp/ipcop/. /");
	        mysystem("/bin/chroot /harddisk /bin/rm -rf /tmp/ipcop");
	    	newtPopWindow();
	        allok_fastexit=1;

	        /* Upgrade necessary files from v1.2 to v1.3 to v1.4 */
	        upgrade_v12_v13();
	        upgrade_v130_v140();
	        break; /* out of loop at this point because floppy has
			successfully restored */
	      }
	    }
	    else { /* success */
	      /* Now copy to correct location */
	      mysystem("/bin/chroot /harddisk /bin/cp -af /tmp/ipcop/. /");
	      mysystem("/bin/chroot /harddisk /bin/rm -rf /tmp/ipcop");
	      newtPopWindow();
	      allok_fastexit=1;

	      /* Upgrade necessary files from v1.2 to v1.3 to v1.4 */
	      upgrade_v12_v13();
	      upgrade_v130_v140();
	      break; /* out of loop at this point because floppy has
			successfully restored */
	    }
	  }
	  else{  /* user chose to skip install from floppy */
	    if (installtype == CDROM_INSTALL){
	      /* if we installed from CD ROM then we didn't set up the
		 network interface yet.  Therefore, set up Network
		 driver and params just before we need them. */

	      if (!(networkmenu(ethernetkv))){
		/* network setup failed, tell the world */
		errorbox(ctr[TR_NETWORK_SETUP_FAILED]);
		goto EXIT;
	      }
	    }
	    break; /* out of loop because we succeeded with ethernet
		      set up and user is notrestarting from floppy*/
	  }
	}
#else	
	if (installtype == CDROM_INSTALL){
	 /* if we installed from CD ROM then we didn't set up the
	    network interface yet.  Therefore, set up Network
	    driver and params just before we need them. */

	if (!(networkmenu(ethernetkv))){
	/* network setup failed, tell the world */
	  errorbox(ctr[TR_NETWORK_SETUP_FAILED]);
	  goto EXIT;
	  }
	}
#endif
	
	/* Check the SQUID acl file exists, if not use our 1.4 copy */
	{
		FILE *aclreadfile;

		if (!(aclreadfile = fopen ("/harddisk" CONFIG_ROOT "/proxy/acl", "r"))) {
			rename ("/harddisk" CONFIG_ROOT "/proxy/acl-1.4",
				"/harddisk" CONFIG_ROOT "/proxy/acl");
		} else {
			unlink ("/harddisk" CONFIG_ROOT "/proxy/acl-1.4");
			fclose(aclreadfile);
		}
		chown  ("/harddisk" CONFIG_ROOT "/proxy/acl", 99, 99);
	}

	/* Build cache lang file */
	mysystem("/bin/chroot /harddisk /usr/bin/perl -e \"require '" CONFIG_ROOT "/lang.pl'; &Lang::BuildCacheLang\"");
	
	if (!allok_fastexit){
	  /* write ethernet and lang configs only if they have not
	     been restored from floppy already. */
	  if (!(write_ethernet_configs( ethernetkv))||
	      !(write_lang_configs(shortlangname))){
	    errorbox(ctr[TR_ERROR_WRITING_CONFIG]);
	    goto EXIT;
	  }
	}

	/* if we detected SCSI then fixup */
        if ((handle = fopen("/scsidriver", "r")))
        {
		char *driver;
           	fgets(line, STRING_SIZE-1, handle);
            	fclose(handle);
		line[strlen(line) - 1] = 0;
		driver = strtok(line, ".");
		fprintf(flog, "Detected SCSI driver %s\n",driver);
		if (strlen(driver) > 1) {
			fprintf(flog, "Fixing up ipfirerd.img\n");
			mysystem("/bin/chroot /harddisk /sbin/modprobe loop");
			mkdir("/harddisk/initrd", S_IRWXU|S_IRWXG|S_IRWXO);
  			snprintf(commandstring, STRING_SIZE, "/bin/chroot /harddisk /sbin/mkinitrd --with=scsi_mod --with=%s --with=sd_mod --with=sr_mod --with=libata --with=ataraid /boot/ipfirerd.img %s", driver, KERNEL_VERSION);
			runcommandwithstatus(commandstring, ctr[TR_BUILDING_INITRD]);
#ifdef __i386__
  			snprintf(commandstring, STRING_SIZE, "/bin/chroot /harddisk /sbin/mkinitrd --with=scsi_mod --with=%s --with=sd_mod --with=sr_mod --with=libata --with=ataraid /boot/ipfirerd-smp.img %s-smp", driver, KERNEL_VERSION);
			runcommandwithstatus(commandstring, ctr[TR_BUILDING_INITRD]);
			mysystem("/bin/chroot /harddisk /bin/mv /boot/grub/scsigrub.conf /boot/grub/grub.conf");
#endif
#ifdef __alpha__
			snprintf(commandstring, STRING_SIZE, "/bin/chroot /harddisk /bin/mv /boot/etc/scsiaboot.conf /boot/etc/aboot.conf");
			runcommandwithstatus(commandstring, ctr[TR_BUILDING_INITRD]);
#endif
		}
	}

#if 0 /* not yet */
 	if (pcmcia_disk)
	{
		fprintf(flog, "Detected SCSI driver PCMCIA\n");
		fprintf(flog, "Fixing up ipfirerd.img\n");
		mysystem("/bin/chroot /harddisk /sbin/modprobe loop");
		mkdir("/harddisk/initrd", S_IRWXU|S_IRWXG|S_IRWXO);
  		snprintf(commandstring, STRING_SIZE, "/bin/chroot /harddisk /sbin/pcinitrd -r %s /boot/ipfirerd.img", KERNEL_VERSION);
		mysystem(commandstring);
#ifdef __i386__
		mysystem("/bin/chroot /harddisk /bin/mv /boot/grub/scsigrub.conf /boot/grub/grub.conf");
#endif
#ifdef __alpha__
		mysystem("/bin/chroot /harddisk /bin/mv /boot/etc/scsiaboot.conf /boot/etc/aboot.conf");
#endif
	}
#endif

#ifdef __i386__
	replace( "/harddisk/boot/grub/grubbatch", "DEVICE", hdparams.devnode);
	/* restore permissions */
	chmod("/harddisk/boot/grub/grubbatch", S_IXUSR | S_IRUSR | S_IXGRP | S_IRGRP | S_IXOTH | S_IROTH);

	if (raid_disk)
		sprintf(string, "root=%sp4", hdparams.devnode);
	else
		sprintf(string, "root=%s4", hdparams.devnode);
	replace( "/harddisk/boot/grub/grub.conf", "root=ROOT", string);

	mysystem("/bin/chroot /harddisk /bin/mount -n -t proc none /proc");

	snprintf(commandstring, STRING_SIZE, "/bin/chroot /harddisk /boot/grub/grubbatch");

	if (runcommandwithstatus(commandstring, ctr[TR_INSTALLING_GRUB]))
	{
		errorbox(ctr[TR_UNABLE_TO_INSTALL_GRUB]);
		goto EXIT;
	}
	/* Set Bootsplash */
	mysystem("/bin/installbootsplash.sh");
	mysystem("/bin/chroot /harddisk /bin/umount -n /proc");
#endif
#ifdef __alpha__
	snprintf(commandstring, STRING_SIZE, "/bin/chroot /harddisk /sbin/swriteboot -f3 %s /boot/bootlx", hdparams.devnode);
	mysystem(commandstring);
	snprintf(commandstring, STRING_SIZE, "/bin/chroot /harddisk /sbin/abootconf %s 1", hdparams.devnode);
	mysystem(commandstring);
	if (raid_disk)
		sprintf(string, "root=%sp4", hdparams.devnode);
	else
		sprintf(string, "root=%s4", hdparams.devnode);
	replace( "/harddisk/boot/etc/aboot.conf", "root=ROOT", string);
#endif

	/* unmounting happens everywhere because there are places
	   which require device is to be unmounted under certain
	   circumstances.  This is the last place we can unmount
	   anything and still succeed. */

	if (!unmount_before && installtype == CDROM_INSTALL){
	  if (mysystem("/sbin/umount /cdrom"))
	    {
	      errorbox(ctr[TR_UNABLE_TO_UNMOUNT_CDROM]);
	      goto EXIT;
	    }
	}

	if (installtype == CDROM_INSTALL)
	{

		if (!(ejectcdrom(cdromparams.devnode)))
		{
			errorbox(ctr[TR_UNABLE_TO_EJECT_CDROM]);
			// goto EXIT;
		}
	}
	
	
	sprintf(message, ctr[TR_CONGRATULATIONS_LONG],
		NAME, SNAME, SNAME, NAME, NAME, NAME);
	newtWinMessage(ctr[TR_CONGRATULATIONS], ctr[TR_OK], message);
		
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
		if (system("/sbin/mount proc -t proc /harddisk/proc"))
			printf("Unable to mount proc in /harddisk.");
		else
		{
			if (system("/bin/chroot /harddisk /usr/local/sbin/setup /dev/tty2 INSTALL"))
				printf("Unable to run setup.\n");
			if (system("/sbin/umount /harddisk/proc"))
				printf("Unable to umount /harddisk/proc.\n");
		}
	}

	fcloseall();

	system("/bin/swapoff /harddisk/swapfile");
	system("/sbin/umount /harddisk/var/log");
	system("/sbin/umount /harddisk/boot");
	system("/sbin/umount /harddisk");
	  
	system("/etc/halt");

	return 0;
}
