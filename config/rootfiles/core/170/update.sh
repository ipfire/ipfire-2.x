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

core=170

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Stop services
/etc/init.d/rc.d/unbound stop

# Remove files
rm -rvf \
	/lib/ld-2.* \
	/lib/libanl-2.* \
	/lib/libc-2.* \
	/lib/libdl-2.* \
	/lib/libm-2.* \
	/lib/libmvec-2.* \
	/lib/libnsl-2.* \
	/lib/libnss_compat-2.* \
	/lib/libnss_db-2.* \
	/lib/libnss_dns-2.* \
	/lib/libnss_files-2.* \
	/lib/libnss_hesiod-2.* \
	/lib/libntfs-3g.so.88* \
	/lib/libpsx.so.2 \
	/lib/libpthread-2.* \
	/lib/libresolv-2.* \
	/lib/librt-2.* \
	/lib/libthread_db-1.0.so \
	/lib/libutil-2.* \
	/sbin/ifcfg \
	/sbin/routef \
	/sbin/rtpr \
	/usr/bin/screen-4.* \
	/usr/bin/x86_64 \
	/usr/lib/libbfd-2.36.* \
	/usr/lib/libbind9-9.16.2* \
	/usr/lib/libdnet* \
	/usr/lib/libirs-9.16.2* \
	/usr/lib/libisc-9.16.2* \
	/usr/lib/libisccc-9.16.2* \
	/usr/lib/libisccfg-9.16.2* \
	/usr/lib/libldap-* \
	/usr/lib/libldap_r-* \
	/usr/lib/libns-9.16.2* \
	/usr/lib/libopenjp2.so.2.3.* \
	/usr/lib/libpoppler.so.11* \
	/usr/lib/perl5/site_perl/5.32.1/Bundle/LWP.pm \
	/usr/lib/perl5/site_perl/5.32.1/File/Listing.pm \
	/usr/lib/perl5/site_perl/5.32.1/HTML/Form.pm \
	/usr/lib/perl5/site_perl/5.32.1/HTTP/Cookies \
	/usr/lib/perl5/site_perl/5.32.1/HTTP/Negotiate.pm \
	/usr/lib/perl5/site_perl/5.32.1/*-linux-thread-multi/auto/Unix/Syslog/autosplit.ix \
	/usr/lib/perl5/site_perl/5.32.1/*-linux-thread-multi/qd.pl \
	/usr/lib/perl5/site_perl/5.32.1/LWP/media.types \
	/usr/lib/perl5/site_perl/5.32.1/LWP/MediaTypes.pm \
	/usr/lib/perl5/site_perl/5.32.1/LWP/Protocol/GHTTP.pm \
	/usr/lib/perl5/site_perl/5.32.1/LWP/Protocol/http10.pm \
	/usr/lib/perl5/site_perl/5.32.1/LWP/Protocol/https10.pm \
	/usr/lib/perl5/site_perl/5.32.1/WWW \
	/usr/sbin/ovpn-ccd-convert \
	/usr/share/xt_geoip

# Extract files
extract_files

# update linker config
ldconfig

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# Create directory for IPBlocklist feature
mkdir -pv /var/lib/ipblocklist
chown nobody:nobody /var/lib/ipblocklist

# Rebuild fcrontab from scratch
/usr/bin/fcrontab -z

# Update collectd.conf
sed -i /etc/collectd.conf \
	-e "/LoadPlugin entropy/d"
/etc/init.d/collectd restart

# Start services
/etc/init.d/rc.d/unbound start
/etc/init.d/rc.d/suricata restart

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
