#!/bin/bash
. /opt/pakfire/lib/functions.sh
mv /etc/sysconfig/rc.local /etc/sysconfig/rc.local.old
extract_files
if [ -e "/var/ipfire/qos/enable" ]; then
 /usr/local/bin/qosctrl stop
 /usr/local/bin/qosctrl generate
 /usr/local/bin/qosctrl start
fi
/usr/local/bin/outgoingfwctrl restart
