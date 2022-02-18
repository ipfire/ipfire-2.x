/* This file is part of the IPCop Firewall.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * Copyright (C) 2003-07-12 Robert Kerr <rkerr@go.to>
 *
 * $Id$
 *
 * Edited by the IPFire Team to change var log messages
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <signal.h>
#include <errno.h>

#include "libsmooth.h"
#include "setuid.h"
#include "netutil.h"

#define ERR_ANY 1
#define ERR_SETTINGS 2    /* error in settings file */
#define ERR_ETC 3         /* error with /etc permissions */
#define ERR_CONFIG 4      /* error updating syslogd config */
#define ERR_SYSLOG 5      /* error restarting syslogd */

int main(void)
{
   char buffer[STRING_SIZE], command[STRING_SIZE], hostname[STRING_SIZE], protocol[STRING_SIZE];
   char varmessages[STRING_SIZE], asynclog[STRING_SIZE];
   int config_fd,rc,fd,pid;
   struct stat st;
   struct keyvalue *kv = NULL;
   memset(buffer, 0, STRING_SIZE);
   memset(hostname, 0, STRING_SIZE);
   memset(protocol, 0, STRING_SIZE);
   memset(varmessages, 0, STRING_SIZE);
   memset(asynclog, 0, STRING_SIZE);

   if (!(initsetuid()))
      exit(1);


   /* Read in and verify config */
   kv=initkeyvalues();

   if (!readkeyvalues(kv, "/var/ipfire/logging/settings"))
   {
      fprintf(stderr, "Cannot read syslog settings\n");
      exit(ERR_SETTINGS);
   }

   if (!findkey(kv, "ENABLE_REMOTELOG", buffer))
   {
      fprintf(stderr, "Cannot read ENABLE_REMOTELOG\n");
      exit(ERR_SETTINGS);
   }

   if (!findkey(kv, "REMOTELOG_ADDR", hostname))
   {
      fprintf(stderr, "Cannot read REMOTELOG_ADDR\n");
      exit(ERR_SETTINGS);
   }

   if (!findkey(kv, "REMOTELOG_PROTOCOL", protocol))
   {
      /* fall back to UDP if no protocol was given */
      strcpy(protocol, "udp");
   }

   if (strspn(hostname, VALID_FQDN) != strlen(hostname))
   {
      fprintf(stderr, "Bad REMOTELOG_ADDR: %s\n", hostname);
      exit(ERR_SETTINGS);
   }

   freekeyvalues(kv);


   /* If anyone other than root can write to /etc this would be totally
    * insecure - same if anyone other than root owns /etc, as they could
    * change the file mode to give themselves or anyone else write access. */

   if(lstat("/etc",&st))
   {
      perror("Unable to stat /etc");
      exit(ERR_ETC);
   }
   if(!S_ISDIR(st.st_mode))
   {
      fprintf(stderr, "/etc is not a directory?!\n");
      exit(ERR_ETC);
   }
   if ( st.st_uid != 0  ||  st.st_mode & S_IWOTH ||
      ((st.st_gid != 0) && (st.st_mode & S_IWGRP)) )
   {
      fprintf(stderr, "/etc is owned/writable by non-root users\n");
      exit(ERR_ETC);
   }

   /* O_CREAT with O_EXCL will make open() fail if the file already exists -
    * mostly to prevent 2 copies running at once */
   if ((config_fd = open( "/etc/syslog.conf.new", O_WRONLY|O_CREAT|O_EXCL, 0644 )) == -1 )
   {
      perror("Unable to open new config file");
      exit(ERR_CONFIG);
   }

   if (!strcmp(buffer,"on"))
   {
      /* check which transmission protocol was given */
      if (strcmp(protocol, "tcp") == 0)
      {
         /* write line for TCP */
         snprintf(buffer, STRING_SIZE - 1, "/bin/sed -e 's/^#\\?\\(\\*\\.\\*[[:blank:]]\\+\\)@@\\?.\\+$/\\1@@%s/' /etc/syslog.conf >&%d", hostname, config_fd);
      }
      else
      {
         /* write line for UDP */
         snprintf(buffer, STRING_SIZE - 1, "/bin/sed -e 's/^#\\?\\(\\*\\.\\*[[:blank:]]\\+\\)@@\\?.\\+$/\\1@%s/' /etc/syslog.conf >&%d", hostname, config_fd);
      }
   }
   else
   {
      /* if remote syslog has been disabled */
      snprintf(buffer, STRING_SIZE - 1, "/bin/sed -e 's/^#\\?\\(\\*\\.\\*[[:blank:]]\\+@@\\?.\\+\\)$/#\\1/' /etc/syslog.conf >&%d", config_fd );
   }

     /* if the return code isn't 0 failsafe */
   if ((rc = unpriv_system(buffer,99,99)) != 0)
   {
      fprintf(stderr, "sed returned bad exit code: %d\n", rc);
      close(config_fd);
      unlink("/etc/syslog.conf.new");
      exit(ERR_CONFIG);
   }
   close(config_fd);

   if (rename("/etc/syslog.conf.new", "/etc/syslog.conf") == -1)
   {
      perror("Unable to replace old config file");
      unlink("/etc/syslog.conf.new");
      exit(ERR_CONFIG);
   }


   /* Get syslogd to read the new config file */
   if ((fd = open("/var/run/syslogd.pid", O_RDONLY)) == -1)
   {
      if(errno == ENOENT)
      {
         /* pid file doesn't exists.. restart syslog */
         if((rc = safe_system("/usr/sbin/syslogd u syslogd -m 0")) == 0 )
            return 0;
         else
         {
            fprintf(stderr,
               "Unable to restart syslogd - returned exit code %d\n", rc);
            exit(ERR_SYSLOG);
         }
      } else {
         /* Something odd is going on, failsafe */
         perror("Unable to open pid file");
         exit(ERR_SYSLOG);
      }
   }

   memset(buffer, 0, STRING_SIZE);
   if (read(fd, buffer, STRING_SIZE - 1) == -1)
   {
      close(fd);
      perror("Couldn't read from pid file");
      exit(ERR_SYSLOG);
   }
   close(fd);
   /* strtol does sanity checks that atoi doesn't do */
   errno = 0;
   pid = (int)strtol(buffer, (char **)NULL, 10);
   if (errno || pid <= 1)
   {
      fprintf(stderr, "Bad pid value\n");
      exit(ERR_SYSLOG);
   }
   if (kill(pid, SIGHUP) == -1)
   {
      fprintf(stderr, "Unable to send SIGHUP\n");
      exit(ERR_SYSLOG);
   }

   return 0;
}
