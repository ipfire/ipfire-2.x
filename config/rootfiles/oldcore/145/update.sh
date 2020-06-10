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
# Copyright (C) 2020 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

core=145

exit_with_error() {
	# Set last succesfull installed core.
	echo $(($core-1)) > /opt/pakfire/db/core/mine
	# force fsck at next boot, this may fix free space on xfs
	touch /forcefsck
	# don't start pakfire again at error
	killall -KILL pak_update
	/usr/bin/logger -p syslog.emerg -t ipfire \
		"core-update-${core}: $1"
	exit $2
}

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Remove files

# Stop services
/etc/init.d/vnstat stop
/etc/init.d/squid stop
/etc/init.d/suricata stop

# Prepare OpenVPN for update
/usr/local/bin/openvpnctrl -k
/usr/local/bin/openvpnctrl -kn2n

# Extract files
extract_files

# update linker config
ldconfig

# update rng init
rm /etc/rc.d/rc0.d/K45random
rm /etc/rc.d/rc6.d/K45random
mv /etc/rc.d/rc3.d/S00random /etc/rc.d/rcsysinit.d/S66random
mv /etc/rc.d/rcsysinit.d/S92rngd /etc/rc.d/rcsysinit.d/S65rngd

# remove converted urlfilter database to force rebuilt
rm -f /var/ipfire/urlfilter/blacklists/*/*.db
rm -f /var/ipfire/urlfilter/blacklists/*/*/*.db

# remove packages that are included now in core
for package in perl-DBI perl-DBD-SQLite; do
        rm -f /opt/pakfire/db/installed/meta-$package
        rm -f /opt/pakfire/db/meta/meta-$package
        rm -f /opt/pakfire/db/rootfiles/$package
done

# Enable OpenVPN metrics collection
sed -E -i /var/ipfire/ovpn/server.conf \
	-e "/^client-(dis)?connect/d"

cat <<EOF >> /var/ipfire/ovpn/server.conf
# Log clients connecting/disconnecting
client-connect "/usr/sbin/openvpn-metrics client-connect"
client-disconnect "/usr/sbin/openvpn-metrics client-disconnect"
EOF

# Start services
/etc/init.d/vnstat start
/etc/init.d/unbound restart
/etc/init.d/suricata start
/etc/init.d/squid start

# Start OpenVPN again
/usr/local/bin/openvpnctrl -s
/usr/local/bin/openvpnctrl -sn2n

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# This update needs a reboot...
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
