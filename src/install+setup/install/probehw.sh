#!/bin/sh

echo "Detecting Hardware"
for MODULE in $(kudzu -qps  -t 30 | grep driver | cut -d ' ' -f 2 | sort | uniq); do
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
