/* SmoothWall install program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Contains some functs for scanning /proc for ide info on CDROMS and
 * harddisks.
 * 
 */

#include "install.h"

int initialize_ide() {
    mysystem("/sbin/modprobe ide-generic");
    mysystem("/sbin/modprobe generic");
    mysystem("/sbin/modprobe ide-cd");
    mysystem("/sbin/modprobe ide-disk");

    return 0;
}

/* checkide().  Scans the named drive letter and returns the IDE_??? type. */
int checkide(char letter)
{
	FILE *f = NULL;
	char filename[STRING_SIZE];
	char buffer[STRING_SIZE];
	
	sprintf(filename, "/proc/ide/hd%c/media", letter);
	
	if (!(f = fopen(filename, "r")))
		return IDE_EMPTY;
		
	if (!(fgets(buffer, STRING_SIZE, f)))
	{
		printf("Couldn't read from %s\n", filename);
		fclose(f);
		return IDE_EMPTY;
	}
		
	fclose(f);
	
	stripnl(buffer);
	
	if (strcmp(buffer, "cdrom") == 0)
		return IDE_CDROM;
	else if (strcmp(buffer, "disk") == 0)
		return IDE_HD;
	else
		return IDE_UNKNOWN;
}

/* findidetype().  Finds the first ide deveice of the given IDE_?? type. */
char findidetype(int type)
{
	char letter;
	
	for (letter = 'a'; letter <= 'z'; letter++)
	{
		if ((checkide(letter)) == type)
		{
			return letter;
		}
	}
	return '\0';
}

