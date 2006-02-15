/* SmoothWall install program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Stuff for downloading the smoothwall tarball using wget.
 * 
 * $Id: net.c,v 1.8.2.2 2004/04/14 22:05:40 gespinasse Exp $
 * 
 */
 
#include "install.h"

extern FILE *flog;
extern char *mylog;

extern char **ctr;

static int got_url = 0;

char url[STRING_SIZE];

static int gettarballurl();

int checktarball(char *file)
{
	int done;
	int tries = 0;
	char commandstring[STRING_SIZE];

	done = 0;
	while (!done)
	{
		if (!got_url && gettarballurl() != 1)
			return 0;

		/* remove any successive /'s */
		while (url[strlen(url)-1] == '/') { url[strlen(url)-1] = '\0'; }

		snprintf(commandstring, STRING_SIZE, "/bin/wget -s -O /dev/null %s/%s", url, file);
		if (!(runcommandwithstatus(commandstring, ctr[TR_CHECKING])))
		{
			done = 1;
			got_url = 1;
		} 
		else 
		{
			errorbox(ctr[TR_FAILED_TO_FIND]);
			got_url = 0;
			if (tries == 3)
				return 0;
		}
		tries++;
	}

	return 1;
}

static int gettarballurl()
{
	char *values[] = {	NULL, NULL };	/* pointers for the values. */
	struct newtWinEntry entries[] =
		{ { "", &values[0], 0,}, { NULL, NULL, 0 } };
	char title[STRING_SIZE];
	char message[1000];
	int rc;

	sprintf(message, ctr[TR_ENTER_URL]);
	sprintf (title, "%s v%s - %s", NAME, VERSION, SLOGAN);
	rc = newtWinEntries(title, message,
		60, 5, 5, 50, entries, ctr[TR_OK], ctr[TR_CANCEL], NULL);
		
	strncpy(url, values[0], STRING_SIZE);

	return rc;
}
