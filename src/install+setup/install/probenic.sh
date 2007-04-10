#!/bin/sh

case "$1" in
	install)
		hwinfo --netcard | egrep "Model|HW Address" | \
			awk -F": " '{ print $2 }' | sed -e '/..:..:..:..:..:../a\\' | sed -e "s/$/\;/g" | \
			tr "\n" "XX" | sed -e "s/XX/\n/g" | sed -e "s/\;X/\;/g" | \
			sort > /tmp/scanned_nics 2>/dev/null
			;;
	"")
		if [ ! -e /var/ipfire/ethernet/scan_lock ]; then
			hwinfo --netcard | egrep "Model|HW Address" | \
				awk -F": " '{ print $2 }' | sed -e '/..:..:..:..:..:../a\\' -e "s/$/\;/g" | \
				tr "\n" "XX" | sed -e "s/XX/\n/g" -e "s/\;X/\;/g" | \
				sort > /var/ipfire/ethernet/scanned_nics 2>/dev/null
		fi
			;;
esac
exit 0
