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
# Copyright (C) 2016 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

core=106

function exit_with_error() {
	# Set last succesfull installed core.
	echo $(($core-1)) > /opt/pakfire/db/core/mine
	/usr/bin/logger -p syslog.emerg -t ipfire \
		"core-update-${core}: $1"
	exit $2
}

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done


# Stop services
/etc/init.d/squid stop
/etc/init.d/ipsec stop
/etc/init.d/dnsmasq stop

# Extract files
extract_files

# Delete dnsmasq
rm -vf \
	/etc/rc.d/init.d/dnsmasq \
	/etc/rc.d/init.d/networking/red.down/05-RS-dnsmasq \
	/etc/rc.d/init.d/networking/red.up/05-RS-dnsmasq \
	/usr/sbin/dnsmasq

# delete unbound link after network start
rm -vf /etc/rc.d/rc3.d/S21unbound

# Delete old net-traffic stuff
rm -vrf \
	/etc/rc.d/helper/writeipac.pl \
	/etc/rc.d/init.d/networking/red.up/40-ipac \
	/var/ipfire/net-traffic \
	/var/log/net-traffic.log*

# update linker config
ldconfig

grep -q unbound-anchor /var/spool/cron/root.orig || cat <<EOF >> /var/spool/cron/root.orig

# Update DNS trust anchor
%daily,random * * @runas(nobody) /usr/sbin/unbound-anchor -a /var/lib/unbound/root.key -c /etc/unbound/icannbundle.pem
EOF

# Update Language cache
/usr/local/bin/update-lang-cache

# Start services
/etc/init.d/unbound start
/etc/init.d/squid start
if grep -q "ENABLED=on" /var/ipfire/vpn/settings; then
	/etc/init.d/ipsec start
fi

# Restart DHCP server to import leases into unbound
/etc/init.d/dhcp restart

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
