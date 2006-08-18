#!/bin/bash
############################################################################################
# Version 0.1a, Copyright (C) 2006  by IPFire.org						  #
# IPFire ist freie Software, die Sie unter bestimmten Bedingungen weitergeben dürfen.      #
############################################################################################

get_list () {

# Alle URLs durcharbeiten bis erste per ping erreichbar erreichbar
url=$(. $HOST_TEST "$PURL")
if [ -n $url ]
 then URL=${url}
fi

# Falls URL nicht gesetzt wurde abbruch des Scripts
if [ -z $URL ]
 then pakfire_logger "Kann keinen Listenserver finden."
  return 1
fi

# Verzeichnis in Zielverzeichnis wechseln für Download
cd $PAKHOME/cache

# Pruefen ob bereits ein File vorhanden ist - falls ja, dann wird sie nun gelöscht
if [ -f $PACKAGE_LIST ]
 then rm $PACKAGE_LIST
fi

# Download der Liste
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
