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

core=167

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


KVER="xxxKVERxxx"

# Backup uEnv.txt if exist
if [ -e /boot/uEnv.txt ]; then
    cp -vf /boot/uEnv.txt /boot/uEnv.txt.org
fi

# Do some sanity checks.
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
rm -rf /boot/System.map-*
rm -rf /boot/config-*
rm -rf /boot/ipfirerd-*
rm -rf /boot/initramfs-*
rm -rf /boot/vmlinuz-*
rm -rf /boot/uImage-*
rm -rf /boot/zImage-*
rm -rf /boot/uInit-*
rm -rf /boot/dtb-*
rm -rf /lib/modules

# Remove files
rm -rvf \
	/bin/setserial \
	/etc/dracut.conf \
	/etc/fonts/conf.d/30-urw-aliases.conf \
	/etc/grub.d/README \
	/etc/rc.d/init.d/networking/red.up/99-geoip-database \
	/etc/udev/rules.d/99-fuse.rules \
	/lib/firmware/amd-ucode/microcode_amd.bin.asc \
	/lib/firmware/amd-ucode/microcode_amd_fam15h.bin.asc \
	/lib/firmware/amd-ucode/microcode_amd_fam16h.bin.asc \
	/lib/firmware/amd-ucode/microcode_amd_fam17h.bin.asc \
	/lib/firmware/ath10k/QCA4019/hw1.0/notice_ath10k_firmware-5.txt \
	/lib/firmware/ath10k/QCA6174/hw2.1/notice_ath10k_firmware-5.txt \
	/lib/firmware/ath10k/QCA6174/hw3.0/notice_ath10k_firmware-4.txt \
	/lib/firmware/ath10k/QCA6174/hw3.0/notice_ath10k_firmware-6.txt \
	/lib/firmware/ath10k/QCA9377/hw1.0/notice_ath10k_firmware-5.txt \
	/lib/firmware/ath10k/QCA9377/hw1.0/notice_ath10k_firmware-6.txt \
	/lib/firmware/ath10k/QCA9887/hw1.0/notice_ath10k_firmware-5.txt \
	/lib/firmware/ath10k/QCA9888/hw2.0/notice_ath10k_firmware-5.txt \
	/lib/firmware/ath10k/QCA988X/hw2.0/notice_ath10k_firmware-4.txt \
	/lib/firmware/ath10k/QCA988X/hw2.0/notice_ath10k_firmware-5.txt \
	/lib/firmware/ath10k/QCA9984/hw1.0/notice_ath10k_firmware-5.txt \
	/lib/firmware/ath10k/QCA99X0/hw2.0/notice_ath10k_firmware-5.txt \
	/lib/firmware/atusb/ChangeLog \
	/lib/firmware/check_whence.py \
	/lib/firmware/cis/src \
	/lib/firmware/copy-firmware.sh \
	/lib/firmware/cxgb4/t4fw-1.20.8.0.bin \
	/lib/firmware/cxgb4/t4fw-1.24.3.0.bin \
	/lib/firmware/cxgb4/t5fw-1.20.8.0.bin \
	/lib/firmware/cxgb4/t5fw-1.24.3.0.bin \
	/lib/firmware/cxgb4/t6fw-1.20.8.0.bin \
	/lib/firmware/cxgb4/t6fw-1.24.3.0.bin \
	/lib/firmware/GPL-2 \
	/lib/firmware/GPL-3 \
	/lib/firmware/isci/README \
	/lib/firmware/LICENSE.* \
	/lib/firmware/Makefile \
	/lib/firmware/mellanox/ \
	/lib/firmware/mrvl/prestera/ \
	/lib/firmware/qca/NOTICE.txt \
	/lib/firmware/qcom/NOTICE.txt \
	/lib/firmware/qcom/sdm845/ \
	/lib/firmware/qcom/sm8250 \
	/lib/firmware/README \
	/lib/firmware/WHENCE \
	/lib/kbd/keymaps/i386/qwerty/fi-latin1.map.gz \
	/lib/kbd/keymaps/i386/qwerty/fi-latin9.map.gz \
	/lib/ld-2.29.so \
	/lib/ld-2.31.so \
	/lib/ld-2.32.so \
	/lib/libcap.so \
	/lib/libhistory.so.5 \
	/lib/libhistory.so.5.2 \
	/lib/libip4tc.so.0 \
	/lib/libip4tc.so.0.1.0 \
	/lib/libip6tc.so.0 \
	/lib/libip6tc.so.0.1.0 \
	/lib/libiptc.so \
	/lib/libiptc.so.0 \
	/lib/libiptc.so.0.0.0 \
	/lib/libnss_nis-2.31.so \
	/lib/libnss_nisplus-2.31.so \
	/lib/libnss_nisplus.so.2 \
	/lib/libnss_nis.so.2 \
	/lib/libproc-3.2.8.so \
	/lib/libreadline.so.5 \
	/lib/libreadline.so.5.2 \
	/lib/libsysfs.so \
	/lib/libsysfs.so.1 \
	/lib/libsysfs.so.1.0.3 \
	/lib/udev/bluetooth_serial \
	/lib/udev/rules.d/24-bluetooth.rules \
	/lib/xtables/libxt_IMQ.so \
	/opt/pakfire/pakfire-2007.key \
	/sbin/mount.fuse \
	/sbin/raw \
	/sbin/xfs_scrub \
	/sbin/xfs_scrub_all \
	/srv/web/ipfire/cgi-bin/bluetooth.cgi \
	/usr/bin/ez-ipupdate \
	/usr/bin/fusermount \
	/usr/bin/gawk-5.1.0 \
	/usr/bin/gcov-dump \
	/usr/bin/getunimap \
	/usr/bin/mkinitrd \
	/usr/bin/mtools \
	/usr/bin/pango-querymodules \
	/usr/bin/perl5.30.0 \
	/usr/bin/setlogcons \
	/usr/bin/setvesablank \
	/usr/bin/tailf \
	/usr/bin/ulockmgr_server \
	/usr/include/python2.7 \
	/usr/lib/cairo \
	/usr/lib/dracut \
	/usr/lib/findutils/bigram \
	/usr/lib/findutils/code \
	/usr/lib/gawk/testext.so \
	/usr/lib/itcl4.2.1 \
	/usr/lib/libasan.so.5 \
	/usr/lib/libasan.so.5.0.0 \
	/usr/lib/libbfd-2.32.so \
	/usr/lib/libbfd-2.34.so \
	/usr/lib/libbfd-2.35.1.so \
	/usr/lib/libbind9-9.16.22.so \
	/usr/lib/libbind9-9.16.26.so \
	/usr/lib/libbind9.so.161 \
	/usr/lib/libbind9.so.161.0.4 \
	/usr/lib/libblkid.so \
	/usr/lib/libdns-9.16.22.so \
	/usr/lib/libdns-9.16.26.so \
	/usr/lib/libdnssec.so.7 \
	/usr/lib/libdnssec.so.7.0.0 \
	/usr/lib/libdns.so.* \
	/usr/lib/libevent-2.1.so.6 \
	/usr/lib/libevent-2.1.so.6.0.2 \
	/usr/lib/libevent_core-2.1.so.6 \
	/usr/lib/libevent_core-2.1.so.6.0.2 \
	/usr/lib/libevent_extra-2.1.so.6 \
	/usr/lib/libevent_extra-2.1.so.6.0.2 \
	/usr/lib/libevent_openssl-2.1.so.6 \
	/usr/lib/libevent_openssl-2.1.so.6.0.2 \
	/usr/lib/libevent_openssl.so \
	/usr/lib/libevent_pthreads-2.1.so.6 \
	/usr/lib/libevent_pthreads-2.1.so.6.0.2 \
	/usr/lib/libevent_pthreads.so \
	/usr/lib/libexpat.so \
	/usr/lib/libexslt.so \
	/usr/lib/libffi.so.6 \
	/usr/lib/libffi.so.6.0.4 \
	/usr/lib/libffi.so.7 \
	/usr/lib/libffi.so.7.1.0 \
	/usr/lib/libfuse.so \
	/usr/lib/libfuse.so.2 \
	/usr/lib/libfuse.so.2.9.7 \
	/usr/lib/libgdbm_compat.so \
	/usr/lib/libgdbm_compat.so.3 \
	/usr/lib/libgdbm_compat.so.3.0.0 \
	/usr/lib/libgdbm.so \
	/usr/lib/libgdbm.so.3 \
	/usr/lib/libgdbm.so.3.0.0 \
	/usr/lib/libgd.so \
	/usr/lib/libgd.so.2 \
	/usr/lib/libgd.so.2.0.0 \
	/usr/lib/libgettextlib-0.19.8.1.so \
	/usr/lib/libgettextsrc-0.19.8.1.so \
	/usr/lib/libhistory.so.6 \
	/usr/lib/libhistory.so.6.3 \
	/usr/lib/libhogweed.so.5 \
	/usr/lib/libhogweed.so.5.0 \
	/usr/lib/libidn.so \
	/usr/lib/libidn.so.11 \
	/usr/lib/libidn.so.11.6.18 \
	/usr/lib/libirs-9.16.22.so \
	/usr/lib/libisc-9.16.22.so \
	/usr/lib/libisc-9.16.26.so \
	/usr/lib/libisccc-9.16.22.so \
	/usr/lib/libisccc-9.16.26.so \
	/usr/lib/libisccc.so.161 \
	/usr/lib/libisccc.so.161.0.1 \
	/usr/lib/libisccfg-9.16.22.so \
	/usr/lib/libisccfg-9.16.26.so \
	/usr/lib/libisccfg.so.163 \
	/usr/lib/libisccfg.so.163.0.8 \
	/usr/lib/libisc.so.1100 \
	/usr/lib/libisc.so.1100.3.2 \
	/usr/lib/libisc.so.1104 \
	/usr/lib/libisc.so.1104.0.0 \
	/usr/lib/libisc.so.1105 \
	/usr/lib/libisc.so.1105.1.1 \
	/usr/lib/libisc.so.1107 \
	/usr/lib/libisc.so.1107.0.5 \
	/usr/lib/libixml.so \
	/usr/lib/libknot.so.10 \
	/usr/lib/libknot.so.10.0.0 \
	/usr/lib/libknot.so.11 \
	/usr/lib/libknot.so.11.0.0 \
	/usr/lib/libknot.so.9 \
	/usr/lib/libknot.so.9.0.0 \
	/usr/lib/liblber-2.3.so.0 \
	/usr/lib/liblber-2.3.so.0.2.8 \
	/usr/lib/libldap-2.3.so.0 \
	/usr/lib/libldap-2.3.so.0.2.8 \
	/usr/lib/libldap_r-2.3.so.0 \
	/usr/lib/libldap_r-2.3.so.0.2.8 \
	/usr/lib/libloc.so.0 \
	/usr/lib/libloc.so.0.0.0 \
	/usr/lib/liblua-5.3.so \
	/usr/lib/liblua.so \
	/usr/lib/liblwres.so.161 \
	/usr/lib/liblwres.so.161.0.4 \
	/usr/lib/libmpfr.so.4 \
	/usr/lib/libmpfr.so.4.1.5 \
	/usr/lib/libmpx.so.2 \
	/usr/lib/libmpx.so.2.0.1 \
	/usr/lib/libmpxwrappers.so.2 \
	/usr/lib/libmpxwrappers.so.2.0.1 \
	/usr/lib/libnettle.so.7 \
	/usr/lib/libnettle.so.7.0 \
	/usr/lib/libns-9.16.22.so \
	/usr/lib/libns-9.16.26.so \
	/usr/lib/libopcodes-2.32.so \
	/usr/lib/libopcodes-2.34.so \
	/usr/lib/libopcodes-2.35.1.so \
	/usr/lib/libpcre2-posix.so.2 \
	/usr/lib/libpcre2-posix.so.2.0.3 \
	/usr/lib/libpng12.so \
	/usr/lib/libpng12.so.0 \
	/usr/lib/libpng12.so.0.57.0 \
	/usr/lib/libpng.so.3 \
	/usr/lib/libpng.so.3.57.0 \
	/usr/lib/libpoppler.so.100 \
	/usr/lib/libpoppler.so.100.0.0 \
	/usr/lib/libpoppler.so.110 \
	/usr/lib/libpoppler.so.110.0.0 \
	/usr/lib/libpoppler.so.111 \
	/usr/lib/libpoppler.so.111.0.0 \
	/usr/lib/libpoppler.so.66 \
	/usr/lib/libpoppler.so.66.0.0 \
	/usr/lib/libqpdf.so.17 \
	/usr/lib/libqpdf.so.17.0.0 \
	/usr/lib/libreadline.so.6 \
	/usr/lib/libreadline.so.6.3 \
	/usr/lib/librrd.so.8.2.1 \
	/usr/lib/libsensors.so.4 \
	/usr/lib/libsensors.so.4.4.0 \
	/usr/lib/libsqlite3.so \
	/usr/lib/libthreadutil.so \
	/usr/lib/libthreadutil.so.6 \
	/usr/lib/libthreadutil.so.6.0.3 \
	/usr/lib/libulockmgr.so \
	/usr/lib/libulockmgr.so.1 \
	/usr/lib/libulockmgr.so.1.0.1 \
	/usr/lib/libupnp.so \
	/usr/lib/libuuid.so \
	/usr/lib/libxml2.so \
	/usr/lib/libxslt.so \
	/usr/lib/pango \
	/usr/lib/perl5/site_perl/5.30.0 \
	/usr/lib/python3.8/ensurepip/_bundled/pip-19.2.3-py2.py3-none-any.whl \
	/usr/lib/python3.8/idlelib/Icons/idle.icns \
	/usr/lib/python3.8/lib2to3/Grammar3.8.1.final.0.pickle \
	/usr/lib/python3.8/lib2to3/PatternGrammar3.8.1.final.0.pickle \
	/usr/lib/sqlite3.34.0 \
	/usr/lib/squid/basic_nis_auth \
	/usr/lib/squid/ext_time_quota_acl \
	/usr/lib/tcl8/8.4/platform-1.0.14.tm \
	/usr/lib/tcl8/8.4/platform-1.0.15.tm \
	/usr/lib/tcl8/8.5/msgcat-1.6.0.tm \
	/usr/lib/tcl8/8.5/tcltest-2.4.0.tm \
	/usr/lib/tcl8/8.6/http-2.8.9.tm \
	/usr/lib/tcl8/8.6/tdbc/sqlite3-1.0.4.tm \
	/usr/lib/tcl8/8.6/tdbc/sqlite3-1.1.2.tm \
	/usr/lib/tdbc1.1.2 \
	/usr/lib/tdbcmysql1.1.2 \
	/usr/lib/tdbcodbc1.1.2 \
	/usr/lib/tdbcpostgres1.1.2 \
	/usr/lib/thread2.8.6 \
	/usr/libexec/xtables-addons \
	/usr/local/bin/convert-ovpn \
	/usr/local/bin/ovpn-ccd-convert \
	/usr/local/bin/rebuild-initrd \
	/usr/local/bin/xt_geoip_build \
	/usr/local/bin/xt_geoip_update \
	/usr/sbin/batctl \
	/usr/sbin/fbset \
	/usr/sbin/fdformat \
	/usr/sbin/update-usbids.sh \
	/usr/sbin/uuidd \
	/usr/share/doc/fireinfo \
	/usr/share/GeoIP \
	/usr/share/zoneinfo/posix/US/Pacific-New \
	/usr/share/zoneinfo/right/US/Pacific-New \
	/usr/share/zoneinfo/US/Pacific-New \
	/var/lib/GeoIP

# Stop services
/etc/init.d/ipsec stop

# Extract files
extract_files

# update linker config
ldconfig

# Delete old 2007 Pakfire key from GPG keyring
GNUPGHOME="/opt/pakfire/etc/.gnupg" gpg --batch --yes --delete-keys 179740DC4D8C47DC63C099C74BDE364C64D96617

# Add new 2022 Pakfire key to GPG keyring
GNUPGHOME="/opt/pakfire/etc/.gnupg" gpg --import /opt/pakfire/pakfire-2022.key

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# Hardlink any identical files to save space
hardlink -c -vv /lib/firmware

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

# Replace /etc/mtab by symlink as mount no longer writes it
rm -vf /etc/mtab
ln -vs /proc/self/mounts /etc/mtab

# Export the location database again and reload the firewall engine
/usr/local/bin/update-location-database

# Rebuild IPS rules
perl -e "require '/var/ipfire/ids-functions.pl'; &IDS::oinkmaster();"
/etc/init.d/suricata reload

# Apply sysctl changes
/etc/init.d/sysctl start

# Apply local configuration to sshd_config
/usr/local/bin/sshctrl

# Start services
/etc/init.d/apache restart
/etc/init.d/sshd restart
if grep -q "ENABLED=on" /var/ipfire/vpn/settings; then
       /etc/init.d/ipsec start
fi

# Nano is now part of the core system, remove Pakfire metadata for it
if [ -e "/opt/pakfire/db/installed/meta-nano" ] && [ -e "/opt/pakfire/db/meta/meta-nano" ]; then
	rm -vf \
		/opt/pakfire/db/installed/meta-nano \
		/opt/pakfire/db/meta/meta-nano \
		/opt/pakfire/db/rootfiles/nano
fi

# remove lm_sensor config after collectd was started
# to reserch sensors at next boot with updated kernel
rm -f  /etc/sysconfig/lm_sensors

# Upadate Kernel version uEnv.txt
if [ -e /boot/uEnv.txt ]; then
    sed -i -e "s/KVER=.*/KVER=${KVER}/g" /boot/uEnv.txt
fi

# call user update script (needed for some arm boards)
if [ -e /boot/pakfire-kernel-update ]; then
    /boot/pakfire-kernel-update ${KVER}
fi

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
