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
# Copyright (C) 2023 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

core=182

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Stop services
/etc/rc.d/init.d/ipsec stop
/etc/rc.d/init.d/squid stop
/etc/rc.d/init.d/unbound stop
/etc/rc.d/init.d/sshd stop

KVER="xxxKVERxxx"

# Backup uEnv.txt if exist
if [ -e /boot/uEnv.txt ]; then
    cp -vf /boot/uEnv.txt /boot/uEnv.txt.org
fi

# Extract files
extract_files

# Remove files
rm -rvf \
	/lib/firmware/cxgb4/t4fw-1.27.3* \
	/lib/firmware/cxgb4/t5fw-1.27.3* \
	/lib/firmware/cxgb4/t6fw-1.27.3* \
	/lib/firmware/ctefx.bin \
	/lib/firmware/ctspeq.bin \
	/lib/firmware/intel/ibt-* \
	/lib/firmware/mediatek/BT_RAM_CODE_* \
	/lib/firmware/nxp \
	/lib/udev/accelerometer \
	/lib/udev/devices \
	/lib/udev/kpartx_id \
	/lib/udev/udevd \
	/lib/udev/rules.d/42-usb-hid-pm.rules \
	/lib/udev/rules.d/50-firmware.rules \
	/lib/udev/rules.d/60-keyboard.rules \
	/lib/udev/rules.d/60-persistent-serial.rules \
	/lib/udev/rules.d/61-accelerometer.rules \
	/lib/udev/rules.d/64-xfs.rules \
	/lib/udev/rules.d/75-tty-description.rules \
	/lib/udev/rules.d/95-udev-late.rules \
	/usr/bin/gawk-5.2*

# update linker config
ldconfig

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# Apply local configuration to sshd_config
/usr/local/bin/sshctrl

# Start services
/etc/init.d/unbound start
if grep -q "ENABLE_SSH=on" /var/ipfire/remote/settings; then
	/etc/init.d/sshd start
fi
if [ -f /var/ipfire/proxy/enable ]; then
	/etc/init.d/squid start
fi
if grep -q "ENABLED=on" /var/ipfire/vpn/settings; then
	/etc/rc.d/init.d/ipsec start
fi

# Change deprecated option in tor configuration file if in usage
if pgrep tor >/dev/null; then
	sed -i 's/ExitNode /ExitNodes /g' /var/ipfire/tor/torrc
	/usr/local/bin/torctrl restart >/dev/null
else
	sed -i 's/ExitNode /ExitNodes /g' /var/ipfire/tor/torrc
fi

# Rebuild initial ramdisks
dracut --regenerate-all --force
KVER="xxxKVERxxx"
case "$(uname -m)" in
	aarch64)
		mkimage -A arm64 -T ramdisk -C lzma -d /boot/initramfs-${KVER}-ipfire.img /boot/uInit-${KVER}-ipfire
		# dont remove initramfs because grub need this to boot.
		;;
esac

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
