#!/bin/bash
. /opt/pakfire/lib/functions.sh

extract_files

sleep 300 && /etc/init.d/cups start &

ln -svf ../init.d/cups /etc/rc.d/rc0.d/K00cups
ln -svf ../init.d/cups /etc/rc.d/rc3.d/S25cups
ln -svf ../init.d/cups /etc/rc.d/rc6.d/K00cups
