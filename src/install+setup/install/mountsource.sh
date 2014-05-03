#!/bin/sh
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2013  IPFire Team  <info@ipfire.org>                     #
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

#lfs patch source here...
version=FullIPFireVersion
#

echo "Scanning source media"

# scan all Block devices
for DEVICE in `find /sys/block/* -maxdepth 0 ! -name fd* ! -name loop* ! -name ram* -exec basename {} \;`
do
		mount /dev/${DEVICE} /cdrom 2> /dev/null
		if [ -n "$(ls /cdrom/${version}.media 2>/dev/null)" ]; then
			echo -n ${DEVICE} > /tmp/source_device
			echo "Found ${version} on ${DEVICE}"
			exit 0
		else
			echo "not found on ${DEVICE} - SKIP"
		fi
		umount /cdrom 2> /dev/null
done

# scan all Partitions on block devices
for DEVICE in `find /sys/block/* -maxdepth 0 ! -name fd* ! -name loop* ! -name ram* -exec basename {} \;`
do
	for DEVICEP in $(ls /dev/${DEVICE}? | sed "s/\/dev\///" 2> /dev/null);do
		mount /dev/${DEVICEP} /cdrom 2> /dev/null
		if [ -n "$(ls /cdrom/${version}.media 2>/dev/null)" ]; then
			echo -n ${DEVICEP} > /tmp/source_device
			echo "Found ${version} on ${DEVICEP}"
			exit 0
		else
			echo "not found on ${DEVICEP} - SKIP"
		fi
		umount /cdrom 2> /dev/null
	done
done

# scan all Partitions on raid/mmc devices
for DEVICE in `find /sys/block/* -maxdepth 0 ! -name fd* ! -name loop* ! -name ram* -exec basename {} \;`
do
	for DEVICEP in $(ls /dev/${DEVICE}p? | sed "s/\/dev\///" 2> /dev/null);do
		mount /dev/${DEVICEP} /cdrom 2> /dev/null
		if [ -n "$(ls /cdrom/${version}.media 2>/dev/null)" ]; then
			echo -n ${DEVICEP} > /tmp/source_device
			echo "Found ${version} on ${DEVICEP}"
			exit 0
		else
			echo "not found on ${DEVICEP} - SKIP"
		fi
		umount /cdrom 2> /dev/null
	done
done

exit 10
