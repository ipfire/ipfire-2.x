#!/bin/bash
############################################################################
#                                                                          #
# This file is part of the IPFire Firewall.                                #
#                                                                          #
# IPFire is free software; you can redistribute it and/or modify           #
# it under the terms of the GNU General Public License as published by     #
# the Free Software Foundation; either version 3 of the License, or        #
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
# Copyright (C) 2024 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1

core=189

# Remove old core updates from pakfire cache to save space...
for (( i=1; i<=$core; i++ )); do
	rm -f /var/cache/pakfire/core-upgrade-*-$i.ipfire
done

# Removed old firmware files
rm -vrf \
	/lib/firmware/amlogic/bluetooth \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10280cbd-spkid0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10280cbd-spkid1.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10280cbd.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10280cbe-spkid0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10280cbe-spkid1.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10280cbe.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10280cbf-spkid0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10280cbf-spkid1.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10280cbf.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10280cc1-spkid0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10280cc1-spkid1.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10280cc1.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10280cc2-spkid0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10280cc2-spkid1.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10280cc2.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10280cc3-spkid0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10280cc3-spkid1.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10280cc3.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10280cc4-spkid0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10280cc4-spkid1.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10280cc4.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c896e-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c896e-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c896e.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8971.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8971.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8972.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8972.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8973.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8973.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8974.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8974.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8975-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8975-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8975.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8981-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8981-l1.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8981-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8981-r1.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8981.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c898e.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c898e.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c898f.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c898f.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8991.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8991.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8992.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8992.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8994.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8994.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8995.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8995.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c89c3-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c89c3-l1.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c89c3-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c89c3-r1.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c89c3.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c89c6-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c89c6-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c89c6.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b42.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b42.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b43.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b43.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b44.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b44.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b45.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b45.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b46.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b46.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b47.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b47.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b63-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b63-l1.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b63-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b63-r1.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b63.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b70.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b70.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b72.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b72.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b74.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b74.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b77.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b77.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b8f-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b8f-l1.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b8f-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b8f-r1.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8b92.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8c26.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8c26.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8c46.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8c46.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8c47.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8c47.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8c48.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8c48.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8c49.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8c49.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8c70.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8c70.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8c71.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8c71.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8c72.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-103c8c72.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-104312af-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-104312af-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-104312af-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-104312af-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-104312af.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431433-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431433-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431433-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431433-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431433.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431463-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431463-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431463-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431463-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431463.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431473-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431473-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431473.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431483-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431483-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431483.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431493-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431493-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431493-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431493-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431493.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-104314d3-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-104314d3-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-104314d3-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-104314d3-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-104314d3.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-104314e3-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-104314e3-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-104314e3-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-104314e3-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-104314e3.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431503-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431503-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431503-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431503-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431503.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431533-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431533-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431533-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431533-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431533.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431573-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431573-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431573-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431573-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431573.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431663-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431663-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431663.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-104317f3-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-104317f3-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-104317f3-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-104317f3-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-104317f3.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431a20.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431a30.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431a40.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431a50.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431a60.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431a8f-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431a8f-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431a8f-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431a8f-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431a8f.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431b93-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431b93-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431b93-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431b93-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431b93.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431c9f-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431c9f-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431c9f-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431c9f-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431c9f.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431caf-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431caf-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431caf-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431caf-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431caf.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431ccf-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431ccf-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431ccf-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431ccf-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431ccf.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431cdf-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431cdf-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431cdf-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431cdf-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431cdf.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431cef-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431cef-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431cef-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431cef-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431cef.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431d1f-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431d1f-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431d1f-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431d1f-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431d1f.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431e02-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431e02-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431e02-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431e02-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431e02.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431e12-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431e12-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431e12-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431e12-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431e12.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431f12-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431f12-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431f12-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431f12-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10431f12.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10433a20-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10433a20-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10433a20-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10433a20-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10433a30-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10433a30-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10433a30-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10433a30-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10433a40-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10433a40-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10433a40-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10433a40-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10433a50-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10433a50-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10433a50-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10433a50-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10433a60-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10433a60-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10433a60-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-10433a60-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa22f1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa22f1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa22f1.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa22f2-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa22f2-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa22f2.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa22f3-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa22f3-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa22f3.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa2316-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa2316-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa2316-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa2316-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa2316.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa2317-spkid0-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa2317-spkid0-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa2317-spkid1-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa2317-spkid1-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa2317.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa2318-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa2318-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa2318.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa2319-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa2319-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa2319.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa231a-l0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa231a-r0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa231a.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa3847-spkid0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa3847-spkid1.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa3847.wmfw \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa3855-spkid0.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa3855-spkid1.bin \
	/lib/firmware/cirrus/cs35l41-dsp1-spk-cali-17aa3855.wmfw \
	/lib/firmware/cxgb4/t4fw-1.27.4.0.bin \
	/lib/firmware/cxgb4/t5fw-1.27.4.0.bin \
	/lib/firmware/cxgb4/t6fw-1.27.4.0.bin \
	/lib/firmware/intel/ice/ddp/ice-1.3.30.0.pkg \
	/lib/firmware/intel/ice/ddp-comms/ice_comms-1.3.40.0.pkg \
	/lib/firmware/intel/ice/ddp-wireless_edge/ice_wireless_edge-1.3.10.0.pkg \
	/lib/firmware/mediatek/sof-tplg/sof-mt8195-mt6359-rt1019-rt5682-dts.tplg \
	/lib/firmware/qcom/sdm845/notice.txt_wlanmdsp \
	/lib/firmware/qcom/vpu-1.0/venus.mdt \
	/lib/firmware/RTL8192E

# Stop services
/usr/local/bin/openvpnctrl -k
/usr/local/bin/openvpnctrl -kn2n

# Extract files
extract_files

# Remove files

# update linker config
ldconfig

# Update Language cache
/usr/local/bin/update-lang-cache

# Filesytem cleanup
/usr/local/bin/filesystem-cleanup

# Apply local configuration to sshd_config
/usr/local/bin/sshctrl

# Reload init
telinit u

# Start services
/usr/local/bin/openvpnctrl -s
/usr/local/bin/openvpnctrl -sn2n

# Regenerate Suricata rule files
perl -e "require '/var/ipfire/ids-functions.pl'; &IDS::write_used_rulefiles_file();"t
/etc/init.d/suricata reload

# Build initial ramdisks
dracut --regenerate-all --force
KVER="xxxKVERxxx"
case "$(uname -m)" in
	aarch64)
		mkimage -A arm64 -T ramdisk -C lzma -d /boot/initramfs-${KVER}-ipfire.img /boot/uInit-${KVER}-ipfire
		# dont remove initramfs because grub need this to boot.
		;;
esac

# This update needs a reboot...
touch /var/run/need_reboot

# Finish
/etc/init.d/fireinfo start
sendprofile

# Update grub config to display new core version
if [ -e /boot/grub/grub.cfg ]; then
	grub-mkconfig -o /boot/grub/grub.cfg
fi

sync

# Don't report the exitcode last command
exit 0
