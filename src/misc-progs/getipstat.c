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

	safe_system("/sbin/iptables -L -v -n > /var/tmp/iptables.txt");
	safe_system("/sbin/iptables -L -v -n -t nat > /var/tmp/iptablesnat.txt");
	safe_system("/sbin/iptables -t mangle -L -v -n > /var/tmp/iptablesmangle.txt");
	safe_system("chown nobody.nobody /var/tmp/iptables.txt /var/tmp/iptablesnat.txt /var/tmp/iptablesmangle.txt");
	
	return 0;
}

