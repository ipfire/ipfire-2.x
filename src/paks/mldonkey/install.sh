#!/bin/bash
. /opt/pakfire/lib/functions.sh

extract_files

/etc/init.d/mldonkey start

ln -svf ../init.d/mldonkey /etc/rc.d/rc0.d/K05mldonkey
ln -svf ../init.d/mldonkey /etc/rc.d/rc3.d/S98mldonkey
ln -svf ../init.d/mldonkey /etc/rc.d/rc6.d/K05mldonkey
