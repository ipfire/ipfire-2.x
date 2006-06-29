#!/bin/bash
#
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
# Copyright (C) 2006 IPFire-Team <entwickler@ipfire.org>.                  #
#                                                                          #
############################################################################
#

  NAME="IPFire"			# Software name
  SNAME="ipfire"			# Short name
  VERSION="1.4"			# Version number
  SLOGAN="We secure your network"	# Software slogan
  CONFIG_ROOT=/var/ipfire		# Configuration rootdir
  NICE=10
  MAX_RETRIES=3			# prefetch/check loop
  KVER=`grep --max-count=1 VER lfs/linux | awk '{ print $3 }'`
  MACHINE=`uname -m`

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

  if [ 'x86_64' = $MACHINE -o 'i686' = $MACHINE -o 'i586' = $MACHINE -o 'i486' = $MACHINE -o 'i386' = $MACHINE ]; then
	echo "`date -u '+%b %e %T'`: Machine is ix86 (or equivalent)" | tee -a $LOGFILE
	MACHINE=i386
	BUILDTARGET=i386-pc-linux-gnu
	CFLAGS="-O2 -mcpu=i386 -march=i386 -pipe -fomit-frame-pointer"
	CXXFLAGS="-O2 -mcpu=i386 -march=i386 -pipe -fomit-frame-pointer"
  elif [ 'alpha' = $MACHINE ]; then
	echo "`date -u '+%b %e %T'`: Machine is Alpha AXP" | tee -a $LOGFILE
	BUILDTARGET=alpha-unknown-linux-gnu
	CFLAGS="-O2 -mcpu=ev4 -mieee -pipe"
	CXXFLAGS="-O2 -mcpu=ev4 -mieee -pipe"
  else
	echo "`date -u '+%b %e %T'`: Can't determine your architecture - $MACHINE" | tee -a $LOGFILE
	exit 1
  fi

# Define immediately
stdumount() {
	umount $BASEDIR/build/dev/pts		2>/dev/null;
	umount $BASEDIR/build/proc			2>/dev/null;
	umount $BASEDIR/build/install/mnt		2>/dev/null;
	umount $BASEDIR/build/usr/src/cache	2>/dev/null;
	umount $BASEDIR/build/usr/src/ccache	2>/dev/null;
	umount $BASEDIR/build/usr/src/config	2>/dev/null;
	umount $BASEDIR/build/usr/src/doc		2>/dev/null;
	umount $BASEDIR/build/usr/src/html		2>/dev/null;
	umount $BASEDIR/build/usr/src/langs	2>/dev/null;
	umount $BASEDIR/build/usr/src/lfs		2>/dev/null;
	umount $BASEDIR/build/usr/src/log		2>/dev/null;
	umount $BASEDIR/build/usr/src/src		2>/dev/null;
}

exiterror() {
	stdumount
	for i in `seq 0 7`; do
	    if ( losetup /dev/loop${i} 2>/dev/null | grep -q "/install/images" ); then
		losetup -d /dev/loop${i} 2>/dev/null
	    fi;
	done
	echo "ERROR: $*"
	echo "       Check $LOGFILE for errors if applicable"
	exit 1
}

entershell() {
	if [ ! -e $BASEDIR/build/usr/src/lfs/ ]; then
		exiterror "No such file or directory: $BASEDIR/build/usr/src/lfs/"
	fi
	echo "Entering to a shell inside LFS chroot, go out with exit"
	chroot $LFS /tools/bin/env -i HOME=/root TERM=$TERM PS1='\u:\w\$ ' \
		PATH=/usr/local/bin:/bin:/usr/bin:/sbin:/usr/sbin:/tools/bin \
		VERSION=$VERSION CONFIG_ROOT=$CONFIG_ROOT \
		NAME="$NAME" SNAME="$SNAME" SLOGAN="$SLOGAN" \
		CFLAGS="$CFLAGS" CXXFLAGS="$CXXFLAGS" \
		CCACHE_DIR=/usr/src/ccache \
		CCACHE_HASHDIR=1 \
		KVER=$KVER \
		BUILDTARGET="$BUILDTARGET" MACHINE="$MACHINE" \
		KGCC="ccache /usr/bin/gcc" \
		/tools/bin/bash
	if [ $? -ne 0 ]; then
			exiterror "chroot error"
	else
		stdumount
	fi
}

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
    echo "`date -u '+%b %e %T'`: Resetting our nice level to $NICE" | tee -a $LOGFILE
    renice $NICE $$ > /dev/null
    if [ `nice` != "$NICE" ]; then
	exiterror "Failed to set correct nice level"
    fi

    ############################################################################
    #                                                                          #
    # Checking if running as root user                                         #
    #                                                                          #
    ############################################################################
    echo "`date -u '+%b %e %T'`: Checking if we're running as root user" | tee -a $LOGFILE
    if [ `id -u` != 0 ]; then
	exiterror "Not building as root"
    fi


    ############################################################################
    #                                                                          #
    # Checking for necessary temporary space                                   #
    #                                                                          #
    ############################################################################
    echo "`date -u '+%b %e %T'`: Checking for necessary space on disk $BASE_DEV" | tee -a $LOGFILE
    BASE_DEV=`df -P -k $BASEDIR | tail -n 1 | awk '{ print $1 }'`
    BASE_ASPACE=`df -P -k $BASEDIR | tail -n 1 | awk '{ print $4 }'`
    if (( 2202000 > $BASE_ASPACE )); then
	BASE_USPACE=`du -skx $BASEDIR | awk '{print $1}'`
	if (( 2202000 - $BASE_USPACE > $BASE_ASPACE )); then
		exiterror "Not enough temporary space available, need at least 2.1GB on $BASE_DEV"
	fi
    fi

    ############################################################################
    #                                                                          #
    # Building Linux From Scratch system                                       #
    #                                                                          #
    ############################################################################
    echo "`date -u '+%b %e %T'`: Building Linux From Scratch system" | tee -a $LOGFILE

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
    export LFS LC_ALL CFLAGS CXXFLAGS
    unset CC CXX CPP LD_LIBRARY_PATH LD_PRELOAD

    # Make some extra directories
    mkdir -p $BASEDIR/build/{tools,etc,usr/src} 2>/dev/null
    mkdir -p $BASEDIR/{cache,ccache} 2>/dev/null
    mkdir -p $BASEDIR/build/dev/pts $BASEDIR/build/proc $BASEDIR/build/usr/src/{cache,config,doc,html,langs,lfs,log,src,ccache}

    # Make all sources and proc available under lfs build
    mount --bind /dev/pts        $BASEDIR/build/dev/pts
    mount --bind /proc           $BASEDIR/build/proc
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
    export CCACHE_HASHDIR=1

    # Remove pre-install list of installed files in case user erase some files before rebuild
    rm -f $BASEDIR/build/usr/src/lsalr 2>/dev/null
}


############################################################################
#                                                                          #
# Necessary shell functions                                                #
#                                                                          #
############################################################################
lfsmake1() {
	if [ -f $BASEDIR/lfs/$1 ]; then
		echo "`date -u '+%b %e %T'`: Building $*" | tee -a $LOGFILE
		cd $BASEDIR/lfs && make -s -f $* LFS_BASEDIR=$BASEDIR MESSAGE="$1\t " download  >> $LOGFILE 2>&1
		if [ $? -ne 0 ]; then
			exiterror "Download error in $1"
		fi
		cd $BASEDIR/lfs && make -s -f $* LFS_BASEDIR=$BASEDIR MESSAGE="$1\t md5sum" md5  >> $LOGFILE 2>&1
		if [ $? -ne 0 ]; then
			exiterror "md5sum error in $1, check file in cache or signature"
		fi
		cd $BASEDIR/lfs && make -f $* 	BUILDTARGET=$BUILDTARGET \
						MACHINE=$MACHINE \
						LFS_BASEDIR=$BASEDIR \
						ROOT=$LFS \
						KVER=$KVER \
						install >> $LOGFILE 2>&1
		if [ $? -ne 0 ]; then
			exiterror "Building $*";
		fi
	else
		exiterror "No such file or directory: $BASEDIR/$1"
	fi
	return 0
}

lfsmake2() {
	if [ -f $BASEDIR/build/usr/src/lfs/$1 ]; then
		echo "`date -u '+%b %e %T'`: Building $*" | tee -a $LOGFILE
		cd $BASEDIR/lfs && make -s -f $* LFS_BASEDIR=$BASEDIR MESSAGE="$1\t " download  >> $LOGFILE 2>&1
		if [ $? -ne 0 ]; then
			exiterror "Download error in $1"
		fi
		cd $BASEDIR/lfs && make -s -f $* LFS_BASEDIR=$BASEDIR MESSAGE="$1\t md5sum" md5  >> $LOGFILE 2>&1
		if [ $? -ne 0 ]; then
			exiterror "md5sum error in $1, check file in cache or signature"
		fi
		chroot $LFS /tools/bin/env -i 	HOME=/root \
						TERM=$TERM PS1='\u:\w\$ ' \
						PATH=/usr/local/bin:/bin:/usr/bin:/sbin:/usr/sbin:/tools/bin \
						VERSION=$VERSION \
						CONFIG_ROOT=$CONFIG_ROOT \
						NAME="$NAME" SNAME="$SNAME" SLOGAN="$SLOGAN" \
						CFLAGS="$CFLAGS" CXXFLAGS="$CXXFLAGS" \
						CCACHE_DIR=/usr/src/ccache CCACHE_HASHDIR=1 \
						KVER=$KVER \
						BUILDTARGET="$BUILDTARGET" MACHINE="$MACHINE" \
		    /tools/bin/bash -x -c "cd /usr/src/lfs && \
		    make -f $* LFS_BASEDIR=/usr/src install" >>$LOGFILE 2>&1
		if [ $? -ne 0 ]; then
			exiterror "Building $*"
		fi
	else
		exiterror "No such file or directory: $BASEDIR/build/usr/src/lfs/$1"
	fi
	return 0
}

ipcopmake() {
	if [ -f $BASEDIR/build/usr/src/lfs/$1 ]; then
		echo "`date -u '+%b %e %T'`: Building $*" | tee -a $LOGFILE
		cd $BASEDIR/lfs && make -s -f $* LFS_BASEDIR=$BASEDIR MESSAGE="$1\t " download  >> $LOGFILE 2>&1
		if [ $? -ne 0 ]; then
			exiterror "Download error in $1"
		fi
		cd $BASEDIR/lfs && make -s -f $* LFS_BASEDIR=$BASEDIR MESSAGE="$1\t md5sum" md5  >> $LOGFILE 2>&1
		if [ $? -ne 0 ]; then
			exiterror "md5sum error in $1, check file in cache or signature"
		fi
		chroot $LFS /tools/bin/env -i 	HOME=/root \
						TERM=$TERM PS1='\u:\w\$ ' \
						PATH=/usr/local/bin:/bin:/usr/bin:/sbin:/usr/sbin \
						VERSION=$VERSION \
						CONFIG_ROOT=$CONFIG_ROOT \
						NAME="$NAME" SNAME="$SNAME" SLOGAN="$SLOGAN" \
						CFLAGS="$CFLAGS" CXXFLAGS="$CXXFLAGS" \
						CCACHE_DIR=/usr/src/ccache CCACHE_HASHDIR=1 \
						KVER=$KVER \
						BUILDTARGET="$BUILDTARGET" MACHINE="$MACHINE" \
		    /bin/bash -x -c "cd /usr/src/lfs && \
		    make -f $* LFS_BASEDIR=/usr/src install" >>$LOGFILE 2>&1
		if [ $? -ne 0 ]; then
			exiterror "Building $*"
		fi
	else
		exiterror "No such file or directory: $BASEDIR/build/usr/src/lfs/$1"
	fi
	return 0
}

ipfiredist() {
	if [ -f $BASEDIR/build/usr/src/lfs/$1 ]; then
#	   if [ ! `ls -w1 $BASEDIR/packages/*.tar.gz | grep $1` ]; then
		echo "`date -u '+%b %e %T'`: Packaging $1" | tee -a $LOGFILE
		chroot $LFS /tools/bin/env -i 	HOME=/root \
						TERM=$TERM PS1='\u:\w\$ ' \
						PATH=/usr/local/bin:/bin:/usr/bin:/sbin:/usr/sbin \
						VERSION=$VERSION \
						CONFIG_ROOT=$CONFIG_ROOT \
						NAME="$NAME" SNAME="$SNAME" SLOGAN="$SLOGAN" \
						CFLAGS="$CFLAGS" CXXFLAGS="$CXXFLAGS" \
						CCACHE_DIR=/usr/src/ccache CCACHE_HASHDIR=1 \
						KVER=$KVER \
						BUILDTARGET="$BUILDTARGET" MACHINE="$MACHINE" \
		    /bin/bash -x -c "cd /usr/src/lfs && \
		    make -f $1 LFS_BASEDIR=/usr/src dist" >>$LOGFILE 2>&1
		if [ $? -ne 0 ]; then
			exiterror "Packaging $1"
		fi
#	   else
#		echo "`date -u '+%b %e %T'`: Packaging: The package $1 already exists"
#	   fi
	else
		exiterror "No such file or directory: $BASEDIR/build/usr/src/lfs/$1"
	fi
	return 0
}


installmake() {
	if [ -f $BASEDIR/build/usr/src/lfs/$1 ]; then
		echo "`date -u '+%b %e %T'`: Building $*" | tee -a $LOGFILE
		cd $BASEDIR/lfs && make -s -f $* LFS_BASEDIR=$BASEDIR MESSAGE="$1\t " download  >> $LOGFILE 2>&1
		if [ $? -ne 0 ]; then
			exiterror "Download error in $1"
		fi
		cd $BASEDIR/lfs && make -s -f $* LFS_BASEDIR=$BASEDIR MESSAGE="$1\t md5sum" md5  >> $LOGFILE 2>&1
		if [ $? -ne 0 ]; then
			exiterror "md5sum error in $1, check file in cache or signature"
		fi
		chroot $LFS /tools/bin/env -i 	HOME=/root \
						TERM=$TERM PS1='\u:\w\$ ' \
						PATH=/usr/local/bin:/opt/$MACHINE-uClibc/usr/bin:/bin:/usr/bin:/sbin:/usr/sbin \
						VERSION=$VERSION \
						CONFIG_ROOT=$CONFIG_ROOT \
						LFS_PASS="install" \
						NAME="$NAME" SNAME="$SNAME" SLOGAN="$SLOGAN" \
						CFLAGS="-Os" CXXFLAGS="-Os" \
						CCACHE_DIR=/usr/src/ccache CCACHE_HASHDIR=1 \
						KVER=$KVER \
						BUILDTARGET="$BUILDTARGET" MACHINE="$MACHINE" \
		    /bin/bash -x -c "cd /usr/src/lfs && \
		    make -f $* LFS_BASEDIR=/usr/src install" >>$LOGFILE 2>&1
		if [ $? -ne 0 ]; then
			exiterror "Building $*"
		fi
	else
		exiterror "No such file or directory: $BASEDIR/build/usr/src/lfs/$1"
	fi
	return 0
}

buildtoolchain() {
    LOGFILE="$BASEDIR/log/_build.toolchain.log"
    export LOGFILE
    echo -ne "`date -u '+%b %e %T'`: Stage1 toolchain build \n" | tee -a $LOGFILE
    # Build sed now, as we use some extensions
    ORG_PATH=$PATH
    NATIVEGCC=`gcc --version | grep GCC | awk {'print $3'}`
    export NATIVEGCC GCCmajor=${NATIVEGCC:0:1} GCCminor=${NATIVEGCC:2:1} GCCrelease=${NATIVEGCC:4:1}
    lfsmake1 ccache
    lfsmake1 sed	LFS_PASS=1
    lfsmake1 m4		LFS_PASS=1
    lfsmake1 bison	LFS_PASS=1
    lfsmake1 flex	LFS_PASS=1
    lfsmake1 binutils   LFS_PASS=1
    lfsmake1 gcc        LFS_PASS=1
    export PATH=$BASEDIR/build/usr/local/bin:$BASEDIR/build/tools/bin:$PATH
    
    lfsmake1 linux
    lfsmake1 tcl
    lfsmake1 expect
    lfsmake1 glibc
    lfsmake1 dejagnu
    lfsmake1 gcc        LFS_PASS=2
    lfsmake1 binutils   LFS_PASS=2
    lfsmake1 gawk
    lfsmake1 coreutils
    lfsmake1 bzip2
    lfsmake1 gzip
    lfsmake1 diffutils
    lfsmake1 findutils
    lfsmake1 make
    lfsmake1 grep
    lfsmake1 sed	LFS_PASS=2
    lfsmake1 m4		LFS_PASS=2
    lfsmake1 bison	LFS_PASS=2
    lfsmake1 flex	LFS_PASS=2
    lfsmake1 gettext
    lfsmake1 ncurses
    lfsmake1 patch
    lfsmake1 tar
    lfsmake1 texinfo
    lfsmake1 bash
    lfsmake1 util-linux
    lfsmake1 perl
    export PATH=$ORG_PATH
}

buildbase() {
    LOGFILE="$BASEDIR/log/_build.base.log"
    export LOGFILE
    echo -ne "`date -u '+%b %e %T'`: Stage2 linux base build \n" | tee -a $LOGFILE
    # Run LFS dynamic binary creation scripts one by one
    lfsmake2 stage2
    lfsmake2 makedev
    lfsmake2 linux
    lfsmake2 man-pages
    lfsmake2 glibc
    lfsmake2 binutils
    lfsmake2 gcc
    lfsmake2 coreutils
    lfsmake2 zlib
    lfsmake2 mktemp
    lfsmake2 iana-etc
    lfsmake2 findutils
    lfsmake2 gawk
    lfsmake2 ncurses
    lfsmake2 vim
    lfsmake2 m4
    lfsmake2 bison
    lfsmake2 less
    lfsmake2 groff
    lfsmake2 sed
    lfsmake2 flex
    lfsmake2 gettext
    lfsmake2 net-tools
    lfsmake2 inetutils
    lfsmake2 perl
    lfsmake2 texinfo
    lfsmake2 autoconf
    lfsmake2 automake
    lfsmake2 bash
    lfsmake2 file
    lfsmake2 libtool
    lfsmake2 bzip2
    lfsmake2 diffutils
    lfsmake2 ed
    lfsmake2 kbd
    lfsmake2 e2fsprogs
    lfsmake2 grep
    if [ 'i386' = $MACHINE ]; then 
  	lfsmake2 grub
    elif [ 'alpha' = $MACHINE ]; then 
  	lfsmake2 aboot
    fi
    lfsmake2 gzip
    lfsmake2 man
    lfsmake2 make
    lfsmake2 modutils
    lfsmake2 patch
    lfsmake2 procinfo
    lfsmake2 procps
    lfsmake2 psmisc
    lfsmake2 shadow
    lfsmake2 sysklogd
    lfsmake2 sysvinit
    lfsmake2 tar
    lfsmake2 util-linux
}

buildipcop() {
  # Run IPFire make scripts one by one
  LOGFILE="$BASEDIR/log/_build.ipfire.log"
  export LOGFILE
  echo -ne "`date -u '+%b %e %T'`: Stage3 $NAME build \n" | tee -a $LOGFILE

  # Build these first as some of the kernel packages below rely on 
  # these for some of their client program functionality 
  ipcopmake configroot
  ipcopmake dhcp
  ipcopmake dhcpcd
  ipcopmake libusb
  ipcopmake libpcap
  ipcopmake linux-atm
  ipcopmake ppp
  ipcopmake rp-pppoe
  ipcopmake unzip
  # Do SMP now
  if [ 'i386' = $MACHINE ]; then 
  	# abuse the SMP flag, and make an minimal installer kernel first
	# so that the boot floppy always works.....
  	ipcopmake linux 	LFS_PASS=ipfire SMP=installer
  	ipcopmake linux 	LFS_PASS=ipfire SMP=1
  	ipcopmake 3cp4218 	SMP=1
  	ipcopmake amedyn 	SMP=1
  	ipcopmake cxacru 	SMP=1
  	ipcopmake eagle 	SMP=1

  	# These are here because they have i386 only binary libraries
	# included in the package.
  	ipcopmake cnx_pci 	SMP=1
 	ipcopmake fcdsl 	SMP=1
 	ipcopmake fcdsl2 	SMP=1
 	ipcopmake fcdslsl 	SMP=1
 	ipcopmake fcdslusb 	SMP=1
 	ipcopmake fcdslslusb 	SMP=1
	ipcopmake fcpci	SMP=1
	ipcopmake fcclassic	SMP=1
	ipcopmake pulsar 	SMP=1
  	ipcopmake unicorn 	SMP=1
  fi

  ipcopmake linux	LFS_PASS=ipfire
  ipcopmake 3cp4218 	
  ipcopmake amedyn 	
  ipcopmake cxacru 	
  ipcopmake eciadsl 	
  ipcopmake eagle 	
  ipcopmake speedtouch 	
  if [ 'i386' = $MACHINE ]; then 
  	# These are here because they have i386 only binary libraries
	# included in the package.
  	ipcopmake cnx_pci 	
 	ipcopmake fcdsl 	
 	ipcopmake fcdsl2 	
 	ipcopmake fcdslsl 	
 	ipcopmake fcdslusb 	
 	ipcopmake fcdslslusb 
  	ipcopmake fcpci
  	ipcopmake fcclassic
	ipcopmake pulsar 	
  	ipcopmake unicorn 	
  fi

  ipcopmake pcmcia-cs
  ipcopmake expat
  ipcopmake gdbm
  ipcopmake gmp
  ipcopmake openssl
  ipcopmake python
  ipcopmake libnet
  ipcopmake libpng
  ipcopmake gd
  ipcopmake popt
  ipcopmake slang
  ipcopmake newt
  ipcopmake libcap
  ipcopmake pciutils
  ipcopmake pcre
  ipcopmake apache
  ipcopmake arping
  ipcopmake beep
  ipcopmake bind
  ipcopmake capi4k-utils
  ipcopmake cdrtools
  ipcopmake dnsmasq
  ipcopmake dosfstools
  ipcopmake ethtool
  ipcopmake ez-ipupdate
  ipcopmake fcron
  ipcopmake perl-GD
  ipcopmake gnupg
  ipcopmake hdparm
  ipcopmake ibod
  ipcopmake initscripts
  ipcopmake iptables
  ipcopmake ipac-ng
  ipcopmake ipaddr
  ipcopmake iproute2
  ipcopmake iptstate
  ipcopmake iputils
  ipcopmake l7-protocols
  ipcopmake isapnptools
  ipcopmake isdn4k-utils
  ipcopmake kudzu
  ipcopmake logrotate
  ipcopmake logwatch
  ipcopmake mingetty
  ipcopmake misc-progs
  ipcopmake mtools
  ipcopmake nano
  ipcopmake nash
  ipcopmake nasm
  ipcopmake URI
  ipcopmake HTML-Tagset
  ipcopmake HTML-Parser
  ipcopmake Compress-Zlib
  ipcopmake Digest
  ipcopmake Digest-SHA1
  ipcopmake Digest-HMAC
  ipcopmake libwww-perl
  ipcopmake Net-DNS
  ipcopmake Net-IPv4Addr
  ipcopmake Net_SSLeay
  ipcopmake IO-Stringy
  ipcopmake Unix-Syslog
  ipcopmake Mail-Tools
  ipcopmake MIME-Tools
  ipcopmake Net-Server
  ipcopmake Convert-TNEF
  ipcopmake Convert-UUlib
  ipcopmake Archive-Tar
  ipcopmake Archive-Zip
  ipcopmake Text-Tabs+Wrap
  ipcopmake Locale-Country
  ipcopmake GeoIP
  ipcopmake fwhits
  ipcopmake berkeley
  ipcopmake BerkeleyDB ## The Perl module
  ipcopmake noip_updater
  ipcopmake ntp
  ipcopmake oinkmaster
  ipcopmake openssh
  ipcopmake openswan
  ipcopmake pptpclient
  ipcopmake rrdtool
  ipcopmake setserial
  ipcopmake setup
  ipcopmake snort
  #ipcopmake speedycgi
  ipcopmake saslauthd PASS=1
  ipcopmake openldap
  ipcopmake squid
  ipcopmake squid-graph
  ipcopmake squidguard
  ipcopmake tcpdump
  ipcopmake traceroute
  ipcopmake vlan
  #ipcopmake wireless
  ipcopmake libsafe
  ipcopmake 3c5x9setup
#  echo -ne "`date -u '+%b %e %T'`: Building ### IPFire modules ### \n" | tee -a $LOGFILE
  ipcopmake pakfire
  ipcopmake startscripts
## Zuerst die Libs und dann die Programme. Ordnung muss sein!
  ipcopmake java
  ipcopmake libtiff
  ipcopmake libjpeg
  ipcopmake libxml2
  ipcopmake spandsp
  ipcopmake lzo
  ipcopmake openvpn
  ipcopmake pkg-config
  ipcopmake glib
  ipcopmake xampp
  ipcopmake pam
  ipcopmake pammysql
  ipcopmake saslauthd PASS=2
  ipcopmake xinetd
  ipcopmake ghostscript
  ipcopmake cups
#  ipcopmake lpd ## Im Moment aus, da CUPS vorhanden ist.
  ipcopmake samba
  ipcopmake sudo
  ipcopmake mc
  ipcopmake pwlib
  ipcopmake openh323
  ipcopmake wget
  ipcopmake wput
  ipcopmake bridge-utils
  ipcopmake screen
  ipcopmake hddtemp
  ipcopmake htop
  ipcopmake lynx
  echo -ne "`date -u '+%b %e %T'`: Building ### Mailserver ### \n" | tee -a $LOGFILE
  ipcopmake postfix
  ipcopmake procmail
  ipcopmake fetchmail
  ipcopmake cyrusimap
  ipcopmake web-cyradm
  ipcopmake mailx
  ipcopmake clamav
  ipcopmake razor
  ipcopmake spamassassin
#  ipcopmake amavisd
  echo -ne "`date -u '+%b %e %T'`: Building ### VoIP-Server ### \n" | tee -a $LOGFILE
  ipcopmake stund
  ipcopmake asterisk
  ipcopmake mpg123
  echo -ne "`date -u '+%b %e %T'`: Building ### MP3-Server ### \n" | tee -a $LOGFILE
  ipcopmake lame
  ipcopmake gnump3d
  echo -ne "`date -u '+%b %e %T'`: Building ### P2P-Clients ### \n" | tee -a $LOGFILE
  ipcopmake applejuice
  ipcopmake edonkeyclc
#  ipcopmake sane
  echo -ne "`date -u '+%b %e %T'`: Building ### Net-Tools ### \n" | tee -a $LOGFILE
  ipcopmake ntop
#  ipcopmake rsync
  ipcopmake tcpwrapper
  ipcopmake portmap
  ipcopmake nfs
  ipcopmake nmap
  ipcopmake iftop
  ipcopmake ncftp
  ipcopmake cftp
  ipcopmake etherwake
  ipcopmake ethereal
#  ipcopmake stunnel # Ausgeschaltet, weil wir es doch nicht nutzen
}

buildinstaller() {
  # Run installer scripts one by one
  LOGFILE="$BASEDIR/log/_build.installer.log"
  export LOGFILE
  echo -ne "`date -u '+%b %e %T'`: Stage4 installer build \n" | tee -a $LOGFILE
  if [ 'i386' = $MACHINE ]; then 
  	ipcopmake syslinux
	ipcopmake as86
	ipcopmake mbr
  	ipcopmake uClibc
  fi
  installmake busybox
  installmake sysvinit
  installmake e2fsprogs
  installmake misc-progs
  installmake slang
  installmake util-linux
  installmake newt
  installmake pciutils
  installmake pcmcia-cs
  installmake kbd
  installmake installer
  installmake scsi.img
  installmake driver.img
  installmake initrd
  installmake boot.img
}

buildpackages() {
  LOGFILE="$BASEDIR/log/_build.packages.log"
  export LOGFILE
  echo "... see detailed log in _build.*.log files" >> $LOGFILE
  echo -ne "`date -u '+%b %e %T'`: Stage5 packages build \n" | tee -a $LOGFILE
  # Strip files
  echo "`date -u '+%b %e %T'`: Stripping files" | tee -a $LOGFILE
  find $LFS/lib $LFS/usr/lib $LFS/usr/share/rrdtool-* $LFS/install ! -type l \( -name '*.so' -o -name '*.so[\.0-9]*' \) \
	! -name 'libc.so' ! -name 'libpthread.so' ! -name 'libcrypto.so.0.9.7.sha1' \
	 -exec $LFS/tools/bin/strip --strip-all {} \; >> $LOGFILE 2>&1
  # add -ls before -exec if you want to verify what files are stripped

  find $LFS/{,s}bin $LFS/usr/{,s}bin $LFS/usr/local/{,s}bin ! -type l \
	-exec file {} \; | grep " ELF " | cut -f1 -d ':' | xargs $LFS/tools/bin/strip --strip-all >> $LOGFILE 2>&1
  # there add -v to strip to verify

  if [ 'i386' = $MACHINE ]; then
	# Create fcdsl packages
	echo "`date -u '+%b %e %T'`: Building fcdsl tgz" | tee -a $LOGFILE
	cp $LFS/install/images/fcdsl/license.txt $LFS  >> $LOGFILE 2>&1
	touch $LFS/var/run/{need-depmod-$KVER,need-depmod-$KVER-smp}
	cd $LFS && tar cvfz $LFS/install/images/$SNAME-fcdsl-$VERSION.$MACHINE.tgz \
		lib/modules/$KVER/misc/fcdsl*.o.gz \
		lib/modules/$KVER-smp/misc/fcdsl*.o.gz \
		usr/lib/isdn/{fds?base.bin,fd?ubase.frm} \
		etc/fcdsl/fcdsl*.conf \
		etc/drdsl/{drdsl,drdsl.ini} \
		license.txt \
		var/run/{need-depmod-$KVER,need-depmod-$KVER-smp} >> $LOGFILE 2>&1
	rm -f $LFS/license.txt >> $LOGFILE 2>&1
	cd $BASEDIR
  fi
  
  # Generating list of packages used
  echo "`date -u '+%b %e %T'`: Generating packages list from logs" | tee -a $LOGFILE
  rm -f $BASEDIR/doc/packages-list
  for i in `ls -1tr $BASEDIR/log/[^_]*`; do
	if [ "$i" != "$BASEDIR/log/FILES" -a -n $i ]; then
		echo "  * `basename $i`" >>$BASEDIR/doc/packages-list
	fi
  done
  echo "====== List of softwares used to build $NAME Version: $VERSION ======" > $BASEDIR/doc/packages-list.txt
  grep -v 'configroot$\|img$\|initrd$\|initscripts$\|installer$\|install$\|ipcop$\|setup$\|pakfire$\|stage2$\|smp$\|tools$\|tools1$\|tools2$' \
	$BASEDIR/doc/packages-list | sort >> $BASEDIR/doc/packages-list.txt
  rm -f $BASEDIR/doc/packages-list
  # packages-list.txt is ready to be displayed for wiki page

  # Create ISO for CDRom and USB-superfloppy
  ipcopmake cdrom
  rm -f $LFS/install/images/*usb*
  cp $LFS/install/images/{*.iso,*.tgz} $BASEDIR >> $LOGFILE 2>&1

  ipfirepackages

  # Cleanup
  stdumount
  rm -rf $BASEDIR/build/tmp/*

  # Generating total list of files
  echo "`date -u '+%b %e %T'`: Generating files list from logs" | tee -a $LOGFILE
  rm -f $BASEDIR/log/FILES
  for i in `ls -1tr $BASEDIR/log/[^_]*`; do
	if [ "$i" != "$BASEDIR/log/FILES" -a -n $i ]; then
		echo "##" >>$BASEDIR/log/FILES
		echo "## `basename $i`" >>$BASEDIR/log/FILES
		echo "##" >>$BASEDIR/log/FILES
		cat $i | sed "s%^\./%#%" | sort >> $BASEDIR/log/FILES
	fi
  done

  cd $PWD

}

ipfirepackages() {
  for i in `ls $BASEDIR/packages`; do
	touch $BASEDIR/build/install/packages/$i.empty
  done
  ipfiredist amavisd
  ipfiredist applejuice
  ipfiredist asterisk
  ipfiredist clamav
  ipfiredist cups
  ipfiredist cyrusimap
  ipfiredist fetchmail
  ipfiredist gnump3d
  ipfiredist java
  ipfiredist lame
  ipfiredist libtiff
  ipfiredist libxml2
  ipfiredist mailx
  ipfiredist nfs
  ipfiredist nmap
  ipfiredist ntop
  ipfiredist postfix
  ipfiredist procmail
  ipfiredist samba
  ipfiredist spamassassin
  ipfiredist web-cyradm
  ipfiredist xampp
  ipfiredist xinetd
  test -d $BASEDIR/packages || mkdir $BASEDIR/packages
  mv -f $LFS/install/packages/*.{tar.gz,md5} $BASEDIR/packages >> $LOGFILE 2>&1
  rm -rf  $BASEDIR/build/install/packages/*
}

# See what we're supposed to do
case "$1" in 
build)
	BUILDMACHINE=`uname -m`
	PACKAGE=`ls -v -r $BASEDIR/cache/$SNAME-1.4-toolchain-$BUILDMACHINE.tar.gz 2> /dev/null | head -n 1`
	#only restore on a clean disk
	if [ ! -f log/perl-*-tools ]; then
		if [ ! -n "$PACKAGE" ]; then
			echo "`date -u '+%b %e %T'`: Full toolchain compilation" | tee -a $LOGFILE
			prepareenv
			buildtoolchain
		else
			PACKAGENAME=${PACKAGE%.tar.gz}
			echo "`date -u '+%b %e %T'`: Restore from $PACKAGE" | tee -a $LOGFILE
			if [ `md5sum $PACKAGE | awk '{print $1}'` == `cat $PACKAGENAME.md5 | awk '{print $1}'` ]; then
				tar zxf $PACKAGE
				prepareenv
			else
				exiterror "$PACKAGENAME md5 did not match, check downloaded package"
			fi
		fi
	else
		echo "`date -u '+%b %e %T'`: Using installed toolchain" | tee -a $LOGFILE
		prepareenv
	fi
	buildbase
	buildipcop
	buildinstaller
	buildpackages
	;;
shell)
	# enter a shell inside LFS chroot
	# may be used to changed kernel settings
	prepareenv
	entershell
	;;
changelog)
	echo -n "Loading new Changelog from SVN: "
	svn log http://svn.ipfire.eu/svn/ipfire > doc/ChangeLog
	echo "Finished!"
	;;
check)
	echo "Checking sources files availability on the web"
	if [ ! -d $DIR_CHK ]; then
		mkdir -p $DIR_CHK
	fi
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
				make -s -f $i MACHINE=$MACHINE LFS_BASEDIR=$BASEDIR ROOT=$BASEDIR/build \
					MESSAGE="$i\t ($c/$MAX_RETRIES)" check
				if [ $? -ne 0 ]; then
					echo "Check : wget error in lfs/$i"
					FINISHED=0
				fi
			fi
		done
	done
	cd -
	;;
checkclean)
	echo "Erasing sources files availability tags"
	rm -rf $DIR_CHK/*
	;;
clean)
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
	;;
dist)
	echo -ne "Updating & building source package from SVN: "
	svn up > /dev/null
	svn export http://svn.ipfire.eu/svn/ipfire ipfire-source/ --force > /dev/null
	tar cfz ipfire-source-`date +'%Y-%m-%d'`-r`svn info | grep Revision | cut -c 11-`.tar.gz ipfire-source
	rm ipfire-source/ -r
	echo "Finished!"
	;;
newpak)
	# create structure for a new package
	echo -e "Name of the new package: $2"
	if [ ! -f "lfs/$2" ]; then
		echo "`date -u '+%b %e %T'`: Creating directory src/paks/$2"
		mkdir -p src/paks/$2
		cd src/paks/$2
		echo "`date -u '+%b %e %T'`: Creating files"
		cp $BASEDIR/lfs/postfix $BASEDIR/lfs/$2

		touch ROOTFILES
		touch {,un}install.sh
	## install.sh
		echo '#!/bin/bash' > install.sh
		echo '#' >> install.sh
		echo '#################################################################' >> install.sh
		echo '#                                                               #' >> install.sh
		echo '# This file belongs to IPFire Firewall - GPLv2 - www.ipfire.org #' >> install.sh
		echo '#                                                               #' >> install.sh
		echo '#################################################################' >> install.sh
		echo '#' >> install.sh
		echo '# Extract the files' >> install.sh
		echo 'tar xfz files.tgz -C /' >> install.sh
		echo 'cp -f ROOTFILES /opt/pakfire/installed/ROOTFILES.$2' >> install.sh
	## uninstall.sh
		echo '#!/bin/bash' > uninstall.sh
		echo '#################################################################' >> uninstall.sh
		echo '#                                                               #' >> uninstall.sh
		echo '# This file belongs to IPFire Firewall - GPLv2 - www.ipfire.org #' >> uninstall.sh
		echo '#                                                               #' >> uninstall.sh
		echo '#################################################################' >> uninstall.sh
		echo '#' >> uninstall.sh
		echo '# Delete the files' >> uninstall.sh
		echo '## Befehl fehlt noch' >> uninstall.sh
		echo 'rm -f /opt/pakfire/installed/ROOTFILES.$2' >> uninstall.sh
		echo "`date -u '+%b %e %T'`: Adding files to SVN"
		cd - && svn add lfs/$2 && svn add src/paks/$2

		echo -n "Do you want to remove the folders? [y/n]"
		read REM
		if  [ "$REM" == "y" ]; then
			echo "Removing the folders..."
			svn del src/paks/$2 --force
		else
			echo "Folders are kept."
		fi
	else
		echo "$2 already exists"
	fi
	exit 0
	;;
prefetch)
	if [ ! -d $BASEDIR/cache ]; then
		mkdir $BASEDIR/cache
	fi
	mkdir -p $BASEDIR/log
	echo "`date -u '+%b %e %T'`:Preload all source files" | tee -a $LOGFILE
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
				make -s -f $i LFS_BASEDIR=$BASEDIR MESSAGE="$i\t ($c/$MAX_RETRIES)" download >> $LOGFILE 2>&1
				if [ $? -ne 0 ]; then
					echo "Prefetch : wget error in lfs/$i"
					FINISHED=0
				else
					if [ $c -eq 1 ]; then
						echo "Prefetch : lfs/$i files loaded"
					fi
				fi
			fi
		done
	done
	echo "Prefetch : verifying md5sum"
	ERROR=0
	for i in *; do
		if [ -f "$i" -a "$i" != "Config" ]; then
			make -s -f $i LFS_BASEDIR=$BASEDIR MESSAGE="$i\t " md5 >> $LOGFILE 2>&1
			if [ $? -ne 0 ]; then
				echo "md5 difference in lfs/$i"
				ERROR=1
			fi
		fi
	done
	if [ $ERROR -eq 0 ]; then
		echo "Prefetch : all files md5sum match"
	fi
	cd -
	;;
toolchain)
	prepareenv
	buildtoolchain
	BUILDMACHINE=`uname -m`
	echo "`date -u '+%b %e %T'`: Create toolchain tar.gz for $BUILDMACHINE" | tee -a $LOGFILE
	cd $BASEDIR && tar -zc --exclude='log/_build.*.log' -f cache/$SNAME-$VERSION-toolchain-$BUILDMACHINE.tar.gz \
		build/{bin,etc,usr/bin,usr/local} \
		build/tools/{bin,etc,*-linux-gnu,include,lib,libexec,sbin,share,var} \
		log >> $LOGFILE
	md5sum cache/$SNAME-$VERSION-toolchain-$BUILDMACHINE.tar.gz \
		> cache/$SNAME-$VERSION-toolchain-$BUILDMACHINE.md5
	stdumount
	;;
gettoolchain)
	BUILDMACHINE=`uname -m`
	# arbitrary name to be updated in case of new toolchain package upload
	PACKAGE=$SNAME-1.4-toolchain-$BUILDMACHINE
	URL_IPFIRE=`grep URL_IPFIRE lfs/Config | awk '{ print $3 }'`
	echo "`date -u '+%b %e %T'`: Load toolchain tar.gz for $BUILDMACHINE" | tee -a $LOGFILE
	cd $BASEDIR/cache
	wget $URL_IPFIRE/toolchains/$PACKAGE.tar.gz $URL_IPFIRE/toolchains/$PACKAGE.md5 >& /dev/null
	if [ $? -ne 0 ]; then
		echo "`date -u '+%b %e %T'`: error downloading toolchain for $BUILDMACHINE machine" | tee -a $LOGFILE
#	else
#		if [ "`md5sum $PACKAGE.tar.gz | awk '{print $1}'`" = "`cat $PACKAGE.md5 | awk '{print $1}'`" ]; then
#			echo "`date -u '+%b %e %T'`: toolchain md5 ok" | tee -a $LOGFILE
#			echo "`date -u '+%b %e %T'`: Uncompressing toolchain" | tee -a $LOGFILE
#			cd $BASEDIR && tar xfz cache/$PACKAGE.tar.gz -C .
#			rm -f $BASEDIR/cache/$PACKAGE.{tar.gz,md5}
#		else
#			exiterror "$PACKAGE.md5 did not match, check downloaded package"
#		fi
	fi
	;;
paks)
	prepareenv
	# buildpackages
	ipfirepackages
	;;
update)
	echo "Load the latest source-files:"
	svn update
	;;
commit)
	echo "Upload the changed files:"
	svn commit
	./make.sh sync
	svn up > /dev/null
	;;
make)
	echo "Do a complete compile:"	
	./make.sh prefetch && ./make.sh gettoolchain && ./make.sh build
	;;
diff)
	echo -ne "Make a local diff to last SVN revision: "
	svn diff > ipfire-diff-`date +'%Y-%m-%d-%H:%M'`-r`svn info | grep Revision | cut -c 11-`.diff
	echo "Finished!"
	echo "Diff was successfully saved to ipfire-diff-`date +'%Y-%m-%d-%H:%M'`-r`svn info | grep Revision | cut -c 11-`.diff"
	;;
sync)
	echo -e "Syncing Cache to FTP:"
	if [ -f .pass ]; then
		PASS="`cat .pass`"
	else
		echo -ne "Password for mirror.ipfire.org: "; read PASS
	fi
	rm -f doc/packages-to-remove-from-ftp
	ncftpls -u web3 -p $PASS ftp://mirror.ipfire.org/html/source-packages/source/ > ftplist
	for i in `ls -w1 cache/`; do
		grep $i ftplist
		if [ "$?" -ne "0" ]; then
			ncftpput -u web3 -p $PASS mirror.ipfire.org /html/source-packages/source cache/$i
			if [ "$?" -eq "0" ]; then
				echo -e "$i was successfully uploaded to the ftp server."
			else
				echo -e "There was an error while uploading $i to the ftp server."
			fi
		fi
	done
	for i in `cat ftplist`; do
		ls -w1 cache/ | grep $i
		if [ "$?" -eq "1" ]; then
			echo $i | grep -v toolchain >> doc/packages-to-remove-from-ftp
		fi
	done
	rm -f ftplist
	;;
pub-iso)
	echo -e "Upload the ISO to the beta-mirror!"
	if [ -f .pass ]; then
		PASS="`cat .pass`"
	else
		echo -ne "Password for mirror.ipfire.org: "; read PASS
	fi
	ncftpls -u web3 -p $PASS ftp://mirror.ipfire.org/html/source-packages/beta/ | grep `svn info | grep Revision | cut -c 11-`
	if [ "$?" -eq "1" ]; then
			cp $BASEDIR/ipfire-install-1.4.i386.iso $BASEDIR/ipfire-install-1.4.i386-r`svn info | grep Revision | cut -c 11-`.iso
			md5sum ipfire-install-1.4.i386-r`svn info | grep Revision | cut -c 11-`.iso > ipfire-install-1.4.i386-r`svn info | grep Revision | cut -c 11-`.iso.md5
			ncftpput -u web3 -p $PASS mirror.ipfire.org /html/source-packages/beta/ ipfire-install-1.4.i386-r`svn info | grep Revision | cut -c 11-`.iso
			ncftpput -u web3 -p $PASS mirror.ipfire.org /html/source-packages/beta/ ipfire-install-1.4.i386-r`svn info | grep Revision | cut -c 11-`.iso.md5
			if [ "$?" -eq "0" ]; then
				echo -e "The ISO of Revision `svn info | grep Revision | cut -c 11-` was successfully uploaded to the ftp server."
			else
				echo -e "There was an error while uploading the ISO to the ftp server."
			fi
	else
		echo -e "File with name ipfire-install-1.4.i386-r`svn info | grep Revision | cut -c 11-`.iso already exists on the ftp server!"
	fi
	rm -f ipfire-install-1.4.i386-r`svn info | grep Revision | cut -c 11-`.iso{,.md5}
	;;
pub-paks)
	echo -e "Upload the packages to the beta-mirror!"
	if [ -f .pass ]; then
		PASS="`cat .pass`"
	else
		echo -ne "Password for mirror.ipfire.org: "; read PASS
	fi
	ncftpput -z -u web3 -p $PASS mirror.ipfire.org /html/source-packages/packages/ packages/*
	if [ "$?" -eq "0" ]; then
		echo -e "The packages were successfully uploaded to the ftp server."
	else
		echo -e "There was an error while uploading the packages to the ftp server."
	fi
	;;
*)
	echo "Usage: $0 {build|changelog|check|checkclean|clean|commit|diff|dist|gettoolchain|make|newpak|prefetch|pub-iso|pub-paks|shell|sync|toolchain|update}"
	cat doc/make.sh-usage
	exit 1
	;;
esac
