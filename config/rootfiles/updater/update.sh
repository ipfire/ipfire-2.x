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
# Copyright (C) 2007 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1
#
OLDVERSION=`grep "version = " /opt/pakfire/etc/pakfire.conf | cut -d'"' -f2`
NEWVERSION="2.3"
KVER="2.6.20.21"
ROOT=`grep "root=" /boot/grub/grub.conf | cut -d"=" -f2 | cut -d" " -f1 | tail -n 1`
MOUNT=`grep "kernel" /boot/grub/grub.conf | tail -n 1`
# Nur den letzten Parameter verwenden
echo $MOUNT > /dev/null
MOUNT=$_
OLDKERNEL=`ls /boot/vmlinuz-*-ipfire | cut -d"-" -f2 | tail -n 1`
#
echo 
echo Update IPFire $OLDVERSION to $NEWVERSION
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
# Add issue and packfire conf to backup
echo etc/issue >> ROOTFILES
echo opt/pakfire/etc/pakfire.conf >> ROOTFILES
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
extract_files
# 
# Modify grub.conf
#
echo 
echo Update grub configuration ...
sed -i "s|ROOT|$ROOT|g" /boot/grub/grub.conf
sed -i "s|KVER|$KVER|g" /boot/grub/grub.conf
sed -i "s|MOUNT|$MOUNT|g" /boot/grub/grub.conf
echo "title Old Kernel" >> /boot/grub/grub.conf
echo "  configfile /grub/grub-old.conf" >> /boot/grub/grub.conf
sed -i "s|/vmlinuz-ipfire|/vmlinuz-$OLDKERNEL-ipfire|g" /boot/grub/grub-old.conf
#
# Made initramdisk
#
echo
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
#
# Create new issue
#
echo IPFire v$NEWVERSION - www.ipfire.org > /
echo =================================== >> /etc/issue
echo \\n running on \\s \\r \\m >> /etc/issue
# Core 15 begin
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
/etc/init.d/mISDN config
# Core 15 end
echo
echo
echo Update to IPFire $NEWVERSION finished. Please reboot...
echo
