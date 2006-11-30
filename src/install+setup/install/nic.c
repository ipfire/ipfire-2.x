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
	int i;
	int count;
	char nics;
	char number;
	char cbValue;
	char driver[STRING_SIZE] = "";
	char driveroptions[STRING_SIZE] = "";
	struct keyvalue *kv = initkeyvalues();
	int result = 0;
	char commandstring[STRING_SIZE];
	char address[STRING_SIZE], netmask[STRING_SIZE];
	FILE *handle;
	char description[1000];
	char message[1000];
	char title[STRING_SIZE];

	/* Detect and count nics */
	count = mysystem("/bin/probenic.sh count");
	fprintf(flog, "Number of detected nics: %s\n", count);

/*	sprintf(commandstring, "/bin/probenic.sh");
	sprintf(message, ctr[TR_PROBING_FOR_NICS]);
	runcommandwithstatus(commandstring, message); */

/*	handle = fopen("/nicdriver", "r");
	fgets(nics, STRING_SIZE, handle);
	fclose(handle); */

/*	fprintf(flog, "Detected NIC drivers: %s\n",driver); */

/*	sprintf (title, "%s %s - %s", NAME, VERSION, SLOGAN);
	sprintf(message, ctr[TR_FOUND_NIC], NAME, description);
	newtWinMessage(title, ctr[TR_OK], message); */

	newtComponent form, checkbox, rb[count], button;
	newtOpenWindow(10, 5, 60, 11, "Checkboxes and Radio buttons");

	for (i = 1; i <= 2; i++)
	{
		fprintf(flog, "Scan: %d\n", i);
		snprintf(commandstring, STRING_SIZE, "/bin/probenic.sh %i", i);
		mysystem(commandstring);
		if ((handle = fopen("/nicdriver", "r")) == NULL) {
			errorbox(ctr[TR_ERROR]);
			goto EXIT;
		}
		fgets(driver, STRING_SIZE, handle);
		fclose(handle);
		findnicdescription(driver, description);
		if ( i == 0 )
			rb[i] = newtRadiobutton(1, i+2, description, 1, NULL);
		else
			rb[i] = newtRadiobutton(1, i+2, description, 0, rb[i-1]);
 	}
 
	button = newtButton(1, count+3, "OK");

	form = newtForm(NULL, NULL, 0);
	newtFormAddComponent(form, checkbox);
	for (i = 1; i <= 2; i++) {
		fprintf(flog, "Add: %d\n", i);
		newtFormAddComponent(form, rb[i]);
	}
	newtFormAddComponent(form, button);

	newtRunForm(form);
	newtFinished();

	for (i = 1; i <= 2; i++)
		if (newtRadioGetCurrent(rb[0]) == rb[i])
			printf("radio button picked: %d\n", i);
	newtFormDestroy(form);


/*	snprintf(commandstring, STRING_SIZE, "/bin/probenic.sh 1");
	mysystem(commandstring);	
	if ((handle = fopen("/nicdriver", "r")) == NULL) {
		errorbox(ctr[TR_ERROR]);
		goto EXIT;
	}
	fgets(driver, STRING_SIZE, handle);
	fprintf(flog, "Green nic driver: %s\n", driver);
	fclose(handle); */

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

