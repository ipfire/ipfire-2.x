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

#define BUFFER_SIZE 1024

int main(int argc, char *argv[]) {
	char command[BUFFER_SIZE];

	if (!(initsetuid()))
		exit(1);

	if (argc < 3) {
		fprintf(stderr, "\nMissing arguments.\n\naddonctrl addon (start|stop|restart|reload|enable|disable)\n\n");
		exit(1);
	}

	const char* name = argv[1];

	if (strlen(name) > 32) {
	    fprintf(stderr, "\nString to large.\n\naddonctrl addon (start|stop|restart|reload|enable|disable)\n\n");
	    exit(1);
	}

	// Check if the input argument is valid
	if (!is_valid_argument_alnum(name)) {
		fprintf(stderr, "Invalid add-on name: %s\n", name);
		exit(2);
	}

	sprintf(command, "/opt/pakfire/db/installed/meta-%s", name);
	FILE *fp = fopen(command,"r");
	if ( fp ) {
	    fclose(fp);
	} else {
	    fprintf(stderr, "\nAddon '%s' not found.\n\naddonctrl addon (start|stop|restart|reload|status|enable|disable)\n\n", name);
	    exit(1);
	}

	if (strcmp(argv[2], "start") == 0) {
		snprintf(command, BUFFER_SIZE - 1, "/etc/rc.d/init.d/%s start", name);
		safe_system(command);
	} else if (strcmp(argv[2], "stop") == 0) {
		snprintf(command, BUFFER_SIZE - 1, "/etc/rc.d/init.d/%s stop", name);
		safe_system(command);
	} else if (strcmp(argv[2], "restart") == 0) {
		snprintf(command, BUFFER_SIZE - 1, "/etc/rc.d/init.d/%s restart", name);
		safe_system(command);
	} else if (strcmp(argv[2], "reload") == 0) {
		snprintf(command, BUFFER_SIZE - 1, "/etc/rc.d/init.d/%s reload", name);
		safe_system(command);
	} else if (strcmp(argv[2], "status") == 0) {
		snprintf(command, BUFFER_SIZE - 1, "/etc/rc.d/init.d/%s status", name);
		safe_system(command);
	} else if (strcmp(argv[2], "enable") == 0) {
		snprintf(command, BUFFER_SIZE - 1, "mv -f /etc/rc.d/rc3.d/off/S??%s /etc/rc.d/rc3.d" , name);
		safe_system(command);
	} else if (strcmp(argv[2], "disable") == 0) {
		snprintf(command, BUFFER_SIZE - 1, "mkdir -p /etc/rc.d/rc3.d/off");
		safe_system(command);
		snprintf(command, BUFFER_SIZE - 1, "mv -f /etc/rc.d/rc3.d/S??%s /etc/rc.d/rc3.d/off" , name);
		safe_system(command);
	} else {
		fprintf(stderr, "\nBad argument given.\n\naddonctrl addon (start|stop|restart|reload|enable|disable)\n\n");
		exit(1);
	}

	return 0;
}
