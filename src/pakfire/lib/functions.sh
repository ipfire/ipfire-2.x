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

extract_files() {
	echo "Extracting files..."
	tar xvf --preserve --numeric-owner /opt/pakfire/tmp/files -C /
	echo "...Finished."
}

reload_libs() {
	echo "(Re-)Initializing the lib-cache..."	
	ldconfig -vv
	echo "...Finished."
}

reload_modules() {
	echo "(Re-)Initializing the module-dependencies..."	
	depmod -va
	echo "...Finished."
}

restart_service() {
	
	/etc/init.d/$1 restart

}
