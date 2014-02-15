/* SmoothWall helper program - smoothierebirth
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Simple program intended to be installed setuid(0) that can be used for
 * starting reboot.
 * 
 * $Id: ipcoprebirth.c,v 1.2 2003/12/11 10:57:34 riddles Exp $
 * 
 */
         
#include <stdlib.h>
#include "setuid.h"

int main(void)
{
	if (!(initsetuid()))
		exit(1);
			
	safe_system("/sbin/shutdown -r now");
	
	return 0;
}
