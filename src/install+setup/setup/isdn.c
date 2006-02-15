/* SmoothWall setup program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * ISDN probing.
 * 
 * $Id: isdn.c,v 1.6.2.1 2004/04/14 22:05:41 gespinasse Exp $
 * 
 */
 
#include "setup.h"
 
extern FILE *flog;
extern char *mylog;

extern char **ctr;

extern int automode;

struct card
{
	char *name;
	int type;
};

struct card cards[] = {
	{ "", 0 },
	{ "Teles 16.0", 1 },
	{ "Teles 8.0", 2 },
	{ "Teles 16.3 (non PnP)", 3 },
	{ "Teles 16.3c", 14 },	
	{ "Teles PCI", 21 },	
	{ "Creatix/Teles PnP", 4 },
	{ "AVM A1 (Fritz)", 5 },
	{ "AVM ISA/PCI", 27 },	
	{ "AVM PCI/PNP (EXPERIMENTAL driver)", 999 },
	{ "ELSA PCC/PCF cards", 6 },
	{ "ELSA Quickstep 1000", 7 },
	{ "ELSA Quickstep 1000PCI", 18 },
	{ "Eicon Diva ISA Pnp and PCI", 11 },
	{ "ASUS COM ISDNLink", 12 },
	{ "HFC-2BS0 based cards", 13 },
	{ "HFC 2BDS0 PCI", 35 },	
	{ "Sedlbauer cards", 15 },
	{ "USR Sportster internal", 16 },
	{ "MIC Card", 17 },
	{ "Compaq ISDN S00 ISA", 19 },
	{ "NETjet PCI card", 20 },
	{ "Dr. Neuhauss Niccy ISA/PCI", 24 },
	{ "Teles S0Box", 25 },
	{ "Sedlbauer Speed Fax+", 28 },
	{ "Siemens I-Surf 1.0", 29 },
	{ "ACER P10", 30 },
	{ "HST Saphir", 31 },
	{ "Telekom A4T", 32 },
	{ "Scitel Quadro", 33 },
	{ "Gazel ISA/PCI", 34 },
	{ "W6692 based PCI cards", 36 },
	{ "ITK ix1-micro Rev.2", 9 },	
	{ "NETspider U PCI card", 38 },
	{ "USB ST5481", 998 },
	{ NULL, 0 }
};

void handleisdnprotocol(char **protocolnames);
int isdnenabledpressed(void);
int isdndisabledpressed(void);
void handleisdncard(void);
void handlemoduleparams(void);
int probeisdncard(void);
int probeusbisdncard(char *s);
void handleisdnmsn(void);

int handleisdn(void)
{
	char *protocolnames[] = { ctr[TR_GERMAN_1TR6], ctr[TR_EURO_EDSS1],
		ctr[TR_LEASED_LINE], ctr[TR_US_NI1], NULL };
	struct keyvalue *kv;
	int rc;
	char protocolname[STRING_SIZE] = "";
	char cardname[STRING_SIZE] = "";
	char msn[STRING_SIZE] = "";
	char temps[STRING_SIZE];
	int tempd;
	char message[1000];
	int c;
	char *sections[] = { ctr[TR_PROTOCOL_COUNTRY],
		ctr[TR_SET_ADDITIONAL_MODULE_PARAMETERS], ctr[TR_ISDN_CARD],
		 ctr[TR_MSN_CONFIGURATION], NULL };
	int choice;
	char enableddisabled[STRING_SIZE];
	FILE *f;
	
	if ((f = fopen(CONFIG_ROOT "/red/active", "r")))
	{
		fclose(f);
		errorbox(ctr[TR_RED_IN_USE]);
		return 1;
	}
	
	/* rc.isdn is a small script to bring down ippp0 and kill ipppd
	 * and removes the ISDN modules. */
	mysystem("/etc/rc.d/rc.isdn stop");

	choice = 0;	
	for (;;)
	{
		kv = initkeyvalues();
		if (!(readkeyvalues(kv, CONFIG_ROOT "/isdn/settings")))
		{
			freekeyvalues(kv);
			errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
			return 0;
		}

		strcpy(enableddisabled, ctr[TR_DISABLED]);
		findkey(kv, "ENABLED", temps);
		if (strcmp(temps, "on") == 0)
			strcpy(enableddisabled, ctr[TR_ENABLED]);
		
		strcpy(temps, "-1");
		findkey(kv, "PROTOCOL", temps);
		tempd = atol(temps);
		if (tempd < 1 || tempd > 4)
			strcpy(protocolname, ctr[TR_UNSET]);
		else
			strcpy(protocolname, protocolnames[tempd - 1]);
				
		strcpy(temps, "-1");
		findkey(kv, "TYPE", temps);
		tempd = atol(temps);
		c = 0;
		while (cards[c].name)
		{
			if (cards[c].type == tempd)
			{
				strcpy(cardname, cards[c].name);
				break;
			}
			c++;
		}
		if (!strlen(cardname))
			strcpy(cardname, ctr[TR_UNSET]);		

		strcpy(temps, "");		
		findkey(kv, "MSN", temps);
		if (strlen(temps))
			strcpy(msn, temps);
		else
			strcpy(msn, ctr[TR_UNSET]);
		sprintf(message, ctr[TR_ISDN_STATUS], enableddisabled, protocolname,
			cardname, msn);
		
		freekeyvalues(kv);
		
		rc = newtWinMenu(ctr[TR_ISDN_CONFIGURATION_MENU], message, 50, 5, 5, 6,
			sections, &choice, ctr[TR_OK], ctr[TR_ENABLE_ISDN],
			ctr[TR_DISABLE_ISDN], NULL);
		
		if (rc == 1 || rc == 0)
		{
			switch (choice)
			{
				case 0:
					handleisdnprotocol(protocolnames);
					break;
					
				case 1:
					handlemoduleparams();
					break;
							
				case 2:
					handleisdncard();
					break;
		
				case 3:
					handleisdnmsn();
					break;
				
				default:
					break;
			}
		}

		else if (rc == 2)
		{
			if (!isdnenabledpressed())
				break;
		}
		else
		{
			if (!(isdndisabledpressed()))
				break;
		}	
	}
	
	return 1;
}

/* Returns 0 if main ISDN setup loop should exit. */
int isdndisabledpressed(void)
{
	struct keyvalue *kv = initkeyvalues();

	if (!(readkeyvalues(kv, CONFIG_ROOT "/isdn/settings")))
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}

	replacekeyvalue(kv, "ENABLED", "off");
	writekeyvalues(kv, CONFIG_ROOT "/isdn/settings");

	freekeyvalues(kv);
	
	return 0;
}

/* Returns 0 if main ISDN setup loop should exit. */
int isdnenabledpressed(void)
{
	struct keyvalue *kv = initkeyvalues();
	char protocol[STRING_SIZE] = "";
	char type[STRING_SIZE] = "";
	char msn[STRING_SIZE] = "";
	char moduleparams[STRING_SIZE] = "";
	char commandstring[STRING_SIZE];
	int result = 0;

	if (!(readkeyvalues(kv, CONFIG_ROOT "/isdn/settings")))
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}

	findkey(kv, "PROTOCOL", protocol);
	findkey(kv, "TYPE", type);
	findkey(kv, "MSN", msn);
	findkey(kv, "MODULE_PARAMS", moduleparams);
				
	if (strlen(protocol) && strlen(type) && strlen(msn))
	{
		if (atol(type) == 998)
		{
                        sprintf(commandstring, "/sbin/modprobe hisax_st5481 protocol=%s %s",
			        protocol, moduleparams);
		}
		else if (atol(type) == 999)
                {
                        sprintf(commandstring, "/sbin/modprobe hisax_fcpcipnp protocol=%s %s",
			        protocol, moduleparams);
		}
                else
                {
                        sprintf(commandstring, "/sbin/modprobe hisax protocol=%s type=%s %s",
			        protocol, type, moduleparams);
		}
                if (runcommandwithstatus(commandstring, ctr[TR_INITIALISING_ISDN]) != 0)
		{
			errorbox(ctr[TR_UNABLE_TO_INITIALISE_ISDN]);
			replacekeyvalue(kv, "ENABLED", "off");
			result = 1;
		}
		else
			replacekeyvalue(kv, "ENABLED", "on");
	}
	else
	{
		errorbox(ctr[TR_ISDN_NOT_SETUP]);
		replacekeyvalue(kv, "ENABLED", "off");
		result = 1;
	}
	writekeyvalues(kv, CONFIG_ROOT "/isdn/settings");

	freekeyvalues(kv);
	
	return result;
}

void handleisdnprotocol(char **protocolnames)
{
	int rc;
	int choice;
	struct keyvalue *kv = initkeyvalues();
	char temp[STRING_SIZE] = "1";

	if (!(readkeyvalues(kv, CONFIG_ROOT "/isdn/settings")))
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return;
	}
	findkey(kv, "PROTOCOL", temp);
	choice = atol(temp) - 1;
	
	rc = newtWinMenu(ctr[TR_ISDN_PROTOCOL_SELECTION], ctr[TR_CHOOSE_THE_ISDN_PROTOCOL],
		50, 5, 5, 6, protocolnames, &choice, ctr[TR_OK], ctr[TR_CANCEL], NULL);
		
	if (rc == 2)
		return;

	sprintf(temp, "%d", choice + 1);
	replacekeyvalue(kv, "PROTOCOL", temp);
	writekeyvalues(kv, CONFIG_ROOT "/isdn/settings");
	freekeyvalues(kv);
}
		
void handlemoduleparams(void)
{
	struct keyvalue *kv = initkeyvalues();
	char moduleparams[STRING_SIZE] = "";
	char *values[] = { moduleparams, NULL };	/* pointers for the values. */
	struct newtWinEntry entries[] =
		{ { "", &values[0], 0,}, { NULL, NULL, 0 } };
	char title[STRING_SIZE];
	int rc;

	if (!(readkeyvalues(kv, CONFIG_ROOT "/isdn/settings")))
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return;
	}

	findkey(kv, "MODULE_PARAMS", moduleparams);

	for (;;)
	{	
		sprintf (title, "%s v%s - %s", NAME, VERSION, SLOGAN);
		rc = newtWinEntries(title, ctr[TR_ENTER_ADDITIONAL_MODULE_PARAMS],
			50, 5, 5, 40, entries, ctr[TR_OK], ctr[TR_CANCEL], NULL);	
		
		if (rc == 1)
		{
			replacekeyvalue(kv, "MODULE_PARAMS", values[0]);
			writekeyvalues(kv, CONFIG_ROOT "/isdn/settings");
			free(values[0]);
			break;
		}
		else
			break;
	}
	freekeyvalues(kv);
}

void handleisdncard(void)
{
	char **selection;
	int c;
	int rc;
	int choice;
	int type;
	struct keyvalue *kv = initkeyvalues();
	char temp[STRING_SIZE] = "0";
	int card;
	char message[STRING_SIZE];
	char commandstring[STRING_SIZE];
	char moduleparams[STRING_SIZE] = "";
	int done = 0;
	
	if (!(readkeyvalues(kv, CONFIG_ROOT "/isdn/settings")))
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return;
	}
	
	findkey(kv, "TYPE", temp);
	type = atol(temp);
	findkey(kv, "MODULE_PARAMS", moduleparams);
	
	/* Count cards. */
	c = 0;
	while (cards[c].name) c++;
	selection = malloc((c + 1) * sizeof(char *));
	
	/* Fill out section. */
	c = 0;
	selection[c] = ctr[TR_AUTODETECT];
	c++;
	while (cards[c].name)
	{
		selection[c] = cards[c].name;
		c++;
	}
	selection[c] = NULL;
	
	/* Determine inital value for choice. */
	c = 0; choice = 0;
	while (cards[c].name)
	{
		if (cards[c].type == type)
		{
			choice = c;
			break;
		}
		c++;
	}
	
	while (!done)
	{
		rc = newtWinMenu(ctr[TR_ISDN_CARD_SELECTION], ctr[TR_CHOOSE_THE_ISDN_CARD_INSTALLED],
			50, 5, 5, 10, selection, &choice, ctr[TR_OK], ctr[TR_CANCEL], NULL);
	
		if (rc == 2)
			done = 1;
		else
		{	
			if (choice == 0)
				card = probeisdncard();
			else
			{
				sprintf(message, ctr[TR_CHECKING_FOR], cards[choice].name);
				if (cards[choice].type == 998)
				{
                                        sprintf(commandstring, "/sbin/modprobe hisax_st5481 protocol=1 %s",
					        moduleparams);
				}
				else if (cards[choice].type == 999)
                              	{
                                        sprintf(commandstring, "/sbin/modprobe hisax_fcpcipnp protocol=1 %s",
					        moduleparams);
				}
                                else
				{
                                        sprintf(commandstring, "/sbin/modprobe hisax type=%d protocol=1 %s",
					        cards[choice].type, moduleparams);
                                }
                                if (runcommandwithstatus(commandstring, message) == 0)
					card = cards[choice].type;
				else
				{
					errorbox(ctr[TR_ISDN_CARD_NOT_DETECTED]);
					card = -1;
				}
				mysystem("/etc/rc.d/rc.isdn stop");
			}

			if (card != -1)
			{
				sprintf(temp, "%d", card);
				replacekeyvalue(kv, "TYPE", temp);
				writekeyvalues(kv, CONFIG_ROOT "/isdn/settings");
				done = 1;
			}
		}
	}

	free(selection);	
	freekeyvalues(kv);
}

int probeusbisdncard(char *s)
{
	FILE *file;
	char buf[STRING_SIZE]; 
	int found = 0;

	if (!(file = fopen("/proc/bus/usb/devices", "r")))
	{
		fprintf(flog, "Unable to open /proc/bus/usb/devices in probeusbisdncard()\n");
		return 0;
	}

	while (fgets(buf, STRING_SIZE, file)) {
		if (strstr(buf, s)) {
			found = 1;
		}
	}

	fclose(file);

	return found;
}

int probeisdncard(void)
{
	int c;
	char message[STRING_SIZE];
	char commandstring[STRING_SIZE];
	char moduleparams[STRING_SIZE] = "";
	struct keyvalue *kv = initkeyvalues();
	char title[STRING_SIZE];
	int result = -1;
	
	if (!(readkeyvalues(kv, CONFIG_ROOT "/isdn/settings")))
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return  -1;
	}
	findkey(kv, "MODULE_PARAMS", moduleparams);
		
	c = 1;
	while (cards[c].name)
	{
		sprintf(message, ctr[TR_CHECKING_FOR], cards[c].name);
		if (cards[c].type == 998)
		{
			/* Try to find if it exists, but should generalize
			 * probeusbisdncard to pass Vendor and ProdID
			 * independently, rather than a string
			 */
			if (probeusbisdncard("Vendor=0483 ProdID=481"))
                        	sprintf(commandstring, "/sbin/modprobe hisax_st5481 protocol=1 %s", moduleparams);
		}
		else if (cards[c].type == 999)
		{
                        sprintf(commandstring, "/sbin/modprobe hisax_fcpcipnp protocol=1 %s", 
			        moduleparams);
		}
                else
		{
                        sprintf(commandstring, "/sbin/modprobe hisax type=%d protocol=1 %s", 
			        cards[c].type, moduleparams);
		}
		if (runcommandwithstatus(commandstring, message) == 0)
		{
			mysystem("/etc/rc.d/rc.isdn stop");
			sprintf (title, "%s v%s - %s", NAME, VERSION, SLOGAN);
			sprintf(message, ctr[TR_DETECTED], cards[c].name);
			newtWinMessage(title, ctr[TR_OK], message);
			result = cards[c].type;
			goto EXIT;
		}
		c++;
	}

	errorbox(ctr[TR_UNABLE_TO_FIND_AN_ISDN_CARD]);
	
EXIT:
	freekeyvalues(kv);
	
	return result;
}

void handleisdnmsn(void)
{
	struct keyvalue *kv = initkeyvalues();
	char msn[STRING_SIZE] = "";
	char *values[] = { msn, NULL };	/* pointers for the values. */
	struct newtWinEntry entries[] =
		{ { "", &values[0], 0,}, { NULL, NULL, 0 } };
	char title[STRING_SIZE];
	int rc;

	if (!(readkeyvalues(kv, CONFIG_ROOT "/isdn/settings")))
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return;
	}
	findkey(kv, "MSN", msn);

	for (;;)
	{	
		sprintf (title, "%s v%s - %s", NAME, VERSION, SLOGAN);
		rc = newtWinEntries(title, ctr[TR_ENTER_THE_LOCAL_MSN],
			50, 5, 5, 40, entries, ctr[TR_OK], ctr[TR_CANCEL], NULL);	
		
		if (rc == 1)
		{
			if (!(strlen(values[0])))
				errorbox(ctr[TR_PHONENUMBER_CANNOT_BE_EMPTY]);
			else
			{			
				replacekeyvalue(kv, "MSN", values[0]);
				writekeyvalues(kv, CONFIG_ROOT "/isdn/settings");
				free(values[0]);
				break;
			}
		}
		else
			break;
	}
	freekeyvalues(kv);
}
