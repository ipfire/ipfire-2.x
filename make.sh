#!/bin/bash
############################################################################
#                                                                          #
# This file is part of the IPFire Firewall.                                #
#                                                                          #
# IPFire is free software; you can redistribute it and/or modify           #
# it under the terms of the GNU General Public License as published by     #
# the Free Software Foundation; either version 2 of the License, or        #
# (at your option) any later version.                                      #
#                                                                          #
# IPFire is distributed in the hope that it will be useful,                #
# but WITHOUT ANY WARRANTY; without even the implied warranty of           #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
# GNU General Public License for more details.                             #
#                                                                          #
# You should have received a copy of the GNU General Public License        #
# along with IPFire; if not, write to the Free Software                    #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA #
#                                                                          #
# Copyright (C) 2007-2017 IPFire Team <info@ipfire.org>.                   #
#                                                                          #
############################################################################
#

NAME="IPFire"							# Software name
SNAME="ipfire"							# Short name
VERSION="2.19"							# Version number
CORE="115"							# Core Level (Filename)
PAKFIRE_CORE="114"						# Core Level (PAKFIRE)
GIT_BRANCH=`git rev-parse --abbrev-ref HEAD`			# Git Branch
SLOGAN="www.ipfire.org"						# Software slogan
CONFIG_ROOT=/var/ipfire						# Configuration rootdir
NICE=10								# Nice level
MAX_RETRIES=1							# prefetch/check loop
BUILD_IMAGES=1							# Flash and Xen Downloader
KVER=`grep --max-count=1 VER lfs/linux | awk '{ print $3 }'`
GIT_TAG=$(git tag | tail -1)					# Git Tag
GIT_LASTCOMMIT=$(git log | head -n1 | cut -d" " -f2 |head -c8)	# Last commit

TOOLCHAINVER=20170705

# New architecture variables
HOST_ARCH="$(uname -m)"

# Debian specific settings
if [ ! -e /etc/debian_version ]; then
	FULLPATH=`which $0`
else
	if [ -x /usr/bin/realpath ]; then
		FULLPATH=`/usr/bin/realpath $0`
	else
		echo "ERROR: Need to do apt-get install realpath"
		exit 1
	fi
fi

PWD=`pwd`
BASENAME=`basename $0`
BASEDIR=`echo $FULLPATH | sed "s/\/$BASENAME//g"`
LOGFILE=$BASEDIR/log/_build.preparation.log
export BASEDIR LOGFILE
DIR_CHK=$BASEDIR/cache/check
mkdir $BASEDIR/log/ 2>/dev/null

# Include funtions
. tools/make-functions

if [ -f .config ]; then
	. .config
fi

if [ -n "${BUILD_ARCH}" ]; then
	configure_build "${BUILD_ARCH}"
elif [ -n "${TARGET_ARCH}" ]; then
	configure_build "${TARGET_ARCH}"
	unset TARGET_ARCH
else
	configure_build "default"
fi

if [ -z $EDITOR ]; then
	for i in nano emacs vi; do
		EDITOR=$(which $i 2>/dev/null)
		if ! [ -z $EDITOR ]; then
			export EDITOR=$EDITOR
			break
		fi
	done
	[ -z $EDITOR ] && exiterror "You should have installed an editor."
fi


prepareenv() {
    ############################################################################
    #                                                                          #
    # Are we running the right shell?                                          #
    #                                                                          #
    ############################################################################
    if [ ! "$BASH" ]; then
			exiterror "BASH environment variable is not set.  You're probably running the wrong shell."
    fi

    if [ -z "${BASH_VERSION}" ]; then
			exiterror "Not running BASH shell."
    fi


    ############################################################################
    #                                                                          #
    # Trap on emergency exit                                                   #
    #                                                                          #
    ############################################################################
    trap "exiterror 'Build process interrupted'" SIGINT SIGTERM SIGKILL SIGSTOP SIGQUIT


    ############################################################################
    #                                                                          #
    # Resetting our nice level                                                 #
    #                                                                          #
    ############################################################################
    echo -ne "Resetting our nice level to $NICE" | tee -a $LOGFILE
    renice $NICE $$ > /dev/null
    if [ `nice` != "$NICE" ]; then
			beautify message FAIL
			exiterror "Failed to set correct nice level"
    else
			beautify message DONE
    fi


    ############################################################################
    #                                                                          #
    # Checking if running as root user                                         #
    #                                                                          #
    ############################################################################
    echo -ne "Checking if we're running as root user" | tee -a $LOGFILE
    if [ `id -u` != 0 ]; then
			beautify message FAIL
			exiterror "Not building as root"
    else
			beautify message DONE
    fi


    ############################################################################
    #                                                                          #
    # Checking for necessary temporary space                                   #
    #                                                                          #
    ############################################################################
    echo -ne "Checking for necessary space on disk $BASE_DEV" | tee -a $LOGFILE
    BASE_DEV=`df -P -k $BASEDIR | tail -n 1 | awk '{ print $1 }'`
    BASE_ASPACE=`df -P -k $BASEDIR | tail -n 1 | awk '{ print $4 }'`
    if (( 2048000 > $BASE_ASPACE )); then
			BASE_USPACE=`du -skx $BASEDIR | awk '{print $1}'`
			if (( 2048000 - $BASE_USPACE > $BASE_ASPACE )); then
				beautify message FAIL
				exiterror "Not enough temporary space available, need at least 2GB on $BASE_DEV"
			fi
    else
			beautify message DONE
    fi

    ############################################################################
    #                                                                          #
    # Building Linux From Scratch system                                       #
    #                                                                          #
    ############################################################################
    # Set umask
    umask 022

    # Set LFS Directory
    LFS=$BASEDIR/build

    # Check /tools symlink
    if [ -h /tools ]; then
        rm -f /tools
    fi
    if [ ! -a /tools ]; then
			ln -s $BASEDIR/build/tools /
    fi
    if [ ! -h /tools ]; then
			exiterror "Could not create /tools symbolic link."
    fi

    # Setup environment
    set +h
    LC_ALL=POSIX
    if [ -z $MAKETUNING ]; then
	CPU_COUNT="$(getconf _NPROCESSORS_ONLN 2>/dev/null)"
	if [ -z "${CPU_COUNT}" ]; then
		CPU_COUNT=1
	fi

	MAKETUNING="-j$(( ${CPU_COUNT} * 2 + 1 ))"
    fi
    export LFS LC_ALL CFLAGS CXXFLAGS MAKETUNING
    unset CC CXX CPP LD_LIBRARY_PATH LD_PRELOAD

    # Make some extra directories
    mkdir -p $BASEDIR/build/{tools,etc,usr/src} 2>/dev/null
    mkdir -p $BASEDIR/build/{dev/{shm,pts},proc,sys}
    mkdir -p $BASEDIR/{cache,ccache} 2>/dev/null
    mkdir -p $BASEDIR/build/usr/src/{cache,config,doc,html,langs,lfs,log,src,ccache}

    mknod -m 600 $BASEDIR/build/dev/console c 5 1 2>/dev/null
    mknod -m 666 $BASEDIR/build/dev/null c 1 3 2>/dev/null

    # Make all sources and proc available under lfs build
    mount --bind /dev            $BASEDIR/build/dev
    mount --bind /dev/pts        $BASEDIR/build/dev/pts
    mount --bind /dev/shm        $BASEDIR/build/dev/shm
    mount --bind /proc           $BASEDIR/build/proc
    mount --bind /sys            $BASEDIR/build/sys
    mount --bind $BASEDIR/cache  $BASEDIR/build/usr/src/cache
    mount --bind $BASEDIR/ccache $BASEDIR/build/usr/src/ccache
    mount --bind $BASEDIR/config $BASEDIR/build/usr/src/config
    mount --bind $BASEDIR/doc    $BASEDIR/build/usr/src/doc
    mount --bind $BASEDIR/html   $BASEDIR/build/usr/src/html
    mount --bind $BASEDIR/langs  $BASEDIR/build/usr/src/langs
    mount --bind $BASEDIR/lfs    $BASEDIR/build/usr/src/lfs
    mount --bind $BASEDIR/log    $BASEDIR/build/usr/src/log
    mount --bind $BASEDIR/src    $BASEDIR/build/usr/src/src

    # Run LFS static binary creation scripts one by one
    export CCACHE_DIR=$BASEDIR/ccache
    export CCACHE_COMPRESS=1
    export CCACHE_COMPILERCHECK="string:toolchain-${TOOLCHAINVER} ${BUILD_ARCH}"

    # Remove pre-install list of installed files in case user erase some files before rebuild
    rm -f $BASEDIR/build/usr/src/lsalr 2>/dev/null

    # Prepare string for /etc/system-release.
    SYSTEM_RELEASE="${NAME} ${VERSION} (${BUILD_ARCH})"
    if [ "$(git status -s | wc -l)" == "0" ]; then
	GIT_STATUS=""
    else
	GIT_STATUS="-dirty"
    fi
    case "$GIT_BRANCH" in
	core*|beta?|rc?)
		SYSTEM_RELEASE="${SYSTEM_RELEASE} - $GIT_BRANCH$GIT_STATUS"
		;;
	*)
		SYSTEM_RELEASE="${SYSTEM_RELEASE} - Development Build: $GIT_BRANCH/$GIT_LASTCOMMIT$GIT_STATUS"
		;;
    esac
}

buildtoolchain() {
    local error=false
    case "${BUILD_ARCH}:${HOST_ARCH}" in
        # x86_64
        x86_64:x86_64)
             # This is working.
             ;;

        # x86
        i586:i586|i586:i686|i586:x86_64)
            # These are working.
            ;;
        i586:*)
            error=true
            ;;

        # ARM
        arvm7hl:armv7hl|armv7hl:armv7l)
            # These are working.
            ;;

        armv5tel:armv5tel|armv5tel:armv5tejl|armv5tel:armv6l|armv5tel:armv7l|armv5tel:aarch64)
            # These are working.
            ;;
        armv5tel:*)
            error=true
            ;;
    esac

    ${error} && \
        exiterror "Cannot build ${BUILD_ARCH} toolchain on $(uname -m). Please use the download if any."

    local gcc=$(type -p gcc)
    if [ -z "${gcc}" ]; then
        exiterror "Could not find GCC. You will need a working build enviroment in order to build the toolchain."
    fi

    LOGFILE="$BASEDIR/log/_build.toolchain.log"
    export LOGFILE

    lfsmake1 stage1
    lfsmake1 ccache			PASS=1
    lfsmake1 binutils			PASS=1
    lfsmake1 gcc			PASS=1
    lfsmake1 linux			KCFG="-headers"
    lfsmake1 glibc
    lfsmake1 gcc			PASS=L
    lfsmake1 binutils			PASS=2
    lfsmake1 gcc			PASS=2
    lfsmake1 ccache			PASS=2
    lfsmake1 tcl
    lfsmake1 expect
    lfsmake1 dejagnu
    lfsmake1 pkg-config
    lfsmake1 ncurses
    lfsmake1 bash
    lfsmake1 bzip2
    lfsmake1 automake
    lfsmake1 coreutils
    lfsmake1 diffutils
    lfsmake1 findutils
    lfsmake1 gawk
    lfsmake1 gettext
    lfsmake1 grep
    lfsmake1 gzip
    lfsmake1 m4
    lfsmake1 make
    lfsmake1 patch
    lfsmake1 perl
    lfsmake1 sed
    lfsmake1 tar
    lfsmake1 texinfo
    lfsmake1 xz
    lfsmake1 fake-environ
    lfsmake1 cleanup-toolchain
}

buildbase() {
    LOGFILE="$BASEDIR/log/_build.base.log"
    export LOGFILE
    lfsmake2 stage2
    lfsmake2 linux			KCFG="-headers"
    lfsmake2 man-pages
    lfsmake2 glibc
    lfsmake2 tzdata
    lfsmake2 cleanup-toolchain
    lfsmake2 zlib
    lfsmake2 binutils
    lfsmake2 gmp
    lfsmake2 gmp-compat
    lfsmake2 mpfr
    lfsmake2 libmpc
    lfsmake2 file
    lfsmake2 gcc
    lfsmake2 sed
    lfsmake2 autoconf
    lfsmake2 automake
    lfsmake2 berkeley
    lfsmake2 coreutils
    lfsmake2 iana-etc
    lfsmake2 m4
    lfsmake2 bison
    lfsmake2 ncurses-compat
    lfsmake2 ncurses
    lfsmake2 procps
    lfsmake2 libtool
    lfsmake2 perl
    lfsmake2 readline
    lfsmake2 readline-compat
    lfsmake2 bzip2
    lfsmake2 pcre
    lfsmake2 pcre-compat
    lfsmake2 bash
    lfsmake2 diffutils
    lfsmake2 e2fsprogs
    lfsmake2 ed
    lfsmake2 findutils
    lfsmake2 flex
    lfsmake2 gawk
    lfsmake2 gettext
    lfsmake2 grep
    lfsmake2 groff
    lfsmake2 gperf
    lfsmake2 gzip
    lfsmake2 hostname
    lfsmake2 iproute2
    lfsmake2 jwhois
    lfsmake2 kbd
    lfsmake2 less
    lfsmake2 make
    lfsmake2 man
    lfsmake2 kmod
    lfsmake2 net-tools
    lfsmake2 patch
    lfsmake2 psmisc
    lfsmake2 shadow
    lfsmake2 sysklogd
    lfsmake2 sysvinit
    lfsmake2 tar
    lfsmake2 texinfo
    lfsmake2 util-linux
    lfsmake2 udev
    lfsmake2 vim
    lfsmake2 xz
    lfsmake2 paxctl
}

buildipfire() {
  LOGFILE="$BASEDIR/log/_build.ipfire.log"
  export LOGFILE
  lfsmake2 configroot
  lfsmake2 initscripts
  lfsmake2 backup
  lfsmake2 pkg-config
  lfsmake2 libusb
  lfsmake2 libusb-compat
  lfsmake2 libpcap
  lfsmake2 ppp
  lfsmake2 pptp
  lfsmake2 unzip
  lfsmake2 which
  lfsmake2 linux-firmware
  lfsmake2 ath10k-firmware
  lfsmake2 dvb-firmwares
  lfsmake2 mt7601u-firmware
  lfsmake2 zd1211-firmware
  lfsmake2 rpi-firmware
  lfsmake2 bc
  lfsmake2 u-boot
  lfsmake2 cpio
  lfsmake2 mdadm
  lfsmake2 dracut
  lfsmake2 lvm2
  lfsmake2 multipath-tools
  lfsmake2 freetype
  lfsmake2 grub
  lfsmake2 libmnl
  lfsmake2 libnfnetlink
  lfsmake2 libnetfilter_queue
  lfsmake2 libnetfilter_conntrack
  lfsmake2 libnetfilter_cthelper
  lfsmake2 libnetfilter_cttimeout
  lfsmake2 iptables

  case "${BUILD_ARCH}" in
	x86_64)
		lfsmake2 linux			KCFG=""
		lfsmake2 backports			KCFG=""
		lfsmake2 e1000e			KCFG=""
		lfsmake2 igb				KCFG=""
		lfsmake2 ixgbe			KCFG=""
		lfsmake2 xtables-addons		KCFG=""
		lfsmake2 linux-initrd			KCFG=""
		;;
	i586)
		# x86-pae (Native and new XEN) kernel build
		lfsmake2 linux			KCFG="-pae"
		lfsmake2 backports			KCFG="-pae"
		lfsmake2 e1000e			KCFG="-pae"
		lfsmake2 igb				KCFG="-pae"
		lfsmake2 ixgbe			KCFG="-pae"
		lfsmake2 xtables-addons		KCFG="-pae"
		lfsmake2 linux-initrd			KCFG="-pae"

		# x86 kernel build
		lfsmake2 linux			KCFG=""
		lfsmake2 backports			KCFG=""
		lfsmake2 e1000e			KCFG=""
		lfsmake2 igb				KCFG=""
		lfsmake2 ixgbe			KCFG=""
		lfsmake2 xtables-addons		KCFG=""
		lfsmake2 linux-initrd			KCFG=""
		;;

	armv5tel)
		# arm-rpi (Raspberry Pi) kernel build
		lfsmake2 linux			KCFG="-rpi"
		lfsmake2 backports			KCFG="-rpi"
		lfsmake2 xtables-addons		KCFG="-rpi"
		lfsmake2 linux-initrd			KCFG="-rpi"

		# arm multi platform (Panda, Wandboard ...) kernel build
		lfsmake2 linux			KCFG="-multi"
		lfsmake2 backports			KCFG="-multi"
		lfsmake2 e1000e			KCFG="-multi"
		lfsmake2 igb				KCFG="-multi"
		lfsmake2 ixgbe			KCFG="-multi"
		lfsmake2 xtables-addons		KCFG="-multi"
		lfsmake2 linux-initrd			KCFG="-multi"

		# arm-kirkwood (Dreamplug, ICY-Box ...) kernel build
		lfsmake2 linux			KCFG="-kirkwood"
		lfsmake2 backports			KCFG="-kirkwood"
		lfsmake2 e1000e			KCFG="-kirkwood"
		lfsmake2 igb				KCFG="-kirkwood"
		lfsmake2 ixgbe			KCFG="-kirkwood"
		lfsmake2 xtables-addons		KCFG="-kirkwood"
		lfsmake2 linux-initrd			KCFG="-kirkwood"
		;;
  esac
  lfsmake2 xtables-addons			USPACE="1"
  lfsmake2 openssl
  [ "${BUILD_ARCH}" = "i586" ] && lfsmake2 openssl KCFG='-sse2'
  lfsmake2 libgpg-error
  lfsmake2 libgcrypt
  lfsmake2 libassuan
  lfsmake2 nettle
  lfsmake2 libevent
  lfsmake2 libevent2
  lfsmake2 libevent2-compat
  lfsmake2 expat
  lfsmake2 apr
  lfsmake2 aprutil
  lfsmake2 unbound
  lfsmake2 gnutls
  lfsmake2 bind
  lfsmake2 dhcp
  lfsmake2 dhcpcd
  lfsmake2 boost
  lfsmake2 linux-atm
  lfsmake2 gdbm
  lfsmake2 pam
  lfsmake2 curl
  lfsmake2 tcl
  lfsmake2 sqlite
  lfsmake2 libffi
  lfsmake2 python
  lfsmake2 python3
  lfsmake2 ca-certificates
  lfsmake2 fireinfo
  lfsmake2 libnet
  lfsmake2 libnl
  lfsmake2 libnl-3
  lfsmake2 libidn
  lfsmake2 nasm
  lfsmake2 libjpeg
  lfsmake2 libjpeg-compat
  lfsmake2 libexif
  lfsmake2 libpng
  lfsmake2 libtiff
  lfsmake2 libart
  lfsmake2 gd
  lfsmake2 popt
  lfsmake2 slang
  lfsmake2 newt
  lfsmake2 libsmooth
  lfsmake2 attr
  lfsmake2 acl
  lfsmake2 libcap
  lfsmake2 pciutils
  lfsmake2 usbutils
  lfsmake2 libxml2
  lfsmake2 libxslt
  lfsmake2 BerkeleyDB
  lfsmake2 mysql
  lfsmake2 cyrus-sasl
  lfsmake2 openldap
  lfsmake2 apache2
  lfsmake2 php
  lfsmake2 web-user-interface
  lfsmake2 flag-icons
  lfsmake2 jquery
  lfsmake2 bootstrap
  lfsmake2 arping
  lfsmake2 beep
  lfsmake2 dvdrtools
  lfsmake2 dosfstools
  lfsmake2 reiserfsprogs
  lfsmake2 xfsprogs
  lfsmake2 sysfsutils
  lfsmake2 fuse
  lfsmake2 ntfs-3g
  lfsmake2 ethtool
  lfsmake2 ez-ipupdate
  lfsmake2 fcron
  lfsmake2 perl-GD
  lfsmake2 GD-Graph
  lfsmake2 GD-TextUtil
  lfsmake2 perl-Device-SerialPort
  lfsmake2 perl-Device-Modem
  lfsmake2 perl-Apache-Htpasswd
  lfsmake2 gnupg
  lfsmake2 hdparm
  lfsmake2 sdparm
  lfsmake2 mtools
  lfsmake2 whatmask
  lfsmake2 conntrack-tools
  lfsmake2 libupnp
  lfsmake2 ipaddr
  lfsmake2 iputils
  lfsmake2 l7-protocols
  lfsmake2 mISDNuser
  lfsmake2 capi4k-utils
  lfsmake2 hwdata
  lfsmake2 logrotate
  lfsmake2 logwatch
  lfsmake2 misc-progs
  lfsmake2 nano
  lfsmake2 URI
  lfsmake2 HTML-Tagset
  lfsmake2 HTML-Parser
  lfsmake2 HTML-Template
  lfsmake2 Compress-Zlib
  lfsmake2 Digest
  lfsmake2 Digest-SHA1
  lfsmake2 Digest-HMAC
  lfsmake2 libwww-perl
  lfsmake2 Net-DNS
  lfsmake2 Net-IPv4Addr
  lfsmake2 Net_SSLeay
  lfsmake2 IO-Stringy
  lfsmake2 IO-Socket-SSL
  lfsmake2 Unix-Syslog
  lfsmake2 Mail-Tools
  lfsmake2 MIME-Tools
  lfsmake2 Net-Server
  lfsmake2 Convert-TNEF
  lfsmake2 Convert-UUlib
  lfsmake2 Archive-Tar
  lfsmake2 Archive-Zip
  lfsmake2 Text-Tabs+Wrap
  lfsmake2 Locale-Country
  lfsmake2 XML-Parser
  lfsmake2 Crypt-PasswdMD5
  lfsmake2 Net-Telnet
  lfsmake2 python-setuptools
  lfsmake2 python-clientform
  lfsmake2 python-mechanize
  lfsmake2 python-feedparser
  lfsmake2 python-rssdler
  lfsmake2 python-inotify
  lfsmake2 python-docutils
  lfsmake2 python-daemon
  lfsmake2 python-ipaddress
  lfsmake2 glib
  lfsmake2 GeoIP
  lfsmake2 noip_updater
  lfsmake2 ntp
  lfsmake2 openssh
  lfsmake2 fontconfig
  lfsmake2 dejavu-fonts-ttf
  lfsmake2 ubuntu-font-family
  lfsmake2 freefont
  lfsmake2 pixman
  lfsmake2 cairo
  lfsmake2 pango
  lfsmake2 rrdtool
  lfsmake2 setserial
  lfsmake2 setup
  lfsmake2 libdnet
  lfsmake2 daq
  lfsmake2 snort
  lfsmake2 oinkmaster
  lfsmake2 squid
  lfsmake2 squidguard
  lfsmake2 calamaris
  lfsmake2 tcpdump
  lfsmake2 traceroute
  lfsmake2 vlan
  lfsmake2 wireless
  lfsmake2 pakfire
  lfsmake2 spandsp
  lfsmake2 lzo
  lfsmake2 openvpn
  lfsmake2 pammysql
  lfsmake2 mpage
  lfsmake2 dbus
  lfsmake2 intltool
  lfsmake2 libdaemon
  lfsmake2 cups
  lfsmake2 lcms2
  lfsmake2 ghostscript
  lfsmake2 qpdf
  lfsmake2 poppler
  lfsmake2 cups-filters
  lfsmake2 epson-inkjet-printer-escpr
  lfsmake2 foomatic
  lfsmake2 hplip
  lfsmake2 cifs-utils
  lfsmake2 krb5
  lfsmake2 samba
  lfsmake2 sudo
  lfsmake2 mc
  lfsmake2 wget
  lfsmake2 bridge-utils
  lfsmake2 screen
  lfsmake2 smartmontools
  lfsmake2 htop
  lfsmake2 chkconfig
  lfsmake2 postfix
  lfsmake2 fetchmail
  lfsmake2 cyrus-imapd
  lfsmake2 openmailadmin
  lfsmake2 clamav
  lfsmake2 spamassassin
  lfsmake2 amavisd
  lfsmake2 dma
  lfsmake2 alsa
  lfsmake2 mpfire
  lfsmake2 guardian
  lfsmake2 libid3tag
  lfsmake2 libmad
  lfsmake2 libogg
  lfsmake2 libvorbis
  lfsmake2 libdvbpsi
  lfsmake2 flac
  lfsmake2 lame
  lfsmake2 sox
  lfsmake2 libshout
  lfsmake2 xvid
  lfsmake2 libmpeg2
  lfsmake2 libarchive
  lfsmake2 cmake
  lfsmake2 gnump3d
  lfsmake2 rsync
  lfsmake2 tcpwrapper
  lfsmake2 libtirpc
  lfsmake2 rpcbind
  lfsmake2 nfs
  lfsmake2 gnu-netcat
  lfsmake2 ncat
  lfsmake2 nmap
  lfsmake2 etherwake
  lfsmake2 bwm-ng
  lfsmake2 sysstat
  lfsmake2 vsftpd
  lfsmake2 strongswan
  lfsmake2 rng-tools
  lfsmake2 lsof
  lfsmake2 br2684ctl
  lfsmake2 pcmciautils
  lfsmake2 lm_sensors
  lfsmake2 liboping
  lfsmake2 collectd
  lfsmake2 elinks
  lfsmake2 igmpproxy
  lfsmake2 fbset
  lfsmake2 opus
  lfsmake2 python-six
  lfsmake2 python-pyparsing
  lfsmake2 spice-protocol
  lfsmake2 spice
  lfsmake2 sdl
  lfsmake2 libusbredir
  lfsmake2 qemu
  lfsmake2 sane
  lfsmake2 netpbm
  lfsmake2 phpSANE
  lfsmake2 tunctl
  lfsmake2 netsnmpd
  lfsmake2 nagios
  lfsmake2 nagios_nrpe
  lfsmake2 icinga
  lfsmake2 ebtables
  lfsmake2 directfb
  lfsmake2 faad2
  lfsmake2 ffmpeg
  lfsmake2 vdr
  lfsmake2 vdr_streamdev
  lfsmake2 vdr_epgsearch
  lfsmake2 vdr_dvbapi
  lfsmake2 vdr_eepg
  lfsmake2 w_scan
  lfsmake2 icecast
  lfsmake2 icegenerator
  lfsmake2 mpd
  lfsmake2 libmpdclient
  lfsmake2 mpc
  lfsmake2 perl-Net-SMTP-SSL
  lfsmake2 perl-MIME-Base64
  lfsmake2 perl-Authen-SASL
  lfsmake2 perl-MIME-Lite
  lfsmake2 perl-Email-Date-Format
  lfsmake2 git
  lfsmake2 squidclamav
  lfsmake2 vnstat
  lfsmake2 iw
  lfsmake2 wpa_supplicant
  lfsmake2 hostapd
  lfsmake2 pycurl
  lfsmake2 urlgrabber
  lfsmake2 syslinux
  lfsmake2 tftpd
  lfsmake2 cpufrequtils
  lfsmake2 bluetooth
  lfsmake2 gutenprint
  lfsmake2 apcupsd
  lfsmake2 iperf
  lfsmake2 iperf3
  lfsmake2 7zip
  lfsmake2 lynis
  lfsmake2 streamripper
  lfsmake2 sshfs
  lfsmake2 taglib
  #lfsmake2 mediatomb
  lfsmake2 sslh
  lfsmake2 perl-gettext
  lfsmake2 perl-Sort-Naturally
  lfsmake2 vdradmin
  lfsmake2 miau
  lfsmake2 perl-DBI
  lfsmake2 perl-DBD-mysql
  lfsmake2 perl-DBD-SQLite
  lfsmake2 perl-File-ReadBackwards
  lfsmake2 cacti
  lfsmake2 openvmtools
  lfsmake2 nagiosql
  lfsmake2 motion
  lfsmake2 joe
  lfsmake2 monit
  lfsmake2 nut
  lfsmake2 watchdog
  lfsmake2 libpri
  lfsmake2 libsrtp
  lfsmake2 asterisk
  lfsmake2 lcr
  lfsmake2 usb_modeswitch
  lfsmake2 usb_modeswitch_data
  lfsmake2 zerofree
  lfsmake2 pound
  lfsmake2 minicom
  lfsmake2 ddrescue
  lfsmake2 miniupnpd
  lfsmake2 client175
  lfsmake2 powertop
  lfsmake2 parted
  lfsmake2 swig
  lfsmake2 python-m2crypto
  lfsmake2 wireless-regdb
  lfsmake2 crda
  lfsmake2 libsolv
  lfsmake2 python-distutils-extra
  lfsmake2 python-lzma
  lfsmake2 python-progressbar
  lfsmake2 python-xattr
  lfsmake2 ddns
  lfsmake2 transmission
  lfsmake2 dpfhack
  lfsmake2 lcd4linux
  lfsmake2 mtr
  lfsmake2 minidlna
  lfsmake2 acpid
  lfsmake2 fping
  lfsmake2 telnet
  lfsmake2 xinetd
  lfsmake2 gpgme
  lfsmake2 pygpgme
  lfsmake2 pakfire3
  lfsmake2 stress
  lfsmake2 libstatgrab
  lfsmake2 sarg
  lfsmake2 check_mk_agent
  lfsmake2 nginx
  lfsmake2 sendEmail
  lfsmake2 sysbench
  lfsmake2 strace
  lfsmake2 elfutils
  lfsmake2 ltrace
  lfsmake2 ipfire-netboot
  lfsmake2 lcdproc
  lfsmake2 bitstream
  lfsmake2 multicat
  lfsmake2 keepalived
  lfsmake2 ipvsadm
  lfsmake2 perl-Carp-Clan
  lfsmake2 perl-Date-Calc
  lfsmake2 perl-Date-Manip
  lfsmake2 perl-File-Tail
  lfsmake2 perl-TimeDate
  lfsmake2 swatch
  lfsmake2 tor
  lfsmake2 arm
  lfsmake2 wavemon
  lfsmake2 iptraf-ng
  lfsmake2 iotop
  lfsmake2 stunnel
  lfsmake2 sslscan
  lfsmake2 owncloud
  lfsmake2 bacula
  lfsmake2 batctl
  lfsmake2 perl-Font-TTF
  lfsmake2 perl-IO-String
  lfsmake2 perl-PDF-API2
  lfsmake2 squid-accounting
  lfsmake2 pigz
  lfsmake2 tmux
  lfsmake2 perl-Text-CSV_XS
  lfsmake2 swconfig
  lfsmake2 haproxy
  lfsmake2 ipset
  lfsmake2 lua
  lfsmake2 dnsdist
  lfsmake2 bird
  lfsmake2 dmidecode
  lfsmake2 mcelog
  lfsmake2 rtpproxy
  lfsmake2 util-macros
  lfsmake2 libpciaccess
  lfsmake2 libyajl
  lfsmake2 libvirt
  lfsmake2 python3-libvirt
  lfsmake2 freeradius
  lfsmake2 perl-common-sense
  lfsmake2 perl-inotify2
  lfsmake2 perl-Net-IP
  lfsmake2 wio
  lfsmake2 iftop
}

buildinstaller() {
  # Run installer scripts one by one
  LOGFILE="$BASEDIR/log/_build.installer.log"
  export LOGFILE
  lfsmake2 memtest
  lfsmake2 installer
  lfsmake1 strip
}

buildpackages() {
  LOGFILE="$BASEDIR/log/_build.packages.log"
  export LOGFILE
  echo "... see detailed log in _build.*.log files" >> $LOGFILE

  
  # Generating list of packages used
  echo -n "Generating packages list from logs" | tee -a $LOGFILE
  rm -f $BASEDIR/doc/packages-list
  for i in `ls -1tr $BASEDIR/log/[^_]*`; do
	if [ "$i" != "$BASEDIR/log/FILES" -a -n $i ]; then
		echo "* `basename $i`" >>$BASEDIR/doc/packages-list
	fi
  done
  echo "== List of softwares used to build $NAME Version: $VERSION ==" > $BASEDIR/doc/packages-list.txt
  grep -v 'configroot$\|img$\|initrd$\|initscripts$\|installer$\|install$\|setup$\|pakfire$\|stage2$\|smp$\|tools$\|tools1$\|tools2$\|.tgz$\|-config$\|_missing_rootfile$\|install1$\|install2$\|pass1$\|pass2$\|pass3$' \
	$BASEDIR/doc/packages-list | sort >> $BASEDIR/doc/packages-list.txt
  rm -f $BASEDIR/doc/packages-list
  # packages-list.txt is ready to be displayed for wiki page
  beautify message DONE
  
  # Update changelog
  cd $BASEDIR
  [ -z $GIT_TAG ]  || LAST_TAG=$GIT_TAG
  [ -z $LAST_TAG ] || EXT="$LAST_TAG..HEAD"
  git log -n 500 --no-merges --pretty=medium --shortstat $EXT > $BASEDIR/doc/ChangeLog

  # Create images for install
  lfsmake2 cdrom

  # Check if there is a loop device for building in virtual environments
  modprobe loop 2>/dev/null
  if [ $BUILD_IMAGES == 1 ] && ([ -e /dev/loop/0 ] || [ -e /dev/loop0 ] || [ -e "/dev/loop-control" ]); then
	lfsmake2 flash-images
	lfsmake2 flash-images SCON=1
  fi

  mv $LFS/install/images/{*.iso,*.tgz,*.img.gz,*.bz2} $BASEDIR >> $LOGFILE 2>&1

  ipfirepackages

  lfsmake2 xen-image
  mv $LFS/install/images/*.bz2 $BASEDIR >> $LOGFILE 2>&1

  cd $BASEDIR

  # remove not useable iso on armv5tel (needed to build flash images)
  [ "${BUILD_ARCH}" = "armv5tel" ] && rm -rf *.iso

  for i in `ls *.bz2 *.img.gz *.iso`; do
	md5sum $i > $i.md5
  done
  cd $PWD

  # Cleanup
  stdumount
  rm -rf $BASEDIR/build/tmp/*

  # Generating total list of files
  echo -n "Generating files list from logs" | tee -a $LOGFILE
  rm -f $BASEDIR/log/FILES
  for i in `ls -1tr $BASEDIR/log/[^_]*`; do
	if [ "$i" != "$BASEDIR/log/FILES" -a -n $i ]; then
		echo "##" >>$BASEDIR/log/FILES
		echo "## `basename $i`" >>$BASEDIR/log/FILES
		echo "##" >>$BASEDIR/log/FILES
		cat $i | sed "s%^\./%#%" | sort >> $BASEDIR/log/FILES
	fi
  done
  beautify message DONE

  cd $PWD
}

ipfirepackages() {
	lfsmake2 core-updates

	local i
	for i in $(find $BASEDIR/config/rootfiles/packages{/${BUILD_ARCH},} -maxdepth 1 -type f); do
		i=$(basename ${i})
		if [ -e $BASEDIR/lfs/$i ]; then
			ipfiredist $i
		else
			echo -n $i
			beautify message SKIP
		fi
	done
  test -d $BASEDIR/packages || mkdir $BASEDIR/packages
  mv -f $LFS/install/packages/* $BASEDIR/packages >> $LOGFILE 2>&1
  rm -rf  $BASEDIR/build/install/packages/*
}

while [ $# -gt 0 ]; do
	case "${1}" in
		--target=*)
			configure_build "${1#--target=}"
			;;
		-*)
			exiterror "Unknown configuration option: ${1}"
			;;
		*)
			# Found a command, so exit options parsing.
			break
			;;
	esac
	shift
done

# See what we're supposed to do
case "$1" in 
build)
	clear
	PACKAGE=`ls -v -r $BASEDIR/cache/toolchains/$SNAME-$VERSION-toolchain-$TOOLCHAINVER-${BUILD_ARCH}.tar.gz 2> /dev/null | head -n 1`
	#only restore on a clean disk
	if [ ! -e "${BASEDIR}/build/tools/.toolchain-successful" ]; then
		if [ ! -n "$PACKAGE" ]; then
			beautify build_stage "Full toolchain compilation"
			prepareenv
			buildtoolchain
		else
			PACKAGENAME=${PACKAGE%.tar.gz}
			beautify build_stage "Packaged toolchain compilation"
			if [ `md5sum $PACKAGE | awk '{print $1}'` == `cat $PACKAGENAME.md5 | awk '{print $1}'` ]; then
				tar zxf $PACKAGE
				prepareenv
			else
				exiterror "$PACKAGENAME md5 did not match, check downloaded package"
			fi
		fi
	else
		echo -n "Using installed toolchain" | tee -a $LOGFILE
		beautify message SKIP
		prepareenv
	fi

	beautify build_start
	beautify build_stage "Building LFS"
	buildbase

	beautify build_stage "Building IPFire"
	buildipfire

	beautify build_stage "Building installer"
	buildinstaller

	beautify build_stage "Building packages"
	buildpackages
	
	beautify build_stage "Checking Logfiles for new Files"

	cd $BASEDIR
	tools/checknewlog.pl
	tools/checkrootfiles
	cd $PWD

	beautify build_end
	;;
shell)
	# enter a shell inside LFS chroot
	# may be used to changed kernel settings
	prepareenv
	entershell
	;;
clean)
	echo -en "${BOLD}Cleaning build directory...${NORMAL}"
	for i in `mount | grep $BASEDIR | sed 's/^.*loop=\(.*\))/\1/'`; do
		$LOSETUP -d $i 2>/dev/null
	done
	for i in `mount | grep $BASEDIR | cut -d " " -f 1`; do
		umount $i
	done
	stdumount
	for i in `seq 0 7`; do
	    if ( losetup /dev/loop${i} 2>/dev/null | grep -q "/install/images" ); then
		umount /dev/loop${i}     2>/dev/null;
		losetup -d /dev/loop${i} 2>/dev/null;
	    fi;
	done
	rm -rf $BASEDIR/build
	rm -rf $BASEDIR/cdrom
	rm -rf $BASEDIR/packages
	rm -rf $BASEDIR/log
	if [ -h /tools ]; then
		rm -f /tools
	fi
	rm -f $BASEDIR/ipfire-*
	beautify message DONE
	;;
downloadsrc)
	if [ ! -d $BASEDIR/cache ]; then
		mkdir $BASEDIR/cache
	fi
	mkdir -p $BASEDIR/log
	echo -e "${BOLD}Preload all source files${NORMAL}" | tee -a $LOGFILE
	FINISHED=0
	cd $BASEDIR/lfs
	for c in `seq $MAX_RETRIES`; do
		if (( FINISHED==1 )); then 
			break
		fi
		FINISHED=1
		cd $BASEDIR/lfs
		for i in *; do
			if [ -f "$i" -a "$i" != "Config" ]; then
				lfsmakecommoncheck ${i} || continue

				make -s -f $i LFS_BASEDIR=$BASEDIR BUILD_ARCH="${BUILD_ARCH}" \
					MESSAGE="$i\t ($c/$MAX_RETRIES)" download >> $LOGFILE 2>&1
				if [ $? -ne 0 ]; then
					beautify message FAIL
					FINISHED=0
				else
					if [ $c -eq 1 ]; then
					beautify message DONE
					fi
				fi
			fi
		done
	done
	echo -e "${BOLD}***Verifying md5sums${NORMAL}"
	ERROR=0
	for i in *; do
		if [ -f "$i" -a "$i" != "Config" ]; then
			lfsmakecommoncheck ${i} > /dev/null || continue
			make -s -f $i LFS_BASEDIR=$BASEDIR BUILD_ARCH="${BUILD_ARCH}" \
				MESSAGE="$i\t " md5 >> $LOGFILE 2>&1
			if [ $? -ne 0 ]; then
				echo -ne "MD5 difference in lfs/$i"
				beautify message FAIL
				ERROR=1
			fi
		fi
	done
	if [ $ERROR -eq 0 ]; then
		echo -ne "${BOLD}all files md5sum match${NORMAL}"
		beautify message DONE
	else
		echo -ne "${BOLD}not all files were correctly download${NORMAL}"
		beautify message FAIL
	fi
	cd - >/dev/null 2>&1
	;;
toolchain)
	clear
	prepareenv
	beautify build_stage "Toolchain compilation"
	buildtoolchain
	echo "`date -u '+%b %e %T'`: Create toolchain tar.gz for ${BUILD_ARCH}" | tee -a $LOGFILE
	test -d $BASEDIR/cache/toolchains || mkdir -p $BASEDIR/cache/toolchains
	cd $BASEDIR && tar -zc --exclude='log/_build.*.log' -f cache/toolchains/$SNAME-$VERSION-toolchain-$TOOLCHAINVER-${BUILD_ARCH}.tar.gz \
		build/tools build/bin/sh log >> $LOGFILE
	md5sum cache/toolchains/$SNAME-$VERSION-toolchain-$TOOLCHAINVER-${BUILD_ARCH}.tar.gz \
		> cache/toolchains/$SNAME-$VERSION-toolchain-$TOOLCHAINVER-${BUILD_ARCH}.md5
	stdumount
	;;
gettoolchain)
	# arbitrary name to be updated in case of new toolchain package upload
	PACKAGE=$SNAME-$VERSION-toolchain-$TOOLCHAINVER-${BUILD_ARCH}
	if [ ! -f $BASEDIR/cache/toolchains/$PACKAGE.tar.gz ]; then
		URL_TOOLCHAIN=`grep URL_TOOLCHAIN lfs/Config | awk '{ print $3 }'`
		test -d $BASEDIR/cache/toolchains || mkdir -p $BASEDIR/cache/toolchains
		echo "`date -u '+%b %e %T'`: Load toolchain tar.gz for ${BUILD_ARCH}" | tee -a $LOGFILE
		cd $BASEDIR/cache/toolchains
		wget -U "IPFireSourceGrabber/2.x" $URL_TOOLCHAIN/$PACKAGE.tar.gz $URL_TOOLCHAIN/$PACKAGE.md5 >& /dev/null
		if [ $? -ne 0 ]; then
			echo "`date -u '+%b %e %T'`: error downloading $PACKAGE toolchain for ${BUILD_ARCH} machine" | tee -a $LOGFILE
		else
			if [ "`md5sum $PACKAGE.tar.gz | awk '{print $1}'`" = "`cat $PACKAGE.md5 | awk '{print $1}'`" ]; then
				echo "`date -u '+%b %e %T'`: toolchain md5 ok" | tee -a $LOGFILE
			else
				exiterror "$PACKAGE.md5 did not match, check downloaded package"
			fi
		fi
	else
		echo "Toolchain is already downloaded. Exiting..."
	fi
	;;
othersrc)
	prepareenv
	echo -ne "`date -u '+%b %e %T'`: Build sources iso for ${BUILD_ARCH}" | tee -a $LOGFILE
	chroot $LFS /tools/bin/env -i   HOME=/root \
	TERM=$TERM PS1='\u:\w\$ ' \
	PATH=/usr/local/bin:/bin:/usr/bin:/sbin:/usr/sbin \
	VERSION=$VERSION NAME="$NAME" SNAME="$SNAME" BUILD_ARCH="${BUILD_ARCH}" \
	/bin/bash -x -c "cd /usr/src/lfs && make -f sources-iso LFS_BASEDIR=/usr/src install" >>$LOGFILE 2>&1
	mv $LFS/install/images/ipfire-* $BASEDIR >> $LOGFILE 2>&1
	if [ $? -eq "0" ]; then
		beautify message DONE
	else
		beautify message FAIL
	fi
	stdumount
	;;
uploadsrc)
	PWD=`pwd`
	if [ -z $IPFIRE_USER ]; then
		echo -n "You have to setup IPFIRE_USER first. See .config for details."
		beautify message FAIL
		exit 1
	fi

	URL_SOURCE=$(grep URL_SOURCE lfs/Config | awk '{ print $3 }')
	REMOTE_FILES=$(echo "ls -1" | sftp -C ${IPFIRE_USER}@${URL_SOURCE})

	for file in ${BASEDIR}/cache/*; do
		[ -d "${file}" ] && continue
		grep -q "$(basename ${file})" <<<$REMOTE_FILES && continue
		NEW_FILES="$NEW_FILES $file"
	done
	[ -n "$NEW_FILES" ] && scp -2 $NEW_FILES ${IPFIRE_USER}@${URL_SOURCE}
	cd $BASEDIR
	cd $PWD
	exit 0
	;;
lang)
	update_langs
	;;
*)
	echo "Usage: $0 {build|changelog|clean|gettoolchain|downloadsrc|shell|sync|toolchain}"
	cat doc/make.sh-usage
	;;
esac
