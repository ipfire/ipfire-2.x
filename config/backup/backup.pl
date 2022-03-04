#!/bin/bash
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2014  IPFire Team  <info@ipfire.org>                     #
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

NOW="$(date "+%Y-%m-%d-%H:%M")"

list_addons() {
	local file
	for file in /var/ipfire/backup/addons/includes/*; do
		if [ -f "${file}" ]; then
			basename "${file}"
		fi
	done

	return 0
}

process_includes() {
	local include

	for include in $@; do
		local file
		while read -r file; do
			for file in ${file}; do
				if [ -e "${file}" ]; then
					echo "${file}"
				fi
			done
		done < "${include}"
	done | sort -u
}

make_backup() {
	local filename="${1}"
	shift

	# Backup all addons first
	local addon
	for addon in $(list_addons); do
		make_addon_backup "${addon}"
	done

	# Backup using global exclude/include definitions
	tar cvfz "${filename}" \
		--exclude-from="/var/ipfire/backup/exclude" \
		--exclude-from="/var/ipfire/backup/exclude.user" \
		$(process_includes "/var/ipfire/backup/include") \
		$(process_includes "/var/ipfire/backup/include.user") \
		"$@"

	return 0
}

restore_backup() {
	local filename="${1}"

	# Extract backup
	if ! tar xvzpf "${filename}" -C /; then
		echo "Could not extract backup" >&2
		return 1
	fi

	# Restart syslogd, httpd and suricata in case we've just loaded old logs
	apachectl -k graceful
	/bin/kill -HUP `cat /var/run/suricata.pid 2> /dev/null` 2> /dev/null
	/bin/kill -HUP `cat /var/run/syslogd.pid 2> /dev/null` 2> /dev/null

	# remove wrong vnstat tag file
	rm -f /var/log/vnstat/tag

	# create dhcpcd user
	groupadd -g 52 dhcpcd
	useradd -c 'dhcpcd privsep user'	\
		-d /run/dhcpcd/chroot		\
		-g dhcpcd			\
		-s /bin/false			\
		-u 52 dhcpcd

	# Run converters

	# Outgoing Firewall
	if [ -d "/var/ipfire/outgoing" ]; then
		# Reset files
		local file
		for file in /var/ipfire/firewall/{config,outgoing} \
				/var/ipfire/fwhosts/custom{hosts,groups,networks}; do
			: > "${file}"
			chown nobody:nobody "${file}"
		done

		# Run converter
		convert-outgoingfw

		# Remove old configuration
		rm -rf "/var/ipfire/outgoing"
	fi

	# External Access
	if [ -d "/var/ipfire/xtaccess" ]; then
		: > /var/ipfire/firewall/config
		chown nobody:nobody "/var/ipfire/firewall/config"

		# Run converter
		convert-xtaccess

		# Remove old configuration
		rm -rf "/var/ipfire/xtaccess"
	fi

	# DMZ Holes
	if [ -d "/var/ipfire/dmzholes" ] || [ -d "/var/ipfire/portfw" ]; then
		: > /var/ipfire/firewall/config
		chown nobody:nobody "/var/ipfire/firewall/config"

		# Run converter
		convert-dmz

		# Remove old configuration
		rm -rf "/var/ipfire/dmzholes"
	fi

	# Port Forwardings
	if [ -d "/var/ipfire/portfw" ]; then
		# Run converter
		convert-portfw

		# Remove old configuration
		rm -rf "/var/ipfire/portfw"
	fi

	# Convert location
	convert-to-location

	# Reload firewall
	firewallctrl

	# Convert old OpenVPN CCD files (CN change, Core Update 75)
	convert-ovpn

	# Snort to suricata converter.
	if [ -d "/var/ipfire/snort" ]; then
		# Run converter
		convert-snort

		# Remove old configuration directory.
		rm -rf "/var/ipfire/snort"
	fi

	# IDS multiple providers converter.
	if [ -e "/var/ipfire/suricata/rules-settings" ]; then
		# Run the converter
		convert-ids-multiple-providers
	fi

	# Convert DNS settings
	convert-dns-settings

	# move nobeeps if exist
	[ -e "/var/ipfire/ppp/nobeeps" ] && mv /var/ipfire/ppp/nobeeps /var/ipfire/red/nobeeps

	return 0
}

find_logfiles() {
	local filelist=( /var/log/messages* /var/log/*.log /var/log/**/*.log )

	echo "${filelist[@]}"
}

make_addon_backup() {
	local name="${1}"
	shift

	if [ ! -f "/var/ipfire/backup/addons/includes/${name}" ]; then
		echo "${name} does not have any backup includes" >&2
		return 1
	fi

	local filename="/var/ipfire/backup/addons/backup/${name}.ipf"

	tar cvzf "${filename}" \
		$(process_includes "/var/ipfire/backup/addons/includes/${name}")
}

restore_addon_backup() {
	local name="${1}"

	if [ -d "/tmp/${name}.ipf" ]; then
		mv "/tmp/${name}.ipf" "/var/ipfire/backup/addons/backup/${name}.ipf"
	fi

	# Extract backup
	if ! tar xvzpf "/var/ipfire/backup/addons/backup/${name}.ipf" -C /; then
		echo "Could not extract backup" >&2
		return 1
	fi
}

main() {
	local command="${1}"
	shift

	case "${command}" in
		include)
			local filename="${1}"

			if [ -z "${filename}" ]; then
				filename="/var/ipfire/backup/${NOW}.ipf"
			fi

			make_backup "${filename}" $(find_logfiles)
			;;

		exclude)
			local filename="${1}"

			if [ -z "${filename}" ]; then
				filename="/var/ipfire/backup/${NOW}.ipf"
			fi

			make_backup "${filename}"
			;;

		restore)
			local filename="${1}"

			if [ -z "${filename}" ]; then
				filename="/tmp/restore.ipf"
			fi

			restore_backup "${filename}"
			;;

		addonbackup)
			make_addon_backup "$@"
			;;

		restoreaddon)
			restore_addon_backup "${1/.ipf/}"
			;;

		iso)
			# Desired backup filename
			local filename="/var/ipfire/backup/${NOW}.ipf"

			if make_backup "${filename}"; then
				/usr/local/bin/backupiso "${NOW}"
			fi
			;;

		makedirs)
			mkdir -p /var/ipfire/backup/addons/{backup,includes}
			;;

		list)
			process_includes "/var/ipfire/backup/include" "/var/ipfire/backup/include.user"
			;;

		/var/ipfire/backup/*.ipf|/var/ipfire/backup/addons/backup/*.ipf|/var/tmp/backupiso/*.iso)
			unlink "${command}"
			;;

		*)
			echo "${0}: [include|exclude|restore|addonbackup <addon>|restoreaddon <addon>|iso]" >&2
			return 2
			;;
	esac

	return $?
}

main "$@" || exit $?
