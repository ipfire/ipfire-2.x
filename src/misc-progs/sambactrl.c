#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "setuid.h"

int main(int argc, char**argv)
{
	char commandstring[256];

        if (!(initsetuid()))
                exit(1);

        // Check what command is asked
        if (argc==1)
        {
            fprintf (stderr, "Missing smbctrl command!\n");
            return 1;
        }

        if (argc==2 && strcmp(argv[1], "smbuserdisable")==0)
        {
            snprintf(commandstring,STRING_SIZE-1,"/usr/bin/smbpasswd -d %s",argv[2]);
            safe_system(commandstring);
            return 0;
        }

        if (argc==2 && strcmp(argv[1], "smbuserenable")==0)
        {
            snprintf(commandstring,STRING_SIZE-1,"/usr/bin/smbpasswd -e %s",argv[2]);
            safe_system(commandstring);
            return 0;
        }

        if (argc==2 && strcmp(argv[1], "smbuserdelete")==0)
        {
            snprintf(commandstring,STRING_SIZE-1,"/usr/bin/smbpasswd -x %s",argv[2]);
            safe_system(commandstring);
            return 0;
        }

        if (argc==2 && strcmp(argv[1], "smbsafeconf")==0)
        {
            safe_system("/bin/cat /var/ipfire/samba/global /var/ipfire/samba/shares > /var/ipfire/samba/smb.conf");
            return 0;
        }

        if (argc==2 && strcmp(argv[1], "smbglobalreset")==0)
        {
            safe_system("/bin/cat /var/ipfire/samba/global.default /var/ipfire/samba/shares > /var/ipfire/samba/smb.conf");
            return 0;
        }

        if (argc==2 && strcmp(argv[1], "smbsharesreset")==0)
        {
            safe_system("/bin/cat /var/ipfire/samba/global /var/ipfire/samba/shares.default > /var/ipfire/samba/smb.conf");
            return 0;
        }

        if (argc==2 && strcmp(argv[1], "smbrestart")==0)
        {
            return 0;
        }

        if (argc==2 && strcmp(argv[1], "smbstop")==0)
        {
            return 0;
        }

        if (argc==2 && strcmp(argv[1], "smbstart")==0)
        {
            return 0;
        }

        if (argc==2 && strcmp(argv[1], "smbuseradd")==0)
        {
            snprintf(commandstring,STRING_SIZE-1,"/usr/sbin/useradd -c 'Samba User' -d /opt/samba -g 2110 -p %s -s /bin/false %s",argv[3],argv[2]);
            safe_system(commandstring);
            snprintf(commandstring,STRING_SIZE-1,"/bin/printf '%s\n%s\n' | /usr/local/bin/smbpasswd -as %s",argv[3],argv[3],argv[2]);
            safe_system(commandstring);
            return 0;
        }

        if (argc==2 && strcmp(argv[1], "smbchangepw")==0)
        {
            snprintf(commandstring,STRING_SIZE-1,"/bin/printf '%s\n%s\n' | /usr/local/bin/smbpasswd -as %s",argv[3],argv[3],argv[2]);
            safe_system(commandstring);
            return 0;
        }

        if (argc==2 && strcmp(argv[1], "readsmbpasswd")==0)
        {
            safe_system("/bin/chown root:nobody /var/ipfire/samba/private");
            safe_system("/bin/chown root:nobody /var/ipfire/samba/private/smbpasswd");
            safe_system("/bin/chmod 640 /var/ipfire/samba/private/smbpasswd");
            safe_system("/bin/chmod 650 /var/ipfire/samba/private");
            return 0;
        }

        if (argc==2 && strcmp(argv[1], "locksmbpasswd")==0)
        {
            safe_system("/bin/chown root:root /var/ipfire/samba/private");
            safe_system("/bin/chown root:root /var/ipfire/samba/private/smbpasswd");
            safe_system("/bin/chmod 600 /var/ipfire/samba/private/smbpasswd");
            safe_system("/bin/chmod 600 /var/ipfire/samba/private");
            return 0;
        }
}
