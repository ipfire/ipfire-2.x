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

core=198

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Stop services

# Remove files

# Extract files
extract_files

# Create /var/run/suricata
if ! [ -d "/var/run/suricata" ]; then
	mkdir -p /var/run/suricata
	chown suricata:suricata /var/run/suricata
fi

# update linker config
ldconfig

# restart init
telinit u

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# Apply SSH configuration
/usr/local/bin/sshctrl

# Start services
/etc/init.d/suricata restart
/etc/init.d/fcron restart

# Build initial ramdisks (for intel-microcode)
dracut --regenerate-all --force
KVER="xxxKVERxxx"
case "$(uname -m)" in
	aarch64)
		mkimage -A arm64 -T ramdisk -C lzma -d /boot/initramfs-${KVER}.img /boot/uInit-${KVER}
		# dont remove initramfs because grub need this to boot.
		;;
esac

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
