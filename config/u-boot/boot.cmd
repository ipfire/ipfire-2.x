# Import uEnv txt...
if fatload mmc 0 ${kernel_addr_r} uEnv.txt; then
	echo Load uEnv.txt...;
	env import -t ${kernel_addr_r} ${filesize};
	if test "${uenvcmd}" = ""; then
		echo ...;
	else
		echo Boot with uEnv.txt...;
		run uenvcmd;
	fi;
fi;

# for compatiblity reasons set DTBSUNXI if we run on sunxi
if test "${board}" = "sunxi"; then
	setenv fdtfile ${DTBSUNXI};
fi;

# Check if serial console is enabled
if test "${SERIAL-CONSOLE}" = "ON"; then
	if test ${console} = ""; then
		if test "${board}" = "rpi"; then
			if test "${fdtfile}" = "bcm2837-rpi-3-b.dtb"; then
				setenv console ttyS1,115200n8;
			else
				setenv console ttyAMA0,115200n8;
			fi;
		else
			setenv console ttyS0,115200n8;
		fi;
	fi
	echo Set console to ${console};
	setenv bootargs console=${console} rootwait root=/dev/mmcblk0p3 rootwait;
else
	echo Set console to tty1 ;
	setenv bootargs console=tty1 rootwait root=/dev/mmcblk0p3 rootwait;
fi;

setenv fdt_high ffffffff;
fatload mmc 0:1 ${kernel_addr_r} vmlinuz-${KVER}-ipfire-multi;
fatload mmc 0:1 ${fdt_addr_r} dtb-${KVER}-ipfire-multi/${fdtfile};
if fatload mmc 0:1 ${ramdisk_addr_r} uInit-${KVER}-ipfire-multi; then
	echo Ramdisk loaded...;
else
	echo Ramdisk not loaded...;
	setenv ramdisk_addr_r -;
fi ;
bootz ${kernel_addr_r} ${ramdisk_addr_r} ${fdt_addr_r};

# Recompile with:
# mkimage -C none -A arm -T script -d /boot/boot.cmd /boot/boot.scr 
