/* SmoothWall setup program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Misc. stuff for the lib.
 * 
 */

// Translation
#include <libintl.h>
#define _(x) dgettext("setup", x)

#include "setup.h"

extern FILE *flog;
extern char *mylog;

extern int automode;

int writehostsfiles(void)
{	
	char message[1000];
	struct keyvalue *kv;
	char hostname[STRING_SIZE];
	char domainname[STRING_SIZE] = "localdomain";
	char commandstring[STRING_SIZE];
	
	kv = initkeyvalues();
	if (!(readkeyvalues(kv, CONFIG_ROOT "/main/settings")))
	{
		freekeyvalues(kv);
		errorbox(_("Unable to open settings file"));
		return 0;
	}
	strcpy(hostname, SNAME );
	findkey(kv, "HOSTNAME", hostname);
	findkey(kv, "DOMAINNAME", domainname);
	freekeyvalues(kv);
		
	sprintf(commandstring, "/bin/hostname %s.%s", hostname, domainname);
	if (mysystem(NULL, commandstring))
	{
		errorbox(_("Unable to set hostname."));
		return 0;
	}
	
	return 1;
}	
