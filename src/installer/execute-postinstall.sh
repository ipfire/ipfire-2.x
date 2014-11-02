#!/bin/sh
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2014  IPFire Team  <info@ipfire.org>                          #
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

DESTINATION="${1}"
DOWNLOAD_URL="${2}"

DOWNLOAD_TARGET="/tmp/post-install.exe"

if download -O "${DESTINATION}${DOWNLOAD_TARGET}" "${DOWNLOAD_URL}"; then
	echo "Downloading post-install script from ${DOWNLOAD_URL}..."

	# Make it executable
	chmod a+x "${DESTINATION}${DOWNLOAD_TARGET}"

	# Replace /etc/resolv.conf so that we will have
	cp -fb /etc/resolv.conf ${DESTINATION}/etc/resolv.conf
	for i in /dev /proc /sys; do
		mount --bind "${i}" "${DESTINATION}${i}"
	done

	# Execute the downloaded script
	chroot "${DESTINATION}" sh --login -c "${DOWNLOAD_TARGET}"
	retval=$?

	# Cleanup the environment
	mv -f ${DESTINATION}/etc/resolv.conf{~,}
	for i in /dev /proc /sys; do
		umount "${DESTINATION}${i}"
	done
	rm -f "${DESTINATION}${DOWNLOAD_TARGET}"

	exit ${retval}

# In case the download failed
else
	echo "Could not download the post-install script" >&2
	exit 1
fi
