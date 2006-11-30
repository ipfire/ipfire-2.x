#!/bin/sh

MODULES=$(/bin/kudzu -qps  -t 30 -c NETWORK | grep driver | cut -d ' ' -f 2 | sort)

if [ "$1" == "count" ]; then
	echo $(echo $MODULES | wc -l)
else
	NUMBER=$1
fi

if [ "$NUMBER" ]; then
	echo "$(echo $MODULES | grep -n $NUMBER | cut -c 1-2 )" > /nicdriver
else
	echo "$MODULES" > /nicdriver
fi
