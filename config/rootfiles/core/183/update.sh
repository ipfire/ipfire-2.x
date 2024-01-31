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

core=183

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
/etc/rc.d/init.d/apache stop
/etc/rc.d/init.d/sshd stop

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

# Extract files
extract_files

# Remove files
rm -rvf \
	/etc/fonts/conf.d/10-sub-pixel-rgb.conf \
	/srv/web/ipfire/html/themes/ipfire/images \
	/usr/lib/libbind9-9.16.44.so \
	/usr/lib/libdns-9.16.44.so \
	/usr/lib/libirs-9.16.44.so \
	/usr/lib/libisc-9.16.44.so \
	/usr/lib/libisccc-9.16.44.so \
	/usr/lib/libisccfg-9.16.44.so \
	/usr/lib/libns-9.16.44.so \
	/usr/lib/libxml2.so.2.11*

# update linker config
ldconfig

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# Relaunch init
telinit u

# Apply local configuration to sshd_config
/usr/local/bin/sshctrl

# Fix permissions of /etc/sudoers.d/
chmod -v 750 /etc/sudoers.d
chmod -v 640 /etc/sudoers.d/*

# Check apache rsa key and replace if it is too small
KEYSIZE=$(openssl rsa -in /etc/httpd/server.key -text -noout | sed -n 's/Private-Key:\ (\(.*\)\ bit.*/\1/p')
if [ $KEYSIZE \< 2048 ]; then
	echo "Generating new HTTPS RSA server key (this will take a moment)..."
	openssl genrsa -out /etc/httpd/server.key 4096 &>/dev/null
	chmod 600 /etc/httpd/server.key
	sed "s/HOSTNAME/`hostname -f`/" < /etc/certparams | \
		openssl req -new -key /etc/httpd/server.key \
			-out /etc/httpd/server.csr &>/dev/null
	openssl x509 -req -days 999999 -sha256 \
		-in /etc/httpd/server.csr \
		-signkey /etc/httpd/server.key \
		-out /etc/httpd/server.crt &>/dev/null
fi

# Start services
/etc/rc.d/init.d/apache start
if grep -q "ENABLE_SSH=on" /var/ipfire/remote/settings; then
	/etc/init.d/sshd start
fi
if grep -q "ENABLED=on" /var/ipfire/vpn/settings; then
	/etc/rc.d/init.d/ipsec start
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
	/usr/bin/install-bootloader
fi

sync

# Don't report the exitcode last command
exit 0
