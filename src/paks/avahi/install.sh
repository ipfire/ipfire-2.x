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

# Create Username and group.
getent group avahi >/dev/null || groupadd -r avahi
getent passwd avahi >/dev/null || \
      useradd -r -g avahi -d /var/run/avahi-daemon -s /sbin/nologin \
      -c "Avahi mDNS daemon" avahi

extract_files
ln -svf  ../init.d/avahi /etc/rc.d/rc3.d/S65avahi
ln -svf  ../init.d/avahi /etc/rc.d/rc0.d/K35avahi
ln -svf  ../init.d/avahi /etc/rc.d/rc6.d/K35avahi
restore_backup ${NAME}

# Reload dbus to load avahi configuration
/etc/init.d/messagebus reload

start_service --background ${NAME}
