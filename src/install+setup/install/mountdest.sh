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
	device_=${device//!/\/}

	# Guess if this could be a raid device.
	for dev in ${device_} ${device_}p1; do
		if [ -e "/dev/${dev}" ]; then
			device=${dev}
			break
		fi
	done

	echo "Checking ${device_}"
	if check_source_drive ${device_}; then
		echo "  is source drive - skipping"
		continue
	fi

	device_size=$(cat /sys/block/${device}/size)
	if [ "${device_size}" = "0" ]; then
		echo "  is empty - skipping"
		continue
	fi

	# Found it.
	echo "  OK, this is it..."
	echo -n "${device_}" > /tmp/dest_device

	# Disk size to GiB.
	device_size=$(( ${device_size} / 2097152 ))

	# Build string with drive details
	device_str="/dev/${device_} - ${device_size} GiB -"
	device_str="${device_str} $(cat /sys/block/${device}/device/vendor)"
	device_str="${device_str} $(cat /sys/block/${device}/device/model)"

	# Remove all whitespace.
	device_str=$(echo ${device_str})

	echo -n "${device_str}" > /tmp/dest_device_info

	# Exit code table:
	#  1: sda
	#  2: RAID
	# 10: nothing found
	case "${device_}" in
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
