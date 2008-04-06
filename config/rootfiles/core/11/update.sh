#!/bin/bash
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1
/etc/init.d/squid stop
extract_files
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
squidGuard -d -C all
chmod 666 /var/ipfire/urlfilter/blacklists/*/*.db
/etc/init.d/squid start
