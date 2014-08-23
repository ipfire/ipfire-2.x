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
core=80
for (( i=1; i<=$core; i++ ))
do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Stop services
/etc/init.d/ipsec stop

# Remove old strongswan files
rm -f \
	/etc/strongswan.d/charon/unity.conf \
	/usr/lib/ipsec/plugins/libstrongswan-unity.so \
	/usr/share/strongswan/templates/config/plugins/unity.conf

rm -f /usr/local/bin/setddns.pl

# Extract files
extract_files

# Start services
/etc/init.d/dnsmasq restart
if [ `grep "ENABLED=on" /var/ipfire/vpn/settings` ]; then
	/etc/init.d/ipsec start
fi


# Update Language cache
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"

# Uninstall the libgpg-error package.
rm -f \
	/opt/pakfire/db/installed/meta-libgpg-error \
	/opt/pakfire/db/rootfiles/libgpg-error

# Fix broken proxy configuration permissions
chown -R nobody.nobody \
	/var/ipfire/proxy/advanced \
	/var/ipfire/proxy/acl-1.4 \
	/var/ipfire/proxy/enable \
	/var/ipfire/proxy/settings \
	/var/ipfire/proxy/squid.conf \
	/var/ipfire/proxy/transparent

# Regenerate squid configuration file
sudo -u nobody /srv/web/ipfire/cgi-bin/proxy.cgi

# Generate ddns configuration file
sudo -u nobody /srv/web/ipfire/cgi-bin/ddns.cgi

# Update crontab
sed -i /var/spool/cron/root.orig -e "/setddns.pl/d"

grep -q /usr/bin/ddns /var/spool/cron/root.orig || cat <<EOF >> /var/spool/cron/root.orig

# Update dynamic DNS records every five minutes.
# Force an update once a month
*/5 * * * *	[ -f "/var/ipfire/red/active" ] && /usr/bin/ddns update-all
3 2 1 * *	[ -f "/var/ipfire/red/active" ] && /usr/bin/ddns update-all --force
EOF

fcrontab -z &>/dev/null

sync

# This update need a reboot...
#touch /var/run/need_reboot

# Finish
/etc/init.d/fireinfo start
sendprofile

# Don't report the exitcode last command
exit 0
