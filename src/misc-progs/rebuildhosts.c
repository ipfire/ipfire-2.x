/* IPCop helper program - rebuildhosts
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Alan Hourihane, 2003
 *
 *
 * $Id: rebuildhosts.c,v 1.3.2.6 2005/07/11 10:56:47 franck78 Exp $
 *
 */

#include "libsmooth.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>

#include "setuid.h"
#include "netutil.h"

FILE *hosts = NULL;
FILE *gw = NULL;
struct keyvalue *kv = NULL;

void exithandler(void)
{
	if (kv)
		freekeyvalues(kv);
	if (hosts)
		fclose(hosts);
	if (gw)
		fclose(gw);
}

int main(int argc, char *argv[])
{
	char hostname[STRING_SIZE] = "";
	char domainname[STRING_SIZE] = "";
	char gateway[STRING_SIZE] = "";
	char address[STRING_SIZE] = "";

	if (!(initsetuid()))
		exit(1);

	atexit(exithandler);

	kv = initkeyvalues();
	if (!(readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings")))
	{
		fprintf(stderr, "Couldn't read ethernet settings\n");
		exit(1);
	}
	findkey(kv, "GREEN_ADDRESS", address);
	freekeyvalues(kv);

	kv = initkeyvalues();
	if (!(readkeyvalues(kv, CONFIG_ROOT "/main/settings")))
	{
		fprintf(stderr, "Couldn't read main settings\n");
		exit(1);
	}
	strcpy(hostname, SNAME );
	findkey(kv, "HOSTNAME", hostname);
	findkey(kv, "DOMAINNAME", domainname);
	freekeyvalues(kv);
	kv = NULL;

	if ((gw = fopen(CONFIG_ROOT "/red/remote-ipaddress", "r"))) {
		if (fgets(gateway, STRING_SIZE, gw) == NULL) {
			fprintf(stderr, "Couldn't read remote-ipaddress\n");
			exit(1);
		}
	} else {
		fprintf(stderr, "Couldn't open remote-ipaddress file\n");
	}

	if (!(hosts = fopen("/etc/hosts", "w")))
	{
		fprintf(stderr, "Couldn't open /etc/hosts file\n");
		exit(1);
	}
	fprintf(hosts, "127.0.0.1\tlocalhost\n");
	if (strlen(domainname))
		fprintf(hosts, "%s\t%s.%s\t%s\n",address,hostname,domainname,hostname);
	else
		fprintf(hosts, "%s\t%s\n",address,hostname);

	if (strlen(gateway) > 0)
		fprintf(hosts, "%s\tgateway\n", gateway);

	return 0;
}
