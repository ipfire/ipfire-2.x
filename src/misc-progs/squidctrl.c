/* This file is part of the IPFire Firewall.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 */

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <fcntl.h>
#include "setuid.h"

int main(int argc, char *argv[]) {

	if (!(initsetuid()))
		exit(1);

	if (argc < 2) {
		fprintf(stderr, "\nNo argument given.\n\nsquidctrl (start|stop|restart|flush|reconfigure)\n\n");
		exit(1);
	}

	if (strcmp(argv[1], "start") == 0) {
		safe_system("/etc/rc.d/init.d/squid start");
	} else if (strcmp(argv[1], "stop") == 0) {
		safe_system("/etc/rc.d/init.d/squid stop");
	} else if (strcmp(argv[1], "restart") == 0) {
		safe_system("/etc/rc.d/init.d/squid restart");
	} else if (strcmp(argv[1], "reconfigure") == 0) {
		safe_system("/etc/rc.d/init.d/squid reconfigure");
	} else if (strcmp(argv[1], "flush") == 0) {
		safe_system("/etc/rc.d/init.d/squid flush");
	} else if (strcmp(argv[1], "enable") == 0) {
		safe_system("ln -fs ../init.d/squid /etc/rc.d/rc0.d/K00squid >/dev/null 2>&1");
		safe_system("ln -fs ../init.d/squid /etc/rc.d/rc6.d/K00squid >/dev/null 2>&1");
	} else if (strcmp(argv[1], "disable") == 0) {
		safe_system("rm -f /etc/rc.d/rc*.d/*squid >/dev/null 2>&1");
	} else {
		fprintf(stderr, "\nBad argument given.\n\nsquidctrl (start|stop|restart|flush|reconfigure|setperms)\n\n");
		exit(1);
	}

	return 0;
}
