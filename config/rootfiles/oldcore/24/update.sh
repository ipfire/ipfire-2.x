#!/bin/bash
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1
extract_files
#perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
