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

	char command[512];
	if (!(initsetuid()))
		exit(1);

	snprintf(command, 512, "/var/ipfire/extrahd/bin/extrahd.pl %s %s", argv[1], argv[2]);
	safe_system("chmod 755 /var/ipfire/extrahd/bin/extrahd.pl 2>&1 >/dev/null");
	safe_system(command);
}
