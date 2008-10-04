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
OLDVERSION=`grep "version = " /opt/pakfire/etc/pakfire.conf | cut -d'"' -f2`
NEWVERSION="2.3"
KVER="2.6.23.17"
ROOT=`grep "root=" /boot/grub/grub.conf | cut -d"=" -f2 | cut -d" " -f1 | tail -n 1`
MOUNT=`grep "kernel" /boot/grub/grub.conf | tail -n 1`
# Nur den letzten Parameter verwenden
echo $MOUNT > /dev/null
MOUNT=$_
#
echo 
echo Update IPFire $OLDVERSION to $NEWVERSION
echo
#
# check if we the backup file already exist
if [ -e /var/ipfire/backup/update_$OLDVERSION-$NEWVERSION.tar.gz ]; then
    echo Moving backup to backup-old ...
    mv -f /var/ipfire/backup/update_$OLDVERSION-$NEWVERSION.tar.gz \
       /var/ipfire/backup/update_$OLDVERSION-$NEWVERSION-old.tar.gz
fi
echo First we made a backup of all files that was inside of the
echo update archive. This may take a while ...
# Add some files that are not in the package to backup
echo etc/issue >> /opt/pakfire/tmp/ROOTFILES
echo opt/pakfire/etc/pakfire.conf >> /opt/pakfire/tmp/ROOTFILES
echo var/spool/cron/root.orig >> /opt/pakfire/tmp/ROOTFILES
echo etc/udev/rules.d/30-persistent-network.rules >> /opt/pakfire/tmp/ROOTFILES
echo etc/sysconfig/lm_sensors >> /opt/pakfire/tmp/ROOTFILES
echo var/log/rrd >> /opt/pakfire/tmp/ROOTFILES
echo var/log/vnstat >> /opt/pakfire/tmp/ROOTFILES
echo var/updatexlerator >> /opt/pakfire/tmp/ROOTFILES
echo lib/iptables >> /opt/pakfire/tmp/ROOTFILES
echo lib/modules >> /opt/pakfire/tmp/ROOTFILES
echo boot >> /opt/pakfire/tmp/ROOTFILES
echo srv/web/ipfire/cgi-bin/fwhits.cgi >> /opt/pakfire/tmp/ROOTFILES
echo srv/web/ipfire/cgi-bin/network.cgi >> /opt/pakfire/tmp/ROOTFILES
echo srv/web/ipfire/cgi-bin/traffics.cgi >> /opt/pakfire/tmp/ROOTFILES
echo srv/web/ipfire/cgi-bin/graphs.cgi >> /opt/pakfire/tmp/ROOTFILES
echo srv/web/ipfire/cgi-bin/qosgraph.cgi >> /opt/pakfire/tmp/ROOTFILES
#
tar czvf /var/ipfire/backup/update_$OLDVERSION-$NEWVERSION.tar.gz \
   -T /opt/pakfire/tmp/ROOTFILES --exclude='#*' -C / > /dev/null 2>&1 
echo
echo Update IPfire to $NEWVERSION ...
#
# On some systems the folder for addon backups is missing
#
if [ ! -e /var/ipfire/backup/addons/backup ]; then
    mkdir -p /var/ipfire/backup/addons/backup
fi
#
# Delete old collectd symlink
#
rm -rf /etc/rc.d/rc3.d/S20collectd
#
# Delete squid symlink
#
rm -rf /etc/rc.d/rc3.d/S99squid
#
# Delete old cgi files ...
#
rm -rf /srv/web/ipfire/cgi-bin/fwhits.cgi
rm -rf /srv/web/ipfire/cgi-bin/network.cgi
rm -rf /srv/web/ipfire/cgi-bin/traffics.cgi
rm -rf /srv/web/ipfire/cgi-bin/graphs.cgi
rm -rf /srv/web/ipfire/cgi-bin/qosgraph.cgi
#
# Delete old iptables libs...
#
rm -rf /lib/iptables
#
# Remove old kernel, configs, initrd, modules ...
#
rm -rf /boot/System.map-*
rm -rf /boot/config-*
rm -rf /boot/ipfirerd-*
rm -rf /boot/vmlinuz-*
rm -rf /lib/modules/
#
# Stopping Squid
#
echo
echo Stopping Squid ...
/etc/init.d/squid stop
#
# Unpack the updated files
#
echo
echo Unpack the updated files ...
extract_files
#
# Starting Squid
#
echo
echo Starting Squid ...
/etc/init.d/squid start
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
#mkinitcpio -k $KVER-ipfire-smp -g /boot/ipfirerd-$KVER-smp.img
#
# ReInstall grub
#
grub-install --no-floppy ${ROOT::`expr length $ROOT`-1}
#
# Update fstab
#
grep -v "tmpfs" /etc/fstab > /tmp/fstab.tmp
echo "none	/tmp		tmpfs	defaults,size=128M	0	0" >> /tmp/fstab.tmp
echo "none	/var/log/rrd	tmpfs	defaults,size=64M	0	0" >> /tmp/fstab.tmp
echo "none	/var/lock	tmpfs	defaults,size=16M	0	0" >> /tmp/fstab.tmp
echo "none	/var/run	tmpfs	defaults,size=16M	0	0" >> /tmp/fstab.tmp
mv /tmp/fstab.tmp /etc/fstab
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
#
# Update crontab
#
grep -v "ipacsum" /var/spool/cron/root.orig | grep -v "hddshutdown" > /tmp/root.orig.tmp
echo "# Backup collectd files" >> /tmp/root.orig.tmp
echo "* 05 * * *	/etc/init.d/tmpfs backup >/dev/null" >> /tmp/root.orig.tmp
echo "# hddshutdown" >> /tmp/root.orig.tmp
echo "*/30 * * * *	/usr/local/bin/hddshutdown >/dev/null" >> /tmp/root.orig.tmp
mv /tmp/root.orig.tmp /var/spool/cron/root.orig
chmod 600 /var/spool/cron/root.orig
chown root:cron /var/spool/cron/root.orig
#
# Update network-rules
#
sed -i 's|"net", SYSFS{address}|"net", SYSFS{type}=="1", SYSFS{address}|g' \
          /etc/udev/rules.d/30-persistent-network.rules
#
# Move vnstat database to /var/log/rrd
#
mkdir -p /var/log/rrd.bak/vnstat
if [ -e /var/log/vnstat ]; then
    cp -pR /var/log/vnstat /var/log/rrd.bak/vnstat
    mv /var/log/vnstat /var/log/rrd/vnstat
fi
#
# Core 17
#
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
perl /var/ipfire/qos/bin/migrate.pl
/var/ipfire/updatexlrator/bin/convert
#
# Delete old lm-sensor modullist...
#
rm -rf /etc/sysconfig/lm_sensors
#
# ISDN
#
/etc/init.d/mISDN config
#
# Remove obsolete packages, update the lists and do upgrade
#
echo '#!/bin/bash'                                        >  /tmp/remove_obsolete_paks 
echo 'while [ "$(ps -A | grep " update.sh")" != "" ]; do' >> /tmp/remove_obsolete_paks
echo '    sleep 2'                                        >> /tmp/remove_obsolete_paks
echo 'done'                                               >> /tmp/remove_obsolete_paks
echo 'while [ "$(ps -A | grep " pakfire")" != "" ]; do'   >> /tmp/remove_obsolete_paks
echo '    sleep 2'                                        >> /tmp/remove_obsolete_paks
echo 'done'                                               >> /tmp/remove_obsolete_paks
echo '/opt/pakfire/pakfire remove -y mpg123 subversion zaptel' >> /tmp/remove_obsolete_paks
echo '/opt/pakfire/pakfire update -y --force'             >> /tmp/remove_obsolete_paks
echo '/opt/pakfire/pakfire upgrade -y'                    >> /tmp/remove_obsolete_paks
echo '/opt/pakfire/pakfire upgrade -y'                    >> /tmp/remove_obsolete_paks
echo '/opt/pakfire/pakfire upgrade -y'                    >> /tmp/remove_obsolete_paks
echo 'logger -p syslog.emerg -t core-upgrade-18 "Upgrade finished. Please reboot... "' >> /tmp/remove_obsolete_paks
#
chmod +x /tmp/remove_obsolete_paks
/tmp/remove_obsolete_paks &
echo
echo Please wait until pakfire has ended...
echo
