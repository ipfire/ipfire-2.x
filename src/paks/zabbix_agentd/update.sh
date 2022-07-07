#!/bin/bash
############################################################################
#                                                                          #
# This file is part of the IPFire Firewall.                                #
#                                                                          #
# IPFire is free software; you can redistribute it and/or modify           #
# it under the terms of the GNU General Public License as published by     #
# the Free Software Foundation; either version 2 of the License, or        #
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
# Copyright (C) 2007 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh

# Check if old sudoers file exists and remove if it was not modified
# or rename to the new zabbix_agentd_user file if it was.
if [ -f /etc/sudoers.d/zabbix.user ]; then
	mv -v /etc/sudoers.d/zabbix.user /etc/sudoers.d/zabbix
fi

if [ -f /etc/sudoers.d/zabbix ]; then
	blake2=$(b2sum /etc/sudoers.d/zabbix | cut -f1 -d" ")
    # from commits 5737a22 & 06fc617
	if [ "$blake2" == "b0f73b107fd3842efc7ef3e30f6d948235aa07d533715476c2d3f58c08379193fdde9ff69aa6e0f5eb6cf4a98b2ed2a6f003f23078a57aff239b34cc29e62a98" ] || \
	   [ "$blake2" == "0628c416a1f217b0962a8ce6d1e339bdb0f0427d86fc06b2e40b63487ffc1a3543562d16f7f954d7fb92cee9764f0261c1663a39dd50bc73fd9b772575c56cfc" ]; then
		rm -vf /etc/sudoers.d/zabbix
	else
		mv -v /etc/sudoers.d/zabbix /etc/sudoers.d/zabbix_agentd_user
	fi
fi

extract_backup_includes
./uninstall.sh
./install.sh

