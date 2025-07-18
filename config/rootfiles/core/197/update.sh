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
# Copyright (C) 2025 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

core=197

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Stop services
/usr/local/bin/openvpnctrl -k
/usr/local/bin/openvpnctrl -kn2n

# Remove files
rm -vf \
	/etc/rc.d/init.d/networking/red.down/10-ovpn \
	/etc/rc.d/init.d/networking/red.up/50-ovpn \
	/usr/lib/libbtrfs.so.0.? \
	/usr/lib/libbtrfsutil.so.1.?

# Extract files
extract_files

# update linker config
ldconfig

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# Update the OpenVPN configuration
sed -r \
	-e "s/^writepid .*/writepid \/var\/run\/openvpn-rw.pid/" \
	-e "/ncp-disable/d" \
	-e "s/^cipher (.*)/data-ciphers-fallback \1/" \
	-i /var/ipfire/ovpn/server.conf

# Change to the subnet topology
if ! grep -q "topology subnet" /var/ipfire/ovpn/server.conf; then
	echo "topology subnet" >> /var/ipfire/ovpn/server.conf
fi

# Migrate away from compression
if ! grep -q "compress migrate" /var/ipfire/ovpn/server.conf; then
	echo "compress migrate" >> /var/ipfire/ovpn/server.conf
fi

# Enable the legacy provider (just in case)
if ! grep -q "providers legacy default" /var/ipfire/ovpn/server.conf; then
	echo "providers legacy default" >> /var/ipfire/ovpn/server.conf
fi

# Enable explicit exit notification
if ! grep -q "explicit-exit-notify" /var/ipfire/ovpn/server.conf; then
	echo "explicit-exit-notify" >> /var/ipfire/ovpn/server.conf
fi

# Apply SSH configuration
/usr/local/bin/sshctrl

# Restart services
/etc/init.d/unbound restart
/etc/init.d/openvpn-n2n start
/etc/init.d/openvpn-rw start

# Reload Apache2
/etc/init.d/apache reload

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
