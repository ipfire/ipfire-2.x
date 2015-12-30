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

#include "setuid.h"

const char *conffile = "/var/ipfire/ddns/ddns.conf";

int main(int argc, char *argv[]) {
	char cmd[STRING_SIZE];

        if (!(initsetuid()))
                exit(1);

        if (argc < 2) {
                fprintf(stderr, "\nNo argument given.\n\nddnsctrl (update-all)\n\n");
                exit(1);
        }

	if (strcmp(argv[1], "update-all") == 0) {
		snprintf(cmd, sizeof(cmd), "/usr/bin/ddns --config %s update-all >/dev/null 2>&1", conffile);
		safe_system(cmd);
	} else {
                fprintf(stderr, "\nBad argument given.\n\nddnsctrl (update-all)\n\n");
                exit(1);
        }

        return 0;
}
