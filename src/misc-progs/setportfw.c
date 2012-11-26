/* SmoothWall helper program - setportfw
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Daniel Goscomb, 2001
 * Copyright (c) 2002/04/13 Steve Bootes - Added source ip support for aliases
 * 
 * Modifications and improvements by Lawrence Manning.
 *
 * 10/04/01 Aslak added protocol support
 * This program reads the list of ports to forward and setups iptables
 * and rules in ipmasqadm to enable them.
 *
 * 02/11/03 Darren Critchley modifications to allow it to open multiple
 *							 source ip addresses
 * 02/25/03 Darren Critchley modifications to allow port ranges
 * 04/01/03 Darren Critchley modifications to allow gre protocol
 * 20/04/03 Robert Kerr Fixed root exploit, validated all variables properly,
 *                      tidied up the iptables logic, killed duplicated code,
 *                      removed srciptmp (unecessary)
 *
 * $Id: setportfw.c,v 1.3.2.6 2005/08/24 18:44:19 gespinasse Exp $
 * 
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "libsmooth.h"
#include "setuid.h"

struct keyvalue *kv = NULL;
FILE *fwdfile = NULL;

void exithandler(void)
{
	if(kv)
		freekeyvalues(kv);
	if (fwdfile)
		fclose(fwdfile);
}

int main(void)
{
	FILE *ipfile = NULL, *ifacefile = NULL;
	int count;
	char iface[STRING_SIZE] ="";
	char locip[STRING_SIZE] ="";
	char greenip[STRING_SIZE] ="", greenmask[STRING_SIZE] ="";
	char bluedev[STRING_SIZE] ="", blueip[STRING_SIZE] ="", bluemask[STRING_SIZE] ="";
	char orangedev[STRING_SIZE] ="", orangeip[STRING_SIZE] ="", orangemask[STRING_SIZE] ="";
	char *protocol;
	char *srcip;
	char *locport;
	char *remip;
	char *remport;
	char *origip;
	char *enabled;
	char s[STRING_SIZE];
	char *result;
	char *key1;
	char *key2;
	char command[STRING_SIZE];

	if (!(initsetuid()))
		exit(1);

	atexit(exithandler);

	/* Read in and verify config */
	kv=initkeyvalues();

	if (!readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings"))
	{
		fprintf(stderr, "Cannot read ethernet settings\n");
		exit(1);
	}

	if (!findkey(kv, "GREEN_ADDRESS", greenip))
	{
		fprintf(stderr, "Cannot read GREEN_ADDRESS\n");
		exit(1);
	}

	if (!VALID_IP(greenip))
	{
		fprintf(stderr, "Bad GREEN_ADDRESS: %s\n", greenip);
		exit(1);
	}

	if (!findkey(kv, "GREEN_NETMASK", greenmask))
	{
		fprintf(stderr, "Cannot read GREEN_NETMASK\n");
		exit(1);
	}

	if (!VALID_IP(greenmask))
	{
		fprintf(stderr, "Bad GREEN_NETMASK: %s\n", greenmask);
		exit(1);
	}

	/* Get the BLUE interface details */
	findkey(kv, "BLUE_DEV", bluedev);

	if (strlen(bluedev))
	{

		if (!VALID_DEVICE(bluedev))
		{
			fprintf(stderr, "Bad BLUE_DEV: %s\n", bluedev);
			exit(1);
		}

		if (!findkey(kv, "BLUE_ADDRESS", blueip))
		{
			fprintf(stderr, "Cannot read BLUE_ADDRESS\n");
			exit(1);
		}

		if (!VALID_IP(blueip))
		{
			fprintf(stderr, "Bad BLUE_ADDRESS: %s\n", blueip);
			exit(1);
		}

		if (!findkey(kv, "BLUE_NETMASK", bluemask))
		{
			fprintf(stderr, "Cannot read BLUE_NETMASK\n");
			exit(1);
		}

		if (!VALID_IP(bluemask))
		{
			fprintf(stderr, "Bad BLUE_NETMASK: %s\n", bluemask);
			exit(1);
		}

	}

	/* Get the ORANGE interface details */
	findkey(kv, "ORANGE_DEV", orangedev);

	if (strlen(orangedev))
	{

		if (!VALID_DEVICE(orangedev))
		{
			fprintf(stderr, "Bad ORANGE_DEV: %s\n", orangedev);
			exit(1);
		}

		if (!findkey(kv, "ORANGE_ADDRESS", orangeip))
		{
			fprintf(stderr, "Cannot read ORANGE_ADDRESS\n");
			exit(1);
		}

		if (!VALID_IP(orangeip))
		{
			fprintf(stderr, "Bad ORANGE_ADDRESS: %s\n", orangeip);
			exit(1);
		}

		if (!findkey(kv, "ORANGE_NETMASK", orangemask))
		{
			fprintf(stderr, "Cannot read ORANGE_NETMASK\n");
			exit(1);
		}

		if (!VALID_IP(orangemask))
		{
			fprintf(stderr, "Bad ORANGE_NETMASK: %s\n", orangemask);
			exit(1);
		}

	}


	if (!(ipfile = fopen(CONFIG_ROOT "/red/local-ipaddress", "r")))
	{
		fprintf(stderr, "Couldn't open local ip file\n");
		exit(1);
	}
	fgets(locip, STRING_SIZE, ipfile);
	if (locip[strlen(locip) - 1] == '\n')
		locip[strlen(locip) - 1] = '\0';
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
	fgets(iface, STRING_SIZE, ifacefile);
	if (iface[strlen(iface) - 1] == '\n')
		iface[strlen(iface) - 1] = '\0';
	fclose (ifacefile);
	if (!VALID_DEVICE(iface))
	{
		fprintf(stderr, "Bad iface: %s\n", iface);
		exit(1);
	}
 	
	if (!(fwdfile = fopen(CONFIG_ROOT "/portfw/config", "r")))
	{
		fprintf(stderr, "Couldn't open portfw settings file\n");
		exit(1);
	}

	safe_system("/sbin/iptables -t nat -F PORTFW");
	safe_system("/sbin/iptables -t mangle -F PORTFWMANGLE");
	safe_system("/sbin/iptables -F PORTFWACCESS");

	while (fgets(s, STRING_SIZE, fwdfile) != NULL)
	{
		if (s[strlen(s) - 1] == '\n')
			s[strlen(s) - 1] = '\0';
		result = strtok(s, ",");

		count = 0;
		key1 = NULL;
		key2 = NULL;
		protocol = NULL;
		srcip = NULL;
		locport = NULL;
		remip = NULL;
		origip = NULL;
		remport = NULL;
		enabled = NULL;
		while (result)
		{
			if (count == 0)
				key1 = result;
			else if (count == 1)
				key2 = result;
			else if (count == 2)
				protocol = result;
			else if (count == 3)
				locport = result;
			else if (count == 4)
				remip = result;
			else if (count == 5)
				remport = result;
			else if (count == 6)
				enabled = result;
			else if (count == 7)
				srcip = result;
			else if (count == 8)
				origip = result;
			count++;
			result = strtok(NULL, ",");
		}
		
		if (!(key1 && key2 && protocol && locport && remip && remport && enabled
			&& srcip && origip))
			break;
		
		if (!VALID_PROTOCOL(protocol))
		{
			fprintf(stderr, "Bad protocol: %s\n", protocol);
			exit(1);
		}
		if (strcmp(protocol, "gre") == 0)
		{
			locport = "0";
			remport = "0";
		}
		if (strcmp(origip,"0") && !VALID_IP_AND_MASK(origip))
		{
			fprintf(stderr, "Bad IP: %s\n", origip);
			exit(1);
		}
		if (!VALID_PORT_RANGE(locport))
		{
			fprintf(stderr, "Bad local port: %s\n", locport);
			exit(1);
		}
		if (!VALID_IP(remip))
		{
			fprintf(stderr, "Bad remote IP: %s\n", remip);
			exit(1);
		}
		if (!VALID_PORT_RANGE(remport))
		{
			fprintf(stderr, "Bad remote port: %s\n", remport);
			exit(1);
		}

                /* check for source ip in config file. If it's there
                 * and it's not 0.0.0.0, use it; else use the
                 * local ip address. (This makes sure we can use old-style
                 * config files without the source ip) */
		if (!srcip || !strcmp(srcip, "0.0.0.0"))
			srcip = locip;
		if (strcmp(srcip,"0") && !VALID_IP(srcip))
		{
			fprintf(stderr, "Bad source IP: %s\n", srcip);
			exit(1);
		}

		/* This may seem complicated... refer to portfw.pl for an explanation of
		 * the keys and their meaning in certain circumstances */
                        
		if (strcmp(enabled, "on") == 0)
		{

			/* If key2 is a zero, then it is a portfw command, otherwise it is an
			 * external access command */
			if (strcmp(key2, "0") == 0) 
			{
				memset(command, 0, STRING_SIZE);
				if (strcmp(protocol, "gre") == 0)
					snprintf(command, STRING_SIZE - 1, "/sbin/iptables -t nat -A PORTFW -p %s -d %s -j DNAT --to %s", protocol, srcip, remip);
				else 
				{
					char *ctr;
					/* If locport contains a - we need to change it to a : */
					if ((ctr = strchr(locport, '-')) != NULL) {*ctr = ':';}
					/* If remport contains a : we need to change it to a - */
					if ((ctr = strchr(remport,':')) != NULL){*ctr = '-';}
					snprintf(command, STRING_SIZE - 1, "/sbin/iptables -t nat -A PORTFW -p %s -d %s --dport %s -j DNAT --to %s:%s", protocol, srcip, locport, remip, remport);
					safe_system(command);
					/* Now if remport contains a - we need to change it to a : */
					if ((ctr = strchr(remport,'-')) != NULL){*ctr = ':';}
					snprintf(command, STRING_SIZE - 1, "/sbin/iptables -t mangle -A PORTFWMANGLE -p %s -s %s/%s -d %s --dport %s -j MARK --set-mark 1", protocol, greenip, greenmask, srcip, locport);
					if (strlen(bluedev))
					{
						safe_system(command);
						snprintf(command, STRING_SIZE - 1, "/sbin/iptables -t mangle -A PORTFWMANGLE -p %s -s %s/%s -d %s --dport %s -j MARK --set-mark 2", protocol, blueip, bluemask, srcip, locport);
					}
					if (strlen(orangedev))
					{
						safe_system(command);
						snprintf(command, STRING_SIZE - 1, "/sbin/iptables -t mangle -A PORTFWMANGLE -p %s -s %s/%s -d %s --dport %s -j MARK --set-mark 3", protocol, orangeip, orangemask, srcip, locport);
					}
				}
				safe_system(command);
			}

			/* if key2 is not "0" then it's an external access rule, if key2 is "0"
			 * then the portfw rule may contain external access information if origip
			 * is not "0" (the only defined not 0 value seems to be 0.0.0.0 - open
			 * to all; again, check portfw.pl for more details) */
			if(strcmp(key2, "0") || strcmp(origip,"0") )
			{
				memset(command, 0, STRING_SIZE);
				if (strcmp(protocol, "gre") == 0)
					snprintf(command, STRING_SIZE - 1, "/sbin/iptables -A PORTFWACCESS -i %s -p %s -s %s -d %s -j ACCEPT", iface, protocol, origip, remip);
				else
				{
					char *ctr;
					/* If remport contains a - we need to change it to a : */
					if ((ctr = strchr(remport,'-')) != NULL){*ctr = ':';}
					snprintf(command, STRING_SIZE - 1, "/sbin/iptables -A PORTFWACCESS -i %s -p %s -s %s -d %s --dport %s -j ACCEPT", iface, protocol, origip, remip, remport);
				}
				safe_system(command);
			}
		}
	}

	return 0;
}
