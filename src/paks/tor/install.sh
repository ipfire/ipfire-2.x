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
# Copyright (C) 2007-2019 IPFire-Team <info@ipfire.org>.                   #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh

# Run Tor as dedicated user and make sure user and group exist
if ! getent group tor &>/dev/null; then
       groupadd -g 119 tor
fi

if ! getent passwd tor; then
       useradd -u 119 -g tor -c "Tor daemon user" -d /var/empty -s /bin/false tor
fi

extract_files
restore_backup ${NAME}

# Adjust some folder permission for new UID/GID
chown -R tor:tor /var/lib/tor
chown -R tor:nobody /var/ipfire/tor

# Tor settings files needs to be writeable by nobody group for WebUI
chmod 664 /var/ipfire/tor/{settings,torrc}

start_service --background ${NAME}
