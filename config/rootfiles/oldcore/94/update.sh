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
# Copyright (C) 2015 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

# Remove old core updates from pakfire cache to save space...
core=94
for (( i=1; i<=$core; i++ ))
do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Stop services
/etc/init.d/squid stop
/etc/init.d/sshd stop
/etc/init.d/dnsmasq stop

# Extract files
extract_files

# Restart init after glibc update
telinit u

# Update Language cache
/usr/local/bin/update-lang-cache

# Update SSH configuration
sed -i /etc/ssh/sshd_config \
	-e 's/^#PermitRootLogin yes$/PermitRootLogin yes/' \
	-e 's|^#\?HostKey /etc/ssh/ssh_host_dsa_key$||' \
	-e 's|^#\?HostKey /etc/ssh/ssh_host_ecdsa_key$||' \
	-e 's|^#\?HostKey /etc/ssh/ssh_host_ed25519_key$||' \
	-e 's|^#\?HostKey /etc/ssh/ssh_host_rsa_key$|HostKey /etc/ssh/ssh_host_ecdsa_key\nHostKey /etc/ssh/ssh_host_ed25519_key\nHostKey /etc/ssh/ssh_host_rsa_key|' \

# Move away old and unsupported keys
mv -f /etc/ssh/ssh_host_dsa_key{,.old}
# Regenerating weak RSA keys
mv -f /etc/ssh/ssh_host_key{,.old}
mv -f /etc/ssh/ssh_host_rsa_key{,.old}

# Update crontab
sed -i /var/spool/cron/root.orig -e "/Force an update once a month/d"
sed -i /var/spool/cron/root.orig -e "/ddns update-all --force/d"

grep -q "dma -q" /var/spool/cron/root.orig || cat <<EOF >> /var/spool/cron/root.orig

# Retry sending spooled mails regularly
%hourly * /usr/sbin/dma -q

# Cleanup the mail spool directory
%weekly * * /usr/sbin/dma-cleanup-spool
EOF

fcrontab -z &>/dev/null

# DMA - reconfigure Postfix if exists
if [ -e /etc/postfix/main.cf ] && [ ! -e "/usr/sbin/sendmail.postfix" ]; then
	mv /usr/sbin/sendmail /usr/sbin/sendmail.postfix
	/usr/sbin/alternatives --install /usr/sbin/sendmail sendmail /usr/sbin/sendmail.postfix 15
	sed -i 's/usr\/sbin\/sendmail/usr/sbin/sendmail.postfix/' /opt/pakfire/db/rootfiles/postfix
fi
# DMA - configure dma as default mta
mkdir -p /etc/alternatives
mkdir -p /var/lib/alternatives
/usr/sbin/alternatives --install /usr/sbin/sendmail sendmail /usr/sbin/sendmail.dma 20

# Start services
/etc/init.d/dnsmasq start
/etc/init.d/sshd start
/etc/init.d/squid start

# This update need a reboot...
#touch /var/run/need_reboot

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
