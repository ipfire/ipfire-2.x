#!/bin/bash
. /opt/pakfire/lib/functions.sh

stop_service ${NAME}

rm -rf /etc/rc.d/rc*.d/*gnump3d
