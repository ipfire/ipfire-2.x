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
# Copyright (C) 2010 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
./uninstall.sh
extract_files

VERSION=$(cat /opt/pakfire/db/installed/meta-squidclamav | grep Release | cut -d" " -f2)

if [ "$VERSION" -gt "10" ]; then
 restore_backup ${NAME}
fi

if [ "$VERSION" -lt "11" ]; then
 sed -e "s|logfile.*|logfile /var/log/squid/squidclamav.log|g" /etc/squidclamav.conf
fi

if [ "$VERSION" -lt "16" ]; then
 sed -e "s/proxy none//g" -i /etc/squidclamav.conf
 sed -e "s/^#squid_ip 127\.0\.0\.1/squid_ip 127\.0\.0\.1/g" \
     -e "s/^#squid_port 3128/squid_port 800/g" \
     -e "s/^#trust_cache 1/trust_cache 1/g" -i /etc/squidclamav.conf

 # Fix permissions.
 chmod 664 /etc/squidclamav.conf
 chown root.nobody /etc/squidclamav.conf

 # Regenerate configuration files.
 perl /srv/web/ipfire/cgi-bin/proxy.cgi
fi
 
/etc/init.d/squid restart
