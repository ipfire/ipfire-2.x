/* SmoothWall setup program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Misc. stuff for the lib.
 * 
 */
 
#include "setup.h"

extern FILE *flog;
extern char *mylog;

extern char **ctr;
 
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
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
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
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}
	strcpy(hostname, SNAME );
	findkey(kv, "HOSTNAME", hostname);
	findkey(kv, "DOMAINNAME", domainname);
	freekeyvalues(kv);
		
	if (!(file = fopen(CONFIG_ROOT "/main/hostname.conf", "w")))
	{
		sprintf (message, ctr[TR_UNABLE_TO_WRITE_VAR_SMOOTHWALL_MAIN_HOSTNAMECONF], CONFIG_ROOT);
		errorbox(message);
		return 0;
	}
	fprintf(file, "ServerName %s.%s\n", hostname,domainname);
	fclose(file);
	
	if (!(file = fopen(CONFIG_ROOT "/main/hosts", "r")))
	{
		errorbox(ctr[TR_UNABLE_TO_OPEN_HOSTS_FILE]);
		return 0;
	}
	if (!(hosts = fopen("/etc/hosts", "w")))
	{
		errorbox(ctr[TR_UNABLE_TO_WRITE_ETC_HOSTS]);
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
	
	/* TCP wrappers stuff. */
	if (!(file = fopen("/etc/hosts.deny", "w")))
	{
		errorbox(ctr[TR_UNABLE_TO_WRITE_ETC_HOSTS_DENY]);
		return 0;
	}
	fprintf(file, "ALL : ALL\n");
	fclose(file);
	
	if (!(file = fopen("/etc/hosts.allow", "w")))
	{
		errorbox(ctr[TR_UNABLE_TO_WRITE_ETC_HOSTS_ALLOW]);
		return 0;
	}
	fprintf(file, "sshd : ALL\n");
	fprintf(file, "ALL  : localhost\n");
	fprintf(file, "ALL  : %s/%s\n", netaddress, netmask);
	fclose(file);
	
	sprintf(commandstring, "/bin/hostname %s.%s", hostname, domainname);
	if (mysystem(commandstring))
	{
		errorbox(ctr[TR_UNABLE_TO_SET_HOSTNAME]);
		return 0;
	}
	
	return 1;
}	

int handleisdn(void)
{
	char command[STRING_SIZE];
	sprintf(command, "/etc/rc.d/init.d/mISDN config");
	if (runcommandwithstatus(command, ctr[TR_PROBING_ISDN]))
		errorbox(ctr[TR_ERROR_PROBING_ISDN]);
	// Need to write some lines that count the cards and say the names...
	return 1;
}
