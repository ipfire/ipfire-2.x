#!/bin/bash
. /opt/pakfire/lib/functions.sh
extract_files
ln -s /etc/rc.d/rc0.d/K50collectd /etc/init.d/collectd
ln -s /etc/rc.d/rc3.d/S20collectd /etc/init.d/collectd
ln -s /etc/rc.d/rc6.d/K50collectd /etc/init.d/collectd
