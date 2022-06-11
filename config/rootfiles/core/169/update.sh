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

core=169

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

# Stop services
/etc/init.d/unbound stop
/etc/init.d/squid stop
/etc/init.d/apache stop

KVER="xxxKVERxxx"

# Backup uEnv.txt if exist
if [ -e /boot/uEnv.txt ]; then
    cp -vf /boot/uEnv.txt /boot/uEnv.txt.org
fi

# Do some sanity checks prior to the kernel update
case $(uname -r) in
    *-ipfire*)
	# Ok.
	;;
    *)
	exit_with_error "ERROR cannot update. No IPFire Kernel." 1
	;;
esac

# Check diskspace on root
ROOTSPACE=`df / -Pk | sed "s| * | |g" | cut -d" " -f4 | tail -n 1`

if [ $ROOTSPACE -lt 100000 ]; then
    exit_with_error "ERROR cannot update because not enough free space on root." 2
    exit 2
fi

# Remove the old kernel
rm -rvf \
	/boot/System.map-* \
	/boot/config-* \
	/boot/ipfirerd-* \
	/boot/initramfs-* \
	/boot/vmlinuz-* \
	/boot/uImage-* \
	/boot/zImage-* \
	/boot/uInit-* \
	/boot/dtb-* \
	/lib/modules

# Remove files
rm -rvf \
	/lib/firmware/ath10k/QCA99X0/hw2.0/board.bin \
	/lib/firmware/intel/ice/ddp/ice-1.3.26.0.pkg \
	/lib/firmware/iwlwifi-3160-10.ucode \
	/lib/firmware/iwlwifi-3160-12.ucode \
	/lib/firmware/iwlwifi-3160-13.ucode \
	/lib/firmware/iwlwifi-3160-16.ucode \
	/lib/firmware/iwlwifi-3160-7.ucode \
	/lib/firmware/iwlwifi-3160-8.ucode \
	/lib/firmware/iwlwifi-3160-9.ucode \
	/lib/firmware/iwlwifi-3168-21.ucode \
	/lib/firmware/iwlwifi-7260-10.ucode \
	/lib/firmware/iwlwifi-7260-12.ucode \
	/lib/firmware/iwlwifi-7260-13.ucode \
	/lib/firmware/iwlwifi-7260-16.ucode \
	/lib/firmware/iwlwifi-7260-7.ucode \
	/lib/firmware/iwlwifi-7260-8.ucode \
	/lib/firmware/iwlwifi-7260-9.ucode \
	/lib/firmware/iwlwifi-7265-10.ucode \
	/lib/firmware/iwlwifi-7265-12.ucode \
	/lib/firmware/iwlwifi-7265-13.ucode \
	/lib/firmware/iwlwifi-7265-16.ucode \
	/lib/firmware/iwlwifi-7265-8.ucode \
	/lib/firmware/iwlwifi-7265-9.ucode \
	/lib/firmware/iwlwifi-7265D-10.ucode \
	/lib/firmware/iwlwifi-7265D-12.ucode \
	/lib/firmware/iwlwifi-7265D-13.ucode \
	/lib/firmware/iwlwifi-7265D-16.ucode \
	/lib/firmware/iwlwifi-7265D-17.ucode \
	/lib/firmware/iwlwifi-7265D-21.ucode \
	/lib/firmware/iwlwifi-8000C-13.ucode \
	/lib/firmware/iwlwifi-8000C-16.ucode \
	/lib/firmware/iwlwifi-8000C-21.ucode \
	/lib/firmware/iwlwifi-8265-21.ucode \
	/lib/libxtables.so.12.4.0 \
	/lib/xtables/libip6t_DNAT.so \
	/lib/xtables/libip6t_REDIRECT.so \
	/lib/xtables/libipt_DNAT.so \
	/lib/xtables/libipt_REDIRECT.so \
	/usr/lib/libfuse3.so.3.10.4 \
	/usr/lib/libunbound.so.8.1.14
	/usr/lib/libxml2.so.2.9.12 \
	/usr/lib/libxslt.so.1.1.34 \
	/usr/lib/libyang.so.2.1.4

# Extract files
extract_files

# update linker config
ldconfig

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# Apply sysctl changes
/etc/init.d/sysctl start

# Start services
telinit u
/etc/init.d/firewall restart
/etc/init.d/apache start
/etc/init.d/unbound start
/etc/init.d/squid start

# This update needs a reboot...
touch /var/run/need_reboot

# Finish
/etc/init.d/fireinfo start
sendprofile

# remove lm_sensor config after collectd was started
# to reserch sensors at next boot with updated kernel
rm -f  /etc/sysconfig/lm_sensors

# Upadate Kernel version in uEnv.txt
if [ -e /boot/uEnv.txt ]; then
    sed -i -e "s/KVER=.*/KVER=${KVER}/g" /boot/uEnv.txt
fi

# Call user update script (needed for some ARM boards)
if [ -e /boot/pakfire-kernel-update ]; then
    /boot/pakfire-kernel-update ${KVER}
fi

# Update grub config to display new core version
if [ -e /boot/grub/grub.cfg ]; then
	grub-mkconfig -o /boot/grub/grub.cfg
fi

sync

# Don't report the exitcode last command
exit 0
