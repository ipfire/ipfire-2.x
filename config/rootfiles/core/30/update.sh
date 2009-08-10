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
# Copyright (C) 2009 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1
extract_files
#Rebuild language cache
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
#Rebuild module dep's
depmod -a
#
# Test if this is a ct'server
#
ctdisk=`ls -l /dev/disk/by-uuid/0bd2211e-4268-442d-9f42-9fb1f8234a7e 2>/dev/null | cut -d">" -f2`
if [ "$ctdisk" == " ../../xvda3" ]; then
	echo "This is a ct-server..."
	#
	# Fix network assignment because 30-persistent-network.rules are overwritten by setup
	# (eg. If you try to configure red=dhcp)
	#
	echo 'KERNEL=="eth0", NAME="green0"'  >  /etc/udev/rules.d/29-ct-server-network.rules
	echo 'KERNEL=="eth1", NAME="red0"'    >> /etc/udev/rules.d/29-ct-server-network.rules
	echo 'KERNEL=="eth2", NAME="blue0"'   >> /etc/udev/rules.d/29-ct-server-network.rules
	echo 'KERNEL=="eth3", NAME="orange0"' >> /etc/udev/rules.d/29-ct-server-network.rules
	#
	# Remove acpi modules autoload
	#
	sed -i 's|^ac|#ac|g' /etc/sysconfig/modules
	sed -i 's|^battery|#battery|g' /etc/sysconfig/modules
	sed -i 's|^button|#button|g' /etc/sysconfig/modules
	sed -i 's|^fan|#fan|g' /etc/sysconfig/modules
	sed -i 's|^processor|#processor|g' /etc/sysconfig/modules
	sed -i 's|^thermal|#thermal|g' /etc/sysconfig/modules
	sed -i 's|^video|#video|g' /etc/sysconfig/modules
	#
	# Disable some initskripts
	#
	echo "#!/bin/bash" > /etc/rc.d/init.d/setclock
	echo "#!/bin/bash" > /etc/rc.d/init.d/keymap
	#
	# Change pakfire trunk from 2.5 to 2.5-ct
	#
	sed -i 's|"2.5"|"2.5-ct"|g' /opt/pakfire/etc/pakfire.conf
fi
