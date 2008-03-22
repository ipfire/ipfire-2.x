#!/bin/bash
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1
/etc/init.d/squid stop
extract_files
squidGuard -d -C all
chmod 666 /var/ipfire/urlfilter/blacklist/*/*.db
/etc/init.d/squid start
