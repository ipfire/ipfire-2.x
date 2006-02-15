/* Derivated from SmoothWall helper programs
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Daniel Goscomb, 2001
 *
 * Modifications and improvements by Lawrence Manning.
 *
 * 19/04/03 Robert Kerr Fixed root exploit
 *
 * 20/08/05 Achim Weber 20 Modified to have a binary for the new firewall options page in IPCop 1.4.8
 *
 * 02/10/05 Gilles Espinasse treat only ping actually
 *
 * $Id: setfilters.c,v 1.1.2.2 2006/02/07 20:54:16 gespinasse Exp $
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "libsmooth.h"
#include "setuid.h"

struct keyvalue *kv = NULL;
FILE *ifacefile = NULL;

void exithandler(void)
{
	if(kv)
		freekeyvalues(kv);
}

int main(void)
{
	char iface[STRING_SIZE] = "";
	char command[STRING_SIZE];
	char disableping[STRING_SIZE];
	int redAvailable = 1;

	if (!(initsetuid()))
		exit(1);

	atexit(exithandler);

	/* Read in and verify config */
	kv=initkeyvalues();

	if (!readkeyvalues(kv, CONFIG_ROOT "/optionsfw/settings")) {
		fprintf(stderr, "Cannot read firewall option settings\n");
		exit(1);
	}

	if (!findkey(kv, "DISABLEPING", disableping)) {
		fprintf(stderr, "Cannot read DISABLEPING\n");
		exit(1);
	}

	if (strcmp(disableping, "NO") != 0 && strcmp(disableping, "ONLYRED") != 0 && strcmp(disableping, "ALL") != 0) {
		fprintf(stderr, "Bad DISABLEPING: %s\n", disableping);
		exit(1);
	}

	if (!(ifacefile = fopen(CONFIG_ROOT "/red/iface", "r"))) {
		redAvailable = 0;
	} else {
		if (fgets(iface, STRING_SIZE, ifacefile)) {
			if (iface[strlen(iface) - 1] == '\n')
				iface[strlen(iface) - 1] = '\0';
		}
		fclose (ifacefile);
		if (!VALID_DEVICE(iface)) {
			fprintf(stderr, "Bad iface: %s\n", iface);
			exit(1);
		}
		redAvailable = 1;
	}

	safe_system("/sbin/iptables -F GUIINPUT");

	/* don't need to do anything if ping is disabled, so treat only other cases */
	if (strcmp(disableping, "NO") == 0
		|| (strcmp(disableping, "ONLYRED") == 0 && redAvailable == 0)) {
		// We allow ping (icmp type 8) on every interfaces
		// or RED is not available, so we can enable it on all (available) Interfaces
		memset(command, 0, STRING_SIZE);
		snprintf(command, STRING_SIZE - 1, "/sbin/iptables -A GUIINPUT -p icmp --icmp-type 8 -j ACCEPT");
		safe_system(command);
	} else {
		// Allow ping only on internal interfaces
		if(strcmp(disableping, "ONLYRED") == 0) {
			memset(command, 0, STRING_SIZE);
			snprintf(command, STRING_SIZE - 1,
				"/sbin/iptables -A GUIINPUT -i ! %s  -p icmp --icmp-type 8 -j ACCEPT", iface);
			safe_system(command);
		}
	}
	return 0;
}
