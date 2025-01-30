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

core=192

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
/etc/rc.d/init.d/collectd stop

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

# Check diskspace on root and size of boot
ROOTSPACE=$( df / -Pk | sed "s| * | |g" | cut -d" " -f4 | tail -n 1 )
if [ $ROOTSPACE -lt 200000 ]; then
    exit_with_error "ERROR cannot update because not enough free space on root." 2
fi
BOOTSIZE=$( df /boot -Pk | sed "s| * | |g" | cut -d" " -f2 | tail -n 1 )
if [ $BOOTSIZE -lt 100000 ]; then
    exit_with_error "ERROR cannot update. BOOT partition is to small." 3
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

# remove old pppd libs
rm -rvf \
	/usr/lib/pppd

# Extract files
extract_files

# Remove the old version of zlib
rm -rfv \
	/lib/libz.so.1.3.1

# update linker config
ldconfig

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# Create collectd 4.x to 5.x migration script from rrd contents, run the script that
# was created and then remove the old interface directory if it is present as it will
# be empty after the migration has been carried out.
for i in $(seq 0 63);
do
	if [ -e /var/log/rrd/collectd/localhost/cpufreq/cpufreq-$i.rrd ]; then
		mkdir -p /var/log/rrd/collectd/localhost/cpufreq-$i
		mv -f /var/log/rrd/collectd/localhost/cpufreq/cpufreq-$i.rrd \
			/var/log/rrd/collectd/localhost/cpufreq-$i/cpufreq.rrd
	fi
done
if [ -e /var/log/rrd/collectd/localhost/thermal-thermal_zone*/temperature-temperature.rrd ]; then
	mv -f /var/log/rrd/collectd/localhost/thermal-thermal_zone*/temperature-temperature.rrd \
		/var/log/rrd/collectd/localhost/thermal-thermal_zone*/temperature.rrd
fi
/var/ipfire/collectd-migrate-4-to-5.pl --indir /var/log/rrd/ > /tmp/rrd-migrate.sh
sh /tmp/rrd-migrate.sh >/dev/null 2>&1
rm -rvf \
	/var/log/rrd/collectd/localhost/cpufreq \
	/var/log/rrd/collectd/localhost/disk-loop* \
	/var/log/rrd/collectd/localhost/disk-sg* \
	/var/log/rrd/collectd/localhost/disk-sr* \
	/var/log/rrd/collectd/localhost/disk-ram* \
	/var/log/rrd/collectd/localhost/interface \
	/var/log/rrd/collectd/localhost/thermal-cooling_device*

# Start services
/etc/init.d/collectd start
/etc/init.d/suricata restart

# Build initial ramdisks
dracut --regenerate-all --force
KVER="xxxKVERxxx"
case "$(uname -m)" in
	aarch64)
		mkimage -A arm64 -T ramdisk -C lzma -d /boot/initramfs-${KVER}.img /boot/uInit-${KVER}
		# dont remove initramfs because grub need this to boot.
		;;
esac

# Upadate Kernel version in uEnv.txt
if [ -e /boot/uEnv.txt ]; then
    sed -i -e "s/KVER=.*/KVER=${KVER}/g" /boot/uEnv.txt
fi

# Call user update script (needed for some ARM boards)
if [ -e /boot/pakfire-kernel-update ]; then
    /boot/pakfire-kernel-update ${KVER}
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
