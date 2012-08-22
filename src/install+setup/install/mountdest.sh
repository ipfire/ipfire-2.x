#!/bin/sh
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2012  IPFire Team  <info@ipfire.org>                     #
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

echo "Scanning for possible destination drives"

# scan sd?
echo "--> sd?"
for DEVICE in `find /sys/block/* -maxdepth 0 -name sd* -or -name vd* -exec basename {} \; | sort | uniq`
do
		if [ "$(grep ${DEVICE} /proc/partitions)" = "" ]; then
			umount /harddisk 2> /dev/null
			echo "${DEVICE} is empty - SKIP"
			continue
		fi
		mount /dev/${DEVICE} /harddisk 2> /dev/null
		if [ -n "$(ls /harddisk/ipfire-*.tlz 2>/dev/null)" ]; then
			umount /harddisk 2> /dev/null
			echo "${DEVICE} is source drive - SKIP"
			continue
		else
			umount /harddisk 2> /dev/null
			mount /dev/${DEVICE}1 /harddisk 2> /dev/null
			if [ -n "$(ls /harddisk/ipfire-*.tlz 2>/dev/null)" ]; then
				umount /harddisk 2> /dev/null
				echo "${DEVICE}1 is source drive - SKIP"
				continue
			else
				umount /harddisk 2> /dev/null
				echo -n "$DEVICE" > /tmp/dest_device
				echo "${DEVICE} - yes, it is our destination"
				exit 1 # (always use /dev/sda as bootdevicename)
			fi
		fi
done

# scan other
echo "--> other"
for DEVICE in `find /sys/block/* -maxdepth 0 ! -name sd* ! -name sr* ! -name fd* ! -name loop* ! -name ram* -exec basename {} \; | sort | uniq`
do
		mount /dev/${DEVICE}p1 /harddisk 2> /dev/null
		if [ -n "$(ls /harddisk/ipfire-*.tlz 2>/dev/null)" ]; then
			umount /harddisk 2> /dev/null
			echo "${DEVICE}p1 is source drive - SKIP"
			continue
		else
			umount /harddisk 2> /dev/null
			if [ "$(grep ${DEVICE} /proc/partitions)" = "" ]; then
				umount /harddisk 2> /dev/null
				echo "${DEVICE} is empty - SKIP"
				continue
			fi
			mount /dev/${DEVICE}1 /harddisk 2> /dev/null
			if [ -n "$(ls /harddisk/ipfire-*.tlz 2>/dev/null)" ]; then
				umount /harddisk 2> /dev/null
				echo "${DEVICE}1 is source drive - SKIP"
				continue
			else
				umount /harddisk 2> /dev/null
				mount /dev/${DEVICE} /harddisk 2> /dev/null
				if [ -n "$(ls /harddisk/ipfire-*.tlz 2>/dev/null)" ]; then
					umount /harddisk 2> /dev/null
					echo "${DEVICE} is source drive - SKIP"
					continue
				else
					echo -n "$DEVICE" > /tmp/dest_device
					echo "${DEVICE} - yes, it is our destination"
					exit 2 # Raid ( /dev/device/diskx )
				fi
			fi
		fi
done

exit 10 # Nothing found
