/* IPCop setup program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * $Id: domainname.c
 * 
 */

// Translation
#include <libintl.h>
#define _(x) dgettext("setup", x)

#include "setup.h"
 
extern FILE *flog;
extern char *mylog;

extern int automode;

int handledomainname(void)
{
	char domainname[STRING_SIZE] = "localdomain";
	struct keyvalue *kv = initkeyvalues();
	char *values[] = { domainname, NULL };	/* pointers for the values. */
	struct newtWinEntry entries[] =
		{ { "", &values[0], 0,}, { NULL, NULL, 0 } };
	int rc;
	int result;
	
	if (!(readkeyvalues(kv, CONFIG_ROOT "/main/settings")))
	{
		freekeyvalues(kv);
		errorbox(_("Unable to open settings file"));
		return 0;
	}	
	
	findkey(kv, "DOMAINNAME", domainname);
	
	for (;;)
	{	
		rc = newtWinEntries(_("Domain name"), _("Enter Domain name"),
			50, 5, 5, 40, entries, _("OK"), _("Cancel"), NULL);	
		
		if (rc == 1) {
			strcpy(domainname, values[0]);
			if (!(strlen(domainname)))
				errorbox(_("Domain name cannot be empty."));
			else if (strchr(domainname, ' '))
				errorbox(_("Domain name cannot contain spaces."));
			else if (strlen(domainname) != strspn(domainname,
				"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-."))
				errorbox(_("Domain name may only contain letters, numbers, hyphens and periods."));
			else
			{
				replacekeyvalue(kv, "DOMAINNAME", domainname);
				writekeyvalues(kv, CONFIG_ROOT "/main/settings");
				writehostsfiles();
				result = 1;
				break;
			}
		}
		else
		{
			result = 0;
			break;
		}
	}
	free(values[0]);
	freekeyvalues(kv);
	
	return result;
}	
