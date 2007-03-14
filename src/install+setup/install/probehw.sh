#!/bin/sh

echo "Detecting Hardware"
for MODULE in $(hwinfo --all | grep modprobe | awk '{ print $5 }' | tr -d \" | sort | uniq); do
    if [ "${MODULE}" = "unknown" ] || \
        [ "${MODULE}" = "ignore" ]; then
        continue
    fi
    if grep -Eqe "^${MODULE} " /proc/modules; then
        continue
    fi
    echo "Loading ${MODULE}"
    modprobe -k ${MODULE}
    udevstart
done

exit 0
