/* IPCop install2 program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * (c) Franck Bourdonnec, 2006
 * Contains update/restore code
 * 
 * $Id: install2.c,v 1.1.2.5 2006/02/10 06:53:57 gespinasse Exp $
 * 
 */
#include "install.h"

FILE *flog = NULL;
char *mylog;
char **ctr;

/* 
    To include a translated string in the final installer, you must reference
    it here with a simplr comment. This save a lot a space in the installer
*/

/* TR_BUILDING_INITRD */
/* TR_HELPLINE */
/* TR_SKIP */
/* TR_RESTORE_CONFIGURATION */
/* TR_RESTORE */
/* TR_OK */
/* TR_CANCEL */
/* TR_ERROR */
/* TR_INSTALLING_FILES */
/* TR_FAILED_TO_FIND */
/* TR_UNABLE_TO_INSTALL_FILES */
/* TR_LOADING_PCMCIA */

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

//upgrade 120
/* TR_UNABLE_TO_OPEN_SETTINGS_FILE */
/* TR_DOMAINNAME */
/* TR_ENTER_DOMAINNAME */
/* TR_DOMAINNAME_CANNOT_CONTAIN_SPACES */
/* TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM */
/* TR_UNABLE_TO_WRITE_ETC_FSTAB */

// dir to find files, chrooted or not...
#define TMP_EXTRACT_CH "/tmp/ipcop"
#define TMP_EXTRACT "/harddisk" TMP_EXTRACT_CH
#define MOUNT_BACKUP_CH "/mnt/usb"
#define MOUNT_BACKUP "/harddisk" MOUNT_BACKUP_CH
/*
    return 0 when dev contains a backup set
    leave dev mounted
*/
int try_mount (char *dev, char *testfile) {
	char commandstring[STRING_SIZE];
	mysystem("/bin/umount " MOUNT_BACKUP);
	sprintf(commandstring, "/bin/mount -t vfat -o ro %s " MOUNT_BACKUP, dev);
	mysystem(commandstring);

	/*verify it's what we want */
	sprintf(commandstring, MOUNT_BACKUP "/%s.dat", testfile);
	FILE *handle = fopen(commandstring, "r");
	if (handle == NULL) {
		return 1;   /* bad disk ! */
	}
	fclose(handle);
	
	handle = fopen(MOUNT_BACKUP "/backup.key", "r");
	if (handle == NULL) {
		return 1;   /* bad disk ! */
	}
	fclose(handle);
	return 0; //success
}

/* try to mount usb device until backup.tgz is found except the 
    destination device (scsi names are identical with usb key)
    check "sda sdb sdc sdd"
*/
int mountbackup (char *testfile, char *destination_device) {
	char sourcedev[30];
	char i,j;
	for (i = 'a'; i < 'e'; i++) {
		sprintf (sourcedev,"/dev/sd%c ",i);
		if (strcmp (destination_device, sourcedev) != 0) {
			if (!try_mount (sourcedev, testfile)) return 0;
		}
		for (j = '1'; j < '5'; j++) {
			sourcedev[8] = j;
			if (strcmp (destination_device, sourcedev) != 0) {
				if (!try_mount (sourcedev, testfile)) return 0;
			}
		}
	}
	return 1;
}

int floppy_locate() {
	/* Temporarily mount /proc under /harddisk/proc,
	   run updfstab to locate the floppy, and unmount /harddisk/proc
	   again.  This should be run each time the user tries to restore
	   so it can properly detect removable devices */
	if (mysystem("/bin/mount -n -t proc /proc /harddisk/proc")) {
		errorbox(ctr[TR_UNABLE_TO_MOUNT_PROC_FILESYSTEM]);
		return 1;
	}
	if (mysystem("/bin/chroot /harddisk /usr/sbin/updfstab")) {
		errorbox(ctr[TR_UNABLE_TO_WRITE_ETC_FSTAB]);
		return 1;
	}
	mysystem("/bin/umount /harddisk/proc");
	return 0;
}

/* Check the SQUID acl file exists, if not use our 1.4 copy */
void fixup_squidacl() {
	FILE *aclreadfile;
	if ((aclreadfile = fopen ("/harddisk" CONFIG_ROOT "/proxy/acl", "r"))) {
		unlink ("/harddisk" CONFIG_ROOT "/proxy/acl-1.4");
		fclose(aclreadfile);
	} else {
		rename ("/harddisk" CONFIG_ROOT "/proxy/acl-1.4",
			"/harddisk" CONFIG_ROOT "/proxy/acl");
	}
	chown  ("/harddisk" CONFIG_ROOT "/proxy/acl", 99, 99);
}
/* if we detected SCSI then fixup */
void fixup_initrd() {
	FILE *handle;
	char line[STRING_SIZE];
	char commandstring[STRING_SIZE];
	
	if (!(handle = fopen("/scsidriver", "r"))) 
	    return;

	char *driver;
	fgets(line, STRING_SIZE-1, handle);
	fclose(handle);
	line[strlen(line) - 1] = 0;
	driver = strtok(line, ".");
	fprintf(flog, "Detected SCSI driver %s\n", driver);
	if (!strlen(driver) > 1) 
		return;
		
	fprintf(flog, "Fixing up ipcoprd.img\n");
	mysystem("/bin/chroot /harddisk /sbin/modprobe loop");
	mkdir("/harddisk/initrd", S_IRWXU|S_IRWXG|S_IRWXO);
	sprintf(commandstring, "/bin/chroot /harddisk /sbin/mkinitrd"
				" --with=scsi_mod --with=%s --with=sd_mod"
				" --with=sr_mod --with=libata"
				" --with=ataraid /boot/ipcoprd.img "KERNEL_VERSION,
				driver );
	runcommandwithstatus(commandstring, ctr[TR_BUILDING_INITRD]);
#ifdef __i386__
	sprintf(commandstring, "/bin/chroot /harddisk /sbin/mkinitrd"
				" --with=scsi_mod --with=%s --with=sd_mod"
				" --with=sr_mod --with=libata"
				" --with=ataraid /boot/ipcoprd-smp.img "KERNEL_VERSION"-smp",
				driver );
	runcommandwithstatus(commandstring, ctr[TR_BUILDING_INITRD]);
	mysystem("/bin/chroot /harddisk /bin/mv /boot/grub/scsigrub.conf /boot/grub/grub.conf");
#endif
#ifdef __alpha__
	runcommandwithstatus("/bin/chroot /harddisk /bin/mv /boot/etc/scsiaboot.conf /boot/etc/aboot.conf", ctr[TR_BUILDING_INITRD]);
#endif
}
/* when backup is ready in tmpdir, move files to definitive location */
void do_copy_files() {
	mysystem("/bin/chroot /harddisk /bin/cp -af "TMP_EXTRACT_CH"/. /");
	/* Upgrade necessary files from v1.2 to v1.3 to v1.4 */
	upgrade_v12_v13();
	upgrade_v130_v140();
	/* Upgrade configuration files starting from 1.4.11 */
	mysystem("/bin/chroot /harddisk /usr/local/bin/upgrade");
}

int main(int argc, char *argv[]) {
#define LANG argv[1]
#define DEST_DEV argv[2]
#define WGET argv[3]

#ifdef	LANG_EN_ONLY
	char **langtrs[] = { en_tr, NULL };
#elifdef	LANG_ALL
	char **langtrs[] = { bz_tr, cs_tr, da_tr, de_tr, en_tr, es_tr, fr_tr, el_tr, it_tr, la_tr, hu_tr, nl_tr, no_tr, pl_tr, pt_tr, sk_tr, so_tr, fi_tr, sv_tr, tr_tr, vi_tr, NULL };
#else
	char **langtrs[] = { de_tr, en_tr, NULL };
#endif
	char message[1000];
	char title[STRING_SIZE];
	char commandstring[STRING_SIZE];

	setlocale (LC_ALL, "");	
	/* Log file/terminal stuff. */
	mylog = "/dev/tty2";
	ctr = langtrs[ atoi(LANG) ];

	if (!(flog = fopen(mylog, "w+")))
	{
		printf("Couldn't open log terminal\n");
		return 0;
	}
	fprintf(flog, "Install2 program started.\n");
	newtInit();
	newtCls();
	strcpy (title, NAME " v" VERSION " - " SLOGAN);
	newtDrawRootText(14, 0, title);
	newtPushHelpLine(ctr[TR_HELPLINE]);

	/* working dirs... */
	mkdir(MOUNT_BACKUP, S_IRWXU|S_IRWXG|S_IRWXO);

	//create the GUI screen and objects
	newtComponent form, header, labelfile, labelkey, file, key, radio0, radio1, radio2, radio3, radio4, ok;

	newtCenteredWindow (55,20,ctr[TR_RESTORE]);
	form = newtForm (NULL, NULL,0);

	sprintf(message, ctr[TR_RESTORE_CONFIGURATION], NAME);
	header = newtTextboxReflowed (2,1,message,51,0,0,0);
	newtFormAddComponent(form, header);

	// The four method of restauration
	int start1=1, start2=0, start3=0, start4=0;
	radio1 = newtRadiobutton (17, 5, ctr[TR_SKIP], start1, NULL);
	radio2 = newtRadiobutton (17, 6, "Floppy (legacy)", start2, radio1);
	radio3 = newtRadiobutton (17, 7, "Usb-storage/CDROM", start3, radio2);
	if (strcmp(WGET,"none"))
	    radio4 = newtRadiobutton (17, 8, "HTTP/FTP", start4, radio3);
	else
	    radio4 = NULL;
	newtFormAddComponents(form, radio1, radio2, radio3, radio4, NULL);

	// The optionnal filename for 'backup'
	labelfile=newtTextbox(12, 10, 35, 1, 0);
	newtTextboxSetText (labelfile, "Filename");
	newtFormAddComponent(form, labelfile);
	char *filevalue;
	char fileinit[STRING_SIZE] = "backup";
	file = newtEntry (17, 11, fileinit, 20, &filevalue, 0);
	newtFormAddComponent(form, file);

	// The optionnal password for the key
	labelkey=newtTextbox(12, 13, 35, 1, 0);
	newtTextboxSetText (labelkey, "Backup key password");
	newtFormAddComponent(form, labelkey);
	char *keyvalue;
	char keyinit[STRING_SIZE] = "";
	key = newtEntry (17, 14, keyinit, 20, &keyvalue, 0);
	newtFormAddComponent(form, key);

	// The OK button
	ok=newtButton (23, 16, ctr[TR_OK]);
	newtFormAddComponent(form, ok);

	/* loop until succeeds or user skips out */
	int retcode = -1;
	while ( retcode<0 ) {

	    // run the windows
	    struct newtExitStruct reponse;
	    newtFormRun (form, &reponse);
	    radio0 = newtRadioGetCurrent(radio1);
	    int radio;
	    radio = radio0 == radio1 ? 1 : radio0 == radio2 ? 2 :  radio0 == radio3 ? 3 : radio0 == radio4 ? 4 : 0;
	    strcpy(keyinit,keyvalue);	//reuse actual value
	    strcpy(fileinit,filevalue);

	    if (radio==1) {
		    retcode = 1;	// no restore: nothing special
		    break;		// out of the while loop
	    }

	    mkdir(TMP_EXTRACT, S_IRWXU|S_IRWXG|S_IRWXO);
	    statuswindow(45, 4, title, ctr[TR_INSTALLING_FILES]);
	    switch (radio) {
	    case 4:	// network
		    sprintf(commandstring,"/bin/wget -P " TMP_EXTRACT " %s/%s.dat", WGET, filevalue);
		    mysystem (commandstring);
		    sprintf(commandstring,"/bin/wget -P " TMP_EXTRACT " %s/%s.key", WGET, filevalue);
		    if (mysystem (commandstring)) {
			    errorbox(ctr[TR_FAILED_TO_FIND]);
			    break;
		    };
		    goto COMMON;
	    case 3:	// normal backup
		    if (mountbackup( filevalue, DEST_DEV )) {
			    errorbox(ctr[TR_UNABLE_TO_INSTALL_FILES]);//mess=no device with backup found
			    break;
		    };
		    // link files to a COMMON location
		    sprintf (commandstring, "chroot /harddisk ln -s "MOUNT_BACKUP_CH"/%s.dat " TMP_EXTRACT_CH "/%s.dat", filevalue, filevalue);
		    mysystem (commandstring);
		    sprintf (commandstring, "chroot /harddisk ln -s "MOUNT_BACKUP_CH"/%s.key " TMP_EXTRACT_CH "/%s.key", filevalue, filevalue);
		    mysystem (commandstring);

	COMMON:	    // DECRYPT THE TARBALL
		    // Copy the key to a new location because we decrypt it!	
		    if (strcmp(keyvalue, "")) { // password provided: decrypt the key
			    sprintf(commandstring,   "/bin/chroot /harddisk /usr/bin/openssl enc"
						    " -a -d -aes256 -salt"
						    " -pass pass:%s"
						    " -in " TMP_EXTRACT_CH "/%s.key"
						    " -out " TMP_EXTRACT_CH "/__tmp.key",
						    keyvalue, filevalue);
		    } else {			//just copy to new name
			    sprintf(commandstring,  "/bin/chroot /harddisk cp"
						    " " TMP_EXTRACT_CH "/%s.key"
						    " " TMP_EXTRACT_CH "/__tmp.key",
						    filevalue);
		    }
		    mysystem (commandstring);

		    sprintf(commandstring,  "/bin/chroot /harddisk /usr/bin/openssl des3"
					    " -d -salt"
					    " -in " TMP_EXTRACT_CH "/%s.dat"
					    " -out " TMP_EXTRACT_CH "/backup.tgz"
					    " -kfile " TMP_EXTRACT_CH "/__tmp.key",
					    filevalue);

		    if (mysystem (commandstring)) {
			    errorbox(ctr[TR_UNABLE_TO_INSTALL_FILES]);//mess=decrypt error:invalid key?
			    break;
		    }
		    strcpy(commandstring,   "/bin/chroot /harddisk /bin/tar"
					    " -X " CONFIG_ROOT "/backup/exclude.system"
					    " -C " TMP_EXTRACT_CH
					    " -xzf " TMP_EXTRACT_CH "/backup.tgz");

		    if (mysystem(commandstring)) {
			    errorbox(ctr[TR_UNABLE_TO_INSTALL_FILES]);
			    break;
		    }
		    sprintf(commandstring, TMP_EXTRACT "/%s.dat", filevalue);
		    unlink(commandstring ); //dont need them anymore
		    unlink( TMP_EXTRACT "/backup.tgz");
		    sprintf(commandstring, TMP_EXTRACT "/%s.key", filevalue);
		    unlink(commandstring );
		    unlink( TMP_EXTRACT "/__tmp.key");

		    /* Now copy to correct location */
		    do_copy_files();
		    retcode = 0; /* successfully restored */
		    break;
	    case 2:
		    // diskette change
		    if (floppy_locate()) {
			    retcode = 2; // this an error!
			    break;
		    }

		    /* Always extract to /tmp/ipcop for temporary extraction
		       just in case floppy fails.
		       try a compressed backup first because it's quicker to fail.
		       In exclude.system, files name must be without leading / or 
		       on extraction, name will never match
		    */
		    sprintf(commandstring,
		     "/bin/chroot /harddisk /bin/tar -X " CONFIG_ROOT "/backup/exclude.system -C "TMP_EXTRACT_CH" -xvzf /dev/floppy > %s 2> /dev/null", mylog);
		    if (system(commandstring)) {
		    /* if it's not compressed, try uncompressed first before failing*/
			sprintf(commandstring,
		     "/bin/chroot /harddisk /bin/tar -X " CONFIG_ROOT "/backup/exclude.system -C "TMP_EXTRACT_CH" -xvf /dev/floppy > %s 2> /dev/null", mylog);
			if (system(commandstring)) {
			    /* command failed trying to read from floppy */
			    errorbox(ctr[TR_UNABLE_TO_INSTALL_FILES]);
			    break;
			} 
		    }
		    /* Now copy to correct location */
		    do_copy_files();
		    retcode = 0; /* successfully restored */
	    }//switch
	    /* remove possible badly restored files */
	    mysystem("/bin/chroot /harddisk /bin/rm -rf " TMP_EXTRACT_CH );
	    newtPopWindow(); // close windows
	}//while
	newtFormDestroy(form);

	/* cleanup */
	mysystem("/bin/umount " MOUNT_BACKUP);
	mysystem("/bin/chroot /harddisk /bin/rmdir " MOUNT_BACKUP_CH);

	/* others operations moved from install to install2 */
	fixup_squidacl();
	fixup_initrd();

	fprintf(flog, "Install2 program ended.\n");
	fflush(flog);
	fclose(flog);
	newtFinished();
	return retcode;
}

