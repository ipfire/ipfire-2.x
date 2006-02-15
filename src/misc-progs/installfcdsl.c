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
 * Copyright (C) 2004-10-14 Gilles Espinasse <g.esp.ipcop@free.fr>
 *
 * $Id: installfcdsl.c,v 1.1.2.4 2004/12/11 08:55:37 gespinasse Exp $
 *
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <fcntl.h>
#include <grp.h>
#include "setuid.h"

#define FCDSL_TGZ_PATH "/var/patches/fcdsl-x.tgz"

char	command[STRING_SIZE],tmpdir[] = "/tmp/fcdsl_XXXXXX";

void exithandler(void)
{
	if(strcmp(tmpdir,"/tmp/fcdsl_XXXXXX"))
	{
		chdir("/tmp");
		snprintf(command, STRING_SIZE - 1, "/bin/rm -rf %s", tmpdir);
		if(safe_system(command))
			perror("Couldn't remove temp dir");
	}
	/* remove loaded package */
	snprintf (command, STRING_SIZE-1, FCDSL_TGZ_PATH);
	unlink (command);
}

int main(void)
{
	if (!(initsetuid()))
		exit(1);

	atexit(exithandler);


	if (close(0)) { fprintf(stderr, "Couldn't close 0\n"); exit(1); }
	if (open("/dev/zero", O_RDONLY) != 0) {fprintf(stderr, "Couldn't reopen stdin from /dev/zero\n"); exit(1); }
	if (close(2)) { fprintf(stderr, "Couldn't close 2\n"); exit(1); }
	if (! dup(1)) { fprintf(stderr, "Couldnt redirect stderr to stdout\n"); exit(1); }

	/* create temporary directory for testing untar */
	if (mkdtemp (tmpdir)==NULL) {
	    exit(1);
	}

	/* Test untarring files from compressed archive */
	snprintf (command, STRING_SIZE-1, "/bin/tar -C %s -xzf %s lib/modules/*/misc/fcdsl*.o.gz "
		"usr/lib/isdn/{fds?base.bin,fd?ubase.frm} etc/fcdsl/fcdsl*.conf etc/drdsl/drdsl* "
		"var/run/need-depmod-* > /dev/null 2> /dev/null", tmpdir, FCDSL_TGZ_PATH);
	if (safe_system (command)) {
	    fprintf (stderr, "Invalid archive\n");
	    exit(1);
	}

	/* Start (real) untarring files from compressed archive */
	snprintf (command, STRING_SIZE-1, "/bin/tar -C / -xzvf %s lib/modules/*/misc/fcdsl*.o.gz "
		"usr/lib/isdn/{fds?base.bin,fd?ubase.frm} etc/fcdsl/fcdsl*.conf etc/drdsl/drdsl* "
		"var/run/need-depmod-* ", FCDSL_TGZ_PATH);
	if (safe_system (command)) {
	    fprintf (stderr, "Error installing modules\n");
	    exit(1);
	}

	exit(0);
}
