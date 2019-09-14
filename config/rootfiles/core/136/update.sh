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
# Copyright (C) 2019 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

core=136

exit_with_error() {
	# Set last succesfull installed core.
	echo $(($core-1)) > /opt/pakfire/db/core/mine
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

# Stop services

# Extract files
extract_files

# Remove old perl files
rm -rf /usr/bin/perl5.12.3
rm -rf /usr/lib/perl5/5.12.3
rm -rf /usr/lib/perl5/site_perl/5.12.3

# update linker config
ldconfig

# Update crontab
sed -i -e "s|^01 0 \* \* \*./usr/local/bin/logwatch|05 0 \* \* \*\t/usr/local/bin/logwatch|g" /var/spool/cron/root.orig
fcrontab -z &>/dev/null

# Update Language cache
/usr/local/bin/update-lang-cache

# move unbound down after network down
mv /etc/rc.d/rc0.d/K79unbound /etc/rc.d/rc0.d/K86unbound
mv /etc/rc.d/rc6.d/K79unbound /etc/rc.d/rc6.d/K86unbound

# Apply local configuration to sshd_config
/usr/local/bin/sshctrl

# Start services
/etc/init.d/sshd restart
/etc/init.d/apache restart

# Update GeoIP
/usr/local/bin/xt_geoip_update

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
