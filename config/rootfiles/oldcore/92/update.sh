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
core=92
for (( i=1; i<=$core; i++ ))
do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Stop services
/etc/init.d/squid stop
/etc/init.d/ipsec stop

# Extract files
extract_files

# Update Language cache
/usr/local/bin/update-lang-cache

# Regenerate IPsec configuration
sudo -u nobody /srv/web/ipfire/cgi-bin/vpnmain.cgi

rm -f /bin/[

# Start services
if [ `grep "ENABLED=on" /var/ipfire/vpn/settings` ]; then
	/etc/init.d/ipsec start
fi
/etc/init.d/squid start

# This update need a reboot...
touch /var/run/need_reboot

# Finish
/etc/init.d/fireinfo start
sendprofile
# Update grub config to display new core version
if [ -e /boot/grub/grub.cfg ]; then
	grub-mkconfig > /boot/grub/grub.cfg
fi
sync

# Don't report the exitcode last command
exit 0
