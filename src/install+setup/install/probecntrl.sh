#!/bin/sh

echo "Probing for SCSI controllers"
MODULE=`/bin/kudzu -qps  -t 30 -c SCSI | grep driver | cut -d ' ' -f 2 | sort | uniq`

if [ "$?" == "0" ]; then
	echo $MODULE > /cntrldriver;
	echo "Your controller is: $MODULE"
	exit 0
fi

echo "No SCSI controller found"
exit 1
