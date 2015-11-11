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


function find_device() {
	local mountpoint="${1}"

	local root
	local dev mp fs flags rest
	while read -r dev mp fs flags rest; do
		# Skip unwanted entries
		[ "${dev}" = "rootfs" ] && continue

		if [ "${mp}" = "${mountpoint}" ] && [ -b "${dev}" ]; then
			root="$(basename "${dev}")"
			break
		fi
	done < /proc/mounts

	# Get the actual device from the partition that holds /
	while [ -n "${root}" ]; do
		if [ -e "/sys/block/${root}" ]; then
			echo "${root}"
			return 0
		fi

		# Remove last character
		root="${root::-1}"
	done

	return 1
}


#
# Remove old core updates from pakfire cache to save space...
core=95
for (( i=1; i<=$core; i++ ))
do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

#
# Do some sanity checks.
case $(uname -r) in
	*-ipfire-versatile )
		/usr/bin/logger -p syslog.emerg -t ipfire \
			"core-update-${core}: ERROR cannot update. versatile support is dropped."
		# Report no error to pakfire. So it does not try to install it again.
		exit 0
		;;
	*-ipfire* )
		# Ok.
		;;
	* )
		/usr/bin/logger -p syslog.emerg -t ipfire \
			"core-update-${core}: ERROR cannot update. No IPFire Kernel."
		exit 1
	;;
esac


#
#
KVER="xxxKVERxxx"

# Check diskspace on root
ROOTSPACE=`df / -Pk | sed "s| * | |g" | cut -d" " -f4 | tail -n 1`

if [ $ROOTSPACE -lt 100000 ]; then
	/usr/bin/logger -p syslog.emerg -t ipfire \
		"core-update-${core}: ERROR cannot update because not enough free space on root."
	exit 2
fi


echo
echo Update Kernel to $KVER ...
#
# Remove old kernel, configs, initrd, modules, dtb's ...
#
rm -rf /boot/System.map-*
rm -rf /boot/config-*
rm -rf /boot/ipfirerd-*
rm -rf /boot/initramfs-*
rm -rf /boot/vmlinuz-*
rm -rf /boot/uImage-ipfire-*
rm -rf /boot/uInit-ipfire-*
rm -rf /boot/dtb-*-ipfire-*
rm -rf /lib/modules

case "$(uname -m)" in
	armv*)
		# Backup uEnv.txt if exist
		if [ -e /boot/uEnv.txt ]; then
			cp -vf /boot/uEnv.txt /boot/uEnv.txt.org
		fi

		# work around the u-boot folder detection bug
		mkdir -pv /boot/dtb-$KVER-ipfire-kirkwood
		mkdir -pv /boot/dtb-$KVER-ipfire-multi
		;;
esac

# Remove files
rm -f /etc/rc.d/init.d/network-vlans
rm -f /etc/rc.d/rcsysinit.d/S91network-vlans

#
#Stop services
/etc/init.d/snort stop
/etc/init.d/squid stop
/etc/init.d/ipsec stop
/etc/init.d/ntp stop
/etc/init.d/apache stop

#
#Extract files
tar xavf /opt/pakfire/tmp/files* --no-overwrite-dir -p --numeric-owner -C /

# Check diskspace on boot
BOOTSPACE=`df /boot -Pk | sed "s| * | |g" | cut -d" " -f4 | tail -n 1`

if [ $BOOTSPACE -lt 1000 ]; then
	case $(uname -r) in
		*-ipfire-kirkwood )
			# Special handling for old kirkwood images.
			# (install only kirkwood kernel)
			rm -rf /boot/*
			# work around the u-boot folder detection bug
			mkdir -pv /boot/dtb-$KVER-ipfire-kirkwood
			tar xavf /opt/pakfire/tmp/files* --no-overwrite-dir -p \
				--numeric-owner -C / --wildcards 'boot/*-kirkwood*'
			;;
		* )
			/usr/bin/logger -p syslog.emerg -t ipfire \
				"core-update-${core}: FATAL-ERROR space run out on boot. System is not bootable..."
			/etc/init.d/apache start
			exit 4
			;;
	esac
fi

# Regenerate IPsec configuration
sudo -u nobody /srv/web/ipfire/cgi-bin/vpnmain.cgi

# Update Language cache
/usr/local/bin/update-lang-cache

#
# Start services
#
/etc/init.d/apache start
/etc/init.d/ntp start
/etc/init.d/squid start
/etc/init.d/snort start
if [ `grep "ENABLED=on" /var/ipfire/vpn/settings` ]; then
	/etc/init.d/ipsec start
fi

if [ -e /boot/grub/grub.cfg ]; then
		grub-mkconfig > /boot/grub/grub.cfg
fi

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
		if [ ! "$(grep "^flags.* pae " /proc/cpuinfo)" == "" ]; then
			ROOTSPACE=`df / -Pk | sed "s| * | |g" | cut -d" " -f4 | tail -n 1`
			BOOTSPACE=`df /boot -Pk | sed "s| * | |g" | cut -d" " -f4 | tail -n 1`
			if [ $BOOTSPACE -lt 12000 -o $ROOTSPACE -lt 90000 ]; then
				/usr/bin/logger -p syslog.emerg -t ipfire \
				"core-update-${core}: WARNING not enough space for pae kernel."
			else
				echo "Name: linux-pae" > /opt/pakfire/db/installed/meta-linux-pae
				echo "ProgVersion: 0" >> /opt/pakfire/db/installed/meta-linux-pae
				echo "Release: 0"     >> /opt/pakfire/db/installed/meta-linux-pae
			fi
		fi
		;;
esac
#
# After pakfire has ended run it again and update the lists and do upgrade
#
echo '#!/bin/bash'                                        >  /tmp/pak_update
echo 'while [ "$(ps -A | grep " update.sh")" != "" ]; do' >> /tmp/pak_update
echo '    sleep 1'                                        >> /tmp/pak_update
echo 'done'                                               >> /tmp/pak_update
echo 'while [ "$(ps -A | grep " pakfire")" != "" ]; do'   >> /tmp/pak_update
echo '    sleep 1'                                        >> /tmp/pak_update
echo 'done'                                               >> /tmp/pak_update
echo '/opt/pakfire/pakfire update -y --force'             >> /tmp/pak_update
echo '/opt/pakfire/pakfire upgrade -y'                    >> /tmp/pak_update
echo '/opt/pakfire/pakfire upgrade -y'                    >> /tmp/pak_update
echo '/opt/pakfire/pakfire upgrade -y'                    >> /tmp/pak_update
echo '/usr/bin/logger -p syslog.emerg -t ipfire "Core-upgrade finished. If you use a customized grub/uboot config"' >> /tmp/pak_update
echo '/usr/bin/logger -p syslog.emerg -t ipfire "Check it before reboot !!!"' >> /tmp/pak_update
echo '/usr/bin/logger -p syslog.emerg -t ipfire " *** Please reboot... *** "' >> /tmp/pak_update
echo 'touch /var/run/need_reboot ' >> /tmp/pak_update
#
killall -KILL pak_update
chmod +x /tmp/pak_update
/tmp/pak_update &

sync

#
#Finish
/etc/init.d/fireinfo start
sendprofile
# Update grub config to display new core version
if [ -e /boot/grub/grub.cfg ]; then
	grub-mkconfig -o /boot/grub/grub.cfg
fi
sync

echo
echo Please wait until pakfire has ended...
echo

# Don't report the exitcode last command
exit 0
