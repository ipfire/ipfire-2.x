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
# Copyright (C) 2011 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

#
# Remove old core updates from pakfire cache to save space...
core=52
for (( i=1; i<=$core; i++ ))
do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

#
#Stop services

/etc/init.d/ipsec stop

#
# Remove old strongswan libs
rm -rf /usr/lib/libcharon.so
rm -rf /usr/lib/libcharon.so.0
rm -rf /usr/lib/libcharon.so.0.0.0
rm -rf /usr/lib/libhydra.so
rm -rf /usr/lib/libhydra.so.0
rm -rf /usr/lib/libhydra.so.0.0.0
rm -rf /usr/lib/libstrongswan.so
rm -rf /usr/lib/libstrongswan.so.0
rm -rf /usr/lib/libstrongswan.so.0.0.0
rm -rf /usr/libexec/ipsec/plugins

#
#Extract files
extract_files

#
#Start services

if [ `grep "ENABLED=on" /var/ipfire/vpn/settings` ]; then
	/etc/init.d/ipsec start
fi

#
#Update Language cache
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"

#Rebuild module dep's
#depmod 2.6.32.45-ipfire     >/dev/null 2>&1
#depmod 2.6.32.45-ipfire-pae >/dev/null 2>&1
#depmod 2.6.32.45-ipfire-xen >/dev/null 2>&1

## Change version of Pakfire.conf
##
#OLDVERSION=`grep "version = " /opt/pakfire/etc/pakfire.conf | cut -d'"' -f2`
#NEWVERSION="2.9"
#sed -i "s|$OLDVERSION|$NEWVERSION|g" /opt/pakfire/etc/pakfire.conf
##
## After pakfire has ended run it again and update the lists and do upgrade
##
#echo '#!/bin/bash'                                        >  /tmp/pak_update
#echo 'while [ "$(ps -A | grep " update.sh")" != "" ]; do' >> /tmp/pak_update
#echo '    sleep 1'                                        >> /tmp/pak_update
#echo 'done'                                               >> /tmp/pak_update
#echo 'while [ "$(ps -A | grep " pakfire")" != "" ]; do'   >> /tmp/pak_update
#echo '    sleep 1'                                        >> /tmp/pak_update
#echo 'done'                                               >> /tmp/pak_update
#echo '/opt/pakfire/pakfire update -y --force'             >> /tmp/pak_update
#echo '/opt/pakfire/pakfire upgrade -y'                    >> /tmp/pak_update
#echo '/opt/pakfire/pakfire upgrade -y'                    >> /tmp/pak_update
#echo '/opt/pakfire/pakfire upgrade -y'                    >> /tmp/pak_update
#echo '/usr/bin/logger -p syslog.emerg -t core-upgrade-44 "Upgrade finished. If you use a customized grub.cfg"' >> /tmp/pak_update
#echo '/usr/bin/logger -p syslog.emerg -t core-upgrade-44 "Check it before reboot !!!"' >> /tmp/pak_update
#echo '/usr/bin/logger -p syslog.emerg -t core-upgrade-44 " *** Please reboot... *** "' >> /tmp/pak_update
#echo 'touch /var/run/need_reboot ' >> /tmp/pak_update
#
#chmod +x /tmp/pak_update
#/tmp/pak_update &
#echo
#echo Please wait until pakfire has ended...
#echo

#
#Finish
/etc/init.d/fireinfo start
sendprofile
#Don't report the exitcode last command
exit 0
