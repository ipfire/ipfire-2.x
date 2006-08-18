#!/bin/bash
############################################################################################
# Version 0.1a, Copyright (C) 2006  by IPFire.org						  #
# IPFire ist freie Software, die Sie unter bestimmten Bedingungen weitergeben dürfen.      #
############################################################################################

get_base() {

. $IP_DIR/BASE

 OLD_VER=$VER

 VER=""
 . $DB_DIR/BASE

 if [ "$OLD_VER" -lt "$VER" ]; then
  pakfire_logger "There is one ore more updates for the base system!"
  for i in `seq $(($OLD_VER+1)) $VER`
   do
    $PAKHOME/pakfire install BASE-$i
   done
 fi

}

################################### EOF ####################################################
