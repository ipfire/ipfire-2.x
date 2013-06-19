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
# Copyright (C) 2013 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

function add_to_backup ()
{
	# Add path to ROOTFILES but remove old entries to prevent double
	# files in the tar
	grep -v "^$1" /opt/pakfire/tmp/ROOTFILES > /opt/pakfire/tmp/ROOTFILES.tmp
	mv /opt/pakfire/tmp/ROOTFILES.tmp /opt/pakfire/tmp/ROOTFILES
	echo $1 >> /opt/pakfire/tmp/ROOTFILES
}

#
# Remove old core updates from pakfire cache to save space...
core=70
for (( i=1; i<=$core; i++ ))
do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

#
# Do some sanity checks.
case $(uname -r) in
	*-ipfire-versatile )
		/usr/bin/logger -p syslog.emerg -t ipfire \
			"core-update-${core}: ERROR cannot update. versatile support is dropped."
		# Report no error to pakfire. So it does not try to install it again.
		exit 0
		;;
	*-ipfire-xen )
		BOOTSIZE=`df /boot -Pk | sed "s| * | |g" | cut -d" " -f2 | tail -n 1`
		if [ $BOOTSIZE -lt 28000 ]; then
			/usr/bin/logger -p syslog.emerg -t ipfire \
				"core-update-${core}: ERROR cannot update because not enough space on boot."
			exit 2
		fi
		;;
	*-ipfire* )
		# Ok.
		;;
	* )
		/usr/bin/logger -p syslog.emerg -t ipfire \
			"core-update-${core}: ERROR cannot update. No IPFire Kernel."
		# Report no error to pakfire. So it does not try to install it again.
		exit 0
	;;
esac


#
#
KVER="3.2.47"
MOUNT=`grep "kernel" /boot/grub/grub.conf 2>/dev/null | tail -n 1 `
# Nur den letzten Parameter verwenden
echo $MOUNT > /dev/null
MOUNT=$_
if [ ! $MOUNT == "rw" ]; then
	MOUNT="ro"
fi

#
# check if we the backup file already exist
if [ -e /var/ipfire/backup/core-upgrade${core}_$KVER.tar.xz ]; then
    echo Moving backup to backup-old ...
    mv -f /var/ipfire/backup/core-upgrade${core}_$KVER.tar.xz \
       /var/ipfire/backup/core-upgrade${core}_$KVER-old.tar.xz
fi
echo First we made a backup of all files that was inside of the
echo update archive. This may take a while ...
# Add some files that are not in the package to backup
add_to_backup lib/modules
add_to_backup boot
add_to_backup etc/sysconfig/lm_sensors
add_to_backup etc/sysconfig/rc.local

# Backup the files
tar cJvf /var/ipfire/backup/core-upgrade${core}_$KVER.tar.xz \
    -C / -T /opt/pakfire/tmp/ROOTFILES --exclude='#*' --exclude='/var/cache' > /dev/null 2>&1

# Check diskspace on root
ROOTSPACE=`df / -Pk | sed "s| * | |g" | cut -d" " -f4 | tail -n 1`

if [ $ROOTSPACE -lt 70000 ]; then
	/usr/bin/logger -p syslog.emerg -t ipfire \
		"core-update-${core}: ERROR cannot update because not enough free space on root."
	exit 2
fi

echo
echo Update Kernel to $KVER ...
#
# Remove old kernel, configs, initrd, modules ...
#
rm -rf /boot/System.map-*
rm -rf /boot/config-*
rm -rf /boot/ipfirerd-*
rm -rf /boot/vmlinuz-*
rm -rf /boot/uImage-ipfire-*
rm -rf /boot/uInit-ipfire-*
rm -rf /lib/modules

case $(uname -m) in
	i?86 )
		#
		# Backup grub.conf
		#
		cp -vf /boot/grub/grub.conf /boot/grub/grub.conf.org
	;;
esac

#
# Remove meta's of packages that are now common...
#
rm -rf /opt/pakfire/db/*/meta-freefont

#
#Stop services

#
#Extract files
tar xavf /opt/pakfire/tmp/files* --no-overwrite-dir -p --numeric-owner -C /

# Check diskspace on boot
BOOTSPACE=`df /boot -Pk | sed "s| * | |g" | cut -d" " -f4 | tail -n 1`

if [ $BOOTSPACE -lt 1000 ]; then
	case $(uname -r) in
		*-ipfire-kirkwood )
			# Special handling for old kirkwood images.
			# (install only kirkwood kernel)
			rm -rf /boot/*
			tar xavf /opt/pakfire/tmp/files* --no-overwrite-dir -p \
				--numeric-owner -C / --wildcards 'boot/*-kirkwood*'
			;;
		* )
			/usr/bin/logger -p syslog.emerg -t ipfire \
				"core-update-${core}: FATAL-ERROR space run out on boot. System is not bootable..."
			/etc/init.d/apache start
			exit 4
			;;
	esac
fi


#
#Start services

case $(uname -m) in
	i?86 )
		#
		# Modify grub.conf
		#
		echo
		echo Update grub configuration ...
		ROOT=`mount | grep " / " | cut -d" " -f1`

		if [ ! -z $ROOT ]; then
			ROOTUUID=`blkid -c /dev/null -sUUID $ROOT | cut -d'"' -f2`
		fi

		if [ ! -z $ROOTUUID ]; then
			sed -i "s|ROOT|UUID=$ROOTUUID|g" /boot/grub/grub.conf
		else
			sed -i "s|ROOT|$ROOT|g" /boot/grub/grub.conf
		fi
		sed -i "s|KVER|$KVER|g" /boot/grub/grub.conf
		sed -i "s|MOUNT|$MOUNT|g" /boot/grub/grub.conf

		if [ "$(grep "^serial" /boot/grub/grub.conf.org)" == "" ]; then
			echo "grub use default console ..."
		else
			echo "grub use serial console ..."
			sed -i -e "s|splashimage|#splashimage|g" /boot/grub/grub.conf
			sed -i -e "s|#serial|serial|g" /boot/grub/grub.conf
			sed -i -e "s|#terminal|terminal|g" /boot/grub/grub.conf
			sed -i -e "s| panic=10 | console=ttyS0,115200n8 panic=10 |g" /boot/grub/grub.conf
		fi

		#
		# ReInstall grub
		#
			echo "(hd0) ${ROOT::`expr length $ROOT`-1}" > /boot/grub/device.map
			grub-install --no-floppy ${ROOT::`expr length $ROOT`-1}
	;;
esac
#
# Delete old lm-sensor modullist to force search at next boot
#
rm -rf /etc/sysconfig/lm_sensors

#
#Update Language cache
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"

# Force (re)install pae kernel if pae is supported
rm -rf /opt/pakfire/db/*/meta-linux-pae
if [ ! "$(grep "^flags.* pae " /proc/cpuinfo)" == "" ]; then
	ROOTSPACE=`df / -Pk | sed "s| * | |g" | cut -d" " -f4 | tail -n 1`
	BOOTSPACE=`df /boot -Pk | sed "s| * | |g" | cut -d" " -f4 | tail -n 1`
	if [ $BOOTSPACE -lt 8000 -o $ROOTSPACE -lt 70000 ]; then
		/usr/bin/logger -p syslog.emerg -t ipfire \
			"core-update-${core}: WARNING not enough space for pae kernel."
	else
		rm -f /boot/grub/grub-backup-*-pae_install.conf
		echo "Name: linux-pae" > /opt/pakfire/db/installed/meta-linux-pae
		echo "ProgVersion: 3.2.46" >> /opt/pakfire/db/installed/meta-linux-pae
		echo "Release: 29"     >> /opt/pakfire/db/installed/meta-linux-pae
	fi
fi

# Force reinstall xen kernel if it was installed
if [ -e "/opt/pakfire/db/installed/meta-linux-xen" ]; then
	rm -f /boot/grub/grub-backup-*-xen.conf
	echo "Name: linux-xen" > /opt/pakfire/db/installed/meta-linux-xen
	echo "ProgVersion: 2.6.32.60" >> /opt/pakfire/db/installed/meta-linux-xen
	echo "Release: 26"     >> /opt/pakfire/db/installed/meta-linux-xen
fi

#
# After pakfire has ended run it again and update the lists and do upgrade
#
echo '#!/bin/bash'                                        >  /tmp/pak_update
echo 'while [ "$(ps -A | grep " update.sh")" != "" ]; do' >> /tmp/pak_update
echo '    sleep 1'                                        >> /tmp/pak_update
echo 'done'                                               >> /tmp/pak_update
echo 'while [ "$(ps -A | grep " pakfire")" != "" ]; do'   >> /tmp/pak_update
echo '    sleep 1'                                        >> /tmp/pak_update
echo 'done'                                               >> /tmp/pak_update
echo '/opt/pakfire/pakfire update -y --force'             >> /tmp/pak_update
echo '/opt/pakfire/pakfire upgrade -y'                    >> /tmp/pak_update
echo '/opt/pakfire/pakfire upgrade -y'                    >> /tmp/pak_update
echo '/opt/pakfire/pakfire upgrade -y'                    >> /tmp/pak_update
echo '/usr/bin/logger -p syslog.emerg -t ipfire "Core-upgrade finished. If you use a customized grub.cfg"' >> /tmp/pak_update
echo '/usr/bin/logger -p syslog.emerg -t ipfire "Check it before reboot !!!"' >> /tmp/pak_update
echo '/usr/bin/logger -p syslog.emerg -t ipfire " *** Please reboot... *** "' >> /tmp/pak_update
echo 'touch /var/run/need_reboot ' >> /tmp/pak_update
#
chmod +x /tmp/pak_update
/tmp/pak_update &


sync
# This update need a reboot...
#touch /var/run/need_reboot

#
#Finish
/etc/init.d/fireinfo start
sendprofile
#Don't report the exitcode last command
exit 0
