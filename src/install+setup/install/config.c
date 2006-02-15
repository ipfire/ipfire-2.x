/* SmoothWall install program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Write the config and get password stuff.
 * 
 * $Id: config.c,v 1.6.2.3 2005/12/07 20:42:48 franck78 Exp $
 * 
 */

#include "install.h"
extern char **ctr;	// text translation table

/* called to write out all config files using the keyvalue interface. */
int write_disk_configs(struct devparams *dp)
{
	char devnode[STRING_SIZE];
	char partition[STRING_SIZE];
	char *messages[5] = {   NULL,
				ctr[TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK1],
				ctr[TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK2],
				ctr[TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK3],
				ctr[TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK4] 
		        };
	/* dev node links. */
	sprintf(devnode, "%s", dp->devnode_disk_run);
	if (symlink(devnode, "/harddisk/dev/harddisk"))
	{
		errorbox(ctr[TR_UNABLE_TO_MAKE_SYMLINK_DEV_HARDDISK]);
		return 0;
	}
	
	int j;
	for (j=1; j<5; j++) {
		sprintf(devnode, "%s%d", dp->devnode_part_run,j);
		sprintf(partition,"/harddisk/dev/harddisk%d",j);
		if (symlink(devnode, partition))
		{
			errorbox( messages[j] );
			return 0;
		}
	}

	/* Add /dev/root symlink linking to the root filesystem to 
	 * keep updfstab happy */
	sprintf(devnode, "%s4", dp->devnode_part_run);
	if (symlink(devnode, "/harddisk/dev/root"))
	{
		errorbox(ctr[TR_UNABLE_TO_MAKE_SYMLINK_DEV_ROOT]);
		return 0;
	}

	return 1;
}

int write_lang_configs( char *lang)
{
	struct keyvalue *kv = initkeyvalues();
	
	/* default stuff for main/settings. */
	replacekeyvalue(kv, "LANGUAGE", lang);
	replacekeyvalue(kv, "HOSTNAME", SNAME);
	writekeyvalues(kv, "/harddisk" CONFIG_ROOT "/main/settings");
	freekeyvalues(kv);
	
	return 1;
}

int write_ethernet_configs(struct keyvalue *ethernetkv)
{
	/* Write out the network settings we got from a few mins ago. */
	writekeyvalues(ethernetkv, "/harddisk" CONFIG_ROOT "/ethernet/settings");
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
		sprintf (title, "%s v%s - %s", NAME, VERSION, SLOGAN);
		rc = newtWinEntries(title, text,
			50, 5, 5, 20, entries, ctr[TR_OK], ctr[TR_CANCEL], NULL);
		
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
		}
	}
	while (!done);

	strncpy(password, values[0], STRING_SIZE);

	if (values[0]) free(values[0]);
	if (values[1]) free(values[1]);

	return rc;
}
