#!/bin/bash
############################################################################################
# Version 0.1a, Copyright (C) 2006  Peter Schaelchli Für IPFire besteht KEINERLEI GARANTIE;#
# IPFire ist freie Software, die Sie unter bestimmten Bedingungen weitergeben dürfen;      #
############################################################################################

# Conf File festlegen
CONF_File=/opt/pakfire/pakfire.conf

if [ -r $CONF_File ]
then 
 STRI=$(grep $1 $CONF_File)
 STRI=${STRI#*=}
fi

if [ -z $2 ]
 then echo "$STRI"
 else cat $STRI
fi

################################### EOF ####################################################
