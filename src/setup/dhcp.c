/* SmoothWall setup program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Stuff for setting up the DHCP server from the setup prog.
 * 
 */

// Translation
#include <libintl.h>
#define _(x) dgettext("setup", x)

#include "setup.h"

#define TOP 4

#define START_ADDRESS 0
#define END_ADDRESS 1
#define PRIMARY_DNS 2
#define SECONDARY_DNS 3
#define DEFAULT_LEASE_TIME 4
#define MAX_LEASE_TIME 5
#define DOMAIN_NAME_SUFFIX 6
#define MAX_BOXES 7

extern FILE *flog;
extern char *mylog;

extern int automode;

newtComponent dhcpform;
newtComponent entries[MAX_BOXES];
newtComponent enabledcheckbox;

void dhcpdialogcallbackdhcp(newtComponent cm, void *data);

int handledhcp(void)
{
	char *results[MAX_BOXES];
	char enabledresult;
	char startenabled;
	struct newtExitStruct es;
	newtComponent header;
	newtComponent labels[MAX_BOXES];
	newtComponent ok, cancel;	
	char message[1000];
	char *labeltexts[MAX_BOXES] = {
		_("Start address:"),
		_("End address:"),
		_("Primary DNS:"),
		_("Secondary DNS:"),
		_("Default lease (mins):"),
		_("Max lease (mins):"),
		_("Domain name suffix:")
	};
	char *varnames[MAX_BOXES] = {
		"START_ADDR_GREEN",
		"END_ADDR_GREEN",
		"DNS1_GREEN",
		"DNS2_GREEN",
		"DEFAULT_LEASE_TIME_GREEN",
		"MAX_LEASE_TIME_GREEN",
		"DOMAIN_NAME_GREEN"
	};
	char defaults[MAX_BOXES][STRING_SIZE]; 
	int result;
	int c;
	char temp[STRING_SIZE];
	struct keyvalue *mainkv = initkeyvalues();
	struct keyvalue *dhcpkv = initkeyvalues();
	struct keyvalue *ethernetkv = initkeyvalues();
	int error;
	FILE *file;
	char greenaddress[STRING_SIZE];	
	char greennetaddress[STRING_SIZE];
	char greennetmask[STRING_SIZE];
	
 	memset(defaults, 0, sizeof(char) * STRING_SIZE * MAX_BOXES);
	
	if (!(readkeyvalues(dhcpkv, CONFIG_ROOT "/dhcp/settings")))
	{
		freekeyvalues(dhcpkv);
		freekeyvalues(ethernetkv);
		errorbox(_("Unable to open settings file"));
		return 0;
	}
	if (!(readkeyvalues(ethernetkv, CONFIG_ROOT "/ethernet/settings")))
	{
		freekeyvalues(dhcpkv);
		freekeyvalues(ethernetkv);
		errorbox(_("Unable to open settings file"));
		return 0;
	}
	if (!(readkeyvalues(mainkv, CONFIG_ROOT "/main/settings")))
	{
		freekeyvalues(dhcpkv);
		freekeyvalues(ethernetkv);
		freekeyvalues(mainkv);
		errorbox(_("Unable to open settings file"));
		return 0;
	}

	/* Set default values. */	
	findkey(ethernetkv, "GREEN_ADDRESS", defaults[PRIMARY_DNS]);
	findkey(mainkv, "DOMAINNAME", defaults[DOMAIN_NAME_SUFFIX]);
	strcpy(defaults[DEFAULT_LEASE_TIME], "60");
	strcpy(defaults[MAX_LEASE_TIME], "120");

	newtCenteredWindow(55, 18, _("DHCP server configuration"));

	dhcpform = newtForm(NULL, NULL, 0);

	header = newtTextboxReflowed(1, 1,
		_("Configure the DHCP server by entering the settings information."),
		52, 0, 0, 0);
	newtFormAddComponent(dhcpform, header);

	strcpy(temp, ""); findkey(dhcpkv, "ENABLE_GREEN", temp);
	if (strcmp(temp, "on") == 0)
		startenabled = '*';
	else
		startenabled = ' ';
	enabledcheckbox = newtCheckbox(2, TOP + 0, _("Enabled"), startenabled, " *", &enabledresult);
	newtFormAddComponent(dhcpform, enabledcheckbox);
	newtComponentAddCallback(enabledcheckbox, dhcpdialogcallbackdhcp, NULL);		

	for (c = 0; c < MAX_BOXES; c++)
	{
		labels[c] = newtTextbox(2, TOP + 2 + c, 33, 1, 0);
		newtTextboxSetText(labels[c], labeltexts[c]);
		newtFormAddComponent(dhcpform, labels[c]);				
		strcpy(temp, defaults[c]); findkey(dhcpkv, varnames[c], temp);
		entries[c] = newtEntry(34, TOP + 2 + c, temp, 18, &results[c], 0);
		newtFormAddComponent(dhcpform, entries[c]);		
		if (startenabled == ' ')
			newtEntrySetFlags(entries[c], NEWT_FLAG_DISABLED, NEWT_FLAGS_SET);			
		
	}
	
	ok = newtButton(10, c + 7, _("OK"));
	cancel = newtButton(34, c + 7, _("Cancel"));

	newtFormAddComponents(dhcpform, ok, cancel, NULL);
	
	do {
		error = 0;
		newtFormRun(dhcpform, &es);
	
		if (es.u.co == ok)
		{
			/* OK was pressed; verify the contents of each entry. */		
			if (enabledresult == '*')
			{
				strcpy(message, _("The following fields are invalid:\n\n"));
				if (inet_addr(results[START_ADDRESS]) == INADDR_NONE)
				{
					strcat(message, _("Start address"));
					strcat(message, "\n");
					error = 1;
				}
				if (inet_addr(results[END_ADDRESS]) == INADDR_NONE)
				{
					strcat(message, _("End address"));
					strcat(message, "\n");
					error = 1;
				}
				if (strlen(results[SECONDARY_DNS]))
				{
					if (inet_addr(results[PRIMARY_DNS]) == INADDR_NONE)
					{
						strcat(message, _("Primary DNS"));
						strcat(message, "\n");
						error = 1;
					}
				}
				if (strlen(results[SECONDARY_DNS]))
				{
					if (inet_addr(results[SECONDARY_DNS]) == INADDR_NONE)
					{
						strcat(message, _("Secondary DNS"));
						strcat(message, "\n");
						error = 1;
					}
				}
				if (!(atol(results[DEFAULT_LEASE_TIME])))
				{
					strcat(message, _("Default lease time"));
					strcat(message, "\n");
					error = 1;
				}
				if (!(atol(results[MAX_LEASE_TIME])))
				{
					strcat(message, _("Max. lease time"));
					strcat(message, "\n");
					error = 1;
				}
			}				
			
			if (error)
				errorbox(message);
			else
			{
				for (c = 0; c < MAX_BOXES; c++)
					replacekeyvalue(dhcpkv, varnames[c], results[c]);
				if (enabledresult == '*')
				{
					replacekeyvalue(dhcpkv, "ENABLE_GREEN", "on");
					fclose(fopen(CONFIG_ROOT "/dhcp/enable_green", "w"));
					chown(CONFIG_ROOT "/dhcp/enable_green", 99, 99);
					mysystem(NULL, "/usr/local/bin/dhcpctrl enable");
				}
				else
				{
					replacekeyvalue(dhcpkv, "ENABLE_GREEN", "off");
					unlink(CONFIG_ROOT "/dhcp/enable_green");
					mysystem(NULL, "/usr/local/bin/dhcpctrl disable");
				}
				replacekeyvalue(dhcpkv, "VALID", "yes");
				writekeyvalues(dhcpkv, CONFIG_ROOT "/dhcp/settings");
				
				findkey(ethernetkv, "GREEN_ADDRESS", greenaddress);				
				findkey(ethernetkv, "GREEN_NETADDRESS", greennetaddress);
				findkey(ethernetkv, "GREEN_NETMASK", greennetmask);
			
				file = fopen(CONFIG_ROOT "/dhcp/dhcpd.conf", "w");
				fprintf(file, "ddns-update-style none;\n");
				fprintf(file, "authoritative;\n");
				fprintf(file, "subnet %s netmask %s\n", greennetaddress, greennetmask);
				fprintf(file, "{\n");
				fprintf(file, "\toption subnet-mask %s;\n", greennetmask);
				fprintf(file, "\toption domain-name \"%s\";\n", results[DOMAIN_NAME_SUFFIX]);		
				fprintf(file, "\toption routers %s;\n", greenaddress);
				if (strlen(results[PRIMARY_DNS]))
				{
					fprintf(file, "\toption domain-name-servers ");
					fprintf(file, "%s", results[PRIMARY_DNS]);
					if (strlen(results[SECONDARY_DNS]))
						fprintf(file, ", %s", results[SECONDARY_DNS]);
					fprintf(file, ";\n");
				}
				
				fprintf(file, "\trange %s %s;\n",	results[START_ADDRESS], results[END_ADDRESS]);
				fprintf(file, "\tdefault-lease-time %d;\n", (int) atol(results[DEFAULT_LEASE_TIME]) * 60);
				fprintf(file, "\tmax-lease-time %d;\n",	(int) atol(results[MAX_LEASE_TIME]) * 60);
				fprintf(file, "}\n");
				fclose(file);
				chown(CONFIG_ROOT "/dhcp/dhcpd.conf", 99, 99);
				if (automode == 0)
					mysystem(NULL, "/usr/local/bin/dhcpctrl enable");
			}
			result = 1;
		}
		else
			result = 0;
	} while (error);
	
	newtFormDestroy(dhcpform);
	newtPopWindow();
	
	freekeyvalues(dhcpkv);
	freekeyvalues(ethernetkv);
	freekeyvalues(mainkv);
	
	return result;
}

/* Called when enabled flag is toggled.  Toggle disabled state of other 3
 * controls. */
void dhcpdialogcallbackdhcp(newtComponent cm, void *data)
{
	int c;
	
	for (c = 0; c < MAX_BOXES; c++)
		newtEntrySetFlags(entries[c], NEWT_FLAG_DISABLED, NEWT_FLAGS_TOGGLE);
		
	newtRefresh();
	newtDrawForm(dhcpform);	
}
