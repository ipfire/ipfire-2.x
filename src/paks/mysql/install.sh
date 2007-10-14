#!/bin/bash
. /opt/pakfire/lib/functions.sh

extract_files

ln -svf  ../init.d/mysql /etc/rc.d/rc0.d/K26mysql
ln -svf  ../init.d/mysql /etc/rc.d/rc3.d/S34mysql
ln -svf  ../init.d/mysql /etc/rc.d/rc6.d/K26mysql

/etc/init.d/mysql start

COUNTER=0

while [ "$COUNTER" -lt "10" ]; do
	[ -e "/var/run/mysql/mysql.sock" ] && break
	echo "MySQL server is still not running. Waiting 5 seconds."
	sleep 5
	(( $COUNTER += 1 ))
done 

[ -e "/var/run/mysql/mysql.sock" ] || (echo "MySQL still noch running... Exiting."; \
	exit 1)

mysqladmin -u root --password='' password 'mysqlfire'
