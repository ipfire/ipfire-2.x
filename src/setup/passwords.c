/* SmoothWall setup program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Password stuff.
 * 
 * $Id: passwords.c,v 1.5.2.1 2004/04/14 22:05:41 gespinasse Exp $
 * 
 */

#include "setup.h"

extern FILE *flog;
extern char *mylog;

extern char **ctr;

extern int automode;

int getpassword(char *password, char *text);

/* Root password. */
int handlerootpassword(void)
{
	char password[STRING_SIZE];
	char commandstring[STRING_SIZE];
		
	/* Root password. */
	if (getpassword(password, ctr[TR_ENTER_ROOT_PASSWORD]) == 2)
		return 0;
	
	snprintf(commandstring, STRING_SIZE,
		"/bin/echo 'root:%s' | /usr/sbin/chpasswd", password);
	if (runhiddencommandwithstatus(commandstring, ctr[TR_SETTING_ROOT_PASSWORD]))
	{
		errorbox(ctr[TR_PROBLEM_SETTING_ROOT_PASSWORD]);
		return 0;
	}
	
	return 1;
}

int handleadminpassword(void)
{
	char password[STRING_SIZE];
	char commandstring[STRING_SIZE];
	char message[1000];
		
	/* web interface admin password. */
	sprintf(message, ctr[TR_ENTER_ADMIN_PASSWORD], NAME, NAME);
	if (getpassword(password, message) == 2)
		return 0;
	
	snprintf(commandstring, STRING_SIZE,
		"/usr/sbin/htpasswd -c -m -b " CONFIG_ROOT "/auth/users admin '%s'", password);
	sprintf(message, ctr[TR_SETTING_ADMIN_PASSWORD], NAME);
	if (runhiddencommandwithstatus(commandstring, message))
	{
		sprintf(message, ctr[TR_PROBLEM_SETTING_ADMIN_PASSWORD], NAME);
		errorbox(message);
		return 0;
	}

	return 1;
}

/* Taken from the cdrom one. */
int getpassword(char *password, char *text)
{
	char *values[] = {	NULL, NULL, NULL };	/* pointers for the values. */
	struct newtWinEntry entries[] =
	{ 
		{ ctr[TR_PASSWORD_PROMPT], &values[0], 2 },
		{ ctr[TR_AGAIN_PROMPT], &values[1], 2 },
		{ NULL, NULL, 0 }
	};
	char title[STRING_SIZE];
	int rc;
	int done;
	
	do
	{
		done = 1;
		sprintf (title, "%s %s - %s", NAME, VERSION, SLOGAN);
		rc = newtWinEntries(title, text,
			65, 5, 5, 50, entries, ctr[TR_OK], ctr[TR_CANCEL], NULL);

		if (rc != 2)
		{
			if (strlen(values[0]) == 0 || strlen(values[1]) == 0)
			{
				errorbox(ctr[TR_PASSWORD_CANNOT_BE_BLANK]);
				done = 0;
				strcpy(values[0], "");
				strcpy(values[1], "");
			}
			else if (strcmp(values[0], values[1]) != 0)
			{
				errorbox(ctr[TR_PASSWORDS_DO_NOT_MATCH]);
				done = 0;
				strcpy(values[0], "");
				strcpy(values[1], "");
			}
			else if (strchr(values[0], ' '))
			{
				errorbox(ctr[TR_PASSWORD_CANNOT_CONTAIN_SPACES]);
				done = 0;
				strcpy(values[0], "");
				strcpy(values[1], "");
			}
		}
	}
	while (!done);

	strncpy(password, values[0], STRING_SIZE);

	if (values[0]) free(values[0]);
	if (values[1]) free(values[1]);

	return rc;
}
