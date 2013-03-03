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
# Copyright (C) 2013 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

#
# Remove old core updates from pakfire cache to save space...
core=67
for (( i=1; i<=$core; i++ ))
do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

#
#Stop services
/etc/init.d/squid stop

#
#Extract files
extract_files

#
#Start services
/etc/init.d/squid start

#
#Update Language cache
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"

#remove wrong mISDN modules
rm -rf /lib/modules/*-ipfire*/kernel/drivers/isdn/mISDN
rm -rf /lib/modules/*-ipfire*/kernel/drivers/isdn/hardware/mISDN

#remove pae kernel from pakfire cache to force reload if it should reinstalled
rm -rf /var/cache/pakfire/linux-pae*.ipfire

#Rebuild module dep's
arch=`uname -m`
if [ ${arch::3} == "arm" ]; then
	depmod -a 3.2.38-ipfire-kirkwood >/dev/null 2>&1
	depmod -a 3.2.38-ipfire-omap >/dev/null 2>&1
	depmod -a 3.2.38-ipfire-rpi >/dev/null 2>&1
else
	depmod -a 3.2.38-ipfire     >/dev/null 2>&1
	depmod -a 3.2.38-ipfire-pae >/dev/null 2>&1
	depmod -a 2.6.32.60-ipfire-xen >/dev/null 2>&1
fi

#Rebuild initrd's
#if [ -e /boot/ipfirerd-3.2.38.img ]; then
#/sbin/dracut --force --verbose /boot/ipfirerd-3.2.38.img 3.2.38-ipfire
#fi
#if [ -e /boot/ipfirerd-3.2.38-pae.img ]; then
#/sbin/dracut --force --verbose /boot/ipfirerd-3.2.38-pae.img 3.2.38-ipfire-pae
#fi
#if [ -e /boot/ipfirerd-2.6.32.60-xen.img ]; then
#/sbin/dracut --force --verbose /boot/ipfirerd-2.6.32.60-xen.img 2.6.32.60-ipfire-xen
#fi

sync

# This update need a reboot...
touch /var/run/need_reboot

#
#Finish
/etc/init.d/fireinfo start
sendprofile
#Don't report the exitcode last command
exit 0
