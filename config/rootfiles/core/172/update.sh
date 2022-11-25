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

core=172

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Stop services
/etc/rc.d/init.d/ipsec stop
/usr/local/bin/openvpnctrl -k
/usr/local/bin/openvpnctrl -kn2n
/etc/rc.d/init.d/sshd stop
/etc/rc.d/init.d/unbound stop

KVER="xxxKVERxxx"

# Backup uEnv.txt if exist
if [ -e /boot/uEnv.txt ]; then
    cp -vf /boot/uEnv.txt /boot/uEnv.txt.org
fi

# Remove files
rm -rvf \
	/etc/pcmcia \
	/etc/strongswan.d/scepclient.conf \
	/etc/udev/rules.d/60-pcmcia.rules \
	/lib/firmware/cnm/wave521c_j721s2_codec_fw.bin \
	/lib/firmware/cxgb4/t4fw-1.26.6.0.bin \
	/lib/firmware/cxgb4/t5fw-1.26.6.0.bin \
	/lib/firmware/cxgb4/t6fw-1.26.6.0.bin \
	/lib/firmware/mediatek/sof/sof-mt8186-mt6366-da7219-max98357.tplg \
	/lib/firmware/mediatek/sof/sof-mt8186-mt6366-rt1019-rt5682s.tplg \
	/lib/firmware/qcom/a530_zap.b00 \
	/lib/firmware/qcom/a530_zap.b01 \
	/lib/firmware/qcom/a530_zap.b02 \
	/lib/firmware/qcom/venus-1.8/venus.b* \
	/lib/firmware/qcom/venus-4.2/venus.b* \
	/lib/firmware/qcom/venus-5.2/venus.b* \
	/lib/firmware/qcom/venus-5.4/venus.b* \
	/lib/firmware/qcom/vpu-1.0/venus.b* \
	/lib/firmware/qcom/vpu-2.0/venus.b* \
	/lib/firmware/qcom/vpu-2.0/venus.mdt \
	/lib/firmware/rtl_bt \
	/lib/libz.so.1.2.12 \
	/sbin/lspcmcia \
	/sbin/pccardctl \
	/sbin/pcmcia-check-broken-cis \
	/sbin/pcmcia-socket-startup \
	/usr/lib/libbind9-9.16.33.so \
	/usr/lib/libdns-9.16.33.so \
	/usr/lib/libexpat.so.1.8.9 \
	/usr/lib/libhistory.so.8.1 \
	/usr/lib/libirs-9.16.33.so \
	/usr/lib/libisc-9.16.33.so \
	/usr/lib/libisccc-9.16.33.so \
	/usr/lib/libisccfg-9.16.33.so \
	/usr/lib/liblzma.so.5.2.5 \
	/usr/lib/libnetfilter_conntrack.so.3.7.0 \
	/usr/lib/libns-9.16.33.so \
	/usr/lib/libreadline.so.8.1 \
	/usr/lib/libunbound.so.8.1.1* \
	/usr/lib/libxml2.so.2.9.* \
	/usr/lib/python3.10/ensurepip/_bundled/pip-21* \
	/usr/lib/python3.10/ensurepip/_bundled/setuptools-5* \
	/usr/lib/python3.10/lib2to3/Grammar3.10.* \
	/usr/lib/python3.10/lib2to3/PatternGrammar3.10.* \
	/usr/lib/python3.10/site-packages/pip-21.* \
	/usr/lib/python3.10/site-packages/pip/_internal/utils/parallel.py \
	/usr/lib/python3.10/site-packages/pip/_internal/utils/pkg_resources.py \
	/usr/lib/python3.10/site-packages/pip/_vendor/appdirs.py \
	/usr/lib/python3.10/site-packages/pip/_vendor/chardet/compat.py \
	/usr/lib/python3.10/site-packages/pip/_vendor/distlib/_backport \
	/usr/lib/python3.10/site-packages/pip/_vendor/distro.py \
	/usr/lib/python3.10/site-packages/pip/_vendor/html5lib \
	/usr/lib/python3.10/site-packages/pip/_vendor/msgpack/_version.py \
	/usr/lib/python3.10/site-packages/pip/_vendor/progress \
	/usr/lib/python3.10/site-packages/pip/_vendor/pyparsing.py \
	/usr/lib/python3.10/site-packages/pip/_vendor/urllib3/packages/ssl_match_hostname \
	/usr/lib/python3.10/site-packages/pkg_resources/_vendor/packaging/_compat.py \
	/usr/lib/python3.10/site-packages/pkg_resources/_vendor/packaging/_typing.py \
	/usr/lib/python3.10/site-packages/pkg_resources/_vendor/pyparsing.py \
	/usr/lib/python3.10/site-packages/pkg_resources/tests/data \
	/usr/lib/python3.10/site-packages/setuptools-5* \
	/usr/lib/python3.10/site-packages/setuptools/_distutils/py35compat.py \
	/usr/lib/python3.10/site-packages/setuptools/_vendor/packaging/_compat.py \
	/usr/lib/python3.10/site-packages/setuptools/_vendor/packaging/_typing.py \
	/usr/lib/python3.10/site-packages/setuptools/_vendor/pyparsing.py \
	/usr/lib/python3.10/site-packages/setuptools/config.py \
	/usr/lib/python3.10/site-packages/setuptools_rust/utils.py \
	/usr/libexec/ipsec/scepclient \
	/var/ipfire/ca/dh1024.pem

# Remove powertop add-on, if installed
if [ -e "/opt/pakfire/db/installed/meta-powertop" ]; then
	for i in $(</opt/pakfire/db/rootfiles/powertop); do
		rm -rfv "/${i}"
	done
fi
rm -vf \
	/opt/pakfire/db/installed/meta-powertop \
	/opt/pakfire/db/meta/meta-powertop \
	/opt/pakfire/db/rootfiles/powertop

# Extract files
extract_files

# update linker config
ldconfig

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# Apply local configuration to sshd_config
/usr/local/bin/sshctrl

# Correct permissions of some library files
chown -Rv root:root /var/ipfire/connscheduler/lib.pl /var/ipfire/updatexlrator/updxlrator-lib.pl /var/ipfire/menu.d/*

# Replace existing OpenVPN Diffie-Hellman parameter by ffdhe4096, as specified in RFC 7919
if [ -f /var/ipfire/ovpn/server.conf ]; then
	sed -i 's|/var/ipfire/ovpn/ca/dh1024.pem|/etc/ssl/ffdhe4096.pem|' /var/ipfire/ovpn/server.conf
fi

if [ -f "/var/ipfire/ovpn/n2nconf/*/*.conf" ]; then
	sed -i 's|/var/ipfire/ovpn/ca/dh1024.pem|/etc/ssl/ffdhe4096.pem|' /var/ipfire/ovpn/n2nconf/*/*.conf
fi

# Start services
/etc/init.d/unbound start
if grep -q "ENABLE_SSH=on" /var/ipfire/remote/settings; then
	/etc/init.d/sshd start
fi
if grep -q "ENABLED=on" /var/ipfire/ovpn/settings; then
	/usr/local/bin/openvpnctrl -s
	/usr/local/bin/openvpnctrl -sn2n
fi
if grep -q "ENABLED=on" /var/ipfire/vpn/settings; then
	/etc/init.d/ipsec start
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

# Call user update script (needed for some ARM boards)
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
