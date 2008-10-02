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
KVER=2.6.25.17
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
cp /boot/grub/grub.conf /boot/grub/grub-backup-$KVER.conf
#
# Add new Entry to grub.conf
#
echo "" >> /boot/grub/grub.conf
echo "title IPFire alternative Kernel:$KVER" >> /boot/grub/grub.conf
echo "  root (hd0,0)" >> /boot/grub/grub.conf
echo "  kernel /vmlinuz-$KVER-ipfire root=$ROOT rootdelay=10 panic=10 $MOUNT" >> /boot/grub/grub.conf
echo "  initrd /ipfirerd-$KVER.img" >> /boot/grub/grub.conf
echo "  savedefault $ENTRY" >> /boot/grub/grub.conf
#
# Made initramdisk
#
mkinitcpio -k $KVER-ipfire -g /boot/ipfirerd-$KVER.img
#
# ReInstall grub
#
grub-install --no-floppy ${ROOT::`expr length $ROOT`-1}
#
# Create new module depency
#
depmod -a $KVER-ipfire

