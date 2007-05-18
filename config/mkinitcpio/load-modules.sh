#! /bin/sh
# Implement blacklisting for udev-loaded modules
#   Includes module checking
# - Aaron Griffin & Tobias Powalowski for Archlinux
[ $# -ne 1 ] && exit 1

if [ -f /proc/cmdline ]; then 
	for cmd in $(cat /proc/cmdline); do
    		case $cmd in
        		*=*) eval $cmd ;;
    		esac
	done
fi

# get the real names from modaliases
i="$(/bin/modprobe -i --show-depends $1 | minised "s#^insmod /lib.*/\(.*\)\.ko.*#\1#g" | minised 's|-|_|g')"
# add disablemodules= from commandline to blacklist
k="$(echo ${disablemodules} | minised 's|-|_|g' | minised 's|,| |g')"

if [ "${k}" != "" ] ; then
	for o in ${k}; do
		echo "${o}.ko" >> /disablemodules
	done
        for n in ${i}; do
		if /bin/ugrep "^$n.ko" /disablemodules 2>&1 >/dev/null; then
                	exit 1
        	fi
	done
fi
/bin/modprobe $1

# vim: set et ts=4:
