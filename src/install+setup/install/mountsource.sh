#!/bin/sh

echo "Scanning source media"

# scan CDROM devices

for DEVICE in $(hwinfo --cdrom | grep "Device File" | awk -F: '{ print $2 }' | cut -c 7- | sort | uniq); do
    mount /dev/${DEVICE} /cdrom 2> /dev/null
    if [ -e /cdrom/boot ]; then
	echo -n ${DEVICE} > /tmp/source_device
	exit 0
    fi
    umount /cdrom 2> /dev/null
done

# scan HD device (usb sticks, etc.)
for DEVICE in $(hwinfo --usb --disk | grep "Device File" | awk -F: '{ print $2 }' | cut -c 7- | sort | uniq); do
    mount /dev/${DEVICE}1 /cdrom 2> /dev/null
    if [ -e /cdrom/boot ]; then
	echo -n ${DEVICE}1 > /tmp/source_device
	exit 1
    fi
    umount /cdrom 2> /dev/null
done

exit 10
