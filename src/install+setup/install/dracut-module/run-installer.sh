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

sleep 60

# Reboot the system
/shutdown reboot
