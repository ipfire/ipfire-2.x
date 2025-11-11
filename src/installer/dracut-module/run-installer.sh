#!/bin/sh
#
# IPFire Installer RC
#

# Enable UTF-8 mode for the console before the installer starts
export LC_ALL="en_US.utf-8"

# wait for udev settle
/bin/udevadm settle

unattended=0
if grep -q "installer.unattended" /proc/cmdline; then
	unattended=1
fi

# Mount efivarfs on EFI systems
if [ -d "/sys/firmware/efi" ]; then
	mount -t efivarfs efivarfs /sys/firmware/efi/efivars
fi

# Silence the kernel
echo >/proc/sys/kernel/printk "1 4 1 7"
echo -n -e "\033[9;0]"

echo "Starting shells on tty2 and tty3 ..."
/usr/local/bin/iowrap /dev/tty2 /bin/bash &
/usr/local/bin/iowrap /dev/tty3 /bin/bash &

echo "Loading Installer..."
/bin/bash --login -c "/usr/bin/installer /dev/tty2"
ret=$?

case "${ret}" in
	139)
		echo "The installer has crashed. You will be dropped to a debugging shell"
		/bin/bash --login
		;;
esac

# Poweroff after an unattended installation
if [ "${unattended}" = "1" ]; then
	/shutdown poweroff
fi

# Reboot the system
/shutdown reboot
