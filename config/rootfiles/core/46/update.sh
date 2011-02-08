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
# Remove core updates from pakfire cache to save space...
rm -f /var/cache/pakfire/core-upgrade-*.ipfire
#
#Stop services

#
#Extract files
extract_files

#
#Start services
/etc/init.d/squid restart

#
#Update Language cache
#perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"

# Rebuild initrd of optional pae and xen kernel
KVER=2.6.32.28
[ -e /boot/ipfirerd-$KVER-pae.img ] && /sbin/dracut --force --verbose /boot/ipfirerd-$KVER-pae.img $KVER-ipfire-pae
[ -e /boot/ipfirerd-$KVER-xen.img ] && /sbin/dracut --force --verbose /boot/ipfirerd-$KVER-xen.img $KVER-ipfire-xen

#Rebuild module dep's
depmod 2.6.32.28-ipfire     >/dev/null 2>&1
depmod 2.6.32.28-ipfire-pae >/dev/null 2>&1
depmod 2.6.32.28-ipfire-xen >/dev/null 2>&1

#
#Finish
#Don't report the exitcode last command
exit 0
