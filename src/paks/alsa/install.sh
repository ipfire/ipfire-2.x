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
groupadd audio 2>/dev/null
touch /var/lib/alsa/asound.state
if [ -f /etc/asound.state ]; then
	rm /etc/asound.state
fi
restore_backup ${NAME}
ln -svf  ../init.d/alsa /etc/rc.d/rc3.d/S65alsa
ln -svf  ../init.d/alsa /etc/rc.d/rc0.d/K35alsa
ln -svf  ../init.d/alsa /etc/rc.d/rc6.d/K35alsa
start_service ${NAME}
exit 0
