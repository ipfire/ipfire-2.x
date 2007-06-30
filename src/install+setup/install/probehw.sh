#!/bin/sh

echo "Detecting Hardware..."
for MODULE in $(kudzu -qps  -t 30 | grep driver: | cut -d ' ' -f 2 | sort | uniq); do
    if [ "${MODULE}" = "unknown" ] || \
        [ "${MODULE}" = "ignore" ]; then
        continue
    fi
    if grep -Eqe "^${MODULE} " /proc/modules; then
        continue
    fi
    echo -n "Loading ${MODULE}"
    modprobe ${MODULE} >/dev/null 2>&1
		echo " --> ecode: $?"
done

sleep 10

if [ $# -eq 0 ]; then
	exit 0
fi

## If the autodetection fails we will try to load every module...
## Do this only when we want...

for i in a b c d e f g; do
	if [ ! -e /dev/sd$i ]; then
		DEVICE="/dev/sd$i"
		echo "Checking for: $DEVICE"
		break
	fi
done

for MODULE in $(ls /lib/modules/*/kernel/drivers/scsi); do
	MODULE=`basename $MODULE | awk -F. '{ print $1 }'`
	
	echo -n "Probing for $MODULE"
	modprobe $MODULE >/dev/null 2>&1
	RETVAL=$?
	echo " --> ecode: $RETVAL"
	if [ "$RETVAL" -eq "0" ]; then
		sleep 3
		if [ -e "$DEVICE" ]; then
			break
		fi
	fi

done

sleep 5

exit 0
