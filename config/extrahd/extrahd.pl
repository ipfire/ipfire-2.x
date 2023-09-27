#!/bin/bash
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2023 IPFire Team  <info@ipfire.org>                           #
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

log() {
	local message="${@}"

	logger -t "extrahd" "${message}"
}

extrahd_mount() {
	local _mountpoint="${1}"

	local device
	local filesystem
	local mountpoint
	local rest
	local failed=0

	while IFS=';' read -r device filesystem mountpoint rest; do
		# Filter by UUID or mountpoint
		case "${_mountpoint}" in
			UUID=*)
				if [ "${device}" != "${_mountpoint}" ]; then
					continue
				fi
				;;

			/*)
				if [ -n "${_mountpoint}" ] && [ "${mountpoint}" != "${_mountpoint}" ]; then
					continue
				fi
				;;
		esac

		# Check that the mountpoint starts with a slash
		if [ "${mountpoint:0:1}" != "/" ]; then
			log "Skipping invalid mountpoint: ${mountpoint}"
			continue
		fi

		# Skip mounting if something is already mounted at the mountpoint
		if mountpoint "${mountpoint}" &>/dev/null; then
			continue
		fi

		# Ensure the mountpoint exists
		mkdir --parents --mode=777 "${mountpoint}" &>/dev/null

		if mount --types "${filesystem}" "${device}" "${mountpoint}"; then
			log "Successfully mounted ${device} to ${mountpoint}"
		else
			log "Could not mount ${device} to ${mountpoint}: $?"
			failed=1
		fi
	done < /var/ipfire/extrahd/devices

	return ${failed}
}

extrahd_umount() {
	local _mountpoint="${1}"

	local device
	local filesystem
	local mountpoint
	local rest
	local failed=0

	while IFS=';' read -r device filesystem mountpoint rest; do
		# Filter by UUID or mountpoint
		case "${_mountpoint}" in
			UUID=*)
				if [ "${device}" != "${_mountpoint}" ]; then
					continue
				fi
				;;

			/*)
				if [ -n "${_mountpoint}" ] && [ "${mountpoint}" != "${_mountpoint}" ]; then
					continue
				fi
				;;
		esac

		# Do not try to umount if nothing is mounted
		if ! mountpoint "${mountpoint}" &>/dev/null; then
			continue
		fi

		# Umount and try lazy umount if failed
		if umount --quiet --recursive "${mountpoint}" || \
				umount --quiet --recursive --lazy "${mountpoint}"; then
			log "Successfully umounted ${device} from ${mountpoint}"
		else
			log "Could not umount ${device} from ${mountpoint}: $?"
			failed=1
		fi
	done < /var/ipfire/extrahd/devices
}

handle_udev_event() {
	case "${ACTION}" in
		add)
			if [ -n "${ID_FS_UUID}" ]; then
				extrahd_mount "UUID=${ID_FS_UUID}" || return $?
			fi
			;;
	esac

	return 0
}

main() {
	( echo "$@"; set ) > /tmp/extrahd.$$

	local command="${1}"
	shift

	local rc=0

	case "${command}" in
		mount)
			extrahd_mount "${@}" || rc="${?}"
			;;
		umount)
			extrahd_umount "${@}" || rc="${rc}"
			;;
		udev-event)
			handle_udev_event "${@}" || rc="${rc}"
			;;
		scanhd)
			exec /usr/local/bin/scanhd "${@}"
			;;

		# No command
		"")
			echo "${0}: No command given" >&2
			rc=2
			;;

		# Unknown command
		*)
			echo "${0}: Unsupported command: ${command}" >&2
			rc=2
			;;
	esac

	return ${rc}
}

# Call main()
main "${@}" || exit ${?}
