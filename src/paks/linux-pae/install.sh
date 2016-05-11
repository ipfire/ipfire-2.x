#!/bin/bash
############################################################################
#                                                                          #
# This file is part of the IPFire Firewall.                                #
#                                                                          #
# IPFire is free software; you can redistribute it and/or modify           #
# it under the terms of the GNU General Public License as published by     #
# the Free Software Foundation; either version 2 of the License, or        #
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
# Copyright (C) 2007-2016 IPFire-Team <info@ipfire.org>.                   #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh


function find_partition() {
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
	echo ${root}
	return 0
}

if [ "$(grep "^flags.* pae " /proc/cpuinfo)" == "" ]; then
	rm -f /opt/pakfire/db/installed/meta-linux-pae
	/usr/bin/logger -p syslog.emerg -i pakfire \
		"linux-pae: no pae support found, aborted!"
	exit 1
fi

extract_files
#
KVER=xxxKVERxxx
ROOT=`find_partition /`
#
# Create new module depency
#
depmod -a $KVER-ipfire-pae
#
# Made initramdisk
#
/usr/bin/dracut --force --xz /boot/initramfs-$KVER-ipfire-pae.img $KVER-ipfire-pae  

if [ -e /boot/grub/grub.cfg ]; then
	#
	# Update grub2 config
	#
	grub-mkconfig > /boot/grub/grub.cfg
else
	#
	# xen pv with pygrub need grub.conf / menu.lst
	#
	echo "timeout 10"                          > /boot/grub/grub.conf
	echo "default 0"                          >> /boot/grub/grub.conf
	echo "title IPFire (pae-kernel)"          >> /boot/grub/grub.conf
	echo "  root (hd0)"		          >> /boot/grub/grub.conf
	echo "  kernel /vmlinuz-$KVER-ipfire-pae root=/dev/$ROOT rootdelay=10 panic=10 console=hvc0" \
						  >> /boot/grub/grub.conf
	echo "  initrd /initramfs-$KVER-ipfire-pae.img" >> /boot/grub/grub.conf
	echo "# savedefault 0"			  >> /boot/grub/grub.conf
	ln -s grub.conf $MNThdd/boot/grub/menu.lst
fi

# request a reboot
touch /var/run/need_reboot
sync && sync