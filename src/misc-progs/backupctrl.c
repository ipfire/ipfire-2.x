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
	char command[STRING_SIZE] = "/var/ipfire/backup/bin/backup.pl";
	char temp[STRING_SIZE];

	if (!(initsetuid()))
		exit(1);

	for (i = 1; i < argc; i++) {
		if (strstr(argv[i], "&&")){
			fprintf (stderr, "Bad Argument!\n");
			exit (1);

		} else if (strstr(argv[i], "|")) {
			fprintf (stderr, "Bad Argument!\n");
			exit (1);

		} else if (argc > 3) {
			fprintf (stderr, "Too Many Arguments!\n");
			exit (1);

		} else {
			snprintf(temp, STRING_SIZE, "%s %s", command, argv[i]);
			snprintf(command, STRING_SIZE, "%s", temp);
		}
	}

	return safe_system(command);
}
