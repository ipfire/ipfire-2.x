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
		fprintf(stderr, "\nNo argument given.\n\ntimectrl (start|stop|restart)\n\n");
		exit(1);
	}

	if (strcmp(argv[1], "start") == 0) {
		safe_system("/etc/rc.d/init.d/ntp start");
	} else if (strcmp(argv[1], "stop") == 0) {
		safe_system("/etc/rc.d/init.d/ntp stop");
	} else if (strcmp(argv[1], "restart") == 0) {
		safe_system("/etc/rc.d/init.d/ntp restart");
	} else if (strcmp(argv[1], "enable") == 0) {
		safe_system("ln -fs ../init.d/ntp /etc/rc.d/rc3.d/S26ntpd >/dev/null 2>&1");
		safe_system("ln -fs ../init.d/ntp /etc/rc.d/rc0.d/K46ntpd >/dev/null 2>&1");
		safe_system("ln -fs ../init.d/ntp /etc/rc.d/rc6.d/K46ntpd >/dev/null 2>&1");
		safe_system("/etc/rc.d/init.d/ntp start");
	} else if (strcmp(argv[1], "disable") == 0) {
		safe_system("/etc/rc.d/init.d/ntp stop");
		safe_system("rm -f /etc/rc.d/rc*.d/*ntpd >/dev/null 2>&1");
	} else {
		fprintf(stderr, "\nBad argument given.\n\ntimectrl (start|stop|restart)\n\n");
		exit(1);
	}

	return 0;
}
