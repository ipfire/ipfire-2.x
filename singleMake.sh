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
# Copyright (C) 2007-2014 IPFire Team <info@ipfire.org>.                   #
#                                                                          #
############################################################################
#
. make.sh
	if [ ! -f "$BASEDIR/lfs/$1" ]; then
	    echo "LFS File not exist"
	    exit 1
	fi
	clear
        LOGFILE="$BASEDIR/log/_build.custom.$1.log"
	export LOGFILE
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

	beautify build_stage "Building $1"

	ipfiremake $1
	beautify build_end
exit