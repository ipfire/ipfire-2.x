#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <fcntl.h>
#include "setuid.h"

#define BUFFER_SIZE 1024

char command[BUFFER_SIZE]; 

int main(int argc, char *argv[])
{

        if (!(initsetuid()))
                exit(1);

        // Check what command is asked
        if (argc==1)
        {
            fprintf (stderr, "Missing upnpctrl command!\n");
            return 1;
        }

        if (strcmp(argv[1], "start")==0)
        {
            snprintf(command, BUFFER_SIZE-1, "route add -net 239.0.0.0 netmask 255.0.0.0 %s", argv[2]);
            safe_system(command);
            printf(command);
            snprintf(command, BUFFER_SIZE-1, "/usr/sbin/upnpd %s %s", argv[2], argv[3] );
            safe_system(command);
            printf(command);
            return 0;
        }

        if (strcmp(argv[1], "stop")==0)
        {
            snprintf(command, BUFFER_SIZE-1, "killall upnpd");
            safe_system(command);
            printf(command);
            snprintf(command, BUFFER_SIZE-1, "route del -net 239.0.0.0 netmask 255.0.0.0 %s", argv[2]);
            safe_system(command);
            printf(command);
            return 0;
        }
}
