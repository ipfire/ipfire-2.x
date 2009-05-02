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
			exit 0
		else
			echo "Found no tarballs on ${DEVICE} - SKIP"
		fi
		umount /cdrom 2> /dev/null
done

# scan HD device part1 (usb sticks, etc.)
for DEVICE in $(kudzu -qps -t 30 -c HD | grep device: | cut -d ' ' -f 2 | sort | uniq); do
		mount /dev/${DEVICE}1 /cdrom 2> /dev/null
		if [ -n "$(ls /cdrom/ipfire-*.tbz2 2>/dev/null)" ]; then
			echo -n ${DEVICE}1 > /tmp/source_device
			echo "Found tarball on ${DEVICE}1"
			exit 0
		else
			echo "Found no tarballs on ${DEVICE}1 - SKIP"
		fi
		umount /cdrom 2> /dev/null
done

# scan HD device unpart (usb sticks, etc.)
for DEVICE in $(kudzu -qps -t 30 -c HD | grep device: | cut -d ' ' -f 2 | sort | uniq); do
		mount /dev/${DEVICE} /cdrom 2> /dev/null
		if [ -n "$(ls /cdrom/ipfire-*.tbz2 2>/dev/null)" ]; then
			echo -n ${DEVICE} > /tmp/source_device
			echo "Found tarball on ${DEVICE}"
			exit 0
		else
			echo "Found no tarballs on ${DEVICE} - SKIP"
		fi
		umount /cdrom 2> /dev/null
done

exit 10
