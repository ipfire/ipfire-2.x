#!/bin/bash
############################################################################################
# Version 0.1a, Copyright (C) 2006  by IPFire.org						  #
# IPFire ist freie Software, die Sie unter bestimmten Bedingungen weitergeben dürfen.      #
############################################################################################

get_pak() {

# Alle URLs durcharbeiten bis erste per ping erreichbar erreichbar
URL=$(. $HOST_TEST "$PURL")

# Falls URL nicht gesetzt wurde abbruch des Scripts
if [ -z $URL ]
 then pakfire_logger "Kann keinen Patchserver finden"
  exit 1
fi

# Verzeichnis in Zielverzeichnis wechseln für Download
cd $CACHE_DIR

. $DB_DIR/$1

FILE="$1-${VER}_${IPFVER}.tar.gz"

# Paket Downloaden
if /usr/bin/wget $URL/packages/$FILE{,.md5} >> $LOG 2>&1
 then
  cd -
  exit 0
 else
  cd -
  pakfire_logger "Cannot download $URL/packages/$FILE"
  exit 1
fi

}

################################### EOF ####################################################
