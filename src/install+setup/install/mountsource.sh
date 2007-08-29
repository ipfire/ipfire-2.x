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

echo "Scanning source media"

# scan CDROM devices
for DEVICE in $(kudzu -qps -t 30 -c CDROM | grep device: | cut -d ' ' -f 2 | sort | uniq); do
		mount /dev/${DEVICE} /cdrom 2> /dev/null
		if [ -n "$(ls /cdrom/ipfire-*.tbz2 2>/dev/null)" ]; then
			echo -n ${DEVICE} > /tmp/source_device
			echo "Found tarball on ${DEVICE}"
		else
			echo "Found no tarballs on ${DEVICE} - SKIP"
		fi
		umount /cdrom 2> /dev/null
done

# scan HD device (usb sticks, etc.)
for DEVICE in $(kudzu -qps -t 30 -c HD | grep device: | cut -d ' ' -f 2 | sort | uniq); do
		mount /dev/${DEVICE}1 /cdrom 2> /dev/null
		if [ -n "$(ls /cdrom/ipfire-*.tbz2 2>/dev/null)" ]; then
			echo -n ${DEVICE}1 > /tmp/source_device
			echo "Found tarball on ${DEVICE}"
		else
			umount /cdrom 2> /dev/null
			echo "Found no tarballs on ${DEVICE} - SKIP"
		fi
		umount /cdrom 2> /dev/null
done

if [ -e "/tmp/source_device" ]; then
	mount /dev/$(cat /tmp/source_device) /cdrom 2> /dev/null
	exit 0
else
	exit 10
fi
