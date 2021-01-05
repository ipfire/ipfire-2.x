#!/bin/bash
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

. /etc/sysconfig/rc
. $rc_functions

extract_files() {
	echo "Extracting files..."
	tar --acls --xattrs --xattrs-include='*' \
		-xavf /opt/pakfire/tmp/files* --no-overwrite-dir -p --numeric-owner -C /
	echo "...Finished."
}

extract_backup_includes() {
	echo "Extracting backup includes..."
	tar xavf /opt/pakfire/tmp/files* --no-overwrite-dir -p --numeric-owner -C / \
		var/ipfire/backup/addons/includes
	echo "...Finished."
}

remove_files() {
	echo "Removing files..."
	for i in $(cat /opt/pakfire/db/rootfiles/${NAME}); do
	    rm -rfv /${i}
	done
	echo "...Finished."
}

make_backup() {
	if [ -e "/var/ipfire/backup/addons/includes/${1}" ]; then
		echo "Creating Backup..."
		/usr/local/bin/backupctrl addonbackup ${1}
		echo "...Finished."
	fi
}

restore_backup() {
	if [ -e "/var/ipfire/backup/addons/backup/${1}.ipf" ]; then
		echo "Restoring Backup..."
		/usr/local/bin/backupctrl restoreaddon ${1}.ipf
		echo "...Finished."
	fi
}

restart_service() {
	/etc/init.d/${1} restart
}

start_service() {
	DELAY=0
	while true
	 do
		case "${1}" in
			--delay|-d)
				DELAY=${2}
				shift 2
				;;
			--background|-b)
				BACKGROUND="&"
				shift
				;;
			-*)
				log_failure_msg "Unknown Option: ${1}"
				return 2 #invalid or excess argument(s)
				;;
			*)
				break
				;;
		esac
	done

	if [ -f "/etc/init.d/${1}" ]; then
	    if [ -n "${BACKGROUND}" ]; then
				(sleep ${DELAY} && /etc/init.d/${1} start) &
			else
				sleep ${DELAY} && /etc/init.d/${1} start
			fi
	fi
}

stop_service() {
	if [ -f "/etc/init.d/${1}" ]; then
		/etc/init.d/${1} stop
	fi
}

rebuild_langcache() {
	echo "Rebuilding language cache..."
	perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
	echo "...Finished."
}

