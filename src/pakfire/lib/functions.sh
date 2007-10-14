#!/bin/bash
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007  Michael Tremer & Christian Schmidt                      #
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
	tar xvf /opt/pakfire/tmp/files --preserve --numeric-owner -C /
	echo "...Finished."
}

remove_files() {
	echo "Removing files..."
	for i in $(cat /opt/pakfire/tmp/ROOTFILES); do
		rm -rfv ${i}
	done
	echo "...Finished."
}

restart_service() {
	
	/etc/init.d/$1 restart

}

start_service() {
	DELAY=0
	while true
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
		
		[ -e "/etc/init.d/${1}" ] && \
		 (sleep ${DELAY} && /etc/init.d/${1} start ${BACKGROUND})
}

stop_service() {
	
	[ -e "/etc/init.d/${1}" ] && /etc/init.d/${1} stop

}
