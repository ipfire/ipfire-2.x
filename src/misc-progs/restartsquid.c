/* SmoothWall helper program - restartsquid
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Restarting squid with transparent proxying.
 *
 * 05/02/2004 - Roy Walker <rwalker@miracomnetwork.com>
 * Exclude red network from transparent proxy to allow browsing to alias IPs
 * Read in VPN settings and exclude each VPN network from transparent proxy
 * 
 * $Id: restartsquid.c,v 1.7.2.8 2005/04/22 18:44:37 rkerr Exp $
 * 
 */
 
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <pwd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include "libsmooth.h"
#include "setuid.h"

int main(int argc, char *argv[])
{
	int fd = -1;
	int enable = 0;
	int enablevpn = 0;
	int transparent = 0;
	int enable_blue = 0;
	int transparent_blue = 0;
	int running = 0;
	struct stat st;
	FILE *ipfile;
	char localip[STRING_SIZE] = "";
	struct keyvalue *net = NULL;
	struct keyvalue *squid = NULL;
	char buffer[STRING_SIZE];
	char proxy_port[STRING_SIZE];
	char s[STRING_SIZE];
	char green_dev[STRING_SIZE] = "";
	char blue_dev[STRING_SIZE] = "";
	char red_netaddress[STRING_SIZE] = "";
	char red_netmask[STRING_SIZE] = "";
	char configtype[STRING_SIZE] = "";
	char redtype[STRING_SIZE] = "";
	char enableredvpn[STRING_SIZE] = "";
	char enablebluevpn[STRING_SIZE] = "";

	if (!(initsetuid()))
		exit(1);

	/* Kill running squid */
	safe_system("/sbin/iptables -t nat -F SQUID");
	safe_system("/usr/sbin/squid -k shutdown >/dev/null 2>/dev/null");
	sleep(5);
	safe_system("/bin/killall -9 squid >/dev/null 2>/dev/null");
	
	/* See if proxy is enabled and / or transparent */
	if ((fd = open(CONFIG_ROOT "/proxy/enable", O_RDONLY)) != -1)
	{
		close(fd);
		enable = 1;
	}
	if ((fd = open(CONFIG_ROOT "/proxy/transparent", O_RDONLY)) != -1)
	{
		close(fd);
		transparent = 1;
	}
	if ((fd = open(CONFIG_ROOT "/proxy/enable_blue", O_RDONLY)) != -1)
	{
		close(fd);
		enable_blue = 1;
	}
	if ((fd = open(CONFIG_ROOT "/proxy/transparent_blue", O_RDONLY)) != -1)
	{
		close(fd);
		transparent_blue = 1;
	}

	/* Read the network configuration */
	net=initkeyvalues();
	if (!readkeyvalues(net, CONFIG_ROOT "/ethernet/settings"))
	{
		fprintf(stderr, "Cannot read ethernet settings\n");
		exit(1);
	}
	if (!findkey(net, "GREEN_DEV", green_dev))
	{
		fprintf(stderr, "Cannot read GREEN_DEV\n");
		exit(1);
	}
	if (!VALID_DEVICE(green_dev))
	{
		fprintf(stderr, "Bad GREEN_DEV: %s\n", green_dev);
		exit(1);
	}
	if (!findkey(net, "CONFIG_TYPE", configtype))
	{
		fprintf(stderr, "Cannot read CONFIG_TYPE\n");
		exit(1);
	}

	findkey(net, "RED_TYPE", redtype);
	findkey(net, "RED_NETADDRESS", red_netaddress);
	findkey(net, "RED_NETMASK", red_netmask);
	findkey(net, "BLUE_DEV", blue_dev);
	freekeyvalues(net);

	/* See if VPN software is enabled */
	net=initkeyvalues();
	if (!readkeyvalues(net, CONFIG_ROOT "/vpn/settings"))
	{
		fprintf(stderr, "Cannot read vpn settings\n");
		exit(1);
	}
	findkey(net, "ENABLED", enableredvpn);
	findkey(net, "ENABLED_BLUE", enablebluevpn);
	freekeyvalues(net);
	if (	(!strcmp(enableredvpn, "on") && VALID_IP(localip)) || 
		(!strcmp(enablebluevpn, "on") && VALID_DEVICE(blue_dev)) ) {
			enablevpn = 1;
	}

	/* Retrieve the Squid pid file */
	if ((fd = open("/var/run/squid.pid", O_RDONLY)) != -1)
	{
		close(fd);
		running = 1;
	}

	/* Retrieve the RED ip address */
	stat(CONFIG_ROOT "/red/local-ipaddress", &st);
	if (S_ISREG(st.st_mode)) {
		if (!(ipfile = fopen(CONFIG_ROOT "/red/local-ipaddress", "r")))
		{
			fprintf(stderr, "Couldn't open ip file\n");
			exit(0); 
		}
		if (fgets(localip, STRING_SIZE, ipfile))
		{
			if (localip[strlen(localip) - 1] == '\n')
				localip[strlen(localip) - 1] = '\0';
		}
		fclose(ipfile);
		if (!VALID_IP(localip))
		{
			fprintf(stderr, "Bad ip: %s\n", localip);
			exit(0);
		}
	}

	/* See if we need to flush the cache */
	if (argc >=2) {
		if (strcmp(argv[1], "-f") == 0) {
			if (stat("/var/log/cache/swap.state", &st) == 0) {
				struct passwd *pw;
				if((pw = getpwnam("squid"))) {
					endpwent(); /* probably paranoia, but just in case.. */
					unpriv_system("/bin/echo > /var/log/cache/swap.state", pw->pw_uid, pw->pw_gid);
				} else { endpwent(); }
			}
		}
	}

	if (enable || enable_blue)
	{
		safe_system("/usr/sbin/squid -D -z"); 
		safe_system("/usr/sbin/squid -D");
	}

	/* Retrieve the proxy port */
	if (transparent || transparent_blue) {
		squid=initkeyvalues();

		if (!readkeyvalues(squid, CONFIG_ROOT "/proxy/settings"))
		{
			fprintf(stderr, "Cannot read proxy settings\n");
			exit(1);
		}

		if (!(findkey(squid, "PROXY_PORT", proxy_port)))
		{
			strcpy (proxy_port, "800");
		} else {
			if(strspn(proxy_port, NUMBERS) != strlen(proxy_port))
			{
				fprintf(stderr, "Invalid proxy port: %s, defaulting to 800\n", proxy_port);
				strcpy(proxy_port, "800");
			}
		}
		freekeyvalues(squid);
	}

	if (transparent && enable) {
		int count;
		char *result;
		char *name;
		char *type;
		char *running;
		char *vpn_network_mask;
		char *vpn_netaddress;
		char *vpn_netmask;
		FILE *file = NULL;
		char *conn_enabled;
		
		/* Darren Critchley - check to see if RED VPN is enabled before mucking with rules */
		if (!strcmp(enableredvpn, "on")) {
			/* Read the /vpn/config file - no check to see if VPN is enabled */
			if (!(file = fopen(CONFIG_ROOT "/vpn/config", "r"))) {
				fprintf(stderr, "Couldn't open vpn config file");
				exit(1);
			}

				while (fgets(s, STRING_SIZE, file) != NULL) {
					if (s[strlen(s) - 1] == '\n')
						s[strlen(s) - 1] = '\0';
					running = strdup (s);
					result = strsep(&running, ",");
					count = 0;
					name = NULL;
					type = NULL;
					vpn_network_mask = NULL;
					conn_enabled = NULL;
					while (result) {
						if (count == 1)
							conn_enabled = result;
						if (count == 2)
							name = result;
						if (count == 4)
							type = result;
						if (count == 12 )
							vpn_network_mask = result;
						count++;
						result = strsep(&running, ",");
					}
	
					if (strspn(name, LETTERS_NUMBERS) != strlen(name)) {
						fprintf(stderr, "Bad connection name: %s\n", name);
						exit(1);
					}
	
					if (! (strcmp(type, "net") == 0)) {
						continue;
					}
	
					/* Darren Critchley - new check to see if connection is enabled */
					if (! (strcmp(conn_enabled, "on") == 0)) {
						continue;
					}
	
					result = strsep(&vpn_network_mask, "/");
					count = 0;
					vpn_netaddress = NULL;
					vpn_netmask = NULL;
					while (result) {
						if (count == 0)
							vpn_netaddress = result;
						if (count == 1)
							vpn_netmask = result;
						count++;
						result = strsep(&vpn_network_mask, "/");
					}
	
					if (!VALID_IP(vpn_netaddress)) {
						fprintf(stderr, "Bad network for vpn connection %s: %s\n", name, vpn_netaddress);
						continue;
					}
	
					if ((!VALID_IP(vpn_netmask)) && (!VALID_SHORT_MASK(vpn_netmask))) {
						fprintf(stderr, "Bad mask for vpn connection %s: %s\n", name, vpn_netmask);
						continue;
					}
	
					memset(buffer, 0, STRING_SIZE);
					if( snprintf(buffer, STRING_SIZE - 1, "/sbin/iptables -t nat -A SQUID -i %s -p tcp -d %s/%s --dport 80 -j RETURN", green_dev, vpn_netaddress, vpn_netmask) >= STRING_SIZE )
					{
						fprintf(stderr, "Command too long\n");
						exit(1);
					}
					safe_system(buffer);
				}
		}	
		
		memset(buffer, 0, STRING_SIZE);
		if ( (	(strcmp(configtype, "2")==0) || (strcmp(configtype, "3")==0)  || 
			(strcmp(configtype, "6")==0) || (strcmp(configtype, "7")==0) ) &&
			(VALID_IP(red_netaddress)) && (VALID_IP(red_netmask)) && 
			(strcmp(redtype, "STATIC")==0) ) 
		{
			memset(buffer, 0, STRING_SIZE);
			if( snprintf(buffer, STRING_SIZE - 1, "/sbin/iptables -t nat -A SQUID -i %s -p tcp -d %s/%s --dport 80 -j RETURN", green_dev, red_netaddress, red_netmask) >= STRING_SIZE )
			{
				fprintf(stderr, "Command too long\n");
				exit(1);
			}
			safe_system(buffer);
		} else if (VALID_IP(localip)) {
			memset(buffer, 0, STRING_SIZE);
			if( snprintf(buffer, STRING_SIZE - 1, "/sbin/iptables -t nat -A SQUID -i %s -p tcp -d %s --dport 80 -j RETURN", green_dev, localip) >= STRING_SIZE )
			{
				fprintf(stderr, "Command too long\n");
				exit(1);
			}
			safe_system(buffer);
		}

		memset(buffer, 0, STRING_SIZE);
		if( snprintf(buffer, STRING_SIZE - 1, "/sbin/iptables -t nat -A SQUID -i %s -p tcp --dport 80 -j REDIRECT --to-port %s", green_dev, proxy_port) >= STRING_SIZE )
		{
			fprintf(stderr, "Command too long\n");
			exit(1);
		}
		safe_system(buffer);
	}

	if (transparent_blue && enable_blue) {
		int count;
		char *result;
		char *name;
		char *type;
		char *running;
		char *vpn_network_mask;
		char *vpn_netaddress;
		char *vpn_netmask;
		char *conn_enabled;
		FILE *file = NULL;

		if (! VALID_DEVICE(blue_dev))
		{
			fprintf(stderr, "Bad BLUE_DEV: %s\n", blue_dev);
			exit(1);
		}

		/* Darren Critchley - check to see if BLUE VPN is enabled before mucking with rules */
		if (!strcmp(enablebluevpn, "on")) {
			/* Read the /vpn/config file - no check to see if VPN is enabled */
			if (!(file = fopen(CONFIG_ROOT "/vpn/config", "r"))) {
				fprintf(stderr, "Couldn't open vpn config file");
				exit(1);
				}
				while (fgets(s, STRING_SIZE, file) != NULL) {
					if (s[strlen(s) - 1] == '\n')
						s[strlen(s) - 1] = '\0';
					running = strdup (s);
					result = strsep(&running, ",");
					count = 0;
					name = NULL;
					type = NULL;
					vpn_network_mask = NULL;
					conn_enabled = NULL;
					while (result) {
						if (count == 1)
							conn_enabled = result;
						if (count == 2)
							name = result;
						if (count == 4)
							type = result;
						if (count == 12 )
							vpn_network_mask = result;
						count++;
						result = strsep(&running, ",");
					}
	
					if (strspn(name, LETTERS_NUMBERS) != strlen(name)) {
						fprintf(stderr, "Bad connection name: %s\n", name);
						exit(1);
					}
	
					if (! (strcmp(type, "net") == 0)) {
						continue;
					}
	
					/* Darren Critchley - new check to see if connection is enabled */
					if (! (strcmp(conn_enabled, "on") == 0)) {
						continue;
					}
	
					result = strsep(&vpn_network_mask, "/");
					count = 0;
					vpn_netaddress = NULL;
					vpn_netmask = NULL;
					while (result) {
						if (count == 0)
							vpn_netaddress = result;
						if (count == 1)
							vpn_netmask = result;
						count++;
						result = strsep(&vpn_network_mask, "/");
					}
	
					if (!VALID_IP(vpn_netaddress)) {
						fprintf(stderr, "Bad network for vpn connection %s: %s\n", name, vpn_netaddress);
						continue;
					}
	
					if ((!VALID_IP(vpn_netmask)) && (!VALID_SHORT_MASK(vpn_netmask))) {
						fprintf(stderr, "Bad mask for vpn connection %s: %s\n", name, vpn_netmask);
						continue;
					}
	
					memset(buffer, 0, STRING_SIZE);
					if (snprintf(buffer, STRING_SIZE - 1, "/sbin/iptables -t nat -A SQUID -i %s -p tcp -d %s/%s --dport 80 -j RETURN", blue_dev, vpn_netaddress, vpn_netmask) >= STRING_SIZE )
					{
						fprintf(stderr, "Command too long\n");
						exit(1);
					}
					safe_system(buffer);
				}
		}
	
		memset(buffer, 0, STRING_SIZE);
		if ( (	(strcmp(configtype, "2")==0) || (strcmp(configtype, "3")==0)  ||
			(strcmp(configtype, "6")==0) || (strcmp(configtype, "7")==0) ) &&
			(VALID_IP(red_netaddress)) && (VALID_IP(red_netmask)) &&
			(strcmp(redtype, "STATIC")==0) )
		{
			memset(buffer, 0, STRING_SIZE);
			if( snprintf(buffer, STRING_SIZE - 1, "/sbin/iptables -t nat -A SQUID -i %s -p tcp -d %s/%s --dport 80 -j RETURN", blue_dev, red_netaddress, red_netmask) >= STRING_SIZE )
			{
				fprintf(stderr, "Command too long\n");
				exit(1);
			}
			safe_system(buffer);
		} else if (VALID_IP(localip)) {
			memset(buffer, 0, STRING_SIZE);
			if( snprintf(buffer, STRING_SIZE - 1, "/sbin/iptables -t nat -A SQUID -i %s -p tcp -d %s --dport 80 -j RETURN", blue_dev, localip) >= STRING_SIZE )
			{
				fprintf(stderr, "Command too long\n");
				exit(1);
			}
			safe_system(buffer);
		}

		memset(buffer, 0, STRING_SIZE);
		if( snprintf(buffer, STRING_SIZE - 1, "/sbin/iptables -t nat -A SQUID -i %s -p tcp --dport 80 -j REDIRECT --to-port %s", blue_dev, proxy_port) >= STRING_SIZE )
		{
			fprintf(stderr, "Command too long\n");
			exit(1);
		}
		safe_system(buffer);
	}
	
	return 0;
}
