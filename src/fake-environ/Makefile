
ifeq "$(CFLAGS)" ""
  $(error CFLAGS not defined)
endif

ifeq "$(TOOLS_DIR)" ""
  $(error TOOLS_DIR not defined)
endif

LIB = libpakfire_preload.so

SOURCES = $(wildcard *.c)
OBJECTS = $(patsubst %.c,%.o,$(SOURCES))

.PHONY: all
all: $(LIB)

%.o: %.c Makefile
	$(CC) $(CFLAGS) -o $@ -c $<

$(LIB): $(OBJECTS)
	$(CC) $(CFLAGS) -shared -o $@ $? -ldl -static-libgcc

.PHONY: install
install: all
	-mkdir -pv $(TOOLS_DIR)/lib/
	install -p -m 755 $(LIB) $(TOOLS_DIR)/lib

.PHONY: clean
clean:
	$(LIB)
