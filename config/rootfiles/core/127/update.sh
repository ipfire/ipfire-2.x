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
# Copyright (C) 2019 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

core=127

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Stop services
/etc/init.d/squid stop

# Remove files

# Extract files
extract_files

# update linker config
ldconfig

# Update Language cache
/usr/local/bin/update-lang-cache

# Regenerate squid configuration file
sudo -u nobody /srv/web/ipfire/cgi-bin/proxy.cgi

# If not exist create ovpn ca index.txt(.attr) and fix rights
touch /var/ipfire/ovpn/ca/index.txt.attr
chmod 644 /var/ipfire/ovpn/ca/index.txt.attr
chown nobody:nobody /var/ipfire/ovpn/ca/index.txt.attr
touch /var/ipfire/ovpn/ca/index.txt
chmod 644 /var/ipfire/ovpn/ca/index.txt
chown nobody:nobody /var/ipfire/ovpn/ca/index.txt

# Start services
/etc/init.d/unbound restart
/etc/init.d/squid start

# Reload sysctl.conf
sysctl -p

# Re-run depmod
depmod -a

# Update xt_geoip
/usr/local/bin/xt_geoip_update

# This update needs a reboot...
touch /var/run/need_reboot

# Finish
/etc/init.d/fireinfo start
sendprofile

# Update grub config to display new core version
if [ -e /boot/grub/grub.cfg ]; then
	grub-mkconfig -o /boot/grub/grub.cfg
fi

sync

# Don't report the exitcode last command
exit 0
