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

# Stop services
/etc/rc.d/init.d/unbound stop
/etc/rc.d/init.d/suricata stop

KVER="xxxKVERxxx"

# Backup uEnv.txt if exist
if [ -e /boot/uEnv.txt ]; then
    cp -vf /boot/uEnv.txt /boot/uEnv.txt.org
fi

# Do some sanity checks prior to the kernel update
case $(uname -r) in
    *-ipfire*)
	# Ok.
	;;
    *)
	exit_with_error "ERROR cannot update. No IPFire Kernel." 1
	;;
esac

# Check diskspace on root
ROOTSPACE=`df / -Pk | sed "s| * | |g" | cut -d" " -f4 | tail -n 1`

if [ $ROOTSPACE -lt 100000 ]; then
    exit_with_error "ERROR cannot update because not enough free space on root." 2
    exit 2
fi

# Remove the old kernel
rm -rvf \
	/boot/System.map-* \
	/boot/config-* \
	/boot/ipfirerd-* \
	/boot/initramfs-* \
	/boot/vmlinuz-* \
	/boot/uImage-* \
	/boot/zImage-* \
	/boot/uInit-* \
	/boot/dtb-* \
	/lib/modules

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
	/usr/lib/libbind9-9.16.30.so \
	/usr/lib/libdnet* \
	/usr/lib/libdns-9.16.30.so \
	/usr/lib/libgnutls.so.30.33.1 \
	/usr/lib/libirs-9.16.2* \
	/usr/lib/libirs-9.16.30.so \
	/usr/lib/libisc-9.16.2* \
	/usr/lib/libisc-9.16.30.so \
	/usr/lib/libisccc-9.16.2* \
	/usr/lib/libisccc-9.16.30.so \
	/usr/lib/libisccfg-9.16.2* \
	/usr/lib/libisccfg-9.16.30.so \
	/usr/lib/libldap-* \
	/usr/lib/libldap_r-* \
	/usr/lib/libns-9.16.2* \
	/usr/lib/libns-9.16.30.so \
	/usr/lib/libopenjp2.so.2.3.* \
	/usr/lib/libpoppler.so.11* \
	/usr/lib/libunbound.so.8.1.17 \
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

# Create necessary files for IPBlocklist and set their ownership accordingly (#12917)
touch /var/ipfire/ipblocklist/{settings,modified}
chown nobody:nobody /var/ipfire/ipblocklist/{settings,modified}

# Rebuild fcrontab from scratch
/usr/bin/fcrontab -z

# Update collectd.conf
sed -i /etc/collectd.conf \
	-e "/LoadPlugin entropy/d"

# Stop collectd Sevice
/etc/init.d/collectd stop

# Cleanup old collectd statistics...
rm -rvf /var/log/rrd/collectd/localhost/processes-mysqld \
	/var/log/rrd/collectd/localhost/processes-snort \
	/var/log/rrd/collectd/localhost/processes-rtorrent \
	/var/log/rrd/collectd/localhost/processes-asterisk \
	/var/log/rrd/collectd/localhost/processes-java \
	/var/log/rrd/collectd/localhost/processes-spamd \
	/var/log/rrd/collectd/localhost/entropy

# Start collectd
/etc/init.d/collectd start

# Start services
/etc/rc.d/init.d/unbound start
/etc/rc.d/init.d/suricata start

# Harden mount options of /boot
sed -E -i "s/\s+\/boot\s+auto\s+defaults\s+/ \/boot    auto defaults,nodev,noexec,nosuid   /g" /etc/fstab

# Regenerate all initrds
dracut --regenerate-all --force
case "$(uname -m)" in
	armv*)
		mkimage -A arm -T ramdisk -C lzma -d /boot/initramfs-${KVER}-ipfire.img /boot/uInit-${KVER}-ipfire
		rm /boot/initramfs-${KVER}-ipfire.img
		;;
	aarch64)
		mkimage -A arm64 -T ramdisk -C lzma -d /boot/initramfs-${KVER}-ipfire.img /boot/uInit-${KVER}-ipfire
		# dont remove initramfs because grub need this to boot.
		;;
esac

# This update needs a reboot...
touch /var/run/need_reboot

# Finish
/etc/init.d/fireinfo start
sendprofile

# remove lm_sensor config after collectd was started
# to reserch sensors at next boot with updated kernel
rm -f  /etc/sysconfig/lm_sensors

# Upadate Kernel version in uEnv.txt
if [ -e /boot/uEnv.txt ]; then
    sed -i -e "s/KVER=.*/KVER=${KVER}/g" /boot/uEnv.txt
fi

# Call user update script (needed for some ARM boards)
if [ -e /boot/pakfire-kernel-update ]; then
    /boot/pakfire-kernel-update ${KVER}
fi

# Update grub config to display new core version
if [ -e /boot/grub/grub.cfg ]; then
	grub-mkconfig -o /boot/grub/grub.cfg
fi

sync

# Don't report the exitcode last command
exit 0
