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
# Copyright (C) 2015 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

# Remove old core updates from pakfire cache to save space...
core=91
for (( i=1; i<=$core; i++ ))
do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Stop services
/etc/init.d/ipsec stop

# Extract files
extract_files

# Create some missing graphs folders (core90)
mkdir -p /srv/web/ipfire/html/{accounting,graphs}
chmod 777 /srv/web/ipfire/html/{accounting,graphs}

# Update Language cache
/usr/local/bin/update-lang-cache

# Regenerate IPsec configuration
sudo -u nobody /srv/web/ipfire/cgi-bin/vpnmain.cgi

sync

# Start services
if [ `grep "ENABLED=on" /var/ipfire/vpn/settings` ]; then
	/etc/init.d/ipsec start
fi

# This update need a reboot...
#touch /var/run/need_reboot

# Finish
/etc/init.d/fireinfo start
sendprofile

# Don't report the exitcode last command
exit 0
