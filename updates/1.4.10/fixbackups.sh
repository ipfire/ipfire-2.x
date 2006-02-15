#!/bin/sh

# fix for 1.4.9 web backup

function fix_backup() {
	/bin/gunzip -d -f $backup
	path=${backup%/*}

	# remove files wich should not have been include starting from 1.4.9
	# --delete accept only one -T each time
	/bin/tar --delete --file=$path/$name.tar -T /var/ipcop/backup/exclude.system
	/bin/tar --delete --file=$path/$name.tar -T /var/ipcop/backup/exclude.user
	# add missing hardware settings since v1.4.0
	/bin/tar --append --file=$path/$name.tar -C / -T /var/ipcop/backup/exclude.hardware

	#create backup again
	/bin/gzip $path/$name.tar
	# create encrypted backup again
	/usr/bin/openssl des3 -e -salt -in $backup -out $path/$name.dat -kfile /var/ipcop/backup/backup.key
	/bin/chown 99:99 $backup
	/bin/chown 99:99 $path/$name.dat
}

name=`hostname`

backups="`/usr/bin/find /var/ipcop/backup/sets -name $name.tar.gz`"
if [ $backup !='' ]; then
	for backup in $backups; do
		fix_backup $backup
	done
fi

backup="/home/httpd/html/backup/$name.tar.gz"
if [ -s $backup ]; then
	fix_backup $backup
fi
