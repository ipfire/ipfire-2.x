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

if ! getent group zabbix &>/dev/null; then
	groupadd -g 118 zabbix
fi

if ! getent passwd zabbix; then
	useradd -u 118 -g zabbix -d /var/empty -s /bin/false zabbix
fi

extract_files

# Create symlinks for runlevel interaction.
ln -sf ../init.d/zabbix_agentd /etc/rc.d/rc3.d/S65zabbix_agentd
ln -sf ../init.d/zabbix_agentd /etc/rc.d/rc0.d/K02zabbix_agentd
ln -sf ../init.d/zabbix_agentd /etc/rc.d/rc6.d/K02zabbix_agentd

# Create additonal directories and set permissions
[ -d /var/log/zabbix ] || ( mkdir -pv /var/log/zabbix && chown zabbix.zabbix /var/log/zabbix )
[ -d /usr/lib/zabbix ] || ( mkdir -pv /usr/lib/zabbix && chown zabbix.zabbix /usr/lib/zabbix )

restore_backup ${NAME}
start_service --background ${NAME}
