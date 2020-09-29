#!/bin/sh
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2011  IPFire Team  <info@ipfire.org>                          #
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

		#Check that is no VLAN if
		if [[ ! "$card" =~ "[.]" ]]; then

			#check if this not a bridge
			if [ ! -e /sys/class/net/$card/brforward ]; then

				#Check if mac is valid (not 00:00... or FF:FF...)
				if [ ! "$hwaddr" == "00:00:00:00:00:00" ];then
				if [ ! "$hwaddr" == "ff:ff:ff:ff:ff:ff" ];then

					driver=`grep DRIVER= /sys/class/net/$card/device/uevent | cut -d"=" -f2`
					type=`grep MODALIAS= /sys/class/net/$card/device/uevent | cut -d"=" -f2 | cut -d":" -f1`

					#Default if not available in /sys/class/net
					if [ "a$type" == "a" ]; then
						type="???"
					fi
					if [ "a$driver" == "a" ]; then
						driver="Unknown Network Interface ($card)"
					fi
					description=`echo $type: $driver`

					#Get more details for pci and usb devices
					if [ "$type" == "pci" ]; then
						slotname=`grep PCI_SLOT_NAME= /sys/class/net/$card/device/uevent | cut -d"=" -f2`
						name=`lspci -s $slotname | cut -d':' -f3 | cut -c 2-`
						description=`echo $type: $name`
					fi
					if [ "$type" == "usb" ]; then
						bus=`grep DEVICE= /sys/class/net/$card/device/uevent | cut -d"/" -f5`
						dev=`grep DEVICE= /sys/class/net/$card/device/uevent | cut -d"/" -f6`
						#work around the base8 convert
						let bus=`echo 1$bus`-1000
						let dev=`echo 1$dev`-1000
						name=`lsusb -s $bus:$dev | cut -d':' -f3 | cut -c 6-`
						#kernel higher 3.2 changes
						if [ "$name" == "" ]; then
							vid=`grep PRODUCT= /sys/class/net/$card/device/uevent | cut -d"=" -f2 | cut -d"/" -f1`
							pid=`grep PRODUCT= /sys/class/net/$card/device/uevent | cut -d"=" -f2 | cut -d"/" -f2`
							name=`lsusb -d $vid:$pid | cut -d':' -f3 | cut -c 6-`
						fi
						description=`echo $type: $name`
					fi

					echo desc: \"$description\"  >>/var/ipfire/ethernet/scanned_nics
					echo driver: $driver         >>/var/ipfire/ethernet/scanned_nics
					echo network.hwaddr: $hwaddr >>/var/ipfire/ethernet/scanned_nics
				fi
				fi
			fi
		fi
	fi
done

exit 0
