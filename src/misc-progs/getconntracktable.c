/* IPFire helper program - getconntracktable
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * The kernel's connection tracking table is not readable by
 * non-root users. So this helper will just read and output it.
 */

#include <stdio.h>
#include <stdlib.h>
#include "setuid.h"

int main(void) {
	if (!(initsetuid()))
		exit(1);

	FILE *fp = fopen("/proc/net/nf_conntrack", "r");
	if (fp == NULL) {
		exit(1);
	}

	/* Read content line by line and write it to stdout. */
	char linebuf[STRING_SIZE];
	while (fgets(linebuf, STRING_SIZE, fp)) {
		printf("%s", linebuf);
	}

	fclose(fp);
	return 0;
}
