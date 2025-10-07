#!/bin/bash
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2025  IPFire Team  <info@ipfire.org>                     #
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

shopt -s nullglob

NOW="$(date "+%Y-%m-%d-%H%M")"

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
			# Skip any empty line (which will include /)
			[ -n "${file}" ] || continue

			for file in /${file}; do
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
	tar cvfz "${filename}" -C / \
		--exclude-from="/var/ipfire/backup/exclude" \
		--exclude-from="/var/ipfire/backup/exclude.user" \
		$(process_includes "/var/ipfire/backup/include") \
		$(process_includes "/var/ipfire/backup/include.user") \
		"$@"

	return 0
}

restore_backup() {
	local filename="${1}"

	# stop collectd to remove the rrd ramdisk for restore and convert
	# the rrd's
	/etc/rc.d/init.d/collectd stop

	# remove all openvpn certs to prevent old unusable
	# certificates being left in directory after a restore
	rm -f /var/ipfire/ovpn/certs/*

	# Extract backup
	if ! tar xvzpf "${filename}" -C / \
			--exclude-from="/var/ipfire/backup/exclude" \
			--exclude-from="/var/ipfire/backup/exclude.user" \
			--force-local; then
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

	# IDS backend converter.
	if [ -e "/var/ipfire/suricata/oinkmaster.conf" ]; then
		# Run the converter
		convert-ids-backend-files
	fi

	# Convert DNS settings
	convert-dns-settings

	# move nobeeps if exist
	[ -e "/var/ipfire/ppp/nobeeps" ] && mv /var/ipfire/ppp/nobeeps /var/ipfire/red/nobeeps

	# Replace previously used OpenVPN Diffie-Hellman parameter by ffdhe4096
	sed -i 's|/var/ipfire/ovpn/ca/dh1024.pem|/etc/ssl/ffdhe4096.pem|' /var/ipfire/ovpn/server.conf /var/ipfire/ovpn/n2nconf/*/*.conf

	# Update OpenVPN CRL
	/etc/fcron.daily/openvpn-crl-updater

	# Update OpenVPN N2N Client Configs
	## Add providers legacy default line to n2n client config files
	# Check if ovpnconfig exists and is not empty
	if [ -s /var/ipfire/ovpn/ovpnconfig ]; then
	       # Identify all n2n connections
	       for y in $(awk -F',' '/net/ { print $3 }' /var/ipfire/ovpn/ovpnconfig); do
	           # Add the legacy option to all N2N client conf files if it does not already exist
			if [ $(grep -c "Open VPN Client Config" /var/ipfire/ovpn/n2nconf/${y}/${y}.conf) -eq 1 ] ; then
				if [ $(grep -c "providers legacy default" /var/ipfire/ovpn/n2nconf/${y}/${y}.conf) -eq 0 ] ; then
					echo "providers legacy default" >> /var/ipfire/ovpn/n2nconf/${y}/${y}.conf
				fi
			fi
	       done
	fi

	#Update ovpnconfig to include pass or no-pass for old backup versions missing the entry
	# Check if ovpnconfig exists and is not empty
	if [ -s /var/ipfire/ovpn/ovpnconfig ]; then
       	# Add blank line at top of ovpnconfig otherwise the first roadwarrior entry is treated like a blank line and missed out from update
       	awk 'NR==1{print ""}1' /var/ipfire/ovpn/ovpnconfig > /var/ipfire/ovpn/tmp_file && mv /var/ipfire/ovpn/tmp_file /var/ipfire/ovpn/ovpnconfig
       	# Make all N2N connections 'no-pass' since they do not use encryption
       	awk '{FS=OFS=","} {if($5=="net") {$43="no-pass"; print $0}}' /var/ipfire/ovpn/ovpnconfig >> /var/ipfire/ovpn/ovpnconfig.new
		# Evaluate roadwarrior connection names for *.p12 files
       	for y in $(awk -F',' '/host/ { print $3 }' /var/ipfire/ovpn/ovpnconfig); do
       	    # Sort all unencrypted roadwarriors out and set 'no-pass' in [43] index
       	        if [[ -n $(openssl pkcs12 -info -in /var/ipfire/ovpn/certs/${y}.p12 -noout -password pass:'' 2>&1 | grep 'Encrypted data') ]]; then
       	                awk -v var="$y" '{FS=OFS=","} {if($3==var) {$43="no-pass"; print $0}}' /var/ipfire/ovpn/ovpnconfig >> /var/ipfire/ovpn/ovpnconfig.new
       	        fi
       	    # Sort all encrypted roadwarriors out and set 'pass' in [43] index
       	        if [[ -n $(openssl pkcs12 -info -in /var/ipfire/ovpn/certs/${y}.p12 -noout -password pass:'' 2>&1 | grep 'verify error')  ]]; then
       	                awk -v var="$y" '{FS=OFS=","} {if($3==var) {$43="pass"; print $0}}' /var/ipfire/ovpn/ovpnconfig >> /var/ipfire/ovpn/ovpnconfig.new
			 fi
	       done
	fi
	# Replace existing ovpnconfig with updated index
	mv /var/ipfire/ovpn/ovpnconfig.new /var/ipfire/ovpn/ovpnconfig
	# Set correct ownership
	chown nobody:nobody /var/ipfire/ovpn/ovpnconfig

	# Generate new HTTPS RSA key if the existing is too small
	KEYSIZE=$(openssl rsa -in /etc/httpd/server.key -text -noout | sed -n 's/Private-Key:\ (\(.*\)\ bit.*/\1/p')
	if [ $KEYSIZE \< 2048 ]; then
		openssl genrsa -out /etc/httpd/server.key 4096 &>/dev/null
		chmod 600 /etc/httpd/server.key
		sed "s/HOSTNAME/`hostname -f`/" < /etc/certparams | \
				openssl req -new -key /etc/httpd/server.key \
				-out /etc/httpd/server.csr &>/dev/null
		openssl x509 -req -days 999999 -sha256 \
			-in /etc/httpd/server.csr \
			-signkey /etc/httpd/server.key \
			-out /etc/httpd/server.crt &>/dev/null
	fi

	# Remove any entry for ALIENVAULT, SPAMHAUS_EDROP, ABUSECH_BOTNETC2 or 3CORESEC from the ipblocklist modified file
	# and the associated ipblocklist files from the /var/lib/ipblocklist directory
	sed -i '/ALIENVAULT=/d' /var/ipfire/ipblocklist/modified
	sed -i '/SPAMHAUS_EDROP=/d' /var/ipfire/ipblocklist/modified
	sed -i '/ABUSECH_BOTNETC2=/d' /var/ipfire/ipblocklist/modified
	sed -i '/3CORESEC_SSH=/d' /var/ipfire/ipblocklist/modified
	sed -i '/3CORESEC_SCAN=/d' /var/ipfire/ipblocklist/modified
	sed -i '/3CORESEC_WEB=/d' /var/ipfire/ipblocklist/modified
	if [ -e /var/lib/ipblocklist/ALIENVAULT.conf ]; then
		rm /var/lib/ipblocklist/ALIENVAULT.conf
	fi
	if [ -e /var/lib/ipblocklist/SPAMHAUS_EDROP.conf ]; then
		rm /var/lib/ipblocklist/SPAMHAUS_EDROP.conf
	fi
	if [ -e /var/lib/ipblocklist/ABUSECH_BOTNETC2.conf ]; then
		rm /var/lib/ipblocklist/ABUSECH_BOTNETC2.conf
	fi
	if [ -e /var/lib/ipblocklist/3CORESEC_SSH.conf ]; then
		rm /var/lib/ipblocklist/3CORESEC_SSH.conf
	fi
	if [ -e /var/lib/ipblocklist/3CORESEC_SCAN.conf ]; then
		rm /var/lib/ipblocklist/3CORESEC_SCAN.conf
	fi
	if [ -e /var/lib/ipblocklist/3CORESEC_WEB.conf ]; then
		rm /var/lib/ipblocklist/3CORESEC_WEB.conf
	fi

	# The collectd directory structure was changed but not all changes
	# are done by the official migration script generator
	for i in $(seq 0 63);
	do
		if [ -e /var/log/rrd/collectd/localhost/cpufreq/cpufreq-$i.rrd ]; then
			mkdir -p /var/log/rrd/collectd/localhost/cpufreq-$i
			mv -f /var/log/rrd/collectd/localhost/cpufreq/cpufreq-$i.rrd \
				/var/log/rrd/collectd/localhost/cpufreq-$i/cpufreq.rrd
		fi
		if [ -e /var/log/rrd/collectd/localhost/thermal-thermal_zone$i/temperature-temperature.rrd ]; then
			mv -f /var/log/rrd/collectd/localhost/thermal-thermal_zone$i/temperature-temperature.rrd \
			/var/log/rrd/collectd/localhost/thermal-thermal_zone$i/temperature.rrd
	fi
	done

	# Create collectd 4.x to 5.x migration script from rrd contents, run the script that
	# was created and then remove the old interface directory if it is present as it will
	# be empty after the migration has been carried out.
	/var/ipfire/collectd-migrate-4-to-5.pl --indir /var/log/rrd/ > /tmp/rrd-migrate.sh
	sh /tmp/rrd-migrate.sh >/dev/null 2>&1

	# Run old collectd cleanup only if the interface dir exist to prevent cleanup of
	# new devices if the user have reenabled it and restore a backup
	if [ -d /var/log/rrd/collectd/localhost/interface ]; then
		rm -rf \
			/var/log/rrd/collectd/localhost/cpufreq \
			/var/log/rrd/collectd/localhost/disk-loop* \
			/var/log/rrd/collectd/localhost/disk-sg* \
			/var/log/rrd/collectd/localhost/disk-sr* \
			/var/log/rrd/collectd/localhost/disk-ram* \
			/var/log/rrd/collectd/localhost/interface \
			/var/log/rrd/collectd/localhost/iptables-filter-HOSTILE \
			/var/log/rrd/collectd/localhost/iptables-filter-HOSTILE_DROP \
			/var/log/rrd/collectd/localhost/processes* \
			/var/log/rrd/collectd/localhost/thermal-cooling_device*
	fi

	# start collectd after restore
	/etc/rc.d/init.d/collectd start

	# Check if ipsec hosctcert.pem serial number is 1 and if the serial file does not contain 02
	# In this case set the serial file to 02 and empty the index.txt file
	ARR=()
	while IFS= read -r line; do
		ARR+=("$line")
	done <<< "$(openssl x509 -in /var/ipfire/certs/hostcert.pem -noout -text)"
       if [ $(echo ${ARR[3]} | sed -E 's,^[^0-9]*([0-9]+).*$,\1,') = 1 ] && \
			[ $(expr $(cat "/var/ipfire/certs/serial") + 0) != 2 ]; then
		sed -i "s/.*/02/" /var/ipfire/certs/serial
		sed -i 'd' /var/ipfire/certs/index.txt
	fi

	# Update MLKEM to only be used in combination with x25519
	if ! grep -q "x25519-ke1_mlkem" /var/ipfire/vpn/config; then
		sed -i -e "s@mlkem@x25519-ke1_mlkem@g" /var/ipfire/vpn/config

		# Regenerate /etc/ipsec.conf
		sudo -u nobody /srv/web/ipfire/cgi-bin/vpnmain.cgi
	fi

        # Restart ipsec if enabled
        # This will ensure that the restored certs and secrets etc are loaded and used
        if [ $(grep -c "ENABLED=on" /var/ipfire/vpn/settings) -eq 1  ] ; then
                /usr/local/bin/ipsecctrl S
        fi

	if [ -e /var/log/pakfire.log ]; then
		rm /var/log/pakfire.log
	fi

	# Update the OpenVPN configuration, update the RW log entry in collectd.vpn
	# if it is the old name and restart the openvpn daemons
	sudo -u nobody /srv/web/ipfire/cgi-bin/ovpnmain.cgi
	if grep -q "/var/run/ovpnserver.log" /var/ipfire/ovpn/collectd.vpn; then
		sed -i 's|"/var/run/ovpnserver.log"|"/var/run/openvpn-rw.log"|' /var/ipfire/ovpn/collectd.vpn
	fi
	/etc/init.d/openvpn-n2n restart
	/etc/init.d/openvpn-rw restart

	#
	# Core Update 198
	#

	# Add the suricata user to the mail group
	usermod -a -G mail suricata

	# Change ownership & permissions of auth.conf
	chmod 640 /var/ipfire/dma/auth.conf
	chown nobody:mail /var/ipfire/dma/auth.conf

	return 0
}

find_logfiles() {
	local filelist=( /var/log/logwatch/* /var/log/messages* /var/log/*.log /var/log/**/*.log )

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

	if [ -e "/tmp/${name}.ipf" ]; then
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
