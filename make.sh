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
# Copyright (C) 2006 IPFire-Team <info@ipfire.eu>.                         #
#                                                                          #
############################################################################
#

NAME="IPFire"				# Software name
SNAME="ipfire"			# Short name
VERSION="2.0"				# Version number
SLOGAN="www.ipfire.eu"		# Software slogan
CONFIG_ROOT=/var/ipfire		# Configuration rootdir
NICE=10				# Nice level
MAX_RETRIES=3				# prefetch/check loop
KVER=`grep --max-count=1 VER lfs/linux | awk '{ print $3 }'`
MACHINE=`uname -m`
SVN_REVISION=`svn info | grep Revision | cut -c 11-`

# Setzen des IPFire Builds
if [ -e ./.svn ]; then
	FIREBUILD=`cat .svn/entries |sed -n 's/^[ \t]*revision=\"// p' | sed -n 's/\".*$// p'`
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
else
	make_config
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
    if (( 2202000 > $BASE_ASPACE )); then
	BASE_USPACE=`du -skx $BASEDIR | awk '{print $1}'`
	if (( 2202000 - $BASE_USPACE > $BASE_ASPACE )); then
		beautify message FAIL
		exiterror "Not enough temporary space available, need at least 2.1GB on $BASE_DEV"
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
    MAKETUNING="-j8"
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
    mount  -t   devpts devpts    $BASEDIR/build/dev/pts
    mount  -t   tmpfs  shm       $BASEDIR/build/dev/shm
    mount  -t   proc   proc      $BASEDIR/build/proc
    mount  -t   sysfs  sysfs     $BASEDIR/build/sys
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

buildtoolchain() {
    LOGFILE="$BASEDIR/log/_build.toolchain.log"
    export LOGFILE
    ORG_PATH=$PATH
    NATIVEGCC=`gcc --version | grep GCC | awk {'print $3'}`
    export NATIVEGCC GCCmajor=${NATIVEGCC:0:1} GCCminor=${NATIVEGCC:2:1} GCCrelease=${NATIVEGCC:4:1}
    lfsmake1 ccache
    lfsmake1 binutils	PASS=1
    lfsmake1 gcc		PASS=1
    export PATH=$BASEDIR/build/usr/local/bin:$BASEDIR/build/tools/bin:$PATH
    lfsmake1 linux-libc-header
    lfsmake1 glibc
    lfsmake1 cleanup-toolchain PASS=1
    lfsmake1 tcl
    lfsmake1 expect
    lfsmake1 dejagnu
    lfsmake1 gcc		PASS=2
    lfsmake1 binutils	PASS=2
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
    lfsmake1 util-linux
    lfsmake1 cleanup-toolchain	PASS=2
    export PATH=$ORG_PATH
}

buildbase() {
    LOGFILE="$BASEDIR/log/_build.base.log"
    export LOGFILE
    lfsmake2 stage2
#    lfsmake2 makedev
    lfsmake2 linux-libc-header
    lfsmake2 man-pages
    lfsmake2 glibc
    lfsmake2 cleanup-toolchain	PASS=3
    lfsmake2 binutils
    lfsmake2 gcc
    lfsmake2 berkeley
    lfsmake2 coreutils
    lfsmake2 iana-etc
    lfsmake2 m4
    lfsmake2 bison
    lfsmake2 ncurses
    lfsmake2 procps
    lfsmake2 sed
    lfsmake2 libtool
    lfsmake2 perl
    lfsmake2 readline
    lfsmake2 zlib
    lfsmake2 autoconf
    lfsmake2 automake
    lfsmake2 bash
    lfsmake2 bzip2
    lfsmake2 diffutils
    lfsmake2 e2fsprogs
    lfsmake2 file
    lfsmake2 findutils
    lfsmake2 flex
    lfsmake2 grub
    lfsmake2 gawk
    lfsmake2 gettext
    lfsmake2 grep
    lfsmake2 groff
    lfsmake2 gzip
    lfsmake2 inetutils
    lfsmake2 iproute2
    lfsmake2 kbd
    lfsmake2 less
    lfsmake2 make
    lfsmake2 man
    lfsmake2 mktemp
    lfsmake2 modutils
    lfsmake2 patch
    lfsmake2 psmisc
    lfsmake2 shadow
    lfsmake2 sysklogd
    lfsmake2 sysvinit
    lfsmake2 tar
    lfsmake2 texinfo
    lfsmake2 udev
    lfsmake2 util-linux
    lfsmake2 vim
####
#    lfsmake2 net-tools
#    lfsmake2 inetutils
#    lfsmake2 ed
#    lfsmake2 procinfo
}

buildipfire() {
  LOGFILE="$BASEDIR/log/_build.ipfire.log"
  export LOGFILE
  ipfiremake configroot
  ipfiremake dhcp
  ipfiremake dhcpcd
  ipfiremake libusb
  ipfiremake libpcap
  ipfiremake linux-atm
  ipfiremake ppp
  ipfiremake rp-pppoe
  ipfiremake unzip
  ipfiremake linux			PASS=ipfire SMP=installer
  ipfiremake linux			PASS=ipfire SMP=1
  ipfiremake 3cp4218			SMP=1
  ipfiremake amedyn			SMP=1
  ipfiremake cxacru			SMP=1
  ipfiremake eagle			SMP=1
  ipfiremake cnx_pci			SMP=1
  ipfiremake fcdsl			SMP=1
  ipfiremake fcdsl2			SMP=1
  ipfiremake fcdslsl			SMP=1
  ipfiremake fcdslusb		SMP=1
  ipfiremake fcdslslusb		SMP=1
  ipfiremake fcpci			SMP=1
  ipfiremake fcclassic		SMP=1
  ipfiremake pulsar			SMP=1
  ipfiremake unicorn			SMP=1
  ipfiremake promise-sata-300-tx	SMP=1
  ipfiremake linux			PASS=ipfire
  ipfiremake 3cp4218 	
  ipfiremake amedyn 	
  ipfiremake cxacru 	
  ipfiremake eciadsl 	
  ipfiremake eagle 	
  ipfiremake speedtouch 	
  ipfiremake cnx_pci 	
  ipfiremake fcdsl 	
  ipfiremake fcdsl2 	
  ipfiremake fcdslsl 	
  ipfiremake fcdslusb 	
  ipfiremake fcdslslusb 
  ipfiremake fcpci
  ipfiremake fcclassic
  ipfiremake pulsar	
  ipfiremake unicorn
  ipfiremake promise-sata-300-tx
  ipfiremake pcmcia-cs
  ipfiremake expat
  ipfiremake gdbm
  ipfiremake gmp
  ipfiremake openssl
  ipfiremake python
  ipfiremake libnet
  ipfiremake libpng
  ipfiremake libtiff
  ipfiremake libjpeg
  ipfiremake lcms
  ipfiremake libmng
  ipfiremake freetype
  ipfiremake gd
  ipfiremake popt
  ipfiremake slang
  ipfiremake newt
  ipfiremake libcap
  ipfiremake pciutils
  ipfiremake pcre
  ipfiremake readline
  ipfiremake libxml2
  ipfiremake berkeley
  ipfiremake BerkeleyDB ## The Perl module
  ipfiremake mysql
  ipfiremake saslauthd PASS=1
  ipfiremake openldap
  ipfiremake apache2
  ipfiremake php
  ipfiremake subversion
  ipfiremake apache2 PASS=CONFIG
  ipfiremake arping
  ipfiremake beep
  ipfiremake bind
  ipfiremake capi4k-utils
  ipfiremake cdrtools
  ipfiremake dnsmasq
  ipfiremake dosfstools
  ipfiremake ethtool
  ipfiremake ez-ipupdate
  ipfiremake fcron
  ipfiremake perl-GD
  ipfiremake gnupg
  ipfiremake hdparm
  ipfiremake ibod
  ipfiremake initscripts
  ipfiremake iptables
  ipfiremake ipac-ng
  ipfiremake ipaddr
  ipfiremake iproute2
  ipfiremake iptstate
  ipfiremake iputils
  ipfiremake l7-protocols
  ipfiremake isapnptools
  ipfiremake isdn4k-utils
  ipfiremake kudzu
  ipfiremake logrotate
  ipfiremake logwatch
  ipfiremake mingetty
  ipfiremake misc-progs
  ipfiremake mtools
  ipfiremake nano
  ipfiremake nash
  ipfiremake nasm
  ipfiremake URI
  ipfiremake HTML-Tagset
  ipfiremake HTML-Parser
  ipfiremake Compress-Zlib
  ipfiremake Digest
  ipfiremake Digest-SHA1
  ipfiremake Digest-HMAC
  ipfiremake libwww-perl
  ipfiremake Net-DNS
  ipfiremake Net-IPv4Addr
  ipfiremake Net_SSLeay
  ipfiremake IO-Stringy
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
  ipfiremake GeoIP
  ipfiremake fwhits
  ipfiremake noip_updater
  ipfiremake ntp
  ipfiremake oinkmaster
  ipfiremake openssh
  ipfiremake openswan
  ipfiremake pptpclient
  ipfiremake rrdtool
  ipfiremake setserial
  ipfiremake setup
  ipfiremake snort
  ipfiremake squid
  ipfiremake squid-graph
  ipfiremake squidguard
  ipfiremake tcpdump
  ipfiremake traceroute
  ipfiremake vlan
  ipfiremake wireless
  ipfiremake libsafe
  ipfiremake 3c5x9setup
  ipfiremake pakfire
  ipfiremake startscripts
  ipfiremake java
  ipfiremake bootsplash
  ipfiremake spandsp
  ipfiremake lzo
  ipfiremake openvpn
  ipfiremake pkg-config
  ipfiremake glib
  ipfiremake pam
  ipfiremake pammysql
  ipfiremake saslauthd PASS=2
  ipfiremake xinetd
  ipfiremake ghostscript
  ipfiremake cups
  ipfiremake samba
  ipfiremake sudo
  ipfiremake mc
  ipfiremake wget
  ipfiremake wput
  ipfiremake bridge-utils
  ipfiremake screen
  ipfiremake hddtemp
  ipfiremake smartmontools
  ipfiremake htop
  ipfiremake lynx
  ipfiremake postfix
  ipfiremake procmail
  ipfiremake fetchmail
  ipfiremake cyrusimap
  ipfiremake webcyradm
  ipfiremake mailx
  ipfiremake clamav
  ipfiremake razor
  ipfiremake spamassassin
#  ipfiremake amavisd
  ipfiremake stund
  ipfiremake zaptel
  ipfiremake libpri
  ipfiremake bristuff
  ipfiremake asterisk
  ipfiremake mpg123
  ipfiremake libmad
  ipfiremake libogg
  ipfiremake libvorbis
  ipfiremake lame
  ipfiremake xvid
  ipfiremake mpeg2dec
  ipfiremake ffmpeg
  ipfiremake sox
  ipfiremake gnump3d
  ipfiremake videolan
  ipfiremake applejuice
  ipfiremake ocaml
  ipfiremake mldonkey
  ipfiremake ntop
  ipfiremake rsync
  ipfiremake tcpwrapper
  ipfiremake portmap
  ipfiremake nfs
  ipfiremake nmap
  ipfiremake mbmon
  ipfiremake iftop
  ipfiremake ncftp
  ipfiremake cftp
  ipfiremake etherwake
  ipfiremake ethereal
  ipfiremake tftp-hpa
  ipfiremake iptraf
  ipfiremake nagios
  ipfiremake yasuc
}

buildinstaller() {
  # Run installer scripts one by one
  LOGFILE="$BASEDIR/log/_build.installer.log"
  export LOGFILE
  ipfiremake syslinux
  ipfiremake as86
  ipfiremake mbr
  ipfiremake uClibc
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
		echo "* `basename $i`" >>$BASEDIR/doc/packages-list
	fi
  done
  echo "== List of softwares used to build $NAME Version: $VERSION ==" > $BASEDIR/doc/packages-list.txt
  grep -v 'configroot$\|img$\|initrd$\|initscripts$\|installer$\|install$\|ipfire$\|setup$\|pakfire$\|stage2$\|smp$\|tools$\|tools1$\|tools2$\|.tgz$\|-config$' \
	$BASEDIR/doc/packages-list | sort >> $BASEDIR/doc/packages-list.txt
  rm -f $BASEDIR/doc/packages-list
  # packages-list.txt is ready to be displayed for wiki page

  # Create ISO for CDROM
  ipfiremake cdrom
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
  cd $BASEDIR/packages; ls -w1 *.ipfire | awk -F ".ipfire" '{ print $1 }' > $BASEDIR/packages/packages_list.txt
  echo -n "###EOF###" >> $BASEDIR/packages/packages_list.txt

  cd $PWD

}

ipfirepackages() {
  if [ -d "$BASEDIR/packages" ]; then
	  for i in `ls $BASEDIR/packages`; do
		touch $BASEDIR/build/install/packages/$i.empty
	  done
  fi
#  ipfiredist amavisd
  ipfiredist applejuice
  ipfiredist asterisk
  ipfiredist clamav
  ipfiredist cups
  ipfiredist cyrusimap
  ipfiredist fetchmail
  ipfiredist ffmpeg
  ipfiredist gnump3d
  ipfiredist iptraf
  ipfiredist java
  ipfiredist lame
  ipfiredist libmad
  ipfiredist libogg
  ipfiredist libtiff
  ipfiredist libvorbis
  ipfiredist mailx
  ipfiredist mldonkey
  ipfiredist mpeg2dec
  ipfiredist nagios
  ipfiredist nfs
  ipfiredist nmap
  ipfiredist ntop
  ipfiredist portmap
  ipfiredist postfix
  ipfiredist procmail
  ipfiredist samba
  ipfiredist sox
  ipfiredist spamassassin
  ipfiredist subversion
  ipfiredist videolan
  ipfiredist webcyradm
  ipfiredist xvid
  ipfiredist yasuc
  test -d $BASEDIR/packages || mkdir $BASEDIR/packages
  mv -f $LFS/install/packages/*.{ipfire,md5} $BASEDIR/packages >> $LOGFILE 2>&1
  rm -rf  $BASEDIR/build/install/packages/*
}

# See what we're supposed to do
case "$1" in 
build)
	BUILDMACHINE=`uname -m`
	PACKAGE=`ls -v -r $BASEDIR/cache/toolchains/$SNAME-$VERSION-toolchain-$BUILDMACHINE.tar.gz 2> /dev/null | head -n 1`
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
		echo "`date -u '+%b %e %T'`: Using installed toolchain" | tee -a $LOGFILE
		prepareenv
	fi

	beautify build_stage "Building base"
	buildbase

	beautify build_stage "Building IPFire"
	buildipfire

	# Setzen des IPFire Builds
	if [ "$FIREBUILD" ]; then
		echo "$FIREBUILD" > $BASEDIR/build/var/ipfire/firebuild
	else
		echo "_(OvO)_" > $BASEDIR/build/var/ipfire/firebuild
	fi

	beautify build_stage "Building installer"
	buildinstaller

	beautify build_stage "Building packages"
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
	beautify build_stage "Toolchain compilation - Native GCC: `gcc --version | grep GCC | awk {'print $3'}`"
	buildtoolchain
	BUILDMACHINE=`uname -m`
	echo "`date -u '+%b %e %T'`: Create toolchain tar.gz for $BUILDMACHINE" | tee -a $LOGFILE
	test -d $BASEDIR/cache/toolchains || mkdir $BASEDIR/cache/toolchains
	cd $BASEDIR && tar -zc --exclude='log/_build.*.log' -f cache/toolchains/$SNAME-$VERSION-toolchain-$BUILDMACHINE.tar.gz \
		build/{bin,etc,usr/bin,usr/local} \
		build/tools/{bin,etc,*-linux-gnu,include,lib,libexec,sbin,share,var} \
		log >> $LOGFILE
	md5sum cache/toolchains/$SNAME-$VERSION-toolchain-$BUILDMACHINE.tar.gz \
		> cache/toolchains/$SNAME-$VERSION-toolchain-$BUILDMACHINE.md5
	stdumount
	;;
gettoolchain)
	BUILDMACHINE=`uname -m`
	# arbitrary name to be updated in case of new toolchain package upload
	PACKAGE=$SNAME-$VERSION-toolchain-$BUILDMACHINE
	if [ ! -f $BASEDIR/cache/toolchains/$PACKAGE.tar.gz ]; then
		URL_IPFIRE=`grep URL_IPFIRE lfs/Config | awk '{ print $3 }'`
		test -d $BASEDIR/cache/toolchains || mkdir $BASEDIR/cache/toolchains
		echo "`date -u '+%b %e %T'`: Load toolchain tar.gz for $BUILDMACHINE" | tee -a $LOGFILE
		cd $BASEDIR/cache/toolchains
		wget $URL_IPFIRE/toolchains/$PACKAGE.tar.gz $URL_IPFIRE/toolchains/$PACKAGE.md5 >& /dev/null
		if [ $? -ne 0 ]; then
			echo "`date -u '+%b %e %T'`: error downloading toolchain for $BUILDMACHINE machine" | tee -a $LOGFILE
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
svn)
	case "$2" in
	  update|up)
		# clear
		echo -ne "Loading the latest source files...\n"
		if [ $3 ]; then
			svn update -r $3 | tee -a $PWD/log/_build.svn.update.log
		else
			svn update | tee -a $PWD/log/_build.svn.update.log
		fi
		if [ $? -eq "0" ]; then
			beautify message DONE
		else
			beautify message FAIL
			exit 1
		fi
		echo -ne "Writing the svn-info to a file"
		svn info > $PWD/svn_status
		if [ $? -eq "0" ]; then
			beautify message DONE
		else
			beautify message FAIL
			exit 1
		fi
		chmod 755 $0
		exit 0
	  ;;
	  commit|ci)
		clear
		if [ -e /sbin/yast ]; then
			if [ "`echo $SVN_REVISION | cut -c 3`" -eq "0" ]; then
				$0 changelog
			fi
		fi
		echo "Upload the changed files..."
		sleep 1
		svn commit
		$0 svn up
	  ;;
	  dist)
		if [ $3 ]; then
			SVN_REVISION=$3
		fi
		if [ -f ipfire-source-r$SVN_REVISION.tar.gz ]; then
			echo -ne "REV $SVN_REVISION: SKIPPED!\n"
			exit 0
		fi
		echo -en "REV $SVN_REVISION: Downloading..."
		svn export http://svn.ipfire.eu/svn/ipfire ipfire-source/ --force > /dev/null
		svn log http://svn.ipfire.eu/svn/ipfire -r 1:$SVN_REVISION > ipfire-source/Changelog
		#svn info http://svn.ipfire.eu/svn/ipfire -r $SVN_REVISION > ipfire-source/svn_status
		evaluate 1

		echo -en "REV $SVN_REVISION: Compressing files..."
		if [ -e ipfire-source/trunk/make.sh ]; then
			chmod 755 ipfire-source/trunk/make.sh
		fi
		tar cfz ipfire-source-r$SVN_REVISION.tar.gz ipfire-source
		evaluate 1
		echo -en "REV $SVN_REVISION: Cleaning up..."
		rm ipfire-source/ -r
		evaluate 1
	  ;;
	  diff|di)
		echo -ne "Make a local diff to last svn revision"
		svn diff > ipfire-diff-`date +'%Y-%m-%d-%H:%M'`-r`svn info | grep Revision | cut -c 11-`.diff
		evaluate 1
		echo "Diff was successfully saved to ipfire-diff-`date +'%Y-%m-%d-%H:%M'`-r`svn info | grep Revision | cut -c 11-`.diff"
	  ;;
	esac
	;;
uploadsrc)
	PWD=`pwd`
	cd $BASEDIR/cache/
	echo -e "Uploading cache to ftp server:"
	ncftpls -u $IPFIRE_FTP_USER_INT -p $IPFIRE_FTP_PASS_INT ftp://$IPFIRE_FTP_URL_INT$IPFIRE_FTP_PATH_INT/ > /var/tmp/ftplist
	for i in *; do
		grep -q $i /var/tmp/ftplist
		if [ "$?" -ne "0" ]; then
			echo -ne "$i"
			ncftpput -bb -u $IPFIRE_FTP_USER_INT -p $IPFIRE_FTP_PASS_INT $IPFIRE_FTP_URL_INT $IPFIRE_FTP_PATH_INT/ $i > /dev/null 2>&1
			if [ "$?" -eq "0" ]; then
				beautify message DONE
			else
				beautify message FAIL
			fi
		fi
	done
	rm -f /var/tmp/ftplist
	UL_TIME_START=`date +'%s'`
	ncftpbatch -d > /dev/null 2>&1
	while ps acx | grep -q ncftpbatch
	do
		UL_TIME=$(expr `date +'%s'` - $UL_TIME_START)
		echo -ne "\r ${UL_TIME}s : Upload is running..."
		sleep 1
	done
	beautify message DONE
	cd $PWD
	exit 0
	;;
upload)
	case "$2" in
	  iso)
		echo -e "Uploading the iso to $IPFIRE_FTP_URL_EXT."
		cat <<EOF > .ftp-commands
mkdir $IPFIRE_FTP_PATH_EXT
ls -lah
quit
EOF
		ncftp -u $IPFIRE_FTP_USER_EXT -p $IPFIRE_FTP_PASS_EXT $IPFIRE_FTP_URL_EXT < .ftp-commands
		rm -f .ftp-commands
		md5sum ipfire-install-$VERSION.i386.iso > ipfire-install-$VERSION.i386.iso.md5
		ncftpput -u $IPFIRE_FTP_USER_EXT -p $IPFIRE_FTP_PASS_EXT $IPFIRE_FTP_URL_EXT $IPFIRE_FTP_PATH_EXT/ ipfire-install-$VERSION.i386.iso
		ncftpput -u $IPFIRE_FTP_USER_EXT -p $IPFIRE_FTP_PASS_EXT $IPFIRE_FTP_URL_EXT $IPFIRE_FTP_PATH_EXT/ ipfire-install-$VERSION.i386.iso.md5
		ncftpput -u $IPFIRE_FTP_USER_EXT -p $IPFIRE_FTP_PASS_EXT $IPFIRE_FTP_URL_EXT $IPFIRE_FTP_PATH_EXT/ ipfire-source-r$SVN_REVISION.tar.gz
		ncftpput -u $IPFIRE_FTP_USER_EXT -p $IPFIRE_FTP_PASS_EXT $IPFIRE_FTP_URL_EXT $IPFIRE_FTP_PATH_EXT/ svn_status
		if [ "$?" -eq "0" ]; then
			echo -e "The iso of Revision $SVN_REVISION was successfully uploaded to $IPFIRE_FTP_URL_EXT$IPFIRE_FTP_PATH_EXT/."
		else
			echo -e "There was an error while uploading the iso to the ftp server."
			exit 1
		fi
		if [ "$3" = "--with-sources-cd" ]; then
			ncftpput -u $IPFIRE_FTP_USER_EXT -p $IPFIRE_FTP_PASS_EXT $IPFIRE_FTP_URL_EXT $IPFIRE_FTP_PATH_EXT/ ipfire-sources-cd-$VERSION.$MACHINE.iso
		fi
		;;
	  paks)
		cat <<EOF > .ftp-commands
mkdir $IPFIRE_FTP_PATH_PAK
ls -lah
quit
EOF
		ncftp -u $IPFIRE_FTP_USER_PAK -p $IPFIRE_FTP_PASS_PAK $IPFIRE_FTP_URL_PAK < .ftp-commands
		rm -f .ftp-commands
		ncftpput -z -u $IPFIRE_FTP_USER_PAK -p $IPFIRE_FTP_PASS_PAK $IPFIRE_FTP_URL_PAK $IPFIRE_FTP_PATH_PAK/ packages/*
		if [ "$?" -eq "0" ]; then
			echo -e "The packages were successfully uploaded to $IPFIRE_FTP_URL_PAK$IPFIRE_FTP_PATH_PAK/."
		else
			echo -e "There was an error while uploading the packages to the ftp server."
			exit 1
		fi
	  ;;
	esac
	;;
batch)
	if [ "$2" -eq "--background" ]; then
		batch_script
		exit $?
	fi
	if [ `screen -ls | grep -q ipfire` ]; then
		echo "Build is already running, sorry!"
		exit 1
	else
		if [ "$2" = "--rebuild" ]; then
			export IPFIRE_REBUILD=1
			echo "REBUILD!"
		else
			export IPFIRE_REBUILD=0
		fi
		echo -en "${BOLD}***IPFire-Batch-Build is starting...${NORMAL}"
		screen -dmS ipfire $0 batch --background
		evaluate 1
		exit 0
	fi
	;;
watch)
	watch_screen
	;;
*)
	clear
	svn info
	select name in "Exit" "IPFIRE: Prefetch" "IPFIRE: Build (silent)" "IPFIRE: Watch Build" "IPFIRE: Batch" "IPFIRE: Clean" "SVN: Commit" "SVN: Update" "SVN: Status" "SVN: Diff" "LOG: Tail" "Help"
	do
	case $name in
	"IPFIRE: Prefetch")
		$0 prefetch
		;;
	"IPFIRE: Build (silent)")
		$0 build-silent
		;;
	"IPFIRE: Watch Build")
		$0 watch
		;;
	"IPFIRE: Batch")
		$0 batch
		;;
	"IPFIRE: Clean")
		$0 clean
		;;
	"SVN: Commit")
		if [ -f /usr/bin/mcedit ]; then
			export EDITOR=/usr/bin/mcedit
		fi
		if [ -f /usr/bin/nano ]; then
			export EDITOR=/usr/bin/nano
		fi
		$0 svn commit
		$0 uploadsrc
		;;
	"SVN: Update")
		$0 svn update
		;;
	"SVN: Status")
		svn status # | grep -v ^?
		;;
	"SVN: Diff")
		$0 svn diff
		;;
	"Help")
		echo "Usage: $0 {build|changelog|clean|gettoolchain|newpak|prefetch|shell|sync|toolchain}"
		cat doc/make.sh-usage
		;;
	"LOG: Tail")
		tail -f log/_*
		;;
	"Exit")
		break
		;;
	esac
	done
	;;
esac
