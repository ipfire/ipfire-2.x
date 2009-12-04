KSRC ?= /lib/modules/$(shell uname -r)/build

obj-m		+= atl1c.o
atl1c-objs	+= atl1c_main.o atl1c_hw.o atl1c_ethtool.o

all:
	$(MAKE) -C $(KSRC) SUBDIRS=$(PWD) modules

clean:
	rm -rf *.ko *.mod.* *.o .*.cmd .tmp_versions Module.symvers

distclean: clean
	rm -rf cscope.* *~
