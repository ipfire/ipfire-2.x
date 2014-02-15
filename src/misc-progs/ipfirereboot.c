/*
 * This file is part of the IPCop Firewall.
 *
 * IPCop is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * IPCop is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with IPCop; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
 *
 * Copyright (C) 2005-10-25 Franck Bourdonnec
 *
 * $Id: ipcopreboot.c,v 1.1.2.2 2005/10/24 23:05:50 franck78 Exp $
 *
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "setuid.h"


/* define operations */
#define OP_REBOOT    	  "boot"
#define OP_REBOOT_FS 	  "bootfs" // add filesystem check option (not yet in GUI)
#define OP_SHUTDOWN  	  "down"
#define OP_SCHEDULE_ADD   "cron+"
#define OP_SCHEDULE_REM   "cron-"
#define OP_SCHEDULE_GET   "cron?"

int main(int argc, char**argv)
{

	if (!(initsetuid()))
	    return 1;

	// Check what command is asked
	if (argc==1)
	{	    
	    fprintf (stderr, "Missing reboot command!\n");
	    return 1;
	}

	if (argc==2 && strcmp(argv[1], OP_SHUTDOWN)==0)
	{
	    safe_system("/sbin/shutdown -h now");
	    return 0;
	}

	if (argc==2 && strcmp(argv[1], OP_REBOOT)==0)
	{
	    safe_system("/sbin/shutdown -r now");
	    return 0;
	}

	if (argc==2 && strcmp(argv[1], OP_REBOOT_FS)==0)
	{
	    safe_system("/sbin/shutdown -F -r now");
	    return 0;
	}

	// output schedule to stdout
	if (argc==2 && strcmp(argv[1], OP_SCHEDULE_GET)==0)
	{
	    safe_system("/bin/grep /sbin/shutdown /var/spool/cron/root.orig");
	    return 0;
	}

	if (argc==2 && strcmp(argv[1], OP_SCHEDULE_REM)==0)
	{
	    safe_system("/usr/bin/perl -i -p -e 's/^.*\\/sbin\\/shutdown.*$//s' /var/spool/cron/root.orig");
	    safe_system("/usr/bin/fcrontab -u root -z");
	    return 0;
	}

	if (argc==6 && strcmp(argv[1], OP_SCHEDULE_ADD)==0)
	{
	    // check args
	    if (!(  strlen(argv[2])<3 &&
		    strspn(argv[2], "0123456789") == strlen (argv[2]) &&
		    strlen(argv[3])<3 &&
		    strspn(argv[3], "0123456789") == strlen (argv[3]) &&
		    strlen(argv[4])<14 &&
		    strspn(argv[4], "1234567,*") == strlen (argv[4])  &&
		    ((strcmp(argv[5], "-r")==0) ||	//reboot
		     (strcmp(argv[5], "-h")==0))  )	//hangup
	        ) {
			fprintf (stderr, "Bad cron+ parameters!\n");
			return 1;
	    }
	    
	    // remove old entry				      
	    safe_system("/usr/bin/perl -i -p -e 's/^.*\\/sbin\\/shutdown.*$//s' /var/spool/cron/root.orig");

	    // add new entry
	    FILE *fd = NULL;
	    if ((fd = fopen("/var/spool/cron/root.orig", "a")))
	    {
		fprintf (fd,"%s %s * * %s /sbin/shutdown %s 1\n",argv[2],argv[3],argv[4],argv[5]);
		fclose (fd);
	    }
	    
	    // inform cron
	    safe_system("/usr/bin/fcrontab -u root -z");
	    return 0;
	}

	fprintf (stderr, "Bad reboot command!\n");
	return 1;
}
