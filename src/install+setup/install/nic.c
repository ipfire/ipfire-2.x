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

//extern struct nic nics[];
//extern struct knic knics[];

int networkmenu(struct keyvalue *ethernetkv)
{
	int rc;
	char driver[STRING_SIZE] = "";
	char driveroptions[STRING_SIZE] = "";
	int result = 0;
	char commandstring[STRING_SIZE];
	char address[STRING_SIZE], netmask[STRING_SIZE];
	int done;
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
			probecards(driver, driveroptions);
			if (!strlen(driver))
				errorbox(ctr[TR_PROBE_FAILED]);
			else
			{
				//findnicdescription(driver, description);
				sprintf (title, "%s v%s - %s", NAME, VERSION, SLOGAN);
				sprintf(message, ctr[TR_FOUND_NIC], NAME, description);
				newtWinMessage(title, ctr[TR_OK], message);
			}		
		}
		else
			done = 1;	
			
		if (strlen(driver))
			done = 1;
	}
	
	if (!strlen(driver))
		goto EXIT;

	/* Default is a GREEN nic only. */
	/* Smoothie is not untarred yet, so we have to delay actually writing the
	 * settings till later. */
	replacekeyvalue(ethernetkv, "CONFIG_TYPE", "0");
	replacekeyvalue(ethernetkv, "GREEN_DEV", "eth0");
	replacekeyvalue(ethernetkv, "GREEN_DISPLAYDRIVER", driver);
	
	if (!(changeaddress(ethernetkv, "GREEN", 0, "")))
		goto EXIT;
	
	strcpy(address, ""); findkey(ethernetkv, "GREEN_ADDRESS", address);
	strcpy(netmask, ""); findkey(ethernetkv, "GREEN_NETMASK", netmask);

	snprintf(commandstring, STRING_SIZE, "/sbin/ifconfig eth0 %s netmask %s up", 
		address, netmask);
	if (mysystem(commandstring))
	{
		errorbox(ctr[TR_INTERFACE_FAILED_TO_COME_UP]);
		goto EXIT;
	}

	result = 1;
	
EXIT:
	
	return result;
}
