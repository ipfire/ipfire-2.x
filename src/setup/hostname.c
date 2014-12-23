/* SmoothWall setup program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Stuff for setting the hostname.
 * 
 * $Id: hostname.c,v 1.6.2.1 2004/04/14 22:05:41 gespinasse Exp $
 * 
 */

// Translation
#include <libintl.h>
#define _(x) dgettext("setup", x)

#include "setup.h"
 
extern FILE *flog;
extern char *mylog;

extern int automode;

int handlehostname(void)
{
	char hostname[STRING_SIZE] = "";
	struct keyvalue *kv = initkeyvalues();
	char *values[] = { hostname, NULL };	/* pointers for the values. */
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
	
	strcpy(hostname, SNAME);
	findkey(kv, "HOSTNAME", hostname);
	
	for (;;)
	{
		rc = newtWinEntries(_("Hostname"), _("Enter the machine's hostname."),
			50, 5, 5, 40, entries, _("OK"), _("Cancel"), NULL);
		
		if (rc == 1)
		{
			strcpy(hostname, values[0]);
			if (!(strlen(hostname)))
				errorbox(_("Hostname cannot be empty."));
			else if (strchr(hostname, ' '))
				errorbox(_("Hostname cannot contain spaces."));
			else if (strlen(hostname) != strspn(hostname,
				"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"))
				errorbox(_("Hostname may only contain letters, numbers and hyphens."));
			else
			{
				replacekeyvalue(kv, "HOSTNAME", hostname);
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
