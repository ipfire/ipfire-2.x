#!/bin/bash
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1
extract_files
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
grep -v 'Interface "ppp"' /etc/collectd.conf > /tmp/collectd.conf
mv /tmp/collectd.conf /etc/collectd.conf
/etc/init.d/collectd restart
/etc/init.d/mISDN config
