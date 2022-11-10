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
/etc/rc.d/init.d/sshd stop
/etc/rc.d/init.d/unbound stop

# Remove files
rm -rvf \
	/etc/strongswan.d/scepclient.conf \
	/lib/libz.so.1.2.12 \
	/usr/lib/libexpat.so.1.8.9 \
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
	/usr/libexec/ipsec/scepclient

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

# Start services
/etc/init.d/unbound start
if grep -q "ENABLE_SSH=on" /var/ipfire/remote/settings; then
	/etc/init.d/sshd start
fi
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
