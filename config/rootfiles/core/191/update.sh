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

core=191

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Stop services
/etci/init.d/squid stop

# Extract files
extract_files

# Remove any entry for FEODO_IP or FEODO_AGGRESSIVE from the ipblocklist
# modified file and the associated ipblocklist files from the /var/lib/ipblocklist directory
sed -i '/FEODO_IP=/d' /var/ipfire/ipblocklist/modified
sed -i '/FEODO_AGGRESSIVE=/d' /var/ipfire/ipblocklist/modified
if [ -e /var/lib/ipblocklist/FEODO_IP.conf ]; then
	rm /var/lib/ipblocklist/FEODO_IP.conf
fi
if [ -e /var/lib/ipblocklist/FEODO_AGGRESSIVE.conf ]; then
	rm /var/lib/ipblocklist/FEODO_AGGRESSIVE.conf
fi

# move elinks config to new dir
if [ -e /root/.elinks/* ]; then
	mv /root/.elinks/* /root/.config/elinks/
	rm -rf /root/.elinks
fi

# Remove files

# update linker config
ldconfig

# run depmod with new kmod version
depmod -a 6.6.63-ipfire

# restart init
telinit u

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# Apply local configuration to sshd_config
/usr/local/bin/sshctrl

# Start services
/etc/init.d/sshd restart
/etc/init.d/unbound restart
/etc/init.d/suricata restart
/etc/init.d/squid start

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
