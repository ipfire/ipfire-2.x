/* This file is part of the IPFire Firewall.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 */

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <fcntl.h>
#include "setuid.h"

#define BUFFER_SIZE 1024

char command[BUFFER_SIZE]; 

int main(int argc, char *argv[]) {

        if (!(initsetuid()))
                exit(1);

        if (argc < 2) {
                fprintf(stderr, "\nNo argument given.\n\nsmartctrl <device>\n\n");
                exit(1);
        }


        sprintf(command, "/tmp/hddshutdown-%s", argv[1]);
        FILE *fp = fopen(command,"r");
	if( fp ) {
		fclose(fp);
		printf("\nDisk %s is in Standby. Do nothing because we won't wakeup\n",argv[1]);
                exit(1);
	}

        sprintf(command, "smartctl -x /dev/%s", argv[1]);
        safe_system(command);

        return 0;
}
