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
			runcommandwithstatus("/etc/rc.d/init.d/network stop",
				ctr[TR_PUSHING_NETWORK_DOWN]);
			runcommandwithstatus("/etc/rc.d/init.d/network start",
				ctr[TR_PULLING_NETWORK_UP]);
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
		runcommandwithstatus("/etc/rc.d/init.d/network stop red blue orange",
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
	FILE *fp;
	struct keyvalue *kv = initkeyvalues();
	char message[1000], macaddr[STRING_SIZE];
	char temp_line[STRING_SIZE];
	char temp[STRING_SIZE], temp1[STRING_SIZE];
	struct knic knics[20], *pknics;
	pknics = knics;
	int configtype;
	int rc, i = 0, kcount = 0;

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
	
	if( (fp = fopen(KNOWN_NICS, "r")) == NULL )
	{
		fprintf(flog,"Couldn't open " KNOWN_NICS);
		return 1;
	}
	while (fgets(temp_line, STRING_SIZE, fp) != NULL)
	{
		strcpy(knics[kcount].description, strtok(temp_line,";"));
		strcpy(knics[kcount].macaddr , strtok(NULL,";"));
		if (strlen(knics[kcount].macaddr) > 5 ) kcount++;
	}
	fclose(fp);
	
	strcpy(macaddr, ctr[TR_UNSET]);
	findkey(kv, "GREEN_MACADDR", macaddr);
	for (i=0; i < kcount; i++)
	{	// Check if the nic is already in use
		if (strcmp(pknics[i].macaddr, macaddr) == NULL )
			break;
	}
	sprintf(temp1, "GREEN: %s (%s / green0)\n", pknics[i].description, pknics[i].macaddr);
	strcat(message, temp1);
	
	if (HAS_BLUE) {
		strcpy(macaddr, ctr[TR_UNSET]);
		findkey(kv, "BLUE_MACADDR", macaddr);
		for (i=0; i < kcount; i++)
		{	// Check if the nic is already in use
			if (strcmp(pknics[i].macaddr, macaddr) == NULL )
				break;
		}
		sprintf(temp1, "BLUE: %s (%s / blue0)\n", pknics[i].description, pknics[i].macaddr);
		strcat(message, temp1);
	}
	if (HAS_ORANGE) {
		strcpy(macaddr, ctr[TR_UNSET]);
		findkey(kv, "ORANGE_MACADDR", macaddr);
		for (i=0; i < kcount; i++)
		{	// Check if the nic is already in use
			if (strcmp(pknics[i].macaddr, macaddr) == NULL )
				break;
		}
		sprintf(temp1, "ORANGE: %s (%s / orange0)\n", pknics[i].description, pknics[i].macaddr);
		strcat(message, temp1);
	}
	if (HAS_RED) {
		strcpy(macaddr, ctr[TR_UNSET]);
		findkey(kv, "RED_MACADDR", macaddr);
		for (i=0; i < kcount; i++)
		{	// Check if the nic is already in use
			if (strcmp(pknics[i].macaddr, macaddr) == NULL )
				break;
		}
		sprintf(temp1, "RED: %s (%s / red0)\n", pknics[i].description, pknics[i].macaddr);
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

int cardassigned(char *colour)
{
	char command[STRING_SIZE];
	sprintf(command, "grep -q %s < /etc/udev/rules.d/30-persistent-network.rules 2>/dev/null", colour);
	if (system(command))
		return 0;
	else
		return 1;
}

int changedrivers(void)
{
	struct keyvalue *kv = initkeyvalues();
	char temp[STRING_SIZE];
	int configtype;
	int green = 0, red = 0, blue = 0, orange = 0;
	
	if (!(readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings")))
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}
	
	strcpy(temp, "0"); findkey(kv, "CONFIG_TYPE", temp);
	configtype = atol(temp);
	
	runcommandwithstatus("/etc/rc.d/init.d/network stop red blue orange",
		ctr[TR_PUSHING_NON_LOCAL_NETWORK_DOWN]);
		
	if (configtype == 0)
		{ green = 1; }
	else if (configtype == 1)
		{ green = 1; orange = 1; }
	else if (configtype == 2)
		{ green = 1; red = 1; }
	else if (configtype == 3)
		{ green = 1; red = 1; orange = 1; }
	else if (configtype == 4)
		{ green = 1; blue = 1; }
	else if (configtype == 5)
		{ green = 1; blue = 1; orange = 1; }
	else if (configtype == 6)
		{ green = 1; red = 1; blue = 1; }
	else if (configtype == 7)
		{ green = 1; red = 1; blue = 1; orange = 1;}
	
	if (green && !cardassigned("green"))
		nicmenu("green");
	if (red && !cardassigned("red"))
		nicmenu("red");
	if (blue && !cardassigned("blue"))
		nicmenu("blue");
	if (orange && !cardassigned("orange"))
		nicmenu("orange");
	
	// writekeyvalues(kv, CONFIG_ROOT "/ethernet/settings");

	freekeyvalues(kv);
	return 1;
}

// Let user change GREEN address.
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

// They can change BLUE, ORANGE and GREEN too :)
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
