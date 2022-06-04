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

core=168

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Stop services
/etc/init.d/ipsec stop
/etc/init.d/squid stop
/usr/local/bin/openvpnctrl -k
/usr/local/bin/openvpnctrl -kn2n
/etc/init.d/suricata stop

# Remove files
rm -rvf \
	/etc/fcron.daily/suricata \
	/etc/fcron.weekly/suricata \
	/lib/firmware/cxgb4/t4fw-1.26.4.0.bin \
	/lib/firmware/cxgb4/t5fw-1.26.4.0.bin \
	/lib/firmware/cxgb4/t6fw-1.26.4.0.bin \
	/lib/firmware/intel/ice/ddp-comms/ice_comms-1.3.20.0.pkg \
	/lib/firmware/silabs \
	/lib/libprocps.so* \
	/usr/bin/dnet-config \
	/usr/bin/sdparm \
	/usr/lib/libart_lgpl_2.so* \
	/usr/lib/libdnet.la \
	/usr/lib/libdnet.so* \
	/usr/lib/libevent-1.4.so* \
	/usr/lib/libevent_core-1.4.so* \
	/usr/lib/libevent_extra-1.4.so* \
	/usr/lib/liblber-2.4.so* \
	/usr/lib/libnl.so* \
	/usr/lib/libpri.so* \
	/usr/lib/libsolv.so* \
	/usr/lib/libsolvext.so* \
	/usr/lib/libusb.so \
	/usr/lib/libusb-0.1.so* \
	/usr/sbin/dnet

# Remove netbpm add-on, if installed
if [ -e "/opt/pakfire/db/installed/meta-netbpm" ]; then
	for i in $(</opt/pakfire/db/rootfiles/netbpm); do
		rm -rfv "/${i}"
	done
fi
rm -vf \
	/opt/pakfire/db/installed/meta-netbpm \
	/opt/pakfire/db/meta/meta-netbpm \
	/opt/pakfire/db/rootfiles/netbpm

# Extract files
extract_files

# update linker config
ldconfig

# Run IDSv4 converter
convert-ids-backend-files

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# Delete orphaned Oinkmaster and Suricata default ruleset
rm -vf \
	/usr/local/bin/oinkmaster.pl \
	/var/ipfire/suricata/oinkmaster.conf \
	/var/ipfire/suricata/suricata-default-rules.yaml

# Apply local configuration to sshd_config
/usr/local/bin/sshctrl

# Apply sysctl changes
/etc/init.d/sysctl start

# Fix permissions of /etc/sudoers.d/
chmod -v 750 /etc/sudoers.d
chmod -v 640 /etc/sudoers.d/*

# Rebuild initial ramdisk to apply microcode updates
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

# Add rd.auto to kernel command line
if ! grep -q rd.auto /etc/default/grub; then
	sed -e "s/panic=10/& rd.auto/" -i /etc/default/grub
fi

# Repair any broken MDRAID arrays
/usr/local/bin/repair-mdraid

# Rebuild fcrontab from scratch
/usr/bin/fcrontab -z

# Start services
/etc/init.d/fcron restart
/etc/init.d/sshd restart
/etc/init.d/vnstatd restart
/etc/init.d/squid start
/usr/local/bin/openvpnctrl -s
/usr/local/bin/openvpnctrl -sn2n
/etc/init.d/suricata start
if grep -q "ENABLED=on" /var/ipfire/vpn/settings; then
       /etc/init.d/ipsec start
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
