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
rm -f /var/cache/pakfire core-upgrade-*.ipfire
#
#Stop services
echo Stopping Proxy
/etc/init.d/squid stop 2>/dev/null
echo Stopping vpn-watch
killall vpn-watch

#
#Extract files
extract_files

# Remove disable cron mails...
sed "s|MAILTO=root|MAILTO=|g" < /var/spool/cron/root.orig > /var/tmp/root.tmp
fcrontab /var/tmp/root.tmp

#
#Start services
echo Starting Proxy
/etc/init.d/squid start 2>/dev/null
echo Rewriting Outgoing FW Rules
/var/ipfire/outgoing/bin/outgoingfw.pl
echo Starting vpn-watch
/usr/local/bin/vpn-watch &

#
#Update Language cache
#perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"

#Rebuild module dep's
#depmod 2.6.32.28-ipfire
#depmod 2.6.32.28-ipfire-pae
#depmod 2.6.32.28-ipfire-xen

#
#Finish
#Don't report the exitcode last command
exit 0
