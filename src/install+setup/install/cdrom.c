/* SmoothWall install program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * CDROM menu. Get "misc" driver name etc. 
 *
 * $Id: cdrom.c,v 1.6.2.1 2004/04/14 22:05:39 gespinasse Exp $
 *
 */

#include "install.h"

extern FILE *flog;
extern char *mylog;

extern char **ctr;

/* Ejects the CDROM.  returns 0 for failure, 1 for success. */
int ejectcdrom(char *dev)
{
	int fd;

	if ((fd = open(dev, O_RDONLY|O_NONBLOCK)) == -1)
		return 0;
	
	if (ioctl(fd, CDROMEJECT) == -1)
	{
		close(fd);
		return 0;
	}
	close(fd);
	
	return 1;
}
