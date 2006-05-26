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
 * Copyright (C) 2003-06-25 Tim Butterfield <timbutterfield@mindspring.com>
 *
 * $Id: ipcoprscfg.c,v 1.2.2.6 2005/11/21 00:11:39 franck78 Exp $
 *
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <grp.h>
#include <dirent.h>
#include "setuid.h"

#define TMP_FILEZ 	"/tmp/TMPFILE.tar.gz"
#define TMP_FILE 	"/tmp/TMPFILE.tar"

/* check existence of a data file */
int data_exists(const char *hostname) {
    char fname[STRING_SIZE];
    snprintf (fname, STRING_SIZE-1, MOUNTPOINT"/%s.dat", hostname);
    return file_exists(fname);
}


int main(int argc, char**argv) {
	int rshardware=0;
	char command[STRING_SIZE];
	char hostname[STRING_SIZE];

	if (argc==2 && strcmp(argv[1],"--hardware")==0)
	    rshardware=1; // restore hardware settings

	gethostname(hostname, STRING_SIZE-1);

	/* Init setuid */
	if (!initsetuid())
	    exit(1);

	/* if  a key file exists, an encrypted .dat is required */
	if (!file_exists(BACKUP_KEY)) {
    	    fprintf (stderr, "Missing encryption key\n");
	    exit (ERR_DECRYPT);
	}
	
	
	if (!data_exists(hostname)) {
	    fprintf (stderr, "Missing encrypted archive "MOUNTPOINT"/%s.dat archive\n", hostname);
	    exit (ERR_DAT);
	}

	/* decrypt .dat file to tmp file */
	snprintf (command, STRING_SIZE-1, "/usr/bin/openssl des3 -d -salt -in "MOUNTPOINT"/%s.dat -out "TMP_FILEZ" -kfile "BACKUP_KEY" > /dev/null 2> /dev/null", hostname);
	if (safe_system (command)) {
	    fprintf (stderr, "Couldn't decrypt "MOUNTPOINT"/%s.dat archive\n", hostname);
	    exit (ERR_DECRYPT);
	}

	/* create temporary directory for testing untar */
	char tmp_dir[STRING_SIZE];

	strcpy (tmp_dir,"cfg_XXXXXXX");
	if (mkdtemp (tmp_dir)==NULL) {
	    unlink (TMP_FILEZ);
	    exit (ERR_ANY);
	}

	/* Start (test) untarring files from compressed archive */
	snprintf (command, STRING_SIZE-1, "/bin/tar -C %s -xzvf "TMP_FILEZ" > /dev/null 2> /dev/null",tmp_dir);
	if (safe_system (command)) {
	    fprintf (stderr, "Archive have errors!\n");
	    unlink (TMP_FILEZ);
	    exit (ERR_UNTARTST);
	}

	/* remove temporary directory */
	snprintf (command, STRING_SIZE-1, "/bin/rm -rf %s > /dev/null 2> /dev/null",tmp_dir);
	safe_system (command);
	
	/* Start (real) untarring files from compressed archive */
	char extraX[STRING_SIZE] = "";
	int retcode = 0;
	if (rshardware==0) { /* extra eXclusion from restore  */
	    strcpy (extraX, "-X "CONFIG_ROOT"/backup/exclude.hardware ");
	}
	snprintf (command, STRING_SIZE-1, "/bin/tar -C / -xzvf "TMP_FILEZ" -X "CONFIG_ROOT"/backup/exclude.system %s > /dev/null 2> /dev/null", extraX);
	if (safe_system (command)) {
	    fprintf (stderr, "Error restoring archive\n");
	    retcode = ERR_UNTAR;
	}

	/* remove temporary archive copy */
	unlink (TMP_FILEZ);

	exit(retcode);
}
