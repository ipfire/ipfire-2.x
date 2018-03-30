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
# Copyright (C) 2017 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

core=119

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Stop services
ipsec stop

# Remove old files
rm -vf \
	/sbin/capiinit \
	/usr/bin/capiinfo \
	/usr/lib/libcapi20* \
	/usr/bin/isdn_text2wireshark \
	/usr/bin/l1oipctrl \
	/usr/bin/msidn_* \
	/usr/lib/libmisdn* \
	/usr/sbin/misdn_* \
	/etc/rc.d/init.d/mISDN \
	/usr/lib/libwrap* \
	/lib/security/pam_mysql.so

# Extract files
extract_files

# update linker config
ldconfig

# restart init
telinit u

# Update Language cache
/usr/local/bin/update-lang-cache

# remove dropped packages
for package in lcr perl-DBD-mysql mysql; do
	if [ -e /opt/pakfire/db/installed/meta-$package ]; then
		pakfire remove -y $package
	fi
	rm -f /opt/pakfire/db/installed/meta-$package
	rm -f /opt/pakfire/db/meta/meta-$package
	rm -f /opt/pakfire/db/rootfiles/$package
done

# Remove more old files
rm -vf \
	/usr/lib/libmysqlclient* \
	/usr/lib/mysql

# Start services
/etc/init.d/apache reload

# Regenerate IPsec configuration
sudo -u nobody /srv/web/ipfire/cgi-bin/vpnmain.cgi
if grep -q "ENABLED=on" /var/ipfire/vpn/settings; then
	/etc/init.d/ipsec restart
fi

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
