#!/bin/bash
. /opt/pakfire/lib/functions.sh
extract_files
depmod -a
/usr/local/bin/backupctrl exclude >/dev/null 2>&1
