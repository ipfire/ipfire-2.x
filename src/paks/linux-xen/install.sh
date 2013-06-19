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
# Copyright (C) 2010 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
extract_files
#
KVER=2.6.32.61
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
#
# backup grub.conf
#
cp /boot/grub/grub.conf /boot/grub/grub-backup-$KVER-xen.conf
#
# Add new Entry to grub.conf
#
echo "" >> /boot/grub/grub.conf
echo "title IPFire (legacy XEN-Kernel $KVER)" >> /boot/grub/grub.conf
echo "  kernel /vmlinuz-$KVER-ipfire-xen root=$ROOT panic=10 console=xvc0 $MOUNT" >> /boot/grub/grub.conf
echo "  initrd /ipfirerd-$KVER-xen.img" >> /boot/grub/grub.conf
echo "# savedefault $ENTRY" >> /boot/grub/grub.conf
#
# Test if we running already on xen
#
uname -r | grep "ipfire-xen";
if [ ${?} = 0 ]; then
	#Xen Kernel is active
	#Set grub default entry to this kernel
	sed -i -e "s|^default .*|default $ENTRY|g" /boot/grub/grub.conf
	#Remove ramdisk of normal kernel (not enough space)
	rm -f /boot/ipfirerd-$KVER.img
else
	#Normal Kernel
	#pygrub crash with "default saved"
	sed -i -e "s|^default saved|#default saved|g" /boot/grub/grub.conf
fi
#
# Made initramdisk
#
/sbin/dracut --force --verbose /boot/ipfirerd-$KVER-xen.img $KVER-ipfire-xen
#
# Create new module depency
#
depmod -a $KVER-ipfire-xen
