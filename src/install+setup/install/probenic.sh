#!/bin/sh

kudzu -qps -c NETWORK | egrep "desc|network.hwaddr|driver" > /var/ipfire/ethernet/scanned_nics 2>/dev/null

exit 0
