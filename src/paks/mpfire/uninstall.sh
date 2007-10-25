#!/bin/bash
. /opt/pakfire/lib/functions.sh

stop_service ${NAME}
make_backup ${NAME}
rm /etc/rc.d/rc3.d/S65mpd
rm /etc/rc.d/rc0.d/K35mpd
rm /etc/rc.d/rc6.d/K35mpd
rm /etc/init.d/mpd
rm /var/ipfire/mpfire/mpd.conf
rm /etc/mpd.conf
rm /var/log/mpd.error.log
rm /var/log/mpd.log

