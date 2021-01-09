/* SmoothWall setup program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * The big one: networking. 
 * 
 */

// Translation
#include <libintl.h>
#define _(x) dgettext("setup", x)

#include "setup.h"

extern FILE *flog;
extern char *mylog;

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
				_("Networking"), _("Stopping network..."), NULL);

			rename_nics();

			runcommandwithstatus("/etc/rc.d/init.d/network start",
				_("Networking"), _("Restarting network..."), NULL);
			runcommandwithstatus("/etc/rc.d/init.d/unbound restart",
				_("Networking"), _("Restarting unbound..."), NULL);
		}
	} else {
		rename_nics();
	}
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
		errorbox(_("Unable to open settings file"));
		return 0;
	}	

	strcpy(temp, "1"); findkey(kv, "CONFIG_TYPE", temp); configtype = atol(temp);
	if (configtype < 1 || configtype > 4) configtype = 1;

	if (HAS_GREEN)
	{
		strcpy(temp, ""); findkey(kv, "GREEN_DEV", temp);
		if (!(strlen(temp)))
		{
			rc = newtWinChoice(_("Error"), _("OK"), _("Ignore"),
				_("No GREEN interface assigned."));
			if (rc == 0 || rc == 1)
			{
				freekeyvalues(kv);
				return 0;
			}
		}
		if (!(interfacecheck(kv, "GREEN")))
		{
			errorbox(_("Missing an IP address on GREEN."));
			freekeyvalues(kv);
			return 0;
		}
	}
	if (HAS_RED)
	{

		strcpy(temp, ""); findkey(kv, "RED_DEV", temp);
		if (!(strlen(temp)))
		{
			rc = newtWinChoice(_("Error"), _("OK"), _("Ignore"),
				_("No RED interface assigned."));
			if (rc == 0 || rc == 1)
			{
				freekeyvalues(kv);
				return 0;
			}
		}
		if (!(interfacecheck(kv, "RED")))
		{
			errorbox(_("Missing an IP address on RED."));
			freekeyvalues(kv);
			return 0;
		}
	}
	if (HAS_ORANGE)
	{
		strcpy(temp, ""); findkey(kv, "ORANGE_DEV", temp);
		if (!(strlen(temp)))
		{
			rc = newtWinChoice(_("Error"), _("OK"), _("Ignore"),
				_("No ORANGE interface assigned."));
			if (rc == 0 || rc == 1)
			{
				freekeyvalues(kv);
				return 0;
			}
		}
		if (!(interfacecheck(kv, "ORANGE")))
		{
			errorbox(_("Missing an IP address on ORANGE."));
			freekeyvalues(kv);
			return 0;
		}
	}
	if (HAS_BLUE)
	{
		strcpy(temp, ""); findkey(kv, "BLUE_DEV", temp);
		if (!(strlen(temp)))
		{
			rc = newtWinChoice(_("Error"), _("OK"), _("Ignore"),
				_("No BLUE interface assigned."));
			if (rc == 0 || rc == 1)
			{
				freekeyvalues(kv);
				return 0;
			}
		}
		if (!(interfacecheck(kv, "BLUE")))
		{
			errorbox(_("Missing an IP address on BLUE."));
			freekeyvalues(kv);
			return 0;
		}
	}
	return 1;
}

	
/* Shows the main menu and a summary of the current settings. */
int firstmenu(void)
{
	char *sections[] = {
		_("Network configuration type"),
		_("Drivers and card assignments"),
		_("Address settings"),
		NULL
	};
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
		errorbox(_("Unable to open settings file"));
		return 0;
	}	

	if (netaddresschange) 
		strcpy(networkrestart, _("When configuration is complete, a network restart will be required."));

	strcpy(temp, ""); findkey(kv, "CONFIG_TYPE", temp); 
	x = atol(temp);
	x--;
	if (x < 0 || x > 4) x = 0;
	/* Format heading bit. */
	snprintf(message, 1000, _("Current config: %s\n\n%s"), configtypenames[x], networkrestart);
	rc = newtWinMenu(_("Network configuration menu"), message, 50, 5, 5, 6,
			sections, &choice, _("OK"), _("Done"), NULL);

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
		errorbox(_("Unable to open settings file"));
		return 0;
	}

	found = scan_network_cards();
	
	findkey(kv, "CONFIG_TYPE", temp); choise = atol(temp);
	choise--;

		sprintf(message, _("Select the network configuration for %s. "
			"The following configuration types list those interfaces which have ethernet attached. "
			"If you change this setting, a network restart will be required, and you will have to "
			"reconfigure the network driver assignments."), NAME);
		rc = newtWinMenu(_("Network configuration type"), message, 50, 5, 5,
			6, configtypenames, &choise, _("OK"), _("Cancel"), NULL);
		if ( configtypecards[choise] > found ) {
			sprintf(message, _("Not enough netcards for your choice.\n\nNeeded: %d - Available: %d\n"),
				configtypecards[choise], found);
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
		errorbox(_("Unable to open settings file"));
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

	strcpy(message, _("Configure network drivers, and which interface each card is assigned to. "
		"The current configuration is as follows:\n\n"));

	kcount = 0;
	neednics = 0;
	if (HAS_GREEN) {
		sprintf(temp, "%-6s: %s\n", "GREEN", knics[_GREEN_CARD_].description);
		strcat(message, temp);
		if (strlen(knics[_GREEN_CARD_].macaddr) ) {
			sprintf(temp, "%-6s: (%s)\n", "GREEN", knics[_GREEN_CARD_].macaddr);
			strcat(message, temp);
		}
		neednics++;
	}
	if (HAS_RED) {
		sprintf(temp, "%-6s: %s\n", "RED", knics[_RED_CARD_].description);
		strcat(message, temp);
		if (strlen(knics[_RED_CARD_].macaddr) ) {
			sprintf(temp, "%-6s: (%s)\n", "RED", knics[_RED_CARD_].macaddr);
			strcat(message, temp);
		}
		neednics++;
	}
	if (HAS_ORANGE) {
		sprintf(temp, "%-6s: %s\n", "ORANGE", knics[_ORANGE_CARD_].description);
		strcat(message, temp);
		if ( strlen(knics[_ORANGE_CARD_].macaddr) ) {
			sprintf(temp, "%-6s: (%s)\n", "ORANGE", knics[_ORANGE_CARD_].macaddr);
			strcat(message, temp);
		}
		neednics++;
	}
	if (HAS_BLUE) {
		sprintf(temp, "%-6s: %s\n", "BLUE", knics[_BLUE_CARD_].description);
		strcat(message, temp);
		if (strlen(knics[_BLUE_CARD_].macaddr)) {
			sprintf(temp, "%-6s: (%s)\n", "BLUE", knics[_BLUE_CARD_].macaddr);
			strcat(message, temp);
		}
		neednics++;
	}

	for ( i=0 ; i<4; i++)
		if (strcmp(knics[i].macaddr, ""))
			kcount++;

	if (neednics = kcount)
	{
		strcat(message, "\n");
		strcat(message, _("Do you wish to change these settings?"));
		rc = newtWinChoice(_("Drivers and card assignments"), _("OK"),
			_("Cancel"), message);
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
		errorbox(_("Unable to open settings file"));
		return 0;
	}
	if (automode == 0)
		runcommandwithstatus("/etc/rc.d/init.d/network stop red blue orange",
			_("Networking"), _("Restarting non-local network..."), NULL);

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
		strcpy(message, _("Please choose the interface you wish to change.\n\n"));

		if (green) {
			strcpy(MenuInhalt[count], "GREEN");
			pMenuInhalt[count] = MenuInhalt[count];
			NicEntry[_GREEN_CARD_] = count;
			sprintf(temp, "%-6s: %s\n", "GREEN", knics[_GREEN_CARD_].description);
			strcat(message, temp);
			if ( strlen(knics[_GREEN_CARD_].macaddr) ) {
				sprintf(temp, "%-6s: (%s)\n", "GREEN", knics[_GREEN_CARD_].macaddr);
				strcat(message, temp);
			}
			count++;
		}

		if (red) {
			strcpy(MenuInhalt[count], "RED");
			pMenuInhalt[count] = MenuInhalt[count];
			NicEntry[_RED_CARD_] = count;
			sprintf(temp, "%-6s: %s\n", "RED", knics[_RED_CARD_].description);
			strcat(message, temp);
			if ( strlen(knics[_RED_CARD_].macaddr) ) {
				sprintf(temp, "%-6s: (%s)\n", "RED", knics[_RED_CARD_].macaddr);
				strcat(message, temp);
			}
			count++;
		}

		if (orange) {
			strcpy(MenuInhalt[count], "ORANGE");
			pMenuInhalt[count] = MenuInhalt[count];
			NicEntry[_ORANGE_CARD_] = count;
			sprintf(temp, "%-6s: %s\n", "ORANGE", knics[_ORANGE_CARD_].description);
			strcat(message, temp);
			if ( strlen(knics[_ORANGE_CARD_].macaddr) ) {
				sprintf(temp, "%-6s: (%s)\n", "ORANGE", knics[_ORANGE_CARD_].macaddr);
				strcat(message, temp);
			}
			count++;
		}

		if (blue) {
			strcpy(MenuInhalt[count], "BLUE");
			pMenuInhalt[count] = MenuInhalt[count];
			NicEntry[_BLUE_CARD_] = count;
			sprintf(temp, "%-6s: %s\n", "BLUE", knics[_BLUE_CARD_].description);
			strcat(message, temp);
			if ( strlen(knics[_BLUE_CARD_].macaddr) ) {
				sprintf(temp, "%-6s: (%s)\n", "BLUE", knics[_BLUE_CARD_].macaddr);
				strcat(message, temp);
			}
			count++;
		}
		pMenuInhalt[count] = NULL;

		rc = newtWinMenu(_("Assigned Cards"), message, 70, 5, 5, 6, pMenuInhalt,
			&choise, _("Select"), _("Remove"), _("Done"), NULL);
			
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
		errorbox(_("Unable to open settings file"));
		return 0;
	}

	sprintf(message, _("If you change this IP address, and you are logged in remotely, "
		"your connection to the %s machine will be broken, and you will have to reconnect "
		"on the new IP. This is a risky operation, and should only be attempted if you "
		"have physical access to the machine, should something go wrong."), NAME);
	rc = newtWinChoice(_("Warning"), _("OK"), _("Cancel"), message);
	
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
		errorbox(_("Unable to open settings file"));
		return 0;
	}
	if (!(readkeyvalues(mainkv, CONFIG_ROOT "/main/settings")))
	{
		freekeyvalues(kv);
		freekeyvalues(mainkv);
		errorbox(_("Unable to open settings file"));
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
		rc = newtWinMenu(_("Address settings"),
			_("Select the interface you wish to reconfigure."), 50, 5,
			5, 6, sections, &choice, _("OK"), _("Done"), NULL);	

		if (rc == 0 || rc == 1)
		{
			if (strcmp(sections[choice], "GREEN") == 0)
			{
				findkey(kv, "GREEN_ADDRESS", oldgreenaddress);
				sprintf(message, _("If you change this IP address, and you are logged in remotely, "
					"your connection to the %s machine will be broken, and you will have to reconnect "
					"on the new IP. This is a risky operation, and should only be attempted if you "
					"have physical access to the machine, should something go wrong."), NAME);
				rc = newtWinChoice(_("Warning"), _("OK"), _("Cancel"), message);
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
