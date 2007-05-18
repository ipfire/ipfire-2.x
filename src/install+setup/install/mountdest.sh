#!/bin/sh

echo "Scanning for possible destination drives"

# scan IDE devices
echo "--> IDE"
for DEVICE in $(kudzu -qps -t 30 -c HD -b IDE | grep device: | cut -d ' ' -f 2 | sort | uniq); do
		echo -n "---> $DEVICE"
    mount /dev/${DEVICE}1 /harddisk 2> /dev/null
    if [ -e /harddisk/ipfire-*.tbz2 ]; then
			umount /harddisk 2> /dev/null
			echo " is source drive"
			continue
    else
    	umount /harddisk 2> /dev/null
    	echo -n "$DEVICE" > /tmp/dest_device
    	echo " - yes, it is our destination"
    	exit 0
		fi
done

# scan USB/SCSI devices
echo "--> USB/SCSI"
for DEVICE in $(kudzu -qps -t 30 -c HD -b SCSI | grep device: | cut -d ' ' -f 2 | sort | uniq); do
    echo -n "---> $DEVICE"
		mount /dev/${DEVICE}1 /harddisk 2> /dev/null
    if [ -e /harddisk/ipfire-*.tbz2 ]; then
			umount /harddisk 2> /dev/null
			echo " is source drive"
			continue
    else
    	umount /harddisk 2> /dev/null
    	echo -n "$DEVICE" > /tmp/dest_device
    	echo " - yes, it is our destination"
    	exit 1
		fi
done

exit 10 # Nothing found
