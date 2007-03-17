/* SmoothWall install program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Stuff for downloading the smoothwall tarball using wget.
 * 
 */
 
#include "install.h"

extern FILE *flog;
extern char *mylog;

extern char **ctr;

static int got_url = 0;

char url[STRING_SIZE] = "http://";;

static int gettarballurl(char *url, char *message);

int checktarball(char *file, char *message)
{
	int done;
	int tries = 0;
	char commandstring[STRING_SIZE];

	done = 0;
	while (!done)
	{
		if (!got_url && gettarballurl(url, message) != 1)
			return 0;

		/* remove any successive /'s */
		while (url[strlen(url)-1] == '/') { url[strlen(url)-1] = '\0'; }

		snprintf(commandstring, STRING_SIZE, "/bin/wget -q --spider -O /dev/null %s/%s", url, file);
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
				return 1; /* failure */
		}
		tries++;
	}

	return 0;
}

static int gettarballurl(char *url, char *message)
{
	char *values[] = { url, NULL };	/* pointers for the values. */
	struct newtWinEntry entries[] =
		{ { "", &values[0], 0,}, { NULL, NULL, 0 } };
	char title[STRING_SIZE];
	int rc;

	sprintf (title, "%s %s - %s", NAME, VERSION, SLOGAN);
	rc = newtWinEntries(title, message,
		60, 5, 5, 50, entries, ctr[TR_OK], ctr[TR_CANCEL], NULL);
		
	strncpy(url, values[0], STRING_SIZE);

	return rc;
}
