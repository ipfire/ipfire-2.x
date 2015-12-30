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
#include "setuid.h"

int main(int argc, char *argv[]) {
	if (!(initsetuid()))
		exit(1);

	if (argc < 2) {
		fprintf(stderr, "\nNo argument given.\n\ncollectdctrl (start|stop|restart)\n\n");
		exit(1);
	}

	if (strcmp(argv[1], "restart") == 0) {
		safe_system("/etc/rc.d/init.d/collectd restart");

	} else if (strcmp(argv[1], "stop") == 0) {
		safe_system("/etc/rc.d/init.d/collectd stop");

	} else if (strcmp(argv[1], "start") == 0) {
		safe_system("/etc/rc.d/init.d/collectd start");

	} else {
		fprintf(stderr, "\nBad argument given.\n\ncollectdctrl (start|stop|restart)\n\n");
		exit(1);
	}

	return 0;
}
