CC := gcc
CFLAGS := -Wall
BUILD_DIR := build

SOURCES := $(wildcard p*.c)
PROGRAMS := $(patsubst %.c,%,$(SOURCES))
TARGETS := $(addprefix $(BUILD_DIR)/,$(PROGRAMS))

all: $(TARGETS)

$(BUILD_DIR):
	mkdir -p $@

$(BUILD_DIR)/%: %.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -o $@ $<

$(PROGRAMS): %: $(BUILD_DIR)/%

clean:
	rm -f $(TARGETS)

.PHONY: all clean $(PROGRAMS)
