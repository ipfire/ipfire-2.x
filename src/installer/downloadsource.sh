#!/bin/sh
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2010  IPFire Team  <info@ipfire.org>                          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

#lfs change the url while build!
IPFireISO=ipfire.iso
#

#Get user defined download from boot cmdline
grep "netinstall=" /proc/cmdline > /dev/null && CMDLINE=1
if ( [ "$CMDLINE" == "1" ]); then
	read CMDLINE < /proc/cmdline
	POS=${CMDLINE%%netinstall*}
	POS=${#POS}
	IPFireISO=`echo ${CMDLINE:POS} | cut -d"=" -f2 | cut -d" " -f1`
fi

echo
echo "Configure Network with DHCP..."
dhcpcd
echo
echo "Sleep 15s..."
sleep 15
echo
echo "Download with wget..."
wget $IPFireISO -O /tmp/download.iso -t3 -U IPFire_NetInstall/2.x
wget $IPFireISO.md5 -O /tmp/download.iso.md5 -t3 -U IPFire_NetInstall/2.x
echo
echo "Checking download..."
md5_file=`md5sum /tmp/download.iso | cut -d" " -f1`
md5_down=`cat /tmp/download.iso.md5 | cut -d" " -f1`
if [ "$md5_file" == "$md5_down" ]; then
	echo -n "/tmp/download.iso" > /tmp/source_device
	exit 0
fi
echo "Error - SKIP"
exit 10
