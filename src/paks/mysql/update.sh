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

# Create backup include file if it is missing.
if [ ! -e "/var/ipfire/backup/addons/includes/mysql" ]; then
	cat <<EOF > /var/ipfire/backup/addons/includes/mysql
/etc/my.cnf
/srv/mysql
EOF
fi

# Stop the mysql service
stop_service "${NAME}"

# Make backup
make_backup "${NAME}"

# Update files
remove_files
extract_files

# Restore backup
restore_backup "${NAME}"

# Restart the service
start_service "${NAME}"

exit 0
