############################################################################################
# Version 0.1a, Copyright (C) 2006  by IPFire.org						  #
# IPFire ist freie Software, die Sie unter bestimmten Bedingungen weitergeben dürfen.      #
############################################################################################

get_mirror() {

# Testen, ob der Server erreichbar ist
#if ! $HOST_TEST $($PAKHOME/lib/url_zerl.sh $H_MIRROR get_host) >/dev/null 2>&1
# then return 1
#fi

# Ins Cache-Verzeichnis wechseln
cd $PAKHOME/cache

# Überprüfen ob File schon vorhanden ist
if [ -e $PAKHOME/cache/$SERVERS_LIST ]
 then rm -f $PAKHOME/cache/$SERVERS_LIST
fi

# File herunterladen
if /usr/bin/wget -q $H_MIRROR >/dev/null 2>&1
 then
  COUNT=0
  for i in `cat $SERVERS_LIST`; do
    COUNT=$(($COUNT+1))
  done
  #. $PAKHOME/lib/test_host.sh `cat $SERVERS_LIST`
  cd -
  return 0
 else
  cd -
  return 1
fi

}
################################### EOF ####################################################
