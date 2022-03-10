/* SmoothWall helper program - iowrap.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Installer helper for redirecting stdout/stderr to a file/terminal.
 * init calls ash through this program to shove it on a tty.
 *
 * $Id: iowrap.c,v 1.2 2001/11/27 15:20:50 riddles Exp $
 *
 */

#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

int main(int argc, char *argv[])
{
	/* Prog takes one argument.  A device to run on (like a getty) */
	if (argc >= 2)
	{
		int fd;

		if ((fd = open(argv[1], O_RDWR)) == -1)
		{
			printf("Couldn't open device\n");
			return 0;
		}
		dup2(fd, 0);
		dup2(fd, 1);
		dup2(fd, 2);
		/* Now its sending/reading on that device. */
	}

	if (argc >= 3)
		execvp(argv[2], &argv[2]);
	else
		printf("No command\n");

	return 0;
}
