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
# Copyright (C) 2022 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

core=165

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

if [ $ROOTSPACE -lt 100000 ]; then
	exit_with_error "ERROR cannot update because not enough free space on root." 2
	exit 2
fi

# Remove files
rm -rvf \
	/lib/xtables/libxt_ACCOUNT.so \
	/lib/xtables/libxt_CHAOS.so \
	/lib/xtables/libxt_condition.so \
	/lib/xtables/libxt_DELUDE.so \
	/lib/xtables/libxt_dhcpmac.so \
	/lib/xtables/libxt_DHCPMAC.so \
	/lib/xtables/libxt_DNETMAP.so \
	/lib/xtables/libxt_ECHO.so \
	/lib/xtables/libxt_fuzzy.so \
	/lib/xtables/libxt_geoip.so \
	/lib/xtables/libxt_gradm.so \
	/lib/xtables/libxt_iface.so \
	/lib/xtables/libxt_IPMARK.so \
	/lib/xtables/libxt_ipp2p.so \
	/lib/xtables/libxt_ipv4options.so \
	/lib/xtables/libxt_length2.so \
	/lib/xtables/libxt_LOGMARK.so \
	/lib/xtables/libxt_lscan.so \
	/lib/xtables/libxt_pknock.so \
	/lib/xtables/libxt_PROTO.so \
	/lib/xtables/libxt_psd.so \
	/lib/xtables/libxt_quota2.so \
	/lib/xtables/libxt_SYSRQ.so \
	/lib/xtables/libxt_TARPIT.so \
	/srv/web/ipfire/cgi-bin/p2p-block.cgi \
	/usr/bin/2to3-3.8 \
	/usr/bin/easy_install-3.8 \
	/usr/bin/idle3.8 \
	/usr/bin/pip3.8 \
	/usr/bin/pydoc3.8 \
	/usr/bin/python3.8 \
	/usr/bin/python3.8-config \
	/usr/bin/xt_geoip_query \
	/usr/lib/libpython3.8.so \
	/usr/lib/libpython3.8.so.1.0 \
	/usr/lib/libxt_ACCOUNT_cl.so* \
	/usr/lib/python3.8/ \
	/usr/sbin/iptaccount \
	/usr/sbin/pknlusr \
	/usr/share/xt_geoip/ \
	/var/ipfire/firewall/p2protocols

# Stop services

# Extract files
extract_files

# update linker config
ldconfig

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# Export location DB in new format.
/usr/bin/location export \
	--directory=/var/lib/location/ipset \
	--family=ipv4 \
	--format=ipset

# Start services
telinit u
/etc/rc.d/init.d/firewall restart

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
