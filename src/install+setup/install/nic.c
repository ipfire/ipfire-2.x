/* SmoothWall install program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Contains stuff related to firing up the network card, including a crude
 * autodector.
 * 
 */

#include "install.h"

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

extern FILE *flog;
extern char *mylog;

extern char **ctr;

extern struct nic nics[];

int networkmenu(struct keyvalue *ethernetkv)
{
	int rc;
	char driver[STRING_SIZE] = "";
	char driveroptions[STRING_SIZE] = "";
	struct keyvalue *kv = initkeyvalues();
	int result = 0;
	char commandstring[STRING_SIZE];
	char address[STRING_SIZE], netmask[STRING_SIZE];
	int done;
	FILE *handle;
	char line[STRING_SIZE];
	char description[1000];
	char message[1000];
	char title[STRING_SIZE];
	done = 0;

	while (!done)
	{
		rc = newtWinTernary(ctr[TR_CONFIGURE_NETWORKING], ctr[TR_PROBE], 
			ctr[TR_SELECT], ctr[TR_CANCEL], ctr[TR_CONFIGURE_NETWORKING_LONG]);
		
		if (rc == 0 || rc == 1)
		{
			sprintf(commandstring, "/bin/probenic.sh 1");
			sprintf(message, ctr[TR_PROBING_FOR_NICS]);
			runcommandwithstatus(commandstring, message);

			if ((handle = fopen("/nicdriver", "r")))
			{
				char *driver;
				fgets(line, STRING_SIZE-1, handle);
				fclose(handle);
				line[strlen(line) - 1] = 0;
				driver = strtok(line, ".");
				fprintf(flog, "Detected NIC driver: %s\n",driver);
				if (strlen(driver) > 1) {
					strcpy(driveroptions, "");
					findnicdescription(driver, description);
					sprintf (title, "%s %s - %s", NAME, VERSION, SLOGAN);
					sprintf(message, ctr[TR_FOUND_NIC], NAME, description);
					newtWinMessage(title, ctr[TR_OK], message);
				} else {
					errorbox(ctr[TR_PROBE_FAILED]);
				}
			}
		}
		else if (rc == 2)
			choosecards(driver, driveroptions);
		else
			done = 1;
	}

	/* Default is a GREEN nic only. */
	/* Smoothie is not untarred yet, so we have to delay actually writing the
	 * settings till later. */
	replacekeyvalue(ethernetkv, "CONFIG_TYPE", "0");
	replacekeyvalue(ethernetkv, "GREEN_DRIVER", driver);
	replacekeyvalue(ethernetkv, "GREEN_DRIVER_OPTIONS", driveroptions);
	replacekeyvalue(ethernetkv, "GREEN_DEV", "eth0");
	replacekeyvalue(ethernetkv, "GREEN_DISPLAYDRIVER", driver);
	
	if (!(changeaddress(ethernetkv, "GREEN", 0, "")))
		goto EXIT;
	
	strcpy(address, ""); findkey(ethernetkv, "GREEN_ADDRESS", address);
	strcpy(netmask, ""); findkey(ethernetkv, "GREEN_NETMASK", netmask);

	snprintf(commandstring, STRING_SIZE, "/bin/ifconfig eth0 %s netmask %s up", 
		address, netmask);
	if (mysystem(commandstring))
	{
		errorbox(ctr[TR_INTERFACE_FAILED_TO_COME_UP]);
		goto EXIT;
	}

	result = 1;
	
EXIT:
	freekeyvalues(kv);
	
	return result;
}

