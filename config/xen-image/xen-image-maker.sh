#/bin/bash
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2013  Arne Fitzenreiter  <arne_f@ipfire.org>             #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

SNAME=xxxSNAMExxx
VERSION=xxxVERSIONxxx
CORE=xxxCORExxx

KERN_TYPE=pae
KVER=xxxKVERxxx
KERN_PACK=xxxKERN_PACKxxx
KRNDOWN=http://mirror0.ipfire.org/pakfire2/$VERSION/paks

###############################################################################
# If you really want to use  outdated legacy kernel uncomment this lines. #####
# Not recommended!!! ##########################################################
######################
#KERN_TYPE=xen
#KVER=2.6.32.61
#KERN_PACK=27
#KRNDOWN=http://mirror0.ipfire.org/pakfire2/2.13/paks
###############################################################################

SIZEboot=30
SIZEswap=512
SIZEroot=512
SIZEvar=950

##############################################################################

SOURCEISO=$SNAME-$VERSION.i586-full-core$CORE.iso
HTTPDIR=http://download.ipfire.org/releases/ipfire-2.x/$VERSION-core$CORE

TMPDIR=./ipfire-tmp
ISODIR=$TMPDIR/iso
MNThdd=$TMPDIR/harddisk

IMGboot=./$SNAME-boot.img
IMGswap=./$SNAME-swap.img
IMGroot=./$SNAME-root.img
IMGvar=./$SNAME-var.img

KERNEL=linux-$KERN_TYPE-$KVER-$KERN_PACK.ipfire

rm -rf $TMPDIR && mkdir -p $MNThdd && mkdir -p $ISODIR
echo --------------------------------------------------------
echo - Download $SOURCEISO ...
echo --------------------------------------------------------
wget $HTTPDIR/$SOURCEISO -O $TMPDIR/$SOURCEISO
mount -o loop $TMPDIR/$SOURCEISO $ISODIR

echo --------------------------------------------------------
echo - Download $KERNEL ...
echo --------------------------------------------------------
wget $KRNDOWN/$KERNEL -O $TMPDIR/$KERNEL.gpg
gpg -d $TMPDIR/$KERNEL.gpg > $TMPDIR/$KERNEL

echo --------------------------------------------------------
echo - Create Images ...
echo --------------------------------------------------------

#Create bootimage
dd bs=1M if=/dev/zero of=$IMGboot count=$SIZEboot
mkfs.ext2 -F $IMGboot

#Create swapimage
dd bs=1M if=/dev/zero of=$IMGswap count=$SIZEswap
mkswap $IMGswap

#Create rootimage
dd bs=1M if=/dev/zero of=$IMGroot count=$SIZEroot
mkfs.ext4 -F $IMGroot

#Create varimage
dd bs=1M if=/dev/zero of=$IMGvar count=$SIZEvar
mkfs.ext4 -F $IMGvar

echo --------------------------------------------------------
echo - Intall IPFire to the Images ...
echo --------------------------------------------------------

# Mount Images
mount -o loop $IMGroot $MNThdd
mkdir $MNThdd/boot
mkdir $MNThdd/var
mkdir $MNThdd/var/log
mount -o loop $IMGboot $MNThdd/boot
mount -o loop $IMGvar $MNThdd/var

# Install IPFire without kernel modules
tar -C $MNThdd/ -xvf $ISODIR/$SNAME-$VERSION.tlz --lzma \
	--exclude=lib/modules* --exclude=boot*

#Install Kernel
tar -C $MNThdd/opt/pakfire/tmp -xvf $TMPDIR/$KERNEL
chroot $MNThdd /opt/pakfire/tmp/install.sh
rm -rf $MNThdd/opt/pakfire/tmp/*

#Create grub menuentry for pygrub
mkdir $MNThdd/boot/grub
echo "timeout 10"                          > $MNThdd/boot/grub/grub.conf
echo "default 0"                          >> $MNThdd/boot/grub/grub.conf
echo "title IPFire ($KERN_TYPE-kernel)"   >> $MNThdd/boot/grub/grub.conf
echo "  kernel /vmlinuz-$KVER-ipfire-xen root=/dev/xvda3 rootdelay=10 panic=10 console=xvc0 ro" \
					  >> $MNThdd/boot/grub/grub.conf
echo "  initrd /ipfirerd-$KVER-$KERN_TYPE.img" >> $MNThdd/boot/grub/grub.conf
echo "# savedefault 0" >> $MNThdd/boot/grub/grub.conf

ln -s grub.conf $MNThdd/boot/grub/menu.lst

#create the meta-info of linux-kernel package
echo ""                       >  $MNThdd/opt/pakfire/db/meta/linux-$KERN_TYPE
echo "Name: linux-$KERN_TYPE" >> $MNThdd/opt/pakfire/db/meta/linux-$KERN_TYPE
echo "ProgVersion: $KVER"     >> $MNThdd/opt/pakfire/db/meta/linux-$KERN_TYPE
echo "Release: $KERN_PACK"    >> $MNThdd/opt/pakfire/db/meta/linux-$KERN_TYPE
echo ""                       >> $MNThdd/opt/pakfire/db/meta/linux-$KERN_TYPE
echo ""                       >  $MNThdd/opt/pakfire/db/installed/linux-$KERN_TYPE
echo "Name: linux-$KERN_TYPE" >> $MNThdd/opt/pakfire/db/installed/linux-$KERN_TYPE
echo "ProgVersion: $KVER"     >> $MNThdd/opt/pakfire/db/installed/linux-$KERN_TYPE
echo "Release: $KERN_PACK"    >> $MNThdd/opt/pakfire/db/installed/linux-$KERN_TYPE
echo ""                       >> $MNThdd/opt/pakfire/db/installed/linux-$KERN_TYPE

#Set default configuration
echo "LANGUAGE=en" >> $MNThdd/var/ipfire/main/settings
echo "HOSTNAME=$SNAME" >> $MNThdd/var/ipfire/main/settings
echo "THEME=ipfire" >> $MNThdd/var/ipfire/main/settings
touch $MNThdd/lib/modules/$KVER-ipfire-$KERN_TYPE/modules.dep
mkdir $MNThdd/proc
mount --bind /proc $MNThdd/proc
mount --bind /dev  $MNThdd/dev
mount --bind /sys  $MNThdd/sys
chroot $MNThdd /usr/bin/perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
sed -i -e "s|DEVICE1|/dev/xvda1|g" $MNThdd/etc/fstab
sed -i -e "s|DEVICE2|/dev/xvda2|g" $MNThdd/etc/fstab
sed -i -e "s|DEVICE3|/dev/xvda3|g" $MNThdd/etc/fstab
sed -i -e "s|DEVICE4|/dev/xvda4|g" $MNThdd/etc/fstab

sed -i -e "s|FSTYPE|ext4|g" $MNThdd/etc/fstab

#Remove root / fstab check
rm -rf $MNThdd/etc/rc.d/rcsysinit.d/S19checkfstab
#Remove console init
rm -rf $MNThdd/etc/rc.d/rcsysinit.d/S70console

#Add xvc0 to securetty
echo xvc0 >> $MNThdd/etc/securetty

#Add getty for xvc0
echo "#Enable login for XEN" >> $MNThdd/etc/inittab
echo "8:2345:respawn:/sbin/agetty xvc0 9600" >> $MNThdd/etc/inittab

#Disable some initskripts
echo "#!/bin/sh" > $MNThdd/etc/rc.d/init.d/setclock
echo "#!/bin/sh" > $MNThdd/etc/rc.d/init.d/keymap

#Remove autoload of acpi modules
sed -i -e "s|^ac|#ac|g" $MNThdd/etc/sysconfig/modules
sed -i -e "s|^battery|#battery|g" $MNThdd/etc/sysconfig/modules
sed -i -e "s|^button|#button|g" $MNThdd/etc/sysconfig/modules
sed -i -e "s|^fan|#fan|g" $MNThdd/etc/sysconfig/modules
sed -i -e "s|^processor|#processor|g" $MNThdd/etc/sysconfig/modules
sed -i -e "s|^thermal|#thermal|g" $MNThdd/etc/sysconfig/modules
sed -i -e "s|^video|#video|g" $MNThdd/etc/sysconfig/modules

# Unmount
umount $MNThdd/proc
umount $MNThdd/dev
umount $MNThdd/sys
umount $MNThdd/var
umount $MNThdd/boot
umount $MNThdd

umount $ISODIR
rm -rf ./ipfire-tmp
echo --------------------------------------------------------
echo - Done.
echo --------------------------------------------------------
