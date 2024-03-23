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
	const char* command = NULL;

	// Become root
	if (!initsetuid())
		exit(1);

	// Check if we have enough arguments
	if (argc < 2) {
		fprintf(stderr, "\nNot enough arguments.\n\n");
		exit(1);
	}

	// Roadwarrior
	if (strcmp(argv[1], "rw") == 0) {
		command = "/etc/rc.d/init.d/openvpn-rw";

	// N2N
	} else if (strcmp(argv[1], "n2n") == 0) {
		command = "/etc/rc.d/init.d/openvpn-n2n";

	// Unknown
	} else {
		fprintf(stderr, "Invalid connection type '%s'\n", argv[1]);
		exit(1);
	}

	return run(command, argv + 2);
}
