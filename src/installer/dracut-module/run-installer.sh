#!/bin/sh
#
# IPFire Installer RC
#

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
	0)
		# The installer has finished without a problem.
		;;
	*)
		echo "The installer has crashed. You will be dropped to a debugging shell"
		/bin/bash --login
		;;
esac

# Reboot the system
/shutdown reboot
