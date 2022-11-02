/* IPCop helper program - wirelessctrl
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Alan Hourihane, 2003
 *
 */

#include "libsmooth.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <signal.h>
#include <errno.h>

#include "setuid.h"
#include "netutil.h"

FILE *fd = NULL;
char blue_dev[STRING_SIZE] = "";
char command[STRING_SIZE];

void exithandler(void) {
	/* added comment mark to the drop rules to be able to collect the bytes by the collectd */
	if (strlen(blue_dev) > 0) {
		snprintf(command, STRING_SIZE-1, "/sbin/iptables --wait -A WIRELESSINPUT -i %s -j DROP -m comment --comment 'DROP_Wirelessinput'", blue_dev);
		safe_system(command);
		snprintf(command, STRING_SIZE-1, "/sbin/iptables --wait -A WIRELESSFORWARD -i %s -j DROP -m comment --comment 'DROP_Wirelessforward'", blue_dev);
		safe_system(command);
	}

	if (fd)
		fclose(fd);
}

int main(void) {
	char buffer[STRING_SIZE];
	char *index, *ipaddress, *macaddress, *enabled;
	struct keyvalue *kv = NULL;
	struct keyvalue* captive_settings = NULL;

	if (!(initsetuid()))
		exit(1);

	/* flush wireless iptables */
	safe_system("/sbin/iptables --wait -F WIRELESSINPUT > /dev/null 2> /dev/null");
	safe_system("/sbin/iptables --wait -F WIRELESSFORWARD > /dev/null 2> /dev/null");

	memset(buffer, 0, STRING_SIZE);

	/* Init the keyvalue structure */
	kv=initkeyvalues();

	/* Read in the current values */
	if (!readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings")) {
		fprintf(stderr, "Cannot read ethernet settings\n");
		exit(1);
	}

	/* Read in the firewall values */
	if (!readkeyvalues(kv, CONFIG_ROOT "/optionsfw/settings")) {
		fprintf(stderr, "Cannot read optionsfw settings\n");
		exit(1);
	}

	// Read captive portal settings
	captive_settings = initkeyvalues();
	if (!readkeyvalues(captive_settings, CONFIG_ROOT "/captive/settings")) {
		fprintf(stderr, "Could not read captive portal settings\n");
		exit(1);
	}

	/* Get the BLUE interface details */
	if (findkey(kv, "BLUE_DEV", blue_dev) > 0) {
		if ((strlen(blue_dev) > 0) && !VALID_DEVICE(blue_dev)) {
			fprintf(stderr, "Bad BLUE_DEV: %s\n", blue_dev);
			exit(1);
		}
	}

	if (strlen(blue_dev) == 0) {
		exit(0);
	}

	// Check if the captive portal is enabled on blue. If so, we will
	// just keep the chains flushed and do not add any rules.
	char captive_enabled[STRING_SIZE];
	if (findkey(captive_settings, "ENABLE_BLUE", captive_enabled) > 0) {
		if (strcmp(captive_enabled, "on") == 0) {
			return 0;
		}
	}

	if ((fd = fopen(CONFIG_ROOT "/wireless/nodrop", "r")))
		return 0;

	/* register exit handler to ensure the block rule is always present */
	atexit(exithandler);

	if (!(fd = fopen(CONFIG_ROOT "/wireless/config", "r"))) {
		exit(0);
	}

	/* restrict blue access tp the proxy port */
	if (findkey(kv, "DROPPROXY", buffer) && strcmp(buffer, "on") == 0) {
		/* Read the proxy values */
		if (!readkeyvalues(kv, CONFIG_ROOT "/proxy/settings") || !(findkey(kv, "PROXY_PORT", buffer))) {
			fprintf(stderr, "Cannot read proxy settings\n");
			exit(1);
		}

		snprintf(command, STRING_SIZE-1, "/sbin/iptables --wait -A WIRELESSFORWARD -i %s -p tcp  ! --dport %s -j DROP -m comment --comment 'DROP_Wirelessforward'", blue_dev, buffer);
		safe_system(command);
		snprintf(command, STRING_SIZE-1, "/sbin/iptables --wait -A WIRELESSINPUT -i %s -p tcp  ! --dport %s -j DROP -m comment --comment 'DROP_Wirelessinput'", blue_dev, buffer);
		safe_system(command);
	}

	/* not allow blue to acces a samba server running on local fire*/
	if (findkey(kv, "DROPSAMBA", buffer) && strcmp(buffer, "on") == 0) {
		snprintf(command, STRING_SIZE-1, "/sbin/iptables --wait -A WIRELESSFORWARD -i %s -p tcp -m multiport --ports 135,137,138,139,445,1025 -j DROP -m comment --comment 'DROP_Wirelessforward'", blue_dev);
		safe_system(command);
		snprintf(command, STRING_SIZE-1, "/sbin/iptables --wait -A WIRELESSINPUT -i %s -p tcp -m multiport --ports 135,137,138,139,445,1025 -j DROP -m comment --comment 'DROP_Wirelessinput'", blue_dev);
		safe_system(command);
		snprintf(command, STRING_SIZE-1, "/sbin/iptables --wait -A WIRELESSFORWARD -i %s -p udp -m multiport --ports 135,137,138,139,445,1025 -j DROP -m comment --comment 'DROP_Wirelessforward'", blue_dev);
		safe_system(command);
		snprintf(command, STRING_SIZE-1, "/sbin/iptables --wait -A WIRELESSINPUT -i %s -p udp -m multiport --ports 135,137,138,139,445,1025 -j DROP -m comment --comment 'DROP_Wirelessinput'", blue_dev);
		safe_system(command);
	}

	while (fgets(buffer, STRING_SIZE, fd)) {
		buffer[strlen(buffer) - 1] = 0;

		index = strtok(buffer, ",");
		ipaddress = strtok(NULL, ",");
		macaddress = strtok(NULL, ",");
		enabled = strtok(NULL, ",");

		if (strcmp(enabled, "on") == 0) {
			/* both specified, added security */
			if ((strlen(macaddress) == 17) && (VALID_IP_AND_MASK(ipaddress))) {
				snprintf(command, STRING_SIZE-1, "/sbin/iptables --wait -A WIRELESSINPUT -m mac --mac-source %s -s %s -i %s -j RETURN", macaddress, ipaddress, blue_dev);
				safe_system(command);
				snprintf(command, STRING_SIZE-1, "/sbin/iptables --wait -A WIRELESSFORWARD -m mac --mac-source %s -s %s -i %s -j RETURN", macaddress, ipaddress, blue_dev);
				safe_system(command);
			} else {
				/* correctly formed mac address is 17 chars */
				if (strlen(macaddress) == 17) {
					snprintf(command, STRING_SIZE-1, "/sbin/iptables --wait -A WIRELESSINPUT -m mac --mac-source %s -i %s -j RETURN", macaddress, blue_dev);
					safe_system(command);
					snprintf(command, STRING_SIZE-1, "/sbin/iptables --wait -A WIRELESSFORWARD -m mac --mac-source %s -i %s -j RETURN", macaddress, blue_dev);
					safe_system(command);
				}

				if (VALID_IP_AND_MASK(ipaddress)) {
					snprintf(command, STRING_SIZE-1, "/sbin/iptables --wait -A WIRELESSINPUT -s %s -i %s -j RETURN", ipaddress, blue_dev);
					safe_system(command);
					snprintf(command, STRING_SIZE-1, "/sbin/iptables --wait -A WIRELESSFORWARD -s %s -i %s -j RETURN", ipaddress, blue_dev);
					safe_system(command);
				}
			}
		}
	}

	/* with this rule you can disable the logging of the dropped wireless input packets*/
	if (findkey(kv, "DROPWIRELESSINPUT", buffer) && strcmp(buffer, "on") == 0) {
		snprintf(command, STRING_SIZE-1, "/sbin/iptables --wait -A WIRELESSINPUT -i %s -j LOG --log-prefix 'DROP_Wirelessinput '", blue_dev);
		safe_system(command);
	}

	/* with this rule you can disable the logging of the dropped wireless forward packets*/
	if (findkey(kv, "DROPWIRELESSFORWARD", buffer) && strcmp(buffer, "on") == 0) {
		snprintf(command, STRING_SIZE-1, "/sbin/iptables --wait -A WIRELESSFORWARD -i %s -j LOG --log-prefix 'DROP_Wirelessforward '", blue_dev);
		safe_system(command);
	}

	return 0;
}
