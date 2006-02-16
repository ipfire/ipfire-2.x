/* SmoothWall install program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Contains main entry point, and misc functions.
 * 
 * $Id: main.c,v 1.63.2.64 2006/01/11 01:01:38 franck78 Exp $
 * 
 */
#include "install.h"

#define CDROM_INSTALL 0
#define URL_INSTALL 1

int raid_disk = 0;
FILE *flog = NULL;
char *mylog;
char **ctr;

char *pcmcia = NULL;
extern char url[STRING_SIZE];

/* 
    To include a translated string in the final installer, you must reference
    it here with a simplr comment. This save a lot a space in the installer
*/
/* TR_WELCOME */
/* TR_HELPLINE */
/* TR_OK */
/* TR_ERROR */
/* TR_SELECT_INSTALLATION_MEDIA_LONG */
/* TR_SELECT_INSTALLATION_MEDIA */
/* TR_CANCEL */
/* TR_INSERT_FLOPPY */
/* TR_INSTALLATION_CANCELED */
/* TR_EXTRACTING_MODULES */
/* TR_UNABLE_TO_EXTRACT_MODULES */
/* TR_LOADING_PCMCIA */
/* TR_PROBING_SCSI */
/* TR_NO_CDROM */
/* TR_INSERT_CDROM */
/* TR_USB_KEY_VFAT_ERR */
/* TR_NETWORK_SETUP_FAILED */
/* TR_NO_IPCOP_TARBALL_FOUND */
/* TR_NO_SCSI_IMAGE_FOUND */
/* TR_INSTALLING_FILES */
/* TR_UNABLE_TO_INSTALL_FILES */
/* TR_NO_HARDDISK */
/* TR_PREPARE_HARDDISK */
/* TR_DISK_TOO_SMALL */
/* TR_CONTINUE_NO_SWAP */
/* TR_PARTITIONING_DISK */
/* TR_UNABLE_TO_PARTITION */
/* TR_MAKING_BOOT_FILESYSTEM */
/* TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM */
/* TR_MAKING_LOG_FILESYSTEM */
/* TR_UNABLE_TO_MAKE_LOG_FILESYSTEM */
/* TR_MAKING_ROOT_FILESYSTEM */
/* TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM */
/* TR_MOUNTING_ROOT_FILESYSTEM */
/* TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM */
/* TR_MAKING_SWAPSPACE */
/* TR_UNABLE_TO_MAKE_SWAPSPACE */
/* TR_MOUNTING_SWAP_PARTITION */
/* TR_UNABLE_TO_MOUNT_SWAP_PARTITION */
/* TR_MOUNTING_BOOT_FILESYSTEM */
/* TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM */
/* TR_MOUNTING_LOG_FILESYSTEM */
/* TR_UNABLE_TO_MOUNT_LOG_FILESYSTEM */
/* TR_ERROR_WRITING_CONFIG */
/* TR_INSTALLING_GRUB */
/* TR_UNABLE_TO_INSTALL_GRUB */
/* TR_UNABLE_TO_UNMOUNT_CDROM */
/* TR_UNABLE_TO_EJECT_CDROM */
/* TR_CONGRATULATIONS_LONG */
/* TR_CONGRATULATIONS */
/* TR_PRESS_OK_TO_REBOOT */

// in nic.c
/* TR_CONFIGURE_NETWORKING */
/* TR_PROBE */
/* TR_SELECT */
/* TR_CONFIGURE_NETWORKING_LONG */
/* TR_PROBE_FAILED */
/* TR_FOUND_NIC */
/* TR_INTERFACE_FAILED_TO_COME_UP */

//netc.c
/* TR_CHECKING */
/* TR_FAILED_TO_FIND */
/* TR_ENTER_URL */

//setup.c
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1 */
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2 */
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3 */
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4 */
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK */
/* TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT */
/* TR_PASSWORD_PROMPT */
/* TR_AGAIN_PROMPT */
/* TR_PASSWORD_CANNOT_BE_BLANK */
/* TR_PASSWORDS_DO_NOT_MATCH */

//libsmooth
/* TR_INTERFACE */
/* TR_ENTER_THE_IP_ADDRESS_INFORMATION */
/* TR_STATIC */
/* TR_DHCP_HOSTNAME */
/* TR_IP_ADDRESS_PROMPT */
/* TR_NETMASK_PROMPT */
/* TR_INVALID_FIELDS */
/* TR_IP_ADDRESS_CR */
/* TR_NETWORK_MASK_CR */
/* TR_DHCP_HOSTNAME_CR */
/* TR_LOOKING_FOR_NIC */
/* TR_MANUAL */
/* TR_SELECT_NETWORK_DRIVER */
/* TR_SELECT_NETWORK_DRIVER_LONG */
/* TR_UNABLE_TO_LOAD_DRIVER_MODULE */
/* TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED */
/* TR_MODULE_PARAMETERS */
/* TR_LOADING_MODULE */
/* TR_MODULE_NAME_CANNOT_BE_BLANK */


int main(int argc, char *argv[])
{
#ifdef	LANG_EN_ONLY
        char *langnames[] = { "English", NULL };
        char *shortlangnames[] = { "en", NULL };
        char **langtrs[] = { en_tr, NULL };
#else
	char *langnames[] = { "Brasil", "Cestina", "Dansk", "Deutsch", "English", "Español", "Français", "Hellenic", "Italiano", "Spanish Latino", "Magyar", "Nederlands", "Norsk", "Polski", "Português", "Slovak", "Soomali", "Suomi", "Svenska", "Türkçe", "Tieng Viet", NULL };
	char *shortlangnames[] = { "bz", "cs", "da", "de", "en", "es", "fr", "el", "it", "la", "hu", "nl", "no", "pl", "pt", "sk", "so", "fi", "sv", "tr", "vi", NULL };
	char **langtrs[] = { bz_tr, cs_tr, da_tr, de_tr, en_tr, es_tr, fr_tr, el_tr, it_tr, la_tr, hu_tr, nl_tr, no_tr, pl_tr, pt_tr, sk_tr, so_tr, fi_tr, sv_tr, tr_tr, vi_tr, NULL };
#endif
	char hdletter, cdletter;
	char harddrive[5], cdromdrive[5];	/* Device holder. */
	struct devparams hdparams, cdromparams;	/* Params for CDROM and HD */
	int cdmounted = 0;		/* Loop flag for inserting a cd. */ 
	int rc;
	char commandstring[STRING_SIZE];
	char *installtypes[] = { "CDROM/USB-KEY", "HTTP/FTP", NULL };
	int installtype = CDROM_INSTALL; 
	char insertmessage[STRING_SIZE];
	char insertdevnode[STRING_SIZE];
	int choice;
	char shortlangname[10];
	char message[1000];
	char title[STRING_SIZE];
	int allok = 0;
	int no_restore=0;
	int unmount_before=0;
	struct keyvalue *ethernetkv = initkeyvalues();
	FILE *handle, *cmdfile;
	char line[STRING_SIZE];
	char string[STRING_SIZE];
	int maximum_free = 0, current_free;
	int memory = 0;
	int log_partition, boot_partition, root_partition, swap_file;
	int scsi_disk = 0;
	int pcmcia_disk = 0;
	int pcmcia_cdrom = 0;
	int scsi_cdrom = 0;
	int ide_cdrom = 0;
	int fdisk = 0;
	int usb_cdrom = 0;

	setlocale (LC_ALL, "");
	sethostname(SNAME, 10);
	
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
	}
	
	/* English is the default */
	for (choice = 0; langnames[choice]; choice++)
	{
		if (strcmp(langnames[choice], "English") == 0)
			break;
	}
	if (!langnames[choice])
		goto EXIT;

#ifdef	LANG_EN_ONLY
	/* No need to ask.  "choice" already has the index for English */
#else
	rc = newtWinMenu("Language selection",
		"Select the language you wish to use for the " NAME ".", 50, 5, 5, 8,
		langnames, &choice, "Ok", NULL);
#endif
	ctr = langtrs[choice];
	strcpy(shortlangname, shortlangnames[choice]);
	if (strcmp(shortlangname, "el") == 0)
		mysystem("/bin/setfont iso07u-16");
	else if (strcmp(shortlangname, "pt") == 0)
		mysystem("/bin/setfont lat1-16");
	else if (strcmp(shortlangname, "bz") == 0)
		mysystem("/bin/setfont lat1-16");
	else if (strcmp(shortlangname, "cs") == 0)
		mysystem("/bin/setfont lat2-16");
	else if (strcmp(shortlangname, "hu") == 0)
		mysystem("/bin/setfont lat2-16");
	else if (strcmp(shortlangname, "pl") == 0)
		mysystem("/bin/setfont lat2-16");
	else if (strcmp(shortlangname, "sk") == 0)
		mysystem("/bin/setfont lat2-16");
	else if (strcmp(shortlangname, "tr") == 0)
		mysystem("/bin/setfont lat5-16");
	else if (strcmp(shortlangname, "vi") == 0)
		mysystem("/bin/setfont viscii10-8x16");
	else
		mysystem("/bin/setfont lat0-16");

	/* need this for reading from formatted device */
	modprobe("vfat");

	newtDrawRootText(14, 0, NAME " v" VERSION " - " SLOGAN );
	newtPushHelpLine(ctr[TR_HELPLINE]);

	snprintf(message, STRING_SIZE, ctr[TR_WELCOME], NAME);
	snprintf (title, STRING_SIZE, "%s v%s - %s", NAME, VERSION, SLOGAN);
	newtWinMessage(title, ctr[TR_OK], message);

	snprintf(message,STRING_SIZE, ctr[TR_SELECT_INSTALLATION_MEDIA_LONG], NAME);
	rc = newtWinMenu(ctr[TR_SELECT_INSTALLATION_MEDIA], message,
		50, 5, 5, 6, installtypes, &installtype, ctr[TR_OK],
		ctr[TR_CANCEL], NULL);

	if (rc == 2)
		goto EXIT;

	if (installtype == CDROM_INSTALL)  // CD or USB-key
	{

		/* try usb key in superfloppy format only */
		if (checkusb("sda")) {
			sprintf(cdromdrive, "sda");
			usb_cdrom = 1;
			goto FOUND_SOURCE;
		}
		if (checkusb("sdb")) {
			sprintf(cdromdrive, "sdb");
			usb_cdrom = 1;
			goto FOUND_SOURCE;
		}

		/* look for an IDE CDROM. */
		if ((cdletter = findidetype(IDE_CDROM)))
		{
			sprintf(cdromdrive, "hd%c", cdletter);
			ide_cdrom = 1;
			goto FOUND_SOURCE;
		}

		/* If we have a USB attached CDROM then it will
		 * have already appeared at /dev/scd0, so we
		 * try to access it first, before asking for the
		 * SCSI drivers disk.
		 */
		if (try_scsi("scd0")) {
			sprintf(cdromdrive, "scd0");
			scsi_cdrom = 1;
			goto FOUND_SOURCE;
		}

		/* ask for supplemental  SCSI driver */
		snprintf(insertmessage, STRING_SIZE, ctr[TR_INSERT_FLOPPY], NAME" SCSI");
		if (newtWinChoice(title, ctr[TR_OK], ctr[TR_CANCEL], insertmessage) != 1)
		{
			errorbox(ctr[TR_INSTALLATION_CANCELED]);
			goto EXIT;
		}

		/* extract new modules */
		if (runcommandwithstatus("/bin/tar -C / -xvzf /dev/floppy", ctr[TR_EXTRACTING_MODULES]))
		{
			errorbox(ctr[TR_UNABLE_TO_EXTRACT_MODULES]);
			goto EXIT;
		}
		/* and load PCMCIA */
		if (pcmcia)
		{
			/* trying to support SCSI pcmcia :-) */
			runcommandwithstatus("cardmgr -o -c /etc/pcmcia/scsi",
				ctr[TR_LOADING_PCMCIA]);
			if (try_scsi("scd0")) {
				sprintf(cdromdrive, "scd0");
				pcmcia_cdrom = 1;
				goto FOUND_SOURCE;
			}
		}

		/* try loading all SCSI modules with default options */
		/* Should expand this to allow options later though */
		runcommandwithstatus("/bin/probescsi.sh", ctr[TR_PROBING_SCSI]);

		/* If it fails, give up. */
		if (try_scsi("scd0")) {
			sprintf(cdromdrive, "scd0");
			scsi_cdrom = 1;
			goto FOUND_SOURCE;
		}

		/* Unable to find a valid source, give up */
		errorbox(ctr[TR_NO_CDROM]);
		goto EXIT;

		FOUND_SOURCE:
		sprintf(cdromparams.devnode_disk, "/dev/%s", cdromdrive);
//		cdromparams.module = 0;

		snprintf(insertmessage,STRING_SIZE ,ctr[TR_INSERT_CDROM], NAME);
		strcpy (insertdevnode, cdromparams.devnode_disk);
	}
	else    /* don't understand why this follows... */
	{
		/* If we've done a PXE boot, we can skip the Drivers floppy,
		 * as we've already got the modules in our instroot.gz */
        	if (!(handle = fopen("/CDROMBOOT", "r"))) {
			snprintf(insertmessage, STRING_SIZE-12, ctr[TR_INSERT_FLOPPY], NAME);
			strcpy (insertdevnode , "/dev/floppy");
		} else {
			fclose(handle);
			cdmounted = 1;
	      		unmount_before = 1;
		}
	}

	/* Try to mount /cdrom with the device discovered */
	if (scsi_cdrom || ide_cdrom || usb_cdrom) {
		snprintf(commandstring, STRING_SIZE, "/bin/mount -o ro %s /cdrom", insertdevnode);
		int skip_dialog = 1;
		int sd_test = 0;
		while (!cdmounted)
		{
			/* for usb-key, we have to try sda then sda1. The key cannot be unpluged */
			if (sd_test == 1) { //change to sda1
				sprintf(commandstring, "/bin/mount -o ro %s1 /cdrom", insertdevnode);
			}
			if (sd_test == 2) { //the key do not contains a vfat file system
				errorbox(ctr[TR_USB_KEY_VFAT_ERR]);
				goto EXIT;
			}
			if (usb_cdrom) sd_test++;	// next USB test
			
			if (!skip_dialog && !usb_cdrom) {
			    rc = newtWinChoice(title, ctr[TR_OK], ctr[TR_CANCEL], insertmessage);
			    if (rc != 1)
			    {
				errorbox(ctr[TR_INSTALLATION_CANCELED]);
				goto EXIT;
			    }
			}
			skip_dialog = 0;
			if (mysystem(commandstring))
			    continue; //mount failed, try again

			/*verify it's what we want */
			handle = fopen ("/cdrom/" SNAME "-" VERSION ".tgz", "r");
			if (handle == NULL) {
				mysystem ("/bin/umount /cdrom");
				continue;   /* bad disk ! */
			}

			fclose (handle);
       		 	cdmounted = 1;
			/* If we've booted from CDROM, then
			 * we've already got the drivers,
			 * so we can skip this unpack. */
        		if ((handle = fopen("/CDROMBOOT", "r"))) {
				fclose(handle);
				break;  /* ok we go everything */
			}
			/* unpack drivers */
			if (runcommandwithprogress(60, 4, title,
						"/bin/tar -C / -xvzf /cdrom/images/drivers-"VERSION".img",
						175, ctr[TR_EXTRACTING_MODULES]))
			{
				errorbox(ctr[TR_UNABLE_TO_EXTRACT_MODULES]);
				goto EXIT;
			}
		}
	} else { /* no cd device were discovered,  ask second diskette */
		sprintf(commandstring, "/bin/tar -C / -xvzf /dev/floppy");
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

		/* Check for ipcop-<VERSION>.tgz */
		if (!(checktarball(SNAME "-" VERSION ".tgz")))
		{
			errorbox(ctr[TR_NO_IPCOP_TARBALL_FOUND]);
			goto EXIT;
		}
	}

	/* Get device for the HD.  This has to succeed. */
	/* first try an IDE disk */
	if ((hdletter = findidetype(IDE_HD)))
	{
		sprintf(harddrive, "hd%c", hdletter);
		goto FOUND_DESTINATION;
	}
	/* unpack SCSI driver if not done during CD detection */
	if (installtype == URL_INSTALL)
	{
		/* If we've done a PXE boot, we can skip the SCSI
		 * floppy as we've already got the modules in our 
		 * instroot.gz */
        	if (!(handle = fopen("/CDROMBOOT", "r"))) 
		{
			/* search img where it is on a mounted loop iso */
			if (!(checktarball("images/scsidrv-"VERSION".img")))
			{
				/* Couldn't find the SCSI drivers on the URL page,
				 * so after 3 failed attempts, ask the user for the
				 * SCSI drivers floppy disk. */
				errorbox(ctr[TR_NO_SCSI_IMAGE_FOUND]);
				snprintf(insertmessage, STRING_SIZE, ctr[TR_INSERT_FLOPPY], NAME" SCSI");
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
				/* unpack... THIS DO NOT WORK BECAUSE var "string" is empty*/
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
	} else {  /* cdrom/usb install, install SCSI id not done */
		if (ide_cdrom) {
			if (runcommandwithstatus("/bin/tar -C / -xvzf /cdrom/images/scsidrv-"VERSION".img", ctr[TR_EXTRACTING_MODULES]))
			{
				errorbox(ctr[TR_UNABLE_TO_EXTRACT_MODULES]);
				goto EXIT;
			}
		}
	}

	/* load SCSI/pcmcia drivers if not done during CD detection */
	if (!scsi_cdrom) {
#if 0 /* not yet */
		if (pcmcia)
		{
			/* trying to support SCSI pcmcia :-) */
			runcommandwithstatus("cardmgr -o -c /etc/pcmcia/scsi", 
				ctr[TR_LOADING_PCMCIA]);
			if (try_scsi(usb_cdrom ? "sdb":"sda")) {
				scsi_disk = 1;
				pcmcia_disk = 1;
			}
			if (checkusb("sdb") && try_scsi("sdc")) {
				scsi_disk = 1;
				pcmcia_disk = 1;
			}
		}
#endif
		/* try loading all SCSI modules with default options */
		/* Should expand this to allow options later though */
		if (!pcmcia_disk)
			runcommandwithstatus("/bin/probescsi.sh",
				ctr[TR_PROBING_SCSI]);
	}
	/* Now try to find destination device...	
	   Need to clean this up at some point
	   scsi disk is sdb/sdc when sda/sdb is used for usb-key
	   if scsi-disk is is sdd or more, it is not discovered
	*/
	if (try_scsi(usb_cdrom ? "sdb":"sda")) {
		scsi_disk = 1;
		sprintf(harddrive, usb_cdrom ? "sdb":"sda");
		goto FOUND_DESTINATION;
	}
	if (checkusb("sdb") && try_scsi("sdc")) {
		scsi_disk = 1;
		sprintf(harddrive, "sdc");
		goto FOUND_DESTINATION;
	}
	if (try_scsi("ida/c0d0")) {
		raid_disk = 1;
		sprintf(harddrive, "ida/c0d0");
		goto FOUND_DESTINATION;
	}
	if (try_scsi("cciss/c0d0")) {
		raid_disk = 1;
		sprintf(harddrive, "cciss/c0d0");
		goto FOUND_DESTINATION;
	}
	if (try_scsi("rd/c0d0")) {
		raid_disk = 1;
		sprintf(harddrive, "rd/c0d0");
		goto FOUND_DESTINATION;
	}
	if (try_scsi("ataraid/d0")) {
		raid_disk = 1;
		sprintf(harddrive, "ataraid/d0");
		goto FOUND_DESTINATION;
	}
	/* nothing worked, give up */
	errorbox(ctr[TR_NO_HARDDISK]);
	goto EXIT;

	FOUND_DESTINATION:
	/* Make the hdparms struct and print the contents.
	   With USB-KEY install and SCSI disk, while installing, the disk
	   is named 'sdb,sdc,...' (following keys)
	   On reboot, it will become 'sda'
	   To avoid many test, all names are built in the struct.
	*/
	sprintf(hdparams.devnode_disk, "/dev/%s", harddrive);
	/* Address the partition or raid partition (eg dev/sda or /dev/sdap1 */
	sprintf(hdparams.devnode_part, "/dev/%s%s", harddrive,raid_disk ? "p" : "");
	/* now the names after the machine is booted. Today only scsi is affected 
	    and we only install on the first scsi disk.
	*/
	{   char tmp[30];
	    strcpy(tmp, scsi_disk ? "sda" : harddrive);
	    sprintf(hdparams.devnode_disk_run, "/dev/%s", tmp);
	    sprintf(hdparams.devnode_part_run, "/dev/%s%s", tmp, raid_disk ? "p" : "");
	}

	rc = newtWinChoice(title, ctr[TR_OK], ctr[TR_CANCEL],
		ctr[TR_PREPARE_HARDDISK], hdparams.devnode_disk_run);
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
	
	fprintf(flog, "maximum_free = %d, memory = %d",	maximum_free, memory);
	
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

	boot_partition = 8; /* in MB */
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

		sprintf(commandstring, "/bin/sfdisk -uM %s < /tmp/partitiontable", hdparams.devnode_disk);
		if (runcommandwithstatus(commandstring, ctr[TR_PARTITIONING_DISK]))
		{
			errorbox(ctr[TR_UNABLE_TO_PARTITION]);
			goto EXIT;
		}
#endif
	}
	/* create filesystem boot partition 1 */
	sprintf(commandstring, "/bin/mke2fs -m 0 -j %s1", hdparams.devnode_part);
	if (runcommandwithstatus(commandstring, ctr[TR_MAKING_BOOT_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MAKE_BOOT_FILESYSTEM]);
		goto EXIT;
	}

	/* create filesystem log partition 2 */
	sprintf(commandstring, "/bin/mke2fs -j %s2", hdparams.devnode_part);
	if (runcommandwithstatus(commandstring, ctr[TR_MAKING_LOG_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MAKE_LOG_FILESYSTEM]);
		goto EXIT;
	}

	/* create filesystem root partition 4 */
	sprintf(commandstring, "/bin/mke2fs -m 1 -j %s4", hdparams.devnode_part);
	if (runcommandwithstatus(commandstring, ctr[TR_MAKING_ROOT_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MAKE_ROOT_FILESYSTEM]);
		goto EXIT;
	}

	/* Mount root on partition 4 */
	sprintf(commandstring, "/sbin/mount -t ext2 %s4 /harddisk", hdparams.devnode_part);
	if (runcommandwithstatus(commandstring, ctr[TR_MOUNTING_ROOT_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MOUNT_ROOT_FILESYSTEM]);
		goto EXIT;
	}
	mkdir("/harddisk/boot", S_IRWXU|S_IRWXG|S_IRWXO);
	mkdir("/harddisk/var", S_IRWXU|S_IRWXG|S_IRWXO);	
	mkdir("/harddisk/var/log", S_IRWXU|S_IRWXG|S_IRWXO);

	/* Make,mount swapfile */
	if (swap_file) {
		sprintf(commandstring, "/bin/dd if=/dev/zero of=/harddisk/swapfile bs=1024k count=%d", swap_file);
		if (runcommandwithstatus(commandstring, ctr[TR_MAKING_SWAPSPACE]))
		{
			errorbox(ctr[TR_UNABLE_TO_MAKE_SWAPSPACE]);
			goto EXIT;
		}
		if (runcommandwithstatus("/bin/mkswap /harddisk/swapfile", ctr[TR_MAKING_SWAPSPACE]))
		{
			errorbox(ctr[TR_UNABLE_TO_MAKE_SWAPSPACE]);
			goto EXIT;
		}
		if (runcommandwithstatus("/bin/swapon /harddisk/swapfile", ctr[TR_MOUNTING_SWAP_PARTITION]))
		{
			errorbox(ctr[TR_UNABLE_TO_MOUNT_SWAP_PARTITION]);
			goto EXIT;
		}
	}

	/* Mount boot on partition 1 */
	sprintf(commandstring, "/sbin/mount -t ext2 %s1 /harddisk/boot", hdparams.devnode_part);
	if (runcommandwithstatus(commandstring, ctr[TR_MOUNTING_BOOT_FILESYSTEM]))
	{
		errorbox(ctr[TR_UNABLE_TO_MOUNT_BOOT_FILESYSTEM]);
		goto EXIT;
	}

	/* Mount log on partition 2 */
	sprintf(commandstring, "/sbin/mount -t ext2 %s2 /harddisk/var/log", hdparams.devnode_part);
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
	
	if (runcommandwithprogress(60, 4, title, commandstring, 4600,
		ctr[TR_INSTALLING_FILES]))
	{
		errorbox(ctr[TR_UNABLE_TO_INSTALL_FILES]);
		goto EXIT;
	}
	
	/* Save USB controller type to modules.conf */
	write_usb_modules_conf();

	/* touch the modules.dep files */
	mysystem("/bin/chroot /harddisk /bin/touch /lib/modules/"KERNEL_VERSION"/modules.dep");
#ifdef __i386__
	mysystem("/bin/chroot /harddisk /bin/touch /lib/modules/"KERNEL_VERSION"-smp/modules.dep");
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
	  
	/* Program is outside install to save space on floppy 
	*/
	fprintf(flog, "Passing control to install2.\n");	
	fflush(flog);
	//newtSuspend();
	/* pass needed parameter for install 2 by position
	    choice: index of langage selected
	    devnode_disk: to prevent unmounting of it
	    url: if network, allow restaure from it
	*/
	sprintf(commandstring, "/harddisk/usr/local/bin/install2 %d %s %s",
		choice,
		strlen(cdromparams.devnode_disk ) ? cdromparams.devnode_disk : "none",
		strlen(url) ? url : "none"
	       );
	no_restore = system(commandstring);
	//newtResume();
	
    	/*  if we installed from CD ROM then we didn't set up the
	    network interface yet.  Therefore, set up Network
	    driver and params just before we need them.
	*/
	if (no_restore && (installtype == CDROM_INSTALL)) {  
	    	if (!(networkmenu(ethernetkv))){
			errorbox(ctr[TR_NETWORK_SETUP_FAILED]);
			goto EXIT;
		}
	}

	/* Build cache lang file */
	mysystem("/bin/chroot /harddisk /usr/bin/perl -e \"require '" CONFIG_ROOT "/lang.pl'; &Lang::BuildCacheLang\"");
	
	/* write ethernet and lang configs only if they have not
	    been restored from floppy already. */
	if (no_restore) {
		if (!write_ethernet_configs(ethernetkv)||
	    	    !write_lang_configs(shortlangname))  {
			errorbox(ctr[TR_ERROR_WRITING_CONFIG]);
			goto EXIT;
		}
	}


#if 0 /* not yet */
 	if (pcmcia_disk)
	{
		fprintf(flog, "Detected SCSI driver PCMCIA\n");
		fprintf(flog, "Fixing up ipcoprd.img\n");
		mysystem("/bin/chroot /harddisk /sbin/modprobe loop");
		mkdir("/harddisk/initrd", S_IRWXU|S_IRWXG|S_IRWXO);
		mysystem("/bin/chroot /harddisk /sbin/pcinitrd -r "KERNEL_VERSION" /boot/ipcoprd.img");
#ifdef __i386__
		mysystem("/bin/chroot /harddisk /bin/mv /boot/grub/scsigrub.conf /boot/grub/grub.conf");
#endif
#ifdef __alpha__
		mysystem("/bin/chroot /harddisk /bin/mv /boot/etc/scsiaboot.conf /boot/etc/aboot.conf");
#endif
	}
#endif

#ifdef __i386__
	// to verify: with USB-key grubbatch install on sdb and boot sda....
	replace( "/harddisk/boot/grub/grubbatch", "DEVICE", hdparams.devnode_disk);
	/* restore permissions */
	chmod("/harddisk/boot/grub/grubbatch", S_IXUSR | S_IRUSR | S_IXGRP | S_IRGRP | S_IXOTH | S_IROTH);

	sprintf(string, "root=%s4", hdparams.devnode_part_run);
	replace( "/harddisk/boot/grub/grub.conf", "root=ROOT", string);

	mysystem("/bin/chroot /harddisk /bin/mount -n -t proc none /proc");

	if (runcommandwithstatus("/bin/chroot /harddisk /boot/grub/grubbatch", ctr[TR_INSTALLING_GRUB]))
	{
		errorbox(ctr[TR_UNABLE_TO_INSTALL_GRUB]);
		goto EXIT;
	}
	mysystem("/bin/chroot /harddisk /bin/umount -n /proc");
#endif
#ifdef __alpha__
	sprintf(commandstring, "/bin/chroot /harddisk /sbin/swriteboot -f3 %s /boot/bootlx", hdparams.devnode_disk);
	mysystem(commandstring);
	sprintf(commandstring, "/bin/chroot /harddisk /sbin/abootconf %s 1", hdparams.devnode_disk_run);
	mysystem(commandstring);
	sprintf(string, "root=%s4", hdparams.devnode_part_run);
	replace( "/harddisk/boot/etc/aboot.conf", "root=ROOT", string);
#endif

	/* unmounting happens everywhere because there are places
	   which require device is to be unmounted under certain
	   circumstances.  This is the last place we can unmount
	   anything and still succeed.
	*/

	if (!unmount_before && !usb_cdrom && installtype == CDROM_INSTALL){
		if (mysystem("/sbin/umount /cdrom"))
		{
	    		errorbox(ctr[TR_UNABLE_TO_UNMOUNT_CDROM]);
	    		goto EXIT;
		}
	}

	if ((installtype == CDROM_INSTALL) && !usb_cdrom)
	{
		if (!(ejectcdrom(cdromparams.devnode_disk)))
		{
			errorbox(ctr[TR_UNABLE_TO_EJECT_CDROM]);
			// goto EXIT;
		}
	}

	snprintf(message, STRING_SIZE, ctr[TR_CONGRATULATIONS_LONG],
		NAME, SNAME, SNAME, NAME, NAME, NAME);
	newtWinMessage(ctr[TR_CONGRATULATIONS], ctr[TR_OK], message);
	
	allok = 1;

EXIT:
	fprintf(flog, "Install program ended.\n");
	fflush(flog);
	fclose(flog);

	if (!allok)
		newtWinMessage(title, ctr[TR_OK], ctr[TR_PRESS_OK_TO_REBOOT]);	

	newtFinished();

	freekeyvalues(ethernetkv);
	//no more needed
	mysystem("/bin/chroot /harddisk /bin/rm /usr/local/bin/install2");

	/* run setup only if config not restored from floppy already. */
	if (allok && no_restore)
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

int modprobe (char *mod) {
    char commandstring[STRING_SIZE];
    sprintf (commandstring,"/sbin/modprobe %s", mod);
    return mysystem (commandstring);    
}

int rmmod (char *mod) {
    char commandstring[STRING_SIZE];
    sprintf (commandstring,"/sbin/rmmod %s", mod);
    return mysystem (commandstring);    
}
