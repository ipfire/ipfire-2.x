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
# Copyright (C) 2023 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

core=174

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Stop services
/etc/rc.d/init.d/apache stop
/etc/rc.d/init.d/squid stop
/etc/rc.d/init.d/ipsec stop

# Extract files
extract_files

# Remove files
rm -rfv \
	/lib/firmware/cxgb4/t4fw-1.27.0.0.bin \
	/lib/firmware/cxgb4/t5fw-1.27.0.0.bin \
	/lib/firmware/cxgb4/t6fw-1.27.0.0.bin \
	/lib/firmware/iwlwifi-1000-3.ucode \
	/lib/firmware/iwlwifi-3168-22.ucode \
	/lib/firmware/iwlwifi-3168-27.ucode \
	/lib/firmware/iwlwifi-5000-1.ucode \
	/lib/firmware/iwlwifi-5000-2.ucode \
	/lib/firmware/iwlwifi-6000g2a-5.ucode \
	/lib/firmware/iwlwifi-6000g2b-5.ucode \
	/lib/firmware/iwlwifi-6050-4.ucode \
	/lib/firmware/iwlwifi-7265D-22.ucode \
	/lib/firmware/iwlwifi-7265D-27.ucode \
	/lib/firmware/iwlwifi-8000C-22.ucode \
	/lib/firmware/iwlwifi-8000C-27.ucode \
	/lib/firmware/iwlwifi-8000C-31.ucode \
	/lib/firmware/iwlwifi-8265-22.ucode \
	/lib/firmware/iwlwifi-8265-27.ucode \
	/lib/firmware/iwlwifi-8265-31.ucode \
	/lib/firmware/iwlwifi-9000-pu-b0-jf-b0-33.ucode \
	/lib/firmware/iwlwifi-9000-pu-b0-jf-b0-41.ucode \
	/lib/firmware/iwlwifi-9000-pu-b0-jf-b0-43.ucode \
	/lib/firmware/iwlwifi-9260-th-b0-jf-b0-33.ucode \
	/lib/firmware/iwlwifi-9260-th-b0-jf-b0-41.ucode \
	/lib/firmware/iwlwifi-9260-th-b0-jf-b0-43.ucode \
	/lib/firmware/iwlwifi-Qu-b0-hr-b0-48.ucode \
	/lib/firmware/iwlwifi-Qu-b0-hr-b0-53.ucode \
	/lib/firmware/iwlwifi-Qu-b0-hr-b0-55.ucode \
	/lib/firmware/iwlwifi-Qu-b0-hr-b0-62.ucode \
	/lib/firmware/iwlwifi-Qu-b0-hr-b0-63.ucode \
	/lib/firmware/iwlwifi-Qu-b0-hr-b0-68.ucode \
	/lib/firmware/iwlwifi-Qu-b0-hr-b0-71.ucode \
	/lib/firmware/iwlwifi-Qu-b0-jf-b0-48.ucode \
	/lib/firmware/iwlwifi-Qu-b0-jf-b0-53.ucode \
	/lib/firmware/iwlwifi-Qu-b0-jf-b0-55.ucode \
	/lib/firmware/iwlwifi-Qu-b0-jf-b0-62.ucode \
	/lib/firmware/iwlwifi-Qu-b0-jf-b0-63.ucode \
	/lib/firmware/iwlwifi-Qu-b0-jf-b0-68.ucode \
	/lib/firmware/iwlwifi-Qu-b0-jf-b0-71.ucode \
	/lib/firmware/iwlwifi-Qu-c0-hr-b0-48.ucode \
	/lib/firmware/iwlwifi-Qu-c0-hr-b0-53.ucode \
	/lib/firmware/iwlwifi-Qu-c0-hr-b0-55.ucode \
	/lib/firmware/iwlwifi-Qu-c0-hr-b0-62.ucode \
	/lib/firmware/iwlwifi-Qu-c0-hr-b0-63.ucode \
	/lib/firmware/iwlwifi-Qu-c0-hr-b0-68.ucode \
	/lib/firmware/iwlwifi-Qu-c0-hr-b0-71.ucode \
	/lib/firmware/iwlwifi-Qu-c0-jf-b0-48.ucode \
	/lib/firmware/iwlwifi-Qu-c0-jf-b0-53.ucode \
	/lib/firmware/iwlwifi-Qu-c0-jf-b0-55.ucode \
	/lib/firmware/iwlwifi-Qu-c0-jf-b0-62.ucode \
	/lib/firmware/iwlwifi-Qu-c0-jf-b0-63.ucode \
	/lib/firmware/iwlwifi-Qu-c0-jf-b0-68.ucode \
	/lib/firmware/iwlwifi-Qu-c0-jf-b0-71.ucode \
	/lib/firmware/iwlwifi-QuZ-a0-hr-b0-48.ucode \
	/lib/firmware/iwlwifi-QuZ-a0-hr-b0-53.ucode \
	/lib/firmware/iwlwifi-QuZ-a0-hr-b0-55.ucode \
	/lib/firmware/iwlwifi-QuZ-a0-hr-b0-62.ucode \
	/lib/firmware/iwlwifi-QuZ-a0-hr-b0-63.ucode \
	/lib/firmware/iwlwifi-QuZ-a0-hr-b0-67.ucode \
	/lib/firmware/iwlwifi-QuZ-a0-hr-b0-68.ucode \
	/lib/firmware/iwlwifi-QuZ-a0-hr-b0-71.ucode \
	/lib/firmware/iwlwifi-QuZ-a0-jf-b0-48.ucode \
	/lib/firmware/iwlwifi-QuZ-a0-jf-b0-53.ucode \
	/lib/firmware/iwlwifi-QuZ-a0-jf-b0-55.ucode \
	/lib/firmware/iwlwifi-QuZ-a0-jf-b0-62.ucode \
	/lib/firmware/iwlwifi-QuZ-a0-jf-b0-63.ucode \
	/lib/firmware/iwlwifi-QuZ-a0-jf-b0-68.ucode \
	/lib/firmware/iwlwifi-QuZ-a0-jf-b0-71.ucode \
	/lib/firmware/iwlwifi-cc-a0-46.ucode \
	/lib/firmware/iwlwifi-cc-a0-48.ucode \
	/lib/firmware/iwlwifi-cc-a0-53.ucode \
	/lib/firmware/iwlwifi-cc-a0-55.ucode \
	/lib/firmware/iwlwifi-cc-a0-62.ucode \
	/lib/firmware/iwlwifi-cc-a0-63.ucode \
	/lib/firmware/iwlwifi-cc-a0-67.ucode \
	/lib/firmware/iwlwifi-cc-a0-68.ucode \
	/lib/firmware/iwlwifi-cc-a0-71.ucode \
	/lib/firmware/iwlwifi-so-a0-gf-a0-64.ucode \
	/lib/firmware/iwlwifi-so-a0-gf-a0-67.ucode \
	/lib/firmware/iwlwifi-so-a0-gf-a0-68.ucode \
	/lib/firmware/iwlwifi-so-a0-gf-a0-71.ucode \
	/lib/firmware/iwlwifi-so-a0-gf4-a0-67.ucode \
	/lib/firmware/iwlwifi-so-a0-gf4-a0-68.ucode \
	/lib/firmware/iwlwifi-so-a0-gf4-a0-71.ucode \
	/lib/firmware/iwlwifi-so-a0-hr-b0-64.ucode \
	/lib/firmware/iwlwifi-so-a0-hr-b0-68.ucode \
	/lib/firmware/iwlwifi-so-a0-hr-b0-71.ucode \
	/lib/firmware/iwlwifi-so-a0-jf-b0-64.ucode \
	/lib/firmware/iwlwifi-so-a0-jf-b0-68.ucode \
	/lib/firmware/iwlwifi-so-a0-jf-b0-71.ucode \
	/lib/firmware/iwlwifi-ty-a0-gf-a0-62.ucode \
	/lib/firmware/iwlwifi-ty-a0-gf-a0-63.ucode \
	/lib/firmware/iwlwifi-ty-a0-gf-a0-67.ucode \
	/lib/firmware/iwlwifi-ty-a0-gf-a0-68.ucode \
	/lib/firmware/iwlwifi-ty-a0-gf-a0-71.ucode \
	/lib/firmware/qca \
	/usr/bin/srptool \
	/usr/lib/libbind9-9.16.37.so \
	/usr/lib/libboost*.so.1.76.0 \
	/usr/lib/libdns-9.16.37.so \
	/usr/lib/libirs-9.16.37.so \
	/usr/lib/libisc-9.16.37.so \
	/usr/lib/libisccc-9.16.37.so \
	/usr/lib/libisccfg-9.16.37.so \
	/usr/lib/libns-9.16.37.so \
	/usr/local/share/locale/de/LC_MESSAGES/elinks.mo

# update linker config
ldconfig

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# Start services
telinit u
/etc/rc.d/init.d/apache start
if [ -f /var/ipfire/proxy/enable ]; then
	/etc/init.d/squid start
fi
if grep -q "ENABLED=on" /var/ipfire/vpn/settings; then
	/etc/rc.d/init.d/ipsec start
fi

# Rebuild initial ramdisk to apply microcode updates
dracut --regenerate-all --force
case "$(uname -m)" in
        aarch64)
                mkimage -A arm64 -T ramdisk -C lzma -d /boot/initramfs-${KVER}-ipfire.img /boot/uInit-${KVER}-ipfire
                # dont remove initramfs because grub need this to boot.
                ;;
esac

# perl-TimeDate is now part of the core system, remove Pakfire metadata for it
if [ -e "/opt/pakfire/db/installed/meta-perl-TimeDate" ] && [ -e "/opt/pakfire/db/meta/meta-perl-TimeDate" ]; then
	rm -vf \
		/opt/pakfire/db/installed/meta-perl-TimeDate \
		/opt/pakfire/db/meta/meta-perl-TimeDate \
		/opt/pakfire/db/rootfiles/perl-TimeDate
fi

# Update IP blocklists to resolve fallout of #13072 as quickly as possible
/usr/local/bin/update-location-database

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
