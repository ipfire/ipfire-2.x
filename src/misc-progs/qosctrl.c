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

	int fd = -1;

	if (!(initsetuid()))
		exit(1);

	if (argc < 2) {
		fprintf(stderr, "\nNo argument given.\n\nqosctrl (start|stop|restart|status|generate)\n\n");
		exit(1);
	}
	
	if ((fd = open("/var/ipfire/qos/bin/qos.sh", O_RDONLY)) != -1) {
		close(fd);
	} else {
		// If there is no qos.sh do nothing.
		exit(0);
	}
	
	safe_system("chmod 755 /var/ipfire/qos/bin/qos.sh &>/dev/null");
	if (strcmp(argv[1], "start") == 0) {
		safe_system("/var/ipfire/qos/bin/qos.sh start");	
	} else if (strcmp(argv[1], "stop") == 0) {
		safe_system("/var/ipfire/qos/bin/qos.sh clear");
	} else if (strcmp(argv[1], "status") == 0) {
		safe_system("/var/ipfire/qos/bin/qos.sh status");
	} else if (strcmp(argv[1], "restart") == 0) {
		safe_system("/var/ipfire/qos/bin/qos.sh restart");
	} else if (strcmp(argv[1], "generate") == 0) {
		safe_system("/usr/bin/perl /var/ipfire/qos/bin/makeqosscripts.pl > /var/ipfire/qos/bin/qos.sh");
	} else {
		fprintf(stderr, "\nBad argument given.\n\nqosctrl (start|stop|restart|status|generate)\n\n");
		exit(1);
	}

	return 0;
}
