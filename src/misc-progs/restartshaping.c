/* IPCop helper program - restartshaping
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * Copyright (C) 2002-04-09 Mark Wormgoor <mark@wormgoor.com>
 *
 * $Id: restartshaping.c,v 1.2.2.5 2005/01/28 13:11:40 riddles Exp $
 *
 */

#include "libsmooth.h"
#include "setuid.h"
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
	FILE *file = NULL, *ifacefile = NULL;
	struct keyvalue *kv = NULL;
	int uplink, downlink, count = 0, r2q = 10;
	char command[STRING_SIZE];
	char iface[STRING_SIZE] = "";
	char s[STRING_SIZE];
	char *result;
	char proto[STRING_SIZE];
	char *protocol;
	char *port;
	char *prio;
	char *enabled;

	if (!(initsetuid())) {
		fprintf(stderr, "Cannot run setuid\n");
		exit(1);
	}

	/* Init the keyvalue structure */
	kv=initkeyvalues();

	/* Read in the current values */
	if (!readkeyvalues(kv, CONFIG_ROOT "/shaping/settings"))
	{
		fprintf(stderr, "Cannot read shaping settings\n");
		goto EXIT;
	}

	/* See what interface there is */
	if ((ifacefile = fopen(CONFIG_ROOT "/red/iface", "r")))
	{
		fgets(iface, STRING_SIZE, ifacefile);
		if (iface[strlen(iface) - 1] == '\n')
			iface[strlen(iface) - 1] = '\0';
		fclose (ifacefile);
	} else {
		fprintf(stderr, "Couldn't open iface file\n");
		return(1);
	}

	if (strspn(iface, LETTERS_NUMBERS) != strlen(iface))
	{
		fprintf(stderr, "Bad iface: %s\n", iface);
		goto EXIT;
	}

	/* Find the VALID value */
	if (!findkey(kv, "VALID", s))
	{
		fprintf(stderr, "Cannot read VALID\n");
		goto EXIT;
	}

	/* Check if config is VALID */
	if (! strcmp(s, "yes")==0)
		goto EXIT;

	snprintf(command, STRING_SIZE-1, "/sbin/tc qdisc del dev %s root", iface);
	safe_system(command);
	snprintf(command, STRING_SIZE-1, "/sbin/tc qdisc del dev %s ingress", iface);
	safe_system(command);

	/* Find the ENABLE value */
	if (!findkey(kv, "ENABLE", s))
	{
		fprintf(stderr, "Cannot read ENABLE\n");
		goto EXIT;
	}

	/* Check if shaping is ENABLED */
	if (! strcmp(s, "on")==0)
		goto EXIT;

	/* Find the UPLINK value */
	if (!findkey(kv, "UPLINK", s))
	{
		fprintf(stderr, "Cannot read UPLINK\n");
		goto EXIT;
	}
	uplink = atoi(s);
	if (! uplink > 0) {
		fprintf(stderr, "Invalid value for UPLINK\n");
		goto EXIT;
	}
	/* In some limited testing, it was shown that 
		r2q = ( uplink * 1024 / 1500 );
	 * produced error messages from the kernel saying r2q needed to be
	 * changed. 1500 is taken as the MTU, but it seems that 16384 works
	 * better. -Alan.
	 */
	r2q = ( uplink * 1024 / 16384 );
	uplink = (uplink * 100) / 101;

	/* Find the DOWNLINK value */
	if (!findkey(kv, "DOWNLINK", s))
	{
		fprintf(stderr, "Cannot read DOWNLINK\n");
		goto EXIT;
	}
	downlink = atoi(s);
	if (! downlink > 0) {
		fprintf(stderr, "Invalid value for DOWNLINK\n");
		goto EXIT;
	}
	downlink = (downlink * 200) / 201;

	/* Uplink classes */
	snprintf(command, STRING_SIZE-1, "/sbin/tc qdisc add dev %s root handle 1: htb default 20 r2q %d", iface, r2q);
	safe_system(command);
	snprintf(command, STRING_SIZE-1, "/sbin/tc class add dev %s parent 1: classid 1:1 htb rate %dkbit", iface, uplink);
	safe_system(command);
	snprintf(command, STRING_SIZE-1, "/sbin/tc class add dev %s parent 1:1 classid 1:10 htb rate %dkbit ceil %dkbit prio 1", iface, (8 * uplink) / 10, uplink);
	safe_system(command);
	snprintf(command, STRING_SIZE-1, "/sbin/tc class add dev %s parent 1:1 classid 1:20 htb rate %dkbit ceil %dkbit prio 2", iface, (6 * uplink) / 10, uplink);
	safe_system(command);
	snprintf(command, STRING_SIZE-1, "/sbin/tc class add dev %s parent 1:1 classid 1:30 htb rate %dkbit ceil %dkbit prio 3", iface, (4 * uplink) / 10, uplink);
	safe_system(command);

	/* Uplink Stochastic fairness queue */
	snprintf(command, STRING_SIZE-1, "/sbin/tc qdisc add dev %s parent 1:10 handle 10: sfq perturb 10", iface);
	safe_system(command);
	snprintf(command, STRING_SIZE-1, "/sbin/tc qdisc add dev %s parent 1:20 handle 20: sfq perturb 10", iface);
	safe_system(command);
	snprintf(command, STRING_SIZE-1, "/sbin/tc qdisc add dev %s parent 1:30 handle 30: sfq perturb 10", iface);
	safe_system(command);

	/* TOS Minimum Delay and ICMP traffic for high priority queue */
 	snprintf(command, STRING_SIZE-1, "/sbin/tc filter add dev %s parent 1:0 protocol ip prio 10 u32 match ip tos 0x10 0xff flowid 1:10", iface);
	safe_system(command);
	snprintf(command, STRING_SIZE-1, "/sbin/tc filter add dev %s parent 1:0 protocol ip prio 10 u32 match ip protocol 1 0xff flowid 1:10", iface);
	safe_system(command);

	/* ACK packets for high priority queue (to speed up downloads) */
	snprintf(command, STRING_SIZE-1, "/sbin/tc filter add dev %s parent 1: protocol ip prio 10 u32 match ip protocol 6 0xff match u8 0x05 0x0f at 0 match u16 0x0000 0xffc0 at 2 match u8 0x10 0xff at 33 flowid 1:10", iface);
	safe_system(command);

	file = fopen(CONFIG_ROOT "/shaping/config", "r");
	if (file)
        {
	        while (fgets(s, STRING_SIZE, file) != NULL)
	        {
	                if (s[strlen(s) - 1] == '\n')
        	                s[strlen(s) - 1] = '\0';
	                result = strtok(s, ",");

			count = 0;
			protocol = NULL;
			port = NULL;
			prio = NULL;
			enabled = NULL;
			while (result)
			{
				if (count == 0)
					protocol = result;
				else if (count == 1)
					port = result;
				else if (count == 2)
					prio = result;
				else if (count == 3)
					enabled = result;
				count++;
				result = strtok(NULL, ",");
			}
			if (!(protocol && port && prio && enabled))
				break;
			if (strcmp(protocol, "tcp") == 0) {
				strcpy(proto, "6");
			} else if (strcmp(protocol, "udp") == 0) {
				strcpy(proto, "17");
			} else {
				fprintf(stderr, "Bad protocol: %s\n", protocol);
				goto EXIT;
			}
			if (strspn(port, PORT_NUMBERS) != strlen(port))
			{
				fprintf(stderr, "Bad port: %s\n", port);
				goto EXIT;
			}
			if (strspn(prio, NUMBERS) != strlen(prio))
			{
				fprintf(stderr, "Bad priority: %s\n", prio);
				goto EXIT;
			}

			if (strcmp(enabled, "on") == 0)
			{
				snprintf(command, STRING_SIZE-1, "/sbin/tc filter add dev %s parent 1: protocol ip prio 14 u32 match ip protocol %s 0xff match ip dport %s 0xffff flowid 1:%s", iface, proto, port, prio);

				safe_system(command);

				snprintf(command, STRING_SIZE-1, "/sbin/tc filter add dev %s parent 1: protocol ip prio 15 u32 match ip protocol %s 0xff match ip sport %s 0xffff flowid 1:%s", iface, proto, port, prio);

				safe_system(command);
			}
		}
	}

	/* Setting everything else to the default queue */
	snprintf(command, STRING_SIZE-1, "/sbin/tc filter add dev %s parent 1: protocol ip prio 18 u32 match ip dst 0.0.0.0/0 flowid 1:20", iface);
	safe_system(command);

	/* Downlink Section */
	snprintf(command, STRING_SIZE-1, "/sbin/tc qdisc add dev %s handle ffff: ingress", iface);
	safe_system(command);
	snprintf(command, STRING_SIZE-1, "/sbin/tc filter add dev %s parent ffff: protocol ip prio 50 u32 match ip src 0.0.0.0/0 police rate %dkbit burst 10k drop flowid :1", iface, downlink);
	safe_system(command);

EXIT:
	if (kv) freekeyvalues(kv);
	if (file) fclose(file);
	return 0;
}
