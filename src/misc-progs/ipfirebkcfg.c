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
 * $Id: ipcopbkcfg.c,v 1.2.2.6 2005/11/20 23:20:13 franck78 Exp $
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


#define EXCLUDE_HARDWARE "exclude.hardware"  // exclude file not used on backup but only optionally on restore
#define TMP_TAR	"/tmp/backup.tar"

char tempincfilename[STRING_SIZE] = "";  /* temp include file name */
char tempexcfilename[STRING_SIZE] = "";  /* temp exclude file name */
char temptarfilename[STRING_SIZE] = "";

/* add fname contents to outfile */
void add_file(int outfile, const char *fname, int verbose)
{
	FILE *freadfile;
	char fbuff[STRING_SIZE];

	if (!(freadfile = fopen(fname, "r"))) {
		/* skip this file */
		return;
	}

	while (fgets(fbuff, STRING_SIZE-1, freadfile) != NULL) {
		int offset=0;
		char *ch;
		char chk_space=1;

		/* trim string in place - don't remove spaces in middle */
		ch = fbuff;
		while (*ch) {
			if (*ch == '\r' || *ch == '\n') {
				*ch = '\0';
			}

			if (offset) {
				*(ch-offset) = *ch;
			}

			if (*ch == '\t' || *ch == ' ') {
				if (chk_space) {
					offset++;
				}
			} else {
				chk_space=0;
			}
 
			ch++;
		}

		/* remove trailing spaces */
		ch = fbuff + strlen(fbuff) - 1;
		while (*ch) {
			if (*ch == '\t' || *ch == ' ') {
				*ch = '\0';
				--ch;
			} else {
				break;
			}
		}

		/* validate name and add it */
		chdir ("/"); /* support both absolute and relative path */
		if (*fbuff) {
			if (file_exists_w(fbuff)) {
				strcat(fbuff, "\n");
				write(outfile, fbuff, strlen(fbuff));
				if (verbose)
					fprintf(stdout, " %s", fbuff);
			}
		}
	}
	fclose(freadfile);
}


/* combine files starting with fnamebase into outfile */
int cmb_files(int outfile, const char *fnamebase, int verbose)
{
	/* scan the directory and add matching files */
	struct dirent **namelist;
	int namecount;
	char addfilename[STRING_SIZE];

	/* scan the directory and get a count of the files */
	if ((namecount=scandir(CONFIG_ROOT"/backup", &namelist, 0, alphasort))<0) {
		fprintf(stderr, "No files found\n");
		exit(1);
	}

	/* process the scanned names */
	while (namecount--) {
		/* check names - compare beginning of name, ignoring case, ignore EXCLUDE_HARDWARE */
		if ((strncasecmp(fnamebase,   namelist[namecount]->d_name, strlen(fnamebase))==0) &&
		    (strncmp(EXCLUDE_HARDWARE,namelist[namecount]->d_name, strlen(EXCLUDE_HARDWARE)))) {
			/* add the contents for this name to output file */
			sprintf(addfilename, CONFIG_ROOT"/backup/%s", namelist[namecount]->d_name);
			if (verbose)
				fprintf(stdout, "%s\n",  namelist[namecount]->d_name);
			add_file(outfile, addfilename, verbose);
			free(namelist[namecount]);
			if (verbose)
				fprintf(stdout, "\n");
		}
	}
	free(namelist);
	return 0;
}

void exithandler(void)
{
	/* clean up temporary files */
	if (temptarfilename)
		unlink (temptarfilename);
	if (tempincfilename)
		unlink (tempincfilename);
	if (tempexcfilename)
		unlink (tempexcfilename);
}

int main(int argc, char**argv)
{
	int  verbose=0;
	char command[STRING_SIZE];
	char hostname[STRING_SIZE];
	int  includefile, excludefile;

	if (!(initsetuid()))
		exit(1);

	if (argc==2 && strcmp(argv[1],"--verbose")==0)
		verbose=1; // display to stdout wich (ex|in)clude files are used

	gethostname(hostname, STRING_SIZE-1);

	if (!file_exists(BACKUP_KEY)) {
		fprintf (stderr, "Couldn't locate encryption key\n");
		exit (ERR_KEY);
	}

	/* now exithandler will have something to erase */ 
	atexit(exithandler);

	/* combine every include and exclude files in backup directory into two temp file
	 * at the exception of exclude.hardware only used optionally on restore */
	/* create/open temp output file */
	// Todo: use -X exclude.files and for include.files, build the list on command line
	// to avoid unneccesary files manipulations
	strcpy (tempincfilename, "/tmp/backup-inclusion.XXXXXX");
	strcpy (tempexcfilename, "/tmp/backup-exclusion.XXXXXX");
	if ( (!(includefile = mkstemp (tempincfilename)) > 0) ||
	     (!(excludefile = mkstemp (tempexcfilename)) > 0) ){
		fprintf(stderr, "Couldn't create temporary file.\n");
		exit(1);
	}
	cmb_files(includefile, "include.", verbose);
	close(includefile);
	cmb_files(excludefile, "exclude.", verbose);
	close(excludefile);

	/* Create temporary tarfile */
	strcpy (temptarfilename, TMP_TAR);

	/* Start tarring files to temp archive
	 W (verify) and z (compress) tar options can't be used together, so separate tar from gzip */
	snprintf (command, STRING_SIZE-1, "/bin/tar -T %s -X %s -C / -cWf %s > /dev/null 2> /dev/null",
					    tempincfilename, tempexcfilename, temptarfilename);
	if (safe_system (command)) {
		fprintf (stderr, "Couldn't create %s file\n", temptarfilename);
		exit (ERR_TAR);
	}
	unlink (tempincfilename);
	strcpy (tempincfilename,"");
	unlink (tempexcfilename);
	strcpy (tempincfilename,"");

	/* Compress archive */
	snprintf (command, STRING_SIZE-1, "/bin/gzip -c < %s > "MOUNTPOINT"/%s.tar.gz", temptarfilename, hostname);
	if (safe_system (command)) {
		fprintf (stderr, "Couldn't create "MOUNTPOINT"%s.tar.gz file\n", hostname);
		exit (ERR_GZ);
	}
	unlink (temptarfilename);
	strcpy (temptarfilename,"");
	
	/* Display to stdout include files names */
	snprintf (command, STRING_SIZE-1, "/bin/tar -ztf "MOUNTPOINT"/%s.tar.gz", hostname);
	if (safe_system (command)) {
		fprintf (stderr, "Couldn't read %s.tar.gz file\n", hostname);
		exit (ERR_TAR);
	}

	/* Encrypt archive */
	snprintf (command, STRING_SIZE-1,
		"/usr/bin/openssl des3 -e -salt -in "MOUNTPOINT"/%s.tar.gz "
		"-out "MOUNTPOINT"/%s.dat -kfile " BACKUP_KEY, hostname, hostname);
	if (safe_system (command)) {
		fprintf (stderr, "Couldn't encrypt archive\n");
		exit (ERR_ENCRYPT);
	}
	snprintf (command, STRING_SIZE-1, MOUNTPOINT"/%s.tar.gz", hostname);
	unlink (command);
	
	/* Make sure web can overwrite */
	snprintf (command, STRING_SIZE-1, MOUNTPOINT"/%s.dat", hostname);
	chown (command, 99, 99);

	exit(0);
}
