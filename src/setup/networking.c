/* SmoothWall setup program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * The big one: networking. 
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

#define HAS_GREEN 1
#define HAS_RED (configtype == 1 || configtype == 2 || configtype == 3 || configtype == 4)
#define HAS_ORANGE (configtype == 2 || configtype == 4)
#define HAS_BLUE (configtype == 3 || configtype == 4)
#define RED_IS_NOT_ETH (configtype == 0)

extern struct nic nics[];
extern struct knic knics[];

char *configtypenames[] = {
	"GREEN + RED",
	"GREEN + RED + ORANGE",
	"GREEN + RED + BLUE",
	"GREEN + RED + ORANGE + BLUE",
	NULL };
int configtypecards[] = {
	2,	// "GREEN + RED",
	3,	// "GREEN + RED + ORANGE",
	3, 	// "GREEN + RED + BLUE",
	4	  // "GREEN + RED + ORANGE + BLUE",
};


int netaddresschange;

int oktoleave(void);
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
	int found;
	
	netaddresschange = 0;

	found =	scan_network_cards();
	found = init_knics();

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
				if (oktoleave()) done = 1;
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

			rename_nics();

			runcommandwithstatus("/etc/rc.d/init.d/network start",
				ctr[TR_PULLING_NETWORK_UP]);
		}
	} else {
		rename_nics();
	}
	create_udev();
	return 1;
}

int oktoleave(void)
{
	struct keyvalue *kv = initkeyvalues();
	char temp[STRING_SIZE];
	int configtype;
	int rc;
	
	if (!(readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings")))
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}	

	strcpy(temp, "1"); findkey(kv, "CONFIG_TYPE", temp); configtype = atol(temp);
	if (configtype < 1 || configtype > 4) configtype = 1;

	if (HAS_GREEN)
	{
		strcpy(temp, ""); findkey(kv, "GREEN_DEV", temp);
		if (!(strlen(temp)))
		{
			errorbox(ctr[TR_NO_GREEN_INTERFACE]);
			freekeyvalues(kv);
			return 0;
		}
		if (!(interfacecheck(kv, "GREEN")))
		{
			errorbox(ctr[TR_MISSING_GREEN_IP]);
			freekeyvalues(kv);
			return 0;
		}
	}
	if (HAS_RED)
	{

		strcpy(temp, ""); findkey(kv, "RED_DEV", temp);
		if (!(strlen(temp)))
		{
			rc = newtWinChoice(ctr[TR_ERROR], ctr[TR_OK], ctr[TR_IGNORE], ctr[TR_NO_RED_INTERFACE]);
			if (rc == 0 || rc == 1)
			{
				freekeyvalues(kv);
				return 0;
			}
		}
		if (!(interfacecheck(kv, "RED")))
		{
			errorbox(ctr[TR_MISSING_RED_IP]);
			freekeyvalues(kv);
			return 0;
		}
	}
	if (HAS_ORANGE)
	{
		strcpy(temp, ""); findkey(kv, "ORANGE_DEV", temp);
		if (!(strlen(temp)))
		{
			errorbox(ctr[TR_NO_ORANGE_INTERFACE]);
			freekeyvalues(kv);
			return 0;
		}
		if (!(interfacecheck(kv, "ORANGE")))
		{
			errorbox(ctr[TR_MISSING_ORANGE_IP]);
			freekeyvalues(kv);
			return 0;
		}
	}
	if (HAS_BLUE)
	{
		strcpy(temp, ""); findkey(kv, "BLUE_DEV", temp);
		if (!(strlen(temp)))
		{
			errorbox(ctr[TR_NO_BLUE_INTERFACE]);
			freekeyvalues(kv);
			return 0;
		}
		if (!(interfacecheck(kv, "BLUE")))
		{
			errorbox(ctr[TR_MISSING_BLUE_IP]);
			freekeyvalues(kv);
			return 0;
		}
	}
	
	strcpy(temp, ""); findkey(kv, "RED_TYPE", temp);
	if ((configtype == 0) || (strcmp(temp, "STATIC") == 0))
	{
		strcpy(temp, ""); findkey(kv, "DNS1", temp);
		if (!(strlen(temp)))
		{
			errorbox(ctr[TR_MISSING_DNS]);
			freekeyvalues(kv);
			return 0;
		}
		strcpy(temp, ""); findkey(kv, "DEFAULT_GATEWAY", temp);
		if (!(strlen(temp)))
		{
			errorbox(ctr[TR_MISSING_DEFAULT]);
			freekeyvalues(kv);
			return 0;
		}
	}
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
	char temp[STRING_SIZE] = "1";
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

	strcpy(temp, ""); findkey(kv, "CONFIG_TYPE", temp); 
	x = atol(temp);
	x--;
	if (x < 0 || x > 4) x = 0;
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
	char temp[STRING_SIZE] = "1";
	char message[1000];
	int choise, found;
	int rc, configtype;

	if (!(readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings")))
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}

	found = scan_network_cards();
	
	findkey(kv, "CONFIG_TYPE", temp); choise = atol(temp);
	choise--;

		sprintf(message, ctr[TR_NETWORK_CONFIGURATION_TYPE_LONG], NAME);
		rc = newtWinMenu(ctr[TR_NETWORK_CONFIGURATION_TYPE], message, 50, 5, 5,
			6, configtypenames, &choise, ctr[TR_OK], ctr[TR_CANCEL], NULL);
		if ( configtypecards[choise] > found ) {
			sprintf(message, ctr[TR_NOT_ENOUGH_INTERFACES] , configtypecards[choise], found);
			errorbox(message);
		}

	if (rc == 0 || rc == 1)
	{
		choise++;
		sprintf(temp, "%d", choise);
		replacekeyvalue(kv, "CONFIG_TYPE", temp);
		configtype = atol(temp);
		if (!HAS_RED)
			clear_card_entry(_RED_CARD_);
		if (!HAS_ORANGE)
			clear_card_entry(_ORANGE_CARD_);
		if (!HAS_BLUE)
			clear_card_entry(_BLUE_CARD_);

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
	char message[STRING_SIZE];
	char temp[STRING_SIZE] = "1";

	int configtype;
	int i, rc, kcount = 0, neednics;

	if (!(readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings")))
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}

	if (findkey(kv, "CONFIG_TYPE", temp))
		configtype = atol(temp);
	else {
		fprintf(flog,"setting CONFIG_TYPE = %s\n",temp);
		configtype = atol(temp);
		replacekeyvalue(kv, "CONFIG_TYPE", temp);
		writekeyvalues(kv, CONFIG_ROOT "/ethernet/settings");
	}

	strcpy(message, ctr[TR_CONFIGURE_NETWORK_DRIVERS]);

	kcount = 0;
	neednics = 0;
	if (HAS_GREEN) {
		sprintf(temp, "GREEN:  %s\n", knics[_GREEN_CARD_].description);
		strcat(message, temp);
		if (strlen(knics[_GREEN_CARD_].macaddr) ) {
			sprintf(temp, "GREEN:  (%s) %s green0\n", knics[_GREEN_CARD_].macaddr, ctr[TR_AS]);
			strcat(message, temp);
		}
		neednics++;
	}
	if (HAS_RED) {
		sprintf(temp, "RED:    %s\n", knics[_RED_CARD_].description);
		strcat(message, temp);
		if (strlen(knics[_RED_CARD_].macaddr) ) {
			sprintf(temp, "RED:    (%s) %s red0\n", knics[_RED_CARD_].macaddr, ctr[TR_AS]);
			strcat(message, temp);
		}
		neednics++;
	}
	if (HAS_ORANGE) {
		sprintf(temp, "ORANGE: %s\n", knics[_ORANGE_CARD_].description);
		strcat(message, temp);
		if ( strlen(knics[_ORANGE_CARD_].macaddr) ) {
			sprintf(temp, "ORANGE: (%s) %s orange0\n", knics[_ORANGE_CARD_].macaddr, ctr[TR_AS]);
			strcat(message, temp);
		}
		neednics++;
	}
	if (HAS_BLUE) {
		sprintf(temp, "BLUE:   %s\n", knics[_BLUE_CARD_].description);
		strcat(message, temp);
		if (strlen(knics[_BLUE_CARD_].macaddr)) {
			sprintf(temp, "BLUE:   (%s) %s blue0\n", knics[_BLUE_CARD_].macaddr, ctr[TR_AS]);
			strcat(message, temp);
		}
		neednics++;
	}

	for ( i=0 ; i<4; i++)
		if (strcmp(knics[i].macaddr, ""))
			kcount++;

	if (neednics = kcount)
	{
		strcat(message, ctr[TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS]);
		rc = newtWinChoice(ctr[TR_DRIVERS_AND_CARD_ASSIGNMENTS], ctr[TR_OK],
		ctr[TR_CANCEL], message);
		if (rc == 0 || rc == 1)
		{
			changedrivers();
		}
	} else {
		changedrivers();
	}
	freekeyvalues(kv);

	return 1;
}

int set_menu_entry_for(int *nr, int *card)
{

}

int changedrivers(void)
{
	struct keyvalue *kv = initkeyvalues();
	char temp[STRING_SIZE], message[STRING_SIZE];
	int configtype;
	int green = 0, red = 0, blue = 0, orange = 0;
	char MenuInhalt[10][180];
	char *pMenuInhalt[10];
	int count = 0, choise = 0, rc;
	int NicEntry[10];

	if (!(readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings")))
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}
	if (automode == 0)
		runcommandwithstatus("/etc/rc.d/init.d/network stop red blue orange",
			ctr[TR_PUSHING_NON_LOCAL_NETWORK_DOWN]);

	findkey(kv, "CONFIG_TYPE", temp); configtype = atol(temp);
	if (configtype == 1)
		{ green = 1; red = 1; }
	else if (configtype == 2)
		{ green = 1; red = 1; orange = 1; }
	else if (configtype == 3)
		{ green = 1; red = 1; blue = 1; }
	else if (configtype == 4)
		{ green = 1; red=1; orange=1; blue = 1; }
	else if (configtype == "")
	  { green = 1; red = 1; }

	do
	{
		count = 0;
		strcpy(message, ctr[TR_INTERFACE_CHANGE]);

		if (green) {
			strcpy(MenuInhalt[count], "GREEN");
			pMenuInhalt[count] = MenuInhalt[count];
			NicEntry[_GREEN_CARD_] = count;
			sprintf(temp, "GREEN:  %s\n", knics[_GREEN_CARD_].description);
			strcat(message, temp);
			if ( strlen(knics[_GREEN_CARD_].macaddr) ) {
				sprintf(temp, "GREEN:  (%s) %s green0\n", knics[_GREEN_CARD_].macaddr, ctr[TR_AS]);
				strcat(message, temp);
			}
			count++;
		}

		if (red) {
			strcpy(MenuInhalt[count], "RED");
			pMenuInhalt[count] = MenuInhalt[count];
			NicEntry[_RED_CARD_] = count;
			sprintf(temp, "RED:    %s\n", knics[_RED_CARD_].description);
			strcat(message, temp);
			if ( strlen(knics[_RED_CARD_].macaddr) ) {
				sprintf(temp, "RED:    (%s) %s red0\n", knics[_RED_CARD_].macaddr, ctr[TR_AS]);
				strcat(message, temp);
			}
			count++;
		}

		if (orange) {
			strcpy(MenuInhalt[count], "ORANGE");
			pMenuInhalt[count] = MenuInhalt[count];
			NicEntry[_ORANGE_CARD_] = count;
			sprintf(temp, "ORANGE: %s\n", knics[_ORANGE_CARD_].description);
			strcat(message, temp);
			if ( strlen(knics[_ORANGE_CARD_].macaddr) ) {
				sprintf(temp, "ORANGE: (%s) %s orange0\n", knics[_ORANGE_CARD_].macaddr, ctr[TR_AS]);
				strcat(message, temp);
			}
			count++;
		}

		if (blue) {
			strcpy(MenuInhalt[count], "BLUE");
			pMenuInhalt[count] = MenuInhalt[count];
			NicEntry[_BLUE_CARD_] = count;
			sprintf(temp, "BLUE:   %s\n", knics[_BLUE_CARD_].description);
			strcat(message, temp);
			if ( strlen(knics[_BLUE_CARD_].macaddr) ) {
				sprintf(temp, "BLUE:   (%s) %s blue0\n", knics[_BLUE_CARD_].macaddr, ctr[TR_AS]);
				strcat(message, temp);
			}
			count++;
		}
		pMenuInhalt[count] = NULL;

		rc = newtWinMenu( ctr[TR_NETCARD_COLOR], message, 70, 5, 5, 6, pMenuInhalt, &choise, ctr[TR_SELECT], ctr[TR_REMOVE], ctr[TR_DONE], NULL);
			
		if ( rc == 0 || rc == 1) {
			if ((green) && ( choise == NicEntry[0])) nicmenu(_GREEN_CARD_);
			if ((red) && ( choise == NicEntry[1])) nicmenu(_RED_CARD_);
			if ((orange) && ( choise == NicEntry[2])) nicmenu(_ORANGE_CARD_);
			if ((blue) && ( choise == NicEntry[3])) nicmenu(_BLUE_CARD_);
			netaddresschange = 1;
		} else if (rc == 2) {
			if ((green) && ( choise == NicEntry[0])) ask_clear_card_entry(_GREEN_CARD_);
			if ((red) && ( choise == NicEntry[1])) ask_clear_card_entry(_RED_CARD_);
			if ((orange) && ( choise == NicEntry[2])) ask_clear_card_entry(_ORANGE_CARD_);
			if ((blue) && ( choise == NicEntry[3])) ask_clear_card_entry(_BLUE_CARD_);
			netaddresschange = 1;
		}
	}
	while ( rc <= 2);

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
