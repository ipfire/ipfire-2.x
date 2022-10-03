# Traverse Ten64 board can boot EFI directly
# Redirect it to the EFI process already in the
# bootloader
# (Remove on release of the 1.x Ten64 firmwire package)
if test "${board}" = "ten64"; then
	load ${devtype} ${devnum}:2 ${kernel_addr_r} efi/boot/bootaa64.efi
	bootefi ${kernel_addr_r} ${fdt_addr_r}
fi;

if test ${boot_dev} = ""; then
	setenv boot_dev mmc;
	setenv root_dev /dev/mmcblk0p3;
fi;

if test ${dev_num} = ""; then
	setenv dev_num ${devnum}
	if test ${dev_num} = ""; then
		setenv dev_num 0;
	fi;
fi;

if test ${boot_part} = ""; then
	setenv boot_part ${dev_num}:1;
fi;

# Import uEnv txt...
if fatload ${boot_dev} ${boot_part} ${kernel_addr_r} uEnv.txt; then
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
			if test ${cpu} = "armv8"; then
				if test "${fdtfile}" = "broadcom/bcm2837-rpi-3-b-plus.dtb"; then
					setenv console ttyS1,115200n8;
				else
					if test "${fdtfile}" = "broadcom/bcm2837-rpi-3-b.dtb"; then
						setenv console ttyS1,115200n8;
					else
						setenv console ttyAMA0,115200n8;
					fi;
				fi;
			else
				if test "${fdtfile}" = "bcm2837-rpi-3-b-plus.dtb"; then
					setenv console ttyS1,115200n8;
				else
					if test "${fdtfile}" = "bcm2837-rpi-3-b.dtb"; then
						setenv console ttyS1,115200n8;
					else
						setenv console ttyAMA0,115200n8;
					fi;
				fi;
			fi;
		else
			setenv console ttyS0,115200n8;
		fi;
	fi
	echo Set console to ${console};
	setenv bootargs console=${console} root=${root_dev} rootwait;
else
	echo Set console to tty1 ;
	setenv bootargs console=tty1 root=${root_dev} rootwait;
fi;

setenv fdt_high ffffffff;
fatload ${boot_dev} ${boot_part} ${kernel_addr_r} vmlinuz-${KVER}-ipfire${kernel_type};
fatload ${boot_dev} ${boot_part} ${fdt_addr_r} dtb-${KVER}-ipfire${kernel_type}/${fdtfile};

if test "${FDTCMDS}" = ""; then
	echo ;
else
	fdt addr ${fdt_addr_r};
	run FDTCMDS;
fi;

setenv ramdisk_addr ${ramdisk_addr_r}
if fatload ${boot_dev} ${boot_part} ${ramdisk_addr} uInit-${KVER}-ipfire${kernel_type}; then
	echo Ramdisk loaded...;
else
	echo Ramdisk not loaded...;
	setenv ramdisk_addr -;
fi;

bootz ${kernel_addr_r} ${ramdisk_addr} ${fdt_addr_r};
booti ${kernel_addr_r} ${ramdisk_addr} ${fdt_addr_r};

bootz ${kernel_addr_r} - ${fdt_addr_r};
booti ${kernel_addr_r} - ${fdt_addr_r};

# Recompile with:
# mkimage -C none -A arm -T script -d /boot/boot.cmd /boot/boot.scr 
