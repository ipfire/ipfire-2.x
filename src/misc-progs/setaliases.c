/*
 * setaliases - configure red aliased interfaces
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Steve Bootes, 2002/04/15
 *
 * 21/04/03 Robert Kerr Changed to link directly to libsmooth rather than
 *                      using a copy & paste
 *
 * $Id: setaliases.c,v 1.2.2.5 2006/07/25 23:15:20 franck78 Exp $
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include "libsmooth.h"
#include "setuid.h"
#include "netutil.h"

struct keyvalue *kv = NULL;
FILE *file = NULL;

void exithandler(void)
{
	if (kv) freekeyvalues(kv);
	if (file) fclose(file);
}

int main(void)
{
	char s[STRING_SIZE];
	char command[STRING_SIZE];
	char red_netmask[STRING_SIZE];
	char red_dev[STRING_SIZE];
	char default_gateway[STRING_SIZE];
	char *aliasip;
	char *enabled;
	char *sptr;
	char *comment;
	int alias;
	int count;

	if (!(initsetuid()))
	{
		fprintf(stderr, "Cannot run setuid\n");
		exit(1);
	}

	atexit(exithandler);

	/* Init the keyvalue structure */
	kv=initkeyvalues();

	/* Read in the current values */
	if (!readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings"))
	{
		fprintf(stderr, "Cannot read ethernet settings\n");
		exit(1);
	}

	/* Find the CONFIG_TYPE value */
	if (!findkey(kv, "CONFIG_TYPE", s))
	{
		fprintf(stderr, "Cannot read CONFIG_TYPE\n");
		exit(1);
	}

	/* Check for CONFIG_TYPE=2 or 3 i.e. RED ethernet present. If not,
	 * exit gracefully.  This is not an error... */
	if (!((strcmp(s, "1")==0) || (strcmp(s, "2")==0) || (strcmp(s, "3")==0) || (strcmp(s, "4")==0)))
		exit(0);

	/* Now check the RED_TYPE - aliases only work with STATIC.
	 * At least, that's what /etc/rc.d/rc.netaddress.up thinks.. */

	/* Find the RED_TYPE value */
	if (!findkey(kv, "RED_TYPE", s))
	{
		fprintf(stderr, "Cannot read RED_TYPE\n");
		exit(1);
	}

	/* Make sure it's the right type */
	if (!(strcmp(s, "STATIC")==0))
		exit(0);

	/* Get the RED interface details */
	if((!findkey(kv, "RED_NETMASK", red_netmask)) ||
		(!findkey(kv, "RED_DEV", red_dev)) || (!findkey(kv, "DEFAULT_GATEWAY", default_gateway)))
	{
		fprintf(stderr, "Cannot read RED settings\n");
		exit(1);
	}

	if (!VALID_DEVICE(red_dev))
	{
		fprintf(stderr, "Bad red_dev: %s\n", red_dev);
		exit(1);
	}

	if (!VALID_IP(red_netmask))
	{
		fprintf(stderr, "Bad red_netmask : %s\n", red_netmask);
		exit(1);
	}

	if (!VALID_IP(default_gateway))
	{
		fprintf(stderr, "Bad default_gateway : %s\n", default_gateway);
		exit(1);
	}

	/* down the aliases in turn until ifconfig complains */
	alias=0;
	do
	{
		memset(command, 0, STRING_SIZE);
		snprintf(command, STRING_SIZE-1, "/sbin/ifconfig %s:%d down 2>/dev/null", red_dev, alias++);
	} while (safe_system(command)==0);

	/* Now set up the new aliases from the config file */
        if (!(file = fopen(CONFIG_ROOT "/ethernet/aliases", "r")))
        {
                fprintf(stderr, "Unable to open aliases configuration file\n");
                exit(1);
        }

	alias=0;
	int linecounter = 0;
        while (fgets(s, STRING_SIZE, file) != NULL)
        {
		linecounter++;
                if (s[strlen(s) - 1] == '\n')
                        s[strlen(s) - 1] = '\0';
                count = 0;
                aliasip = NULL;
                enabled = NULL;
                comment = NULL;
                sptr = strtok(s, ",");
                while (sptr)
                {
                        if (count == 0)
                                aliasip = sptr;
                        if (count == 1)
                                enabled = sptr;
                        else
                                comment = sptr;
                        count++;
			sptr = strtok(NULL, ",");
		}

		if (!(aliasip && enabled)) {
			fprintf(stderr, "Incomplete data line: in %s(%d)\n",
					CONFIG_ROOT "/ethernet/aliases",
					linecounter);
			exit(1);
		}
		if (!strcmp(enabled, "on") == 0)	/* disabled rule? */
			continue;

		if (!VALID_IP(aliasip))
                {
                        fprintf(stderr, "Bad alias : %s in %s(%d)\n",
					aliasip,
					CONFIG_ROOT "/ethernet/aliases",
					linecounter);
                        exit(1);
                }

		memset(command, 0, STRING_SIZE);
		snprintf(command, STRING_SIZE-1,
				"/sbin/ifconfig %s:%d %s netmask %s up",
			     red_dev, alias, aliasip, red_netmask);
		safe_system(command);
		memset(command, 0, STRING_SIZE);
		snprintf(command, STRING_SIZE-1,
				"/usr/sbin/arping -q -c 1 -w 1 -i %s -S %s %s",
				red_dev, aliasip, default_gateway);
		safe_system(command);
		alias++;
	}
	return 0;
}
