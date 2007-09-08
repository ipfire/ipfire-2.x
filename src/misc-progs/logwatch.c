/* This file is part of the IPCop Firewall.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * Copyright (C) 2003-07-12 Robert Kerr <rkerr@go.to>
 *
 * $Id: logwatch.c,v 1.2 2003/12/11 11:25:54 riddles Exp $
 *
 */

#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <grp.h>
#include <pwd.h>
#include <sys/types.h>
#include "libsmooth.h"
#include "setuid.h"

/* Lots of distros just run logwatch as root from cron, but logwatch doesn't
 * need any root privs, just the ability to access it's filter scripts
 * (/etc/log.d/) and the log files (under /var/log/). By creating a logwatch
 * user and group and ensuring it has read access to the logs we can run
 * logwatch unprivileged. Apart from the principle of least privilege running
 * logwatch as root turns out to be doubly a bad idea because a flaw in the way
 * it works:
 *
 *   http://www.securityfocus.com/archive/1/327833/2003-07-01/2003-07-07/0
 *
 * This wrapper program should be run as root, but not installed setuid root,
 * it's basic aim is to allow a root cron job to safely run logcheck; as such
 * it will drop privileges, becoming the locheck user & group then run
 * logcheck. In many ways this is much the same as getting cron to run
 *    su -s /etc/log.d/scripts/logwatch.pl
 * the wrapper however is able to read configuration info from /var/ipcop and
 * pass the correct args to logwatch
 */

int main(void)
{
   char buffer[STRING_SIZE];
   struct keyvalue *kv = NULL;
   struct passwd *pw;
   gid_t groups[2];
   char * argv[4];

   if(getuid())
   {
      fprintf(stderr, "logwatch should be ran by root\n");
      exit(1);
   }

   /* Read in and verify config */
   kv=initkeyvalues();

   if (!readkeyvalues(kv, CONFIG_ROOT "/logging/settings"))
   {
      fprintf(stderr, "Cannot read syslog settings\n");
      exit(1);
   }

   if (!findkey(kv, "LOGWATCH_LEVEL", buffer))
   {
      fprintf(stderr, "Cannot read LOGWATCH_LEVEL\n");
      exit(1);
   }

   if (strcmp(buffer,"Low") && strcmp(buffer,"Med") && strcmp(buffer,"High"))
   {
      fprintf(stderr, "Bad LOGWATCH_LEVEL: %s\n", buffer);
      exit(1);
   }

   freekeyvalues(kv);


   /* lookup logwatch user */
   if(!(pw = getpwnam("logwatch")))
   {
      fprintf(stderr,"Couldn't find logwatch user.\n");
      exit(1);
   }
   /* paranoia... */
   memset(pw->pw_passwd, 0, strlen(pw->pw_passwd));
   endpwent();

   /* more paranoia */
   if(!pw->pw_uid || !pw->pw_gid)
   {
      fprintf(stderr,"logwatch user appears to be UID or GID 0, aborting.\n");
      exit(1);
   }

   /* drop privs */
   groups[0] = groups[1] = pw->pw_gid;
   if (setgroups(1,groups)) { perror("Couldn't clear group list"); exit(1); }
   if (setgid(pw->pw_gid))  { perror("Couldn't setgid(logwatch)"); exit(1); }
   if (setuid(pw->pw_uid))  { perror("Couldn't setuid(logwatch)"); exit(1); }

   /* ok, spawn logwatch */
   argv[0] = "logwatch.pl";
   argv[1] = "--detail";
   argv[2] = buffer;
   argv[3] = NULL;
   execve("/usr/share/logwatch/scripts/logwatch.pl", argv, trusted_env);

   /* shouldn't get here - execve replaces current running process */
   perror("logwatch: execve failed");
   exit(1);
}
