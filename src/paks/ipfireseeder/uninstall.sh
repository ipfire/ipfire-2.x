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
stop_service ${NAME}

#prevent erasing the downloaded data at uninstall/update
cat /opt/pakfire/db/rootfiles/ipfireseeder | \
    grep -v "var/ipfire/seeder" | \
    grep -v "var/log/seeder" > /opt/pakfire/db/rootfiles/ipfireseeder.tmp
mv /opt/pakfire/db/rootfiles/ipfireseeder.tmp \
    /opt/pakfire/db/rootfiles/ipfireseeder

grep -v "IPFireSeeder" /var/ipfire/xtaccess/config > /var/ipfire/xtaccess/config.tmp
mv /var/ipfire/xtaccess/config.tmp /var/ipfire/xtaccess/config
chown nobody:nobody /var/ipfire/xtaccess/config
chmod 644 /var/ipfire/xtaccess/config

rm -f /etc/rc.d/rc?.d/???ipfireseeder
rm -f /etc/rc.d/init.d/networking/red.*/??-?-ipfireseeder

remove_files
