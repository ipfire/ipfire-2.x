/* SmoothWall setup program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Stuff for setting the timezone.
 * 
 * $Id: timezone.c,v 1.4.2.1 2004/04/14 22:05:41 gespinasse Exp $
 * 
 */

// Translation
#include <libintl.h>
#define _(x) dgettext("setup", x)

#include "setup.h"
 
extern FILE *flog;
extern char *mylog;

extern int automode;

#define MAX_FILENAMES 5000
#define ZONEFILES "/usr/share/zoneinfo/posix"

static int filenamecount;
static char *filenames[MAX_FILENAMES];
static char *displaynames[MAX_FILENAMES];

static int process(char *prefix, char *path);
static int cmp(const void *s1, const void *s2);

int handletimezone(void)
{
	int c;
	int choice;
	char *temp;
	struct keyvalue *kv = initkeyvalues();	
	int rc;
	int result;
	char timezone[STRING_SIZE];

	filenamecount = 0;	

	process(ZONEFILES, "");
	filenames[filenamecount] = NULL;
	qsort(filenames, filenamecount, sizeof(char *), cmp);
	
	for (c = 0; filenames[c]; c++)
	{
		displaynames[c] = malloc(STRING_SIZE);
		if ((temp = strstr(filenames[c], ZONEFILES)))
			strcpy(displaynames[c], temp + strlen(ZONEFILES) + 1);
		else
			strcpy(displaynames[c], filenames[c]);
	}
	displaynames[c] = NULL;
	
	if (!(readkeyvalues(kv, CONFIG_ROOT "/main/settings")))
	{
		freekeyvalues(kv);
		errorbox(_("Unable to open settings file"));
		return 0;
	}	
	
	strcpy(timezone, ZONEFILES "/Europe/Berlin");
	findkey(kv, "TIMEZONE", timezone);
	
	choice = 0;
	for (c = 0; filenames[c]; c++)
	{
		if (strcmp(timezone, filenames[c]) == 0)
			choice = c;
	}
	
	rc = newtWinMenu(_("Timezone"), _("Choose the timezone you are in from the list below."),
		50, 5, 5, 6, displaynames, &choice, _("OK"), _("Cancel"), NULL);

	strcpy(timezone, filenames[choice]);
	
	if (rc != 2)
	{
		replacekeyvalue(kv, "TIMEZONE", timezone);
		writekeyvalues(kv, CONFIG_ROOT "/main/settings");
		unlink("/etc/localtime");
		link(timezone, "/etc/localtime");
		result = 1;
	}
	else
		result = 0;	
	
	for (c = 0; filenames[c]; c++)
	{
		free(filenames[c]);
		free(displaynames[c]);
	}
	freekeyvalues(kv);	
	
	return result;
}

static int process(char *prefix, char *path)
{
	DIR *dir;
	struct dirent *de;
	char newpath[PATH_MAX];
	
	snprintf(newpath, PATH_MAX, "%s%s", prefix, path);
	
	if (!(dir = opendir(newpath)))
	{
		if (filenamecount > MAX_FILENAMES)
			return 1;
		
		filenames[filenamecount] = (char *) strdup(newpath);
		filenamecount++;
		return 0;
	}
			
	while ((de = readdir(dir)))
	{
		if (de->d_name[0] == '.') continue;
		snprintf(newpath, PATH_MAX, "%s/%s", path, de->d_name);
		process(prefix, newpath);
	}
	closedir(dir);
	
	return 1;
}

/* Small wrapper for use with qsort(). */		
static int cmp(const void *s1, const void *s2)
{
	return (strcmp(* (char **) s1, * (char **) s2));
}
