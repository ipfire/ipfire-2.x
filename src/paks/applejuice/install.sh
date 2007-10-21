#!/bin/bash
. /opt/pakfire/lib/functions.sh

extract_files

sleep 60 && /etc/init.d/applejuice start &

ln -svf ../init.d/applejuice /etc/rc.d/rc0.d/K05applejuice
ln -svf ../init.d/applejuice /etc/rc.d/rc3.d/S98applejuice
ln -svf ../init.d/applejuice /etc/rc.d/rc6.d/K05applejuice

/etc/init.d/apache reload 
