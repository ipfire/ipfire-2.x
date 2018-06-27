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

core=120

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Remove forgotten PHP file
rm -f /etc/httpd/conf/conf.d/php5.conf

# Delete old PAM libs and symlinks if presant
if ls /lib | grep -q 'libpam.*'; then
    rm -f /lib/libpam*
fi

# Stop services

# Extract files
extract_files

# update linker config
ldconfig

# Update Language cache
/usr/local/bin/update-lang-cache

# Changed and new OpenVPN-2.4 directives will wrote to server.conf and renew CRL while update an core update
if [ -e /var/ipfire/ovpn/server.conf ]; then
	/usr/local/bin/openvpnctrl -k

	# Update configuration directives
	sed -i -e 's/script-security 3 system/script-security 3/' \
		-e '/status .*/ a ncp-disable' /var/ipfire/ovpn/server.conf

	# Disable Path MTU discovery settings
	sed -e "/^mtu-disc/d" -i /var/ipfire/ovpn/server.conf

	# Update the OpenVPN CRL
	openssl ca -gencrl -keyfile /var/ipfire/ovpn/ca/cakey.pem \
		-cert /var/ipfire/ovpn/ca/cacert.pem \
		-out /var/ipfire/ovpn/crls/cacrl.pem \
		-config /var/ipfire/ovpn/openssl/ovpn.cnf

	/usr/local/bin/openvpnctrl -s
fi

# Update OpenVPN N2N configurations
/usr/local/bin/openvpnctrl -kn2n

for file in /var/ipfire/ovpn/n2nconf/*/*.conf; do
	sed -e "/^mtu-disc/d" -i ${file}
done

/usr/local/bin/openvpnctrl -sn2n

# Start services
/etc/init.d/apache restart
/etc/init.d/unbound restart

# Regenerate IPsec configuration
sudo -u nobody /srv/web/ipfire/cgi-bin/vpnmain.cgi
if grep -q "ENABLED=on" /var/ipfire/vpn/settings; then
	/etc/init.d/ipsec restart
fi

# Remove deprecated SSH configuration option
sed -e "/UsePrivilegeSeparation/d" -i /etc/ssh/sshd_config

# Import new Pakfire key
/etc/init.d/pakfire start

# This update needs a reboot...
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
