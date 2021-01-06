/* This file is part of the IPFire Firewall.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 */

#include "setuid.h"

int main(int argc, char** argv) {
	if (!initsetuid())
		exit(1);

	return run("/var/ipfire/backup/bin/backup.pl", argv);
}
