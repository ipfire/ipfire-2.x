#!/bin/sh
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007  Michael Tremer & Christian Schmidt                      #
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

if [ -e /var/ipfire/ethernet/scanned_nics ]; then
	rm -f /var/ipfire/ethernet/scanned_nics
fi
touch /var/ipfire/ethernet/scanned_nics

for card in `ls /sys/class/net`; do

	#Check if this is an Ethernet device (type=1)
	if [ `cat /sys/class/net/$card/type` == "1" ]; then
		hwaddr=`cat /sys/class/net/$card/address`

		#Check if mac is valid (not 00:00... or FF:FF...)
		if [ ! "$hwaddr" == "00:00:00:00:00:00" ];then
		if [ ! "$hwaddr" == "ff:ff:ff:ff:ff:ff" ];then

			driver=`grep PHYSDEVDRIVER= /sys/class/net/$card/uevent | cut -d"=" -f2`
			type=`grep PHYSDEVBUS= /sys/class/net/$card/uevent | cut -d"=" -f2`
			description=`echo $type: $driver`

			#Get more details for pci and usb devices
			if [ "$type" == "pci" ]; then
				slotname=`grep PCI_SLOT_NAME= /sys/class/net/$card/device/uevent | cut -d"=" -f2`
				name=`lspci -s $slotname | cut -d':' -f3`
				description=`echo $type:$name`
			fi
			if [ "$type" == "usb" ]; then
				bus=`grep DEVICE= /sys/class/net/$card/device/uevent | cut -d"/" -f5`
				dev=`grep DEVICE= /sys/class/net/$card/device/uevent | cut -d"/" -f6`
				#work around the base8 convert
				let bus=`echo 1$bus`-1000
				let dev=`echo 1$dev`-1000
				name=`lsusb -s $bus:$dev | cut -d':' -f3`
				description=`echo $type: $name`
			fi

			echo desc: \"$description\"  >>/var/ipfire/ethernet/scanned_nics
			echo driver: $driver         >>/var/ipfire/ethernet/scanned_nics
			echo network.hwaddr: $hwaddr >>/var/ipfire/ethernet/scanned_nics
		fi
		fi
	fi
done

# Revert Accesspoint marking at mac address
sed -i 's|hwaddr: 06:|hwaddr: 00:|g' /var/ipfire/ethernet/scanned_nics

exit 0
