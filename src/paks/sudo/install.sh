#!/bin/bash
#
#################################################################
#                                                               #
# This file belongs to IPFire Firewall - GPLv2 - www.ipfire.org #
#                                                               #
#################################################################
#
# Extract the files
tar xfz files.tgz -C /
tar xfz conf.tgz -C /
cp -f ROOTFILES /opt/pakfire/installed/ROOTFILES.$2
