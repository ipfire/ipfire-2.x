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

core=115

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Stop services
openvpnctrl -k
openvpnctrl -kn2n
/etc/rc.d/init.d/apache stop

# Extract files
extract_files

# Remove files
rm -vf \
	/usr/local/bin/httpscert \
	/srv/web/ipfire/html/dial.cgi

# update linker config
ldconfig

# Update Language cache
/usr/local/bin/update-lang-cache

# Start services
/etc/rc.d/init.d/apache2 start
openvpnctrl -s
openvpnctrl -sn2n

grep -q "captivectrl" /var/spool/cron/root.orig || cat <<EOF >> /var/spool/cron/root.orig
# Cleanup captive clients
%hourly * /usr/bin/captive-cleanup

# Reload captive firewall rules
%nightly * 23-1   /usr/local/bin/captivectrl >/dev/null
EOF
fcrontab -z

# Load captive portal configuration
/etc/rc.d/init.d/firewall restart

# Regenerate IPsec configuration
sudo -u nobody /srv/web/ipfire/cgi-bin/vpnmain.cgi
if grep -q "ENABLED=on" /var/ipfire/vpn/settings; then
	/etc/init.d/ipsec restart
fi

# Let pakfire forget the perl-PDF-API2 package
rm -fv /opt/pakfire/db/rootfiles/perl-PDF-API2
rm -fv /opt/pakfire/db/*/meta-perl-PDF-API2

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
