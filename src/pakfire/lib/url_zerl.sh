#!/bin/bash
############################################################################################
# Version 0.1a, Copyright (C) 2006  Peter Schaelchli Für IPFire besteht KEINERLEI GARANTIE;#
# IPFire ist freie Software, die Sie unter bestimmten Bedingungen weitergeben dürfen;      #
############################################################################################

protokoll=${1%%:*}

rest=${1#*'//'}

if grep @ <<EOF >/dev/null
$rest
EOF
then
# User heraus suchen
user=${rest%%:*}
rest=${rest#*:}
pass=${rest%%@*}
rest=${rest#*@}
fi

host=${rest%%/*}
rest=${rest#*/}

if grep / <<EOF >/dev/null
$rest
EOF
then
dir=${rest%/*}
rest=${rest##*/}
fi

file=$rest

case "$2" in
	get_proto)
		echo $protokoll
		;;
	get_user)
		echo $user
		;;
	get_pass)
		echo $pass
		;;
	get_host)
		echo $host
		;;
	get_dir)
		echo $dir
		;;
	get_file)
		echo $file
		;;
	*) exit 1
esac

################################### EOF ####################################################
