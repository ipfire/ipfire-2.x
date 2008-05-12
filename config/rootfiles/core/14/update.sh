#!/bin/bash
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1
rm /lib/modules/2.6.16.57-ipfire/kernel/drivers/media/video/video-buf.ko
rm /lib/modules/2.6.16.57-ipfire/kernel/drivers/media/dvb/frontends/dib3000-common.ko
rm /lib/modules/2.6.16.57-ipfire-smp/kernel/drivers/media/video/video-buf.ko
rm /lib/modules/2.6.16.57-ipfire-smp/kernel/drivers/media/dvb/frontends/dib3000-common.ko
/etc/init.d/squid stop
extract_files
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
/etc/init.d/squid start
depmod -a 2.6.16.57-ipfire
depmod -a 2.6.16.57-ipfire-smp
