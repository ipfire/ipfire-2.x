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

core=101

function exit_with_error() {
	# Set last succesfull installed core.
	echo $(($core-1)) > /opt/pakfire/db/core/mine
	/usr/bin/logger -p syslog.emerg -t ipfire \
		"core-update-${core}: $1"
	exit $2
}

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ ))
do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done


# Stop services
/etc/init.d/squid stop

# Remove old raspberrypi modules
rm -rf /lib/modules/3.14.65-ipfire-rpi

# Extract files
extract_files

# update linker config
ldconfig

# Fix conntrack configuration
for i in CONNTRACK_H323 CONNTRACK_FTP CONNTRACK_PPTP CONNTRACK_TFTP CONNTRACK_IRC; do
	if ! grep -q "^${i}" /var/ipfire/optionsfw/settings; then
		echo "${i}=on"
	fi
done >> /var/ipfire/optionsfw/settings

# Special handling for SIP
if ! grep -q "^CONNTRACK_SIP" /var/ipfire/optionsfw/settings; then
	if [ -e "/var/ipfire/main/disable_nf_sip" ]; then
		echo "CONNTRACK_SIP=off" >> /var/ipfire/optionsfw/settings
		rm -f /var/ipfire/main/disable_nf_sip
	else
		echo "CONNTRACK_SIP=on" >> /var/ipfire/optionsfw/settings
	fi
fi

# Update Language cache
#/usr/local/bin/update-lang-cache

#
# Start services
#
/etc/init.d/squid start

sync
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
