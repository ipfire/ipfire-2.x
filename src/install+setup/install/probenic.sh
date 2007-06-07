#!/bin/sh

case "$1" in
	install)
		kudzu -qps -c NETWORK | egrep "desc|network.hwaddr|driver" > /tmp/scanned_nics 2>/dev/null
			;;
	"")
		kudzu -qps -c NETWORK | egrep "desc|network.hwaddr|driver" > /var/ipfire/ethernet/scanned_nics 2>/dev/null
			;;
esac
exit 0
