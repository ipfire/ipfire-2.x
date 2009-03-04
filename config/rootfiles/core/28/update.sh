#!/bin/bash
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1
#perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
/etc/init.d/snort restart