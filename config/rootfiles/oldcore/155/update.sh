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
# Copyright (C) 2020 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

core=155

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Remove files
rm -vrf \
	/lib/libcrypt.so.1 \
	/lib/libcrypt-2.32.so \
	/lib/libhistory.so.6 \
	/lib/libhistory.so.6.3 \
	/lib/libreadline.so.6 \
	/lib/libreadline.so.6.3 \
	/usr/lib/sse2 \
	/usr/local/lib/sse2 \
	/usr/lib/libboost* \
	/usr/lib/libdb-4.so \
	/usr/lib/libdb-4.4.so \
	/usr/lib/libdb_cxx-4.so \
	/usr/lib/libdb_cxx-4.4.so \
	/usr/lib/libgmp.so.3 \
	/usr/lib/libgmp.so.3.5.2 \
	/usr/lib/libjpeg.so.62 \
	/usr/lib/libjpeg.so.62.1.0 \
	/usr/lib/libturbojpeg.so.0.0.0 \
	/lib/libpcre.so.0 \
	/lib/libpcre.so.0.0.1

# Stop services

# Extract files
extract_files

# update linker config
ldconfig

# Create a symlink from /run/initctl to /dev/initctl
ln -s /dev/initctl /run/initctl

# Disable all connection tracking helper
sed -E -e "s/^CONNTRACK_(.*?)=on/CONNTRACK_\1=off/g" \
	-i /var/ipfire/optionsfw/settings

# Apply local configuration to sshd_config
/usr/local/bin/sshctrl

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# Start services
/etc/init.d/sshd restart
/etc/init.d/dhcp restart
/etc/init.d/unbound restart
/etc/init.d/collectd restart
/etc/init.d/squid restart
/etc/init.d/suricata restart

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
