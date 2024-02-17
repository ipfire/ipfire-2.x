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
# Copyright (C) 2024 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

core=185

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Stop services
/etc/init.d/ntp stop

# Extract files
extract_files

# Remove files
rm -rvf \
	/lib/firmware/ath10k/WCN3990/hw1.0/notice.txt_wlanmdsp \
	/lib/firmware/ath11k/IPQ6018/hw1.0/Notice.txt \
	/lib/firmware/ath11k/IPQ8074/hw2.0/Notice.txt \
	/lib/firmware/ath11k/QCA6390/hw2.0/Notice.txt \
	/lib/firmware/ath11k/QCN9074/hw1.0/Notice.txt \
	/lib/firmware/ath11k/WCN6855/hw2.0/Notice.txt \
	/lib/firmware/intel-ucode/06-86-04 \
	/lib/firmware/intel-ucode/06-86-05

# update linker config
ldconfig

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# Apply local configuration to sshd_config
/usr/local/bin/sshctrl

# Fix permissions of /etc/sudoers.d/
chmod -v 750 /etc/sudoers.d
chmod -v 640 /etc/sudoers.d/*

# Start services
telinit u
/etc/init.d/suricata restart
/etc/init.d/unbound restart
/etc/init.d/ntp start

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
