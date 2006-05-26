/* IFire helper program - restartapplejuice
 *
 * Starts or stops the applejuice core
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
	
	safe_system("/etc/init.d/applejuice stop");
	sleep(3);
	safe_system("/etc/init.d/applejuice start");

	return 0;
}
