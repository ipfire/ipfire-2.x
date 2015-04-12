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
# Copyright (C) 2014 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

# Remove old core updates from pakfire cache to save space...
core=89
for (( i=1; i<=$core; i++ ))
do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Stop services
/etc/init.d/ipsec stop

# Remove old files
rm -f /usr/local/sbin/setup

# Extract files
extract_files

# Update /etc/sysconfig/createfiles
cat <<EOF >> /etc/sysconfig/createfiles
/var/run/ovpnserver.log file    644     nobody  nobody
/var/run/openvpn        dir     644     nobody  nobody
EOF

# Update /etc/collectd.conf
if ! grep -q "collectd.vpn" /etc/collectd.conf; then
	echo "include \"/etc/collectd.vpn\"" >> /etc/collectd.conf
fi

# Generate ddns configuration file
sudo -u nobody /srv/web/ipfire/cgi-bin/ddns.cgi

# Start services
/etc/init.d/dnsmasq restart
if [ `grep "ENABLED=on" /var/ipfire/vpn/settings` ]; then
	/etc/init.d/ipsec start
fi

# Update Language cache
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"

# Prevent uninstall sqlite (now common package).
rm -f \
	/opt/pakfire/db/*/meta-sqlite \
	/opt/pakfire/db/rootfiles/sqlite

# Update OpenVPN/collectd configuration
/usr/sbin/ovpn-collectd-convert
chown nobody.nobody /var/ipfire/ovpn/collectd.vpn

# Fix #10625
mkdir -p /etc/logrotate.d

sync

# This update need a reboot...
#touch /var/run/need_reboot

# Finish
/etc/init.d/fireinfo start
sendprofile

# Don't report the exitcode last command
exit 0
