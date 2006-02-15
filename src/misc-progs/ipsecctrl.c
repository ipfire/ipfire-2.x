/*
 *
 * File originally from the Smoothwall project
 * (c) 2001 Smoothwall Team
 *
 * $Id: ipsecctrl.c,v 1.5.2.14 2005/05/15 12:58:28 rkerr Exp $
 *
 */

#include "libsmooth.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <signal.h>
#include "setuid.h"

void usage() {
	fprintf (stderr, "Usage:\n");
	fprintf (stderr, "\tipsecctrl S [connectionkey]\n");
	fprintf (stderr, "\tipsecctrl D [connectionkey]\n");
	fprintf (stderr, "\tipsecctrl R\n");
	fprintf (stderr, "\t\tS : Start/Restart Connection\n");
	fprintf (stderr, "\t\tD : Stop Connection\n");
	fprintf (stderr, "\t\tR : Reload Certificates and Secrets\n");
}

void loadalgmodules() {
	safe_system("/sbin/modprobe ipsec_3des");
	safe_system("/sbin/modprobe ipsec_aes");
	safe_system("/sbin/modprobe ipsec_blowfish");
	safe_system("/sbin/modprobe ipsec_md5");
	safe_system("/sbin/modprobe ipsec_serpent");
	safe_system("/sbin/modprobe ipsec_sha1");
	safe_system("/sbin/modprobe ipsec_sha2");
	safe_system("/sbin/modprobe ipsec_twofish");
}

void ipsecrules(char *chain, char *interface)
{
	char str[STRING_SIZE];

	sprintf(str, "/sbin/iptables -A %s -p 47  -i %s -j ACCEPT", chain, interface);
	safe_system(str);
	sprintf(str, "/sbin/iptables -A %s -p 50  -i %s -j ACCEPT", chain, interface);
	safe_system(str);
	sprintf(str, "/sbin/iptables -A %s -p 51  -i %s -j ACCEPT", chain, interface);
	safe_system(str);
	sprintf(str, "/sbin/iptables -A %s -p udp -i %s --sport 500 --dport 500 -j ACCEPT", chain, interface);
	safe_system(str);
	sprintf(str, "/sbin/iptables -A %s -p udp -i %s --dport 4500 -j ACCEPT", chain, interface);
	safe_system(str);
}

void addaliasinterfaces(char *configtype, char *redtype, char *redif, char *enablered, char*enableblue)
{
	FILE *file = NULL;
	char s[STRING_SIZE];
	char *sptr;
	char *aliasip=NULL;
	char *enabled=NULL;
	char *comment=NULL;
	int count=0;
	int alias=0;
	int add=0;

	if ( strcmp(enablered, "on") == 0 ) 
		add += 1;
	if ( strcmp(enableblue, "on") == 0 )
		add += 1;
	
	/* Check for CONFIG_TYPE=2 or 3 i.e. RED ethernet present. If not,
	* exit gracefully.  This is not an error... */
	if (!((strcmp(configtype, "2")==0) || (strcmp(configtype, "3")==0) || (strcmp(configtype, "6")==0) || (strcmp(configtype, "7")==0)))
		return;

        /* Now check the RED_TYPE - aliases only work with STATIC. */
	if (!(strcmp(redtype, "STATIC")==0))
		return;

	/* Now set up the new aliases from the config file */
	if (!(file = fopen(CONFIG_ROOT "/ethernet/aliases", "r")))
	{
		fprintf(stderr, "Unable to open aliases configuration file\n");
		return;
	}

	while (fgets(s, STRING_SIZE, file) != NULL && (add+alias) < 16)
	{
		if (s[strlen(s) - 1] == '\n')
			s[strlen(s) - 1] = '\0';
		sptr = strtok(s, ",");
		count = 0;
		aliasip = NULL;
		enabled = NULL;
		comment = NULL;
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

		if (!(aliasip && enabled))
			continue;

		if (!VALID_IP(aliasip))
		{
			fprintf(stderr, "Bad alias : %s\n", aliasip);
			return;
		}

		if (strcmp(enabled, "on") == 0)
		{
			memset(s, 0, STRING_SIZE);
			snprintf(s, STRING_SIZE-1, "/usr/sbin/ipsec tncfg --attach --virtual ipsec%d --physical %s:%d >/dev/null", alias+add, redif, alias);
			safe_system(s);
			alias++;
		}
	}
}

int main(int argc, char *argv[]) {
	int count;
	char s[STRING_SIZE];
	char configtype[STRING_SIZE];
	char redtype[STRING_SIZE] = "";
	char command[STRING_SIZE];
	char *result;
	char *key;
	char *enabled;
	char *name;
	char *type;
	char *running;
	FILE *file = NULL;
	struct keyvalue *kv = NULL;
	char enablered[STRING_SIZE] = "off";
	char enableblue[STRING_SIZE] = "off";
	char redif[STRING_SIZE] = "";;
	char blueif[STRING_SIZE] = "";
	FILE *ifacefile = NULL;
			
	if (!(initsetuid()))
		exit(1);
	
	if (argc < 2) {
		usage();
		exit(1);
	}

	/* FIXME: workaround for pclose() issue - still no real idea why
	 * this is happening */
	signal(SIGCHLD, SIG_DFL);

	/* Init the keyvalue structure */
	kv=initkeyvalues();

	/* Read in the current values */
	if (!readkeyvalues(kv, CONFIG_ROOT "/vpn/settings"))
	{
		fprintf(stderr, "Cannot read vpn settings\n");
		exit(1);
	}

	findkey(kv, "ENABLED", enablered);
	findkey(kv, "ENABLED_BLUE", enableblue);

	freekeyvalues(kv);
	kv=initkeyvalues();

	if (!readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings"))
	{
		fprintf(stderr, "Cannot read ethernet settings\n");
		exit(1);
	}

	if (!findkey(kv, "CONFIG_TYPE", configtype))
	{
		fprintf(stderr, "Cannot read CONFIG_TYPE\n");
		exit(1);
	}

	findkey(kv, "RED_TYPE", redtype);
	findkey(kv, "BLUE_DEV", blueif);
	freekeyvalues(kv);
	memset(redif, 0, STRING_SIZE);

	if ((ifacefile = fopen(CONFIG_ROOT "/red/iface", "r")))
	{
		if (fgets(redif, STRING_SIZE, ifacefile))
		{
			if (redif[strlen(redif) - 1] == '\n')
				redif[strlen(redif) - 1] = '\0';
		}
		fclose (ifacefile);
		ifacefile = NULL;

		if (!VALID_DEVICE(redif))
		{
			memset(redif, 0, STRING_SIZE);
		}
	}

	safe_system("/sbin/iptables -F IPSECRED");
	if (!strcmp(enablered, "on") && strlen(redif)) {
		ipsecrules("IPSECRED", redif);
	}

	safe_system("/sbin/iptables -F IPSECBLUE");
	if (!strcmp(enableblue, "on")) {
		if (VALID_DEVICE(blueif))
			ipsecrules("IPSECBLUE", blueif);
		else
		{
			fprintf(stderr, "IPSec enabled on blue but blue interface is invalid or not found\n");
			exit(1);
		}
	}

	/* Only shutdown pluto if it really is running */
	if (argc == 2) {
		if (strcmp(argv[1], "D") == 0) {
			int fd;
   			/* Get pluto pid */
   			if ((fd = open("/var/run/pluto.pid", O_RDONLY)) != -1) {
				safe_system("/etc/rc.d/ipsec stop 2> /dev/null >/dev/null");
				close(fd);
			}
		}
	}

	if ((strcmp(enablered, "on") || !strlen(redif)) && strcmp(enableblue, "on"))
		exit(0);

	if (argc == 2) {
		if (strcmp(argv[1], "S") == 0) {
			loadalgmodules();
			safe_system("/usr/sbin/ipsec tncfg --clear >/dev/null");
			safe_system("/etc/rc.d/ipsec restart >/dev/null");
			addaliasinterfaces(configtype, redtype, redif, enablered, enableblue);
		} else if (strcmp(argv[1], "R") == 0) {
			safe_system("/usr/sbin/ipsec auto --rereadall");
		} else {
			fprintf(stderr, "Bad arg\n");
			usage();
			exit(1);
		}
	} else if (strspn(argv[2], NUMBERS) == strlen(argv[2])) {
		if (!(file = fopen(CONFIG_ROOT "/vpn/config", "r"))) {
			fprintf(stderr, "Couldn't open vpn settings file");
			exit(1);
		}
		while (fgets(s, STRING_SIZE, file) != NULL) {
			if (s[strlen(s) - 1] == '\n')
				s[strlen(s) - 1] = '\0';
			running = strdup (s);
			result = strsep(&running, ",");
			count = 0;
			key = NULL;
			name = NULL;
			enabled = NULL;
			type = NULL;
			while (result) {
				if (count == 0)
					key = result;
				if (count == 1)
					enabled = result;	
				if (count == 2)
					name = result;
				if (count == 4)
					type = result;
				count++;
				result = strsep(&running, ",");
			}
			if (strcmp(key, argv[2]) != 0)
				continue;
			
			if (!(name && enabled))
				continue;
			
			if (strspn(name, LETTERS_NUMBERS) != strlen(name)) {
				fprintf(stderr, "Bad connection name: %s\n", name);
				goto EXIT;
			}

			if (! (strcmp(type, "host") == 0 || strcmp(type, "net") == 0)) {
				fprintf(stderr, "Bad connection type: %s\n", type);
				goto EXIT;
			}
			
			if (strcmp(argv[1], "S") == 0 && strcmp(enabled, "on") == 0) {
				safe_system("/usr/sbin/ipsec auto --rereadsecrets >/dev/null");
				memset(command, 0, STRING_SIZE);
				snprintf(command, STRING_SIZE - 1, 
					"/usr/sbin/ipsec auto --replace %s >/dev/null", name);
				safe_system(command);
				if (strcmp(type, "net") == 0) {
					memset(command, 0, STRING_SIZE);
					snprintf(command, STRING_SIZE - 1, 
						"/usr/sbin/ipsec auto --asynchronous --up %s >/dev/null", name);
					safe_system(command);
				}
			} else if (strcmp(argv[1], "D") == 0) {
				safe_system("/usr/sbin/ipsec auto --rereadsecrets >/dev/null");
				memset(command, 0, STRING_SIZE);
				snprintf(command, STRING_SIZE - 1, 
					"/usr/sbin/ipsec auto --down %s >/dev/null", name);
				safe_system(command);
				memset(command, 0, STRING_SIZE);
				snprintf(command, STRING_SIZE - 1, 
					"/usr/sbin/ipsec auto --delete %s >/dev/null", name);
				safe_system(command);
			}
		}
	} else {
		fprintf(stderr, "Bad arg\n");
		usage();
		exit(1);
	}

EXIT:
	if (file)
		fclose(file);
	return 0;
}
