############################################################################################
# Version 0.1a, Copyright (C) 2006  by IPFire.org						  #
# IPFire ist freie Software, die Sie unter bestimmten Bedingungen weitergeben dürfen.      #
############################################################################################

get_mirror() {

# Testen ob Server erreichbar ist
if ! $HOST_TEST $($URL_ZERL $H_MIRROR get_host) >/dev/null 2>&1
 then exit 1
fi

# Ins Verzeichnis wechseln
cd $HOME

# Überprüfen ob File schon vorhanden ist
if [ -e $HOME/$($URL_ZERL $H_MIRROR get_file) ]
 then rm $HOME/$($URL_ZERL $H_MIRROR get_file)
fi

# File herunterladen
if /usr/bin/wget -q $H_MIRROR >/dev/null 2>&1
 then 
  cd -
  exit 0
 else
  cd -
  exit 1
fi

}
################################### EOF ####################################################
