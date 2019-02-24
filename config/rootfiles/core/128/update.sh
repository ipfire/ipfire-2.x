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
# Copyright (C) 2018 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

core=128

exit_with_error() {
	# Set last succesfull installed core.
	echo $(($core-1)) > /opt/pakfire/db/core/mine
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

# Check diskspace on root
ROOTSPACE=`df / -Pk | sed "s| * | |g" | cut -d" " -f4 | tail -n 1`

if [ $ROOTSPACE -lt 80000 ]; then
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
rm -f  /etc/sysconfig/lm_sensors

# Stop services
/etc/init.d/apache stop

# Remove files
rm -rvf \
	/usr/lib{,/sse2}/libcrypto.so.10 \
	/usr/lib{,/sse2}/libssl.so.10 \
	/usr/lib/openssl/engines \
	/home/nobody/.rnd \
	/var/ipfire/ovpn/ca/.rnd \
	/var/tmp/.rnd \
	/.rnd \
	/root/.rnd

# Extract files
extract_files

# update linker config
ldconfig

# Update Language cache
/usr/local/bin/update-lang-cache

# Reload sysctl.conf
sysctl -p

# Apply local configuration to sshd_config
/usr/local/bin/sshctrl

# Start services
if grep -q "ENABLED=on" /var/ipfire/vpn/settings; then
	/etc/init.d/ipsec restart
fi
/etc/init.d/sshd restart
/etc/init.d/apache start
/etc/init.d/unbound restart

# Upadate Kernel version uEnv.txt
if [ -e /boot/uEnv.txt ]; then
	sed -i -e "s/KVER=.*/KVER=${KVER}/g" /boot/uEnv.txt
fi

# call user update script (needed for some arm boards)
if [ -e /boot/pakfire-kernel-update ]; then
	/boot/pakfire-kernel-update ${KVER}
fi

case "$(uname -m)" in
	i?86)
		# Force (re)install pae kernel if pae is supported
		rm -rf /opt/pakfire/db/installed/meta-linux-pae
		rm -rf /opt/pakfire/db/rootfiles/linux-pae
		if [ ! "$(grep "^flags.* pae " /proc/cpuinfo)" == "" ]; then
			ROOTSPACE=`df / -Pk | sed "s| * | |g" | cut -d" " -f4 | tail -n 1`
			BOOTSPACE=`df /boot -Pk | sed "s| * | |g" | cut -d" " -f4 | tail -n 1`
			if [ $BOOTSPACE -lt 22000 -o $ROOTSPACE -lt 120000 ]; then
				/usr/bin/logger -p syslog.emerg -t ipfire \
				"core-update-${core}: WARNING not enough space for pae kernel."
				touch /var/run/need_reboot
			else
				echo "Name: linux-pae" > /opt/pakfire/db/installed/meta-linux-pae
				echo "ProgVersion: 0" >> /opt/pakfire/db/installed/meta-linux-pae
				echo "Release: 0"     >> /opt/pakfire/db/installed/meta-linux-pae
			fi
		else
			touch /var/run/need_reboot
		fi
		;;
	*)
		# This update needs a reboot...
		touch /var/run/need_reboot
		;;
esac

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
