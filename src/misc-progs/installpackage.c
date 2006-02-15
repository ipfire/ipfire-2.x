/* This file is part of the IPCop Firewall.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * Copyright (C) 2004-05-31 Robert Kerr <rkerr@go.to>
 *
 * Loosely based on the smoothwall helper program by the same name,
 * portions are (c) Lawrence Manning, 2001
 *
 * $Id: installpackage.c,v 1.3.2.6 2005/08/22 20:51:38 eoberlander Exp $
 * 
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <sys/file.h>
#include <fcntl.h>
#include <syslog.h>
#include <time.h>
#include "setuid.h"

#define ERR_ANY 1
#define ERR_TMPDIR 2
#define ERR_SIG 3
#define ERR_TAR 4
#define ERR_INFO 5
#define ERR_PACKLIST 6
#define ERR_INSTALLED 7
#define ERR_POPEN 8
#define ERR_SETUP 9
#define ERR_MISSING_PREVIOUS 10
#define ERR_DISK 11

/* The lines in the package information file and the patches/installed list
 * are often longer than STRING_SIZE so we use a larger buffer */
#define BUFFER_SIZE 4096

char *info = NULL;
FILE *infofile = NULL;
char command[STRING_SIZE], tmpdir[] = "/var/log/pat_install_XXXXXX";
void exithandler(void)
{
	if(info) free(info);
	if(infofile)
	{
		flock(fileno(infofile), LOCK_UN);
		fclose(infofile);
	}
	/* Cleanup tmpdir */
	chdir("/var/patches"); /* get out of it before erasing */
	snprintf(command, STRING_SIZE - 1, "/bin/rm -rf %s", tmpdir);
	if(safe_system(command))
    	    perror("Couldn't remove temp dir");
}

int main(int argc, char *argv[])
{
	char buffer[BUFFER_SIZE];
	int ret;
	FILE *p;

	if (!(initsetuid()))
		exit(1);

	/* Sanitize arguments */
	if (argc < 2)
	{
		fprintf(stderr, "Missing arg\n");
		exit(1);
	}
	if (strspn(argv[1], NUMBERS) != strlen(argv[1]))
	{
		fprintf(stderr, "Bad arg\n");
		exit(1);
	}

	if(!mkdtemp(tmpdir))
	{
		perror("Unable to create secure temp dir");
		exit(ERR_TMPDIR);
	}
	
	/* now exithandler will have something to erase */ 
	atexit(exithandler);

	/* verify and extract package */
	memset(command, 0, STRING_SIZE);
	snprintf(command, STRING_SIZE-1, "/usr/bin/gpg --batch --homedir /root/.gnupg -o %s/patch.tar.gz --decrypt /var/patches/patch-%s.tar.gz.gpg", tmpdir, argv[1]);
	ret = safe_system(command) >> 8;
	if(ret==1)  /* 1=> gpg-key error */
	{
		fprintf(stderr, "Invalid package: signature check failed\n");
		exit(ERR_SIG);
	}
	if(ret==2)  /* 2=> gpg pub key not found */
	{
		fprintf(stderr, "Public signature not found (who signed package?) !\n");
		exit(ERR_SIG);
	}
	if(ret) /* retry extraction on other partition */
	{   
	    rmdir(tmpdir);
	    strcpy (tmpdir,"/var/patches/install_XXXXXX");
	    if(!mkdtemp(tmpdir))
	    {
		    perror("Unable to create secure temp dir");
		    _exit(ERR_TMPDIR); /* no need exit handler */
	    }
	    memset(command, 0, STRING_SIZE);
	    snprintf(command, STRING_SIZE-1, "/usr/bin/gpg --batch --homedir /root/.gnupg -o %s/patch.tar.gz --decrypt /var/patches/patch-%s.tar.gz.gpg", tmpdir, argv[1]);
	    ret = safe_system(command);
	    if(ret)
	    {
		    fprintf(stderr, "Not enough disk space or gpg error %d !\n",ret);
		    exit(ERR_DISK);
	    }	
	}
	/* no more needed gpg-package & make room */
	snprintf(command, STRING_SIZE-1, "/var/patches/patch-%s.tar.gz.gpg", argv[1]);
	unlink ( command );
	
	/* unzip the package */
	chdir (tmpdir);
	if(safe_system("/bin/tar xzf patch.tar.gz"))
	{
		fprintf(stderr, "Invalid package: untar failed\n");
		exit(ERR_TAR);
	}
	/* And read 'information' to check validity */
	snprintf(buffer, STRING_SIZE-1, "%s/information", tmpdir);
	if(!(infofile = fopen(buffer,"r")))
	{
		if(errno == ENOENT)
			fprintf(stderr, "Invalid package: contains no information file\n");
		else
			perror("Unable to open package information file");
		exit(ERR_INFO);
	}
	if(!fgets(buffer, BUFFER_SIZE, infofile))
	{
		perror("Couldn't read package information");
		exit(ERR_INFO);
	}
	fclose(infofile);
	if(buffer[strlen(buffer)-1] == '\n')
		buffer[strlen(buffer)-1] = '\0';
	if(!strchr(buffer,'|'))
	{
		fprintf(stderr, "Invalid package: malformed information string.\n");
		exit(ERR_INFO);
	}
	info = strdup(buffer);

	/* check if package is already installed */
	if(!(infofile = fopen(CONFIG_ROOT "/patches/installed","r+")))
	{
		perror("Unable to open installed package list");
		exit(ERR_PACKLIST);
	}
	/* get exclusive lock to prevent a mess if 2 copies run at once, and set
	 * close-on-exec flag so the FD doesn't leak to the setup script */
	flock(fileno(infofile), LOCK_EX);
	fcntl(fileno(infofile), F_SETFD, FD_CLOEXEC);

	while(fgets(buffer, BUFFER_SIZE, infofile))
	{
		if(!strncmp(buffer, info, strlen(info)))
		{
			fprintf(stderr,"This package is already installed\n");
			exit(ERR_INSTALLED);
		}
	}

	/* install package */
	openlog("installpackage", LOG_PID, LOG_USER);
	snprintf(command, STRING_SIZE - 1, "%s/setup", tmpdir);
	/* FIXME: popen suffers from the same environment problems as system() */
	if (!(p = popen(command, "r")))
	{
		fprintf(stderr,"popen() failed\n");
		closelog();
		exit(ERR_POPEN);
	}
	setvbuf(p, NULL, _IOLBF, 255);
	while (fgets(buffer, STRING_SIZE, p))
	{
		syslog(LOG_INFO, "%s", buffer);
	}
	ret = pclose(p);
	closelog();

	if(ret)
	{
		fprintf(stderr, "setup script returned exit code %d\n", ret>>8);
		exit(ERR_SETUP);
	}

	/* write to package db */
	if(strncmp(info, "000|", 4))
	{
		time_t curtime = time(NULL);
		strftime(buffer, STRING_SIZE, "%Y-%m-%d", gmtime(&curtime));
		fprintf(infofile, "%s|%s\n", info, buffer);
		flock(fileno(infofile), LOCK_UN);
		fclose(infofile);
	} else { /* Full system upgrade to new version */
		flock(fileno(infofile), LOCK_UN);
		fclose(infofile);
		unlink(CONFIG_ROOT "/patches/available");
		unlink(CONFIG_ROOT "/patches/installed");
	}
	free(info);
	exit(0);
}
