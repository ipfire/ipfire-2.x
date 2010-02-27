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
# Copyright (C) 2007 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
extract_files
#
KVER=2.6.32.9
ROOT=`grep "root=" /boot/grub/grub.conf | cut -d"=" -f2 | cut -d" " -f1 | tail -n 1`
MOUNT=`grep "kernel" /boot/grub/grub.conf | tail -n 1`
# Nur den letzten Parameter verwenden
echo $MOUNT > /dev/null
MOUNT=$_
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
echo "title IPFire (XEN-Kernel)" >> /boot/grub/grub.conf
echo "  kernel /vmlinuz-$KVER-ipfire-xen root=$ROOT rootdelay=10 panic=10 console=xvc0 $MOUNT" >> /boot/grub/grub.conf
echo "  initrd /ipfirerd-$KVER-xen.img" >> /boot/grub/grub.conf
echo "# savedefault $ENTRY" >> /boot/grub/grub.conf
#
# Test if we running already on xen
#
uname -r | grep "ipfire-xen";
if [ ${?} = 0 ]; then
	#Xen Kernel is active
	#Set grub default entry to this kernel
	sed -i -e "s|^default saved|default $ENTRY|g" /boot/grub/grub.conf
else
	#Normal Kernel
	#pygrub crash with "default saved"
	sed -i -e "s|^default saved|#default saved|g" /boot/grub/grub.conf
fi
#
# Made initramdisk
#
cp -f /etc/mkinitcpio.conf.org /etc/mkinitcpio.conf
sed -i -e "s| autodetect | |g" /etc/mkinitcpio.conf
mkinitcpio -k $KVER-ipfire-xen -g /boot/ipfirerd-$KVER-xen.img
#
# Create new module depency
#
depmod -a $KVER-ipfire-xen
