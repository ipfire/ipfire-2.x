/* SmoothWall helper program - sshctrl
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Mark Wormgoor, 2001
 * Simple program intended to be installed setuid(0) that can be used for
 * restarting SSHd.
 *
 * $Id: sshctrl.c,v 1.3 2003/12/11 10:57:34 riddles Exp $
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <fcntl.h>
#include <signal.h>
#include <errno.h>
#include "libsmooth.h"
#include "setuid.h"

#define BUFFER_SIZE 1024

char command[BUFFER_SIZE];

int main(int argc, char *argv[])
{
	if (argc < 2) {
				int fd, config_fd, rc, pid;
				char buffer[STRING_SIZE], command[STRING_SIZE] = "/bin/sed -e '";
				struct keyvalue *kv = NULL;

				if (!(initsetuid()))
						exit(1);

				kv = initkeyvalues();
				if (!readkeyvalues(kv, CONFIG_ROOT "/remote/settings")){
						fprintf(stderr, "Cannot read remote access settings\n");
						exit(1);
				}

				/* By using O_CREAT with O_EXCL open() will fail if the file already exists,
				* this prevents 2 copies of sshctrl both trying to edit the config file
				* at once. It also prevents race conditions, but these shouldn't be
				* possible as /etc/ssh/ should only be writable by root anyhow
				*/

				if ((config_fd = open( "/etc/ssh/sshd_config.new", O_WRONLY|O_CREAT|O_EXCL, 0644 )) == -1 ){
						perror("Unable to open new config file");
						freekeyvalues(kv);
						exit(1);
				}

				strlcat(command, "s/^Protocol .*$/Protocol 2/;", STRING_SIZE - 1 );

				if(findkey(kv, "ENABLE_SSH_KEYS", buffer) && !strcmp(buffer,"off"))
						strlcat(command, "s/^RSAAuthentication .*$/RSAAuthentication no/;"		"s/^PubkeyAuthentication .*$/PubkeyAuthentication no/;", STRING_SIZE - 1 );
				else
						strlcat(command, "s/^RSAAuthentication .*$/RSAAuthentication yes/;"		"s/^PubkeyAuthentication .*$/PubkeyAuthentication yes/;", STRING_SIZE - 1 );

				if(findkey(kv, "ENABLE_SSH_PASSWORDS", buffer) && !strcmp(buffer,"off"))
						strlcat(command, "s/^PasswordAuthentication .*$/PasswordAuthentication no/;", STRING_SIZE - 1 );
				else
						strlcat(command, "s/^PasswordAuthentication .*$/PasswordAuthentication yes/;", STRING_SIZE - 1 );

				if(findkey(kv, "ENABLE_SSH_PORTFW", buffer) && !strcmp(buffer,"on"))
						strlcat(command, "s/^AllowTcpForwarding .*$/AllowTcpForwarding yes/;"	"s/^PermitOpen .*$/PermitOpen any/;", STRING_SIZE - 1 );
				else
						strlcat(command, "s/^AllowTcpForwarding .*$/AllowTcpForwarding no/;"	"s/^PermitOpen .*$/PermitOpen none/;", STRING_SIZE - 1 );

				if(findkey(kv, "SSH_PORT", buffer) && !strcmp(buffer,"on"))
						strlcat(command, "s/^Port .*$/Port 22/;", STRING_SIZE - 1 );
				else
						strlcat(command, "s/^Port .*$/Port 222/;", STRING_SIZE - 1 );

				if(findkey(kv, "SSH_AGENT_FORWARDING", buffer) && !strcmp(buffer,"on"))
						strlcat(command, "s/^AllowAgentForwarding .*$/AllowAgentForwarding yes/;", STRING_SIZE - 1 );
				else
						strlcat(command, "s/^AllowAgentForwarding .*$/AllowAgentForwarding no/;", STRING_SIZE - 1 );

				freekeyvalues(kv);

				snprintf(buffer, STRING_SIZE - 1, "' /etc/ssh/sshd_config >&%d", config_fd );
				strlcat(command, buffer, STRING_SIZE - 1);

				if((rc = unpriv_system(command,99,99)) != 0){
						fprintf(stderr, "sed returned bad exit code: %d\n", rc);
						close(config_fd);
						unlink("/etc/ssh/sshd_config.new");
						exit(1);
				}

				close(config_fd);
				if (rename("/etc/ssh/sshd_config.new","/etc/ssh/sshd_config") != 0){
						perror("Unable to replace old config file");
						unlink("/etc/ssh/sshd_config.new");
						exit(1);
				}

				memset(buffer, 0, STRING_SIZE);

				if ((fd = open("/var/run/sshd.pid", O_RDONLY)) != -1){
						if (read(fd, buffer, STRING_SIZE - 1) == -1)
								fprintf(stderr, "Couldn't read from pid file\n");
						else{
								pid = atoi(buffer);
								if (pid <= 1)
										fprintf(stderr, "Bad pid value\n");
								else{
										if (kill(pid, SIGTERM) == -1)
												fprintf(stderr, "Unable to send SIGTERM\n");
										else
												unlink("/var/run/sshd.pid");
										}
								}
						close(fd);
				}
				else{
						if (errno != ENOENT){
								perror("Unable to open pid file");
								exit(1);
						}
				}

				if ((fd = open(CONFIG_ROOT "/remote/enablessh", O_RDONLY)) != -1){
						close(fd);
						safe_system("/usr/sbin/sshd");
				}

				return 0;
	}
	else if (strcmp(argv[1], "tempstart") == 0) {
		if (!is_valid_argument_num(argv[2])) {
			fprintf(stderr, "Invalid time '%s'\n", argv[2]);
			exit(2);
		}

				safe_system("/usr/local/bin/sshctrl");
				sleep(5);
				unlink("/var/ipfire/remote/enablessh");
				safe_system("cat /var/ipfire/remote/settings | sed 's/ENABLE_SSH=on/ENABLE_SSH=off/' > /var/ipfire/remote/settings2 && mv /var/ipfire/remote/settings2 /var/ipfire/remote/settings");
        safe_system("chown nobody.nobody /var/ipfire/remote/settings");
				snprintf(command, BUFFER_SIZE-1, "sleep %s && /usr/local/bin/sshctrl &", argv[2]);
				safe_system(command);
	}
}
