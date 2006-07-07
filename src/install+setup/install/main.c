/* SmoothWall install program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Contains main entry point, and misc functions.
 * 
 * $Id: main.c,v 1.63.2.57 2005/09/25 19:57:46 gespinasse Exp $
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

extern char *bz_tr[];
extern char *cs_tr[];
extern char *da_tr[];
extern char *en_tr[];
extern char *es_tr[];
extern char *fi_tr[];
extern char *fr_tr[];
extern char *hu_tr[];
extern char *la_tr[];
extern char *nl_tr[];
extern char *de_tr[];
extern char *tr_tr[];
extern char *it_tr[];
extern char *el_tr[];
extern char *pl_tr[];
extern char *pt_tr[];
extern char *so_tr[];
extern char *sv_tr[];
extern char *no_tr[];
extern char *vi_tr[];

int main(int argc, char *argv[])
{
#ifdef	LANG_EN_ONLY
        char *langnames[] = { "English", NULL };
        char *shortlangnames[] = { "en", NULL };
        char **langtrs[] = { en_tr, NULL };
#elifdef	LANG_ALL
	char *langnames[] = { "Brasil", "Cestina", "Dansk", "Deutsch", "English", "Español", "Français", "Hellenic", "Italiano", "Spanish Latino", "Magyar", "Nederlands", "Norsk", "Polski", "Português", "Soomali", "Suomi", "Svenska", "Türkçe", "Tieng Viet", NULL };
	char *shortlangnames[] = { "bz", "cs", "da", "de", "en", "es", "fr", "el", "it", "la", "hu", "nl", "no", "pl", "pt", "so", "fi", "sv", "tr", "vi", NULL };
	char **langtrs[] = { bz_tr, cs_tr, da_tr, de_tr, en_tr, es_tr, fr_tr, el_tr, it_tr, la_tr, hu_tr, nl_tr, no_tr, pl_tr, pt_tr, so_tr, fi_tr, sv_tr, tr_tr, vi_tr, NULL };	
#else
	char *langnames[] = { "Deutsch", "English", NULL };
	char *shortlangnames[] = { "de", "en", NULL };
	char **langtrs[] = { de_tr, en_tr, NULL };
#endif
	char hdletter, cdletter;
	char harddrive[5], cdromdrive[5];	/* Device holder. */
	struct devparams hdparams, cdromparams;	/* Params for CDROM and HD */
	int cdmounted = 0;		/* Loop flag for inserting a cd. */ 
	int rc;
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
	int maximum_free = 0, current_free;
	int memory = 0;
	int log_partition, boot_partition, root_partition, swap_file;
	int scsi_disk = 0;
	int pcmcia_disk = 0;
	int pcmcia_cdrom = 0;
	int scsi_cdrom = 0;
	int ide_cdrom = 0;
	int fdisk = 0;


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
	}
	
	/* Deutsch is the default */
	for (choice = 0; langnames[choice]; choice++)
	{
		if (strcmp(langnames[choice], "Deutsch") == 0)
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
	else if (strcmp(shortlangname, "tr") == 0)
		mysystem("/bin/setfont lat5-16");
	else if (strcmp(shortlangname, "vi") == 0)
		mysystem("/bin/setfont viscii10-8x16");
	else
		mysystem("/bin/setfont lat0-16");
	
	newtDrawRootText(14, 0, NAME " v" VERSION " - " SLOGAN );
	newtPushHelpLine(ctr[TR_HELPLINE]);

	sprintf(message, ctr[TR_WELCOME], NAME);
	sprintf (title, "%s v%s - %s", NAME, VERSION, SLOGAN);
	newtWinMessage(title, ctr[TR_OK], message);

	/* sprintf(message, ctr[TR_SELECT_INSTALLATION_MEDIA_LONG], NAME);
	 * rc = newtWinMenu(ctr[TR_SELECT_INSTALLATION_MEDIA], message,
	 *	50, 5, 5, 6, installtypes, &installtype, ctr[TR_OK],
	 *	ctr[TR_CANCEL], NULL); 
	 *
	 * 	if (rc == 2)
	 *	goto EXIT;
	 * This is for avoiding the question for a network installation. Set to cdrom.
	 */
	sprintf(installtype, CDROM_INSTALL, NAME);
					
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
				    runcommandwithstatus("/bin/probescsi.sh",
					ctr[TR_PROBING_SCSI]);
	
				/* If it fails, give up. */
				if (!(try_scsi("scd0"))) {
					errorbox(ctr[TR_NO_CDROM]);
					goto EXIT;
				}
			}

			sprintf(cdromdrive, "scd0");
			scsi_cdrom = 1;
		} else {
			sprintf(cdromdrive, "hd%c", cdletter);
			ide_cdrom = 1;
		}

		snprintf(cdromparams.devnode, STRING_SIZE, "/dev/%s", cdromdrive);
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
				runcommandwithstatus("/bin/probescsi.sh",
					ctr[TR_PROBING_SCSI]);
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
	if ((handle = fopen("/scsidriver", "r")))
		mysystem("/bin/chroot /harddisk /sbin/splash -s -f /boot/splash/config/bootsplash-1024x768.cgf >> /harddisk/boot/ipfirerd.img");
	else
		mysystem("/bin/chroot /harddisk /sbin/splash -s -f /boot/splash/config/bootsplash-1024x768.cgf > /harddisk/boot/initrd.splash");
	if ((handle = fopen("/scsidriver", "r")))
		mysystem("/bin/chroot /harddisk /sbin/splash -s -f /boot/splash/config/bootsplash-1024x768.cgf >> /harddisk/boot/ipfirerd-smp.img");
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
