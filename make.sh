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
# Copyright (C) 2007-2013 IPFire Team <info@ipfire.org>.                   #
#                                                                          #
############################################################################
#

NAME="IPFire"							# Software name
SNAME="ipfire"							# Short name
VERSION="2.15"							# Version number
CORE="76-beta1"							# Core Level (Filename)
PAKFIRE_CORE="76"						# Core Level (PAKFIRE)
GIT_BRANCH=`git rev-parse --abbrev-ref HEAD`			# Git Branch
SLOGAN="www.ipfire.org"						# Software slogan
CONFIG_ROOT=/var/ipfire						# Configuration rootdir
NICE=10								# Nice level
MAX_RETRIES=1							# prefetch/check loop
BUILD_IMAGES=1							# Flash and Xen Downloader
KVER=`grep --max-count=1 VER lfs/linux | awk '{ print $3 }'`
MACHINE=`uname -m`
GIT_TAG=$(git tag | tail -1)					# Git Tag
GIT_LASTCOMMIT=$(git log | head -n1 | cut -d" " -f2 |head -c8)	# Last commit
TOOLCHAINVER=7

BUILDMACHINE=$MACHINE
    if [ "$MACHINE" = "x86_64" ]; then
        BUILDMACHINE="i686";
    fi


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

# Prepare string for /etc/system-release.
SYSTEM_RELEASE="${NAME} ${VERSION} (${MACHINE})"
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
    export CCACHE_COMPILERCHECK="none"

    # Remove pre-install list of installed files in case user erase some files before rebuild
    rm -f $BASEDIR/build/usr/src/lsalr 2>/dev/null
}

buildtoolchain() {
    local error=false
    case "${MACHINE}:$(uname -m)" in
        # x86
        i586:i586|i586:i686|i586:x86_64)
            # These are working.
            ;;
        i586:*)
            error=true
            ;;

        # ARM
        armv5tel:armv5tel|armv5tel:armv5tejl|armv5tel:armv6l|armv5tel:armv7l)
            # These are working.
            ;;
        armv5tel:*)
            error=true
            ;;
    esac

    ${error} && \
        exiterror "Cannot build ${MACHINE} toolchain on $(uname -m). Please use the download if any."

    local gcc=$(type -p gcc)
    if [ -z "${gcc}" ]; then
        exiterror "Could not find GCC. You will need a working build enviroment in order to build the toolchain."
    fi

    LOGFILE="$BASEDIR/log/_build.toolchain.log"
    export LOGFILE

    local ORG_PATH=$PATH
    export PATH="/tools/ccache/bin:/tools/bin:$PATH"
    lfsmake1 ccache			PASS=1
    lfsmake1 binutils			PASS=1
    lfsmake1 gcc			PASS=1
    lfsmake1 linux			TOOLS=1 KCFG="-headers"
    lfsmake1 glibc
    lfsmake1 cleanup-toolchain		PASS=1
    lfsmake1 binutils			PASS=2
    lfsmake1 gcc			PASS=2
    lfsmake1 ccache			PASS=2
    lfsmake1 tcl
    lfsmake1 expect
    lfsmake1 dejagnu
    lfsmake1 ncurses
    lfsmake1 bash
    lfsmake1 bzip2
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
    lfsmake1 cleanup-toolchain		PASS=2
    export PATH=$ORG_PATH
}

buildbase() {
    LOGFILE="$BASEDIR/log/_build.base.log"
    export LOGFILE
    lfsmake2 stage2
    lfsmake2 linux			KCFG="-headers"
    lfsmake2 man-pages
    lfsmake2 glibc
    lfsmake2 tzdata
    lfsmake2 cleanup-toolchain		PASS=3
    lfsmake2 zlib
    lfsmake2 binutils
    lfsmake2 gmp
    lfsmake2 gmp-compat
    lfsmake2 mpfr
    lfsmake2 file
    lfsmake2 gcc
    lfsmake2 sed
    lfsmake2 berkeley
    lfsmake2 coreutils
    lfsmake2 iana-etc
    lfsmake2 m4
    lfsmake2 bison
    lfsmake2 ncurses
    lfsmake2 procps
    lfsmake2 libtool
    lfsmake2 perl
    lfsmake2 readline
    lfsmake2 readline-compat
    lfsmake2 pcre
    lfsmake2 pcre-compat
    lfsmake2 autoconf
    lfsmake2 automake
    lfsmake2 bash
    lfsmake2 bzip2
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
    lfsmake2 inetutils
    lfsmake2 iproute2
    lfsmake2 jwhois
    lfsmake2 kbd
    lfsmake2 less
    lfsmake2 make
    lfsmake2 man
    lfsmake2 mktemp
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
    lfsmake2 grub
}

buildipfire() {
  LOGFILE="$BASEDIR/log/_build.ipfire.log"
  export LOGFILE
  ipfiremake configroot
  ipfiremake backup
  ipfiremake bind
  ipfiremake dhcp
  ipfiremake dhcpcd
  ipfiremake libusb
  ipfiremake libusbx
  ipfiremake libpcap
  ipfiremake ppp
  ipfiremake pptp
  ipfiremake unzip
  ipfiremake which
  ipfiremake linux-firmware
  ipfiremake dvb-firmwares
  ipfiremake zd1211-firmware
  ipfiremake rpi-firmware
  ipfiremake bc
  ipfiremake u-boot

  if [ "${MACHINE_TYPE}" != "arm" ]; then

    # x86-pae (Native and new XEN) kernel build
    ipfiremake linux			KCFG="-pae"
#    ipfiremake kvm-kmod			KCFG="-pae"
#    ipfiremake v4l-dvb			KCFG="-pae"
#    ipfiremake mISDN			KCFG="-pae"
    ipfiremake cryptodev		KCFG="-pae"
#    ipfiremake compat-drivers		KCFG="-pae"
#    ipfiremake r8169			KCFG="-pae"
#    ipfiremake r8168			KCFG="-pae"
#    ipfiremake r8101			KCFG="-pae"
#    ipfiremake e1000e			KCFG="-pae"
#    ipfiremake igb			KCFG="-pae"

    # x86 kernel build
    ipfiremake linux			KCFG=""
#    ipfiremake kvm-kmod			KCFG=""
#    ipfiremake v4l-dvb			KCFG=""
#    ipfiremake mISDN			KCFG=""
    ipfiremake cryptodev		KCFG=""
#    ipfiremake compat-drivers		KCFG=""
#    ipfiremake r8169			KCFG=""
#    ipfiremake r8168			KCFG=""
#    ipfiremake r8101			KCFG=""
#    ipfiremake e1000e			KCFG=""
#    ipfiremake igb			KCFG=""

  else
    # arm-rpi (Raspberry Pi) kernel build
    ipfiremake linux			KCFG="-rpi"
#    ipfiremake v4l-dvb			KCFG="-rpi"
#    ipfiremake mISDN			KCFG="-rpi" NOPCI=1
    ipfiremake cryptodev		KCFG="-rpi"
#    ipfiremake compat-drivers		KCFG="-rpi"

    # arm multi platform (Panda, Wandboard ...) kernel build
    ipfiremake linux			KCFG="-multi"
    ipfiremake cryptodev		KCFG="-multi"

    # arm-kirkwood (Dreamplug, ICY-Box ...) kernel build
    ipfiremake linux			KCFG="-kirkwood"
#    ipfiremake v4l-dvb			KCFG="-kirkwood"
#    ipfiremake mISDN			KCFG="-kirkwood"
    ipfiremake cryptodev		KCFG="-kirkwood"
#    ipfiremake compat-drivers		KCFG="-kirkwood"
#    ipfiremake r8169			KCFG="-kirkwood"
#    ipfiremake r8168			KCFG="-kirkwood"
#    ipfiremake r8101			KCFG="-kirkwood"
#   ipfiremake e1000e			KCFG="-kirkwood"
#    ipfiremake igb			KCFG="-kirkwood"

  fi
  ipfiremake pkg-config
  ipfiremake linux-atm
  ipfiremake cpio
  ipfiremake dracut
  ipfiremake expat
  ipfiremake gdbm
  ipfiremake pam
  ipfiremake openssl
  ipfiremake openssl-compat
  ipfiremake curl
  ipfiremake tcl
  ipfiremake sqlite
  ipfiremake python
  ipfiremake fireinfo
  ipfiremake libnet
  ipfiremake libnl
  ipfiremake libidn
  ipfiremake nasm
  ipfiremake libjpeg
  ipfiremake libexif
  ipfiremake libpng
  ipfiremake libtiff
  ipfiremake libart
  ipfiremake freetype
  ipfiremake gd
  ipfiremake popt
  ipfiremake pcre
  ipfiremake slang
  ipfiremake newt
  ipfiremake attr
  ipfiremake acl
  ipfiremake libcap
  ipfiremake pciutils
  ipfiremake usbutils
  ipfiremake libxml2
  ipfiremake libxslt
  ipfiremake BerkeleyDB
  ipfiremake mysql
  ipfiremake cyrus-sasl
  ipfiremake openldap
  ipfiremake apache2
  ipfiremake php
  ipfiremake apache2			PASS=C
  ipfiremake jquery
  ipfiremake arping
  ipfiremake beep
  ipfiremake dvdrtools
  ipfiremake dnsmasq
  ipfiremake dosfstools
  ipfiremake reiserfsprogs
  ipfiremake xfsprogs
  ipfiremake sysfsutils
  ipfiremake fuse
  ipfiremake ntfs-3g
  ipfiremake ethtool
  ipfiremake ez-ipupdate
  ipfiremake fcron
  ipfiremake perl-GD
  ipfiremake GD-Graph
  ipfiremake GD-TextUtil
  ipfiremake gnupg
  ipfiremake hdparm
  ipfiremake sdparm
  ipfiremake mtools
  ipfiremake initscripts
  ipfiremake whatmask
  ipfiremake libmnl
  ipfiremake iptables
  ipfiremake conntrack-tools
  ipfiremake libupnp
  ipfiremake ipaddr
  ipfiremake iputils
  ipfiremake l7-protocols
  ipfiremake mISDNuser
  ipfiremake capi4k-utils
  ipfiremake hwdata
  ipfiremake logrotate
  ipfiremake logwatch
  ipfiremake misc-progs
  ipfiremake nano
  ipfiremake URI
  ipfiremake HTML-Tagset
  ipfiremake HTML-Parser
  ipfiremake HTML-Template
  ipfiremake Compress-Zlib
  ipfiremake Digest
  ipfiremake Digest-SHA1
  ipfiremake Digest-HMAC
  ipfiremake libwww-perl
  ipfiremake Net-DNS
  ipfiremake Net-IPv4Addr
  ipfiremake Net_SSLeay
  ipfiremake IO-Stringy
  ipfiremake IO-Socket-SSL
  ipfiremake Unix-Syslog
  ipfiremake Mail-Tools
  ipfiremake MIME-Tools
  ipfiremake Net-Server
  ipfiremake Convert-TNEF
  ipfiremake Convert-UUlib
  ipfiremake Archive-Tar
  ipfiremake Archive-Zip
  ipfiremake Text-Tabs+Wrap
  ipfiremake Locale-Country
  ipfiremake XML-Parser
  ipfiremake Crypt-PasswdMD5
  ipfiremake Net-Telnet
  ipfiremake python-setuptools
  ipfiremake python-clientform
  ipfiremake python-mechanize
  ipfiremake python-feedparser
  ipfiremake python-rssdler
  ipfiremake libffi
  ipfiremake glib
  ipfiremake GeoIP
  ipfiremake fwhits
  ipfiremake noip_updater
  ipfiremake ntp
  ipfiremake openssh
  ipfiremake fontconfig
  ipfiremake dejavu-fonts-ttf
  ipfiremake freefont
  ipfiremake pixman
  ipfiremake cairo
  ipfiremake pango
  ipfiremake rrdtool
  ipfiremake setserial
  ipfiremake setup
  ipfiremake libdnet
  ipfiremake daq
  ipfiremake snort
  ipfiremake oinkmaster
  ipfiremake squid
  ipfiremake squidguard
  ipfiremake calamaris
  ipfiremake tcpdump
  ipfiremake traceroute
  ipfiremake vlan
  ipfiremake wireless
  ipfiremake pakfire
  ipfiremake spandsp
  ipfiremake lzo
  ipfiremake openvpn
  ipfiremake pammysql
  ipfiremake mpage
  ipfiremake dbus
  ipfiremake cups
  ipfiremake ghostscript
  ipfiremake foomatic
  ipfiremake hplip
  ipfiremake cifs-utils
  ipfiremake samba
  ipfiremake sudo
  ipfiremake mc
  ipfiremake wget
  ipfiremake bridge-utils
  ipfiremake screen
  ipfiremake smartmontools
  ipfiremake htop
  ipfiremake postfix
  ipfiremake fetchmail
  ipfiremake cyrus-imapd
  ipfiremake openmailadmin
  ipfiremake clamav
  ipfiremake spamassassin
  ipfiremake amavisd
  ipfiremake alsa
  ipfiremake mpfire
  ipfiremake guardian
  ipfiremake libid3tag
  ipfiremake libmad
  ipfiremake libogg
  ipfiremake libvorbis
  ipfiremake libdvbpsi
  ipfiremake flac
  ipfiremake lame
  ipfiremake sox
  ipfiremake libshout
  ipfiremake xvid
  ipfiremake libmpeg2
  ipfiremake cmake
  ipfiremake gnump3d
  ipfiremake libsigc++
  ipfiremake libtorrent
  ipfiremake rtorrent
  ipfiremake rsync
  ipfiremake tcpwrapper
  ipfiremake libevent
  ipfiremake libevent2
  ipfiremake portmap
  ipfiremake nfs
  ipfiremake nmap
  ipfiremake ncftp
  ipfiremake etherwake
  ipfiremake bwm-ng
  ipfiremake tripwire
  ipfiremake sysstat
  ipfiremake vsftpd
  ipfiremake strongswan
  ipfiremake rng-tools
  ipfiremake lsof
  ipfiremake br2684ctl
  ipfiremake pcmciautils
  ipfiremake lm_sensors
  ipfiremake liboping
  ipfiremake collectd
  ipfiremake teamspeak
  ipfiremake elinks
  ipfiremake igmpproxy
  ipfiremake fbset
  ipfiremake sdl
  ipfiremake qemu
  ipfiremake sane
  ipfiremake netpbm
  ipfiremake phpSANE
  ipfiremake tunctl
  ipfiremake nagios
  ipfiremake nagios_nrpe
  ipfiremake ebtables
  ipfiremake directfb
  ipfiremake dfb++
  ipfiremake faad2
  ipfiremake ffmpeg
  ipfiremake vdr
  ipfiremake vdr_streamdev
  ipfiremake vdr_vnsiserver3
  ipfiremake vdr_epgsearch
  ipfiremake w_scan
  ipfiremake icecast
  ipfiremake icegenerator
  ipfiremake mpd
  ipfiremake libmpdclient
  ipfiremake mpc
  ipfiremake git
  ipfiremake squidclamav
  ipfiremake vnstat
  ipfiremake vnstati
  ipfiremake iw
  ipfiremake wpa_supplicant
  ipfiremake hostapd
  ipfiremake pycurl
  ipfiremake urlgrabber
  ipfiremake syslinux
  ipfiremake tftpd
  ipfiremake cpufrequtils
  ipfiremake bluetooth
  ipfiremake gutenprint
  ipfiremake apcupsd
  ipfiremake iperf
  ipfiremake netcat
  ipfiremake 7zip
  ipfiremake lynis
  ipfiremake streamripper
  ipfiremake sshfs
  ipfiremake taglib
  ipfiremake mediatomb
  ipfiremake sslh
  ipfiremake perl-gettext
  ipfiremake perl-Sort-Naturally
  ipfiremake vdradmin
  ipfiremake miau
  ipfiremake netsnmpd
  ipfiremake perl-DBI
  ipfiremake perl-DBD-mysql
  ipfiremake perl-DBD-SQLite
  ipfiremake perl-File-ReadBackwards
  ipfiremake perl-PDF-Create
  ipfiremake cacti
  ipfiremake icecc
  ipfiremake openvmtools
  ipfiremake nagiosql
  ipfiremake iftop
  ipfiremake motion
  ipfiremake joe
  ipfiremake nut
  ipfiremake watchdog
  ipfiremake libpri
  ipfiremake asterisk
  ipfiremake lcr
  ipfiremake usb_modeswitch
  ipfiremake usb_modeswitch_data
  ipfiremake zerofree
  ipfiremake mdadm
  ipfiremake pound
  ipfiremake minicom
  ipfiremake ddrescue
  ipfiremake imspector
  ipfiremake miniupnpd
  ipfiremake client175
  ipfiremake powertop
  ipfiremake parted
  ipfiremake swig
  ipfiremake python-m2crypto
  ipfiremake wireless-regdb
  ipfiremake crda
  ipfiremake libsolv
  ipfiremake python-distutils-extra
  ipfiremake python-lzma
  ipfiremake python-progressbar
  ipfiremake python-xattr
  ipfiremake intltool
  ipfiremake transmission
  ipfiremake dpfhack
  ipfiremake lcd4linux
  ipfiremake mtr
  ipfiremake tcpick
  ipfiremake minidlna
  ipfiremake acpid
  ipfiremake fping
  ipfiremake telnet
  ipfiremake xinetd
  ipfiremake libgpg-error
  ipfiremake libassuan
  ipfiremake gpgme
  ipfiremake pygpgme
  ipfiremake pakfire3
  ipfiremake stress
  ipfiremake libstatgrab
  ipfiremake sarg
  ipfiremake check_mk_agent
  ipfiremake libdaemon
  ipfiremake avahi
  ipfiremake nginx
  ipfiremake sendEmail
  ipfiremake sysbench
  ipfiremake strace
  ipfiremake ipfire-netboot
  ipfiremake lcdproc
  ipfiremake bitstream
  ipfiremake multicat
  ipfiremake keepalived
  ipfiremake ipvsadm
  ipfiremake perl-Carp-Clan
  ipfiremake perl-Date-Calc
  ipfiremake perl-Date-Manip
  ipfiremake perl-File-Tail
  ipfiremake perl-TimeDate
  ipfiremake swatch
  ipfiremake tor
  ipfiremake arm
  ipfiremake wavemon
  ipfiremake iptraf-ng
  ipfiremake iotop
}

buildinstaller() {
  # Run installer scripts one by one
  LOGFILE="$BASEDIR/log/_build.installer.log"
  export LOGFILE
  ipfiremake memtest
  ipfiremake installer
  installmake strip
  ipfiremake initrd
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
  ipfiremake cdrom

  # Check if there is a loop device for building in virtual environments
  if [ $BUILD_IMAGES == 1 ] && ([ -e /dev/loop/0 ] || [ -e /dev/loop0 ]); then
	ipfiremake flash-images
  fi

  mv $LFS/install/images/{*.iso,*.tgz,*.img.gz,*.bz2} $BASEDIR >> $LOGFILE 2>&1

  ipfirepackages

  ipfiremake xen-image
  mv $LFS/install/images/*.bz2 $BASEDIR >> $LOGFILE 2>&1

  cd $BASEDIR
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
	ipfiremake core-updates

	local i
	for i in $(find $BASEDIR/config/rootfiles/packages{/${MACHINE},} -maxdepth 1 -type f); do
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

# See what we're supposed to do
case "$1" in 
build)
	clear
	PACKAGE=`ls -v -r $BASEDIR/cache/toolchains/$SNAME-$VERSION-toolchain-$TOOLCHAINVER-$MACHINE.tar.gz 2> /dev/null | head -n 1`
	#only restore on a clean disk
	if [ ! -f log/cleanup-toolchain-2-tools ]; then
		if [ ! -n "$PACKAGE" ]; then
			beautify build_stage "Full toolchain compilation - Native GCC: `gcc --version | grep GCC | awk {'print $3'}`"
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
	tools/checkwronginitlinks
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

				make -s -f $i LFS_BASEDIR=$BASEDIR MACHINE=$MACHINE \
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
			make -s -f $i LFS_BASEDIR=$BASEDIR MACHINE=$MACHINE \
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
	beautify build_stage "Toolchain compilation - Native GCC: `gcc --version | grep GCC | awk {'print $3'}`"
	buildtoolchain
	echo "`date -u '+%b %e %T'`: Create toolchain tar.gz for $MACHINE" | tee -a $LOGFILE
	test -d $BASEDIR/cache/toolchains || mkdir -p $BASEDIR/cache/toolchains
	cd $BASEDIR && tar -zc --exclude='log/_build.*.log' -f cache/toolchains/$SNAME-$VERSION-toolchain-$TOOLCHAINVER-$MACHINE.tar.gz \
		build/tools build/bin/sh log >> $LOGFILE
	md5sum cache/toolchains/$SNAME-$VERSION-toolchain-$TOOLCHAINVER-$MACHINE.tar.gz \
		> cache/toolchains/$SNAME-$VERSION-toolchain-$TOOLCHAINVER-$MACHINE.md5
	stdumount
	;;
gettoolchain)
	# arbitrary name to be updated in case of new toolchain package upload
	PACKAGE=$SNAME-$VERSION-toolchain-$TOOLCHAINVER-$MACHINE
	if [ ! -f $BASEDIR/cache/toolchains/$PACKAGE.tar.gz ]; then
		URL_TOOLCHAIN=`grep URL_TOOLCHAIN lfs/Config | awk '{ print $3 }'`
		test -d $BASEDIR/cache/toolchains || mkdir -p $BASEDIR/cache/toolchains
		echo "`date -u '+%b %e %T'`: Load toolchain tar.gz for $MACHINE" | tee -a $LOGFILE
		cd $BASEDIR/cache/toolchains
		wget -U "IPFireSourceGrabber/2.x" $URL_TOOLCHAIN/$PACKAGE.tar.gz $URL_TOOLCHAIN/$PACKAGE.md5 >& /dev/null
		if [ $? -ne 0 ]; then
			echo "`date -u '+%b %e %T'`: error downloading $PACKAGE toolchain for $MACHINE machine" | tee -a $LOGFILE
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
	echo -ne "`date -u '+%b %e %T'`: Build sources iso for $MACHINE" | tee -a $LOGFILE
	chroot $LFS /tools/bin/env -i   HOME=/root \
	TERM=$TERM PS1='\u:\w\$ ' \
	PATH=/usr/local/bin:/bin:/usr/bin:/sbin:/usr/sbin \
	VERSION=$VERSION NAME="$NAME" SNAME="$SNAME" MACHINE=$MACHINE \
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
