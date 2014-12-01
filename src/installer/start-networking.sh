#!/bin/bash
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

function list_interfaces() {
	local interface

	for interface in /sys/class/net/*; do
		[ -d "${interface}" ] || continue

		interface="$(basename ${interface})"
		case "${interface}" in
			eth*)
				echo "${interface}"
				;;
		esac
	done
}

function try_dhcp() {
	local interface="${1}"

	# Bring up the interface
	ip link set "${interface}" up

	# Try to make the lights of the adapter light up
	ethtool -i "${interface}" &>/dev/null

	# Start the DHCP client
	dhcpcd "${interface}"
}

function main() {
	local interface
	for interface in $(list_interfaces); do
		if ! try_dhcp "${interface}"; then
			echo "Could not acquire an IP address on ${interface}"
			continue
		fi

		echo "Successfully started on ${interface}"

		# Wait until everything is settled
		sleep 15

		return 0
	done

	return 1
}

main
