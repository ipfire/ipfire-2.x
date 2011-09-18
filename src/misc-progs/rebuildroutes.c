/* IPFire helper program - rebuildroutes
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 */

#include "libsmooth.h"
#include "setuid.h"

int main(int argc, char *argv[]) {
	if (!(initsetuid()))
		exit(1);

	safe_system("/etc/init.d/static-routes start >/dev/null 2>&1");

	return 0;
}
