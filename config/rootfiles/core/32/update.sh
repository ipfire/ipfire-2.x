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
# Copyright (C) 2009 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1
extract_files
#
# Fix tmpfs Backup cronjob entry
grep -v "tmpfs backup" /var/spool/cron/root.orig > /var/tmp/root.tmp
echo "17 5 * * *      /etc/init.d/tmpfs backup >/dev/null" >> /var/tmp/root.tmp
fcrontab /var/tmp/root.tmp
#Fix openvpn server permissions
if [ -e "/var/ipfire/ovpn/server.conf" ]; then
	chmod 644 /var/ipfire/ovpn/server.conf
	chown nobody:nobody /var/ipfire/ovpn/server.conf
fi
#Update Language cache
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
#Remove some non compat-wireless modules
rm -rf /lib/modules/2.6.27.31-ipfire/kernel/drivers/net/wireless/ath?k
rm -rf /lib/modules/2.6.27.31-ipfire/kernel/drivers/net/wireless/rtl818?.ko
rm -rf /lib/modules/2.6.27.31-ipfire-xen/kernel/drivers/net/wireless/ath?k
rm -rf /lib/modules/2.6.27.31-ipfire-xen/kernel/drivers/net/wireless/rtl818?.ko
#Rebuild module dep's
depmod -a
#Don't report the exitcode of depmod
exit 0
