#!/bin/bash
. /opt/pakfire/lib/functions.sh
extract_files
depmod -a
echo "DROPWIRELESSFORWARD=on" >> /var/ipfire/optionsfw/settings
echo "DROPWIRELESSINPUT=on" >> /var/ipfire/optionsfw/settings
/usr/local/bin/backupctrl exclude >/dev/null 2>&1
