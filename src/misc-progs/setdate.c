/* Ipcop helper program - setdate.c
 *
 * Sets the date and time
 *
 * (c) Darren Critchley 2003
 * 
 * $Id: setdate.c,v 1.2 2003/12/11 11:25:54 riddles Exp $
 * 
 */
         
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include "setuid.h"

int main(int argc, char *argv[])
{
	char command[STRING_SIZE];
	int a,b,c;
	
	if (!(initsetuid()))
		exit(1);
	
	if (argc < 3)
	{
		fprintf(stderr, "Missing arg\n");
		exit(1);
	}
	
	if (! (strlen(argv[1]) < 11 && sscanf(argv[1], "%d-%d-%d", &a, &b, &c) == 3)
	   || (strspn(argv[1], NUMBERS "-" ) != strlen(argv[1])))
	{
		fprintf(stderr, "Bad arg\n");
		exit(1);
	}

	if (! (strlen(argv[2]) < 6 && sscanf(argv[2], "%d:%d", &a, &b) == 2)
	   || (strspn(argv[2], NUMBERS ":" ) != strlen(argv[2])))
	{
		fprintf(stderr, "Bad arg\n");
		exit(1);
	}

	memset(command, 0, STRING_SIZE);
	snprintf(command, STRING_SIZE - 1, "/bin/date -s '%s %s' >/dev/null", argv[1], argv[2]);
	fprintf(stderr, "Setting Date: %s %s\n", argv[1], argv[2]);
	safe_system(command);
	
	return 0;
}
