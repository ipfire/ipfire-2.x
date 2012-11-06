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
# Copyright (C) 2012 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

#
# Remove old core updates from pakfire cache to save space...
core=65
for (( i=1; i<=$core; i++ ))
do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

#
KVER="3.2.33"
MOUNT=`grep "kernel" /boot/grub/grub.conf | tail -n 1`
# Nur den letzten Parameter verwenden
echo $MOUNT > /dev/null
MOUNT=$_
if [ ! $MOUNT == "rw" ]; then
	MOUNT="ro"
fi

#
# check if we the backup file already exist
if [ -e /var/ipfire/backup/core-upgrade_$KVER.tar.xz ]; then
    echo Moving backup to backup-old ...
    mv -f /var/ipfire/backup/core-upgrade_$KVER.tar.xz \
       /var/ipfire/backup/core-upgrade_$KVER-old.tar.xz
fi
echo First we made a backup of all files that was inside of the
echo update archive. This may take a while ...
# Add some files that are not in the package to backup
echo lib/modules >> /opt/pakfire/tmp/ROOTFILES
echo etc/udev >> /opt/pakfire/tmp/ROOTFILES
echo lib/udev >> /opt/pakfire/tmp/ROOTFILES
echo boot >> /opt/pakfire/tmp/ROOTFILES
echo etc/snort >> /opt/pakfire/tmp/ROOTFILES
echo usr/lib/snort_* >> /opt/pakfire/tmp/ROOTFILES

# Backup the files
tar cJvf /var/ipfire/backup/core-upgrade_$KVER.tar.xz \
    -C / -T /opt/pakfire/tmp/ROOTFILES --exclude='#*' --exclude='/var/cache' > /dev/null 2>&1

echo
echo Update Kernel to $KVER ...
#
# Remove old kernel, configs, initrd, modules ...
#
rm -rf /boot/System.map-*
rm -rf /boot/config-*
rm -rf /boot/ipfirerd-*
rm -rf /boot/vmlinuz-*
rm -rf /lib/modules/*-ipfire
#
# Remove old udev rules.
#
cp /etc/udev/rules.d/29-ct-server-network.rules /tmp/
cp /etc/udev/rules.d/30-persistent-network.rules /tmp/
rm -rf /etc/udev
rm -rf /lib/udev
mkdir -p /etc/udev/rules.d
mv /tmp/29-ct-server-network.rules /etc/udev/rules.d/
mv /tmp/30-persistent-network.rules /etc/udev/rules.d/

#
# Backup grub.conf
#
cp -vf /boot/grub/grub.conf /boot/grub/grub.conf.org

#
#Stop services
/etc/init.d/snort stop
/etc/init.d/squid stop
/etc/init.d/ipsec stop

#Remove old snort
rm -rf /etc/snort
rm -rf /usr/lib/snort_*

#
#Extract files
extract_files

#
# Start services
#
/etc/init.d/squid start
/etc/init.d/snort start
if [ `grep "ENABLED=on" /var/ipfire/vpn/settings` ]; then
	/etc/init.d/ipsec start
fi

#
# Rebuild qosscript if enabled
#
if [ -e /var/ipfire/qos/enable ]; then
	/usr/local/bin/qosctrl stop
	/usr/local/bin/qosctrl generate
	/usr/local/bin/qosctrl start
fi

#
# Modify grub.conf
#
echo
echo Update grub configuration ...
ROOT=`mount | grep " / " | cut -d" " -f1`

if [ ! -z $ROOT ]; then
	ROOTUUID=`blkid -c /dev/null -sUUID $ROOT | cut -d'"' -f2`
fi

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
# Delete old lm-sensor modullist to force search at next boot
#
rm -rf /etc/sysconfig/lm_sensors

#
#Update Language cache
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"

#
# Remove meta's of packages that are now common...
#
rm -rf /opt/pakfire/db/*/meta-fontconfig
rm -rf /opt/pakfire/db/*/meta-glib

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
echo '/usr/bin/logger -p syslog.emerg -t core-upgrade-65 "Upgrade finished. If you use a customized grub.cfg"' >> /tmp/pak_update
echo '/usr/bin/logger -p syslog.emerg -t core-upgrade-65 "Check it before reboot !!!"' >> /tmp/pak_update
echo '/usr/bin/logger -p syslog.emerg -t core-upgrade-65 " *** Please reboot... *** "' >> /tmp/pak_update
echo 'touch /var/run/need_reboot ' >> /tmp/pak_update
#
chmod +x /tmp/pak_update
/tmp/pak_update &

sync

#
#Finish
/etc/init.d/fireinfo start
sendprofile

echo
echo Please wait until pakfire has ended...
echo
#Don't report the exitcode last command
exit 0

