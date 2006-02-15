/*
 * This file is part of the IPCop Firewall.
 *
 * IPCop is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * IPCop is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with IPCop; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
 *
 * Copyright 2002: Mark Wormgoor <mark@wormgoor.com>
 * 
 * $Id: upgrade-v12-v13.c,v 1.2.2.3 2004/11/11 09:39:25 alanh Exp $
 * 
 */

#include "install.h"

void _convert_ppp_settings() {
	DIR *dirp;
	struct dirent *dp;
	char filename[STRING_SIZE];
	
	dirp = opendir( "/harddisk/var/ipcop/ppp" );
	while ( (dp = readdir( dirp )) != NULL ) {
		if ( strstr( dp->d_name, "settings" ) == dp->d_name ) {
			snprintf (filename, STRING_SIZE-1, "%s/%s", 
				"/harddisk/var/ipcop/ppp", dp->d_name);

			/* reduce furthur replacements from commands below */
			replace (filename, "TYPE=modem", "");
			replace (filename, "COMPORT=ttyS0", "TYPE=modem\nCOMPORT=ttyS0");
			replace (filename, "COMPORT=ttyS1", "TYPE=modem\nCOMPORT=ttyS1");
			replace (filename, "COMPORT=ttyS2", "TYPE=modem\nCOMPORT=ttyS2");
			replace (filename, "COMPORT=ttyS3", "TYPE=modem\nCOMPORT=ttyS3");
			/* reduce furthur replacements from commands below */
			replace (filename, "TYPE=isdn", "");
			replace (filename, "COMPORT=isdn1", "TYPE=isdn\nCOMPORT=isdn1");
			replace (filename, "COMPORT=isdn2", "TYPE=isdn\nCOMPORT=isdn2");
			replace (filename, "COMPORT=pppoe", "TYPE=pppoe");
			replace (filename, "COMPORT=pptp", "TYPE=pptp");
			replace (filename, "COMPORT=usbadsl", "TYPE=alcatelusb");
			replace (filename, "COMPORT=pppoa", "TYPE=pulsardsl");

			chown (filename, 99, 99);
		}	
	}
	(void) closedir( dirp );
}

int _convert_xtaccess() {
	int count=1, count2=0;
        FILE *portfw1, *portfw2;
        char portsrctemp[STRING_SIZE], portdsttemp[STRING_SIZE];
	char *portproto, *portsrcip, *portsrcport, *portdstip, *portdstport, *portenabled, *portremip;

        FILE *xtaccess1, *xtaccess2;
	char xtsrctemp[STRING_SIZE], xtdsttemp[STRING_SIZE];
	char *xtproto, *xtsrcip, *xtdstip, *xtdstport, *xtenabled;
        
	if (!(portfw1 = fopen ("/harddisk/var/ipcop/portfw/config", "r"))) return 1;
	if (!(portfw2 = fopen ("/harddisk/var/ipcop/portfw/config.new", "w"))) 
	{
		fclose(portfw1);
		return 1;
	}

        while (fgets (portsrctemp, STRING_SIZE, portfw1) != NULL) {
        	count2 = 0;
		portproto   = NULL;
		portsrcip   = NULL;
		portsrcport = NULL;
		portdstip   = NULL;
		portdstport = NULL;
		portremip   = NULL;
		portenabled = NULL;
		
		if (!(xtaccess1 = fopen ("/harddisk/var/ipcop/xtaccess/config", "r"))) 
		{
			fclose(portfw1);
			fclose(portfw2);
			return 1;
		}
		if (!(xtaccess2 = fopen ("/harddisk/var/ipcop/xtaccess/config.new", "w"))) 
		{
			fclose(portfw1);
			fclose(portfw2);
			fclose(xtaccess1);
			return 1;
		}

		if (isdigit (portsrctemp[0])) {
			/* Already converted to new format */
			fputs(portsrctemp, portfw2);
			continue;
		}

		if (portsrctemp[strlen(portsrctemp) - 1] == '\n')
			portsrctemp[strlen(portsrctemp) - 1] = '\0';
		portproto   = strtok (portsrctemp, ",");
		portsrcport = strtok (NULL, ",");
		portdstip   = strtok (NULL, ",");
		portdstport = strtok (NULL, ",");
		portenabled = strtok (NULL, ",");
		portsrcip   = strtok (NULL, ",");
		portremip   = strtok (NULL, ",");
		if (!(portproto && portsrcport && portdstip && 
			portdstport && portenabled ))
			continue;

		if (portsrcip == NULL) portsrcip = strdup ("0.0.0.0");

	        while (fgets (xtsrctemp, STRING_SIZE, xtaccess1)) {
			xtproto   = NULL;
			xtsrcip   = NULL;
			xtdstip   = NULL;
			xtdstport = NULL;
			xtenabled = NULL;

			if (xtsrctemp[strlen(xtsrctemp) - 1] == '\n')
				xtsrctemp[strlen(xtsrctemp) - 1] = '\0';
			xtproto   = strtok (xtsrctemp, ",");
			xtsrcip   = strtok (NULL, ",");
			xtdstport = strtok (NULL, ",");
			xtenabled = strtok (NULL, ",");
			xtdstip   = strtok (NULL, ",");
			if (!(xtproto && xtsrcip && xtdstport && xtenabled)) continue;

			if (xtdstip == NULL) xtdstip = strdup ("0.0.0.0");

			if (strcmp (portproto, xtproto) == 0 &&
					strcmp (portsrcport, xtdstport) == 0 &&
					strcmp (portsrcip, xtdstip) == 0) {
				portremip = strdup (xtsrcip);
				if ((strcmp (portremip, "0.0.0.0/0") == 0) && (count2 == 0)) {
					sprintf (portdsttemp, "%d,%d,%s,%s,%s,%s,%s,%s,%s\n",
						count, count2, portproto, portsrcport, portdstip,
						portdstport, portenabled, portsrcip, portremip);
					fputs(portdsttemp, portfw2);
				} else {
					if (count2 == 0) {
						sprintf (portdsttemp, "%d,%d,%s,%s,%s,%s,%s,%s,%d\n",
							count,count2,portproto, portsrcport, portdstip,
							portdstport, portenabled, portsrcip, 0);
						fputs(portdsttemp, portfw2);
						count2++;
					}
					sprintf (portdsttemp, "%d,%d,%s,%d,%s,%s,%s,%d,%s\n",
						count,count2,portproto, 0, portdstip,
						portdstport, portenabled, 0, portremip);
					fputs(portdsttemp, portfw2);
				}
				count2++;
			} else {
				sprintf (xtdsttemp, "%s,%s,%s,%s,%s\n",
					xtproto, xtsrcip, xtdstport, xtenabled, xtdstip);
				fputs(xtdsttemp, xtaccess2);
			}
                }

		/* Close source and destination xtaccess files */
		fclose (xtaccess1);
		fclose (xtaccess2);

		/* Move the new xtaccess file */
		rename ("/harddisk/var/ipcop/xtaccess/config.new",
			"/harddisk/var/ipcop/xtaccess/config");

		/* If no external access line existed, add a no access line */
		if (count2 == 0) {
			if (portremip == NULL) portremip = strdup ("127.0.0.1/32");

			/* Print new port forwarding line to file */
			sprintf (portdsttemp, "%d,%d,%s,%s,%s,%s,%s,%s,%s\n",
				count, count2, portproto, portsrcport, portdstip, 
				portdstport, portenabled, portsrcip, portremip);
			fputs(portdsttemp, portfw2);
		}
		count++;
	}

	/* Close source and destination portfw files */
	fclose (portfw1);
	fclose (portfw2);

	/* Move the new portfw file */
	rename ("/harddisk/var/ipcop/portfw/config.new",
		"/harddisk/var/ipcop/portfw/config");
	chown  ("/harddisk/var/ipcop/xtaccess/config", 99, 99);
	chown  ("/harddisk/var/ipcop/portfw/config", 99, 99);

	return 0;
}

int _convert_pulsardsl() {
	DIR *dirp;
	struct dirent *dp;
	char filename[STRING_SIZE];
	FILE *settings, *pulsardsl;
	char line[STRING_SIZE];
	
	if (!(pulsardsl = fopen ("/harddisk/var/ipcop/pciadsl/settings", "r"))) return 1;
	
	dirp = opendir( "/harddisk/var/ipcop/ppp" );
	while ( (dp = readdir( dirp )) != NULL ) {
		if ( strstr( dp->d_name, "settings" ) == dp->d_name ) {
			snprintf (filename, STRING_SIZE-1, "%s/%s", 
				"/harddisk/var/ipcop/ppp", dp->d_name);
        		if (!(settings = fopen (filename, "r+"))) {
				closedir(dirp);
				fclose(pulsardsl);
				return 1;
			}
			while (fgets (line, STRING_SIZE, settings) != NULL) {
				if (strstr (line, "TYPE=pulsardsl") == line) {
					fseek(settings,0,SEEK_END);
					rewind(pulsardsl);
					while (fgets(line, STRING_SIZE, pulsardsl) != NULL) {
						fputs (line, settings);
					}
					fclose (settings);
					chown (filename, 99, 99);
				}
			}
		}
	}
	fclose(pulsardsl);
	(void) closedir( dirp );


	return 0;
}

int _convert_pulsardsl_ethernet() {
	DIR *dirp;
	struct dirent *dp;
	FILE *ethernet, *settings;
	char line[STRING_SIZE];
	char type[STRING_SIZE];
	char ip[STRING_SIZE];
	char filename[STRING_SIZE];
	
	if (!(ethernet = fopen ("/harddisk/var/ipcop/ethernet/settings", "r"))) return 1;

	while (fgets (line, STRING_SIZE, ethernet) != NULL) {
		if (strstr (line, "RED_DRIVER=pciadsl") == line) {
			rewind (ethernet);
			while (fgets (line, STRING_SIZE, ethernet) != NULL) {
				if (strstr (line, "RED_TYPE") == line) {
					strcpy (type, line + 9*sizeof(char));
					if (type[strlen(type) - 1] == '\n')
						type[strlen(type) - 1] = '\0';
				}
				if (strstr (line, "RED_ADDRESS") == line) {
					strcpy (ip, line + 12*sizeof(char));
					if (ip[strlen(ip) - 1] == '\n')
						type[strlen(ip) - 1] = '\0';
				}
				fclose (ethernet);

				replace ("/harddisk/var/ipcop/ethernet/settings", "RED_DEV=eth1", "RED_DEV=");
				replace ("/harddisk/var/ipcop/ethernet/settings", "CONFIG_TYPE=2", "CONFIG_TYPE=0");
				replace ("/harddisk/var/ipcop/ethernet/settings", "CONFIG_TYPE=3", "CONFIG_TYPE=1");
				replace ("/harddisk/var/ipcop/ethernet/settings", "RED_DEV=eth2", "RED_DEV=");
				chown ("/harddisk/var/ipcop/ethernet/settings", 99, 99);
				
				dirp = opendir( "/harddisk/var/ipcop/ppp" );
				while ( (dp = readdir( dirp )) != NULL ) {
					if ( strstr( dp->d_name, "settings-" ) == dp->d_name ) {
						snprintf (filename, STRING_SIZE-1, "%s/%s", 
							"/harddisk/var/ipcop/ppp", dp->d_name);
			        		if (!(settings = fopen (filename, "r+"))) 
						{
							closedir(dirp);
							return 1;
						}
						while (fgets (line, STRING_SIZE, settings) != NULL) {
							if (strstr (line, "TYPE=pulsardsl") == line) {
								fseek(settings,0,SEEK_END);
								fprintf (settings, "METHOD=%s\n", type);
								fprintf (settings, "IP=%s\n", ip);
								fclose (settings);
								chown (filename, 99, 99);
							}
						}
					}
				}
				(void) closedir( dirp );
			}
		}
	}

	return 0;
}

int upgrade_v12_v13() {
	struct stat s;
	replace ("/harddisk/var/ipcop/ethernet/settings", "rtl8139", "8139too");
	replace ("/harddisk/var/ipcop/vpn/ipsec.conf", "auto=add", "auto=start");
	chown ("/harddisk/var/ipcop/vpn/ipsec.conf", 99, 99);
	chown ("/harddisk/var/ipcop/ethernet/settings", 99, 99);
	chown ("/harddisk/var/ipcop/main/settings", 99, 99);
	_convert_ppp_settings();
	_convert_xtaccess();
	_convert_pulsardsl();
	_convert_pulsardsl_ethernet();

	/* Rename usbadsl directory */
	stat ("/harddisk/var/ipcop/usbadsl", &s);
	if (S_ISDIR(s.st_mode)) {
		remove ("/harddisk/var/ipcop/usbadsl/settings");
		if (! system("/bin/chroot /harddisk /bin/rm -rf /var/ipcop/alcatelusb"))
			rename ("/harddisk/var/ipcop/usbadsl", "/harddisk/var/ipcop/alcatelusb");
	}
	
	/* Rename pciadsl module and directory */
	remove ("/harddisk/var/ipcop/pulsar/settings");
	rename ("/harddisk/var/ipcop/pciadsl/pciadsl.o", "/harddisk/var/ipcop/pciadsl/pulsar.o");
	stat ("/harddisk/var/ipcop/pciadsl", &s);
	if (S_ISDIR(s.st_mode)) {
		if (! system("/bin/chroot /harddisk /bin/rm -rf /var/ipcop/pulsardsl"))
			rename ("/harddisk/var/ipcop/pciadsl", "/harddisk/var/ipcop/pulsardsl");
	}

	/* Change squid cache directory */
	replace ("/harddisk/var/ipcop/proxy/squid.conf", "/var/spool/squid", "/var/log/cache");
	chown ("/harddisk/var/ipcop/proxy/squid.conf", 99, 99);
	
	/* Change setup user shell */
	replace ("/harddisk/etc/passwd", ":/usr/local/sbin/setup", ":/bin/bash -c /usr/local/sbin/setup");
	
	return 0;
}
