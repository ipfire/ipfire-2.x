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
		fprintf(stderr, "\nNo argument given.\n\nsmartctrl <device>\n\n");
		exit(1);
	}

	if (!is_valid_argument_alnum(argv[1])) {
		fprintf(stderr, "Invalid device name '%s'\n", argv[1]);
		exit(2);
	}

	char command[STRING_SIZE];
	snprintf(command, STRING_SIZE, "/var/run/hddshutdown-%s", argv[1]);

        FILE *fp = fopen(command, "r");
	if (fp != NULL) {
		fclose(fp);

		printf("\nDisk %s is in Standby. Do nothing because we won't wakeup\n",argv[1]);
		exit(1);
	}

	snprintf(command, STRING_SIZE, "smartctl -iHA /dev/%s", argv[1]);
	safe_system(command);

        return 0;
}
