#!/bin/bash
########################################################
##							      ##
## Make packages					      ##
##  							      ##
## (c) www.ipfire.org - GPL	v2			      ##
## 							      ##
########################################################
echo "`date -u '+%b %e %T'`: Packing $1" | tee -a $LOGFILE
cd / && mkdir -p /paks/$1/ROOT

## Copy install.sh/uninstall.sh to pak-dir and make executeable
#
cp -f /usr/src/src/paks/$1/{,un}install.sh /paks/$1
chmod 755 /paks/$1/{,un}install.sh

# This tar+untar+tar is for removing files compressed twice
tar -c -C / --files-from=/usr/src/src/paks/$1/ROOTFILES -f /paks/$1/filestmp.tar --exclude='#*'
tar -x -C /paks/$1/ROOT -f /paks/$1/filestmp.tar
rm -f /paks/$1/filestmp.tar
cd /paks/$1/ROOT && tar zcf /paks/$1/files.tgz *

cd /paks/$1 && tar cvfz ../$2.tar.gz files.tgz install.sh uninstall.sh
cd .. && md5sum $2.tar.gz > $2.tar.gz.md5

rm -fr /paks/$1

exit 0