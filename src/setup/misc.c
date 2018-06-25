/* SmoothWall setup program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Misc. stuff for the lib.
 * 
 */

// Translation
#include <libintl.h>
#define _(x) dgettext("setup", x)

#include "setup.h"

extern FILE *flog;
extern char *mylog;

extern int automode;

/* This will rewrite /etc/hosts, /etc/hosts.*, and the apache ServerName file. */
int writehostsfiles(void)
{	
	char address[STRING_SIZE] = "";
	char netaddress[STRING_SIZE] = "";
	char netmask[STRING_SIZE] = "";
	char message[1000];
	FILE *file, *hosts;
	struct keyvalue *kv;
	char hostname[STRING_SIZE];
	char domainname[STRING_SIZE] = "localdomain";
	char commandstring[STRING_SIZE];
	char buffer[STRING_SIZE];
	
	kv = initkeyvalues();
	if (!(readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings")))
	{
		freekeyvalues(kv);
		errorbox(_("Unable to open settings file"));
		return 0;
	}
	findkey(kv, "GREEN_ADDRESS", address);
	findkey(kv, "GREEN_NETADDRESS", netaddress);
	findkey(kv, "GREEN_NETMASK", netmask);	
	freekeyvalues(kv);
	
	kv = initkeyvalues();
	if (!(readkeyvalues(kv, CONFIG_ROOT "/main/settings")))
	{
		freekeyvalues(kv);
		errorbox(_("Unable to open settings file"));
		return 0;
	}
	strcpy(hostname, SNAME );
	findkey(kv, "HOSTNAME", hostname);
	findkey(kv, "DOMAINNAME", domainname);
	freekeyvalues(kv);
		
	if (!(file = fopen(CONFIG_ROOT "/main/hosts", "r")))
	{
		errorbox(_("Unable to open main hosts file."));
		return 0;
	}
	if (!(hosts = fopen("/etc/hosts", "w")))
	{
		errorbox(_("Unable to write /etc/hosts."));
		return 0;
	}
	fprintf(hosts, "127.0.0.1\tlocalhost\n");
	if (strlen(domainname))
		fprintf(hosts, "%s\t%s.%s\t%s\n",address,hostname,domainname,hostname);
	else
		fprintf(hosts, "%s\t%s\n",address,hostname);
	while (fgets(buffer, STRING_SIZE, file))
	{
		char *token, *ip, *host, *domain;

		buffer[strlen(buffer) - 1] = 0;

		token = strtok(buffer, ",");

		ip = strtok(NULL, ",");
		host = strtok(NULL, ",");
		domain = strtok(NULL, ",");

		if (!(ip && host))
			break;

		if (strlen(ip) < 7 || strlen(ip) > 15
		 || strspn(ip, "0123456789.") != strlen(ip))
			break;

		if (strspn(host, "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-") != strlen(host))
			break;

		if (domain)
			fprintf(hosts, "%s\t%s.%s\t%s\n",ip,host,domain,host);
		else
			fprintf(hosts, "%s\t%s\n",ip,host);
	}
	fclose(file);
	fclose(hosts);

	sprintf(commandstring, "/bin/hostname %s.%s", hostname, domainname);
	if (mysystem(NULL, commandstring))
	{
		errorbox(_("Unable to set hostname."));
		return 0;
	}
	
	return 1;
}	
