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
# Copyright (C) 2015 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

# Remove old core updates from pakfire cache to save space...
core=96
for (( i=1; i<=$core; i++ ))
do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Stop services
/etc/init.d/fcron stop
/etc/init.d/collectd stop
/usr/local/bin/qosctrl stop

# Backup RRDs
if [ -d "/var/log/rrd.bak" ]; then
	# Umount ramdisk
	umount -l "/var/log/rrd"
	rm -rf "/var/log/rrd"

	mv "/var/log/rrd.bak/vnstat" "/var/log/vnstat"
	mv "/var/log/rrd.bak" "/var/log/rrd"
fi

# Remove old scripts
rm -f /etc/rc.d/init.d/tmpfs \
	/etc/rc.d/rc0.d/K85tmpfs \
	/etc/rc.d/rc3.d/S01tmpfs \
	/etc/rc.d/rc6.d/K85tmpfs

# Extract files
extract_files

# Update Language cache
/usr/local/bin/update-lang-cache

# Remove Ramdisk entry from fstab
sed -i -e "s|^none\s/var/log/rrd.*||g" /etc/fstab

# Keep (almost) old ramdisk behaviour
if [ ! -e "/etc/sysconfig/ramdisk" ]; then
	echo "RAMDISK_MODE=2" > /etc/sysconfig/ramdisk
fi

if [ -L "/var/spool/cron" ]; then
	rm -f /var/spool/cron
	mv /var/log/rrd/cron /var/spool/cron
	chown cron:cron /var/spool/cron

	# Add new crontab entries
	sed -i /var/spool/cron/root.orig -e "/tmpfs backup/d"
	grep -q "collectd backup" /var/spool/cron/root.orig || cat <<EOF >> /var/spool/cron/root.orig
# Backup ramdisks if necessary
%nightly,random * 23-4  /etc/init.d/collectd backup &>/dev/null
%nightly,random * 23-4  /etc/init.d/vnstat backup &>/dev/null
EOF
	fcrontab -z
fi

# Start services
/etc/init.d/collectd start
/etc/init.d/vnstat start
/etc/init.d/fcron start
/etc/init.d/dnsmasq restart
/usr/local/bin/qosctrl start

# Disable loading of cryptodev
sed -e "s/^cryptodev/# &/g" -i /etc/sysconfig/modules

# This update need a reboot...
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
