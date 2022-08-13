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

# Check if old IPFire specifc userparameters exist and move out of the way
if [ -f /etc/zabbix_agentd/zabbix_agentd.d/userparameter_pakfire.conf ]; then
	mv /etc/zabbix_agentd/zabbix_agentd.d/userparameter_pakfire.conf \
	   /etc/zabbix_agentd/zabbix_agentd.d/userparameter_pakfire.conf.save
fi

# Check if new IPFire specific config is included in restored config
# and add if required.
grep -q "Include=/var/ipfire/zabbix_agentd/userparameters/\*.conf" /etc/zabbix_agentd/zabbix_agentd.conf
if [ $? -eq 1 ]; then
	echo "" >> /etc/zabbix_agentd/zabbix_agentd.conf
	echo "# This line activates IPFire specific userparameters. " >> /etc/zabbix_agentd/zabbix_agentd.conf
	echo "# See IPFire wiki for details." >> /etc/zabbix_agentd/zabbix_agentd.conf
	echo "# To deactivate them: Comment this line out." >> /etc/zabbix_agentd/zabbix_agentd.conf
	echo "# (DO NOT REMOVE OR ALTER IT as then it will be re-added on next upgrade)" >> /etc/zabbix_agentd/zabbix_agentd.conf
	echo "Include=/var/ipfire/zabbix_agentd/userparameters/*.conf" >> /etc/zabbix_agentd/zabbix_agentd.conf
fi

grep -q "Include=/var/ipfire/zabbix_agentd/zabbix_agentd_ipfire_mandatory.conf" /etc/zabbix_agentd/zabbix_agentd.conf
if [ $? -eq 1 ]; then
	# Remove settings that are now in our own config
	sed -i -e "\|^PidFile=.*$|d" /etc/zabbix_agentd/zabbix_agentd.conf
	sed -i -e "\|^LogFile=.*$|d" /etc/zabbix_agentd/zabbix_agentd.conf
	sed -i -e "\|^LogFileSize=.*$|d" /etc/zabbix_agentd/zabbix_agentd.conf
	sed -i -e "\|^LoadModulePath=.*$|d" /etc/zabbix_agentd/zabbix_agentd.conf
	sed -i -e "\|^Include=/etc/zabbix_agentd/zabbix_agentd\.d/\*\.conf$|d" /etc/zabbix_agentd/zabbix_agentd.conf
	# Include our own config in main config
	echo "" >> /etc/zabbix_agentd/zabbix_agentd.conf
	echo "# Mandatory Zabbix Agent configuration to start and run on IPFire correctly" >> /etc/zabbix_agentd/zabbix_agentd.conf
	echo "# DO NOT REMOVE OR MODIFY THIS LINE:" >> /etc/zabbix_agentd/zabbix_agentd.conf
	echo "Include=/var/ipfire/zabbix_agentd/zabbix_agentd_ipfire_mandatory.conf" >> /etc/zabbix_agentd/zabbix_agentd.conf
fi

# By default, only listen on GREEN
( 
	eval $(/usr/local/bin/readhash /var/ipfire/ethernet/settings)
	if [ -n "${GREEN_ADDRESS}" ]; then
		sed -i -e "s|ListenIP=GREEN_ADDRESS|ListenIP=${GREEN_ADDRESS}|g" /etc/zabbix_agentd/zabbix_agentd.conf
	else
		sed -i -e "\|ListenIP=GREEN_ADDRESS|d" /etc/zabbix_agentd/zabbix_agentd.conf
	fi
) || :

start_service --background ${NAME}
