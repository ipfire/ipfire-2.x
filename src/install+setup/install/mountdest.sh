#!/bin/sh

echo "Scanning for possible destination drives"

# scan IDE devices
echo "--> IDE"
for DEVICE in $(kudzu -qps -t 30 -c HD -b IDE | grep device: | cut -d ' ' -f 2 | sort | uniq); do
		mount /dev/${DEVICE}1 /harddisk 2> /dev/null
		if [ -n "$(ls /harddisk/ipfire-*.tbz2 2>/dev/null)" ]; then
			umount /harddisk 2> /dev/null
			echo "${DEVICE} is source drive - SKIP"
			continue
		else
			umount /harddisk 2> /dev/null
			echo -n "$DEVICE" > /tmp/dest_device
			echo "${DEVICE} - yes, it is our destination"
			exit 0
		fi
done

# scan USB/SCSI devices
echo "--> USB/SCSI"
for DEVICE in $(kudzu -qps -t 30 -c HD -b SCSI | grep device: | cut -d ' ' -f 2 | sort | uniq); do
		mount /dev/${DEVICE}1 /harddisk 2> /dev/null
		if [ -n "$(ls /harddisk/ipfire-*.tbz2 2>/dev/null)" ]; then
			umount /harddisk 2> /dev/null
			echo "${DEVICE} is source drive - SKIP"
			continue
		else
			umount /harddisk 2> /dev/null
			echo -n "$DEVICE" > /tmp/dest_device
			echo "${DEVICE} - yes, it is our destination"
			exit 1
		fi
done

# scan RAID devices
echo "--> RAID"
for DEVICE in $(kudzu -qps -t 30 -c HD -b RAID | grep device: | cut -d ' ' -f 2 | sort | uniq); do
		mount /dev/${DEVICE}p1 /harddisk 2> /dev/null
		if [ -n "$(ls /harddisk/ipfire-*.tbz2 2>/dev/null)" ]; then
			umount /harddisk 2> /dev/null
			echo "${DEVICE} is source drive - SKIP"
			continue
		else
			umount /harddisk 2> /dev/null
			echo -n "$DEVICE" > /tmp/dest_device
			echo "${DEVICE} - yes, it is our destination"
			exit 2
		fi
done

exit 10 # Nothing found
