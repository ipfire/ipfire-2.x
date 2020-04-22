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

core=143

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


# Remove files
rm -rf /usr/lib/go/9.2.0

# Stop services
/etc/init.d/suricata stop

# move swap after mount
mv -f /etc/rc.d/rcsysinit.d/S20swap \
      /etc/rc.d/rcsysinit.d/S41swap
      
# Extract files
extract_files

# update linker config
ldconfig

# remove wrong vnstat tag file
/etc/init.d/vnstat stop
rm -f /var/log/vnstat/tag
/etc/init.d/vnstat start

# set /var/spool/cron to cron user
chown cron:cron /var/spool/cron

# restart init after glibc replace
telinit u

# Apply changed sysctl settings
/etc/init.d/sysctl start

# Apply local configuration to sshd_config
/usr/local/bin/sshctrl

# Generate new http ports file for suricata
perl -e "require '/var/ipfire/ids-functions.pl'; \
     &IDS::generate_http_ports_file(); \
     &IDS::set_ownership(\"\$IDS::http_ports_file\"); "

# Start services
/usr/local/bin/ipsecctrl S
/etc/init.d/unbound restart
/etc/init.d/sshd restart
/etc/init.d/suricata start

# remove dropped packages
for package in bluetooth; do
	if [ -e /opt/pakfire/db/installed/meta-$package ]; then
		stop_service $package
		for i in $(cat /opt/pakfire/db/rootfiles/$package); do
			rm -rfv /${i}
		done
	fi
	rm -f /opt/pakfire/db/installed/meta-$package
	rm -f /opt/pakfire/db/meta/meta-$package
	rm -f /opt/pakfire/db/rootfiles/$package
done

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# This update needs a reboot...
touch /var/run/need_reboot

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
