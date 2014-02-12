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
# Copyright (C) 2007-2013 IPFire-Team <info@ipfire.org>.                   #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
extract_files
#
KVER=xxxKVERxxx
ROOT=`mount | grep " / " | cut -d" " -f1`
ROOTUUID=`blkid -c /dev/null -sUUID $ROOT | cut -d'"' -f2`
if [ ! -z $ROOTUUID ]; then
	ROOT="UUID=$ROOTUUID"
fi

MOUNT=`grep "kernel" /boot/grub/grub.conf | tail -n 1`
# Nur den letzten Parameter verwenden
echo $MOUNT > /dev/null
MOUNT=$_
if [ ! $MOUNT == "rw" ]; then
	MOUNT="ro"
fi

ENTRY=`grep "savedefault" /boot/grub/grub.conf | tail -n 1`
# Nur den letzten Parameter verwenden
echo $ENTRY > /dev/null
let ENTRY=$_+1

#Check if the system use serial console...
if [ "$(grep "^serial" /boot/grub/grub.conf)" == "" ]; then
	console=""
else
	console=" console=ttyS0,115200n8"
fi

#
# backup grub.conf
#
cp /boot/grub/grub.conf /boot/grub/grub-backup-$KVER-pae_install.conf
#
# Add new Entry to grub.conf
#
echo "" >> /boot/grub/grub.conf
echo "title IPFire (PAE-Kernel)" >> /boot/grub/grub.conf
echo "  kernel /vmlinuz-$KVER-ipfire-pae root=$ROOT panic=10$console $MOUNT" >> /boot/grub/grub.conf
echo "  initrd /ipfirerd-$KVER-pae.img" >> /boot/grub/grub.conf
echo "  savedefault $ENTRY" >> /boot/grub/grub.conf
#
# Create new module depency
#
depmod -a $KVER-ipfire-pae
#
# Made initramdisk
#
/sbin/dracut --force --verbose /boot/ipfirerd-$KVER-pae.img $KVER-ipfire-pae

# Default pae and request a reboot if pae is supported
if [ ! "$(grep "^flags.* pae " /proc/cpuinfo)" == "" ]; then
	grub-set-default $ENTRY
	touch /var/run/need_reboot
fi
sync && sync