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

function download() {
	wget -U "IPFire-NetInstall/2.x" "$@"
}

if [ $# -lt 2 ]; then
	echo "$0: Insufficient number of arguments" >&2
	exit 2
fi

OUTPUT="${1}"
URL="${2}"

echo "Downloading ${URL}..."
if ! download -O "${OUTPUT}" "${URL}"; then
	echo "Download failed" >&2

	rm -f "${OUTPUT}"
	exit 1
fi

# Download went well. Checking for MD5 sum
if download -O "${OUTPUT}.md5" "${URL}.md5" &>/dev/null; then
	# Read downloaded checksum
	read -r md5sum rest < "${OUTPUT}.md5"
	rm -f "${OUTPUT}.md5"

	# Compute checkum of downloaded image file
	read -r md5sum_image rest <<< "$(md5sum "${OUTPUT}")"

	if [ "${md5sum}" != "${md5sum_image}" ]; then
		echo "MD5 sum mismatch: ${md5sum} != ${md5sum_image}" >&2
		exit 2
	fi
fi

exit 0
