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
		fprintf(stderr, "\nNo argument given.\n\nsuricatactrl (start|stop|restart|reload)\n\n");
		exit(1);
	}

	if (strcmp(argv[1], "start") == 0) {
		safe_system("/etc/rc.d/init.d/suricata start");
	} else if (strcmp(argv[1], "stop") == 0) {
		safe_system("/etc/rc.d/init.d/suricata stop");
	} else if (strcmp(argv[1], "restart") == 0) {
		safe_system("/etc/rc.d/init.d/suricata restart");
	} else if (strcmp(argv[1], "reload") == 0) {
		safe_system("/etc/rc.d/init.d/suricata reload");
	} else if (strcmp(argv[1], "fix-rules-dir") == 0) {
		safe_system("chown -R nobody:nobody /var/lib/suricata");
	} else if (strcmp(argv[1], "cron") == 0) {
			safe_system("rm /etc/fcron.*/suricata >/dev/null 2>&1");
		if (strcmp(argv[2], "off") == 0) {
			return(1);
		} else if (strcmp(argv[2], "daily") == 0){
                        safe_system("ln -s /usr/local/bin/update-ids-ruleset /etc/fcron.daily/suricata");
                } else if (strcmp(argv[2], "weekly") == 0){
                        safe_system("ln -s /usr/local/bin/update-ids-ruleset /etc/fcron.weekly/suricata");
                } else{
                        printf("invalid parameter(s)\n");
                return(1);
                }
	} else {
		fprintf(stderr, "\nBad argument given.\n\nsuricatactrl (start|stop|restart|reload)\n\n");
		exit(1);
	}

	return 0;
}
