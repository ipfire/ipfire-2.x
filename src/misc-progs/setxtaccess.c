/* SmoothWall helper program - setxtaccess
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Daniel Goscomb, 2001
 * 
 * Modifications and improvements by Lawrence Manning.
 *
 * 10/04/01 Aslak added protocol support
 * 
 * (c) Steve Bootes 2002/04/14 - Added source IP support for aliases
 *
 * 19/04/03 Robert Kerr Fixed root exploit
 *
 * $Id: setxtaccess.c,v 1.3.2.1 2005/01/04 17:21:40 eoberlander Exp $
 * 
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "setuid.h"

FILE *ifacefile = NULL;
FILE *fwdfile = NULL;
FILE *ipfile = NULL;

void exithandler(void)
{
	if (fwdfile)
		fclose(fwdfile);
}

int main(void)
{
	char iface[STRING_SIZE] = "";
	char locip[STRING_SIZE] = "";
	char s[STRING_SIZE] = "";
	int count;
	char *protocol;
	char *destip;
	char *remip;
	char *locport;
	char *enabled;
	char *information;
	char *result;
	char command[STRING_SIZE];

	if (!(initsetuid()))
		exit(1);

	atexit(exithandler);

	if (!(ipfile = fopen(CONFIG_ROOT "/red/local-ipaddress", "r")))
	{
		fprintf(stderr, "Couldn't open local ip file\n");
		exit(1);
	}
	if (fgets(locip, STRING_SIZE, ipfile))
	{
		if (locip[strlen(locip) - 1] == '\n')
			locip[strlen(locip) - 1] = '\0';
	}
	fclose (ipfile);
	if (!VALID_IP(locip))
	{
		fprintf(stderr, "Bad local IP: %s\n", locip);
		exit(1);
	}

	if (!(ifacefile = fopen(CONFIG_ROOT "/red/iface", "r")))
	{
		fprintf(stderr, "Couldn't open iface file\n");
		exit(1);
	}
	if (fgets(iface, STRING_SIZE, ifacefile))
	{
		if (iface[strlen(iface) - 1] == '\n')
			iface[strlen(iface) - 1] = '\0';
	}
		fclose (ifacefile);
	if (!VALID_DEVICE(iface))
	{
		fprintf(stderr, "Bad iface: %s\n", iface);
		exit(1);
	}
 
	if (!(fwdfile = fopen(CONFIG_ROOT "/xtaccess/config", "r")))
	{
		fprintf(stderr, "Couldn't open xtaccess settings file\n");
		exit(1);
	}

	safe_system("/sbin/iptables -F XTACCESS");

	while (fgets(s, STRING_SIZE, fwdfile) != NULL)
	{
		if (s[strlen(s) - 1] == '\n')
			s[strlen(s) - 1] = '\0';
		count = 0;
		protocol = NULL;
		remip = NULL;
		destip = NULL;
		locport = NULL;
		enabled = NULL;
		information = NULL;
		result = strtok(s, ",");
		while (result)
		{
			if (count == 0)
				protocol = result;
			else if (count == 1)
				remip = result;
			else if (count == 2)
				locport = result;
			else if (count == 3)
				enabled = result;
			else if (count == 4)
				destip = result;
			else
				information = result;
			count++;
			result = strtok(NULL, ",");
		}

		if (!(protocol && remip && locport && enabled))
			break;
		
		if (!VALID_PROTOCOL(protocol))
		{
			fprintf(stderr, "Bad protocol: %s\n", protocol);
			exit(1);
		}
		if (!VALID_IP_AND_MASK(remip))
		{
			fprintf(stderr, "Bad remote IP: %s\n", remip);
			exit(1);
		}
		if (!VALID_PORT_RANGE(locport))
		{
			fprintf(stderr, "Bad local port: %s\n", locport);
			exit(1);
		}

                /* check for destination ip in config file. If it's there
                 * and it's not 0.0.0.0, use it; else use the current
                 * local ip address. (This makes sure we can use old-style
                 * config files without the destination ip) */
		if (!destip || !strcmp(destip, "0.0.0.0"))
			destip = locip;
		if (!VALID_IP(destip))
		{
			fprintf(stderr, "Bad destination IP: %s\n", remip);
			exit(1);
		}

		if (strcmp(enabled, "on") == 0)
		{
			memset(command, 0, STRING_SIZE);
			snprintf(command, STRING_SIZE - 1, "/sbin/iptables -A XTACCESS -i %s -p %s -s %s -d %s --dport %s -j ACCEPT",
	iface, protocol, remip, destip, locport);
			safe_system(command);
		}
	}
	
	return 0;
}
