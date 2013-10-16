#!/bin/bash
############################################################################
#                                                                          #
# This file is part of the IPFire Firewall.                                #
#                                                                          #
# IPFire is free software; you can redistribute it and/or modify           #
# it under the terms of the GNU General Public License as published by     #
# the Free Software Foundation; either version 3 of the License, or        #
# (at your option) any later version.                                      #
#                                                                          #
# IPFire is distributed in the hope that it will be useful,                #
# but WITHOUT ANY WARRANTY; without even the implied warranty of           #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
# GNU General Public License for more details.                             #
#                                                                          #
# You should have received a copy of the GNU General Public License        #
# along with IPFire; if not, write to the Free Software                    #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA #
#                                                                          #
# Copyright (C) 2013 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

#
# Remove old core updates from pakfire cache to save space...
core=73
for (( i=1; i<=$core; i++ ))
do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done


#
#Stop services
/etc/init.d/squid stop


#
#Extract files
extract_files

if [ -e "/var/ipfire/proxy/enable" ] || [ -e "/var/ipfire/proxy/enable_blue" ]; then
	(
		eval $(/usr/local/bin/readhash /var/ipfire/proxy/advanced/settings)

		TRANSPARENT_PORT="$(( ${PROXY_PORT} + 1 ))"
		echo "TRANSPARENT_PORT=${TRANSPARENT_PORT}" >> /var/ipfire/proxy/advanced/settings
	)
fi

# Regenerate squid configuration files.
/srv/web/ipfire/cgi-bin/proxy.cgi

#
#Start services
/etc/init.d/squid start

#
#Update Language cache
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"

# Remove invalid fetchmail symlinks when postfix is installed.
if [ ! -e "/etc/rc.d/init.d/fetchmail" ]; then
	rm -f /etc/rc.d/rc*.d/*fetchmail
fi

sync

# This update need a reboot...
#touch /var/run/need_reboot

#
#Finish
/etc/init.d/fireinfo start
sendprofile
#Don't report the exitcode last command
exit 0

