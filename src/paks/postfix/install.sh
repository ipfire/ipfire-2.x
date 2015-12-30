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
restore_backup ${NAME}
postalias /etc/aliases
# Set postfix's hostname
postconf -e "myhostname=$(hostname -f)"

start_service ${NAME}

# Enable autostart for postfix
ln -sf  ../init.d/postfix /etc/rc.d/rc0.d/K25postfix
ln -sf  ../init.d/postfix /etc/rc.d/rc3.d/S35postfix
ln -sf  ../init.d/postfix /etc/rc.d/rc6.d/K25postfix

# Update alternatives
/usr/sbin/alternatives --install /usr/sbin/sendmail sendmail /usr/sbin/sendmail.postfix 15
