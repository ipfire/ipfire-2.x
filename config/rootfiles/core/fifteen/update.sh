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
# Copyright (C) 2013 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

#
# Remove old core updates from pakfire cache to save space...
core=74
for (( i=1; i<=$core; i++ ))
do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Stop services


# Extract files
extract_files

# Start services


# Update Language cache
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"

# Remove old openssl engines
rm -rf /usr/lib/engines

# Remove old initscripts
rm -f /etc/rc.d/init.d/networking/red.up/22-outgoingfwctrl
rm -f /etc/rc.d/init.d/networking/red.up/25-portfw
rm -f /etc/rc.d/init.d/networking/red.up/26-xtaccess

# Remove old firewallscripts
rm -f /usr/local/bin/setportfw
rm -f /usr/local/bin/setdmzholes
rm -f /usr/local/bin/setxtaccess
rm -f /usr/local/bin/outgoingfwctrl

# Remove old CGI files
rm -f /srv/web/ipfire/cgi-bin/{dmzholes,outgoingfw,portfw,xtaccess}.cgi

# Generate chains for new firewall
/sbin/iptables -N INPUTFW
/sbin/iptables -N FORWARDFW
/sbin/iptables -N POLICYFWD
/sbin/iptables -N POLICYIN
/sbin/iptables -N POLICYOUT
/sbin/iptables -t nat -N NAT_SOURCE
/sbin/iptables -t nat -N NAT_DESTINATION

# Convert firewall configuration
/usr/sbin/convert-xtaccess
/usr/sbin/convert-outgoingfw
/usr/sbin/convert-portfw
/usr/sbin/convert-dmz

# Remove old firewall configuration files
rm -rf /var/ipfire/{dmzholes,portfw,outgoing,xtaccess}

sync

# This update need a reboot...
touch /var/run/need_reboot

# Finish
# Update the fireinfo profile
(
	/etc/init.d/fireinfo start
	sendprofile
) >/dev/null 2>&1 &

exit 0
