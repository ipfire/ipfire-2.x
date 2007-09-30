#!/bin/bash
. /opt/pakfire/lib/functions.sh

extract_files

ln -sf  ../init.d/cyrus-sasl /etc/rc.d/rc0.d/K49cyrus-sasl
ln -sf  ../init.d/cyrus-sasl /etc/rc.d/rc3.d/S24cyrus-sasl
ln -sf  ../init.d/cyrus-sasl /etc/rc.d/rc6.d/K49cyrus-sasl

/etc/init.d/cyrus-sasl start
