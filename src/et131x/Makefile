KSRC ?= /lib/modules/$(shell uname -r)/build

obj-m = et131x.o

et131x-objs :=	et1310_eeprom.o \
		et1310_jagcore.o \
		et1310_mac.o \
		et1310_phy.o \
		et1310_pm.o \
		et1310_rx.o \
		et1310_tx.o \
		et131x_config.o \
		et131x_debug.o \
		et131x_initpci.o \
		et131x_isr.o \
		et131x_netdev.o

all:
	$(MAKE) -C $(KSRC) SUBDIRS=$(PWD) modules

clean:
	rm -rf *.ko *.mod.* *.o .*.cmd .tmp_versions Module.symvers

distclean: clean
	rm -rf cscope.* *~
