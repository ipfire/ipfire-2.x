#!/bin/sh

case "$1" in
	install)
		kudzu -qps -c NETWORK | egrep "desc|network.hwaddr|driver" | \
				awk -F": " '{ print $2";" }' | sed -e '/..:..:..:..:..:..;/a\X' | \
				tr "\n" "X" | sed -e 's/XXX/\n/g' -e 's/;X/;/g' | \
				sort > /tmp/scanned_nics 2>/dev/null
			;;
	"")
		if [ ! -e /var/ipfire/ethernet/scan_lock ]; then
			kudzu -qps -c NETWORK | egrep "desc|network.hwaddr|driver" | \
				awk -F": " '{ print $2";" }' | sed -e '/..:..:..:..:..:..;/a\X' | \
				tr "\n" "X" | sed -e "s/XXX/\n/g" -e 's/;X/;/g' | \
				sort > /var/ipfire/ethernet/scanned_nics 2>/dev/null
		fi
			;;
esac
exit 0
