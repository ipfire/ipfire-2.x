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

#Create a backupinclude if it not exist
if [ ! -e "/var/ipfire/backup/addons/includes/vsftpd" ]; then
    echo /etc/vsftpd.conf > /var/ipfire/backup/addons/includes/vsftpd
    echo /etc/vsftpd.user_list >> /var/ipfire/backup/addons/includes/vsftpd
fi
#Fix wrong backupinclude
sed 's|^etc/vsftpd.conf|/etc/vsftpd.conf|g' /var/ipfire/backup/addons/includes/vsftpd
sed 's|^vsftpd.user_list|/vsftpd.user_list|g' /var/ipfire/backup/addons/includes/vsftpd
make_backup ${NAME}
#Remove userdate from rootfile
cat /opt/pakfire/db/rootfiles/vsftpd | \
    grep -v "home/ftp" | \
    grep -v "var/ftp" > /opt/pakfire/db/rootfiles/vsftpd.tmp
mv /opt/pakfire/db/rootfiles/vsftpd.tmp /opt/pakfire/db/rootfiles/vsftpd 

remove_files
