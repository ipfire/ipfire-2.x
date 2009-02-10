#!/bin/bash
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1
extract_files
[ -e /var/ipfire/qos/enable ] && qosctrl stop
qosctrl generate
[ -e /var/ipfire/qos/enable ] && qosctrl start
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
sysctl -p
/etc/init.d/squid restart
