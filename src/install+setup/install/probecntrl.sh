#!/bin/sh

echo "Probing for storage controllers"
for MODULE in $(hwinfo --usb --usb-ctrl --storage-ctrl | grep modprobe | awk '{ print $5 }' | tr -d \" | sort | uniq); do
    if [ "${MODULE}" = "piix" ]; then
        continue
    fi
    if grep -Eqe "^${MODULE} " /proc/modules; then
        MODULES="${MODULES} --with=${MODULE}"
        echo "Found: ${MODULE}"
    fi
done

if [ -z "${MODULES}" ]; then
	exit 1
else
	echo "${MODULES}" > /tmp/cntrldriver
	exit 0
fi
