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

# This tar+untar+tar is for removing files compressed twice
tar cvf /paks/$1/filestmp.tar --files=/usr/src/src/paks/$1/ROOTFILES --exclude='#*'
tar cvf /paks/$1/conftmp.tar  --files=/usr/src/src/paks/$1/CONFFILES --exclude='#*'

mkdir -p /paks/$1/ROOT /paks/$1/CONF
tar xvf /paks/$1/filestmp.tar -C /paks/$1/ROOT
tar xvf /paks/$1/conftmp.tar -C /paks/$1/CONF
rm -f /paks/$1/{files,conf}tmp.tar
cd /paks/$1/ROOT && tar cvfz /paks/$1/files.tgz *
cd /paks/$1/CONF && tar cvfz /paks/$1/conf.tgz *

cd /paks/$1 && tar cvfz ../$2.tar.gz files.tgz conf.tgz install.sh uninstall.sh
cd .. && md5sum $2.tar.gz >> $2.tar.gz.md5

rm -fr /paks/$1

exit 0