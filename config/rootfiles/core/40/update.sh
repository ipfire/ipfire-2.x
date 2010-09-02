#!/bin/bash
############################################################################
#                                                                          #
# This file is part of the IPFire Firewall.                                #
#                                                                          #
# IPFire is free software; you can redistribute it and/or modify           #
# it under the terms of the GNU General Public License as published by     #
# the Free Software Foundation; either version 3 of the License, or        #
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
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

#
#Stop services
/usr/local/bin/openvpnctrl -k
#
#Extract files
extract_files
#
#Remove old python files...
rm -rf /usr/lib/python2.4

#
#Start services
/usr/local/bin/openvpnctrl -s

#
#Update Language cache
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"

# Change var lock size to 8MB
grep -v "/var/lock" /etc/fstab > /tmp/fstab.tmp
mv /tmp/fstab.tmp /etc/fstab
echo non        /var/lock        tmpfs   defaults,size=8M      0       0 >> /etc/fstab


#Rebuild module dep's
depmod 2.6.32.15-ipfire
depmod 2.6.32.15-ipfire-xen

#Create the misssing mac group
mkdir /var/ipfire/outgoing/macgroups
chown nobody.nobody /var/ipfire/outgoing/macgroups

#
#Finish
#Don't report the exitcode last command
exit 0
