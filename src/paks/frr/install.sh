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

if ! getent group frr &>/dev/null; then
	groupadd -r frr
fi

if ! getent group frrvty &>/dev/null; then
	groupadd -r frrvty
fi

if ! getent passwd frr &>/dev/null; then
	useradd -r frr -g frr -s /bin/false -b /var/empty -G frrvty
fi

# Extract files
extract_files

# Restore any backups
restore_backup "${NAME}"

# Start services
start_service "${NAME}"

# Enable autostart
ln -svf ../init.d/frr /etc/rc.d/rc0.d/K40frr
ln -svf ../init.d/frr /etc/rc.d/rc3.d/S50frr
ln -svf ../init.d/frr /etc/rc.d/rc6.d/K40frr

exit 0
