/* SmoothWall libsmooth.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Contains network library functions.
 * 
 * $Id: netstuff.c,v 1.19.2.7 2004/11/05 23:40:17 alanh Exp $
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
	
/* Network probing! */
struct nic nics[] = {
	{ "100VG-AnyLan Network Adapters, HP J2585B, J2585A, etc", "hp100" },
	{ "3Com EtherLink III", "3c509" },
	{ "3Com 3c501", "3c501" },
	{ "3Com ISA EtherLink XL", "3c515" },
	{ "3Com 3c503 and 3c503/16", "3c503" },
	{ "3Com EtherLink MC (3c523)", "3c523" },
	{ "3Com EtherLink MC/32 (3c527)", "3c527" },
	{ "3Com EtherLink Plus (3c505)", "3c505" },
	{ "3Com EtherLink 16", "3c507" },
	{ "3Com \"Corkscrew\" EtherLink PCI III/XL, etc.", "3c59x" },
	{ "3Com Typhoon Family (3C990, 3CR990, and variants)", "typhoon" },
	{ "Adaptec Starfire/DuraLAN", "starfire" },
	{ "Alteon AceNIC/3Com 3C985/Netgear GA620 Gigabit", "acenic" },
	{ "AMD8111 based 10/100 Ethernet Controller", "amd8111e" },
	{ "AMD LANCE/PCnetAllied Telesis AT1500,  J2405A, etc", "lance" },
	{ "AMD PCnet32 and AMD PCnetPCI", "pcnet32" },
	{ "Ansel Communications EISA 3200", "ac3200" },
	{ "Apricot 680x0 VME, 82596 chipset", "82596" },
	{ "AT1700/1720", "at1700" },
	{ "Broadcom 4400", "b44" },
	{ "Broadcom Tigon3", "tg3" },
	{ "Cabletron E2100 series ethercards", "e2100" },
	{ "CATC USB NetMate-based Ethernet", "catc" },
	{ "CDC USB Ethernet", "CDCEther" },
	{ "Crystal LAN CS8900/CS8920", "cs89x0" },
	{ "Compaq Netelligent 10/100 TX PCI UTP, etc", "tlan" },
	{ "D-Link DL2000-based Gigabit Ethernet", "dl2k" },
	{ "Digi Intl. RightSwitch SE-X EISA and PCI", "dgrs" },
	{ "Digital 21x4x Tulip PCI ethernet cards, etc.", "tulip" },
	{ "Digital DEPCA & EtherWORKS,DEPCA, DE100, etc", "depca" },
	{ "DM9102 PCI Fast Ethernet Adapter", "dmfe", },
	{ "Dummy Network Card (testing)", "dummy", },
	{ "EtherWORKS DE425 TP/COAX EISA, DE434 TP PCI, etc.", "de4x5" },
	{ "EtherWORKS 3 (DE203, DE204 and DE205)", "ewrk3" },
	{ "HP PCLAN/plus", "hp-plus" },
	{ "HP LAN ethernet", "hp" },
	{ "IBM LANA", "ibmlana" },
	{ "ICL EtherTeam 16i/32" ,"eth16i" },
	{ "Intel i82557/i82558 PCI EtherExpressPro", "e100" },
	{ "Intel EtherExpress Cardbus Ethernet", "eepro100_cb" },
	{ "Intel i82595 ISA EtherExpressPro10/10+ driver" ,"eepro" },
	{ "Intel EtherExpress 16 (i82586)", "eexpress" },
	{ "Intel Panther onboard i82596 driver", "lp486e" },
	{ "Intel PRO/1000 Gigabit Ethernet", "e1000" },
	{ "KLSI USB KL5USB101-based", "kaweth" },
	{ "MiCom-Interlan NI5010 ethercard", "ni5010" },
	{ "Mylex EISA LNE390A/B", "lne390", },
	{ "Myson MTD-8xx PCI Ethernet", "fealnx" },
	{ "National Semiconductor DP8381x" , "natsemi" },
	{ "National Semiconductor DP83820" , "ns83820" },
	{ "NE/2 MCA", "ne2" },
	{ "NE2000 PCI cards, RealTEk RTL-8029, etc", "ne2k-pci" },
	{ "NE1000 / NE2000 (non-pci)", "ne" },
	{ "NI50 card (i82586 Ethernet chip)", "ni52" },
	{ "NI6510, ni6510 EtherBlaster", "ni65" },
	{ "Novell/Eagle/Microdyne NE3210 EISA", "ne3210" },
	{ "NVidia Nforce2 Driver", "forcedeth" },
	{ "Packet Engines Hamachi GNIC-II", "hamachi" },
	{ "Packet Engines Yellowfin Gigabit-NIC", "yellowfin" },
	{ "Pegasus/Pegasus-II USB ethernet", "pegasus" },
	{ "PureData PDUC8028,WD8003 and WD8013 compatibles", "wd" },
	{ "Racal-Interlan EISA ES3210", "es3210" },
	{ "RealTek RTL-8139 Fast Ethernet", "8139too" },
	{ "RealTek RTL-8139C+ series 10/100 PCI Ethernet", "8139cp" },
	{ "RealTek RTL-8150 USB ethernet", "rtl8150" },
	{ "RealTek RTL-8169 Gigabit Ethernet", "r8169" },
	{ "SiS 900 PCI", "sis900" },
	{ "SKnet MCA", "sk_mca" },
	{ "SMC 9000 series of ethernet cards", "smc9194" },
	{ "SMC EtherPower II", "epic100" },
	{ "SMC Ultra/EtherEZ ISA/PnP Ethernet", "smc-ultra" },
	{ "SMC Ultra32 EISA Ethernet", "smc-ultra32" },
	{ "SMC Ultra MCA Ethernet", "smc-mca" },
	{ "Sundance Alta", "sundance" },
	{ "SysKonnect SK-98xx", "sk98lin" },
	{ "Toshiba TC35815 Ethernet", "tc35815" },
	{ "Tulip chipset Cardbus Ethernet", "tulip_cb" },
	{ "USB Ethernet", "usbnet" },
	{ "VIA Rhine PCI Fast Ethernet, etc", "via-rhine" },
	{ "Winbond W89c840 Ethernet", "winbond-840" },
	{ "Xircom Cardbus Ethernet", "xircom_cb" },
	{ "Xircom (tulip-like) Cardbus Ethernet", "xircom_tulip_cb" },
	{ NULL, NULL }
};

/* Funky routine for loading all drivers (cept those are already loaded.). */
int probecards(char *driver, char *driveroptions)
{
	char message[1000];
	char commandstring[STRING_SIZE];
	FILE *handle;
	char line[STRING_SIZE];

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
		fprintf(flog, "Detected NIC driver %s\n",driver);
		if (strlen(driver) > 1) {
			strcpy(driveroptions, "");
			return 1;
		}
	}
	strcpy(driver, "");
	strcpy(driveroptions, "");
	
	return 0;
}

/* A listbox for selected the card... with a * MANUAL * entry at top for
 * manual module names. */
int choosecards(char *driver, char *driveroptions)
{
	int c;
	char **sections;
	int drivercount;
	int rc;
	int choice;
	char commandstring[STRING_SIZE];
	char message[STRING_SIZE];
	int done = 0;
	
	/* Count 'em */
	c = 0; drivercount = 0;
	while (nics[c].modulename)
	{
		drivercount++;
		c++;
	}
	drivercount++;
	sections = malloc((drivercount + 1) * sizeof(char *));
	
	/* Copy 'em. */
	c = 0;
	sections[c] = ctr[TR_MANUAL];
	c++;
	while (nics[c - 1].modulename)
	{
		sections[c] = nics[c - 1].description;
		c++;
	}
	sections[c] = NULL;
	
	strcpy(driver, "");
	strcpy(driveroptions, "");
	
	done = 0; choice = 1;
	while (!done)
	{
		rc = newtWinMenu(ctr[TR_SELECT_NETWORK_DRIVER],
			ctr[TR_SELECT_NETWORK_DRIVER_LONG], 50, 5, 5, 6,
			sections, &choice, ctr[TR_OK], ctr[TR_CANCEL], NULL);
		if (rc == 0 || rc == 1)
		{
			if (choice > 0)
			{
				/* Find module number, load module. */
				c = choice - 1;	
		
				if (!checkformodule(nics[c].modulename))
				{
					sprintf(commandstring, "/sbin/modprobe %s", nics[c].modulename);
					sprintf(message, ctr[TR_LOOKING_FOR_NIC], nics[c].description);
					if (runcommandwithstatus(commandstring, message) == 0)
					{
						strcpy(driver, nics[c].modulename);
						strcpy(driveroptions, "");
						done = 1;
					}
					else
						errorbox(ctr[TR_UNABLE_TO_LOAD_DRIVER_MODULE]);
				}
				else
					errorbox(ctr[TR_THIS_DRIVER_MODULE_IS_ALREADY_LOADED]);
			}
			else
			{
				manualdriver(driver, driveroptions);
				if (strlen(driver))
					done = 1;
			}
		}
		else
			done = 1;	
	}

	return 1;
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

/* Returns the total number of nics current available as ethX devices. */
int countcards(void)
{
 	FILE *file;
	char buffer[STRING_SIZE];
	char *start;
	int niccount = 0;
	
	if (!(file = fopen("/proc/net/dev", "r")))
	{
		fprintf(flog, "Unable to open /proc/net/dev in countnics()\n");
		return 0;
	}
	
	while (fgets(buffer, STRING_SIZE, file))
	{
		start = buffer;
		while (*start == ' ') start++;
		if (strncmp(start, "eth", strlen("eth")) == 0)
			niccount++;
		if (strncmp(start, "dummy", strlen("dummy")) == 0)
			niccount++;
	}
	
	fclose(file);
	
	return niccount;
}

/* Finds the listed module name and copies the card description back. */
int findnicdescription(char *modulename, char *description)
{
	int c = 0;
	
	if (strcmp(modulename, "pcmcia") == 0) {
		strcpy(description, "PCMCIA Ethernet card");
		return 0;
	}

	while (nics[c].description)
	{
		if (strcmp(nics[c].modulename, modulename) == 0)
		{
			strcpy(description, nics[c].description);
			return 1;
		}
		c++;
	}
	
	strcpy(description, "UNKNOWN");
	return 0;
}
