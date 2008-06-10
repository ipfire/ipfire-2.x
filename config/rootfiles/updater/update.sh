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
#
OLDVERSION="2.1.1"
NEWVERSION="2.2-test"
CORE="14"
KVER="2.6.20.21"
ROOT=`grep "root=" /boot/grub/grub.conf | cut -d"=" -f2 | cut -d" " -f1 | tail -n 1`
MOUNT=`grep "kernel" /boot/grub/grub.conf | tail -n 1`
# Nur den letzten Parameter verwenden
echo $MOUNT > /dev/null
MOUNT=$_
INSTALLEDVERSION=`grep "version = " /opt/pakfire/etc/pakfire.conf | cut -d'"' -f2`
INSTALLEDCORE=`cat /opt/pakfire/db/core/mine`
#
# check version
#
if [ ! "$INSTALLEDVERSION" == "$OLDVERSION" ]; then
    echo Error! This update is only for IPfire $OLDVERSION CORE $CORE
    echo You have installed IPfire $INSTALLEDVERSION CORE $INSTALLEDCORE
    exit 1
fi
# check core
if [ ! "$INSTALLEDCORE" == "$CORE" ]; then
    echo Error! This update is only for IPfire $OLDVERSION CORE $CORE
    echo You have installed IPfire $INSTALLEDVERSION CORE $INSTALLEDCORE
    exit 2
fi
#
#
echo 
echo Update IPfire $OLDVERSION to $NEWVERSION
echo
echo Press Enter to begin.
read
echo
#
# check if we the backup file already exist
if [ -e /var/ipfire/backup/update_$OLDVERSION-$NEWVERSION.tar.bz2 ]; then
    echo Error! The backupfile of this update already exist!!!
    echo Have you already installed this update?
    exit 3
fi
echo First we made a backup of all files that was inside of the
echo update archive. This may take a while ...
tar cjvf /var/ipfire/backup/update_$OLDVERSION-$NEWVERSION.tar.bz2 \
   -T ROOTFILES --exclude='#*' -C / > /dev/null 2>&1 
echo
echo Update IPfire to $NEWVERSON ...
#
# Backup the old grub config
#
mv /boot/grub/grub.conf /boot/grub/grub-old.conf
#
# Unpack the updated files
#
echo
echo Unpack the updated files ...
tar xjvf files.ipfire -C /
# 
# Modify grub.conf
# 
echo Update grub configuration ...
sed -i "s|MOUNT|$ROOT|g" /boot/grub/grub.conf
sed -i "s|KVER|$KVER|g" /boot/grub/grub.conf
sed -i "s|MOUNT|$MOUNT|g" /boot/grub/grub.conf
echo "title Old Kernel" >> /boot/grub/grub.conf
echo "	configfile /grub/grub-old.conf" >> /boot/grub/grub.conf
#
# Made initramdisk
#
echo Create new Initramdisks ...
if [ "${ROOT:0:7}" == "/dev/sd" ]; then
    # Remove ide hook if root is on sda 
    sed -i "s| ide | |g" /etc/mkinitcpio.conf
else
if [ "${ROOT:0:7}" == "/dev/hd" ]; then
    # Remove pata hook if root is on hda 
    sed -i "s| pata | |g" /etc/mkinitcpio.conf
fi
fi
mkinitcpio -k $KVER-ipfire -g /boot/ipfirerd-$KVER.img
mkinitcpio -k $KVER-ipfire-smp -g /boot/ipfirerd-$KVER-smp.img
#
# Change version of Pakfire.conf
#
sed -i "s|$OLDVERSION|$NEWVERSION|g" /opt/pakfire/etc/pakfire.conf
echo
echo Update to IPfire $NEWVERSION finished. Please reboot...
echo
