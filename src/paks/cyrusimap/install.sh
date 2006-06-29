#!/bin/bash
#
#################################################################
#                                                               #
# This file belongs to IPFire Firewall - GPLv2 - www.ipfire.org #
#                                                               #
#################################################################
#
CONFIGDIR=/var/ipfire/cyrusimap
#
# Extract the files
tar xfz files.tgz -C /
cp -f ROOTFILES /opt/pakfire/installed/ROOTFILES.$2



if [ ! -f $CONFIGDIR/server.pm ]; then
	cd /tmp && openssl req -new -nodes -out req.pem -keyout key.pem
	cd /tmp && openssl rsa -in key.pem -out new.key.pem
	cd /tmp && openssl x509 -in req.pem -out ca-cert -req -signkey new.key.pem -days 999
	
	cd /tmp && cp new.key.pem $CONFIGDIR/server.pem
	cd /tmp && rm new.key.pem
	cd /tmp && cat ca-cert >> $CONFIGDIR/server.pem
	chown cyrus:mail $CONFIGDIR/server.pem
	chmod 600 $CONFIGDIR/server.pem # Your key should be protected
fi
