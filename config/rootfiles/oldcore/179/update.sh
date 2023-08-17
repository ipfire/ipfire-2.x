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
# Copyright (C) 2023 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

migrate_extrahd() {
	local dev
	local fs
	local mp
	local rest

	while IFS=';' read -r dev fs mp rest; do
		# Make sure mountpoint it set (so that we won't delete
		# everything in /etc/fstab if there was an empty line).
		if [ -z "${mp}" ]; then
			continue
		fi

		# Remove the mountpoint from /etc/fstab
		sed "/[[:blank:]]${mp//\//\\\/}[[:blank:]]/d" -i /etc/fstab
	done < /var/ipfire/extrahd/devices
}

core=179

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Stop services
/usr/local/bin/openvpnctrl -k
/usr/local/bin/openvpnctrl -kn2n

# Extract files
extract_files

# Remove files
rm -rvf \
	/usr/lib/pppd/2.4.9

# Remove dropped sox addon
rm -vf \
	/opt/pakfire/db/installed/meta-sox \
	/opt/pakfire/db/meta/meta-sox \
	/opt/pakfire/db/rootfiles/sox \
	/usr/bin/play \
	/usr/bin/rec \
	/usr/bin/sox \
	/usr/bin/soxi \
	/usr/lib/libsox.so.3 \
	/usr/lib/libsox.so.3.0.0

# update linker config
ldconfig

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# Migrate ExtraHD
migrate_extrahd

# Start services
/etc/init.d/udev restart
/etc/init.d/squid restart
/usr/local/bin/openvpnctrl -s
/usr/local/bin/openvpnctrl -sn2n

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
