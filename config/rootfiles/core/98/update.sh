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
# Copyright (C) 2016 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

# Remove old core updates from pakfire cache to save space...
core=98
for (( i=1; i<=$core; i++ ))
do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Stop services

# Extract files
extract_files

# Bugfixes for core96 updater bugs...
if [ -e /boot/grub/grub.conf ]; then
	# legacy grub config on xen or citrix conflicts with grub2 config
	# and core96 contains an empty file
	if [ ! -s /boot/grub/grub.cfg ]; then
		rm /boot/grub/grub.cfg
	fi
fi

if [ -e /boot/grub/grub.cfg ]; then
	# test if serial console is enabled
	grep "^7:2345" /etc/inittab > /dev/null
	if [ "${?}" == "0" ]; then
		# Fix grub config for serial console
		sed -i /etc/default/grub \
			-e "s|\"panic=10\"|\"panic=10 console=ttyS0,115200n8\"|g"
		sed -i /etc/default/grub \
			-e "s|^GRUB_TERMINAL=.*||g"
		sed -i /etc/default/grub \
			-e "s|^GRUB_SERIAL_COMMAND=.*||g"
		echo "GRUB_TERMINAL=\"serial\"" >> /etc/default/grub
		echo "GRUB_SERIAL_COMMAND=\"serial --unit=0 --speed=115200\"" >> /etc/default/grub
	fi
fi


# Update Language cache
# /usr/local/bin/update-lang-cache

# restart init after glibc update
telinit u

# Start services

# This update need a reboot...
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
