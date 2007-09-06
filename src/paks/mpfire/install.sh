#!/bin/bash
. /opt/pakfire/lib/functions.sh

extract_files
chown nobody.nobody -Rv /var/ipfire/mpfire
ln -svf  ../init.d/mpd /etc/rc.d/rc3.d/S65mpd
ln -svf  ../init.d/mpd /etc/rc.d/rc0.d/K35mpd
ln -svf  ../init.d/mpd /etc/rc.d/rc6.d/K35mpd
touch /var/log/mpd.error.log
touch /var/log/mpd.log
