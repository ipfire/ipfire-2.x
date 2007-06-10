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
	int i;
	char command; // Add size here
	char add; // Add size here
	
	if (!(initsetuid()))
		exit(1);

	sprintf(command, "/opt/pakfire/pakfire");

	for (i = 0; i < argc - 1; i++) {
		sprintf(add, " %s", argv[i]);
		strcat(command, add);
	}
	
	return safe_system(command);
	
}
