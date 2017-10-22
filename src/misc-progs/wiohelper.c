/* wiohelper - a Who Is Online? Addon helper program
 *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 * 
 * IPFire.org - A linux based firewall
 * Copyright (C) 2017 Stephan Feddersen <addons@h-loit.de>
 *
 * All Rights Reserved.
 *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *
 * Simple program intended to be installed setuid(0) that can be used from WIO
 *
*/

#include "setuid.h"

int main(void)
{
	if (!(initsetuid()))
		exit(1);

	safe_system("/var/ipfire/wio/wio.pl");

	return 0;
}
