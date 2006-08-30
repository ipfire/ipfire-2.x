#!/bin/bash
############################################################################################
# Version 0.1a, Copyright (C) 2006  by IPFire.org						  #
# IPFire ist freie Software, die Sie unter bestimmten Bedingungen weitergeben dürfen.      #
############################################################################################

get_pak() {

URL=$(. $HOST_TEST "$PURL")

if [ -z $URL ]
 then pakfire_logger "Cannot find a mirror."
  exit 1
fi

. $DB_DIR/$1

FILE="$1-${VER}_${IPFVER}.ipfire"

if [ ! -f $CACHE_DIR/$FILE ]; then
  cd /var/tmp
  pakfire_logger "Downloading $FILE from $URL..."
  if /usr/bin/wget $URL/packages/$FILE{,.md5} >> $LOG 2>&1
   then
      if [ "`md5sum $FILE`" = "`cat ${FILE}.md5`" ]; then
      mv -f /var/tmp/$FILE{,.md5} $CACHE_DIR
      pakfire_logger "MD5 sum OK in $FILE!"
    else
      pakfire_logger "Wrong MD5 sum in $FILE."
      rm -f /var/tmp/$FILE{,.md5}
      exit 1
    fi
    cd -
   else
    cd -
    pakfire_logger "Cannot download $URL/packages/$FILE"
    exit 1
  fi
else
  pakfire_logger "No need to download $FILE."
fi

}

################################### EOF ####################################################
