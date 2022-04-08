#!/bin/sh
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2022  IPFire Team  <info@ipfire.org>                     #
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

function download() {
	wget -U "IPFire-NetInstall/2.x" "$@"
}

if [ $# -lt 2 ]; then
	echo "$0: Insufficient number of arguments" >&2
	exit 2
fi

OUTPUT="${1}"
URL="${2}"

# Mount a tmpfs which is big enough to hold the ISO image
OUTPUT_DIR="${OUTPUT%/*}"

mkdir -p "${OUTPUT_DIR}"
if ! mount -t tmpfs none "${OUTPUT_DIR}" -o size=512M; then
	echo "Could not mount tmpfs to ${OUTPUT_DIR}" >&2
	exit 1
fi

echo "Downloading ${URL}..."
if ! download -O "${OUTPUT}" "${URL}"; then
	echo "Download failed" >&2

	rm -f "${OUTPUT}"
	exit 1
fi

# Download went well. Checking for BLAKE2 sum
if download -O "${OUTPUT}.b2" "${URL}.b2" &>/dev/null; then
	# Read downloaded checksum
	read -r b2sum rest < "${OUTPUT}.b2"
	rm -f "${OUTPUT}.b2"

	# Compute checkum of downloaded image file
	read -r b2sum_image rest <<< "$(b2sum "${OUTPUT}")"

	if [ "${b2sum}" != "${b2sum_image}" ]; then
		echo "BLAKE2 checksum mismatch: ${b2sum} != ${b2sum_image}" >&2
		exit 2
	fi
fi

exit 0
