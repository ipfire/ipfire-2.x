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

// Translation
#include <libintl.h>
#define _(x) dgettext("setup", x)

#include "setup.h"

extern FILE *flog;
extern char *mylog;

extern int automode;

int getpassword(char *password, char *text);

/* Root password. */
int handlerootpassword(void)
{
	char password[STRING_SIZE];
	char commandstring[STRING_SIZE];
		
	/* Root password. */
	if (getpassword(password, _("Enter the 'root' user password. Login as this user for commandline access.")) == 2)
		return 0;
	
	snprintf(commandstring, STRING_SIZE,
		"/bin/echo 'root:%s' | /usr/sbin/chpasswd", password);
	if (runhiddencommandwithstatus(commandstring, _("Setting password"), _("Setting 'root' password...."), NULL)) {
		errorbox(_("Problem setting 'root' password."));
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
	sprintf(message, _("Enter %s 'admin' user password. "
		"This is the user to use for logging into the %s web administration pages."), NAME, NAME);
	if (getpassword(password, message) == 2)
		return 0;
	
	snprintf(commandstring, STRING_SIZE,
		"/usr/bin/htpasswd -c -B -C 7 -b " CONFIG_ROOT "/auth/users admin '%s'", password);
	sprintf(message, _("Setting %s 'admin' user password..."), NAME);
	if (runhiddencommandwithstatus(commandstring, _("Setting password"), message, NULL)) {
		sprintf(message, _("Problem setting %s 'admin' user password."), NAME);
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
		{ _("Password:"), &values[0], 2 },
		{ _("Again:"), &values[1], 2 },
		{ NULL, NULL, 0 }
	};
	char title[STRING_SIZE];
	int rc;
	int done;
	
	do
	{
		done = 1;
		sprintf (title, "%s - %s", NAME, SLOGAN);
		rc = newtWinEntries(title, text,
			65, 5, 5, 50, entries, _("OK"), _("Cancel"), NULL);

		if (rc != 2)
		{
			if (strlen(values[0]) == 0 || strlen(values[1]) == 0)
			{
				errorbox(_("Password cannot be blank."));
				done = 0;
				strcpy(values[0], "");
				strcpy(values[1], "");
			}
			else if (strcmp(values[0], values[1]) != 0)
			{
				errorbox(_("Passwords do not match."));
				done = 0;
				strcpy(values[0], "");
				strcpy(values[1], "");
			}
			else if (strchr(values[0], ' '))
			{
				errorbox(_("Password cannot contain spaces."));
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
