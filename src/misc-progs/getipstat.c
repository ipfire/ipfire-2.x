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
	
	safe_system("/sbin/iptables -L -v -n > /home/httpd/html/iptables.txt");
	safe_system("/sbin/iptables -L -v -n -t nat > /home/httpd/html/iptablesnat.txt");
	safe_system("/sbin/iptables -t mangle -L -v -n > /home/httpd/html/iptablesmangle.txt");
	safe_system("chown nobody.nobody /home/httpd/html/iptables.txt /home/httpd/html/iptablesnat.txt /home/httpd/html/iptablesmangle.txt");
	
	return 0;
}

