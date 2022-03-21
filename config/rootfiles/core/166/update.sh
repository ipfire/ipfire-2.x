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

core=166

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Remove files
rm -vf \
	/etc/dracut.conf \
	/opt/pakfire/pakfire-2007.key \
	/usr/bin/mkinitrd \
	/usr/lib/dracut \
	/usr/local/bin/ovpn-ccd-convert \
	/usr/local/bin/rebuild-initrd

# Delete old 2007 Pakfire key from GPG keyring
export GNUPGHOME="/opt/pakfire/etc/.gnupg"
gpg --batch --yes --delete-keys 179740DC4D8C47DC63C099C74BDE364C64D96617
unset GNUPGHOME

# Stop services

# Extract files
extract_files

# update linker config
ldconfig

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# Regenerate all initrds
dracut --regenerate-all --force

# Rebuild IPS rules
perl -e "require '/var/ipfire/ids-functions.pl'; &IDS::oinkmaster();"
/etc/init.d/suricata reload

# Start services
/etc/init.d/apache restart
/etc/init.d/sshd restart

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
