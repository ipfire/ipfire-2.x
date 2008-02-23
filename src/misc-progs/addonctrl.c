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

	if (argc < 3) {
		fprintf(stderr, "\nMissing arguments.\n\naddonctrl addon (start|stop|restart|reload|enable|disable)\n\n");
		exit(1);
	}
	
	if ( strlen(argv[1])>32 ) {
	    fprintf(stderr, "\nString to large.\n\naddonctrl addon (start|stop|restart|reload|enable|disable)\n\n");
	    exit(1);
	}
	
	if ( strchr(argv[1],'/') || strchr(argv[1],'$') || strchr(argv[1],'[') || strchr(argv[1],'{') ) {
	    fprintf(stderr, "\nIllegal Char found.\n\naddonctrl addon (start|stop|restart|reload|enable|disable)\n\n");
	    exit(1);
	}
	
	sprintf(command, "/opt/pakfire/db/installed/meta-%s", argv[1]);
	FILE *fp = fopen(command,"r");
	if ( fp ) {
	    fclose(fp);
	} else {
	    fprintf(stderr, "\nAddon '%s' not found.\n\naddonctrl addon (start|stop|restart|reload|status|enable|disable)\n\n", argv[1]);
	    exit(1);
	}
	
	if (strcmp(argv[2], "start") == 0) {
		sprintf(command,"/etc/rc.d/init.d/%s start", argv[1]);
		safe_system(command);
	} else if (strcmp(argv[2], "stop") == 0) {
		sprintf(command,"/etc/rc.d/init.d/%s stop", argv[1]);
		safe_system(command);
	} else if (strcmp(argv[2], "restart") == 0) {
		sprintf(command,"/etc/rc.d/init.d/%s restart", argv[1]);
		safe_system(command);
	} else if (strcmp(argv[2], "reload") == 0) {
		sprintf(command,"/etc/rc.d/init.d/%s reload", argv[1]);
		safe_system(command);
	} else if (strcmp(argv[2], "status") == 0) {
		sprintf(command,"/etc/rc.d/init.d/%s status", argv[1]);
		safe_system(command);
	} else if (strcmp(argv[2], "enable") == 0) {
		sprintf(command,"mv -f /etc/rc.d/rc3.d/off/S??%s /etc/rc.d/rc3.d" , argv[1]);
		safe_system(command);
	} else if (strcmp(argv[2], "disable") == 0) {
		sprintf(command,"mkdir -p /etc/rc.d/rc3.d/off");
		safe_system(command);
		sprintf(command,"mv -f /etc/rc.d/rc3.d/S??%s /etc/rc.d/rc3.d/off" , argv[1]);
		safe_system(command);
	} else {
		fprintf(stderr, "\nBad argument given.\n\naddonctrl addon (start|stop|restart|reload|enable|disable)\n\n");
		exit(1);
	}

	return 0;
}
