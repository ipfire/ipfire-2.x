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

#define HAS_GREEN 1
#define HAS_RED (configtype == 1 || configtype == 2 || configtype == 3 || configtype == 4)
#define HAS_ORANGE (configtype == 2 || configtype == 4)
#define HAS_BLUE (configtype == 3 || configtype == 4)
#define RED_IS_NOT_ETH (configtype == 0)

//#define HAS_ORANGE (configtype == 1 || configtype == 3 || configtype == 5 || configtype == 7)
//#define HAS_RED (configtype == 2 || configtype == 3 || configtype == 6 || configtype == 7)
//#define HAS_BLUE (configtype == 4 || configtype == 5 || configtype == 6 || configtype == 7)
//#define RED_IS_NOT_ETH (configtype == 0 || configtype == 1 || configtype == 4 || configtype == 5)

extern struct nic nics[];
extern struct knic knics[];

/* char *configtypenames[] = { 
	"GREEN (RED is modem/ISDN)", 
	"GREEN + ORANGE (RED is modem/ISDN)", 
	"GREEN + RED",
	"GREEN + ORANGE + RED", 
	"GREEN + BLUE (RED is modem/ISDN) ",
	"GREEN + ORANGE + BLUE (RED is modem/ISDN)",
	"GREEN + BLUE + RED",
	"GREEN + ORANGE + BLUE + RED",
	NULL };
*/
char *configtypenames[] = { 
	"GREEN",
	"GREEN + RED",
	"GREEN + RED + ORANGE",
	"GREEN + RED + BLUE",
	"GREEN + RED + ORANGE + BLUE",
	NULL };
int configtypecards[] = {
	1,	// "GREEN",
	2,	// "GREEN + RED",
	3,	// "GREEN + RED + ORANGE",
	3, 	// "GREEN + RED + BLUE",
	4	// "GREEN + RED + ORANGE + BLUE",
};


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
	int found;
	char errormessage[STRING_SIZE];
	
	netaddresschange = 0;

	fprintf(flog,"Enter HandleNetworking\n"); // #### Debug ####

	found =	scan_network_cards();
	fprintf(flog,"found %d cards\n",found); // #### Debug ####

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
	if (configtype < 1 || configtype > 4) configtype = 0;

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
	if (x < 1 || x > 4) x = 0;
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
	int choise, found;
	int rc;

	fprintf(flog,"Enter ConfigMenu\n");

	if (!(readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings")))
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}

	found = scan_network_cards();
	fprintf(flog,"found %d Card\'s\n", found ); // #### Debug ####
	
	findkey(kv, "CONFIG_TYPE", temp); choise = atol(temp);

	do
	{
		sprintf(message, ctr[TR_NETWORK_CONFIGURATION_TYPE_LONG], NAME);
		rc = newtWinMenu(ctr[TR_NETWORK_CONFIGURATION_TYPE], message, 50, 5, 5,
			6, configtypenames, &choise, ctr[TR_OK], ctr[TR_CANCEL], NULL);
		if ( configtypecards[choise] > found ) {
			sprintf(message, "(TR) Nicht genuegend Netzwerkkarten fuer diese Auswahl gefunden.\n\nBenoetigt: %d\nGefunden: %d\n", configtypecards[choise], found);
			errorbox(message);
		}
	}
	while ( configtypecards[choise] > found);

	if (rc == 0 || rc == 1)
	{
//	if (automode != 0) runcommandwithstatus("/etc/rc.d/init.d/network stop red blue orange", ctr[TR_PUSHING_NON_LOCAL_NETWORK_DOWN]);

		sprintf(temp, "%d", choise);
		replacekeyvalue(kv, "CONFIG_TYPE", temp);
		clear_card_entry(_RED_CARD_);
		clear_card_entry(_ORANGE_CARD_);
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
	char temp[STRING_SIZE];
//	char description[STRING_SIZE], macaddr[STRING_SIZE];
//	struct nic *pnics = nics;
//	pnics = nics;
//	struct knic *pknics = knics;
//	pknics = knics;
	int configtype;
	int rc, kcount = 0, neednics; //i = 0, count = 0,
	
	fprintf(flog,"Enter driverenu\n"); // #### Debug ####

	if (!(readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings")))
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}

	strcpy(temp, "0"); findkey(kv, "CONFIG_TYPE", temp);
	configtype = atol(temp);
	
//	if (configtype == 0)
//	{
//		freekeyvalues(kv);
//		errorbox(ctr[TR_YOUR_CONFIGURATION_IS_SINGLE_GREEN_ALREADY_HAS_DRIVER]);
//		return 0;
//	}

	strcpy(message, ctr[TR_CONFIGURE_NETWORK_DRIVERS]);

	kcount = 0;	// counter to find knowing nics.
	neednics = 0;	// counter to use needing nics.
	if (HAS_GREEN) {
		strcpy(temp, ""); findkey(kv, "GREEN_MACADDR", temp);
		if (strlen(temp)) {
			strcpy(knics[_GREEN_CARD_].macaddr, temp);
			strcpy(knics[_GREEN_CARD_].colour, "GREEN");
			findkey(kv, "GREEN_DESCRIPTION", temp);
			strcpy(knics[_GREEN_CARD_].description, temp);
			findkey(kv, "GREEN_DRIVER", temp);
			strcpy(knics[_GREEN_CARD_].driver, temp);
			kcount++;
		} else {
			strcpy(knics[_GREEN_CARD_].description, ctr[TR_UNSET]);
		}
		sprintf(temp, "GREEN:  %s\n", knics[_GREEN_CARD_].description);
		strcat(message, temp);
		if (strlen(knics[_GREEN_CARD_].macaddr) ) {
			sprintf(temp, "GREEN:  (%s) %s green0\n", knics[_GREEN_CARD_].macaddr, ctr[TR_AS]);
			strcat(message, temp);
		}
		neednics++;
	}
	if (HAS_RED) {
		strcpy(temp, ""); findkey(kv, "RED_MACADDR", temp);
		if (strlen(temp)) {
			strcpy(knics[_RED_CARD_].macaddr, temp);
			strcpy(knics[_RED_CARD_].colour, "RED");
			findkey(kv, "RED_DESCRIPTION", temp);
			strcpy(knics[_RED_CARD_].description, temp);
			findkey(kv, "RED_DRIVER", temp);
			strcpy(knics[_RED_CARD_].driver, temp);
			kcount++;
		} else {
			strcpy(knics[_RED_CARD_].description, ctr[TR_UNSET]);
		}
		sprintf(temp, "RED:    %s\n", knics[_RED_CARD_].description);
		strcat(message, temp);
		if (strlen(knics[_RED_CARD_].macaddr) ) {
			sprintf(temp, "RED:    (%s) %s red0\n", knics[_RED_CARD_].macaddr, ctr[TR_AS]);
			strcat(message, temp);
		}
		neednics++;
	}
	if (HAS_ORANGE) {
		strcpy(temp, ""); findkey(kv, "ORANGE_MACADDR", temp);
		if (strlen(temp)) {
			strcpy(knics[_ORANGE_CARD_].macaddr, temp);
			strcpy(knics[_ORANGE_CARD_].colour, "ORANGE");
			findkey(kv, "ORANGE_DESCRIPTION", temp );
			strcpy(knics[_ORANGE_CARD_].description, temp );
			findkey(kv, "ORANGE_DRIVER", temp);
			strcpy(knics[_ORANGE_CARD_].driver, temp);
			kcount++;
		} else {
			strcpy(knics[_ORANGE_CARD_].description, ctr[TR_UNSET]);
		}
		sprintf(temp, "ORANGE: %s\n", knics[_ORANGE_CARD_].description);
		strcat(message, temp);
		if ( strlen(knics[_ORANGE_CARD_].macaddr) ) {
			sprintf(temp, "ORANGE: (%s) %s orange0\n", knics[_ORANGE_CARD_].macaddr, ctr[TR_AS]);
			strcat(message, temp);
		}
		neednics++;
	}
	if (HAS_BLUE) {
		strcpy(temp, ""); findkey(kv, "BLUE_MACADDR", temp);
		if (strlen(temp)) {
			strcpy(knics[_BLUE_CARD_].macaddr, temp);
			strcpy(knics[_BLUE_CARD_].colour, "BLUE");
			findkey(kv, "BLUE_DESCRIPTION", temp );
			strcpy(knics[_BLUE_CARD_].description, temp);
			findkey(kv, "BLUE_DRIVER", temp);
			strcpy(knics[_BLUE_CARD_].driver, temp);
			kcount++;
		} else {
			strcpy(knics[_BLUE_CARD_].description, ctr[TR_UNSET]);
		}
		sprintf(temp, "BLUE:   %s\n", knics[_BLUE_CARD_].description);
		strcat(message, temp);
		if (strlen(knics[_BLUE_CARD_].macaddr)) {
			sprintf(temp, "BLUE:   (%s) %s blue0\n", knics[_BLUE_CARD_].macaddr, ctr[TR_AS]);
			strcat(message, temp);
		}
		neednics++;
	}

	fprintf(flog,"found %d knowing Card\'s\n", kcount); // #### DEBUG ####

	if (neednics = kcount) {
		strcat(message, ctr[TR_DO_YOU_WISH_TO_CHANGE_THESE_SETTINGS]);
		rc = newtWinChoice(ctr[TR_DRIVERS_AND_CARD_ASSIGNMENTS], ctr[TR_OK],
		ctr[TR_CANCEL], message);
		if (rc == 0 || rc == 1)
		{
			/* Shit, got to do something.. */
			changedrivers();
		}
	} else {
		strcat(message, "\nEs wurden noch nicht alle Netzwerkkarten konfiguriert.\n");
		newtWinMessage(ctr[TR_DRIVERS_AND_CARD_ASSIGNMENTS], ctr[TR_OK], message);
		/* Shit, got to do something.. */
		changedrivers();
	}
	freekeyvalues(kv);

	return 1;
}

int cardassigned(char *colour)
{
	char command[STRING_SIZE];
	fprintf(flog,"cardassigned - %s\n", colour);
	sprintf(command, "grep -q %s < /etc/udev/rules.d/30-persistent-network.rules 2>/dev/null", colour);
	if (system(command))
		return 0;
	else
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
	fprintf(flog,"stop network on red, blue and orange\n");	// #### Debug ####
	runcommandwithstatus("/etc/rc.d/init.d/network stop red blue orange",
		ctr[TR_PUSHING_NON_LOCAL_NETWORK_DOWN]);

	findkey(kv, "CONFIG_TYPE", temp); configtype = atol(temp);
	if (configtype == 0)
		{ green = 1; }
	else if (configtype == 1)
		{ green = 1; red = 1; }
	else if (configtype == 2)
		{ green = 1; red = 1; orange = 1; }
	else if (configtype == 3)
		{ green = 1; red = 1; blue = 1; }
	else if (configtype == 4)
		{ green = 1; red=1; orange=1; blue = 1; }
//	else if (configtype == 5)
//		{ green = 1; blue = 1; orange = 1; }
//	else if (configtype == 6)
//		{ green = 1; red = 1; blue = 1; }
//	else if (configtype == 7)
//		{ green = 1; red = 1; blue = 1; orange = 1; }

	fprintf(flog,"found: g=%d r=%d o=%d b=%d\n",green, red, orange, blue); // #### Debug ####

	do
	{
		count = 0;
		strcpy(message, "(TR) Bitte wählen Sie das Interface aus das geaendert werden soll.\n\n");

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
//			fprintf(flog,"found: %s as entry %d\n", MenuInhalt[count], NicEntry[count]); // #### Debug ####
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
//			fprintf(flog,"found: %s as entry %d\n", MenuInhalt[count], NicEntry[count]); // #### Debug ####
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
//			fprintf(flog,"found: %s as entry %d\n", MenuInhalt[count], NicEntry[count]); // #### Debug ####
			sprintf(temp, "BLUE:   %s\n", knics[_BLUE_CARD_].description);
			strcat(message, temp);
			if ( strlen(knics[_BLUE_CARD_].macaddr) ) {
				sprintf(temp, "BLUE:   (%s) %s blue0\n", knics[_BLUE_CARD_].macaddr, ctr[TR_AS]);
				strcat(message, temp);
			}
			count++;
		}
		pMenuInhalt[count] = NULL;

		rc = newtWinMenu("(TR) Netcard Farbe", message, 70, 5, 5, 6, pMenuInhalt, &choise, ctr[TR_SELECT], "(TR) Entfernen" , ctr[TR_DONE], NULL);
			
		if ( rc == 0 || rc == 1) {
//			write_configs_netudev(pnics[choise].description, pnics[choise].macaddr, colour);
			// insert nic to colourcard
			if ((green) && ( choise == NicEntry[0])) nicmenu(_GREEN_CARD_);
			if ((red) && ( choise == NicEntry[1])) nicmenu(_RED_CARD_);
			if ((orange) && ( choise == NicEntry[2])) nicmenu(_ORANGE_CARD_);
			if ((blue) && ( choise == NicEntry[3])) nicmenu(_BLUE_CARD_);
		} else if (rc == 2) {
			if ((green) && ( choise == NicEntry[0])) ask_clear_card_entry(_GREEN_CARD_);
			if ((red) && ( choise == NicEntry[1])) ask_clear_card_entry(_RED_CARD_);
			if ((orange) && ( choise == NicEntry[2])) ask_clear_card_entry(_ORANGE_CARD_);
			if ((blue) && ( choise == NicEntry[3])) ask_clear_card_entry(_BLUE_CARD_);
		} 
//		else {
//			errorbox("Sie haben keine Netzwerkkarte ausgewaehlt.\n");
//			return 1;
//		}
	}
	while ( rc <= 2);
	
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

/*	strcpy(temp, "0"); findkey(kv, "CONFIG_TYPE", temp);
	configtype = atol(temp);
	
	if (RED_IS_NOT_ETH)
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_DNS_GATEWAY_WITH_GREEN]);
		return 0;
	}
*/
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
