/* SmoothWall helper program - restartdhcp
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Simple program intended to be installed setuid(0) that can be used for
 * restarting DHCPd.
 * 
 * $Id: restartdhcp.c,v 1.5.2.1 2004/11/03 13:50:26 alanh Exp $
 * 
 */

#include "libsmooth.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <signal.h>
#include "setuid.h"

int main(void)
{
	int fd = -1;
	int fdblue = -1;
	char buffer[STRING_SIZE];
	char blue_dev[STRING_SIZE] = "", green_dev[STRING_SIZE] = "";
	int pid;
	struct keyvalue *kv = NULL;
	
	if (!(initsetuid()))
		exit(1);
		
	memset(buffer, 0, STRING_SIZE);

	/* Init the keyvalue structure */
	kv=initkeyvalues();

	/* Read in the current values */
	if (!readkeyvalues(kv, CONFIG_ROOT "/ethernet/settings"))
	{
		fprintf(stderr, "Cannot read ethernet settings\n");
		exit(1);
	}

	if (!findkey(kv, "GREEN_DEV", green_dev))
	{
		fprintf(stderr, "Cannot read GREEN_DEV\n");
		exit(1);
	}

	if (!VALID_DEVICE(green_dev))
	{
		fprintf(stderr, "Bad GREEN_DEV: %s\n", green_dev);
		exit(1);
	}

	/* Get the BLUE interface details */
	findkey(kv, "BLUE_DEV", blue_dev);

	freekeyvalues(kv);

	if ((fdblue = open(CONFIG_ROOT "/dhcp/enable_blue", O_RDONLY)) != -1)
	{
		close(fdblue);
		if (!VALID_DEVICE(blue_dev))
		{
			fprintf(stderr, "Bad BLUE_DEV: %s\n", blue_dev);
			exit(1);
		}
	}

	if ((fd = open("/var/run/dhcpd.pid", O_RDONLY)) != -1)
	{
		if (read(fd, buffer, STRING_SIZE - 1) == -1)
			fprintf(stderr, "Couldn't read from pid file\n");
		else
		{
			pid = atoi(buffer);
			if (pid <= 1)
				fprintf(stderr, "Bad pid value\n");
			else
			{
				if (kill(pid, SIGTERM) == -1)
					fprintf(stderr, "Unable to send SIGTERM\n");
				else
					unlink("/var/run/dhcpd.pid");
			}
		}
		safe_system("/bin/killall -KILL dhcpd");
		close(fd);
	}

	safe_system("/sbin/iptables -F DHCPBLUEINPUT");

	buffer[0] = '\0';

	if ((fd = open(CONFIG_ROOT "/dhcp/enable_green", O_RDONLY)) != -1)
	{
		close(fd);
		if ((fdblue = open(CONFIG_ROOT "/dhcp/enable_blue", O_RDONLY)) != -1)
		{
			close(fdblue);
			
			snprintf(buffer, STRING_SIZE-1, "/sbin/iptables -A DHCPBLUEINPUT -p tcp --source-port 68 --destination-port 67 -i %s -j ACCEPT > /dev/null 2>&1", blue_dev);
			safe_system(buffer);
			snprintf(buffer, STRING_SIZE-1, "/sbin/iptables -A DHCPBLUEINPUT -p udp --source-port 68 --destination-port 67 -i %s -j ACCEPT > /dev/null 2>&1", blue_dev);
			safe_system(buffer);
			snprintf(buffer, STRING_SIZE-1, "/usr/sbin/dhcpd -q %s %s", green_dev, blue_dev);
		} else {
			snprintf(buffer, STRING_SIZE-1, "/usr/sbin/dhcpd -q %s", green_dev);
		}
		safe_system(buffer);
	} else {
		if ((fdblue = open(CONFIG_ROOT "/dhcp/enable_blue", O_RDONLY)) != -1)
		{
			close(fdblue);

			snprintf(buffer, STRING_SIZE-1, "/sbin/iptables -A DHCPBLUEINPUT -p tcp --source-port 68 --destination-port 67 -i %s -j ACCEPT > /dev/null 2>&1", blue_dev);
			safe_system(buffer);
			snprintf(buffer, STRING_SIZE-1, "/sbin/iptables -A DHCPBLUEINPUT -p udp --source-port 68 --destination-port 67 -i %s -j ACCEPT > /dev/null 2>&1", blue_dev);
			safe_system(buffer);
			snprintf(buffer, STRING_SIZE-1,  "/usr/sbin/dhcpd -q %s", blue_dev);
			safe_system(buffer);
		}
	}

	if (buffer[0] != '\0')
	{
		/* Silly dhcpd creates pids with mode 640 */
		sleep (1);
		if ((fd = open("/var/run/dhcpd.pid", 0)) == -1)
		{
			fprintf(stderr, "No pid file\n");
			return 1;
		}
		fchmod(fd, 00644);
		close(fd);
	}

	return 0;
}
