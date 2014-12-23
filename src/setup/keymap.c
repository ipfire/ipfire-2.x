/* SmoothWall setup program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Stuff for setting the keymap.
 * 
 * $Id: keymap.c,v 1.9.2.1 2004/04/14 22:05:41 gespinasse Exp $
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
#define KEYMAPROOT "/lib/kbd/keymaps/i386/"

static int filenamecount;
static char *filenames[MAX_FILENAMES];
static char *displaynames[MAX_FILENAMES];

static int process(char *prefix, char *path);
static int cmp(const void *s1, const void *s2);

int handlekeymap(void)
{
	int c;
	int choice;
	char *temp;
	struct keyvalue *kv = initkeyvalues();	
	int rc;
	int result;
	char keymap[STRING_SIZE];
	char commandstring[STRING_SIZE];

	filenamecount = 0;	

	process(KEYMAPROOT "azerty", "");		
	process(KEYMAPROOT "dvorak", "");
	process(KEYMAPROOT "fgGIod", "");	
	process(KEYMAPROOT "qwerty", "");
	process(KEYMAPROOT "qwertz", "");
	filenames[filenamecount] = NULL;
	qsort(filenames, filenamecount, sizeof(char *), cmp);
	
	for (c = 0; filenames[c]; c++)
	{
		displaynames[c] = malloc(STRING_SIZE);
		if ((temp = strrchr(filenames[c], '/')))
			strcpy(displaynames[c], temp + 1);
		else
			strcpy(displaynames[c], filenames[c]);
		if ((temp = strstr(displaynames[c], ".map.gz")))
			*temp = '\0';
	}
	displaynames[c] = NULL;
	
	if (!(readkeyvalues(kv, CONFIG_ROOT "/main/settings")))
	{
		freekeyvalues(kv);
		errorbox(_("Unable to open settings file"));
		return 0;
	}	
	
	strcpy(keymap, "/lib/kbd/keymaps/i386/qwerty/us.map.gz");
	findkey(kv, "KEYMAP", keymap);
	
	choice = 0;
	for (c = 0; filenames[c]; c++)
	{
		if (strcmp(keymap, filenames[c]) == 0)
			choice = c;
	}
	
	rc = newtWinMenu(_("Keyboard mapping"),
		_("Choose the type of keyboard you are using from the list below."),
		50, 5, 5, 6, displaynames, &choice, _("OK"), _("Cancel"), NULL);

	strcpy(keymap, filenames[choice]);
	
	if (rc != 2)
	{
		replacekeyvalue(kv, "KEYMAP", keymap);
		writekeyvalues(kv, CONFIG_ROOT "/main/settings");
		sprintf(commandstring, "/bin/loadkeys %s", keymap);
		mysystem(NULL, commandstring);
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

/* Small wrapper for use with qsort() to sort filename part. */		
static int cmp(const void *s1, const void *s2)
{
	/* c1 and c2 are copies. */
	char *c1 = strdup(* (char **) s1);
	char *c2 = strdup(* (char **) s2);
	/* point to somewhere in cN. */
	char *f1, *f2;
	char *temp;
	int res;
	
	if ((temp = strrchr(c1, '/')))
		f1 = temp + 1;
	else
		f1 = c1;
	if ((temp = strrchr(c2, '/')))
		f2 = temp + 1;
	else
		f2 = c2;
	/* bang off the . */
	if ((temp = strchr(f1, '.')))
		*temp = '\0';
	if ((temp = strchr(f2, '.')))
		*temp = '\0';
	
	res = strcmp(f1, f2);
	
	free(c1); free(c2);
	
	return res;
}
