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
#include <fcntl.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <signal.h>

#include "setuid.h"
#include "netutil.h"

FILE *fd = NULL;
FILE *hosts = NULL;
FILE *gw = NULL;
struct keyvalue *kv = NULL;

void exithandler(void)
{
	if (kv)
		freekeyvalues(kv);
	if (fd)
		fclose(fd);
	if (hosts)
		fclose(hosts);
	if (gw)
		fclose(gw);
}

int main(int argc, char *argv[])
{
	int fdpid; 
	char hostname[STRING_SIZE] = "";
	char domainname[STRING_SIZE] = "";
	char gateway[STRING_SIZE] = "";
	char buffer[STRING_SIZE];
	char address[STRING_SIZE] = "";
	char *active, *ip, *host, *domain;
	int pid;

	if (!(initsetuid()))
		exit(1);

	atexit(exithandler);

	memset(buffer, 0, STRING_SIZE);

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

	if (!(gw = fopen(CONFIG_ROOT "/red/remote-ipaddress", "r")))
	{
		fprintf(stderr, "Couldn't open remote-ipaddress file\n");
		exit(1);
	}

	if (fgets(gateway, STRING_SIZE, gw) == NULL)
	{
		fprintf(stderr, "Couldn't read remote-ipaddress\n");
		exit(1);
	}

	if (!(fd = fopen(CONFIG_ROOT "/main/hosts", "r")))
	{
		fprintf(stderr, "Couldn't open main hosts file\n");
		exit(1);
	}

	if (!(hosts = fopen("/etc/hosts", "w")))
	{
		fprintf(stderr, "Couldn't open /etc/hosts file\n");
    		fclose(fd);
		fd = NULL;
		exit(1);
	}
	fprintf(hosts, "127.0.0.1\tlocalhost\n");
	if (strlen(domainname))
		fprintf(hosts, "%s\t%s.%s\t%s\n",address,hostname,domainname,hostname);
	else
		fprintf(hosts, "%s\t%s\n",address,hostname);

	fprintf(hosts, "%s\tgateway\n",gateway);

	while (fgets(buffer, STRING_SIZE, fd))
	{
		buffer[strlen(buffer) - 1] = 0;
		if (buffer[0]==',') continue;		/* disabled if empty field	*/
		active = strtok(buffer, ",");
		if (strcmp(active, "off")==0) continue; /* or 'off'			*/
		
		ip = strtok(NULL, ",");
		host = strtok(NULL, ",");
		domain = strtok(NULL, ",");

		if (!(ip && host))
			continue;	// bad line ? skip

		if (!VALID_IP(ip))
		{
			fprintf(stderr, "Bad IP: %s\n", ip);
			continue;       /*  bad ip, skip */
		}

		if (strspn(host, LETTERS_NUMBERS "-") != strlen(host))
		{
			fprintf(stderr, "Bad Host: %s\n", host);
			continue;       /*  bad name, skip */
		}

		if (domain)
			fprintf(hosts, "%s\t%s.%s\t%s\n",ip,host,domain,host);
		else
			fprintf(hosts, "%s\t%s\n",ip,host);
	}
	fclose(fd);
	fd = NULL;
	fclose(hosts);
	hosts = NULL;

	if ((fdpid = open("/var/run/dnsmasq.pid", O_RDONLY)) == -1)
	{
		fprintf(stderr, "Couldn't open pid file\n");
		exit(1);
	}
	if (read(fdpid, buffer, STRING_SIZE - 1) == -1)
	{
		fprintf(stderr, "Couldn't read from pid file\n");
		close(fdpid);
		exit(1);
	}
	close(fdpid);
	pid = atoi(buffer);
	if (pid <= 1)
	{
		fprintf(stderr, "Bad pid value\n");
		exit(1);
	}
	if (kill(pid, SIGHUP) == -1)
	{
		fprintf(stderr, "Unable to send SIGHUP\n");
		exit(1);
	}

	return 0;
}
