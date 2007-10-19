/* IPCop setup program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * $Id: domainname.c
 * 
 */
 
#include "setup.h"
 
extern FILE *flog;
extern char *mylog;

extern char **ctr;

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
		errorbox(ctr[TR_UNABLE_TO_OPEN_SETTINGS_FILE]);
		return 0;
	}	
	
	findkey(kv, "DOMAINNAME", domainname);
	
	for (;;)
	{	
		rc = newtWinEntries(ctr[TR_DOMAINNAME], ctr[TR_ENTER_DOMAINNAME],
			50, 5, 5, 40, entries, ctr[TR_OK], ctr[TR_CANCEL], NULL);	
		
		if (rc == 1)
		{
			strcpy(domainname, values[0]);
			if (!(strlen(domainname)))
				errorbox(ctr[TR_DOMAINNAME_CANNOT_BE_EMPTY]);
			else if (strchr(domainname, ' '))
				errorbox(ctr[TR_DOMAINNAME_CANNOT_CONTAIN_SPACES]);
			else if (strlen(domainname) != strspn(domainname,
				"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-."))
				errorbox(ctr[TR_DOMAINNAME_NOT_VALID_CHARS]);
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
