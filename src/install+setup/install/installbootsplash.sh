#!/bin/sh
if [ -e /harddisk/boot/ipfirerd.img ]; then
	/sbin/chroot /harddisk /sbin/splash -s -f /boot/splash/config/bootsplash-1024x768.cfg >> /harddisk/boot/ipfirerd.img
	/sbin/chroot /harddisk /sbin/splash -s -f /boot/splash/config/bootsplash-1024x768.cfg >> /harddisk/boot/ipfirerd-smp.img
else
	/sbin/chroot /harddisk /sbin/splash -s -f /boot/splash/config/bootsplash-1024x768.cfg >  /harddisk/boot/initrd.splash
fi
