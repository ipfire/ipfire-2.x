#!/bin/bash

/etc/init.d/cups stop

rm -rf /etc/rc.d/rc*.d/*cups
