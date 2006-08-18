#!/bin/bash
############################################################################################
# Version 0.1a, Copyright (C) 2006  by IPFire.org						  #
# IPFire ist freie Software, die Sie unter bestimmten Bedingungen weitergeben dürfen.      #
############################################################################################

get_upgrade() {

updates=""

for list in $(find $IP_DIR -type f -name "*")
do
 list=$(basename $list)
 . $IP_DIR/$list
 OLD_VER=$VER
 OLD_IPFVER=$IPFVER

 VER=""
 IPFVER=""
 . $DB_DIR/$list

 if [ "$OLD_IPFVER" -lt "$IPFVER" ]; then
  updates="$list $updates"
 fi

done

for i in $updates
do
 pakfire_logger "New version of $i available."
done
}

################################### EOF ####################################################
