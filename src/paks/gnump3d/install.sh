#!/bin/bash
. /opt/pakfire/lib/functions.sh

extract_files

start_service --background ${NAME}

ln -svf  ../init.d/gnump3d /etc/rc.d/rc0.d/K00gnump3d
ln -svf  ../init.d/gnump3d /etc/rc.d/rc3.d/S99gnump3d
ln -svf  ../init.d/gnump3d /etc/rc.d/rc6.d/K00gnump3d
