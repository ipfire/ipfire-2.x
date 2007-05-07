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
		fprintf(stderr, "\nNo argument given.\n\ndhcpctrl (start|stop|restart|reload)\n\n");
		exit(1);
	}

	if (strcmp(argv[1], "start") == 0) {
		safe_system("/etc/rc.d/init.d/dhcp start");
	} else if (strcmp(argv[1], "stop") == 0) {
		safe_system("/etc/rc.d/init.d/dhcp stop");
	} else if (strcmp(argv[1], "restart") == 0) {
		safe_system("/etc/rc.d/init.d/dhcp restart");
	} else if (strcmp(argv[1], "reload") == 0) {
		safe_system("/etc/rc.d/init.d/dhcp reload");
	} else if (strcmp(argv[1], "enable") == 0) {
		safe_system("ln -fs ../init.d/dhcp /etc/rc.d/rc3.d/S30dhcp >/dev/null 2>&1");
		safe_system("ln -fs ../init.d/dhcp /etc/rc.d/rc0.d/K30dhcp >/dev/null 2>&1");
		safe_system("ln -fs ../init.d/dhcp /etc/rc.d/rc6.d/K30dhcp >/dev/null 2>&1");
	} else if (strcmp(argv[1], "disable") == 0) {
		safe_system("rm -f /etc/rc.d/rc*.d/*dhcp >/dev/null 2>&1");
	} else {
		fprintf(stderr, "\nBad argument given.\n\ndhcpctrl (start|stop|restart|reload)\n\n");
		exit(1);
	}

	return 0;
}
