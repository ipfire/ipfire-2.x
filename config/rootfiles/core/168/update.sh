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
# Copyright (C) 2022 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

core=168

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Remove files
rm -rvf \
	/usr/bin/dnet-config \
	/usr/bin/sdparm \
	/usr/lib/libart_lgpl_2.so* \
	/usr/lib/libdnet.la \
	/usr/lib/libdnet.so* \
	/usr/lib/libevent-1.4.so* \
	/usr/lib/libevent_core-1.4.so* \
	/usr/lib/libevent_extra-1.4.so* \
	/usr/lib/libnl.so* \
	/usr/lib/libpri.so* \
	/usr/lib/libsolv.so* \
	/usr/lib/libsolvext.so* \
	/usr/sbin/dnet

# Remove netbpm add-on, if installed
if [ -e "/opt/pakfire/db/installed/meta-netbpm" ]; then
	for i in $(</opt/pakfire/db/rootfiles/netbpm); do
		rm -rfv "/${i}"
	done
fi
rm -vf \
	/opt/pakfire/db/installed/meta-netbpm \
	/opt/pakfire/db/meta/meta-netbpm \
	/opt/pakfire/db/rootfiles/netbpm

# Stop services

# Extract files
extract_files

# update linker config
ldconfig

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# Start services

# This update needs a reboot...
#touch /var/run/need_reboot

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
