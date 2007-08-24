#!/bin/sh

echo "Scanning source media"

# scan CDROM devices
for DEVICE in $(kudzu -qps -t 30 -c CDROM | grep device: | cut -d ' ' -f 2 | sort | uniq); do
		mount /dev/${DEVICE} /cdrom 2> /dev/null
		if [ -n "$(ls /cdrom/ipfire-*.tbz2 2>/dev/null)" ]; then
			echo -n ${DEVICE} > /tmp/source_device
			echo "Found tarball on ${DEVICE}"
		else
			echo "Found no tarballs on ${DEVICE} - SKIP"
		fi
		umount /cdrom 2> /dev/null
done

# scan HD device (usb sticks, etc.)
for DEVICE in $(kudzu -qps -t 30 -c HD | grep device: | cut -d ' ' -f 2 | sort | uniq); do
		mount /dev/${DEVICE}1 /cdrom 2> /dev/null
		if [ -n "$(ls /cdrom/ipfire-*.tbz2 2>/dev/null)" ]; then
			echo -n ${DEVICE}1 > /tmp/source_device
			echo "Found tarball on ${DEVICE}"
		else
			umount /cdrom 2> /dev/null
			echo "Found no tarballs on ${DEVICE} - SKIP"
		fi
		umount /cdrom 2> /dev/null
done

if [ -e "/tmp/source_device" ]; then
	mount /dev/$(cat /tmp/source_device) /cdrom 2> /dev/null
	exit 0
else
	exit 10
fi
