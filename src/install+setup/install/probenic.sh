#!/bin/sh

NUMBER=$1
MODULES=`/bin/kudzu -qps  -t 30 -c NETWORK | grep driver | cut -d ' ' -f 2 | sort | uniq`

if [ "$NUMBER" ]; then
	NICS=`echo $MODULES | head -$NUMBER`
else
	NICS=$MODULES
fi

echo "$NICS" > /nicdriver
