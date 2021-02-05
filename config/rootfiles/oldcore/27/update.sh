#!/bin/bash
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1
/etc/init.d/squid stop
extract_files
[ -e /var/ipfire/qos/enable ] && /usr/local/bin/qosctrl stop
/usr/local/bin/qosctrl generate
[ -e /var/ipfire/qos/enable ] && /usr/local/bin/qosctrl start
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
sysctl -p
mv /etc/squid/cachemgr.conf /var/ipfire/proxy/cachemgr.conf
ln -sf /var/ipfire/proxy/cachemgr.conf /etc/squid/cachemgr.conf
chown nobody.nobody /var/ipfire/proxy/cachemgr.conf
/etc/init.d/squid start
