/* Addon helper program - monitorTraff
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * Copyright (c) Achim Weber 2 November 2006
 *
 * Wrapper for Perl Monitoring script
 *
 * $Id: monitorTraff.c,v 1.4 2006/11/15 17:53:43 dotzball Exp $
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "setuid.h"

/* define parameters */
#define PARA_TEST		"--testEmail"
#define PARA_WARN		"--warnEmail"
#define PARA_FORCE		"--force"

struct keyvalue *kv = NULL;

void usage()
{
	fprintf (stderr, "Usage:\n");
	fprintf (stderr, "\tmonitorTraff [PARAMETER]\n");
	fprintf (stderr, "\t\tWhen called without parameter, monitorTraff calculates the traffic.\n");
	fprintf (stderr, "\t\tPARAMETER:\n");
	fprintf (stderr, "\t\t\t--testEmail : Send a test email\n");
	fprintf (stderr, "\t\t\t--warnEmail : Send a warn email\n");
	fprintf (stderr, "\t\t\t--force 	: Force re-calculation\n");
}

int main(int argc, char *argv[])
{
	char buffer[STRING_SIZE];

	if (!(initsetuid()))
		return 1;

	// What should we do?
	if (argc==1)
	{
		// calc traffic
		safe_system("/usr/local/bin/monitorTraffic.pl");
	}
	else if (argc==2
		&& (strcmp(argv[1], PARA_TEST)==0 
			|| strcmp(argv[1], PARA_WARN)==0 
			|| strcmp(argv[1], PARA_FORCE)==0) )
	{
		// send (test|warn) Email or force re-calc
		memset(buffer, 0, STRING_SIZE);
		if ( snprintf(buffer, STRING_SIZE - 1, "/usr/local/bin/monitorTraffic.pl %s", argv[1]) >= STRING_SIZE )
		{
			fprintf(stderr, "Command too long\n");
			exit(1);
		}
		safe_system(buffer);
	}
	else
	{
		usage();
	}

	return 0;
}
