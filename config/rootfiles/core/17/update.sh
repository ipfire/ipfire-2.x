#!/bin/bash
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1
/etc/init.d/squid stop
/etc/init.d/collectd stop
extract_files
/etc/init.d/squid start
/etc/init.d/collectd start
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
perl /var/ipfire/qos/bin/migrate.pl
/var/ipfire/updatexlrator/bin/convert
