/* SmoothWall setup program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * The big one: networking. 
 * 
 * $Id: networking.c,v 1.5.2.6 2006/02/06 22:00:13 gespinasse Exp $
 * 
 */
 
#include "setup.h"

#define DNS1 0
#define DNS2 1
#define DEFAULT_GATEWAY 2
#define DNSGATEWAY_TOTAL 3

extern FILE *flog;
extern char *mylog;

extern char **ctr;

extern int automode;

#define HAS_ORANGE (configtype == 1 || configtype == 3 || configtype == 5 || configtype == 7)
#define HAS_RED (configtype == 2 || configtype == 3 || configtype == 6 || configtype == 7)
#define HAS_BLUE (configtype == 4 || configtype == 5 || configtype == 6 || configtype == 7)
#define RED_IS_NOT_ETH (configtype == 0 || configtype == 1 || configtype == 4 || configtype == 5)

extern struct nic nics[];

char *configtypenames[] = { 
	"GREEN (RED is modem/ISDN)", 
	"GREEN + ORANGE (RED is modem/ISDN)", 
	"GREEN + RED",
	"GREEN + ORANGE + RED", 
	"GREEN + BLUE (RED is modem/ISDN) ",
	"GREEN + ORANGE + BLUE (RED is modem/ISDN)",
	"GREEN + BLUE + RED",
	"GREEN + ORANGE + BLUE + RED",
	NULL };
int netaddresschange;

int oktoleave(char *errormessage);
int firstmenu(void);
int configtypemenu(void);
int drivermenu(void);
int changedrivers(void);
int greenaddressmenu(void);
int addressesmenu(void);
int dnsgatewaymenu(void);

int handlenetworking(void)
{
	int done;
	int choice;
	char errormessage[STRING_SIZE];
	
	netaddresschange = 0;

	done = 0;
	while (!done)
	{
		choice = firstmenu();
			
		switch (choice)
		{
			case 1:
				configtypemenu();
				break;

			case 2:
				drivermenu();
				break;
							
			case 3:
				addressesmenu();
				break;
			
			case 4:
				dnsgatewaymenu();
				break;
				
			case 0:
				if (oktoleave(errormessage))
					done = 1;
				else
					errorbox(errormessage);
				break;
				
			default:
				break;
		}				
	}

	if (automode == 0)
	{
		/* Restart networking! */	
		if (netaddresschange)
		{
			runcommandwithstatus("/etc/rc.d/rc.netaddress.down",
				ctr[TR_PUSHING_NETWORK_DOWN]);
			runcommandwithstatus("/etc/rc.d/rc.netaddress.up",
				ctr[TR_PULLING_NETWORK_UP]);
			mysystem("/etc/rc.d/rc.pcmcia start");
		}
	}
	
	return 1;
}

int oktoleave(char *errormessage)
{
	struct keyvalue *kv = initkeyvalues();
	char temp[STRING_SIZE];
	int configtype;
	
	if (!(readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings")))
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}	

	strcpy(temp, "0"); findkey(kv, "CONFIG_TYPE", temp); configtype = atol(temp);
	if (configtype < 0 || configtype > 7) configtype = 0;

	if (HAS_BLUE)
	{
		strcpy(temp, ""); findkey(kv, "BLUE_DEV", temp);
		if (!(strlen(temp)))
		{
			strcpy(errormessage, ctr[TR_NO_BLUE_INTERFACE]);
			goto EXIT;
		}
		if (!(interfacecheck(kv, "BLUE")))
		{
			strcpy(errormessage, ctr[TR_MISSING_BLUE_IP]);
			goto EXIT;
		}
	}
	if (HAS_ORANGE)
	{
		strcpy(temp, ""); findkey(kv, "ORANGE_DEV", temp);
		if (!(strlen(temp)))
		{
			strcpy(errormessage, ctr[TR_NO_ORANGE_INTERFACE]);
			goto EXIT;
		}
		if (!(interfacecheck(kv, "ORANGE")))
		{
			strcpy(errormessage, ctr[TR_MISSING_ORANGE_IP]);
			goto EXIT;
		}
	}
	if (HAS_RED)
	{
		strcpy(temp, ""); findkey(kv, "RED_DEV", temp);
		if (!(strlen(temp)))
		{
			strcpy(errormessage, ctr[TR_NO_RED_INTERFACE]);
			goto EXIT;
		}
		if (!(interfacecheck(kv, "RED")))
		{
			strcpy(errormessage, ctr[TR_MISSING_RED_IP]);
			goto EXIT;
		}
	}
	strcpy(errormessage, "");
EXIT:
	freekeyvalues(kv);
	
	if (strlen(errormessage))
		return 0;
	else
		return 1;
}

	
/* Shows the main menu and a summary of the current settings. */
int firstmenu(void)
{
	char *sections[] = { ctr[TR_NETWORK_CONFIGURATION_TYPE],
		ctr[TR_DRIVERS_AND_CARD_ASSIGNMENTS],
		ctr[TR_ADDRESS_SETTINGS],
		ctr[TR_DNS_AND_GATEWAY_SETTINGS], NULL };
	int rc;
	static int choice = 0;
	struct keyvalue *kv = initkeyvalues();
	char message[1000];
	char temp[STRING_SIZE];
	int x;
	int result;
	char networkrestart[STRING_SIZE] = "";
	
	if (!(readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings")))
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}	

	if (netaddresschange) 
		strcpy(networkrestart, ctr[TR_RESTART_REQUIRED]);

	strcpy(temp, ""); findkey(kv, "CONFIG_TYPE", temp); x = atol(temp);
	if (x < 0 || x > 7) x = 0;
	/* Format heading bit. */
	snprintf(message, 1000, ctr[TR_CURRENT_CONFIG], configtypenames[x],
		networkrestart);
	rc = newtWinMenu(ctr[TR_NETWORK_CONFIGURATION_MENU], message, 50, 5, 5, 6,
			sections, &choice, ctr[TR_OK], ctr[TR_DONE], NULL);

	if (rc == 0 || rc == 1)
		result = choice + 1;
	else
		result = 0;

	return result;
}

/* Here they choose general network config, number of nics etc. */
int configtypemenu(void)
{
	struct keyvalue *kv = initkeyvalues();
	char temp[STRING_SIZE] = "0";
	char message[1000];
	int choice;
	int rc;

	if (!(readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings")))
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}
	
	findkey(kv, "CONFIG_TYPE", temp); choice = atol(temp);
	sprintf(message, ctr[TR_NETWORK_CONFIGURATION_TYPE_LONG], NAME);
	rc = newtWinMenu(ctr[TR_NETWORK_CONFIGURATION_TYPE], message, 50, 5, 5,
		6, configtypenames, &choice, ctr[TR_OK], ctr[TR_CANCEL], NULL);

	if (rc == 0 || rc == 1)
	{
		runcommandwithstatus("/etc/rc.d/rc.netaddress.down NOTGREEN",
			ctr[TR_PUSHING_NON_LOCAL_NETWORK_DOWN]);
	
		sprintf(temp, "%d", choice);
		replacekeyvalue(kv, "CONFIG_TYPE", temp);
		replacekeyvalue(kv, "ORANGE_DEV", "");
		replacekeyvalue(kv, "BLUE_DEV", "");
		replacekeyvalue(kv, "RED_DEV", "");
		writekeyvalues(kv, CONFIG_ROOT "/ethernet/settings");
		netaddresschange = 1;
	}
	
	freekeyvalues(kv);
	
	return 0;
}

/* Driver menu.  Choose drivers.. */
int drivermenu(void)
{
	struct keyvalue *kv = initkeyvalues();
	char message[1000];
	char temp[STRING_SIZE], temp1[STRING_SIZE];
	char driver[STRING_SIZE], dev[STRING_SIZE];
	int configtype;
	int rc;

	if (!(readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings")))
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}

	strcpy(temp, "0"); findkey(kv, "CONFIG_TYPE", temp);
	configtype = atol(temp);
	
	if (configtype == 0)
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER]);
		return 0;
	}

	strcpy(message, ctr[TR_CONFIGURE_NETWORK_DRIVERS]);
	
	/* This horrible big formats the heading :( */
	strcpy(driver, ""); findkey(kv, "GREEN_DISPLAYDRIVER", driver);
	findnicdescription(driver, temp);
	strcpy(dev, ctr[TR_UNSET]); findkey(kv, "GREEN_DEV", dev);
	if (!strlen(dev)) strcpy(dev, ctr[TR_UNSET]);
	sprintf(temp1, "GREEN: %s (%s)\n", temp, dev);
	strcat(message, temp1);
	if (HAS_BLUE)
	{
		strcpy(driver, ""); findkey(kv, "BLUE_DISPLAYDRIVER", driver);
		findnicdescription(driver, temp);
		strcpy(dev, ctr[TR_UNSET]); findkey(kv, "BLUE_DEV", dev);
		if (!strlen(dev)) strcpy(dev, ctr[TR_UNSET]);
		sprintf(temp1, "BLUE: %s (%s)\n", temp, dev);
		strcat(message, temp1);
	}
	if (HAS_ORANGE)
	{
		strcpy(driver, ""); findkey(kv, "ORANGE_DISPLAYDRIVER", driver);
		findnicdescription(driver, temp);
		strcpy(dev, ctr[TR_UNSET]); findkey(kv, "ORANGE_DEV", dev);
		if (!strlen(dev)) strcpy(dev, ctr[TR_UNSET]);
		sprintf(temp1, "ORANGE: %s (%s)\n", temp, dev);
		strcat(message, temp1);
	}
	if (HAS_RED)
	{
		strcpy(driver, ""); findkey(kv, "RED_DISPLAYDRIVER", driver);
		findnicdescription(driver, temp);
		strcpy(dev, ctr[TR_UNSET]); findkey(kv, "RED_DEV", dev);
		if (!strlen(dev)) strcpy(dev, ctr[TR_UNSET]);
		sprintf(temp1, "RED: %s (%s)\n", temp, dev);
		strcat(message, temp1);
	}
	strcat(message, ctr[TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS]);
	rc = newtWinChoice(ctr[TR_DRIVERS_AND_CARD_ASSIGNMENTS], ctr[TR_OK],
		ctr[TR_CANCEL], message);
	if (rc == 0 || rc == 1)
	{
		/* Shit, got to do something.. */
		changedrivers();
	}
	
	freekeyvalues(kv);

	return 1;
}

int changedrivers(void)
{
	struct keyvalue *kv = initkeyvalues();
	char message[1000];
	char temp[STRING_SIZE];
	char driver[STRING_SIZE];
	int configtype;
	int rc;
	int c;
	int needcards, sofarallocated, countofcards, toallocate;
	char *orange = "ORANGE";
	char *blue = "BLUE";
	char *red = "RED";
	char *sections[4];
	int choice;
	char nexteth[STRING_SIZE];
	int abort;
	char currentdriver[STRING_SIZE], currentdriveroptions[STRING_SIZE];
	char displaydriver[STRING_SIZE];
	struct stat st;
	
	if (!(readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings")))
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}

	strcpy(temp, "0"); findkey(kv, "CONFIG_TYPE", temp);
	configtype = atol(temp);

	runcommandwithstatus("/etc/rc.d/rc.netaddress.down NOTGREEN",
		ctr[TR_PUSHING_NON_LOCAL_NETWORK_DOWN]);
	
	/* Remove all modules not needed for green networking. */
	c = 0;
	strcpy(driver, ""); findkey(kv, "GREEN_DRIVER", driver);
	if (strcmp(driver, "pcmcia") != 0) {
		stat("/proc/bus/pccard", &st);
		mysystem("/etc/rc.d/rc.pcmcia stop");
		if (S_ISDIR(st.st_mode)) {
			mysystem("/sbin/modprobe pcmcia_core");
			mysystem("/sbin/modprobe pcmcia-controller");
			mysystem("/sbin/modprobe ds");
		}
	}
	while (nics[c].modulename)
	{
		if (strcmp(nics[c].modulename, driver) != 0)
		{
			if (checkformodule(nics[c].modulename))
			{
				sprintf(temp, "/sbin/rmmod %s", nics[c].modulename);
				mysystem(temp);
			}
		}
		c++;
	}
	
	/* Blank them so the rc.netaddress.up does not get confused. */
	replacekeyvalue(kv, "ORANGE_DEV", "");
	replacekeyvalue(kv, "BLUE_DEV", "");
	replacekeyvalue(kv, "RED_DEV", "");
	
	if (configtype == 0)
		needcards = 1;
	else if (configtype == 1 || configtype == 2 || configtype == 4)
		needcards = 2;
	else if (configtype == 7)
		needcards = 4;
	else
		needcards = 3;

	/* This is the green card. */		
	sofarallocated = 1;

	findkey(kv, "GREEN_DRIVER", currentdriver);
	findkey(kv, "GREEN_DRIVER_OPTIONS", currentdriveroptions);
	strcpy(displaydriver, currentdriver);
	
	if (countcards() > 1)
		strcpy(currentdriver, "");
		
	abort = 0;
	/* Keep going till all cards are got, or they give up. */
	while (sofarallocated < needcards && !abort)
	{
		countofcards = countcards();

		/* This is how many cards were added by the last module. */
		toallocate = countofcards - sofarallocated;
		while (toallocate > 0 && sofarallocated < needcards)
		{
			findnicdescription(displaydriver, temp);
			sprintf(message, ctr[TR_UNCLAIMED_DRIVER], temp);
			c = 0; choice = 0;
			strcpy(temp, ""); findkey(kv, "BLUE_DEV", temp);
			if (HAS_BLUE && !strlen(temp))
			{
				sections[c] = blue;
				c++;
			}
			strcpy(temp, ""); findkey(kv, "ORANGE_DEV", temp);
			if (HAS_ORANGE && !strlen(temp))
			{
				sections[c] = orange;
				c++;
			}
			strcpy(temp, ""); findkey(kv, "RED_DEV", temp);			
			if (HAS_RED && !strlen(temp))
			{
				sections[c] = red;
				c++;
			}
			sections[c] = NULL;
			rc = newtWinMenu(ctr[TR_CARD_ASSIGNMENT],
				message, 50, 5,	5, 6, sections, &choice, ctr[TR_OK],
				ctr[TR_CANCEL], NULL);	
			if (rc == 0 || rc == 1)
			{
				/* Now we see which iface needs its settings changed. */
				sprintf(nexteth, "eth%d", sofarallocated);
				if (strcmp(sections[choice], blue) == 0)
				{
					replacekeyvalue(kv, "BLUE_DEV", nexteth);
					replacekeyvalue(kv, "BLUE_DRIVER", currentdriver);
					replacekeyvalue(kv, "BLUE_DRIVER_OPTIONS", currentdriveroptions);
					replacekeyvalue(kv, "BLUE_DISPLAYDRIVER", displaydriver);
					sofarallocated++;
					toallocate--;
					strcpy(currentdriver, "");
					strcpy(currentdriveroptions, "");
				}
				if (strcmp(sections[choice], orange) == 0)
				{
					replacekeyvalue(kv, "ORANGE_DEV", nexteth);
					replacekeyvalue(kv, "ORANGE_DRIVER", currentdriver);
					replacekeyvalue(kv, "ORANGE_DRIVER_OPTIONS", currentdriveroptions);
					replacekeyvalue(kv, "ORANGE_DISPLAYDRIVER", displaydriver);
					sofarallocated++;
					toallocate--;
					strcpy(currentdriver, "");
					strcpy(currentdriveroptions, "");
				}
				if (strcmp(sections[choice], red) == 0)
				{
					replacekeyvalue(kv, "RED_DEV", nexteth);
					replacekeyvalue(kv, "RED_DRIVER", currentdriver);
					replacekeyvalue(kv, "RED_DRIVER_OPTIONS", currentdriveroptions);
					replacekeyvalue(kv, "RED_DISPLAYDRIVER", displaydriver);
					sofarallocated++;
					toallocate--;
					strcpy(currentdriver, "");
					strcpy(currentdriveroptions, "");
				}
			}
			else
			{
				break;
			}
		}
		
		/* Need another module!  The nitty gritty code is in libsmooth. */
		if (sofarallocated < needcards)
		{
			rc = newtWinTernary(ctr[TR_CARD_ASSIGNMENT], ctr[TR_PROBE], 
				ctr[TR_SELECT], ctr[TR_CANCEL], ctr[TR_NO_UNALLOCATED_CARDS]);
				
			if (rc == 0 || rc == 1)
			{
				probecards(currentdriver, currentdriveroptions);
				if (!strlen(currentdriver))
					errorbox(ctr[TR_PROBE_FAILED]);
			}				
			else if (rc == 2)
				choosecards(currentdriver, currentdriveroptions);
			else
				abort = 1;
				
			strcpy(displaydriver, currentdriver);
		}
	}
	
	countofcards = countcards();

	if (countofcards >= needcards)
	{
		newtWinMessage(ctr[TR_CARD_ASSIGNMENT], ctr[TR_OK],
			ctr[TR_ALL_CARDS_SUCCESSFULLY_ALLOCATED]);
	}
	else
		errorbox(ctr[TR_NOT_ENOUGH_CARDS_WERE_ALLOCATED]);
		
	writekeyvalues(kv, CONFIG_ROOT "/ethernet/settings");

	freekeyvalues(kv);

	netaddresschange = 1;
	
	return 1;
}

/* Let user change GREEN address. */
int greenaddressmenu(void)
{
	struct keyvalue *kv = initkeyvalues();
	char message[1000];
	int rc;
	
	if (!(readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings")))
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}

	sprintf(message, ctr[TR_WARNING_LONG], NAME);
	rc = newtWinChoice(ctr[TR_WARNING], ctr[TR_OK], ctr[TR_CANCEL], message);
	
	if (rc == 0 || rc == 1)
	{
		if (changeaddress(kv, "GREEN", 0, ""))
		{
			netaddresschange = 1;
			writekeyvalues(kv, CONFIG_ROOT "/ethernet/settings");			
			writehostsfiles();			
		}
	}
	
	freekeyvalues(kv);

	return 0;
}

/* They can change BLUE, ORANGE and GREEN too :) */
int addressesmenu(void)
{
	struct keyvalue *kv = initkeyvalues();
	struct keyvalue *mainkv = initkeyvalues();
	int rc = 0;
	char *sections[5];
	char *green = "GREEN";
	char *orange = "ORANGE";
	char *blue = "BLUE";
	char *red = "RED";
	int c = 0;
	char greenaddress[STRING_SIZE];
	char oldgreenaddress[STRING_SIZE];
	char temp[STRING_SIZE];
	char temp2[STRING_SIZE];
	char message[1000];
	int configtype;
	int done;
	int choice;
	char hostname[STRING_SIZE];
	
	if (!(readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings")))
	{
		freekeyvalues(kv);
		freekeyvalues(mainkv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}
	if (!(readkeyvalues(mainkv, CONFIG_ROOT "/main/settings")))
	{
		freekeyvalues(kv);
		freekeyvalues(mainkv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}

	strcpy(temp, "0"); findkey(kv, "CONFIG_TYPE", temp);
	configtype = atol(temp);
	
	sections[c] = green;
	c++;
	if (HAS_BLUE)
	{
		sections[c] = blue;
		c++;
	}
	if (HAS_ORANGE)
	{
		sections[c] = orange;
		c++;
	}
	if (HAS_RED)
	{
		sections[c] = red;
		c++;
	}
	sections[c] = NULL;

	choice = 0;	
	done = 0;	
	while (!done)
	{
		rc = newtWinMenu(ctr[TR_ADDRESS_SETTINGS],
			ctr[TR_SELECT_THE_INTERFACE_YOU_WISH_TO_RECONFIGURE], 50, 5,
			5, 6, sections, &choice, ctr[TR_OK], ctr[TR_DONE], NULL);	

		if (rc == 0 || rc == 1)
		{
			if (strcmp(sections[choice], "GREEN") == 0)
			{
				findkey(kv, "GREEN_ADDRESS", oldgreenaddress);
				sprintf(message, ctr[TR_WARNING_LONG], NAME);
				rc = newtWinChoice(ctr[TR_WARNING], ctr[TR_OK], ctr[TR_CANCEL],
					message);
				if (rc == 0 || rc == 1)
				{
					if (changeaddress(kv, "GREEN", 0, ""))
					{
						netaddresschange = 1;
						writekeyvalues(kv, CONFIG_ROOT "/ethernet/settings");
						writehostsfiles();
						findkey(kv, "GREEN_ADDRESS", greenaddress);
						snprintf(temp, STRING_SIZE-1, "option routers %s", oldgreenaddress);
						snprintf(temp2, STRING_SIZE-1, "option routers %s", greenaddress);
						replace (CONFIG_ROOT "/dhcp/dhcpd.conf", temp, temp2);
						chown  (CONFIG_ROOT "/dhcp/dhcpd.conf", 99, 99);
					}
				}
			}
			if (strcmp(sections[choice], "BLUE") == 0)
			{
				if (changeaddress(kv, "BLUE", 0, ""))
					netaddresschange = 1;
			}
			if (strcmp(sections[choice], "ORANGE") == 0)
			{
				if (changeaddress(kv, "ORANGE", 0, ""))
					netaddresschange = 1;
			}
			if (strcmp(sections[choice], "RED") == 0)
			{
				strcpy(hostname, "");
				findkey(mainkv, "HOSTNAME", hostname);
				if (changeaddress(kv, "RED", 1, hostname))
					netaddresschange = 1;
			}
		}
		else
			done = 1;
	}
	
	writekeyvalues(kv, CONFIG_ROOT "/ethernet/settings");
	freekeyvalues(kv);
	freekeyvalues(mainkv);
	
	return 0;
}

/* DNS and default gateway.... */
int dnsgatewaymenu(void)
{
	struct keyvalue *kv = initkeyvalues();
	char message[1000];
	char temp[STRING_SIZE] = "0";
	struct newtWinEntry entries[DNSGATEWAY_TOTAL+1];
	char *values[DNSGATEWAY_TOTAL];         /* pointers for the values. */
	int error;
	int configtype;
	int rc;

	if (!(readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings")))
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}

	strcpy(temp, "0"); findkey(kv, "CONFIG_TYPE", temp);
	configtype = atol(temp);
	
	if (RED_IS_NOT_ETH)
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_DNS_GATEWAY_WITH_GREEN]);
		return 0;
	}

	entries[DNS1].text = ctr[TR_PRIMARY_DNS];
	strcpy(temp, ""); findkey(kv, "DNS1", temp);
	values[DNS1] = strdup(temp);
	entries[DNS1].value = &values[DNS1];
	entries[DNS1].flags = 0;
	
	entries[DNS2].text = ctr[TR_SECONDARY_DNS];
	strcpy(temp, ""); findkey(kv, "DNS2", temp);
	values[DNS2] = strdup(temp);
	entries[DNS2].value = &values[DNS2];
	entries[DNS2].flags = 0;
	
	entries[DEFAULT_GATEWAY].text = ctr[TR_DEFAULT_GATEWAY];
	strcpy(temp, ""); findkey(kv, "DEFAULT_GATEWAY", temp);
	values[DEFAULT_GATEWAY] = strdup(temp);
	entries[DEFAULT_GATEWAY].value = &values[DEFAULT_GATEWAY];
	entries[DEFAULT_GATEWAY].flags = 0;
	
	entries[DNSGATEWAY_TOTAL].text = NULL;
	entries[DNSGATEWAY_TOTAL].value = NULL;
	entries[DNSGATEWAY_TOTAL].flags = 0;
	
	do
	{
		error = 0;
		
		rc = newtWinEntries(ctr[TR_DNS_AND_GATEWAY_SETTINGS], 
			ctr[TR_DNS_AND_GATEWAY_SETTINGS_LONG], 50, 5, 5, 18, entries,
			ctr[TR_OK], ctr[TR_CANCEL], NULL);
		if (rc == 0 || rc == 1)
		{
			strcpy(message, ctr[TR_INVALID_FIELDS]);
			if (strlen(values[DNS1]))
			{
				if (inet_addr(values[DNS1]) == INADDR_NONE)
				{
					strcat(message, ctr[TR_PRIMARY_DNS_CR]);
					error = 1;
				}
			}
			if (strlen(values[DNS2]))
			{
				if (inet_addr(values[DNS2]) == INADDR_NONE)
				{
					strcat(message, ctr[TR_SECONDARY_DNS_CR]);
					error = 1;
				}
			}
			if (strlen(values[DEFAULT_GATEWAY]))
			{
				if (inet_addr(values[DEFAULT_GATEWAY]) == INADDR_NONE)
				{
					strcat(message, ctr[TR_DEFAULT_GATEWAY_CR]);
					error = 1;
				}
			}
			if (!strlen(values[DNS1]) && strlen(values[DNS2]))
			{
				strcpy(message, ctr[TR_SECONDARY_WITHOUT_PRIMARY_DNS]);
				error = 1;
			}

			if (error)
				errorbox(message);
			else
			{
				replacekeyvalue(kv, "DNS1", values[DNS1]);
				replacekeyvalue(kv, "DNS2", values[DNS2]);
				replacekeyvalue(kv, "DEFAULT_GATEWAY", values[DEFAULT_GATEWAY]);
				netaddresschange = 1;
				free(values[DNS1]);
				free(values[DNS2]);
				free(values[DEFAULT_GATEWAY]);
				writekeyvalues(kv, CONFIG_ROOT "/ethernet/settings");
			}
		}
	}
	while (error);
	
	freekeyvalues(kv);
	
	return 1;
}			
