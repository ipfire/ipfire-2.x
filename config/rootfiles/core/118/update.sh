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

core=118

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Stop services
/etc/init.d/snort stop
/etc/init.d/squid stop
/etc/init.d/unbound stop

# Delete files
rm -rvf \
	/etc/httpd/conf.d/php5.conf \
	/etc/pear.conf \
	/etc/php.ini \
	/usr/bin/phar \
	/usr/bin/phar.phar \
	/usr/bin/php \
	/usr/lib/apache/libphp5.so \
	/usr/lib/php

# Extract files
extract_files

# update linker config
ldconfig

# Update Language cache
/usr/local/bin/update-lang-cache

# remove dropped packages
for package in python-libvirt owncloud mediatomb openmailadmin \
		tunctl phpSANE cacti nagios nagiosql ffmpeg-libs \
		sslscan pound vsftpd imspector tripwire; do
	if [ -e /opt/pakfire/db/installed/meta-$package ]; then
		pakfire remove -y $package
	fi
	rm -f /opt/pakfire/db/installed/meta-$package
	rm -f /opt/pakfire/db/meta/meta-$package
	rm -f /opt/pakfire/db/rootfiles/$package
done

# Start services
/etc/init.d/unbound start
/etc/init.d/apache restart
/etc/init.d/squid start
/etc/init.d/snort start

# This update need a reboot...
#touch /var/run/need_reboot

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
