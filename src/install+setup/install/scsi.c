/* IPCop install program.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Alan Hourihane, 2003 <alanh@fairlite.demon.co.uk>
 * 
 * $Id: scsi.c
 * 
 */

#include "install.h"

int
try_scsi(char *disk_device)
{
	int fd;
	char dev[10];

	sprintf(dev, "/dev/%s", disk_device);

	if ((fd = open(dev, O_RDONLY)) < 0)
		return 0;

	close(fd);

	return 1;
}
