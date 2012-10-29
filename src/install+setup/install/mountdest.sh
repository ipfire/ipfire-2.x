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

# Set histchars to an empty string so we are able to replace an
# exclamation mark.
histchars=

echo "Scanning for possible destination drives"

function _mount() {
	local what=${1}

	# Don't mount if the device does not exist.
	[ -e "${what}" ] || return 1

	mount ${what} /harddisk 2>/dev/null
}

function _umount() {
	umount -l /harddisk 2>/dev/null
}

function check_source_drive() {
	local device="/dev/${1}"

	local ret=1
	local dev
	for dev in ${device} ${device}1; do
		# Mount the device (if possible).
		_mount ${dev} || continue

		if [ -n "$(ls /harddisk/ipfire-*.tlz 2>/dev/null)" ]; then
			ret=0
		fi

		_umount

		# Stop if the device has been detected as a source drive.
		[ "${ret}" = "0" ] && break
	done

	return ${ret}
}

for path in /sys/block/*; do
	device=$(basename ${path})

	# Skip devices which cannot be used.
	case "${device}" in
		# Virtual devices.
		loop*|ram*)
			continue
			;;
		# Floppy.
		fd*)
			continue
			;;
		# Cd/Tape.
		sr*)
			continue
			;;
	esac

	# Replace any exclamation marks (e.g. cciss!c0d0).
	device=${device//!/\/}

	# Guess if this could be a raid device.
	for dev in ${device} ${device}p1; do
		if [ -e "/dev/${dev}" ]; then
			device=${dev}
			break
		fi
	done

	echo "Checking ${device}"
	if check_source_drive ${device}; then
		echo "  is source drive - skipping"
		continue
	fi

	# Found it.
	echo "  OK, this is it..."
	echo -n "${device}" > /tmp/dest_device

	# Exit code table:
	#  1: sda
	#  2: RAID
	# 10: nothing found
	case "${device}" in
		*p1|*c0d0)
			exit 2
			;;
		*)
			exit 1
			;;
	esac
done

# Nothing found.
exit 10
