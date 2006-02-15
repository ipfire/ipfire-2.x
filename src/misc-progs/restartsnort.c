/* SmoothWall helper program - restartsnort
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Restarting snort.
 * 
 * $Id: restartsnort.c,v 1.8.2.3 2005/10/16 12:36:14 rkerr Exp $
 * 
 */
 
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <string.h>
#include <fcntl.h>
#include <signal.h>
#include "libsmooth.h"
#include "setuid.h"

struct keyvalue *kv = NULL;
FILE *varsfile = NULL;

void exithandler(void)
{
	if (varsfile)
		fclose (varsfile);

	if (kv)
		freekeyvalues(kv);
}

int killsnort(char *interface)
{
	int fd;
	char pidname[STRING_SIZE] = "";
	char buffer[STRING_SIZE] = "";
	int pid;

	sprintf(pidname, "/var/run/snort_%s.pid", interface);

	if ((fd = open(pidname, O_RDONLY)) != -1)
	{
		if (read(fd, buffer, STRING_SIZE - 1) == -1)
			fprintf(stderr, "Couldn't read from pid file\n");
		else
		{
			pid = atoi(buffer);
			if (pid <= 1)
				fprintf(stderr, "Bad pid value\n");
			else
			{
				if (kill(pid, SIGTERM) == -1)
					fprintf(stderr, "Unable to send SIGTERM\n");
				close (fd);
				return 0;
			}
		}
		close(fd);
	}
	return 1;
}

int main(int argc, char *argv[])
{
	int fd = -1;
	FILE *ifacefile, *ipfile, *dns1file, *dns2file;
	char iface[STRING_SIZE] = "";
	char locip[STRING_SIZE] = "";
	char dns1[STRING_SIZE] = "";
	char dns2[STRING_SIZE] = "";
	char command[STRING_SIZE] = "";
	char greendev[STRING_SIZE] = "";
	char orangedev[STRING_SIZE] = "";
	char bluedev[STRING_SIZE] = "";
	char greenip[STRING_SIZE] = "";
	char orangeip[STRING_SIZE] = "";
	char blueip[STRING_SIZE] = "";
	struct stat st;
	int i;
	int restartred = 0, restartgreen = 0, restartblue = 0, restartorange = 0;
	
	if (!(initsetuid()))
		exit(1);
	
	atexit(exithandler);

	for (i=0; i<argc; i++) {
		if (!strcmp(argv[i], "red"))
			restartred = 1;
		if (!strcmp(argv[i], "orange"))
			restartorange = 1;
		if (!strcmp(argv[i], "blue"))
			restartblue = 1;
		if (!strcmp(argv[i], "green"))
			restartgreen = 1;
	}
	
	kv = initkeyvalues();
	if (!(readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings")))
		exit(1);

	if (! findkey(kv, "GREEN_DEV", greendev)) {
		fprintf(stderr, "Couldn't find GREEN device\n");
		exit(1);
	}
	if (! strlen (greendev) > 0) {
		fprintf(stderr, "Couldn't find GREEN device\n");
		exit(1);
	}
	if (!VALID_DEVICE(greendev))
	{
		fprintf(stderr, "Bad GREEN_DEV: %s\n", greendev);
		exit(1);
	}
	if (!(findkey(kv, "GREEN_ADDRESS", greenip))) {
		fprintf(stderr, "Couldn't find GREEN address\n");
		exit(1);
	}
	if (!VALID_IP(greenip)) {
		fprintf(stderr, "Bad GREEN_ADDRESS: %s\n", greenip);
		exit(1);
	}

	if (findkey(kv, "ORANGE_DEV", orangedev) && strlen (orangedev) > 0) {
		if (!VALID_DEVICE(orangedev))
		{
			fprintf(stderr, "Bad ORANGE_DEV: %s\n", orangedev);
			exit(1);
		}
		if (!(findkey(kv, "ORANGE_ADDRESS", orangeip))) {
			fprintf(stderr, "Couldn't find ORANGE address\n");
			exit(1);
		}
		if (!VALID_IP(orangeip)) {
			fprintf(stderr, "Bad ORANGE_ADDRESS: %s\n", orangeip);
			exit(1);
		}
	}

	if (findkey(kv, "BLUE_DEV", bluedev) && strlen (bluedev) > 0) {
		if (!VALID_DEVICE(bluedev))
		{
			fprintf(stderr, "Bad BLUE_DEV: %s\n", bluedev);
			exit(1);
		}
		if (!(findkey(kv, "BLUE_ADDRESS", blueip))) {
			fprintf(stderr, "Couldn't find BLUE address\n");
			exit(1);
		}
		if (!VALID_IP(blueip)) {
			fprintf(stderr, "Bad BLUE_ADDRESS: %s\n", blueip);
			exit(1);
		}
	}

	stat(CONFIG_ROOT "/red/active", &st);

	if (S_ISREG(st.st_mode)) {
		if (!(ifacefile = fopen(CONFIG_ROOT "/red/iface", "r")))
		{
			fprintf(stderr, "Couldn't open iface file\n");
			exit(0);
		}

		if (fgets(iface, STRING_SIZE, ifacefile))
		{
			if (iface[strlen(iface) - 1] == '\n')
				iface[strlen(iface) - 1] = '\0';
		}
		fclose(ifacefile);
		if (!VALID_DEVICE(iface))
		{
			fprintf(stderr, "Bad iface: %s\n", iface);
			exit(0);
		}

	        if (!(ipfile = fopen(CONFIG_ROOT "/red/local-ipaddress", "r")))
        	{
        	        fprintf(stderr, "Couldn't open local ip file\n");
	                exit(0);
        	}
		if (fgets(locip, STRING_SIZE, ipfile))
		{
		        if (locip[strlen(locip) - 1] == '\n')
        		        locip[strlen(locip) - 1] = '\0';
		}
        	fclose (ipfile);
		if (strlen(locip) && !VALID_IP(locip))
		{
			fprintf(stderr, "Bad local IP: %s\n", locip);
			exit(1);
		}
	
	        if (!(dns1file = fopen(CONFIG_ROOT "/red/dns1", "r")))
        	{
                	fprintf(stderr, "Couldn't open dns1 file\n");
	                exit(0);
        	}
		if (fgets(dns1, STRING_SIZE, dns1file))
		{
	        	if (dns1[strlen(dns1) - 1] == '\n')
	        	        dns1[strlen(dns1) - 1] = '\0';
		}
	        fclose (dns1file);
		if (strlen(dns1) && !VALID_IP(dns1))
		{
			fprintf(stderr, "Bad DNS1 IP: %s\n", dns1);
			exit(1);
		}
		        
	        if (!(dns2file = fopen(CONFIG_ROOT "/red/dns2", "r")))
        	{
	                fprintf(stderr, "Couldn't open dns2 file\n");
        	        exit(1);
	        }
		if (fgets(dns2, STRING_SIZE, dns2file))
		{
		        if (dns2[strlen(dns2) - 1] == '\n')
	        	        dns2[strlen(dns2) - 1] = '\0';
		}
	        fclose (dns2file);
		if (strlen(dns2) && !VALID_IP(dns2))
		{
			fprintf(stderr, "Bad DNS2 IP: %s\n", dns2);
			exit(1);
		}
	}

	if (restartred)
		killsnort(iface);

	if (restartblue)
		killsnort(bluedev);
	
	if (restartorange)
		killsnort(orangedev);

	if (restartgreen)
		killsnort(greendev);
        
	if (!(varsfile = fopen("/etc/snort/vars", "w")))
	{
		fprintf(stderr, "Couldn't create vars file\n");
		exit(1);
	}
	if (strlen(blueip)) {
		if (strlen(orangeip)) {
			if (strlen(locip)) {
				fprintf(varsfile, "var HOME_NET [%s,%s,%s,%s]\n", greenip, orangeip, blueip, locip);
			} else {
				fprintf(varsfile, "var HOME_NET [%s,%s,%s]\n", greenip, orangeip, blueip);
			}
		} else {
			if (strlen(locip)) {
				fprintf(varsfile, "var HOME_NET [%s,%s,%s]\n", greenip, blueip, locip);
			} else {
				fprintf(varsfile, "var HOME_NET [%s,%s]\n", greenip, blueip);
			}
		}
	} else {
		if (strlen(orangeip)) {
			if (strlen(locip)) {
				fprintf(varsfile, "var HOME_NET [%s,%s,%s]\n", greenip, orangeip, locip);
			} else {
				fprintf(varsfile, "var HOME_NET [%s,%s]\n", greenip, orangeip);
			}
		} else {
			if (strlen(locip)) {
				fprintf(varsfile, "var HOME_NET [%s,%s]\n", greenip, locip);
			} else {
				fprintf(varsfile, "var HOME_NET [%s]\n", greenip);
			}
		}
	}
	if (strlen(dns1))
	{
		if (strlen(dns2))
			fprintf(varsfile, "var DNS_SERVERS [%s,%s]\n", dns1, dns2);
		else
			fprintf(varsfile, "var DNS_SERVERS %s\n", dns1);
	} else {
		fprintf(varsfile, "var DNS_SERVERS []\n");
	}
	fclose(varsfile);
	varsfile = NULL;
	
	if (restartred && strlen(iface) && (fd = open(CONFIG_ROOT "/snort/enable", O_RDONLY)) != -1)
	{
		close(fd);
		snprintf(command, STRING_SIZE -1,
			"/usr/sbin/snort -c /etc/snort/snort.conf -D -u snort -g snort -d -e -o -p -b -A fast -m 022 -i %s",
			iface);
		safe_system(command);
	}
	if (restartblue && strlen(bluedev) && (fd = open(CONFIG_ROOT "/snort/enable_blue", O_RDONLY)) != -1 && bluedev)
        {
		close(fd);
		snprintf(command, STRING_SIZE -1,
			"/usr/sbin/snort -c /etc/snort/snort.conf -D -u snort -g snort -d -e -o -p -b -A fast -m 022 -i %s",
			bluedev);
		safe_system(command);
	}
	if (restartorange && strlen(orangedev) && (fd = open(CONFIG_ROOT "/snort/enable_orange", O_RDONLY)) != -1 && orangedev)
	{
		close(fd);
		snprintf(command, STRING_SIZE -1,
			"/usr/sbin/snort -c /etc/snort/snort.conf -D -u snort -g snort -d -e -o -p -b -A fast -m 022 -i %s",
			orangedev);
		safe_system(command);
	}
	if (restartgreen && (fd = open(CONFIG_ROOT "/snort/enable_green", O_RDONLY)) != -1)
	{
		close(fd);
		snprintf(command, STRING_SIZE -1,
			"/usr/sbin/snort -c /etc/snort/snort.conf -D -u snort -g snort -d -e -o -p -b -A fast -m 022 -i %s",
			greendev);
		safe_system(command);
	}

  return 0;
}
