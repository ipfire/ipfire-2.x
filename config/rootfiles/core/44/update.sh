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
KVER="2.6.32.27"
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
echo etc/snort >> /opt/pakfire/tmp/ROOTFILES
echo usr/lib/snort_* >> /opt/pakfire/tmp/ROOTFILES
echo usr/lib/squid >> /opt/pakfire/tmp/ROOTFILES

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
# Stop services to save memory
#
/etc/init.d/snort stop
/etc/init.d/squid stop
/etc/init.d/ipsec stop

#
#
# Remove old snort...
rm -rf /etc/snort
rm -rf /usr/lib/snort_*
# Remove old squid...
rm -rf /usr/lib/squid
#
# Unpack the updated files
#
echo
echo Unpack the updated files ...
#
tar xvf /opt/pakfire/tmp/files --preserve --numeric-owner -C / \
	--no-overwrite-dir

#
# Change collectd init symlinks
#
rm -f /etc/rc.d/rc3.d/S21collectd
ln -f -s ../init.d/collectd /etc/rc.d/rc3.d/S29collectd

# Remove old pakfire cronjob.
rm -f /etc/fcron.daily/pakfire-update

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

#new strongswan need keyexchange=ikev1 because this is not default anymore
mv /var/ipfire/vpn/ipsec.conf /var/ipfire/vpn/ipsec.conf.org
grep -v "keyexchange=ikev1" /var/ipfire/vpn/ipsec.conf.org > /var/ipfire/vpn/ipsec.conf
sed -i "s|^conn [A-Za-z].*$|&\n\tkeyexchange=ikev1|g" /var/ipfire/vpn/ipsec.conf
chown nobody:nobody /var/ipfire/vpn/ipsec.conf

#new squid has some changed options. Build a basic config to be able start squid.
mv /var/ipfire/proxy/squid.conf /var/ipfire/proxy/squid.conf.org
grep -v "header_access " /var/ipfire/proxy/squid.conf.org | \
grep -v "error_directory " | \
grep -v "cache_dir null" | \
grep -v "reply_body_max_size 0" > /var/ipfire/proxy/squid.conf
echo >> /var/ipfire/proxy/squid.conf
echo error_directory /etc/squid/errors >> /var/ipfire/proxy/squid.conf
chown nobody:nobody /var/ipfire/proxy/squid.conf

#Convert extrahd entries to UUID
cp -f /var/ipfire/extrahd/devices /var/ipfire/extrahd/devices.org
while read entry
do
	device=`echo $entry | cut -f1 -d";"`
	uuid=`blkid  -c /dev/null -s UUID -o value /dev/$device`
	if [ ! -z $uuid ]; then
		sed -i -e "s|$device|UUID=$uuid|g" /var/ipfire/extrahd/devices
		sed -i -e "s|/dev/$device|UUID=$uuid|g" /var/ipfire/extrahd/fstab
		sed -i -e "s|/dev/$device|UUID=$uuid|g" /etc/fstab
	fi
done < /var/ipfire/extrahd/devices.org

#
# Start services
#
/etc/init.d/squid start
/etc/init.d/snort start
if [ `grep "ENABLED=on" /var/ipfire/vpn/settings` ]; then
	/etc/init.d/ipsec start
fi

# Add pakfire and fireinfo cronjobs...
grep -v "# fireinfo" /var/spool/cron/root.orig |
grep -v "/usr/bin/sendprofile" |
grep -v "# pakfire" |
grep -v "/usr/local/bin/pakfire" > /var/tmp/root.tmp
echo "" >> /var/tmp/root.tmp
echo "# fireinfo" >> /var/tmp/root.tmp
echo "%nightly,random * 23-4 /usr/bin/sendprofile >/dev/null 2>&1" >> /var/tmp/root.tmp
echo "" >> /var/tmp/root.tmp
echo "# pakfire" >> /var/tmp/root.tmp
echo "%nightly,random * 23-4 /usr/local/bin/pakfire update >/dev/null 2>&1" >> /var/tmp/root.tmp
fcrontab /var/tmp/root.tmp

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
# Don't show gpl on updated systens
#
touch /var/ipfire/main/gpl_accepted
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
#
# Change version of Pakfire.conf
#
OLDVERSION=`grep "version = " /opt/pakfire/etc/pakfire.conf | cut -d'"' -f2`
NEWVERSION="2.9"
sed -i "s|$OLDVERSION|$NEWVERSION|g" /opt/pakfire/etc/pakfire.conf
#
# After pakfire has ended run it again and update the lists and do upgrade
#
echo '#!/bin/bash'                                        >  /tmp/pak_update
echo 'while [ "$(ps -A | grep " update.sh")" != "" ]; do' >> /tmp/pak_update
echo '    sleep 1'                                        >> /tmp/pak_update
echo 'done'                                               >> /tmp/pak_update
echo 'while [ "$(ps -A | grep " pakfire")" != "" ]; do'   >> /tmp/pak_update
echo '    sleep 1'                                        >> /tmp/pak_update
echo 'done'                                               >> /tmp/pak_update
echo '/opt/pakfire/pakfire update -y --force'             >> /tmp/pak_update
echo '/opt/pakfire/pakfire upgrade -y'                    >> /tmp/pak_update
echo '/opt/pakfire/pakfire upgrade -y'                    >> /tmp/pak_update
echo '/opt/pakfire/pakfire upgrade -y'                    >> /tmp/pak_update
echo '/usr/bin/logger -p syslog.emerg -t core-upgrade-44 "Upgrade finished. If you use a customized grub.cfg"' >> /tmp/pak_update
echo '/usr/bin/logger -p syslog.emerg -t core-upgrade-44 "Check it before reboot !!!"' >> /tmp/pak_update
echo '/usr/bin/logger -p syslog.emerg -t core-upgrade-44 " *** Please reboot... *** "' >> /tmp/pak_update
echo 'touch /var/run/need_reboot ' >> /tmp/pak_update
#
chmod +x /tmp/pak_update
/tmp/pak_update &
echo
echo Please wait until pakfire has ended...
echo
