/* This file is part of the IPFire Firewall.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 */

#include <unistd.h>

#include "setuid.h"

int main(int argc, char *argv[]) {
	if (!(initsetuid()))
		exit(1);

	int retval = safe_system("/usr/lib/firewall/rules.pl");

	/* If rules.pl has been successfully executed, the indicator
	 * file is removed. */
	if (retval == 0) {
		unlink("/var/ipfire/firewall/reread");
	}

	return 0;
}
