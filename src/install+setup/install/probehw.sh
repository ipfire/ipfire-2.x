#!/bin/sh
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

echo "Detecting Hardware..."
for MODULE in $(kudzu -qps  -t 30 | grep driver: | cut -d ' ' -f 2 | sort | uniq); do
		if [ "${MODULE}" = "unknown" ] || \
				[ "${MODULE}" = "ignore" ] || \
				[ "${MODULE}" = "" ]; then
        continue
		fi
		MODULE=$(basename $(find /lib/modules -name $(echo $MODULE | sed -e 's/[_-]/*/g')* ) | cut -d. -f1 | head -1 2>/dev/null)
    [ "${MODULE}" == "" ] && continue
    
		if grep -Eqe "^${MODULE} " /proc/modules; then
			continue
		fi
		echo -n "Loading ${MODULE}"
		modprobe ${MODULE} >/dev/null 2>&1
		echo " --> ecode: $?"
done

sleep 10

if [ $# -eq 0 ]; then
	exit 0
fi

## If the autodetection fails we will try to load every module...
## Do this only when we want...

for i in a b c d e f g; do
	if [ ! -e /dev/sd$i ]; then
		DEVICE="/dev/sd$i"
		echo "Checking for: $DEVICE"
		break
	fi
done

for MODULE in $(ls /lib/modules/*/kernel/drivers/scsi); do
	MODULE=`basename $MODULE | awk -F. '{ print $1 }'`
	
	echo -n "Probing for $MODULE"
	modprobe $MODULE >/dev/null 2>&1
	RETVAL=$?
	echo " --> ecode: $RETVAL"
	if [ "$RETVAL" -eq "0" ]; then
		sleep 3
		if [ -e "$DEVICE" ]; then
			break
		fi
	fi

done

sleep 5

exit 0
