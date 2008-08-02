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
KVER="2.6.23.17"
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
    echo Moving backup to backup-old ...
    mv -f /var/ipfire/backup/update_$OLDVERSION-$NEWVERSION.tar.bz2 \
       /var/ipfire/backup/update_$OLDVERSION-$NEWVERSION-old.tar.bz2
fi
echo First we made a backup of all files that was inside of the
echo update archive. This may take a while ...
# Add issue and packfire conf to backup
echo etc/issue >> /opt/pakfire/tmp/ROOTFILES
echo opt/pakfire/etc/pakfire.conf >> /opt/pakfire/tmp/ROOTFILES
tar cjvf /var/ipfire/backup/update_$OLDVERSION-$NEWVERSION.tar.bz2 \
   -T /opt/pakfire/tmp/ROOTFILES --exclude='#*' -C / > /dev/null 2>&1 
echo
echo Update IPfire to $NEWVERSON ...
#
# Delete old collectd symlink
#
rm -rf /etc/rc.d/rc3.d/S20collectd
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
# Made emergency - initramdisk
#
echo
echo Create new Initramdisks ...
cp -f /etc/mkinitcpio.conf /etc/mkinitcpio.conf.org
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
mkinitcpio -k $KVER-ipfire-smp -g /boot/ipfirerd-$KVER-smp.img
#
# Change version of Pakfire.conf
#
sed -i "s|$OLDVERSION|$NEWVERSION|g" /opt/pakfire/etc/pakfire.conf
#
# Create new issue
#
echo IPFire v$NEWVERSION - www.ipfire.org > /etc/issue
echo =================================== >> /etc/issue
echo \\n running on \\s \\r \\m >> /etc/issue
# Core 16 begin
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
/etc/init.d/mISDN config
# Core 16 end
#
# Remove obsolete packages
#
echo '#!/bin/bash'                                        >  /tmp/remove_obsolete_paks 
echo 'while [ "$(ps -A | grep " update.sh")" != "" ]; do' >> /tmp/remove_obsolete_paks
echo '    sleep 2'                                        >> /tmp/remove_obsolete_paks
echo 'done'                                               >> /tmp/remove_obsolete_paks
echo 'while [ "$(ps -A | grep " pakfire")" != "" ]; do'   >> /tmp/remove_obsolete_paks
echo '    sleep 2'                                        >> /tmp/remove_obsolete_paks
echo 'done'                                               >> /tmp/remove_obsolete_paks
echo '/opt/pakfire/pakfire remove zaptel -y'              >> /tmp/remove_obsolete_paks
echo '/opt/pakfire/pakfire update --force'                >> /tmp/remove_obsolete_paks
echo 'echo'                                               >> /tmp/remove_obsolete_paks
echo 'echo Update to IPFire $NEWVERSION finished. Please reboot... ' >> /tmp/remove_obsolete_paks
echo 'echo'                                               >> /tmp/remove_obsolete_paks
chmod +x /tmp/remove_obsolete_paks
/tmp/remove_obsolete_paks &
echo
echo Please wait until pakfire has ended...
echo