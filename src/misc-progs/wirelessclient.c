/* IPFire helper program - wirelessclient
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 */

#include <stdio.h>
#include <stdlib.h>
#include "setuid.h"

int main(int argc, char *argv[]) {
	if (!(initsetuid()))
		exit(1);

	if (strcmp(argv[1], "restart") == 0) {
		safe_system("/etc/rc.d/init.d/wlanclient restart >/dev/null 2>&1");
		return 0;
	}

	if (strcmp(argv[1], "status") == 0) {
		safe_system("/usr/sbin/wpa_cli status verbose");
		return 0;
	}

	return 0;
}
