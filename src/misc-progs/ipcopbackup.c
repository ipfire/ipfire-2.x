/*
 * This file is part of the IPCop Firewall.
 *
 * IPCop is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * IPCop is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with IPCop; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
 *
 * Copyright (C) 2002-06-02 Mark Wormgoor <mark@wormgoor.com>
 *
 * $Id: ipcopbackup.c,v 1.8.2.6 2006/01/20 13:30:42 franck78 Exp $
 *
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <pwd.h>
#include <shadow.h>
#include <crypt.h>
#include <glob.h>
#include "setuid.h"

// want a bigger buffer to concatenate a possibly long string
#define COMMAND_SIZE 4000
//Append lines contained in 'inputfile' to 'string'
int catlist(char* inputfile,
	    char* string ) {

    struct stat s;		// input file stats
    char buffer[STRING_SIZE];	// read buffer

    if (stat(inputfile,&s) != 0) return 1;
    if (s.st_size+strlen(string)>COMMAND_SIZE) return 1;	// too big!
    int f = open(inputfile, O_RDONLY);
    if (!f) return 1;  						// cannot open file

    int count;
    while ((count = read(f, buffer, STRING_SIZE - 1))) {
	int j;
	for (j=0; j<count; j++) {	//replace newlines with spaces
	    if (buffer[j] == '\n') buffer[j] = ' ';  
	}
	buffer[j] = '\0';
	strcat (string,buffer);	// append to string
    }
    close (f);
    return 0;	//success
}

// make a raw backup to floppy_dev (no partitioning)
int savecfg_floppy(char* floppy_dev) {
	char command[COMMAND_SIZE];  // because copy each filename here

	// want special output...
        if (close(0)) { fprintf(stderr, "Couldn't close 0\n"); exit(1); }
        if (open("/dev/zero", O_RDONLY) != 0) {fprintf(stderr, "Couldn't reopen stdin from /dev/zero\n"); exit(1); }
        if (close(2)) { fprintf(stderr, "Couldn't close 2\n"); exit(1); }
	if (! dup(1)) { fprintf(stderr, "Couldnt redirect stderr to stdout\n"); exit(1); }

	/* Make sure floppy device name is up to date */
	safe_system ("/usr/sbin/updfstab");

	/* Darren Critchley - check for floppy disk in disk drive before continuing */
	snprintf (command, STRING_SIZE-1, "dd if=%s of=/dev/null bs=1k count=1 2> /dev/null", floppy_dev);
	if (safe_system(command)) {
		perror( "Error: No floppy in drive or bad floppy in drive" );
		exit(1);
	}

	/* Clearing disk */
	snprintf (command, STRING_SIZE-1, "/bin/dd if=/dev/zero of=%s bs=1k 2> /dev/null", floppy_dev);
	safe_system (command);

	/* Start tarring files to floppy */
	snprintf (command, COMMAND_SIZE-1, "/bin/tar -X " CONFIG_ROOT"/backup/exclude.system "
					            "-X " CONFIG_ROOT"/backup/exclude.user "
						    "-C / -cvzf %s "
						    "-T " CONFIG_ROOT"/backup/include.user ",
						    floppy_dev);
	/* add include.system file content to 'command' */
        if (catlist(CONFIG_ROOT "/backup/include.system", command))  {
                fprintf(stderr, "Couldn't open backup system include file\n");
		exit (1);
        }
	safe_system (command);

	/* Now check it */
	snprintf (command, STRING_SIZE-1,"/bin/echo '<b>Checking</b>'; /bin/tar -tzf %s" , floppy_dev);
	safe_system (command);

	exit(0);
}


// Just verify that root password is ok
int  checkrootpass (char* passwd) {

    struct passwd *pw;
    struct spwd *spwd;

    if ((pw = getpwnam("root")) == NULL) {
        return (0); // root unknown....!
    }

    // get shadowed password			    
    spwd = getspnam("root");

    //and use it in right place
    if (spwd)
        pw->pw_passwd = spwd->sp_pwdp;

    return (strcmp ( crypt(passwd, pw->pw_passwd),	//encrypt cleartext
			pw->pw_passwd) == 0		//compare to encrypted version
	   ) ?  1 : 0;	// true or false
}


int main (int argc, char *argv[]) {
	char command[STRING_SIZE];

	if (argc < 3) {		// at least two args always needed, avoid some testing.
	    fprintf (stderr, "Err %s: used from cgi only !\n", argv[0]);
	    exit (1);
	}

	if (!initsetuid()){
	    fprintf (stderr, "Err %s: cannot setuid !\n", argv[0]);
	    exit (1);
	}

	// save on normal floppy for use during reinstall ONLY
	if ( (strcmp(argv[1],"-savecfg" ) == 0) &&
	     (strcmp(argv[2],"floppy") == 0) ) 
	     savecfg_floppy("/dev/floppy");	// to do: mount usb floppy....

	if ( (strcmp(argv[1],"-proc" ) == 0) &&
	     (strcmp(argv[2],"partitions") == 0) ) { //  issue cat /proc/partitions

	    int fi;
	    if ( (fi = open("/proc/partitions", O_RDONLY))==-1) exit (1); // cannot open file
	    char string[STRING_SIZE];
            int count;
	    while ((count = read(fi, string, STRING_SIZE))) {
		write (1, string, count);
	    }
	    close (fi);
	    exit (0);
	}

	// output result of 'glob' function
	if ( (strcmp(argv[1],"-glob" ) == 0)) {
	    glob_t g;
	    if (glob (argv[2],0,NULL,&g) == 0) {
		char** pstr = g.gl_pathv;	// base array
		while (*pstr) {			// while not NULL
		    printf ("%s\n", *pstr);  	// pstr is a pointer to array of char*
		    pstr++;			// next pointer
		}
		globfree (&g);
	    }
	    exit (0);
	}

	// tell if the backup.key is present
	if ( (strcmp(argv[1],"-key" ) == 0) &&
	     (strcmp(argv[2],"exist") == 0) ) { //  check key existence
	    if ( !(file_exists(BACKUP_KEY)) ) {
		fprintf (stderr, "Err %s: backup key "BACKUP_KEY" does not exist !\n", argv[0]);
		exit (ERR_KEY);
	    }
	    exit (0);
	}

	// cat the backup.key, for saving it
	if ( strcmp(argv[1],"-keycat" ) == 0) {
	    if (! checkrootpass (argv[2])) exit (1); // but only if root pw provided
	    int fi;
	    if ( (fi = open(BACKUP_KEY, O_RDONLY))==-1) exit (1); // cannot open file
	    char string[STRING_SIZE];
            int count;
	    while ((count = read(fi, string, STRING_SIZE))) {
		write (1, string, count);
	    }
	    close (fi);
	    exit (0);
	}
	
	//  generate a new backup.key ONLY if inexistant
	if ( (strcmp(argv[1],"-key" ) == 0) &&
	     (strcmp(argv[2],"new") == 0) ) { 
	    if ( (file_exists(BACKUP_KEY)) ) {
		fprintf (stderr, "Err %s: backup key "BACKUP_KEY" already exists !\n", argv[0]);
		exit (ERR_KEY);
	    }
	    //ok we can generate it
	    if (safe_system ("/usr/sbin/ipsec ranbits 256 > " BACKUP_KEY)) {
	        fprintf (stderr, "Err %s: couldn't create key !\n", argv[0]);
	        exit (ERR_KEY);
	    }
	    chmod(BACKUP_KEY, S_IRUSR);	// protect it
	    exit (0);
	}
	
	//  import a backup.key only if non existent
	if ( (strcmp(argv[1],"-key" ) == 0) &&
	     (strcmp(argv[2],"import") == 0) ) {
	    if ( (file_exists(BACKUP_KEY)) ) {
		unlink (MOUNTPOINT"/key");	// clean anyway
		fprintf (stderr, "Err %s: backup key "BACKUP_KEY" already exists !\n", argv[0]);
		exit (ERR_KEY);
	    }

	    int fi, fo;
	    if ( (fi = open(MOUNTPOINT"/key", O_RDONLY))==-1) {
		fprintf (stderr, "Err %s: no backup key "MOUNTPOINT"/key to import !\n", argv[0]);
		exit (ERR_KEY); // cannot open file
	    }	

	    if ( (fo = open(BACKUP_KEY, O_WRONLY | O_CREAT ))==-1) {
		close (fi);
		unlink (MOUNTPOINT"/key");	// clean anyway
		fprintf (stderr, "Err %s: backup key "BACKUP_KEY" creation error !\n", argv[0]);
		exit (ERR_KEY);
	    }

	    char buffer[STRING_SIZE];
            int count;
	    while ((count = read(fi, buffer, STRING_SIZE))) {
		write (fo, buffer, count);
	    }
	    close (fo);
	    close (fi);
	    unlink (MOUNTPOINT"/key");
	    exit (0);
	}

	// disk functions like mount umount,...
	if ((strspn(argv[2], LETTERS_NUMBERS ) == strlen(argv[2])) &&
	    (strlen(argv[2]) >2) && (strlen(argv[2]) <6)) {
		if (strcmp(argv[1],"-M") == 0) { //  M  sda1 => mount /dev/sda1 /mountpoint
			//safe_system("/bin/sync");
			snprintf(command, STRING_SIZE - 1,"/bin/mount -t vfat -o,uid=99,gid=99 /dev/%s "MOUNTPOINT, argv[2]);
			safe_system(command);
			//safe_system("/bin/sync");
		}else
		if (strcmp(argv[1],"-U") == 0) { // U sda1 => umount /dev/sda1
			//safe_system("/bin/sync");
			snprintf(command, STRING_SIZE - 1,"/bin/umount /dev/%s", argv[2]);
			safe_system(command);
			safe_system("/bin/sync");
		}else
		if (strcmp(argv[1],"-f") == 0) { // f sda1 => mke2fs /dev/sda1
			snprintf(command, STRING_SIZE - 1,"/sbin/mke2fs -q /dev/%s", argv[2]);
			//safe_system(command);
			//safe_system("/bin/sync");
		}else
		if (strcmp(argv[1],"-F") == 0) { // F sda => fdisk /dev/sda
			//safe_system("/bin/sync");
			snprintf(command, STRING_SIZE - 1,"/bin/dd if=/dev/zero of=/dev/%s count=2 bs=512", argv[2]);
			//safe_system(command);
			snprintf(command, STRING_SIZE - 1,"/bin/echo \"n\np\n1\n1\n\nw\nq\n\"|/sbin/fdisk /dev/%s", argv[2]);
			//safe_system(command);
			snprintf(command, STRING_SIZE - 1,"/sbin/mke2fs -q /dev/%s1", argv[2]);  // beware of %s1
			//safe_system(command);
			//safe_system("/bin/sync");
		}else {
		    fprintf (stderr, "Err %s: bad command !\n", argv[0]);
		    exit (1);
		}
		exit (0);
	}else {
		fprintf (stderr, "Err %s: bad arg !\n", argv[0]);
		exit (1);
	}
	return 0;
}
