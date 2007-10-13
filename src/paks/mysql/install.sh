#!/bin/bash
. /opt/pakfire/lib/functions.sh

extract_files

ln -svf  ../init.d/mysql /etc/rc.d/rc0.d/K26mysql
ln -svf  ../init.d/mysql /etc/rc.d/rc3.d/S34mysql
ln -svf  ../init.d/mysql /etc/rc.d/rc6.d/K26mysql

/etc/init.d/mysql start

sleep 10

mysqladmin -u root --password='' password 'mysqlfire'
