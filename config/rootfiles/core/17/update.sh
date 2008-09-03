#!/bin/bash
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1
/etc/init.d/squid stop
extract_files
/etc/init.d/squid start
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
perl -e "/var/ipfire/qos/bin/migrate.pl"
