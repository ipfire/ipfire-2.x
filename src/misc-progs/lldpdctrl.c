/* This file is part of the IPFire Firewall.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 */

#include <stdio.h>
#include <string.h>

#include "setuid.h"

int main(int argc, char** argv) {
	// Become root
	if (!initsetuid())
		exit(1);

	// Check if we have enough arguments
	if (argc < 2) {
		fprintf(stderr, "\nNot enough arguments.\n\n");
		exit(1);
	}

	if (strcmp(argv[1], "start") == 0)
		return run("/etc/rc.d/init.d/lldpd", argv + 1);

	else if (strcmp(argv[1], "stop") == 0)
		return run("/etc/rc.d/init.d/lldpd", argv + 1);

	else if (strcmp(argv[1], "restart") == 0)
		return run("/etc/rc.d/init.d/lldpd", argv + 1);
 
	fprintf(stderr, "Invalid command\n");
	exit(1);
}
