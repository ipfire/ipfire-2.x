#!/bin/bash
############################################################################
#                                                                          #
# This file is part of the IPFire Firewall.                                #
#                                                                          #
# IPFire is free software; you can redistribute it and/or modify           #
# it under the terms of the GNU General Public License as published by     #
# the Free Software Foundation; either version 2 of the License, or        #
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
# Copyright (C) 2007 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh

#
#uninstall
#
stop_service libvirtd
extract_backup_includes
make_backup ${NAME}

remove_files

rm -f /etc/rc.d/rc*.d/*libvirt-guests
rm -f /etc/rc.d/rc*.d/*libvirtd
rm -f /etc/rc.d/rc*.d/*virtlogd

#
#install
#

# creates a new user and group called libvirt-remote if they not exist
getent group libvirt-remote >/dev/null || groupadd  libvirt-remote
getent passwd libvirt-remote >/dev/null || \
useradd -m -g libvirt-remote -s /bin/bash "libvirt-remote"

extract_files

# create diretorys in var
mkdir -p /var/cache/libvirt/qemu \
/var/lib/libvirt/boot \
/var/lib/libvirt/filesystems \
/var/lib/libvirt/images \
/var/lib/libvirt/lockd/files \
/var/lib/libvirt/qemu \
/var/log/libvirt/qemu
# set the permissions
chown -R nobody:kvm /var/cache/libvirt/qemu
chown -R nobody:kvm /var/lib/libvirt/qemu
chown -R nobody:kvm /var/lib/libvirt/images
# restore the backup
restore_backup ${NAME}

#restart virtlogd to use the new version
if [ -f "/var/run/virtlogd.pid" ]; then
# the daemon runs restart him
/etc/init.d/virtlogd restart
else
# the daemon runs not start him
/etc/init.d/virtlogd start
fi

start_service --background libvirtd

ln -svf /etc/init.d/virtlogd /etc/rc.d/rc0.d/K21virtlogd
ln -svf /etc/init.d/virtlogd /etc/rc.d/rc3.d/S69virtlogd
ln -svf /etc/init.d/virtlogd /etc/rc.d/rc6.d/K21virtlogd

ln -svf /etc/init.d/libvirtd /etc/rc.d/rc0.d/K20libvirtd
ln -svf /etc/init.d/libvirtd /etc/rc.d/rc3.d/S70libvirtd
ln -svf /etc/init.d/libvirtd /etc/rc.d/rc6.d/K20libvirtd

ln -svf /etc/init.d/libvirt-guests /etc/rc.d/rc0.d/K19libvirt-guests
ln -svf /etc/init.d/libvirt-guests /etc/rc.d/rc3.d/S71libvirt-guests
ln -svf /etc/init.d/libvirt-guests /etc/rc.d/rc6.d/K19libvirt-guests

