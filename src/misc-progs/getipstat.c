/* IPFire helper program - IPStat
 *
 * Get the list from IPTABLES -L
 * 
 * Optional commandline parameters:
 *  -x 
 *   instruct iptables to expand numbers
 *  -f 
 *   display filter table 
 *  -n
 *   display nat table
 *  -m
 *   display mangle table
 */

#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include "setuid.h"

int main(int argc, char** argv)
{
	// Set defaults
	// first argument has to be "iptables" since execve executes the program pointed to by filename
	// but /sbin/iptables is actually a symlink to /sbin/xtables-legacy-multi hence that program is executed
	// however without the notion that it was called as "iptables". So we have to pass "iptables" as first
	// argument.
	char *args[10] = {"iptables", "--list", "--verbose", "--numeric", "--wait", "5", NULL, NULL, NULL, NULL};
	char *usage = "getipstat [-x][-f|-n|-m]";
	unsigned int pcount = 6;
	unsigned int table_set = 0;

	int opt;
	
	if (!(initsetuid()))
		exit(1);

	// Parse command line arguments
	if (argc > 1) {
		while ((opt = getopt(argc, argv, "xfnm")) != -1) {
			switch(opt) {
				case 'x':
					args[pcount++] = "--exact";
					break;
				case 'f':
					table_set++;
					break;
				case 'n':
					if (table_set == 0) {
						args[pcount++] = "--table";
						args[pcount++] = "nat";
					}
					table_set++;
					break;
				case 'm':
					if (table_set == 0) {
						args[pcount++] = "--table";
						args[pcount++] = "mangle";
					}
					table_set++;
					break;
				default:
					fprintf(stderr, "\nBad argument given.\n\n%s\n", usage);
					exit(1);
			}
		}
		if (table_set > 1) {
			fprintf(stderr, "\nArguments -f/-n/-m are mutualy exclusive.\n\n%s\n", usage);
			exit(1);
		}
	}

	return run("/sbin/iptables", args);
}

