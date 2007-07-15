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
	char command[1024];
	char add[STRING_SIZE];
	
	if (!(initsetuid()))
		exit(1);

	snprintf(command, STRING_SIZE, "/var/ipfire/mpfire/bin/mpfire.pl");

	for (i = 1; i < argc; i++) {
    if (strstr(argv[i], "&&")){
	    	fprintf (stderr, "Bad Argument!\n");
        exit (1);
    }
		else if (strstr(argv[i], "|")){
		    fprintf (stderr, "Bad Argument!\n");
		    exit (1);
		}
		sprintf(add, " %s", argv[i]);
		strcat(command, add);
	}
	return safe_system(command);
}
