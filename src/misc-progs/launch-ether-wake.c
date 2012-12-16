/* This file is part of the Wake-on-LAN GUI AddOn
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * Copyright (C) 2006-03-03 weizen_42
 *
 *
 */

#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <fcntl.h>
#include "setuid.h"


#define BUFFER_SIZE 512

char command[BUFFER_SIZE];

int main(int argc, char *argv[])
{
	if (!(initsetuid()))
		exit(1);

  snprintf(command, BUFFER_SIZE-1, "/usr/sbin/etherwake -i %s %s", argv[2], argv[1]);
  safe_system(command);

  /* Send magic packet with broadcast flag set. */
  snprintf(command, BUFFER_SIZE-1, "/usr/sbin/etherwake -i %s -b %s", argv[2], argv[1]);
  safe_system(command);

  return(0);
}
