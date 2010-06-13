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
OLDVERSION=`grep "version = " /opt/pakfire/etc/pakfire.conf | cut -d'"' -f2`
#
# Test if we running on xen
#
uname -r | grep "ipfire-xen";
if [ ${?} = 0 ]; then
	#Xen Kernel is active
	NEWVERSION="2.7-xen"
else
	#Normal Kernel
	NEWVERSION="2.7"
fi
#
KVER="2.6.32.15"
ROOT=`grep "root=" /boot/grub/grub.conf | cut -d"=" -f2 | cut -d" " -f1 | tail -n 1`
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
echo etc/sysconfig/lm_sensors >> /opt/pakfire/tmp/ROOTFILES
echo usr/lib/ipsec >> /opt/pakfire/tmp/ROOTFILES
echo usr/libexec/ipsec >> /opt/pakfire/tmp/ROOTFILES
tar cjvf /var/ipfire/backup/core-upgrade_$KVER.tar.bz2 \
    -C / -T /opt/pakfire/tmp/ROOTFILES --exclude='#*' > /dev/null 2>&1

#
# Stop Sevices
#
/etc/init.d/collectd stop
/etc/init.d/squid stop
/etc/init.d/ipsec stop

echo
echo Update Kernel to $KVER ...
# Remove old kernel, configs, initrd, modules ...
#
rm -rf /boot/System.map-*
rm -rf /boot/config-*
rm -rf /boot/ipfirerd-*
rm -rf /boot/vmlinuz-*
rm -rf /lib/modules/*-ipfire
# Don't remove all old xen modules. Kernel may stored outside.
# only from 2.6.27.25 and 31
rm -rf /lib/modules/2.6.27.25-ipfire-xen
rm -rf /lib/modules/2.6.27.31-ipfire-xen
#
# remove openswan libs ...
#
rm -rf /usr/lib/ipsec
rm -rf /usr/libexec/ipsec
#
# old snort libs ...
#
rm -rf /usr/lib/snort_*

#
# Backup grub.conf
#
cp -vf /boot/grub/grub.conf /boot/grub/grub.conf.org
#
# Stop sysklogd
/etc/init.d/sysklogd stop
#
# Unpack the updated files
#
echo
echo Unpack the updated files ...
#
tar xvf /opt/pakfire/tmp/files --preserve --numeric-owner -C / \
	--no-overwrite-dir
#
# Start Sevices
/etc/init.d/sysklogd start
/etc/init.d/squid start
#
# Modify grub.conf
#
echo
echo Update grub configuration ...
sed -i "s|ROOT|$ROOT|g" /boot/grub/grub.conf
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
#
# ReInstall grub
#
grub-install --no-floppy ${ROOT::`expr length $ROOT`-1} --recheck
#
# Rebuild Language
#
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
#
# Cleanup Collectd statistics...
#
PRECLEAN=`du -sh /var/log/rrd/collectd`
#
rm -rf /var/log/rrd*/collectd/localhost/processes-*/ps_count*
rm -rf /var/log/rrd*/collectd/localhost/processes-*/ps_pagefaults*
rm -rf /var/log/rrd*/collectd/localhost/processes-*/ps_stacksize*
rm -rf /var/log/rrd*/collectd/localhost/processes-*/ps_state*
rm -rf /var/log/rrd*/collectd/localhost/processes-*/ps_vm*
#
rm -rf /var/log/rrd*/collectd/localhost/interface/if_errors*
rm -rf /var/log/rrd*/collectd/localhost/interface/if_packets*
#
rm -rf /var/log/rrd*/collectd/localhost/disk-*/disk_merged*
rm -rf /var/log/rrd*/collectd/localhost/disk-*/disk_ops*
rm -rf /var/log/rrd*/collectd/localhost/disk-*/disk_time*
#
rm -rf /var/log/rrd*/collectd/localhost/iptables-filter-INPUT/*-DROP_Wirelessinput*
rm -rf /var/log/rrd*/collectd/localhost/iptables-filter-FORWARD/*-DROP_Wirelessforward*
rm -rf /var/log/rrd*/collectd/localhost/iptables-filter-OUTGOINGFW
POSTCLEAN=`du -sh /var/log/rrd/collectd`
#
echo Cleaned up collectd directory from $PRECLEAN to $POSTCLEAN size.
#
# Start collectd
/etc/init.d/collectd start
#
# Delete old lm-sensor modullist to force search at next boot
#
rm -rf /etc/sysconfig/lm_sensors
#
# USB Modeswitch conf now called setup, rename ...
#
if [ -e /etc/usb_modeswitch.conf ]; then
mv -f /etc/usb_modeswitch.conf /etc/usb_modeswitch.setup
fi
#
# rebuild qosscript if enabled...
if [ -e /var/ipfire/qos/enable ]; then
	/usr/local/bin/qosctrl stop
	/usr/local/bin/qosctrl generate
	/usr/local/bin/qosctrl start
fi
#
#
# convert ipsec.conf from openswan to strongswan...
mv /var/ipfire/vpn/ipsec.conf /var/ipfire/vpn/ipsec.conf.org
cat /var/ipfire/vpn/ipsec.conf.org | \
grep -v "disablearrivalcheck=" | \
grep -v "klipsdebug=" | \
grep -v "leftfirewall=" | \
grep -v "lefthostaccess=" | \
grep -v "charonstart=" | \
grep -v "aggrmode=" > /var/ipfire/vpn/ipsec.conf
sed -i "s|ipsec[0-9]=||g" /var/ipfire/vpn/ipsec.conf
sed -i "s|nat_t ||g" /var/ipfire/vpn/ipsec.conf
sed -i "s|klips ||g" /var/ipfire/vpn/ipsec.conf
sed -i "s|^conn [A-Za-z].*$|&\n\tleftfirewall=yes\n\tlefthostaccess=yes|g" /var/ipfire/vpn/ipsec.conf
sed -i "s|^config setup$|&\n\tcharonstart=no|g" /var/ipfire/vpn/ipsec.conf
chown nobody:nobody /var/ipfire/vpn/ipsec.conf
chmod 644 /var/ipfire/vpn/ipsec.conf
#
# Add cryptodev to /etc/sysconfig/modules
mv /etc/sysconfig/modules /etc/sysconfig/modules.org
cat /etc/sysconfig/modules.org | \
grep -v "cryptodev" | \
grep -v "# End /etc/sysconfig/modules" > /etc/sysconfig/modules
echo "" >> /etc/sysconfig/modules
echo "### cryptodev" >> /etc/sysconfig/modules
echo "#" >> /etc/sysconfig/modules
echo "cryptodev" >> /etc/sysconfig/modules
echo "" >> /etc/sysconfig/modules
echo "# End /etc/sysconfig/modules" >> /etc/sysconfig/modules
chmod 644 /etc/sysconfig/modules
# Change version of Pakfire.conf
#
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
echo '/usr/bin/logger -p syslog.emerg -t core-upgrade-38 "Upgrade finished. If you use a customized grub.cfg"' >> /tmp/pak_update
echo '/usr/bin/logger -p syslog.emerg -t core-upgrade-38 "Check it before reboot !!!"' >> /tmp/pak_update
echo '/usr/bin/logger -p syslog.emerg -t core-upgrade-38 " *** Please reboot... *** "' >> /tmp/pak_update
#
chmod +x /tmp/pak_update
/tmp/pak_update &
#
echo
echo Please wait until pakfire has ended...
echo
