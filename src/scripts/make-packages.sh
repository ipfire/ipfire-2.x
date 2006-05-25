#!/bin/bash
########################################################
##							      ##
## Make packages					      ##
##  							      ##
## (c) www.ipfire.org - GPL	v2			      ##
## 							      ##
########################################################
echo "`date -u '+%b %e %T'`: Packing $1" | tee -a $LOGFILE
cd / && mkdir -p /paks/$1

## Copy install.sh/uninstall.sh to pak-dir and make executeable
#
cp -f /usr/src/src/paks/$1/{,un}install.sh /paks/$1
chmod 755 /paks/$1/{,un}install.sh

tar cvfz /paks/$1/files.tgz --files=/usr/src/src/paks/$1/ROOTFILES --exclude='#*'

tar cvfz /paks/$1/conf.tgz  --files=/usr/src/src/paks/$1/CONFFILES --exclude='#*'

cd /paks/$1 && tar cvfz ../$2.tar.gz files.tgz conf.tgz install.sh uninstall.sh
cd .. && md5sum $2.tar.gz >> $2.tar.gz.md5

rm -fr /paks/$1

exit 0