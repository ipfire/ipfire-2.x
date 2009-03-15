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
# Copyright (C) 2008 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1
#
KVER="2.6.25.20"
ROOT=`grep "root=" /boot/grub/grub.conf | cut -d"=" -f2 | cut -d" " -f1 | tail -n 1`
MOUNT=`grep "kernel" /boot/grub/grub.conf | tail -n 1`
# Nur den letzten Parameter verwenden
echo $MOUNT > /dev/null
MOUNT=$_
#
# check if we the backup file already exist
if [ -e /var/ipfire/backup/coreupdate28_$KVER.tar.gz ]; then
    echo Moving backup to backup-old ...
    mv -f /var/ipfire/backup/coreupdate28_$KVER.tar.gz \
       /var/ipfire/backup/coreupdate28_$KVER-old.tar.gz
fi
echo First we made a backup of all files that was inside of the
echo update archive. This may take a while ...
# Add some files that are not in the package to backup
echo lib/modules >> /opt/pakfire/tmp/ROOTFILES
echo boot >> /opt/pakfire/tmp/ROOTFILES
#

tar czvf /var/ipfire/backup/coreupdate28_$KVER.tar.gz.tar.gz \
   -T /opt/pakfire/tmp/ROOTFILES --exclude='#*' -C / > /dev/null 2>&1
echo
echo Update IPfire Kernel to $KVER ...
# Remove old kernel, configs, initrd, modules ...
#
rm -rf /boot/System.map-*
rm -rf /boot/config-*
rm -rf /boot/ipfirerd-*
rm -rf /boot/vmlinuz-*
rm -rf /lib/modules/
#
# Unpack the updated files
#
echo
echo Unpack the updated files ...
#
tar xvf /opt/pakfire/tmp/files --preserve --numeric-owner -C / \
	--no-overwrite-dir
#
# Modify grub.conf
#
echo
echo Update grub configuration ...
sed -i "s|ROOT|$ROOT|g" /boot/grub/grub.conf
sed -i "s|KVER|$KVER|g" /boot/grub/grub.conf
sed -i "s|MOUNT|$MOUNT|g" /boot/grub/grub.conf
#
# Made emergency - initramdisk
#
echo
echo Create new Initramdisks ...
cp -f /etc/mkinitcpio.conf.org /etc/mkinitcpio.conf
sed -i "s| autodetect | |g" /etc/mkinitcpio.conf
mkinitcpio -k $KVER-ipfire -g /boot/ipfirerd-$KVER-emergency.img
cp -f /etc/mkinitcpio.conf.org /etc/mkinitcpio.conf
#
# Made initramdisk
#
if [ "${ROOT:0:7}" == "/dev/sd" ]; then
    # Remove ide hook if root is on sda
    sed -i "s| ide | |g" /etc/mkinitcpio.conf
else
if [ "${ROOT:0:7}" == "/dev/hd" ]; then
    # Remove pata & sata hook if root is on hda
    sed -i "s| pata | |g" /etc/mkinitcpio.conf
    sed -i "s| sata | |g" /etc/mkinitcpio.conf
fi
fi
mkinitcpio -k $KVER-ipfire -g /boot/ipfirerd-$KVER.img
#
# ReInstall grub
#
grub-install --no-floppy ${ROOT::`expr length $ROOT`-1} --recheck
#
# Rebuild Language
#
#perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
#
# Restart snort
#
/etc/init.d/snort restart
#
# This core-update need a reboot
/usr/bin/logger -p syslog.emerg -t core-upgrade-28 "Upgrade finished. Please reboot... "' >> /tmp/remove_obsolete_paks
