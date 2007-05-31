/* SmoothWall install program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * CDROM menu. Get "misc" driver name etc. 
 *
 */

#include "install.h"

extern FILE *flog;
extern char *mylog;

extern char **ctr;

/* Ejects the CDROM.  returns 0 for failure, 1 for success. */
int ejectcdrom(char *dev)
{
	char command;
	sprintf(command, "eject -r %s", dev);
	if (mysystem(command))
		return 0;
	else
		return 1;
}
