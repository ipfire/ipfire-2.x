KSRC ?= /lib/modules/$(shell uname -r)/build

obj-m	+= r8101.o

all:
	$(MAKE) -C $(KSRC) SUBDIRS=$(PWD) modules

clean:
	rm -rf *.ko *.mod.* *.o .*.cmd .tmp_versions Module.symvers

distclean: clean
	rm -rf cscope.* *~
