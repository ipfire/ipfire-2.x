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
            fprintf (stderr, "Missing smbctrl command!\n");
            return 1;
        }

        if (strcmp(argv[1], "smbuserdisable")==0)
        {
            snprintf(command, BUFFER_SIZE-1, "/usr/bin/smbpasswd -d %s", argv[2]);
            safe_system(command);
            return 0;
        }

        if (strcmp(argv[1], "smbuserenable")==0)
        {
            snprintf(command, BUFFER_SIZE-1, "/usr/bin/smbpasswd -e %s", argv[2]);
            safe_system(command);
            return 0;
        }

        if (strcmp(argv[1], "smbuserdelete")==0)
        {
            snprintf(command, BUFFER_SIZE-1, "/usr/bin/smbpasswd -x %s", argv[2]);
            safe_system(command);
            snprintf(command, BUFFER_SIZE-1, "/usr/sbin/userdel %s", argv[2]);
            safe_system(command);
            return 0;
        }

        if (strcmp(argv[1], "smbsafeconf")==0)
        {
            safe_system("/bin/cat /var/ipfire/samba/global /var/ipfire/samba/shares > /var/ipfire/samba/smb.conf");
            return 0;
        }

        if (strcmp(argv[1], "smbsafeconfpdc")==0)
        {
            safe_system("/bin/cat /var/ipfire/samba/global /var/ipfire/samba/pdc /var/ipfire/samba/shares > /var/ipfire/samba/smb.conf");
            return 0;
        }

        if (strcmp(argv[1], "smbglobalreset")==0)
        {
            safe_system("/bin/cat /var/ipfire/samba/default.global /var/ipfire/samba/shares > /var/ipfire/samba/smb.conf");
            safe_system("/bin/cat /var/ipfire/samba/default.settings > /var/ipfire/samba/settings");
            safe_system("/bin/cat /var/ipfire/samba/default.global > /var/ipfire/samba/global");
            safe_system("/bin/cat /var/ipfire/samba/default.pdc > /var/ipfire/samba/pdc");
            return 0;
        }

        if (strcmp(argv[1], "smbsharesreset")==0)
        {
            safe_system("/bin/cat /var/ipfire/samba/global /var/ipfire/samba/default.shares > /var/ipfire/samba/smb.conf");
            safe_system("/bin/cat /var/ipfire/samba/default.shares > /var/ipfire/samba/shares");
            return 0;
        }

        if (strcmp(argv[1], "smbstop")==0)
        {
            safe_system("/etc/rc.d/init.d/samba stop");
            printf(command);
            return 0;
        }

        if (strcmp(argv[1], "smbstart")==0)
        {
            safe_system("/etc/rc.d/init.d/samba start");
            printf(command);
            return 0;
        }

        if (strcmp(argv[1], "smbrestart")==0)
        {
            safe_system("/etc/rc.d/init.d/samba restart");
            printf(command);
            return 0;
        }

        if (strcmp(argv[1], "smbreload")==0)
        {
            safe_system("/etc/rc.d/init.d/samba reload");
            printf(command);
            return 0;
        }

        if (strcmp(argv[1], "smbstatus")==0)
        {
            snprintf(command, BUFFER_SIZE-1, "/usr/sbin/smbstatus");
            safe_system(command);
            return 0;
        }

        if (strcmp(argv[1], "smbuseradd")==0)
        {
            snprintf(command, BUFFER_SIZE-1, "/usr/sbin/groupadd sambauser");
            safe_system(command);
            snprintf(command, BUFFER_SIZE-1, "/usr/sbin/useradd -c 'Samba User' -m -g %s -p %s -s %s %s", argv[4], argv[3], argv[5], argv[2]);
            safe_system(command);
            printf(command);
            snprintf(command, BUFFER_SIZE-1, "/usr/bin/printf '%s\n%s\n' | /usr/bin/smbpasswd -as %s", argv[3], argv[3], argv[2]);
            safe_system(command);
            printf(command);
            return 0;
        }

        if (strcmp(argv[1], "smbpcadd")==0)
        {
            snprintf(command, BUFFER_SIZE-1, "/usr/sbin/groupadd sambawks");
            safe_system(command);
            snprintf(command, BUFFER_SIZE-1, "/usr/sbin/useradd -c 'Samba Workstation' -g %s -s %s %s", argv[3], argv[4], argv[2]);
            safe_system(command);
            printf(command);
            snprintf(command, BUFFER_SIZE-1, "/usr/bin/smbpasswd -a -m %s", argv[2]);
            safe_system(command);
            printf(command);
            return 0;
        }

        if (strcmp(argv[1], "smbchangepw")==0)
        {
            snprintf(command, BUFFER_SIZE-1, "/usr/bin/printf '%s\n%s\n' | /usr/bin/smbpasswd -as %s", argv[3], argv[3], argv[2]);
            safe_system(command);
            printf(command);
            return 0;
        }

        if (strcmp(argv[1], "readsmbpasswd")==0)
        {
            safe_system("/bin/chown root:nobody /var/ipfire/samba/private");
            safe_system("/bin/chown root:nobody /var/ipfire/samba/private/smbpasswd");
            safe_system("/bin/chmod 640 /var/ipfire/samba/private/smbpasswd");
            safe_system("/bin/chmod 650 /var/ipfire/samba/private");
            return 0;
        }

        if (strcmp(argv[1], "locksmbpasswd")==0)
        {
            safe_system("/bin/chown root:root /var/ipfire/samba/private");
            safe_system("/bin/chown root:root /var/ipfire/samba/private/smbpasswd");
            safe_system("/bin/chmod 600 /var/ipfire/samba/private/smbpasswd");
            safe_system("/bin/chmod 600 /var/ipfire/samba/private");
            return 0;
        }

        if (strcmp(argv[1], "smbechotest")==0)
        {
            sprintf(command, BUFFER_SIZE-1, "/usr/bin/printf %s %s", argv[2], argv[3]);
            printf(command);
            safe_system(command);
            return 0;
        }
}
