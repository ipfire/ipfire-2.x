#!/bin/bash

/etc/init.d/cyrus-sasl stop

rm -rvf /etc/rc.d/rc*.d/*cyrus-sasl
