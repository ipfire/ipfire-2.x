#!/bin/sh

hwinfo --netcard | egrep "Model|HW Address" | \
		awk -F": " '{ print $2 }' | sed -e '/..:..:..:..:..:../a\\' -e "s/$/\;/g" | \
		tr "\n" "XX" | sed -e "s/XX/\n/g" -e "s/\;X/\;/g" | \
		sort > /var/ipfire/ethernet/scanned_nics 2>/dev/null
