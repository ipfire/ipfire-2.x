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
#include "libsmooth.h"

#define QOS_SH "/var/ipfire/qos/bin/qos.sh"

int main(int argc, char *argv[]) {
	struct keyvalue* kv = NULL;
        int fd = -1;
	int r = 0;

        if (!(initsetuid()))
                exit(1);

        if (argc < 2) {
                fprintf(stderr, "\nNo argument given.\n\nqosctrl (start|stop|restart|status|generate)\n\n");
                exit(1);
        }

        if (strcmp(argv[1], "generate") == 0) {
		kv = initkeyvalues();
		if (!readkeyvalues(kv, CONFIG_ROOT "/qos/settings")) {
			fprintf(stderr, "Cannot read QoS settings\n");
			r = 1;
			goto END;
		}

		char enabled[STRING_SIZE];
		if (!findkey(kv, "ENABLED", enabled))
			strcpy(enabled, "off");

		if (strcmp(enabled, "on") == 0)
	                safe_system("/usr/bin/perl /var/ipfire/qos/bin/makeqosscripts.pl > " QOS_SH);
		else
			unlink(QOS_SH);
        }

        if ((fd = open(QOS_SH, O_RDONLY)) != -1) {
                close(fd);
        } else {
                // If there is no qos.sh do nothing.
                goto END;
        }

        safe_system("chmod 755 " QOS_SH " &>/dev/null");
        if (strcmp(argv[1], "start") == 0) {
                safe_system(QOS_SH " start");
        } else if (strcmp(argv[1], "stop") == 0) {
                safe_system(QOS_SH " clear");
        } else if (strcmp(argv[1], "status") == 0) {
                safe_system(QOS_SH " status");
        } else if (strcmp(argv[1], "restart") == 0) {
                safe_system(QOS_SH " restart");
        } else {
                if (strcmp(argv[1], "generate") == 0) {exit(0);}
                fprintf(stderr, "\nBad argument given.\n\nqosctrl (start|stop|restart|status|generate)\n\n");
                exit(1);
        }

END:
	if (kv)
		freekeyvalues(kv);

        return r;
}
