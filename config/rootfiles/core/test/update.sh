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
# Copyright (C) 2010 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1
#
KVER="2.6.32.24"
MOUNT=`grep "kernel" /boot/grub/grub.conf | tail -n 1`
# Nur den letzten Parameter verwenden
echo $MOUNT > /dev/null
MOUNT=$_
if [ ! $MOUNT == "rw" ]; then
	MOUNT="ro"
fi


#
# check if we the backup file already exist
if [ -e /var/ipfire/backup/core-upgrade_$KVER.tar.bz2 ]; then
    echo Moving backup to backup-old ...
    mv -f /var/ipfire/backup/core-upgrade_$KVER.tar.bz2 \
       /var/ipfire/backup/core-upgrade_$KVER-old.tar.bz2
fi
echo First we made a backup of all files that was inside of the
echo update archive. This may take a while ...
# Add some files that are not in the package to backup
echo lib/modules >> /opt/pakfire/tmp/ROOTFILES
echo boot >> /opt/pakfire/tmp/ROOTFILES
echo etc/mkinitcpio.conf >> /opt/pakfire/tmp/ROOTFILES
echo etc/mkinitcpio.conf.org >> /opt/pakfire/tmp/ROOTFILES
echo etc/mkinitcpio.d >> /opt/pakfire/tmp/ROOTFILES
echo lib/initcpio >> /opt/pakfire/tmp/ROOTFILES
echo sbin/mkinitcpio >> /opt/pakfire/tmp/ROOTFILES
echo usr/bin/iw >> /opt/pakfire/tmp/ROOTFILES

# Backup the files
tar cjvf /var/ipfire/backup/core-upgrade_$KVER.tar.bz2 \
    -C / -T /opt/pakfire/tmp/ROOTFILES --exclude='#*' > /dev/null 2>&1

echo
echo Update Kernel to $KVER ...
# Remove old kernel, configs, initrd, modules ...
#
rm -rf /boot/System.map-*
rm -rf /boot/config-*
rm -rf /boot/ipfirerd-*
rm -rf /boot/vmlinuz-*
rm -rf /lib/modules/*-ipfire
# Remove mkinitcpio
rm -rf /etc/mkinitcpio.*
rm -rf /lib/initcpio
rm -rf /sbin/mkinitcpio
# Remove old iw (new is in usr/sbin)
rm -rf /usr/bin/iw
#
# Backup grub.conf
#
cp -vf /boot/grub/grub.conf /boot/grub/grub.conf.org
#
# Unpack the updated files
#
echo
echo Unpack the updated files ...
#
tar xvf /opt/pakfire/tmp/files --preserve --numeric-owner -C / \
	--no-overwrite-dir

#
# Stop services to save memory
#
/etc/init.d/snort stop
/etc/init.d/squid stop

# Convert /etc/fstab entries to UUID ...
#
echo Convert fstab entries to UUID ...
ROOT=`mount | grep " / " | cut -d" " -f1`
BOOT=`mount | grep " /boot " | cut -d" " -f1`
VAR=`mount | grep " /var " | cut -d" " -f1`
SWAP=`grep "/dev/" /proc/swaps | cut -d" " -f1`
#

if [ ! -z $ROOT ]; then
	ROOTUUID=`blkid -c /dev/null -sUUID $ROOT | cut -d'"' -f2`
	if [ ! -z $ROOTUUID ]; then
		sed -i "s|^$ROOT|UUID=$ROOTUUID|g" /etc/fstab
	#else
		#to do add uuid to rootfs
	fi
	else
	echo "ERROR! / not found!!!"
fi

if [ ! -z $BOOT ]; then
	BOOTUUID=`blkid -c /dev/null -sUUID $BOOT | cut -d'"' -f2`
	if [ ! -z $BOOTUUID ]; then
		sed -i "s|^$BOOT|UUID=$BOOTUUID|g" /etc/fstab
	#else
		#to do add uuid to bootfs
	fi
	else
	echo "WARNING! /boot not found!!!"
fi

if [ ! -z $VAR ]; then
	VARUUID=`blkid -c /dev/null -sUUID $VAR | cut -d'"' -f2`
	if [ ! -z $VARUUID ]; then
		sed -i "s|^$VAR|UUID=$VARUUID|g" /etc/fstab
	#else
		#to do add uuid to varfs
	fi
	else
	echo "WARNING! /var not found!!!"
fi

if [ ! -z $SWAP ]; then
	SWAPUUID=`blkid -c /dev/null -sUUID $SWAP | cut -d'"' -f2`
	if [ ! -z $SWAPUUID ]; then
		sed -i "s|^$SWAP|UUID=$SWAPUUID|g" /etc/fstab
	else
		# Reformat swap to add a UUID
		swapoff -a
		mkswap $SWAP
		swapon -a
		SWAPUUID=`blkid -c /dev/null -sUUID $SWAP | cut -d'"' -f2`
		if [ ! -z $SWAPUUID ]; then
			sed -i "s|^$SWAP|UUID=$SWAPUUID|g" /etc/fstab
		fi
	fi
	else
	echo "WARNING! swap not found!!!"
fi

#
# Start services
#
/etc/init.d/squid start
/etc/init.d/snort start

#
# Modify grub.conf
#
echo
echo Update grub configuration ...
if [ ! -z $ROOTUUID ]; then
	sed -i "s|ROOT|UUID=$ROOTUUID|g" /boot/grub/grub.conf
else
	sed -i "s|ROOT|$ROOT|g" /boot/grub/grub.conf
fi
sed -i "s|KVER|$KVER|g" /boot/grub/grub.conf
sed -i "s|MOUNT|$MOUNT|g" /boot/grub/grub.conf

if [ "$(grep "^serial" /boot/grub/grub.conf.org)" == "" ]; then
	echo "grub use default console ..."
else
	echo "grub use serial console ..."
	sed -i -e "s|splashimage|#splashimage|g" /boot/grub/grub.conf
	sed -i -e "s|#serial|serial|g" /boot/grub/grub.conf
	sed -i -e "s|#terminal|terminal|g" /boot/grub/grub.conf
	sed -i -e "s| panic=10 | console=ttyS0,38400n8 panic=10 |g" /boot/grub/grub.conf
fi
#
# Change /dev/hd? to /dev/sda
#
if [ "${ROOT:0:7}" == "/dev/hd" ];then
	sed -i -e "s|${ROOT:0:8}|/dev/sda|g" /boot/grub/grub.conf
	sed -i -e "s|${ROOT:0:8}|/dev/sda|g" /etc/fstab
fi
#
# ReInstall grub
#
grub-install --no-floppy ${ROOT::`expr length $ROOT`-1} --recheck
#
# Rebuild Language
#
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
#
# Delete old lm-sensor modullist to force search at next boot
#
rm -rf /etc/sysconfig/lm_sensors
/usr/bin/logger -p syslog.emerg -t kernel "Upgrade finished. If you use a customized grub.cfg"
/usr/bin/logger -p syslog.emerg -t kernel "Check it before reboot !!!"
/usr/bin/logger -p syslog.emerg -t kernel " *** Please reboot... *** "
