/* IPFire helper program - IPStat
 *
 * Get the list from IPTABLES -L
 * 
 */
         
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <fcntl.h>
#include "setuid.h"


int main(void)
{
	if (!(initsetuid()))
		exit(1);
	
	safe_system("/usr/sbin/iptstate -1rbt");
	return 0;
}

