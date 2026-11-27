all: prepare-nso-version fxs
.PHONY: all

# Include standard NCS examples build definitions and rules
include $(NCS_DIR)/src/ncs/build/include.ncs.mk

NSO_VERSION ?= $(shell ncs --version)
NSO_67_OR_LATER = $(shell echo "$(NSO_VERSION)" | awk -F. '{ print (($$1 > 6) || ($$1 == 6 && $$2 >= 7)) ? 1 : 0 }')
NSO_67_PATCH = ../nso-6.7.patch
NSO_67_MARKER = tailf-ncs-commit-params

SRC = $(wildcard yang/*.yang)
DIRS = ../load-dir
FXS = $(SRC:yang/%.yang=../load-dir/%.fxs)

## Uncomment and patch the line below if you have a dependency to a NED
## or to other YANG files
# YANGPATH += ../../<ned-name>/src/ncsc-out/modules/yang \
# 	../../<pkt-name>/src/yang

NCSCPATH   = $(YANGPATH:%=--yangpath %)
YANGERPATH = $(YANGPATH:%=--path %)

prepare-nso-version:
	@if [ "$(NSO_67_OR_LATER)" = "1" ]; then \
		grep -q "$(NSO_67_MARKER)" yang/respl3vpn.yang || patch -d .. -p1 < $(NSO_67_PATCH); \
	else \
		! grep -q "$(NSO_67_MARKER)" yang/respl3vpn.yang || patch -d .. -p1 -R < $(NSO_67_PATCH); \
	fi
.PHONY: prepare-nso-version

fxs: $(DIRS) $(FXS)

$(DIRS):
	mkdir -p $@

../load-dir/%.fxs: yang/%.yang
	$(NCSC)  `ls $*-ann.yang  > /dev/null 2>&1 && echo "-a $*-ann.yang"` \
		--fail-on-warnings \
		$(NCSCPATH) \
		-c -o $@ $<

clean:
	rm -rf $(DIRS)
.PHONY: clean
