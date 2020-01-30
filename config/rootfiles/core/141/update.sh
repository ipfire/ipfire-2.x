#!/bin/bash
############################################################################
#                                                                          #
# This file is part of the IPFire Firewall.                                #
#                                                                          #
# IPFire is free software; you can redistribute it and/or modify           #
# it under the terms of the GNU General Public License as published by     #
# the Free Software Foundation; either version 3 of the License, or        #
# (at your option) any later version.                                      #
#                                                                          #
# IPFire is distributed in the hope that it will be useful,                #
# but WITHOUT ANY WARRANTY; without even the implied warranty of           #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
# GNU General Public License for more details.                             #
#                                                                          #
# You should have received a copy of the GNU General Public License        #
# along with IPFire; if not, write to the Free Software                    #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA #
#                                                                          #
# Copyright (C) 2020 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

core=141

exit_with_error() {
	# Set last succesfull installed core.
	echo $(($core-1)) > /opt/pakfire/db/core/mine
	# force fsck at next boot, this may fix free space on xfs
	touch /forcefsck
	# don't start pakfire again at error
	killall -KILL pak_update
	/usr/bin/logger -p syslog.emerg -t ipfire \
		"core-update-${core}: $1"
	exit $2
}

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Check diskspace on root
ROOTSPACE=`df / -Pk | sed "s| * | |g" | cut -d" " -f4 | tail -n 1`

if [ $ROOTSPACE -lt 180000 ]; then
	exit_with_error "ERROR cannot update because not enough free space on root." 2
fi

# Remove files
rm -f /etc/rc.d/init.d/networking/red.up/06-safe-search
rm -rf /usr/lib/go/8.3.0

# Stop services

# Extract files
extract_files

# update linker config
ldconfig

# restart init after glibc replace
telinit u

# Update Language cache
/usr/local/bin/update-lang-cache

# Update Language cache
/usr/local/bin/filesystem-cleanup

# Convert DNS settings
/usr/local/bin/convert-dns-settings

# move nobeeps if exist
[ -e "/var/ipfire/ppp/nobeeps" ] && mv /var/ipfire/ppp/nobeeps /var/ipfire/red/nobeeps

# Start services
/etc/init.d/unbound restart

# This update needs a reboot...
touch /var/run/need_reboot

# Force pakfire to redownload lists
rm -f /opt/pakfire/db/lists/*.db

# Let pakfire forget the elinks and python3 package
rm -fv /opt/pakfire/db/rootfiles/elinks
rm -fv /opt/pakfire/db/*/meta-elinks
rm -fv /opt/pakfire/db/rootfiles/python3
rm -fv /opt/pakfire/db/*/meta-python3

# run pakfire update twice (first sometimes fail)
/usr/local/bin/pakfire update
/usr/local/bin/pakfire update

# Finish
/etc/init.d/fireinfo start
sendprofile

# Update grub config to display new core version
if [ -e /boot/grub/grub.cfg ]; then
	grub-mkconfig -o /boot/grub/grub.cfg
fi

sync

# Don't report the exitcode last command
exit 0
