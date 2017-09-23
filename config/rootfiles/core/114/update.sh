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
# Copyright (C) 2017 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

core=114

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Stop services
ipsec stop
/etc/init.d/squid stop
/etc/init.d/unbound stop
/etc/init.d/apache stop

# Remove old apache configuration files of add-ons
# These will be reinstalled by the updated packages
# as soon as the core update is finished.
rm -f \
	/etc/httpd/conf/vhosts.d/cacti.conf \
	/etc/httpd/conf/vhosts.d/icinga.conf \
	/etc/httpd/conf/vhosts.d/nagios.conf \
	/etc/httpd/conf/vhosts.d/openmailadmin.conf \
	/etc/httpd/conf/vhosts.d/owncloud.conf \
	/etc/httpd/conf/vhosts.d/phpSANE.conf

# Extract files
extract_files

# update linker config
ldconfig

# Remove some files
rm -f /usr/sbin/htpasswd

# Update Language cache
/usr/local/bin/update-lang-cache

# Start services
/etc/init.d/unbound start
/etc/init.d/apache start
/etc/init.d/squid start

if grep -q "ENABLED=on" /var/ipfire/vpn/settings; then
	ipsec start
fi

#
# After pakfire has ended run it again and update all addons
# this is needed for apache update.
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
echo 'touch /var/run/need_reboot ' >> /tmp/pak_update
#
killall -KILL pak_update
chmod +x /tmp/pak_update
/tmp/pak_update &

# This update need a reboot...
touch /var/run/need_reboot

# Finish
/etc/init.d/fireinfo start
sendprofile

# Update grub config to display new core version
if [ -e /boot/grub/grub.cfg ]; then
	grub-mkconfig -o /boot/grub/grub.cfg
fi

sync

# Don't report the exitcode last command
exit 0
