#!/bin/bash
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1
rm /lib/modules/2.6.16.57-ipfire/kernel/drivers/media/video/video-buf.ko
rm /lib/modules/2.6.16.57-ipfire-smp/kernel/drivers/media/video/video-buf.ko
extract_files
depmod -a 2.6.16.57-ipfire
depmod -a 2.6.16.57-ipfire-smp

