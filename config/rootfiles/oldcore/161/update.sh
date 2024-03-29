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
# Copyright (C) 2021 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

core=161

exit_with_error() {
	# Set last succesfull installed core.
	echo $(($core-1)) > /opt/pakfire/db/core/mine
	# force fsck at next boot, this may fix free space on xfs
	touch /forcefsck
	# don't start pakfire again at error
	killall -KILL pak_update
	/usr/bin/logger -p syslog.emerg -t ipfire \
		"core-update-${core}: $1"
	exit $2
}

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

KVER="xxxKVERxxx"

# Backup uEnv.txt if exist
if [ -e /boot/uEnv.txt ]; then
	cp -vf /boot/uEnv.txt /boot/uEnv.txt.org
fi

# Do some sanity checks.
case $(uname -r) in
	*-ipfire*)
		# Ok.
		;;
	*)
		exit_with_error "ERROR cannot update. No IPFire Kernel." 1
		;;
esac
if [ -e /boot/grub/grub.conf ]; then
	exit_with_error "ERROR unsupported GRUB1/pygrub found!" 1
fi

# Check diskspace on root
ROOTSPACE=`df / -Pk | sed "s| * | |g" | cut -d" " -f4 | tail -n 1`

if [ $ROOTSPACE -lt 100000 ]; then
	exit_with_error "ERROR cannot update because not enough free space on root." 2
	exit 2
fi

# Remove the old kernel
rm -rf /boot/System.map-*
rm -rf /boot/config-*
rm -rf /boot/ipfirerd-*
rm -rf /boot/initramfs-*
rm -rf /boot/vmlinuz-*
rm -rf /boot/uImage-*-ipfire-*
rm -rf /boot/zImage-*-ipfire-*
rm -rf /boot/uInit-*-ipfire-*
rm -rf /boot/dtb-*-ipfire-*
rm -rf /lib/modules

# remove old/renamed u-boot files
rm -rf /boot/kernel*
rm -rf /usr/share/u-boot/rpi*

# Remove dropped packages
for package in client175; do
        if [ -e "/opt/pakfire/db/installed/meta-${package}" ]; then
                stop_service "${package}"
                for i in $(</opt/pakfire/db/rootfiles/${package}); do
                        rm -rfv "/${i}"
                done
        fi
        rm -f "/opt/pakfire/db/installed/meta-${package}"
        rm -f "/opt/pakfire/db/meta/meta-${package}"
        rm -f "/opt/pakfire/db/rootfiles/${package}"
done

# Remove files
rm -rf /usr/bin/python
rm -rf /usr/bin/python2
rm -rf /usr/bin/python2.7
rm -rf /usr/lib/libpython2*
rm -rf /usr/lib/python2*
rm -rf /usr/lib/collectd/python.so

# Stop services
/etc/init.d/ipsec stop

# disconnect if red is ppp0
if [ $(</var/ipfire/red/iface) = "ppp0" ]; then
	/usr/local/bin/connscheduler hangup
fi

# Extract files
extract_files

# Fix permissions just in case they broke again
chmod -v 755 \
	/usr \
	/usr/bin \
	/usr/lib \
	/usr/sbin \
	/var \
	/var/ipfire

# update linker config
ldconfig

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# restart firewall
/etc/init.d/firewall restart

# reconnect if red is ppp0
if [ $(</var/ipfire/red/iface) = "ppp0" ]; then
	/usr/local/bin/connscheduler reconnect
fi

# Start services
if grep -q "ENABLED=on" /var/ipfire/vpn/settings; then
	/etc/init.d/ipsec start
fi

# Delete orphaned shared object files
rm -rf \
       /usr/lib/pppd/2.4.8 \
       /usr/lib/itcl4.0.5 \
       /usr/lib/sqlite3.13.0 \
       /usr/lib/tcl8.4 \
       /usr/lib/tdbc1.0.4 \
       /usr/lib/tdbcmysql1.0.4 \
       /usr/lib/tdbcodbc1.0.4 \
       /usr/lib/tdbcpostgres1.0.4 \
       /usr/lib/thread2.8.0

# Generate new qos.sh
/usr/local/bin/qosctrl stop
/usr/local/bin/qosctrl generate
/usr/local/bin/qosctrl start

# remove lm_sensor config after collectd was started
# to reserch sensors at next boot with updated kernel
rm -f  /etc/sysconfig/lm_sensors

# Upadate Kernel version uEnv.txt
if [ -e /boot/uEnv.txt ]; then
	sed -i -e "s/KVER=.*/KVER=${KVER}/g" /boot/uEnv.txt
fi

# call user update script (needed for some arm boards)
if [ -e /boot/pakfire-kernel-update ]; then
	/boot/pakfire-kernel-update ${KVER}
fi

# This update needs a reboot...
touch /var/run/need_reboot

# Finish
/etc/init.d/fireinfo start
sendprofile

# Install updated grub
/usr/bin/install-bootloader

# Update grub config to display new core version
if [ -e /boot/grub/grub.cfg ]; then
	grub-mkconfig -o /boot/grub/grub.cfg
fi

sync

# Don't report the exitcode last command
exit 0
# Stop services
