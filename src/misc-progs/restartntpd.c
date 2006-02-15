/* Ipcop helper program - restartntpd
 *
 * Starts or stops the ntpd daemon
 *
 * (c) Darren Critchley 2003
 * 
 * $Id: restartntpd.c,v 1.5 2003/12/19 14:29:09 riddles Exp $
 * 
 */
         
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <fcntl.h>
#include "setuid.h"


int main(void)
{
	int fd = -1;
	int enable = 0;

	if (!(initsetuid()))
		exit(1);
	
	safe_system("/bin/killall ntpd 2> /dev/null");
	sleep(3);

	if ((fd = open(CONFIG_ROOT "/time/allowclients", O_RDONLY)) != -1)
	{
		close(fd);
		enable = 1;
	}

	if (enable)
	{
		safe_system("/usr/bin/ntpd -Ap /var/run/ntpd.pid -u ntp:ntp");
	}
	return 0;
}
