#!/bin/bash
############################################################################################
# Version 0.1a, Copyright (C) 2006  by IPFire.org						  #
# IPFire ist freie Software, die Sie unter bestimmten Bedingungen weitergeben dürfen.      #
############################################################################################

get_list () {

PURL=`cat ${CACHE_DIR}$SERVERS_LIST`

if [ "$PURL" ]; then
  url=$(. $HOST_TEST "$PURL")
  if [ -n $url ]
   then URL=${url}
  fi
else
  echo "No server-address available. Exiting..."
  exit 1
fi

if [ -z $URL ]
 then pakfire_logger "Cannot find a working mirror."
  return 1
fi

cd $PAKHOME/cache

if [ -f $PACKAGE_LIST ]
 then rm $PACKAGE_LIST
fi

if /usr/bin/wget $URL/$PACKAGE_LIST > /dev/null 2>&1
 then
  cd -
  pakfire_logger "Updateliste heruntergeladen von $URL"
  return 0
 else
  cd -
  pakfire_logger "Updateliste konnnte nicht heruntergeladen werden von $URL"
  return 1
fi

}

################################### EOF ####################################################
