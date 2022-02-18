/* IPFire helper program - fireinfoctrl
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) IPFire Team, 2011
 *
 * Simple program that calls "sendprofile" as the root user.
 *
 */

#include <stdlib.h>
#include "setuid.h"

int main(void)
{
	if (!(initsetuid()))
		exit(1);

	safe_system("/usr/bin/sendprofile");

	return 0;
}
