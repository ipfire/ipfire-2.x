############################################################################################
# Version 0.1a, Copyright (C) 2006  by IPFire.org						  #
# IPFire ist freie Software, die Sie unter bestimmten Bedingungen weitergeben dürfen.      #
############################################################################################

get_mirror() {

cd $PAKHOME/cache

#if [ -e $PAKHOME/cache/$SERVERS_LIST ]
# then rm -f $PAKHOME/cache/$SERVERS_LIST
#fi

if /usr/bin/wget $H_MIRROR >$LOG 2>&1
 then
  pakfire_logger "Got servers!"
  cd -
  return 0
 else
  pakfire_logger "Got no servers!"
  cd -
  return 1
fi

}
################################### EOF ####################################################
