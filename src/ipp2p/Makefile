ifneq ($(KERNELRELEASE),)
obj-m := ipt_ipp2p.o

else

KERNEL_SRC ?= $(firstword $(wildcard /lib/modules/$(shell uname -r)/build /usr/src/linux))
ifeq ($(KERNEL_SRC),)
$(error You need to define KERNEL_SRC)
endif

ifneq ($wildcard $(KERNEL_SRC)/include/linux/modversions.h),)
MODVERSIONS = -DMODVERSIONS
endif

_KVER = $(strip $(shell cat $(KERNEL_SRC)/Makefile | grep -e '^VERSION' | cut -d"=" -f2))
_KPL = $(strip $(shell cat $(KERNEL_SRC)/Makefile | grep -e '^PATCHLEVEL' | cut -d"=" -f2))
_KSUB = $(strip $(shell cat $(KERNEL_SRC)/Makefile | grep -e '^SUBLEVEL' | cut -d"=" -f2))
KERNEL_SERIES=$(_KVER).$(_KPL)

ifeq ($(KERNEL_SERIES), 2.6)
	TARGET=ipt_ipp2p.ko
else
	TARGET=ipt_ipp2p.o
endif

SED = sed
IPTABLES_BIN = iptables

ifndef $(IPTABLES_SRC)
IPTVER = \
	$(shell $(IPTABLES_BIN) --version | $(SED) -e 's/^iptables v//')
IPTABLES_SRC = $(wildcard /usr/src/iptables-$(IPTVER))
endif

ifeq ($(IPTABLES_SRC),)
$(warning You need to install iptables sources and maybe set IPTABLES_SRC)
endif

IPTABLES_INCLUDE = -I$(IPTABLES_SRC)/include

ifneq ($(IPTVER),)
	IPTABLES_VERSION = $(IPTVER)
else
	IPTABLES_VERSION = $(shell cat $(IPTABLES_SRC)/Makefile | grep -e '^IPTABLES_VERSION:=' | cut -d"=" -f2)
endif

IPTABLES_OPTION = -DIPTABLES_VERSION=\"$(IPTABLES_VERSION)\"

CC = gcc
CFLAGS = -O2 -march=i586 -pipe -fomit-frame-pointer



all: modules libipt_ipp2p.so

modules: $(TARGET)

ipt_ipp2p.o: ipt_ipp2p.h ipt_ipp2p.c
	$(CC) $(CFLAGS) -I$(KERNEL_SRC)/include -c ipt_ipp2p.c -D__KERNEL__ -DMODULE $(MODVERSIONS)

ipt_ipp2p.ko: ipt_ipp2p.h ipt_ipp2p.c
	$(MAKE) -C $(KERNEL_SRC) SUBDIRS=$(PWD) modules


libipt_ipp2p.so: libipt_ipp2p.c ipt_ipp2p.h
	$(CC) $(CFLAGS) $(IPTABLES_OPTION) $(IPTABLES_INCLUDE) -fPIC -c libipt_ipp2p.c
	ld -shared -o libipt_ipp2p.so libipt_ipp2p.o

clean:
	-rm -f *.o *.so *.ko .*.cmd *.mod.c
endif
