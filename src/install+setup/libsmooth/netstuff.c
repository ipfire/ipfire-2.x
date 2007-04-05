/* SmoothWall libsmooth.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Contains network library functions.
 * 
 */

#include "libsmooth.h"
#include <signal.h>

extern FILE *flog;
extern char *mylog;

extern char **ctr;

newtComponent networkform;
newtComponent addressentry;
newtComponent netmaskentry;
newtComponent statictyperadio;
newtComponent dhcptyperadio;
newtComponent pppoetyperadio;
newtComponent pptptyperadio;
newtComponent dhcphostnameentry;

/* acceptable character filter for IP and netmaks entry boxes */
static int ip_input_filter(newtComponent entry, void * data, int ch, int cursor)
{
	if ((ch >= '0' && ch <= '9') || ch == '.' || ch == '\r' || ch >= NEWT_KEY_EXTRA_BASE)
		return ch;
	return 0;
}

/* This is a groovie dialog for showing network info.  Takes a keyvalue list,
 * a colour and a dhcp flag.  Shows the current settings, and rewrites them
 * if necessary.  DHCP flag sets wether to show the dhcp checkbox. */
int changeaddress(struct keyvalue *kv, char *colour, int typeflag,
	char *defaultdhcphostname)
{
	char *addressresult;
	char *netmaskresult;
	char *dhcphostnameresult;
	struct newtExitStruct es;
	newtComponent header;
	newtComponent addresslabel;
	newtComponent netmasklabel;
	newtComponent dhcphostnamelabel;
	newtComponent ok, cancel;	
	char message[1000];
	char temp[STRING_SIZE];
	char addressfield[STRING_SIZE];
	char netmaskfield[STRING_SIZE];
	char typefield[STRING_SIZE];
	char dhcphostnamefield[STRING_SIZE];
	int error;
	int result = 0;
	char type[STRING_SIZE];
	int startstatictype = 0;
	int startdhcptype = 0;
	int startpppoetype = 0;
	int startpptptype = 0;
		
	/* Build some key strings. */
	sprintf(addressfield, "%s_ADDRESS", colour);
	sprintf(netmaskfield, "%s_NETMASK", colour);
	sprintf(typefield, "%s_TYPE", colour);
	sprintf(dhcphostnamefield, "%s_DHCP_HOSTNAME", colour);
		
	sprintf(message, ctr[TR_INTERFACE], colour);
	newtCenteredWindow(44, (typeflag ? 18 : 12), message);
	
	networkform = newtForm(NULL, NULL, 0);

	sprintf(message, ctr[TR_ENTER_THE_IP_ADDRESS_INFORMATION], colour);
	header = newtTextboxReflowed(1, 1, message, 42, 0, 0, 0);
	newtFormAddComponent(networkform, header);

	/* See if we need a dhcp checkbox.  If we do, then we shift the contents
	 * of the window down two rows to make room. */
	if (typeflag)
	{
		strcpy(temp, "STATIC"); findkey(kv, typefield, temp);
		if (strcmp(temp, "STATIC") == 0) startstatictype = 1;
		if (strcmp(temp, "DHCP") == 0) startdhcptype = 1;
		if (strcmp(temp, "PPPOE") == 0) startpppoetype = 1;
		if (strcmp(temp, "PPTP") == 0) startpptptype = 1;
		statictyperadio = newtRadiobutton(2, 4, ctr[TR_STATIC], startstatictype, NULL);
		dhcptyperadio = newtRadiobutton(2, 5, "DHCP", startdhcptype, statictyperadio);
		pppoetyperadio = newtRadiobutton(2, 6, "PPPOE", startpppoetype, dhcptyperadio);
		pptptyperadio = newtRadiobutton(2, 7, "PPTP", startpptptype, pppoetyperadio);
		newtFormAddComponents(networkform, statictyperadio, dhcptyperadio, 
			pppoetyperadio, pptptyperadio, NULL);
		newtComponentAddCallback(statictyperadio, networkdialogcallbacktype, NULL);
		newtComponentAddCallback(dhcptyperadio, networkdialogcallbacktype, NULL);
		newtComponentAddCallback(pppoetyperadio, networkdialogcallbacktype, NULL);
		newtComponentAddCallback(pptptyperadio, networkdialogcallbacktype, NULL);
		dhcphostnamelabel = newtTextbox(2, 9, 18, 1, 0);
		newtTextboxSetText(dhcphostnamelabel, ctr[TR_DHCP_HOSTNAME]);
		strcpy(temp, defaultdhcphostname);
		findkey(kv, dhcphostnamefield, temp);
		dhcphostnameentry = newtEntry(20, 9, temp, 20, &dhcphostnameresult, 0);
		newtFormAddComponent(networkform, dhcphostnamelabel);		
		newtFormAddComponent(networkform, dhcphostnameentry);	
		if (startdhcptype == 0)
			newtEntrySetFlags(dhcphostnameentry, NEWT_FLAG_DISABLED, NEWT_FLAGS_SET);
	}
	/* Address */
	addresslabel = newtTextbox(2, (typeflag ? 11 : 4) + 0, 18, 1, 0);
	newtTextboxSetText(addresslabel, ctr[TR_IP_ADDRESS_PROMPT]);
	strcpy(temp, "");
	findkey(kv, addressfield, temp);
	addressentry = newtEntry(20, (typeflag ? 11 : 4) + 0, temp, 20, &addressresult, 0);
	newtEntrySetFilter(addressentry, ip_input_filter, NULL);
	if (typeflag == 1 && startstatictype == 0 && startpptptype == 0 )
		newtEntrySetFlags(addressentry, NEWT_FLAG_DISABLED, NEWT_FLAGS_SET);
	newtFormAddComponent(networkform, addresslabel);
	newtFormAddComponent(networkform, addressentry);
	
	/* Netmask */
	netmasklabel = newtTextbox(2, (typeflag ? 11 : 4) + 1, 18, 1, 0);
	newtTextboxSetText(netmasklabel, ctr[TR_NETMASK_PROMPT]);
	strcpy(temp, "255.255.255.0"); findkey(kv, netmaskfield, temp);
	netmaskentry = newtEntry(20, (typeflag ? 11 : 4) + 1, temp, 20, &netmaskresult, 0);
	newtEntrySetFilter(netmaskentry, ip_input_filter, NULL);
	if (typeflag == 1 && startstatictype == 0 && startpptptype == 0 ) 
		newtEntrySetFlags(netmaskentry, NEWT_FLAG_DISABLED, NEWT_FLAGS_SET);

	newtFormAddComponent(networkform, netmasklabel);
	newtFormAddComponent(networkform, netmaskentry);

	/* Buttons. */
	ok = newtButton(8, (typeflag ? 14 : 7), ctr[TR_OK]);
	cancel = newtButton(26, (typeflag ? 14 : 7), ctr[TR_CANCEL]);

	newtFormAddComponents(networkform, ok, cancel, NULL);

	newtRefresh();
	newtDrawForm(networkform);

	do
	{
		error = 0;
		newtFormRun(networkform, &es);
	
		if (es.u.co == ok)
		{
			/* OK was pressed; verify the contents of each entry. */
			strcpy(message, ctr[TR_INVALID_FIELDS]);
			
			strcpy(type, "STATIC");
			if (typeflag)
				gettype(type);
			if (strcmp(type, "STATIC") == 0 || strcmp(type, "PPTP") == 0 )
			{		
				if (inet_addr(addressresult) == INADDR_NONE)
				{
					strcat(message, ctr[TR_IP_ADDRESS_CR]);
					error = 1;
				}
				if (inet_addr(netmaskresult) == INADDR_NONE)
				{
					strcat(message, ctr[TR_NETWORK_MASK_CR]);
					error = 1;
				}
			}
			if (strcmp(type, "DHCP") == 0)
			{
				if (!strlen(dhcphostnameresult))
				{
					strcat(message, ctr[TR_DHCP_HOSTNAME_CR]);
					error = 1;
				}
			}
			if (error)
				errorbox(message);
			else
			{
				/* No errors!  Set new values, depending on dhcp flag etc. */
				if (typeflag)
				{
					replacekeyvalue(kv, dhcphostnamefield, dhcphostnameresult);
					if (strcmp(type, "STATIC") != 0 && strcmp(type, "PPTP") != 0)
					{
						replacekeyvalue(kv, addressfield, "0.0.0.0");
						replacekeyvalue(kv, netmaskfield, "0.0.0.0");
					}
					else
					{
						replacekeyvalue(kv, addressfield, addressresult);
						replacekeyvalue(kv, netmaskfield, netmaskresult);
					}
					replacekeyvalue(kv, typefield, type);					
				}
				else
				{
					replacekeyvalue(kv, addressfield, addressresult);
					replacekeyvalue(kv, netmaskfield, netmaskresult);
				}
				
				setnetaddress(kv, colour);
				result = 1;
			}
		}			
	}
	while (error);

	newtFormDestroy(networkform);
	newtPopWindow();
		
	return result;
}

/* for pppoe: return string thats type STATIC, DHCP or PPPOE */
int gettype(char *type)
{
	newtComponent selected = newtRadioGetCurrent(statictyperadio);
	
	if (selected == statictyperadio)
		strcpy(type, "STATIC");
	else if (selected == dhcptyperadio)
		strcpy(type, "DHCP");
	else if (selected == pppoetyperadio)
		strcpy(type, "PPPOE");
	else if (selected == pptptyperadio)
		strcpy(type, "PPTP");
	else
		strcpy(type, "ERROR");
	
	return 0;
}

/* 0.9.9: calculates broadcast too. */
int setnetaddress(struct keyvalue *kv, char *colour)
{
	char addressfield[STRING_SIZE];
	char netaddressfield[STRING_SIZE];		
	char netmaskfield[STRING_SIZE];
	char broadcastfield[STRING_SIZE];
	char address[STRING_SIZE];
	char netmask[STRING_SIZE];
	unsigned long int intaddress;
	unsigned long int intnetaddress;
	unsigned long int intnetmask;
	unsigned long int intbroadcast;
	struct in_addr temp;
	char *netaddress;
	char *broadcast;
		
	/* Build some key strings. */
	sprintf(addressfield, "%s_ADDRESS", colour);
	sprintf(netaddressfield, "%s_NETADDRESS", colour);
	sprintf(netmaskfield, "%s_NETMASK", colour);
	sprintf(broadcastfield, "%s_BROADCAST", colour);

	strcpy(address, ""); findkey(kv, addressfield, address);	
	strcpy(netmask, ""); findkey(kv, netmaskfield, netmask);		

	/* Calculate netaddress. Messy.. */
	intaddress = inet_addr(address);
	intnetmask = inet_addr(netmask);
	
	intnetaddress = intaddress & intnetmask;
	temp.s_addr = intnetaddress;	
	netaddress = inet_ntoa(temp);
	
	replacekeyvalue(kv, netaddressfield, netaddress);
	
	intbroadcast = intnetaddress | ~intnetmask;
	temp.s_addr = intbroadcast;
	broadcast = inet_ntoa(temp);	
	
	replacekeyvalue(kv, broadcastfield, broadcast);
	
	return 1;
}	

/* Called when dhcp flag is toggled.  Toggle disabled state of other 3
 * controls. */
void networkdialogcallbacktype(newtComponent cm, void *data)
{
	char type[STRING_SIZE];
	
	gettype(type);

	if (strcmp(type, "STATIC") != 0  && strcmp(type, "PPTP") != 0 )
	{
		newtEntrySetFlags(addressentry, NEWT_FLAG_DISABLED, NEWT_FLAGS_SET);
		newtEntrySetFlags(netmaskentry, NEWT_FLAG_DISABLED, NEWT_FLAGS_SET);
	}
	else
	{
		newtEntrySetFlags(addressentry, NEWT_FLAG_DISABLED, NEWT_FLAGS_RESET);
		newtEntrySetFlags(netmaskentry, NEWT_FLAG_DISABLED, NEWT_FLAGS_RESET);
	}
	if (strcmp(type, "DHCP") == 0)
		newtEntrySetFlags(dhcphostnameentry, NEWT_FLAG_DISABLED, NEWT_FLAGS_RESET);
	else
		newtEntrySetFlags(dhcphostnameentry, NEWT_FLAG_DISABLED, NEWT_FLAGS_SET);		
		
	newtRefresh();
	newtDrawForm(networkform);	
}

int interfacecheck(struct keyvalue *kv, char *colour)
{
	char temp[STRING_SIZE];
	char colourfields[NETCHANGE_TOTAL][STRING_SIZE];
	int c;

	sprintf(colourfields[ADDRESS], "%s_ADDRESS", colour);
	sprintf(colourfields[NETADDRESS], "%s_NETADDRESS", colour);
	sprintf(colourfields[NETMASK], "%s_NETMASK", colour);

	for (c = 0; c < 3; c++)
	{
		strcpy(temp, ""); findkey(kv, colourfields[c], temp);
		if (!(strlen(temp))) return 0;
	}
	return 1;
}

/* Funky routine for loading all drivers (cept those are already loaded.). */
int probecards(char *driver, char *driveroptions)
{
	return 0;
}

char *strupper(char *s)
{
 int n;
 for (n=0;s[n];n++) s[n]=toupper(s[n]);
 return s;
}


int write_configs_netudev(char *description, char *macaddr, char *colour)
{	
	#define UDEV_NET_CONF "/etc/udev/rules.d/30-persistent-network.rules"
	
	FILE *fp;
	char commandstring[STRING_SIZE];
	struct keyvalue *kv = initkeyvalues();
	char temp1[STRING_SIZE], temp2[STRING_SIZE], temp3[STRING_SIZE];
	char ucolour[STRING_SIZE];
	
	sprintf(ucolour, colour);
	strupper(ucolour);

	if (!(readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings")))
	{
		freekeyvalues(kv);
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}

	sprintf(temp1, "%s_DEV", ucolour);
	sprintf(temp2, "%s_MACADDR", ucolour);
	sprintf(temp3, "%s0", colour);
	replacekeyvalue(kv, temp1, temp3);
	replacekeyvalue(kv, temp2, macaddr);

	writekeyvalues(kv, CONFIG_ROOT "/ethernet/settings");
	freekeyvalues(kv);
	
	if( (fp = fopen(KNOWN_NICS, "a")) == NULL )
	{
		fprintf(stderr,"Couldn't open "KNOWN_NICS);
		return 1;
	}
	fprintf(fp,"%s;%s;\n", description, macaddr);
	fclose(fp);

	// Make sure that there is no conflict
	snprintf(commandstring, STRING_SIZE, "/usr/bin/touch "UDEV_NET_CONF" >/dev/null 2>&1");
  system(commandstring);
  snprintf(commandstring, STRING_SIZE, "/bin/cat "UDEV_NET_CONF" | /bin/grep -v \"%s\" > "UDEV_NET_CONF" 2>/dev/null", macaddr);
  system(commandstring);
  snprintf(commandstring, STRING_SIZE, "/bin/cat "UDEV_NET_CONF" | /bin/grep -v \"%s\" > "UDEV_NET_CONF" 2>/dev/null", colour);
	system(commandstring);

	if( (fp = fopen(UDEV_NET_CONF, "a")) == NULL )
	{
		fprintf(stderr,"Couldn't open" UDEV_NET_CONF);
		return 1;
	}
	fprintf(fp,"ACTION==\"add\", SUBSYSTEM==\"net\", SYSFS{address}==\"%s\", NAME=\"%s0\" # %s\n", macaddr, colour, description);
	fclose(fp);	
	
	return 0;
}

int nicmenu(char *colour)
{
			FILE *fp;
			char temp_line[STRING_SIZE];
			struct nic nics[20], *pnics;
			pnics = nics;
			struct knic knics[20], *pknics;
			pknics = knics;
			int rc, choise, count = 0, kcount = 0, i, found;
			char macaddr[STRING_SIZE], description[STRING_SIZE];
			char message[STRING_SIZE];

			char MenuInhalt[20][80];
			char *pMenuInhalt[20];
			
			mysystem("/bin/probenic.sh");
			
			// Read the nics we already use
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

			// Read our scanned nics
			if( (fp = fopen(SCANNED_NICS, "r")) == NULL )
			{
				fprintf(stderr,"Couldn't open "SCANNED_NICS);
				return 1;
			}
			while (fgets(temp_line, STRING_SIZE, fp) != NULL)
			{
				strcpy(description, strtok(temp_line,";"));
				strcpy(macaddr,     strtok(NULL,";"));
				found = 0;
				if (strlen(macaddr) > 5 ) {
					for (i=0; i < kcount; i++)
					{
						// Check if the nic is already in use
						if (strcmp(pknics[i].macaddr, macaddr) == NULL )
						{
							found = 1;
						}
					}
					if (!found)
					{
						strcpy( pnics[count].description , description );
						strcpy( pnics[count].macaddr , macaddr );
						count++;
					}
				}
			}
			fclose(fp);
			
			// If new nics are found...
			if (count > 0) {
				char cMenuInhalt[STRING_SIZE];
				for (i=0 ; i < count ; i++)
				{
					if ( strlen(nics[i].description) < 52 )
						strncpy(MenuInhalt[i], nics[i].description + 1, strlen(nics[i].description)- 2);
					else
					{
						strncpy(cMenuInhalt, nics[i].description + 1, 50);
						strncpy(MenuInhalt[i], cMenuInhalt,(strrchr(cMenuInhalt,' ') - cMenuInhalt));
						strcat (MenuInhalt[i], "...");
					}
					while ( strlen(MenuInhalt[i]) < 50)
						// Fill with space.
						strcat( MenuInhalt[i], " ");
	
					strcat(MenuInhalt[i], " (");
					strcat(MenuInhalt[i], nics[i].macaddr);
					strcat(MenuInhalt[i], ")");
					pMenuInhalt[i] = MenuInhalt[i];
				}
				
				sprintf(message, "Es wurde(n) %d freie Netzwerkkarte(n) in Ihrem System gefunden.\nBitte waehlen Sie im naechsten Dialog eine davon aus.\n", count);
				
				newtWinMessage("NetcardMenu", ctr[TR_OK], message);

				sprintf(message, "Bitte waehlen Sie eine der untenstehenden Netzwerkkarten fuer die Schnittstelle \"%s\" aus.\n", colour);
		
				rc = newtWinMenu("NetcardMenu", message, 50, 5, 5, 6, pMenuInhalt, &choise, ctr[TR_OK], ctr[TR_SELECT], ctr[TR_CANCEL], NULL);
				
				if ( rc == 0 || rc == 1) {
					write_configs_netudev(pnics[choise].description, pnics[choise].macaddr, colour);
				} else if (rc == 2) {
					manualdriver("pcnet32","");
	      } else {
	      	errorbox("Sie haben keine Netzwerkkarte ausgewaehlt.\n");
					return 1;
				}
				return 0;
		} else {
			// We have to add here that you can manually add a device
			newtWinMessage("NetcardMenu", ctr[TR_OK], "Es wurden leider keine freien Netzwerkkarten fuer die Schnittstelle \"%s\" in ihrem System gefunden.", colour);
			return 1;
		}
}

/* Manual entry for gurus. */
int manualdriver(char *driver, char *driveroptions)
{
	char *values[] = { NULL, NULL };	/* pointers for the values. */
	struct newtWinEntry entries[] =
		{ { "", &values[0], 0,}, { NULL, NULL, 0 } };
	int rc;
	char commandstring[STRING_SIZE];
	char *driverend;

	strcpy(driver, "");
	strcpy(driveroptions, "");
	
	rc = newtWinEntries(ctr[TR_SELECT_NETWORK_DRIVER], 
		ctr[TR_MODULE_PARAMETERS], 50, 5, 5, 40, entries, 
		ctr[TR_OK], ctr[TR_CANCEL], NULL);	
	if (rc == 0 || rc == 1)
	{
		if (strlen(values[0]))
		{
			sprintf(commandstring, "/sbin/modprobe %s", values[0]);
			if (runcommandwithstatus(commandstring, ctr[TR_LOADING_MODULE]) == 0)
			{
				if ((driverend = strchr(values[0], ' ')))
				{
					*driverend = '\0';
					strcpy(driver, values[0]);
					strcpy(driveroptions, driverend + 1);
				}				
				else
				{
					strcpy(driver, values[0]);
					strcpy(driveroptions, "");
				}
			}
			else
				errorbox(ctr[TR_UNABLE_TO_LOAD_DRIVER_MODULE]);
		}
		else
			errorbox(ctr[TR_MODULE_NAME_CANNOT_BE_BLANK]);
	}
	free(values[0]);

	return 1;
}
