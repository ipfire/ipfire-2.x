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

extract_files

ln -svf  ../init.d/mysql /etc/rc.d/rc0.d/K26mysql
ln -svf  ../init.d/mysql /etc/rc.d/rc3.d/S34mysql
ln -svf  ../init.d/mysql /etc/rc.d/rc6.d/K26mysql

restore_backup "${NAME}"

start_service "${NAME}"

COUNTER=0
while [ "$COUNTER" -lt "10" ]; do
	[ -e "/var/run/mysql/mysql.sock" ] && break
	echo "MySQL server is still not running. Waiting 5 seconds."
	sleep 5
	COUNTER=$(($COUNTER + 1))
done 

[ -e "/var/run/mysql/mysql.sock" ] || (echo "MySQL still noch running... Exiting."; \
	exit 1)

mysqladmin -u root --password='' password 'mysqlfire'
