/* This file is part of the IPCop Firewall.
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
 * Copyright (C) 2003-04-22 Robert Kerr <rkerr@go.to>
 *
 * $Id: setuid.c,v 1.2.2.1 2005/11/18 14:51:43 franck78 Exp $
 *
 */

#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <limits.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <grp.h>
#include <signal.h>
#include <sys/wait.h>
#include <glob.h>
#include "setuid.h"

#ifndef OPEN_MAX
#define OPEN_MAX 256
#endif

/* Trusted environment for executing commands */
char * trusted_env[4] = {
	"PATH=/usr/bin:/usr/sbin:/sbin:/bin",
	"SHELL=/bin/sh",
	"TERM=dumb",
	NULL
};

/* Spawns a child process that uses /bin/sh to interpret a command.
 * This is much the same in use and purpose as system(), yet as it uses execve
 * to pass a trusted environment it's immune to attacks based upon changing
 * IFS, ENV, BASH_ENV and other such variables.
 * Note this does NOT guard against any other attacks, inparticular you MUST
 * validate the command you are passing. If the command is formed from user
 * input be sure to check this input is what you expect. Nasty things can
 * happen if a user can inject ; or `` into your command for example */
int safe_system(char* command) {
	return system_core(command, 0, 0, "safe_system");
}

/* Much like safe_system but lets you specify a non-root uid and gid to run
 * the command as */
int unpriv_system(char* command, uid_t uid, gid_t gid) {
	return system_core(command, uid, gid, "unpriv_system");
}

int system_core(char* command, uid_t uid, gid_t gid, char *error) {
	int pid, status;

	if(!command)
		return 1;

	switch(pid = fork()) {
		case -1:
			return -1;

		case 0: /* child */ {
			char *argv[4];

			if (gid && setgid(gid))	{
				fprintf(stderr, "%s: ", error);
				perror("Couldn't setgid");
				exit(127);
			}

			if (uid && setuid(uid)) {
				fprintf(stderr, "%s: ", error);
				perror("Couldn't setuid");
				exit(127);
			}

			argv[0] = "sh";
			argv[1] = "-c";
			argv[2] = command;
			argv[3] = NULL;
			execve("/bin/sh", argv, trusted_env);
			fprintf(stderr, "%s: ", error);
			perror("execve failed");
			exit(127);
		}

		default: /* parent */
			do {
				if (waitpid(pid, &status, 0) == -1) {
					if (errno != EINTR)
						return -1;
					} else {
						return status;
					}
			} while (1);
	}

}

/* General routine to initialise a setuid root program, and put the
 * environment in a known state. Returns 1 on success, if initsetuid() returns
 * 0 then you should exit(1) immediately, DON'T attempt to recover from the
 * error */
int initsetuid(void) {
	int fds, i;
	struct stat st;
	struct rlimit rlim;

	/* Prevent signal tricks by ignoring all except SIGKILL and SIGCHILD */
	for (i = 0; i < NSIG; i++) {
		if (i != SIGKILL && i != SIGCHLD)
			signal(i, SIG_IGN);
	}

	/* dump all non-standard file descriptors (a full descriptor table could
	 * lead to DoS by preventing us opening files) */
	if ((fds = getdtablesize()) == -1)
		fds = OPEN_MAX;
	for (i = 3; i < fds; i++)
		close(i);

	/* check stdin, stdout & stderr are open before going any further */
	for (i = 0; i < 3; i++)
		if( fstat(i, &st) == -1 && ((errno != EBADF) || (close(i), open("/dev/null", O_RDWR, 0)) != i))
			return 0;

	/* disable core dumps in case we're processing sensitive information */
	rlim.rlim_cur = rlim.rlim_max = 0;
	if (setrlimit(RLIMIT_CORE, &rlim)) {
		perror("Couldn't disable core dumps");
		return 0;
	}

	/* drop any supplementary groups, set uid & gid to root */
	if (setgroups(0, NULL)) {
		perror("Couldn't clear group list");
		return 0;
	}

	if (setgid(0)) {
		perror("Couldn't setgid(0)");
		return 0;
	}

	if (setuid(0)) {
		perror("Couldn't setuid(0)");
		return 0;
	}

	return 1;
}
