#!/bin/bash
############################################################################################
# Version 0.1a, Copyright (C) 2006  by IPFire.org						  #
# IPFire ist freie Software, die Sie unter bestimmten Bedingungen weitergeben dürfen.      #
############################################################################################

install_pak() {

cd $CACHE_DIR

. $DB_DIR/$1
FILE="$1-${VER}_${IPFVER}.tar.gz"

pakfire_logger "Unpaking $FILE..."
mkdir $TMP_DIR/$1
tar xfz $CACHE_DIR/$FILE -C $TMP_DIR/$1

$PAKHOME/lib/resolv_deps.sh $TMP_DIR/$1/$DEPS

cd $TMP_DIR/$1
$TMP_DIR/$1/$INSTALL

cp -f ROOTFILES $IP_DIR/$1

}

################################### EOF ####################################################
