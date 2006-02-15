/* SmoothWall helper program - setdmzhole
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Daniel Goscomb, 2001
 * 
 * Modifications and improvements by Lawrence Manning.
 *
 * 10/04/01 Aslak added protocol support
 * This program reads the list of ports to forward and setups iptables
 * and rules in ipmasqadm to enable them.
 * 
 * $Id: setdmzholes.c,v 1.5.2.3 2005/10/18 17:05:27 franck78 Exp $
 * 
 */
#include "libsmooth.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "setuid.h"

FILE *fwdfile = NULL;

void exithandler(void)
{
	if (fwdfile)
		fclose(fwdfile);
}

int main(void)
{
	int count;
	char *protocol;
	char *locip;
	char *remip;
	char *remport;
	char *enabled;
	char *src_net;
	char *dst_net;
	char s[STRING_SIZE];
	char *result;
	struct keyvalue *kv = NULL;
	char orange_dev[STRING_SIZE] = "";
	char blue_dev[STRING_SIZE] = "";
	char green_dev[STRING_SIZE] = "";
	char *idev;
	char *odev;
	char command[STRING_SIZE];

	if (!(initsetuid()))
		exit(1);

	atexit(exithandler);

	kv=initkeyvalues();
	if (!readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings"))
	{
		fprintf(stderr, "Cannot read ethernet settings\n");
		exit(1);
	}

	if (!findkey(kv, "GREEN_DEV", green_dev))
	{
		fprintf(stderr, "Cannot read GREEN_DEV\n");
		exit(1);
	}
	findkey(kv, "BLUE_DEV", blue_dev);
	findkey(kv, "ORANGE_DEV", orange_dev);

	if (!(fwdfile = fopen(CONFIG_ROOT "/dmzholes/config", "r")))
	{
		fprintf(stderr, "Couldn't open dmzholes settings file\n");
		exit(1);
	}

	safe_system("/sbin/iptables -F DMZHOLES");

	while (fgets(s, STRING_SIZE, fwdfile) != NULL)
	{
		if (s[strlen(s) - 1] == '\n')
		        s[strlen(s) - 1] = '\0';
		result = strtok(s, ",");
		
		count = 0;
		protocol = NULL;
		locip = NULL; remip = NULL;
		remport = NULL;
		enabled = NULL;
		src_net = NULL;
		dst_net = NULL;
		idev = NULL;
		odev = NULL;
		
		while (result)
		{
			if (count == 0)
				protocol = result;
			else if (count == 1)
				locip = result;
			else if (count == 2)
				remip = result;
			else if (count == 3)
				remport = result;
			else if (count == 4)
				enabled = result;
			else if (count == 5)
				src_net = result;
			else if (count == 6)
				dst_net = result;
			count++;
			result = strtok(NULL, ",");
		}

		if (!(protocol && locip && remip && remport && enabled))
		{
			fprintf(stderr, "Bad line:\n");
			break;
		}

		if (!VALID_PROTOCOL(protocol))
		{
			fprintf(stderr, "Bad protocol: %s\n", protocol);
			exit(1);
		}
		if (!VALID_IP_AND_MASK(locip))
		{
			fprintf(stderr, "Bad local IP: %s\n", locip);
			exit(1);
		}
		if (!VALID_IP_AND_MASK(remip))
		{
			fprintf(stderr, "Bad remote IP: %s\n", remip);
			exit(1);
		}
		if (!VALID_PORT_RANGE(remport))
		{
			fprintf(stderr, "Bad remote port: %s\n", remport);
			exit(1);
		}
		
		if (!src_net) { src_net = strdup ("orange");}
		if (!dst_net) { dst_net = strdup ("green");}
		
		if (!strcmp(src_net, "blue"))   { idev = blue_dev; }
		if (!strcmp(src_net, "orange")) { idev = orange_dev; }
		if (!strcmp(dst_net, "blue"))   { odev = blue_dev; }
		if (!strcmp(dst_net, "green"))  { odev = green_dev; }
		
		if (!strcmp(enabled, "on") && strlen(idev) && strlen (odev))
		{
			char *ctr;
			/* If remport contains a - we need to change it to a : */
			if ((ctr = strchr(remport,'-')) != NULL){*ctr = ':';}
			memset(command, 0, STRING_SIZE);
			snprintf(command, STRING_SIZE - 1, "/sbin/iptables -A DMZHOLES -p %s -i %s -o %s -s %s -d %s --dport %s -j ACCEPT", protocol, idev, odev, locip, remip, remport);
			safe_system(command);
		}
	}

	return 0;
}
