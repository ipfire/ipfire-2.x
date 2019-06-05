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

core=133

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# remove dropped packages
for package in jansson; do
	rm -f "/opt/pakfire/db/installed/meta-${package}"
	rm -f "/opt/pakfire/db/meta/meta-${package}"
	rm -f "/opt/pakfire/db/rootfiles/${package}"
done

# Stop services
/etc/init.d/squid stop
/usr/local/bin/ipsecctrl D

# Extract files
extract_files

# create main/security file
touch /var/ipfire/main/security
chmod 644 /var/ipfire/main/security
chown nobody:nobody /var/ipfire/main/security

# update linker config
ldconfig

# restart init after glibc update
telinit u

# Update Language cache
/usr/local/bin/update-lang-cache

# Regenerate /etc/ipsec.conf
sudo -u nobody /srv/web/ipfire/cgi-bin/vpnmain.cgi

# Modify suricata modify-sids file
/usr/sbin/convert-ids-modifysids-file

# Start services
/usr/local/bin/ipsecctrl S
/etc/init.d/suricata restart
/etc/init.d/squid start
/etc/init.d/collectd restart

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
