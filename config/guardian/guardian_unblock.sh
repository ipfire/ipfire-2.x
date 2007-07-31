#!/bin/sh

# this is a sample unblock script for guardian. This should work with ipchains. 
# This command gets called by guardian as such:
#  unblock.sh <source_ip>
# and the script will issue a command to remove the block that was created with # block.sh address. 
source=$1

/sbin/iptables -D INPUT -s $source -j DROP
