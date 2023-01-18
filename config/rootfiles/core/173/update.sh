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

core=173

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
/etc/rc.d/init.d/ipsec stop
/usr/local/bin/openvpnctrl -k
/usr/local/bin/openvpnctrl -kn2n

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

# Extract files
extract_files

# update linker config
ldconfig

# Remove files
rm -rvf \
	/lib/xtables/libip6t_LOG.so \
	/lib/xtables/libip6t_MASQUERADE.so \
	/lib/xtables/libip6t_SNAT.so \
	/lib/xtables/libipt_LOG.so \
	/lib/xtables/libipt_MASQUERADE.so \
	/lib/xtables/libipt_SNAT.so

# Remove spandsp add-on, if installed
for addon in spandsp; do
	if [ -e "/opt/pakfire/db/installed/meta-${addon}" ]; then
		for i in $(</opt/pakfire/db/rootfiles/${addon}); do
			rm -rfv "/${i}"
		done
	fi
	rm -vf \
		/opt/pakfire/db/installed/meta-${addon} \
		/opt/pakfire/db/meta/meta-${addon} \
		/opt/pakfire/db/rootfiles/${addon}
done

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# Start services
if grep -q "ENABLED=on" /var/ipfire/ovpn/settings; then
	/usr/local/bin/openvpnctrl -s
	/usr/local/bin/openvpnctrl -sn2n
fi
if grep -q "ENABLED=on" /var/ipfire/vpn/settings; then
	/etc/init.d/ipsec start
fi

# Regenerate all initrds
dracut --regenerate-all --force
case "$(uname -m)" in
	armv*)
		mkimage -A arm -T ramdisk -C lzma -d /boot/initramfs-${KVER}-ipfire.img /boot/uInit-${KVER}-ipfire
		rm /boot/initramfs-${KVER}-ipfire.img
		;;
	aarch64)
		mkimage -A arm64 -T ramdisk -C lzma -d /boot/initramfs-${KVER}-ipfire.img /boot/uInit-${KVER}-ipfire
		# dont remove initramfs because grub need this to boot.
		;;
esac

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
