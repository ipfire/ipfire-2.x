#!/bin/sh
OLDDIR=`pwd`
cd /lib/modules/*/kernel/drivers/scsi
/bin/modprobe scsi_mod.o.gz > /dev/null 2>&1
/bin/modprobe sd_mod.o.gz > /dev/null 2>&1
/bin/modprobe sr_mod.o.gz > /dev/null 2>&1
/bin/modprobe sg.o.gz > /dev/null 2>&1
/bin/modprobe libata.o.gz > /dev/null 2>&1
echo "Trying cpqarray"; 
if /bin/modprobe cpqarray > /dev/null 2>&1; then
	echo "cpqarray.o.gz" > /scsidriver;
	exit 0;
fi
echo "Trying cciss";
if /bin/modprobe cciss > /dev/null 2>&1; then
	echo "cciss.o.gz" > /scsidriver;
	exit 0;
fi
echo "Trying DAC960";
if /bin/modprobe DAC960 > /dev/null 2>&1; then
	echo "DAC960.o.gz" > /scsidriver;
	exit 0;
fi
/bin/modprobe ataraid.o.gz > /dev/null 2>&1
echo "Trying medley";
if /bin/modprobe medley > /dev/null 2>&1; then
	echo "medley.o.gz" > /scsidriver;
	exit 0;
fi
echo "Trying hptraid";
if /bin/modprobe hptraid > /dev/null 2>&1; then
	echo "hptraid.o.gz" > /scsidriver;
	exit 0;
fi
echo "Trying pdcraid";
if /bin/modprobe pdcraid > /dev/null 2>&1; then
	echo "pdcraid.o.gz" > /scsidriver;
	exit 0;
fi
echo "Trying silraid";
if /bin/modprobe silraid > /dev/null 2>&1; then
	echo "silraid.o.gz" > /scsidriver;
	exit 0;
fi
for i in * message/fusion/mptscsih.o.gz ; 
do 
# Skip the generic scsi modules and ancillary support modules
# Added eata_dma to skip list because it crashes some machines. Probe last.
if [ $i != "scsi_mod.o.gz" -a $i != "sd_mod.o.gz" -a $i != "sg.o.gz" -a $i != "sr_mod.o.gz" -a $i != "53c700.o.gz" -a $i != "NCR53C9x.o.gz" -a $i != "eata_dma.o.gz" -a $i != "libata.o.gz" ]; then
	DRIVER=`echo $i | sed 's/.o.gz//'`
	echo "Trying $DRIVER"; 
	if /bin/modprobe $DRIVER > /dev/null 2>&1; then
		echo $i > /scsidriver;
		/bin/cat /proc/scsi/scsi;
		exit 0;
	fi;
fi;
done
echo "Trying eata_dma";
if /bin/modprobe eata_dma > /dev/null 2>&1; then
	echo "eata_dma.o.gz" > /scsidriver;
	exit 0;
fi
cd $OLDDIR
