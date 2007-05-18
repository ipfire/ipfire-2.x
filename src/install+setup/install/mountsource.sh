#!/bin/sh

echo "Scanning source media"

# scan CDROM devices
for DEVICE in $(kudzu -qps -t 30 -c CDROM | grep device: | cut -d ' ' -f 2 | sort | uniq); do
    mount /dev/${DEVICE} /cdrom 2> /dev/null
    if [ -e /cdrom/ipfire-*.tbz2 ]; then
			echo -n ${DEVICE} > /tmp/source_device
			exit 0
    fi
    umount /cdrom 2> /dev/null
done

# scan HD device (usb sticks, etc.)
for DEVICE in $(kudzu -qps -t 30 -c HD | grep device: | cut -d ' ' -f 2 | sort | uniq); do
    mount /dev/${DEVICE}1 /cdrom 2> /dev/null
    if [ -e /cdrom/ipfire-*.tbz2 ]; then
			echo -n ${DEVICE}1 > /tmp/source_device
			exit 1
    fi
    umount /cdrom 2> /dev/null
done

exit 10
