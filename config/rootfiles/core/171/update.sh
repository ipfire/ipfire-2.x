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

core=171

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
/etc/rc.d/init.d/apache stop
/etc/rc.d/init.d/unbound stop
/etc/rc.d/init.d/squid stop
/usr/local/bin/openvpnctrl -k
/usr/local/bin/openvpnctrl -kn2n
/etc/rc.d/init.d/ipsec stop
/etc/init.d/rc.d/suricata stop
/etc/rc.d/init.d/collectd stop

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
	/lib/firmware/3com/3C359.bin \
	/lib/firmware/TDA7706_OM_v2.5.1_boot.txt \
	/lib/firmware/TDA7706_OM_v3.0.2_boot.txt \
	/lib/firmware/atmsar11.fw \
	/lib/firmware/bnx2/bnx2-mips-06-4.6.16.fw \
	/lib/firmware/bnx2/bnx2-mips-06-5.0.0.j3.fw \
	/lib/firmware/bnx2/bnx2-mips-06-5.0.0.j6.fw \
	/lib/firmware/bnx2/bnx2-mips-06-6.0.15.fw \
	/lib/firmware/bnx2/bnx2-mips-06-6.2.1.fw \
	/lib/firmware/bnx2/bnx2-mips-09-4.6.17.fw \
	/lib/firmware/bnx2/bnx2-mips-09-5.0.0.j15.fw \
	/lib/firmware/bnx2/bnx2-mips-09-5.0.0.j3.fw \
	/lib/firmware/bnx2/bnx2-mips-09-5.0.0.j9.fw \
	/lib/firmware/bnx2/bnx2-mips-09-6.0.17.fw \
	/lib/firmware/bnx2/bnx2-mips-09-6.2.1.fw \
	/lib/firmware/bnx2/bnx2-mips-09-6.2.1a.fw \
	/lib/firmware/bnx2/bnx2-rv2p-06-4.6.16.fw \
	/lib/firmware/bnx2/bnx2-rv2p-06-5.0.0.j3.fw \
	/lib/firmware/bnx2/bnx2-rv2p-09-4.6.15.fw \
	/lib/firmware/bnx2/bnx2-rv2p-09-5.0.0.j10.fw \
	/lib/firmware/bnx2/bnx2-rv2p-09-5.0.0.j3.fw \
	/lib/firmware/bnx2/bnx2-rv2p-09ax-5.0.0.j10.fw \
	/lib/firmware/bnx2/bnx2-rv2p-09ax-5.0.0.j3.fw \
	/lib/firmware/bnx2x-e1-4.8.53.0.fw \
	/lib/firmware/bnx2x-e1-5.2.13.0.fw \
	/lib/firmware/bnx2x-e1-5.2.7.0.fw \
	/lib/firmware/bnx2x-e1h-4.8.53.0.fw \
	/lib/firmware/bnx2x-e1h-5.2.13.0.fw \
	/lib/firmware/bnx2x-e1h-5.2.7.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1-6.0.34.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1-6.2.5.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1-6.2.9.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1-7.0.20.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1-7.0.23.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1-7.0.29.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1-7.10.51.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1-7.12.30.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1-7.2.16.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1-7.2.51.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1-7.8.17.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1-7.8.19.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1-7.8.2.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1h-6.0.34.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1h-6.2.5.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1h-6.2.9.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1h-7.0.20.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1h-7.0.23.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1h-7.0.29.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1h-7.10.51.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1h-7.12.30.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1h-7.2.16.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1h-7.2.51.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1h-7.8.17.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1h-7.8.19.0.fw \
	/lib/firmware/bnx2x/bnx2x-e1h-7.8.2.0.fw \
	/lib/firmware/bnx2x/bnx2x-e2-6.0.34.0.fw \
	/lib/firmware/bnx2x/bnx2x-e2-6.2.5.0.fw \
	/lib/firmware/bnx2x/bnx2x-e2-6.2.9.0.fw \
	/lib/firmware/bnx2x/bnx2x-e2-7.0.20.0.fw \
	/lib/firmware/bnx2x/bnx2x-e2-7.0.23.0.fw \
	/lib/firmware/bnx2x/bnx2x-e2-7.0.29.0.fw \
	/lib/firmware/bnx2x/bnx2x-e2-7.10.51.0.fw \
	/lib/firmware/bnx2x/bnx2x-e2-7.12.30.0.fw \
	/lib/firmware/bnx2x/bnx2x-e2-7.2.16.0.fw \
	/lib/firmware/bnx2x/bnx2x-e2-7.2.51.0.fw \
	/lib/firmware/bnx2x/bnx2x-e2-7.8.17.0.fw \
	/lib/firmware/bnx2x/bnx2x-e2-7.8.19.0.fw \
	/lib/firmware/bnx2x/bnx2x-e2-7.8.2.0.fw \
	/lib/firmware/cbfw-3.2.1.1.bin \
	/lib/firmware/cbfw-3.2.3.0.bin \
	/lib/firmware/ct2fw-3.2.1.1.bin \
	/lib/firmware/ct2fw-3.2.3.0.bin \
	/lib/firmware/ctfw-3.2.1.1.bin \
	/lib/firmware/ctfw-3.2.3.0.bin \
	/lib/firmware/intel/ice/ddp/ice-1.3.28.0.pkg \
	/lib/firmware/intel/ibt-* \
	/lib/firmware/intelliport2.bin \
	/lib/firmware/LICENCE* \
	/lib/firmware/mediatek/BT_RAM_CODE_MT7922_1_1_hdr.bin \
	/lib/firmware/mediatek/BT_RAM_CODE_MT7961_1_2_hdr.bin \
	/lib/firmware/tr_smctr.bin \
	/usr/bin/perl5.32* \
	/usr/lib/libbfd-2.37.so \
	/usr/lib/libbind9-9.16.31.so \
	/usr/lib/libbind9-9.16.32.so \
	/usr/lib/libdns-9.16.2* \
	/usr/lib/libdns-9.16.31.so \
	/usr/lib/libdns-9.16.32.so \
	/usr/lib/libefiboot.so.1.37 \
	/usr/lib/libefivar.so.1.37 \
	/usr/lib/libexpat.so.1.8.8 \
	/usr/lib/libhogweed.so.6.4 \
	/usr/lib/libirs-9.16.31.so \
	/usr/lib/libirs-9.16.32.so \
	/usr/lib/libisc-9.16.31.so \
	/usr/lib/libisc-9.16.32.so \
	/usr/lib/libisccc-9.16.31.so \
	/usr/lib/libisccc-9.16.32.so \
	/usr/lib/libisccfg-9.16.31.so \
	/usr/lib/libisccfg-9.16.32.so \
	/usr/lib/libnettle.so.8.4 \
	/usr/lib/libns-9.16.31.so \
	/usr/lib/libns-9.16.32.so \
	/usr/lib/libopcodes-2.36* \
	/usr/lib/libopcodes-2.37.so \
	/usr/lib/libunbound.so.8.1.18 \
	/usr/lib/perl5/5.32* \
	/usr/lib/perl5/site_perl/5.32* \
	/usr/share/man/* \
	/usr/share/usb_modeswitch/1004:61aa \
	/usr/share/usb_modeswitch/12d1:\#android \
	/usr/share/usb_modeswitch/12d1:\#linux \
	/usr/share/usb_modeswitch/19d2:\#linux \
	/srv/web/ipfire/html/themes/ipfire/include/css/style-rounded.css

# Extract files
extract_files

# update linker config
ldconfig

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# Rebuild fcrontab from scratch
/usr/bin/fcrontab -z

# Fix backup file permissions
chown -v root:root /var/ipfire/backup/{in,ex}clude*

# Start services
/etc/rc.d/init.d/collectd start
if grep -q "ENABLED=on" /var/ipfire/suricata/settings; then
	/etc/rc.d/init.d/suricata start
fi
/etc/rc.d/init.d/unbound start
/etc/rc.d/init.d/apache start
if grep -q "ENABLED=on" /var/ipfire/ovpn/settings; then
	/usr/local/bin/openvpnctrl -s
	/usr/local/bin/openvpnctrl -sn2n
fi
if grep -q "ENABLED=on" /var/ipfire/vpn/settings; then
	/etc/init.d/ipsec start
fi
if [ -f /var/ipfire/proxy/enable ]; then
	/etc/init.d/squid start
fi

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
